#!/usr/bin/env python3
"""
d3kOS Cloud Command Agent (v0.9.4 S1)
Polls AtMyBoat.com command queue every 30s, executes commands, writes results back.

Commands handled in S1:
  ping        - Respond with current version + timestamp. Confirms agent is alive.
  export_now  - Trigger immediate export via export-manager POST to :8094.
  tier_change - Read new tier from payload, update license.json.

Commands deferred to later sessions:
  fix_my_pi   - S4
  ota_upgrade - S3

Config:  /opt/d3kos/config/cloud-config.json  (amboat_api_key, amboat_base_url)
Token:   /opt/d3kos/config/device-token.json  (created on first run if absent)
License: /opt/d3kos/config/license.json       (installation_id, tier)
Log:     /opt/d3kos/logs/cloud-agent.log      (rotating, max 5MB × 3 files)

Service: d3kos-cloud-agent
Author:  d3kOS Team
Version: 0.9.4-S1
"""

import json
import os
import time
import uuid
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

import requests

# ── Paths ────────────────────────────────────────────────────────────────────
CLOUD_CONFIG_FILE  = Path('/opt/d3kos/config/cloud-config.json')
LICENSE_FILE       = Path('/opt/d3kos/config/license.json')
DEVICE_TOKEN_FILE  = Path('/opt/d3kos/config/device-token.json')
VERSION_FILE       = Path('/opt/d3kos/config/version.txt')
LOG_DIR            = Path('/opt/d3kos/logs')
LOG_FILE           = str(LOG_DIR / 'cloud-agent.log')

# ── Logging ──────────────────────────────────────────────────────────────────
LOG_DIR.mkdir(parents=True, exist_ok=True)
logger = logging.getLogger('cloud-agent')
logger.setLevel(logging.INFO)
_handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3)
_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(_handler)


# ── Config helpers ────────────────────────────────────────────────────────────

def load_cloud_config():
    """Load cloud-config.json. Returns None if missing or placeholder key not set."""
    try:
        with open(CLOUD_CONFIG_FILE) as f:
            cfg = json.load(f)
    except FileNotFoundError:
        logger.error(
            f"cloud-config.json not found at {CLOUD_CONFIG_FILE}. "
            "Copy deployment/v0.9.4/pi_source/cloud-config.json to "
            "/opt/d3kos/config/cloud-config.json and fill in amboat_api_key."
        )
        return None
    except Exception as e:
        logger.error(f"Failed to parse cloud-config.json: {e}")
        return None

    api_key = cfg.get('amboat_api_key', '')
    if not api_key or api_key == 'YOUR_32_CHAR_HEX_KEY_HERE':
        logger.error(
            "amboat_api_key not set in cloud-config.json. "
            "Set it to the same value as AMBOAT_API_KEY in mobile/config.php on AtMyBoat.com staging."
        )
        return None

    return cfg


def get_device_token():
    """Return device token UUID. Creates device-token.json on first run."""
    if DEVICE_TOKEN_FILE.exists():
        try:
            with open(DEVICE_TOKEN_FILE) as f:
                data = json.load(f)
            token = data.get('device_token')
            if token:
                return token
        except Exception as e:
            logger.error(f"Failed to read device-token.json: {e}")

    # Generate new UUID and persist
    token = str(uuid.uuid4())
    try:
        with open(DEVICE_TOKEN_FILE, 'w') as f:
            json.dump({
                'device_token': token,
                'created_at': datetime.utcnow().isoformat() + 'Z'
            }, f, indent=2)
        logger.info(f"Generated new device token: {token}")
        logger.info(
            "OPERATOR ACTION REQUIRED: Register this device token in AtMyBoat.com staging. "
            "In phpMyAdmin → atmyb197_WP302 → wp_usermeta: "
            f"INSERT a row for the d3kos test user with meta_key='atmyboat_device_token' "
            f"and meta_value='{token}'"
        )
    except Exception as e:
        logger.error(f"Failed to write device-token.json: {e}")

    return token


def get_version():
    """Read version string from version.txt."""
    try:
        for line in VERSION_FILE.read_text().strip().split('\n'):
            if line.strip().startswith('d3kOS Version'):
                return line.replace('d3kOS Version', '').strip()
    except Exception:
        pass
    return 'unknown'


def make_headers(api_key, device_token):
    return {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}',
        'X-Device-Token': device_token,
    }


# ── Command queue ─────────────────────────────────────────────────────────────

def poll_commands(base_url, api_key, device_token):
    """Fetch pending commands from command-queue.php. Returns list (may be empty)."""
    url = f"{base_url}/wp-content/themes/twentytwenty-child/mobile/command-queue.php"
    try:
        r = requests.get(url, headers=make_headers(api_key, device_token), timeout=15)
        if r.status_code == 200:
            body = r.json()
            if body.get('success'):
                return body.get('data', {}).get('commands', [])
            else:
                logger.warning(f"Command queue returned: {body.get('error')}")
        else:
            logger.warning(f"Command queue HTTP {r.status_code}: {r.text[:100]}")
    except requests.exceptions.ConnectionError:
        logger.debug("Command queue unreachable (no network or Pi offline)")
    except Exception as e:
        logger.error(f"Poll error: {e}")
    return []


def ack_command(base_url, api_key, device_token, cmd_id, status, result=None):
    """ACK a command as 'completed' or 'failed', with optional result payload."""
    url = f"{base_url}/wp-content/themes/twentytwenty-child/mobile/command-queue.php"
    body = {'ack_id': cmd_id, 'status': status}
    if result is not None:
        body['result'] = result
    try:
        r = requests.post(url, json=body, headers=make_headers(api_key, device_token), timeout=15)
        if r.status_code == 200:
            logger.info(f"ACK cmd {cmd_id}: {status}")
        else:
            logger.warning(f"ACK HTTP {r.status_code}: {r.text[:100]}")
    except Exception as e:
        logger.error(f"Failed to ACK command {cmd_id}: {e}")


# ── Command handlers ──────────────────────────────────────────────────────────

def handle_ping(cmd_id, base_url, api_key, device_token):
    """Respond with current version + timestamp. Confirms agent is alive."""
    version = get_version()
    result = {
        'version': version,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'agent': 'd3kos-cloud-agent',
    }
    ack_command(base_url, api_key, device_token, cmd_id, 'completed', result)
    logger.info(f"ping response: version={version}")


def handle_export_now(cmd_id, base_url, api_key, device_token):
    """Trigger immediate export via export-manager at :8094."""
    try:
        r = requests.post('http://localhost:8094/export/generate', timeout=60)
        if r.status_code == 200:
            data = r.json()
            result = {
                'export_file':    data.get('export_file'),
                'queue_id':       data.get('queue_id'),
                'category_count': data.get('category_count'),
            }
            ack_command(base_url, api_key, device_token, cmd_id, 'completed', result)
            logger.info(f"export_now: triggered {data.get('export_file')}")
        else:
            error = f"export-manager HTTP {r.status_code}: {r.text[:100]}"
            ack_command(base_url, api_key, device_token, cmd_id, 'failed', {'error': error})
            logger.error(f"export_now failed: {error}")
    except Exception as e:
        ack_command(base_url, api_key, device_token, cmd_id, 'failed', {'error': str(e)})
        logger.error(f"export_now exception: {e}")


def handle_tier_change(cmd_id, payload, base_url, api_key, device_token):
    """Update tier in license.json from command payload."""
    try:
        new_tier = payload.get('tier')
        if new_tier is None:
            raise ValueError("payload missing 'tier' field")

        with open(LICENSE_FILE) as f:
            license_data = json.load(f)

        old_tier = license_data.get('tier')
        license_data['tier'] = int(new_tier)

        with open(LICENSE_FILE, 'w') as f:
            json.dump(license_data, f, indent=2)

        result = {'old_tier': old_tier, 'new_tier': int(new_tier)}
        ack_command(base_url, api_key, device_token, cmd_id, 'completed', result)
        logger.info(f"tier_change: {old_tier} → {new_tier}")

    except Exception as e:
        ack_command(base_url, api_key, device_token, cmd_id, 'failed', {'error': str(e)})
        logger.error(f"tier_change exception: {e}")


def dispatch(cmd, base_url, api_key, device_token):
    """Dispatch a single command to its handler."""
    cmd_id   = cmd.get('id')
    command  = cmd.get('command', '')
    payload  = cmd.get('payload', {})

    logger.info(f"Received command: {command} (id={cmd_id})")

    if command == 'ping':
        handle_ping(cmd_id, base_url, api_key, device_token)

    elif command == 'export_now':
        handle_export_now(cmd_id, base_url, api_key, device_token)

    elif command == 'tier_change':
        handle_tier_change(cmd_id, payload, base_url, api_key, device_token)

    elif command in ('fix_my_pi', 'ota_upgrade'):
        # Deferred: fix_my_pi → S4, ota_upgrade → S3
        ack_command(base_url, api_key, device_token, cmd_id, 'failed',
                    {'error': f'Command {command} not yet implemented (deferred to future session)'})
        logger.info(f"Deferred command received and rejected: {command}")

    else:
        ack_command(base_url, api_key, device_token, cmd_id, 'failed',
                    {'error': f'Unknown command: {command}'})
        logger.warning(f"Unknown command: {command}")


# ── Main loop ─────────────────────────────────────────────────────────────────

def run():
    logger.info("d3kOS Cloud Agent starting (v0.9.4 S1)")

    # Config load with retry on missing/invalid config
    while True:
        config = load_cloud_config()
        if config:
            break
        logger.info("Retrying config load in 60s...")
        time.sleep(60)

    api_key       = config['amboat_api_key']
    base_url      = config.get('amboat_base_url', 'https://atmyboat.com/staging').rstrip('/')
    poll_interval = int(config.get('poll_interval_seconds', 30))

    device_token = get_device_token()
    if not device_token:
        logger.error("Cannot get device token. Exiting.")
        return

    logger.info(
        f"Config loaded. Base URL: {base_url} | "
        f"Poll interval: {poll_interval}s | "
        f"Device token: {device_token[:8]}..."
    )

    while True:
        try:
            commands = poll_commands(base_url, api_key, device_token)
            for cmd in commands:
                dispatch(cmd, base_url, api_key, device_token)
        except Exception as e:
            logger.error(f"Main loop error: {e}")

        time.sleep(poll_interval)


if __name__ == '__main__':
    run()
