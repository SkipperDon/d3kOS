#!/usr/bin/env python3
"""
Deploy PWA files to staging/app/ on HostPapa via FTPS.
Reads FTP credentials from atmyboat-forum/.env

Usage: python3 deployment/v0.9.4/scripts/deploy-pwa.py
"""

import ftplib
import sys
from pathlib import Path

# ─── Load .env from atmyboat-forum repo ──────────────────────────────────────
repo_root  = Path(__file__).parent.parent.parent.parent  # Helm-OS root
env_file   = repo_root.parent / 'atmyboat-forum' / '.env'

if not env_file.exists():
    print(f"ERROR: .env not found at {env_file}")
    print("       Copy atmyboat-forum/.env.example to .env and fill in credentials.")
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

# ─── What to deploy ──────────────────────────────────────────────────────────
LOCAL_PWA   = Path(__file__).parent.parent / 'pwa'
REMOTE_PWA  = '/staging/app'

SKIP_NAMES = {'.git', 'ICONS_NEEDED.md'}

# ─── FTP helpers ─────────────────────────────────────────────────────────────
def connect():
    print(f"Connecting to {FTP_HOST} as {FTP_USER}...")
    try:
        ftp = ftplib.FTP_TLS()
        ftp.connect(FTP_HOST, 21, timeout=30)
        ftp.login(FTP_USER, FTP_PASS)
        ftp.prot_p()
        print("  Connected (FTPS)")
        return ftp
    except ftplib.error_perm:
        print("  TLS rejected — trying plain FTP...")
        ftp = ftplib.FTP()
        ftp.connect(FTP_HOST, 21, timeout=30)
        ftp.login(FTP_USER, FTP_PASS)
        print("  Connected (plain FTP)")
        return ftp

def ensure_remote_dir(ftp, remote_path):
    parts = [p for p in remote_path.split('/') if p]
    current = ''
    for part in parts:
        current += '/' + part
        try:
            ftp.mkd(current)
        except ftplib.error_perm:
            pass  # already exists

def upload_dir(ftp, local_dir: Path, remote_dir: str):
    ensure_remote_dir(ftp, remote_dir)
    uploaded = 0
    for item in sorted(local_dir.iterdir()):
        if item.name in SKIP_NAMES:
            continue
        remote_path = remote_dir.rstrip('/') + '/' + item.name
        if item.is_dir():
            u = upload_dir(ftp, item, remote_path)
            uploaded += u
        elif item.is_file():
            try:
                with open(item, 'rb') as f:
                    ftp.storbinary(f'STOR {remote_path}', f)
                print(f"  UP  {item.relative_to(local_dir.parent)}")
                uploaded += 1
            except Exception as e:
                print(f"  ERR {item.name}: {e}")
    return uploaded

# ─── Main ────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("d3kOS PWA — Staging Deploy")
    print("=" * 60)
    print(f"Local:  {LOCAL_PWA}")
    print(f"Remote: {FTP_HOST}{REMOTE_PWA}")
    print()

    ftp = connect()
    print(f"\nDeploying PWA files...")
    uploaded = upload_dir(ftp, LOCAL_PWA, REMOTE_PWA)
    ftp.quit()

    print()
    print("=" * 60)
    print(f"Done. {uploaded} files uploaded.")
    print("=" * 60)
    print(f"\nPWA live at: https://atmyboat.com/staging/app/")

if __name__ == '__main__':
    main()
