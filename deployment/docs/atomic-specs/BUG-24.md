# ATOMIC SPEC — BUG-24

**Defect:** Boat Log engine auto-capture never fires. The logic works; it is loaded on the wrong page.
**Severity:** MEDIUM — a feature that silently does nothing.
**Tier:** ⚠ **Requires an operator design decision before any implementation.** §2 presents three options.
**Created:** 2026-08-24 (S131)
**Bug record:** `V09994_BUG_FIXES.md` BUG-24 (re-diagnosed S116; original hypothesis disproved)

---

## 1. VERIFIED ROOT CAUSE — confirmed S131

`boatlog-engine.js` is referenced by exactly **one** template:

```
deployment/v0.9.9.4/opt/d3kos/services/dashboard/templates/boat-log.html   <- the only loader
```

(The other two matches are `MANIFEST.md5` and `verify-bug29.sh`, neither a loader.)

The capture logic itself is sound — read S131 from the file:

```js
line 18:  var RPM_THRESHOLD_HZ = 3;              /* 3 Hz = 180 RPM — engine considered running */
line 93:  function _checkEngineState(rpmHz) {
line 94:    var isRunning = rpmHz > RPM_THRESHOLD_HZ;
```

**So auto-capture only runs while the operator is looking at the Boat Log page.** In normal use the helm
displays the dashboard, so the engine starts, runs and stops with nothing watching. The S116
re-diagnosis was correct: *"the logic WORKS; root cause is architectural."*

⚠ **The original hypothesis was disproved.** Do not re-diagnose the threshold or the RPM path — both are
correct. The defect is *where the code lives*.

---

## 2. THE DECISION — this is why the spec stops here

Client-side capture cannot work. A browser tab is not a reliable place to run a background task on a
vessel: the page may not be open, Chromium may be showing AvNav, the screen may be asleep, and the
browser may be restarted by the launcher. **Any fix that keeps this in the browser is a fix that works
only when someone is watching, which is the bug.**

Three options. Each has a different cost and a different failure mode.

### Option A — server-side capture service (recommended)
A small Python service subscribes to Signal K server-side and writes Boat Log entries directly.

- **Pros:** always running; survives browser restarts and screen sleep; the same pattern as
  `alert_watcher.py`, which already does exactly this shape of job. Testable with LAB-SIM, no browser.
- **Cons:** a new systemd unit on a Pi that already runs ~40. Duplicates threshold logic unless the JS
  path is retired.
- **Precedent to follow:** `alert_watcher.py` — *"monitors alerts, triggers immediate export on event."*
  Same trigger-on-state-change shape. **Diff against it rather than designing fresh.**
- ⚠ **Must use `Environment=PYTHONUNBUFFERED=1`** in the unit if it uses `print()`. BUG-54's five months
  of invisible failures were caused by exactly that omission — systemd block-buffers stdout at 8 KB.

### Option B — move the JS to the always-loaded page
Load `boatlog-engine.js` from `index.html` (the dashboard) instead of `boat-log.html`.

- **Pros:** a one-line template change; no new service.
- **Cons:** still dead whenever the browser shows AvNav, charts, or is restarted. **It converts "never
  captures" into "captures sometimes", which is harder to diagnose than a clean failure.**
- **Assessment:** looks like the cheap win and is the trap. Not recommended.

### Option C — Node-RED flow
- **Cons:** Node-RED is documented as **disabled until Phase 4** and its only `flows.json` sits in the
  v0.9.2 tree. Adopting it here means owning that whole dependency.
- **Assessment:** not now.

**CLARIFICATION REQUIRED — do not proceed without an answer:**
> Option A (new server-side service), B (move the JS), or C (Node-RED)?
> **Recommendation: A**, modelled on `alert_watcher.py`.

The remainder of this spec assumes A and must be revised if you choose otherwise.

---

## 3. IF OPTION A — implementation shape

| Item | Value |
|---|---|
| Service | `d3kos-boatlog-capture.service` |
| Code | `opt/d3kos/services/boatlog/boatlog_capture.py` |
| Input | Signal K WS, `propulsion.port.revolutions` |
| Threshold | **reuse `RPM_THRESHOLD_HZ = 3`** — import or share, do not retype the constant |
| Output | the existing Boat Log API (`d3kos-boatlog-api`), **not** a direct file write |
| Unit | `Environment=PYTHONUNBUFFERED=1` |

**Required behaviour:**

1. **Debounce the transition.** Capture on a sustained state change, not on the first delta above
   threshold. Raw SK deltas are noisy — BUG-13 (speed flicker) and BUG-15 (COG flashing) are both that
   noise, and BUG-13's fix was a 250 ms coalesce timer. **Reuse that lesson: require the state to hold
   before logging.** Otherwise one noisy sample creates a spurious ENGINE entry.
2. **Log start and stop as one session,** with duration — the operator wants engine hours, not two
   disconnected events.
3. **Ignore `$source = LAB-SIM` in production?** **No — and this is deliberate.** LAB-SIM data must flow
   through so the feature is testable. Every injected value is already tagged `$source=LAB-SIM`, and the
   simulator never lands on the Pi's disk, so it cannot run on a vessel by accident.
4. **Survive Signal K restarts** — reconnect with backoff, never exit.
5. **Do not write a duplicate entry** if the JS path also fires. **Retire the JS auto-capture in the same
   change** — two writers is worse than none.

---

## 4. TESTS — LAB-SIM makes this desk-testable

| # | Scenario | Expect |
|---|---|---|
| T1 | `run.sh cruise` — RPM rises above threshold and holds | one ENGINE start entry |
| T2 | RPM returns to 0 and holds | matching stop entry, with duration |
| **T3** | **RPM oscillates across the threshold rapidly (throttle-step scenario)** | **exactly one session, not many** — the debounce test |
| T4 | Dashboard open, Boat Log page never opened | entry still created — **the regression test for this bug** |
| T5 | Browser closed entirely | entry still created |
| T6 | Signal K restarted mid-session | service reconnects; no crash; session closed or resumed coherently |
| T7 | JS path retired | exactly one entry per session, no duplicates |
| T8 | Service `print()` output visible in the journal within 1 s | proves `PYTHONUNBUFFERED=1` (BUG-54 guard) |

**T4 is the test that proves BUG-24 is fixed.** T3 is the one most likely to fail on a first attempt.

---

## 5. DEFINITION OF DONE

- [ ] Operator has chosen A, B or C — **spec not implementable before that**
- [ ] T4 passes with the Boat Log page never opened
- [ ] T3 passes — no spurious sessions from threshold noise
- [ ] JS auto-capture retired; T7 confirms no duplicates
- [ ] `PYTHONUNBUFFERED=1` present and proven by T8
- [ ] Threshold constant shared, not duplicated
- [ ] BUG-24 entry updated with the chosen option and the reason

## 6. WHAT THIS DOES NOT FIX

- **BUG-23b** — voice transcription. There is no STT engine installed; moved to v0.9.9.5. Unrelated.
- **Engine-hours accuracy.** This logs sessions from RPM. Whether that is the authoritative hour meter is
  a separate question — the CX5106 may report engine hours directly (PGN 127489 family). **Do not conflate
  the two; if hours are wanted from the bus, log it as a new item.**
