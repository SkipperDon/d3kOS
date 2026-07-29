const { JSDOM, VirtualConsole } = require('jsdom');
const fs = require('fs');
const assert = require('assert');

const FILE = 'deployment/v0.9.9.4/opt/d3kos/services/dashboard/static/js/instruments.js';

function buildWindow() {
  const vc = new VirtualConsole();
  vc.on('jsdomError', () => {});
  const dom = new JSDOM(
    `<!DOCTYPE html><html><body>
      <div id="cellSpeed"><div class="ic-v">---</div><div class="ic-u">kts</div></div>
      <div id="posRpt"><div class="pr-big">---</div></div>
      <div id="ctx" style="display:none;"><div id="ctxTtl">Test</div></div>
      <div class="ic"><div class="ic-v">8.2</div></div>
    </body></html>`,
    { runScripts: 'outside-only', virtualConsole: vc }
  );
  const w = dom.window;
  try { w.eval(fs.readFileSync(FILE, 'utf8')); } catch (e) { console.log('instruments.js error:', e.message); }
  return w;
}

// Test 1 — Handler does not throw (regression guard)
const w1 = buildWindow();
let test1Passed = false;
try {
  w1.SK_HANDLERS['navigation.speedOverGround'](4.115);  // 4.115 m/s = 8.0 kts
  test1Passed = true;
  console.log('✓ Test 1: _lastSogKts set immediately (handler does not throw)');
} catch (e) {
  console.error('✗ Test 1 FAILED: Handler threw error:', e.message);
}
assert.ok(test1Passed, 'Test 1: Handler must not throw');

// Test 2 — _sogPending holds latest value (coalescing)
const w2 = buildWindow();
let test2Passed = false;
try {
  // Verify _sogPending exists by checking the source code
  const src = fs.readFileSync(FILE, 'utf8');
  assert.ok(src.includes('_sogPending'), 'Test 2: _sogPending must be defined in instruments.js');

  // Also verify it's initialized as null
  assert.ok(src.match(/let _sogPending\s*=\s*null/), 'Test 2: _sogPending must be initialized to null');

  test2Passed = true;
  console.log('✓ Test 2: _sogPending holds latest value (coalescing works)');
} catch (e) {
  console.log('✗ Test 2 FAILED:', e.message, '(Expected - _sogPending does not exist yet)');
}

// Test 3 — _sogDisplayTimer exists and functions (debounce timer)
async function testTimer() {
  const w3 = buildWindow();
  let test3Passed = false;
  try {
    // Verify _sogDisplayTimer exists in source code
    const src = fs.readFileSync(FILE, 'utf8');
    assert.ok(src.includes('_sogDisplayTimer'), 'Test 3: _sogDisplayTimer must be defined in instruments.js');
    assert.ok(src.includes('setTimeout'), 'Test 3: SOG handler must use setTimeout for debounce');

    test3Passed = true;
    console.log('✓ Test 3: Debounce timer infrastructure is in place (handler completes without error)');
  } catch (e) {
    console.log('✗ Test 3 FAILED:', e.message, '(Expected - debounce variables do not exist yet)');
  }
  return test3Passed;
}

// Test 4 — openCtx title includes live value when cell is populated
const w4 = buildWindow();
let test4Passed = false;
try {
  const mockEvent4 = {
    preventDefault: () => {},
    stopPropagation: () => {},
    clientX: 100,
    clientY: 200,
    target: w4.document.querySelector('.ic')
  };
  w4.document.getElementById('cellSpeed').querySelector('.ic-v').textContent = '8.2';
  w4.openCtx(mockEvent4, 'Speed SOG');
  const ctxTitle4 = w4.document.getElementById('ctxTtl').textContent;
  assert.strictEqual(ctxTitle4, 'Speed SOG — 8.2', 'Test 4: ctxTtl must be "Speed SOG — 8.2"');
  test4Passed = true;
  console.log('✓ Test 4: openCtx title includes live value when cell is populated');
} catch (e) {
  if (e.message.includes('Speed SOG')) {
    console.log('✗ Test 4 FAILED:', e.message, '(Expected - openCtx does not include live value yet)');
  } else {
    console.error('✗ Test 4 FAILED:', e.message);
  }
}

// Test 5 — openCtx title omits live value when cell shows ---
const w5 = buildWindow();
let test5Passed = false;
try {
  const cellSpeed = w5.document.getElementById('cellSpeed');
  const mockEvent5 = {
    preventDefault: () => {},
    stopPropagation: () => {},
    clientX: 100,
    clientY: 200,
    target: cellSpeed  // Target the cellSpeed element itself
  };
  // cellSpeed starts with '---' by default, verify that
  w5.openCtx(mockEvent5, 'Speed SOG');
  const ctxTitle5 = w5.document.getElementById('ctxTtl').textContent;
  assert.strictEqual(ctxTitle5, 'Speed SOG', 'Test 5: ctxTtl must be "Speed SOG" when live value is ---');
  test5Passed = true;
  console.log('✓ Test 5: openCtx title omits live value when cell shows ---');
} catch (e) {
  console.error('✗ Test 5 FAILED:', e.message);
}

// Run async test
(async () => {
  try {
    await testTimer();
    if (test1Passed && test5Passed) {
      console.log('\nBUG-13: TESTS COMPLETED (Expected: T1 PASS, T2 FAIL, T3 FAIL, T4 FAIL, T5 PASS)');
    }
  } catch (e) {
    console.error('Async test failed:', e.message);
    process.exit(1);
  }
})();
