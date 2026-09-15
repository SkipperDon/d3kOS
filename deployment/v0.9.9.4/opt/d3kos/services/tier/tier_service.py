#!/usr/bin/env python3
"""
d3kOS Tier Service
Port 8093 — reads license.json, returns tier + feature flags

GET /tier/status              → { tier, installation_id, features, version }
GET /tier/feature/<name>      → { feature, enabled }
GET /health

Author: d3kOS Team
Version: 0.9.5 — added predictive_alerts (T1+) and maintenance_schedule (T2+)
"""

import json
import logging
import os
import sys
import time
from pathlib import Path

from flask import Flask, jsonify

# device_sign lives one directory above this service's tier/ subdirectory
sys.path.insert(0, str(Path(__file__).parent.parent))

app = Flask(__name__)

LICENSE_FILE       = Path('/opt/d3kos/config/license.json')
CLOUD_CONFIG_FILE  = Path('/opt/d3kos/config/cloud-config.json')
APPROVAL_CACHE     = Path('/opt/d3kos/state/tier1-approval.json')
SUBSCRIPTION_KEY   = Path('/opt/d3kos/config/subscription.key')
TOKEN_FILE         = Path('/opt/d3kos/config/device-token.json')
APPROVAL_POLL_MIN  = 15
PORT               = 8093

OPENCPN_PATHS = (
    '/usr/bin/opencpn',
    '/usr/local/bin/opencpn',
    '/opt/opencpn/bin/opencpn',
)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('tier-service')

def _parse_tier(raw):
    """Parse tier from license.json — handles int (0) and string ('T0') formats."""
    if isinstance(raw, str) and raw.upper().startswith('T'):
        try:
            return int(raw[1:])
        except (ValueError, IndexError):
            return 0
    try:
        return int(raw)
    except (TypeError, ValueError):
        return 0



# Feature matrix per tier — mirrors data-ingress.php feature_matrix
FEATURE_MATRIX = {
    0: {
        'mobile_app':           False,
        'find_my_boat':         False,
        'engine_monitoring':    False,
        'ota_upgrades':         False,
        'anchor_alerts':        False,
        'engine_alerts':        False,
        'community_map':        False,
        'fix_my_pi':            'paid',
        'pdf_reports':          False,
        'sms_alerts':           False,
        'multiple_phones':      False,
        'fleet_management':     False,
        'cloud_sync':           False,
        'camera':               False,
        'voice_assistant':      False,
        'predictive_alerts':    False,
        'maintenance_schedule': False,
    },
    1: {
        'mobile_app':           True,
        'find_my_boat':         True,
        'engine_monitoring':    True,
        'ota_upgrades':         True,
        'anchor_alerts':        True,
        'engine_alerts':        True,
        'community_map':        True,
        'fix_my_pi':            'paid',
        'pdf_reports':          False,
        'sms_alerts':           False,
        'multiple_phones':      False,
        'fleet_management':     False,
        'cloud_sync':           True,
        'camera':               True,
        'voice_assistant':      True,
        'predictive_alerts':    True,
        'maintenance_schedule': False,
    },
    2: {
        'mobile_app':           True,
        'find_my_boat':         True,
        'engine_monitoring':    True,
        'ota_upgrades':         True,
        'anchor_alerts':        True,
        'engine_alerts':        True,
        'community_map':        True,
        'fix_my_pi':            '3_per_month',
        'pdf_reports':          True,
        'sms_alerts':           True,
        'multiple_phones':      True,
        'fleet_management':     False,
        'cloud_sync':           True,
        'camera':               True,
        'voice_assistant':      True,
        'predictive_alerts':    True,
        'maintenance_schedule': True,
    },
    3: {
        'mobile_app':           True,
        'find_my_boat':         True,
        'engine_monitoring':    True,
        'ota_upgrades':         True,
        'anchor_alerts':        True,
        'engine_alerts':        True,
        'community_map':        True,
        'fix_my_pi':            'unlimited',
        'pdf_reports':          True,
        'sms_alerts':           True,
        'multiple_phones':      True,
        'fleet_management':     True,
        'cloud_sync':           True,
        'camera':               True,
        'voice_assistant':      True,
        'predictive_alerts':    True,
        'maintenance_schedule': True,
    },
}


def load_license():
    try:
        with open(LICENSE_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f'license.json not found at {LICENSE_FILE}')
        return None
    except Exception as e:
        logger.error(f'Failed to read license.json: {e}')
        return None


def device_is_paired_and_approved() -> bool:
    """
    Returns True only when the server confirms this device has status 'approved'.

    Rules (non-negotiable — see BUG-77 spec):
    - 'pending' is NOT Tier 1; only the literal string 'approved' grants it.
    - Server unreachable → cached result stands (offline-first; vessel at sea must not lose tier).
    - No cache + server unreachable → False (fail closed; never fail open with no evidence).
    - Polls at most once per APPROVAL_POLL_MIN minutes.
    - Cache written mode 600 (only root/d3kos can read).
    - Logs cache staleness explicitly — no silent degradation.
    """
    if not TOKEN_FILE.exists():
        logger.info('tier1-check: device-token.json absent — Tier 0 (device not enrolled)')
        return False

    now = time.time()
    cached_approved = None
    try:
        if APPROVAL_CACHE.exists():
            cache = json.loads(APPROVAL_CACHE.read_text())
            cached_at = cache.get('cached_at', 0)
            cached_approved = cache.get('approved', False)
            age_min = (now - cached_at) / 60
            if age_min < APPROVAL_POLL_MIN:
                return cached_approved
            logger.info(f'tier1-check: cache stale ({age_min:.1f} min) — polling server')
    except Exception as e:
        logger.warning(f'tier1-check: cache read error: {e}')

    try:
        cloud_cfg = json.loads(CLOUD_CONFIG_FILE.read_text())
        base_url = cloud_cfg.get('amboat_base_url', 'https://atmyboat.com').rstrip('/')
    except Exception as e:
        logger.warning(f'tier1-check: cloud-config.json unreadable: {e}')
        if cached_approved is not None:
            logger.warning('tier1-check: cloud-config unreadable — keeping cached result')
            return cached_approved
        return False

    try:
        from device_sign import sign_device_request
        import requests as req_lib
        # Signed message must use the route as WordPress's REST API sees it
        # (no /wp-json prefix — that's the REST mount point, not part of the route).
        # auto_enrol.py signs '/amboat-device/v1/enrol' the same way; that call verifies.
        route = '/amboat-device/v1/status'
        request_path = f'/wp-json{route}'
        headers = sign_device_request(route)
        headers['User-Agent'] = 'd3kOS/0.9.9.4 (tier-check)'
        resp = req_lib.get(f'{base_url}{request_path}', headers=headers, timeout=10)
        resp.raise_for_status()
        status = resp.json().get('status', 'unknown')
        approved = (status == 'approved')
    except Exception as e:
        logger.warning(f'tier1-check: server unreachable ({type(e).__name__}): {e}')
        if cached_approved is not None:
            logger.warning('tier1-check: server down — keeping cached result '
                           f'(approved={cached_approved})')
            return cached_approved
        logger.warning('tier1-check: no cache + server down — returning False (fail closed, '
                       'nothing to trust)')
        return False

    try:
        APPROVAL_CACHE.parent.mkdir(parents=True, exist_ok=True)
        cache_data = json.dumps({'approved': approved, 'status': status, 'cached_at': now})
        fd = os.open(APPROVAL_CACHE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, 'w') as f:
            f.write(cache_data)
    except Exception as e:
        logger.warning(f'tier1-check: cache write error: {e}')

    return approved


def detect_tier() -> int:
    """
    Detect device tier in priority order (highest first).

    Tier 3: subscription.key present (filesystem test — forgeable, BUG-65 tracks hardening)
    Tier 2: OpenCPN installed at any known path
    Tier 1: server-verified approval via /wp-json/amboat-device/v1/status (BUG-77 fix)
    Tier 0: none of the above

    license.json is NOT consulted here — it is forged too easily (T8 trust-anchor test).
    Feature matrix and installation_id are still sourced from load_license() in the route.
    """
    if SUBSCRIPTION_KEY.exists():
        return 3
    for p in OPENCPN_PATHS:
        if Path(p).exists():
            return 2
    if device_is_paired_and_approved():
        return 1
    return 0


@app.route('/tier/status', methods=['GET'])
def tier_status():
    tier = detect_tier()
    features = FEATURE_MATRIX.get(tier, FEATURE_MATRIX[0])
    # load_license() for metadata only — it does NOT determine the tier (T8 trust-anchor).
    license_data = load_license()
    return jsonify({
        'tier':            tier,
        'installation_id': license_data.get('installation_id') if license_data else None,
        'version':         license_data.get('version') if license_data else None,
        'testing_mode':    license_data.get('testing_mode', False) if license_data else False,
        'features':        features,
    })


@app.route('/tier/feature/<name>', methods=['GET'])
def tier_feature(name):
    tier = detect_tier()
    features = FEATURE_MATRIX.get(tier, FEATURE_MATRIX[0])
    if name not in features:
        return jsonify({'feature': name, 'enabled': False, 'error': 'unknown feature'}), 404
    value = features[name]
    # Non-boolean values (e.g. 'paid', '3_per_month') are truthy — treat as enabled
    enabled = bool(value) if not isinstance(value, bool) else value
    return jsonify({'feature': name, 'enabled': enabled})


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'tier-service', 'port': PORT})


if __name__ == '__main__':
    logger.info(f'Starting d3kOS Tier Service on port {PORT}')
    app.run(host='127.0.0.1', port=PORT, debug=False)
