#!/usr/bin/env python3
"""
Tier 3 dispatch — BUG-50, ROUND 2 (correction round).

Round 1 was REJECTED by Tier 1 §25.8 verification with 7 defects, 4 fatal.
Two were caused by the prompt itself: source was shown inside markdown code
fences, and Tier 3 copied a fence into an anchor string.

Round 2 removes anchoring from Tier 3's job entirely. Tier 3 returns only NAMED
CODE BODIES; Tier 1 places them. That eliminates the whole anchor-matching
failure class while Tier 3 still writes the implementation.

Runs ON the Pi so the Gemini key never leaves the device. Modifies nothing.
"""
import json
import sys
import urllib.request

CFG = "/opt/d3kos/config/api-keys.json"

PROMPT = r"""You are a Tier 3 implementer. Return ONLY JSON. No markdown, no code fences.

# Context
Raspberry Pi marine navigation dashboard, Flask + Jinja2. Fixing BUG-50: the Settings
"System Status" panel reports GPS and AIS as healthy when they are not, because both are
wired to whether the Signal K SERVER is running rather than to any actual data. On the
live device the GPS light is green while Signal K has no position at all, and the AIS
light is green while Signal K holds zero targets. A green light at a boat's helm saying
"your AIS works" when it does not is a safety defect.

# YOUR PREVIOUS ATTEMPT WAS REJECTED. Do not repeat these 7 defects:
1. You put a markdown fence sequence inside an anchor string. This round you return no
   anchors at all - only the bodies named below.
2. You used re.search but the `re` module is NOT imported in this file. DO NOT USE `re`.
   Parse with plain string/split operations only.
3. You emitted a second @app.route('/status') definition while also replacing the existing
   one, which would register the route twice and crash Flask on startup. This round you
   must NOT write any @app.route decorator anywhere.
4. You called setAIS('si-gps', d.gps, ...). setAIS is the THREE-STATE renderer and takes
   (id, stateString). Passing a boolean makes GPS permanently display "NO DATA". GPS is
   TWO-STATE and must use the existing setSI(id, ok, label).
5. Your AvNav chart parsing iterated handler['info'] as if it were a list. It is a DICT.
   The real shape is: handler["info"]["items"] -> list of {"name":..,"status":..,"info":..}
6. You placed the "no charts" label in the FALSE branch, so it displayed when AvNav was
   DOWN. It must display when AvNav is UP and the chart count is 0.
7. You changed a timeout that was not in scope. Leave unrelated values alone.

# Environment facts - these are measured, not assumptions
- Already imported in app.py: requests, json, os, hashlib, shutil, socket, subprocess,
  pathlib.Path. `re` is NOT imported. `datetime` is NOT imported.
- Module constants already exist: SIGNALK_PORT, AVNAV_PORT, GEMINI_PORT, OLLAMA_HOST.
- Signal K position endpoint returns exactly this shape:
  {"value":{"latitude":42.89,"longitude":-79.2},"$source":"can0.0","timestamp":"2026-08-02T14:43:55.218Z"}
  Note trailing "Z" - Python fromisoformat needs it replaced with "+00:00".
- Signal K /signalk/v1/api/self returns the self id as a bare quoted string.
- Signal K /signalk/v1/api/vessels/ returns a dict keyed by vessel id.
- AvNav status endpoint http://localhost:{AVNAV_PORT}/viewer/avnav_navi.php?request=status
  returns {"handler":[ {"name":"ChartHandler","info":{"items":[
      {"name":"main","status":"NMEA","info":"handling directory /var/lib/avnav/charts, 1 charts"}]}} ]}

# Deliverables - return each as a JSON string value

"py_helpers": Python source for FOUR module-level functions, in this order, separated by
one blank line. No imports, no decorators, no route definitions. 4-space indent.
  _sk_age_seconds(timestamp) -> float or None
      Age in seconds of a Signal K ISO-8601 timestamp. Return None if unparseable.
      Use datetime.datetime and datetime.timezone (module-style, since we import the
      module not the names).
  check_gps() -> bool
      True ONLY IF the position endpoint returns 2xx AND value.latitude and
      value.longitude are both present AND _sk_age_seconds(timestamp) <= 10.
      Presence alone is NOT health - stale data must be False.
      Wrap all network access; never raise.
  check_ais() -> str  one of "receiving" | "no_targets" | "no_data"
      "receiving": at least one vessel other than self whose
                   navigation.position.timestamp age <= 300 seconds.
      "no_targets": reachable but no fresh non-self vessel.
      "no_data": unreachable or query failed.
      Exclude the self vessel. Never raise.
  check_avnav() -> tuple of (bool, int or None)
      Healthy ONLY IF 2xx AND body has a list under key "handler".
      Chart count: find handler with name == "ChartHandler", walk
      handler["info"]["items"], and from each item's "info" string extract the integer
      that immediately precedes the word "charts". Parse WITHOUT the re module.
      Return (False, None) on any failure.
  All timeouts must be 3 seconds or less.

"py_status_body": ONLY the body that goes inside the existing status() function, after its
docstring. Do NOT include the decorator or the def line. Must start with a call to
check_avnav() unpacking two values, then a single return jsonify({...}) containing exactly
these keys: internet, avnav, avnav_charts, gemini, ai_bridge, signalk, ollama, gps, ais.
Keep internet/gemini/ai_bridge/signalk/ollama exactly as they are today:
  check_internet(), check_service(GEMINI_PORT), check_service('3002'),
  check_service(SIGNALK_PORT), check_ollama()
Use 4-space base indent (it sits inside a function).

"js_loadstatus_lines": The replacement JavaScript for exactly these three existing lines:
      setSI('si-openplotter', true, '● RUNNING');
      setSI('si-gps',  d.signalk, ...);
      setSI('si-ais',  d.signalk, ...);
  Return TWO lines only: a setSI call for si-gps reading d.gps with labels
  "● LIVE FIX" / "○ NO FIX", and a setAIS call for si-ais passing d.ais.
  The OpenPlotter line is deleted entirely. Indent 10 spaces.

"js_avnav_line": The replacement for the single existing si-avnav line. When d.avnav is
  TRUE and d.avnav_charts === 0 the label is "● UP — NO CHARTS"; when d.avnav is
  TRUE otherwise it is "● LIVE"; when d.avnav is FALSE it is "○ DOWN".
  Indent 10 spaces.

"js_setais": The complete new setAIS(id, state) function. Renders three states:
    "receiving"  -> textContent "● RECEIVING",  className "si-val ok",  style.color ""
    "no_targets" -> textContent "◐ NO TARGETS", className "si-val",     style.color "var(--warn,#FFA500)"
    anything else-> textContent "○ NO DATA",    className "si-val off", style.color ""
  Guard against a missing element. Indent 4 spaces (it sits among sibling functions).

# Output - JSON object with exactly these five string keys, nothing else
{"py_helpers":"...","py_status_body":"...","js_loadstatus_lines":"...","js_avnav_line":"...","js_setais":"..."}
"""


def main():
    with open(CFG) as f:
        cfg = json.load(f)
    key = cfg["gemini_api_key"]
    model = cfg.get("gemini_model", "gemini-2.5-flash-lite")

    body = json.dumps({
        "contents": [{"parts": [{"text": PROMPT}]}],
        "generationConfig": {"temperature": 0.0, "maxOutputTokens": 8192,
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

    print(json.dumps({"model": model,
                      "usage": resp.get("usageMetadata", {}),
                      "result": json.loads(text)}, indent=2))


if __name__ == "__main__":
    main()
