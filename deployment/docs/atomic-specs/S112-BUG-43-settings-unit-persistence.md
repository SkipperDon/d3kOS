# Atomic Spec — BUG-43: Settings Unit Preference Persistence
**Version:** 1.0.0  
**Session:** S112 — 2026-07-31  
**Author:** Opus (Tier 1 architect)  
**Implementer:** Haiku (Tier 3)  
**Target files:** settings.html, instruments.js  
**Risk level:** LOW — browser-only JS + HTML, no backend changes, fully reversible via git  

---

## WHY THIS SPEC EXISTS

The d3kOS settings page has a "Units & Display" section with dropdowns for temperature, speed, distance, and a Metric/Imperial toggle. The "Save Display Settings" button currently does ONLY this:

```html
onclick="showToast('&#10003; Display settings saved')"
```

It shows a toast notification but NEVER saves anything. On the next page load, all dropdowns reset to defaults. The operator has no way to permanently switch between metric and imperial units.

**On-boat observation (S112 2026-07-31):** Operator confirmed imperial preference (°F, feet) but dashboard always shows °C and metres regardless.

---

## SCOPE OF THIS FIX (strictly bounded)

This fix implements unit persistence for the two most impactful conversions:
1. **Temperature:** Coolant temperature display — °C vs °F
2. **Depth:** Water depth display — metres vs feet

Speed and distance are explicitly OUT OF SCOPE for this sprint. Knots is the marine standard and is not changed. Distance in nm is the marine standard and is not changed.

The **Measurement System toggle** (`#met-tog`) is the primary control:
- Unchecked (default label "Imperial"): temperature in °F, depth in feet
- Checked (label "Metric"): temperature in °C, depth in metres

The individual dropdowns (`#tmp-u`, `#dist-u`, `#spd-u`, `#prs-u`) do NOT change this sprint. They continue to render but their values are not read by the save function.

**Why the toggle, not the dropdowns?**  
The operator uses the toggle (observed S112). The dropdowns are supplementary detail not wired to instruments.js. Wiring all dropdowns would require changing 4 instrument handlers — high risk for this sprint.

---

## WHAT HAIKU MUST NOT DO

- Do NOT touch any handler other than `coolantTemperature` and `_renderDepth` in instruments.js
- Do NOT change any threshold values
- Do NOT change any CSS
- Do NOT add new HTML elements to settings.html (no new inputs, no new buttons)
- Do NOT add a backend API call — localStorage only
- Do NOT change the `saveVesselSettings()` function
- Do NOT modify the `_skWs` connection logic
- Do NOT modify any other settings section (engine, alerts, AI, camera, etc.)

---

## PREREQUISITE: VERIFY STARTING STATE

**Check 1:** In settings.html, confirm line 145 reads exactly:
```html
          <button class="btn btn-primary" onclick="showToast('&#10003; Display settings saved')">&#128190; Save Display Settings</button>
```

**Check 2:** In instruments.js, confirm the coolant temperature handler (around line 183) reads exactly:
```js
  'propulsion.0.coolantTemperature': (v) => {
    const c = v - 273.15, disp = c.toFixed(0);
    window._d3kEngData.coolant_c = c;
    _setVal('cellCoolant', disp + '°');
```

**Check 3:** In instruments.js, confirm the `_renderDepth` function (around line 130) reads exactly:
```js
function _renderDepth(v, source) {
  // belowKeel always wins; never let a transducer value overwrite it
  if (source === 'transducer' && _depthSource === 'keel') return;
  _depthSource = source;
  window._d3kEngData.depth_m = parseFloat(v.toFixed(1));  // BUG-34
  _setVal('cellDepth', v.toFixed(1));
  const state = _evalBelow(v, THR.depth);
  _setCellState('cellDepth', state);
  const unit = source === 'keel' ? 'metres' : 'm · UNDER TRANSDUCER';
  _setUnit('cellDepth', state ? unit + ' · ' + state : unit);
}
```

If any check fails, STOP and report. Do not proceed.

---

## STEP 1 — instruments.js: Add unit preference loader

**File:** `deployment/v0.9.9.4/opt/d3kos/services/dashboard/static/js/instruments.js`

**What to find** — the module-level variables block. After the two lines added by BUG-42/45 spec (Step 1 of that spec), the block ends at approximately:

```js
window._oilCritAcknowledged = false;  // BUG-42: dismiss latch — set by closeCrit(), reset when oil recovers
```

**Insert the following TWO new lines immediately after** `window._oilCritAcknowledged = false;`:

```js
let _unitPrefs = { temp: 'F', depth: 'ft' };  // BUG-43: default imperial — loaded from localStorage in _init()
```

Note: Default is `F` and `ft` because the operator's documented preference is imperial.

**Verification:** Confirm `_unitPrefs` variable appears in the module-level variable declarations block (before the `SK_HANDLERS` object). Confirm default values are `'F'` and `'ft'`.

---

## STEP 2 — instruments.js: Load saved unit prefs in _init()

**File:** same as Step 1

**What to find** — the `_init()` function at the bottom of the file, approximately lines 573-580:

```js
function _init() {
  showRow('both');
  _markAllDash();       // clear demo values — SK will fill in once connected
  _connectSK();
  _pollWaypoint();
  setInterval(_pollWaypoint, WP_POLL_MS);
  _connectRouteSSE();
}
```

**Replace with:**
```js
function _init() {
  // BUG-43: load persisted unit preferences from settings page
  try {
    const saved = JSON.parse(localStorage.getItem('d3kUnitPrefs') || '{}');
    if (saved.temp  === 'C' || saved.temp  === 'F')  _unitPrefs.temp  = saved.temp;
    if (saved.depth === 'm' || saved.depth === 'ft') _unitPrefs.depth = saved.depth;
  } catch (_) {}
  showRow('both');
  _markAllDash();       // clear demo values — SK will fill in once connected
  _connectSK();
  _pollWaypoint();
  setInterval(_pollWaypoint, WP_POLL_MS);
  _connectRouteSSE();
}
```

**Critical details:**
- The `try/catch` around the localStorage read is REQUIRED. localStorage may be unavailable (private browsing, security policy). The catch silently uses the default `_unitPrefs` values.
- The `if` guards validate the saved value before applying it. Never apply an unknown string to `_unitPrefs`.
- The 5-line block before `showRow('both')` is the ONLY addition. No other line in `_init()` changes.

---

## STEP 3 — instruments.js: Apply temperature unit in coolant handler

**File:** same as Step 1

**What to find** — the `'propulsion.0.coolantTemperature'` handler, approximately lines 183-199:

```js
  'propulsion.0.coolantTemperature': (v) => {
    const c = v - 273.15, disp = c.toFixed(0);
    window._d3kEngData.coolant_c = c;
    _setVal('cellCoolant', disp + '°');
    const state = _evalAbove(c, THR.coolant);
    _setCellState('cellCoolant', state);
    _setUnit('cellCoolant', state ? 'C · ' + state + ' ↑ tap for AI' : 'C · normal');
    if (state === 'crit') {
      _setAlertTicker('⛔ CRITICAL — COOLANT ' + disp + '°C — REDUCE RPM NOW');
    } else if (state === 'alrt') {
      _setAlertTicker('⚠ ALERT — COOLANT ' + disp + '°C — REDUCE SPEED');
    } else if (state === 'adv') {
      _setAlertTicker('⚠ ADVISORY — COOLANT ' + disp + '°C — MONITOR');
    } else {
      _clearAlertTicker('COOLANT');
    }
  },
```

**Replace with:**
```js
  'propulsion.0.coolantTemperature': (v) => {
    const c = v - 273.15;
    window._d3kEngData.coolant_c = c;
    // BUG-43: apply user unit preference
    const disp = _unitPrefs.temp === 'F'
      ? Math.round(c * 9 / 5 + 32).toString()
      : c.toFixed(0);
    const unitSuffix = _unitPrefs.temp === 'F' ? '°F' : '°C';
    _setVal('cellCoolant', disp + '°');
    const state = _evalAbove(c, THR.coolant);  // threshold always in °C
    _setCellState('cellCoolant', state);
    _setUnit('cellCoolant', state ? unitSuffix + ' · ' + state + ' ↑ tap for AI' : unitSuffix + ' · normal');
    if (state === 'crit') {
      _setAlertTicker('⛔ CRITICAL — COOLANT ' + disp + unitSuffix + ' — REDUCE RPM NOW');
    } else if (state === 'alrt') {
      _setAlertTicker('⚠ ALERT — COOLANT ' + disp + unitSuffix + ' — REDUCE SPEED');
    } else if (state === 'adv') {
      _setAlertTicker('⚠ ADVISORY — COOLANT ' + disp + unitSuffix + ' — MONITOR');
    } else {
      _clearAlertTicker('COOLANT');
    }
  },
```

**Critical details:**
- `_evalAbove(c, THR.coolant)` uses `c` (Celsius). Thresholds are in °C. This does NOT change.
- `_d3kEngData.coolant_c = c` stores °C always. The diagnostic panel reads this for Gemini. This does NOT change.
- The displayed value (`disp`) and unit label change based on `_unitPrefs.temp`.
- `disp + '°'` keeps the degree symbol separate from the unit label — the cell shows "195°" and the unit shows "°F · normal" in the `.ic-u` element.
- Alert ticker messages include the unit suffix for clarity.
- The variable `c` is still declared but `disp` is now computed on the next line (not on the same line as `c`). This is a minor restructuring; verify the logic is preserved.

---

## STEP 4 — instruments.js: Apply depth unit in _renderDepth

**File:** same as Step 1

**What to find** — the `_renderDepth` function, approximately lines 130-140:

```js
function _renderDepth(v, source) {
  // belowKeel always wins; never let a transducer value overwrite it
  if (source === 'transducer' && _depthSource === 'keel') return;
  _depthSource = source;
  window._d3kEngData.depth_m = parseFloat(v.toFixed(1));  // BUG-34
  _setVal('cellDepth', v.toFixed(1));
  const state = _evalBelow(v, THR.depth);
  _setCellState('cellDepth', state);
  const unit = source === 'keel' ? 'metres' : 'm · UNDER TRANSDUCER';
  _setUnit('cellDepth', state ? unit + ' · ' + state : unit);
}
```

**Replace with:**
```js
function _renderDepth(v, source) {
  // belowKeel always wins; never let a transducer value overwrite it
  if (source === 'transducer' && _depthSource === 'keel') return;
  _depthSource = source;
  window._d3kEngData.depth_m = parseFloat(v.toFixed(1));  // BUG-34: always store metres
  // BUG-43: display in user's preferred unit
  const dispVal  = _unitPrefs.depth === 'ft' ? (v * 3.28084).toFixed(1) : v.toFixed(1);
  const dispUnit = _unitPrefs.depth === 'ft'
    ? (source === 'keel' ? 'feet' : 'ft · UNDER TRANSDUCER')
    : (source === 'keel' ? 'metres' : 'm · UNDER TRANSDUCER');
  _setVal('cellDepth', dispVal);
  const state = _evalBelow(v, THR.depth);  // threshold in metres always
  _setCellState('cellDepth', state);
  _setUnit('cellDepth', state ? dispUnit + ' · ' + state : dispUnit);
}
```

**Critical details:**
- `window._d3kEngData.depth_m` stores metres always. This does NOT change. Gemini diagnostic uses this.
- `_evalBelow(v, THR.depth)` uses `v` (metres). Thresholds are in metres. This does NOT change.
- The displayed value `dispVal` and unit label `dispUnit` change based on `_unitPrefs.depth`.
- Conversion factor for feet: `1 metre = 3.28084 feet`. Use this exact value.

---

## STEP 5 — settings.html: Wire Save Display Settings button

**File:** `deployment/v0.9.9.4/opt/d3kos/services/dashboard/templates/settings.html`

**What to find** (line 145):
```html
          <button class="btn btn-primary" onclick="showToast('&#10003; Display settings saved')">&#128190; Save Display Settings</button>
```

**Replace with:**
```html
          <button class="btn btn-primary" onclick="saveDisplaySettings()">&#128190; Save Display Settings</button>
```

**Verification:** Confirm only the `onclick` attribute changed. The button text, class, and surrounding HTML are unchanged.

---

## STEP 6 — settings.html: Add saveDisplaySettings() function

**File:** same as Step 5

**What to find** — the end of the first `<script>` block in settings.html. The last function in that block is `saveVesselSettings()`. Find this exact closing sequence (approximately lines 1032-1036):

```js
    function saveVesselSettings() {
      const name = (document.getElementById('vessel-name').value || '').trim();
      const port = (document.getElementById('home-port').value  || '').trim();
      if (!name) { showToast('✗ Vessel name is required'); return; }
      fetch('/api/settings/vessel', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({vessel_name: name, home_port: port})
      })
      .then(r => r.json())
      .then(d => showToast(d.ok ? '✓ Vessel settings saved' : '✗ ' + d.error))
      .catch(() => showToast('✗ Save failed — check connection'));
    }

  </script>
```

**Insert the `saveDisplaySettings` function BEFORE the closing `</script>` tag.** Add it after `saveVesselSettings()` ends, before `</script>`:

```js
    function saveDisplaySettings() {
      // Read the Measurement System toggle — this is the primary unit control
      // Unchecked = Imperial (°F, feet), Checked = Metric (°C, metres)
      const isMetric = document.getElementById('met-tog').checked;
      const prefs = {
        temp:  isMetric ? 'C' : 'F',
        depth: isMetric ? 'm' : 'ft'
      };
      try {
        localStorage.setItem('d3kUnitPrefs', JSON.stringify(prefs));
        showToast('✓ Display settings saved — reload dashboard to apply');
      } catch (_) {
        showToast('✗ Could not save settings — storage unavailable');
      }
    }
```

**Verification:** 
- Confirm `saveDisplaySettings` is INSIDE the `<script>` block (before `</script>`)
- Confirm it appears AFTER `saveVesselSettings()`
- Confirm `saveVesselSettings()` is unchanged
- Confirm the `</script>` tag still closes the block

---

## STEP 7 — settings.html: Set default toggle state to unchecked (Imperial)

**File:** same as Step 5

**What to find** (around line 137):
```html
                <input type="checkbox" id="met-tog" onchange="document.getElementById('met-lbl').textContent=this.checked?'Metric':'Imperial'">
```

**What to check:** Is `checked` attribute present on this input? If it is, remove it. If it is not present, no change needed.

Current state from file read: the input does NOT have the `checked` attribute. The label text defaults to "Imperial". No change needed to this element.

**Verification:** Read line ~137 of settings.html. Confirm `id="met-tog"` element does NOT have `checked` attribute. Confirm label `id="met-lbl"` shows "Imperial" by default (it does — the label text on line 140 is `Imperial`).

This step is CONFIRM ONLY — no edit needed.

---

## STEP 8 — VERIFICATION CHECKLIST

**instruments.js:**
- [ ] `let _unitPrefs = { temp: 'F', depth: 'ft' };` exists in module scope
- [ ] `_init()` contains `localStorage.getItem('d3kUnitPrefs')` in a try/catch
- [ ] `_init()` validates `saved.temp` is `'C'` or `'F'` before applying
- [ ] `_init()` validates `saved.depth` is `'m'` or `'ft'` before applying
- [ ] Coolant handler: `_unitPrefs.temp === 'F'` branch applies `c * 9 / 5 + 32` conversion
- [ ] Coolant handler: `_evalAbove(c, THR.coolant)` still uses raw Celsius `c`
- [ ] `_renderDepth`: `_unitPrefs.depth === 'ft'` branch applies `v * 3.28084` conversion
- [ ] `_renderDepth`: `_evalBelow(v, THR.depth)` still uses raw metres `v`
- [ ] `_d3kEngData.depth_m` still stores metres (not feet)
- [ ] `_d3kEngData.coolant_c` still stores Celsius (not Fahrenheit)
- [ ] Battery, fuel, RPM, speed, course, position handlers UNCHANGED

**settings.html:**
- [ ] "Save Display Settings" button calls `saveDisplaySettings()` (not `showToast`)
- [ ] `saveDisplaySettings()` function exists in the `<script>` block
- [ ] `saveDisplaySettings()` reads `#met-tog` checkbox state
- [ ] `saveDisplaySettings()` saves to `localStorage.setItem('d3kUnitPrefs', ...)`
- [ ] `saveDisplaySettings()` shows toast with "reload dashboard to apply" message
- [ ] `saveVesselSettings()` is UNCHANGED

---

## STEP 9 — FUNCTIONAL TEST SCENARIOS

**Test 1 — Save imperial preference**
1. Open `localhost:3000/settings` → Units & Display section
2. Verify Measurement System toggle shows "Imperial" (unchecked is default)
3. Tap "Save Display Settings"
4. Expected: Toast shows "✓ Display settings saved — reload dashboard to apply"
5. Open browser dev tools → Application → Local Storage → `localhost:3000`
6. Expected: Key `d3kUnitPrefs` = `{"temp":"F","depth":"ft"}`
7. Pass criteria: key exists with correct values

**Test 2 — Dashboard applies imperial units**
1. Open `localhost:3000` (dashboard)
2. Wait for SK to connect and send coolant/depth data
3. Expected: Coolant cell shows value in °F (e.g., "195°" with unit "°F · normal")
4. Expected: Depth cell shows value in feet (e.g., "3.0" with unit "feet")
5. Pass criteria: Both cells show imperial values

**Test 3 — Switch to metric**
1. Open `localhost:3000/settings` → Units & Display
2. Toggle Measurement System to "Metric" (check the toggle)
3. Tap "Save Display Settings"
4. Expected: Toast confirms save
5. Open `localhost:3000` → reload
6. Expected: Coolant in °C, depth in metres
7. Pass criteria: Both cells show metric values

**Test 4 — Threshold still works correctly**
1. While in imperial mode, verify the oil pressure critical at 4 PSI still triggers (unchanged)
2. Verify depth advisory at 3m triggers (SK sends depth in metres, threshold is in metres)
3. Note: Threshold in metres (3m) = 9.84 feet. When displaying in feet, cell will show "2.9 ft" when threshold fires. This is correct — the threshold evaluates on raw metres.
4. Pass criteria: Depth cell turns yellow (advisory) when depth < 3m, even though display shows feet

**Test 5 — Settings survive page reload**
1. Set to imperial, save, reload dashboard
2. Reload dashboard again
3. Expected: Still showing imperial units after second reload
4. Pass criteria: localStorage persists across reloads (it does by design)

---

## ROLLBACK PROCEDURE

If anything breaks:

```bash
cd /home/boatiq/Helm-OS
git checkout deployment/v0.9.9.4/opt/d3kos/services/dashboard/static/js/instruments.js
git checkout deployment/v0.9.9.4/opt/d3kos/services/dashboard/templates/settings.html
```

To clear saved preferences from the browser (so defaults restore):
- Open browser dev tools → Application → Local Storage → delete `d3kUnitPrefs` key

---

## COMMIT INSTRUCTIONS

After all tests pass, commit with:

```
S112: BUG-43 — settings unit preference persistence (imperial °F/ft default)

Wire Save Display Settings to localStorage. Dashboard reads prefs on init.
Coolant display: °C ↔ °F. Depth display: metres ↔ feet.
Thresholds remain in SI units internally.
```

Stage only these two files:
- `deployment/v0.9.9.4/opt/d3kos/services/dashboard/static/js/instruments.js`
- `deployment/v0.9.9.4/opt/d3kos/services/dashboard/templates/settings.html`

Note: instruments.js is also modified by the BUG-42/44/45 spec. Both specs modify this file. Do the BUG-42/44/45 spec FIRST, then apply BUG-43 changes to the already-modified file. All changes are in different sections and do not conflict.
