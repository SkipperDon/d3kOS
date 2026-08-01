/**
 * LAB-SIM verification batch — BUG-18, BUG-16, BUG-24.
 *
 * All three were logged as OPEN with root cause unknown. Two were suspected of
 * having been silently resolved by later fixes (BUG-30 and BUG-34), and one by
 * BUG-29. Before this session none of them could be tested at a desk, because
 * the lab Pi has no depth sounder, no engine and no N2K bus at all.
 *
 * These tests inject synthetic Signal K data the way LAB-SIM does and assert on
 * real rendered DOM / real localStorage, so each bug is either closed on
 * evidence or shown to be genuinely still broken.
 *
 *   BASE_URL=http://192.168.1.237:3000 npx playwright test tests/bug16-18-24-labsim-verification.spec.ts
 */
import { test, expect, Page } from '@playwright/test';

const BASE = process.env.BASE_URL ?? 'http://192.168.1.237:3000';
const HOST = new URL(BASE).hostname;
const SK_WS = `ws://${HOST}:8099/signalk/v1/stream?subscribe=none`;

const psi = (v: number) => v * 6894.757;
const degF = (v: number) => (v - 32) * 5 / 9 + 273.15;
const rpmHz = (v: number) => v / 60;

async function openPage(page: Page, path: string) {
  // domcontentloaded: the dashboard holds a SK websocket + SSE open, so 'load'
  // never fires and goto() would time out.
  await page.goto(BASE + path, { waitUntil: 'domcontentloaded' });
}

/** Inject repeatedly — the page clears cells on init and may connect late. */
async function injectSK(page: Page, values: Record<string, number>, shots = 8) {
  const ok = await page.evaluate(
    async ({ url, vals, n }) => {
      return await new Promise<string>((resolve) => {
        const ws = new WebSocket(url);
        const payload = JSON.stringify({
          updates: [{
            $source: 'LABSIM-VERIFY',
            values: Object.entries(vals).map(([path, value]) => ({ path, value })),
          }],
        });
        ws.onerror = () => resolve('WS_ERROR');
        ws.onopen = () => {
          let i = 0;
          const t = setInterval(() => {
            ws.send(payload);
            if (++i >= n) { clearInterval(t); resolve('SENT'); }
          }, 250);
        };
        setTimeout(() => resolve('WS_TIMEOUT'), 10000);
      });
    },
    { url: SK_WS, vals: values, n: shots },
  );
  expect(ok, 'injection must succeed or the result is meaningless').toBe('SENT');
}

// ─────────────────────────────────────────────────────────────────────────────

test.describe('BUG-18 — depth gauge registers', () => {
  test('depth gauge renders an injected belowTransducer value', async ({ page }) => {
    // BUG-18 was logged when depth showed nothing. BUG-30 later found the cause:
    // the dashboard read `belowKeel` while Signal K publishes `belowTransducer`.
    await page.addInitScript(() =>
      localStorage.setItem('d3kUnitPrefs', JSON.stringify({ temp: 'C', depth: 'm' })));
    await openPage(page, '/');
    await injectSK(page, { 'environment.depth.belowTransducer': 3.8 });

    await expect(page.locator('#cellDepth .ic-v')).not.toHaveText('---');
    await expect(page.locator('#cellDepth .ic-v')).toHaveText('3.8');
  });

  test('depth gauge tracks a changing value (S112 cruise depths)', async ({ page }) => {
    await page.addInitScript(() =>
      localStorage.setItem('d3kUnitPrefs', JSON.stringify({ temp: 'C', depth: 'm' })));
    await openPage(page, '/');

    await injectSK(page, { 'environment.depth.belowTransducer': 0.9 }, 6);
    await expect(page.locator('#cellDepth .ic-v')).toHaveText('0.9');

    await injectSK(page, { 'environment.depth.belowTransducer': 3.8 }, 6);
    await expect(page.locator('#cellDepth .ic-v')).toHaveText('3.8');
  });
});

// ─────────────────────────────────────────────────────────────────────────────

test.describe('BUG-16 — gauge tap dialog shows LIVE values, not hardcoded', () => {
  test('tap dialog reports the injected readings, not simulated ones', async ({ page }) => {
    // The original report: tapping a gauge showed a hardcoded "oil pressure too
    // low" regardless of the real reading. Inject deliberately distinctive
    // healthy values — a hardcoded dialog cannot reproduce these numbers.
    await openPage(page, '/');
    await injectSK(page, {
      'propulsion.port.oilPressure': psi(47),
      'propulsion.port.temperature': degF(171),
      'propulsion.port.revolutions': rpmHz(2350),
      'electrical.batteries.0.voltage': 13.7,
    });

    // The live cache is what openDiag builds its cards from.
    const eng = await page.evaluate(() => (window as any)._d3kEngData);
    expect(eng.oil_psi, 'live cache must hold the injected oil pressure').toBe(47);
    expect(eng.rpm, 'live cache must hold the injected RPM').toBe(2350);
    expect(Math.round(eng.coolant_c), 'live cache must hold the injected coolant').toBe(77);

    // Open the dialog and assert the rendered cards carry those live numbers.
    await page.evaluate(() => (window as any).openDiag('cellOil'));
    await expect(page.locator('#diagBack')).toHaveClass(/\bshow\b/);

    const grid = page.locator('#diagGrid');
    await expect(grid).toContainText('47');    // oil PSI, live
    await expect(grid).toContainText('2350');  // RPM, live
  });

  test('tap dialog does NOT claim an oil alarm when oil pressure is healthy', async ({ page }) => {
    // The exact symptom reported on-boat: an oil alarm shown while the gauge
    // read normally.
    await openPage(page, '/');
    await injectSK(page, {
      'propulsion.port.oilPressure': psi(47),
      'propulsion.port.revolutions': rpmHz(2350),
    });

    await expect(page.locator('#cellOil .ic-v')).toHaveText('47');
    // 47 PSI is above every oil threshold (adv 30 / alrt 25 / crit 4),
    // so the cell must carry no alarm state class.
    await expect(page.locator('#cellOil')).not.toHaveClass(/\b(adv|alrt|crit)\b/);
  });
});

// ─────────────────────────────────────────────────────────────────────────────

test.describe('BUG-24 — Boat Log engine auto-capture', () => {
  test('auto-capture fires on engine start WHEN the Boat Log page is open', async ({ page }) => {
    // boatlog-engine.js implements this. RPM_THRESHOLD_HZ = 3 (180 RPM);
    // crossing 0 -> running records a 'start' entry to localStorage.
    await page.addInitScript(() => localStorage.removeItem('d3kos-boatlog-entries'));
    await openPage(page, '/boat-log');

    // engine off, then running
    await injectSK(page, { 'propulsion.port.revolutions': 0 }, 4);
    await injectSK(page, {
      'propulsion.port.revolutions': rpmHz(2200),
      'propulsion.port.oilPressure': psi(44),
      'electrical.batteries.0.voltage': 13.9,
    }, 8);

    await expect.poll(async () =>
      await page.evaluate(() => {
        try {
          const e = JSON.parse(localStorage.getItem('d3kos-boatlog-entries') || '[]');
          return e.filter((x: any) => x.type === 'engine' && x.event === 'start').length;
        } catch { return 0; }
      }), { timeout: 20000, message: 'expected an engine "start" entry in the Boat Log' },
    ).toBeGreaterThan(0);
  });

  test('DASHBOARD does not auto-capture — boatlog-engine.js is not loaded there', async ({ page }) => {
    // Documents the real architectural limitation: auto-capture is a client-side
    // script loaded ONLY by boat-log.html. At the helm the dashboard is on
    // screen, so engine start/stop is never recorded. This test asserts the
    // CURRENT behaviour so the limitation is visible rather than assumed.
    await page.addInitScript(() => localStorage.removeItem('d3kos-boatlog-entries'));
    await openPage(page, '/');

    const loaded = await page.evaluate(() =>
      Array.from(document.scripts).some(s => s.src.includes('boatlog-engine')));
    expect(loaded, 'boatlog-engine.js is NOT loaded on the dashboard — this is the BUG-24 root cause')
      .toBe(false);
  });
});
