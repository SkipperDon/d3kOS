# d3kOS / Helm-OS — Claude Operational Instructions

Full technical spec is at: `Claude/CLAUDE.md` — read it before making architectural decisions.

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
2. Present a concise summary in chat covering:
   - What was built / changed
   - Key decisions made and why
   - What Ollama handled vs what required manual correction
   - Any issues encountered and how resolved
   - Files committed, tags created
   - What's pending for next session

Format for SESSION_LOG.md entry:
```
## Session YYYY-MM-DD
**Goal:** <one line>
**Completed:** <bullet list>
**Decisions:** <bullet list — each decision with brief rationale>
**Ollama:** <auto-applied X files, corrected Y files, list what was wrong>
**Pending:** <bullet list>
---
```

---

## Pi Deployment

- Pi IP: `192.168.1.237`
- Pi user: `d3kos`
- SSH key: `~/.ssh/id_d3kos`
- Web root: `/var/www/html/`
- Services: `/opt/d3kos/services/`
- Config: `/opt/d3kos/config/`
- Deploy script: `deployment/v0.9.2/scripts/deploy.sh`
