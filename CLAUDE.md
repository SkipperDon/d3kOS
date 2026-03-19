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

## Backup Naming Standard (AAO Section 18)

When asked to back up a file, use this convention. No other format.

**All backups go to `.aao-backups/` at project root. Never elsewhere.**

**Format:**
```
.aao-backups/YYYYMMDD_HHMMSS_<SESSION_ID>/mirrored/path/filename.ext.bak
```

**Rules:**
- Session folder timestamp = set at first backup of session, never changes
- All backups this session share one folder
- Mirror the full original path inside the session folder
- Append `.bak` — never replace the original extension
- Before creating: state the full backup path in chat, wait for acknowledgment
- Verify `.aao-backups/` is in `.gitignore` before creating first backup of session
  If absent: add it first, then create the backup

**Cleanup (operator-triggered only — never automatic):**
- `/aao-backup-status` — list all backups, age, purge eligibility
- `/aao-backup-purge` — list eligible files, wait for explicit confirm, delete, report
- Keep last 3 backups per original file — older ones are purge-eligible
- Never purge current session's folder
- Never delete anything without listing first and receiving explicit confirmation

## Pre-Edit Snapshot Rule (AAO Section 17 — Interactive Development Mode)

This rule implements the snapshot requirement from AAO SPECIFICATION.md Section 17.
It applies at the start of every session, before any file is modified.

**Step 1 — Check working tree (MANDATORY)**
Run `git status` before touching any file.

If clean (`nothing to commit, working tree clean`):
> State: "Working tree clean — git snapshot valid. Proceeding with [sprint scope]."

If NOT clean (uncommitted changes exist):
> STOP. List every uncommitted file in chat.
> State: "Uncommitted changes exist. I cannot proceed until these are committed or
> you explicitly acknowledge the risk and authorize me to continue."
> Do NOT proceed until the operator responds.

**Step 2 — State scope before starting**
Before any edit, state the exact list of files this sprint will touch.
This is the scope boundary. Do not modify any file not on this list.

**Step 3 — Checkpoint commits for structural edits**
If this session touches three or more files, or any structural file
(CLAUDE.md, package.json, schema files, config files, .env files), state:
> "This session touches structural files. I will stop and request a checkpoint
> commit after each logical unit of work before continuing."

**Step 4 — File-change summary before every commit**
Before requesting a commit, present:
- Every file modified this task
- A one-line description of what changed in each file
- Confirmation that no file outside the stated scope was touched

The operator must acknowledge this summary before the commit proceeds.

**Why this rule exists (AAO Section 17.7):**
Claude Code writes directly to live files. If a session goes sideways and the
working tree was not clean, the prior state of modified files is permanently lost.
Git is only a valid rollback mechanism when a clean commit exists as the baseline.
This rule ensures that baseline always exists before work begins.

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
- Ollama executor: `deployment/scripts/ollama_execute_v3.py`
- Helm-OS context file for Ollama prompts: `deployment/docs/helm_os_context.md`
- Let Ollama generate code — review the output, correct where wrong, apply, deploy
- Do not write the entire solution and then ask Ollama to format it

---

## Session Reports

At the end of every session (user says "done", "that's it", "end", "wrap up",
"commit and close"), perform the full session close sequence in order.
Do not skip steps. If a file does not need updating, state that in the chat summary.

**Step 1 — SESSION_LOG.md**
Write a new entry to SESSION_LOG.md in the project root.

Format:
```
## Session YYYY-MM-DD
**Goal:** <one line>
**Completed:**
- <bullet list>
**Decisions:**
- <each decision with brief rationale>
**Ollama:** <N initial calls + N corrections; auto-applied X, corrected Y, flagged Z>
**Costs:**
| Source | Metric | Cost |
|--------|--------|------|
| Claude API | check console.anthropic.com → Usage → YYYY-MM-DD | TBD |
| Ollama (qwen3-coder:30b) | N calls | $0.00 |
| Session total | | TBD |
**Pending:**
- <bullet list>
---
```

Never edit or delete prior entries. Append only.

**Step 2 — PROJECT_CHECKLIST.md**
Update /home/boatiq/Helm-OS/PROJECT_CHECKLIST.md:
- Mark any tasks completed this session as done
- Add any new tasks discovered during this session
- Update the status of any in-progress items
- Do not remove existing entries — update status only

**Step 3 — DEPLOYMENT_INDEX.md**
Update /home/boatiq/Helm-OS/deployment/docs/DEPLOYMENT_INDEX.md:
- Add every new file created this session (full Pi path or repo path, description, version)
- Add every new document created this session
- Add every new feature built or bug fixed
- Update version numbers if a milestone was reached
Rule: if it was built or fixed this session, it must appear in this index.

**Step 4 — CHANGELOG.md** (conditional)
Update /home/boatiq/Helm-OS/CHANGELOG.md only if a version milestone was
reached or a significant feature was completed.
Skip and state "no changelog entry needed" if not applicable.

**Step 5 — MEMORY.md**
Update /home/boatiq/.claude/projects/-home-boatiq/memory/MEMORY.md:
- Add stable patterns confirmed this session
- Add corrections to prior wrong assumptions
- Add key facts that must persist across future sessions
- Do not add transient or session-specific details

**Step 6 — BUILD_CHECKLIST.md** (conditional)
If an active feature build was in progress, update:
/home/boatiq/Helm-OS/deployment/features/<feature>/BUILD_CHECKLIST.md
- Mark completed build steps
- Note any blocked or deferred steps
Skip and state "no active build checklist" if not applicable.

**Step 7 — Feature or Solution Docs** (conditional)
If any feature document (e.g. MARINE_VISION_CAMERA_SYSTEM.md,
MARINE_VISION_CAMERA_OVERHAUL.md) was affected by work done this session,
update it to reflect current state. Version bump the document header.
Skip and state which docs were not affected if not applicable.

**Step 8 — Git Commit**
Stage and commit all session changes with a clear commit message.
Never push — local only. See Git Policy above.

**Step 9 — Chat Summary**
Present a concise summary in chat covering:
- What was accomplished
- What was deferred or blocked
- Which governance files were updated (list them)
- Which governance files were skipped and why
- Cost note (remind operator to check console.anthropic.com for actual Claude cost)
- Any decisions the operator should be aware of

The chat summary is the final step. It is not optional.

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

---

## Active Build — v0.9.2 Open Tasks

**Status:** v0.9.2 is the active version. All camera overhaul work (5 steps) is COMPLETE as of 2026-03-11.
**Camera overhaul history:** `deployment/features/camera-overhaul/BUILD_CHECKLIST.md`
**Camera overhaul spec:** `deployment/docs/MARINE_VISION_CAMERA_OVERHAUL.md`

### Remaining open tasks before v0.9.2 closes
- **On-screen keyboard**: keyboard-fix.js v2.0 deployed — needs live test confirmation on Pi
- **i18n keys**: 4 pages missing translations (Initial Setup, QR Code, Upload Manual, History)
- **Boatlog voice note**: verify record → transcribe → save → view full flow on Pi
- **WebSocket real-time push**: Remote Access page
- **UAT**: 5 metric + 5 imperial users
- **Data export**: test with unit metadata
- **CHANGELOG.md**: update for v0.9.2
- **o-charts chart activation**: Don's task — see `deployment/docs/OPENCPN_FLATPAK_OCHARTS.md`

### Camera overhaul — completed config (Pi reference)
- `/opt/d3kos/config/slots.json` — owner-defined positions
- `/opt/d3kos/config/hardware.json` — discovered hardware
- `/opt/d3kos/config/cameras.json.bak` — original backup (never delete)
- `camera_stream_manager.py` → `/opt/d3kos/services/camera/camera_stream_manager.py`
- `fish_detector.py` → `/opt/d3kos/services/camera/fish_detector.py`
- Port 8084 (camera), Port 8086 (fish detector)
