#!/usr/bin/env python3
"""
d3kOS Fix My Pi — Diagnostic and Repair Script
Invoked by cloud_agent.py when a fix_my_pi command is received from AtMyBoat.com.

Performs:
  1. Service health check — restart any failed d3kOS services
  2. Disk space check — alert if < 500MB free
  3. Config file check — verify all required config files exist
  4. Network check — verify outbound connectivity to atmyboat.com
  5. Log rotation — trim oversized logs to reclaim disk

Returns a JSON-serialisable dict with:
  { 'ok': bool, 'checks': [...], 'actions_taken': [...], 'errors': [...] }

Author: d3kOS Team
Version: 0.9.4
"""

import json
import subprocess
import shutil
import time
from pathlib import Path
from datetime import datetime

# ── d3kOS services that must be running ───────────────────────────────────────
REQUIRED_SERVICES = [
    'd3kos-cloud-agent',
    'd3kos-export-manager',
    'd3kos-tier',
]

# ── Config files that must exist ─────────────────────────────────────────────
REQUIRED_CONFIGS = [
    Path('/opt/d3kos/config/cloud-config.json'),
    Path('/opt/d3kos/config/license.json'),
    Path('/opt/d3kos/config/device-token.json'),
]

# ── Log files to trim if oversized (max bytes each) ───────────────────────────
LOG_TRIM_RULES = [
    (Path('/opt/d3kos/logs/cloud-agent.log'),    10 * 1024 * 1024),
    (Path('/opt/d3kos/logs/export-manager.log'), 10 * 1024 * 1024),
]

MIN_FREE_DISK_MB = 500


def _run(cmd, timeout=15):
    """Run shell command, return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, '', f'Timeout after {timeout}s'
    except Exception as e:
        return -1, '', str(e)


def check_service(service_name):
    """Check if systemd service is active. Returns (active: bool, state: str)."""
    rc, out, _ = _run(['systemctl', 'is-active', service_name])
    state = out.strip() if out else 'unknown'
    return state == 'active', state


def restart_service(service_name):
    """Attempt to restart a systemd service. Returns (success: bool, output: str)."""
    rc, out, err = _run(['sudo', 'systemctl', 'restart', service_name], timeout=30)
    if rc == 0:
        # Verify it started
        time.sleep(2)
        active, state = check_service(service_name)
        if active:
            return True, f'restarted → {state}'
        else:
            return False, f'restart issued but service is now {state}'
    return False, err or f'exit code {rc}'


def check_services():
    """Check all required services, attempt restarts of failed ones."""
    checks = []
    actions = []
    errors = []

    for svc in REQUIRED_SERVICES:
        active, state = check_service(svc)
        if active:
            checks.append({'service': svc, 'state': 'active', 'ok': True})
        else:
            checks.append({'service': svc, 'state': state, 'ok': False})
            # Attempt restart
            success, msg = restart_service(svc)
            if success:
                actions.append(f'Restarted {svc}: {msg}')
                checks[-1]['recovered'] = True
            else:
                errors.append(f'Failed to restart {svc}: {msg}')
                checks[-1]['recovered'] = False

    return checks, actions, errors


def check_disk():
    """Check free disk space on /."""
    checks = []
    actions = []
    errors = []

    try:
        usage = shutil.disk_usage('/')
        free_mb = usage.free // (1024 * 1024)
        total_mb = usage.total // (1024 * 1024)
        used_pct = int((usage.used / usage.total) * 100)

        ok = free_mb >= MIN_FREE_DISK_MB
        checks.append({
            'check':    'disk_space',
            'free_mb':  free_mb,
            'total_mb': total_mb,
            'used_pct': used_pct,
            'ok':       ok,
        })

        if not ok:
            errors.append(
                f'Low disk space: {free_mb}MB free (threshold: {MIN_FREE_DISK_MB}MB). '
                'Consider clearing /opt/d3kos/data/exports/completed/'
            )

    except Exception as e:
        errors.append(f'Disk check failed: {e}')

    return checks, actions, errors


def check_configs():
    """Verify all required config files exist and are valid JSON."""
    checks = []
    actions = []
    errors = []

    for path in REQUIRED_CONFIGS:
        if not path.exists():
            checks.append({'config': str(path), 'ok': False, 'reason': 'file missing'})
            errors.append(f'Config file missing: {path}')
            continue

        try:
            with open(path) as f:
                json.load(f)
            checks.append({'config': str(path), 'ok': True})
        except json.JSONDecodeError as e:
            checks.append({'config': str(path), 'ok': False, 'reason': f'invalid JSON: {e}'})
            errors.append(f'Config file corrupt (invalid JSON): {path}')

    return checks, actions, errors


def check_network(base_url='https://atmyboat.com'):
    """Verify outbound connectivity to atmyboat.com."""
    checks = []
    actions = []
    errors = []

    import urllib.request
    try:
        req = urllib.request.Request(base_url, method='HEAD')
        req.add_header('User-Agent', 'd3kOS-FixMyPi/0.9.4')
        with urllib.request.urlopen(req, timeout=10) as resp:
            ok = resp.status < 500
            checks.append({'check': 'network', 'url': base_url, 'http_status': resp.status, 'ok': ok})
    except Exception as e:
        checks.append({'check': 'network', 'url': base_url, 'ok': False, 'error': str(e)})
        errors.append(f'Network check failed: cannot reach {base_url}: {e}')

    return checks, actions, errors


def trim_logs():
    """Trim oversized log files to reclaim disk."""
    actions = []
    errors = []

    for log_path, max_bytes in LOG_TRIM_RULES:
        if not log_path.exists():
            continue
        try:
            size = log_path.stat().st_size
            if size > max_bytes:
                # Keep the last max_bytes worth of the file
                with open(log_path, 'rb') as f:
                    f.seek(-max_bytes, 2)
                    tail = f.read()
                with open(log_path, 'wb') as f:
                    f.write(tail)
                freed_mb = (size - max_bytes) // (1024 * 1024)
                actions.append(f'Trimmed {log_path.name}: freed ~{freed_mb}MB')
        except Exception as e:
            errors.append(f'Failed to trim {log_path}: {e}')

    return actions, errors


def run_diagnostics(base_url='https://atmyboat.com'):
    """
    Run all diagnostic checks and repairs.
    Returns dict: { ok, checks, actions_taken, errors, timestamp }
    """
    all_checks  = []
    all_actions = []
    all_errors  = []

    # Service health
    c, a, e = check_services()
    all_checks.extend(c); all_actions.extend(a); all_errors.extend(e)

    # Disk space
    c, a, e = check_disk()
    all_checks.extend(c); all_actions.extend(a); all_errors.extend(e)

    # Log trimming (reclaim disk before reporting)
    a, e = trim_logs()
    all_actions.extend(a); all_errors.extend(e)

    # Config files
    c, a, e = check_configs()
    all_checks.extend(c); all_actions.extend(a); all_errors.extend(e)

    # Network
    c, a, e = check_network(base_url)
    all_checks.extend(c); all_actions.extend(a); all_errors.extend(e)

    overall_ok = len(all_errors) == 0

    return {
        'ok':           overall_ok,
        'checks':       all_checks,
        'actions_taken': all_actions,
        'errors':       all_errors,
        'timestamp':    datetime.utcnow().isoformat() + 'Z',
    }


if __name__ == '__main__':
    result = run_diagnostics()
    print(json.dumps(result, indent=2))
