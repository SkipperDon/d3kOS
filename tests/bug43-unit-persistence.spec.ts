/**
 * BUG-43 — Settings unit selection (Imperial/Metric) has no effect on gauges.
 *
 * Symptom (on-boat, S112): operator set Imperial, dashboard kept showing metric.
 * The "Save Display Settings" button only called showToast() and saved nothing.
 *
 * These tests drive the REAL dashboard in a REAL browser against a REAL Signal K
 * server, injecting synthetic deltas the same way LAB-SIM does. They assert on
 * rendered DOM text — not on source code — because "the source contains the
 * conversion" is not evidence that the gauge displays it.
 *
 * Environment
 * -----------
 *   BASE_URL   dashboard root      (default http://192.168.1.237:3000)
 *   SK_WS      Signal K websocket  (default derived from BASE_URL, port 8099)
 *
 * Run:
 *   npx playwright test tests/bug43-unit-persistence.spec.ts
 *   npx playwright test tests/bug43-unit-persistence.spec.ts --headed
 *
 * Troubleshooting:
 *   - All assertions time out          -> dashboard unreachable, check BASE_URL
 *   - Cells stay "---"                 -> Signal K unreachable from the browser,
 *                                         check SK_WS host/port and that
 *                                         security is disabled on the SK server
 *   - Coolant right, depth wrong       -> _renderDepth not converting; BUG-43
 *                                         Step 4 was not applied
 */
import { test, expect, Page } from '@playwright/test';

const BASE = process.env.BASE_URL ?? 'http://192.168.1.237:3000';
const SK_WS = process.env.SK_WS ?? `ws://${new URL(BASE).hostname}:8099/signalk/v1/stream?subscribe=none`;

/** Kelvin for a given Celsius value. Signal K stores temperature in K. */
const K = (c: number) => c + 273.15;

/**
 * Push Signal K deltas from inside the browser, tagged so simulated data is
 * always distinguishable from real sensor data.
 *
 * Sent repeatedly: the dashboard clears all cells on init (_markAllDash) and
 * only fills them when a delta arrives, so a single shot can race the page load.
 */
async function injectSK(page: Page, values: Record<string, number>, repeats = 6) {
  await page.evaluate(
    async ({ url, vals, n }) => {
      await new Promise<void>((resolve, reject) => {
        const ws = new WebSocket(url);
        const payload = JSON.stringify({
          updates: [{
            $source: 'PLAYWRIGHT-BUG43',
            values: Object.entries(vals).map(([path, value]) => ({ path, value })),
          }],
        });
        ws.onerror = () => reject(new Error('Signal K websocket failed: ' + url));
        ws.onopen = () => {
          let sent = 0;
          const t = setInterval(() => {
            ws.send(payload);
            if (++sent >= n) { clearInterval(t); ws.close(); resolve(); }
          }, 250);
        };
      });
    },
    { url: SK_WS, vals: values, n: repeats },
  );
}

/** Seed localStorage BEFORE the page scripts run, so _init() reads it. */
async function withPrefs(page: Page, prefs: { temp: string; depth: string } | null) {
  await page.addInitScript((p) => {
    if (p === null) localStorage.removeItem('d3kUnitPrefs');
    else localStorage.setItem('d3kUnitPrefs', JSON.stringify(p));
  }, prefs);
}

/**
 * Open a dashboard page.
 *
 * waitUntil:'domcontentloaded' is REQUIRED. The dashboard opens a Signal K
 * WebSocket and a route SSE stream that stay open for the life of the page, so
 * the 'load' event (Playwright's default) never fires and goto() times out.
 */
async function openPage(page: Page, path: string) {
  await page.goto(BASE + path, { waitUntil: 'domcontentloaded' });
}

const val = (page: Page, cell: string) => page.locator(`#${cell} .ic-v`);
const unit = (page: Page, cell: string) => page.locator(`#${cell} .ic-u`);

// ---------------------------------------------------------------------------

test.describe('BUG-43 — unit preference is applied to gauges', () => {

  test('default with no saved preference renders IMPERIAL (operator default)', async ({ page }) => {
    // Purpose: operator preference is Imperial; a fresh install must not show metric.
    await withPrefs(page, null);
    await openPage(page, '/');
    await injectSK(page, {
      // NOTE: 'propulsion.port.coolantTemperature' has NO handler in
      // instruments.js — the BUG-29 alias block covers revolutions, oilPressure,
      // temperature and drive.trimState but NOT coolantTemperature. Use the
      // alias that actually exists.
      'propulsion.port.temperature': K(100),   // 100 C == 212 F exactly
      'environment.depth.belowTransducer': 3.048,     // 3.048 m == 10.0 ft exactly
    });

    await expect(val(page, 'cellCoolant')).toHaveText('212°');
    await expect(unit(page, 'cellCoolant')).toContainText('°F');
    await expect(val(page, 'cellDepth')).toHaveText('10.0');
    await expect(unit(page, 'cellDepth')).toContainText('ft');
  });

  test('saved IMPERIAL preference renders °F and feet', async ({ page }) => {
    await withPrefs(page, { temp: 'F', depth: 'ft' });
    await openPage(page, '/');
    await injectSK(page, {
      // NOTE: 'propulsion.port.coolantTemperature' has NO handler in
      // instruments.js — the BUG-29 alias block covers revolutions, oilPressure,
      // temperature and drive.trimState but NOT coolantTemperature. Use the
      // alias that actually exists.
      'propulsion.port.temperature': K(100),
      'environment.depth.belowTransducer': 3.048,
    });

    await expect(val(page, 'cellCoolant')).toHaveText('212°');
    await expect(unit(page, 'cellCoolant')).toContainText('°F');
    await expect(val(page, 'cellDepth')).toHaveText('10.0');
    await expect(unit(page, 'cellDepth')).toContainText('ft');
  });

  test('saved METRIC preference renders °C and metres', async ({ page }) => {
    // This is the assertion that fails hardest pre-fix: pre-fix the dashboard
    // was ALWAYS metric, so it would pass metric and fail imperial. Both
    // directions are asserted so neither hard-coded unit can pass the suite.
    await withPrefs(page, { temp: 'C', depth: 'm' });
    await openPage(page, '/');
    await injectSK(page, {
      // NOTE: 'propulsion.port.coolantTemperature' has NO handler in
      // instruments.js — the BUG-29 alias block covers revolutions, oilPressure,
      // temperature and drive.trimState but NOT coolantTemperature. Use the
      // alias that actually exists.
      'propulsion.port.temperature': K(100),
      'environment.depth.belowTransducer': 3.048,
    });

    await expect(val(page, 'cellCoolant')).toHaveText('100°');
    await expect(unit(page, 'cellCoolant')).toContainText('°C');
    await expect(val(page, 'cellDepth')).toHaveText('3.0');
    // Source is 'transducer' (we inject belowTransducer), so the metric label is
    // "m · UNDER TRANSDUCER". The word "metres" only appears for a keel source.
    await expect(unit(page, 'cellDepth')).toContainText('m ·');
  });

  test('preference survives a reload', async ({ page }) => {
    await withPrefs(page, { temp: 'C', depth: 'm' });
    await openPage(page, '/');
    await page.reload({ waitUntil: 'domcontentloaded' });
    await injectSK(page, { 'environment.depth.belowTransducer': 3.048 });

    await expect(val(page, 'cellDepth')).toHaveText('3.0');
  });
});

test.describe('BUG-43 — unit change must NOT move the alarm thresholds', () => {

  test('depth advisory still fires on raw metres while displaying feet', async ({ page }) => {
    // THR.depth = { adv: 3, alrt: 2, crit: 1 } in METRES.
    // 2.5 m is below the 3 m advisory. Displayed in feet it reads 8.2, which is
    // nowhere near 3 — so if the threshold were ever evaluated on the converted
    // number the advisory would silently stop firing. That is the dangerous
    // failure mode this test exists to catch.
    await withPrefs(page, { temp: 'F', depth: 'ft' });
    await openPage(page, '/');
    await injectSK(page, { 'environment.depth.belowTransducer': 2.5 });

    await expect(val(page, 'cellDepth')).toHaveText('8.2');          // 2.5 m in feet
    await expect(page.locator('#cellDepth')).toHaveClass(/\badv\b/); // still advisory
  });

  test('coolant advisory still fires on raw Celsius while displaying °F', async ({ page }) => {
    // THR.coolant.adv = 88 °C. 90 °C = 194 °F. The advisory must fire on 90,
    // not on 194 being compared against 88.
    await withPrefs(page, { temp: 'F', depth: 'ft' });
    await openPage(page, '/');
    await injectSK(page, { 'propulsion.port.temperature': K(90) });

    await expect(val(page, 'cellCoolant')).toHaveText('194°');
    await expect(page.locator('#cellCoolant')).toHaveClass(/\badv\b/);
  });
});

test.describe('BUG-43 — settings page actually persists the choice', () => {

  test('Save Display Settings writes d3kUnitPrefs to localStorage', async ({ page }) => {
    // Pre-fix this button called showToast() only and wrote nothing.
    await openPage(page, '/settings');
    await page.evaluate(() => localStorage.removeItem('d3kUnitPrefs'));

    // Unchecked == Imperial, which is the default, so no toggle click is needed.
    // Confirm the visible label agrees before saving.
    await expect(page.locator('#met-lbl')).toHaveText('Imperial');
    await expect(page.locator('#met-tog')).not.toBeChecked();
    await page.getByRole('button', { name: /Save Display Settings/i }).click();

    const saved = await page.evaluate(() => localStorage.getItem('d3kUnitPrefs'));
    expect(saved).not.toBeNull();
    expect(JSON.parse(saved as string)).toEqual({ temp: 'F', depth: 'ft' });
  });

  test('toggling to Metric saves °C and metres', async ({ page }) => {
    await openPage(page, '/settings');
    await page.evaluate(() => localStorage.removeItem('d3kUnitPrefs'));

    // #met-tog is an opacity-0 checkbox positioned outside the viewport; the
    // operator taps the .tslider span. Click what the operator clicks.
    // Scope to the label wrapping #met-tog — the settings page has ~9 toggles.
    await page.locator('label.toggle:has(#met-tog) .tslider').click();
    await expect(page.locator('#met-lbl')).toHaveText('Metric');
    await expect(page.locator('#met-tog')).toBeChecked();
    await page.getByRole('button', { name: /Save Display Settings/i }).click();

    const saved = await page.evaluate(() => localStorage.getItem('d3kUnitPrefs'));
    expect(JSON.parse(saved as string)).toEqual({ temp: 'C', depth: 'm' });
  });
});
