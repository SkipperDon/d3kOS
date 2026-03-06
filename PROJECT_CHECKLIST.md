# d3kOS Project Implementation Checklist

**Version:** 1.0 | **Status:** Active Development | **Current Version:** v0.9.5 → Target: v1.0.0

## 📋 LEGEND

- [ ] 

- Not Started

- \[🔄\] In Progress

- \[✅\] Complete

- \[⚠️\] Blocked/Issue

- \[🔍\] Verification Needed

- \[❌\] Failed/Not Working

**Verification Comments:** Issues found during testing noted with `\\\<!-- VERIFY: description --\\\>`

## Developer Infrastructure

### Ollama Executor (`deployment/scripts/ollama\\\_execute\\\_v3.py`)

- \[✅\] v2: enclosing-function context extraction, validation, auto-apply

- \[✅\] `helm\\\_os\\\_context.md` injected into every prompt

- \[✅\] Correction loop: flagged blocks sent back with targeted advice (1 retry)

- \[✅\] Parallel execution: `--parallel N` flag

- \[✅\] Fix 1: `ACTION: AFTER/BEFORE` aliases accepted (both executors)

- \[✅\] Fix 2: function parameters recognised as declared in scope (both executors)

- \[✅\] Fix 3: FIND\_LINE prompt rules — no comment lines, no bare `\\\{`/`\\\}`

- \[✅\] Wire RAG retrieval into executor: query `helm\\\_os\\\_source` before each phase

- \[✅\] v3: Generic executor — reads `phases.json`, no per-feature Python edits needed

- \[✅\] Fix 4: END\_LINE support — multi-line block replacement (FIND\_LINE → END\_LINE)

- \[✅\] Fix 5: RAG label changed to "BACKGROUND REFERENCE" — stops Ollama picking FIND\_LINEs from RAG context

- \[✅\] Fix 6: KNOWN\_GLOBALS expanded — Python exceptions (TypeError/ValueError/etc), port/starboard, indent

- \[✅\] Ollama REPLACE\_EXACT mode — Claude provides FIND\_LINE/END\_LINE in phases.json, Ollama writes CODE only

- \[✅\] `--skip-ollama` mode — loads pre-written `.instructions` files (spec code blocks), bypasses model when needed

- \[✅\] `benchmark.py` — 3-test suite, 5-dimension scoring (syntax/keywords/forbidden/variables/similarity), results saved to `benchmark\\\_results.json`

- \[✅\] Model benchmark run: qwen3-coder:30b **97/100** vs deepseek-coder-v2:16b 70/100 — qwen3 is executor default

### Project RAG Knowledge Base (`/home/boatiq/rag-stack/`)

- \[✅\] `helm\\\_os\\\_docs` collection: 1,079 chunks — docs, specs, session history, architecture

- \[✅\] `helm\\\_os\\\_source` collection: 54 chunks — live Pi `.py` + `.html` source files

- \[✅\] `helm\\\_os\\\_ingest.py`: smart filtered ingestion (excludes ATMYBOAT/fish/training noise)

- \[✅\] `ingest.py`: extended to support `.py` and `.html` files

- \[✅\] RAG retrieval wired into both executors — top-4 chunks injected before every Ollama call

- [ ] 

- Re-ingest `helm\\\_os\\\_source` after each Pi deployment (keeps code context current)

### Verify Agent (`deployment/scripts/verify\\\_agent.py`)

- \[✅\] `d3kos-verify-agent.service` deployed on TrueNAS VM `192.168.1.103:11436`

- \[✅\] `POST /verify` — receives generated code + instruction, returns `\\\{pass, score, issue, suggestion\\\}`

- \[✅\] `GET /health`, `/report`, `/stats` — monitoring endpoints accessible from laptop

- \[✅\] Inference routed to workstation `qwen3-coder:30b` GPU (TrueNAS CPU too slow — 0.03 t/s even on 1.5b due to bhyve ZFS ARC memory contention)

- \[✅\] `call\\\_verify()` wired into `ollama\\\_execute\\\_v3.py` — both REPLACE\_EXACT and standard modes

- \[✅\] FAIL → `Verify:` issue appended to block, triggers correction loop

- \[✅\] Verifier offline → `None` returned, pipeline continues uninterrupted

- \[✅\] Executor summary report now fetches verify stats from TrueNAS

- \[✅\] `helm\\\_os\\\_context.md` updated — Ollama knows its GENERATOR role and the two-step pipeline

- \[✅\] `deployment/docs/VERIFY\\\_AGENT.md` written — full architecture, endpoints, management commands

- \[✅\] `MEMORY.md` updated with verify agent details

### `helm\\\_os\\\_context.md` (`deployment/docs/`)

- \[✅\] Units.js return types and variable names

- \[✅\] Variable names for all Pi pages (dashboard, navigation, helm, weather, onboarding)

- \[✅\] query\_handler.py class structure and method signatures

- \[✅\] AI services: ports 8097/8099/8107, endpoints, `\\\_query\\\_gemini()` pattern, `ai\\\_used` constraint

- \[✅\] FIND\_LINE / ACTION / CODE format rules and example

## v0.9.1 — Voice AI Assistant `\\\[LARGE\\\]`

**Status:** \[✅\] Complete | **Shipped:** v0.9.1.x (multiple sessions) | **Priority:** HIGH

### Wake Word & Speech Pipeline

- \[✅\] Wake word detection — Vosk with constrained grammar (`\\\["helm"\\\]`)

- \[✅\] TTS responses — Piper (`en\\\_US-hfc\\\_male`) with pre-rendered acknowledgement audio

- \[✅\] "Aye Aye Captain" acknowledgement plays on wake word (~4s audio)

- \[✅\] `voice-assistant-hybrid.py` — full pipeline (listen → STT → query → TTS)

- \[✅\] Listen duration: 7s window after wake word (raised from 3s to allow TTS to finish)

- \[✅\] USB microphone renumbering fix — persistent device assignment across reboots

- \[✅\] Voice watchdog service — auto-restarts on crash

- \[✅\] Emergency reboot voice command — "Helm, reboot" via dbus

### Query Routing

- \[✅\] Rule-based engine data responses (RPM, oil, temperature, fuel, battery, speed, boost)

- \[✅\] RAG search for manual/technical questions

- \[✅\] Gemini 2.5 Flash for complex conversational queries (v0.9.4)

- \[✅\] Fallback chain: Gemini → RAG → rule-based

- \[✅\] Rule overmatch fixed (v0.9.5): diagnostic intent guard added + all patterns tightened to multi-word phrases

### Voice Assistant Service

- \[✅\] `d3kos-voice-assistant.service` — systemd, enabled, auto-start

- \[✅\] Integrated with SignalK for live engine data context

- \[✅\] Conversations logged to SQLite (`ai\\\_used`: online/onboard)

**Deliverable:** d3kOS v0.9.1.x — fully operational hands-free voice AI

## v0.9.2 — Metric/Imperial Conversion System `\\\[MEDIUM\\\]`

**Status:** \[✅\] Complete | **Shipped:** v0.9.2 (commit `e3ddbef`) | **Priority:** HIGH

### Foundation

- \[✅\] Create `/var/www/html/js/units.js` conversion utility — 9 types, 25/25 unit tests

  - \[✅\] Temperature conversion (°F ↔ °C)

  - \[✅\] Pressure conversion (PSI ↔ bar)

  - \[✅\] Speed conversion (knots+MPH ↔ knots+km/h)

  - \[✅\] Distance conversion (nm ↔ km)

  - \[✅\] Depth conversion (ft ↔ m)

  - \[✅\] Fuel conversion (gal ↔ L)

  - \[✅\] Length conversion (ft ↔ m)

  - \[✅\] Weight conversion (lb ↔ kg)

  - \[✅\] Displacement conversion (ci ↔ L)

- \[✅\] Extend Preferences API (Port 8107) — `preferences-api.py`, Flask, systemd

  - \[✅\] Add `measurement\\\_system` field to user preferences

  - \[✅\] GET /preferences endpoint

  - \[✅\] POST /preferences endpoint

  - \[✅\] Update `/opt/d3kos/config/user-preferences.json` schema

- \[✅\] Create Settings UI toggle

  - \[✅\] Add Measurement System section to settings.html

  - \[✅\] Toggle switch (Imperial/Metric)

  - \[✅\] Real-time page update without reload (waits for POST before reload)

### UI Updates

- \[✅\] Update Dashboard (`/var/www/html/dashboard.html` — index.html is launcher menu)

  - \[✅\] Engine temperature display (°F/°C)

  - \[✅\] Oil pressure display (PSI/bar)

  - \[✅\] Fuel level display (gal/L)

  - \[✅\] Boost pressure display (PSI/bar)

  - \[✅\] Coolant temperature display (°F/°C)

  - \[✅\] Speed display (knots+MPH/knots+km/h)

- \[✅\] Update Onboarding Wizard (`/var/www/html/onboarding.html`)

  - \[✅\] Step 15: Add auto-default logic based on boat origin

    - \[✅\] USA/Canada → Imperial

    - \[✅\] Europe/Asia/Oceania/Africa/South America → Metric

  - \[✅\] Step 9: Engine size input (ci/L dropdown)

  - \[✅\] Step 10: Engine power input (hp/kW dropdown)

  - \[✅\] Set preference in localStorage on boat origin selection

- \[✅\] Update Navigation page (`/var/www/html/navigation.html`)

  - \[✅\] Speed display (knots+MPH/knots+km/h)

  - \[✅\] Depth display (ft/m)

- \[✅\] Update Weather page (`/var/www/html/weather.html`)

  - \[✅\] Temperature display (°F/°C)

  - \[✅\] Wind speed display (knots+MPH/knots+km/h)

- [ ] 

- Update Boatlog display — deferred (not in v0.9.2 scope)

  - [ ] 

  - Display entries in user's preferred units

  - [ ] 

  - Stored data remains in imperial (no conversion on storage)

### Voice Assistant & Testing

- \[✅\] Update Voice Assistant (`/opt/d3kos/services/ai/query\\\_handler.py`)

  - \[✅\] Load user preferences on query

  - \[✅\] Convert RPM responses (no conversion needed, display only)

  - \[✅\] Convert oil pressure responses (PSI/bar)

  - \[✅\] Convert temperature responses (°F/°C)

  - \[✅\] Convert fuel responses (gal/L)

  - \[✅\] Convert battery responses (V - no conversion)

  - \[✅\] Convert speed responses (knots+MPH/knots+km/h)

  - \[✅\] Convert heading responses (degrees - no conversion)

  - \[✅\] Convert boost responses (PSI/bar)

- \[✅\] Integration Testing — 15/15 passing

  - \[✅\] Test Settings toggle (changes take effect immediately)

  - \[✅\] Test auto-default logic (all 7 region options)

  - \[✅\] Test dashboard live updates

  - \[✅\] Test onboarding wizard dropdowns

  - \[✅\] Test voice responses in both units

  - [ ] 

  - Test data export (includes unit metadata) — deferred

- \[✅\] Accuracy Verification — 25/25 unit tests passing

  - \[✅\] Temperature: 185°F = 85°C (±0.1°C)

  - \[✅\] Pressure: 45 PSI = 3.10 bar (±0.01 bar)

  - \[✅\] Speed: 10 knots = 18.52 km/h (±0.1 km/h)

  - \[✅\] Fuel: 50 gal = 189.3 L (±0.1 L)

  - \[✅\] Performance: \< 1ms conversion time

- [ ] 

- User Acceptance Testing — deferred to beta

  - [ ] 

  - Test with 5 metric users

  - [ ] 

  - Test with 5 imperial users

  - [ ] 

  - Collect feedback and iterate

### Deployment

- \[✅\] Git commit — `e3ddbef`

- \[✅\] Tag release as v0.9.2

- [ ] 

- Update CHANGELOG.md — pending

- \[✅\] Deploy to production Pi

- \[✅\] Verify all features working on live system

- \[✅\] Update documentation — UNITS\_API\_REFERENCE.md, UNITS\_FEATURE\_README.md

**Deliverable:** d3kOS v0.9.2 with full metric/imperial support

## v0.9.2 — Multi-Camera System `\\\[LARGE\\\]`

**Status:** \[✅\] Core complete — both cameras live, nginx fixed, fish detector running | **Priority:** HIGH

**Hardware:** 2 cameras active, 2 more planned for later:

- Camera 1 (bow, 10.42.0.100) — connected, live

- Camera 2 (stern, 10.42.0.63) — Reolink RLC-820A — connected, live

- Camera 3 & 4 — future purchase (RLC-820A × 2) — add to `cameras.json` when ready, no code changes needed

**Commit:** `be236c5`

### Camera Registry System

- \[✅\] Create camera configuration schema

  - \[✅\] `/opt/d3kos/config/cameras.json` deployed (id, name, location, ip, rtsp\_url, model, detection\_enabled)

- [ ] 

- Configure DHCP reservations

  - [ ] 

  - Reserve 10.42.0.100 (Bow) and 10.42.0.63 (Stern) in dnsmasq

  - [ ] 

  - Restart NetworkManager

- \[🔄\] Test camera connectivity

  - \[✅\] Bow camera connects (10.42.0.100, RTSP working)

  - \[✅\] Stern RLC-820A (10.42.0.63) — RTSP connected (`d3kos2026$`, stored percent-encoded)

### Multi-Camera Backend API

- \[✅\] Extend Camera Stream Manager (per-camera frame-grabber threads, graceful offline handling)

- \[✅\] Create new API endpoints (Port 8084)

  - \[✅\] GET `/camera/list` — all cameras + status

  - \[✅\] POST `/camera/switch/\\\<id\\\>` — switch active camera

  - \[✅\] GET `/camera/grid` — side-by-side JPEG of all cameras

  - \[✅\] GET `/camera/frame/\\\<id\\\>` — frame from specific camera

- \[✅\] Backwards-compatible endpoints: `/camera/status`, `/camera/frame`, `/camera/record/\\\*`, `/camera/capture`

- \[✅\] All endpoints tested with curl — both cameras live

- [ ] 

- 24-hour stability test (once both cameras connected)

### UI Implementation

- \[✅\] Update `/marine-vision.html`:

  - \[✅\] Camera selector buttons (Bow Camera / Stern Camera) — switches without page reload

  - \[✅\] Grid View toggle button — side-by-side via `/camera/grid`

  - \[✅\] Feed label shows active camera name

  - \[✅\] All-cameras status cards (shows connection state per camera)

- \[✅\] `settings.html` camera section — dynamic multi-camera display via `/camera/list`

  - \[✅\] Replaces hardcoded Camera 1 UI with live camera cards per camera

  - \[✅\] "Set Active" button per camera (calls `/camera/switch/\\\<id\\\>`)

  - \[✅\] "Open Marine Vision" button

  - \[✅\] Deployed to Pi — commit `9e53dfa`

- \[✅\] Camera position assignment (bow/stern/port/starboard per camera)

  - \[✅\] Spec written: `deployment/features/camera-position-assignment/feature\\\_spec.md`

  - \[✅\] API spec: `POST /camera/assign` with bow/stern/port/starboard positions

  - \[✅\] UI spec: assign buttons on each settings.html camera card

  - \[✅\] marine-vision.html spec: direction labels (Bow/Stern/Port/Starboard) instead of names

  - \[✅\] Applied via `--skip-ollama` with spec code blocks as instructions files

  - \[✅\] `/camera/list` returns `position` field for each camera

  - \[✅\] cameras.json updated with `position: bow/stern`, ownership fixed to d3kos

  - \[✅\] Deployed to Pi — commit `dbff06e`

- [ ] 

- DHCP / static IP confirmation (cameras should stay on same IPs)

- [ ] 

- Test UI on touchscreen + mobile

### Testing & Optimization

- [ ] 

- Performance testing

  - [ ] 

  - Measure CPU usage (target: \< 35%)

  - [ ] 

  - Measure memory usage (target: \< 970 MB total)

  - [ ] 

  - Measure bandwidth (grid: \< 12 Mbps, single: \< 4 Mbps)

  - [ ] 

  - Test with both cameras for 24 hours continuous

- [ ] 

- Resource optimization

  - [ ] 

  - Tune frame rates if needed

  - [ ] 

  - Optimize detection frequency

  - [ ] 

  - Add frame dropping if overloaded

- [ ] 

- Storage management

  - [ ] 

  - Implement motion-triggered recording

  - [ ] 

  - Set 7-day retention policy

  - [ ] 

  - Add automatic cleanup (old recordings)

  - [ ] 

  - Verify storage usage (target: \< 28 GB for 7 days)

- [ ] 

- Integration testing

  - [ ] 

  - Test camera switching in all scenarios

  - [ ] 

  - Test grid view performance

  - [ ] 

  - Test Forward Watch with real obstacles

  - [ ] 

  - Test with weak network conditions

- [ ] 

- Bug fixes

  - [ ] 

  - Fix any issues found in testing

  - [ ] 

  - Retest after fixes

### Documentation & Deployment

- [ ] 

- Update documentation

  - [ ] 

  - User guide for multi-camera system

  - [ ] 

  - Setup instructions for additional cameras

  - [ ] 

  - Troubleshooting guide

  - [ ] 

  - API documentation updates

- [ ] 

- Hardware setup

  - \[✅\] Camera 1 — Bow camera (10.42.0.100) — on network, RTSP working

  - \[✅\] Camera 2 — Reolink RLC-820A (10.42.0.63) — on network

  - \[✅\] RLC-820A password confirmed (`d3kos2026$`), `cameras.json` updated, service restarted

  - [ ] 

  - Decide on mounting location for RLC-820A (stern confirmed in registry — verify physical mount)

  - \[✅\] Both cameras verified accessible via RTSP

- \[✅\] Deployment — core deployed, commits `be236c5`, `9478f1d`

  - \[✅\] `cameras.json` → `/opt/d3kos/config/`

  - \[✅\] `camera\\\_stream\\\_manager.py` → `/opt/d3kos/services/marine-vision/`

  - \[✅\] `marine-vision.html` → `/var/www/html/`

  - \[✅\] Service restarted, bow camera live

  - \[✅\] Both cameras live — bow (10.42.0.100) + stern RLC-820A (10.42.0.63)

- [ ] 

- User training

  - [ ] 

  - Create video tutorial

  - [ ] 

  - Write quick start guide

  - [ ] 

  - Train user on camera switching and grid view

**Deliverable:** d3kOS v0.9.2 — 2-camera system live (bow + stern). Cameras 3 & 4 deferred — no code changes needed when added, just update `cameras.json`.

**Also fixed this session:**

- \[✅\] nginx: all 18 service proxies restored (wiped during Part 5 nginx corruption fix)

- \[✅\] Fish detector: restarted after dependency failure (camera stream was down Feb 28) — YOLOv8n + 483 species active

## v0.9.2— Gemini API Integration `\\\[SMALL\\\]`

**Status:** \[✅\] Complete | **Shipped:** v0.9.4 (commit `02d2694`) | **Priority:** MEDIUM

### Tasks

- \[✅\] Backend Gemini proxy service (Port 8097 — `d3kos-gemini-proxy.service`)

- \[✅\] Settings UI: API key input, model selector, Save + Test Connection

- \[✅\] `query\\\_handler.py`: `\\\_query\\\_gemini()` method + routing (Gemini → RAG fallback)

- \[✅\] `GEMINI\\\_SETUP.md` setup guide with step-by-step API key instructions

- \[✅\] End-to-end tested: "what causes white smoke from marine exhaust" → Gemini 8s ✓

- [ ] 

- Onboarding wizard integration (Steps 17.x) — deferred to future version

**Note:** Port 8099 was occupied by `issue\\\_detector.py` — Gemini proxy uses port 8097.

**Deliverable:** d3kOS v0.9.4 with conversational AI via Gemini 2.5 Flash

## v0.9.2 — Remote Access API `\\\[SMALL\\\]`

**Status:** \[✅\] Phase 1 Complete | **Shipped:** v0.9.5 | **Priority:** HIGH

### Tasks

- \[✅\] `remote\\\_api.py` — Flask service on port 8111 with API key auth

- \[✅\] `GET /remote/health` — unauthenticated health check

- \[✅\] `GET /remote/status` — all boat metrics from SignalK (engine, nav, systems)

- \[✅\] `GET /remote/maintenance` — last 20 maintenance log entries

- \[✅\] `POST /remote/note` — add maintenance note from phone

- \[✅\] Systemd service `d3kos-remote-api.service` (enabled, active)

- \[✅\] Nginx proxy `/remote/` → `localhost:8111`

- \[✅\] API key generated and stored in `api-keys.json`

- \[✅\] `REMOTE\\\_ACCESS\\\_SETUP.md` with Tailscale + LAN + port-forward options

- \[✅\] Tailscale install on Pi — connected, IP: `100.88.112.63` (networkdon89@ account)

- [ ] 

- Camera stream relay RTSP → HLS (blocked: cameras not purchased)

- [ ] 

- WebSocket real-time push (future — polling via /remote/status is sufficient for now)

- \[✅\] **"My Remote Access" settings page** (`remote-access.html`) — commit `06a6a94`

  - \[✅\] Display Tailscale IP (fetched live from `/remote/config`)

  - \[✅\] Display API key (masked by default, tap to reveal, copy button)

  - \[✅\] Generate QR code linking to `http://100.88.112.63` — scan with phone camera, no typing

  - \[✅\] 4-step connection instructions

  - \[✅\] Fallback: shows local IP QR + warning when Tailscale is off

  - \[✅\] Button added to Settings page

**Deliverable:** d3kOS v0.9.5 — Remote status readable from phone anywhere via Tailscale

## v0.9.2 — Multi-Language Support `\\\[LARGE\\\]`

**Status:** \[🔄\] Phase 1 Complete — Foundation deployed 2026-03-06 | **Priority:** REQUIRED for v1.0

### Tasks

- \[✅\] i18n system foundation: 18 JSON translation files + onboarding.json + language API (GET/POST /api/language, GET /api/i18n/<lang_code>, GET /api/languages) added to network-api.py

- \[✅\] language-menu.html deployed — 18-language touch-optimised selector page

- \[✅\] Globe button on index.html (fixed top-right, shows current language code loaded from API)

- \[✅\] Language Settings tile on settings.html

- \[✅\] Language selection overlay on onboarding.html (shown on first boot when language = default English)

- \[🔄\] UI translation (all pages with data-i18n attributes) — foundation in place, page-by-page translation pending

- [ ] Professional translation review (French, Spanish, German, Italian, Dutch, Swedish, Norwegian)

- [ ] Voice assistant integration (Piper TTS models per language)

- [ ] Native speaker testing and QA

### Languages (18 deployed — JSON files + language selector)

- \[✅\] English (en) — Default

- \[✅\] French (fr)

- \[✅\] Spanish (es)

- \[✅\] German (de)

- \[✅\] Italian (it)

- \[✅\] Dutch (nl)

- \[✅\] Swedish (sv)

- \[✅\] Norwegian (no)

- \[✅\] Danish (da)

- \[✅\] Finnish (fi)

- \[✅\] Portuguese (pt)

- \[✅\] Greek (el)

- \[✅\] Croatian (hr)

- \[✅\] Turkish (tr)

- \[✅\] Arabic (ar) — RTL

- \[✅\] Chinese (zh)

- \[✅\] Japanese (ja)

- \[✅\] Ukrainian (uk)

**Deliverable:** d3kOS v0.15.0 with full 18-language support (Phase 1 foundation: DONE — page-by-page translation: pending)

## signalk-forward-watch — Standalone Signal K Community Plugin

**Status:** \[✅\] v0.1.0 Published | **Priority:** HIGH **Repo:** [https://github.com/SkipperDon/signalk-forward-watch](https://github.com/SkipperDon/signalk-forward-watch) **npm:** signalk-forward-watch **Project dir:** `/home/boatiq/signalk-forward-watch/`

### Model Training

- \[✅\] Dataset prepared — 21,719 labeled images (19,500 train / 2,219 val)

- \[✅\] YOLOv8n training complete — workstation RTX 3060 Ti, 100 epochs

- \[✅\] Export best.pt → ONNX (12MB)

- \[✅\] forward-watch.onnx uploaded to GitHub Releases v0.1.0

### Plugin Code

- \[✅\] `package.json`

- \[✅\] `index.js`

- \[✅\] `plugin/camera-discovery.js`

- \[✅\] `plugin/rtsp-grabber.js`

- \[✅\] `plugin/detector.js`

- \[✅\] `plugin/gps-calculator.js`

- \[✅\] `plugin/signalk-output.js`

- \[✅\] `plugin/opencpn-output.js` — detections appear as AIS targets in OpenCPN

### Deployment & Publishing

- \[✅\] Deployed and confirmed working on d3kOS Pi

- \[✅\] Published to GitHub — v0.1.0

- \[✅\] README with full field reference, install instructions, OpenCPN section

- \[✅\] Announced on Signal K Discord

- \[✅\] Announced on OpenMarine forum

- \[ \] Test on OpenPlotter

- \[ \] `npm publish` to npm registry — NOTE: account created but sign-in broken (tried multiple browsers). Try again later or contact npm support. Username/email on file.

- \[ \] Add download-on-first-run (auto-fetch model from GitHub Releases)

**Deliverable:** `signalk-forward-watch` on npm / Signal K AppStore

## v0.9.2 — Community Features `\\\[SMALL\\\]`

**Status:** \[ \] Not Started | **Priority:** LOW

### Tasks

- [ ] 

- Anonymous engine benchmark service

- [ ] 

- Anonymizer service (position randomization, ID hashing)

- [ ] 

- Community boat map (opt-in, privacy-first)

- [ ] 

- Hazard/POI marker system (user-submitted, vote system)

- [ ] 

- Knowledge base to pattern sync

**Deliverable:** d3kOS v0.14.0 with community features

## v0.9.2 — Post-Install Bug Fixes & UI Polish `\\\[MEDIUM\\\]`

**Status:** \[✅\] Complete (deployed 2026-03-05, Part 12 — all 14 fixes via Ollama executor) | **Priority:** CRITICAL — Blocking demo quality | **Spec:** `deployment/features/post-install-fixes/OLLAMA\_SPEC.md`

> These issues were identified during first full boot and functional test of v0.9.5. All items to be implemented by Ollama workstation. Claude is planner/reviewer only.


### 1. Dashboard — SignalK Disconnected Banner

- ✅ Detect SignalK connection status on page load (poll `/signalk/v1/api/` on port 3000)

- ✅Show yellow banner when disconnected: "⚠️ Signal K is offline — Go to Settings → System Actions to restart"

- ✅ Banner includes tap-to-navigate button → `settings.html\#system-actions`

- ✅ Banner auto-dismisses when SignalK comes back online (re-poll every 5s)

- ✅ Do not show banner when SignalK is connected

### 2. Engine Benchmark — Not Working

- \[✅\] Investigate why Engine Benchmark page is non-functional

- \[✅\] Check benchmark API endpoint availability and response

- \[✅\] Verify benchmark data collection is running (d3kos-health.service feeding data)

- \[✅\] Fix any broken API calls or missing data connections

- \[✅\] Confirm benchmark displays on dashboard after fix

### 3. Export — Race Condition at Boot

- \[✅\] Add retry loop (max 5 × 3s) in `export-daily.sh` for tier API health check before proceeding

- \[✅\] Add retry loop in `export-on-boot.sh` for export-manager API health check

- \[✅\] Add `After=d3kos-tier-api.service` to `d3kos-export-daily.service` unit file

- \[✅\] Test: reboot, verify both export services succeed (no exit code 7)

- \[✅\] Deploy updated scripts and service files to Pi

### 4. Navigation — GPS Readings Not Showing

- ✅Verify SignalK `gps` and `ais` pipedProviders are enabled (fixed 2026-03-04 — verify persists after redeploy)

- ✅ Confirm navigation.html reads from correct SignalK paths: `navigation/position`, `navigation/speedOverGround`, `navigation/headingTrue`, `navigation/courseOverGroundTrue`

- ✅Fix any broken SignalK data paths on navigation page

- ✅Verify depth, speed, COG, SOG all display when GPS has a fix

- ✅Add "No GPS fix" indicator when `mode \< 2` (instead of blank fields)

### 5. Boatlog — Voice Note & Export

- \[✅\] **Voice Note**: Add microphone button to boatlog.html that records a voice note using browser MediaRecorder API → uploads to `/boatlog/voice-note` endpoint

- \[✅\] **Voice Note API**: Add `POST /boatlog/voice-note` to `boatlog-api.py` — saves WAV to `/opt/d3kos/data/boatlog-audio/` with timestamp filename, transcribes via Vosk, stores text in boatlog entry

- \[✅\] **Export**: Verify boatlog export endpoint works end-to-end (CSV + JSON)

- \[✅\] **Export button**: Confirm boatlog.html export button calls correct API and downloads file

- \[🔍\] Test voice note record → transcribe → save → view cycle (verify agent flagged syntax — test on Pi)

### 6. Weather — GPS Centering & Wind/Clouds Overlay

- \[✅\] **Root cause**: `weather.html` has hardcoded fallback `\{ lat: 44.4167, lon: -79.3333 \}` (Lake Simcoe). Map initialises with this before GPS resolves.

- \[✅\] **Fix**: On page load, fetch GPS position from SignalK (`/signalk/v1/api/vessels/self/navigation/position`) before initialising map. Show loading state.

- \[✅\] If SignalK returns no position (no fix), fallback to Lake Simcoe with a visible "No GPS — using default location" label

- \[✅\] **Wind/Clouds overlay**: Debug why wind and cloud layers are not rendering. Check OpenWeatherMap API key is configured. Check tile URL format and layer names.

- \[✅\] Verify `recenter` button recenters to live GPS position, not hardcoded fallback

- \[✅\] Test with GPS active: map must open centred on actual vessel position

### 7. Marine Vision — Camera Errors & Fish Detector

- \[✅\] **Stern camera**: Debug why stern camera (10.42.0.63) shows error. Cameras are on 10.42.0.x (boat hotspot network — not available at home). Add graceful offline message: "Camera offline — not on boat network" instead of error.

- \[✅\] **Bow camera**: Same graceful offline handling for 10.42.0.100

- \[✅\] **Fish detector**: Verify `fish\_detector.py` handles camera-offline state without crashing. Add health check that returns `offline` state cleanly.

- \[🔍\] **UI**: When cameras offline, show placeholder with camera name + "Offline — Connect to boat network" instead of error/broken image (only CSS injected — verify JS onerror handlers work on Pi)

- \[✅\] **Fish detector API**: Ensure `/fish/status` returns `\{ "status": "offline", "reason": "camera unavailable" \}` not an error when camera not reachable

### 8. Charts — OpenCPN Flatpak Migration

- \[✅\] **Research** (Claude has done this): OpenCPN available on Flathub as `org.opencpn.OpenCPN`. Flatpak version supports plugins via built-in plugin installer. Works on ARM64 Trixie.

- \[✅\] **Phase 1 — Install Flatpak**: `sudo apt install flatpak` + add Flathub repo

- \[✅\] **Phase 2 — Export current settings**: Back up `~/.opencpn/` (charts, config, plugins) before removing native package

- \[✅\] **Phase 3 — Remove native package**: `sudo apt remove opencpn` (retain config backup)

- \[✅\] **Phase 4 — Install Flatpak OpenCPN**: `flatpak install flathub org.opencpn.OpenCPN` — Flatpak 5.12.4 confirmed installed system-wide

- \[✅\] **Phase 5 — Migrate settings**: Flatpak config already initialised with touchscreen settings at `~/.var/app/org.opencpn.OpenCPN/config/opencpn/`

- \[✅\] **Phase 6 — Update launcher**: `install-opencpn.sh` fixed — uses `flatpak run org.opencpn.OpenCPN` (no --user); DISPLAY/XAUTHORITY set correctly

- \[✅\] **Phase 7 — Plugins**: o-charts and AIS Radar View installed via Flatpak plugin manager; AIS pipeline active (Signal K → signalk-to-nmea0183 → TCP 10110 → OpenCPN)

- \[✅\] Applied `sudo flatpak override --device=input --device=dri` for touchscreen and display

- \[🔍\] Verify touchscreen touch and pinch-zoom work in Flatpak OpenCPN (test on Pi at dock)

- \[⚠️\] o-charts chart activation pending — user must: go to o-charts.org → My Charts → Assign device using fingerprint file `oc03L_1772818229.fpr` → download charts → copy to `~/.var/app/org.opencpn.OpenCPN/data/opencpn/charts/`

### 9. Boat Setup Wizard — Gemini API Configuration Step

- ✅ **Confirmed gap**: Gemini configuration was deferred from onboarding wizard (checklist item: "Onboarding wizard integration — deferred to future version")

- ✅Add Step 17 to `onboarding.html`: "AI Assistant Setup"

  - ✅Input field: Gemini API key (optional — skip button available)

  - ✅Test Connection button → calls `/gemini/test` endpoint

  - ✅On success: green tick + "AI Assistant ready"

  - ✅ On skip: note that AI can be configured later in Settings

  - ✅ Saves key to gemini config on `POST /gemini/config`

- ✅ Ensure step is skippable (boat works fully without Gemini key)

### 10. AI Assistant — RAG Precision Improvement

- \[✅\] **Embedding re-ingest**: Re-ingest `helm\_os\_source` collection after this deployment (`helm\_os\_ingest.py --collection source`) to keep source current

- \[✅\] **Query precision**: In `query\_handler.py`, increase `n\_results` from 4 to 6 for RAG retrieval on technical questions

- \[✅\] **Score threshold**: Filter RAG results with cosine distance \< 0.4 (discard weak matches that add noise)

- \[✅\] **Context window**: When RAG results are used, include the collection name + chunk source file in the prompt context so Ollama knows where information came from

- \[🔍\] **Hybrid routing**: Verify score 30 from verify agent — check `query\_handler.py` on Pi to confirm n\_results increase deployed correctly

### 11. System Boot — Keyring Auto-Unlock

- **✅Assessment**: gnome-keyring runs on boot (`/usr/bin/gnome-keyring-daemon`), prompts for password. On a dedicated marine device this is unacceptable.

- **✅Solution A — Empty password keyring** (recommended for dedicated device):

  - ✅Set keyring password to empty string via `seahorse` or `secret-tool`

  - ✅ Configure PAM to auto-unlock keyring on auto-login: add `auth optional pam\_gnome\_keyring.so` to `/etc/pam.d/lightdm-autologin`


- ✅ Test: reboot → desktop appears without any password prompt → d3kOS UI launches automatically

- ✅Ensure SSH still requires password (security boundary)

### 12. Settings — Measurement System Section Formatting

- \[✅\] **Root cause**: `settings.html` line 627 uses `\<h2\>Measurement System\</h2\>` without `class="section-header"` and without an emoji icon

- \[✅\] **Fix**: Change to `\<h2 class="section-header"\>📏 Measurement System\</h2\>` to match all other sections

- \[✅\] Also check lines 691+ for `\<h2\>🤖 AI Assistant — Gemini API\</h2\>` — apply same class if missing

- \[✅\] Visual test: confirm Measurement System heading matches Engine Configuration, Units & Display, etc.

### 13. Settings — System Actions Actually Work

- \[✅\] **Root cause**: `restartsignalk()`, `restartNodered()`, `rebootSystem()` at lines 1019-1034 only show `alert()` with SSH instructions — they do nothing

- \[✅\] **Create Settings Action API** (`d3kos-settings-api.py`, port 8101):

  - \[✅\] `POST /settings/restart-signalk` → `subprocess.run(\['sudo', 'systemctl', 'restart', 'signalk'\])`

  - \[✅\] `POST /settings/restart-nodered` → `subprocess.run(\['sudo', 'systemctl', 'restart', 'nodered'\])`

  - \[✅\] `POST /settings/reboot` → `subprocess.run(\['sudo', 'reboot'\])`

  - \[✅\] `POST /settings/initial-setup-reset` → call existing reset logic

  - \[✅\] All endpoints return `\{ "success": true, "message": "..." \}`

  - \[✅\] Add sudoers rule: `d3kos ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart signalk, /usr/bin/systemctl restart nodered, /usr/bin/reboot`

- \[✅\] **Update settings.html**: Replace all `alert()` calls with `fetch('/settings/restart-signalk', \{method:'POST'\})` calls

- \[✅\] **Confirm with user before reboot**: reboot action shows confirmation dialog first

- \[✅\] Add nginx proxy `/settings/action/` → `localhost:8101`

- \[✅\] Create systemd service `d3kos-settings-api.service`, enable, deploy

### 14. All Pages — Scrollbar Size (Touch-Friendly)

- \[✅\] **Root cause**: All pages with right-side scrollbars use default browser scrollbar (~8-12px wide) — impossible to grab accurately on touchscreen

- \[✅\] **Fix**: Add global CSS rule to ALL html pages (or shared CSS file): scrollbar must be minimum 5× current size (~50-60px wide) with high-contrast track and thumb

- \[✅\] Apply to: `dashboard.html`, `navigation.html`, `weather.html`, `marine-vision.html`, `boatlog.html`, `settings.html`, `onboarding.html`, and any other pages with scrollable content (56px scrollbars deployed to all 26 pages)

- \[✅\] CSS added: `::-webkit-scrollbar { width: 56px }` + track/thumb/active rules on all pages

- \[✅\] Also created shared `d3kos-touch.css` (2026-03-06) with touch-action, tap-highlight, and overscroll rules

- \[✅\] Test on touchscreen: scrollbar must be easy to grab and drag with a finger


**Deliverable:** All 14 items resolved. d3kOS fully functional on first boot with no SSH required for any operation.

**Spec for Ollama:** `deployment/features/post-install-fixes/OLLAMA\_SPEC.md`

## v0.9.4 — Mobile Apps (iOS/Android) `\\\[LARGE\\\]`

**Status:** \[ \] Not Started | **Priority:** HIGH

### Tasks

- [ ] 

- AtMyBoat.com VPS setup (Headscale, MQTT, PostgreSQL)

- [ ] 

- REST API + web dashboard

- [ ] 

- React Native mobile app

- [ ] 

- Pi integration (Tailscale, MQTT publisher)

**Deliverable:** d3kOS v0.9.5 + AtMyBoat.com cloud platform

## v0.9.5 — Predictive Maintenance `\\\[LARGE\\\]`

**Status:** \[ \] Not Started | **Priority:** HIGH

### Tasks

- [ ] 

- Data collection (30-day baseline)

- [ ] 

- Anomaly detection algorithms

- [ ] 

- ML models (5 models: overheating, oil, battery, SD card, GPS)

- [ ] 

- Alert system integration

- [ ] 

- Additional automation (weather, fuel, maintenance scheduling)

**Deliverable:** d3kOS v0.10.0 with predictive maintenance

## v0.9.6 — Fleet Management `\\\[MEDIUM\\\]`

**Status:** \[ \] Not Started | **Priority:** MEDIUM

### Tasks

- [ ] 

- Fleet creation and invitation system

- [ ] 

- Fleet map with live vessel positions

- [ ] 

- Fleet analytics (engine hours, fuel, alerts)

- [ ] 

- Testing and Tier 3 activation

**Deliverable:** d3kOS v0.10.1 with fleet management

## v0.9.6 — Remote Diagnostic Console `\\\[MEDIUM\\\]`

**Status:** \[ \] Not Started | **Priority:** MEDIUM

### Tasks

- [ ] 

- Support ticket system + consent flow

- [ ] 

- Diagnostic agent (log collection)

- [ ] 

- Claude API + AI diagnosis

- [ ] 

- Fix delivery + user approval

- [ ] 

- Knowledge base and admin console

**Deliverable:** d3kOS v0.11.0 with remote diagnostics

## v0.9.7 — Autonomous Agents `\\\[LARGE\\\]`

**Status:** \[ \] Not Started | **Priority:** HIGH

### Tasks

- [ ] 

- Agent framework (base class, scheduler, communication bus)

- [ ] 

- Update agent (GitHub integration, backup/restore, auto-rollback)

- [ ] 

- Performance agent (CPU/memory/disk monitoring, auto-remediation)

- [ ] 

- Storage agent (cleanup automation, predictive warnings)

- [ ] 

- Health check agent (daily reports, weekly scans)

- [ ] 

- Backup agent (incremental backups, cloud sync)

- [ ] 

- Testing (reliability, failure modes, UAT)

**Deliverable:** d3kOS v0.12.0 with autonomous agents

## v0.9.5 — AI Action Layer `\\\[SMALL\\\]`

**Status:** \[✅\] Complete | **Shipped:** v0.9.5 (commit `c68d8c6`) | **Priority:** MEDIUM

### Tasks

- \[✅\] `classify\\\_action\\\_query()` — detect action intent before simple/Gemini routing

- \[✅\] `execute\\\_action()` — whitelist dispatcher (log\_note, log\_hours, set\_fuel\_alarm)

- \[✅\] `\\\_append\\\_maintenance\\\_log()` — append-only JSON log at `/opt/d3kos/data/maintenance-log.json`

- \[✅\] `\\\_set\\\_pref()` — write to `user-preferences.json` for config changes

- \[✅\] Wired into `query()` — action check runs before all other routing

- \[✅\] 10/10 classification tests pass

- \[✅\] Deployed to Pi, services restarted

### Supported Actions

| Phrase | Action | Output |
| - | - | - |
| "log a note \[text\]" | log\_note | Appends note to maintenance-log.json |
| "note that \[text\]" | log\_note | Same |
| "log engine hours \[N\]" | log\_hours | Logs engine hours entry |
| "set fuel alarm to \[N\] percent" | set\_fuel\_alarm | Updates user-preferences.json |


**Deliverable:** d3kOS v0.9.5 with voice-triggered maintenance logging and config actions

## v0.9.7 — Failure Intelligence & Recovery `\\\[SMALL\\\]`

**Status:** \[ \] Not Started | **Priority:** MEDIUM

### Tasks

- [ ] 

- Failure pattern recognition

- [ ] 

- Community data aggregation

- [ ] 

- Recovery playbook system

- [ ] 

- Testing and knowledge base integration

**Deliverable:** d3kOS v0.13.0 with failure intelligence

## v0.9.8 — Security Audit & Penetration Testing `\\\[LARGE\\\]`

**Status:** \[ \] Not Started | **Priority:** CRITICAL — Required before v1.0 launch

### Automated Security Scanning

- [ ] 

- Run npm audit (Node.js dependencies)

- [ ] 

- Run pip-audit (Python dependencies)

- [ ] 

- OWASP ZAP automated scan (all web endpoints)

- [ ] 

- SQL injection testing (SQLMap on all database queries)

- [ ] 

- Review OWASP Top 10 compliance

- [ ] 

- Scan for hardcoded secrets in codebase

- [ ] 

- Check file permissions on sensitive files

### Manual Code Review

- [ ] 

- Authentication/authorization review

  - [ ] 

  - Verify all API endpoints require auth

  - [ ] 

  - Check JWT token validation

  - [ ] 

  - Review session management

  - [ ] 

  - Test for session hijacking

- [ ] 

- Input validation review

  - [ ] 

  - Check all user inputs for XSS prevention

  - [ ] 

  - Verify parameterized database queries

  - [ ] 

  - Test file upload security

  - [ ] 

  - Check for command injection vulnerabilities

  - [ ] 

  - Test for directory traversal attacks

- [ ] 

- Secrets management review

  - [ ] 

  - API key storage (should be encrypted)

  - [ ] 

  - Password hashing (bcrypt/scrypt)

  - [ ] 

  - Certificate management

  - [ ] 

  - Webhook signature verification

### Penetration Testing (External Firm)

- [ ] 

- Contract professional penetration testing firm

- [ ] 

- External penetration test (network-level attacks)

- [ ] 

- Internal penetration test (privilege escalation)

- [ ] 

- API endpoint fuzzing (all 20+ services)

- [ ] 

- WireGuard VPN security review

- [ ] 

- MQTT broker security audit (TLS, ACLs)

- [ ] 

- Signal K server security review

- [ ] 

- Rate limiting and DDoS protection testing

### Fixes & Privacy Compliance

- [ ] 

- Fix all critical vulnerabilities (must be zero)

- [ ] 

- Fix all high vulnerabilities (must be zero)

- [ ] 

- Document medium/low vulnerabilities with mitigation plans

- [ ] 

- GDPR compliance verification

  - [ ] 

  - Data retention policy implementation

  - [ ] 

  - User data export functionality (Article 20)

  - [ ] 

  - Data deletion functionality (Article 17)

  - [ ] 

  - Privacy policy review and update

- [ ] 

- CCPA compliance verification (California users)

- [ ] 

- Retest after fixes

- [ ] 

- Obtain penetration test certificate

### Critical Checklist (Must Pass)

- [ ] 

- Zero critical vulnerabilities

- [ ] 

- Zero high vulnerabilities

- [ ] 

- All API endpoints require authentication

- [ ] 

- All database queries use parameterized statements

- [ ] 

- All passwords hashed with bcrypt/scrypt

- [ ] 

- No hardcoded secrets in code

- [ ] 

- All external APIs use HTTPS

- [ ] 

- Rate limiting on all public endpoints

- [ ] 

- MQTT topics secured with ACLs

- [ ] 

- File uploads validated for malicious content

- [ ] 

- Sessions expire properly

- [ ] 

- All webhooks validate signatures

- [ ] 

- GDPR/CCPA compliant

- [ ] 

- Penetration test certificate obtained

**Deliverable:** d3kOS v0.16.0 — Security certified, production ready

## v1.0.0 — Incremental Update System & Production Launch `\\\[LARGE\\\]`

**Status:** \[ \] Not Started | **Priority:** HIGH

### Incremental Update System

- [ ] 

- Enhanced update service (signature verification, checksum)

- [ ] 

- Pre-update snapshot system

- [ ] 

- Post-update health check and auto-rollback

- [ ] 

- Update package storage (AtMyBoat.com)

- [ ] 

- Admin console update manager

### Production Launch Checklist

- [ ] 

- All v0.x versions deployed and stable

- [ ] 

- Security audit passed (v0.16.0)

- [ ] 

- Multi-language support active (v0.15.0)

- [ ] 

- Documentation complete (user + developer guides)

- [ ] 

- Professional website launched (AtMyBoat.com)

- [ ] 

- Support infrastructure ready (ticketing, diagnostic console)

- [ ] 

- Payment processing active (Stripe, Apple IAP, Google Play)

- [ ] 

- Beta testing complete (100+ users, 6+ months)

- [ ] 

- Performance targets met (uptime \> 99.5%, response \< 3s)

- [ ] 

- Backup and recovery tested

- [ ] 

- Disaster recovery plan documented

- [ ] 

- Legal review complete (terms, privacy, GDPR/CCPA)

- [ ] 

- Marketing materials ready

- [ ] 

- Press release prepared

- [ ] 

- Launch date announced

**Deliverable:** d3kOS v1.0.0 — Production ready, international marine electronics platform

## 📊 OVERALL PROGRESS TRACKING

### Milestones

- \[✅\] v0.9.1 Complete (Voice AI Assistant)

- \[✅\] v0.9.2 Complete (Metric/Imperial)

- \[✅\] v0.9.3 Complete (Complete Website Rewrite — full dark marine UI, all 9 pages)

- \[✅\] v0.9.2 Complete (Multi-Camera System) — both cameras live, nginx fixed, fish detector running

- \[✅\] v0.9.4 Complete (Gemini AI Integration)

- \[✅\] v0.9.5 Complete (AI Action Layer + Remote Access API + Tailscale)

- \[✅\] v0.9.5 Complete (Post-Install Bug Fixes — all 14 items, deployed 2026-03-05)

- \[🔄\] v0.9.x In Progress (i18n Multi-Language Foundation — 18 languages, Phase 1 deployed 2026-03-06)

- \[🔄\] v0.9.x In Progress (OpenCPN Flatpak + AIS Pipeline — Flatpak live, AIS flowing, o-charts activation pending)

- [ ] 

- v0.9.6 Complete (Remote Access & Camera Streaming) — cameras not purchased

- [ ] 

- v0.9.6 Complete (Fleet Management)

- [ ] 

- v0.10.0 Complete (Predictive Maintenance)

- [ ] 

- v0.11.0 Complete (Diagnostic Console)

- [ ] 

- v0.12.0 Complete (Autonomous Agents)

- [ ] 

- v0.12.1 Complete (AI Action Layer — extended)

- [ ] 

- v0.13.0 Complete (Failure Intelligence)

- [ ] 

- v0.14.0 Complete (Community Features)

- [ ] 

- v0.15.0 Complete (Multi-Language) — REQUIRED for v1.0

- [ ] 

- v0.16.0 Complete (Security Audit) — REQUIRED for v1.0

- [ ] 

- v1.0.0 LAUNCHED (Production Release)

### Critical Path

- \[✅\] v0.9.1 (Voice AI) — DONE

- \[✅\] v0.9.2 (Metric/Imperial) — DONE

- \[✅\] v0.9.3 (Complete Website Rewrite) — DONE

- \[✅\] v0.9.4 (Gemini AI) — DONE

- \[✅\] v0.9.2 (Multi-Camera) — both cameras live, nginx fixed, fish detector running

- \[✅\] Fix: voice rule overmatch ("speed" pattern) — FIXED commit `680a795`

- \[✅\] v0.9.5 (Post-Install Bug Fixes) — all 14 deployed 2026-03-05

- \[🔄\] v0.x (Multi-Language Phase 1) — foundation deployed 2026-03-06, page translation pending

- \[🔄\] v0.x (OpenCPN + AIS) — Flatpak live, AIS flowing, o-charts activation pending

- [ ] v0.15.0 (Multi-Language full) — REQUIRED for v1.0

- [ ] v0.16.0 (Security Audit) — REQUIRED for v1.0

### Risk Areas (Monitor Closely)

- [ ] 

- Security vulnerabilities (must be zero critical/high at v1.0)

- [ ] 

- Performance degradation (monitor CPU/memory/bandwidth)

- [ ] 

- Third-party API dependencies (Google Gemini, Stripe, Apple, Google Play)

- [ ] 

- Hardware compatibility (cameras, GPS, CAN bus)

- [ ] 

- User adoption (need 1,000+ Tier 2 users for break-even)

- [ ] 

- International compliance (GDPR, CCPA, translation quality)

## 📝 NOTES & CONVENTIONS

### Checklist Update Protocol

1. When starting a task: Change `\\\[ \\\]` to `\\\[🔄\\\]`

2. When completing a task: Change `\\\[🔄\\\]` to `\\\[✅\\\]`

3. When blocked: Change to `\\\[⚠️\\\]` and add comment explaining blocker

4. When verification fails: Change to `\\\[🔍\\\]` and add `\\\<!-- VERIFY: issue description --\\\>`

5. When something doesn't work: Change to `\\\[❌\\\]` and add `\\\<!-- NOT WORKING: description --\\\>`

### Commit Protocol

Every commit should update this checklist — mark completed tasks as `\\\[✅\\\]`, add verification comments if testing reveals issues, and tag commits with the version number (e.g., v0.9.2).

### Verification Protocol

All `\\\[🔍\\\]` items must be retested before considering a version complete. Add `\\\<!-- VERIFY: description --\\\>` comments for issues found. Do not proceed to next version until all verifications pass.

**Last Updated:** March 6, 2026 (Part 17) | **Maintained By:** Development team + Claude Code

**© 2026 AtMyBoat.com | d3kOS — AI-Powered Marine Electronics** *"Smarter Boating, Simpler Systems"*

