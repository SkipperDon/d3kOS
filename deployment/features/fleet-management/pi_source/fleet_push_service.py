#!/usr/bin/env python3
"""
d3kOS Fleet Push Service — Port 8107
Pushes GPS position + engine snapshot to HostPapa fleet-ingest.php every 1 minute
when engine is on or GPS fix is active. Idles otherwise.

Service: d3kos-fleet-push.service
Config:  /opt/d3kos/config/fleet.json  (written by PWA when device joins fleet)
License: /opt/d3kos/config/license.json (tier check)

fleet.json schema:
  { "fleet_id": N, "fleet_code": "ABC123", "role": "owner|member" }

Environment (from /opt/d3kos/services/fleet/config/fleet-push.env):
  FLEET_INGEST_URL=https://atmyboat.com/staging/mobile/fleet-ingest.php
  AMBOAT_API_KEY=<key>
  SIGNALK_URL=http://localhost:8099
  PREDICTIVE_STATUS_URL=http://localhost:8106/predictive/status
  PUSH_INTERVAL_S=60
"""

import json
import logging
import os
import sys
import threading
import time
from pathlib import Path

import requests
from flask import Flask, jsonify

# ── Config ────────────────────────────────────────────────────────────────────
_ENV = Path('/opt/d3kos/services/fleet/config/fleet-push.env')
if _ENV.is_file():
    from dotenv import load_dotenv
    load_dotenv(_ENV)

FLEET_INGEST_URL  = os.environ.get('FLEET_INGEST_URL',
                                   'https://atmyboat.com/staging/mobile/fleet-ingest.php')
AMBOAT_API_KEY    = os.environ.get('AMBOAT_API_KEY', '')
SIGNALK_URL       = os.environ.get('SIGNALK_URL',   'http://localhost:8099')
PREDICTIVE_URL    = os.environ.get('PREDICTIVE_STATUS_URL', 'http://localhost:8106/predictive/status')
PUSH_INTERVAL_S   = int(os.environ.get('PUSH_INTERVAL_S', 60))
PORT              = int(os.environ.get('FLEET_PUSH_PORT', 8108))

FLEET_CONFIG      = Path('/opt/d3kos/config/fleet.json')
LICENSE_CONFIG    = Path('/opt/d3kos/config/license.json')
DEVICE_TOKEN_FILE = Path('/opt/d3kos/config/device-token.json')

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [fleet_push] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
log = logging.getLogger('fleet_push')

app   = Flask(__name__)
_state = {'last_push': None, 'last_status': 'idle', 'push_count': 0, 'error': None}
_lock  = threading.Lock()


# ── Config readers ────────────────────────────────────────────────────────────

def _load_fleet_config() -> dict | None:
    """Returns fleet config dict or None if device hasn't joined a fleet."""
    if not FLEET_CONFIG.is_file():
        return None
    try:
        return json.loads(FLEET_CONFIG.read_text())
    except Exception as exc:
        log.warning('fleet.json unreadable: %s', exc)
        return None


def _load_device_token() -> str | None:
    if not DEVICE_TOKEN_FILE.is_file():
        return None
    try:
        data = json.loads(DEVICE_TOKEN_FILE.read_text())
        return data.get('device_token') or data.get('token')
    except Exception:
        return None


def _get_tier() -> int:
    """Read tier from license.json. Returns integer 0-3."""
    if not LICENSE_CONFIG.is_file():
        return 0
    try:
        data   = json.loads(LICENSE_CONFIG.read_text())
        raw    = data.get('tier', 0)
        # Handle "T3" string or integer 3
        if isinstance(raw, str) and raw.startswith('T'):
            return int(raw[1:])
        return int(raw)
    except Exception:
        return 0


# ── SignalK data reader ───────────────────────────────────────────────────────

def _get_signalk_position() -> dict:
    """Fetch GPS position and speed from SignalK. Returns partial dict."""
    result = {}
    try:
        r = requests.get(
            f'{SIGNALK_URL}/signalk/v1/api/vessels/self',
            timeout=3,
        )
        if r.status_code != 200:
            return result
        data = r.json()
        nav  = data.get('navigation', {})

        pos = nav.get('position', {}).get('value', {})
        if pos.get('latitude') and pos.get('longitude'):
            result['lat'] = round(pos['latitude'],  6)
            result['lon'] = round(pos['longitude'], 6)

        cog_rad = nav.get('courseOverGroundTrue', {}).get('value')
        if cog_rad is not None:
            import math
            result['cog'] = round(math.degrees(cog_rad) % 360, 1)

        sog_ms = nav.get('speedOverGround', {}).get('value')
        if sog_ms is not None:
            result['sog'] = round(sog_ms * 1.94384, 2)  # m/s → knots

    except Exception as exc:
        log.debug('SignalK GPS read failed: %s', exc)
    return result


def _get_engine_data() -> dict:
    """Fetch engine snapshot from predictive status endpoint."""
    result = {}
    try:
        r = requests.get(PREDICTIVE_URL, timeout=3)
        if r.status_code != 200:
            return result
        data = r.json()

        # predictive/status returns risk_state with field values
        for field, key in [
            ('rpm',             'rpm'),
            ('oil_pressure_kpa', 'oil_pressure_kpa'),
            ('coolant_temp_c',  'coolant_temp_c'),
        ]:
            val = data.get(field, {}).get('value')
            if val is not None:
                result[key] = val

        # Engine hours from predictive status if present
        if 'engine_hours' in data:
            result['engine_hours'] = data['engine_hours']

    except Exception as exc:
        log.debug('Engine data read failed: %s', exc)
    return result


def _is_active(pos: dict, engine: dict) -> bool:
    """Returns True if we should push — GPS fix present or engine running."""
    has_gps    = 'lat' in pos and 'lon' in pos
    engine_rpm = engine.get('rpm', 0) or 0
    return has_gps or engine_rpm > 200


# ── Push loop ─────────────────────────────────────────────────────────────────

def _push_loop():
    log.info('Fleet push loop started. Interval: %ds', PUSH_INTERVAL_S)
    while True:
        time.sleep(PUSH_INTERVAL_S)
        try:
            _do_push()
        except Exception as exc:
            log.error('Push loop error: %s', exc)
            with _lock:
                _state['error'] = str(exc)


def _do_push():
    # Check tier
    if _get_tier() < 3:
        with _lock:
            _state['last_status'] = 'idle_tier'
        return

    # Load fleet config
    fleet = _load_fleet_config()
    if not fleet or not fleet.get('fleet_id'):
        with _lock:
            _state['last_status'] = 'idle_no_fleet'
        return

    device_token = _load_device_token()
    if not device_token:
        log.warning('device_token not found — cannot push')
        return

    # Collect data
    pos    = _get_signalk_position()
    engine = _get_engine_data()

    if not _is_active(pos, engine):
        with _lock:
            _state['last_status'] = 'idle_inactive'
        log.debug('No GPS fix and engine off — skipping push')
        return

    if 'lat' not in pos or 'lon' not in pos:
        with _lock:
            _state['last_status'] = 'skip_no_gps'
        log.debug('No GPS position available — skipping push')
        return

    payload = {'fleet_id': fleet['fleet_id'], **pos, **engine}

    try:
        r = requests.post(
            FLEET_INGEST_URL,
            json=payload,
            headers={
                'Authorization':  f'Bearer {AMBOAT_API_KEY}',
                'X-Device-Token': device_token,
                'Content-Type':   'application/json',
            },
            timeout=10,
        )
        if r.status_code == 200:
            with _lock:
                _state['last_push']   = time.time()
                _state['last_status'] = 'ok'
                _state['push_count'] += 1
                _state['error']       = None
            log.debug('Position pushed OK (fleet %d, pos %.4f,%.4f)',
                      fleet['fleet_id'], pos['lat'], pos['lon'])
        else:
            log.warning('Ingest returned %d: %s', r.status_code, r.text[:200])
            with _lock:
                _state['last_status'] = f'error_{r.status_code}'
    except requests.RequestException as exc:
        log.warning('Ingest POST failed: %s', exc)
        with _lock:
            _state['last_status'] = 'error_network'
            _state['error']       = str(exc)


# ── Status endpoint ────────────────────────────────────────────────────────────

@app.route('/fleet/status', methods=['GET'])
def status():
    fleet  = _load_fleet_config()
    tier   = _get_tier()
    with _lock:
        st = dict(_state)
    return jsonify({
        'service':        'd3kos-fleet-push',
        'tier':           tier,
        'fleet_id':       fleet.get('fleet_id') if fleet else None,
        'fleet_code':     fleet.get('fleet_code') if fleet else None,
        'push_interval_s': PUSH_INTERVAL_S,
        'push_count':     st['push_count'],
        'last_status':    st['last_status'],
        'last_push_ago_s': int(time.time() - st['last_push']) if st['last_push'] else None,
        'error':          st['error'],
    })


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    if not AMBOAT_API_KEY:
        log.error('AMBOAT_API_KEY not set — fleet push will fail auth')

    t = threading.Thread(target=_push_loop, daemon=True)
    t.start()

    log.info('Fleet push service starting on port %d', PORT)
    app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)
