/**
 * BUG-49 — Header brand: logo asset 404s, and its alt-text fallback is invisible
 * in day mode.
 *
 * `index.html` references /static/images/amboat-logo.png, which did not exist in
 * the canonical tree or on the Pi. The browser therefore rendered the img's alt
 * text ("AtMyBoat d3kOS") in place of the logo — which is what the operator saw
 * and described as a "wordmark".
 *
 * That fallback text inherited --ink with no explicit colour on .sb-brand:
 *   day   #040C04 on --bar #003200 =  1.37:1  <- WCAG AA fail, invisible
 *   night #D6EDD6 on --bar #001A00 = 14.76:1  <- passes, which is why it only
 *                                               disappeared in day mode
 *
 * Two assertions, because fixing only the asset would leave the contrast defect
 * latent for the next time an image fails to load.
 *
 *   BASE_URL=http://192.168.1.237:3000 npx playwright test tests/bug49-header-brand.spec.ts
 */
import { test, expect, Page } from '@playwright/test';

const BASE = process.env.BASE_URL ?? 'http://192.168.1.237:3000';

/** WCAG 2.0 relative luminance. */
function luminance(rgb: [number, number, number]): number {
  const [r, g, b] = rgb.map(v => {
    const s = v / 255;
    return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

function contrast(a: [number, number, number], b: [number, number, number]): number {
  const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (hi + 0.05) / (lo + 0.05);
}

/** Parse a computed `rgb(...)` / `rgba(...)` string. */
function parseRGB(s: string): [number, number, number] {
  const m = s.match(/(\d+(?:\.\d+)?)/g);
  if (!m || m.length < 3) throw new Error(`cannot parse colour: ${s}`);
  return [Number(m[0]), Number(m[1]), Number(m[2])];
}

async function brandColours(page: Page) {
  return await page.evaluate(() => {
    const img = document.querySelector('.sb-brand') as HTMLElement | null;
    const bar = document.getElementById('sb');
    if (!img || !bar) throw new Error('.sb-brand or #sb not found');
    return {
      fg: getComputedStyle(img).color,
      bg: getComputedStyle(bar).backgroundColor,
    };
  });
}

test('BUG-49: the header logo asset is served (not 404)', async ({ request }) => {
  const r = await request.get(`${BASE}/static/images/amboat-logo.png`);
  expect(r.status(), 'logo asset must exist — a 404 makes the browser render alt text instead')
    .toBe(200);
  const len = Number(r.headers()['content-length'] ?? 0);
  expect(len, 'logo must be a real image, not an empty file').toBeGreaterThan(1000);
});

test('BUG-49: brand alt-text contrast passes WCAG AA in DAY mode', async ({ page }) => {
  await page.goto(BASE + '/', { waitUntil: 'domcontentloaded' });
  // Day mode = absence of the data-night attribute on <body>.
  await page.evaluate(() => document.body.removeAttribute('data-night'));

  const { fg, bg } = await brandColours(page);
  const ratio = contrast(parseRGB(fg), parseRGB(bg));
  expect(ratio, `day-mode brand contrast ${ratio.toFixed(2)}:1 (fg ${fg} on bg ${bg})`)
    .toBeGreaterThanOrEqual(4.5);
});

test('BUG-49: brand alt-text contrast passes WCAG AA in NIGHT mode', async ({ page }) => {
  await page.goto(BASE + '/', { waitUntil: 'domcontentloaded' });
  await page.evaluate(() => document.body.setAttribute('data-night', ''));

  const { fg, bg } = await brandColours(page);
  const ratio = contrast(parseRGB(fg), parseRGB(bg));
  expect(ratio, `night-mode brand contrast ${ratio.toFixed(2)}:1 (fg ${fg} on bg ${bg})`)
    .toBeGreaterThanOrEqual(4.5);
});
