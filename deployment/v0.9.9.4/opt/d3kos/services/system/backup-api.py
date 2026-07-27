#!/usr/bin/env python3
"""
d3kOS Backup API
Provides HTTP API for backup and restore operations
Port: 8100
"""

from flask import Flask, jsonify, send_file
import subprocess
import os
import glob

app = Flask(__name__)

BACKUP_DIR = '/opt/d3kos/backups'
BACKUP_SCRIPT = '/opt/d3kos/scripts/create-backup.sh'

@app.route('/api/backup/create', methods=['POST'])
def create_backup():
    """Create new backup"""
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)

        result = subprocess.run(
            [BACKUP_SCRIPT],
            capture_output=True,
            text=True,
            check=True
        )

        # Get latest backup file
        backups = glob.glob(f"{BACKUP_DIR}/d3kos_backup_*.tar.gz")
        if not backups:
            return jsonify({
                'success': False,
                'error': 'Backup created but file not found'
            }), 500

        latest = max(backups, key=os.path.getctime)

        return jsonify({
            'success': True,
            'backup_file': os.path.basename(latest),
            'size_bytes': os.path.getsize(latest),
            'path': latest
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/backup/list', methods=['GET'])
def list_backups():
    """List all backups"""
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        backups = glob.glob(f"{BACKUP_DIR}/d3kos_backup_*.tar.gz")

        backup_list = [{
            'filename': os.path.basename(b),
            'size_bytes': os.path.getsize(b),
            'created': os.path.getctime(b),
            'path': b
        } for b in sorted(backups, key=os.path.getctime, reverse=True)]

        return jsonify({'success': True, 'backups': backup_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/backup/download/<filename>', methods=['GET'])
def download_backup(filename):
    """Download backup file"""
    try:
        filepath = os.path.join(BACKUP_DIR, filename)

        if not os.path.exists(filepath):
            return jsonify({'success': False, 'error': 'File not found'}), 404

        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'ok', 'service': 'backup-api'})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8100, debug=False)
