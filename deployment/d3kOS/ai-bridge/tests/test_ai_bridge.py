"""
d3kOS AI Bridge — pytest test suite
Phase 5 spec: ai-bridge/tests/test_ai_bridge.py

Run from ai-bridge/ directory:
    pytest tests/test_ai_bridge.py -v

Integration tests (require live Pi services) are marked @pytest.mark.integration
and skipped by default:
    pytest tests/test_ai_bridge.py -v -m integration
"""

import json
import math
import os
import sys
import types
import pytest

# Ensure ai-bridge root is in path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


# ── Unit tests: geo.py ─────────────────────────────────────────────────────────

from utils.geo import (
    haversine_nm, bearing_degrees, ms_to_knots, rad_to_deg,
    gpx_total_distance_nm, metres_to_nm,
)


def test_haversine_nm_calculation():
    """
    2 nm trigger accuracy test.
    Kingston ON to 2nm point north: approx 43.9700N, 76.4900W → 43.9367N, 76.4900W
    should be close to 2.0nm.
    """
    # Known distance: 1 degree of latitude ≈ 60nm
    nm = haversine_nm(43.0, -76.0, 44.0, -76.0)
    assert 59.5 < nm < 60.5, f'Expected ~60nm for 1 degree lat, got {nm:.3f}nm'


def test_haversine_same_point():
    """Distance from a point to itself is zero."""
    assert haversine_nm(43.5, -76.5, 43.5, -76.5) == 0.0


def test_haversine_two_nm_approx():
    """Verify 2nm trigger distance is detectable."""
    # 2nm north of Kingston — approx 0.0333 degrees lat
    nm = haversine_nm(43.9367, -76.4900, 43.9700, -76.4900)
    assert 1.9 < nm < 2.1, f'Expected ~2nm, got {nm:.3f}nm'


def test_bearing_north():
    """Point directly north should give bearing 0 (or 360)."""
    b = bearing_degrees(43.0, -76.0, 44.0, -76.0)
    assert b < 1.0 or b > 359.0, f'Expected ~0 degrees, got {b:.1f}'


def test_bearing_east():
    """Point directly east should give bearing ~90."""
    b = bearing_degrees(43.0, -76.0, 43.0, -75.0)
    assert 88.0 < b < 92.0, f'Expected ~90 degrees, got {b:.1f}'


def test_ms_to_knots():
    """1 m/s = 1.94384 knots."""
    assert abs(ms_to_knots(1.0) - 1.94384) < 0.001


def test_ms_to_knots_zero():
    assert ms_to_knots(0.0) == 0.0


def test_rad_to_deg():
    """pi radians = 180 degrees."""
    assert abs(rad_to_deg(math.pi) - 180.0) < 0.001


def test_rad_to_deg_two_pi():
    """2*pi radians should wrap to 0 degrees."""
    result = rad_to_deg(2 * math.pi)
    assert result < 0.001 or abs(result - 360) < 0.001


def test_gpx_total_distance():
    """Two points 1 degree of lat apart should be ~60nm."""
    points = [(43.0, -76.0), (44.0, -76.0)]
    nm = gpx_total_distance_nm(points)
    assert 59.5 < nm < 60.5


def test_gpx_empty_track():
    assert gpx_total_distance_nm([]) == 0.0
    assert gpx_total_distance_nm([(43.0, -76.0)]) == 0.0


# ── Unit tests: voyage_logger.py / GPX parsing ────────────────────────────────

from features.voyage_logger import parse_gpx_summary

_SAMPLE_GPX = """\
<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="AvNav" xmlns="http://www.topografix.com/GPX/1/1">
  <trk>
    <trkseg>
      <trkpt lat="43.9367" lon="-76.4900">
        <time>2026-07-15T10:00:00Z</time>
      </trkpt>
      <trkpt lat="43.9500" lon="-76.4800">
        <time>2026-07-15T11:00:00Z</time>
      </trkpt>
      <trkpt lat="44.0000" lon="-76.4700">
        <time>2026-07-15T12:00:00Z</time>
      </trkpt>
    </trkseg>
  </trk>
</gpx>"""

_EMPTY_GPX = """\
<?xml version="1.0"?>
<gpx version="1.1" xmlns="http://www.topografix.com/GPX/1/1">
  <trk><trkseg></trkseg></trk>
</gpx>"""


def test_gpx_summary_extraction():
    """parse_gpx_summary returns expected fields from sample GPX."""
    summary = parse_gpx_summary(_SAMPLE_GPX)
    assert summary is not None
    assert summary['point_count'] == 3
    assert abs(summary['start_lat'] - 43.9367) < 0.001
    assert abs(summary['start_lon'] - (-76.4900)) < 0.001
    assert summary['start_time'] == '2026-07-15T10:00:00Z'
    assert summary['end_time']   == '2026-07-15T12:00:00Z'
    assert summary['elapsed_seconds'] == 7200  # 2 hours
    assert summary['total_nm'] > 0


def test_gpx_summary_empty_track():
    """Empty track returns None."""
    result = parse_gpx_summary(_EMPTY_GPX)
    assert result is None


def test_gpx_raw_data_not_in_prompt():
    """
    parse_gpx_summary must not return raw coordinate arrays.
    Only summary statistics should be in the returned dict.
    Privacy rule: raw GPS points never sent to AI.
    """
    summary = parse_gpx_summary(_SAMPLE_GPX)
    assert summary is not None
    # The summary dict must NOT contain a list of coordinates
    for key, val in summary.items():
        assert not isinstance(val, list), (
            f'summary[{key!r}] is a list — raw coordinates must not be returned'
        )


# ── Unit tests: anchor_watch.py ────────────────────────────────────────────────

def test_anchor_drag_confirmation_debounce():
    """
    AnchorWatch must require DRAG_CONFIRM_COUNT consecutive exceedances.
    A single exceedance must NOT fire the alert.
    """
    from features.anchor_watch import AnchorWatch

    fired = []

    def mock_broadcast(event_type, data):
        if event_type == 'anchor_alert':
            fired.append(data)

    aw = AnchorWatch(mock_broadcast)
    aw._active = True

    # Simulate Signal K data via monkeypatching get_anchor_data
    import utils.signalk_client as sk

    call_count = [0]

    def mock_get_anchor_data():
        call_count[0] += 1
        return {
            'max_radius_m':     30.0,
            'current_radius_m': 50.0,  # Always exceeding
            'anchor_lat':       43.9,
            'anchor_lon':       -76.5,
        }

    def mock_get_nav_snapshot():
        return {'lat': 43.901, 'lon': -76.499, 'sog_ms': 0.1,
                'cog_rad': 0, 'anchor_max_radius_m': 30, 'anchor_current_radius_m': 50,
                'anchor_lat': 43.9, 'anchor_lon': -76.5}

    original_get_anchor = sk.get_anchor_data
    original_get_snap   = sk.get_navigation_snapshot
    sk.get_anchor_data        = mock_get_anchor_data
    sk.get_navigation_snapshot = mock_get_nav_snapshot

    # Override anchor_watch module's import too
    import features.anchor_watch as aw_mod
    aw_mod.get_anchor_data = mock_get_anchor_data
    aw_mod.get_navigation_snapshot = mock_get_nav_snapshot

    try:
        # Poll once — counter = 1, no alert
        aw._check_drag()
        assert len(fired) == 0, 'Alert fired on first poll — debounce failed'
        assert aw._drag_confirm_counter == 1

        # Poll twice — counter = 2, no alert
        aw._check_drag()
        assert len(fired) == 0, 'Alert fired on second poll — debounce failed'

        # Poll three times — counter = 3, alert fires
        aw._check_drag()
        assert len(fired) == 1, 'Alert did not fire after 3 consecutive exceedances'
    finally:
        sk.get_anchor_data        = original_get_anchor
        sk.get_navigation_snapshot = original_get_snap


# ── Unit tests: Signal K path and unit conversions ────────────────────────────

def test_signalk_path_parsing_sog():
    """SOG from Signal K is m/s — must convert to knots correctly."""
    sog_ms  = 2.572  # ~5 knots
    sog_kts = ms_to_knots(sog_ms)
    assert 4.9 < sog_kts < 5.1, f'Expected ~5 knots, got {sog_kts:.2f}'


def test_signalk_path_parsing_cog():
    """COG from Signal K is radians — must convert to degrees correctly."""
    # 1.5708 rad = pi/2 = 90 degrees
    cog_deg = rad_to_deg(math.pi / 2)
    assert abs(cog_deg - 90.0) < 0.01


def test_signalk_path_parsing_kelvin():
    """Engine temp in Signal K is Kelvin — verify basic conversion formula."""
    temp_k  = 358.15  # 85°C
    temp_c  = temp_k - 273.15
    assert abs(temp_c - 85.0) < 0.01


# ── Unit tests: avnav_client.py — must use POST ────────────────────────────────

def test_avnav_client_uses_post():
    """
    avnav_client._post() must use requests.post, never requests.get.
    This verifies the A1/A2 anomaly fix in the spec.
    """
    import utils.avnav_client as avc
    import unittest.mock as mock

    post_called = []
    get_called  = []

    def mock_post(url, data=None, headers=None, timeout=None):
        post_called.append(url)
        resp = mock.MagicMock()
        resp.raise_for_status = lambda: None
        resp.json.return_value = {'status': 'OK', 'data': {}}
        return resp

    def mock_get(url, timeout=None):
        get_called.append(url)
        raise AssertionError('avnav_client must not use GET — AvNav returns HTTP 501 for GET')

    with mock.patch('requests.post', side_effect=mock_post), \
         mock.patch('requests.get',  side_effect=mock_get):
        avc.get_status()
        avc.get_nav_data()

    assert len(post_called) >= 2, 'Expected at least 2 POST calls'
    assert len(get_called)  == 0, f'Unexpected GET calls: {get_called}'


# ── Unit tests: TTS ────────────────────────────────────────────────────────────

def test_tts_available_check():
    """tts.is_available() must return a bool — not raise."""
    from utils.tts import is_available
    result = is_available()
    assert isinstance(result, bool)


def test_tts_empty_text_no_crash():
    """Speaking empty string must return False without crashing."""
    from utils import tts
    result = tts.speak('', block=False)
    assert result is False


# ── Integration tests (require live Pi services) ──────────────────────────────

@pytest.mark.integration
def test_avnav_api_reachable():
    """POST to avnav_navi.php responds with status OK."""
    from utils.avnav_client import get_status
    result = get_status()
    assert result is not None, 'AvNav API unreachable — is avnav.service running?'


@pytest.mark.integration
def test_signalk_ws_connects():
    """Signal K REST API responds (proxy for WS availability)."""
    from utils.signalk_client import is_reachable
    assert is_reachable(), 'Signal K unreachable at localhost:8099'


@pytest.mark.integration
def test_gemini_proxy_reachable():
    """Gemini proxy status endpoint at localhost:3001."""
    import requests as req
    resp = req.get('http://localhost:3001/status', timeout=5)
    assert resp.status_code == 200, f'Gemini proxy returned {resp.status_code}'


@pytest.mark.integration
def test_ai_bridge_status_reachable():
    """AI Bridge status endpoint at localhost:3002."""
    import requests as req
    resp = req.get('http://localhost:3002/status', timeout=5)
    assert resp.status_code == 200
    data = resp.json()
    assert data.get('service') == 'd3kos-ai-bridge'


@pytest.mark.integration
def test_webhook_query_returns_response():
    """POST /webhook/query returns JSON with response field."""
    import requests as req
    resp = req.post(
        'http://localhost:3002/webhook/query',
        json={'query': 'What does VHF channel 16 mean on a boat?'},
        timeout=30,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get('ok') is True
    assert 'response' in data
    assert len(data['response']) > 10


@pytest.mark.integration
def test_webhook_alert_fires():
    """POST /webhook/alert returns ok (audio fires on Pi speakers)."""
    import requests as req
    resp = req.post(
        'http://localhost:3002/webhook/alert',
        json={'message': 'AI Bridge test alert from pytest.', 'severity': 'info'},
        timeout=10,
    )
    assert resp.status_code == 200
    assert resp.json().get('ok') is True


# ── Privacy test: AI cache must not store query text ─────────────────────────

def test_ai_bridge_cache_no_query_text():
    """
    Webhook query endpoint must not log the query text.
    Verify by checking that ai_bridge.py has no persistent query storage.
    """
    import inspect
    import ai_bridge
    source = inspect.getsource(ai_bridge)

    # These patterns would indicate query text being persisted
    forbidden = ['query_log', 'save_query', 'query_history', 'log_query']
    for pattern in forbidden:
        assert pattern not in source, (
            f'ai_bridge.py contains "{pattern}" — query text must not be stored'
        )
