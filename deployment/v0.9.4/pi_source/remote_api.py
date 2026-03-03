#!/usr/bin/env python3
"""
d3kOS Remote Status API
Port: 8111

Provides authenticated REST endpoints so the boat can be monitored
from any phone or tablet — on LAN or via Tailscale.

Auth: set "remote_api_key" in /opt/d3kos/config/api-keys.json.
      If the key is empty, all requests are allowed (local-only mode).
      Pass key as: X-API-Key: <key>

Endpoints:
  GET /remote/health       — unauthenticated health check
  GET /remote/status       — all current boat metrics (engine, nav, systems)
  GET /remote/maintenance  — last 20 maintenance log entries (newest first)
  POST /remote/note        — add maintenance note from phone
                             body: {"content": "checked bilge pump"}
"""

import json
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request, abort

app = Flask(__name__)

CONFIG_PATH          = Path('/opt/d3kos/config/api-keys.json')
PREFS_PATH           = Path('/opt/d3kos/config/user-preferences.json')
MAINTENANCE_LOG_PATH = Path('/opt/d3kos/data/maintenance-log.json')
SIGNALK_API          = 'http://localhost:3000/signalk/v1/api/'


# ── Auth ──────────────────────────────────────────────────────────────────────

def _configured_key() -> str:
    try:
        return json.loads(CONFIG_PATH.read_text()).get('remote_api_key', '')
    except Exception:
        return ''

def _require_auth():
    key = _configured_key()
    if not key:
        return  # No key configured — allow (local-network mode)
    if request.headers.get('X-API-Key') != key:
        abort(401, 'Invalid or missing X-API-Key header')


# ── SignalK helpers ───────────────────────────────────────────────────────────

def _sk(path: str, timeout: int = 2):
    """Fetch a single value from SignalK. Returns the raw value or None."""
    try:
        url = f'{SIGNALK_API}vessels/self/{path}'
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return json.loads(r.read()).get('value')
    except Exception:
        return None


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.route('/remote/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat(),
                    'auth_required': bool(_configured_key())})


@app.route('/remote/status', methods=['GET'])
def status():
    _require_auth()

    rpm_raw     = _sk('propulsion/main/revolutions')      # rev/s
    oil_raw     = _sk('propulsion/main/oilPressure')      # Pa
    temp_raw    = _sk('propulsion/main/temperature')      # K
    hours_raw   = _sk('propulsion/main/runTime')          # s
    fuel_raw    = _sk('tanks/fuel/main/currentLevel')     # 0-1
    voltage_raw = _sk('electrical/batteries/house/voltage')
    sog_raw     = _sk('navigation/speedOverGround')       # m/s
    pos_raw     = _sk('navigation/position')              # {latitude, longitude}
    hdg_raw     = _sk('navigation/headingTrue')           # radians

    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'engine': {
            'rpm':             int(rpm_raw * 60)           if rpm_raw  is not None else None,
            'oil_pressure_psi': round(oil_raw / 6894.76, 1) if oil_raw  is not None else None,
            'coolant_temp_f':  round((temp_raw - 273.15) * 9/5 + 32, 1) if temp_raw is not None else None,
            'hours':           round(hours_raw / 3600, 1)  if hours_raw is not None else None,
        },
        'navigation': {
            'speed_kts':   round(sog_raw * 1.94384, 1) if sog_raw is not None else None,
            'heading_deg': round(hdg_raw * 180 / 3.141593) if hdg_raw is not None else None,
            'latitude':    pos_raw.get('latitude')  if isinstance(pos_raw, dict) else None,
            'longitude':   pos_raw.get('longitude') if isinstance(pos_raw, dict) else None,
        },
        'systems': {
            'fuel_pct':   round(fuel_raw * 100, 1) if fuel_raw    is not None else None,
            'battery_v':  round(voltage_raw, 2)    if voltage_raw is not None else None,
        },
    })


@app.route('/remote/maintenance', methods=['GET'])
def maintenance():
    _require_auth()
    try:
        log = json.loads(MAINTENANCE_LOG_PATH.read_text()) if MAINTENANCE_LOG_PATH.exists() else []
        return jsonify({'entries': list(reversed(log[-20:]))})
    except Exception as e:
        return jsonify({'entries': [], 'error': str(e)})


@app.route('/remote/note', methods=['POST'])
def add_note():
    _require_auth()
    data = request.get_json(silent=True) or {}
    content = str(data.get('content', '')).strip()
    if not content:
        abort(400, 'Missing "content" field')
    entry = {'timestamp': datetime.now().isoformat(), 'type': 'note',
             'content': content, 'source': 'remote'}
    try:
        log = json.loads(MAINTENANCE_LOG_PATH.read_text()) if MAINTENANCE_LOG_PATH.exists() else []
        log.append(entry)
        MAINTENANCE_LOG_PATH.write_text(json.dumps(log, indent=2))
        return jsonify({'ok': True, 'entry': entry}), 201
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


if __name__ == '__main__':
    print('d3kOS Remote Status API starting on port 8111...', flush=True)
    app.run(host='0.0.0.0', port=8111, debug=False)
