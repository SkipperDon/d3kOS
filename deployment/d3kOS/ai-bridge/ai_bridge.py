"""
d3kOS AI Bridge — main service, localhost:3002

Features:
  Feature 1 — Route analysis widget (every 5 min)
  Feature 2 — Port arrival briefing (2nm trigger)
  Feature 3 — Voyage log summarization
  Feature 4 — Anchor watch AI alerts

Endpoints:
  GET  /status            health check
  GET  /stream            Server-Sent Events to dashboard
  POST /analyze-route     immediate route analysis
  POST /summarize-voyage  generate voyage summary
  POST /anchor/activate   start anchor watch
  POST /anchor/dismiss    dismiss anchor alarm
  GET  /anchor/advice     get AI corrective action
  POST /webhook/arrival   Node-RED: trigger port briefing
  POST /webhook/alert     Node-RED: push custom TTS alert
  POST /webhook/query     Node-RED: arbitrary AI query
"""

import os
import json
import queue
import logging
import threading
import time
from datetime import datetime, timezone

import requests
from flask import Flask, jsonify, request, Response
from dotenv import load_dotenv

# Load config from environment file
_ENV_PATH = os.path.join(os.path.dirname(__file__), 'config', 'ai-bridge.env')
if os.path.isfile(_ENV_PATH):
    load_dotenv(_ENV_PATH)

# Feature modules
from features.route_analyzer import RouteAnalyzer
from features.port_arrival   import PortArrivalMonitor
from features.voyage_logger  import VoyageLogger
from features.anchor_watch   import AnchorWatch
from utils                   import tts
from utils.signalk_client    import is_reachable as sk_reachable
from utils.avnav_client      import get_status as avnav_status

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
log = logging.getLogger('ai_bridge')

# ── Config ─────────────────────────────────────────────────────────────────────
PORT             = int(os.environ.get('AI_BRIDGE_PORT', 3002))
GEMINI_PROXY_URL = os.environ.get('GEMINI_PROXY_URL', 'http://localhost:3001')

app = Flask(__name__)

# ── SSE subscriber management ─────────────────────────────────────────────────
_subscribers: list[queue.Queue] = []
_subscribers_lock = threading.Lock()


def broadcast(event_type: str, data: dict):
    """Push a Server-Sent Event to all connected dashboard clients."""
    payload = f'event: {event_type}\ndata: {json.dumps(data)}\n\n'
    dead = []
    with _subscribers_lock:
        for q in _subscribers:
            try:
                q.put_nowait(payload)
            except queue.Full:
                dead.append(q)
        for q in dead:
            _subscribers.remove(q)


# ── Feature instances ──────────────────────────────────────────────────────────
route_analyzer   = RouteAnalyzer(broadcast)
port_arrival     = PortArrivalMonitor(broadcast)
voyage_logger    = VoyageLogger(broadcast)
anchor_watch     = AnchorWatch(broadcast)


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route('/status')
def status():
    """Health check — all subsystem states."""
    sk_up    = sk_reachable()
    avnav_ok = avnav_status() is not None

    try:
        gemini_resp = requests.get(f'{GEMINI_PROXY_URL}/status', timeout=3)
        gemini_up   = gemini_resp.status_code == 200
    except Exception:
        gemini_up = False

    return jsonify({
        'service':       'd3kos-ai-bridge',
        'port':          PORT,
        'timestamp':     datetime.now(timezone.utc).isoformat(),
        'signalk':       'up' if sk_up    else 'down',
        'avnav':         'up' if avnav_ok else 'down',
        'gemini_proxy':  'up' if gemini_up else 'down',
        'tts_engine':    os.environ.get('TTS_ENGINE', 'espeak-ng'),
        'tts_available': tts.is_available(),
        'subscribers':   len(_subscribers),
    })


@app.route('/stream')
def stream():
    """
    Server-Sent Events stream for dashboard.
    Each connected client gets its own queue.
    """
    def generate():
        q = queue.Queue(maxsize=50)
        with _subscribers_lock:
            _subscribers.append(q)
        # Send initial heartbeat
        yield 'event: heartbeat\ndata: {"ts": "' + datetime.now(timezone.utc).isoformat() + '"}\n\n'
        try:
            while True:
                try:
                    msg = q.get(timeout=30)
                    yield msg
                except queue.Empty:
                    # Keep connection alive
                    yield ': keepalive\n\n'
        except GeneratorExit:
            with _subscribers_lock:
                if q in _subscribers:
                    _subscribers.remove(q)

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
        },
    )


@app.route('/analyze-route', methods=['POST'])
def analyze_route():
    """Trigger immediate route analysis (from 'Analyze Now' button)."""
    route_analyzer.force_analyze()
    return jsonify({'ok': True, 'message': 'Route analysis triggered.'})


@app.route('/summarize-voyage', methods=['POST'])
def summarize_voyage():
    """
    Generate voyage summary.
    Body: {'filename': '2026-03-13.gpx'} or {} for most recent track.
    """
    data     = request.get_json(silent=True) or {}
    filename = data.get('filename')

    if filename:
        result = voyage_logger.summarize_by_filename(filename)
    else:
        result = voyage_logger.summarize_latest()

    if not result.get('ok'):
        return jsonify(result), 400

    broadcast('voyage_summary', {
        'trigger':  'manual',
        'summary':  result['summary'],
        'filename': result.get('filename', ''),
        'source':   result.get('source', 'unknown'),
    })
    return jsonify(result)


@app.route('/anchor/activate', methods=['POST'])
def anchor_activate():
    """
    Activate anchor watch.
    Body: {'radius_m': 30} — optional, uses Signal K value if omitted.
    """
    data     = request.get_json(silent=True) or {}
    radius_m = data.get('radius_m')
    if radius_m is not None:
        try:
            radius_m = float(radius_m)
        except (TypeError, ValueError):
            return jsonify({'ok': False, 'error': 'radius_m must be a number'}), 400

    result = anchor_watch.activate(radius_m)
    return jsonify(result)


@app.route('/anchor/dismiss', methods=['POST'])
def anchor_dismiss():
    """Dismiss active anchor alarm."""
    result = anchor_watch.dismiss()
    return jsonify(result)


@app.route('/anchor/advice', methods=['GET'])
def anchor_advice():
    """Get AI corrective action for current drag event."""
    result = anchor_watch.get_ai_advice()
    if result.get('ok'):
        broadcast('anchor_advice', {'advice': result['advice'], 'source': result['source']})
    return jsonify(result)


# ── Node-RED webhook endpoints ─────────────────────────────────────────────────

@app.route('/webhook/arrival', methods=['POST'])
def webhook_arrival():
    """
    Node-RED can trigger a port arrival briefing for a named destination.
    Body: {'destination': str, 'lat': float, 'lon': float}
    """
    data = request.get_json(silent=True) or {}
    dest = data.get('destination', '')
    lat  = data.get('lat', 0.0)
    lon  = data.get('lon', 0.0)

    if not dest:
        return jsonify({'ok': False, 'error': 'destination required'}), 400

    port_arrival.trigger_for_destination(dest, float(lat), float(lon))
    return jsonify({'ok': True, 'destination': dest})


@app.route('/webhook/alert', methods=['POST'])
def webhook_alert():
    """
    Node-RED can push a custom alert through TTS + screen.
    Body: {'message': str, 'severity': 'info|warning|critical'}
    """
    data     = request.get_json(silent=True) or {}
    message  = data.get('message', '').strip()
    severity = data.get('severity', 'info')

    if not message:
        return jsonify({'ok': False, 'error': 'message required'}), 400

    repeat = 2 if severity == 'critical' else 1
    tts.speak_urgent(message, repeat=repeat)

    broadcast('custom_alert', {'message': message, 'severity': severity})
    return jsonify({'ok': True})


@app.route('/webhook/query', methods=['POST'])
def webhook_query():
    """
    Node-RED can send arbitrary marine queries to AI and get a response.
    Body: {'query': str}
    Response: {'response': str, 'source': 'gemini|ollama'}
    """
    data  = request.get_json(silent=True) or {}
    query = data.get('query', '').strip()

    if not query:
        return jsonify({'ok': False, 'error': 'query required'}), 400

    try:
        resp = requests.post(
            f'{GEMINI_PROXY_URL}/ask',
            json={'prompt': query},
            timeout=60,
        )
        resp.raise_for_status()
        result = resp.json()
        return jsonify({
            'ok':       True,
            'response': result.get('response', ''),
            'source':   result.get('source', 'unknown'),
        })
    except Exception as exc:
        log.warning('webhook_query AI call failed: %s', exc)
        return jsonify({'ok': False, 'error': str(exc)}), 503


# ── HELM mute control ──────────────────────────────────────────────────────────

@app.route('/helm/mute', methods=['POST'])
def helm_mute():
    """
    Browser calls this when operator taps the HELM mute button.
    Body: {'muted': true|false}
    Immediately stops any active espeak subprocess and sets mute state.
    """
    data  = request.get_json(silent=True) or {}
    muted = bool(data.get('muted', True))
    tts.set_muted(muted)
    log.info('HELM TTS %s', 'MUTED' if muted else 'UNMUTED')
    return jsonify({'ok': True, 'muted': muted})


# ── Voyage summary list (for settings page) ────────────────────────────────────

@app.route('/voyages', methods=['GET'])
def voyage_list():
    """Return most recent 5 voyage summaries."""
    summaries = voyage_logger.list_recent_summaries(count=5)
    return jsonify({'ok': True, 'summaries': summaries})


# ── Startup ────────────────────────────────────────────────────────────────────

def _start_background_services():
    log.info('Starting AI Bridge background services...')
    route_analyzer.start()
    port_arrival.start()
    voyage_logger.start()
    anchor_watch.start()
    log.info('All background services started.')


if __name__ == '__main__':
    _start_background_services()
    log.info('d3kOS AI Bridge starting on port %d', PORT)
    app.run(
        host='0.0.0.0',
        port=PORT,
        debug=False,
        threaded=True,
    )
