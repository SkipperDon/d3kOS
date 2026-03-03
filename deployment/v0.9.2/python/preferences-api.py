#!/usr/bin/env python3
"""
d3kOS User Preferences API
Version: 0.9.2
Port: 8107
Manages user preferences including measurement_system (imperial/metric)
"""
import json
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

CONFIG_FILE = '/opt/d3kos/config/user-preferences.json'

DEFAULTS = {
    'measurement_system': 'imperial',
    'language': 'en',
    'timezone': 'UTC',
    'theme': 'dark'
}

VALID_SYSTEMS = ['imperial', 'metric']


def load_prefs():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                return {**DEFAULTS, **json.load(f)}
        except Exception:
            pass
    return DEFAULTS.copy()


def save_prefs(prefs):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(prefs, f, indent=2)


@app.route('/preferences', methods=['GET'])
@app.route('/api/preferences', methods=['GET'])
def get_prefs():
    return jsonify(load_prefs())


@app.route('/preferences', methods=['POST'])
@app.route('/api/preferences', methods=['POST'])
def set_prefs():
    data = request.get_json(force=True) or {}
    if 'measurement_system' in data:
        if data['measurement_system'] not in VALID_SYSTEMS:
            return jsonify({'error': 'measurement_system must be "imperial" or "metric"'}), 400
    prefs = load_prefs()
    prefs.update({k: v for k, v in data.items() if k in DEFAULTS})
    save_prefs(prefs)
    return jsonify({'success': True, 'preferences': prefs})


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'preferences-api', 'version': '0.9.2'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8107, debug=False)
