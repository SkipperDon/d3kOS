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

**Verification Comments:** Issues found during testing noted with `\\\\\\\\\\\\\\\<!-- VERIFY: description --\\\\\\\\\\\\\\\>`

## Developer Infrastructure

### Ollama Executor (`deployment/scripts/ollama\\\\\\\\\\\\\\\_execute\\\\\\\\\\\\\\\_v3.py`)

- \[✅\] v2: enclosing-function context extraction, validation, auto-apply

- \[✅\] `helm\\\\\\\\\\\\\\\_os\\\\\\\\\\\\\\\_context.md` injected into every prompt

- \[✅\] Correction loop: flagged blocks sent back with targeted advice (1 retry)

- \[✅\] Parallel execution: `--parallel N` flag

- \[✅\] Fix 1: `ACTION: AFTER/BEFORE` aliases accepted (both executors)

- \[✅\] Fix 2: function parameters recognised as declared in scope (both executors)

- \[✅\] Fix 3: FIND\_LINE prompt rules — no comment lines, no bare `\\\\\\\\\\\\\\\{`/`\\\\\\\\\\\\\\\}`

- \[✅\] Wire RAG retrieval into executor: query `helm\\\\\\\\\\\\\\\_os\\\\\\\\\\\\\\\_source` before each phase

- \[✅\] v3: Generic executor — reads `phases.json`, no per-feature Python edits needed

- \[✅\] Fix 4: END\_LINE support — multi-line block replacement (FIND\_LINE → END\_LINE)

- \[✅\] Fix 5: RAG label changed to "BACKGROUND REFERENCE" — stops Ollama picking FIND\_LINEs from RAG context

- \[✅\] Fix 6: KNOWN\_GLOBALS expanded — Python exceptions (TypeError/ValueError/etc), port/starboard, indent

- \[✅\] Ollama REPLACE\_EXACT mode — Claude provides FIND\_LINE/END\_LINE in phases.json, Ollama writes CODE only

- \[✅\] `--skip-ollama` mode — loads pre-written `.instructions` files (spec code blocks), bypasses model when needed

- \[✅\] `benchmark.py` — 3-test suite, 5-dimension scoring (syntax/keywords/forbidden/variables/similarity), results saved to `benchmark\\\\\\\\\\\\\\\_results.json`

- \[✅\] Model benchmark run: qwen3-coder:30b **97/100** vs deepseek-coder-v2:16b 70/100 — qwen3 is executor default

### Project RAG Knowledge Base (`/home/boatiq/rag-stack/`)

- \[✅\] `helm\\\\\\\\\\\\\\\_os\\\\\\\\\\\\\\\_docs` collection: 1,079 chunks — docs, specs, session history, architecture

- \[✅\] `helm\\\\\\\\\\\\\\\_os\\\\\\\\\\\\\\\_source` collection: 54 chunks — live Pi `.py` + `.html` source files

- \[✅\] `helm\\\\\\\\\\\\\\\_os\\\\\\\\\\\\\\\_ingest.py`: smart filtered ingestion (excludes ATMYBOAT/fish/training noise)

- \[✅\] `ingest.py`: extended to support `.py` and `.html` files

- \[✅\] RAG retrieval wired into both executors — top-4 chunks injected before every Ollama call

- \[🔄\] Re-ingest `helm\\\\\\\\\\\\\\\_os\\\\\\\\\\\\\\\_source` after each Pi deployment — recurring task, not one-time. Command: `cd /home/boatiq/rag-stack && .venv/bin/python3 helm\_os\_ingest.py --collection source`

### Verify Agent (`deployment/scripts/verify\\\\\\\\\\\\\\\_agent.py`)

- \[✅\] `d3kos-verify-agent.service` deployed on TrueNAS VM `192.168.1.103:11436`

- \[✅\] `POST /verify` — receives generated code + instruction, returns `\\\\\\\\\\\\\\\{pass, score, issue, suggestion\\\\\\\\\\\\\\\}`

- \[✅\] `GET /health`, `/report`, `/stats` — monitoring endpoints accessible from laptop

- \[✅\] Inference routed to workstation `qwen3-coder:30b` GPU (TrueNAS CPU too slow — 0.03 t/s even on 1.5b due to bhyve ZFS ARC memory contention)

- \[✅\] `call\\\\\\\\\\\\\\\_verify()` wired into `ollama\\\\\\\\\\\\\\\_execute\\\\\\\\\\\\\\\_v3.py` — both REPLACE\_EXACT and standard modes

- \[✅\] FAIL → `Verify:` issue appended to block, triggers correction loop

- \[✅\] Verifier offline → `None` returned, pipeline continues uninterrupted

- \[✅\] Executor summary report now fetches verify stats from TrueNAS

- \[✅\] `helm\\\\\\\\\\\\\\\_os\\\\\\\\\\\\\\\_context.md` updated — Ollama knows its GENERATOR role and the two-step pipeline

- \[✅\] `deployment/docs/VERIFY\\\\\\\\\\\\\\\_AGENT.md` written — full architecture, endpoints, management commands

- \[✅\] `MEMORY.md` updated with verify agent details

### `helm\\\\\\\\\\\\\\\_os\\\\\\\\\\\\\\\_context.md` (`deployment/docs/`)

- \[✅\] Units.js return types and variable names

- \[✅\] Variable names for all Pi pages (dashboard, navigation, helm, weather, onboarding)

- \[✅\] query\_handler.py class structure and method signatures

- \[✅\] AI services: ports 8097/8099/8107, endpoints, `\\\\\\\\\\\\\\\_query\\\\\\\\\\\\\\\_gemini()` pattern, `ai\\\\\\\\\\\\\\\_used` constraint

- \[✅\] FIND\_LINE / ACTION / CODE format rules and example

### AAO Operating Environment — Claude Code Hardening (2026-03-10)

- \[✅\] DI-001 drift incident documented — Claude touched files outside task scope; /methodology-check, /clear, /compact had no blocking effect

- \[✅\] PreToolUse hook added to `~/.claude/settings.json` — scope audit echo fires before every Write/Edit/MultiEdit/Bash call

- \[✅\] PostToolUse hook updated — ruff lint check after every write

- \[✅\] Stop hook updated — AAO compliance checklist reminder at session end

- \[✅\] Emergency Brake — Hard Stop Protocol added to `/home/boatiq/CLAUDE.md` — phrases STOP / HALT / FREEZE / AAO STOP trigger unconditional halt + file audit + re-authorization

- \[✅\] Emergency Brake section mirrored to `MEMORY.md`

- \[✅\] DI-001 incident record added to top of `SESSION\_LOG.md`

- \[✅\] Clarified: /compact, /clear, /methodology-check are advisory only — brake phrases are the only unconditional stop mechanism

- \[✅\] `/session-close` command updated — now 5-step AAO close: file list, compliance checklist, PROJECT\_CHECKLIST.md update, SESSION\_LOG.md entry, plain-language summary

- \[✅\] `aao-methodology-repo` updated and pushed to GitHub — governing-docs/, config/, remediation/DRIFT\_INCIDENT\_001.md, remediation/EMERGENCY\_BRAKE\_PROTOCOL.md (commit 5e19b73)

- \[✅\] AAO Methodology website deployed to GitHub Pages — 4-page static site (index, install, red-flags, commands) live at https://skipperdon.github.io/AAO-Methodology/ (commit 6c96bc4)

- \[✅\] README.md updated with live site URL — tagline and Status section (commit ce0c56f)

## v0.9.1 — Voice AI Assistant \[Effort: Large\]

**Status:** \[✅\] Complete | **Shipped:** v0.9.1.x (multiple sessions) | **Priority:** HIGH

### Wake Word & Speech Pipeline

- \[✅\] Wake word detection — Vosk with constrained grammar (`\\\\\\\\\\\\\\\["helm"\\\\\\\\\\\\\\\]`)

- \[✅\] TTS responses — Piper (`en\\\\\\\\\\\\\\\_US-hfc\\\\\\\\\\\\\\\_male`) with pre-rendered acknowledgement audio

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

- \[✅\] Conversations logged to SQLite (`ai\\\\\\\\\\\\\\\_used`: online/onboard)

**Deliverable:** d3kOS v0.9.1.x — fully operational hands-free voice AI

## v0.9.2 — Metric/Imperial Conversion System \[Effort: Medium\]

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

  - \[✅\] Add `measurement\\\\\\\\\\\\\\\_system` field to user preferences

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

- Update Boatlog display

  - [ ] 

  - Display entries in user's preferred units

  - [ ] 

  - Stored data remains in imperial (no conversion on storage)

### Voice Assistant & Testing

- \[✅\] Update Voice Assistant (`/opt/d3kos/services/ai/query\\\\\\\\\\\\\\\_handler.py`)

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

  - Test data export (includes unit metadata)

- \[✅\] Accuracy Verification — 25/25 unit tests passing

  - \[✅\] Temperature: 185°F = 85°C (±0.1°C)

  - \[✅\] Pressure: 45 PSI = 3.10 bar (±0.01 bar)

  - \[✅\] Speed: 10 knots = 18.52 km/h (±0.1 km/h)

  - \[✅\] Fuel: 50 gal = 189.3 L (±0.1 L)

  - \[✅\] Performance: \< 1ms conversion time

- [ ] User Acceptance Testing

  - [ ] 

  - Test with 5 metric users

  - [ ] 

  - Test with 5 imperial users

  - [ ] 

  - Collect feedback and iterate

### Deployment

- \[✅\] Git commit — `e3ddbef`

- \[✅\] Tag release as v0.9.2

- Update CHANGELOG.md

- \[✅\] Deploy to production Pi

- \[✅\] Verify all features working on live system

- \[✅\] Update documentation — UNITS\_API\_REFERENCE.md, UNITS\_FEATURE\_README.md

**Deliverable:** d3kOS v0.9.2 with full metric/imperial support

## v0.9.2 — Marine Vision: Camera Overhaul — Slot/Hardware Architecture \[Effort: Large\]

**What this is:** Full replacement of the hardcoded cameras.json system with a dynamic Slot/Hardware architecture supporting 1–20 cameras. Slots are named boat positions (persistent). Hardware is physical cameras (assigned by MAC). Owner manages assignments via Settings UI.

**Status:** \[✅\] Complete — all 5 steps deployed 2026-03-11 | **Priority:** HIGH
**Feature dir:** `deployment/features/camera-overhaul/` | **Build checklist:** `deployment/features/camera-overhaul/BUILD_CHECKLIST.md`
**Spec:** `deployment/docs/MARINE_VISION_CAMERA_OVERHAUL.md`

- \[✅\] Step 1 — migrate_cameras.py: slots.json + hardware.json created, both MACs resolved
- \[✅\] Step 2 — camera_stream_manager.py rewrite: frame buffer, slot/hardware API, discovery scan, backwards compat
- \[✅\] Step 3 — Settings UI: Camera Setup tab (3-panel), slot CRUD, assign/unassign, role toggles, scan
- \[✅\] Step 4 — marine-vision.html rewrite: dynamic tile renderer, focus+filmstrip, staggered polling, fish detection canvas overlay
- \[✅\] Step 5 — fish_detector.py: reads slots.json, per-slot frame fetch, slot_id on captures, /detect/reload endpoint
- \[⚠️\] Touchscreen test Settings UI + Marine Vision (requires Pi touchscreen)
- \[⚠️\] 24hr stability test + performance test — requires cameras (lab cameras will cover this)
- \[✅\] DEPLOYMENT_INDEX.md updated — done 2026-03-11
- [ ] setup_dhcp_reservations.py: one-line update to read hardware.json (deferred — low priority)

**Note on "On-Boat Tasks":** Some tasks are marked as on-boat tasks. These can only be done physically on the boat with cameras connected to the boat's hotspot network (10.42.0.x). They cannot be done from home or over Tailscale.

---

## v0.9.2 — Marine Vision: Live IP Camera System (Bow + Stern) — SUPERSEDED \[Effort: Large\]

> **SUPERSEDED — 2026-03-11 by camera-overhaul.** Retained as history. See section above.

**What this was:** Original two-camera cameras.json system — camera switching, grid view, fish detector.
**Status:** \[✅\] Complete at time of overhaul. Now replaced.

**Note on "On-Boat Tasks":** Some tasks below are marked as on-boat tasks. These can only be done physically on the boat with cameras connected to the boat's hotspot network (10.42.0.x). They cannot be done from home or over Tailscale.

**Hardware:** 2 cameras active, 2 more planned:

- Camera 1 (bow, 10.42.0.100) — connected, live

- Camera 2 (stern, 10.42.0.63) — Reolink RLC-820A — connected, live

- Camera 3 & 4 — Reolink RLC-820A × 2 (planned purchase) — when purchased, add to `cameras.json` — no code changes needed

**Commit:** `be236c5`

### Camera Registry System

- \[✅\] Create camera configuration schema

  - \[✅\] `/opt/d3kos/config/cameras.json` deployed (id, name, location, ip, rtsp\_url, model, detection\_enabled)

- \[⚠️\] Configure DHCP reservations — ON-BOAT TASK

  - \[✅\] `setup\\\\\\\_dhcp\\\\\\\_reservations.py` deployed to `/home/d3kos/` on Pi

  - \[⚠️\] Run `sudo python3 ~/setup\\\\\\\_dhcp\\\\\\\_reservations.py` once when cameras are connected to hotspot — auto-reads MAC addresses from lease file + writes dnsmasq.conf + restarts dnsmasq

- \[🔄\] Test camera connectivity

  - \[✅\] Bow camera connects (10.42.0.100, RTSP working)

  - \[✅\] Stern RLC-820A (10.42.0.63) — RTSP connected (`d3kos2026$`, stored percent-encoded)

### Multi-Camera Backend API

- \[✅\] Extend Camera Stream Manager (per-camera frame-grabber threads, graceful offline handling)

- \[✅\] Create new API endpoints (Port 8084)

  - \[✅\] GET `/camera/list` — all cameras + status

  - \[✅\] POST `/camera/switch/\\\\\\\\\\\\\\\<id\\\\\\\\\\\\\\\>` — switch active camera

  - \[✅\] GET `/camera/grid` — side-by-side JPEG of all cameras

  - \[✅\] GET `/camera/frame/\\\\\\\\\\\\\\\<id\\\\\\\\\\\\\\\>` — frame from specific camera

- \[✅\] Backwards-compatible endpoints: `/camera/status`, `/camera/frame`, `/camera/record/\\\\\\\\\\\\\\\*`, `/camera/capture`

- \[✅\] All endpoints tested with curl — both cameras live

- [ ] 24-hour stability test (once both cameras connected)

### UI Implementation

- \[✅\] Update `/marine-vision.html`:

  - \[✅\] Camera selector buttons (Bow Camera / Stern Camera) — switches without page reload

  - \[✅\] Grid View toggle button — side-by-side via `/camera/grid`

  - \[✅\] Feed label shows active camera name

  - \[✅\] All-cameras status cards (shows connection state per camera)

- \[✅\] `settings.html` camera section — dynamic multi-camera display via `/camera/list`

  - \[✅\] Replaces hardcoded Camera 1 UI with live camera cards per camera

  - \[✅\] "Set Active" button per camera (calls `/camera/switch/\\\\\\\\\\\\\\\<id\\\\\\\\\\\\\\\>`)

  - \[✅\] "Open Marine Vision" button

  - \[✅\] Deployed to Pi — commit `9e53dfa`

- \[✅\] Camera position assignment (bow/stern/port/starboard per camera)

  - \[✅\] Spec written: `deployment/features/camera-position-assignment/feature\\\\\\\\\\\\\\\_spec.md`

  - \[✅\] API spec: `POST /camera/assign` with bow/stern/port/starboard positions

  - \[✅\] UI spec: assign buttons on each settings.html camera card

  - \[✅\] marine-vision.html spec: direction labels (Bow/Stern/Port/Starboard) instead of names

  - \[✅\] Applied via `--skip-ollama` with spec code blocks as instructions files

  - \[✅\] `/camera/list` returns `position` field for each camera

  - \[✅\] cameras.json updated with `position: bow/stern`, ownership fixed to d3kos

  - \[✅\] Deployed to Pi — commit `dbff06e`

  - \[✅\] settings.html HTML false-positive artifacts manually fixed (2026-03-06): duplicate `camera-cards-container` section removed, misplaced Data Management button removed, octal `047` artifacts → proper single quotes

- [ ] DHCP / static IP confirmation (cameras should stay on same IPs)

- [ ] Test UI on touchscreen + mobile

### Testing & Optimization

- [ ] Performance testing

  - [ ] Measure CPU usage (target: \< 35%)

  - [ ] Measure memory usage (target: \< 970 MB total)

  - [ ] Measure bandwidth (grid: \< 12 Mbps, single: \< 4 Mbps)

  - [ ] Test with both cameras for 24 hours continuous

- [ ] Resource optimization

  - [ ] Tune frame rates if needed

  - [ ] Optimize detection frequency

  - [ ] Add frame dropping if overloaded

- [ ] Storage management

  - [ ] Implement motion-triggered recording

  - [ ] Set 7-day retention policy

  - [ ] Add automatic cleanup (old recordings)

  - [ ] Verify storage usage (target: \< 28 GB for 7 days)

- [ ] Integration testing

  - [ ] Test camera switching in all scenarios

  - [ ] Test grid view performance

  - [ ] Test Forward Watch with real obstacles

  - [ ] Test with weak network conditions

- [ ] Bug fixes

  - [ ] Fix any issues found in testing

  - [ ] Retest after fixes

### Documentation & Deployment

- [ ] Update documentation

  - [ ] User guide for Marine Vision camera system

  - [ ] Setup instructions for additional cameras

  - [ ] Troubleshooting guide

  - [ ] API documentation updates

- [ ] Hardware setup

  - \[✅\] Camera 1 — Bow camera (10.42.0.100) — on network, RTSP working

  - \[✅\] Camera 2 — Reolink RLC-820A (10.42.0.63) — on network

  - \[✅\] RLC-820A password confirmed (`d3kos2026$`), `cameras.json` updated, service restarted

  - [ ] Decide on mounting location for RLC-820A (stern confirmed in registry — verify physical mount)

  - \[✅\] Both cameras verified accessible via RTSP

- \[✅\] Deployment — core deployed, commits `be236c5`, `9478f1d`

  - \[✅\] `cameras.json` → `/opt/d3kos/config/`

  - \[✅\] `camera\\\\\\\\\\\\\\\_stream\\\\\\\\\\\\\\\_manager.py` → `/opt/d3kos/services/marine-vision/`

  - \[✅\] `marine-vision.html` → `/var/www/html/`

  - \[✅\] Service restarted, bow camera live

  - \[✅\] Both cameras live — bow (10.42.0.100) + stern RLC-820A (10.42.0.63)

- [ ] User training

  - [ ] Create video tutorial

  - [ ] Write quick start guide

  - [ ] Train user on camera switching and grid view

**Deliverable:** d3kOS v0.9.2 — Marine Vision live with bow + stern cameras. Now superseded by camera-overhaul. Cameras 3 & 4: add via Settings → Camera Setup → Scan + Assign. No code changes needed — overhaul supports up to 20 cameras via UI.

**Also fixed this session:**

- \[✅\] nginx: all 18 service proxies restored (wiped during Part 5 nginx corruption fix)

- \[✅\] Fish detector: restarted after dependency failure (camera stream was down Feb 28) — YOLOv8n + 483 species active

## v0.9.2— Gemini API Integration \[Effort: Small\]

**Status:** \[✅\] Complete | **Shipped:** v0.9.4 (commit `02d2694`) | **Priority:** MEDIUM

### Tasks

- \[✅\] Backend Gemini proxy service (Port 8097 — `d3kos-gemini-proxy.service`)

- \[✅\] Settings UI: API key input, model selector, Save + Test Connection

- \[✅\] `query\\\\\\\\\\\\\\\_handler.py`: `\\\\\\\\\\\\\\\_query\\\\\\\\\\\\\\\_gemini()` method + routing (Gemini → RAG fallback)

- \[✅\] `GEMINI\\\\\\\\\\\\\\\_SETUP.md` setup guide with step-by-step API key instructions

- \[✅\] End-to-end tested: "what causes white smoke from marine exhaust" → Gemini 8s ✓

- \[✅\] Onboarding wizard integration (Steps 17.x) — deployed in Post-Install Fix \#9 (Part 12): Step 17 "AI Assistant Setup" added to onboarding.html with API key input, Test Connection button, skip option

**Note:** Port 8099 was occupied by `issue\\\\\\\\\\\\\\\_detector.py` — Gemini proxy uses port 8097.

**Deliverable:** d3kOS v0.9.4 with conversational AI via Gemini 2.5 Flash

## v0.9.2 — Remote Access API \[Effort: Small\]

**Status:** \[✅\] Phase 1 Complete | **Shipped:** v0.9.5 | **Priority:** HIGH

### Tasks

- \[✅\] `remote\\\\\\\\\\\\\\\_api.py` — Flask service on port 8111 with API key auth

- \[✅\] `GET /remote/health` — unauthenticated health check

- \[✅\] `GET /remote/status` — all boat metrics from SignalK (engine, nav, systems)

- \[✅\] `GET /remote/maintenance` — last 20 maintenance log entries

- \[✅\] `POST /remote/note` — add maintenance note from phone

- \[✅\] Systemd service `d3kos-remote-api.service` (enabled, active)

- \[✅\] Nginx proxy `/remote/` → `localhost:8111`

- \[✅\] API key generated and stored in `api-keys.json`

- \[✅\] `REMOTE\\\\\\\\\\\\\\\_ACCESS\\\\\\\\\\\\\\\_SETUP.md` with Tailscale + LAN + port-forward options

- \[✅\] Tailscale install on Pi — connected, IP: `100.88.112.63` (networkdon89@ account)

- [ ] Camera stream relay RTSP → HLS (implement when cameras 3 & 4 purchased)

- [ ] WebSocket real-time push — implement push notifications instead of polling `/remote/status`

- \[✅\] **"My Remote Access" settings page** (`remote-access.html`) — commit `06a6a94`

  - \[✅\] Display Tailscale IP (fetched live from `/remote/config`)

  - \[✅\] Display API key (masked by default, tap to reveal, copy button)

  - \[✅\] Generate QR code linking to `http://100.88.112.63` — scan with phone camera, no typing

  - \[✅\] 4-step connection instructions

  - \[✅\] Fallback: shows local IP QR + warning when Tailscale is off

  - \[✅\] Button added to Settings page

**Deliverable:** d3kOS v0.9.5 — Remote status readable from phone anywhere via Tailscale

## v1.1 — Multi-Language Platform \[Effort: Very Large\]

**Status:** \[🔄\] Layer 0 (UI foundation) partially done — Layers 1–5 (voice, AI, keyboard) not started **Priority:** REQUIRED for v1.1 **Full spec:** `doc/MULTILANGUAGE\_PLATFORM\_SPEC.md` | `deployment/v1.1/`

> Multi-language is not UI translation. It is a 6-layer platform stack covering speech input, speech output, AI response language, keyboard/text input, boat log recording, and UI display. All layers must work together for a captain to fully operate d3kOS in their own language.


### Layer 0 — UI Foundation (Translation JSON + Display)

**Status:** \[🔄\] Partial — 6 of 20 pages wired, 14 remaining

- \[✅\] 18 JSON translation files deployed at `/opt/d3kos/config/i18n/`

- \[✅\] Language API live on port 8101 — GET/POST `/api/language`, GET `/api/i18n/\<code\>`, GET `/api/languages`

- \[✅\] `language-menu.html` — 18-language touch-optimised selector

- \[✅\] Globe button on `index.html`

- \[✅\] Language tile in `settings.html`

- \[✅\] Language overlay on `onboarding.html`

- \[✅\] `data-i18n` wired: `index.html`, `dashboard.html`, `navigation.html`, `boatlog.html`, `settings.html`, `onboarding.html`

- [ ] Wire 14 remaining pages: `weather.html`, `marine-vision.html`, `helm.html`, `ai-assistant.html`, `charts.html`, `manuals.html`, `manual-search.html`, `history.html`, `settings-network.html`, `settings-data.html`, `settings-healing.html`, `settings-simulator.html`, `remote-access.html`, `upload-manual.html`

- [ ] Expand translation keys in all 18 JSON files to cover new pages

- [ ] Noto fonts installed on Pi for Arabic, CJK, Greek, Cyrillic: `sudo apt install fonts-noto fonts-noto-cjk fonts-noto-extra`

- [ ] Arabic RTL: `document.documentElement.dir` set on all pages when `lang=ar`

- [ ] Professional translation review: French, Spanish, German, Italian, Dutch, Swedish, Norwegian (marine terminology)

- [ ] Native speaker QA testing


### Layer 1 — Speech-to-Text (Voice Input in Any Language)

**Status:** \[ \] Not Started **Files:** `voice-assistant-hybrid.py` (listen()), `boatlog-export-api.py` (transcribe\_audio()), new `whisper\_transcribe.py`

**What it does:** A French captain says "Helm, quel est mon régime moteur?" — the spoken command after the wake word is transcribed in French, not forced through an English model.

- [ ] Deploy `whisper-small` model (244MB, 99 languages) to Pi at `/opt/d3kos/models/whisper/`

- [ ] Create `whisper\_transcribe.py` helper — loads model once, reads `language` from `onboarding.json`, exposes `transcribe(wav\_path) -\> str`

- [ ] Replace Vosk transcription in `voice-assistant-hybrid.py` `listen()` — keep Vosk for wake-word detection only, switch to Whisper for post-wake command transcription

- [ ] Replace Vosk transcription in `boatlog-export-api.py` `transcribe\_audio()` with Whisper

- [ ] Performance test: whisper-small on Pi 4B — target \< 6s per transcription

- [ ] Test: French, German, Spanish voice commands correctly transcribed

- [ ] Test: Arabic voice note transcribed correctly


### Layer 2 — Text-to-Speech (Voice Output in Any Language)

**Status:** \[ \] Not Started **Files:** `voice-assistant-hybrid.py` (TTS calls), new per-language Piper model files

**What it does:** Helm speaks back to the captain in their language, not always English.

- [ ] Map language codes to Piper model names (fr, de, es, it, nl, pt, uk, ar have official Piper models)

- [ ] Download and deploy Piper `.onnx` models for: French, German, Spanish, Italian, Dutch, Portuguese, Ukrainian, Arabic (~60–200MB each, ~1.5GB total)

- [ ] For languages without Piper models (fi, sv, no, da, hr, tr, el, zh, ja): configure `espeak-ng` fallback voices

- [ ] Update `voice-assistant-hybrid.py` to read `language` from `onboarding.json` on startup and select correct TTS model/voice

- [ ] Create `tts\_speak(text, language)` abstraction — routes to Piper or espeak-ng based on language

- [ ] Test: French response spoken in French voice

- [ ] Test: Arabic response spoken correctly (rtl text still spoken ltr by Piper)

- [ ] Test: Finnish/Norwegian fallback via espeak-ng is intelligible


### Layer 3 — AI Response Language

**Status:** \[ \] Not Started **Files:** `query\_handler.py`

**What it does:** Gemini, RAG, and all rule-based engine responses come back in the captain's language — not English.

- [ ] Read `language` from `/opt/d3kos/config/onboarding.json` on `query\_handler.py` startup

- [ ] Inject language instruction into all Gemini system prompts: `"The user speaks \[language\]. Always respond in \[language\]. Use correct marine terminology for \[language\]."`

- [ ] Replace hardcoded English strings in rule-based responses (RPM, temperature, oil, fuel, speed) with values pulled from i18n JSON files

- [ ] RAG responses: Gemini translates the English retrieved chunks into the user's language before replying

- [ ] Test: "what is my engine temperature" asked in French → French response

- [ ] Test: rule-based "Your RPM is 2400" rendered in Spanish

- [ ] Test: RAG marine manual answer returned in Italian

- [ ] Language quality caveat documented for minor languages (Croatian, Ukrainian, Finnish)


### Layer 4 — Keyboard and Text Input

**Status:** \[ \] Not Started — existing keyboard bug must be fixed first **Dependency:** Resolve open keyboard investigation (`memory/keyboard-scroll-investigation.md`) before starting

**What it does:** A captain can type a boat log entry, chat with Helm, or search manuals in their own language.

#### Latin-script languages (fr, de, es, it, nl, sv, no, da, fi, pt, hr, tr, uk)

- [ ] Fix existing English on-screen keyboard bug (pre-condition)

- [ ] Implement per-language virtual keyboard layouts (AZERTY, QWERTZ, accented characters: é, ü, ø, ç, ğ, і, etc.)

- [ ] Switch keyboard layout automatically based on `onboarding.json` language

#### Arabic (RTL)

- [ ] Install `fcitx5` on Pi with Arabic keyboard layout

- [ ] Configure labwc/Wayland to use fcitx5 as input method

- [ ] Set `dir="rtl"` and `lang="ar"` on all text input fields when Arabic active

- [ ] Cursor starts right, text flows right-to-left in all input fields

- [ ] Test: Arabic entry in boatlog stores and displays correctly

#### CJK — Chinese and Japanese (separate milestone, not v1.0)

- [ ] `fcitx5` + `fcitx5-chinese-addons` (Pinyin → Hanzi) for Chinese

- [ ] `fcitx5` + `fcitx5-mozc` (Romaji/Kana → Kanji) for Japanese

- [ ] Voice input (Layer 1) is the practical path for CJK on a touchscreen boat helm


### Layer 5 — Boat Log in the User's Language

**Status:** \[ \] Not Started — automatic once Layers 1 and 4 are complete **Files:** `boatlog-export-api.py`, `boatlog.html`

**What it does:** A captain records and reads their log entirely in their own language.

- [ ] Voice notes: transcribed by Whisper in user's language (Layer 1 dependency)

- [ ] Text entries: typed in user's language with correct keyboard (Layer 4 dependency)

- [ ] Noto fonts rendering all languages in `boatlog.html` display (Layer 0 dependency)

- [ ] CSV/JSON export: UTF-8 already — no code changes needed

- [ ] Test: French captain speaks a voice note → stored and displayed in French

- [ ] Test: German captain types a log entry in German → stored and displayed correctly

- [ ] Test: Arabic entry stored and displayed RTL


### Supported Languages

| Code | Language | Piper TTS | Whisper STT | Keyboard |
| - | - | - | - | - |
| en | English | ✅ Deployed | ✅ | ✅ |
| fr | French | Piper model needed | Whisper-small | Latin layout |
| de | German | Piper model needed | Whisper-small | QWERTZ layout |
| es | Spanish | Piper model needed | Whisper-small | Latin layout |
| it | Italian | Piper model needed | Whisper-small | Latin layout |
| nl | Dutch | Piper model needed | Whisper-small | Latin layout |
| pt | Portuguese | Piper model needed | Whisper-small | Latin layout |
| uk | Ukrainian | Piper model needed | Whisper-small | Cyrillic layout |
| ar | Arabic | Piper model needed | Whisper-small | fcitx5 RTL |
| sv | Swedish | espeak-ng fallback | Whisper-small | Latin layout |
| no | Norwegian | espeak-ng fallback | Whisper-small | Latin layout |
| da | Danish | espeak-ng fallback | Whisper-small | Latin layout |
| fi | Finnish | espeak-ng fallback | Whisper-small | Latin layout |
| hr | Croatian | espeak-ng fallback | Whisper-small | Latin layout |
| tr | Turkish | espeak-ng fallback | Whisper-small | Latin layout |
| el | Greek | espeak-ng fallback | Whisper-small | Greek layout |
| zh | Chinese | espeak-ng fallback | Whisper-small | fcitx5 (v1.1+) |
| ja | Japanese | espeak-ng fallback | Whisper-small | fcitx5 (v1.1+) |



### Delivery Order (dependencies)

1. Layer 1 (Whisper STT) — blocks all voice testing in any language

2. Layer 2 (Piper/espeak TTS) — parallel with Layer 1

3. Layer 3 (AI response language) — testable once Layer 1 works

4. Layer 0 (wire remaining 14 pages) — parallel, no dependency on voice

5. Layer 4 (keyboard) — fix existing bug first, then add layouts

6. Layer 5 (boat log) — automatic once Layers 1 and 4 are done

**Minimum viable multilingual** (captain can speak, hear, and write in their language): Layers 1 + 2 + 3 + 5

**Deliverable:** d3kOS v1.0 — full 18-language platform. A captain operates the system entirely in their own language: voice commands, voice responses, AI answers, boat log, and UI.

## signalk-forward-watch — Standalone Signal K Community Plugin

**Status:** \[✅\] v0.2.0 Published to GitHub + npm | **Priority:** HIGH | **Repo:** [https://github.com/SkipperDon/signalk-forward-watch](https://github.com/SkipperDon/signalk-forward-watch) | **npm:** signalk-forward-watch | **Project dir:** `/home/boatiq/signalk-forward-watch/`

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

- \[✅\] `plugin/detector.js` — rewritten as worker wrapper (v0.2.0)

- \[✅\] `plugin/detector-worker.js` — NEW v0.2.0. onnxruntime isolated in worker thread; SK main heap unaffected

- \[✅\] `plugin/gps-calculator.js`

- \[✅\] `plugin/signalk-output.js`

- \[✅\] `plugin/opencpn-output.js` — detections appear as AIS targets in OpenCPN

### Deployment & Publishing

- \[✅\] Deployed and confirmed working on d3kOS Pi

- \[✅\] Published to GitHub — v0.1.0, v0.2.0 (2026-03-11)

- \[✅\] README with full field reference, install instructions, OpenCPN section

- \[✅\] Announced on Signal K Discord

- \[✅\] Announced on OpenMarine forum

- \[ \] Test on OpenPlotter

- \[✅\] `npm publish` — v0.2.0 published 2026-03-11. Granular access token required (OTP alone insufficient when account has publish 2FA policy)

- \[ \] Add download-on-first-run (auto-fetch model from GitHub Releases)

**Deliverable:** `signalk-forward-watch` on npm / Signal K AppStore

## v0.9.2 — Community Features \[Effort: Small\]

**Status:** \[✅\] Pi-side deployed 2026-03-07 (Part 18) | flows currently disabled until atmyboat.com backend exists (v0.9.3) | **Priority:** MEDIUM

**What was deployed to Pi (Part 18):**

- \[✅\] `anonymiser.py` — anon\_token (HMAC-SHA256), strip\_position (2dp ~1.1km grid), strip\_vessel\_name

- \[✅\] `community-api.py` — Flask port 8103, POST /api/community/marker, GET /api/community/markers, prefs gating

- \[✅\] `d3kos-community-api.service` — created, enabled, running on Pi

- \[✅\] `community-prefs.json` — created on Pi, all features off by default

- \[✅\] `settings.html` — Community & Privacy section with 4 opt-in toggles (Tier 1 gate shown, toggles disabled for T0)

- \[✅\] `helm.html` — hazard/POI floating button + bottom sheet modal + submitHazardReport()

- \[✅\] 3 Node-RED flows deployed (UUIDs remapped to avoid collisions): engine-benchmark (600s), boat-map (3600s), knowledge-log (file watch)

**Current state:** Flows disabled in Node-RED UI — all 3 were making HTTP calls to atmyboat.com endpoints that don't exist yet. Was causing Node-RED 93% CPU. Re-enable when v0.9.3 backend is live.

**What remains:**

- \[ \] Re-enable flows when atmyboat.com community API endpoints are live (v0.9.3)

- \[ \] End-to-end test: toggle on → data flows to atmyboat.com → appears on community map

**Deliverable:** Full end-to-end when atmyboat.com backend (v0.9.3) is live. Pi-side is complete.

## v0.9.2 — Post-Install Bug Fixes & UI Polish \[Effort: Medium\]

**Status:** \[✅\] Complete (deployed 2026-03-05, Part 12 — all 14 fixes via Ollama executor) | **Priority:** CRITICAL — Blocking demo quality | **Spec:** `deployment/features/post-install-fixes/OLLAMA\\\\\\\_SPEC.md`

> These issues were identified during first full boot and functional test of v0.9.5. All items to be implemented by Ollama workstation. Claude is planner/reviewer only.

### 1. Dashboard — SignalK Disconnected Banner

- ✅ Detect SignalK connection status on page load (poll `/signalk/v1/api/` on port 3000)

- ✅Show yellow banner when disconnected: "⚠️ Signal K is offline — Go to Settings → System Actions to restart"

- ✅ Banner includes tap-to-navigate button → `settings.html\\\\\\\#system-actions`

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

- \[✅\] Add `After=d3kos-tier-api.service` to `d3kos-export-daily.service` unit file

- \[✅\] **Root cause fixed 2026-03-11:** `d3kos-export-boot.service` was FAILED since 2026-03-04. Previous retry loop fix was insufficient — `set -e` + `curl` exit code 7 (CURLE_COULDNT_CONNECT) killed the script before the retry ran. `systemctl is-active` returns active as soon as the process starts but Flask doesn't bind port 8094 for ~2s. Fixed in `export-on-boot.sh`: removed `set -e`; replaced `is-active` check with `nc -z localhost 8094` port-ready loop (10 × 3s, 30s max); wrapped `curl` and `jq` with `|| echo` fallbacks. Tested: `status=0/SUCCESS`.

### 4. Navigation — GPS Readings Not Showing

- ✅Verify SignalK `gps` and `ais` pipedProviders are enabled (fixed 2026-03-04 — verify persists after redeploy)

- ✅ Confirm navigation.html reads from correct SignalK paths: `navigation/position`, `navigation/speedOverGround`, `navigation/headingTrue`, `navigation/courseOverGroundTrue`

- ✅Fix any broken SignalK data paths on navigation page

- ✅Verify depth, speed, COG, SOG all display when GPS has a fix

- ✅Add "No GPS fix" indicator when `mode \\\\\\\< 2` (instead of blank fields)

### 5. Boatlog — Voice Note & Export

- \[✅\] **Voice Note**: Add microphone button to boatlog.html that records a voice note using browser MediaRecorder API → uploads to `/boatlog/voice-note` endpoint

- \[✅\] **Voice Note API**: Add `POST /boatlog/voice-note` to `boatlog-api.py` — saves WAV to `/opt/d3kos/data/boatlog-audio/` with timestamp filename, transcribes via Vosk, stores text in boatlog entry

- \[✅\] **Export**: Verify boatlog export endpoint works end-to-end (CSV + JSON)

- \[✅\] **Export button**: Confirm boatlog.html export button calls correct API and downloads file

- \[✅\] recordVoiceNote() replaced — real MediaRecorder implementation deployed 2026-03-06 (verify agent corrected Ollama placeholder regeneration)

- \[🔍\] Test voice note record → transcribe → save → view cycle on Pi at dock

### 6. Weather — GPS Centering & Wind/Clouds Overlay

- \[✅\] **Root cause**: `weather.html` has hardcoded fallback `\\\\\\\{ lat: 44.4167, lon: -79.3333 \\\\\\\}` (Lake Simcoe). Map initialises with this before GPS resolves.

- \[✅\] **Fix**: On page load, fetch GPS position from SignalK (`/signalk/v1/api/vessels/self/navigation/position`) before initialising map. Show loading state.

- \[✅\] If SignalK returns no position (no fix), fallback to Lake Simcoe with a visible "No GPS — using default location" label

- \[✅\] **Wind/Clouds overlay**: Debug why wind and cloud layers are not rendering. Check OpenWeatherMap API key is configured. Check tile URL format and layer names.

- \[✅\] Verify `recenter` button recenters to live GPS position, not hardcoded fallback

- \[✅\] Test with GPS active: map must open centred on actual vessel position

### 7. Marine Vision — Camera Errors & Fish Detector

- \[✅\] **Stern camera**: Debug why stern camera (10.42.0.63) shows error. Cameras are on 10.42.0.x (boat hotspot network — not available at home). Add graceful offline message: "Camera offline — not on boat network" instead of error.

- \[✅\] **Bow camera**: Same graceful offline handling for 10.42.0.100

- \[✅\] **Fish detector**: Verify `fish\\\\\\\_detector.py` handles camera-offline state without crashing. Add health check that returns `offline` state cleanly.

- \[✅\] **UI**: onerror handler deployed — shows "No camera feed available" + hides broken image (marine-vision.html line 492)

- \[✅\] **Fish detector API**: Ensure `/fish/status` returns `\\\\\\\{ "status": "offline", "reason": "camera unavailable" \\\\\\\}` not an error when camera not reachable

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

- \[✅\] Touchscreen touch and pinch-zoom confirmed working in Flatpak OpenCPN — twofing patched for Wayland XInput fallback, ILITEK touchscreen symlinked via udev rule to `/dev/twofingtouch`, autostarted in labwc before OpenCPN

- \[ \] o-charts chart activation — Don's manual task: open OpenCPN → Options → Plugins → O-Charts → Preferences → Log in with o-charts.org account → download charts. Alternative: fingerprint file `oc03L\\\_1772818229.fpr` at `C:\\Users\\donmo\\Downloads\\` for web registration at o-charts.org → My Charts → Assign Device. See `deployment/docs/OPENCPN\_FLATPAK\_OCHARTS.md`

### 9. Boat Setup Wizard — Gemini API Configuration Step

- \[✅\] Gemini API key configuration added to onboarding wizard (Step 17)

- ✅Add Step 17 to `onboarding.html`: "AI Assistant Setup"

  - ✅Input field: Gemini API key (optional — skip button available)

  - ✅Test Connection button → calls `/gemini/test` endpoint

  - ✅On success: green tick + "AI Assistant ready"

  - ✅ On skip: note that AI can be configured later in Settings

  - ✅ Saves key to gemini config on `POST /gemini/config`

- ✅ Ensure step is skippable (boat works fully without Gemini key)

### 10. AI Assistant — RAG Precision Improvement

- \[✅\] **Embedding re-ingest**: Re-ingest `helm\\\\\\\_os\\\\\\\_source` collection after this deployment (`helm\\\\\\\_os\\\\\\\_ingest.py --collection source`) to keep source current

- \[✅\] **Query precision**: In `query\\\\\\\_handler.py`, increase `n\\\\\\\_results` from 4 to 6 for RAG retrieval on technical questions

- \[✅\] **Score threshold**: Filter RAG results with cosine distance \< 0.4 (discard weak matches that add noise)

- \[✅\] **Context window**: When RAG results are used, include the collection name + chunk source file in the prompt context so Ollama knows where information came from

- \[✅\] **Hybrid routing confirmed**: `k=6` + distance filter (`\\\< 0.4`) confirmed in `query\\\\\\\_handler.py` line 232-236 on Pi

### 11. System Boot — Keyring Auto-Unlock

- **✅Assessment**: gnome-keyring runs on boot (`/usr/bin/gnome-keyring-daemon`), prompts for password. On a dedicated marine device this is unacceptable.

- **✅Solution A — Empty password keyring** (recommended for dedicated device):

  - ✅Set keyring password to empty string via `seahorse` or `secret-tool`

  - ✅ Configure PAM to auto-unlock keyring on auto-login: add `auth optional pam\\\\\\\_gnome\\\\\\\_keyring.so` to `/etc/pam.d/lightdm-autologin`

- ✅ Test: reboot → desktop appears without any password prompt → d3kOS UI launches automatically

- ✅Ensure SSH still requires password (security boundary)

### 12. Settings — Measurement System Section Formatting

- \[✅\] **Root cause**: `settings.html` line 627 uses `\\\\\\\<h2\\\\\\\>Measurement System\\\\\\\</h2\\\\\\\>` without `class="section-header"` and without an emoji icon

- \[✅\] **Fix**: Change to `\\\\\\\<h2 class="section-header"\\\\\\\>📏 Measurement System\\\\\\\</h2\\\\\\\>` to match all other sections

- \[✅\] Also check lines 691+ for `\\\\\\\<h2\\\\\\\>🤖 AI Assistant — Gemini API\\\\\\\</h2\\\\\\\>` — apply same class if missing

- \[✅\] Visual test: confirm Measurement System heading matches Engine Configuration, Units & Display, etc.

### 13. Settings — System Actions Actually Work

- \[✅\] **Root cause**: `restartsignalk()`, `restartNodered()`, `rebootSystem()` at lines 1019-1034 only show `alert()` with SSH instructions — they do nothing

- \[✅\] **Create Settings Action API** (`d3kos-settings-api.py`, port 8101):

  - \[✅\] `POST /settings/restart-signalk` → `subprocess.run(\\\\\\\['sudo', 'systemctl', 'restart', 'signalk'\\\\\\\])`

  - \[✅\] `POST /settings/restart-nodered` → `subprocess.run(\\\\\\\['sudo', 'systemctl', 'restart', 'nodered'\\\\\\\])`

  - \[✅\] `POST /settings/reboot` → `subprocess.run(\\\\\\\['sudo', 'reboot'\\\\\\\])`

  - \[✅\] `POST /settings/initial-setup-reset` → call existing reset logic

  - \[✅\] All endpoints return `\\\\\\\{ "success": true, "message": "..." \\\\\\\}`

  - \[✅\] Add sudoers rule: `d3kos ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart signalk, /usr/bin/systemctl restart nodered, /usr/bin/reboot`

- \[✅\] **Update settings.html**: Replace all `alert()` calls with `fetch('/settings/restart-signalk', \\\\\\\{method:'POST'\\\\\\\})` calls

- \[✅\] **Confirm with user before reboot**: reboot action shows confirmation dialog first

- \[✅\] Add nginx proxy `/settings/action/` → `localhost:8101`

- \[✅\] Create systemd service `d3kos-settings-api.service`, enable, deploy

### 14. All Pages — Scrollbar Size (Touch-Friendly)

- \[✅\] **Root cause**: All pages with right-side scrollbars use default browser scrollbar (~8-12px wide) — impossible to grab accurately on touchscreen

- \[✅\] **Fix**: Add global CSS rule to ALL html pages (or shared CSS file): scrollbar must be minimum 5× current size (~50-60px wide) with high-contrast track and thumb

- \[✅\] Apply to: `dashboard.html`, `navigation.html`, `weather.html`, `marine-vision.html`, `boatlog.html`, `settings.html`, `onboarding.html`, and any other pages with scrollable content (56px scrollbars deployed to all 26 pages)

- \[✅\] CSS added: `::-webkit-scrollbar \\\{ width: 56px \\\}` + track/thumb/active rules on all pages

- \[✅\] Also created shared `d3kos-touch.css` (2026-03-06) with touch-action, tap-highlight, and overscroll rules

- \[✅\] Chromium pinch/multitouch flags deployed (2026-03-06): `--enable-pinch --pull-to-refresh=1 --enable-features=TouchpadAndWheelScrollLatching,AsyncWheelEvents` added to `/home/d3kos/.config/autostart/d3kos-browser.desktop`

- \[✅\] Test on touchscreen: scrollbar must be easy to grab and drag with a finger

**Deliverable:** All 14 items resolved. d3kOS fully functional on first boot with no SSH required for any operation.

**Spec for Ollama:** `deployment/features/post-install-fixes/OLLAMA\\\\\\\_SPEC.md`


## v0.9.2 — Cloud Integration Pre-Requisites (Pi Side) \[Effort: Medium\]

**Status:** \[✅\] Complete (deployed 2026-03-06) | **Priority:** CRITICAL — Must complete before v0.9.3 website build **Spec:** `deployment/v0.9.3/ATMYBOAT\_CLAUDE\_CODE\_SPEC.md` — PART 14

> Pi-side changes only. v0.9.2 closes completely before v0.9.3 starts.

### 1. QR Code URL Update

- \[✅\] Update onboarding wizard QR to encode: `https://atmyboat.com/register?device=\[INSTALLATION\_ID\]&tier=t0&version=\[FIRMWARE\]`

- \[✅\] Confirm `INSTALLATION\_ID` generated on first boot and persisted to `/opt/d3kos/config/device.json`

### 2. Registration Handshake Endpoint (Port 8091)

- \[✅\] New Flask service `cloud-link-api.py` at `/opt/d3kos/services/cloud/cloud-link-api.py`

- \[✅\] `POST /api/link` — receives `\{boat\_uuid, device\_api\_key, supabase\_url\}` from website, writes `cloud-credentials.json`

- \[✅\] `GET /api/status` — returns `\{tier, firmware\_version, uptime, last\_push\}`

- \[✅\] Systemd service `d3kos-cloud-link.service` on port 8092 (8091 taken by license-api), nginx proxy `/cloud/` → `localhost:8091`

### 3. cloud-credentials.json

- \[✅\] New file `/opt/d3kos/config/cloud-credentials.json` — T1+ only, not created on T0 (offline by design)

- \[✅\] Schema: `\{boat\_uuid, device\_api\_key, supabase\_url, supabase\_anon\_key, webhook\_url, tier\}`

- \[✅\] `chmod 600` — API key file, readable by d3kos user only

- \[✅\] Added to `.gitignore`

### 4. Node-RED Telemetry Push Flow

- \[✅\] New Node-RED flow `d3kOS-cloud-telemetry-push`

- \[✅\] Checks for `cloud-credentials.json` on startup — absent = flow inactive (T0 safe)

- \[✅\] `POST https://atmyboat.com/api/telemetry/push` every 60 seconds, `Authorization: Bearer \[device\_api\_key\]`

- \[✅\] Payload: RPM, coolant temp, fuel level, battery volts, GPS lat/lon/speed, firmware version, uptime

- \[✅\] SQLite offline buffer (JSONL append at telemetry-buffer.jsonl) `/opt/d3kos/data/telemetry-buffer.db` — queues offline, flushes on reconnect

### 5. Alarm Webhook Flow

- \[✅\] New Node-RED flow `d3kOS-alarm-webhook`

- \[✅\] Fires on WARNING or CRITICAL engine/system alerts

- \[✅\] `POST https://atmyboat.com/api/notify` with `device\_api\_key` auth

- \[✅\] Payload: `\{alert\_type, severity, value, threshold, timestamp\}`

- \[✅\] Only active when `cloud-credentials.json` exists (T0 safe)

### 6. Force Password Change (Security — EU CRA / NIST)

- \[✅\] Onboarding wizard: detect if Pi password is still default (`step-password` shown before step1) `pi`

- \[✅\] Block wizard progression until password changed — call `passwd` from wizard UI

- \[✅\] Store `password\_changed: true` in `onboarding.json` once confirmed

**Deliverable:** Pi fully cloud-ready. T0 devices unaffected. T1+ register via website and push telemetry automatically.


## v0.9.3 — AtMyBoat.com Community Platform \[Effort: Large\]

**Status:** \[ \] Not Started | **Priority:** HIGH **Platform:** WordPress + bbPress + PHP AI — HostPapa shared hosting (no SSH) **Repo:** `github.com/SkipperDon/atmyboat-forum` **Spec:** `deployment/v0.9.3/ATMYBOAT\_BUILD\_REFERENCE.md` (authoritative — all decisions final) **Standing instruction:** `deployment/v0.9.3/ATMYBOAT\_STANDING\_INSTRUCTION.md` — paste at top of every session **Design mockup:** `deployment/v0.9.3/atmyboat-mockup-v2-accessible.html`

> Every session working on v0.9.3 must start by pasting ATMYBOAT\_STANDING\_INSTRUCTION.md. All work happens on HostPapa Staging — never touch the live site until Phase 4. Phases must be completed in strict order.

### What This Builds

| Layer | URL | Technology |
| - | - | - |
| Community forum | atmyboat.com/forum | bbPress WordPress plugin |
| Product hub | atmyboat.com/products | WordPress page templates |
| AI assistant | Forum widget | PHP + cURL → Claude Haiku (claude-haiku-4-5-20251001) |
| Blog SEO | atmyboat.com/blog | Yoast SEO configuration |


### Stack (final — do not substitute)

- **Forum:** bbPress (not Flarum — uses existing WP users, DB, and admin)

- **AI:** PHP + cURL only — HostPapa blocks Node.js, npm, PM2

- **AI model:** Claude Haiku only — hard cap $30/month in Anthropic Console

- **Hosting:** HostPapa Growth shared hosting — FTPS deploy via `lftp`, or cPanel Git VC

- **Theme:** Twenty Twenty child theme — never modify parent theme

- **No subdomains** — all content at atmyboat.com/subfolder (SEO authority stays on one domain)


### Phase 0 — Staging & Safety Net \[Manual — Don does this\]

- [ ] Run UpdraftPlus full backup on live site — verify completed, download off-server

- [ ] Activate HostPapa Staging (cPanel → Staging → Create Staging Site)

- [ ] Confirm staging URL loads identical to live, has its own database

- [ ] Register Anthropic Console account — set $30/month hard billing cap immediately

- [ ] Generate Anthropic API key — keep locally, never paste in chat

**Phase 0 complete when:** Backup downloaded. Staging live. API key in hand.


### Phase 1 — Child Theme Setup \[Manual — Don does this on staging\]

- [ ] Create `wp-content/themes/twentytwenty-child/` with `style.css` (Template: twentytwenty) and `functions.php`

- [ ] Create `inc/`, `logs/`, `data/` folders inside child theme

- [ ] Create `inc/atmyboat-config.php` with Anthropic API key — add to `.gitignore` immediately

- [ ] Activate child theme on staging — verify site still loads correctly

- [ ] Create GitHub repo `SkipperDon/atmyboat-forum` — push child theme (excluding config file)

- [ ] Review existing repo contents before building any file

**Phase 1 complete when:** Child theme active on staging. Config file in place. GitHub repo live.


### Phase 2A — bbPress Forum + MailPoet

- [ ] Install bbPress plugin on staging

- [ ] Create 7 forum categories (in order): d3kOS Support, Marine Electronics, Engine & Mechanical, Electrical & Wiring, Navigation & Charts, General Seamanship, AI-Assisted Fixes

- [ ] Enable open self-registration (WP Admin → Settings → General → Anyone can register)

- [ ] Configure MailPoet for bbPress notification emails via HostPapa SMTP

- [ ] Create forum index page at `/forum` — assign bbPress forum index template

- [ ] Draft 10 seed threads (Claude Code task) — Don posts manually in WP Admin

- [ ] Verify 7 forums visible at `/forum`, 10 threads present, email notifications working


### Phase 2B — AODA Design System

**Design:** Dark navy (\#0A2342) + amber (\#B87800) + teal (\#1A7A6E). Fonts: Playfair Display + Source Serif 4 + JetBrains Mono. All WCAG 2.0 AA minimum 4.5:1 contrast.

- [ ] Add CSS variables and Google Fonts to `style.css`

- [ ] Add blueprint grid background texture (`body::before`)

- [ ] Create `bbpress.css` — forum thread list, post layout, member avatars, category cards

- [ ] Forum body text: 18px minimum, 1.8 line-height (Source Serif 4) — AODA non-negotiable

- [ ] All buttons and links: 48×48px minimum touch targets

- [ ] Skip-to-content link as first focusable element on every page (`header.php` override)

- [ ] Sticky header: backdrop blur, logo left, nav links, amber CTA right

- [ ] Mobile: 4-item bottom nav (Home / Forum / Search / Profile), 48×56px per item

- [ ] Forum readable at 320px — no horizontal scroll

- [ ] Verify all colour pairs pass WCAG 2.0 AA 4.5:1 (see Part 3 of build reference)


### Phase 2C — PHP AI Assistant

**Model:** `claude-haiku-4-5-20251001` only. Max 1000 tokens output. 500 char input limit. No query text stored — token counts and timestamps only.

- [ ] Create `inc/ai-assistant.php` — bbPress context search (WP\_Query top 5 posts) + cURL Anthropic API call

- [ ] System prompt: marine mechanic persona, cites forum thread URLs, plain English, safety caveats

- [ ] Cost guards: reject \>500 char questions, enforce 1000 token cap, log daily token totals to `/logs/ai-YYYY-MM-DD.log`

- [ ] AJAX endpoint in `functions.php` — nonce validation (`check\_ajax\_referer`), input sanitization

- [ ] Create `ai-widget.php` — `\[atmyboat\_ai\]` shortcode, navy/teal styling, question input, answer + source links, disclaimer

- [ ] Add `\[atmyboat\_ai\]` to forum index page and sidebar

- [ ] Test: d3kOS question → response with cited thread URLs

- [ ] Test: \>500 char question → graceful rejection

- [ ] Verify log file created, token counts only, no query text


### Phase 2D — Product Hub

- [ ] Create `data/products.json` — d3kOS entry (name, slug, features, specs, CTAs)

- [ ] Create `page-products.php` — reads products.json, renders product card grid

- [ ] Create `page-product.php` — hero, features, specs, GitHub link, forum support CTA

- [ ] Create d3kOS product page in WP Admin at `/products/d3kos` using `page-product.php`

- [ ] Verify d3kOS page links to d3kOS Support forum category

- [ ] Add Products to main WordPress navigation menu on staging

- [ ] Yoast: set meta title and description on `/products` and `/products/d3kos`


### Phase 2E — SEO Configuration

- [ ] Yoast: enable XML sitemap — includes `/forum`, `/products`, and all blog posts

- [ ] Yoast: bbPress forum threads and archives in sitemap XML

- [ ] Yoast: meta title format for forum threads: "Thread Title | AtMyBoat Community"

- [ ] Yoast: Open Graph for product pages

- [ ] Register Bing Webmaster Tools — verify atmyboat.com, add verification meta tag via Yoast

- [ ] Submit sitemap to Bing Webmaster Tools: `atmyboat.com/sitemap\_index.xml`

- [ ] Submit updated sitemap to Google Search Console via Site Kit

- [ ] Create `/privacy` privacy policy page (PIPEDA requirement)

- [ ] Create `/accessibility` accessibility statement (AODA requirement)

- [ ] Add internal cross-links: homepage → products → forum → blog


### Phase 3 — AODA Compliance Audit (staging — before any migration)

- [ ] All body text 4.5:1 minimum contrast — test every text/background pair

- [ ] 18px minimum font for all forum body text — verify in Chrome DevTools

- [ ] All buttons and links 48×48px touch targets — DevTools mobile emulation

- [ ] All images have descriptive alt text — WAVE scan at wave.webaim.org

- [ ] All form inputs have visible labels (not placeholder-only)

- [ ] Tab navigation through every interactive element in logical order

- [ ] Focus ring visible on every focused element at 3:1+ contrast

- [ ] Skip-to-content link is first Tab stop on every page

- [ ] Screen reader navigates forum thread list (VoiceOver or NVDA)

- [ ] No content flashes more than 3 times per second

- [ ] `lang="en"` on all HTML pages

- [ ] `/privacy` and `/accessibility` pages live and linked in footer

- [ ] Security: `inc/atmyboat-config.php` not in GitHub, AJAX nonces in place, logs not browser-accessible

**Phase 3 complete when:** All AODA checks pass on staging. Cleared for live migration.


### Phase 4 — Migration: Staging → Live \[Manual — Don does this\]

- [ ] Run UpdraftPlus full backup on **live site** — verify completed, download off-server

- [ ] Write down backup timestamp before touching anything

- [ ] HostPapa cPanel: Staging → Push to Live — wait for confirmation

- [ ] Verify: atmyboat.com homepage loads correctly

- [ ] Verify: atmyboat.com/forum loads with all categories and seed threads

- [ ] Verify: atmyboat.com/products loads, d3kOS product page renders

- [ ] Test: submit a forum post — saves correctly, email notification arrives

- [ ] Test: AI assistant question → response with thread citations

- [ ] Verify: sitemap at atmyboat.com/sitemap\_index.xml includes forum and products

- [ ] Resubmit sitemap in Google Search Console and Bing Webmaster Tools

**Phase 4 complete when:** Forum and Product Hub live. AI assistant working. SEO resubmitted.


### Phase 5 — Future Platform Expansion (do not start until Phase 4 verified)

- [ ] T1/T2/T3 subscription tiers

- [ ] Device registration via QR scan

- [ ] Supabase telemetry dashboard

- [ ] Advanced AI (First Mate, session history)

- [ ] Marine Vision gallery

- [ ] Fleet management (T3)

- [ ] B2B intelligence portal

**Deliverable:** atmyboat.com community forum live with AI assistant, product hub showing d3kOS, full AODA compliance, SEO configured.

## v0.9.4 — Mobile Apps (iOS/Android) \[Effort: Large\]

**Status:** \[ \] Not Started | **Priority:** HIGH

### Tasks

- [ ] AtMyBoat.com VPS setup (Headscale, MQTT, PostgreSQL)

- [ ] REST API + web dashboard

- [ ] React Native mobile app

- [ ] Pi integration (Tailscale, MQTT publisher)

**Deliverable:** d3kOS v0.9.5 + AtMyBoat.com cloud platform

## v0.9.5 — Predictive Maintenance \[Effort: Large\]

**Status:** \[ \] Not Started | **Priority:** HIGH

### Tasks

- [ ] Data collection (30-day baseline)

- [ ] Anomaly detection algorithms

- [ ] ML models (5 models: overheating, oil, battery, SD card, GPS)

- [ ] Alert system integration

- [ ] Additional automation (weather, fuel, maintenance scheduling)

**Deliverable:** d3kOS v0.10.0 with predictive maintenance

## v0.9.6 — Fleet Management \[Effort: Medium\]

**Status:** \[ \] Not Started | **Priority:** MEDIUM

### Tasks

- [ ] Fleet creation and invitation system

- [ ] Fleet map with live vessel positions

- [ ] Fleet analytics (engine hours, fuel, alerts)

- [ ] Testing and Tier 3 activation

**Deliverable:** d3kOS v0.10.1 with fleet management

## v0.9.6 — Remote Diagnostic Console \[Effort: Medium\]

**Status:** \[ \] Not Started | **Priority:** MEDIUM

### Tasks

- [ ] Support ticket system + consent flow

- [ ] Diagnostic agent (log collection)

- [ ] Claude API + AI diagnosis

- [ ] Fix delivery + user approval

- [ ] Knowledge base and admin console

**Deliverable:** d3kOS v0.11.0 with remote diagnostics

## v0.9.7 — Autonomous Agents \[Effort: Large\]

**Status:** \[ \] Not Started | **Priority:** HIGH

### Tasks

- [ ] Agent framework (base class, scheduler, communication bus)

- [ ] Update agent (GitHub integration, backup/restore, auto-rollback)

- [ ] Performance agent (CPU/memory/disk monitoring, auto-remediation)

- [ ] Storage agent (cleanup automation, predictive warnings)

- [ ] Health check agent (daily reports, weekly scans)

- [ ] Backup agent (incremental backups, cloud sync)

- [ ] Testing (reliability, failure modes, UAT)

**Deliverable:** d3kOS v0.12.0 with autonomous agents

## v0.9.5 — AI Action Layer \[Effort: Small\]

**Status:** \[✅\] Complete | **Shipped:** v0.9.5 (commit `c68d8c6`) | **Priority:** MEDIUM

### Tasks

- \[✅\] `classify\\\\\\\\\\\\\\\_action\\\\\\\\\\\\\\\_query()` — detect action intent before simple/Gemini routing

- \[✅\] `execute\\\\\\\\\\\\\\\_action()` — whitelist dispatcher (log\_note, log\_hours, set\_fuel\_alarm)

- \[✅\] `\\\\\\\\\\\\\\\_append\\\\\\\\\\\\\\\_maintenance\\\\\\\\\\\\\\\_log()` — append-only JSON log at `/opt/d3kos/data/maintenance-log.json`

- \[✅\] `\\\\\\\\\\\\\\\_set\\\\\\\\\\\\\\\_pref()` — write to `user-preferences.json` for config changes

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

## v0.9.7 — Failure Intelligence & Recovery \[Effort: Small\]

**Status:** \[ \] Not Started | **Priority:** MEDIUM

### Tasks

- [ ] Failure pattern recognition

- [ ] Community data aggregation

- [ ] Recovery playbook system

- [ ] Testing and knowledge base integration

**Deliverable:** d3kOS v0.13.0 with failure intelligence

## v0.9.8 — Security Audit & Penetration Testing \[Effort: Large\]

**Status:** \[ \] Not Started | **Priority:** CRITICAL — Required before v1.0 launch

### Automated Security Scanning

- [ ] Run npm audit (Node.js dependencies)

- [ ] Run pip-audit (Python dependencies)

- [ ] OWASP ZAP automated scan (all web endpoints)

- [ ] SQL injection testing (SQLMap on all database queries)

- [ ] Review OWASP Top 10 compliance

- [ ] Scan for hardcoded secrets in codebase

- [ ] Check file permissions on sensitive files

### Manual Code Review

- [ ] Authentication/authorization review

  - [ ] Verify all API endpoints require auth

  - [ ] Check JWT token validation

  - [ ] Review session management

  - [ ] Test for session hijacking

- [ ] Input validation review

  - [ ] Check all user inputs for XSS prevention

  - [ ] Verify parameterized database queries

  - [ ] Test file upload security

  - [ ] Check for command injection vulnerabilities

  - [ ] Test for directory traversal attacks

- [ ] Secrets management review

  - [ ] API key storage (should be encrypted)

  - [ ] Password hashing (bcrypt/scrypt)

  - [ ] Certificate management

  - [ ] Webhook signature verification

### Penetration Testing (External Firm)

- [ ] Contract professional penetration testing firm

- [ ] External penetration test (network-level attacks)

- [ ] Internal penetration test (privilege escalation)

- [ ] API endpoint fuzzing (all 20+ services)

- [ ] WireGuard VPN security review

- [ ] MQTT broker security audit (TLS, ACLs)

- [ ] Signal K server security review

- [ ] Rate limiting and DDoS protection testing

### Fixes & Privacy Compliance

- [ ] Fix all critical vulnerabilities (must be zero)

- [ ] Fix all high vulnerabilities (must be zero)

- [ ] Document medium/low vulnerabilities with mitigation plans

- [ ] GDPR compliance verification

  - [ ] Data retention policy implementation

  - [ ] User data export functionality (Article 20)

  - [ ] Data deletion functionality (Article 17)

  - [ ] Privacy policy review and update

- [ ] CCPA compliance verification (California users)

- [ ] Retest after fixes

- [ ] Obtain penetration test certificate

### Critical Checklist (Must Pass)

- [ ] Zero critical vulnerabilities

- [ ] Zero high vulnerabilities

- [ ] All API endpoints require authentication

- [ ] All database queries use parameterized statements

- [ ] All passwords hashed with bcrypt/scrypt

- [ ] No hardcoded secrets in code

- [ ] All external APIs use HTTPS

- [ ] Rate limiting on all public endpoints

- [ ] MQTT topics secured with ACLs

- [ ] File uploads validated for malicious content

- [ ] Sessions expire properly

- [ ] All webhooks validate signatures

- [ ] GDPR/CCPA compliant

- [ ] Penetration test certificate obtained

**Deliverable:** d3kOS v0.16.0 — Security certified, production ready

## v1.0.0 — Incremental Update System & Production Launch \[Effort: Large\]

**Status:** \[ \] Not Started | **Priority:** HIGH

### Incremental Update System

- [ ] Enhanced update service (signature verification, checksum)

- [ ] Pre-update snapshot system

- [ ] Post-update health check and auto-rollback

- [ ] Update package storage (AtMyBoat.com)

- [ ] Admin console update manager

### Production Launch Checklist

- [ ] All v0.x eprsions deployed and stable

- [ ] Security audit passed (v0.16.0)

- [ ] Multi-language support active (v0.15.0)

- [ ] Documentation complete (user + developer guides)

- [ ] Professional website launched (AtMyBoat.com)

- [ ] Support infrastructure ready (ticketing, diagnostic console)

- [ ] Payment processing active (Stripe, Apple IAP, Google Play)

- [ ] Beta testing complete (100+ users, 6+ months)

- [ ] Performance targets met (uptime \> 99.5%, response \< 3s)

- [ ] Backup and recovery tested

- [ ] Disaster recovery plan documented

- [ ] Legal review complete (terms, privacy, GDPR/CCPA)

- [ ] Marketing materials ready

- [ ] Press release prepared

- [ ] Launch date announced

**Deliverable:** d3kOS v1.0.0 — Production ready, international marine electronics platform

## 📊 OVERALL PROGRESS TRACKING

### Milestones

- \[✅\] v0.9.1 Complete (Voice AI Assistant)

- \[✅\] v0.9.2 Complete (Metric/Imperial)

- \[✅\] v0.9.2 Complete (Pi Website — dark marine UI rewrite, all 9 pages: index, dashboard, navigation, weather, marine-vision, boatlog, settings, onboarding, helm)

- \[✅\] v0.9.2 Complete (Marine Vision — Live IP Camera System) — both cameras live, nginx fixed, fish detector running

- \[✅\] v0.9.4 Complete (Gemini AI Integration)

- \[✅\] v0.9.5 Complete (AI Action Layer + Remote Access API + Tailscale)

- \[✅\] v0.9.5 Complete (Post-Install Bug Fixes — all 14 items, deployed 2026-03-05)

- \[✅\] v0.9.x Complete (i18n Multi-Language Foundation — 18 languages, Phase 1 deployed 2026-03-06; 14 remaining pages wired in v1.1)

- \[✅\] v0.9.x Complete (Touchscreen Multitouch — d3kos-touch.css + Chromium pinch flags deployed 2026-03-06)

- \[✅\] v0.9.x Complete (OpenCPN Flatpak + AIS Pipeline — Flatpak live, AIS flowing; twofing pinch-zoom working; o-charts activation: Don's manual task)

- [ ] v0.9.6 Complete (Remote Access & Camera Streaming) — cameras not purchased

- [ ] v0.9.6 Complete (Fleet Management)

- [ ] v0.10.0 Complete (Predictive Maintenance)

- [ ] v0.11.0 Complete (Diagnostic Console)

- [ ] v0.12.0 Complete (Autonomous Agents)

- [ ] v0.12.1 Complete (AI Action Layer — extended)

- [ ] v0.13.0 Complete (Failure Intelligence)

- [ ] v0.14.0 Complete (Community Features)

- [ ] v0.15.0 Complete (Multi-Language) — REQUIRED for v1.0

- [ ] v0.16.0 Complete (Security Audit) — REQUIRED for v1.0

- [ ] v1.0.0 LAUNCHED (Production Release)

### Critical Path

- \[✅\] v0.9.1 (Voice AI) — DONE

- \[✅\] v0.9.2 (Metric/Imperial) — DONE

- \[✅\] v0.9.2 (Pi Website dark UI rewrite) — DONE

- \[✅\] v0.9.4 (Gemini AI) — DONE

- \[✅\] v0.9.2 (Marine Vision — Live IP Camera System) — both cameras live, nginx fixed, fish detector running

- \[✅\] Fix: voice rule overmatch ("speed" pattern) — FIXED commit `680a795`

- \[✅\] v0.9.5 (Post-Install Bug Fixes) — all 14 deployed 2026-03-05

- \[✅\] v0.x (Multi-Language Phase 1) — foundation deployed 2026-03-06; 14-page wiring in v1.1

- \[✅\] v0.x (Touchscreen Multitouch) — d3kos-touch.css + Chromium pinch flags deployed 2026-03-06

- \[✅\] v0.x (OpenCPN + AIS) — Flatpak live, AIS flowing; twofing pinch-zoom working; o-charts activation: Don's manual task

- \[✅\] v0.9.2 (Cloud Integration Pre-Requisites — Pi Side) — QR update, port 8091, cloud-credentials.json, Node-RED telemetry push, alarm webhook, force password change

- \[ \] v0.9.3 (atmyboat.com website) — Phase 1: Launch → Phase 2: Community → Phase 3: Revenue → Phase 4: Scale

- [ ] v0.15.0 (Multi-Language full) — REQUIRED for v1.0

- [ ] v0.16.0 (Security Audit) — REQUIRED for v1.0

### Risk Areas (Monitor Closely)

- [ ] Security vulnerabilities (must be zero critical/high at v1.0)

- [ ] Performance degradation (monitor CPU/memory/bandwidth)

- [ ] Third-party API dependencies (Google Gemini, Stripe, Apple, Google Play)

- [ ] Hardware compatibility (cameras, GPS, CAN bus)

- [ ] User adoption (need 1,000+ Tier 2 users for break-even)

- [ ] International compliance (GDPR, CCPA, translation quality)

**Last Updated:** 2026-03-11 | Session: Marine Vision Camera Overhaul complete (Steps 1–5), DEPLOYMENT_INDEX updated

## 📝 NOTES & CONVENTIONS

### Checklist Update Protocol

1. When starting a task: Change `\\\\\\\\\\\\\\\[ \\\\\\\\\\\\\\\]` to `\\\\\\\\\\\\\\\[🔄\\\\\\\\\\\\\\\]`

2. When completing a task: Change `\\\\\\\\\\\\\\\[🔄\\\\\\\\\\\\\\\]` to `\\\\\\\\\\\\\\\[✅\\\\\\\\\\\\\\\]`

3. When blocked: Change to `\\\\\\\\\\\\\\\[⚠️\\\\\\\\\\\\\\\]` and add comment explaining blocker

4. When verification fails: Change to `\\\\\\\\\\\\\\\[🔍\\\\\\\\\\\\\\\]` and add `\\\\\\\\\\\\\\\<!-- VERIFY: issue description --\\\\\\\\\\\\\\\>`

5. When something doesn't work: Change to `\\\\\\\\\\\\\\\[❌\\\\\\\\\\\\\\\]` and add `\\\\\\\\\\\\\\\<!-- NOT WORKING: description --\\\\\\\\\\\\\\\>`

### Commit Protocol

Every commit should update this checklist — mark completed tasks as `\\\\\\\\\\\\\\\[✅\\\\\\\\\\\\\\\]`, add verification comments if testing reveals issues, and tag commits with the version number (e.g., v0.9.2).

### Verification Protocol

All `\\\\\\\\\\\\\\\[🔍\\\\\\\\\\\\\\\]` items must be retested before considering a version complete. Add `\\\\\\\\\\\\\\\<!-- VERIFY: description --\\\\\\\\\\\\\\\>` comments for issues found. Do not proceed to next version until all verifications pass.

**Last Updated:** March 11, 2026 (AAO Methodology GitHub Pages deployment session) | **Maintained By:** Development team + Claude Code

**© 2026 AtMyBoat.com | d3kOS — AI-Powered Marine Electronics** *"Smarter Boating, Simpler Systems"*

