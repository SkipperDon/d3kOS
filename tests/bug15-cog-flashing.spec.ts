import { test, expect } from '@playwright/test';

const BASE = process.env.BASE_URL ?? 'http://192.168.1.237:3000';

test.describe('BUG-15: COG flashing when stationary', () => {
  test('Scenario A: COG held when stationary (SOG < 0.5 kn)', async ({ page }) => {
    await page.goto(BASE + '/');

    // Set SOG = 0 m/s (stationary)
    await page.evaluate(() => {
      (window as any).SK_HANDLERS['navigation.speedOverGround'](0);
    });

    // Feed an initial COG value (10°)
    await page.evaluate(() => {
      (window as any).SK_HANDLERS['navigation.courseOverGroundTrue'](0.1745); // 10°
    });

    // Get initial COG display
    const initialCourse = await page.locator('#cellCourse .ic-v').textContent();

    // Feed second COG (200°) — should NOT update
    await page.evaluate(() => {
      (window as any).SK_HANDLERS['navigation.courseOverGroundTrue'](3.4907); // 200°
    });
    const course2 = await page.locator('#cellCourse .ic-v').textContent();
    await expect(course2).toBe(initialCourse);

    // Feed third COG (45°) — should NOT update
    await page.evaluate(() => {
      (window as any).SK_HANDLERS['navigation.courseOverGroundTrue'](0.7854); // 45°
    });
    const course3 = await page.locator('#cellCourse .ic-v').textContent();
    await expect(course3).toBe(initialCourse);
  });

  test('Scenario B: COG updates when moving (SOG >= 0.5 kn)', async ({ page }) => {
    await page.goto(BASE + '/');

    // Set SOG = ~3 kn (1.543 m/s)
    await page.evaluate(() => {
      (window as any).SK_HANDLERS['navigation.speedOverGround'](1.543);
    });

    // Feed COG = 90°
    await page.evaluate(() => {
      (window as any).SK_HANDLERS['navigation.courseOverGroundTrue'](1.5708); // 90°
    });

    // Assert COG shows "90°"
    const courseText = await page.locator('#cellCourse .ic-v').textContent();
    await expect(courseText).toBe('90°');
  });
});
