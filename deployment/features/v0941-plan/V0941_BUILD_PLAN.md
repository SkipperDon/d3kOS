# v0.9.4.1 Build Plan — Community Map + Chart Room
**Written:** 2026-04-08 S35
**Status:** READY TO BUILD (website-side and app-side work can start on staging now)
**Blocked items:** N1–N4 (Node-RED flow wiring) require Phase 4 live push first
**Estimated sessions:** 2–3

---

## What We're Building

The three pieces of the platform were built independently:
- **Pi** — exports engine data, GPS, alerts to HostPapa every 30 minutes
- **HostPapa** — stores the data in MySQL
- **Website + PWA** — has the pages but shows no live data

v0.9.4.1 wires them together. Two visible outcomes:

1. **The Chart Room** (`atmyboat.com/dashboard`) shows live Pi data for logged-in users: engine snapshot, GPS position, alert history, PDF reports list.
2. **The Community Map** (`atmyboat.com/community`) shows anonymised dots for every boat with community sharing enabled — hazard markers, fleet positions, benchmark overlays.

---

## What Already Exists (do not rebuild)

| Item | Location | Status |
|------|----------|--------|
| Pi export_worker.py | `/opt/d3kos/services/export/` | Live — exporting to HostPapa every 30 min |
| data-ingress.php | HostPapa `mobile/` | Live — receiving Pi exports, writing amboat_engine_snapshots, amboat_alerts |
| dashboard-data.php | HostPapa `mobile/` | Live — reads engine + GPS + alerts for a user |
| list-vessels.php | HostPapa `mobile/` | Live — returns paired Pi list |
| community map page | `page-community.php` | Exists — Leaflet map renders but shows no data (no markers endpoint yet) |
| Chart Room page | `/dashboard` WordPress page | Exists — page loads, tier gate works, but shows placeholder content |
| Node-RED flows | Pi | Built but **disabled** — waiting for live URL |

---

## Phase 1 — Chart Room: Display Live Pi Data (staging, no live push needed)

**Files to build:** WordPress theme PHP + JS

### P1-A: dashboard-display.php (or update existing Chart Room page template)

The Chart Room page (`page-dashboard.php` or equivalent) needs to call `dashboard-data.php` and render the results. Currently the page exists but makes no API call.

**What to display:**
```
┌─ Your Boat ──────────────────────────────────────────────────────┐
│  Vessel: [vessel_name]          Last sync: [X minutes ago]        │
│  d3kOS: [version]               Status: ● Online / ◌ Offline     │
├─ Engine (last snapshot) ─────────────────────────────────────────┤
│  RPM: [value]    Coolant: [°C]    Battery: [V]    Fuel: [%]      │
├─ Find My Boat (T1+) ─────────────────────────────────────────────┤
│  [Lat, Lon] as of [timestamp]    [View on Google Maps ↗]         │
├─ Recent Alerts ──────────────────────────────────────────────────┤
│  [last 5 alerts: time | category | severity | message]            │
├─ PDF Reports (T2+) ──────────────────────────────────────────────┤
│  [list: date | filename | download link]                           │
└──────────────────────────────────────────────────────────────────┘
```

**Source data:**
- `dashboard-data.php` → engine snapshot + GPS + alert list + last_sync
- `list-reports.php` → PDF report list (T2+ only)

**Tier gates:**
- Find My Boat: T1+ only (T0 sees locked card with upgrade CTA)
- PDF Reports: T2+ only
- Engine snapshot: all tiers

**Implementation:** PHP + vanilla JS (same pattern as existing community page). No React, no framework.

### P1-B: Multi-boat support (T3)

When user has >1 paired Pi, Chart Room shows a boat selector tabs at the top. Clicking a tab switches all panels to that Pi's data. Uses `list-vessels.php` to enumerate, `dashboard-data.php?pi_id=<device_token>` to fetch per-Pi data.

**`dashboard-data.php` already accepts `pi_id` param** — just needs to be wired into the page.

### P1-C: PDF report list on Chart Room

`list-reports.php` exists and returns last 20 reports. Chart Room shows them as a download list. T2+ gate. Simple table: date | vessel | download link.

---

## Phase 2 — Community Map: Backend Endpoints (staging)

The community map page (`/community`) already has Leaflet loaded and is ready to display markers. It just needs the PHP endpoints that serve the data.

### P2-A: community-markers.php (NEW)

```
POST /mobile/community-markers.php
  Auth: Bearer app_token or device_token
  Body: { device_token, lat, lon, marker_type, description, severity }
  → Stores in amboat_community_markers
  → Returns { success, marker_id }

GET /mobile/community-markers.php?bbox=lat1,lon1,lat2,lon2
  Auth: Bearer app_token (PWA) or none (public read)
  → Returns markers within bbox
  → Coordinates rounded to 2 decimal places on output (500m privacy blur)
  → Returns { success, markers: [...] }
```

**MySQL table (auto-created on first call):**
```sql
CREATE TABLE IF NOT EXISTS amboat_community_markers (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    device_token VARCHAR(36)  NOT NULL,
    lat          DECIMAL(9,6) NOT NULL,
    lon          DECIMAL(9,6) NOT NULL,
    marker_type  ENUM('hazard','anchorage','fuel','interesting') DEFAULT 'hazard',
    description  VARCHAR(200),
    severity     ENUM('low','medium','high') DEFAULT 'low',
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at   DATETIME,          -- NULL = permanent
    INDEX idx_loc (lat, lon)
)
```

**Privacy rule:** GET output always rounds lat/lon to 2 decimal places (~1.1km precision). Store full precision, serve blurred.

### P2-B: community-position.php (NEW)

```
POST /mobile/community-position.php
  Auth: Bearer AMBOAT_API_KEY + X-Device-Token (Pi-facing)
  Body: { device_token, lat, lon, heading, speed }
  → UPSERT into amboat_community_positions (one row per device_token)
  → Returns { success }

GET /mobile/community-positions.php
  Auth: Bearer app_token (PWA)
  → Returns all active positions (last_seen < 30 min)
  → Coordinates 2 decimal place privacy blur
  → Returns { success, positions: [...] }
```

**MySQL table:**
```sql
CREATE TABLE IF NOT EXISTS amboat_community_positions (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    device_token VARCHAR(36)  NOT NULL UNIQUE,
    lat          DECIMAL(9,6),
    lon          DECIMAL(9,6),
    heading      SMALLINT,
    speed        DECIMAL(5,2),
    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_updated (updated_at)
)
```

### P2-C: Wire community map page

`page-community.php` already has Leaflet. Add JS to:
1. On load: `GET community-positions.php` → plot boat dots (blurred, no identity)
2. On load: `GET community-markers.php?bbox=<viewport>` → plot hazard/anchorage/fuel markers
3. Auto-refresh every 5 minutes
4. If user is logged in (T1+): show "Add Marker" button → POST to community-markers.php

**Marker icons:**
- Hazard: ⚠ red
- Anchorage: ⚓ blue
- Fuel: ⛽ green
- Interesting: ★ amber

---

## Phase 3 — Node-RED Flow Activation (BLOCKED on Phase 4 live push)

These steps happen the day of or after the Phase 4 live push. Don performs these, not Claude.

| # | Step | Detail |
|---|------|--------|
| N1 | Update Node-RED flow URL | In Node-RED editor: open "Post to Community DB" nodes → change URL from placeholder to `https://atmyboat.com/mobile/community-position.php` |
| N2 | Wire API key | Open `/opt/d3kos/config/cloud-credentials.json` → set `community_api_key` → Node-RED reads it |
| N3 | Enable 3 flows | In Node-RED editor: telemetry/push, community/benchmark, community/position → Enable → Deploy |
| N4 | End-to-end test | Toggle community sharing ON in Pi dashboard Settings → wait 30 min → check community map shows boat dot |

---

## Phase 4 — Integration Tests

| # | Test | Pass criteria |
|---|------|---------------|
| T1 | Chart Room load | Logged-in T1 user → /dashboard → engine snapshot shows RPM/coolant/battery from last Pi export |
| T2 | Find My Boat | Chart Room → GPS coordinates displayed, Google Maps link opens correct location |
| T3 | Alert history | Chart Room → last 5 alerts listed with time, category, severity |
| T4 | PDF report list | T2 user → Chart Room → last 3 PDF reports shown with download links |
| T5 | T0 locked state | T0 user → Chart Room → Find My Boat and PDF sections show locked cards with upgrade CTA |
| T6 | Community map loads | /community → Leaflet map renders, no JS errors |
| T7 | Community markers | POST marker → GET bbox → marker appears at blurred coordinates |
| T8 | Position privacy | GET positions → lat/lon rounded to 2 decimal places in response |
| T9 | Stale position filter | Position updated >30 min ago → does not appear on community map |

---

## Build Order

```
Session 1 (staging — no live push needed):
  ├── Phase 1A: Chart Room display (dashboard page template + JS)
  ├── Phase 1B: Multi-boat tab selector
  ├── Phase 1C: PDF report list
  └── Phase 2A+2B: community-markers.php + community-position.php

Session 2 (staging):
  ├── Phase 2C: Wire community map page JS (Leaflet markers + auto-refresh)
  └── Phase 4: T1–T9 integration tests on staging

Post-Phase-4 live push (Don's action):
  └── Phase 3: Node-RED flow activation (N1–N4)
```

---

## Key Constraints

- **No new libraries** — Leaflet is already loaded on community page. No React, no npm.
- **Tier gates** — T0 gets locked cards, not errors. Upgrade CTA links to `atmyboat.com/upgrade`.
- **Privacy blur is non-negotiable** — community positions and markers always output 2 decimal place precision regardless of stored precision.
- **Pi-facing endpoints** use `AMBOAT_API_KEY` + `X-Device-Token`. PWA-facing use `app_token`. Never mix.
- **Auto-create tables** — all new PHP files create their tables with `CREATE TABLE IF NOT EXISTS` on first call. No phpMyAdmin step required.
- **app.js service worker** — after any change to app.js, bump the SW cache version constant.
- **deploy pattern** — PHP to HostPapa via Python ftplib. Pi files via SCP + SSH. App.js via SCP to Pi `/var/www/html/app.js`.

---

## Files to Create

| File | Location | Purpose |
|------|----------|---------|
| `community-markers.php` | HostPapa `mobile/` | POST store + GET bbox query |
| `community-position.php` | HostPapa `mobile/` | POST UPSERT boat position (Pi-facing) |
| `community-positions.php` | HostPapa `mobile/` | GET active positions (PWA-facing) |
| `page-dashboard.php` update | WordPress theme | Chart Room live data display |
| `page-community.php` update | WordPress theme | Wire Leaflet to endpoints |
| `app.js` update (optional) | Pi `/var/www/html/` | Community sharing toggle in PWA if not already present |

---

*Plan written S35 2026-04-08. Ready to execute next session.*
