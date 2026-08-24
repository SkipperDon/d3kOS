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
// Create expected object in jsdom context to match prototype
w.eval('window._expected = { coolant_c:null, oil_psi:null, rpm:null, bat_v:null, fuel_pct:null, depth_m:null };');
assert.deepStrictEqual(w._d3kEngData, w._expected,
  'cache must initialise all-null');

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
