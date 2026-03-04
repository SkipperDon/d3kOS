#!/usr/bin/env python3
"""
d3kOS Post-Install Fix Executor
Implements 13 fixes from OLLAMA_SPEC.md using Ollama + verify agent.
Runs fully autonomously. No monitoring required.

Usage:
  nohup python3 ollama_execute_fixes.py > /tmp/d3kos_fixes.log 2>&1 &

Output:
  /tmp/d3kos_fixes.log          — live log
  ollama_output/fixes/          — saved outputs per fix
  ollama_output/fixes_report.json — final report
"""

import json, time, sys, os, re, subprocess, tempfile, pathlib, datetime
import urllib.request, urllib.error, traceback, threading

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
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR.parent / "ollama_output" / "fixes"
REPORT_FILE = SCRIPT_DIR.parent / "ollama_output" / "fixes_report.json"
LOG_FILE   = pathlib.Path("/tmp/d3kos_fixes.log")

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

# ── SSH/SCP ───────────────────────────────────────────────────────────────────
def ssh_run(cmd, timeout=90):
    full = ["ssh"] + SSH_OPTS + [f"{PI_USER}@{PI_HOST}", cmd]
    r = subprocess.run(full, capture_output=True, text=True, timeout=timeout)
    return r.stdout.strip(), r.returncode

def fetch_pi_file(pi_path):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as f:
        tmp = f.name
    try:
        subprocess.run(
            ["scp"] + SSH_OPTS + [f"{PI_USER}@{PI_HOST}:{pi_path}", tmp],
            check=True, capture_output=True, timeout=30
        )
        with open(tmp, "r", errors="replace") as f:
            return f.read()
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)

def deploy_pi_file(pi_path, content, sudo=False, mode="644"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp", mode="w", encoding="utf-8") as f:
        f.write(content)
        tmp_local = f.name
    tmp_remote = f"/tmp/d3kfix_{os.path.basename(pi_path)}"
    try:
        subprocess.run(
            ["scp"] + SSH_OPTS + [tmp_local, f"{PI_USER}@{PI_HOST}:{tmp_remote}"],
            check=True, capture_output=True, timeout=30
        )
        if sudo:
            pi_dir = os.path.dirname(pi_path)
            ssh_run(f"sudo mkdir -p {pi_dir} && sudo mv {tmp_remote} {pi_path} && sudo chmod {mode} {pi_path}")
        else:
            ssh_run(f"mv {tmp_remote} {pi_path} && chmod {mode} {pi_path}")
    finally:
        if os.path.exists(tmp_local):
            os.unlink(tmp_local)

# ── Ollama ────────────────────────────────────────────────────────────────────
def call_ollama(prompt, fix_id, label=""):
    payload = json.dumps({
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.05, "num_predict": 16384, "num_ctx": 32768}
    }).encode()
    log(f"  [Fix {fix_id}] Ollama{' '+label if label else ''}: {len(prompt)} chars → sending...")
    t0 = time.time()
    try:
        req = urllib.request.Request(
            OLLAMA_URL, data=payload,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=600) as resp:
            data = json.loads(resp.read())
        text = data.get("response", "").strip()
        text = re.sub(r"^```[\w]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text).strip()
        log(f"  [Fix {fix_id}] Ollama done: {len(text)} chars in {time.time()-t0:.0f}s")
        return text
    except Exception as e:
        log(f"  [Fix {fix_id}] Ollama ERROR: {e}", "ERROR")
        return None

# ── Verify agent ──────────────────────────────────────────────────────────────
def call_verify(code, instruction, context, filename, fix_id):
    payload = json.dumps({
        "code": code[:10000],
        "instruction": instruction,
        "context": context[:3000],
        "filename": filename,
        "phase_name": f"fix_{fix_id}"
    }).encode()
    try:
        req = urllib.request.Request(
            VERIFY_URL, data=payload,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read())
        passed = str(data.get("pass", "NO")).upper() == "YES"
        score  = data.get("score", 0)
        issue  = data.get("issue", "none")
        log(f"  [Fix {fix_id}] Verify: {'PASS' if passed else 'FAIL'} score={score} — {issue[:80]}")
        return passed, issue
    except Exception as e:
        log(f"  [Fix {fix_id}] Verify agent offline/error: {e} — continuing (non-blocking)")
        return None, str(e)

# ── Spec parser ───────────────────────────────────────────────────────────────
def load_spec(spec_path):
    text = spec_path.read_text()
    sections = {}
    parts = re.split(r"(?=\n## Fix \d+)", text)
    for part in parts:
        m = re.match(r"\n?## Fix (\d+)", part)
        if m:
            sections[int(m.group(1))] = part.strip()
    return sections

# ── Prompt templates ──────────────────────────────────────────────────────────
MODIFY_PROMPT = """\
You are modifying a file for d3kOS — a marine intelligence OS on Raspberry Pi 4B \
(Debian Trixie, Wayland/labwc, touchscreen UI, dark theme).

TASK: Apply exactly the fix described in the specification to the current file.

=== FIX SPECIFICATION ===
{spec}

=== CURRENT FILE: {pi_path} ===
{content}

=== RULES ===
- Apply ONLY the changes described. Do not change anything else.
- Return the COMPLETE modified file — every single line.
- NO markdown fences (```). NO explanation. Just the raw file content.
- CSS: add inside existing <style> block or create <style> in <head>
- JS: add before </body> or inside existing <script> block
- Keep ALL existing functionality intact
"""

CREATE_PROMPT = """\
You are creating a new file for d3kOS — a marine intelligence OS on Raspberry Pi 4B \
(Debian Trixie, Python 3.11, Flask services, systemd).

TASK: Create the file {pi_path} according to the specification below.

=== SPECIFICATION ===
{spec}

=== RULES ===
- Return ONLY the complete file content. No markdown fences, no explanation.
- Python services: Flask, 127.0.0.1, port as specified, compatible with User=d3kos
- Systemd: User=d3kos, Restart=on-failure, WantedBy=multi-user.target
- Sudoers: NOPASSWD for specific commands only, never ALL=(ALL) ALL
"""

CORRECTION_PROMPT = """\
The code you generated has a problem. Fix it and return the corrected version.

ORIGINAL TASK:
{instruction}

YOUR CODE:
{code}

REVIEWER FEEDBACK:
{feedback}

Return ONLY the corrected file content. No markdown fences, no explanation.
"""

# ── Core handlers ─────────────────────────────────────────────────────────────
def handle_modify(fix_id, spec, pi_path, description, sudo=False):
    log(f"  [Fix {fix_id}] Fetching {pi_path}")
    try:
        content = fetch_pi_file(pi_path)
    except Exception as e:
        log(f"  [Fix {fix_id}] FETCH FAILED {pi_path}: {e}", "ERROR")
        return False, f"fetch failed: {e}"

    (OUTPUT_DIR / f"fix{fix_id}_orig_{os.path.basename(pi_path)}").write_text(content)

    result = call_ollama(
        MODIFY_PROMPT.format(spec=spec, pi_path=pi_path, content=content),
        fix_id, label=os.path.basename(pi_path)
    )
    if not result:
        return False, "ollama returned empty"

    (OUTPUT_DIR / f"fix{fix_id}_out_{os.path.basename(pi_path)}").write_text(result)

    passed, feedback = call_verify(result, description, content[:2000],
                                   os.path.basename(pi_path), fix_id)
    if passed is False:
        log(f"  [Fix {fix_id}] Verify failed — attempting correction")
        result2 = call_ollama(
            CORRECTION_PROMPT.format(instruction=description, code=result, feedback=feedback),
            fix_id, label="correction"
        )
        if result2:
            result = result2
            (OUTPUT_DIR / f"fix{fix_id}_corrected_{os.path.basename(pi_path)}").write_text(result)

    try:
        deploy_pi_file(pi_path, result, sudo=sudo)
        log(f"  [Fix {fix_id}] ✓ Deployed {pi_path}")
        return True, "deployed"
    except Exception as e:
        log(f"  [Fix {fix_id}] DEPLOY FAILED {pi_path}: {e}", "ERROR")
        return False, f"deploy failed: {e}"


def handle_create(fix_id, spec, pi_path, description, sudo=False, mode="644"):
    log(f"  [Fix {fix_id}] Creating {pi_path}")
    result = call_ollama(
        CREATE_PROMPT.format(spec=spec, pi_path=pi_path),
        fix_id, label=f"create {os.path.basename(pi_path)}"
    )
    if not result:
        return False, "ollama returned empty"

    (OUTPUT_DIR / f"fix{fix_id}_new_{os.path.basename(pi_path)}").write_text(result)

    passed, feedback = call_verify(result, description, "", os.path.basename(pi_path), fix_id)
    if passed is False:
        log(f"  [Fix {fix_id}] Verify failed — attempting correction")
        result2 = call_ollama(
            CORRECTION_PROMPT.format(instruction=description, code=result, feedback=feedback),
            fix_id, label="correction"
        )
        if result2:
            result = result2

    try:
        deploy_pi_file(pi_path, result, sudo=sudo, mode=mode)
        log(f"  [Fix {fix_id}] ✓ Created {pi_path}")
        return True, "deployed"
    except Exception as e:
        log(f"  [Fix {fix_id}] DEPLOY FAILED {pi_path}: {e}", "ERROR")
        return False, f"deploy failed: {e}"


def inject_css(fix_id, html_files, css_block):
    css_marker = "d3kos-scrollbar-fix"
    css_tag = f'\n<style id="{css_marker}">\n{css_block}\n</style>'
    ok_count = 0
    for pi_path in html_files:
        try:
            content = fetch_pi_file(pi_path)
            if css_marker in content:
                log(f"  [Fix {fix_id}] Already patched: {pi_path}")
                ok_count += 1
                continue
            if "</head>" in content:
                modified = content.replace("</head>", css_tag + "\n</head>", 1)
            else:
                modified = content + css_tag
            deploy_pi_file(pi_path, modified)
            log(f"  [Fix {fix_id}] ✓ Scrollbar CSS → {pi_path}")
            ok_count += 1
        except Exception as e:
            log(f"  [Fix {fix_id}] FAILED {pi_path}: {e}", "ERROR")
    return ok_count, len(html_files)


# ── Fix implementations ───────────────────────────────────────────────────────
def run_all_fixes():
    log("=" * 60)
    log("d3kOS Post-Install Fix Executor")
    log(f"Pi: {PI_HOST}  Ollama: {OLLAMA_URL}  Verify: {VERIFY_URL}")
    log(f"Spec: {SPEC_FILE}")
    log("=" * 60)

    spec = load_spec(SPEC_FILE)
    results = {}
    t_start = time.time()

    # ── Fix 13: Settings Action API ───────────────────────────────────────────
    log("\n── Fix 13: Settings System Actions API ──")
    r = {}

    ok, msg = handle_create(13, spec.get(13, ""),
        "/opt/d3kos/services/settings-api.py",
        "Flask API on port 8101: POST /settings/action/restart-signalk, restart-nodered, reboot. "
        "Each action runs allowed sudo command and returns JSON {success, message}.",
        sudo=False, mode="755")
    r["settings_api_py"] = (ok, msg)

    ok, msg = handle_create(13, spec.get(13, ""),
        "/etc/systemd/system/d3kos-settings-api.service",
        "systemd service for /opt/d3kos/services/settings-api.py, User=d3kos, port 8101",
        sudo=True, mode="644")
    r["service_file"] = (ok, msg)

    ok, msg = handle_create(13, spec.get(13, ""),
        "/etc/sudoers.d/d3kos-settings-api",
        "sudoers file: d3kos NOPASSWD for systemctl restart signalk, systemctl restart nodered, /usr/sbin/reboot",
        sudo=True, mode="440")
    r["sudoers"] = (ok, msg)

    # Nginx proxy block
    try:
        nginx = fetch_pi_file("/etc/nginx/sites-enabled/default")
        if "/settings/action/" not in nginx:
            block = ('\n    location /settings/action/ {\n'
                     '        proxy_pass http://127.0.0.1:8101;\n'
                     '        proxy_set_header Host $host;\n'
                     '    }\n')
            # Insert before last closing brace of outermost server block
            idx = nginx.rfind("}")
            if idx != -1:
                nginx = nginx[:idx] + block + nginx[idx:]
            deploy_pi_file("/etc/nginx/sites-enabled/default", nginx, sudo=True)
            log("  [Fix 13] ✓ Nginx proxy block added")
            r["nginx"] = (True, "added")
        else:
            log("  [Fix 13] Nginx proxy already present")
            r["nginx"] = (True, "already present")
    except Exception as e:
        log(f"  [Fix 13] Nginx: {e}", "ERROR")
        r["nginx"] = (False, str(e))

    # settings.html — replace alert-based JS with fetch calls
    ok, msg = handle_modify(13, spec.get(13, ""),
        "/var/www/html/settings.html",
        "Replace alert()-based system action buttons with fetch() calls to /settings/action/ API; "
        "add showToast() helper if not present; restart-signalk, restart-nodered, reboot, initial-setup-reset")
    r["settings_html"] = (ok, msg)

    # Post-deploy commands
    cmds = [
        "sudo systemctl daemon-reload",
        "sudo systemctl enable d3kos-settings-api",
        "sudo systemctl start d3kos-settings-api",
        "sudo nginx -t && sudo systemctl reload nginx",
    ]
    for cmd in cmds:
        out, rc = ssh_run(cmd)
        log(f"  [Fix 13] {cmd}: rc={rc}" + (f" {out[:60]}" if out else ""))
    results[13] = r

    # ── Fix 3: Export race condition ──────────────────────────────────────────
    log("\n── Fix 3: Export Race Condition ──")
    r = {}
    ok, msg = handle_modify(3, spec.get(3, ""),
        "/opt/d3kos/scripts/export-daily.sh",
        "Add wait_for_api() bash function that retries curl to localhost:8093 up to 10 times "
        "(3s sleep between attempts) before proceeding; exit 0 gracefully if still not available")
    r["export_daily_sh"] = (ok, msg)

    # Add After= ordering to export-daily systemd service
    try:
        svc_path = "/etc/systemd/system/d3kos-export-daily.service"
        svc = fetch_pi_file(svc_path)
        if "d3kos-tier-api" not in svc:
            if "After=network-online.target" in svc:
                svc = svc.replace(
                    "After=network-online.target",
                    "After=network-online.target d3kos-export-manager.service d3kos-tier-api.service"
                )
            elif "[Unit]" in svc:
                svc = svc.replace(
                    "[Unit]",
                    "[Unit]\nAfter=network-online.target d3kos-export-manager.service d3kos-tier-api.service"
                )
            deploy_pi_file(svc_path, svc, sudo=True)
            ssh_run("sudo systemctl daemon-reload")
            log("  [Fix 3] ✓ Service After= ordering updated")
            r["service_ordering"] = (True, "updated")
        else:
            r["service_ordering"] = (True, "already correct")
    except Exception as e:
        log(f"  [Fix 3] Service ordering: {e}", "WARN")
        r["service_ordering"] = (False, str(e))
    results[3] = r

    # ── Fix 1: Dashboard SignalK banner ───────────────────────────────────────
    log("\n── Fix 1: Dashboard SignalK Disconnected Banner ──")
    ok, msg = handle_modify(1, spec.get(1, ""),
        "/var/www/html/dashboard.html",
        "Add yellow sticky banner that shows when SignalK is offline (polls /signalk/v1/api/ every 5s); "
        "banner disappears when SignalK recovers; includes link to Settings page")
    results[1] = {"dashboard_html": (ok, msg)}

    # ── Fix 2: Engine Benchmark ───────────────────────────────────────────────
    log("\n── Fix 2: Engine Benchmark Diagnose and Fix ──")
    try:
        bench = fetch_pi_file("/var/www/html/benchmark.html")
        svc_list, _ = ssh_run("systemctl list-units 'd3kos-*' --no-pager --no-legend 2>/dev/null | head -30")
        port_check, _ = ssh_run("ss -tlnp | grep -E '808[0-9]|809[0-9]' 2>/dev/null")
        extra = f"\n\n=== RUNNING d3kOS SERVICES ===\n{svc_list}\n\n=== LISTENING PORTS ===\n{port_check}"
        ok, msg = handle_modify(2, spec.get(2, "") + extra,
            "/var/www/html/benchmark.html",
            "Diagnose broken Engine Benchmark page: fix API endpoint URLs, ensure correct port, "
            "add error handling, display 'Service offline' if API unreachable")
        results[2] = {"benchmark_html": (ok, msg)}
    except Exception as e:
        log(f"  [Fix 2] Error: {e}", "ERROR")
        results[2] = {"error": (False, str(e))}

    # ── Fix 4: Navigation GPS readings ───────────────────────────────────────
    log("\n── Fix 4: Navigation GPS Readings ──")
    ok, msg = handle_modify(4, spec.get(4, ""),
        "/var/www/html/navigation.html",
        "Fix GPS field display: verify fetch URLs use correct SignalK paths "
        "(navigation/position, speedOverGround, headingTrue, courseOverGroundTrue); "
        "convert radians to degrees and m/s to knots; show '--' placeholder when no GPS fix")
    results[4] = {"navigation_html": (ok, msg)}

    # ── Fix 6: Weather GPS centering ─────────────────────────────────────────
    log("\n── Fix 6: Weather GPS Centering ──")
    ok, msg = handle_modify(6, spec.get(6, ""),
        "/var/www/html/weather.html",
        "Replace hardcoded Lake Simcoe lat/lon with async fetch from SignalK navigation/position "
        "before map initialisation; use fetched position as map center; fallback to Lake Simcoe if GPS unavailable; "
        "fix OpenWeatherMap tile URL format for wind_new and clouds_new layers")
    results[6] = {"weather_html": (ok, msg)}

    # ── Fix 7: Marine Vision offline handling ────────────────────────────────
    log("\n── Fix 7: Marine Vision Graceful Offline ──")
    ok, msg = handle_modify(7, spec.get(7, ""),
        "/var/www/html/marine-vision.html",
        "Add img.onerror handlers to camera feed images showing dark placeholder div with "
        "'Offline — Connect to boat network' message; add camera-offline-placeholder CSS class")
    results[7] = {"marine_vision_html": (ok, msg)}

    # Backend service files
    for svc_path in [
        "/opt/d3kos/services/marine-vision/camera_stream_manager.py",
        "/opt/d3kos/services/marine-vision/fish_detector.py",
    ]:
        out, rc = ssh_run(f"test -f {svc_path} && echo exists")
        if "exists" in out:
            ok2, msg2 = handle_modify(7, spec.get(7, ""), svc_path,
                "Wrap camera frame access in try/except; return offline status dict on exception; "
                "add 'status' key to camera dict ('online'/'offline')")
            results[7][os.path.basename(svc_path)] = (ok2, msg2)

    # ── Fix 5: Boatlog voice note ─────────────────────────────────────────────
    log("\n── Fix 5: Boatlog Voice Note ──")
    ok, msg = handle_modify(5, spec.get(5, ""),
        "/var/www/html/boatlog.html",
        "Add microphone button (🎤) to boatlog entry form; implement MediaRecorder JS to record audio; "
        "POST blob to /boatlog/voice-note endpoint; append transcript or filename to notes field on completion")
    results[5] = {"boatlog_html": (ok, msg)}

    # Backend — add voice note endpoint to boatlog API
    try:
        svc_out, _ = ssh_run("find /opt/d3kos/services/boatlog -name '*.py' 2>/dev/null | head -3")
        boatlog_py = None
        for line in svc_out.split("\n"):
            line = line.strip()
            if line.endswith(".py"):
                boatlog_py = line
                break
        if boatlog_py:
            ok2, msg2 = handle_modify(5, spec.get(5, ""), boatlog_py,
                "Add POST /boatlog/voice-note endpoint: save uploaded audio file to "
                "/opt/d3kos/data/boatlog-audio/; return {success, filename, transcript, timestamp}; "
                "attempt Vosk transcription if available, return empty transcript otherwise")
            results[5]["boatlog_api"] = (ok2, msg2)
        else:
            log("  [Fix 5] Boatlog API .py not found — skipping backend", "WARN")
            results[5]["boatlog_api"] = (False, "not found")
    except Exception as e:
        log(f"  [Fix 5] Backend: {e}", "WARN")

    # ── Fix 9: Wizard Gemini step ─────────────────────────────────────────────
    log("\n── Fix 9: Wizard Gemini API Step ──")
    ok, msg = handle_modify(9, spec.get(9, ""),
        "/var/www/html/onboarding.html",
        "Add new wizard step 'AI Assistant Setup' before the final completion screen; "
        "include password input for Gemini API key, Test Connection button (calls /gemini/test), "
        "Save & Continue button (calls /gemini/config), and Skip option")
    results[9] = {"onboarding_html": (ok, msg)}

    # ── Fix 12: Settings section header formatting (mechanical) ───────────────
    log("\n── Fix 12: Settings Section Header Formatting ──")
    try:
        content = fetch_pi_file("/var/www/html/settings.html")
        def add_class(m):
            tag = m.group(0)
            if "section-header" not in tag:
                if 'class="' in tag:
                    return tag.replace('class="', 'class="section-header ', 1)
                else:
                    return tag.replace("<h2", '<h2 class="section-header"', 1)
            return tag
        modified = re.sub(r"<h2(?:\s[^>]*)?>", add_class, content)
        if modified != content:
            deploy_pi_file("/var/www/html/settings.html", modified)
            log("  [Fix 12] ✓ Section headers updated")
            results[12] = {"settings_html": (True, "mechanical fix applied")}
        else:
            log("  [Fix 12] All h2 already correct")
            results[12] = {"settings_html": (True, "no changes needed")}
    except Exception as e:
        log(f"  [Fix 12] Error: {e}", "ERROR")
        results[12] = {"error": (False, str(e))}

    # ── Fix 10: RAG precision ─────────────────────────────────────────────────
    log("\n── Fix 10: AI RAG Precision ──")
    qh_path = "/opt/d3kos/services/ai/query_handler.py"
    out, rc = ssh_run(f"test -f {qh_path} && echo exists")
    if "exists" in out:
        ok, msg = handle_modify(10, spec.get(10, ""), qh_path,
            "Increase RAG n_results from 4 to 6; filter results by distance < 0.40; "
            "include source filename in context passed to LLM prompt")
        results[10] = {"query_handler": (ok, msg)}
    else:
        log(f"  [Fix 10] {qh_path} not found", "WARN")
        results[10] = {"query_handler": (False, "file not found on Pi")}

    # ── Fix 8: OpenCPN Flatpak migration ─────────────────────────────────────
    log("\n── Fix 8: OpenCPN Flatpak Migration ──")
    r = {}
    try:
        flatpak_check, _ = ssh_run("flatpak list 2>/dev/null | grep -i opencpn")
        if flatpak_check:
            log("  [Fix 8] OpenCPN Flatpak already installed")
            r["status"] = (True, "already installed")
        else:
            log("  [Fix 8] Backing up config...")
            ssh_run("cp -r ~/.opencpn ~/.opencpn.backup.$(date +%Y%m%d) 2>/dev/null || true")

            log("  [Fix 8] Installing flatpak package...")
            _, rc = ssh_run("sudo apt-get install -y flatpak 2>&1", timeout=120)
            log(f"  [Fix 8] apt install flatpak: rc={rc}")

            log("  [Fix 8] Adding Flathub repository...")
            _, rc = ssh_run("sudo flatpak remote-add --if-not-exists flathub "
                            "https://flathub.org/repo/flathub.flatpakrepo 2>&1", timeout=60)
            log(f"  [Fix 8] Flathub add: rc={rc}")

            log("  [Fix 8] Removing native OpenCPN...")
            _, rc = ssh_run("sudo apt-get remove -y opencpn 2>&1", timeout=60)
            log(f"  [Fix 8] Remove native: rc={rc}")

            log("  [Fix 8] Installing OpenCPN via Flatpak (slow — ARM64 download)...")
            out, rc = ssh_run("flatpak install -y flathub org.opencpn.OpenCPN 2>&1", timeout=900)
            log(f"  [Fix 8] Flatpak install: rc={rc} tail={out[-150:] if out else ''}")

            if rc == 0:
                ssh_run("mkdir -p ~/.var/app/org.opencpn.OpenCPN/config/opencpn/")
                ssh_run("cp ~/.opencpn/opencpn.conf "
                        "~/.var/app/org.opencpn.OpenCPN/config/opencpn/ 2>/dev/null || true")
                r["status"] = (True, "installed + config migrated")
                log("  [Fix 8] ✓ OpenCPN Flatpak installed")
            else:
                r["status"] = (False, f"flatpak install rc={rc}")

        # Update index.html launcher
        try:
            idx_content = fetch_pi_file("/var/www/html/index.html")
            if "'opencpn'" in idx_content or '"opencpn"' in idx_content:
                updated = idx_content.replace("'opencpn'", "'flatpak run org.opencpn.OpenCPN'")
                updated = updated.replace('"opencpn"', '"flatpak run org.opencpn.OpenCPN"')
                if updated != idx_content:
                    deploy_pi_file("/var/www/html/index.html", updated)
                    log("  [Fix 8] ✓ index.html launcher updated")
                    r["launcher"] = (True, "updated")
        except Exception as e:
            log(f"  [Fix 8] Launcher update: {e}", "WARN")

    except Exception as e:
        log(f"  [Fix 8] Error: {e}", "ERROR")
        r["error"] = (False, str(e))
    results[8] = r

    # ── Fix 14: Touch-friendly scrollbars ────────────────────────────────────
    log("\n── Fix 14: Touch-Friendly Scrollbars (all pages) ──")
    scrollbar_css = (
        "/* d3kOS touch-friendly scrollbars — 56px width for finger-grab on touchscreen */\n"
        "::-webkit-scrollbar { width: 56px; height: 56px; }\n"
        "::-webkit-scrollbar-track { background: #1a1a1a; border-radius: 8px; }\n"
        "::-webkit-scrollbar-thumb { background: #555; border-radius: 8px; min-height: 80px; }\n"
        "::-webkit-scrollbar-thumb:active { background: #FFD700; }\n"
        "* { scrollbar-width: thick; scrollbar-color: #555 #1a1a1a; }"
    )
    html_list, _ = ssh_run("ls /var/www/html/*.html 2>/dev/null")
    html_files = [p.strip() for p in html_list.split("\n")
                  if p.strip().endswith(".html") and "nginx-debian" not in p]
    ok_count, total = inject_css(14, html_files, scrollbar_css)
    results[14] = {"scrollbars": (ok_count == total, f"{ok_count}/{total} files patched")}

    # ── Final report ──────────────────────────────────────────────────────────
    elapsed = int(time.time() - t_start)
    passed_fixes, failed_fixes = [], []
    for fid, fdata in sorted(results.items()):
        all_ok = all(v[0] for v in fdata.values() if isinstance(v, tuple))
        (passed_fixes if all_ok else failed_fixes).append(fid)

    report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "elapsed_seconds": elapsed,
        "ollama_url": OLLAMA_URL,
        "model": MODEL,
        "passed_fixes": passed_fixes,
        "failed_fixes": failed_fixes,
        "details": {
            str(k): {kk: [vv[0], vv[1]] for kk, vv in v.items() if isinstance(vv, tuple)}
            for k, v in results.items()
        }
    }
    REPORT_FILE.write_text(json.dumps(report, indent=2))

    log("\n" + "=" * 60)
    log(f"COMPLETE — {len(passed_fixes)} passed, {len(failed_fixes)} failed in {elapsed}s")
    log(f"Passed: {passed_fixes}")
    log(f"Failed: {failed_fixes}")
    log(f"Report: {REPORT_FILE}")
    log(f"Log:    {LOG_FILE}")
    log("=" * 60)
    return report


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        run_all_fixes()
    except KeyboardInterrupt:
        log("Interrupted", "WARN")
    except Exception as e:
        log(f"Fatal: {e}\n{traceback.format_exc()}", "ERROR")
        sys.exit(1)
