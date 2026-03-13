"""
d3kOS AI Bridge — AvNav REST client
All requests use POST to avnav_navi.php — GET returns HTTP 501.
"""

import os
import logging
import requests

log = logging.getLogger(__name__)

AVNAV_API = os.environ.get('AVNAV_API', 'http://localhost:8080/viewer/avnav_navi.php')
AVNAV_DATA_DIR = os.environ.get('AVNAV_DATA_DIR', '/var/lib/avnav')

# Keys to fetch for navigation state in one POST call.
_NAV_KEYS = ','.join([
    'gps.lat',
    'gps.lon',
    'gps.speed',        # m/s — same as SOG from Signal K
    'gps.track',        # degrees
    'nav.wp.name',
    'nav.wp.lat',
    'nav.wp.lon',
    'nav.wp.distance',  # metres
    'nav.route.name',
    'nav.route.numpoints',
    'nav.anchor.distance',
    'nav.anchor.heading',
    'nav.recordingStatus',
])


def _post(data: dict, timeout: int = 8) -> dict | None:
    """
    POST form-encoded data to AvNav API.
    Returns parsed JSON dict or None on failure.
    """
    try:
        resp = requests.post(
            AVNAV_API,
            data=data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=timeout,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        log.warning('AvNav POST failed (%s): %s', data.get('request'), exc)
        return None


def get_status() -> dict | None:
    """Check AvNav service status. Returns raw JSON or None."""
    return _post({'request': 'status'})


def get_nav_data() -> dict:
    """
    Fetch current navigation state from AvNav.

    Returns a flat dict with normalised keys:
      lat, lon, sog_ms, cog_deg,
      wp_name, wp_lat, wp_lon, wp_distance_m,
      route_name, route_numpoints,
      anchor_distance_m, anchor_heading_deg,
      recording_status
    All values are None if not available.
    """
    result = _post({'request': 'navigate', 'keys': _NAV_KEYS})
    if result is None:
        return _empty_nav()

    # AvNav returns data nested under 'data' key
    raw = result.get('data', result)

    def _get(key):
        # AvNav sometimes nests under 'values' subkey
        val = raw.get(key)
        if val is None:
            return None
        if isinstance(val, dict):
            return val.get('value')
        return val

    try:
        return {
            'lat':                _safe_float(_get('gps.lat')),
            'lon':                _safe_float(_get('gps.lon')),
            'sog_ms':             _safe_float(_get('gps.speed')),
            'cog_deg':            _safe_float(_get('gps.track')),
            'wp_name':            _get('nav.wp.name'),
            'wp_lat':             _safe_float(_get('nav.wp.lat')),
            'wp_lon':             _safe_float(_get('nav.wp.lon')),
            'wp_distance_m':      _safe_float(_get('nav.wp.distance')),
            'route_name':         _get('nav.route.name'),
            'route_numpoints':    _safe_int(_get('nav.route.numpoints')),
            'anchor_distance_m':  _safe_float(_get('nav.anchor.distance')),
            'anchor_heading_deg': _safe_float(_get('nav.anchor.heading')),
            'recording_status':   _get('nav.recordingStatus'),
        }
    except Exception as exc:
        log.warning('AvNav nav data parse error: %s', exc)
        return _empty_nav()


def get_route_list() -> list:
    """Return list of available routes from AvNav. Each item is a dict."""
    result = _post({'request': 'list', 'type': 'route'})
    if result is None:
        return []
    return result.get('items', [])


def get_track_list() -> list:
    """Return list of available tracks from AvNav. Each item is a dict."""
    result = _post({'request': 'list', 'type': 'track'})
    if result is None:
        return []
    return result.get('items', [])


def download_track_gpx(filename: str) -> str | None:
    """
    Download a GPX track file from AvNav by filename (e.g. '2026-03-13.gpx').
    Returns GPX text content or None on failure.

    Preferred approach: read directly from disk if AVNAV_DATA_DIR is accessible.
    Falls back to POST download API.
    """
    # Direct disk read is preferred — avoids HTTP roundtrip
    disk_path = os.path.join(AVNAV_DATA_DIR, 'tracks', filename)
    if os.path.isfile(disk_path):
        try:
            with open(disk_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as exc:
            log.warning('AvNav track disk read failed (%s): %s', disk_path, exc)

    # API fallback
    try:
        resp = requests.post(
            AVNAV_API,
            data={'request': 'download', 'name': filename, 'type': 'track'},
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.text
    except Exception as exc:
        log.warning('AvNav track download failed (%s): %s', filename, exc)
        return None


def read_current_leg() -> dict:
    """
    Read currentLeg.json directly from AvNav data directory.
    Returns parsed dict (may be empty dict if no active route).
    """
    import json
    path = os.path.join(AVNAV_DATA_DIR, 'routes', 'currentLeg.json')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as exc:
        log.warning('currentLeg.json read failed: %s', exc)
        return {}


def _empty_nav() -> dict:
    return {k: None for k in (
        'lat', 'lon', 'sog_ms', 'cog_deg',
        'wp_name', 'wp_lat', 'wp_lon', 'wp_distance_m',
        'route_name', 'route_numpoints',
        'anchor_distance_m', 'anchor_heading_deg',
        'recording_status',
    )}


def _safe_float(val) -> float | None:
    try:
        return float(val) if val is not None else None
    except (TypeError, ValueError):
        return None


def _safe_int(val) -> int | None:
    try:
        return int(val) if val is not None else None
    except (TypeError, ValueError):
        return None
