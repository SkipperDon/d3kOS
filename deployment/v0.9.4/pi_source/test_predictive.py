#!/usr/bin/env python3
"""
TDD Validation — v0.9.5 Predictive Maintenance
Verifies the anomaly detector fires on known injected anomalies and does NOT
fire on normal baseline readings.

Run BEFORE generate_test_data.py: service exists, DB is created, no test data yet.
Run AFTER generate_test_data.py:  should pass all assertions.

Test sequence:
  1. Create temp DB (isolated from production data)
  2. Insert 1000 normal baseline readings
  3. Insert 3 anomalous readings (coolant spike, oil drop, rpm spike)
  4. Call detect_anomalies() directly (no service required)
  5. Assert:
       - coolant_temp_c  → ALERT  (107°C exceeds 100°C hard limit)
       - oil_pressure_kpa → ALERT (180 kPa below 150 kPa hard limit)
       - rpm              → WATCH  (3800 is > 2σ above 2200±150 baseline)
  6. Clear anomalous readings, insert 3 normal readings
  7. Re-run detect_anomalies()
  8. Assert all fields → OK (no false positives)

Usage: python3 test_predictive.py
Exit code: 0 = all pass, 1 = one or more failures
"""

import random
import sqlite3
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Resolve module: Pi production path first, fall back to repo path (local dev/test)
sys.path.insert(0, '/opt/d3kos/services/predictive')
sys.path.insert(0, str(Path(__file__).parent))

import predictive_maintenance as pm

# ── Setup ─────────────────────────────────────────────────────────────────────

tmp = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
TEST_DB = Path(tmp.name)
tmp.close()

print(f'Test DB: {TEST_DB}')
pm.init_db(TEST_DB)


def insert_readings(rows_data, hours_ago_start=None, hours_ago_end=None):
    """
    Insert list of (rpm, oil_pressure_kpa, coolant_temp_c) tuples as engine-on rows.
    hours_ago_start/end: spread timestamps over that age range (past).
    Default: last 23 hours (within the 24h check window).
    """
    now = datetime.now(timezone.utc)
    h_start = hours_ago_start if hours_ago_start is not None else 23
    h_end   = hours_ago_end   if hours_ago_end   is not None else 0
    total = len(rows_data)
    with sqlite3.connect(str(TEST_DB)) as conn:
        for i, (rpm, oil, coolant) in enumerate(rows_data):
            # Spread evenly from h_start hours ago to h_end hours ago
            fraction = i / max(total - 1, 1)
            hours_offset = h_start - fraction * (h_start - h_end)
            ts = (now - timedelta(hours=hours_offset)).isoformat()
            conn.execute("""
                INSERT INTO engine_snapshots
                  (ts, rpm, oil_pressure_kpa, coolant_temp_c, boost_pressure_kpa,
                   fuel_level_pct, engine_hours, engine_on, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1, 'test')
            """, (ts, rpm, oil, coolant, 95.0, 60.0, float(i) / 60))
        conn.commit()


def clear_readings():
    with sqlite3.connect(str(TEST_DB)) as conn:
        conn.execute("DELETE FROM engine_snapshots")
        conn.commit()


def run_detection():
    pm.detect_anomalies(db_path=TEST_DB)
    import threading
    with pm._risk_lock:
        return dict(pm._risk_state)


# ── Build baseline (1000 normal readings — older than 24h check window) ────────

print('Inserting 1000 normal baseline readings (3–28 days old — outside check window)...')
normal = [
    (int(random.gauss(2200, 150)), round(random.gauss(310.0, 15.0), 1), round(random.gauss(82.0, 4.0), 1))
    for _ in range(1000)
]
insert_readings(normal, hours_ago_start=672, hours_ago_end=25)   # 28 days → 25 hours ago
print('  Done.')

# ── Phase 1: Anomaly detection ─────────────────────────────────────────────────

print('\nInserting 3 anomalous readings (within last 30 min — inside check window)...')
anomalous = [
    (2200, 310.0, 107.0),   # coolant spike → ALERT  (hard limit > 100°C)
    (2200, 140.0, 82.0),    # oil drop 140 kPa → ALERT (hard limit < 150 kPa)
    (3800, 310.0, 82.0),    # rpm spike → WATCH (2σ above 2200±150)
]
insert_readings(anomalous, hours_ago_start=0.5, hours_ago_end=0)

print('Running detect_anomalies()...')
state = run_detection()

print()
print('─' * 60)
print('PHASE 1: Anomaly detection results')
print('─' * 60)

passed = True

checks = [
    ('coolant_temp_c',   'ALERT', 'coolant spike 107°C → hard limit > 100°C'),
    ('oil_pressure_kpa', 'ALERT', 'oil drop 140 kPa → hard limit < 150 kPa'),
    ('rpm',              'WATCH', 'rpm spike 3800 → 2σ above 2200±150'),
]

for field, expected_status, description in checks:
    field_state = state.get(field, {})
    actual      = field_state.get('status', 'MISSING')
    ok          = actual == expected_status
    if not ok:
        passed = False
    marker = 'PASS' if ok else 'FAIL'
    print(f'  [{marker}] {field}: expected {expected_status}, got {actual}')
    print(f'         {description}')
    if not ok:
        print(f'         message: {field_state.get("message", "(no message)")}')

# ── Phase 2: No false positives ───────────────────────────────────────────────

print()
print('─' * 60)
print('PHASE 2: False positive check (normal readings only)')
print('─' * 60)

# Clear all rows and insert only normal readings
clear_readings()
print('Inserting 1000 normal baseline readings (old) + 3 normal recent readings...')
normal2 = [
    (int(random.gauss(2200, 150)), round(random.gauss(310.0, 15.0), 1), round(random.gauss(82.0, 4.0), 1))
    for _ in range(1000)
]
insert_readings(normal2, hours_ago_start=672, hours_ago_end=25)   # baseline outside window

# 3 recent readings — all well within normal range (no Gaussian variation — fixed values)
normal_recent = [
    (2200, 310.0, 82.0),
    (2210, 308.0, 81.5),
    (2195, 312.0, 82.5),
]
insert_readings(normal_recent, hours_ago_start=0.5, hours_ago_end=0)

print('Running detect_anomalies()...')
state2 = run_detection()

for field in ('coolant_temp_c', 'oil_pressure_kpa', 'rpm'):
    field_state = state2.get(field, {})
    actual      = field_state.get('status', 'MISSING')
    ok          = actual == 'OK'
    if not ok:
        passed = False
    marker = 'PASS' if ok else 'FAIL'
    print(f'  [{marker}] {field}: expected OK, got {actual}')

# ── Cleanup ───────────────────────────────────────────────────────────────────
import os
try:
    os.unlink(TEST_DB)
    print(f'\nTemp DB cleaned up.')
except Exception:
    pass

# ── Summary ───────────────────────────────────────────────────────────────────
print()
print('═' * 60)
if passed:
    print('ALL TESTS PASSED — predictive_maintenance.py anomaly detection is working.')
    print('Next: run generate_test_data.py on Pi to load data into production DB.')
else:
    print('ONE OR MORE TESTS FAILED — review output above before deploying.')
print('═' * 60)

sys.exit(0 if passed else 1)
