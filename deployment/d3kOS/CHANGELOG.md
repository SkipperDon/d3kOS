# d3kOS Changelog

Milestone entries only. Minor session work goes in SESSION_LOG.md.

---

## [v0.9.2.2] — 2026-03-14 — Frontend UI Rebuild Complete

### New UI (v12 Design System)
- Full dashboard rebuild from mockup v12 — Bebas Neue numerals, Chakra Petch UI, white day / near-black night
- 3-way instrument row toggle: BOTH / ENGINE / NAV
- HELM voice overlay button — protrudes 24px above nav bar, amber when listening
- Day/night manual override with `manualTheme` flag (auto-theme never clobbers manual selection)
- JS split into 5 modules: `instruments.js`, `theme.js`, `helm.js`, `overlays.js`, `nav.js`

### Live Signal K Integration
- All 10 instrument cells wired to `ws://localhost:8099/signalk/v1/stream`
- Auto-reconnect every 5 s on drop
- Advisory / alert / critical flood states with amber status bar ticker
- Next Waypoint cell: polls AvNav every 15 s, haversine distance + ETA calculation
- GPS position exposed as `window.d3kGpsLat` / `window.d3kGpsLon` for weather tab

### AI Navigator Panel
- Real AI chat panel — no demo/fake content
- POST to `:3001/ask` — Gemini online, Ollama fallback
- Voice input via Web Speech API (HELM button + split-pane mic)
- Source label updates dynamically after first response: GEMINI or OLLAMA
- Route AI widget via SSE from `:3002/stream`

### Weather Tab
- Live Windy embed (free public embed — no API key required)
- Three overlays: Sea State (waves), Radar (rain/nowcast), Wind
- Uses GPS position from Signal K; falls back to home port coordinates

### Cameras Tab
- Polls `/camera/slots` at `:8084` (Marine Vision camera overhaul API)
- Forward watch slot — full-width primary view
- Grid slots — 2×2 layout with 500 ms frame refresh

### More Menu (Production Layout)
- Removed all demo/test buttons
- Added: AvNav Charts, AI Navigation, Engine Monitor, Trip Log, Settings, OpenCPN, Windowed Mode

### AvNav Chart Fix
- Rewrote `osm-online.xml` — removed European bounding box, global coverage, HTTPS tile URLs
- OpenStreetMap + OpenSeaMap nautical overlay now available worldwide

### First-Run Onboarding Wizard
- Fires when `vessel.env` is absent (redirect to `/setup`)
- Fields: Vessel Name, Home Port, Dashboard Language (18 options)
- Chart configuration section: shows OSM + OpenSeaMap pre-configured, live AvNav status check
- Writes `vessel.env`, reloads runtime env vars, redirects to dashboard

### Bug Fixes
- wait-for-signalk.sh stale URL (:3000 → :8099) — Node-RED stuck on boot
- keyboard-api.py windowed toggle — correct labwc keybinding, correct Chromium app_id
- 5 stale SK WebSocket URLs in legacy pages fixed
- AODA: nav/HELM labels bumped to 20 px, touch targets ≥ 48 px

---

## [v0.9.2.1] — 2026-03-12 — d3kOS Architecture Plan Deployed
- D3KOS_PLAN.md v2.0.0 established in repo
- Directory structure created for Phases 0-4
- UI design reference (mockup v4) deployed to docs/
- Governance stubs initialized: SESSION_LOG.md, PROJECT_CHECKLIST.md, CHANGELOG.md

---
