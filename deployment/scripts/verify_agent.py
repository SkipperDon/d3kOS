#!/usr/bin/env python3
"""
d3kOS Verify Agent — TrueNAS independent code verifier
Port: 11436
Model: qwen2.5-coder:1.5b (local Ollama on same VM)

Role in pipeline:
  Workstation (qwen3-coder:30b) generates code
       ↓ POST /verify
  TrueNAS (qwen2.5-coder:1.5b) independently checks the code
       ↓ returns {pass, score, issues, suggestion}
  Executor uses result to accept, correct, or flag

Endpoints:
  POST /verify   — verify a generated code block
  GET  /health   — service health
  GET  /report   — last 20 verification results
  GET  /stats    — aggregate pass/fail counts

Deploy: /opt/verify-agent/verify_agent.py
Service: d3kos-verify-agent.service (port 11436)
"""

import json
import time
import logging
import urllib.request
from collections import deque
from datetime import datetime
from flask import Flask, request, jsonify

# ── Config ────────────────────────────────────────────────────────────────────

OLLAMA_URL    = "http://192.168.1.36:11434/api/generate"   # workstation GPU
VERIFY_MODEL  = "qwen3-coder:30b"                          # same high-quality model, different role
VERIFY_PORT   = 11436
OLLAMA_TIMEOUT = 120   # workstation GPU: 80-token review ~30-40s

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('/var/log/verify-agent.log'),
        logging.StreamHandler()
    ]
)
log = logging.getLogger('verify-agent')

app = Flask(__name__)
_results = deque(maxlen=20)   # rolling last-20 results
_stats   = {'pass': 0, 'fail': 0, 'error': 0, 'total_calls': 0}

# ── Verify logic ──────────────────────────────────────────────────────────────

VERIFY_PROMPT_TEMPLATE = """You are a strict code reviewer. You did NOT write this code — another AI generated it. Your job: verify it is correct.

INSTRUCTION (what the code must do):
{instruction}

CODE SUBMITTED FOR REVIEW:
{code}

SURROUNDING FILE CONTEXT (for variable name reference):
{context}

FILE: {filename}

Check these three things only:
1. Does the code correctly implement the instruction? If NO, explain what is wrong or missing.
2. Any syntax errors?
3. Any variable names used that do not appear in the context and were not declared in the code itself?

Reply in EXACTLY this format — nothing else:
PASS: YES or NO
SCORE: 0-100
ISSUE: <single line — the most critical problem, or "none">
SUGGESTION: <single line fix if PASS is NO, or "none">
"""


def call_ollama_verify(instruction: str, code: str, context: str, filename: str) -> dict:
    prompt = VERIFY_PROMPT_TEMPLATE.format(
        instruction=instruction[:800],
        code=code[:1500],
        context=context[:800],
        filename=filename,
    )
    payload = json.dumps({
        "model":   VERIFY_MODEL,
        "prompt":  prompt,
        "stream":  False,
        "options": {"temperature": 0.0, "num_predict": 80},
    }).encode()

    req = urllib.request.Request(
        OLLAMA_URL, data=payload,
        headers={"Content-Type": "application/json"}
    )
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=OLLAMA_TIMEOUT) as r:
            raw = json.loads(r.read().decode()).get('response', '').strip()
    except Exception as e:
        log.error(f"Ollama call failed: {e}")
        return {'error': str(e)}

    elapsed = round(time.time() - start, 1)
    log.info(f"Ollama response in {elapsed}s: {raw[:120]}")
    return parse_verify_response(raw, elapsed)


def parse_verify_response(raw: str, elapsed: float) -> dict:
    result = {
        'pass':       False,
        'score':      0,
        'issue':      'parse error',
        'suggestion': 'none',
        'raw':        raw,
        'elapsed_s':  elapsed,
    }
    for line in raw.splitlines():
        line = line.strip()
        if line.upper().startswith('PASS:'):
            result['pass'] = 'YES' in line.upper()
        elif line.upper().startswith('SCORE:'):
            try:
                result['score'] = int(''.join(c for c in line.split(':', 1)[1] if c.isdigit())[:3])
            except ValueError:
                pass
        elif line.upper().startswith('ISSUE:'):
            result['issue'] = line.split(':', 1)[1].strip()
        elif line.upper().startswith('SUGGESTION:'):
            result['suggestion'] = line.split(':', 1)[1].strip()
    return result


# ── Flask endpoints ───────────────────────────────────────────────────────────

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status':  'healthy',
        'model':   VERIFY_MODEL,
        'port':    VERIFY_PORT,
        'stats':   _stats,
        'timestamp': datetime.utcnow().isoformat(),
    })


@app.route('/verify', methods=['POST'])
def verify():
    body = request.get_json(force=True, silent=True) or {}
    code        = body.get('code', '')
    instruction = body.get('instruction', '')
    context     = body.get('context', '')
    filename    = body.get('filename', 'unknown')
    phase_name  = body.get('phase_name', '')

    if not code or not instruction:
        return jsonify({'error': 'code and instruction required'}), 400

    _stats['total_calls'] += 1
    log.info(f"Verify request: phase={phase_name} file={filename} code_len={len(code)}")

    verify_result = call_ollama_verify(instruction, code, context, filename)

    if 'error' in verify_result:
        _stats['error'] += 1
        record = {
            'phase_name': phase_name,
            'filename':   filename,
            'pass':       None,
            'score':      None,
            'issue':      verify_result['error'],
            'suggestion': 'none',
            'timestamp':  datetime.utcnow().isoformat(),
            'error':      True,
        }
        _results.append(record)
        # Return pass=None so executor treats it as a soft failure (log, don't block)
        return jsonify({
            'pass':       None,
            'score':      None,
            'issue':      verify_result['error'],
            'suggestion': 'none',
            'model':      VERIFY_MODEL,
            'error':      True,
        })

    passed = verify_result['pass']
    _stats['pass' if passed else 'fail'] += 1

    record = {
        'phase_name': phase_name,
        'filename':   filename,
        'pass':       passed,
        'score':      verify_result['score'],
        'issue':      verify_result['issue'],
        'suggestion': verify_result['suggestion'],
        'elapsed_s':  verify_result['elapsed_s'],
        'timestamp':  datetime.utcnow().isoformat(),
    }
    _results.append(record)

    log.info(f"  → {'PASS' if passed else 'FAIL'} score={verify_result['score']} issue={verify_result['issue']}")

    return jsonify({
        'pass':       passed,
        'score':      verify_result['score'],
        'issue':      verify_result['issue'],
        'suggestion': verify_result['suggestion'],
        'model':      VERIFY_MODEL,
        'elapsed_s':  verify_result['elapsed_s'],
    })


@app.route('/report', methods=['GET'])
def report():
    return jsonify({
        'results':   list(_results),
        'stats':     _stats,
        'model':     VERIFY_MODEL,
        'timestamp': datetime.utcnow().isoformat(),
    })


@app.route('/stats', methods=['GET'])
def stats():
    total = _stats['total_calls'] or 1
    return jsonify({
        'total_calls':  _stats['total_calls'],
        'pass':         _stats['pass'],
        'fail':         _stats['fail'],
        'error':        _stats['error'],
        'pass_rate_pct': round(_stats['pass'] / total * 100, 1),
        'model':        VERIFY_MODEL,
    })


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    log.info(f"Verify Agent starting — model={VERIFY_MODEL} port={VERIFY_PORT}")
    app.run(host='0.0.0.0', port=VERIFY_PORT, debug=False)
