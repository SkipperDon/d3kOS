#!/usr/bin/env python3
"""
d3kOS Ollama Phase Executor v2 — Gemini API Integration (v0.9.4)

Phases:
  query_handler  — Add _query_gemini() method + modify query() routing
  settings       — Add Gemini API configuration section to settings.html

Usage:
  python3 ollama_execute.py <phase>           # run one phase, show validation report
  python3 ollama_execute.py <phase> --apply   # run + auto-apply validated blocks
  python3 ollama_execute.py all               # run all phases
  python3 ollama_execute.py all --apply       # run all + auto-apply all validated
  python3 ollama_execute.py all --skip-ollama # validate saved instructions (no API call)
"""

import sys
import re
import json
import time
import pathlib
import tempfile
import subprocess
import threading
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

# ── Paths ─────────────────────────────────────────────────────────────────────
VERSION_DIR  = pathlib.Path(__file__).resolve().parent.parent   # deployment/v0.9.4/
PROJECT_ROOT = VERSION_DIR.parent.parent                         # Helm-OS/
SPEC_FILE    = PROJECT_ROOT / "doc/v0.9.2_GEMINI_API_INTEGRATION_OLLAMA_SPEC.md"
CONTEXT_FILE = PROJECT_ROOT / "deployment/docs/helm_os_context.md"
SOURCE_DIR   = VERSION_DIR / "pi_source"
OUTPUT_DIR   = VERSION_DIR / "ollama_output"

# ── Ollama config ──────────────────────────────────────────────────────────────
OLLAMA_URL = "http://192.168.1.36:11434/api/generate"
MODEL      = "qwen3-coder:30b"
TIMEOUT    = 300

# ── Runtime stats ─────────────────────────────────────────────────────────────
_stats_lock  = threading.Lock()
_print_lock  = threading.Lock()
_ollama_calls = []

def tprint(*args, **kwargs):
    with _print_lock:
        print(*args, **kwargs)

# ── Known globals ──────────────────────────────────────────────────────────────
KNOWN_GLOBALS = {
    # JS language
    'const', 'let', 'var', 'function', 'return', 'if', 'else', 'for', 'while',
    'do', 'switch', 'case', 'break', 'continue', 'new', 'this', 'typeof',
    'instanceof', 'class', 'import', 'export', 'default', 'from', 'async',
    'await', 'try', 'catch', 'finally', 'throw', 'in', 'of', 'delete', 'void',
    'true', 'false', 'null', 'undefined', 'NaN', 'Infinity',
    # JS built-ins
    'JSON', 'Math', 'Date', 'parseInt', 'parseFloat', 'isNaN', 'isFinite',
    'Promise', 'Error', 'Object', 'Array', 'String', 'Number', 'Boolean',
    'Symbol', 'Map', 'Set', 'WeakMap', 'RegExp', 'Proxy', 'Reflect',
    # Browser globals
    'Units', 'window', 'document', 'navigator', 'location', 'history',
    'localStorage', 'sessionStorage', 'console', 'alert', 'confirm', 'prompt',
    'fetch', 'WebSocket', 'XMLHttpRequest', 'FormData', 'URLSearchParams',
    'setTimeout', 'setInterval', 'clearTimeout', 'clearInterval',
    'requestAnimationFrame', 'cancelAnimationFrame', 'performance',
    'CustomEvent', 'Event', 'MutationObserver', 'IntersectionObserver',
    # DOM properties
    'nextElementSibling', 'previousElementSibling', 'parentElement', 'children',
    'firstChild', 'lastChild', 'childNodes', 'nodeType', 'nodeName',
    'classList', 'className', 'textContent', 'innerHTML', 'innerText',
    'style', 'dataset', 'attributes', 'offsetWidth', 'offsetHeight',
    'scrollTop', 'scrollLeft', 'clientWidth', 'clientHeight',
    'getElementById', 'querySelector', 'querySelectorAll',
    'getElementsByClassName', 'getElementsByTagName',
    'addEventListener', 'removeEventListener', 'dispatchEvent',
    'getAttribute', 'setAttribute', 'removeAttribute', 'hasAttribute',
    'appendChild', 'removeChild', 'insertBefore', 'replaceChild', 'cloneNode',
    'contains', 'closest', 'matches', 'focus', 'blur', 'click', 'submit',
    # Common short names
    'add', 'remove', 'toggle', 'replace', 'trim', 'split', 'join', 'push',
    'pop', 'shift', 'unshift', 'slice', 'splice', 'sort', 'filter', 'map',
    'forEach', 'find', 'findIndex', 'includes', 'some', 'every', 'reduce',
    'keys', 'values', 'entries', 'assign', 'create', 'freeze',
    'parse', 'stringify', 'floor', 'ceil', 'round', 'abs', 'max', 'min',
    'toFixed', 'toString', 'valueOf', 'hasOwnProperty', 'call', 'apply', 'bind',
    # Common variable names
    'event', 'data', 'value', 'values', 'error', 'errors', 'result', 'results',
    'callback', 'response', 'request', 'options', 'config', 'settings',
    'item', 'items', 'index', 'element', 'elements', 'target', 'source',
    'input', 'output', 'name', 'type', 'path', 'url', 'href', 'src',
    'text', 'html', 'node', 'body', 'head', 'form', 'link',
    # d3kOS globals
    'temperature', 'pressure', 'speed', 'depth', 'fuel', 'distance',
    'length', 'weight', 'displacement', 'getPreference', 'setPreference',
    'toDisplay', 'toC', 'toF', 'toBar', 'toPSI', 'toKmh', 'toMph',
    'toKm', 'toNm', 'toMeters', 'toFeet', 'toLiters', 'toGallons',
    'toKg', 'toLb', 'toCi', 'unit', 'measurementSystemChanged',
    # Python language
    'self', 'cls', 'None', 'True', 'False',
    'def', 'return', 'import', 'from', 'class', 'if', 'elif', 'else',
    'for', 'while', 'try', 'except', 'finally', 'with', 'as', 'pass',
    'raise', 'yield', 'lambda', 'global', 'nonlocal', 'assert', 'del',
    # Python built-ins
    'print', 'len', 'str', 'int', 'float', 'bool', 'list', 'dict', 'tuple',
    'set', 'type', 'open', 'range', 'enumerate', 'zip', 'map', 'filter',
    'sorted', 'reversed', 'sum', 'min', 'max', 'abs', 'round', 'repr',
    'isinstance', 'issubclass', 'hasattr', 'getattr', 'setattr', 'delattr',
    'callable', 'iter', 'next', 'super', 'property', 'staticmethod',
    'classmethod', 'format', 'input', 'vars', 'dir', 'help', 'id',
    # Python common names
    'system', 'metric', 'imperial', 'psi', 'bar', 'fahrenheit', 'celsius',
    'knots', 'kmh', 'mph', 'status', 'parts', 'response', 'formatted',
    'preference', 'category', 'message', 'content', 'body', 'headers',
    'json', 'load', 'loads', 'dump', 'dumps',
    # Gemini/AI specific (to avoid false-positive invented-var flags)
    'gemini', 'proxy', 'requests', 'payload', 'elapsed', 'timeout',
    'manual_context', 'boat_status', 'query_text', 'api_key', 'model',
    'candidates', 'history', 'session_history', 'start_time', 'elapsed_ms',
}

# ── Phase definitions ──────────────────────────────────────────────────────────
# phase → (spec section header, source file, context keywords)
PHASES = {
    "query_handler": (
        "PHASE 3: VOICE ASSISTANT INTEGRATION",
        "query_handler.py",
        ["def query", "def _query", "openrouter", "manual_context", "format_quick_answer",
         "def query_openrouter", "search_manuals", "RAG"]
    ),
    "settings": (
        "PHASE 4: SETTINGS UI",
        "settings.html",
        ["</main>", "measurement-section", "settings-section", "setting-row",
         "Measurement System", "handleMeasurementToggle"]
    ),
}


# ── Context extraction ─────────────────────────────────────────────────────────

def extract_enclosing_function_js(lines, hit_line):
    func_start = None
    for i in range(hit_line, max(-1, hit_line - 80), -1):
        if re.search(r'\bfunction\s+\w+\s*\(|^\s*(async\s+)?function\b|=\s*(async\s+)?\(.*\)\s*=>', lines[i]):
            func_start = i
            break
    if func_start is None:
        return max(0, hit_line - 50), min(len(lines) - 1, hit_line + 50)
    depth = 0
    func_end = hit_line
    found_open = False
    for i in range(func_start, min(len(lines), func_start + 200)):
        for ch in lines[i]:
            if ch == '{': depth += 1; found_open = True
            elif ch == '}': depth -= 1
        if found_open and depth == 0:
            func_end = i
            break
    return func_start, func_end


def extract_enclosing_function_py(lines, hit_line):
    func_start = None
    hit_indent = len(lines[hit_line]) - len(lines[hit_line].lstrip())
    for i in range(hit_line, max(-1, hit_line - 100), -1):
        stripped = lines[i].lstrip()
        indent = len(lines[i]) - len(stripped)
        if stripped.startswith('def ') and indent < hit_indent:
            func_start = i; break
        if stripped.startswith('def ') and indent == 0:
            func_start = i; break
    if func_start is None:
        return max(0, hit_line - 50), min(len(lines) - 1, hit_line + 60)
    base_indent = len(lines[func_start]) - len(lines[func_start].lstrip())
    func_end = func_start
    for i in range(func_start + 1, min(len(lines), func_start + 200)):
        line = lines[i]
        stripped = line.lstrip()
        if not stripped or stripped.startswith('#'):
            continue
        indent = len(line) - len(stripped)
        if indent <= base_indent and stripped and not stripped.startswith('#'):
            func_end = i - 1; break
        func_end = i
    return func_start, func_end


def extract_context(source_text, keywords, file_type):
    lines = source_text.splitlines()
    hit_line = None
    for i, line in enumerate(lines):
        for kw in keywords:
            bare_kw = kw.split('.')[-1]
            if re.search(rf'\bfunction\s+{re.escape(bare_kw)}\s*\(', line):
                hit_line = i; break
        if hit_line is not None:
            break
    if hit_line is None:
        for i, line in enumerate(lines):
            for kw in keywords:
                if re.search(kw, line, re.IGNORECASE):
                    hit_line = i; break
            if hit_line is not None:
                break
    if hit_line is None:
        start = max(0, len(lines) - 80)
        block = lines[start:]
        context = '\n'.join(f"{i+start+1}: {l}" for i, l in enumerate(block))
        return context, []
    if file_type == 'py':
        start, end = extract_enclosing_function_py(lines, hit_line)
    else:
        start, end = extract_enclosing_function_js(lines, hit_line)
    context = '\n'.join(f"{i+1}: {lines[i]}" for i in range(start, end + 1))
    preamble = '\n'.join(f"{i+1}: {lines[i]}" for i in range(min(15, start)))
    if preamble:
        context = preamble + '\n\n... (intervening lines omitted) ...\n\n' + context
    func_lines = lines[start:end + 1]
    scope_vars = extract_scope_vars('\n'.join(func_lines), file_type)
    return context, scope_vars


def extract_scope_vars(text, file_type):
    vars_found = set()
    if file_type == 'py':
        for m in re.finditer(r'\bdef\s+(\w+)\b', text): vars_found.add(m.group(1))
        for m in re.finditer(r'\bself\.(\w+)\b', text): vars_found.add(m.group(1))
        for m in re.finditer(r'^(\s*)(\w+)\s*=\s*', text, re.MULTILINE):
            if m.group(2) not in ('True', 'False', 'None'): vars_found.add(m.group(2))
    else:
        for m in re.finditer(r'\b(?:const|let|var)\s+(\w+)\b', text): vars_found.add(m.group(1))
        for m in re.finditer(r'\bfunction\s+(\w+)\b', text): vars_found.add(m.group(1))
        for m in re.finditer(r'\b(\w+)\s*:\s*{', text): vars_found.add(m.group(1))
        for m in re.finditer(r'\b(\w+)\.(\w+)\b', text):
            vars_found.add(m.group(1)); vars_found.add(m.group(2))
    return sorted(vars_found - KNOWN_GLOBALS)


# ── Validation ─────────────────────────────────────────────────────────────────

def parse_instruction_blocks(text):
    blocks = []
    text = re.sub(r'^```[^\n]*\n?', '', text, flags=re.MULTILINE)
    text = re.sub(r'^```\s*$', '', text, flags=re.MULTILINE)
    pattern = re.compile(
        r'FIND_LINE:\s*(.+?)\n'
        r'ACTION:\s*(INSERT_BEFORE|INSERT_AFTER|REPLACE)\s*\n'
        r'CODE:\s*\n(.*?)END_CODE',
        re.DOTALL
    )
    for m in pattern.finditer(text):
        find_line = m.group(1).strip().strip('`')
        blocks.append({
            'find_line': find_line,
            'action':    m.group(2).strip(),
            'code':      m.group(3).rstrip('\n'),
            'valid':     True,
            'issues':    [],
            'correction_attempted': False,
            'corrected': False,
        })
    return blocks


def check_find_line(find_line, source_text):
    return find_line in source_text


def check_invented_vars(code, source_text, file_type):
    declared_in_code = set()
    if file_type == 'py':
        for m in re.finditer(r'\bdef\s+(\w+)\b', code): declared_in_code.add(m.group(1))
        for m in re.finditer(r'^\s*(\w+)\s*=\s*', code, re.MULTILINE): declared_in_code.add(m.group(1))
        for m in re.finditer(r'\bfor\s+(\w+)\b', code): declared_in_code.add(m.group(1))
    else:
        for m in re.finditer(r'\b(?:const|let|var)\s+(\w+)\b', code): declared_in_code.add(m.group(1))
        for m in re.finditer(r'\bfunction\s+(\w+)\b', code): declared_in_code.add(m.group(1))
        for m in re.finditer(r'\bfor\s*\([^)]*\b(\w+)\b', code): declared_in_code.add(m.group(1))
    clean_code = re.sub(r'"[^"\n]*"|\'[^\'\\n]*\'|`[^`]*`', '""', code)
    clean_code = re.sub(r'//[^\n]*', '', clean_code)
    clean_code = re.sub(r'/\*.*?\*/', '', clean_code, flags=re.DOTALL)
    clean_code = re.sub(r'#[^\n]*', '', clean_code)
    suspicious = []
    candidates = set()
    for m in re.finditer(r'(?<![.\w])([a-zA-Z_$][a-zA-Z0-9_$]{4,})\b(?!\s*:)(?!\s*\()', clean_code):
        candidates.add(m.group(1))
    for m in re.finditer(r'(?<![.\w])([a-zA-Z_$][a-zA-Z0-9_$]{4,})\b\s*\(', clean_code):
        candidates.add(m.group(1))
    for name in candidates:
        if name in KNOWN_GLOBALS or name in declared_in_code or name in source_text:
            continue
        suspicious.append(name)
    for m in re.finditer(r'\bwindow\.([a-zA-Z_$][a-zA-Z0-9_$]{4,})\b', clean_code):
        prop = m.group(1)
        if prop in KNOWN_GLOBALS or prop in declared_in_code or prop in source_text:
            continue
        suspicious.append(f'window.{prop}')
    return sorted(set(suspicious))


def syntax_check_js(code):
    with tempfile.NamedTemporaryFile(suffix='.js', mode='w', delete=False) as f:
        f.write(code); tmp = f.name
    r = subprocess.run(['node', '--check', tmp], capture_output=True, text=True)
    pathlib.Path(tmp).unlink(missing_ok=True)
    if r.returncode != 0:
        err = (r.stderr or r.stdout).strip().split('\n')[0]
        return False, err
    return True, ''


def syntax_check_py(code):
    with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False) as f:
        f.write(code); tmp = f.name
    r = subprocess.run([sys.executable, '-m', 'py_compile', tmp], capture_output=True, text=True)
    pathlib.Path(tmp).unlink(missing_ok=True)
    if r.returncode != 0:
        err = (r.stderr or r.stdout).strip()
        return False, err
    return True, ''


def validate_blocks(blocks, source_text, file_type, phase_label=''):
    for b in blocks:
        b['valid'] = True; b['issues'] = []
        if not check_find_line(b['find_line'], source_text):
            b['valid'] = False
            b['issues'].append(f"FIND_LINE not found verbatim in source: {b['find_line']!r}")
        invented = check_invented_vars(b['code'], source_text, file_type)
        if invented:
            b['valid'] = False
            b['issues'].append(f"Invented identifiers (not in source): {', '.join(invented)}")
        if file_type == 'js' and '<script' not in b['code']:
            ok, err = syntax_check_js(b['code'])
            if not ok:
                b['valid'] = False
                b['issues'].append(f"JS syntax error: {err}")
        if file_type == 'py':
            ok, err = syntax_check_py(b['code'])
            if not ok:
                b['valid'] = False
                b['issues'].append(f"Python syntax error: {err}")
    return blocks


# ── Correction loop ────────────────────────────────────────────────────────────

def find_similar_lines(find_line, source_text):
    words = set(find_line.lower().split())
    if len(words) < 2:
        return []
    scored = []
    for line in source_text.splitlines():
        line_words = set(line.lower().split())
        overlap = len(words & line_words)
        if overlap >= 2:
            scored.append((overlap, line.strip()))
    scored.sort(reverse=True)
    return [l for _, l in scored[:3]]


def find_context_for_correction(block, source_text):
    lines = source_text.splitlines()
    best_line = None
    best_overlap = 0
    words = set(block['find_line'].lower().split())
    for i, line in enumerate(lines):
        overlap = len(words & set(line.lower().split()))
        if overlap > best_overlap:
            best_overlap = overlap; best_line = i
    if best_line is None:
        return '\n'.join(f"{i+1}: {l}" for i, l in enumerate(lines[-30:], len(lines)-29))
    start = max(0, best_line - 15); end = min(len(lines), best_line + 15)
    return '\n'.join(f"{i+1}: {lines[i]}" for i in range(start, end))


def generate_correction_advice(block, source_text, scope_vars):
    advice_parts = []
    for issue in block['issues']:
        if 'FIND_LINE not found' in issue:
            similar = find_similar_lines(block['find_line'], source_text)
            if similar:
                advice_parts.append(
                    f"The FIND_LINE you used does not exist. Use one of these real lines instead:\n"
                    + '\n'.join(f'  "{l}"' for l in similar)
                )
            else:
                advice_parts.append(
                    "The FIND_LINE you used does not exist in the file. "
                    "Look at the file context below and pick a real line near your insertion point."
                )
        elif 'Invented identifiers' in issue:
            invented_names = re.findall(r'`([^`]+)`|(\w{4,})', issue.split(':', 1)[-1])
            invented_names = [a or b for a, b in invented_names if (a or b) not in ('not', 'source')]
            fixes = []
            for name in invented_names[:3]:
                matches = [v for v in scope_vars if name.lower() in v.lower() or v.lower() in name.lower()]
                if matches:
                    fixes.append(f"  '{name}' → did you mean '{matches[0]}'? (from scope)")
                else:
                    fixes.append(f"  '{name}' → not found in scope; check the variable names listed below")
            if fixes:
                advice_parts.append("Variable name corrections needed:\n" + '\n'.join(fixes))
            else:
                advice_parts.append(
                    f"These names don't exist in the file: {issue.split(':', 1)[-1].strip()}. "
                    "Use only names from the scope variables list below."
                )
        elif 'syntax error' in issue.lower():
            advice_parts.append(f"Fix this syntax error: {issue}")
    return '\n\n'.join(advice_parts) or 'Fix the issues listed above.'


def call_ollama(prompt, label=''):
    start = time.time()
    data = json.dumps({"model": MODEL, "prompt": prompt, "stream": False}).encode()
    req = urllib.request.Request(OLLAMA_URL, data=data,
                                  headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            result = json.loads(resp.read().decode())
            response = result.get('response', '')
    except Exception as e:
        tprint(f"  [Ollama ERROR] {e}")
        return ''
    elapsed = round(time.time() - start, 1)
    with _stats_lock:
        _ollama_calls.append({
            'label': label,
            'prompt_chars': len(prompt),
            'response_chars': len(response),
            'elapsed_s': elapsed,
        })
    tprint(f"  [Ollama] {label}: {len(response)} chars in {elapsed}s")
    return response


def run_correction(block, source_text, source_filename, scope_vars):
    advice = generate_correction_advice(block, source_text, scope_vars)
    nearby_ctx = find_context_for_correction(block, source_text)
    prompt = f"""You generated an instruction block for {source_filename} that failed validation.

## YOUR FAILED BLOCK
FIND_LINE: {block['find_line']}
ACTION: {block['action']}
CODE:
{block['code']}
END_CODE

## WHAT WENT WRONG
{chr(10).join('- ' + e for e in block['issues'])}

## HOW TO FIX IT
{advice}

## VARIABLES AVAILABLE IN SCOPE (use these — do not invent new names)
{', '.join(scope_vars[:30])}

## RELEVANT FILE CONTEXT
{nearby_ctx}

## YOUR TASK
Return EXACTLY ONE corrected block. Fix what went wrong. Nothing else.
FIND_LINE: <exact verbatim line from the file above>
ACTION: {block['action']}
CODE:
<corrected code>
END_CODE"""
    response = call_ollama(prompt, label=f'correction:{source_filename}')
    corrected = parse_instruction_blocks(response)
    return corrected[0] if corrected else None


# ── Spec extraction ────────────────────────────────────────────────────────────

def load_spec_section(section_header):
    spec_text = SPEC_FILE.read_text()
    pattern = re.compile(
        rf'^## {re.escape(section_header)}.*?(?=^## |\Z)',
        re.MULTILINE | re.DOTALL
    )
    m = pattern.search(spec_text)
    if not m:
        return f"[Section '{section_header}' not found in spec]"
    return m.group(0).strip()


def load_context_file():
    if CONTEXT_FILE.exists():
        return CONTEXT_FILE.read_text()
    return ''


# ── Phase runner ───────────────────────────────────────────────────────────────

def run_phase(phase_name, apply=False, skip_ollama=False):
    if phase_name not in PHASES:
        tprint(f"Unknown phase: {phase_name}. Available: {', '.join(PHASES)}")
        return

    section_header, source_filename, keywords = PHASES[phase_name]
    source_path = SOURCE_DIR / source_filename
    out_path    = OUTPUT_DIR / f"{phase_name}.instructions"
    file_type   = 'py' if source_filename.endswith('.py') else 'js'

    tprint(f"\n{'='*60}")
    tprint(f"PHASE: {phase_name} | FILE: {source_filename}")
    tprint(f"{'='*60}")

    if not source_path.exists():
        tprint(f"  [ERROR] Source not found: {source_path}")
        return

    source_text = source_path.read_text()

    # Extract context for prompt
    context, scope_vars = extract_context(source_text, keywords, file_type)
    tprint(f"  Context: {len(context)} chars | Scope vars: {scope_vars[:10]}")

    # Get instructions from Ollama (or load saved)
    if skip_ollama and out_path.exists():
        tprint(f"  [SKIP-OLLAMA] Loading saved instructions from {out_path.name}")
        response = out_path.read_text()
    elif skip_ollama:
        tprint(f"  [SKIP-OLLAMA] No saved instructions found for {phase_name}, skipping")
        return
    else:
        spec_section = load_spec_section(section_header)
        context_file = load_context_file()
        prompt = f"""{context_file}

---

## TASK: {phase_name.upper()} — {source_filename}

## SPEC — What to implement:
{spec_section}

## CURRENT FILE CONTEXT (around the area to modify):
{context}

## VARIABLES IN SCOPE (use these exact names):
{', '.join(scope_vars[:30]) if scope_vars else '(see context above)'}

## NOTE: Gemini proxy runs on port 8097 (not 8099). Use http://localhost:8097/gemini/...

## OUTPUT FORMAT — REQUIRED:
Use FIND_LINE/ACTION/CODE format exactly.
Do NOT wrap output in markdown code fences.
"""
        tprint(f"  Calling Ollama ({len(prompt)} chars)...")
        response = call_ollama(prompt, label=phase_name)
        if response:
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            out_path.write_text(response)
            tprint(f"  Saved to {out_path.name}")

    if not response:
        tprint(f"  [ERROR] No response for {phase_name}")
        return

    # Parse blocks
    blocks = parse_instruction_blocks(response)
    tprint(f"  Parsed {len(blocks)} instruction blocks")
    if not blocks:
        tprint(f"  [WARNING] No FIND_LINE/ACTION/CODE blocks found in response")
        tprint(f"  --- Raw response (first 500 chars) ---")
        tprint(response[:500])
        return

    # Re-read source (important if running multiple phases)
    source_text = source_path.read_text()

    # Validate
    blocks = validate_blocks(blocks, source_text, file_type, phase_label=phase_name)

    # Correction loop for invalid blocks (live runs only)
    if not skip_ollama:
        for b in blocks:
            if not b['valid'] and not b['correction_attempted']:
                tprint(f"  [CORRECTION] Block failed: {b['issues']}")
                b['correction_attempted'] = True
                corrected = run_correction(b, source_text, source_filename, scope_vars)
                if corrected:
                    corrected_list = validate_blocks([corrected], source_text, file_type)
                    if corrected_list[0]['valid']:
                        tprint(f"  [CORRECTION] Fixed!")
                        b.update(corrected_list[0])
                        b['corrected'] = True
                    else:
                        tprint(f"  [CORRECTION] Still invalid after retry: {corrected_list[0]['issues']}")
                else:
                    tprint(f"  [CORRECTION] No parseable block in correction response")

    # Report
    valid = [b for b in blocks if b['valid']]
    invalid = [b for b in blocks if not b['valid']]
    corrected = [b for b in blocks if b.get('corrected')]
    tprint(f"\n  VALIDATION: {len(valid)}/{len(blocks)} valid | {len(corrected)} corrected | {len(invalid)} flagged")
    for b in invalid:
        tprint(f"    ✗ FIND_LINE: {b['find_line']!r}")
        for issue in b['issues']:
            tprint(f"      → {issue}")

    # Apply
    if apply and valid:
        tprint(f"\n  Applying {len(valid)} valid blocks to {source_filename}...")
        current = source_path.read_text()
        for b in valid:
            if b['action'] == 'REPLACE':
                current = current.replace(b['find_line'], b['code'], 1)
            elif b['action'] == 'INSERT_AFTER':
                current = current.replace(b['find_line'], b['find_line'] + '\n' + b['code'], 1)
            elif b['action'] == 'INSERT_BEFORE':
                current = current.replace(b['find_line'], b['code'] + '\n' + b['find_line'], 1)
        source_path.write_text(current)
        tprint(f"  ✓ Applied to {source_path}")
    elif apply and not valid:
        tprint(f"  No valid blocks to apply")
    else:
        for i, b in enumerate(valid):
            tprint(f"\n  Block {i+1}: {b['action']} at {b['find_line']!r}")
            tprint(f"  Code preview: {b['code'][:200]}...")


# ── Report ─────────────────────────────────────────────────────────────────────

def print_report():
    with _stats_lock:
        calls = list(_ollama_calls)
    if not calls:
        return
    total_prompt = sum(c['prompt_chars'] for c in calls)
    total_response = sum(c['response_chars'] for c in calls)
    total_time = sum(c['elapsed_s'] for c in calls)
    print(f"\n{'='*60}")
    print(f"OLLAMA CALL SUMMARY ({len(calls)} calls)")
    print(f"{'='*60}")
    for c in calls:
        print(f"  {c['label']:30s} {c['prompt_chars']:6d}p → {c['response_chars']:6d}r  {c['elapsed_s']:.1f}s")
    print(f"  {'TOTAL':30s} {total_prompt:6d}p → {total_response:6d}r  {total_time:.1f}s")
    print(f"\n  Ollama (qwen3-coder:30b @ 192.168.1.36): $0.00 (local GPU)")
    print(f"  Claude API: check console.anthropic.com → Usage → today")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description='d3kOS Ollama Executor v2 — Gemini Integration')
    parser.add_argument('phase', help=f'Phase to run: {", ".join(PHASES)} or all')
    parser.add_argument('--apply', action='store_true', help='Auto-apply validated blocks')
    parser.add_argument('--skip-ollama', action='store_true', help='Use saved instructions (no Ollama call)')
    parser.add_argument('--parallel', type=int, default=1, help='Parallel phases (default 1)')
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    phases_to_run = list(PHASES.keys()) if args.phase == 'all' else [args.phase]

    if args.parallel > 1 and len(phases_to_run) > 1:
        with ThreadPoolExecutor(max_workers=args.parallel) as executor:
            futures = {executor.submit(run_phase, p, args.apply, args.skip_ollama): p
                       for p in phases_to_run}
            for f in as_completed(futures):
                p = futures[f]
                try:
                    f.result()
                except Exception as e:
                    tprint(f"  [ERROR in {p}] {e}")
    else:
        for p in phases_to_run:
            run_phase(p, args.apply, args.skip_ollama)

    print_report()


if __name__ == '__main__':
    main()
