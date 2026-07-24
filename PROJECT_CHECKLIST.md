# d3kOS & AtMyBoat.com — Master Project Checklist (Active Items)
**Version:** 3.6 | **Last Updated:** 2026-07-11 S97 — BUG-13 logged; speed gauge flicker + long-press UX issue
**Archive:** `PROJECT_CHECKLIST_ARCHIVE.md` — all completed work, decisions, and history preserved

> This file contains OPEN, IN-PROGRESS, and BLOCKED items only.
> For completed work, design decisions, and historical context → `PROJECT_CHECKLIST_ARCHIVE.md`
> PART 17 (Bug Tracker) always stays in this file per standing rule.

---

## LEGEND
- `[ ]` Not started
- `[~]` In progress
- `[!]` Blocked / needs action
- `[–]` Abandoned / superseded

---

## PART 17 — v0.9.9.4 Bug Fixes — STANDING HOLISTIC BUG TRACKER

**Version:** v0.9.9.4
**Standing rule:** ALL bugs on ALL platforms go here first — before any fix is attempted. No fix without a BUG-XX entry. Read this section AND `deployment/docs/V09994_BUG_FIXES.md` at the start of every session before accepting any new work.
**Full investigation doc:** `deployment/docs/V09994_BUG_FIXES.md`
**On-boat analysis plan:** `deployment/docs/V09994_ONBOAT_ANALYSIS_PLAN.md` (S106 — expectations + per-bug investigation steps; fix in lab after on-boat evidence)
**S106 operator corrections (2026-07-24):** E1 — BUG-18 depth source = **Garmin via NMEA 2000** (candidate "no depth sounder present" REMOVED). E2 — BUG-16: gauge tap must show that gauge's live value + normal range from the boat's documentation + advice (identical generic text = broken). Confound: o-charts license EXPIRED → AvNav blank → renew (OB-O05) before judging BUG-19/BUG-20 overlays.

| # | Bug | Status | Detail |
|---|-----|--------|--------|
| BUG-08 | Helm Assistant on-screen keyboard shows then immediately hides; manual keyboard does not type | `[~]` **IN PROGRESS — fix v2.1 insufficient** | `keyboard-fix.js` v2.1 deployed. Root cause: `el.blur()` fires previous tap's `{ once: true }` hideKeyboard listener BEFORE `_recentlyShown` is set. Next step: test whether first tap (no prior listener) works; consider removing `el.blur()` + using `requestAnimationFrame` around `el.focus()`. Full record: `V09994_BUG_FIXES.md` BUG-08. |
| BUG-09 | AvNav chart data corrupts after boat power loss; broader scope: audit all critical services for unclean-shutdown vulnerability and design self-healing | `[ ]` **OPEN — research required** | Root cause: unexpected power loss (boat electrical) causes filesystem/data corruption in AvNav. Two-part scope: (1) research AvNav-specific recovery — detect corruption on boot, auto-repair or restore from known-good state; (2) full audit of all critical services (Signal K, Flask APIs, SQLite DBs, ChromaDB RAG, AvNav) for power-loss vulnerability — design a unified self-healing strategy (integrity check + auto-repair on boot via systemd). Full record: `V09994_BUG_FIXES.md` BUG-09. |
| BUG-11 | No universal method to verify any brand of AIS, GPS, microphone, or speaker is working when connected to d3kOS; solution must be model-agnostic and work for any device worldwide | `[ ]` **OPEN — research required** | Solution cannot be brand-specific. Research must define a generic detection framework: (1) how does d3kOS detect device presence vs. absence for each category, regardless of make/model; (2) how is ongoing health monitored (data flow, silence detection); (3) what is the notification path when a device fails or is missing. Full record: `V09994_BUG_FIXES.md` BUG-11. |
| BUG-12 | AIS not showing in dashboard — Signal K AIS pipedProvider was disabled; rtl_ais was running but SK was not reading from it | `[x]` **FIXED S96 2026-07-11** | Root cause: `ais` pipedProvider set to `enabled: false` in `~/.signalk/settings.json` (unknown when changed). rtl_ais was running correctly on TCP 10110 the whole time. Fix: enabled the provider via Python JSON edit, restarted Signal K. Stale test MMSIs (800000001/800000003) cleared on restart. Full record: `V09994_BUG_FIXES.md` BUG-12. |
| BUG-13 | Boat speed gauge flickers between steady-state value and current value during speed changes; long-press on gauge tile brings up options panel that obscures the speed readout | `[ ]` **OPEN — investigation required** | At steady speed the gauge displays correctly. When speed changes (increase or decrease), the display momentarily shows the new speed, snaps back to the prior steady-state reading, then oscillates between the two values throughout the transition — does not settle cleanly on the current speed. Secondary: long-pressing the gauge tile opens an options menu which, while functional, blocks the ability to read current speed during the interaction. Reported on-boat S97. Full record: `V09994_BUG_FIXES.md` BUG-13. |
| BUG-14 | CX5106 NMEA 2000 engine gateway not transmitting data — device not visible on NMEA 2000 bus | `[~]` **IN PROGRESS — S101 2026-07-20: replacement unit on bus, tach signal connection pending** | S101: New CX5106 unit confirmed on NMEA 2000 bus (src=106, heartbeat PGN 126993 every 60s). Fuel sender (fuel gauge line) connected. ONE fuel packet (PGN 127505, value=0%) received by Signal K when RPM wire briefly connected — data path confirmed working. NOT broadcasting continuously — requires stable tachometer signal. Tach signal wire identified: **blue wire, Pole 3 of RPM gauge** (Monterey non-standard; ABYC gray = Monterey blue). RPM clip not reliably made on boat today. DIP switches on new unit: SW1=ON, SW2=OFF, SW3=ON, SW6=ON. Battery data (PGN 127489) also blocked by same root cause (see BUG-17). Full record: `V09994_BUG_FIXES.md` BUG-14. |
| BUG-15 | Course heading flashes different directions on d3kOS dashboard while boat is stationary (not moving) | `[x]` **FIXED S105 2026-07-23** | Root cause: COG handler updates on every Signal K delta; at SOG≈0, GPS noise causes rapid heading jumps. Fix: gate COG updates below 0.5 kn threshold (matches existing precedent). Edits: (1) state var `_lastSogKts`, (2) SOG handler stores kts, (3) COG guard `if (_lastSogKts !== null && _lastSogKts < 0.5) return;`, (4) test seam `window.SK_HANDLERS = SK_HANDLERS`. TDD logic verified: stationary suppresses updates, moving allows updates. Deployed via AAO atomic spec + Tier-3 build + Tier-1 verify. Operator on-boat check: anchor, no COG flashing. Full record: `V09994_BUG_FIXES.md` BUG-15; spec: `deployment/docs/atomic-specs/BUG-15.md`. |
| BUG-16 | Engine gauge tap dialog shows hardcoded/simulated data instead of reading live Signal K values and comparing against actual tolerances | `[ ]` **OPEN — logged only** | When tapping any engine gauge (oil, coolant, RPM, battery, fuel), a dialog appears but shows simulation/demo data (e.g., hardcoded "oil pressure too low" with fixed PSI) rather than reading the actual live Signal K value and checking if it falls within the normal tolerance range. Expected: tap gauge → read live value → compare to thresholds → advise operator based on actual reading, sourced from boat maintenance manual or AI research. Root cause candidates: (1) `showCrit()` in overlays.js uses hardcoded string; (2) `openDiag()` silent fallback when `_d3kEngData` cache empty; (3) tier gate shows "upgrade" screen to T0/T1 users instead of any live data. **Scope confirmed S101 2026-07-20: ALL engine gauges (fuel, oil, RPM, battery, coolant) show identical generic message — not just one gauge.** Full record: `V09994_BUG_FIXES.md` BUG-16. Reported on-boat S100 2026-07-15. |
| BUG-17 | Battery voltage not displaying on d3kOS dashboard | `[ ]` **OPEN — logged S101 2026-07-20** | Battery voltage tile on d3kOS dashboard shows no data. Signal K has zero electrical/battery data (`/vessels/self/electrical/` returns empty). No battery monitor or alternator voltage source present on NMEA 2000 bus. CX5106 would provide battery/alternator voltage via PGN 127489 once operational — blocked by same root cause as BUG-14 (tachometer signal connection). Separate from BUG-14: even when CX5106 is fully operational, a battery voltage input wire may need to be connected to CX5106. Full record: `V09994_BUG_FIXES.md` BUG-17. |
| BUG-18 | Depth gauge not registering on d3kOS dashboard — expected source is NMEA 2000 network | `[ ]` **OPEN — logged S103 2026-07-20** | Depth gauge on d3kOS dashboard shows no data. Depth data is expected to come from a depth sounder on the NMEA 2000 bus (PGN 128267 — Water Depth), read by Signal K, displayed by d3kOS. Root cause unknown — candidates: (1) no depth sounder present on NMEA 2000 bus; (2) depth sounder present but not broadcasting PGN 128267; (3) Signal K receiving PGN 128267 but d3kOS reading wrong path; (4) d3kOS depth gauge display bug. Investigation required. Full record: `V09994_BUG_FIXES.md` BUG-18. |
| BUG-19 | AIS data confirmed in Signal K but no AIS target symbols displayed on AvNav map | `[ ]` **OPEN — logged S104 2026-07-21** | AIS is confirmed working (rtl_ais running, Signal K AIS provider enabled per BUG-12 fix). When AIS-broadcasting vessels are present, no symbols or targets appear on the AvNav chart display. Root cause unknown — candidates: (1) AvNav not subscribed to Signal K AIS feed; (2) AvNav AIS overlay layer disabled or misconfigured; (3) AIS data present in SK but not forwarded to AvNav via AVNSignalKHandler; (4) no AIS-transmitting vessels were actually within range during testing. Reported on-boat S104 2026-07-21. Full record: `V09994_BUG_FIXES.md` BUG-19. |
| BUG-20 | Camera-detected waterway hazards (kayakers, logs, ducks, geese, swimmers) not appearing on AvNav map | `[ ]` **OPEN — logged S104 2026-07-21** | Cameras functioning and connected. Multiple real-world hazards observed (kayakers, deadhead log, ducks, geese, people swimming) — none appeared as markers or overlays on the AvNav chart. Root cause: integration pipeline from camera object detection → Signal K → AvNav map overlay is likely not implemented. signalk-forward-watch publishes marine detections to Signal K but AvNav overlay of those detections has not been built. G-10 also failed (no fish detection bounding boxes). Investigation required. Reported on-boat S104 2026-07-21. Full record: `V09994_BUG_FIXES.md` BUG-20. |
| BUG-21 | No verbal or visual warning triggered when cameras detect waterway hazards | `[ ]` **OPEN — logged S104 2026-07-21** | Cameras functioning. Kayakers, deadhead log, ducks, geese, and swimmers were observed at close range. No audio warning and no visual alert were generated. Root cause: hazard warning pipeline (camera detection → alert threshold → audio/visual notification) is likely not implemented end-to-end. SafeHelm collision avoidance is design-only (no code). signalk-forward-watch forward-watch alerting to d3kOS notification system may not be wired. Blocking: operator cannot safely use d3kOS as a situational awareness tool without this feature. Reported on-boat S104 2026-07-21. Full record: `V09994_BUG_FIXES.md` BUG-21. |
| BUG-22 | Setup wizard bypassed on fresh load — goes straight to dashboard | `[ ]` **OPEN — logged S104 2026-07-21** | On fresh browser load (or cleared cookies), the system is expected to redirect to the Setup Wizard (Step 1 of 6). Instead it goes directly to the main dashboard. B-01 and B-02 both failed. Root cause candidates: (1) wizard-completed flag set incorrectly or persisted from prior session; (2) redirect logic in dashboard entry point checking wrong condition; (3) cookie/localStorage detection broken after system update. Reported on-boat checklist S104 2026-07-21. Full record: `V09994_BUG_FIXES.md` BUG-22. |
| BUG-23 | Boat Log voice note transcription failing — recorded entry does not appear | `[~]` **DIAGNOSED S105 2026-07-23 — partial** | Tapping voice record, speaking, and tapping stop does not produce a VOICE entry in the Boat Log list. H-03 failed. Root cause candidates: (1) STT (speech-to-text) transcription service not running or not reachable; (2) voice-note POST to `/api/boatlog/voice-note` endpoint failing; (3) entry written to DB but not rendering in log list. Reported on-boat checklist S104 2026-07-21. Full record: `V09994_BUG_FIXES.md` BUG-23. |
| BUG-24 | Boat Log engine auto-capture not working — no ENGINE badge entry after engine running | `[ ]` **OPEN — logged S104 2026-07-21** | After running the engine for 30+ minutes, no ENGINE badge entry appeared automatically in the Boat Log. H-04 failed. Root cause candidates: (1) engine detection logic requires RPM data from CX5106 (blocked by BUG-14); (2) auto-capture service not running; (3) RPM threshold detection broken. May be dependent on BUG-14 — engine auto-capture may require live RPM data to trigger. Reported on-boat checklist S104 2026-07-21. Full record: `V09994_BUG_FIXES.md` BUG-24. |
| BUG-25 | AI Navigation (Gemini) — "could not connect" — entire feature non-functional on boat | `[~]` **DIAGNOSED S105 — likely internet egress, not d3kOS** | AI Navigation page fails to connect on the boat. J-01, J-02, J-03 all failed. Root cause candidates: (1) gemini-proxy service (port 8097) not running; (2) gemini-nav service (port 3001) not running; (3) API key in `api-keys.json` or `gemini.env` invalid or missing; (4) model changed — memory says `gemini-2.5-flash-lite` is the required model on all environments. Two Gemini services on Pi: gemini-proxy port 8097 (reads `api-keys.json`) + gemini-nav port 3001 (reads `gemini.env`) — both must be checked. Reported on-boat checklist S104 2026-07-21. Full record: `V09994_BUG_FIXES.md` BUG-25. |
| BUG-26 | Anchor Watch — Set Anchor failing; no alarm sound when radius exceeded | `[x]` **FIXED S105 2026-07-23** (K-02 fetch routing) | Root cause: anchor-watch.html calls fetch('/anchor/*') → resolves to dashboard :3000 (no routes) → 404. ai-bridge :3002 serves /anchor endpoints (confirmed live). Fix: add const `AI_BRIDGE = 'http://localhost:3002'`, prefix 5 fetches (set/clear/dismiss/advice/state). SSE unchanged (already :3002). TDD source check verified: 5 AI_BRIDGE-prefixed, 0 bare calls. Deployed via AAO atomic spec + Tier-3 build + Tier-1 verify. K-02 (Set Anchor arms) now functional; K-03 (alarm) is downstream of K-02 (retest after K-02 confirmed working on-boat). Full record: `V09994_BUG_FIXES.md` BUG-26; spec: `deployment/docs/atomic-specs/BUG-26.md`. |
| BUG-27 | Status bar (vessel name + clock) text too small to read at 1 metre — AODA violation | `[x]` **COMPLETE 2026-07-23 — deployed + operator-confirmed 1 m legibility** | Root cause CORRECTED: nothing was below 18px — `.sb-vessel` was 18px (AODA floor), `#clk` 22px; 18px floor ≠ helm-legible on 10.1" screen. Fix: raised `.sb-vessel` 18→28px, `#clk` 22→26px in `#sb` (d3kos.css). Deployed to `/opt/d3kos/services/dashboard/static/css/d3kos.css` (backup `.bak.20260723`). Done via AAO §23/§25 atomic spec + Tier-3 (Haiku) build + Tier-1 (Opus) verify. Operator must confirm 1 m legibility on-screen (hardware check). Full record: `V09994_BUG_FIXES.md` BUG-27; spec: `deployment/docs/atomic-specs/BUG-27.md`. |

---

## SAFEHELM — CONCEPT GAUGE (S77–S78 2026-05-11)

**Status:** Concept design complete. Forum article ready. Community interest gauge pending publication.

| # | Item | Status |
|---|------|--------|
| SH-1 | Forum article finalized (Navigation & Charts) — ready for posting | `[~]` Awaiting user post |
| SH-2 | Community feedback on COLREGs compliance gap | `[ ]` Pending article publication |
| SH-3 | Phase 1 (Shadow Mode) design approval — if community interest confirmed | `[ ]` Blocked on SH-2 |

---

## D3K-LITE — INTEREST GAUGE (NEW — 2026-05-11 S78)

**Status:** Feasibility study complete (1,261 lines). Forum article ready. Community interest gauge pending publication.

| # | Item | Status |
|---|------|--------|
| DL-1 | Interest gauge article drafted (Navigation & Charts) — ready for posting | `[~]` Awaiting user post |
| DL-2 | Topic tags prepared (openplotter, d3k-lite, kiosk-dashboard, ai-assistant, fix-my-pi, interest-gauge, feedback-wanted, signal-k) | `[✓]` Done S78 |
| DL-3 | Community feedback on Fix My Pi, dashboard layout, mobile features | `[ ]` Pending article publication |
| DL-4 | Phase 1 build approval — if community interest validates | `[ ]` Blocked on DL-3 |

---

## OPERATOR / ON-BOAT TASKS

**Last updated:** 2026-05-19 S83 (rev 2) — 96-item full checklist. See full printable version: `C:\Users\donmo\Downloads\d3kOS_OnBoat_Validation_Checklist.md`

### INSTALLATION (physical setup — do these first)

| # | Item | Owner | Status |
|---|------|-------|--------|
| OB-I01 | Install RPi + 10.1" screen at helm — confirm power, boot, `d3kos.local:3000` loads | Don | `[ ]` |
| OB-I02 | Confirm boat hotspot network is `10.42.0.x` — DHCP reservations already set 2026-03-23 | Don | `[ ]` |
| OB-I03 | Connect cameras — confirm bow at `10.42.0.100`, stern at `10.42.0.63` via Settings → Camera Setup → Scan | Don | `[ ]` |
| OB-I04 | Connect NMEA2000 backbone to Pi via USB gateway — confirm Signal K sees data | Don | `[ ]` |

### d3kOS CORE — First Boot & System Validation

| # | Item | Owner | Status |
|---|------|-------|--------|
| OB-1 | First-boot password change flow — load `http://d3kos.local:3000`, must redirect to Setup wizard password step | Don | `[ ]` |
| OB-2 | GPS outdoor verification — at dock with clear sky, confirm Signal K `/api/vessels/self/navigation/position` shows non-zero lat/lon | Don | `[!]` Never confirmed with live fix |
| OB-3 | Signal K live data check — confirm SOG, COG, DEPTH, AIS targets all populating in dashboard instrument ribbon | Don | `[!]` Requires NMEA2000 connected |
| OB-4 | Battery voltage — verify Garmin sends PGN 127508: `curl -s 'http://localhost:8099/signalk/v1/api/vessels/self/electrical' \| python3 -m json.tool` | Don | `[!]` |
| OB-5 | BUG-08 touchscreen keyboard test — tap HELM mic field on Pi screen, keyboard must appear and stay visible, typed text must appear in field. Confirms keyboard-fix.js v2.1 result. | Don | `[~]` v2.1 deployed — needs physical touchscreen test |

### CAMERAS — Installation & Validation

| # | Item | Owner | Status |
|---|------|-------|--------|
| OB-C01 | Settings → Camera Setup on Pi touchscreen — create bow/stern slots, assign hardware, confirm thumbnails load | Don | `[ ]` Requires cameras on boat network |
| OB-C02 | Marine Vision page on Pi touchscreen — Focus mode shows bow as primary, stern in filmstrip. Tap filmstrip tile → swaps to primary. | Don | `[ ]` Requires cameras |
| OB-C03 | Fish detection on both cameras independently — stern has `fish_detection=true`, bow does not. Captures in DB must show `slot_id=stern`. | Don | `[ ]` Requires cameras |
| OB-C04 | Marine Vision bounding boxes appear on correct primary tile when fish detected | Don | `[ ]` Requires cameras + fish detection trigger |
| OB-C05 | Camera offline amber state — unplug one camera, Marine Vision must show "Camera offline" amber overlay, not a crash | Don | `[ ]` Requires cameras |
| OB-C06 | 24-hour stability + performance — both cameras running, CPU <35%, memory <970MB, scan completes in <3 sec | Don | `[!]` Never run on boat |
| OB-C07 | Storage check — confirm recordings directory is not filling root partition after 24hr | Don | `[ ]` Part of OB-C06 window |

### HELM DISTANCE — Readability at the Wheel (from cancelled UAT INC-16)

Stand at normal helm position (~1 metre from the 10.1" screen):

| # | Item | Owner | Status |
|---|------|-------|--------|
| OB-H01 | Instrument labels (SOG, DEPTH, COURSE) readable at 1 metre without moving closer | Don | `[ ]` |
| OB-H02 | Instrument values (current SOG and DEPTH numbers) readable at 1 metre | Don | `[ ]` |
| OB-H03 | Bottom nav labels (Dashboard, Weather, Boat Log etc.) readable at 1 metre | Don | `[ ]` |
| OB-H04 | Status bar (vessel name + clock) readable at 1 metre | Don | `[ ]` |
| OB-H05 | Night mode readable in low light (green on black, no washed-out colours) | Don | `[ ]` |
| OB-H06 | Day mode readable in bright daylight — no glare or low-contrast text | Don | `[ ]` |

### BOAT LOG — Requires Engine Running

| # | Item | Owner | Status |
|---|------|-------|--------|
| OB-L01 | Voice record — tap record button, speak, tap stop — new VOICE entry must appear in log list | Don | `[ ]` |
| OB-L02 | Engine auto-capture — start engine, wait 30 min — ENGINE badge entry must appear in Boat Log | Don | `[ ]` Requires engine running |
| OB-L03 | Entry type badges are distinct — VOICE / ENGINE / WEATHER / ALERT show different colours | Don | `[ ]` |

### ENGINE MONITOR — Requires Engine Running

| # | Item | Owner | Status |
|---|------|-------|--------|
| OB-E01 | Engine Monitor page — 6 metric tiles visible (SOG, RPM, oil, coolant, battery, fuel) | Don | `[ ]` |
| OB-E02 | Values update in real time when engine is running — not static `---` | Don | `[ ]` |
| OB-E03 | **v0.9.9.4** — Once CX5106 sender/tach wire IDs are verified on-boat using `deployment/docs/CX5106_WIRE_ID_FIELD_PROCEDURE.md` (results table filled in), **publish that field procedure to d3kOS docs on the Pi**. Gated on on-boat verification. Relates to BUG-14, BUG-17. | Don / Claude | `[ ]` |

### o-CHARTS (Don's task — requires OpenCPN + account)

| # | Item | Owner | Status |
|---|------|-------|--------|
| OB-O01 | OpenCPN launches from Charts button on dashboard | Don | `[ ]` See `deployment/docs/OPENCPN_FLATPAK_OCHARTS.md` |
| OB-O02 | o-charts plugin visible in OpenCPN plugin manager | Don | `[ ]` |
| OB-O03 | Licensed charts visible for your area | Don | `[ ]` |
| OB-O04 | Chart renders — no blank tiles in local area | Don | `[ ]` |

### o-CHARTS LICENSE RENEWAL — AvNav (Don's task — urgent)

| # | Item | Owner | Status |
|---|------|-------|--------|
| OB-O05 | Renew Canada chart subscription at www.o-charts.org — CAac (Atlantic) + CAgl (Great Lakes) both expired **2026-04-01** | Don | `[!]` **BLOCKING — AvNav shows blank** |
| OB-O06 | After renewal: download new chart `.zip` files from o-charts.org → My Devices → Pi fingerprint | Don | `[ ]` Blocked on OB-O05 |
| OB-O07 | Install new charts via AvNav at `http://172.20.10.8:8080` → Charts → Upload | Don | `[ ]` Blocked on OB-O06 |
| OB-O08 | Verify AvNav chart renders for Port Colborne / Lake Erie area | Don | `[ ]` Blocked on OB-O07 |

### FULL UI TOUCHSCREEN WALKTHROUGH (every page on Pi screen)

| # | Item | Owner | Status |
|---|------|-------|--------|
| OB-P01 | Setup wizard — all 6 steps load and progress dots advance | Don | `[ ]` |
| OB-P02 | Dashboard home — instrument ribbon + nav bar functional | Don | `[ ]` |
| OB-P03 | HELM overlay — opens, close button works, mute works | Don | `[ ]` |
| OB-P04 | Weather panel — loads from left, AvNav still visible, data present | Don | `[ ]` |
| OB-P05 | Marine Vision — focus mode, filmstrip swap, grid mode | Don | `[ ]` Requires cameras |
| OB-P06 | Boat Log — voice record full flow: record → stop → entry appears with transcription | Don | `[ ]` |
| OB-P07 | More menu — all 6 items present, icons + labels correct size | Don | `[ ]` |
| OB-P08 | Settings — loads, dropdowns finger-friendly, units change works, Signal K status shows | Don | `[ ]` |
| OB-P09 | AI Navigation — loads, query returns response, Gemini badge visible | Don | `[ ]` |
| OB-P10 | Engine Monitor — 6 tiles visible, values update with engine running | Don | `[ ]` Requires engine |
| OB-P11 | Anchor Watch — GPS position shown, set radius, alarm triggers | Don | `[ ]` Requires GPS fix |
| OB-P12 | Upload Documents — file picker present | Don | `[ ]` |
| OB-P13 | Manage Documents — list or empty state shown | Don | `[ ]` |
| OB-P14 | Data History — page loads, export includes unit metadata | Don | `[ ]` |
| OB-P15 | Charts / AvNav — chart pane visible on dashboard, tiles load for local area | Don | `[ ]` Requires GPS / tiles downloaded |
| OB-P16 | QR Pairing — QR code displays on Pi screen, scannable with phone | Don | `[ ]` |

### SERVICES HEALTH CHECK (SSH to Pi required)

| # | Item | Owner | Status |
|---|------|-------|--------|
| OB-S01 | All services active: dashboard, camera-stream, fish-detector, gemini, gemini-proxy, signalk, avnav | Don | `[ ]` `systemctl is-active <service>` for each |
| OB-S02 | Signal K responding: `curl -s http://localhost:8099/signalk` returns valid JSON | Don | `[ ]` |
| OB-S03 | Root partition health: `df -h /` shows <80% full | Don | `[ ]` |
| OB-S04 | Memory: `free -m` shows >200MB available | Don | `[ ]` |

### KNOWN OPEN ISSUES — Confirm fix status on boat

| # | Item | Owner | Status |
|---|------|-------|--------|
| OB-Q01 | BUG-08 keyboard final result — keyboard stays visible AND typing works on Pi touchscreen | Don | `[~]` v2.1 fix — needs physical confirmation |
| OB-Q02 | DEP17 title bar text — should be white text on Pi Labwc desktop | Don | `[~]` One-line fix available if still black |
| OB-Q03 | i18n gaps — Initial Setup, QR Code, Upload Manual, History pages: change language, note any untranslated strings | Don | `[ ]` |
| OB-Q04 | Remote Access / WebSocket — Settings → Network: WebSocket status shows connected | Don | `[ ]` |
| OB-Q05 | Node-RED: Settings → System Status — should show disabled/inactive, NOT error | Don | `[ ]` |

### UAT — Metric/Imperial (recruit testers after above items pass)

| # | Item | Owner | Status |
|---|------|-------|--------|
| OB-U01 | 5 metric users: SOG in knots/km/h, DEPTH in metres, temp °C, distance in km/nm, export shows metric metadata | Don (recruit) | `[ ]` Ready — S-06 fixes deployed 2026-03-17 |
| OB-U02 | 5 imperial users: SOG in knots, DEPTH in feet, temp °F, distance in nm/miles, export shows imperial metadata | Don (recruit) | `[ ]` |

---

## SIGNAL K UPGRADE (v0.9.2 — pending)

**Status:** SK v2.22.1 on Pi. All d3kOS connections unauthenticated. Upgrade to v2.23.0 when on-boat work window opens.

**Step 1 — Security check on Pi (before anything else)**
- [ ] Read `~/.signalk/settings.json` — look for `"strategy": "./tokensecurity"`
  - If `dummysecurity` or missing: security off → skip Steps 2 & 3
  - If `tokensecurity`: check `allow_readonly` and decide if token work needed

**Step 2 — Token auth in Python + JS (conditional — only if security enabled)**
- [ ] Generate long-lived token: `signalk-generate-token -u <admin> -e 0 -s ~/.signalk/security.json`
- [ ] Store in `/opt/d3kos/config/signalk.env` — never hardcode
- [ ] `signalk_client.py`: add `Authorization: Bearer <token>` header to all REST calls
- [ ] `instruments.js`, `boatlog-engine.js`, `engine-monitor.html`: append `?token=<token>` to WS URL

**Step 3 — Fix `remote_api.py` port bug (do regardless)**
- [ ] Change `SIGNALK_API = 'http://localhost:3000/signalk/v1/api/'` → `http://localhost:8099/signalk/v1/api/`

**Step 4 — Upgrade SK on Pi**
- [ ] `cd ~/.signalk && npm install signalk-server@2.23.0`
- [ ] `sudo systemctl restart signalk`
- [ ] Verify: `curl http://localhost:8099/signalk`

**Step 5 — Verify AvNav patch survives**
- [ ] Confirm `signalkhandler.py` line 1580 still reads `/v2/api/` post-upgrade
- [ ] `curl http://localhost:8080` — confirm AvNav loads and charts render

**Step 6 — Smoke test (Don confirms on Pi screen)**
- [ ] Instruments panel — live SOG, COG, position
- [ ] Engine monitor — live data or graceful "no NMEA2000"
- [ ] Boat log engine capture fires correctly
- [ ] AvNav charts visible
- [ ] Settings §12 Signal K status shows LIVE

---

## v0.9.3 WEBSITE — PHASE 4 PRE-LAUNCH

| # | Item | Status |
|---|------|--------|
| AD | Architecture flow diagram (Part 7A) | `[ ]` |
| PH4-1 | Proper live deploy plan | `[ ]` To be scoped when v0.9.4.1 complete |
| PH4-2 | Post-push smoke test (all pages, AI widget, Stripe Fix My Pi) | `[ ]` |
| PH4-3 | Rotate Gemini API key | `[ ]` |
| PH4-4 | Change FTP password for d3kos@atmyboat.com | `[ ]` |
| PH4-5 | **UPDATE cPanel CRON JOBS (M15-D)** — `offline-check.php` + `fix-my-pi-timeout.php`: change `/staging/wp-content/...` → `/wp-content/...` | `[ ]` |
| SEO | 2E — SEO (Yoast, sitemap, Bing Webmaster) | `[ ]` Deferred to post-launch |
| FOOT | Footer not rendering correctly | `[!]` Root cause unknown — Don said "move on" 2026-03-25. Deferred. |
| FMP | Fix My Pi end-to-end automation | `[ ]` Spec: `ATMYBOAT_BUILD_REFERENCE.md` Part 17.4. Pi watchdog + systemd timer + PHP endpoints + 30-min refund + expectation disclaimer. |
| COMP | `/compatible` — engine checker page | `[!]` Blocked on Don's compatibility data list |
| CA4 | Document credential vault — ~20 fields still `[DON TO PROVIDE]` (cPanel pw, prod DB pw, WP admin, Stripe live keys, email) | `[~]` **IN PROGRESS S27c** |
| OP | Create `mobile/config.php` from template — add DB credentials, Stripe keys, Gemini key, API key | `[ ]` |
| OP | Run `setup/install-pages.php?key=<key>` once → delete | `[ ]` |
| OP | Install MailPoet plugin on staging | `[ ]` |

---

## v0.9.3 WEBSITE — POST-LAUNCH

| # | Item | Status |
|---|------|--------|
| PL-1 | Monitor Gemini API usage (free tier: 20 req/day) | `[ ]` |
| PL-2 | UAT with real boaters (ages 45–70) | `[ ]` |
| PL-3 | Node-RED flow activation — replace placeholder URL, create cloud-credentials.json, enable 3 flows | `[ ]` See Part 8A §8A.2 in archive |
| PL-4 | Re-enable Node-RED community flows when API endpoints are live | `[ ]` Blocked on v0.9.3 live |
| PL-5 | End-to-end test: community sharing ON → community map shows dot | `[ ]` Blocked on v0.9.3 live |
| PL-6 | page-manual.php — Don creates GitHub release with PDF; update PDF URL in page-manual.php | `[ ]` Don action |
| PL-7 | Community map end-to-end: enable map_sharing in usermeta → wait for Pi sync → dot appears | `[ ]` Testable on staging |

---

## Pi — OPEN ITEMS

| # | Item | Status | Detail |
|---|------|--------|--------|
| DEP13 | Pi AODA compliance pass | `[~]` **Awaiting Don go-ahead** | Track A (contrast ~50 selectors), Track B (skip links/h2/aria-labels on 13 templates), Track C (font floor). S51 plan ready. Static pages done S8. Flask templates not done. |
| DEP17 | Pi title bar text color — text still black | `[~]` **OPEN** | Fix: `window.active.label.text.color: #ffffff` in `/home/d3kos/.config/labwc/themerc-override`. One-line change. |
| DEP20 | Dual dashboard source-of-truth audit | `[!]` **OPEN S52** | `deployment/d3kOS/dashboard/` and `deployment/v0.9.4/pi_source/` still diverge. Partial sync done S52. Full audit needed — any new page must be added to BOTH dirs. |
| PM4 | Predictive maintenance ML models (5 targets) | `[ ]` Deferred — needs on-water training data |
| PM7 | Predictive maintenance advanced automation | `[ ]` Deferred — T3/Phase 5 |
| RAG | RAG re-ingest after each Pi deployment | `[ ]` Recurring — `cd /home/boatiq/rag-stack && .venv/bin/python3 helm_os_ingest.py --collection source` |
| SK-FW | signalk-forward-watch: add download-on-first-run | `[ ]` |
| SK-FW | signalk-forward-watch: test on OpenPlotter | `[ ]` |
| SK-FW | signalk-forward-watch: fix README (Step 2 model download now unnecessary) | `[ ]` |

---

## INTEGRATION TESTS (v0.9.4.1 — require live site)

| # | Test | Expected result | Status |
|---|------|-----------------|--------|
| T1 | Pi sync → website: POST to data-ingress.php with real API key | 200 OK, engine snapshot in DB, last_sync updated | `[ ]` |
| T2 | Command round-trip: app queues `restart_service` → Pi executes → result returned | App shows "completed" within 35 min | `[ ]` |
| T3 | Community data flow: enable boat_map in Settings → position appears on /community map | Dot appears within 30 min | `[ ]` |
| T4 | Alert trigger: simulate anchor drag → immediate export → alert in DB | Alert in `amboat_alerts` within 2 min | `[ ]` |
| T5 | Find My Boat: Pi syncs position → Chart Room shows correct marker | Position on map within 35 min | `[ ]` |
| A1 | App writes command to `command-queue.php` | Depends on PWA build | `[ ]` |
| A2 | Pi command pickup loop executes and returns result | Depends on P3 | `[ ]` |
| A3 | App polls `command-queue.php` for command result | Depends on PWA build | `[ ]` |
| M8 | T1: Pi → website sync (post-launch) | Same as T1 — post-launch | `[ ]` |
| M9 | T2: Command round-trip (post-launch) | Same as T2 — post-launch | `[ ]` |
| M10 | T3: Community data flow (post-launch) | Same as T3 — post-launch | `[ ]` |
| M11 | T4: Anchor drag alert (post-launch) | Same as T4 — post-launch | `[ ]` |
| M12 | T5: Find My Boat (post-launch) | Same as T5 — post-launch | `[ ]` |

---

## FLEET MANAGEMENT — v0.9.6 Phase 4 (remaining)

| # | Item | Status | Detail |
|---|------|--------|--------|
| FM2 | Fleet map PWA screen | `[~]` Backend done, PWA Leaflet screen not built | |
| FM6 | T3 activation gate — two-device hardware test | `[~]` Backend + admin CRM done. Hardware test still pending. | |

---

## SECURITY AUDIT — v0.9.9 (gate before v1.0 full launch)

| # | Item | Status | Detail |
|---|------|--------|--------|
| SA4 | External penetration test | `[ ]` **Don to hire firm** — network attacks, privilege escalation, API fuzzing, rate limiting |
| SA5 | Fix all critical/high vulnerabilities from pen test | `[ ]` Blocked on SA4 |
| SA7 | Penetration test certificate | `[ ]` Blocked on SA4 |

---

## v1.1 MULTI-LANGUAGE (deferred)

| Layer | Item | Status |
|-------|------|--------|
| Layer 0 | Noto fonts for Arabic/CJK/Greek/Cyrillic, Arabic RTL, professional translation review | `[ ]` |
| Layer 1 | Whisper-small STT (99 languages) | `[ ]` Not started |
| Layer 2 | Per-language Piper TTS models | `[ ]` Not started |
| Layer 3 | AI response language injection | `[x]` Done |
| Layer 4 | Per-language virtual keyboards, Arabic RTL | `[ ]` Not started — fix BUG-08 first |
| Layer 5 | Boat log in user's language | `[ ]` Not started — auto after Layers 1+4 |

---

## RESEARCH PAPER & AAO DATA

| # | Item | Owner | Status |
|---|------|-------|--------|
| PAPER-4 | Verify ai_model_version column in session_sqs_dataset_v2.csv (all 36 rows show placeholder "claude-sonnet-4") | Don | `[ ]` |
| PAPER-5 | Document remaining 10 excluded sessions in session_exclusion_log.csv | Don/Claude | `[ ]` |
| PAPER-6 | Phase 1 research data collection — record tasks_planned/completed/governing_doc_version at every session close | Claude | `[ ]` **Active — starts now** |
| PAPER-7 | Submit Governing_the_AI_Productivity_Promise_v3.3 to Research Policy | Don | `[ ]` SSRN first, then journal |

---

## AAO DATA COLLECTION SYSTEM — Phase 1 (awaiting Don go-ahead)

**Architecture:** `aao-methodology-repo/data-collection/ARCHITECTURE.md` v1.1
**Deploy target:** `atmyboat.com/research/`

| # | Task | Owner | Status |
|---|------|-------|--------|
| DC-02 | UpdraftPlus backup before DB changes | Don | `[ ]` **Prerequisite** |
| DC-03 | Confirm `admin@atmyboat.com` deliverability on HostPapa | Don | `[ ]` |
| DC-04 | MySQL tables: `aao_contributors` + `aao_sessions` | Claude | `[ ]` |
| DC-05 | `aao-collector.py` — Python stdlib, reads `aao_api_key:` from CLAUDE.md | Claude | `[ ]` |
| DC-06 | `aao-register.php` + registration form | Claude | `[ ]` |
| DC-07 | `aao-submit.php` — validation, dedup, IP hash, storage | Claude | `[ ]` |
| DC-08 | `aao-data.php` — public aggregate JSON API | Claude | `[ ]` |
| DC-09 | `atmyboat.com/research/index.html` — landing page + download link | Claude | `[ ]` |
| DC-10 | `atmyboat.com/research/privacy/` — privacy policy page | Claude | `[ ]` |
| DC-11 | CLAUDE.md template update in `aao-methodology-repo` | Claude | `[✓]` Done S81 — 3-tier Classification Gate, Atomic Spec, Watchdog, provider-agnostic |
| DC-12 | `commands/session-close.md` — collector reminder line | Claude | `[ ]` |

---

## MISC OPEN

| # | Item | Status |
|---|------|--------|
| AAO-6 | Initialize LLM-Wiki for Helm-OS | `[ ]` Awaiting Don instruction — say "initialize the wiki" to activate |
| AAO-7 | Update `aao-methodology-repo/SPECIFICATION.md` to formally add Section 23 — Three-Tier Agentic Model / Adaptive Governance Specification Principle | Claude | `[✓]` Done S81 — 10 subsections, commit 728a166, pushed to GitHub. |
| BUG-06 | PWA tier still shows T1 | `[!]` Operator action: (1) Ctrl+Shift+R hard refresh, (2) log out → log in as admin@atmyboat.com (T3), (3) check localStorage `amboat_tier`. Cannot diagnose further without operator confirmation. |
| SQS | SQS calculation block in CLAUDE.md session-close | `[ ]` Already running correctly — confirm and close |
| v0.9.4.1 | Blocked on Phase 4 live push for public availability. Code complete on staging. | `[ ]` |
| v0.9.9 | Security audit gates v1.0 full launch — see SA4-SA7 above | `[ ]` |
| v1.1 | CJK keyboard, self-hosted STUN coordination server | `[ ]` Future |

---

---

## PART 18 — SafeHelm Collision Avoidance Module (S76 2026-05-11)

**Design document:** `deployment/docs/SAFEHELM_DESIGN.md`
**Target:** `github.com/SkipperDon/d3kOS/services/safehelm/`
**Status:** Design complete. Build not started.

| # | Task | Status | Notes |
|---|------|--------|-------|
| SH-01 | Resolve camera range estimation | `[~]` PARTIAL | S79: WiBoat WiFi CSI solves range for non-AIS targets in integrated system (range + bearing from CSI). Camera-only mode remains bearing-only. Integrated SafeHelm+WiBoat resolves L1 limitation — camera targets fuse with WiBoat contacts when within ±15° bearing + ±50m range. No longer blocks Phase 1 start. |
| SH-02 | Add Rule 12 (sailing vessels) to COLREGs classifier | `[ ]` | Port/starboard tack, windward/leeward. Requires wind angle input from NMEA. |
| SH-03 | Add Rule 19 (restricted visibility) mode | `[ ]` | Fog/night detection, speed reduction advisory, fog signal output, suspend Rules 12–18. |
| SH-04 | Night / low-light camera fallback | `[ ]` | Auto-switch to AIS_ONLY when camera confidence → 0 after sunset or in fog. |
| SH-05 | Add Rule 18 vessel type hierarchy | `[ ]` | Use AIS vessel type field. Power→Sailing→Fishing→RAM→NUC pecking order. |
| SH-06 | Spec AIS-camera fusion algorithm | `[ ]` | Association threshold, bearing/position proximity matching, duplicate suppression. |
| SH-07 | Virtual MMSI expiry logic | `[ ]` | Remove ghost vessels from Signal K when camera loses track. TTL-based cleanup. |
| SH-08 | Startup health check | `[ ]` | Verify Signal K reachable, GPS fix, AIS receiving before operating. Alert captain if not. |
| SH-09 | Connect depth sounder to Safety Envelope | `[ ]` | Pipeline from SK depth path into `shallow_water_depth_m` check. |
| SH-10 | Incident logging spec | `[ ]` | File, format, fields, review UI. Required for post-incident verification. |
| SH-11 | Phase 1 Shadow Mode build | `[ ]` | Log-only — no alarms, no autopilot. CPA/TCPA + COLREGs classifier working. |
| SH-12 | Phase 2 Advisory Mode build | `[ ]` | Voice alerts via ai_bridge + AvNav widget. Sea trial validation. |
| SH-13 | Phase 3 Conflict Solver build | `[ ]` | Multi-vessel graph, non-compliant vessel detection, defensive mode. |
| SH-14 | Phase 4 pypilot integration | `[ ]` | Only after Phase 2 sea trial confirms advisory accuracy. High risk — do not rush. |
| SH-15 | AIS isolation audit — explicit transmitPGNs whitelist in Signal K canboat-js provider | `[ ]` | **Phase 1 hard gate.** Current state is implicit (nothing configured wrong) but not verified. Must be explicit whitelist before any synthetic AIS injection ships. S85: 4-layer isolation spec written in `wiki/concepts/ais-isolation.md`. |

---

## PART 19 — WiBoat + SafeHelm Integrated System (S79 2026-05-12)

**Architecture document:** `deployment/docs/wiboat/WIBOAT_SAFEHELM_INTEGRATED_ARCHITECTURE.md` (moved from Downloads S82)
**FRD:** `deployment/docs/wiboat/WIBOAT_SAFEHELM_FRD_v1.1.md` (v1.1 S82 — dual-network, 4-antenna Phase 1)
**BOM:** `deployment/docs/wiboat/WiBoat_BOM_v2.md` (v2.0 S82 — 4-antenna + SP4T switch, $565–$868 CAD)
**Status:** Architecture + FRD + BOM complete. Phase 1 build not started.
**Relationship to PART 18:** WiBoat is the sensor layer that integrates with SafeHelm. Architecture supersedes SAFEHELM_SYSTEM_SPEC.md for ports, MMSIs, and API formats.

| # | Task | Status | Notes |
|---|------|--------|-------|
| WB-01 | Assign static IP `10.42.0.2` to WiBoat RPi 4B on boat router; confirm RPi 5 on-boat IP | `[!]` OPERATOR ACTION | IP confirmed S82: `10.42.0.2` on-boat. Must assign on boat router. Also confirm RPi 5 on-boat IP (`10.42.0.1` is placeholder in FRD). Must happen before Phase 1 code. |
| WB-02 | Procure WiBoat Phase 1 hardware | `[ ]` | BOM v2.0 ready: RPi 4B 4GB, 2× ALFA AWUS036NH, 4× 12dBi omni antennas, 1× SP4T RF switch, LMR-400, Heltec V3. Est. $565–$868 CAD. See `deployment/docs/wiboat/WiBoat_BOM_v2.md`. |
| WB-03 | Flash RPi 4B with Bullseye 32-bit, lock kernel 5.10 | `[ ]` | Do NOT run apt upgrade after flash. Kernel must stay 5.10 for nexmon_csi compatibility. |
| WB-04 | Install nexmon_csi via picsi, confirm CSI packets on UDP :5500 | `[ ]` | Phase 1 gate G1.1 depends on this. |
| WB-05 | Implement wiboat-processor.py (range only) + WebSocket :8766 | `[ ]` | Phase 1 WiBoat deliverable. IFFT ToF range, Kalman tracker, contact JSON schema. |
| WB-06 | Connect WiBoat to SafeHelm via LAN — confirm contact feed received | `[ ]` | Phase 1 integration gate G1.3. |
| WB-07 | Flash Heltec V3, confirm Meshtastic LoRa operation | `[ ]` | Phase 1 gate G1.4. |
| WB-08 | Phase 1 acceptance gates (all 5) | `[ ]` | G1.1–G1.5 per architecture doc §10. Must all pass before Phase 2. |
| WB-09 | Phase 2: 4-antenna bearing (MUSIC AoA via SP4T switch), marine environment test | `[ ]` | Updated S82: hardware Phase 1, software Phase 2. Gate: ±15° at 100m (4-antenna UCA, no port/starboard ambiguity). |
| WB-10 | Phase 2: SafeHelm advisory mode + WiBoat CPA integration | `[ ]` | Voice alerts, AvNav widget, WiBoat contacts as 998xxxxxx AIS targets. |
| WB-11 | Phase 2 sea trial (4-hour advisory-only passage) | `[ ]` | HARD GATE: zero false CRITICAL alarms, captain endorsement required. |
| WB-12 | Phase 3: 360° bearing validation, batman-adv cooperative mesh | `[ ]` | Updated S82: 4-antenna hardware is Phase 1 (no longer a Phase 3 upgrade). Phase 3 = full-quadrant validation testing + batman-adv mesh only. |
| WB-13 | Migration Gate 3: bench single-box validation on RPi 5 | `[ ]` | Non-16k kernel + all d3kOS services + WiBoat simultaneously. Must pass before Phase 4. |
| WB-14 | G3.5 calendar gate: one full sailing season in Phase 2 advisory mode | `[ ]` | HARD GATE — cannot be bypassed. Phase 4 autopilot blocked until complete. |
| WB-15 | Phase 4: single-box consolidation (ALFA adapters to RPi 5) | `[ ]` | Migration Gate 4. 4-hour shadow run at anchor before sea use. |
| WB-16 | Phase 4: SafeHelm autopilot (pypilot integration, sea trial) | `[ ]` | Only after WB-14 + WB-15. High risk — see architecture doc §13. |

---

---

## PART 20 — v0.9.9.5 Research & Discussion Backlog

**Full document:** `deployment/docs/V09995_DISCUSSION_PLAN.md`
**Created:** 2026-06-23 S92
**Purpose:** Tracks ideas, research topics, and architectural discussions that have been explored but are not yet approved for build. When an item is approved, it gets a task breakdown here in the checklist.

| # | Topic | Status | Summary |
|---|-------|--------|---------|
| D01 | WiBoat — WiFi CSI Marine Radar | `DESIGN COMPLETE` | FRD v1.2 + BOM v2.0 done. Blocked on hardware procurement (WB-02) and IP confirmation (WB-01). |
| D02 | SafeHelm — Collision Avoidance | `DESIGN COMPLETE` | 7-layer architecture + COLREGs framework done. Blocked on community validation (forum article not yet posted — SH-1). |
| D03 | Sail-O-Vision Collaboration | `RESEARCH` | nmea_client.py assessed as reusable in SafeHelm. Dragon's Lair simulator concept filed. Awaiting Don decision on outreach. |
| D04 | D3K-Lite — OpenPlotter Addon | `AWAITING COMMUNITY` | Feasibility (1,261 lines) + forum article done. Blocked on community validation (article not yet posted — DL-1). |
| D05 | signalk-forward-watch v0.2.4 | `PARTIAL DESIGN` | 3 small improvements discussed: download-on-first-run, OpenPlotter test, README fix. |
| D06 | AAO Data Collection System | `AWAITING OPERATOR` | Architecture v1.1 done. Blocked on DC-02 (UpdraftPlus backup) and DC-03 (email confirm) — Don's actions. |
| D07 | Mobile App PWA — Remaining | `PARTIAL DESIGN` | Strategy decided. Fix My Pi, Find My Boat, OTA, fleet map not yet built. Blocked on on-boat validation first. |
| D08 | pypilot Integration | `DEFERRED` | SafeHelm Phase 4 only. Hard gate: one full sailing season in advisory mode (WB-14) must pass first. |
| D09 | Research Paper Submission | `AWAITING OPERATOR` | Paper v3.3 complete. Don to verify ai_model_version (PAPER-4), document excluded sessions (PAPER-5), then submit (PAPER-7). |
| D10 | AAO Methodology Evolution | `RESEARCH` | Section 24 not yet exercised. Threshold of 3 questions may need tuning after first real build. |
| D11 | 360° Marine Vision: NCS2 + Satellite + Cellular | `PARTIAL DESIGN` | 4× Reolink cameras + Intel NCS2 + YOLOv8n via OpenVINO. Sub-stream RTSP + frame skip + MQTT → d3kOS. Satellite base layer (NASA GIBS / Copernicus) + eSIM/4G. Standalone module. Open questions: NCS2 vs Hailo/Coral hardware, marine class model source, AvNav vs MapLibre chart engine. |
| D12 | On-Boat Validation (prerequisite) | `AWAITING OPERATOR` | GPS fix, BUG-08 keyboard, NMEA2000 backbone, Signal K live data. Prerequisite for all above. |
| D13 | VHF Communication Suite — Audio Replay + STT + Translation + Signal K Alerts | `PARTIAL DESIGN` | 4 phases: (1) audio replay via USB tap + sox/ffmpeg denoise, (2) keyword alerts → Signal K (MAYDAY/PAN-PAN/SECURITE/vessel name), (3) Faster-Whisper STT transcription on Pi CPU, (4) Argos Translate offline MT. Base project: github.com/hwater/vhf-clear-audio-replay (MIT). Port 8088. ~$10-15 CAD USB audio adapter. BLOCKING: VHF radio audio tap accessibility unconfirmed. |

---

*Completed work archived in: `PROJECT_CHECKLIST_ARCHIVE.md`*
*Do not delete entries — update status or move to archive only.*
