"""
d3kOS AI Bridge — Feature 4: Anchor Watch AI Alerts

Safety-critical feature. The alarm NEVER waits for AI.
Pre-written audio fires the instant drag is confirmed (3 consecutive polls).
AI corrective action is on-demand only.

Signal K paths monitored:
  navigation.anchor.maxRadius     (metres — set by skipper)
  navigation.anchor.currentRadius (metres — live distance from anchor)
  navigation.anchor.position      (lat/lon of set anchor)
  navigation.position             (current vessel position)
"""

import os
import json
import logging
import threading
import time
from datetime import datetime, timezone

import requests

from utils.signalk_client import get_anchor_data, get_navigation_snapshot
from utils.geo import bearing_degrees, metres_to_nm, ms_to_knots
from utils import tts

log = logging.getLogger(__name__)

ANCHOR_POLL_INTERVAL   = int(os.environ.get('ANCHOR_POLL_INTERVAL', 15))
DRAG_CONFIRM_COUNT     = int(os.environ.get('ANCHOR_DRAG_CONFIRM_COUNT', 3))
GEMINI_PROXY_URL       = os.environ.get('GEMINI_PROXY_URL', 'http://localhost:3001')
VESSEL_NAME            = os.environ.get('VESSEL_NAME', 'the vessel')
LOG_DIR                = os.environ.get('LOG_DIR', '/home/d3kos/logs')

_ANCHOR_LOG_DIR = os.path.join(LOG_DIR, 'anchor-events')

_AI_ADVICE_PROMPT = """\
Marine emergency: vessel {vessel_name} anchor drag detected.

Anchor position: {anchor_lat:.4f}N, {anchor_lon:.4f}W
Current position: {current_lat:.4f}N, {current_lon:.4f}W
Drift distance: {drift_m:.0f} metres
Drift direction: {drift_bearing:.0f} degrees
Current speed: {sog:.1f} knots
Time: {timestamp}

Provide a brief, calm, practical 3-4 step corrective action plan.
Steps should be in order of urgency. Be direct. This is an emergency."""


class AnchorWatch:
    """
    Background thread that monitors Signal K for anchor drag.
    broadcast_fn(event_type, data) pushes SSE to dashboard.
    """

    def __init__(self, broadcast_fn):
        self._broadcast = broadcast_fn
        self._stop_event = threading.Event()
        self._thread = None
        self._active = False
        self._alarm_active = False
        self._repeat_thread = None
        self._drag_confirm_counter = 0
        self._last_drag_alert_time = None
        self._dismissed = False

    def start(self):
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._loop, daemon=True, name='anchor-watch'
        )
        self._thread.start()
        log.info('AnchorWatch started (poll=%ds, confirm=%d)',
                 ANCHOR_POLL_INTERVAL, DRAG_CONFIRM_COUNT)

    def stop(self):
        self._stop_event.set()
        self._alarm_active = False

    def activate(self, radius_m: float | None = None) -> dict:
        """
        Activate anchor watch. Optionally set a custom radius.
        Returns {'ok': bool, 'message': str}.
        """
        self._active = True
        self._dismissed = False
        self._drag_confirm_counter = 0
        self._alarm_active = False

        snap = get_navigation_snapshot()
        current_radius = None
        if snap.get('anchor_max_radius_m'):
            current_radius = snap['anchor_max_radius_m']

        msg = (f'Anchor watch active. '
               f'Radius: {radius_m or current_radius or "unknown"} metres.')
        tts.speak(msg)
        log.info('Anchor watch activated — radius: %s m', radius_m or current_radius)

        self._broadcast('anchor_status', {
            'active': True,
            'alarm':  False,
            'radius_m': radius_m or current_radius,
        })
        return {'ok': True, 'message': msg}

    def dismiss(self) -> dict:
        """Dismiss active anchor alarm."""
        self._alarm_active = False
        self._dismissed = True
        self._drag_confirm_counter = 0

        if self._repeat_thread and self._repeat_thread.is_alive():
            # Signal repeat thread to stop via alarm flag already False
            pass

        log.info('Anchor alarm dismissed')
        self._broadcast('anchor_status', {
            'active': self._active,
            'alarm':  False,
            'dismissed': True,
        })
        return {'ok': True}

    def get_ai_advice(self) -> dict:
        """
        Generate AI corrective action for current drag event.
        Called when user taps "GET AI ADVICE" — never called automatically.
        """
        snap = get_navigation_snapshot()
        anchor = get_anchor_data()

        drift_m = anchor.get('current_radius_m') or 0.0
        bearing = 0.0
        if (anchor.get('anchor_lat') and anchor.get('anchor_lon') and
                snap.get('lat') and snap.get('lon')):
            bearing = bearing_degrees(
                anchor['anchor_lat'], anchor['anchor_lon'],
                snap['lat'], snap['lon'],
            )

        prompt = _AI_ADVICE_PROMPT.format(
            vessel_name  = VESSEL_NAME,
            anchor_lat   = anchor.get('anchor_lat') or 0,
            anchor_lon   = abs(anchor.get('anchor_lon') or 0),
            current_lat  = snap.get('lat') or 0,
            current_lon  = abs(snap.get('lon') or 0),
            drift_m      = drift_m,
            drift_bearing = bearing,
            sog          = ms_to_knots(snap.get('sog_ms') or 0),
            timestamp    = datetime.now(timezone.utc).isoformat(),
        )

        result = _call_ai(prompt)
        return {
            'ok':     True,
            'advice': result.get('response', 'AI unavailable.'),
            'source': result.get('source', 'error'),
        }

    def _loop(self):
        while not self._stop_event.is_set():
            try:
                if self._active:
                    self._check_drag()
            except Exception as exc:
                log.error('AnchorWatch error: %s', exc)

            for _ in range(ANCHOR_POLL_INTERVAL):
                if self._stop_event.is_set():
                    return
                time.sleep(1)

    def _check_drag(self):
        anchor = get_anchor_data()
        max_r     = anchor.get('max_radius_m')
        current_r = anchor.get('current_radius_m')

        if max_r is None or max_r <= 0:
            # Anchor watch not set in Signal K — auto-detect activation
            return

        # Auto-activate if Signal K has anchor data but we weren't manually activated
        if not self._active:
            self._active = True
            self._dismissed = False

        if self._alarm_active:
            return  # Alarm already firing — don't re-evaluate until dismissed

        if current_r is None:
            self._drag_confirm_counter = 0
            return

        exceeds = current_r > max_r

        if exceeds:
            self._drag_confirm_counter += 1
            log.debug('Anchor drag counter: %d/%d (%.1fm > %.1fm)',
                      self._drag_confirm_counter, DRAG_CONFIRM_COUNT,
                      current_r, max_r)
        else:
            self._drag_confirm_counter = 0
            return

        if self._drag_confirm_counter >= DRAG_CONFIRM_COUNT:
            self._fire_drag_alert(anchor, current_r, max_r)

    def _fire_drag_alert(self, anchor: dict, current_r: float, max_r: float):
        self._alarm_active = True
        self._dismissed = False
        ts = datetime.now(timezone.utc)

        snap = get_navigation_snapshot()
        sog  = ms_to_knots(snap.get('sog_ms') or 0)

        # Bearing from anchor to vessel
        drift_bearing = 0.0
        if (anchor.get('anchor_lat') and anchor.get('anchor_lon') and
                snap.get('lat') and snap.get('lon')):
            drift_bearing = bearing_degrees(
                anchor['anchor_lat'], anchor['anchor_lon'],
                snap['lat'], snap['lon'],
            )

        log.warning('ANCHOR DRAG ALERT: %.1fm drift (limit %.1fm)', current_r, max_r)

        # Part 1 — immediate audio (pre-written, no AI wait)
        alarm_text = (
            f'Anchor drag detected. Anchor drag detected. '
            f'Vessel has moved {current_r:.0f} metres from anchor position. '
            f'Check your position immediately.'
        )
        tts.speak_urgent(alarm_text, repeat=1)

        # Part 2 — screen alert via SSE
        self._broadcast('anchor_alert', {
            'alarm':          True,
            'drift_m':        round(current_r, 1),
            'max_radius_m':   round(max_r, 1),
            'drift_bearing':  round(drift_bearing, 0),
            'sog_kts':        round(sog, 1),
            'timestamp':      ts.isoformat(),
            'vessel_lat':     snap.get('lat'),
            'vessel_lon':     snap.get('lon'),
            'anchor_lat':     anchor.get('anchor_lat'),
            'anchor_lon':     anchor.get('anchor_lon'),
        })

        # Part 4 — log event to disk
        _log_drag_event(
            anchor_lat    = anchor.get('anchor_lat'),
            anchor_lon    = anchor.get('anchor_lon'),
            vessel_lat    = snap.get('lat'),
            vessel_lon    = snap.get('lon'),
            drift_m       = current_r,
            drift_bearing = drift_bearing,
            max_radius_m  = max_r,
            sog_kts       = sog,
            timestamp     = ts,
        )

        # Repeat audio every 60 seconds until dismissed
        self._repeat_thread = threading.Thread(
            target=self._repeat_alarm,
            args=(current_r,),
            daemon=True,
        )
        self._repeat_thread.start()

    def _repeat_alarm(self, drift_m: float):
        repeat_text = (
            f'Anchor drag. {drift_m:.0f} metres. Check your position.'
        )
        while self._alarm_active and not self._stop_event.is_set():
            time.sleep(60)
            if self._alarm_active:
                tts.speak(repeat_text)


def _log_drag_event(anchor_lat, anchor_lon, vessel_lat, vessel_lon,
                    drift_m, drift_bearing, max_radius_m, sog_kts, timestamp):
    os.makedirs(_ANCHOR_LOG_DIR, exist_ok=True)
    ts_str   = timestamp.strftime('%Y-%m-%d_%H%M')
    filename = f'{ts_str}_anchor_drag.json'
    path     = os.path.join(_ANCHOR_LOG_DIR, filename)

    event = {
        'timestamp':           timestamp.isoformat(),
        'event_type':          'anchor_drag',
        'anchor_position':     {'lat': anchor_lat, 'lon': anchor_lon},
        'vessel_position':     {'lat': vessel_lat, 'lon': vessel_lon},
        'drift_metres':        round(drift_m, 1),
        'drift_bearing':       round(drift_bearing, 0),
        'max_radius_set':      round(max_radius_m, 0),
        'sog_at_event':        round(sog_kts, 1),
        'ai_advice_requested': False,
    }

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(event, f, indent=2)

    log.info('Anchor drag event logged: %s', path)


def _call_ai(prompt: str) -> dict:
    try:
        resp = requests.post(
            f'{GEMINI_PROXY_URL}/ask',
            json={'message': prompt},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        log.warning('AI proxy call failed: %s', exc)
        return {'response': '', 'source': 'error'}
