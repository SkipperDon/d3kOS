def camera_status():
    state = cam_state.get(active_id, {})
    connected = state.get('connected', False)
    has_frame  = state.get('frame') is not None
    cam        = cameras.get(active_id, {})
    rtsp_url   = cam.get('rtsp_url', '')
    # Ensure status fields exist
    camera = {
        'connected':  connected,
        'has_frame':  has_frame,
        'camera_id':  active_id,
        'camera_ip':  cam.get('ip', 'Not configured'),
        'camera_name': cam.get('name', active_id),
        'rtsp_url':   rtsp_url.replace(RTSP_PASSWORD, '****') if rtsp_url else 'Not configured',
        'recording':  recording_active,
        'service':    'd3kos-camera-stream',
        'port':       8084,
        'status':     'online' if connected else 'offline',
        'offline_reason': 'Camera unreachable — connect to boat network' if not connected else ''
    }