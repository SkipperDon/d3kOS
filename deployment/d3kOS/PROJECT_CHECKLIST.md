# d3kOS Project Checklist
**Version:** v0.9.2.1 | **Plan:** D3KOS_PLAN.md v2.0.0 | **UI Reference:** docs/d3kos-mockup-v4.html
**Updated:** 2026-03-12

Before each session: read D3KOS_PLAN.md, this file, SESSION_LOG.md (last 3 entries).

---

## Phase 0 — Initial Setup & Directory Structure
**Risk:** NONE | **Status:** COMPLETE 2026-03-12

- [x] Directory tree created (pi-menu/, dashboard/, gemini-nav/, docs/)
- [x] .gitignore in place — d3kos-config.env and gemini.env excluded
- [x] SESSION_LOG.md stub created
- [x] PROJECT_CHECKLIST.md stub created
- [x] CHANGELOG.md stub created
- [x] BACKUP_LOG.txt stub created
- [x] D3KOS_PLAN.md v2.0.0 deployed (copied from D3KOS_CLAUDE_CODE_PLAN_v2.md)
- [x] d3kos-mockup-v4.html deployed to docs/ (UI design reference)

---

## Phase 1 — Pi Menu Restructure
**Risk:** LOW | **Status:** TODO | **Requires:** Pi connection (192.168.1.237)
**Reference:** D3KOS_PLAN.md §Phase 1

- [ ] Pre-actions run: AvNav :8080, Signal K :8099, OpenPlotter :8081, ports 3000+3001 confirmed
- [ ] Current menu/desktop files backed up to pi-menu/BACKUP/ with timestamp in BACKUP_LOG.txt
- [ ] `d3kos-dashboard.desktop` created — opens localhost:3000 in Chromium fullscreen
- [ ] `d3kos-opencpn.desktop` created — OpenCPN fallback (emergency only)
- [ ] `d3kos-avnav.desktop` created — opens localhost:8080
- [ ] `d3kos-gemini-nav.desktop` created — opens localhost:3001
- [ ] `d3kOS.menu` registered as Pi menu category
- [ ] `d3kOS.directory` created for menu display
- [ ] OpenCPN removed from standard Navigation menu (Categories override only — system file untouched)
- [ ] All .desktop files pass `desktop-file-validate`
- [ ] d3kOS category visible in Pi application menu
- [ ] docs/MENU_STRUCTURE.md written with before/after and rollback instructions
- [ ] SESSION_LOG.md updated

---

## Phase 2 — Dashboard Hub (Flask :3000)
**Risk:** MEDIUM | **Status:** IN PROGRESS 2026-03-13 | **Requires:** Phase 1 complete
**Reference:** D3KOS_PLAN.md §Phase 2 | UI Reference: docs/d3kos-mockup-v4.html (screen-menu + iframe panes)

### Pre-conditions
- [ ] Python 3.9+ confirmed on Pi
- [ ] Flask, python-dotenv, requests installable via pip3
- [ ] Port 3000 confirmed free
- [ ] 500MB+ RAM free

### Files to create
- [x] `dashboard/config/d3kos-config.env` — NOT committed (gitignore confirmed)
- [x] `dashboard/app.py` — Flask app, routes: /, /status, /settings, /offline, /launch/opencpn
- [x] `dashboard/templates/index.html` — 9-button 3x3 grid per mockup v4, JS screen navigation
- [x] `dashboard/templates/settings.html` — placeholder (full build in Phase 4)
- [x] `dashboard/templates/offline.html` — shown when AvNav unreachable
- [x] `dashboard/static/css/d3kos.css` — dark nautical theme (black bg, #00CC00 accent, mockup v4 grid)
- [x] `dashboard/static/js/connectivity-check.js` — polls /status every 30s, Ollama indicator added
- [x] `dashboard/static/js/panel-toggle.js` — screen navigation + Windy/Radar weather screens
- [x] `dashboard/d3kos-dashboard.service` — systemd unit (deploy to Pi /etc/systemd/system/)

### Systemd
- [ ] `/etc/systemd/system/d3kos-dashboard.service` deployed to Pi
- [ ] Service enabled and starts on boot
- [ ] Service survives reboot test

### Verification
- [ ] Dashboard loads at http://localhost:3000
- [ ] 9 menu buttons match mockup v4: AvNav, AI Nav, Settings, Sea State, Radar, Engine Monitor, Trip Log, Marine Vision, OpenCPN
- [ ] AvNav iframe loads (http://localhost:8080)
- [ ] Weather panel opens/closes (Windy + Radar tabs)
- [ ] Offline notice shown when internet down
- [ ] Status indicators update every 30s (AvNav :8080, Signal K :8099, Gemini :3001, Ollama 192.168.1.36:11434, Internet)
- [ ] Clock displays and ticks in status bar
- [ ] d3kos-config.env NOT in git — verified with `git status`
- [ ] SESSION_LOG.md updated

---

## Phase 3 — Gemini Marine AI Proxy (:3001)
**Risk:** MEDIUM-HIGH | **Status:** TODO | **Requires:** Phase 2 complete
**Reference:** D3KOS_PLAN.md §Phase 3
**Decision (2026-03-12):** Option B — once Phase 3 is tested, retire old `d3kos-gemini-proxy.service` at :8097 and update `voice-assistant-hybrid.py` + `query_handler.py` to call :3001.

### Pre-conditions
- [ ] Ollama reachable at http://192.168.1.36:11434/api/tags
- [ ] Available Ollama models listed (confirm model name for gemini.env)
- [ ] Gemini API key obtained from aistudio.google.com (starts AIzaSy…)
- [ ] Port 3001 confirmed free

### Files to create
- [ ] `gemini-nav/config/gemini.env` — NOT committed (gitignore verified)
- [ ] `gemini-nav/gemini_proxy.py` — Flask proxy, marine system prompt, Gemini→Ollama routing
- [ ] `gemini-nav/templates/chat.html` — chat UI per mockup v4 (AI Navigator screen)
- [ ] `gemini-nav/tests/test_gemini_proxy.py` — full pytest suite

### Systemd
- [ ] `/etc/systemd/system/d3kos-gemini.service` deployed to Pi
- [ ] Service enabled and starts on boot

### Verification
- [ ] All pytest tests pass: `pytest tests/test_gemini_proxy.py -v`
- [ ] /ask returns Gemini response (source: gemini) when online
- [ ] /ask falls back to Ollama (source: ollama) when offline
- [ ] Source badge in chat UI shows correct source
- [ ] Cache never exceeds 10 entries
- [ ] Query text NOT in cache — manually verify response_cache.json
- [ ] gemini.env NOT in git — verified with `git status`
- [ ] SESSION_LOG.md updated

---

## Phase 4 — Settings Page + AvNav Documentation
**Risk:** LOW | **Status:** TODO | **Requires:** Phase 2 complete (Phase 3 recommended)
**Reference:** D3KOS_PLAN.md §Phase 4 | UI Reference: docs/d3kos-mockup-v4.html (screen-settings, all 16 sections)

### Settings page (16 sections)
- [ ] Settings page loads at http://localhost:3000/settings
- [ ] Bookmark sidebar scrolls to all 16 sections
- [ ] Section 1: System Status — live indicators (AvNav, SK, GPS, AIS, Gemini, Ollama, OpenPlotter, Internet)
- [ ] Section 2: Engine Configuration — service interval, oil interval, engine hours, hours since service
- [ ] Section 3: Units & Display — distance, speed, temperature, pressure + metric/imperial toggle
- [ ] Section 4: Alerts & Notifications — service due, overheat, low oil, battery voltage toggles
- [ ] Section 5: AI Assistant — vessel name, home port, Gemini model, routing mode, API key field, privacy toggles, system prompt preview
- [ ] Section 6: Camera Setup — slot/hardware panel (existing camera overhaul system)
- [ ] Section 7: Data Management — export, import, clear trip data, clear benchmarks
- [ ] Section 8: Network & Connectivity — port table, Ollama address, Windy/Radar toggles
- [ ] Section 9: Chart Setup & Docs — o-charts install, AvNav plugins, free charts, AvNav how-to (doc modals)
- [ ] Section 10: OpenPlotter & Infrastructure — OpenPlotter ref, plugins guide, OpenCPN fallback guide (doc modals)
- [ ] Section 11: Getting Started — daily use steps + emergency procedures
- [ ] Section 12: Phase Roadmap — all 5 phases with status badges
- [ ] Section 13: System Actions — restart SK, restart Node-RED, reboot, factory reset
- [ ] Section 14: System Information — version, Pi model, OS, SK status, IP, disk, memory, CPU temp, uptime
- [ ] Section 15: License & Tier — tier, install ID, features
- [ ] Section 16: About d3kOS — version, platform, project, credits

### Critical fix (from D3KOS_PLAN)
- [ ] Signal K WebSocket check uses ws://localhost:8099 — NOT ws://localhost:3000

### Documentation files
- [ ] docs/AVNAV_OCHARTS_INSTALL.md written
- [ ] docs/AVNAV_PLUGINS.md written
- [ ] docs/OPENPLOTTER_REFERENCE.md written
- [ ] All port references accurate (AvNav :8080, Signal K :8099, OpenPlotter :8081)
- [ ] SESSION_LOG.md updated

---

## Phase 5 — AI + AvNav Integration
**Risk:** MEDIUM-HIGH | **Status:** TODO | **Requires:** Phase 4 complete + AvNav installed + one stable voyage
**Spec:** docs/D3KOS_PHASE5_AI_AVNAV_INTEGRATION.md (v1.1.0)
**Install guide:** docs/AVNAV_INSTALL_AND_API.md

### Stage A-F — AvNav Install Pre-Gate (docs/AVNAV_INSTALL_AND_API.md)
- [ ] A1. Pre-install checks run: Signal K port confirmed, disk OK, ports 8080/8082 free
- [ ] A2. Signal K port recorded in SESSION_LOG.md — confirm 8099, update plan if different
- [ ] A3. Port 8085 conflict resolved — keyboard-api moved to 8086 before AvNav install
- [ ] B1. AvNav installed via OpenPlotter Settings → Apps → AvNav Installer (NOT standalone .deb)
- [ ] B2. AvNav Autostart enabled in OpenPlotter
- [ ] B3. AvNav service running — `systemctl is-active avnav` returns active
- [ ] C1. Verification script run — all items pass
- [ ] C2. http://localhost:8080 loads in Chromium
- [ ] C3. AvNav connected to Signal K at correct port
- [ ] D1. AvNav data root path found and recorded in SESSION_LOG.md
- [ ] D2. AVNAV_DATA_DIR updated in D3KOS_PHASE5_AI_AVNAV_INTEGRATION.md + ai-bridge.env
- [ ] E1. POST API tested — gps.lat and gps.lon return real values
- [ ] E2. Test route loaded and activated in AvNav
- [ ] E3. currentLeg.json found and readable
- [ ] E4. Track directory found and GPX files visible
- [ ] E5. docs/AVNAV_API_REFERENCE.md created with real JSON responses
- [ ] F1-F9. All final gate checks pass — Phase 5 coding may begin

### Phase 5 Pre-Actions (docs/D3KOS_PHASE5_AI_AVNAV_INTEGRATION.md §Pre-Actions)
- [ ] P5.0. AvNav API explored — docs/AVNAV_API_REFERENCE.md complete (POST method confirmed)
- [ ] P5.1. Signal K paths verified for Don's setup — all 10 paths checked and documented
- [ ] P5.2. Node-RED flows audited — AvNav/SK conflicts identified, anchor watch coordination confirmed
- [ ] P5.3. TTS engine selected (piper recommended), installed, tested on Pi speakers
- [ ] P5.4. Port 3002 confirmed free for AI Bridge
- [ ] All 8 open questions answered and recorded in SESSION_LOG.md

### Files to create
- [ ] `ai-bridge/config/ai-bridge.env` — NOT committed (verify **/*.env .gitignore rule)
- [ ] `ai-bridge/ai_bridge.py` — Flask app port 3002, all endpoints
- [ ] `ai-bridge/features/route_analyzer.py` — Feature 1: 5-min route widget
- [ ] `ai-bridge/features/port_arrival.py` — Feature 2: 2nm arrival briefing
- [ ] `ai-bridge/features/voyage_logger.py` — Feature 3: GPX summarization
- [ ] `ai-bridge/features/anchor_watch.py` — Feature 4: drag detection + alert
- [ ] `ai-bridge/utils/signalk_client.py` — WS reader for ws://localhost:8099
- [ ] `ai-bridge/utils/avnav_client.py` — POST client for avnav_navi.php (NOT GET)
- [ ] `ai-bridge/utils/tts.py` — TTS wrapper
- [ ] `ai-bridge/utils/geo.py` — haversine, bearing, unit conversions
- [ ] `ai-bridge/tests/test_ai_bridge.py` — full test suite

### Systemd
- [ ] `/etc/systemd/system/d3kos-ai-bridge.service` deployed to Pi
- [ ] Service enabled and starts on boot
- [ ] Service listed in `After=` after d3kos-dashboard and d3kos-gemini

### Feature 1 — Route Analysis Widget
- [ ] Route widget visible in dashboard above AvNav iframe
- [ ] Updates every 5 minutes when route is active
- [ ] Shows "NO ROUTE" when AvNav has no active route
- [ ] Re-triggers immediately when route or next waypoint changes
- [ ] "Analyze Now" button triggers immediate analysis
- [ ] Shows "OFFLINE AI" badge when using Ollama

### Feature 2 — Port Arrival Briefing
- [ ] Briefing fires exactly at 2nm from final destination waypoint
- [ ] Triggers once per destination (no re-fire until new route)
- [ ] Covers all 6 required categories: fuel, marina, customs, anchorage, provisioning, hazards
- [ ] Stage 1 audio (short summary) plays on Pi speakers
- [ ] Full briefing text visible in side panel
- [ ] Section headings tappable to hear read aloud

### Feature 3 — Voyage Log Summary
- [ ] Auto-generates when AvNav track recording stops
- [ ] On-demand "Summarize Voyage" button works from dashboard
- [ ] Raw GPS coordinates NOT sent to AI (summary stats only)
- [ ] Summaries saved to /home/boatiq/logs/voyage-summaries/
- [ ] Most recent 5 summaries shown in settings page

### Feature 4 — Anchor Watch AI Alerts
- [ ] Alarm fires from pre-written text — zero AI wait
- [ ] 3-consecutive-poll confirmation prevents GPS jitter false alarms
- [ ] Screen alert shows drift distance, bearing, timestamp, speed
- [ ] Audio alarm repeats every 60s until dismissed
- [ ] "GET AI ADVICE" button generates corrective action on demand
- [ ] Drift event JSON logged to /home/boatiq/logs/anchor-events/
- [ ] Anchor watch coordination with AvNav built-in alarm confirmed (P5.2)

### Node-RED Integration
- [ ] POST /webhook/query returns AI response JSON
- [ ] POST /webhook/alert fires TTS + screen alert
- [ ] All existing Node-RED flows confirmed unmodified

### Dashboard Updates (Phase 2 files)
- [ ] Phase 2 app.py /status endpoint updated: added ai_bridge check for :3002
- [ ] index.html status bar: AI Bridge indicator added

### Verification
- [ ] All pytest tests pass: `pytest tests/test_ai_bridge.py -v`
- [ ] test_avnav_client_uses_post() passes — verifies POST not GET
- [ ] Full offline test: internet disconnected, all features work via Ollama
- [ ] ai-bridge.env NOT in git — verified with `git status`
- [ ] SESSION_LOG.md updated
- [ ] docs/AVNAV_API_REFERENCE.md committed with real responses

---

## Known Port Reference (from D3KOS_PLAN — immutable)

| Service | Port/URL | Notes |
|---------|----------|-------|
| d3kOS Dashboard | localhost:3000 | Phase 2 |
| d3kOS Gemini Proxy | localhost:3001 | Phase 3 |
| d3kOS AI Bridge | localhost:3002 | Phase 5 |
| AvNav Charts | localhost:8080 | Phase 5 prerequisite |
| AvNav o-charts | localhost:8082 | Auto-started by AvNav |
| AvNav updater | localhost:8085 | CONFLICT with keyboard-api — resolve before Phase 5 |
| OpenPlotter | localhost:8081 | Infrastructure |
| Signal K | localhost:8099 | Read-only |
| Signal K WS | ws://localhost:8099/signalk/v1/stream | Read-only |
| AvNav REST API | POST http://localhost:8080/viewer/avnav_navi.php | POST only — GET returns 501 |
| Ollama (LAN) | 192.168.1.36:11434 | Offline AI fallback |
| Gemini API | generativelanguage.googleapis.com | Online AI |
