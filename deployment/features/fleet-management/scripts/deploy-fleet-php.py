#!/usr/bin/env python3
"""
Deploy fleet PHP endpoints to HostPapa staging via FTPS.
Reads credentials from atmyboat-forum/.env (same as deploy-pwa.py).

Files deployed to /staging/mobile/:
  fleet-setup.php
  fleet-create.php
  fleet-join.php
  fleet-ingest.php
  fleet-map.php
  fleet-analytics.php

Usage:
  python3 deploy-fleet-php.py
"""

import ftplib
import os
import sys
from pathlib import Path

# Locate .env relative to this script
_REPO_ROOT = Path(__file__).resolve().parents[4]
_ENV_FILE  = _REPO_ROOT / 'atmyboat-forum' / '.env'

if not _ENV_FILE.is_file():
    print(f'ERROR: .env not found at {_ENV_FILE}')
    sys.exit(1)

# Parse .env manually (avoid external deps)
env = {}
for line in _ENV_FILE.read_text().splitlines():
    line = line.strip()
    if '=' in line and not line.startswith('#'):
        k, _, v = line.partition('=')
        env[k.strip()] = v.strip().strip('"').strip("'")

FTP_HOST   = env.get('FTP_HOST', 'ftp.atmyboat.com')
FTP_USER   = env.get('FTP_USER', '')
FTP_PASS   = env.get('FTP_PASS', '')
REMOTE_DIR = '/staging/wp-content/themes/twentytwenty-child/mobile'

if not FTP_USER or not FTP_PASS:
    print('ERROR: FTP_USER or FTP_PASS missing in .env')
    sys.exit(1)

PHP_DIR = Path(__file__).parent.parent / 'php'
PHP_FILES = [
    'fleet-setup.php',
    'fleet-create.php',
    'fleet-join.php',
    'fleet-ingest.php',
    'fleet-map.php',
    'fleet-analytics.php',
]

def connect_ftp():
    print(f'Connecting to {FTP_HOST} as {FTP_USER}...')
    try:
        ftp = ftplib.FTP_TLS()
        ftp.connect(FTP_HOST, 21, timeout=30)
        ftp.login(FTP_USER, FTP_PASS)
        ftp.prot_p()
        print('  Connected (FTPS)')
        return ftp
    except ftplib.error_perm:
        print('  TLS rejected — trying plain FTP...')
        ftp = ftplib.FTP()
        ftp.connect(FTP_HOST, 21, timeout=30)
        ftp.login(FTP_USER, FTP_PASS)
        print('  Connected (plain FTP)')
        return ftp

def upload_file(ftp, local_path: Path, remote_path: str):
    with open(local_path, 'rb') as f:
        ftp.storbinary(f'STOR {remote_path}', f)
    print(f'  ✓ {local_path.name} → {remote_path}')

def main():
    # Verify all local files exist
    missing = [f for f in PHP_FILES if not (PHP_DIR / f).is_file()]
    if missing:
        print(f'ERROR: Missing PHP files: {missing}')
        sys.exit(1)

    ftp = connect_ftp()
    ftp.cwd(REMOTE_DIR)
    print(f'\nUploading to {FTP_HOST}{REMOTE_DIR}/')

    for filename in PHP_FILES:
        local  = PHP_DIR / filename
        remote = f'{REMOTE_DIR}/{filename}'
        upload_file(ftp, local, remote)

    ftp.quit()
    print(f'\nAll {len(PHP_FILES)} files deployed.')
    print('\nNext steps:')
    print('1. Open browser: https://atmyboat.com/staging/mobile/fleet-setup.php?action=create_tables&setup_key=YOUR_KEY')
    print('2. Confirm: { "success": true, "tables_created": [...] }')
    print('3. Seed test data: ?action=seed_test&setup_key=YOUR_KEY')
    print('4. Verify: ?action=verify&setup_key=YOUR_KEY')
    print('5. Run: python3 test_fleet_e2e.py')
    print('\nIMPORTANT: Add FLEET_SETUP_KEY=<secret> to config.php on HostPapa before running setup.')

if __name__ == '__main__':
    main()
