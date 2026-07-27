# v0.9.9.4 — On-Boat Analysis Plan & Confirmed Expectations

**Version:** 1.1.0 | **Created:** 2026-07-24 S106 | **Updated:** 2026-07-27 S107 | **Status:** **PHASE A EXECUTED** — evidence gathered on-boat; Phase B (lab) ready

> ## PHASE A RESULTS — 2026-07-27 (S107)
>
> Executed on the boat Pi (`172.20.10.8`), engine running, Garmin connected mid-session by the
> operator. Full evidence in `V09994_BUG_FIXES.md` BUG-28…BUG-34 and `SESSION_LOG.md` S107.
> **No fix was written or deployed** — Phase A discipline held.
>
> **Two code defects explain four bugs:**
> - **BUG-29** — dashboard subscribes `propulsion.0.*`; Signal K publishes `propulsion.port.*`
>   (`propulsion` keys = `['port']`). Cascades into **BUG-16** (`_d3kEngData` permanently null →
>   Gemini receives "fuel 0%" for every gauge = the E2 violation) and **BUG-24** (`rpmHz > 3` never
>   true). Blast radius 6 live files. **Present in the latest source — a redeploy will not fix it.**
> - **BUG-30** — depth gauge reads `belowKeel`; Signal K publishes `belowTransducer`.
>
> **§3 expectations — both confirmed:**
> - **E1 CONFIRMED.** Garmin depth IS live: `environment.depth.belowTransducer` = 0.99 m,
>   `$source: can0.0`, PGN 128267. The "no depth sounder present" candidate is definitively dead.
> - **E2 CONFIRMED as violated,** with the mechanism now known (BUG-29 + BUG-34).
>
> **§5 confound RESOLVED differently than expected:** o-charts SENC data IS installed
> (`oeuSENC-CAac-2026-1-1-base-avnav`, `oeuSENC-CAgl-2026-1-1-base-avnav`) — the blank chart is a
> licence/expiry issue, not missing chart data. **But BUG-19/BUG-20 still could not be judged**, for a
> new reason: **BUG-32** — AIS never reaches Signal K at all (rtl_ais pushes to TCP 10110, which
> Signal K itself occupies as its NMEA0183 *output*; 20 s listen = 0 AIVDM; `ais` provider
> `enabled:false`). Fix BUG-32 **before** evaluating the overlays.
>
> **§6 prerequisites:**
> - **P1 — RESOLVED** (S106-cont: manuals converted). S107 adds that BUG-34's thresholds are generic
>   JS literals that contradict those sourced values (idle oil ≥4 psi vs `crit:20` → false alarms;
>   battery has no upper bound → 15.5 V overcharge reads "Normal").
> - **P2 — still AWAITING OPERATOR.** BUG-22 confirmed NOT a bug (gate works as designed); the
>   fresh-user vs re-triggerable question is unanswered.
> - **P3 — superseded.** Chart data is present; the licence is the issue, and BUG-32 now blocks first.
> - **P4 — partially resolved.** BUG-19's real blocker is BUG-32, not subscription. BUG-21 is partly a
>   **config** defect (`audio_alarm:false`, `detection_interval:300` = 5 min), not purely "never built".
>
> **Also closed as NOT bugs:** BUG-25 (live Gemini query succeeded on the boat, `tokens:290`) and
> BUG-22. **BUG-23's S105 diagnosis corrected** (watchdog `inactive/dead` is normal — `.timer` is
> active; STT is Vosk, not Faster-Whisper).
>
> **New Phase A blocker not anticipated by this plan:** **BUG-28** — the boat Pi runs **v0.9.2.2**
> (build 2026-03-23) and never received the S96/S105 fixes, so BUG-15/26/27 are *not* fixed on the
> boat. Cause: `deployment/v0.9.4/pi_source/` froze 2026-04-08 while `deployment/d3kOS/dashboard/`
> advanced to 2026-07-23 — the two-source-sync rule is violated. **Any future Phase C deploy must
> verify which tree it is shipping and stamp the version.**
>
> **Still requires the operator:** identify **src 64** physically (real device, serial
> `N20210700100`, sending frozen engine data + false 0% fuel on a confirmed-full tank); confirm the
> actual tank capacity; confirm the **lab Pi version** on return (lab Pi unreachable from the boat).
**Companion to:** `V09994_BUG_FIXES.md` (holistic bug tracker) + `PROJECT_CHECKLIST.md` PART 17
**Author model:** Tier 1 (Opus) — requirements + investigation plan only. No fix implemented in this document.

---

## 1. Why this document exists

This records the S106 conversation and turns it into an executable plan. The operator's
direction was explicit:

> "things are not working to expectation… expectation needs to be understood… this is not
> an exercise to do it your way. we need to fix the problems."

The correction taken from that: **the expected behavior is the fixed target and is sourced
from the operator and the boat's documentation — not inferred by Claude.** Root-cause
investigation happens on the boat; the fix is developed and tested in the lab.

This document does NOT attempt any fix. It defines (a) what "working" means for each open
bug, and (b) exactly what to look at on the boat to find the real root cause.

---

## 2. Three-phase workflow (agreed S106)

```
PHASE A — BOAT (investigate)      PHASE B — LAB (fix)              PHASE C — BOAT (deploy)
- Pi reachable at 172.20.10.8     - Opus authors atomic spec       - Deploy fix to Pi
  (boat hotspot only)               with expectation = acceptance   - Operator approval REQUIRED
- Gather evidence against          - Haiku (Tier 3) implements        (High risk, per CLAUDE.md)
  each confirmed expectation      - Opus verifies (§25.8)          - Operator confirms against
- Capture data for the lab        - Tested against local source      the expectation on-screen
- NO fixes on the boat                                             - Release Package Manifest
```

**Hard constraint:** off-boat, the Pi is unreachable (`ssh 172.20.10.8` → "Network is
unreachable"). All Phase A checks below can only run when the operator is on the boat and the
Pi is on the hotspot network. Nothing deploys without explicit operator approval in that session.

---

## 3. Operator-confirmed expectations (authoritative — corrects the bug tracker)

| # | Confirmed by operator S106 | Effect on bug record |
|---|----------------------------|----------------------|
| E1 | **Depth comes from the Garmin unit via NMEA 2000** and must display live on the dashboard depth gauge. | BUG-18: the "no depth sounder present" candidate is **WRONG** and is removed. The sounder (Garmin) exists on the N2K bus. Problem = Garmin depth is not reaching the gauge. |
| E2 | **Pressing any gauge must show that specific gauge's live value AND its normal range / meaning based on THIS boat's documentation**, then advise on the actual reading. Identical generic text on every gauge = broken. | BUG-16: acceptance criteria now explicit. Requires the boat's documented tolerances as a data source (see §6 open prerequisite). |

---

## 4. Expectations + on-boat analysis plan (by tier)

Legend for each bug block:
- **Expected** = acceptance criteria ("fixed" means this is true)
- **Don observes** = what to look at on the Pi touchscreen / at the helm
- **Claude checks (Pi/SSH)** = diagnostics Claude runs when the Pi is reachable on the boat
- **Candidates** = root causes to confirm or rule out
- **Capture for lab** = the evidence to bring back so the fix can be built off-boat

> N2K PGNs and Signal K paths below are NMEA 2000 / Signal K **standards** (not boat-specific
> claims). Exact paths are confirmed against live Signal K during Phase A before any fix.

---

### TIER 1 — Safety-critical

#### BUG-18 — Depth gauge (Garmin → N2K → gauge)
- **Expected:** Garmin depth shows live on the dashboard depth gauge, in the operator's units.
- **Don observes:** Depth gauge on dashboard — blank / `---` or a value? Does Garmin's own display show a depth at the same moment?
- **Claude checks (Pi/SSH):**
  - Signal K depth paths: `curl -s localhost:8099/signalk/v1/api/vessels/self/environment/depth` — is `belowTransducer` / `belowKeel` / `belowSurface` present and updating?
  - Is PGN 128267 (Water Depth) arriving on the N2K bus at all? (Signal K data browser / CAN capture)
  - Which depth path does the dashboard gauge read? (lab: dashboard JS source)
- **Candidates:** (1) Garmin not transmitting 128267; (2) SK receiving but under a path the gauge doesn't read; (3) gauge display bug / wrong path binding.
- **Capture for lab:** the exact SK depth path + a sample value; the dashboard gauge's current source binding.

#### BUG-16 — Gauge tap shows gauge-specific live data + boat-documented tolerance
- **Expected (E2):** tap any gauge → live Signal K value for THAT gauge + its normal range from the boat's documentation + advice based on the actual reading. Never the same generic message on all gauges.
- **Don observes:** tap fuel, oil, RPM, battery, coolant one at a time — is the dialog identical for all? Does it reflect the live value?
- **Claude checks (Pi/SSH):** confirm live values exist in SK per gauge; (lab) inspect `overlays.js` `showCrit()` / `openDiag()` and the tier gate.
- **Candidates:** (1) `showCrit()` hardcoded string; (2) `openDiag()` silent fallback when `_d3kEngData` cache empty; (3) tier gate shows upgrade screen instead of data; (4) no tolerance data source wired.
- **Capture for lab:** which gauges have live SK data vs. none; the boat's documented normal ranges (see §6).

#### BUG-21 — Audible + visual hazard warning
- **Expected:** camera detects a hazard (kayak, log, swimmer, duck, goose) → audible **and** visual alert at the helm in real time.
- **Don observes:** with a known hazard in frame — any sound? any on-screen alert?
- **Claude checks (Pi/SSH):** is signalk-forward-watch publishing detections to SK? is any alert/notification consumer wired to audio (Piper/ALSA) and to the dashboard?
- **Candidates:** detection→alert pipeline never wired end-to-end (build, not just fix).
- **Capture for lab:** does a detection reach SK? what notification path exists today?

#### BUG-20 — Camera hazards on the AvNav chart
- **Expected:** camera-detected hazards appear as markers/overlays on the AvNav chart.
- **Don observes:** any markers on AvNav when hazards are present?
- **Claude checks (Pi/SSH):** are detections forwarded to AvNav via `AVNSignalKHandler` (:8099)? is an AvNav overlay layer defined for them?
- **⚠ Confound:** see §5 — AvNav charts are currently **blank** (o-charts license expired 2026-04-01). Markers cannot be judged on a blank chart. Renew charts (OB-O05) **before** concluding this overlay is broken.
- **Capture for lab:** whether detections reach AvNav at all vs. whether only the chart base is missing.

#### BUG-19 — AIS targets on the AvNav chart
- **Expected:** AIS-transmitting vessels appear as target symbols on the AvNav chart.
- **Don observes:** with AIS vessels known in range — any symbols on AvNav?
- **Claude checks (Pi/SSH):** AIS confirmed in SK (BUG-12 fix — `ais` provider enabled, rtl_ais on TCP 10110). Confirm SK has live `vessels.*` AIS targets; confirm AvNav is subscribed to the SK AIS feed.
- **⚠ Confound:** same blank-chart issue as BUG-20 — renew o-charts first.
- **Candidates:** (1) blank chart hides symbols; (2) AvNav not subscribed to AIS; (3) no AIS vessels were actually in range during the test.
- **Capture for lab:** live SK AIS target count + timestamps during the observation window.

---

### TIER 2 — Core data / hardware root cause

#### BUG-14 — CX5106 engine data on N2K (ROOT-CAUSE BLOCKER for 17, 24)
- **Expected:** CX5106 transmits engine data (RPM via PGN 127488, dynamic via 127489) onto the N2K bus → SK → dashboard gauges show live engine values.
- **Don observes / physical:** the tach signal wire must be connected (per S101: blue wire, Pole 3 of RPM gauge — Monterey non-standard). Field procedure: `CX5106_WIRE_ID_FIELD_PROCEDURE.md`.
- **Claude checks (Pi/SSH):** CX5106 on bus (src=106, heartbeat 126993); with engine running + tach wire connected, are 127488/127489 arriving continuously?
- **Candidates:** tach signal not stable → CX5106 does not broadcast continuously (confirmed intermittent S101).
- **Capture for lab:** whether engine PGNs stream once the tach wire is stable (this is physical, not code).

#### BUG-17 — Battery / alternator voltage
- **Expected:** battery/alternator voltage shows live on the dashboard.
- **Claude checks (Pi/SSH):** `curl localhost:8099/signalk/v1/api/vessels/self/electrical` — any data? Two possible sources: **Garmin PGN 127508 (Battery Status)** or **CX5106 PGN 127489**.
- **Candidates:** (1) no source transmitting battery data; (2) CX5106 path blocked by BUG-14; (3) Garmin could supply it independently of CX5106 — check first.
- **Capture for lab:** which device (if any) puts battery data on the bus; the SK electrical path.

#### BUG-24 — Boat Log engine auto-capture
- **Expected:** engine runs 30+ min → an ENGINE entry appears automatically in the Boat Log.
- **Candidates:** likely gated on live RPM (BUG-14). Also confirm the auto-capture service is running and its RPM threshold.
- **Capture for lab:** does RPM reach SK (post BUG-14)? is the capture service running? what threshold fires it?
- **Dependency:** retest only after BUG-14 produces stable RPM.

#### BUG-13 — Speed gauge flicker
- **Expected:** speed gauge settles cleanly on the actual speed; no oscillation between old/new during throttle changes; the long-press options panel must not obscure the readout.
- **Don observes:** change throttle — does it snap back and oscillate? long-press — does the panel cover the number?
- **Claude checks (Pi/SSH):** (lab) speed handler in dashboard JS — likely needs the same debounce/gate approach used for BUG-15 (COG at low SOG).
- **Capture for lab:** the SOG handler code + the long-press panel layout (this one is largely code-fixable in the lab).

---

### TIER 3 — Feature broken (non-safety)

#### BUG-25 — AI Navigation cannot connect on boat
- **Expected:** AI Navigation connects and returns answers **on the boat**.
- **Diagnosed S105:** likely **internet egress**, not d3kOS — both Gemini services up, model `gemini-2.5-flash-lite` correct, key present, `:3001/status` online. Bad model only in `.bak`.
- **Don observes:** does the boat hotspot actually have working upstream internet (open a website on the phone)?
- **Claude checks (Pi/SSH):** `curl -sS -o /dev/null -w '%{http_code}' https://www.google.com` from the Pi — `000` = no egress.
- **Candidates:** boat hotspot has no/weak upstream internet. If egress works and it still fails → escalate to a real service bug.
- **Capture for lab:** egress result + which service errors (if any).

#### BUG-22 — Setup wizard bypassed on fresh load
- **Expected:** on a fresh/first-run load the Setup Wizard appears (Step 1 of 6) rather than going straight to the dashboard.
- **Known (memory):** the wizard gate is a **server-side file** `/opt/d3kos/config/vessel.env`, NOT a browser cookie — clearing cookies does nothing. Wizard shows only at genuine fresh install.
- **⚠ Expectation to confirm:** is the concern (a) a brand-new user won't get the wizard, or (b) you want to be able to re-trigger it on an already-configured Pi? These need different fixes. **Confirm with operator.**
- **Claude checks (Pi/SSH):** does `vessel.env` exist and what's in it? what condition does the dashboard entry point test?
- **Capture for lab:** the entry-point redirect logic + vessel.env state.

#### BUG-23 — Boat Log voice transcription
- **Expected:** record a voice note → transcribed entry appears in the Boat Log list.
- **Diagnosed S105:** `d3kos-voice-watchdog` FAILED (1 thread, expected 2+); no local STT/whisper service found — may be a feature gap (Faster-Whisper STT is a v0.9.9.5 item, possibly not built).
- **Claude checks (Pi/SSH):** watchdog thread state (find the 1-thread cause — do NOT blind-restart); is any STT service present; does the voice-note POST to `/api/boatlog/voice-note` succeed; does the DB row get written?
- **Candidates:** (1) STT not built (feature gap); (2) POST failing; (3) row written but not rendering.
- **Capture for lab:** watchdog root cause + whether STT exists at all (determines fix vs. build).

#### BUG-08 — Helm on-screen keyboard
- **Expected:** the helm keyboard appears, stays visible, and typed text enters the field.
- **Root cause identified:** `keyboard-fix.js` v2.1 — `el.blur()` fires a previous tap's `{once:true}` hideKeyboard listener before `_recentlyShown` is set → flash.
- **Don observes:** first tap on a fresh page vs. second tap — does the flash differ?
- **Claude checks (Pi/SSH):** keyboard API log for show→hide same-second pattern; (lab) rewrite to remove `el.blur()` and re-register `zwp_text_input_v3` via `requestAnimationFrame`.
- **Capture for lab:** first-tap vs. second-tap behavior; the log timing.

---

### TIER 4 — Research / design (design phase before any implementation)

#### BUG-09 — Power-loss self-healing
- **Expected:** after an unclean power loss the Pi boots clean — no AvNav/config/DB corruption.
- **Phase A role:** if a corruption event is observed, capture the exact failure (which files, which service, journal errors) — this feeds the R1–R5 research in the bug record.
- **Note:** implementation is blocked on design; not a Haiku task yet.

#### BUG-11 — Universal device health (AIS/GPS/mic/speaker)
- **Expected:** any connected AIS/GPS/mic/speaker is verified working with a health indicator, and the operator is notified when one fails — model-agnostic.
- **Phase A role:** capture current SK provider config + ALSA enumeration (`arecord -l`, `aplay -l`) as the baseline the generic framework hooks into.
- **Note:** design-first; not a Haiku task yet.

---

## 5. Cross-cutting confound — expired o-charts license (affects BUG-19, BUG-20)

Per memory (S96): CAac + CAgl o-charts licenses **expired 2026-04-01**; AvNav shows **blank**.
AIS symbols (BUG-19) and hazard markers (BUG-20) are drawn **on top of** the chart. On a blank
chart you cannot tell "overlay broken" from "chart base missing."

**Order of operations on the boat:** renew o-charts (OB-O05) and confirm the chart base renders
**first** — then re-evaluate BUG-19 and BUG-20. Do not conclude those overlays are broken while
the chart is blank.

---

## 6. Open prerequisites to resolve

| # | Prerequisite | For | Status |
|---|--------------|-----|--------|
| P1 | **Is the boat's engine/vessel documentation (Monterey 265 / Mercruiser normal ranges) already uploaded to d3kOS, or must it be sourced?** Without documented tolerances, BUG-16's "advise on the reading" cannot be built. | BUG-16 | **AWAITING OPERATOR** |
| P2 | BUG-22 expectation: fresh-user wizard vs. re-triggerable wizard on a configured Pi? | BUG-22 | **AWAITING OPERATOR** |
| P3 | Renew o-charts license (OB-O05) before judging AvNav overlays. | BUG-19, BUG-20 | Operator task |
| P4 | Confirm the inferred `[INFERRED]` expectations in §3 conversation table (21/20/19) match operator intent. | Tier 1 | **AWAITING OPERATOR** |

---

## 7. Next actions

1. **Operator:** answer P1, P2, P4 (can be done off-boat, any time).
2. **On the boat (Phase A):** Claude runs the per-bug Pi/SSH checks above; Don makes the touchscreen observations. Evidence captured per "Capture for lab."
3. **Lab (Phase B):** each confirmed root cause → atomic spec (expectation = acceptance criteria) → Haiku implements → Opus verifies.
4. **Boat (Phase C):** deploy with operator approval + Release Package Manifest; operator confirms against the expectation.

**No fix is written or deployed until Phase A evidence exists for that bug.**
