"""
d3kOS Gemini Marine AI Proxy — localhost:3001
Routes marine queries to:
  1. Gemini API (https://generativelanguage.googleapis.com) — when online
  2. 503 response — when offline (no local LLM fallback)

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
VESSEL_NAME    = os.getenv('VESSEL_NAME',    'Your Vessel')
HOME_PORT      = os.getenv('HOME_PORT',      'Home Port')

CACHE_FILE = Path(__file__).parent / 'cache' / 'response_cache.json'
CACHE_MAX  = 10

SYSTEM_PROMPT = (
    f"You are the AI assistant for a vessel named {VESSEL_NAME}, "
    f"home port {HOME_PORT}. You assist the skipper with all aspects of vessel operation:\n"
    "- Engine diagnostics: troubleshooting overheating, oil pressure, starting problems, unusual noises\n"
    "- Electrical systems: battery voltage, charging, shore power, inverters, circuit problems\n"
    "- Mechanical systems: fuel, cooling, raw water, bilge, through-hulls, steering\n"
    "- Navigation: waypoints, anchorages, port facilities, fuel docks, customs, depth, tides\n"
    "- Passage planning: weather windows, tidal timing, hazards, marina contacts, provisioning\n"
    "- Safety: emergency procedures, coast guard contacts, tow services, medical, distress signals\n"
    "- Maintenance: service intervals, winterizing, zincs, antifouling, rigging checks\n"
    "- On-board systems: watermaker, generator, refrigeration, NMEA, chart plotter, AIS\n\n"
    "Respond concisely and practically — this assistant is used at sea on the helm display.\n"
    "Give direct actionable answers. If the skipper describes a problem, diagnose it and give steps.\n"
    "Politely redirect only if a query has no connection to boating or vessel operation.\n"
    "Always note when information may be outdated and should be verified with official sources."
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



@app.route('/')
def chat_ui():
    return render_template('chat.html', vessel=VESSEL_NAME, model=GEMINI_MODEL)


@app.route('/status')
def status():
    """Health check endpoint — polled by dashboard connectivity-check.js."""
    return jsonify({
        'online':     check_internet(),
        'gemini_key': bool(GEMINI_API_KEY),
        'model':      GEMINI_MODEL,
    })


@app.route('/ask', methods=['POST'])
def ask():
    """
    Handle a marine query.
    Routing: Gemini (online + key) → 503 (no Ollama fallback — Pi cannot run LLMs)
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


    if result is None:
        return jsonify({
            'error':  'Gemini AI unavailable. Check internet connection and API key.',
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
