#!/usr/bin/env python3
"""
d3kOS Issue Detector Service
Monitors system health and detects anomalies
"""

import psutil
import subprocess
import time
import json
import os
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, jsonify

app = Flask(__name__)

class IssueDetector:
    def __init__(self):
        # Env override exists only for verify-bug105.sh (scratch DB). Production sets nothing.
        self.db_path = os.environ.get('D3KOS_ISSUES_DB', '/opt/d3kos/data/self-healing/issues.db')
        self.init_database()

    def init_database(self):
        """Initialize SQLite database for issue tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                category TEXT NOT NULL,
                severity TEXT NOT NULL,
                description TEXT NOT NULL,
                metrics TEXT,
                status TEXT DEFAULT 'detected',
                resolved_at TEXT,
                remediation_action TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def check_cpu_temp(self):
        """Check Raspberry Pi CPU temperature"""
        try:
            temp = psutil.sensors_temperatures()['cpu_thermal'][0].current
            if temp > 80:
                return {
                    'category': 'cpu_temperature',
                    'severity': 'critical' if temp > 85 else 'warning',
                    'description': f'CPU temperature high: {temp}°C',
                    'metrics': json.dumps({'temp': temp})
                }
        except Exception as e:
            print(f"Error checking CPU temp: {e}")
        return None

    def check_memory(self):
        """Check system memory usage"""
        mem = psutil.virtual_memory()
        if mem.percent > 90:
            return {
                'category': 'memory',
                'severity': 'critical' if mem.percent > 95 else 'warning',
                'description': f'Memory usage high: {mem.percent}%',
                'metrics': json.dumps({
                    'percent': mem.percent,
                    'available_mb': mem.available / 1024 / 1024
                })
            }
        return None

    def check_disk_space(self):
        """Check disk space on root and data partitions"""
        issues = []
        for partition in ['/', '/media/d3kos']:
            try:
                disk = psutil.disk_usage(partition)
                if disk.percent > 90:
                    issues.append({
                        'category': 'disk_space',
                        'severity': 'critical' if disk.percent > 95 else 'warning',
                        'description': f'{partition} disk usage high: {disk.percent}%',
                        'metrics': json.dumps({
                            'partition': partition,
                            'percent': disk.percent,
                            'free_gb': disk.free / 1024 / 1024 / 1024
                        })
                    })
            except:
                pass
        return issues[0] if issues else None

    def check_services(self):
        """Check critical d3kOS services"""
        critical_services = [
            'd3kos-license-api',
            'd3kos-ai-api',
            'd3kos-camera-stream',
            'd3kos-timezone-api'
        ]

        for service in critical_services:
            result = subprocess.run(
                ['systemctl', 'is-active', service],
                capture_output=True,
                text=True
            )
            # BUG-105: only 'failed' is an issue. 'inactive' is a clean stop — a tier-gated unit
            # skipped by ExecCondition (BUG-102) or an operator `systemctl stop`. Fighting either
            # is exactly the loop that froze the lab Pi.
            if result.stdout.strip() == 'failed':
                return {
                    'category': 'service_down',
                    'severity': 'critical',
                    'description': f'Service {service} is not running',
                    'metrics': json.dumps({'service': service})
                }
        return None

    def _already_open(self, cursor, description):
        """BUG-105 dedup: one open row per symptom. A row the engine retired as 'failed'
        suppresses re-entry for one hour, so a genuinely broken service gets ~3 restart
        attempts per hour instead of 40 per second."""
        cutoff = (datetime.now() - timedelta(hours=1)).isoformat()
        row = cursor.execute('''
            SELECT 1 FROM issues
            WHERE description = ?
              AND (status = 'detected'
                   OR (status = 'failed' AND resolved_at > ?))
            LIMIT 1
        ''', (description, cutoff)).fetchone()
        return row is not None

    def detect_issues(self):
        """Run all detection checks and log issues"""
        checks = [
            self.check_cpu_temp(),
            self.check_memory(),
            self.check_disk_space(),
            self.check_services()
        ]

        detected_issues = [issue for issue in checks if issue]

        # Log to database
        if detected_issues:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            for issue in detected_issues:
                if self._already_open(cursor, issue['description']):
                    continue   # BUG-105: one open row per symptom — never one row per poll
                cursor.execute('''
                    INSERT INTO issues (timestamp, category, severity, description, metrics)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    datetime.now().isoformat(),
                    issue['category'],
                    issue['severity'],
                    issue['description'],
                    issue.get('metrics', '{}')
                ))
            conn.commit()
            conn.close()

        return detected_issues

detector = IssueDetector()

@app.route('/healing/detect', methods=['POST'])
def run_detection():
    """Run issue detection on demand"""
    issues = detector.detect_issues()
    return jsonify({
        'success': True,
        'issues_found': len(issues),
        'issues': issues
    })

@app.route('/healing/issues', methods=['GET'])
def get_issues():
    """Get all unresolved issues"""
    conn = sqlite3.connect(detector.db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, timestamp, category, severity, description, metrics
        FROM issues
        WHERE status = 'detected'
        ORDER BY timestamp DESC
    ''')
    rows = cursor.fetchall()
    conn.close()

    issues = [{
        'id': row[0],
        'timestamp': row[1],
        'category': row[2],
        'severity': row[3],
        'description': row[4],
        'metrics': json.loads(row[5]) if row[5] else {}
    } for row in rows]

    return jsonify({'success': True, 'issues': issues})

@app.route('/healing/status', methods=['GET'])
def get_status():
    """Get detection service status"""
    return jsonify({
        'success': True,
        'service': 'issue_detector',
        'status': 'running'
    })

if __name__ == '__main__':
    # Run continuous detection loop
    import threading

    def detection_loop():
        while True:
            detector.detect_issues()
            time.sleep(60)  # Check every 60 seconds

    # Start background detection
    detection_thread = threading.Thread(target=detection_loop, daemon=True)
    detection_thread.start()

    # Start API
    app.run(host='0.0.0.0', port=8199)
