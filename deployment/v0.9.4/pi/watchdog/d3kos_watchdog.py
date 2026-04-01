#!/usr/bin/env python3
"""
d3kOS Service Watchdog
Runs every 5 minutes via cron. Checks critical services, restarts on failure,
emails the operator if a restart fails or a service is persistently down.

Config: /opt/d3kos/config/watchdog-config.json
Log:    /opt/d3kos/logs/watchdog.log
State:  /opt/d3kos/data/watchdog-state.json  (email cooldown tracking)
"""

import json
import logging
import smtplib
import subprocess
import sys
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────

CONFIG_PATH = Path('/opt/d3kos/config/watchdog-config.json')
STATE_PATH  = Path('/opt/d3kos/data/watchdog-state.json')
LOG_PATH    = Path('/opt/d3kos/logs/watchdog.log')

# ── Critical services — ordered by importance ─────────────────────────────────
# Format: (service_name, human_label, auto_restart)
# auto_restart=False means alert only — never restart (e.g. one-shot services)

CRITICAL_SERVICES = [
    ('d3kos-cloud-agent',    'Cloud Command Agent (Fix My Pi / OTA / commands)',  True),
    ('d3kos-tier',           'Tier Service (port 8093)',                           True),
    ('d3kos-export-manager', 'Export Manager (data sync to cloud)',                True),
    ('d3kos-alert-watcher',  'Alert Watcher',                                      True),
    ('d3kos-live',           'Live Session / WebRTC tunnel',                       True),
    ('d3kos-dashboard',      'Marine Dashboard (UI)',                               True),
    ('d3kos-camera-stream',  'Camera Stream Manager',                               True),
    ('d3kos-ai-api',         'AI API Server',                                       True),
    ('d3kos-health',         'System Health Monitor',                              True),
    ('d3kos-issue-detector', 'Issue Detector / Self-Healing',                      True),
]

# ── Email cooldown — don't alert same service twice within this window ─────────
COOLDOWN_MINUTES = 30

# ── Logging setup ──────────────────────────────────────────────────────────────

logging.basicConfig(
    filename=str(LOG_PATH),
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
log = logging.getLogger('watchdog')


# ── Config ────────────────────────────────────────────────────────────────────

def load_config() -> dict:
    if not CONFIG_PATH.exists():
        log.error('watchdog-config.json not found at %s', CONFIG_PATH)
        sys.exit(1)
    with open(CONFIG_PATH) as f:
        return json.load(f)


# ── State (email cooldown) ────────────────────────────────────────────────────

def load_state() -> dict:
    if STATE_PATH.exists():
        try:
            with open(STATE_PATH) as f:
                return json.load(f)
        except Exception:
            pass
    return {'last_alerted': {}}


def save_state(state: dict):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_PATH, 'w') as f:
        json.dump(state, f, indent=2)


def is_on_cooldown(service: str, state: dict) -> bool:
    last = state['last_alerted'].get(service)
    if not last:
        return False
    last_dt = datetime.fromisoformat(last)
    return datetime.now() - last_dt < timedelta(minutes=COOLDOWN_MINUTES)


def mark_alerted(service: str, state: dict):
    state['last_alerted'][service] = datetime.now().isoformat()


# ── Service checks ────────────────────────────────────────────────────────────

def is_active(service: str) -> bool:
    result = subprocess.run(
        ['systemctl', 'is-active', service],
        capture_output=True, text=True
    )
    return result.stdout.strip() == 'active'


def restart_service(service: str) -> bool:
    """Attempt restart. Returns True if service comes up within 8 seconds."""
    log.warning('Restarting %s ...', service)
    subprocess.run(['sudo', 'systemctl', 'restart', service],
                   capture_output=True, text=True)
    time.sleep(8)
    return is_active(service)


# ── Email ─────────────────────────────────────────────────────────────────────

def send_alert(cfg: dict, subject: str, body: str):
    email_cfg = cfg.get('email', {})
    smtp_host = email_cfg.get('smtp_host', '')
    smtp_port = int(email_cfg.get('smtp_port', 587))
    smtp_user = email_cfg.get('smtp_user', '')
    smtp_pass = email_cfg.get('smtp_pass', '')
    to_addr   = email_cfg.get('to', smtp_user)

    if not smtp_host or not smtp_user or not smtp_pass:
        log.error('Email not configured — skipping alert: %s', subject)
        return

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From']    = smtp_user
    msg['To']      = to_addr

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as s:
            s.ehlo()
            s.starttls()
            s.login(smtp_user, smtp_pass)
            s.sendmail(smtp_user, [to_addr], msg.as_string())
        log.info('Alert email sent: %s', subject)
    except Exception as e:
        log.error('Failed to send alert email: %s', e)


# ── Main watchdog loop ────────────────────────────────────────────────────────

def run():
    cfg   = load_config()
    state = load_state()
    pi_id = cfg.get('pi_id', 'Pi')

    failures  = []   # services that stayed down after restart
    restarted = []   # services that were down but came back

    for service, label, auto_restart in CRITICAL_SERVICES:
        if is_active(service):
            continue

        log.warning('DOWN: %s (%s)', service, label)

        if not auto_restart:
            failures.append((service, label, 'monitoring only — restart disabled'))
            continue

        came_back = restart_service(service)

        if came_back:
            log.info('RECOVERED: %s came back after restart', service)
            restarted.append((service, label))
        else:
            log.error('PERSISTENT FAILURE: %s did not recover after restart', service)
            failures.append((service, label, 'did not recover after restart attempt'))

    # Email for persistent failures (with cooldown)
    for service, label, reason in failures:
        if is_on_cooldown(service, state):
            log.info('Cooldown active for %s — skipping email', service)
            continue

        subject = f'[d3kOS ALERT] {label} is DOWN on {pi_id}'
        body = (
            f'd3kOS Watchdog Alert\n'
            f'Pi:     {pi_id}\n'
            f'Time:   {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n'
            f'Service FAILED and did not recover:\n'
            f'  {service}\n'
            f'  {label}\n'
            f'  Reason: {reason}\n\n'
            f'Actions already taken:\n'
            f'  - systemctl restart {service} attempted\n'
            f'  - Service still not active after 8 seconds\n\n'
            f'What to do:\n'
            f'  1. SSH to Pi: ssh d3kos@192.168.1.237\n'
            f'  2. Check logs: journalctl -u {service} -n 50 --no-pager\n'
            f'  3. Manual restart: sudo systemctl restart {service}\n\n'
            f'This alert will repeat every {COOLDOWN_MINUTES} minutes until the service recovers.\n'
        )
        send_alert(cfg, subject, body)
        mark_alerted(service, state)

    # Email summary for auto-restarted services (optional — single digest)
    if restarted and cfg.get('email', {}).get('notify_on_restart', False):
        names = ', '.join(s for s, _ in restarted)
        subject = f'[d3kOS INFO] Auto-restarted {len(restarted)} service(s) on {pi_id}'
        body = (
            f'd3kOS Watchdog — Auto-Recovery Notice\n'
            f'Pi:   {pi_id}\n'
            f'Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n'
            f'The following services were down and were automatically restarted:\n'
        )
        for service, label in restarted:
            body += f'  ✓ {service} — {label}\n'
        body += '\nNo action required — all recovered.'
        send_alert(cfg, subject, body)

    save_state(state)

    if not failures and not restarted:
        log.debug('All %d critical services healthy.', len(CRITICAL_SERVICES))


if __name__ == '__main__':
    run()
