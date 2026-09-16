"""
d3kOS OTA Update Agent — D23.

Polls HostPapa ota-queue.php every 60 seconds for pending OTA commands.
On receipt: verifies tier, downloads archive, checks SHA-256, backs up
current deployment, installs, and rolls back on health failure.

Config:  /opt/d3kos/config/cloud-config.json  (amboat_base_url)
License: /opt/d3kos/config/license.json       (tier)
Token:   /opt/d3kos/config/device-token.json  (device_token)

Signing: Ed25519 via device_sign.py — same pattern as tier_service.py.
"""

import hashlib
import json
import logging
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path

import requests

# ── Path setup ────────────────────────────────────────────────────────────────
# device_sign.py lives one level up from services/ota/
sys.path.insert(0, str(Path(__file__).parent.parent))
from device_sign import sign_device_request

# ── Constants ─────────────────────────────────────────────────────────────────
CLOUD_CONFIG_FILE   = Path('/opt/d3kos/config/cloud-config.json')
LICENSE_PATH        = Path('/opt/d3kos/config/license.json')
HARDWARE_PROFILE    = Path('/opt/d3kos/config/hardware-profile.json')
DEPLOY_ROOT         = Path('/opt/d3kos')
ROLLBACK_DIR        = Path('/opt/d3kos.ota-rollback')
HEALTH_URL          = 'http://localhost:3000/health'
OTA_PHP_SUFFIX      = '/wp-content/themes/twentytwenty-child/mobile/ota-queue.php'
POLL_INTERVAL       = 60   # seconds
REQUEST_TIMEOUT     = 30   # seconds

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [d3kos-ota-agent] %(levelname)s %(message)s',
    stream=sys.stdout,
)
logger = logging.getLogger('d3kos-ota-agent')


# ── Tier gate (§5 — verbatim from spec) ──────────────────────────────────────

def _check_tier() -> bool:
    """Return True if tier >= 1, False if T0 or file unreadable."""
    try:
        with open(LICENSE_PATH) as f:
            data = json.load(f)
        return int(data.get('tier', 0)) >= 1
    except Exception:
        return False  # fail closed — no OTA if license unreadable


# ── Config ────────────────────────────────────────────────────────────────────

def _load_base_url() -> tuple[str, str] | tuple[None, None]:
    """Return (origin, ota_php_path) derived from cloud-config.json.

    origin   = scheme + netloc only (e.g. 'https://atmyboat.com')
    php_path = full URI path including any environment prefix
               (e.g. '/staging/wp-content/.../ota-queue.php' for staging,
                     '/wp-content/.../ota-queue.php' for production)

    _peek / _ack / _post_result construct the final URL as origin + php_path.
    The signed path equals php_path, which matches REQUEST_URI on the server.
    """
    try:
        with open(CLOUD_CONFIG_FILE) as f:
            cfg = json.load(f)
        url = cfg.get('amboat_base_url', '').rstrip('/')
        if not url:
            return None, None
        from urllib.parse import urlparse
        parsed = urlparse(url)
        origin   = f'{parsed.scheme}://{parsed.netloc}'
        prefix   = parsed.path.rstrip('/')
        php_path = prefix + OTA_PHP_SUFFIX
        return origin, php_path
    except Exception as e:
        logger.error(f'Failed to read cloud-config.json: {e}')
        return None, None


def _get_hardware_profile_version() -> str:
    try:
        with open(HARDWARE_PROFILE) as f:
            data = json.load(f)
        return str(data.get('probe_version', 'unknown'))
    except FileNotFoundError:
        return 'unknown'
    except Exception:
        return 'unknown'


# ── SHA-256 verification ──────────────────────────────────────────────────────

def _verify_sha256(file_path: Path, expected_hex: str) -> bool:
    sha = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            sha.update(chunk)
    return sha.hexdigest() == expected_hex.lower()


# ── Command schema validation ─────────────────────────────────────────────────

def _parse_command(raw: dict) -> dict:
    """Validate command shape. Raises ValueError for wrong type or missing keys."""
    if raw.get('command_type') != 'ota_install':
        raise ValueError(f"Unexpected command_type: {raw.get('command_type')!r}")
    payload = raw.get('payload', {})
    for key in ('version', 'download_url', 'sha256'):
        if key not in payload:
            raise ValueError(f"Missing payload key: {key!r}")
    return raw


# ── Result payload ────────────────────────────────────────────────────────────

def _build_result_payload(command_id: int, pi_id: str, status: str,
                           version_installed: str = '',
                           detail: str = '') -> dict:
    payload = {
        'command_id':              command_id,
        'pi_id':                   pi_id,
        'status':                  status,
        'version_installed':       version_installed,
        'hardware_profile_version': _get_hardware_profile_version(),
    }
    if detail:
        payload['detail'] = detail
    return payload


# ── HostPapa HTTP helpers ─────────────────────────────────────────────────────

def _signed_headers(php_path: str) -> dict:
    """Ed25519 headers for Pi→HostPapa request."""
    hdrs = sign_device_request(php_path)
    hdrs['User-Agent'] = 'Mozilla/5.0'  # nginx on HostPapa blocks python-requests UA (BUG-56)
    hdrs['Content-Type'] = 'application/json'
    return hdrs


def _peek(base_url: str, php_path: str, pi_id: str) -> dict | None:
    """Fetch oldest pending command. Returns raw dict or None."""
    url = base_url + php_path
    try:
        r = requests.get(
            url,
            params={'action': 'peek', 'pi_id': pi_id},
            headers=_signed_headers(php_path),
            timeout=REQUEST_TIMEOUT,
        )
        if r.status_code == 200:
            body = r.json()
            if body.get('status') == 'none':
                return None
            return body.get('command')
        logger.warning(f'peek HTTP {r.status_code}: {r.text[:120]}')
    except requests.exceptions.ConnectionError:
        logger.debug('ota-queue.php unreachable — offline?')
    except Exception as e:
        logger.error(f'peek error: {e}')
    return None


def _ack(base_url: str, php_path: str, command_id: int) -> None:
    url = base_url + php_path
    try:
        requests.post(
            url,
            json={'action': 'ack', 'command_id': command_id},
            headers=_signed_headers(php_path),
            timeout=REQUEST_TIMEOUT,
        )
    except Exception as e:
        logger.warning(f'ack error (non-fatal): {e}')


def _post_result(base_url: str, php_path: str, payload: dict) -> None:
    url = base_url + php_path
    try:
        requests.post(
            url,
            json={'action': 'result', **payload},
            headers=_signed_headers(php_path),
            timeout=REQUEST_TIMEOUT,
        )
    except Exception as e:
        logger.warning(f'post_result error (non-fatal): {e}')


# ── Service control helpers ───────────────────────────────────────────────────

def _d3kos_services() -> list[str]:
    """Return active d3kos-*.service units, excluding this agent."""
    try:
        out = subprocess.check_output(
            ['systemctl', 'list-units', '--type=service', '--state=active',
             '--no-legend', '--no-pager'],
            text=True,
        )
        units = []
        for line in out.splitlines():
            name = line.split()[0]
            if name.startswith('d3kos-') and name != 'd3kos-ota-agent.service':
                units.append(name)
        return units
    except Exception as e:
        logger.warning(f'Failed to list d3kos services: {e}')
        return []


def _stop_services(units: list[str]) -> None:
    if units:
        subprocess.run(['systemctl', 'stop'] + units, check=False)


def _start_services(units: list[str]) -> None:
    if units:
        subprocess.run(['systemctl', 'daemon-reload'], check=False)
        subprocess.run(['systemctl', 'start'] + units, check=False)


def _health_check(attempts: int = 5, interval: int = 5) -> bool:
    for i in range(attempts):
        try:
            r = requests.get(HEALTH_URL, timeout=10)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        if i < attempts - 1:
            time.sleep(interval)
    return False


# ── Rollback ──────────────────────────────────────────────────────────────────

def _rollback(units: list[str], detail: str) -> None:
    logger.error(f'Health check failed — rolling back. {detail}')
    _stop_services(units)
    shutil.rmtree(DEPLOY_ROOT, ignore_errors=True)
    if ROLLBACK_DIR.exists():
        ROLLBACK_DIR.rename(DEPLOY_ROOT)
    subprocess.run(['systemctl', 'daemon-reload'], check=False)
    _start_services(units)


# ── Install flow (§3.3) ───────────────────────────────────────────────────────

def _install(base_url: str, php_path: str, pi_id: str, cmd: dict) -> None:
    command_id = cmd['command_id']
    payload    = cmd['payload']
    version    = payload['version']
    url        = payload['download_url']
    sha256     = payload['sha256']

    # Step 2: T1+ gate
    if not _check_tier():
        logger.warning('OTA blocked: tier insufficient (T0)')
        _post_result(base_url, php_path, _build_result_payload(
            command_id, pi_id, 'tier_insufficient',
            detail='OTA requires Tier 1 or higher. Visit atmyboat.com to upgrade.',
        ))
        return

    # Step 3: ACK
    _ack(base_url, php_path, command_id)

    # Step 4: Download
    archive = Path(tempfile.gettempdir()) / f'd3kos-ota-{version}.tar.gz'
    logger.info(f'Downloading OTA {version} from {url}')
    try:
        with requests.get(url, stream=True, timeout=REQUEST_TIMEOUT) as r:
            r.raise_for_status()
            with open(archive, 'wb') as f:
                for chunk in r.iter_content(65536):
                    f.write(chunk)
    except Exception as e:
        logger.error(f'Download failed: {e}')
        _post_result(base_url, php_path, _build_result_payload(
            command_id, pi_id, 'download_fail', detail=str(e),
        ))
        archive.unlink(missing_ok=True)
        return

    # Step 5: SHA-256 verify
    if not _verify_sha256(archive, sha256):
        logger.error('SHA-256 mismatch — aborting install')
        _post_result(base_url, php_path, _build_result_payload(
            command_id, pi_id, 'checksum_fail',
            detail='Archive SHA-256 did not match the expected value.',
        ))
        archive.unlink(missing_ok=True)
        return

    # Step 6: Backup
    logger.info('Backing up current deployment')
    if ROLLBACK_DIR.exists():
        shutil.rmtree(ROLLBACK_DIR)
    shutil.copytree(DEPLOY_ROOT, ROLLBACK_DIR)

    # Step 7: Extract to staging
    stage = Path(tempfile.gettempdir()) / 'd3kos-ota-stage'
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir()
    try:
        with tarfile.open(archive, 'r:gz') as tf:
            tf.extractall(stage)
    except Exception as e:
        logger.error(f'Extraction failed: {e}')
        _post_result(base_url, php_path, _build_result_payload(
            command_id, pi_id, 'extract_fail', detail=str(e),
        ))
        shutil.rmtree(stage, ignore_errors=True)
        archive.unlink(missing_ok=True)
        shutil.rmtree(ROLLBACK_DIR, ignore_errors=True)
        return

    # Step 8: Stop services
    units = _d3kos_services()
    logger.info(f'Stopping services: {units}')
    _stop_services(units)

    # Step 9: rsync
    subprocess.run(
        ['rsync', '--archive', '--delete',
         str(stage) + '/', str(DEPLOY_ROOT) + '/'],
        check=True,
    )

    # Step 10: daemon-reload
    subprocess.run(['systemctl', 'daemon-reload'], check=False)

    # Step 11: Start services
    logger.info('Starting services')
    _start_services(units)

    # Step 12: Health check
    logger.info('Running health check')
    if _health_check():
        # Step 13a: Success
        logger.info(f'OTA {version} installed successfully')
        _post_result(base_url, php_path, _build_result_payload(
            command_id, pi_id, 'success', version_installed=version,
        ))
        # Step 14: Cleanup
        archive.unlink(missing_ok=True)
        shutil.rmtree(stage, ignore_errors=True)
        shutil.rmtree(ROLLBACK_DIR, ignore_errors=True)
    else:
        # Step 13b: Rollback
        _rollback(units, f'Health check failed after installing {version}')
        _post_result(base_url, php_path, _build_result_payload(
            command_id, pi_id, 'rollback_complete',
            detail=f'Health check failed after installing {version}; rolled back.',
        ))
        archive.unlink(missing_ok=True)
        shutil.rmtree(stage, ignore_errors=True)


# ── Main poll loop ────────────────────────────────────────────────────────────

def main() -> None:
    logger.info('d3kOS OTA agent starting (D23)')

    while True:
        try:
            base_url, php_path = _load_base_url()
            if not base_url:
                logger.warning('amboat_base_url not set — skipping poll')
            else:
                try:
                    from device_sign import _load_device_token
                    pi_id = _load_device_token()
                except Exception as e:
                    logger.warning(f'Cannot load device token: {e}')
                    pi_id = None

                if pi_id:
                    raw = _peek(base_url, php_path, pi_id)
                    if raw:
                        try:
                            cmd = _parse_command(raw)
                        except ValueError as e:
                            logger.warning(f'Ignored command: {e}')
                            cmd = None
                        if cmd:
                            _install(base_url, php_path, pi_id, cmd)
        except Exception as e:
            logger.error(f'Unexpected error in poll loop: {e}')

        time.sleep(POLL_INTERVAL)


if __name__ == '__main__':
    main()
