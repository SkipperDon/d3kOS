#!/usr/bin/env python3
"""
d3kOS Autonomous Agent Framework — Base Class (AA1)
v0.9.8

Defines AgentBase, AgentResult, and shared file paths.
All agents (AA2-AA6) inherit from AgentBase.

State DB : /opt/d3kos/data/agents/agent_state.db
Status JSON: /opt/d3kos/data/agents/agent_status.json  (read by dashboard)
"""

import time
import urllib.request
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ── Shared paths ──────────────────────────────────────────────────────────────

STATE_DB    = Path('/opt/d3kos/data/agents/agent_state.db')
STATUS_JSON = Path('/opt/d3kos/data/agents/agent_status.json')
LOG_PATH    = Path('/opt/d3kos/logs/agents.log')


# ── Result type ───────────────────────────────────────────────────────────────

@dataclass
class AgentResult:
    status:  str                        # 'green' | 'yellow' | 'red'
    message: str                        # short human-readable (≤ 60 chars)
    details: dict = field(default_factory=dict)


# ── Base class ────────────────────────────────────────────────────────────────

class AgentBase:
    """
    Inherit from this class to create an autonomous agent.

    Required class attributes to set in subclass:
        name             — unique key stored in DB (snake_case, e.g. 'performance')
        label            — human display name (e.g. 'Performance Monitor')
        interval_seconds — minimum seconds between runs (e.g. 300 = 5 min, 86400 = daily)

    Required method to implement:
        run() -> AgentResult
    """

    name:             str = ''     # must override
    label:            str = ''     # must override
    interval_seconds: int = 300    # must override

    def run(self) -> AgentResult:
        """Execute the agent's task. Return an AgentResult. Override in subclass."""
        raise NotImplementedError(f'{self.__class__.__name__}.run() not implemented')

    def report_failure(self, error_type: str, message: str):
        """
        Non-blocking call to FI1 failure reporter (Port 8106).
        Call this when the agent detects a significant error worth tracking
        across the fleet lifecycle. Never raises — failure to report is silent.
        """
        try:
            payload = json.dumps({
                'service':    self.name,
                'error_type': error_type,
                'message':    message[:300],
            }).encode()
            req = urllib.request.Request(
                'http://127.0.0.1:8109/report',
                data=payload,
                method='POST',
                headers={'Content-Type': 'application/json'},
            )
            urllib.request.urlopen(req, timeout=2)
        except Exception:
            pass   # FI1 may not be running yet — never block the agent

    def should_run(self, last_run_ts: Optional[float]) -> bool:
        """
        Returns True if this agent is overdue.
        On Pi startup, any agent with last_run_ts=None or older than interval runs immediately.
        This handles the case where the Pi was off at the scheduled time.
        """
        if last_run_ts is None:
            return True
        return (time.time() - last_run_ts) >= self.interval_seconds
