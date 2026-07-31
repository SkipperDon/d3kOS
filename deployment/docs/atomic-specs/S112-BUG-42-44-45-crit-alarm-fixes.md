# Atomic Spec — BUG-42, BUG-44, BUG-45: Critical Alarm System Fixes
**Version:** 1.0.0  
**Session:** S112 — 2026-07-31  
**Author:** Opus (Tier 1 architect)  
**Implementer:** Haiku (Tier 3)  
**Target files:** instruments.js, overlays.js  
**Risk level:** LOW — browser-only JS, no backend, fully reversible via git  

---

## WHY THIS SPEC EXISTS (read before touching any code)

Three separate bugs caused a broken alarm experience on the boat on 2026-07-31:

- **BUG-45:** Oil pressure critical alarm fires on every Pi boot before the engine starts, because Pangoo sends 0 PSI when the engine is off and there is no startup gate.
- **BUG-42:** The ACKNOWLEDGE button dismisses the overlay but it immediately re-appears because `showCrit()` is called unconditionally on every SK delta (≤1 second apart) with no acknowledgement latch.
- **BUG-44:** The `showCrit()` function only shows a visual overlay — it never calls the TTS endpoint at port 3002, so the voice alarm is silent.

These three bugs interact. All three must be fixed together in the exact order below.

**Root cause summary:**
```
instruments.js line 210:  if (typeof showCrit === 'function') showCrit();
```
This call has NO gates: no engine-running check (BUG-45), no latch check (BUG-42).

```
overlays.js lines 128-144: showCrit() / closeCrit()
```
`showCrit()` has no TTS call (BUG-44). `closeCrit()` sets no latch (BUG-42).

---

## WHAT HAIKU MUST NOT DO

- Do NOT touch any file not listed in this spec
- Do NOT change threshold values (THR.oil, THR.coolant, etc.)
- Do NOT change the HTML in index.html
- Do NOT change CSS
- Do NOT add any new HTML elements
- Do NOT change any handler other than `propulsion.0.oilPressure`
- Do NOT touch the battery, fuel, coolant, or depth handlers
- If any step produces a syntax error, STOP and report — do not guess a fix

---

## PREREQUISITE: VERIFY STARTING STATE

Before making any change, Haiku MUST verify each of these is true.
If any fails, STOP and report to Sonnet.

**Check 1:** In instruments.js, confirm line 210 reads exactly:
```
      if (typeof showCrit === 'function') showCrit();
```

**Check 2:** In overlays.js, confirm lines 128-135 read exactly:
```js
function showCrit() {
  document.getElementById('critSc').classList.add('show');
  const ticker = document.getElementById('ticker');
  if (ticker) {
    ticker.textContent = '⛔ CRITICAL ENGINE ALARM — SHUT DOWN ENGINE IMMEDIATELY';
    ticker.classList.add('hot');
  }
}
```

**Check 3:** In overlays.js, confirm lines 137-144 read exactly:
```js
function closeCrit() {
  document.getElementById('critSc').classList.remove('show');
  const ticker = document.getElementById('ticker');
  if (ticker) {
    ticker.classList.remove('hot');
    ticker.textContent = TICKS[0];
  }
}
```

**Check 4:** In instruments.js, confirm the module-level variables block around lines 124-128 reads:
```js
let _gpsLat = null, _gpsLon = null;  // shared for waypoint distance calc
let _lastSogKts = null;
let _sogPending    = null;   // BUG-13: coalesced value waiting to display
let _sogDisplayTimer = null; // BUG-13: 250 ms coalesce timer handle
let _depthSource = null;  // 'keel' | 'transducer' | null — BUG-30
```

---

## STEP 1 — instruments.js: Add boot-debounce variable and latch variable

**File:** `deployment/v0.9.9.4/opt/d3kos/services/dashboard/static/js/instruments.js`

**What to find** (around line 128, immediately after `let _depthSource = null;`):
```js
let _depthSource = null;  // 'keel' | 'transducer' | null — BUG-30
```

**What to insert AFTER that line** (two new lines, no existing lines removed):
```js
let _skFirstConnectAt = null;  // BUG-45: timestamp when SK WS first opens this session
window._oilCritAcknowledged = false;  // BUG-42: dismiss latch — set by closeCrit(), reset when oil recovers
```

**Result after edit** (lines 128-131 should read):
```js
let _depthSource = null;  // 'keel' | 'transducer' | null — BUG-30
let _skFirstConnectAt = null;  // BUG-45: timestamp when SK WS first opens this session
window._oilCritAcknowledged = false;  // BUG-42: dismiss latch — set by closeCrit(), reset when oil recovers
```

**Verification:** Open instruments.js and confirm the two new lines appear immediately after `_depthSource`. No other lines changed.

---

## STEP 2 — instruments.js: Set the boot timer in _skWs.onopen

**File:** same as Step 1

**What to find** — the `_skWs.onopen` handler (around line 317). It currently reads:
```js
  _skWs.onopen = () => {
    clearTimeout(_skReconnectTimer);
    if (_skOfflineMsg) {
      _skOfflineMsg = false;
      const el = document.getElementById('ticker');
      if (el && !el.classList.contains('hot') && !_alertTickerMsg) {
        el.style.color = '';
        el.textContent = typeof TICKS !== 'undefined' ? TICKS[0]
                       : 'AI FIRST OFFICER ACTIVE — ALL SYSTEMS NOMINAL';
      }
    }
  };
```

**What to change:** Insert TWO new lines immediately after `clearTimeout(_skReconnectTimer);`:
```js
    if (!_skFirstConnectAt) _skFirstConnectAt = Date.now();  // BUG-45: record first connect only
    window._oilCritAcknowledged = false;  // BUG-42: reset latch on reconnect
```

**Result after edit** — the `_skWs.onopen` handler should read:
```js
  _skWs.onopen = () => {
    clearTimeout(_skReconnectTimer);
    if (!_skFirstConnectAt) _skFirstConnectAt = Date.now();  // BUG-45: record first connect only
    window._oilCritAcknowledged = false;  // BUG-42: reset latch on reconnect
    if (_skOfflineMsg) {
      _skOfflineMsg = false;
      const el = document.getElementById('ticker');
      if (el && !el.classList.contains('hot') && !_alertTickerMsg) {
        el.style.color = '';
        el.textContent = typeof TICKS !== 'undefined' ? TICKS[0]
                       : 'AI FIRST OFFICER ACTIVE — ALL SYSTEMS NOMINAL';
      }
    }
  };
```

**Verification:** Confirm the two new lines are the ONLY change in the `_skWs.onopen` block. Confirm `clearTimeout(_skReconnectTimer);` is still the first line inside the block.

---

## STEP 3 — instruments.js: Replace the oil pressure handler

**File:** same as Step 1

**What to find** — the entire `'propulsion.0.oilPressure'` handler, lines 201-216:
```js
  'propulsion.0.oilPressure': (v) => {
    const psi = Math.round(v * 0.000145038);
    window._d3kEngData.oil_psi = psi;
    _setVal('cellOil', psi.toString());
    const state = _evalBelow(psi, THR.oil);
    _setCellState('cellOil', state);
    _setUnit('cellOil', state ? 'PSI · ' + state : 'PSI · normal');
    if (state === 'crit') {
      _setAlertTicker('⛔ CRITICAL — OIL PRESSURE ' + psi + ' PSI — TAKE ACTION NOW');
      if (typeof showCrit === 'function') showCrit();
    } else if (state) {
      _setAlertTicker('⚠ ' + state.toUpperCase() + ' — OIL PRESSURE ' + psi + ' PSI');
    } else {
      _clearAlertTicker('OIL PRESSURE');
    }
  },
```

**Replace the entire handler with this exact text:**
```js
  'propulsion.0.oilPressure': (v) => {
    const psi = Math.round(v * 0.000145038);
    window._d3kEngData.oil_psi = psi;
    _setVal('cellOil', psi.toString());
    const state = _evalBelow(psi, THR.oil);
    _setCellState('cellOil', state);
    _setUnit('cellOil', state ? 'PSI · ' + state : 'PSI · normal');
    if (state === 'crit') {
      _setAlertTicker('⛔ CRITICAL — OIL PRESSURE ' + psi + ' PSI — TAKE ACTION NOW');
      // BUG-45: only fire after 30s boot debounce (prevents false alarm on Pi start)
      // BUG-42: only fire if operator has not already acknowledged this alarm
      const debounced = _skFirstConnectAt && (Date.now() - _skFirstConnectAt >= 30000);
      if (debounced && !window._oilCritAcknowledged) {
        if (typeof showCrit === 'function') showCrit();
      }
    } else if (state) {
      _setAlertTicker('⚠ ' + state.toUpperCase() + ' — OIL PRESSURE ' + psi + ' PSI');
      window._oilCritAcknowledged = false;  // BUG-42: reset latch when pressure recovers to advisory/alert
    } else {
      _clearAlertTicker('OIL PRESSURE');
      window._oilCritAcknowledged = false;  // BUG-42: reset latch when pressure returns to normal
    }
  },
```

**Critical details Haiku MUST verify:**
1. The latch reset (`window._oilCritAcknowledged = false`) appears in BOTH the `else if (state)` branch AND the `else` branch. This is intentional — reset happens any time pressure rises above critical.
2. The `debounced` check uses `_skFirstConnectAt` (not `Date.now()` directly). This variable is set once when SK first connects and never changes after that.
3. The conversion `v * 0.000145038` is UNCHANGED — do not modify it.
4. The `_evalBelow`, `_setVal`, `_setCellState`, `_setUnit`, `_setAlertTicker`, `_clearAlertTicker` calls are UNCHANGED.

**What the 30-second gate means:**
- First 30s after SK connects: oil pressure cell shows crit state (red) but `showCrit()` does NOT fire
- After 30s: if oil pressure is still critical, `showCrit()` fires on the next SK delta
- If operator acknowledges: `showCrit()` never fires again until oil pressure recovers above critical threshold
- If oil pressure recovers: latch resets; alarm can fire again if pressure drops back into critical

---

## STEP 4 — overlays.js: Replace showCrit() and closeCrit()

**File:** `deployment/v0.9.9.4/opt/d3kos/services/dashboard/static/js/overlays.js`

**What to find** — the entire critical screen section, lines 127-144:
```js
/* ── CRITICAL SCREEN ── */
function showCrit() {
  document.getElementById('critSc').classList.add('show');
  const ticker = document.getElementById('ticker');
  if (ticker) {
    ticker.textContent = '⛔ CRITICAL ENGINE ALARM — SHUT DOWN ENGINE IMMEDIATELY';
    ticker.classList.add('hot');
  }
}

function closeCrit() {
  document.getElementById('critSc').classList.remove('show');
  const ticker = document.getElementById('ticker');
  if (ticker) {
    ticker.classList.remove('hot');
    ticker.textContent = TICKS[0];
  }
}
```

**Replace with this exact text:**
```js
/* ── CRITICAL SCREEN ── */
function showCrit() {
  document.getElementById('critSc').classList.add('show');
  const ticker = document.getElementById('ticker');
  if (ticker) {
    ticker.textContent = '⛔ CRITICAL ENGINE ALARM — SHUT DOWN ENGINE IMMEDIATELY';
    ticker.classList.add('hot');
  }
  // BUG-44: trigger voice alarm via ai-bridge TTS
  fetch('http://' + window.location.hostname + ':3002/webhook/alert', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ message: 'Critical engine alarm. Oil pressure is critically low. Shut down engine immediately.', severity: 'critical' })
  }).catch(function() {});  // fire-and-forget — never block the UI
}

function closeCrit() {
  document.getElementById('critSc').classList.remove('show');
  const ticker = document.getElementById('ticker');
  if (ticker) {
    ticker.classList.remove('hot');
    ticker.textContent = TICKS[0];
  }
  // BUG-42: set latch so showCrit() cannot re-fire until oil pressure recovers above critical
  if (typeof window._oilCritAcknowledged !== 'undefined') window._oilCritAcknowledged = true;
}
```

**Critical details Haiku MUST verify:**
1. The fetch in `showCrit()` uses `window.location.hostname` — NOT hardcoded `localhost`. This is intentional: the dashboard must work from the Pi's IP address on a phone/tablet.
2. The `.catch(function() {})` is REQUIRED — the TTS endpoint may be offline and must never crash the UI.
3. Do NOT use `async/await` — the function is not async and cannot be changed to async without breaking the caller in instruments.js.
4. In `closeCrit()`, the latch is set via `window._oilCritAcknowledged` (the same global defined in instruments.js). The `typeof` guard is required because overlays.js loads independently.
5. The comment block `/* ── CRITICAL SCREEN ── */` is UNCHANGED.

---

## STEP 5 — VERIFICATION SCRIPT (run after all edits)

Haiku must verify each of these by reading the final state of the files:

**instruments.js verification checklist:**
- [ ] Line after `let _depthSource = null;`: `let _skFirstConnectAt = null;` exists
- [ ] Line after `_skFirstConnectAt`: `window._oilCritAcknowledged = false;` exists
- [ ] Inside `_skWs.onopen`, after `clearTimeout(_skReconnectTimer);`: two new lines for `_skFirstConnectAt` and `_oilCritAcknowledged` reset
- [ ] `'propulsion.0.oilPressure'` handler: contains `_skFirstConnectAt` reference
- [ ] `'propulsion.0.oilPressure'` handler: contains `window._oilCritAcknowledged` reference
- [ ] `'propulsion.0.oilPressure'` handler: `window._oilCritAcknowledged = false;` appears in BOTH the `else if` and `else` branches
- [ ] NO changes to battery, coolant, fuel, depth, speed, course, position handlers
- [ ] NO changes to THR object values

**overlays.js verification checklist:**
- [ ] `showCrit()` body: contains `fetch('http://' + window.location.hostname + ':3002/webhook/alert'`
- [ ] `showCrit()` body: fetch has `.catch(function() {})` 
- [ ] `showCrit()` body: severity is `'critical'`
- [ ] `closeCrit()` body: contains `window._oilCritAcknowledged = true;`
- [ ] `closeCrit()` body: the assignment is guarded by `typeof window._oilCritAcknowledged !== 'undefined'`
- [ ] NO other functions in overlays.js changed

---

## STEP 6 — FUNCTIONAL TEST SCENARIOS

After deploying to lab Pi, Haiku must validate each scenario:

**Test 1 — Boot false-alarm suppression (BUG-45)**
- Procedure: Reboot Pi. Open dashboard immediately. Watch for first 30 seconds.
- Expected: Oil pressure cell turns red (crit state) but the full-screen overlay does NOT appear.
- After 30 seconds: if oil pressure is still reading 0 PSI, the overlay fires.
- Pass criteria: NO overlay in first 30 seconds.

**Test 2 — Latch prevents re-fire (BUG-42)**
- Procedure: Wait until after 30-second window (or skip by temporarily changing 30000 to 5000 for test). When overlay appears, tap ACKNOWLEDGE.
- Expected: Overlay closes. Does NOT re-appear on next SK update (within 1-5 seconds).
- Overlay should remain closed until oil pressure rises above 4 PSI (the crit threshold).
- Pass criteria: ACKNOWLEDGE closes the overlay and it stays closed.

**Test 3 — Latch resets when pressure recovers**
- Procedure: After acknowledging, simulate oil pressure recovery by sending a SK delta with value > 4 PSI. In lab this can be done by stopping and restarting Pangoo or manually injecting a SK value.
- Alternative: If Pangoo is not available in lab, open browser console and run:
  ```js
  window._oilCritAcknowledged = false;
  ```
  Then observe that the overlay fires again on the next oil pressure delta (after waiting for the 30s window to elapse).
- Pass criteria: After reset, overlay fires again when oil pressure is critical.

**Test 4 — TTS fires (BUG-44)**
- Procedure: Wait for overlay to fire (after 30s window).
- Expected: espeak-ng voice announces "Critical engine alarm. Oil pressure is critically low. Shut down engine immediately."
- Verify ai-bridge is running: `systemctl status d3kos-ai-bridge`
- Verify TTS is not muted: `cat /opt/d3kos/config/tts-mute.json`
- Pass criteria: Voice alarm heard within 1-2 seconds of overlay appearing.

**Test 5 — Regression check**
- Open dashboard and verify ALL of these cells still show data normally:
  - Depth: shows live depth reading
  - Battery: shows live voltage
  - Fuel: shows live percentage
  - Speed/Course/Position: show live navigation data
- None of these should be affected by this change.
- Pass criteria: All cells show `---` until SK connects, then show live values as before.

---

## KNOWN CONSTRAINTS (do not work around these)

1. **RPM = 0 on this boat** — Pangoo's tachometer input wire is disconnected. `window._d3kEngData.rpm` will always be 0 (not null), even when engine is running. The debounce gate uses time, not RPM, specifically because of this hardware limitation.

2. **SK delta frequency** — SK sends deltas only when values CHANGE. If Pangoo sends a constant 0 PSI, SK may send infrequent deltas. The latch system still works because once the overlay fires (at T+30s), the latch prevents re-fire until pressure recovers.

3. **TTS silence is not an error** — If ai-bridge is not running, the fetch `.catch()` silently swallows the error. The visual alarm is unaffected. Do not add error handling beyond what is specified.

4. **CX5106 is absent from N2K bus** — The only source of engine data is Pangoo (src 64). Oil pressure readings of 0 PSI are real (Pangoo reads 0 when engine is off). The debounce is not a workaround for bad data — it is a time-gate that prevents alarming before the engine has had time to start and build pressure.

---

## ROLLBACK PROCEDURE

If any test fails or the dashboard breaks:

```bash
cd /home/boatiq/Helm-OS
git checkout deployment/v0.9.9.4/opt/d3kos/services/dashboard/static/js/instruments.js
git checkout deployment/v0.9.9.4/opt/d3kos/services/dashboard/static/js/overlays.js
```

This restores both files to the pre-fix state. The cell states (red/yellow) will still show but the overlay and TTS behavior reverts to the original broken behavior.

---

## COMMIT INSTRUCTIONS

After all tests pass, commit with:

```
S112: BUG-42/44/45 — oil pressure crit alarm: boot debounce + dismiss latch + TTS

BUG-45: 30s boot gate in _skWs.onopen prevents false critical on Pi start
BUG-42: _oilCritAcknowledged latch prevents re-fire after ACKNOWLEDGE tap  
BUG-44: showCrit() now POSTs to ai-bridge :3002/webhook/alert for TTS voice
```

Stage only these two files:
- `deployment/v0.9.9.4/opt/d3kos/services/dashboard/static/js/instruments.js`
- `deployment/v0.9.9.4/opt/d3kos/services/dashboard/static/js/overlays.js`
