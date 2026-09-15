# alert_manager.py
import time
from enum import Enum

class AlertState(Enum):
    ACTIVE_UNACKED     = 1
    ACKNOWLEDGED_MUTED = 2
    CLEARED            = 3


class SafeHelmAlertManager:
    """Per-target alert lifecycle. One instance per MMSI.

    Based on the operator-supplied state machine (S159). Three changes, all
    required by policy D02-4 or by a defect in the original:
      1. per-target gap 15s -> 60s   (D02-4; the 15s cap is now global)
      2. 20% degradation measured against CPA *at acknowledgement*, not the
         previous tick -- at 1 Hz the original needed a 20% drop inside one
         second, so the re-trigger effectively never fired
      3. clearing driven by the gate returning None, with hysteresis, instead of
         'cpa > 500 and tcpa < 0' which could never be satisfied (see above)
    """

    REPEAT_GAP_S     = 60.0     # Tier 3 cadence (D02-4 per-target cap)
    ONCE_GAP_S       = 120.0    # Tier 2 episode length
    SNOOZE_TIMEOUT_S = 120.0
    DEGRADE_FRACTION = 0.80
    CLEAR_HYSTERESIS = 3

    def __init__(self, target_id, cpa, tcpa, bearing, rule_id, tier, voice_mode):
        self.target_id = target_id
        self.cpa, self.tcpa, self.bearing = cpa, tcpa, bearing
        self.rule_id, self.tier = rule_id, tier
        self.voice_mode = voice_mode            # None | 'once' | 'repeat'
        self.state = AlertState.ACTIVE_UNACKED
        self.ack_time = None
        self.cpa_at_ack = None
        self.last_audio_played = 0.0
        self._ungated_ticks = 0
        self._preempt = False
        self._spoken_this_episode = False

    def _arm(self):
        """Start a new alert episode: eligible to speak again immediately."""
        self.state = AlertState.ACTIVE_UNACKED
        self._spoken_this_episode = False

    def update_metrics(self, cpa, tcpa, tier):
        """tier is alert_gate.classify_tier(...) or None."""
        self.cpa, self.tcpa = cpa, tcpa

        if tier is None:
            self._ungated_ticks += 1
            if self._ungated_ticks >= self.CLEAR_HYSTERESIS:
                self.state = AlertState.CLEARED
            return
        self._ungated_ticks = 0

        escalated = tier['tier'] == 'critical' and self.tier != 'critical'
        self.tier = tier['tier']
        self.voice_mode = tier['voice']

        if escalated:
            # D02-5: a fresh Critical wins queue insertion immediately, even if
            # another target is mid-acknowledgement. One-shot; cleared on speaking.
            self._preempt = True
            self.last_audio_played = 0.0
            self._arm()
            return

        if self.state is AlertState.ACKNOWLEDGED_MUTED:
            snoozed_out = time.time() - self.ack_time > self.SNOOZE_TIMEOUT_S
            degraded = (self.cpa_at_ack is not None
                        and self.cpa < self.cpa_at_ack * self.DEGRADE_FRACTION)
            if snoozed_out or degraded:
                self._arm()

    def execute_ui_acknowledgement(self):
        """D02-5: clears ONLY this target's audio segment. Never touches another target."""
        self.state = AlertState.ACKNOWLEDGED_MUTED
        self.ack_time = time.time()
        self.cpa_at_ack = self.cpa
        self._preempt = False

    def wants_audio(self) -> bool:
        """True if eligible to speak. The global arbiter decides who actually does.

        Cadence is driven by the tier's voice mode (§8.2). v1.2 ignored it and
        applied one 60 s gap to every tier, so Critical was no more insistent
        than Warning.
        """
        if self.state is not AlertState.ACTIVE_UNACKED:
            return False
        if self.voice_mode is None:
            return False                        # Tier 1 Advisory is visual only
        if self._preempt:
            return True                         # D02-5 preemption ignores the cap
        if not self._spoken_this_episode:
            return True                         # first utterance of this episode
        gap = self.REPEAT_GAP_S if self.voice_mode == 'repeat' else self.ONCE_GAP_S
        return time.time() - self.last_audio_played > gap

    def preempts(self) -> bool:
        return self._preempt

    def mark_spoken(self):
        """Call ONLY on the arbiter's winning candidate — never on the losers.

        Marking a loser resets its cadence timer without it having spoken, which
        silences it for a full gap period. See §8.8 and test_advisory_loop.py::I1.
        """
        self.last_audio_played = time.time()
        self._preempt = False                   # one-shot
        self._spoken_this_episode = True
