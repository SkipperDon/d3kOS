#!/usr/bin/env python3
"""
d3kOS OTA Upgrade Script
Invoked by cloud_agent.py when an ota_upgrade command is received from AtMyBoat.com.

Flow:
  1. Fetch latest release info from AtMyBoat.com version-registry.php
  2. Compare to current installed version — skip if already up to date
  3. Download release zip to /tmp/d3kos-ota/
  4. Verify SHA-256 checksum
  5. Back up current /opt/d3kos/services/ to /opt/d3kos/.ota-backup/
  6. Extract and install new files
  7. Restart all d3kOS services
  8. Verify services are running — rollback on failure

Returns dict: { ok, old_version, new_version, actions_taken, errors, timestamp }

Author: d3kOS Team
Version: 0.9.4
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import zipfile
from datetime import datetime
from pathlib import Path

import requests

# ── Paths ─────────────────────────────────────────────────────────────────────
SERVICES_DIR    = Path('/opt/d3kos/services')
CONFIG_DIR      = Path('/opt/d3kos/config')
VERSION_FILE    = Path('/opt/d3kos/config/version.txt')
BACKUP_DIR      = Path('/opt/d3kos/.ota-backup')
STAGE_DIR       = Path('/tmp/d3kos-ota')

# ── Services to restart after upgrade ─────────────────────────────────────────
MANAGED_SERVICES = [
    'd3kos-cloud-agent',
    'd3kos-export-manager',
    'd3kos-tier',
]


def get_current_version():
    """Read installed version from version.txt."""
    try:
        for line in VERSION_FILE.read_text().strip().splitlines():
            if 'Version' in line:
                return line.split()[-1].strip()
    except Exception:
        pass
    return 'unknown'


def write_version_file(new_version, release=None):
    """Rewrite version.txt preserving every field.

    Updates 'd3kOS Version' and 'Build' from new_version. Takes
    'Release Date' and 'Status' from the release manifest when it
    supplies them, otherwise PRESERVES the existing values. Never
    invents a date. BUG-35.
    """
    release = release or {}
    fields = {
        'd3kOS Version': None,
        'Release Date':  None,
        'Status':        None,
        'Build':         None,
    }
    # read whatever is currently there
    try:
        for line in VERSION_FILE.read_text().splitlines():
            line = line.strip()
            if line.startswith('d3kOS Version'):
                fields['d3kOS Version'] = line.replace('d3kOS Version', '').strip()
            elif line.startswith('Release Date:'):
                fields['Release Date'] = line.replace('Release Date:', '').strip()
            elif line.startswith('Status:'):
                fields['Status'] = line.replace('Status:', '').strip()
            elif line.startswith('Build:'):
                fields['Build'] = line.replace('Build:', '').strip()
    except Exception:
        pass                      # missing/unreadable file -> fall through to defaults

    fields['d3kOS Version'] = str(new_version)
    fields['Build'] = 'v' + str(new_version)
    if release.get('release_date'):
        fields['Release Date'] = str(release['release_date'])
    if release.get('status'):
        fields['Status'] = str(release['status'])
    if not fields['Release Date']:
        fields['Release Date'] = 'unknown'
    if not fields['Status']:
        fields['Status'] = 'unknown'

    VERSION_FILE.write_text(
        "d3kOS Version {}\nRelease Date: {}\nStatus: {}\nBuild: {}\n".format(
            fields['d3kOS Version'], fields['Release Date'],
            fields['Status'], fields['Build']))


def fetch_latest_release(base_url, api_key, device_token):
    """
    Ask AtMyBoat.com version-registry.php for the latest available release.
    Returns dict: { version, download_url, sha256 } or raises on failure.
    """
    url = f"{base_url}/wp-content/themes/twentytwenty-child/mobile/version-registry.php"
    headers = {
        'Authorization':  f'Bearer {api_key}',
        'X-Device-Token': device_token,
        'Content-Type':   'application/json',
    }
    r = requests.get(url, headers=headers, timeout=15)
    if r.status_code != 200:
        raise RuntimeError(f'version-registry.php returned HTTP {r.status_code}: {r.text[:100]}')

    body = r.json()
    if not body.get('success'):
        raise RuntimeError(f"version-registry.php error: {body.get('error', 'unknown')}")

    data = body.get('data', {})
    release = data.get('latest_release')
    if not release:
        raise RuntimeError('version-registry.php returned no latest_release')

    return release  # expects { version, download_url, sha256 }


def download_release(download_url, expected_sha256):
    """Download release zip to STAGE_DIR, verify SHA-256. Returns Path to zip."""
    STAGE_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = STAGE_DIR / 'd3kos-upgrade.zip'

    if zip_path.exists():
        zip_path.unlink()

    with requests.get(download_url, stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(zip_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=65536):
                if chunk:
                    f.write(chunk)

    # Verify SHA-256
    sha = hashlib.sha256()
    with open(zip_path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            sha.update(chunk)
    actual = sha.hexdigest().lower()
    expected = expected_sha256.lower()

    if actual != expected:
        zip_path.unlink()
        raise RuntimeError(
            f'SHA-256 mismatch. Expected {expected[:16]}… got {actual[:16]}…'
        )

    return zip_path


def backup_services():
    """Back up current /opt/d3kos/services to BACKUP_DIR/services-<timestamp>."""
    ts = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    backup_path = BACKUP_DIR / f'services-{ts}'
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    if SERVICES_DIR.exists():
        shutil.copytree(str(SERVICES_DIR), str(backup_path))

    return backup_path


def stop_services():
    """Stop all managed services. Returns list of (service, success, msg)."""
    results = []
    for svc in MANAGED_SERVICES:
        rc, out, err = _run(['sudo', 'systemctl', 'stop', svc], timeout=20)
        results.append((svc, rc == 0, err or out))
    return results


def start_services():
    """Start all managed services. Returns list of (service, active, state)."""
    results = []
    for svc in MANAGED_SERVICES:
        _run(['sudo', 'systemctl', 'start', svc], timeout=20)
        time.sleep(1)
        rc, state_out, _ = _run(['systemctl', 'is-active', svc])
        state = state_out.strip()
        results.append((svc, state == 'active', state))
    return results


def install_release(zip_path):
    """Extract zip to STAGE_DIR/extracted and copy service files to SERVICES_DIR."""
    extract_dir = STAGE_DIR / 'extracted'
    if extract_dir.exists():
        shutil.rmtree(extract_dir)

    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(extract_dir)

    # Find the services/ directory inside the archive
    # Expected structure: d3kos-vX.Y.Z/services/
    services_src = None
    for candidate in extract_dir.rglob('services'):
        if candidate.is_dir():
            services_src = candidate
            break

    if not services_src:
        raise RuntimeError(
            'Release zip does not contain a services/ directory. '
            'Expected: d3kos-vX.Y.Z/services/ inside the archive.'
        )

    # Overwrite service files
    for item in services_src.iterdir():
        dest = SERVICES_DIR / item.name
        if item.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(str(item), str(dest))
        else:
            shutil.copy2(str(item), str(dest))


def rollback(backup_path):
    """Restore services from backup. Returns (success, msg)."""
    try:
        if SERVICES_DIR.exists():
            shutil.rmtree(SERVICES_DIR)
        shutil.copytree(str(backup_path), str(SERVICES_DIR))
        return True, f'Rolled back to {backup_path.name}'
    except Exception as e:
        return False, f'Rollback failed: {e}'


def _run(cmd, timeout=15):
    """Run shell command, return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, '', f'Timeout after {timeout}s'
    except Exception as e:
        return -1, '', str(e)


def run_upgrade(base_url, api_key, device_token):
    """
    Execute full OTA upgrade sequence.
    Returns dict: { ok, old_version, new_version, actions_taken, errors, timestamp }
    """
    actions = []
    errors  = []
    backup_path = None

    old_version = get_current_version()
    new_version = old_version  # updated after successful install

    try:
        # 1. Fetch release info
        actions.append('Fetching release info from AtMyBoat.com...')
        release = fetch_latest_release(base_url, api_key, device_token)
        latest_ver = release.get('version', 'unknown')

        # 2. Check if update is needed
        if latest_ver == old_version:
            actions.append(f'Already at latest version ({old_version}). No upgrade needed.')
            return {
                'ok':            True,
                'old_version':   old_version,
                'new_version':   old_version,
                'up_to_date':    True,
                'actions_taken': actions,
                'errors':        errors,
                'timestamp':     datetime.utcnow().isoformat() + 'Z',
            }

        download_url     = release.get('download_url')
        expected_sha256  = release.get('sha256', '')

        if not download_url:
            raise RuntimeError('Release info missing download_url.')
        if not expected_sha256:
            raise RuntimeError(
                f'No SHA-256 checksum available for {latest_ver}. '
                'The server administrator must set the sha256 field in version-registry.php '
                'before OTA upgrades can be enabled. Download will not proceed without verification.'
            )

        actions.append(f'Upgrading {old_version} → {latest_ver}')

        # 3. Download and verify
        actions.append(f'Downloading release from {download_url[:60]}...')
        zip_path = download_release(download_url, expected_sha256)
        actions.append(f'Download complete. SHA-256 verified.')

        # 4. Back up current services
        backup_path = backup_services()
        actions.append(f'Backup created: {backup_path}')

        # 5. Stop services
        stop_results = stop_services()
        for svc, ok, msg in stop_results:
            actions.append(f'Stopped {svc}: {"ok" if ok else msg}')

        # 6. Install new files
        actions.append('Installing new release...')
        install_release(zip_path)
        actions.append('Files installed.')

        # 7. Update version.txt
        try:
            write_version_file(latest_ver, release)     # BUG-35: preserve all four fields
        except Exception as e:
            errors.append(f'Could not update version.txt: {e}')

        # 8. Start services and verify
        actions.append('Starting services...')
        start_results = start_services()
        failed_services = [(svc, state) for svc, ok, state in start_results if not ok]

        if failed_services:
            raise RuntimeError(
                f'Services failed to start after upgrade: '
                + ', '.join(f'{s}={st}' for s, st in failed_services)
            )

        for svc, ok, state in start_results:
            actions.append(f'Service {svc}: {state}')

        # 9. Clean up staging dir
        try:
            shutil.rmtree(STAGE_DIR)
        except Exception:
            pass

        new_version = latest_ver

        return {
            'ok':            True,
            'old_version':   old_version,
            'new_version':   new_version,
            'actions_taken': actions,
            'errors':        errors,
            'timestamp':     datetime.utcnow().isoformat() + 'Z',
        }

    except Exception as exc:
        errors.append(str(exc))

        # Attempt rollback if we got past the backup stage
        if backup_path and backup_path.exists():
            actions.append('Attempting rollback...')
            rb_ok, rb_msg = rollback(backup_path)
            actions.append(f'Rollback: {rb_msg}')

            if rb_ok:
                # Restart services from rollback
                start_results = start_services()
                for svc, ok, state in start_results:
                    actions.append(f'Post-rollback {svc}: {state}')

        return {
            'ok':            False,
            'old_version':   old_version,
            'new_version':   new_version,
            'actions_taken': actions,
            'errors':        errors,
            'timestamp':     datetime.utcnow().isoformat() + 'Z',
        }


if __name__ == '__main__':
    # Standalone test — reads config from standard paths
    cfg_path = Path('/opt/d3kos/config/cloud-config.json')
    tok_path = Path('/opt/d3kos/config/device-token.json')

    with open(cfg_path) as f:
        cfg = json.load(f)
    with open(tok_path) as f:
        tok = json.load(f)

    result = run_upgrade(
        base_url=cfg.get('amboat_base_url', 'https://atmyboat.com').rstrip('/'),
        api_key=cfg['amboat_api_key'],
        device_token=tok['device_token'],
    )
    print(json.dumps(result, indent=2))
