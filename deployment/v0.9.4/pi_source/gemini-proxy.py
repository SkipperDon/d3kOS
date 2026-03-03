#!/usr/bin/env python3
"""
d3kOS Gemini API Proxy
Version: 0.9.4
Port: 8097
Proxies requests to Google Gemini API with d3kOS-specific system context.
Keeps API key on Pi (never exposed to browser).
"""
import json
import os
import time
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

API_KEYS_FILE = '/opt/d3kos/config/api-keys.json'
GEMINI_BASE_URL = 'https://generativelanguage.googleapis.com/v1beta'

D3KOS_SYSTEM_CONTEXT = """You are Helm, the AI assistant for d3kOS — an AI-powered marine
electronics system installed on a boat. You help boaters with:
- Engine monitoring and diagnostics (RPM, oil pressure, temperature, fuel)
- Navigation assistance and route planning
- Safety information and maritime regulations
- Weather interpretation for marine conditions
- General boating questions and advice

Keep responses concise and appropriate for hands-free voice use (1-3 sentences max).
Use clear, calm language — the user may be operating a vessel.
If asked about engine data, note that live data comes from NMEA2000 sensors.
"""


def load_api_keys() -> dict:
    try:
        with open(API_KEYS_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def save_api_keys(data: dict):
    keys = load_api_keys()
    keys.update(data)
    os.makedirs(os.path.dirname(API_KEYS_FILE), exist_ok=True)
    with open(API_KEYS_FILE, 'w') as f:
        json.dump(keys, f, indent=2)
    os.chmod(API_KEYS_FILE, 0o600)


def get_gemini_key() -> str:
    return load_api_keys().get('gemini_api_key', '')


def get_gemini_model() -> str:
    return load_api_keys().get('gemini_model', 'gemini-2.5-flash')


@app.route('/gemini/chat', methods=['POST'])
def gemini_chat():
    data = request.get_json(force=True) or {}
    user_message = data.get('message', '').strip()
    context = data.get('context', {})  # Optional boat status context
    session_history = data.get('history', [])  # Optional conversation history

    if not user_message:
        return jsonify({'error': 'message is required'}), 400

    api_key = get_gemini_key()
    if not api_key:
        return jsonify({'error': 'Gemini API key not configured. Set in Settings.'}), 503

    model = get_gemini_model()

    # Build system prompt with optional boat status
    system_prompt = D3KOS_SYSTEM_CONTEXT
    if context:
        system_prompt += f"\n\nCurrent boat status: {json.dumps(context)}"

    # Build conversation contents
    contents = []
    for h in session_history[-6:]:  # Keep last 6 turns for context
        contents.append({'role': h['role'], 'parts': [{'text': h['text']}]})
    contents.append({'role': 'user', 'parts': [{'text': user_message}]})

    payload = {
        'contents': contents,
        'systemInstruction': {'parts': [{'text': system_prompt}]},
        'generationConfig': {
            'maxOutputTokens': 512,
            'temperature': 0.4,
            'topP': 0.8
        }
    }

    url = f'{GEMINI_BASE_URL}/models/{model}:generateContent?key={api_key}'

    try:
        start = time.time()
        r = requests.post(url, json=payload, timeout=15)
        elapsed = round(time.time() - start, 2)

        if r.status_code != 200:
            return jsonify({
                'error': f'Gemini API error: {r.status_code}',
                'detail': r.text[:500]
            }), 502

        r_data = r.json()
        candidates = r_data.get('candidates', [])
        if not candidates:
            return jsonify({'error': 'No response from Gemini'}), 502

        parts = candidates[0].get('content', {}).get('parts', [])
        if not parts:
            return jsonify({'error': 'Gemini returned no text (thinking used all tokens — try again)'}), 502
        response_text = parts[0]['text']
        return jsonify({
            'response': response_text,
            'model': model,
            'elapsed_seconds': elapsed,
            'source': 'gemini'
        })

    except requests.Timeout:
        return jsonify({'error': 'Gemini API timeout (15s)'}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/gemini/health', methods=['GET'])
def gemini_health():
    api_key = get_gemini_key()
    configured = bool(api_key and len(api_key) > 10)
    return jsonify({
        'status': 'ok',
        'service': 'gemini-proxy',
        'version': '0.9.4',
        'gemini_configured': configured,
        'model': get_gemini_model(),
        'key_preview': (api_key[:8] + '...') if configured else 'not set'
    })


@app.route('/gemini/test', methods=['GET'])
def gemini_test():
    """Test Gemini connectivity with a simple hello."""
    api_key = get_gemini_key()
    if not api_key:
        return jsonify({'error': 'API key not configured'}), 503
    model = get_gemini_model()
    url = f'{GEMINI_BASE_URL}/models/{model}:generateContent?key={api_key}'
    try:
        r = requests.post(url, json={
            'contents': [{'role': 'user', 'parts': [{'text': 'Say "Gemini connected" and nothing else.'}]}],
            'generationConfig': {'maxOutputTokens': 200}
        }, timeout=15)
        if r.status_code == 200:
            candidate = r.json().get('candidates', [{}])[0]
            parts = candidate.get('content', {}).get('parts', [])
            text = parts[0]['text'].strip() if parts else 'Connected (no text — increase token limit)'
            return jsonify({'success': True, 'response': text, 'model': model})
        return jsonify({'success': False, 'error': r.text[:200]}), 502
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/gemini/config', methods=['GET'])
def get_config():
    keys = load_api_keys()
    api_key = keys.get('gemini_api_key', '')
    return jsonify({
        'gemini_configured': bool(api_key),
        'gemini_model': keys.get('gemini_model', 'gemini-1.5-flash'),
        'key_set': bool(api_key)
    })


@app.route('/gemini/config', methods=['POST'])
def set_config():
    data = request.get_json(force=True) or {}
    updates = {}
    if 'gemini_api_key' in data:
        updates['gemini_api_key'] = data['gemini_api_key']
    if 'gemini_model' in data:
        if data['gemini_model'] not in ['gemini-2.0-flash', 'gemini-2.5-flash', 'gemini-2.5-pro']:
            return jsonify({'error': 'Invalid model name'}), 400
        updates['gemini_model'] = data['gemini_model']
    if updates:
        save_api_keys(updates)
    return jsonify({'success': True, 'config': load_api_keys()})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8097, debug=False)
