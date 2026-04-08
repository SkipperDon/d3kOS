# Autonomous Agents Build Checklist
**Feature:** v0.9.8 — Autonomous Agents + Failure Intelligence
**Version:** 1.0
**Status:** S33 COMPLETE (Phases 1–5). Phase 6 (FI4) deferred S34. Deploy steps P5-3 through P5-7 pending.

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
| A | `failure_reporter.py` — Flask :8106, SQLite, error signature, background sync | `[x]` S31 |
| B | `d3kos-failure-reporter.service` | `[x]` S31 |
| C | HostPapa `failure-report.php` + `fix-confirmed.php` + `issue-api.php` | `[x]` S31 |
| D | Admin CRM: `failure_routes.py` + `failures.html` — issue lifecycle dashboard | `[x]` S31 |
| E | `agent_base.py` `report_failure()` helper — any agent can report to FI1 | `[x]` S31 |
| F | `update_agent.py` — calls FI1 on update fail, calls FI2 fix-confirmed on success | `[x]` S31 |

### Deploy Steps (S31)
| # | Step | Status |
|---|------|--------|
| F1 | Copy `failure_reporter.py` → `/opt/d3kos/services/agents/` | `[ ]` |
| F2 | Copy updated `agent_base.py` → `/opt/d3kos/services/agents/` | `[ ]` |
| F3 | Copy updated `update_agent.py` → `/opt/d3kos/services/agents/agents/` | `[ ]` |
| F4 | Copy `d3kos-failure-reporter.service` → `/etc/systemd/system/` | `[ ]` |
| F5 | `sudo systemctl daemon-reload` | `[ ]` |
| F6 | `sudo systemctl enable --now d3kos-failure-reporter` | `[ ]` |
| F7 | Verify: `curl http://localhost:8106/health` → `{"ok":true,...}` | `[ ]` |
| F8 | Test: `curl -X POST http://localhost:8106/report -H "Content-Type: application/json" -d '{"service":"test","error_type":"test","message":"deployment test"}'` | `[ ]` |
| F9 | `sudo systemctl restart d3kos-agents` (picks up updated agent_base + update_agent) | `[ ]` |
| F10 | Upload `failure-report.php`, `fix-confirmed.php`, `issue-api.php` to HostPapa mobile/ | `[ ]` |
| F11 | Add `failure_routes.py` content + `failures.html` to admin CRM on VM | `[ ]` |
| F12 | Add `d3kos-failure-reporter` to watchdog CRITICAL_SERVICES | `[ ]` |

---

## PHASE 5 — Version Heartbeat + Fleet Version GUI (S33 — COMPLETE)

| # | Item | Status |
|---|------|--------|
| A | `version-heartbeat.php` — receives current_version + device_token from AA2 | `[x]` S33 |
| B | `amboat_devices.current_version` + `version_updated_at` columns | `[x]` S33 (ALTER TABLE in version-heartbeat.php) |
| C | `update_agent.py` — POST current version to HostPapa on every run | `[x]` S33 (_version_heartbeat() method added) |
| D | CRM `/fleet-versions` page — per-Pi version status, "behind" indicator, last check-in | `[x]` S33 (fleet_versions.html + fleet_versions_routes.py) |
| E | Document: AUTONOMOUS_AGENTS_AND_FI.md — full feature doc for v0.9.8 system | `[x]` S33 |

### Phase 5 Deploy (pending)
| # | Step | Status |
|---|------|--------|
| P5-1 | FTP `version-heartbeat.php` to HostPapa `mobile/` | `[x]` done during S33 |
| P5-2 | FTP `version-api.php` to HostPapa `mobile/` | `[x]` done during S33 |
| P5-3 | Deploy updated `update_agent.py` to Pi | `[ ]` pending |
| P5-4 | Insert fleet_versions_routes.py + proxy_call_versions() into VM app.py | `[ ]` pending |
| P5-5 | Copy fleet_versions.html to VM templates/ | `[ ]` pending |
| P5-6 | Add nav links in base.html (Failures, Fleet Versions, Publish Update) | `[ ]` pending |
| P5-7 | `sudo systemctl restart admin-crm` on VM | `[ ]` pending |

## PHASE 6 — FI4 Recovery Mode + Config Packages (S33/S34 — deferred)

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
