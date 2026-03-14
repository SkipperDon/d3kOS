# d3kOS Deployment Document Index

**Project:** d3kOS / Helm-OS
**Maintained:** Update this file every time a solution document is created or a feature is deployed.

This is the master index of all solution documents, feature deployments, and architectural records for d3kOS. If something was built, fixed, or deployed, it must have an entry here.

---

## Governing Standards (Don's Engineering Standards)

These documents define how all AI work must be performed. They are embedded in full in `/home/boatiq/CLAUDE.md` (auto-loaded every session). Source files in `/home/boatiq/`:

| Source File | Document Name |
|-------------|--------------|
| `1 Master AI Engineering & Testing Standard.md` | Master AI Engineering, Coding, and Testing Standard |
| `1 standar test case creation template.md` | Standard Test Case Creation Template |
| `1 AI Egnieering & Automated Testing Specification Template.md` | AI Engineering & Automated Testing Specification Template |
| `1 AI Egineering SPecification & Soltuion Design Template.md` | AI Engineering Specification & Solution Design Template |
| `aao-methodology-repo/SPECIFICATION.md` | AAO Autonomous Action Operating Methodology v1.1 — 820 lines, 16 sections. d3kOS is the reference implementation. Operational requirements for Claude extracted into `/home/boatiq/CLAUDE.md` Document 5. |

Claude acknowledges all five at the start of every session. See `/home/boatiq/CLAUDE.md` for full content.

## Technical Reference Documents (Don's Reference Guides)

Documents Don has written as technical references. Each is deployed as a solution doc in this project:

| Source File | Deployed To | What It Covers |
|-------------|-------------|---------------|
| `1 openCPN using flatback.md` | `deployment/docs/OPENCPN_FLATPAK_OCHARTS.md` | OpenCPN Flatpak on Debian Trixie + O-Charts plugin — why Flatpak is required, how to activate charts (direct login method + fingerprint method) |

---

## Solution Documents — What Was Built and How

These documents explain what problem was solved and exactly how the solution works. Read these before touching any related code.

| Document | What It Covers |
|----------|---------------|
| `deployment/docs/TOUCH_SCROLL_FIX.md` | labwc mouseEmulation fix — why scrolling broke and how it was fixed (rc.xml change) |
| `deployment/docs/OPENCPN_PINCH_ZOOM.md` | twofing daemon — two-finger pinch zoom in OpenCPN Flatpak via XWayland |
| `deployment/docs/SIGNALK_UPGRADE.md` | Signal K v2.20.3 → v2.22.1 — AIS memory leak fix, heap limit, cx5106 removal |
| `deployment/docs/VOICE_AUDIO_FIX.md` | Voice audio device fix — wrong ALSA card (HDMI) → Roland S-330 USB |
| `deployment/docs/VOICE_QUERY_SPEED.md` | Voice query 7.6s → 0.9s — lazy PDF import + bulk Signal K fetch |
| `deployment/docs/MARINE_VISION_CAMERA_SYSTEM.md` | **[SUPERSEDED — 2026-03-11]** Original two-camera cameras.json system. Replaced by camera-overhaul. Read-only history. |
| `deployment/docs/MARINE_VISION_CAMERA_OVERHAUL.md` | **[ACTIVE]** Slot/Hardware camera architecture — dynamic 1–20 camera management, slots.json + hardware.json, frame buffer, discovery scan, Settings UI camera management tab, Marine Vision dynamic tile renderer, fish detector multi-slot tagging |
| `deployment/docs/VERIFY_AGENT.md` | Independent code reviewer on TrueNAS VM — how it works, endpoints |
| `deployment/docs/WORKFLOW.md` | Ollama executor workflow — how features are built via Ollama |
| `deployment/docs/EXPORT_BOOT_RACE_FIX.md` | `d3kos-export-boot.service` FAILED since 2026-03-04 — root cause: `set -e` + `curl` exit 7 before Flask bound port 8094. Fix: `nc -z` port-ready loop, removed `set -e`, guarded curl/jq. Resolved 2026-03-11. |
| `deployment/docs/FORWARD_WATCH_WORKER_THREAD.md` | `signalk-forward-watch` v0.2.0 — onnxruntime loaded into SK main heap at require() time (~470MB) even when disabled. Fix: moved inference into Node.js Worker thread (`detector-worker.js`). SK heap unaffected. Deployed + verified stable 2026-03-11. |
| Pi: `/home/d3kos/install-opencpn.sh` | OpenCPN Flatpak launcher — bug fix 2026-03-11: `pgrep -f` → `pgrep -x` to prevent SSH command strings triggering false "already running" branch. APT 5.10.2 removed same session; only Flatpak 5.12.4 remains. |
| **[REMOVED 2026-03-12]** Pi: `/etc/systemd/system/d3kos-simulator-api.service` | NMEA2000 Simulator API service — removed, safety/liability risk. Archive: `/home/boatiq/archive/simulator-2026-02-21/` |
| **[REMOVED 2026-03-12]** Pi: `/etc/systemd/system/d3kos-simulator.service` | NMEA2000 Simulator service — removed. Archive: `/home/boatiq/archive/simulator-2026-02-21/` |
| **[REMOVED 2026-03-12]** Pi: `/opt/d3kos/simulator/` | Simulator shell scripts directory — removed. Archive: `/home/boatiq/archive/simulator-2026-02-21/` |
| **[REMOVED 2026-03-12]** Pi: `/opt/d3kos/services/simulator/` | Simulator API Python service directory — removed. Archive: `/home/boatiq/archive/simulator-2026-02-21/` |
| **[REMOVED 2026-03-12]** Pi: `/var/www/html/settings-simulator.html` | Simulator web UI page — removed. |
| `deployment/docs/SIMULATOR_REMOVAL_INSTRUCTIONS.md` | NMEA2000 Simulator removal spec — 14-phase removal procedure. Completed 2026-03-12, commit `a2b05b4`. |
| `deployment/docs/CHARTS_OPENCPN_FIX_INSTRUCTIONS.md` | **[v0.9.2 — ACTIVE]** Charts button / OpenCPN windowed mode fix spec. Tasks 1+2 complete (2026-03-12): index.html charts case uses `goWindowed()`, charts.html `launchOpenCPN()` rewritten. Remaining: nginx proxy for Node-RED `/launch-opencpn` (port 1880 not yet proxied). See STATUS section in doc. |

| `deployment/v0.9.2/python/keyboard-api.py` | **[2026-03-13]** keyboard-api port 8085→8087 (8086 was fish detector). /window/toggle endpoint restored (was missing from repo). Pi: `/opt/d3kos/services/system/keyboard-api.py` |
| `deployment/v0.9.2/nginx/d3kos-nginx.conf` | **[2026-03-13]** /window/ and /keyboard/ proxy_pass updated to 8087. Both sites-available/default and sites-enabled/default kept in sync. |
| `deployment/v0.9.2/pi_source/boatlog.html` | **[2026-03-13]** Voice note onstop handler: replaced download-link pattern with POST to /api/boatlog/voice-note. Keeps voice pause/resume, indicators, 30s auto-stop. Pi: `/var/www/html/boatlog.html` |
| `deployment/v0.9.2/python/remote_api.py` | **[2026-03-13 — NEW IN REPO]** remote_api.py added to repo. Added _tailscale_status() helper, GET /remote/status-stream SSE endpoint (5s poll, keepalive every 15s), threaded=True. Pi: `/opt/d3kos/services/remote/remote_api.py` |
| `deployment/v0.9.2/pi_source/remote-access.html` | **[2026-03-13]** Added startStatusStream() (EventSource /remote/status-stream) and updateStatusBadge(). Tailscale status and QR code update live without page refresh. Pi: `/var/www/html/remote-access.html` |
| `deployment/v0.9.2/python/export_categories.py` | **[2026-03-13 — NEW IN REPO]** collect_settings() now reads user-preferences.json. Adds unit_metadata block (measurement_system, speed/temp/pressure/volume units) to every JSON export. Pi: `/opt/d3kos/services/export/export_categories.py` |
| `deployment/v0.9.2/python/boatlog-export-api.py` | **[2026-03-13 — NEW IN REPO]** CSV export now writes 3-row unit metadata section before data header. _get_unit_metadata() reads user-preferences.json. Pi: `/opt/d3kos/services/boatlog/boatlog-export-api.py` |
| `deployment/docs/MOBILE_APP_STRATEGY_BRIEF.md` | **[2026-03-14 — NEW]** v2.0.0 — Complete mobile app strategy built from 9-question operator Q&A. Covers: PWA on GitHub Pages, HostPapa message broker, tier system (T0-T3), Fix My Pi service, PDF boat reports, OS lockdown, OTA from phone, Find My Boat, build sequence (5 stages). No third-party relay. Zero new infrastructure cost. Context zip at `C:\Users\donmo\Downloads\d3kos-mobile-strategy-2026-03-14.zip` |

---

## Feature Deployments — Ollama Executor Features

Each directory in `deployment/features/` contains a `feature_spec.md`, `phases.json`, Ollama output, and deployed source.

| Feature Dir | What It Does | Status |
|-------------|--------------|--------|
| `deployment/features/post-install-fixes/` | 14 post-install bug fixes (dashboard SK banner, engine benchmark, GPS, export race condition, etc.) | Deployed 2026-03-05 |
| `deployment/features/i18n-page-wiring/` | data-i18n attributes on all 13 HTML pages, 36 new translation keys added to all 18 JSON files. Phases 1–9 (Mar 7), Phases 10–13 (Mar 11). Span-wrap pattern for emoji/arrow elements. | Complete 2026-03-11 |
| `deployment/features/camera-settings-update/` | **[SUPERSEDED]** Dynamic camera cards in settings.html via /camera/list (cameras.json era) | Superseded by camera-overhaul 2026-03-11 |
| `deployment/features/camera-position-assignment/` | **[SUPERSEDED]** Bow/stern/port/starboard position labels per camera (cameras.json era) | Superseded by camera-overhaul 2026-03-11 |
| `deployment/features/community-features/` | Community engine benchmark, anonymizer, boat map, hazard markers | Deployed 2026-03-07 |
| `deployment/features/cloud-integration-prereqs/` | QR code URL, port 8091, cloud-credentials.json, Node-RED telemetry, alarm webhook | Deployed 2026-03-06 |
| `deployment/features/boatlog-voice-note/` | Voice-to-text boat log entries — onstop fix 2026-03-13: API POST working, Don confirmed. | Deployed 2026-03-13 |
| `deployment/features/camera-overhaul/` | **[ACTIVE]** Full camera management overhaul — Slot/Hardware architecture. migrate_cameras.py (Step 1), camera_stream_manager.py rewrite (Step 2), Settings Camera Setup tab (Step 3), Marine Vision dynamic tile renderer (Step 4), fish_detector.py multi-slot (Step 5). Source: `pi_source/`. Spec + checklist in feature dir. | Deployed 2026-03-11 |
| `/home/boatiq/signalk-forward-watch/` | **signalk-forward-watch** standalone SK plugin — YOLOv8 obstacle detection via bow camera. v0.1.0: initial release. v0.2.0 (2026-03-11): onnxruntime moved to Worker thread, SK heap isolated. Published npm + GitHub. | v0.2.0 deployed to Pi 2026-03-11 |

---

## v0.9.2.1 — d3kOS v2.0 Architecture (deployment/d3kOS/)

New Flask-based dashboard stack. Web-first, AI-assisted marine dashboard replacing the OpenCPN-centric Pi menu. AvNav is primary charts, Gemini AI proxy handles navigation AI, OpenCPN is emergency fallback only.

**Plan:** `deployment/d3kOS/D3KOS_PLAN.md` v2.0.0 (canonical implementation plan)
**UI Reference:** `deployment/d3kOS/docs/d3kos-mockup-v4.html` (interactive mockup — all screens)
**Detailed Checklist:** `deployment/d3kOS/PROJECT_CHECKLIST.md`

### Governance Files (d3kOS-specific)

| File | Purpose |
|------|---------|
| `deployment/d3kOS/D3KOS_PLAN.md` | Canonical implementation plan — Phases 0–5, all code, port reference, rollback procedures |
| `deployment/d3kOS/docs/d3kos-mockup-v4.html` | Full interactive UI mockup — main menu, AI nav, settings (16 sections), design system |
| `deployment/d3kOS/PROJECT_CHECKLIST.md` | Phase-by-phase task tracking (detailed) |
| `deployment/d3kOS/SESSION_LOG.md` | Append-only session log for d3kOS build sessions |
| `deployment/d3kOS/CHANGELOG.md` | Milestone entries only |
| `deployment/d3kOS/.gitignore` | Excludes all .env files and cache from git |
| `deployment/d3kOS/pi-menu/BACKUP/BACKUP_LOG.txt` | Timestamped record of all Pi menu backups |

### Directory Structure (to be populated per phase)

| Directory | Phase | Contents |
|-----------|-------|---------|
| `deployment/d3kOS/pi-menu/` | Phase 1 | .desktop and .menu files for Pi menu restructure |
| `deployment/d3kOS/pi-menu/BACKUP/` | Phase 1 | Originals backed up before any edit |
| `deployment/d3kOS/dashboard/` | Phase 2 | Flask app at localhost:3000 |
| `deployment/d3kOS/dashboard/templates/` | Phase 2 | index.html (9-button menu), settings.html (16 sections), offline.html |
| `deployment/d3kOS/dashboard/static/css/` | Phase 2 | d3kos.css — dark theme (#000 bg, #00CC00 accent, Roboto) |
| `deployment/d3kOS/dashboard/static/js/` | Phase 2 | connectivity-check.js (status polling), panel-toggle.js (Windy/Radar) |
| `deployment/d3kOS/dashboard/config/` | Phase 2 | d3kos-config.env (NEVER committed) |
| `deployment/d3kOS/gemini-nav/` | Phase 3 | Flask proxy at localhost:3001 |
| `deployment/d3kOS/gemini-nav/templates/` | Phase 3 | chat.html — AI navigator UI |
| `deployment/d3kOS/gemini-nav/cache/` | Phase 3 | response_cache.json (auto-created, max 10, no query text) |
| `deployment/d3kOS/gemini-nav/config/` | Phase 3 | gemini.env (NEVER committed) |
| `deployment/d3kOS/gemini-nav/tests/` | Phase 3 | test_gemini_proxy.py — full pytest suite (10/10 passing) |
| `deployment/d3kOS/docs/AVNAV_OCHARTS_INSTALL.md` | Phase 4 | **[v1.0.0 — 2026-03-13]** o-charts install guide — plugin install, account, licence activation (direct + fingerprint), chart download, troubleshooting |
| `deployment/d3kOS/docs/AVNAV_PLUGINS.md` | Phase 4 | **[v1.0.0 — 2026-03-13]** AvNav plugins guide — ochartsng, SignalK plugin (ws://localhost:8099 hard rule), anchor alarm, GPX export, POST-only API reference |
| `deployment/d3kOS/docs/OPENPLOTTER_REFERENCE.md` | Phase 4 | **[v1.0.0 — 2026-03-13]** OpenPlotter reference — data flow, plugin config, SK Data Browser, troubleshooting table, service management table |
| `deployment/d3kOS/dashboard/templates/settings.html` | Phase 4 | **[COMPLETE 2026-03-13]** Full 16-section settings page — two-column layout, bookmark sidebar, live status from /status + /sysinfo, system action endpoints, phase roadmap with accurate badges |
| `deployment/d3kOS/dashboard/app.py` | Phase 2+4 | **[Updated 2026-03-13]** Added /sysinfo endpoint (disk/mem/CPU temp/uptime/IP), /action/restart (signalk, nodered, dashboard, gemini), /action/reboot |
| `deployment/d3kOS/dashboard/static/css/d3kos.css` | Phase 2+4 | **[Updated 2026-03-13]** Settings page CSS added — bookmark sidebar, section headers, status grids, cards, form controls, toggles, buttons, phases, info grid, toast |
| `deployment/d3kOS/docs/AVNAV_INSTALL_AND_API.md` | Phase 5 pre-req | AvNav installation procedure. UPDATED 2026-03-13: actual install via apt from free-x.de trixie (OpenPlotter not installed on this Pi). Python 3.13 cgi.parse_qs patch documented. Signal K port 8099. Staged pre-install checklist (Stages A-F) with actual results. |
| `/opt/d3kos/services/ai/ai_api.py` | runtime | ai_api.py moved from port 8080 → 8089 (2026-03-13) to free port 8080 for AvNav. nginx /ai/ proxy updated. |
| `deployment/d3kOS/docs/D3KOS_PHASE5_AI_AVNAV_INTEGRATION.md` | Phase 5 spec | Full AI + AvNav Integration spec v1.1.0. 4 features: Route Widget, Port Arrival Briefing, Voyage Log Summary, Anchor Watch. AI Bridge service at :3002, SSE to dashboard, TTS to Pi speakers. Anomaly-corrected from v1.0.0 (GET→POST, wrong API URL). |
| `deployment/d3kOS/docs/AVNAV_API_REFERENCE.md` | Phase 5 pre-req | **CREATED 2026-03-13** — verified live responses from Pi (request=gps), actual signalk.* key names, Python access patterns. Corrects original spec (request=navigate does not exist in v20250822). |
| `deployment/d3kOS/ai-bridge/ai_bridge.py` | Phase 5 | **[DEPLOYED 2026-03-13]** Flask :3002. /status, /stream (SSE), /analyze-route, /summarize-voyage, /anchor/activate, /anchor/dismiss, /anchor/advice, /voyages. Webhooks: /webhook/arrival, /webhook/alert, /webhook/query. Pi: `/opt/d3kos/services/ai-bridge/ai_bridge.py` |
| `deployment/d3kOS/ai-bridge/features/route_analyzer.py` | Phase 5 | **[DEPLOYED 2026-03-13]** Feature 1: 5-min route analysis widget. RouteAnalyzer background thread. force_analyze(). Route/waypoint change detection. Offline badge. Pi: `/opt/d3kos/services/ai-bridge/features/` |
| `deployment/d3kOS/ai-bridge/features/port_arrival.py` | Phase 5 | **[DEPLOYED 2026-03-13]** Feature 2: 2nm arrival briefing. PortArrivalMonitor. Stage 1 audio pre-AI. Per-destination deduplication. |
| `deployment/d3kOS/ai-bridge/features/voyage_logger.py` | Phase 5 | **[DEPLOYED 2026-03-13]** Feature 3: GPX summarization. parse_gpx_summary() (stats only — no raw GPS to AI). Auto-trigger on recording stop. /voyages endpoint for 5 most recent. |
| `deployment/d3kOS/ai-bridge/features/anchor_watch.py` | Phase 5 | **[DEPLOYED 2026-03-13]** Feature 4: Anchor drag detection. Safety-critical: audio from hardcoded text (NO AI wait). 3-poll debounce. Drift event JSON logged. Repeat alarm every 60s. AI advice on-demand. |
| `deployment/d3kOS/ai-bridge/utils/geo.py` | Phase 5 | **[DEPLOYED 2026-03-13]** haversine_nm, bearing_degrees, ms_to_knots, rad_to_deg, gpx_total_distance_nm |
| `deployment/d3kOS/ai-bridge/utils/avnav_client.py` | Phase 5 | **[DEPLOYED 2026-03-13]** POST-only AvNav client. AVNAV_DATA_DIR=/var/lib/avnav. Direct disk GPX read preferred over API. currentLeg.json reader. |
| `deployment/d3kOS/ai-bridge/utils/signalk_client.py` | Phase 5 | **[DEPLOYED 2026-03-13]** REST polling client. Confirmed paths: navigation.position, speedOverGround (m/s), courseOverGroundTrue (rad), anchor.* |
| `deployment/d3kOS/ai-bridge/utils/tts.py` | Phase 5 | **[DEPLOYED 2026-03-13]** espeak-ng primary (piper unavailable — no voice model on Pi). plughw:S330,0. speak(), speak_urgent(repeat). |
| `deployment/d3kOS/ai-bridge/tests/test_ai_bridge.py` | Phase 5 | **[TODO]** Full pytest suite — not yet written. |
| `deployment/d3kOS/ai-bridge/d3kos-ai-bridge.service` | Phase 5 | **[DEPLOYED 2026-03-13]** systemd unit. User=d3kos. WorkingDirectory=/opt/d3kos/services/ai-bridge. EnvironmentFile=config/ai-bridge.env. Pi: `/etc/systemd/system/d3kos-ai-bridge.service` |
| `deployment/d3kOS/ai-bridge/config/ai-bridge.env` | Phase 5 | **[DEPLOYED 2026-03-13]** Live on Pi at `/opt/d3kos/services/ai-bridge/config/ai-bridge.env`. NEVER committed. gitignored. |
| `deployment/d3kOS/dashboard/static/js/ai-bridge.js` | Phase 5 | **[DEPLOYED 2026-03-13]** SSE EventSource to :3002/stream. Handles all 5 event types. triggerRouteAnalysis(), dismissAnchorAlarm(), getAnchorAdvice(). Pi: `/opt/d3kos/services/dashboard/static/js/ai-bridge.js` |

### v0.9.2.2 Session 1 — Frontend Rebuild (2026-03-14, commit d94b2f9)

| File | Purpose |
|------|---------|
| `deployment/d3kOS/dashboard/config/vessel.env` | Owner config (NEVER committed — gitignored). VESSEL_NAME, HOME_PORT, UI_LANG=en-GB. Loaded by app.py after d3kos-config.env with override=True. Pi: `/opt/d3kos/services/dashboard/config/vessel.env` |
| `deployment/d3kOS/dashboard/templates/index.html` | **[REPLACED 2026-03-14]** Full v12 Jinja2 template — replaces v4 9-button hub. `<html lang="{{ ui_lang }}">`. 3-way row toggle (BOTH/ENGINE/NAV). Day/night with manual=true flag. All Phase 5 AI Bridge IDs present. More menu position 9 = Windowed Mode toggle. JS load order: instruments.js → helm.js → overlays.js → nav.js → ai-bridge.js. Bug 2 fixed (no hidden class on nav row). |
| `deployment/d3kOS/dashboard/static/css/d3kos.css` | **[REPLACED 2026-03-14]** Full v12 design system. Bebas Neue (numerals) + Chakra Petch (UI). White day / `#020702` night. Forest green accent (`#004400` day / `#00CC00` night). Phase 5 additions: `.ai-state` variants, `#anchor-widget`, `#voyage-notice`. |
| `deployment/d3kOS/dashboard/static/js/instruments.js` | **[NEW 2026-03-14]** Row toggle: `showRow('both'|'engine'|'nav')` — toggles `hidden` on `rowEngine`/`rowNav`, sets `.on` on toggle buttons, updates row hint, manages alert dots. Context menu open/close. DOMContentLoaded calls `showRow('both')`. Pi: `/opt/d3kos/services/dashboard/static/js/instruments.js` |
| `deployment/d3kOS/dashboard/static/js/helm.js` | **[NEW 2026-03-14]** HELM voice overlay — `openHelm()`, `closeHelm()`, `toggleMic()`. `HELM_LANG = document.documentElement.lang || 'en-GB'` for Web Speech API locale. 3.5s demo capture timeout. Pi: `/opt/d3kos/services/dashboard/static/js/helm.js` |
| `deployment/d3kOS/dashboard/static/js/overlays.js` | **[NEW 2026-03-14]** All modal/overlay functions: `toast()`, `showAlert()/closeAlert()` (AIS alert + ticker hot), `openDiag()/closeDiag()` (engine), `showCrit()/closeCrit()` (critical screen), `showPosRpt()/closePosRpt()` (4s auto + progress bar), `closeArr()` (arrival banner — id=arrival-widget). Pi: `/opt/d3kos/services/dashboard/static/js/overlays.js` |
| `deployment/d3kOS/dashboard/static/js/nav.js` | **[NEW 2026-03-14]** Bug 1 fix: `manualTheme` flag — `autoTheme()` skips if true; day/night buttons set `manual=true`. Clock, 5-message ticker (fade transition). Split pane `openSplit()/closeSplit()/showTab()`. More menu. `toggleWindowedMode()` → POST localhost:8087/window/toggle. Keyboard shortcuts: d/n/h/m/1/2/3/a/g/c/r/p/Escape. `/status` polling every 30s — ticker shows OFFLINE: failures. Pi: `/opt/d3kos/services/dashboard/static/js/nav.js` |
| `deployment/d3kOS/dashboard/app.py` | **[UPDATED 2026-03-14]** `vessel.env` loaded after `d3kos-config.env` with `override=True`. `UI_LANG = os.getenv('UI_LANG', 'en-GB')`. `ui_lang=UI_LANG` added to `index()` route context. |

### Port Reference (immutable — single source of truth)

| Service | URL | Note |
|---------|-----|------|
| d3kOS Dashboard | localhost:3000 | Flask app — Phase 2 |
| d3kOS Gemini Proxy | localhost:3001 | Flask proxy — Phase 3 |
| d3kOS AI Bridge | localhost:3002 | Flask service — Phase 5 |
| AvNav Charts | localhost:8080 | **INSTALLED 2026-03-13** — avnav 20250822, SK connected on 8099, system.default layout loaded in Chromium ✓ |
| AvNav REST API | POST http://localhost:8080/viewer/avnav_navi.php | POST only — GET returns 501 |
| AvNav updater | localhost:8085 | keyboard-api moved to :8087 — port 8085 free ✓ |
| OpenPlotter | localhost:8081 | Infrastructure only — do NOT touch |
| Signal K | localhost:8099 | Read-only data broker |
| Signal K WebSocket | ws://localhost:8099/signalk/v1/stream | NOT :3000 |
| Ollama (LAN) | 192.168.1.36:11434 | Offline AI fallback |
| Gemini API | generativelanguage.googleapis.com | gemini-2.5-flash |

### Phase Status

| Phase | Name | Status |
|-------|------|--------|
| 0 | Initial Setup & Directory Structure | COMPLETE 2026-03-12 |
| 1 | Pi Menu Restructure | COMPLETE 2026-03-13 |
| 2 | Dashboard Hub (Flask :3000) | COMPLETE 2026-03-13 |
| 3 | Gemini Marine AI Proxy (:3001) | COMPLETE 2026-03-13 |
| 4 | Settings Page + Documentation | COMPLETE 2026-03-13 |
| 5 | AI + AvNav Integration | SOURCE COMPLETE 2026-03-13 — Pi deploy pending |
| **v0.9.2.2** | **Frontend UI Rebuild** | **IN PLANNING 2026-03-13** |

---

## v0.9.2.2 — Frontend UI Rebuild (deployment/d3kOS/)

Complete replacement of the v0.9.2.1 frontend (9-button hub, black/Roboto theme) with the v12 marine-grade instrument dashboard. Backend services unchanged.

**Spec:** `deployment/d3kOS/docs/D3KOS_UI_SPEC.md` v1.0.0
**Addendum:** `deployment/d3kOS/docs/D3KOS_UI_SPEC_ADDENDUM_01.md` v1.0.0 (Wayland kiosk fix)
**Reference mockup:** `deployment/d3kOS/docs/d3kos-mockup-v12.html` (canonical — build 2)
**Findings:** `deployment/d3kOS/docs/D3KOS_V12_FINDINGS.md`

### New Files (2026-03-13)

| File | Purpose |
|------|---------|
| `deployment/d3kOS/docs/D3KOS_UI_SPEC.md` | **[NEW 2026-03-13]** Complete UI/UX spec for v0.9.2.2 — design system, layout, instrument panel, overlays, signal K mapping, alert thresholds. Supersedes d3kos-mockup-v4.html as spec authority. |
| `deployment/d3kOS/docs/D3KOS_UI_SPEC_ADDENDUM_01.md` | **[NEW 2026-03-13]** Wayland kiosk architecture fix. --kiosk → --app --start-maximized. labwc windowRules, Squeekboard integration, wlrctl windowed toggle, UI_LANG in vessel.env. APPROVED — supersedes spec Section 19. |
| `deployment/d3kOS/docs/d3kos-mockup-v12.html` | **[NEW 2026-03-13]** Canonical reference mockup — full v12 UI with 3-way BOTH/ENGINE/NAV toggle, all 5 overlays, day/night mode. This is the implementation reference for v0.9.2.2. |
| `deployment/d3kOS/docs/D3KOS_V12_FINDINGS.md` | **[NEW 2026-03-13]** Design review findings document — canonical mockup declaration, design system tokens, 2 bugs with fix code, gap analysis, v0.9.2.1 comparison, 3-session build plan. |
| `deployment/d3kOS/scripts/launch-d3kos.sh` | **[NEW 2026-03-13]** Chromium launch script — `--app --start-maximized --ozone-platform=wayland`. Replaces kiosk mode. Deploy to Pi at same path, chmod +x. |

---

## Version Release Docs

| Directory | What It Contains |
|-----------|-----------------|
| `deployment/d3kOS/` | **[v0.9.2.1 — ACTIVE BUILD]** d3kOS v2.0 Flask dashboard architecture — Phase 0 complete 2026-03-12. See section above for full index. |
| `deployment/v0.9.2/` | Core v0.9.2 source files — metric/imperial, unit API, scripts, nginx config, systemd units |
| `deployment/v0.9.2/docs/UNITS_API_REFERENCE.md` | Units API — all endpoints, request/response format |
| `deployment/v0.9.2/docs/UNITS_FEATURE_README.md` | Metric/Imperial feature — what it does, how to test |
| `deployment/v0.9.2-multicam/` | **[SUPERSEDED — 2026-03-11]** Pre-overhaul camera source — cameras.json, old camera_stream_manager.py, old marine-vision.html. Read-only history. Active source now at `deployment/features/camera-overhaul/pi_source/` |
| `deployment/v0.9.3/` | AtMyBoat.com build references and spec |
| `deployment/v0.9.3/ATMYBOAT_BUILD_REFERENCE.md` | WordPress + bbPress + HostPapa build master reference |
| `deployment/v0.9.3/ATMYBOAT_STANDING_INSTRUCTION.md` | Hard rules for all v0.9.3 AI sessions |
| `deployment/v1.1/README.md` | v1.1 multilanguage platform — 6-layer build order |

---

## Architectural Specs

| Document | What It Covers |
|----------|---------------|
| `doc/MULTILANGUAGE_PLATFORM_SPEC.md` | Full 6-layer multilanguage architecture spec (v1.1) |
| `Claude/PROJECT_SPEC.md` | Full d3kOS project spec — 43k tokens, read selectively |

---

## Operational Tools

| Document / Path | What It Does |
|-----------------|-------------|
| `deployment/scripts/ollama_execute_v3.py` | Ollama executor — runs features via qwen3-coder:30b |
| `deployment/scripts/verify_agent.py` | Source for TrueNAS verify agent |
| `deployment/scripts/deploy.sh` | Deploys files to Pi via SSH |
| `deployment/docs/helm_os_context.md` | Context file injected into Ollama prompts |

---

## Historical Archive — doc/

The `doc/` directory contains ~200 markdown files written during earlier development sessions (pre-v0.9.2). These are session completion reports, feature plans, fix summaries, Ollama specs, and architectural explorations. They are not actively maintained but serve as the historical record.

**Key docs in doc/ worth knowing:**

| Document | What It Covers |
|----------|---------------|
| `doc/MASTER_SYSTEM_SPEC.md` | Earlier system architecture spec |
| `doc/MARINE_VISION.md` / `doc/MARINE_VISION_API.md` | Phase 1 camera system design |
| `doc/TASK_3_MULTI_CAMERA_COMPLETE.md` | Multi-camera implementation completion record |
| `doc/TASK_1_FORWARD_WATCH_COMPLETE.md` | Forward Watch training completion record |
| `doc/TASK_2_METRIC_IMPERIAL_COMPLETE.md` | Metric/Imperial feature completion |
| `doc/v0.9.2_MULTI_CAMERA_SYSTEM_OLLAMA_SPEC.md` | Original Ollama spec for camera system |
| `doc/v0.9.2_GEMINI_API_INTEGRATION_OLLAMA_SPEC.md` | Gemini integration Ollama spec |
| `doc/v0.9.2_METRIC_IMPERIAL_CONVERSION_OLLAMA_SPEC.md` | Metric/Imperial Ollama spec |
| `doc/PROBLEMS_AND_RESOLUTIONS.md` | Problems encountered and how they were resolved |
| `doc/VOICE_ASSISTANT_ROOT_CAUSE_REPORT.md` | Voice assistant root cause analysis |
| `doc/forward-watch/` | All Forward Watch / obstacle detection docs |

**Rule:** For anything built after 2026-03-06, the solution document goes in `deployment/docs/`, not `doc/`. `doc/` is read-only history.

---

## Update Protocol

Every time work is completed:
1. If it fixed something: create a solution doc in `deployment/docs/`
2. If it is a new feature built via Ollama executor: it already has a `features/` dir
3. Update this index with a new row
4. Update `SESSION_LOG.md`
5. Update `PROJECT_CHECKLIST.md`
