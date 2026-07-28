# Atomic Spec — BUG-29 (dashboard subscribes engine paths Signal K never publishes)

**Format:** AAO §23.5 Atomic Spec · §25 escalation-enabled · §24 Question Queue
**Created:** 2026-07-27 (S108-cont) by Tier 1 (Opus 5)
**Tracker:** `deployment/docs/V09994_BUG_FIXES.md` BUG-29 · `PROJECT_CHECKLIST.md` PART 17
**Questions:** `wiki/questions/2026-07-27-v0994-tier3-spec-questions.md` — read Q0.1–Q0.5
**Blocks:** BUG-16 and BUG-24 (both are fully downstream of this)
**Depends on:** BUG-36 (the `_d3kEngData` cache must exist for the fix to have anywhere to write)

---

## Tier-1 findings — three things S107 did not have

### 1. The instance segment is NOT configurable
`@signalk/n2k-signalk/dist/utils.js`:
```js
function skEngineId(n2k) {
    let id = n2k.fields.instance;
    if (typeof id === 'number') { return id; }                       // -> propulsion.0.*
    return id === 'Single Engine or Dual Engine Port' ? 'port' : 'starboard';  // -> propulsion.port.*
}
```
A hardcoded ternary inside a node_module. **There is no mapper setting.** The open S107 question
("maybe a mapper config beats editing files") is answered: no. Patching node_modules is not an
option — any `npm install` wipes it.

### 2. The path is genuinely unstable, which is why the fix must accept BOTH forms
`skEngineId()` returns the **number** when canboat decodes `fields.instance` numerically, and the
**string** `'port'` when it decodes the enum. Which happens depends on the device and the PGN
definition in use. On the boat (S107) it produced `propulsion.port.*`. Neither form is universally
correct, so subscribing to both is not belt-and-braces — it is the correct engineering answer.

### 3. TWO of the four paths have a wrong LEAF as well as a wrong instance
| Dashboard subscribes | Signal K actually publishes | Wrong part |
|---|---|---|
| `propulsion.0.revolutions` | `propulsion.<id>.revolutions` | instance only |
| `propulsion.0.oilPressure` | `propulsion.<id>.oilPressure` | instance only |
| `propulsion.0.coolantTemperature` | `propulsion.<id>.`**`temperature`** | instance **and leaf** |
| `propulsion.0.trimTabPosition` | `propulsion.<id>.`**`drive.trimState`** | instance **and leaf** |

Sources: `pgns/127488.js` (revolutions, `drive.trimState`), `pgns/127489.js` line 8 (`temperature`),
line 28 (`oilPressure`).

**A blind `propulsion.0.` → `propulsion.port.` string replace fixes only two of the four.** The
alias table below is explicit for that reason.

### 4. Two paths previously suspected are CORRECT — do not touch them
- `electrical.batteries.0.voltage` — `pgns/127508.js` builds `electrical.batteries.<raw instance>.voltage`
  with **no** port/starboard mapping. `0` is right. **This closes the open question flagged in PART 17.**
- `tanks.fuel.0.currentLevel` — `pgns/127505.js` uses the raw instance too, and it is the one path
  observed working on the boat.

---

## SPEC (paste this block to the Tier 3 model)

```
🔧 ATOMIC SPEC — BUG-29   (AAO §23.5 · §25 escalation-enabled)
═══════════════════════════════════════════════════════════════════════
TASK TYPE : [IMPLEMENT] — Tier 3
BUG       : BUG-29 — accept the engine paths Signal K actually publishes

FILES TO EDIT (exactly four, all under deployment/v0.9.9.4/)
  1. opt/d3kos/services/dashboard/static/js/instruments.js
  2. opt/d3kos/services/dashboard/static/js/boatlog-engine.js
  3. opt/d3kos/services/dashboard/templates/engine-monitor.html
  4. opt/d3kos/services/dashboard/templates/helm-assistant.html

THE ALIAS TABLE — the single source of truth for this task
  Every existing subscription must ALSO accept these Signal K paths:

    existing key                          ALSO accept
    ────────────────────────────────────  ──────────────────────────────────
    propulsion.0.revolutions              propulsion.port.revolutions
    propulsion.0.oilPressure              propulsion.port.oilPressure
    propulsion.0.coolantTemperature       propulsion.port.temperature
                                          propulsion.0.temperature
    propulsion.0.trimTabPosition          propulsion.port.drive.trimState
                                          propulsion.0.drive.trimState

  Note the last two rows carefully: the LEAF differs, not just the instance.
  Coolant is published as `.temperature`, and trim as `.drive.trimState`.

  DO NOT alias 'starboard' — this vessel is single-engine (vessel.env
  ENGINE_COUNT=single) and skEngineId() returns 'port' for a single engine.

  DO NOT touch electrical.batteries.0.voltage or tanks.fuel.0.currentLevel.
  Both are already correct — Signal K uses the raw numeric instance for those.

KEEP THE OLD PATHS. This is ADDITIVE. Removing propulsion.0.* would break any
setup where canboat decodes the instance numerically. Both forms must work.

PER-FILE PATTERN — each file dispatches differently, read before editing

  (1) instruments.js — receives ALL self deltas (the stream defaults to self;
      there is no explicit subscribe message). Dispatch is an exact-key lookup:
          const handler = SK_HANDLERS[path];
      So aliasing requires NO subscription change. After the SK_HANDLERS object
      literal closes, add alias keys pointing at the SAME function references —
      do not duplicate handler bodies. Do the same for _NULL_CELLS (line 240) so
      a null value on an aliased path still blanks the cell.
      NOTE: _NULL_CELLS is the ONLY path->cell map in this file. There is no
      PATH_TO_CELL map — do not go looking for one.

  (2) boatlog-engine.js — explicit `?subscribe=none` plus a subscribe list, and
      dispatch via the `_SK` object. TWO changes: add the alias keys to `_SK`
      (same function references), AND add matching { path, period } entries to
      the subscribe list. Use the SAME period as the path it aliases.

  (3) engine-monitor.html — same two-part pattern as (2): handler object keys
      plus subscribe-list entries. Match the existing periods.

  (4) helm-assistant.html — subscribe list plus a `switch (kv.path)`. Add the
      subscribe entries, and add the alias paths as ADDITIONAL fall-through
      `case` labels on the existing cases. Example shape:
          case 'propulsion.0.coolantTemperature':
          case 'propulsion.port.temperature':
          case 'propulsion.0.temperature':
            live.coolant = kv.value - 273.15; break;

CONSTRAINT BOUNDARIES (do NOT)
  • Do NOT remove or rename any existing path. Additive only.
  • Do NOT duplicate handler bodies. Alias keys must reference the SAME function.
  • Do NOT change any unit conversion, threshold, or display logic.
  • Do NOT alias 'starboard'.
  • Do NOT touch electrical.batteries.* or tanks.fuel.* — already correct.
  • Do NOT patch anything under ~/.signalk/node_modules. skEngineId() is library
    code; an npm install would wipe the patch.
  • Do NOT touch environment.depth.* — that is BUG-30, a separate spec.
  • Do NOT regenerate MANIFEST.md5. Do NOT commit. Do NOT touch the Pi.

INTERFACE CONTRACT
  For each of the four files, after the change:
    - every original path still resolves to its original handler
    - each alias path resolves to the SAME handler function (identity, not a copy)
    - files 2,3,4: every alias path also appears in the subscribe list with the
      same period as the path it aliases
    - no other path added or removed

FAILING TEST FIRST (TDD — write it, RUN IT, watch it fail, then fix)
  File: tests/bug29-engine-path-aliases.test.js     (plain Node, no server)
  Run : node tests/bug29-engine-path-aliases.test.js
  The jsdom harness for instruments.js is proven (see BUG-36). For the other
  three files, assert on the SOURCE TEXT — they are not loadable standalone.

    const { JSDOM, VirtualConsole } = require('jsdom');
    const fs = require('fs'); const assert = require('assert');
    const B = 'deployment/v0.9.9.4/opt/d3kos/services/dashboard/';

    const ALIASES = {
      'propulsion.0.revolutions':        ['propulsion.port.revolutions'],
      'propulsion.0.oilPressure':        ['propulsion.port.oilPressure'],
      'propulsion.0.coolantTemperature': ['propulsion.port.temperature',
                                          'propulsion.0.temperature'],
      'propulsion.0.trimTabPosition':    ['propulsion.port.drive.trimState',
                                          'propulsion.0.drive.trimState'],
    };

    // ---- 1. instruments.js: alias keys must share handler IDENTITY ----
    const vc = new VirtualConsole(); vc.on('jsdomError', () => {});
    const dom = new JSDOM('<!doctype html><html><body></body></html>',
                          { runScripts: 'outside-only', virtualConsole: vc });
    dom.window.eval(fs.readFileSync(B + 'static/js/instruments.js', 'utf8'));
    const H = dom.window.SK_HANDLERS;
    for (const [orig, aliases] of Object.entries(ALIASES)) {
      assert.ok(H[orig], `instruments.js: original ${orig} missing`);
      for (const a of aliases) {
        assert.ok(H[a], `instruments.js: alias ${a} not registered`);
        assert.strictEqual(H[a], H[orig],
          `instruments.js: ${a} must be the SAME function as ${orig}, not a copy`);
      }
    }
    // battery + fuel must be untouched
    assert.ok(H['electrical.batteries.0.voltage'], 'battery path must survive');
    assert.ok(!H['electrical.batteries.port.voltage'], 'battery must NOT be aliased');

    // ---- 2. behavioural: an aliased delta populates the cache (needs BUG-36) ----
    dom.window.SK_HANDLERS['propulsion.port.temperature'](368.15);
    assert.strictEqual(Math.round(dom.window._d3kEngData.coolant_c), 95,
      'a propulsion.port.temperature delta must reach the engine cache');
    dom.window.SK_HANDLERS['propulsion.port.revolutions'](30);
    assert.strictEqual(dom.window._d3kEngData.rpm, 1800,
      'a propulsion.port.revolutions delta must reach the engine cache');

    // ---- 3. the other three files: every alias present in source ----
    for (const f of ['static/js/boatlog-engine.js',
                     'templates/engine-monitor.html',
                     'templates/helm-assistant.html']) {
      const src = fs.readFileSync(B + f, 'utf8');
      for (const [orig, aliases] of Object.entries(ALIASES)) {
        if (!src.includes(orig)) continue;          // file may not use every path
        for (const a of aliases) {
          assert.ok(src.includes(a), `${f}: missing alias ${a} for ${orig}`);
        }
      }
    }

    // ---- 4. subscribe lists must carry the aliases too ----
    for (const f of ['static/js/boatlog-engine.js',
                     'templates/engine-monitor.html',
                     'templates/helm-assistant.html']) {
      const src = fs.readFileSync(B + f, 'utf8');
      for (const a of ['propulsion.port.revolutions', 'propulsion.port.temperature']) {
        if (!src.includes(a)) continue;
        assert.ok(new RegExp("path:\\s*'" + a.replace(/\./g, '\\.') + "'").test(src),
          `${f}: ${a} must appear as a { path: ... } subscribe entry`);
      }
    }

    console.log('BUG-29: ALL ASSERTIONS PASSED');

  EXPECTED BEFORE THE FIX: the first alias assertion fails —
    "instruments.js: alias propulsion.port.revolutions not registered"
  If it passes before your fix, STOP and escalate.

DONE WHEN
  • The test FAILED before your edit and PASSES after.
  • All four files changed; additions only — zero paths removed.
  • No handler body duplicated anywhere (alias keys share function identity).

ESCALATE-IF  (emit the 🔺 block — do not guess)
  • A file's dispatch shape does not match the per-file pattern above
                                  → CLARIFICATION (show the actual shape)
  • You believe a unit conversion is wrong for an aliased path
                                  → ADVICE. Do NOT change it. See the units note below.
  • You are tempted to remove the propulsion.0.* forms
                                  → STOP. Both forms must survive.
  • The BUG-36 `_d3kEngData` cache is absent from instruments.js
                                  → CLARIFICATION (BUG-29 depends on BUG-36)

PRE-FLIGHT SELF-CHECK
  1. How many files?             → exactly 4
  2. Do I remove old paths?      → never; additive only
  3. Coolant's real leaf?        → .temperature (NOT .coolantTemperature)
  4. Trim's real leaf?           → .drive.trimState (NOT .trimTabPosition)
  5. Battery/fuel?               → untouched, already correct
  6. May I patch node_modules?   → no

RETURN TO TIER 1
  • The diff for all four files
  • Terminal output: fail-before and pass-after
  • Decision Log: every deviation, or "none"
═══════════════════════════════════════════════════════════════════════
```

---

## ⚠ Units caveat — flagged, deliberately NOT fixed here

`pgns/127489.js` reads:
```js
node: 'propulsion.<id>.oilPressure',
value: function (n2k) { var kpa = Number(n2k.fields.oilPressure); return isNaN(kpa) ? null : kpa; }
```
The variable is named `kpa` but the value is returned unconverted. The dashboard applies
`v * 0.000145038` (Pa → PSI). If Signal K is emitting kPa rather than Pa, displayed oil pressure will
be **1000× low**.

`Uncertainty flag: I cannot resolve this without live PGN 127489 data. The lab Pi has no N2K source,
and S107's boat capture only ever saw 127488 from src 64 — 127489 was never observed. The variable
name may simply be misleading and the canboat field may already be Pa.`

**This is explicitly out of scope for BUG-29** and must not be "fixed" speculatively — changing a
unit conversion on a guess is how a gauge ends up confidently wrong. It becomes a **post-deploy
verification item**: with the engine running, compare the displayed oil PSI against the analogue
gauge. If it reads ~1000× low, log it as a new bug.

## Tier-1 verification pass (§25.8)

1. Alias keys share **function identity** with their originals (`===`), not copies. A copy means a
   future edit to one handler silently diverges from the other.
2. Zero paths removed across all four files.
3. `electrical.batteries.*` and `tanks.fuel.*` untouched.
4. Coolant aliases to `.temperature` and trim to `.drive.trimState` — verify the leaves, not just the
   instance segment. This is the defect most likely to be half-fixed.
5. Subscribe lists in files 2–4 carry the aliases with matching periods.
6. Nothing under `node_modules` touched.
7. **Cannot verify remotely:** that real data now reaches the gauges. That needs a deploy plus a live
   N2K source. Do not claim BUG-16 or BUG-24 fixed — both need on-boat confirmation.

## Out of scope
Pi deployment · `environment.depth.*` (BUG-30) · the oil-pressure unit question · BUG-34 thresholds ·
patching `@signalk/n2k-signalk`.
