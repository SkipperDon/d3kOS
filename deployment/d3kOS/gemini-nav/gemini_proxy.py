"""
d3kOS Gemini Marine AI Proxy — localhost:3001
Routes marine queries to:
  1. Gemini API (https://generativelanguage.googleapis.com) — when online
  2. Ollama (http://192.168.1.36:11434)                    — offline fallback

Privacy rules:
  - Never store user query text
  - Cache stores: timestamp, source, token count, response text only
  - Cache max: 10 entries (CACHE_MAX)
"""
from flask import Flask, request, jsonify, render_template
import requests
import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / 'config' / 'gemini.env')
# api-keys.env is written by the onboarding wizard and holds GEMINI_API_KEY
# (override=False so gemini.env takes precedence if both have the key)
load_dotenv(Path(__file__).parent.parent / 'dashboard' / 'config' / 'api-keys.env', override=False)

app = Flask(__name__)


@app.after_request
def add_cors(response):
    response.headers['Access-Control-Allow-Origin']  = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GEMINI_MODEL   = os.getenv('GEMINI_MODEL',   'gemini-2.5-flash')
OLLAMA_URL     = os.getenv('OLLAMA_URL',     'http://192.168.1.36:11434')
OLLAMA_MODEL   = os.getenv('OLLAMA_MODEL',   'qwen3-coder:30b')
VESSEL_NAME    = os.getenv('VESSEL_NAME',    'Your Vessel')
HOME_PORT      = os.getenv('HOME_PORT',      'Home Port')

CACHE_FILE = Path(__file__).parent / 'cache' / 'response_cache.json'
CACHE_MAX  = 10

SYSTEM_PROMPT = (
    f"You are a marine navigation assistant for a vessel named {VESSEL_NAME}, "
    f"home port {HOME_PORT}. You help with:\n"
    "- Port information: facilities, depth, fuel docks, customs, entry procedures\n"
    "- Destination planning: waypoints, anchorages, marina contacts, provisioning\n"
    "- Passage safety: weather windows, tidal timing, hazards\n"
    "- Local knowledge: points of interest, fuel prices, marine services\n"
    "- Emergency contacts: coast guard, tow services, medical\n\n"
    "Respond concisely and practically — this is used at sea.\n"
    "Politely refuse if a query is not marine-related.\n"
    "Always note if information may be outdated and should be verified on official charts."
)


def load_cache() -> list:
    try:
        if CACHE_FILE.exists():
            return json.loads(CACHE_FILE.read_text())
    except Exception:
        pass
    return []


def save_cache(entries: list) -> None:
    """Persist last CACHE_MAX entries — never store query text."""
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(entries[-CACHE_MAX:], indent=2))


def check_internet() -> bool:
    """Lightweight connectivity probe — no user data sent."""
    try:
        requests.get('http://captive.apple.com', timeout=3)
        return True
    except Exception:
        return False


def check_ollama() -> bool:
    """Confirm Ollama LAN server is responding."""
    try:
        r = requests.get(f'{OLLAMA_URL}/api/tags', timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def query_gemini(user_message: str) -> dict:
    """
    Send query to Gemini API.
    Endpoint: generativelanguage.googleapis.com/v1beta/models/{model}:generateContent
    Returns: {text, tokens, source}
    """
    url = (
        f'https://generativelanguage.googleapis.com/v1beta/models/'
        f'{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}'
    )
    payload = {
        'contents': [{'parts': [{'text': user_message}]}],
        'systemInstruction': {'parts': [{'text': SYSTEM_PROMPT}]},
        'generationConfig': {'maxOutputTokens': 800},
    }
    r = requests.post(url, json=payload, timeout=20)
    r.raise_for_status()
    data   = r.json()
    text   = data['candidates'][0]['content']['parts'][0]['text']
    tokens = data.get('usageMetadata', {}).get('totalTokenCount', 0)
    return {'text': text, 'tokens': tokens, 'source': 'gemini'}


def query_ollama(user_message: str) -> dict:
    """
    Send query to Ollama via /api/chat (chat format — required for qwen3-coder).
    Endpoint: http://192.168.1.36:11434/api/chat
    Returns: {text, tokens, source}
    """
    url = f'{OLLAMA_URL}/api/chat'
    payload = {
        'model':  OLLAMA_MODEL,
        'stream': False,
        'messages': [
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user',   'content': user_message},
        ],
    }
    r = requests.post(url, json=payload, timeout=120)
    r.raise_for_status()
    data = r.json()
    text = data.get('message', {}).get('content', '')
    tokens = (
        data.get('prompt_eval_count', 0) +
        data.get('eval_count', 0)
    )
    return {'text': text, 'tokens': tokens, 'source': 'ollama'}


@app.route('/')
def chat_ui():
    return render_template('chat.html', vessel=VESSEL_NAME, model=GEMINI_MODEL)


@app.route('/status')
def status():
    """Health check endpoint — polled by dashboard connectivity-check.js."""
    return jsonify({
        'online':     check_internet(),
        'ollama':     check_ollama(),
        'gemini_key': bool(GEMINI_API_KEY),
        'model':      GEMINI_MODEL,
        'ollama_model': OLLAMA_MODEL,
    })


@app.route('/ask', methods=['POST'])
def ask():
    """
    Handle a marine query.
    Routing: Gemini (online + key) → Ollama (LAN fallback) → 503
    Privacy: NEVER log or cache query text (CLAUDE.md hard rule).
    """
    body = request.get_json()
    if not body or 'message' not in body:
        return jsonify({'error': 'No message provided'}), 400

    user_message = body['message'].strip()
    if not user_message:
        return jsonify({'error': 'Empty message'}), 400

    result = None
    error  = None

    # Route 1: Gemini (online + key present)
    if check_internet() and GEMINI_API_KEY:
        try:
            result = query_gemini(user_message)
        except Exception as e:
            error = f'Gemini error: {e}'

    # Route 2: Ollama fallback
    if result is None and check_ollama():
        try:
            result = query_ollama(user_message)
        except Exception as e:
            error = f'Ollama error: {e}'

    if result is None:
        return jsonify({
            'error':  'No AI service available. Check internet or Ollama at 192.168.1.36:11434.',
            'detail': error,
        }), 503

    # Cache: response text + metadata ONLY — never query text
    cache = load_cache()
    cache.append({
        'timestamp': int(time.time()),
        'source':    result['source'],
        'tokens':    result['tokens'],
        'response':  result['text'],
    })
    save_cache(cache)

    return jsonify({
        'response': result['text'],
        'source':   result['source'],
        'tokens':   result['tokens'],
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001, debug=False)
