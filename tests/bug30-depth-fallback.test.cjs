const { JSDOM, VirtualConsole } = require('jsdom');
const fs = require('fs');
const assert = require('assert');

const F = 'deployment/v0.9.9.4/opt/d3kos/services/dashboard/static/js/instruments.js';

function load() {
  const vc = new VirtualConsole();
  vc.on('jsdomError', () => {});
  const dom = new JSDOM(
    '<!doctype html><html><body>' +
    '<div id="cellDepth"><div class="ic-v"></div><div class="ic-u"></div></div>' +
    '<div id="rowEngine" class="hidden"></div>' +
    '<div id="rowNav" class="hidden"></div>' +
    '<div id="engineAlert"></div>' +
    '<div id="navAlert"></div>' +
    '<div id="ticker"></div>' +
    '</body></html>',
    { runScripts: 'outside-only', virtualConsole: vc }
  );
  // Stub dependencies that won't be used in this test
  dom.window.openDiag = () => {};
  dom.window.eval(fs.readFileSync(F, 'utf8'));
  return dom.window;
}

const val  = w => w.document.querySelector('#cellDepth .ic-v').innerHTML;
const unit = w => w.document.querySelector('#cellDepth .ic-u').textContent;

// BUG-43: default unit is imperial (feet). Display values are metres × 3.28084, toFixed(1).
// 4.2m × 3.28084 = 13.779… → '13.8'
// 3.5m × 3.28084 = 11.482… → '11.5'
// Thresholds in THR.depth are metres: { adv: 3, alrt: 2, crit: 1 }. 4.2m and 3.5m are above all.

// 1 — belowTransducer alone renders, and is LABELLED as transducer depth
let w = load();
assert.ok(w.SK_HANDLERS['environment.depth.belowTransducer'],
          'belowTransducer handler must exist');
w.SK_HANDLERS['environment.depth.belowTransducer'](4.2);
assert.strictEqual(val(w), '13.8', 'transducer 4.2m must display as 13.8 ft (BUG-43 imperial)');
assert.ok(/UNDER TRANSDUCER/.test(unit(w)),
  'a transducer reading MUST be labelled as such — never plain "feet"');

// 2 — belowKeel renders with the plain label
w = load();
w.SK_HANDLERS['environment.depth.belowKeel'](3.5);
assert.strictEqual(val(w), '11.5', 'keel 3.5m must display as 11.5 ft (BUG-43 imperial)');
assert.ok(!/TRANSDUCER/.test(unit(w)), 'keel depth must NOT carry the transducer label');

// 3 — SAFETY: transducer must never overwrite a keel value
//   (assertions 3-5 were NEVER executed before — stale expectations blocked assertions 1-2)
w = load();
w.SK_HANDLERS['environment.depth.belowKeel'](3.5);
w.SK_HANDLERS['environment.depth.belowTransducer'](4.2);
assert.strictEqual(val(w), '11.5',
  'belowTransducer must NOT overwrite belowKeel — that would overstate clearance (BUG-30 safety)');
assert.ok(!/TRANSDUCER/.test(unit(w)), 'label must stay on keel after transducer arrives late');

// 4 — keel arriving later takes over (it always wins, whenever it arrives)
w = load();
w.SK_HANDLERS['environment.depth.belowTransducer'](4.2);
w.SK_HANDLERS['environment.depth.belowKeel'](3.5);
assert.strictEqual(val(w), '11.5', 'belowKeel must take over when it arrives after transducer');
assert.ok(!/TRANSDUCER/.test(unit(w)), 'label must switch to keel when keel arrives');

// 5 — REGRESSION: shallow-water alarm still fires on both sources
//   0.5m depth: _evalBelow(0.5, {adv:3, alrt:2, crit:1}) → 'crit'; unit = 'feet · crit'
w = load();
w.SK_HANDLERS['environment.depth.belowKeel'](0.5);
assert.ok(/crit|alrt|adv/i.test(unit(w)), 'keel alarm state must still render at 0.5m');
w = load();
w.SK_HANDLERS['environment.depth.belowTransducer'](0.5);
assert.ok(/crit|alrt|adv/i.test(unit(w)), 'transducer alarm state must still render at 0.5m');

console.log('BUG-30: ALL ASSERTIONS PASSED (including safety assertions 3-5 — first clean run)');
process.exit(0);
