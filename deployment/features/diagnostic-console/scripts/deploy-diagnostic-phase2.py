#!/usr/bin/env python3
"""
deploy-diagnostic-phase2.py — v0.9.7 Phase 2 deployment
Deploys Remote Diagnostic Console files to HostPapa staging and Pi.

Run: ATMYBOAT_FTP_PASS=xxx python3 deploy-diagnostic-phase2.py
"""

import ftplib
import os
import subprocess
import sys

# ── FTP config ────────────────────────────────────────────────────────────────
FTP_HOST   = 'ftp.atmyboat.com'
FTP_PORT   = 21
FTP_USER   = 'd3kos@atmyboat.com'
FTP_PASS   = os.environ.get('ATMYBOAT_FTP_PASS', '')
FTP_MOBILE = 'staging/wp-content/themes/twentytwenty-child/mobile'
FTP_APP    = 'staging/wp-content/themes/twentytwenty-child/app'

# ── Pi config ─────────────────────────────────────────────────────────────────
PI_HOST    = '192.168.1.237'
PI_USER    = 'd3kos'
PI_KEY     = os.path.expanduser('~/.ssh/id_d3kos')

# ── Paths ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
FEATURE_DIR = os.path.dirname(SCRIPT_DIR)
REPO_ROOT   = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../../'))
PHP_DIR     = os.path.join(FEATURE_DIR, 'php')
PI_DIR      = os.path.join(FEATURE_DIR, 'pi')
APP_JS      = os.path.join(REPO_ROOT, 'deployment/v0.9.4/pwa/app.js')
CLOUD_AGENT = os.path.join(REPO_ROOT, 'deployment/v0.9.4/pi_source/cloud_agent.py')


def ftp_upload(ftp, local_path, remote_path):
    print(f'  uploading {os.path.basename(local_path)} → {remote_path}')
    with open(local_path, 'rb') as f:
        ftp.storbinary(f'STOR {remote_path}', f)
    print(f'  ✓ {os.path.basename(local_path)}')


def deploy_php():
    print('\n── Step 1: PHP files → HostPapa staging ──────────────────────')
    if not FTP_PASS:
        print('ERROR: set ATMYBOAT_FTP_PASS env var')
        return False

    php_files = [
        'diagnostic-migrate.php',
        'diagnostic-consent.php',
        'diagnostic-status.php',
        'diagnostic-upload.php',
        'diagnostic-revoke.php',
    ]

    try:
        ftp = ftplib.FTP()
        ftp.connect(FTP_HOST, FTP_PORT)
        ftp.login(FTP_USER, FTP_PASS)
        ftp.set_pasv(True)
        print(f'  Connected to {FTP_HOST}')

        for fn in php_files:
            local = os.path.join(PHP_DIR, fn)
            if not os.path.exists(local):
                print(f'  SKIP (not found): {fn}')
                continue
            ftp_upload(ftp, local, f'{FTP_MOBILE}/{fn}')

        ftp.quit()
        print('  PHP deploy complete.')
        return True
    except Exception as e:
        print(f'  FTP error: {e}')
        return False


def deploy_pwa():
    print('\n── Step 2: app.js → HostPapa staging ────────────────────────')
    if not FTP_PASS:
        print('ERROR: set ATMYBOAT_FTP_PASS env var')
        return False

    try:
        ftp = ftplib.FTP()
        ftp.connect(FTP_HOST, FTP_PORT)
        ftp.login(FTP_USER, FTP_PASS)
        ftp.set_pasv(True)

        ftp_upload(ftp, APP_JS, f'{FTP_APP}/app.js')
        ftp.quit()
        print('  PWA deploy complete.')
        return True
    except Exception as e:
        print(f'  FTP error: {e}')
        return False


def ssh(cmd):
    """Run command on Pi via SSH, return (returncode, stdout+stderr)."""
    r = subprocess.run(
        ['ssh', '-i', PI_KEY, '-o', 'StrictHostKeyChecking=no', '-o', 'BatchMode=yes',
         f'{PI_USER}@{PI_HOST}', cmd],
        capture_output=True, text=True, timeout=30
    )
    return r.returncode, r.stdout + r.stderr


def scp(local, remote):
    """SCP local file to Pi."""
    r = subprocess.run(
        ['scp', '-i', PI_KEY, '-o', 'StrictHostKeyChecking=no',
         local, f'{PI_USER}@{PI_HOST}:{remote}'],
        capture_output=True, text=True, timeout=30
    )
    return r.returncode, r.stdout + r.stderr


def deploy_pi():
    print('\n── Step 3: Pi files ─────────────────────────────────────────')

    # Verify Pi reachable
    rc, out = ssh('echo ok')
    if rc != 0:
        print(f'  ERROR: cannot reach Pi: {out}')
        return False
    print('  Pi reachable ✓')

    # Create diagnostic service directory
    rc, out = ssh('mkdir -p /opt/d3kos/services/diagnostic')
    if rc != 0:
        print(f'  mkdir error: {out}')
        return False
    print('  /opt/d3kos/services/diagnostic created ✓')

    # Upload diagnostic_agent.py
    agent_local = os.path.join(PI_DIR, 'diagnostic_agent.py')
    rc, out = scp(agent_local, '/opt/d3kos/services/diagnostic/diagnostic_agent.py')
    if rc != 0:
        print(f'  scp diagnostic_agent.py error: {out}')
        return False
    ssh('chmod +x /opt/d3kos/services/diagnostic/diagnostic_agent.py')
    print('  diagnostic_agent.py deployed ✓')

    # Upload updated cloud_agent.py
    rc, out = scp(CLOUD_AGENT, '/tmp/cloud_agent.py')
    if rc != 0:
        print(f'  scp cloud_agent.py error: {out}')
        return False
    rc, out = ssh('sudo cp /tmp/cloud_agent.py /opt/d3kos/services/cloud-agent/cloud_agent.py')
    if rc != 0:
        print(f'  cp cloud_agent.py error: {out}')
        return False
    print('  cloud_agent.py deployed ✓')

    # Upload and install systemd service
    svc_local = os.path.join(PI_DIR, 'd3kos-diagnostic.service')
    rc, out = scp(svc_local, '/tmp/d3kos-diagnostic.service')
    if rc != 0:
        print(f'  scp service file error: {out}')
        return False
    rc, out = ssh('sudo cp /tmp/d3kos-diagnostic.service /etc/systemd/system/ && sudo systemctl daemon-reload')
    if rc != 0:
        print(f'  systemd install error: {out}')
        return False
    print('  d3kos-diagnostic.service installed ✓')

    # Restart cloud-agent to pick up diagnostic_collect handler
    rc, out = ssh('sudo systemctl restart d3kos-cloud-agent')
    if rc != 0:
        print(f'  restart error: {out}')
        return False
    print('  d3kos-cloud-agent restarted ✓')

    # Verify cloud-agent is running
    rc, out = ssh('systemctl is-active d3kos-cloud-agent')
    status = out.strip()
    print(f'  d3kos-cloud-agent status: {status}')

    print('  Pi deploy complete.')
    return True


def show_migration_url():
    print('\n── Step 4: Run DB migration ──────────────────────────────────')
    print('  Open in browser:')
    print('  https://atmyboat.com/staging/wp-content/themes/twentytwenty-child/mobile/diagnostic-migrate.php?key=fleet2026test')
    print('  Expected output: all 4 tables = OK')
    print('  Then delete diagnostic-migrate.php via cPanel File Manager.')


if __name__ == '__main__':
    print('v0.9.7 Phase 2 — Remote Diagnostic Console Deploy')
    print('=' * 55)

    ok1 = deploy_php()
    ok2 = deploy_pwa() if ok1 else False
    ok3 = deploy_pi()
    show_migration_url()

    print('\n── Summary ───────────────────────────────────────────────────')
    print(f'PHP files (5):  {"✓" if ok1 else "FAILED"}')
    print(f'app.js:         {"✓" if ok2 else "FAILED"}')
    print(f'Pi files:       {"✓" if ok3 else "FAILED"}')
    print()
    print('Manual steps remaining:')
    print('  1. Open migration URL above in browser (creates 4 DB tables)')
    print('  2. Delete diagnostic-migrate.php from HostPapa cPanel')
    print('  3. Clear SW cache on phone: Chrome → Site Settings → Clear & Reset')
    if not ok1 or not ok2 or not ok3:
        sys.exit(1)
