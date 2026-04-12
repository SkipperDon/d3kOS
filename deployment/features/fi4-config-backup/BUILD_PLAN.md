# FI4 Config Backup & Recovery — Build Plan
**Version:** 1.0.0
**Tier gate:** T1, T2, T3 only
**Spec:** `deployment/docs/FI4_CONFIG_BACKUP_RECOVERY.md`
**Status:** Ready to build

---

## Overview

Four build phases. Each phase is independently deployable and testable.
Phases 1 and 2 are backend-only — no UI visible to Don until Phase 3.

```
Phase 1 — HostPapa backend    (config-backup.php + config-restore.php + DB table)
Phase 2 — Pi cloud_agent.py  (push_config_snapshot + fix_my_pi integration)
Phase 3 — Setup wizard        (Recover mode in setup.html)
Phase 4 — PWA + settings      (Recovery Key display + Restore Pi button + local cache)
```

---

## Phase 1 — HostPapa Backend

**Files to create/modify:**
- `mobile/config-backup.php` (new)
- `mobile/config-restore.php` (new)
- DB table `amboat_config_packages` (auto-created by config-backup.php)

**Deploy to:** HostPapa staging via FTP (`staging/mobile/`)

### Phase 1 — Steps

| # | Step | Detail |
|---|------|--------|
| 1 | Write `config-backup.php` | POST endpoint. Auth: X-Device-Token + X-Api-Key. Validate device token exists in wpax_usermeta. UPSERT into amboat_config_packages. Auto-create table on first call. Return {success, updated_at}. |
| 2 | Write `config-restore.php` | GET endpoint. Token via query string only. Rate limit: 5 requests/token/hour (use amboat_config_packages.restore_attempts + last_restore_at columns). Return full config_json or {success:false, error}. 404 response does not confirm token existence. |
| 3 | FTP deploy both files | Python ftplib to staging/mobile/. |
| 4 | Smoke test backup | curl POST from workstation with test device_token + dummy config. Verify row in DB. |
| 5 | Smoke test restore | curl GET with same token. Verify config_json returned matches what was posted. |
| 6 | Smoke test rate limit | 6th request within 1 hour returns 429. |

**Phase 1 acceptance:** Both endpoints respond correctly. Row created/updated in DB. Rate limit enforced.

---

## Phase 2 — Pi cloud_agent.py

**Files to modify:**
- `deployment/v0.9.4/pi_source/cloud_agent.py`
- `deployment/v0.9.4/pi_source/fix_my_pi.py`

**Deploy to:** Pi via SCP + sudo cp + service restart

### Phase 2 — Steps

| # | Step | Detail |
|---|------|--------|
| 1 | Add `CONFIG_BACKUP_FILES` list | 12 files: cloud-config.json, device-token.json, license.json, user-preferences.json, ai-config.json, slots.json, hardware.json, fleet.json, community-prefs.json, onboarding.json, timezone.txt, tts-mute.json |
| 2 | Write `_read_config_files()` | Reads each file into dict keyed by filename. Missing files skipped (not errors). Returns dict. |
| 3 | Write `push_config_snapshot()` | Reads config dict. Serialises to JSON string. SHA-256 hash. Compare to `/opt/d3kos/config/config-snapshot-hash.txt`. Skip if unchanged. POST to config-backup.php with X-Device-Token + X-Api-Key. Log result. Update hash file on success. |
| 4 | Call `push_config_snapshot()` in main loop | Called once per sync cycle. Uses existing `base_url` + `api_key` + `device_token` already available in `run()`. |
| 5 | Call `push_config_snapshot()` in `handle_pair_confirmed()` | After tier write, push snapshot so HostPapa always has current state post-pair. |
| 6 | Update `fix_my_pi.py` `run_diagnostics()` | Call `push_config_snapshot()` as Step 0 (before all other checks). Adds `config_backup` entry to checks result: `{check: "config_backup", ok: True/False, updated_at: "..."}` |
| 7 | Deploy to Pi | SCP + sudo cp cloud_agent.py + fix_my_pi.py. Restart d3kos-cloud-agent. |
| 8 | Verify on Pi | Check Pi logs for "config snapshot pushed" within 60 seconds of restart. Verify row appears in HostPapa DB. |

**Phase 2 acceptance:** Pi pushes snapshot within one sync cycle. Log shows push success. HostPapa DB row updated. Fix My Pi run includes config_backup check.

---

## Phase 3 — Setup Wizard Recovery Mode

**Files to modify:**
- `deployment/d3kOS/dashboard/templates/setup.html`
- `deployment/v0.9.4/pi_source/setup.html` (sync)

**Deploy to:** Pi via SCP + sudo cp (templates directory)

### Phase 3 — Steps

| # | Step | Detail |
|---|------|--------|
| 1 | Add "Recover Existing Pi" button to setup wizard welcome step | Placed below the normal "Begin Setup" button. Visible only on welcome screen (Step 1). |
| 2 | Add recovery mode step | Hidden div that appears when "Recover Existing Pi" tapped. Shows: heading "Restore Your Pi", instruction text, Recovery Key input (text field, 36 chars), Restore button. |
| 3 | Write `doRecover()` JS function | Reads token from input. Validates format (non-empty, reasonable length). POST to `config-restore.php?token=...` via fetch. On success: write files by calling new Flask endpoint `/setup/restore`. On error: show user-friendly message. |
| 4 | Add Flask route `/setup/restore` in `app.py` | POST endpoint. Accepts JSON config package from setup wizard JS. Writes each file in config_json to `/opt/d3kos/config/`. Restarts d3kos services. Returns {ok: true}. |
| 5 | Add Flask route to `app.py` in pi_source | Same route needed in pi source version. |
| 6 | Post-restore: redirect to dashboard | On success, wizard redirects to `/` (dashboard). Toast shows "Config restored — welcome back." |
| 7 | Add loading state | Restore button shows spinner + "Restoring..." during fetch. Prevents double-tap. |
| 8 | Deploy to Pi | SCP setup.html + app.py. Restart d3kos-dashboard. |
| 9 | Test recovery flow end to end | Manually clear config files on Pi. Open setup wizard. Enter recovery key. Verify files restored. Dashboard loads correctly. |

**Phase 3 acceptance:** Entering a valid recovery key in the wizard restores all config files and loads the dashboard. Invalid key shows a clear error. The normal setup flow is unaffected.

---

## Phase 4 — PWA + Settings UI

**Files to modify:**
- `deployment/d3kOS/dashboard/templates/settings.html` — Recovery Key display
- `deployment/v0.9.4/pi_source/settings.html` — sync
- PWA files at `atmyboat.com/staging/app/` — Recovery Key + Restore Pi + local cache

**Deploy to:** Pi (settings.html) + HostPapa (PWA files)

### Phase 4 — Steps

| # | Step | Detail |
|---|------|--------|
| 1 | Add Recovery Key to settings.html System section | Show device_token UUID read from `/opt/d3kos/config/device-token.json` via Flask template variable. Copy-to-clipboard button. Instructional text: "Write this on a label and stick it to your Pi. You will need it if you ever need to restore after a reflash." T1+ gate: hide for T0. |
| 2 | Add Flask template variable for device_token | `app.py` reads device-token.json and passes `device_token` to settings template render. |
| 3 | PWA — store config snapshot in local storage | After each successful sync that returns Pi data, fetch `/opt/d3kos/config/` snapshot via new Flask GET endpoint `/api/config-snapshot`. Store in PWA `localStorage['d3kos_config_cache_{device_token}']`. |
| 4 | PWA — "Restore Pi" button in Settings | In app Settings → Device section. Tapping shows modal: "Restore Pi from backup?" with three options: (a) Restore via Cloud (calls HostPapa), (b) Restore via App Cache (uses local storage), (c) Cancel. |
| 5 | PWA — Path 3 local push | "Restore via App Cache" option: app POSTs cached config to Pi's local IP. Pi must be on same WiFi. Uses `/setup/restore` Flask endpoint. |
| 6 | PWA — Recovery Key display | In app Settings → Device Info: show Recovery Key with Copy button. Same token as Pi settings. |
| 7 | Pi Flask — `/api/config-snapshot` GET | Returns all config files as JSON dict. Auth: session or local-only. |
| 8 | Deploy Pi changes | SCP settings.html + app.py. Restart dashboard. |
| 9 | Deploy PWA changes | FTP to HostPapa staging/app/. Bump PWA cache version. |
| 10 | Test Path 1 (app + internet) | Full end-to-end with wiped config. App restore → config recovered. |
| 11 | Test Path 3 (no internet) | Disable Pi internet. App restore from cache → config recovered over LAN. |

**Phase 4 acceptance:** Recovery Key visible and copyable in both Pi settings and app. "Restore Pi" in app works via both cloud (Path 1) and app cache (Path 3). Config snapshot stored in PWA local storage after each sync.

---

## Testing Plan

### Unit-level
- [ ] `push_config_snapshot()` — skips push when hash unchanged
- [ ] `push_config_snapshot()` — pushes when hash changes
- [ ] `config-backup.php` — rejects invalid api_key
- [ ] `config-backup.php` — accepts valid credentials, creates row
- [ ] `config-restore.php` — returns 404 for unknown token
- [ ] `config-restore.php` — returns config for known token
- [ ] `config-restore.php` — rate limit enforced at 6th request

### Integration
- [ ] Pi push → HostPapa DB row created → restore returns same data
- [ ] `pair_confirmed` handler → config snapshot pushed → DB updated
- [ ] Fix My Pi run → config_backup check appears in report

### End-to-end recovery
- [ ] **Path 1:** Wipe Pi config → open app → tap Restore → config fully restored → dashboard loads
- [ ] **Path 2:** Wipe Pi config → open setup wizard → enter token manually → config restored
- [ ] **Path 3:** Disable internet → open app → restore from cache → config restored over LAN
- [ ] **Negative:** Enter wrong token → clear error message, no partial restore

### Regression
- [ ] Normal setup wizard flow (new Pi) — unaffected
- [ ] Daily cloud sync — unaffected
- [ ] Fix My Pi (existing checks) — still pass after fix_my_pi.py change

---

## Session Estimate

| Phase | Estimated sessions |
|---|---|
| Phase 1 — HostPapa backend | 1 session |
| Phase 2 — Pi cloud_agent.py | 1 session |
| Phase 3 — Setup wizard recovery mode | 1 session |
| Phase 4 — PWA + settings UI | 1–2 sessions |
| **Total** | **4–5 sessions** |

---

## Open Decisions

| # | Decision | Default if not changed |
|---|---|---|
| 1 | Rate limit on config-restore.php (currently 5/hour) | 5 per hour per token |
| 2 | Config snapshot push frequency — every sync vs. only on change (hash) | Hash-change only (more efficient) |
| 3 | PWA cache expiry — how long to keep local config snapshot | 30 days |
| 4 | Recovery Key shown at end of setup wizard as explicit step | Yes — add to Step 8 "Ready to Set Sail" |
| 5 | Email recovery key to user on first pair | Yes — add to pair_confirmed email (future) |

---

*FI4 Config Backup & Recovery Build Plan — v1.0.0 — 2026-04-12*
*AtMyBoat.com — d3kOS feature build documentation*
