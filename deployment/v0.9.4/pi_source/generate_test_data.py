#!/usr/bin/env python3
"""
v0.9.5 Test Data Generator
Generates 2,000 synthetic engine readings (30 synthetic days) with 3 known anomalies.
Used to validate the predictive maintenance anomaly detector without waiting for
on-water data.

Anomaly injection (all in last 24h of test data so detection window captures them):
  Reading 1997: coolant_temp_c  = 107.0°C    → expect engine_overtemp ALERT (hard limit)
  Reading 1998: oil_pressure_kpa = 180.0 kPa → expect engine_oil_pressure ALERT (hard limit)
  Reading 1999: rpm = 3,800                  → expect engine_roughness WATCH (2σ)

Normal baseline parameters (readings 0–1996):
  RPM:          2,200 ± 150 rpm
  Coolant:      82.0  ± 4.0 °C
  Oil pressure: 310.0 ± 15.0 kPa
  Boost:        95.0  ± 5.0 kPa
  Fuel:         starts at 95%, decreases ~3.2%/hr at cruise

Usage:
  python3 generate_test_data.py           # generate 2000 readings
  python3 generate_test_data.py --clear   # delete existing test rows first
  python3 generate_test_data.py --status  # show count of test rows in DB
"""

import argparse
import random
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Must match predictive_maintenance.py
HIST_DB = Path('/opt/d3kos/data/predictive/engine_history.db')

TOTAL_READINGS  = 2000
SPAN_DAYS       = 30

# Anomalies at final 3 readings (within last 24h of test data)
# These are the last 3 readings so they fall in the 24h detection window
ANOMALY_IDX = {
    1997: {'coolant_temp_c':   107.0},   # hard limit: > 100°C → ALERT
    1998: {'oil_pressure_kpa': 140.0},   # hard limit: < 150 kPa → ALERT
    1999: {'rpm':              3800},    # 2σ above baseline 2200±150 → WATCH
}


def generate(db_path=None, clear=False):
    p = db_path or HIST_DB

    if not p.exists():
        print(f'ERROR: {p} not found.')
        print('Run predictive_maintenance.py first to create the database, or:')
        print('  python3 -c "from predictive_maintenance import init_db; init_db()"')
        return False

    with sqlite3.connect(str(p)) as conn:
        if clear:
            deleted = conn.execute(
                "DELETE FROM engine_snapshots WHERE source = 'test'"
            ).rowcount
            conn.commit()
            print(f'Cleared {deleted} existing test rows.')

        existing = conn.execute(
            "SELECT COUNT(*) FROM engine_snapshots WHERE source = 'test'"
        ).fetchone()[0]
        if existing > 0:
            print(f'WARNING: {existing} test rows already in DB. Use --clear to remove first.')
            return False

        # Timestamps: end 1 minute ago so they're all "in the past"
        # Last 3 readings are within the last 24h (start of last day)
        end_dt    = datetime.now(timezone.utc) - timedelta(minutes=1)
        start_dt  = end_dt - timedelta(days=SPAN_DAYS)
        interval  = (end_dt - start_dt) / TOTAL_READINGS  # ~21.6 min per reading

        fuel_pct = 95.0
        rows = []

        for i in range(TOTAL_READINGS):
            ts = (start_dt + interval * i).isoformat()

            rpm            = int(random.gauss(2200, 150))
            coolant_temp   = round(random.gauss(82.0, 4.0), 1)
            oil_pressure   = round(random.gauss(310.0, 15.0), 1)
            boost_pressure = round(random.gauss(95.0, 5.0), 1)

            # Fuel decreases over time
            fuel_pct = max(5.0, fuel_pct - (3.2 / 60) * (interval.total_seconds() / 60))
            fuel = round(fuel_pct, 1)

            engine_hours = round((interval.total_seconds() * i) / 3600, 2)

            # Apply anomaly overrides at known positions
            if i in ANOMALY_IDX:
                for field, val in ANOMALY_IDX[i].items():
                    if field == 'coolant_temp_c':
                        coolant_temp = val
                    elif field == 'oil_pressure_kpa':
                        oil_pressure = val
                    elif field == 'rpm':
                        rpm = val

            rows.append((
                ts, rpm, oil_pressure, coolant_temp, boost_pressure,
                fuel, engine_hours, 1, 'test'
            ))

        conn.executemany("""
            INSERT INTO engine_snapshots
              (ts, rpm, oil_pressure_kpa, coolant_temp_c, boost_pressure_kpa,
               fuel_level_pct, engine_hours, engine_on, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, rows)
        conn.commit()

    print(f'Generated {len(rows)} test readings spanning {SPAN_DAYS} days.')
    print()
    print('Known anomalies injected (last 3 readings — within 24h detection window):')
    print('  Reading 1997: coolant_temp_c  = 107.0°C   → expect engine_overtemp  ALERT')
    print('  Reading 1998: oil_pressure_kpa = 140.0 kPa → expect engine_oil_pressure ALERT')
    print('  Reading 1999: rpm             = 3800       → expect engine_roughness WATCH')
    print()
    print('Next steps:')
    print('  1. Ensure predictive_maintenance.py is running (or call detect_anomalies() directly)')
    print('  2. Wait up to 5 minutes for the detector to run, OR:')
    print('     python3 test_predictive.py    ← runs validation immediately')
    print('  3. curl http://localhost:8106/predictive/status')
    print('  4. curl http://localhost:8106/predictive/baseline')
    return True


def status(db_path=None):
    p = db_path or HIST_DB
    if not p.exists():
        print(f'DB not found: {p}')
        return
    with sqlite3.connect(str(p)) as conn:
        total = conn.execute("SELECT COUNT(*) FROM engine_snapshots").fetchone()[0]
        test  = conn.execute(
            "SELECT COUNT(*) FROM engine_snapshots WHERE source = 'test'"
        ).fetchone()[0]
        live  = conn.execute(
            "SELECT COUNT(*) FROM engine_snapshots WHERE source = 'signalk'"
        ).fetchone()[0]
    print(f'engine_history.db rows: {total} total | {live} signalk | {test} test')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='v0.9.5 test data generator')
    parser.add_argument('--clear',  action='store_true', help='Delete test rows before generating')
    parser.add_argument('--status', action='store_true', help='Show row counts and exit')
    args = parser.parse_args()

    if args.status:
        status()
    else:
        generate(clear=args.clear)
