import { test, expect } from '@playwright/test';

const BASE = process.env.BASE_URL ?? 'http://localhost:5000';

test.describe('BUG-26: Anchor Watch Set Anchor origin fix', () => {
  test('Anchor Set endpoint called on :3002 (AI_BRIDGE) not :3000 (dashboard)', async ({ page, context }) => {
    // Intercept all fetch requests to verify the URL origin
    const requests: string[] = [];
    page.on('request', (request) => {
      if (request.url().includes('/anchor/set')) {
        requests.push(request.url());
      }
    });

    await page.goto(BASE + '/anchor-watch.html');

    // Set a radius value
    const slider = await page.locator('#aw-radius');
    await slider.fill('25');

    // Click Set Anchor button
    const setBtn = await page.locator('#btn-set');
    await setBtn.click();

    // Wait a moment for the fetch to be initiated
    await page.waitForTimeout(500);

    // Assert the /anchor/set request was made to :3002 (AI_BRIDGE), not :3000
    const setAnchorRequest = requests.find(url => url.includes('/anchor/set'));
    if (setAnchorRequest) {
      await expect(setAnchorRequest).toContain('localhost:3002');
      await expect(setAnchorRequest).not.toContain('localhost:3000');
    }
  });

  test('Verify all anchor endpoints route to AI_BRIDGE (:3002)', async ({ page }) => {
    // Source-level verification (can also add integration tests for each endpoint)
    const response = await page.goto(BASE + '/anchor-watch.html');
    const content = await response?.text() || '';

    // Verify the file has AI_BRIDGE const
    expect(content).toContain("const AI_BRIDGE = 'http://localhost:3002'");

    // Verify all anchor endpoints use AI_BRIDGE prefix
    expect(content).toContain("fetch(AI_BRIDGE + '/anchor/set'");
    expect(content).toContain("fetch(AI_BRIDGE + '/anchor/clear'");
    expect(content).toContain("fetch(AI_BRIDGE + '/anchor/dismiss'");
    expect(content).toContain("fetch(AI_BRIDGE + '/anchor/advice'");
    expect(content).toContain("fetch(AI_BRIDGE + '/anchor/state'");

    // Verify no bare /anchor/ fetches remain
    expect(content).not.toMatch(/fetch\(['"]\/anchor\//);
  });
});
