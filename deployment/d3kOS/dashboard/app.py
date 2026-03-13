"""
d3kOS Dashboard Server
Serves the main marine navigation hub at http://localhost:3000

Port assignments (from d3kos-config.env):
  Dashboard:    localhost:3000  (this app)
  AvNav:        localhost:8080
  Gemini Proxy: localhost:3001
  Signal K:     localhost:8099
  OpenPlotter:  localhost:8081  (infrastructure — not referenced here)
  Ollama:       192.168.1.36:11434 (LAN AI server)

CRITICAL: Signal K WebSocket is ws://localhost:8099 — NOT ws://localhost:3000.
"""
from flask import Flask, render_template, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), 'config', 'd3kos-config.env'))

app = Flask(__name__)

AVNAV_PORT    = os.getenv('AVNAV_PORT',    '8080')
GEMINI_PORT   = os.getenv('GEMINI_PORT',   '3001')
SIGNALK_PORT  = os.getenv('SIGNALK_PORT',  '8099')
OLLAMA_HOST   = os.getenv('OLLAMA_HOST',   '192.168.1.36:11434')
VESSEL_NAME   = os.getenv('VESSEL_NAME',   'Vessel')
HOME_PORT_VAL = os.getenv('HOME_PORT',     'Home Port')


def check_internet() -> bool:
    """Lightweight connectivity probe — no user data sent."""
    try:
        requests.get('http://captive.apple.com', timeout=3)
        return True
    except requests.RequestException:
        return False


def check_service(port: str) -> bool:
    """Return True if a local service answers on the given port."""
    try:
        requests.get(f'http://localhost:{port}', timeout=2)
        return True
    except requests.RequestException:
        return False


def check_ollama() -> bool:
    """Return True if the Ollama LAN server is reachable."""
    try:
        requests.get(f'http://{OLLAMA_HOST}/api/tags', timeout=3)
        return True
    except requests.RequestException:
        return False


@app.route('/')
def index():
    return render_template(
        'index.html',
        avnav_port=AVNAV_PORT,
        gemini_port=GEMINI_PORT,
        vessel_name=VESSEL_NAME,
    )


@app.route('/status')
def status():
    """
    Live system status — polled by the frontend every 30 s.
    Checks: internet, AvNav (:8080), Gemini proxy (:3001),
            Signal K (:8099), Ollama (LAN 192.168.1.36:11434).

    Phase 5 will add: ai_bridge — check_service('3002')
    """
    return jsonify({
        'internet': check_internet(),
        'avnav':    check_service(AVNAV_PORT),    # localhost:8080
        'gemini':   check_service(GEMINI_PORT),   # localhost:3001
        'signalk':  check_service(SIGNALK_PORT),  # localhost:8099
        'ollama':   check_ollama(),               # 192.168.1.36:11434
    })


@app.route('/settings')
def settings():
    """Settings & Help page — placeholder. Full build in Phase 4."""
    return render_template(
        'settings.html',
        avnav_port=AVNAV_PORT,
        gemini_port=GEMINI_PORT,
        signalk_port=SIGNALK_PORT,
        vessel_name=VESSEL_NAME,
        home_port=HOME_PORT_VAL,
    )


@app.route('/offline')
def offline():
    return render_template('offline.html')


@app.route('/launch/opencpn', methods=['POST'])
def launch_opencpn():
    """
    Trigger OpenCPN via Node-RED.
    Proxies to existing Node-RED flow at localhost:1880/launch-opencpn
    (added in v0.9.2 — see nginx proxy block).
    """
    try:
        r = requests.post('http://127.0.0.1:1880/launch-opencpn', timeout=5)
        return jsonify({'ok': True, 'status': r.status_code})
    except requests.RequestException as exc:
        return jsonify({'ok': False, 'error': str(exc)}), 502


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=False)
