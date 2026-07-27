#!/usr/bin/env python3
"""
d3kOS Timezone API
Port: 8098
Endpoints: GET/POST /api/timezone, POST /api/timezone/redetect
"""

import json
import os
import subprocess
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

TIMEZONE_FILE = '/opt/d3kos/config/timezone.txt'
DETECTION_SCRIPT = '/opt/d3kos/scripts/detect-timezone.sh'

@app.route('/api/timezone', methods=['GET'])
def get_timezone():
    """Get current timezone configuration"""
    try:
        # Read configured timezone
        if os.path.exists(TIMEZONE_FILE):
            with open(TIMEZONE_FILE, 'r') as f:
                timezone = f.read().strip()
        else:
            timezone = 'Not configured'

        # Get system timezone
        result = subprocess.run(['timedatectl', 'show', '--property=Timezone'],
                                capture_output=True, text=True)
        system_tz = result.stdout.strip().split('=')[1] if '=' in result.stdout else 'Unknown'

        # Determine detection method
        if timezone == 'UTC':
            method = 'Fallback (UTC)'
        elif timezone == system_tz:
            method = 'Auto-detected'
        else:
            method = 'Manual override'

        return jsonify({
            'success': True,
            'timezone': timezone,
            'system_timezone': system_tz,
            'method': method
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/timezone', methods=['POST'])
def set_timezone():
    """Manually set timezone"""
    try:
        data = request.get_json()
        timezone = data.get('timezone', '').strip()

        if not timezone:
            return jsonify({'success': False, 'error': 'Timezone required'}), 400

        # Set system timezone
        result = subprocess.run(['timedatectl', 'set-timezone', timezone],
                                capture_output=True, text=True)

        if result.returncode != 0:
            return jsonify({'success': False, 'error': result.stderr}), 500

        # Save to config
        with open(TIMEZONE_FILE, 'w') as f:
            f.write(timezone)

        return jsonify({'success': True, 'timezone': timezone})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/timezone/redetect', methods=['POST'])
def redetect_timezone():
    """Re-run auto-detection"""
    try:
        # Remove config file to trigger re-detection
        if os.path.exists(TIMEZONE_FILE):
            os.remove(TIMEZONE_FILE)

        # Run detection script
        result = subprocess.run([DETECTION_SCRIPT],
                                capture_output=True, text=True)

        if result.returncode != 0:
            return jsonify({'success': False, 'error': result.stderr}), 500

        return jsonify({'success': True, 'message': 'Timezone re-detected'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8098, debug=False)
