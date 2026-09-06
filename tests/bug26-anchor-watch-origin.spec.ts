import { test, expect } from '@playwright/test';

const BASE = process.env.BASE_URL ?? 'http://192.168.1.237:3000';
// Derive expected AI_BRIDGE host from BASE_URL (matches BUG-48 fix: window.location.hostname)
const BASE_HOST = new URL(BASE).hostname;

test.describe('BUG-26: Anchor Watch Set Anchor origin fix', () => {
  test('Anchor Set endpoint called on :3002 (AI_BRIDGE) not :3000 (dashboard)', async ({ page }) => {
    // Intercept all fetch requests to verify the URL origin
    const requests: string[] = [];
    page.on('request', (request) => {
      if (request.url().includes('/anchor/set')) {
        requests.push(request.url());
      }
    });

    await page.goto(BASE + '/anchor-watch');

    // Set a radius value
    const slider = await page.locator('#aw-radius');
    await slider.fill('25');

    // Click Set Anchor button
    const setBtn = await page.locator('#btn-set');
    await setBtn.click();

    // Wait a moment for the fetch to be initiated
    await page.waitForTimeout(500);

    const setAnchorRequest = requests.find(url => url.includes('/anchor/set'));
    if (setAnchorRequest) {
      // BUG-48 fix: host must be derived from the page, NOT hardcoded localhost.
      // Assert: URL uses the correct host (same as the page) and the AI_BRIDGE port 3002.
      await expect(setAnchorRequest).toContain(BASE_HOST + ':3002');
      // BUG-53 regression guard: localhost must NOT appear — BUG-48 removed it.
      await expect(setAnchorRequest).not.toContain('localhost');
    }
  });

  test('Verify AI_BRIDGE constant uses window.location.hostname (BUG-48 fix)', async ({ page }) => {
    const response = await page.goto(BASE + '/anchor-watch');
    const content = await response?.text() || '';

    // BUG-48 contract: AI_BRIDGE must be derived from the page's hostname, NOT literal.
    expect(content).toContain("window.location.hostname");
    expect(content).toContain("':3002'");

    // BUG-53 regression guard: old hardcoded form must NOT be present.
    expect(content).not.toContain("'http://localhost:3002'");

    // Anchor paths still use AI_BRIDGE prefix (the fetch paths themselves are unchanged).
    expect(content).toContain("fetch(AI_BRIDGE + '/anchor/set'");
    expect(content).toContain("fetch(AI_BRIDGE + '/anchor/clear'");
    expect(content).toContain("fetch(AI_BRIDGE + '/anchor/dismiss'");
    expect(content).toContain("fetch(AI_BRIDGE + '/anchor/advice'");
    expect(content).toContain("fetch(AI_BRIDGE + '/anchor/state'");

    // Verify no bare /anchor/ fetches remain (BUG-26 original fix still holds).
    expect(content).not.toMatch(/fetch\(['"]\/anchor\//);
  });
});
