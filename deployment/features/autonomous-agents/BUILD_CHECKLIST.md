# Autonomous Agents Build Checklist
**Feature:** v0.9.8 — Autonomous Agents + Failure Intelligence
**Version:** 1.0
**Status:** S28 IN PROGRESS

---

## PHASE 1 — AA1 Framework + AA3 Performance Agent (S28)

### Pi Source Files
| # | File | Path on Pi | Status |
|---|------|-----------|--------|
| 1 | `agent_base.py` | `/opt/d3kos/services/agents/` | `[x]` written S28 |
| 2 | `agent_scheduler.py` | `/opt/d3kos/services/agents/` | `[x]` written S28 |
| 3 | `agents/__init__.py` | `/opt/d3kos/services/agents/agents/` | `[x]` written S28 |
| 4 | `agents/performance_agent.py` | `/opt/d3kos/services/agents/agents/` | `[x]` written S28 |
| 5 | `d3kos-agents.service` | `/etc/systemd/system/` | `[x]` written S28 |

### Dashboard Files
| # | File | Change | Status |
|---|------|--------|--------|
| 6 | `app.py` | Added `/agents/status` route | `[x]` written S28 |
| 7 | `d3kos.css` | Added `.pi-health` styles (v20) | `[x]` written S28 |
| 8 | `index.html` | Pi health dot in status bar + polling JS | `[x]` written S28 |
| 9 | `engine-monitor.html` | Section 6 Agents + updateAgents() JS | `[x]` written S28 |

### Deploy Steps
| # | Step | Status |
|---|------|--------|
| D1 | `sudo mkdir -p /opt/d3kos/services/agents/agents` | `[ ]` |
| D2 | Copy `agent_base.py`, `agent_scheduler.py`, `agents/__init__.py`, `agents/performance_agent.py` | `[ ]` |
| D3 | `sudo chown -R d3kos:d3kos /opt/d3kos/services/agents/` | `[ ]` |
| D4 | `sudo mkdir -p /opt/d3kos/data/agents /opt/d3kos/logs` | `[ ]` |
| D5 | `sudo chown -R d3kos:d3kos /opt/d3kos/data/agents` | `[ ]` |
| D6 | Copy `d3kos-agents.service` → `/etc/systemd/system/` | `[ ]` |
| D7 | `sudo systemctl daemon-reload` | `[ ]` |
| D8 | `sudo systemctl enable --now d3kos-agents` | `[ ]` |
| D9 | Verify: `sudo systemctl status d3kos-agents` → active | `[ ]` |
| D10 | Verify: `cat /opt/d3kos/data/agents/agent_status.json` → overall=green | `[ ]` |
| D11 | Copy updated `app.py` → `/opt/d3kos/services/dashboard/` | `[ ]` |
| D12 | Copy updated `d3kos.css` → `/opt/d3kos/services/dashboard/static/css/` | `[ ]` |
| D13 | Copy updated `index.html` → `/opt/d3kos/services/dashboard/templates/` | `[ ]` |
| D14 | Copy updated `engine-monitor.html` → `/opt/d3kos/services/dashboard/templates/` | `[ ]` |
| D15 | `sudo systemctl restart d3kos-dashboard` | `[ ]` |
| D16 | Browser test: `http://192.168.1.237` → Pi health dot visible in status bar | `[ ]` |
| D17 | Browser test: `http://192.168.1.237/engine-monitor` → Section 6 Agents visible | `[ ]` |
| D18 | Add `d3kos-agents` to watchdog CRITICAL_SERVICES list in `d3kos_watchdog.py` | `[x]` done S28 |

### Verify
- `[ ]` `d3kos-agents` service stays active after 10 minutes
- `[ ]` `/opt/d3kos/data/agents/agent_status.json` updates every 5 minutes
- `[ ]` Status dot shows green on Pi dashboard
- `[ ]` Agents section shows in engine-monitor with performance message
- `[ ]` Disk critical test: fill /tmp and verify _clear_tmp() runs (dev test only)

---

## PHASE 2 — AA2 Update Agent + AA4 Storage Agent (S29)

| # | Item | Status |
|---|------|--------|
| A | `agents/update_agent.py` — HostPapa version check + archive.org download + backup/apply/rollback | `[ ]` |
| B | `agents/storage_agent.py` — old log cleanup, predictive disk warning (7 day) | `[ ]` |
| C | HostPapa `version.php` — version manifest endpoint (incremental releases) | `[ ]` |
| D | Register AA2 + AA4 in `agent_scheduler.py` AGENTS list | `[ ]` |
| E | Engine-monitor: add AA2 + AA4 status cards dynamically | `[ ]` |

---

## PHASE 3 — AA5 Health Agent + AA6 Backup Agent (S30)

| # | Item | Status |
|---|------|--------|
| A | `agents/health_agent.py` — health score 0-100, daily report, weekly deep scan | `[ ]` |
| B | `agents/backup_agent.py` — USB incremental daily, full weekly, T3 cloud sync | `[ ]` |
| C | USB mount detection logic | `[ ]` |
| D | Register AA5 + AA6 in scheduler | `[ ]` |

---

## PHASE 4 — FI1 Failure Reporter + FI2 HostPapa DB (S31)

| # | Item | Status |
|---|------|--------|
| A | `failure_reporter.py` — Flask :8106, SQLite, 4-field capture, background sync | `[ ]` |
| B | `d3kos-failure-reporter.service` | `[ ]` |
| C | HostPapa `failure-report.php` + `amboat_failure_reports` table | `[ ]` |
| D | Admin CRM: failure patterns dashboard | `[ ]` |

---

## PHASE 5 — FI3 Config Packages + FI4 Recovery Mode (S32)

| # | Item | Status |
|---|------|--------|
| A | HostPapa `config-package.php` + `amboat_config_packages` table | `[ ]` |
| B | Config snapshot capture on cloud sync | `[ ]` |
| C | `cloud_agent.py` recovery mode handler | `[ ]` |
| D | FI4 fresh SD card detection + auto-download + restore | `[ ]` |

---

## Notes
- AA3 does NOT auto-kill processes or restart services — watchdog handles crash detection.
  AA3 handles resource pressure only (disk cleanup, logging for thermal/memory).
- All agents poll-based (not cron) — handles Pi off 24/7.
- Agent status JSON at `/opt/d3kos/data/agents/agent_status.json` — written atomically.
- Add `d3kos-agents` to watchdog CRITICAL_SERVICES after D18 above.
