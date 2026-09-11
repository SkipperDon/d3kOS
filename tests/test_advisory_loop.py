"""I1-I6 -- advisory loop integration guards (V09995-SOL-001 §8.8, §12).

Added v1.3 after external review. v1.2 specified `SafeHelmAlertManager` and
`VoiceArbiter` but not the wiring between them. Both track their own
"have I just spoken" state, both need mark_spoken() called correctly, and
NEITHER UNIT SUITE CAN CATCH A BUG IN THAT GLUE.

The invariant that matters most (I1): mark_spoken() is called on the arbiter
and on the WINNING manager only. Marking the losers resets their cadence
timers without them having spoken, silencing each for a full gap period --
a bug that presents as "the system went quiet", not as an error.

These are still red-phase guards: safehelm.advisory_tick does not exist yet.
"""
import pytest

from conftest import require_module

SPEC = '§8.8'


class FakeTarget:
    """A Signal K AIS target reduced to what advisory_tick consumes."""

    def __init__(self, mmsi, lat, lon, sog, cog, relative_bearing):
        self.mmsi = mmsi
        self.lat, self.lon = lat, lon
        self.sog, self.cog = sog, cog
        self.relative_bearing = relative_bearing


class FakeOwn:
    def __init__(self, lat=45.0, lon=0.0, sog=10.0, cog=0.0):
        self.lat, self.lon, self.sog, self.cog = lat, lon, sog, cog


M_PER_DEG_LAT = 111320.0


def _north(metres, base=45.0):
    return base + metres / M_PER_DEG_LAT


def _closing_target(mmsi, metres_ahead, relative_bearing=0.0, sog=10.0):
    """A target dead ahead on a reciprocal course, i.e. closing on us."""
    return FakeTarget(mmsi, _north(metres_ahead), 0.0, sog, 180.0, relative_bearing)


@pytest.fixture
def loop(clock, monkeypatch):
    """Returns (module, arbiter, managers). Resolved inside the test body."""
    def _make():
        sh = require_module('safehelm', SPEC)
        va = require_module('voice_arbiter', '§8.3')
        am = require_module('alert_manager', '§8.5')
        monkeypatch.setattr(va.time, 'time', clock)
        monkeypatch.setattr(am.time, 'time', clock)
        spoken = []
        monkeypatch.setattr(sh.voice_client, 'speak',
                            lambda msg, repeat=1: spoken.append(msg) or True)
        return sh, va.VoiceArbiter(), {}, spoken
    return _make


# --------------------------------------------------------------------------

def test_i1_only_the_winner_is_marked_spoken(loop, clock):
    """I1: THE GLUE GUARD. Losing candidates must keep their cadence intact.

    Two Critical targets both want audio. The arbiter picks one. If the loop
    marks both, the loser's 60 s timer restarts without it having spoken and
    it is silenced for a full minute for no reason.
    """
    sh, arb, managers, spoken = loop()
    own = FakeOwn()
    targets = [_closing_target('111111111', 700.0),
               _closing_target('222222222', 500.0)]

    winner = sh.advisory_tick(own, targets, managers, arb, '2026-09-11T00:00:00Z')
    assert winner is not None
    assert len(spoken) == 1, 'exactly one sentence per tick'

    loser_id = '111111111' if winner['target_id'] == '222222222' else '222222222'
    assert managers[winner['target_id']].last_audio_played > 0.0
    assert managers[loser_id].last_audio_played == 0.0, (
        'loser was marked spoken -- its cadence timer restarted without it '
        'having said anything')
    assert managers[loser_id].wants_audio() is True, 'loser was silenced'


def test_i2_nearest_tcpa_wins_across_the_whole_pipeline(loop):
    """I2: priority ordering survives the loop, not just the arbiter in isolation."""
    sh, arb, managers, spoken = loop()
    own = FakeOwn()
    targets = [_closing_target('111111111', 900.0),
               _closing_target('222222222', 400.0)]

    winner = sh.advisory_tick(own, targets, managers, arb, '2026-09-11T00:00:00Z')
    assert winner['target_id'] == '222222222', 'more imminent target did not win'


def test_i3_global_gap_holds_across_ticks(loop, clock):
    """I3: two ticks inside 15 s produce one utterance, not two."""
    sh, arb, managers, spoken = loop()
    own = FakeOwn()
    targets = [_closing_target('111111111', 700.0),
               _closing_target('222222222', 500.0)]

    sh.advisory_tick(own, targets, managers, arb, '2026-09-11T00:00:00Z')
    clock.advance(3)
    sh.advisory_tick(own, targets, managers, arb, '2026-09-11T00:00:03Z')
    assert len(spoken) == 1, 'global 15 s cap was bypassed by the loop'

    clock.advance(13)
    sh.advisory_tick(own, targets, managers, arb, '2026-09-11T00:00:16Z')
    assert len(spoken) == 2, 'nothing spoke after the global gap expired'


def test_i4_cleared_target_is_removed_from_the_manager_map(loop, clock):
    """I4: the manager dict must not grow without bound.

    A target that leaves the gate for CLEAR_HYSTERESIS consecutive ticks is
    dropped. Leaking entries would hold stale alerts and grow memory on a
    long passage through busy water.
    """
    sh, arb, managers, spoken = loop()
    own = FakeOwn()
    close = [_closing_target('111111111', 500.0)]
    sh.advisory_tick(own, close, managers, arb, '2026-09-11T00:00:00Z')
    assert '111111111' in managers

    # Same MMSI, now far away and opening: outside every gate.
    far = [FakeTarget('111111111', _north(-40000.0), 0.0, 10.0, 180.0, 180.0)]
    for i in range(5):
        clock.advance(1)
        sh.advisory_tick(own, far, managers, arb, f'2026-09-11T00:00:0{i}Z')
    assert '111111111' not in managers, 'cleared alert leaked in the manager map'


def test_i5_advisory_tier_target_never_speaks(loop):
    """I5: a Tier 1 target may create a manager entry but must stay silent."""
    sh, arb, managers, spoken = loop()
    own = FakeOwn()
    # ~3.4 km ahead, closing: inside Tier 1 range, outside Tier 2 range.
    targets = [_closing_target('111111111', 3400.0)]

    winner = sh.advisory_tick(own, targets, managers, arb, '2026-09-11T00:00:00Z')
    assert winner is None, 'Tier 1 Advisory spoke'
    assert spoken == []


def test_i6_no_targets_is_silent_and_harmless(loop):
    """I6: an empty AIS picture must not raise and must not speak."""
    sh, arb, managers, spoken = loop()
    assert sh.advisory_tick(FakeOwn(), [], managers, arb,
                            '2026-09-11T00:00:00Z') is None
    assert spoken == []
    assert managers == {}
