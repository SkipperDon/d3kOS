#!/usr/bin/env python3
"""
=============================================================================
Ollama Agent Service
Runs INSIDE the Ubuntu VM — monitors Ollama, manages restarts, exposes
a /health endpoint so the TrueNAS host watchdog can query it.
=============================================================================
Install:
  pip install psutil requests --break-system-packages
  cp ollama-agent.py /opt/ollama-agent/ollama-agent.py
  cp ollama-agent.service /etc/systemd/system/
  systemctl enable --now ollama-agent
=============================================================================
"""

import json
import logging
import os
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional

import psutil
import requests

# =============================================================================
# CONFIG
# =============================================================================
OLLAMA_BASE_URL      = "http://localhost:11434"
AGENT_PORT           = 11435           # Health endpoint port
CHECK_INTERVAL       = 30              # Seconds between health checks
INFERENCE_TIMEOUT    = 30              # Max seconds to wait for test inference
HANG_TIMEOUT         = 60             # Seconds before declaring Ollama hung
MAX_RESTARTS_PER_HOUR = 5             # Alert if restarting too often
RESTART_COOLDOWN     = 120            # Seconds between restarts

# Inference probe — uses smallest/fastest model available
PROBE_MODEL          = ""             # Leave empty to auto-detect smallest model
PROBE_PROMPT         = "Reply with only the word: OK"

# Notifications (same as host watchdog — set what you use)
NOTIFY_EMAIL         = ""             # Uses system mail command
NTFY_TOPIC           = ""             # e.g. "truenas-alerts"
NOTIFY_WEBHOOK       = ""             # Slack/Discord webhook URL

# Log file
LOG_FILE             = "/var/log/ollama-agent.log"

# VRAM thresholds (percentage used)
VRAM_WARN_PCT        = 85
VRAM_CRITICAL_PCT    = 95
RAM_WARN_PCT         = 85
# =============================================================================

# --- Logging setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ]
)
log = logging.getLogger("ollama-agent")

# =============================================================================
# GLOBAL STATE
# =============================================================================
state = {
    "status":          "starting",     # healthy | degraded | hung | restarting | down
    "ollama_running":  False,
    "api_reachable":   False,
    "inference_ok":    False,
    "last_check":      None,
    "last_restart":    None,
    "restart_count":   0,
    "restarts_this_hour": 0,
    "models":          [],
    "active_model":    None,
    "ram_used_pct":    0.0,
    "vram_used_pct":   None,          # None if no GPU
    "vram_used_mb":    None,
    "vram_total_mb":   None,
    "gpu_name":        None,
    "uptime_seconds":  0,
    "errors":          [],
    "warnings":        [],
    "agent_start":     datetime.now().isoformat(),
}
state_lock = threading.Lock()

# =============================================================================
# NOTIFICATIONS
# =============================================================================
def notify(subject: str, body: str):
    log.warning(f"NOTIFY: {subject}")
    if NTFY_TOPIC:
        try:
            requests.post(f"https://ntfy.sh/{NTFY_TOPIC}",
                          data=f"{subject}: {body}", timeout=5)
        except Exception:
            pass
    if NOTIFY_WEBHOOK:
        try:
            requests.post(NOTIFY_WEBHOOK,
                          json={"text": f"[Ollama-Agent] {subject}\n{body}"},
                          timeout=5)
        except Exception:
            pass
    if NOTIFY_EMAIL:
        try:
            subprocess.run(
                ["sendmail", NOTIFY_EMAIL],
                input=f"Subject: [Ollama-Agent] {subject}\n\n{body}",
                text=True, timeout=10
            )
        except Exception:
            pass

# =============================================================================
# SYSTEM CHECKS
# =============================================================================
def check_ollama_process() -> bool:
    """Check if the ollama process is running."""
    for proc in psutil.process_iter(["name", "cmdline"]):
        try:
            if "ollama" in proc.info["name"].lower():
                return True
            if proc.info["cmdline"] and any("ollama" in c for c in proc.info["cmdline"]):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False


def check_ollama_api() -> tuple[bool, list]:
    """Hit /api/tags — confirms API is accepting connections and returns models."""
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10)
        if resp.status_code == 200:
            models = [m["name"] for m in resp.json().get("models", [])]
            return True, models
    except requests.exceptions.ConnectionError:
        pass
    except Exception as e:
        log.error(f"API check error: {e}")
    return False, []


def check_ollama_inference(model: str) -> bool:
    """Send a minimal prompt and verify we get a response."""
    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={"model": model, "prompt": PROBE_PROMPT,
                  "stream": False, "options": {"num_predict": 5}},
            timeout=INFERENCE_TIMEOUT
        )
        if resp.status_code == 200:
            result = resp.json().get("response", "").strip()
            log.info(f"Inference probe response: '{result}'")
            return len(result) > 0
    except requests.exceptions.Timeout:
        log.error(f"Inference probe timed out after {INFERENCE_TIMEOUT}s — Ollama may be hung")
    except Exception as e:
        log.error(f"Inference probe error: {e}")
    return False


def get_vram_stats() -> dict:
    """Try nvidia-smi, then rocm-smi for AMD, then return None if no GPU."""
    # NVIDIA
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,memory.used,memory.total,utilization.gpu",
             "--format=csv,noheader,nounits"],
            timeout=5, stderr=subprocess.DEVNULL
        ).decode().strip().split(",")
        if len(out) >= 3:
            used, total = float(out[1].strip()), float(out[2].strip())
            return {
                "gpu_name":     out[0].strip(),
                "vram_used_mb": used,
                "vram_total_mb": total,
                "vram_used_pct": round(used / total * 100, 1) if total > 0 else 0,
            }
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        pass
    # AMD ROCm
    try:
        out = subprocess.check_output(
            ["rocm-smi", "--showmeminfo", "vram", "--csv"],
            timeout=5, stderr=subprocess.DEVNULL
        ).decode()
        lines = [l for l in out.splitlines() if l and not l.startswith("GPU")]
        if lines:
            parts = lines[0].split(",")
            used = float(parts[1]) / (1024 * 1024)
            total = float(parts[2]) / (1024 * 1024)
            return {
                "gpu_name":      "AMD GPU",
                "vram_used_mb":  round(used, 1),
                "vram_total_mb": round(total, 1),
                "vram_used_pct": round(used / total * 100, 1) if total > 0 else 0,
            }
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        pass
    return {}


def get_ram_stats() -> float:
    vm = psutil.virtual_memory()
    return round(vm.percent, 1)


def pick_probe_model(models: list) -> Optional[str]:
    """Pick the smallest model for inference probing."""
    if PROBE_MODEL and PROBE_MODEL in models:
        return PROBE_MODEL
    # Prefer tiny known-fast models
    for preferred in ["tinyllama", "phi", "gemma:2b", "llama3.2:1b", "mistral"]:
        for m in models:
            if preferred in m.lower():
                return m
    return models[0] if models else None

# =============================================================================
# OLLAMA SERVICE MANAGEMENT
# =============================================================================
def restart_ollama(reason: str):
    """Restart the ollama systemd service."""
    global state
    now = datetime.now()

    with state_lock:
        last = state["last_restart"]
        if last:
            elapsed = (now - datetime.fromisoformat(last)).total_seconds()
            if elapsed < RESTART_COOLDOWN:
                log.warning(f"Restart cooldown active ({int(RESTART_COOLDOWN - elapsed)}s left). Skipping.")
                return

        state["status"] = "restarting"
        state["last_restart"] = now.isoformat()
        state["restart_count"] += 1
        state["restarts_this_hour"] += 1

    log.warning(f"Restarting ollama service — reason: {reason}")
    notify("Ollama restarted", f"Reason: {reason}\nRestart #{state['restart_count']}")

    try:
        subprocess.run(["systemctl", "restart", "ollama"], timeout=30, check=True)
        log.info("Ollama service restarted successfully")
        time.sleep(10)  # Give it time to come up
    except subprocess.CalledProcessError as e:
        log.error(f"Failed to restart ollama: {e}")
        notify("Ollama restart FAILED", str(e))


def check_restart_loop():
    with state_lock:
        count = state["restarts_this_hour"]
    if count >= MAX_RESTARTS_PER_HOUR:
        notify(
            "CRITICAL: Ollama restart loop",
            f"Ollama has restarted {count} times this hour. "
            "Manual intervention required. Agent is pausing restarts."
        )
        log.error(f"Restart loop detected: {count} restarts/hour")
        return True
    return False

# =============================================================================
# MAIN HEALTH CHECK LOOP
# =============================================================================
_hour_reset_time = time.time()

def health_check_loop():
    global _hour_reset_time
    log.info("Ollama Agent started — beginning health check loop")

    while True:
        errors, warnings = [], []

        # Reset hourly counter
        if time.time() - _hour_reset_time > 3600:
            with state_lock:
                state["restarts_this_hour"] = 0
            _hour_reset_time = time.time()

        # 1. Process check
        proc_ok = check_ollama_process()
        if not proc_ok:
            errors.append("Ollama process not found")
            log.error("Ollama process is not running")

        # 2. API check
        api_ok, models = check_ollama_api()
        if not api_ok:
            errors.append("Ollama API not reachable on port 11434")
            log.error("Ollama API unreachable")

        # 3. Inference check (only if API is up and models exist)
        inference_ok = False
        probe_model = None
        if api_ok and models:
            probe_model = pick_probe_model(models)
            if probe_model:
                inference_ok = check_ollama_inference(probe_model)
                if not inference_ok:
                    errors.append(f"Inference probe failed on model: {probe_model}")

        # 4. Resource checks
        ram_pct = get_ram_stats()
        vram = get_vram_stats()

        if ram_pct >= RAM_WARN_PCT:
            warnings.append(f"RAM usage critical: {ram_pct}%")
            log.warning(f"High RAM: {ram_pct}%")

        if vram.get("vram_used_pct") is not None:
            if vram["vram_used_pct"] >= VRAM_CRITICAL_PCT:
                errors.append(f"VRAM critical: {vram['vram_used_pct']}%")
                notify("VRAM Critical", f"{vram['vram_used_pct']}% VRAM used — model may crash")
            elif vram["vram_used_pct"] >= VRAM_WARN_PCT:
                warnings.append(f"VRAM high: {vram['vram_used_pct']}%")

        # 5. Determine overall status
        if not proc_ok or (api_ok and not inference_ok and models):
            new_status = "hung"
        elif not api_ok:
            new_status = "down"
        elif warnings:
            new_status = "degraded"
        else:
            new_status = "healthy"

        # 6. Update state
        with state_lock:
            state.update({
                "status":         new_status,
                "ollama_running": proc_ok,
                "api_reachable":  api_ok,
                "inference_ok":   inference_ok,
                "last_check":     datetime.now().isoformat(),
                "models":         models,
                "active_model":   probe_model,
                "ram_used_pct":   ram_pct,
                "errors":         errors,
                "warnings":       warnings,
                **vram,
            })

        log.info(
            f"Status={new_status} | proc={proc_ok} api={api_ok} "
            f"inference={inference_ok} | RAM={ram_pct}% "
            f"VRAM={vram.get('vram_used_pct', 'N/A')}%"
        )

        # 7. Auto-recovery
        if new_status in ("hung", "down") and not check_restart_loop():
            restart_ollama(reason="; ".join(errors))

        elif new_status == "degraded":
            if not any("warned" in w for w in warnings):
                notify("Ollama Degraded", "\n".join(warnings))

        time.sleep(CHECK_INTERVAL)


# =============================================================================
# HTTP HEALTH ENDPOINT
# =============================================================================
class HealthHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress default access log spam

    def do_GET(self):
        if self.path in ("/health", "/"):
            with state_lock:
                payload = dict(state)

            payload["timestamp"] = datetime.now().isoformat()
            payload["healthy"] = state["status"] == "healthy"

            status_code = 200 if payload["healthy"] else 503
            body = json.dumps(payload, indent=2).encode()

            self.send_response(status_code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)

        elif self.path == "/restart":
            # Manual restart trigger (POST only in production — simplified here)
            threading.Thread(target=restart_ollama, args=("Manual trigger via /restart",)).start()
            self.send_response(202)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "restart initiated"}')

        else:
            self.send_response(404)
            self.end_headers()


def run_http_server():
    server = HTTPServer(("0.0.0.0", AGENT_PORT), HealthHandler)
    log.info(f"Health endpoint running on :{AGENT_PORT}/health")
    server.serve_forever()


# =============================================================================
# ENTRY POINT
# =============================================================================
if __name__ == "__main__":
    # Start HTTP server in background thread
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()

    # Run health check loop (blocking)
    try:
        health_check_loop()
    except KeyboardInterrupt:
        log.info("Agent stopped")
