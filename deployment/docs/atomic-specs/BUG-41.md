# Atomic Spec — BUG-41 (`/settings` returns HTTP 500 — `tier_num` and `device_token` never passed)

**Format:** AAO §23.5 Atomic Spec · §25 escalation-enabled · §24 Question Queue
**Created:** 2026-07-29 (S110) by Tier 1 (Opus 5)
**Tracker:** `deployment/docs/V09994_BUG_FIXES.md` BUG-41 · `PROJECT_CHECKLIST.md` PART 17
**Questions:** none open — all information derived directly from the target file.
**Depends on:** nothing. Reproducible on the lab Pi now; no on-boat access required.

---

## Tier-1 finding

`settings()` in `app.py` (line 344) calls `render_template('settings.html', …)` but omits
two variables the template requires:

| Variable | Used at | Effect of omission |
|----------|---------|-------------------|
| `tier_num` | line 509 — `{% if tier_num >= 1 and device_token %}` | Jinja2 raises `UndefinedError: 'tier_num' is undefined` immediately |
| `device_token` | line 521 — `{{ device_token }}` | Only rendered if the `if` above is entered — but `tier_num` fails first |

**Root cause:** The deployed `app.py` is from the `d3kOS/dashboard` lineage; the deployed
`settings.html` is from the `pi_source` lineage. `pi_source/app.py` passes both variables;
`d3kOS/dashboard/app.py` does not. The S105 deploy brought in the wrong half of the pair
(see BUG-36/37 for the same lineage split).

**Complete Jinja2 variable audit of `settings.html`** — variables currently passed vs. required:

| Variable | Passed today | After fix |
|----------|-------------|-----------|
| `vessel_name` | ✓ | ✓ |
| `home_port` | ✓ | ✓ |
| `avnav_port` | ✓ | ✓ |
| `gemini_port` | ✓ | ✓ |
| `signalk_port` | ✓ | ✓ |
| `tier_num` | ✗ — **500** | ✓ |
| `device_token` | ✗ | ✓ |

Both patterns already exist in `app.py`:
- `tier_num` — identical logic to `config_tier()` (line 613)
- `device_token` — identical logic to `api_recovery_key()` (line 364)

---

## SPEC (paste this block to the Tier 3 model)

```
🔧 ATOMIC SPEC — BUG-41   (AAO §23.5 · §25 escalation-enabled)
═══════════════════════════════════════════════════════════════════════
TASK TYPE : [IMPLEMENT] — Tier 3
BUG       : BUG-41 — /settings returns HTTP 500: tier_num and device_token
            never passed to settings.html

FILE TO EDIT (exactly one)
  deployment/v0.9.9.4/opt/d3kos/services/dashboard/app.py

CURRENT STATE — the settings() function (lines 344–354):

    @app.route('/settings')
    def settings():
        """Settings & Help page — placeholder. Full build in Phase 4."""
        return render_template(
            'settings.html',
            avnav_port=AVNAV_PORT,
            gemini_port=GEMINI_PORT,
            signalk_port=SIGNALK_PORT,
            vessel_name=VESSEL_NAME,
            home_port=HOME_PORT_VAL,
        )

CHANGE — add two reads before the render_template call, then pass both
variables. The exact replacement for the entire settings() function body:

    @app.route('/settings')
    def settings():
        """Settings & Help page — placeholder. Full build in Phase 4."""
        try:
            lic = json.loads(Path('/opt/d3kos/config/license.json').read_text())
            t = lic.get('tier', 'T0')
            tier_num = int(str(t).replace('T', '')) if t else 0
        except Exception:
            tier_num = 0
        try:
            device_token = json.loads(
                Path('/opt/d3kos/config/device-token.json').read_text()
            ).get('device_token', '')
        except Exception:
            device_token = ''
        return render_template(
            'settings.html',
            avnav_port=AVNAV_PORT,
            gemini_port=GEMINI_PORT,
            signalk_port=SIGNALK_PORT,
            vessel_name=VESSEL_NAME,
            home_port=HOME_PORT_VAL,
            tier_num=tier_num,
            device_token=device_token,
        )

PATTERNS — do NOT invent these. They are copied verbatim from two existing
functions in the same file:
  • tier_num  logic  → config_tier()       at line 613
  • device_token logic → api_recovery_key() at line 364
Both already import json and Path at the top of app.py. No new imports needed.

CONSTRAINT BOUNDARIES (do NOT)
  • Do NOT edit settings.html — the template is correct.
  • Do NOT edit any other file.
  • Do NOT remove any of the five variables already passed to render_template.
  • Do NOT raise inside the two new try/except blocks — the defaults (0 and '')
    are the correct fallbacks when the Pi config files are absent.
  • Do NOT add imports — json and Path are already imported at the top.
  • Do NOT deploy to the Pi.

INTERFACE CONTRACT
  GET /settings with license.json absent  → 200, tier_num=0, device_token=''
                                            (Recovery Key section hidden by the
                                             {% if tier_num >= 1 %} guard)
  GET /settings with license.json T3 present → 200, tier_num=3
  GET /settings — current (broken) state → 500 UndefinedError

FAILING TEST FIRST (TDD — write it, RUN IT, watch it fail, THEN fix)
  File: tests/test_bug41_settings_route.py     (pytest, Flask test client — no Pi needed)
  Run : python3 -m pytest tests/test_bug41_settings_route.py -v

    import sys, os, importlib.util, pytest

    APP_PATH = 'deployment/v0.9.9.4/opt/d3kos/services/dashboard/app.py'

    def load_app():
        spec = importlib.util.spec_from_file_location('dashboard_app', APP_PATH)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.app

    @pytest.fixture(scope='module')
    def client():
        flask_app = load_app()
        flask_app.config['TESTING'] = False   # exceptions become 500, not raised
        with flask_app.test_client() as c:
            yield c

    def test_settings_returns_200_not_500(client):
        """Before fix: Jinja UndefinedError -> 500. After fix: 200."""
        response = client.get('/settings')
        assert response.status_code == 200, (
            f'Expected 200 but got {response.status_code}. '
            'tier_num or device_token is still not passed to render_template.'
        )

    def test_settings_response_contains_html(client):
        """Confirms the template rendered, not a Flask error page."""
        response = client.get('/settings')
        body = response.data.decode('utf-8', errors='replace')
        assert '<html' in body.lower(), 'Response should be an HTML page'
        assert 'UndefinedError' not in body, 'Jinja error must not appear in output'
        assert 'tier_num' not in body, (
            'tier_num must be resolved; it must not appear as literal text'
        )

    def test_app_py_passes_tier_num_and_device_token():
        """Static check: render_template call in settings() must include both vars."""
        import pathlib
        src = pathlib.Path(APP_PATH).read_text()
        settings_block = src.split('@app.route(\'/settings\')')[1].split('@app.route')[0]
        assert 'tier_num' in settings_block, \
            'tier_num must be in the settings() render_template call'
        assert 'device_token' in settings_block, \
            'device_token must be in the settings() render_template call'

  EXPECTED BEFORE THE FIX:
    test_settings_returns_200_not_500   FAILED  (AssertionError: got 500)
    test_settings_response_contains_html FAILED or SKIPPED (depends on 500 body)
    test_app_py_passes_tier_num_and_device_token FAILED (strings absent)

  If the tests do NOT fail before your edit, STOP and escalate —
  the file may already be patched or your import is hitting the wrong file.

DONE WHEN
  • All 3 tests FAILED before your edit and PASS after.
  • git diff touches only app.py and the new test file.
  • No other variables were added or removed from the render_template call.

ESCALATE-IF  (emit the 🔺 block — do not guess)
  • Importing app.py raises at module level (load_dotenv exceptions are normal
    and silent — only non-load_dotenv raises count)
                                   → SOLUTION-REQUEST (describe the error exactly)
  • The settings() function body looks materially different from the spec above
    (extra logic, different route decorator, split across helpers)
                                   → ADVICE (paste what you see; do not force the patch)
  • A third variable in settings.html is undefined beyond tier_num and device_token
                                   → ADVICE (list it; do not fix it silently)

PRE-FLIGHT SELF-CHECK
  1. How many files do I edit?        → exactly 1 (app.py)
  2. Do I edit settings.html?         → NO
  3. May the try/except blocks raise? → NO — defaults are 0 and ''
  4. What proves done?                → 3 tests flip fail → pass

RETURN TO TIER 1
  • The diff for app.py
  • pytest output showing fail-before / pass-after (3 tests)
  • Decision Log: any deviation, or "none"
═══════════════════════════════════════════════════════════════════════
```

---

## Tier-1 verification pass (§25.8)

1. `tier_num` added to `render_template` in `settings()` with safe default 0.
2. `device_token` added to `render_template` in `settings()` with safe default ''.
3. Both reads use identical patterns to existing functions in the same file — no novel logic.
4. No other file touched — `settings.html` untouched, template audit shows no third undefined variable.
5. `test_settings_returns_200_not_500` proves the route no longer 500s.
6. `test_app_py_passes_tier_num_and_device_token` provides a static anchor: if Haiku
   accidentally puts the variables in the wrong function, this test catches it.
7. Tests genuinely fail first — require the pre-fix output.

## Out of scope
Deploying to Pi · fixing the hardcoded "Tier 2 / d3k-2024-boatiq-001" static text
in the License & Tier card (that text is HTML literals, not template variables) ·
any change to `settings.html` · reconciling the lineage split (BUG-36/37 scope).
