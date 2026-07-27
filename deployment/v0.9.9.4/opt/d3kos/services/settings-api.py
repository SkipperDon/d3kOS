#!/usr/bin/env python3
"""d3kOS Settings Action API — port 8102"""
import subprocess
from flask import Flask, jsonify, request

app = Flask(__name__)

ALLOWED_COMMANDS = {
    'restart-signalk':  ['sudo', 'systemctl', 'restart', 'signalk'],
    'restart-nodered':  ['sudo', 'systemctl', 'restart', 'nodered'],
    'reboot':           ['sudo', 'reboot'],
}

@app.route('/settings/action/<action>', methods=['POST'])
def run_action(action):
    if action not in ALLOWED_COMMANDS:
        return jsonify({'success': False, 'error': 'Unknown action'}), 400
    try:
        result = subprocess.run(ALLOWED_COMMANDS[action], capture_output=True, text=True, timeout=15)
        return jsonify({'success': True, 'message': f'{action} triggered', 'output': result.stdout})
    except subprocess.TimeoutExpired:
        return jsonify({'success': True, 'message': f'{action} triggered (no response expected)'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/settings/action/initial-setup-reset', methods=['POST'])
def initial_setup_reset():
    # Call existing reset logic
    try:
        subprocess.run(['/opt/d3kos/scripts/sanitize.sh'], timeout=30)
        return jsonify({'success': True, 'message': 'Initial setup reset complete'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8102)