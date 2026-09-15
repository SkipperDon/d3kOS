# alert_gate.py
import math

NM = 1852.0
HEADON_TCPA_BONUS_S = 120.0

#      tier,        cpa_max_m, tcpa_max_s, range_max_m, voice
TIERS = (
    ('critical',    150.0,     240.0,      0.75 * NM,   'repeat'),
    ('warning',     300.0,     420.0,      1.50 * NM,   'once'),
    ('advisory',    500.0,     600.0,      2.00 * NM,   None),
)

def classify_tier(cpa_m, tcpa_s, range_m, is_headon=False):
    """Highest qualifying tier, or None. None means: log it, never voice it."""
    if tcpa_s is None or math.isinf(tcpa_s) or math.isnan(tcpa_s):
        return None
    if tcpa_s < 0.0:
        return None
    bonus = HEADON_TCPA_BONUS_S if is_headon else 0.0
    for tier, cpa_max, tcpa_max, range_max, voice in TIERS:
        if cpa_m <= cpa_max and tcpa_s <= tcpa_max + bonus and range_m <= range_max:
            return {'tier': tier, 'voice': voice}
    return None
