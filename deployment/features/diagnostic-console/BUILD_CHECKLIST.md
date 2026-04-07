# v0.9.7 Remote Diagnostic Console — Build Checklist (Phases 2–4)
**Version:** 1.2 | **Created:** 2026-04-07 S26 | **Updated:** 2026-04-07 S27 | **Status:** PHASES 2+3+4 DEPLOYED — PENDING HARDWARE TEST

---

## Architecture

```
PWA (phone)
  └── Support screen
        ├── "Request Diagnostic Support" button (after ticket exists)
        │     └── Consent dialog → POST diagnostic-consent.php
        │           → HostPapa stores consent + enqueues diagnostic_collect to Pi
        └── Revoke button (while consent active)

Pi (vessel)
  └── cloud_agent.py picks up diagnostic_collect command
        └── diagnostic_agent.py (Port 8109)
              ├── Collect: syslog(24h), dmesg, kern.log, systemctl d3kos-*, ps/df/free
              ├── Strip API keys from config files
              ├── Bundle → /tmp/d3kos-diag-TIMESTAMP.tar.gz (<60s, <50MB)
              └── POST multipart → diagnostic-upload.php → LONGBLOB in DB

Admin CRM (Flask VM)
  └── /ticket/<id> detail
        ├── Diagnostic panel: bundle status, sizes, upload time
        ├── "Run AI Diagnosis" → ai_client.py → Gemini 2.5 Flash
        ├── Diagnosis panel: root cause, confidence, fix steps
        └── "Send Fix" → enqueue to command queue → Pi executes → streams output

HostPapa MySQL
  ├── amboat_diagnostic_consents  (consent tokens, 2hr TTL)
  ├── amboat_diagnostic_bundles   (LONGBLOB bundle per ticket)
  ├── amboat_diagnostics_resolved (case log on ticket resolve)
  └── amboat_diagnostics_rules    (auto-rules from 3+ pattern matches)
```

---

## Phase 2 — Diagnostic Collection (RD2 + RD3)

### DB Schema
- [x] `amboat_diagnostic_consents` — consent_id, ticket_id, user_id, device_token, granted_at, expires_at, revoked_at, status ENUM(active/expired/revoked) — written S26
- [x] `amboat_diagnostic_bundles` — bundle_id, ticket_id, device_token, bundle_data LONGBLOB, bundle_size_bytes, ai_diagnosis TEXT, created_at — written S26
- [x] `amboat_diagnostics_resolved` — case_id, ticket_id, installation_id_hash, problem_category, symptoms_hash, root_cause, fix_applied, outcome ENUM, time_to_resolution_min, created_at — written S26
- [x] `amboat_diagnostics_rules` — rule_id, symptoms_hash, recommended_fix, match_count, last_matched_at, created_at — written S26

### HostPapa PHP
- [x] `diagnostic-migrate.php` — creates all 4 tables, FLEET_SETUP_KEY protected, delete after run — written S26
- [x] `diagnostic-consent.php` — POST, app_token auth. Stores consent (2hr TTL), enqueues diagnostic_collect to Pi command queue. Returns consent_id + expires_at — written S26
- [x] `diagnostic-status.php` — GET ?ticket_id=N, app_token auth. Returns consent status + whether bundle exists — written S26
- [x] `diagnostic-upload.php` — POST, AMBOAT_API_KEY (Pi auth). Receives multipart bundle, stores LONGBLOB via send_long_data, links to ticket_id — written S26
- [x] `diagnostic-revoke.php` — POST, app_token auth. Sets consent status=revoked, revoked_at=NOW() — written S26
- [x] DEPLOY: FTP all 5 files to HostPapa staging mobile/ — S26
- [x] RUN: diagnostic-migrate.php in browser (creates 4 tables) — S26
- [x] DELETE: diagnostic-migrate.php from HostPapa after run — S26

### PWA (app.js)
- [x] Support screen: "Request Diagnostic Support" panel shown when ticket_id exists in localStorage — written S26
- [x] Consent dialog: lists 4 collected items (logs/services/ps/config), Approve / Decline — written S26
- [x] On approve: POST diagnostic-consent.php, show "Pi is collecting data" — written S26
- [x] Show consent status (active/expired/revoked/bundle_ready) — written S26
- [x] Revoke button (shown while consent active) — written S26
- [x] Poll diagnostic-status.php every 30s while consent active to show "Bundle received" when done — written S26
- [x] Restore diagPanel on screen re-render if ticket_id in localStorage — written S26
- [x] DEPLOY: FTP app.js to HostPapa staging/app/ — S26

### Pi
- [x] `diagnostic_agent.py` — collects syslog/dmesg/kern.log/services/ps/df/free/d3kOS logs/config, strips API keys, bundles tar.gz, uploads multipart — written S26
- [x] cloud_agent.py: `diagnostic_collect` handler — ACKs immediately, launches agent as subprocess — written S26
- [x] `/etc/systemd/system/d3kos-diagnostic.service` — oneshot service file — written S26
- [x] DEPLOY: SCP diagnostic_agent.py to Pi /opt/d3kos/services/diagnostic/ — S26
- [x] DEPLOY: SCP cloud_agent.py to Pi — S26
- [x] DEPLOY: install d3kos-diagnostic.service + systemctl daemon-reload — S26
- [x] DEPLOY: mkdir /opt/d3kos/services/diagnostic on Pi — S26
- [x] d3kos-cloud-agent restarted + confirmed active — S26
- [x] `/etc/sudoers.d/d3kos` — added NOPASSWD for diagnostic_fix service restarts + journalctl + reboot — S27

### Phase 2 test criteria
- [ ] PWA: "Request Diagnostic Support" panel appears on support screen for existing ticket — SW cache clear required
- [ ] PWA: Consent dialog lists collected items, Approve/Decline work
- [x] POST diagnostic-consent.php stores consent + enqueues command — confirmed S26 (bundle_id=1 in DB)
- [x] Pi receives diagnostic_collect command, runs collection (<60s), uploads bundle — confirmed S26
- [x] Bundle appears in amboat_diagnostic_bundles — bundle_size_bytes=105891 confirmed S26/S27
- [ ] PWA: "Bundle received (N KB)" shown after 30s poll — phone test required
- [ ] Revoke button cancels active consent — status=revoked in DB
- [ ] Consent auto-expires after 2 hours (check expires_at)

---

## Phase 3 — AI Diagnosis (RD4 + RD7) ✅ DEPLOYED S26

### HostPapa PHP
- [x] `diagnostic-bundle.php` — deployed S26. Returns bundle metadata + base64 bundle. TESTED S27 ✓

### Admin CRM (Flask VM)
- [x] `ticket_bundle_status` route: `/ticket/<id>/bundle-status` — deployed S26
- [x] tickets.html: Diagnostic panel (bundle info, sizes, upload time) — deployed S26
- [x] "Run AI Diagnosis" button → POST /ticket/<id>/diagnose — deployed S26
- [x] `/ticket/<id>/diagnose` route: downloads bundle, calls diagnose_pi(), stores result — deployed S26
- [x] `diagnose_pi()` function in ai_client.py — deployed S26
- [x] tickets.html: Diagnosis panel — root cause, confidence %, fix steps — deployed S26
- [x] Store diagnosis in `amboat_diagnostic_bundles.ai_diagnosis` — CONFIRMED S27 (diagnosis present in bundle_id=1)

### Phase 3 test criteria
- [x] CRM: bundle-status API returns has_bundle=true, size=105891 bytes — CONFIRMED S27
- [x] AI diagnosis stored in DB (root_cause: SignalK 404 errors, confidence=90%) — CONFIRMED S27
- [x] Diagnosis retrieved on re-load (api_diagnosis field present) — CONFIRMED S27
- [ ] CRM ticket detail page: visual verification — requires browser access to VM:5000

---

## Phase 4 — Fix Delivery + Knowledge Base (RD5 + RD6) ✅ DEPLOYED S26/S27

### DB Schema
- [x] `amboat_diagnostics_resolved` — created by diagnostic-migrate.php S26
- [x] `amboat_diagnostics_rules` — created by diagnostic-migrate.php S26

### HostPapa PHP
- [x] `diagnostic-fix.php` — deployed S26. Whitelist enforced. TESTED S27: valid=command_id=21 ✓, invalid=400 error ✓
- [x] `diagnostic-resolve.php` — deployed S26. TESTED S27: case_id=2, match_count=1 ✓
- [x] `diagnostic-past-cases.php` — deployed S26. TESTED S27: returns {cases:[], rule:null} ✓

### PWA (app.js)
- [ ] Fix approval notification (user-side approval flow) — DEFERRED to Phase 4b (not in scope for admin-only MVP)
- [ ] "Approve Fix" / "Decline" buttons — DEFERRED

### Admin CRM (Flask VM)
- [x] tickets.html: "Send Fix" form with fix_type/target dropdowns — deployed S26
- [x] `/ticket/<id>/send-fix` route: proxies to diagnostic-fix.php — deployed S26
- [x] `/ticket/<id>/resolve` route: proxies to diagnostic-resolve.php — deployed S26
- [x] `/ticket/<id>/past-cases` route: proxies to diagnostic-past-cases.php — deployed S26
- [x] tickets.html: Resolve Case panel + Knowledge Base panel — deployed S26
- [x] Pi cloud_agent.py: `handle_diagnostic_fix` handler + dispatch — deployed S26
- [x] Pi sudoers: NOPASSWD for all whitelist service restarts + journalctl + reboot — S27

### Fix command whitelist (enforced in diagnostic-fix.php + cloud_agent.py)
- restart_service: d3kos-voice, d3kos-ai-bridge, d3kos-fleet-push, signalk, nodered, d3kos-cloud-link, d3kos-predictive, d3kos-gemini-proxy, d3kos-cloud-agent
- clear_cache: signalk_cache, ai_cache, temp_files
- rotate_logs: d3kos, nginx
- update_config: gps_timeout, ai_model_id, log_retention_days
- restart_pi: requires active diagnostic consent (checked by PHP)
- recalibrate_sensor: gps, temperature, pressure, fuel
- restart_signalk: standalone

### Phase 4 test criteria
- [x] Non-whitelisted command rejected (400) — CONFIRMED S27
- [x] Valid fix enqueued (command_id=21) — CONFIRMED S27
- [x] Resolved case logged (case_id=2) — CONFIRMED S27
- [ ] Pi executes fix command end-to-end — requires Pi + cloud-agent polling
- [ ] 3+ matching cases trigger auto-rule — requires 3+ resolve events
- [ ] CRM shows past cases — requires resolved cases in DB

---

## Files This Feature Touches

### New (HostPapa staging)
- `mobile/diagnostic-migrate.php`
- `mobile/diagnostic-consent.php`
- `mobile/diagnostic-status.php`
- `mobile/diagnostic-upload.php`
- `mobile/diagnostic-revoke.php`
- `mobile/diagnostic-bundle.php`
- `mobile/diagnostic-fix.php`
- `mobile/diagnostic-resolve.php`

### Modified (PWA)
- `app/app.js` — consent UI, fix approval

### New (Pi)
- `/opt/d3kos/services/diagnostic/diagnostic_agent.py`
- `/etc/systemd/system/d3kos-diagnostic.service`

### Modified (Pi)
- `/opt/d3kos/services/cloud-agent/cloud_agent.py` — diagnostic_collect handler

### Modified (Admin CRM VM)
- `/home/d3kos-admin/app.py` — diagnose + resolve routes
- `/home/d3kos-admin/templates/tickets.html` — 3-panel expansion
