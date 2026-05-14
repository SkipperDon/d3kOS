# d3kOS & AtMyBoat.com — Master Project Checklist (Active Items)
**Version:** 3.3 | **Last Updated:** 2026-05-12 S79 — WiBoat + SafeHelm integrated architecture complete
**Archive:** `PROJECT_CHECKLIST_ARCHIVE.md` — all completed work, decisions, and history preserved

> This file contains OPEN, IN-PROGRESS, and BLOCKED items only.
> For completed work, design decisions, and historical context → `PROJECT_CHECKLIST_ARCHIVE.md`
> PART 17 (Bug Tracker) always stays in this file per standing rule.

---

## LEGEND
- `[ ]` Not started
- `[~]` In progress
- `[!]` Blocked / needs action
- `[–]` Abandoned / superseded

---

## PART 17 — v0.9.9.4 Bug Fixes — STANDING HOLISTIC BUG TRACKER

**Version:** v0.9.9.4
**Standing rule:** ALL bugs on ALL platforms go here first — before any fix is attempted. No fix without a BUG-XX entry. Read this section AND `deployment/docs/V09994_BUG_FIXES.md` at the start of every session before accepting any new work.
**Full investigation doc:** `deployment/docs/V09994_BUG_FIXES.md`

| # | Bug | Status | Detail |
|---|-----|--------|--------|
| BUG-08 | Helm Assistant on-screen keyboard shows then immediately hides; manual keyboard does not type | `[~]` **IN PROGRESS — fix v2.1 insufficient** | `keyboard-fix.js` v2.1 deployed. Root cause: `el.blur()` fires previous tap's `{ once: true }` hideKeyboard listener BEFORE `_recentlyShown` is set. Next step: test whether first tap (no prior listener) works; consider removing `el.blur()` + using `requestAnimationFrame` around `el.focus()`. Full record: `V09994_BUG_FIXES.md` BUG-08. |

---

## SAFEHELM — CONCEPT GAUGE (S77–S78 2026-05-11)

**Status:** Concept design complete. Forum article ready. Community interest gauge pending publication.

| # | Item | Status |
|---|------|--------|
| SH-1 | Forum article finalized (Navigation & Charts) — ready for posting | `[~]` Awaiting user post |
| SH-2 | Community feedback on COLREGs compliance gap | `[ ]` Pending article publication |
| SH-3 | Phase 1 (Shadow Mode) design approval — if community interest confirmed | `[ ]` Blocked on SH-2 |

---

## D3K-LITE — INTEREST GAUGE (NEW — 2026-05-11 S78)

**Status:** Feasibility study complete (1,261 lines). Forum article ready. Community interest gauge pending publication.

| # | Item | Status |
|---|------|--------|
| DL-1 | Interest gauge article drafted (Navigation & Charts) — ready for posting | `[~]` Awaiting user post |
| DL-2 | Topic tags prepared (openplotter, d3k-lite, kiosk-dashboard, ai-assistant, fix-my-pi, interest-gauge, feedback-wanted, signal-k) | `[✓]` Done S78 |
| DL-3 | Community feedback on Fix My Pi, dashboard layout, mobile features | `[ ]` Pending article publication |
| DL-4 | Phase 1 build approval — if community interest validates | `[ ]` Blocked on DL-3 |

---

## OPERATOR / ON-BOAT TASKS

| # | Item | Owner | Status |
|---|------|-------|--------|
| OB-1 | UAT: 5 metric + 5 imperial users | Don (recruit) | `[ ]` Ready — S-06 fixes deployed 2026-03-17 |
| OB-2 | o-charts chart activation | Don | `[ ]` See `deployment/docs/OPENCPN_FLATPAK_OCHARTS.md` |
| OB-3 | GPS outdoor verification | Don (Pi at dock) | `[!]` Test: check Signal K position outdoors, confirm lat/lon non-zero |
| OB-4 | Camera on-boat tests | Don (on boat with cameras) | `[!]` 24hr stability + performance + storage. DHCP reservations done 2026-03-23. |
| OB-5 | Battery voltage — verify Garmin sends PGN 127508 | Don (on boat, Garmin on) | `[!]` SSH to Pi, run `curl -s 'http://localhost:8099/signalk/v1/api/vessels/self/electrical' \| python3 -m json.tool` |
| OB-6 | Pi first-boot password change flow | Don | `[ ]` Load `http://d3kos.local:3000` — should redirect to Setup wizard password pre-step |
| OB-7 | bbPress login redirect test | Don | `[ ]` Log out → go to `/staging/forum/` → must redirect to `/staging/login/` (not wp-login.php) |

---

## SIGNAL K UPGRADE (v0.9.2 — pending)

**Status:** SK v2.22.1 on Pi. All d3kOS connections unauthenticated. Upgrade to v2.23.0 when on-boat work window opens.

**Step 1 — Security check on Pi (before anything else)**
- [ ] Read `~/.signalk/settings.json` — look for `"strategy": "./tokensecurity"`
  - If `dummysecurity` or missing: security off → skip Steps 2 & 3
  - If `tokensecurity`: check `allow_readonly` and decide if token work needed

**Step 2 — Token auth in Python + JS (conditional — only if security enabled)**
- [ ] Generate long-lived token: `signalk-generate-token -u <admin> -e 0 -s ~/.signalk/security.json`
- [ ] Store in `/opt/d3kos/config/signalk.env` — never hardcode
- [ ] `signalk_client.py`: add `Authorization: Bearer <token>` header to all REST calls
- [ ] `instruments.js`, `boatlog-engine.js`, `engine-monitor.html`: append `?token=<token>` to WS URL

**Step 3 — Fix `remote_api.py` port bug (do regardless)**
- [ ] Change `SIGNALK_API = 'http://localhost:3000/signalk/v1/api/'` → `http://localhost:8099/signalk/v1/api/`

**Step 4 — Upgrade SK on Pi**
- [ ] `cd ~/.signalk && npm install signalk-server@2.23.0`
- [ ] `sudo systemctl restart signalk`
- [ ] Verify: `curl http://localhost:8099/signalk`

**Step 5 — Verify AvNav patch survives**
- [ ] Confirm `signalkhandler.py` line 1580 still reads `/v2/api/` post-upgrade
- [ ] `curl http://localhost:8080` — confirm AvNav loads and charts render

**Step 6 — Smoke test (Don confirms on Pi screen)**
- [ ] Instruments panel — live SOG, COG, position
- [ ] Engine monitor — live data or graceful "no NMEA2000"
- [ ] Boat log engine capture fires correctly
- [ ] AvNav charts visible
- [ ] Settings §12 Signal K status shows LIVE

---

## v0.9.3 WEBSITE — PHASE 4 PRE-LAUNCH

| # | Item | Status |
|---|------|--------|
| AD | Architecture flow diagram (Part 7A) | `[ ]` |
| PH4-1 | Proper live deploy plan | `[ ]` To be scoped when v0.9.4.1 complete |
| PH4-2 | Post-push smoke test (all pages, AI widget, Stripe Fix My Pi) | `[ ]` |
| PH4-3 | Rotate Gemini API key | `[ ]` |
| PH4-4 | Change FTP password for d3kos@atmyboat.com | `[ ]` |
| PH4-5 | **UPDATE cPanel CRON JOBS (M15-D)** — `offline-check.php` + `fix-my-pi-timeout.php`: change `/staging/wp-content/...` → `/wp-content/...` | `[ ]` |
| SEO | 2E — SEO (Yoast, sitemap, Bing Webmaster) | `[ ]` Deferred to post-launch |
| FOOT | Footer not rendering correctly | `[!]` Root cause unknown — Don said "move on" 2026-03-25. Deferred. |
| FMP | Fix My Pi end-to-end automation | `[ ]` Spec: `ATMYBOAT_BUILD_REFERENCE.md` Part 17.4. Pi watchdog + systemd timer + PHP endpoints + 30-min refund + expectation disclaimer. |
| COMP | `/compatible` — engine checker page | `[!]` Blocked on Don's compatibility data list |
| CA4 | Document credential vault — ~20 fields still `[DON TO PROVIDE]` (cPanel pw, prod DB pw, WP admin, Stripe live keys, email) | `[~]` **IN PROGRESS S27c** |
| OP | Create `mobile/config.php` from template — add DB credentials, Stripe keys, Gemini key, API key | `[ ]` |
| OP | Run `setup/install-pages.php?key=<key>` once → delete | `[ ]` |
| OP | Install MailPoet plugin on staging | `[ ]` |

---

## v0.9.3 WEBSITE — POST-LAUNCH

| # | Item | Status |
|---|------|--------|
| PL-1 | Monitor Gemini API usage (free tier: 20 req/day) | `[ ]` |
| PL-2 | UAT with real boaters (ages 45–70) | `[ ]` |
| PL-3 | Node-RED flow activation — replace placeholder URL, create cloud-credentials.json, enable 3 flows | `[ ]` See Part 8A §8A.2 in archive |
| PL-4 | Re-enable Node-RED community flows when API endpoints are live | `[ ]` Blocked on v0.9.3 live |
| PL-5 | End-to-end test: community sharing ON → community map shows dot | `[ ]` Blocked on v0.9.3 live |
| PL-6 | page-manual.php — Don creates GitHub release with PDF; update PDF URL in page-manual.php | `[ ]` Don action |
| PL-7 | Community map end-to-end: enable map_sharing in usermeta → wait for Pi sync → dot appears | `[ ]` Testable on staging |

---

## Pi — OPEN ITEMS

| # | Item | Status | Detail |
|---|------|--------|--------|
| DEP13 | Pi AODA compliance pass | `[~]` **Awaiting Don go-ahead** | Track A (contrast ~50 selectors), Track B (skip links/h2/aria-labels on 13 templates), Track C (font floor). S51 plan ready. Static pages done S8. Flask templates not done. |
| DEP17 | Pi title bar text color — text still black | `[~]` **OPEN** | Fix: `window.active.label.text.color: #ffffff` in `/home/d3kos/.config/labwc/themerc-override`. One-line change. |
| DEP20 | Dual dashboard source-of-truth audit | `[!]` **OPEN S52** | `deployment/d3kOS/dashboard/` and `deployment/v0.9.4/pi_source/` still diverge. Partial sync done S52. Full audit needed — any new page must be added to BOTH dirs. |
| PM4 | Predictive maintenance ML models (5 targets) | `[ ]` Deferred — needs on-water training data |
| PM7 | Predictive maintenance advanced automation | `[ ]` Deferred — T3/Phase 5 |
| RAG | RAG re-ingest after each Pi deployment | `[ ]` Recurring — `cd /home/boatiq/rag-stack && .venv/bin/python3 helm_os_ingest.py --collection source` |
| SK-FW | signalk-forward-watch: add download-on-first-run | `[ ]` |
| SK-FW | signalk-forward-watch: test on OpenPlotter | `[ ]` |
| SK-FW | signalk-forward-watch: fix README (Step 2 model download now unnecessary) | `[ ]` |

---

## INTEGRATION TESTS (v0.9.4.1 — require live site)

| # | Test | Expected result | Status |
|---|------|-----------------|--------|
| T1 | Pi sync → website: POST to data-ingress.php with real API key | 200 OK, engine snapshot in DB, last_sync updated | `[ ]` |
| T2 | Command round-trip: app queues `restart_service` → Pi executes → result returned | App shows "completed" within 35 min | `[ ]` |
| T3 | Community data flow: enable boat_map in Settings → position appears on /community map | Dot appears within 30 min | `[ ]` |
| T4 | Alert trigger: simulate anchor drag → immediate export → alert in DB | Alert in `amboat_alerts` within 2 min | `[ ]` |
| T5 | Find My Boat: Pi syncs position → Chart Room shows correct marker | Position on map within 35 min | `[ ]` |
| A1 | App writes command to `command-queue.php` | Depends on PWA build | `[ ]` |
| A2 | Pi command pickup loop executes and returns result | Depends on P3 | `[ ]` |
| A3 | App polls `command-queue.php` for command result | Depends on PWA build | `[ ]` |
| M8 | T1: Pi → website sync (post-launch) | Same as T1 — post-launch | `[ ]` |
| M9 | T2: Command round-trip (post-launch) | Same as T2 — post-launch | `[ ]` |
| M10 | T3: Community data flow (post-launch) | Same as T3 — post-launch | `[ ]` |
| M11 | T4: Anchor drag alert (post-launch) | Same as T4 — post-launch | `[ ]` |
| M12 | T5: Find My Boat (post-launch) | Same as T5 — post-launch | `[ ]` |

---

## FLEET MANAGEMENT — v0.9.6 Phase 4 (remaining)

| # | Item | Status | Detail |
|---|------|--------|--------|
| FM2 | Fleet map PWA screen | `[~]` Backend done, PWA Leaflet screen not built | |
| FM6 | T3 activation gate — two-device hardware test | `[~]` Backend + admin CRM done. Hardware test still pending. | |

---

## SECURITY AUDIT — v0.9.9 (gate before v1.0 full launch)

| # | Item | Status | Detail |
|---|------|--------|--------|
| SA4 | External penetration test | `[ ]` **Don to hire firm** — network attacks, privilege escalation, API fuzzing, rate limiting |
| SA5 | Fix all critical/high vulnerabilities from pen test | `[ ]` Blocked on SA4 |
| SA7 | Penetration test certificate | `[ ]` Blocked on SA4 |

---

## v1.1 MULTI-LANGUAGE (deferred)

| Layer | Item | Status |
|-------|------|--------|
| Layer 0 | Noto fonts for Arabic/CJK/Greek/Cyrillic, Arabic RTL, professional translation review | `[ ]` |
| Layer 1 | Whisper-small STT (99 languages) | `[ ]` Not started |
| Layer 2 | Per-language Piper TTS models | `[ ]` Not started |
| Layer 3 | AI response language injection | `[x]` Done |
| Layer 4 | Per-language virtual keyboards, Arabic RTL | `[ ]` Not started — fix BUG-08 first |
| Layer 5 | Boat log in user's language | `[ ]` Not started — auto after Layers 1+4 |

---

## RESEARCH PAPER & AAO DATA

| # | Item | Owner | Status |
|---|------|-------|--------|
| PAPER-4 | Verify ai_model_version column in session_sqs_dataset_v2.csv (all 36 rows show placeholder "claude-sonnet-4") | Don | `[ ]` |
| PAPER-5 | Document remaining 10 excluded sessions in session_exclusion_log.csv | Don/Claude | `[ ]` |
| PAPER-6 | Phase 1 research data collection — record tasks_planned/completed/governing_doc_version at every session close | Claude | `[ ]` **Active — starts now** |
| PAPER-7 | Submit Governing_the_AI_Productivity_Promise_v3.3 to Research Policy | Don | `[ ]` SSRN first, then journal |

---

## AAO DATA COLLECTION SYSTEM — Phase 1 (awaiting Don go-ahead)

**Architecture:** `aao-methodology-repo/data-collection/ARCHITECTURE.md` v1.1
**Deploy target:** `atmyboat.com/research/`

| # | Task | Owner | Status |
|---|------|-------|--------|
| DC-02 | UpdraftPlus backup before DB changes | Don | `[ ]` **Prerequisite** |
| DC-03 | Confirm `admin@atmyboat.com` deliverability on HostPapa | Don | `[ ]` |
| DC-04 | MySQL tables: `aao_contributors` + `aao_sessions` | Claude | `[ ]` |
| DC-05 | `aao-collector.py` — Python stdlib, reads `aao_api_key:` from CLAUDE.md | Claude | `[ ]` |
| DC-06 | `aao-register.php` + registration form | Claude | `[ ]` |
| DC-07 | `aao-submit.php` — validation, dedup, IP hash, storage | Claude | `[ ]` |
| DC-08 | `aao-data.php` — public aggregate JSON API | Claude | `[ ]` |
| DC-09 | `atmyboat.com/research/index.html` — landing page + download link | Claude | `[ ]` |
| DC-10 | `atmyboat.com/research/privacy/` — privacy policy page | Claude | `[ ]` |
| DC-11 | CLAUDE.md template update in `aao-methodology-repo` | Claude | `[✓]` Done S81 — 3-tier Classification Gate, Atomic Spec, Watchdog, provider-agnostic |
| DC-12 | `commands/session-close.md` — collector reminder line | Claude | `[ ]` |

---

## MISC OPEN

| # | Item | Status |
|---|------|--------|
| AAO-6 | Initialize LLM-Wiki for Helm-OS | `[ ]` Awaiting Don instruction — say "initialize the wiki" to activate |
| AAO-7 | Update `aao-methodology-repo/SPECIFICATION.md` to formally add Section 23 — Three-Tier Agentic Model / Adaptive Governance Specification Principle (v1.9 README/CLAUDE.md updated S81; SPECIFICATION.md not yet updated) | Claude | `[ ]` |
| BUG-06 | PWA tier still shows T1 | `[!]` Operator action: (1) Ctrl+Shift+R hard refresh, (2) log out → log in as admin@atmyboat.com (T3), (3) check localStorage `amboat_tier`. Cannot diagnose further without operator confirmation. |
| SQS | SQS calculation block in CLAUDE.md session-close | `[ ]` Already running correctly — confirm and close |
| v0.9.4.1 | Blocked on Phase 4 live push for public availability. Code complete on staging. | `[ ]` |
| v0.9.9 | Security audit gates v1.0 full launch — see SA4-SA7 above | `[ ]` |
| v1.1 | CJK keyboard, self-hosted STUN coordination server | `[ ]` Future |

---

---

## PART 18 — SafeHelm Collision Avoidance Module (S76 2026-05-11)

**Design document:** `deployment/docs/SAFEHELM_DESIGN.md`
**Target:** `github.com/SkipperDon/d3kOS/services/safehelm/`
**Status:** Design complete. Build not started.

| # | Task | Status | Notes |
|---|------|--------|-------|
| SH-01 | Resolve camera range estimation | `[~]` PARTIAL | S79: WiBoat WiFi CSI solves range for non-AIS targets in integrated system (range + bearing from CSI). Camera-only mode remains bearing-only. Integrated SafeHelm+WiBoat resolves L1 limitation — camera targets fuse with WiBoat contacts when within ±15° bearing + ±50m range. No longer blocks Phase 1 start. |
| SH-02 | Add Rule 12 (sailing vessels) to COLREGs classifier | `[ ]` | Port/starboard tack, windward/leeward. Requires wind angle input from NMEA. |
| SH-03 | Add Rule 19 (restricted visibility) mode | `[ ]` | Fog/night detection, speed reduction advisory, fog signal output, suspend Rules 12–18. |
| SH-04 | Night / low-light camera fallback | `[ ]` | Auto-switch to AIS_ONLY when camera confidence → 0 after sunset or in fog. |
| SH-05 | Add Rule 18 vessel type hierarchy | `[ ]` | Use AIS vessel type field. Power→Sailing→Fishing→RAM→NUC pecking order. |
| SH-06 | Spec AIS-camera fusion algorithm | `[ ]` | Association threshold, bearing/position proximity matching, duplicate suppression. |
| SH-07 | Virtual MMSI expiry logic | `[ ]` | Remove ghost vessels from Signal K when camera loses track. TTL-based cleanup. |
| SH-08 | Startup health check | `[ ]` | Verify Signal K reachable, GPS fix, AIS receiving before operating. Alert captain if not. |
| SH-09 | Connect depth sounder to Safety Envelope | `[ ]` | Pipeline from SK depth path into `shallow_water_depth_m` check. |
| SH-10 | Incident logging spec | `[ ]` | File, format, fields, review UI. Required for post-incident verification. |
| SH-11 | Phase 1 Shadow Mode build | `[ ]` | Log-only — no alarms, no autopilot. CPA/TCPA + COLREGs classifier working. |
| SH-12 | Phase 2 Advisory Mode build | `[ ]` | Voice alerts via ai_bridge + AvNav widget. Sea trial validation. |
| SH-13 | Phase 3 Conflict Solver build | `[ ]` | Multi-vessel graph, non-compliant vessel detection, defensive mode. |
| SH-14 | Phase 4 pypilot integration | `[ ]` | Only after Phase 2 sea trial confirms advisory accuracy. High risk — do not rush. |

---

## PART 19 — WiBoat + SafeHelm Integrated System (S79 2026-05-12)

**Architecture document:** `C:\Users\donmo\Downloads\wiboat\WIBOAT_SAFEHELM_INTEGRATED_ARCHITECTURE.md`
**Status:** Architecture complete. Phase 1 build not started.
**Relationship to PART 18:** WiBoat is the sensor layer that integrates with SafeHelm. Architecture supersedes SAFEHELM_SYSTEM_SPEC.md for ports, MMSIs, and API formats.

| # | Task | Status | Notes |
|---|------|--------|-------|
| WB-01 | Assign static IP to WiBoat RPi 4B on boat router | `[!]` OPERATOR ACTION | Replace 192.168.1.WB placeholder in all config files. Must happen before any Phase 1 code is written. |
| WB-02 | Procure WiBoat Phase 1 hardware | `[ ]` | RPi 4B 4GB, 2× ALFA AWUS036NH, 2× 12dBi omni antennas, LMR-400, DC-DC converter, Heltec V3. See BOM in architecture doc §16. |
| WB-03 | Flash RPi 4B with Bullseye 32-bit, lock kernel 5.10 | `[ ]` | Do NOT run apt upgrade after flash. Kernel must stay 5.10 for nexmon_csi compatibility. |
| WB-04 | Install nexmon_csi via picsi, confirm CSI packets on UDP :5500 | `[ ]` | Phase 1 gate G1.1 depends on this. |
| WB-05 | Implement wiboat-processor.py (range only) + WebSocket :8766 | `[ ]` | Phase 1 WiBoat deliverable. IFFT ToF range, Kalman tracker, contact JSON schema. |
| WB-06 | Connect WiBoat to SafeHelm via LAN — confirm contact feed received | `[ ]` | Phase 1 integration gate G1.3. |
| WB-07 | Flash Heltec V3, confirm Meshtastic LoRa operation | `[ ]` | Phase 1 gate G1.4. |
| WB-08 | Phase 1 acceptance gates (all 5) | `[ ]` | G1.1–G1.5 per architecture doc §10. Must all pass before Phase 2. |
| WB-09 | Phase 2: 2-antenna bearing (MUSIC AoA), marine environment test | `[ ]` | Gate: ±20° at 100m, <30% FP fibreglass at 100m. |
| WB-10 | Phase 2: SafeHelm advisory mode + WiBoat CPA integration | `[ ]` | Voice alerts, AvNav widget, WiBoat contacts as 998xxxxxx AIS targets. |
| WB-11 | Phase 2 sea trial (4-hour advisory-only passage) | `[ ]` | HARD GATE: zero false CRITICAL alarms, captain endorsement required. |
| WB-12 | Phase 3: 4-antenna array, full 360° bearing, batman-adv mesh | `[ ]` | Removes port/starboard ambiguity. Cooperative contacts from nearby WiBoat boats. |
| WB-13 | Migration Gate 3: bench single-box validation on RPi 5 | `[ ]` | Non-16k kernel + all d3kOS services + WiBoat simultaneously. Must pass before Phase 4. |
| WB-14 | G3.5 calendar gate: one full sailing season in Phase 2 advisory mode | `[ ]` | HARD GATE — cannot be bypassed. Phase 4 autopilot blocked until complete. |
| WB-15 | Phase 4: single-box consolidation (ALFA adapters to RPi 5) | `[ ]` | Migration Gate 4. 4-hour shadow run at anchor before sea use. |
| WB-16 | Phase 4: SafeHelm autopilot (pypilot integration, sea trial) | `[ ]` | Only after WB-14 + WB-15. High risk — see architecture doc §13. |

---

*Completed work archived in: `PROJECT_CHECKLIST_ARCHIVE.md`*
*Do not delete entries — update status or move to archive only.*
