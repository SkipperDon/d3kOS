# d3kOS & AtMyBoat.com — Master Project Checklist
**Version:** 1.2 | **Last Updated:** 2026-03-20 (Session: anti-sycophancy deploy + checklist updates)
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
**Status: COMPLETE** — v0.2.0 published to GitHub + npm 2026-03-11. Worker thread architecture. 21,719 labeled images, YOLOv8n model.

| Open item | Status |
|-----------|--------|
| Add download-on-first-run (auto-fetch model from GitHub Releases) | `[ ]` |
| Test on OpenPlotter | `[ ]` |

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
| 4 | Camera on-boat tests (DHCP reservations, 24hr stability, performance, storage) | Don (on boat with cameras) | `[!]` On-boat dependency |
| 5 | SQS calculation block — add to CLAUDE.md session-close | Claude | `[ ]` AAO Section 19 |
| 6 | RAG re-ingest after each Pi deployment | Claude (recurring) | `[~]` Must run after every deploy session |
| 7 | Remove git worktrees (v0.9.2, v0.9.2.1, v0.9.3) from disk | Claude | `[ ]` `build-v0.9.2.1` has 5 unmerged commits — decide: merge or discard before removing |
| 9 | Marine Vision — UI does not match operator expectations | Don + Claude | `[ ]` Functional (4 cameras streaming, CORS fixed 2026-03-21) but layout/UX is not what was expected. Don to describe what the expected UI looks like — then scope the redesign. |
| 8 | Marine Vision — plug-and-play camera setup wizard | Claude | `[ ]` **Confirmed solution 2026-03-21:** Two-layer approach. Layer 1 (auto): on scan, read ONVIF device name from each camera — if name matches a known position (Bow/Helm/Port/Starboard) auto-assign silently, no wizard needed. Layer 2 (fallback): Initial Setup wizard shows live thumbnail per discovered camera → user taps image and selects position from dropdown → assigned by MAC (IP-change safe). Settings camera section also needs: correct API field names (currently reads slot.id/slot.name/slot.camera_id — API returns slot_id/label/hardware_id), scan button, and assign controls for post-setup changes. |
| 10 | Fish detection — Gemini Vision species ID | Claude | `[x]` **COMPLETE 2026-03-21.** `identify_species_gemini()` + on-demand `POST /detect/identify/<capture_id>` endpoint in fish_detector.py. Sends capture JPEG to Gemini 2.5 Flash Vision API. Returns: common name, scientific name, confidence, visual features, Ontario regulation note. Stored in captures.db. Marine Vision shows "Identify Species" button per capture — tappable, retryable until satisfied. Auto-call removed (was causing 429 rate limit errors on free tier). Gemini key from existing gemini.env. |
| 11 | Ontario fish species RAG — confirm scripts run on Pi | Don/Claude | `[ ]` Run `create_fish_species_pdfs.py` then `add_fish_to_rag.py` on Pi to populate `/opt/d3kos/datasets/fish-rag/species_pdfs/`. Feeds voice AI text queries about Ontario fish regulations. |
| 12 | Engine Dashboard — restore original layout | Claude | `[x]` **COMPLETE 2026-03-21.** Full rebuild: 5 sections (Engine, Electrical, Tanks, System Status, Network Status), progress bars on all cells, alert states retained, DAY/NGT toggle, back arrow, one-finger scroll. CSS v=19, AODA compliant. |
| 13 | Helm Assistant — new page | Claude | `[x]` **COMPLETE 2026-03-21.** 4 quick-action buttons (Engine Status, Check Issues, System Health, Run Diagnostics), chat UI, RAG→Gemini fallback (MANUAL/GEMINI source badge), AODA fonts (18px min), keyboard-fix.js. Added to More menu. |
| 14 | Gemini CORS fix — d3kos-gemini proxy | Claude | `[x]` **COMPLETE 2026-03-21.** Root cause: no CORS headers on gemini_proxy.py. Browser at :3000 was blocked making cross-origin calls to :3001. Fix: `@app.after_request` CORS handler added. Key and service were correctly configured — proxy was working, browser was blocked. |
| 15 | Gemini system prompt — expand to full vessel operation | Claude | `[x]` **COMPLETE 2026-03-21.** Navigation-only prompt caused Helm Assistant to give unhelpful answers to engine/mechanical questions. Prompt now covers: engine diagnostics, electrical, mechanical, maintenance, on-board systems, navigation, safety. `_ragUseful()` threshold also tightened (30→60 chars, +8 no-info patterns). |
| 16 | Engine Dashboard + Settings — remove 960px max-width | Claude | `[x]` **COMPLETE 2026-03-21.** Engine gauge cells were ~174px wide on 1280px display due to 960px container. Settings had same constraint in `.settings-content`. Both now fill full screen width (~238px per engine cell). |
| 17 | Signal K upgrade v2.22.1 → v2.23.0 + remote_api.py port fix | Claude | `[x]` **COMPLETE 2026-03-22.** SK upgraded to v2.23.0 on Pi. remote_api.py port fixed (:3000→:8099). AvNav patch survives. All SK REST endpoints responding. Smoke test passed. |
| 18 | Boat log — voice-to-text "api unavailable, transcript not saved" | Claude | `[x]` **COMPLETE 2026-03-22.** Root cause: `vosk-transcribe` CLI not installed. Fix: replaced with Vosk Python API + ffmpeg webm→WAV conversion. Deployed, service active. |
| 19 | Settings — o-charts section not working as intended | Don + Claude | `[x]` **COMPLETE 2026-03-22.** Root cause: openDoc() only showed toast with file path. Fix: /docs/<name> Flask route + full-screen markdown overlay with day/night theme support. Three docs deployed to Pi at /opt/d3kos/docs/. |
| 20 | Settings — AvNav charts documentation section not working as intended | Don + Claude | `[x]` **COMPLETE 2026-03-22.** Same fix as item 19 — resolved by same overlay implementation. |

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
**Status: IN PROGRESS — Staging build underway**
**Platform:** WordPress + Twenty Twenty child theme on HostPapa staging
**Repo:** github.com/SkipperDon/atmyboat-forum
**Rules:** Child theme only · PHP + cURL · No Node.js · AI model = claude-haiku-4-5-20251001 · AODA enforced

### Phase 0 — Repo & Staging Setup
- [x] GitHub repo created, staging confirmed, FTP access established, child theme created

### Phase 1 — bbPress Forum
- [x] bbPress installed on staging, /forum/ slug confirmed

### Phase 2 — Features
| Item | Status |
|------|--------|
| 2A — MailPoet email notifications | `[ ]` Not started |
| 2B — AODA CSS & design system (style.css, bbpress.css, functions.php) | `[~]` Core done — font sizes need final audit |
| 2C — AI Assistant (inc/ai-assistant.php, ai-widget.php, AJAX handler) | `[x]` Complete — renders and submits on staging |
| 2D — Products Hub (page-products.php, products.json) | `[x]` Complete — renders on staging |
| 2E — SEO (Yoast/RankMath, sitemap, Bing Webmaster) | `[ ]` Not started |

### Phase 3 — AODA Compliance Audit
**Owner: Don** — Keyboard nav · WAVE scan · Touch targets (≥48×48px) · Contrast (4.5:1) · Screen reader

- [ ] All 5 audit steps complete and issues fixed

### Phase 4 — Staging → Live
**Owner: Don's hands only**
- [ ] UpdraftPlus full backup of live site
- [ ] cPanel Staging → Push to Live
- [ ] Post-push smoke test (forum, products, AI widget)
- [ ] GitHub repo set to Private
- [ ] Remove Gemini API key from atmyboat-config.php and rotate
- [ ] Change FTP password for d3kos@atmyboat.com

### Post-Launch
- [ ] Monitor Gemini API usage (free tier: 20 req/day)
- [ ] UAT with real boaters (ages 45–70)
- [ ] Node-RED flow verification once AtMyBoat.com APIs are live (see Part 4.7)
  - POST /api/telemetry/push
  - POST /api/community/benchmark
  - POST /api/community/position
  - Replace placeholder URL in "Post to Community DB" nodes (2 nodes)
  - Create /opt/d3kos/config/cloud-credentials.json with AtMyBoat.com API key

### Abandoned v0.9.3 Concept
**Status: ABANDONED** — An earlier v0.9.3 concept (Next.js 15 + Supabase + Stripe + Vercel) was superseded by the current WordPress + HostPapa approach. The original spec is archived at `deployment/v0.9.3/old instructions/PROJECT_CHECKLIST.md.bak`. Do not action any items from that spec.

---

## PART 8 — v0.9.4 d3kOS Mobile Companion App (PWA)
**Status: PLANNED — Not started. Pre-build task: remove Tailscale from Pi (done 2026-03-19).**
**Strategy:** `deployment/docs/MOBILE_APP_STRATEGY_BRIEF.md` v2.0.0
**Q&A record (authoritative):** `deployment/docs/MOBILE_APP_QA_RECORD.md` v1.0.0

| Build step | Status |
|------------|--------|
| Pre-build: Remove Tailscale from Pi | `[x]` Done 2026-03-19 |
| Foundation (PWA shell on GitHub Pages) | `[ ]` |
| WebRTC/STUN live tunnel (Pi ↔ phone) | `[ ]` |
| Core PWA features (Find My Boat, boat health dashboard) | `[ ]` |
| Fix My Pi (diagnostic + restore, $29.99/incident) | `[ ]` |
| PDF Reports via mPDF + Gemini 2.5 Flash (T2/T3 only) | `[ ]` |
| OS Lockdown (apt-mark hold + pre-upgrade hook) | `[ ]` |
| Command queue / OTA / Fix My Pi broker (HostPapa PHP+MySQL) | `[ ]` |

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
| v1.0 | Multi-language + v0.9.4 + signalk-forward-watch AppStore | `[ ]` Planned |
| v1.1 | CJK keyboard, self-hosted STUN coordination server, fleet features | `[ ]` Future |

---

*Archived originals: `.aao-backups/20260320_000000_checklist-merge/`*
*Do not create new PROJECT_CHECKLIST.md files — update this file only.*
