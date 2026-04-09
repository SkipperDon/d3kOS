#!/usr/bin/env python3
"""
TDD — Voice keyword classification: classify_simple_query()
Bug: natural speech sensor queries and Vosk-drifted transcriptions were
falling through to Gemini/RAG instead of the instant rule-based path.

Run BEFORE fix: 13+ failures expected.
Run AFTER fix:  all 37 should pass.

Usage: python3 test_query_handler.py
Exit code: 0 = all pass, 1 = one or more failures.
"""

import importlib
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

# ── Bootstrap (mock Pi-only dependencies) ─────────────────────────────────────
for _mod in ('signalk_client', 'pdf_processor', 'requests', 'dbus'):
    sys.modules[_mod] = MagicMock()

sys.path.insert(0, str(Path(__file__).parent))

_FAKE_CONFIG = json.dumps({
    'providers': {
        'openrouter': {'api_key': '', 'default_model': 'gpt-4'},
        'ollama': {
            'enabled': False, 'default_model': '',
            'api_endpoint': '', 'temperature': 0.7, 'timeout': 5000
        }
    }
})

with patch('builtins.open', mock_open(read_data=_FAKE_CONFIG)):
    import query_handler as _qh
    importlib.reload(_qh)
    _h = _qh.AIQueryHandler(no_rag=True)

# ── Test cases ─────────────────────────────────────────────────────────────────

# Queries that MUST return a sensor category (instant rule-based response)
SHOULD_MATCH = [
    # Temperature — Don's natural speech + Vosk drift variants
    ('coolant temperature',              'temperature'),
    ('what is range of coolant',         'temperature'),
    ('what is the coolant temperature',  'temperature'),
    ('coolant',                          'temperature'),
    ('temperature',                      'temperature'),
    ('how hot',                          'temperature'),
    ('engine temp',                      'temperature'),
    ('water temperature',                'temperature'),
    ('current temp',                     'temperature'),
    # RPM — bare word and natural forms
    ('rpm',                              'rpm'),
    ('what is the rpm',                  'rpm'),
    ('engine speed',                     'rpm'),
    ('engine revolutions',               'rpm'),
    # Status / state — Don's natural speech
    ('what is the engine status',        'status'),
    ('what is the engine state',         'status'),
    ('what is the state of the engine',  'status'),
    ('engine check',                     'status'),
    ('all systems',                      'status'),
    # Navigation — 'which' must not be blocked by procedure_keywords
    ('which way am i heading',           'heading'),
    ('which way am i going',             'heading'),
    ('heading',                          'heading'),
    ('direction',                        'heading'),
    ('bearing',                          'heading'),
    ('compass',                          'heading'),
    # Single-word sensor triggers
    ('oil',                              'oil'),
    ('oil pressure',                     'oil'),
    ('fuel',                             'fuel'),
    ('battery',                          'battery'),
    ('voltage',                          'battery'),
    ('speed',                            'speed'),
    ('knots',                            'speed'),
    ('how fast',                         'speed'),
    ('hours',                            'hours'),
    ('engine hours',                     'hours'),
    ('boost',                            'boost'),
    ('turbo',                            'boost'),
]

# Queries that MUST return None (→ Gemini for diagnosis, or → RAG for knowledge)
MUST_BE_NONE = [
    # Diagnostic — 'overheating' confirmed → Gemini (option B, user decision)
    ('the engine is overheating',                None),
    ('why is my coolant temperature so high',    None),
    ('why is my rpm fluctuating',                None),
    ('should i be concerned about the temp',     None),
    ('what causes white smoke',                  None),
    ('is it normal for the engine to run hot',   None),
    # Procedure — must reach RAG
    ('how do i change my oil',                   None),
    ('how to flush the coolant',                 None),
    ('replace the fuel filter',                  None),
    ('what type of oil should i use',            None),
    # RAG knowledge queries — no sensor match
    ('what is the walleye limit for lake erie',  None),
    ('ontario size limit for bass',              None),
]

# ── Runner ─────────────────────────────────────────────────────────────────────

def run():
    passes = 0
    failures = 0

    print('=== SHOULD MATCH ===')
    for phrase, expected in SHOULD_MATCH:
        got = _h.classify_simple_query(phrase)
        ok = got == expected
        passes += ok
        failures += not ok
        print(f'  [{"PASS" if ok else "FAIL"}] {phrase!r:48s} -> {got!r}')

    print()
    print('=== MUST BE NONE (→ Gemini / RAG) ===')
    for phrase, _ in MUST_BE_NONE:
        got = _h.classify_simple_query(phrase)
        ok = got is None
        passes += ok
        failures += not ok
        print(f'  [{"PASS" if ok else "FAIL"}] {phrase!r:48s} -> {got!r}')

    print()
    print(f'Result: {passes} passed, {failures} failed')
    return failures


if __name__ == '__main__':
    sys.exit(run())
