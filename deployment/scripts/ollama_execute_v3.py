#!/usr/bin/env python3
"""
d3kOS Ollama Executor v3 — Generic, feature-agnostic

Reads phases.json from a feature directory. No per-feature Python edits needed.
Claude writes the spec + phases.json. Ollama writes the code.

Usage:
  python3 ollama_execute_v3.py <feature_dir> <phase|all>            # dry run
  python3 ollama_execute_v3.py <feature_dir> <phase|all> --apply    # apply valid blocks
  python3 ollama_execute_v3.py <feature_dir> <phase|all> --skip-ollama --apply

Feature directory must contain:
  phases.json       — list of phase definitions
  feature_spec.md   — full spec (Ollama reads the relevant section per phase)
  pi_source/        — copies of the Pi source files to be modified (or symlinks)
"""

import sys, re, json, time, pathlib, tempfile, subprocess, threading, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

OLLAMA_URL       = "http://192.168.1.36:11434/api/generate"
OLLAMA_EMBED_URL = "http://192.168.1.36:11434/api/embed"
MODEL            = "qwen3-coder:30b"
TIMEOUT          = 300

VERIFY_URL       = "http://192.168.1.103:11436/verify"   # TrueNAS independent verifier
VERIFY_TIMEOUT   = 120                                    # 1.5b model, short prompts ~60-90s
VERIFY_ENABLED   = True                                   # set False to bypass verifier

RAG_CHROMA_PATH  = str(pathlib.Path.home() / "rag-stack/chroma_data")
RAG_VENV_SITE    = str(pathlib.Path.home() / "rag-stack/.venv/lib/python3.12/site-packages")
CONTEXT_FILE     = pathlib.Path(__file__).parent.parent / "docs/helm_os_context.md"

_stats_lock  = threading.Lock()
_print_lock  = threading.Lock()
_ollama_calls = []

def tprint(*a, **k):
    with _print_lock: print(*a, **k)


# ── Known globals (unchanged from v2) ─────────────────────────────────────────

KNOWN_GLOBALS = {
    'const','let','var','function','return','if','else','for','while','do',
    'switch','case','break','continue','new','this','typeof','instanceof',
    'class','import','export','default','from','async','await','try','catch',
    'finally','throw','in','of','delete','void','true','false','null',
    'undefined','NaN','Infinity','JSON','Math','Date','parseInt','parseFloat',
    'isNaN','isFinite','Promise','Error','Object','Array','String','Number',
    'Boolean','Symbol','Map','Set','WeakMap','RegExp','Proxy','Reflect',
    'Units','window','document','navigator','location','history',
    'localStorage','sessionStorage','console','alert','confirm','prompt',
    'fetch','WebSocket','XMLHttpRequest','FormData','URLSearchParams',
    'setTimeout','setInterval','clearTimeout','clearInterval',
    'requestAnimationFrame','cancelAnimationFrame','performance',
    'CustomEvent','Event','MutationObserver','IntersectionObserver',
    'nextElementSibling','previousElementSibling','parentElement','children',
    'firstChild','lastChild','childNodes','nodeType','nodeName',
    'classList','className','textContent','innerHTML','innerText',
    'style','dataset','attributes','offsetWidth','offsetHeight',
    'scrollTop','scrollLeft','clientWidth','clientHeight',
    'getElementById','querySelector','querySelectorAll',
    'getElementsByClassName','getElementsByTagName',
    'addEventListener','removeEventListener','dispatchEvent',
    'getAttribute','setAttribute','removeAttribute','hasAttribute',
    'appendChild','removeChild','insertBefore','replaceChild','cloneNode',
    'contains','closest','matches','focus','blur','click','submit',
    'add','remove','toggle','replace','trim','split','join','push','pop',
    'shift','unshift','slice','splice','sort','filter','map','forEach',
    'find','findIndex','includes','some','every','reduce','keys','values',
    'entries','assign','create','freeze','parse','stringify','floor','ceil',
    'round','abs','max','min','toFixed','toString','valueOf','hasOwnProperty',
    'call','apply','bind','event','data','value','values','error','errors',
    'result','results','callback','response','request','options','config',
    'settings','item','items','index','element','elements','target','source',
    'input','output','name','type','path','url','href','src','text','html',
    'node','body','head','form','link',
    'temperature','pressure','speed','depth','fuel','distance','length',
    'weight','displacement','getPreference','setPreference','toDisplay',
    'toC','toF','toBar','toPSI','toKmh','toMph','toKm','toNm','toMeters',
    'toFeet','toLiters','toGallons','toKg','toLb','toCi','unit',
    'measurementSystemChanged',
    'self','cls','None','True','False','def','return','import','from',
    'class','if','elif','else','for','while','try','except','finally',
    'with','as','pass','raise','yield','lambda','global','nonlocal',
    'assert','del','print','len','str','int','float','bool','list','dict',
    'tuple','set','type','open','range','enumerate','zip','map','filter',
    'sorted','reversed','sum','min','max','abs','round','repr','isinstance',
    'issubclass','hasattr','getattr','setattr','delattr','callable','iter',
    'next','super','property','staticmethod','classmethod','format','input',
    'vars','dir','help','id','json','load','loads','dump','dumps',
    'system','metric','imperial','psi','bar','fahrenheit','celsius',
    'knots','kmh','mph','status','parts','response','formatted',
    'preference','category','message','content','body','headers',
    'gemini','proxy','requests','payload','elapsed','timeout',
    'manual_context','boat_status','query_text','api_key','model',
    'candidates','history','session_history','start_time','elapsed_ms',
    # Python exceptions and keyword args
    'TypeError','ValueError','KeyError','IndexError','AttributeError',
    'RuntimeError','Exception','StopIteration','OSError','IOError',
    'indent','encoding','errors','mode','newline',
    # Camera-specific
    'cameras','camera','cam','active','connected','has_frame','camera_id',
    'camera_name','camera_ip','recording','bow','stern','port','starboard',
    'position','assign','direction','unassigned',
}


# ── RAG ───────────────────────────────────────────────────────────────────────

def query_rag(source_filename, keywords, n=4):
    try:
        import chromadb
        from chromadb.config import Settings as CS
    except ImportError:
        sys.path.insert(0, RAG_VENV_SITE)
        try:
            import chromadb
            from chromadb.config import Settings as CS
        except ImportError:
            return ""
    try:
        client = chromadb.PersistentClient(path=RAG_CHROMA_PATH,
                                            settings=CS(anonymized_telemetry=False))
        col   = client.get_collection("helm_os_source")
        query = f"functions variables {source_filename} {' '.join(keywords[:4])}"
        emb_payload = json.dumps({"model":"nomic-embed-text","input":query}).encode()
        req = urllib.request.Request(OLLAMA_EMBED_URL, data=emb_payload,
                                     headers={"Content-Type":"application/json"})
        with urllib.request.urlopen(req, timeout=15) as r:
            emb = json.loads(r.read())["embeddings"][0]
        res  = col.query(query_embeddings=[emb], n_results=n,
                         include=["documents","metadatas"])
        docs, metas = res["documents"][0], res["metadatas"][0]
        if not docs: return ""
        chunks = [f"[{pathlib.Path(m.get('source','?')).name}]\n{d}"
                  for d, m in zip(docs, metas)]
        tprint(f"  [RAG] {len(chunks)} chunk(s) for {source_filename}")
        return "\n\n---\n\n".join(chunks)
    except Exception as e:
        tprint(f"  [RAG] unavailable: {e}")
        return ""


# ── Context extraction (unchanged from v2) ───────────────────────────────────

def _extract_fn_js(lines, hit):
    for i in range(hit, max(-1, hit-80), -1):
        if re.search(r'\bfunction\s+\w+\s*\(|^\s*(async\s+)?function\b|=\s*(async\s+)?\(.*\)\s*=>', lines[i]):
            fs = i; break
    else:
        return max(0, hit-50), min(len(lines)-1, hit+50)
    depth, fe, found = 0, hit, False
    for i in range(fs, min(len(lines), fs+200)):
        for ch in lines[i]:
            if ch=='{': depth+=1; found=True
            elif ch=='}': depth-=1
        if found and depth==0: fe=i; break
    return fs, fe

def _extract_fn_py(lines, hit):
    fs, hi = None, len(lines[hit])-len(lines[hit].lstrip())
    for i in range(hit, max(-1, hit-100), -1):
        s = lines[i].lstrip(); ind = len(lines[i])-len(s)
        if s.startswith('def ') and (ind<hi or ind==0): fs=i; break
    if fs is None: return max(0, hit-50), min(len(lines)-1, hit+60)
    bi = len(lines[fs])-len(lines[fs].lstrip()); fe = fs
    for i in range(fs+1, min(len(lines), fs+200)):
        l = lines[i]; s = l.lstrip()
        if not s or s.startswith('#'): continue
        if len(l)-len(s) <= bi and s and not s.startswith('#'): fe=i-1; break
        fe = i
    return fs, fe

def extract_context(source_text, keywords, file_type):
    lines = source_text.splitlines(); hit = None
    for i,l in enumerate(lines):
        for kw in keywords:
            bare = kw.split('.')[-1]
            if re.search(rf'\bfunction\s+{re.escape(bare)}\s*\(', l):
                hit=i; break
        if hit is not None: break
    if hit is None:
        for i,l in enumerate(lines):
            for kw in keywords:
                if re.search(kw, l, re.IGNORECASE): hit=i; break
            if hit is not None: break
    if hit is None:
        start=max(0,len(lines)-80)
        return '\n'.join(f"{i+start+1}: {l}" for i,l in enumerate(lines[start:])), []
    fn = _extract_fn_py if file_type=='py' else _extract_fn_js
    s,e = fn(lines, hit)
    ctx    = '\n'.join(f"{i+1}: {lines[i]}" for i in range(s,e+1))
    preamb = '\n'.join(f"{i+1}: {lines[i]}" for i in range(min(15,s)))
    if preamb: ctx = preamb + '\n\n... (intervening lines omitted) ...\n\n' + ctx
    scope_vars = _scope_vars('\n'.join(lines[s:e+1]), file_type)
    return ctx, scope_vars

def _scope_vars(text, ft):
    v = set()
    if ft=='py':
        for m in re.finditer(r'\bdef\s+(\w+)\b', text): v.add(m.group(1))
        for m in re.finditer(r'\bself\.(\w+)\b', text): v.add(m.group(1))
        for m in re.finditer(r'^(\s*)(\w+)\s*=\s*', text, re.MULTILINE):
            if m.group(2) not in ('True','False','None'): v.add(m.group(2))
    else:
        for m in re.finditer(r'\b(?:const|let|var)\s+(\w+)\b', text): v.add(m.group(1))
        for m in re.finditer(r'\bfunction\s+(\w+)\b', text): v.add(m.group(1))
        for m in re.finditer(r'\b(\w+)\s*:\s*{', text): v.add(m.group(1))
        for m in re.finditer(r'\b(\w+)\.(\w+)\b', text): v.add(m.group(1)); v.add(m.group(2))
    return sorted(v - KNOWN_GLOBALS)


# ── Validation ────────────────────────────────────────────────────────────────

def parse_blocks(text):
    text = re.sub(r'^```[^\n]*\n?','',text,flags=re.MULTILINE)
    text = re.sub(r'^```\s*$','',text,flags=re.MULTILINE)
    ALIASES = {'AFTER':'INSERT_AFTER','INSERT_AFTER':'INSERT_AFTER',
               'BEFORE':'INSERT_BEFORE','INSERT_BEFORE':'INSERT_BEFORE','REPLACE':'REPLACE'}
    blocks = []
    for m in re.compile(
            r'FIND_LINE:\s*(.+?)\n(?:END_LINE:\s*(.+?)\n)?ACTION:\s*(INSERT_BEFORE|INSERT_AFTER|REPLACE|BEFORE|AFTER)\s*\n'
            r'CODE:\s*\n(.*?)END_CODE', re.DOTALL).finditer(text):
        blocks.append({'find_line': m.group(1).strip().strip('`'),
                       'end_line':  (m.group(2) or '').strip().strip('`'),
                       'action': ALIASES.get(m.group(3).strip(), m.group(3).strip()),
                       'code': m.group(4).rstrip('\n'),
                       'valid':True,'issues':[],'correction_attempted':False,'corrected':False})
    return blocks

def check_invented(code, source, ft):
    declared = set()
    if ft=='py':
        for m in re.finditer(r'\bdef\s+(\w+)\b', code): declared.add(m.group(1))
        for m in re.finditer(r'\bdef\s+\w+\s*\(([^)]*)\)', code):
            for p in m.group(1).split(','):
                p=p.strip().lstrip('*').split('=')[0].strip()
                if p and p.isidentifier(): declared.add(p)
        for m in re.finditer(r'^\s*(\w+)\s*=\s*', code, re.MULTILINE): declared.add(m.group(1))
        for m in re.finditer(r'\bfor\s+(\w+)\b', code): declared.add(m.group(1))
    else:
        for m in re.finditer(r'\b(?:const|let|var)\s+(\w+)\b', code): declared.add(m.group(1))
        for m in re.finditer(r'\bfunction\s+(\w+)\b', code): declared.add(m.group(1))
        for m in re.finditer(r'\bfunction\s*\w*\s*\(([^)]*)\)', code):
            for p in m.group(1).split(','):
                p=p.strip().lstrip('.').split('=')[0].strip()
                if p and p.isidentifier(): declared.add(p)
        for m in re.finditer(r'\(([^)]*)\)\s*=>', code):
            for p in m.group(1).split(','):
                p=p.strip().lstrip('.').split('=')[0].strip()
                if p and p.isidentifier(): declared.add(p)
        for m in re.finditer(r'\bfor\s*\([^)]*\b(\w+)\b', code): declared.add(m.group(1))
    clean = re.sub(r'"[^"\n]*"|\'[^\'\n]*\'|`[^`]*`','""',code)
    clean = re.sub(r'//[^\n]*','',clean)
    clean = re.sub(r'/\*.*?\*/','',clean,flags=re.DOTALL)
    clean = re.sub(r'#[^\n]*','',clean)
    sus = set()
    for m in re.finditer(r'(?<![.\w])([a-zA-Z_$][a-zA-Z0-9_$]{4,})\b(?!\s*:)(?!\s*\()', clean):
        sus.add(m.group(1))
    for m in re.finditer(r'(?<![.\w])([a-zA-Z_$][a-zA-Z0-9_$]{4,})\b\s*\(', clean):
        sus.add(m.group(1))
    return sorted(n for n in sus if n not in KNOWN_GLOBALS and n not in declared and n not in source)

def syntax_js(code):
    with tempfile.NamedTemporaryFile(suffix='.js',mode='w',delete=False) as f:
        f.write(code); tmp=f.name
    r = subprocess.run(['node','--check',tmp],capture_output=True,text=True)
    pathlib.Path(tmp).unlink(missing_ok=True)
    return (True,'') if r.returncode==0 else (False,(r.stderr or r.stdout).strip().split('\n')[0])

def syntax_py(code):
    with tempfile.NamedTemporaryFile(suffix='.py',mode='w',delete=False) as f:
        f.write(code); tmp=f.name
    r = subprocess.run([sys.executable,'-m','py_compile',tmp],capture_output=True,text=True)
    pathlib.Path(tmp).unlink(missing_ok=True)
    return (True,'') if r.returncode==0 else (False,(r.stderr or r.stdout).strip())

def validate(blocks, source, ft):
    for b in blocks:
        b['valid']=True; b['issues']=[]
        if b['find_line'] not in source:
            b['valid']=False
            b['issues'].append(f"FIND_LINE not found: {b['find_line']!r}")
        if b.get('end_line') and b['end_line'] not in source:
            b['valid']=False
            b['issues'].append(f"END_LINE not found: {b['end_line']!r}")
        inv = check_invented(b['code'], source, ft)
        if inv:
            b['valid']=False
            b['issues'].append(f"Invented identifiers: {', '.join(inv)}")
        if ft=='js' and '<script' not in b['code']:
            ok,err = syntax_js(b['code'])
            if not ok: b['valid']=False; b['issues'].append(f"JS syntax: {err}")
        if ft=='py':
            ok,err = syntax_py(b['code'])
            if not ok: b['valid']=False; b['issues'].append(f"Python syntax: {err}")
    return blocks


# ── Correction loop ───────────────────────────────────────────────────────────

def _similar_lines(find_line, source):
    words = set(find_line.lower().split())
    if len(words)<2: return []
    scored = [(len(words & set(l.lower().split())), l.strip())
              for l in source.splitlines()
              if len(words & set(l.lower().split()))>=2]
    return [l for _,l in sorted(scored,reverse=True)[:3]]

def _nearby_ctx(block, source):
    lines=source.splitlines(); best=None; bov=0; words=set(block['find_line'].lower().split())
    for i,l in enumerate(lines):
        ov=len(words & set(l.lower().split()))
        if ov>bov: bov=ov; best=i
    if best is None: return '\n'.join(f"{i+1}: {l}" for i,l in enumerate(lines[-30:],len(lines)-29))
    s=max(0,best-15); e=min(len(lines),best+15)
    return '\n'.join(f"{i+1}: {lines[i]}" for i in range(s,e))

def run_correction(block, source, filename, scope_vars):
    advice = []
    for issue in block['issues']:
        if 'FIND_LINE not found' in issue:
            sim = _similar_lines(block['find_line'], source)
            advice.append("The FIND_LINE does not exist. Use one of these real lines:\n" +
                          '\n'.join(f'  "{l}"' for l in sim) if sim else
                          "FIND_LINE not found. Pick a real line from the context below.")
        elif 'Invented' in issue:
            advice.append(f"These names don't exist in the file: {issue.split(':',1)[-1].strip()}. "
                          f"Use only names from scope list below.")
        elif 'syntax' in issue.lower():
            advice.append(f"Fix this syntax error: {issue}")
    prompt = f"""Your instruction block for {filename} failed validation.

FAILED BLOCK:
FIND_LINE: {block['find_line']}
ACTION: {block['action']}
CODE:
{block['code']}
END_CODE

ISSUES:
{chr(10).join('- '+e for e in block['issues'])}

HOW TO FIX:
{chr(10).join(advice) or 'Fix the issues above.'}

SCOPE VARIABLES (use only these):
{', '.join(scope_vars[:30])}

NEARBY FILE CONTEXT:
{_nearby_ctx(block, source)}

Return EXACTLY ONE corrected block. Nothing else.
FIND_LINE: <exact verbatim line from the file>
ACTION: {block['action']}
CODE:
<corrected code>
END_CODE"""
    resp = call_ollama(prompt, label=f'correction:{filename}')
    corrected = parse_blocks(resp)
    return corrected[0] if corrected else None


# ── TrueNAS Verify call ───────────────────────────────────────────────────────

def call_verify(code, instruction, context, filename, phase_name=''):
    """
    POST generated code to TrueNAS verify agent (qwen2.5-coder:1.5b).
    Returns dict with keys: pass (bool|None), score (int), issue (str), suggestion (str).
    Returns None if verifier is disabled or unreachable — caller must treat as non-blocking.
    """
    if not VERIFY_ENABLED:
        return None
    payload = json.dumps({
        'code':        code,
        'instruction': instruction,
        'context':     context,
        'filename':    filename,
        'phase_name':  phase_name,
    }).encode()
    req = urllib.request.Request(VERIFY_URL, data=payload,
                                  headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=VERIFY_TIMEOUT) as r:
            result = json.loads(r.read().decode())
        verdict = 'PASS' if result.get('pass') else ('FAIL' if result.get('pass') is False else 'ERROR')
        tprint(f"  [Verify] {verdict} score={result.get('score','?')} issue={result.get('issue','')}")
        return result
    except Exception as e:
        tprint(f"  [Verify] unreachable: {e} — continuing without verify")
        return None


# ── Ollama call ───────────────────────────────────────────────────────────────

def call_ollama(prompt, label=''):
    start = time.time()
    data = json.dumps({"model":MODEL,"prompt":prompt,"stream":False}).encode()
    req = urllib.request.Request(OLLAMA_URL, data=data,
                                  headers={"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            response = json.loads(r.read().decode()).get('response','')
    except Exception as e:
        tprint(f"  [Ollama ERROR] {e}"); return ''
    elapsed = round(time.time()-start, 1)
    with _stats_lock:
        _ollama_calls.append({'label':label,'prompt_chars':len(prompt),
                               'response_chars':len(response),'elapsed_s':elapsed})
    tprint(f"  [Ollama] {label}: {len(response)} chars in {elapsed}s")
    return response


# ── Phase runner ──────────────────────────────────────────────────────────────

def _apply_block(current, b):
    """Apply a single validated block to source text. Returns updated text."""
    if b['action'] == 'REPLACE' and b.get('end_line'):
        fi = current.find(b['find_line'])
        ei = current.find(b['end_line'], fi) + len(b['end_line'])
        return current[:fi] + b['code'] + current[ei:]
    elif b['action'] == 'REPLACE':
        return current.replace(b['find_line'], b['code'], 1)
    elif b['action'] == 'INSERT_AFTER':
        return current.replace(b['find_line'], b['find_line'] + '\n' + b['code'], 1)
    elif b['action'] == 'INSERT_BEFORE':
        return current.replace(b['find_line'], b['code'] + '\n' + b['find_line'], 1)
    return current


def _strip_fences(text):
    text = re.sub(r'^```[^\n]*\n?', '', text, flags=re.MULTILINE)
    return re.sub(r'^```\s*$', '', text, flags=re.MULTILINE).strip()


def run_phase(phase_cfg, feature_dir, apply=False, skip_ollama=False):
    name        = phase_cfg['name']
    src_file    = phase_cfg['source_file']
    spec_section= phase_cfg['spec_section']
    keywords    = phase_cfg.get('keywords', [])
    replace_exact = phase_cfg.get('replace_exact', False)

    feature_dir = pathlib.Path(feature_dir)
    source_path = feature_dir / 'pi_source' / src_file
    spec_path   = feature_dir / 'feature_spec.md'
    out_path    = feature_dir / 'ollama_output' / f'{name}.instructions'
    ft          = 'py' if src_file.endswith('.py') else 'js'

    tprint(f"\n{'='*60}\nPHASE: {name} | FILE: {src_file}"
           f"{' [EXACT]' if replace_exact else ''}\n{'='*60}")

    if not source_path.exists():
        tprint(f"  [ERROR] Source not found: {source_path}"); return
    if not spec_path.exists():
        tprint(f"  [ERROR] feature_spec.md not found: {spec_path}"); return

    source_text = source_path.read_text()
    ctx, scope_vars = extract_context(source_text, keywords, ft)
    tprint(f"  Context: {len(ctx)} chars | Scope vars: {scope_vars[:8]}")

    # ── REPLACE_EXACT mode: anchors from phases.json, Ollama writes CODE only ──
    if replace_exact:
        exact_find   = phase_cfg.get('find_line', '')
        exact_end    = phase_cfg.get('end_line', '')
        exact_action = phase_cfg.get('action', 'REPLACE')

        if exact_find not in source_text:
            tprint(f"  [ERROR] phases.json find_line not in source: {exact_find!r}"); return
        if exact_end and exact_end not in source_text:
            tprint(f"  [ERROR] phases.json end_line not in source: {exact_end!r}"); return

        if skip_ollama and out_path.exists():
            tprint(f"  [SKIP-OLLAMA] Loading {out_path.name}")
            code = _strip_fences(out_path.read_text())
        elif skip_ollama:
            tprint(f"  [SKIP-OLLAMA] No saved output for {name}"); return
        else:
            spec_text = spec_path.read_text()
            pat = re.compile(rf'^## {re.escape(spec_section)}.*?(?=^## |\Z)', re.MULTILINE|re.DOTALL)
            m   = pat.search(spec_text)
            spec_section_text = m.group(0).strip() if m else f"[Section not found]"

            context_file = CONTEXT_FILE.read_text() if CONTEXT_FILE.exists() else ''
            rag = query_rag(src_file, keywords)
            rag_block = ("\n\n## BACKGROUND REFERENCE\n" + rag) if rag else ""

            if exact_action == 'INSERT_BEFORE':
                anchor_desc = (f"Insert your code immediately BEFORE this line (do NOT include this line in your output — it is preserved automatically):\n`{exact_find}`")
            elif exact_action == 'INSERT_AFTER':
                anchor_desc = (f"Insert your code immediately AFTER this line (do NOT include this line in your output — it is preserved automatically):\n`{exact_find}`")
            else:
                anchor_desc = (f"Replace the block from:\n`{exact_find}`\nthrough:\n`{exact_end}`\nwith your code.")

            prompt = f"""{context_file}

---

## TASK: {name.upper()} — {src_file}

## SPEC:
{spec_section_text}{rag_block}

## CURRENT FILE CONTEXT (existing code for reference):
{ctx}

## VARIABLES IN SCOPE (use these exact names only):
{', '.join(scope_vars[:30]) if scope_vars else '(see context above)'}

## YOUR JOB:
{anchor_desc}

IMPORTANT: The SPEC section above contains a code block (between ``` markers) showing EXACTLY what to write. Write that code. Do not reproduce the existing code from CURRENT FILE CONTEXT — write the NEW code from the SPEC.

Write ONLY the code — no FIND_LINE, no END_LINE, no ACTION, no END_CODE marker.
Do not wrap in markdown fences.
"""
            tprint(f"  Calling Ollama ({len(prompt)} chars)...")
            response = call_ollama(prompt, label=name)
            if not response:
                tprint(f"  [ERROR] No response"); return
            code = _strip_fences(response)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(code)
            tprint(f"  Saved → {out_path.name}")

        b = {'find_line': exact_find, 'end_line': exact_end,
             'action': exact_action, 'code': code,
             'valid': True, 'issues': [], 'correction_attempted': False, 'corrected': False}
        source_text = source_path.read_text()
        [b] = validate([b], source_text, ft)

        # ── TrueNAS independent verify ─────────────────────────────────────────
        if b['valid'] and not skip_ollama:
            vr = call_verify(code=b['code'],
                             instruction=spec_section_text[:800],
                             context=ctx[:800],
                             filename=src_file,
                             phase_name=name)
            if vr and vr.get('pass') is False:
                b['valid'] = False
                issue_msg = f"Verify: {vr.get('issue','failed')} (score={vr.get('score',0)})"
                b['issues'].append(issue_msg)
                tprint(f"  [Verify] FAIL → adding to correction: {issue_msg}")

        if not b['valid'] and not skip_ollama:
            tprint(f"  [CORRECTION] {b['issues']}")
            corr_prompt = f"""Your code for {src_file} failed validation.

ISSUES:
{chr(10).join('- ' + e for e in b['issues'])}

ORIGINAL CODE:
{b['code']}

SCOPE VARIABLES:
{', '.join(scope_vars[:30])}

Rewrite ONLY the corrected code. No FIND_LINE, no markers, no fences.
"""
            resp2 = call_ollama(corr_prompt, label=f'correction:{src_file}')
            if resp2:
                b['code'] = _strip_fences(resp2)
                b['correction_attempted'] = True
                [b] = validate([b], source_text, ft)
                if b['valid']:
                    tprint(f"  [CORRECTION] Fixed!")
                    b['corrected'] = True
                else:
                    tprint(f"  [CORRECTION] Still invalid: {b['issues']}")

        valid_flag = '✓' if b['valid'] else '✗'
        tprint(f"\n  RESULT: {valid_flag} | corrected: {b.get('corrected',False)}")
        if not b['valid']:
            for i in b['issues']: tprint(f"    → {i}")

        if apply and b['valid']:
            tprint(f"\n  Applying...")
            current = source_path.read_text()
            source_path.write_text(_apply_block(current, b))
            tprint(f"  ✓ Written to {source_path}")
        elif apply:
            tprint(f"  No valid block to apply.")
        return

    # ── Standard mode ──────────────────────────────────────────────────────────
    if skip_ollama and out_path.exists():
        tprint(f"  [SKIP-OLLAMA] Loading {out_path.name}")
        response = out_path.read_text()
    elif skip_ollama:
        tprint(f"  [SKIP-OLLAMA] No saved output for {name}"); return
    else:
        spec_text = spec_path.read_text()
        pattern = re.compile(rf'^## {re.escape(spec_section)}.*?(?=^## |\Z)',
                              re.MULTILINE|re.DOTALL)
        m = pattern.search(spec_text)
        spec_section_text = m.group(0).strip() if m else f"[Section '{spec_section}' not found]"

        context_file = CONTEXT_FILE.read_text() if CONTEXT_FILE.exists() else ''
        rag = query_rag(src_file, keywords)
        rag_block = ("\n\n## BACKGROUND REFERENCE (do NOT copy FIND_LINE or END_LINE from here — use CURRENT FILE CONTEXT only)\n" + rag) if rag else ""

        prompt = f"""{context_file}

---

## TASK: {name.upper()} — {src_file}

## SPEC:
{spec_section_text}{rag_block}

## CURRENT FILE CONTEXT (area to modify):
{ctx}

## VARIABLES IN SCOPE (use these exact names only):
{', '.join(scope_vars[:30]) if scope_vars else '(see context above)'}

## OUTPUT FORMAT — REQUIRED:
FIND_LINE must be copied exactly from CURRENT FILE CONTEXT above (not from BACKGROUND REFERENCE).
FIND_LINE must not be a comment (no //, #, <!--).
FIND_LINE must not be a bare {{ or }}.
For REPLACE of a multi-line block, add END_LINE with the last line of the block to remove.
Do NOT wrap output in markdown code fences.

FIND_LINE: <exact line from CURRENT FILE CONTEXT>
END_LINE: <last line of block to replace — omit if replacing single line>
ACTION: INSERT_AFTER | INSERT_BEFORE | REPLACE
CODE:
<your code here>
END_CODE
"""
        tprint(f"  Calling Ollama ({len(prompt)} chars)...")
        response = call_ollama(prompt, label=name)
        if response:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(response)
            tprint(f"  Saved → {out_path.name}")

    if not response:
        tprint(f"  [ERROR] No response"); return

    blocks = parse_blocks(response)
    tprint(f"  Parsed {len(blocks)} block(s)")
    if not blocks:
        tprint(f"  [WARNING] No FIND_LINE/ACTION/CODE blocks\n  Response:\n{response[:500]}"); return

    source_text = source_path.read_text()
    blocks = validate(blocks, source_text, ft)

    if not skip_ollama:
        # ── TrueNAS verify pass for each valid block ───────────────────────────
        spec_text_for_verify = spec_path.read_text() if spec_path.exists() else ''
        for b in blocks:
            if b['valid']:
                vr = call_verify(code=b['code'],
                                 instruction=spec_text_for_verify[:800],
                                 context=ctx[:800],
                                 filename=src_file,
                                 phase_name=name)
                if vr and vr.get('pass') is False:
                    b['valid'] = False
                    issue_msg = f"Verify: {vr.get('issue','failed')} (score={vr.get('score',0)})"
                    b['issues'].append(issue_msg)
                    tprint(f"  [Verify] FAIL → adding to correction: {issue_msg}")

        for b in blocks:
            if not b['valid'] and not b['correction_attempted']:
                tprint(f"  [CORRECTION] {b['issues']}")
                b['correction_attempted'] = True
                fixed = run_correction(b, source_text, src_file, scope_vars)
                if fixed:
                    [fb] = validate([fixed], source_text, ft)
                    if fb['valid']:
                        tprint(f"  [CORRECTION] Fixed!")
                        b.update(fb); b['corrected']=True
                    else:
                        tprint(f"  [CORRECTION] Still invalid: {fb['issues']}")

    valid   = [b for b in blocks if b['valid']]
    invalid = [b for b in blocks if not b['valid']]
    tprint(f"\n  RESULT: {len(valid)}/{len(blocks)} valid | "
           f"{sum(1 for b in blocks if b.get('corrected'))} corrected | {len(invalid)} flagged")
    for b in invalid:
        tprint(f"    ✗ {b['find_line']!r}")
        for i in b['issues']: tprint(f"      → {i}")

    if apply and valid:
        tprint(f"\n  Applying {len(valid)} block(s)...")
        current = source_path.read_text()
        for b in valid:
            current = _apply_block(current, b)
        source_path.write_text(current)
        tprint(f"  ✓ Written to {source_path}")
    elif apply:
        tprint(f"  No valid blocks to apply.")
    else:
        for i,b in enumerate(valid):
            tprint(f"\n  Block {i+1}: {b['action']} at {b['find_line']!r}")
            tprint(f"  Preview: {b['code'][:200]}...")


# ── Report ────────────────────────────────────────────────────────────────────

def print_report():
    with _stats_lock: calls = list(_ollama_calls)
    if not calls: return
    print(f"\n{'='*60}\nOLLAMA SUMMARY ({len(calls)} calls)\n{'='*60}")
    for c in calls:
        print(f"  {c['label']:35s} {c['prompt_chars']:6d}p → {c['response_chars']:6d}r  {c['elapsed_s']:.1f}s")
    print(f"  {'TOTAL':35s} {sum(c['prompt_chars'] for c in calls):6d}p → "
          f"{sum(c['response_chars'] for c in calls):6d}r  {sum(c['elapsed_s'] for c in calls):.1f}s")
    print(f"\n  Ollama generator  (qwen3-coder:30b  @ 192.168.1.36 workstation): $0.00")
    print(f"  Ollama verifier   (qwen2.5-coder:1.5b @ 192.168.1.103 TrueNAS): $0.00")
    # Fetch verify stats from TrueNAS
    try:
        with urllib.request.urlopen(
            urllib.request.Request("http://192.168.1.103:11436/stats"), timeout=5
        ) as r:
            vs = json.loads(r.read().decode())
        print(f"  Verify stats: {vs['total_calls']} calls | "
              f"{vs['pass']} pass / {vs['fail']} fail / {vs['error']} error "
              f"({vs['pass_rate_pct']}% pass rate)")
    except Exception:
        print(f"  Verify stats: unavailable (TrueNAS verify agent offline)")
    print(f"  Claude API: console.anthropic.com → Usage → today")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    import argparse
    p = argparse.ArgumentParser(description='d3kOS Ollama Executor v3')
    p.add_argument('feature_dir', help='Path to feature directory (contains phases.json + feature_spec.md)')
    p.add_argument('phase', help='Phase name or "all"')
    p.add_argument('--apply', action='store_true')
    p.add_argument('--skip-ollama', action='store_true')
    p.add_argument('--parallel', type=int, default=1)
    args = p.parse_args()

    feature_dir = pathlib.Path(args.feature_dir)
    phases_file = feature_dir / 'phases.json'
    if not phases_file.exists():
        print(f"ERROR: phases.json not found in {feature_dir}"); sys.exit(1)

    all_phases = json.loads(phases_file.read_text())
    phases_to_run = all_phases if args.phase=='all' else \
                    [p for p in all_phases if p['name']==args.phase]
    if not phases_to_run:
        print(f"Phase '{args.phase}' not found. Available: {[p['name'] for p in all_phases]}")
        sys.exit(1)

    run_fn = lambda cfg: run_phase(cfg, feature_dir, args.apply, args.skip_ollama)

    if args.parallel > 1 and len(phases_to_run) > 1:
        with ThreadPoolExecutor(max_workers=args.parallel) as ex:
            futures = {ex.submit(run_fn, cfg): cfg['name'] for cfg in phases_to_run}
            for f in as_completed(futures):
                try: f.result()
                except Exception as e: tprint(f"  [ERROR in {futures[f]}] {e}")
    else:
        for cfg in phases_to_run:
            run_fn(cfg)

    print_report()

if __name__ == '__main__':
    main()
