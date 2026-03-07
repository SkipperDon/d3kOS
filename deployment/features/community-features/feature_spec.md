# Community Features — Pi-Side Spec

## Overview

Community features allow d3kOS devices to contribute anonymised data to the wider boating community on atmyboat.com. All features are **opt-in**, T0-safe (no-ops when cloud-credentials.json is absent), and strip personally identifying information before any data leaves the boat.

Five sub-features, all implemented as Pi-side services/Node-RED flows feeding into the atmyboat.com v0.9.3 backend.

---

## Sub-Feature 1: Anonymous Engine Benchmark Service

**Purpose:** Collect engine performance readings (RPM, coolant temp, fuel burn rate) and push anonymised benchmarks to atmyboat.com. Allows users to compare their engine's health against fleet averages for the same make/model.

**Pi work:**
- New Node-RED flow: `community-engine-benchmark.json`
  - Triggers every 10 minutes when engine RPM > 500 (engine running)
  - Reads: RPM, coolant temp, fuel level delta over interval → calculates burn rate
  - Strips: boat_uuid (replaced with anon_token), GPS position
  - Sends: `POST https://atmyboat.com/api/community/benchmark` with `{anon_token, engine_make, engine_model, rpm, coolant_temp_c, fuel_burn_lph, firmware_version}`
- New settings toggle in settings.html: "Share engine benchmarks" (community section)
- Toggle persisted to `/opt/d3kos/config/community-prefs.json`

**Backend (v0.9.3):** Supabase table `community_benchmarks`. Aggregation view for fleet averages by engine make/model.

---

## Sub-Feature 2: Anonymiser Utility

**Purpose:** Shared utility used by all community sub-features to strip PII before any data leaves the boat.

**Pi work:**
- New file: `/opt/d3kos/services/community/anonymiser.py`
  - `anon_token(boat_uuid)` → SHA-256 HMAC keyed on device_api_key. Same boat always gets same token (for fleet aggregation), but token cannot be reversed to boat_uuid.
  - `strip_position(lat, lon, precision=2)` → rounds to 2 decimal places (~1.1 km grid). Returns `{lat_approx, lon_approx}`.
  - `strip_vessel_name(data)` → removes any field named `name`, `vessel_name`, `mmsi`, `callsign`.
- Imported by all other community services.

---

## Sub-Feature 3: Community Boat Map

**Purpose:** Show a live map on atmyboat.com of active d3kOS boats (opted in), with approximate position. Not a tracking service — positions update at most every 60 minutes, grid-snapped to ~1 km.

**Pi work:**
- New Node-RED flow: `community-boat-map.json`
  - Triggers every 60 minutes
  - Reads GPS position from Signal K
  - Anonymises: anon_token + strip_position (2 decimal places)
  - Sends: `POST https://atmyboat.com/api/community/position` with `{anon_token, lat_approx, lon_approx, firmware_version, timestamp}`
- Settings toggle: "Show my boat on community map (approximate position)"
- If GPS has no fix → skip push silently

**Backend (v0.9.3):** Supabase table `community_positions`. Only most recent position per anon_token stored. Map rendered on atmyboat.com community page.

---

## Sub-Feature 4: Hazard and POI Marker Submission

**Purpose:** Crew can tag hazards (shallow water, debris, hazard buoy off-station) or POIs (good anchorage, fuel dock) directly from the nav page. Markers are shared to the community map.

**Pi work:**
- New button on `helm.html` (nav page): "Report Hazard / POI" — opens a bottom sheet
- Bottom sheet: category dropdown (Hazard / Shallow / Fuel / Anchorage / Marina / Other), optional one-line description (max 80 chars), uses current GPS position snapped to 2dp
- Submits to local API: `POST http://localhost:8095/api/community/marker`
- New Flask service: `community-api.py` port 8095
  - `POST /api/community/marker`: validates category/description, anonymises position, forwards to `POST https://atmyboat.com/api/community/markers`
  - `GET /api/community/markers`: proxies `GET https://atmyboat.com/api/community/markers?bbox=...` for display on nav page
- Settings toggle: "Enable hazard/POI reporting"

**Backend (v0.9.3):** Supabase table `community_markers`. Moderated — new markers appear immediately but can be flagged. Displayed as overlay on community map.

---

## Sub-Feature 5: Knowledge Base Pattern Logger

**Purpose:** When crew uses maintenance log or engine alarms trigger, log the pattern (not the content) to help atmyboat.com build a knowledge base of common issues by engine type, season, and region.

**Pi work:**
- New Node-RED flow: `community-knowledge-log.json`
  - Triggers on maintenance-log writes (watch `/opt/d3kos/data/maintenance-log.json` for changes)
  - Extracts: category, engine_make, engine_model, approximate region (country from GPS 0dp)
  - Strips: all free-text description content, exact position, dates replaced with month/year only
  - Sends: `POST https://atmyboat.com/api/community/knowledge` with `{anon_token, category, engine_make, engine_model, region_country, month_year, firmware_version}`
- Settings toggle: "Help improve the knowledge base (shares issue category only, no details)"

**Backend (v0.9.3):** Supabase table `community_knowledge`. Powers "Common issues for [engine make]" knowledge articles on atmyboat.com.

---

## Settings UI

New section in `settings.html` — "Community & Privacy":

```
[ ] Share engine benchmarks (anonymous fleet comparison)
[ ] Show my boat on community map (approx. 1 km grid)
[ ] Enable hazard/POI reporting from nav page
[ ] Help improve the knowledge base (issue category only)
```

All checkboxes off by default. Persisted to `/opt/d3kos/config/community-prefs.json`.
Settings page reads prefs on load, writes on toggle.

---

## Service Architecture

| Service | Port | Type | Notes |
|---------|------|------|-------|
| community-api.py | 8095 | Flask | Marker submit/fetch proxy |
| community/anonymiser.py | — | Library | Imported by Flask + Node-RED exec nodes |
| community-engine-benchmark.json | — | Node-RED flow | 10-min interval, engine-on only |
| community-boat-map.json | — | Node-RED flow | 60-min interval |
| community-knowledge-log.json | — | Node-RED flow | File-watch triggered |

All services check `community-prefs.json` for their respective opt-in flag before sending any data. All check `cloud-credentials.json` for T1+ status — T0 devices collect nothing.

---

## Privacy Guarantees

1. anon_token is HMAC-keyed — cannot be reversed without device_api_key
2. GPS never transmitted at better than 2dp (~1.1 km)
3. Free text (maintenance notes, vessel name) never transmitted
4. No real-time tracking — position max every 60 minutes
5. All opt-in, all off by default
6. User can delete their community data from atmyboat.com account page (sends `DELETE /api/community/data/{anon_token}` — Pi also supports this via community-api.py)

---

## Dependencies on v0.9.3 Backend

These features are built and deployed in v0.9.2 (Pi side) but will be **inactive** until v0.9.3 backend endpoints exist. The services will catch connection errors silently and retry next interval. This means Pi code can be shipped and tested in isolation before the website is built.
