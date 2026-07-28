# Atomic Spec — BUG-36 (S105 deploy removed the M14 `_d3kEngData` engine cache)

**Format:** AAO §23.5 Atomic Spec · §25 escalation-enabled · §24 Question Queue
**Created:** 2026-07-27 (S108) by Tier 1 (Opus 5)
**Revised 2026-07-27 after Tier-3 execution — two Tier-1 spec defects corrected:**
(1) the line count said SIX; the itemised content is EIGHT (comment + declaration + blank +
five assignments). (2) the `propulsion.0.revolutions` anchor was quoted from the read-only
*reference* file, not the *target* — the target computes inline and has no `const _rpm`.
Combined with the zero-deletions rule this made the spec unsatisfiable as literally written.
Tier 3 identified both and resolved them correctly; the escalation it should have raised per
ESCALATE-IF would have deadlocked on Tier 1's own error.
**Tracker:** `deployment/docs/V09994_BUG_FIXES.md` BUG-36 · `PROJECT_CHECKLIST.md` PART 17
**Questions:** `wiki/questions/2026-07-27-v0994-tier3-spec-questions.md` — **read Q0.1–Q0.5 and Q36.1–Q36.4 before coding**
**Depends on:** nothing. **Blocks:** BUG-16 acceptance (with BUG-38).

---

## Tier-1 finding

On 2026-07-23 the S105 BUG-15 deploy took `instruments.js` from
`deployment/d3kOS/dashboard/` — a source tree that **never contained the M14 engine-data cache**.
The COG fix itself was correct; the file it landed in was from the wrong lineage.

| File | md5 | `_d3kEngData` | Size |
|---|---|---|---|
| Pi backup `instruments.js.bak.20260723` (pre-S105) | `496d9800…` = `pi_source` | **6** | 19,201 |
| Current canonical / Pi | `d957fb8b…` = `d3kOS/dashboard` | **0** | 18,794 |

`overlays.js` line 61 reads `const eng = window._d3kEngData || {};`. Nothing populates it, so every
diagnostic card renders `—` and the Gemini prompt says *"no live readings available"* regardless of
which gauge was tapped. **Empirically confirmed** by loading the current file in jsdom and firing all
five engine handlers: `window._d3kEngData` is `undefined`.

**This is a pure restoration.** The lost block goes back verbatim — eight added lines, zero deletions. Nothing else changes.

---

## SPEC (paste this block to the Tier 3 model)

```
🔧 ATOMIC SPEC — BUG-36   (AAO §23.5 · §25 escalation-enabled)
═══════════════════════════════════════════════════════════════════════
TASK TYPE : [IMPLEMENT] — Tier 3
BUG       : BUG-36 — restore the M14 live engine-data cache

FILE TO EDIT (exactly one)
  deployment/v0.9.9.4/opt/d3kos/services/dashboard/static/js/instruments.js

READ-ONLY REFERENCE (copy FROM this, never write to it)
  deployment/v0.9.4/pi_source/instruments.js        ← the v0.9.9.2 original

CHANGE — add EIGHT lines. Add nothing else. Delete nothing.
  (comment + declaration + the blank separator after it + five assignments.
   The blank line reproduces pi_source's formatting — keep it.)

  (1) DECLARATION — insert immediately BEFORE the line `/* ── CELL STATE ── */`
      (currently ~line 26 of the canonical file), reproducing the original exactly:

          /* ── LIVE ENGINE DATA CACHE (populated by SK handlers, read by openDiag) ── */
          window._d3kEngData = { coolant_c:null, oil_psi:null, rpm:null, bat_v:null, fuel_pct:null };

  (2..6) FIVE CACHE ASSIGNMENTS — one line into each existing engine handler.
      Insert each as the FIRST statement after the handler's existing local
      computation, exactly as positioned in pi_source. Do not restructure the
      handlers; do not touch their display logic.

      handler 'propulsion.0.coolantTemperature'
        after :  const c = v - 273.15, disp = c.toFixed(0);
        add   :  window._d3kEngData.coolant_c = c;

      handler 'propulsion.0.oilPressure'
        after :  const psi = Math.round(v * 0.000145038);
        add   :  window._d3kEngData.oil_psi = psi;

      handler 'propulsion.0.revolutions'
        NOTE: the TARGET file has no `const _rpm` line — it computes inline inside
        _setVal(). Introducing `const _rpm` would require EDITING the existing
        _setVal line, which the zero-deletions rule forbids. So add the value
        directly as the handler's first statement:
        add   :  window._d3kEngData.rpm = Math.round(v * 60);
        (This duplicates the Math.round call. That is correct and intended here —
         the zero-deletions constraint takes precedence over avoiding it.)

      handler 'tanks.fuel.0.currentLevel'
        after :  const pct = Math.round(v * 100);
        add   :  window._d3kEngData.fuel_pct = v;      ← the FRACTION v, NOT pct. See Q36.2.

      handler 'electrical.batteries.0.voltage'
        first statement in the handler
        add   :  window._d3kEngData.bat_v = parseFloat(v.toFixed(1));

CONSTRAINT BOUNDARIES (do NOT)
  • Do NOT change any Signal K path. The handlers keep the 'propulsion.0.*' keys
    exactly as they are. BUG-29 corrects those paths in its own spec — see Q36.1.
  • Do NOT copy the whole pi_source file over the canonical file. That would delete
    the S105 COG fix and re-create BUG-15. See Q36.4.
  • Do NOT touch _lastSogKts (canonical lines ~121, ~126, ~135) — S105's BUG-15 fix.
  • Do NOT touch window.SK_HANDLERS (~line 229) — the test seam.
  • Do NOT touch THR, FUEL_CAP_L, _setVal, _setUnit, _setCellState, or any display code.
  • Do NOT store fuel as a percentage. _diagReadingsSummary() multiplies by 100.
  • Do NOT edit any other file. Do NOT regenerate MANIFEST.md5 (Q0.4).
  • Do NOT deploy to the Pi (Q0.2).

INTERFACE CONTRACT
  After loading instruments.js and firing the five engine handlers, the object
  window._d3kEngData satisfies:

    { coolant_c: <number °C>,        // kelvin - 273.15, unrounded
      oil_psi:   <integer PSI>,      // pascals * 0.000145038, rounded
      rpm:       <integer>,          // hertz * 60, rounded
      bat_v:     <number, 1 dp>,     // parseFloat(v.toFixed(1))
      fuel_pct:  <number 0..1> }     // the RAW FRACTION, not a percentage

  Before any handler fires, every key is null (not undefined, not absent).

FAILING TEST FIRST (TDD — write it, RUN IT, watch it fail, then fix)
  File: tests/bug36-engine-data-cache.test.js      (plain Node — no Playwright, no server)
  Run : node tests/bug36-engine-data-cache.test.js
  This harness is PROVEN to work — Tier 1 executed it against the unfixed file.

    const { JSDOM, VirtualConsole } = require('jsdom');
    const fs = require('fs');
    const assert = require('assert');

    const FILE = 'deployment/v0.9.9.4/opt/d3kos/services/dashboard/static/js/instruments.js';

    function load(file) {
      const vc = new VirtualConsole();
      vc.on('jsdomError', () => {});   // _init() touches DOM nodes we deliberately don't stub
      const dom = new JSDOM('<!doctype html><html><body></body></html>',
                            { runScripts: 'outside-only', virtualConsole: vc });
      dom.window.eval(fs.readFileSync(file, 'utf8'));
      return dom.window;
    }

    // 1 — cache exists and is all-null before any data arrives
    let w = load(FILE);
    assert.ok(w._d3kEngData, 'window._d3kEngData must exist on load');
    // NOTE: build the expected object INSIDE the jsdom realm. A plain Node object
    // literal has a different Object.prototype, so deepStrictEqual fails on
    // prototype identity across realms even when the values match. (Found by
    // Tier 3 during execution; corrected here.)
    w.eval('window._expected = { coolant_c:null, oil_psi:null, rpm:null, bat_v:null, fuel_pct:null };');
    assert.deepStrictEqual(w._d3kEngData, w._expected, 'cache must initialise all-null');

    // 2 — each handler populates its key with the right unit conversion
    w.SK_HANDLERS['propulsion.0.coolantTemperature'](368.15);   // K   -> 95 C
    w.SK_HANDLERS['propulsion.0.oilPressure'](344738);          // Pa  -> 50 PSI
    w.SK_HANDLERS['propulsion.0.revolutions'](30);              // Hz  -> 1800 rpm
    w.SK_HANDLERS['tanks.fuel.0.currentLevel'](0.5);            // fraction
    w.SK_HANDLERS['electrical.batteries.0.voltage'](12.64);     // V

    assert.strictEqual(Math.round(w._d3kEngData.coolant_c), 95, 'coolant_c');
    assert.strictEqual(w._d3kEngData.oil_psi, 50,                'oil_psi');
    assert.strictEqual(w._d3kEngData.rpm, 1800,                  'rpm');
    assert.strictEqual(w._d3kEngData.fuel_pct, 0.5,              'fuel_pct must be the FRACTION');
    assert.strictEqual(w._d3kEngData.bat_v, 12.6,                'bat_v');

    // 3 — REGRESSION: the S105 BUG-15 COG gate must still be intact
    const src = fs.readFileSync(FILE, 'utf8');
    assert.ok(/_lastSogKts/.test(src),            'S105 _lastSogKts must survive');
    assert.ok(/window\.SK_HANDLERS\s*=/.test(src),'test seam must survive');

    // 4 — REGRESSION: COG still suppressed when stationary
    w = load(FILE);
    w.SK_HANDLERS['navigation.speedOverGround'](0);
    w.SK_HANDLERS['navigation.courseOverGroundTrue'](0.1745);
    w.SK_HANDLERS['navigation.courseOverGroundTrue'](3.4907);
    // no assertion on DOM (not stubbed) — this must simply not throw

    console.log('BUG-36: ALL ASSERTIONS PASSED');

  EXPECTED BEFORE THE FIX: assertion 1 fails —
    "window._d3kEngData must exist on load"   (it is currently undefined)
  If it does not fail, STOP and escalate — you are editing the wrong file.

DONE WHEN
  • The test FAILED before your edit and PASSES after.
  • git diff shows exactly EIGHT added lines in instruments.js and ZERO deletions.
  • git diff shows no other file changed except the new test file.

ESCALATE-IF  (emit the 🔺 block — do not guess)
  • The test passes BEFORE your fix          → CLARIFICATION (wrong file / already fixed)
  • A handler's "after" anchor line does not match this spec
                                             → CLARIFICATION (file differs from expectation)
  • _lastSogKts is absent from the canonical file
                                             → CLARIFICATION (S105 fix missing — bigger problem)
  • You believe the Signal K paths must change to make the test pass
                                             → ADVICE (that is BUG-29 — do not do it here)
  • jsdom is not resolvable                  → SOLUTION-REQUEST (run from the Helm-OS repo root)

PRE-FLIGHT SELF-CHECK (answer from this spec; if you cannot, escalate)
  1. Which file do I edit?        → canonical instruments.js only
  2. How many lines do I add?     → exactly 8; deletions: 0
  3. Fuel: fraction or percent?   → fraction (v), never pct
  4. What must survive untouched? → _lastSogKts, window.SK_HANDLERS, all display logic
  5. Do I fix propulsion.0.*?     → no, that is BUG-29

RETURN TO TIER 1
  • The six-line diff
  • Terminal output showing fail-before and pass-after
  • Decision Log: any deviation, or "none"
═══════════════════════════════════════════════════════════════════════
```

---

## Tier-1 verification pass (§25.8 — run on Tier 3's return)

1. `git diff` = exactly 8 insertions, 0 deletions in `instruments.js`.
2. `_lastSogKts` still present at 3 sites; `window.SK_HANDLERS` still present.
3. Test genuinely failed first — require the pre-fix terminal output, not a claim.
4. `fuel_pct` stores the fraction. A percentage here is a silent 100× error — check explicitly.
5. No Signal K path changed (`propulsion.0.` count unchanged at 8).
6. **Cannot verify remotely:** that the diagnostic panel now shows live values. That needs BUG-38
   (the DOM IDs) plus BUG-29 (real data on the path) plus a deploy. Do not claim BUG-16 fixed.

## Out of scope
Pi deployment · BUG-29 path correction · BUG-38 DOM IDs · anything in `overlays.js`.
