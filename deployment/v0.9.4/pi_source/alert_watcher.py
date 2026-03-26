#!/usr/bin/env python3
"""
d3kOS Alert Watcher — P4 Alert-Triggered Immediate Export
Polls the self-healing issues.db every 30 seconds.
When a new CRITICAL or high-priority WARNING alert appears, triggers an
immediate export via export-manager (:8094) rather than waiting for the
next scheduled 30-minute export.

Categories that trigger immediate export:
  - anchor_drag
  - engine_overtemp
  - engine_oil_pressure
  - low_fuel
  - gps_lost
  - collision_risk

All other categories: export on normal schedule.

State: last seen issue ID stored in /opt/d3kos/config/alert-watcher-state.json

Service: d3kos-alert-watcher
Author:  d3kOS Team
Version: 0.9.4
"""

import json
import sqlite3
import time
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

import requests

# ── Config ────────────────────────────────────────────────────────────────────
ISSUES_DB     = Path('/opt/d3kos/data/self-healing/issues.db')
STATE_FILE    = Path('/opt/d3kos/config/alert-watcher-state.json')
LOG_FILE      = Path('/opt/d3kos/logs/alert-watcher.log')
EXPORT_URL    = 'http://localhost:8094/export/generate'
POLL_INTERVAL = 30   # seconds

# Alert categories that trigger an immediate export
IMMEDIATE_EXPORT_CATEGORIES = {
    'anchor_drag',
    'engine_overtemp',
    'engine_oil_pressure',
    'low_fuel',
    'gps_lost',
    'collision_risk',
}

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logger = logging.getLogger('alert-watcher')
logger.setLevel(logging.INFO)
_h = RotatingFileHandler(str(LOG_FILE), maxBytes=2 * 1024 * 1024, backupCount=2)
_h.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(_h)


def load_state():
    """Load last seen issue ID from state file."""
    try:
        if STATE_FILE.exists():
            with open(STATE_FILE) as f:
                return json.load(f).get('last_issue_id', 0)
    except Exception:
        pass
    return 0


def save_state(last_issue_id):
    """Persist last seen issue ID."""
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump({'last_issue_id': last_issue_id, 'updated_at': datetime.utcnow().isoformat()}, f)
    except Exception as e:
        logger.warning(f'Failed to save state: {e}')


def check_new_critical_alerts(last_id):
    """
    Check issues.db for new alerts since last_id.
    Returns (new_last_id, should_export_now, trigger_reason).
    """
    if not ISSUES_DB.exists():
        return last_id, False, None

    try:
        conn = sqlite3.connect(str(ISSUES_DB))
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("""
            SELECT id, category, severity, description, timestamp, status
            FROM issues
            WHERE id > ?
            ORDER BY id ASC
        """, (last_id,))

        rows = cur.fetchall()
        conn.close()

        if not rows:
            return last_id, False, None

        new_last_id = rows[-1]['id']
        should_export = False
        trigger_reason = None

        for row in rows:
            severity = (row['severity'] or '').lower()
            category = (row['category'] or '').lower()
            status   = (row['status']   or '').lower()

            if status == 'resolved':
                continue

            # Critical alerts always trigger export
            if severity == 'critical':
                should_export = True
                trigger_reason = f"critical alert id={row['id']} category={category}"
                break

            # High-priority warning categories also trigger export
            if severity == 'warning' and category in IMMEDIATE_EXPORT_CATEGORIES:
                should_export = True
                trigger_reason = f"priority warning id={row['id']} category={category}"
                break

        return new_last_id, should_export, trigger_reason

    except Exception as e:
        logger.error(f'DB read error: {e}')
        return last_id, False, None


def trigger_export(reason):
    """POST to export-manager to generate and upload an immediate export."""
    try:
        r = requests.post(EXPORT_URL, timeout=60)
        if r.status_code == 200:
            data = r.json()
            logger.info(
                f'Immediate export triggered by [{reason}] — '
                f'file={data.get("export_file")} queue_id={data.get("queue_id")}'
            )
            return True
        else:
            logger.warning(
                f'Export trigger failed (HTTP {r.status_code}) for [{reason}]: {r.text[:100]}'
            )
            return False
    except Exception as e:
        logger.error(f'Export trigger exception for [{reason}]: {e}')
        return False


def run():
    logger.info('d3kOS Alert Watcher starting (v0.9.4)')
    last_id = load_state()
    logger.info(f'Resuming from issue_id={last_id}')

    # Cooldown: minimum seconds between consecutive export triggers
    # Prevents storm of exports if many alerts fire at once
    last_export_time = 0
    export_cooldown  = 120  # 2 minutes

    while True:
        try:
            new_last_id, should_export, reason = check_new_critical_alerts(last_id)

            if new_last_id != last_id:
                logger.debug(f'New alerts: id {last_id} → {new_last_id}')
                last_id = new_last_id
                save_state(last_id)

            if should_export:
                now = time.monotonic()
                if now - last_export_time >= export_cooldown:
                    success = trigger_export(reason)
                    if success:
                        last_export_time = now
                else:
                    remaining = int(export_cooldown - (now - last_export_time))
                    logger.info(
                        f'Export cooldown active ({remaining}s remaining) — '
                        f'skipping trigger for [{reason}]'
                    )

        except Exception as e:
            logger.error(f'Watcher loop error: {e}')

        time.sleep(POLL_INTERVAL)


if __name__ == '__main__':
    run()
