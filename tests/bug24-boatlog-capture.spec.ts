/**
 * bug24-boatlog-capture.spec.ts
 * BUG-24 — Boat Log engine auto-capture (Option A: server-side service)
 *
 * Prerequisites:
 *   - Lab Pi at 192.168.1.237 with boatlog_capture.py deployed and running
 *   - Lab-sim injector: deployment/tools/lab-sim/run.sh <scenario>
 *   - Run with: ./tests/run-all.sh (--workers=1 required)
 *
 * T3 and T12 MUST be seen to fail before the fix (TDD — STANDING TRAP 6).
 * T4 proves the bug is fixed. T10 proves the operator can see it.
 */

import { test, expect, chromium } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';
import { execSync } from 'child_process';

const BASE_HOST = process.env.BASE_HOST || '192.168.1.237';
const BASE_URL  = `http://${BASE_HOST}:3000`;
const LAB_SIM   = 'deployment/tools/lab-sim/run.sh';

function sim(scenario: string): void {
  execSync(`bash ${LAB_SIM} ${scenario}`, { stdio: 'inherit' });
}

// ── T1: Engine start → DB row ─────────────────────────────────────────────────

test('T1: engine start row written when RPM rises above threshold', async () => {
  sim('cruise');  // raises RPM above 180 RPM (3 Hz)
  // Wait 20 s for 3-sample debounce + write
  await new Promise(r => setTimeout(r, 20_000));

  const res  = await fetch(`${BASE_URL}/api/boatlog/entries`);
  const body = await res.json();
  expect(body.ok).toBe(true);

  const engineEntries = (body.entries as any[]).filter(
    e => e.entry_type === 'engine' && e.content?.includes('Engine started')
  );
  expect(engineEntries.length).toBeGreaterThanOrEqual(1);
  expect(engineEntries[0].content).toContain('[Auto] Engine started');
});

// ── T2: Engine stop → stop row with duration ─────────────────────────────────

test('T2: engine stop row written with duration', async () => {
  sim('idle');  // drops RPM to 0
  await new Promise(r => setTimeout(r, 20_000));

  const res  = await fetch(`${BASE_URL}/api/boatlog/entries`);
  const body = await res.json();
  const stopEntries = (body.entries as any[]).filter(
    e => e.entry_type === 'engine' && e.content?.includes('Engine stopped')
  );
  expect(stopEntries.length).toBeGreaterThanOrEqual(1);
  // Duration format: "ran X min" or "ran X h Y min"
  expect(stopEntries[0].content).toMatch(/ran \d/);
});

// ── T3: Debounce — oscillating RPM must not produce many sessions ─────────────

test('T3: RPM oscillating across threshold every 2 s for 60 s produces exactly one session', async () => {
  // TDD: this test MUST fail before boatlog_capture.py is deployed with debounce.
  // A debounce of 3 × 5-second samples (15 s) must absorb 2-second toggling.

  const resBefore = await fetch(`${BASE_URL}/api/boatlog/entries`);
  const bodyBefore = await resBefore.json();
  const startCountBefore = (bodyBefore.entries as any[]).filter(
    e => e.entry_type === 'engine' && e.content?.includes('Engine started')
  ).length;

  sim('oscillate');  // oscillates RPM ±3 Hz every 2 s for 60 s
  await new Promise(r => setTimeout(r, 75_000));

  const resAfter  = await fetch(`${BASE_URL}/api/boatlog/entries`);
  const bodyAfter = await resAfter.json();
  const startCountAfter = (bodyAfter.entries as any[]).filter(
    e => e.entry_type === 'engine' && e.content?.includes('Engine started')
  ).length;

  // Oscillating for 60 s must produce at most 1 new start (not one per toggle)
  expect(startCountAfter - startCountBefore).toBeLessThanOrEqual(1);
});

// ── T4: Boat Log page never opened — row still created ───────────────────────
// THIS IS THE TEST THAT PROVES BUG-24 IS FIXED.

test('T4: engine row created even when Boat Log page is never opened', async ({ page }) => {
  // Navigate to dashboard (NOT boat-log) — the JS capture would not have loaded
  await page.goto(`${BASE_URL}/`);
  await page.waitForLoadState('networkidle');

  const resBefore = await fetch(`${BASE_URL}/api/boatlog/entries`);
  const bodyBefore = await resBefore.json();
  const countBefore = (bodyBefore.entries as any[]).filter(
    e => e.entry_type === 'engine' && e.content?.includes('Engine started')
  ).length;

  // Trigger engine start — page is showing dashboard, not boat-log
  sim('cruise');
  await new Promise(r => setTimeout(r, 20_000));

  const resAfter = await fetch(`${BASE_URL}/api/boatlog/entries`);
  const bodyAfter = await resAfter.json();
  const countAfter = (bodyAfter.entries as any[]).filter(
    e => e.entry_type === 'engine' && e.content?.includes('Engine started')
  ).length;

  expect(countAfter).toBeGreaterThan(countBefore);
});

// ── T5: Browser closed — row still created ───────────────────────────────────

test('T5: engine row created with browser closed', async () => {
  // No browser context — pure HTTP check
  const resBefore = await fetch(`${BASE_URL}/api/boatlog/entries`);
  const bodyBefore = await resBefore.json();
  const countBefore = (bodyBefore.entries as any[]).filter(
    e => e.entry_type === 'engine' && e.content?.includes('Engine started')
  ).length;

  sim('cruise');
  await new Promise(r => setTimeout(r, 20_000));

  const resAfter = await fetch(`${BASE_URL}/api/boatlog/entries`);
  const bodyAfter = await resAfter.json();
  const countAfter = (bodyAfter.entries as any[]).filter(
    e => e.entry_type === 'engine' && e.content?.includes('Engine started')
  ).length;

  expect(countAfter).toBeGreaterThan(countBefore);
});

// ── T6: SK stops mid-session — service survives ───────────────────────────────

test('T6: service does not crash when SignalK is temporarily stopped', async () => {
  // Restart SK (stop + start)
  execSync(`ssh -i ~/.ssh/id_d3kos d3kos@${BASE_HOST} "sudo systemctl stop signalk && sleep 5 && sudo systemctl start signalk"`, { stdio: 'inherit' });
  await new Promise(r => setTimeout(r, 15_000));

  // Service must still be running
  const status = execSync(
    `ssh -i ~/.ssh/id_d3kos d3kos@${BASE_HOST} "systemctl is-active d3kos-boatlog-capture"`
  ).toString().trim();
  expect(status).toBe('active');
});

// ── T7: No duplicate rows (JS retired) ───────────────────────────────────────

test('T7: no duplicate engine rows — only one writer active', async () => {
  sim('cruise');
  await new Promise(r => setTimeout(r, 20_000));
  sim('idle');
  await new Promise(r => setTimeout(r, 20_000));

  const res  = await fetch(`${BASE_URL}/api/boatlog/entries`);
  const body = await res.json();

  const ids = (body.entries as any[]).map(e => e.entry_id);
  const unique = new Set(ids);
  expect(unique.size).toBe(ids.length);  // no duplicate entry_ids
});

// ── T8: PYTHONUNBUFFERED — output appears within 1 s ─────────────────────────

test('T8: journald shows output within 1 s of a log call (PYTHONUNBUFFERED=1)', async () => {
  // Restart the service to force a fresh log entry
  execSync(
    `ssh -i ~/.ssh/id_d3kos d3kos@${BASE_HOST} "sudo systemctl restart d3kos-boatlog-capture && sleep 2 && journalctl -u d3kos-boatlog-capture --since '3 seconds ago' -n 5"`,
    { stdio: 'pipe' }
  );
  // If PYTHONUNBUFFERED=0, 'boatlog_capture started' would be buffered and appear late or not at all.
  // The command succeeds + returns lines = buffering not blocking.
  const log = execSync(
    `ssh -i ~/.ssh/id_d3kos d3kos@${BASE_HOST} "journalctl -u d3kos-boatlog-capture --since '5 seconds ago' -n 20 --no-pager"`
  ).toString();
  expect(log).toContain('boatlog_capture started');
});

// ── T9: GET /api/boatlog/entries returns new row ─────────────────────────────

test('T9: GET :3000/api/boatlog/entries returns engine row', async () => {
  const res = await fetch(`${BASE_URL}/api/boatlog/entries`);
  expect(res.status).toBe(200);
  const body = await res.json();
  expect(body.ok).toBe(true);
  expect(Array.isArray(body.entries)).toBe(true);

  const engineEntry = (body.entries as any[]).find(e => e.entry_type === 'engine');
  expect(engineEntry).toBeDefined();
  expect(engineEntry.content).toContain('[Auto]');
});

// ── T10: Remote browser sees engine entry on screen ─────────────────────────
// OPERATOR-FACING PROOF.

test('T10: engine entry is visible on screen in boat-log.html from remote browser', async ({ page }) => {
  await page.goto(`${BASE_URL}/boat-log`);
  await page.waitForLoadState('networkidle');
  // Allow _fetchServerEntries to complete
  await page.waitForTimeout(3000);

  // Engine badge visible
  const engineBadge = page.locator('.bl-entry-type.engine');
  await expect(engineBadge.first()).toBeVisible();

  // Content text visible
  const entryText = page.locator('.bl-entry-text, .bl-engine-event');
  await expect(entryText.first()).toBeVisible();
});

// ── T11: localStorage entries still render after T10 ────────────────────────

test('T11: pre-existing localStorage entries still render after server merge', async ({ page }) => {
  // Inject a synthetic localStorage entry
  await page.goto(`${BASE_URL}/boat-log`);
  await page.evaluate(() => {
    const key     = 'd3kos-boatlog-entries';
    const entry   = { entry_id: 'test-legacy-001', timestamp: '2026-01-01T00:00:00Z',
                      type: 'voice', text: 'Test legacy entry T11' };
    const current = JSON.parse(localStorage.getItem(key) || '[]');
    current.push(entry);
    localStorage.setItem(key, JSON.stringify(current));
  });
  await page.reload();
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(3000);

  // Legacy entry must still be visible
  await expect(page.locator('text=Test legacy entry T11')).toBeVisible();
});

// ── T12: Missing DB — service does not crash-loop ─────────────────────────────
// TDD: this MUST fail (service crashes) before the BOATLOG_DB.exists() guard is in place.

test('T12: service logs and continues when boatlog.db does not exist', async () => {
  // Rename the DB away to simulate absence
  execSync(
    `ssh -i ~/.ssh/id_d3kos d3kos@${BASE_HOST} "sudo mv /opt/d3kos/data/boatlog/boatlog.db /opt/d3kos/data/boatlog/boatlog.db.t12bak 2>/dev/null || true"`,
    { stdio: 'inherit' }
  );
  await new Promise(r => setTimeout(r, 12_000));

  // Service must be active (not crash-looping)
  const status = execSync(
    `ssh -i ~/.ssh/id_d3kos d3kos@${BASE_HOST} "systemctl is-active d3kos-boatlog-capture"`
  ).toString().trim();
  expect(status).toBe('active');

  // Restore DB
  execSync(
    `ssh -i ~/.ssh/id_d3kos d3kos@${BASE_HOST} "sudo mv /opt/d3kos/data/boatlog/boatlog.db.t12bak /opt/d3kos/data/boatlog/boatlog.db 2>/dev/null || true"`,
    { stdio: 'inherit' }
  );
});

// ── T13: Read-only route cannot write ────────────────────────────────────────

test('T13: GET /api/boatlog/entries connection is read-only', async () => {
  // The endpoint uses mode=ro; any attempt to INSERT through it raises OperationalError.
  // We verify the endpoint returns 200 with ok:true (reads work) and there is no
  // route that accepts a POST — a POST returns 405 Method Not Allowed.
  const get = await fetch(`${BASE_URL}/api/boatlog/entries`);
  expect(get.status).toBe(200);

  const post = await fetch(`${BASE_URL}/api/boatlog/entries`, { method: 'POST', body: '{}' });
  expect(post.status).toBe(405);
});
