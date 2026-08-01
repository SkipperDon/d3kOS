/**
 * BUG-08 — Helm Assistant on-screen keyboard.
 *
 * The logged root-cause analysis (keyboard-fix.js v2.1 blur/timing) was performed
 * against the nginx page at /var/www/html/helm.html. That is NOT the page the
 * kiosk runs. The kiosk runs http://localhost:3000/ — the Flask dashboard — whose
 * helm-assistant.html loaded the script with an absolute `/js/keyboard-fix.js`.
 * Flask serves static from /static/, so that path returned 404 and
 * **the script never loaded on the live page at all.**
 *
 * A second blocker sat behind it: keyboard-fix.js POSTs to origin-relative
 * /keyboard/show, which nginx proxies to 127.0.0.1:8087 but Flask had no route
 * for — so even a loaded script could not have reached the keyboard API.
 *
 * These tests cover the PLUMBING, which is what was broken and what can regress
 * silently. They cannot cover whether squeekboard visually appears and accepts
 * keystrokes — that is real touch-input behaviour on the Pi's own display and
 * must be confirmed by the operator at the helm.
 *
 *   BASE_URL=http://192.168.1.237:3000 npx playwright test tests/bug08-keyboard-fix-wiring.spec.ts
 */
import { test, expect } from '@playwright/test';

const BASE = process.env.BASE_URL ?? 'http://192.168.1.237:3000';

test('BUG-08: keyboard-fix.js is served by Flask (was 404)', async ({ request }) => {
  const r = await request.get(`${BASE}/static/js/keyboard-fix.js`);
  expect(r.status(), 'the script must be served from Flask static, not only nginx').toBe(200);
  const body = await r.text();
  expect(body).toContain('keyboard/show');
});

test('BUG-08: helm-assistant references the Flask static path, not the nginx one', async ({ request }) => {
  const html = await (await request.get(`${BASE}/helm-assistant`)).text();
  expect(html, 'must use /static/js/, the Flask-served path')
    .toContain('src="/static/js/keyboard-fix.js"');
  // The old absolute nginx path must not come back.
  expect(html.match(/src="\/js\/keyboard-fix\.js"/), 'the nginx path /js/ must not be used')
    .toBeNull();
});

test('BUG-08: Flask proxies /keyboard/show and /keyboard/hide to the keyboard API', async ({ request }) => {
  for (const action of ['show', 'hide']) {
    const r = await request.post(`${BASE}/keyboard/${action}`);
    expect(r.status(), `/keyboard/${action} must be routed, not 404`).toBe(200);
    expect((await r.json()).ok, `/keyboard/${action} must report ok`).toBe(true);
  }
});

test('BUG-08: unknown keyboard actions are rejected', async ({ request }) => {
  const r = await request.post(`${BASE}/keyboard/bogus`);
  expect(r.status()).toBe(404);
});

test.describe('BUG-08 — remote browsers must NOT raise the helm keyboard', () => {
  test.use({ hasTouch: true });

  test('touching a textarea from a REMOTE host sends no /keyboard/show', async ({ page }) => {
    // Since BUG-46 the dashboard is reachable from a phone or laptop. squeekboard
    // exists only on the Pi's own display, so a remote tap must not pop a keyboard
    // up at the helm. v2.2 adds a same-machine guard; this asserts it holds.
    const calls: string[] = [];
    await page.route('**/keyboard/**', route => {
      calls.push(route.request().url());
      return route.fulfill({ status: 200, body: '{"ok":true}' });
    });

    await page.goto(BASE + '/helm-assistant', { waitUntil: 'domcontentloaded' });
    // Sanity: we really are on a non-localhost origin, or this test proves nothing.
    const host = await page.evaluate(() => window.location.hostname);
    expect(host, 'this test is only meaningful against a remote host')
      .not.toMatch(/^(localhost|127\.0\.0\.1)$/);

    const box = page.locator('#msg-input');
    await expect(box).toBeVisible();
    await box.tap();
    await page.waitForTimeout(1200);

    expect(calls, `remote tap must not call the keyboard API; got ${calls.join(', ')}`)
      .toEqual([]);
  });
});
