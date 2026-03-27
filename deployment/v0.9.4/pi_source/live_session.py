"""
live_session.py — d3kOS WebRTC live tunnel service (v0.9.4 S6)

Polls rtc-signal.php every 3 seconds for a pending WebRTC offer from the app.
When an offer is found:
  1. Creates a WebRTC answer via aiortc
  2. Posts answer + ICE candidates back to signal endpoint
  3. Waits for P2P data channel to open
  4. Sends live sensor readings (JSON) every 5 seconds
  5. Handles camera stream requests via data channel messages

Camera switching via data channel message:
  App sends: { "type": "camera_request", "slot": "<slot_id>" }
  Pi starts streaming that camera as the video track.
  App sends: { "type": "camera_stop" } to close camera.

Runs as d3kos-live.service (always on, waits for offers).
"""

import asyncio
import glob
import hashlib
import json
import logging
import os
import shutil
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

import requests

# ── aiortc imports ─────────────────────────────────────────────────────────────
try:
    from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceServer, RTCConfiguration
    from aiortc.contrib.media import MediaPlayer
    AIORTC_OK = True
except ImportError:
    AIORTC_OK = False
    logging.warning("aiortc not installed — live tunnel unavailable. Run: pip3 install aiortc")

# ── Config ────────────────────────────────────────────────────────────────────
LOG_FILE    = '/opt/d3kos/logs/live-session.log'
CONFIG_FILE  = '/opt/d3kos/config/cloud-config.json'
DEVICE_FILE  = '/opt/d3kos/config/device-token.json'
LICENSE_FILE = '/opt/d3kos/config/license.json'
SIGNAL_POLL = 3       # seconds between offer polls
DATA_PUSH   = 5       # seconds between sensor readings on data channel
STUN_SERVERS = [
    'stun:stun.l.google.com:19302',
    'stun:stun1.l.google.com:19302',
    'stun:stun.cloudflare.com:3478',
]

# ── Signal K sensor endpoints ─────────────────────────────────────────────────
SK_BASE = 'http://localhost:8099/signalk/v1/api/vessels/self'
SENSOR_PATHS = {
    'rpm':          f'{SK_BASE}/propulsion/port/revolutions',
    'coolant_temp': f'{SK_BASE}/propulsion/port/coolantTemperature',
    'oil_pressure': f'{SK_BASE}/propulsion/port/oilPressure',
    'fuel_level':   f'{SK_BASE}/tanks/fuel/0/currentLevel',
    'engine_hours': f'{SK_BASE}/propulsion/port/runTime',
    'battery_v':    f'{SK_BASE}/electrical/batteries/0/voltage',
    'sog':          f'{SK_BASE}/navigation/speedOverGround',
    'cog':          f'{SK_BASE}/navigation/courseOverGroundTrue',
    'lat':          f'{SK_BASE}/navigation/position',
    'heading':      f'{SK_BASE}/navigation/headingTrue',
}

# Camera stream base URL (served by camera_stream_manager.py on port 8084)
CAMERA_BASE      = 'http://localhost:8084'

# Media storage
RECORDING_PATH   = '/home/d3kos/camera-recordings'
MEDIA_README     = os.path.join(RECORDING_PATH, 'MEDIA_README.txt')
TRANSFER_CHUNK   = 16_384          # 16 KB per chunk over data channel
DISK_WARN_PCT    = 90              # warn when disk >= this percent used
DISK_CHECK_SECS  = 1800            # check every 30 minutes

# ── Logging ───────────────────────────────────────────────────────────────────
os.makedirs('/opt/d3kos/logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [live] %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ]
)
log = logging.getLogger('live_session')


def load_config():
    """Load API key, base URL, and device token from config files."""
    config = {}
    try:
        with open(CONFIG_FILE) as f:
            cfg = json.load(f)
        config['api_key']       = cfg.get('amboat_api_key', '')
        config['base_url']      = cfg.get('amboat_base_url', '').rstrip('/')
        config['turn_username'] = cfg.get('turn_username', '')
        config['turn_credential'] = cfg.get('turn_credential', '')
    except Exception as e:
        log.error(f"Cannot read cloud-config.json: {e}")
        return None
    try:
        with open(DEVICE_FILE) as f:
            dev = json.load(f)
        config['device_token'] = dev.get('device_token', '')
        # pi_id for rtc-signal.php must match d3kos_pairings.pi_id — which is device_token
        config['pi_id'] = config['device_token']
    except Exception as e:
        log.error(f"Cannot read device-token.json: {e}")
        return None
    return config


def pi_headers(config):
    return {
        'Authorization': f"Bearer {config['api_key']}",
        'X-Device-Token': config['device_token'],
        'Content-Type': 'application/json',
    }


def fetch_sensors():
    """Pull current sensor readings from Signal K. Returns dict."""
    readings = {
        'ts':           int(time.time()),
        'rpm':          None,
        'coolant_temp': None,
        'oil_pressure': None,
        'fuel_level':   None,
        'engine_hours': None,
        'battery_v':    None,
        'sog':          None,
        'cog':          None,
        'lat':          None,
        'lng':          None,
        'heading':      None,
    }
    try:
        r = requests.get(SENSOR_PATHS['rpm'], timeout=2)
        if r.status_code == 200:
            rps = r.json().get('value')
            if rps is not None:
                readings['rpm'] = int(round(float(rps) * 60))   # rps → rpm

        r = requests.get(SENSOR_PATHS['coolant_temp'], timeout=2)
        if r.status_code == 200:
            k = r.json().get('value')
            if k is not None:
                readings['coolant_temp'] = round(float(k) - 273.15, 1)   # K → °C

        r = requests.get(SENSOR_PATHS['oil_pressure'], timeout=2)
        if r.status_code == 200:
            pa = r.json().get('value')
            if pa is not None:
                readings['oil_pressure'] = round(float(pa) / 1000, 1)   # Pa → kPa

        r = requests.get(SENSOR_PATHS['fuel_level'], timeout=2)
        if r.status_code == 200:
            ratio = r.json().get('value')
            if ratio is not None:
                readings['fuel_level'] = round(float(ratio) * 100, 1)   # 0-1 → %

        r = requests.get(SENSOR_PATHS['engine_hours'], timeout=2)
        if r.status_code == 200:
            s = r.json().get('value')
            if s is not None:
                readings['engine_hours'] = round(float(s) / 3600, 2)    # s → h

        r = requests.get(SENSOR_PATHS['battery_v'], timeout=2)
        if r.status_code == 200:
            bv = r.json().get('value')
            if bv is not None:
                readings['battery_v'] = round(float(bv), 2)

        r = requests.get(SENSOR_PATHS['sog'], timeout=2)
        if r.status_code == 200:
            ms = r.json().get('value')
            if ms is not None:
                readings['sog'] = round(float(ms) * 1.94384, 1)   # m/s → knots

        r = requests.get(SENSOR_PATHS['cog'], timeout=2)
        if r.status_code == 200:
            rad = r.json().get('value')
            if rad is not None:
                import math
                readings['cog'] = round(math.degrees(float(rad)) % 360, 1)

        r = requests.get(SENSOR_PATHS['lat'], timeout=2)
        if r.status_code == 200:
            pos = r.json().get('value', {})
            if isinstance(pos, dict):
                readings['lat'] = pos.get('latitude')
                readings['lng'] = pos.get('longitude')

        r = requests.get(SENSOR_PATHS['heading'], timeout=2)
        if r.status_code == 200:
            rad = r.json().get('value')
            if rad is not None:
                import math
                readings['heading'] = round(math.degrees(float(rad)) % 360, 1)

    except Exception as e:
        log.debug(f"Sensor fetch error: {e}")

    return readings


def get_camera_url(slot_id: str) -> str | None:
    """Return the MJPEG stream URL for a given camera slot, or None."""
    try:
        r = requests.get(f'{CAMERA_BASE}/camera/slots', timeout=3)
        if r.status_code == 200:
            slots = r.json()
            for slot in slots:
                if str(slot.get('slot_id')) == str(slot_id):
                    hw_id = slot.get('hardware_id')
                    if hw_id:
                        return f'{CAMERA_BASE}/camera/stream/hw/{hw_id}'
    except Exception as e:
        log.debug(f"Camera slot lookup failed: {e}")
    return None


# ── Media helpers ─────────────────────────────────────────────────────────────

def check_disk_usage() -> dict:
    """Return {'percent_used': float, 'free_gb': float} for the root filesystem."""
    try:
        usage = shutil.disk_usage('/')
        pct   = round(usage.used / usage.total * 100, 1)
        free  = round(usage.free / 1_073_741_824, 2)
        return {'percent_used': pct, 'free_gb': free}
    except Exception:
        return {'percent_used': 0.0, 'free_gb': 0.0}


def list_media_files() -> list:
    """Return list of media files in RECORDING_PATH (and captures/ subdir)."""
    files = []
    if not os.path.exists(RECORDING_PATH):
        return files
    for fn in sorted(os.listdir(RECORDING_PATH), reverse=True):
        if fn in ('MEDIA_README.txt',):
            continue
        fp = os.path.join(RECORDING_PATH, fn)
        if os.path.isfile(fp) and (fn.endswith('.mp4') or fn.endswith('.jpg')):
            mtime = datetime.fromtimestamp(os.path.getmtime(fp)).strftime('%Y-%m-%d %H:%M')
            files.append({
                'filename':   fn,
                'media_type': 'video' if fn.endswith('.mp4') else 'photo',
                'size_bytes': os.path.getsize(fp),
                'modified_at': mtime,
            })
    # Fish detection captures in captures/ subdir
    cap_dir = os.path.join(RECORDING_PATH, 'captures')
    if os.path.isdir(cap_dir):
        for fn in sorted(os.listdir(cap_dir), reverse=True):
            fp = os.path.join(cap_dir, fn)
            if os.path.isfile(fp) and fn.endswith('.jpg'):
                mtime = datetime.fromtimestamp(os.path.getmtime(fp)).strftime('%Y-%m-%d %H:%M')
                files.append({
                    'filename':   f'captures/{fn}',
                    'media_type': 'fish_capture',
                    'size_bytes': os.path.getsize(fp),
                    'modified_at': mtime,
                })
    return files


async def send_file_chunks(channel, filepath: str, filename: str):
    """Send a file over the WebRTC data channel as binary chunks.
    Protocol: file_start JSON → binary chunks → file_end JSON.
    Caller sends transfer_complete ack; Pi then deletes the file.
    """
    try:
        size_bytes = os.path.getsize(filepath)
        with open(filepath, 'rb') as f:
            raw = f.read()
        md5 = hashlib.md5(raw).hexdigest()
        chunk_count = (len(raw) + TRANSFER_CHUNK - 1) // TRANSFER_CHUNK
        mime = 'video/mp4' if filename.endswith('.mp4') else 'image/jpeg'

        channel.send(json.dumps({
            'type':        'file_start',
            'filename':    filename,
            'media_type':  'video' if mime == 'video/mp4' else 'photo',
            'mime':        mime,
            'size_bytes':  size_bytes,
            'chunk_count': chunk_count,
        }))
        log.info(f"Sending {filename} ({size_bytes} bytes, {chunk_count} chunks)")

        for i in range(0, len(raw), TRANSFER_CHUNK):
            channel.send(raw[i:i + TRANSFER_CHUNK])
            await asyncio.sleep(0.01)   # yield to event loop; ~1.6 MB/s max

        channel.send(json.dumps({
            'type':     'file_end',
            'filename': filename,
            'checksum': f'md5:{md5}',
        }))
        log.info(f"Transfer of {filename} complete")

    except Exception as e:
        log.error(f"File transfer error for {filename}: {e}")
        channel.send(json.dumps({'type': 'transfer_error', 'filename': filename, 'reason': str(e)}))


def delete_media_file(filename: str) -> bool:
    """Delete a media file from RECORDING_PATH or captures/ subdir. Update readme."""
    try:
        if filename.startswith('captures/'):
            fp = os.path.join(RECORDING_PATH, filename)
        else:
            fp = os.path.join(RECORDING_PATH, filename)
        if os.path.isfile(fp):
            os.remove(fp)
            log.info(f"Deleted media file: {filename}")
            update_media_readme()
            return True
        log.warning(f"delete_media_file: not found: {filename}")
        return False
    except Exception as e:
        log.error(f"Error deleting {filename}: {e}")
        return False


def update_media_readme():
    """Regenerate MEDIA_README.txt with current file list and SCP instructions."""
    try:
        os.makedirs(RECORDING_PATH, exist_ok=True)
        files     = list_media_files()
        total_mb  = sum(f['size_bytes'] for f in files) / 1_048_576
        disk      = check_disk_usage()
        now       = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        lines = [
            f"d3kOS Media Storage — {RECORDING_PATH}",
            f"Last updated: {now}",
            f"Total files: {len(files)}  |  Total size: {total_mb:.1f} MB  |  Disk usage: {disk['percent_used']}%",
            "",
            "FILES STORED:",
        ]
        if files:
            for f in files:
                size_mb = f['size_bytes'] / 1_048_576
                lines.append(f"  {f['filename']:<50s} {size_mb:6.1f} MB   {f['modified_at']}")
        else:
            lines.append("  (none)")

        lines += [
            "",
            "TO REMOVE FILES VIA SCP — WINDOWS:",
            "  Install WinSCP from https://winscp.net (free, GUI)",
            "  Host: [Pi IP address]  Port: 22  Username: d3kos",
            f"  Navigate to: {RECORDING_PATH}",
            "  Select files and press Delete.",
            "  Or drag files to your Windows desktop first, then delete on Pi side.",
            "",
            "TO REMOVE FILES VIA SCP — MAC:",
            "  Open Terminal (Finder → Applications → Utilities → Terminal)",
            "  Copy a file to your Mac desktop:",
            "    scp d3kos@[Pi IP]:/home/d3kos/camera-recordings/filename.mp4 ~/Desktop/",
            "  Delete a file from the Pi:",
            "    ssh d3kos@[Pi IP] \"rm /home/d3kos/camera-recordings/filename.mp4\"",
            "  Delete all files at once:",
            "    ssh d3kos@[Pi IP] \"rm /home/d3kos/camera-recordings/*.mp4 /home/d3kos/camera-recordings/*.jpg\"",
            "",
            "TO REMOVE FILES VIA SCP — LINUX:",
            "  Open a terminal.",
            "  Copy a file to your home directory:",
            "    scp d3kos@[Pi IP]:/home/d3kos/camera-recordings/filename.mp4 ~/",
            "  Delete a file from the Pi:",
            "    ssh d3kos@[Pi IP] \"rm /home/d3kos/camera-recordings/filename.mp4\"",
            "  Delete all files at once:",
            "    ssh d3kos@[Pi IP] \"rm /home/d3kos/camera-recordings/*.mp4 /home/d3kos/camera-recordings/*.jpg\"",
            "",
            "NOTE: Replace [Pi IP address] with the IP shown in d3kOS Settings.",
            "      Default SSH credentials — Username: d3kos",
            "",
            "Files are automatically removed after successful transfer to the mobile app.",
            "If a file remains here it was not yet transferred or transfer failed.",
        ]

        with open(MEDIA_README, 'w') as fh:
            fh.write('\n'.join(lines) + '\n')

    except Exception as e:
        log.error(f"Failed to update MEDIA_README.txt: {e}")


# ── VideoStreamTrack for camera relay ────────────────────────────────────────
if AIORTC_OK:
    import av
    from aiortc import VideoStreamTrack

    class DummyVideoTrack(VideoStreamTrack):
        """
        Silent black-frame video track.
        Added to the RTCPeerConnection before the answer is created so the
        browser fires ontrack at connection time and shows the camera panel.
        Replaced with MJPEGCameraTrack via replaceTrack() when the user taps
        a camera slot.
        """
        kind = 'video'

        async def recv(self):
            pts, time_base = await self.next_timestamp()
            frame = av.VideoFrame(width=640, height=480, format='yuv420p')
            frame.pts       = pts
            frame.time_base = time_base
            return frame

    class MJPEGCameraTrack(VideoStreamTrack):
        """Reads frames from a local MJPEG stream and relays as WebRTC video."""

        kind = 'video'

        def __init__(self, stream_url: str):
            super().__init__()
            self._url    = stream_url
            self._player = None
            self._track  = None
            self._setup()

        def _setup(self):
            try:
                self._player = MediaPlayer(self._url, options={'rtsp_transport': 'tcp'})
                self._track  = self._player.video
            except Exception as e:
                log.error(f"Camera player setup failed: {e}")

        async def recv(self):
            if self._track:
                try:
                    return await self._track.recv()
                except Exception:
                    pass
            # Fallback: send a blank frame if camera unavailable
            import fractions
            frame = av.VideoFrame(width=640, height=480, format='yuv420p')
            pts, time_base = await self.next_timestamp()
            frame.pts       = pts
            frame.time_base = time_base
            return frame


# ── Main WebRTC session handler ───────────────────────────────────────────────
async def handle_offer(config: dict, offer_data: dict):
    """
    Given an offer from rtc-signal.php, create an answer, open a data channel,
    and start sending live sensor data every 5 seconds.
    """
    session_id = offer_data['session_id']
    signal_url = f"{config['base_url']}/wp-content/themes/twentytwenty-child/mobile/rtc-signal.php"
    log.info(f"Handling offer for session {session_id}")

    # ICE configuration — STUN for direct P2P, TURN relay for cellular/CGNAT
    ice_servers = [RTCIceServer(urls=s) for s in STUN_SERVERS]
    if config.get('turn_username') and config.get('turn_credential'):
        ice_servers.append(RTCIceServer(
            urls=[
                'turn:atmyboat.metered.live:80',
                'turn:atmyboat.metered.live:443',
                'turns:atmyboat.metered.live:443',
            ],
            username=config['turn_username'],
            credential=config['turn_credential'],
        ))
        log.info("TURN relay configured (Metered.ca)")
    else:
        log.warning("No TURN credentials in cloud-config.json — cellular connections may fail")
    pc = RTCPeerConnection(configuration=RTCConfiguration(iceServers=ice_servers))

    # Add a dummy video track BEFORE the answer is created.
    # This ensures the browser fires ontrack at connection time, making the
    # camera panel visible. The real camera is swapped in via replaceTrack()
    # when the user taps a slot — no renegotiation required.
    video_sender = pc.addTrack(DummyVideoTrack()) if AIORTC_OK else None

    # Track connection state for cleanup
    connected    = asyncio.Event()
    closed       = asyncio.Event()
    camera_track = None

    @pc.on('connectionstatechange')
    async def on_state_change():
        log.info(f"Connection state: {pc.connectionState}")
        if pc.connectionState == 'connected':
            connected.set()
        elif pc.connectionState in ('failed', 'closed', 'disconnected'):
            closed.set()

    @pc.on('datachannel')
    def on_datachannel(channel):
        log.info(f"Data channel opened: {channel.label}")

        # Track active recording filename so record_stop knows what to send
        session_state = {'recording_file': None}

        @channel.on('message')
        def on_message(msg):
            nonlocal camera_track
            try:
                data = json.loads(msg)
            except (json.JSONDecodeError, TypeError):
                return   # binary messages (acks) ignored here

            msg_type = data.get('type', '')

            # ── Camera streaming ──────────────────────────────────────────────
            if msg_type == 'camera_request':
                slot_id    = str(data.get('slot', ''))
                stream_url = get_camera_url(slot_id)
                if stream_url and AIORTC_OK and video_sender:
                    # Stop previous camera track if one is active
                    if camera_track:
                        camera_track.stop()
                    camera_track = MJPEGCameraTrack(stream_url)
                    # replaceTrack swaps the track on the already-negotiated sender —
                    # no renegotiation needed. Browser ontrack already fired at connect.
                    asyncio.ensure_future(video_sender.replaceTrack(camera_track))
                    log.info(f"Camera track replaced for slot {slot_id}: {stream_url}")
                    channel.send(json.dumps({'type': 'camera_ok', 'slot': slot_id}))
                else:
                    channel.send(json.dumps({'type': 'camera_error', 'reason': 'slot not found'}))

            elif msg_type == 'camera_stop':
                if camera_track:
                    camera_track.stop()
                    camera_track = None
                # Replace back with silent dummy so the video sender stays valid
                if AIORTC_OK and video_sender:
                    asyncio.ensure_future(video_sender.replaceTrack(DummyVideoTrack()))
                channel.send(json.dumps({'type': 'camera_stopped'}))

            elif msg_type == 'camera_slots_request':
                try:
                    r = requests.get(f'{CAMERA_BASE}/camera/slots', timeout=3)
                    slots = r.json() if r.status_code == 200 else []
                except Exception:
                    slots = []
                channel.send(json.dumps({'type': 'camera_slots', 'slots': slots}))

            # ── Photo capture ─────────────────────────────────────────────────
            elif msg_type == 'capture_request':
                asyncio.ensure_future(_do_capture(channel))

            # ── Video recording ───────────────────────────────────────────────
            elif msg_type == 'record_start':
                try:
                    r = requests.post(f'{CAMERA_BASE}/camera/record/start', timeout=5)
                    if r.status_code == 200:
                        info = r.json()
                        session_state['recording_file'] = info.get('filename', '')
                        channel.send(json.dumps({
                            'type': 'record_started',
                            'filename': session_state['recording_file'],
                        }))
                    else:
                        channel.send(json.dumps({'type': 'record_error', 'reason': f'HTTP {r.status_code}'}))
                except Exception as e:
                    channel.send(json.dumps({'type': 'record_error', 'reason': str(e)}))

            elif msg_type == 'record_stop':
                asyncio.ensure_future(_do_record_stop(channel, session_state))

            # ── File transfer ─────────────────────────────────────────────────
            elif msg_type == 'transfer_request':
                filename = data.get('filename', '')
                if filename:
                    asyncio.ensure_future(_do_transfer(channel, filename))

            elif msg_type == 'transfer_complete':
                filename = data.get('filename', '')
                if filename:
                    ok = delete_media_file(filename)
                    log.info(f"Post-transfer delete {'OK' if ok else 'FAILED'}: {filename}")

            elif msg_type == 'delete_request':
                filename = data.get('filename', '')
                if filename:
                    ok = delete_media_file(filename)
                    channel.send(json.dumps({'type': 'delete_ack', 'filename': filename, 'ok': ok}))

            # ── Media library ─────────────────────────────────────────────────
            elif msg_type == 'media_list_request':
                files = list_media_files()
                disk  = check_disk_usage()
                channel.send(json.dumps({
                    'type':         'media_list',
                    'files':        files,
                    'disk_percent': disk['percent_used'],
                    'free_gb':      disk['free_gb'],
                }))

            elif msg_type == 'ping':
                channel.send(json.dumps({'type': 'pong', 'ts': int(time.time())}))

        # ── Async helpers spawned from on_message ─────────────────────────────

        async def _do_capture(channel):
            try:
                r = requests.post(f'{CAMERA_BASE}/camera/capture', timeout=10)
                if r.status_code == 200:
                    info     = r.json()
                    filepath = info['path']
                    filename = info['filename']
                    size_b   = int(info.get('size_mb', 0) * 1_048_576)
                    channel.send(json.dumps({
                        'type': 'capture_done', 'filename': filename, 'size_bytes': size_b
                    }))
                    update_media_readme()
                    await send_file_chunks(channel, filepath, filename)
                else:
                    channel.send(json.dumps({'type': 'capture_error', 'reason': f'HTTP {r.status_code}'}))
            except Exception as e:
                channel.send(json.dumps({'type': 'capture_error', 'reason': str(e)}))

        async def _do_record_stop(channel, session_state):
            try:
                r = requests.post(f'{CAMERA_BASE}/camera/record/stop', timeout=5)
                if r.status_code == 200:
                    filename = session_state.get('recording_file', '')
                    if not filename:
                        # Fallback: find most recent mp4
                        mp4s = sorted(
                            glob.glob(os.path.join(RECORDING_PATH, '*.mp4')),
                            key=os.path.getmtime, reverse=True,
                        )
                        filename = os.path.basename(mp4s[0]) if mp4s else ''
                    if filename:
                        filepath   = os.path.join(RECORDING_PATH, filename)
                        size_bytes = os.path.getsize(filepath) if os.path.isfile(filepath) else 0
                        channel.send(json.dumps({
                            'type': 'record_stopped', 'filename': filename, 'size_bytes': size_bytes
                        }))
                        update_media_readme()
                        await send_file_chunks(channel, filepath, filename)
                    else:
                        channel.send(json.dumps({'type': 'record_error', 'reason': 'Recording file not found'}))
                    session_state['recording_file'] = None
                else:
                    channel.send(json.dumps({'type': 'record_error', 'reason': f'HTTP {r.status_code}'}))
            except Exception as e:
                channel.send(json.dumps({'type': 'record_error', 'reason': str(e)}))

        async def _do_transfer(channel, filename):
            if filename.startswith('captures/'):
                filepath = os.path.join(RECORDING_PATH, filename)
            else:
                filepath = os.path.join(RECORDING_PATH, filename)
            if os.path.isfile(filepath):
                await send_file_chunks(channel, filepath, filename)
            else:
                channel.send(json.dumps({'type': 'transfer_error', 'filename': filename, 'reason': 'File not found'}))

        # ── Sensor push loop ──────────────────────────────────────────────────

        # Start pushing sensor data every 5 seconds
        async def push_sensors():
            storage_warned   = False
            last_disk_check  = 0.0
            while not closed.is_set():
                try:
                    sensors = fetch_sensors()
                    sensors['type'] = 'sensors'
                    channel.send(json.dumps(sensors))
                except Exception as e:
                    log.debug(f"Sensor push error: {e}")

                # Periodic disk usage check (every DISK_CHECK_SECS)
                now = time.time()
                if now - last_disk_check >= DISK_CHECK_SECS:
                    last_disk_check = now
                    disk = check_disk_usage()
                    if disk['percent_used'] >= DISK_WARN_PCT:
                        if not storage_warned:
                            log.warning(f"Disk usage at {disk['percent_used']}% — sending storage warning")
                            storage_warned = True
                        try:
                            channel.send(json.dumps({
                                'type':         'storage_warning',
                                'percent_used': disk['percent_used'],
                                'free_gb':      disk['free_gb'],
                            }))
                        except Exception:
                            pass
                    else:
                        storage_warned = False   # reset once below threshold

                await asyncio.sleep(DATA_PUSH)

        asyncio.ensure_future(push_sensors())

    # Set remote description from app's offer
    offer_sdp_str = offer_data.get('sdp', '')
    sdp_head = offer_sdp_str[:500].replace('\r\n', '|').replace('\n', '|')
    log.info(f"Offer SDP first 500 chars: {sdp_head}")
    remote_sdp  = RTCSessionDescription(sdp=offer_sdp_str, type='offer')
    try:
        await pc.setRemoteDescription(remote_sdp)
    except Exception as e:
        log.error(f"setRemoteDescription failed: {e}")
        return

    # Add app's ICE candidates.
    # Browser sends JSON: {"candidate": "candidate:xxx ...", "sdpMid": "0", ...}
    # candidate_from_sdp() expects the SDP string WITHOUT the "candidate:" prefix.
    app_cands = offer_data.get('ice_candidates', [])
    log.info(f"App sent {len(app_cands)} ICE candidates")
    for cand_obj in app_cands:
        try:
            from aiortc.sdp import candidate_from_sdp
            if isinstance(cand_obj, dict):
                raw = cand_obj.get('candidate', '')
            else:
                raw = str(cand_obj)
            sdp_str = raw.replace('candidate:', '', 1).strip()
            if sdp_str:
                await pc.addIceCandidate(candidate_from_sdp(sdp_str))
        except Exception as e:
            log.debug(f"ICE candidate add error: {e} — raw: {raw!r}")

    # Create answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    # Wait for ICE gathering to complete (up to 8 seconds)
    deadline = asyncio.get_event_loop().time() + 8
    while pc.iceGatheringState != 'complete':
        if asyncio.get_event_loop().time() > deadline:
            log.warning(f"ICE gathering not complete after 8s (state: {pc.iceGatheringState})")
            break
        await asyncio.sleep(0.1)

    # Log Pi's ICE candidates for diagnostics
    sdp_lines = pc.localDescription.sdp.split('\r\n')
    cand_lines = [l for l in sdp_lines if l.startswith('a=candidate')]
    log.info(f"Pi ICE candidates ({len(cand_lines)}): {cand_lines[:4]}")

    our_candidates = []  # candidates are embedded in the SDP — not sent separately

    payload = {
        'session_id':     session_id,
        'sdp':            pc.localDescription.sdp,
        'ice_candidates': our_candidates,
    }
    try:
        r = requests.post(
            f'{signal_url}?action=answer',
            json=payload,
            headers=pi_headers(config),
            timeout=8,
        )
        log.info(f"Answer posted: HTTP {r.status_code}")
    except Exception as e:
        log.error(f"Failed to post answer: {e}")
        await pc.close()
        return

    # Wait for connection or timeout (2 minutes)
    try:
        await asyncio.wait_for(connected.wait(), timeout=120)
        log.info(f"Session {session_id}: P2P connected")
    except asyncio.TimeoutError:
        log.warning(f"Session {session_id}: connection timed out")
        await pc.close()
        return

    # Keep alive until disconnected or 4 hours max
    try:
        await asyncio.wait_for(closed.wait(), timeout=14400)
    except asyncio.TimeoutError:
        log.info(f"Session {session_id}: max session duration reached")

    if camera_track:
        camera_track.stop()
    await pc.close()
    log.info(f"Session {session_id}: closed")


# ── Poll loop ─────────────────────────────────────────────────────────────────
async def poll_loop(config: dict):
    """Continuously poll for new WebRTC offers from the app."""
    signal_url  = f"{config['base_url']}/wp-content/themes/twentytwenty-child/mobile/rtc-signal.php"
    pi_id       = config['pi_id']
    active_sessions: set = set()
    headers     = pi_headers(config)

    log.info(f"Live session service started. Pi ID: {pi_id}")
    log.info(f"Signal endpoint: {signal_url}")

    while True:
        try:
            r = requests.get(
                f'{signal_url}?action=poll_offer&pi_id={pi_id}',
                headers=headers,
                timeout=6,
            )
            if r.status_code == 200:
                data = r.json()
                if data.get('success') and data.get('data', {}).get('ready'):
                    offer_data = data['data']
                    sid        = offer_data.get('session_id')
                    if sid and sid not in active_sessions:
                        active_sessions.add(sid)
                        log.info(f"New offer received: session {sid}")
                        # Handle in background so we keep polling
                        asyncio.ensure_future(
                            handle_offer_safe(config, offer_data, active_sessions, sid)
                        )
        except requests.exceptions.RequestException as e:
            log.debug(f"Poll error: {e}")
        except Exception as e:
            log.error(f"Unexpected poll error: {e}")
            log.debug(traceback.format_exc())

        await asyncio.sleep(SIGNAL_POLL)


async def handle_offer_safe(config, offer_data, active_sessions, sid):
    """Wrapper to ensure active_sessions is cleaned up after session ends."""
    try:
        await handle_offer(config, offer_data)
    except Exception as e:
        log.error(f"Session {sid} error: {e}")
        log.debug(traceback.format_exc())
    finally:
        active_sessions.discard(sid)


# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    if not AIORTC_OK:
        log.error("aiortc is required for the live tunnel. Install it with: pip3 install aiortc")
        log.error("Sensor data will be pushed via the existing 30-minute sync until aiortc is installed.")
        # Don't exit — the service stays up so systemd doesn't restart-loop.
        # When aiortc is installed, restart this service.
        while True:
            time.sleep(60)

    config = load_config()
    if not config:
        log.error("Cannot load config — exiting.")
        sys.exit(1)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(poll_loop(config))
    except KeyboardInterrupt:
        log.info("Stopped by operator.")
    finally:
        loop.close()


if __name__ == '__main__':
    main()
