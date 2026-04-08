# Autonomous Agents and Failure Intelligence
**Feature:** d3kOS v0.9.8
**Document version:** 1.0 — S33 2026-04-07
**Status:** Phases 1–5 complete. Phase 6 (FI4 Recovery Mode) deferred to S34.

---

## 1. Design Philosophy

### "All deployments are testers"

d3kOS runs on physical boats, in marine environments, with intermittent connectivity and
real-world workloads. The fleet itself is the QA environment. Every Pi that encounters a
problem is sending a signal — the system's job is to receive that signal, normalise it,
cluster it with similar signals from other devices, route it to the developer, and
automatically verify that the fix reached the whole fleet.

This shapes every architecture decision:

- Failures are reported by the Pi automatically, not by the user manually.
- Issues are clustered by error signature (same logical problem from different Pis = one issue).
- A fix is validated on one Pi, then packaged and released to all Pis.
- The system tracks which Pis applied the fix and auto-closes the issue when coverage reaches 90%.
- The developer's view is the CRM — open issues, fix status, fleet version coverage.

### Operational reality this addresses

Before v0.9.8: a Pi failure produced a vague user complaint. The developer had no
systematic way to know if 3 Pis were all hitting the same bug, how often the error
occurred, or whether a fix reached the whole fleet.

After v0.9.8: the error surface is visible. Issues are deduplicated. Fleet version
coverage is a live dashboard. The release-to-resolution loop is tracked end to end.

---

## 2. Architecture Overview

```
 Pi Fleet                          HostPapa PHP                    Admin CRM (VM Flask)
 ──────────────────────────        ──────────────────────────       ──────────────────────
 AA2 UpdateAgent (24h)             version.php                      /publish-update
   │  checks version manifest  →   amboat_versions table            publishes .tar.gz
   │  downloads + applies update   update-publish.php               deactivates old version
   │  reports version heartbeat →  version-heartbeat.php        →   /fleet-versions
   │  reports fix confirmed     →  fix-confirmed.php               (per-Pi version status)
   │
 FI1 FailureReporter (:8109)       failure-report.php              /failures
   │  any agent calls              amboat_failure_reports          (issue lifecycle dashboard)
   │  report_failure()         →   amboat_issues                   /failure/<id>
   │  background sync thread       (cluster by signature)           (detail + lifecycle update)
                                   issue-api.php                    → fix_validated → released
                                   fix-confirmed.php               
                                   (auto-close at 90% fleet fix)
```

---

## 3. Components

### 3.1 AA2 — Update Agent (`update_agent.py`)

- Runs every 24 hours (poll-based, not cron — handles Pi being off at scheduled time).
- Fetches version manifest from `version.php`.
- **Version heartbeat**: on every successful check, POSTs current version to
  `version-heartbeat.php`. This is separate from whether an update was applied —
  the heartbeat runs even when the Pi is already up to date.
- T1/T2/T3: auto-applies incremental updates (and major if `t1_upgrade=true`).
- T0: notifies via Pi dashboard notice bar only. Never sends to cloud.
- On successful update: calls `_confirm_fix(new_ver)` → `fix-confirmed.php`.
- On update failure: calls `report_failure('update_failed', msg)` → FI1.
- On update success: restarts affected services and verifies each came back `active`.
- Rollback: if any service fails to restart, restores backed-up files and reverts
  `license.json` version.

**Backup location:** `/opt/d3kos/backups/pre-vX.X.X/` — files before patch applied.

### 3.2 FI1 — Failure Reporter (`failure_reporter.py`)

- Flask service on **port 8109**, running as `d3kos` user.
- Managed by systemd: `d3kos-failure-reporter.service`
  (starts 25s after `d3kos-agents.service`).
- Any agent calls `self.report_failure(error_type, message)` (from `AgentBase`).
- Normalises the error message (strips UUIDs, file paths, long numbers, hex addresses)
  before generating SHA-256 signature (12-char prefix).
- Stores in local SQLite: `/opt/d3kos/data/failures.db`
- Background thread syncs to HostPapa `failure-report.php` every 5 minutes.
- Endpoints: `POST /report`, `GET /health`, `GET /recent`

**Why local SQLite first:** Pi may be offline. Reports queue locally and drain when
connectivity is available.

**Error signature design:** normalisation before hashing means the same logical error
produces the same signature even when the error message contains a different timestamp,
UUID, or file path on each occurrence. This clusters them into a single issue in FI2.

### 3.3 FI2 — Issue Lifecycle Database (HostPapa MySQL)

Three tables (auto-created by PHP on first call):

**`amboat_failure_reports`** — raw per-device report log. Every report from every Pi.

**`amboat_issues`** — one row per unique error signature. Tracks:
- `status`: open → diagnosed → fix_validated → released → closed
- `affected_count` / `resolved_count` — fleet coverage counters
- `fixed_in_version` — set by developer when fix is released
- `validation_device` — device_token that first confirmed the fix

**`amboat_issue_resolutions`** — one row per (issue × device) confirming fix applied.
Prevents double-counting. Auto-closes issue when `resolved_count ≥ ceil(affected_count × 0.9)`
and no new reports in last 48 hours.

### 3.4 FI3 — Issue Dashboard (Admin CRM)

Routes: `/failures` (list with status tabs), `/failure/<id>` (detail + lifecycle update)

**Issue lifecycle (developer workflow):**
1. Pi reports error → FI1 queues → syncs to HostPapa → `amboat_issues` row created (`open`)
2. Developer sees issue in CRM → investigates → sets status to `diagnosed`
3. Developer reproduces + fixes on one Pi → sets `fix_validated` + `validation_device`
4. Developer packages fix (`package-update.py`) → publishes via CRM → version released to fleet
5. AA2 on each Pi applies update → `fix-confirmed.php` increments `resolved_count`
6. At 90% fleet coverage + 48h silence → issue auto-closes (`closed`)

### 3.5 Update Publisher

**`version.php`** (HostPapa): Returns version manifest JSON read from `amboat_versions`
MySQL table. Falls back to empty blocks if DB is unavailable — Pi stays on current
version without noise.

**`update-publish.php`** (HostPapa): API for CRM to publish/deactivate/reactivate
version entries. Auto-creates `amboat_versions` table.

**`package-update.py`** (developer laptop): CLI tool that takes a list of changed files,
maps repo paths to Pi paths, builds `d3kos-X.X.X.tar.gz` with embedded `manifest.json`,
generates SHA-256 checksum. Prints HostPapa upload path and CRM-ready values.

**`/publish-update`** (CRM): Shows active versions, publish form, version history.

**Update package format:**
```
d3kos-X.X.X.tar.gz
  manifest.json          {"version","files":[pipath,...],"services_to_restart":[...]}
  opt/d3kos/...          changed files mirrored from Pi filesystem
```

**HostPapa storage:** `wp-content/themes/twentytwenty-child/mobile/updates/`

### 3.6 Version Heartbeat

**`version-heartbeat.php`** (HostPapa): Receives current version from AA2 on every
24h run. Updates `amboat_devices.current_version`, `version_updated_at`,
`version_check_count`. Returns `latest_version` and `update_available` flag.

**Why separate from fix-confirmed:** Fix confirmation only fires when an update is
applied. Version heartbeat fires regardless — so a Pi that is already up to date
still reports its version every 24h. This gives accurate fleet coverage even when
no updates have been deployed recently.

**`/fleet-versions`** (CRM): Per-Pi table showing current version, latest version,
status pill (up_to_date / behind / unknown / stale), hours since last heartbeat,
Pi online status, version distribution bar chart.

**Status classification:**
- `up_to_date` — Pi version ≥ latest active incremental version
- `behind` — Pi version < latest, heartbeat < 48h old
- `offline` (stale) — last heartbeat > 48h ago
- `unknown` — no heartbeat received yet

---

## 4. Port Assignments

| Port | Service | Notes |
|------|---------|-------|
| 3000 | d3kos-dashboard (Flask) | Pi local web UI |
| 8084 | camera_stream_manager | Pi camera streams |
| 8086 | fish_detector | Pi ML service |
| 8100 | d3kos-tier-api | Masked (disabled) |
| 8105 | predictive_maintenance | Engine health |
| 8106 | predictive_maintenance | ← occupied, do not use |
| 8107 | cloud_agent | Pi ↔ HostPapa command queue |
| 8108 | d3kos-agents scheduler | Agent runner |
| **8109** | **d3kos-failure-reporter** | **FI1** |

---

## 5. Auth Patterns

| Endpoint | Auth method | Header |
|----------|-------------|--------|
| `failure-report.php` | Bearer + device | `Authorization: Bearer {api_key}` + `X-Device-Token` |
| `fix-confirmed.php` | Bearer + device | same |
| `version-heartbeat.php` | Bearer + device | same |
| `version.php` | None (public) | — |
| `issue-api.php` | Bearer only | `Authorization: Bearer {proxy_api_key}` |
| `update-publish.php` | Bearer only | same |
| `version-api.php` | Bearer only | same |

Pi-facing endpoints require `X-Device-Token` to identify which device is reporting.
CRM-facing endpoints use the same `AMBOAT_API_KEY` as all other admin proxies — no
additional header needed.

---

## 6. File Index

### Pi source files

| File | Pi path | Purpose |
|------|---------|---------|
| `agent_base.py` | `/opt/d3kos/services/agents/` | Base class + `report_failure()` |
| `agents/update_agent.py` | `/opt/d3kos/services/agents/agents/` | AA2 update + heartbeat + fix confirm |
| `failure_reporter.py` | `/opt/d3kos/services/agents/` | FI1 Flask service |
| `d3kos-failure-reporter.service` | `/etc/systemd/system/` | FI1 systemd unit |

### HostPapa PHP files (deploy to `mobile/`)

| File | Purpose |
|------|---------|
| `version.php` | Version manifest (DB-backed) |
| `version-heartbeat.php` | Receives AA2 version reports |
| `version-api.php` | CRM fleet version read API |
| `update-publish.php` | CRM publish/manage versions |
| `failure-report.php` | Receives FI1 failure reports |
| `fix-confirmed.php` | Tracks fix application per device |
| `issue-api.php` | CRM issue lifecycle read/write |

### Admin CRM (deploy to VM Flask app)

| File | Purpose |
|------|---------|
| `failure_routes.py` | Route snippets for `/failures`, `/failure/<id>` |
| `failures.html` | Issue list + detail template |
| `update_routes.py` | Route snippet for `/publish-update` |
| `publish_update.html` | Update publisher template |
| `fleet_versions_routes.py` | Route snippet for `/fleet-versions` |
| `fleet_versions.html` | Fleet version dashboard template |

### Developer tools

| File | Purpose |
|------|---------|
| `scripts/package-update.py` | Build update `.tar.gz` + manifest + checksum |

---

## 7. Deploy Checklist

### HostPapa (FTP to `mobile/`)
- [ ] `version.php` (replaces hardcoded JSON version)
- [ ] `version-heartbeat.php`
- [ ] `version-api.php`
- [ ] `update-publish.php`
- [ ] `failure-report.php`
- [ ] `fix-confirmed.php`
- [ ] `issue-api.php`
- [ ] Create `updates/` directory in `mobile/` for update packages

### Admin CRM VM (`/opt/crm/`)
- [ ] Insert `failure_routes.py` content into `app.py` (before `if __name__ == '__main__':`)
- [ ] Add `proxy_call_issues()` and `proxy_post_issues()` helpers to `app.py`
- [ ] Copy `failures.html` → `templates/`
- [ ] Insert `update_routes.py` content into `app.py`
- [ ] Add `proxy_call_publish()` and `proxy_post_publish()` helpers to `app.py`
- [ ] Copy `publish_update.html` → `templates/`
- [ ] Insert `fleet_versions_routes.py` content into `app.py`
- [ ] Add `proxy_call_versions()` helper to `app.py`
- [ ] Copy `fleet_versions.html` → `templates/`
- [ ] Add nav links in `base.html`:
  - `<a href="{{ url_for('failures') }}">Failures</a>`
  - `<a href="{{ url_for('fleet_versions') }}">Fleet Versions</a>`
  - `<a href="{{ url_for('publish_update') }}">Publish Update</a>`
- [ ] `sudo systemctl restart admin-crm`

### Pi
- [ ] Copy `agent_base.py` → `/opt/d3kos/services/agents/`
- [ ] Copy `agents/update_agent.py` → `/opt/d3kos/services/agents/agents/`
- [ ] Copy `failure_reporter.py` → `/opt/d3kos/services/agents/`
- [ ] Copy `d3kos-failure-reporter.service` → `/etc/systemd/system/`
- [ ] `sudo systemctl daemon-reload`
- [ ] `sudo systemctl enable --now d3kos-failure-reporter`
- [ ] `sudo systemctl restart d3kos-agents`
- [ ] Verify: `curl http://localhost:8109/health` → `{"ok":true,...}`

---

## 8. Release Workflow (step by step)

This is the workflow the developer follows to close an issue:

```
1. Issue detected
   Pi hits error → FI1 reports → amboat_issues row created (open)
   CRM /failures shows new issue

2. Diagnose
   CRM: set status = diagnosed
   Developer investigates: check recent reports, affected devices, error messages

3. Fix
   Edit file(s) on Pi (direct SSH or update)
   Test on that Pi — confirm error no longer occurs
   CRM: set status = fix_validated, set validation_device = that Pi's device_token

4. Package
   Run on laptop:
   python3 deployment/features/autonomous-agents/scripts/package-update.py \
     --version 0.9.8.1 \
     --files deployment/features/autonomous-agents/pi_source/agents/some_agent.py \
     --services d3kos-agents \
     --type incremental

   Output: d3kos-0.9.8.1.tar.gz + SHA-256 + HostPapa upload URL

5. Upload
   FTP d3kos-0.9.8.1.tar.gz to HostPapa mobile/updates/

6. Publish
   CRM /publish-update:
   - Version: 0.9.8.1
   - URL: https://atmyboat.com/staging/wp-content/themes/.../mobile/updates/d3kos-0.9.8.1.tar.gz
   - Checksum: sha256:<hash>
   - Released: today's date
   - Release notes: [what was fixed]
   - Services to restart: d3kos-agents
   Click Publish

7. Fleet rolls out
   AA2 on each Pi picks up new version on its 24h cycle
   Downloads, applies, restarts services
   Calls fix-confirmed.php → amboat_issue_resolutions + resolved_count increments
   Issue auto-closes when resolved_count ≥ 90% of affected_count + 48h silence

8. Verify
   CRM /fleet-versions: see each Pi reporting new version
   CRM /failure/<id>: watch resolved_count climb, issue closes automatically
```

---

## 9. Known Limitations and Deferred Items

- **FI4 Recovery Mode** (deferred S34): fresh SD card detects first-boot state,
  downloads config package from HostPapa, restores Pi to its pre-failure state.
  Tables and PHP endpoint (`config-package.php`, `amboat_config_packages`) not yet built.

- **T0 heartbeat**: T0 (no account) Pis do send heartbeats if `cloud-config.json`
  is populated. In practice T0 Pis have no cloud config — heartbeat silently skips.
  T0 fleet visibility is not supported by design.

- **48h staleness threshold**: chosen to allow for daily AA2 runs with some margin.
  A Pi that is powered off for 3 days will show as stale. This is correct behaviour.

- **90% auto-close threshold**: leaves room for Pis that are permanently offline,
  decommissioned, or in dry storage. 100% would leave issues open forever if one Pi
  never comes back.

- **Update package hosting on HostPapa**: HostPapa shared hosting has a 250MB file
  size limit per upload. Update packages are expected to be small (individual Python
  files, configs). Full OS images are not supported via this path.

---

*Document maintained in:* `deployment/docs/AUTONOMOUS_AGENTS_AND_FI.md`
*Source files:* `deployment/features/autonomous-agents/`
