#!/usr/bin/env python3
"""
d3kOS Ollama Phase Executor v2

Improvements over v1:
  - Injects helm_os_context.md into every prompt (prevents variable/type hallucination)
  - Extracts enclosing function context instead of ±N lines
  - Extracts in-scope variable names and includes them in the prompt
  - Validates each output block before apply:
      * FIND_LINE text must exist in the source file
      * Invented variable names check (vars not in source or known globals)
      * Syntax check on generated code (node --check / py_compile)
  - Correction loop: flagged blocks are sent back to Ollama with targeted advice
      * Finds the closest real line for FIND_LINE misses
      * Identifies the correct in-scope variable to replace invented ones
      * One retry per block — if still invalid, escalates to manual review
  - Auto-applies validated (and corrected) blocks with --apply flag
  - Generates a report: auto-applied vs corrected vs flagged

Usage:
  python3 ollama_execute.py <phase>           # run one phase, show validation report
  python3 ollama_execute.py <phase> --apply   # run + auto-apply validated blocks
  python3 ollama_execute.py all               # run all phases
  python3 ollama_execute.py all --apply       # run all + auto-apply all validated
  python3 ollama_execute.py all --skip-ollama # validate saved instructions (no API call)

Phases: settings, dashboard, onboarding, navigation, weather, query_handler
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
# Script lives at: deployment/v0.9.2/scripts/ollama_execute.py
# parents[0] = scripts/   parents[1] = v0.9.2/   parents[2] = deployment/   parents[3] = Helm-OS/
VERSION_DIR  = pathlib.Path(__file__).resolve().parent.parent   # deployment/v0.9.2/
PROJECT_ROOT = VERSION_DIR.parent.parent                         # Helm-OS/
SPEC_FILE    = PROJECT_ROOT / "doc/v0.9.2_METRIC_IMPERIAL_CONVERSION_OLLAMA_SPEC.md"
CONTEXT_FILE = PROJECT_ROOT / "deployment/docs/helm_os_context.md"
SOURCE_DIR   = VERSION_DIR / "pi_source"
OUTPUT_DIR   = VERSION_DIR / "ollama_output"

# ── Ollama config ──────────────────────────────────────────────────────────────
OLLAMA_URL = "http://192.168.1.36:11434/api/generate"
MODEL      = "qwen3-coder:30b"
TIMEOUT    = 300

# ── Runtime stats (accumulated across all calls this run) ─────────────────────
_stats_lock  = threading.Lock()
_print_lock  = threading.Lock()
_ollama_calls = []   # list of {phase, type, prompt_chars, response_chars, elapsed_s}

def tprint(*args, **kwargs):
    """Thread-safe print — keeps output readable during parallel runs."""
    with _print_lock:
        print(*args, **kwargs)

# ── Known globals: valid identifiers that won't appear in pi_source files ─────
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
    # DOM element properties (appear after . but also used standalone in destructuring)
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
    # Common short names that appear frequently in generated code
    'add', 'remove', 'toggle', 'replace', 'trim', 'split', 'join', 'push',
    'pop', 'shift', 'unshift', 'slice', 'splice', 'sort', 'filter', 'map',
    'forEach', 'find', 'findIndex', 'includes', 'some', 'every', 'reduce',
    'keys', 'values', 'entries', 'assign', 'create', 'freeze', 'keys',
    'parse', 'stringify', 'floor', 'ceil', 'round', 'abs', 'max', 'min',
    'toFixed', 'toString', 'valueOf', 'hasOwnProperty', 'call', 'apply', 'bind',
    # Common variable names used in generated code
    'event', 'data', 'value', 'values', 'error', 'errors', 'result', 'results',
    'callback', 'response', 'request', 'options', 'config', 'settings',
    'item', 'items', 'index', 'element', 'elements', 'target', 'source',
    'input', 'output', 'name', 'type', 'path', 'url', 'href', 'src',
    'text', 'html', 'node', 'body', 'head', 'form', 'link',
    # d3kOS specific globals (in units.js, always available)
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
    # Python common names in generated code
    'system', 'metric', 'imperial', 'psi', 'bar', 'fahrenheit', 'celsius',
    'knots', 'kmh', 'mph', 'status', 'parts', 'response', 'formatted',
    'preference', 'category', 'message', 'content', 'body', 'headers',
    # json module (commonly imported in generated Python)
    'json', 'load', 'loads', 'dump', 'dumps',
}

# ── Phase definitions ──────────────────────────────────────────────────────────
# phase → (spec section header, source file, context keywords)
PHASES = {
    "settings": (
        "PHASE 3: SETTINGS UI",
        "settings.html",
        ["</main>", "settings-section", "setting-card", "setting-row"]
    ),
    "dashboard": (
        "PHASE 4: DASHBOARD",
        "dashboard.html",
        ["updateGauge", "function updateGauge", "gauge-value", "temp-value", "oil-value"]
    ),
    "onboarding": (
        "PHASE 5: ONBOARDING",
        "onboarding.html",
        ["q15", "boat.*origin", "origin", "step15", "step16", "engine.*size", "q9"]
    ),
    "navigation": (
        "PHASE 6: NAVIGATION",
        "navigation.html",
        ["updateSOG", "updateDepth", "speedOverGround", "navData.depth", "function updateSOG"]
    ),
    "weather": (
        "PHASE 7: WEATHER",
        "weather.html",
        ["updateRadar", "function updateRadar", "metricTemp", "windyUrl", "radarFrame"]
    ),
    "query_handler": (
        "PHASE 8: VOICE ASSISTANT",
        "query_handler.py",
        ["def simple_response", "format_quick_answer", "oil_pressure", "coolant_temp"]
    ),
}


# ── Context extraction ─────────────────────────────────────────────────────────

def extract_enclosing_function_js(lines: list, hit_line: int) -> tuple:
    """
    Walk backwards from hit_line to find the enclosing JS function declaration.
    Walk forwards from there to find the closing brace.
    Returns (start_line, end_line).
    """
    # Walk back up to 80 lines to find a function declaration
    func_start = None
    for i in range(hit_line, max(-1, hit_line - 80), -1):
        if re.search(r'\bfunction\s+\w+\s*\(|^\s*(async\s+)?function\b|=\s*(async\s+)?\(.*\)\s*=>', lines[i]):
            func_start = i
            break

    if func_start is None:
        # No function found — return ±50 lines around hit
        return max(0, hit_line - 50), min(len(lines) - 1, hit_line + 50)

    # Walk forward from func_start, count braces to find closing }
    depth = 0
    func_end = hit_line
    found_open = False
    for i in range(func_start, min(len(lines), func_start + 200)):
        for ch in lines[i]:
            if ch == '{':
                depth += 1
                found_open = True
            elif ch == '}':
                depth -= 1
        if found_open and depth == 0:
            func_end = i
            break

    return func_start, func_end


def extract_enclosing_function_py(lines: list, hit_line: int) -> tuple:
    """
    Walk backwards from hit_line to find the enclosing Python def/class.
    Returns (start_line, end_line).
    """
    # Find enclosing def
    func_start = None
    hit_indent = len(lines[hit_line]) - len(lines[hit_line].lstrip())
    for i in range(hit_line, max(-1, hit_line - 100), -1):
        stripped = lines[i].lstrip()
        indent = len(lines[i]) - len(stripped)
        if stripped.startswith('def ') and indent < hit_indent:
            func_start = i
            break
        if stripped.startswith('def ') and indent == 0:
            func_start = i
            break

    if func_start is None:
        return max(0, hit_line - 50), min(len(lines) - 1, hit_line + 60)

    # Walk forward — function ends when we hit a line with same or less indentation
    base_indent = len(lines[func_start]) - len(lines[func_start].lstrip())
    func_end = func_start
    for i in range(func_start + 1, min(len(lines), func_start + 200)):
        line = lines[i]
        stripped = line.lstrip()
        if not stripped or stripped.startswith('#'):
            continue
        indent = len(line) - len(stripped)
        if indent <= base_indent and stripped and not stripped.startswith('#'):
            func_end = i - 1
            break
        func_end = i

    return func_start, func_end


def extract_context(source_text: str, keywords: list, file_type: str) -> tuple:
    """
    Find the first keyword hit, extract the enclosing function.
    Also extract a list of variable names in scope.
    Returns (context_str, scope_vars_list).
    """
    lines = source_text.splitlines()

    # Prioritise finding a FUNCTION DEFINITION matching a keyword
    # e.g. "function updateSOG" beats a random call to updateSOG() three files up
    hit_line = None
    for i, line in enumerate(lines):
        for kw in keywords:
            bare_kw = kw.split('.')[-1]  # 'navData.depth' → 'depth' for function search
            if re.search(rf'\bfunction\s+{re.escape(bare_kw)}\s*\(', line):
                hit_line = i
                break
        if hit_line is not None:
            break

    # Fall back to any keyword match (calls, assignments, element IDs, etc.)
    if hit_line is None:
        for i, line in enumerate(lines):
            for kw in keywords:
                if re.search(kw, line, re.IGNORECASE):
                    hit_line = i
                    break
            if hit_line is not None:
                break

    if hit_line is None:
        # Fallback: last 80 lines (where most insertions happen)
        start = max(0, len(lines) - 80)
        block = lines[start:]
        context = '\n'.join(f"{i+start+1}: {l}" for i, l in enumerate(block))
        return context, []

    # Extract enclosing function
    if file_type == 'py':
        start, end = extract_enclosing_function_py(lines, hit_line)
    else:
        start, end = extract_enclosing_function_js(lines, hit_line)

    func_lines = lines[start:end + 1]
    context = '\n'.join(f"{i+start+1}: {lines[i]}" for i in range(start, end + 1))

    # Also include first 15 lines (imports/globals/declarations)
    preamble = '\n'.join(f"{i+1}: {lines[i]}" for i in range(min(15, start)))
    if preamble:
        context = preamble + '\n\n... (intervening lines omitted) ...\n\n' + context

    # Extract scope variables from the function
    scope_vars = extract_scope_vars('\n'.join(func_lines), file_type)

    return context, scope_vars


def extract_scope_vars(text: str, file_type: str) -> list:
    """Extract variable/function names declared in the given code block."""
    vars_found = set()
    if file_type == 'py':
        # def method_name, self.attr, local = value
        for m in re.finditer(r'\bdef\s+(\w+)\b', text):
            vars_found.add(m.group(1))
        for m in re.finditer(r'\bself\.(\w+)\b', text):
            vars_found.add(m.group(1))
        for m in re.finditer(r'^(\s*)(\w+)\s*=\s*', text, re.MULTILINE):
            if m.group(2) not in ('True', 'False', 'None'):
                vars_found.add(m.group(2))
    else:
        # const/let/var name, function name, obj.prop
        for m in re.finditer(r'\b(?:const|let|var)\s+(\w+)\b', text):
            vars_found.add(m.group(1))
        for m in re.finditer(r'\bfunction\s+(\w+)\b', text):
            vars_found.add(m.group(1))
        for m in re.finditer(r'\b(\w+)\s*:\s*{', text):
            vars_found.add(m.group(1))
        # object property accesses: obj.prop
        for m in re.finditer(r'\b(\w+)\.(\w+)\b', text):
            vars_found.add(m.group(1))
            vars_found.add(m.group(2))

    return sorted(vars_found - KNOWN_GLOBALS)


# ── Validation ─────────────────────────────────────────────────────────────────

def parse_instruction_blocks(text: str) -> list:
    """Parse FIND_LINE/ACTION/CODE blocks from Ollama output."""
    blocks = []
    # Strip markdown fences if present
    text = re.sub(r'^```[^\n]*\n?', '', text, flags=re.MULTILINE)
    text = re.sub(r'^```\s*$', '', text, flags=re.MULTILINE)

    pattern = re.compile(
        r'FIND_LINE:\s*(.+?)\n'
        r'ACTION:\s*(INSERT_BEFORE|INSERT_AFTER|REPLACE)\s*\n'
        r'CODE:\s*\n(.*?)END_CODE',
        re.DOTALL
    )
    for m in pattern.finditer(text):
        # Strip backtick wrapping from FIND_LINE (old Ollama outputs wrapped in markdown)
        find_line = m.group(1).strip().strip('`')
        blocks.append({
            'find_line': find_line,
            'action':    m.group(2).strip(),
            'code':      m.group(3).rstrip('\n'),
            'valid':     True,
            'issues':    []
        })
    return blocks


def check_find_line(find_line: str, source_text: str) -> bool:
    """Check that FIND_LINE text exists verbatim in the source."""
    return find_line in source_text


def check_invented_vars(code: str, source_text: str, file_type: str) -> list:
    """
    Find identifiers used in generated code that:
      - Are not in source_text (so they'd be undefined at runtime)
      - Are not in KNOWN_GLOBALS
      - Are not declared within the generated code itself
    Returns list of suspicious names (likely invented variable names).
    """
    # Find identifiers declared WITHIN the generated code — these are fine to use
    declared_in_code = set()
    if file_type == 'py':
        for m in re.finditer(r'\bdef\s+(\w+)\b', code):
            declared_in_code.add(m.group(1))
        for m in re.finditer(r'^\s*(\w+)\s*=\s*', code, re.MULTILINE):
            declared_in_code.add(m.group(1))
        for m in re.finditer(r'\bfor\s+(\w+)\b', code):
            declared_in_code.add(m.group(1))
    else:
        for m in re.finditer(r'\b(?:const|let|var)\s+(\w+)\b', code):
            declared_in_code.add(m.group(1))
        for m in re.finditer(r'\bfunction\s+(\w+)\b', code):
            declared_in_code.add(m.group(1))
        for m in re.finditer(r'\bfor\s*\([^)]*\b(\w+)\b', code):
            declared_in_code.add(m.group(1))

    # Strip strings and comments before checking (prevents false positives on comment words)
    clean_code = re.sub(r'"[^"\n]*"|\'[^\'\\n]*\'|`[^`]*`', '""', code)
    clean_code = re.sub(r'//[^\n]*', '', clean_code)           # JS single-line comments
    clean_code = re.sub(r'/\*.*?\*/', '', clean_code, flags=re.DOTALL)  # JS block comments
    clean_code = re.sub(r'#[^\n]*', '', clean_code)            # Python comments

    suspicious = []

    # 1. Standalone identifiers NOT preceded by '.' (variable refs, function calls)
    candidates = set()
    for m in re.finditer(r'(?<![.\w])([a-zA-Z_$][a-zA-Z0-9_$]{4,})\b(?!\s*:)(?!\s*\()', clean_code):
        candidates.add(m.group(1))
    for m in re.finditer(r'(?<![.\w])([a-zA-Z_$][a-zA-Z0-9_$]{4,})\b\s*\(', clean_code):
        candidates.add(m.group(1))

    for name in candidates:
        if name in KNOWN_GLOBALS or name in declared_in_code or name in source_text:
            continue
        suspicious.append(name)

    # 2. window.IDENTIFIER accesses — Ollama commonly invents these
    #    e.g. window.navSpeedKnots when the real var is navData.speedOverGround
    for m in re.finditer(r'\bwindow\.([a-zA-Z_$][a-zA-Z0-9_$]{4,})\b', clean_code):
        prop = m.group(1)
        if prop in KNOWN_GLOBALS or prop in declared_in_code:
            continue
        if prop in source_text:
            continue
        suspicious.append(f'window.{prop}')

    return sorted(set(suspicious))


def syntax_check_js(code: str) -> tuple:
    """Run node --check on generated JS code. Returns (ok, error_msg)."""
    with tempfile.NamedTemporaryFile(suffix='.js', mode='w', delete=False) as f:
        f.write(code)
        tmp = f.name
    r = subprocess.run(['node', '--check', tmp], capture_output=True, text=True)
    pathlib.Path(tmp).unlink(missing_ok=True)
    return r.returncode == 0, r.stderr.strip()


def syntax_check_py(code: str) -> tuple:
    """Run py_compile on generated Python code. Returns (ok, error_msg)."""
    with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False) as f:
        f.write(code)
        tmp = f.name
    r = subprocess.run(['python3', '-m', 'py_compile', tmp], capture_output=True, text=True)
    pathlib.Path(tmp).unlink(missing_ok=True)
    return r.returncode == 0, r.stderr.strip()


def validate_blocks(blocks: list, source_text: str, source_file: str) -> list:
    """
    Validate each parsed block. Mutates block['valid'] and block['issues'].
    Returns the same list with validation results filled in.
    """
    file_type = 'py' if source_file.endswith('.py') else 'js'

    for block in blocks:
        issues = []

        # 1. FIND_LINE must exist in source
        if not check_find_line(block['find_line'], source_text):
            issues.append(f"FIND_LINE not found in file: '{block['find_line'][:70]}'")

        # 2. Invented variable check
        invented = check_invented_vars(block['code'], source_text, file_type)
        if invented:
            issues.append(f"Possible invented identifiers: {', '.join(invented[:8])}")

        # 3. Syntax check on generated code (only for REPLACE blocks — insert code
        #    may be incomplete fragments)
        if block['action'] == 'REPLACE':
            if file_type == 'py':
                ok, err = syntax_check_py(block['code'])
            else:
                ok, err = syntax_check_js(block['code'])
            if not ok and err:
                # Only fail on definite syntax errors, not incomplete fragment warnings
                if 'SyntaxError' in err or 'Unexpected token' in err:
                    issues.append(f"Syntax error: {err[:120]}")

        block['valid'] = len(issues) == 0
        block['issues'] = issues

    return blocks


# ── Correction loop ────────────────────────────────────────────────────────────

def find_similar_lines(find_line: str, source_text: str) -> list:
    """Find source lines with the most word overlap to a failed FIND_LINE."""
    words = set(find_line.strip().lower().split())
    if not words:
        return []
    scored = []
    for line in source_text.splitlines():
        stripped = line.strip()
        if not stripped or len(stripped) < 5:
            continue
        line_words = set(stripped.lower().split())
        overlap = len(words & line_words) / max(len(words), 1)
        if overlap >= 0.4:
            scored.append((overlap, stripped))
    scored.sort(key=lambda x: (-x[0], len(x[1])))
    return [l for _, l in scored[:3]]


def find_context_for_correction(block: dict, source_text: str) -> str:
    """
    Return ±15 lines of source around the best-guess location for the change.
    For FIND_LINE failures: find the closest matching line.
    For invented var failures: find lines containing the action target.
    """
    lines = source_text.splitlines()
    find_line = block['find_line']
    words = find_line.strip().split()

    best_idx, best_score = 0, 0
    for i, line in enumerate(lines):
        score = sum(1 for w in words if w in line)
        if score > best_score:
            best_score = score
            best_idx = i

    start = max(0, best_idx - 10)
    end   = min(len(lines), best_idx + 20)
    return '\n'.join(f"{i+1}: {lines[i]}" for i in range(start, end))


def generate_correction_advice(block: dict, source_text: str, scope_vars: list) -> str:
    """
    Build targeted, specific advice for each validation failure in the block.
    This is sent to Ollama so it knows exactly what to fix.
    """
    advice = []

    for issue in block['issues']:

        if 'FIND_LINE not found' in issue:
            find_line = block['find_line']
            similar = find_similar_lines(find_line, source_text)
            if similar:
                advice.append(
                    f"FIND_LINE '{find_line}' does not exist verbatim in the file.\n"
                    f"  These are the closest real lines — use one of them instead:\n"
                    + '\n'.join(f"    {l}" for l in similar)
                )
            else:
                advice.append(
                    f"FIND_LINE '{find_line}' does not exist in the file. "
                    "Look at the file context below and choose a line that IS there."
                )

        elif 'Possible invented identifiers' in issue or 'window.' in issue:
            names_str = re.sub(r'Possible invented identifiers:\s*', '', issue)
            invented_names = [n.strip() for n in names_str.split(',') if n.strip()]

            for inv in invented_names:
                bare = inv.replace('window.', '')

                # Find candidates in scope vars first
                scope_matches = [v for v in scope_vars
                                 if bare.lower() in v.lower() or v.lower() in bare.lower()]

                # Also search source text for similarly-named identifiers
                source_idents = re.findall(r'\b[a-z][a-zA-Z0-9]{4,}\b', source_text)
                source_matches = [v for v in dict.fromkeys(source_idents)
                                  if (bare.lower()[:5] in v.lower()
                                      or v.lower()[:5] in bare.lower())
                                  and v not in scope_matches][:3]

                all_suggestions = scope_matches[:3] + source_matches[:2]

                if all_suggestions:
                    advice.append(
                        f"'{inv}' does not exist in this file. "
                        f"The correct identifier is likely: {', '.join(all_suggestions)}. "
                        f"Use the exact name from the scope list."
                    )
                else:
                    advice.append(
                        f"'{inv}' does not exist. "
                        f"Only use variables from scope: {', '.join(scope_vars[:12])}"
                    )

        elif 'Syntax error' in issue:
            err = issue.replace('Syntax error:', '').strip()
            advice.append(f"Fix this syntax error in your CODE block: {err}")

    return '\n'.join(f"- {a}" for a in advice) if advice else "- Review the file context and correct the block."


def run_correction(block: dict, source_text: str, source_filename: str,
                   scope_vars: list) -> dict:
    """
    Send one failed block back to Ollama with specific advice.
    Returns a corrected block dict — valid=True if fixed, valid=False if still broken.
    """
    advice     = generate_correction_advice(block, source_text, scope_vars)
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
{', '.join(scope_vars[:30]) if scope_vars else '(see file context below)'}

## RELEVANT FILE CONTEXT (find the right FIND_LINE anchor here)
{nearby_ctx}

## YOUR TASK
Return EXACTLY ONE corrected block. Fix what went wrong. Nothing else.
No explanation. No markdown. No extra text.

FIND_LINE: <exact verbatim line from the file above>
ACTION: {block['action']}
CODE:
<corrected code>
END_CODE"""

    tprint(f"      → Asking Ollama to correct block...")
    raw = call_ollama(prompt, label=f"{source_filename}:correction")

    corrected_blocks = parse_instruction_blocks(raw)
    if not corrected_blocks:
        tprint(f"      ✗ Ollama returned no parseable block in correction response")
        block['correction_attempted'] = True
        return block

    corrected = corrected_blocks[0]
    corrected['action'] = block['action']
    corrected['correction_attempted'] = True

    corrected = validate_blocks([corrected], source_text, source_filename)[0]

    if corrected['valid']:
        tprint(f"      ✓ Ollama corrected the block — will apply")
    else:
        tprint(f"      ✗ Still invalid after correction: {corrected['issues']}")

    return corrected


# ── Apply ──────────────────────────────────────────────────────────────────────

def apply_blocks(blocks: list, source_text: str) -> tuple:
    """
    Apply valid blocks to source text.
    Returns (modified_text, applied_count, skipped_count).
    """
    lines = source_text.splitlines(keepends=True)
    applied = 0
    skipped = 0

    for block in blocks:
        if not block['valid']:
            skipped += 1
            continue

        find_line = block['find_line']
        action    = block['action']
        code      = block['code']

        # Find the line
        target_idx = None
        for i, line in enumerate(lines):
            if find_line in line:
                target_idx = i
                break

        if target_idx is None:
            block['issues'].append("FIND_LINE disappeared during multi-block apply")
            block['valid'] = False
            skipped += 1
            continue

        code_lines = [l + '\n' for l in code.splitlines()]
        if not code_lines:
            code_lines = [code + '\n']

        if action == 'INSERT_AFTER':
            lines[target_idx + 1:target_idx + 1] = code_lines
            applied += 1
        elif action == 'INSERT_BEFORE':
            lines[target_idx:target_idx] = code_lines
            applied += 1
        elif action == 'REPLACE':
            lines[target_idx:target_idx + 1] = code_lines
            applied += 1

    return ''.join(lines), applied, skipped


# ── Ollama call ────────────────────────────────────────────────────────────────

def call_ollama(prompt: str, label: str = "?") -> str:
    """Send prompt to Ollama, record call stats, return response text."""
    payload = json.dumps({
        "model":   MODEL,
        "prompt":  prompt,
        "stream":  False,
        "options": {"temperature": 0.1, "num_predict": 8192}
    }).encode()
    req = urllib.request.Request(
        OLLAMA_URL, data=payload, headers={"Content-Type": "application/json"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            response = json.loads(resp.read()).get("response", "")
    except urllib.error.URLError as e:
        tprint(f"[ERROR] Ollama unreachable: {e}")
        sys.exit(1)
    elapsed = time.time() - t0
    with _stats_lock:
        _ollama_calls.append({
            'label':          label,
            'prompt_chars':   len(prompt),
            'response_chars': len(response),
            'elapsed_s':      round(elapsed, 1),
        })
    return response


# ── Spec extraction ────────────────────────────────────────────────────────────

def extract_spec_section(spec_text: str, header: str) -> str:
    lines = spec_text.splitlines()
    start = next((i for i, l in enumerate(lines)
                  if header in l and l.startswith("##")), None)
    if start is None:
        return f"[Section '{header}' not found in spec]"
    section = []
    for line in lines[start + 1:]:
        if line.startswith("## ") and section:
            break
        section.append(line)
    return "\n".join(section).strip()


# ── Main phase runner ──────────────────────────────────────────────────────────

def run_phase(phase_name: str, do_apply: bool = False, skip_ollama: bool = False) -> dict:
    """
    Run one phase. Returns a result dict:
      {'phase', 'file', 'blocks', 'auto_applied', 'corrected', 'flagged', 'output_path'}
    """
    spec_header, source_filename, keywords = PHASES[phase_name]

    source_path = SOURCE_DIR / source_filename
    if not source_path.exists():
        print(f"[WARN] Source file not found: {source_path}")
        return {'phase': phase_name, 'file': source_filename,
                'blocks': [], 'auto_applied': 0, 'corrected': 0, 'flagged': 0,
                'output_path': None}

    source_text = source_path.read_text()
    file_type   = 'py' if source_filename.endswith('.py') else 'js'

    OUTPUT_DIR.mkdir(exist_ok=True)
    out_path = OUTPUT_DIR / (source_filename + ".instructions")

    # Always extract context and scope vars — needed for both prompt and correction loop
    context_str, scope_vars = extract_context(source_text, keywords, file_type)

    # ── Get Ollama output ──────────────────────────────────────────────────────
    if skip_ollama and out_path.exists():
        print(f"\n  [SKIP-OLLAMA] Using saved: {out_path.name}")
        raw_output = out_path.read_text()
    elif skip_ollama and not out_path.exists():
        print(f"\n  [SKIP-OLLAMA] No saved instructions for {phase_name} — skipping")
        return {'phase': phase_name, 'file': source_filename,
                'blocks': [], 'auto_applied': 0, 'corrected': 0, 'flagged': 0,
                'output_path': None}
    else:
        context_md   = CONTEXT_FILE.read_text() if CONTEXT_FILE.exists() else ""
        spec_text    = SPEC_FILE.read_text() if SPEC_FILE.exists() else ""
        spec_section = extract_spec_section(spec_text, spec_header)

        scope_note = ""
        if scope_vars:
            scope_note = (
                "\n\n## VARIABLES IN SCOPE (from the function shown above)\n"
                + ', '.join(scope_vars[:40])
                + "\nOnly use variables from this list or standard globals. "
                  "Do NOT invent new variable names."
            )

        prompt = f"""{context_md}

---

## TASK: Execute the following spec section for {source_filename}

{spec_section}

## RELEVANT CODE FROM {source_filename} (with line numbers)
{context_str}{scope_note}

## YOUR OUTPUT FORMAT
Return ONLY structured change blocks in EXACTLY this format.
No explanation. No markdown fences. No other text.

FIND_LINE: <exact verbatim text of an existing line in the file>
ACTION: INSERT_BEFORE | INSERT_AFTER | REPLACE
CODE:
<exact code — preserve indentation>
END_CODE

Multiple blocks allowed. Every FIND_LINE must exist verbatim in the file above.
"""

        tprint(f"\n[{phase_name}] Sending to Ollama ({len(prompt.splitlines())} lines)...")
        raw_output = call_ollama(prompt, label=f"{phase_name}:initial")

        if not raw_output.strip():
            tprint(f"[ERROR] Empty response from Ollama for phase: {phase_name}")
            return {'phase': phase_name, 'file': source_filename,
                    'blocks': [], 'auto_applied': 0, 'corrected': 0, 'flagged': 0,
                    'output_path': None}

        out_path.write_text(raw_output)
        tprint(f"  Instructions saved → {out_path.name}")

    # ── Parse and initial validation ───────────────────────────────────────────
    blocks = parse_instruction_blocks(raw_output)
    if not blocks:
        tprint(f"  [WARN] No FIND_LINE/ACTION/CODE blocks parsed")
        tprint(f"  Raw output preview: {raw_output[:200]}")
        return {'phase': phase_name, 'file': source_filename,
                'blocks': [], 'auto_applied': 0, 'corrected': 0, 'flagged': 0,
                'output_path': out_path}

    blocks = validate_blocks(blocks, source_text, source_filename)

    initial_invalid = sum(1 for b in blocks if not b['valid'])
    tprint(f"  Parsed {len(blocks)} block(s): "
           f"{len(blocks) - initial_invalid} valid, {initial_invalid} flagged")

    for i, b in enumerate(blocks):
        status = "OK " if b['valid'] else "ERR"
        tprint(f"    [{status}] Block {i+1}: {b['action']} @ '{b['find_line'][:50]}'")
        for issue in b['issues']:
            tprint(f"          ^ {issue}")

    # ── Correction loop (live Ollama runs only) ────────────────────────────────
    corrected_count = 0
    if not skip_ollama and initial_invalid > 0:
        tprint(f"\n  [CORRECT] {initial_invalid} block(s) failed — sending back to Ollama with advice...")
        for i, block in enumerate(blocks):
            if not block['valid']:
                tprint(f"    Block {i+1}: {block['action']} @ '{block['find_line'][:50]}'")
                corrected = run_correction(block, source_text, source_filename, scope_vars)
                blocks[i] = corrected
                if corrected['valid']:
                    corrected_count += 1

        still_invalid = sum(1 for b in blocks if not b['valid'])
        if corrected_count > 0:
            tprint(f"\n  After correction: {corrected_count} fixed, {still_invalid} still flagged")
        if still_invalid > 0:
            tprint(f"  {still_invalid} block(s) need manual review")

    final_invalid = sum(1 for b in blocks if not b['valid'])

    # ── Auto-apply ─────────────────────────────────────────────────────────────
    auto_applied = 0
    if do_apply:
        valid_blocks = [b for b in blocks if b['valid']]
        if valid_blocks:
            # Re-read source in case a previous phase in 'all' mode modified it
            source_text = source_path.read_text()
            modified, auto_applied, skipped = apply_blocks(blocks, source_text)
            source_path.write_text(modified)
            tprint(f"  Applied {auto_applied} block(s) to {source_filename}")
            if skipped:
                tprint(f"  Skipped {skipped} block(s)")

    return {
        'phase':        phase_name,
        'file':         source_filename,
        'blocks':       blocks,
        'auto_applied': auto_applied,
        'corrected':    corrected_count,
        'flagged':      final_invalid,
        'output_path':  out_path,
    }


def print_report(results: list):
    """Print end-of-run summary."""
    print("\n" + "═" * 68)
    print("  d3kOS Ollama Executor — Run Report")
    print("═" * 68)
    total_blocks    = sum(len(r['blocks']) for r in results)
    total_applied   = sum(r['auto_applied'] for r in results)
    total_corrected = sum(r.get('corrected', 0) for r in results)
    total_flagged   = sum(r['flagged'] for r in results)

    for r in results:
        mark = "✓" if r['flagged'] == 0 else "⚠"
        corr = r.get('corrected', 0)
        print(f"  {mark} {r['phase']:14s} {r['file']:24s} "
              f"blocks={len(r['blocks'])}  "
              f"applied={r['auto_applied']}  "
              f"corrected={corr}  "
              f"flagged={r['flagged']}")
        for b in r['blocks']:
            if not b['valid']:
                attempt = " (correction attempted)" if b.get('correction_attempted') else ""
                print(f"      FLAGGED{attempt}: {b['action']} @ '{b['find_line'][:45]}'")
                for issue in b['issues']:
                    print(f"               → {issue}")

    print("─" * 68)
    print(f"  Total: {total_blocks} blocks  |  "
          f"Applied: {total_applied}  |  "
          f"Ollama-corrected: {total_corrected}  |  "
          f"Manual review needed: {total_flagged}")
    if total_flagged > 0:
        print(f"\n  {total_flagged} block(s) still need manual review.")
        print("  Check ollama_output/<file>.instructions for raw output.")
    else:
        print("\n  All blocks handled — none require manual review.")

    # ── Ollama call stats (for cost log) ──────────────────────────────────────
    if _ollama_calls:
        total_calls     = len(_ollama_calls)
        total_prompt_k  = sum(c['prompt_chars'] for c in _ollama_calls) // 1000
        total_resp_k    = sum(c['response_chars'] for c in _ollama_calls) // 1000
        total_time_s    = sum(c['elapsed_s'] for c in _ollama_calls)
        initial_calls   = sum(1 for c in _ollama_calls if c['label'].endswith(':initial'))
        correction_calls = total_calls - initial_calls
        print(f"\n  Ollama calls this run:")
        print(f"    {initial_calls} initial  +  {correction_calls} corrections  =  {total_calls} total")
        print(f"    ~{total_prompt_k}k chars prompt  +  ~{total_resp_k}k chars response")
        print(f"    {total_time_s:.0f}s total inference time  |  cost: $0 (local GPU)")
        print(f"\n  Claude API cost: check console.anthropic.com → Usage → filter by today")
        print(f"  Tip: copy these stats to SESSION_LOG.md Costs section")

    print("═" * 68 + "\n")


def main():
    args       = sys.argv[1:]
    do_apply   = '--apply' in args
    skip_oll   = '--skip-ollama' in args

    # --parallel N  (default 1 = sequential)
    parallel = 1
    for i, a in enumerate(args):
        if a == '--parallel' and i + 1 < len(args):
            try:
                parallel = max(1, int(args[i + 1]))
            except ValueError:
                pass

    phases_arg = [a for a in args if not a.startswith('--')
                  and not (args[max(0, args.index(a)-1):args.index(a)] == ['--parallel']
                           if '--parallel' in args else False)]
    # Simpler: just strip --parallel and its value
    clean_args = []
    skip_next = False
    for a in args:
        if skip_next:
            skip_next = False
            continue
        if a == '--parallel':
            skip_next = True
            continue
        if not a.startswith('--'):
            clean_args.append(a)

    if not clean_args or clean_args[0] not in list(PHASES.keys()) + ['all']:
        print(f"Usage: python3 {sys.argv[0]} <phase|all> [--apply] [--skip-ollama] [--parallel N]")
        print(f"Phases: {', '.join(PHASES.keys())}, all")
        print(f"  --parallel N  run N phases concurrently (Ollama queues them; default 1)")
        sys.exit(1)

    phase_list = list(PHASES.keys()) if clean_args[0] == 'all' else [clean_args[0]]

    print(f"\nd3kOS Ollama Executor v2")
    print(f"  Model    : {MODEL}")
    print(f"  Phases   : {', '.join(phase_list)}")
    print(f"  Apply    : {'yes' if do_apply else 'no — dry run (add --apply to write changes)'}")
    print(f"  Parallel : {parallel} worker(s)")
    print(f"  Context  : {CONTEXT_FILE.name} ({'found' if CONTEXT_FILE.exists() else 'MISSING'})")

    if parallel > 1 and len(phase_list) > 1:
        # Parallel run — each phase modifies a different file, safe to parallelise
        # Note: Ollama queues requests server-side (single GPU), but validation /
        # context extraction / correction loops overlap with each other's GPU wait
        print(f"  [PARALLEL] Submitting {len(phase_list)} phases to {parallel} workers...")
        results_map = {}
        with ThreadPoolExecutor(max_workers=parallel) as executor:
            futures = {
                executor.submit(run_phase, phase, do_apply, skip_oll): phase
                for phase in phase_list
            }
            for future in as_completed(futures):
                phase = futures[future]
                results_map[phase] = future.result()
        # Restore original phase order in report
        results = [results_map[p] for p in phase_list]
    else:
        results = [run_phase(p, do_apply=do_apply, skip_ollama=skip_oll) for p in phase_list]

    print_report(results)


if __name__ == "__main__":
    main()
