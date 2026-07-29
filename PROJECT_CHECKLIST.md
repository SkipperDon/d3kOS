# d3kOS & AtMyBoat.com — Master Project Checklist (Active Items)
**Version:** 3.18 | **Last Updated:** 2026-07-29 S110 — **BUG-32 FIXED (lab); BUG-40 FIXED + DEPLOYED**. Prior: **BUG-13 FIXED (lab)** — SOG 250ms debounce + ctx menu live value; on-boat validation required for Issue 1. Prior: **BUG-41 + BUG-34 FIXED + DEPLOYED to lab Pi**; atomic specs + tests committed. Prior: 2026-07-28 S109 — BUG-12 REOPENED; 7 deployed-bug rows corrected. Prior: 2026-07-27 S108-cont — BUG-29/30/35/36/37/38/39 DEPLOYED to lab Pi.
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
**⚠ S107 ON-BOAT PHASE A (2026-07-27) — READ BEFORE ACCEPTING ANY BUG STATUS BELOW.** Live SSH on the boat Pi (`172.20.10.8`), engine running, Garmin connected. Full evidence: `deployment/docs/V09994_BUG_FIXES.md` BUG-28…BUG-34.
- **The boat Pi runs d3kOS v0.9.2.2 (build 2026-03-23).** The S96 and S105 fixes are NOT on it (no `.bak.20260723` backups; `.sb-vessel` still 18px; `_lastSogKts` and `AI_BRIDGE` both absent; `settings.json` mtime 2026-03-12). **BUG-15, BUG-26, BUG-27 are NOT fixed on the boat** — those deploys reached the lab Pi (`192.168.1.237`) only. Cause: `deployment/v0.9.4/pi_source/` froze 2026-04-08 while `deployment/d3kOS/dashboard/` advanced to 2026-07-23 — the two-source-sync rule is violated. → **BUG-28**
- **Root causes found (present in the LATEST source, so re-copying the release will NOT fix them):** dashboard subscribes `propulsion.0.*` but Signal K publishes `propulsion.port.*` (→ **BUG-29**, cascades into BUG-16 and BUG-24); depth gauge reads `belowKeel` but Signal K publishes `belowTransducer` (→ **BUG-30**, replaces the BUG-18 root cause).
- **E1 CONFIRMED:** Garmin depth IS live in Signal K (`belowTransducer` = 0.99 m, `$source: can0.0`, PGN 128267). The candidate "no depth sounder present" is definitively wrong.
- **BUG-25 and BUG-22 are NOT bugs** — Gemini answered a live on-boat query (`tokens:290`, `online:true`, egress OK); the wizard gate behaves as designed (`vessel.env` exists).
- **Open operator actions:** physically identify the src 64 device (**BUG-31**); confirm actual fuel tank capacity (src 64 reports 1.16 m³ ≈ 306 US gal and 0% on a confirmed-full tank); **confirm the version on the lab Pi when back in the lab** (lab Pi unreachable from the boat hotspot).
- **Memory correction:** the wizard gate file is `/opt/d3kos/services/dashboard/config/vessel.env` (relative to `app.py`), NOT `/opt/d3kos/config/vessel.env`. Two separate config directories exist.

**✅ S108-cont STATUS (2026-07-27):** **BUG-29, 30, 35, 36, 37, 38 and 39 are all FIXED IN REPO and independently verified — none is deployed.** The lab Pi still runs the pre-fix code; the boat is untouched. Verifier scripts per bug at `deployment/v0.9.9.4/tools/verify-bug*.sh`. **Next gate = an operator-authorised deploy to the lab Pi, with `MANIFEST.md5` regenerated as part of it.** ⚠ **`check-drift.sh` blind spot:** it compares the **Pi** against the manifest, not the **repo** against the manifest. The repo is now **8 files ahead of both**, yet it reports "NO DRIFT" — do not read that as "the Pi is current". ⚠ **BUG-16 and BUG-24 are NOT closed** by these fixes; both need on-boat confirmation with live N2K data. ⚠ **Open scaling question:** `pgns/127489.js` returns `oilPressure` unconverted from a variable named `kpa` while the dashboard converts Pa→PSI — if SK emits kPa the gauge reads **1000× low**. Unresolvable off-boat; **post-deploy, compare displayed oil PSI against the analogue gauge.** **Operator action:** measure transducer-to-keel and set it as a **negative** offset on the Garmin — that is the real BUG-30 fix.

**S106-cont (2026-07-24) — BUG-16 prerequisite P1 RESOLVED:** boat + engine docs now converted to AI-friendly, RAG-ready form: `deployment/docs/MONTEREY_246_265_286_OM_AI.md` + `deployment/docs/MERCRUISER_454_MAG_MPI_SM_AI.md` (commit 9dcdb4a). Engine gauge tolerances for BUG-16/17 now SOURCED — oil ≥30 psi@2000/≥4 psi idle, thermostat 160°F, idle 600/WOT 4200–4600 rpm, alternator 13.9–14.7V. BUG-14: MerCruiser BIA colors + sender resistance tables captured (but EFI harness is non-standard → meter-ID per S102 remains authority). Operator to ingest into d3kOS RAG.

| # | Bug | Status | Detail |
|---|-----|--------|--------|
| BUG-08 | Helm Assistant on-screen keyboard shows then immediately hides; manual keyboard does not type | `[~]` **IN PROGRESS — fix v2.1 insufficient** | `keyboard-fix.js` v2.1 deployed. Root cause: `el.blur()` fires previous tap's `{ once: true }` hideKeyboard listener BEFORE `_recentlyShown` is set. Next step: test whether first tap (no prior listener) works; consider removing `el.blur()` + using `requestAnimationFrame` around `el.focus()`. Full record: `V09994_BUG_FIXES.md` BUG-08. |
| BUG-09 | AvNav chart data corrupts after boat power loss; broader scope: audit all critical services for unclean-shutdown vulnerability and design self-healing | `[ ]` **OPEN — research required** | Root cause: unexpected power loss (boat electrical) causes filesystem/data corruption in AvNav. Two-part scope: (1) research AvNav-specific recovery — detect corruption on boot, auto-repair or restore from known-good state; (2) full audit of all critical services (Signal K, Flask APIs, SQLite DBs, ChromaDB RAG, AvNav) for power-loss vulnerability — design a unified self-healing strategy (integrity check + auto-repair on boot via systemd). Full record: `V09994_BUG_FIXES.md` BUG-09. |
| BUG-11 | No universal method to verify any brand of AIS, GPS, microphone, or speaker is working when connected to d3kOS; solution must be model-agnostic and work for any device worldwide | `[ ]` **OPEN — research required** | Solution cannot be brand-specific. Research must define a generic detection framework: (1) how does d3kOS detect device presence vs. absence for each category, regardless of make/model; (2) how is ongoing health monitored (data flow, silence detection); (3) what is the notification path when a device fails or is missing. Full record: `V09994_BUG_FIXES.md` BUG-11. |
| BUG-12 | AIS not showing in dashboard — Signal K AIS pipedProvider was disabled; rtl_ais was running but SK was not reading from it | `[ ]` **REOPENED S109 2026-07-28 — the `[x] FIXED` claim was FALSE; SUPERSEDED BY BUG-32** | **CORRECTION S109 2026-07-28:** this fix is on NO Pi in service — the boat's `settings.json` mtime is 2026-03-12 (S107) and the lab Pi master was read live as `enabled: false` (2026-07-28) — AND the approach is invalid: Signal K itself holds TCP 10110 as its NMEA0183 **output**, so enabling the `ais` **client** provider on that port loops SK's own GPS back instead of carrying AIS. Do NOT re-apply. Real fix is BUG-32 (unbuilt). Original S96 record follows. Root cause: `ais` pipedProvider set to `enabled: false` in `~/.signalk/settings.json` (unknown when changed). rtl_ais was running correctly on TCP 10110 the whole time. Fix: enabled the provider via Python JSON edit, restarted Signal K. Stale test MMSIs (800000001/800000003) cleared on restart. Full record: `V09994_BUG_FIXES.md` BUG-12. |
| BUG-13 | Boat speed gauge flickers between steady-state value and current value during speed changes; long-press on gauge tile brings up options panel that obscures the speed readout | `[~]` **FIXED (lab) — on-boat validation required (Issue 1)** | S110 2026-07-29: Issue 1 (flicker) — 250 ms display coalesce timer added to SOG handler; multi-source SK interleave identified as root cause. Issue 2 (ctx menu) — live cell value now shown in menu title. File: `instruments.js`. Tests: `tests/bug13-speed-gauge.test.cjs` (5 pass). Spec: `atomic-specs/BUG-13.md`. Issue 1 validation requires on-boat throttle change to confirm debounce resolves flicker. |
| BUG-14 | CX5106 NMEA 2000 engine gateway not transmitting data — device not visible on NMEA 2000 bus | `[~]` **IN PROGRESS — S101 2026-07-20: replacement unit on bus, tach signal connection pending** | S101: New CX5106 unit confirmed on NMEA 2000 bus (src=106, heartbeat PGN 126993 every 60s). Fuel sender (fuel gauge line) connected. ONE fuel packet (PGN 127505, value=0%) received by Signal K when RPM wire briefly connected — data path confirmed working. NOT broadcasting continuously — requires stable tachometer signal. Tach signal wire identified: **blue wire, Pole 3 of RPM gauge** (Monterey non-standard; ABYC gray = Monterey blue). RPM clip not reliably made on boat today. DIP switches on new unit: SW1=ON, SW2=OFF, SW3=ON, SW6=ON. Battery data (PGN 127489) also blocked by same root cause (see BUG-17). Full record: `V09994_BUG_FIXES.md` BUG-14. |
| BUG-15 | Course heading flashes different directions on d3kOS dashboard while boat is stationary (not moving) | `[~]` **FIXED IN LAB ONLY — S107: NOT on the boat Pi** (`_lastSogKts` 0 occurrences; `instruments.js` dated Apr 8). Will still reproduce on-boat. See BUG-28. | Root cause: COG handler updates on every Signal K delta; at SOG≈0, GPS noise causes rapid heading jumps. Fix: gate COG updates below 0.5 kn threshold (matches existing precedent). Edits: (1) state var `_lastSogKts`, (2) SOG handler stores kts, (3) COG guard `if (_lastSogKts !== null && _lastSogKts < 0.5) return;`, (4) test seam `window.SK_HANDLERS = SK_HANDLERS`. TDD logic verified: stationary suppresses updates, moving allows updates. Deployed via AAO atomic spec + Tier-3 build + Tier-1 verify. Operator on-boat check: anchor, no COG flashing. Full record: `V09994_BUG_FIXES.md` BUG-15; spec: `deployment/docs/atomic-specs/BUG-15.md`. |
| BUG-16 | Engine gauge tap dialog shows hardcoded/simulated data instead of reading live Signal K values and comparing against actual tolerances | `[ ]` **OPEN — logged only** | When tapping any engine gauge (oil, coolant, RPM, battery, fuel), a dialog appears but shows simulation/demo data (e.g., hardcoded "oil pressure too low" with fixed PSI) rather than reading the actual live Signal K value and checking if it falls within the normal tolerance range. Expected: tap gauge → read live value → compare to thresholds → advise operator based on actual reading, sourced from boat maintenance manual or AI research. Root cause candidates: (1) `showCrit()` in overlays.js uses hardcoded string; (2) `openDiag()` silent fallback when `_d3kEngData` cache empty; (3) tier gate shows "upgrade" screen to T0/T1 users instead of any live data. **Scope confirmed S101 2026-07-20: ALL engine gauges (fuel, oil, RPM, battery, coolant) show identical generic message — not just one gauge.** Full record: `V09994_BUG_FIXES.md` BUG-16. Reported on-boat S100 2026-07-15. |
| BUG-17 | Battery voltage not displaying on d3kOS dashboard | `[ ]` **OPEN — logged S101 2026-07-20** | Battery voltage tile on d3kOS dashboard shows no data. Signal K has zero electrical/battery data (`/vessels/self/electrical/` returns empty). No battery monitor or alternator voltage source present on NMEA 2000 bus. CX5106 would provide battery/alternator voltage via PGN 127489 once operational — blocked by same root cause as BUG-14 (tachometer signal connection). Separate from BUG-14: even when CX5106 is fully operational, a battery voltage input wire may need to be connected to CX5106. Full record: `V09994_BUG_FIXES.md` BUG-17. |
| BUG-18 | Depth gauge not registering on d3kOS dashboard — expected source is NMEA 2000 network | `[~]` **ROOT CAUSE FOUND S107 → see BUG-30** (path mismatch `belowKeel` vs `belowTransducer`; E1 confirmed, Garmin depth live at 0.99 m) | Depth gauge on d3kOS dashboard shows no data. Depth data is expected to come from a depth sounder on the NMEA 2000 bus (PGN 128267 — Water Depth), read by Signal K, displayed by d3kOS. Root cause unknown — candidates: (1) no depth sounder present on NMEA 2000 bus; (2) depth sounder present but not broadcasting PGN 128267; (3) Signal K receiving PGN 128267 but d3kOS reading wrong path; (4) d3kOS depth gauge display bug. Investigation required. Full record: `V09994_BUG_FIXES.md` BUG-18. |
| BUG-19 | AIS data confirmed in Signal K but no AIS target symbols displayed on AvNav map | `[ ]` **OPEN — logged S104 2026-07-21** | AIS is confirmed working (rtl_ais running, Signal K AIS provider enabled per BUG-12 fix). When AIS-broadcasting vessels are present, no symbols or targets appear on the AvNav chart display. Root cause unknown — candidates: (1) AvNav not subscribed to Signal K AIS feed; (2) AvNav AIS overlay layer disabled or misconfigured; (3) AIS data present in SK but not forwarded to AvNav via AVNSignalKHandler; (4) no AIS-transmitting vessels were actually within range during testing. Reported on-boat S104 2026-07-21. Full record: `V09994_BUG_FIXES.md` BUG-19. |
| BUG-20 | Camera-detected waterway hazards (kayakers, logs, ducks, geese, swimmers) not appearing on AvNav map | `[ ]` **OPEN — logged S104 2026-07-21** | Cameras functioning and connected. Multiple real-world hazards observed (kayakers, deadhead log, ducks, geese, people swimming) — none appeared as markers or overlays on the AvNav chart. Root cause: integration pipeline from camera object detection → Signal K → AvNav map overlay is likely not implemented. signalk-forward-watch publishes marine detections to Signal K but AvNav overlay of those detections has not been built. G-10 also failed (no fish detection bounding boxes). Investigation required. Reported on-boat S104 2026-07-21. Full record: `V09994_BUG_FIXES.md` BUG-20. |
| BUG-21 | No verbal or visual warning triggered when cameras detect waterway hazards | `[~]` **RESOLVED by BUG-33 config fix S110 2026-07-29 — pipeline confirmed built end-to-end; on-boat validation required** | Cameras functioning. Kayakers, deadhead log, ducks, geese, and swimmers were observed at close range. No audio warning and no visual alert were generated. Root cause: hazard warning pipeline (camera detection → alert threshold → audio/visual notification) is likely not implemented end-to-end. SafeHelm collision avoidance is design-only (no code). signalk-forward-watch forward-watch alerting to d3kOS notification system may not be wired. Blocking: operator cannot safely use d3kOS as a situational awareness tool without this feature. Reported on-boat S104 2026-07-21. Full record: `V09994_BUG_FIXES.md` BUG-21. |
| BUG-22 | Setup wizard bypassed on fresh load — goes straight to dashboard | `[ ]` **OPEN — logged S104 2026-07-21** | On fresh browser load (or cleared cookies), the system is expected to redirect to the Setup Wizard (Step 1 of 6). Instead it goes directly to the main dashboard. B-01 and B-02 both failed. Root cause candidates: (1) wizard-completed flag set incorrectly or persisted from prior session; (2) redirect logic in dashboard entry point checking wrong condition; (3) cookie/localStorage detection broken after system update. Reported on-boat checklist S104 2026-07-21. Full record: `V09994_BUG_FIXES.md` BUG-22. |
| BUG-23 | Boat Log voice note transcription failing — recorded entry does not appear | `[~]` **DIAGNOSED S105 2026-07-23 — partial** | Tapping voice record, speaking, and tapping stop does not produce a VOICE entry in the Boat Log list. H-03 failed. Root cause candidates: (1) STT (speech-to-text) transcription service not running or not reachable; (2) voice-note POST to `/api/boatlog/voice-note` endpoint failing; (3) entry written to DB but not rendering in log list. Reported on-boat checklist S104 2026-07-21. Full record: `V09994_BUG_FIXES.md` BUG-23. |
| BUG-24 | Boat Log engine auto-capture not working — no ENGINE badge entry after engine running | `[~]` **ROOT CAUSE FOUND S107 — fully downstream of BUG-29** (not an independent bug) | `boatlog-engine.js` gates on `rpmHz > RPM_THRESHOLD_HZ (3)` reading `propulsion.0.revolutions`, which Signal K never publishes (it publishes `propulsion.port.revolutions`) — so `rpm_hz` stays 0 and the engine is never considered running. There is **no server-side capture service**: `/opt/d3kos/services/boatlog/` contains only `boatlog-export-api.py`; capture is client-side JS and only runs while the dashboard page is open. Retest after BUG-29 and BUG-31. Original report: after running the engine for 30+ minutes, no ENGINE badge entry appeared automatically in the Boat Log (H-04 failed), on-boat checklist S104 2026-07-21. S107 resolves candidate (2) — there is no auto-capture *service* by design — and supersedes candidate (3): the threshold logic is correct, the subscription path is wrong. Full record: `V09994_BUG_FIXES.md` BUG-24 + BUG-29. |
| BUG-25 | AI Navigation (Gemini) — "could not connect" — entire feature non-functional on boat | `[x]` **NOT A BUG — S107 verified live ON THE BOAT.** `:3001/status` → `{"gemini_key":true,"model":"gemini-2.5-flash-lite","online":true}`; egress OK (google.com → 200, DNS resolves); real query `POST /ask` returned `{"response":"A safe anchoring depth is generally 10 and 30 feet…","tokens":290}`. The S105 "internet egress" hypothesis is disproven — egress and the AI both work. Operator to retest on-screen; if it fails there, log as a NEW front-end bug (note the hardcoded `localhost:8097` URL in BUG-34). | AI Navigation page fails to connect on the boat. J-01, J-02, J-03 all failed. Root cause candidates: (1) gemini-proxy service (port 8097) not running; (2) gemini-nav service (port 3001) not running; (3) API key in `api-keys.json` or `gemini.env` invalid or missing; (4) model changed — memory says `gemini-2.5-flash-lite` is the required model on all environments. Two Gemini services on Pi: gemini-proxy port 8097 (reads `api-keys.json`) + gemini-nav port 3001 (reads `gemini.env`) — both must be checked. Reported on-boat checklist S104 2026-07-21. Full record: `V09994_BUG_FIXES.md` BUG-25. |
| BUG-26 | Anchor Watch — Set Anchor failing; no alarm sound when radius exceeded | `[~]` **FIXED IN LAB ONLY — S107: NOT on the boat Pi** (`AI_BRIDGE` 0 occurrences; `anchor-watch.html` dated Apr 12). Will still reproduce on-boat. See BUG-28. | Root cause: anchor-watch.html calls fetch('/anchor/*') → resolves to dashboard :3000 (no routes) → 404. ai-bridge :3002 serves /anchor endpoints (confirmed live). Fix: add const `AI_BRIDGE = 'http://localhost:3002'`, prefix 5 fetches (set/clear/dismiss/advice/state). SSE unchanged (already :3002). TDD source check verified: 5 AI_BRIDGE-prefixed, 0 bare calls. Deployed via AAO atomic spec + Tier-3 build + Tier-1 verify. K-02 (Set Anchor arms) now functional; K-03 (alarm) is downstream of K-02 (retest after K-02 confirmed working on-boat). Full record: `V09994_BUG_FIXES.md` BUG-26; spec: `deployment/docs/atomic-specs/BUG-26.md`. |
| BUG-27 | Status bar (vessel name + clock) text too small to read at 1 metre — AODA violation | `[~]` **DEPLOYED TO LAB PI ONLY — S107: NOT on the boat Pi** (`.sb-vessel` still 18px) | Root cause CORRECTED: nothing was below 18px — `.sb-vessel` was 18px (AODA floor), `#clk` 22px; 18px floor ≠ helm-legible on 10.1" screen. Fix: raised `.sb-vessel` 18→28px, `#clk` 22→26px in `#sb` (d3kos.css). Deployed to `/opt/d3kos/services/dashboard/static/css/d3kos.css` (backup `.bak.20260723`). Done via AAO §23/§25 atomic spec + Tier-3 (Haiku) build + Tier-1 (Opus) verify. Operator must confirm 1 m legibility on-screen (hardware check). Full record: `V09994_BUG_FIXES.md` BUG-27; spec: `deployment/docs/atomic-specs/BUG-27.md`. **⚠ S107: NOT on the boat Pi — `.sb-vessel` still 18px, no `.bak.20260723`. Status is DEPLOYED TO LAB PI ONLY; the 1 m confirmation was not on the boat screen. See BUG-28.** |
| BUG-28 | Boat Pi running v0.9.2.2 — S96/S105 fixes absent; two deploy sources diverged | `[~]` **OPEN — logged S107; ⚠ LINEAGE CLAIM CORRECTED S108.** S107 called `pi_source` "frozen/stale" and `d3kOS/dashboard` "current" — **that is backwards**: `pi_source` IS the v0.9.9.2 release tree and `d3kOS/dashboard` never had the v0.9.9.2 features (md5-proven — see the S108 LINEAGE CORRECTION block in `V09994_BUG_FIXES.md`, and BUG-36/37). Also: `version.txt` is a **stale label, not a version** — the lab Pi read v0.9.2.2 while running v0.9.9.2 code, so the boat is likely v0.9.9.2-era missing only the three S105 patches, not four months behind. Confirm on-boat via `manual.html`. Resolution: lab Pi = master, relabelled v0.9.9.4. | `version.txt` = v0.9.2.2 (build 2026-03-23). BUG-27 `.sb-vessel` still 18px; BUG-15 `_lastSogKts` 0 occurrences; BUG-26 `AI_BRIDGE` 0 occurrences; no `.bak.20260723` backups exist; `settings.json` mtime 2026-03-12 (so the S96 AIS fix is absent too). Pi is otherwise healthy — data files written 15:01 on 2026-07-27, exports from Apr 15/Apr 22 — only the deployed **code** is frozen. Root cause: `deployment/v0.9.4/pi_source/instruments.js` last commit `9800728` 2026-04-08 vs `deployment/d3kOS/dashboard/.../instruments.js` last commit `4420050` 2026-07-23 → `diff` DIVERGED, violating `concepts/two-source-sync-rule`. Uncertainty: not yet distinguished whether the boat was built from the stale tree or imaged before 2026-07-23. **Deferred operator action: confirm the lab Pi version when back in the lab.** Full record: `V09994_BUG_FIXES.md` BUG-28. |
| BUG-29 | Dashboard subscribes `propulsion.0.*`; Signal K publishes `propulsion.port.*` — every engine gauge dead | `[~]` **FIXED + DEPLOYED TO LAB PI 2026-07-27 S108-cont — NOT on the boat Pi** (Tier 3 + Tier-1 §25.8 ACCEPT 13/13). Additive aliasing across 4 files — **not** a rename; both `propulsion.0.*` and `propulsion.port.*` dispatch. Two paths also needed a **leaf** correction (`.temperature`, `.drive.trimState`). `electrical.batteries.0.voltage` + `tanks.fuel.0.currentLevel` confirmed CORRECT and untouched. Spec: `atomic-specs/BUG-29.md`. | `curl .../propulsion` returns keys `['port']`. Repo (both trees): `propulsion.0.` ×8, `propulsion.port.` ×0. Only `tanks.fuel.0.currentLevel` coincidentally matches — which is why fuel is the one gauge receiving data. Cascade: `_d3kEngData` stays `{coolant:null,oil:null,rpm:null,bat:null,fuel:0}` → **root cause of BUG-24** (`boatlog-engine.js` gates on `rpmHz > 3`, never fires) and a **root cause of BUG-16** (Gemini receives "Current readings: fuel 0%" for every gauge). Blast radius 6 live files: `instruments.js`, `boatlog-engine.js`, `engine-monitor.html`, `helm-assistant.html` (d3kOS tree) + `instruments.js`, `engine-monitor.html` (pi_source tree). **Present in the latest source — a redeploy will not fix it.** Full record: `V09994_BUG_FIXES.md` BUG-29. |
| BUG-30 | Depth gauge reads `environment.depth.belowKeel`; Signal K publishes `belowTransducer` | `[~]` **FIXED + DEPLOYED TO LAB PI 2026-07-27 S108-cont — NOT on the boat Pi** (Tier 3 + Tier-1 §25.8 ACCEPT 16/16). **The primary fix is CONFIGURATION** — Signal K already computes `belowKeel` when PGN 128267 carries a negative offset, so setting a keel offset on the Garmin makes the existing code work with zero change. The code adds a fallback that renders `belowTransducer` only when no `belowKeel` exists and relabels the cell **UNDER TRANSDUCER**. Spec: `atomic-specs/BUG-30.md`. | With the Garmin connected: `environment.depth.belowTransducer` = **0.99 m**, `$source: can0.0`, PGN 128267 arriving ~1 Hz (Garmin src 0 also sends 129025/129026/129029 ×420 and 130310/130312 ×50 per 20 s). Dashboard subscribes to `belowKeel`; repo has `belowKeel` ×2, `belowTransducer` ×0; no keel/transducer offset configured in Signal K so `belowKeel` is never derived. **E1 confirmed — the sounder exists and the data arrives.** Decision needed: configure the offset (safer displayed value) vs. subscribe to `belowTransducer` and relabel the gauge. Full record: `V09994_BUG_FIXES.md` BUG-30. |
| BUG-31 | Unidentified N2K device at src 64 broadcasting frozen engine data + false 0% fuel | `[ ]` **OPEN — logged S107 2026-07-27 — needs physical ID on the boat** | `candump`: `09F20040` PGN 127488 src 64 ×201/20s (10 Hz), payload **byte-identical every frame**: `00 00 00 96 05 00 FF FF` → 0 RPM, boost 143,000 Pa (engine has **no turbo/supercharger**), trim 0. Also `19F21140` PGN 127505 src 64 ×8/20s → fuel **0% on a confirmed-FULL tank**, capacity 1.16 m³ ≈ 306 US gal. Identity (PGN 126996): `modelId "Pangoo"`, mfr 1998, product 1002, serial `N20210700100`, cert Level B, LEN 2, class *Internetwork device*, fn 132 (A/D converter). Signal K binds the engine gauges to **src 64's zeros, not to the CX5106 (src 106)**, which sends heartbeat PGN 126993 only. Simulator hypothesis **checked and ruled out** — no simulator files/units/processes on the Pi; the src-64 address match with the removed sim script is coincidence. `[UNVERIFIED INFERENCE]` may be the original CX5106 from S98; WebSearch did NOT confirm Pangoo as the CX5106 maker. Blocks trustworthy validation of BUG-14/16/17/24. Full record: `V09994_BUG_FIXES.md` BUG-31. |
| BUG-32 | AIS never reaches Signal K — rtl_ais pushes to TCP 10110 which Signal K itself occupies | `[~]` **FIXED (lab) — on-boat validation required** S110 2026-07-29 | `ss -tlnp`: `LISTEN *:10110 users:(("node",pid=2152))` = Signal K's own NMEA0183 **output** server. rtl_ais journal: *"AIS data will be sent to 127.0.0.1 port 10110"* — it is a **client** pushing into an output socket, so AIS is discarded. 20 s listen on 10110 → **0 AIVDM**, only `$GPGGA/$GPRMC/$GPZDA/$GPGSV`. SK vessels API → 1 entry (self only), zero AIS targets. Second fault: `ais` pipedProvider `enabled: false` (S96 fix absent — see BUG-28). Hardware is fine: RTL2838 on USB, rtl_ais running, tuned 162.000 MHz, decoder enabled, dongle serial `myAIS`. Fix must also guard the Signal K/rtl_ais boot-order race. Confirm AIS reaches SK **before** judging BUG-19/BUG-20 overlays. Full record: `V09994_BUG_FIXES.md` BUG-32. |
| BUG-33 | Hazard alerting disabled and 5-minute detection interval in forward-watch config | `[~]` **CONFIG FIXED on lab Pi S110 2026-07-29 — on-boat validation required** — refines BUG-21 | `signalk-forward-watch.json`: **`audio_alarm: false`** (audible path switched off) and **`detection_interval: 300`** — 300 s = **5 minutes** between passes, useless for a kayaker/swimmer/deadhead at close range. Signal K `notifications` tree **absent entirely** (top-level keys: environment, navigation, propulsion, tanks, uuid). Cameras ARE reachable — `ping 10.42.0.100` 0% loss, startup scan found 4 RTSP hosts (`.63/.100/.133/.181`); Pi is subnet gateway `eth0 10.42.0.1/24`. **Zero** forward-watch lines in last 200 SK journal entries. So BUG-21 is partly a config defect, not purely "never built". Also security: `camera_pass` plaintext and embedded in the RTSP URL. Full record: `V09994_BUG_FIXES.md` BUG-33. |
| BUG-34 | Gauge tap: hardcoded alarm string + generic thresholds not from boat documentation | `[~]` **FIXED + DEPLOYED TO LAB PI S110 2026-07-29** (Tier 3 + Tier-1 §25.8 ACCEPT 9/9). instruments.js: THR.oil.crit 20→4 (MerCruiser 454 idle min); bat_hi added (overcharge); depth_m added to _d3kEngData. overlays.js: alarm string de-fabricated; openDiag URL portable (window.location.hostname); overcharge guard on battery card; fuel + depth cards added. Atomic spec: `atomic-specs/BUG-34.md`. **NOT on the boat Pi.** | `overlays.js`: (1) `showCrit()` hardcodes `'⛔ CRITICAL — OIL PRESSURE 8 PSI — TAKE ACTION NOW'` — a fabricated reading; (2) `THR` are generic JS literals `oil:{adv:30,alrt:25,crit:20}`, `coolant:{88,98,105}`, `bat:{12.4,12.0,11.5}` — **not** this boat's documented values (S106-sourced MerCruiser 454: oil ≥30 psi@2000 / **≥4 psi at idle**, thermostat 160 °F/71 °C, alternator 13.9–14.7 V) → a normal idle oil pressure is flagged **"Critical"**, and battery has **no upper bound** so a 15.5 V overcharge reads "✓ Normal" (safety gap); (3) `_diagBuildCards()` has no fuel or depth card though `_diagCellLabel()` maps `cellFuel`/`cellDepth`; (4) **tier gate RULED OUT** — `license.json` `tier: T3`, the `tier < 2` branch is not taken; (5) `openDiag()` posts to hardcoded `http://localhost:8097/gemini/chat` — fails from the PWA/phone. Full record: `V09994_BUG_FIXES.md` BUG-34. |
| BUG-35 | OTA upgrade wipes 3 of the 4 fields in `version.txt` — latent, never fired | `[~]` **FIXED + DEPLOYED TO LAB PI 2026-07-27 S108-cont — NOT on the boat Pi** (Tier 3 + Tier-1 §25.8 ACCEPT 12/12) | `ota_upgrade.py` step 7 rewrites the whole file as a single line — `VERSION_FILE.write_text(f'd3kOS Version {latest_ver}\n')` — truncating away `Release Date`, `Status` and `Build`. **Silent failure:** `ota_upgrade.get_current_version()` and `cloud_agent.get_version()` need only line 1 so nothing errors, but `export_categories.collect_version()` loses its `release_date` and `status` keys. **3 live copies, all at line 277:** `/opt/d3kos/services/cloud-agent/ota_upgrade.py` (the live one — `d3kos-cloud-agent` has `WorkingDirectory=/opt/d3kos/services/cloud-agent`), `/opt/d3kos/services/ota_upgrade.py` (**diverged** — md5 `7043f1d7…` vs `6105de65…`), and repo `deployment/v0.9.4/pi_source/ota_upgrade.py` (frozen `pi_source` tree, see BUG-28). Will wipe the S108 label correction (0.9.9.2 / April 12, 2026 / Release) on the first OTA. **NOT the cause of the S108 stale label** — `version.txt` still held all four fields at mtime 2026-03-23, so no OTA has ever run; the April 12 v0.9.9.2 release never touched the file at all. Full record: `V09994_BUG_FIXES.md` BUG-35. |
| BUG-36 | S105 deploy regressed `instruments.js` — M14 engine-data cache silently removed | `[~]` **FIXED + DEPLOYED TO LAB PI 2026-07-27 S108-cont — NOT on the boat Pi** (Tier 3 + Tier-1 §25.8 ACCEPT 13/13) | The S105 BUG-15 deploy (2026-07-23 10:12) sourced `instruments.js` from `deployment/d3kOS/dashboard/`, which never contained the M14 cache. Pre-S105 backup `instruments.js.bak.20260723` = md5 `496d9800…` = `pi_source` with `_d3kEngData` **×6**; current file = md5 `d957fb8b…` = `d3kOS/dashboard` with **×0** (19,201 → 18,794 bytes). `overlays.js` line 61 reads `const eng = window._d3kEngData \|\| {};` — nothing populates it, so `[UNVERIFIED INFERENCE — code path, page not loaded]` the M14 diagnostic renders empty cards. The COG fix itself was correct; it was applied to a file from the wrong lineage. Fix must restore the cache **while keeping** the S105 `_lastSogKts` gate. Full record: `V09994_BUG_FIXES.md` BUG-36. |
| BUG-37 | Dashboard `app.py` missing all seven v0.9.9.2 routes | `[~]` **FIXED + DEPLOYED TO LAB PI 2026-07-27 S108-cont — NOT on the boat Pi** (Tier 3 + Tier-1 §25.8 ACCEPT 9/9) | Lab Pi `app.py` md5 `34211e37…` = `deployment/d3kOS/dashboard/app.py`; the v0.9.9.2 tree (`pi_source/app.py`, md5 `d06b15da…`) defines seven routes the deployed file lacks: `/config/tier`, `/anchor/set`, `/anchor/state`, `/anchor/clear`, `/anchor/dismiss`, `/anchor/advice`, `/helm/mute`. **This is the true root cause of BUG-26** — the S105 `AI_BRIDGE` change is a workaround for proxy routes v0.9.9.2 already provides on :3000. Also disables the M14 tier gate (`/config/tier`) and leaves the S44 `/helm/mute` CORS fix with no server side. Full record: `V09994_BUG_FIXES.md` BUG-37. |
| BUG-38 | `overlays.js` writes to three DOM IDs `index.html` never defines — present in the v0.9.9.2 release itself | `[~]` **FIXED + DEPLOYED TO LAB PI 2026-07-27 S108-cont — NOT on the boat Pi** (Tier 3 + Tier-1 §25.8 ACCEPT 15/15) | `overlays.js` (md5-identical to the v0.9.9.2 source) calls `getElementById('diagGrid')`, `('diagTitle')`, `('diagAiTxt')`. The deployed `index.html` **matches v0.9.9.2 exactly** and defines only `id="diagBack"`; both repo trees' `index.html` are md5-identical (`295f287c…`) and define none of the three. DEPLOYMENT_INDEX records these IDs as added in S39 — **that change was never committed to either tree**. All three lookups return `null`, so with BUG-36 the diag panel has neither data nor a container. Second independent root cause of BUG-16. Full record: `V09994_BUG_FIXES.md` BUG-38. |
| BUG-39 | Cloning the master duplicates six identity values across two Pis | `[~]` **DEPLOYED TO LAB PI S108-cont — unit DISABLED, master GUARDED** (Tier 3 + Tier-1 §25.8 ACCEPT 23/23). Operator chose option 2: deploy both files, do not enable, and create `/opt/d3kos/config/.identity-regenerated` on the master so it can never fire there. Three guards verified: systemd `ConditionResult=no`, the script's sentinel check is its first logic, unit `disabled`. Master identity byte-identical before and after. **⚠ CLONE PROCEDURE — on the COPY, `rm /opt/d3kos/config/.identity-regenerated` and `systemctl enable d3kos-identity-regen`, or the clone keeps the master's identity and BUG-39 is unfixed.** | Read from the lab Pi: `device_token` `701e5754-e2ce-4fa3-97a6-f2c7c7e020c6` (**most serious** — one cloud identity for two Pis; telemetry, Fix My Pi, fleet and PWA pairing all collide in `amboat_devices`); `installation_id` `3861513b314c5ee7` (tier T3); Signal K vessel UUID `urn:mrn:signalk:uuid:e1592142-…`; `machine-id` `c654e389…`; 3 SSH host keys; filesystem UUIDs `d6944274…` / `F587-071F` (a third copy joins the existing SD↔USB duplicate pair — PARTUUIDs differ so boot is safe, but UUID-based mounts are ambiguous). Requires a first-boot identity-regeneration script before any clone. Full record: `V09994_BUG_FIXES.md` BUG-39. |
| BUG-40 | Signal K runs with a different vessel UUID than `settings.json` declares | `[x]` **FIXED + DEPLOYED lab Pi** S110 2026-07-29 | `~/.signalk/settings.json` sets `vessel.uuid = urn:mrn:signalk:uuid:af7d4be0-fb1d-4164-976d-de373c1c0331`, but the live API reports `…e1592142-4955-4b4d-a085-40fa674e0e13`. The configured identity is being **ignored**. The live value is on disk **nowhere** (`grep -rl` across `/home/d3kos`, `/opt/d3kos`, `/etc` → no match), `serverState/` is empty and `defaults.json` does not exist — so SK v2.23.0 is generating the vessel identity at runtime rather than reading the configured one. Impact: the vessel's declared identity is not the one published to the N2K/AIS layer or to any consumer of `vessels.self`. Found while resolving Q39.3 for BUG-39; it **removes** the SK UUID from BUG-39's scope (nothing persistent to duplicate). Not yet diagnosed: whether SK v2 moved vessel identity to `defaults.json` (absent here) and silently ignores the legacy `settings.json` `vessel` block. Full record: `V09994_BUG_FIXES.md` BUG-40. |
| BUG-41 | `/settings` returns HTTP 500 — `settings.html` needs `tier_num`, `app.py` never passes it | `[~]` **FIXED + DEPLOYED TO LAB PI S110 2026-07-29** (Tier 3 + Tier-1 §25.8 ACCEPT). app.py settings() now reads tier_num from license.json and device_token from device-token.json with safe defaults (0, ''). Passes both to render_template. Atomic spec: `atomic-specs/BUG-41.md`. Verified: `/settings` → 200 post-deploy. **NOT on the boat Pi.** | `jinja2.exceptions.UndefinedError: 'tier_num' is undefined` at `app.py:347` rendering `settings.html`. **Another casualty of the lineage split** (see BUG-36/37): `pi_source/settings.html` does **not** use `tier_num` while `pi_source/app.py` **does** pass it (works); `d3kOS/dashboard/settings.html` **does** use it while its `app.py` does **not** pass it (breaks). The Pi has the d3kOS-lineage pairing of both halves → 500. **Pre-existing since 2026-04-13** — `settings.html` mtime is Apr 13 and the S108-cont deploy left both `settings()` and `settings.html` byte-identical; proven not caused by that deploy. Fix options: (a) pass `tier_num` from `settings()` — small and targeted, or (b) adopt `pi_source/settings.html` — older lineage, may lose later content. Needs an atomic spec. Full record: `V09994_BUG_FIXES.md` BUG-41. |

**S107 observations (logged, not yet separate bugs):** Pi clock jumped at boot — journal shows "Jul 20 18:09" for services `ps` reports as started 2026-07-27 14:11:53 (stale RTC then corrected; undermines log forensics, relevant to BUG-09). can0 shows **543 dropped RX frames** / 2 errors (bus ERROR-ACTIVE, bitrate 250000 correct). Plaintext camera credentials in plugin config (see BUG-33).

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
| DEP20 | Dual dashboard source-of-truth audit | `[~]` **SUPERSEDED S108 — resolution approved** | **S108 correction:** the two trees are not peers to be kept in sync — `deployment/v0.9.4/pi_source/` **IS the v0.9.9.2 release tree** (it stopped changing at release, which is why its dates look stale) and `deployment/d3kOS/dashboard/` is a separate lineage that never contained the v0.9.9.2 features (`_d3kEngData`, `/config/tier`, the 5 anchor routes, `/helm/mute`). Proven by md5 — see the S108 LINEAGE CORRECTION block in `V09994_BUG_FIXES.md`. The "add every new page to BOTH dirs" instruction is what produced BUG-36/BUG-37. **Operator decision S108:** the lab Pi is the master (relabelled v0.9.9.4 In Development); a new canonical tree will be seeded **from the Pi** and both old trees archived. Supersedes this item. |
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
