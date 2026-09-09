/**
 * registration-flow.spec.ts — BUG-111/112/113/114/115/116/119 regression guards
 *
 * Tests written to FAIL against pre-fix code (TDD — Step 7 of spec).
 * Each test is documented with current (failing) behaviour and expected (passing) behaviour.
 *
 * Prerequisites:
 *   - Lab Pi running at BASE_URL (default http://192.168.1.237:3000)
 *   - Pi device APPROVED in wp-admin (generate-reg-token returns 200)
 *
 * Run: BASE_URL=http://192.168.1.237:3000 npx playwright test tests/registration-flow.spec.ts --workers=1
 *
 * Spec: deployment/docs/atomic-specs/BUG-111-118-REGISTRATION.md §8 (Step 7)
 * TDD status: written BEFORE any Pi deploy — expected RED on current code.
 */

import { test, expect } from '@playwright/test';

const BASE = process.env.BASE_URL ?? 'http://192.168.1.237:3000';

// ---------------------------------------------------------------------------
// Helper — navigate to wizard step 6
// ---------------------------------------------------------------------------
async function goToStep6(page: any) {
  await page.goto(`${BASE}/setup`);
  await page.waitForLoadState('networkidle');
  await page.evaluate(() => (window as any).goTo(6));
  // Wait for the step panel to be active
  await page.waitForSelector('#wiz-6.active', { timeout: 5000 });
}

// ---------------------------------------------------------------------------
// T1 — QR payload must be an https://atmyboat.com/register/?rt= URL
// Current: initQR() encodes 'd3kos://pair/' + DEVICE_UUID — no phone camera handler
// Expected: fetch /api/generate-reg-token, encode register_url in QR
// ---------------------------------------------------------------------------
test('T1: Step 6 QR encodes https://atmyboat.com/register URL, not d3kos://', async ({ page }) => {
  try {
    await goToStep6(page);
    await page.waitForSelector('#reg-state-code', { timeout: 12000 });

    // No d3kos:// anywhere in the step 6 DOM
    const step6Text = await page.locator('#wiz-6').textContent();
    expect(step6Text).not.toContain('d3kos://');

    // A link whose href contains the registration URL must exist
    const link = page.locator('#reg-state-code a[href*="atmyboat.com/register/?rt="]').first();
    await expect(link).toBeVisible();
    const href = await link.getAttribute('href');
    expect(href).toMatch(/https:\/\/atmyboat\.com\/register\/\?rt=[A-Z2-9]{7}/);
  } catch (err) {
    await page.screenshot({ path: 'test-results/T1-failure.png' });
    throw err;
  }
});

// ---------------------------------------------------------------------------
// T2 — 403 from endpoint shows pending-approval state (not broken QR)
// Current: no state containers exist; error path not handled
// Expected: #reg-state-pending visible, no QR canvas children, Skip ≥48×48px
// ---------------------------------------------------------------------------
test('T2: 403 response shows pending-approval state, Skip button present', async ({ page }) => {
  try {
    await page.route('**/api/generate-reg-token', route =>
      route.fulfill({ status: 403, body: JSON.stringify({ success: false, error: 'Device not approved' }) })
    );

    await goToStep6(page);
    await page.waitForSelector('#reg-state-pending', { timeout: 6000 });

    await expect(page.locator('#reg-state-pending')).toBeVisible();

    // QR canvas must have no children (no broken QR rendered)
    const childCount = await page.locator('#qr-canvas').evaluate((el: Element) => el.children.length);
    expect(childCount).toBe(0);

    // Skip button present and large enough
    const skip = page.locator('#wiz-6 button.btn-skip-step');
    await expect(skip).toBeVisible();
    const box = await skip.boundingBox();
    expect(box?.height).toBeGreaterThanOrEqual(48);
    expect(box?.width).toBeGreaterThanOrEqual(48);
  } catch (err) {
    await page.screenshot({ path: 'test-results/T2-failure.png' });
    throw err;
  }
});

// ---------------------------------------------------------------------------
// T3 — Network abort shows offline state with Settings → Community guidance
// Current: no offline state container exists
// Expected: #reg-state-offline visible with text naming Settings and Community
// ---------------------------------------------------------------------------
test('T3: Network abort shows offline state with Settings/Community text', async ({ page }) => {
  try {
    await page.route('**/api/generate-reg-token', route => route.abort());

    await goToStep6(page);
    await page.waitForSelector('#reg-state-offline', { timeout: 6000 });

    const offlineEl = page.locator('#reg-state-offline');
    await expect(offlineEl).toBeVisible();

    const text = await offlineEl.textContent() ?? '';
    expect(text).toContain('Settings');
    expect(text).toContain('Community');
  } catch (err) {
    await page.screenshot({ path: 'test-results/T3-failure.png' });
    throw err;
  }
});

// ---------------------------------------------------------------------------
// T4 — CDN blocked; QR must still render via local /static/js/qrcode.min.js
// Current: qrcode.min.js loaded from cdnjs.cloudflare.com only → no local fallback
// Expected: local file serves library; canvas has children even offline
// ---------------------------------------------------------------------------
test('T4: CDN blocked — QR still renders via local library (BUG-113)', async ({ page }) => {
  try {
    await page.route('https://cdnjs.cloudflare.com/**', route => route.abort());

    await goToStep6(page);
    // Give enough time for any local script load + fetch
    await page.waitForSelector('#reg-state-code', { timeout: 8000 });
    await page.waitForTimeout(1000);

    const canvasChildren = await page.locator('#qr-canvas').evaluate((el: Element) => el.children.length);
    expect(canvasChildren).toBeGreaterThan(0);
  } catch (err) {
    await page.screenshot({ path: 'test-results/T4-failure.png' });
    throw err;
  }
});

// ---------------------------------------------------------------------------
// T5 — Settings token display shows bare code, no R- prefix
// Current: line 707 sets textContent = d.token (which is "R-XXXXXXX")
// Expected: strip "R-", display only the 7-char code
// ---------------------------------------------------------------------------
test('T5: Settings token display shows bare code matching /^[A-Z2-9]{7}$/', async ({ page }) => {
  try {
    await page.goto(`${BASE}/settings`);
    await page.waitForLoadState('networkidle');

    // Trigger the token fetch by clicking the button
    const getCodeBtn = page.locator('button[onclick*="generateRegToken"]');
    await expect(getCodeBtn).toBeVisible({ timeout: 5000 });
    await getCodeBtn.click();

    // Wait for the display to have non-empty content
    const display = page.locator('#reg-token-display');
    await expect(display).not.toHaveText('', { timeout: 8000 });

    const tokenText = (await display.textContent() ?? '').trim();
    expect(tokenText).not.toMatch(/^R-/);
    expect(tokenText).toMatch(/^[A-Z2-9]{7}$/);
  } catch (err) {
    await page.screenshot({ path: 'test-results/T5-failure.png' });
    throw err;
  }
});

// ---------------------------------------------------------------------------
// T6 — Anonymity language present in every visible Step 6 state
// Current: no state containers exist → no anonymity language anywhere
// Expected: each state container shows "optional"/"anonymous"/"without" text
// ---------------------------------------------------------------------------
test('T6: All visible Step 6 states include anonymity language', async ({ page }) => {
  try {
    await goToStep6(page);
    await page.waitForTimeout(2000);

    const stateSelectors = [
      '#reg-state-loading',
      '#reg-state-code',
      '#reg-state-pending',
      '#reg-state-offline',
      '#reg-state-error',
    ];
    const keywords = ['optional', 'anonymous', 'without'];

    let visibleCount = 0;
    for (const sel of stateSelectors) {
      const el = page.locator(sel);
      const isVisible = await el.isVisible().catch(() => false);
      if (isVisible) {
        visibleCount++;
        const text = (await el.textContent() ?? '').toLowerCase();
        const hasKeyword = keywords.some(k => text.includes(k));
        expect(hasKeyword, `${sel} missing anonymity language`).toBeTruthy();
      }
    }

    // At least one state must be active — vacuous pass is not acceptable
    expect(visibleCount, 'No state containers found — fix not yet applied').toBeGreaterThan(0);
  } catch (err) {
    await page.screenshot({ path: 'test-results/T6-failure.png' });
    throw err;
  }
});

// ---------------------------------------------------------------------------
// T7 — Every element inside new Step 6 state containers ≥ 18px (AODA)
// Current: no state containers exist → test fails on waitForSelector
// Expected: all rendered text ≥ 18px computed font-size
// ---------------------------------------------------------------------------
test('T7: All Step 6 state container elements have font-size ≥ 18px', async ({ page }) => {
  try {
    await goToStep6(page);
    // Must wait for at least one state container to exist after fix
    await page.waitForSelector('#reg-state-loading, #reg-state-code, #reg-state-pending', { timeout: 6000 });

    const stateSelectors = [
      '#reg-state-loading',
      '#reg-state-code',
      '#reg-state-pending',
      '#reg-state-offline',
      '#reg-state-error',
    ];

    for (const sel of stateSelectors) {
      const exists = await page.locator(sel).count() > 0;
      if (!exists) continue;

      const elements = page.locator(`${sel} *`);
      const count = await elements.count();
      for (let i = 0; i < count; i++) {
        const el = elements.nth(i);
        const fontSize = await el.evaluate((e: Element) =>
          parseFloat(window.getComputedStyle(e).fontSize)
        );
        if (fontSize > 0) {
          expect(fontSize, `${sel} element has font-size ${fontSize}px — must be ≥ 18px`).toBeGreaterThanOrEqual(18);
        }
      }
    }
  } catch (err) {
    await page.screenshot({ path: 'test-results/T7-failure.png' });
    throw err;
  }
});

// ---------------------------------------------------------------------------
// T8 — Skip on Step 6 advances wizard to Step 7 (regression guard)
// Current: Skip button exists (onclick="goTo(7)") — may already pass
// Expected: wizard reaches #wiz-7.active with no error
// ---------------------------------------------------------------------------
test('T8: Skip on Step 6 advances wizard to Step 7', async ({ page }) => {
  try {
    await goToStep6(page);

    // Don't wait for state containers — Skip must work regardless of fetch state
    const skip = page.locator('#wiz-6 button.btn-skip-step');
    await expect(skip).toBeVisible({ timeout: 5000 });
    await skip.click();
    await page.waitForTimeout(500);

    // Step 7 (#wiz-7) must become active
    await expect(page.locator('#wiz-7')).toHaveClass(/active/, { timeout: 3000 });
  } catch (err) {
    await page.screenshot({ path: 'test-results/T8-failure.png' });
    throw err;
  }
});
