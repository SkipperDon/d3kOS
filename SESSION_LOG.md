# d3kOS Session Log

---

## Session 2026-03-03 (Part 5)
**Goal:** Fix voice rule overmatch + build AI Action Layer + Remote Access API

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
- PROJECT_CHECKLIST.md updated: v0.9.5 entries for Action Layer + Remote Access, overmatch fix ticked

**Decisions:**
- Diagnostic intent guard approach (not just pattern tightening) — catches open-ended questions reliably regardless of which sensor keywords appear
- Action Layer uses append-only JSON (not SQLite) for maintenance log — simpler, human-readable, easy to inspect
- Remote API auth: key required for /status and /maintenance; health is open — phone can test connectivity without key
- Remote API nulls when engine off — correct behavior, sensors unavailable at dock
- Tailscale is the recommended remote access path (no port forwarding, works on cellular); setup left to user (requires their account)

**Ollama:** 0 calls (all code written directly)

**Costs:**
| Source | Metric | Cost |
|--------|--------|------|
| Claude API (this session) | check console.anthropic.com → Usage → 2026-03-03 | TBD |
| Ollama (qwen3-coder:30b) | 0 calls | $0.00 |
| **Session total** | | **TBD** |

**Pending:**
- Install Tailscale on Pi (user step — needs Tailscale account auth, see REMOTE_ACCESS_SETUP.md)
- Re-ingest `helm_os_source` RAG collection (source files changed this session)
- v0.9.3 Multi-Camera System (hardware blocked: cameras not purchased)
- WebSocket real-time data push (lower priority — polling /remote/status is adequate)

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
