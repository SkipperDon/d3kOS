# ATOMIC SPEC — BUG-24

**Defect:** Boat Log engine auto-capture never fires. The logic works; it is loaded on the wrong page.
**Severity:** MEDIUM — a feature that silently does nothing.
**Tier:** Tier 3 implementable. **G6 CLEARED — operator chose Option A on 2026-08-28 (S135).**
**Created:** 2026-08-24 (S131) · **Rewritten:** 2026-08-28 (S135) after reading the live code
**Bug record:** `V09994_BUG_FIXES.md` BUG-24 (re-diagnosed S116; original hypothesis disproved)

---

## 0. WHAT CHANGED IN S135 — read this before section 3

S131 wrote sections 1–2 from the documents. S135 read the **live Pi and the actual source files** and
found the defect is **larger than "the script is on the wrong page."** Three further faults sit in the
same path, all confirmed on `192.168.1.237`:

| # | Fault | Evidence (live, 2026-08-28) |
|---|---|---|
| F1 | **`/api/boatlog/engine-entry` does not exist.** `boatlog-engine.js:85` POSTs to it. | `grep -c engine-entry` on the **deployed** `boatlog-export-api.py` → **0**. The API serves only `/status`, `/export`, `/voice-note`, `/health`. |
| F2 | **The POST is silently discarded.** | `boatlog-engine.js:89` — `.catch(function () { /* API unavailable */ })`. A 404 looks identical to success. |
| F3 | **`boatlog-export-api.py` binds loopback only.** | `app.run(host='127.0.0.1', port=8095)` → live: `LISTEN 127.0.0.1:8095`. `boat-log.html:316` builds `http://<window.location.hostname>:8095`, so **every** :8095 call fails whenever the page is served over the LAN IP — not just engine capture, but voice-note, export and status too. |

**Consequence:** even on the one page where capture *did* run, entries only ever reached browser
`localStorage`. Nothing engine-related has ever been persisted. The live DB confirms it:

```
boatlog_entries by type:  predictive_alert 72 · text 1 · voice 2 · engine 0
```

⚠ **F3 is wider than BUG-24 and must be logged as its own bug before it is fixed** (standing rule: no fix
without a BUG-XX entry). This spec is designed so that **BUG-24 does not depend on F3 being fixed** —
see §3.3.

---

## 1. VERIFIED ROOT CAUSE — confirmed S131, re-confirmed S135

`boatlog-engine.js` is referenced by exactly **one** template — `boat-log.html:617`. The capture logic
itself is sound:

```js
line 18:  var RPM_THRESHOLD_HZ = 3;              /* 3 Hz = 180 RPM — engine considered running */
line 93:  function _checkEngineState(rpmHz) {
line 94:    var isRunning = rpmHz > RPM_THRESHOLD_HZ;
```

**Auto-capture only runs while the operator is looking at the Boat Log page.** In normal use the helm
shows the dashboard, so the engine starts, runs and stops with nothing watching.

⚠ **Do not re-diagnose the threshold or the RPM path.** Both are correct, and BUG-29's `propulsion.port.*`
aliases are already present at `boatlog-engine.js:172-175`. The defect is *where the code lives*.

---

## 2. THE DECISION — RESOLVED

Client-side capture cannot work: the page may not be open, Chromium may be showing AvNav, the screen may
sleep, the launcher may restart the browser.

- **Option A — server-side capture service.** ✅ **CHOSEN by operator, S135 2026-08-28.**
- **Option B — load the JS on every page.** Rejected. Converts "never captures" into "captures
  sometimes", which is harder to diagnose than a clean failure.
- **Option C — Node-RED flow.** Rejected. Node-RED is disabled until Phase 4.

---

## 3. IMPLEMENTATION — Option A

### 3.1 ⚠ Model on `predictive_maintenance.py`, NOT `alert_watcher.py`

S131 recommended `alert_watcher.py`. **That recommendation is superseded.**
`opt/d3kos/services/predictive/predictive_maintenance.py` already does this exact job on this exact
database, and is running in production — it wrote all 72 `predictive_alert` rows. *Diff against what
works.* Copy these four patterns verbatim:

| Pattern | Anchor in `predictive_maintenance.py` |
|---|---|
| Read engine data from SK **REST on localhost** (not a WebSocket) | `:56` `SK_ENGINE_URL = 'http://localhost:8099/signalk/v1/api/vessels/self/propulsion/port'`; fetched at `:177` `requests.get(SK_ENGINE_URL, timeout=5)` |
| Write straight to `boatlog.db` — **no HTTP hop** | `:271` `def write_boatlog(message)`; INSERT at `:279` |
| Guard on DB absence rather than crashing | `:273` `if not BOATLOG_DB.exists(): … return` |
| Cooldown to suppress repeats | `_alert_times[category] = time.monotonic()` |

⚠ **`localhost` here is correct and must stay.** BUG-46/48 removed `localhost` from **front-end** code
because it resolves in the *browser*. This is server-side Python on the Pi — `app.py` keeps localhost for
the same reason. Do not "fix" it.

### 3.2 Writing to the existing schema — NO MIGRATION

Live schema, read from the Pi 2026-08-28:

```sql
CREATE TABLE boatlog_entries (
    entry_id TEXT PRIMARY KEY, timestamp TEXT, entry_type TEXT, content TEXT,
    latitude REAL, longitude REAL, weather_conditions TEXT
)
```

There is no column for `rpm`, `oil_psi`, `coolant_c` or duration. **Do not add one.** Follow the
`predictive_alert` precedent exactly: `entry_type='engine'`, readings rendered into `content` as text.

```
[Auto] Engine started — 720 RPM, oil 47 PSI, coolant 78.5 °C, fuel 64%
[Auto] Engine running — 2350 RPM, oil 47 PSI, coolant 82.1 °C, fuel 61%
[Auto] Engine stopped — ran 1 h 42 min
```

This keeps `/api/boatlog/export` working unchanged (it selects only the seven existing columns) and
avoids a migration on a live SQLite file. Operator preference is **Imperial** — PSI and °F where the
dashboard uses them; match `instruments.js`, do not invent a second convention.

### 3.3 The UI read path — serve it from the dashboard, not :8095

**Without this, BUG-24 is not fixed.** `boat-log.html` renders from `localStorage` only
(`:345 _load()` → `:392 renderEntries()`). A service writing to SQLite would still show the operator
nothing.

**Add `GET /api/boatlog/entries` to `opt/d3kos/services/dashboard/app.py` (port 3000)** — *not* to
`boatlog-export-api.py`.

Why the dashboard:
- **Same origin** as the page. No CORS, no second port, no new firewall surface.
- **Sidesteps F3 entirely** — :3000 is already reachable remotely; :8095 is loopback-bound and BUG-24
  must not be blocked behind fixing that.
- `app.py` is already the page server and already the pattern-holder for `/api/*` routes
  (`:496 @app.route('/api/recovery-key')`).

⚠ `app.py` does **not** currently import `sqlite3`. Add the import. Open the DB **read-only**
(`sqlite3.connect('file:…?mode=ro', uri=True)`) — the dashboard must never write to the log.

Then in `boat-log.html`: fetch server entries on load, merge with the legacy `localStorage` list, dedupe
on `entry_id`, sort by timestamp descending. **Keep the localStorage read** — operators have existing
entries in their browsers and this change must not make them vanish.

### 3.4 Service shape

| Item | Value |
|---|---|
| Code | `opt/d3kos/services/boatlog/boatlog_capture.py` |
| Unit | `etc/systemd/system/d3kos-boatlog-capture.service` |
| User / Group | `d3kos` / `d3kos` — matches `d3kos-boatlog-api.service` |
| Poll interval | 5 s |
| Threshold | `RPM_THRESHOLD_HZ = 3` (180 RPM) — the value from `boatlog-engine.js:18` |
| Debounce | **3 consecutive samples (15 s)** must agree before the state flips |
| Snapshot | one `running` entry every 30 min, matching `boatlog-engine.js:19` |
| Restart | `Restart=always`, `RestartSec=10` |

⛔ **`Environment=PYTHONUNBUFFERED=1` is mandatory in the unit.** BUG-54 hid five months of failures for
exactly this reason: under systemd stdout is a socket, not a TTY, so CPython block-buffers `print()` at
8 KB. Prefer `logging` (as `predictive_maintenance.py` does) **and** set the variable — belt and braces.

### 3.5 Retire the JS capture path

Two writers is worse than none. In the same change:

1. Delete `<script src="…/boatlog-engine.js">` from `boat-log.html:617`.
2. Leave `boatlog-engine.js` **on disk**, with a header comment stating it is retired by BUG-24 and why.
   ⚠ **Do not delete the file.** BUG-08's lesson is that a deleted script's history is what proves the
   diagnosis later.
3. `window.renderEntries` (`boat-log.html:431`) exists solely so the JS can trigger a re-render. Keep the
   function; drop the comment that explains it as the JS hook.

This also resolves S131's "share the threshold constant, do not retype it" — after retirement there is
only one definition.

---

## 4. TESTS — LAB-SIM makes this desk-testable

Runner: `./tests/run-all.sh` (the only runner — `--workers=1`).
Injector: `deployment/tools/lab-sim/run.sh <scenario>`.

| # | Scenario | Expect |
|---|---|---|
| T1 | `run.sh cruise` — RPM rises above threshold and holds 15 s+ | exactly one `engine` / start row in `boatlog_entries` |
| T2 | RPM returns to 0 and holds | matching stop row, `content` carries a duration |
| **T3** | **RPM oscillates across the threshold every 2 s for 60 s** | **exactly one session, not many** — proves the 3-sample debounce |
| **T4** | **Dashboard open, Boat Log page never opened** | **row still created — this is the test that proves BUG-24 is fixed** |
| T5 | Browser closed entirely | row still created |
| T6 | Signal K stopped mid-session, restarted | service does not exit; `requests` timeout handled; session closed or resumed coherently |
| T7 | JS retired | exactly one row per session — no duplicates |
| T8 | `journalctl -u d3kos-boatlog-capture` shows output within 1 s of a log call | proves `PYTHONUNBUFFERED=1` (BUG-54 guard) |
| T9 | `GET :3000/api/boatlog/entries` after T1 | JSON includes the new row |
| T10 | Load `boat-log.html` from a **remote** browser after T1 | the engine entry is **visible on screen** — the operator-facing proof |
| T11 | Pre-existing `localStorage` entries still render after T10 | legacy entries not destroyed |
| **T12** | **Negative: point the service at a DB path that does not exist** | logs and continues; **does not crash-loop** (BUG-23a: a watchdog hot-looped at 39% CPU and ~2,536 log lines/min) |
| T13 | `GET :3000/api/boatlog/entries` cannot write | attempt an INSERT through the route's connection → fails; read-only mode proven |

**T4 proves the bug is fixed. T10 proves the operator can see it. T3 and T12 are the two most likely to
fail on a first attempt.**

⚠ **T3 and T12 must be seen to fail before the fix** (TDD, non-negotiable) — a guard test that has never
failed has not been proven to bite (STANDING TRAP 6).

---

## 5. DEFINITION OF DONE

- [x] Operator has chosen A — **G6 cleared 2026-08-28**
- [ ] T1–T13 written **first**, T3/T4/T12 observed failing pre-fix
- [ ] T4 passes with the Boat Log page never opened
- [ ] T10 passes from a remote browser — entry visible on screen
- [ ] T3 passes — no spurious sessions from threshold noise
- [ ] JS capture retired; T7 confirms no duplicates; file kept on disk with a header note
- [ ] `PYTHONUNBUFFERED=1` present and proven by T8
- [ ] No schema migration performed
- [ ] `release-state.sh` run **before and after** deploy; `MANIFEST.md5` regenerated as part of the deploy
- [ ] BUG-24 entry updated in `V09994_BUG_FIXES.md` **and** PART 17 with the chosen option and reason
- [ ] Lab Pi only. **Boat Pi is out of scope by operator directive, S135.**

---

## 6. WHAT THIS DOES NOT FIX — log separately, do not fold in

- **F3 — `boatlog-export-api.py` loopback bind.** Breaks voice-note, export and status from any remote
  browser. Wider than BUG-24. **Log as a new bug before fixing.** §3.3 routes around it deliberately.
- **F1 — the absent `/api/boatlog/engine-entry` endpoint.** Once the JS is retired nothing calls it, so
  this spec does not build it. Record the finding so a future session does not "restore" a dead endpoint.
- **BUG-23b** — voice transcription. No STT engine installed; moved to v0.9.9.5. Unrelated.
  ⚠ Note: `boatlog-export-api.py:42` references a **Vosk** model path, so an STT path was at least
  attempted here. Do not treat that as contradicting BUG-23b without checking whether the model exists.
- **Engine hours accuracy.** This logs sessions from RPM. Whether that is the authoritative hour meter is
  separate — the CX5106 may report hours directly. **Do not conflate; log a new item if wanted.**
- **`electrical.batteries.0.voltage`** (`boatlog-engine.js:162`) — BUG-17 closed battery monitoring as out
  of scope. **Do not carry the battery threshold into the Python service.**
