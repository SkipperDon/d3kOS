# d3kOS Session Log

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
