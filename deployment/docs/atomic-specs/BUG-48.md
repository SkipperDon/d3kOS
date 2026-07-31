# Atomic Spec — BUG-48: Remaining Hardcoded `localhost` Service URLs

**Version:** 1.0.0
**Session:** S114 — 2026-07-31
**Author:** Opus (Tier 1 architect)
**Implementer:** Tier 3 (Ollama `devstral:24b`)
**Verifier:** Opus, AAO §25.8
**Risk level:** LOW — browser-side URL strings only. No backend, no schema, no
config. Fully reversible with `git checkout`.

---

## WHY THIS SPEC EXISTS

`localhost` in front-end code is resolved by the **browser**, not the server. When
the d3kOS dashboard is opened from a phone, tablet or laptop, every `localhost`
URL points at *that device's* loopback, where no d3kOS service is running.

BUG-46 fixed this for the Signal K WebSocket, so the gauges now work remotely.
Everything else does not: AI navigation, cameras, AvNav, anchor watch, document
upload, manuals, boatlog and the weather panel all fail silently.

This is the **third** time this defect class has been fixed one file at a time
(BUG-34 → BUG-46 → BUG-48). Step 4 of this spec adds a guard test so there is no
fourth.

---

## THE PATTERN — use this exact form everywhere

```js
'http://' + window.location.hostname + ':<PORT>' + '<path>'
```

This is the pattern already established by BUG-34 in `overlays.js:75` and by
BUG-46 in `instruments.js:9`. **Do not invent a different one.** Do not create a
helper module, do not add a config endpoint, do not use `window.location.origin`
(the port differs from the page's port).

---

## WHAT TIER 3 MUST NOT DO

- Do NOT change any port number. Ports stay exactly as they are.
- Do NOT change any path or query string.
- Do NOT touch `templates/index.html:191` — it is server-rendered Jinja
  (`src="http://localhost:{{ avnav_port }}"`). It needs a different approach and
  is explicitly OUT OF SCOPE. Leave it alone. It is handled in Step 5 as a
  reported finding only.
- Do NOT modify comment blocks that merely mention `localhost` for documentation
  (e.g. `connectivity-check.js` lines 7–10 are a comment header — leave them).
- Do NOT touch any file under `deployment/v0.9.4/pi_source/` or `d3kOS/dashboard/`
  — both are SUPERSEDED read-only reference trees.
- Do NOT deploy to the Pi. No ssh, no scp. Tier 1 deploys.
- Do NOT commit.
- Do NOT regenerate MANIFEST.md5.

---

## SCOPE — exactly these edits, in `deployment/v0.9.9.4/opt/d3kos/services/dashboard/`

Verify each line matches before editing. If a line does not match, STOP and report.

### Group A — `static/js/` (7 files)

| # | File | Line | Current | Port |
|---|---|---|---|---|
| A1 | `static/js/helm.js` | 15 | `const GEMINI_URL = 'http://localhost:3001/ask';` | 3001 |
| A2 | `static/js/instruments.js` | 13 | `const AVNAV_API    = 'http://localhost:8080/viewer/avnav_navi.php';` | 8080 |
| A3 | `static/js/instruments.js` | 14 | `const _BRIDGE_URL  = 'http://localhost:3002'; // prefixed to avoid conflict with ai-bridge.js` | 3002 |
| A4 | `static/js/instruments.js` | 521 | `if (fsFrame) fsFrame.src = 'http://localhost/weather.html';` | 80 (no port) |
| A5 | `static/js/boatlog-engine.js` | 16 | `var API_URL          = 'http://localhost:8095';` | 8095 |
| A6 | `static/js/cameras.js` | 7 | `const CAM_API   = 'http://localhost:8084';` | 8084 |
| A7 | `static/js/ai-bridge.js` | 7 | `const AI_BRIDGE = 'http://localhost:3002';` | 3002 |
| A8 | `static/js/panel-toggle.js` | 49 | `frame.src = cfg.avnavUrl \|\| 'http://localhost:8080';` | 8080 |
| A9 | `static/js/panel-toggle.js` | 116 | `window.open('http://localhost:' + port, '_blank');` | variable |
| A10 | `static/js/panel-toggle.js` | 124 | `window.open('http://localhost:8084', '_blank');` | 8084 |

**A4 special case** — no port. Correct result:
```js
if (fsFrame) fsFrame.src = 'http://' + window.location.hostname + '/weather.html';
```

**A9 special case** — the port is already a variable. Correct result:
```js
window.open('http://' + window.location.hostname + ':' + port, '_blank');
```

**A3 note** — keep the existing trailing comment
`// prefixed to avoid conflict with ai-bridge.js`. Do not drop it.

**All line numbers verified against the repo on 2026-07-31 after the BUG-46 and
BUG-47 commits.** If a line number is off, locate by content — the content
strings in the table are exact.

### Group B — `templates/` (5 files)

| # | File | Line | Current | Port |
|---|---|---|---|---|
| B1 | `templates/anchor-watch.html` | 203 | `const AI_BRIDGE = 'http://localhost:3002';` | 3002 |
| B2 | `templates/anchor-watch.html` | 399 | `var _sse = new EventSource('http://localhost:3002/stream');` | 3002 |
| B3 | `templates/ai-navigation.html` | 233 | `const resp = await fetch('http://localhost:3001/ask', {` | 3001 |
| B4 | `templates/upload-documents.html` | 187 | `const resp = await fetch('http://localhost:8081/upload/manual', {` | 8081 |
| B5 | `templates/manage-documents.html` | 172 | `const resp = await fetch('http://localhost:8083/manuals/list', ...` | 8083 |
| B6 | `templates/manage-documents.html` | 246 | `` `http://localhost:8083/manuals/delete/${encodeURIComponent(filename)}`, `` | 8083 |
| B7 | `templates/helm-assistant.html` | ~645 | `const gemRes  = await fetch('http://localhost:3001/ask', {` | 3001 |
| B8 | `templates/marine-vision.html` | 476 | `var CAM_API    = 'http://localhost:8084';` | 8084 |

**B6 special case** — it is a template literal. Correct result:
```js
`http://${window.location.hostname}:8083/manuals/delete/${encodeURIComponent(filename)}`,
```
Inside a template literal use `${window.location.hostname}`, not string concatenation.

### Group C — user-facing error strings (do NOT change the text, only verify)

These mention `localhost` in operator-facing messages. **Leave them exactly as
they are** — changing user-visible copy is out of scope and requires operator
approval:
- `templates/upload-documents.html:216`
- `templates/ai-navigation.html:267`
- `templates/manage-documents.html:218`

Report them in your Decision Log as "left unchanged per spec Group C".

---

## TDD — MANDATORY SEQUENCE, NO SHORTCUTS

### Step 1 — write the guard test FIRST

Create `tests/bug48-no-hardcoded-localhost.spec.ts`:

```ts
/**
 * BUG-48 — no served JS or template may hardcode a localhost service URL.
 *
 * `localhost` is resolved by the BROWSER. Any hardcoded localhost URL is dead on
 * every device except the Pi's own screen. This is the third occurrence of this
 * class (BUG-34, BUG-46, BUG-48); this test exists so there is no fourth.
 */
import { test, expect } from '@playwright/test';

const BASE = process.env.BASE_URL ?? 'http://192.168.1.237:3000';

const JS_FILES = [
  'helm.js', 'instruments.js', 'boatlog-engine.js', 'cameras.js',
  'ai-bridge.js', 'panel-toggle.js', 'overlays.js',
];

const PAGES = [
  '/', '/settings', '/anchor-watch', '/ai-navigation',
  '/upload-documents', '/manage-documents', '/helm-assistant', '/marine-vision',
];

// Matches a real URL, not a comment mentioning the word.
const BAD = /(?:https?:|ws:)\/\/localhost/;

for (const f of JS_FILES) {
  test(`BUG-48: ${f} has no hardcoded localhost URL`, async ({ request }) => {
    const r = await request.get(`${BASE}/static/js/${f}`);
    if (r.status() === 404) test.skip(true, `${f} not served`);
    const body = await r.text();
    const hits = body.split('\n')
      .map((l, i) => [i + 1, l] as [number, string])
      .filter(([, l]) => BAD.test(l) && !l.trim().startsWith('*') && !l.trim().startsWith('//'));
    expect(hits.map(([n, l]) => `${n}: ${l.trim()}`), `hardcoded localhost in ${f}`).toEqual([]);
  });
}

for (const p of PAGES) {
  test(`BUG-48: page ${p} has no hardcoded localhost URL`, async ({ request }) => {
    const r = await request.get(BASE + p);
    if (r.status() !== 200) test.skip(true, `${p} returned ${r.status()}`);
    const body = await r.text();
    const hits = body.split('\n')
      .map((l, i) => [i + 1, l] as [number, string])
      // index.html AvNav iframe is server-rendered Jinja — out of scope, see spec.
      .filter(([, l]) => BAD.test(l) && !l.includes('avnav_port'))
      .filter(([, l]) => !l.trim().startsWith('*') && !l.trim().startsWith('//'))
      // Group C: operator-facing error text mentioning localhost is allowed.
      .filter(([, l]) => !/Could not reach|not responding|Check that/.test(l));
    expect(hits.map(([n, l]) => `${n}: ${l.trim()}`), `hardcoded localhost in ${p}`).toEqual([]);
  });
}
```

### Step 2 — RUN IT. Paste the real terminal output.

```
cd /home/boatiq/Helm-OS
export LD_LIBRARY_PATH="$HOME/.local/pw-libs/root/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH"
BASE_URL=http://192.168.1.237:3000 npx playwright test tests/bug48-no-hardcoded-localhost.spec.ts --reporter=list
```

It MUST FAIL, listing the hardcoded URLs. Tier 1 confirmed this is the current
state. **If it passes, STOP and escalate — you are testing the wrong target.**

Note: this runs against the **deployed lab Pi**, which Tier 1 has NOT yet updated
with your edits. Your edits go in the repo. After Step 3, the test will still fail
until Tier 1 deploys. That is expected — see "What to return".

### Step 3 — make the edits

Groups A and B only. One file at a time.

### Step 4 — re-run and paste output

Run against the repo copy is not possible for a served-file test, so instead run:
```
grep -rnE "(https?:|ws:)//localhost" deployment/v0.9.9.4/opt/d3kos/services/dashboard/static/js/ deployment/v0.9.9.4/opt/d3kos/services/dashboard/templates/ | grep -v avnav_port
```
The ONLY remaining hits must be the Group C error strings and comment lines.
Paste the real output.

### Step 5 — syntax check every edited JS file

```
for f in helm.js instruments.js boatlog-engine.js cameras.js ai-bridge.js panel-toggle.js; do
  node --check deployment/v0.9.9.4/opt/d3kos/services/dashboard/static/js/$f && echo "$f OK"
done
```
Paste the real output. All must be OK.

---

## IF YOU ARE UNSURE ABOUT ANYTHING

Do not guess and do not invent a default. File a question at
`wiki/questions/2026-07-31-<slug>.md`, add a pointer to `wiki/index.md`, record
your provisional assumption, and continue with the other edits. Do NOT assume on
anything touching ports or paths.

---

## WHEN DONE, RETURN

1. `git diff --stat` — expect ~11 files changed, roughly 18 insertions / 18 deletions
2. `git diff` for `static/js/panel-toggle.js` and `templates/manage-documents.html`
   in full (these have the two trickiest edits, A9 and B6)
3. The failing Step 2 output AND the Step 4 grep output AND the Step 5 syntax output
4. Decision Log: every deviation from this spec, or "none"

---

## TIER 1 VERIFICATION CHECKLIST (§25.8 — Opus performs, not Tier 3)

- [ ] No port number changed anywhere — diff every `:<port>` against the table
- [ ] No path or query string changed
- [ ] `templates/index.html:191` untouched
- [ ] Group C error strings untouched
- [ ] A4 has no port segment (`hostname + '/weather.html'`)
- [ ] A9 keeps the `port` variable
- [ ] B6 uses `${window.location.hostname}` inside the template literal, not concatenation
- [ ] `node --check` passes on all 6 edited JS files
- [ ] No file outside the dashboard directory modified
- [ ] After deploy: `bug48` suite green, and BUG-43/46/47 suites still 14/14
