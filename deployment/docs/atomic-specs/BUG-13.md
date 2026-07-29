# Atomic Spec — BUG-13 (Speed Gauge Flicker + Context Menu Obscures Readout)

**Format:** AAO §23.5 Atomic Spec · §25 escalation-enabled · §24 Question Queue
**Created:** 2026-07-29 (S110) by Tier 1 (Opus 5)
**Tracker:** `deployment/docs/V09994_BUG_FIXES.md` BUG-13 · `PROJECT_CHECKLIST.md` PART 17
**Questions:** none open — two root causes identified directly from the source files.
**Depends on:** nothing. Both fixes apply to the lab Pi now; Issue 1 validation requires on-boat speed change.

---

## Tier-1 finding

Two independent defects in `instruments.js`. One file. One commit.

### Issue 1 — Speed gauge flicker (lines 141–148)

The `navigation.speedOverGround` handler calls `_setVal('cellSpeed', kts)` on every
WebSocket message — no rate limiting, no coalescing. Signal K publishes SOG from
**all sources on the bus**: the Garmin (src 0) updates at ~1 Hz with live GPS SOG;
the Pangoo gateway (src 64, S107-confirmed present) can also publish SOG from a lagged
or cached value. The two sources interleave. During a throttle change the Garmin sees
the new speed immediately; the Pangoo lags. The display alternates between the two
values every ~100–200 ms — the observed oscillation.

**Fix:** coalesce display updates to once per 250 ms. The SOG handler still sets
`_lastSogKts` immediately (so the COG suppression at line 152 keeps working), but
a 250 ms timer controls what appears on screen. Multiple updates arriving within
one 250 ms window are collapsed; only the most-recent value is rendered.

`[ASSUMED]` The root cause is multi-source interleaving. If on-boat testing after
this fix still shows flickering at the same rate, escalate — the root cause may instead
be a Signal K burst-retry behaviour and source filtering would be required.

---

### Issue 2 — Context menu title shows name only; no live value (lines 549–558)

`openCtx(e, name)` sets `ctxTtl.textContent = name` — just the cell label.
When the touchscreen menu opens it covers the gauge tile. Don cannot see the live
speed while the menu is displayed.

**Fix:** before setting the title, traverse from `e.target` to the nearest `.ic`
ancestor and read its `.ic-v` child's text. If the value is present and not `'---'`,
append it to the title: `"Speed SOG — 8.2"`. The gauge value is then visible in the
menu header even while the tile is covered.

This change applies to ALL cells (not just speed) because every `.ic` tile uses
`openCtx`. Every cell benefits.

---

## CURRENT STATE (derive from these exact lines — do not guess)

**State variables block (lines 123–126):**
```javascript
/* ── SIGNAL K HANDLERS ── */
let _gpsLat = null, _gpsLon = null;  // shared for waypoint distance calc
let _lastSogKts = null;
let _depthSource = null;  // 'keel' | 'transducer' | null — BUG-30
```

**SOG handler (lines 141–148) — inside `const SK_HANDLERS = {`:**
```javascript
  'navigation.speedOverGround': (v) => {
    const kts = (v * 1.944).toFixed(1);
    _lastSogKts = parseFloat(kts);
    _setVal('cellSpeed', kts);
    _setUnit('cellSpeed', 'kts · SOG');
    // Expose for position report
    const pr = document.querySelector('#posRpt .pr-big');
    if (pr) pr.textContent = kts + ' kts';
  },
```

**openCtx function (lines 549–558):**
```javascript
function openCtx(e, name) {
  e.preventDefault();
  e.stopPropagation();
  const m = document.getElementById('ctx');
  document.getElementById('ctxTtl').textContent = name;
  m.style.left = Math.min(e.clientX, window.innerWidth - 230) + 'px';
  m.style.top  = Math.max(e.clientY - 180, 60) + 'px';
  m.classList.add('show');
  setTimeout(() => document.addEventListener('click', hideCtx, { once: true }), 10);
}
```

---

## SPEC (paste this block to the Tier 3 model)

```
🔧 ATOMIC SPEC — BUG-13   (AAO §23.5 · §25 escalation-enabled)
═══════════════════════════════════════════════════════════════════════
TASK TYPE : [IMPLEMENT] — Tier 3
BUG       : BUG-13 — Speed gauge flickers during throttle transitions;
            context menu opens over gauge with no live value visible

FILE TO EDIT (exactly one)
  deployment/v0.9.9.4/opt/d3kos/services/dashboard/static/js/instruments.js

CHANGE A — Add two state variables immediately after `let _lastSogKts = null;`
  (current line 125 — after the line, before `let _depthSource`):

    let _sogPending    = null;   // BUG-13: coalesced value waiting to display
    let _sogDisplayTimer = null; // BUG-13: 250 ms coalesce timer handle

CHANGE B — Replace the entire SOG handler body
  (the 7-line block at lines 141–148 inside SK_HANDLERS):

  CURRENT:
    'navigation.speedOverGround': (v) => {
      const kts = (v * 1.944).toFixed(1);
      _lastSogKts = parseFloat(kts);
      _setVal('cellSpeed', kts);
      _setUnit('cellSpeed', 'kts · SOG');
      // Expose for position report
      const pr = document.querySelector('#posRpt .pr-big');
      if (pr) pr.textContent = kts + ' kts';
    },

  REPLACEMENT:
    'navigation.speedOverGround': (v) => {
      const kts = (v * 1.944).toFixed(1);
      _lastSogKts = parseFloat(kts);       // immediate — COG guard depends on this
      _sogPending = kts;                   // BUG-13: stage for coalesced display
      if (!_sogDisplayTimer) {             // BUG-13: start timer only if not already running
        _sogDisplayTimer = setTimeout(() => {
          _sogDisplayTimer = null;
          _setVal('cellSpeed', _sogPending);
          _setUnit('cellSpeed', 'kts · SOG');
          const pr = document.querySelector('#posRpt .pr-big');
          if (pr) pr.textContent = _sogPending + ' kts';
        }, 250);
      }
    },

CHANGE C — Replace the body of openCtx (lines 549–558):

  CURRENT:
    function openCtx(e, name) {
      e.preventDefault();
      e.stopPropagation();
      const m = document.getElementById('ctx');
      document.getElementById('ctxTtl').textContent = name;
      m.style.left = Math.min(e.clientX, window.innerWidth - 230) + 'px';
      m.style.top  = Math.max(e.clientY - 180, 60) + 'px';
      m.classList.add('show');
      setTimeout(() => document.addEventListener('click', hideCtx, { once: true }), 10);
    }

  REPLACEMENT:
    function openCtx(e, name) {
      e.preventDefault();
      e.stopPropagation();
      const m   = document.getElementById('ctx');
      const cell = e.target.closest('.ic');
      const valEl = cell && cell.querySelector('.ic-v');
      const live  = valEl && valEl.textContent !== '---' ? valEl.textContent : '';
      document.getElementById('ctxTtl').textContent = live ? name + ' — ' + live : name;
      m.style.left = Math.min(e.clientX, window.innerWidth - 230) + 'px';
      m.style.top  = Math.max(e.clientY - 180, 60) + 'px';
      m.classList.add('show');
      setTimeout(() => document.addEventListener('click', hideCtx, { once: true }), 10);
    }

  NOTE: — is the em-dash character (—). Use the Unicode escape, not a literal —,
  to avoid charset issues.

CONSTRAINT BOUNDARIES (do NOT)
  • Do NOT touch any other file — index.html, overlays.js, app.py, CSS.
  • Do NOT change _lastSogKts — it must still be set immediately (line preserved).
  • Do NOT remove or modify the COG guard at line 152.
  • Do NOT add a new setInterval or modify _init — the timer is fire-and-forget.
  • Do NOT change the units string 'kts · SOG'.
  • Do NOT add the timer to any other handler (depth, RPM, etc.) — SOG only.
  • Do NOT deploy to the Pi.

INTERFACE CONTRACT
  After Change A+B, with two rapid SOG updates arriving within 250 ms:
    → _lastSogKts reflects the LATEST raw value immediately
    → _sogPending reflects the LATEST raw value immediately
    → cellSpeed DOM text is NOT updated until 250 ms after the FIRST update
    → After 250 ms, cellSpeed shows _sogPending (the last value received)

  After Change C, with cellSpeed showing "8.2":
    → openCtx(event, 'Speed SOG') sets ctxTtl.textContent = 'Speed SOG — 8.2'

  After Change C, with cellSpeed showing "---":
    → openCtx(event, 'Speed SOG') sets ctxTtl.textContent = 'Speed SOG'

FAILING TESTS FIRST (TDD — write, RUN, watch fail, THEN fix)
  File: tests/bug13-speed-gauge.test.cjs
  Run : node tests/bug13-speed-gauge.test.cjs

  The test file must be CommonJS (.cjs) with an async main() pattern.
  Use the same mock-document pattern as tests/bug34-diag-panel.test.cjs.

  Required test cases (5):

  1. _lastSogKts set immediately (no debounce) — COG backward-compat
     Send one SOG update (4.115 m/s → 8.0 kts). Assert _lastSogKts === 8.0
     immediately after the call (no await needed).

  2. _sogPending holds latest value (coalescing works)
     Send two rapid SOG updates: 4.115 m/s (8.0 kts), then 1.543 m/s (3.0 kts).
     Assert _sogPending === '3.0' immediately (last value wins).
     Assert cellSpeed DOM text is NOT '3.0' yet (timer has not fired).

  3. After 300 ms, display reflects latest value (timer fires)
     Continue from test 2 state. Await 300 ms.
     Assert cellSpeed DOM text equals '3.0'.

  4. openCtx title includes live value when cell is populated
     Set up a mock .ic element with .ic-v.textContent = '8.2'.
     Call openCtx with e.target that traverses to this .ic.
     Assert ctxTtl.textContent === 'Speed SOG — 8.2'.

  5. openCtx title omits live value when cell shows ---
     Set .ic-v.textContent = '---'.
     Call openCtx.
     Assert ctxTtl.textContent === 'Speed SOG' (no dash, no ---).

  EXPECTED BEFORE THE FIX (tests 1-5 must all fail or error):
    test 1 — FAIL: _lastSogKts set to 8.0 — this one actually PASSES before fix
             (it tests existing behavior — use it as a regression guard)
    test 2 — FAIL: no _sogPending variable exists before Change A
    test 3 — FAIL: no debounce timer before Change B
    test 4 — FAIL: ctxTtl.textContent will be 'Speed SOG' (no live value appended)
    test 5 — PASS before fix (coincidentally correct — title is just the name)

  Tests 2 and 4 must flip from FAIL to PASS. Test 1 must PASS before and after.
  Test 5 must PASS before and after.
  Report the BEFORE run output even if only tests 2 and 4 fail.

DONE WHEN
  • Tests 2, 3, 4 FAIL before edit and PASS after.
  • Tests 1, 5 PASS before and after (regression).
  • git diff touches only instruments.js and the new test file.
  • No other variables or functions were modified.

ESCALATE-IF  (emit the 🔺 block — do not guess)
  • The instruments.js SOG handler looks materially different from the CURRENT block
    above (different line structure, additional logic, different variable names)
                                   → ADVICE (paste what you see; do not force the patch)
  • `_lastSogKts` is used anywhere other than the two places shown
    (line 125 declaration and line 152 COG guard)
                                   → ADVICE (list the usages; proceed with caution)
  • `e.target.closest` is not available (very old browser environment)
                                   → SOLUTION-REQUEST (describe environment; do not use polyfill)
  • The test runner cannot complete test 3 (async timer) in a .cjs file
                                   → ADVICE (describe the error; propose alternative)

PRE-FLIGHT SELF-CHECK
  1. How many files do I edit?             → exactly 1 (instruments.js)
  2. Do I modify any other handler?        → NO — SOG only
  3. Is _lastSogKts still set immediately? → YES — first line of the handler, unchanged
  4. Does openCtx still call preventDefault? → YES — line 1 of the replacement
  5. What proves done?                     → tests 2, 3, 4 flip fail → pass

RETURN TO TIER 1
  • The diff for instruments.js
  • node output showing BEFORE run (fail) then AFTER run (pass) for all 5 tests
  • Decision Log: any deviation, or "none"
═══════════════════════════════════════════════════════════════════════
```

---

## Tier-1 verification pass (§25.8)

1. `_lastSogKts` is set immediately — preserves COG suppression backward compat (line 152).
2. `_sogPending` coalesces rapid updates — only the most-recent value renders after 250 ms.
3. `_sogDisplayTimer` is a one-shot fire-and-forget per 250 ms window — no leaked timers, no interval.
4. `openCtx` change uses `e.target.closest('.ic')` — reliable traversal from any child element.
5. Guard `valEl.textContent !== '---'` prevents appending dash when no data present.
6. Em-dash `—` avoids charset issues in a JS string literal.
7. Tests 1 and 5 serve as regression guards — they must pass before AND after the fix.
8. ESCALATE-IF covers: handler mismatch, unexpected `_lastSogKts` usages, missing `.closest`, async test failure.

## Out of scope
Deploying to Pi · source filtering in the SK WebSocket subscription (would fix Issue 1 more permanently but requires changing the WS handshake — deferred to BUG-13v2 if the debounce proves insufficient) · changing the 250 ms interval · modifying any other gauge handler · adding debounce to depth/RPM/etc.
