"""P1-P5 -- CPA/TCPA geometry guard tests (V09995-SOL-001 §8.5, §10.3, §12).

The v1.0 geometry was correct and is retained: tcpa = -(r.v)/|v|^2,
cpa = |r + v*tcpa|. The defects were in the guards and the downstream use:

  * the no-relative-motion branch returned inf, which the clear condition
    `cpa > 500 and tcpa < 0` could never satisfy -> permanent alert   -> P2
  * cpa was computed with a NEGATIVE tcpa for receding targets, yielding a
    historical closest distance that could hold an alert open forever -> P3

Scenarios are hand-computed; expected values are in the docstrings so a
future reader can check them without re-deriving.
"""
import math

import pytest

from conftest import lazy_module

SPEC = '§8.5'

LAT = 45.0
M_PER_DEG_LAT = 111320.0
M_PER_DEG_LON = M_PER_DEG_LAT * math.cos(math.radians(LAT))   # 78716.7 at lat 45
KTS = 0.514444


@pytest.fixture
def eng():
    return lazy_module('cpa_engine', SPEC)


def _north(metres):
    return LAT + metres / M_PER_DEG_LAT


def _east(metres):
    return metres / M_PER_DEG_LON


# --------------------------------------------------------------------------

def test_p1_head_on_one_nautical_mile_at_ten_knots(eng):
    """P1: reciprocal courses, 1 NM apart, 10 kt each -> CPA 0 at TCPA 180 s.

    Closing speed = 2 * 10 kt = 20 kt = 10.2889 m/s.
    1852 m / 10.2889 m/s = 180.0 s. Collision course, so CPA = 0.
    """
    cpa, tcpa, rng = eng.compute_cpa_tcpa(
        own_lat=LAT,           own_lon=0.0, own_sog=10.0, own_cog=0.0,
        tgt_lat=_north(1852.0), tgt_lon=0.0, tgt_sog=10.0, tgt_cog=180.0)
    assert tcpa == pytest.approx(180.0, abs=0.5)
    assert cpa == pytest.approx(0.0, abs=1.0)
    assert rng == pytest.approx(1852.0, rel=1e-3)


def test_p2_parallel_same_speed_has_no_relative_motion(eng):
    """P2: identical course and speed, 500 m abeam -> TCPA inf, CPA = range.

    Returning inf (rather than 0 or a huge finite number) is what lets the
    §8.2 gate reject the target instead of treating a fixed 500 m separation
    as an imminent CPA. v1.0 returned inf too, but nothing downstream handled
    it -- see test_g5 and test_alert_manager M4.
    """
    cpa, tcpa, rng = eng.compute_cpa_tcpa(
        own_lat=LAT,          own_lon=0.0, own_sog=10.0, own_cog=90.0,
        tgt_lat=_north(500.0), tgt_lon=0.0, tgt_sog=10.0, tgt_cog=90.0)
    assert math.isinf(tcpa), 'no relative motion must yield infinite TCPA'
    assert rng == pytest.approx(500.0, rel=1e-3)
    assert cpa == pytest.approx(500.0, rel=1e-3)


def test_p3_receding_target_reports_present_range_as_cpa(eng):
    """P3: target astern and opening -> TCPA < 0, and CPA == current range.

    v1.0 evaluated |r + v*tcpa| with a negative tcpa, which returns the
    distance at the historical closest point. For a target that passed close
    and is now miles away that value stays small forever, so an alert keyed
    on CPA could never clear. Reporting present range instead makes the
    receding case unambiguous.
    """
    cpa, tcpa, rng = eng.compute_cpa_tcpa(
        own_lat=LAT,            own_lon=0.0, own_sog=10.0, own_cog=0.0,
        tgt_lat=_north(-500.0), tgt_lon=0.0, tgt_sog=10.0, tgt_cog=180.0)
    assert tcpa < 0.0, 'target astern and opening must give negative TCPA'
    assert rng == pytest.approx(500.0, rel=1e-3)
    assert cpa == pytest.approx(rng, rel=1e-6), 'receding CPA must be present range'


def test_p4_perpendicular_crossing_matches_hand_calculation(eng):
    """P4: we head north, target 1000 m east heads west, both 10 kt.

    Relative velocity is (-10 kt west, -10 kt south) = 5.1444 m/s on each axis.
    TCPA = 1000 / (2 * 5.1444) ... solving -(r.v)/|v|^2 gives 97.2 s.
    At TCPA we have moved 500 m north and the target 500 m west, leaving a
    500 m x 500 m offset: CPA = 1000/sqrt(2) = 707.1 m.
    """
    cpa, tcpa, rng = eng.compute_cpa_tcpa(
        own_lat=LAT, own_lon=0.0,           own_sog=10.0, own_cog=0.0,
        tgt_lat=LAT, tgt_lon=_east(1000.0), tgt_sog=10.0, tgt_cog=270.0)
    assert tcpa == pytest.approx(97.2, abs=1.0)
    assert cpa == pytest.approx(1000.0 / math.sqrt(2.0), rel=0.01)
    assert rng == pytest.approx(1000.0, rel=1e-3)


def test_p5_longitude_is_scaled_by_latitude(eng):
    """P5: one degree of longitude at lat 45 is 111320*cos(45) = 78716.7 m.

    Omitting the cos(lat) factor overstates east-west separation by 41% at
    this latitude, which would push real targets outside the range gate.
    Both vessels stationary, so the function returns range directly.
    """
    _, _, rng = eng.compute_cpa_tcpa(
        own_lat=LAT, own_lon=0.0, own_sog=0.0, own_cog=0.0,
        tgt_lat=LAT, tgt_lon=1.0, tgt_sog=0.0, tgt_cog=0.0)
    assert rng == pytest.approx(M_PER_DEG_LON, rel=0.001)


def test_p5b_latitude_is_not_scaled(eng):
    """One degree of latitude is 111320 m at any latitude."""
    _, _, rng = eng.compute_cpa_tcpa(
        own_lat=LAT,       own_lon=0.0, own_sog=0.0, own_cog=0.0,
        tgt_lat=LAT + 1.0, tgt_lon=0.0, tgt_sog=0.0, tgt_cog=0.0)
    assert rng == pytest.approx(M_PER_DEG_LAT, rel=0.001)


# --------------------------------------------------------------------------
# Course convention. Getting sin/cos the wrong way round mirrors every bearing.
# --------------------------------------------------------------------------

def test_p_course_000_is_north_not_east(eng):
    """COG 000 must move a vessel north. Swapping sin/cos sends it east.

    We sit still; the target is 1000 m south on COG 000 (northbound), so it
    closes on us and CPA is ~0 at range/speed seconds.
    """
    cpa, tcpa, _ = eng.compute_cpa_tcpa(
        own_lat=LAT,             own_lon=0.0, own_sog=0.0,  own_cog=0.0,
        tgt_lat=_north(-1000.0), tgt_lon=0.0, tgt_sog=10.0, tgt_cog=0.0)
    assert tcpa > 0.0, 'northbound target south of us must be closing'
    assert cpa == pytest.approx(0.0, abs=1.0)
    assert tcpa == pytest.approx(1000.0 / (10.0 * KTS), abs=2.0)


def test_p_course_090_is_east(eng):
    """COG 090 must move a vessel east."""
    cpa, tcpa, _ = eng.compute_cpa_tcpa(
        own_lat=LAT, own_lon=0.0,             own_sog=0.0,  own_cog=0.0,
        tgt_lat=LAT, tgt_lon=_east(-1000.0), tgt_sog=10.0, tgt_cog=90.0)
    assert tcpa > 0.0, 'eastbound target west of us must be closing'
    assert cpa == pytest.approx(0.0, abs=1.0)
