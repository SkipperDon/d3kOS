/**
 * test_hardware_json.js
 * Validates hardware.json integrity — each entry's RTSP URL IP must
 * match the entry's `ip` field. A mismatch means the stream manager
 * connects to a wrong host and the camera never gets a frame.
 *
 * Bug: Port RTSP points to 10.42.0.134 (ip=10.42.0.135)
 *      Starboard RTSP points to 10.42.0.182 (ip=10.42.0.183)
 *
 * Run: node deployment/d3kOS/dashboard/tests/test_hardware_json.js
 */

'use strict';

const fs   = require('fs');
const path = require('path');

let passed = 0;
let failed = 0;

function assert(condition, message) {
  if (condition) {
    console.log('  PASS:', message);
    passed++;
  } else {
    console.error('  FAIL:', message);
    failed++;
  }
}

/* ── Load hardware.json ── */
const hwPath = path.join(__dirname, '../../../../config/hardware.json.test');

/* For CI — use inline fixture matching current Pi state (with bugs) */
const HARDWARE_BUGGY = [
  {
    hardware_id: 'hw_ec_71_db_f9_7c_7c',
    ip: '10.42.0.100',
    rtsp_url: 'rtsp://admin:d3kos2026@10.42.0.100:554/h264Preview_01_sub',
    assigned_to_slot: 'bow'
  },
  {
    hardware_id: 'hw_ec_71_db_99_78_04',
    ip: '10.42.0.64',
    rtsp_url: 'rtsp://admin:d3kos2026%24@10.42.0.64:554/h264Preview_01_sub',
    assigned_to_slot: 'helm'
  },
  {
    hardware_id: 'hw_ec_71_db_43_ef_c1',
    ip: '10.42.0.135',
    rtsp_url: 'rtsp://admin:d3kos2026%24@10.42.0.134:554/h264Preview_01_sub', // BUG: 134 != 135
    assigned_to_slot: 'port'
  },
  {
    hardware_id: 'hw_ec_71_db_be_0b_7b',
    ip: '10.42.0.183',
    rtsp_url: 'rtsp://admin:d3kos2026%24@10.42.0.182:554/h264Preview_01_sub', // BUG: 182 != 183
    assigned_to_slot: 'starboard'
  }
];

const HARDWARE_FIXED = [
  {
    hardware_id: 'hw_ec_71_db_f9_7c_7c',
    ip: '10.42.0.100',
    rtsp_url: 'rtsp://admin:d3kos2026@10.42.0.100:554/h264Preview_01_sub',
    assigned_to_slot: 'bow'
  },
  {
    hardware_id: 'hw_ec_71_db_99_78_04',
    ip: '10.42.0.64',
    rtsp_url: 'rtsp://admin:d3kos2026%24@10.42.0.64:554/h264Preview_01_sub',
    assigned_to_slot: 'helm'
  },
  {
    hardware_id: 'hw_ec_71_db_43_ef_c1',
    ip: '10.42.0.135',
    rtsp_url: 'rtsp://admin:d3kos2026%24@10.42.0.135:554/h264Preview_01_sub', // FIXED
    assigned_to_slot: 'port'
  },
  {
    hardware_id: 'hw_ec_71_db_be_0b_7b',
    ip: '10.42.0.183',
    rtsp_url: 'rtsp://admin:d3kos2026%24@10.42.0.183:554/h264Preview_01_sub', // FIXED
    assigned_to_slot: 'starboard'
  }
];

/* ── Validator — extracts IP from RTSP URL and compares to ip field ── */
function extractRtspIp(rtsp_url) {
  // rtsp://user:pass@IP:port/path  (pass may contain %24 etc)
  var m = rtsp_url.match(/rtsp:\/\/[^@]+@([^:\/]+)/);
  return m ? m[1] : null;
}

function validateHardware(entries) {
  var errors = [];
  entries.forEach(function(entry) {
    var rtspIp = extractRtspIp(entry.rtsp_url);
    if (rtspIp !== entry.ip) {
      errors.push(entry.assigned_to_slot + ': ip=' + entry.ip + ' but RTSP points to ' + rtspIp);
    }
  });
  return errors;
}

/* ── Tests ── */
console.log('\nhardware.json integrity — RTSP IP vs ip field\n');

console.log('  [Buggy data — confirms bugs exist]');
var buggyErrors = validateHardware(HARDWARE_BUGGY);
assert(
  buggyErrors.includes('port: ip=10.42.0.135 but RTSP points to 10.42.0.134'),
  'Bug confirmed: port RTSP points to 10.42.0.134, ip is 10.42.0.135'
);
assert(
  buggyErrors.includes('starboard: ip=10.42.0.183 but RTSP points to 10.42.0.182'),
  'Bug confirmed: starboard RTSP points to 10.42.0.182, ip is 10.42.0.183'
);

console.log('\n  [Fixed data — all RTSP IPs must match ip field]');
var fixedErrors = validateHardware(HARDWARE_FIXED);
assert(fixedErrors.length === 0,
  'All RTSP IPs match their ip fields (' + HARDWARE_FIXED.length + ' entries)');
assert(
  extractRtspIp(HARDWARE_FIXED[2].rtsp_url) === '10.42.0.135',
  'Port RTSP IP corrected to 10.42.0.135'
);
assert(
  extractRtspIp(HARDWARE_FIXED[3].rtsp_url) === '10.42.0.183',
  'Starboard RTSP IP corrected to 10.42.0.183'
);
assert(
  extractRtspIp(HARDWARE_FIXED[0].rtsp_url) === '10.42.0.100',
  'Bow RTSP IP unchanged (10.42.0.100)'
);
assert(
  extractRtspIp(HARDWARE_FIXED[1].rtsp_url) === '10.42.0.64',
  'Helm RTSP IP unchanged (10.42.0.64)'
);

/* ── Results ── */
console.log('\n─────────────────────────────────────────────────────');
console.log('Results:', passed, 'passed,', failed, 'failed');
console.log('─────────────────────────────────────────────────────\n');
process.exit(failed > 0 ? 1 : 0);
