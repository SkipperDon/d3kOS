# d3kOS v12 Mockup — Findings & Total Recommendation
**Document:** D3KOS_V12_FINDINGS.md
**Version:** 1.0.0
**Date:** 2026-03-13
**Author:** Claude Code / AAO v1.1
**Subject:** Full analysis of d3kos-mockup-v12 (2).html and total build recommendation for v0.9.2.2

---

## 1. THE TWO FILES — WHICH ONE IS CANONICAL

Two v12 files were submitted:

| File | Row Toggle | Default State | Status |
|---|---|---|---|
| `d3kos-mockup-v12.html` | 2-way: ENGINE / NAV | ENGINE only | Earlier draft — discard |
| `d3kos-mockup-v12 (2).html` | 3-way: BOTH / ENGINE / NAV | BOTH (both rows visible) | **Canonical — use this** |

The only meaningful difference between the two files is the row toggle. Everything else — all 967 lines of CSS, all HTML structure, all overlays, all JavaScript — is byte-for-byte identical.

**`d3kos-mockup-v12 (2).html` is the build reference for v0.9.2.2.** All implementation work starts from this file.

---

## 2. WHAT v12 (2) IS

A fully working, self-contained static prototype. Single HTML file, ~1565 lines. Zero runtime dependencies other than Google Fonts (Bebas Neue + Chakra Petch). Every screen, interaction, animation, and overlay is implemented and interactive.

**Open it in any browser. Everything works:**
- Day/Night toggle with smooth transitions
- 3-way instrument row toggle (BOTH / ENGINE / NAV) with alert dot logic
- All 5 overlays: HELM listening, AI alert card, engine diagnostic, position report, critical screen
- Port arrival banner
- Slide-up More menu with spring animation
- Split pane (AI Nav / Weather / Cameras) with tab switching
- Cell context menu on right-click / long-press
- Route AI strip with dismiss
- All keyboard shortcuts (d/n/h/m/1/2/3/a/g/c/r/p/Escape)
- Clock (live), ticker (rotating, 5.5s interval), toast notifications

This is a production-quality UI prototype. It is not a rough sketch. The CSS and HTML structure can go directly into the Flask template with minimal modification.

---

## 3. COMPLETE FINDINGS

### 3.1 Design System — Confirmed Correct

| Token | Day Mode | Night Mode (`[data-night]`) |
|---|---|---|
| Background | `#FFFFFF` (white) | `#020702` (near-black) |
| Panel | `#F0F4F0` | `#070E07` |
| Cell | `#FFFFFF` | `#0B130B` |
| Primary text | `#040C04` | `#D6EDD6` |
| Green accent | `#004400` | `#00CC00` |
| Status bar | `#003200` | `#001A00` |
| Numeral font | Bebas Neue | Bebas Neue |
| UI font | Chakra Petch | Chakra Petch |

Night mode alert colours are brighter/higher-contrast than day — correct for a dark display.
Night mode values have a subtle green glow (`text-shadow: 0 0 20px rgba(0,196,0,.3)`) — intentional, adds readability in darkness.

### 3.2 Layout Structure — Confirmed

```
[STATUS BAR — 48px — always dark green #003200]
[ROW TOGGLE STRIP — 48px — BOTH | ENGINE | NAV pill + hint label]
[ENGINE ROW — 120px — RPM | Trim | Oil Press | Coolant(adv) | Fuel | Battery]
  (hidden when NAV selected)
[NAV ROW — 120px — Speed | Depth | Course | Position | Next Waypoint]
  (hidden when ENGINE selected, both visible when BOTH selected)
[MAIN AREA — flex:1 — fills remaining height]
  [CHART PANE — flex:1 — AvNav iframe placeholder]
    [Route AI strip — absolute, bottom of chart]
  [SPLIT PANE — width:0 closed / clamp(340px,38vw,440px) open]
    [Tab bar — 56px — AI Nav | Weather | Cameras | X]
    [Tab content — flex:1]
[BOTTOM NAV — 104px — Charts | Weather | AI Nav | HELM(+24px) | Cameras | More]
```

Total vertical consumption at 1280x800 (10.1" display):
- 48 + 48 + 120 (one row) + 104 = **320px chrome**, 480px chart (single row mode)
- 48 + 48 + 120 + 120 + 104 = **440px chrome**, 360px chart (BOTH rows)

360px of chart is usable at 1280px wide — acceptable. AvNav is legible at that height.

### 3.3 Instrument Panel — Confirmed

**Engine row cells (left to right):**
| Cell | Displayed Value | Unit line | Alert State |
|---|---|---|---|
| RPM | 2250 | rev / min | Normal |
| Trim | +8° | degrees | Normal |
| Oil Press | 52 | PSI · normal | Normal |
| Coolant | 92° | C · advisory | **ADVISORY** (amber flood, pulsing border) |
| Fuel | 68% | 84 L · 2h 40m | Normal |
| Battery | 13.8 | V · charging | Normal |

**Nav row cells (left to right):**
| Cell | Displayed Value | Notes |
|---|---|---|
| Speed | 18.4 | kts · SOG |
| Depth | 12.1 | metres |
| Course | 245° | true |
| Position | 43°50.5N / 76°19.2W | `.ic-gps` class, 20px stacked Bebas Neue |
| Next Waypoint | Duck Island · 8.3nm | `.ic-wp` flex:1.7, green tint bg, ETA + bearing |

Coolant cell has `onclick="openDiag()"` — tap triggers Engine Diagnostic overlay directly. This is the production behaviour, not just demo behaviour.

### 3.4 Row Toggle — Confirmed 3-Way (v12 (2) only)

```javascript
function showRow(which){
  const showE = which === 'both' || which === 'engine';
  const showN = which === 'both' || which === 'nav';
  // hides/shows rows, sets .on class, updates hint label
  // sets alert dots on hidden tabs if those rows have active alerts
}
showRow('both'); // default on load
```

Default: BOTH rows visible. `rowHint` shows "Both rows" / "Engine instruments" / "Navigation instruments".

Alert dot (`.rp-alert`) appears on ENGINE or NAV tab button if that row is hidden and contains an `.ic.adv`, `.ic.alrt`, or `.ic.crit` cell. Prevents silent hidden alerts.

### 3.5 HELM Button — Confirmed

- Position 4 in 6-column grid
- `margin-top: calc(-1 * var(--helm-rise))` = -24px — protrudes above nav bar
- `height: calc(var(--bot-h) + var(--helm-rise))` = 128px total
- `border-radius: 18px 18px 0 0` — rounded top only
- Background: `var(--g-txt)` (#004400 day / #00CC00 night)
- Active/listening: changes to `var(--alrt)` orange, pulsing box-shadow, label flashes
- The HELM pill in the status bar also activates simultaneously (`.helm-pill.live`)

### 3.6 Overlays — All Confirmed Present and Working

| Overlay | Trigger | z-index | Dismiss |
|---|---|---|---|
| HELM listening | HELM button tap, H key | 800 | Cancel button, 3.5s auto (demo) |
| AI alert card | A key, More > Demo | 600 | ACKNOWLEDGE, ASK AI MORE, Dismiss |
| Engine diagnostic | Coolant cell tap, G key, More > Demo | 650 | 3 action buttons |
| Position report | R key, More > Demo | 700 | Tap anywhere, 4s auto |
| Critical screen | C key, More > Demo | 900 | ACK button only — cannot swipe |
| Port arrival | P key, More > Demo | 590 | X button |

z-index stack (low to high): Instrument panel 200 / Bottom nav 200 / Status bar 300 / More menu backdrop 500 / Port arrival 590 / AI alert card 600 / Engine diagnostic 650 / Position report 700 / HELM listening 800 / Critical screen 900 / Toast 999.

Critical screen (z-index 900) correctly sits above everything. It has an 8px red border surrounding the full viewport and a red pulse animation at 0.65s. Cannot be dismissed by tapping background — only the ACK button works.

### 3.7 More Menu — 3x3 Grid Contents

Current 9 buttons (as built in v12 (2)):

| Position | Label | Action |
|---|---|---|
| 1 | AvNav Charts | toast (placeholder) |
| 2 | AI Navigation | openSplit('ai') |
| 3 | Engine Monitor | toast (placeholder) |
| 4 | Demo: AIS Alert | showAlert() |
| 5 | Demo: Engine Diag | openDiag() |
| 6 | Demo: Pos Report | showPosRpt() |
| 7 | Demo: Arrival | show arrival banner |
| 8 | Demo: Critical | showCrit() |
| 9 | Settings | toast (placeholder) |

Positions 3, 4–8, and 9 are all placeholders. In production: positions 4–8 become Trip Log, Onboarding/Setup, Exit to Desktop, + 2 remaining production items. All demo buttons removed before final deploy.

### 3.8 AI Split Pane — Confirmed

- Status bar: green pill, pulsing dot, "GEMINI 2.5 FLASH · ONLINE", "OLLAMA STANDBY" right-aligned
- Chat bubbles: user (green tint, bold) / AI (panel bg, ink2 text)
- Meta line per AI message: model · tokens · "not stored" — confirmed present
- 72px circle mic button: green bg, turns amber + pulsing when active, shows stop icon
- Text input: 72px tall, 18px Chakra Petch, green focus border
- Voice demo: 3s timeout → populates field with demo text

### 3.9 Route AI Widget — Confirmed

Absolute-positioned strip at bottom of chart pane:
- Tag: "🧭 Route AI" (Bebas Neue 15px)
- Sample text: Kingston Run · 42nm, hazard note, dock info
- GEMINI badge (green pill)
- X dismiss button (slides widget out via `translateY(100%)`)

Wires to AI Bridge at :3002 in production via SSE stream.

---

## 4. BUGS FOUND IN v12 (2)

Two bugs confirmed. Both must be fixed before production deployment.

### Bug 1 — Auto-theme overrides manual selection (CRITICAL)

**Location:** JavaScript, lines 1396–1397
```javascript
function autoTheme(){ setTheme(new Date().getHours()>=7&&new Date().getHours()<20?'day':'night'); }
autoTheme(); setInterval(autoTheme, 60000);
```

**Problem:** The auto-theme timer fires every 60 seconds unconditionally. If the captain manually selects Night mode at 19:45, the timer fires at 19:46 and forces Day mode. The spec (Section 18) explicitly states: "Manual selection persists until the user selects the other option. Do NOT implement an auto timer that overrides a manual selection mid-session."

**Fix required:**
```javascript
let manualTheme = false;
function setTheme(t, manual=false){
  if(manual) manualTheme = true;
  // ... rest of setTheme
}
function autoTheme(){
  if(!manualTheme) setTheme(new Date().getHours()>=7&&new Date().getHours()<20?'day':'night');
}
// Button onclick calls: setTheme('day', true) / setTheme('night', true)
```

### Bug 2 — Nav row starts hidden despite BOTH being the default

**Location:** HTML, line 1048
```html
<div class="irow nav-row hidden" id="rowNav">
```

**Problem:** The nav row has `hidden` class in HTML. `showRow('both')` is called on load (line 1387) and correctly removes it — but there is a flash of the layout without the nav row before the script executes. On a slow Pi, this may be visible.

**Fix required:** Remove the `hidden` class from the nav row in HTML. The `showRow('both')` call on load will set the correct state regardless. Or move `showRow('both')` into a `DOMContentLoaded` listener to guarantee execution order.

---

## 5. GAPS — WHAT v12 (2) DOES NOT CONTAIN

These are intentional placeholders in the mockup that require real implementation.

| Gap | Mockup State | Production Implementation |
|---|---|---|
| AvNav chart | Green placeholder div | `<iframe src="http://localhost:8080" frameborder="0">` |
| Signal K data | Static values in HTML | WebSocket `ws://localhost:8099/signalk/v1/stream` feeding all 11 cells |
| AI responses | Static example bubbles | POST to `http://localhost:3001/ask`, render streamed response |
| Route AI widget | Static sample text | SSE from `http://localhost:3002/route/stream` |
| Vessel name | "MV SERENITY" hardcoded | Read from `config/vessel.env` via Flask, injected as Jinja2 `{{ vessel_name }}` |
| Camera tab | 2 placeholder frames (FORWARD, ENGINE ROOM) | MJPEG streams from existing slot system at :8084 |
| Weather tab | Windy placeholder frame | `<iframe src="https://embed.windy.com/embed2.html?...">` |
| Onboarding | Not present | Flask route `/onboard`, reads `vessel.env`, redirects to `/` when complete |
| Exit to desktop | Not present | More menu item — calls `keyboard-api.py` `/window/windowed` then `window.close()` |
| Alert thresholds | Toast placeholder | Settings page configuration, stored in `config/thresholds.json` |
| Cell data source | Toast placeholder | Settings page configuration |

---

## 6. v12 (2) vs v0.9.2.1 CURRENT DASHBOARD — FULL COMPARISON

### Navigation Model

| | v0.9.2.1 | v12 (2) Target |
|---|---|---|
| Entry screen | 9-button 3x3 hub menu | Instrument panel + chart pane immediately |
| Moving between sections | Navigate to separate screens, back button | Bottom nav bar tabs — everything coexists |
| AI Nav | Navigates away to separate `chat.html` | Split pane opens alongside chart — chart stays visible |
| Weather | Navigates to full-screen Windy or Radar iframe | Split pane tab |
| Cameras | Navigates to full-screen camera view | Split pane tab |
| Settings | Separate full-screen page | Entry via More menu |
| Return path | Back button in status bar | Tab selection or split pane X |

### Visual Design

| | v0.9.2.1 | v12 (2) Target |
|---|---|---|
| Background (default) | Black `#000000` | White `#FFFFFF` |
| Accent colour | `#00CC00` bright green | `#004400` dark green (day) / `#00CC00` (night) |
| Status bar bg | `#0d1117` dark surface | `#003200` dark green |
| Primary font | Roboto | Chakra Petch (UI) + Bebas Neue (numerals) |
| Day/Night modes | Not present | Full dual-mode with auto-switching |

### Screens Present

| Screen | v0.9.2.1 | v12 (2) Target |
|---|---|---|
| Main menu hub | Yes (9-button grid) | **Removed** |
| Instrument panel | No | Yes — always visible, 2 rows x 120px |
| Charts (AvNav) | Full screen | Main pane, always visible |
| AI Navigation | Full screen (separate service) | Split pane tab |
| Weather | Full screen | Split pane tab |
| Cameras | Full screen | Split pane tab |
| Settings | Full screen | Via More menu |
| Offline | Separate offline.html | (Not yet defined in v12) |
| HELM listening | Not present | Full-screen overlay |
| Engine diagnostic | Not present | Modal overlay |
| Critical alert | Not present | Full-viewport pulse overlay |
| AI alert card | Not present | Slide-in card |
| Position report | Not present | Full-screen timed overlay |
| Port arrival | Not present | Slide-in banner |

### What the Current Flask App Retains

These backend components carry forward unchanged — only the frontend template changes:

| Component | Retention |
|---|---|
| `app.py` Flask app at :3000 | Keep — add vessel.env loading, onboarding redirect |
| `gemini_proxy.py` at :3001 | Keep unchanged — `/ask` endpoint already correct |
| `ai_bridge.py` at :3002 | Keep unchanged — route AI widget wires here |
| `connectivity-check.js` | Keep logic — adapt to new status bar (ticker not dots) |
| `panel-toggle.js` | **Superseded** by v12 row toggle — retire |
| `d3kos.css` | **Superseded** by v12 inline CSS extracted to file — retire |
| `index.html` current | **Replace** entirely with v12 template |
| `chat.html` in gemini-nav | **Orphaned** — AI is now inline in split pane |
| `settings.html` | Retain — entry point changes from direct nav to More menu |
| `offline.html` | Retain — still needed when AvNav unreachable |

---

## 7. v12 (2) vs D3KOS_UI_SPEC.md — ALIGNMENT CHECK

| Spec Section | Spec Says | v12 (2) Implements | Status |
|---|---|---|---|
| Fonts | Bebas Neue + Chakra Petch only | Bebas Neue + Chakra Petch only | MATCH |
| Colour tokens | Day white / night dark | Day white / night dark | MATCH |
| Alert flood approach | Whole cell changes colour | Whole cell changes colour | MATCH |
| Status bar height | 48px | 48px (`--sb-h`) | MATCH |
| Row height | 120px | 120px (`--row-h`) | MATCH |
| Bottom nav height | 104px | 104px (`--bot-h`) | MATCH |
| HELM protrusion | 24px | 24px (`--helm-rise`) | MATCH |
| Min touch target | 80x80px | Bottom nav buttons ~80px+ | MATCH |
| Alert buttons | 64px tall | `.btn64 { height: 64px }` | MATCH |
| Split pane width | clamp(340px,38vw,440px) | clamp(340px,38vw,440px) | MATCH |
| Row toggle | 3-way BOTH/ENGINE/NAV, default BOTH | 3-way, `showRow('both')` on load | MATCH |
| Day/Night auto | 07:00→Day, 20:00→Night, manual persists | Auto present, **manual override BUG** | BUG |
| HELM listening | 160px ring, 3 waves, 7 bars, fullscreen | Exactly this | MATCH |
| AI ticker | Rotates every 5.5s, fade | 5.5s setInterval with opacity fade | MATCH |
| Alert dot on hidden tab | Amber dot if hidden row has alert | `.rp-alert.show` logic in showRow() | MATCH |
| Tapping alert cell | Opens Engine Diagnostic immediately | `onclick="openDiag()"` on Coolant cell | MATCH |
| Critical ACK only | Cannot be swiped | No backdrop click handler on `#critSc` | MATCH |
| Port arrival at 2.0nm | Banner trigger | Static demo only (no live trigger) | PLACEHOLDER |
| Position report every 2min | Auto-schedule | Demo only (no timer) | PLACEHOLDER |
| Onboarding wizard | vessel.env, hull type, engine config | Not in mockup | NOT IN MOCKUP |
| Signal K at ws://localhost:8099 | WebSocket path | Not wired (static values) | PLACEHOLDER |
| Vessel name from config | `vessel.env` | "MV SERENITY" hardcoded | PLACEHOLDER |

**Conclusion:** The mockup correctly implements every locked design decision in the spec. The remaining gaps are all live-data wiring, not design decisions.

---

## 8. THE ONE FACTUAL SPEC ERROR THAT AFFECTS THE BUILD

The spec contains this hard rule (Section 4, Rule 9):

> "AvNav install: OpenPlotter Settings only — never standalone .deb"

This rule is wrong for this Pi. AvNav was installed via `apt install avnav` from `http://www.free-x.de/debian trixie main` because OpenPlotter is not installed on this Pi. The correct rule is:

> "AvNav is installed via apt from free-x.de repository. Do not reinstall, do not modify core files."

This does not affect the v12 build — AvNav is already running at :8080. The spec rule needs correcting to prevent confusion in future sessions.

---

## 9. TOTAL RECOMMENDATION

### The Verdict on v12 (2)

**Use it. It is the build.** The mockup is not a sketch — it is a finished UI that needs data wired into it. The CSS design system is complete, production-quality, and marine-grade. Every interaction is correct. Copy the file, convert to a Jinja2 template, wire the data, deploy.

### What Version This Becomes

This is **d3kOS v0.9.2.2**. It replaces the 9-button hub dashboard with a continuous helm interface. The version increment is correct — it is not a new major version because the backend services (Flask, Gemini proxy, AI Bridge, AvNav, Signal K) are all unchanged. Only the frontend template changes.

### The Two Bugs to Fix Before Deploying

1. **Auto-theme manual override** — add `manualTheme` flag to `setTheme()`. Without this fix, Don sets night mode at 20:00, it flips back to day at 20:01.
2. **Nav row flash on load** — remove `hidden` class from nav row HTML. `showRow('both')` handles it.

### Build Plan — 3 Sessions

**Session 1 — Static template (no live data)**

Goal: v12 (2) running on Pi as the Flask dashboard, all interactions working, static placeholder values.

1. Copy `d3kos-mockup-v12 (2).html` to repo as `docs/d3kos-mockup-v12.html` (canonical reference)
2. Fix Bug 1 (auto-theme) and Bug 2 (nav row flash) in the source
3. Convert HTML to Jinja2 template `dashboard/templates/index.html`:
   - Replace `"MV SERENITY"` with `{{ vessel_name }}`
   - Replace `"d3kOS · MV SERENITY"` in More menu with `{{ vessel_name }}`
   - Add `vessel.env` loading to `app.py`
   - Add onboarding redirect: if `vessel.env` missing, serve onboarding wizard
4. Extract inline CSS to `static/css/d3kos.css`
5. Extract inline JS to 4 module files:
   - `static/js/instruments.js` — row toggle, alert dot logic, cell context menu
   - `static/js/helm.js` — HELM overlay, split mic
   - `static/js/overlays.js` — all modal/overlay open/close functions
   - `static/js/nav.js` — bottom nav, split pane tabs, theme, clock, ticker
6. Replace current `index.html` with new template
7. Deploy to Pi — verify all interactions work in browser
8. Test in `--kiosk` mode — confirm bottom nav touch works (different from old 9-button grid issue)

**Session 2 — Live data wiring**

Goal: All 11 instrument cells showing real values. Chart showing AvNav. AI panel connected.

1. `instruments.js` — open WebSocket to `ws://localhost:8099/signalk/v1/stream`
   - Map Signal K paths to each cell (11 paths, see spec Section 22)
   - Apply unit conversions: m/s→knots, radians→degrees, Kelvin→Celsius, Pascals→PSI
   - Evaluate thresholds on each update, apply `.adv` / `.alrt` / `.crit` class
   - Show `---` if path returns null or Signal K disconnects
   - Update ticker with "SIGNAL K OFFLINE — RECONNECTING" on disconnect
2. `nav.js` — replace chart-mock div with AvNav iframe
   - `<iframe src="http://localhost:8080" frameborder="0" style="width:100%;height:100%;">`
3. AI split pane — wire text input to `:3001/ask`
   - On submit: show user bubble, POST to `/ask`, render response as AI bubble with meta line
   - Include vessel context in prompt: speed, depth, course, position, next waypoint
4. Route AI widget — connect to `:3002/route/analyze` SSE stream
   - Show "No active route" state when AvNav has no active leg
   - Show "Analyzing route…" spinner while waiting for AI Bridge response
5. Status bar ticker — add live alert messages for active cell states
6. Port arrival trigger — monitor `:3002/waypoint` distance, fire banner at 2.0nm
7. Position report auto-timer — fire every 2 minutes when Signal K speed > 0.5 knots

**Session 3 — Camera integration + More menu production items**

Goal: Camera tab showing real feeds. More menu cleaned up. Full v0.9.2.2 complete.

1. Camera tab — replace placeholders with live slot system feeds
   - GET `/camera/slots` from :8084, build MJPEG frame URLs from slot assignments
   - Render one `<img>` per active slot with MJPEG polling (forward_watch slot first)
   - Show placeholder frame for unassigned slots
   - Stagger polling: primary 500ms, others 2000ms (match existing camera system)
2. More menu — replace demo buttons with production items:
   - Trip Log (placeholder for now, shows "Coming in v0.9.3")
   - Settings → `/settings` page
   - Exit to Desktop → confirmation dialog → `keyboard-api.py /window/windowed` + `window.close()`
   - Keep 1–2 demo buttons during development, remove at UAT
3. Onboarding wizard — Flask route `/onboard`
   - Form fields: vessel name, home port, hull type, engine config, primary use
   - Writes `config/vessel.env`
   - Redirects to `/` on completion
4. Alert threshold storage — `config/thresholds.json`, loaded at startup, used by instruments.js
5. Remove all dead code: old `panel-toggle.js`, old `connectivity-check.js` dot logic, `chat.html`

### What Gets Retired

| File | Fate |
|---|---|
| `dashboard/templates/index.html` (current 9-button hub) | Replaced entirely |
| `dashboard/static/css/d3kos.css` (Roboto/black theme) | Replaced by v12 CSS |
| `dashboard/static/js/panel-toggle.js` | Retired — row toggle is now in instruments.js |
| `gemini-nav/templates/chat.html` | Orphaned — AI is inline in split pane |
| `docs/d3kos-mockup-v4.html` | Archive — no longer the reference |

### What Stays Unchanged

| Component | Status |
|---|---|
| `app.py` Flask service at :3000 | Minimal changes — add vessel.env, onboarding route |
| `gemini_proxy.py` at :3001 | No changes |
| `ai_bridge.py` at :3002 | No changes |
| `settings.html` | No changes — entry point only changes |
| `offline.html` | No changes |
| All systemd services | No changes |
| Port assignments | No changes |

### Decision Required Before Starting

**One unresolved item requires Don's confirmation before Session 1:**

**Kiosk mode test:** The spec mandates `--kiosk`. Memory documents that `--kiosk` broke touch on the old 9-button grid cards (2026-03-13). The new design has no menu cards in normal page flow — the bottom nav buttons are in a CSS grid with `position:relative`, not `position:fixed`. The previous kiosk touch issue was specific to the old menu card structure.

**Required action:** Before Session 1, Don should open `d3kos-mockup-v12 (2).html` directly on the Pi in kiosk mode:
```
chromium-browser --kiosk file:///home/d3kos/d3kos-mockup-v12.html
```
Then test: can all 6 bottom nav buttons be tapped? Can the More menu open? Can overlays be dismissed? If yes, proceed with `--kiosk`. If touch is broken again, keep `--start-fullscreen` and document the deviation from spec.

---

## 10. SUMMARY TABLE

| Item | Status | Action |
|---|---|---|
| Canonical mockup file | `d3kos-mockup-v12 (2).html` | Copy to repo, rename |
| CSS design system | Production-ready | Extract inline → d3kos.css |
| HTML structure | Production-ready | Convert to Jinja2 template |
| JavaScript | Production-ready with 2 bugs | Fix bugs, split to modules |
| Bug 1: auto-theme override | Present in both v12 files | Fix before deploy |
| Bug 2: nav row flash on load | Present in both v12 files | Fix before deploy |
| Spec accuracy | 1 factual error (AvNav install rule) | Update spec |
| Backend services (Flask, proxy, bridge) | All unchanged | No action |
| Camera integration | 2 placeholders in mockup | Session 3 work |
| Live Signal K data | Static placeholders | Session 2 work |
| Kiosk mode | Unconfirmed | Test on Pi before Session 1 |
| Version designation | v0.9.2.2 | Confirm |

---

*Document version 1.0.0 — 2026-03-13*
*Deploy to: `/home/boatiq/Helm-OS/deployment/d3kOS/docs/D3KOS_V12_FINDINGS.md`*
*Owner: Skipper Don / AtMyBoat.com*
*Reference files: `d3kos-mockup-v12 (2).html` (canonical), `D3KOS_UI_SPEC.md`*
