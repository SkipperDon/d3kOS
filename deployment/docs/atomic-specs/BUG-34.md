# Atomic Spec — BUG-34 (Diag panel: fabricated alarm string, wrong thresholds, missing cards, broken PWA URL)

**Format:** AAO §23.5 Atomic Spec · §25 escalation-enabled · §24 Question Queue
**Created:** 2026-07-29 (S110) by Tier 1 (Opus 5)
**Tracker:** `deployment/docs/V09994_BUG_FIXES.md` BUG-34 · `PROJECT_CHECKLIST.md` PART 17
**Questions:** none open — all information derived directly from the two target files.
**Depends on:** BUG-36 (M14 `_d3kEngData` cache must exist — verified DEPLOYED to lab Pi).
**Source authority:** MerCruiser 454 Mag MPI SM: oil ≥30 psi@2000 RPM / ≥4 psi idle; alternator 13.9–14.7 V normal. Sourced S106 — `deployment/docs/MERCRUISER_454_MAG_MPI_SM_AI.md`.

---

## Tier-1 finding

Five defects in two files, all in the M14 engine diagnostic panel:

| # | File | Line | Defect |
|---|------|------|--------|
| D1 | `overlays.js` | 123 | `showCrit()` hardcodes fabricated reading `'8 PSI'` in ticker |
| D2 | `instruments.js` | 20 | `THR.oil.crit:20` — normal idle oil pressure (~8 PSI) triggers Critical |
| D3 | `instruments.js` | 21 | `THR.bat` has no upper bound — 15.5 V overcharge reads "✓ Normal" |
| D4 | `overlays.js` | 105–116 | `_diagBuildCards` builds 4 cards; `cellFuel` and `cellDepth` are mapped in `_diagCellLabel` but never rendered |
| D5 | `overlays.js` | 75 | `openDiag` fetches `http://localhost:8097/gemini/chat` — fails from PWA/phone (localhost resolves to the phone) |

**D2 detail:** `_stateBelow(8, {adv:30, alrt:25, crit:20})` → `8 ≤ 20` → `'Critical'`. Normal idle oil is 4–15 PSI per MerCruiser 454. Fix: `crit:4` — only below 4 PSI (absolute minimum per spec) triggers Critical. The `adv:30` and `alrt:25` thresholds remain as operating-speed guidance.

**D3 detail:** `_stateBelow(15.5, {adv:12.4, alrt:12.0, crit:11.5})` → no condition matches → `null` → shows "✓ Normal". Normal charging range is 13.9–14.7 V. Fix: add `bat_hi: { adv:14.8, alrt:15.2, crit:15.6 }` and check it in the battery card using `_stateAbove`.

**D4 detail:** `_d3kEngData` does not currently hold a depth value, so depth cannot be shown from cache. Fix: add `depth_m:null` to `_d3kEngData` and write it in `_renderDepth`. Then add both cards.

**D5 detail:** No Flask proxy for `/gemini/chat` exists in `app.py`. Fix: replace `http://localhost:8097` with `'http://' + window.location.hostname + ':8097'`. On the Pi screen (`localhost:3000`), hostname = `localhost` → unchanged. From PWA (`192.168.1.237:3000`), hostname = `192.168.1.237` → correct.

---

## SPEC (paste this block to the Tier 3 model)

```
🔧 ATOMIC SPEC — BUG-34   (AAO §23.5 · §25 escalation-enabled)
═══════════════════════════════════════════════════════════════════════
TASK TYPE : [IMPLEMENT] — Tier 3
BUG       : BUG-34 — Diag panel: fabricated alarm, wrong thresholds,
            missing fuel/depth cards, broken PWA URL

FILES TO EDIT (exactly two)
  deployment/v0.9.9.4/opt/d3kos/services/dashboard/static/js/instruments.js
  deployment/v0.9.9.4/opt/d3kos/services/dashboard/static/js/overlays.js

════════════════════════════════════════════════════════════════════
CHANGE A — instruments.js  (3 targeted edits, no other changes)
════════════════════════════════════════════════════════════════════

A1. THR.oil.crit — change 20 → 4

  FIND (exact line):
    oil:     { adv: 30,   alrt: 25,   crit: 20   },  // PSI, below = alarm

  REPLACE WITH:
    oil:     { adv: 30,   alrt: 25,   crit: 4    },  // PSI, below = alarm; ≥4 psi min idle per MerCruiser 454

A2. THR.bat_hi — add new entry directly after the bat line

  FIND (exact line):
    bat:     { adv: 12.4, alrt: 12.0, crit: 11.5 },  // V, below = alarm

  REPLACE WITH:
    bat:     { adv: 12.4, alrt: 12.0, crit: 11.5 },  // V, below = alarm
    bat_hi:  { adv: 14.8, alrt: 15.2, crit: 15.6 },  // V, above = overcharge alarm; normal charging 13.9–14.7 V

A3. _d3kEngData — add depth_m key AND write it in _renderDepth

  FIND (exact line):
    window._d3kEngData = { coolant_c:null, oil_psi:null, rpm:null, bat_v:null, fuel_pct:null };

  REPLACE WITH:
    window._d3kEngData = { coolant_c:null, oil_psi:null, rpm:null, bat_v:null, fuel_pct:null, depth_m:null };

  THEN find the _renderDepth function body. It begins:
    function _renderDepth(v, source) {
      // belowKeel always wins; never let a transducer value overwrite it
      if (source === 'transducer' && _depthSource === 'keel') return;
      _depthSource = source;
      _setVal('cellDepth', v.toFixed(1));

  Add one line after `_depthSource = source;`:
    window._d3kEngData.depth_m = parseFloat(v.toFixed(1));  // BUG-34

  The result must be:
    function _renderDepth(v, source) {
      // belowKeel always wins; never let a transducer value overwrite it
      if (source === 'transducer' && _depthSource === 'keel') return;
      _depthSource = source;
      window._d3kEngData.depth_m = parseFloat(v.toFixed(1));  // BUG-34
      _setVal('cellDepth', v.toFixed(1));

════════════════════════════════════════════════════════════════════
CHANGE B — overlays.js  (5 targeted edits, no other changes)
════════════════════════════════════════════════════════════════════

B1. showCrit fabricated string — line ~123

  FIND (exact line):
    ticker.textContent = '⛔ CRITICAL — OIL PRESSURE 8 PSI — TAKE ACTION NOW';

  REPLACE WITH:
    ticker.textContent = '⛔ CRITICAL ENGINE ALARM — SHUT DOWN ENGINE IMMEDIATELY';

B2. openDiag hardcoded URL — line ~75

  FIND (exact):
    const r = await fetch('http://localhost:8097/gemini/chat', {

  REPLACE WITH:
    const r = await fetch('http://' + window.location.hostname + ':8097/gemini/chat', {

B3. _diagBuildCards fallback THR — line ~106

  FIND (exact line):
    const thr = typeof THR !== 'undefined' ? THR : {coolant:{adv:88,alrt:98,crit:105},oil:{adv:30,alrt:25,crit:20},bat:{adv:12.4,alrt:12.0,crit:11.5}};

  REPLACE WITH:
    const thr = typeof THR !== 'undefined' ? THR : {
      coolant: {adv:88,  alrt:98,  crit:105},
      oil:     {adv:30,  alrt:25,  crit:4},
      bat:     {adv:12.4,alrt:12.0,crit:11.5},
      bat_hi:  {adv:14.8,alrt:15.2,crit:15.6},
      depth:   {adv:3,   alrt:2,   crit:1},
      fuel:    {adv:0.25,alrt:0.15,crit:0.10},
    };

B4. Battery card — update to check overcharge via bat_hi — line ~113

  FIND (exact line):
    { lbl:'Battery', val: eng.bat_v!=null ? eng.bat_v+'V':'—', st: _stateBelow(eng.bat_v, thr.bat) },

  REPLACE WITH:
    { lbl:'Battery', val: eng.bat_v!=null ? eng.bat_v+'V':'—', st: _stateBelow(eng.bat_v, thr.bat) || (thr.bat_hi ? _stateAbove(eng.bat_v, thr.bat_hi) : null) },

  WHY the guard `thr.bat_hi ? ... : null`: if overlays.js somehow loads without
  instruments.js (test environment), thr.bat_hi is undefined; without the guard
  _stateAbove would throw TypeError. The guard makes the overcharge check graceful.

B5. Add fuel and depth cards — insert after the battery card line

  FIND (the battery card line you just edited, and the line that closes the cards array):
    { lbl:'Battery', val: eng.bat_v!=null ? eng.bat_v+'V':'—', st: _stateBelow(eng.bat_v, thr.bat) || (thr.bat_hi ? _stateAbove(eng.bat_v, thr.bat_hi) : null) },
  ];

  REPLACE WITH:
    { lbl:'Battery', val: eng.bat_v!=null ? eng.bat_v+'V':'—', st: _stateBelow(eng.bat_v, thr.bat) || (thr.bat_hi ? _stateAbove(eng.bat_v, thr.bat_hi) : null) },
    { lbl:'Fuel',    val: eng.fuel_pct!=null ? Math.round(eng.fuel_pct*100)+'%':'—', st: _stateBelow(eng.fuel_pct, thr.fuel) },
    { lbl:'Depth',   val: eng.depth_m!=null  ? eng.depth_m.toFixed(1)+' m':'—',     st: _stateBelow(eng.depth_m,  thr.depth) },
  ];

  NOTE: fuel_pct is a fraction (0.0–1.0). `Math.round(eng.fuel_pct*100)+'%'` is the
  correct display format — it already matches _diagReadingsSummary at line ~101.
  depth_m is in metres, matching the THR.depth unit (m, below = alarm).

CONSTRAINT BOUNDARIES (do NOT)
  • Do NOT change any Signal K path, handler, or subscription.
  • Do NOT change _stateAbove or _stateBelow function signatures.
  • Do NOT edit any other file (app.py, settings.html, index.html, etc.).
  • Do NOT touch the pi_source trees.
  • Do NOT deploy to the Pi.
  • Do NOT regenerate MANIFEST.md5.
  • Do NOT commit.

INTERFACE CONTRACTS

  After the fix:
  • showCrit() ticker: must NOT contain '8 PSI' or any fabricated reading
  • openDiag() URL: must NOT contain 'localhost:8097' as a literal string
  • THR.oil.crit === 4  (instruments.js)
  • THR.bat_hi exists with adv:14.8, alrt:15.2, crit:15.6  (instruments.js)
  • window._d3kEngData has key depth_m  (instruments.js)
  • _renderDepth writes window._d3kEngData.depth_m  (instruments.js)
  • _diagBuildCards({fuel_pct:0.5, depth_m:8.0}) HTML contains 'Fuel' and 'Depth'
  • _diagBuildCards({bat_v:15.5}) HTML contains class 'bad' (overcharge = Alert)
  • _diagBuildCards({bat_v:13.0}) HTML does NOT contain class 'bad' (normal = no alarm)

FAILING TEST FIRST (TDD — write it, RUN IT, watch it fail, THEN fix)
  File: tests/bug34-diag-panel.test.js
  Run : node --experimental-vm-modules node_modules/.bin/jest tests/bug34-diag-panel.test.js
  (same runner used for bug36 and bug38 tests)

  import { readFileSync } from 'fs';
  import { JSDOM } from 'jsdom';

  const INSTRUMENTS = 'deployment/v0.9.9.4/opt/d3kos/services/dashboard/static/js/instruments.js';
  const OVERLAYS    = 'deployment/v0.9.9.4/opt/d3kos/services/dashboard/static/js/overlays.js';

  // ── Static source checks (no DOM needed) ────────────────────────────────

  test('showCrit does not contain fabricated 8 PSI reading', () => {
    const src = readFileSync(OVERLAYS, 'utf8');
    expect(src).not.toMatch(/8 PSI/);
  });

  test('openDiag does not contain hardcoded localhost:8097', () => {
    const src = readFileSync(OVERLAYS, 'utf8');
    expect(src).not.toMatch(/['"`]http:\/\/localhost:8097/);
  });

  test('THR.oil.crit is 4 in instruments.js', () => {
    const src = readFileSync(INSTRUMENTS, 'utf8');
    // Must contain crit: 4 in the oil line, NOT crit: 20
    expect(src).toMatch(/oil\s*:.*crit\s*:\s*4/);
    expect(src).not.toMatch(/oil\s*:.*crit\s*:\s*20/);
  });

  test('THR.bat_hi exists in instruments.js', () => {
    const src = readFileSync(INSTRUMENTS, 'utf8');
    expect(src).toMatch(/bat_hi\s*:/);
    expect(src).toMatch(/14\.8/);   // adv
    expect(src).toMatch(/15\.6/);   // crit
  });

  test('_d3kEngData includes depth_m key in instruments.js', () => {
    const src = readFileSync(INSTRUMENTS, 'utf8');
    expect(src).toMatch(/depth_m\s*:\s*null/);
  });

  test('_renderDepth writes depth_m to _d3kEngData in instruments.js', () => {
    const src = readFileSync(INSTRUMENTS, 'utf8');
    const renderDepthBlock = src.split('function _renderDepth')[1]?.split(/^}/m)[0] ?? '';
    expect(renderDepthBlock).toMatch(/_d3kEngData\.depth_m/);
  });

  // ── Functional checks (jsdom) ────────────────────────────────────────────

  function buildWindow() {
    const dom = new JSDOM(
      `<!DOCTYPE html><html><body>
        <div id="ticker"></div><div id="critSc"></div>
        <div id="diagBack"></div><div id="diagGrid"></div>
        <div id="diagTitle"></div><div id="diagAiTxt"></div>
        <div id="toast"></div><div id="alertCard"></div>
      </body></html>`,
      { runScripts: 'dangerously' }
    );
    const w = dom.window;
    // instruments.js defines THR and _d3kEngData; suppress WebSocket/fetch errors
    try { w.eval(readFileSync(INSTRUMENTS, 'utf8')); } catch {}
    w.eval(readFileSync(OVERLAYS, 'utf8'));
    return w;
  }

  test('_diagBuildCards renders Fuel and Depth cards', () => {
    const w = buildWindow();
    const html = w._diagBuildCards({ fuel_pct: 0.5, depth_m: 8.0 });
    expect(html).toMatch(/Fuel/);
    expect(html).toMatch(/Depth/);
    expect(html).toMatch(/50%/);
    expect(html).toMatch(/8\.0\s*m/);
  });

  test('_diagBuildCards flags 15.5V battery as bad (overcharge)', () => {
    const w = buildWindow();
    const html = w._diagBuildCards({ bat_v: 15.5 });
    // The card div for Battery must carry the 'bad' class
    const batteryCard = html.match(/<div class="dc[^"]*">[^<]*<div class="dc-lbl">Battery/)?.[0] ?? '';
    expect(batteryCard).toMatch(/bad/);
  });

  test('_diagBuildCards does NOT flag 13.0V battery as bad (normal charging)', () => {
    const w = buildWindow();
    const html = w._diagBuildCards({ bat_v: 13.0 });
    const batteryCard = html.match(/<div class="dc[^"]*">[^<]*<div class="dc-lbl">Battery/)?.[0] ?? '';
    expect(batteryCard).not.toMatch(/bad/);
  });

  EXPECTED BEFORE THE FIX:
    showCrit does not contain fabricated 8 PSI reading   FAILED
    openDiag does not contain hardcoded localhost:8097   FAILED
    THR.oil.crit is 4 in instruments.js                 FAILED
    THR.bat_hi exists in instruments.js                 FAILED
    _d3kEngData includes depth_m key                    FAILED
    _renderDepth writes depth_m                         FAILED
    _diagBuildCards renders Fuel and Depth cards        FAILED
    _diagBuildCards flags 15.5V as bad                  FAILED
    _diagBuildCards does NOT flag 13.0V as bad          PASSED (it already passes before fix)

  If fewer than 8 tests fail before your edit, STOP and escalate — you may
  be editing the wrong file or the fix is partially applied already.

DONE WHEN
  • All 9 tests PASS after your edits.
  • git diff touches exactly instruments.js and overlays.js (plus the new test file).
  • No handler, no Signal K path, no other file is changed.

ESCALATE-IF  (emit the 🔺 block — do not guess)
  • The findable FIND string for any change is absent from the file
    → ADVICE (paste the surrounding 5 lines so Tier 1 can identify the correct anchor)
  • The jsdom functional tests error on load (not just the static tests)
    → SOLUTION-REQUEST (paste the error; do not silence it with try/catch and claim pass)
  • You cannot isolate the battery card HTML in the _diagBuildCards output to test it
    → ADVICE (describe the actual HTML structure; do not skip the test)
  • instruments.js or overlays.js has materially different content from what the spec describes
    → ADVICE (paste the diff)

PRE-FLIGHT SELF-CHECK
  1. How many files do I edit?            → exactly 2 (instruments.js + overlays.js)
  2. Do I change any SK handler or path?  → NO
  3. Is the bat_hi guard in place?        → YES — `thr.bat_hi ? _stateAbove(...) : null`
  4. Is fuel_pct multiplied by 100?       → YES — `Math.round(eng.fuel_pct*100)+'%'`
  5. What proves done?                    → 9 tests flip fail→pass (except test 9 which already passes)

RETURN TO TIER 1
  • git diff for both files
  • jest output: failing run AND passing run
  • Decision Log: any deviation from the spec, or "none"
═══════════════════════════════════════════════════════════════════════
```

---

## Tier-1 verification pass (§25.8)

1. `THR.oil.crit:4` — 4 PSI is the documented MerCruiser 454 minimum at idle. Normal idle (4–15 PSI) no longer triggers Critical.
2. `THR.bat_hi` added — `_stateAbove(15.5, {adv:14.8, alrt:15.2, crit:15.6})` → 15.5 ≥ 15.2 → 'Alert'. Was null before.
3. `bat_hi` guard — `thr.bat_hi ? _stateAbove(...) : null` prevents TypeError if overlays.js loads without instruments.js.
4. `depth_m` added to `_d3kEngData` and written in `_renderDepth` — depth card now has live data to display.
5. `fuel_pct * 100` — matches `_diagReadingsSummary` formula at line 101. No 100× error.
6. `window.location.hostname` — works from Pi screen (`localhost`) and PWA phone (`192.168.1.237`).
7. Fabricated string gone — `showCrit` ticker now generic, no invented PSI value.
8. Tests genuinely fail first — require the pre-fix run output for all 8.
9. **Cannot verify without live engine data:** oil at 8 PSI idle no longer flags Critical — this will be confirmed on-boat. Post-deploy: check diag panel with engine idling and engine at cruise.

## Out of scope
Changing any Signal K path · fixing `_BRIDGE_URL` in instruments.js (same localhost issue, separate bug) · changing RPM threshold logic in `boatlog-engine.js` · deploying to Pi · pi_source trees.
