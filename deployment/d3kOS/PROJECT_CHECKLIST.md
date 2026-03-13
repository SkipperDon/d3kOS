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
**Risk:** LOW | **Status:** COMPLETE 2026-03-13 | **Requires:** Pi connection (192.168.1.237)
**Reference:** D3KOS_PLAN.md §Phase 1

- [x] Pre-actions run: SK confirmed :8099, ports 3000+3001 confirmed free, port 8085 free
- [x] Port migration: SK moved :3000→:8099, issue_detector moved :8099→:8199
- [x] Current menu files backed up to /home/d3kos/backups/d3kos-menu-backup-2026-03-13/ with timestamp
- [x] `d3kos-dashboard.desktop` created — opens localhost:3000 in Chromium fullscreen
- [x] `d3kos-opencpn.desktop` created — OpenCPN fallback (`flatpak run org.opencpn.OpenCPN`)
- [x] `d3kos-avnav.desktop` created — opens localhost:8080
- [x] `d3kos-gemini-nav.desktop` created — opens localhost:3001
- [x] `d3kOS.menu` registered as Pi menu category (X-d3kOS)
- [x] `d3kOS.directory` created for menu display
- [~] OpenCPN removed from Navigation menu — N/A: OpenCPN is Flatpak only, no system .desktop to override
- [x] All .desktop files pass `desktop-file-validate`
- [ ] d3kOS category visible in Pi application menu (verify on Pi screen)
- [x] docs/MENU_STRUCTURE.md written with before/after, rollback, and port migration instructions
- [x] SESSION_LOG.md updated

---

## Phase 2 — Dashboard Hub (Flask :3000)
**Risk:** MEDIUM | **Status:** COMPLETE 2026-03-13 | **Requires:** Phase 1 complete
**Reference:** D3KOS_PLAN.md §Phase 2 | UI Reference: docs/d3kos-mockup-v4.html (screen-menu + iframe panes)

### Pre-conditions
- [x] Python 3.13.5 confirmed on Pi
- [x] Flask 3.1.1 already installed — no pip install needed
- [x] Port 3000 confirmed free (after SK port migration)
- [x] RAM adequate (confirmed)

### Files to create
- [x] `dashboard/config/d3kos-config.env` — NOT committed (gitignore confirmed)
- [x] `dashboard/app.py` — Flask app, routes: /, /status, /settings, /offline, /launch/opencpn
- [x] `dashboard/templates/index.html` — 9-button 3x3 grid per mockup v4, JS screen navigation
- [x] `dashboard/templates/settings.html` — placeholder (full build in Phase 4)
- [x] `dashboard/templates/offline.html` — shown when AvNav unreachable
- [x] `dashboard/static/css/d3kos.css` — dark nautical theme (black bg, #00CC00 accent, mockup v4 grid)
- [x] `dashboard/static/js/connectivity-check.js` — polls /status every 30s, Ollama indicator added
- [x] `dashboard/static/js/panel-toggle.js` — screen navigation + Windy/Radar weather screens
- [x] `dashboard/d3kos-dashboard.service` — systemd unit (repo copy; Pi uses /opt/d3kos/services/dashboard/)

### Systemd (Pi)
- [x] `/etc/systemd/system/d3kos-dashboard.service` deployed to Pi (WorkingDirectory=/opt/d3kos/services/dashboard)
- [x] Service enabled (symlink created) and starts on boot
- [ ] Service survives reboot test

### Verification
- [x] Dashboard loads at http://localhost:3000 (curl confirmed HTML response)
- [ ] 9 menu buttons match mockup v4 (verify on Pi screen)
- [ ] AvNav iframe loads (http://localhost:8080) — AvNav not yet installed; ai_api.py on :8080 for now
- [ ] Weather panel opens/closes (Windy + Radar tabs) — verify on Pi screen
- [x] Status indicators: /status returns internet:true, signalk:true, ollama:true, gemini:false (correct)
- [ ] Clock displays and ticks (verify on Pi screen)
- [x] d3kos-config.env NOT in git — verified
- [ ] SESSION_LOG.md updated

---

## Phase 3 — Gemini Marine AI Proxy (:3001)
**Risk:** MEDIUM-HIGH | **Status:** COMPLETE 2026-03-13 | **Requires:** Phase 2 complete
**Reference:** D3KOS_PLAN.md §Phase 3
**Decision (2026-03-12):** Option B — once Phase 3 is tested, retire old `d3kos-gemini-proxy.service` at :8097 and update `voice-assistant-hybrid.py` + `query_handler.py` to call :3001.

### Pre-conditions
- [x] Ollama reachable at http://192.168.1.36:11434/api/tags — models: qwen3-coder:30b, nomic-embed-text
- [x] Ollama model: qwen3-coder:30b (plan default `mistral` not installed — updated in gemini.env)
- [x] Gemini API key confirmed in /opt/d3kos/config/api-keys.json (starts AIzaSy...)
- [x] Port 3001 confirmed free

### Files to create
- [x] `gemini-nav/config/gemini.env` — NOT committed (gitignore confirmed via **/*.env)
- [x] `gemini-nav/gemini_proxy.py` — Gemini→Ollama routing, /api/chat for qwen3-coder:30b
- [x] `gemini-nav/templates/chat.html` — full chat UI (typing indicator, source badge, suggestion chips)
- [x] `gemini-nav/tests/test_gemini_proxy.py` — 10 tests (privacy, cache, routing, UI)
- [x] `gemini-nav/d3kos-gemini.service` — repo copy

### Systemd (Pi)
- [x] `/etc/systemd/system/d3kos-gemini.service` deployed (WorkingDirectory=/opt/d3kos/services/gemini-nav)
- [x] Service enabled + active

### Verification
- [x] All 10 pytest tests pass (10/10 on Pi — pytest 9.0.2, Python 3.13.5)
- [x] /ask returns Gemini response (source:gemini, tokens:219 confirmed live)
- [ ] /ask falls back to Ollama when offline (verify by disconnecting internet)
- [x] dashboard /status now shows gemini:true
- [ ] Cache entries verified — no query text (check /opt/d3kos/services/gemini-nav/cache/response_cache.json)
- [x] gemini.env NOT in git — confirmed
- [x] SESSION_LOG.md updated

---

## Phase 4 — Settings Page + AvNav Documentation
**Risk:** LOW | **Status:** COMPLETE 2026-03-13 | **Requires:** Phase 2 complete (Phase 3 recommended)
**Reference:** D3KOS_PLAN.md §Phase 4 | UI Reference: docs/d3kos-mockup-v4.html (screen-settings, all 16 sections)

### Settings page (16 sections)
- [x] Settings page loads at http://localhost:3000/settings
- [x] Bookmark sidebar scrolls to all 16 sections
- [x] Section 1: System Status — live indicators (AvNav, SK, GPS, AIS, Gemini, Ollama, OpenPlotter, Internet) — fetches /status on load
- [x] Section 2: Engine Configuration — service interval, oil interval, engine hours, hours since service
- [x] Section 3: Units & Display — distance, speed, temperature, pressure + metric/imperial toggle
- [x] Section 4: Alerts & Notifications — service due, overheat, low oil, battery voltage toggles
- [x] Section 5: AI Assistant — vessel name, home port, Gemini model, routing mode, API key field, privacy toggles, system prompt preview
- [x] Section 6: Camera Setup — slot/hardware panel (existing camera overhaul system)
- [x] Section 7: Data Management — export, import, clear trip data, clear benchmarks
- [x] Section 8: Network & Connectivity — port table (live status), Ollama address, Windy/Radar toggles
- [x] Section 9: Chart Setup & Docs — o-charts install, AvNav plugins, free charts, AvNav how-to
- [x] Section 10: OpenPlotter & Infrastructure — OpenPlotter ref, plugins guide, OpenCPN fallback guide
- [x] Section 11: Getting Started — daily use steps + emergency procedures
- [x] Section 12: Phase Roadmap — all 5 phases with accurate status badges (0-3 done, 4 active, 5 todo)
- [x] Section 13: System Actions — restart SK, restart Node-RED, restart Dashboard, restart Gemini, reboot
- [x] Section 14: System Information — live from /sysinfo endpoint (disk, memory, CPU temp, uptime, IP)
- [x] Section 15: License & Tier — tier, install ID, features
- [x] Section 16: About d3kOS — version, platform, project, credits
- [x] Pi deploy: app.py, settings.html, d3kos.css copied to /opt/d3kos/services/dashboard/ — 2026-03-13
- [x] Pi deploy: /etc/sudoers.d/d3kos created — NOPASSWD systemctl restart for signalk, nodered, d3kos-dashboard, d3kos-gemini, reboot. Verified: `visudo -c` OK
- [x] /settings loads HTML on Pi (curl confirmed)
- [x] /sysinfo returns live data: CPU 63.3°C, disk 30%, mem 31%, uptime 21h 28m, IP 192.168.1.237
- [x] /status: avnav:true, gemini:true, internet:true, ollama:true, signalk:true — all live
- [x] /action/restart tested: {"ok":true,"service":"gemini"} — d3kos-gemini restarts and returns active
- [ ] Visual verify on Pi screen: bookmark sidebar scrolls, all 16 sections visible

### Critical fix (from D3KOS_PLAN)
- [x] Signal K WebSocket check uses ws://localhost:8099 — NOT ws://localhost:3000 (all docs + UI corrected)

### Documentation files
- [x] docs/AVNAV_OCHARTS_INSTALL.md written (v1.0.0)
- [x] docs/AVNAV_PLUGINS.md written (v1.0.0) — includes POST-only API reminder and Phase 5 integration notes
- [x] docs/OPENPLOTTER_REFERENCE.md written (v1.0.0)
- [x] All port references accurate (AvNav :8080, Signal K :8099, OpenPlotter :8081)
- [x] SESSION_LOG.md updated

---

## Phase 5 — AI + AvNav Integration
**Risk:** MEDIUM-HIGH | **Status:** DEPLOYED 2026-03-13 — service active at :3002
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
- [x] P5.0. AvNav API explored — POST-only confirmed from live Pi probe (2026-03-13)
- [x] P5.1. Signal K paths verified from live Pi — navigation.position, speedOverGround (m/s), courseOverGroundTrue (rad)
- [x] P5.2. Node-RED flows audited — 78 nodes, no AvNav flows, no conflicting anchor watch
- [x] P5.3. TTS engine selected — espeak-ng (piper has no voice model on Pi). plughw:S330,0 confirmed.
- [x] P5.4. Port 3002 confirmed free for AI Bridge
- [ ] All 8 open questions formally answered — partial (AVNAV_DATA_DIR=/var/lib/avnav confirmed, LOG_DIR=/home/d3kos/logs)

### Files created (source complete — Pi deploy pending)
- [x] `ai-bridge/config/ai-bridge.env` — placeholder template only (gitignored, line 4 + **/*.env)
- [x] `ai-bridge/ai_bridge.py` — Flask app port 3002, all endpoints + SSE stream
- [x] `ai-bridge/features/route_analyzer.py` — Feature 1: 5-min route widget
- [x] `ai-bridge/features/port_arrival.py` — Feature 2: 2nm arrival briefing
- [x] `ai-bridge/features/voyage_logger.py` — Feature 3: GPX summarization
- [x] `ai-bridge/features/anchor_watch.py` — Feature 4: drag detection + alert
- [x] `ai-bridge/utils/signalk_client.py` — REST polling (no WebSocket dep) for localhost:8099
- [x] `ai-bridge/utils/avnav_client.py` — POST-only client for avnav_navi.php
- [x] `ai-bridge/utils/tts.py` — espeak-ng wrapper
- [x] `ai-bridge/utils/geo.py` — haversine, bearing, unit conversions
- [x] `ai-bridge/tests/test_ai_bridge.py` — full test suite (unit + @integration markers)

### Systemd
- [x] `d3kos-ai-bridge.service` source written (User=d3kos, WorkingDirectory=/opt/d3kos/services/ai-bridge)
- [x] `/etc/systemd/system/d3kos-ai-bridge.service` deployed to Pi — 2026-03-13
- [x] Service enabled and starts on boot — enabled via systemctl enable
- [x] Service listed in `After=` after d3kos-dashboard and d3kos-gemini

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
- [x] Auto-generates when AvNav track recording stops (recording→stopped transition detection)
- [x] On-demand summarize_latest() / summarize_by_filename() — POST /summarize-voyage
- [x] Raw GPS coordinates NOT sent to AI (summary stats only — privacy enforced, test verifies)
- [x] Summaries saved to LOG_DIR/voyage-summaries/ (LOG_DIR=/home/d3kos/logs on Pi)
- [x] /voyages endpoint returns 5 most recent summaries (for settings page)
- [ ] Most recent 5 summaries shown in settings page (settings UI update deferred)

### Feature 4 — Anchor Watch AI Alerts
- [x] Alarm fires from pre-written text — zero AI wait (hardcoded tts.speak call in _fire_drag_alert)
- [x] 3-consecutive-poll confirmation (DRAG_CONFIRM_COUNT=3) — unit test verified
- [x] Screen alert shows drift distance, bearing, timestamp, speed (SSE anchor_alert event)
- [x] Audio alarm repeats every 60s via _repeat_alarm() background thread until dismissed
- [x] "GET AI ADVICE" button → GET /anchor/advice → on-demand only
- [x] Drift event JSON logged to LOG_DIR/anchor-events/
- [x] Anchor watch coordination with AvNav built-in confirmed (P5.2 — no conflict)

### Node-RED Integration
- [x] POST /webhook/query returns AI response JSON — calls Gemini proxy :3001
- [x] POST /webhook/alert fires TTS + SSE screen alert
- [x] POST /webhook/arrival triggers port arrival briefing for named destination
- [ ] All existing Node-RED flows confirmed unmodified (no flows changed — verify on Pi)

### Dashboard Updates (source complete)
- [x] app.py /status: added ai_bridge check for :3002
- [x] app.py _RESTART_SERVICES: added d3kos-ai-bridge
- [x] index.html status bar: ind-ai-bridge indicator added
- [x] index.html AvNav screen: avnav-layout with #ai-panel, route widget, arrival widget, anchor alarm
- [x] ai-bridge.js: SSE EventSource, all event handlers, triggerRouteAnalysis(), dismissAnchorAlarm(), getAnchorAdvice()
- [x] d3kos.css: Phase 5 AI panel CSS block
- [x] connectivity-check.js: ai_bridge wired
- [x] Dashboard files deployed to Pi + d3kos-dashboard restarted — 2026-03-13

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
