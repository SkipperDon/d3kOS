"""
d3kOS AI Bridge — pytest test suite
Phase 5 spec: ai-bridge/tests/test_ai_bridge.py

Covers:
  utils/geo.py            pure math — no mocking
  utils/avnav_client.py   POST-only enforcement, parsers, disk-preferred reads
  utils/signalk_client.py envelope extraction, mocked HTTP
  utils/tts.py            binary detection, empty-string guard, shell quoting
  features/anchor_watch.py   state machine, 3-poll debounce
  features/voyage_logger.py  GPX parser, privacy (no raw GPS in AI prompt)
  ai_bridge.py Flask routes  /status, /stream, /webhook/*, /anchor/*, /voyages

All external calls (HTTP, subprocess, disk I/O) are mocked in unit tests.
No Pi connection required for unit tests.

Run from deployment/d3kOS/ai-bridge/:
    pip install pytest flask requests python-dotenv
    pytest tests/ -v

Integration tests (require live Pi on 192.168.1.237) are skipped by default:
    pytest tests/ -v -m integration
"""

import json
import math
import os
import sys
import pytest
from unittest.mock import MagicMock, patch, mock_open

# conftest.py adds ai-bridge root to sys.path


# =============================================================================
# geo.py — pure functions, no I/O
# =============================================================================

class TestHaversineNm:
    def test_same_point_is_zero(self):
        from utils.geo import haversine_nm
        assert haversine_nm(43.686, -79.520, 43.686, -79.520) == 0.0

    def test_one_degree_latitude_approx_60nm(self):
        from utils.geo import haversine_nm
        nm = haversine_nm(43.0, -76.0, 44.0, -76.0)
        assert 59.5 < nm < 60.5, f'Expected ~60 nm, got {nm:.3f}'

    def test_two_nm_trigger_detectable(self):
        """Port arrival fires at 2 nm — verify that distance is measurable."""
        from utils.geo import haversine_nm
        nm = haversine_nm(43.9367, -76.4900, 43.9700, -76.4900)
        assert 1.9 < nm < 2.1, f'Expected ~2 nm, got {nm:.3f}'

    def test_symmetric(self):
        from utils.geo import haversine_nm
        d1 = haversine_nm(43.0, -79.0, 44.0, -80.0)
        d2 = haversine_nm(44.0, -80.0, 43.0, -79.0)
        assert abs(d1 - d2) < 0.001

    def test_returns_float(self):
        from utils.geo import haversine_nm
        assert isinstance(haversine_nm(0.0, 0.0, 1.0, 1.0), float)


class TestBearingDegrees:
    def test_due_north(self):
        from utils.geo import bearing_degrees
        b = bearing_degrees(43.0, -76.0, 44.0, -76.0)
        assert b < 1.0 or b > 359.0, f'Expected ~0, got {b:.1f}'

    def test_due_south(self):
        from utils.geo import bearing_degrees
        b = bearing_degrees(44.0, -76.0, 43.0, -76.0)
        assert 179.0 < b < 181.0, f'Expected ~180, got {b:.1f}'

    def test_due_east(self):
        from utils.geo import bearing_degrees
        b = bearing_degrees(43.0, -76.0, 43.0, -75.0)
        assert 88.0 < b < 92.0, f'Expected ~90, got {b:.1f}'

    def test_due_west(self):
        from utils.geo import bearing_degrees
        b = bearing_degrees(43.0, -75.0, 43.0, -76.0)
        assert 268.0 < b < 272.0, f'Expected ~270, got {b:.1f}'

    def test_result_in_range_0_to_360(self):
        from utils.geo import bearing_degrees
        b = bearing_degrees(43.686, -79.520, 43.250, -79.866)
        assert 0.0 <= b < 360.0


class TestUnitConversions:
    def test_ms_to_knots_one(self):
        from utils.geo import ms_to_knots
        assert abs(ms_to_knots(1.0) - 1.94384) < 0.001

    def test_ms_to_knots_zero(self):
        from utils.geo import ms_to_knots
        assert ms_to_knots(0.0) == 0.0

    def test_ms_to_knots_five_knots(self):
        """2.572 m/s ≈ 5 knots."""
        from utils.geo import ms_to_knots
        assert 4.9 < ms_to_knots(2.572) < 5.1

    def test_rad_to_deg_pi_is_180(self):
        from utils.geo import rad_to_deg
        assert abs(rad_to_deg(math.pi) - 180.0) < 0.001

    def test_rad_to_deg_half_pi_is_90(self):
        from utils.geo import rad_to_deg
        assert abs(rad_to_deg(math.pi / 2) - 90.0) < 0.001

    def test_rad_to_deg_two_pi_wraps_to_zero(self):
        from utils.geo import rad_to_deg
        r = rad_to_deg(2 * math.pi)
        assert r < 0.001 or abs(r - 360) < 0.001

    def test_nm_to_metres(self):
        from utils.geo import nm_to_metres
        assert nm_to_metres(1.0) == 1852.0

    def test_metres_to_nm(self):
        from utils.geo import metres_to_nm
        assert metres_to_nm(1852.0) == 1.0

    def test_roundtrip(self):
        from utils.geo import nm_to_metres, metres_to_nm
        assert abs(metres_to_nm(nm_to_metres(5.0)) - 5.0) < 0.0001


class TestGpxTotalDistanceNm:
    def test_empty_list_is_zero(self):
        from utils.geo import gpx_total_distance_nm
        assert gpx_total_distance_nm([]) == 0.0

    def test_single_point_is_zero(self):
        from utils.geo import gpx_total_distance_nm
        assert gpx_total_distance_nm([(43.686, -79.520)]) == 0.0

    def test_two_identical_points_is_zero(self):
        from utils.geo import gpx_total_distance_nm
        assert gpx_total_distance_nm([(43.0, -79.0), (43.0, -79.0)]) == 0.0

    def test_one_degree_lat_is_60nm(self):
        from utils.geo import gpx_total_distance_nm
        pts = [(43.0, -76.0), (44.0, -76.0)]
        assert 59.5 < gpx_total_distance_nm(pts) < 60.5

    def test_accumulates_multiple_legs(self):
        """Three-point track: two legs of ~1nm each → ~2nm total."""
        from utils.geo import gpx_total_distance_nm
        pts = [(43.0, -76.0), (43.0167, -76.0), (43.0334, -76.0)]
        assert 1.8 < gpx_total_distance_nm(pts) < 2.2


# =============================================================================
# avnav_client.py — parsers + POST enforcement
# =============================================================================

class TestAvnavSafeConversions:
    def test_safe_float_none(self):
        from utils.avnav_client import _safe_float
        assert _safe_float(None) is None

    def test_safe_float_string(self):
        from utils.avnav_client import _safe_float
        assert abs(_safe_float("3.14") - 3.14) < 0.001

    def test_safe_float_invalid(self):
        from utils.avnav_client import _safe_float
        assert _safe_float("not_a_number") is None

    def test_safe_float_int_input(self):
        from utils.avnav_client import _safe_float
        assert _safe_float(5) == 5.0

    def test_safe_int_none(self):
        from utils.avnav_client import _safe_int
        assert _safe_int(None) is None

    def test_safe_int_string(self):
        from utils.avnav_client import _safe_int
        assert _safe_int("7") == 7

    def test_safe_int_invalid(self):
        from utils.avnav_client import _safe_int
        assert _safe_int("abc") is None


class TestAvnavEmptyNav:
    def test_has_all_keys(self):
        from utils.avnav_client import _empty_nav
        expected = {'lat', 'lon', 'sog_ms', 'cog_deg',
                    'wp_name', 'wp_lat', 'wp_lon', 'wp_distance_m',
                    'route_name', 'route_numpoints',
                    'anchor_distance_m', 'anchor_heading_deg',
                    'recording_status'}
        assert set(_empty_nav().keys()) == expected

    def test_all_values_none(self):
        from utils.avnav_client import _empty_nav
        assert all(v is None for v in _empty_nav().values())


class TestAvnavPostOnly:
    """AvNav REST API is POST-only — GET returns HTTP 501. Client must never call GET."""

    def test_get_status_uses_post_not_get(self):
        with patch('utils.avnav_client.requests.post') as mock_post, \
             patch('utils.avnav_client.requests.get') as mock_get:
            mock_post.return_value = MagicMock(
                status_code=200, json=lambda: {'status': 'ok'})
            from utils.avnav_client import get_status
            get_status()
        assert mock_post.called
        assert not mock_get.called, 'avnav_client called requests.get — must use POST only'

    def test_get_nav_data_uses_post_not_get(self):
        with patch('utils.avnav_client.requests.post') as mock_post, \
             patch('utils.avnav_client.requests.get') as mock_get:
            mock_post.return_value = MagicMock(status_code=200, json=lambda: {})
            from utils.avnav_client import get_nav_data
            get_nav_data()
        assert mock_post.called
        assert not mock_get.called, 'avnav_client called requests.get — must use POST only'

    def test_post_body_has_request_field(self):
        """Every AvNav call must include 'request' in the POST body."""
        captured = {}
        def capture(url, data=None, **kwargs):
            captured['data'] = data
            return MagicMock(status_code=200, json=lambda: {})
        with patch('utils.avnav_client.requests.post', side_effect=capture):
            from utils.avnav_client import get_status
            get_status()
        assert 'request' in captured.get('data', {}), \
            "AvNav POST body missing 'request' field"

    def test_get_nav_data_returns_all_keys_on_failure(self):
        """If AvNav is unreachable, get_nav_data() returns all-None dict."""
        with patch('utils.avnav_client.requests.post', side_effect=ConnectionError):
            from utils.avnav_client import get_nav_data, _empty_nav
            result = get_nav_data()
        assert set(result.keys()) == set(_empty_nav().keys())
        assert all(v is None for v in result.values())

    def test_get_nav_data_does_not_use_request_navigate(self):
        """
        AvNav v20250822 has no 'request=navigate' handler — it returns a 500/error.
        get_nav_data() must use 'request=gps' and/or 'request=api' instead.

        NOTE: If this test fails, avnav_client.get_nav_data() still uses the
        broken 'request=navigate' call. Fix: replace with 'request=gps' +
        'request=api&type=route&command=getleg'.
        See deployment/d3kOS/docs/AVNAV_API_REFERENCE.md for correct API usage.
        """
        captured_requests = []
        def capture(url, data=None, **kwargs):
            captured_requests.append(data.get('request', ''))
            return MagicMock(status_code=200, json=lambda: {})
        with patch('utils.avnav_client.requests.post', side_effect=capture):
            from utils.avnav_client import get_nav_data
            get_nav_data()
        assert 'navigate' not in captured_requests, (
            "get_nav_data() is using 'request=navigate' which does not exist in "
            "AvNav v20250822. Use 'request=gps' and 'request=api&type=route&command=getleg'."
        )


class TestAvnavCurrentLeg:
    def test_file_missing_returns_empty_dict(self):
        with patch('builtins.open', side_effect=FileNotFoundError):
            from utils.avnav_client import read_current_leg
            assert read_current_leg() == {}

    def test_valid_json_returns_parsed_dict(self):
        leg = json.dumps({'toWpt': {'name': 'Marina', 'lat': 43.5, 'lon': -79.3}})
        with patch('builtins.open', mock_open(read_data=leg)), \
             patch('os.path.join', return_value='/fake/currentLeg.json'):
            from utils.avnav_client import read_current_leg
            result = read_current_leg()
        assert result.get('toWpt', {}).get('name') == 'Marina'


class TestAvnavDiskPreferred:
    def test_disk_read_before_http_api(self):
        """download_track_gpx must read from disk when available — no HTTP call."""
        fake_gpx = '<gpx><trk><trkseg></trkseg></trk></gpx>'
        with patch('os.path.isfile', return_value=True), \
             patch('builtins.open', mock_open(read_data=fake_gpx)), \
             patch('utils.avnav_client.requests.post') as mock_post:
            from utils.avnav_client import download_track_gpx
            result = download_track_gpx('2026-03-13.gpx')
        assert result == fake_gpx
        assert not mock_post.called, 'HTTP API was called despite disk file being available'


# =============================================================================
# signalk_client.py — envelope extraction + mocked HTTP
# =============================================================================

class TestSignalKExtractValue:
    def test_none_returns_none(self):
        from utils.signalk_client import _extract_value
        assert _extract_value(None) is None

    def test_dict_with_value_key(self):
        from utils.signalk_client import _extract_value
        assert _extract_value({'value': 42.0, 'source': 'gps'}) == 42.0

    def test_dict_without_value_returns_none(self):
        from utils.signalk_client import _extract_value
        assert _extract_value({'data': 1}) is None

    def test_value_can_be_nested_dict(self):
        from utils.signalk_client import _extract_value
        inner = {'latitude': 43.686, 'longitude': -79.520}
        assert _extract_value({'value': inner}) == inner


class TestSignalKSafeFloat:
    def test_none_returns_none(self):
        from utils.signalk_client import _safe_float
        assert _safe_float(None) is None

    def test_valid_string(self):
        from utils.signalk_client import _safe_float
        assert abs(_safe_float("1.5") - 1.5) < 0.001

    def test_invalid_returns_none(self):
        from utils.signalk_client import _safe_float
        assert _safe_float("bad") is None


class TestSignalKGetPosition:
    def test_returns_lat_lon_on_success(self):
        envelope = {'value': {'latitude': 43.686, 'longitude': -79.520}}
        with patch('utils.signalk_client.requests.get') as mock_get:
            mock_get.return_value = MagicMock(
                status_code=200, json=lambda: envelope)
            from utils.signalk_client import get_position
            pos = get_position()
        assert pos == {'latitude': 43.686, 'longitude': -79.520}

    def test_returns_none_on_connection_error(self):
        with patch('utils.signalk_client.requests.get', side_effect=ConnectionError):
            from utils.signalk_client import get_position
            assert get_position() is None

    def test_returns_none_when_value_missing(self):
        with patch('utils.signalk_client.requests.get') as mock_get:
            mock_get.return_value = MagicMock(status_code=200, json=lambda: {})
            from utils.signalk_client import get_position
            assert get_position() is None


class TestSignalKIsReachable:
    def test_true_on_200(self):
        with patch('utils.signalk_client.requests.get') as mock_get:
            mock_get.return_value = MagicMock(status_code=200)
            from utils.signalk_client import is_reachable
            assert is_reachable() is True

    def test_false_on_connection_error(self):
        with patch('utils.signalk_client.requests.get', side_effect=ConnectionError):
            from utils.signalk_client import is_reachable
            assert is_reachable() is False


class TestSignalKNavigationSnapshot:
    def test_all_none_when_sk_down(self):
        with patch('utils.signalk_client.requests.get', side_effect=ConnectionError):
            from utils.signalk_client import get_navigation_snapshot
            snap = get_navigation_snapshot()
        expected = {'lat', 'lon', 'sog_ms', 'cog_rad',
                    'anchor_max_radius_m', 'anchor_current_radius_m',
                    'anchor_lat', 'anchor_lon'}
        assert set(snap.keys()) == expected
        assert all(v is None for v in snap.values())


# =============================================================================
# tts.py — binary detection, empty-string guard, shell quoting
# =============================================================================

class TestTtsIsAvailable:
    def test_true_when_binary_found(self):
        with patch('utils.tts.subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            from utils.tts import is_available
            assert is_available() is True

    def test_false_when_binary_missing(self):
        with patch('utils.tts.subprocess.run', side_effect=FileNotFoundError):
            from utils.tts import is_available
            assert is_available() is False

    def test_false_when_which_exits_nonzero(self):
        import subprocess
        with patch('utils.tts.subprocess.run',
                   side_effect=subprocess.CalledProcessError(1, 'which')):
            from utils.tts import is_available
            assert is_available() is False

    def test_returns_bool_not_raises(self):
        from utils.tts import is_available
        result = is_available()
        assert isinstance(result, bool)


class TestTtsSpeak:
    def test_empty_string_returns_false(self):
        with patch('utils.tts.subprocess.Popen') as mock_popen:
            from utils.tts import speak
            assert speak('', block=True) is False
        assert not mock_popen.called

    def test_whitespace_only_returns_false(self):
        with patch('utils.tts.subprocess.Popen') as mock_popen:
            from utils.tts import speak
            assert speak('   ', block=True) is False
        assert not mock_popen.called

    def test_nonblocking_starts_thread(self):
        with patch('utils.tts.threading.Thread') as mock_thread:
            mock_thread.return_value = MagicMock()
            from utils.tts import speak
            result = speak('Anchor drag detected', block=False)
        assert result is True
        assert mock_thread.called


class TestTtsShellQuote:
    def test_basic_quoting(self):
        from utils.tts import _shell_quote
        assert _shell_quote('hello') == "'hello'"

    def test_wraps_in_single_quotes(self):
        from utils.tts import _shell_quote
        result = _shell_quote('test message')
        assert result.startswith("'") and result.endswith("'")

    def test_single_quote_in_text_escaped(self):
        from utils.tts import _shell_quote
        result = _shell_quote("don't")
        # Must not contain unescaped sequence that closes the outer quote
        assert 'don' in result
        # The internal apostrophe must be escaped
        assert result != "'don't'"

    def test_no_injection_vector(self):
        """A payload designed to break out of single-quote context must not appear verbatim."""
        from utils.tts import _shell_quote
        payload = "'; rm -rf /; '"
        result = _shell_quote(payload)
        assert payload not in result
        assert result.startswith("'") and result.endswith("'")


# =============================================================================
# voyage_logger.py — GPX parsing + privacy
# =============================================================================

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


class TestGpxParsing:
    def test_returns_expected_keys(self):
        from features.voyage_logger import parse_gpx_summary
        result = parse_gpx_summary(_SAMPLE_GPX)
        expected = {'start_lat', 'start_lon', 'end_lat', 'end_lon',
                    'start_time', 'end_time', 'elapsed_seconds',
                    'point_count', 'total_nm'}
        assert expected.issubset(set(result.keys()))

    def test_point_count(self):
        from features.voyage_logger import parse_gpx_summary
        assert parse_gpx_summary(_SAMPLE_GPX)['point_count'] == 3

    def test_start_coordinates(self):
        from features.voyage_logger import parse_gpx_summary
        r = parse_gpx_summary(_SAMPLE_GPX)
        assert abs(r['start_lat'] - 43.9367) < 0.001
        assert abs(r['start_lon'] - (-76.4900)) < 0.001

    def test_end_coordinates(self):
        from features.voyage_logger import parse_gpx_summary
        r = parse_gpx_summary(_SAMPLE_GPX)
        assert abs(r['end_lat'] - 44.0000) < 0.001

    def test_elapsed_seconds_two_hours(self):
        from features.voyage_logger import parse_gpx_summary
        assert parse_gpx_summary(_SAMPLE_GPX)['elapsed_seconds'] == 7200

    def test_total_distance_positive(self):
        from features.voyage_logger import parse_gpx_summary
        assert parse_gpx_summary(_SAMPLE_GPX)['total_nm'] > 0

    def test_empty_track_returns_none(self):
        from features.voyage_logger import parse_gpx_summary
        assert parse_gpx_summary(_EMPTY_GPX) is None

    def test_invalid_xml_returns_none(self):
        from features.voyage_logger import parse_gpx_summary
        assert parse_gpx_summary('not xml at all') is None

    def test_no_coordinate_lists_in_result(self):
        """Privacy: summary dict must not contain raw coordinate arrays."""
        from features.voyage_logger import parse_gpx_summary
        result = parse_gpx_summary(_SAMPLE_GPX)
        for key, val in result.items():
            assert not isinstance(val, list), \
                f'summary[{key!r}] is a list — raw coordinates must not be returned'


class TestVoyageLoggerPrivacy:
    """AI prompt must contain only rounded statistics, never full-precision GPS."""

    def test_prompt_does_not_contain_full_precision_start_coords(self):
        from features.voyage_logger import _LOG_PROMPT
        prompt = _LOG_PROMPT.format(
            vessel_name='Test', home_port='Toronto',
            start_lat=43.686197, start_lon=79.520877,
            end_lat=43.700123, end_lon=79.500456,
            start_time='2026-03-13T10:00:00Z', end_time='2026-03-13T11:00:00Z',
            total_nm=1.5, elapsed_hours=1.0, avg_speed=1.5, point_count=3,
        )
        assert '43.686197' not in prompt
        assert '79.520877' not in prompt

    def test_prompt_does_not_contain_full_precision_end_coords(self):
        from features.voyage_logger import _LOG_PROMPT
        prompt = _LOG_PROMPT.format(
            vessel_name='Test', home_port='Toronto',
            start_lat=43.686197, start_lon=79.520877,
            end_lat=43.700123, end_lon=79.500456,
            start_time='2026-03-13T10:00:00Z', end_time='2026-03-13T11:00:00Z',
            total_nm=1.5, elapsed_hours=1.0, avg_speed=1.5, point_count=3,
        )
        assert '43.700123' not in prompt
        assert '79.500456' not in prompt

    def test_anchor_prompt_does_not_contain_full_precision_coords(self):
        """Anchor watch AI advice prompt must use :.4f rounding."""
        from features.anchor_watch import _AI_ADVICE_PROMPT
        prompt = _AI_ADVICE_PROMPT.format(
            vessel_name='Test',
            anchor_lat=43.686197, anchor_lon=79.520877,
            current_lat=43.686512, current_lon=79.521334,
            drift_m=35.0, drift_bearing=270.0,
            sog=0.5, timestamp='2026-03-13T11:00:00Z',
        )
        assert '43.686197' not in prompt
        assert '43.686512' not in prompt


# =============================================================================
# anchor_watch.py — state machine + 3-poll debounce
# =============================================================================

class TestAnchorWatchState:
    def _make(self):
        from features.anchor_watch import AnchorWatch
        return AnchorWatch(broadcast_fn=MagicMock())

    def test_starts_inactive(self):
        aw = self._make()
        assert aw._active is False
        assert aw._alarm_active is False
        assert aw._drag_confirm_counter == 0

    def test_activate_sets_active_flag(self):
        aw = self._make()
        with patch('features.anchor_watch.tts.speak'), \
             patch('features.anchor_watch.get_navigation_snapshot',
                   return_value={k: None for k in
                                 ('lat', 'lon', 'sog_ms', 'cog_rad',
                                  'anchor_max_radius_m', 'anchor_current_radius_m',
                                  'anchor_lat', 'anchor_lon')}):
            result = aw.activate(radius_m=30.0)
        assert aw._active is True
        assert result['ok'] is True

    def test_dismiss_clears_alarm(self):
        aw = self._make()
        aw._active = True
        aw._alarm_active = True
        result = aw.dismiss()
        assert aw._alarm_active is False
        assert result['ok'] is True

    def test_dismiss_resets_counter(self):
        aw = self._make()
        aw._drag_confirm_counter = 3
        aw._alarm_active = True
        aw.dismiss()
        assert aw._drag_confirm_counter == 0

    def test_alarm_not_fired_when_inactive(self):
        aw = self._make()
        aw._active = False
        with patch('features.anchor_watch.get_anchor_data',
                   return_value={'max_radius_m': 30.0, 'current_radius_m': 99.0,
                                 'anchor_lat': 43.686, 'anchor_lon': -79.520}):
            aw._check_drag()
        assert aw._alarm_active is False


class TestAnchorWatchDebounce:
    """3 consecutive exceedances required — prevents GPS jitter false alarms."""

    def _make_active(self):
        from features.anchor_watch import AnchorWatch
        aw = AnchorWatch(broadcast_fn=MagicMock())
        aw._active = True
        return aw

    def _drag_data(self, current_r=45.0, max_r=30.0):
        return {'max_radius_m': max_r, 'current_radius_m': current_r,
                'anchor_lat': 43.686, 'anchor_lon': -79.520}

    def _snap(self):
        return {'lat': 43.687, 'lon': -79.521, 'sog_ms': 0.5, 'cog_rad': 0.0,
                'anchor_max_radius_m': 30.0, 'anchor_current_radius_m': 45.0,
                'anchor_lat': 43.686, 'anchor_lon': -79.520}

    def test_one_poll_no_alarm(self):
        aw = self._make_active()
        with patch('features.anchor_watch.get_anchor_data',
                   return_value=self._drag_data()), \
             patch('features.anchor_watch.get_navigation_snapshot',
                   return_value=self._snap()):
            aw._check_drag()
        assert aw._alarm_active is False
        assert aw._drag_confirm_counter == 1

    def test_two_polls_no_alarm(self):
        aw = self._make_active()
        with patch('features.anchor_watch.get_anchor_data',
                   return_value=self._drag_data()), \
             patch('features.anchor_watch.get_navigation_snapshot',
                   return_value=self._snap()):
            aw._check_drag()
            aw._check_drag()
        assert aw._alarm_active is False
        assert aw._drag_confirm_counter == 2

    def test_three_polls_fires_alarm(self):
        aw = self._make_active()
        with patch('features.anchor_watch.get_anchor_data',
                   return_value=self._drag_data()), \
             patch('features.anchor_watch.get_navigation_snapshot',
                   return_value=self._snap()), \
             patch('features.anchor_watch.tts.speak_urgent'), \
             patch('features.anchor_watch._log_drag_event'), \
             patch('features.anchor_watch.threading.Thread') as mock_thread:
            mock_thread.return_value = MagicMock()
            aw._check_drag()
            aw._check_drag()
            aw._check_drag()
        assert aw._alarm_active is True

    def test_non_exceedance_resets_counter(self):
        aw = self._make_active()
        aw._drag_confirm_counter = 2
        with patch('features.anchor_watch.get_anchor_data',
                   return_value=self._drag_data(current_r=20.0)):  # inside radius
            aw._check_drag()
        assert aw._drag_confirm_counter == 0
        assert aw._alarm_active is False

    def test_no_radius_in_sk_returns_early(self):
        aw = self._make_active()
        with patch('features.anchor_watch.get_anchor_data',
                   return_value={'max_radius_m': None, 'current_radius_m': 99.0,
                                 'anchor_lat': None, 'anchor_lon': None}):
            aw._check_drag()
        assert aw._drag_confirm_counter == 0

    def test_full_debounce_sequence(self):
        """1 drag → 1 non-drag (reset) → 3 drags → alarm fires. Total: 4 polls before alarm."""
        aw = self._make_active()
        snap = self._snap()

        def drag_sequence():
            yield self._drag_data()    # poll 1 — counter → 1
            yield self._drag_data(current_r=20.0)  # poll 2 — resets to 0
            yield self._drag_data()    # poll 3 — counter → 1
            yield self._drag_data()    # poll 4 — counter → 2
            yield self._drag_data()    # poll 5 — counter → 3, fires

        gen = drag_sequence()

        fired = []
        aw._broadcast = lambda e, d: fired.append(e) if e == 'anchor_alert' else None

        with patch('features.anchor_watch.get_anchor_data', side_effect=gen), \
             patch('features.anchor_watch.get_navigation_snapshot', return_value=snap), \
             patch('features.anchor_watch.tts.speak_urgent'), \
             patch('features.anchor_watch._log_drag_event'), \
             patch('features.anchor_watch.threading.Thread') as mt:
            mt.return_value = MagicMock()
            for _ in range(5):
                aw._check_drag()

        assert len(fired) == 1
        assert aw._alarm_active is True


# =============================================================================
# ai_bridge.py — Flask route tests
# =============================================================================

@pytest.fixture(scope='module')
def flask_app():
    """
    Import ai_bridge and return the Flask app for testing.
    No background threads are started (they only start in __main__).
    All external HTTP calls are patched per-test.
    """
    import ai_bridge
    ai_bridge.app.config['TESTING'] = True
    return ai_bridge.app


@pytest.fixture
def client(flask_app):
    return flask_app.test_client()


class TestFlaskStatus:
    def test_returns_200(self, client):
        with patch('ai_bridge.sk_reachable', return_value=True), \
             patch('ai_bridge.avnav_status', return_value={'status': 'ok'}), \
             patch('ai_bridge.requests.get') as mock_get, \
             patch('ai_bridge.tts.is_available', return_value=True):
            mock_get.return_value = MagicMock(status_code=200)
            resp = client.get('/status')
        assert resp.status_code == 200

    def test_has_service_name(self, client):
        with patch('ai_bridge.sk_reachable', return_value=True), \
             patch('ai_bridge.avnav_status', return_value={}), \
             patch('ai_bridge.requests.get') as mock_get, \
             patch('ai_bridge.tts.is_available', return_value=True):
            mock_get.return_value = MagicMock(status_code=200)
            data = json.loads(client.get('/status').data)
        assert data['service'] == 'd3kos-ai-bridge'

    def test_has_all_subsystem_fields(self, client):
        with patch('ai_bridge.sk_reachable', return_value=True), \
             patch('ai_bridge.avnav_status', return_value={}), \
             patch('ai_bridge.requests.get') as mock_get, \
             patch('ai_bridge.tts.is_available', return_value=True):
            mock_get.return_value = MagicMock(status_code=200)
            data = json.loads(client.get('/status').data)
        for field in ('signalk', 'avnav', 'gemini_proxy', 'tts_available', 'port', 'timestamp'):
            assert field in data, f'Missing field: {field}'

    def test_reports_down_when_sk_unreachable(self, client):
        with patch('ai_bridge.sk_reachable', return_value=False), \
             patch('ai_bridge.avnav_status', return_value=None), \
             patch('ai_bridge.requests.get', side_effect=ConnectionError), \
             patch('ai_bridge.tts.is_available', return_value=False):
            data = json.loads(client.get('/status').data)
        assert data['signalk'] == 'down'
        assert data['avnav'] == 'down'


class TestFlaskStream:
    def test_returns_text_event_stream_content_type(self, client):
        with client.get('/stream', buffered=False) as resp:
            assert 'text/event-stream' in resp.content_type


class TestFlaskWebhookAlert:
    def test_missing_message_returns_400(self, client):
        resp = client.post('/webhook/alert',
                           json={'severity': 'info'},
                           content_type='application/json')
        assert resp.status_code == 400

    def test_empty_message_returns_400(self, client):
        resp = client.post('/webhook/alert',
                           json={'message': '   '},
                           content_type='application/json')
        assert resp.status_code == 400

    def test_no_body_returns_400(self, client):
        resp = client.post('/webhook/alert')
        assert resp.status_code == 400

    def test_valid_message_returns_200(self, client):
        with patch('ai_bridge.tts.speak_urgent'):
            resp = client.post('/webhook/alert',
                               json={'message': 'Engine overheat', 'severity': 'critical'},
                               content_type='application/json')
        assert resp.status_code == 200
        assert json.loads(resp.data)['ok'] is True

    def test_critical_severity_repeats_twice(self, client):
        calls = []
        def capture_speak(text, repeat=1):
            calls.append(repeat)
        with patch('ai_bridge.tts.speak_urgent', side_effect=capture_speak):
            client.post('/webhook/alert',
                        json={'message': 'MAYDAY', 'severity': 'critical'},
                        content_type='application/json')
        assert calls and calls[0] == 2, 'Critical severity must repeat=2'

    def test_info_severity_repeats_once(self, client):
        calls = []
        def capture_speak(text, repeat=1):
            calls.append(repeat)
        with patch('ai_bridge.tts.speak_urgent', side_effect=capture_speak):
            client.post('/webhook/alert',
                        json={'message': 'Waypoint reached', 'severity': 'info'},
                        content_type='application/json')
        assert calls and calls[0] == 1, 'Info severity must repeat=1'


class TestFlaskWebhookArrival:
    def test_missing_destination_returns_400(self, client):
        resp = client.post('/webhook/arrival',
                           json={'lat': 43.5, 'lon': -79.3},
                           content_type='application/json')
        assert resp.status_code == 400

    def test_empty_destination_returns_400(self, client):
        resp = client.post('/webhook/arrival',
                           json={'destination': '', 'lat': 0.0, 'lon': 0.0},
                           content_type='application/json')
        assert resp.status_code == 400

    def test_valid_destination_returns_200(self, client):
        resp = client.post('/webhook/arrival',
                           json={'destination': 'Port Credit Marina',
                                 'lat': 43.550, 'lon': -79.583},
                           content_type='application/json')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['ok'] is True
        assert data['destination'] == 'Port Credit Marina'


class TestFlaskAnchorActivate:
    def test_invalid_radius_returns_400(self, client):
        resp = client.post('/anchor/activate',
                           json={'radius_m': 'not_a_number'},
                           content_type='application/json')
        assert resp.status_code == 400

    def test_no_body_returns_200(self, client):
        """Empty body is valid — uses Signal K radius."""
        resp = client.post('/anchor/activate',
                           data='', content_type='application/json')
        assert resp.status_code == 200

    def test_valid_radius_returns_200(self, client):
        resp = client.post('/anchor/activate',
                           json={'radius_m': 30.0},
                           content_type='application/json')
        assert resp.status_code == 200


class TestFlaskAnchorDismiss:
    def test_returns_200(self, client):
        assert client.post('/anchor/dismiss').status_code == 200

    def test_returns_ok_true(self, client):
        data = json.loads(client.post('/anchor/dismiss').data)
        assert data['ok'] is True


class TestFlaskVoyages:
    def test_returns_200(self, client):
        assert client.get('/voyages').status_code == 200

    def test_has_ok_and_summaries_list(self, client):
        data = json.loads(client.get('/voyages').data)
        assert data.get('ok') is True
        assert isinstance(data.get('summaries'), list)


class TestFlaskAnalyzeRoute:
    def test_returns_200(self, client):
        assert client.post('/analyze-route').status_code == 200

    def test_returns_ok_true(self, client):
        data = json.loads(client.post('/analyze-route').data)
        assert data['ok'] is True


class TestFlaskWebhookQuery:
    def test_missing_query_returns_400(self, client):
        resp = client.post('/webhook/query',
                           json={},
                           content_type='application/json')
        assert resp.status_code == 400

    def test_empty_query_returns_400(self, client):
        resp = client.post('/webhook/query',
                           json={'query': '   '},
                           content_type='application/json')
        assert resp.status_code == 400

    def test_valid_query_proxied_to_gemini(self, client):
        fake_ai = MagicMock(status_code=200)
        fake_ai.json.return_value = {'response': 'VHF 16 is distress channel', 'source': 'gemini'}
        fake_ai.raise_for_status = lambda: None
        with patch('ai_bridge.requests.post', return_value=fake_ai):
            resp = client.post('/webhook/query',
                               json={'query': 'What is VHF channel 16?'},
                               content_type='application/json')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['ok'] is True
        assert 'response' in data


# =============================================================================
# Integration tests — require live Pi at 192.168.1.237
# =============================================================================

@pytest.mark.integration
class TestIntegrationAvNav:
    def test_status_responds(self):
        from utils.avnav_client import get_status
        assert get_status() is not None

    def test_gps_request_returns_signalk_keys(self):
        import requests as req
        resp = req.post(
            'http://192.168.1.237:8080/viewer/avnav_navi.php',
            data={'request': 'gps'}, timeout=5)
        data = resp.json()
        assert 'signalk' in data
        assert 'navigation' in data['signalk']
        assert 'position' in data['signalk']['navigation']

    def test_get_returns_501(self):
        """Confirms AvNav rejects GET — POST-only enforcement is required."""
        import requests as req
        resp = req.get(
            'http://192.168.1.237:8080/viewer/avnav_navi.php', timeout=5)
        assert resp.status_code == 501


@pytest.mark.integration
class TestIntegrationSignalK:
    def test_is_reachable(self):
        from utils.signalk_client import is_reachable
        assert is_reachable() is True

    def test_position_in_toronto_area(self):
        from utils.signalk_client import get_position
        pos = get_position()
        assert pos is not None
        assert 43.0 < pos['latitude'] < 44.5


@pytest.mark.integration
class TestIntegrationAiBridge:
    def test_status_all_up(self):
        import requests as req
        data = req.get('http://192.168.1.237:3002/status', timeout=5).json()
        assert data['avnav'] == 'up'
        assert data['signalk'] == 'up'
        assert data['gemini_proxy'] == 'up'
        assert data['tts_available'] is True

    def test_webhook_query_returns_ai_response(self):
        import requests as req
        resp = req.post(
            'http://192.168.1.237:3002/webhook/query',
            json={'query': 'What does VHF channel 16 mean on a boat?'},
            timeout=30)
        data = resp.json()
        assert data['ok'] is True
        assert len(data.get('response', '')) > 10

    def test_webhook_alert_fires(self):
        import requests as req
        data = req.post(
            'http://192.168.1.237:3002/webhook/alert',
            json={'message': 'AI Bridge integration test.', 'severity': 'info'},
            timeout=10).json()
        assert data['ok'] is True
