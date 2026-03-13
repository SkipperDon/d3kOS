"""
d3kOS AI Bridge — Signal K client (REST polling, no WebSocket dependency)

Uses Signal K REST API at http://localhost:8099/signalk/v1/api/vessels/self/
Confirmed key paths from live Pi probe (2026-03-13):
  navigation.position.latitude   / longitude
  navigation.speedOverGround     (m/s)
  navigation.courseOverGroundTrue (radians)
"""

import os
import logging
import requests

log = logging.getLogger(__name__)

_SK_BASE = 'http://localhost:8099/signalk/v1/api/vessels/self'
_TIMEOUT = 5  # seconds


def _get(path: str) -> dict | None:
    """
    GET a Signal K path under /vessels/self.
    path: e.g. 'navigation/position'
    Returns the Signal K value envelope dict or None on failure.
    """
    url = f'{_SK_BASE}/{path}'
    try:
        resp = requests.get(url, timeout=_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        log.debug('Signal K GET failed (%s): %s', path, exc)
        return None


def _extract_value(envelope: dict | None):
    """Extract the 'value' field from a Signal K envelope."""
    if envelope is None:
        return None
    return envelope.get('value')


def get_position() -> dict | None:
    """
    Returns {'latitude': float, 'longitude': float} or None.
    Confirmed live path: navigation/position
    """
    data = _get('navigation/position')
    val = _extract_value(data)
    if isinstance(val, dict) and 'latitude' in val:
        return {'latitude': float(val['latitude']), 'longitude': float(val['longitude'])}
    return None


def get_sog() -> float | None:
    """
    Speed over ground in m/s. Convert to knots with geo.ms_to_knots().
    Confirmed live path: navigation/speedOverGround
    """
    data = _get('navigation/speedOverGround')
    val = _extract_value(data)
    try:
        return float(val) if val is not None else None
    except (TypeError, ValueError):
        return None


def get_cog() -> float | None:
    """
    Course over ground in radians. Convert to degrees with geo.rad_to_deg().
    Confirmed live path: navigation/courseOverGroundTrue
    """
    data = _get('navigation/courseOverGroundTrue')
    val = _extract_value(data)
    try:
        return float(val) if val is not None else None
    except (TypeError, ValueError):
        return None


def get_heading_magnetic() -> float | None:
    """Magnetic heading in radians. May not be present on all setups."""
    data = _get('navigation/headingMagnetic')
    val = _extract_value(data)
    try:
        return float(val) if val is not None else None
    except (TypeError, ValueError):
        return None


def get_anchor_data() -> dict:
    """
    Returns anchor watch state from Signal K:
      max_radius_m:     float or None  (metres — set by skipper)
      current_radius_m: float or None  (metres — live distance from anchor)
      anchor_lat:       float or None
      anchor_lon:       float or None

    All values None if anchor watch is not active.
    """
    result = {
        'max_radius_m':     None,
        'current_radius_m': None,
        'anchor_lat':       None,
        'anchor_lon':       None,
    }

    max_r = _get('navigation/anchor/maxRadius')
    result['max_radius_m'] = _safe_float(_extract_value(max_r))

    cur_r = _get('navigation/anchor/currentRadius')
    result['current_radius_m'] = _safe_float(_extract_value(cur_r))

    pos = _get('navigation/anchor/position')
    pos_val = _extract_value(pos)
    if isinstance(pos_val, dict):
        result['anchor_lat'] = _safe_float(pos_val.get('latitude'))
        result['anchor_lon'] = _safe_float(pos_val.get('longitude'))

    return result


def get_engine_data() -> dict:
    """
    Returns engine data. Keys may be absent if NMEA 2000 engine not connected.
      run_time_s:          seconds (int) or None
      coolant_temp_k:      Kelvin (float) or None
      oil_pressure_pa:     Pascals (float) or None
    """
    result = {
        'run_time_s':      None,
        'coolant_temp_k':  None,
        'oil_pressure_pa': None,
    }

    rt = _get('propulsion/0/runTime')
    result['run_time_s'] = _safe_float(_extract_value(rt))

    ct = _get('propulsion/0/coolantTemperature')
    result['coolant_temp_k'] = _safe_float(_extract_value(ct))

    op = _get('propulsion/0/oilPressure')
    result['oil_pressure_pa'] = _safe_float(_extract_value(op))

    return result


def get_navigation_snapshot() -> dict:
    """
    Fetch all navigation fields in parallel (separate REST calls).
    Returns a consolidated dict — used by features that need the full picture.

    Keys (all may be None):
      lat, lon, sog_ms, cog_rad,
      anchor_max_radius_m, anchor_current_radius_m, anchor_lat, anchor_lon
    """
    pos     = get_position()
    sog     = get_sog()
    cog     = get_cog()
    anchor  = get_anchor_data()

    return {
        'lat':                    pos['latitude']  if pos else None,
        'lon':                    pos['longitude'] if pos else None,
        'sog_ms':                 sog,
        'cog_rad':                cog,
        'anchor_max_radius_m':    anchor['max_radius_m'],
        'anchor_current_radius_m': anchor['current_radius_m'],
        'anchor_lat':             anchor['anchor_lat'],
        'anchor_lon':             anchor['anchor_lon'],
    }


def is_reachable() -> bool:
    """Quick connectivity check — returns True if Signal K REST API responds."""
    try:
        resp = requests.get('http://localhost:8099/signalk', timeout=3)
        return resp.status_code == 200
    except Exception:
        return False


def _safe_float(val) -> float | None:
    try:
        return float(val) if val is not None else None
    except (TypeError, ValueError):
        return None
