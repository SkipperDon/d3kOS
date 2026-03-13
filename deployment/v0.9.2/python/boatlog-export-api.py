#!/usr/bin/env python3
"""
d3kOS Boatlog Export API
Provides CSV export functionality for boatlog entries

Port: 8095
Endpoints:
  - POST/GET /api/boatlog/export - Export boatlog as CSV
  - GET /api/boatlog/status - Service status
  - POST /api/boatlog/voice-note - Save voice note and transcribe

Author: d3kOS Team
Date: 2026-02-20
"""

from flask import Flask, jsonify, Response, request
import json
import sqlite3
import csv
from io import StringIO
from datetime import datetime
import os
import logging
import wave
import subprocess

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
VOICE_NOTE_DIR = '/opt/d3kos/data/boatlog-audio'
os.makedirs(VOICE_NOTE_DIR, exist_ok=True)

PREFS_PATH = '/opt/d3kos/config/user-preferences.json'

def _get_unit_metadata():
    """Return unit system and derived unit labels from user-preferences.json."""
    try:
        prefs = json.loads(open(PREFS_PATH).read())
    except Exception:
        prefs = {}
    system = prefs.get('measurement_system', 'metric')
    return {
        'measurement_system': system,
        'speed_unit':        'km/h' if system == 'metric' else 'mph',
        'temperature_unit':  'C'    if system == 'metric' else 'F',
        'pressure_unit':     'bar'  if system == 'metric' else 'psi',
        'volume_unit':       'L'    if system == 'metric' else 'gal',
    }


def get_db_connection():
    """Create database connection"""
    if not os.path.exists(BOATLOG_DB):
        raise FileNotFoundError(f"Boatlog database not found: {BOATLOG_DB}")

    conn = sqlite3.connect(BOATLOG_DB)
    conn.row_factory = sqlite3.Row
    return conn

def transcribe_audio(audio_path):
    """Transcribe audio using Vosk"""
    try:
        # Use vosk-transcribe if available
        result = subprocess.run([
            'vosk-transcribe',
            '--model', '/opt/d3kos/models/vosk-model-small-en-us-0.15',
            '--audio', audio_path
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            logger.warning(f"Vosk transcription failed: {result.stderr}")
            return ""
    except Exception as e:
        logger.warning(f"Vosk transcription error: {e}")
        return ""

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
                'GET /api/boatlog/export',
                'POST /api/boatlog/voice-note'
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

        # Write unit metadata rows (two rows: key names, then values)
        units = _get_unit_metadata()
        writer.writerow(['# UNIT METADATA', '', '', '', '', '', ''])
        writer.writerow(['measurement_system', 'speed_unit', 'temperature_unit',
                         'pressure_unit', 'volume_unit', 'export_timestamp', ''])
        writer.writerow([units['measurement_system'], units['speed_unit'],
                         units['temperature_unit'], units['pressure_unit'],
                         units['volume_unit'], datetime.now().isoformat(), ''])
        writer.writerow([])  # blank separator

        # Write data header row
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

@app.route('/api/boatlog/voice-note', methods=['POST'])
def save_voice_note():
    """Save voice note and transcribe it"""
    if 'audio' not in request.files:
        return jsonify({'success': False, 'error': 'No audio file'}), 400
    
    audio = request.files['audio']
    
    # Save audio file
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'voice_note_{ts}.webm'
    path = os.path.join(VOICE_NOTE_DIR, filename)
    audio.save(path)
    
    # Transcription via Vosk (best-effort — return empty if Vosk unavailable)
    transcript = ''
    try:
        transcript = transcribe_audio(path)
    except Exception as e:
        logger.warning(f"Transcription failed: {e}")
        pass
    
    return jsonify({
        'success': True, 
        'filename': filename, 
        'transcript': transcript, 
        'timestamp': ts
    })

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