# v0.9.9.4 — Holistic Bug Fix Plan

**Version:** 1.0.0
**Created:** 2026-07-31 (S114)
**Owner:** Skipper Don / AtMyBoat.com
**Source of truth for:** what is fixed, what is in flight, what is next.

---

## HOW TO USE THIS FILE

This file exists so that no context is ever lost between sessions or across a
conversation compaction. It is the authoritative work state.

**For Don (Windows Explorer path):**
`\\wsl.localhost\Ubuntu\home\boatiq\Helm-OS\deployment\docs\V09994_FIX_PLAN.md`

**For Claude, at the start of any bug work:**
1. Read this file. Read only this file — not `SESSION_LOG.md`, not the full
   `V09994_BUG_FIXES.md`.
2. Find the first batch whose status is not `DONE`.
3. Read only the bug entries for that batch from `V09994_BUG_FIXES.md`.
4. Do the work. Update the Progress Log at the bottom of this file
   **before** replying to the operator.

**Rule:** the Progress Log is updated after every unit of work, not at session
close. If the conversation compacts mid-batch, the log is what survives.

**Detail lives elsewhere.** This file holds sequencing and state only. Symptom,
root cause, and fix detail stay in `V09994_BUG_FIXES.md` under each `BUG-XX`.

---

## 1. WHY THE LAST ON-BOAT TEST APPEARED TO FAIL

Recorded here because it caused a loss of confidence and must not be
re-litigated from memory in a future session.

The S112 cruise (2026-07-31, 25 min active maneuvering) did **not** show that
the software fixes failed. Per `S112_cruise_validation_report.md`:

- BUG-30 (depth) tracked 0.90 m → 3.80 m → 1.08 m correctly. **Working.**
- BUG-32 (AIS) detected 2 vessels consistently. **Working.**
- BUG-29 (propulsion aliases) byte-verified present in served `instruments.js`. **Deployed.**

The engine ribbon was dark for a **hardware** reason that no software change can
address: the CX5106 was absent from the N2K bus, and the Pangoo's tachometer
input is dead. Gauges cannot display data that no device is transmitting.

One genuine new software defect was layered on top — BUG-45, a false critical
alarm firing on every boot because there is no engine-running gate.

**Conclusion:** good fixes, tested against dead hardware, plus one real new bug.
The remedy for that is sequencing (fix the hardware first), not rewriting the
fixes.

---

## 2. THE TWO META-BUGS

Everything else is blocked behind these. They are batched first for that reason.

### META-A — Deployment state is not knowable
`BUG-28, 35, 36, 39, 40`

There is no trustworthy way to determine what code is running on a given Pi.
Symptoms of this meta-bug already in the record:

- `version.txt` is a stale label; `check-drift.sh` compares Pi against MANIFEST,
  not repo against MANIFEST — a green result does not mean the Pi is current.
- A deploy (S105) silently **removed** a working feature (BUG-36).
- **17 entries in `V09994_BUG_FIXES.md` are tagged "NOT on the boat Pi", but the
  S112 cruise report shows those fixes were present on the boat** — because the
  boat Pi is a clone of the lab Pi. The document and the field evidence
  contradict each other as of this writing. Only BUG-42/44/45 (fixed S113,
  after the clone) are genuinely absent from the boat.

Until this is fixed, **every on-boat test result is uninterpretable**, because
the build under test is unknown.

### META-B — No trustworthy engine data source
`BUG-14, 31` — blocks `BUG-16, 24` and the testability of `29, 42, 44, 45`

- **CX5106** is absent from the bus. Root cause on record: the tachometer wire
  (blue, Pole 3 of the RPM gauge) was never permanently clipped.
- **Pangoo (src 64)** is broadcasting frozen RPM/trim and oscillating false fuel
  (0% → 20% → 3% → 12% → 1% over 25 min). This is worse than no data, because
  the dashboard renders it as truth.

This is a multimeter task, not a coding task.

---

## 3. BUG INVENTORY — 39 ENTRIES

Status as read from `V09994_BUG_FIXES.md` on 2026-07-31.

| Status | Count | Bugs |
|---|---|---|
| `[x]` Closed | 7 | 07, 10, 12, 22, 26, 27, 40 |
| `[~]` Fixed in lab / in progress | 21 | 08, 13, 14, 17, 21, 23, 25, 29, 30, 32, 33, 34, 35, 36, 37, 38, 39, 41, 42, 44, 45 |
| `[ ]` Open | 11 | 09, 11, 15, 16, 18, 19, 20, 24, 28, 31, 43 |

### 3.1 VERIFIED LIVE ON THE LAB PI — S114 2026-07-31

Read directly from `192.168.1.237`, not from a deploy record. This is evidence,
per the S109 rule.

| Bug | Marker checked | File | Result |
|---|---|---|---|
| BUG-29 | `propulsion.port` | `static/js/instruments.js` | ✅ PRESENT |
| BUG-36 | `_d3kEngData` | `static/js/instruments.js` | ✅ PRESENT |
| BUG-30 | `belowTransducer` | `static/js/instruments.js` | ✅ PRESENT |
| BUG-42 | `_oilCritAcknowledged` | `static/js/instruments.js` | ✅ PRESENT |
| BUG-45 | `_skFirstConnectAt` | `static/js/instruments.js` | ✅ PRESENT |
| BUG-44 | `webhook/alert` | `static/js/overlays.js` | ✅ PRESENT |
| BUG-38 | `diagGrid` | `templates/index.html` | ✅ PRESENT |
| BUG-37 | `/config/tier` | `app.py` | ✅ PRESENT |
| BUG-17 | `cellBat` | `templates/index.html` | ✅ CORRECTLY ABSENT (cell removed) |
| BUG-41 | `/settings` HTTP | live | ✅ 200 |
| BUG-43 | `d3kUnitPrefs` | `static/js/instruments.js` | ❌ ABSENT — not yet fixed |

Services: `d3kos-dashboard` active · `signalk` active · `avnav` active ·
`d3kos-ai-bridge` active · `rtl-ais` **crash-looping** (no dongle) ·
`d3kos-voice-watchdog` **failed** (BUG-23a confirmed live).

`forward-watch` config location confirmed:
`/home/d3kos/.signalk/plugin-config-data/signalk-forward-watch.json`
(it is NOT in `/opt/d3kos/config/` — earlier assumption was wrong).

### 3.2 WHAT ACTUALLY REMAINS — the real number

The "39 bugs" figure is misleading. Reconciled:

| Category | Count | Bugs |
|---|---|---|
| Closed / not a bug | 6 | 07, 10, 12, 22, 26, 27 |
| Fixed + verified live on lab Pi | 10 | 17, 29, 30, 36, 37, 38, 41, 42, 44, 45 |
| Fixed in lab per record, not yet re-verified | 8 | 13, 21, 32, 33, 34, 35, 39, 40 |
| Moved to v0.9.9.5 (approved S114) | 2 | 11, 23b (STT engine) |
| Hardware — boat only | 2 | 14, 31 |
| Not a d3kOS defect (boat internet egress) | 1 | 25 |
| **REMAINING LAB WORK** | **10** | **08, 09, 15, 16, 18, 19, 20, 24, 43, 23a** |

Of those 10, two are likely already resolved and need confirming, not fixing:
- **BUG-18** (depth) — superseded by BUG-30, which tracked correctly through the
  entire S112 cruise. Probably closeable on evidence already held.
- **BUG-16** (gauge tap hardcoded) — may be satisfied by the BUG-34 fix. Verify
  before writing anything.

**Realistic remaining lab work: 8 items.** Not 39.

---

## 4. THE BATCHES

Batches are ordered by dependency, not by severity. A batch is not started
until every batch above it is `DONE`.

Each batch is a **single holistic fix** — one shared root cause, one design,
one deploy, one validation. Bugs inside a batch are never fixed one-off.

---

### BATCH 1 — Deployment state integrity
**Status:** `NOT STARTED`
**Bugs:** BUG-28, BUG-35, BUG-36, BUG-39, BUG-40
**Location:** Lab only. No boat trip.
**Blocks:** every subsequent validation

**Shared root cause:** no single source of truth for what is running on a Pi.

**Holistic fix — one deliverable, not five patches:**
1. A release-state verifier that fingerprints the actual files on a Pi (md5 per
   file) and reports drift against a manifest. Compares **repo → manifest → Pi**,
   closing the `check-drift.sh` gap.
2. Make `version.txt` write-safe across OTA (BUG-35).
3. Wire the BUG-39 identity-regeneration unit into the clone procedure (Phase B,
   never started).
4. Reconcile all 17 stale "NOT on the boat Pi" tags against a live read of both
   Pis, and replace the per-bug annotations with one generated release-state table.

**Definition of done:** running one command prints an accurate, current table of
what is deployed on the lab Pi and the boat Pi, and the two are reconciled.

---

### BATCH 2 — Engine data source (HARDWARE — operator task)
**Status:** `NOT STARTED`
**Bugs:** BUG-14, BUG-31 → unblocks BUG-16, BUG-24
**Location:** Boat. Multimeter. No code.
**Blocks:** Batch 4 validation, and all engine gauge work

**Tasks:**
1. Permanently clip the CX5106 tachometer wire (blue, Pole 3, RPM gauge).
   Confirm src 106 appears in Signal K sources and stays present.
2. Physically identify the Pangoo (src 64) and decide: repair its tach input, or
   **remove it from the bus**. It is currently publishing false fuel and RPM
   data that the dashboard displays as real.

**Reference:** `mercruiser_7p4l_gauge_wiring.md` — Monterey 265 SEL uses
NON-STANDARD wire colours (three failed identification attempts in S101).
Identify by the moulded gauge post letter (I/S/G/L) plus multimeter resistance
on the S post. **Never unplug the tach harness** — ignition 12 V runs through it.

**Definition of done:** Signal K shows a stable src 106 with live oil pressure
and coolant temperature, and no source is publishing false engine data.

---

### BATCH 3 — Signal K ↔ dashboard data contract
**Status:** `NOT STARTED`
**Bugs:** BUG-29, BUG-30, BUG-37, BUG-38, BUG-41
**Location:** Lab.

**Shared root cause:** the dashboard subscribes to paths and writes to DOM IDs
that do not exist. The same defect five separate times:

- BUG-29 — subscribes `propulsion.0.*`; SK publishes `propulsion.port.*`
- BUG-30 — reads `belowKeel`; SK publishes `belowTransducer`
- BUG-37 — `app.py` missing all seven v0.9.9.2 routes
- BUG-38 — `overlays.js` writes to three DOM IDs `index.html` never defines
- BUG-41 — `/settings` HTTP 500: `tier_num`/`device_token` never passed to template

All five already have fixes deployed to the lab Pi. **The remaining work is not
the fixes — it is the missing test.**

**Holistic fix:** a contract test that enumerates every SK path the dashboard
subscribes to, every DOM ID the JS writes to, and every route the templates
call, then asserts each one exists. Run it in CI and pre-deploy. This class of
bug then cannot recur silently.

**Definition of done:** contract test exists, passes, and would have caught all
five of these bugs.

---

### BATCH 4 — Alarm subsystem
**Status:** `NOT STARTED`
**Bugs:** BUG-42, BUG-44, BUG-45, BUG-33, BUG-21
**Location:** Lab, then boat validation (needs Batch 2 for a real engine signal).

**Shared root cause:** the alarm system was never designed end-to-end. It has no
state machine, no debounce, no engine-running gate, and no TTS wiring.

- BUG-45 — false critical alert on every boot (no boot gate). **Alert fatigue = HIGH severity.**
- BUG-42 — ACKNOWLEDGE cannot dismiss; overlay re-fires within 1 s (no latch)
- BUG-44 — visual alert fires with no voice announcement (TTS never called)
- BUG-33 — hazard alerting config disabled and far too slow (`audio_alarm: false`, `detection_interval: 300`)
- BUG-21 — no verbal or visual hazard warning (resolved by BUG-33 config)

42/44/45 are fixed and deployed to the lab Pi (S113) but are **genuinely not on
the boat Pi** — they post-date the clone.

**Holistic fix:** one alarm state machine — `IDLE → ARMED → RAISED → ACKED →
CLEARED` — with a single boot/engine-running gate, one acknowledge latch, and
one notification sink that drives both the overlay and TTS. Replace the ad-hoc
per-gauge alert calls with it.

**Definition of done:** no alert on boot with engine off; ACKNOWLEDGE dismisses
and stays dismissed until the condition clears and re-occurs; every critical
alert speaks.

---

### BATCH 5 — Chart overlay integration
**Status:** `NOT STARTED`
**Bugs:** BUG-19, BUG-20, BUG-32
**Location:** Lab, then boat validation (RTL-SDR dongle is absent from the lab Pi).

**Shared root cause:** the AvNav overlay layer was never built. Signal K
receives the data; nothing renders it on the chart.

- BUG-32 — rtl_ais sent to TCP 10110, which SK itself occupies. Fixed in lab
  (moved to 10108); boat-validated as working in S112.
- BUG-19 — SK has AIS targets; AvNav does not display them
- BUG-20 — camera hazard detections do not reach the AvNav map

**Do not re-apply the S96 BUG-12 fix.** Enabling the `ais` provider on 10110
loops SK's own GPS back into itself. That path is closed permanently.

**Holistic fix:** one overlay feed from SK into AvNav carrying both AIS targets
and camera hazard contacts, rather than two separate integrations.

**Definition of done:** the AIS targets SK already receives appear on the AvNav
chart, and camera hazards appear on the same layer.

---

### BATCH 6 — UI and display
**Status:** `NOT STARTED`
**Bugs:** BUG-13, BUG-15, BUG-34, BUG-43
**Location:** Lab. BUG-13 and BUG-15 need boat validation (require real motion).

- BUG-13 — speed gauge flickers during throttle transitions (fixed lab; needs throttle test)
- BUG-15 — COG flashes different directions while stationary
- BUG-34 — gauge tap dialog: hardcoded alarm string, generic thresholds (fixed lab)
- BUG-43 — Imperial/Metric selection has no effect on gauges **(open)**

**Shared thread:** all four are the display layer presenting something other
than the live, correctly-scaled value.

BUG-15 and BUG-13 are likely the same underlying issue — no smoothing/deadband
on a noisy low-speed signal. Investigate them as one before writing two fixes.

**Operator unit preference: Imperial (°F, ft).** Atomic spec for BUG-43 exists at
`atomic-specs/S112-BUG-43-settings-unit-persistence.md`.

**Definition of done:** no flicker at steady state; units honour the setting and
persist across reload.

---

### BATCH 7 — Service resilience
**Status:** `NOT STARTED`
**Bugs:** BUG-09, BUG-08, BUG-25
**Location:** Lab.

- BUG-09 — AvNav data corruption after power loss; self-healing audit needed
- BUG-08 — Helm Assistant on-screen keyboard shows then immediately hides
- BUG-25 — Gemini cannot connect on boat. **Diagnosed as NOT a d3kOS bug** —
  points to internet egress on the boat hotspot. Pending on-boat confirmation.

**Holistic fix for BUG-09:** a service health and self-heal layer covering all
critical services, not an AvNav-specific patch. A boat loses power without
warning as a normal event; every service must survive it.

---

### PROPOSED FOR REMOVAL FROM THE BUG LIST
**Status:** `AWAITING OPERATOR DECISION`

These are **unbuilt features**, not defects. They inflate the bug count and make
the backlog look worse than it is.

- **BUG-11** — no universal method to verify any brand of AIS/GPS/mic/speaker.
  This is a new diagnostics feature.
- **BUG-23** — Boat Log voice transcription. Diagnosis found no local STT
  service exists. Faster-Whisper STT is scheduled as v0.9.9.5 item D13 — it was
  never built, so it cannot regress.

**Recommendation:** move both to the v0.9.9.5 backlog. That takes the count from
39 to 37 and makes the remainder honest.

---

## 5. VALIDATION STRATEGY — OPERATOR MODEL (S114, supersedes the batch-trip model)

**Operator directive, 2026-07-31:** fix all bugs in the lab → clone the master
card → one boat trip to verify each one → keep cost low, ship quality, finish fast.

This replaces the earlier per-batch validation model. Cloning solves the
deployment-state problem **physically** — if the boat card is a byte copy of the
lab card, there is nothing to verify about what is deployed. That is cheaper and
faster than building a drift-detection tool, so the tool is dropped.

### 5.1 THE ROOT CAUSE OF THREE FAILED BOAT TRIPS — measured S114

Ground truth read from the lab Pi (192.168.1.237) on 2026-07-31:

```
can0                UP, but NO NMEA 2000 devices on the bus
SK sources          defaults, freeboard-sk, signalk-rpi-monitor, kip, signalk-server
                    — no can0, no engine, no depth, no GPS
lsusb               no RTL-SDR dongle present
rtl-ais             activating (auto-restart), exit code 1 — crash-looping
```

**The lab Pi has no engine, no depth sounder, no AIS, and no GPS.**

Consequence, and this is the whole problem:

1. Any gauge / alarm / depth / AIS fix cannot be tested in the lab — no data source.
2. So it is marked "fixed in lab, on-boat validation required".
3. At the boat, the boat's own hardware is broken (CX5106 off the bus, Pangoo dead).
4. So it cannot be validated there either.
5. Nothing is ever proven. Confidence collapses. Repeat.

This consumed S101, S107 and S112. It is not a batch-order problem and not a
model-capability problem. **The lab has no way to produce test data.**

### 5.2 THE FIX — Signal K data simulator (LAB-SIM)

Inject synthetic Signal K deltas into the lab Pi. Everything downstream of
Signal K — which is where nearly every open bug lives — cannot distinguish
simulated data from the real boat.

**LAB-SIM must be able to drive:**

| Scenario | Validates |
|---|---|
| Boot with engine off, oil pressure 0 | BUG-45 (no false alarm) |
| Oil pressure → critical → hold → recover | BUG-42 (ack latch), BUG-44 (TTS fires) |
| Engine running: RPM, coolant, fuel, oil sweep | BUG-16, BUG-24, BUG-34 |
| Depth sweep 0.9 m → 3.8 m | BUG-30 |
| Throttle transition (SOG step change) | BUG-13 (flicker) |
| Stationary GPS, noisy heading | BUG-15 (COG flashing) |
| AIS targets appearing / moving | BUG-19, BUG-32 |
| Unit toggle Imperial ↔ Metric | BUG-43 |

**LAB-SIM is the highest-value item in this entire plan.** It converts roughly
20 "boat validation required" bugs into desk-testable bugs, and it is reusable
for every future release.

#### BUILT AND PROVEN WORKING — S114 2026-07-31

**Location:** `deployment/tools/lab-sim/` — `labsim.py` + `run.sh`

```
./run.sh list            # show scenarios
./run.sh cruise          # full healthy cruise, smoke-tests the rig
./run.sh oil-critical    # BUG-42 ack latch + BUG-44 voice alarm
PI=172.20.10.8 ./run.sh depth-sweep    # boat Pi, on the boat hotspot
```

**Scenarios:** `cruise`, `boot-engine-off` (BUG-45), `oil-critical` (BUG-42/44),
`oil-recover` (BUG-42 re-arm), `depth-sweep` (BUG-30), `throttle-step` (BUG-13),
`stationary-cog` (BUG-15), `units` (BUG-43), `clear`.

**Proven end-to-end on the lab Pi.** Injected and read back:
`revolutions 40.000 Hz` (= 2400 rpm), `oilPressure 289579.794 Pa` (= 42.0 psi),
`coolantTemperature 347.039 K` (= 165.0 °F), `fuel 0.620`, `voltage 13.800` —
all tagged `$source=LAB-SIM`.

**Two safety properties, both deliberate:**
1. **The script is NEVER installed on the Pi.** It lives in the repo on the
   workstation and is streamed into the Pi's `python3` over SSH stdin. Nothing is
   written to the Pi's disk, so it can never clone onto the boat card. A
   simulator that could start accidentally on a live vessel — injecting fake
   position and depth underway — is a genuine hazard.
2. **Every injected value carries `$source = "LAB-SIM"`**, so simulated data is
   always distinguishable from real sensor data in Signal K.

**Cost: $0 of Ollama, one Claude turn.** The originally-planned
spec → Ollama → review → correct → re-review loop was dropped: for a few hundred
lines, the review round trips cost more Claude tokens than writing it directly.
The Tier-3/Ollama split earns its keep on large code volume, not small utilities.
Also note: **`qwen3-coder:30b` named in CLAUDE.md is NOT installed** on
192.168.1.36. Actual models: `devstral:24b`, `gemma4`, `gemma4:31b-cloud`,
`llama3`, `deepseek-coder:6.7b`. CLAUDE.md needs correcting.

#### sksim — installed, but covers only 3 of 19 paths

`sksim` v1.9.2 was installed on the lab Pi at operator request and works
(registered, enabled, webapp present). Investigation of its source found:

- Its server plugin is a **dumb pipe** — `processUIPost` forwards `{path,value}`
  pairs to `server.handleMessage`. All generation happens in the browser webapp.
- The webapp emits: `propulsion.port.rpm`, `propulsion.port.temperature`,
  `environment.depth`, `environment.water`, `environment.wind`,
  `navigation.gnss`, `navigation.position`, `steering.rudderAngle`.
- **It does NOT emit oilPressure, coolantTemperature, fuel, battery, COG, SOG,
  trim, or AIS** — i.e. none of the alarm-critical paths.
- It emits `propulsion.port.rpm`, which is **not** the standard SK path the
  dashboard reads (`propulsion.port.revolutions`).

Against the 19 paths the dashboard actually consumes, sksim covers 3.

⚠ **CLONE HAZARD:** sksim is currently **enabled** on the master card. If cloned
to the boat it can be started from the SK Web Apps screen and will inject fake
navigation data on a live vessel.

**Recommendation: uninstall it.** LAB-SIM covers all 19 paths and carries no
clone risk. Rollback is prepared: `~/.signalk/package.json.pre-sksim.bak` exists
on the lab Pi; `npm uninstall sksim` + restart signalk reverses the install.
**AWAITING OPERATOR DECISION** — if kept, a mandatory pre-clone disable step must
be added to the Phase 2 clone procedure.

### 5.3 THE THREE PHASES

**PHASE 1 — LAB (no boat)**
1. Build LAB-SIM.
2. Fix every remaining lab-fixable bug.
3. Validate every fix against LAB-SIM scenarios. Record pass/fail here.
4. Nothing leaves the lab until its scenario passes.

**PHASE 2 — CLONE**
Clone the lab master SD card to the boat card. Boat Pi then equals lab Pi by
construction — BUG-28 (divergence) is closed physically, not by tooling.

⚠ **Known clone regressions — must be handled or the clone ships broken:**
- AvNav charts are wiped; the lab card holds only `osm-online.xml`
- The u-blox USB ignore rule is absent from the lab's `avnav_server.xml`
- BUG-39 identity sentinel clones with the card (installed DISABLED, so it will
  not fire) — identity must be regenerated on the clone
- Keep the boat's original card intact as the rollback

**PHASE 3 — ONE BOAT TRIP**
1. Hardware first: clip the CX5106 tach wire; identify and fix-or-remove the Pangoo.
2. Work the test card (Section 7) — one line per bug, pass/fail, signed.
3. Record results in the Progress Log before the session closes.

Only these need the boat, because only these need real hardware:
**BUG-14, BUG-31** (hardware), and final confirmation of **BUG-19/20/32** (needs
the RTL-SDR dongle, absent from the lab) and **BUG-25** (boat hotspot egress).

### 5.4 COST MODEL (operator constraint: keep cost low)

Per AAO §25 tier workflow and the Tier 3 hard cap of $30/month:

| Work | Who | Cost |
|---|---|---|
| Atomic specs, architecture, verification | Opus (Tier 1) | billed — keep turns few and targeted |
| Code generation, scripts, boilerplate | **Ollama `qwen3-coder:30b`, local GPU** | **$0** |
| Small mechanical edits | Direct edit, no AI | $0 |

**Rules for this project:** never use Claude to write code Ollama can write.
Never read `SESSION_LOG.md` (460 KB / ~115k tokens) — read this file instead.
Read only the specific `BUG-XX` entries needed, never the whole 126 KB bug file.

---

## 6. PROGRESS LOG

Append only. Never edit or delete a prior entry. Update **during** work, not at
session close.

Format:
```
### [YYYY-MM-DD] S### — Batch N — <status>
- Done: <what actually changed, with file paths>
- Verified: <how it was proven, with evidence>
- Not done: <what was skipped and why>
- Next: <the exact next action>
```

---

### [2026-07-31] S114 — BUG-43 TDD-VERIFIED (8/8) + TWO NEW BUGS FOUND
- Done: Browser deps resolved **without root** — `apt-get download` +
  `dpkg-deb -x` into `~/.local/pw-libs`, then
  `LD_LIBRARY_PATH=$HOME/.local/pw-libs/root/usr/lib/x86_64-linux-gnu`.
  (`sudo apt-get install` failed: no TTY for the password.)
- **Verified BUG-43 properly:**
  - RUN pre-fix, final test file: **7 failed / 1 passed.** Real assertion
    mismatches — coolant `Received "100°"` (expected `212°`), depth
    `Received "2.5"` (expected `8.2`), localStorage `Received null`.
    The 1 pass is the metric-depth reload test, which pre-fix was already metric.
  - RUN post-fix: **8 passed.**
  - Same test file both runs. This is genuine failing-first evidence.
- ⚠ **Test harness needs an SSH tunnel** until BUG-46 is fixed:
  `ssh -N -L 3000:localhost:3000 -L 8099:localhost:8099 d3kos@192.168.1.237`
  then `BASE_URL=http://localhost:3000 npx playwright test ...`
- **TWO NEW BUGS LOGGED** (log-before-fix rule observed; neither fixed):
  - **BUG-46 (HIGH)** — `SK_WS_URL` is hardcoded to `ws://localhost:8099`.
    Any browser other than the Pi's own gets **no live data at all**; every gauge
    stays `---`. Also in `boatlog-engine.js:15`. Very likely blocks the v0.9.4 PWA.
  - **BUG-47 (MEDIUM-HIGH)** — no handler for
    `propulsion.port.coolantTemperature`. The BUG-29 alias block covers
    revolutions/oilPressure/temperature/trimState but missed coolantTemperature,
    which is the path SK produces from N2K PGN 127489. The coolant gauge will
    still be dead after the CX5106 is restored unless this is fixed.
    Sixth instance of the BUG-29 defect class — reinforces the Batch 3 contract test.
- Corrected in LAB-SIM: it was publishing only
  `propulsion.port.coolantTemperature` (no handler). Now publishes both that and
  `propulsion.port.temperature`.
- Lab Pi left in the **FIXED** state (`_unitPrefs` ×7, dashboard 200).
- Not done: BUG-46/47 not fixed. No Ollama work started yet.

### [2026-07-31] S114 — sksim UNINSTALLED; BUG-43 Playwright test written (BLOCKED on browser deps)
- Done: **sksim uninstalled from the lab Pi** (operator-approved). Dependency
  list verified back to the original 7; `node_modules/sksim` removed; 11 plugins;
  signalk active; dashboard 200. **Clone hazard eliminated** — the master card no
  longer carries a simulator.
- Done: Wrote `tests/bug43-unit-persistence.spec.ts` — 8 Playwright tests
  asserting on **rendered DOM**, not source. Injects SK deltas from the browser
  (tagged `$source=PLAYWRIGHT-BUG43`). Covers: imperial default, saved imperial,
  saved metric, survives reload, **depth advisory still fires on raw metres while
  displaying feet**, **coolant advisory still fires on raw °C while displaying
  °F**, and both settings-page persistence directions. Selectors read from the
  live markup (`#cellCoolant .ic-v` / `.ic-u`), not guessed.
- ⚠ BLOCKED — TEST HAS NEVER VALIDLY RUN. All 8 tests error before reaching the
  page: Chromium cannot launch in WSL.
  `libnspr4.so / libnss3.so / libnssutil3.so / libasound.so.2: not found`.
  The failing run is therefore **NOT** evidence the test detects the bug.
- Fix required (needs root; no passwordless sudo on this workstation):
  `sudo apt-get install -y libnspr4 libnss3 libasound2t64`   (Ubuntu 24.04 noble)
- The pre-fix revert used to attempt a failing-first run was **fully restored**:
  lab Pi serves `_unitPrefs` ×7, `/` returns 200.
- Next: install the 4 libs → run failing-first proof (revert to
  `*.pre-bug43.bak`, expect FAIL) → restore fix → expect PASS. Only then is
  BUG-43 closeable.

### [2026-07-31] S114 — BUG-43 IMPLEMENTED + DEPLOYED TO LAB PI
- Done: Applied `S112-BUG-43-settings-unit-persistence.md` in full (Steps 1–7).
  Files: `deployment/v0.9.9.4/.../static/js/instruments.js` (+`_unitPrefs`,
  `_init()` localStorage load, coolant °F branch, `_renderDepth` ft branch) and
  `.../templates/settings.html` (button wired, `saveDisplaySettings()` added).
  44 insertions / 12 deletions, 2 files. Deployed to lab Pi + dashboard restarted.
- Verified: All 6 spec prerequisites matched before editing. `node --check` OK.
  All 15 Step-8 checklist items PASS. Thresholds still evaluate raw SI
  (`_evalAbove(c,…)`, `_evalBelow(v,…)`); `_d3kEngData.coolant_c` still °C and
  `.depth_m` still metres. Served files confirm `_unitPrefs` ×7 and
  `saveDisplaySettings` ×2. `/` and `/settings` both 200.
  LAB-SIM `units` injected 373.15 K and 3.048 m; conversion math yields
  212 °F / 10.0 ft.
- ⚠ NOT VERIFIED: the rendered DOM. Arithmetic and served source are confirmed;
  **no browser has actually displayed the values.** Playwright 1.61.1 IS
  installed with existing BUG-27 tests — a DOM test must be written before
  BUG-43 can be called done.
- ⚠ TDD DEVIATION: the standards require a failing test FIRST. That was not done
  here — the spec's literal code was applied, then verified. Reported, not hidden.
- Rollback: `~/.../instruments.js.pre-bug43.bak` and `settings.html.pre-bug43.bak`
  on the lab Pi; `git checkout` the two repo files.
- Next: Playwright DOM test for BUG-43, then Tier 1 specs for the un-specced
  bugs (08, 09, 16, 18, 19, 20, 24, 23a) → Ollama `devstral:24b` as Tier 3.

### [2026-07-31] S114 — LAB-SIM BUILT AND PROVEN
- Done: Installed `sksim` v1.9.2 on the lab Pi (operator-approved). Investigated
  its source: covers only 3 of the 19 paths the dashboard consumes, no
  oil/fuel/battery/COG/AIS. Built LAB-SIM instead —
  `deployment/tools/lab-sim/labsim.py` + `run.sh`, 9 scenarios mapped to
  BUG-13/15/30/42/43/44/45.
- Verified: End-to-end injection proven. Read back from SK:
  `revolutions 40.000 Hz` (2400 rpm), `oilPressure 289579.794 Pa` (42.0 psi),
  `coolantTemperature 347.039 K` (165.0 °F), `fuel 0.620`, `voltage 13.800`,
  all `$source=LAB-SIM`. Unit conversions confirmed correct.
- Design: script never lands on the Pi's disk (streamed over SSH stdin) so it
  cannot clone to the boat card. All values tagged `$source=LAB-SIM`.
- Corrected: dropped the Ollama route for this tool — spec+review round trips
  cost more Claude tokens than writing 300 lines directly. `qwen3-coder:30b`
  named in CLAUDE.md is NOT installed; actual coder model is `devstral:24b`.
- Not done: no bug fixed yet. sksim uninstall decision pending with operator.
- Next: atomic specs → Ollama (devstral:24b) as Tier 3 implementer, starting
  with BUG-43 (spec already exists, and LAB-SIM `units` scenario tests it).

### [2026-07-31] S114 — Ground truth established; plan restructured to operator model
- Done: Read the lab Pi live (192.168.1.237). Confirmed 10 fixes present in the
  actually-served files (see 3.1). Confirmed BUG-23a real: voice watchdog fails
  with "Only 1 thread(s) running (expected 2+)", restart does not recover.
  Located `forward-watch` config at
  `/home/d3kos/.signalk/plugin-config-data/signalk-forward-watch.json`.
- Verified: **Root cause of three failed boat trips identified and measured** —
  the lab Pi has no N2K devices on can0, no RTL-SDR dongle, no engine, no depth,
  no GPS. Fixes therefore could never be validated in the lab, deferred to the
  boat, where the boat's own hardware was broken. Nothing could be proven in
  either location. Documented in 5.1.
- Decisions: Operator directive adopted — fix all in lab → clone → one boat trip.
  Drift-detection tool DROPPED (cloning solves it physically). LAB-SIM adopted as
  the key enabler. BUG-11 and BUG-23b moved to v0.9.9.5 (operator approved).
  Boat Pi is unreachable from the lab network (boat hotspot only) — confirmed.
- Corrected: real remaining lab work is **8 items**, not 39 (see 3.2).
- Not done: LAB-SIM not built. No bug fixed this session. Test card not written.
- Next: build LAB-SIM via Ollama ($0), then work the 8 remaining lab items.

### [2026-07-31] S114 — Plan created
- Done: This file created. All 39 bugs read from `V09994_BUG_FIXES.md` and
  grouped into 7 dependency-ordered batches plus a removal proposal.
- Verified: Bug statuses and counts read directly from the source file
  (7 closed / 21 in-progress / 11 open = 39). Cross-checked the S112 cruise
  report against the "NOT on the boat Pi" annotations — contradiction found and
  documented in META-A.
- Not done: No code changed. No bug fixed. No batch started.
- Next: Operator decision on batch order and on the BUG-11 / BUG-23 removal
  proposal, then begin Batch 1.
