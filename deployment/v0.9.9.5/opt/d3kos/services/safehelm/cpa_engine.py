# cpa_engine.py
import math

KTS_TO_MS = 0.514444
M_PER_DEG_LAT = 111320.0

def compute_cpa_tcpa(own_lat, own_lon, own_sog, own_cog,
                     tgt_lat, tgt_lon, tgt_sog, tgt_cog):
    """(cpa_m, tcpa_s, range_m). tcpa_s < 0 => already passed. inf => no relative motion.

    Flat-earth approximation; valid well inside the 2 NM gating range of §8.2.
    """
    m_per_deg_lon = M_PER_DEG_LAT * math.cos(math.radians(own_lat))
    dx = (tgt_lon - own_lon) * m_per_deg_lon      # metres east
    dy = (tgt_lat - own_lat) * M_PER_DEG_LAT      # metres north
    range_m = math.hypot(dx, dy)

    ovx = own_sog * KTS_TO_MS * math.sin(math.radians(own_cog))
    ovy = own_sog * KTS_TO_MS * math.cos(math.radians(own_cog))
    tvx = tgt_sog * KTS_TO_MS * math.sin(math.radians(tgt_cog))
    tvy = tgt_sog * KTS_TO_MS * math.cos(math.radians(tgt_cog))
    rvx, rvy = tvx - ovx, tvy - ovy
    v2 = rvx * rvx + rvy * rvy

    if v2 < 1e-9:
        return range_m, float('inf'), range_m

    tcpa = -(dx * rvx + dy * rvy) / v2
    if tcpa < 0.0:
        return range_m, tcpa, range_m
    cpa = math.hypot(dx + rvx * tcpa, dy + rvy * tcpa)
    return cpa, tcpa, range_m
