# d3kOS & AtMyBoat.com — Master Project Checklist
**Version:** 2.2 | **Last Updated:** 2026-04-08 S40 — M14 verified working (3 bugs fixed: JS syntax, onclick wiring, cloud_agent path); context menu→openDiag; font sizes increased
**Replaces:** Helm-OS/PROJECT_CHECKLIST.md · deployment/d3kOS/PROJECT_CHECKLIST.md · deployment/v0.9.3/PROJECT_CHECKLIST.md
**Archives:** `.aao-backups/20260320_000000_checklist-merge/` (all originals preserved as .bak)

> **Purpose:** Single source of truth — what is done, what is open, what was abandoned.
> Completed phases are summarised. Open items are listed in full. Abandoned work is noted with reason.

---

## LEGEND
- `[x]` Complete
- `[ ]` Not started
- `[~]` In progress
- `[!]` Blocked / needs action
- `[–]` Abandoned / superseded

---

## PART 1 — Developer Infrastructure
**Status: COMPLETE**

All Ollama executor tooling, RAG knowledge base, and Verify Agent are operational.

| Item | Status | Detail |
|------|--------|--------|
| Ollama executor v3 (`ollama_execute_v3.py`) | `[x]` | Generic phases.json-driven executor. Model: qwen3-coder:30b at 192.168.1.36:11434. Score: 97/100. |
| RAG knowledge base | `[x]` | helm_os_docs: 1,079 chunks. helm_os_source: 54 chunks. Smart filtered ingestion. |
| Verify Agent | `[x]` | Deployed on TrueNAS VM 192.168.1.103:11436. Routed to workstation GPU. |
| helm_os_context.md | `[x]` | Full Pi variable names, port map, API patterns, format rules. |
| RAG re-ingest | `[~]` | Recurring task after every Pi deployment. Command: `cd /home/boatiq/rag-stack && .venv/bin/python3 helm_os_ingest.py --collection source` |

---

## PART 2 — AAO Operating Environment
**Status: COMPLETE (1 item open)**

| Item | Status | Detail |
|------|--------|--------|
| Hooks, Emergency Brake, Sprint Mode | `[x]` | All in ~/.claude/settings.json + CLAUDE.md. |
| AAO Methodology GitHub repo | `[x]` | https://github.com/SkipperDon/aao-methodology — v1.5 current. Pushed 2026-03-20. |
| AAO Methodology website | `[x]` | https://skipperdon.github.io/AAO-Methodology/ live. |
| Session Memory Loop (session-start / session-close) | `[x]` | Deployed to both CLAUDE.md files. |
| Session Quality Metrics (Section 19) | `[x]` | Spec written and pushed. OIC (Section 20) added as 6th metric 2026-03-20. |
| SQS calculation block in CLAUDE.md | `[ ]` | Sprint scope item 5 — not yet executed. Add to session-close steps. |

---

## PART 3 — v0.9.1 Voice AI Assistant
**Status: COMPLETE — Shipped**

Full hands-free voice pipeline deployed on Pi. Vosk wake word detection, Piper TTS, Gemini/RAG/rule-based query routing, SQLite conversation logging. Service: `d3kos-voice-assistant.service`. All 18 query types tested.

---

## PART 4 — v0.9.2 Core Platform Features
**Status: COMPLETE — All features shipped. On-boat verification tasks remain.**

### 4.1 Metric/Imperial Conversion System
**Status: COMPLETE** — units.js (25/25 tests), Preferences API :8107, Settings toggle, all pages updated. Commit e3ddbef.

### 4.2 Marine Vision — Camera Overhaul (Slot/Hardware Architecture)
**Status: COMPLETE** — Dynamic slot/hardware architecture replacing hardcoded cameras.json. Supports 1–20 cameras. All 5 steps deployed 2026-03-11.

| Open item | Status |
|-----------|--------|
| Touchscreen test — Settings UI + Marine Vision (requires Pi touchscreen) | `[!]` On-boat |
| 24hr stability test + performance test (requires cameras on boat network) | `[!]` On-boat |
| setup_dhcp_reservations.py: one-line update to read hardware.json | `[ ]` Low priority |

### 4.3 Marine Vision — Original System
**Status: ABANDONED** — Superseded 2026-03-11 by camera-overhaul (§4.2). Original two-camera cameras.json system replaced entirely. All open items from original system are closed — add cameras 3 & 4 via Settings → Camera Setup → Scan + Assign. No code changes needed.

### 4.4 Gemini API Integration
**Status: COMPLETE** — Gemini proxy :8097, Settings UI, query_handler.py routing, onboarding Step 17. Commit 02d2694.

### 4.5 Remote Access API
**Status: COMPLETE** — remote_api.py :8111, API key auth, /remote/health/status/maintenance/note, Tailscale removed 2026-03-19 (replaced with LAN-only + v0.9.4 placeholder). SSE /remote/status-stream live. remote-access.html updated.

| Open item | Status |
|-----------|--------|
| Camera stream relay RTSP → HLS | `[ ]` Deferred — implement when cameras 3 & 4 purchased |

### 4.6 Post-Install Bug Fixes & UI Polish
**Status: COMPLETE** — All 14 fixes deployed 2026-03-05 via Ollama executor. Commit in Part 12.

### 4.7 Community Features (Pi Side)
**Status: COMPLETE (flows disabled)** — anonymiser.py, community-api.py :8103, community-prefs.json, settings.html community section, Node-RED flows (3 flows deployed but disabled).

| Open item | Status |
|-----------|--------|
| Re-enable Node-RED flows when v0.9.3 AtMyBoat.com community API endpoints are live | `[ ]` Blocked on v0.9.3 |
| End-to-end test: toggle on → data flows to atmyboat.com → appears on community map | `[ ]` Blocked on v0.9.3 |

### 4.8 Export Boot Race Fix
**Status: COMPLETE** — `d3kos-export-boot.service` race resolved with `set -e` + `curl` exit 7 fix. See `deployment/docs/EXPORT_BOOT_RACE_FIX.md`.

### 4.9 signalk-forward-watch (npm Plugin)
**Status: COMPLETE** — v0.2.1 published to npm 2026-03-22. SK v2.23.0 compatibility verified on Pi. Worker thread architecture. 21,719 labeled images, YOLOv8n model.

| Open item | Status |
|-----------|--------|
| Add download-on-first-run (auto-fetch model from GitHub Releases) | `[ ]` |
| Test on OpenPlotter | `[ ]` |
| Fix README accuracy — Step 2 (model download) is now unnecessary since model is bundled in npm package; remove or update that step | `[ ]` |
| Push v0.2.1 commits + README to GitHub | `[ ]` Don's task — when ready |

---

## PART 5 — v0.9.2.x UI Rebuild & Fixes
**Status: COMPLETE — Active system is v0.9.2.2 CSS v=15**

### 5.1 d3kOS Dashboard UI — Phases 0–5
**Status: COMPLETE** — Full dashboard hub (Flask :3000), Gemini proxy (:3001), AI Bridge (:3002), AvNav integration, Settings (16 sections), Phase 5 AI+AvNav features. All phases deployed and verified on Pi.

On-boat verification still pending:
- Route Analysis Widget, Port Arrival Briefing, Voyage Log Summary, Anchor Watch — require live GPS + active route + waypoint approach.

### 5.2 v0.9.2.2 Frontend UI Rebuild
**Status: COMPLETE — APPROVED AND CLOSED 2026-03-16** — Full v12 layout, 5 JS modules, Signal K WebSocket, AvNav iframe, AI panel, cameras, onboarding wizard. Commits: d94b2f9 · 7097664 · c6fd43e. CSS ?v=15.

### 5.3 v0.9.2.2 Recovery
**Status: COMPLETE** — INC-01 through INC-16 all deployed. AODA font scale (IEC 62288 Option B): 32px labels, 28px nav, 20px forms. All confirmed on Pi screen.

### 5.4 v0.9.2.3 UI Remediation
**Status: ABANDONED** — Cancelled 2026-03-18. Complete deployment failure. CSS regressions broke working dashboard. Weather panel (I-11/I-12/I-13) was scope Don never requested. Don restored from prior backup. All surviving fixes (I-05, I-07, I-08, I-14–I-19, WX fullscreen) were re-applied directly to v0.9.2.2 and deployed 2026-03-19. See V0923_PLAN.md for historical record only.

---

## PART 6 — v0.9.2 OPEN ITEMS (Active)
**These are the remaining items blocking v0.9.2 close.**

| # | Item | Owner | Status |
|---|------|-------|--------|
| 1 | UAT: 5 metric + 5 imperial users | Don (recruit users) | `[ ]` Ready — S-06 fixes deployed 2026-03-17 |
| 2 | o-charts chart activation | Don | `[ ]` See `deployment/docs/OPENCPN_FLATPAK_OCHARTS.md` |
| 3 | GPS outdoor verification | Don (Pi at dock) | `[!]` Don disputes 2026-03-19 diagnosis (V=no fix indoors). Test: check Signal K position outdoors, confirm lat/lon non-zero. Do after UAT. |
| 4 | Camera on-boat tests (24hr stability, performance, storage) | Don (on boat with cameras) | `[!]` On-boat dependency. DHCP reservations DONE 2026-03-23C (MAC→IP infinite lease, all 4 cameras). Remaining: 24hr stability test, performance, storage management. |
| 16 | **Battery voltage — verify Garmin sends PGN 127508** | Don (on boat, Garmin powered on) | `[!]` On-boat. With engine on and Garmin chartplotter running, SSH to Pi and run: `curl -s 'http://localhost:8099/signalk/v1/api/vessels/self/electrical' \| python3 -m json.tool` — if battery data appears, voltage flows to the app automatically. Currently only Pangoo device (src 64) visible on NMEA2000 — Garmin not seen (likely off at bench). No code changes needed once confirmed. |
| 22 | **Pi boot splash screen — branded d3kOS splash** | Claude | `[x]` **COMPLETE 2026-04-02 S15** — Plymouth theme deployed to Pi. Files: `deployment/features/boot-splash/theme/` (d3kos.plymouth + d3kos.script + amboat-logo.png). deploy-boot-splash.sh executed. Plymouth installed, theme registered via update-alternatives, initramfs rebuilt, cmdline.txt patched. Displays on next reboot. |
| 5 | SQS calculation block — add to CLAUDE.md session-close | Claude | `[x]` **COMPLETE** — Already in `~/.claude/commands/session-close.md`. Has been running correctly every session. Item was stale. |
| 6 | RAG re-ingest after each Pi deployment | Claude (recurring) | `[x]` **COMPLETE 2026-03-23.** 3 SCP-deployed docs (AVNAV_OCHARTS_INSTALL, AVNAV_PLUGINS, OPENPLOTTER_REFERENCE) ingested — 41 chunks total. Normal uploads auto-ingest via upload_api.py. This was a one-time exception. |
| 7 | Remove git worktrees (v0.9.2, v0.9.2.1, v0.9.3) from disk | Claude | `[x]` **COMPLETE 2026-03-23.** build-v0.9.2.1 merged (prompt→message fix, AvNav client rewrite, voyage logger sort fix). All 3 worktrees removed. Commit a3cb12c. |
| 9 | Marine Vision — UI does not match operator expectations | Don + Claude | `[x]` **COMPLETE 2026-03-23.** Rebuild confirmed done — current layout matches specified design: selector buttons → large feed → controls → status → fish detection → recordings. d3kOS design system applied. Bug fixes (blank feed on load, connecting state lock) applied in sessions 23B/23C. |
| 8 | Marine Vision — plug-and-play camera setup wizard | Claude | `[x]` **COMPLETE 2026-03-23.** Audit confirmed fully built: Settings §6 has scan, live thumbnails via /camera/frame/hw/<id>, position input with datalist, role presets, Assign All, Unassign. /camera/frame/hw/ endpoint confirmed in camera_stream_manager.py. Setup wizard Step 8 opens Settings in new tab at #s-camera. Bow camera (RLC-810A) unassigned — Don to assign via Settings → Camera Setup → Scan. |
| 10 | Fish detection — Gemini Vision species ID | Claude | `[x]` **COMPLETE 2026-03-21.** `identify_species_gemini()` + on-demand `POST /detect/identify/<capture_id>` endpoint in fish_detector.py. Sends capture JPEG to Gemini 2.5 Flash Vision API. Returns: common name, scientific name, confidence, visual features, Ontario regulation note. Stored in captures.db. Marine Vision shows "Identify Species" button per capture — tappable, retryable until satisfied. Auto-call removed (was causing 429 rate limit errors on free tier). Gemini key from existing gemini.env. |
| 11 | Ontario fish species RAG — confirm scripts run on Pi | Don/Claude | `[x]` **COMPLETE** — confirmed 2026-03-23. All 21 species PDFs already in ChromaDB vector database. `add_fish_to_rag.py` re-run confirmed "already exists" for all 21. Helm Assistant can answer Ontario fish regulation queries. |
| 12 | Engine Dashboard — restore original layout | Claude | `[x]` **COMPLETE 2026-03-21.** Full rebuild: 5 sections (Engine, Electrical, Tanks, System Status, Network Status), progress bars on all cells, alert states retained, DAY/NGT toggle, back arrow, one-finger scroll. CSS v=19, AODA compliant. |
| 13 | Helm Assistant — new page | Claude | `[x]` **COMPLETE 2026-03-21.** 4 quick-action buttons (Engine Status, Check Issues, System Health, Run Diagnostics), chat UI, RAG→Gemini fallback (MANUAL/GEMINI source badge), AODA fonts (18px min), keyboard-fix.js. Added to More menu. |
| 14 | Gemini CORS fix — d3kos-gemini proxy | Claude | `[x]` **COMPLETE 2026-03-21.** Root cause: no CORS headers on gemini_proxy.py. Browser at :3000 was blocked making cross-origin calls to :3001. Fix: `@app.after_request` CORS handler added. Key and service were correctly configured — proxy was working, browser was blocked. |
| 15 | Gemini system prompt — expand to full vessel operation | Claude | `[x]` **COMPLETE 2026-03-21.** Navigation-only prompt caused Helm Assistant to give unhelpful answers to engine/mechanical questions. Prompt now covers: engine diagnostics, electrical, mechanical, maintenance, on-board systems, navigation, safety. `_ragUseful()` threshold also tightened (30→60 chars, +8 no-info patterns). |
| 16 | Engine Dashboard + Settings — remove 960px max-width | Claude | `[x]` **COMPLETE 2026-03-21.** Engine gauge cells were ~174px wide on 1280px display due to 960px container. Settings had same constraint in `.settings-content`. Both now fill full screen width (~238px per engine cell). |
| 17 | Signal K upgrade v2.22.1 → v2.23.0 + remote_api.py port fix | Claude | `[x]` **COMPLETE 2026-03-22.** SK upgraded to v2.23.0 on Pi. remote_api.py port fixed (:3000→:8099). AvNav patch survives. All SK REST endpoints responding. Smoke test passed. |
| 18 | Boat log — voice-to-text "api unavailable, transcript not saved" | Claude | `[x]` **COMPLETE 2026-03-22B.** Three root causes: (1) CORS missing — browser at :3000 blocked reading API responses from :8095; (2) Vosk loaded per-request (~8s) exceeding nginx 30s timeout; (3) voice notes not persisted to SQLite DB. Fixes: flask-cors, Vosk singleton, DB INSERT, MIME type detection + HELM pause/resume in client. End-to-end confirmed: record → transcript → DB → export CSV. |
| 19 | Settings — o-charts section not working as intended | Don + Claude | `[x]` **COMPLETE 2026-03-22.** Root cause: openDoc() only showed toast with file path. Fix: /docs/<name> Flask route + full-screen markdown overlay with day/night theme support. Three docs deployed to Pi at /opt/d3kos/docs/. |
| 20 | Settings — AvNav charts documentation section not working as intended | Don + Claude | `[x]` **COMPLETE 2026-03-22.** Same fix as item 19 — resolved by same overlay implementation. |
| 21 | Onboarding wizard — UX overhaul + DIP switch step restore | Claude | `[x]` **COMPLETE 2026-03-23G.** 8-step wizard: back arrow, full-width, AODA marine fonts, skip buttons, localStorage persistence (d3kos_wiz_v3), camera opens new tab, settings return banner. DIP switches restored as dedicated Step 5 (option B). Commit d970afc. |

### Item 17 — Signal K v2.22.1 → v2.23.0 Upgrade Plan (revised 2026-03-22)

**Current state:** SK v2.22.1 on Pi. All d3kOS connections are unauthenticated.

**Unknowns resolved (2026-03-22 research):**
- **Auth:** v2.23.0 change only affects clients that send a *bad/revoked token* — they now get 401 instead of silent read-only fallback. Unauthenticated clients are unaffected. No token work needed **unless** security is enabled on the Pi (check Step 1).
- **Unit Preferences Framework:** Non-breaking. Values always served in SI. Framework only adds conversion formulas to metadata — never touches `value` fields. d3kOS unaffected.

**Affected files:**

| File | What it does with SK | Risk |
|------|---------------------|------|
| `signalk_client.py` | REST polling via `/v1/api/` | Low — unaffected if security off |
| `instruments.js` | WebSocket `ws://localhost:8099/signalk/v1/stream` | Low — unaffected if security off |
| `boatlog-engine.js` | WebSocket `ws://localhost:8099/signalk/v1/stream` | Low — unaffected if security off |
| `engine-monitor.html` | WebSocket `ws://localhost:8099/signalk/v1/stream` | Low — unaffected if security off |
| `remote_api.py` (v0.9.4) | REST — pre-existing port bug `:3000` instead of `:8099` | Fix regardless of upgrade |
| AvNav `signalkhandler.py` | Resources API `/v2/api/` — patched 2026-03-18 | Low — npm upgrade won't touch AvNav |

**Step 1 — Security check on Pi (Claude — before anything else)**
- [ ] Read `~/.signalk/settings.json` on Pi — look for `"strategy": "./tokensecurity"`
- If `dummysecurity` or no security key: security is off — skip Steps 2 & 3
- If `tokensecurity`: check `allow_readonly` value and decide if token work is needed

**Step 2 — Token auth in Python + JS (Claude — conditional, only if security enabled)**
- [ ] Generate long-lived token: `signalk-generate-token -u <admin> -e 0 -s ~/.signalk/security.json`
- [ ] Store in `/opt/d3kos/config/signalk.env` — never hardcode
- [ ] `signalk_client.py`: add `Authorization: Bearer <token>` header to all REST calls; `is_reachable()` stays unauthenticated
- [ ] `instruments.js`, `boatlog-engine.js`, `engine-monitor.html`: append `?token=<token>` to WS URL; token injected via Flask template

**Step 3 — Fix `remote_api.py` port bug (Claude — do regardless)**
- [ ] Change `SIGNALK_API = 'http://localhost:3000/signalk/v1/api/'` → `http://localhost:8099/signalk/v1/api/`

**Step 4 — Upgrade SK on Pi (Claude runs)**
- [ ] `cd ~/.signalk && npm install signalk-server@2.23.0`
- [ ] `sudo systemctl restart signalk`
- [ ] Verify SK responds: `curl http://localhost:8099/signalk`

**Step 5 — Verify AvNav patch survives (Claude)**
- [ ] Confirm `signalkhandler.py` line 1580 still reads `/v2/api/` post-upgrade
- [ ] `curl http://localhost:8080` — confirm AvNav loads and charts render

**Step 6 — Smoke test (Don confirms on Pi screen)**
- [ ] Instruments panel — live SOG, COG, position
- [ ] Engine monitor — live data or graceful "no NMEA2000"
- [ ] Boat log engine capture fires correctly
- [ ] AvNav charts visible
- [ ] Settings §12 Signal K status shows LIVE

---

## PART 7 — v0.9.3 AtMyBoat.com Community Platform (WordPress)
**Status: IN PROGRESS — Sessions 1–5 complete 2026-03-24. Commit 959ef65.**
**Platform:** WordPress + Twenty Twenty child theme on HostPapa staging
**Repo:** github.com/SkipperDon/atmyboat-forum (first commit e354c23 — 2026-03-24)
**Rules:** Child theme only · PHP + cURL · No Node.js · AI model = **Gemini 2.5 Flash** · AODA enforced
**Full decisions:** `deployment/v0.9.3/ATMYBOAT_BUILD_REFERENCE.md` Part 16 (authoritative)

### Phase 0 — Repo & Staging Setup
- [x] GitHub repo created, staging confirmed, FTP access established, child theme created
- [x] First git commit e354c23 — all 2026-03-13 build work under version control

### Phase 1 — bbPress Forum
- [x] bbPress installed on staging, /forum/ slug confirmed

### Phase 2 — Features (8-session plan — see BUILD_REFERENCE Part 16)
| Session | Item | Status |
|---------|------|--------|
| S1 | Registration page + login styling + QR pairing flow | `[x]` **COMPLETE 2026-03-24** |
| S1 | Legal pages — /privacy, /terms, /warranty | `[x]` **COMPLETE 2026-03-24** |
| S1 | 2A — MailPoet email notifications | `[x]` **COMPLETE** — Hook built in registration.php. Subscribes on CASL consent at registration. |
| S1 | 2B — AODA CSS completion (font fix) | `[~]` BUILD_REFERENCE corrected 2026-03-25 (Fraunces+Nunito confirmed). Content-first workflow now in place — CSS applied as part of first S6 page build, not as standalone task. |
| Done | 2C — AI Assistant (Gemini 2.5 Flash) | `[x]` Complete — on staging + committed |
| Done | 2D — Products Hub | `[x]` Complete — on staging + committed |
| S2 | /hardware, /download, /app pages | `[x]` **COMPLETE 2026-03-24** |
| S3 | /community (map), /marketplace, /features, /challenges, /hall-of-fame | `[x]` **COMPLETE 2026-03-24** |
| S4 | /directory (business listings), /dashboard (The Chart Room T1+) | `[x]` **COMPLETE 2026-03-24** |
| S5 | Mobile backend (7 tables, 10 PHP endpoints, Stripe, mPDF, version registry) | `[x]` **COMPLETE 2026-03-24** |
| S6 | **CONTENT PLAN REVIEW** — `deployment/v0.9.3/SESSION6_CONTENT_PLAN.md` — operator must approve before S6 build starts | `[x]` **APPROVED 2026-03-25** — All 6 Q&A answers recorded. See BUILD_REFERENCE Part 17. |
| S6 | **2B CSS font fix** — Source Serif 4 → Nunito in registration.php login styles (2 occurrences). | `[x]` **COMPLETE 2026-03-25 (C)** commit f8bc813 |
| S6 | **Footer not rendering correctly** — Don said "move on" 2026-03-25 (C). Root cause unknown. Not blocking S6 content. | `[!]` Deferred by operator |
| S6 | **`/about`** — Our Story page. | `[x]` **COMPLETE 2026-03-25** commit 7ce2c06 |
| S6 | **`/contact`** — Contact Us. AI assistant + form + skipperdon@atmyboat.com. | `[x]` **COMPLETE 2026-03-25 (C)** commit 91b7cfa |
| S6 | **`/pricing`** — Tier comparison T0/T1/T2/T3. Full feature matrix, FAQ, CTAs. | `[x]` **COMPLETE 2026-03-25 (C)** commit cfdefbf |
| S6 | **`/upgrade`** — Stripe Checkout, authenticated, T2/T3. | `[x]` **COMPLETE 2026-03-25 (C)** commit 5b8311e |
| S6 | **`/help`** — Help Centre. AI widget + 6 quick-link cards. | `[x]` **COMPLETE 2026-03-25 (C)** commit 85458b3 |
| S6 | **`/help/software-update`** — OTA + manual image replacement. | `[x]` **COMPLETE 2026-03-25 (C)** commit 85458b3 |
| S6 | **`/help/software-downgrade`** — Manual reflash guide. | `[x]` **COMPLETE 2026-03-25 (C)** commit 85458b3 |
| S6 | **`/help/create-subscription`** — T2/T3 signup walkthrough. | `[x]` **COMPLETE 2026-03-25 (C)** commit 85458b3 |
| S6 | **`/help/cancel-subscription`** — Cancellation steps + grace period. | `[x]` **COMPLETE 2026-03-25 (C)** commit 85458b3 |
| S6 | **`/hardware` connectivity update** — NMEA 2000 / WiFi / Ethernet 3-card section. | `[x]` **COMPLETE 2026-03-25 (C)** commit 11592b1 |
| S6 | **`/products` connectivity update** — How It Connects diagram + 3 description cards. | `[x]` **COMPLETE 2026-03-25 (C)** commit 11592b1 |
| S6 | **Stripe subscription lifecycle webhooks** — checkout.session.completed, invoice.payment_failed, customer.subscription.deleted, customer.subscription.updated. | `[x]` **COMPLETE 2026-03-25 (C)** inc/stripe-webhook.php commit 5b8311e |
| S6 | **Downgrade logic** — revert tier to T1 on subscription.deleted, grace period on payment_failed, email notifications. | `[x]` **COMPLETE 2026-03-25 (C)** inc/stripe-webhook.php commit 5b8311e |
| S6 | **Multi-boat schema fix** — ALTER TABLE before live push. Must be done before Phase 4. | `[x]` **COMPLETE** commit 05006ef |
| S6 | **data-ingress.php returns current tier** — add `"tier": "T2"` to response JSON. | `[x]` **COMPLETE** commit 05006ef |
| S6 | **T2 monthly Fix My Pi counter reset** — WP-Cron daily, fires on 1st of month. | `[x]` **COMPLETE** commit 05006ef |
| S6 | Community API endpoints — 5 PHP files. GPS blur enforced. | `[x]` **COMPLETE** commit 05006ef |
| S6 | **AODA pass 2** — `--text-faint` var, `code` element override, help page font sizes. Don confirmed all items cleared. | `[x]` **COMPLETE 2026-03-26** commit fb9bb5b |
| S6 | **data-ingress.php gaps** — pi_id write-back + last_seen_at + d3kos_version to amboat_devices, last_seen_at to d3kos_pairings, full feature matrix + fmp_remaining in response. | `[x]` **COMPLETE 2026-03-26** commit 0c0c6d9 |
| S6 | **T2 FMP cron meta key bug** — `atmyboat_fmp_month_count` → `atmyboat_fmp_used_month` in functions.php. | `[x]` **COMPLETE 2026-03-26** commit c88c444 |
| S6 | **FMP lifecycle** — `report_result` endpoint, auto-refund on failure/timeout, `charge.refunded` webhook, email notification, `amboat_billing.refunded` column. | `[x]` **COMPLETE 2026-03-26** commit 143edad |
| S6 | **Multi-boat schema** — 7 ALTER TABLE: amboat_billing (refunded/refunded_at), community_positions (pi_id PK), command_queue (pi_pending index), engine_snapshots (vessel_date index), alerts (vessel_date index), d3kos_pairings (last_seen_at). | `[x]` **COMPLETE 2026-03-26** commit 0bc5b29 |
| S6 | **Community map wiring** — community-get.php + community-markers.php + Leaflet 1.9.4 on page-community.php. | `[x]` **COMPLETE 2026-03-26** commit c0ecd6d |
| S6 | **Account page AODA + billing** — 6 sub-18px fixes, refund status in billing table, last_seen_at on devices, SVG colour fix. | `[x]` **COMPLETE 2026-03-26** commit bf1f0a5 |
| S6 | **`/accessibility`** — AODA compliance statement page (Ontario legal requirement). | `[x]` **COMPLETE 2026-03-26** commit 7c0dfe0. **UPDATED 2026-04-01** — compliance badges (AODA, WCAG 2.0 AA, OWASP, IEC 62288) + Security Practices section (6 cards) added. commit 14cf1b3. |
| S6 | 2E — SEO (Yoast, sitemap, Bing Webmaster) | `[ ]` Deferred to post-launch |
| **Operator task** | **WordPress admin: create all pages** — install-pages.php run, Safety + Account created manually, slugs fixed via fix-slugs.php. | `[x]` **COMPLETE 2026-03-25 (D)** |
| **Operator task** | **WordPress admin: update menus** — Main menu verified OK. Footer menus set up. | `[x]` **COMPLETE 2026-03-26** |
| **Operator task** | **WordPress admin: /accessibility page** — page created in WP admin, accessibility template assigned. | `[x]` **COMPLETE 2026-03-26** confirmed by Don |
| **Operator task** | **Stripe setup** — 2 webhooks created, all keys added to server inc/atmyboat-config.php. | `[x]` **COMPLETE 2026-03-25 (D)** |
| **Operator task** | **Database schema** — 12 tables installed via install-schema.php (browser-run). pi_installation_id migration ran. | `[x]` **COMPLETE 2026-03-25 (D)** |
| **Operator task** | **Fix My Pi cron** — cPanel cron every 5 min, fix-my-pi-timeout.php confirmed active. | `[x]` **COMPLETE 2026-03-25 (D)** |
| **Operator task** | **Full theme deploy to staging** — zip upload + extract via cPanel. All new files confirmed. | `[x]` **COMPLETE 2026-03-25 (D)** |
| **S6 gap** | **mobile/config.php template** — server-only file referenced by all mobile endpoints, never committed. Create placeholder template in repo next session. | `[x]` **COMPLETE** commit ee8011d |
| **S6 fix** | **`/hardware` BOM display too small** — font sizes in BOM cards and connectivity section need review. Don flagged 2026-03-25 (C). Address in next session. | `[x]` **COMPLETE** commit 48b88b4 |
| S7 | **`/account`** — Account management: current tier, billing history, cancel subscription, paired devices. Reads Stripe Customer Portal. | `[x]` **COMPLETE 2026-03-25 (D)** commit f206a1d |
| S7 | **`/safety`** — Safety features page: Forward Watch, engine protection, anchor watch, cameras, weather, alerts. | `[x]` **COMPLETE 2026-03-25 (D)** commit 8c04b0e — fonts fixed commit 3a2138d |
| S7 | **FTP deploy via Python** — Deploy single files via Python ftplib (bash breaks ! in password). | `[x]` **COMPLETE 2026-03-25 (D)** — page-safety.php deployed via Python FTPS |
| S7 | **Footer menu** — Create footer menu in WordPress Admin → Appearance → Menus. | `[x]` **DONE 2026-03-26** — 4 nav locations registered (footer-platform, footer-community, footer-resources, footer-legal). Don confirmed menus set up. |
| Deferred | /compatible — engine checker (needs Don's compatibility data list first) | `[!]` Blocked on data |

### T3 Vessel Limit — RESOLVED 2026-03-25
**`[x]` DECISION MADE: T3 = unlimited vessels. No cap. No soft limit.**
Rationale: Admiral tier positioning. No abuse risk at launch volumes. Future enterprise conversations handled ad hoc.
Affects: `d3kos_pairings` schema (no enforced limit), pricing copy ("unlimited vessels"), `pair-device.php` (no ceiling check for T3).

### Fix My Pi Automation Architecture — NEW S6 TASK
**`[ ]` Build Fix My Pi end-to-end automation (S6)**
Full spec: `ATMYBOAT_BUILD_REFERENCE.md` Part 17.4
- Pi bash watchdog script (`fix-my-pi-watchdog.sh`) — bash only, survives broken Python
- Systemd timer on Pi (5–10 min poll interval)
- HostPapa PHP endpoints: `fix-my-pi-job.php`, `fix-my-pi-result.php`, `fix-my-pi-timeout.php`
- 30-min timeout → automatic Stripe refund + reflash email
- Expectation disclaimer shown before payment on `/fix-my-pi` page
- Request initiated from mobile app (not Pi dashboard)

### 8.3 — Multi-Boat Schema Fix (S6 — before live push)
**Why S6:** Current schema breaks silently for any user with >1 Pi. ALTER TABLE on staging costs nothing. On a live HostPapa database it requires a migration. Fix now.

**Schema changes required:**

| Table | Change | SQL |
|-------|--------|-----|
| `d3kos_pairings` | Add `vessel_name VARCHAR(80) NOT NULL DEFAULT ''` | `ALTER TABLE d3kos_pairings ADD COLUMN vessel_name VARCHAR(80) NOT NULL DEFAULT '';` |
| `d3kos_pairings` | Add `vessel_type VARCHAR(50) DEFAULT 'powerboat'` | `ALTER TABLE d3kos_pairings ADD COLUMN vessel_type VARCHAR(50) DEFAULT 'powerboat';` |
| `d3kos_pairings` | Add `is_primary TINYINT(1) DEFAULT 0` — marks the default boat shown on app open | `ALTER TABLE d3kos_pairings ADD COLUMN is_primary TINYINT(1) NOT NULL DEFAULT 0;` |
| `amboat_engine_snapshots` | Add `pi_installation_id VARCHAR(64)` — without this, two Pis write to the same user bucket and overwrite each other | `ALTER TABLE amboat_engine_snapshots ADD COLUMN pi_installation_id VARCHAR(64) DEFAULT NULL;` |
| `amboat_alerts` | Add `pi_installation_id VARCHAR(64)` — same issue for alerts | `ALTER TABLE amboat_alerts ADD COLUMN pi_installation_id VARCHAR(64) DEFAULT NULL;` |

**`data-ingress.php` logic change (S6):**
- Currently writes engine snapshot and alerts to `user_id` only
- Must also write `pi_installation_id` to each snapshot and alert row
- Pi sends its `installation_id` in the request body already — just needs to be stored

**`pair-device.php` logic change (S6):**
- On QR pairing, prompt for `vessel_name` and `vessel_type`
- If this is the account's first pairing: set `is_primary = 1` automatically
- If not the first: set `is_primary = 0` (user can change in app settings)

### Operator Actions Required Before Staging Deploy (Sessions 1–5)
- [ ] Create `mobile/config.php` from `config.php.example` — add DB credentials, Stripe keys, Gemini key, API key
- [x] Import `setup/mobile-schema.sql` via phpMyAdmin → 7 tables — **DONE 2026-03-26** (tables installed via s1-setup.php scripts in S1 session; confirmed by Don 2026-03-26)
- [ ] Run `setup/install-pages.php?key=<key>` once to create all WP pages, then delete the file
- [ ] Install MailPoet plugin on staging if not already installed
- [ ] Create `.env` from `.env.example` with FTP credentials, then run `deploy/sync-staging.sh`

### Phase 3 — AODA Compliance Audit (Session 7)
**Owner: Don** — Keyboard nav · WAVE scan · Touch targets (≥48×48px) · Contrast (4.5:1) · Screen reader
- [x] **COMPLETE 2026-03-26** — Don ran WAVE on all pages and confirmed all red items cleared. Known exception: WordPress frame WP bar (not our code, ignored). Footer still broken but deferred by operator.
- **WAVE FORUM RE-TEST COMPLETE (S47 addendum 2026-04-11):** 24 contrast errors → 3 → 0. Final fix: `li.bbp-header` / `ul.bbp-forums-header` explicit dark background. Don confirmed "all good now." AIM Score: 9/10.
- **OPERATOR ACTION STILL PENDING:** Run bbPress repair at staging/wp-admin/tools.php?page=bbp-repair → "Recount all forum topics" to fix stale counts (AI-Assisted Fixes: 6 should be 3; d3kOS Support: 9 should be 5; Engine & Mechanical: 6 should be 3). Note: repair ran S48 — counts still off. Operator chose to leave.
- **S48 FIX:** `single.php` — "← Back to Blog" was shown on bbPress topic pages (WordPress falls back to single.php for `topic` post type). Fixed: post type check added; topics now show "← Back to Forum" linking to parent forum. Deployed 2026-04-11.

### Phase 3B — Pre-Launch Security & Testing (REQUIRED before Phase 4)

#### Gemini AI Security Hardening
| # | Item | Detail | Status |
|---|------|--------|--------|
| GS1 | System prompt hardening | Restrict Gemini to marine topics only (d3kOS, boat maintenance, AtMyBoat.com features). Explicit refusal instructions for off-topic, political, commercial, or harmful requests. | `[x]` **COMPLETE 2026-04-01** — strict refusal rules in system_instruction(). Off-topic → "I can only help with marine and boating questions." Role-play/override attempts → same refusal. |
| GS2 | Prompt injection defence | Detect and block injection patterns in user input before sending to Gemini API: "ignore previous instructions", "you are now", "disregard", "override", "new instructions:", "system:". Log attempts. Return polite refusal. | `[x]` **COMPLETE 2026-04-01** — detect_injection(): 28 patterns. Blocked before Gemini call. Logged as SECURITY event (no content stored). |
| GS3 | Output filtering | Server-side scan of Gemini response before returning to browser. Block: code execution instructions, binary/hex payloads, external URLs not on allowlist, anything that looks like an exploit or attack vector. | `[x]` **COMPLETE 2026-04-01** — filter_output(): 11 regex patterns block code/hex. URL allowlist (18 trusted marine domains) — unlisted URLs replaced with [link removed]. |
| GS4 | Rate limiting | Per-user (by IP + session) request budget: max 20 requests/session, max 50/day. Hard server-side block — not just JS. Prevents API abuse and cost overrun. | `[x]` **COMPLETE 2026-04-01** — WP transients, hashed IP. 20 req/hour + 50 req/day. Counter only increments on successful response. |
| GS5 | Input sanitization | Strip or escape HTML, script tags, null bytes, and control characters from user input before it touches the Gemini API or gets stored in any log. | `[x]` **COMPLETE 2026-04-01** — sanitize_input(): null bytes + control chars stripped, HTML stripped, whitespace normalised, 500-char cap. |
| GS6 | Security test — adversarial prompts | Manually test 10+ attack prompts: jailbreaks, role-play overrides, indirect injections, topic bypass attempts, binary payload attempts. All must return refusal, none must succeed. Document test results. | `[x]` **COMPLETE 2026-04-02 S15** — 15 test cases run manually by operator on staging. 13 attack tests: all refused correctly. Tests 14–15 (normal marine questions): proper marine answers returned. Hex decode prompt (bonus test) correctly refused. GS1–GS6 ALL COMPLETE. |

#### Stripe End-to-End Testing (staging)
| # | Item | Detail | Status |
|---|------|--------|--------|
| ST1 | T2 subscription flow | Stripe test mode: complete checkout for $9.99/mo. Confirm: `checkout.session.completed` webhook fires → user tier updated to T2 in `wpax_usermeta` → Pi tier sync on next export. | `[x]` **COMPLETE 2026-04-01 — confirmed by Don** |
| ST2 | T3 annual flow | Same for $99.99/yr. Confirm tier = T3 in DB. | `[x]` **COMPLETE 2026-04-01 — confirmed by Don** |
| ST3 | Payment failure + grace period | Simulate `invoice.payment_failed` webhook. Confirm: email sent, tier NOT immediately downgraded, grace period active. | `[x]` **COMPLETE 2026-04-01 — confirmed by Don** |
| ST4 | Subscription cancellation | Simulate `customer.subscription.deleted`. Confirm: tier reverts to T1, access gates update, email sent. | `[x]` **COMPLETE 2026-04-01 — confirmed by Don** |
| ST5 | Fix My Pi $29.99 flow | T1 user triggers Fix My Pi in PWA. Confirm: Stripe charge → webhook → `fix_my_pi` command queued → Pi picks up → result returned → charge shown in billing history. | `[x]` **COMPLETE 2026-04-01 — confirmed by Don** |
| ST6 | Fix My Pi auto-refund | Simulate 30-min timeout (no Pi result). Confirm: automatic Stripe refund issued, `amboat_billing.refunded = 1`, refund email sent to user. | `[x]` **COMPLETE 2026-04-01 — confirmed by Don** |
| ST7 | Switch to live Stripe keys | After test mode confirmed: swap test keys for live keys in `inc/atmyboat-config.php` on staging. Run one live T2 test charge then immediately refund. Confirm live webhook fires. | `[x]` **COMPLETE 2026-04-01 — confirmed by Don** |

### Phase 4 — Staging → Live
**Owner: Don's hands only — DEFERRED by operator decision 2026-03-26**
**Trigger: After v0.9.4 and v0.9.4.1 are complete. No live push before then.**
- [x] UpdraftPlus full backup of live site — done 2026-03-26
- [ ] Architecture flow diagram complete (see Part 7A below)
- [x] Gemini AI security hardening complete (GS1–GS6 ALL COMPLETE 2026-04-02. 15/15 adversarial test cases passed on staging.)
- [x] Stripe E2E testing complete (Phase 3B above — all ST items) — confirmed 2026-04-01
- [ ] Proper live deploy plan — to be scoped when v0.9.4.1 is complete
- [ ] Post-push smoke test (all pages, AI widget, Stripe Fix My Pi)
- [–] ~~GitHub repo set to Private~~ — REMOVED: OTA firmware hosted on archive.org; public repo does not block downloads. Don confirmed 2026-04-11.
- [ ] Rotate Gemini API key
- [ ] Change FTP password for d3kos@atmyboat.com
- [x] **PRIVACY POLICY** — Published to WordPress. Confirmed by Don 2026-04-11.
- [ ] **UPDATE cPanel CRON JOBS (M15-D)** — Two cron jobs were added in staging. Before/after live push, update BOTH:
  - `offline-check.php`: change `/staging/wp-content/...` → `/wp-content/...`
  - `fix-my-pi-timeout.php` (if staging URL): confirm it points to live URL
  - Remove the staging-URL versions once live versions are confirmed working
  - cPanel → Advanced → Cron Jobs → edit each entry

### Post-Launch
- [ ] Monitor Gemini API usage (free tier: 20 req/day)
- [ ] UAT with real boaters (ages 45–70)
- [ ] Node-RED flow activation — endpoints now built in S6. After live push: replace placeholder URL in "Post to Community DB" nodes, create /opt/d3kos/config/cloud-credentials.json, enable 3 flows. See Part 8A §8A.2.

### Abandoned v0.9.3 Concept
**Status: ABANDONED** — An earlier v0.9.3 concept (Next.js 15 + Supabase + Stripe + Vercel) was superseded by the current WordPress + HostPapa approach. The original spec is archived at `deployment/v0.9.3/old instructions/PROJECT_CHECKLIST.md.bak`. Do not action any items from that spec.

---

## PART 7A — Pre-Deployment: Architecture Diagram & Credential Audit
**Status: NOT STARTED — REQUIRED before any live deployment**
**Why this exists:** Three platforms (website, d3kOS Pi, PWA) connect through ~12 credentials and 6 external services. Before going live, Don needs a single document that maps every credential, every service-to-service connection, and every data flow. This is the reference used to verify nothing is missing and nothing is hardcoded.

### 7A.1 — Architecture Flow Diagram

| # | Item | Detail | Status |
|---|------|--------|--------|
| AD1 | Service map — all platforms and ports | Document every running service: Pi ports (3000, 8084, 8093, 8095, 8099, 8103, 8107, 8111...), HostPapa PHP endpoints, Metered.ca TURN, Stripe, Gemini API, Signal K. One diagram. | `[x]` **COMPLETE 2026-04-02 S15** — `deployment/docs/ARCH_SERVICE_MAP.md` |
| AD2 | Data flow diagram | Pi → HostPapa (export_worker.py → data-ingress.php) → PWA (dashboard-data.php) → user. Node-RED → community endpoints. Alert → alert_watcher → export → HostPapa → PWA push. | `[x]` **COMPLETE 2026-04-02 S15** — `deployment/docs/ARCH_DATA_FLOW.md` |
| AD3 | WebRTC path diagram | PWA → turn-credentials.php → ICE gather → STUN (Google/Cloudflare) → TURN (a.relay.metered.ca) → Pi live_session.py → data channel open. Show CGNAT traversal. | `[x]` **COMPLETE 2026-04-02 S15** — `deployment/docs/ARCH_WEBRTC_PATH.md` |
| AD4 | Payment flow diagram | User → Stripe Checkout → webhook (HostPapa) → tier updated in DB → Pi cloud_agent sync → license.json updated. Fix My Pi: PWA → app-command.php → Stripe charge → command queue → Pi fix_my_pi.py → result → auto-refund if timeout. | `[x]` **COMPLETE 2026-04-02 S15** — `deployment/docs/ARCH_PAYMENT_FLOW.md` |
| AD5 | Credential map | Every credential listed: what it is, which service owns it, which services consume it, where it is stored (Pi config file, HostPapa PHP file, Stripe dashboard, etc.). No actual values — just the map. | `[x]` **COMPLETE 2026-04-02 S15** — `deployment/docs/ARCH_CREDENTIAL_MAP.md` |

### 7A.2 — Pre-Launch Credential Audit

| # | Item | Detail | Status |
|---|------|--------|--------|
| CA1 | Verify all credentials are in secure locations | No hardcoded keys in any PHP, Python, or JS file committed to git. All keys in: `inc/atmyboat-config.php` (HostPapa, gitignored), `cloud-config.json` (Pi, gitignored), `.env` (local dev, gitignored). | `[x]` **COMPLETE 2026-04-02 S15** — Repo scan clean. Pre-commit hooks on both repos. All secrets gitignored. |
| CA2 | Credential rotation before live push | AMBOAT_API_KEY, Gemini API key, FTP password, Stripe webhook secrets — all rotated to fresh values before live. Old values (used during development) must not survive to production. | `[x]` **COMPLETE — confirmed by Don 2026-04-11.** |
| CA3 | Verify `.gitignore` coverage | Confirm every secrets file is covered: `atmyboat-config.php`, `cloud-config.json`, `cloud-credentials.json`, `.env`, `api-keys.json`. Run `git status` — none of these should appear. | `[x]` **COMPLETE 2026-04-02 S15** — Verified in both repos. All secrets files gitignored. Added `*-diag.php` + `check-*.php` to atmyboat-forum .gitignore. |
| CA4 | Document credential vault | Don's credential document updated with final production values for all: WordPress admin, HostPapa cPanel, FTP, Stripe (live keys + webhook secrets), Gemini API key, AMBOAT_API_KEY, Metered.ca TURN credentials, Pi SSH key location. | `[~]` **IN PROGRESS S27c** — 10 known fields filled (FTP pw, staging DB pw, Stripe test keys x3, Gemini staging key, TURN credentials, Pi device_token, VM password). ~20 fields marked `[DON TO PROVIDE]` — require cPanel pw, prod DB pw, WP admin credentials, Stripe live keys, email/IMAP/SMTP. |
| CA5 | Pre-commit hook active on atmyboat-forum repo | Verify `.git/hooks/pre-commit` blocks API key patterns in forum repo (same as Helm-OS). If absent: add it before any live-key commits are possible. | `[x]` **COMPLETE 2026-04-02 S15** — Hook created: `atmyboat-forum/.git/hooks/pre-commit`. Blocks 8 patterns: Stripe live/test, webhook, Gemini, AMBOAT_API_KEY, Anthropic, OpenAI, Metered TURN. |

---

## PART 8 — v0.9.4 d3kOS Mobile Companion App (PWA)
**Status: PLANNED — Not started. Pre-build task: remove Tailscale from Pi (done 2026-03-19).**
**Strategy:** `deployment/docs/MOBILE_APP_STRATEGY_BRIEF.md` v2.0.0
**Q&A record (authoritative):** `deployment/docs/MOBILE_APP_QA_RECORD.md` v1.0.0

### 8.1 — PWA Foundation & Live Tunnel

| Build step | Status |
|------------|--------|
| Pre-build: Remove Tailscale from Pi | `[x]` Done 2026-03-19 |
| Command queue / OTA / Fix My Pi broker (HostPapa PHP+MySQL) | `[x]` **DONE — Built in v0.9.3 S5** (register-device.php, pair-device.php, command-queue.php, fix-my-pi-billing.php, pdf-report.php + 7-table schema) |
| **v0.9.4 S1 — Pi cloud infrastructure** | `[x]` **DONE 2026-03-26** — export_worker.py (ingress format + auth), export_categories.py (13 categories), cloud_agent.py (command consumer), cloud-config.json, device-token.json, d3kos-cloud-agent.service. End-to-end test passed. |
| **Security: Rotate AMBOAT_API_KEY** | `[x]` **DONE 2026-03-27** — New key written to Pi cloud-config.json, service restarted. Don updated mobile/config.php on HostPapa staging. |
| Foundation (PWA shell on GitHub Pages) | `[x]` **DONE 2026-03-26 S2** — manifest.json, sw.js, index.html, app.css, app.js, 6 screens. Deployed to `atmyboat.com/staging/app/`. |
| PWA icon — SVG source | `[x]` **DONE 2026-03-26 S2C** — icon.svg has AtMyBoat logo base64-embedded on navy background. Deployed to `staging/app/icons/icon.svg`. |
| PWA icon — PNG files (192px + 512px) | `[x]` **DONE 2026-03-27** — icon-192.png + icon-512.png generated via Chrome DevTools canvas script and uploaded to `staging/app/icons/` via cPanel. |
| Delete d3kos-app GitHub repo | `[x]` **DONE 2026-03-27** — github.com/SkipperDon/d3kos-app deleted by operator. |
| WebRTC/STUN live tunnel (Pi ↔ phone) | `[x]` **LAB TEST PASSED 2026-03-27 S6b-LiveTest** — Pi 192.168.1.237 ↔ Phone 192.168.1.51, peer reflexive ICE, data channel open, "● Live — updating every 5s" confirmed. Bugs fixed: signal URL (missing WP theme path), rtc-signal.php bind_param type ('ssiis'→'ssiss' — SDP was stored as int 0), role not updated on answer (poll_offer returned answered sessions forever), ICE candidate JSON format. Commits: Helm-OS a00b463, forum 2f875f9. |
| **Camera live feed over WebRTC** — MJPEG stream endpoint + replaceTrack sync fix | `[x]` **DONE 2026-03-27 S6c** — Added `/camera/stream/hw/<id>` MJPEG endpoint to camera_stream_manager.py. Fixed `ensure_future(replaceTrack())` TypeError (replaceTrack is sync in aiortc 1.x). Camera feed confirmed working. |
| Media capture/transfer (Pi → app via data channel) | `[x]` **DONE 2026-03-27 S6b** — Photo (JPEG via camera_stream_manager.py), video (MP4 via record_start/stop), binary chunked transfer 16KB/chunk, MD5 ack, Pi deletes on receipt, saveMediaToDevice (browser download). MEDIA_README.txt on Pi with SCP instructions. 90% disk warning. |
| screens.media — media library screen | `[x]` **DONE 2026-03-27 S6b** — Storage bar, no-connection guard, file list with ↓Get/✕Del per file, Transfer All, SCP footnote. Accessed via Media Library button on live screen. |
| `dc.binaryType = 'arraybuffer'` fix in app.js | `[x]` **DONE 2026-03-27 S6b-UserTest** — Added after `createDataChannel('sensors')`. Commit Helm-OS efb337d. |
| **pi_installation_id mismatch fix** — data-ingress.php stored license.json hex as pi_installation_id; app queries by device_token UUID; everything returned empty | `[x]` **DONE 2026-03-27 S6b-UserTest** — data-ingress.php now uses `$auth['device_token']`. Also fixed dashboard-data.php alert COUNT (unfiltered) + list-reports.php missing-table guard. Commits: forum 84a2438, 752c12c. Stale DB data (3861513b314c5ee7) purged by operator via phpMyAdmin. |
| **v0.9.3.1 — PWA AODA pass** — full font size + touch target audit on app.css + app.js | `[x]` **DONE 2026-03-27** — All readable text ≥1rem, supplemental labels ≥0.9rem, all touch targets ≥48×48px. #online-dot aria-label now updates dynamically. #header-vessel vessel-switcher role/keyboard already correct. Commit Helm-OS ec94e4a. Deployed to staging/app/. |
| **On-boat cellular test** — WebRTC live tunnel confirmed on LAN. Must verify it works over mobile data before v0.9.4 ships. | `[x]` **DONE 2026-03-27 S6c** — TURN relay via Metered.ca confirmed working over cellular CGNAT. See TURN fix notes below. |
| Core PWA features (Find My Boat, boat health dashboard) | `[x]` **DONE 2026-03-26 S2** |
| Fix My Pi (diagnostic + restore, $29.99/incident) | `[x]` **DONE 2026-03-26 S2** — fix_my_pi.py deployed. Pi-side diagnostics + service restarts + disk + config + network checks. PWA Stripe flow = S4. |
| PDF Reports via Gemini + FPDF (all tiers — no cap) | `[x]` **DONE 2026-03-27 S6** — pdf-engine-report.php (Gemini 2.0 Flash, aggregated stats, FPDF 1.86, AI disclaimer), list-reports.php, fpdf/ vendored. PWA screens.reports: library, generate, Web Share API. |
| OS Lockdown (apt-mark hold + pre-upgrade hook) | `[x]` **DONE 2026-03-26 S2** — os_lockdown.py, delivered via setup_lockdown cloud_agent command (DEP7 option b). |

### 8.2 — App ↔ Website API Integration (app-side JavaScript)
**Note:** All website PHP endpoints listed here were built in v0.9.3 S5 and are on staging. The app-side calls (this section) are entirely unbuilt — this is the missing connection.

| # | App feature | Calls | What it does | Status |
|---|------------|-------|--------------|--------|
| AW1 | First install — device registration | `POST register-device.php` | Generates device UUID, stores on HostPapa, links to install | `[x]` **NOT A PWA ITEM** — register-device.php is called by the Pi automatically on first boot after QR scan. App does not call it. Handled by cloud_agent.py pair_confirmed handler (S18). Confirmed 2026-04-11. |
| AW2 | QR pairing — link device to account + vessel | `POST pair-device.php` | User scans QR on Pi → app sends UUID + user token + vessel name/type → account linked. T3: can pair multiple Pis. | `[x]` **DONE 2026-03-26 S3** — screens.pair: camera → jsQR → vessel form → pair-device-app.php. New endpoint uses app_token auth. |
| AW3 | Fix My Pi — trigger diagnostic | `POST fix-my-pi-billing.php` → Stripe → `POST command-queue.php` | Charges $29.99, writes `fix_my_pi` command for the active Pi | `[x]` **DONE 2026-03-27 S4** — fix-my-pi-app.php (app_token auth): T0 blocked, T1 Stripe checkout + post-payment poll, T2 allowance check, T3 direct queue. PWA screens.fixmypi: disclaimer→progress→result. Stripe webhook updated for pi_installation_id. |
| AW4 | Send command to Pi | `POST command-queue.php` | App writes command for the active Pi (restart_service, ota_update, reboot) | `[x]` **DONE 2026-03-26 S3** — app-command.php POST. Verifies Pi paired to user. Returns command_id. |
| AW5 | Poll command result | `GET command-queue.php?id=<id>` | App checks if Pi has completed the command; shows status | `[x]` **DONE 2026-03-26 S3** — app-command.php GET `?command_id=`. OTA button polls every 10s, 20min timeout. |
| AW6 | Request PDF report | `POST pdf-engine-report.php` | App triggers Gemini-powered PDF engine health report; returns download URL, stores in library | `[x]` **DONE 2026-03-27 S6** — all tiers, no cap. PWA: generate button, library list, Web Share API. |
| AW7 | Read boat health dashboard data | `GET dashboard-data.php` | `[x]` **DONE 2026-03-26 S2** — endpoint built + deployed to staging. PWA app.js calls it. |
| AW8 | Find My Boat | `GET dashboard-data.php` position fields | `[x]` **DONE 2026-03-26 S2** — dashboard-data.php returns position. PWA shows on Google Maps link. |
| AW9 | User authentication | Bearer app_token UUID via user-login.php + auth.php | `[x]` **DONE 2026-03-26 S2** — token stored in localStorage. |

### 8.3 — Multi-Boat: Boat Selector (app-side, T3)
**Depends on:** v0.9.3 S6 schema fix (vessel_name, is_primary columns in d3kos_pairings)

| # | Item | Detail | Status |
|---|------|--------|--------|
| MB1 | Fetch paired vessels list | `GET list-vessels.php` | `[x]` **DONE 2026-03-26 S2** — endpoint built + deployed. |
| MB2 | Boat selector screen | Cards per vessel, online indicator, tap to select | `[x]` **DONE 2026-03-26 S2** — built in PWA app.js select-vessel screen. |
| MB3 | Active boat state | pi_installation_id in localStorage | `[x]` **DONE 2026-03-26 S2** — state.vessel + localStorage in PWA. |
| MB4 | Boat switcher in app nav | Persistent control in header/nav showing current vessel name. Tap → returns to boat selector screen. | `[x]` **DONE 2026-03-27** — header-vessel span becomes tappable with › indicator + keyboard support when >1 vessel. Single-vessel accounts: no change. |
| MB5 | Primary boat default | On app open with >1 vessel: auto-select the `is_primary` vessel. User can change primary in app settings. | `[x]` **DONE 2026-03-26 S3** — loadVessels() prefers is_primary vessel, falls back to vessels[0]. |
| MB6 | Single-boat shortcut | If account has exactly 1 paired Pi: skip boat selector entirely, go straight to dashboard. | `[x]` **DONE 2026-03-26 S2** — already in app.js (vessels.length === 1 auto-selects). Item was stale. |
| MB7 | Vessel name displayed on QR pairing | During QR scan flow: prompt "Name this vessel" + vessel type dropdown before completing pairing | `[x]` **DONE 2026-03-26 S3** — Phase 2 of screens.pair: vessel name input + type select before POST. |

### 8.4 — Tier Service on Pi (port 8093)
**Belongs in v0.9.4 build. Pi nginx already routes `/tier/` to port 8093 but no service exists. Pi dashboard and Settings call `/tier/status` to decide which features to show. Feature gating on the Pi is broken without this.**

| # | Item | Status |
|---|------|--------|
| TS1 | Build tier service Python script on Pi (port 8093) | `[x]` **DONE 2026-03-26 S2** |
| TS2 | Register as systemd service (d3kos-tier.service) — starts on boot, restarts on crash | `[x]` **DONE 2026-03-26 S2** |
| TS5 | `/tier/feature/<name>` route + `camera` feature flag — camera stream service ExecStartPre calls this endpoint; missing route caused 131 alerts from crash loop | `[x]` **DONE 2026-03-27 S6c** |
| TS6 | `voice_assistant` feature key added to FEATURE_MATRIX — ExecStartPre for d3kos-voice.service checks `/tier/feature/voice_assistant`; was returning "unknown feature" → service crash. Added: T0=False, T1/T2/T3=True. Also disabled and masked `d3kos-tier-api.service` (old duplicate conflicting on port 8093). | `[x]` **DONE 2026-03-28 S8** |
| TS3 | Upgrade prompt in app — locked features show "Upgrade to [tier] to unlock" with link to `/upgrade` page on atmyboat.com | `[x]` **DONE 2026-03-27** — Settings screen shows locked feature cards (PDF Reports T2+, SMS Alerts T2+, Multiple Phones T2+, Fleet Management T3) with upgrade CTA linking to atmyboat.com/upgrade. |
| TS4 | Chart Room locked sections — PDF Reports, Analytics, Fleet Map shown as locked cards with upgrade CTA for users below required tier | `[x]` **DONE 2026-03-27** — Implemented as locked-features-section in PWA settings. T1 sees 4 locked cards. T2 sees Fleet Management only. T3 sees nothing. |

### 8.5 — Deployment Solutions (all required before v0.9.4 ships)


| # | Item | Status |
|---|------|--------|
| DEP1 | **OTA download source** — archive.org confirmed. Services zip (not full disk image). URL: `https://archive.org/download/d-3k-os-v-0.9.2/d3kos-v0.9.2.2-services.zip` | `[x]` **DONE 2026-03-27** — zip built (0.44MB), SHA-256 set in version-registry.php. Don uploads zip to archive.org item `d-3k-os-v-0.9.2`. |
| DEP2 | Pi upgrade script (ota_upgrade.py) | `[x]` **DONE 2026-03-26 S2** — download, SHA-256 verify, backup, install, rollback. SHA-256 field in version-registry.php must be populated before first OTA. |
| DEP3 | **Fix My Pi file manifest** — generate a SHA-256 manifest of every file in a clean d3kOS installation. Host on HostPapa. Fix My Pi compares Pi files against it. Must be regenerated for every new d3kOS release. | `[x]` **COMPLETE 2026-04-01 S9** — file-manifest.php deployed (11 files, SHA-256+size). check_file_integrity() in fix_my_pi.py. Verified: correctly detected 2 real mismatches on Don's phone. Hashes must be regenerated after any Pi service file change. |
| DEP4 | **SQL-before-PHP deploy gate** — add hard gate to v0.9.4.1 deploy checklist: run S6 MySQL ALTER TABLE statements via phpMyAdmin BEFORE deploying any new PHP files. If PHP deploys first and ALTERs haven't run, multi-boat writes will fail silently. | `[x]` **COMPLETE 2026-04-06 S17c** — Gate documented in CREDENTIAL_VAULT.md Pre-Launch Checklist. Rule: SQL schema changes always precede PHP deploys. |
| DEP8 | **S6 schema: run in phpMyAdmin** — CREATE TABLE `amboat_rtc_sessions` + `amboat_pdf_reports` (SQL delivered in S6 chat). PHP files already deployed, will 500 until tables exist. | `[x]` **DONE 2026-03-27** — both tables created, confirmed by operator |
| DEP9 | **Create `staging/app/reports/` directory on HostPapa** — pdf-engine-report.php saves PDFs there. Needs to exist with write permissions (755). Use cPanel File Manager → staging/app/ → New Folder. | `[x]` **DONE 2026-03-27** — directory created by operator |
| DEP10 | **TURN server** — relay for WebRTC when STUN P2P fails (carrier-grade NAT). | `[x]` **DONE 2026-03-27 S6c** — Metered.ca TURN (a.relay.metered.ca:3478). Pi: aioice timeout patch 5s→12s, live_session.py uses correct relay hostname. App: turn-credentials.php returns correct ICE servers. Relay confirmed: `178.156.179.144` (Metered.ca). Cellular test passed. |
| DEP13 | **Pi AODA compliance pass — MANDATORY** — WCAG 2.0 AA applied to all 20 static HTML pages (`/var/www/html/`) and 12 Flask templates. Skip-to-content links, id="main-content", focus-visible indicators, font-size floor 18px, min-height 48px touch targets. CSS appended to both `d3kos-touch.css` and `d3kos.css`. | `[~]` S8 static pages done. S50 Flask attempt FAILED AND REVERTED. **S51 PLAN COMPLETE — awaiting Don's go-ahead.** Track A: contrast overrides ~50 selectors (no token changes). Track B: skip links, h2, aria-labels on all 13 templates. Track C: font size floor 45–70yr users. Required — commercial software, accessibility law. |
| DEP17 | **Pi display config — two-instance + title bar color** | Two Chromium instances launched on every boot: `launch-d3kos.sh` (labwc autostart, waits for Flask) AND `d3kos-browser.desktop` (lxsession-xdg-autostart). Title bar text black — labwc themerc-override controls title bar color, not Chromium theme-color meta tag. | `[~]` **S55b 2026-04-12 PARTIAL** — Two-instance fixed: `launch-d3kos.sh` now `--app=http://localhost/` (nginx); `d3kos-browser.desktop` disabled (Hidden=true). **OPEN: title bar text still black.** Fix: `window.active.label.text.color: #ffffff` in `/home/d3kos/.config/labwc/themerc-override`. Deferred. |
| DEP14 | **Settings & Help section index bar** — 17 pill buttons in sticky nav at top of Flask settings.html page. IntersectionObserver highlights active section on scroll. Tap scrolls `.settings-page-body` container directly. Pill colours: active = green outline + green text, default = white text transparent. | `[x]` **DONE 2026-03-28 S8** |
| DEP15 | **Status bar indicators removed** — `<div class="indicators">` block (🌐🗺🤖📡🧠 icons beside clock) removed from Flask settings.html. | `[x]` **DONE 2026-03-28 S8** |
| DEP16 | **Alert clear/dismiss in PWA** — `clear-alerts.php` (HostPapa, Bearer auth) + app.js alerts screen: "🗑 Clear All" button + per-row ✕ dismiss with fade animation. Both deployed to staging. Don must clear 212 stale tier-api alerts via phpMyAdmin first. | `[x]` **DONE 2026-03-28 S8** — **Don action required: phpMyAdmin DELETE** |
| DEP5 | **T3 multi-Pi OTA** — add "Update all vessels" to app UX. Queues one `ota_update` command per paired Pi. App shows per-Pi progress bars simultaneously. | `[x]` **COMPLETE 2026-04-01 S9** — "Update All Vessels" block in app.js; T3 only, 2+ vessels required; per-Pi progress. |
| DEP11 | **Brand asset audit — logo consistency across all surfaces** | Verify the same canonical AtMyBoat logo is used on: (1) PWA manifest icons (192px + 512px), (2) PWA splash/header, (3) d3kOS Pi dashboard header, (4) AtMyBoat.com WordPress child theme `images/amboat-logo.png`, (5) Pi boot splash screen (item 22 in Part 6). Single source file. No surface uses an older or different variant. | `[x]` **COMPLETE 2026-04-02 S15** — Pi dashboard header changed from text to amboat-logo.png image. Boot splash uses same logo. PWA icons regenerated from same source. All 5 surfaces confirmed consistent. |
| DEP12 | **Pi boot splash — branded d3kOS screen** | Implement at Pi level: AtMyBoat logo + d3kOS version + © AtMyBoat.com. See Part 6 item 22. | `[x]` **COMPLETE 2026-04-02 S15** — See item 22 above. Plymouth theme deployed. |
| DEP17 | **Pi service watchdog cron** — `d3kos_watchdog.py` monitors 10 critical services, auto-restarts, POSTs to HostPapa watchdog-alert.php on persistent failure — wp_mail() emails registered account holder. No SMTP on Pi. | `[x]` **COMPLETE 2026-04-01 S9b** — Option B (cloud-routed). No operator action required — email from WP account automatically. |
| DEP18 | **PWA app back chevron** — phone back button exits PWA entirely. Need in-app `←` in screen header for sub-screens. | `[x]` **COMPLETE 2026-04-01 S10** — `backButton()` helper function + `←` chevron added to 4 sub-screens: Live (back to dashboard), Reports (back to dashboard), Media (back to live screen), Fix My Pi (back to dashboard). Commit `ee01765`. |
| DEP19 | **file-manifest.php auto-update** — hashes currently updated manually. Add to Pi deploy script so manifest is regenerated automatically on every firmware deploy. | `[x]` **COMPLETE 2026-04-02 S15** — `deployment/scripts/generate_manifest.py` created. Maps 11 Pi service files → local repo paths. Computes SHA-256 + size, regenerates file-manifest.php. Run after every Pi service file change. Manifest regenerated 2026-04-02T18:30:40Z. |
| DEP6 | **PWA version enforcement** — app calls `version-registry.php` on launch, compares to running service worker version. Shows "Update available — tap to refresh" banner if stale. Prevents users running old app against new Pi firmware. | `[x]` **DONE 2026-03-26 S3** — versionLessThan() helper + LATEST_D3KOS constant. Green banner on dashboard if vessel Pi firmware is behind. No extra API call — uses d3kos_version from dashboard-data response. Update LATEST_D3KOS constant each release. |
| DEP7 | OS Lockdown delivery path | `[x]` **DONE 2026-03-26 S2** — Option b: setup_lockdown command via command queue. |
| DEP20 | **Dual dashboard source-of-truth risk** — `deployment/d3kOS/dashboard/` and `deployment/v0.9.4/pi_source/` are two separate directories. New pages added to v0.9.4/pi_source/ (S39b manual, S41 anchor-watch) were never synced to d3kOS/dashboard/. S52 reconciled index.html, app.py, manual.html. Other files may still differ. Any new page must be added to BOTH directories and confirmed in the Pi deploy list. | `[!]` **OPEN — S52 2026-04-11** — partial sync done. Full audit of both directories needed. |

---

## PART 8A — v0.9.4.1 Pi ↔ Website ↔ App Integration
**Status: CODE COMPLETE S36 2026-04-08 — Blocked on Phase 4 live push only.**
**Definition:** v0.9.4.1 completes the full data pipeline: Pi exports reach the real website endpoint, community API endpoints live on staging, the Chart Room PDF section reads from the DB, and the community map Leaflet is fully wired.
**Depends on:** Phase 4 live push for public availability. All code deployed to staging.

### 8A.1 — Pi Side: Connect Export Worker to Real Endpoint

| # | Item | File | Status |
|---|------|------|--------|
| P1 | Update `export_worker.py` URL from placeholder to real endpoint | `services/export/export_worker.py` line 30 — `d3kos-cloud-api.example.com` → `https://atmyboat.com/mobile/data-ingress.php` | `[x]` **COMPLETE 2026-03-26 S1** |
| P2 | Fix auth headers in `export_worker.py` — current: `Bearer <installation_id>` wrong. Needs: `Authorization: Bearer <API_KEY>` + `X-Device-Token: <device_uuid>` to match `data-ingress.php` auth.php | `services/export/export_worker.py` | `[x]` **COMPLETE 2026-03-26 S1** |
| P2.5 | **cloud_agent.py command consumer** — new service polls `command-queue.php` every 30s, executes ping/export_now/tier_change. d3kos-cloud-agent.service installed + enabled on Pi. | `services/cloud-agent/cloud_agent.py` | `[x]` **COMPLETE 2026-03-26 S1** |
| P3 | Add command pickup loop — `data-ingress.php` returns `pending_commands` array in response body. Pi must read and execute each command. | Handled by `cloud_agent.py` (polls separately) — `export_worker.py` not changed | `[x]` **COMPLETE via cloud_agent.py 2026-03-26 S1** |
| P4 | Alert-triggered export | `[x]` **DONE 2026-03-26 S2** — alert_watcher.py polls issues.db, triggers immediate export on critical/priority alerts. Service running. |
| P5 | Create `/opt/d3kos/config/cloud-config.json` with AtMyBoat.com API key. Template in repo (placeholder). | Pi config | `[x]` **COMPLETE 2026-03-26 S1** — `cloud-config.json` created, key written directly to Pi |
| P6 | Pi reads tier from sync response, updates license.json | `[x]` **DONE 2026-03-26 S2** — export_worker.py _sync_tier_from_response() |
| P7 | **T0 → T1 upgrade path** — when `pair-device.php` confirms pairing, response includes `"tier": "T1"`. Pi reads it and upgrades `license.json` from tier 0 to tier 1. Enables export and cloud sync for the first time. | `services/cloud-agent/cloud_agent.py` | `[x]` **COMPLETE 2026-04-06 S18** — `handle_pair_confirmed()` added to cloud_agent.py. Writes string tier (e.g. "T1") to license.json. Triggers immediate export (best-effort). TDD: 3/3 assertions passed on Pi. Service restarted and active. |

### 8A.2 — Pi Side: Node-RED Community Flows

**S36 FINDING: Node-RED community flows do not exist.** Build plan stated "built but disabled" — investigation of flows.json confirmed only system/Signal K flows present (49 nodes, 1 tab). The community flows were never built.

**These flows are NOT needed for the community map to work.** The existing export_worker.py → data-ingress.php pipeline already writes position data to wpax_usermeta. community-get.php reads from that. Fleet dots work via this path today.

`community-position.php` (Pi-direct UPSERT endpoint) is deployed on staging for future use if real-time sub-30min position updates are desired.

| # | Item | Status |
|---|------|--------|
| N1 | Node-RED "Post to Community DB" URL wiring | `[–]` **SUPERSEDED** — flows don't exist; existing export pipeline covers this |
| N2 | Wire API key into Node-RED HTTP nodes | `[–]` **SUPERSEDED** — same reason |
| N3 | Enable 3 Node-RED flows | `[–]` **SUPERSEDED** — flows don't exist |
| N4 | End-to-end test: community sharing ON → community map shows dot | `[ ]` Testable on staging now — enable map_sharing in usermeta, wait for next Pi sync |

### 8A.3 — Website Side: Community API Endpoints

| # | Item | Endpoint | Status |
|---|------|----------|--------|
| W1 | Build `POST /api/community/markers` endpoint — receives hazard markers, stores in amboat_community_markers | `[x]` **COMPLETE S36 2026-04-08** — `community-markers-write.php` deployed to staging. Dual auth (app_token or AMBOAT_API_KEY). Rate limited 20/device/24h. |
| W2 | Build `GET /api/community/markers` endpoint — returns markers for community map | `[x]` **COMPLETE S36 2026-04-08** — `community-get.php` deployed. Returns positions + markers + fleet_count in one call. |
| W3 | Build `POST /api/telemetry/push` endpoint — Node-RED telemetry | `[–]` **SUPERSEDED** — Node-RED flows don't exist. Deferred. |
| W4 | Build `POST /api/community/benchmark` endpoint — Node-RED benchmark | `[–]` **SUPERSEDED** — Node-RED flows don't exist. Deferred. |
| W5 | Build `POST /api/community/position` endpoint — Pi-direct position UPSERT | `[x]` **COMPLETE S36 2026-04-08** — `community-position.php` deployed to staging. Pi-facing auth. UPSERT one row per device_token. |
| W6 | Community map coordinates privacy blur — 2 decimal places on output | `[x]` **COMPLETE S36 2026-04-08** — `community-get.php` uses ROUND(lat,2) and ROUND(lon,2) on all query output. |

### 8A.4 — Website Side: Display Synced Pi Data + Multi-Boat Endpoints

**Note:** All queries in D1–D4 must filter by `pi_installation_id`, not just `user_id`. Without this, T3 multi-boat data is mixed together.

| # | Item | Page / Endpoint | Status |
|---|------|-----------------|--------|
| D1 | Chart Room — last sync time, d3kOS version, engine snapshot | `/dashboard` | `[x]` **Already existed** — page-dashboard.php reads usermeta (last_sync, last_rpm, coolant_temp, d3kos_version) written by data-ingress.php. Working. |
| D2 | Find My Boat — last known GPS + timestamp, T1+ only | `/dashboard` | `[x]` **Already existed** — page-dashboard.php reads atmyboat_position_lat/lng from usermeta. Working. |
| D3 | Alert history — last 20 alerts | `/dashboard` | `[x]` **Already existed** — page-dashboard.php reads atmyboat_fmp_history from usermeta. Working. |
| D4 | PDF report download list — T2/T3 only | `/dashboard` (T2/T3 only) | `[x]` **WORKING AS DESIGNED** — reads `atmyboat_pdf_reports` usermeta, written by `mobile/pdf-report.php` (server-side Gemini reports). Appears empty until first report is generated — not a bug. S36 investigation confirmed original code was correct; attempted fix was reverted. |
| D5 | Build `dashboard-data.php` — engine + position + alerts + sync time | `[x]` **DONE 2026-03-26 S2** — built + deployed to staging. |
| D6 | Build `list-vessels.php` — all paired Pis for authenticated account | `[x]` **DONE 2026-03-26 S2** — built + deployed to staging. |

### 8A.5 — App Side: Command Queue Integration

| # | Item | Status |
|---|------|--------|
| A1 | App writes command to `command-queue.php` (e.g. `fix_my_pi`, `ota_update`, `restart_service`) | `[ ]` Depends on PWA build (v0.9.4) |
| A2 | Pi's command pickup loop (P3 above) executes commands and POSTs result back to `command-queue.php` | `[ ]` Depends on P3 |
| A3 | App polls `command-queue.php` for command result — shows status to user | `[ ]` Depends on PWA build |

### 8A.6 — Integration Test Plan

| # | Test | Expected result | Status |
|---|------|-----------------|--------|
| T1 | Pi sync → website: POST to data-ingress.php with real API key | 200 OK, engine snapshot row in DB, last_sync updated | `[ ]` |
| T2 | Command round-trip: app queues `restart_service` → Pi picks up on next sync → executes → result returned | App shows "completed" within 35 minutes | `[ ]` |
| T3 | Community data flow: enable boat_map in Settings → next Node-RED tick → position appears on /community map | Dot appears within 30 minutes of enabling | `[ ]` |
| T4 | Alert trigger: simulate anchor drag → immediate export fires (not wait for timer) → alert in DB | Alert in `amboat_alerts` within 2 minutes | `[ ]` |
| T5 | Find My Boat: Pi syncs position → Chart Room shows marker at correct location | Position on map within 35 minutes of sync | `[ ]` |
| T6 | PDF report: T2 user requests engine report → Gemini called → PDF generated → download link returned | PDF available within 30 seconds | `[x]` **COMPLETE 2026-04-01 S11.** Architecture pivoted from server-side FPDF to client-side jsPDF. Phone generates PDF in-browser via jsPDF (loaded from CDN), uploads base64 binary to pdf-store.php for permanent server storage. Gemini analysis via new pdf-analyze.php endpoint. window.open() trap replaced with navigator.share() + Blob fetch. Confirmed: vessel "Our Time" generated RPT-20260401-NZ222B, shared via system share sheet. list-reports.php fixed (removed file_size_kb from SELECT — column does not exist on staging). sw.js bumped to v7 (v6 broken — CDN URL in STATIC_ASSETS blocked SW install). |

---

## PART 8B — v0.9.5 Predictive Maintenance
**Status: COMPLETE — S21 2026-04-07 — All phases done. On-water validation pending.**
**Dependency updated:** Does NOT require v0.9.4.1. Engine historian stores locally on Pi. Cloud sync of predictions is bonus, not required.
**Reference:** `doc/D3KOS_VERSION_ROADMAP_2026.md` § v0.10.0

### Build Phases
| Phase | Scope | Status |
|-------|-------|--------|
| Phase 1 | Engine historian service + SQLite schema + test data generator | `[x]` DONE S19/S20 |
| Phase 2 | Statistical baseline (2σ) + anomaly detector + alert integration | `[x]` DONE S19/S20 |
| Phase 3 | Dashboard widget + voice alert (T2+) + boatlog auto-entry | `[x]` DONE S20 |
| Phase 4 | ML model inference infrastructure (training deferred to on-water data) | `[ ]` Deferred — needs on-water data |
| Phase 5 | Advanced: fuel optimization, maintenance scheduling, geofence (T3) | `[ ]` Deferred — T3 feature |

### Test Data Validation (operator-approved approach 2026-04-07)
Before any on-water testing, validate with synthetic known data:
- 2,000 readings over 30 synthetic days (normal baseline)
- Inject 3 anomalies at known timestamps: coolant spike Day 15, oil pressure drop Day 22, RPM variance Day 27
- Pass criteria: each alert fires within 1 detection cycle; no false positives on normal data
- **S21 2026-04-07: Test data CLEARED from production DB** — 2,000 rows deleted. 131 signalk production rows remain. On-water data will build from here.

| # | Item | Detail | Status |
|---|------|--------|--------|
| PM1 | Predictive maintenance service (Port 8106) | Flask service, SQLite engine historian, historian thread + detector thread, 5-min detection cycle | `[x]` DONE S19 |
| PM2 | 30-day baseline data collection | Test data approach: generate_test_data.py (2000 rows, 3 anomalies). On-water data will replace. TDD 6/6 passed S19. | `[x]` DONE S19 |
| PM3 | Statistical anomaly detection | 2σ z-score + HARD_LIMITS (coolant >100°C ALERT, oil <150 kPa ALERT). WATCH/ALERT/OK per field. | `[x]` DONE S19 |
| PM4 | ML models — 5 targets | Overheating predictor (LSTM autoencoder), oil pressure failure, battery failure, SD card failure, GPS failure | `[ ]` Deferred — needs on-water training data |
| PM5 | Alert system integration | AI bridge webhook → TTS (Piper) + SSE ticker. Direct Piper fallback. Boatlog auto-entry. | `[x]` DONE S20. S21 fix: Piper timeout removed, mute persistence added, test DB cleared. |
| PM6 | Dashboard widget | Engine Monitor page: Predictive Health section (4 eng-cell cards). Ticker via AI bridge SSE. No new UI on main dashboard. | `[x]` DONE S20 |
| PM7 | Additional automation | Weather-triggered storm warnings. Fuel optimization. Maintenance scheduling. Geofence alerts (T3). | `[ ]` Deferred — T3/Phase 5 |
| PM8 | Boatlog integration | Auto-entry on WATCH/ALERT via write_boatlog() with 1hr cooldown dedup | `[x]` DONE S19 |

**Deliverable:** d3kOS v0.9.5 — predictive maintenance with 24h advance failure warnings

---

## PART 8C — v0.9.6 Fleet Management
**Status: PHASE 1 COMPLETE — 2026-04-07 S21c** (backend + Pi deploy + live push verified)
**Strategy:** Build and test entirely on staging. v0.9.4.1 multi-boat pipeline absorbed into Phase 1 (no separate version).
**Depends on:** Nothing blocking — staging-first approach removes Phase 4 live push as a gate.
**Reference:** `deployment/features/fleet-management/BUILD_CHECKLIST.md` (created S21)

### Phases
| Phase | Scope | Status |
|-------|-------|--------|
| Phase 1 | Pi data push + HostPapa fleet endpoints (absorbs v0.9.4.1) | `[x]` **COMPLETE — 17/17 tests + live push confirmed 2026-04-07 S21c** |
| Phase 2 | PWA fleet screen — map + health cards | `[x]` **COMPLETE S22/S23** — Leaflet map + vessel list + join/create + status/leave + Pi fleet_assign command |
| Phase 3 | Analytics — engine hours, fuel, alert history per vessel | `[x]` **COMPLETE S27b** — fleet-analytics.php alerts_30d per vessel + fleet_alerts_30d summary; app.js alert breakdown + CSV export. Deployed + endpoint verified. |
| Phase 4 | Tier 3 gate + admin console fleet view | `[~]` **IN PROGRESS** — Tier gate verified S27b (T1 gets 403 on all fleet endpoints, T3 passes). Admin CRM fleet view done S24. PWA locked card done S23. Two-device hardware test still pending. |

### Items
| # | Item | Detail | Status |
|---|------|--------|--------|
| FM0 | Pi fleet data push service | Port 8108, 1-min push when engine_on OR GPS fix, idles otherwise, T3 gate, reads fleet.json | `[x]` **DONE S21c** — active on Pi, live push confirmed |
| FM1 | Fleet creation + invitation system | fleet_code (6-char), charter/fishing/marina/other, roles: owner/member/view, 15-vessel cap | `[x]` **DONE S21b** — fleet-create.php, fleet-join.php deployed + tested |
| FM2 | Fleet map | fleet-map.php: last-known position per vessel, age_minutes, role. Leaflet.js PWA screen TBD | `[~]` Backend done (15-vessel e2e ✓), PWA screen not started |
| FM3 | Fleet analytics | fleet-analytics.php: engine_hours, avg RPM/coolant/oil (24h), fleet summary + alerts_30d per vessel | `[x]` **DONE S27b** — backend + PWA analytics screen complete. Alert history per vessel deployed. Endpoint verified (vessel_count=15, alerts_30d present). |
| FM4 | HostPapa PHP endpoints | fleet-create/join/ingest/map/analytics.php + fleet-setup.php — all deployed to staging | `[x]` **DONE S21b — ALL 17 TESTS PASSED** |
| FM4b | fleet-status.php + fleet-leave.php | fleet-status: GET membership; fleet-leave: owner deletes/member removes self | `[x]` **DONE S23** — deployed to staging, confirmed working |
| FM5 | PWA fleet screen | Fleet tab (T3), Leaflet map (colored markers), vessel list (health cards), join/create/status/leave flow | `[x]` **DONE S22/S23** — all flows confirmed by Don |
| FM5b | Pi fleet_assign command | fleet_assign/fleet_unassign handlers in cloud_agent.py; enqueued by fleet PHP; Pi writes fleet.json automatically | `[x]` **DONE S23** — deployed to Pi, sudoers updated |
| FM6 | Tier 3 activation gate | Backend T3 gate verified (401 on bad token). PWA locked card DONE S23. Admin CRM fleet view DONE S24. | `[~]` T1 gets 403 "Fleet management requires Tier 3" on create/join/map/analytics — confirmed S27b. T3 passes all endpoints. Two-device hardware test still pending. |
| FM7 | Admin CRM fleet view | Flask routes /fleets + /fleet/<id> + /fleet/<id>/suspend. fleet.html list+detail. suspended column added. | `[x]` **DONE S24** — VM deployed, verified end-to-end |

**Deliverable:** d3kOS v0.9.6 — fleet management for Tier 3 operators (charter, fishing guide, marina)

---

## PART 8D — v0.9.7 Remote Diagnostic Console
**Status: PHASES 1+2+3+4 COMPLETE (S25–S27 2026-04-07) — PENDING HARDWARE UAT**
**Depends on:** v0.9.4 (PWA + Pi command queue), v0.9.3 live push
**Reference:** `doc/D3KOS_VERSION_ROADMAP_2026.md` § v0.11.0

| # | Item | Detail | Status |
|---|------|--------|--------|
| RD1 | Support ticket system | User submits ticket (problem description) from PWA. Admin receives notification within 60 seconds. Ticket tracking and status updates. | `[x]` Phase 1 complete S25 |
| RD2 | Diagnostic consent flow | Per-session approval required from user. Time-limited access (2 hours max). Auto-expiry after session. | `[x]` Phase 2 complete S26 — diagnostic-consent.php, -status.php, -revoke.php, PWA consent UI |
| RD3 | Diagnostic agent on Pi (Port 8109) | Controlled log collection. Bundle creation (<60 seconds). Upload to AtMyBoat.com. | `[x]` Phase 2 complete S26 — diagnostic_agent.py, cloud_agent diagnostic_collect handler. Bundle confirmed 105KB |
| RD4 | AI diagnosis engine | Gemini 2.5 Flash via ai_client.py (admin console only). Log analysis and diagnosis. Fix recommendations. | `[x]` Phase 3 complete S26 — diagnose_pi(), /ticket/<id>/diagnose route. Diagnosis stored: SignalK 404, confidence 90% |
| RD5 | Fix delivery system | Admin creates fix (AI or manual). Fix execution via whitelisted command queue. | `[x]` Phase 4 complete S26 — diagnostic-fix.php whitelist enforced, cloud_agent handle_diagnostic_fix, /ticket/<id>/send-fix route. User approval deferred. |
| RD6 | Knowledge base | Resolved cases logged. Pattern detection (3+ matches → auto-rule). Recurrence tracking. | `[x]` Phase 4 complete S26 — diagnostic-resolve.php, diagnostic-past-cases.php, KB panel in CRM |
| RD7 | Admin console UI | Full 3-panel layout: diagnostic bundle + AI diagnosis + send fix + resolve + knowledge base. | `[x]` Phase 3+4 complete S26 — tickets.html 5 panels, all JS wired |

**Deliverable:** d3kOS v0.9.7 — remote diagnostic console for operator support

---

## PART 8E — v0.9.8 Autonomous Agents + Failure Intelligence
**Status: S34 DEPLOYED + VERIFIED — fleet version dashboard live, Pi heartbeat confirmed working. FI4 deferred.**
**Depends on:** v0.9.7 (action layer + whitelisted command queue)
**Reference:** `doc/D3KOS_VERSION_ROADMAP_2026.md` § v0.12.0 + v0.13.0

### 8E.1 — Autonomous Agents

| # | Item | Detail | Status |
|---|------|--------|--------|
| AA1 | Agent framework | Base agent class, scheduler, SQLite state, atomic JSON, 5-min poll loop. | `[x]` S28 deployed + verified |
| AA2 | Update agent | DB-backed version manifest, T1+ auto-apply with rollback, FI1/FI2 integration. | `[x]` S29+S31+S32 |
| AA3 | Performance agent | CPU/mem/disk/thermal. Pi-tuned thresholds (SwiftShader). /tmp cleanup at disk crit. | `[x]` S28 deployed + verified |
| AA4 | Storage agent | Log trimming, old backup cleanup, predictive disk warning (7-day). | `[x]` S29 |
| AA5 | Health check agent | Health score 0-100, 12-service check, weekly DB integrity deep scan. | `[x]` S30 |
| AA6 | Backup agent | USB incremental/full rsync, T3 cloud sync stub (config-package.php not yet built). | `[x]` S30 |

### 8E.2 — Failure Intelligence & Recovery

| # | Item | Detail | Status |
|---|------|--------|--------|
| FI1 | Failure reporter (Port 8109) | Flask service, SQLite, error signature normalisation, background FI2 sync. Any service calls POST /report. | `[x]` S31 deployed Pi:8109 |
| FI2 | Issue lifecycle DB at HostPapa | failure-report.php + fix-confirmed.php + issue-api.php. amboat_issues + amboat_failure_reports + amboat_issue_resolutions tables. | `[x]` S31 deployed |
| FI2b | Update Publisher | version.php DB-backed (amboat_versions). update-publish.php CRM API. package-update.py local packager. CRM /publish-update page. | `[x]` S32 deployed |
| FI2c | Version heartbeat | AA2 reports current_version to HostPapa on every run. amboat_devices.current_version. CRM fleet version view. | `[x]` S33 — version-heartbeat.php + version-api.php + fleet_versions.html |
| FI3 | Admin CRM issue dashboard | /failures list + /failure/<id> detail. Lifecycle: open→diagnosed→fix_validated→released→closed. Progress bars. | `[x]` S31 deployed CRM |
| FI4 | Recovery mode boot sequence | Fresh SD card detection. Download config packages. Restore settings + boatlog. | `[x]` **COMPLETE S55 2026-04-12** — Phase 1 (HostPapa backend), Phase 2 (cloud_agent push), Phase 3 (setup wizard recovery mode), Phase 4 (Pi settings Recovery Key display). T2/T3 multi-boat: config-backup-status.php + CRM /backup-status + PWA Recovery Key card + Pi GET /api/recovery-key. |

### 8E.3 — DevOps Release Workflow (new — confirmed S31+S32)
Full lifecycle: bug detected (FI1) → clustered (FI2) → fixed on one Pi (validated) → packaged (`package-update.py`) → uploaded to HostPapa `updates/` → published via CRM `/publish-update` → all T1+ Pis auto-apply within 24h → fleet resolution tracked in FI3.

**Deliverable:** d3kOS v0.9.8 — autonomous agents + failure intelligence

---

## PART 8F — v0.9.9 Security Audit & Penetration Testing
**Status: NOT STARTED — REQUIRED before v1.0 launch**
**Reference:** `doc/D3KOS_VERSION_ROADMAP_2026.md` § v0.16.0

| # | Item | Detail | Status |
|---|------|--------|--------|
| SA1 | Automated scanning | Hardcoded credentials scan + secrets audit across all PHP files. | `[x]` **COMPLETE S34 2026-04-08** — Production DB password removed from git history. All DB credentials + ADMIN_API_KEY centralised in config.php. Pre-commit hook active. |
| SA2 | Manual code review — SQL injection | All `real_escape_string()` replaced with `prepare()`+`bind_param()`. Zero string-concatenated SQL remaining. | `[x]` **COMPLETE S35 2026-04-08** — 4 files fixed: failure-report.php, fix-confirmed.php, issue-api.php, update-publish.php + diagnostic-upload.php. All 29 endpoints use parameterised queries. |
| SA3 | Secrets management review | All API key comparisons use `hash_equals()` (timing-safe). Auth coverage: 100% of endpoints authenticated. No XSS vectors (JSON-only output). | `[x]` **COMPLETE S35 2026-04-08** — 11 files patched. hash_equals() applied to all ADMIN_API_KEY and AMBOAT_API_KEY comparisons. |
| SA4 | External penetration test | Contract professional pen test firm. Network-level attacks, privilege escalation, API fuzzing, rate limiting + DDoS. | `[ ]` **Don to hire firm** |
| SA5 | Fixes | Fix all critical/high vulnerabilities from pen test. Document medium/low with mitigation plans. Retest after fixes. | `[ ]` Blocked on SA4 |
| SA6 | Privacy compliance | GDPR Art.15 (export), Art.17 (erasure), privacy policy published. CCPA covered by same endpoints. | `[x]` **COMPLETE S35 2026-04-08** — data-export.php + data-delete.php deployed. PWA Privacy & Data card in settings. PRIVACY_POLICY_TEMPLATE.md ready for WordPress. Phase 4 checklist updated. |
| SA7 | Certification | Obtain penetration test certificate. Document all cleared findings. | `[ ]` Blocked on SA4 |

**Critical gate — v1.0 blocked until all of these pass:**
- Zero critical vulnerabilities
- Zero high vulnerabilities
- All API endpoints require authentication
- All DB queries use parameterized statements
- No hardcoded secrets
- GDPR/CCPA compliant
- Penetration test certificate obtained

**Deliverable:** d3kOS v0.9.9 — security certified, production ready for v1.0 launch

---

## PART 8G — v0.9.9.1 Admin CRM Tool (Private — VM-based)
**Status: PLANNED — spec complete, build not started**
**Version target:** v0.9.9.1 (after security audit, before public launch)
**Spec:** `deployment/features/admin-crm/SPEC.md`
**Build checklist:** `deployment/features/admin-crm/BUILD_CHECKLIST.md`

**What it is:** Private Flask web app on Ubuntu VM (VirtualBox, workstation).
Complete customer view: tier + billing + Pi health + support emails + AI draft assist.
Completely independent of WordPress — direct MySQL + IMAP connections.

**Pre-build operator actions (completed 2026-04-03 S16):**
- [x] **OP1** — Remote MySQL blocked by HostPapa. PHP proxy (Option B) adopted permanently.
- [x] **OP2** — IMAP/SMTP: mail.atmyboat.com, 993 SSL, 465 SSL. Password reset to 8tm1b08t.$Sk1pp3r.
- [x] **OP3** — Gemini API key confirmed in config.json on VM.
- [x] **OP4** — Staging DB: atmyb197_wp302 / [redacted]. Production: atmyb197_wp59874 / [redacted].

**Build phases:**
| Phase | Feature | Status |
|-------|---------|--------|
| P1 | Foundation — Flask skeleton, login, DB connection | `[x]` **COMPLETE 2026-04-03 S16** — Flask, bcrypt login, 8h session, 5-attempt lockout, config.py, db.py (PHP proxy), dashboard |
| P2 | Customer View — list, search, profile page | `[x]` **COMPLETE 2026-04-03 S16** — Paginated customer list, search, profile with Pi cards, billing, FMP history. Schema fixes applied. |
| P3 | Pi Diagnostics — SSH health, alerts, commands, engine | `[x]` **COMPLETE 2026-04-03 S16** — Alerts + commands via PHP proxy. Live SSH health check deferred (VM→Pi network not confirmed). |
| P4 | Email Inbox — IMAP read, account linking, SMTP reply | `[x]` **COMPLETE 2026-04-03 S16** — IMAP fetch (2min cache), thread view, SMTP reply, mark handled, account auto-link. |
| P5 | AI Draft Assist — Gemini Flash, context builder | `[x]` **COMPLETE 2026-04-03 S16** — Gemini 2.5 Flash, context builder, draft button in thread view. |
| P6 | Tier Management + Audit Log — amboat_admin_log | `[x]` **COMPLETE 2026-04-03 S16** — Tier change + FMP reset + amboat_admin_log audit trail. Table created by Don via phpMyAdmin. |
| P7 | Database Explorer — table browser, CSV export | `[x]` **COMPLETE 2026-04-03 S16** — 8 whitelisted tables, column filter, CSV export. PDO mixed-param bug fixed. |
| P8 | PWA Support Button — structured email from app | `[x]` **COMPLETE 2026-04-03 S16** — Settings → Contact Support → support-request.php. Rate limit 3/24h. Email confirmed received at skipperdon@atmyboat.com. |

**Minimum viable:** P1 + P2 + P6 — foundation + customers + tier management
**Complete picture:** All 8 phases

**AI:** Gemini Flash free tier (zero cost, already configured)
**Migration path:** VirtualBox VM → cloud VM (Hetzner ~$4/month) — same code, config change only

---

## PART 9 — v1.1 Multi-Language Platform
**Status: LAYER 0 COMPLETE — Layers 1–5 not started**
**Full spec:** `doc/MULTILANGUAGE_PLATFORM_SPEC.md` | `deployment/v1.1/`
**Supported languages:** 18 (en, fr, de, es, it, nl, pt, uk, ar, sv, no, da, fi, hr, tr, el, zh, ja)

| Layer | What it covers | Status |
|-------|---------------|--------|
| Layer 0 — UI Foundation | i18n JSON, language API :8101, data-i18n wired on all 13 pages, 38 new keys | `[x]` Complete |
| Layer 0 remaining | Noto fonts for Arabic/CJK/Greek/Cyrillic, Arabic RTL, professional translation review | `[ ]` |
| Layer 1 — Speech-to-Text | Whisper-small (244MB, 99 languages), replaces Vosk post-wake, whisper_transcribe.py | `[ ]` Not started |
| Layer 2 — Text-to-Speech | Per-language Piper models (fr/de/es/it/nl/pt/uk/ar), espeak-ng fallback for others | `[ ]` Not started |
| Layer 3 — AI Response Language | Inject language into Gemini system prompt, i18n rule-based responses | `[ ]` Not started |
| Layer 4 — Keyboard & Text Input | Per-language virtual keyboard layouts, Arabic RTL fcitx5, CJK deferred to v1.1+ | `[ ]` Not started — fix existing keyboard bug first |
| Layer 5 — Boat Log in User's Language | Auto once Layers 1 + 4 done | `[ ]` Not started |

---

## PART 11 — Pi System Stability Fixes (S12 — 2026-04-01)

| Item | Status | Detail |
|------|--------|--------|
| journald persistence enabled | `[x]` **COMPLETE 2026-04-01 S12** | Created `/var/log/journal/<machine-id>/` with correct ownership. Future reboots will be logged. |
| Ollama death loop — gemini_proxy.py | `[x]` **COMPLETE 2026-04-01 S12** | Root cause: `OLLAMA_URL=http://127.0.0.1:11434` in gemini.env caused Gemini-fail → load phi3.5 (3.8GB) → timeout → retry loop. Fix: removed entire Ollama fallback from gemini_proxy.py and both env vars from gemini.env. |
| Ollama service disabled on Pi | `[x]` **COMPLETE 2026-04-01 S12** | `sudo systemctl disable ollama.service`. Binary + phi3.5 model kept on disk. Will not auto-start on reboot. |
| Node-RED dead tabs removed | `[x]` **COMPLETE 2026-04-01 S12** | Deleted 4 tabs permanently: d3kOS Cloud Telemetry Push (dead endpoint), Community Engine Benchmark, Community Boat Map, Community Knowledge Log (Watch node error loop). 26 nodes removed. System tab only remains. |
| Pi load confirmed stable | `[x]` **COMPLETE 2026-04-01 S12** | Load 1.89 at 9 min uptime after fixes. Previous crisis load: 9.4+. |
| Fish RAG assessment | `[x]` **COMPLETE 2026-04-06 S17** | fish_rag_llm.py deployed. query_handler.py wired. On-demand Ollama synthesis active via gemma3:1b when Gemini offline. |
| Voice assistant fishing regulation queries | `[x]` **COMPLETE 2026-04-06 S18** | Ontario Regulation 2026.pdf (682 chunks), MNR.pdf (27 chunks), global_marine_emergency_contacts.pdf (6 chunks) indexed into d3kos_documents ChromaDB. RAG search confirmed returning correct size limits (walleye 35-45 cm). Total ChromaDB: ~2,028 docs. |
| On-demand Ollama — ingest fish-rag corpus into ChromaDB | `[x]` **COMPLETE 2026-04-06 S17** | 21 species PDFs already indexed. 3 visual guides newly added (54 chunks). Total: 1,313 docs. NOTE: dataset is fish ID guide only, not bag limits/size limits. |
| On-demand Ollama — inference speed | `[x]` **COMPLETE 2026-04-06 S17** | k=6→k=3 applied. Inference time ~114s (from ~200s). |
| LangChain deprecation in pdf_processor.py | `[x]` **COMPLETE 2026-04-06 S17** | Migrated to langchain-ollama + langchain-chroma. Deprecated .persist() removed. No warnings. |
| Ontario fishing regulations — actual bag limits/size limits | `[x]` **COMPLETE 2026-04-06 S18** | Ontario Regulation 2026.pdf indexed (682 chunks, 137 pages). RAG verified: walleye 35-45 cm size limit returned correctly. MNR.pdf (27 chunks) and global_marine_emergency_contacts.pdf (6 chunks) also indexed. |

---

## PART 12 — S19 Hotfixes (2026-04-06)

| Item | Status | Detail |
|------|--------|--------|
| tier_service.py — `_parse_tier()` helper | `[x]` **COMPLETE 2026-04-06 S19** | Root cause: `int("T0")` ValueError crash. tier_service uses integer FEATURE_MATRIX keys (0,1,2,3) but license.json stores string tiers ("T0","T1","T2"). Fix: added `_parse_tier()` helper that strips 'T' prefix. Two `int()` call sites replaced. Repo file synced from Pi. |
| admin-api.php `update_tier` duplicate rows | `[x]` **COMPLETE 2026-04-06 S19** | Root cause: S16 Admin CRM P6 testing inserted duplicate `atmyboat_tier` rows in `wpax_usermeta` (no unique index). INSERT ON DUPLICATE KEY UPDATE silently created new rows each tier change. Fix: SELECT→UPDATE/INSERT pattern + DELETE duplicates cleanup query run by Don. Dashboard now shows correct tier. |
| pdf-store.php INT32 overflow → no response | `[x]` **COMPLETE 2026-04-06 S19** | Root cause: `amboat_pdf_reports.report_id` was INT (max 2,147,483,647). Reached INT32_MAX — PHP fatal error on INSERT → no response body → PWA showed "Invalid response from server". Fix: `ALTER TABLE amboat_pdf_reports MODIFY report_id BIGINT UNSIGNED AUTO_INCREMENT`. Report now returns proper "no engine data" message. Note: "no engine data" is expected — Pi has no real engine sensors until on-water use. |
| handle_tier_change integer bug | `[x]` **COMPLETE 2026-04-07 S27c** | `cloud_agent.py handle_tier_change()` patched to normalise payload to string "T0"–"T3". Handles int (1→"T1"), string "1"→"T1", string "T1"→"T1". Service restarted. |

---

## PART 10 — Version Roadmap Summary

| Version | Description | Status |
|---------|-------------|--------|
| v0.9.1 | Voice AI Assistant | `[x]` Shipped |
| v0.9.2 | Core platform — cameras, units, Gemini, remote access, UI rebuild | `[~]` Code complete — UAT + on-boat tasks remain |
| v0.9.3 | AtMyBoat.com community platform (WordPress) | `[~]` Staging in progress |
| v0.9.4 | d3kOS Mobile Companion App (PWA) | `[~]` In progress |
| v0.9.4.1 | Pi ↔ Website ↔ App full integration (data pipeline wiring) | `[ ]` Planned — blocked on v0.9.3 live |
| v0.9.5 | Predictive Maintenance — 30-day baseline, anomaly detection, 5 ML models | `[ ]` Planned |
| v0.9.6 | Fleet Management — fleet map, analytics, Tier 3 activation | `[ ]` Planned |
| v0.9.7 | Remote Diagnostic Console — support tickets, AI diagnosis, fix delivery | `[ ]` Planned |
| v0.9.8 | Autonomous Agents + Failure Intelligence — self-healing Pi, recovery mode | `[ ]` Planned |
| v0.9.9 | Security Audit & Penetration Testing — required gate before v1.0 | `[ ]` Planned |
| v0.9.9.2 | Missed items — features specified but never built across all platforms | `[~]` In progress — M1/M2/M14/M15/M17 complete |
| v0.9.9.3 | Pre-Launch — Pi AODA + speech + partition/restore + cleanup + manual + image | `[~]` **ACTIVE — see Part 13 below** |
| v1.0 | Production launch — Phase 4 live push, archive.org image, staging → production | `[ ]` Blocked on v0.9.9.3 |
| v1.1 | CJK keyboard, self-hosted STUN coordination server, multi-language full | `[ ]` Future |

---

## PART 9 — v0.9.9.2 Missed Items
**Status: IN PROGRESS — planning complete 2026-04-08 S38**
**Definition:** Features that were fully specified and/or had backends built, but the front-end or user-facing implementation was never written. These are not deferred features — they were supposed to be built and were missed.
**Planning decisions recorded:** `ATMYBOAT_BUILD_REFERENCE.md` Part 18 (2026-04-08 S38)

### d3kOS — Missing Features

| ID | Item | Details | Status |
|----|------|---------|--------|
| M1 | **Anchor Watch — d3kOS dedicated page** | Dedicated `anchor-watch.html` page on d3kOS (T0 — all tiers). NOT in PWA (T0 users have no mobile app). Set Anchor button captures current GPS → stores anchor position. Radius slider default **25m** (adjustable — 25m is the safety-correct default; 50m puts you into neighbouring boats at anchor). Active state: Leaflet mini-map showing boat vs anchor drop point + live distance text. TTS alarm + visual flashing overlay on drag detect (3-poll confirm, 45s). DISMISS button always visible when alarm active. Repeat alarm every 60s until dismissed. T1+ sends mobile push via alert delivery pipeline (M15). Backend (`anchor_watch.py` at AI bridge :3002) fully deployed. | `[x]` **COMPLETE 2026-04-08 S41** — anchor-watch.html deployed to Pi. Flask route `/anchor-watch` in app.py. d3kOS stores anchor position natively (not SK). Haversine distance. Standard `#status-bar` + `.back-btn` + DAY/NGT. Checklist not updated at session close — corrected 2026-04-11. |
| M14 | **AI Engine Diagnostic — live data** | When engine cell tapped, `openDiag()` currently shows hardcoded demo content. Fix: pull live Signal K readings on tap → POST all engine readings to Gemini → populate panel with real diagnosis (plain English, urgency, suggested fixes — format per MASTER_SYSTEM_SPEC §6.4.4). **Tier: T2 and T3 only.** Fire immediately on tap — no confirmation. Response also integrated into PDF engine report. | `[x]` **COMPLETE + VERIFIED 2026-04-08 S39/S40** — `openDiag()` fully rewritten as async Gemini call. Tier gate via `/config/tier` Flask endpoint. Live SK data from `window._d3kEngData` cache (instruments.js). T0/T1 shows upgrade prompt. T2/T3 POSTs to Gemini proxy port 8097. Panel populated dynamically. **S40 fixes:** (1) overlays.js regex syntax error (literal newline in /\n/g — JS SyntaxError at parse time); (2) _setCellState decoupled from onclick — all engine cells now always tappable; (3) cellRpm typo fixed; (4) context menu on hold replaced with openDiag(); (5) font sizes increased (AI text 24px, buttons 22px). Verified by Don: "beautifully done it working." |

### PWA — Missing Screens

| ID | Item | Details | Status |
|----|------|---------|--------|
| M3 | **Command queue — send OTA/restart commands** | PWA screen for T1+ to send `ota_update` and `restart_service` commands to Pi via `command-queue.php`. Fix My Pi already exists as a separate screen. This covers the remaining two commands. Backend endpoint exists. Location: Pi Controls section within existing Fix My Pi flow or new "Pi Management" tab. | `[x]` **COMPLETE 2026-04-08 S39** — OTA Upgrade card was already in renderSettings(). "Restart Pi" card added: sends `restart_service` command via `apiSendCommand()`. Pi-side `handle_restart_services()` added to cloud_agent.py — restarts voice/ai-bridge/gemini-proxy/predictive. Deployed PWA to HostPapa, cloud_agent.py to Pi. |
| M4 | **Command queue — result poll and status** | PWA polls for command result and shows status to user. Backend exists. Status display not built. | `[x]` **COMPLETE 2026-04-08 S39** — Restart Pi card polls via `apiPollCommand()` every 5s, 2-minute timeout. OTA card already had full polling (every 10s, 20-minute timeout). Both complete with success/fail/timeout display. |

### T3 — Fleet Management Web Portal (NEW SCOPE — 2026-04-08)

| ID | Item | Details | Status |
|----|------|---------|--------|
| M2 | **T3 Fleet Management Web Portal** | **SCOPE EXPANDED from "fleet map PWA screen" to full web-based fleet management portal.** T3 operators need a dedicated web screen (not just a PWA map). Requirements: (1) Leaflet map showing all fleet vessels with boat names (not anonymous dots), coloured by health score; (2) Click vessel → full vessel detail: engine data, performance metrics, captain log entries, PDF reports; (3) Send customer service messages to captains from the portal; (4) Fleet-level alert management and notification history; (5) Engine operations summary across fleet. Architecture: PHP web pages (HostPapa), extending the fleet backend already built. Similar UX pattern to Admin CRM. Backend (`fleet-map.php`, `fleet-analytics.php`) already built. | `[x]` **COMPLETE 2026-04-11 S49** — `page-fleet-portal.php` (WP template, T3 gate, Leaflet map, vessel list, detail panel, fleet summary stats) + `mobile/fleet-message.php` (captain messaging via wp_mail()) + CSS block in style.css. Deployed to HostPapa staging. WordPress page created by Don (Template: Fleet Portal, slug: fleet) — confirmed complete 2026-04-11. |

### Alert Delivery (REDESIGNED — 2026-04-08)

| ID | Item | Details | Status |
|----|------|---------|--------|
| M15 | **Alert delivery pipeline — email + in-app, toggles, quiet hours** | **Twilio SMS removed — never approved. No additional cost solutions only.** Delivery channels: (1) Email via wp_mail() (T1+); (2) In-app badge in PWA. Alert types: anchor_drag, engine_overtemp, engine_oil_pressure, low_fuel, gps_lost, collision_risk. User controls: master email toggle, per-type toggles, quiet hours. Pi offline cron check (60 min, cPanel). | `[x]` **COMPLETE 2026-04-11 S48** — 5 parts deployed: (A) `alert-notify.php` Pi→email HostPapa endpoint; (B) `alert_watcher.py` v0.9.6 cloud notify with local pre-filter; (C) Pi settings.html alert prefs UI + Flask `/api/settings/alert-preferences`; (D) `offline-check.php` cron endpoint; (E) PWA app.js badge zero-on-view + visibilitychange refresh. **Phase 4 action required:** update cPanel cron URLs from /staging/ to / (see Phase 4 checklist). |

### Website

| ID | Item | Details | Status |
|----|------|---------|--------|
| M16 | **Website AI not working — FIXED 2026-04-08 S38** | Root cause confirmed: `atmyboat-config.php` on staging defined `ATMYBOAT_API_KEY` but `ai-assistant.php` expects `GEMINI_API_KEY`. Fix deployed: added `GEMINI_API_KEY`, `GEMINI_MODEL` (gemini-2.5-flash-preview-04-17), `GEMINI_MAX_TOKENS` (1000) to staging `atmyboat-config.php`. Legacy `ATMYBOAT_API_KEY` kept for compatibility. | `[x]` **COMPLETE 2026-04-08 S38** |
| M17 | **Website — full branding and design consistency** | **SCOPE EXPANDED from "forum theming only" to full website design review.** All public pages must be consistent, professional, and AODA-compliant. Issues identified: inconsistent fonts, font scale problems, layout flow, colour inconsistency across pages. Scope: (1) bbPress forum theming (categories, thread list, single topic, reply form — dark marine design system); (2) All page templates: consistent header, nav, footer, typography, spacing; (3) Design flows that guide the reader through the content; (4) Every page meets AODA minimum: 18px+ body, 4.5:1 contrast, 48×48px touch targets. | `[x]` **COMPLETE 2026-04-11 S46+S47** — S46: 88+ font-size violations fixed across 11 page templates (all pages 18px minimum). S47: bbpress.css nuclear rewrite — forum dark theme, full-width Twenty Twenty container overrides, WAVE 24 contrast errors resolved to 0. All files deployed to HostPapa staging. Checklist not updated at session close — corrected 2026-04-11. |
| M18 | **Community page — finalize simplified layout** | Hall of fame and challenges removed (S37). Remaining: finalize map + stats + recent forum discussions + "Go to Forum" button. | `[x]` **COMPLETE 2026-04-08 S38** — Confirmed live on staging: map → stats → "Recent Discussions" layout. No further changes needed. |
| M19 | **Website claims audit** | Claude reads all public-facing page templates, identifies features described but not built or not working, produces findings report with recommendations. Gate before Phase 4. | `[x]` **COMPLETE 2026-04-08 S38** — All 11 public pages audited. 3 hard blockers for Phase 4: (1) safety page claims Anchor Watch + AI Engine Diagnostic as current — both unbuilt; (2) pricing T3 claims Fleet GPS map — unbuilt; (3) download page claims "Full i18n" — Layer 0 only. Recommendation: add "Coming Soon" badges OR build M1/M14/M2 before live push. |
| — | **page-manual.php + PDF + RAG** | User manual (D3KOS_USER_MANUAL_v0992.md) to be: (1) Generated as PDF; (2) Uploaded to GitHub; (3) Ingested into Pi RAG (ChromaDB) so Helm AI can answer questions from it; (4) Linked from Help page on website. NOT a full PHP page — just a link to the PDF download + RAG integration. | `[~]` **PARTIAL 2026-04-08 S39** — page-manual.php built (Template Name: User Manual, PDF download button + 16-section ToC). Deployed to HostPapa staging. Help page updated with "User Manual" quick-link card (7th card → `/manual/`). DEFERRED: (1) Don must create GitHub release with PDF; (2) RAG ingest deferred — requires Ollama running for nomic-embed-text 768d embeddings. |
| — | **Hardware page — H2 duplicate photo** | Strip col 1 shows H2 (same as hero). Should revert to H1 (Pi in enclosure). Small visual fix. | `[x]` **COMPLETE 2026-04-08 S38** — `page-hardware.php` photo strip col 1 changed from H2-Nmea-200-connection.jpg → H1-Pi-in-enclosure-mounted.jpg. Alt text updated. Deployed to HostPapa staging. |

### i18n

| ID | Item | Details | Status |
|----|------|---------|--------|
| M5 | **Layer 1 — Speech-to-text multilingual** | Whisper-small (99 languages). Significant Pi build. **DEFERRED to v1.1.** | `[–]` Deferred v1.1 |
| M6 | **Layer 2 — TTS multilingual (Piper)** | Per-language Piper voice models. Significant Pi build. **DEFERRED to v1.1.** | `[–]` Deferred v1.1 |
| M7 | **Layer 3 — AI responses in user language** | Inject selected UI language into Gemini system prompt. One-line change in `query_handler.py`. Trivial — include in build. | `[x]` **COMPLETE 2026-04-08 S38** — Language injection added to `gemini-proxy.py` (Port 8097) at system_prompt build. Reads `/opt/d3kos/config/user-preferences.json` → `language` field. If not 'en'/'english', appends "Respond in {language}." to system prompt. Deployed to Pi, d3kos-gemini-proxy restarted, service active. |

### BUG LOG — Reported But Not Yet Investigated

| ID | Bug | Reported | Status |
|----|-----|----------|--------|
| BUG-01 | **Mute not working** | RESOLVED S44 2026-04-09. ALSA hardware mute (cset numid=2) cuts S330 speaker at OS level. Don confirmed working. | `[x]` DONE S44 |
| BUG-02 | **Voice 9-second delay** | RESOLVED S44c 2026-04-09. PDFProcessor deferred import in query_handler.py. 9.6s → 0.6s confirmed. | `[x]` DONE S44c |
| BUG-03 | **"Nothing heard" on first voice query after wake word** | RESOLVED S44 2026-04-09. Pre-warm KaldiRecognizer at startup via _prewarm_recognizer(). listen() uses pre-warmed instance instantly; kicks off next pre-warm in background while recording. Don confirmed "works fast." | `[x]` DONE S44 |

---

### REMOVED FROM BUILD (never requested)

| ID | Item | Reason |
|----|------|--------|
| M13 | ~~Marine Vision motion detection~~ | Never requested by Don. Removed 2026-04-08 S38. |

### Integration Tests — Post-Launch (require live site + real hardware)

| ID | Item | Expected Result | Status |
|----|------|-----------------|--------|
| M8 | **T1: Pi → website sync** | POST to `data-ingress.php` with real device token → 200 OK, engine snapshot in DB, `last_sync` updated | `[ ]` Post-launch |
| M9 | **T2: Command round-trip** | App queues `restart_service` → Pi picks up on next sync → executes → result returned to app within 35 min | `[ ]` Post-launch |
| M10 | **T3: Community data flow** | Enable boat_map in Pi Settings → position appears on `/community` map within 30 min | `[ ]` Post-launch |
| M11 | **T4: Anchor drag alert** | Simulate anchor drag on Pi → immediate export fires → alert in `amboat_alerts` DB within 2 min | `[ ]` Post-launch |
| M12 | **T5: Find My Boat** | Pi syncs position → Chart Room shows correct map marker within 35 min | `[ ]` Post-launch |

---

---

## PART 13 — v0.9.9.3 Pre-Launch Build
**Version:** v0.9.9.3
**Status:** ACTIVE — defined by Don 2026-04-11
**Definition of done:** All items below complete → Pi image created → uploaded to archive.org → staging updated → Phase 4 live push.

| # | Item | Detail | Status |
|---|------|--------|--------|
| 1 | **Pi AODA compliance** | DEP13 — Track A (contrast), Track B (skip links/h2/aria), Track C (font floor). All 13 Flask templates + static pages. Plan from S51 ready. | `[x]` **COMPLETE S54 2026-04-12** — Tracks A+B+C all done. 13 templates + d3kos.css. Commits b573e93, 90db62a, 46c015a. Deployed + confirmed on Pi (Don screenshots). |
| 2 | **Helm working** | Full d3kOS dashboard functional — all pages, all routes, day/night, More menu 9 items. Confirm after Pi reboot (S52 fixes). | `[x]` **COMPLETE S54 2026-04-12** — Confirmed by Don screenshot after Pi reboot. ENGINE label white, status bar visible, day/night both working. |
| 3 | **Speech working** | Voice assistant pipeline end-to-end: wake word → query → Piper TTS female voice response. TTSPlayer/S330 sample rate issue still open. Engine-on test needed. | `[x]` **COMPLETE 2026-04-12** — Confirmed working by Don. |
| 4 | **Pi partition for config/restore** | Dedicated partition storing system config so Fix My Pi can save and restore configuration across reflashes. (FI4 — previously deferred.) | `[x]` **COMPLETE S55 2026-04-12** — FI4 Config Backup & Recovery deployed: config-backup-status.php (HostPapa), /backup-status CRM page, Pi GET /api/recovery-key, PWA Recovery Key card (T1+). Cloud-backed config packages via amboat_config_packages. |
| 5 | **Cleanup unnecessary files** | Remove unused files from Pi. | `[x]` **COMPLETE S55 2026-04-12** — phi3.5 model removed (2.1G), tmp files cleared, boat_log + pictures/video preserved. 3GB recovered (27G → 24G). |
| 6 | **Update user manual** | (a) Update manual content to v0.9.9.3; (b) Deploy to Pi RAG (ChromaDB ingest); (c) Update website page-manual.php; (d) Create GitHub release with PDF. | `[~]` **PARTIAL S55 2026-04-12** — (a) DONE: D3KOS_USER_MANUAL_v0992.md v2.3.0 — added Anchor Watch section, 6 alert types, Recovery Key in Settings. (b) DONE: RAG ingested 2079→2216 docs. (c) DEFERRED: page-manual.php ToC structure unchanged (16 sections); actionable only after (d). (d) DEFERRED — Don creates GitHub release with PDF (manual task). |
| 7 | **Create Pi image** | Full SD card image of v0.9.9.3 Pi state. | `[~]` **IN PROGRESS 2026-04-12 S55c** — Don performing SD card backup now. |
| 8 | **Upload to archive.org** | Upload Pi image to archive.org item. Update OTA SHA-256 in version-registry.php. | `[x]` **COMPLETE 2026-04-12** — Image uploaded: https://archive.org/details/d3kos_v0.9.9.2 (50GB uncompressed .img). README.md updated. version-registry.php (HostPapa) — OTA SHA-256 not applicable for disk image (OTA uses services tar.gz). |
| 9 | **Update staging** | Deploy v0.9.9.3 changes to HostPapa staging. Smoke test all pages. | `[x]` **COMPLETE 2026-04-12 S55d** — 3 waves deployed: FI4 PHP (3 files), full theme sync (120 files), PWA (9 files). Smoke tests all green: config-backup 401, config-restore 404, config-backup-status 401, staging home 200, PWA 200, alert-notify 401. |
| 10 | **Promote to production** | Phase 4 live push — Don's hands only. Update cPanel cron URLs (offline-check.php). Rotate keys. Post-push smoke test. | `[~]` **READY — awaiting Don** — see Phase 4 runbook below. |

---

*Archived originals: `.aao-backups/20260320_000000_checklist-merge/`*
*Do not create new PROJECT_CHECKLIST.md files — update this file only.*
