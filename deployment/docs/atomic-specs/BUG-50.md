# ATOMIC SPEC — BUG-50

**Author:** Tier 1 (Opus), S117 2026-08-02
**Implementer:** Tier 3 — Gemini 2.5-flash-lite, dispatched FROM the Pi
**Verifier:** Tier 1, AAO §25.8
**Failing test (must exist and fail before implementation):** `tests/bug50-status-truthfulness.spec.ts`
— confirmed **7 of 10 failing** against pre-fix code on 2026-08-02.

---

## 1. Problem

The Settings "System Status" panel reports four capabilities as healthy when they are not.
Proven live on the lab Pi: GPS shows green while `navigation/position` returns 404; AIS shows green
while Signal K holds one vessel (own ship, zero targets).

Four defects:
1. `si-gps` and `si-ais` are both wired to `d.signalk` — the Signal K **server's** liveness.
2. `si-openplotter` is hardcoded `true` and can never report a fault.
3. AvNav's check is a bare `GET localhost:8080` — passes with blank charts or AIS fetching disabled.
4. `check_service()` catches only `RequestException`, so an HTTP **500** reads as up.

---

## 2. Constraint boundaries — what Tier 3 MUST NOT do

- **Make ONLY the exact string replacements in §4.** Do not reformat, reorder, or regenerate any
  file. Whole-file regeneration is what caused BUG-36.
- **Do not touch any file other than the two named in §4.**
- **Do not change `check_internet()` or `check_ollama()`.**
- **Do not add dependencies.** `requests`, `json`, `os`, `Path` are already imported. `datetime` is
  NOT — replacement R0 adds it.
- **Do not use `localhost` in any front-end (template) code.** Server-side Python in `app.py`
  correctly uses `localhost` because it runs on the Pi (BUG-46/48 boundary — do not "fix" it).
- **Do not invent a fifth indicator or rename existing JSON keys.** `internet`, `avnav`, `gemini`,
  `ai_bridge`, `signalk`, `ollama` keep their names and boolean type.
- **Never return a two-state value for AIS.** Reporting a three-state truth as a binary is the
  defect being fixed.
- **No timeouts above 3 seconds** — `/status` is polled every 30 s and must not stall the page.

---

## 3. Interface contract — the exact `/status` JSON

```json
{
  "internet":     true,
  "avnav":        true,
  "gemini":       true,
  "ai_bridge":    true,
  "signalk":      true,
  "ollama":       false,
  "gps":          false,
  "ais":          "no_data",
  "avnav_charts": 0
}
```

| Key | Type | Definition |
|---|---|---|
| `gps` | `bool` | `true` **only if** `navigation.position` exists with both `latitude` and `longitude`, **and** its `timestamp` is within **10 seconds** of now. Anything else is `false`. |
| `ais` | `str` | `"receiving"` — ≥1 non-self vessel whose `navigation.position.timestamp` is within **300 seconds**. `"no_targets"` — Signal K reachable, zero fresh non-self vessels. `"no_data"` — Signal K unreachable or the vessels query failed. |
| `avnav_charts` | `int` or `null` | Chart count from AvNav's own status API. `null` if AvNav did not answer. |
| `avnav` | `bool` | `true` only if AvNav's status API returns HTTP 200 **and** the body parses as JSON containing a `handler` list. A listening socket alone is not health. |

**Freshness thresholds (operator-approved S117):** GPS **10 s**, AIS **300 s**.

**Why `"no_targets"` is a distinct state:** "nothing in range" is completely normal at sea. Calling
it a fault trains the operator to ignore the indicator. It is also **genuinely ambiguous** —
Signal K alone cannot distinguish "no vessels nearby" from "receiver is dead". The UI label must
say `NO TARGETS`, in amber, and must not claim the receiver is healthy.

---

## 4. Exact replacements

### FILE A — `opt/d3kos/services/dashboard/app.py`

#### R0 — add the datetime import

**OLD** (exact, one occurrence):
```python
from pathlib import Path
```
**NEW:**
```python
from pathlib import Path
from datetime import datetime, timezone
```

#### R1 — `check_service()` must treat a SERVER ERROR as down

> ⚠ **SPEC DEFECT CORRECTED DURING S117 VALIDATION.** This section originally specified
> `200 <= status < 300`. That is **wrong** and was caught by live validation: ai-bridge on
> :3002 returns **404 on `/`** while answering **200 on `/anchor/state`** — it is alive. A
> 2xx-only rule reported it as down, turning "this service has no root route" into "this
> service is broken". Signal K and AvNav only escaped because `requests` follows their
> 301/302 to a 200. **The correct rule is `status_code < 500`:** connection refused → down,
> 5xx → down, but 2xx/3xx/4xx all mean the service answered. The deployed code uses `< 500`.
> This was a Tier 1 spec error, not a Tier 3 implementation error.

**OLD** (exact, one occurrence):
```python
def check_service(port: str) -> bool:
    """Return True if a local service answers on the given port."""
    try:
        requests.get(f'http://localhost:{port}', timeout=2)
        return True
    except requests.RequestException:
        return False
```
**NEW:**
```python
def check_service(port: str) -> bool:
    """Return True if a local service answers without a server error.

    BUG-50 defect 4: the previous version caught only RequestException, so a
    service returning HTTP 500 was reported as up.

    A 2xx-only rule is WRONG here and was corrected during S117 validation:
    ai-bridge on :3002 returns 404 on "/" while answering 200 on /anchor/state,
    so 2xx-only reported a healthy service as down. 4xx means the server is
    there and answered; only 5xx means it is broken.
    """
    try:
        r = requests.get(f'http://localhost:{port}', timeout=2)
        return r.status_code < 500
    except requests.RequestException:
        return False


def _sk_age_seconds(timestamp: str):
    """Age in seconds of a Signal K ISO-8601 timestamp, or None if unparseable."""
    if not timestamp:
        return None
    try:
        ts = datetime.fromisoformat(str(timestamp).replace('Z', '+00:00'))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - ts).total_seconds()
    except (ValueError, TypeError):
        return None


def check_gps(max_age_s: int = 10) -> bool:
    """True only if Signal K holds a position that is BOTH present and fresh.

    Checking that Signal K is running tells you nothing about whether a GPS
    exists — that was BUG-50 defect 1.
    """
    try:
        r = requests.get(
            f'http://localhost:{SIGNALK_PORT}/signalk/v1/api/vessels/self/navigation/position',
            timeout=2,
        )
        if not (200 <= r.status_code < 300):
            return False
        pos = r.json()
    except (requests.RequestException, ValueError):
        return False

    value = pos.get('value') if isinstance(pos, dict) else None
    if not isinstance(value, dict):
        return False
    if value.get('latitude') is None or value.get('longitude') is None:
        return False

    age = _sk_age_seconds(pos.get('timestamp'))
    return age is not None and age <= max_age_s


def check_ais(max_age_s: int = 300) -> str:
    """Three-state AIS health: 'receiving' | 'no_targets' | 'no_data'.

    'no_targets' is deliberately NOT a healthy state and NOT a fault. Signal K
    alone cannot tell "nothing in range" from "receiver is dead", so the honest
    answer is a third state — never a green light.
    """
    try:
        self_r = requests.get(f'http://localhost:{SIGNALK_PORT}/signalk/v1/api/self', timeout=2)
        vessels_r = requests.get(f'http://localhost:{SIGNALK_PORT}/signalk/v1/api/vessels/', timeout=3)
        if not (200 <= vessels_r.status_code < 300):
            return 'no_data'
        vessels = vessels_r.json()
        self_id = self_r.text.strip().strip('"') if 200 <= self_r.status_code < 300 else ''
    except (requests.RequestException, ValueError):
        return 'no_data'

    if not isinstance(vessels, dict):
        return 'no_data'

    for key, vessel in vessels.items():
        if self_id and (key in self_id or self_id.endswith(key)):
            continue
        if not isinstance(vessel, dict):
            continue
        ts = (vessel.get('navigation', {}) or {}).get('position', {}) or {}
        age = _sk_age_seconds(ts.get('timestamp'))
        if age is not None and age <= max_age_s:
            return 'receiving'

    return 'no_targets'


def check_avnav():
    """(healthy, chart_count) from AvNav's OWN status API.

    A bare port probe passes with an expired chart licence and zero charts —
    the exact OB-O05 state, and BUG-50 defect 3.
    """
    try:
        r = requests.get(
            f'http://localhost:{AVNAV_PORT}/viewer/avnav_navi.php?request=status',
            timeout=3,
        )
        if not (200 <= r.status_code < 300):
            return False, None
        data = r.json()
    except (requests.RequestException, ValueError):
        return False, None

    handlers = data.get('handler')
    if not isinstance(handlers, list):
        return False, None

    charts = None
    for h in handlers:
        if h.get('name') != 'ChartHandler':
            continue
        for item in (h.get('info', {}) or {}).get('items', []):
            text = str(item.get('info', ''))
            for token in text.replace(',', ' ').split():
                if token.isdigit():
                    charts = int(token)
                    break
    return True, charts
```

#### R2 — `/status` must report GPS, AIS and chart count

**OLD** (exact, one occurrence):
```python
    return jsonify({
        'internet':  check_internet(),
        'avnav':     check_service(AVNAV_PORT),    # localhost:8080
        'gemini':    check_service(GEMINI_PORT),   # localhost:3001
        'ai_bridge': check_service('3002'),        # localhost:3002 (Phase 5)
        'signalk':   check_service(SIGNALK_PORT),  # localhost:8099
        'ollama':    check_ollama(),               # 192.168.1.36:11434
    })
```
**NEW:**
```python
    avnav_ok, avnav_charts = check_avnav()
    return jsonify({
        'internet':     check_internet(),
        'avnav':        avnav_ok,                     # AvNav's own status API, not a bare port
        'avnav_charts': avnav_charts,                 # surfaces blank charts (OB-O05)
        'gemini':       check_service(GEMINI_PORT),   # localhost:3001
        'ai_bridge':    check_service('3002'),        # localhost:3002 (Phase 5)
        'signalk':      check_service(SIGNALK_PORT),  # localhost:8099
        'ollama':       check_ollama(),               # 192.168.1.36:11434
        'gps':          check_gps(),                  # real position + 10s freshness
        'ais':          check_ais(),                  # 'receiving' | 'no_targets' | 'no_data'
    })
```

---

### FILE B — `opt/d3kos/services/dashboard/templates/settings.html`

#### R3 — delete the always-green OpenPlotter row (operator decision S117)

**OLD** (exact, one occurrence — the whole line including its leading whitespace):
```html
          <div class="si"><div class="si-name">OpenPlotter</div><div class="si-val" id="si-openplotter">&#8212;</div><div class="si-sub">localhost:8081 &middot; infra</div></div>
```
**NEW:** *(empty — delete the line entirely)*

#### R4 — rewire GPS and AIS to their own fields; drop the OpenPlotter call

**OLD** (exact, one occurrence — three consecutive lines):
```javascript
          setSI('si-openplotter', true, '● RUNNING');     /* infra — always up */
          setSI('si-gps',  d.signalk, d.signalk ? '● VIA SK'  : '○ NO SK');
          setSI('si-ais',  d.signalk, d.signalk ? '● VIA SK'  : '○ NO SK');
```
**NEW:**
```javascript
          setSI('si-gps', d.gps, d.gps ? '● LIVE FIX' : '○ NO FIX');
          setAIS('si-ais', d.ais);
```

#### R5 — AvNav label must show the chart count

**OLD** (exact, one occurrence):
```javascript
          setSI('si-avnav',     d.avnav,    d.avnav    ? '● LIVE'      : '○ DOWN');
```
**NEW:**
```javascript
          setSI('si-avnav', d.avnav,
                d.avnav ? (d.avnav_charts === 0 ? '● UP — NO CHARTS' : '● LIVE') : '○ DOWN');
```

#### R6 — add the three-state AIS renderer

**OLD** (exact, one occurrence):
```javascript
    function setSI(id, ok, label) {
      const el = document.getElementById(id);
      if (!el) return;
      el.textContent = label;
      el.className = 'si-val ' + (ok ? 'ok' : 'off');
    }
```
**NEW:**
```javascript
    function setSI(id, ok, label) {
      const el = document.getElementById(id);
      if (!el) return;
      el.textContent = label;
      el.className = 'si-val ' + (ok ? 'ok' : 'off');
    }

    /* AIS is three-state on purpose. "No targets" is normal at sea and must not
       read as a fault, but it also cannot claim the receiver is healthy —
       Signal K cannot tell "nothing in range" from "receiver dead". */
    function setAIS(id, state) {
      const el = document.getElementById(id);
      if (!el) return;
      if (state === 'receiving') {
        el.textContent = '● RECEIVING';
        el.className = 'si-val ok';
        el.style.color = '';
      } else if (state === 'no_targets') {
        el.textContent = '◐ NO TARGETS';
        el.className = 'si-val';
        el.style.color = 'var(--warn,#FFA500)';
      } else {
        el.textContent = '○ NO DATA';
        el.className = 'si-val off';
        el.style.color = '';
      }
    }
```

---

## 5. Acceptance — Tier 1 §25.8 verification

| # | Check | Expected |
|---|---|---|
| 1 | `tests/bug50-status-truthfulness.spec.ts` | **10/10 pass** (was 7 failing) |
| 2 | `curl /status \| jq .gps` on the lab Pi (no GPS present) | `false` |
| 3 | `curl /status \| jq .ais` on the lab Pi (no AIS present) | `"no_targets"` or `"no_data"` — **never** `"receiving"` |
| 4 | `curl /status \| jq .avnav_charts` | an integer, not missing |
| 5 | `grep -c si-openplotter templates/settings.html` | `0` |
| 6 | LAB-SIM `run.sh cruise` running → `curl /status \| jq .gps` | `true` |
| 7 | LAB-SIM stopped, wait > 10 s → `curl /status \| jq .gps` | back to `false` — **this proves freshness, not mere presence** |
| 8 | Inject an AIS vessel (S115 method) → `.ais` | `"receiving"` |
| 9 | Full regression suite | no test that passed before now fails |
| 10 | `/settings` and `/` | HTTP 200 on both `:3000` and nginx `:80` |

**Check 7 is the one that matters most.** A fix that only tests "does the path exist" would pass
1–6 and 8 while still being wrong.

---

## 6. Out of scope — do not touch

- Microphone and speaker indicators → **D15** (ex BUG-11), v0.9.9.5.
- The generic brand-agnostic device framework → **D15**.
- The four other pages that load `keyboard-fix.js` → no bug logged.
- `keyboard-api.py`, squeekboard, Chromium flags, nginx.
- The boat Pi. Lab Pi only.


---

## 7. Tier 3 outcome and Tier 1 §25.8 verdict — S117 2026-08-02

**Model:** `gemini-2.5-flash-lite`, dispatched FROM the Pi so the key never left the device.
**Three rounds, ~11,800 tokens total, well under one cent.**

| Round | Result | Detail |
|---|---|---|
| 1 | **REJECT** | 7 defects, 4 fatal. Two were caused by the *prompt*: source was shown inside markdown fences and Tier 3 copied a fence into an anchor string (` ``` ` appeared in an `old` value, so it could never match). Also used `re.search` with `re` unimported; emitted a second `@app.route('/status')` while replacing the first (duplicate route, Flask would refuse to start); routed GPS through the three-state AIS renderer so it would read "NO DATA" permanently; parsed `handler['info']` as a list when it is a dict; put the "no charts" label in the FALSE branch so it showed when AvNav was DOWN. |
| 2 | **ACCEPT with 3 Tier 1 corrections** | Substantially correct. Corrections: (a) `setSI` takes **three** args, not four — Tier 3 confused it with `setPT`, so the label was wrong whenever the value was false; (b) **self-vessel exclusion never fired** — `/api/self` returns `"vessels.urn:mrn:..."` while vessel keys omit the `vessels.` prefix, so own ship would be counted as an AIS target and a boat with a GPS fix would report `"receiving"` with zero real targets; (c) exception breadth — only `RequestException` was caught, so a 200 with a non-JSON body would 500 the whole endpoint. |
| 3 | **DISCARD — severe regression** | A correction-only prompt caused context loss. It invented endpoints that do not exist (`/signalk/v1/api/gps`, `/signalk/v1/api/avnav`), dropped host and port entirely, hardcoded placeholder values into `/status` (`gemini = False`, `signalk = True`, `'gps': internet`), mangled `●` via `String.fromCharCode(0xE2,0x96,0x89)` (UTF-8 bytes as UTF-16 units), and lost the three-state AIS renderer. Round 2 + Tier 1 corrections was taken instead. |

**Lesson for future Tier 3 dispatches:** never show source inside markdown code fences — Tier 3
copies the fence into anchors. Round 2 removed anchoring from Tier 3's job entirely (it returned
named code bodies; Tier 1 placed them) and that eliminated the whole failure class. And a
correction-only prompt that restates requirements without full original context can regress badly —
prefer one well-formed round plus Tier 1 finishing over iterative correction rounds.

**One Tier 1 spec defect** (the 2xx rule) was found by validation, not by review. See the R1 note.

### Acceptance results — all 10 checks

| # | Check | Result |
|---|---|---|
| 1 | `tests/bug50-status-truthfulness.spec.ts` | **10/10 pass** (7 failing pre-fix) |
| 2 | `.gps` with no GPS | `false` ✅ |
| 3 | `.ais` with no targets | `"no_targets"` — never `receiving` ✅ |
| 4 | `.avnav_charts` | `1` (integer) ✅ |
| 5 | `grep -c si-openplotter` | `0` ✅ |
| 6 | LAB-SIM `cruise` running → `.gps` | `true` ✅ |
| 7 | **Feed stopped, >10 s → `.gps`** | **back to `false`** ✅ — and Signal K *still held the position*, so a presence-only check would have stayed green forever. This is the decisive one. |
| 8 | AIS target injected → `.ais` | `"receiving"` ✅ |
| 9 | **Own ship fresh, zero other vessels → `.ais`** | **`"no_targets"`** ✅ — proves the self-exclusion fix; without it the boat would report a false `receiving` |
| 10 | Both origins, `/` and `/settings` | 200 on `:3000` and nginx `:80` ✅ |

**Regression:** full Playwright suite **52 passed / 6 failed**. The 6 are `page.goto: net::ERR_ABORTED`
in `bug15`, `bug26`, `bug27` — **proven pre-existing** by reverting the Pi to pre-BUG-50 code and
re-running those exact six, which failed identically. Restored immediately after.

**Test-environment defects found and fixed/recorded along the way:**
- The Playwright browser could not launch at all (`libnspr4.so` missing). The correct library path
  is `~/.local/pw-libs/root/usr/lib/x86_64-linux-gnu` — MEMORY.md omitted the `root/` level.
  With it corrected, 28 browser tests that were silently failing now run.
- `tests/bug29-engine-path-aliases.test.js` and `tests/bug38-diag-panel-ids.test.js` use
  `require()` under `"type": "module"` and **cannot run**. Any prior "all green" count that
  included them was overstated. Not fixed — out of BUG-50 scope.
- The BUG-50 suite's own skip conditions initially keyed on *presence* of a position. Signal K
  never expires stale data, so after any GPS run those negative tests would have skipped forever
  while appearing green. Hardened to key on *freshness*; 0 skipped now.

### Known characteristic, not a defect
`/status` now takes **~5.3 s** (was ~3.5 s). The dominant cost is `check_ollama()` — Ollama is
unreachable and burns its full 3 s timeout every poll. Each new check is ≤3 s individually per
spec, and the endpoint is polled every 30 s, so this does not stall the page. Worth revisiting if
Ollama stays down: the checks could run concurrently.
