"""
d3kOS AI Bridge — Feature 1: Always-On Route Analysis Widget

Polls AvNav every ROUTE_ANALYSIS_INTERVAL seconds (default 5 min).
Generates a 4-6 sentence passage brief via Gemini proxy at :3001.
Re-triggers immediately on route change or explicit "Analyze Now" request.
"""

import os
import time
import logging
import threading
import requests

from utils.avnav_client import get_nav_data, read_current_leg
from utils.signalk_client import get_navigation_snapshot
from utils.geo import ms_to_knots, rad_to_deg, metres_to_nm

log = logging.getLogger(__name__)

ROUTE_ANALYSIS_INTERVAL = int(os.environ.get('ROUTE_ANALYSIS_INTERVAL', 300))
GEMINI_PROXY_URL         = os.environ.get('GEMINI_PROXY_URL', 'http://localhost:3001')
VESSEL_NAME              = os.environ.get('VESSEL_NAME', 'the vessel')
HOME_PORT                = os.environ.get('HOME_PORT', 'home port')

_PROMPT_TEMPLATE = """\
You are a marine navigation assistant for vessel {vessel_name}, home port {home_port}.

Current position: {lat:.4f}N, {lon:.4f}W
Speed: {sog:.1f} knots | Course: {cog:.0f} degrees
Active route: {route_name} — {waypoint_count} waypoints
Next waypoint: {wp_name}
Distance to next waypoint: {dtw_nm:.1f} nm

Write a brief passage analysis (4-6 sentences):
1. Next waypoint — any approach notes or hazards
2. Upcoming waypoints — anything to prepare for
3. One practical piece of local knowledge if relevant
4. Any timing or tidal considerations

Be concise. This is displayed on a chart tablet underway. Use nautical terminology."""


class RouteAnalyzer:
    """
    Runs as a background thread.
    Calls broadcast_fn(event_type, data) to push SSE updates to the dashboard.
    """

    def __init__(self, broadcast_fn):
        self._broadcast = broadcast_fn
        self._stop_event = threading.Event()
        self._thread = None
        self._last_route_name = None
        self._last_wp_name = None
        self._force_flag = threading.Event()

    def start(self):
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True, name='route-analyzer')
        self._thread.start()
        log.info('RouteAnalyzer started (interval=%ds)', ROUTE_ANALYSIS_INTERVAL)

    def stop(self):
        self._stop_event.set()

    def force_analyze(self):
        """Trigger an immediate analysis (called by /analyze-route endpoint)."""
        self._force_flag.set()

    def _loop(self):
        while not self._stop_event.is_set():
            try:
                self._run_analysis()
            except Exception as exc:
                log.error('RouteAnalyzer error: %s', exc)
                self._broadcast('route_update', {
                    'state': 'ERROR',
                    'text': 'Route analysis error — check AI Bridge logs.',
                    'source': 'error',
                })

            # Wait for interval or force trigger
            for _ in range(ROUTE_ANALYSIS_INTERVAL):
                if self._stop_event.is_set() or self._force_flag.is_set():
                    break
                time.sleep(1)

            self._force_flag.clear()

    def _run_analysis(self):
        nav = get_nav_data()
        sk  = get_navigation_snapshot()

        route_name = nav.get('route_name')
        wp_name    = nav.get('wp_name')

        # No active route
        if not route_name:
            self._broadcast('route_update', {
                'state': 'NO_ROUTE',
                'text': 'No active route in AvNav.',
                'source': 'none',
            })
            self._last_route_name = None
            self._last_wp_name = None
            return

        # Detect route or waypoint change — force immediate re-analysis logged
        if route_name != self._last_route_name or wp_name != self._last_wp_name:
            log.info('Route/waypoint changed — re-analyzing: %s / %s', route_name, wp_name)

        self._last_route_name = route_name
        self._last_wp_name    = wp_name

        # Broadcast spinner state
        self._broadcast('route_update', {'state': 'UPDATING', 'text': '', 'source': 'loading'})

        # Build position context
        lat = sk.get('lat') or nav.get('lat')
        lon = sk.get('lon') or nav.get('lon')
        sog_ms  = sk.get('sog_ms') or nav.get('sog_ms') or 0.0
        cog_rad = sk.get('cog_rad')
        cog_deg = rad_to_deg(cog_rad) if cog_rad is not None else (nav.get('cog_deg') or 0.0)
        sog_kts = ms_to_knots(sog_ms)
        dtw_nm  = metres_to_nm(nav['wp_distance_m']) if nav.get('wp_distance_m') else 0.0

        if lat is None or lon is None:
            self._broadcast('route_update', {
                'state': 'NO_GPS',
                'text': 'Waiting for GPS fix.',
                'source': 'none',
            })
            return

        prompt = _PROMPT_TEMPLATE.format(
            vessel_name    = VESSEL_NAME,
            home_port      = HOME_PORT,
            lat            = lat,
            lon            = abs(lon),
            sog            = sog_kts,
            cog            = cog_deg,
            route_name     = route_name,
            waypoint_count = nav.get('route_numpoints') or '?',
            wp_name        = wp_name or 'unknown',
            dtw_nm         = dtw_nm,
        )

        ai_result = _call_ai(prompt)
        source = ai_result.get('source', 'unknown')
        text   = ai_result.get('response', '')

        if text:
            self._broadcast('route_update', {
                'state':  'ACTIVE',
                'text':   text,
                'source': source,
                'offline': source == 'ollama',
                'route_name': route_name,
                'wp_name': wp_name,
                'sog_kts': round(sog_kts, 1),
                'cog_deg': round(cog_deg, 0),
            })
        else:
            self._broadcast('route_update', {
                'state':  'AI_UNAVAILABLE',
                'text':   'AI unavailable — check Ollama at 192.168.1.36:11434',
                'source': 'error',
            })


def _call_ai(prompt: str) -> dict:
    """POST to Gemini proxy at :3001/ask. Returns {'response': str, 'source': str}."""
    try:
        resp = requests.post(
            f'{GEMINI_PROXY_URL}/ask',
            json={'prompt': prompt},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        log.warning('AI proxy call failed: %s', exc)
        return {'response': '', 'source': 'error'}
