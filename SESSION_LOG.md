# d3kOS Session Log

---

## Session 2026-03-04 (Part 10)
**Goal:** Fix Pi post-installation boot failures — SignalK, GPS, AIS, export services

**Completed:**
- Fixed SignalK not starting on boot (root cause: systemd ordering cycle)
  - `d3kos-timezone-setup.service` had `After=signalk.service` creating a circular dependency with `d3kos-first-boot.service` (`Before=signalk.service`)
  - Systemd broke the cycle by deleting SignalK's start job — it never ran at boot
  - Fix: removed `signalk.service` from timezone-setup `After=` line (only needs `network-online.target`)
- Fixed GPS and AIS not working in SignalK
  - Root cause: `gps` and `ais` pipedProviders in `~/.signalk/settings.json` both had `"enabled": false`
  - Fix: set both to `"enabled": true`; confirmed `gps.GP`, `ais.GP`, `ais.II` all active
- Fixed export services failing at boot (`d3kos-export-boot`, `d3kos-export-daily`)
  - Root cause: `/var/log/d3kos-export-boot.log` and `d3kos-export-daily.log` did not exist; `d3kos` user has no write permission to create files in `/var/log/`
  - Fix: created log files with correct ownership on Pi; updated source scripts to `touch "$LOG_FILE"` at startup with `/tmp/` fallback
- Installed `chrony` to replace `systemd-timesyncd` for NTP time sync
  - GPS time sync via gpsd SHM/SOCK left for future work (gpsd/chrony SHM permission model requires more investigation); chrony synced to internet NTP pool
- Rebooted and verified clean boot: SignalK, gpsd, rtl-ais, export-boot all active; no ordering cycles

**Decisions:**
- Removed `signalk.service` from timezone-setup `After=` — timezone detection only needs network, not SignalK running
- GPS pipedProviders were disabled (likely turned off during a previous troubleshooting session or install); re-enabled
- Export log fallback to `/tmp/` if `/var/log/` write fails — makes scripts self-healing on fresh installs
- Left chrony on internet NTP for now; GPS time sync deferred (offline-at-sea use case, not urgent)

**Pending:**
- GPS time sync via gpsd SHM → chrony (for offline-at-sea use; gpsd runs as `gpsd` user, SHM 0 owned by root/600 perms — needs permission resolution)
- Export-daily race condition at boot: Persistent=true timer fires immediately if 3AM was missed; curl fails with code 7 if tier-api not fully listening yet — needs small retry loop in script

---

## Session 2026-03-04 (Part 9)
**Goal:** Fix TrueNAS Ollama agent restart loop + build independent verify agent pipeline

**Completed:**
- Fixed `ollama-agent.py` restart loop on TrueNAS VM (`192.168.1.103`):
  - Bug: hung detection fired when `inference_ok=False AND models non-empty` even when `PROBE_MODEL=""` (probing disabled)
  - Fix: added `and PROBE_MODEL` guard — line 334 in `/opt/ollama-agent/ollama-agent.py`
  - Result: `status: healthy`, `restart_count: 0`, stable
- Benchmarked TrueNAS VM Ollama inference:
  - `qwen2.5-coder:14b`: 0.02 t/s — "say hello" took 264s — unusable
  - Root cause: bhyve VM memory bandwidth throttled by ZFS ARC; `cpu cores: 2` in VM
  - `qwen2.5-coder:1.5b` pulled (986MB), 14b removed — RAM freed from 162MB to 12GB free
  - `qwen2.5-coder:1.5b`: 0.03 t/s — still unusable; hardware constraint, not fixable with software
- Built **TrueNAS Verify Agent** (`deployment/scripts/verify_agent.py`):
  - Architecture: TrueNAS runs the HTTP service, inference routed to workstation GPU
  - `d3kos-verify-agent.service` deployed on `192.168.1.103:11436`, enabled, auto-start
  - `POST /verify` → sends code + instruction to `qwen3-coder:30b` (workstation) for independent review
  - `GET /health`, `/report`, `/stats` — all reachable from laptop
  - Two-role model: generator generates, verifier critiques (different prompt, different context, independent inference)
- Wired verify agent into `ollama_execute_v3.py`:
  - `VERIFY_URL`, `VERIFY_ENABLED`, `VERIFY_TIMEOUT` constants at top of file
  - `call_verify()` called after structural validation in both REPLACE_EXACT and standard modes
  - FAIL → `Verify:` issue added to block, enters correction loop
  - Verifier offline → `None`, pipeline continues (non-blocking)
  - Summary report now fetches verify stats from TrueNAS endpoint
- `helm_os_context.md` updated with two-step pipeline section — Ollama now knows its GENERATOR role and that a verifier reviews its output
- `PROJECT_CHECKLIST.md` updated — verify agent section added as complete
- `MEMORY.md` updated with TrueNAS VM constraints and verify agent details
- `deployment/docs/VERIFY_AGENT.md` written — full architecture, endpoints, configuration, management
- Commits: `a607e04` (verify agent + executor), subsequent doc commits

**Decisions:**
- TrueNAS VM runs the verify SERVICE but not the model — bhyve + ZFS ARC memory contention is a permanent hardware constraint; routing inference to workstation GPU is the correct architecture
- Same model (qwen3-coder:30b) for both roles is valid — generator and verifier are independent inference calls with different prompts and context windows; reviewer has no memory of generation
- Verifier is non-blocking: if TrueNAS is offline the pipeline continues; prevents single point of failure
- `VERIFY_ENABLED = True` at top of executor — can be toggled False to bypass globally

**Ollama:** 0 executor calls (infrastructure session); 2 TrueNAS test calls (timed out); verify agent test calls via workstation GPU

**Costs:**
| Source | Metric | Cost |
|--------|--------|------|
| Claude API | check console.anthropic.com → Usage → 2026-03-04 | TBD |
| Ollama (qwen3-coder:30b) | verify agent tests | $0.00 |
| Session total | | TBD |

**Pending:**
- Re-ingest `helm_os_source` RAG collection (helm_os_context.md updated)
- Test full executor run end-to-end with verify agent in the loop
- Test camera assign UI on Pi touchscreen
- DHCP / static IP confirmation for cameras

---

## Session 2026-03-04 (Part 8)
**Goal:** Deploy camera-position-assignment feature + build Ollama model benchmark

**Completed:**
- camera-position-assignment deployed to Pi (all 3 phases):
  - `POST /camera/assign` endpoint in `camera_stream_manager.py` — validates position, clears conflicts, writes cameras.json
  - `settings.html` — each camera card shows position (color-coded orange=unassigned, green=assigned) + Bow/Stern/Port/Starboard/Clear buttons
  - `marine-vision.html` — `renderSelector()` now shows direction labels (Bow/Stern/Port/Starboard); falls back to camera names if no positions set
  - `/camera/list` updated to return `position` field for each camera
  - cameras.json updated on Pi: `position: bow/stern` added to existing cameras
  - cameras.json ownership fixed to `d3kos` user (was root — service couldn't write at runtime)
  - Commits: `dbff06e`, `7508cdf`
- Executor improvements committed:
  - `REPLACE_EXACT` mode and `--skip-ollama` mode ticked off checklist
  - Executor END_LINE substring match bug documented: `str.find("    }")` matches inside `      }` — phase 3 marine-vision applied manually with Edit tool instead
- `benchmark.py` built (`deployment/scripts/benchmark.py`):
  - 3 test cases: camera-assign-api (Python), camera-vision-buttons (JS), simple-instruction-follow
  - 5 scoring dimensions: syntax (20), keywords (20), forbidden patterns (20), variable names (20), similarity to reference (20)
  - Results saved to `benchmark_results.json` for tracking over time
  - Commit: `35c386b`
- Model benchmark run — deepseek-coder-v2:16b pulled, tested, removed:
  - qwen3-coder:30b: **97/100** — executor default confirmed
  - deepseek-coder-v2:16b: 70/100 — fails no-fences instruction, syntax drops to 0
  - deepseek removed from workstation (freed 8GB)

**Decisions:**
- `--skip-ollama` with spec code blocks is the reliable path for complex multi-block JS — Ollama semantic drift not worth retrying
- executor END_LINE must use line content unique enough not to appear as substring in indented lines; bare `    }` is unsafe — use the line before the closing brace instead
- qwen3-coder:30b stays as executor model — 27pt quality gap over deepseek justifies the extra 13s/call and 9GB
- cameras.json must be owned by `d3kos` (not root) for the Flask service to write position assignments at runtime
- WSL2 172.x.x.x is the auto-created `vEthernet (WSL)` adapter — not a concern, not deployed by us

**Ollama:** 0 live calls this session (all phases used --skip-ollama); benchmark: 6 calls total (3 tests × 2 models)

**Costs:**
| Source | Metric | Cost |
|--------|--------|------|
| Claude API | check console.anthropic.com → Usage → 2026-03-04 | TBD |
| Ollama (qwen3-coder:30b) | 3 benchmark calls | $0.00 |
| Ollama (deepseek-coder-v2:16b) | 3 benchmark calls | $0.00 |
| Session total | | TBD |

**Pending:**
- Re-ingest `helm_os_source` RAG collection (3 Pi files updated this session)
- Test camera assign UI on Pi touchscreen
- DHCP / static IP confirmation for cameras (stay on same IPs across reboots)

---

## Session 2026-03-03 (Part 6)
**Goal:** Build v0.9.2 Multi-Camera System + fix nginx + fix fish detector

**Completed:**
- v0.9.2 Multi-Camera System — full implementation deployed:
  - `cameras.json` registry at `/opt/d3kos/config/` — bow (10.42.0.100) + stern RLC-820A (10.42.0.63)
  - `camera_stream_manager.py` rewritten — per-camera frame-grabber threads, graceful offline handling, all original endpoints backwards-compatible
  - New endpoints: `/camera/list`, `/camera/frame/<id>`, `/camera/switch/<id>`, `/camera/grid`
  - `marine-vision.html` updated — camera selector buttons, Grid View toggle, all-cameras status cards
  - Stern RLC-820A password: `d3kos2026$` — had to URL-encode as `%24` (RTSP URI parser treats `$@` as shell variable, dropping the `@`)
  - Both cameras live: bow frame 48KB, stern frame confirmed streaming
  - Commits: `be236c5`, `9478f1d`
- Camera count decision: stay at 2 for now (bow + stern), add cameras 3 & 4 later — no code changes needed, just add to `cameras.json`
- nginx: restored all 18 service proxy location blocks (commit `52ceee0`)
  - Root cause: Part 5 nginx corruption fix restored a backup that only had `/remote/` — all other proxies were silently lost
  - Every API call from every page was returning 404 from nginx
  - Added proxies for: `/ai/` `/upload/` `/history/` `/manuals/` `/camera/` `/detect/` `/notify/` `/export/` `/license/` `/tier/` `/simulator/` `/healing/` `/network/` `/api/preferences` `/api/timezone` `/api/backup/` `/api/boatlog/` `/gemini/` `/remote/`
  - `/network/` uses trailing-slash proxy_pass to strip prefix (service routes at `/status`, `/wifi/*`, `/hotspot/*`)
- Fish detector: restarted manually — had been dead since Feb 28 due to dependency failure (camera stream was down when boot ran). Now active: YOLOv8n + 483-species EfficientNet classifier

**Decisions:**
- `$` in RTSP password must be percent-encoded as `%24` in URL — libav RTSP parser interprets `$@` as a variable substitution
- `sites-enabled/default` on this Pi is a flat file copy, not a symlink to `sites-available/` — must write both or write directly to sites-enabled
- Camera 3 & 4 deferred to future purchase — system designed to accommodate any number, zero code changes required
- nginx proxy for `/network/` strips prefix (trailing `/` in proxy_pass) — network-api.py routes at `/status` not `/network/status`

**Ollama:** 0 calls (all work done directly)

**Costs:**
| Source | Metric | Cost |
|--------|--------|------|
| Claude API (this session) | check console.anthropic.com → Usage → 2026-03-03 | TBD |
| Ollama (qwen3-coder:30b) | 0 calls | $0.00 |
| **Session total** | | **TBD** |

**Pending:**
- DHCP reservations for camera IPs (dnsmasq — cameras currently on dynamic IPs, should be reserved)
- 24-hour stability test with both cameras streaming
- Physical mount decision for stern RLC-820A
- Re-ingest `helm_os_source` RAG collection (camera_stream_manager.py changed significantly)

---

## Session 2026-03-03 (Part 5)
**Goal:** Fix voice rule overmatch + build AI Action Layer + Remote Access API + Tailscale

**Completed:**
- Fix: `classify_simple_query()` rule overmatch — "what causes white smoke at high speed" was routing to 'speed' rule
  - Added `diagnostic_intents` guard (why/what causes/explain/smoke/vibrat/overheating/etc.) before any pattern check
  - Tightened all patterns from single-word to multi-word phrases:
    - `'speed'` → `['what is my speed', 'current speed', 'how fast am i', 'sog', ...]`
    - `'temperature'` → `['coolant temp', 'engine temp', 'what is the temperature', ...]`
    - `'battery'` → `['battery voltage', 'battery level', 'system voltage', ...]`
    - all other categories similarly tightened
  - 15/15 classification tests pass. Committed `680a795`
- AI Action Layer (v0.9.5): three whitelisted voice actions in `query_handler.py`
  - `classify_action_query()` — detects action intent before simple/Gemini routing
  - `execute_action()` — dispatcher for 3 actions
  - `log_note`: "log a note [text]" / "note that [text]" → appends to `maintenance-log.json`
  - `log_hours`: "log engine hours [N]" → logs hours entry to maintenance-log.json
  - `set_fuel_alarm`: "set fuel alarm to [N] percent" → updates `user-preferences.json`
  - 10/10 tests pass. Deployed to Pi. Committed `c68d8c6`
- Remote Access API (v0.9.5): `remote_api.py` Flask service on port 8111
  - `GET /remote/health` — unauthenticated
  - `GET /remote/status` — all SignalK metrics (engine, nav, systems) with API key auth
  - `GET /remote/maintenance` — last 20 maintenance log entries
  - `POST /remote/note` — add maintenance note from phone
  - Systemd service `d3kos-remote-api.service` enabled and active
  - Nginx proxy `/remote/` → `localhost:8111`
  - API key generated and stored in `api-keys.json`
  - `REMOTE_ACCESS_SETUP.md` written (Tailscale, LAN, port-forward options)
  - Committed `f93f312`
- Tailscale installed on Pi (v1.94.2) and authenticated — IP: `100.88.112.63`
  - Full d3kOS web UI accessible remotely at `http://100.88.112.63`
  - Tested and confirmed working on phone over cellular
  - Committed `97c90f0`
- `helm_os_source` RAG collection re-ingested (57 chunks — includes new `remote_api.py`)
- PROJECT_CHECKLIST.md updated throughout

**Decisions:**
- Diagnostic intent guard approach (not just pattern tightening) — catches open-ended questions reliably regardless of which sensor keywords appear
- Action Layer uses append-only JSON (not SQLite) for maintenance log — simpler, human-readable, easy to inspect
- Remote API auth: key required for /status and /maintenance; health is open — phone can test connectivity without key
- Remote API nulls when engine off — correct behavior, sensors unavailable at dock
- Tailscale chosen for remote access — no port forwarding required, works on cellular
- **UX note:** Tailscale setup has friction — requires separate app install, must be running in background, and URL syntax (`http://` prefix) is not obvious to non-technical users. Acceptable for a single-owner boat but worth revisiting if d3kOS is ever distributed. A simpler alternative for future consideration: a cloud-hosted status page that the Pi pushes data to (no VPN needed on phone).

**Ollama:** 0 calls (all code written directly)

**Costs:**
| Source | Metric | Cost |
|--------|--------|------|
| Claude API (this session) | check console.anthropic.com → Usage → 2026-03-03 | TBD |
| Ollama (qwen3-coder:30b) | 0 calls | $0.00 |
| **Session total** | | **TBD** |

**Pending:**
- v0.9.3 Multi-Camera System (hardware blocked: cameras not purchased)
- WebSocket real-time data push (low priority — polling /remote/status is adequate for now)
- Consider push-based remote status (Pi POSTs to cloud endpoint) as simpler phone alternative to Tailscale

---

## Session 2026-03-03 (Part 4)
**Goal:** Ollama executor improvements + build project RAG knowledge base

**Completed:**
- Fix 1 applied to v0.9.4 executor: accept `ACTION: AFTER/BEFORE` as aliases (v0.9.2 had this from Part 3)
- Fix 2 applied to both executors: function parameters added to `declared_in_code` in `check_invented_vars()`
  - Python: `def foo(self, param1, param2=default, *args)` → all params added to declared set
  - JS: `function foo(a, b, c)` and arrow `(a, b) =>` → params added to declared set
  - Resolves `isError` false-positive from v0.9.4 settings phase
- Fix 3 applied to both executors: tightened FIND_LINE rules in prompt
  - "Must not be a comment line (no //, #, <!--)" and "must not be a line containing only { or }"
- `helm_os_context.md`: new AI Services section — ports 8097/8099/8107, endpoint table, `_query_gemini()` pattern, `ai_used` constraint
- `gemini-proxy.py` docstring: `Port: 8099` → `Port: 8097`
- `ingest.py`: extended to support `.py` and `.html` files (was .md/.txt/.pdf only)
- `helm_os_ingest.py`: created with smart filtering — excludes ATMYBOAT/fish/training noise
- RAG ingestion complete (nomic-embed-text via Ollama workstation):
  - `helm_os_docs`: 1,079 chunks from 209 files (docs, specs, session history, architecture)
  - `helm_os_source`: 54 chunks from 11 files (live Pi .py + .html source)
- Committed `5522565`

**Decisions:**
- RAG split: `helm_os_docs` (corpus) vs `helm_os_source` (live code) — source is smaller and more targeted for code-context retrieval
- Chunk size 500 words; individual chunks that exceed nomic-embed-text token limit emit a 400 error but rest of file still ingests — non-fatal, acceptable
- Excluded from docs ingest: `ATMYBOAT_*`, `FISH_*`, `FORWARD_WATCH_TRAINING_*`, `WINDOWS_TRAINING_*` — unrelated to d3kOS Pi project
- Claude memory stores stable facts (IPs, ports, conventions); RAG stores searchable project corpus — complementary, not redundant

**Ollama:** 0 calls (infrastructure and tooling only)

**Costs:**
| Source | Metric | Cost |
|--------|--------|------|
| Claude API (this session) | check console.anthropic.com → Usage → 2026-03-03 | TBD |
| Ollama (qwen3-coder:30b) | 0 calls | $0.00 |
| **Session total** | | **TBD** |

**Pending:**
- Wire RAG retrieval into `ollama_execute.py`: query `helm_os_source` before each phase, prepend top-3 chunks to prompt
- Re-run `helm_os_ingest.py --collection source` after any Pi source file changes
- Rule-based pattern overmatch: "speed" in diagnostic questions triggers speed rule instead of Gemini
- v0.9.3 Multi-Camera System (blocked: 3 Reolink RLC-810A cameras not yet purchased)
- MCP filesystem server: give Claude live Pi file access without manual copy step

---

## Session 2026-03-03 (Part 3)
**Goal:** Build and deploy Gemini API integration (v0.9.4) as first real test of improved Ollama workflow

**Completed:**
- Chose Gemini API integration over Multi-Camera (Multi-Camera blocked: 3 of 4 cameras not yet purchased)
- Phase 1: `/opt/d3kos/config/api-keys.json` created (chmod 600, empty key placeholder)
- Phase 2: `gemini-proxy.py` deployed at `/opt/d3kos/services/ai/gemini-proxy.py` (port 8097)
  - Port 8099 was taken by `issue_detector.py` — moved to 8097
  - Systemd service `d3kos-gemini-proxy.service` enabled and active
  - Nginx proxy: `/gemini/` → `localhost:8097`
- Phase 3: `query_handler.py` — added `_query_gemini()` method; modified `query()` to try Gemini for complex queries with boat status context, falls back to RAG results
  - Fixed SQLite constraint: `ai_used` must be `'online'`/`'onboard'` (not `'gemini'`)
- Phase 4: `settings.html` — Gemini API section added: key input, model selector, Save + Test Connection buttons
- End-to-end test: complex query tries Gemini (503 — no key), falls back to RAG results gracefully
- Committed as `02d2694`, tagged `v0.9.4`
- `deployment/v0.9.4/` executor created with `ollama_execute.py` for future modifications
- `GEMINI_SETUP.md` written with setup instructions

**Decisions:**
- Gemini proxy port: 8097 (8099 occupied by issue_detector.py — discovered at deploy time)
- Applied query_handler and settings changes directly (not via Ollama auto-apply): Ollama's format errors were corrected manually after reviewing the correct logic from Ollama's output
- `ai_used` in conversations DB must be 'online'/'onboard' — schema constraint; Gemini = 'online'
- Static HTML insertion for Gemini settings section (Ollama tried dynamic DOM creation — spec's static HTML is cleaner)
- Gemini uses port 8097; spec said 8099 — updated context and prompts for future runs

**Ollama:** 2 phases attempted (query_handler, settings)
- `query_handler`: 1 call (98.8s) + 2 correction calls (8.5s + 14s) = 3 calls. Both blocks flagged — code logic was correct, format issues (ACTION: AFTER instead of INSERT_AFTER; FIND_LINE for routing didn't exist). Applied manually with Ollama's logic.
- `settings`: 1 call (169.7s) + 1 correction call (36.2s) = 2 calls. Failed: `isError` function parameter not recognized as declared (false positive in invented-var check). Applied correct version directly from spec.
- Total: 5 Ollama calls, ~327s, 30k prompt chars → 10k response chars. $0.00

**Costs:**
| Source | Metric | Cost |
|--------|--------|------|
| Claude API (this session) | check console.anthropic.com → Usage → 2026-03-03 | TBD |
| Ollama (qwen3-coder:30b) | 5 calls (3 primary + 2 correction) | $0.00 |
| **Session total** | | **TBD** |

**Additional fixes applied post-deploy:**
- Gemini model names: 1.5-flash no longer exists — updated to 2.5-flash/2.5-pro/2.0-flash
- Token limits: increased test 20→200, chat 256→512 (Gemini 2.5 uses tokens for internal thinking)
- Defensive response parsing: handle missing 'parts' key when thinking consumes all output tokens
- Listen duration: 3→7 seconds (3s too short after "Aye Aye Captain" plays ~4s, user had no time)
- **End-to-end test passed**: "what causes white smoke from a marine exhaust" → Gemini responded in 8s ✓

**Pending:**
- Correction loop improvement: recognize function parameters as "declared in scope" (fixes `isError` false positive)
- Executor improvement: handle `ACTION: AFTER` as alias for `INSERT_AFTER`
- v0.9.3 Multi-Camera System (hardware: purchase 3 Reolink RLC-810A cameras first)
- Rule-based pattern overmatch: "speed" pattern catches diagnostic questions (e.g. "high speed" triggers speed rule instead of Gemini)

---

## Session 2026-03-03 (Part 2)
**Goal:** Ollama workflow improvements + auto-approval setup

**Completed:**
- Auto-approval configured: `~/.claude/settings.json` + `Helm-OS/.claude/settings.json`
- `CLAUDE.md` at project root: autonomous operation, no questions policy, session report format
- `ollama_execute.py` v2: enclosing-function context, validation, auto-apply
- `deployment/docs/helm_os_context.md`: knowledge file injected into every Ollama prompt
- Ollama correction loop: flagged blocks sent back with targeted advice, one retry per block
- Parallel execution: `--parallel N` flag (phases run concurrently, Ollama queues server-side)
- Ollama call stats tracked per run (calls, chars, time) — printed in report
- Cost tracking added to session log format and CLAUDE.md

**Decisions:**
- Correction loop retries once per block — if still invalid, flag for manual review
- `tprint()` thread-safe print for parallel runs keeps output readable
- `--parallel N` default 1 (sequential); N=2-3 practical max since Ollama is single-GPU
- Cost section added to SESSION_LOG.md; Ollama = $0 always; Claude = check console

**Costs:**
| Source | Metric | Cost |
|--------|--------|------|
| Claude API (this session) | check console.anthropic.com → Usage → 2026-03-03 | TBD |
| Ollama (qwen3-coder:30b) | 0 calls this session (no feature work done) | $0.00 |
| **Session total** | | **TBD** |

**Pending:**
- Test improved Ollama workflow on next major feature (v0.9.3 or v0.9.4)
- Browser verify: settings.html toggle → dashboard.html shows matching units
- v0.9.3 Multi-Camera System
- v0.9.4 Gemini API Integration

---

## Session 2026-03-03 (Part 1)
**Goal:** Complete and deploy v0.9.2 Metric/Imperial unit conversion system

**Completed:**
- Pi SSH key-based auth set up (`~/.ssh/id_d3kos` via paramiko)
- preferences-api.py deployed (Flask, port 8107, systemd, nginx proxy at `/api/preferences`)
- units.js built — 9 unit types, 25/25 tests passing, race condition fixed
- All Pi pages patched: dashboard.html, helm.html, navigation.html, weather.html, onboarding.html, settings.html
- query_handler.py updated with unit helper methods for voice responses
- Integration tests: 15/15 passing
- Docs written: UNITS_FEATURE_README.md, UNITS_API_REFERENCE.md (local + copied to Pi)
- Committed as `e3ddbef`, tagged `v0.9.2`
- Auto-approval and session reporting workflow configured (this session)

**Decisions:**
- Focused context (±40 lines) instead of full file for Ollama prompts — full file caused Ollama to return empty output
- FIND_LINE/ACTION/CODE format instead of unified diff — diffs had malformed hunk headers
- `apt-get install python3-flask` instead of pip3 — Debian Trixie PEP 668 blocks system pip
- loadPreferenceFromBackend() only updates localStorage if API value differs — eliminates race condition where POST hadn't completed before page reload
- settings.html waits for POST to complete before `location.reload()` — not blind 1500ms timer
- index.html is launcher menu (not gauges) — spec was wrong, dashboard.html is the real gauge page

**Ollama:** 8 files processed
- Auto-applied clean: settings.html (2nd attempt), onboarding.html logic
- Corrected before apply: dashboard.html (returned object not string), helm.html (spurious `<code>` tags), query_handler.py (line number anchor instead of text), navigation.html (invented variable names), weather.html (incomplete output)
- Rejected entirely: settings.html 1st attempt (hallucinated license/tier code), index.html (wrong file — spec error)

**Pending:**
- Test improved Ollama workflow on next major feature (v0.9.3 or v0.9.4)
- Browser verify: settings.html toggle → dashboard.html shows matching units
- Cost tracking for Claude API usage across sessions
- v0.9.3 Multi-Camera System
- v0.9.4 Gemini API Integration

---
