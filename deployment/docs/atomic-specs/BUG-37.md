# Atomic Spec — BUG-37 (dashboard `app.py` is missing all seven v0.9.9.2 routes)

**Format:** AAO §23.5 Atomic Spec · §25 escalation-enabled · §24 Question Queue
**Created:** 2026-07-27 (S108) by Tier 1 (Opus 5)
**Tracker:** `deployment/docs/V09994_BUG_FIXES.md` BUG-37 · `PROJECT_CHECKLIST.md` PART 17
**Questions:** `wiki/questions/2026-07-27-v0994-tier3-spec-questions.md` — **read Q0.1–Q0.5 and Q37.1–Q37.5 first**
**Depends on:** nothing. **Blocks:** BUG-26 proper fix, M14 tier gate.

---

## Tier-1 finding

The deployed `app.py` (md5 `34211e37…`) is the `deployment/d3kOS/dashboard/` copy. The v0.9.9.2
release copy (`deployment/v0.9.4/pi_source/app.py`, md5 `d06b15da…`) defines seven routes the
deployed file has never had:

```
/config/tier   /anchor/set   /anchor/state   /anchor/clear
/anchor/dismiss   /anchor/advice   /helm/mute
```

Consequences: `openDiag()` calls `fetch('/config/tier')`, gets a 404, falls into its `catch`, and
`tier` stays `0` — so **every user is treated as T0 and shown the upgrade screen**, regardless of the
real T3 licence. `anchor-watch.html` got the S105 `AI_BRIDGE` workaround precisely because these
proxies were missing — **BUG-37 is the true root cause of BUG-26.** And S44's `/helm/mute` CORS fix
has no server side.

This is a **verbatim port**, not a redesign. All required imports are already present (Q37.1).

---

## SPEC (paste this block to the Tier 3 model)

```
🔧 ATOMIC SPEC — BUG-37   (AAO §23.5 · §25 escalation-enabled)
═══════════════════════════════════════════════════════════════════════
TASK TYPE : [IMPLEMENT] — Tier 3
BUG       : BUG-37 — port the seven missing v0.9.9.2 Flask routes

FILE TO EDIT (exactly one)
  deployment/v0.9.9.4/opt/d3kos/services/dashboard/app.py

READ-ONLY REFERENCE (copy FROM this, never write to it)
  deployment/v0.9.4/pi_source/app.py       lines 407-417 and 732-795

CHANGE
  Append the seven route handlers below, VERBATIM, after the last existing route
  (@app.route('/docs/<name>'), ~line 599) and before any
  `if __name__ == '__main__':` block. Add NO imports — all are already present
  (jsonify, request line 16; requests line 18; json line 17; Path line 24).

  Copy these exactly as written:

    @app.route('/config/tier')
    def config_tier():
        """Tier for M14 engine diagnostic gate. T0/T1 blocked, T2/T3 allowed."""
        try:
            import json
            lic = json.loads(Path('/opt/d3kos/config/license.json').read_text())
            t = lic.get('tier', 'T0')
            n = int(str(t).replace('T', '')) if t else 0
            return jsonify({'tier': n, 'tier_str': 'T' + str(n)})
        except Exception:
            return jsonify({'tier': 0, 'tier_str': 'T0'})

    @app.route('/anchor/set', methods=['POST'])
    def anchor_set():
        """Get current vessel position from SK, tell ai_bridge to set anchor."""
        try:
            data = request.get_json(silent=True) or {}
            radius_m = float(data.get('radius_m', 25.0))
            r = requests.get('http://localhost:8099/signalk/v1/api/vessels/self/navigation/position', timeout=3)
            pos = r.json().get('value', {})
            lat = float(pos['latitude'])
            lon = float(pos['longitude'])
            result = requests.post('http://localhost:3002/anchor/set',
                                   json={'lat': lat, 'lon': lon, 'radius_m': radius_m},
                                   timeout=5)
            return jsonify(result.json())
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500

    @app.route('/anchor/state')
    def anchor_state():
        try:
            r = requests.get('http://localhost:3002/anchor/state', timeout=3)
            return jsonify(r.json())
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500

    @app.route('/anchor/dismiss', methods=['POST'])
    def anchor_dismiss_proxy():
        try:
            r = requests.post('http://localhost:3002/anchor/dismiss', timeout=3)
            return jsonify(r.json())
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500

    @app.route('/anchor/clear', methods=['POST'])
    def anchor_clear_proxy():
        try:
            r = requests.post('http://localhost:3002/anchor/clear', timeout=3)
            return jsonify(r.json())
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500

    @app.route('/anchor/advice')
    def anchor_advice_proxy():
        try:
            r = requests.get('http://localhost:3002/anchor/advice', timeout=60)
            return jsonify(r.json())
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500

    @app.route('/helm/mute', methods=['POST'])
    def helm_mute_proxy():
        """Proxy HELM mute toggle to ai_bridge (same origin via Flask:3000 avoids CORS)."""
        try:
            r = requests.post('http://localhost:3002/helm/mute',
                              json=request.get_json(), timeout=3)
            return jsonify(r.json())
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500

CONSTRAINT BOUNDARIES (do NOT)
  • Do NOT add, remove or reorder imports. They are already there (Q37.1).
  • Do NOT "improve" the ported code: keep the hardcoded localhost:3002 and
    localhost:8099 URLs, the 60s advice timeout, and the redundant inner
    `import json`. This is a port, not a refactor (Q37.4).
  • Do NOT modify or delete any existing route.
  • Do NOT touch templates/anchor-watch.html. The S105 AI_BRIDGE workaround stays
    for now — reverting it is an operator decision (Q37.3).
  • Do NOT edit any other file. Do NOT regenerate MANIFEST.md5 (Q0.4).
  • Do NOT deploy to the Pi (Q0.2).

INTERFACE CONTRACT
  After the change, Flask's url_map contains all seven rules with these methods:

    /config/tier      GET
    /anchor/set       POST
    /anchor/state     GET
    /anchor/clear     POST
    /anchor/dismiss   POST
    /anchor/advice    GET
    /helm/mute        POST

  Every previously existing rule is still present. No rule is duplicated.

FAILING TEST FIRST (TDD — write it, RUN IT, watch it fail, then fix)
  File: tests/test_bug37_routes.py        (pytest — no server, no Pi needed)
  Run : python3 -m pytest tests/test_bug37_routes.py -v

  The module cannot simply be imported (it reads /opt/d3kos/... at import time and
  binds a port). So parse it statically with `ast` — this asserts the exact
  interface contract without executing anything:

    import ast, pathlib, pytest

    APP = pathlib.Path('deployment/v0.9.9.4/opt/d3kos/services/dashboard/app.py')

    EXPECTED = {
        '/config/tier':    {'GET'},
        '/anchor/set':     {'POST'},
        '/anchor/state':   {'GET'},
        '/anchor/clear':   {'POST'},
        '/anchor/dismiss': {'POST'},
        '/anchor/advice':  {'GET'},
        '/helm/mute':      {'POST'},
    }

    def _routes():
        """Return {rule: {methods}} for every @app.route in app.py."""
        tree = ast.parse(APP.read_text())
        found = {}
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            for dec in node.decorator_list:
                if not (isinstance(dec, ast.Call) and getattr(dec.func, 'attr', '') == 'route'):
                    continue
                rule = dec.args[0].value
                methods = {'GET'}
                for kw in dec.keywords:
                    if kw.arg == 'methods':
                        methods = {e.value for e in kw.value.elts}
                found.setdefault(rule, set()).update(methods)
        return found

    @pytest.mark.parametrize('rule,methods', EXPECTED.items())
    def test_route_registered(rule, methods):
        found = _routes()
        assert rule in found, f'{rule} is not registered in app.py'
        assert methods <= found[rule], f'{rule} missing methods {methods - found[rule]}'

    def test_existing_routes_survive():
        found = _routes()
        for rule in ('/', '/settings', '/anchor-watch', '/engine-monitor', '/manual'):
            assert rule in found, f'pre-existing route {rule} was removed'

    def test_source_is_syntactically_valid():
        ast.parse(APP.read_text())      # raises SyntaxError if the port broke the file

  EXPECTED BEFORE THE FIX: all seven test_route_registered cases FAIL
  ("/config/tier is not registered in app.py" etc). test_existing_routes_survive
  and test_source_is_syntactically_valid PASS before and after.
  If the seven do not fail first, STOP and escalate.

DONE WHEN
  • The seven route tests FAILED before your edit and PASS after.
  • The two guard tests pass before AND after.
  • git diff shows only additions to app.py — zero deletions, zero modified lines.

ESCALATE-IF  (emit the 🔺 block — do not guess)
  • Any of the seven routes already exists in the canonical app.py
                                        → CLARIFICATION (partial port / wrong file)
  • pi_source/app.py does not contain the code shown above
                                        → CLARIFICATION (reference drifted)
  • test_source_is_syntactically_valid fails after your edit
                                        → SOLUTION-REQUEST (indentation/paste damage)
  • A route needs an import that is missing
                                        → ADVICE (contradicts Q37.1 — flag it)

PRE-FLIGHT SELF-CHECK
  1. How many routes am I adding?  → exactly 7
  2. How many imports?             → zero
  3. May I clean up the code?      → no, verbatim port
  4. Do I touch anchor-watch.html? → no
  5. What proves done?             → 7 ast tests flip fail→pass, 2 guard tests stay green

RETURN TO TIER 1
  • The diff (additions only)
  • pytest output showing fail-before / pass-after
  • Decision Log: any deviation, or "none"
═══════════════════════════════════════════════════════════════════════
```

---

## Tier-1 verification pass (§25.8)

1. `git diff` = additions only. Any deletion or modified existing line is a fail.
2. All seven rules present with correct methods; no duplicate rule names; no duplicate function names
   (a name collision silently overrides an earlier route in Flask — grep the function names).
3. `python3 -m py_compile` on the file passes.
4. Confirm `anchor-watch.html` is untouched.
5. **Cannot verify remotely:** that the routes actually proxy correctly to ai-bridge :3002 and Signal K
   :8099. That requires a deploy and a live Pi. Do not claim BUG-26 fixed.

## Out of scope
Pi deployment · reverting the S105 `AI_BRIDGE` workaround · making service URLs configurable ·
any behaviour change to the ported code.
