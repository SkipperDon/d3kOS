#!/usr/bin/env python3
"""
d3kOS Service Watchdog
Runs every 5 minutes via cron. Checks critical services, restarts on failure.
On persistent failure, POSTs directly to HostPapa watchdog-alert.php which
emails the registered account holder via wp_mail() — no SMTP config on Pi.

Credentials: reads /opt/d3kos/config/cloud-config.json + device-token.json
State:       /opt/d3kos/data/watchdog-state.json  (alert cooldown tracking)
Log:         /opt/d3kos/logs/watchdog.log
"""

import json
import logging
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────

CLOUD_CONFIG_PATH  = Path('/opt/d3kos/config/cloud-config.json')
DEVICE_TOKEN_PATH  = Path('/opt/d3kos/config/device-token.json')
STATE_PATH         = Path('/opt/d3kos/data/watchdog-state.json')
LOG_PATH           = Path('/opt/d3kos/logs/watchdog.log')

# ── Critical services — ordered by importance ─────────────────────────────────
# (service_name, human_label, auto_restart)
# auto_restart=False means alert only, never restart

CRITICAL_SERVICES = [
    ('d3kos-cloud-agent',    'Cloud Command Agent (Fix My Pi / OTA / commands)',  True),
    ('d3kos-tier',           'Tier Service',                                       True),
    ('d3kos-export-manager', 'Export Manager (data sync to cloud)',                True),
    ('d3kos-alert-watcher',  'Alert Watcher',                                      True),
    ('d3kos-live',           'Live Session / WebRTC tunnel',                       True),
    ('d3kos-dashboard',      'Marine Dashboard',                                   True),
    ('d3kos-camera-stream',  'Camera Stream Manager',                               True),
    ('d3kos-ai-api',         'AI API Server',                                       True),
    ('d3kos-health',         'System Health Monitor',                              True),
    ('d3kos-issue-detector', 'Issue Detector / Self-Healing',                      True),
    ('d3kos-ai-bridge',      'AI Bridge (route analysis / anchor watch)',       True),
    ('d3kos-agents',         'Autonomous Agents (AA1-AA6)',                     True),
]

# Don't alert same service twice within this window
COOLDOWN_MINUTES = 30

# ── Logging ───────────────────────────────────────────────────────────────────

logging.basicConfig(
    filename=str(LOG_PATH),
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
log = logging.getLogger('watchdog')


# ── Cloud credentials (read from existing Pi config) ──────────────────────────

def load_cloud_config() -> dict:
    cfg = {}
    if CLOUD_CONFIG_PATH.exists():
        with open(CLOUD_CONFIG_PATH) as f:
            data = json.load(f)
        cfg['api_key']  = data.get('amboat_api_key', '')
        cfg['base_url'] = data.get('amboat_base_url', '').rstrip('/')
    if DEVICE_TOKEN_PATH.exists():
        with open(DEVICE_TOKEN_PATH) as f:
            data = json.load(f)
        cfg['device_token'] = data.get('device_token', '')
    return cfg


# ── Cooldown state ────────────────────────────────────────────────────────────

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
    return datetime.now() - datetime.fromisoformat(last) < timedelta(minutes=COOLDOWN_MINUTES)


def mark_alerted(service: str, state: dict):
    state['last_alerted'][service] = datetime.now().isoformat()


# ── Service checks ────────────────────────────────────────────────────────────

def is_active(service: str) -> bool:
    r = subprocess.run(['systemctl', 'is-active', service], capture_output=True, text=True)
    return r.stdout.strip() == 'active'


def restart_service(service: str) -> bool:
    """Attempt restart. Returns True if service comes up within 8 seconds."""
    log.warning('Restarting %s ...', service)
    subprocess.run(['sudo', 'systemctl', 'restart', service], capture_output=True, text=True)
    time.sleep(8)
    return is_active(service)


# ── Cloud alert — POST to HostPapa, which emails the account holder ───────────

def post_alert_to_cloud(cfg: dict, service: str, label: str, reason: str):
    api_key      = cfg.get('api_key', '')
    device_token = cfg.get('device_token', '')
    base_url     = cfg.get('base_url', '')

    if not api_key or not device_token or not base_url:
        log.error('Cloud config incomplete — cannot post watchdog alert')
        return

    url = f'{base_url}/wp-content/themes/twentytwenty-child/mobile/watchdog-alert.php'

    payload = json.dumps({
        'service':            service,
        'label':              label,
        'reason':             reason,
        'timestamp':          datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        'restart_attempted':  True,
        'cooldown_minutes':   COOLDOWN_MINUTES,
    }).encode('utf-8')

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            'Authorization':  f'Bearer {api_key}',
            'X-Device-Token': device_token,
            'Content-Type':   'application/json',
        },
        method='POST',
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode('utf-8')
            log.info('Alert posted to cloud for %s — response: %s', service, body[:120])
    except urllib.error.HTTPError as e:
        log.error('HTTP error posting alert for %s: %s %s', service, e.code, e.reason)
    except Exception as e:
        log.error('Failed to post alert for %s: %s', service, e)


# ── Main ──────────────────────────────────────────────────────────────────────

def run():
    cfg   = load_cloud_config()
    state = load_state()

    failures  = []
    restarted = []

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

    # Cloud alert for persistent failures (with cooldown)
    for service, label, reason in failures:
        if is_on_cooldown(service, state):
            log.info('Cooldown active for %s — skipping alert', service)
            continue
        post_alert_to_cloud(cfg, service, label, reason)
        mark_alerted(service, state)

    save_state(state)

    if not failures and not restarted:
        log.debug('All %d critical services healthy.', len(CRITICAL_SERVICES))


if __name__ == '__main__':
    run()
