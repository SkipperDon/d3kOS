# v0.9.4 — S1 Session Plan
**Version:** 1.0.0
**Date:** 2026-03-26
**Status:** DRAFT — awaiting operator approval before any code is written

---

## GOAL
Pi can push all required data categories to AtMyBoat.com staging.
Command Consumer Agent is running and can receive + execute commands from the queue.

---

## PREREQUISITES (confirmed before this plan was written)
- ✅ Tailscale: removed from Pi (binary not found, service not found)
- ✅ Signal K v2.23.0: running on Pi at :8099
- ✅ SSH access: working (d3kos@192.168.1.237)
- ✅ export-manager: running at :8094, 9 categories, 5 implemented
- ✅ Self-healing DB: `/opt/d3kos/data/self-healing/issues.db` — 2,595 records
- ✅ Version file: `/opt/d3kos/config/version.txt`
- ⚠️ CENTRAL_API_URL in export-manager.py: placeholder — must be fixed in this session

---

## WHAT IS NOT CHANGING THIS SESSION
- No changes to Signal K configuration
- No changes to existing export categories (boatlog, marine_vision_captures, settings, onboarding, telemetry)
- No changes to AtMyBoat.com PHP endpoints (already built in v0.9.3)
- No changes to Pi systemd services beyond adding the new cloud agent service
- No changes to AvNav, Node-RED, or any other Pi service

---

## TASK 1 — Fix CENTRAL_API_URL in export-manager.py

**File:** `/opt/d3kos/services/export/export-manager.py`

**Change:** Replace the placeholder URL with the real AtMyBoat.com staging endpoint.

```
BEFORE: CENTRAL_API_URL = "https://d3kos-cloud-api.example.com"
AFTER:  CENTRAL_API_URL = "https://atmyboat.com/staging/wp-content/themes/twentytwenty-child/mobile/data-ingress.php"
```

**Why:** The Pi has never actually pushed exports to AtMyBoat.com. Without this fix, every other S1 task is unreachable.

**Test:** After fix, trigger a manual export and confirm AtMyBoat.com staging receives it (HTTP 200).

---

## TASK 2 — Add 5 missing export categories to export_categories.py

**File:** `/opt/d3kos/services/export/export_categories.py`

Add these 5 new `collect_*` methods to the `ExportCategories` class and call them from `collect_all()`.

### 2a — GPS / Navigation
**Source:** Signal K `http://localhost:8099/signalk/v1/api/vessels/self/navigation`

Collects:
- `latitude`, `longitude` from `navigation.position.value`
- `speed_over_ground_knots` — converts from m/s (SK value × 1.944)
- `course_over_ground_deg` — converts from radians (SK value × 57.2958)
- `signal_k_timestamp` — the SK source timestamp
- `has_fix` — boolean: true if lat ≠ 0 or lng ≠ 0

Returns `null` for any field SK does not provide. Never errors out — returns empty structure on failure.

### 2b — Engine
**Source:** Signal K `http://localhost:8099/signalk/v1/api/vessels/self/propulsion/port`

**Important:** Key is `propulsion.port` — NOT `propulsion.0`. Confirmed on this Pi.

Collects:
- `rpm` — `revolutions` value × 60 (SK gives Hz)
- `boost_pressure_kpa` — `boostPressure` value ÷ 1000 (SK gives Pa)
- `oil_pressure_kpa` — `oilPressure` value ÷ 1000 (if present)
- `coolant_temp_c` — `temperature` value − 273.15 (SK gives Kelvin, if present)
- `fuel_level_pct` — from `tanks.fuel.0.currentLevel` × 100 (if present)
- `engine_hours` — `runTime` value ÷ 3600 (SK gives seconds, if present)
- `engine_on` — boolean: true if rpm > 0

**All fields optional.** Engine is off at the dock — oil/coolant/fuel will be null. That is correct behaviour. The mobile app displays "last known" for null fields.

### 2c — System Health
**Source:** `systemctl is-active` for each d3kOS service + existing telemetry data

Services to check (exact service names from Pi):
```
d3kos-dashboard
d3kos-gemini
d3kos-ai-bridge
d3kos-export-manager
d3kos-camera
d3kos-fish-detector
d3kos-keyboard-api
d3kos-ai-api
d3kos-cloud-agent     ← added in Task 3 this session
signalk
avnav
```

Returns per service: `{ "name": "d3kos-dashboard", "status": "active" | "inactive" | "failed" | "unknown" }`

Also includes from existing telemetry:
- `uptime_seconds`
- `memory_used_percent`
- `disk_used_percent`
- `cpu_temp_c` — reads from `/sys/class/thermal/thermal_zone0/temp` ÷ 1000

### 2d — System Alerts
**Source:** `/opt/d3kos/data/self-healing/issues.db` — `issues` table

Collects last 50 records ordered by `timestamp DESC`.

Returns per record:
```json
{
  "id": 1,
  "timestamp": "2026-02-20T13:12:47",
  "category": "service_down",
  "severity": "critical",
  "description": "Service d3kos-license-api is not running",
  "status": "resolved",
  "resolved_at": "2026-02-20T13:13:36",
  "remediation_action": "Restarted service d3kos-license-api"
}
```

Also returns summary counts: `total`, `critical_unresolved`, `warning_unresolved`.

### 2e — Version
**Source:** `/opt/d3kos/config/version.txt`

Collects:
- `version` — e.g. "0.9.2.2"
- `release_date` — e.g. "March 23, 2026"
- `status` — e.g. "Release Candidate"
- `raw` — full file content

---

## TASK 3 — Build Command Consumer Agent

**New file:** `/opt/d3kos/services/cloud-agent/cloud_agent.py`
**New service:** `d3kos-cloud-agent.service`

### What it does
Polls `command-queue.php` on AtMyBoat.com every 30 seconds. Picks up pending commands. Executes them. Writes result back.

### Poll endpoint
```
GET https://atmyboat.com/staging/.../mobile/command-queue.php
Headers: Authorization: Bearer <API_KEY>, X-Device-Token: <device_token>
```

### Commands to handle in S1 (minimal viable set)
| Command | What it does |
|---------|-------------|
| `ping` | Responds with current version + timestamp. Used to confirm agent is alive. |
| `export_now` | Triggers immediate export via export-manager (POST to :8094). |
| `tier_change` | Reads new tier from payload, updates license.json. |

Commands deferred to S4 (Fix My Pi) and S3 (OTA):
- `fix_my_pi` — deferred to S4
- `ota_upgrade` — deferred to S3

### Agent behaviour
- Reads `installation_id` from `/opt/d3kos/config/license.json`
- Reads `device_token` from `/opt/d3kos/config/device-token.json` (create if not exists — generate UUID once, persist)
- On pickup: ACKs command (marks `in_progress`)
- On completion: writes result JSON back to queue
- On failure: writes error to queue, does NOT retry automatically
- Logs to `/opt/d3kos/logs/cloud-agent.log` (rotating, max 5MB)
- Never crashes the Pi — all exceptions caught, logged, agent continues

### Systemd service
```
[Unit]
Description=d3kOS Cloud Command Agent
After=network.target d3kos-export-manager.service

[Service]
Type=simple
User=d3kos
WorkingDirectory=/opt/d3kos/services/cloud-agent
ExecStart=/usr/bin/python3 cloud_agent.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## TASK 4 — End-to-End Test

Before closing S1, run this test sequence:

1. **Export test:** Trigger `export_now` command via AtMyBoat.com staging phpMyAdmin (insert row directly into `amboat_command_queue`). Confirm:
   - Cloud agent picks it up within 30s
   - Export runs
   - AtMyBoat.com staging receives the export at data-ingress.php (check DB for new row)
   - All 5 new categories appear in the payload with real data

2. **Ping test:** Insert `ping` command. Confirm agent responds with version "0.9.2.2" and current timestamp.

3. **System health check:** Confirm `system_health` category lists all services with correct `active`/`inactive` states.

---

## FILES CHANGED THIS SESSION

| File | Location | Change |
|------|----------|--------|
| `export-manager.py` | Pi `/opt/d3kos/services/export/` | Fix CENTRAL_API_URL |
| `export_categories.py` | Pi `/opt/d3kos/services/export/` | Add 5 new collect methods |
| `cloud_agent.py` | Pi `/opt/d3kos/services/cloud-agent/` | New file |
| `d3kos-cloud-agent.service` | Pi `/etc/systemd/system/` | New systemd service |

All changes also written to local repo at `/home/boatiq/Helm-OS/deployment/v0.9.4/pi_source/` before deploying to Pi.

---

## OUT OF SCOPE THIS SESSION
- PWA / GitHub Pages — S2
- OTA upgrade command — S3
- Fix My Pi diagnostic script — S4
- WebRTC/STUN — S6
- Any AtMyBoat.com PHP changes
- Any changes to live atmyboat.com

---

## OPEN QUESTION BEFORE STARTING

**device-token.json:** Does `/opt/d3kos/config/device-token.json` already exist on the Pi, or does the cloud agent need to create it on first run? I will check at S1 start — no assumption made here.

---

*v0.9.4 S1 Session Plan v1.0.0 — 2026-03-26 — Awaiting operator approval*
