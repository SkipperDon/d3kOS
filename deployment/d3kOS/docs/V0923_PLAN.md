# d3kOS v0.9.2.3 — UI Remediation Plan
**Version:** v0.9.2.3 | **Status:** APPROVED — PLANNING COMPLETE
**Created:** 2026-03-16 | **Owner:** Donald Moskaluk — AtMyBoat.com
**Supersedes:** v0.9.2.2 (status: NOT APPROVED — investigation complete, issues catalogued below)

---

## Governing Principle

This plan addresses every deficiency identified during Don's investigation of v0.9.2.2.
Questions were asked one at a time. All answers are confirmed by Don.
No implementation begins without explicit "go ahead" / "implement" / "proceed" authorization.
Plan approval and implementation approval are separate events.

---

## Issues Register

| ID | Area | Issue | Decision |
|----|------|-------|----------|
| I-01 | NAV ribbon | Position label not top-aligned | Top-align to match SPEED/DEPTH/COURSE |
| I-02 | NAV ribbon | Position numbers too small | 50% of SOG value size |
| I-03 | NAV ribbon | Next Waypoint label not top-aligned | Top-align, same size as other labels |
| I-04 | NAV ribbon | Next Waypoint value (no data/dest) too small | Same size as position data value |
| I-05 | Bottom nav | HELM permanently highlighted | Only highlight active button; HELM only when overlay open |
| I-06 | Bottom nav | Weather button too small | Increase to match other nav buttons |
| I-07 | HELM overlay | No software mute (stop talking) | Simple toggle button inside HELM overlay; green=talking, grey=muted |
| I-08 | Close buttons | X too light, too small, near screen edge | All X buttons: 48×48px min, inset from edges, dark high-contrast, bold — entire app |
| I-09 | More popup | Icons ~half bottom-nav size | Scale icons to match bottom nav icon size |
| I-10 | More popup | Fonts too small | Scale fonts to match bottom nav label size |
| I-11 | Weather | Conditions panel lost in v0.9.2.2 | Restore as left-side overlay panel (25-30% width) over AvNav |
| I-12 | Weather | Panel displaces AvNav and ribbons | Overlay only — ribbons stay full width, AvNav visible on right |
| I-13 | Weather | Toggle behaviour | Single Weather button tap shows/hides panel |
| I-14 | Marine Vision | "Leave app?" dialog appears | Suppress beforeunload in HELM when navigating internal routes |
| I-15 | Boat Log | "Leave app?" dialog appears | Same fix as I-14 |
| I-16 | Boat Log | Fonts inconsistent with main app | All boat log text: Bebas Neue / Chakra Petch, same sizing as dashboard |
| I-17 | Boat Log | Automatic engine capture missing | Event-driven + 30-min snapshots while engine running |
| I-18 | Dropdowns | Too small for touch across all pages | All selects 3× larger, touch-friendly, all pages |
| I-19 | Global | Font inconsistency across pages | Bebas Neue / Chakra Petch enforced on all pages |

---

## Architecture Decisions

### Weather Panel (I-11, I-12, I-13)
- **Type:** Left-side overlay panel, 25-30% of screen width
- **Behaviour:** Slides over AvNav when Weather button tapped. ENGINE and NAV ribbons stay full width at all times.
- **Dismiss:** Tap Weather button again — panel slides out
- **Data source:** Open-Meteo API (free, no key) — same as original weather.html
- **Data shown (vertical stack):**
  - Weather alerts (orange = warning, red = critical, blinking)
  - Wind speed, direction, gusts
  - Wave height, direction, period, sea state
  - Barometric pressure, temperature, humidity, visibility, precipitation
- **Auto-log:** Weather snapshot to boat log every 30 minutes while panel is open (restored from v0.9.2)
- **GPS:** Reads from Signal K `navigation.position`; falls back to Lake Simcoe (43.4167, -79.3333)

### Leave App Dialog Fix (I-14, I-15)
- **Root cause:** HELM's `beforeunload` event fires on any full-page navigation
- **Fix:** Clear `beforeunload` handler before navigating to internal routes (`/boat-log`, `/marine-vision`, all internal hrefs)
- **Architecture unchanged:** Pages remain full-page Flask routes — correct for 10.1" display

### Boat Log Engine Capture (I-17)
- **Engine running detection:** RPM > 0 from Signal K `propulsion.*.revolutions`
- **Capture events:**
  - Engine start (RPM transitions 0 → >0)
  - Every 30 minutes while engine running
  - Engine stop (RPM transitions >0 → 0)
  - Alert threshold crossed (oil pressure low, coolant high, battery low)
- **Data captured per entry:** timestamp, RPM, oil pressure, coolant temp, fuel level, battery voltage, GPS position
- **Storage:** localStorage (same as voice notes) + POST to boatlog-export-api.py :8095
- **Data growth:** ~5 entries per 2-hour passage. 90-day auto-archive.
- **Implementation:** New JS module `boatlog-engine.js` loaded on boat-log.html

### HELM Software Mute (I-07)
- **Type:** Simple toggle — one tap mutes, one tap unmutes
- **Location:** Inside HELM overlay
- **Visual state:** Speaker icon — green = talking active, grey = muted
- **Behaviour:** Mutes TTS/espeak-ng output only. HELM still listens and processes.
- **Persistence:** Stored in localStorage `d3kHelmMute` — survives page reload

### Close Button Standard (I-08)
- **Size:** Minimum 48×48px touch target (AODA compliant)
- **Position:** Minimum 24px inset from all screen edges (clear of physical frame)
- **Colour:** Dark — `rgba(0,0,0,0.85)` background, white ✕ symbol, 2px solid border
- **Weight:** Font-weight 700, font-size 24px minimum
- **Applied to:** HELM overlay, More popup, weather panel, all modal overlays throughout app

---

## Session Plan (5 Sessions)

### Session A — NAV Ribbon + Nav Active State + Leave App Fix
**Files:** `index.html`, `d3kos.css`, `helm.js`
**Risk:** LOW
**Items:** I-01, I-02, I-03, I-04, I-05, I-06, I-14, I-15
**Scope:**
1. NAV ribbon CSS — Position and Next Waypoint cells: `vertical-align: top`, `align-items: flex-start`
2. Position value font-size = 50% of SOG `.ic-l` value (target ~16px Bebas if SOG is 32px)
3. Next Waypoint value font-size = same as position data
4. Bottom nav active state — JS tracks last-tapped button, applies `.nb-active` class to that button only
5. HELM `.nb-active` only added when HELM overlay `openHelm()` is called; removed on `closeHelm()`
6. Weather button width/padding increased to match Dashboard/Marine Vision/Boat Log buttons
7. `helm.js` — clear `beforeunload` before any internal `window.location.href` navigation
8. CSS cache-bust: `?v=10`
**Deploy:** SCP to Pi, restart d3kos-dashboard, visual verify

---

### Session B — Close Buttons + More Popup + Dropdowns
**Files:** `d3kos.css`, `index.html`, `settings.html`, `boat-log.html`, `marine-vision.html`, `setup.html`, `upload-documents.html`, `manage-documents.html`, `ai-navigation.html`, `engine-monitor.html`
**Risk:** LOW
**Items:** I-08, I-09, I-10, I-18, I-19
**Scope:**
1. CSS `.close-btn` universal class — 48×48px, inset, dark, bold — applied to all X buttons
2. More popup — icon font-size scaled to match bottom nav (currently ~24px emoji → target 40px+)
3. More popup — label font-size scaled to match bottom nav labels (currently small → target 20px+)
4. All `<select>` elements — global CSS rule: min-height 52px, font-size 20px, padding 8px 16px
5. Bebas Neue / Chakra Petch enforced via body-level CSS on all page templates
6. CSS cache-bust: `?v=11`
**Deploy:** SCP to Pi, restart d3kos-dashboard, visual verify

---

### Session C — HELM Mute + Weather Overlay Panel
**Files:** `helm.js`, `index.html`, new `static/js/weather-panel.js`, `d3kos.css`
**Risk:** MEDIUM (new component)
**Items:** I-07, I-11, I-12, I-13
**Scope:**
1. `helm.js` — add `helmMuted` flag, mute button in HELM overlay, toggle TTS on/off, persist to localStorage
2. `weather-panel.js` — new JS module:
   - Reads GPS from Signal K REST `navigation.position`
   - Fetches Open-Meteo weather + marine API (same endpoints as original weather.html)
   - Builds vertical conditions panel HTML (alerts, wind, sea state, atmospheric)
   - `openWeatherPanel()` / `closeWeatherPanel()` functions
   - Auto-log to boatlog-export-api.py :8095 every 30 min while panel open
3. `index.html` — weather panel `<div>` added as left-side overlay, hidden by default
4. `index.html` — Weather bottom nav button wired to `openWeatherPanel()` / `closeWeatherPanel()` toggle
5. `d3kos.css` — `.wx-panel` styles: fixed left, top below status bar, bottom above nav bar, 28% width, slides in/out with CSS transition
6. Load order: instruments → theme → overlays → helm → nav → cameras → weather-panel → ai-bridge
7. CSS cache-bust: `?v=12`
**Deploy:** SCP to Pi, restart d3kos-dashboard, visual verify

---

### Session D — Boat Log Overhaul
**Files:** `boat-log.html`, new `static/js/boatlog-engine.js`, `d3kos.css`
**Risk:** MEDIUM (new engine capture logic)
**Items:** I-16, I-17
**Scope:**
1. `boat-log.html` — font rewrite: all text Bebas Neue / Chakra Petch at dashboard-consistent sizes
2. `boatlog-engine.js` — new JS module:
   - Connects to Signal K WebSocket `ws://localhost:8099/signalk/v1/stream`
   - Subscribes to: RPM, oil pressure, coolant temp, battery voltage
   - Detects engine start/stop (RPM threshold)
   - Captures full snapshot on start, every 30 min while running, on stop
   - Captures immediate snapshot on any alert threshold crossing
   - Saves entries to localStorage + POST to boatlog-export-api.py :8095
3. `boat-log.html` — engine entry display in log list (distinct style from voice notes)
4. `boat-log.html` — entry type badge: VOICE / ENGINE / WEATHER / ALERT
5. CSS cache-bust: `?v=13`
**Deploy:** SCP to Pi, restart d3kos-dashboard, visual verify

---

### Session E — Global Font Audit + Full Deploy + Verification
**Files:** All templates, `d3kos.css`
**Risk:** LOW
**Items:** I-19 (final sweep)
**Scope:**
1. Read each template — confirm Bebas Neue / Chakra Petch in use, no Roboto remnants
2. Confirm all font sizes meet IEC 62288 standard (32px labels, 28px nav, 20px forms minimum)
3. Confirm all dropdowns are touch-sized on every page
4. Final CSS cache-bust
5. Full deploy to Pi
6. 16-check verification checklist (same structure as INC-12)
7. SESSION_LOG.md + CHANGELOG.md + version bump to v0.9.2.3
**Deploy:** Full SCP deploy, reboot Pi, verify all 9 routes HTTP 200

---

## Verification Checklist (Session E)

| # | Check | Pass Criteria |
|---|-------|---------------|
| V-01 | NAV ribbon alignment | Position + Next Waypoint labels top-aligned with SPEED/DEPTH/COURSE |
| V-02 | Position number size | Visibly 50% of SOG value size |
| V-03 | Next Waypoint value | Same size as position lat/lon |
| V-04 | Bottom nav active state | Only last-tapped button highlighted |
| V-05 | HELM highlight | Only highlighted when HELM overlay is open |
| V-06 | HELM mute | Tap mute → HELM stops talking; tap again → resumes |
| V-07 | Close buttons | All X buttons: visible, dark, bold, not at screen edge, 48×48px+ |
| V-08 | More popup icons | Icons match bottom nav size |
| V-09 | More popup fonts | Fonts match bottom nav label size |
| V-10 | Weather panel | Opens left-side overlay; ribbons stay full width; AvNav visible |
| V-11 | Weather data | Wind, wave, atmospheric, alerts all displayed |
| V-12 | Weather auto-log | Entry in boat log after 30 min with panel open |
| V-13 | Leave app dialog | No dialog when tapping Marine Vision or Boat Log |
| V-14 | Boat log fonts | Bebas Neue / Chakra Petch, consistent with dashboard |
| V-15 | Engine auto-capture | Entry appears in boat log within 30 min of engine start |
| V-16 | Dropdowns | All selects touch-friendly (52px+ height) on all pages |

---

## Multi-Session Rules

- **Read this plan at the start of every session** before touching any file
- **Read PROJECT_CHECKLIST.md** — check which sessions are complete
- **Read SESSION_LOG.md (last 3 entries)** — context from prior sessions
- **Each session is self-contained** — can be paused and resumed without loss
- **Do not start Session B work in Session A** — complete and verify each session before proceeding
- **Commit at end of every session** — local only, no push

---

## What This Plan Does NOT Change

- Flask routing architecture — pages remain full-page routes
- Port assignments — all ports unchanged
- Signal K integration — WebSocket at :8099 unchanged
- AvNav integration — iframe at :8080 unchanged
- AI bridge — :3002 unchanged
- Gemini proxy — :3001 unchanged
- Boat log API — boatlog-export-api.py at :8095 unchanged (extended only)
- Camera system — unchanged

---

*Plan written: 2026-03-16 | Based on Don's investigation findings and Q&A session*
*Methodology: AAO v1.1 — risk classified per action, pre-action statements required*
