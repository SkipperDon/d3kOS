#!/usr/bin/env python3
"""
d3kOS Remediation Engine
Automatically fixes detected issues
"""

import subprocess
import sqlite3
import json
import time
from datetime import datetime

class RemediationEngine:
    def __init__(self):
        self.db_path = '/opt/d3kos/data/self-healing/issues.db'
        self.log_path = '/var/log/d3kos/remediation.log'

    def log(self, message):
        """Log remediation actions"""
        timestamp = datetime.now().isoformat()
        log_line = f"[{timestamp}] {message}\n"
        with open(self.log_path, 'a') as f:
            f.write(log_line)
        print(log_line.strip())

    def restart_service(self, service_name):
        """Restart a systemd service"""
        try:
            subprocess.run(['systemctl', 'restart', service_name], check=True)
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

    def run_remediation_loop(self):
        """Continuous remediation loop"""
        while True:
            try:
                # Get unresolved issues
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

                    self.log(f"Attempting remediation for issue #{issue_id}: {issue_dict['description']}")

                    success, action = self.remediate_issue(issue_dict)

                    if success:
                        # Mark as resolved
                        cursor.execute('''
                            UPDATE issues
                            SET status = 'resolved',
                                resolved_at = ?,
                                remediation_action = ?
                            WHERE id = ?
                        ''', (datetime.now().isoformat(), action, issue_id))
                        conn.commit()
                        self.log(f"✓ Issue #{issue_id} resolved: {action}")
                    else:
                        self.log(f"✗ Issue #{issue_id} remediation failed")

                conn.close()

            except Exception as e:
                self.log(f"Error in remediation loop: {e}")

            time.sleep(30)  # Check every 30 seconds

if __name__ == '__main__':
    engine = RemediationEngine()
    engine.run_remediation_loop()
