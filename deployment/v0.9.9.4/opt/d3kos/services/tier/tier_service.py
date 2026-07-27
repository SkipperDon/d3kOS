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

from flask import Flask, jsonify
import json
import logging
from pathlib import Path

app = Flask(__name__)

LICENSE_FILE = Path('/opt/d3kos/config/license.json')
PORT = 8093

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


@app.route('/tier/status', methods=['GET'])
def tier_status():
    license_data = load_license()
    if not license_data:
        return jsonify({
            'tier': 0,
            'features': FEATURE_MATRIX[0],
            'error': 'license.json not found',
        }), 404

    tier = _parse_tier(license_data.get('tier', 0))
    features = FEATURE_MATRIX.get(tier, FEATURE_MATRIX[0])

    return jsonify({
        'tier':            tier,
        'installation_id': license_data.get('installation_id'),
        'version':         license_data.get('version'),
        'testing_mode':    license_data.get('testing_mode', False),
        'features':        features,
    })


@app.route('/tier/feature/<name>', methods=['GET'])
def tier_feature(name):
    license_data = load_license()
    tier = 0
    if license_data:
        tier = _parse_tier(license_data.get('tier', 0))
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
