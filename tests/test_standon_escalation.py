"""E1-E8 -- Rule 17 stand-on escalation guards (V09995-SOL-001 §8.9, gate 7c).

Found by the §14 Part B enumeration. v1.6 said "You are Stand-On. Monitor."
and stopped. Rule 17 does not stop there:

  17(a)(i)  the stand-on vessel shall keep her course and speed
  17(a)(ii) she MAY act once it becomes apparent the give-way vessel is not
            taking appropriate action
  17(b)     she SHALL act when so close that collision cannot be avoided by
            the give-way vessel alone
  17(c)     and shall not alter to port for a vessel on her own port side

A stand-on vessel holding course into a collision is the failure mode in much
of the collision case law. Telling a captain "Monitor" with no escalation is
the software equivalent.
"""
import pytest

from conftest import lazy_module

SPEC = '§8.9'

NOW = 1_000_000.0


@pytest.fixture
def esc():
    return lazy_module('standon_escalation', SPEC)


def _steady_track(now=NOW, n=7, cog=90.0, sog=10.0, step=10.0):
    """A target holding course and speed -- i.e. not taking action."""
    return [(now - step * (n - 1 - i), cog, sog) for i in range(n)]


def _turning_track(now=NOW, n=7, cog=90.0, sog=10.0, total_turn=25.0, step=10.0):
    """A target making a readily-apparent alteration (Rule 8(b))."""
    return [(now - step * (n - 1 - i), cog + total_turn * i / (n - 1), sog)
            for i in range(n)]


# --------------------------------------------------------------------------
# 17(a)(i) -- the default.
# --------------------------------------------------------------------------

def test_e1_give_way_vessel_acting_means_we_hold(esc):
    """E1: 17(a)(i). The other vessel is turning, so we keep course and speed."""
    assert esc.escalation_stage('warning', 300.0, _turning_track(), NOW) == esc.STAGE_HOLD


def test_e2_a_slowing_target_also_counts_as_acting(esc):
    """E2: Rule 8 permits action by speed as well as course."""
    track = [(NOW - 60 + 10 * i, 90.0, 10.0 - 0.5 * i) for i in range(7)]
    assert esc.escalation_stage('warning', 300.0, track, NOW) == esc.STAGE_HOLD


# --------------------------------------------------------------------------
# 17(a)(ii) -- permission unlocks.
# --------------------------------------------------------------------------

def test_e3_steady_give_way_vessel_unlocks_permission_to_act(esc):
    """E3: 17(a)(ii). THE GAP GUARD.

    The give-way vessel has held course and speed throughout the window while
    risk persists. The captain needs to be told the permission has unlocked --
    v1.6 would have said "Monitor" indefinitely.
    """
    assert esc.escalation_stage('warning', 300.0,
                                _steady_track(), NOW) == esc.STAGE_MAY_ACT


def test_e4_thin_track_data_fails_safe_towards_hold(esc):
    """E4: never accuse the other vessel of inaction on insufficient data.

    Doing so would push the captain to manoeuvre while 17(a)(i) still says
    hold course, which is its own hazard. One report is not evidence of
    anything.
    """
    assert esc.escalation_stage('warning', 300.0,
                                [(NOW, 90.0, 10.0)], NOW) == esc.STAGE_HOLD
    assert esc.escalation_stage('warning', 300.0, [], NOW) == esc.STAGE_HOLD


def test_e4b_stale_track_points_are_not_counted(esc):
    """E4b: a turn made five minutes ago is not evidence of acting now."""
    old_turn = [(NOW - 400, 90.0, 10.0), (NOW - 380, 120.0, 10.0)]
    steady_since = [(NOW - 50 + 10 * i, 120.0, 10.0) for i in range(6)]
    assert esc.escalation_stage('warning', 300.0,
                                old_turn + steady_since, NOW) == esc.STAGE_MAY_ACT


# --------------------------------------------------------------------------
# 17(b) -- the duty.
# --------------------------------------------------------------------------

def test_e5_imminent_collision_creates_a_duty_to_act(esc):
    """E5: 17(b). "shall take such action as will best aid to avoid collision"."""
    assert esc.escalation_stage('critical', 90.0,
                                _turning_track(), NOW) == esc.STAGE_MUST_ACT


def test_e6_duty_does_not_depend_on_track_history(esc):
    """E6: 17(b) is proximity alone.

    It must fire for a target acquired thirty seconds ago. Gating the duty on
    having enough history would suppress the single most urgent output the
    system can produce.
    """
    assert esc.escalation_stage('critical', 60.0, [], NOW) == esc.STAGE_MUST_ACT


def test_e6b_duty_outranks_permission(esc):
    """E6b: a steady target inside the 17(b) window is MUST_ACT, not MAY_ACT."""
    assert esc.escalation_stage('critical', 60.0,
                                _steady_track(), NOW) == esc.STAGE_MUST_ACT


def test_e6c_duty_does_not_fire_on_a_receding_target(esc):
    """E6c: negative TCPA means passed and opening -- no duty."""
    assert esc.escalation_stage('critical', -30.0,
                                _turning_track(), NOW) != esc.STAGE_MUST_ACT


def test_e6d_warning_tier_alone_does_not_create_the_duty(esc):
    """E6d: 17(b) requires being "so close"; Tier 2 is not that."""
    assert esc.escalation_stage('warning', 60.0,
                                _turning_track(), NOW) == esc.STAGE_HOLD


# --------------------------------------------------------------------------
# 17(c) and phrasing.
# --------------------------------------------------------------------------

def test_e7_may_act_phrase_carries_the_rule_17c_advice(esc):
    """E7: 17(c). In a Rule 15 stand-on the target is to port by definition,
    so "do not alter to port" is always the right accompanying advice."""
    phrase = esc.STANDON_PHRASES[esc.STAGE_MAY_ACT].lower()
    assert 'not altering' in phrase or 'is not' in phrase
    assert 'port' in phrase, 'missing the Rule 17(c) advice'


def test_e8_phrases_stay_advisory_but_convey_the_change_in_duty(esc):
    """E8: D02-6 -- no imperatives, while still distinguishing may from shall."""
    may = esc.STANDON_PHRASES[esc.STAGE_MAY_ACT].lower()
    must = esc.STANDON_PHRASES[esc.STAGE_MUST_ACT].lower()

    for phrase in (may, must):
        for sentence in phrase.split('.'):
            first = sentence.strip().split(' ')[0]
            assert first not in ('alter', 'hold', 'keep', 'turn', 'reduce', 'steer', 'stop'), (
                f'imperative opener in Rule 17 phrasing -- violates D02-6: {sentence!r}')

    assert 'may' in may, '17(a)(ii) is permission -- the phrase must say so'
    assert 'require' in must, '17(b) is a duty -- the phrase must convey that'


# --------------------------------------------------------------------------
# E9-E10 -- engine liveness (§8.0). Added v1.12 with the plugin decision.
#
# The plugin shim runs the Python engine as a child process. If it dies the
# plugin emits nothing -- and §13.1 tells the captain that silence means no
# qualifying target. Silence from a crash is then indistinguishable from
# silence from clear water, which is the worst failure this system can have.
# --------------------------------------------------------------------------

def test_e9_engine_exposes_a_liveness_signal(esc):
    """E9: the engine must be able to say it is alive, so absence is detectable."""
    assert hasattr(esc, 'HEARTBEAT_INTERVAL_S'), (
        'no heartbeat interval — the shim cannot distinguish a dead engine '
        'from a quiet one (§8.0)')
    assert esc.HEARTBEAT_INTERVAL_S <= 10.0, (
        'heartbeat too slow to catch a crash before the captain relies on silence')


def test_e10_engine_failure_phrase_states_the_advisory_is_not_running(esc):
    """E10: the failure announcement must say the advisory has STOPPED.

    "SafeHelm error" would leave a captain assuming it is still watching.
    """
    phrase = esc.STANDON_PHRASES.get('engine_failure', '').lower()
    assert phrase, 'no engine-failure phrase (§8.0)'
    assert 'not running' in phrase or 'stopped' in phrase, (
        'failure phrase does not tell the captain the advisory has stopped')
