#!/usr/bin/env python3
"""
d3kOS Boatlog Capture Service — BUG-24 Option A
Polls SignalK every 5 s for engine RPM; writes start/running/stop entries
to boatlog.db without requiring any browser page to be open.

Model: predictive_maintenance.py — copy its four patterns verbatim:
  1. SK REST on localhost (not WebSocket)
  2. Write straight to boatlog.db — no HTTP hop
  3. Guard on DB absence rather than crashing
  4. Cooldown / debounce to suppress repeats
"""

import logging
import sqlite3
import time
import uuid
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path

import requests

# ── Config ────────────────────────────────────────────────────────────────────
BOATLOG_DB        = Path('/opt/d3kos/data/boatlog/boatlog.db')
LOG_FILE          = Path('/opt/d3kos/logs/boatlog-capture.log')

# localhost is correct here — this is server-side Python on the Pi (not a browser).
# BUG-46/48 removed localhost from front-end code; server code keeps it.
SK_ENGINE_URL     = 'http://localhost:8099/signalk/v1/api/vessels/self/propulsion/port'
SK_FUEL_URL       = 'http://localhost:8099/signalk/v1/api/vessels/self/tanks/fuel/0'

POLL_INTERVAL_S   = 5
RPM_THRESHOLD_HZ  = 3       # 3 Hz = 180 RPM — matches boatlog-engine.js:18
DEBOUNCE_SAMPLES  = 3       # 3 consecutive samples (15 s) must agree before state flip
SNAPSHOT_INTERVAL = 30 * 60 # one running entry every 30 min — matches boatlog-engine.js:19

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logger = logging.getLogger('boatlog_capture')
logger.setLevel(logging.INFO)
_fh = RotatingFileHandler(str(LOG_FILE), maxBytes=2 * 1024 * 1024, backupCount=3)
_fh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(_fh)
logger.addHandler(logging.StreamHandler())  # also to stdout → journald

# ── State ────────────────────────────────────────────────────────────────────
_engine_running     = False
_session_start_time = None          # monotonic time when engine started
_debounce_buf       = []            # list of bool: last DEBOUNCE_SAMPLES readings
_last_snapshot_ts   = 0.0           # monotonic time of last running-snapshot write


# ── DB writer (pattern from predictive_maintenance.py:write_boatlog) ──────────

def _write_entry(entry_type: str, content: str) -> None:
    if not BOATLOG_DB.exists():
        logger.debug('boatlog.db not found — skipping entry')
        return
    eid = str(uuid.uuid4())
    ts  = datetime.now(timezone.utc).isoformat()
    try:
        with sqlite3.connect(str(BOATLOG_DB)) as conn:
            conn.execute(
                "INSERT INTO boatlog_entries "
                "(entry_id, timestamp, entry_type, content, latitude, longitude, weather_conditions) "
                "VALUES (?, ?, ?, ?, NULL, NULL, NULL)",
                (eid, ts, entry_type, content)
            )
            conn.commit()
        logger.info('Wrote boatlog entry: %s', content)
    except Exception as exc:
        logger.error('Failed to write boatlog entry: %s', exc)


# ── SK reader (pattern from predictive_maintenance.py:read_engine_snapshot) ───

def _read_sk() -> dict:
    """Return {'rpm_hz': float|None, 'oil_psi': float|None, 'coolant_f': float|None,
               'fuel_pct': float|None}. None for any value SK did not supply."""
    data = {'rpm_hz': None, 'oil_psi': None, 'coolant_f': None, 'fuel_pct': None}
    try:
        r    = requests.get(SK_ENGINE_URL, timeout=5)
        prop = r.json()

        rev = prop.get('revolutions', {}).get('value')
        if rev is not None:
            data['rpm_hz'] = float(rev)

        oil = prop.get('oilPressure', {}).get('value')
        if oil is not None:
            # SK delivers Pascals; convert to PSI for operator preference (Imperial)
            data['oil_psi'] = round(oil * 0.000145038, 1)

        temp = prop.get('temperature', {}).get('value')
        if temp is not None:
            # SK delivers Kelvin; convert to °F
            data['coolant_f'] = round((temp - 273.15) * 9 / 5 + 32, 1)

        try:
            r2 = requests.get(SK_FUEL_URL, timeout=3)
            fuel = r2.json().get('currentLevel', {}).get('value')
            if fuel is not None:
                data['fuel_pct'] = round(float(fuel) * 100, 1)
        except Exception:
            pass

    except Exception as exc:
        logger.debug('SK read failed (engine may be off or SK not running): %s', exc)
    return data


def _is_running(sk: dict) -> bool:
    rpm_hz = sk.get('rpm_hz')
    return rpm_hz is not None and rpm_hz > RPM_THRESHOLD_HZ


def _format_readings(sk: dict) -> str:
    parts = []
    if sk['rpm_hz'] is not None:
        parts.append(f"{int(sk['rpm_hz'] * 60)} RPM")
    if sk['oil_psi'] is not None:
        parts.append(f"oil {sk['oil_psi']} PSI")
    if sk['coolant_f'] is not None:
        parts.append(f"coolant {sk['coolant_f']} °F")
    if sk['fuel_pct'] is not None:
        parts.append(f"fuel {sk['fuel_pct']}%")
    return ', '.join(parts) if parts else 'no readings'


def _duration_str(elapsed_s: float) -> str:
    h = int(elapsed_s) // 3600
    m = (int(elapsed_s) % 3600) // 60
    if h:
        return f'{h} h {m} min'
    return f'{m} min'


# ── Main loop ─────────────────────────────────────────────────────────────────

def run() -> None:
    global _engine_running, _session_start_time, _debounce_buf, _last_snapshot_ts

    logger.info('boatlog_capture started (poll=%ds, threshold=%s Hz, debounce=%d samples)',
                POLL_INTERVAL_S, RPM_THRESHOLD_HZ, DEBOUNCE_SAMPLES)

    while True:
        try:
            sk      = _read_sk()
            running = _is_running(sk)

            # Debounce: keep last DEBOUNCE_SAMPLES readings; only flip state when all agree
            _debounce_buf.append(running)
            if len(_debounce_buf) > DEBOUNCE_SAMPLES:
                _debounce_buf.pop(0)

            if len(_debounce_buf) == DEBOUNCE_SAMPLES and len(set(_debounce_buf)) == 1:
                debounced = _debounce_buf[0]

                if debounced and not _engine_running:
                    # Engine just started
                    _engine_running     = True
                    _session_start_time = time.monotonic()
                    _last_snapshot_ts   = _session_start_time
                    content = f'[Auto] Engine started — {_format_readings(sk)}'
                    _write_entry('engine', content)

                elif not debounced and _engine_running:
                    # Engine just stopped
                    elapsed = time.monotonic() - (_session_start_time or time.monotonic())
                    _engine_running     = False
                    _session_start_time = None
                    content = f'[Auto] Engine stopped — ran {_duration_str(elapsed)}'
                    _write_entry('engine', content)
                    _debounce_buf = []

                elif debounced and _engine_running:
                    # Running snapshot every 30 min
                    if time.monotonic() - _last_snapshot_ts >= SNAPSHOT_INTERVAL:
                        _last_snapshot_ts = time.monotonic()
                        content = f'[Auto] Engine running — {_format_readings(sk)}'
                        _write_entry('engine', content)

        except Exception as exc:
            logger.error('Unexpected error in poll loop: %s', exc)

        time.sleep(POLL_INTERVAL_S)


if __name__ == '__main__':
    run()
