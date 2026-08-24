#!/usr/bin/env python3
"""
d3kOS Cloud Command Agent (v0.9.4 S2 / v0.9.7)
Polls AtMyBoat.com command queue every 30s, executes commands, writes results back.

Commands handled:
  ping               - Respond with current version + timestamp. Confirms agent is alive.
  export_now         - Trigger immediate export via export-manager POST to :8094.
  tier_change        - Read new tier from payload, update license.json.
  fix_my_pi          - Run diagnostics + service restarts, report results back.
  ota_upgrade        - Download, verify, install latest release, restart services.
  setup_lockdown     - Apply apt-mark hold on critical packages to prevent OS upgrades breaking d3kOS.
  pair_confirmed     - Pi paired via app. Upgrade tier in license.json, trigger immediate export.
  fleet_assign       - Write /opt/d3kos/config/fleet.json, restart d3kos-fleet-push.service.
  fleet_unassign     - Remove /opt/d3kos/config/fleet.json, stop d3kos-fleet-push.service.
  diagnostic_collect - Collect system logs + config, bundle, upload to HostPapa for ticket.

Config:  /opt/d3kos/config/cloud-config.json  (amboat_api_key, amboat_base_url)
Token:   /opt/d3kos/config/device-token.json  (created on first run if absent)
License: /opt/d3kos/config/license.json       (installation_id, tier)
Log:     /opt/d3kos/logs/cloud-agent.log      (rotating, max 5MB × 3 files)

Service: d3kos-cloud-agent
Author:  d3kOS Team
Version: 0.9.9.3-FI4
"""

import hashlib
import json
import os
import time
import uuid
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

import requests

import sys
sys.path.insert(0, '/opt/d3kos/services')

# ── Paths ────────────────────────────────────────────────────────────────────
CLOUD_CONFIG_FILE  = Path('/opt/d3kos/config/cloud-config.json')
LICENSE_FILE       = Path('/opt/d3kos/config/license.json')
DEVICE_TOKEN_FILE  = Path('/opt/d3kos/config/device-token.json')
VERSION_FILE       = Path('/opt/d3kos/config/version.txt')
LOG_DIR            = Path('/opt/d3kos/logs')
LOG_FILE           = str(LOG_DIR / 'cloud-agent.log')

# ── Config backup (FI4) ───────────────────────────────────────────────────────
CONFIG_DIR           = Path('/opt/d3kos/config')
CONFIG_SNAPSHOT_HASH = Path('/opt/d3kos/config/config-snapshot-hash.txt')

CONFIG_BACKUP_FILES = [
    'cloud-config.json', 'device-token.json', 'license.json',
    'user-preferences.json', 'ai-config.json', 'slots.json',
    'hardware.json', 'fleet.json', 'community-prefs.json',
    'onboarding.json', 'timezone.txt', 'tts-mute.json',
]

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


# ── Config backup (FI4) ───────────────────────────────────────────────────────

def _read_config_files():
    """Read CONFIG_BACKUP_FILES into a dict {filename: text}. Missing files skipped."""
    data = {}
    for name in CONFIG_BACKUP_FILES:
        path = CONFIG_DIR / name
        try:
            data[name] = path.read_text()
        except FileNotFoundError:
            pass  # optional — skip silently
        except Exception as e:
            logger.debug(f'config_snapshot: could not read {name}: {e}')
    return data


def push_config_snapshot(base_url, api_key, device_token):
    """Push config snapshot to HostPapa config-backup.php.
    Skips push if config is unchanged since last successful push (hash check).
    Best-effort — logs on failure, never raises, never blocks command processing."""
    try:
        config_data = _read_config_files()
        if not config_data:
            logger.debug('config_snapshot: no config files readable, skipping')
            return

        config_json = json.dumps(config_data, separators=(',', ':'), sort_keys=True)
        checksum    = hashlib.sha256(config_json.encode()).hexdigest()

        # Skip if config unchanged since last push
        try:
            last_hash = CONFIG_SNAPSHOT_HASH.read_text().strip()
        except FileNotFoundError:
            last_hash = ''

        if checksum == last_hash:
            logger.debug('config_snapshot: unchanged, skipping push')
            return

        url = (f"{base_url}/wp-content/themes/twentytwenty-child"
               "/mobile/config-backup.php")
        body = {
            'config_json': config_json,
            'version':     get_version(),
            'checksum':    checksum,
        }

        r = requests.post(url, json=body,
                          headers=make_headers(api_key, device_token),
                          timeout=20)

        if r.status_code == 200 and r.json().get('success'):
            CONFIG_SNAPSHOT_HASH.write_text(checksum)
            logger.info(f'config_snapshot: pushed (checksum={checksum[:8]}...)')
        else:
            logger.warning(
                f'config_snapshot: push failed HTTP {r.status_code}: '
                f'{r.text[:120]}'
            )

    except requests.exceptions.ConnectionError:
        logger.debug('config_snapshot: offline, skipping push')
    except Exception as e:
        logger.warning(f'config_snapshot: push error (non-fatal): {e}')


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


def handle_fix_my_pi(cmd_id, base_url, api_key, device_token):
    """Run diagnostics and service repairs. Report results back."""
    try:
        # Step 0: push config snapshot before diagnostics — ensures latest state
        # is backed up before any repair actions modify config (FI4)
        push_config_snapshot(base_url, api_key, device_token)

        from fix_my_pi import run_diagnostics
        result = run_diagnostics(base_url)
        status = 'completed' if result.get('ok') else 'failed'
        ack_command(base_url, api_key, device_token, cmd_id, status, result)
        logger.info(
            f"fix_my_pi: ok={result.get('ok')} actions={len(result.get('actions_taken', []))} "
            f"errors={len(result.get('errors', []))}"
        )
    except ImportError:
        err = 'fix_my_pi.py not found at /opt/d3kos/services/fix_my_pi.py'
        ack_command(base_url, api_key, device_token, cmd_id, 'failed', {'error': err})
        logger.error(f"fix_my_pi: {err}")
    except Exception as e:
        ack_command(base_url, api_key, device_token, cmd_id, 'failed', {'error': str(e)})
        logger.error(f"fix_my_pi exception: {e}")


def handle_restart_services(cmd_id, base_url, api_key, device_token):
    """Restart core d3kOS application services (voice, AI, Gemini, predictive)."""
    import subprocess
    SERVICES = [
        'd3kos-voice',
        'd3kos-ai-bridge',
        'd3kos-gemini-proxy',
        'd3kos-predictive',
    ]
    results = []
    for svc in SERVICES:
        try:
            r = subprocess.run(['sudo', 'systemctl', 'restart', svc],
                               capture_output=True, text=True, timeout=30)
            results.append(f"{svc}:{'ok' if r.returncode == 0 else 'err'}")
        except Exception as e:
            results.append(f"{svc}:exc")
            logger.warning(f"restart_services: {svc} exception: {e}")
    summary = ', '.join(results)
    ack_command(base_url, api_key, device_token, cmd_id, 'completed', {'output': summary})
    logger.info(f"restart_services: {summary}")


def handle_ota_upgrade(cmd_id, base_url, api_key, device_token):
    """Download, verify, and install the latest d3kOS release."""
    try:
        from ota_upgrade import run_upgrade
        result = run_upgrade(base_url, api_key, device_token)
        status = 'completed' if result.get('ok') else 'failed'
        ack_command(base_url, api_key, device_token, cmd_id, status, result)
        logger.info(
            f"ota_upgrade: ok={result.get('ok')} "
            f"{result.get('old_version')} → {result.get('new_version')}"
        )
    except ImportError:
        err = 'ota_upgrade.py not found at /opt/d3kos/services/ota_upgrade.py'
        ack_command(base_url, api_key, device_token, cmd_id, 'failed', {'error': err})
        logger.error(f"ota_upgrade: {err}")
    except Exception as e:
        ack_command(base_url, api_key, device_token, cmd_id, 'failed', {'error': str(e)})
        logger.error(f"ota_upgrade exception: {e}")


def handle_setup_lockdown(cmd_id, base_url, api_key, device_token):
    """Apply OS package lockdown — apt-mark hold on critical packages."""
    try:
        from os_lockdown import apply_lockdown
        result = apply_lockdown()
        status = 'completed' if result.get('ok') else 'failed'
        ack_command(base_url, api_key, device_token, cmd_id, status, result)
        logger.info(
            f"setup_lockdown: ok={result.get('ok')} "
            f"held={len(result.get('packages_held', []))} "
            f"errors={len(result.get('errors', []))}"
        )
    except ImportError:
        err = 'os_lockdown.py not found at /opt/d3kos/services/os_lockdown.py'
        ack_command(base_url, api_key, device_token, cmd_id, 'failed', {'error': err})
        logger.error(f"setup_lockdown: {err}")
    except Exception as e:
        ack_command(base_url, api_key, device_token, cmd_id, 'failed', {'error': str(e)})
        logger.error(f"setup_lockdown exception: {e}")


def handle_pair_confirmed(cmd_id, payload, base_url, api_key, device_token):
    """T0 → T1: Pi has been paired via the app. Upgrade tier in license.json
    and trigger an immediate export so HostPapa gets first-sync data."""
    try:
        tier_str = str(payload.get('tier', 'T1')).upper()

        lic_path = Path('/opt/d3kos/config/license.json')
        if lic_path.exists():
            lic = json.loads(lic_path.read_text())
            old_tier = lic.get('tier', 'T0')
            lic['tier'] = tier_str
            lic_path.write_text(json.dumps(lic, indent=2))
            logger.info(f'pair_confirmed: tier {old_tier} -> {tier_str}')
        else:
            old_tier = None
            logger.warning('pair_confirmed: license.json not found, skipping tier update')

        # Trigger immediate export (best-effort — pair_confirmed succeeds even if export fails)
        try:
            requests.post('http://localhost:8094/export/generate', timeout=60)
            logger.info('pair_confirmed: triggered post-pair export')
        except Exception as e_exp:
            logger.warning(f'pair_confirmed: export trigger failed (non-fatal): {e_exp}')

        # Push config snapshot — ensures HostPapa has current state after pairing (FI4)
        push_config_snapshot(base_url, api_key, device_token)

        result = {'old_tier': old_tier, 'new_tier': tier_str}
        ack_command(base_url, api_key, device_token, cmd_id, 'completed', result)
        logger.info(f'pair_confirmed: completed for cmd_id={cmd_id}')

    except Exception as e:
        ack_command(base_url, api_key, device_token, cmd_id, 'failed', {'error': str(e)})
        logger.error(f'pair_confirmed exception: {e}')


FLEET_CONFIG = Path('/opt/d3kos/config/fleet.json')


def handle_fleet_assign(cmd_id, payload, base_url, api_key, device_token):
    """Write fleet.json and (re)start fleet push service."""
    import subprocess
    try:
        fleet_id   = payload.get('fleet_id')
        fleet_code = payload.get('fleet_code', '')
        role       = payload.get('role', 'member')

        if not fleet_id:
            raise ValueError("payload missing 'fleet_id'")

        fleet_data = {
            'fleet_id':   int(fleet_id),
            'fleet_code': str(fleet_code).upper(),
            'role':       str(role),
        }
        FLEET_CONFIG.write_text(json.dumps(fleet_data, indent=2))
        logger.info(f'fleet_assign: wrote fleet.json fleet_id={fleet_id} role={role}')

        # Restart fleet push service so it picks up the new config immediately
        subprocess.run(
            ['sudo', 'systemctl', 'restart', 'd3kos-fleet-push.service'],
            timeout=15, check=False
        )
        logger.info('fleet_assign: restarted d3kos-fleet-push.service')

        ack_command(base_url, api_key, device_token, cmd_id, 'completed',
                    {'fleet_id': int(fleet_id), 'fleet_code': fleet_code, 'role': role})

    except Exception as e:
        ack_command(base_url, api_key, device_token, cmd_id, 'failed', {'error': str(e)})
        logger.error(f'fleet_assign exception: {e}')


DIAGNOSTIC_FIX_WHITELIST = {
    'restart_service':    ['d3kos-voice','d3kos-ai-bridge','d3kos-fleet-push','signalk',
                           'nodered','d3kos-cloud-link','d3kos-predictive','d3kos-gemini-proxy',
                           'd3kos-cloud-agent'],
    'clear_cache':        ['signalk_cache','ai_cache','temp_files'],
    'rotate_logs':        ['d3kos','nginx'],
    'update_config':      ['gps_timeout','ai_model_id','log_retention_days'],
    'recalibrate_sensor': ['gps','temperature','pressure','fuel'],
    'restart_signalk':    [],
    'restart_pi':         [],
}


def handle_diagnostic_fix(cmd_id, payload, base_url, api_key, device_token):
    """Execute a whitelisted diagnostic fix command."""
    import subprocess
    fix_type   = payload.get('fix_type', '')
    fix_target = payload.get('fix_target', '')

    if fix_type not in DIAGNOSTIC_FIX_WHITELIST:
        ack_command(base_url, api_key, device_token, cmd_id, 'failed',
                    {'error': f'fix_type {fix_type!r} not whitelisted'})
        return

    allowed = DIAGNOSTIC_FIX_WHITELIST[fix_type]
    if allowed and fix_target not in allowed:
        ack_command(base_url, api_key, device_token, cmd_id, 'failed',
                    {'error': f'fix_target {fix_target!r} not allowed for {fix_type}'})
        return

    try:
        output = ''

        if fix_type == 'restart_service':
            r = subprocess.run(['sudo', 'systemctl', 'restart', fix_target],
                               capture_output=True, text=True, timeout=30)
            output = (r.stdout + r.stderr).strip() or f'{fix_target} restarted'

        elif fix_type == 'restart_signalk':
            r = subprocess.run(['sudo', 'systemctl', 'restart', 'signalk'],
                               capture_output=True, text=True, timeout=30)
            output = (r.stdout + r.stderr).strip() or 'signalk restarted'

        elif fix_type == 'restart_pi':
            ack_command(base_url, api_key, device_token, cmd_id, 'completed',
                        {'output': 'Rebooting Pi now...'})
            subprocess.run(['sudo', 'reboot'], timeout=10)
            return

        elif fix_type == 'clear_cache':
            cache_map = {
                'signalk_cache': '/tmp/signalk-*',
                'ai_cache':      '/tmp/ai-cache-*',
                'temp_files':    '/tmp/d3kos-*',
            }
            pattern = cache_map.get(fix_target, '')
            if pattern:
                r = subprocess.run(['bash', '-c', f'rm -rf {pattern}'],
                                   capture_output=True, text=True, timeout=15)
                output = f'{fix_target} cleared'
            else:
                output = f'Unknown cache target: {fix_target}'

        elif fix_type == 'rotate_logs':
            service_pattern = 'd3kos-*' if fix_target == 'd3kos' else fix_target
            r = subprocess.run(['sudo', 'journalctl', '--rotate'],
                               capture_output=True, text=True, timeout=15)
            r2 = subprocess.run(['sudo', 'journalctl', '--vacuum-time=7d'],
                                capture_output=True, text=True, timeout=15)
            output = f'Logs rotated for {fix_target}'

        elif fix_type == 'update_config':
            fix_value = payload.get('fix_value')
            if fix_value is None:
                ack_command(base_url, api_key, device_token, cmd_id, 'failed',
                            {'error': 'fix_value required for update_config'})
                return
            config_path = Path('/opt/d3kos/config/cloud-config.json')
            cfg = json.loads(config_path.read_text())
            cfg[fix_target] = fix_value
            config_path.write_text(json.dumps(cfg, indent=2))
            output = f'Config updated: {fix_target}={fix_value}'

        elif fix_type == 'recalibrate_sensor':
            output = f'Sensor recalibration for {fix_target} — not yet implemented on this Pi'

        ack_command(base_url, api_key, device_token, cmd_id, 'completed',
                    {'fix_type': fix_type, 'fix_target': fix_target, 'output': output})
        logger.info(f'diagnostic_fix: {fix_type}/{fix_target} completed')

    except Exception as e:
        ack_command(base_url, api_key, device_token, cmd_id, 'failed', {'error': str(e)})
        logger.error(f'diagnostic_fix exception: {e}')


def handle_diagnostic_collect(cmd_id, payload, base_url, api_key, device_token):
    """Launch diagnostic_agent.py to collect logs, bundle, and upload for a ticket."""
    import subprocess
    ticket_id = payload.get('ticket_id')
    if not ticket_id:
        ack_command(base_url, api_key, device_token, cmd_id, 'failed',
                    {'error': 'ticket_id missing from payload'})
        logger.error('diagnostic_collect: ticket_id missing')
        return

    # ACK immediately — collection takes up to 60s; agent uploads asynchronously
    ack_command(base_url, api_key, device_token, cmd_id, 'completed',
                {'status': 'collecting', 'ticket_id': int(ticket_id)})
    logger.info(f'diagnostic_collect: launching agent for ticket_id={ticket_id}')

    try:
        agent_path = '/opt/d3kos/services/diagnostic/diagnostic_agent.py'
        subprocess.Popen(
            ['/usr/bin/python3', agent_path, '--ticket-id', str(ticket_id)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        logger.info(f'diagnostic_collect: agent launched for ticket_id={ticket_id}')
    except Exception as e:
        logger.error(f'diagnostic_collect: failed to launch agent: {e}')


def handle_fleet_unassign(cmd_id, base_url, api_key, device_token):
    """Remove fleet.json and stop fleet push service."""
    import subprocess
    try:
        if FLEET_CONFIG.exists():
            FLEET_CONFIG.unlink()
            logger.info('fleet_unassign: removed fleet.json')
        else:
            logger.info('fleet_unassign: fleet.json already absent')

        # Stop push service — it will idle when fleet.json is absent
        subprocess.run(
            ['sudo', 'systemctl', 'stop', 'd3kos-fleet-push.service'],
            timeout=15, check=False
        )
        logger.info('fleet_unassign: stopped d3kos-fleet-push.service')

        ack_command(base_url, api_key, device_token, cmd_id, 'completed', {'action': 'unassigned'})

    except Exception as e:
        ack_command(base_url, api_key, device_token, cmd_id, 'failed', {'error': str(e)})
        logger.error(f'fleet_unassign exception: {e}')


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

    elif command == 'fix_my_pi':
        handle_fix_my_pi(cmd_id, base_url, api_key, device_token)

    elif command == 'restart_service':
        handle_restart_services(cmd_id, base_url, api_key, device_token)

    elif command == 'ota_upgrade':
        handle_ota_upgrade(cmd_id, base_url, api_key, device_token)

    elif command == 'setup_lockdown':
        handle_setup_lockdown(cmd_id, base_url, api_key, device_token)

    elif command == 'pair_confirmed':
        handle_pair_confirmed(cmd_id, payload, base_url, api_key, device_token)

    elif command == 'fleet_assign':
        handle_fleet_assign(cmd_id, payload, base_url, api_key, device_token)

    elif command == 'fleet_unassign':
        handle_fleet_unassign(cmd_id, base_url, api_key, device_token)

    elif command == 'diagnostic_collect':
        handle_diagnostic_collect(cmd_id, payload, base_url, api_key, device_token)

    elif command == 'diagnostic_fix':
        handle_diagnostic_fix(cmd_id, payload, base_url, api_key, device_token)

    else:
        ack_command(base_url, api_key, device_token, cmd_id, 'failed',
                    {'error': f'Unknown command: {command}'})
        logger.warning(f"Unknown command: {command}")


# ── Main loop ─────────────────────────────────────────────────────────────────

def run():
    logger.info("d3kOS Cloud Agent starting (v0.9.9.3-FI4)")

    # Config load with retry on missing/invalid config
    while True:
        config = load_cloud_config()
        if config:
            break
        logger.info("Retrying config load in 60s...")
        time.sleep(60)

    api_key       = config['amboat_api_key']
    base_url      = config.get('amboat_base_url', 'https://atmyboat.com').rstrip('/')
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

            # Push config snapshot if changed since last push (FI4 — hash-gated)
            push_config_snapshot(base_url, api_key, device_token)

        except Exception as e:
            logger.error(f"Main loop error: {e}")

        time.sleep(poll_interval)


if __name__ == '__main__':
    run()
