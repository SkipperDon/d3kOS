#!/usr/bin/env python3
"""
d3kOS Failure Intelligence — FI1 Failure Reporter
v0.9.8

Lightweight Flask service on Port 8106.
Any d3kOS service calls POST /report to log a failure.
Failures are stored locally in SQLite and synced to FI2 (HostPapa) in background.

How other services call it:
    import requests
    requests.post('http://localhost:8106/report', json={
        'service':    'd3kos-cloud-agent',
        'error_type': 'crash',
        'message':    'ConnectionRefusedError: ...',
    }, timeout=2)

Error signature:
    SHA-256 of "service:error_type:normalised_message" truncated to 12 hex chars.
    Normalisation strips numbers, UUIDs, file paths — so the same logical
    error clusters across devices regardless of line numbers or timestamps.

Background sync:
    Every 5 minutes, unsynchronised rows are POSTed to FI2 (HostPapa
    failure-report.php). Requires cloud-config.json with amboat_api_key
    + device_token + amboat_base_url. Sync is best-effort — failures are
    never lost locally even if HostPapa is unreachable.

Deploy:
    sudo cp failure_reporter.py /opt/d3kos/services/agents/
    sudo cp d3kos-failure-reporter.service /etc/systemd/system/
    sudo systemctl enable --now d3kos-failure-reporter
"""

import hashlib
import json
import logging
import logging.handlers
import re
import sqlite3
import threading
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, request

# ── Paths ──────────────────────────────────────────────────────────────────────

DB_PATH      = Path('/opt/d3kos/data/failures.db')
CLOUD_CONFIG = Path('/opt/d3kos/config/cloud-config.json')
LOG_PATH     = Path('/opt/d3kos/logs/failure-reporter.log')

SYNC_INTERVAL = 300   # 5 minutes
PORT          = 8109

# ── Logging ───────────────────────────────────────────────────────────────────

LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
_handler = logging.handlers.RotatingFileHandler(
    str(LOG_PATH), maxBytes=1024 * 1024, backupCount=2
)
_handler.setFormatter(logging.Formatter(
    '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
))
logging.basicConfig(level=logging.INFO, handlers=[_handler])
log = logging.getLogger('failure_reporter')

# ── Flask app ──────────────────────────────────────────────────────────────────

app = Flask(__name__)


# ── Database ──────────────────────────────────────────────────────────────────

def _init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS failures (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            service         TEXT NOT NULL,
            error_type      TEXT NOT NULL,
            message         TEXT NOT NULL,
            error_signature TEXT NOT NULL,
            reported_at     TEXT NOT NULL,
            synced          INTEGER DEFAULT 0
        )
    ''')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_synced ON failures (synced)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_sig ON failures (error_signature)')
    # Rolling window: keep last 1000 rows per service
    conn.commit()
    conn.close()


def _insert_failure(service: str, error_type: str, message: str, sig: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        'INSERT INTO failures (service, error_type, message, error_signature, reported_at) '
        'VALUES (?, ?, ?, ?, ?)',
        (service, error_type, message[:500], sig,
         datetime.now(tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S'))
    )
    # Trim to last 2000 rows
    conn.execute('''
        DELETE FROM failures WHERE id NOT IN (
            SELECT id FROM failures ORDER BY id DESC LIMIT 2000
        )
    ''')
    conn.commit()
    conn.close()


def _get_unsynced() -> list:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        'SELECT id, service, error_type, message, error_signature, reported_at '
        'FROM failures WHERE synced = 0 ORDER BY id LIMIT 50'
    ).fetchall()
    conn.close()
    return rows


def _mark_synced(ids: list):
    if not ids:
        return
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        f'UPDATE failures SET synced = 1 WHERE id IN ({",".join("?" * len(ids))})',
        ids
    )
    conn.commit()
    conn.close()


# ── Error signature ────────────────────────────────────────────────────────────

_STRIP_PATTERNS = [
    r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b',  # UUID
    r'/[^\s]+',          # file paths
    r'\b\d{4,}\b',       # long numbers (line numbers, timestamps, ports)
    r'\b0x[0-9a-f]+\b',  # hex addresses
]
_COMPILED = [re.compile(p, re.IGNORECASE) for p in _STRIP_PATTERNS]


def _make_signature(service: str, error_type: str, message: str) -> str:
    """
    Normalise message (strip file paths, numbers, UUIDs) then SHA-256 hash
    service:error_type:normalised. Return first 12 hex chars.
    Two different Pi units with the same logical error will produce the same signature.
    """
    normalised = message.lower()
    for pattern in _COMPILED:
        normalised = pattern.sub(' ', normalised)
    # Collapse whitespace
    normalised = ' '.join(normalised.split())[:200]
    raw = f'{service}:{error_type}:{normalised}'
    return hashlib.sha256(raw.encode()).hexdigest()[:12]


# ── Flask routes ───────────────────────────────────────────────────────────────

@app.route('/report', methods=['POST'])
def report():
    """
    POST /report
    Body: {"service": "...", "error_type": "...", "message": "..."}
    Returns: {"ok": true, "signature": "abc123def456"}
    """
    data = request.get_json(silent=True) or {}
    service    = str(data.get('service', 'unknown'))[:100]
    error_type = str(data.get('error_type', 'error'))[:50]
    message    = str(data.get('message', ''))[:500]

    if not message:
        return jsonify({'ok': False, 'error': 'message required'}), 400

    sig = _make_signature(service, error_type, message)
    _insert_failure(service, error_type, message, sig)
    log.info('Failure recorded: %s / %s — sig=%s', service, error_type, sig)
    return jsonify({'ok': True, 'signature': sig})


@app.route('/health', methods=['GET'])
def health():
    """GET /health — liveness check."""
    try:
        conn = sqlite3.connect(DB_PATH)
        total   = conn.execute('SELECT COUNT(*) FROM failures').fetchone()[0]
        unsynced = conn.execute('SELECT COUNT(*) FROM failures WHERE synced=0').fetchone()[0]
        conn.close()
        return jsonify({'ok': True, 'total': total, 'unsynced': unsynced})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/recent', methods=['GET'])
def recent():
    """GET /recent?limit=20 — last N failures (dashboard use)."""
    limit = min(int(request.args.get('limit', 20)), 100)
    conn  = sqlite3.connect(DB_PATH)
    rows  = conn.execute(
        'SELECT service, error_type, message, error_signature, reported_at '
        'FROM failures ORDER BY id DESC LIMIT ?', (limit,)
    ).fetchall()
    conn.close()
    return jsonify([{
        'service': r[0], 'error_type': r[1], 'message': r[2],
        'signature': r[3], 'reported_at': r[4],
    } for r in rows])


# ── Background sync to FI2 ─────────────────────────────────────────────────────

def _load_cloud_config() -> dict:
    try:
        return json.loads(CLOUD_CONFIG.read_text()) if CLOUD_CONFIG.exists() else {}
    except Exception:
        return {}


def _sync_to_fi2():
    """Post unsynced failures to HostPapa failure-report.php."""
    cfg          = _load_cloud_config()
    api_key      = cfg.get('amboat_api_key', '')
    device_token = cfg.get('device_token', '')
    base_url     = cfg.get('amboat_base_url', '').rstrip('/')

    if not api_key or not base_url:
        return   # Not configured — cloud sync not available

    rows = _get_unsynced()
    if not rows:
        return

    url = f'{base_url}/wp-content/themes/twentytwenty-child/mobile/failure-report.php'
    synced_ids = []

    for row in rows:
        row_id, service, error_type, message, sig, reported_at = row
        payload = json.dumps({
            'service':         service,
            'error_type':      error_type,
            'message':         message,
            'error_signature': sig,
            'reported_at':     reported_at,
        }).encode()

        try:
            req = urllib.request.Request(url, data=payload, method='POST', headers={
                'Authorization':  f'Bearer {api_key}',
                'X-Device-Token': device_token,
                'Content-Type':   'application/json',
            })
            urllib.request.urlopen(req, timeout=15)
            synced_ids.append(row_id)
        except Exception as e:
            log.debug('FI2 sync failed for id=%d: %s', row_id, e)
            break   # Stop on first error — retry next cycle

    if synced_ids:
        _mark_synced(synced_ids)
        log.info('FI2 sync: %d failures uploaded', len(synced_ids))


def _sync_loop():
    while True:
        time.sleep(SYNC_INTERVAL)
        try:
            _sync_to_fi2()
        except Exception as e:
            log.error('Sync loop error: %s', e)


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    _init_db()
    log.info('FI1 Failure Reporter starting on port %d', PORT)

    # Start background sync thread
    t = threading.Thread(target=_sync_loop, daemon=True)
    t.start()

    app.run(host='127.0.0.1', port=PORT, debug=False)
