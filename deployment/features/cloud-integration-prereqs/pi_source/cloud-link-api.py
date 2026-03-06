#!/usr/bin/env python3
"""
d3kOS Cloud Link API — Port 8091
Handles registration handshake between Pi and atmyboat.com website.
T0 devices: this service runs but cloud-credentials.json is never written.
T1+ devices: website POSTs credentials after user registers, Pi saves them.
"""

import json
import os
import time
import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

CREDENTIALS_FILE = '/opt/d3kos/config/cloud-credentials.json'
LAST_PUSH_FILE   = '/opt/d3kos/data/telemetry-last-push.txt'
VERSION_FILE     = '/opt/d3kos/config/version.txt'
START_TIME       = time.time()


def read_credentials():
    if not os.path.exists(CREDENTIALS_FILE):
        return None
    try:
        with open(CREDENTIALS_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return None


def read_version():
    try:
        with open(VERSION_FILE, 'r') as f:
            return f.read().strip()
    except Exception:
        return 'unknown'


def read_last_push():
    try:
        with open(LAST_PUSH_FILE, 'r') as f:
            return f.read().strip()
    except Exception:
        return None


@app.route('/api/link', methods=['POST'])
def link_device():
    """Receive credentials from atmyboat.com and write cloud-credentials.json."""
    data = request.get_json(silent=True) or {}
    required = ['boat_uuid', 'device_api_key', 'supabase_url', 'supabase_anon_key', 'tier']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({'success': False, 'error': f'Missing fields: {", ".join(missing)}'}), 400

    credentials = {
        'boat_uuid':        data['boat_uuid'],
        'device_api_key':   data['device_api_key'],
        'supabase_url':     data['supabase_url'],
        'supabase_anon_key': data['supabase_anon_key'],
        'webhook_url':      data.get('webhook_url', 'https://atmyboat.com/api/notify'),
        'tier':             data['tier'],
        'linked_at':        datetime.utcnow().isoformat() + 'Z'
    }

    try:
        os.makedirs(os.path.dirname(CREDENTIALS_FILE), exist_ok=True)
        with open(CREDENTIALS_FILE, 'w') as f:
            json.dump(credentials, f, indent=2)
        os.chmod(CREDENTIALS_FILE, 0o600)
        return jsonify({'success': True, 'tier': data['tier']})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/status', methods=['GET'])
def get_status():
    """Return cloud link status — called by atmyboat.com to verify Pi is reachable."""
    creds = read_credentials()
    uptime = int(time.time() - START_TIME)

    if not creds:
        return jsonify({
            'linked': False,
            'tier': 't0',
            'firmware_version': read_version(),
            'uptime_seconds': uptime,
            'last_push': None
        })

    return jsonify({
        'linked': True,
        'tier': creds.get('tier', 't1'),
        'boat_uuid': creds.get('boat_uuid'),
        'firmware_version': read_version(),
        'uptime_seconds': uptime,
        'last_push': read_last_push()
    })


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'd3kos-cloud-link'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8092, debug=False)
