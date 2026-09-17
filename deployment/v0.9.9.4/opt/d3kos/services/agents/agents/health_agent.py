#!/usr/bin/env python3
"""
d3kOS Autonomous Agent AA5 — Health Check
v0.9.8

Runs every 24h. Produces a health score 0-100 and a health report JSON.
Deep scan (DB integrity + filesystem) runs every 7 days.

Health score deductions:
  Service DOWN              : -10 per service
  Disk > 85%                : -15
  Disk > 70%                : -5
  Memory > 90%              : -15
  Memory > 70%              : -5
  SQLite DB corrupted       : -20 per DB
  No internet               : -5
  CRITICAL log entries/24h  : -2 each (max -20)

Score thresholds:
  90-100 : green  (healthy)
  70-89  : yellow (degraded)
  < 70   : red    (unhealthy)

Report written to: /opt/d3kos/data/health-report.json
Read by:           /health/report endpoint in app.py
"""

import json
import logging
import shutil
import socket
import sqlite3
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from agent_base import AgentBase, AgentResult, STATE_DB

log = logging.getLogger('health_agent')

# ── Config ────────────────────────────────────────────────────────────────────

REPORT_FILE  = Path('/opt/d3kos/data/health-report.json')
LOG_DIR      = Path('/opt/d3kos/logs')
DATA_DIR     = Path('/opt/d3kos/data')
DEEP_SCAN_INTERVAL = 7 * 86400   # 7 days

CRITICAL_SERVICES = [
    'd3kos-cloud-agent', 'd3kos-tier', 'd3kos-export-manager',
    'd3kos-alert-watcher', 'd3kos-live', 'd3kos-dashboard',
    'd3kos-camera-stream', 'd3kos-ai-api', 'd3kos-health',
    'd3kos-issue-detector', 'd3kos-ai-bridge', 'd3kos-agents',
]


class HealthAgent(AgentBase):
    name             = 'health'
    label            = 'Health Check'
    interval_seconds = 86400   # 24 hours

    def run(self) -> AgentResult:
        score    = 100
        issues   = []
        details  = {}

        # ── 1. Service health ─────────────────────────────────────────────
        svc_down = self._check_services()
        details['services_down'] = svc_down
        for svc in svc_down:
            score -= 10
            issues.append(f'{svc} DOWN')

        # ── 2. Disk / memory ──────────────────────────────────────────────
        disk_pct = self._disk_pct()
        mem_pct  = self._mem_pct()
        details['disk_pct'] = disk_pct
        details['mem_pct']  = mem_pct

        if disk_pct >= 85:
            score -= 15; issues.append(f'Disk {disk_pct:.0f}% CRITICAL')
        elif disk_pct >= 70:
            score -= 5;  issues.append(f'Disk {disk_pct:.0f}% WARNING')

        if mem_pct >= 90:
            score -= 15; issues.append(f'Memory {mem_pct:.0f}% CRITICAL')
        elif mem_pct >= 70:
            score -= 5;  issues.append(f'Memory {mem_pct:.0f}% WARNING')

        # ── 3. Internet connectivity ──────────────────────────────────────
        has_internet = self._check_internet()
        details['internet'] = has_internet
        if not has_internet:
            score -= 5; issues.append('No internet')

        # ── 4. Log errors in last 24h ─────────────────────────────────────
        error_count = self._count_log_errors()
        details['log_errors_24h'] = error_count
        deduct = min(error_count * 2, 20)
        if deduct:
            score -= deduct
            issues.append(f'{error_count} CRITICAL log entries (24h)')

        # ── 5. Deep scan — DB integrity (every 7 days) ────────────────────
        if self._deep_scan_due():
            db_issues = self._check_db_integrity()
            details['db_integrity'] = db_issues
            for db_name in db_issues:
                score -= 20
                issues.append(f'DB corrupt: {db_name}')
            self._record_deep_scan()
        else:
            details['db_integrity'] = 'skipped (not due)'

        score = max(0, score)
        details['score'] = score
        details['checked'] = datetime.now(tz=timezone.utc).isoformat()
        details['issues']  = issues

        # ── Write report ──────────────────────────────────────────────────
        self._write_report(score, issues, details)

        # ── Result ────────────────────────────────────────────────────────
        if score >= 90:
            status = 'green'
            msg = f'Health {score}/100 \u2014 all systems OK'
        elif score >= 70:
            status = 'yellow'
            msg = f'Health {score}/100 \u2014 {issues[0]}' if issues else f'Health {score}/100'
        else:
            status = 'red'
            msg = f'Health {score}/100 \u2014 {len(issues)} issue(s)'

        log.info('Health check: %d/100 — %d issues', score, len(issues))
        return AgentResult(status=status, message=msg, details=details)

    # ── Checks ────────────────────────────────────────────────────────────────

    def _check_services(self) -> list:
        down = []
        for svc in CRITICAL_SERVICES:
            try:
                r = subprocess.run(['systemctl', 'is-active', svc],
                                   capture_output=True, text=True, timeout=5)
                if r.stdout.strip() != 'active':
                    down.append(svc)
            except Exception:
                down.append(svc)
        return down

    def _disk_pct(self) -> float:
        try:
            u = shutil.disk_usage('/')
            return round(u.used / u.total * 100, 1)
        except Exception:
            return 0.0

    def _mem_pct(self) -> float:
        try:
            mem = {}
            with open('/proc/meminfo') as f:
                for line in f:
                    if line.startswith(('MemTotal:', 'MemAvailable:')):
                        k, v = line.split(':')
                        mem[k.strip()] = int(v.split()[0])
            total = mem.get('MemTotal', 1)
            avail = mem.get('MemAvailable', total)
            return round((total - avail) / total * 100, 1)
        except Exception:
            return 0.0

    def _check_internet(self) -> bool:
        try:
            socket.setdefaulttimeout(5)
            socket.socket().connect(('8.8.8.8', 53))
            return True
        except Exception:
            return False

    def _count_log_errors(self) -> int:
        """Count [ERROR]/[CRITICAL] log lines whose timestamp is within the last 24h."""
        import re as _re
        count = 0
        cutoff = time.time() - 86400
        ts_pat = _re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})')
        if not LOG_DIR.exists():
            return 0
        for log_file in LOG_DIR.glob('*.log'):
            try:
                if log_file.stat().st_mtime < cutoff:
                    continue
                with open(log_file, errors='replace') as f:
                    for line in f:
                        if '[CRITICAL]' not in line and '[ERROR]' not in line:
                            continue
                        m = ts_pat.match(line)
                        if m:
                            try:
                                from datetime import datetime as _dt
                                line_ts = _dt.strptime(m.group(1), '%Y-%m-%d %H:%M:%S').timestamp()
                                if line_ts < cutoff:
                                    continue
                            except ValueError:
                                pass
                        count += 1
            except Exception:
                pass
        return count

    def _check_db_integrity(self) -> list:
        """Run PRAGMA integrity_check on all SQLite DBs. Returns list of corrupt DB names."""
        corrupt = []
        for db_path in DATA_DIR.rglob('*.db'):
            try:
                conn = sqlite3.connect(str(db_path), timeout=10)
                result = conn.execute('PRAGMA integrity_check').fetchone()
                conn.close()
                if result and result[0] != 'ok':
                    corrupt.append(db_path.name)
                    log.error('DB integrity FAILED: %s — %s', db_path.name, result[0])
                else:
                    log.debug('DB OK: %s', db_path.name)
            except Exception as e:
                corrupt.append(db_path.name)
                log.error('DB check failed for %s: %s', db_path.name, e)
        return corrupt

    def _deep_scan_due(self) -> bool:
        try:
            conn = sqlite3.connect(STATE_DB)
            row  = conn.execute(
                "SELECT last_run_ts FROM agent_runs WHERE name='health_deep_scan'"
            ).fetchone()
            conn.close()
            if not row:
                return True
            return (time.time() - row[0]) >= DEEP_SCAN_INTERVAL
        except Exception:
            return True

    def _record_deep_scan(self):
        try:
            conn = sqlite3.connect(STATE_DB)
            conn.execute('''
                INSERT INTO agent_runs (name, last_run_ts, last_status, last_message, run_count)
                VALUES ('health_deep_scan', ?, 'ok', 'deep scan complete', 1)
                ON CONFLICT(name) DO UPDATE SET
                    last_run_ts=excluded.last_run_ts,
                    last_message=excluded.last_message,
                    run_count=run_count+1
            ''', (time.time(),))
            conn.commit()
            conn.close()
        except Exception:
            pass

    # ── Report ────────────────────────────────────────────────────────────────

    def _write_report(self, score: int, issues: list, details: dict):
        REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            'score':   score,
            'status':  'green' if score >= 90 else ('yellow' if score >= 70 else 'red'),
            'issues':  issues,
            'details': details,
            'updated': datetime.now(tz=timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),
        }
        tmp = REPORT_FILE.with_suffix('.tmp')
        tmp.write_text(json.dumps(payload, indent=2))
        tmp.replace(REPORT_FILE)
