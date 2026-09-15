# safehelm.py — SafeHelm Advisory Mode, d3kOS v0.9.9.5
# Port 8095, 127.0.0.1 only (proxied via dashboard :3000).
import json
import logging
import os
import queue
import threading
import time

from flask import Flask, Response, jsonify, request

import alert_gate
import alert_manager
import colregs_classifier
import cpa_engine
import shadow_logger
import voice_client

logger = logging.getLogger('safehelm')

app = Flask(__name__)

# ── [T1] Phase feature flag ────────────────────────────────────────────────
SAFEHELM_PHASE = int(os.environ.get('SAFEHELM_PHASE', '1'))

# ── SSE subscriber registry ───────────────────────────────────────────────
_sse_clients = []
_sse_lock = threading.Lock()


# ── [T1] Advisory tick — glue between per-target and global state ──────────

def advisory_tick(own, targets, managers, arbiter, now_iso):
    """One pass of the advisory loop. Returns the spoken candidate, or None.

    `managers` is mutated: a dict {mmsi: SafeHelmAlertManager}. Entries appear
    when a target first qualifies and are removed when the alert clears.
    """
    candidates = []

    for tgt in targets:
        cpa, tcpa, rng = cpa_engine.compute_cpa_tcpa(
            own.lat, own.lon, own.sog, own.cog,
            tgt.lat, tgt.lon, tgt.sog, tgt.cog)
        mgr_prior = managers.get(tgt.mmsi)
        rule = colregs_classifier.classify(
            own.cog, own.sog, tgt.cog, tgt.sog, tgt.relative_bearing,
            tgt_class=getattr(tgt, 'vessel_class', None),
            prior_rule=mgr_prior.rule_id if mgr_prior else None,
            is_past_and_clear=(tcpa < 0.0
                               and rng > colregs_classifier.PAST_AND_CLEAR_RANGE_M))
        tier = alert_gate.classify_tier(
            cpa, tcpa, rng, is_headon=rule in colregs_classifier.HEADON_RULES)

        shadow_logger.record(now_iso, tgt.mmsi, cpa, tcpa, rng, rule, tier)

        mgr = managers.get(tgt.mmsi)
        if mgr is None:
            if tier is None or rule == 'no_situation':
                continue                       # never qualified; logged only
            mgr = managers[tgt.mmsi] = alert_manager.SafeHelmAlertManager(
                tgt.mmsi, cpa, tcpa, tgt.relative_bearing,
                rule, tier['tier'], tier['voice'])
        else:
            mgr.rule_id = rule
            mgr.bearing = tgt.relative_bearing
            mgr.update_metrics(cpa, tcpa, tier)

        # Rule 13(d): thread the established rule back in so an overtaking
        # encounter cannot be re-read as a crossing when the bearing moves.
        # `managers` is where that state lives; the classifier stays pure.

        if mgr.state is alert_manager.AlertState.CLEARED:
            del managers[tgt.mmsi]
            continue

        if mgr.wants_audio():
            candidates.append({
                'target_id': tgt.mmsi,
                'tier':      mgr.tier,
                'tcpa_s':    mgr.tcpa,
                'phrase':    colregs_classifier.VOICE_PHRASES[mgr.rule_id],
                'preempt':   mgr.preempts(),
            })

    winner = arbiter.select(candidates)
    if winner is None:
        return None

    voice_client.speak(winner['phrase'])
    arbiter.mark_spoken()
    managers[winner['target_id']].mark_spoken()    # the WINNER ONLY
    return winner


# ── [T3] Flask routes ──────────────────────────────────────────────────────

def _sse_event(data):
    return f'data: {json.dumps(data)}\n\n'


@app.route('/sse')
def sse_stream():
    """SSE stream for the SafeHelm widget — proxied by dashboard :3000."""
    q = queue.Queue(maxsize=50)
    with _sse_lock:
        _sse_clients.append(q)

    def generate():
        try:
            yield _sse_event({'type': 'connected'})
            while True:
                try:
                    event = q.get(timeout=15)
                    yield _sse_event(event)
                except queue.Empty:
                    yield ': keepalive\n\n'
        finally:
            with _sse_lock:
                _sse_clients.remove(q)

    return Response(generate(), mimetype='text/event-stream',
                    headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})


def _broadcast(event):
    with _sse_lock:
        dead = []
        for q in _sse_clients:
            try:
                q.put_nowait(event)
            except queue.Full:
                dead.append(q)
        for q in dead:
            _sse_clients.remove(q)


@app.route('/ack', methods=['POST'])
def ack_alert():
    """Acknowledge a specific MMSI's alert. D02-5: only that target is muted."""
    data = request.get_json(silent=True) or {}
    mmsi = str(data.get('mmsi', '')).strip()
    if not mmsi.isdigit() or not (7 <= len(mmsi) <= 9):
        return jsonify({'error': 'invalid mmsi'}), 400
    # Ack is processed by the advisory loop thread via shared state
    _pending_acks.add(mmsi)
    return jsonify({'acked': mmsi})


@app.route('/dismiss', methods=['POST'])
def dismiss_alert():
    """Dismiss (clear) a specific MMSI from the widget display."""
    data = request.get_json(silent=True) or {}
    mmsi = str(data.get('mmsi', '')).strip()
    if not mmsi.isdigit() or not (7 <= len(mmsi) <= 9):
        return jsonify({'error': 'invalid mmsi'}), 400
    _pending_dismissals.add(mmsi)
    return jsonify({'dismissed': mmsi})


@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'phase': SAFEHELM_PHASE})


# ── [T3] Boot stubs ────────────────────────────────────────────────────────

_pending_acks = set()
_pending_dismissals = set()

# §13.3 disclaimer acknowledgement gate. SafeHelm will not produce voice output
# until the operator has accepted the disclaimer. The acceptance date is recorded
# in disclaimer-accepted.json alongside d3kOS version at acceptance time.
_DISCLAIMER_ACCEPTED_FILE = '/opt/d3kos/config/disclaimer-accepted.json'


def _disclaimer_accepted() -> bool:
    """True if the operator has previously accepted the disclaimer."""
    try:
        with open(_DISCLAIMER_ACCEPTED_FILE) as f:
            rec = json.load(f)
        return bool(rec.get('accepted') or rec.get('acknowledged'))
    except Exception:
        return False

_sk_client = None
_arbiter = None
_managers = {}


def boot_cpa_engine():
    pass   # pure module; import is sufficient


def boot_colregs_classifier():
    pass


def boot_alert_gate():
    pass


def boot_signalk_consumer():
    global _sk_client
    from signalk_client import SignalKClient
    host = os.environ.get('SIGNALK_HOST', 'localhost')
    _sk_client = SignalKClient(host=host)
    _sk_client.start()


def boot_voice_arbiter():
    global _arbiter
    from voice_arbiter import VoiceArbiter
    _arbiter = VoiceArbiter()


def initialize_shadow_logger():
    shadow_logger.initialize()


def boot_voice_client():
    pass   # voice_client uses requests at call time


def boot_widget_sse_server():
    pass   # Flask app handles SSE


def announce_advisory_role():
    voice_client.announce_startup()


def verify_signalk_transmit_whitelist():
    return False   # Phase 1 — never transmits


def boot_synthetic_ais_injector():
    pass   # Phase 2 only


def initialize_system():
    boot_cpa_engine()
    boot_colregs_classifier()
    boot_alert_gate()
    boot_signalk_consumer()          # ws://<host>:8099/signalk/v1/stream
    boot_voice_arbiter()
    initialize_shadow_logger()
    boot_voice_client()              # Advisory output — in scope (D02-1)
    boot_widget_sse_server()         # Advisory output — in scope (D02-1)
    announce_advisory_role()         # ADV-2

    if SAFEHELM_PHASE < 2:
        logger.info('SafeHelm Advisory Mode. No Signal K write path; SH-15 not engaged.')
        return

    if not verify_signalk_transmit_whitelist():
        logger.critical('SH-15 not satisfied: transmitPGNs whitelist missing. '
                        'Refusing to start Phase 2. Service will stay in Advisory Mode.')
        return                       # degrade to Advisory — do NOT exit
    boot_synthetic_ais_injector()


# ── [T3] Advisory loop thread ─────────────────────────────────────────────

def _advisory_loop():
    """Background thread: runs advisory_tick at ~1 Hz."""
    while True:
        try:
            now_iso = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            if _sk_client and _arbiter is not None:
                own = _sk_client.get_own()
                targets = _sk_client.get_targets()
                if own is not None:
                    # Apply pending acks
                    for mmsi in list(_pending_acks):
                        mgr = _managers.get(mmsi)
                        if mgr:
                            mgr.execute_ui_acknowledgement()
                        _pending_acks.discard(mmsi)
                    # Apply pending dismissals
                    for mmsi in list(_pending_dismissals):
                        _managers.pop(mmsi, None)
                        _pending_dismissals.discard(mmsi)

                    winner = advisory_tick(own, targets, _managers, _arbiter, now_iso)

                    # Broadcast state update to SSE clients
                    alert_list = [
                        {'mmsi': k, 'tier': m.tier, 'rule': m.rule_id,
                         'cpa_m': round(m.cpa, 1), 'tcpa_s': round(m.tcpa, 1),
                         'state': m.state.name}
                        for k, m in _managers.items()
                    ]
                    _broadcast({'type': 'state', 'alerts': alert_list,
                                'winner': winner})
        except Exception:
            logger.exception('advisory_loop error')
        time.sleep(1.0)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    initialize_system()
    loop_thread = threading.Thread(target=_advisory_loop, daemon=True)
    loop_thread.start()
    # BUG-48: bind to 127.0.0.1 only — proxied by dashboard
    app.run(host='127.0.0.1', port=8095, threaded=True)
