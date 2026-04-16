#!/usr/bin/env python3
"""
Deploy PWA files to HostPapa via FTPS.

Deploys to TWO targets:
  1. /app/          — live production (API_BASE → live PHP)
  2. /staging/app/  — staging (API_BASE → staging PHP, substituted at deploy time)

Reads FTP credentials from atmyboat-forum/.env

Usage: python3 deployment/v0.9.4/scripts/deploy-pwa.py
"""

import ftplib
import io
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

# ─── API_BASE values ─────────────────────────────────────────────────────────
LIVE_API_BASE    = 'https://atmyboat.com/wp-content/themes/twentytwenty-child/mobile'
STAGING_API_BASE = 'https://atmyboat.com/staging/wp-content/themes/twentytwenty-child/mobile'

# ─── Deploy targets ──────────────────────────────────────────────────────────
LOCAL_PWA = Path(__file__).parent.parent / 'pwa'

TARGETS = [
    {
        'label':    'Live    → /app/',
        'remote':   '/app',
        'api_base': LIVE_API_BASE,
    },
    {
        'label':    'Staging → /staging/app/',
        'remote':   '/staging/app',
        'api_base': STAGING_API_BASE,
    },
]

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


def make_app_js_bytes(api_base: str) -> bytes:
    """Read repo app.js and substitute API_BASE for the target environment."""
    source = (LOCAL_PWA / 'app.js').read_text(encoding='utf-8')
    # The repo source always carries the live API_BASE — substitute when needed
    result = source.replace(LIVE_API_BASE, api_base)
    return result.encode('utf-8')


def upload_dir(ftp, local_dir: Path, remote_dir: str, api_base: str):
    ensure_remote_dir(ftp, remote_dir)
    uploaded = 0
    for item in sorted(local_dir.iterdir()):
        if item.name in SKIP_NAMES:
            continue
        remote_path = remote_dir.rstrip('/') + '/' + item.name
        if item.is_dir():
            u = upload_dir(ftp, item, remote_path, api_base)
            uploaded += u
        elif item.is_file():
            try:
                if item.name == 'app.js':
                    # Substitute API_BASE for this environment
                    data = io.BytesIO(make_app_js_bytes(api_base))
                    ftp.storbinary(f'STOR {remote_path}', data)
                else:
                    with open(item, 'rb') as f:
                        ftp.storbinary(f'STOR {remote_path}', f)
                print(f"  UP  {item.name}")
                uploaded += 1
            except Exception as e:
                print(f"  ERR {item.name}: {e}")
    return uploaded


# ─── Main ────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("d3kOS PWA — Deploy (live + staging)")
    print("=" * 60)

    ftp = connect()

    for target in TARGETS:
        print(f"\n── {target['label']} ──")
        print(f"   API_BASE: {target['api_base']}")
        uploaded = upload_dir(ftp, LOCAL_PWA, target['remote'], target['api_base'])
        print(f"   {uploaded} files uploaded")

    ftp.quit()

    print()
    print("=" * 60)
    print("Done.")
    print("  Live PWA    : https://atmyboat.com/app/")
    print("  Staging PWA : https://atmyboat.com/staging/app/")
    print("=" * 60)


if __name__ == '__main__':
    main()
