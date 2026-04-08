#!/usr/bin/env python3
"""
d3kOS Autonomous Agent Scheduler (AA1)
v0.9.8

5-minute master poll loop. Each agent decides if it is overdue based on
its last_run timestamp persisted in SQLite.

Design rationale:
  - Pi may not be on 24/7. Fixed-time schedules (cron at 3AM) are unreliable.
  - On startup, any agent whose interval has elapsed since last run executes immediately.
  - No external scheduler library needed — one thread, one sleep loop.

Deploying:
  sudo cp agent_scheduler.py /opt/d3kos/services/agents/
  sudo cp d3kos-agents.service /etc/systemd/system/
  sudo systemctl enable --now d3kos-agents.service

Adding a new agent (e.g. AA2):
  1. Create agents/update_agent.py inheriting AgentBase
  2. Import it below and add an instance to AGENTS
  3. sudo systemctl restart d3kos-agents
"""

import json
import logging
import logging.handlers
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List

# Ensure local imports work when run from /opt/d3kos/services/agents/
sys.path.insert(0, str(Path(__file__).parent))

from agent_base import AgentBase, AgentResult, STATE_DB, STATUS_JSON, LOG_PATH
from agents.performance_agent import PerformanceAgent
from agents.update_agent import UpdateAgent
from agents.storage_agent import StorageAgent
from agents.health_agent import HealthAgent
from agents.backup_agent import BackupAgent

# ── Agent registry ────────────────────────────────────────────────────────────

AGENTS: List[AgentBase] = [
    PerformanceAgent(),   # AA3 — every 5 min
    UpdateAgent(),        # AA2 — every 24h
    StorageAgent(),       # AA4 — every 24h
    HealthAgent(),        # AA5 — every 24h
    BackupAgent(),        # AA6 — every 24h
]

POLL_INTERVAL = 300   # seconds — 5 minutes

# ── Logging ───────────────────────────────────────────────────────────────────

LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
handler = logging.handlers.RotatingFileHandler(
    str(LOG_PATH), maxBytes=2 * 1024 * 1024, backupCount=3
)
handler.setFormatter(logging.Formatter(
    '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
))
logging.basicConfig(level=logging.INFO, handlers=[handler])
log = logging.getLogger('scheduler')


# ── Database ──────────────────────────────────────────────────────────────────

def _init_db():
    STATE_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(STATE_DB)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS agent_runs (
            name         TEXT PRIMARY KEY,
            last_run_ts  REAL,
            last_status  TEXT,
            last_message TEXT,
            run_count    INTEGER DEFAULT 0
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS agent_history (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name    TEXT,
            ts      REAL,
            status  TEXT,
            message TEXT
        )
    ''')
    conn.commit()
    conn.close()


def _load_state() -> dict:
    """Returns {agent_name: last_run_ts} — None if never run."""
    conn = sqlite3.connect(STATE_DB)
    rows = conn.execute('SELECT name, last_run_ts FROM agent_runs').fetchall()
    conn.close()
    return {r[0]: r[1] for r in rows}


def _save_result(name: str, result: AgentResult):
    now = time.time()
    conn = sqlite3.connect(STATE_DB)
    conn.execute('''
        INSERT INTO agent_runs (name, last_run_ts, last_status, last_message, run_count)
        VALUES (?, ?, ?, ?, 1)
        ON CONFLICT(name) DO UPDATE SET
            last_run_ts  = excluded.last_run_ts,
            last_status  = excluded.last_status,
            last_message = excluded.last_message,
            run_count    = run_count + 1
    ''', (name, now, result.status, result.message))
    conn.execute(
        'INSERT INTO agent_history (name, ts, status, message) VALUES (?, ?, ?, ?)',
        (name, now, result.status, result.message)
    )
    # Keep last 100 history rows per agent
    conn.execute('''
        DELETE FROM agent_history
        WHERE name = ? AND id NOT IN (
            SELECT id FROM agent_history
            WHERE name = ?
            ORDER BY ts DESC LIMIT 100
        )
    ''', (name, name))
    conn.commit()
    conn.close()


# ── Status JSON (read by Pi dashboard) ───────────────────────────────────────

def _write_status_json(state: dict, results: dict):
    """
    Writes /opt/d3kos/data/agents/agent_status.json.
    Dashboard app.py reads this file at /agents/status.
    """
    agents_out = {}
    overall = 'green'

    for agent in AGENTS:
        r       = results.get(agent.name)
        last_ts = state.get(agent.name)

        agents_out[agent.name] = {
            'label':    agent.label,
            'status':   r.status  if r else 'unknown',
            'message':  r.message if r else 'Not yet run',
            'last_run': (
                datetime.fromtimestamp(last_ts, tz=timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
                if last_ts else 'Never'
            ),
            'interval_h': round(agent.interval_seconds / 3600, 1),
        }

        if r:
            if r.status == 'red' and overall != 'red':
                overall = 'red'
            elif r.status == 'yellow' and overall == 'green':
                overall = 'yellow'

    payload = {
        'overall': overall,
        'updated': datetime.now(tz=timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),
        'agents':  agents_out,
    }

    STATUS_JSON.parent.mkdir(parents=True, exist_ok=True)
    # Atomic write via temp file — avoids dashboard reading a half-written file
    tmp = STATUS_JSON.with_suffix('.tmp')
    tmp.write_text(json.dumps(payload, indent=2))
    tmp.replace(STATUS_JSON)


# ── Main loop ─────────────────────────────────────────────────────────────────

def main():
    _init_db()
    log.info('Agent scheduler started — %d agents: %s',
             len(AGENTS), ', '.join(a.name for a in AGENTS))

    results: dict = {}   # last result per agent, kept in memory between cycles

    while True:
        state = _load_state()

        for agent in AGENTS:
            if not agent.should_run(state.get(agent.name)):
                log.debug('Agent %s: not yet due (interval %ds)', agent.name, agent.interval_seconds)
                continue

            log.info('Running agent: %s', agent.name)
            try:
                result = agent.run()
            except Exception as e:
                log.exception('Agent %s raised an unhandled exception: %s', agent.name, e)
                result = AgentResult(status='red', message=f'Agent error: {str(e)[:50]}')

            results[agent.name] = result
            _save_result(agent.name, result)
            log.info('Agent %s finished: %s — %s', agent.name, result.status, result.message)

        # Reload state (timestamps updated by _save_result above)
        state = _load_state()
        _write_status_json(state, results)

        time.sleep(POLL_INTERVAL)


if __name__ == '__main__':
    main()
