# v0.9.6 Fleet Management — Build Checklist
**Version:** 1.1 | **Created:** 2026-04-07 S21 | **Updated:** 2026-04-07 S21 — design questions resolved | **Status:** READY TO BUILD

---

## Strategy

- Build and test entirely on **HostPapa staging** (`atmyboat.com/staging/`) + **local Pi**
- v0.9.4.1 multi-boat data pipeline **absorbed into Phase 1** — no separate version milestone
- Phase 4 live push is NOT a prerequisite — staging-first removes that blocker
- Tier 3 gate tested with test accounts on staging before any live push

---

## Architecture

```
Pi (each vessel)
  └── fleet_push_service.py (Port 8107)
        │  Every 1 min (when engine on or GPS fix active): GPS position + engine snapshot
        │  Only when engine_on OR GPS fix active
        └─► POST fleet-ingest.php (HostPapa staging)
                │  Auth: device_token + fleet_id
                └─► MySQL: amboat_fleet_vessels
                           amboat_fleet_positions
                           amboat_fleet_engine_snapshots

PWA (phone)
  └── Fleet screen
        ├── fleet-map.php     → Leaflet.js positions
        ├── fleet-analytics.php → engine hours, alerts
        └── fleet-create.php / fleet-join.php → fleet admin
```

---

## Phase 1 — Infrastructure: Pi Data Push + HostPapa Fleet Endpoints

### MySQL Schema (run on staging DB)
- [x] `amboat_fleets` — fleet_id, fleet_code (6-char), name, type (charter/fishing/marina), owner_device_token, created_at
- [x] `amboat_fleet_members` — fleet_id, device_token, role (owner/member/view), joined_at
- [x] `amboat_fleet_positions` — fleet_id, device_token, lat, lon, cog, sog, ts — keep last 24h only
- [x] `amboat_fleet_engine_snapshots` — fleet_id, device_token, rpm, oil_pressure_kpa, coolant_temp_c, engine_hours, ts — keep last 7 days
*Schema deployed via `fleet-setup.php?action=create_tables` — see deploy instructions below*

### HostPapa PHP endpoints
- [x] `fleet-setup.php` — one-shot schema + test data seeder. Delete after testing.
- [x] `fleet-create.php` — POST, app_token auth. Creates fleet record, returns fleet_code. One fleet per device max. T3 gate.
- [x] `fleet-join.php` — POST, app_token + fleet_code. Adds device as member. 15-vessel cap enforced. T3 gate.
- [x] `fleet-ingest.php` — POST, AMBOAT_API_KEY + X-Device-Token. Writes position + engine snapshot. Prunes old rows (24h position, 7d engine). Rate-limited: max 1 write per 50s per device.
- [x] `fleet-map.php` — GET, app_token + fleet_id. Returns all member positions (last known). T3 gate.
- [x] `fleet-analytics.php` — GET, app_token + fleet_id. Returns per-vessel engine hours, avg RPM/coolant/oil (24h), fleet summary. T3 gate.

### Pi fleet_push_service.py (Port 8107)
- [x] New systemd service `d3kos-fleet-push.service` — written
- [x] Reads fleet_id from `/opt/d3kos/config/fleet.json` (written when owner joins fleet via PWA)
- [x] **1-minute push interval** when engine_on=True OR GPS fix active (operator confirmed 2026-04-07)
- [x] Idles (no push, no CPU) when engine off AND no GPS fix — prevents background drain at dock
- [x] Only runs when fleet_id is set (no fleet_id = service idles, no network calls)
- [x] Respects Tier gate: T3 only — reads tier from `license.json` before each push
- [ ] **DEPLOY TO PI** — not yet on Pi (pending staging test confirmation)
- [ ] TDD: test 1-min push fires, test idle when no fleet_id, test tier gate blocks T1/T2

### Phase 1 test criteria
- [x] `fleet-setup.php?action=create_tables` succeeds on staging ✓ 2026-04-07 S21
- [x] `fleet-setup.php?action=seed_test` inserts TEST01 fleet + 15 vessels + 60 min data ✓ 2026-04-07 S21
- [x] `test_fleet_e2e.py` — ALL 17 TESTS PASSED ✓ 2026-04-07 S21 (fleet-map: 15 positions, analytics: 3429h, tier gate: 401)
- [x] Pi fleet_push_service.py deployed and `d3kos-fleet-push.service` active ✓ Port 8108 (8107 taken by preferences-api)
- [x] Live push confirmed: Pi position appears in fleet-map.php within 1 min ✓ 2026-04-07 — lat=43.686938, lon=-79.520978, age=1min

### Deployment Instructions (Phase 1)

**Step 1 — Add FLEET_SETUP_KEY to config.php on HostPapa:**
Open HostPapa cPanel File Manager → `staging/mobile/config.php` → add:
```php
define('FLEET_SETUP_KEY', 'choose-a-secret-here');
```

**Step 2 — Deploy PHP files:**
Run on WSL: `python3 deployment/features/fleet-management/scripts/deploy-fleet-php.py`

**Step 3 — Create tables (browser):**
Open: `https://atmyboat.com/staging/mobile/fleet-setup.php?action=create_tables&setup_key=YOUR_KEY`
Expected: `{"success":true,"tables_created":["amboat_fleets","amboat_fleet_members","amboat_fleet_positions","amboat_fleet_engine_snapshots"]}`

**Step 4 — Seed 15-boat test data (browser):**
Open: `https://atmyboat.com/staging/mobile/fleet-setup.php?action=seed_test&setup_key=YOUR_KEY`
Expected: `{"success":true,"members_added":15,"positions_added":900,"engine_added":900,...}`

**Step 5 — Run end-to-end test:**
Run on WSL: `python3 deployment/features/fleet-management/scripts/test_fleet_e2e.py --app-token YOUR_T3_APP_TOKEN`
Expected: ALL 15 TESTS PASSED

---

## Phase 2 — PWA Fleet Screen

### Fleet screen layout
- [ ] Fleet tab in bottom nav (only visible to T3 — locked card for T1/T2)
- [ ] **Fleet Map view**: Leaflet.js, markers for each vessel, tap for vessel name + status
- [ ] **Vessel list view**: per-vessel health card (engine status light, last seen, GPS fix age)
- [ ] Fleet join/create flow: enter fleet_code or create new fleet
- [ ] Privacy toggle per-vessel (500m randomization opt-in)

### Phase 2 test criteria
- [ ] Map loads, markers appear for all fleet members
- [ ] Health cards show correct engine state (green/amber/red based on predictive status)
- [ ] Create fleet → get fleet_code → enter on second device → both appear on map

---

## Phase 3 — Analytics

### Analytics screen
- [ ] Engine hours per vessel (bar chart — Chart.js, same lib already in PWA)
- [ ] Alert history (WATCH + ALERT counts per vessel, last 30 days)
- [ ] Fleet-wide engine health summary (best/worst vessel)
- [ ] CSV export (fleet data download, T3 only)

### Phase 3 test criteria
- [ ] Analytics screen shows correct engine hours from DB
- [ ] Alert counts match predictive_maintenance alert log
- [ ] CSV export downloads correctly

---

## Phase 4 — Tier 3 Gate + Admin View

### Tier gate
- [ ] All fleet endpoints return `{"error": "T3 required"}` for T0/T1/T2
- [ ] PWA fleet tab: T1/T2 see locked upgrade card (CTA → atmyboat.com/upgrade)
- [ ] T3 activation tested with test account on staging

### Admin console fleet view (admin CRM — new tab)
- [ ] Fleet list: all fleets, member count, last activity
- [ ] Per-fleet: member device tokens, position history, alert summary
- [ ] Fleet suspension (disable fleet if account delinquent)

### Phase 4 test criteria
- [ ] T1 account sees locked card, not fleet data
- [ ] T3 account sees full fleet screen
- [ ] Admin can view all fleet records

---

## Design Decisions — LOCKED (2026-04-07 S21)

All four questions resolved by operator before Phase 1 build:

1. **Fleet invitation model:** `fleet_code` (6-char typed in PWA). Simple, works offline, no QR dependency. ✓
2. **Position update frequency:** **1 minute** when engine on OR GPS fix active. Idles otherwise. ✓
3. **Data retention on HostPapa:** Positions = 24h. Engine snapshots = 7 days. Pi keeps full history locally. ✓
4. **Fleet size cap at T3:** **15 vessels** maximum per fleet at launch. Enforced in `fleet-join.php`. ✓

---

## Files This Feature Will Touch

### New (Pi)
- `/opt/d3kos/services/fleet/fleet_push_service.py`
- `/opt/d3kos/config/fleet.json` (written by Pi when fleet joined)
- `/etc/systemd/system/d3kos-fleet-push.service`

### New (HostPapa staging)
- `mobile/fleet-create.php`
- `mobile/fleet-join.php`
- `mobile/fleet-ingest.php`
- `mobile/fleet-map.php`
- `mobile/fleet-analytics.php`

### Modified (PWA)
- `app/screens/fleet.js` (new screen)
- `app/sw.js` (cache v8 — add fleet endpoints)
- `app/manifest.json` (no change expected)

### Modified (Admin CRM)
- `admin-crm/fleet-tab.html` (new tab)
- `admin-crm/app.py` (new fleet routes)

---

## Definition of Done

- [ ] All Phase 1–4 checklist items complete
- [ ] TDD tests pass for Pi service
- [ ] Two test accounts demonstrate fleet map live on staging
- [ ] T3 gate verified (T1 locked, T3 open)
- [ ] Admin fleet view working
- [ ] SESSION_LOG.md updated
- [ ] DEPLOYMENT_INDEX.md updated
- [ ] CHANGELOG.md v0.9.6 entry written
