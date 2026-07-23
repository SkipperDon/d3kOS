import { test, expect } from '@playwright/test';

const BASE = process.env.BASE_URL ?? 'http://localhost:5000';

test('BUG-27: helm status bar vessel name is >= 28px', async ({ page }) => {
  await page.goto(BASE + '/');
  const px = await page.locator('.sb-vessel').first()
    .evaluate(el => parseFloat(getComputedStyle(el).fontSize));
  await expect(px).toBeGreaterThanOrEqual(28);
});

test('BUG-27: helm status bar clock is >= 26px', async ({ page }) => {
  await page.goto(BASE + '/');
  const px = await page.locator('#clk').first()
    .evaluate(el => parseFloat(getComputedStyle(el).fontSize));
  await expect(px).toBeGreaterThanOrEqual(26);
});
