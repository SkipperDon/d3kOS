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
from flask_cors import CORS
import sqlite3
import csv
from io import StringIO
from datetime import datetime
import os
import logging
import wave
import subprocess
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('boatlog-export-api')

app = Flask(__name__)
CORS(app)   # allow cross-origin from Flask dashboard (port 3000)

# Configuration
BOATLOG_DB = '/opt/d3kos/data/boatlog/boatlog.db'
PORT = 8095
VOICE_NOTE_DIR = '/opt/d3kos/data/boatlog-audio'
VOSK_MODEL_PATH = '/opt/d3kos/models/vosk/vosk-model-small-en-us-0.15'
os.makedirs(VOICE_NOTE_DIR, exist_ok=True)

# ── Vosk model — loaded once at startup, not per request ─────────────────────
_vosk_model = None

def _get_vosk_model():
    """Return cached Vosk model, loading it on first call."""
    global _vosk_model
    if _vosk_model is None:
        try:
            import vosk
            _vosk_model = vosk.Model(VOSK_MODEL_PATH)
            logger.info("Vosk model loaded and cached")
        except Exception as e:
            logger.warning(f"Vosk model load failed: {e}")
    return _vosk_model


def get_db_connection():
    """Create database connection"""
    if not os.path.exists(BOATLOG_DB):
        raise FileNotFoundError(f"Boatlog database not found: {BOATLOG_DB}")

    conn = sqlite3.connect(BOATLOG_DB)
    conn.row_factory = sqlite3.Row
    return conn

def transcribe_audio(audio_path):
    """Transcribe audio using cached Vosk model.
    Browser records .webm — convert to 16kHz mono WAV first via ffmpeg,
    then feed PCM frames to Vosk recogniser.
    """
    import json as _json
    model = _get_vosk_model()
    if model is None:
        return ""

    import vosk
    wav_path = audio_path + '.wav'
    try:
        # Convert webm → 16kHz mono PCM WAV
        conv = subprocess.run([
            'ffmpeg', '-y', '-i', audio_path,
            '-ar', '16000', '-ac', '1', '-f', 'wav', wav_path
        ], capture_output=True, timeout=30)
        if conv.returncode != 0:
            logger.warning(f"ffmpeg conversion failed: {conv.stderr.decode()}")
            return ""

        rec   = vosk.KaldiRecognizer(model, 16000)
        words = []
        with wave.open(wav_path, 'rb') as wf:
            while True:
                data = wf.readframes(4000)
                if not data:
                    break
                if rec.AcceptWaveform(data):
                    words.append(_json.loads(rec.Result()).get('text', ''))
        words.append(_json.loads(rec.FinalResult()).get('text', ''))
        return ' '.join(w for w in words if w).strip()

    except Exception as e:
        logger.warning(f"Vosk transcription error: {e}")
        return ""
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)

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

_MIME_EXT = {
    'audio/webm':  '.webm',
    'audio/ogg':   '.ogg',
    'audio/mp4':   '.mp4',
    'audio/mpeg':  '.mp3',
    'audio/wav':   '.wav',
    'audio/x-wav': '.wav',
}


@app.route('/api/boatlog/voice-note', methods=['POST'])
def save_voice_note():
    """Save voice note, transcribe it, and persist to DB"""
    if 'audio' not in request.files:
        return jsonify({'success': False, 'error': 'No audio file'}), 400

    audio = request.files['audio']

    # Reject empty uploads — browser recorded nothing (e.g. unsupported codec)
    audio.stream.seek(0, 2)
    size = audio.stream.tell()
    audio.stream.seek(0)
    if size == 0:
        logger.warning('Voice note upload rejected: 0-byte file')
        return jsonify({'success': False, 'error': 'Empty audio — nothing was recorded. Check browser microphone permissions.'}), 400

    # Use MIME type to pick correct extension so ffmpeg detects format reliably
    mime = (audio.mimetype or 'audio/webm').split(';')[0].strip().lower()
    ext  = _MIME_EXT.get(mime, '.webm')

    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'voice_note_{ts}{ext}'
    path = os.path.join(VOICE_NOTE_DIR, filename)
    audio.save(path)

    # Transcription via cached Vosk (best-effort — return empty if unavailable)
    transcript = ''
    try:
        transcript = transcribe_audio(path)
    except Exception as e:
        logger.warning(f"Transcription failed: {e}")

    # Persist to SQLite so export includes voice notes
    iso_ts = datetime.now().isoformat()
    entry_id = str(uuid.uuid4())
    content = transcript if transcript else f'(voice note — {filename})'
    try:
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO boatlog_entries (entry_id, timestamp, entry_type, content) VALUES (?,?,?,?)",
            (entry_id, iso_ts, 'voice', content)
        )
        conn.commit()
        conn.close()
        logger.info(f"Voice note saved to DB: {entry_id}")
    except Exception as e:
        logger.warning(f"DB insert failed: {e}")

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

    # Pre-load Vosk model so first voice note responds quickly
    logger.info("Pre-loading Vosk model...")
    _get_vosk_model()

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
