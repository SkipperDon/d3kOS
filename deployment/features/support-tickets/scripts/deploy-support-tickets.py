#!/usr/bin/env python3
"""
deploy-support-tickets.py — v0.9.7 Phase 1 deployment
Deploys support ticket PHP files to HostPapa staging and CRM files to Admin VM.

Run from WSL: python3 deployment/features/support-tickets/scripts/deploy-support-tickets.py
"""

import ftplib
import os
import sys
import subprocess

# ── FTP config (HostPapa staging) ─────────────────────────────────────────────
FTP_HOST = 'ftp.atmyboat.com'
FTP_PORT = 21
FTP_USER = 'd3kos@atmyboat.com'
FTP_PASS = os.environ.get('ATMYBOAT_FTP_PASS', '')
FTP_MOBILE = 'staging/wp-content/themes/twentytwenty-child/mobile'

# ── VM config (Admin CRM) ─────────────────────────────────────────────────────
VM_IP   = '192.168.236.5'
VM_USER = 'skipper'
VM_PASS = os.environ.get('ADMIN_VM_PASS', '')
PSCP    = 'pscp.exe'   # run from Windows; in WSL call via subprocess
PLINK   = 'plink.exe'

# ── Local file paths ──────────────────────────────────────────────────────────
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
FEATURE_DIR = os.path.dirname(SCRIPT_DIR)
PHP_DIR     = os.path.join(FEATURE_DIR, 'php')
CRM_DIR     = os.path.join(FEATURE_DIR, 'crm')

# PWA app.js is in v0.9.4
REPO_ROOT   = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../../'))
PWA_JS      = os.path.join(REPO_ROOT, 'deployment/v0.9.4/pwa/app.js')
PWA_FTP_DIR = 'staging/wp-content/themes/twentytwenty-child/app'


def ftp_upload(ftp, local_path, remote_path):
    print(f'  FTP upload: {os.path.basename(local_path)} → {remote_path}')
    with open(local_path, 'rb') as f:
        ftp.storbinary(f'STOR {remote_path}', f)
    print(f'  ✓ {os.path.basename(local_path)}')


def deploy_php():
    print('\n── Phase 1: HostPapa PHP files ───────────────────────────────')
    if not FTP_PASS:
        print('ERROR: set ATMYBOAT_FTP_PASS env var before running')
        return False

    php_files = [
        ('support-request.php', FTP_MOBILE),
        ('support-migrate.php', FTP_MOBILE),
        ('ticket-status.php',   FTP_MOBILE),
        ('admin-api-tickets.php', FTP_MOBILE),
    ]

    try:
        ftp = ftplib.FTP()
        ftp.connect(FTP_HOST, FTP_PORT)
        ftp.login(FTP_USER, FTP_PASS)
        ftp.set_pasv(True)
        print(f'Connected to {FTP_HOST}')

        for filename, remote_dir in php_files:
            local  = os.path.join(PHP_DIR, filename)
            remote = f'{remote_dir}/{filename}'
            if not os.path.exists(local):
                print(f'  SKIP (not found): {local}')
                continue
            ftp_upload(ftp, local, remote)

        ftp.quit()
        print('PHP deploy complete.')
        return True
    except Exception as e:
        print(f'FTP error: {e}')
        return False


def deploy_pwa():
    print('\n── Phase 2: PWA app.js ───────────────────────────────────────')
    if not FTP_PASS:
        print('ERROR: set ATMYBOAT_FTP_PASS env var before running')
        return False

    try:
        ftp = ftplib.FTP()
        ftp.connect(FTP_HOST, FTP_PORT)
        ftp.login(FTP_USER, FTP_PASS)
        ftp.set_pasv(True)

        # Try common PWA paths
        pwa_remote_candidates = [
            f'{PWA_FTP_DIR}/app.js',
            'staging/app/app.js',
        ]
        uploaded = False
        for remote in pwa_remote_candidates:
            try:
                ftp_upload(ftp, PWA_JS, remote)
                uploaded = True
                break
            except ftplib.error_perm:
                continue

        ftp.quit()
        if not uploaded:
            print('WARNING: could not determine PWA FTP path — upload app.js manually')
            return False
        print('PWA deploy complete.')
        return True
    except Exception as e:
        print(f'FTP error: {e}')
        return False


def deploy_crm():
    print('\n── Phase 3: Admin CRM (VM) ───────────────────────────────────')
    if not VM_PASS:
        print('ERROR: set ADMIN_VM_PASS env var before running')
        return False

    crm_files = [
        (os.path.join(CRM_DIR, 'tickets.html'), '/home/d3kos-admin/templates/tickets.html'),
    ]

    for local, remote in crm_files:
        if not os.path.exists(local):
            print(f'  SKIP (not found): {local}')
            continue

        tmp = f'/tmp/{os.path.basename(local)}'
        dest = remote

        # Convert WSL path to Windows path for pscp.exe
        win_local = local.replace('/home/', '\\\\wsl.localhost\\Ubuntu\\home\\').replace('/', '\\')

        print(f'  Uploading {os.path.basename(local)} to {dest}')
        pscp_cmd = (
            f'cmd.exe /c "{PSCP} -pw {VM_PASS} -batch '
            f'"{win_local}" {VM_USER}@{VM_IP}:{tmp}"'
        )
        r = subprocess.run(pscp_cmd, shell=True, capture_output=True, text=True)
        if r.returncode != 0:
            print(f'  pscp error: {r.stderr}')
            return False

        cp_cmd = (
            f'cmd.exe /c "{PLINK} -pw {VM_PASS} -batch '
            f'{VM_USER}@{VM_IP} sudo cp {tmp} {dest}"'
        )
        r = subprocess.run(cp_cmd, shell=True, capture_output=True, text=True)
        if r.returncode != 0:
            print(f'  plink error: {r.stderr}')
            return False

        print(f'  ✓ {os.path.basename(local)} → {dest}')

    print('\n  MANUAL STEP REQUIRED — app.py update on VM:')
    print('  1. Read ticket_routes_snippet.py in deployment/features/support-tickets/crm/')
    print('  2. Add proxy_call_tickets() helper near proxy_call() in app.py')
    print('  3. Add the 3 route functions before  if __name__ == "__main__":')
    print('  4. Add Tickets nav link in base.html before DB Explorer')
    print('  5. sudo systemctl restart admin-crm.service')
    print('\n  Tickets nav link to add in base.html:')
    print("  <li><a href=\"{{ url_for('tickets') }}\" "
          "{% if request.endpoint in ('tickets','ticket_detail','ticket_update') %}"
          "class=\"active\"{% endif %}>Tickets</a></li>")

    return True


def run_migration():
    print('\n── Phase 4: Run DB migration ─────────────────────────────────')
    print('  Open in browser (replace YOUR_KEY):')
    print('  https://atmyboat.com/staging/mobile/support-migrate.php?setup_key=YOUR_KEY')
    print('  Expected: {"success":true,"results":["amboat_support_tickets — created (or already existed)"]}')
    print('  Then DELETE support-migrate.php from HostPapa (cPanel File Manager).')


if __name__ == '__main__':
    print('v0.9.7 Phase 1 — Support Ticket Deploy')
    print('=' * 55)

    ok1 = deploy_php()
    ok2 = deploy_pwa() if ok1 else False
    ok3 = deploy_crm()
    run_migration()

    print('\n── Summary ───────────────────────────────────────────────────')
    print(f'PHP files:  {"✓" if ok1 else "FAILED"}')
    print(f'PWA app.js: {"✓" if ok2 else "FAILED/manual"}')
    print(f'CRM files:  {"✓" if ok3 else "FAILED"}')
    print('\nManual steps remaining:')
    print('  1. Add proxy_call_tickets() + 3 routes to app.py on VM')
    print('  2. Add Tickets link to base.html on VM')
    print('  3. Restart admin-crm.service on VM')
    print('  4. Run support-migrate.php in browser')
    print('  5. Delete support-migrate.php from HostPapa')
