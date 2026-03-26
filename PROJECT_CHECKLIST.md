# d3kOS & AtMyBoat.com — Master Project Checklist
**Version:** 1.3 | **Last Updated:** 2026-03-24 (Session B: v0.9.3 Phase 2B root cause confirmed)
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
| S6 | **`/accessibility`** — AODA compliance statement page (Ontario legal requirement). | `[x]` **COMPLETE 2026-03-26** commit 7c0dfe0 |
| S6 | 2E — SEO (Yoast, sitemap, Bing Webmaster) | `[ ]` Deferred to post-launch |
| **Operator task** | **WordPress admin: create all pages** — install-pages.php run, Safety + Account created manually, slugs fixed via fix-slugs.php. | `[x]` **COMPLETE 2026-03-25 (D)** |
| **Operator task** | **WordPress admin: update menus** — Main menu verified OK. Footer menu not yet set up. | `[~]` Footer menu still needed |
| **Operator task** | **Stripe setup** — 2 webhooks created, all keys added to server inc/atmyboat-config.php. | `[x]` **COMPLETE 2026-03-25 (D)** |
| **Operator task** | **Database schema** — 12 tables installed via install-schema.php (browser-run). pi_installation_id migration ran. | `[x]` **COMPLETE 2026-03-25 (D)** |
| **Operator task** | **Fix My Pi cron** — cPanel cron every 5 min, fix-my-pi-timeout.php confirmed active. | `[x]` **COMPLETE 2026-03-25 (D)** |
| **Operator task** | **Full theme deploy to staging** — zip upload + extract via cPanel. All new files confirmed. | `[x]` **COMPLETE 2026-03-25 (D)** |
| **S6 gap** | **mobile/config.php template** — server-only file referenced by all mobile endpoints, never committed. Create placeholder template in repo next session. | `[x]` **COMPLETE** commit ee8011d |
| **S6 fix** | **`/hardware` BOM display too small** — font sizes in BOM cards and connectivity section need review. Don flagged 2026-03-25 (C). Address in next session. | `[x]` **COMPLETE** commit 48b88b4 |
| S7 | **`/account`** — Account management: current tier, billing history, cancel subscription, paired devices. Reads Stripe Customer Portal. | `[x]` **COMPLETE 2026-03-25 (D)** commit f206a1d |
| S7 | **`/safety`** — Safety features page: Forward Watch, engine protection, anchor watch, cameras, weather, alerts. | `[x]` **COMPLETE 2026-03-25 (D)** commit 8c04b0e — fonts fixed commit 3a2138d |
| S7 | **FTP deploy via Python** — Deploy single files via Python ftplib (bash breaks ! in password). | `[x]` **COMPLETE 2026-03-25 (D)** — page-safety.php deployed via Python FTPS |
| S7 | **Footer menu** — Create footer menu in WordPress Admin → Appearance → Menus. | `[ ]` Don's task |
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
- [ ] Import `setup/mobile-schema.sql` via phpMyAdmin → 7 tables
- [ ] Run `setup/install-pages.php?key=<key>` once to create all WP pages, then delete the file
- [ ] Install MailPoet plugin on staging if not already installed
- [ ] Create `.env` from `.env.example` with FTP credentials, then run `deploy/sync-staging.sh`

### Phase 3 — AODA Compliance Audit (Session 7)
**Owner: Don** — Keyboard nav · WAVE scan · Touch targets (≥48×48px) · Contrast (4.5:1) · Screen reader
- [x] **COMPLETE 2026-03-26** — Don ran WAVE on all pages and confirmed all red items cleared. Known exception: WordPress frame WP bar (not our code, ignored). Footer still broken but deferred by operator.

### Phase 4 — Staging → Live (Session 8)
**Owner: Don's hands only**
- [ ] UpdraftPlus full backup of live site
- [ ] cPanel Staging → Push to Live
- [ ] Post-push smoke test (all pages, AI widget, Stripe Fix My Pi)
- [ ] GitHub repo set to Private
- [ ] Rotate Gemini API key
- [ ] Change FTP password for d3kos@atmyboat.com

### Post-Launch
- [ ] Monitor Gemini API usage (free tier: 20 req/day)
- [ ] UAT with real boaters (ages 45–70)
- [ ] Node-RED flow activation — endpoints now built in S6. After live push: replace placeholder URL in "Post to Community DB" nodes, create /opt/d3kos/config/cloud-credentials.json, enable 3 flows. See Part 8A §8A.2.

### Abandoned v0.9.3 Concept
**Status: ABANDONED** — An earlier v0.9.3 concept (Next.js 15 + Supabase + Stripe + Vercel) was superseded by the current WordPress + HostPapa approach. The original spec is archived at `deployment/v0.9.3/old instructions/PROJECT_CHECKLIST.md.bak`. Do not action any items from that spec.

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
| Foundation (PWA shell on GitHub Pages) | `[ ]` |
| WebRTC/STUN live tunnel (Pi ↔ phone) | `[ ]` |
| Core PWA features (Find My Boat, boat health dashboard) | `[ ]` |
| Fix My Pi (diagnostic + restore, $29.99/incident) | `[ ]` |
| PDF Reports via mPDF + Gemini 2.5 Flash (T2/T3 only) | `[ ]` |
| OS Lockdown (apt-mark hold + pre-upgrade hook) | `[ ]` |

### 8.2 — App ↔ Website API Integration (app-side JavaScript)
**Note:** All website PHP endpoints listed here were built in v0.9.3 S5 and are on staging. The app-side calls (this section) are entirely unbuilt — this is the missing connection.

| # | App feature | Calls | What it does | Status |
|---|------------|-------|--------------|--------|
| AW1 | First install — device registration | `POST register-device.php` | Generates device UUID, stores on HostPapa, links to install | `[ ]` |
| AW2 | QR pairing — link device to account + vessel | `POST pair-device.php` | User scans QR on Pi → app sends UUID + user token + vessel name/type → account linked. T3: can pair multiple Pis. | `[ ]` |
| AW3 | Fix My Pi — trigger diagnostic | `POST fix-my-pi-billing.php` → Stripe → `POST command-queue.php` | Charges $29.99, writes `fix_my_pi` command for the active Pi | `[ ]` |
| AW4 | Send command to Pi | `POST command-queue.php` | App writes command for the active Pi (restart_service, ota_update, reboot) | `[ ]` |
| AW5 | Poll command result | `GET command-queue.php?id=<id>` | App checks if Pi has completed the command; shows status | `[ ]` |
| AW6 | Request PDF report | `POST pdf-report.php` | App triggers report for the active Pi; returns download URL | `[ ]` T2/T3 only |
| AW7 | Read boat health dashboard data | `GET dashboard-data.php?pi=<installation_id>` (to be built in v0.9.4.1 §8A.4) | App reads last engine snapshot, sync time, alerts for the active Pi | `[ ]` Blocked on §8A.4 |
| AW8 | Find My Boat | `GET dashboard-data.php?pi=<installation_id>` position fields | App reads last known GPS + timestamp for the active Pi; displays on map | `[ ]` Blocked on §8A.4 |
| AW9 | User authentication | WordPress cookie auth or JWT via `auth.php` | App must authenticate before any endpoint call; session token stored on device | `[ ]` Auth mechanism to be decided |

### 8.3 — Multi-Boat: Boat Selector (app-side, T3)
**Depends on:** v0.9.3 S6 schema fix (vessel_name, is_primary columns in d3kos_pairings)

| # | Item | Detail | Status |
|---|------|--------|--------|
| MB1 | Fetch paired vessels list | `GET list-vessels.php` (new endpoint, v0.9.4.1 §8A.4) — returns all Pis paired to this account: vessel name, type, last sync time, online/offline state | `[ ]` |
| MB2 | Boat selector screen | Shown on app open if account has >1 paired Pi. Cards per vessel: name, type icon, last sync time, online indicator. Tap to select. | `[ ]` |
| MB3 | Active boat state | Selected `pi_installation_id` stored in device localStorage. All subsequent API calls pass it as a parameter. | `[ ]` |
| MB4 | Boat switcher in app nav | Persistent control in header/nav showing current vessel name. Tap → returns to boat selector screen. | `[ ]` |
| MB5 | Primary boat default | On app open with >1 vessel: auto-select the `is_primary` vessel. User can change primary in app settings. | `[ ]` |
| MB6 | Single-boat shortcut | If account has exactly 1 paired Pi: skip boat selector entirely, go straight to dashboard. | `[ ]` |
| MB7 | Vessel name displayed on QR pairing | During QR scan flow: prompt "Name this vessel" + vessel type dropdown before completing pairing | `[ ]` |

### 8.4 — Tier Service on Pi (port 8093)
**Belongs in v0.9.4 build. Pi nginx already routes `/tier/` to port 8093 but no service exists. Pi dashboard and Settings call `/tier/status` to decide which features to show. Feature gating on the Pi is broken without this.**

| # | Item | Status |
|---|------|--------|
| TS1 | Build tier service Python script on Pi (port 8093) — reads `license.json`, returns `{ "tier": 2, "features": { "export": true, "pdf_reports": true, "community": true, ... } }`. One service, lightweight, reads a local file. | `[ ]` |
| TS2 | Register as systemd service (`d3kos-tier.service`) — starts on boot, restarts on crash | `[ ]` |
| TS3 | Upgrade prompt in app — locked features show "Upgrade to [tier] to unlock" with link to `/upgrade` page on atmyboat.com | `[ ]` |
| TS4 | Chart Room locked sections — PDF Reports, Analytics, Fleet Map shown as locked cards with upgrade CTA for users below required tier | `[ ]` |

### 8.5 — Deployment Solutions (all required before v0.9.4 ships)


| # | Item | Status |
|---|------|--------|
| DEP1 | **OTA download source** — confirm GitHub Releases as the Pi's download source. Decide release package format (tar.gz). Document the public download URL pattern. | `[ ]` Decision needed |
| DEP2 | **Pi upgrade script** — build the script the Pi runs when it receives an `ota_update` command: check disk space, snapshot current install, curl download from GitHub Releases, SHA-256 verify, stop services, overwrite files, restart, health check, rollback on failure, report result back via command queue. | `[ ]` Largest gap in v0.9.4 |
| DEP3 | **Fix My Pi file manifest** — generate a SHA-256 manifest of every file in a clean d3kOS installation. Host on HostPapa. Fix My Pi compares Pi files against it. Must be regenerated for every new d3kOS release. | `[ ]` Required for Fix My Pi integrity check |
| DEP4 | **SQL-before-PHP deploy gate** — add hard gate to v0.9.4.1 deploy checklist: run S6 MySQL ALTER TABLE statements via phpMyAdmin BEFORE deploying any new PHP files. If PHP deploys first and ALTERs haven't run, multi-boat writes will fail silently. | `[ ]` Sequencing risk |
| DEP5 | **T3 multi-Pi OTA** — add "Update all vessels" to app UX. Queues one `ota_update` command per paired Pi. App shows per-Pi progress bars simultaneously. | `[ ]` T3 users can't update all boats at once without this |
| DEP6 | **PWA version enforcement** — app calls `version-registry.php` on launch, compares to running service worker version. Shows "Update available — tap to refresh" banner if stale. Prevents users running old app against new Pi firmware. | `[ ]` |
| DEP7 | **OS Lockdown delivery path** — decide how `apt-mark hold` + pre-upgrade hook gets onto the Pi: (a) manually via SSH by Don before v0.9.4 ships, (b) `setup_lockdown` command via command queue on first connect, or (c) bundled in the v0.9.4 OTA package. | `[ ]` Decision needed |

---

## PART 8A — v0.9.4.1 Pi ↔ Website ↔ App Integration
**Status: NOT STARTED — All three systems built independently. This version wires them together.**
**Definition:** v0.9.4.1 completes the full data pipeline: Pi exports reach the real website endpoint, Node-RED community flows activate, the command queue is read by the Pi, community API endpoints go live on the website, and the Chart Room + Find My Boat display live Pi data.
**Depends on:** v0.9.3 staging → live push (Phase 4). All items below are blocked until website is live.

### 8A.1 — Pi Side: Connect Export Worker to Real Endpoint

| # | Item | File | Status |
|---|------|------|--------|
| P1 | Update `export_worker.py` URL from placeholder to real endpoint | `services/export/export_worker.py` line 30 — `d3kos-cloud-api.example.com` → `https://atmyboat.com/mobile/data-ingress.php` | `[ ]` |
| P2 | Fix auth headers in `export_worker.py` — current: `Bearer <installation_id>` wrong. Needs: `Authorization: Bearer <API_KEY>` + `X-Device-Token: <device_uuid>` to match `data-ingress.php` auth.php | `services/export/export_worker.py` | `[ ]` |
| P3 | Add command pickup loop — `data-ingress.php` returns `pending_commands` array in response body. `export_worker.py` currently discards it. Pi must read and execute each command. | `services/export/export_worker.py` | `[ ]` |
| P4 | Alert-triggered export — critical alerts (anchor drag, engine overtemp, low fuel) must trigger immediate export, not wait for next 30-min timer. Add event hook from alert system → export queue. | `services/export/export_worker.py` + alert service | `[ ]` |
| P5 | Create `/opt/d3kos/config/cloud-credentials.json` with AtMyBoat.com device API key. Add to `.gitignore`. Template: `{ "atmyboat_api_key": "YOUR_KEY_HERE", "device_uuid": "auto-generated-on-first-run" }` | Pi config | `[ ]` |
| P6 | **Pi reads tier from sync response and updates license.json** — when `data-ingress.php` returns `"tier": "T2"` in the response body, `export_worker.py` must read it and write the new tier integer to `/opt/d3kos/config/license.json`. This is how a tier upgrade paid on the website reaches the Pi (max 30-min delay). | `services/export/export_worker.py` | `[ ]` |
| P7 | **T0 → T1 upgrade path** — when `pair-device.php` confirms pairing, response includes `"tier": "T1"`. Pi reads it and upgrades `license.json` from tier 0 to tier 1. Enables export and cloud sync for the first time. | `services/export/export_worker.py` | `[ ]` |

### 8A.2 — Pi Side: Activate Node-RED Community Flows

| # | Item | Status |
|---|------|--------|
| N1 | Update placeholder URL in 2 Node-RED "Post to Community DB" flow nodes → real `https://atmyboat.com/mobile/data-ingress.php` | `[ ]` |
| N2 | Wire API key from `/opt/d3kos/config/cloud-credentials.json` into Node-RED HTTP Request nodes (not hardcoded) | `[ ]` |
| N3 | Enable the 3 disabled Node-RED flows: telemetry/push, community/benchmark, community/position | `[ ]` |
| N4 | End-to-end test: toggle community sharing ON → data flows to atmyboat.com → appears on community map | `[ ]` Blocked on v0.9.3 live |

### 8A.3 — Website Side: Community API Endpoints

| # | Item | Endpoint | Status |
|---|------|----------|--------|
| W1 | Build `POST /api/community/markers` endpoint — receives anonymised hazard markers from Pi, stores in WP custom table | New PHP file | `[ ]` |
| W2 | Build `GET /api/community/markers?bbox=` endpoint — returns markers within bounding box for community map display | New PHP file | `[ ]` |
| W3 | Build `POST /api/telemetry/push` endpoint — receives engine benchmark telemetry from Node-RED flow | New PHP file | `[ ]` |
| W4 | Build `POST /api/community/benchmark` endpoint — receives performance comparison data from Node-RED flow | New PHP file | `[ ]` |
| W5 | Build `POST /api/community/position` endpoint — receives boat position update for community map dot | New PHP file | `[ ]` |
| W6 | Community map 500m blur on read — `/api/community/markers` GET must round coordinates to 2 decimal places on output even if stored with higher precision | `[ ]` |

### 8A.4 — Website Side: Display Synced Pi Data + Multi-Boat Endpoints

**Note:** All queries in D1–D4 must filter by `pi_installation_id`, not just `user_id`. Without this, T3 multi-boat data is mixed together.

| # | Item | Page / Endpoint | Status |
|---|------|-----------------|--------|
| D1 | Chart Room dashboard — display last sync time, d3kOS version, engine snapshot (RPM, coolant, fuel) from `amboat_engine_snapshots WHERE pi_installation_id = ?` | `/dashboard` (The Chart Room) | `[ ]` |
| D2 | Find My Boat — display last known GPS + timestamp. T1+ only. "Pi offline" if >2h since last sync. Per-Pi (not per-user). | `/dashboard` | `[ ]` |
| D3 | Alert history — last 20 alerts from `amboat_alerts WHERE pi_installation_id = ?` | `/dashboard` | `[ ]` |
| D4 | PDF report download list — last 20 from `atmyboat_pdf_reports` user meta | `/dashboard` (T2/T3 only) | `[ ]` |
| D5 | Build `dashboard-data.php` — GET endpoint, accepts `?pi=<installation_id>`, returns engine snapshot + position + alerts + sync time for that Pi. Auth required. | New PHP file | `[ ]` |
| D6 | Build `list-vessels.php` — GET endpoint, returns all Pis paired to the authenticated account: vessel_name, vessel_type, pi_installation_id, is_primary, last_sync, online/offline state. Used by app boat selector (MB1). | New PHP file | `[ ]` |

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
| T6 | PDF report: T2 user requests engine report → Gemini called → PDF generated → download link returned | PDF available within 30 seconds | `[ ]` |

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

## PART 10 — Version Roadmap Summary

| Version | Description | Status |
|---------|-------------|--------|
| v0.9.1 | Voice AI Assistant | `[x]` Shipped |
| v0.9.2 | Core platform — cameras, units, Gemini, remote access, UI rebuild | `[~]` Code complete — UAT + on-boat tasks remain |
| v0.9.3 | AtMyBoat.com community platform (WordPress) | `[~]` Staging in progress |
| v0.9.4 | d3kOS Mobile Companion App (PWA) | `[ ]` Planned |
| v0.9.4.1 | Pi ↔ Website ↔ App full integration (data pipeline wiring) | `[ ]` Planned — blocked on v0.9.3 live |
| v1.0 | Multi-language + v0.9.4 + signalk-forward-watch AppStore | `[ ]` Planned |
| v1.1 | CJK keyboard, self-hosted STUN coordination server, fleet features | `[ ]` Future |

---

*Archived originals: `.aao-backups/20260320_000000_checklist-merge/`*
*Do not create new PROJECT_CHECKLIST.md files — update this file only.*
