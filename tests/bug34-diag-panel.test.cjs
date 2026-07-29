const { JSDOM, VirtualConsole } = require('jsdom');
const fs = require('fs');
const assert = require('assert');

const INSTRUMENTS = 'deployment/v0.9.9.4/opt/d3kos/services/dashboard/static/js/instruments.js';
const OVERLAYS = 'deployment/v0.9.9.4/opt/d3kos/services/dashboard/static/js/overlays.js';

// ── Static source checks (no DOM needed) ────────────────────────────────

assert.ok(!fs.readFileSync(OVERLAYS, 'utf8').match(/8 PSI/),
  'FAIL: showCrit does not contain fabricated 8 PSI reading');
console.log('✓ showCrit does not contain fabricated 8 PSI reading');

assert.ok(!fs.readFileSync(OVERLAYS, 'utf8').match(/['"`]http:\/\/localhost:8097/),
  'FAIL: openDiag does not contain hardcoded localhost:8097');
console.log('✓ openDiag does not contain hardcoded localhost:8097');

const instrSrc = fs.readFileSync(INSTRUMENTS, 'utf8');
assert.ok(instrSrc.match(/oil\s*:.*crit\s*:\s*4/),
  'FAIL: THR.oil.crit is 4 in instruments.js');
assert.ok(!instrSrc.match(/oil\s*:.*crit\s*:\s*20/),
  'FAIL: THR.oil.crit should not be 20');
console.log('✓ THR.oil.crit is 4 in instruments.js');

assert.ok(instrSrc.match(/bat_hi\s*:/),
  'FAIL: THR.bat_hi exists in instruments.js');
assert.ok(instrSrc.match(/14\.8/),
  'FAIL: bat_hi must have adv:14.8');
assert.ok(instrSrc.match(/15\.6/),
  'FAIL: bat_hi must have crit:15.6');
console.log('✓ THR.bat_hi exists in instruments.js');

assert.ok(instrSrc.match(/depth_m\s*:\s*null/),
  'FAIL: _d3kEngData includes depth_m key in instruments.js');
console.log('✓ _d3kEngData includes depth_m key in instruments.js');

const renderDepthBlock = instrSrc.split('function _renderDepth')[1]?.split(/^}/m)[0] ?? '';
assert.ok(renderDepthBlock.match(/_d3kEngData\.depth_m/),
  'FAIL: _renderDepth writes depth_m to _d3kEngData in instruments.js');
console.log('✓ _renderDepth writes depth_m to _d3kEngData in instruments.js');

// ── Functional checks (jsdom) ────────────────────────────────────────────

function buildWindow() {
  const vc = new VirtualConsole();
  vc.on('jsdomError', () => {});
  const dom = new JSDOM(
    `<!DOCTYPE html><html><body>
      <div id="ticker"></div><div id="critSc"></div>
      <div id="diagBack"></div><div id="diagGrid"></div>
      <div id="diagTitle"></div><div id="diagAiTxt"></div>
      <div id="toast"></div><div id="alertCard"></div>
    </body></html>`,
    { runScripts: 'outside-only', virtualConsole: vc }
  );
  const w = dom.window;
  try { w.eval(fs.readFileSync(INSTRUMENTS, 'utf8')); } catch (e) { console.log('instruments.js error:', e.message); }
  try { w.eval(fs.readFileSync(OVERLAYS, 'utf8')); } catch (e) { console.log('overlays.js error:', e.message); }
  return w;
}

const w = buildWindow();
const html1 = w._diagBuildCards({ fuel_pct: 0.5, depth_m: 8.0 });
assert.ok(html1.match(/Fuel/),
  'FAIL: _diagBuildCards renders Fuel card');
assert.ok(html1.match(/Depth/),
  'FAIL: _diagBuildCards renders Depth card');
assert.ok(html1.match(/50%/),
  'FAIL: fuel_pct 0.5 should render as 50%');
assert.ok(html1.match(/8\.0\s*m/),
  'FAIL: depth_m should render as 8.0 m');
console.log('✓ _diagBuildCards renders Fuel and Depth cards');

const w2 = buildWindow();
const html2 = w2._diagBuildCards({ bat_v: 15.5 });
const batteryCard2 = html2.match(/<div class="dc[^"]*">[^<]*<div class="dc-lbl">Battery/)?.[0] ?? '';
assert.ok(batteryCard2.match(/bad/),
  'FAIL: _diagBuildCards flags 15.5V battery as bad (overcharge)');
console.log('✓ _diagBuildCards flags 15.5V battery as bad (overcharge)');

const w3 = buildWindow();
const html3 = w3._diagBuildCards({ bat_v: 13.0 });
const batteryCard3 = html3.match(/<div class="dc[^"]*">[^<]*<div class="dc-lbl">Battery/)?.[0] ?? '';
assert.ok(!batteryCard3.match(/bad/),
  'FAIL: _diagBuildCards does NOT flag 13.0V battery as bad (normal charging)');
console.log('✓ _diagBuildCards does NOT flag 13.0V battery as bad (normal charging)');

console.log('\nBUG-34: ALL ASSERTIONS PASSED');
