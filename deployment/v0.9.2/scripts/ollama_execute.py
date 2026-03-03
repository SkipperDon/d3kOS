#!/usr/bin/env python3
"""
d3kOS v0.9.2 — Ollama Phase Executor
Feeds spec sections + focused file context to Ollama.
Ollama returns structured INSERT/MODIFY instructions. Claude applies them.

Usage:
  python3 ollama_execute.py <phase>

Phases: settings, index, onboarding, navigation, weather, query_handler
"""

import sys
import json
import pathlib
import urllib.request
import urllib.error

OLLAMA_URL  = "http://192.168.1.36:11434/api/generate"
MODEL       = "qwen3-coder:30b"
SPEC_FILE   = pathlib.Path(__file__).resolve().parents[3] / "doc/v0.9.2_METRIC_IMPERIAL_CONVERSION_OLLAMA_SPEC.md"
SOURCE_DIR  = pathlib.Path(__file__).resolve().parent.parent / "pi_source"
OUTPUT_DIR  = pathlib.Path(__file__).resolve().parent.parent / "ollama_output"
TIMEOUT     = 300

# phase → (spec section header, source file, context keywords to find insertion points)
PHASES = {
    "settings": (
        "PHASE 3: SETTINGS UI",
        "settings.html",
        ["</main>", "settings-section", "setting-card"]
    ),
    "index": (
        "PHASE 4: DASHBOARD",
        "index.html",
        ["engine-temp", "oil-press", "coolant", "fuel", "speed", "gauge", "updateGauge", "signalk", "ws.onmessage"]
    ),
    "onboarding": (
        "PHASE 5: ONBOARDING",
        "onboarding.html",
        ["boat-origin", "boat_origin", "origin", "engine-size", "engine_size", "step-15", "data-step"]
    ),
    "navigation": (
        "PHASE 6: NAVIGATION",
        "navigation.html",
        ["nav-speed", "speed", "altitude", "data-field", "knots", "updateNav"]
    ),
    "weather": (
        "PHASE 7: WEATHER",
        "weather.html",
        ["weather-temp", "temperature", "wind", "weather-wind", "updateWeather"]
    ),
    "query_handler": (
        "PHASE 8: VOICE ASSISTANT",
        "query_handler.py",
        ["format_quick_answer", "format_response", "fahrenheit", "psi", "gallons", "def _format", "quick_answer"]
    ),
}


def extract_spec_section(spec_text: str, header: str) -> str:
    lines = spec_text.splitlines()
    start = next((i for i, l in enumerate(lines) if header in l and l.startswith("##")), None)
    if start is None:
        return f"[Section '{header}' not found]"
    section = []
    for line in lines[start + 1:]:
        if line.startswith("## ") and section:
            break
        section.append(line)
    return "\n".join(section).strip()


def extract_context(source_text: str, keywords: list, context_lines: int = 40) -> str:
    """Find lines matching keywords and return surrounding context."""
    lines = source_text.splitlines()
    hit_lines = set()
    for i, line in enumerate(lines):
        if any(kw.lower() in line.lower() for kw in keywords):
            for j in range(max(0, i - context_lines), min(len(lines), i + context_lines)):
                hit_lines.add(j)

    if not hit_lines:
        # Fall back to last 60 lines (likely where </main> is)
        return "\n".join(f"{i+1}: {l}" for i, l in enumerate(lines[-60:], len(lines) - 60))

    # Return contiguous blocks with line numbers
    result = []
    prev = -2
    for i in sorted(hit_lines):
        if i > prev + 1:
            result.append(f"\n... (lines {prev+2}–{i}) ...\n")
        result.append(f"{i+1}: {lines[i]}")
        prev = i
    return "\n".join(result)


def call_ollama(prompt: str) -> str:
    payload = json.dumps({
        "model":   MODEL,
        "prompt":  prompt,
        "stream":  False,
        "options": {"temperature": 0.1, "num_predict": 8192}
    }).encode()
    req = urllib.request.Request(OLLAMA_URL, data=payload,
                                  headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return json.loads(resp.read()).get("response", "")
    except urllib.error.URLError as e:
        print(f"[ERROR] Ollama unreachable: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in PHASES:
        print(f"Usage: python3 {sys.argv[0]} <phase>")
        print(f"Phases: {', '.join(PHASES)}")
        sys.exit(1)

    phase_name = sys.argv[1]
    spec_header, source_filename, keywords = PHASES[phase_name]

    spec_text    = SPEC_FILE.read_text()
    spec_section = extract_spec_section(spec_text, spec_header)
    source_path  = SOURCE_DIR / source_filename
    source_text  = source_path.read_text()
    context      = extract_context(source_text, keywords)

    OUTPUT_DIR.mkdir(exist_ok=True)
    out_path = OUTPUT_DIR / (source_filename + ".instructions")

    prompt = f"""You are the d3kOS build system. Execute the following spec section.

## SPEC SECTION
{spec_section}

## RELEVANT SECTIONS OF {source_filename} (with line numbers)
{context}

## YOUR OUTPUT FORMAT
Return a series of change instructions in EXACTLY this format — nothing else:

FIND_LINE: <exact text of an existing line in the file to anchor the change>
ACTION: INSERT_BEFORE | INSERT_AFTER | REPLACE
CODE:
<the exact code to insert or use as replacement>
END_CODE

Rules:
- FIND_LINE must be a line that exists verbatim in the file
- Use multiple FIND_LINE/ACTION/CODE blocks if multiple changes are needed
- For adding <script src="/js/units.js"></script> to <head>: FIND_LINE the first line after <head>
- Keep indentation consistent with surrounding code
- No explanation outside the structured blocks
"""

    print(f"\n[d3kOS Ollama Executor]")
    print(f"  Phase    : {phase_name} ({spec_header})")
    print(f"  Source   : {source_filename} ({len(source_text.splitlines())} lines)")
    print(f"  Context  : {len(context.splitlines())} lines sent to Ollama")
    print(f"  Model    : {MODEL}")
    print(f"  Output   : {out_path.name}")
    print(f"\nSending to Ollama...")

    result = call_ollama(prompt)

    if not result.strip():
        print("[ERROR] Ollama returned empty response")
        sys.exit(1)

    out_path.write_text(result)
    print(f"Done. Instructions saved ({len(result.splitlines())} lines)\n")
    print(result)
    print(f"\nSaved to: {out_path}")


if __name__ == "__main__":
    main()
