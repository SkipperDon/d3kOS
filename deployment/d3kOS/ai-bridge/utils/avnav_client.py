"""
d3kOS AI Bridge — AvNav REST client
All requests use POST to avnav_navi.php — GET returns HTTP 501.

Confirmed working endpoints (AvNav 20250822):
  request=gps                                → basic update timestamps + SignalK data
  request=status                             → handler status dict
  request=list&type=route|track              → file lists
  request=api&type=route&command=getleg      → active leg (route name, waypoints)
  request=api&type=route&command=setleg      → set active leg
  request=api&type=route&command=unsetleg    → clear active leg
  request=api&type=track&command=getTrackV2  → current track points

NOTE: 'request=navigate' does NOT exist in AvNav — returns 500.
GPS position comes from Signal K REST (signalk_client.py), not AvNav.
"""

import math
import os
import logging
import requests

log = logging.getLogger(__name__)

AVNAV_API      = os.environ.get('AVNAV_API', 'http://localhost:8080/viewer/avnav_navi.php')
AVNAV_DATA_DIR = os.environ.get('AVNAV_DATA_DIR', '/var/lib/avnav')

_NM_PER_METRE = 1 / 1852.0
_EARTH_RADIUS_M = 6_371_000


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
    Fetch current navigation state from AvNav + recording status.

    Uses two endpoints:
      1. request=gps  → SignalK-sourced lat/lon/SOG embedded in response
      2. request=api&type=route&command=getleg → active route/waypoint data

    wp_distance_m is computed locally via haversine when lat/lon are available.

    Returns a flat dict with normalised keys:
      lat, lon, sog_ms, cog_deg,
      wp_name, wp_lat, wp_lon, wp_distance_m,
      route_name, route_numpoints,
      anchor_distance_m, anchor_heading_deg,
      recording_status
    All values are None if not available.
    """
    out = _empty_nav()

    # ── 1. GPS position from request=gps (SignalK data embedded) ──────────────
    gps_result = _post({'request': 'gps'})
    if gps_result:
        sk = gps_result.get('signalk', {})
        nav_sk = sk.get('navigation', {})
        pos = nav_sk.get('position', {})
        out['lat']    = _safe_float(pos.get('latitude'))
        out['lon']    = _safe_float(pos.get('longitude'))
        out['sog_ms'] = _safe_float(nav_sk.get('speedOverGround'))
        out['cog_deg']= _safe_float(nav_sk.get('courseOverGroundTrue'))

        # Track recording status: check update timestamps
        # AvNav sets updateroute when a track is active
        out['recording_status'] = _detect_recording_status()

    # ── 2. Active leg from route API ───────────────────────────────────────────
    leg_result = _post({'request': 'api', 'type': 'route', 'command': 'getleg'})
    if leg_result and leg_result.get('active'):
        route = leg_result.get('currentRoute') or {}
        to_wp = leg_result.get('to') or {}
        from_wp = leg_result.get('from') or {}
        points  = route.get('points') or []

        out['route_name']      = route.get('name')
        out['route_numpoints'] = len(points) if points else None
        out['wp_name']         = to_wp.get('name')
        out['wp_lat']          = _safe_float(to_wp.get('lat'))
        out['wp_lon']          = _safe_float(to_wp.get('lon'))

        # Anchor watch: anchorDistance in leg means anchor mode is active
        anchor_m = leg_result.get('anchorDistance')
        if anchor_m is not None:
            out['anchor_distance_m'] = _safe_float(anchor_m)

        # Compute distance to next waypoint if we have position + waypoint
        if (out['lat'] is not None and out['lon'] is not None
                and out['wp_lat'] is not None and out['wp_lon'] is not None):
            out['wp_distance_m'] = _haversine_m(
                out['lat'], out['lon'], out['wp_lat'], out['wp_lon']
            )

    return out


def _detect_recording_status() -> str | None:
    """
    Infer AvNav recording status from today's track file modification time.
    Returns 'recording' if modified within last 90s, 'stopped' if older, None if no file.
    """
    import time
    import glob as _glob
    from datetime import datetime, timezone
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    pattern = os.path.join(AVNAV_DATA_DIR, 'tracks', f'{today}.gpx')
    matches = _glob.glob(pattern)
    if not matches:
        return None
    mtime = os.path.getmtime(matches[0])
    age_s = time.time() - mtime
    return 'recording' if age_s < 90 else 'stopped'


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return distance in metres between two lat/lon points."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi  = math.radians(lat2 - lat1)
    dlam  = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return 2 * _EARTH_RADIUS_M * math.asin(math.sqrt(a))


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
