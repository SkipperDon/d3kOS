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

const val = w => w.document.querySelector('#cellDepth .ic-v').innerHTML;
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
assert.ok(/crit|alrt|adv/i.test(unit(w)), 'keel alarm state must still render');
w = load();
w.SK_HANDLERS['environment.depth.belowTransducer'](0.5);
assert.ok(/crit|alrt|adv/i.test(unit(w)), 'transducer alarm state must still render');

console.log('BUG-30: ALL ASSERTIONS PASSED');
process.exit(0);
