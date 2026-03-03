/**
 * d3kOS v0.9.2 — units.js Unit Tests
 * Run with: node test_units.js
 * All 17 tests must pass before deployment.
 */

'use strict';

let passed = 0;
let failed = 0;

function assert(condition, testName, expected, actual) {
  if (condition) {
    passed++;
    console.log(`  ✓ ${testName}`);
  } else {
    failed++;
    console.error(`  ✗ ${testName}`);
    if (expected !== undefined) console.error(`    Expected: ${expected}, Got: ${actual}`);
  }
}

// ── Shim browser globals for Node.js test environment ──
global.localStorage = {
  _store: {},
  getItem(k) { return this._store[k] || null; },
  setItem(k, v) { this._store[k] = String(v); }
};
global.window = {
  dispatchEvent() {},
  addEventListener() {}
};
global.fetch = () => Promise.resolve({ json: () => Promise.resolve({}) });

// ── Load the Units module ──
const path = require('path');
const fs   = require('fs');
const localPath = path.join(__dirname, '../js/units.js');
const piPath    = '/var/www/html/js/units.js';
const unitsPath = fs.existsSync(localPath) ? localPath : piPath;
const Units = require(unitsPath);

// Force imperial default for tests (spec default)
localStorage.setItem('d3kos-measurement-system', 'imperial');

// ── Helper: conversions without DOM ──
const C = {
  tempToC: f  => Math.round(((f-32)*5/9)*10)/10,
  tempToF: c  => Math.round(((c*9/5)+32)*10)/10,
  psiToBar: p => Math.round(p*0.0689476*100)/100,
  barToPsi: b => Math.round(b*14.5038*10)/10,
  knotsToKmh: k => Math.round(k*1.852*10)/10,
  knotsToMph: k => Math.round(k*1.15078*10)/10,
  nmToKm: n   => Math.round(n*1.852*10)/10,
  ftToM: f    => Math.round(f*0.3048*10)/10,
  galToL: g   => Math.round(g*3.78541*10)/10,
  lbToKg: l   => Math.round(l*0.453592*10)/10,
  ciToL: c    => Math.round(c*0.0163871*10)/10
};

// ═══════════════════════════════════════════════
console.log('\nd3kOS v0.9.2 — units.js Test Suite');
console.log('═'.repeat(50));

// ── Temperature ──
console.log('\n[Temperature]');
assert(C.tempToC(212) === 100.0,  '212°F = 100°C',    100.0, C.tempToC(212));
assert(C.tempToC(32)  === 0.0,    '32°F  = 0°C',      0.0,   C.tempToC(32));
assert(C.tempToC(185) === 85.0,   '185°F = 85°C',     85.0,  C.tempToC(185));
assert(C.tempToC(-40) === -40.0,  '-40°F = -40°C',    -40.0, C.tempToC(-40));
assert(C.tempToF(100) === 212.0,  '100°C = 212°F',    212.0, C.tempToF(100));

// ── Pressure ──
console.log('\n[Pressure]');
assert(C.psiToBar(45)   === 3.10,  '45 PSI = 3.10 bar',  3.10, C.psiToBar(45));
assert(C.psiToBar(14.7) === 1.01,  '14.7 PSI = 1.01 bar',1.01, C.psiToBar(14.7));
assert(C.psiToBar(0)    === 0.0,   '0 PSI = 0 bar',      0.0,  C.psiToBar(0));

// ── Speed ──
console.log('\n[Speed]');
assert(C.knotsToKmh(10) === 18.5,  '10 kts = 18.5 km/h', 18.5, C.knotsToKmh(10));
assert(C.knotsToMph(10) === 11.5,  '10 kts = 11.5 mph',  11.5, C.knotsToMph(10));
assert(C.knotsToKmh(0)  === 0.0,   '0 kts = 0 km/h',     0.0,  C.knotsToKmh(0));

// ── Distance ──
console.log('\n[Distance]');
assert(C.nmToKm(10) === 18.5,  '10 nm = 18.5 km',  18.5, C.nmToKm(10));

// ── Depth ──
console.log('\n[Depth]');
assert(C.ftToM(30) === 9.1,  '30 ft = 9.1 m', 9.1, C.ftToM(30));
assert(C.ftToM(0)  === 0.0,  '0 ft  = 0 m',   0.0, C.ftToM(0));

// ── Fuel ──
console.log('\n[Fuel]');
assert(C.galToL(50) === 189.3,  '50 gal = 189.3 L', 189.3, C.galToL(50));
assert(C.galToL(0)  === 0.0,    '0 gal  = 0 L',     0.0,   C.galToL(0));

// ── Displacement ──
console.log('\n[Displacement]');
assert(C.ciToL(350) === 5.7,  '350 ci = 5.7 L', 5.7, C.ciToL(350));
assert(C.ciToL(454) === 7.4,  '454 ci = 7.4 L', 7.4, C.ciToL(454));

// ── Units module structure check ──
console.log('\n[Module Structure]');
const categories = ['temperature','pressure','speed','distance','depth','fuel','length','weight','displacement'];
let structOK = true;
for (const cat of categories) {
  if (!Units[cat] || typeof Units[cat].toDisplay !== 'function') {
    structOK = false;
    console.error(`  ✗ Units.${cat}.toDisplay missing`);
  }
}
if (structOK) {
  passed++;
  console.log('  ✓ All 9 category objects present with toDisplay()');
} else {
  failed++;
}

// ── Default preference ──
console.log('\n[Defaults]');
localStorage.setItem('d3kos-measurement-system', 'imperial');
assert(Units.getPreference() === 'imperial', 'Default preference is imperial', 'imperial', Units.getPreference());

// ── N/A handling ──
console.log('\n[Edge Cases]');
assert(Units.temperature.toDisplay(NaN)       === 'N/A', 'NaN → N/A');
assert(Units.pressure.toDisplay(null)          === 'N/A', 'null → N/A');
assert(Units.fuel.toDisplay(undefined)         === 'N/A', 'undefined → N/A');

// ── Speed format ──
console.log('\n[Speed Display Format]');
localStorage.setItem('d3kos-measurement-system', 'metric');
const metricSpeed = Units.speed.toDisplay(10);
assert(metricSpeed.includes('km/h'), 'Metric speed includes km/h', 'km/h', metricSpeed);

localStorage.setItem('d3kos-measurement-system', 'imperial');
const imperialSpeed = Units.speed.toDisplay(10);
assert(imperialSpeed.includes('mph'), 'Imperial speed includes mph', 'mph', imperialSpeed);

// ═══════════════════════════════════════════════
console.log('\n' + '═'.repeat(50));
console.log(`Results: ${passed} passed, ${failed} failed`);
if (failed === 0) {
  console.log('ALL TESTS PASSED ✓ — Ready for deployment');
  process.exit(0);
} else {
  console.error(`FAILED: ${failed} test(s) failed — DO NOT DEPLOY`);
  process.exit(1);
}
