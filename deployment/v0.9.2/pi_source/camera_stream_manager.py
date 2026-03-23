#!/usr/bin/env python3
"""
d3kOS Camera Stream Manager — Slot/Hardware Architecture
Port: 8084

Config: /opt/d3kos/config/slots.json
        /opt/d3kos/config/hardware.json
Recording: /home/d3kos/camera-recordings/

Core model:
  SLOT     = named position on the boat (lives forever, not tied to hardware)
  HARDWARE = physical camera discovered on the network (comes and goes)
  ASSIGNMENT = owner-controlled link between slot and hardware

Frame buffer: one background RTSP decoder per hardware entry.
Any number of /camera/frame/<slot_id> requests read from the buffer —
zero additional RTSP decode load per browser client.

New endpoints:
  GET    /camera/slots                  — all slots + resolved hardware status
  GET    /camera/hardware               — all discovered hardware
  POST   /camera/slots                  — create a new slot
  PATCH  /camera/slots/<slot_id>        — update label, display_order, or roles
  POST   /camera/slots/<slot_id>/assign — assign hardware_id to slot
  POST   /camera/slots/<slot_id>/unassign — remove hardware assignment
  DELETE /camera/slots/<slot_id>        — delete slot (hardware returned to pool)
  POST   /camera/scan                   — trigger network discovery scan
  GET    /camera/frame/<slot_id>        — single frame by slot

Backwards-compatible endpoints (unchanged callers):
  GET  /camera/status       — active camera status (returns forward_watch slot)
  GET  /camera/frame        — current frame (returns forward_watch slot frame)
  GET  /camera/list         — all cameras + status (returns slots as cameras)
  POST /camera/switch/<id>  — switch active camera (sets active_default role)
  POST /camera/record/start — start recording forward_watch slot
  POST /camera/record/stop  — stop recording
  GET  /camera/recordings   — list recordings
  POST /camera/capture      — capture photo from forward_watch slot

Removed: /camera/grid (server-side stitch — browser handles grid layout now)
"""

import re
import socket
import time
import os
import json
from datetime import datetime, timezone
from threading import Thread, Lock
from typing import Optional
import io

import cv2
import numpy as np
import vlc
from flask import Flask, jsonify, send_file, request

app = Flask(__name__)

@app.after_request
def _cors(r):
    r.headers["Access-Control-Allow-Origin"] = "*"
    return r

# ── Config paths ───────────────────────────────────────────────────────────────

SLOTS_CONFIG    = '/opt/d3kos/config/slots.json'
HARDWARE_CONFIG = '/opt/d3kos/config/hardware.json'
RECORDING_PATH  = '/home/d3kos/camera-recordings'

# Discovery scan
SCAN_SUBNET  = '10.42.0'
SCAN_START   = 50
SCAN_END     = 200
SCAN_PORT    = 554
SCAN_TIMEOUT = 0.3  # seconds per IP

# ── Global state ───────────────────────────────────────────────────────────────

slots    = {}   # slot_id    → slot dict
hardware = {}   # hardware_id → hw dict
hw_state = {}   # hardware_id → {'cap', 'frame', 'lock', 'connected', 'thread'}

config_lock = Lock()  # serialises writes to slots.json / hardware.json

# Recording state (always applies to forward_watch slot)
recording_instance = None
recording_player   = None
recording_active   = False


# ── Data layer ─────────────────────────────────────────────────────────────────

def load_config() -> None:
    global slots, hardware
    if os.path.exists(SLOTS_CONFIG):
        with open(SLOTS_CONFIG) as f:
            slots = {s['slot_id']: s for s in json.load(f)}
        print(f'✓ Loaded {len(slots)} slot(s): {list(slots.keys())}')
    else:
        slots = {}
        print('⚠ slots.json not found — no slots configured')

    if os.path.exists(HARDWARE_CONFIG):
        with open(HARDWARE_CONFIG) as f:
            hardware = {h['hardware_id']: h for h in json.load(f)}
        print(f'✓ Loaded {len(hardware)} hardware entry(s)')
    else:
        hardware = {}
        print('⚠ hardware.json not found — no hardware configured')


def save_slots() -> None:
    with config_lock:
        with open(SLOTS_CONFIG, 'w') as f:
            json.dump(list(slots.values()), f, indent=2)


def save_hardware() -> None:
    with config_lock:
        with open(HARDWARE_CONFIG, 'w') as f:
            json.dump(list(hardware.values()), f, indent=2)


# ── Role helpers ───────────────────────────────────────────────────────────────

def get_forward_watch_slot_id() -> Optional[str]:
    for sid, slot in slots.items():
        if slot.get('roles', {}).get('forward_watch'):
            return sid
    return None


def get_active_default_slot_id() -> Optional[str]:
    for sid, slot in slots.items():
        if slot.get('roles', {}).get('active_default'):
            return sid
    return get_forward_watch_slot_id()


def get_hw_for_slot(slot_id: str) -> Optional[dict]:
    slot = slots.get(slot_id)
    if not slot or not slot.get('assigned'):
        return None
    return hardware.get(slot.get('hardware_id', ''))


def _clear_exclusive_role(role: str, except_slot_id: str) -> None:
    """Clear an exclusive role (forward_watch / active_default) from all
    slots except the one being set, so only one slot holds the role."""
    for sid, slot in slots.items():
        if sid != except_slot_id and slot.get('roles', {}).get(role):
            slot['roles'][role] = False


# ── Frame buffer ───────────────────────────────────────────────────────────────

def _open_cap(rtsp_url: str) -> Optional[cv2.VideoCapture]:
    cap = cv2.VideoCapture(rtsp_url)
    if cap.isOpened():
        return cap
    cap.release()
    return None


def _frame_grabber_thread(hardware_id: str) -> None:
    """Decode RTSP for one hardware entry continuously, write JPEG to hw_state.
    One thread per hardware entry — never per browser client.
    """
    state = hw_state[hardware_id]
    reconnect_delay = 10
    last_attempt = 0.0

    while True:
        cap = state['cap']
        if cap and cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                _, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                with state['lock']:
                    state['frame']     = jpeg.tobytes()
                    state['connected'] = True
            else:
                state['connected'] = False
                now = time.time()
                if now - last_attempt > reconnect_delay:
                    last_attempt = now
                    try:
                        cap.release()
                    except Exception:
                        pass
                    hw = hardware.get(hardware_id, {})
                    state['cap'] = _open_cap(hw.get('rtsp_url', ''))
            time.sleep(0.033)   # ~30 fps decode loop
        else:
            state['connected'] = False
            now = time.time()
            if now - last_attempt > reconnect_delay:
                last_attempt = now
                hw = hardware.get(hardware_id, {})
                state['cap'] = _open_cap(hw.get('rtsp_url', ''))
            time.sleep(2)


def start_grabber(hardware_id: str) -> None:
    """Create hw_state entry and launch frame grabber thread for one hardware."""
    hw = hardware.get(hardware_id)
    if not hw or not hw.get('rtsp_url'):
        return
    if hardware_id in hw_state:
        return  # already running

    state = {
        'cap':       _open_cap(hw['rtsp_url']),
        'frame':     None,
        'lock':      Lock(),
        'connected': False,
        'thread':    None,
    }
    hw_state[hardware_id] = state
    t = Thread(target=_frame_grabber_thread, args=(hardware_id,), daemon=True)
    t.start()
    state['thread'] = t
    print(f'✓ Frame grabber: {hardware_id} ({hw.get("ip", "?")})')


def start_all_grabbers() -> None:
    for hw_id in hardware:
        start_grabber(hw_id)


# ── Frame helpers ──────────────────────────────────────────────────────────────

def _offline_placeholder(label: str = 'Offline') -> bytes:
    img = np.zeros((240, 426, 3), dtype=np.uint8)
    cv2.putText(img, label, (20, 130),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 200, 0), 2, cv2.LINE_AA)
    _, buf = cv2.imencode('.jpg', img)
    return buf.tobytes()


def _get_frame_for_slot(slot_id: str) -> Optional[bytes]:
    """Resolve slot → hardware → frame buffer. Returns JPEG bytes or None."""
    slot = slots.get(slot_id)
    if not slot or not slot.get('assigned') or not slot.get('hardware_id'):
        return None
    state = hw_state.get(slot['hardware_id'])
    if not state:
        return None
    with state['lock']:
        return state['frame']


def _frame_or_placeholder(slot_id: str) -> bytes:
    data = _get_frame_for_slot(slot_id)
    if data:
        return data
    slot = slots.get(slot_id, {})
    return _offline_placeholder(slot.get('label', slot_id) + ' Offline')


def _mask_rtsp(url: str) -> str:
    """Replace RTSP credentials with **** for safe display."""
    return re.sub(r'(rtsp://)([^@]+)(@)', r'\1****\3', url)


# ── Discovery scan ─────────────────────────────────────────────────────────────

def _probe_tcp(ip: str) -> bool:
    try:
        with socket.create_connection((ip, SCAN_PORT), timeout=SCAN_TIMEOUT):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def _mac_from_arp(ip: str) -> Optional[str]:
    try:
        with open('/proc/net/arp') as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 4 and parts[0] == ip:
                    mac = parts[3]
                    if mac != '00:00:00:00:00:00':
                        return mac.upper()
    except Exception:
        pass
    return None


def _mac_to_hw_id(mac: str) -> str:
    return 'hw_' + mac.replace(':', '_').lower()


def run_discovery_scan() -> None:
    """Probe SCAN_SUBNET.SCAN_START–SCAN_END for cameras on TCP 554.
    Threaded — all IPs probed concurrently, completes in ~300ms.
    Adds new hardware as unassigned. Updates IP/status for existing entries.
    """
    print(f'  Scan: probing {SCAN_SUBNET}.{SCAN_START}–{SCAN_END} (TCP {SCAN_PORT})...')
    ips = [f'{SCAN_SUBNET}.{i}' for i in range(SCAN_START, SCAN_END + 1)]
    responding = {}
    lock = Lock()

    def probe(ip: str) -> None:
        if _probe_tcp(ip):
            with lock:
                responding[ip] = True

    threads = [Thread(target=probe, args=(ip,), daemon=True) for ip in ips]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=2)

    found = list(responding.keys())
    print(f'  Scan: {len(found)} IP(s) on port 554: {found}')

    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')
    changed = False

    for ip in found:
        mac = _mac_from_arp(ip)
        if not mac:
            print(f'  Scan: {ip} — port open but MAC not in ARP (no traffic yet?)')
            continue
        hw_id = _mac_to_hw_id(mac)

        if hw_id not in hardware:
            hardware[hw_id] = {
                'hardware_id':      hw_id,
                'mac':              mac,
                'ip':               ip,
                'model':            'Unknown',
                'rtsp_url':         f'rtsp://admin:d3kos2026%24@{ip}:554/h264Preview_01_sub',
                'last_seen':        now,
                'status':           'online',
                'assigned_to_slot': None,
            }
            print(f'  Scan: new camera — {hw_id} at {ip}')
            start_grabber(hw_id)
            changed = True
        else:
            hw = hardware[hw_id]
            if hw.get('ip') != ip:
                print(f'  Scan: {hw_id} IP updated {hw["ip"]} → {ip}')
                hw['ip'] = ip
                hw['rtsp_url'] = re.sub(r'(?<=@)[^:]+(?=:)', ip, hw.get('rtsp_url', ''))
                changed = True
            if hw.get('status') != 'online':
                hw['status'] = 'online'
                changed = True
            hw['last_seen'] = now

    if changed:
        save_hardware()

    print('  Scan complete.')


# ── Slot response builder ──────────────────────────────────────────────────────

def _slot_status(slot: dict) -> str:
    if not slot.get('assigned') or not slot.get('hardware_id'):
        return 'unassigned'
    state = hw_state.get(slot['hardware_id'], {})
    if state.get('connected'):
        return 'online'
    hw = hardware.get(slot['hardware_id'], {})
    return 'offline' if hw.get('status') == 'offline' else 'connecting'


def _slot_response(slot: dict) -> dict:
    hw    = hardware.get(slot.get('hardware_id', ''))
    state = hw_state.get(slot.get('hardware_id', ''), {})
    return {
        'slot_id':       slot['slot_id'],
        'label':         slot['label'],
        'display_order': slot.get('display_order', 0),
        'roles':         slot.get('roles', {}),
        'assigned':      slot.get('assigned', False),
        'hardware_id':   slot.get('hardware_id'),
        'status':        _slot_status(slot),
        'has_frame':     state.get('frame') is not None,
        'hardware': {
            'hardware_id': hw['hardware_id'],
            'ip':          hw.get('ip'),
            'model':       hw.get('model'),
            'mac':         hw.get('mac'),
            'last_seen':   hw.get('last_seen'),
            'status':      hw.get('status'),
        } if hw else None,
    }


# ── New slot / hardware API ────────────────────────────────────────────────────

@app.route('/camera/slots', methods=['GET'])
def get_slots():
    ordered = sorted(slots.values(), key=lambda s: s.get('display_order', 99))
    return jsonify([_slot_response(s) for s in ordered])


@app.route('/camera/hardware', methods=['GET'])
def get_hardware():
    result = []
    for hw_id, hw in hardware.items():
        state = hw_state.get(hw_id, {})
        result.append({
            'hardware_id':      hw['hardware_id'],
            'mac':              hw.get('mac'),
            'ip':               hw.get('ip'),
            'model':            hw.get('model'),
            'last_seen':        hw.get('last_seen'),
            'status':           hw.get('status'),
            'assigned_to_slot': hw.get('assigned_to_slot'),
            'connected':        state.get('connected', False),
            'has_frame':        state.get('frame') is not None,
        })
    return jsonify(result)


@app.route('/camera/slots', methods=['POST'])
def create_slot():
    data  = request.get_json() or {}
    label = (data.get('label') or '').strip()
    if not label:
        return jsonify({'error': 'label is required'}), 400

    slot_id = re.sub(r'[^a-z0-9]+', '_', label.lower()).strip('_')
    if not slot_id:
        return jsonify({'error': 'label produces empty slug'}), 400
    if slot_id in slots:
        return jsonify({'error': f'slot_id already exists: {slot_id}'}), 409

    roles = data.get('roles', {})
    if roles.get('forward_watch'):
        _clear_exclusive_role('forward_watch', slot_id)
    if roles.get('active_default'):
        _clear_exclusive_role('active_default', slot_id)

    max_order = max((s.get('display_order', 0) for s in slots.values()), default=0)
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')

    slot = {
        'slot_id':       slot_id,
        'label':         label,
        'display_order': max_order + 1,
        'roles': {
            'forward_watch':  bool(roles.get('forward_watch', False)),
            'fish_detection': bool(roles.get('fish_detection', False)),
            'active_default': bool(roles.get('active_default', False)),
            'display_in_grid': bool(roles.get('display_in_grid', True)),
        },
        'hardware_id': None,
        'assigned':    False,
        'created':     now,
    }
    slots[slot_id] = slot
    save_slots()
    return jsonify(_slot_response(slot)), 201


@app.route('/camera/slots/<slot_id>', methods=['PATCH'])
def update_slot(slot_id):
    slot = slots.get(slot_id)
    if not slot:
        return jsonify({'error': f'Unknown slot: {slot_id}'}), 404

    data = request.get_json() or {}

    if 'label' in data:
        slot['label'] = data['label'].strip()

    if 'display_order' in data:
        slot['display_order'] = int(data['display_order'])

    if 'roles' in data:
        for role, val in data['roles'].items():
            if role in ('forward_watch', 'active_default') and val:
                _clear_exclusive_role(role, slot_id)
            slot['roles'][role] = bool(val)

    save_slots()
    return jsonify(_slot_response(slot))


@app.route('/camera/slots/<slot_id>/assign', methods=['POST'])
def assign_hardware_to_slot(slot_id):
    slot = slots.get(slot_id)
    if not slot:
        return jsonify({'error': f'Unknown slot: {slot_id}'}), 404

    data  = request.get_json() or {}
    hw_id = data.get('hardware_id')
    if not hw_id:
        return jsonify({'error': 'hardware_id is required'}), 400
    if hw_id not in hardware:
        return jsonify({'error': f'Unknown hardware: {hw_id}'}), 404

    # Remove hardware from its previous slot
    prev = hardware[hw_id].get('assigned_to_slot')
    if prev and prev != slot_id and prev in slots:
        slots[prev]['assigned'] = False
        slots[prev]['hardware_id'] = None

    # Unlink old hardware from this slot
    old_hw = slot.get('hardware_id')
    if old_hw and old_hw != hw_id and old_hw in hardware:
        hardware[old_hw]['assigned_to_slot'] = None

    slot['hardware_id'] = hw_id
    slot['assigned']    = True
    hardware[hw_id]['assigned_to_slot'] = slot_id

    if hw_id not in hw_state:
        start_grabber(hw_id)

    save_slots()
    save_hardware()
    return jsonify(_slot_response(slot))


@app.route('/camera/slots/<slot_id>/unassign', methods=['POST'])
def unassign_hardware_from_slot(slot_id):
    slot = slots.get(slot_id)
    if not slot:
        return jsonify({'error': f'Unknown slot: {slot_id}'}), 404

    hw_id = slot.get('hardware_id')
    if hw_id and hw_id in hardware:
        hardware[hw_id]['assigned_to_slot'] = None
        save_hardware()

    slot['hardware_id'] = None
    slot['assigned']    = False
    save_slots()
    return jsonify(_slot_response(slot))


@app.route('/camera/slots/<slot_id>', methods=['DELETE'])
def delete_slot(slot_id):
    slot = slots.get(slot_id)
    if not slot:
        return jsonify({'error': f'Unknown slot: {slot_id}'}), 404

    hw_id = slot.get('hardware_id')
    if hw_id and hw_id in hardware:
        hardware[hw_id]['assigned_to_slot'] = None
        save_hardware()

    del slots[slot_id]
    save_slots()
    return jsonify({'ok': True, 'deleted': slot_id})


@app.route('/camera/scan', methods=['POST'])
def trigger_scan():
    Thread(target=run_discovery_scan, daemon=True).start()
    return jsonify({'ok': True, 'message': 'Scan started — check /camera/hardware for results'})


@app.route('/camera/frame/<slot_id>', methods=['GET'])
def get_frame_by_slot(slot_id):
    """Return JPEG by slot_id (resolves slot → hardware → frame buffer)."""
    if slot_id not in slots:
        return jsonify({'error': f'Unknown slot: {slot_id}'}), 404
    data = _frame_or_placeholder(slot_id)
    return send_file(io.BytesIO(data), mimetype='image/jpeg')


@app.route('/camera/frame/hw/<hardware_id>', methods=['GET'])
def get_frame_by_hardware(hardware_id: str):
    """Return JPEG by hardware_id — used by setup wizard before slot assignment."""
    state = hw_state.get(hardware_id)
    if state:
        with state['lock']:
            frame = state['frame']
        if frame:
            return send_file(io.BytesIO(frame), mimetype='image/jpeg')
    hw = hardware.get(hardware_id, {})
    label = hw.get('model', hardware_id)
    return send_file(io.BytesIO(_offline_placeholder(label)), mimetype='image/jpeg')


# ── Backwards-compatible endpoints ────────────────────────────────────────────

@app.route('/camera/status', methods=['GET'])
def camera_status():
    fw_id  = get_forward_watch_slot_id()
    slot   = slots.get(fw_id, {}) if fw_id else {}
    hw     = get_hw_for_slot(fw_id) if fw_id else None
    state  = hw_state.get((hw or {}).get('hardware_id', ''), {})
    rtsp   = (hw or {}).get('rtsp_url', '')
    return jsonify({
        'connected':     state.get('connected', False),
        'has_frame':     state.get('frame') is not None,
        'camera_id':     fw_id,
        'camera_ip':     (hw or {}).get('ip', 'Not configured'),
        'camera_name':   slot.get('label', fw_id or 'None'),
        'rtsp_url':      _mask_rtsp(rtsp) if rtsp else 'Not configured',
        'recording':     recording_active,
        'service':       'd3kos-camera-stream',
        'port':          8084,
        'offline_reason': '' if state.get('connected') else 'Camera not reachable on boat network',
    })


@app.route('/camera/frame', methods=['GET'])
def get_frame():
    """Return JPEG from forward_watch slot (backwards compat)."""
    fw_id = get_forward_watch_slot_id()
    data  = _frame_or_placeholder(fw_id) if fw_id else _offline_placeholder('No Camera')
    return send_file(io.BytesIO(data), mimetype='image/jpeg')


@app.route('/camera/list', methods=['GET'])
def camera_list():
    """Legacy: return all slots presented as a cameras list."""
    fw_id  = get_forward_watch_slot_id()
    result = []
    for slot_id, slot in slots.items():
        hw    = get_hw_for_slot(slot_id) or {}
        state = hw_state.get((hw or {}).get('hardware_id', ''), {})
        result.append({
            'id':               slot_id,
            'name':             slot.get('label', slot_id),
            'location':         slot.get('label', slot_id),
            'ip':               hw.get('ip', ''),
            'model':            hw.get('model', ''),
            'connected':        state.get('connected', False),
            'has_frame':        state.get('frame') is not None,
            'active':           slot_id == fw_id,
            'detection_enabled': slot.get('roles', {}).get('fish_detection', False),
            'position':         slot_id,
        })
    return jsonify({'cameras': result, 'active_camera': fw_id})


@app.route('/camera/switch/<cam_id>', methods=['POST'])
def switch_camera(cam_id):
    """Legacy: set a slot as active_default."""
    if cam_id not in slots:
        return jsonify({'error': f'Unknown slot: {cam_id}'}), 404
    _clear_exclusive_role('active_default', cam_id)
    slots[cam_id]['roles']['active_default'] = True
    save_slots()
    return jsonify({'ok': True, 'active_camera': cam_id})


@app.route('/camera/assign', methods=['POST'])
def legacy_assign():
    """Legacy position assignment — superseded by /camera/slots/<id>/assign."""
    return jsonify({
        'ok':    False,
        'error': 'Use POST /camera/slots/<slot_id>/assign with {hardware_id}. '
                 'Legacy /camera/assign not supported in the slot/hardware build.',
    }), 410


# ── Recording ─────────────────────────────────────────────────────────────────

@app.route('/camera/record/start', methods=['POST'])
def start_recording():
    global recording_instance, recording_player, recording_active
    if recording_active:
        return jsonify({'error': 'Already recording'}), 400
    fw_id = get_forward_watch_slot_id()
    hw    = get_hw_for_slot(fw_id) if fw_id else None
    if not hw:
        return jsonify({'error': 'No forward-watch camera assigned'}), 503
    state = hw_state.get(hw['hardware_id'], {})
    if not state.get('connected'):
        return jsonify({'error': 'Camera not connected'}), 503
    url = hw.get('rtsp_url', '')
    if not url:
        return jsonify({'error': 'No RTSP URL'}), 503
    ts       = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'recording_{fw_id}_{ts}.mp4'
    filepath = os.path.join(RECORDING_PATH, filename)
    os.makedirs(RECORDING_PATH, exist_ok=True)
    try:
        recording_instance = vlc.Instance()
        recording_player   = recording_instance.media_player_new()
        media = recording_instance.media_new(url)
        media.add_options(f':sout=#transcode{{vcodec=h264,vb=8000}}:file{{dst={filepath}}}')
        media.add_options(':sout-keep')
        recording_player.set_media(media)
        recording_player.play()
        recording_active = True
        print(f'✓ Recording started: {filename}')
        return jsonify({'status': 'recording_started', 'filename': filename, 'path': filepath})
    except Exception as e:
        recording_active = False
        return jsonify({'error': f'Failed to start recording: {e}'}), 500


@app.route('/camera/record/stop', methods=['POST'])
def stop_recording():
    global recording_instance, recording_player, recording_active
    if not recording_active:
        return jsonify({'error': 'Not recording'}), 400
    try:
        if recording_player:
            recording_player.stop()
            recording_player.release()
            recording_player = None
        if recording_instance:
            recording_instance.release()
            recording_instance = None
        recording_active = False
        print('✓ Recording stopped')
        return jsonify({'status': 'recording_stopped'})
    except Exception as e:
        return jsonify({'error': f'Failed to stop recording: {e}'}), 500


@app.route('/camera/recordings', methods=['GET'])
def list_recordings():
    if not os.path.exists(RECORDING_PATH):
        return jsonify({'recordings': []})
    recordings = []
    for fn in sorted(os.listdir(RECORDING_PATH), reverse=True):
        if fn.endswith('.mp4') or fn.endswith('.jpg'):
            fp = os.path.join(RECORDING_PATH, fn)
            recordings.append({
                'filename': fn,
                'size_mb':  round(os.path.getsize(fp) / 1_048_576, 2),
            })
    return jsonify({'recordings': recordings})


@app.route('/camera/capture', methods=['POST'])
def capture_photo():
    fw_id = get_forward_watch_slot_id()
    hw    = get_hw_for_slot(fw_id) if fw_id else None
    state = hw_state.get((hw or {}).get('hardware_id', ''), {})
    with state.get('lock', Lock()):
        frame_bytes = state.get('frame')
    if not frame_bytes:
        return jsonify({'error': 'No frame available'}), 503
    ts       = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'capture_{fw_id}_{ts}.jpg'
    filepath = os.path.join(RECORDING_PATH, filename)
    os.makedirs(RECORDING_PATH, exist_ok=True)
    with open(filepath, 'wb') as f:
        f.write(frame_bytes)
    print(f'✓ Photo captured: {filename}')
    return jsonify({
        'status':   'captured',
        'filename': filename,
        'path':     filepath,
        'size_mb':  round(os.path.getsize(filepath) / 1_048_576, 2),
    })


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print('=' * 60)
    print('d3kOS Camera Stream Manager — Slot/Hardware Architecture')
    print('=' * 60)
    load_config()
    start_all_grabbers()
    # Non-blocking startup scan — runs in background, doesn't delay service start
    Thread(target=run_discovery_scan, daemon=True).start()
    print()
    print('✓ Starting on port 8084...')
    app.run(host='0.0.0.0', port=8084, threaded=True)
