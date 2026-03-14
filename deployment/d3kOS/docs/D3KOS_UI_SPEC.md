# d3kOS Dashboard — UI/UX & Implementation Specification
**Project:** Helm-OS / d3kOS Marine Dashboard
**Operator:** Skipper Don / AtMyBoat.com
**Document:** `D3KOS_UI_SPEC.md`
**Version:** 1.0.0
**Created:** 2026-03-13
**Methodology:** AAO v1.1 | Master AI Engineering Standard
**Status:** APPROVED — implement from this document

---

## CLAUDE CODE: HOW TO USE THIS DOCUMENT

Read this document fully at the start of every d3kOS dashboard session.
This is the single source of truth for all UI decisions.
Do not deviate from locked decisions without explicit approval from Don.
If Don asks for something that conflicts with a locked decision, flag the conflict before implementing.

The reference mockup is `d3kos-mockup-v12.html`.
All new dashboard code must match the design language, sizing, and behaviour described here.

**ADDENDUM:** Read `D3KOS_UI_SPEC_ADDENDUM_01.md` immediately after this document.
Where the addendum conflicts with this document, the addendum wins.

---

## 1. PROJECT CONTEXT

d3kOS is a custom marine helm dashboard running on a Raspberry Pi aboard MV [VESSEL_NAME].
It runs fullscreen in Chromium on a 10.1" 1000-nit display mounted at the helm.

**Primary users:** Captain Don, operating underway — wet hands, gloves possible, boat moving, sun on screen.

**Core principle:** Every design decision must serve a captain operating a moving vessel in direct sun.
Nothing is decorative unless it earns its place.

---

## 2. TECHNOLOGY STACK

| Component | Technology |
|---|---|
| Dashboard | Flask (Python) · HTML/CSS/JS single-page app |
| Fonts | Bebas Neue (all numerals) · Chakra Petch (all UI labels) |
| Browser | Chromium `--app --start-maximized` — NOT `--kiosk` (see Addendum Section C) |
| Display | 10.1" 1000-nit touchscreen |
| AI proxy | Gemini 2.5 Flash via Flask proxy at :3001 |
| AI fallback | Ollama at 192.168.1.36:11434 (offline) |
| Charts | AvNav at :8080 (iframe embedded) |
| Vessel data | Signal K WebSocket at ws://localhost:8099 |

---

## 3. PORT ASSIGNMENTS — SINGLE SOURCE OF TRUTH

| Service | Port | Notes |
|---|---|---|
| d3kOS Dashboard | **3000** | Flask app — the main UI |
| Gemini AI Proxy | **3001** | Flask proxy — handles Gemini + Ollama routing |
| d3kOS AI Bridge | **3002** | Phase 5 — deployed 2026-03-13 |
| AvNav Charts | **8080** | Installed 2026-03-13 — avnav 20250822 |
| Signal K | **8099** | Confirmed 2026-03-13 — migrated from :3000 |
| keyboard-api | **8087** | Window/keyboard control service |
| Ollama (LAN) | **192.168.1.36:11434** | Offline AI fallback |

---

## 4. HARD RULES — NEVER VIOLATE

1. **Never push to GitHub** — local commits only
2. **Never touch OpenPlotter** (:8081) or its configuration
3. **Never modify AvNav core files** — read-only integration only
4. **Never commit .env files** — always in .gitignore
5. **OpenCPN is frozen** — menu entry exists, do not modify
6. **Ollama first** before any Gemini API call (proxy handles this)
7. **Never store user query text** — token counts only
8. **Signal K is port 8099** — confirmed 2026-03-13
9. **AvNav install: apt from free-x.de trixie** — OpenPlotter not installed on this Pi; standalone apt is correct
10. **AvNav API uses POST not GET** — confirmed on this Pi, GET returns 501
11. **Never use `--kiosk` or `--start-fullscreen`** — both modes place Chromium on the Wayland fullscreen layer, above Squeekboard, making the on-screen keyboard permanently invisible. Use `--app --start-maximized` exclusively. See Addendum Section C.

---

## 5. VESSEL NAME

The dashboard currently displays **MV SERENITY** as a placeholder.
This must be replaced with a configurable value read from:
```
/home/boatiq/Helm-OS/deployment/d3kOS/config/vessel.env
VESSEL_NAME=Your Vessel Name
HOME_PORT=Your Home Port
UI_LANG=en-GB
```
The vessel name appears in:
- Status bar (top left, after d3kOS brand)
- Slide-up More menu title
- All AI prompts as `{VESSEL_NAME}`
- TTS audio announcements
- Voyage log entries

---

## 6. DISPLAY & TOUCH SIZING MANDATE

Every dimension below is a hard minimum. Do not reduce them.

| Element | Minimum Size | Reason |
|---|---|---|
| Status bar height | 48px | Always visible, informational only |
| Instrument row height | 120px | Readable at arm's length in sun |
| Primary instrument numeral | 72px (Bebas Neue) | Glanceable at helm, polarised sunglasses |
| Unit / supporting text | 14px | Secondary but readable |
| Label (category above value) | 11px uppercase, 0.16em spacing | Dim, spaced — supporting role only |
| Bottom nav bar height | 104px | Fat thumb target |
| HELM button protrusion above nav | 24px | Physically dominant, no ambiguity |
| Minimum touch target | 80 × 80px | Gloved hands on moving vessel |
| Modal action buttons | 64px tall, 18–20px text | Emergency use — must not be missed |
| Split pane mic button | 72px circle | One-tap voice in cramped AI panel |
| Row toggle pill buttons | 36px tall | Quick access, still finger-safe |

---

## 7. COLOUR SYSTEM

One accent colour. Used precisely. No palette drift.

### Day Mode (`:root`)
```css
--bg:       #FFFFFF   /* pure white — reflects in direct sun */
--panel:    #F0F4F0   /* instrument panel background */
--cell:     #FFFFFF   /* individual instrument cells */
--ink:      #040C04   /* primary text */
--ink2:     rgba(4,12,4,.52)  /* secondary text */
--ink3:     rgba(4,12,4,.28)  /* labels, dim text */
--g:        #003A00   /* green — base */
--g-txt:    #004400   /* green — on white surfaces */
--g-dim:    rgba(0,58,0,.06)  /* green tint backgrounds */
--g-bdr:    rgba(0,58,0,.16)  /* green borders */
--bar:      #003200   /* status bar background */
```

### Night Mode (`[data-night]` on body)
```css
--bg:       #020702
--panel:    #070E07
--cell:     #0B130B
--ink:      #D6EDD6
--g:        #00C400   /* brighter green — readable on dark */
--g-txt:    #00CC00
--bar:      #001A00
```

### Alert System — FLOOD approach
Alerts change the ENTIRE cell background. Not a subtle glow. Unmissable.

| State | Background | Border | Numeral colour |
|---|---|---|---|
| Advisory | #FFF6DC (amber tint) | #C47B00 animated | #7A4400 |
| Alert | #FFF2EC (orange tint) + pulse | #C03A00 animated | #8B2A00 |
| Critical | #FFF2F2 (red tint) + fast pulse | #BB0000 animated | #8A0000 |

**Night mode:** Use rgba backgrounds for the same tiers — see CSS variables in v12.

**Animation rules:**
- Advisory: border opacity pulses slowly (2s ease-in-out infinite)
- Alert: full cell background + border pulses at 1.3s
- Critical: fast pulse at 0.65s, unmissable

**Tapping an advisory/alert cell** opens the Engine Diagnostic overlay immediately.
The cell must be obviously tappable — add `cursor:pointer` and `:active` state.

---

## 8. TYPOGRAPHY

```css
/* Numerals — all instrument values */
font-family: 'Bebas Neue', sans-serif;

/* UI — all labels, buttons, text, menus */
font-family: 'Chakra Petch', sans-serif;
```

Load via Google Fonts:
```html
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Chakra+Petch:wght@400;500;600;700&display=swap" rel="stylesheet">
```

**Never use:** Inter, Roboto, Arial, system-ui, or any other font.
Bebas Neue and Chakra Petch are the only permitted fonts in d3kOS.

---

## 9. LAYOUT STRUCTURE

```
┌─────────────────────────────────────────┐
│  STATUS BAR (48px)                      │  ← always visible, dark green bg
├─────────────────────────────────────────┤
│  ROW TOGGLE STRIP (48px)                │  ← BOTH / ENGINE / NAV pill
├─────────────────────────────────────────┤
│  INSTRUMENT ROW (120px)                 │  ← one or both rows visible
│  (hidden if toggle selects other row)   │
├─────────────────────────────────────────┤
│                          │              │
│   CHART PANE             │  SPLIT PANE  │  ← split pane: AI Nav / Weather / Cameras
│   (AvNav iframe)         │  (optional)  │
│                          │              │
│   [Route AI strip]       │              │  ← collapsible at bottom of chart
├─────────────────────────────────────────┤
│  BOTTOM NAV (104px) + HELM protrudes    │  ← Charts · Weather · AI Nav · HELM · Cameras · More
└─────────────────────────────────────────┘
```

**The instrument panel (rows + toggle) is structural.**
It does NOT move when the user switches between Charts, Weather, AI Nav, or Cameras.
It is always visible on every screen. This is intentional and locked.

---

## 10. INSTRUMENT PANEL

### Row Toggle Strip (48px)

A three-way pill toggle above the instrument rows:

```
[ ⚙ + 🧭 BOTH ] [ ⚙ ENGINE ] [ 🧭 NAV ]     Engine + Nav
```

- Default on load: **BOTH** (both rows visible)
- Active button: dark green background, white text
- Inactive buttons: white background, dim text
- Right side label shows current mode: "Engine + Nav" / "Engine instruments" / "Navigation instruments"

**Alert dot on inactive tab:**
If a row is hidden and one of its cells has an advisory/alert/critical state,
a small amber dot appears on that tab's button. This prevents silent hidden alerts.

```javascript
// Re-evaluate after any cell state change
function updateAlertDots() {
  const hasEngineAlert = !!document.querySelector('#rowEngine .ic.adv, #rowEngine .ic.alrt, #rowEngine .ic.crit');
  const hasNavAlert    = !!document.querySelector('#rowNav .ic.adv, #rowNav .ic.alrt, #rowNav .ic.crit');
  const engineVisible  = !document.getElementById('rowEngine').classList.contains('hidden');
  const navVisible     = !document.getElementById('rowNav').classList.contains('hidden');
  document.getElementById('engineAlert').classList.toggle('show', !engineVisible && hasEngineAlert);
  document.getElementById('navAlert').classList.toggle('show',    !navVisible && hasNavAlert);
}
```

### Engine Row Cells (left to right)

| Cell | Label | Value format | Unit | Notes |
|---|---|---|---|---|
| RPM | RPM | `####` | rev / min | Signal K: `propulsion.0.revolutions` × 60 |
| Trim | Trim | `+##°` or `-##°` | degrees | Signal K: `propulsion.0.trimTabPosition` |
| Oil Press | Oil Press | `##` | PSI · normal/low | Normal 45–65. Advisory <30. Critical <20 |
| Coolant | Coolant | `##°` | C · normal/advisory | Advisory >88°C. Alert >98°C. Critical >105°C |
| Fuel | Fuel | `##%` | ##L · ##h ##m | Derived: level × capacity. AI calculates range |
| Battery | Battery | `##.#` | V · charging/discharging | Advisory <12.2V. Alert <11.8V |

**Coolant cell is ADVISORY by default in the mockup** — demonstrating the amber flood state.
In production it reads Signal K `propulsion.0.coolantTemperature` (Kelvin, convert to °C).

### Nav Row Cells (left to right)

| Cell | Label | Value format | Unit | Notes |
|---|---|---|---|---|
| Speed | Speed | `##.#` | kts · SOG | Signal K: `navigation.speedOverGround` × 1.944 |
| Depth | Depth | `##.#` | metres | Signal K: `environment.depth.belowKeel` |
| Course | Course | `###°` | true | Signal K: `navigation.courseOverGroundTrue` (radians → degrees) |
| Position | Position | `##°##.#N` `##°##.#W` | (stacked coords) | Signal K: `navigation.position` |
| Next Waypoint | ▶ NEXT WAYPOINT | Destination name + distance + ETA + bearing | — | From AvNav currentLeg.json. Wider cell (flex: 1.7) |

### Instrument Cell Behaviour

- **Right-click (or long-press):** Opens cell context menu
- **Tap on advisory/alert/critical cell:** Opens Engine Diagnostic overlay immediately
- **Context menu options:**
  - Change data source
  - Set alert thresholds
  - Mark as Priority 1
  - Schedule full-screen report
  - Hide this cell

---

## 11. STATUS BAR

Height: 48px. Dark green background (`--bar: #003200`). Always visible.

Left to right:
1. `d3kOS` — Bebas Neue 24px white, 0.15em spacing
2. Separator rule
3. `[VESSEL_NAME]` — Chakra Petch 13px, 0.1em spacing, 75% white opacity
4. AI ticker — Chakra Petch 11px, 0.07em spacing, 55% white — scrolls/rotates status messages
5. **HELM pill** — right side, always visible. Shows "HELM" with status dot. Tapping activates voice
6. Day/Night toggle pill — ☀ DAY / ☾ NIGHT
7. Clock — Bebas Neue 22px, HH:MM 24h format

**AI Ticker messages** (rotate every 5.5 seconds, fade transition):
```
AI FIRST OFFICER ACTIVE — ALL SYSTEMS NOMINAL
GEMINI 2.5 FLASH ONLINE — ROUTE ANALYZED
FUEL RANGE [X]NM AT CURRENT SPEED — [X]H [X]M REMAINING
SIGNAL K STREAM ACTIVE — AIS [N] TARGETS IN RANGE
[When alert active]: ⚠ AIS ALERT — VESSEL CPA 0.18NM IN 4 MINUTES
[When critical]: ⛔ CRITICAL — OIL PRESSURE 8 PSI — TAKE ACTION NOW
```

Alert/critical messages: amber `#FFD454` colour, flash animation at 0.9s step-end.

---

## 12. BOTTOM NAVIGATION BAR

Height: 104px. Six equal columns.

| Position | Icon | Label | Action |
|---|---|---|---|
| 1 | 🗺️ | Charts | Show chart pane, close split |
| 2 | 🌤 | Weather | Open split pane → Weather tab |
| 3 | 🤖 | AI Nav | Open split pane → AI Nav tab |
| **4** | **🎤** | **HELM** | **Activate voice listening** |
| 5 | 📹 | Cameras | Open split pane → Cameras tab |
| 6 | ⋮⋮ | More | Open slide-up menu |

### HELM Button (position 4)

This button is physically and visually dominant. Rules:
- Background: `var(--g-txt)` — dark green in day, bright green in night
- Protrudes 24px above the nav bar top edge (`margin-top: calc(-1 * var(--helm-rise))`)
- Height: `var(--bot-h) + var(--helm-rise)` = 128px total
- Border radius: 18px 18px 0 0 (rounded top, square bottom to meet nav bar)
- Box shadow above: `0 -8px 28px rgba(0,0,0,.22)`
- Icon: 38px (larger than other nav icons at 32px)
- Label: "HELM", 13px, 0.14em letter-spacing, 85% white opacity

**Active/listening state:**
- Background changes to `var(--alrt)` (amber/orange)
- Box shadow pulses
- Label animation: `flash` keyframe

No `::after` bottom line indicator — the protrusion IS the indicator.

**Active/selected state for other nav buttons:**
3px green line appears at the bottom edge.

---

## 13. HELM VOICE INTERFACE

Wake word: **"Helm"** (always listening in production — Web Speech API)
Also activated by tapping the HELM nav button or the HELM pill in the status bar.

### Helm Listening Overlay (fullscreen)

When activated:
- Background: `rgba(0,0,0,.78)` with `backdrop-filter: blur(10px)`
- Centre: 160px circular button with mic emoji, deep green bg, 3 expanding ring waves
- Below ring: 7-bar animated waveform (bars animate height with staggered delays)
- Title: "HELM IS LISTENING" — Bebas Neue 42px white, 0.18em spacing
- Subtitle: "Ask any question — or give a command" — Chakra Petch 16px 50% white
- Cancel button: 30px radius pill, `rgba(255,255,255,.1)` bg, 16px text
- Auto-cancel after 10 seconds of silence (production) / 3.5 seconds (demo)

### After Voice Captured

1. Overlay closes
2. Status bar ticker updates immediately: `HELM HEARD: "[QUERY]" — RESPONDING IN AI PANEL`
3. AI dot in HELM pill pulses
4. Split pane opens to AI Nav tab
5. Response appears in AI chat bubbles
6. If AI panel was already open: response appends to existing conversation

### AI Panel Voice Input (split pane)

72px circle mic button (`mic72` class).
Tap to activate: button turns amber, label changes to ⏹ (stop).
On silence detection (3s): field populates with transcribed text, button resets.

Voice language is set via `UI_LANG` in vessel.env. See Addendum Section C 19.8.

---

## 14. SPLIT PANE

Opens from right side of chart pane when any non-chart nav button is tapped.
Width: `clamp(340px, 38vw, 440px)` — adapts to screen width.
3 tabs: AI Nav · Weather · Cameras. Close (✕) button always visible.

### AI Nav Tab

```
┌──────────────────────────────────────┐
│ ● GEMINI 2.5 FLASH · ONLINE  OLLAMA ▸│  ← status bar
├──────────────────────────────────────┤
│ [scrollable chat messages]           │
│                                      │
│ me: [user question bubble]           │
│ bot: [AI response bubble]            │
│      - meta: model · tokens · stored │
│                                      │
├──────────────────────────────────────┤
│ [72px MIC]  [72px tall text field]   │  ← voice input row
└──────────────────────────────────────┘
```

Chat bubbles:
- User: `var(--g-dim)` background, green border, bold text
- AI: `var(--panel)` background, rule border, ink2 colour text
- Meta line: 10px, ink3, letter-spaced — shows model + token count + "not stored"

Text field: 72px tall, 18px Chakra Petch, green focus border.

### Weather Tab

Two sub-buttons: Sea State | Radar (56px tall, finger-safe)
Placeholder frame for Windy embed (16/9 aspect ratio)
In production: `<iframe src="https://embed.windy.com/..." />`

### Cameras Tab

2×2 grid of 4/3 placeholder frames
In production: MJPEG stream iframes from the slot/hardware camera system at :8084

---

## 15. AI FIRST OFFICER OVERLAYS

### Proactive Alert Card

Slides in from top of screen (below status bar) when AI detects a situational issue.
Does not block the chart — slides in as a card.

Structure:
```
5px stripe (alert colour)
Overtitle: "AI FIRST OFFICER · SITUATIONAL ALERT"  10px spaced
Title: Large (Bebas Neue 32px)
Body: 17px Chakra Petch, line-height 1.75
Buttons: ACKNOWLEDGE (primary 64px) | ASK AI MORE (secondary 64px) | Dismiss (ghost)
```

Buttons must be 64px tall minimum (emergency use).
Primary button background: `var(--alrt-bdr)`.
Border matches alert tier (advisory/alert/critical).

### Engine Diagnostic Overlay

Full-screen backdrop, centred card.
Triggered by tapping any advisory/alert cell OR from More menu.

Structure:
```
Header: alert-coloured background, icon + "AI ENGINE DIAGNOSTIC" + fault title
Body:
  3-column readings grid (44px Bebas Neue values, good/bad states)
  AI Analysis box (green tint bg, green label, 16px analysis text)
  3 action buttons (64px tall):
    PRIMARY — recommended action (e.g. "REDUCE TO 1800 RPM")
    INFO — "FULL AI BRIEF" → opens AI panel
    DISMISS — "MONITOR · DISMISS"
```

### Scheduled Position Report (full-screen)

Triggered automatically on schedule (default: every 2 minutes when underway).
Tap anywhere to dismiss. Auto-dismisses after 4 seconds.

Structure:
```
Label: "Scheduled Position Report" (small, spaced, dim)
Speed: clamp(72px,14vw,130px) Bebas Neue — the dominant number
Course: clamp(48px,9vw,80px) — secondary
Position: clamp(28px,4.5vw,50px) — lat/lon in Bebas Neue
4s progress bar → auto-dismiss
"Tap anywhere to dismiss"
```

### Critical Screen

The entire viewport pulses red. Background animates from transparent to `rgba(180,0,0,.22)` at 0.65s.
An 8px red border surrounds the entire screen.
Centred card with:
- Oil Pressure / fault title in Bebas Neue 42px red
- 90px value (e.g. "8 PSI") — massive
- Plain text instructions (reduce RPM, check oil, etc.)
- Full-width 72px ACK button: "ACKNOWLEDGE — TAKING ACTION NOW"

**Cannot be swiped away.** Must tap the ACK button.

### Port Arrival Banner

Slides down from top of screen at 2.0nm from destination.
Not fullscreen — compact card, allows chart still visible.

Sections: Fuel dock · Marina · Customs · Anchorage · Approach hazards
Footer: distance indicator + "Full Briefing in AI →" button (52px tall)

---

## 16. SLIDE-UP MORE MENU

Triggered by More button (⋮⋮) in nav bar.
Full-width sheet slides up from bottom with spring animation.
Black backdrop dismisses on tap.
Drag handle at top.
Header: "d3kOS · [VESSEL_NAME]"

**3×3 grid of 120px-min buttons:**
- AvNav Charts (:8080)
- AI Navigation
- Engine Monitor
- Trip Log
- Settings
- [3 demo buttons for testing in development]
- **Position 9 (bottom right): Windowed Mode toggle** — see Addendum Section C 19.7

Button structure: 32px icon + bold label + dim sub-label
`:active` state: green tint background, green border

---

## 17. ROUTE AI WIDGET

A strip pinned to the bottom of the chart pane.
Visible when an AvNav route is active. Dismissible with ✕.

```
[🧭 Route AI]  [Analysis text...]  [GEMINI badge]  [✕]
```

In Phase 5: populated by AI Bridge SSE stream from :3002.
Before Phase 5: static placeholder text.

States:
- **ACTIVE** — shows AI analysis text, model badge, timestamp
- **NO ROUTE** — "No active route — load a route in AvNav to enable analysis"
- **UPDATING** — "Analyzing route…" with spinner
- **OFFLINE** — shows Ollama badge instead of Gemini

---

## 18. DAY / NIGHT MODE

**Auto-switching:** 07:00 → Day, 20:00 → Night. Checked every 60 seconds.

**Manual override:** Day/Night toggle pill in status bar. Manual selection persists
until the user selects the other option. Do NOT implement an "auto" timer that
overrides a manual selection mid-session.

**Implementation — manual flag required:**
```javascript
let manualTheme = false;

function setTheme(t, manual = false) {
  if (manual) manualTheme = true;
  document.body.toggleAttribute('data-night', t === 'night');
  // update toggle button states
}

function autoTheme() {
  if (manualTheme) return;  // never override manual selection
  const h = new Date().getHours();
  setTheme(h >= 7 && h < 20 ? 'day' : 'night');
}
autoTheme();
setInterval(autoTheme, 60000);
```

**Theme switching:** `[data-night]` attribute on `<body>`.
Day is the default (no attribute). Night adds the attribute.

**Transition:** `background .3s, color .3s` on html and body — smooth, not jarring.

---

## 19. DISPLAY MODE — MAXIMISED APP WINDOW (WAYLAND / LABWC)

**This section is fully defined in `D3KOS_UI_SPEC_ADDENDUM_01.md` Section C.**

Summary: d3kOS runs Chromium as `--app --start-maximized`. Never `--kiosk` or `--start-fullscreen`.
See the addendum for the complete launch script, labwc window rules, Squeekboard setup, and wlrctl windowed toggle.

---

## 20. ONBOARDING WIZARD

First-run wizard that sets:
- Vessel name and home port
- Hull type (powerboat / sailboat / RIB / trawler)
- Engine configuration (single / twin / twin + generator)
- Primary use (coastal day trips / overnight / bluewater / racing)

Wizard persists to `/home/boatiq/Helm-OS/deployment/d3kOS/config/vessel.env`
and drives which instrument cells are shown by default in each row.

Dashboard reads this file on startup. If file missing → show wizard.

---

## 21. KEYBOARD SHORTCUTS (development / testing)

| Key | Action |
|---|---|
| D | Set day mode |
| N | Set night mode |
| H | Activate Helm listening overlay |
| M | Open More menu |
| 1 | Open AI Nav panel |
| 2 | Open Weather panel |
| 3 | Open Cameras panel |
| A | Demo: AIS proactive alert |
| G | Demo: Engine diagnostic (Coolant) |
| C | Demo: Critical screen (Oil Pressure) |
| R | Demo: Scheduled position report |
| P | Demo: Port arrival banner |
| Escape | Close all overlays / menus |

---

## 22. SIGNAL K DATA MAPPING

All instrument values read from Signal K WebSocket at `ws://localhost:8099/signalk/v1/stream`.

**Unit conversions required:**
```python
# Speed: m/s → knots
sog_kts = signalk_value * 1.944

# Course: radians → degrees
cog_deg = signalk_value * (180 / math.pi)

# Temperature: Kelvin → Celsius
temp_c = signalk_value - 273.15

# Pressure: Pascals → PSI
pressure_psi = signalk_value * 0.000145038
```

**Expected Signal K paths (verified on Pi 2026-03-13):**

| Display | Signal K path |
|---|---|
| Speed SOG | `navigation.speedOverGround` |
| Course COG | `navigation.courseOverGroundTrue` |
| GPS position | `navigation.position` (lat/lon object) |
| Depth | `environment.depth.belowKeel` |
| Coolant temp | `propulsion.0.coolantTemperature` |
| Oil pressure | `propulsion.0.oilPressure` |
| Engine RPM | `propulsion.0.revolutions` (×60 for RPM) |
| Fuel level | `tanks.fuel.0.currentLevel` (0.0–1.0 × capacity) |
| Battery voltage | `electrical.batteries.0.voltage` |
| Anchor radius | `navigation.anchor.maxRadius` |
| Anchor drift | `navigation.anchor.currentRadius` |

**If a path returns null:** show `---` in the value field, not 0.
**If Signal K disconnects:** all cells show `---`, status bar ticker shows
"SIGNAL K OFFLINE — RECONNECTING"

---

## 23. ALERT THRESHOLD REFERENCE

Default thresholds (configurable via cell context menu):

| Parameter | Advisory | Alert | Critical |
|---|---|---|---|
| Coolant temp | > 88°C | > 98°C | > 105°C |
| Oil pressure | < 30 PSI | < 25 PSI | < 20 PSI |
| Battery voltage | < 12.4V | < 12.0V | < 11.5V |
| Depth | < 3m | < 2m | < 1m |
| Fuel level | < 25% | < 15% | < 10% |

**Cell state changes trigger:**
1. Cell visual update (flood background + animated border)
2. Status bar ticker update
3. At Alert tier: if AI panel is open, AI First Officer generates analysis
4. At Critical tier: full-screen critical overlay fires immediately

---

## 24. FILE STRUCTURE

```
/home/boatiq/Helm-OS/deployment/d3kOS/
├── scripts/
│   └── launch-d3kos.sh        ← Chromium launch script (chmod +x) — see Addendum
├── dashboard/
│   ├── app.py                     ← Flask app (port 3000)
│   ├── templates/
│   │   └── index.html             ← Main UI (implements this spec — v0.9.2.2 rebuild)
│   ├── static/
│   │   ├── css/d3kos.css
│   │   └── js/
│   │       ├── instruments.js     ← Signal K WebSocket + cell updates
│   │       ├── helm.js            ← Voice interface + wake word
│   │       ├── overlays.js        ← All modal/overlay logic
│   │       ├── theme.js           ← Day/Night switching
│   │       └── nav.js             ← Tab/split pane navigation
│   └── config/
│       └── vessel.env             ← VESSEL_NAME, HOME_PORT, UI_LANG (never in git)
├── gemini-proxy/
│   └── proxy.py                   ← AI proxy (port 3001)
├── ai-bridge/                     ← Phase 5 — deployed 2026-03-13
├── docs/
│   ├── D3KOS_UI_SPEC.md           ← THIS DOCUMENT
│   ├── D3KOS_UI_SPEC_ADDENDUM_01.md  ← Wayland/kiosk architecture fix
│   ├── d3kos-mockup-v12.html      ← Canonical reference mockup (v12 build 2)
│   ├── D3KOS_V12_FINDINGS.md      ← Design review findings + build plan
│   └── [other docs]
└── .gitignore                     ← Must include *.env, config/vessel.env
```

**vessel.env contents:**
```
VESSEL_NAME=   (vessel name)
HOME_PORT=     (home port)
UI_LANG=       (BCP 47 locale tag, e.g. en-GB, de-DE, ja-JP)
```

---

## 25. WHAT HAS BEEN BUILT

| File | Description | Status |
|---|---|---|
| `docs/d3kos-mockup-v12.html` | **Canonical reference** — full UI, 3-way row toggle, all overlays, day/night, all demos | Reference only |
| `docs/D3KOS_V12_FINDINGS.md` | Design review findings — bugs, gaps, build plan | Reference |
| `docs/d3kos-mockup-v4.html` | Previous reference (v0.9.2.1 era) — 9-button grid | Superseded |
| `dashboard/app.py` | Flask app :3000 — 9-button hub (v0.9.2.1 era) | To be rebuilt |
| `dashboard/templates/index.html` | 9-button hub (v0.9.2.1 era) | To be replaced by v12 |
| `dashboard/static/css/d3kos.css` | Dark theme, Roboto (v0.9.2.1 era) | To be replaced by v12 |

---

## 26. PHASE STATUS

| Phase | Status | Notes |
|---|---|---|
| 0 — Directory setup | COMPLETE 2026-03-12 | |
| 1 — Pi menu restructure | COMPLETE 2026-03-13 | .desktop files deployed |
| 2 — Dashboard Hub :3000 | COMPLETE 2026-03-13 | Flask app + 9-button hub (v0.9.2.1 design) |
| 3 — Gemini Proxy :3001 | COMPLETE 2026-03-13 | AI proxy live |
| 4 — Settings page | COMPLETE 2026-03-13 | 16-section settings.html deployed |
| 5 — AI+AvNav Bridge :3002 | SOURCE COMPLETE 2026-03-13 | Pi deploy pending |
| **v0.9.2.2 — Frontend UI Rebuild** | **PLANNING 2026-03-13** | **Replaces index.html + d3kos.css with v12 design** |

---

## 27. SESSION START CHECKLIST FOR CLAUDE CODE

At the start of every d3kOS coding session:

```
1. Read this document (D3KOS_UI_SPEC.md) — done
2. Read D3KOS_UI_SPEC_ADDENDUM_01.md — done (addendum wins on conflicts)
3. Read D3KOS_PLAN.md — check phase status
4. Read SESSION_LOG.md — what happened last session
5. Read PROJECT_CHECKLIST.md — what is outstanding
6. Confirm with Don: "I have the spec. Current phase is [X]. Last session [summary]. Ready to proceed?"
7. Never start coding until Don confirms
```

Do not assume anything not stated in this document.
If a design detail is not covered here, ask Don before guessing.

---

*Version 1.0.0 — Written 2026-03-13*
*Deployed to: `/home/boatiq/Helm-OS/deployment/d3kOS/docs/D3KOS_UI_SPEC.md`*
*Owner: Skipper Don / AtMyBoat.com*
*Reference mockup: docs/d3kos-mockup-v12.html*
*Addendum: docs/D3KOS_UI_SPEC_ADDENDUM_01.md*
