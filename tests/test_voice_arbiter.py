"""A1-A6 -- global voice arbiter guard tests (V09995-SOL-001 §8.3, §12).

Policy D02-4: one spoken sentence every 15 s system-wide, priority by lowest
TCPA. Policy D02-5: a Critical on another target wins queue insertion
immediately rather than waiting behind the global gap.

Without a global cap, thirty gated targets would each speak on their own
60 s per-target timer and overlap constantly.

The arbiter is built by a FACTORY fixture, not returned directly: the module
import must happen inside the test body so a missing module is reported as a
FAILURE rather than a fixture setup ERROR (§12.1).
"""
import pytest

from conftest import require_module

SPEC = '§8.3'


@pytest.fixture
def make_arb(clock, monkeypatch):
    def _make():
        va = require_module('voice_arbiter', SPEC)      # resolved in the test body
        monkeypatch.setattr(va.time, 'time', clock)
        return va.VoiceArbiter()
    return _make


def _c(target_id, tier, tcpa_s, preempt=False):
    return {'target_id': target_id, 'tier': tier, 'tcpa_s': tcpa_s,
            'phrase': f'phrase for {target_id}', 'preempt': preempt}


# --------------------------------------------------------------------------

def test_a1_nothing_to_say_returns_none(make_arb):
    assert make_arb().select([]) is None


def test_a2_lowest_tcpa_wins_within_a_tier(make_arb):
    """A2: D02-4 -- among equals, the most imminent target speaks first."""
    chosen = make_arb().select([
        _c('111111111', 'warning', 400.0),
        _c('222222222', 'warning', 120.0),
        _c('333333333', 'warning', 300.0),
    ])
    assert chosen['target_id'] == '222222222'


def test_a3_critical_outranks_a_nearer_warning(make_arb):
    """A3: tier dominates TCPA ordering.

    A Warning 30 s out must not delay a Critical 200 s out -- severity is the
    primary key, TCPA only breaks ties.
    """
    chosen = make_arb().select([
        _c('111111111', 'warning', 30.0),
        _c('222222222', 'critical', 200.0),
    ])
    assert chosen['target_id'] == '222222222'


def test_a4_global_gap_is_fifteen_seconds(make_arb, clock):
    """A4: D02-4 -- 15 s between any two spoken sentences, system-wide."""
    arb = make_arb()
    assert arb.GLOBAL_MIN_GAP_S == pytest.approx(15.0)

    assert arb.select([_c('111111111', 'warning', 300.0)]) is not None
    arb.mark_spoken()

    clock.advance(5)
    assert arb.select([_c('222222222', 'warning', 250.0)]) is None, 'spoke inside the gap'
    clock.advance(11)
    assert arb.select([_c('222222222', 'warning', 250.0)]) is not None


def test_a5_preempting_critical_bypasses_the_global_gap(make_arb, clock):
    """A5: D02-5 -- a fresh Critical wins queue insertion immediately.

    Without the bypass a Critical could sit at the head of the queue for up to
    15 s, which is not "immediately".
    """
    arb = make_arb()
    arb.mark_spoken()
    clock.advance(2)

    assert arb.select([_c('111111111', 'warning', 100.0)]) is None
    chosen = arb.select([
        _c('111111111', 'warning', 100.0),
        _c('222222222', 'critical', 200.0, preempt=True),
    ])
    assert chosen is not None, 'preempting Critical was blocked by the global gap'
    assert chosen['target_id'] == '222222222'


def test_a5b_preemption_does_not_disable_the_gap_afterwards(make_arb, clock):
    """A5b: the bypass is per-candidate, not a latch."""
    arb = make_arb()
    arb.mark_spoken()
    clock.advance(2)
    arb.select([_c('222222222', 'critical', 200.0, preempt=True)])
    arb.mark_spoken()
    clock.advance(3)
    assert arb.select([_c('111111111', 'warning', 100.0)]) is None, 'gap stayed open'


def test_a5c_most_severe_preempting_candidate_wins(make_arb):
    """A5c: with several preempting candidates, ordering still applies."""
    arb = make_arb()
    arb.mark_spoken()
    chosen = arb.select([
        _c('111111111', 'critical', 220.0, preempt=True),
        _c('222222222', 'critical', 90.0, preempt=True),
    ])
    assert chosen['target_id'] == '222222222'


def test_a6_unknown_tier_sorts_last_and_does_not_crash(make_arb):
    """A6: an unexpected tier string must degrade, not raise.

    Fail-soft on the audio path: a bad tier label should never take down the
    advisory loop.
    """
    chosen = make_arb().select([
        _c('111111111', 'something-new', 10.0),
        _c('222222222', 'warning', 400.0),
    ])
    assert chosen['target_id'] == '222222222'
