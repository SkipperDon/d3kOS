"""
d3kOS AI Bridge — Geographic utilities
Haversine distance, bearing, and unit conversions.
"""

import math


EARTH_RADIUS_NM = 3440.065  # nautical miles


def haversine_nm(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Distance in nautical miles between two lat/lon points (decimal degrees).
    Uses haversine formula — accurate for small and medium distances.
    """
    lat1_r = math.radians(lat1)
    lat2_r = math.radians(lat2)
    dlat   = math.radians(lat2 - lat1)
    dlon   = math.radians(lon2 - lon1)

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_NM * c


def bearing_degrees(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Initial bearing in degrees (0-360, clockwise from north) from point 1 to point 2.
    """
    lat1_r = math.radians(lat1)
    lat2_r = math.radians(lat2)
    dlon   = math.radians(lon2 - lon1)

    x = math.sin(dlon) * math.cos(lat2_r)
    y = math.cos(lat1_r) * math.sin(lat2_r) - math.sin(lat1_r) * math.cos(lat2_r) * math.cos(dlon)
    bearing = math.degrees(math.atan2(x, y))
    return (bearing + 360) % 360


def ms_to_knots(speed_ms: float) -> float:
    """Convert metres-per-second to knots (Signal K SOG is m/s)."""
    return speed_ms * 1.94384


def rad_to_deg(radians: float) -> float:
    """Convert radians to degrees (Signal K COG/heading is radians)."""
    return math.degrees(radians) % 360


def nm_to_metres(nm: float) -> float:
    """Convert nautical miles to metres."""
    return nm * 1852.0


def metres_to_nm(metres: float) -> float:
    """Convert metres to nautical miles."""
    return metres / 1852.0


def gpx_total_distance_nm(points: list) -> float:
    """
    Calculate total track distance in nautical miles from a list of
    (lat, lon) tuples representing consecutive track points.
    """
    if len(points) < 2:
        return 0.0
    total = 0.0
    for i in range(1, len(points)):
        total += haversine_nm(points[i - 1][0], points[i - 1][1],
                              points[i][0],     points[i][1])
    return total
