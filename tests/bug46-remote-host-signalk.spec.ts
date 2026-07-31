/**
 * BUG-46 — Dashboard Signal K WebSocket hardcoded to `localhost`.
 *
 * `const SK_WS_URL = 'ws://localhost:8099/signalk/v1/stream'` is resolved by the
 * BROWSER, not the server. Loaded from any device other than the Pi's own screen,
 * `localhost` points at that device's loopback, where no Signal K server exists.
 * The socket never opens and every instrument cell stays "---" forever.
 *
 * This test MUST be run against the Pi's real IP with NO SSH tunnel. Tunnelling
 * port 8099 to localhost is precisely what masks this bug.
 *
 *   BASE_URL=http://192.168.1.237:3000 npx playwright test tests/bug46-remote-host-signalk.spec.ts
 *
 * If BASE_URL points at localhost the test refuses to run, because a pass would
 * be meaningless.
 */
import { test, expect, Page } from '@playwright/test';

const BASE = process.env.BASE_URL ?? 'http://192.168.1.237:3000';
const HOST = new URL(BASE).hostname;
const SK_WS = `ws://${HOST}:8099/signalk/v1/stream?subscribe=none`;

test.beforeAll(() => {
  if (HOST === 'localhost' || HOST === '127.0.0.1') {
    throw new Error(
      `BUG-46 must be tested against a REMOTE host, not ${HOST}. ` +
      `A tunnel or a localhost BASE_URL hides the defect. Set BASE_URL to the Pi's IP.`,
    );
  }
});

/** Push deltas straight into the Pi's Signal K, independent of the dashboard. */
async function injectSK(page: Page, values: Record<string, number>) {
  const ok = await page.evaluate(
    async ({ url, vals }) => {
      return await new Promise<string>((resolve) => {
        const ws = new WebSocket(url);
        const payload = JSON.stringify({
          updates: [{
            $source: 'PLAYWRIGHT-BUG46',
            values: Object.entries(vals).map(([path, value]) => ({ path, value })),
          }],
        });
        ws.onerror = () => resolve('WS_ERROR');
        ws.onopen = () => {
          let n = 0;
          const t = setInterval(() => {
            ws.send(payload);
            if (++n >= 8) { clearInterval(t); resolve('SENT'); }
          }, 300);
        };
        setTimeout(() => resolve('WS_TIMEOUT'), 10000);
      });
    },
    { url: SK_WS, vals: values },
  );
  // Guard: if injection itself failed the test would report a false BUG-46.
  expect(ok, 'injection into Signal K must succeed for this test to be meaningful').toBe('SENT');
}

test('BUG-46: gauges populate when the dashboard is loaded from a remote host', async ({ page }) => {
  await page.goto(BASE + '/', { waitUntil: 'domcontentloaded' });

  await injectSK(page, {
    'environment.depth.belowTransducer': 3.048,
    'propulsion.port.temperature': 373.15,
  });

  // Pre-fix these stay "---" because the dashboard's own SK socket never opened.
  await expect(page.locator('#cellDepth .ic-v')).not.toHaveText('---');
  await expect(page.locator('#cellCoolant .ic-v')).not.toHaveText('---');
});

test('BUG-46: SK_WS_URL served to the browser is not hardcoded to localhost', async ({ page }) => {
  // Source-level guard so the defect cannot silently return in a future edit.
  const js = await (await page.request.get(BASE + '/static/js/instruments.js')).text();
  expect(js, 'instruments.js must not hardcode a localhost Signal K socket')
    .not.toContain("'ws://localhost:8099");
});

test('BUG-46: boatlog-engine.js does not hardcode a localhost Signal K socket', async ({ page }) => {
  const js = await (await page.request.get(BASE + '/static/js/boatlog-engine.js')).text();
  expect(js).not.toContain("'ws://localhost:8099");
});
