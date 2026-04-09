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
| `deployment/docs/FISH_DETECTION_ARCHITECTURE.md` | **[v1.1.0 — 2026-03-21]** Fish detection two-track architecture: ONNX pipeline (YOLOv8n + EfficientNet-483) vs. RAG/PDF Ontario species knowledge base. NMS fix, log-softmax confidence fix, Gemini Vision on-demand species ID, Phase 2 freshwater model plan. |
| `deployment/docs/VERIFY_AGENT.md` | Independent code reviewer on TrueNAS VM — how it works, endpoints |
| `deployment/docs/D3KOS_USER_MANUAL_v0922.md` | **[v1.0.0 — 2026-03-23]** Full user manual for v0.9.2.2 — covers Setup Wizard (all 8 steps), Dashboard, Weather, Marine Vision, Engine Dashboard, Helm AI, Boat Log, Settings, Remote Access, Troubleshooting. Ingested into Pi RAG (ChromaDB). Superseded by v0992 below. |
| `deployment/docs/D3KOS_USER_MANUAL_v0992.md` | **[v2.0.0 — 2026-04-08 S37]** Full user manual updated to v0.9.9.2 — 16 sections. New vs. v0922: Mobile Companion App (§9), Fix My Pi & OTA (§10), Fleet Management T3 (§11), Autonomous Health System (§14). Updated: Step 6 QR pairing live, Helm AI mute persistence, Predictive Maintenance, Settings (mobile/fleet/predictive subsections), Troubleshooting expanded. NOT YET on website — page-manual.php still to build. |
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
| `deployment/docs/MOBILE_APP_QA_RECORD.md` | **[2026-03-18 — NEW]** v1.0.0 — Verbatim Q&A decision record for mobile app strategy. Authoritative source for all 12 confirmed decisions. 4 corrections applied to original 2026-03-14 brief. |
| `deployment/d3kOS/docs/D3KOS_UAT_V0922_FIXES.md` | **[2026-03-18 — NEW]** v1.0.0 — UAT checklist for 8 confirmed UI fixes identified in 2026-03-18 issue review (I-05, I-07, I-08, I-11, I-14/15, I-16, I-17, I-18, I-19). Don runs this after all 8 fixes are deployed. |

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
**Detailed Checklist:** `PROJECT_CHECKLIST.md` (project root — single master for all projects)

### Governance Files (d3kOS-specific)

| File | Purpose |
|------|---------|
| `deployment/d3kOS/D3KOS_PLAN.md` | Canonical implementation plan — Phases 0–5, all code, port reference, rollback procedures |
| `deployment/d3kOS/docs/d3kos-mockup-v4.html` | Full interactive UI mockup — main menu, AI nav, settings (16 sections), design system |
| `PROJECT_CHECKLIST.md` | Single master checklist — all projects (d3kOS, AtMyBoat, mobile). Consolidated 2026-03-20. |
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

### ❌ v0.9.2.3 — CANCELLED 2026-03-18 — DO NOT DEPLOY

> v0.9.2.3 was a complete deployment failure. CSS regressions broke the working dashboard.
> The weather panel (Session C) was scope Don never requested. Don restored from a prior backup.
> All files listed below are v0.9.2.3 artifacts. They exist in the repo as historical record only.
> Authorized replacement versions of these files were deployed 2026-03-19 (see section below).

| File | Status |
|------|--------|
| `deployment/d3kOS/dashboard/static/css/d3kos.css` | ❌ CANCELLED — superseded by authorized 2026-03-19 deploy (I-08/I-18/I-19 fixes, CSS v=15). |
| `deployment/d3kOS/dashboard/static/js/helm.js` | ❌ CANCELLED — superseded by authorized 2026-03-19 deploy (I-05/I-07). |
| `deployment/d3kOS/dashboard/static/js/nav.js` | ❌ CANCELLED — superseded by authorized 2026-03-19 deploy (I-14/I-15). |
| `deployment/d3kOS/dashboard/static/js/weather-panel.js` | ❌ CANCELLED PERMANENTLY — Open-Meteo weather overlay. Never to be deployed. Not on Pi. |
| `deployment/d3kOS/dashboard/static/js/boatlog-engine.js` | ❌ CANCELLED — superseded by authorized 2026-03-19 deploy (I-17). |
| `deployment/d3kOS/dashboard/templates/index.html` | ❌ CANCELLED — superseded by authorized 2026-03-19 deploy (WX fullscreen). |
| `deployment/d3kOS/dashboard/templates/boat-log.html` | ❌ CANCELLED — Session D font + engine entry changes not to be deployed. |
| `deployment/d3kOS/docs/V0923_PLAN.md` | ❌ CANCELLED — plan is void. Retained as historical record only. |
| `deployment/d3kOS/docs/D3KOS_UAT_V0923.md` | ❌ CANCELLED — UAT is void. |

---

### v0.9.2.2 — Authorized UI Fix Deployment (2026-03-19, commit 426c783)

Batches 1–4 of authorized v0.9.2.2 UI fixes. All changes explicitly authorized by Don before implementation. No Session C (v0.9.2.3) code used.

| File | Description |
|------|-------------|
| `deployment/d3kOS/dashboard/static/css/d3kos.css` | **[UPDATED 2026-03-19]** I-19: base font 18px → 20px. I-08: `.close-btn` 48×48px, 24px inset, dark bg, bold. I-18: global dropdown rule min-height:52px, 20px font. CSS v=15. Backup: `d3kos.css.bak-20260319`. |
| `deployment/d3kOS/dashboard/templates/index.html` | **[UPDATED 2026-03-19]** CSS link bumped to `?v=15`. WX pill button added to row toggle (4th: BOTH\|ENGINE\|NAV\|WX). `#wxFs` div + `#wxFsFrame` iframe + `#wxFsBar` countdown/day-night. Inline CSS for WX fullscreen. Weather bottom nav button regression fixed: `openSplit('wx')` restored. Backup: `index.html.bak-20260319`. |
| `deployment/d3kOS/dashboard/templates/ai-navigation.html` | **[UPDATED 2026-03-19]** CSS link bumped to `?v=15`. |
| `deployment/d3kOS/dashboard/templates/boat-log.html` | **[UPDATED 2026-03-19]** CSS link bumped to `?v=15`. |
| `deployment/d3kOS/dashboard/templates/engine-monitor.html` | **[UPDATED 2026-03-19]** CSS link bumped to `?v=15`. |
| `deployment/d3kOS/dashboard/templates/manage-documents.html` | **[UPDATED 2026-03-19]** CSS link bumped to `?v=15`. |
| `deployment/d3kOS/dashboard/templates/marine-vision.html` | **[UPDATED 2026-03-19]** CSS link bumped to `?v=15`. |
| `deployment/d3kOS/dashboard/templates/upload-documents.html` | **[UPDATED 2026-03-19]** CSS link bumped to `?v=15`. |
| `deployment/d3kOS/dashboard/static/js/instruments.js` | **[UPDATED 2026-03-19]** `showRow()` extended: `'wx'` case hides `#main`, shows `#wxFs`, manages Windy iframes (windyFrame blanked), calls `_wxFsStart()`/`_wxFsStop()`. WX fullscreen functions: `_wxFsStart()`, `_wxFsStop()`, `wxFsToggleDayNight()`, `_wxFsSyncDayNight()`, `_wxFsUpdateCountdown()`. Countdown 15-min timer, auto-reload weather.html on expiry. Backup: `instruments.js.bak-20260319`. |
| Pi: `/opt/d3kos/services/dashboard/static/js/helm.js` | **[UPDATED 2026-03-19, Pi only]** I-05: `nb-active` added to HELM button only when overlay is open, removed on close. I-07: `helmMuted` flag + `toggleHelmMute()`, persisted via `localStorage('d3kHelmMute')`, cancels speechSynthesis on mute. |
| Pi: `/opt/d3kos/services/dashboard/static/js/nav.js` | **[UPDATED 2026-03-19, Pi only]** I-14/I-15: `window.onbeforeunload = null` set before `window.location.href` for all internal navigation (Marine Vision, Boat Log, and all other internal links). |
| Pi: `/opt/d3kos/services/dashboard/static/js/boatlog-engine.js` | **[NEW 2026-03-19, Pi only]** I-17: Signal K WebSocket subscriber for engine data. Detects engine start/stop via RPM threshold. Records: start event, 30-min snapshots (RPM + coolant + oil + battery + fuel), stop event, threshold alert crossings. POSTs to `POST /api/boatlog/engine-entry`. |
| Pi: `/opt/d3kos/services/boatlog/boatlog-export-api.py` | **[UPDATED 2026-03-19, Pi only — targeted insert]** `POST /api/boatlog/engine-entry` endpoint added. Creates `boatlog_entries` table if absent. Inserts engine snapshot with ENGINE badge. Voice-note endpoint and unit metadata already on Pi — NOT overwritten. |
| Pi: `/var/www/html/weather.html` | **[UPDATED 2026-03-19, Pi only]** Header hidden when loaded as iframe (`window.self !== window.top`). GPS no-fix guard: skip lat=0/lon=0 Signal K updates to preserve Lake Simcoe fallback. Backup: `weather.html.bak-20260319-wxfs`. |
| Pi: `/etc/nginx/sites-enabled/default` | **[UPDATED 2026-03-19, Pi only]** Added `location = /weather.html` → `/var/www/html/weather.html` (static). Added `location /js/` → `/var/www/html/js/` (static). Both inserted before `location /` (Flask proxy) to prevent 404. |

---

### v0.9.2.2 Recovery Session D — Upload Docs, Manage Docs, AI Navigation, Engine Monitor (2026-03-16)

| File | Description |
|------|-------------|
| `deployment/d3kOS/dashboard/templates/upload-documents.html` | **[REPLACED 2026-03-16]** Full PDF upload page. File picker (PDF only, 50 MB max), manual type selector, POST multipart to `localhost:8081/upload/manual`, progress bar, success/error feedback, D/N theme. |
| `deployment/d3kOS/dashboard/templates/manage-documents.html` | **[REPLACED 2026-03-16]** Document library page. GET `localhost:8083/manuals/list`, filename/size/date per row, delete with confirm dialog, DELETE `localhost:8083/manuals/delete/<filename>`, empty state, D/N theme. |
| `deployment/d3kOS/dashboard/templates/ai-navigation.html` | **[REPLACED 2026-03-16]** Full-page AI marine chat. POST `localhost:3001/ask` with `{message}`, me/bot bubbles, thinking animation, GEMINI/OLLAMA source badge, 60 s timeout, D/N theme. |
| `deployment/d3kOS/dashboard/templates/engine-monitor.html` | **[REPLACED 2026-03-16]** Live engine data page. SK WebSocket `ws://localhost:8099/signalk/v1/stream`, 6 paths (RPM/coolant/oil/battery/fuel/trim), alert flood states (adv/alrt/crit), auto-reconnect 5 s, D/N theme. |

---

### v0.9.2.2 Session 3 — Cameras, More Menu, Onboarding (2026-03-14, commit c6fd43e)

| File | Purpose |
|------|---------|
| `deployment/d3kOS/dashboard/static/js/cameras.js` | **[NEW 2026-03-14]** Cameras tab logic. `loadCameras()` fetches `/camera/slots` from :8084; renders forward-watch slot as full-width primary; display_in_grid slots in 2×2 grid. Frame polling at 500ms via `/camera/frame/<slot_id>`. `clearCamIntervals()` called by `closeSplit()`. Graceful "unavailable" fallback. Pi: `/opt/d3kos/services/dashboard/static/js/cameras.js` |
| `deployment/d3kOS/dashboard/templates/setup.html` | **[UPDATED 2026-03-23G]** 8-step onboarding wizard. Step 1: Welcome. Step 2: Vessel Identity. Step 3: Engine & Drive (skip). Step 4: Electronics & NMEA. **Step 5: Gateway Configuration** — dedicated DIP switch step (CX5106 Row 1+Row 2 diagrams, port+starboard for twin engines, Why These Settings box, install warning, EMU-1/generic/no-gateway notices). Step 6: Mobile Pairing (skip). Step 7: Gemini API Key (skip). Step 8: Done (camera in new tab). Back arrow all steps, full-width AODA layout, localStorage `d3kos_wiz_v3`. Commit d970afc. Pi: `/opt/d3kos/services/dashboard/templates/setup.html` |
| `deployment/d3kOS/dashboard/templates/index.html` | **[UPDATED 2026-03-14]** Cameras tab wired to cameras.js. More menu: removed Demo:EngDiag/PosReport/Arrival; added real Engine Monitor, Trip Log, Settings, OpenCPN. Load order adds cameras.js between nav.js and ai-bridge.js. |
| `deployment/d3kOS/dashboard/static/js/nav.js` | **[UPDATED 2026-03-14]** showTab() calls loadCameras() on cam tab; closeSplit() calls clearCamIntervals(); launchOpenCPN() added → POST /launch/opencpn. |
| `deployment/d3kOS/dashboard/app.py` | **[UPDATED 2026-03-14]** index() redirects to /setup when vessel.env absent. /setup GET renders setup.html. /setup POST writes vessel.env, reloads runtime env vars, redirects to /. |

### v0.9.2.2 Session 1 — Frontend Rebuild (2026-03-14, commit d94b2f9)

| File | Purpose |
|------|---------|
| `deployment/d3kOS/dashboard/config/vessel.env` | Owner config (NEVER committed — gitignored). VESSEL_NAME, HOME_PORT, UI_LANG=en-GB. Loaded by app.py after d3kos-config.env with override=True. Pi: `/opt/d3kos/services/dashboard/config/vessel.env` |
| `deployment/d3kOS/dashboard/templates/index.html` | **[REPLACED 2026-03-14]** Full v12 Jinja2 template — replaces v4 9-button hub. `<html lang="{{ ui_lang }}">`. 3-way row toggle (BOTH/ENGINE/NAV). Day/night with manual=true flag. All Phase 5 AI Bridge IDs present. More menu position 9 = Windowed Mode toggle. JS load order: instruments.js → helm.js → overlays.js → nav.js → ai-bridge.js. Bug 2 fixed (no hidden class on nav row). |
| `deployment/d3kOS/dashboard/static/css/d3kos.css` | **[UPDATED 2026-03-16]** v12 design system + AODA/IEC-62288 marine helm font scale (CSS v=9). Research basis: IEC 62288 + ISO 9241-303 at 1m on 10.1" 150PPI. `.ic-l`=32px, `.ic-u`=24px, `.nb-lbl`=28px, `--row-h`=160px, form controls 20px min-height:52px, zero 16px violations. |
| `deployment/d3kOS/dashboard/static/js/instruments.js` | **[NEW 2026-03-14]** Row toggle: `showRow('both'|'engine'|'nav')` — toggles `hidden` on `rowEngine`/`rowNav`, sets `.on` on toggle buttons, updates row hint, manages alert dots. Context menu open/close. DOMContentLoaded calls `showRow('both')`. Pi: `/opt/d3kos/services/dashboard/static/js/instruments.js` |
| `deployment/d3kOS/dashboard/static/js/helm.js` | **[NEW 2026-03-14]** HELM voice overlay — `openHelm()`, `closeHelm()`, `toggleMic()`. `HELM_LANG = document.documentElement.lang || 'en-GB'` for Web Speech API locale. 3.5s demo capture timeout. Pi: `/opt/d3kos/services/dashboard/static/js/helm.js` |
| `deployment/d3kOS/dashboard/static/js/overlays.js` | **[NEW 2026-03-14]** All modal/overlay functions: `toast()`, `showAlert()/closeAlert()` (AIS alert + ticker hot), `openDiag()/closeDiag()` (engine), `showCrit()/closeCrit()` (critical screen), `showPosRpt()/closePosRpt()` (4s auto + progress bar), `closeArr()` (arrival banner — id=arrival-widget). Pi: `/opt/d3kos/services/dashboard/static/js/overlays.js` |
| `deployment/d3kOS/dashboard/static/js/nav.js` | **[NEW 2026-03-14]** Bug 1 fix: `manualTheme` flag — `autoTheme()` skips if true; day/night buttons set `manual=true`. Clock, 5-message ticker (fade transition). Split pane `openSplit()/closeSplit()/showTab()`. More menu. `toggleWindowedMode()` → POST localhost:8087/window/toggle. Keyboard shortcuts: d/n/h/m/1/2/3/a/g/c/r/p/Escape. `/status` polling every 30s — ticker shows OFFLINE: failures. **[UPDATED 2026-03-23]** `navTo()` blanks AvNav iframe before navigating — suppresses Leave site dialog. **[UPDATED 2026-03-23D]** `launchOpenCPN()` removed (OpenCPN removed from d3kOS). Pi: `/opt/d3kos/services/dashboard/static/js/nav.js` |
| `deployment/d3kOS/dashboard/static/js/panel-toggle.js` | **[UPDATED 2026-03-23D]** `launchOpenCPN()` function removed (OpenCPN removed from d3kOS). Pi: `/opt/d3kos/services/dashboard/static/js/panel-toggle.js` |
| `deployment/d3kOS/dashboard/templates/settings.html` | **[UPDATED 2026-03-23D]** OpenCPN Fallback Guide doc-btn removed from documentation section. "AvNav down → Use OpenCPN Fallback" emergency step removed. Pi: `/opt/d3kos/services/dashboard/templates/settings.html` |
| Pi: `/home/d3kos/.node-red/flows.json` | **[UPDATED 2026-03-23D, Pi only]** 3 OpenCPN flow nodes removed: `launch_opencpn_http_in`, `launch_opencpn_exec`, `launch_opencpn_http_response`. Backup: `flows.json.bak-20260323-opencpn`. Node-RED restarted — active. |
| `deployment/d3kOS/dashboard/templates/marine-vision.html` | **[UPDATED 2026-03-23E]** Day mode visibility fix: back button and h1 title used `var(--g-txt)` (#004400 dark green) over `var(--bar)` (#003200 dark green) — invisible. Both now `rgba(180,255,180,0.92)` — visible over dark bar in both modes. Layout: removed `max-width:1400px` + `margin:0 auto` from `.container`; padding 20px→10px; `.camera-container` padding 18px→8px. **[UPDATED 2026-03-23B]** Bug 1: active default fallback — `loadSlots()` now falls back to first slot with `has_frame:true` if active_default has no frame (graceful chain: active_default+frame → first-with-frame → active_default → slots[0]). Bug 2: connecting/offline distinction — `renderSelector()` disables only when `hardware.status==='offline'`; new `.connecting` CSS class (opacity 0.65, tappable). Commits: d5a87f0 (tests), f56ee11 (fix). Pi: `/opt/d3kos/services/dashboard/templates/marine-vision.html` |
| `deployment/d3kOS/dashboard/tests/test_marine_vision_ui.js` | **[NEW 2026-03-23B]** TDD tests for marine-vision.html UI bugs — Bug 1 (active default fallback) and Bug 2 (connecting/offline distinction). 8/8 pass. Commits: d5a87f0, f56ee11. |
| `deployment/d3kOS/dashboard/tests/test_hardware_json.js` | **[NEW 2026-03-23C]** TDD test confirming hardware.json RTSP IP mismatch for Port (.134≠.135) and Starboard (.182≠.183). Validates that rtsp_url host matches ip field for all hardware entries. 7/7 pass. |
| `deployment/d3kOS/dashboard/tests/test_camera_stream_manager_rtsp_sync.py` | **[NEW 2026-03-23C]** TDD test for camera_stream_manager structural bug — `run_discovery_scan()` updating `ip` without updating `rtsp_url`. 6/6 pass. Bug confirmed with BUGGY fixture. |
| `deployment/v0.9.2/pi_source/camera_stream_manager.py` | **[UPDATED 2026-03-23C]** Structural fix in `run_discovery_scan()`: added `hw['rtsp_url'] = re.sub(r'(?<=@)[^:]+(?=:)', ip, hw.get('rtsp_url', ''))` after `hw['ip'] = ip`. Prevents RTSP URL staleness on DHCP lease change. Pi: `/opt/d3kos/services/marine-vision/camera_stream_manager.py`. Backup: `camera_stream_manager.py.bak-20260323b`. |
| Pi: `/opt/d3kos/config/hardware.json` | **[FIXED 2026-03-23C, Pi only]** Corrected RTSP URLs for Port (was .134, now .133) and Starboard (was .182, now .181). Helm IP updated to .63. All 4 cameras online after fix. Backup: `hardware.json.bak-20260323`. |
| Pi: `/etc/NetworkManager/dnsmasq-shared.d/camera-reservation.conf` | **[UPDATED 2026-03-23C, Pi only]** MAC→IP reservations (infinite lease) for all 4 cameras: bow=ec:71:db:f9:7c:7c→10.42.0.100, helm=ec:71:db:99:78:04→10.42.0.63, port=ec:71:db:43:ef:c1→10.42.0.133, starboard=ec:71:db:be:0b:7b→10.42.0.181. Reloaded via SIGHUP to dnsmasq PID 1457. |
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
| **v0.9.2.2** | **Frontend UI Rebuild** | **CODE COMPLETE 2026-03-14 — Don verify pending** |

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
| `deployment/d3kOS/docs/V0922_RECOVERY_PLAN.md` | **[NEW 2026-03-14]** v0.9.2.2 Recovery Plan v1.0.0 — 17-assumption register, 9-page scope, 5-session execution plan (3 waves, 12 increments). AAO methodology section embedded. Read before every recovery session. |

---

## Pi Health Fixes — 2026-03-18

Continuous-operation diagnostic session. 6 anomalies found and resolved directly on Pi via SSH. No new repo files — all changes are Pi-side patches.

| Item | Pi Path | What Changed |
|------|---------|-------------|
| Chromium launch script | `/opt/d3kos/scripts/launch-d3kos.sh` | `--disable-gpu` removed. `--use-gl=angle --use-angle=swiftshader` active. Deployed from repo. |
| fake-hwclock | `/etc/fake-hwclock.data` | `apt install fake-hwclock` — saves/restores clock across reboots. Pi has no hardware RTC; without this, systemd timestamps are unreliable after reboot. |
| AvNav Signal K handler | `/usr/lib/avnav/server/handler/signalkhandler.py` | Line 1580 patched — charts URL from `/v1/api/` to `/v2/api/`. SK 2.x moved resources to v2; AvNav was polling v1. Backup: `.bak-20260318`. |
| Signal K resources-provider | `~/.signalk/package.json` | `@signalk/resources-provider ^1.5.1` — confirmed built-in to SK 2.22.1. Active on `/signalk/v2/api/resources/charts` → `200 {}`. |
| Node-RED settings | `/home/d3kos/.node-red/settings.js` | `contextStorage: localfilesystem` enabled. `credentialSecret` set. |

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
| `deployment/v0.9.3/ATMYBOAT_BUILD_REFERENCE.md` | WordPress + bbPress + HostPapa build master reference — v2.2 (Part 18 added 2026-04-08 S38: all v0.9.9.2 build decisions — M1 anchor watch 25m, M2 fleet portal, M14 AI engine diagnostic, M15 alert delivery no SMS, M16 root cause fixed, M17 branding, M18 manual, M13 removed) |
| `deployment/v0.9.3/ATMYBOAT_STANDING_INSTRUCTION.md` | Hard rules for all v0.9.3 AI sessions |
| `deployment/v0.9.3/SESSION6_CONTENT_PLAN.md` | S6 content plan — APPROVED 2026-03-25 — 9 pages + connectivity sections, all Q&A decisions recorded |
| `deployment/v1.1/README.md` | v1.1 multilanguage platform — 6-layer build order |

### v0.9.3 Child Theme — PHP Endpoints & Pages (2026-03-26)

| File | Description |
|------|-------------|
| `wp-content/themes/twentytwenty-child/mobile/community-get.php` | GET community map data — blurred positions + hazard markers. No auth. Bounding box query, 60s cache. |
| `wp-content/themes/twentytwenty-child/mobile/community-markers.php` | POST hazard marker from Pi. Auth required. Rate-limited 20/day. Awards 1 community point. |
| `wp-content/themes/twentytwenty-child/page-accessibility.php` | /accessibility — AODA compliance statement (Ontario legal requirement). Static page. Template: Accessibility Statement. |
| `wp-content/themes/twentytwenty-child/page-account.php` | /account — Account management. Updated: AODA font fixes, refund status in billing, last_seen_at on devices. |
| `wp-content/themes/twentytwenty-child/mobile/data-ingress.php` | Pi heartbeat. Updated: pi_id + last_seen_at + d3kos_version written to amboat_devices; d3kos_pairings.last_seen_at updated; full feature matrix + fmp_remaining in response. |
| `wp-content/themes/twentytwenty-child/mobile/fix-my-pi-billing.php` | FMP billing. Updated: report_result endpoint (Pi reports success/failed/timeout), auto-refund on T1 failure, charge.refunded webhook. |
| `wp-content/themes/twentytwenty-child/setup/mobile-schema.sql` | DB schema. Updated: 7 ALTER TABLE statements for multi-boat support + refund columns. |
| `wp-content/themes/twentytwenty-child/functions.php` | WordPress functions. Bug fix: T2 FMP monthly cron reset wrong meta key (fmp_month_count → fmp_used_month). |
| `wp-content/themes/twentytwenty-child/style.css` | Master stylesheet. Updated: --text-faint CSS variable (5.36:1 AA), code/kbd/samp 18px override. |
| `wp-content/themes/twentytwenty-child/page-community.php` | /community — Updated: full Leaflet 1.9.4 map wiring (fleet dots + hazard markers + auto-refresh + privacy blurring). S38: confirmed simplified layout complete (map → stats → discussions). |
| `wp-content/themes/twentytwenty-child/page-hardware.php` | /hardware — S38 2026-04-08: photo strip col 1 fixed H2→H1 (H1-Pi-in-enclosure-mounted.jpg). Hero stays H2. |
| `wp-content/themes/twentytwenty-child/atmyboat-config.php` | Staging config — S38 2026-04-08: M16 fix — added GEMINI_API_KEY, GEMINI_MODEL, GEMINI_MAX_TOKENS. ai-assistant.php now has correct constants. |

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

---

## Session 2026-03-22B Updates

| File | Description |
|------|-------------|
| `deployment/features/boatlog-voice-note/pi_source/boatlog-export-api.py` | **[UPDATED 2026-03-22B]** Three fixes: (1) `flask-cors` CORS() wrapper — browser at :3000 can now read API responses from :8095; (2) `_get_vosk_model()` singleton — Vosk loaded once at startup, cached; beats nginx 30s proxy timeout; (3) voice notes now INSERT into `boatlog_entries` SQLite table after transcription so export CSV includes them. Pi: `/opt/d3kos/services/boatlog/boatlog-export-api.py` |
| `deployment/d3kOS/dashboard/templates/boat-log.html` | **[UPDATED 2026-03-22B]** Client fix: `MediaRecorder.isTypeSupported()` MIME probe for Pi ARM64 codec detection; voice service pause before `getUserMedia` (prevents HELM wake-word activation during recording); voice service resume in onstop and error paths. Pi: `/opt/d3kos/services/dashboard/templates/boat-log.html` |
| `deployment/features/boatlog-voice-note/tests/test_voice_note_api.py` | **[2026-03-22 — NEW]** TDD test suite: 3 tests covering 0-byte rejection, OGG extension mapping, missing audio field. All 3 passing. |

## Session 2026-03-23F Updates

| File | Description |
|------|-------------|
| `deployment/d3kOS/dashboard/app.py` | **[UPDATED 2026-03-23F]** Added `POST /api/settings/vessel` endpoint — reads vessel_name + home_port from JSON, updates vessel.env (preserves all other keys), reloads runtime globals. Also fixed `OLLAMA_HOST` default: `192.168.1.36:11434` → `127.0.0.1:11434`. Pi: `/opt/d3kos/services/dashboard/app.py` |
| `deployment/d3kOS/dashboard/templates/settings.html` | **[UPDATED 2026-03-23F]** Added "Save Vessel Settings" button + `saveVesselSettings()` JS in AI section — was missing despite inputs existing. Fixed 3 hardcoded Ollama display values: address `192.168.1.36:11434` → `127.0.0.1:11434`, model `qwen3-coder:30b` → `phi3.5:latest`. Pi: `/opt/d3kos/services/dashboard/templates/settings.html` |
| Pi: `d3kos-config.env` | **[UPDATED 2026-03-23F — Pi only]** `OLLAMA_HOST=192.168.1.36:11434` → `127.0.0.1:11434`. Root cause of `/status` returning `ollama:false` despite Ollama running locally. Pi: `/opt/d3kos/services/dashboard/config/d3kos-config.env` |
| Pi: `gemini.env` | **[UPDATED 2026-03-23F — Pi only]** `OLLAMA_URL=http://192.168.1.36:11434` → `http://127.0.0.1:11434`. `OLLAMA_MODEL=qwen3-coder:30b` → `phi3.5:latest` (installed on Pi). Backup: `gemini.env.bak-20260323`. Pi: `/opt/d3kos/services/gemini-nav/config/gemini.env` |

## Session 2026-03-26 Updates — v0.9.4 S1 Pi Cloud Infrastructure

| File | Description |
|------|-------------|
| `deployment/v0.9.4/pi_source/export-manager.py` | **[UPDATED 2026-03-26]** `CENTRAL_API_URL` fixed: `d3kos-cloud-api.example.com` → `https://atmyboat.com/staging`. Pi: `/opt/d3kos/services/export/export-manager.py` |
| `deployment/v0.9.4/pi_source/export_categories.py` | **[NEW — 2026-03-26]** Full rewrite with 5 new categories: `collect_gps()` (Signal K nav.position, SOG knots, COG deg, has_fix), `collect_engine()` (propulsion.port rpm/temp/oil/fuel/hours), `collect_system_health()` (11 service statuses + uptime/memory/disk/cpu_temp), `collect_system_alerts()` (last 50 self-healing DB records), `collect_version()` (parses version.txt). collect_all() now produces 13 categories. Pi: `/opt/d3kos/services/export/export_categories.py` |
| `deployment/v0.9.4/pi_source/export_worker.py` | **[NEW — 2026-03-26]** Full rewrite. Reads `amboat_api_key` + `amboat_base_url` from `cloud-config.json`. Reads device_token from `device-token.json`. POSTs to `data-ingress.php` with correct auth headers. `_build_ingress_payload()` maps 13-category export to data-ingress.php format (position, engine, system, alerts, boatlog). Pi: `/opt/d3kos/services/export/export_worker.py` |
| `deployment/v0.9.4/pi_source/cloud_agent.py` | **[NEW — 2026-03-26]** Command consumer service. Polls `command-queue.php` every 30s. Handlers: ping, export_now, tier_change. fix_my_pi/ota_upgrade ACK'd as not-yet-implemented. Generates device UUID on first run. Logs to `/opt/d3kos/logs/cloud-agent.log`. Pi: `/opt/d3kos/services/cloud-agent/cloud_agent.py` |
| `deployment/v0.9.4/pi_source/cloud-config.json` | **[NEW — 2026-03-26]** Template for Pi-side AtMyBoat.com config. Stores amboat_api_key (placeholder in repo), amboat_base_url, poll_interval_seconds. Real key written directly to Pi, never committed. Pi: `/opt/d3kos/config/cloud-config.json` |
| `deployment/v0.9.4/pi_source/d3kos-cloud-agent.service` | **[NEW — 2026-03-26]** systemd unit for cloud_agent.py. After: network.target d3kos-export-manager.service. Pi: `/etc/systemd/system/d3kos-cloud-agent.service` |
| `atmyboat-forum: mobile/data-ingress.php` | **[UPDATED 2026-03-26]** Added boatlog text entries handling — INSERT IGNORE into amboat_boatlog with (user_id, pi_installation_id, pi_entry_id, entry_type, content, entry_timestamp). Server: `/staging/wp-content/themes/twentytwenty-child/mobile/data-ingress.php` |
| `atmyboat-forum: setup/mobile-schema.sql` | **[UPDATED 2026-03-26]** Added amboat_boatlog table — v0.9.4 S1 addition. UNIQUE KEY on (pi_installation_id, pi_entry_id) prevents duplicate imports. |
| `atmyboat-forum: setup/s1-setup.php` | **[2026-03-26 — Setup script, run and kept as doc]** Created amboat_boatlog table on staging. |
| `atmyboat-forum: setup/s1-migrate.php` | **[2026-03-26 — Setup script, run and kept as doc]** Added d3kos_pairings.last_seen_at column (was missing, caused HTTP 500 in data-ingress.php). |

## Session 2026-03-26 S2 Updates — v0.9.4 S2 Full Build

| File | Description |
|------|-------------|
| `deployment/v0.9.4/pi_source/tier_service.py` | **[NEW — 2026-03-26 S2]** Flask service port 8093. Reads license.json, returns tier int + feature matrix per tier (0–3). Pi: `/opt/d3kos/services/tier/tier_service.py` |
| `deployment/v0.9.4/pi_source/d3kos-tier.service` | **[NEW — 2026-03-26 S2]** systemd unit for tier_service.py. Pi: `/etc/systemd/system/d3kos-tier.service` |
| `deployment/v0.9.4/pi_source/export_worker.py` | **[UPDATED — 2026-03-26 S2]** P6: added `_sync_tier_from_response()` — reads tier from data-ingress.php response, updates license.json. Pi: `/opt/d3kos/services/export/export_worker.py` |
| `deployment/v0.9.4/pi_source/fix_my_pi.py` | **[NEW — 2026-03-26 S2]** Diagnostic + repair script. Checks services (auto-restart), disk, config files, network. Returns structured JSON report. Pi: `/opt/d3kos/services/cloud-agent/fix_my_pi.py` |
| `deployment/v0.9.4/pi_source/ota_upgrade.py` | **[NEW — 2026-03-26 S2]** Full OTA pipeline: version check → download → SHA-256 verify → backup → install → restart → rollback. Pi: `/opt/d3kos/services/cloud-agent/ota_upgrade.py` |
| `deployment/v0.9.4/pi_source/alert_watcher.py` | **[NEW — 2026-03-26 S2]** P4: polls issues.db every 30s, triggers immediate export on critical alerts. 2-min cooldown. Pi: `/opt/d3kos/services/alert_watcher.py` |
| `deployment/v0.9.4/pi_source/d3kos-alert-watcher.service` | **[NEW — 2026-03-26 S2]** systemd unit for alert_watcher.py. Pi: `/etc/systemd/system/d3kos-alert-watcher.service` |
| `deployment/v0.9.4/pi_source/os_lockdown.py` | **[NEW — 2026-03-26 S2]** DEP7: apt-mark hold on critical packages. Delivered via setup_lockdown cloud_agent command. Pi: `/opt/d3kos/services/os_lockdown.py` |
| `deployment/v0.9.4/pi_source/cloud_agent.py` | **[UPDATED — 2026-03-26 S2]** S2: handlers added for fix_my_pi, ota_upgrade, setup_lockdown. 6 commands total. Pi: `/opt/d3kos/services/cloud-agent/cloud_agent.py` |
| `atmyboat-forum: mobile/auth.php` | **[UPDATED — 2026-03-26 S2]** Added `amboat_auth_app_request()` for PWA Bearer app_token auth. |
| `atmyboat-forum: mobile/user-login.php` | **[NEW — 2026-03-26 S2]** PWA auth endpoint. POST credentials → app_token. Uses wp-load.php + wp_authenticate(). |
| `atmyboat-forum: mobile/dashboard-data.php` | **[NEW — 2026-03-26 S2]** GET last known boat state: synced_at, online, position, engine, system, alerts, boatlog. |
| `atmyboat-forum: mobile/list-vessels.php` | **[NEW — 2026-03-26 S2]** GET all paired Pi vessels for authenticated user. |
| `atmyboat-forum: mobile/version-registry.php` | **[UPDATED — 2026-03-26 S2]** sha256 field + latest_release block. download_url format updated. |
| `deployment/v0.9.4/pwa/index.html` | **[NEW — 2026-03-26 S2]** PWA SPA shell. 6 screens: login, vessel selector, dashboard, alerts, boatlog, settings. |
| `deployment/v0.9.4/pwa/app.css` | **[NEW — 2026-03-26 S2]** Dark marine theme. AODA AA contrast. 18px+ text. 48px touch targets. |
| `deployment/v0.9.4/pwa/app.js` | **[NEW — 2026-03-26 S2]** Vanilla JS SPA. API wrappers, screen renderers, auto-refresh, session persistence. |
| `deployment/v0.9.4/pwa/manifest.json` | **[NEW — 2026-03-26 S2]** PWA install manifest. |
| `deployment/v0.9.4/pwa/sw.js` | **[NEW — 2026-03-26 S2]** Service worker: cache-first static, network-first API. |
| `deployment/v0.9.4/pwa/icons/icon.svg` | **[UPDATED — 2026-03-26 S2C]** Self-contained SVG — AtMyBoat logo base64-embedded on dark navy (#0a1628) background. No external URL. CORS-safe for canvas PNG export. Deployed to `staging/app/icons/icon.svg`. |
| `deployment/v0.9.4/pwa/README.md` | **[NEW — 2026-03-26 S2]** GitHub Pages deploy instructions for PWA. |

## Session 2026-03-26 S2D Updates — Site Polish + Blog + Footer

| File | Description |
|------|-------------|
| `atmyboat-forum: header.php` | **[UPDATED — 2026-03-26 S2D]** Replaced hardcoded SVG compass with real AtMyBoat logo PNG (158×118px, vertically centered). |
| `atmyboat-forum: footer.php` | **[UPDATED — 2026-03-26 S2D]** Full rewrite — 5 columns (brand + Platform/Community/Resources/Legal), all 29 pages covered, `wp_nav_menu()` with hardcoded fallback, AtMyBoat logo PNG, Skipper Don in copyright. |
| `atmyboat-forum: functions.php` | **[UPDATED — 2026-03-26 S2D]** Registered 4 footer nav menu locations: footer-platform, footer-community, footer-resources, footer-legal. |
| `atmyboat-forum: style.css` | **[UPDATED — 2026-03-26 S2D]** Header logo CSS (158×118, centered), 5-col footer grid, footer-nav-list styles, full blog archive + single post CSS, footer link spacing halved, Skipper Don author line. |
| `atmyboat-forum: index.php` | **[NEW — 2026-03-26 S2D]** Blog archive template — dark theme, 3-col card grid, featured image, category badge, excerpt, pagination. Also handles search, category, tag archives. |
| `atmyboat-forum: single.php` | **[NEW — 2026-03-26 S2D]** Blog single post template — dark theme, back breadcrumb, featured image, formatted content (headings/blockquotes/code), tags, prev/next nav. |
| `atmyboat-forum: images/amboat-logo.png` | **[NEW — 2026-03-26 S2D]** AtMyBoat logo PNG stored in child theme (120×90, 65KB). Used in header and footer. Not dependent on media library. |
| `atmyboat-forum: page-privacy.php` | **[UPDATED — 2026-03-26 S2D]** "Donald Moskaluk" → "Skipper Don". |
| `atmyboat-forum: page-accessibility.php` | **[UPDATED — 2026-03-26 S2D]** "Don Moskaluk" → "Skipper Don". |

## Session 2026-03-26 S3 Updates — v0.9.4 QR Pairing, Command Polling, Version Check

| File | Description |
|------|-------------|
| `atmyboat-forum: mobile/pair-device-app.php` | **[NEW — 2026-03-26 S3]** AW2: PWA QR pairing endpoint. Bearer app_token auth. POST: pi_id + vessel_name + vessel_type → upserts d3kos_pairings (is_primary on first pairing) + queues pair_confirmed command. Staging: `/staging/wp-content/themes/twentytwenty-child/mobile/pair-device-app.php` |
| `atmyboat-forum: mobile/app-command.php` | **[NEW — 2026-03-26 S3]** AW4+AW5: App-to-Pi command endpoint. Bearer app_token auth. POST: write command (ota_upgrade, restart_service, reboot, fix_my_pi, export_now) → returns command_id. GET `?command_id=`: poll status + result. Separate from Pi-facing command-queue.php (which uses Pi API key auth). Staging: `/staging/wp-content/themes/twentytwenty-child/mobile/app-command.php` |
| `deployment/v0.9.4/pwa/app.js` | **[UPDATED — 2026-03-26 S3]** Added: screens.pair (QR scanning → vessel form → pairing), apiPairDevice(), apiPollCommand(), versionLessThan(), extractPiId(). Fixed: apiSendCommand now calls app-command.php (was command-queue.php — Pi auth, would have 401'd). OTA button now polls for completion. Version banner on dashboard. MB5 primary boat fix in loadVessels(). |
| `deployment/v0.9.4/pwa/app.css` | **[UPDATED — 2026-03-26 S3]** Added .update-banner style (green border, dark green bg). |
| `deployment/v0.9.4/pwa/index.html` | **[UPDATED — 2026-03-26 S3]** Added jsQR CDN script (v1.4.0, SRI integrity hash) for QR scanning in pair screen. |
| `deployment/v0.9.4/scripts/deploy-pwa.py` | **[NEW — 2026-03-26 S3]** FTPS deploy script for staging/app/ (PWA files). Reads FTP credentials from atmyboat-forum/.env. Usage: `python3 deployment/v0.9.4/scripts/deploy-pwa.py` from Helm-OS root. |

## Session 2026-03-27 S5 Updates — v0.9.4 Engine Detail, Alerts List, Boatlog List + Oil Pressure Fix + Battery Voltage Full Stack

| File | Description |
|------|-------------|
| `atmyboat-forum: mobile/engine-history.php` | **[NEW — 2026-03-27 S5]** Returns last 24h of engine snapshots ordered ASC for sparkline charts. Bearer app_token auth. `?pi=<uuid>`. SELECT: rpm, coolant_temp, oil_pressure_kpa, fuel_level_pct, engine_hours_h, battery_voltage_v. Up to 144 rows (1/10min). Staging: `/staging/wp-content/themes/twentytwenty-child/mobile/engine-history.php` |
| `atmyboat-forum: mobile/alerts-list.php` | **[NEW — 2026-03-27 S5]** Full paginated alert list. Bearer app_token auth. `?pi=&limit=&offset=`. Default 50, max 100. Returns total count + alerts array (id, alert_type, message, triggered_at). Staging: `/staging/wp-content/themes/twentytwenty-child/mobile/alerts-list.php` |
| `atmyboat-forum: mobile/boatlog-list.php` | **[NEW — 2026-03-27 S5]** Full paginated boatlog list. Bearer app_token auth. `?pi=&limit=&offset=`. Default 30, max 100. Returns total count + entries array (pi_entry_id, entry_type, content, entry_timestamp). Staging: `/staging/wp-content/themes/twentytwenty-child/mobile/boatlog-list.php` |
| `atmyboat-forum: mobile/dashboard-data.php` | **[UPDATED — 2026-03-27 S5]** Added oil_pressure_kpa and battery_voltage_v to engine snapshot SELECT. Both returned in engine object (oil_pressure, battery_voltage). Previously oil_pressure_kpa was stored but never retrieved — gap fixed. |
| `atmyboat-forum: mobile/data-ingress.php` | **[UPDATED — 2026-03-27 S5]** INSERT into amboat_engine_snapshots extended with battery_voltage_v column. Accepts engine.battery_voltage from Pi payload. bind_param: `'isidddd'` → `'isiddddd'`. |
| `atmyboat-forum: setup/mobile-schema.sql` | **[UPDATED — 2026-03-27 S5]** v0.9.4 S5 migration block: ALTER TABLE amboat_engine_snapshots ADD COLUMN battery_voltage_v DECIMAL(5,2) AFTER engine_hours_h. Don confirmed applied via phpMyAdmin. |
| `deployment/v0.9.4/pwa/app.js` | **[UPDATED — 2026-03-27 S5]** Added: apiEngineHistory(), apiAlertsList(), apiBoatlogList(), sparkline() SVG helper. screens.engine: current values card + 5 sparkline charts (RPM, coolant, oil press, battery, fuel) with conditional oil+battery series. screens.alerts: live fetch, color-coded type badges (ALERT_COLORS), tap to expand. screens.boatlog: live fetch, type badges (BOATLOG_TYPE_COLORS), tap to expand. Dashboard engine card: oil pressure + battery voltage stats added (conditional). |
| `deployment/v0.9.4/pwa/app.css` | **[UPDATED — 2026-03-27 S5]** Added: .sparkline-section, .sparkline-header, .sparkline-label, .sparkline-last, .sparkline-svg, .sparkline-range (engine charts). .alert-item-full, .alert-item-top, .alert-type-badge (alerts screen). .log-item-full, .log-item-top, .log-type-badge (boatlog screen). .list-footnote (shared). |
| `Pi: /opt/d3kos/services/export/export_categories.py` | **[UPDATED — 2026-03-27 S5 via SSH]** collect_engine() extended: fetches electrical/batteries/0/voltage from Signal K localhost:8099. Returns battery_voltage_v in engine dict. Backed up on Pi as .bak-s5battery. |
| `Pi: /opt/d3kos/services/export/export_worker.py` | **[UPDATED — 2026-03-27 S5 via SSH]** _build_ingress_payload() extended: forwards engine_cat['battery_voltage_v'] as engine['battery_voltage'] in POST body. Backed up on Pi as .bak-s5battery. |

## Session 2026-03-27 S6 Updates — v0.9.4 WebRTC Live Tunnel + PDF Engine Reports

| File | Description |
|------|-------------|
| `deployment/v0.9.4/pi_source/live_session.py` | **[NEW — 2026-03-27 S6]** Pi WebRTC tunnel service. aiortc-based. Polls rtc-signal.php every 3s. On offer: creates RTCPeerConnection, answers, opens data channel, sends 10-sensor JSON every 5s. Camera relay via MJPEGCameraTrack (aiortc MediaPlayer → WebRTC video track). Camera switching via data channel `camera_request` message. Reads pi_id from license.json (installation_id). Pi path: `/opt/d3kos/services/live/live_session.py` |
| `deployment/v0.9.4/pi_source/d3kos-live.service` | **[NEW — 2026-03-27 S6]** systemd unit for live_session.py. User=d3kos, WorkingDirectory=/opt/d3kos/services/live, Restart=on-failure. Enabled and running on Pi 192.168.1.237. Pi path: `/etc/systemd/system/d3kos-live.service` |
| `atmyboat-forum: mobile/rtc-signal.php` | **[NEW — 2026-03-27 S6]** WebRTC signaling relay. 6 actions: offer (app POST SDP+ICE → creates session row, returns session_id), poll_answer (app GET → returns Pi SDP+ICE when ready), app_ice (app POST trickle ICE), poll_offer (Pi GET → returns app offer), answer (Pi POST → inserts answer row), pi_ice (Pi POST trickle ICE). Sessions expire 5 min. Opportunistic cleanup on ~10% of requests. App auth: app_token. Pi auth: API key + device token. Staging: `mobile/rtc-signal.php` |
| `atmyboat-forum: mobile/pdf-engine-report.php` | **[NEW — 2026-03-27 S6]** PDF engine health report generator. POST, Bearer app_token. Aggregates all engine snapshots (all-time baseline + last-30-day). Calls Gemini 2.0 Flash with stats (not raw rows). Renders FPDF: cover page, RAG health badges, baseline vs 30d comparison table, alert history, Gemini narrative (4 sections), color-coded action items (URGENT/MONITOR/ROUTINE). AI disclaimer footer. Saves to `staging/app/reports/<uuid>.pdf`. Inserts metadata into amboat_pdf_reports. Staging: `mobile/pdf-engine-report.php` |
| `atmyboat-forum: mobile/list-reports.php` | **[NEW — 2026-03-27 S6]** Report library endpoint. GET, Bearer app_token. `?pi=&limit=&offset=`. Default 50, max 100. Returns `{total, reports:[{report_id, url, vessel_name, period_start, period_end, snapshot_count, file_size_kb, created_at}]}`. URL constructed as full HTTPS path. Staging: `mobile/list-reports.php` |
| `atmyboat-forum: mobile/fpdf/fpdf.php` | **[NEW — 2026-03-27 S6]** FPDF 1.86 vendored (no Composer required). Single-file PHP PDF library. From github.com/Setasign/FPDF. Staging: `mobile/fpdf/fpdf.php` |
| `deployment/v0.9.4/pwa/app.js` | **[UPDATED — 2026-03-27 S6]** Added: apiRtcOffer(), apiRtcPollAnswer(), apiRtcAppIce(), apiGenerateReport(), apiListReports(), fmtDate(). Go Live + My Reports quick-action row on dashboard. screens.live: WebRTC handshake via rtc-signal.php polling, 10-sensor grid (5s updates), connection UX messages (10s/30s/2min), camera panel with slot switcher, graceful disconnect. screens.reports: report library via list-reports.php, generate button, Web Share API with note prompt, Open PDF button. Helm-OS commit: ff7ed38 |
| `deployment/v0.9.4/pwa/app.css` | **[UPDATED — 2026-03-27 S6]** Added: .quick-actions, .btn-live, .btn-reports (dashboard quick actions). .screen-header, .screen-title, .back-btn (sub-screen navigation pattern). .live-status-bar (with .connected/.error states), .live-sensors-grid, .live-cell, .live-camera-panel, .cam-close-btn, .live-cam-row, .btn-cam-slot (live screen). .reports-total, .report-card, .report-meta, .report-btn-row (reports screen). Helm-OS commit: ff7ed38 |
| Schema SQL (delivered in chat — run in phpMyAdmin) | **[NEW — 2026-03-27 S6]** `amboat_rtc_sessions`: stores WebRTC offer/answer SDP + ICE, expires 5 min. `amboat_pdf_reports`: permanent PDF report library (report_id, user_id, pi_installation_id, vessel_name, file_path, file_size_kb, period_start, period_end, snapshot_count, created_at). Operator must run before testing. |

| `deployment/docs/MEDIA_CAPTURE_TRANSFER_SPEC.md` | **[NEW — 2026-03-27 S6]** Governing specification for all media capture, storage, Pi-to-app transfer, and deletion. Covers: existing camera API (port 8084), storage paths (/home/d3kos/camera-recordings/), WebRTC data channel binary chunking protocol, data channel message reference (complete), Pi MEDIA_README.txt manifest, 90% storage warning, app media library screen design, fish detection capture handling. Version 1.0. |

## Session 2026-03-27 S6b Updates — v0.9.4 User Test Fixes (pi_installation_id root cause + iOS binary + Reports guard)

| File | Description |
|------|-------------|
| `atmyboat-forum: mobile/data-ingress.php` | **[UPDATED — 2026-03-27 S6b]** CRITICAL root-cause fix: `$pi_installation_id` now reads from `$auth['device_token']` (authenticated UUID from d3kos_pairings.pi_id) instead of `$body['installation_id']` (license.json hex). This single change fixes: vessel showing Online in list-vessels.php, d3kOS version populating, alerts stored under correct key, boatlog stored under correct key, engine snapshots stored under correct key. Old stale rows stored under hex key deleted by operator via phpMyAdmin. Forum commit: 84a2438. |
| `atmyboat-forum: mobile/dashboard-data.php` | **[UPDATED — 2026-03-27 S6b]** Alert COUNT query was `WHERE user_id = ?` only — counted all 19 alerts for all vessels regardless of pi_id. Fixed: added pi_id conditional filter (same pattern as alert list SELECT above it). Dashboards now shows per-vessel alert count. Forum commit: 84a2438. |
| `atmyboat-forum: mobile/list-reports.php` | **[UPDATED — 2026-03-27 S6b]** `amboat_pdf_reports` table did not exist on staging → `$db->prepare()` returned false → PHP fatal error outputting HTML → app got "invalid response from server". Added guard: if `!$ct` return `{total:0, reports:[]}` gracefully. Forum commit: 752c12c. |
| `atmyboat-forum: mobile/rtc-signal.php` | **[UPDATED — 2026-03-27 S6b]** Two bugs fixed: (1) SDP bind_param type `'ssiis'` → `'ssiss'` — 4th param $sdp was bound as integer 'i', PHP cast every SDP string to 0. (2) ON DUPLICATE KEY UPDATE for answer action now includes `role = 'answer'` — without this, session stayed role='offer' and poll_offer returned it forever. Forum commit: 84a2438. |
| `deployment/v0.9.4/pi_source/live_session.py` | **[UPDATED — 2026-03-27 S6b]** Three bugs fixed: (1) Signal URL was missing full WP theme path — now uses `config['base_url'] + '/wp-content/themes/twentytwenty-child/mobile/rtc-signal.php'`. (2) ICE candidate format: browser sends `{"candidate": "candidate:xxx"}`, aiortc expects the string without `candidate:` prefix — fixed by `.replace('candidate:', '', 1).strip()`. (3) Pi reads `device_token` from `device-token.json` for identity instead of `installation_id` from `license.json`. Helm-OS commit: efb337d. |
| `deployment/v0.9.4/pwa/app.js` | **[UPDATED — 2026-03-27 S6b]** `dc.binaryType = 'arraybuffer'` added immediately after `pc.createDataChannel('sensors')`. Safari (iOS) defaults to Blob for binary WebRTC messages — without this, `evt.data instanceof ArrayBuffer` is false and all binary file transfers fail silently. Helm-OS commit: efb337d. |

## Session 2026-03-27 S6b-AODA — v0.9.3.1 PWA AODA Pass (font sizes + touch targets + aria-label)

| File | Description |
|------|-------------|
| `deployment/v0.9.4/pwa/app.css` | **[UPDATED — 2026-03-27 v0.9.3.1]** Full AODA pass. 30+ font-size violations corrected: readable text minimum 1rem, supplemental labels/badges (nav badge, card title, stat labels, timestamps, tier badge, locked badge, sparkline range, media meta, live cell labels) minimum 0.9rem. Touch target violations corrected: nav buttons, back button, cam slot buttons, capture/record/media lib buttons, cam close button, vessel icon, position link, vessel switcher item — all minimum 48×48px. Added `font-family: inherit` and `min-height: 48px` to `.btn-live`, `.btn-reports`. Added `:focus-visible` outline on `#header-vessel.vessel-switcher`. Deployed to `staging/app/`. Helm-OS commit: ec94e4a. |
| `deployment/v0.9.4/pwa/app.js` | **[UPDATED — 2026-03-27 v0.9.3.1]** `updateHeader()`: `#online-dot` now receives `aria-label="Vessel online"` or `"Vessel offline"` on every status change. Screen readers now announce live vessel connection status. `#header-vessel.vessel-switcher` role/tabindex/aria-label/keyboard handler already correct (no change). Deployed to `staging/app/`. Helm-OS commit: ec94e4a. |

## Session 2026-03-27 S6c Updates — v0.9.4 TURN relay, camera live feed, stream service alert storm

| File | Change |
|------|--------|
| `deployment/v0.9.4/pi_source/live_session.py` | **[UPDATED — 2026-03-27 S6c]** (1) aioice timeout patch: `get_component_candidates` default timeout extended 5s→12s via monkey-patch at import — TURN relay allocation takes 5.11s and was silently cancelled. (2) TURN URL corrected from `atmyboat.metered.live` (Azure API domain, not a relay) to `a.relay.metered.ca:3478`. (3) ICE gathering wait extended 8s→15s. (4) Log ALL ICE candidates with relay count. (5) `asyncio.ensure_future(video_sender.replaceTrack(...))` → `video_sender.replaceTrack(...)` — replaceTrack is synchronous in aiortc 1.x; ensure_future(None) raised TypeError closing the WebRTC session on every camera tap. Pi deployed: `/opt/d3kos/services/live/live_session.py` |
| `deployment/v0.9.4/pi_source/tier_service.py` | **[UPDATED — 2026-03-27 S6c]** (1) Added `camera: True` to T1/T2/T3 feature matrices (T0: False). (2) Added `/tier/feature/<name>` GET route returning `{"feature": "...", "enabled": bool}`. d3kos-camera-stream.service ExecStartPre was calling this missing route, causing 131-alert crash loop. Pi deployed: `/opt/d3kos/services/tier/tier_service.py` |
| `deployment/v0.9.4/pi_source/camera_stream_manager.py` | **[UPDATED — 2026-03-27 S6c]** (1) Added `Response` to Flask imports. (2) Added `/camera/stream/hw/<hardware_id>` MJPEG stream endpoint — serves Pi-cached frames from `hw_state` dict as `multipart/x-mixed-replace; boundary=frame` at ~10fps. This is the URL that `live_session.py`'s `get_camera_url()` returns; without it, MediaPlayer received 404 and fell back to blank YUV frame (green screen). Pi deployed: `/opt/d3kos/services/marine-vision/camera_stream_manager.py` |
| `atmyboat-forum: mobile/turn-credentials.php` | **[UPDATED — 2026-03-27 S6c]** TURN URLs corrected from `atmyboat.metered.live` to `a.relay.metered.ca` (actual relay infrastructure). Deployed to HostPapa staging via FTPS. |

## Session 2026-03-27 S7 Updates — Roadmap planning

No new files deployed this session. Checklist and governance updates only:

| File | Description |
|------|-------------|
| `PROJECT_CHECKLIST.md` | **[UPDATED — 2026-03-27 S7]** Added Parts 8B–8F (v0.9.5–v0.9.9 roadmap sections). Added Part 7A (pre-deployment architecture diagram + credential audit). Added Phase 3B (Gemini AI security hardening GS1–GS6, Stripe E2E testing ST1–ST7). Added Part 6 item 22 (Pi boot splash). Added DEP11–DEP12 (brand asset consistency). Updated Part 10 roadmap table. |
| `SESSION_LOG.md` | **[UPDATED — 2026-03-27 S7]** Session S7 entry appended — roadmap research, version planning decisions. |

## Session 2026-03-28 S8 + S8b Updates — Pi AODA, Settings index bar, AvNav persistence, tier-api mask

| File | Description |
|------|-------------|
| Pi: `d3kos-touch.css` + Flask `d3kos.css` | **[UPDATED — 2026-03-28 S8]** Full WCAG 2.0 AA pass on all 20 static HTML pages and 12 Flask templates. 26 font-size violations fixed (floor 18px / 0.9rem). Skip-to-content links, id="main-content", focus-visible indicators, 48px touch targets on all interactive elements. |
| Pi: `settings.html` (Flask template) | **[UPDATED — 2026-03-28 S8]** 17-pill section index bar added (sticky, IntersectionObserver highlights active section). Status bar indicators (`<div class="indicators">`) removed. |
| Pi: `index.html` (Flask template) | **[UPDATED — 2026-03-28 S8b]** `allow="autoplay"` added to AvNav iframe — fixes sound dialog on every load. |
| Pi: `/var/lib/avnav/user/viewer/user.js` | **[UPDATED — 2026-03-28 S8b]** startNavPage + lastChart localStorage management — AvNav now opens directly to last viewed OSM chart instead of chart-selection dialog. |
| Pi: `/etc/systemd/system/d3kos-tier-api.service` | **[UPDATED — 2026-03-28 S8b]** Real file deleted; /dev/null symlink created (permanent mask). Eliminates port 8093 conflict with d3kos-tier.service. |
| HostPapa: `staging/app/sw.js` | **[UPDATED — 2026-03-28 S8b]** CACHE_NAME `d3kos-pwa-v1` → `v2`. Forced all client phones to fetch updated assets. |

## Session 2026-04-01 S9 + S9b Updates — Fix My Pi E2E verified, DEP3, DEP5, watchdog, admin tools

| File | Description |
|------|-------------|
| HostPapa: `staging/.../mobile/file-manifest.php` | **[NEW — 2026-04-01 S9]** DEP3 complete. SHA-256 + size manifest for 11 core Pi service files. Pi-facing auth (amboat_auth_pi_request). Hashes regenerated to match current Pi state. Fix My Pi downloads this and compares against actual files — verified working: correctly detected 2 mismatches on Don's phone. Must be regenerated after every Pi service file change. |
| HostPapa: `staging/.../page-admin-tools.php` | **[NEW — 2026-04-01 S9]** WordPress admin-only tools page. Features: user/tier table, set-tier dropdown (T0–T3), reset FMP counter, clear alerts, manual command queue, pending queue display. WP nonce protection. Staging-only banner. Confirmed working by operator. |
| HostPapa: `staging/.../mobile/watchdog-alert.php` | **[NEW — 2026-04-01 S9b]** Receives POST from Pi watchdog when a service fails and won't restart. Looks up account holder email via user_id from d3kos_pairings. Sends wp_mail() with vessel name + service details. Also inserts watchdog_failure into amboat_alerts. No SMTP on Pi required. |
| HostPapa: `staging/.../mobile/fix-my-pi-app.php` | **[UPDATED — 2026-04-01 S9]** T1 tier: detects placeholder Stripe keys and queues command directly (test_mode:true) for testing without live Stripe credentials. Real Stripe flow unchanged. |
| HostPapa: `staging/app/sw.js` | **[UPDATED — 2026-04-01 S9]** CACHE_NAME `d3kos-pwa-v2` → `v3`. Forced cache refresh after app.js changes. |
| HostPapa: `staging/app/app.js` | **[UPDATED — 2026-04-01 S9]** Three changes: (1) fmtTime() appends 'Z' to bare datetime strings — fixes timestamps showing server time instead of phone local time. (2) DEP5: "Update All Vessels" block (T3 only, 2+ vessels, per-Pi progress). (3) T1 Fix My Pi: opens Stripe checkout_url in new tab when present, falls through to progress screen in test mode. |
| Pi: `/opt/d3kos/services/watchdog/d3kos_watchdog.py` | **[NEW — 2026-04-01 S9b]** Cron watchdog (*/5 min). Checks 10 critical services. Auto-restart on failure (sudo systemctl restart). On persistent failure: POSTs to watchdog-alert.php on HostPapa — no SMTP on Pi. 30-min alert cooldown per service. Reads credentials from cloud-config.json + device-token.json. |
| Pi: `/opt/d3kos/config/watchdog-config.json` | **[NEW — 2026-04-01 S9b]** Minimal config: cooldown_minutes + notify_on_auto_restart. No email credentials needed. |
| Pi: `/etc/sudoers.d/d3kos-watchdog` | **[NEW — 2026-04-01 S9]** NOPASSWD restart rules for all 10 watchdog-managed services. |
| Pi: `/opt/d3kos/services/cloud-agent/cloud_agent.py` | **[UPDATED — 2026-04-01 S9]** sys.path fix (cloud-agent dir at position 0, services at 1). run_diagnostics() now called with 3 params: base_url, api_key, device_token. |
| Pi: `/opt/d3kos/services/cloud-agent/fix_my_pi.py` | **[UPDATED — 2026-04-01 S9]** DEP3: check_file_integrity() added. Downloads file-manifest.php from HostPapa, compares SHA-256 of each file on Pi. Reports mismatches in diagnostic result. run_diagnostics() signature updated to accept base_url, api_key, device_token. |
| Pi: `/opt/d3kos/services/export/export_worker.py` | **[UPDATED — 2026-04-01 S9]** INTERNAL_ALERT_TYPES filter added: service_down, service_restart, high_memory, high_cpu categories suppressed from HostPapa export. Eliminates spurious alert flood (720 alerts in this session). |
| Pi: `/opt/d3kos/services/self-healing/issue_detector.py` | **[UPDATED — 2026-04-01 S9]** Removed `d3kos-tier-api` from critical_services list — service is permanently masked, was generating continuous false alerts. |
| Helm-OS repo: `deployment/v0.9.4/pi/watchdog/` | **[NEW — 2026-04-01 S9b]** New directory: d3kos_watchdog.py + watchdog-config.template.json. Source-of-record for Pi watchdog cron. |


## Session 2026-04-01 S11 Updates — PDF Reports end-to-end working (jsPDF architecture)

| File | Description |
|------|-------------|
| HostPapa: `staging/.../mobile/pdf-analyze.php` | **[NEW — 2026-04-01 S11]** Gemini AI analysis endpoint. POST, Bearer app_token. Receives `vessel_summary` JSON from phone. Builds structured prompt and calls Gemini API (model from GEMINI_MODEL constant, default gemini-2.0-flash). JSON extraction uses strpos/strrpos (not regex) to handle Gemini wrapping text around JSON response. Returns `{analysis, recommendations[{issue, action}]}`. Graceful fallback if Gemini parse fails — never returns 500. |
| HostPapa: `staging/.../mobile/pdf-store.php` | **[NEW — 2026-04-01 S11]** PDF binary storage endpoint. POST, Bearer app_token. Receives base64-encoded PDF from phone, verifies Pi is paired to user via d3kos_pairings, saves to `staging/app/reports/RPT-YYYYMMDD-XXXXXXXX.pdf`, inserts into `amboat_pdf_reports` (without file_size_kb — column does not exist on staging). Returns `{report_id, url, vessel_name, created_at}`. |
| HostPapa: `staging/.../mobile/list-reports.php` | **[UPDATED — 2026-04-01 S11]** Removed `file_size_kb` from both SELECT queries (COUNT and paginated rows). Column does not exist in staging `amboat_pdf_reports` — its presence caused MySQL "Unknown column" error, making the endpoint return failure and the report library appear empty. `file_size_kb` is now hardcoded to `null` in the output array. |
| HostPapa: `staging/app/index.html` | **[UPDATED — 2026-04-01 S11]** Added jsPDF 2.5.1 CDN script tag (`cdn.jsdelivr.net/npm/jspdf@2.5.1/dist/jspdf.umd.min.js`) before app.js. No SRI hash (jsPDF UMD bundle hash varies). |
| HostPapa: `staging/app/app.js` | **[UPDATED — 2026-04-01 S11]** PDF report section fully rewritten. (1) `apiAnalyseReport()` POSTs vessel_summary to pdf-analyze.php and returns `{analysis, recommendations}`. (2) `apiStoreReport()` uploads base64 PDF binary to pdf-store.php. (3) `generateReport()` fetches dashboard-data + alerts-list + engine-history in parallel (Promise.allSettled), builds vesselSummary, calls Gemini, generates PDF with jsPDF (`window.jspdf.jsPDF`), uploads binary. (4) `saveReport()` fetches PDF as Blob, calls `navigator.share({files:[...]})` — opens system share sheet. Falls back to anchor download if Web Share API unavailable. (5) `renderReportList()` — removed "Open PDF" button (window.open mobile trap), replaced with single "Save / Share" button. |
| HostPapa: `staging/app/sw.js` | **[UPDATED — 2026-04-01 S11]** CACHE_NAME `d3kos-pwa-v6` → `v7`. v6 was broken: jsPDF CDN URL was incorrectly added to STATIC_ASSETS — `cache.addAll()` aborts entire SW installation if any resource fails. CDN URLs must never be in STATIC_ASSETS. v7 has local assets only. |


## Session 2026-04-01 S12 Updates — Pi stability: Ollama death loop + Node-RED dead tabs

| File | Description |
|------|-------------|
| Pi: `/opt/d3kos/services/gemini-nav/gemini_proxy.py` | **[UPDATED — 2026-04-01 S12]** Removed entire Ollama fallback: `query_ollama()` function, `check_ollama()` function, `OLLAMA_URL` and `OLLAMA_MODEL` constants, Route 2 fallback block in `/ask` endpoint, ollama fields from `/status` endpoint. When Gemini unavailable → 503 immediately. Pi cannot run LLMs — fallback was the root cause of system overload and Pi reboot. |
| Pi: `/opt/d3kos/services/gemini-nav/config/gemini.env` | **[UPDATED — 2026-04-01 S12]** Removed `OLLAMA_URL` and `OLLAMA_MODEL` lines. Both were pointing to `http://127.0.0.1:11434` (Pi local Ollama) which triggered the death loop. |
| Pi: `/home/d3kos/.node-red/flows.json` | **[UPDATED — 2026-04-01 S12]** Deleted 4 dead tabs and all 22 associated nodes: (1) d3kOS Cloud Telemetry Push — pointed to non-existent HostPapa endpoint, consumed 63% CPU; (2) Community Engine Benchmark — never built; (3) Community Boat Map — never built; (4) Community Knowledge Log — Watch node missing `files` property → constant error loop. System tab only remains. |
| Pi: Ollama systemd service | **[DISABLED — 2026-04-01 S12]** `sudo systemctl disable ollama.service`. Binary and phi3.5 model remain installed. Will not auto-start on reboot. |
| Helm-OS: `deployment/v0.9.4/pi-fixes/fix_gemini_proxy.py` | **[NEW — 2026-04-01 S12]** Reusable Python script. Backs up and patches gemini_proxy.py + gemini.env on Pi. Removes all Ollama code. Use if Pi is ever re-imaged and old service files restored. |
| Helm-OS: `deployment/v0.9.4/pi-fixes/fix_nodered_flows.py` | **[NEW — 2026-04-01 S12]** Reusable Python script. Reads flows.json, removes 4 dead tabs by label, writes cleaned version. Keeps System tab only. |


## Session 2026-04-01 S12b Updates — Memory backup + skills commands restored

| File | Description |
|------|-------------|
| Backup: `.aao-backups/20260401_192758_S12/.claude/projects/-home-boatiq/memory/` | **[BACKUP — 2026-04-01 S12b]** Full snapshot of all 16 Claude memory files taken before MEMORY.md reorganisation. Files: MEMORY.md.bak + 15 topic files (.bak). Restore by copying .bak files back to `/home/boatiq/.claude/projects/-home-boatiq/memory/` and removing the .bak extension. |
| `~/.claude/skills/session-start/SKILL.md` | **[NEW — 2026-04-01 S12b]** Migrated from ~/.claude/commands/ to skills format. Restores /session-start shortcut in Claude Code slash command list. |
| `~/.claude/skills/session-close/SKILL.md` | **[NEW — 2026-04-01 S12b]** Migrated from ~/.claude/commands/ to skills format. Restores /session-close shortcut in Claude Code slash command list. |
| `~/.claude/skills/methodology-check/SKILL.md` | **[NEW — 2026-04-01 S12b]** Migrated from ~/.claude/commands/ to skills format. Restores /methodology-check shortcut in Claude Code slash command list. |
| `~/.claude/skills/bug-fix/SKILL.md` | **[NEW — 2026-04-01 S12b]** Migrated from ~/.claude/commands/ to skills format. Restores /bug-fix shortcut in Claude Code slash command list. |


## Session 2026-04-01 S13 Updates — Gemini AI Security Hardening (GS1–GS5) + OWASP Documentation

| File | Description |
|------|-------------|
| HostPapa: `staging/.../inc/ai-assistant.php` | **[UPDATED — 2026-04-01 S13]** Full security hardening. GS1: system prompt hardened with explicit refusal rules for role-play overrides, instruction bypass, topic redirect. GS2 (direct): `detect_injection()` — 28 patterns blocked before Gemini call, logged as security event. GS2 (indirect): forum context screened for same 28 patterns before entering Gemini prompt — contaminated threads skipped. GS3: `filter_output()` — 11 regex patterns block code execution/hex payloads; URL allowlist (18 trusted marine domains) strips unlisted URLs. GS4: `check_rate_limit()` / `increment_rate_limit()` — 20 req/hour + 50 req/day per hashed IP via WP transients. GS5: `sanitize_input()` — Unicode zero-width char removal, transliterator homoglyph normalization, null bytes, HTML strip, 500-char cap. Context cap: forum context capped at 2000 chars to prevent token stuffing. |
| HostPapa: `staging/.../logs/.htaccess` | **[NEW — 2026-04-01 S13]** `Deny from all` — blocks public browser access to ai-usage.log. |
| Helm-OS: `deployment/docs/SECURITY_OWASP_LLM.md` | **[NEW — 2026-04-01 S13]** OWASP LLM Top 10 assessment for the AtMyBoat.com AI assistant. Covers LLM01–LLM10 with status (mitigated / N/A / accepted), implementation details, residual risks, and GS6 adversarial test cases. Includes credential rotation checklist for Phase 4 live push. |
| HostPapa: `staging/.../page-accessibility.php` | **[UPDATED — 2026-04-01 S14]** Added compliance badges (AODA, WCAG 2.0 AA, OWASP Security Guidelines, IEC 62288). Added "Security Practices" section with 6 cards (AI protection, privacy, rate limiting, payments, input validation, HTTPS). Updated date to April 2026. |


## Session 2026-04-02 S15 Updates — Pre-Phase-4 Prep Sprint (CA, AD, DEP, GS6, Boot Splash)

| File | Description |
|------|-------------|
| Helm-OS: `deployment/docs/ARCH_SERVICE_MAP.md` | **[NEW — 2026-04-02 S15]** AD1 complete. Full service map: all Pi ports (3000, 8084, 8086, 8093–8111, 8095, 8099, 8103, 8107, 8111), all HostPapa PHP endpoints, PWA endpoints, external services (Stripe, Gemini, STUN/TURN, Signal K). |
| Helm-OS: `deployment/docs/ARCH_DATA_FLOW.md` | **[NEW — 2026-04-02 S15]** AD2 complete. Pi export pipeline: export_worker.py → data-ingress.php → amboat_vessel_data → dashboard-data.php → PWA. Alert flow: alert_watcher → export → HostPapa → PWA push. Node-RED community flows. |
| Helm-OS: `deployment/docs/ARCH_WEBRTC_PATH.md` | **[NEW — 2026-04-02 S15]** AD3 complete. Full ICE/STUN/TURN sequence: PWA → turn-credentials.php → STUN gather → CGNAT traversal → TURN fallback → Pi live_session.py aiortc → data channel open. |
| Helm-OS: `deployment/docs/ARCH_PAYMENT_FLOW.md` | **[NEW — 2026-04-02 S15]** AD4 complete. Stripe Checkout → webhook → tier DB update → Pi cloud_agent sync → license.json. Fix My Pi payment flow: app-command.php → Stripe charge → command queue → fix_my_pi.py → result → auto-refund on timeout. |
| Helm-OS: `deployment/docs/ARCH_CREDENTIAL_MAP.md` | **[NEW — 2026-04-02 S15]** AD5 complete. All 13 credentials mapped: owner service, consuming services, storage location (Pi config / HostPapa PHP / Stripe dashboard). No actual values — map only. |
| Helm-OS: `deployment/v0.9.3/CREDENTIAL_ROTATION_CHECKLIST.md` | **[NEW — 2026-04-02 S15]** CA2 checklist. Full pre-launch credential rotation: Stripe live keys (3 items), Gemini API key, AMBOAT_API_KEY, FTP password, WordPress admin, Metered TURN. Post-rotation smoke test steps. Operator action required before Phase 4. |
| Helm-OS: `deployment/scripts/generate_manifest.py` | **[NEW — 2026-04-02 S15]** DEP19 complete. Maps 11 Pi service files (Pi path → local repo path). Computes SHA-256 + size. Regenerates `mobile/file-manifest.php` automatically. Run `python3 deployment/scripts/generate_manifest.py` after every Pi service file deploy. |
| Helm-OS: `deployment/features/boot-splash/theme/d3kos.plymouth` | **[NEW — 2026-04-02 S15]** Plymouth theme descriptor. ModuleName=script. ImageDir + ScriptFile set to /usr/share/plymouth/themes/d3kos/. |
| Helm-OS: `deployment/features/boot-splash/theme/d3kos.script` | **[NEW — 2026-04-02 S15]** Plymouth Script plugin. Navy background (#0a1628). amboat-logo.png at 20% screen width, centred -40px from middle. Version text "d3kOS v0.9.4". Copyright "© AtMyBoat.com". Progress bar in AtMyBoat blue. |
| Helm-OS: `deployment/features/boot-splash/theme/amboat-logo.png` | **[NEW — 2026-04-02 S15]** Logo asset for Pi boot splash. Copied from wp-content/themes/twentytwenty-child/images/. Source-of-record in Helm-OS. Also deployed to Pi at /usr/share/plymouth/themes/d3kos/amboat-logo.png. |
| Helm-OS: `deployment/features/boot-splash/deploy-boot-splash.sh` | **[NEW — 2026-04-02 S15]** DEP12 deployment script. Installs Plymouth if missing, copies 3 theme files, registers via update-alternatives, rebuilds initramfs, patches cmdline.txt. Executed successfully 2026-04-02. Boot splash active — visible on next Pi reboot. |
| Helm-OS: `deployment/d3kOS/dashboard/static/images/amboat-logo.png` | **[NEW — 2026-04-02 S15]** DEP11. Logo for Pi dashboard header. Copied from atmyboat-forum canonical source. Served by Flask at /static/images/. |
| Helm-OS: `deployment/d3kOS/dashboard/templates/index.html` | **[UPDATED — 2026-04-02 S15]** DEP11. `.sb-brand` element changed from text `d3kOS` to `<img>` tag referencing amboat-logo.png. Height 28px, width auto. |
| Helm-OS: `deployment/d3kOS/dashboard/static/css/d3kos.css` | **[UPDATED — 2026-04-02 S15]** DEP11. `.sb-brand` CSS changed from Bebas Neue font to `height:28px; width:auto; flex-shrink:0`. |
| Helm-OS: `deployment/v0.9.4/pwa/icons/icon-192.png` | **[NEW — 2026-04-02 S15]** PWA maskable icon 192×192px. AmBoat logo on navy #0a1628 background, 15% padding safe zone. Generated via Node.js + sharp. |
| Helm-OS: `deployment/v0.9.4/pwa/icons/icon-512.png` | **[NEW — 2026-04-02 S15]** PWA maskable icon 512×512px. Same generation as icon-192.png. Source-of-record in Helm-OS; upload to `staging/app/icons/` via cPanel when deploying. |
| atmyboat-forum: `.gitignore` | **[UPDATED — 2026-04-02 S15]** CA3. Added `*-diag.php` and `check-*.php` patterns. Prevents diagnostic test files from being staged/committed. |
| atmyboat-forum: `.git/hooks/pre-commit` | **[NEW — 2026-04-02 S15]** CA5 complete. Blocks 8 credential patterns: Stripe live keys, Stripe test keys, webhook secrets, Gemini API key, AMBOAT_API_KEY, Anthropic keys, OpenAI keys, Metered TURN credentials. Executable. |
| atmyboat-forum: `inc/atmyboat-config.php` | **[UPDATED — 2026-04-02 S15]** GEMINI_MODEL constant updated from `gemini-2.0-flash` to `gemini-2.5-flash`. gemini-2.0-flash returns 404 on new Google Cloud accounts (model sunset for new users). gemini-2.5-flash confirmed working on staging. |
| atmyboat-forum: `mobile/file-manifest.php` | **[UPDATED — 2026-04-02 S15]** Regenerated by generate_manifest.py. 11 files, all SHA-256 hashes current, generated 2026-04-02T18:30:40Z. Do not edit manually — use generate_manifest.py. |


## Session 2026-04-06 S18 Updates — P7 pair_confirmed + RAG PDF Ingestion

| File | Description |
|------|-------------|
| Helm-OS: `deployment/v0.9.4/pi_source/cloud_agent.py` | **[UPDATED — 2026-04-06 S18]** P7 complete. Added `handle_pair_confirmed()` — writes string tier ("T1") to license.json, triggers best-effort export, single clean ack. Added `pair_confirmed` case to `dispatch()`. Updated module docstring. Bug fixed: Pi previously had handler that wrote integer tier (1) and double-acked via handle_export_now. |
| Pi: `/opt/d3kos/services/cloud-agent/cloud_agent.py` | **[DEPLOYED — 2026-04-06 S18]** Fixed handle_pair_confirmed deployed. Backup at `.bak.pre-p7`. Service d3kos-cloud-agent restarted, status=active. TDD: 3/3 assertions passed on Pi. |
| Pi: `/opt/d3kos/data/vector-db/` | **[UPDATED — 2026-04-06 S18]** RAG ChromaDB updated. 688 new chunks added: Ontario Regulation 2026.pdf (682 chunks, 137 pages — actual size limits, bag limits, zone rules), global_marine_emergency_contacts.pdf (6 chunks). MNR.pdf was already indexed. Total d3kos_documents collection: ~2,028 docs. |
| Pi: `/opt/d3kos/data/pdf-metadata.json` | **[UPDATED — 2026-04-06 S18]** 2 new entries: ontario_reg_2026.pdf and global_marine_emergency_contacts.pdf. |


## Session 2026-04-06 S19 Updates — Hotfixes: tier display, PDF crash, duplicate usermeta

| File | Description |
|------|-------------|
| Helm-OS: `deployment/v0.9.4/pi_source/tier_service.py` | **[UPDATED — 2026-04-06 S19]** Added `_parse_tier()` helper. Handles both `"T0"` string and `0` integer formats from license.json. Two `int()` call sites at lines ~137 and ~154 replaced with `_parse_tier()`. Fixes ValueError crash that caused tier to display as "3". Synced from Pi. |
| HostPapa: `mobile/admin-api.php` | **[UPDATED — 2026-04-06 S19]** `update_tier` action: replaced INSERT ON DUPLICATE KEY UPDATE with SELECT→UPDATE/INSERT + DELETE-duplicates pattern. Prevents silent duplicate `atmyboat_tier` rows in `wpax_usermeta`. Root cause of "tier showing 3" confirmed as S16 Admin CRM P6 testing inserting duplicate rows on 2026-04-03. Don ran cleanup SQL to remove duplicates. |
| HostPapa MySQL: `amboat_pdf_reports.report_id` | **[HOTFIX — 2026-04-06 S19]** Column type changed INT → BIGINT UNSIGNED via `ALTER TABLE amboat_pdf_reports MODIFY report_id BIGINT UNSIGNED AUTO_INCREMENT`. Root cause: column reached INT32_MAX (2,147,483,647) — PHP fatal error on INSERT → no response body → PWA reported "Invalid response from server". PDF generation now working (returns "no engine data" — expected until Pi is on water). |


## Session 2026-04-07 S20 — v0.9.5 Predictive Alert Integration + AI Bridge Fix

| File | Description |
|------|-------------|
| Helm-OS: `deployment/v0.9.4/pi_source/predictive_maintenance.py` | **[UPDATED — S20]** Added `_notify_ai_bridge()` — POSTs WATCH/ALERT to AI bridge `/webhook/alert` for TTS + SSE ticker. Direct Piper kept as fallback. ALERT=critical, WATCH=warning severity. |
| Pi: `/opt/d3kos/services/predictive/predictive_maintenance.py` | **[DEPLOYED — S20]** As above. Service restarted. |
| Helm-OS: `deployment/v0.9.4/pi_source/ai-bridge.js` | **[ADDED — S20]** Repo copy. Added `custom_alert` SSE handler calling `_setAlertTicker()` (instruments.js function) to update dashboard status bar ticker with ⚠ prefix on predictive alerts. |
| Pi: `/opt/d3kos/services/dashboard/static/js/ai-bridge.js` | **[UPDATED — S20]** As above. |
| Helm-OS: `deployment/v0.9.4/pi_source/engine-monitor.html` | **[ADDED — S20]** Repo copy. Added Predictive Health section (section 2) between Engine and Tank Levels — 4 eng-cell cards (Overall, Coolant, Oil Press, RPM Trend). WATCH→adv CSS, ALERT→crit CSS. Polls /predictive/status every 60s. |
| Pi: `/opt/d3kos/services/dashboard/templates/engine-monitor.html` | **[UPDATED — S20]** As above. |
| Helm-OS: `deployment/v0.9.4/pi_source/d3kos_watchdog.py` | **[UPDATED — S20]** Added d3kos-ai-bridge to CRITICAL_SERVICES with auto_restart=True. |
| Pi: `/opt/d3kos/services/watchdog/d3kos_watchdog.py` | **[DEPLOYED — S20]** As above. |
| Pi: `/opt/d3kos/services/ai-bridge/config/ai-bridge.env` | **[UPDATED — S20]** TTS_ENGINE: espeak-ng → piper. Pi-only (config file, not in repo). |
| Pi: `systemd d3kos-ai-bridge.service` | **[ENABLED — S20]** `systemctl enable` run. Service now starts on every boot. Previously disabled — never registered since service was built March 19. |

## Session 2026-04-07 S21 — v0.9.5 Post-Release Fixes: Piper Voice + Persistent Mute + DB Cleanup

| File | Description |
|------|-------------|
| Helm-OS: `deployment/v0.9.4/pi_source/ai-bridge-tts.py` | **[UPDATED — S21]** `_piper()`: removed 20-second `communicate()` timeout — Piper was timing out under Pi load and falling back to espeak-ng (male voice). Added piper process + aplay process to `_active_procs` for kill-on-mute. Matches voice-assistant-hybrid.py behavior. |
| Pi: `/opt/d3kos/services/ai-bridge/utils/tts.py` | **[DEPLOYED — S21]** As above. |
| Helm-OS: `deployment/v0.9.4/pi_source/ai_bridge.py` | **[UPDATED — S21]** Added `MUTE_STATE_FILE = '/opt/d3kos/config/tts-mute.json'`. `helm_mute()` endpoint now writes mute state to file on every toggle. `_start_background_services()` reads saved state on startup. HELM mute now survives service restarts. |
| Pi: `/opt/d3kos/services/ai-bridge/ai_bridge.py` | **[DEPLOYED — S21]** As above. |
| Pi: `/opt/d3kos/data/predictive/engine_history.db` | **[DATA CLEANUP — S21]** Deleted 2,000 rows WHERE source='test'. 131 production (signalk) rows remain. Clears repeating alert condition caused by TDD test data still in production DB. |

## v0.9.6 Fleet Management — Phase 1 Backend Complete (S21b 2026-04-07)

| File | Description |
|------|-------------|
| `deployment/features/fleet-management/BUILD_CHECKLIST.md` | **[NEW — S21]** Full v0.9.6 build checklist. Phase 1 backend complete S21b (17/17 tests passed). |
| `deployment/features/fleet-management/php/fleet-setup.php` | **[NEW — S21]** One-shot staging setup: create_tables, seed_test (15 boats × 60 min), verify, create_test_user, cleanup_test. Protected by FLEET_SETUP_KEY. Delete after testing. |
| `deployment/features/fleet-management/php/fleet-create.php` | **[NEW — S21]** POST — creates fleet, returns 6-char fleet_code. T3 gate. One fleet per device. |
| `deployment/features/fleet-management/php/fleet-join.php` | **[NEW — S21]** POST — joins fleet by fleet_code. 15-vessel cap enforced. T3 gate. |
| `deployment/features/fleet-management/php/fleet-ingest.php` | **[NEW — S21]** POST — Pi position + engine push. AMBOAT_API_KEY + X-Device-Token auth. 50s rate limit. Prunes 24h/7d. |
| `deployment/features/fleet-management/php/fleet-map.php` | **[NEW — S21]** GET — last-known positions for all fleet vessels. app_token Bearer auth. T3 gate. |
| `deployment/features/fleet-management/php/fleet-analytics.php` | **[UPDATED — S27b]** GET — per-vessel engine hours, avg RPM/coolant/oil, fleet summary + alerts_30d per vessel (30-day alert history from amboat_alerts). T3 gate. |
| `deployment/features/fleet-management/pi_source/fleet_push_service.py` | **[NEW — S21]** Pi Fleet Push Service (Port 8107). 1-min push loop, idles when inactive. Reads fleet.json + license.json + device-token.json. GPS via SignalK :8099, engine via :8106. |
| `deployment/features/fleet-management/pi_source/d3kos-fleet-push.service` | **[NEW — S21]** systemd unit for fleet_push_service.py. User=d3kos, EnvironmentFile=fleet-push.env. Pending Pi deploy. |
| `deployment/features/fleet-management/scripts/deploy-fleet-php.py` | **[UPDATED — S23]** FTPS deploy script — now includes fleet-status.php + fleet-leave.php (8 files total). |
| `deployment/features/fleet-management/scripts/test_fleet_e2e.py` | **[NEW — S21]** End-to-end test: fleet-map (15 positions, Toronto area), fleet-analytics (engine hours, RPM), tier gate (401). ALL 17 TESTS PASSED 2026-04-07. |
| `deployment/features/fleet-management/php/fleet-status.php` | **[NEW — S23]** GET — returns device's current fleet membership (fleet_id, fleet_code, name, type, role, member_count) or null. app_token Bearer auth. |
| `deployment/features/fleet-management/php/fleet-leave.php` | **[NEW — S23]** POST — owner deletes fleet+all data; member removes self. Enqueues fleet_unassign to Pi command queue. app_token Bearer auth. |
| `deployment/features/fleet-management/php/fleet-create.php` | **[UPDATED — S23]** Now enqueues fleet_assign command to amboat_command_queue after successful create. |
| `deployment/features/fleet-management/php/fleet-join.php` | **[UPDATED — S23]** Now enqueues fleet_assign command to amboat_command_queue after successful join. |
| `deployment/v0.9.4/pi_source/cloud_agent.py` | **[UPDATED — S23]** Added handle_fleet_assign() — writes /opt/d3kos/config/fleet.json + restarts d3kos-fleet-push.service. Added handle_fleet_unassign() — removes fleet.json + stops service. Both wired into dispatch(). |
| Pi: `/opt/d3kos/services/cloud-agent/cloud_agent.py` | **[DEPLOYED — S23]** fleet_assign + fleet_unassign handlers live. Service restarted active. |
| Pi: `/etc/sudoers.d/d3kos` | **[UPDATED — S23]** Added NOPASSWD for systemctl restart + stop d3kos-fleet-push.service. |
| VM: `/home/d3kos-admin/app.py` | **[UPDATED — S24]** Added 3 fleet routes: GET /fleets (paginated list), GET /fleet/<id> (detail + members), POST /fleet/<id>/suspend (suspend with reason). |
| VM: `/home/d3kos-admin/templates/fleet.html` | **[NEW — S24]** Dual-mode fleet template: list view (fleet table) + detail view (info grid, member table with last position, suspend form). |
| VM: `/home/d3kos-admin/templates/base.html` | **[UPDATED — S24]** Added "Fleets" nav link, active-state for fleet/fleet_detail/fleet_suspend endpoints. |
| VM: `/home/d3kos-admin/static/style.css` | **[UPDATED — S24]** Appended fleet CSS: .fleet-code-badge, .suspended-badge, .active-badge, .role-badge (owner/member/view), .info-grid, .danger-zone, .btn-danger, .mono. |
| HostPapa staging DB: `amboat_fleets.suspended` | **[MIGRATION — S24]** Added TINYINT(1) NOT NULL DEFAULT 0 column. Done via fleet-migrate.php (deployed, run, deleted). Enables fleet suspension in admin CRM. |
| `deployment/features/fleet-management/admin-crm/fleet.html` | **[NEW — S24]** Repo copy of admin CRM fleet.html template. |
| `deployment/features/fleet-management/admin-crm/app_fleet_routes.py` | **[NEW — S24]** Repo copy of app.py with fleet routes. |
| `deployment/features/fleet-management/admin-crm/base.html` | **[NEW — S24]** Repo copy of base.html with Fleet nav link. |

## v0.9.7 Phase 1 — Support Ticket System (S25 2026-04-07)

| File | Description |
|------|-------------|
| `deployment/features/support-tickets/php/support-request.php` | **[NEW — S25]** Upgraded support request endpoint. Adds amboat_support_tickets DB insert via $wpdb, returns ticket_id. Error suppression prevents WP notices corrupting JSON. Replaces Apr-3 one-way email version. |
| `deployment/features/support-tickets/php/ticket-status.php` | **[NEW — S25]** GET ?ticket_id=N — returns ticket status + admin_note (resolved only) for authenticated user's own ticket. config.php + direct mysqli auth. |
| `deployment/features/support-tickets/php/admin-api-tickets.php` | **[NEW — S25]** Admin ticket API. PDO, Bearer auth (same ADMIN_API_KEY as admin-api.php). Actions: get_tickets (paginated + status filter), get_ticket (full detail), update_ticket (status + admin_note). |
| `deployment/features/support-tickets/crm/tickets.html` | **[NEW — S25]** Admin CRM tickets template. List view: status tabs (All/Open/In Progress/Resolved), pagination, data-table. Detail view: subject/body/admin_note display, update form. Light theme with inline styles. |
| `deployment/features/support-tickets/crm/app_patched.py` | **[NEW — S25]** Deployed to VM as /home/d3kos-admin/app.py. Adds proxy_call_tickets() + /tickets, /ticket/<id>, /ticket/<id>/update Flask routes. |
| `deployment/features/support-tickets/scripts/deploy-support-tickets.py` | **[NEW — S25]** FTP + VM deployment script for all support ticket files. |
| `deployment/features/support-tickets/BUILD_CHECKLIST.md` | **[NEW — S25]** Phase 1 build tracking. Phase 1 complete. Phase 2 deferred. |
| `deployment/v0.9.4/pwa/app.js` | **[UPDATED — S25]** Support screen: captures ticket_id on send success, shows "Message sent — Ticket #N", adds Check Status button, stores ticket_id in localStorage. apiFetch result now captured (was discarded). |
| VM: `/home/d3kos-admin/app.py` | **[REPLACED — S25]** Added proxy_call_tickets() helper + 3 ticket routes. Full file replaced (not patched) after patch-vm-app.py regex approach failed. |
| VM: `/home/d3kos-admin/templates/tickets.html` | **[NEW — S25]** Support tickets CRM template. Deployed via pscp.exe + plink sudo cp. |
| VM: `/home/d3kos-admin/templates/base.html` | **[UPDATED — S25]** Tickets nav link added after Fleets. Inserted via plink python3 one-liner. |
| HostPapa staging DB: `amboat_support_tickets` | **[MIGRATION — S25]** Created via support-migrate.php (deployed, run, deleted). Columns: ticket_id AUTO_INCREMENT, user_id, device_token, subject, body, status ENUM(open/in_progress/resolved), admin_note, created_at, updated_at. |

## v0.9.8 — Autonomous Agents AA1-AA6 (S28-S30 2026-04-07)

| File | Description |
|------|-------------|
| `deployment/features/autonomous-agents/pi_source/agent_base.py` | **[NEW — S28]** AgentBase class, AgentResult dataclass, shared paths (STATE_DB, STATUS_JSON, LOG_PATH). report_failure() helper added S31. |
| `deployment/features/autonomous-agents/pi_source/agent_scheduler.py` | **[NEW — S28]** 5-min poll loop. SQLite state (agent_runs + agent_history). Atomic JSON write via .tmp rename. Rotating log. 5 agents registered. |
| `deployment/features/autonomous-agents/pi_source/agents/performance_agent.py` | **[NEW — S28]** AA3: CPU/mem/disk/thermal. Pi-tuned thresholds (cpu warn 90%/crit 95% for SwiftShader). /tmp cleanup at disk critical. Interval: 5 min. |
| `deployment/features/autonomous-agents/pi_source/agents/update_agent.py` | **[NEW — S29, UPDATED — S31+S32]** AA2: version.php check, T1+ auto-apply + rollback. FI1 failure report on update fail. FI2 fix-confirmed on update success. Interval: 24h. |
| `deployment/features/autonomous-agents/pi_source/agents/storage_agent.py` | **[NEW — S29]** AA4: log trimming >50MB, old backup cleanup (keep 3), predictive disk full warning. Interval: 24h. |
| `deployment/features/autonomous-agents/pi_source/agents/health_agent.py` | **[NEW — S30]** AA5: health score 0-100, 12-service check, DB integrity deep scan every 7 days. Writes health-report.json. Interval: 24h. |
| `deployment/features/autonomous-agents/pi_source/agents/backup_agent.py` | **[NEW — S30]** AA6: USB device detection (st_dev comparison), rsync incremental/full, T3 cloud sync stub. Interval: 24h. |
| `deployment/features/autonomous-agents/pi_source/d3kos-agents.service` | **[NEW — S28]** systemd unit. User=d3kos. ExecStartPre sleep 20. Restart=always. |
| `deployment/features/autonomous-agents/scripts/deploy-agents.py` | **[NEW — S28]** SSH/SCP deploy script for all agent files + service. |
| Pi: `/opt/d3kos/services/agents/` | **[DEPLOYED — S28-S30]** All agent files live. d3kos-agents service active, health 96/100 green. |
| `deployment/d3kOS/dashboard/app.py` | **[UPDATED — S28]** Added /agents/status, /health/report, /update/status routes. |
| `deployment/d3kOS/dashboard/static/css/d3kos.css` | **[UPDATED — S28]** v20: .pi-health dot with ok/warn/crit states. |
| `deployment/d3kOS/dashboard/templates/index.html` | **[UPDATED — S28]** Pi health dot in status bar. Update notice bar (amber, dismissible). Agent status polling JS (5 min). |
| `deployment/v0.9.4/pi_source/engine-monitor.html` | **[UPDATED — S28]** Section 6 Autonomous Agents — fully dynamic agent cards via updateAgents(). |
| `deployment/v0.9.4/pi_source/d3kos_watchdog.py` | **[UPDATED — S28+S31]** d3kos-agents + d3kos-failure-reporter added to CRITICAL_SERVICES. |

## v0.9.8 — Failure Intelligence FI1/FI2/FI3 + Update Publisher (S31+S32 2026-04-07)

| File | Description |
|------|-------------|
| `deployment/features/autonomous-agents/pi_source/failure_reporter.py` | **[NEW — S31]** FI1: Flask Port 8109. POST /report captures service/error_type/message. SHA-256 signature normalises message (strips numbers/paths/UUIDs) for cross-fleet clustering. SQLite local store. Background sync to FI2 every 5 min. GET /health + /recent. |
| `deployment/features/autonomous-agents/pi_source/d3kos-failure-reporter.service` | **[NEW — S31]** systemd unit for FI1. User=d3kos. ExecStartPre sleep 25. Restart=always. No StandardOutput redirect (avoids root-owned log conflict). |
| `deployment/features/autonomous-agents/php/failure-report.php` | **[NEW — S31]** FI2 receive endpoint. Inserts amboat_failure_reports, upserts amboat_issues (cluster by error_signature). Tables auto-created on first call. Bearer + X-Device-Token auth. |
| `deployment/features/autonomous-agents/php/fix-confirmed.php` | **[NEW — S31]** FI2 fix confirmation. AA2 calls after successful update. Updates amboat_issue_resolutions + resolved_count. Auto-closes issue at ≥90% resolution + 48h silence. Bearer + X-Device-Token auth. |
| `deployment/features/autonomous-agents/php/issue-api.php` | **[NEW — S31]** FI2 CRM API. GET list/get/stats, POST update. Full lifecycle: open→diagnosed→fix_validated→released→closed. Bearer auth (matches CRM proxy_api_key). |
| `deployment/features/autonomous-agents/crm/failure_routes.py` | **[NEW — S31]** FI3 CRM route snippet. /failures list + /failure/<id> detail + /failure/<id>/update. Integrated into VM app.py S31. |
| `deployment/features/autonomous-agents/crm/failures.html` | **[NEW — S31]** FI3 CRM template. Issue list with per-issue resolution progress bars. Detail: affected devices, resolutions, recent reports, lifecycle update form. |
| `deployment/features/autonomous-agents/scripts/deploy-fi.py` | **[NEW — S31]** FTP deploy script for FI PHP files to HostPapa. |
| `deployment/features/autonomous-agents/php/version.php` | **[REWRITTEN — S32]** DB-backed. Reads amboat_versions (auto-created). Falls back to empty blocks if DB unavailable. Replaces hardcoded JSON. |
| `deployment/features/autonomous-agents/php/update-publish.php` | **[NEW — S32]** Update Publisher API. POST publish (deactivates old, inserts new), deactivate, reactivate. GET list, current. Bearer auth. |
| `deployment/features/autonomous-agents/crm/update_routes.py` | **[NEW — S32]** CRM route snippet. /publish-update GET+POST. Integrated into VM app.py S32. |
| `deployment/features/autonomous-agents/crm/publish_update.html` | **[NEW — S32]** Update Publisher CRM page. Active version cards (incremental + major), publish form, version history with pull/restore, workflow guide. |
| `deployment/features/autonomous-agents/scripts/package-update.py` | **[NEW — S32]** Local packager. Maps repo-relative paths to Pi paths via REPO_TO_PI dict. Builds tar.gz with manifest.json. Generates SHA-256. Prints HostPapa upload URL + CRM-ready values. |
| HostPapa staging: `updates/` directory | **[NEW — S32]** Created via FTP. Package hosting location: .../twentytwenty-child/updates/ |
| HostPapa DB: `amboat_versions` | **[NEW — S32]** Auto-created by version.php/update-publish.php on first call. Columns: id, update_type, version, url, checksum, released, t1_upgrade, services_to_restart, release_notes, published_at, is_active. |
| HostPapa DB: `amboat_issues` | **[NEW — S31]** Issue lifecycle table. Clustered by error_signature. Status ENUM. resolved_count tracks fleet adoption. |
| HostPapa DB: `amboat_failure_reports` | **[NEW — S31]** Raw failure report log. Indexed by error_signature + device_token. |
| HostPapa DB: `amboat_issue_resolutions` | **[NEW — S31]** Per-device fix confirmation records. UNIQUE(issue_id, device_token). |
| VM: `/home/d3kos-admin/app.py` | **[UPDATED — S31+S32]** failure_routes + update_routes appended. /failures, /failure/<id>, /failure/<id>/update, /publish-update live. |
| VM: `/home/d3kos-admin/templates/failures.html` | **[NEW — S31]** FI3 issue dashboard template. |
| VM: `/home/d3kos-admin/templates/publish_update.html` | **[NEW — S32]** Update Publisher template. |
| `deployment/features/autonomous-agents/php/version-heartbeat.php` | **[DEPLOYED S34]** UPSERT pattern (INSERT ... ON DUPLICATE KEY UPDATE). MySQL 5.7 safe. Receives AA2 heartbeat, inserts new devices, updates existing. Verified working — device_found:true. |
| `deployment/features/autonomous-agents/php/version-api.php` | **[DEPLOYED S34]** ADMIN_API_KEY auth. CREATE TABLE IF NOT EXISTS amboat_versions. Safe fetch on all queries. Fleet + distribution actions live. |
| `deployment/features/autonomous-agents/crm/fleet_versions_routes.py` | **[DEPLOYED S34]** Live in VM app.py. proxy_call_versions module-level helper. Calls fleet + distribution endpoints. |
| `deployment/features/autonomous-agents/crm/fleet_versions.html` | **[DEPLOYED S34]** Live in VM templates/. Distribution via pre-sorted PHP list. Plain-English empty state. Verified showing Pi. |
| `deployment/docs/AUTONOMOUS_AGENTS_AND_FI.md` | **[NEW — S33]** Full v0.9.8 feature document. Design philosophy, architecture, all components, port map, auth patterns, file index, deploy checklist, step-by-step release workflow. |
| HostPapa DB: `amboat_devices.current_version` | **[LIVE S34]** MySQL 5.7-safe column add via information_schema check. UPSERT inserts new devices automatically. |
| VM: `/home/d3kos-admin/templates/fleet_versions.html` | **[DEPLOYED S34]** Live. Route wired, nav links added, service restarted. Verified showing Skipper Don Pi v0.9.2.2. |
| `deployment/features/privacy/php/data-export.php` | **[NEW — S35 2026-04-08]** GDPR Art.15 data export. Bearer app_token auth. Returns account, devices, tickets, commands, billing as JSON. Deployed to HostPapa staging mobile/. |
| `deployment/features/privacy/php/data-delete.php` | **[NEW — S35 2026-04-08]** GDPR Art.17 erasure. Bearer app_token auth + confirm:true. Anonymizes WP user, deletes all amboat_* PII, anonymizes billing rows, logs deletion timestamp. Deployed to HostPapa staging mobile/. |
| `deployment/features/privacy/PRIVACY_POLICY_TEMPLATE.md` | **[NEW — S35 2026-04-08]** Full GDPR/CCPA privacy policy. Covers data types, retention table, third-party table (HostPapa/Stripe/Gemini), rights (access/erasure/portability/objection). Don publishes to WordPress before Phase 4 live push. |
| `deployment/v0.9.4/pwa/app.js` | **[UPDATED — S35 2026-04-08]** Privacy & Data card added to settings screen. Download My Data (JSON) + Delete My Account (two-tap confirmation). Deployed to Pi /var/www/html/app.js. |
| HostPapa: security patch S35 | **[S35 2026-04-08]** 12 PHP files patched: hash_equals() replaces !== on all API key comparisons. Zero real_escape_string() remaining. Files: failure-report.php, fix-confirmed.php, issue-api.php, update-publish.php, version-heartbeat.php, version-api.php, diagnostic-bundle.php, diagnostic-past-cases.php, diagnostic-resolve.php, diagnostic-fix.php, diagnostic-upload.php, admin-api-tickets.php. |

## v0.9.4.1 — Community Map + Chart Room (S36 2026-04-08)

| File | Description |
|------|-------------|
| `deployment/features/v0941-plan/php/community-get.php` | **[NEW — S35/S36]** Public GET endpoint. Returns fleet positions (wpax_usermeta, map_sharing=1, synced 48h), hazard markers, fleet count. All coordinates ROUND(lat/lon,2) ~1.1km privacy blur. Auto-creates amboat_community_markers + amboat_community_positions tables. Deployed to HostPapa staging mobile/. |
| `deployment/features/v0941-plan/php/community-markers-write.php` | **[NEW — S36]** POST endpoint for hazard/anchorage/fuel markers. Dual auth: app_token (PWA) or AMBOAT_API_KEY + X-Device-Token (Pi). Whitelist enum validation. Rate limited 20 markers/device/24h. Deployed to HostPapa staging mobile/. |
| `deployment/features/v0941-plan/php/community-position.php` | **[NEW — S36]** Pi-direct position UPSERT. Pi-facing auth only (AMBOAT_API_KEY + X-Device-Token). UPSERT one row per device_token into amboat_community_positions. Validates coords, rejects null-island. Deployed to HostPapa staging mobile/. |
| `deployment/features/v0941-plan/php/page-dashboard.php` | **[NEW — S36]** Chart Room template — PDF reports section fixed. Replaced get_user_meta('atmyboat_pdf_reports') (old deprecated usermeta format) with $wpdb query on amboat_pdf_reports table keyed by device_token. Deployed to HostPapa staging theme root. |
| `deployment/features/v0941-plan/php/page-community.php` | **[NEW — S36]** Community page — Leaflet fully wired. Initialises OSM map, fetches community-get.php on load, plots fleet dots + typed hazard markers, auto-refreshes every 5 min, Add Marker flow for T1+ (crosshair mode, overlay form, POST to community-markers-write.php). Deployed to HostPapa staging theme root. |
| HostPapa DB: `amboat_community_markers` | **[AUTO-CREATED]** Stores community hazard/anchorage/fuel markers. Auto-created by community-get.php and community-markers-write.php on first call. |
| HostPapa DB: `amboat_community_positions` | **[AUTO-CREATED]** Pi-direct position table. One row per device_token. Auto-created by community-get.php and community-position.php on first call. |

## v0.9.9.2 Phase B — M14 AI Engine Diagnostic + M3/M4 Restart Services (S39 2026-04-08)

| File | Description |
|------|-------------|
| `deployment/v0.9.4/pi_source/overlays.js` | **[NEW IN REPO — S39]** `openDiag()` rewritten as async Gemini call. Tier gate: `/config/tier` endpoint. Helper functions: `_diagCellLabel()`, `_diagReadingsSummary()`, `_diagBuildCards()`. T0/T1: upgrade prompt. T2/T3: live SK data → Gemini proxy port 8097 → panel populated. Pi: `/opt/d3kos/services/dashboard/static/js/overlays.js` |
| `deployment/v0.9.4/pi_source/instruments.js` | **[NEW IN REPO — S39]** `window._d3kEngData` cache added. Each SK_HANDLER (coolant, oil, RPM, battery, fuel) updates cache. Cell onclick changed to `() => openDiag(id)`. Pi: `/opt/d3kos/services/dashboard/static/js/instruments.js` |
| `deployment/v0.9.4/pi_source/index.html` | **[NEW IN REPO — S39]** `diagTitle`, `diagGrid`, `diagAiTxt` IDs added to diag panel elements. Pi: `/opt/d3kos/services/dashboard/templates/index.html` |
| `deployment/v0.9.4/pi_source/app.py` | **[NEW IN REPO — S39]** `/config/tier` Flask endpoint — reads license.json, returns `{tier: 3, tier_str: "T3"}`. Pi: `/opt/d3kos/services/dashboard/app.py` |
| `deployment/v0.9.4/pi_source/cloud_agent.py` | **[UPDATED — S39]** `handle_restart_services()` added — restarts d3kos-voice, d3kos-ai-bridge, d3kos-gemini-proxy, d3kos-predictive. `restart_service` dispatch case added. Pi: `/opt/d3kos/services/cloud_agent.py` |
| `deployment/v0.9.4/pwa/app.js` | **[UPDATED — S39]** "Restart Pi" card added to `renderSettings()`. Sends `restart_service` via `apiSendCommand()`. Polls via `apiPollCommand()` every 5s, 2-min timeout. HostPapa: `/staging/app/app.js` |
| HostPapa: `page-help.php` | **[UPDATED — S39]** "User Manual" quick-link card added (7th card, links to `/manual/`). Book SVG icon. `staging/wp-content/themes/twentytwenty-child/page-help.php` |
| HostPapa: `page-manual.php` | **[DEPLOYED S38 — ADDED TO REPO S39]** User Manual page template. PDF download button (GitHub releases). 16-section ToC. "Ask Helm" RAG section. `staging/wp-content/themes/twentytwenty-child/page-manual.php` |
