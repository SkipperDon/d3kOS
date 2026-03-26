#!/usr/bin/env python3
"""
d3kOS OS Lockdown
Prevents OS package upgrades from breaking d3kOS services.

Executed by cloud_agent.py when a 'setup_lockdown' command is received.
Can also be run standalone: sudo python3 os_lockdown.py

Actions:
  1. apt-mark hold on all critical d3kOS dependencies
  2. Install /etc/apt/apt.conf.d/99-d3kos-hold.conf to show warning on apt upgrade
  3. Write lockdown state to /opt/d3kos/config/lockdown.json

Packages held:
  - python3, python3-pip (d3kOS runs on system Python)
  - libsignalk-* (Signal K server — holds 2.23.0)
  - node* (Node-RED depends on Node.js version)
  - avnav (chart plotting)
  - chromium-browser (kiosk)
  - nginx (reverse proxy)

Author: d3kOS Team
Version: 0.9.4
"""

import json
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler

# ── Config ────────────────────────────────────────────────────────────────────
LOCKDOWN_FILE  = Path('/opt/d3kos/config/lockdown.json')
APT_CONF_FILE  = Path('/etc/apt/apt.conf.d/99-d3kos-hold.conf')
LOG_FILE       = Path('/opt/d3kos/logs/os-lockdown.log')

# Packages to hold. These are the versions confirmed working with d3kOS v0.9.2.2.
HELD_PACKAGES = [
    'python3',
    'python3-pip',
    'python3-flask',
    'signalk-server',
    'nodejs',
    'avnav',
    'chromium-browser',
    'nginx',
]

APT_CONF_CONTENT = """\
// d3kOS OS Lockdown — do not remove this file.
// Several system packages are held by d3kOS to ensure service stability.
// Run 'apt-mark showhold' to see held packages.
// To upgrade d3kOS, use the AtMyBoat.com mobile app (OTA upgrade).
// To temporarily release holds: sudo apt-mark unhold <package>
// WARNING: Releasing holds may break d3kOS services.
DPkg::Pre-Invoke { "echo '\\n*** d3kOS: Some packages are held. Run apt-mark showhold to list them. ***\\n'"; };
"""

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logger = logging.getLogger('os-lockdown')
logger.setLevel(logging.INFO)
_h = RotatingFileHandler(str(LOG_FILE), maxBytes=1024 * 1024, backupCount=1)
_h.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(_h)


def _run(cmd, timeout=15):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except Exception as e:
        return -1, '', str(e)


def get_held_packages():
    """Return list of currently held packages."""
    rc, out, _ = _run(['apt-mark', 'showhold'])
    if rc == 0 and out:
        return [p.strip() for p in out.splitlines() if p.strip()]
    return []


def apply_lockdown():
    """
    Apply apt-mark hold on all critical packages.
    Returns { ok, actions_taken, errors, packages_held }
    """
    actions = []
    errors  = []

    already_held = set(get_held_packages())
    newly_held   = []
    not_found    = []

    for pkg in HELD_PACKAGES:
        if pkg in already_held:
            actions.append(f'{pkg}: already held')
            continue

        rc, out, err = _run(['sudo', 'apt-mark', 'hold', pkg])
        if rc == 0:
            newly_held.append(pkg)
            actions.append(f'{pkg}: held')
        else:
            # Package may not be installed — log but don't fail
            not_found.append(pkg)
            actions.append(f'{pkg}: not installed or hold failed — skipped')
            logger.warning(f'apt-mark hold {pkg}: {err}')

    # Install apt warning conf
    try:
        APT_CONF_FILE.write_text(APT_CONF_CONTENT)
        actions.append(f'Wrote {APT_CONF_FILE}')
    except PermissionError:
        errors.append(
            f'Cannot write {APT_CONF_FILE} — run as root or via sudo. '
            'Holds were still applied via apt-mark.'
        )
    except Exception as e:
        errors.append(f'apt.conf write error: {e}')

    # Write lockdown state
    all_held = list(already_held | set(newly_held))
    state = {
        'applied_at':      datetime.utcnow().isoformat() + 'Z',
        'packages_held':   sorted(all_held),
        'packages_skipped': not_found,
    }
    try:
        with open(LOCKDOWN_FILE, 'w') as f:
            json.dump(state, f, indent=2)
        actions.append(f'Wrote {LOCKDOWN_FILE}')
    except Exception as e:
        errors.append(f'Lockdown state write error: {e}')

    ok = len(errors) == 0
    logger.info(
        f'Lockdown applied: {len(newly_held)} new holds, '
        f'{len(already_held)} already held, {len(not_found)} not found. '
        f'errors={len(errors)}'
    )

    return {
        'ok':             ok,
        'packages_held':  all_held,
        'packages_newly_held': newly_held,
        'packages_skipped': not_found,
        'actions_taken':  actions,
        'errors':         errors,
        'timestamp':      datetime.utcnow().isoformat() + 'Z',
    }


def get_lockdown_status():
    """Return current lockdown state (held packages + config status)."""
    held = get_held_packages()
    conf_exists = APT_CONF_FILE.exists()
    state_exists = LOCKDOWN_FILE.exists()

    return {
        'packages_held': held,
        'apt_conf_installed': conf_exists,
        'lockdown_state_file': state_exists,
        'lockdown_active': len(held) > 0 and conf_exists,
    }


if __name__ == '__main__':
    import sys
    if '--status' in sys.argv:
        print(json.dumps(get_lockdown_status(), indent=2))
    else:
        result = apply_lockdown()
        print(json.dumps(result, indent=2))
