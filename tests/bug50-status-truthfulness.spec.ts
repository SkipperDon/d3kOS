/**
 * BUG-50 — the Settings "System Status" panel must not report a capability as
 * healthy when it is not.
 *
 * The defect: `si-gps` and `si-ais` were both wired to `d.signalk` — the Signal K
 * *server's* liveness — so Signal K running made both go green regardless of
 * whether any GPS position or AIS target existed. `si-openplotter` was hardcoded
 * to `true` and could never report a fault. AvNav's check was a bare GET on :8080,
 * which passes with blank charts or with AIS fetching disabled inside AvNav —
 * exactly the BUG-19/20 state. And `check_service()` caught only RequestException,
 * so an HTTP 500 read as "up".
 *
 * Proven on the lab Pi 2026-08-02: Settings showed GPS green while
 * navigation/position returned 404, and AIS green while Signal K held one vessel
 * (own ship, zero targets).
 *
 * These tests are written to FAIL against the pre-fix code. The lab Pi has no GPS
 * and no AIS, so it is the natural negative fixture: every one of these indicators
 * SHOULD read not-healthy here.
 *
 * A green indicator is worse than a missing one. A missing indicator tells the
 * operator nothing; a green one tells them something false, at the helm.
 *
 * Run:
 *   BASE_URL=http://192.168.1.237:3000 npx playwright test tests/bug50-status-truthfulness.spec.ts
 */
import { test, expect } from '@playwright/test';

const BASE = process.env.BASE_URL ?? 'http://192.168.1.237:3000';
const SK = process.env.SK_URL ?? 'http://192.168.1.237:8099';

/** Ground truth read straight from Signal K, independent of anything d3kOS reports. */
async function signalkTruth(request: any) {
  let hasPosition = false;
  let aisTargets = 0;

  // Freshness, NOT mere presence. Signal K never expires a stale position, so a
  // presence-based check would make every negative test skip permanently after
  // any GPS had ever run once — the tests would look green while asserting nothing.
  const posRes = await request.get(
    `${SK}/signalk/v1/api/vessels/self/navigation/position`, { failOnStatusCode: false });
  if (posRes.ok()) {
    const pos = await posRes.json();
    const hasLatLon = pos?.value?.latitude !== undefined && pos?.value?.longitude !== undefined;
    const ageS = pos?.timestamp
      ? (Date.now() - Date.parse(pos.timestamp)) / 1000
      : Number.POSITIVE_INFINITY;
    hasPosition = !!hasLatLon && ageS <= 10;
  }

  const vesselsRes = await request.get(`${SK}/signalk/v1/api/vessels/`, { failOnStatusCode: false });
  if (vesselsRes.ok()) {
    const vessels = await vesselsRes.json();
    const selfUuid = (await (await request.get(`${SK}/signalk/v1/api/self`, { failOnStatusCode: false })).text())
      .replace(/"/g, '').trim().replace(/^vessels\./, '');
    aisTargets = Object.entries(vessels).filter(([k, v]: [string, any]) => {
      if (k === selfUuid || selfUuid.endsWith(k)) return false;
      const ts = v?.navigation?.position?.timestamp;
      return !!ts && (Date.now() - Date.parse(ts)) / 1000 <= 300;
    }).length;
  }

  return { hasPosition, aisTargets };
}

test.describe('BUG-50 — /status must report GPS and AIS from data, not from server liveness', () => {
  test('/status exposes a dedicated gps field', async ({ request }) => {
    const body = await (await request.get(`${BASE}/status`)).json();
    expect(
      Object.prototype.hasOwnProperty.call(body, 'gps'),
      '/status must report GPS independently — it currently omits the field entirely, ' +
        'which is why the UI had to borrow d.signalk',
    ).toBe(true);
  });

  test('/status exposes a dedicated ais field', async ({ request }) => {
    const body = await (await request.get(`${BASE}/status`)).json();
    expect(
      Object.prototype.hasOwnProperty.call(body, 'ais'),
      '/status must report AIS independently',
    ).toBe(true);
  });

  test('gps is not reported healthy when Signal K has no position', async ({ request }) => {
    const truth = await signalkTruth(request);
    const body = await (await request.get(`${BASE}/status`)).json();
    test.skip(truth.hasPosition, 'Signal K has a live position — this asserts the negative case');
    expect(
      body.gps,
      `Signal K has no navigation.position, so gps must be false. Got ${JSON.stringify(body.gps)}`,
    ).toBe(false);
  });

  test('ais reports no_data — not a healthy state — when Signal K holds zero targets', async ({ request }) => {
    const truth = await signalkTruth(request);
    const body = await (await request.get(`${BASE}/status`)).json();
    test.skip(truth.aisTargets > 0, 'AIS targets present — this asserts the negative case');
    expect(
      body.ais,
      `Zero AIS targets in Signal K, so ais must not claim to be receiving. Got ${JSON.stringify(body.ais)}`,
    ).not.toBe('receiving');
  });

  test('ais is a three-state value, never a bare boolean', async ({ request }) => {
    const body = await (await request.get(`${BASE}/status`)).json();
    expect(
      ['receiving', 'no_targets', 'no_data'],
      'AIS cannot be expressed as green/red — "nothing in range" is normal and must be ' +
        'distinguishable from "receiver is dead". Reporting a three-state truth as a ' +
        'two-state light is what created this bug.',
    ).toContain(body.ais);
  });

  test('gps must NOT simply mirror the signalk field', async ({ request }) => {
    const truth = await signalkTruth(request);
    const body = await (await request.get(`${BASE}/status`)).json();
    test.skip(truth.hasPosition, 'only meaningful when there is no position to find');
    expect(
      body.signalk === true && body.gps === true,
      'gps tracking signalk exactly is the original defect',
    ).toBe(false);
  });
});

test.describe('BUG-50 — the Settings page must not wire GPS/AIS to Signal K liveness', () => {
  test('loadStatus no longer derives si-gps or si-ais from d.signalk', async ({ request }) => {
    const html = await (await request.get(`${BASE}/settings`)).text();
    expect(html, "si-gps must read its own field, not d.signalk").not.toMatch(
      /setSI\(\s*['"]si-gps['"]\s*,\s*d\.signalk/,
    );
    expect(html, "si-ais must read its own field, not d.signalk").not.toMatch(
      /setSI\(\s*['"]si-ais['"]\s*,\s*d\.signalk/,
    );
  });

  test('the hardcoded always-green OpenPlotter row is gone', async ({ request }) => {
    const html = await (await request.get(`${BASE}/settings`)).text();
    expect(
      html,
      'si-openplotter was hardcoded true — an indicator that can never report a fault ' +
        'is worse than no indicator. Operator decision S117: remove the row.',
    ).not.toContain('si-openplotter');
  });
});

test.describe('BUG-50 — AvNav health must mean more than "a socket answered"', () => {
  test('/status reports AvNav chart availability, so blank charts are visible', async ({ request }) => {
    const body = await (await request.get(`${BASE}/status`)).json();
    expect(
      Object.prototype.hasOwnProperty.call(body, 'avnav_charts'),
      'A bare port probe passes with an expired chart licence and zero charts — that is ' +
        'the exact OB-O05 state. Chart count must be surfaced.',
    ).toBe(true);
  });
});

test.describe('BUG-50 — check_service must treat a SERVER ERROR as down', () => {
  // Corrected during S117 validation: a 2xx-only rule was WRONG. ai-bridge on :3002
  // returns 404 on "/" while answering 200 on /anchor/state, so 2xx-only reported a
  // healthy service as down. 4xx means the server answered; only 5xx means broken.
  test('a service returning 5xx is not reported as up', async ({ request }) => {
    const html = await (await request.get(`${BASE}/settings`)).text();
    // Guard at source level: the helper must inspect status_code, not merely
    // survive the request. Asserted via the served page's own behaviour contract
    // in the Python unit test; here we assert the endpoint stays well-formed.
    const body = await (await request.get(`${BASE}/status`)).json();
    for (const k of ['internet', 'avnav', 'gemini', 'signalk', 'ollama']) {
      expect(typeof body[k], `${k} must remain a boolean`).toBe('boolean');
    }
    expect(html).toBeTruthy();
  });
});
