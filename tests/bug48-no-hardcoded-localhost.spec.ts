/**
 * BUG-48 — no served JS or template may hardcode a localhost service URL.
 *
 * `localhost` is resolved by the BROWSER. Any hardcoded localhost URL in
 * front-end code is dead on every device except the Pi's own screen. This is the
 * third occurrence of this class (BUG-34 → BUG-46 → BUG-48); this test exists so
 * there is no fourth.
 *
 * Scope note: app.py is deliberately NOT covered. It is server-side Python
 * running ON the Pi, where `localhost` genuinely means the Pi and is correct.
 *
 * Run against the Pi's real IP (no tunnel — BUG-46 is fixed):
 *   BASE_URL=http://192.168.1.237:3000 npx playwright test tests/bug48-no-hardcoded-localhost.spec.ts
 */
import { test, expect } from '@playwright/test';

const BASE = process.env.BASE_URL ?? 'http://192.168.1.237:3000';

const JS_FILES = [
  'helm.js', 'instruments.js', 'boatlog-engine.js', 'cameras.js',
  'ai-bridge.js', 'panel-toggle.js', 'overlays.js', 'nav.js',
  'connectivity-check.js',
];

const PAGES = [
  '/', '/settings', '/anchor-watch', '/ai-navigation', '/boat-log',
  '/upload-documents', '/manage-documents', '/helm-assistant',
  '/marine-vision', '/engine-monitor',
];

/** A real URL, not the bare word in prose. */
const BAD = /(?:https?:|ws:)\/\/localhost/;

/** Comment lines and operator-facing copy are allowed to say "localhost". */
function offenders(body: string, extraAllow: RegExp[] = []): string[] {
  return body.split('\n')
    .map((l, i) => [i + 1, l] as [number, string])
    .filter(([, l]) => BAD.test(l))
    .filter(([, l]) => {
      const t = l.trim();
      if (t.startsWith('*') || t.startsWith('//') || t.startsWith('/*')) return false;
      return !extraAllow.some(re => re.test(l));
    })
    .map(([n, l]) => `${n}: ${l.trim()}`);
}

const PAGE_ALLOW = [
  /showToast\(/,                      // operator-facing diagnostic text
  /<td|<code>|ph-desc|doc-desc/,      // documentation copy shown to the operator
  /si-sub/,                           // status-panel labels
];

for (const f of JS_FILES) {
  test(`BUG-48: ${f} has no hardcoded localhost URL`, async ({ request }) => {
    const r = await request.get(`${BASE}/static/js/${f}`);
    if (r.status() !== 200) test.skip(true, `${f} returned ${r.status()}`);
    expect(offenders(await r.text()), `hardcoded localhost in ${f}`).toEqual([]);
  });
}

for (const p of PAGES) {
  test(`BUG-48: page ${p} has no hardcoded localhost URL`, async ({ request }) => {
    const r = await request.get(BASE + p);
    if (r.status() !== 200) test.skip(true, `${p} returned ${r.status()}`);
    expect(offenders(await r.text(), PAGE_ALLOW), `hardcoded localhost in ${p}`).toEqual([]);
  });
}
