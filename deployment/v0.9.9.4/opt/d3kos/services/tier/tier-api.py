#!/usr/bin/env python3
"""
d3kOS Tier API Service
Provides HTTP API for checking tier status and features
Port: 8093
"""

from flask import Flask, jsonify, request
import json
import os
import sys
import logging
from datetime import datetime

app = Flask(__name__)

# Configuration
LICENSE_FILE = '/opt/d3kos/config/license.json'
PORT = 8093

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('tier-api')

def load_license():
    """Load license.json file"""
    try:
        if not os.path.exists(LICENSE_FILE):
            logger.error(f"License file not found: {LICENSE_FILE}")
            return None

        with open(LICENSE_FILE, 'r') as f:
            license_data = json.load(f)

        return license_data
    except Exception as e:
        logger.error(f"Error loading license file: {e}")
        return None

def is_feature_enabled(feature_name):
    """Check if a specific feature is enabled for current tier"""
    license_data = load_license()
    if not license_data:
        return False

    features = license_data.get('features', {})
    return features.get(feature_name, False)

@app.route('/tier/status', methods=['GET'])
def get_tier_status():
    """Get current tier and all feature flags"""
    license_data = load_license()

    if not license_data:
        return jsonify({
            'success': False,
            'error': 'License file not found'
        }), 500

    return jsonify({
        'success': True,
        'tier': license_data.get('tier', 0),
        'installation_id': license_data.get('installation_id', 'unknown'),
        'features': license_data.get('features', {}),
        'reset_count': license_data.get('reset_count', 0),
        'max_resets': license_data.get('max_resets', 10),
        'subscription_status': license_data.get('subscription_status', 'none'),
        'is_paid_tier': license_data.get('is_paid_tier', False)
    })

@app.route('/tier/feature/<feature_name>', methods=['GET'])
def check_feature(feature_name):
    """Check if a specific feature is enabled"""
    enabled = is_feature_enabled(feature_name)

    return jsonify({
        'success': True,
        'feature': feature_name,
        'enabled': enabled
    })

@app.route('/tier/increment-reset', methods=['POST'])
def increment_reset_counter():
    """Increment reset counter (called by onboarding wizard)"""
    license_data = load_license()

    if not license_data:
        return jsonify({
            'success': False,
            'error': 'License file not found'
        }), 500

    current_count = license_data.get('reset_count', 0)
    max_resets = license_data.get('max_resets', 10)

    # Check if max resets exceeded
    if current_count >= max_resets:
        return jsonify({
            'success': False,
            'error': f'Maximum resets ({max_resets}) exceeded',
            'reset_count': current_count,
            'max_resets': max_resets,
            'upgrade_required': True
        }), 403

    # Increment counter
    license_data['reset_count'] = current_count + 1
    license_data['last_reset'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    # Save updated license.json
    try:
        with open(LICENSE_FILE, 'w') as f:
            json.dump(license_data, f, indent=2)

        logger.info(f"Reset counter incremented: {current_count} -> {current_count + 1}")

        return jsonify({
            'success': True,
            'reset_count': license_data['reset_count'],
            'max_resets': max_resets,
            'resets_remaining': max_resets - license_data['reset_count']
        })

    except Exception as e:
        logger.error(f"Error saving license file: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to update license file'
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'tier-api'})

if __name__ == '__main__':
    logger.info(f"Starting d3kOS Tier API on port {PORT}")
    app.run(host='127.0.0.1', port=PORT, debug=False)
