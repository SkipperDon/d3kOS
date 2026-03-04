#!/usr/bin/env python3
"""
d3kOS Camera Stream Manager — Multi-Camera
Port: 8084

Manages multiple RTSP cameras. Each camera runs its own frame-grabber thread.
One camera is "active" at a time; backwards-compatible single-camera endpoints
always reference the active camera.

Config: /opt/d3kos/config/cameras.json
Recording: /home/d3kos/camera-recordings/

Endpoints (backwards-compatible):
  GET  /camera/status           — active camera status
  GET  /camera/frame            — current frame from active camera
  POST /camera/record/start     — start recording active camera
  POST /camera/record/stop      — stop recording
  GET  /camera/recordings       — list recordings
  POST /camera/capture          — capture photo from active camera

New multi-camera endpoints:
  GET  /camera/list             — all cameras + status
  GET  /camera/frame/<id>       — frame from specific camera
  POST /camera/switch/<id>      — switch active camera
  GET  /camera/grid             — side-by-side JPEG of all cameras
"""

from flask import Flask, jsonify, send_file, request
import cv2
import numpy as np
import vlc
import time
import os
import json
from datetime import datetime
from threading import Thread, Lock
import io

app = Flask(__name__)
@app.route('/camera/assign/<cam_id>/<position>', methods=['POST'])
def assign_camera(cam_id, position):
    """Assign a camera to a specific position (e.g., 'top-left', 'bottom-right')."""
    # Validate position
    valid_positions = ['top-left', 'top-right', 'bottom-left', 'bottom-right', 'center']
    if position not in valid_positions:
        return jsonify({'error': 'Invalid position'}), 400
    
    if cam_id not in cameras:
        return jsonify({'error': 'Camera not found'}), 404
    
    # Load current config
    with open(CAMERAS_CONFIG) as f:
        cfg = json.load(f)
    
    # Find the camera in the list and update its position
    for cam in cfg.get('cameras', []):
        if cam['id'] == cam_id:
            cam['position'] = position
            break
    
    # Save updated config
    with open(CAMERAS_CONFIG, 'w') as f:
        json.dump(cfg, f)
    
    return jsonify({'status': 'success', 'message': f'Camera {cam_id} assigned to {position}'})
def assign_camera(cam_id, position):
    """Assign a camera to a specific position (e.g., 'top-left', 'bottom-right')."""
    if cam_id not in cameras:
        return jsonify({'error': 'Camera not found'}), 404
    
    # Load current config
    with open(CAMERAS_CONFIG) as f:
        cfg = json.load(f)
    
    # Find the camera in the list and update its position
    for cam in cfg.get('cameras', []):
        if cam['id'] == cam_id:
            cam['position'] = position
            break
    
    # Save updated config
    with open(CAMERAS_CONFIG, 'w') as f:
        json.dump(cfg, f)
    
    return jsonify({'status': 'success', 'message': f'Camera {cam_id} assigned to {position}'})

CAMERAS_CONFIG     = '/opt/d3kos/config/cameras.json'
RECORDING_PATH     = '/home/d3kos/camera-recordings'
RTSP_USERNAME      = 'admin'
RTSP_PASSWORD      = 'd3kos2026'

# Per-camera state — keyed by camera id
cameras     = {}       # id → config dict from JSON
cam_state   = {}       # id → {'cap', 'frame', 'lock', 'connected', 'thread'}
active_id   = None     # id of the currently active camera

# Recording state (always applies to active camera)
recording_instance = None
recording_player   = None
recording_active   = False


# ── Startup ──────────────────────────────────────────────────────────────────

def load_cameras():
    global cameras, active_id
    if not os.path.exists(CAMERAS_CONFIG):
        print(f'✗ cameras.json not found: {CAMERAS_CONFIG}')
        return False
    with open(CAMERAS_CONFIG) as f:
        cfg = json.load(f)
    cameras   = {c['id']: c for c in cfg.get('cameras', [])}
    active_id = cfg.get('active_camera') or (list(cameras.keys())[0] if cameras else None)
    print(f'✓ Loaded {len(cameras)} camera(s): {list(cameras.keys())}')
    print(f'✓ Active camera: {active_id}')
    return True


def init_camera(cam_id):
    """Open cv2.VideoCapture for one camera. Returns cap or None."""
    cam = cameras.get(cam_id)
    if not cam:
        return None
    url = cam['rtsp_url']
    print(f'  Connecting to {cam_id} ({cam["ip"]})...')
    cap = cv2.VideoCapture(url)
    if cap.isOpened():
        print(f'  ✓ {cam_id} connected')
        return cap
    cap.release()
    print(f'  ✗ {cam_id} connection failed (will retry)')
    return None


def frame_grabber(cam_id):
    """Background thread: continuously grab frames for one camera."""
    state           = cam_state[cam_id]
    reconnect_delay = 10
    last_attempt    = 0

    while True:
        cap = state['cap']
        if cap and cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                with state['lock']:
                    state['frame']     = frame
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
                    state['cap'] = init_camera(cam_id)
            time.sleep(0.033)   # ~30 FPS
        else:
            state['connected'] = False
            now = time.time()
            if now - last_attempt > reconnect_delay:
                last_attempt = now
                state['cap'] = init_camera(cam_id)
            time.sleep(2)


def start_all():
    """Initialise state dicts and launch one grabber thread per camera."""
    for cam_id in cameras:
        state = {
            'cap':       None,
            'frame':     None,
            'lock':      Lock(),
            'connected': False,
            'thread':    None,
        }
        state['cap'] = init_camera(cam_id)
        cam_state[cam_id] = state

        t = Thread(target=frame_grabber, args=(cam_id,), daemon=True)
        t.start()
        state['thread'] = t
        print(f'✓ Frame grabber started for {cam_id}')


# ── Helpers ───────────────────────────────────────────────────────────────────

def _encode_frame(frame, quality=85):
    """Encode numpy frame to JPEG bytes or None."""
    ret, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return buf.tobytes() if ret else None


def _offline_placeholder(label='Offline'):
    """Return a small black JPEG with white text for disconnected cameras."""
    img = np.zeros((240, 426, 3), dtype=np.uint8)
    cv2.putText(img, label, (120, 130),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 200, 0), 2, cv2.LINE_AA)
    _, buf = cv2.imencode('.jpg', img)
    return buf.tobytes()


def _frame_or_placeholder(cam_id):
    """Return JPEG bytes: real frame if available, offline placeholder otherwise."""
    state = cam_state.get(cam_id)
    if state:
        with state['lock']:
            frame = state['frame']
        if frame is not None:
            return _encode_frame(frame)
    cam = cameras.get(cam_id, {})
    return _offline_placeholder(cam.get('name', cam_id) + ' Offline')


# ── Backwards-compatible endpoints ────────────────────────────────────────────

@app.route('/camera/status', methods=['GET'])
def camera_status():
    state = cam_state.get(active_id, {})
    connected = state.get('connected', False)
    has_frame  = state.get('frame') is not None
    cam        = cameras.get(active_id, {})
    rtsp_url   = cam.get('rtsp_url', '')
    return jsonify({
        'connected':  connected,
        'has_frame':  has_frame,
        'camera_id':  active_id,
        'camera_ip':  cam.get('ip', 'Not configured'),
        'camera_name': cam.get('name', active_id),
        'rtsp_url':   rtsp_url.replace(RTSP_PASSWORD, '****') if rtsp_url else 'Not configured',
        'recording':  recording_active,
        'service':    'd3kos-camera-stream',
        'port':       8084,
    })


@app.route('/camera/frame', methods=['GET'])
def get_frame():
    """Return JPEG from active camera."""
    data = _frame_or_placeholder(active_id)
    if data is None:
        return jsonify({'error': 'No frame available'}), 503
    return send_file(io.BytesIO(data), mimetype='image/jpeg')


@app.route('/camera/record/start', methods=['POST'])
def start_recording():
    global recording_instance, recording_player, recording_active
    if recording_active:
        return jsonify({'error': 'Already recording'}), 400
    state = cam_state.get(active_id, {})
    if not state.get('connected'):
        return jsonify({'error': 'Camera not connected'}), 503
    cam     = cameras.get(active_id, {})
    url     = cam.get('rtsp_url', '')
    if not url:
        return jsonify({'error': 'No RTSP URL for active camera'}), 503
    ts       = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'recording_{active_id}_{ts}.mp4'
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
            fp  = os.path.join(RECORDING_PATH, fn)
            recordings.append({
                'filename': fn,
                'size_mb':  round(os.path.getsize(fp) / 1_048_576, 2),
            })
    return jsonify({'recordings': recordings})


@app.route('/camera/capture', methods=['POST'])
def capture_photo():
    state = cam_state.get(active_id, {})
    with state.get('lock', Lock()):
        frame = state.get('frame')
    if frame is None:
        return jsonify({'error': 'No frame available'}), 503
    ts       = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'capture_{active_id}_{ts}.jpg'
    filepath = os.path.join(RECORDING_PATH, filename)
    os.makedirs(RECORDING_PATH, exist_ok=True)
    cv2.imwrite(filepath, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
    print(f'✓ Photo captured: {filename}')
    return jsonify({
        'status':   'captured',
        'filename': filename,
        'path':     filepath,
        'size_mb':  round(os.path.getsize(filepath) / 1_048_576, 2),
    })


# ── New multi-camera endpoints ────────────────────────────────────────────────

@app.route('/camera/list', methods=['GET'])
def camera_list():
    """Return all cameras with their current connection status."""
    result = []
    for cam_id, cam in cameras.items():
        state = cam_state.get(cam_id, {})
        result.append({
            'id':        cam_id,
            'name':      cam.get('name', cam_id),
            'location':  cam.get('location', ''),
            'ip':        cam.get('ip', ''),
            'model':     cam.get('model', ''),
            'connected': state.get('connected', False),
            'has_frame': state.get('frame') is not None,
            'active':    cam_id == active_id,
            'detection_enabled': cam.get('detection_enabled', False),
        })
    return jsonify({'cameras': result, 'active_camera': active_id})


@app.route('/camera/frame/<cam_id>', methods=['GET'])
def get_frame_by_id(cam_id):
    """Return JPEG frame from a specific camera."""
    if cam_id not in cameras:
        return jsonify({'error': f'Unknown camera: {cam_id}'}), 404
    data = _frame_or_placeholder(cam_id)
    return send_file(io.BytesIO(data), mimetype='image/jpeg')


@app.route('/camera/switch/<cam_id>', methods=['POST'])
def switch_camera(cam_id):
    """Switch the active camera."""
    global active_id
    if cam_id not in cameras:
        return jsonify({'error': f'Unknown camera: {cam_id}'}), 404
    active_id = cam_id
    print(f'✓ Active camera switched to: {cam_id}')
    return jsonify({'ok': True, 'active_camera': active_id})


@app.route('/camera/grid', methods=['GET'])
def camera_grid():
    """Return a side-by-side JPEG of all cameras (max 2 wide)."""
    frames = []
    target_h = 360
    target_w = 640

    for cam_id in cameras:
        data = _frame_or_placeholder(cam_id)
        arr  = np.frombuffer(data, dtype=np.uint8)
        img  = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            img = np.zeros((target_h, target_w, 3), dtype=np.uint8)
        # Resize to uniform height
        h, w = img.shape[:2]
        scale  = target_h / h
        img    = cv2.resize(img, (int(w * scale), target_h))
        # Pad or crop to target width
        ch, cw = img.shape[:2]
        if cw < target_w:
            pad  = np.zeros((ch, target_w - cw, 3), dtype=np.uint8)
            img  = np.hstack([img, pad])
        elif cw > target_w:
            img  = img[:, :target_w]
        frames.append(img)

    grid = np.hstack(frames) if frames else np.zeros((target_h, target_w, 3), dtype=np.uint8)
    ret, buf = cv2.imencode('.jpg', grid, [cv2.IMWRITE_JPEG_QUALITY, 80])
    if not ret:
        return jsonify({'error': 'Failed to encode grid'}), 500
    return send_file(io.BytesIO(buf.tobytes()), mimetype='image/jpeg')


# ── Main ─────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print('=' * 60)
    print('d3kOS Camera Stream Manager — Multi-Camera')
    print('=' * 60)

    if not load_cameras():
        print('⚠ No cameras configured — service will start but no feeds available')
    else:
        start_all()

    print()
    print('✓ Starting on port 8084...')
    app.run(host='0.0.0.0', port=8084, threaded=True)
