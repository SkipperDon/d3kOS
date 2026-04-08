#!/usr/bin/env python3
"""
deploy-agents.py — v0.9.8 S28 Autonomous Agents deploy to Pi
Deploys AA1 framework + AA3 performance agent, plus dashboard updates.

Run from WSL:
  python3 deployment/features/autonomous-agents/scripts/deploy-agents.py

Pi SSH key must be at: ~/.ssh/id_d3kos
Pi:  192.168.1.237  user: d3kos

What this script does:
  1. Creates /opt/d3kos/services/agents/ directory on Pi
  2. Copies agent Python files
  3. Copies systemd service file and enables it
  4. Copies updated dashboard files (app.py, d3kos.css, index.html, engine-monitor.html)
  5. Restarts d3kos-dashboard
  6. Verifies agent service is active
"""

import subprocess
import sys
import os
from pathlib import Path

# ── Pi config ─────────────────────────────────────────────────────────────────
PI_HOST = '192.168.1.237'
PI_USER = 'd3kos'
SSH_KEY = os.path.expanduser('~/.ssh/id_d3kos')
SSH_OPTS = ['-i', SSH_KEY, '-o', 'StrictHostKeyChecking=no', '-o', 'ConnectTimeout=10']

# ── Local file paths ──────────────────────────────────────────────────────────
SCRIPT_DIR   = Path(__file__).parent
FEATURE_DIR  = SCRIPT_DIR.parent
PI_SRC       = FEATURE_DIR / 'pi_source'
AGENTS_SRC   = PI_SRC / 'agents'
REPO_ROOT    = FEATURE_DIR.parents[2]
DASHBOARD    = REPO_ROOT / 'deployment' / 'd3kOS' / 'dashboard'
ENG_MON_SRC  = REPO_ROOT / 'deployment' / 'v0.9.4' / 'pi_source' / 'engine-monitor.html'

# ── Pi destination paths ──────────────────────────────────────────────────────
PI_AGENTS_DIR    = '/opt/d3kos/services/agents'
PI_DASHBOARD_DIR = '/opt/d3kos/services/dashboard'
PI_DATA_DIR      = '/opt/d3kos/data/agents'
PI_LOG_DIR       = '/opt/d3kos/logs'


# ── Helpers ───────────────────────────────────────────────────────────────────

def ssh(cmd: str, check: bool = True) -> str:
    """Run a command on the Pi via SSH."""
    full = ['ssh'] + SSH_OPTS + [f'{PI_USER}@{PI_HOST}', cmd]
    print(f'  SSH: {cmd}')
    r = subprocess.run(full, capture_output=True, text=True)
    if check and r.returncode != 0:
        print(f'  FAILED (rc={r.returncode}): {r.stderr.strip()}')
        sys.exit(1)
    if r.stdout.strip():
        print(f'  OUT: {r.stdout.strip()}')
    return r.stdout.strip()


def scp(local: Path, remote: str):
    """Copy a local file to Pi via SCP."""
    dest = f'{PI_USER}@{PI_HOST}:{remote}'
    full = ['scp'] + SSH_OPTS + [str(local), dest]
    print(f'  SCP: {local.name} → {remote}')
    r = subprocess.run(full, capture_output=True, text=True)
    if r.returncode != 0:
        print(f'  FAILED: {r.stderr.strip()}')
        sys.exit(1)


def step(msg: str):
    print(f'\n── {msg}')


def ok(msg: str = 'done'):
    print(f'  ✓ {msg}')


# ── Deploy steps ──────────────────────────────────────────────────────────────

def check_ssh():
    step('1 · Checking Pi connection')
    out = ssh('echo pong', check=False)
    if 'pong' not in out:
        print('ERROR: Cannot reach Pi at 192.168.1.237')
        print('  Check: Pi is on, SSH key at ~/.ssh/id_d3kos is correct')
        sys.exit(1)
    ok('Pi reachable')


def create_dirs():
    step('2 · Creating directories on Pi')
    ssh(f'mkdir -p {PI_AGENTS_DIR}/agents {PI_DATA_DIR} {PI_LOG_DIR}')
    ok('Directories created')


def copy_agent_files():
    step('3 · Copying agent Python files')
    files = [
        (PI_SRC / 'agent_base.py',      f'{PI_AGENTS_DIR}/agent_base.py'),
        (PI_SRC / 'agent_scheduler.py', f'{PI_AGENTS_DIR}/agent_scheduler.py'),
        (AGENTS_SRC / '__init__.py',     f'{PI_AGENTS_DIR}/agents/__init__.py'),
        (AGENTS_SRC / 'performance_agent.py', f'{PI_AGENTS_DIR}/agents/performance_agent.py'),
    ]
    for local, remote in files:
        if not local.exists():
            print(f'  ERROR: {local} not found')
            sys.exit(1)
        scp(local, remote)
    ok('Agent files copied')


def install_service():
    step('4 · Installing systemd service')
    service_src = PI_SRC / 'd3kos-agents.service'
    scp(service_src, '/tmp/d3kos-agents.service')
    ssh('sudo cp /tmp/d3kos-agents.service /etc/systemd/system/d3kos-agents.service')
    ssh('sudo systemctl daemon-reload')
    ssh('sudo systemctl enable d3kos-agents')
    ok('Service installed and enabled')


def copy_dashboard_files():
    step('5 · Copying dashboard files')
    dashboard_files = [
        (DASHBOARD / 'app.py',                         f'{PI_DASHBOARD_DIR}/app.py'),
        (DASHBOARD / 'static' / 'css' / 'd3kos.css',  f'{PI_DASHBOARD_DIR}/static/css/d3kos.css'),
        (DASHBOARD / 'templates' / 'index.html',       f'{PI_DASHBOARD_DIR}/templates/index.html'),
    ]
    for local, remote in dashboard_files:
        if not local.exists():
            print(f'  ERROR: {local} not found')
            sys.exit(1)
        scp(local, remote)
    # engine-monitor.html is in v0.9.4/pi_source
    if not ENG_MON_SRC.exists():
        print(f'  ERROR: {ENG_MON_SRC} not found')
        sys.exit(1)
    scp(ENG_MON_SRC, f'{PI_DASHBOARD_DIR}/templates/engine-monitor.html')
    ok('Dashboard files copied')


def restart_services():
    step('6 · Starting agent service + restarting dashboard')
    ssh('sudo systemctl start d3kos-agents')
    ssh('sudo systemctl restart d3kos-dashboard')
    ok('Services started')


def verify():
    step('7 · Verifying')
    # Agent service active?
    out = ssh('systemctl is-active d3kos-agents', check=False)
    if out.strip() == 'active':
        ok('d3kos-agents: active')
    else:
        print(f'  WARNING: d3kos-agents status = {out!r}')
        print('  Check: sudo journalctl -u d3kos-agents -n 30')

    # Status JSON written?
    import time
    print('  Waiting 10s for first agent run ...')
    time.sleep(10)
    out = ssh('test -f /opt/d3kos/data/agents/agent_status.json && echo exists || echo missing', check=False)
    if 'exists' in out:
        content = ssh('cat /opt/d3kos/data/agents/agent_status.json', check=False)
        ok(f'agent_status.json written: {content[:120]}')
    else:
        print('  NOTE: agent_status.json not yet written (agents have 5-min first run window)')
        print('  Check after 5 min: cat /opt/d3kos/data/agents/agent_status.json')

    # Dashboard serving /agents/status?
    out = ssh('curl -s http://localhost:3000/agents/status', check=False)
    if 'overall' in out:
        ok(f'/agents/status responding: {out[:100]}')
    else:
        print(f'  WARNING: /agents/status not responding as expected: {out[:100]}')


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print('=' * 60)
    print('d3kOS v0.9.8 S28 — Autonomous Agents Deploy')
    print(f'Target: {PI_USER}@{PI_HOST}')
    print('=' * 60)

    check_ssh()
    create_dirs()
    copy_agent_files()
    install_service()
    copy_dashboard_files()
    restart_services()
    verify()

    print('\n' + '=' * 60)
    print('Deploy complete.')
    print()
    print('Next steps:')
    print('  1. Open http://192.168.1.237 — confirm Pi health dot in status bar')
    print('  2. Open http://192.168.1.237/engine-monitor — confirm Section 6 Agents')
    print('  3. Wait 5 min — dot should turn green once first agent run completes')
    print('  4. Check logs: ssh -i ~/.ssh/id_d3kos d3kos@192.168.1.237')
    print('                 tail -f /opt/d3kos/logs/agents.log')
    print()
    print('Still to do (BUILD_CHECKLIST D18):')
    print('  Add d3kos-agents to CRITICAL_SERVICES in d3kos_watchdog.py')
    print('=' * 60)
