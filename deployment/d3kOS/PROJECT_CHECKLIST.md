# d3kOS Project Checklist
**Version:** v0.9.2.2 | **Plan:** D3KOS_PLAN.md v2.0.0 | **UI Reference:** docs/d3kos-mockup-v12.html
**Spec:** docs/D3KOS_UI_SPEC.md v1.0.0 | **Addendum:** docs/D3KOS_UI_SPEC_ADDENDUM_01.md v1.0.0
**Updated:** 2026-03-13

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
**Risk:** LOW | **Status:** ✅ COMPLETE 2026-03-13 | .desktop files deployed, SK port confirmed
**Reference:** D3KOS_PLAN.md §Phase 1

- [✅] Pre-actions run: AvNav :8080 ✓ (installed 2026-03-13), SK :8099 ✓, ports 3000+3001 confirmed
- [✅] Current menu/desktop files backed up to pi-menu/BACKUP/2026-03-13/ + BACKUP_LOG.txt updated
- [✅] `d3kos-dashboard.desktop` deployed ✓
- [✅] `d3kos-opencpn.desktop` deployed ✓
- [✅] `d3kos-avnav.desktop` deployed ✓
- [✅] `d3kos-gemini-nav.desktop` deployed ✓
- [✅] `d3kOS.menu` registered as Pi menu category (applications-merged/d3kOS.menu)
- [✅] `d3kOS.directory` created for menu display
- [⏭] OpenCPN removed from standard Navigation menu — SKIPPED: labwc kiosk never exposes system menu; root-level change not needed
- [✅] All .desktop files pass `desktop-file-validate` — confirmed on Pi 2026-03-13
- [✅] d3kOS category visible in Pi application menu (X-d3kOS category wired)
- [✅] docs/MENU_STRUCTURE.md written with before/after and rollback instructions
- [✅] SESSION_LOG.md updated

---

## Phase 2 — Dashboard Hub (Flask :3000)
**Risk:** MEDIUM | **Status:** ✅ COMPLETE 2026-03-13 | Flask dashboard live at :3000
**Reference:** D3KOS_PLAN.md §Phase 2 | UI Reference: docs/d3kos-mockup-v4.html (screen-menu + iframe panes)

### Pre-conditions
- [ ] Python 3.9+ confirmed on Pi
- [ ] Flask, python-dotenv, requests installable via pip3
- [ ] Port 3000 confirmed free
- [ ] 500MB+ RAM free

### Files to create
- [ ] `dashboard/config/d3kos-config.env` — NOT committed (verify gitignore)
- [ ] `dashboard/app.py` — Flask app, routes: /, /status, /settings, /offline
- [ ] `dashboard/templates/index.html` — main menu (9-button grid per mockup v4)
- [ ] `dashboard/templates/settings.html` — placeholder (full build in Phase 4)
- [ ] `dashboard/templates/offline.html` — shown when AvNav unreachable
- [ ] `dashboard/static/css/d3kos.css` — dark nautical theme (black bg, #00CC00 accent)
- [ ] `dashboard/static/js/connectivity-check.js` — polls /status every 30s
- [ ] `dashboard/static/js/panel-toggle.js` — Windy/Radar side panel controls

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
**Risk:** MEDIUM-HIGH | **Status:** ✅ COMPLETE 2026-03-13 | Gemini proxy live at :3001
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
**Risk:** LOW | **Status:** ✅ COMPLETE 2026-03-13 | 16-section settings.html deployed, AvNav docs written
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
**Risk:** MEDIUM-HIGH | **Status:** ✅ DEPLOYED 2026-03-13 | AI Bridge live at :3002, SSE stream active, all upstreams up
**Spec:** docs/D3KOS_PHASE5_AI_AVNAV_INTEGRATION.md (v1.1.0)
**Install guide:** docs/AVNAV_INSTALL_AND_API.md

### Stage A-F — AvNav Install Pre-Gate (docs/AVNAV_INSTALL_AND_API.md)
- [✅] A1. Pre-install checks run: SK on 8099 ✓, disk 77GB free ✓, ports checked 2026-03-13
- [✅] A2. Signal K port: 8099 confirmed 2026-03-13. All plan docs already use 8099 — no updates needed
- [x] A3. Port 8085 conflict RESOLVED (2026-03-13) — keyboard-api moved to 8087 (8086=fish_detector); Pi deploy pending Session 1
- [✅] B1. AvNav 20250822 installed 2026-03-13 via apt (free-x.de trixie). OpenPlotter not installed on this Pi; no conflict.
- [✅] B2. AvNav autostart enabled: systemctl enable avnav
- [✅] B3. avnav.service: active ✓
- [✅] C1. Verification: service active, port 8080, HTTP 200, 25 handlers, SK connected ✓
- [✅] C2. http://localhost:8080 loads in Chromium on Pi — system.default layout selected 2026-03-13 ✓
- [✅] C3. SK connected: "NMEA connected at http://localhost:8099/signalk/v1/api/" ✓
- [✅] D1. AVNAV_DATA = /var/lib/avnav (routes/ tracks/ charts/ log/) ✓
- [✅] D2. AVNAV_DATA_DIR updated in AVNAV_INSTALL_AND_API.md; ai-bridge.env does not exist yet (Phase 5)
- [✅] E1. POST request=gps: lat=43.686, lon=-79.521 ✓ (NOT request=navigate — does not exist in v20250822)
- [⏭] E2. Test route deferred — AvNav loads correctly confirmed. Don can test route creation at leisure (long-press chart to place waypoint)
- [✅] E3. currentLeg.json at /var/lib/avnav/routes/currentLeg.json — {} (no active route, normal) ✓
- [✅] E4. Track dir: /var/lib/avnav/tracks/ — 2026-03-13.gpx recording live ✓
- [✅] E5. deployment/d3kOS/docs/AVNAV_API_REFERENCE.md created with verified live responses ✓
- [✅] F1-F9. All gate checks pass 2026-03-13. Phase 5 coding may begin after Phase 1-4 complete.

### Phase 5 Pre-Actions (docs/D3KOS_PHASE5_AI_AVNAV_INTEGRATION.md §Pre-Actions)
- [✅] P5.0. AvNav API explored — docs/AVNAV_API_REFERENCE.md complete (POST method confirmed) ✓ 2026-03-13
- [ ] P5.1. Signal K paths verified for Don's setup — all 10 paths checked and documented
- [ ] P5.2. Node-RED flows audited — AvNav/SK conflicts identified, anchor watch coordination confirmed
- [✅] P5.3. TTS engine: espeak-ng v1.52.0 installed (piper unavailable), tested on plughw:S330,0 ✓ 2026-03-13
- [✅] P5.4. Port 3002 confirmed free and in use by d3kos-ai-bridge ✓ 2026-03-13
- [ ] All 8 open questions answered and recorded in SESSION_LOG.md

### Files to create
- [✅] `ai-bridge/config/ai-bridge.env` — deployed to Pi (NOT in git) ✓ 2026-03-13
- [✅] `ai-bridge/ai_bridge.py` — Flask app port 3002, all endpoints ✓ 2026-03-13
- [✅] `ai-bridge/features/route_analyzer.py` — Feature 1 ✓ 2026-03-13
- [✅] `ai-bridge/features/port_arrival.py` — Feature 2 ✓ 2026-03-13
- [✅] `ai-bridge/features/voyage_logger.py` — Feature 3 ✓ 2026-03-13
- [✅] `ai-bridge/features/anchor_watch.py` — Feature 4 ✓ 2026-03-13
- [✅] `ai-bridge/utils/signalk_client.py` — WS reader ✓ 2026-03-13
- [✅] `ai-bridge/utils/avnav_client.py` — POST client ✓ 2026-03-13
- [✅] `ai-bridge/utils/tts.py` — TTS wrapper (espeak-ng) ✓ 2026-03-13
- [✅] `ai-bridge/utils/geo.py` — haversine, bearing, unit conversions ✓ 2026-03-13
- [ ] `ai-bridge/tests/test_ai_bridge.py` — full test suite (not yet written)

### Systemd
- [✅] `/etc/systemd/system/d3kos-ai-bridge.service` deployed to Pi ✓ 2026-03-13
- [✅] Service enabled and starts on boot ✓ 2026-03-13
- [✅] Service listed in `After=` after d3kos-dashboard and d3kos-gemini ✓ 2026-03-13

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
- [✅] Phase 2 app.py /status endpoint updated: ai_bridge :3002 check deployed ✓ 2026-03-13
- [✅] index.html status bar: AI Bridge indicator deployed ✓ 2026-03-13

### Verification
- [ ] All pytest tests pass: `pytest tests/test_ai_bridge.py -v` (test suite not yet written)
- [ ] test_avnav_client_uses_post() passes — verifies POST not GET
- [ ] Full offline test: internet disconnected, all features work via Ollama
- [✅] ai-bridge.env NOT in git — verified 2026-03-13 (config/ excluded by .gitignore)
- [✅] SESSION_LOG.md updated 2026-03-13
- [✅] docs/AVNAV_API_REFERENCE.md committed with verified live responses ✓ 2026-03-13
- [✅] /status endpoint: avnav:up, gemini_proxy:up, signalk:up, tts_available:true ✓ 2026-03-13
- [✅] SSE /stream: heartbeat events flowing ✓ 2026-03-13

---

## Known Port Reference (from D3KOS_PLAN — immutable)

| Service | Port/URL | Notes |
|---------|----------|-------|
| d3kOS Dashboard | localhost:3000 | Phase 2 |
| d3kOS Gemini Proxy | localhost:3001 | Phase 3 |
| d3kOS AI Bridge | localhost:3002 | Phase 5 |
| AvNav Charts | localhost:8080 | Phase 5 prerequisite |
| AvNav o-charts | localhost:8082 | Auto-started by AvNav |
| AvNav updater | localhost:8085 | keyboard-api moved to :8087 — port 8085 free ✓ |
| OpenPlotter | localhost:8081 | Infrastructure |
| Signal K | localhost:8099 | Read-only |
| Signal K WS | ws://localhost:8099/signalk/v1/stream | Read-only |
| AvNav REST API | POST http://localhost:8080/viewer/avnav_navi.php | POST only — GET returns 501 |
| Ollama (LAN) | 192.168.1.36:11434 | Offline AI fallback |
| Gemini API | generativelanguage.googleapis.com | Online AI |

---

## v0.9.2.2 — Frontend UI Rebuild
**Version:** v0.9.2.2 | **Status:** IN PLANNING 2026-03-13
**Spec:** docs/D3KOS_UI_SPEC.md v1.0.0 + docs/D3KOS_UI_SPEC_ADDENDUM_01.md v1.0.0
**Reference mockup:** docs/d3kos-mockup-v12.html (canonical — build 2)
**Findings:** docs/D3KOS_V12_FINDINGS.md

### Pre-Session 1 — Spec Documents (COMPLETE 2026-03-13)
- [x] D3KOS_UI_SPEC.md deployed to docs/ ✓ 2026-03-13
- [x] D3KOS_UI_SPEC_ADDENDUM_01.md deployed to docs/ ✓ 2026-03-13
- [x] d3kos-mockup-v12.html deployed to docs/ ✓ 2026-03-13
- [x] D3KOS_V12_FINDINGS.md deployed to docs/ ✓ 2026-03-13
- [x] scripts/launch-d3kos.sh created (chmod +x) ✓ 2026-03-13
- [x] D3KOS_PLAN.md updated with v0.9.2.2 section ✓ 2026-03-13
- [x] PROJECT_CHECKLIST.md updated to v0.9.2.2 ✓ 2026-03-13

### Step 0 — Pi System Prerequisites (run once)
**Risk:** LOW | **Status:** ✅ COMPLETE 2026-03-14
- [✅] keyboard-api.py: /window/state, /window/maximize, /window/restore per Addendum 19.7. Already live on Pi. ✓
- [✅] `squeekboard` v1.43.1 — already installed ✓
- [✅] `wlrctl` v0.2.2 — already installed ✓
- [✅] `unclutter-xfixes` — installed 2026-03-14 ✓
- [✅] `~/.config/labwc/rc.xml` — `<windowRules><windowRule identifier="chromium" serverDecoration="no"/></windowRules>` added. ILITEK `mouseEmulation="no"` preserved. Backup: rc.xml.bak ✓
- [✅] `~/.config/labwc/autostart` — unclutter-xfixes + launch-d3kos.sh block added (waits for :3000 before launch). Backup: autostart.bak ✓
- [✅] `labwc` reloaded — SIGUSR1 sent to PID 1264 ✓
- [✅] `/opt/d3kos/scripts/launch-d3kos.sh` deployed, chmod +x ✓
- [ ] Verify on Pi screen: tap input field → Squeekboard appears (Don)
- [ ] Verify on Pi screen: wlrctl windowed toggle works via More menu (Don)
- [ ] Verify on reboot: Chromium auto-launches to localhost:3000 (Don)

### Session 1 — Static Template
**Risk:** MEDIUM | **Status:** ✅ COMPLETE 2026-03-14 | Commit d94b2f9
**Reference:** D3KOS_PLAN.md §v0.9.2.2 Session 1

#### index.html rebuild
- [✅] Extract v12 CSS from d3kos-mockup-v12.html → replace d3kos.css (keep Phase 5 AI widget CSS)
- [✅] Build new index.html from v12 HTML structure (status bar, toggle strip, 2 instrument rows, chart pane, split pane, bottom nav)
- [✅] Fix Bug 1: add `manualTheme` flag — autoTheme() never overrides manual selection
- [✅] Fix Bug 2: remove `hidden` class from nav row HTML (default BOTH = both rows visible)
- [✅] Row toggle: BOTH / ENGINE / NAV. Default: BOTH. `showRow('both')` on load
- [✅] HELM button: protrudes 24px, 128px total height, amber when listening
- [✅] More menu position 9: Windowed Mode toggle (wlrctl via keyboard-api.py :8087)
- [✅] All 5 overlays work: AIS alert (A), Engine diag (G), Critical (C), Position report (R), Port arrival (P)
- [✅] Day/night keyboard shortcuts: D / N

#### JS file split
- [✅] static/js/theme.js — CREATED (extracted from nav.js). manualTheme flag + setTheme() + autoTheme(). Loads before nav.js. Bug 1 fix. 2026-03-14
- [✅] static/js/nav.js — theme (Bug 1 fix), clock, ticker, split pane, windowed toggle, connectivity polling
- [✅] static/js/helm.js — HELM voice overlay, `HELM_LANG = document.documentElement.lang`
- [✅] static/js/overlays.js — all modal/overlay logic + toast
- [✅] static/js/instruments.js — showRow() 3-way toggle, context menu, DOMContentLoaded init

#### Flask wire-up
- [✅] app.py: inject `UI_LANG` from vessel.env into Jinja2 template context
- [✅] config/vessel.env: VESSEL_NAME, HOME_PORT, UI_LANG=en-GB

#### Session 1 Deploy + Verify
- [✅] Files deployed to Pi 2026-03-14 — 9 files to /opt/d3kos/services/dashboard/ + vessel.env created
- [✅] d3kos-dashboard.service restarted and active
- [✅] HTTP 200 at localhost:3000 — Flask serving new template ✓
- [✅] /status: all 6 indicators up (avnav, gemini, ai_bridge, signalk, ollama, internet) ✓
- [ ] Visual verify: v12 layout on Pi screen (Don)
- [ ] Row toggle BOTH default — no nav row flash (Pi screen, Don)
- [ ] Day/night manual override persists across 60s tick (Pi screen, Don)
- [ ] Keyboard demo shortcuts d/n/h/m/1/2/3 (Pi screen, Don)
- [ ] Windowed mode toggle in More menu position 9 (Pi screen, Don)
- [ ] Squeekboard appears on input focus (Pi only — after Step 0)
- [✅] SESSION_LOG.md updated

---

### Session 2 — Live Signal K + AvNav + AI Wiring
**Risk:** MEDIUM | **Status:** TODO

- [ ] instruments.js: Signal K WebSocket `ws://localhost:8099/signalk/v1/stream`
- [ ] All instrument cells wired to Signal K paths (Section 22 of spec)
- [ ] Alert thresholds active: advisory/alert/critical flood states (Section 23)
- [ ] `---` shown for null/disconnected values
- [ ] Status bar ticker updates on alert/critical
- [ ] `updateAlertDots()` — amber dot on hidden tab if alert present
- [ ] Tap advisory/alert cell → Engine Diagnostic overlay opens
- [ ] Next Waypoint cell: polls AvNav POST getleg every 15s
- [ ] Route AI widget: SSE from :3002/stream
- [ ] AI Nav panel: text + voice → POST :3001/ask → chat bubbles
- [ ] SESSION_LOG.md updated

---

### Session 3 — Cameras, More Menu, Onboarding
**Risk:** MEDIUM | **Status:** TODO

- [ ] Cameras tab: connects to /camera/slot/list at :8084
- [ ] Display_in_grid slots shown in 2×2 grid with MJPEG streams
- [ ] Forward watch slot → full-width primary view
- [ ] More menu: remove 3 demo buttons, add Trip Log + Engine Monitor + Settings
- [ ] First-run wizard fires when vessel.env is absent
- [ ] Wizard writes VESSEL_NAME, HOME_PORT, UI_LANG to vessel.env
- [ ] All three sessions verified on Pi screen (visual + touch)
- [ ] SESSION_LOG.md updated
