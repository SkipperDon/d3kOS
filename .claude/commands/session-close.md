## Session Close — AAO Compliant

Before closing any session, complete all of the following:

1. Verify AAO checklist is complete

**Step 1B — Calculate Session Quality Metrics (AAO Section 19)**

Before writing the SESSION_LOG entry, calculate the five quality metrics for
this session. This is required at every session close without exception.

**Calculate each metric:**

SCR — Scope Compliance Rate:
- List every task in the stated sprint scope
- List every action taken outside that scope
- SCR = (in-scope tasks / total tasks) × 100

SGCR — Stop Gate Compliance Rate:
- Count every required stop gate this session
- Count how many were honored (Claude Code stopped and waited)
- SGCR = (honored / required) × 100

REC — Recovery Event Count:
- Count every git restore, git checkout, backup rollback, or manual correction
  used to undo an AI change during this session

MLS — Memory Load Success:
- 1 if /project:session-start was run and all three memory files were read
- 0 if skipped or run after work had already begun

UAC — Unauthorized Action Count:
- Count every file modified, created, or action taken outside the sprint scope
  without explicit operator instruction

**Calculate Session Quality Score:**
```
SQS = (SCR × 0.30) + (SGCR × 0.30) + (REC_score × 0.15) +
      (MLS × 0.10) + (UAC_score × 0.15)

REC_score: 100 if REC=0 | 80 if REC=1-2 | 50 if REC=3-4 | 0 if REC≥5
UAC_score: 100 if UAC=0 | 80 if UAC=1-2 | 50 if UAC=3-5 | 0 if UAC≥6
MLS as: 100 (success) or 0 (failure)
```

**Write to SESSION_LOG.md in this format:**
```
QUALITY METRICS — [date]
─────────────────────────────────────────────────────
SCR  (Scope Compliance Rate)       : [X]%
SGCR (Stop Gate Compliance Rate)   : [X]%
REC  (Recovery Event Count)        : [X]
MLS  (Memory Load Success)         : [1/0]
UAC  (Unauthorized Action Count)   : [X]
─────────────────────────────────────────────────────
SESSION QUALITY SCORE              : [X]/100
─────────────────────────────────────────────────────
```

If any metric is below its acceptable threshold, add:
`ROOT CAUSE NOTE: [metric] — [one-line explanation]`

If this is the 5th or later session, also calculate and present:
- Average SQS over the last 5 sessions
- Which metric has the lowest average (primary improvement target)
- Whether trend is improving, stable, or declining

2. List every file changed this session
3. Produce Release Package Manifest if any Pi deploy occurred
4. Write SESSION_LOG.md entry — complete, not summarised
5. Confirm no git push was executed
6. Present full session summary in chat for Don's review
