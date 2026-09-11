"""G1-G8 -- alert gating guard tests (V09995-SOL-001 §8.2, §10.2, §12).

Solution design v1.0 had NO gating at all: the classifier received no CPA,
TCPA or range, so every AIS target in receive range produced a voice alert
every 15 seconds. Thirty targets in a busy channel would have been a
continuous stream of spoken alarms, and alert fatigue is how an advisory
system gets switched off -- the worst outcome for a system whose purpose is
assisting the captain (§1).

Policy D02-3 (operator, S160):
    Tier 1 Advisory  cpa <= 500m, tcpa 0-10min, range <= 2.0 NM  visual only
    Tier 2 Warning   cpa <= 300m, tcpa 0-7min,  range <= 1.5 NM  voice once
    Tier 3 Critical  cpa <= 150m, tcpa 0-4min,  range <= 0.75NM  voice repeated
    Head-on: Tier 2/3 TCPA limits extended by +2 min.
"""
import math

import pytest

from conftest import lazy_module

SPEC = '§8.2'
NM = 1852.0


@pytest.fixture
def gate():
    return lazy_module('alert_gate', SPEC)


def _tier(result):
    return result['tier'] if result else None


# --------------------------------------------------------------------------
# Tier selection.
# --------------------------------------------------------------------------

def test_g1_critical_tier(gate):
    """G1: inside all three Critical thresholds."""
    r = gate.classify_tier(cpa_m=100.0, tcpa_s=120.0, range_m=900.0)
    assert _tier(r) == 'critical'
    assert r['voice'] == 'repeat'


def test_g2_warning_tier(gate):
    """G2: outside Critical CPA, inside all three Warning thresholds."""
    r = gate.classify_tier(cpa_m=250.0, tcpa_s=300.0, range_m=2000.0)
    assert _tier(r) == 'warning'
    assert r['voice'] == 'once'


def test_g3_advisory_tier_is_silent(gate):
    """G3: Tier 1 is a widget entry only. It must never voice (D02-3)."""
    r = gate.classify_tier(cpa_m=450.0, tcpa_s=540.0, range_m=3500.0)
    assert _tier(r) == 'advisory'
    assert r['voice'] is None, 'Tier 1 Advisory must be visual-only'


def test_g_highest_qualifying_tier_wins(gate):
    """A target satisfying all three tiers is Critical, not Advisory."""
    r = gate.classify_tier(cpa_m=50.0, tcpa_s=60.0, range_m=500.0)
    assert _tier(r) == 'critical'


# --------------------------------------------------------------------------
# TCPA lower bound. This corrects the policy as supplied.
# --------------------------------------------------------------------------

def test_g4_receding_target_does_not_alert(gate):
    """G4: negative TCPA means already passed and opening -> no alert.

    The gating policy as supplied read "TCPA <= X" with no lower bound, so a
    target with TCPA = -3 min satisfied "<= 7 min" and would have alerted.
    A lower bound of 0 is required.
    """
    assert gate.classify_tier(cpa_m=100.0, tcpa_s=-180.0, range_m=900.0) is None


def test_g5_no_relative_motion_does_not_alert(gate):
    """G5: infinite TCPA (parallel / matched velocity) -> no alert.

    v1.0's clear condition was `cpa > 500 and tcpa < 0`. `inf < 0` is False,
    so a target with no relative motion could never clear: a permanent alert
    that nothing would dismiss.
    """
    assert gate.classify_tier(cpa_m=100.0, tcpa_s=float('inf'), range_m=900.0) is None


def test_g5b_undefined_tcpa_does_not_alert(gate):
    """G5b: None and NaN must be rejected, not compared."""
    assert gate.classify_tier(cpa_m=100.0, tcpa_s=None, range_m=900.0) is None
    assert gate.classify_tier(cpa_m=100.0, tcpa_s=float('nan'), range_m=900.0) is None


# --------------------------------------------------------------------------
# Head-on TCPA bonus.
# --------------------------------------------------------------------------

def test_g6_head_on_extends_the_tcpa_window(gate):
    """G6: tcpa 480s exceeds Warning's 420s, but head-on adds +120s -> Warning.

    Closing speed in a head-on is roughly doubled, so the same TCPA leaves
    materially less distance. The window is widened to compensate.
    """
    r = gate.classify_tier(cpa_m=250.0, tcpa_s=480.0, range_m=2000.0, is_headon=True)
    assert _tier(r) == 'warning'
    assert r['voice'] == 'once'


def test_g7_bonus_is_not_applied_when_not_head_on(gate):
    """G7: same geometry without the head-on flag must not reach a voice tier.

    It falls back to Advisory (cpa 250<=500, tcpa 480<=600, range 2000<=3704),
    which is silent. The safety-relevant assertion is that it is NOT Warning.

    NOTE: the §10.2 table originally listed None here. Working the numbers
    while writing this test showed Advisory is correct; the table was
    corrected in v1.2. The guard is 'stays silent', not 'returns None'.
    """
    r = gate.classify_tier(cpa_m=250.0, tcpa_s=480.0, range_m=2000.0, is_headon=False)
    assert _tier(r) == 'advisory'
    assert r['voice'] is None, 'head-on bonus leaked into a non-head-on target'


# --------------------------------------------------------------------------
# Each dimension gates independently.
# --------------------------------------------------------------------------

def test_g8_range_gates_independently(gate):
    """G8: dangerous CPA and TCPA but the target is 4 km away -> no alert."""
    assert gate.classify_tier(cpa_m=100.0, tcpa_s=120.0, range_m=4000.0) is None


def test_g8b_cpa_gates_independently(gate):
    """Close in time and range, but passing 600 m clear -> no alert."""
    assert gate.classify_tier(cpa_m=600.0, tcpa_s=120.0, range_m=900.0) is None


def test_g8c_tcpa_gates_independently(gate):
    """Close CPA and range, but CPA is 20 minutes out -> no alert."""
    assert gate.classify_tier(cpa_m=100.0, tcpa_s=1200.0, range_m=900.0) is None


# --------------------------------------------------------------------------
# Threshold constants must match D02-3 exactly.
# --------------------------------------------------------------------------

def test_g_thresholds_match_the_approved_policy(gate):
    """The numbers are an operator ruling. Drift here is a policy change."""
    assert math.isclose(gate.HEADON_TCPA_BONUS_S, 120.0), 'head-on bonus must be +2 min'
    expected = {
        'critical': (150.0, 240.0, 0.75 * NM, 'repeat'),
        'warning':  (300.0, 420.0, 1.50 * NM, 'once'),
        'advisory': (500.0, 600.0, 2.00 * NM, None),
    }
    actual = {t[0]: (t[1], t[2], t[3], t[4]) for t in gate.TIERS}
    assert actual == expected, 'TIERS drifted from approved policy D02-3'


def test_g_tiers_are_ordered_most_severe_first(gate):
    """classify_tier returns the first match, so ordering is load-bearing."""
    assert [t[0] for t in gate.TIERS] == ['critical', 'warning', 'advisory']
