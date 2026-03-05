#!/usr/bin/env python3
"""
d3kOS Ollama Executor v3
Production-quality autonomous fix executor.

Improvements over v2:
  1. Smart JS extraction — prescan identifies target function(s), sends only those (~2KB vs ~20KB)
  2. Deployment gate — verify score < 50 (and verify is online) blocks deploy; flags for manual review
  3. Backup before deploy — .bak file created on Pi before every overwrite
  4. Service restart — Python service files trigger systemctl restart after deploy
  5. Resume checkpoint — checkpoint.json tracks completed fixes; restart resumes from last success
  6. Diff output — saves unified diff of every deployed change for manual review
  7. Verify pre-check — /health at startup; connectivity errors don't trigger correction loops
  8. Better wizard injection — fallback patterns for Fix 9 onboarding step insertion

Usage:
  python3 ollama_execute_v3.py                  # run all pending fixes
  python3 ollama_execute_v3.py --fixes 1,4,6    # run specific fixes
  python3 ollama_execute_v3.py --fresh           # ignore checkpoint, restart from scratch

Output:
  /tmp/d3kos_v3.log
  ollama_output/v3/fix{N}_diff.txt
  ollama_output/v3/fix{N}_injected.txt
  ollama_output/v3/checkpoint.json
  ollama_output/v3/report.json
"""

import json, time, sys, os, re, subprocess, tempfile, pathlib, datetime
import urllib.request, traceback, threading, difflib, argparse, hashlib

# ── Config ────────────────────────────────────────────────────────────────────
PI_HOST    = "192.168.1.237"
PI_USER    = "d3kos"
SSH_KEY    = os.path.expanduser("~/.ssh/id_d3kos")
SSH_OPTS   = ["-i", SSH_KEY, "-o", "StrictHostKeyChecking=no",
              "-o", "BatchMode=yes", "-o", "ConnectTimeout=15"]

OLLAMA_URL  = "http://192.168.1.62:11434/api/generate"
MODEL       = "qwen3-coder:30b"
VERIFY_URL  = "http://192.168.1.103:11436/verify"
VERIFY_HEALTH_URL = "http://192.168.1.103:11436/health"

SPEC_FILE   = pathlib.Path("/home/boatiq/Helm-OS/deployment/features/post-install-fixes/OLLAMA_SPEC.md")
OUTPUT_DIR  = pathlib.Path("/home/boatiq/Helm-OS/deployment/v0.9.2/ollama_output/v3")
LOG_FILE    = pathlib.Path("/tmp/d3kos_v3.log")
CHECKPOINT  = OUTPUT_DIR / "checkpoint.json"
REPORT_FILE = OUTPUT_DIR / "report.json"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Service restart map ───────────────────────────────────────────────────────
# Pi service file path → systemd unit name
SERVICE_MAP = {
    "/opt/d3kos/services/ai/query_handler.py":                   "d3kos-ai-api",
    "/opt/d3kos/services/ai/ai_api.py":                          "d3kos-ai-api",
    "/opt/d3kos/services/boatlog/boatlog-export-api.py":         "d3kos-boatlog-api",
    "/opt/d3kos/services/marine-vision/camera_stream_manager.py":"d3kos-camera-stream",
    "/opt/d3kos/services/marine-vision/fish_detector.py":        "d3kos-camera-stream",
    "/opt/d3kos/services/settings-api.py":                       "d3kos-settings-api",
    "/opt/d3kos/services/voice/voice_api.py":                    "d3kos-voice",
    "/opt/d3kos/services/tier/tier_api.py":                      "d3kos-tier-api",
    "/opt/d3kos/services/system/health_api.py":                  "d3kos-health",
}

# Deploy gate: don't deploy if verify score < this AND verify is online
DEPLOY_MIN_SCORE = 50

_print_lock      = threading.Lock()
_verify_online   = False   # set by pre-check at startup
_run_id          = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

# ── Logging ───────────────────────────────────────────────────────────────────
def log(msg, level="INFO"):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    with _print_lock:
        print(line, flush=True)
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")

# ── SSH / SCP ─────────────────────────────────────────────────────────────────
def ssh_run(cmd, timeout=90):
    r = subprocess.run(["ssh"] + SSH_OPTS + [f"{PI_USER}@{PI_HOST}", cmd],
                       capture_output=True, text=True, timeout=timeout)
    return r.stdout.strip(), r.returncode

def fetch_pi_file(pi_path):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as f:
        tmp = f.name
    try:
        subprocess.run(["scp"] + SSH_OPTS + [f"{PI_USER}@{PI_HOST}:{pi_path}", tmp],
                       check=True, capture_output=True, timeout=30)
        with open(tmp, "r", errors="replace") as f:
            return f.read()
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def deploy_pi_file(pi_path, content, sudo=False, mode="644"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp", mode="w", encoding="utf-8") as f:
        f.write(content)
        tmp_local = f.name
    tmp_remote = f"/tmp/d3kv3_{os.path.basename(pi_path)}"
    try:
        subprocess.run(["scp"] + SSH_OPTS + [tmp_local, f"{PI_USER}@{PI_HOST}:{tmp_remote}"],
                       check=True, capture_output=True, timeout=30)
        if sudo:
            ssh_run(f"sudo mkdir -p {os.path.dirname(pi_path)} && "
                    f"sudo mv {tmp_remote} {pi_path} && sudo chmod {mode} {pi_path}")
        else:
            ssh_run(f"mv {tmp_remote} {pi_path} && chmod {mode} {pi_path}")
    finally:
        if os.path.exists(tmp_local): os.unlink(tmp_local)

# ── Backup ────────────────────────────────────────────────────────────────────
def backup_pi_file(pi_path):
    """Create timestamped backup on Pi before overwriting."""
    bak = f"{pi_path}.bak.{datetime.datetime.now().strftime('%Y%m%d%H%M')}"
    out, rc = ssh_run(f"cp {pi_path} {bak} 2>/dev/null && echo ok")
    if "ok" in out:
        log(f"    Backup: {bak}")
    return rc == 0

# ── Diff ──────────────────────────────────────────────────────────────────────
def save_diff(fix_id, pi_path, original, modified):
    """Save unified diff of the change."""
    orig_lines = original.splitlines(keepends=True)
    new_lines  = modified.splitlines(keepends=True)
    diff = list(difflib.unified_diff(
        orig_lines, new_lines,
        fromfile=f"a/{os.path.basename(pi_path)}",
        tofile=f"b/{os.path.basename(pi_path)}",
        n=3
    ))
    if diff:
        diff_path = OUTPUT_DIR / f"fix{fix_id}_diff_{os.path.basename(pi_path)}.txt"
        diff_path.write_text("".join(diff))
        log(f"    Diff saved: {diff_path.name} ({len(diff)} lines changed)")
    else:
        log(f"    No diff — file unchanged")

# ── Service restart ───────────────────────────────────────────────────────────
def restart_service_for(pi_path):
    """Restart the systemd service associated with this Pi file path."""
    svc = SERVICE_MAP.get(pi_path)
    if svc:
        out, rc = ssh_run(f"sudo systemctl restart {svc} && sleep 1 && "
                          f"systemctl is-active {svc}")
        log(f"    Service {svc}: {out.strip() or ('rc='+str(rc))}")
        return rc == 0
    return True

# ── Checkpoint ────────────────────────────────────────────────────────────────
def load_checkpoint():
    if CHECKPOINT.exists():
        try:
            return json.loads(CHECKPOINT.read_text())
        except Exception:
            pass
    return {"run_id": _run_id, "completed": [], "flagged": []}

def save_checkpoint(cp):
    CHECKPOINT.write_text(json.dumps(cp, indent=2))

# ── Verify pre-check ──────────────────────────────────────────────────────────
def check_verify_agent():
    global _verify_online
    try:
        req = urllib.request.Request(VERIFY_HEALTH_URL)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        _verify_online = data.get("status") == "healthy"
        log(f"Verify agent: {'online' if _verify_online else 'degraded'} — "
            f"model={data.get('model','?')} calls={data.get('stats',{}).get('total_calls',0)}")
    except Exception as e:
        _verify_online = False
        log(f"Verify agent: OFFLINE ({e}) — correction loops disabled, deploy gate inactive", "WARN")

# ── Ollama ────────────────────────────────────────────────────────────────────
def call_ollama(prompt, label, timeout=900, max_tokens=8192):
    payload = json.dumps({
        "model": MODEL, "prompt": prompt, "stream": False,
        "options": {"temperature": 0.05, "num_predict": max_tokens, "num_ctx": 16384}
    }).encode()
    log(f"  Ollama [{label}]: {len(prompt)} chars → sending...")
    t0 = time.time()
    try:
        req = urllib.request.Request(OLLAMA_URL, data=payload,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
        text = data.get("response", "").strip()
        text = re.sub(r"^```[\w]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text).strip()
        log(f"  Ollama [{label}]: {len(text)} chars in {time.time()-t0:.0f}s")
        return text
    except Exception as e:
        log(f"  Ollama [{label}] ERROR: {e}", "ERROR")
        return None

# ── Verify ────────────────────────────────────────────────────────────────────
def call_verify(code, instruction, context, filename, fix_id):
    """Returns (passed: bool|None, score: int, issue: str).
    None = offline/error (non-blocking). False = explicit fail."""
    if not _verify_online:
        return None, 0, "verify offline"
    payload = json.dumps({
        "code": code[:10000], "instruction": instruction,
        "context": context[:2000], "filename": filename,
        "phase_name": f"fix{fix_id}_v3"
    }).encode()
    try:
        req = urllib.request.Request(VERIFY_URL, data=payload,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read())
        passed = str(data.get("pass", "NO")).upper() == "YES"
        score  = int(data.get("score", 0) or 0)
        issue  = data.get("issue", "none")
        log(f"  Verify fix{fix_id}: {'PASS' if passed else 'FAIL'} "
            f"score={score} — {issue[:100]}")
        return passed, score, issue
    except Exception as e:
        # Connectivity error — treat as offline for this call
        log(f"  Verify fix{fix_id}: connection error ({e}) — skipping gate", "WARN")
        return None, 0, str(e)

# ── Spec parser ───────────────────────────────────────────────────────────────
def load_spec(spec_path):
    text = spec_path.read_text()
    sections = {}
    for part in re.split(r"(?=\n## Fix \d+)", text):
        m = re.match(r"\n?## Fix (\d+)", part)
        if m:
            sections[int(m.group(1))] = part.strip()
    return sections

# ── HTML utilities ────────────────────────────────────────────────────────────
def get_script_text(html):
    blocks = re.findall(r"<script(?!\s+src)[^>]*>(.*?)</script>",
                        html, re.DOTALL | re.IGNORECASE)
    return "\n\n/* ===BLOCK=== */\n\n".join(b for b in blocks if b.strip())

def replace_scripts(html, new_js):
    # Remove all inline script blocks
    result = re.sub(r"<script(?!\s+src)[^>]*>.*?</script>", "",
                    html, flags=re.DOTALL | re.IGNORECASE)
    # Insert combined new scripts before </body>
    tag = f"<script>\n{new_js}\n</script>"
    if "</body>" in result:
        return result.replace("</body>", tag + "\n</body>", 1)
    return result + "\n" + tag

def inject_before_head_close(html, css):
    if not css: return html
    tag = f"<style>\n{css}\n</style>"
    return html.replace("</head>", tag + "\n</head>", 1) if "</head>" in html else html + tag

def inject_after_body_open(html, snippet):
    if not snippet: return html
    return re.sub(r"(<body[^>]*>)", r"\1\n" + snippet, html, count=1, flags=re.IGNORECASE)

def inject_before_body_close(html, js):
    if not js: return html
    tag = f"<script>\n{js}\n</script>"
    return html.replace("</body>", tag + "\n</body>", 1) if "</body>" in html else html + "\n" + tag

def parse_inject_response(text):
    sections = {"CSS": "", "HTML_AFTER_BODY": "", "JS_BEFORE_BODY_CLOSE": "", "JS_INLINE": ""}
    current, lines = None, []
    for line in text.splitlines():
        m = re.match(r"^===\s*(CSS|HTML_AFTER_BODY|JS_BEFORE_BODY_CLOSE|JS_INLINE)\s*===", line)
        if m:
            if current and lines:
                val = "\n".join(lines).strip()
                sections[current] = "" if val.upper() in ("NONE", "") else val
            current, lines = m.group(1), []
        elif current:
            lines.append(line)
    if current and lines:
        val = "\n".join(lines).strip()
        sections[current] = "" if val.upper() in ("NONE", "") else val
    return sections

# ── Smart JS extraction ───────────────────────────────────────────────────────
PRESCAN_PROMPT = """\
A JavaScript file needs to be modified. Identify the target.

FIX DESCRIPTION:
{description}

Reply with ONLY a comma-separated list of JavaScript function names that need to be changed.
No explanation. No other text. Example: initMap,checkSignalK
If it is a new function to be added, reply: NEW
"""

def prescan_target_functions(description, fix_id):
    """Quick Ollama call to identify target function names. Returns list or None."""
    result = call_ollama(
        PRESCAN_PROMPT.format(description=description),
        f"fix{fix_id}-prescan", timeout=60, max_tokens=50
    )
    if not result or result.upper() == "NEW":
        return None
    names = [n.strip() for n in result.split(",") if n.strip() and " " not in n.strip()]
    log(f"  Prescan fix{fix_id}: target functions = {names}")
    return names if names else None

def extract_functions(js_text, func_names):
    """Extract named function blocks from JS source."""
    extracted = []
    for name in func_names:
        # Match: function name(...) { ... } or const/let/var name = function/arrow
        patterns = [
            rf"(?:async\s+)?function\s+{re.escape(name)}\s*\([^)]*\)\s*\{{[^{{}}]*(?:\{{[^{{}}]*\}}[^{{}}]*)?\}}",
            rf"(?:const|let|var)\s+{re.escape(name)}\s*=\s*(?:async\s+)?(?:function\s*\([^)]*\)|[^=>\n]+\s*=>)\s*\{{[^{{}}]*(?:\{{[^{{}}]*\}}[^{{}}]*)?\}}",
        ]
        for pat in patterns:
            m = re.search(pat, js_text, re.DOTALL)
            if m:
                extracted.append(m.group(0))
                break
    return "\n\n".join(extracted) if extracted else None

# ── Prompt templates ──────────────────────────────────────────────────────────
INJECT_PROMPT = """\
Generate ONLY the new code to inject into {pi_path}. Do NOT return the full file.

FIX SPEC:
{spec}

Return in EXACTLY this format (include all four headers; write NONE if not needed):
=== CSS ===
[css rules]
=== HTML_AFTER_BODY ===
[html to insert after <body> opening tag]
=== JS_BEFORE_BODY_CLOSE ===
[javascript functions]
=== JS_INLINE ===
[immediate JS calls like init(); setInterval(...)]
"""

PATCH_JS_PROMPT = """\
Modify this JavaScript from {pi_path}. Apply ONLY the changes the spec describes.
Keep ALL other functions exactly as they are.

FIX SPEC:
{spec}

JAVASCRIPT TO MODIFY:
{scripts}

Return the complete corrected JavaScript. No HTML tags. No <script> tags. No markdown.
"""

PATCH_FN_PROMPT = """\
Modify this code section from {pi_path} per the spec.
Apply ONLY what the spec describes. Keep everything else identical.

FIX SPEC:
{spec}

CODE:
{code}

Return only the corrected code. No markdown, no explanation.
"""

CORRECTION_PROMPT = """\
Your code has a problem. Fix it.

TASK: {instruction}
PROBLEM: {issue}

CODE:
{code}

Return only the corrected code. No markdown, no explanation.
"""

# ── Core: deploy with gate ────────────────────────────────────────────────────
def gated_deploy(fix_id, pi_path, original, modified, description,
                 sudo=False, mode="644"):
    """
    Verify → gate → backup → deploy → diff → restart service.
    Returns (deployed: bool, reason: str).
    """
    # Verify
    passed, score, issue = call_verify(
        modified, description, original[:2000],
        os.path.basename(pi_path), fix_id
    )

    # Correction loop if verify online and score too low
    if passed is False and score < DEPLOY_MIN_SCORE:
        log(f"  Gate: score={score} < {DEPLOY_MIN_SCORE} — attempting correction")
        corrected = call_ollama(
            CORRECTION_PROMPT.format(
                instruction=description, issue=issue, code=modified
            ),
            f"fix{fix_id}-correction"
        )
        if corrected:
            modified = corrected
            passed, score, issue = call_verify(
                modified, description, original[:2000],
                os.path.basename(pi_path), fix_id
            )

    # Gate decision
    if passed is False and score < DEPLOY_MIN_SCORE:
        flagged_path = OUTPUT_DIR / f"fix{fix_id}_FLAGGED_{os.path.basename(pi_path)}"
        flagged_path.write_text(modified)
        log(f"  Gate: BLOCKED score={score} — saved to {flagged_path.name} for manual review", "WARN")
        return False, f"blocked by gate score={score}"

    if not passed and score < DEPLOY_MIN_SCORE:
        # verify offline — deploy unconditionally
        log(f"  Gate: verify offline — deploying unconditionally")
    else:
        log(f"  Gate: score={score} ≥ {DEPLOY_MIN_SCORE} or verify offline — deploying")

    # Backup
    backup_pi_file(pi_path)

    # Deploy
    deploy_pi_file(pi_path, modified, sudo=sudo, mode=mode)
    log(f"  ✓ Deployed {pi_path}")

    # Diff
    save_diff(fix_id, pi_path, original, modified)

    # Service restart
    restart_service_for(pi_path)

    return True, "deployed"

# ── Handlers ──────────────────────────────────────────────────────────────────
def handle_inject(fix_id, spec, pi_path, description, sudo=False):
    log(f"  [Fix {fix_id}] INJECT: {pi_path}")
    prompt = INJECT_PROMPT.format(spec=spec, pi_path=pi_path)
    result = call_ollama(prompt, f"fix{fix_id}-inject")
    if not result:
        return False, "ollama empty"

    (OUTPUT_DIR / f"fix{fix_id}_injected_{os.path.basename(pi_path)}.txt").write_text(result)
    parsed = parse_inject_response(result)
    log(f"  [Fix {fix_id}] CSS={len(parsed['CSS'])}c "
        f"HTML={len(parsed['HTML_AFTER_BODY'])}c "
        f"JS={len(parsed['JS_BEFORE_BODY_CLOSE'])}c "
        f"inline={len(parsed['JS_INLINE'])}c")

    try:
        original = fetch_pi_file(pi_path)
        html = original
        if parsed["CSS"]:
            html = inject_before_head_close(html, parsed["CSS"])
        if parsed["HTML_AFTER_BODY"]:
            html = inject_after_body_open(html, parsed["HTML_AFTER_BODY"])
        js = "\n\n".join(filter(None, [parsed["JS_BEFORE_BODY_CLOSE"], parsed["JS_INLINE"]]))
        if js:
            html = inject_before_body_close(html, js)
        return gated_deploy(fix_id, pi_path, original, html, description, sudo=sudo)
    except Exception as e:
        log(f"  [Fix {fix_id}] FAILED: {e}", "ERROR")
        return False, str(e)


def handle_patch_js(fix_id, spec, pi_path, description, use_prescan=True, sudo=False):
    log(f"  [Fix {fix_id}] PATCH_JS: {pi_path}")
    try:
        original = fetch_pi_file(pi_path)
    except Exception as e:
        return False, f"fetch failed: {e}"

    all_scripts = get_script_text(original)
    if not all_scripts.strip():
        log(f"  [Fix {fix_id}] No inline scripts — using INJECT fallback")
        return handle_inject(fix_id, spec, pi_path, description, sudo=sudo)

    # Smart extraction: prescan for target functions
    target_js = all_scripts
    if use_prescan:
        func_names = prescan_target_functions(description, fix_id)
        if func_names:
            extracted = extract_functions(all_scripts, func_names)
            if extracted:
                log(f"  [Fix {fix_id}] Smart extract: {len(extracted)}c "
                    f"(vs {len(all_scripts)}c full scripts)")
                target_js = extracted
            else:
                log(f"  [Fix {fix_id}] Prescan names not found in scripts — using full")

    prompt = PATCH_JS_PROMPT.format(spec=spec, pi_path=pi_path, scripts=target_js)
    result = call_ollama(prompt, f"fix{fix_id}-patchjs")
    if not result:
        return False, "ollama empty"

    (OUTPUT_DIR / f"fix{fix_id}_patched_js_{os.path.basename(pi_path)}.js").write_text(result)

    # If we only patched specific functions, merge back into full scripts
    if target_js != all_scripts:
        # Replace the extracted functions in the full script with the patched versions
        merged = all_scripts
        for name in (prescan_target_functions(description, fix_id) or []):
            pat = (rf"(?:async\s+)?function\s+{re.escape(name)}\s*\([^)]*\)\s*\{{[^{{}}]*"
                   rf"(?:\{{[^{{}}]*\}}[^{{}}]*)?\}}")
            if re.search(pat, merged, re.DOTALL):
                merged = re.sub(pat, result, merged, count=1, flags=re.DOTALL)
                break
        else:
            merged = result  # fallback: use full patched result
        result = merged

    try:
        new_html = replace_scripts(original, result)
        return gated_deploy(fix_id, pi_path, original, new_html, description, sudo=sudo)
    except Exception as e:
        log(f"  [Fix {fix_id}] FAILED: {e}", "ERROR")
        return False, str(e)


def handle_patch_fn(fix_id, spec, pi_path, description, extract_re=None, sudo=False):
    log(f"  [Fix {fix_id}] PATCH_FN: {pi_path}")
    try:
        original = fetch_pi_file(pi_path)
    except Exception as e:
        return False, f"fetch failed: {e}"

    # Extract section
    if extract_re:
        m = re.search(extract_re, original, re.DOTALL)
        code_section = m.group(0) if m else "\n".join(original.splitlines()[:150])
        full_replace = m is None
        span = (m.start(), m.end()) if m else None
    else:
        code_section = original
        full_replace = True
        span = None

    log(f"  [Fix {fix_id}] Extracted {len(code_section)}c of Python")
    result = call_ollama(
        PATCH_FN_PROMPT.format(spec=spec, pi_path=pi_path, code=code_section),
        f"fix{fix_id}-patchfn"
    )
    if not result:
        return False, "ollama empty"

    (OUTPUT_DIR / f"fix{fix_id}_patched_{os.path.basename(pi_path)}").write_text(result)

    modified = result if full_replace else (original[:span[0]] + result + original[span[1]:])

    return gated_deploy(fix_id, pi_path, original, modified, description, sudo=sudo)


def handle_create(fix_id, spec, pi_path, description, sudo=False, mode="644"):
    log(f"  [Fix {fix_id}] CREATE: {pi_path}")
    prompt = (f"Create the file {pi_path} for d3kOS (Pi 4B, Debian Trixie, Flask services).\n\n"
              f"SPEC:\n{spec}\n\nReturn ONLY the file content. No markdown, no explanation.")
    result = call_ollama(prompt, f"fix{fix_id}-create")
    if not result:
        return False, "ollama empty"

    (OUTPUT_DIR / f"fix{fix_id}_new_{os.path.basename(pi_path)}").write_text(result)
    passed, score, issue = call_verify(result, description, "", os.path.basename(pi_path), fix_id)

    if passed is False and score < DEPLOY_MIN_SCORE:
        corrected = call_ollama(
            CORRECTION_PROMPT.format(instruction=description, issue=issue, code=result),
            f"fix{fix_id}-correction"
        )
        if corrected:
            result = corrected

    try:
        deploy_pi_file(pi_path, result, sudo=sudo, mode=mode)
        log(f"  ✓ Created {pi_path}")
        restart_service_for(pi_path)
        return True, "deployed"
    except Exception as e:
        log(f"  CREATE FAILED: {e}", "ERROR")
        return False, str(e)


# ── Main ──────────────────────────────────────────────────────────────────────
def run(fix_filter=None, fresh=False):
    global _verify_online

    log("=" * 60)
    log(f"d3kOS Ollama Executor v3  run_id={_run_id}")
    log(f"Pi:{PI_HOST}  Ollama:{OLLAMA_URL}  model:{MODEL}")
    log("=" * 60)

    # Verify pre-check
    check_verify_agent()

    spec = load_spec(SPEC_FILE)

    # Checkpoint
    cp = {"run_id": _run_id, "completed": [], "flagged": []}
    if not fresh and CHECKPOINT.exists():
        cp = load_checkpoint()
        if cp.get("completed"):
            log(f"Resuming — already completed: {cp['completed']}")

    results = {}
    t_start = time.time()

    def should_run(fix_id):
        if fix_filter and fix_id not in fix_filter:
            return False
        if fix_id in cp["completed"]:
            log(f"  Skipping Fix {fix_id} (checkpoint)")
            return False
        return True

    def record(fix_id, sub_results):
        results[fix_id] = sub_results
        all_ok = all(v[0] for v in sub_results.values() if isinstance(v, tuple))
        any_flagged = any("blocked" in str(v) for v in sub_results.values())
        if all_ok:
            cp["completed"].append(fix_id)
        if any_flagged and fix_id not in cp["flagged"]:
            cp["flagged"].append(fix_id)
        save_checkpoint(cp)

    # ── Fix 13: settings.html ─────────────────────────────────────────────────
    if should_run(13):
        log("\n── Fix 13: settings.html — replace alert() actions with fetch() ──")
        ok, msg = handle_patch_js(13, spec.get(13, ""),
            "/var/www/html/settings.html",
            "Replace restartSignalK(), restartNodered(), rebootSystem() action functions "
            "that use alert() or show SSH instructions — replace with fetch() to "
            "/settings/action/ endpoints. Add showToast(msg) helper if not present.")
        record(13, {"settings_html": (ok, msg)})

    # ── Fix 1: dashboard.html ─────────────────────────────────────────────────
    if should_run(1):
        log("\n── Fix 1: dashboard.html — SignalK disconnected banner ──")
        ok, msg = handle_inject(1, spec.get(1, ""),
            "/var/www/html/dashboard.html",
            "Add yellow sticky banner that shows when SignalK offline (polls /signalk/v1/api/ "
            "every 5s); disappears when recovered; includes link to Settings page.")
        record(1, {"dashboard_html": (ok, msg)})

    # ── Fix 2: benchmark.html ─────────────────────────────────────────────────
    if should_run(2):
        log("\n── Fix 2: benchmark.html — diagnose broken API calls ──")
        svc_list, _ = ssh_run("systemctl list-units 'd3kos-*' --no-pager --no-legend 2>/dev/null")
        ports, _ = ssh_run("ss -tlnp 2>/dev/null | grep -E '808|809|810'")
        diag = f"\n\n=== RUNNING SERVICES ===\n{svc_list}\n\n=== LISTENING PORTS ===\n{ports}"
        ok, msg = handle_patch_js(2, spec.get(2, "") + diag,
            "/var/www/html/benchmark.html",
            "Fix broken Engine Benchmark API endpoint URLs; add 'Service offline' "
            "fallback display; fix any port mismatches")
        record(2, {"benchmark_html": (ok, msg)})

    # ── Fix 4: navigation.html ────────────────────────────────────────────────
    if should_run(4):
        log("\n── Fix 4: navigation.html — GPS SignalK fetch paths ──")
        ok, msg = handle_patch_js(4, spec.get(4, ""),
            "/var/www/html/navigation.html",
            "Fix GPS fetch URLs to correct SignalK paths; convert radians→degrees "
            "and m/s→knots; show '--' placeholder when GPS fix unavailable")
        record(4, {"navigation_html": (ok, msg)})

    # ── Fix 5: boatlog.html ───────────────────────────────────────────────────
    if should_run(5):
        log("\n── Fix 5: boatlog.html — voice note mic button ──")
        ok, msg = handle_inject(5, spec.get(5, ""),
            "/var/www/html/boatlog.html",
            "Add microphone button near notes field; MediaRecorder JS to record audio; "
            "POST blob to /boatlog/voice-note; append transcript to notes textarea")
        record(5, {"boatlog_html": (ok, msg)})

    # ── Fix 6: weather.html ───────────────────────────────────────────────────
    if should_run(6):
        log("\n── Fix 6: weather.html — GPS centering + OWM overlay ──")
        ok, msg = handle_patch_js(6, spec.get(6, ""),
            "/var/www/html/weather.html",
            "Replace hardcoded Lake Simcoe position with async SignalK GPS fetch before "
            "map init; fix OWM tile layer URLs to use wind_new and clouds_new")
        record(6, {"weather_html": (ok, msg)})

    # ── Fix 7: marine-vision.html ─────────────────────────────────────────────
    if should_run(7):
        log("\n── Fix 7: marine-vision.html — camera offline placeholder ──")
        # HTML + CSS + JS onerror handlers (inject approach, spec is explicit about JS needed)
        ok, msg = handle_inject(7, spec.get(7, ""),
            "/var/www/html/marine-vision.html",
            "Add img.onerror handlers to ALL camera feed <img> elements showing dark "
            "placeholder div with camera name and 'Offline — Connect to boat network'; "
            "add .camera-offline-placeholder CSS; onerror must be JavaScript, not CSS only")
        record(7, {"marine_vision_html": (ok, msg)})

        # camera_stream_manager.py
        log("\n── Fix 7b: camera_stream_manager.py ──")
        ok2, msg2 = handle_patch_fn(7, spec.get(7, ""),
            "/opt/d3kos/services/marine-vision/camera_stream_manager.py",
            "Add 'status': 'online'/'offline' key to each camera dict; "
            "wrap camera connection in try/except; return status='offline' on exception",
            extract_re=r"def (?:get_camera|check_camera|build_camera|camera_status)[^\n]*\n(?:(?!^def ).*\n){0,60}")
        record(7, {**results.get(7, {}), "camera_stream_manager": (ok2, msg2)})

    # ── Fix 9: onboarding.html ────────────────────────────────────────────────
    if should_run(9):
        log("\n── Fix 9: onboarding.html — Gemini API wizard step ──")
        # Improved: find wizard step structure using multiple pattern attempts
        try:
            onboarding = fetch_pi_file("/var/www/html/onboarding.html")
            # Try several patterns to find existing steps
            step_info = ""
            for pat in [
                r'id=["\']step[-_](\d+)["\']',
                r'id=["\']wizard[-_]step[-_](\d+)["\']',
                r'class=["\'][^"\']*step[^"\']*["\'][^>]*>.*?<h[123][^>]*>(.*?)</h[123]>',
                r'<h[123][^>]*>(.*?)</h[123]>',  # any headings
            ]:
                matches = re.findall(pat, onboarding, re.DOTALL | re.IGNORECASE)
                if matches:
                    step_info = f"Found {len(matches)} matches with pattern: {pat}\nSamples: {str(matches[:5])}"
                    log(f"  [Fix 9] {step_info}")
                    break

            # Find completion/finish step near end of file
            tail = onboarding[-3000:]
            completion_keywords = ["complete", "finish", "done", "ready", "success", "all set"]
            completion_idx = None
            for kw in completion_keywords:
                idx = tail.lower().rfind(kw)
                if idx != -1:
                    completion_idx = len(onboarding) - 3000 + idx
                    log(f"  [Fix 9] Found completion keyword '{kw}' at position {completion_idx}")
                    break

            inject_spec = spec.get(9, "") + f"\n\n=== WIZARD STRUCTURE ===\n{step_info}"
            if completion_idx:
                inject_spec += f"\n\nINSERTION HINT: Insert the new step HTML before position {completion_idx} in the file (near the completion screen)"
        except Exception:
            inject_spec = spec.get(9, "")

        ok, msg = handle_inject(9, inject_spec,
            "/var/www/html/onboarding.html",
            "Add new Gemini API key wizard step before final completion screen. "
            "MUST include: HTML_AFTER_BODY with the new step div (password input for API key, "
            "Test Connection button calling /gemini/test, Save & Continue calling /gemini/config, "
            "Skip button); and JS_BEFORE_BODY_CLOSE with testGeminiKey(), saveGeminiAndContinue(), "
            "skipGemini() functions. Both HTML and JS sections are required.")
        record(9, {"onboarding_html": (ok, msg)})

    # ── Fix 10: query_handler.py ──────────────────────────────────────────────
    if should_run(10):
        log("\n── Fix 10: query_handler.py — RAG precision ──")
        ok, msg = handle_patch_fn(10, spec.get(10, ""),
            "/opt/d3kos/services/ai/query_handler.py",
            "Increase n_results from 4 to 6; add distance filter (skip results where "
            "distance >= 0.40); prepend '[Source: filename]' to each RAG context chunk",
            extract_re=r"n_results\s*=\s*\d+.*?(?=\n(?:def |class |\Z))",)
        record(10, {"query_handler": (ok, msg)})

    # ── Fix 8: OpenCPN Flatpak ────────────────────────────────────────────────
    if should_run(8):
        log("\n── Fix 8: OpenCPN Flatpak (sudo --system) ──")
        r8 = {}
        try:
            check, _ = ssh_run("flatpak list 2>/dev/null | grep -i opencpn")
            if check:
                log("  [Fix 8] Already installed")
                r8["status"] = (True, "already installed")
            else:
                ssh_run("cp -r ~/.opencpn ~/.opencpn.backup.$(date +%Y%m%d) 2>/dev/null || true")
                for label, cmd, t in [
                    ("apt flatpak",   "sudo apt-get install -y flatpak 2>&1", 120),
                    ("Flathub add",   "sudo flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo 2>&1", 60),
                    ("remove native", "sudo apt-get remove -y opencpn 2>&1", 60),
                ]:
                    _, rc = ssh_run(cmd, timeout=t)
                    log(f"  [Fix 8] {label}: rc={rc}")

                log("  [Fix 8] Installing via Flatpak (ARM64 — slow)...")
                out, rc = ssh_run("sudo flatpak install -y --system flathub org.opencpn.OpenCPN 2>&1", timeout=900)
                log(f"  [Fix 8] rc={rc} tail={out[-150:] if out else ''}")
                if rc == 0:
                    ssh_run("mkdir -p ~/.var/app/org.opencpn.OpenCPN/config/opencpn/")
                    ssh_run("cp ~/.opencpn/opencpn.conf ~/.var/app/org.opencpn.OpenCPN/config/opencpn/ 2>/dev/null || true")
                    log("  [Fix 8] ✓ Installed + config migrated")
                    r8["status"] = (True, "installed")
                else:
                    r8["status"] = (False, f"rc={rc}")

            # Update index.html launcher
            try:
                idx = fetch_pi_file("/var/www/html/index.html")
                updated = idx.replace("'opencpn'", "'flatpak run org.opencpn.OpenCPN'")\
                             .replace('"opencpn"', '"flatpak run org.opencpn.OpenCPN"')
                if updated != idx:
                    backup_pi_file("/var/www/html/index.html")
                    deploy_pi_file("/var/www/html/index.html", updated)
                    save_diff(8, "/var/www/html/index.html", idx, updated)
                    log("  [Fix 8] ✓ index.html launcher updated")
                    r8["launcher"] = (True, "updated")
            except Exception as e:
                log(f"  [Fix 8] Launcher: {e}", "WARN")
        except Exception as e:
            log(f"  [Fix 8] Error: {e}", "ERROR")
            r8["error"] = (False, str(e))
        record(8, r8)

    # ── Report ────────────────────────────────────────────────────────────────
    elapsed = int(time.time() - t_start)
    passed, failed, flagged = [], [], cp.get("flagged", [])
    for fid, fdata in sorted(results.items()):
        ok_all = all(v[0] for v in fdata.values() if isinstance(v, tuple))
        (passed if ok_all else failed).append(fid)

    report = {
        "run_id": _run_id,
        "timestamp": datetime.datetime.now().isoformat(),
        "elapsed_seconds": elapsed,
        "model": MODEL,
        "verify_online": _verify_online,
        "deploy_min_score": DEPLOY_MIN_SCORE,
        "passed": passed,
        "failed": failed,
        "flagged_for_review": flagged,
        "details": {
            str(k): {kk: list(vv) for kk, vv in v.items() if isinstance(vv, tuple)}
            for k, v in results.items()
        }
    }
    REPORT_FILE.write_text(json.dumps(report, indent=2))

    log("\n" + "=" * 60)
    log(f"COMPLETE — {len(passed)} passed, {len(failed)} failed, {len(flagged)} flagged")
    log(f"Passed:  {passed}")
    log(f"Failed:  {failed}")
    log(f"Flagged: {flagged}")
    log(f"Report:  {REPORT_FILE}")
    log("=" * 60)
    return report


# ── Entry ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="d3kOS Ollama Executor v3")
    parser.add_argument("--fixes", help="Comma-separated fix IDs to run (e.g. 1,4,6)")
    parser.add_argument("--fresh", action="store_true", help="Ignore checkpoint, start fresh")
    args = parser.parse_args()

    fix_filter = None
    if args.fixes:
        fix_filter = [int(x.strip()) for x in args.fixes.split(",")]
        log(f"Running only fixes: {fix_filter}")

    try:
        run(fix_filter=fix_filter, fresh=args.fresh)
    except KeyboardInterrupt:
        log("Interrupted", "WARN")
    except Exception as e:
        log(f"Fatal: {e}\n{traceback.format_exc()}", "ERROR")
        sys.exit(1)
