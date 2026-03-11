# d3kOS / Helm-OS — Claude Operational Instructions

Full technical spec is at: `Claude/PROJECT_SPEC.md` — read it before making architectural decisions.

**Master document index:** `deployment/docs/DEPLOYMENT_INDEX.md` — lists every solution document, feature directory, version directory, and tool in this project. Read this before asking "where is the doc for X?" or "what was done for Y?". Update it every time something is built or fixed.

---

## Autonomous Operation

**Proceed without asking for approval.** Do the work, then report.

Exceptions — the ONLY things that require explicit user confirmation:
- Destructive and irreversible actions: `rm -rf`, dropping databases, deleting git branches
- Actions visible to others: sending emails, posting to external services
- `git push` to any remote (covered by deny rules — just don't do it)

**Do NOT ask about:**
- Which file to edit, which approach to take for routine tasks
- Whether to proceed with a next step that follows logically from the request
- Implementation details, naming choices, file locations
- "Shall I commit this?", "Would you like me to...", "Is this correct?"

If genuinely blocked with two meaningfully different paths that produce different outcomes for the user — say so once, briefly, with a recommendation. Then proceed with the recommendation if no response within the same message exchange.

---

## Git Policy

- **NEVER push to GitHub** — no `git push`, no `gh pr create`, no force push
- Commit freely, tag versions, create branches — all local only
- All work stays on this laptop until the user explicitly instructs a push
- Documentation, specs, and session logs stay local

## Security — API Keys (CRITICAL — READ EVERY SESSION)

**NEVER write a real API key, token, or password anywhere in this repo — not in docs, not in examples, not in comments.**

- Doc files, session notes, and "before/after" config examples are the highest risk — they go into commits
- Always use placeholders: `YOUR_KEY_HERE`, `sk-or-v1-***REDACTED***`, `[device_api_key]`
- Pre-commit hook at `.git/hooks/pre-commit` will block commits containing key patterns — do not bypass it
- If a key is spotted in staged files: stop, redact it, then commit
- Files that must NEVER be committed: `api-keys.json`, `cloud-credentials.json`, `.env` — covered by `.gitignore`
- Incident history: OpenRouter key `...c0f4` exposed in `doc/OLLAMA_INTEGRATION_COMPLETE_2026-02-27.md` — committed Feb 2026, caught by GitHub secret scanning, key auto-revoked. Cause: live key pasted into a doc as a config example.

---

## Ollama Workflow

- Ollama runs at `192.168.1.36:11434`, model `qwen3-coder:30b`
- SSH key for Pi (192.168.1.237): `~/.ssh/id_d3kos`
- Ollama executor: `deployment/v0.9.2/scripts/ollama_execute.py`
- Helm-OS context file for Ollama prompts: `deployment/docs/helm_os_context.md`
- Let Ollama generate code — review the output, correct where wrong, apply, deploy
- Do not write the entire solution and then ask Ollama to format it

---

## Session Reports

At the end of every session (user says "done", "that's it", "end", "wrap up", "commit and close"):

1. Write an entry to `SESSION_LOG.md` in the project root
2. Present a concise summary in chat

Format for SESSION_LOG.md entry:
```
## Session YYYY-MM-DD
**Goal:** <one line>
**Completed:** <bullet list>
**Decisions:** <bullet list — each decision with brief rationale>
**Ollama:** <N initial calls + N corrections; auto-applied X, corrected Y, flagged Z>
**Costs:**
| Source | Metric | Cost |
|--------|--------|------|
| Claude API | check console.anthropic.com → Usage → YYYY-MM-DD | TBD |
| Ollama (qwen3-coder:30b) | N calls (copy from executor report) | $0.00 |
| Session total | | TBD |
**Pending:** <bullet list>
---
```

Cost notes:
- Ollama is always $0 (local GPU at 192.168.1.36)
- Claude API cost: log into console.anthropic.com, go to Usage, filter by date
- Executor prints Ollama stats at end of run — copy the call count into the log
- Over time this builds a cost-per-feature baseline for planning

---

## Cost Control (CRITICAL)

Before every action ask: **can I do this directly without AI?**
- Direct file edits, deploys, config changes, one-line patches = just do it
- New files, complex code generation, multi-block patches = use Ollama (free, local GPU)
- Planning, spec writing, reviewing output, debugging = Claude (necessary cost)
- Never use Claude to write code Ollama can write
- Never call Ollama for trivial changes Claude can apply directly in one Edit tool call
- When in doubt: direct action first, Ollama second, Claude last

## Windows GUI Rule (HARD — applies to every instruction given to Don)

Don runs Windows. When giving Don instructions:
- NEVER mention terminal, WSL, PowerShell, SSH, SCP, bash, or any command line
- ALWAYS use click-by-click Windows Explorer and browser steps
- To access WSL files from Windows: `\\wsl.localhost\Ubuntu\home\boatiq\...` in Windows Explorer address bar
- To access files on the Pi: use the browser (Node-RED UI, d3kOS web UI) or Windows Explorer network path if SMB is available
- If something genuinely requires a command, Claude runs it silently — Don never sees or types it

## Pi Deployment

- Pi IP: `192.168.1.237`
- Pi user: `d3kos`
- SSH key: `~/.ssh/id_d3kos`
- Web root: `/var/www/html/`
- Services: `/opt/d3kos/services/`
- Config: `/opt/d3kos/config/`
- Deploy script: `deployment/v0.9.2/scripts/deploy.sh`
