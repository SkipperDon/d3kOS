#!/usr/bin/env python3
"""
d3kOS Post-Install Fix Executor v2
Re-runs the 10 fixes that failed in v1 due to HTML file size timeouts.

Strategy:
  INJECT      — generate ONLY new code blocks, inject at known HTML locations
  PATCH_JS    — extract <script> blocks only (~30% file size), patch, replace
  PATCH_FN    — extract one Python function, patch it, replace in file
  DIRECT      — mechanical change, no Ollama needed
  COMMANDS    — run shell commands on Pi

Usage:
  nohup python3 ollama_execute_fixes_v2.py > /tmp/d3kos_fixes_v2.log 2>&1 &

Output:
  /tmp/d3kos_fixes_v2.log
  ollama_output/fixes_v2_report.json
"""

import json, time, sys, os, re, subprocess, tempfile, pathlib, datetime
import urllib.request, traceback, threading

# ── Config ────────────────────────────────────────────────────────────────────
PI_HOST    = "192.168.1.237"
PI_USER    = "d3kos"
SSH_KEY    = os.path.expanduser("~/.ssh/id_d3kos")
SSH_OPTS   = ["-i", SSH_KEY, "-o", "StrictHostKeyChecking=no",
              "-o", "BatchMode=yes", "-o", "ConnectTimeout=15"]

OLLAMA_URL = "http://192.168.1.62:11434/api/generate"
MODEL      = "qwen3-coder:30b"
VERIFY_URL = "http://192.168.1.103:11436/verify"

SPEC_FILE  = pathlib.Path("/home/boatiq/Helm-OS/deployment/features/post-install-fixes/OLLAMA_SPEC.md")
OUTPUT_DIR = pathlib.Path("/home/boatiq/Helm-OS/deployment/v0.9.2/ollama_output/fixes_v2")
REPORT_FILE = pathlib.Path("/home/boatiq/Helm-OS/deployment/v0.9.2/ollama_output/fixes_v2_report.json")
LOG_FILE   = pathlib.Path("/tmp/d3kos_fixes_v2.log")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
_print_lock = threading.Lock()

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
    tmp_remote = f"/tmp/d3kfix2_{os.path.basename(pi_path)}"
    try:
        subprocess.run(["scp"] + SSH_OPTS + [tmp_local, f"{PI_USER}@{PI_HOST}:{tmp_remote}"],
                       check=True, capture_output=True, timeout=30)
        if sudo:
            pi_dir = os.path.dirname(pi_path)
            ssh_run(f"sudo mkdir -p {pi_dir} && sudo mv {tmp_remote} {pi_path} && sudo chmod {mode} {pi_path}")
        else:
            ssh_run(f"mv {tmp_remote} {pi_path} && chmod {mode} {pi_path}")
    finally:
        if os.path.exists(tmp_local): os.unlink(tmp_local)

# ── Ollama ────────────────────────────────────────────────────────────────────
def call_ollama(prompt, label, timeout=900):
    payload = json.dumps({
        "model": MODEL, "prompt": prompt, "stream": False,
        "options": {"temperature": 0.05, "num_predict": 8192, "num_ctx": 16384}
    }).encode()
    log(f"  Ollama [{label}]: {len(prompt)} chars → sending...")
    t0 = time.time()
    try:
        req = urllib.request.Request(OLLAMA_URL, data=payload,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
        text = data.get("response", "").strip()
        # Strip accidental markdown fences
        text = re.sub(r"^```[\w]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text).strip()
        log(f"  Ollama [{label}]: done {len(text)} chars in {time.time()-t0:.0f}s")
        return text
    except Exception as e:
        log(f"  Ollama [{label}] ERROR: {e}", "ERROR")
        return None

# ── Verify ────────────────────────────────────────────────────────────────────
def call_verify(code, instruction, context, filename, fix_id):
    payload = json.dumps({
        "code": code[:10000], "instruction": instruction,
        "context": context[:2000], "filename": filename,
        "phase_name": f"fix{fix_id}_v2"
    }).encode()
    try:
        req = urllib.request.Request(VERIFY_URL, data=payload,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read())
        passed = str(data.get("pass", "NO")).upper() == "YES"
        log(f"  Verify fix{fix_id}: {'PASS' if passed else 'FAIL'} "
            f"score={data.get('score',0)} — {data.get('issue','')[:80]}")
        return passed, data.get("issue", "")
    except Exception as e:
        log(f"  Verify offline: {e} — skipping")
        return None, str(e)

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
def extract_scripts(html):
    """Return list of (start_idx, end_idx, content) for all <script> blocks."""
    blocks = []
    for m in re.finditer(r"(<script(?:[^>]*)>)(.*?)(</script>)", html, re.DOTALL | re.IGNORECASE):
        blocks.append((m.start(), m.end(), m.group(1), m.group(2), m.group(3)))
    return blocks

def get_script_text(html):
    """Concatenate all inline script block contents."""
    blocks = extract_scripts(html)
    return "\n\n/* === SCRIPT BLOCK === */\n\n".join(b[3] for b in blocks if b[3].strip())

def replace_scripts(html, new_js):
    """Replace all existing <script> inline blocks with one combined block."""
    blocks = extract_scripts(html)
    if not blocks:
        return html + f"\n<script>\n{new_js}\n</script>"
    # Remove all existing inline script blocks (reverse order to preserve indices)
    result = html
    for start, end, open_tag, content, close_tag in reversed(blocks):
        # Only replace inline scripts (not src= scripts)
        if 'src=' not in open_tag:
            result = result[:start] + result[end:]
    # Insert combined script before </body>
    if "</body>" in result:
        result = result.replace("</body>", f"<script>\n{new_js}\n</script>\n</body>", 1)
    else:
        result += f"\n<script>\n{new_js}\n</script>"
    return result

def inject_before_head_close(html, css):
    tag = f"<style>\n{css}\n</style>"
    if "</head>" in html:
        return html.replace("</head>", tag + "\n</head>", 1)
    return html + tag

def inject_after_body_open(html, html_snippet):
    return re.sub(r"(<body[^>]*>)", r"\1\n" + html_snippet, html, count=1, flags=re.IGNORECASE)

def inject_before_body_close(html, js):
    tag = f"<script>\n{js}\n</script>"
    if "</body>" in html:
        return html.replace("</body>", tag + "\n</body>", 1)
    return html + "\n" + tag

# ── Prompt templates ──────────────────────────────────────────────────────────
INJECT_PROMPT = """\
Generate ONLY the new code to add to {pi_path}. Do NOT return the full file.

FIX SPEC:
{spec}

Return in EXACTLY this format — include all four section headers even if empty:
=== CSS ===
[css rules to add, or NONE]
=== HTML_AFTER_BODY ===
[html elements to insert right after <body> tag, or NONE]
=== JS_BEFORE_BODY_CLOSE ===
[javascript functions to add before </body>, or NONE]
=== JS_INLINE ===
[any immediate JS calls like checkSignalK(); setInterval(...), or NONE]
"""

PATCH_JS_PROMPT = """\
Fix the JavaScript below from {pi_path}. Apply ONLY the changes described in the spec.
Keep ALL existing functions intact. Only modify or add what the spec requires.

FIX SPEC:
{spec}

CURRENT JAVASCRIPT (all inline script blocks combined):
{scripts}

Return the complete corrected JavaScript only. No HTML tags. No markdown. No explanation.
"""

PATCH_FN_PROMPT = """\
Modify this Python code section from {pi_path} per the spec.
Apply ONLY the changes described. Keep everything else identical.

FIX SPEC:
{spec}

CODE SECTION:
{code}

Return only the corrected code section. No markdown, no explanation.
"""

# ── Parse INJECT response ─────────────────────────────────────────────────────
def parse_inject_response(text):
    sections = {"CSS": "", "HTML_AFTER_BODY": "", "JS_BEFORE_BODY_CLOSE": "", "JS_INLINE": ""}
    current = None
    lines = []
    for line in text.splitlines():
        m = re.match(r"^===\s*(CSS|HTML_AFTER_BODY|JS_BEFORE_BODY_CLOSE|JS_INLINE)\s*===", line)
        if m:
            if current and lines:
                val = "\n".join(lines).strip()
                sections[current] = "" if val.upper() == "NONE" else val
            current = m.group(1)
            lines = []
        elif current:
            lines.append(line)
    if current and lines:
        val = "\n".join(lines).strip()
        sections[current] = "" if val.upper() == "NONE" else val
    return sections

# ── Fix handlers ──────────────────────────────────────────────────────────────
def handle_inject(fix_id, spec, pi_path, description):
    """Generate only new code, inject into existing file."""
    log(f"  [Fix {fix_id}] INJECT strategy: {pi_path}")
    prompt = INJECT_PROMPT.format(spec=spec, pi_path=pi_path)
    result = call_ollama(prompt, f"fix{fix_id}-inject")
    if not result:
        return False, "ollama empty"

    (OUTPUT_DIR / f"fix{fix_id}_inject_{os.path.basename(pi_path)}.txt").write_text(result)
    parsed = parse_inject_response(result)
    log(f"  [Fix {fix_id}] Parsed: CSS={len(parsed['CSS'])}c "
        f"HTML={len(parsed['HTML_AFTER_BODY'])}c "
        f"JS={len(parsed['JS_BEFORE_BODY_CLOSE'])}c "
        f"inline={len(parsed['JS_INLINE'])}c")

    try:
        html = fetch_pi_file(pi_path)
        (OUTPUT_DIR / f"fix{fix_id}_orig_{os.path.basename(pi_path)}").write_text(html)

        if parsed["CSS"]:
            html = inject_before_head_close(html, parsed["CSS"])
        if parsed["HTML_AFTER_BODY"]:
            html = inject_after_body_open(html, parsed["HTML_AFTER_BODY"])
        js_combined = "\n\n".join(filter(None, [
            parsed["JS_BEFORE_BODY_CLOSE"],
            parsed["JS_INLINE"]
        ]))
        if js_combined:
            html = inject_before_body_close(html, js_combined)

        call_verify(result, description, "", os.path.basename(pi_path), fix_id)
        deploy_pi_file(pi_path, html)
        log(f"  [Fix {fix_id}] ✓ Injected into {pi_path}")
        return True, "deployed"
    except Exception as e:
        log(f"  [Fix {fix_id}] FAILED: {e}", "ERROR")
        return False, str(e)


def handle_patch_js(fix_id, spec, pi_path, description):
    """Extract script blocks, patch JS only, replace in file."""
    log(f"  [Fix {fix_id}] PATCH_JS strategy: {pi_path}")
    try:
        html = fetch_pi_file(pi_path)
        (OUTPUT_DIR / f"fix{fix_id}_orig_{os.path.basename(pi_path)}").write_text(html)
    except Exception as e:
        return False, f"fetch failed: {e}"

    scripts = get_script_text(html)
    if not scripts.strip():
        log(f"  [Fix {fix_id}] No inline scripts found — falling back to inject")
        return handle_inject(fix_id, spec, pi_path, description)

    log(f"  [Fix {fix_id}] Extracted {len(scripts)} chars of JS (vs {len(html)} HTML)")
    prompt = PATCH_JS_PROMPT.format(spec=spec, pi_path=pi_path, scripts=scripts)
    result = call_ollama(prompt, f"fix{fix_id}-patchjs")
    if not result:
        return False, "ollama empty"

    (OUTPUT_DIR / f"fix{fix_id}_patched_js_{os.path.basename(pi_path)}.js").write_text(result)

    # Verify the JS
    passed, feedback = call_verify(result, description, scripts[:2000],
                                   os.path.basename(pi_path), fix_id)
    if passed is False:
        log(f"  [Fix {fix_id}] Verify failed — correcting")
        corr_prompt = (f"Fix this JavaScript. Keep all existing functions.\n\n"
                       f"PROBLEM: {feedback}\n\nCODE:\n{result}\n\n"
                       f"Return only corrected JS. No explanation.")
        result2 = call_ollama(corr_prompt, f"fix{fix_id}-correction")
        if result2:
            result = result2

    try:
        new_html = replace_scripts(html, result)
        deploy_pi_file(pi_path, new_html)
        log(f"  [Fix {fix_id}] ✓ Patched JS in {pi_path}")
        return True, "deployed"
    except Exception as e:
        log(f"  [Fix {fix_id}] DEPLOY FAILED: {e}", "ERROR")
        return False, str(e)


def handle_patch_python_fn(fix_id, spec, pi_path, extract_pattern, description):
    """Extract a Python function/section by regex, patch it, replace in file."""
    log(f"  [Fix {fix_id}] PATCH_FN strategy: {pi_path}")
    try:
        content = fetch_pi_file(pi_path)
        (OUTPUT_DIR / f"fix{fix_id}_orig_{os.path.basename(pi_path)}").write_text(content)
    except Exception as e:
        return False, f"fetch failed: {e}"

    m = re.search(extract_pattern, content, re.DOTALL)
    if not m:
        log(f"  [Fix {fix_id}] Pattern not found — sending first 200 lines")
        code_section = "\n".join(content.splitlines()[:200])
        full_file = True
    else:
        code_section = m.group(0)
        full_file = False

    log(f"  [Fix {fix_id}] Extracted {len(code_section)} chars of Python")
    prompt = PATCH_FN_PROMPT.format(spec=spec, pi_path=pi_path, code=code_section)
    result = call_ollama(prompt, f"fix{fix_id}-patchfn")
    if not result:
        return False, "ollama empty"

    (OUTPUT_DIR / f"fix{fix_id}_patched_{os.path.basename(pi_path)}").write_text(result)
    call_verify(result, description, code_section[:2000], os.path.basename(pi_path), fix_id)

    try:
        if full_file:
            new_content = result
        else:
            new_content = content[:m.start()] + result + content[m.end():]
        deploy_pi_file(pi_path, new_content)
        log(f"  [Fix {fix_id}] ✓ Patched {pi_path}")
        return True, "deployed"
    except Exception as e:
        log(f"  [Fix {fix_id}] DEPLOY FAILED: {e}", "ERROR")
        return False, str(e)


# ── Main ──────────────────────────────────────────────────────────────────────
def run_v2():
    log("=" * 60)
    log("d3kOS Fix Executor v2 — surgical patch approach")
    log(f"Pi: {PI_HOST}  Ollama: {OLLAMA_URL}")
    log("Fixes: 1,2,4,5,6,7,8,9,10,13 (HTML timeouts + Flatpak + RAG)")
    log("=" * 60)

    spec = load_spec(SPEC_FILE)
    results = {}
    t_start = time.time()

    # ── Fix 13: settings.html JS (Settings Actions) ───────────────────────────
    log("\n── Fix 13: settings.html — replace alert() actions with fetch() ──")
    ok, msg = handle_patch_js(13, spec.get(13, ""),
        "/var/www/html/settings.html",
        "Replace restartSignalK(), restartNodered(), rebootSystem() and any similar action functions "
        "that currently use alert() or show SSH instructions — replace with fetch() calls to "
        "/settings/action/restart-signalk, /settings/action/restart-nodered, /settings/action/reboot. "
        "Add showToast(msg) helper if not already present.")
    results[13] = {"settings_html": (ok, msg)}

    # ── Fix 1: dashboard.html — SignalK disconnected banner ───────────────────
    log("\n── Fix 1: dashboard.html — SignalK disconnected banner ──")
    ok, msg = handle_inject(1, spec.get(1, ""),
        "/var/www/html/dashboard.html",
        "Add yellow sticky banner that appears when SignalK offline, disappears when recovered, "
        "with link to Settings. Polls /signalk/v1/api/ every 5 seconds.")
    results[1] = {"dashboard_html": (ok, msg)}

    # ── Fix 2: benchmark.html — investigate and fix ───────────────────────────
    log("\n── Fix 2: benchmark.html — diagnose broken API calls ──")
    # Gather context about running services to help Ollama diagnose
    svc_list, _ = ssh_run("systemctl list-units 'd3kos-*' --no-pager --no-legend 2>/dev/null")
    ports, _ = ssh_run("ss -tlnp 2>/dev/null | grep -E '808|809|810'")
    diag_spec = spec.get(2, "") + f"\n\n=== RUNNING SERVICES ===\n{svc_list}\n\n=== LISTENING PORTS ===\n{ports}"
    ok, msg = handle_patch_js(2, diag_spec,
        "/var/www/html/benchmark.html",
        "Diagnose and fix broken Engine Benchmark API calls; fix endpoint URLs to match running services; "
        "add graceful 'Service offline' display if API unreachable")
    results[2] = {"benchmark_html": (ok, msg)}

    # ── Fix 4: navigation.html — GPS SignalK paths ────────────────────────────
    log("\n── Fix 4: navigation.html — fix GPS SignalK fetch paths ──")
    ok, msg = handle_patch_js(4, spec.get(4, ""),
        "/var/www/html/navigation.html",
        "Fix GPS fetch URLs to use correct SignalK paths: navigation/position (.value.latitude/.value.longitude), "
        "navigation/speedOverGround (m/s × 1.944 = knots), navigation/headingTrue (rad × 180/π = degrees), "
        "navigation/courseOverGroundTrue (rad × 180/π). Show '--' when no GPS fix instead of blank.")
    results[4] = {"navigation_html": (ok, msg)}

    # ── Fix 5: boatlog.html — voice note mic button ───────────────────────────
    log("\n── Fix 5: boatlog.html — add voice note mic button ──")
    ok, msg = handle_inject(5, spec.get(5, ""),
        "/var/www/html/boatlog.html",
        "Add microphone button (🎤) near the notes field; MediaRecorder JS to start/stop recording; "
        "POST audio blob to /boatlog/voice-note; append transcript or saved confirmation to notes textarea.")
    results[5] = {"boatlog_html": (ok, msg)}

    # ── Fix 6: weather.html — GPS centering + overlay fix ─────────────────────
    log("\n── Fix 6: weather.html — GPS centering and overlay fix ──")
    ok, msg = handle_patch_js(6, spec.get(6, ""),
        "/var/www/html/weather.html",
        "Replace hardcoded Lake Simcoe position with async GPS fetch from "
        "/signalk/v1/api/vessels/self/navigation/position before map init; "
        "fix OpenWeatherMap tile layer URLs to use wind_new and clouds_new layer names; "
        "show overlay error notice if API key missing.")
    results[6] = {"weather_html": (ok, msg)}

    # ── Fix 7: marine-vision.html — camera offline placeholder ───────────────
    log("\n── Fix 7: marine-vision.html — camera offline placeholder ──")
    ok, msg = handle_inject(7, spec.get(7, ""),
        "/var/www/html/marine-vision.html",
        "Add img.onerror handlers showing dark placeholder div with camera name and "
        "'Offline — Connect to boat network' message; add .camera-offline-placeholder CSS class.")
    results[7] = {"marine_vision_html": (ok, msg)}

    # camera_stream_manager.py — offline status field
    log("\n── Fix 7b: camera_stream_manager.py ──")
    ok2, msg2 = handle_patch_python_fn(7, spec.get(7, ""),
        "/opt/d3kos/services/marine-vision/camera_stream_manager.py",
        r"def (?:get_camera_status|get_cameras|camera_status|check_cameras|build_camera)[^\n]*\n(?:(?!^def ).*\n)*",
        "Add 'status': 'online'/'offline' key to each camera dict; "
        "wrap connection attempt in try/except, set status='offline' on exception")
    results[7]["camera_stream_manager"] = (ok2, msg2)

    # ── Fix 9: onboarding.html — Gemini wizard step ───────────────────────────
    log("\n── Fix 9: onboarding.html — add Gemini API step ──")
    # Extract wizard step structure (just the step headings) to understand numbering
    try:
        onboarding = fetch_pi_file("/var/www/html/onboarding.html")
        step_divs = re.findall(r'<div[^>]+id=["\']step-(\d+)["\'][^>]*>.*?<h[12][^>]*>(.*?)</h[12]>',
                               onboarding, re.DOTALL)
        step_summary = "\n".join(f"Step {n}: {h.strip()}" for n, h in step_divs)
        log(f"  [Fix 9] Found {len(step_divs)} wizard steps: {step_summary[:200]}")
        inject_spec = spec.get(9, "") + f"\n\n=== EXISTING WIZARD STEPS ===\n{step_summary}"
    except Exception:
        inject_spec = spec.get(9, "")

    ok, msg = handle_inject(9, inject_spec,
        "/var/www/html/onboarding.html",
        "Add new Gemini API key wizard step before the final completion screen; "
        "include password input, Test Connection button calling /gemini/test, "
        "Save & Continue button calling /gemini/config, and Skip option.")
    results[9] = {"onboarding_html": (ok, msg)}

    # ── Fix 10: query_handler.py — RAG precision ─────────────────────────────
    log("\n── Fix 10: query_handler.py — RAG precision ──")
    # Extract only the RAG query section (search for n_results or query_rag function)
    ok, msg = handle_patch_python_fn(10, spec.get(10, ""),
        "/opt/d3kos/services/ai/query_handler.py",
        r"(?:n_results\s*=\s*\d+|def (?:query_rag|_query_rag|rag_query|query)[^\n]*\n)(?:(?!^def ).*\n){0,80}",
        "Increase n_results from 4 to 6; filter results where distance >= 0.40; "
        "prepend [Source: filename] to each context chunk in the RAG prompt")
    results[10] = {"query_handler": (ok, msg)}

    # ── Fix 8: OpenCPN Flatpak (sudo) ─────────────────────────────────────────
    log("\n── Fix 8: OpenCPN Flatpak (sudo install) ──")
    r8 = {}
    try:
        flatpak_check, _ = ssh_run("flatpak list 2>/dev/null | grep -i opencpn")
        if flatpak_check:
            log("  [Fix 8] Already installed")
            r8["status"] = (True, "already installed")
        else:
            ssh_run("cp -r ~/.opencpn ~/.opencpn.backup.$(date +%Y%m%d) 2>/dev/null || true")

            log("  [Fix 8] Installing flatpak if needed...")
            _, rc = ssh_run("sudo apt-get install -y flatpak 2>&1", timeout=120)
            log(f"  [Fix 8] apt flatpak: rc={rc}")

            log("  [Fix 8] Adding Flathub...")
            _, rc = ssh_run("sudo flatpak remote-add --if-not-exists flathub "
                            "https://flathub.org/repo/flathub.flatpakrepo 2>&1", timeout=60)
            log(f"  [Fix 8] Flathub: rc={rc}")

            log("  [Fix 8] Removing native OpenCPN...")
            ssh_run("sudo apt-get remove -y opencpn 2>&1", timeout=60)

            log("  [Fix 8] Installing OpenCPN Flatpak with sudo (ARM64 download — slow)...")
            out, rc = ssh_run("sudo flatpak install -y --system flathub org.opencpn.OpenCPN 2>&1",
                              timeout=900)
            log(f"  [Fix 8] Install: rc={rc} tail={out[-200:] if out else ''}")

            if rc == 0:
                ssh_run("mkdir -p ~/.var/app/org.opencpn.OpenCPN/config/opencpn/")
                ssh_run("cp ~/.opencpn/opencpn.conf "
                        "~/.var/app/org.opencpn.OpenCPN/config/opencpn/ 2>/dev/null || true")
                r8["status"] = (True, "installed + config migrated")
                log("  [Fix 8] ✓ OpenCPN Flatpak installed")
            else:
                r8["status"] = (False, f"install failed rc={rc}: {out[-300:]}")

        # Update index.html launcher
        try:
            idx = fetch_pi_file("/var/www/html/index.html")
            updated = idx.replace("'opencpn'", "'flatpak run org.opencpn.OpenCPN'")
            updated = updated.replace('"opencpn"', '"flatpak run org.opencpn.OpenCPN"')
            if updated != idx:
                deploy_pi_file("/var/www/html/index.html", updated)
                log("  [Fix 8] ✓ index.html launcher updated")
                r8["launcher"] = (True, "updated")
        except Exception as e:
            log(f"  [Fix 8] Launcher: {e}", "WARN")

    except Exception as e:
        log(f"  [Fix 8] Error: {e}", "ERROR")
        r8["error"] = (False, str(e))
    results[8] = r8

    # ── Report ────────────────────────────────────────────────────────────────
    elapsed = int(time.time() - t_start)
    passed, failed = [], []
    for fid, fdata in sorted(results.items()):
        ok_all = all(v[0] for v in fdata.values() if isinstance(v, tuple))
        (passed if ok_all else failed).append(fid)

    report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "elapsed_seconds": elapsed,
        "model": MODEL,
        "strategy": "inject+patch_js — never sends full HTML file",
        "passed": passed,
        "failed": failed,
        "details": {
            str(k): {kk: list(vv) for kk, vv in v.items() if isinstance(vv, tuple)}
            for k, v in results.items()
        }
    }
    REPORT_FILE.write_text(json.dumps(report, indent=2))

    log("\n" + "=" * 60)
    log(f"COMPLETE — {len(passed)} passed, {len(failed)} failed in {elapsed}s")
    log(f"Passed: {passed}")
    log(f"Failed: {failed}")
    log(f"Report: {REPORT_FILE}")
    log("=" * 60)


if __name__ == "__main__":
    try:
        run_v2()
    except KeyboardInterrupt:
        log("Interrupted", "WARN")
    except Exception as e:
        log(f"Fatal: {e}\n{traceback.format_exc()}", "ERROR")
        sys.exit(1)
