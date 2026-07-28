# Atomic Spec — BUG-30 (depth gauge subscribes `belowKeel`; Signal K publishes `belowTransducer`)

**Format:** AAO §23.5 Atomic Spec · §25 escalation-enabled · §24 Question Queue
**Created:** 2026-07-27 (S108-cont) by Tier 1 (Opus 5)
**Tracker:** `deployment/docs/V09994_BUG_FIXES.md` BUG-30 · `PROJECT_CHECKLIST.md` PART 17
**Replaces the BUG-18 root cause.** **Depends on:** nothing.

---

## ⚠ The primary fix is CONFIGURATION, not code

`@signalk/n2k-signalk/dist/pgns/128267.js` — the Water Depth converter — already does this:

```js
{ source: 'depth',  node: 'environment.depth.belowTransducer' },
{ source: 'offset', node: 'environment.depth.transducerToKeel',
  filter: n2k => typeof n2k.fields.offset !== 'undefined' && n2k.fields.offset < 0 },
{ node: 'environment.depth.belowKeel',
  filter: n2k => n2k.fields.depth !== undefined && n2k.fields.offset !== undefined && n2k.fields.offset < 0,
  value:  n2k => Number(n2k.fields.depth) + Number(n2k.fields.offset) }
```

**Signal K computes `belowKeel` on its own — but only when PGN 128267 carries a NEGATIVE offset.**
A negative offset is the transducer-to-keel distance. S107 observed `belowTransducer = 0.99 m` with no
`belowKeel`, which means the Garmin is transmitting **no offset, or a positive one**.

So: **set a negative keel offset on the Garmin sounder and the existing dashboard code works
unchanged, with the correct and safest value.** No code change is required for the primary fix.

That is an on-boat operator action (measure transducer-to-keel, enter it on the Garmin). It is
recorded as an operator action, not a Tier-3 task.

## Why a code change is still warranted

Until the offset is set — and on any vessel where it never is — the depth gauge shows nothing at all,
which is worse than showing an honestly-labelled transducer reading. The code change below is a
**safe fallback**, not a replacement for the configuration.

**The safety rule this spec exists to protect:** `belowTransducer` is always a LARGER number than
`belowKeel`. Displaying transducer depth under a "Depth" label invites the skipper to read it as
clearance under the hull, overstating available water by the transducer-to-keel distance. In shallow
water that is a grounding. **The fallback must therefore relabel the cell so the two can never be
confused.**

---

## SPEC (paste this block to the Tier 3 model)

```
🔧 ATOMIC SPEC — BUG-30   (AAO §23.5 · §25 escalation-enabled)
═══════════════════════════════════════════════════════════════════════
TASK TYPE : [IMPLEMENT] — Tier 3
BUG       : BUG-30 — depth gauge shows nothing because it only accepts belowKeel

FILE TO EDIT (exactly one)
  deployment/v0.9.9.4/opt/d3kos/services/dashboard/static/js/instruments.js

CURRENT CODE (~line 159)
  'environment.depth.belowKeel': (v) => {
    _setVal('cellDepth', v.toFixed(1));
    const state = _evalBelow(v, THR.depth);
    _setCellState('cellDepth', state);
    _setUnit('cellDepth', state ? 'metres · ' + state : 'metres');
  },

WHAT TO BUILD — a preference-ordered fallback with an honest label

  belowKeel is ALWAYS preferred. belowTransducer is displayed ONLY when no
  belowKeel value has ever been seen, and when it is displayed the unit label
  MUST say so.

  (1) Add one module-level state variable immediately after the existing
      `let _lastSogKts = null;` (line 124, under the /* ── SIGNAL K HANDLERS ── */
      comment, just before `const SK_HANDLERS = {` at line 126):

        let _depthSource = null;   // 'keel' | 'transducer' | null — BUG-30

  (2) Replace the belowKeel handler body with a shared renderer plus two
      handlers. Keep the existing threshold and cell-state logic exactly.

        function _renderDepth(v, source) {
          // belowKeel always wins; never let a transducer value overwrite it
          if (source === 'transducer' && _depthSource === 'keel') return;
          _depthSource = source;
          _setVal('cellDepth', v.toFixed(1));
          const state = _evalBelow(v, THR.depth);
          _setCellState('cellDepth', state);
          const unit = source === 'keel' ? 'metres' : 'm · UNDER TRANSDUCER';
          _setUnit('cellDepth', state ? unit + ' · ' + state : unit);
        }

        'environment.depth.belowKeel':       (v) => _renderDepth(v, 'keel'),
        'environment.depth.belowTransducer': (v) => _renderDepth(v, 'transducer'),

  (3) Add the new path to _NULL_CELLS (the map starts at line 240; the existing
      belowKeel entry is line 244) so a null value still blanks the cell:

        'environment.depth.belowTransducer': 'cellDepth',

      NOTE: _NULL_CELLS is the ONLY path->cell map in this file. There is no
      PATH_TO_CELL map — do not go looking for one.

CONSTRAINT BOUNDARIES (do NOT)
  • Do NOT remove the belowKeel handler or subscription. It is the PREFERRED
    source and will start working the moment the sounder offset is configured.
  • Do NOT let a belowTransducer value overwrite a belowKeel value. Ever.
  • Do NOT display a transducer reading with a plain "metres" label. The label
    change is the safety control, not decoration.
  • Do NOT change THR.depth. See the alarm note below — the thresholds stay as
    they are and the limitation is documented, not silently compensated for.
  • Do NOT compute a keel offset in JavaScript. Signal K does that correctly when
    the sounder supplies one; guessing an offset in the client would invent data.
  • Do NOT touch environment.depth.belowSurface, surfaceToTransducer or
    transducerToKeel.
  • Do NOT touch any propulsion path — that is BUG-29.
  • Do NOT edit any other file. Do NOT regenerate MANIFEST.md5. Do NOT commit.
  • Do NOT touch the Pi.

INTERFACE CONTRACT
  after belowKeel(3.5)                     -> value 3.5, unit starts "metres"
  after belowTransducer(4.2) with no keel  -> value 4.2, unit contains "UNDER TRANSDUCER"
  belowKeel(3.5) then belowTransducer(4.2) -> value STAYS 3.5, unit stays "metres"
  belowTransducer(4.2) then belowKeel(3.5) -> value becomes 3.5, unit "metres"
  threshold/cell-state behaviour unchanged for both sources

FAILING TEST FIRST (TDD — write it, RUN IT, watch it fail, then fix)
  File: tests/bug30-depth-fallback.test.js       (plain Node, jsdom, no server)
  Run : node tests/bug30-depth-fallback.test.js
  The harness is proven (see BUG-36). Stub the depth cell so _setVal/_setUnit
  have somewhere to write — they no-op on a missing element.

    const { JSDOM, VirtualConsole } = require('jsdom');
    const fs = require('fs'); const assert = require('assert');
    const F = 'deployment/v0.9.9.4/opt/d3kos/services/dashboard/static/js/instruments.js';

    function load() {
      const vc = new VirtualConsole(); vc.on('jsdomError', () => {});
      const dom = new JSDOM(
        '<!doctype html><html><body>' +
        '<div id="cellDepth"><div class="ic-v"></div><div class="ic-u"></div></div>' +
        '</body></html>', { runScripts: 'outside-only', virtualConsole: vc });
      dom.window.eval(fs.readFileSync(F, 'utf8'));
      return dom.window;
    }
    const val  = w => w.document.querySelector('#cellDepth .ic-v').innerHTML;
    const unit = w => w.document.querySelector('#cellDepth .ic-u').textContent;

    // 1 — belowTransducer alone renders, and is LABELLED as transducer depth
    let w = load();
    assert.ok(w.SK_HANDLERS['environment.depth.belowTransducer'],
              'belowTransducer handler must exist');
    w.SK_HANDLERS['environment.depth.belowTransducer'](4.2);
    assert.strictEqual(val(w), '4.2', 'transducer depth must render');
    assert.ok(/UNDER TRANSDUCER/.test(unit(w)),
      'a transducer reading MUST be labelled as such — never plain "metres"');

    // 2 — belowKeel renders with the plain label
    w = load();
    w.SK_HANDLERS['environment.depth.belowKeel'](3.5);
    assert.strictEqual(val(w), '3.5');
    assert.ok(!/TRANSDUCER/.test(unit(w)), 'keel depth must NOT carry the transducer label');

    // 3 — SAFETY: transducer must never overwrite a keel value
    w = load();
    w.SK_HANDLERS['environment.depth.belowKeel'](3.5);
    w.SK_HANDLERS['environment.depth.belowTransducer'](4.2);
    assert.strictEqual(val(w), '3.5',
      'belowTransducer must NOT overwrite belowKeel — that would overstate clearance');
    assert.ok(!/TRANSDUCER/.test(unit(w)), 'label must stay on keel');

    // 4 — keel arriving later takes over
    w = load();
    w.SK_HANDLERS['environment.depth.belowTransducer'](4.2);
    w.SK_HANDLERS['environment.depth.belowKeel'](3.5);
    assert.strictEqual(val(w), '3.5', 'belowKeel must take over when it arrives');
    assert.ok(!/TRANSDUCER/.test(unit(w)));

    // 5 — REGRESSION: shallow-water alarm still fires on both sources
    w = load();
    w.SK_HANDLERS['environment.depth.belowKeel'](0.5);
    assert.ok(/Critical|Alert|Advisory/i.test(unit(w)), 'keel alarm state must still render');
    w = load();
    w.SK_HANDLERS['environment.depth.belowTransducer'](0.5);
    assert.ok(/Critical|Alert|Advisory/i.test(unit(w)), 'transducer alarm state must still render');

    console.log('BUG-30: ALL ASSERTIONS PASSED');

  EXPECTED BEFORE THE FIX: assertion 1 fails —
    "belowTransducer handler must exist"
  If it passes before your fix, STOP and escalate.

DONE WHEN
  • The test FAILED before your edit and PASSES after.
  • Only instruments.js changed.
  • The belowKeel path and its behaviour are unchanged when belowKeel is present.

ESCALATE-IF  (emit the 🔺 block — do not guess)
  • You think the client should compute belowKeel from a hardcoded offset
                            → STOP. That invents safety-critical data.
  • You think THR.depth should be adjusted for the transducer case
                            → ADVICE. Do not change it. See the alarm note.
  • _setUnit / _evalBelow / THR.depth are not as this spec describes
                            → CLARIFICATION (file differs from expectation)

PRE-FLIGHT SELF-CHECK
  1. Which source wins?          → belowKeel, always
  2. What must the fallback do?  → relabel to "UNDER TRANSDUCER"
  3. May transducer overwrite keel? → never
  4. Do I compute an offset?     → no, never
  5. Files changed?              → instruments.js only

RETURN TO TIER 1
  • The diff
  • Terminal output: fail-before and pass-after
  • Decision Log: every deviation, or "none"
═══════════════════════════════════════════════════════════════════════
```

---

## ⚠ Alarm limitation — documented, deliberately not compensated for

`THR.depth` is `{ adv: 3, alrt: 2, crit: 1 }` metres. Those numbers were chosen for depth **under the
keel**. When the fallback is active the gauge is showing depth under the **transducer**, which is a
larger number — so the shallow-water alarm fires **later than it should**, i.e. optimistically.

The thresholds are deliberately left alone: the true correction is the transducer-to-keel offset,
which the client does not know and must not guess. The `UNDER TRANSDUCER` label is the mitigation —
it tells the skipper the reading is not keel clearance.

**This is another reason the sounder offset is the real fix, not the fallback.**

## Operator actions

1. **Measure the transducer-to-keel distance** on the Monterey 265 — vertical distance from the
   transducer face to the lowest point of the hull/drive.
2. **Set that as a NEGATIVE keel offset on the Garmin sounder.** Signal K then publishes
   `environment.depth.belowKeel` automatically and the preferred path lights up with no further code
   change, the label reverts to plain `metres`, and the alarm thresholds become correct.
3. Confirm on-boat: `curl -s http://localhost:8099/signalk/v1/api/vessels/self/environment/depth`
   should show `belowKeel` alongside `belowTransducer`.

`Uncertainty flag: I have not verified how the Garmin's offset setting is labelled in its menus, and
I have not researched the Monterey 265's transducer position. Per the Hardware Claim Protocol I am
making no claim about either — the measurement and the menu path are operator territory.`

## Tier-1 verification pass (§25.8)

1. **The safety assertion is the one that matters:** `belowTransducer` must never overwrite a
   `belowKeel` value, and must never render with a plain `metres` label. Check both directly.
2. `belowKeel` behaviour byte-for-byte unchanged when `belowKeel` is present.
3. No hardcoded offset, no client-side arithmetic on depth beyond `toFixed(1)`.
4. `THR.depth` unchanged.
5. Only `instruments.js` changed.
6. **Cannot verify remotely:** real depth on a real gauge. Needs a deploy and a live sounder.

## Out of scope
Pi deployment · configuring the Garmin (operator) · `THR.depth` retuning · `belowSurface` /
`surfaceToTransducer` / `transducerToKeel` paths · BUG-29 propulsion paths.
