#!/usr/bin/env python3
"""
d3kOS Boatlog Export API
Provides CSV export functionality for boatlog entries

Port: 8095
Endpoints:
  - POST/GET /api/boatlog/export - Export boatlog as CSV
  - GET /api/boatlog/status - Service status

Author: d3kOS Team
Date: 2026-02-20
"""

from flask import Flask, jsonify, Response, request
import sqlite3
import csv
from io import StringIO
from datetime import datetime
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('boatlog-export-api')

app = Flask(__name__)

# Configuration
BOATLOG_DB = '/opt/d3kos/data/boatlog/boatlog.db'
PORT = 8095

def get_db_connection():
    """Create database connection"""
    if not os.path.exists(BOATLOG_DB):
        raise FileNotFoundError(f"Boatlog database not found: {BOATLOG_DB}")

    conn = sqlite3.connect(BOATLOG_DB)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/boatlog/status', methods=['GET'])
def status():
    """Get service status"""
    try:
        # Check database exists
        db_exists = os.path.exists(BOATLOG_DB)

        # Count entries if database exists
        entry_count = 0
        if db_exists:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) as count FROM boatlog_entries")
                entry_count = cursor.fetchone()['count']
                conn.close()
            except Exception as e:
                logger.error(f"Error counting entries: {e}")

        return jsonify({
            'status': 'running',
            'service': 'boatlog-export-api',
            'port': PORT,
            'database_exists': db_exists,
            'database_path': BOATLOG_DB,
            'entry_count': entry_count,
            'endpoints': [
                'GET /api/boatlog/status',
                'POST /api/boatlog/export',
                'GET /api/boatlog/export'
            ]
        })
    except Exception as e:
        logger.error(f"Status check error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/boatlog/export', methods=['POST', 'GET'])
def export_boatlog():
    """
    Export all boatlog entries as CSV

    Returns:
        CSV file with all boatlog entries

    CSV Columns:
        - Entry ID: Unique identifier
        - Timestamp: ISO-8601 format
        - Type: voice, text, auto, weather
        - Content: Entry text/transcription
        - Latitude: GPS latitude (if available)
        - Longitude: GPS longitude (if available)
        - Weather: Weather conditions (if auto-log)
    """
    try:
        logger.info("Export request received")

        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Query all entries, ordered by newest first
        cursor.execute("""
            SELECT
                entry_id,
                timestamp,
                entry_type,
                content,
                latitude,
                longitude,
                weather_conditions
            FROM boatlog_entries
            ORDER BY timestamp DESC
        """)

        rows = cursor.fetchall()
        row_count = len(rows)

        logger.info(f"Retrieved {row_count} entries from database")

        # Create CSV in memory
        output = StringIO()
        writer = csv.writer(output)

        # Write header row
        writer.writerow([
            'Entry ID',
            'Timestamp',
            'Type',
            'Content',
            'Latitude',
            'Longitude',
            'Weather Conditions'
        ])

        # Write data rows
        for row in rows:
            writer.writerow([
                row['entry_id'],
                row['timestamp'],
                row['entry_type'],
                row['content'] or '',
                row['latitude'] if row['latitude'] is not None else '',
                row['longitude'] if row['longitude'] is not None else '',
                row['weather_conditions'] or ''
            ])

        conn.close()

        # Get CSV string
        csv_data = output.getvalue()
        output.close()

        # Generate filename with current date
        filename = f"d3kos_boatlog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        logger.info(f"Export complete: {row_count} entries, filename: {filename}")

        # Return CSV as downloadable file
        return Response(
            csv_data,
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Type': 'text/csv; charset=utf-8'
            }
        )

    except FileNotFoundError as e:
        logger.error(f"Database not found: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Boatlog database not found. Add entries first.',
            'database_path': BOATLOG_DB
        }), 404

    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Database error: {str(e)}'
        }), 500

    except Exception as e:
        logger.error(f"Export error: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    logger.info(f"Starting d3kOS Boatlog Export API on port {PORT}")
    logger.info(f"Database path: {BOATLOG_DB}")

    # Verify database exists
    if os.path.exists(BOATLOG_DB):
        logger.info(f"✓ Database found")
    else:
        logger.warning(f"⚠ Database not found (will be created when first entry added)")

    # Start Flask app
    app.run(
        host='127.0.0.1',
        port=PORT,
        debug=False
    )
