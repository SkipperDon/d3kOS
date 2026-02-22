#!/usr/bin/env python3
# d3kOS - Marine Intelligence Operating System
# Copyright (C) 2026 Donald Moskaluk / AtMyBoat.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# For commercial licensing contact: skipperdon@atmyboat.com

"""
d3kOS Export Manager Service with Full Queue Support
Provides HTTP API for exporting boat data with retry logic and all 9 categories

Port: 8094

Author: d3kOS Team
Date: 2026-02-20
Version: 2.0 (with queue, worker, and 9 categories)
"""

from flask import Flask, jsonify, request
import json
import os
import sys
import atexit
from datetime import datetime
from pathlib import Path
import logging

# Add service directory to path
sys.path.insert(0, '/opt/d3kos/services/export')

# Import queue, worker, and categories modules
try:
    from export_queue import ExportQueue
    from export_worker import ExportWorker
    from export_categories import ExportCategories
except ImportError as e:
    print(f"ERROR: Failed to import modules: {e}")
    print("Make sure export_queue.py, export_worker.py, and export_categories.py are in /opt/d3kos/services/export/")
    sys.exit(1)

app = Flask(__name__)

# Configuration
LICENSE_FILE = '/opt/d3kos/config/license.json'
EXPORT_DIR = '/opt/d3kos/data/exports/exports'
PORT = 8094
CENTRAL_API_URL = "https://d3kos-cloud-api.example.com"  # TODO: Update with actual URL

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('export-manager')

# Initialize queue and worker (global instances)
export_queue = None
export_worker = None

def initialize_services():
    """Initialize queue and worker"""
    global export_queue, export_worker

    try:
        # Initialize export queue
        export_queue = ExportQueue()
        logger.info("Export queue initialized")

        # Initialize and start background worker
        export_worker = ExportWorker(CENTRAL_API_URL)
        export_worker.start()
        logger.info("Export worker started")

    except Exception as e:
        logger.error(f"Error initializing services: {e}")

def shutdown_services():
    """Shutdown worker on exit"""
    global export_worker

    if export_worker:
        logger.info("Shutting down export worker...")
        export_worker.stop()

# Register shutdown handler
atexit.register(shutdown_services)

def load_license():
    """Load license.json"""
    try:
        with open(LICENSE_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading license: {e}")
        return None

def check_export_permission():
    """Check if tier allows export (Tier 1+)"""
    license_data = load_license()
    if not license_data:
        return False, 0, "License file not found"

    tier = license_data.get('tier', 0)
    if tier == 0:
        logger.warning('Export blocked: Tier 0 does not have export capability')
        return False, tier, "Tier 0 does not have export capability"

    return True, tier, None

@app.route('/export/status', methods=['GET'])
def api_export_status():
    """Get export manager status"""
    try:
        can_export, tier, error = check_export_permission()

        # Get queue status
        queue_status = export_queue.get_queue_status() if export_queue else {}

        return jsonify({
            'success': True,
            'service': 'export-manager',
            'port': PORT,
            'tier': tier,
            'can_export': can_export,
            'error': error,
            'queue': queue_status
        })

    except Exception as e:
        logger.error(f"Status check error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/export/generate', methods=['POST'])
def api_generate_export():
    """Generate export with all 9 categories and add to queue"""
    try:
        # Check export permission
        can_export, tier, error = check_export_permission()

        if not can_export:
            return jsonify({
                'success': False,
                'error': error
            }), 403

        # Get installation ID from license
        license_data = load_license()
        installation_id = license_data.get('installation_id', 'unknown')

        # Collect all 9 categories
        logger.info(f"Generating export for installation {installation_id}")
        categories = ExportCategories(installation_id)
        export_data = categories.collect_all()

        # Create export directory
        export_dir = Path(EXPORT_DIR)
        export_dir.mkdir(parents=True, exist_ok=True)

        # Generate export filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_filename = f"export_{timestamp}.json"
        export_path = export_dir / export_filename

        # Write export file
        with open(export_path, 'w') as f:
            json.dump(export_data, f, indent=2)

        # Get category count
        category_count = len(export_data['data'])

        # Add to queue
        queue_id = export_queue.add_export(
            export_file=str(export_path),
            tier=tier,
            category_count=category_count
        )

        logger.info(f"Export generated and queued: {export_filename} (queue_id: {queue_id})")

        return jsonify({
            'success': True,
            'export_file': export_filename,
            'queue_id': queue_id,
            'category_count': category_count,
            'message': 'Export generated and added to queue'
        })

    except Exception as e:
        logger.error(f"Export generation error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/export/queue/status', methods=['GET'])
def api_queue_status():
    """Get export queue status"""
    try:
        if not export_queue:
            return jsonify({
                'error': 'Queue not initialized'
            }), 500

        status = export_queue.get_queue_status()
        return jsonify(status)

    except Exception as e:
        logger.error(f"Queue status error: {e}")
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/export/queue/cleanup', methods=['POST'])
def api_queue_cleanup():
    """Cleanup old completed and failed exports"""
    try:
        if not export_queue:
            return jsonify({
                'error': 'Queue not initialized'
            }), 500

        # Cleanup old completed (30 days)
        export_queue.cleanup_old_completed(days=30)

        # Cleanup old failed (7 days)
        export_queue.cleanup_old_failed(days=7)

        return jsonify({
            'success': True,
            'message': 'Queue cleanup completed'
        })

    except Exception as e:
        logger.error(f"Queue cleanup error: {e}")
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'export-manager',
        'queue_initialized': export_queue is not None,
        'worker_running': export_worker is not None and export_worker.worker_thread is not None
    }), 200


if __name__ == '__main__':
    logger.info(f"Starting d3kOS Export Manager v2.0 on port {PORT}")
    logger.info(f"Central API URL: {CENTRAL_API_URL}")

    # Initialize services
    initialize_services()

    # Start Flask app
    app.run(
        host='127.0.0.1',
        port=PORT,
        debug=False
    )
