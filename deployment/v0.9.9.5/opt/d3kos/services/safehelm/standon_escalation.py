# standon_escalation.py — pure. History lives with the caller.
STAGE_HOLD     = 'hold'       # 17(a)(i)
STAGE_MAY_ACT  = 'may_act'    # 17(a)(ii)
STAGE_MUST_ACT = 'must_act'   # 17(b)

# Rule 8(b) requires alterations "large enough to be readily apparent to another
# vessel observing visually or by radar". Tunables #6-#8 (§12.3 6a).
APPARENT_COURSE_CHANGE_DEG = 10.0
APPARENT_SPEED_CHANGE_FRAC = 0.20
NO_ACTION_WINDOW_S         = 60.0
MUST_ACT_TCPA_S            = 120.0

# §8.0 liveness signal — heartbeat interval so callers can detect a silent engine.
HEARTBEAT_INTERVAL_S = 5.0


def _ang_diff(a, b):
    return abs((b - a + 180.0) % 360.0 - 180.0)


def target_has_manoeuvred(track, now, window_s=NO_ACTION_WINDOW_S):
    """track: [(t, cog, sog)] oldest first. Did the target visibly act?

    FAILS SAFE TOWARDS 'yes'. On thin data we must not accuse the other vessel
    of inaction: that would push the captain to manoeuvre while 17(a)(i) still
    says hold course, which is its own hazard.
    """
    recent = [p for p in track if now - p[0] <= window_s]
    if len(recent) < 2:
        return True
    t0, cog0, sog0 = recent[0]
    turned = max(_ang_diff(cog0, c) for _, c, _ in recent) >= APPARENT_COURSE_CHANGE_DEG
    slowed = (max(abs(s - sog0) for _, _, s in recent) / max(sog0, 0.1)
              >= APPARENT_SPEED_CHANGE_FRAC)
    return turned or slowed


def escalation_stage(tier, tcpa_s, track, now):
    """Rule 17 stage. Call ONLY when we hold a stand-on role."""
    # 17(b) is proximity alone and does NOT depend on track data -- it must
    # fire even for a target we have only just acquired.
    if (tier == 'critical' and tcpa_s is not None
            and 0.0 <= tcpa_s <= MUST_ACT_TCPA_S):
        return STAGE_MUST_ACT
    if not target_has_manoeuvred(track, now):
        return STAGE_MAY_ACT
    return STAGE_HOLD


STANDON_PHRASES = {
    STAGE_MAY_ACT:  'Warning. Give-way vessel is not altering. You may now take action. '
                    'COLREGs advise against altering to port.',          # 17(a)(ii)+17(c)
    STAGE_MUST_ACT: 'Danger. Collision cannot be avoided by the other vessel alone. '
                    'COLREGs require you to act now.',                    # 17(b)
    # §8.0 — engine failure announcement. Must state advisory has stopped.
    'engine_failure': 'SafeHelm advisory has stopped. Collision avoidance is not running.',
}
