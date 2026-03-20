# Session Start — Memory Load and Orientation

Run this command at the beginning of every Claude Code session before any work begins.

---

## What This Command Does

Loads all persistent memory from prior sessions and orients Claude Code for
the current session. This is the read side of the memory loop — session-close
writes memory, session-start reads it.

---

## Execution Sequence

**Step 1 — Pre-flight check**
```bash
git status
```
Report working tree state. If NOT clean:
- List every uncommitted and untracked file
- STOP and wait for operator instruction before proceeding
- Do not begin any work with a dirty working tree

**Step 2 — Load MEMORY.md**
Read `MEMORY.md` fully. Summarize key stable facts in chat.
If not found: state this and continue.

**Step 3 — Load PROJECT_CHECKLIST.md**
Read `PROJECT_CHECKLIST.md` fully. List all open and in-progress items.
If not found: state this and continue.

**Step 4 — Load recent SESSION_LOG.md**
Read the two most recent entries in `SESSION_LOG.md`.
Summarize: what was done last session, what was pending, any corrections noted.
If not found: state this and continue.

**Step 5 — State session orientation**

Present this summary in chat:

```
SESSION ORIENTATION — [today's date]
─────────────────────────────────────────────────────
Last session : [date] — [one-line summary]
Open items   : [count] — [list if 5 or fewer]
Memory facts : [count of MEMORY.md entries]
Git state    : [clean / dirty — list files if dirty]
─────────────────────────────────────────────────────
Ready for    : [operator's stated task, or "awaiting task"]
```

**Step 6 — Confirm Sprint Mode status**

State whether this session is starting in Sprint Mode or Autonomous Mode:
- If operator's opening message includes "Sprint mode: ON" → confirm Sprint Mode active
- Otherwise → confirm Autonomous Mode (default), remind operator that Sprint Mode
  can be activated at any time with "Sprint mode: ON [scope]"

---

## When to Run This

- Every session, as the first action
- After `/compact` — re-run steps 2–5 to reload context lost in compaction
- When switching between projects — run `/clear` first, then this command

---

## Related Commands

- `/project:session-close` — end-of-session governance sequence (writes memory)
- `/project:methodology-check` — mid-session self-audit
- `/project:bug-fix` — TDD-enforced bug fix workflow

---

*AAO Methodology | commands/session-start.md*
*Part of the session memory loop — pairs with session-close.md*
