#!/usr/bin/env python3
"""
d3kOS Remediation Engine
Automatically fixes detected issues
"""

import os
import subprocess
import sqlite3
import json
import sys
import time
from datetime import datetime

# BUG-105 brakes. The env overrides exist ONLY so verify-bug105.sh can run the engine
# against a scratch DB/log. Production units set neither.
DB_PATH_DEFAULT  = '/opt/d3kos/data/self-healing/issues.db'
LOG_PATH_DEFAULT = '/var/log/d3kos/remediation.log'
MAX_ATTEMPTS     = 3                  # per issue row; then status='failed' (terminal)
LOG_ROTATE_BYTES = 20 * 1024 * 1024   # remediation.log reached 2.6 GB unrotated (S148)
CYCLE_SECONDS    = 30

class RemediationEngine:
    def __init__(self):
        self.db_path = os.environ.get('D3KOS_ISSUES_DB', DB_PATH_DEFAULT)
        self.log_path = os.environ.get('D3KOS_REMEDIATION_LOG', LOG_PATH_DEFAULT)
        self.attempts = {}   # issue_id -> failed attempts (in-memory; resets with the process — intended)

    def log(self, message):
        """Log remediation actions"""
        timestamp = datetime.now().isoformat()
        log_line = f"[{timestamp}] {message}\n"
        try:
            if os.path.exists(self.log_path) and os.path.getsize(self.log_path) > LOG_ROTATE_BYTES:
                os.replace(self.log_path, self.log_path + '.1')   # one generation kept, then overwritten
        except OSError:
            pass
        with open(self.log_path, 'a') as f:
            f.write(log_line)
        print(log_line.strip())

    def restart_service(self, service_name):
        """Restart a systemd service — only if systemd says it is 'failed' (BUG-105)."""
        state = subprocess.run(['systemctl', 'is-active', service_name],
                               capture_output=True, text=True).stdout.strip()
        if state != 'failed':
            # active     = nothing to do (S148: 218 restarts of a HEALTHY license-api killed it)
            # inactive   = clean stop: tier-gated ExecCondition skip or operator `systemctl stop`
            # activating = already starting. None of these are ours to touch.
            self.log(f"• {service_name} is '{state}' — no restart issued")
            return True
        try:
            subprocess.run(['systemctl', 'restart', service_name], check=True,
                           capture_output=True, text=True)
            self.log(f"✓ Restarted service: {service_name}")
            return True
        except Exception as e:
            self.log(f"✗ Failed to restart {service_name}: {e}")
            return False

    def clear_temp_files(self):
        """Clear temporary files to free disk space"""
        try:
            subprocess.run(['find', '/tmp', '-type', 'f', '-atime', '+7', '-delete'], check=True)
            subprocess.run(['journalctl', '--vacuum-size=100M'], check=True)
            self.log(f"✓ Cleared temporary files and old logs")
            return True
        except Exception as e:
            self.log(f"✗ Failed to clear temp files: {e}")
            return False

    def remediate_issue(self, issue):
        """Apply remediation based on issue category"""
        category = issue['category']
        metrics = json.loads(issue['metrics']) if issue['metrics'] else {}

        action_taken = None
        success = False

        if category == 'service_down':
            service = metrics.get('service')
            if service:
                success = self.restart_service(service)
                action_taken = f"Restarted service {service}"

        elif category == 'disk_space':
            success = self.clear_temp_files()
            action_taken = "Cleared temporary files"

        elif category == 'cpu_temperature':
            # Log warning, no auto-remediation for hardware issues
            self.log(f"⚠ High CPU temperature detected: {metrics.get('temp')}°C - manual intervention may be needed")
            action_taken = "Logged warning - manual check recommended"
            success = True  # Not a failure, just informational

        elif category == 'memory':
            # Restart non-critical services to free memory
            self.log("⚠ High memory usage - consider manual intervention")
            action_taken = "Logged warning"
            success = True

        return success, action_taken

    def run_cycle(self):
        """One pass over open issues.
        BUG-105 brakes: at most ONE systemctl action per service per pass, and a row that
        fails MAX_ATTEMPTS times is retired as status='failed' instead of retried forever."""
        decided = {}   # service_name -> success bool, shared by rows naming the same service this pass
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, category, severity, description, metrics
            FROM issues
            WHERE status = 'detected'
            ORDER BY severity DESC, timestamp ASC
        ''')
        issues = cursor.fetchall()

        for issue in issues:
            issue_id = issue[0]
            issue_dict = {
                'id': issue_id,
                'category': issue[1],
                'severity': issue[2],
                'description': issue[3],
                'metrics': issue[4]
            }
            metrics = json.loads(issue_dict['metrics']) if issue_dict['metrics'] else {}
            service = metrics.get('service') if issue_dict['category'] == 'service_down' else None

            if service and service in decided:
                success, action = decided[service], f"Restarted service {service} (same pass)"
            else:
                self.log(f"Attempting remediation for issue #{issue_id}: {issue_dict['description']}")
                success, action = self.remediate_issue(issue_dict)
                if service:
                    decided[service] = success

            if success:
                cursor.execute('''
                    UPDATE issues
                    SET status = 'resolved',
                        resolved_at = ?,
                        remediation_action = ?
                    WHERE id = ?
                ''', (datetime.now().isoformat(), action, issue_id))
                self.log(f"✓ Issue #{issue_id} resolved: {action}")
            else:
                self.attempts[issue_id] = self.attempts.get(issue_id, 0) + 1
                if self.attempts[issue_id] >= MAX_ATTEMPTS:
                    cursor.execute('''
                        UPDATE issues
                        SET status = 'failed',
                            resolved_at = ?,
                            remediation_action = ?
                        WHERE id = ?
                    ''', (datetime.now().isoformat(),
                          f"gave up after {MAX_ATTEMPTS} attempts", issue_id))
                    self.log(f"✗ Issue #{issue_id} retired as failed after {MAX_ATTEMPTS} attempts")
                else:
                    self.log(f"✗ Issue #{issue_id} remediation failed "
                             f"({self.attempts[issue_id]}/{MAX_ATTEMPTS})")
            conn.commit()

        conn.close()
        return len(issues)

    def run_remediation_loop(self):
        """Continuous remediation loop"""
        while True:
            try:
                self.run_cycle()
            except Exception as e:
                self.log(f"Error in remediation loop: {e}")
            time.sleep(CYCLE_SECONDS)

if __name__ == '__main__':
    engine = RemediationEngine()
    if '--once' in sys.argv:          # test harness: one pass, then exit
        engine.run_cycle()
        sys.exit(0)
    engine.run_remediation_loop()
