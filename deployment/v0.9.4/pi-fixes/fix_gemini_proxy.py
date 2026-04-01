#!/usr/bin/env python3
"""
Pi fix script — run directly on the Pi.
Removes Ollama fallback from gemini_proxy.py and cleans gemini.env.

Root cause: gemini.env had OLLAMA_URL=http://127.0.0.1:11434 (Pi local Ollama).
When Gemini API failed, gemini_proxy fell back to local Ollama, loaded
phi3.5:latest (3.8GB), hit timeout, ai_bridge retried — death loop.

Usage: python3 fix_gemini_proxy.py
"""

import re
import shutil
from pathlib import Path

PROXY = Path('/opt/d3kos/services/gemini-nav/gemini_proxy.py')
ENV   = Path('/opt/d3kos/services/gemini-nav/config/gemini.env')

# ── 1. Backup ─────────────────────────────────────────────────────────────────
shutil.copy(PROXY, PROXY.with_suffix('.py.bak-ollama-removal'))
shutil.copy(ENV,   ENV.with_suffix('.env.bak-ollama-removal'))
print("Backups created.")

# ── 2. Fix gemini_proxy.py ────────────────────────────────────────────────────
src = PROXY.read_text()

# Remove OLLAMA_URL and OLLAMA_MODEL constants (two lines)
src = re.sub(
    r"^OLLAMA_URL\s*=.*\n",
    "",
    src,
    flags=re.MULTILINE,
)
src = re.sub(
    r"^OLLAMA_MODEL\s*=.*\n",
    "",
    src,
    flags=re.MULTILINE,
)

# Remove check_ollama() function (entire function)
src = re.sub(
    r"\ndef check_ollama\(\)[^\n]*\n.*?(?=\ndef |\n@app\.route|\nif __name__)",
    "\n",
    src,
    flags=re.DOTALL,
)

# Remove query_ollama() function (entire function)
src = re.sub(
    r"\ndef query_ollama\([^)]*\)[^\n]*\n.*?(?=\ndef |\n@app\.route|\nif __name__)",
    "\n",
    src,
    flags=re.DOTALL,
)

# Remove "Route 2: Ollama fallback" block from /ask endpoint
src = re.sub(
    r"\n    # Route 2: Ollama fallback\n    if result is None and check_ollama\(\):\n        try:\n            result = query_ollama\(user_message\)\n        except Exception as e:\n            error = f'Ollama error: \{e\}'\n",
    "\n",
    src,
)

# Update docstring in /ask: remove Ollama reference
src = src.replace(
    "Routing: Gemini (online + key) → Ollama (LAN fallback) → 503",
    "Routing: Gemini (online + key) → 503 (no Ollama fallback — Pi cannot run LLMs)",
)

# Fix the 503 error message
src = src.replace(
    "'error':  'No AI service available. Check internet or Ollama at 192.168.1.36:11434.'",
    "'error':  'Gemini AI unavailable. Check internet connection and API key.'",
)

# Fix /status endpoint: remove ollama fields
src = re.sub(
    r"        'ollama':\s+check_ollama\(\),\n",
    "",
    src,
)
src = re.sub(
    r"        'ollama_model':\s+OLLAMA_MODEL,\n",
    "",
    src,
)

# Fix module docstring to remove Ollama reference
src = src.replace(
    """d3kOS Gemini Marine AI Proxy — localhost:3001
Routes marine queries to:
  1. Gemini API (https://generativelanguage.googleapis.com) — when online
  2. Ollama (http://192.168.1.36:11434)                    — offline fallback""",
    """d3kOS Gemini Marine AI Proxy — localhost:3001
Routes marine queries to:
  1. Gemini API (https://generativelanguage.googleapis.com) — when online
  2. 503 response — when offline (no local LLM fallback)""",
)

PROXY.write_text(src)
print("gemini_proxy.py fixed.")

# ── 3. Fix gemini.env ─────────────────────────────────────────────────────────
env_lines = ENV.read_text().splitlines(keepends=True)
cleaned = [
    line for line in env_lines
    if not line.startswith('OLLAMA_URL=') and not line.startswith('OLLAMA_MODEL=')
]
ENV.write_text(''.join(cleaned))
print("gemini.env fixed (OLLAMA_URL and OLLAMA_MODEL removed).")

# ── 4. Verify no Ollama references remain ─────────────────────────────────────
remaining = [l for l in PROXY.read_text().splitlines() if 'ollama' in l.lower()]
if remaining:
    print("\nWARNING — remaining ollama references:")
    for l in remaining:
        print(f"  {l}")
else:
    print("Verification passed — no ollama references remain in gemini_proxy.py.")

print("\nDone. Run: sudo systemctl restart d3kos-gemini-nav")
print("Then:     sudo systemctl start d3kos-ai-bridge")
