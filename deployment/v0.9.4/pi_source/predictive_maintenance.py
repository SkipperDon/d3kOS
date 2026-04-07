#!/usr/bin/env python3
"""
d3kOS Predictive Maintenance Service v0.9.5
Port 8106

Two background threads:
  historian  — polls SignalK every 60s, stores engine readings in SQLite
  detector   — every 5 min, scans last 24h of readings for anomalies vs 30-day baseline

Flask API:
  GET /predictive/health      service health check
  GET /predictive/status      current risk per field (OK / WATCH / ALERT)
  GET /predictive/history     last N readings (default 200, max 2000)
  GET /predictive/baseline    mean/stdev stats per field over baseline window

Tier gate:
  Data collection runs regardless of tier.
  Writing alerts to issues.db requires predictive_alerts feature (T1+).

Author:  d3kOS Team
Version: 0.9.5
"""

import logging
import sqlite3
import statistics
import subprocess
import threading
import time
import uuid
from datetime import datetime, timedelta, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path

import requests

# Flask is only needed when running as the service (not during testing/import)
try:
    from flask import Flask, jsonify, request as flask_request
    _flask_available = True
except ImportError:
    _flask_available = False

# ── Config ────────────────────────────────────────────────────────────────────
PORT              = 8106
HIST_DB           = Path('/opt/d3kos/data/predictive/engine_history.db')
ISSUES_DB         = Path('/opt/d3kos/data/self-healing/issues.db')
LOG_FILE          = Path('/opt/d3kos/logs/predictive.log')
TIER_URL          = 'http://localhost:8093/tier/feature/predictive_alerts'
TIER_VOICE_URL    = 'http://localhost:8093/tier/feature/voice_assistant'
BOATLOG_DB        = Path('/opt/d3kos/data/boatlog/boatlog.db')
PIPER_BIN         = '/usr/local/bin/piper'
PIPER_VOICE       = '/opt/d3kos/models/piper/en_US-amy-medium.onnx'
SPEAK_WAV         = '/tmp/predictive-alert.wav'
APLAY_DEVICE      = 'plughw:S330,0'
SK_ENGINE_URL     = 'http://localhost:8099/signalk/v1/api/vessels/self/propulsion/port'
SK_FUEL_URL       = 'http://localhost:8099/signalk/v1/api/vessels/self/tanks/fuel/0'

POLL_INTERVAL     = 60     # seconds between historian reads
DETECT_INTERVAL   = 300    # seconds between detection runs (5 min)
MIN_BASELINE_ROWS = 100    # minimum engine-on readings before anomaly detection fires
BASELINE_WINDOW   = 1000   # last N engine-on readings used for mean/σ
CHECK_WINDOW_HOURS = 24    # anomalies found within this window drive risk state
PURGE_DAYS        = 90     # auto-purge signalk readings older than this
ALERT_COOLDOWN_S  = 3600   # minimum seconds between duplicate alerts for same category

# Field anomaly config:
#   db_column -> (alert_category, sigma_severity, direction)
#   direction: 'high' = alert when too high, 'low' = too low, 'both' = either
FIELD_CONFIG = {
    'coolant_temp_c':    ('engine_overtemp',     'warning', 'high'),
    'oil_pressure_kpa':  ('engine_oil_pressure', 'warning', 'low'),
    'rpm':               ('engine_roughness',    'warning', 'both'),
}

# Hard limits — 'critical' severity regardless of baseline
# Format: field -> (operator, limit_value, category, severity, message_template)
HARD_LIMITS = {
    'coolant_temp_c':  ('>', 100.0, 'engine_overtemp',    'critical',
                        'Coolant critical: {val:.1f}°C exceeds 100°C limit'),
    'oil_pressure_kpa': ('<', 150.0, 'engine_oil_pressure', 'critical',
                        'Oil pressure critical: {val:.1f} kPa below 150 kPa limit'),
}

# ── Logging ───────────────────────────────────────────────────────────────────
logger = logging.getLogger('predictive-maintenance')
logger.setLevel(logging.INFO)

def _init_logging():
    """Set up file logging. Called at service startup — not at import time."""
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        _h = RotatingFileHandler(str(LOG_FILE), maxBytes=2 * 1024 * 1024, backupCount=2)
        _h.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        logger.addHandler(_h)
    except Exception:
        # Fall back to console logging (e.g. during testing or no /opt/d3kos)
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(levelname)s %(message)s')

if _flask_available:
    app = Flask(__name__)
else:
    app = None

# Thread-safe risk state — updated by detector, read by Flask
_risk_lock  = threading.Lock()
_risk_state = {}   # field -> {status, message, updated_at}

# Alert deduplication — tracks last time each category was written to issues.db
_alert_times = {}   # category -> float (time.monotonic())


# ── Database ──────────────────────────────────────────────────────────────────

def init_db(db_path=None):
    """Create engine_history.db and schema if not present."""
    p = db_path or HIST_DB
    p.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(p)) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS engine_snapshots (
                id                 INTEGER PRIMARY KEY AUTOINCREMENT,
                ts                 TEXT    NOT NULL,
                rpm                INTEGER,
                oil_pressure_kpa   REAL,
                coolant_temp_c     REAL,
                boost_pressure_kpa REAL,
                fuel_level_pct     REAL,
                engine_hours       REAL,
                engine_on          INTEGER DEFAULT 0,
                source             TEXT    DEFAULT 'signalk'
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_ts ON engine_snapshots(ts)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_src ON engine_snapshots(source)")
        conn.commit()
    logger.info(f'DB ready: {p}')


def purge_old_rows():
    """Delete signalk rows older than PURGE_DAYS to protect SD card."""
    try:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=PURGE_DAYS)).isoformat()
        with sqlite3.connect(str(HIST_DB)) as conn:
            cur = conn.execute(
                "DELETE FROM engine_snapshots WHERE ts < ? AND source = 'signalk'",
                (cutoff,)
            )
            if cur.rowcount:
                logger.info(f'Purged {cur.rowcount} signalk rows older than {PURGE_DAYS}d')
            conn.commit()
    except Exception as e:
        logger.warning(f'Purge error: {e}')


# ── SignalK reader ─────────────────────────────────────────────────────────────

def read_engine_snapshot():
    """
    Read current engine state from SignalK.
    Returns a dict or None if SignalK is unreachable.
    Always returns a row (engine_on=0) so the historian maintains continuous coverage.
    """
    snap = {
        'ts':                 datetime.now(timezone.utc).isoformat(),
        'rpm':                None,
        'oil_pressure_kpa':   None,
        'coolant_temp_c':     None,
        'boost_pressure_kpa': None,
        'fuel_level_pct':     None,
        'engine_hours':       None,
        'engine_on':          0,
        'source':             'signalk',
    }
    try:
        r = requests.get(SK_ENGINE_URL, timeout=5)
        prop = r.json()

        rev_val = prop.get('revolutions', {}).get('value')
        if rev_val is not None:
            snap['rpm'] = round(rev_val * 60)

        boost_val = prop.get('boostPressure', {}).get('value')
        if boost_val is not None:
            snap['boost_pressure_kpa'] = round(boost_val / 1000, 2)

        oil_val = prop.get('oilPressure', {}).get('value')
        if oil_val is not None:
            snap['oil_pressure_kpa'] = round(oil_val / 1000, 2)

        temp_val = prop.get('temperature', {}).get('value')
        if temp_val is not None:
            snap['coolant_temp_c'] = round(temp_val - 273.15, 1)

        runtime_val = prop.get('runTime', {}).get('value')
        if runtime_val is not None:
            snap['engine_hours'] = round(runtime_val / 3600, 2)

        snap['engine_on'] = 1 if (snap['rpm'] is not None and snap['rpm'] > 0) else 0

        try:
            r2 = requests.get(SK_FUEL_URL, timeout=3)
            fuel_val = r2.json().get('currentLevel', {}).get('value')
            if fuel_val is not None:
                snap['fuel_level_pct'] = round(fuel_val * 100, 1)
        except Exception:
            pass

    except Exception as e:
        logger.debug(f'SignalK read failed (engine may be off or SK not running): {e}')

    return snap


def store_snapshot(snap, db_path=None):
    p = db_path or HIST_DB
    with sqlite3.connect(str(p)) as conn:
        conn.execute("""
            INSERT INTO engine_snapshots
              (ts, rpm, oil_pressure_kpa, coolant_temp_c, boost_pressure_kpa,
               fuel_level_pct, engine_hours, engine_on, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            snap['ts'], snap['rpm'], snap['oil_pressure_kpa'], snap['coolant_temp_c'],
            snap['boost_pressure_kpa'], snap['fuel_level_pct'], snap['engine_hours'],
            snap['engine_on'], snap['source']
        ))
        conn.commit()


# ── Anomaly detection ─────────────────────────────────────────────────────────

def _is_predictive_alerts_enabled():
    """Check tier gate. Fail-safe: returns False if tier service unreachable."""
    try:
        r = requests.get(TIER_URL, timeout=3)
        return r.json().get('enabled', False)
    except Exception:
        return False


def _can_write_alert(category):
    """Deduplication guard — returns False if same category was alerted within cooldown."""
    last = _alert_times.get(category, 0)
    return (time.monotonic() - last) >= ALERT_COOLDOWN_S


def write_issue(category, severity, description):
    """Write a predictive alert to issues.db (same schema as alert_watcher)."""
    if not ISSUES_DB.exists():
        logger.warning(f'issues.db not found — skipping alert: {category}')
        return
    if not _can_write_alert(category):
        logger.debug(f'Alert cooldown active for {category} — skipping duplicate')
        return
    try:
        with sqlite3.connect(str(ISSUES_DB)) as conn:
            conn.execute(
                "INSERT INTO issues (category, severity, description, timestamp, status) "
                "VALUES (?, ?, ?, ?, 'open')",
                (category, severity, description, datetime.now(timezone.utc).isoformat())
            )
            conn.commit()
        _alert_times[category] = time.monotonic()
        logger.warning(f'Predictive alert: [{severity}] {category} — {description}')
    except Exception as e:
        logger.error(f'Failed to write issue: {e}')


def write_boatlog(message):
    """Write an auto predictive alert entry to boatlog.db."""
    if not BOATLOG_DB.exists():
        logger.debug('boatlog.db not found — skipping boatlog entry')
        return
    try:
        with sqlite3.connect(str(BOATLOG_DB)) as conn:
            conn.execute(
                "INSERT INTO boatlog_entries "
                "(entry_id, timestamp, entry_type, content, latitude, longitude, weather_conditions) "
                "VALUES (?, ?, 'predictive_alert', ?, NULL, NULL, NULL)",
                (str(uuid.uuid4()), datetime.now(timezone.utc).isoformat(), f'[Auto] {message}')
            )
            conn.commit()
        logger.info(f'Boatlog entry written: {message}')
    except Exception as e:
        logger.error(f'Failed to write boatlog entry: {e}')


def speak_alert(message):
    """Speak the alert message via Piper TTS + aplay. Non-blocking, best-effort."""
    try:
        piper = Path(PIPER_BIN)
        model = Path(PIPER_VOICE)
        if not piper.exists() or not model.exists():
            logger.debug('Piper TTS not available — skipping voice alert')
            return
        # Run in background thread so it doesn't block detection loop
        def _speak():
            try:
                p = subprocess.Popen(
                    [str(piper), '--model', str(model), '--output_file', SPEAK_WAV],
                    stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                p.communicate(input=message.encode(), timeout=15)
                subprocess.run(
                    ['aplay', '-q', '-D', APLAY_DEVICE, SPEAK_WAV],
                    timeout=15, stderr=subprocess.DEVNULL
                )
            except Exception as e:
                logger.warning(f'Voice alert playback failed: {e}')
        threading.Thread(target=_speak, daemon=True, name='speak').start()
    except Exception as e:
        logger.warning(f'speak_alert error: {e}')


def _is_voice_alert_enabled():
    """Check tier gate for voice alerts (T1+ voice_assistant feature)."""
    try:
        r = requests.get(TIER_VOICE_URL, timeout=3)
        return r.json().get('enabled', False)
    except Exception:
        return False


def detect_anomalies(db_path=None):
    """
    Scan last CHECK_WINDOW_HOURS of engine-on readings for anomalies.
    Baseline is built from last BASELINE_WINDOW engine-on readings.
    Updates _risk_state. Writes to issues.db if tier allows and cooldown permits.
    Accepts optional db_path for testing.
    """
    global _risk_state

    p = db_path or HIST_DB
    now_utc = datetime.now(timezone.utc)
    window_start = (now_utc - timedelta(hours=CHECK_WINDOW_HOURS)).isoformat()

    try:
        with sqlite3.connect(str(p)) as conn:
            conn.row_factory = sqlite3.Row

            # Baseline: last BASELINE_WINDOW engine-on readings (any age)
            baseline_rows = conn.execute(
                "SELECT rpm, oil_pressure_kpa, coolant_temp_c FROM engine_snapshots "
                "WHERE engine_on = 1 ORDER BY ts DESC LIMIT ?",
                (BASELINE_WINDOW,)
            ).fetchall()

            # Check window: engine-on readings in last 24h
            check_rows = conn.execute(
                "SELECT * FROM engine_snapshots "
                "WHERE engine_on = 1 AND ts >= ? ORDER BY ts ASC",
                (window_start,)
            ).fetchall()

        baseline_count = len(baseline_rows)

        if baseline_count < MIN_BASELINE_ROWS:
            msg = f'Collecting baseline: {baseline_count}/{MIN_BASELINE_ROWS} engine-on readings'
            logger.debug(msg)
            with _risk_lock:
                _risk_state = {
                    '_meta': {
                        'status': 'COLLECTING_BASELINE',
                        'message': msg,
                        'baseline_count': baseline_count,
                        'required': MIN_BASELINE_ROWS,
                        'updated_at': now_utc.isoformat(),
                    }
                }
            return

        if not check_rows:
            logger.debug('No engine-on readings in check window — engine off or idle')
            with _risk_lock:
                _risk_state = {
                    '_meta': {
                        'status': 'ENGINE_OFF',
                        'message': f'No engine-on readings in last {CHECK_WINDOW_HOURS}h',
                        'baseline_count': baseline_count,
                        'updated_at': now_utc.isoformat(),
                    }
                }
            return

        alerts_enabled = _is_predictive_alerts_enabled()
        new_risk = {}

        for field, (category, sigma_severity, direction) in FIELD_CONFIG.items():
            # Baseline stats for this field
            baseline_vals = [r[field] for r in baseline_rows if r[field] is not None]
            if len(baseline_vals) < MIN_BASELINE_ROWS:
                new_risk[field] = {
                    'status': 'OK',
                    'message': f'Insufficient {field} baseline readings ({len(baseline_vals)})',
                    'updated_at': now_utc.isoformat(),
                }
                continue

            mean  = statistics.mean(baseline_vals)
            stdev = statistics.stdev(baseline_vals) if len(baseline_vals) > 1 else 0.0

            # Scan all check-window readings for this field
            worst_status  = 'OK'
            worst_message = f'{field}: normal (baseline {mean:.1f} ± {stdev:.1f})'

            for row in check_rows:
                val = row[field]
                if val is None:
                    continue

                # Hard limit check
                if field in HARD_LIMITS:
                    op, limit, hcat, hsev, hmsg = HARD_LIMITS[field]
                    if (op == '>' and val > limit) or (op == '<' and val < limit):
                        msg = hmsg.format(val=val)
                        worst_status  = 'ALERT'
                        worst_message = msg
                        if alerts_enabled:
                            write_issue(hcat, hsev, msg)
                        break  # ALERT is highest — no need to scan further

                # 2σ anomaly
                if stdev > 0:
                    z = (val - mean) / stdev
                    alert_high = direction in ('high', 'both') and z >  2.0
                    alert_low  = direction in ('low',  'both') and z < -2.0
                    if alert_high or alert_low:
                        direction_word = 'high' if alert_high else 'low'
                        msg = (f'{field} {direction_word}: {val:.1f} '
                               f'(baseline {mean:.1f} ± {stdev:.1f}, z={z:.1f})')
                        if worst_status != 'ALERT':
                            worst_status  = 'WATCH'
                            worst_message = msg
                        if alerts_enabled:
                            write_issue(category, sigma_severity, msg)

            new_risk[field] = {
                'status':     worst_status,
                'message':    worst_message,
                'updated_at': now_utc.isoformat(),
            }

        with _risk_lock:
            _risk_state = new_risk
            _risk_state['_meta'] = {
                'status':          'ACTIVE',
                'baseline_count':  baseline_count,
                'check_rows':      len(check_rows),
                'alerts_enabled':  alerts_enabled,
                'updated_at':      now_utc.isoformat(),
            }

        # Boatlog + voice alert for any WATCH or ALERT field
        voice_enabled = _is_voice_alert_enabled()
        for field, risk in new_risk.items():
            status = risk.get('status', 'OK')
            if status in ('WATCH', 'ALERT') and _can_write_alert(f'boatlog_{field}'):
                write_boatlog(risk['message'])
                _alert_times[f'boatlog_{field}'] = time.monotonic()
                if voice_enabled and status == 'ALERT':
                    speak_alert(f'Predictive alert. {risk["message"]}')

        logger.info(
            f'Detection run: {len(check_rows)} check rows, {baseline_count} baseline rows. '
            f'Risk: { {k: v["status"] for k, v in new_risk.items()} }'
        )

    except Exception as e:
        logger.error(f'Anomaly detection error: {e}')


# ── Background threads ────────────────────────────────────────────────────────

def historian_thread():
    logger.info('Historian thread started')
    purge_counter = 0
    while True:
        try:
            snap = read_engine_snapshot()
            store_snapshot(snap)
            logger.debug(
                f'Stored: engine_on={snap["engine_on"]} rpm={snap["rpm"]} '
                f'coolant={snap["coolant_temp_c"]} oil={snap["oil_pressure_kpa"]}'
            )
            purge_counter += 1
            if purge_counter >= 1440:   # roughly daily at 60s intervals
                purge_old_rows()
                purge_counter = 0
        except Exception as e:
            logger.error(f'Historian error: {e}')
        time.sleep(POLL_INTERVAL)


def detector_thread():
    logger.info('Detector thread started')
    time.sleep(120)   # let historian collect a few readings first
    while True:
        try:
            detect_anomalies()
        except Exception as e:
            logger.error(f'Detector thread error: {e}')
        time.sleep(DETECT_INTERVAL)


# ── Flask routes (only registered when Flask is available) ────────────────────

def _register_routes(application):
    @application.route('/predictive/health', methods=['GET'])
    def health():
        return jsonify({'status': 'healthy', 'service': 'predictive-maintenance', 'port': PORT})

    @application.route('/predictive/status', methods=['GET'])
    def status():
        with _risk_lock:
            state = dict(_risk_state)
        levels = {'OK': 0, 'WATCH': 1, 'ALERT': 2}
        overall = 'OK'
        for key, val in state.items():
            if key.startswith('_'):
                continue
            s = val.get('status', 'OK')
            if levels.get(s, 0) > levels.get(overall, 0):
                overall = s
        return jsonify({
            'overall_risk': overall,
            'fields':       {k: v for k, v in state.items() if not k.startswith('_')},
            'meta':         state.get('_meta', {}),
            'updated_at':   datetime.now(timezone.utc).isoformat(),
        })

    @application.route('/predictive/history', methods=['GET'])
    def history():
        limit = min(int(flask_request.args.get('limit', 200)), 2000)
        source = flask_request.args.get('source')   # optional filter: 'signalk' or 'test'
        try:
            with sqlite3.connect(str(HIST_DB)) as conn:
                conn.row_factory = sqlite3.Row
                if source:
                    rows = conn.execute(
                        "SELECT * FROM engine_snapshots WHERE source = ? ORDER BY ts DESC LIMIT ?",
                        (source, limit)
                    ).fetchall()
                else:
                    rows = conn.execute(
                        "SELECT * FROM engine_snapshots ORDER BY ts DESC LIMIT ?", (limit,)
                    ).fetchall()
            return jsonify({'count': len(rows), 'readings': [dict(r) for r in rows]})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @application.route('/predictive/baseline', methods=['GET'])
    def baseline():
        try:
            with sqlite3.connect(str(HIST_DB)) as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute(
                    "SELECT * FROM engine_snapshots WHERE engine_on = 1 "
                    "ORDER BY ts DESC LIMIT ?",
                    (BASELINE_WINDOW,)
                ).fetchall()
            stats = {}
            for field in ('rpm', 'oil_pressure_kpa', 'coolant_temp_c',
                          'boost_pressure_kpa', 'fuel_level_pct'):
                vals = [r[field] for r in rows if r[field] is not None]
                if len(vals) >= 2:
                    stats[field] = {
                        'count': len(vals),
                        'mean':  round(statistics.mean(vals), 2),
                        'stdev': round(statistics.stdev(vals), 2),
                        'min':   round(min(vals), 2),
                        'max':   round(max(vals), 2),
                    }
                else:
                    stats[field] = {'count': len(vals), 'note': 'insufficient data'}
            return jsonify({'baseline_window': BASELINE_WINDOW, 'fields': stats})
        except Exception as e:
            return jsonify({'error': str(e)}), 500


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    if not _flask_available:
        print('ERROR: Flask is required to run the service. Install: sudo apt install python3-flask')
        raise SystemExit(1)

    _init_logging()
    init_db()
    _register_routes(app)
    logger.info(f'Starting d3kOS Predictive Maintenance on port {PORT}')

    threading.Thread(target=historian_thread, daemon=True, name='historian').start()
    threading.Thread(target=detector_thread,  daemon=True, name='detector').start()

    app.run(host='127.0.0.1', port=PORT, debug=False)
