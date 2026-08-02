#!/usr/bin/env python3
"""
Tier 3 dispatch — BUG-50 implementation.

Runs ON the Pi (streamed over SSH stdin, never written to the Pi's disk) so the
Gemini key in /opt/d3kos/config/api-keys.json never leaves the device.

Tier 1 authored the atomic spec (deployment/docs/atomic-specs/BUG-50.md) and this
prompt. Tier 3 (gemini-2.5-flash-lite) writes the implementation. Tier 1 then
verifies every returned edit under AAO §25.8 before anything is applied.

Output: JSON on stdout. Nothing is modified by this script — it only proposes.
"""
import json
import sys
import urllib.request

CFG = "/opt/d3kos/config/api-keys.json"
APP = "/opt/d3kos/services/dashboard/app.py"
TPL = "/opt/d3kos/services/dashboard/templates/settings.html"


def load_cfg():
    with open(CFG) as f:
        d = json.load(f)
    return d["gemini_api_key"], d.get("gemini_model", "gemini-2.5-flash-lite")


def region(path, needle, before=2, after=25):
    """Return the exact current text around an anchor, so Tier 3 edits reality."""
    lines = open(path).read().split("\n")
    for i, ln in enumerate(lines):
        if needle in ln:
            return "\n".join(lines[max(0, i - before):i + after])
    return f"<<ANCHOR NOT FOUND: {needle}>>"


PROMPT = """You are a Tier 3 implementer working to a fixed specification. Return ONLY JSON.

# Task
Fix BUG-50 in a Raspberry Pi marine navigation dashboard (Flask + Jinja2).

The Settings "System Status" panel reports capabilities as healthy when they are not.
Proven on the live device: the GPS indicator shows green while Signal K has no position at
all, and the AIS indicator shows green while Signal K holds zero targets. Both indicators
are wired to `d.signalk` — whether the Signal K SERVER is running — instead of to any
actual data. A green light at a boat's helm that says "your AIS works" when it does not is
a safety defect.

# Hard constraints — violating any of these fails review
1. Produce EXACT string replacements only. Never regenerate a whole file.
   Each "old" MUST appear VERBATIM and EXACTLY ONCE in the file shown below,
   including leading whitespace. Copy it character-for-character from the source given.
2. Do not add any dependency. Already imported in app.py: requests, json, os, socket,
   subprocess, hashlib, shutil, pathlib.Path. `datetime` is NOT imported — add it.
3. No network timeout above 3 seconds. /status is polled every 30 s and must not stall.
4. Server-side Python correctly uses `localhost` (it runs ON the Pi). Do NOT change that.
5. Existing JSON keys keep their names and boolean types:
   internet, avnav, gemini, ai_bridge, signalk, ollama.
6. AIS MUST be a three-state string, never a boolean.
7. Every network call must be individually wrapped so one dead service cannot 500 the
   whole /status endpoint.

# Required behaviour

## check_service(port) — currently broken
It catches only requests.RequestException, so a service returning HTTP 500 is reported as
UP. Fix it to return True only for a 2xx status.

## New: check_gps() -> bool
True ONLY IF Signal K has navigation.position with both latitude and longitude present,
AND its ISO-8601 `timestamp` is within 10 SECONDS of now. Otherwise False.
Endpoint: http://localhost:{SIGNALK_PORT}/signalk/v1/api/vessels/self/navigation/position
Signal K shape: {{"value": {{"latitude": 42.9, "longitude": -79.2}}, "timestamp": "2026-08-02T14:43:55.218Z"}}
Note the trailing "Z" — Python's fromisoformat needs it converted to +00:00.
Presence alone is NOT health. Stale data must read False.

## New: check_ais() -> str, one of "receiving" | "no_targets" | "no_data"
- "receiving"  : at least one vessel OTHER THAN self has navigation.position.timestamp
                 within 300 SECONDS.
- "no_targets" : Signal K reachable, but no fresh non-self vessel.
- "no_data"    : Signal K unreachable or the query failed.
Endpoints: /signalk/v1/api/vessels/ (dict keyed by vessel id) and /signalk/v1/api/self
(returns the self id as a bare quoted string — strip quotes; exclude that vessel).
"no_targets" is deliberately neither healthy nor a fault: nothing in range is normal at
sea, and Signal K cannot distinguish that from a dead receiver.

## New: check_avnav() -> (bool, int|None)
A bare port probe passes even when the chart licence has expired and zero charts load.
Query AvNav's OWN status API:
  http://localhost:{AVNAV_PORT}/viewer/avnav_navi.php?request=status
Healthy ONLY IF HTTP 2xx AND the body parses as JSON containing a list under key "handler".
Also return the chart count: find the handler whose "name" == "ChartHandler" and parse the
integer out of its info.items[].info text, which reads like:
  "handling directory /var/lib/avnav/charts, 1 charts"
Return (False, None) on any failure.

## /status route
Add "gps", "ais" and "avnav_charts". Use check_avnav() for "avnav" instead of
check_service(AVNAV_PORT). Keep all existing keys.

## Template settings.html
- DELETE the OpenPlotter status row entirely. It is hardcoded to always show green and can
  never report a fault, which is worse than having no row.
- DELETE the `setSI('si-openplotter', true, ...)` call.
- Rewire si-gps to read d.gps  -> label "● LIVE FIX" / "○ NO FIX".
- Rewire si-ais to a NEW function setAIS(id, state) rendering three states:
    receiving  -> "● RECEIVING",   className "si-val ok"
    no_targets -> "◐ NO TARGETS",  className "si-val", inline color var(--warn,#FFA500)
    no_data    -> "○ NO DATA",     className "si-val off"
- AvNav label must surface empty charts: when d.avnav is true and d.avnav_charts === 0,
  show "● UP — NO CHARTS" instead of "● LIVE".
- Add setAIS immediately after the existing setSI function, leaving setSI unchanged.

# Current source — copy your "old" strings verbatim from here

## app.py — imports
```python
{app_imports}
```

## app.py — check_service
```python
{app_check_service}
```

## app.py — /status route
```python
{app_status}
```

## settings.html — the OpenPlotter grid row
```html
{tpl_row}
```

## settings.html — loadStatus body
```javascript
{tpl_loadstatus}
```

## settings.html — setSI
```javascript
{tpl_setsi}
```

# Output format — JSON only, no prose, no markdown fence
{{"replacements":[{{"id":"R0","file":"app.py","reason":"...","old":"...","new":"..."}}]}}

Use file value exactly "app.py" or "settings.html". Order R0..R6.
"""


def main():
    key, model = load_cfg()

    prompt = PROMPT.format(
        SIGNALK_PORT="{SIGNALK_PORT}",
        AVNAV_PORT="{AVNAV_PORT}",
        app_imports=region(APP, "from pathlib import Path", before=4, after=3),
        app_check_service=region(APP, "def check_service(port: str)", before=0, after=8),
        app_status=region(APP, "@app.route('/status')", before=0, after=16),
        tpl_row=region(TPL, 'id="si-openplotter"', before=0, after=1),
        tpl_loadstatus=region(TPL, "function loadStatus()", before=0, after=22),
        tpl_setsi=region(TPL, "function setSI(id, ok, label)", before=0, after=7),
    )

    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 8192,
                             "responseMimeType": "application/json"},
    }).encode()

    url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
           f"{model}:generateContent?key={key}")
    req = urllib.request.Request(url, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        resp = json.load(r)

    try:
        text = resp["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        print(json.dumps({"error": "unexpected response", "raw": resp})[:4000])
        sys.exit(1)

    usage = resp.get("usageMetadata", {})
    print(json.dumps({
        "model": model,
        "usage": usage,
        "result": json.loads(text),
    }, indent=2))


if __name__ == "__main__":
    main()
