# d3kOS Settings & Configuration Reference

**Version:** v0.9.9.5  
**Source:** `services/dashboard/templates/settings.html`, `setup.html`, `app.py`  
**Last updated:** 2026-11-25

---

## Overview

d3kOS has two configuration entry points:

| Entry Point | URL | Purpose |
|---|---|---|
| **Setup Wizard** | `localhost:3000/setup` | First-run personalisation — 8 steps, ~5 min |
| **Settings Page** | `localhost:3000/settings` | Ongoing configuration — 17 sections |

Configuration is persisted in two env files on the Pi (never committed to git):

| File | Path | Contents |
|---|---|---|
| `vessel.env` | `/opt/d3kos/config/vessel.env` | Owner/vessel data, language, engine specs, electronics |
| `api-keys.env` | `/opt/d3kos/config/api-keys.env` | Gemini API key (sensitive — gitignored) |

Runtime config (Telegram bot, alert preferences, camera slots) lives in `/opt/d3kos/config/`.

---

## Part 1 — Setup Wizard (`/setup`)

Runs once on first boot. Can be re-run from Settings (Tier 0 limit: 3 runs; Tier 1+ unlimited). All steps except vessel name are optional — every field can be skipped and updated later in Settings.

### Pre-Step — Password Change

Triggered automatically if the factory default password has not been changed.

| Field | Type | Constraint |
|---|---|---|
| New Password | Password input | Minimum 8 characters; cannot reuse the factory default |
| Confirm Password | Password input | Must match |

**Action:** Calls `POST /network/change-password`. Writes flag to `/opt/d3kos/data/onboarding.json`. Must complete before wizard proceeds.

---

### Step 1 — Welcome

No configuration fields. Displays feature overview. Option to **Recover Existing Pi** by entering a 36-character UUID Recovery Key from a previous install.

**Recovery:** `POST` to AtMyBoat.com cloud with device UUID → pulls paired account config back to this Pi.

---

### Step 2 — Vessel Identity

| Field | Type | Values / Notes |
|---|---|---|
| Vessel Name | Text | **Required.** Shown in status bar; injected into all AI prompts |
| Home Port | Text | Optional. e.g. `Kingston, ON` |
| Dashboard Language | Select | 18 languages (BCP 47 tags). Sets HELM voice recognition language. Default: `en-GB` |
| Manufacturer | Text | Optional boat particulars |
| Year | Number | 1950–2026 |
| Model | Text | e.g. `2600, 3260 XO` |
| Length (ft) | Number | 6–200 ft, 0.5 step |
| Boat Type | Select | Power Single / Twin, Sail, Catamaran Power/Sail, RIB, Other |
| Region Sold | Select | North America / Europe / Australia-NZ / Other |

**Persisted to:** `vessel.env` keys `VESSEL_NAME`, `HOME_PORT`, `UI_LANG`, `BOAT_MAKE`, `BOAT_YEAR`, `BOAT_MODEL`, `BOAT_TYPE`, `BOAT_LOA`, `BOAT_REGION`.

---

### Step 3 — Engine & Drive

Calibrates engine monitor baselines and powers the NMEA DIP switch calculator (Step 5).

**Engine 1 (Primary / Single)**

| Field | Type | Values |
|---|---|---|
| Make | Select | Mercury Marine, MerCruiser, Yamaha, Volvo Penta, Yanmar, Cummins, Detroit Diesel, Cat, John Deere, Perkins, Suzuki, Honda, Tohatsu, Evinrude/BRP, OMC/Johnson, Crusader, Indmar, PCM, Ilmor, Other |
| Year | Number | 1950–2026 |
| Model / Spec | Text | e.g. `5.0L MPI Alpha` — used for manual search |
| Horsepower | Number | 1–3000 HP |
| Cylinders | Select | 1 / 2 / 3 / 4 / 6 / 8 / 12 |
| Fuel Type | Select | Gasoline (4-stroke) / Diesel (4-stroke) / Outboard (4-stroke) / Outboard (2-stroke) |
| Induction | Select | Naturally Aspirated / Turbocharged / Supercharged |
| Idle RPM | Number | 200–1500 RPM |
| Max RPM (WOT) | Text | e.g. `4800–5200` |
| Twin Engines | Toggle | Enables Engine 2 block below |

**Engine 2 (Starboard — twin only)**

| Field | Type |
|---|---|
| Make | Select (same list as Engine 1) |
| Year | Number |
| Model / Spec | Text |

**Persisted to:** `vessel.env` keys `ENGINE_MAKE`, `ENGINE_MODEL`, `ENGINE_YEAR`, `ENGINE_HP`, `ENGINE_CYLINDERS`, `ENGINE_FUEL`, `ENGINE_INDUCTION`, `ENGINE_IDLE_RPM`, `ENGINE_MAX_RPM`, `ENGINE_COUNT`, `ENGINE2_MAKE`, `ENGINE2_MODEL`, `ENGINE2_YEAR`.

---

### Step 4 — Electronics & NMEA

| Field | Type | Values |
|---|---|---|
| Chart Plotter / MFD | Text | e.g. `Garmin GPSMap 1242xsv` |
| VHF Radio | Text | e.g. `Standard Horizon GX2400` |
| Gateway Model | Select | None / Matsutec CX5106 / Actisense EMU-1 / Yacht Devices YDAB-01 / Garmin NMEA 2000 / Other |
| Fuel/Level Sender Standard | Select (CX5106 only) | North America 240–33 Ω (high→low) / Europe 0–190 Ω (low→high) |

**Persisted to:** `vessel.env` keys `NMEA_GATEWAY`, `CHARTPLOTTER`, `VHF_RADIO`.

---

### Step 5 — Gateway Configuration (DIP Switches)

Computed display only — no user input fields. Generates the complete DIP switch diagram for the selected gateway model from Step 4 data (engine make, fuel type, region, twin/single). CX5106 shows two blocks (A = engine configuration 7 switches, B = fuel/level sender settings).

---

### Step 6 — Mobile Pairing

Optional. Connects this Pi to AtMyBoat.com (free Tier 1 account).

| Element | Description |
|---|---|
| QR Code | Scan with phone camera → opens `atmyboat.com/register?token=<UUID>` |
| Registration Code | 6-digit code, manual entry at `atmyboat.com/register` |
| Device UUID | 36-char UUID displayed for support reference |
| States | Loading → code available → pending approval → offline → error |

**What registration enables:** Mobile app access, cameras, voice assistant, anchor alerts, cloud sync, data export (Tier 1 features). **Pi works fully without an account — registration is optional.**

---

### Step 7 — Gemini API Key

| Field | Type | Notes |
|---|---|---|
| Gemini API Key | Password input | Starts with `AIzaSy…`. Get from `aistudio.google.com` → Get API Key |

**Persisted to:** `api-keys.env` as `GEMINI_API_KEY`. Gitignored — never committed. Reload applied live without Flask restart.

---

### Step 8 — Done

Summary screen. Option to open Camera Setup in a new tab (`/settings#s-camera`). Submit finalises all wizard data and redirects to dashboard.

---

## Part 2 — Settings Page (`/settings`)

17 sections. Navigate via the sidebar or scroll. All changes are live unless noted.

---

### Section 1 — System Status

**Purpose:** Live health check of all d3kOS services.

| Indicator | Service | Address |
|---|---|---|
| AvNav Charts | Chart plotter | `localhost:8080` |
| Signal K | Instrument data hub | `localhost:8099` |
| GPS | NMEA position feed | Via Signal K |
| AIS | AIS targets | Via Signal K / UDP 10110 |
| Gemini AI | Cloud AI proxy | `localhost:3001` |
| Ollama | LAN AI fallback | `192.168.1.36:11434` |
| Internet | Cloud connectivity | External ping |

**Buttons:**

| Button | Action |
|---|---|
| Refresh | Re-polls all 7 indicators (also auto-polls every 30 s) |
| Test Signal K | Verifies WebSocket connection at `ws://localhost:8099/signalk/v1/stream` |

---

### Section 2 — Engine Monitoring

**Purpose:** Configure engine service intervals and hour tracking for the Engine Ribbon.

| Field | Type | Range | Default |
|---|---|---|---|
| Service interval | Select | 10, 25, 50, 100, 150, 200, 500 h | 100 h |
| Oil change interval | Select | 10, 25, 50, 100, 150, 200 h | 50 h |
| Total engine hours | Number input | 0–99,999 h | 0 |
| Hours since last service | Number input | 0–9,999 h | 0 |

**Buttons:**

| Button | Action |
|---|---|
| Save Engine Settings | Persists intervals and hour values |
| Reset Service Counter | Zeros "hours since last service" (for use after servicing) |

**Affects:** Engine Ribbon (RPM/Trim/Oil/Coolant/Fuel), service-due badge on dashboard.

---

### Section 3 — Units & Display

**Purpose:** Set measurement units for all instrument readouts.

| Setting | Options | Notes |
|---|---|---|
| Distance | Nautical Miles (nm) / Kilometres (km) / Miles (mi) | Affects speed-distance calculations |
| Speed | Knots (kts) / km/h / mph | Affects SOG, STW displays |
| Temperature | Celsius (°C) / Fahrenheit (°F) | Affects engine coolant, air temp |
| Pressure | kPa / PSI / Bar | Affects oil pressure display |
| Metric / Imperial master | Toggle | Convenience switch — sets all four above at once |

**Save button:** Persists to user preferences. Applied immediately on save.

---

### Section 4 — Alerts & Notifications

**Purpose:** Enable or disable each alert category. Per-type toggle switches.

| Alert Type | Toggle | On by default |
|---|---|---|
| Anchor drag | On/Off | Yes |
| Engine overtemp | On/Off | Yes |
| Engine oil pressure | On/Off | Yes |
| Low fuel | On/Off | Yes |
| GPS lost | On/Off | Yes |
| Collision risk (SafeHelm) | On/Off | Yes |
| (additional types per alert_watcher.py) | On/Off | Yes |

**Save button:** Persists all toggles. Changes take effect on next alert_watcher.py poll (30-second cycle).

> See `D3KOS_ALERTS_NOTIFICATIONS.md` for full delivery channels, timing, and voice priority for each alert type.

---

### Section 5 — HELM AI Assistant

**Purpose:** Configure the AI First Officer — vessel identity injected into prompts, cloud and offline AI endpoints.

| Field | Type | Notes |
|---|---|---|
| Vessel Name | Text | Pre-filled from setup. Injected into every AI query and voice prompt |
| Home Port | Text | Pre-filled from setup. Used in port arrival and voyage briefings |
| Gemini API Key | Password (show/hide toggle) | Google Gemini key — stored in `api-keys.env`, never logged |
| Gemini Model | Select | `gemini-2.5-flash` (recommended) / `gemini-2.0-flash` / `gemini-2.5-pro` |
| Ollama Address | Text | Default: `127.0.0.1:11434`. Change to LAN address (e.g. `192.168.1.36:11434`) for a network Ollama server |
| Ollama Model | Text | Default: `phi3.5:latest`. Any model pulled on the Ollama server |
| System Prompt Preview | Read-only | Shows the marine context prompt prepended to every Gemini and Ollama query |

**Privacy toggles:**

| Toggle | Behaviour |
|---|---|
| Token count logging | Logs token usage only — no query text ever stored |
| Query text storage | Always OFF and cannot be enabled — query text is never persisted |

**How AI routing works:**

1. Query arrives at Gemini proxy (`localhost:3001`)
2. If Gemini API key is set and internet is reachable → routes to Gemini cloud
3. If offline or key missing → falls back to Ollama at configured address/model
4. If Ollama also unreachable → returns cached response (max 10 entries, no query text)

---

### Section 6 — Camera Setup

**Purpose:** Configure IP cameras for the Marine Vision page.

| Element | Description |
|---|---|
| Scan button | Discovers cameras on the LAN |
| RTSP URL field | Manual entry for cameras not auto-discovered. Format: `rtsp://user:pass@IP:554/stream` |
| Slot assignment wizard | Maps each camera stream to a slot (bow, stern, port, starboard, interior) in go2rtc |

**How it works:** Camera streams are served via go2rtc at `localhost:8084`. go2rtc requires at least one camera URL in `cameras-config.json` before its service starts.

**Common RTSP formats:**

| Brand | URL pattern |
|---|---|
| Hikvision | `rtsp://admin:admin@[IP]:554/Streaming/Channels/101` |
| Dahua | `rtsp://admin:admin@[IP]:554/cam/realmonitor?channel=1&subtype=0` |
| Reolink | `rtsp://admin:[pass]@[IP]:554/h264Preview_01_main` |
| Generic | `rtsp://admin:password@192.168.1.x:554/stream` |

---

### Section 7 — Data Management

**Purpose:** Import, export, and clear boat log and trip data.

| Button | Action | Notes |
|---|---|---|
| Export All Data | Downloads complete boat log and issues database as ZIP | Calls `POST /api/boatlog/export` |
| Import Data | Uploads a previously exported ZIP to restore boat log | File picker |
| Clear Trip Data | Erases all trip records from local database | Irreversible |
| Clear Benchmarks | Erases engine benchmark history | Irreversible |

---

### Section 8 — Network & Connectivity

**Purpose:** Service port map and cloud panel toggles.

**Port Map (read-only display):**

| Service | Address | Status |
|---|---|---|
| d3kOS Dashboard | `localhost:3000` | Always UP (you are connected) |
| AvNav Charts | `localhost:8080` | Live status indicator |
| Gemini AI Proxy | `localhost:3001` | Live status indicator |
| Signal K | `localhost:8099` | Live status indicator |
| Signal K WebSocket | `ws://localhost:8099/signalk/v1/stream` | Live status indicator |
| OpenPlotter | `localhost:8081` | Shown as INFRA (always present) |
| Ollama (LAN) | `192.168.1.36:11434` | Live status indicator |

**Cloud Panel Toggles:**

| Toggle | Service | Requires |
|---|---|---|
| Windy weather panel | Windy embed (`embed.windy.com`) | Internet |
| Radar panel (RainViewer) | RainViewer radar overlay | Internet |

**Network settings button:** Opens OpenPlotter at `localhost:8081 → Network` for WiFi, hotspot, and LAN configuration.

---

### Section 9 — Chart Setup & Documentation

**Purpose:** Links to built-in documentation for chart installation and AvNav usage.

| Doc Button | Opens |
|---|---|
| o-charts Installation | Step-by-step: install o-charts into AvNav, activate license, download Canada CHS / UK / US charts |
| AvNav Plugins Guide | AIS overlay, anchor alarm, NMEA display (Signal K), voyage log, ochartsng plugin setup |
| Free Chart Sources | NOAA ENC (USA/Great Lakes), LINZ (NZ/Pacific), RIS (Europe inland), Marinha (Brazil) — all load in AvNav |
| How to Use AvNav | Waypoints, route planning, anchor alarm, AIS overlay, voyage GPX export — opens `localhost:8080` |

---

### Section 10 — OpenPlotter & System Infrastructure

**Purpose:** Links to OpenPlotter reference documentation.

| Doc Button | Topic |
|---|---|
| OpenPlotter Reference | What OpenPlotter manages (GPS, AIS, NMEA, Signal K). Access at `localhost:8081`. Why it runs in background |
| OpenPlotter Plugins | NMEA 0183, Signal K, AIS, pypilot — enable, configure, troubleshoot. Signal K WS: `ws://localhost:8099` |

---

### Section 11 — Getting Started

**Purpose:** Daily-use quick reference and emergency procedures. Read-only guide.

**Daily Use (5 steps):**

1. Pi boots → dashboard auto-launches at `localhost:3000`
2. Charts → Main Menu → AvNav Charts → live GPS at `localhost:8080`
3. Weather → Dashboard → Sea State → Windy / RainViewer panels
4. AI Nav → Main Menu → AI Navigation → marine queries at `localhost:3001`
5. Offline → AvNav + GPS work without internet; AI falls back to Ollama at `192.168.1.36:11434`

**Emergency Procedures:**

| Situation | Action |
|---|---|
| Dashboard down | Settings → System Actions → Restart Dashboard |
| No GPS in AvNav | Check Signal K at `localhost:8099` → Data Browser |
| AI Proxy down | Settings → System Actions → Restart Gemini Proxy |
| AI not responding | Check Ollama at `192.168.1.36:11434` on LAN |

---

### Section 12 — Phase Roadmap

**Purpose:** Read-only history of d3kOS build phases. Current phase marked ACTIVE.

| Phase | Status | Description |
|---|---|---|
| Phase 0 | Done | Directories, .gitignore, governance stubs (2026-03-12) |
| Phase 1 | Done | Pi menu restructure, AvNav + Gemini desktop entries, port migration SK :3000→:8099 (2026-03-13) |
| Phase 2 | Done | Dashboard hub Flask :3000, 9-button menu, AvNav iframe, Windy/Radar panel, 5 status indicators (2026-03-13) |
| Phase 3 | Done | Gemini AI proxy :3001 — Gemini online / Ollama offline fallback, response cache (2026-03-13) |
| Phase 4 | Active | Settings page (16 sections), Signal K WebSocket, AvNav documentation |
| Phase 5 | Planned | AI + AvNav integration — route suggestion, voyage log GPX, port arrival briefings, AI Bridge :3002 |

---

### Section 13 — System Actions

**Purpose:** Restart services and reboot the Pi.

| Button | Action | Notes |
|---|---|---|
| Restart Signal K | `POST /action/restart` body `{service:"signalk"}` | Requires sudo in `/etc/sudoers.d/d3kos` |
| Restart Node-RED | `POST /action/restart` body `{service:"nodered"}` | Requires sudo |
| Reboot System | `POST /action/reboot` with confirmation dialog | Full Pi reboot |
| Initial Setup Reset | Disabled in UI | Requires triple confirmation — contact support |
| Restart Dashboard | `POST /action/restart` body `{service:"dashboard"}` | Restarts Flask at :3000 |
| Restart Gemini Proxy | `POST /action/restart` body `{service:"gemini"}` | Restarts proxy at :3001 |

---

### Section 14 — System Information

**Purpose:** Live Pi hardware and software status. Read-only.

| Field | Source |
|---|---|
| System | d3kOS version string |
| Hardware | Raspberry Pi model (4B 8GB RAM default) |
| OS | Debian GNU/Linux 13 (Trixie) 64-bit |
| Signal K | Live version via `GET /signalk/v1/api/self` |
| IP Address | Live from `GET /sysinfo` |
| Disk Usage | Live from `GET /sysinfo` |
| Memory | Live from `GET /sysinfo` |
| CPU Temp | Live from `GET /sysinfo` |
| Uptime | Live from `GET /sysinfo` |

**Refresh button:** Calls `GET /sysinfo` and updates all fields.

---

### Section 15 — License & Tier

**Purpose:** Displays current tier and device recovery key.

| Field | Description |
|---|---|
| Tier | Current tier level (T0–T3) with feature summary |
| Install ID | Human-readable install identifier |
| Features | Checkmarks for Voice, Camera, AI Nav (tier-gated) |
| Recovery Key | Device UUID — write on a label and stick to the Pi. Enter in wizard Step 1 to restore after reflash |

The recovery key is the `device_token` from `api-keys.json`. It must be preserved on reflash to restore cloud pairing. Copy button available for convenience.

---

### Section 16 — Security

**Purpose:** Change the d3kOS system password post-setup.

| Field | Type | Constraint |
|---|---|---|
| New Password | Password input | Minimum 8 characters |
| Confirm Password | Password input | Must match |

**Change Password button:** Calls `POST /network/change-password`. Writes flag to `onboarding.json`. Use after first boot or for periodic rotation.

> A factory default password ships with every Pi image. Changing it is enforced before the setup wizard proceeds.

---

### Section 17 — About d3kOS

**Purpose:** System description and service address summary. Read-only.

Shows build description, service addresses, and version attribution.

---

## Part 3 — Configuration Files Reference

Files that live on the Pi at runtime (never in git):

| File | Path | Format | Contents |
|---|---|---|---|
| `vessel.env` | `/opt/d3kos/config/vessel.env` | KEY=value | Vessel name, home port, language, boat particulars, engine specs, electronics |
| `api-keys.env` | `/opt/d3kos/config/api-keys.env` | KEY=value | `GEMINI_API_KEY` only |
| `api-keys.json` | `/opt/d3kos/config/api-keys.json` | JSON | `device_token` (UUID), `amboat_api_key` — heartbeat auth. Must be preserved on reflash |
| `telegram-config.json` | `/opt/d3kos/config/telegram-config.json` | JSON | `enabled`, `bot_token`, `chat_id`, `retry_attempts`, `retry_delay` |
| `cameras-config.json` | `/opt/d3kos/config/cameras-config.json` | JSON | Camera slot assignments for go2rtc. `{"cameras":[]}` = no cameras (go2rtc will not start) |
| `cloud-config.json` | `/opt/d3kos/config/cloud-config.json` | JSON | AtMyBoat.com endpoint and heartbeat configuration |

> `api-keys.json` contains the `amboat_api_key` which authenticates heartbeat calls with `Authorization: Bearer <amboat_api_key>` + `X-Device-Token: <UUID>`. This key must be preserved when reflashing a Pi.

---

## Part 4 — Key API Endpoints

Endpoints used by the Settings page (all on `localhost:3000`):

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/status` | 7-service status object (polls every 30 s) |
| GET | `/sysinfo` | Live IP, disk, memory, CPU temp, uptime |
| GET | `/health` | Simple health check |
| GET | `/health/report` | Full health report with agent status |
| POST | `/api/settings/vessel` | Save vessel name and home port from AI settings card |
| GET | `/api/vessel-home` | Current vessel name and home port |
| GET | `/api/recovery-key` | Device UUID for recovery key display |
| POST | `/action/restart` | Restart a named service (signalk/nodered/dashboard/gemini) |
| POST | `/action/reboot` | Reboot the Pi |
| GET | `/network/check-default-password` | Returns `{default: true}` if factory password unchanged |
| POST | `/network/change-password` | Change system password |
| POST | `/api/generate-reg-token` | Generate registration token for mobile pairing |
| GET | `/config/tier` | Current tier level |
| GET | `/api/boatlog/entries` | Boat log entry list |
| POST | `/api/boatlog/export` | Trigger boat log ZIP export |
| POST | `/api/boatlog/voice-note` | Submit a voice note to boat log |
