#!/usr/bin/env python3
"""
BUG-63 Step 3 deployment — FTP upload to live atmyboat.com.

Deploys:
  page-register.php       → public_html/wp-content/themes/twentytwenty-child/
  device-registration.php → public_html/wp-content/themes/twentytwenty-child/
  cleanup-botnet-accounts.php → public_html/wp-content/themes/twentytwenty-child/mobile/
"""

import ftplib
import ssl
import sys

FTP_HOST = 'ftp.atmyboat.com'
FTP_PORT = 21
FTP_USER = 'd3kos@atmyboat.com'
FTP_PASS = '*].MMQ{^s-1WxNy='

REPO = '/home/boatiq/Helm-OS'

UPLOADS = [
    (
        f'{REPO}/deployment/features/auth-pages/php/page-register.php',
        'wp-content/themes/twentytwenty-child/page-register.php',
    ),
    (
        f'{REPO}/deployment/features/auth-pages/php/device-registration.php',
        'wp-content/themes/twentytwenty-child/device-registration.php',
    ),
    (
        f'{REPO}/deployment/v0.9.9.4-server/tools/cleanup-botnet-accounts.php',
        'wp-content/themes/twentytwenty-child/mobile/cleanup-botnet-accounts.php',
    ),
]

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

print(f'Connecting to {FTP_HOST}:{FTP_PORT} as {FTP_USER}...')
ftp = ftplib.FTP_TLS(context=ctx)
ftp.connect(FTP_HOST, FTP_PORT, timeout=30)
ftp.login(FTP_USER, FTP_PASS)
ftp.prot_p()
print('Connected OK\n')

errors = []
for local_path, remote_path in UPLOADS:
    try:
        with open(local_path, 'rb') as f:
            ftp.storbinary(f'STOR {remote_path}', f)
        print(f'  OK: {remote_path}')
    except Exception as e:
        msg = f'  FAIL: {remote_path} — {e}'
        print(msg)
        errors.append(msg)

ftp.quit()
print()

if errors:
    print('ERRORS:')
    for e in errors:
        print(e)
    sys.exit(1)
else:
    print('All files uploaded successfully.')
    print()
    print('Next steps:')
    print('  1. DRY RUN:  browse to https://atmyboat.com/wp-content/themes/twentytwenty-child/mobile/cleanup-botnet-accounts.php')
    print('     Review the count of candidate accounts.')
    print('  2. LIVE RUN: append ?run=1 to execute deletion + republish /register/')
    print('  3. Verify /register/ is live at https://atmyboat.com/register/')
    print('  4. DELETE the cleanup script: run delete-cleanup-script.py')
