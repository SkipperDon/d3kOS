const { JSDOM, VirtualConsole } = require('jsdom');
const fs = require('fs');
const assert = require('assert');

const B = 'deployment/v0.9.9.4/opt/d3kos/services/dashboard/';

const ALIASES = {
  'propulsion.0.revolutions':        ['propulsion.port.revolutions'],
  'propulsion.0.oilPressure':        ['propulsion.port.oilPressure'],
  'propulsion.0.coolantTemperature': ['propulsion.port.temperature',
                                      'propulsion.0.temperature'],
  'propulsion.0.trimTabPosition':    ['propulsion.port.drive.trimState',
                                      'propulsion.0.drive.trimState'],
};

// ---- 1. instruments.js: alias keys must share handler IDENTITY ----
const vc = new VirtualConsole();
vc.on('jsdomError', () => {});
const dom = new JSDOM('<!doctype html><html><body>' +
  '<div id="rowEngine" class="hidden"></div><div id="rowNav" class="hidden"></div>' +
  '<div id="engineAlert"></div><div id="navAlert"></div><div id="ticker"></div>' +
  '</body></html>', { runScripts: 'outside-only', virtualConsole: vc });
dom.window.openDiag = () => {};
dom.window.eval(fs.readFileSync(B + 'static/js/instruments.js', 'utf8'));
const H = dom.window.SK_HANDLERS;
for (const [orig, aliases] of Object.entries(ALIASES)) {
  assert.ok(H[orig], `instruments.js: original ${orig} missing`);
  for (const a of aliases) {
    assert.ok(H[a], `instruments.js: alias ${a} not registered`);
    assert.strictEqual(H[a], H[orig],
      `instruments.js: ${a} must be the SAME function as ${orig}, not a copy`);
  }
}
// battery + fuel must be untouched
assert.ok(H['electrical.batteries.0.voltage'], 'battery path must survive');
assert.ok(!H['electrical.batteries.port.voltage'], 'battery must NOT be aliased');

// ---- 2. behavioural: an aliased delta populates the cache (needs BUG-36) ----
dom.window.SK_HANDLERS['propulsion.port.temperature'](368.15);
assert.strictEqual(Math.round(dom.window._d3kEngData.coolant_c), 95,
  'a propulsion.port.temperature delta must reach the engine cache');
dom.window.SK_HANDLERS['propulsion.port.revolutions'](30);
assert.strictEqual(dom.window._d3kEngData.rpm, 1800,
  'a propulsion.port.revolutions delta must reach the engine cache');

// ---- 3. the other three files: every alias present in source ----
for (const f of ['static/js/boatlog-engine.js',
                 'templates/engine-monitor.html',
                 'templates/helm-assistant.html']) {
  const src = fs.readFileSync(B + f, 'utf8');
  for (const [orig, aliases] of Object.entries(ALIASES)) {
    if (!src.includes(orig)) continue;          // file may not use every path
    for (const a of aliases) {
      assert.ok(src.includes(a), `${f}: missing alias ${a} for ${orig}`);
    }
  }
}

// ---- 4. subscribe lists must carry the aliases too ----
for (const f of ['static/js/boatlog-engine.js',
                 'templates/engine-monitor.html',
                 'templates/helm-assistant.html']) {
  const src = fs.readFileSync(B + f, 'utf8');
  for (const a of ['propulsion.port.revolutions', 'propulsion.port.temperature']) {
    if (!src.includes(a)) continue;
    assert.ok(new RegExp("path:\\s*'" + a.replace(/\./g, '\\.') + "'").test(src),
      `${f}: ${a} must appear as a { path: ... } subscribe entry`);
  }
}

console.log('BUG-29: ALL ASSERTIONS PASSED');
process.exit(0);
