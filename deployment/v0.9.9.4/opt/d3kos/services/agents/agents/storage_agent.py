#!/usr/bin/env python3
"""
d3kOS Autonomous Agent AA4 — Storage Manager
v0.9.8

Runs every 24h (or on first boot if overdue).

Actions:
  1. Trim log files > 50MB — keep the most recent 50MB of each log
  2. Clean old update backups — keep last MAX_BACKUPS sets
  3. Predictive disk warning — estimate days until full from last two readings

No files are deleted without being oversized/old. Never deletes:
  - /opt/d3kos/config/
  - /opt/d3kos/data/
  - Any file outside /opt/d3kos/logs/ or /opt/d3kos/backups/
"""

import json
import logging
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from agent_base import AgentBase, AgentResult, STATE_DB

log = logging.getLogger('storage_agent')

# ── Config ────────────────────────────────────────────────────────────────────

LOG_DIR        = Path('/opt/d3kos/logs')
BACKUP_DIR     = Path('/opt/d3kos/backups')
MAX_LOG_BYTES  = 50 * 1024 * 1024    # 50 MB per log file
MAX_BACKUPS    = 3                    # keep last N update backup sets
WARN_DAYS      = 7                    # warn if disk full in < 7 days


class StorageAgent(AgentBase):
    name             = 'storage'
    label            = 'Storage Manager'
    interval_seconds = 86400   # daily

    def run(self) -> AgentResult:
        issues   = []
        trimmed  = self._trim_logs()
        cleaned  = self._clean_old_backups()
        days_left = self._predict_disk_full()

        if days_left is not None and days_left < WARN_DAYS:
            issues.append(f'Disk full in ~{days_left:.0f} days')
            log.warning('Disk full predicted in %.0f days', days_left)

        disk = shutil.disk_usage('/')
        disk_pct = round(disk.used / disk.total * 100, 1)
        free_gb  = round(disk.free / (1024 ** 3), 1)

        if issues:
            return AgentResult('yellow', issues[0],
                               details={'disk_pct': disk_pct, 'free_gb': free_gb,
                                        'trimmed_files': trimmed, 'cleaned_backups': cleaned})

        msg = f'Disk {disk_pct}% \u00b7 {free_gb}GB free'
        if trimmed:
            msg += f' \u00b7 trimmed {trimmed} log(s)'
        return AgentResult('green', msg,
                           details={'disk_pct': disk_pct, 'free_gb': free_gb,
                                    'trimmed_files': trimmed, 'cleaned_backups': cleaned})

    # ── Log trimming ──────────────────────────────────────────────────────────

    def _trim_logs(self) -> int:
        """
        For each .log file > MAX_LOG_BYTES, keep only the last MAX_LOG_BYTES.
        Avoids deleting files — truncates in-place by rewriting tail.
        Returns count of files trimmed.
        """
        trimmed = 0
        if not LOG_DIR.exists():
            return 0

        for log_file in LOG_DIR.glob('*.log'):
            try:
                size = log_file.stat().st_size
                if size <= MAX_LOG_BYTES:
                    continue

                # Read last MAX_LOG_BYTES
                with open(log_file, 'rb') as f:
                    f.seek(-MAX_LOG_BYTES, 2)
                    # Skip to next newline so we don't start mid-line
                    f.readline()
                    tail = f.read()

                # Rewrite file with tail only
                log_file.write_bytes(tail)
                trimmed += 1
                log.info('Trimmed %s: %.1fMB → 50MB', log_file.name, size / (1024*1024))

            except Exception as e:
                log.warning('Could not trim %s: %s', log_file.name, e)

        return trimmed

    # ── Backup cleanup ────────────────────────────────────────────────────────

    def _clean_old_backups(self) -> int:
        """
        Keep the MAX_BACKUPS most recent pre-vX.X.X backup sets.
        Delete older ones. Returns count of sets deleted.
        """
        if not BACKUP_DIR.exists():
            return 0

        backup_sets = sorted(
            [d for d in BACKUP_DIR.iterdir() if d.is_dir() and d.name.startswith('pre-v')],
            key=lambda d: d.stat().st_mtime
        )

        to_delete = backup_sets[:-MAX_BACKUPS] if len(backup_sets) > MAX_BACKUPS else []
        for old_set in to_delete:
            try:
                shutil.rmtree(old_set)
                log.info('Removed old backup set: %s', old_set.name)
            except Exception as e:
                log.warning('Could not remove backup set %s: %s', old_set.name, e)

        return len(to_delete)

    # ── Predictive disk warning ───────────────────────────────────────────────

    def _predict_disk_full(self):
        """
        Compare current disk usage to last recorded usage stored in agent_state.db details.
        Returns estimated days until disk full, or None if insufficient data.
        """
        try:
            import sqlite3
            current_used = shutil.disk_usage('/').used
            total        = shutil.disk_usage('/').total
            now          = time.time()

            conn = sqlite3.connect(STATE_DB)
            row  = conn.execute(
                "SELECT last_run_ts, last_message FROM agent_runs WHERE name = 'storage'"
            ).fetchone()
            conn.close()

            if not row or not row[0]:
                return None   # no previous reading

            prev_ts  = row[0]
            elapsed  = now - prev_ts
            if elapsed < 3600:
                return None   # too soon for a meaningful rate

            # Try to read previous disk_used from details stored in history
            conn = sqlite3.connect(STATE_DB)
            hist = conn.execute(
                "SELECT message FROM agent_history WHERE name='storage' ORDER BY ts DESC LIMIT 5"
            ).fetchall()
            conn.close()

            # Parse disk_pct from previous message e.g. "Disk 22.1% · 99.5GB free"
            prev_pct = None
            for h_row in hist[1:]:   # skip most recent (that's current run's previous)
                msg = h_row[0] or ''
                if 'Disk ' in msg and '%' in msg:
                    try:
                        prev_pct = float(msg.split('Disk ')[1].split('%')[0])
                        break
                    except Exception:
                        pass

            if prev_pct is None:
                return None

            current_pct  = round(current_used / total * 100, 1)
            pct_per_day  = (current_pct - prev_pct) / (elapsed / 86400)

            if pct_per_day <= 0:
                return None   # disk shrinking or stable — no warning

            days_left = (100 - current_pct) / pct_per_day
            return days_left

        except Exception as e:
            log.debug('Predict disk full error (non-critical): %s', e)
            return None
