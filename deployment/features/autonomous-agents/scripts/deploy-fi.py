#!/usr/bin/env python3
"""
deploy-fi.py — v0.9.8 S31 FI1/FI2/FI3 deployment
Deploys Failure Intelligence PHP files to HostPapa staging.
CRM files must be added to Admin VM manually (see instructions below).

Run from WSL: python3 deployment/features/autonomous-agents/scripts/deploy-fi.py

CRM integration (manual — paste into app.py on VM):
  deployment/features/autonomous-agents/crm/failure_routes.py
  deployment/features/autonomous-agents/crm/failures.html → /opt/admin-crm/templates/

Also add these two helpers near proxy_call() in app.py on VM:
  def proxy_call_issues(params): ...
  def proxy_post_issues(payload): ...
(See failure_routes.py header for the exact code.)
"""

import ftplib
import os
import sys

# ── FTP config ────────────────────────────────────────────────────────────────
FTP_HOST   = 'ftp.atmyboat.com'
FTP_PORT   = 21
FTP_USER   = 'd3kos@atmyboat.com'
FTP_PASS   = os.environ.get('ATMYBOAT_FTP_PASS', '')
FTP_MOBILE = 'staging/wp-content/themes/twentytwenty-child/mobile'

# ── Local file paths ──────────────────────────────────────────────────────────
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
FEATURE_DIR = os.path.dirname(SCRIPT_DIR)
PHP_DIR     = os.path.join(FEATURE_DIR, 'php')

PHP_FILES = [
    'failure-report.php',
    'fix-confirmed.php',
    'issue-api.php',
]


def ftp_upload(ftp, local_path, remote_path):
    with open(local_path, 'rb') as f:
        ftp.storbinary(f'STOR {remote_path}', f)
    print(f'  ✓ {os.path.basename(local_path)} → {remote_path}')


def main():
    if not FTP_PASS:
        print('ERROR: Set ATMYBOAT_FTP_PASS environment variable before running.')
        sys.exit(1)

    print('Connecting to HostPapa FTP...')
    ftp = ftplib.FTP()
    ftp.connect(FTP_HOST, FTP_PORT, timeout=30)
    ftp.login(FTP_USER, FTP_PASS)
    ftp.set_pasv(True)
    print('Connected.\n')

    print('Deploying FI PHP endpoints to mobile/ ...')
    for fname in PHP_FILES:
        local  = os.path.join(PHP_DIR, fname)
        remote = f'{FTP_MOBILE}/{fname}'
        ftp_upload(ftp, local, remote)

    ftp.quit()
    print('\nHostPapa deploy complete.')
    print()
    print('Next: Add CRM routes to Admin VM app.py')
    print('  1. Append deployment/features/autonomous-agents/crm/failure_routes.py')
    print('     to /opt/admin-crm/app.py (before the if __name__ block)')
    print('  2. Add proxy_call_issues() + proxy_post_issues() helpers (see file header)')
    print('  3. Copy failures.html to /opt/admin-crm/templates/')
    print('  4. sudo systemctl restart admin-crm')


if __name__ == '__main__':
    main()
