#!/usr/bin/env python3
"""
d3kOS Ollama Benchmark

Measures Ollama model quality on real spec-driven code generation tasks
drawn from deployed feature specs.

Usage:
  python3 benchmark.py                          # test default model
  python3 benchmark.py --model qwen3-coder:30b
  python3 benchmark.py --all                    # test all known models
  python3 benchmark.py --list                   # show available models on Ollama

Results saved to: deployment/scripts/benchmark_results.json
"""

import sys, json, time, re, difflib, tempfile, subprocess, pathlib, argparse
import urllib.request, urllib.error
from datetime import datetime

OLLAMA_URL = "http://192.168.1.36:11434"
RESULTS_FILE = pathlib.Path(__file__).parent / "benchmark_results.json"

KNOWN_MODELS = [
    "deepseek-coder-v2:16b",
    "qwen3-coder:30b",
]

# ---------------------------------------------------------------------------
# Test cases
# Each test case has:
#   name       — identifier
#   lang       — 'python' or 'javascript'
#   prompt     — the full instruction given to the model
#   reference  — the known-correct output (from deployed spec)
#   keywords   — strings that MUST appear in output
#   variables  — exact variable names the spec requires
#   forbidden  — patterns that should NOT appear (instruction-following)
# ---------------------------------------------------------------------------

TESTS = [

  {
    "name": "camera-assign-api",
    "lang": "python",
    "prompt": """\
You are modifying a Python Flask application called camera_stream_manager.py.

## CURRENT FILE CONTEXT

```python
@app.route('/camera/grid', methods=['GET'])
def camera_grid():
    \"\"\"Return a multi-camera JPEG grid image.\"\"\"
    with cam_state_lock:
        frames = [cam_state[c].get('frame') for c in cameras if cam_state.get(c, {}).get('frame')]
```

## SPEC

Write a new Flask route to insert BEFORE `@app.route('/camera/grid', methods=['GET'])`.

Requirements:
- URL: `/camera/assign`, method: POST
- Function name: `assign_camera_position`
- Read `camera_id` and `position` from JSON body using variable names `cam_id` and `position`
- Define list named `valid_positions`: `['bow', 'stern', 'port', 'starboard', 'unassigned']`
- Return 400 + `{'ok': False, 'error': 'invalid position'}` if position not in valid_positions
- Open `CAMERAS_CONFIG`, load into variable named `config`
- Iterate `config['cameras']` as a list of dicts
- Use a boolean `found = False`; set True when cam['id'] == cam_id
- If cam already has that position AND position != 'unassigned': set cam['position'] = 'unassigned'
- After loop: if not found, return 404 + `{'ok': False, 'error': 'camera not found'}`
- Second loop over `config['cameras']`: set cam['position'] = position where cam['id'] == cam_id
- Write back: `json.dump(config, f, indent=2)`
- Return `{'ok': True, 'camera_id': cam_id, 'position': position}`

Variables in scope (exact names): `CAMERAS_CONFIG`, `json`, `request`, `jsonify`
Do NOT add any imports. Do NOT add markdown fences. Write ONLY the Python code.
""",
    "reference": """\
@app.route('/camera/assign', methods=['POST'])
def assign_camera_position():
    data = request.get_json()
    cam_id = data.get('camera_id')
    position = data.get('position')
    valid_positions = ['bow', 'stern', 'port', 'starboard', 'unassigned']
    if position not in valid_positions:
        return jsonify({'ok': False, 'error': 'invalid position'}), 400
    with open(CAMERAS_CONFIG) as f:
        config = json.load(f)
    found = False
    for cam in config['cameras']:
        if cam['id'] == cam_id:
            found = True
        if cam.get('position') == position and position != 'unassigned':
            cam['position'] = 'unassigned'
    if not found:
        return jsonify({'ok': False, 'error': 'camera not found'}), 404
    for cam in config['cameras']:
        if cam['id'] == cam_id:
            cam['position'] = position
    with open(CAMERAS_CONFIG, 'w') as f:
        json.dump(config, f, indent=2)
    return jsonify({'ok': True, 'camera_id': cam_id, 'position': position})
""",
    "keywords": [
        "/camera/assign",
        "assign_camera_position",
        "valid_positions",
        "CAMERAS_CONFIG",
        "camera not found",
        "invalid position",
        "indent=2",
        "'ok': True",
        "config['cameras']",
        "position != 'unassigned'",
    ],
    "variables": ["cam_id", "position", "valid_positions", "config", "found"],
    "forbidden": ["```", "import ", "camera_id ="],   # fences, extra imports, wrong var name
  },

  {
    "name": "camera-vision-buttons",
    "lang": "javascript",
    "prompt": """\
You are modifying marine-vision.html, a boat navigation web page.

## CURRENT FILE CONTEXT

```javascript
    function renderSelector(cams, activeId) {
      const sel = document.getElementById('cameraSelector');
      let html = '';

      cams.forEach(cam => {
        const isActive  = cam.id === activeId && !gridMode;
        const isOffline = !cam.connected;
        let cls = 'cam-btn';
        if (isActive)  cls += ' active';
        if (isOffline) cls += ' offline';
        html += `<button class="${cls}" onclick="switchCamera('${cam.id}')">${cam.name}</button>`;
      });

      if (cams.length > 1) {
        const gCls = 'grid-btn' + (gridMode ? ' active' : '');
        html += `<button class="${gCls}" onclick="toggleGrid()">Grid View</button>`;
      }

      sel.innerHTML = html;
    }
```

## SPEC

Replace the entire `renderSelector` function body with a version that shows direction labels.

Requirements:
- Keep function signature: `function renderSelector(cams, activeId)`
- Define `const posOrder = ['bow', 'stern', 'port', 'starboard']`
- Loop posOrder with `posOrder.forEach(function(pos) { ... })`
- Inside loop: find camera with `cams.find(function(c) { return c.position === pos; })`
- If no cam found for that pos: `return` (skip)
- Build `cls` with `'cam-btn'`, add `' active'` and `' offline'` same as before
- Label: `pos.charAt(0).toUpperCase() + pos.slice(1)`
- Button uses `switchCamera(cam.id)` and shows label
- After posOrder loop: add `if (!html)` fallback that loops all cams and uses `cam.name`
- Keep Grid View button logic unchanged (only if cams.length > 1)
- Last line of function body: `sel.innerHTML = html;`

Variables in scope: `gridMode`, `cams`, `activeId`, `switchCamera`, `toggleGrid`
Do NOT add markdown fences. Do NOT modify switchCamera or toggleGrid.
Write ONLY the replacement function body including the opening and closing lines.
""",
    "reference": """\
    function renderSelector(cams, activeId) {
      const sel = document.getElementById('cameraSelector');
      let html = '';
      const posOrder = ['bow', 'stern', 'port', 'starboard'];
      posOrder.forEach(function(pos) {
        const cam = cams.find(function(c) { return c.position === pos; });
        if (!cam) return;
        const isActive  = cam.id === activeId && !gridMode;
        const isOffline = !cam.connected;
        let cls = 'cam-btn';
        if (isActive)  cls += ' active';
        if (isOffline) cls += ' offline';
        const label = pos.charAt(0).toUpperCase() + pos.slice(1);
        html += `<button class="${cls}" onclick="switchCamera('${cam.id}')">${label}</button>`;
      });
      if (!html) {
        cams.forEach(function(cam) {
          const isActive  = cam.id === activeId && !gridMode;
          const isOffline = !cam.connected;
          let cls = 'cam-btn';
          if (isActive)  cls += ' active';
          if (isOffline) cls += ' offline';
          html += `<button class="${cls}" onclick="switchCamera('${cam.id}')">${cam.name}</button>`;
        });
      }
      if (cams.length > 1) {
        const gCls = 'grid-btn' + (gridMode ? ' active' : '');
        html += `<button class="${gCls}" onclick="toggleGrid()">Grid View</button>`;
      }
      sel.innerHTML = html;
    }
""",
    "keywords": [
        "renderSelector",
        "posOrder",
        "c.position === pos",
        "charAt(0).toUpperCase()",
        "if (!html)",
        "sel.innerHTML = html",
        "toggleGrid()",
        "Grid View",
        "cameraSelector",
    ],
    "variables": ["posOrder", "sel", "html", "cls", "label", "gCls"],
    "forbidden": ["```", "cam.name", "cams.forEach(cam =>"],  # fences, old pattern, arrow fn in outer loop
  },

  {
    "name": "simple-instruction-follow",
    "lang": "python",
    "prompt": """\
Write a Python function called `celsius_to_fahrenheit` that:
- Takes one parameter named `celsius`
- Returns `celsius * 9 / 5 + 32`
- No docstring, no type hints, no comments

Do NOT add markdown fences. Write ONLY the function definition.
""",
    "reference": """\
def celsius_to_fahrenheit(celsius):
    return celsius * 9 / 5 + 32
""",
    "keywords": [
        "def celsius_to_fahrenheit(celsius)",
        "return",
        "9",
        "32",
    ],
    "variables": ["celsius"],
    "forbidden": ["```", '"""', "#"],
  },

]


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def check_syntax(code: str, lang: str) -> tuple[bool, str]:
    """Returns (passed, error_message)."""
    if lang == "python":
        try:
            compile(code, "<benchmark>", "exec")
            return True, ""
        except SyntaxError as e:
            return False, str(e)
    elif lang == "javascript":
        with tempfile.NamedTemporaryFile(suffix=".js", mode="w", delete=False) as f:
            f.write(code)
            fname = f.name
        try:
            r = subprocess.run(["node", "--check", fname],
                               capture_output=True, text=True, timeout=10)
            if r.returncode == 0:
                return True, ""
            return False, r.stderr.strip().split("\n")[0]
        except Exception as e:
            return False, str(e)
        finally:
            pathlib.Path(fname).unlink(missing_ok=True)
    return True, ""


def similarity_score(output: str, reference: str) -> float:
    """SequenceMatcher ratio between stripped outputs, 0.0–1.0."""
    a = re.sub(r'\s+', ' ', output.strip())
    b = re.sub(r'\s+', ' ', reference.strip())
    return difflib.SequenceMatcher(None, a, b).ratio()


def strip_fences(text: str) -> str:
    text = re.sub(r'^```[a-zA-Z]*\n', '', text, flags=re.MULTILINE)
    text = re.sub(r'^```\s*$', '', text, flags=re.MULTILINE)
    return text.strip()


def score_response(output: str, test: dict) -> dict:
    """
    Returns a dict of per-dimension scores and a total (0–100).

    Dimensions (20 pts each):
      syntax       — code parses / node --check passes
      keywords     — required strings all present
      no_forbidden — none of the forbidden patterns present
      variables    — exact variable names used
      similarity   — diff against reference code
    """
    cleaned = strip_fences(output)

    # 1. Syntax (20 pts)
    syn_ok, syn_err = check_syntax(cleaned, test["lang"])
    syntax_score = 20 if syn_ok else 0

    # 2. Keywords (20 pts, proportional)
    kw_hits = sum(1 for k in test["keywords"] if k in cleaned)
    kw_total = len(test["keywords"])
    keyword_score = round(20 * kw_hits / kw_total) if kw_total else 20

    # 3. No forbidden patterns (20 pts, -4 per violation)
    violations = [f for f in test["forbidden"] if f in cleaned]
    forbidden_score = max(0, 20 - len(violations) * 4)

    # 4. Variable names (20 pts, proportional)
    var_hits = sum(1 for v in test["variables"] if v in cleaned)
    var_total = len(test["variables"])
    variable_score = round(20 * var_hits / var_total) if var_total else 20

    # 5. Similarity to reference (20 pts)
    sim = similarity_score(cleaned, test["reference"])
    similarity_score_ = round(20 * sim)

    total = syntax_score + keyword_score + forbidden_score + variable_score + similarity_score_

    return {
        "syntax":     {"score": syntax_score,     "max": 20, "detail": syn_err or "ok"},
        "keywords":   {"score": keyword_score,     "max": 20, "detail": f"{kw_hits}/{kw_total} hits"},
        "forbidden":  {"score": forbidden_score,   "max": 20, "detail": f"violations: {violations}" if violations else "clean"},
        "variables":  {"score": variable_score,    "max": 20, "detail": f"{var_hits}/{var_total} exact names"},
        "similarity": {"score": similarity_score_, "max": 20, "detail": f"{sim:.0%} match to reference"},
        "total":      total,
        "max":        100,
    }


# ---------------------------------------------------------------------------
# Ollama call
# ---------------------------------------------------------------------------

def call_ollama(model: str, prompt: str, timeout: int = 120) -> tuple[str, dict]:
    """Returns (response_text, stats_dict)."""
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 700},
    }).encode()
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read())
    elapsed = time.time() - t0
    return data.get("response", ""), {
        "elapsed_s":    round(elapsed, 1),
        "tokens_in":    data.get("prompt_eval_count", 0),
        "tokens_out":   data.get("eval_count", 0),
        "tokens_per_s": round(data.get("eval_count", 0) / max(elapsed, 0.1), 1),
    }


def list_models() -> list[str]:
    req = urllib.request.Request(f"{OLLAMA_URL}/api/tags", method="GET")
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
    return [m["name"] for m in data.get("models", [])]


# ---------------------------------------------------------------------------
# Run benchmark for one model
# ---------------------------------------------------------------------------

def run_model(model: str, verbose: bool = True) -> dict:
    results = {"model": model, "timestamp": datetime.now().isoformat(), "tests": {}}
    totals = []

    for test in TESTS:
        if verbose:
            print(f"\n  [{test['name']}]", end="", flush=True)

        try:
            response, stats = call_ollama(model, test["prompt"])
        except Exception as e:
            if verbose:
                print(f" ERROR: {e}")
            results["tests"][test["name"]] = {"error": str(e)}
            continue

        scores = score_response(response, test)
        totals.append(scores["total"])

        results["tests"][test["name"]] = {
            "scores": scores,
            "stats":  stats,
            "output_snippet": response[:300].replace("\n", "↵"),
        }

        if verbose:
            t = scores["total"]
            bar = "█" * (t // 5) + "░" * (20 - t // 5)
            print(f" {t:3d}/100 [{bar}] {stats['elapsed_s']}s")
            for dim, v in scores.items():
                if dim in ("total", "max"):
                    continue
                status = "✓" if v["score"] == v["max"] else "✗" if v["score"] == 0 else "~"
                print(f"    {status} {dim:<12} {v['score']:2d}/{v['max']} — {v['detail']}")

    overall = round(sum(totals) / len(totals)) if totals else 0
    results["overall"] = overall
    results["test_count"] = len(totals)

    if verbose:
        print(f"\n  {'─'*50}")
        print(f"  OVERALL  {overall}/100  ({len(totals)} tests)")

    return results


# ---------------------------------------------------------------------------
# Save / load results
# ---------------------------------------------------------------------------

def save_result(result: dict):
    existing = []
    if RESULTS_FILE.exists():
        try:
            existing = json.loads(RESULTS_FILE.read_text())
        except Exception:
            existing = []
    existing.append(result)
    RESULTS_FILE.write_text(json.dumps(existing, indent=2))


def print_comparison(results: list[dict]):
    print(f"\n{'═'*60}")
    print("  HEAD-TO-HEAD COMPARISON")
    print(f"{'═'*60}")
    tests = [t["name"] for t in TESTS]
    col = 22
    header = f"  {'Test':<28}" + "".join(f"{r['model'][:col]:<{col}}" for r in results)
    print(header)
    print(f"  {'─'*28}" + "─" * (col * len(results)))
    for tname in tests:
        row = f"  {tname:<28}"
        for r in results:
            td = r["tests"].get(tname, {})
            score = td.get("scores", {}).get("total", "ERR")
            elapsed = td.get("stats", {}).get("elapsed_s", "-")
            row += f"{str(score)+'/100':>8}  {str(elapsed)+'s':<12}"
        print(row)
    print(f"  {'─'*28}" + "─" * (col * len(results)))
    overall_row = f"  {'OVERALL':<28}"
    for r in results:
        overall_row += f"{str(r.get('overall','?'))+'/100':>8}  {'':12}"
    print(overall_row)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="d3kOS Ollama Benchmark")
    parser.add_argument("--model", default=None, help="Model to test")
    parser.add_argument("--all",   action="store_true", help="Test all known models")
    parser.add_argument("--list",  action="store_true", help="List available models")
    args = parser.parse_args()

    if args.list:
        print("Models available on Ollama:")
        for m in list_models():
            print(f"  {m}")
        return

    models_to_test = KNOWN_MODELS if args.all else [args.model or "deepseek-coder-v2:16b"]

    # Verify models exist
    available = list_models()
    for m in models_to_test:
        if m not in available:
            print(f"✗ Model not found: {m}  (run: ollama pull {m})")
            sys.exit(1)

    all_results = []
    for model in models_to_test:
        print(f"\n{'═'*60}")
        print(f"  BENCHMARKING: {model}")
        print(f"{'═'*60}")
        result = run_model(model)
        save_result(result)
        all_results.append(result)
        print(f"\n  Results saved → {RESULTS_FILE}")

    if len(all_results) > 1:
        print_comparison(all_results)


if __name__ == "__main__":
    main()
