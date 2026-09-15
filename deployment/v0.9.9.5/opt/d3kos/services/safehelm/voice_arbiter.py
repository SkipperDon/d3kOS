# voice_arbiter.py
import time

class VoiceArbiter:
    GLOBAL_MIN_GAP_S = 15.0
    TIER_RANK = {'critical': 0, 'warning': 1, 'advisory': 2}

    def __init__(self):
        self._last_spoken = 0.0

    def _order(self, c):
        return (self.TIER_RANK.get(c['tier'], 9), c['tcpa_s'])

    def select(self, candidates):
        if not candidates:
            return None
        preempting = [c for c in candidates if c.get('preempt')]
        if preempting:
            return min(preempting, key=self._order)
        if time.time() - self._last_spoken < self.GLOBAL_MIN_GAP_S:
            return None
        return min(candidates, key=self._order)

    def mark_spoken(self):
        self._last_spoken = time.time()
