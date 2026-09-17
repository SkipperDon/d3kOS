#!/usr/bin/env python3
"""
Deploy D23 sodium_compat fix to HostPapa staging.
Uploads device-auth.php + sodium_compat/ folder to:
  /staging/wp-content/themes/twentytwenty-child/mobile/

Credentials from /home/boatiq/atmyboat-forum/.env
"""

import ftplib
import os
import sys
from pathlib import Path

# ─── Load credentials from atmyboat-forum .env ───────────────────────────────
env_file = Path('/home/boatiq/atmyboat-forum/.env')
if not env_file.exists():
    print("ERROR: .env not found at", env_file)
    sys.exit(1)

env = {}
for line in env_file.read_text().splitlines():
    line = line.strip()
    if line and not line.startswith('#') and '=' in line:
        k, v = line.split('=', 1)
        env[k.strip()] = v.strip()

FTP_HOST = env.get('FTP_HOST', 'ftp.atmyboat.com')
FTP_USER = env.get('FTP_USER', '')
FTP_PASS = env.get('FTP_PASS', '')

if not FTP_USER or not FTP_PASS:
    print("ERROR: FTP_USER or FTP_PASS missing in .env")
    sys.exit(1)

# ─── Paths ────────────────────────────────────────────────────────────────────
REPO_MOBILE   = Path('/home/boatiq/Helm-OS/deployment/v0.9.9.4-server/mobile')
REMOTE_MOBILE = '/staging/wp-content/themes/twentytwenty-child/mobile'

# ─── FTP helpers ─────────────────────────────────────────────────────────────
def connect():
    print(f"Connecting to {FTP_HOST} as {FTP_USER}...")
    ftp = ftplib.FTP_TLS()
    ftp.connect(FTP_HOST, 21, timeout=30)
    ftp.login(FTP_USER, FTP_PASS)
    ftp.prot_p()
    ftp.set_pasv(True)
    print("  Connected (FTPS)")
    return ftp

def ensure_remote_dir(ftp, remote_dir):
    parts = remote_dir.rstrip('/').split('/')
    path = ''
    for part in parts:
        if not part:
            path = '/'
            continue
        path = path.rstrip('/') + '/' + part
        try:
            ftp.mkd(path)
        except ftplib.error_perm:
            pass  # already exists

def upload_file(ftp, local_path, remote_path):
    with open(local_path, 'rb') as f:
        ftp.storbinary(f'STOR {remote_path}', f)
    print(f"  ✓ {remote_path}")

def upload_tree(ftp, local_dir, remote_dir):
    ensure_remote_dir(ftp, remote_dir)
    for item in sorted(local_dir.iterdir()):
        if item.name.startswith('.'):
            continue
        remote_item = remote_dir.rstrip('/') + '/' + item.name
        if item.is_dir():
            upload_tree(ftp, item, remote_item)
        else:
            upload_file(ftp, item, remote_item)

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    ftp = connect()

    print(f"\nUploading device-auth.php...")
    upload_file(ftp, REPO_MOBILE / 'device-auth.php',
                REMOTE_MOBILE + '/device-auth.php')

    print(f"\nUploading sodium_compat/ (77 files)...")
    upload_tree(ftp, REPO_MOBILE / 'sodium_compat',
                REMOTE_MOBILE + '/sodium_compat')

    ftp.quit()
    print("\nDone. Next step: verify ImunifyAV did not quarantine sodium_compat/")
    print(f"  Test URL: https://staging.atmyboat.com/wp-content/themes/twentytwenty-child/mobile/sodium_compat/autoload.php")

if __name__ == '__main__':
    main()
