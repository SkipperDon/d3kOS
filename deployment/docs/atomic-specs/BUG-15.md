# Atomic Spec — BUG-15 (COG heading flashes when stationary)

**Format:** AAO §23.5 / §25 escalation-enabled. Created 2026-07-23 by Tier 1 (Opus).
**Tracker:** `deployment/docs/V09994_BUG_FIXES.md` BUG-15.

## Tier-1 finding (verified in repo)
COG is rendered by the handler at `static/js/instruments.js:132`
(`'navigation.courseOverGroundTrue'`) → writes `#cellCourse`. SOG is handled at
`:123` (`'navigation.speedOverGround'`, value `v` in m/s → kts = v×1.944). When the
boat is stationary (SOG≈0), GPS COG is noise, so the value jumps every update →
visible flashing. Fix: gate COG updates below a low SOG threshold, holding the last
displayed value. Threshold **0.5 kn** matches the existing precedent at `:353`
(`if (sog > 0.5)`), so it is not an invented number.

---

## SPEC (paste this block to the Tier 3 model)

```
🔧 ATOMIC SPEC — BUG-15  (AAO §23.5 · §25 escalation-enabled)
═══════════════════════════════════════════════════════════════════════
TASK TYPE : [IMPLEMENT] — Tier 3
BUG       : BUG-15 — COG (course over ground) flashes/oscillates on the
            dashboard when the boat is stationary (SOG near 0).

CONTEXT (read ONLY this file)
  static/js/instruments.js
  (in the dashboard dir: deployment/d3kOS/dashboard/static/js/instruments.js)

ROOT CAUSE
  The COG handler updates #cellCourse on every navigation.courseOverGroundTrue
  delta. At SOG≈0, GPS COG is meaningless noise that jumps each update → flashing.

CHANGE (three small edits, this file only)
  1. Add a module-level state var next to the other shared vars (~line 120,
     beside `let _gpsLat = null, _gpsLon = null;`):
        let _lastSogKts = null;
  2. In the SOG handler ('navigation.speedOverGround', ~line 123), after computing
     `kts`, store it:
        _lastSogKts = parseFloat(kts);
  3. In the COG handler ('navigation.courseOverGroundTrue', ~line 132), add a guard
     as the FIRST statement — hold the last displayed value when SOG is below
     threshold:
        if (_lastSogKts !== null && _lastSogKts < 0.5) return;
     (0.5 kn matches the existing precedent at ~line 353.)
  4. TEST SEAM (Tier-1 approved 2026-07-23 in response to escalation): immediately
     after the SK_HANDLERS const definition, expose it once for testing:
        window.SK_HANDLERS = SK_HANDLERS;   // test seam — harmless reference
     This is intentional and production-safe (a reference to an existing object).

BEHAVIOR CONTRACT
  • SOG < 0.5 kn (and known): COG display (#cellCourse) does NOT change — the last
    value is held. Do NOT blank it, do NOT show a placeholder.
  • SOG >= 0.5 kn: COG updates live as before.
  • SOG unknown (null, no delta yet): COG updates (do not suppress on unknown).

CONSTRAINT BOUNDARIES (do NOT)
  • Do NOT change the SOG display, units, position-report text, or any other handler.
  • Do NOT alter the COG radian→degree math or #cellCourse formatting.
  • Do NOT touch any file other than instruments.js.
  • Do NOT add smoothing/averaging — the fix is a threshold gate only.

FAILING TEST FIRST (TDD — must fail before the fix)
  Write a test that drives the two Signal K handlers and asserts #cellCourse:
    Scenario A (stationary): feed SOG=0, then COG=10°,200°,45° in sequence →
      assert #cellCourse text is UNCHANGED across the three COG updates.
    Scenario B (moving):     feed SOG≈3 kn (m/s ~1.54), then COG=90° →
      assert #cellCourse shows "90°".
  Drive the handlers however the app exposes them (WebSocket feed simulation, or
  by invoking SK_HANDLERS[path](value) if reachable). Screenshot on failure.

DONE WHEN
  • Test fails before the edit, passes after.
  • git diff shows ONLY the four additions above in instruments.js (3 fix + 1 test seam) — nothing else.

ESCALATE-IF (emit the 🔺 ESCALATION block — do NOT guess)
  • SK_HANDLERS / the SOG+COG feed cannot be driven from a test (not exposed,
    no simulation hook)        → SOLUTION-REQUEST (Tier 1 will provide a test hook)
  • The COG handler is not at the described location or has a different shape
                               → CLARIFICATION
  • SOG value is not in a form you can convert to knots reliably
                               → CLARIFICATION
  • The fix seems to need a file other than instruments.js
                               → ADVICE (scope)
  (§25.5.1: if an ESCALATE-IF fires, escalate first — substitute only with Tier-1
   approval, and only if it tests the SAME assertion.)

PRE-FLIGHT SELF-CHECK (answer from THIS spec; if you can't, escalate)
  1. Which file? → instruments.js only
  2. What proves done? → the two-scenario test flips fail→pass; diff = 3 additions
  3. Forbidden to touch? → SOG display, COG math/format, all other handlers, other files

RETURN TO TIER 1
  • The diff · test output (fail-before/pass-after) · Decision Log (deviation or "none")
═══════════════════════════════════════════════════════════════════════
```

## Tier-1 verification (on return — §25.8)
1. Confirm test failed before / passes after.
2. `git diff`: exactly the 3 additions; no change to SOG handler output, COG math, or other handlers.
3. Logic probe: guard is `< 0.5` and only suppresses when `_lastSogKts` is a known number (not on null).
4. **Cannot verify remotely:** no-flicker behavior on the water when anchored — operator on-boat check after deploy.

## Out of scope
- Pi deploy (separate operator-authorized step).
- BUG-13 (speed gauge oscillation / options panel) — related symptom, different bug.
