"""M1-M8 -- alert state machine guard tests (V09995-SOL-001 §8.3, §8.5, §12).

Guards the three changes v1.1 made to the operator-supplied state machine,
plus the D02-5 ACK-scope ruling:

  M2  20% re-trigger measured against CPA AT ACKNOWLEDGEMENT, not the previous
      tick. The original compared against last tick's value, so at 1 Hz it
      needed a 20% drop inside one second and effectively never fired.
  M4  clearing is driven by the gate returning None with hysteresis. The
      original used `cpa > 500 and tcpa < 0`, which a no-relative-motion
      target (tcpa = inf) could never satisfy.
  M5  per-target gap is 60 s (policy D02-4 moved the 15 s cap to global).
  M7  ACK clears ONLY that target's audio segment (D02-5).

`make_mgr` is a FACTORY fixture: the module import must happen inside the test
body so a missing module is a FAILURE, not a fixture setup ERROR (§12.1).
"""
import pytest

from conftest import require_module

SPEC = '§8.5'

CRITICAL = {'tier': 'critical', 'voice': 'repeat'}
WARNING = {'tier': 'warning', 'voice': 'once'}
ADVISORY = {'tier': 'advisory', 'voice': None}


@pytest.fixture
def make_mgr(clock, monkeypatch):
    """Returns (module, manager). Resolved on call, i.e. inside the test body."""
    def _make(**kw):
        am = require_module('alert_manager', SPEC)
        monkeypatch.setattr(am.time, 'time', clock)
        args = dict(target_id='123456789', cpa=300.0, tcpa=400.0, bearing=45.0,
                    rule_id='rule15_giveway', tier='warning')
        args.update(kw)
        return am, am.SafeHelmAlertManager(**args)
    return _make


# --------------------------------------------------------------------------

def test_m1_new_alert_is_active_and_wants_audio(make_mgr):
    """M1: a fresh Warning alert speaks immediately."""
    am, mgr = make_mgr()
    assert mgr.state is am.AlertState.ACTIVE_UNACKED
    assert mgr.wants_audio() is True


def test_m1b_advisory_tier_never_wants_audio(make_mgr):
    """M1b: Tier 1 is visual-only (D02-3), even while ACTIVE_UNACKED."""
    am, mgr = make_mgr()
    mgr.update_metrics(cpa=450.0, tcpa=540.0, tier=ADVISORY)
    assert mgr.state is am.AlertState.ACTIVE_UNACKED
    assert mgr.wants_audio() is False, 'Tier 1 Advisory must stay silent'


def test_m2_retrigger_uses_cpa_at_ack_not_previous_tick(make_mgr, clock):
    """M2: a slow drift totalling >20% since ACK must re-trigger.

    This is the regression guard. CPA is stepped down 2 m per tick from 300 m.
    No single tick is a 20% drop, so the original implementation -- which
    compared against the previous tick -- would never have re-triggered and
    the operator's stated 20% requirement would have been silently dead.

    300 m at ACK; threshold is 300 * 0.80 = 240 m.
    """
    am, mgr = make_mgr()
    mgr.execute_ui_acknowledgement()
    assert mgr.state is am.AlertState.ACKNOWLEDGED_MUTED
    assert mgr.cpa_at_ack == pytest.approx(300.0)

    cpa = 300.0
    while cpa > 242.0:
        cpa -= 2.0
        clock.advance(1)                       # stay well inside the 120 s snooze
        mgr.update_metrics(cpa=cpa, tcpa=380.0, tier=WARNING)
        assert mgr.state is am.AlertState.ACKNOWLEDGED_MUTED, (
            f'woke too early at cpa={cpa} (threshold is 240)')

    clock.advance(1)
    mgr.update_metrics(cpa=239.0, tcpa=380.0, tier=WARNING)
    assert mgr.state is am.AlertState.ACTIVE_UNACKED, (
        'CPA degraded 20% since ACK but the alert did not re-trigger')


def test_m2b_stable_cpa_stays_muted_within_the_snooze(make_mgr, clock):
    """M2b: acknowledging a stable target keeps it quiet for the full 120 s."""
    am, mgr = make_mgr()
    mgr.execute_ui_acknowledgement()
    for _ in range(110):
        clock.advance(1)
        mgr.update_metrics(cpa=299.0, tcpa=380.0, tier=WARNING)
    assert mgr.state is am.AlertState.ACKNOWLEDGED_MUTED


def test_m3_snooze_expires_after_120_seconds(make_mgr, clock):
    """M3: the 120 s snooze re-arms the alert even with no CPA change."""
    am, mgr = make_mgr()
    mgr.execute_ui_acknowledgement()
    clock.advance(121)
    mgr.update_metrics(cpa=300.0, tcpa=380.0, tier=WARNING)
    assert mgr.state is am.AlertState.ACTIVE_UNACKED
    assert mgr.SNOOZE_TIMEOUT_S == pytest.approx(120.0)


def test_m4_clears_after_hysteresis_when_no_longer_gated(make_mgr):
    """M4: N consecutive ungated ticks clear the alert; fewer do not."""
    am, mgr = make_mgr()
    for i in range(mgr.CLEAR_HYSTERESIS - 1):
        mgr.update_metrics(cpa=900.0, tcpa=-10.0, tier=None)
        assert mgr.state is not am.AlertState.CLEARED, f'cleared too early on tick {i+1}'
    mgr.update_metrics(cpa=900.0, tcpa=-10.0, tier=None)
    assert mgr.state is am.AlertState.CLEARED


def test_m4b_a_single_dropout_does_not_clear(make_mgr):
    """M4b: one missed AIS report must not dismiss a live alert."""
    am, mgr = make_mgr()
    mgr.update_metrics(cpa=900.0, tcpa=-10.0, tier=None)
    mgr.update_metrics(cpa=290.0, tcpa=380.0, tier=WARNING)
    for _ in range(mgr.CLEAR_HYSTERESIS - 1):
        mgr.update_metrics(cpa=900.0, tcpa=-10.0, tier=None)
    assert mgr.state is not am.AlertState.CLEARED, 'hysteresis counter was not reset'


def test_m4c_no_relative_motion_target_can_clear(make_mgr):
    """M4c: the gate rejects infinite TCPA, so the alert clears.

    v1.0's condition `cpa > 500 and tcpa < 0` was unsatisfiable for inf, so
    a target matching our course and speed held an alert open permanently.
    """
    am, mgr = make_mgr()
    for _ in range(mgr.CLEAR_HYSTERESIS):
        mgr.update_metrics(cpa=500.0, tcpa=float('inf'), tier=None)
    assert mgr.state is am.AlertState.CLEARED


def test_m5_per_target_gap_is_sixty_seconds(make_mgr, clock):
    """M5: policy D02-4 -- per-target 60 s; the 15 s cap is global, not per-target."""
    am, mgr = make_mgr()
    assert mgr.PER_TARGET_MIN_GAP_S == pytest.approx(60.0)

    mgr.mark_spoken()
    assert mgr.wants_audio() is False
    clock.advance(45)
    assert mgr.wants_audio() is False, 'spoke again before the 60 s per-target gap'
    clock.advance(20)
    assert mgr.wants_audio() is True


def test_m6_escalation_to_critical_preempts(make_mgr, clock):
    """M6: escalating into Critical sets preempt and bypasses the per-target gap.

    D02-5: a Critical must win queue insertion immediately.
    """
    am, mgr = make_mgr()
    mgr.mark_spoken()
    clock.advance(5)
    assert mgr.wants_audio() is False

    mgr.update_metrics(cpa=140.0, tcpa=200.0, tier=CRITICAL)
    assert mgr.preempts() is True
    assert mgr.wants_audio() is True, 'Critical did not bypass the per-target gap'


def test_m6b_preempt_is_one_shot(make_mgr):
    """M6b: a Critical cannot monopolise the audio channel."""
    am, mgr = make_mgr()
    mgr.update_metrics(cpa=140.0, tcpa=200.0, tier=CRITICAL)
    assert mgr.preempts() is True
    mgr.mark_spoken()
    assert mgr.preempts() is False, 'preempt must clear once spoken'
    assert mgr.wants_audio() is False, 'back under the per-target gap after speaking'


def test_m6c_escalation_wakes_an_acknowledged_alert(make_mgr, clock):
    """M6c: ACK does not suppress a subsequent escalation to Critical."""
    am, mgr = make_mgr()
    mgr.execute_ui_acknowledgement()
    clock.advance(5)
    mgr.update_metrics(cpa=140.0, tcpa=200.0, tier=CRITICAL)
    assert mgr.state is am.AlertState.ACTIVE_UNACKED
    assert mgr.wants_audio() is True


def test_m6d_staying_critical_does_not_re_preempt(make_mgr, clock):
    """M6d: preemption fires on the transition, not on every Critical tick."""
    am, mgr = make_mgr()
    mgr.update_metrics(cpa=140.0, tcpa=200.0, tier=CRITICAL)
    mgr.mark_spoken()
    clock.advance(1)
    mgr.update_metrics(cpa=138.0, tcpa=190.0, tier=CRITICAL)
    assert mgr.preempts() is False, 'already Critical -- not a fresh escalation'


def test_m7_ack_affects_only_its_own_target(make_mgr):
    """M7: D02-5 -- ACK clears only that target's audio segment.

    Acknowledging target A must never silence, drop or delay target B.
    """
    am, a = make_mgr(target_id='111111111')
    b = am.SafeHelmAlertManager('222222222', 280.0, 380.0, 315.0,
                                'rule15_standon', 'warning')

    a.execute_ui_acknowledgement()

    assert a.state is am.AlertState.ACKNOWLEDGED_MUTED
    assert b.state is am.AlertState.ACTIVE_UNACKED, 'ACK on A muted B'
    assert b.wants_audio() is True, 'ACK on A suppressed audio for B'


def test_m7b_critical_on_b_survives_ack_on_a(make_mgr):
    """M7b: D02-5 -- a Critical on B while A is acknowledged still preempts."""
    am, a = make_mgr(target_id='111111111')
    b = am.SafeHelmAlertManager('222222222', 280.0, 380.0, 315.0,
                                'rule15_standon', 'warning')

    a.execute_ui_acknowledgement()
    b.update_metrics(cpa=140.0, tcpa=200.0, tier=CRITICAL)

    assert b.preempts() is True
    assert b.wants_audio() is True
    assert a.state is am.AlertState.ACKNOWLEDGED_MUTED, 'B escalating disturbed A'


def test_m8_degrade_fraction_matches_policy(make_mgr):
    """M8: the 20% figure is an operator requirement; drift is a policy change."""
    _, mgr = make_mgr()
    assert mgr.DEGRADE_FRACTION == pytest.approx(0.80)
