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
**Risk:** MEDIUM | **Status:** TODO | **Requires:** Phase 1 complete
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

## Phase 5 — AI + AvNav Integration (DEFERRED — v1.1)
**Status:** LOCKED — do not implement until Phase 4 is stable for one voyage

- [ ] Research AvNav REST API at http://localhost:8080/api
- [ ] Design integration spec
- [ ] Implement: route suggestion, voyage log summarization, condition-aware routing, port arrival briefing, anchor watch AI alerts, chart object explanation

---

## Known Port Reference (from D3KOS_PLAN — immutable)

| Service | Port/URL |
|---------|----------|
| d3kOS Dashboard | localhost:3000 |
| d3kOS Gemini Proxy | localhost:3001 |
| AvNav Charts | localhost:8080 |
| OpenPlotter | localhost:8081 |
| Signal K | localhost:8099 |
| Signal K WS | ws://localhost:8099/signalk/v1/stream |
| Ollama (LAN) | 192.168.1.36:11434 |
| Gemini API | generativelanguage.googleapis.com |
