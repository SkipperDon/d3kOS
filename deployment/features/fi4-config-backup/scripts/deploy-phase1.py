#!/usr/bin/env python3
"""
deploy-phase1.py — FI4 Config Backup & Recovery Phase 1
Deploys config-backup.php and config-restore.php to HostPapa staging.

Usage:
    ATMYBOAT_FTP_PASS='your-password' python3 deployment/features/fi4-config-backup/scripts/deploy-phase1.py

Run from Helm-OS/ root.
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
    'config-backup.php',
    'config-restore.php',
]

# ── Preflight ─────────────────────────────────────────────────────────────────
if not FTP_PASS:
    print('ERROR: ATMYBOAT_FTP_PASS environment variable not set.')
    print('Usage: ATMYBOAT_FTP_PASS=\'your-password\' python3 deployment/features/fi4-config-backup/scripts/deploy-phase1.py')
    sys.exit(1)

for f in PHP_FILES:
    path = os.path.join(PHP_DIR, f)
    if not os.path.exists(path):
        print(f'ERROR: Local file not found: {path}')
        sys.exit(1)

# ── Deploy ────────────────────────────────────────────────────────────────────
print(f'Connecting to {FTP_HOST}...')
ftp = ftplib.FTP()
ftp.connect(FTP_HOST, FTP_PORT, timeout=30)
ftp.login(FTP_USER, FTP_PASS)
ftp.cwd(FTP_MOBILE)
print(f'Connected. Working directory: {ftp.pwd()}')

for fname in PHP_FILES:
    local_path = os.path.join(PHP_DIR, fname)
    with open(local_path, 'rb') as f:
        ftp.storbinary(f'STOR {fname}', f)
    print(f'  Uploaded: {fname}')

ftp.quit()
print()
print('Phase 1 deploy complete.')
print()
print('Smoke tests — run these to verify:')
print()
print('1. Test backup endpoint (expect 401 — no auth):')
print('   curl -s -o /dev/null -w "%{http_code}" \\')
print('     -X POST https://atmyboat.com/staging/wp-content/themes/twentytwenty-child/mobile/config-backup.php')
print()
print('2. Test restore endpoint (expect 404 — no token):')
print('   curl -s https://atmyboat.com/staging/wp-content/themes/twentytwenty-child/mobile/config-restore.php?token=invalid')
