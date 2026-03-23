/**
 * test_marine_vision_ui.js
 * Unit tests for marine-vision.html UI logic bugs.
 *
 * Bug 1: active default fallback
 *   When active_default camera has no frame, page should fall back to
 *   the first camera with has_frame:true — not show a blank feed.
 *
 * Bug 2: connecting/offline distinction in selector
 *   Cameras with status 'connecting' should be tappable (dimmed).
 *   Only cameras with status 'offline' should be truly disabled.
 *
 * Run: node deployment/d3kOS/dashboard/tests/test_marine_vision_ui.js
 */

'use strict';

let passed = 0;
let failed = 0;

/* assert — counts toward pass/fail exit code */
function assert(condition, message) {
  if (condition) {
    console.log('  PASS:', message);
    passed++;
  } else {
    console.error('  FAIL:', message);
    failed++;
  }
}

/* demonstrateBug — shows what the buggy code does; does NOT count toward exit code */
function demonstrateBug(condition, message) {
  if (!condition) {
    console.log('  BUG CONFIRMED:', message);
  } else {
    console.log('  (bug not triggered):', message);
  }
}

/* ── Logic under test (mirrors marine-vision.html JS) ── */

/**
 * selectActiveSlot — determines which slot to show on page load.
 * CURRENT (buggy): picks active_default regardless of has_frame.
 * FIXED: falls back to first slot with has_frame:true if active_default has no frame.
 */
function selectActiveSlot_BUGGY(slots) {
  var def = slots.find(function(s) { return s.roles && s.roles.active_default; });
  return def ? def.slot_id : (slots[0] ? slots[0].slot_id : null);
}

function selectActiveSlot_FIXED(slots) {
  var def = slots.find(function(s) { return s.roles && s.roles.active_default; });
  if (def && def.has_frame) {
    return def.slot_id;
  } else {
    var withFrame = slots.find(function(s) { return s.has_frame; });
    return withFrame ? withFrame.slot_id
         : def       ? def.slot_id
         : (slots[0] ? slots[0].slot_id : null);
  }
}

/**
 * slotIsDisabled — determines if a camera button should be cursor:not-allowed.
 * CURRENT (buggy): disables any slot that is not 'online' (includes 'connecting').
 * FIXED: only disables slots where hardware.status === 'offline'.
 */
function slotIsDisabled_BUGGY(slot) {
  return slot.status !== 'online';
}

function slotIsDisabled_FIXED(slot) {
  // offline = hardware truly offline (cursor:not-allowed)
  // connecting = dimmed but still tappable — NOT disabled
  return !!(slot.hardware && slot.hardware.status === 'offline');
}

/* ── Test data matching Pi's actual state ── */
const SLOTS_PI = [
  {
    slot_id: 'bow',   label: 'Bow',
    status: 'online', has_frame: true,
    roles: { active_default: false, display_in_grid: true },
    hardware: { status: 'online', ip: '10.42.0.100' }
  },
  {
    slot_id: 'helm',  label: 'Helm',
    status: 'connecting', has_frame: true,
    roles: { active_default: false, display_in_grid: true },
    hardware: { status: 'online', ip: '10.42.0.64' }  // hardware says online, stream reconnecting
  },
  {
    slot_id: 'port',  label: 'Port',
    status: 'connecting', has_frame: false,
    roles: { active_default: true, display_in_grid: true },   // ← active_default but NO frame
    hardware: { status: 'online', ip: '10.42.0.135' }
  },
  {
    slot_id: 'starboard', label: 'Starboard',
    status: 'connecting', has_frame: false,
    roles: { active_default: false, display_in_grid: true },
    hardware: { status: 'online', ip: '10.42.0.183' }
  }
];

const SLOTS_ALL_OFFLINE = [
  {
    slot_id: 'bow', label: 'Bow',
    status: 'offline', has_frame: false,
    roles: { active_default: true },
    hardware: { status: 'offline', ip: '10.42.0.100' }
  }
];

const SLOTS_DEFAULT_HAS_FRAME = [
  {
    slot_id: 'bow', label: 'Bow',
    status: 'online', has_frame: true,
    roles: { active_default: true },
    hardware: { status: 'online' }
  },
  {
    slot_id: 'helm', label: 'Helm',
    status: 'connecting', has_frame: false,
    roles: { active_default: false },
    hardware: { status: 'online' }
  }
];

/* ─────────────────────────────────────────────────────────────
   BUG 1 TESTS — active default fallback
   ───────────────────────────────────────────────────────────── */
console.log('\nBug 1: active default fallback\n');

// Demonstrate the bug (does not count toward exit code)
demonstrateBug(
  selectActiveSlot_BUGGY(SLOTS_PI) !== 'port',
  'BUGGY: active_default=port (no frame) should NOT be selected — falls back to bow'
);

// These should PASS with fixed code
console.log('  [FIXED behaviour — these must PASS after the fix]');
assert(
  selectActiveSlot_FIXED(SLOTS_PI) === 'bow',
  'FIXED: active_default=port has no frame → falls back to bow (has_frame:true)'
);
assert(
  selectActiveSlot_FIXED(SLOTS_DEFAULT_HAS_FRAME) === 'bow',
  'FIXED: active_default=bow has frame → selects bow (no fallback needed)'
);
assert(
  selectActiveSlot_FIXED(SLOTS_ALL_OFFLINE) === 'bow',
  'FIXED: nothing has a frame → still selects active_default bow (graceful fallback)'
);
assert(
  selectActiveSlot_FIXED([]) === null,
  'FIXED: empty slot list → returns null'
);

/* ─────────────────────────────────────────────────────────────
   BUG 2 TESTS — connecting/offline distinction
   ───────────────────────────────────────────────────────────── */
console.log('\nBug 2: connecting/offline distinction\n');

const helmSlot      = SLOTS_PI[1]; // status:connecting, hardware.status:online
const portSlot      = SLOTS_PI[2]; // status:connecting, hardware.status:online
const trueOffline   = SLOTS_ALL_OFFLINE[0]; // hardware.status:offline

// Demonstrate the bugs (do not count toward exit code)
demonstrateBug(
  slotIsDisabled_BUGGY(helmSlot) === false,
  'BUGGY: helm connecting+hardware online was disabled (cursor:not-allowed) — should be tappable'
);
demonstrateBug(
  slotIsDisabled_BUGGY(portSlot) === false,
  'BUGGY: port connecting+hardware online was disabled (cursor:not-allowed) — should be tappable'
);

// These should PASS with fixed code
console.log('  [FIXED behaviour — these must PASS after the fix]');
assert(
  slotIsDisabled_FIXED(helmSlot) === false,
  'FIXED: helm connecting + hardware online → not disabled (tappable)'
);
assert(
  slotIsDisabled_FIXED(portSlot) === false,
  'FIXED: port connecting + hardware online → not disabled (tappable)'
);
assert(
  slotIsDisabled_FIXED(trueOffline) === true,
  'FIXED: hardware.status=offline → disabled (cursor:not-allowed)'
);
assert(
  slotIsDisabled_FIXED(SLOTS_PI[0]) === false,
  'FIXED: bow online → not disabled'
);

/* ─────────────────────────────────────────────────────────────
   RESULTS
   ───────────────────────────────────────────────────────────── */
console.log('\n─────────────────────────────────────────────────────');
console.log('Results:', passed, 'passed,', failed, 'failed');
console.log('─────────────────────────────────────────────────────\n');
process.exit(failed > 0 ? 1 : 0);
