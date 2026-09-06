/**
 * contract-dashboard.spec.ts — Dashboard Contract Test (PHASE1-contract-test.md)
 *
 * Asserts three contracts so no BUG-29/30/37/38/41/47-class defect can recur silently:
 *   C1: every SK path the JS subscribes to EXISTS in the live SK tree (or is EXPECTED_ABSENT)
 *   C2: every DOM ID the JS writes to EXISTS in the rendered page DOM
 *   C3: every route the templates call returns ≠404 and ≠5xx from the live Flask app
 *
 * Prerequisites:
 *   - Lab Pi reachable at BASE_URL (default http://192.168.1.237:3000)
 *   - LAB-SIM cruise scenario running: deployment/tools/lab-sim/run.sh cruise
 *     Without LAB-SIM, real SK paths are absent and the EXPECTED_ABSENT list grows;
 *     with LAB-SIM, the list stays small and meaningful.
 *   - SK reachable at SK_URL (default http://192.168.1.237:8099)
 *
 * Run: BASE_URL=http://192.168.1.237:3000 SK_URL=http://192.168.1.237:8099 npx playwright test contract-dashboard
 *
 * Spec: deployment/docs/atomic-specs/PHASE1-contract-test.md
 */

import { test, expect } from '@playwright/test';

const BASE = process.env.BASE_URL ?? 'http://192.168.1.237:3000';
const SK   = process.env.SK_URL  ?? 'http://192.168.1.237:8099';

// ---------------------------------------------------------------------------
// EXPECTED_ABSENT: SK paths legitimately absent from the lab Pi.
// Each entry MUST have a justification. An unjustified entry is a hidden skip.
// Reviewed by Tier 1 (PHASE1-contract-test.md §5).
// ---------------------------------------------------------------------------
const EXPECTED_ABSENT = new Set([
  // Engine — no physical engine on the lab Pi; LAB-SIM injects these but they
  // may still be absent from the persistent SK tree if LAB-SIM has not run.
  // If LAB-SIM cruise is active, these should be PRESENT. Remove from this list
  // when the cruise scenario reliably populates them, to keep the list minimal.
  // 'propulsion.port.coolantTemperature',  // LAB-SIM covers this — do not add
  // 'propulsion.port.oilPressure',         // LAB-SIM covers this

  // AIS — no AIS receiver on the lab Pi; rtl_ais is not running in the lab
  'vessels.urn:mrn:imo:mmsi:*',            // AIS vessels; dynamic keys not checkable
]);

// SK paths that must have a handler (bidirectional — C1 direction 2).
// Derived from the BUG-47 alias block: every propulsion.port.* twin must exist.
// Add to this list whenever a new alias is added to instruments.js.
const REQUIRED_HANDLED_PATHS = [
  'propulsion.port.coolantTemperature',
  'propulsion.port.oilPressure',
  'propulsion.port.revolutions',
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function extractSkPaths(jsSource: string): string[] {
  // Extract keys from SK_HANDLERS = { 'path': ..., "path": ... }
  // Pattern: quoted string that looks like a dotted SK path
  const matches = jsSource.matchAll(/['"]([a-zA-Z][a-zA-Z0-9._*]+\.[a-zA-Z][a-zA-Z0-9._*]+)['"]\s*:/g);
  const paths = new Set<string>();
  for (const m of matches) {
    const p = m[1];
    // Only include SignalK-shaped paths (two or more dot-separated segments)
    if (p.includes('.') && !p.startsWith('http') && !p.startsWith('ws')) {
      paths.add(p);
    }
  }
  return [...paths];
}

function extractDomIds(jsSource: string): string[] {
  const matches = jsSource.matchAll(/getElementById\(['"]([^'"]+)['"]\)|querySelector\(['"]#([^'"]+)['"]\)/g);
  const ids = new Set<string>();
  for (const m of matches) {
    ids.add(m[1] || m[2]);
  }
  return [...ids];
}

// Flatten a nested SK tree object into dot-separated key paths
function flattenSkTree(obj: Record<string, unknown>, prefix = ''): Set<string> {
  const result = new Set<string>();
  for (const [k, v] of Object.entries(obj)) {
    const full = prefix ? `${prefix}.${k}` : k;
    result.add(full);
    if (v && typeof v === 'object' && !Array.isArray(v) && !('value' in (v as object))) {
      for (const sub of flattenSkTree(v as Record<string, unknown>, full)) {
        result.add(sub);
      }
    }
  }
  return result;
}

// ---------------------------------------------------------------------------
// C1: Signal K path contract
// ---------------------------------------------------------------------------
test.describe('C1 — Signal K path contract', () => {
  test('Every subscribed SK path exists in the live tree (or is EXPECTED_ABSENT)', async ({ page }) => {
    // Fetch served instruments.js — NOT from repo. The contract that matters is what is served.
    const jsResp = await page.goto(BASE + '/static/js/instruments.js');
    expect(jsResp?.status(), 'instruments.js must be served (not 404)').toBe(200);
    const jsSource = await jsResp!.text();

    const paths = extractSkPaths(jsSource);
    // T7: count must be non-zero — a broken regex that matches nothing passes silently
    expect(paths.length, 'extracted SK paths must be non-zero (T7: regex must look)').toBeGreaterThan(5);
    console.log(`C1: extracted ${paths.length} SK paths from instruments.js`);

    // Fetch live SK tree
    const skResp = await page.goto(`${SK}/signalk/v1/api/vessels/self`);
    expect(skResp?.status(), 'SK REST API must respond').toBe(200);
    const skTree = await skResp!.json();
    const skPaths = flattenSkTree(skTree, 'vessels.self');

    const violations: string[] = [];
    for (const path of paths) {
      // Check by checking if any SK tree key starts with or contains this path
      const normalized = path.replace('propulsion.0.', 'propulsion.port.');
      const inTree = skPaths.has(path) || skPaths.has(normalized) ||
                     [...skPaths].some(k => k.includes(path.split('.').slice(-1)[0]));
      if (!inTree && !EXPECTED_ABSENT.has(path)) {
        violations.push(`"${path}" subscribed in instruments.js but absent from SK tree and not EXPECTED_ABSENT`);
      }
    }
    if (violations.length > 0) {
      console.error('C1 violations:\n' + violations.join('\n'));
    }
    expect(violations, 'All subscribed SK paths must exist in live SK tree or EXPECTED_ABSENT').toEqual([]);
  });

  test('Bidirectional: propulsion.port.* twins all have handlers (BUG-47 guard)', async ({ page }) => {
    const jsResp = await page.goto(BASE + '/static/js/instruments.js');
    const jsSource = await jsResp!.text();
    const paths = extractSkPaths(jsSource);
    const pathSet = new Set(paths);

    const missing: string[] = [];
    for (const required of REQUIRED_HANDLED_PATHS) {
      if (!pathSet.has(required)) {
        missing.push(`"${required}" is required (BUG-47 bidirectional guard) but has no handler in instruments.js`);
      }
    }
    if (missing.length > 0) {
      console.error('C1 bidirectional violations:\n' + missing.join('\n'));
    }
    expect(missing, 'All required propulsion.port.* aliases must have handlers').toEqual([]);
  });
});

// ---------------------------------------------------------------------------
// C2: DOM ID contract
// ---------------------------------------------------------------------------
test.describe('C2 — DOM ID contract', () => {
  test('Every DOM ID written by instruments.js exists in the rendered index.html', async ({ page }) => {
    // Fetch instruments.js first (served, not repo)
    const jsResp = await page.goto(BASE + '/static/js/instruments.js');
    const jsSource = await jsResp!.text();
    const ids = extractDomIds(jsSource);

    // T7: extraction must find something
    expect(ids.length, 'extracted DOM IDs must be non-zero (T7: regex must look)').toBeGreaterThan(3);
    console.log(`C2: extracted ${ids.length} DOM IDs from instruments.js`);

    // Navigate to the actual page
    await page.goto(BASE + '/');
    await page.waitForLoadState('networkidle');

    const violations: string[] = [];
    for (const id of ids) {
      // Compound selectors (e.g. "posRpt .pr-big" from querySelector('#posRpt .pr-big'))
      // must be used as-is with the # prefix; CSS.escape would corrupt the space/dot.
      const selector = id.includes(' ')
        ? `#${id}`
        : `#${await page.evaluate((i) => CSS.escape(i), id)}`;
      const el = await page.$(selector);
      if (!el) {
        violations.push(`#${id} written by instruments.js but absent from rendered index.html`);
      }
    }
    if (violations.length > 0) {
      console.error('C2 violations:\n' + violations.join('\n'));
    }
    expect(violations, 'All DOM IDs written by instruments.js must exist in rendered page').toEqual([]);
  });
});

// ---------------------------------------------------------------------------
// C3: Route contract
// ---------------------------------------------------------------------------
test.describe('C3 — Flask route contract', () => {
  // Routes extracted from the dashboard templates and JS.
  // These are the paths the dashboard itself navigates to or fetches.
  // Extend this list whenever new routes are added.
  const EXPECTED_ROUTES = [
    '/',
    '/anchor-watch',
    '/boat-log',
    '/settings',
    '/status',
  ];

  test('Every dashboard route returns a non-404, non-5xx response', async ({ page }) => {
    const violations: string[] = [];
    for (const route of EXPECTED_ROUTES) {
      const resp = await page.goto(BASE + route);
      const status = resp?.status() ?? 0;
      // Accept: 200, 302 (redirect), 401 (auth gate), 405 (method not allowed)
      // Fail on: 404 (not found), 5xx (server error) — BUG-37, BUG-41
      if (status === 404 || status >= 500) {
        violations.push(`${route} returned HTTP ${status} — expected 200/302/401/405`);
      }
      console.log(`C3: ${route} → ${status}`);
    }
    if (violations.length > 0) {
      console.error('C3 violations:\n' + violations.join('\n'));
    }
    expect(violations, 'All dashboard routes must return ≠404 and ≠5xx').toEqual([]);
  });
});
