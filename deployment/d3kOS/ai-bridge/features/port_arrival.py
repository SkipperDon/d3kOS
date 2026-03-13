"""
d3kOS AI Bridge — Feature 2: Port Arrival Briefing

Fires once when vessel reaches ARRIVAL_TRIGGER_NM (default 2.0nm) from
final destination waypoint. Delivers full briefing to screen + short audio.
Will not re-fire for the same destination.
"""

import os
import time
import logging
import threading
import requests

from utils.avnav_client import get_nav_data
from utils.signalk_client import get_navigation_snapshot
from utils.geo import haversine_nm, ms_to_knots
from utils import tts

log = logging.getLogger(__name__)

ARRIVAL_TRIGGER_NM    = float(os.environ.get('ARRIVAL_TRIGGER_NM', 2.0))
ARRIVAL_POLL_INTERVAL = int(os.environ.get('ARRIVAL_POLL_INTERVAL', 60))
GEMINI_PROXY_URL      = os.environ.get('GEMINI_PROXY_URL', 'http://localhost:3001')
VESSEL_NAME           = os.environ.get('VESSEL_NAME', 'the vessel')
HOME_PORT             = os.environ.get('HOME_PORT', 'home port')

_BRIEFING_PROMPT = """\
You are a marine navigation assistant for vessel {vessel_name}, home port {home_port}.
The vessel is approaching {destination}.

Current position: {lat:.4f}N, {lon:.4f}W
Speed: {sog:.1f} knots
Distance to {destination}: {distance:.1f} nautical miles

Provide a complete port arrival briefing covering ALL of the following sections:

1. FUEL DOCK — location within marina, hours of operation, VHF channel for fuel
2. MARINA CONTACT — harbour master VHF channel, phone number, transient berth policy
3. CUSTOMS / ENTRY — required procedures, documentation, CBSA/NEXUS if Canadian waters
4. ANCHORAGE — best area, depth, bottom type, holding quality, any restrictions
5. PROVISIONING — grocery, chandlery, restaurants within walking or dinghy distance
6. APPROACH HAZARDS — tidal timing, charted shoals, speed limits, narrow channels

Format as numbered sections with bold headers. Be specific and practical.
Note if any information may be outdated and should be verified on official charts.
Extract one brief sentence about the most important approach hazard for audio delivery."""


class PortArrivalMonitor:
    """
    Background thread that polls navigation data and fires arrival briefings.
    broadcast_fn(event_type, data) pushes SSE to dashboard.
    """

    def __init__(self, broadcast_fn):
        self._broadcast = broadcast_fn
        self._stop_event = threading.Event()
        self._thread = None
        self._triggered_destinations: set = set()

    def start(self):
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._loop, daemon=True, name='port-arrival'
        )
        self._thread.start()
        log.info('PortArrivalMonitor started (trigger=%.1fnm, poll=%ds)',
                 ARRIVAL_TRIGGER_NM, ARRIVAL_POLL_INTERVAL)

    def stop(self):
        self._stop_event.set()

    def trigger_for_destination(self, destination_name: str, lat: float, lon: float):
        """
        External trigger — called by /webhook/arrival endpoint.
        Fires briefing immediately for a named destination.
        """
        t = threading.Thread(
            target=self._generate_and_broadcast,
            args=(destination_name, lat, lon, 0.0),
            daemon=True,
        )
        t.start()

    def _loop(self):
        while not self._stop_event.is_set():
            try:
                self._check_arrival()
            except Exception as exc:
                log.error('PortArrivalMonitor error: %s', exc)

            for _ in range(ARRIVAL_POLL_INTERVAL):
                if self._stop_event.is_set():
                    return
                time.sleep(1)

    def _check_arrival(self):
        nav = get_nav_data()
        sk  = get_navigation_snapshot()

        dest_name = nav.get('wp_name')
        dest_lat  = nav.get('wp_lat')
        dest_lon  = nav.get('wp_lon')

        if not dest_name or dest_lat is None or dest_lon is None:
            return  # No active waypoint

        if dest_name in self._triggered_destinations:
            return  # Already briefed for this destination

        vessel_lat = sk.get('lat') or nav.get('lat')
        vessel_lon = sk.get('lon') or nav.get('lon')

        if vessel_lat is None or vessel_lon is None:
            return  # No GPS fix

        distance_nm = haversine_nm(vessel_lat, vessel_lon, dest_lat, dest_lon)

        if distance_nm <= ARRIVAL_TRIGGER_NM:
            log.info('Arrival trigger: %.2fnm from %s', distance_nm, dest_name)
            self._triggered_destinations.add(dest_name)
            self._generate_and_broadcast(dest_name, dest_lat, dest_lon, distance_nm,
                                         vessel_lat=vessel_lat, vessel_lon=vessel_lon,
                                         sog_ms=sk.get('sog_ms') or nav.get('sog_ms') or 0.0)

    def _generate_and_broadcast(self, destination: str,
                                 dest_lat: float, dest_lon: float,
                                 distance_nm: float,
                                 vessel_lat: float = 0.0,
                                 vessel_lon: float = 0.0,
                                 sog_ms: float = 0.0):
        sog_kts = ms_to_knots(sog_ms)

        # Stage 1 audio fires immediately — no AI wait
        stage1_text = (
            f'Approaching {destination}. '
            f'{distance_nm:.1f} nautical miles. '
            f'Port arrival briefing ready on screen.'
        )
        tts.speak(stage1_text)

        # Generate full briefing via AI
        prompt = _BRIEFING_PROMPT.format(
            vessel_name = VESSEL_NAME,
            home_port   = HOME_PORT,
            destination = destination,
            lat         = abs(vessel_lat),
            lon         = abs(vessel_lon),
            sog         = sog_kts,
            distance    = distance_nm,
        )

        ai_result = _call_ai(prompt)
        briefing_text = ai_result.get('response', '')
        source = ai_result.get('source', 'error')

        if not briefing_text:
            briefing_text = f'AI briefing unavailable. Approaching {destination} in {distance_nm:.1f}nm.'

        self._broadcast('arrival_briefing', {
            'destination': destination,
            'distance_nm': round(distance_nm, 2),
            'briefing':    briefing_text,
            'source':      source,
            'offline':     source == 'ollama',
        })


def _call_ai(prompt: str) -> dict:
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
