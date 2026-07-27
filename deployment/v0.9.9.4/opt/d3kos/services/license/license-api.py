#!/usr/bin/env python3
"""
d3kOS License API Service
Provides HTTP API for reading license information
Port: 8090 (localhost only)
"""

from flask import Flask, jsonify
import json
import os
import sys
import logging

app = Flask(__name__)

# Configuration
LICENSE_FILE = '/opt/d3kos/config/license.json'
PORT = 8091

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('license-api')

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

@app.route('/license/info', methods=['GET'])
def get_license_info():
    """Get basic license information (installation_id, tier, features)"""
    license_data = load_license()
    
    if not license_data:
        return jsonify({
            'success': False,
            'error': 'License file not found or invalid'
        }), 500
    
    # Return basic info (exclude sensitive fields if any)
    return jsonify({
        'success': True,
        'installation_id': license_data.get('installation_id', 'unknown'),
        'tier': license_data.get('tier', 0),
        'features': license_data.get('features', {}),
        'version': license_data.get('version', 'unknown')
    })

@app.route('/license/full', methods=['GET'])
def get_license_full():
    """Get complete license.json contents"""
    license_data = load_license()
    
    if not license_data:
        return jsonify({
            'success': False,
            'error': 'License file not found or invalid'
        }), 500
    
    return jsonify({
        'success': True,
        'license': license_data
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'license-api'})

if __name__ == '__main__':
    logger.info(f"Starting d3kOS License API on port {PORT}")
    logger.info(f"License file: {LICENSE_FILE}")
    
    # Check if license file exists on startup
    if os.path.exists(LICENSE_FILE):
        logger.info("License file found")
        license_data = load_license()
        if license_data:
            logger.info(f"Installation ID: {license_data.get('installation_id', 'unknown')}")
            logger.info(f"Tier: {license_data.get('tier', 0)}")
    else:
        logger.warning("License file not found - generate it first!")
    
    app.run(host='127.0.0.1', port=PORT, debug=False)
