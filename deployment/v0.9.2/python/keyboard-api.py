#!/usr/bin/env python3
"""
d3kOS Keyboard API
Controls squeekboard on-screen keyboard via DBus (sm.puri.OSK0.SetVisible).
Bypasses zwp_text_input_v3 which Chromium does not trigger on real touch events
when labwc mouseEmulation="no".
Port: 8087 (localhost only, proxied by nginx at /keyboard/)
"""

import subprocess
import time
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# DBus session environment for user d3kos (uid 1000)
_ENV = {
    'DBUS_SESSION_BUS_ADDRESS': 'unix:path=/run/user/1000/bus',
    'XDG_RUNTIME_DIR': '/run/user/1000',
    'PATH': '/usr/bin:/bin',
}

_DBUS_BASE = [
    'dbus-send',
    '--session',
    '--dest=sm.puri.OSK0',
    '--type=method_call',
    '--print-reply',
    '/sm/puri/OSK0',
    'sm.puri.OSK0.SetVisible',
]


def _set_visible(visible: bool) -> bool:
    cmd = _DBUS_BASE + ['boolean:true' if visible else 'boolean:false']
    try:
        result = subprocess.run(cmd, env=_ENV, capture_output=True, text=True, timeout=3)
        return result.returncode == 0
    except Exception:
        return False


@app.route('/keyboard/show', methods=['POST'])
def show():
    ok = _set_visible(True)
    return jsonify({'ok': ok})


@app.route('/keyboard/hide', methods=['POST'])
def hide():
    ok = _set_visible(False)
    return jsonify({'ok': ok})


_WAYLAND_ENV = {
    'DBUS_SESSION_BUS_ADDRESS': 'unix:path=/run/user/1000/bus',
    'XDG_RUNTIME_DIR': '/run/user/1000',
    'WAYLAND_DISPLAY': 'wayland-0',
    'PATH': '/usr/bin:/bin',
}

_STATE_FILE = '/tmp/d3kos-fullscreen-state'


def _read_window_state() -> str:
    try:
        with open(_STATE_FILE) as f:
            return f.read().strip()
    except Exception:
        return 'fullscreen'


def _write_window_state(state: str) -> None:
    try:
        with open(_STATE_FILE, 'w') as f:
            f.write(state)
    except Exception:
        pass


@app.route('/window/windowed', methods=['POST'])
def go_windowed():
    if _read_window_state() != 'windowed':
        try:
            subprocess.run(['wtype', '-k', 'F11'], env=_WAYLAND_ENV,
                           capture_output=True, timeout=3)
            time.sleep(0.3)
            subprocess.run(['wlrctl', 'toplevel', 'maximize', 'app_id:chromium'],
                           env=_WAYLAND_ENV, capture_output=True, timeout=3)
            _write_window_state('windowed')
        except Exception:
            return jsonify({'ok': False})
    return jsonify({'ok': True})


@app.route('/window/fullscreen', methods=['POST'])
def go_fullscreen():
    if _read_window_state() != 'fullscreen':
        try:
            subprocess.run(['wlrctl', 'toplevel', 'fullscreen', 'app_id:chromium'],
                           env=_WAYLAND_ENV, capture_output=True, timeout=3)
            _write_window_state('fullscreen')
        except Exception:
            return jsonify({'ok': False})
    return jsonify({'ok': True})


@app.route('/window/toggle', methods=['POST'])
def toggle_window():
    if _read_window_state() == 'windowed':
        return go_fullscreen()
    else:
        return go_windowed()


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8087, debug=False)
