#!/usr/bin/env python3
"""
d3kOS Alert Watcher — P4 Alert-Triggered Immediate Export + M15 Cloud Notify
Polls the self-healing issues.db every 30 seconds.
When a new CRITICAL or high-priority WARNING alert appears, triggers an
immediate export via export-manager (:8094) rather than waiting for the
next scheduled 30-minute export.

M15 addition: also POSTs the alert to HostPapa alert-notify.php so the
account holder receives an email notification. Fire-and-forget — cloud
notify failure never blocks the export trigger or the poll loop.

Categories that trigger immediate export + email notification:
  - anchor_drag
  - engine_overtemp
  - engine_oil_pressure
  - low_fuel
  - gps_lost
  - collision_risk

All other categories: export on normal schedule, no email.

State: last seen issue ID stored in /opt/d3kos/config/alert-watcher-state.json
Cloud: credentials from /opt/d3kos/config/cloud-config.json
Token: device identity from /opt/d3kos/config/device-token.json

Service: d3kos-alert-watcher
Author:  d3kOS Team
Version: 0.9.5
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
ISSUES_DB          = Path('/opt/d3kos/data/self-healing/issues.db')
STATE_FILE         = Path('/opt/d3kos/config/alert-watcher-state.json')
CLOUD_CONFIG_FILE  = Path('/opt/d3kos/config/cloud-config.json')
DEVICE_TOKEN_FILE  = Path('/opt/d3kos/config/device-token.json')
LOG_FILE           = Path('/opt/d3kos/logs/alert-watcher.log')
EXPORT_URL         = 'http://localhost:8094/export/generate'
POLL_INTERVAL      = 30   # seconds

NOTIFY_PATH = '/wp-content/themes/twentytwenty-child/mobile/alert-notify.php'
NOTIFY_TIMEOUT = 5  # seconds — fire-and-forget, short timeout

# Alert categories that trigger an immediate export AND email notification
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


def load_cloud_config():
    """
    Load cloud-config.json. Returns dict with amboat_api_key and amboat_base_url,
    or None if the file is missing or the key is still a placeholder.
    """
    try:
        with open(CLOUD_CONFIG_FILE) as f:
            cfg = json.load(f)
    except FileNotFoundError:
        logger.warning(f'cloud-config.json not found at {CLOUD_CONFIG_FILE} — cloud notify disabled')
        return None
    except Exception as e:
        logger.warning(f'Failed to parse cloud-config.json: {e} — cloud notify disabled')
        return None

    api_key = cfg.get('amboat_api_key', '')
    if not api_key or api_key == 'YOUR_32_CHAR_HEX_KEY_HERE':
        logger.warning('amboat_api_key not set in cloud-config.json — cloud notify disabled')
        return None

    return cfg


def get_device_token():
    """Return device token UUID from device-token.json, or None if unavailable."""
    try:
        if DEVICE_TOKEN_FILE.exists():
            with open(DEVICE_TOKEN_FILE) as f:
                data = json.load(f)
            token = data.get('device_token')
            if token:
                return token
    except Exception as e:
        logger.warning(f'Failed to read device-token.json: {e}')
    return None


def notify_cloud_alert(base_url, api_key, device_token, alert_type, severity, message, timestamp):
    """
    POST alert to HostPapa alert-notify.php. Fire-and-forget — returns True/False
    for logging only; caller never blocks on failure.

    Server-side rate limiting (15 min per type per device) prevents email floods.
    Quiet hours and per-type toggles are also enforced server-side.
    """
    url = base_url.rstrip('/') + NOTIFY_PATH
    headers = {
        'Authorization':  f'Bearer {api_key}',
        'X-Device-Token': device_token,
        'Content-Type':   'application/json',
    }
    payload = {
        'alert_type': alert_type,
        'severity':   severity,
        'message':    message,
        'timestamp':  timestamp,
    }
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=NOTIFY_TIMEOUT)
        if r.status_code == 200:
            data = r.json()
            emailed = data.get('data', {}).get('emailed', False)
            reason  = data.get('data', {}).get('reason', 'unknown')
            logger.info(
                f'Cloud notify [{alert_type}/{severity}]: '
                f'emailed={emailed} reason={reason}'
            )
            return True
        else:
            logger.warning(
                f'Cloud notify [{alert_type}] HTTP {r.status_code}: {r.text[:120]}'
            )
            return False
    except requests.exceptions.Timeout:
        logger.warning(f'Cloud notify [{alert_type}] timed out after {NOTIFY_TIMEOUT}s — continuing')
        return False
    except Exception as e:
        logger.warning(f'Cloud notify [{alert_type}] error: {e} — continuing')
        return False


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
    Returns (new_last_id, should_export_now, trigger_reason, notify_queue).

    notify_queue is a list of dicts for alerts that should trigger an email:
      [{'alert_type', 'severity', 'message', 'timestamp'}, ...]
    Server-side rate limiting handles dedup — we send all qualifying alerts.
    """
    if not ISSUES_DB.exists():
        return last_id, False, None, []

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
            return last_id, False, None, []

        new_last_id    = rows[-1]['id']
        should_export  = False
        trigger_reason = None
        notify_queue   = []

        for row in rows:
            severity = (row['severity']    or '').lower()
            category = (row['category']    or '').lower()
            status   = (row['status']      or '').lower()
            desc     = (row['description'] or '').strip()
            ts       = (row['timestamp']   or datetime.utcnow().isoformat())

            if status == 'resolved':
                continue

            # Critical alerts: trigger export + notify
            if severity == 'critical':
                if not should_export:
                    should_export  = True
                    trigger_reason = f"critical alert id={row['id']} category={category}"
                notify_queue.append({
                    'alert_type': category,
                    'severity':   severity,
                    'message':    desc or f"Critical alert: {category}",
                    'timestamp':  ts,
                })
                continue

            # High-priority warning categories: trigger export + notify
            if severity == 'warning' and category in IMMEDIATE_EXPORT_CATEGORIES:
                if not should_export:
                    should_export  = True
                    trigger_reason = f"priority warning id={row['id']} category={category}"
                notify_queue.append({
                    'alert_type': category,
                    'severity':   severity,
                    'message':    desc or f"Warning: {category}",
                    'timestamp':  ts,
                })

        return new_last_id, should_export, trigger_reason, notify_queue

    except Exception as e:
        logger.error(f'DB read error: {e}')
        return last_id, False, None, []


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
    logger.info('d3kOS Alert Watcher starting (v0.9.5)')
    last_id = load_state()
    logger.info(f'Resuming from issue_id={last_id}')

    # Load cloud credentials once at startup (re-read on None to handle late config)
    cloud_cfg    = load_cloud_config()
    device_token = get_device_token()
    if cloud_cfg and device_token:
        logger.info('Cloud notify: enabled')
    else:
        logger.info('Cloud notify: disabled (missing cloud-config.json or device-token.json)')

    # Cooldown: minimum seconds between consecutive export triggers
    # Prevents storm of exports if many alerts fire at once
    last_export_time = 0
    export_cooldown  = 120  # 2 minutes

    while True:
        try:
            new_last_id, should_export, reason, notify_queue = check_new_critical_alerts(last_id)

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

            # ── Cloud notify — fire-and-forget for each qualifying alert ──────
            if notify_queue:
                # Retry cloud config load if it was unavailable at startup
                if not cloud_cfg:
                    cloud_cfg    = load_cloud_config()
                    device_token = get_device_token()

                if cloud_cfg and device_token:
                    base_url = cloud_cfg.get('amboat_base_url', 'https://atmyboat.com').rstrip('/')
                    api_key  = cloud_cfg.get('amboat_api_key', '')
                    for alert in notify_queue:
                        notify_cloud_alert(
                            base_url, api_key, device_token,
                            alert['alert_type'],
                            alert['severity'],
                            alert['message'],
                            alert['timestamp'],
                        )

        except Exception as e:
            logger.error(f'Watcher loop error: {e}')

        time.sleep(POLL_INTERVAL)


if __name__ == '__main__':
    run()
