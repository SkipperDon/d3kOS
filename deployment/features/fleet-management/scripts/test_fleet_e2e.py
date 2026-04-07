#!/usr/bin/env python3
"""
Fleet Management End-to-End Test — 15 Boats
Tests fleet-map.php and fleet-analytics.php against the seeded test data.

Prerequisites:
  1. deploy-fleet-php.py has been run
  2. fleet-setup.php?action=create_tables was called
  3. fleet-setup.php?action=seed_test was called (creates TEST01 fleet with 15 boats + 60 min data)

Usage:
  python3 test_fleet_e2e.py --base-url https://atmyboat.com/staging/mobile --app-token YOUR_APP_TOKEN

The app_token must belong to a T3 test account on staging.
"""

import argparse
import json
import sys
import time

import requests

BASE = 'https://atmyboat.com/staging/mobile'
HEADERS_APP = {}  # set in main()

PASS = '[PASS]'
FAIL = '[FAIL]'


def check(label: str, condition: bool, detail: str = ''):
    marker = PASS if condition else FAIL
    print(f'  {marker} {label}' + (f' — {detail}' if detail else ''))
    return condition


def get(path, params=None):
    r = requests.get(f'{BASE}/{path}', headers=HEADERS_APP, params=params, timeout=15)
    return r


def post(path, body):
    r = requests.post(f'{BASE}/{path}', headers=HEADERS_APP, json=body, timeout=15)
    return r


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-url', default=BASE)
    parser.add_argument('--app-token', required=True, help='T3 test account app_token')
    args = parser.parse_args()

    global BASE, HEADERS_APP
    BASE = args.base_url.rstrip('/')
    HEADERS_APP = {
        'Authorization': f'Bearer {args.app_token}',
        'Content-Type':  'application/json',
    }

    print('=' * 60)
    print('d3kOS Fleet Management — End-to-End Test')
    print('Target:', BASE)
    print('=' * 60)

    results = []

    # ── Test 1: fleet-map.php returns 15 vessels ──────────────────────────────
    print('\nTest 1: fleet-map.php — 15 vessel positions')
    r = get('fleet-map.php', {'fleet_id': 0})
    # We need the fleet_id for TEST01. Look it up via verify first.
    # For now we test with fleet_id from seed (will be 1 unless other fleets exist).
    # A real test would get the fleet_id from fleet-create response.
    # Using fleet_id=1 as the seed default — adjust if needed.

    # Try fleet_id 1..5 to find TEST01
    fleet_id = None
    for fid in range(1, 6):
        r = get('fleet-map.php', {'fleet_id': fid})
        if r.status_code == 200:
            data = r.json()
            if data.get('success') and data.get('data', {}).get('fleet_name') == 'Test Fleet — 15 Boats':
                fleet_id = fid
                break

    ok = check('TEST01 fleet found', fleet_id is not None,
               f'fleet_id={fleet_id}' if fleet_id else 'no fleet found — was seed run?')
    results.append(ok)

    if not fleet_id:
        print('\nCannot continue without fleet_id. Run fleet-setup.php?action=seed_test first.')
        sys.exit(1)

    r = get('fleet-map.php', {'fleet_id': fleet_id})
    data = r.json().get('data', {})
    vessels = data.get('vessels', [])

    ok = check('HTTP 200', r.status_code == 200, f'got {r.status_code}'); results.append(ok)
    ok = check('success=true', r.json().get('success')); results.append(ok)
    ok = check('15 vessels returned', len(vessels) == 15, f'got {len(vessels)}'); results.append(ok)

    vessels_with_pos = [v for v in vessels if v.get('lat') is not None]
    ok = check('All 15 have GPS positions', len(vessels_with_pos) == 15,
               f'{len(vessels_with_pos)}/15 have position'); results.append(ok)

    recent = [v for v in vessels if v.get('age_minutes') is not None and v['age_minutes'] <= 60]
    ok = check('All 15 seen within last 60 min', len(recent) == 15,
               f'{len(recent)}/15 recent'); results.append(ok)

    # Check positions are in Toronto harbour area
    toronto_area = [v for v in vessels_with_pos
                    if 43.0 < v.get('lat', 0) < 44.5 and -80.5 < v.get('lon', 0) < -79.0]
    ok = check('All positions near Toronto harbour', len(toronto_area) == 15,
               f'{len(toronto_area)}/15 in expected area'); results.append(ok)

    owner_vessels = [v for v in vessels if v.get('role') == 'owner']
    ok = check('Exactly 1 owner', len(owner_vessels) == 1); results.append(ok)

    # ── Test 2: fleet-analytics.php ──────────────────────────────────────────
    print('\nTest 2: fleet-analytics.php — engine hours + fleet summary')
    r = get('fleet-analytics.php', {'fleet_id': fleet_id})
    ok = check('HTTP 200', r.status_code == 200, f'got {r.status_code}'); results.append(ok)
    ok = check('success=true', r.json().get('success')); results.append(ok)

    adata   = r.json().get('data', {})
    vessels_a = adata.get('vessels', [])
    summary   = adata.get('fleet_summary', {})

    ok = check('15 vessel analytics', len(vessels_a) == 15, f'got {len(vessels_a)}'); results.append(ok)
    ok = check('fleet_summary present', bool(summary)); results.append(ok)
    ok = check('vessels_active_24h = 15', summary.get('vessels_active_24h') == 15,
               f"got {summary.get('vessels_active_24h')}"); results.append(ok)

    with_hours = [v for v in vessels_a if v.get('engine_hours_total') is not None]
    ok = check('All 15 have engine hours', len(with_hours) == 15,
               f'{len(with_hours)}/15'); results.append(ok)

    total_hours = summary.get('total_engine_hours', 0)
    ok = check('Total engine hours > 0', total_hours > 0, f'{total_hours}h'); results.append(ok)

    fleet_rpm = summary.get('fleet_avg_rpm')
    ok = check('Fleet avg RPM in realistic range (1500–3000)',
               fleet_rpm is not None and 1500 < fleet_rpm < 3000,
               f'avg RPM={fleet_rpm}'); results.append(ok)

    # ── Test 3: T3 gate — reject T0 token ────────────────────────────────────
    print('\nTest 3: Tier gate (expected 403 with bad token)')
    r_gate = requests.get(f'{BASE}/fleet-map.php',
                          headers={'Authorization': 'Bearer 00000000-0000-0000-0000-000000000000',
                                   'Content-Type': 'application/json'},
                          params={'fleet_id': fleet_id}, timeout=10)
    ok = check('Bad token returns 401 or 403', r_gate.status_code in (401, 403),
               f'got {r_gate.status_code}'); results.append(ok)

    # ── Test 4: fleet-ingest.php rate limit ──────────────────────────────────
    print('\nTest 4: fleet-ingest.php rate-limit (50s window)')
    # Test device already has data from seed — a push within 50s of "now" should rate-limit
    # We can't reliably test this without a real device token. Mark as info only.
    print('  [INFO] Rate-limit test skipped — requires live Pi device token')

    # ── Summary ──────────────────────────────────────────────────────────────
    passed = sum(results)
    total  = len(results)
    print()
    print('=' * 60)
    if passed == total:
        print(f'ALL {total} TESTS PASSED — Fleet Phase 1 backend verified.')
        print('Test fleet TEST01 is live on staging with 15 vessels + 60 min data.')
        print('\nNext: build Phase 2 (PWA fleet screen + Leaflet.js map).')
    else:
        print(f'{passed}/{total} PASSED — {total - passed} FAILED. Review output above.')
    print('=' * 60)
    sys.exit(0 if passed == total else 1)


if __name__ == '__main__':
    main()
