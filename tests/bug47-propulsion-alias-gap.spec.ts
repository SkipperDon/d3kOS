/**
 * BUG-47 — Missing `propulsion.port.*` handler aliases.
 *
 * Signal K maps NMEA 2000 PGN 127489 (Engine Parameters, Dynamic) to
 * `propulsion.<instance>.coolantTemperature`. With a `port` instance that is
 * `propulsion.port.coolantTemperature`, for which instruments.js has no handler
 * — so the delta is silently discarded and the coolant gauge never populates.
 *
 * The BUG-29 alias block covers revolutions, oilPressure, temperature and
 * drive.trimState but missed coolantTemperature and trimTabPosition.
 *
 * This has been masked on the boat because the CX5106 has been off the N2K bus
 * since S112, so no coolant data has reached Signal K at all. The gauge will
 * STILL be dead after the CX5106 is restored unless this is fixed.
 *
 * Run (no tunnel — BUG-46 is fixed, so the real IP works):
 *   BASE_URL=http://192.168.1.237:3000 npx playwright test tests/bug47-propulsion-alias-gap.spec.ts
 */
import { test, expect, Page } from '@playwright/test';

const BASE = process.env.BASE_URL ?? 'http://192.168.1.237:3000';
const HOST = new URL(BASE).hostname;
const SK_WS = `ws://${HOST}:8099/signalk/v1/stream?subscribe=none`;

const K = (c: number) => c + 273.15;

async function injectSK(page: Page, values: Record<string, number>) {
  const ok = await page.evaluate(
    async ({ url, vals }) => {
      return await new Promise<string>((resolve) => {
        const ws = new WebSocket(url);
        const payload = JSON.stringify({
          updates: [{
            $source: 'PLAYWRIGHT-BUG47',
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
  expect(ok, 'injection must succeed or the result is meaningless').toBe('SENT');
}

/**
 * Every propulsion.0.* handler must have a matching propulsion.port.* alias.
 * Computed from the live page rather than hardcoded, so a NEW handler added
 * without its alias also fails this test.
 */
test('BUG-47: every propulsion.0.* handler has a propulsion.port.* alias', async ({ page }) => {
  await page.goto(BASE + '/', { waitUntil: 'domcontentloaded' });

  const missing = await page.evaluate(() => {
    const H = (window as any).SK_HANDLERS as Record<string, unknown>;
    if (!H) throw new Error('window.SK_HANDLERS test seam is absent');
    return Object.keys(H)
      .filter(k => k.startsWith('propulsion.0.'))
      .map(k => 'propulsion.port.' + k.slice('propulsion.0.'.length))
      .filter(want => !(want in H));
  });

  expect(missing, `these propulsion.port.* aliases are missing: ${missing.join(', ')}`)
    .toEqual([]);
});

test('BUG-47: coolant gauge populates from propulsion.port.coolantTemperature', async ({ page }) => {
  await page.addInitScript(() =>
    localStorage.setItem('d3kUnitPrefs', JSON.stringify({ temp: 'C', depth: 'm' })));
  await page.goto(BASE + '/', { waitUntil: 'domcontentloaded' });

  // ONLY the coolantTemperature path — deliberately NOT .temperature, which
  // already has an alias and would mask the gap.
  await injectSK(page, { 'propulsion.port.coolantTemperature': K(84) });

  await expect(page.locator('#cellCoolant .ic-v')).toHaveText('84°');
});

test('BUG-47: trim gauge populates from propulsion.port.trimTabPosition', async ({ page }) => {
  await page.goto(BASE + '/', { waitUntil: 'domcontentloaded' });

  // 0.2618 rad = 15 degrees
  await injectSK(page, { 'propulsion.port.trimTabPosition': 0.261799 });

  await expect(page.locator('#cellTrim .ic-v')).toHaveText('+15°');
});
