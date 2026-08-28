# ATOMIC SPEC — S135 ITEM 0.5: Commit the uncommitted working trees

**Created:** 2026-08-28 (S135, Opus / Tier 1) · **Assigned to:** Tier 3 implementer (Sonnet), next session
**Type:** repo hygiene · **Risk:** Low (local commits only) — **except** where marked ⛔
**Blocks:** nothing technically. Do it **first** anyway: until it is done, the Pre-Edit Snapshot Rule
(AAO §17) has no valid baseline for `/home/boatiq` or `atmyboat-forum`, and any session that goes
sideways loses the prior state of those files permanently.

---

## 0 — WHY THIS EXISTS

At S135 session start, `git status` was run in all three repos:

| Repo | State |
|---|---|
| `/home/boatiq/Helm-OS` | **CLEAN** — nothing to do |
| `/home/boatiq` (parent) | **DIRTY** — 3 real changes + 276 machine-noise entries |
| `/home/boatiq/atmyboat-forum` | **DIRTY** — 2 modified, 8 untracked, **one of them carries credentials** |

S134-cont closed without committing them. This spec closes that gap.

⛔ **`/home/boatiq` has no git remote and must never get one.** It holds `CREDENTIAL_VAULT.md`,
`.ssh/`, `.git-credentials`, `.claude.json`. Commit locally. Never `git push`. Never `git remote add`.

---

## 1 — PREREQUISITE CHECKS (abort on mismatch)

Run these before any `git add`. **If any check fails, stop and report. Do not adapt to what you find —
the mismatch is the finding.**

| # | Check | Expected |
|---|---|---|
| P1 | `cd /home/boatiq/Helm-OS && git status --short \| wc -l` | `0` |
| P2 | `cd /home/boatiq/Helm-OS && git rev-parse HEAD` | `3729b63b…` |
| P3 | `cd /home/boatiq && git remote -v` | **empty output** |
| P4 | `cd /home/boatiq && git diff --stat SESSION_LOG.md` | `1 file changed, 181 insertions(+)` |
| P5 | `cd /home/boatiq/atmyboat-forum && git rev-parse HEAD` | `628f0b98…` |
| P6 | `ls /home/boatiq/atmyboat-forum/.git/hooks/pre-commit` | exists, executable |

⚠ P4: if the insertion count differs, another session has written to `SESSION_LOG.md` since S135.
Read the new content before committing it — do not commit a diff you have not read.

---

## 2 — TASK A: `atmyboat-forum` (do this FIRST — it is the one with a credential hazard)

### A1 — ⛔ Protect the credential file BEFORE staging anything

`wp-content/themes/twentytwenty-child/mobile/crm-config.php` is **untracked and contains 11
credential-bearing lines** (`define(`, password, key patterns). It is **NOT** covered by the existing
`.gitignore` — that file ignores `mobile/config.php` and `inc/atmyboat-config.php`, neither of which
matches this path.

**A blanket `git add -A` stages it.** Do not run one.

Append to `/home/boatiq/atmyboat-forum/.gitignore`, under the existing
`# Server credentials — never commit` block:

```
wp-content/themes/twentytwenty-child/mobile/crm-config.php
wp-content/themes/twentytwenty-child/mobile/crm-proxy-test*.php
```

Then verify: `git status --short | grep crm-config` must return **nothing**.

⚠ The BUG-59 pre-commit hook is a backstop, not the control. Do not use "the hook would have caught
it" as a reason to skip A1. Prevention first, hook second.

### A2 — Commit the real deliverables

Stage **by explicit path only**:

```
wp-content/themes/twentytwenty-child/footer.php          (modified)
wp-content/themes/twentytwenty-child/page-manual.php     (modified)
wp-content/themes/twentytwenty-child/mobile/crm-proxy.php (new — 0 credential lines; the
                                                            Admin Console VM proxy)
.gitignore                                                (A1)
```

**Read the diff of the two modified files before committing.** They date from earlier sessions and
neither is described in any session log entry — you are committing changes whose provenance is not
recorded. State in the commit message what they actually change.

### A3 — Two items need an OPERATOR DECISION — do not act unilaterally

| Item | Why it is not yours to decide |
|---|---|
| `mobile/crm-proxy-test{,2,3,4,5,6}.php` — 6 scratch diagnostics | Ignored by A1, but **still on disk**. Deleting is irreversible; keeping clutters the theme. Ask. |
| `downloads/D3KOS_USER_MANUAL_v2.3.0.html` (70 KB, dated 2026-04-18) | A shipped user-facing artefact or a stale build? Committing publishes a possibly-obsolete manual. Ask. |

Report both in chat. Do not delete. Do not commit. Wait.

---

## 3 — TASK B: `/home/boatiq` parent repo

### B1 — Commit the three real changes, by explicit path

```
git -C /home/boatiq add SESSION_LOG.md Helm-OS atmyboat-forum
```

| Path | What it is |
|---|---|
| `SESSION_LOG.md` | +181 lines — the S134-cont entry and its five addenda, never committed |
| `Helm-OS` (gitlink) | `3c480fbf` → `3729b63b` — 40 commits of S133/S134 work |
| `atmyboat-forum` (gitlink) | `bc684745` → the new HEAD from Task A |

⚠ **Task A must be committed first**, or the gitlink still records `-dirty`.

### B1a — ⚠ S135 transcript contains FTP passwords

This session's transcript (`.claude/projects/-home-boatiq/<session>.jsonl`) contains **both FTP
passwords in cleartext** — once from a failed redaction of `CREDENTIAL_VAULT.md`, once pasted by the
operator. The parent repo tracks `.claude/`, so committing the noise tree commits the passwords.

Net-new exposure is limited: they were already cleartext in `CREDENTIAL_VAULT.md` in the same tree, and
`/home/boatiq` has no remote. **But the operator was advised to rotate both.** Before committing
anything under `.claude/`:

1. Confirm with the operator whether the FTP passwords have been rotated.
2. If **not** rotated: do not commit `.claude/projects/*.jsonl` — leave the noise tree dirty and say so.
3. If rotated: the transcript holds dead credentials and B2's normal handling applies.

⚠ Also: `CREDENTIAL_VAULT.md` lists the FTP passwords **twice** — the current pair near line 18–22 and
the stale `D3kFtp2026!` pair at lines 507–508 that S134 replaced. **Two records, one truth.** Reconcile
them; a reader hitting line 507 first gets a password that has not worked for months.

### B2 — The 276 noise entries: commit separately, then propose the cleanup

`.claude/` (file-history, backups, paste-cache, `projects/*.jsonl`), `.npm/_cacache`, `.npm/_logs`,
`.cache/gh/`, `.bash_history`, and the `@anthropic-ai/claude-code` npm binaries are all runtime churn
from Claude Code and npm. **They are tracked, which is why this repo is never clean** — and why the
Pre-Edit Snapshot Rule fires a false alarm at the start of every single session.

**This task: commit them in their own commit**, after B1, message `chore: runtime cache churn (S135)`.
⚠ Subject to **B1a** — if the FTP passwords have not been rotated, **omit `.claude/projects/*.jsonl`**
and say so.

**Then propose the permanent cleanup — do NOT execute it in this task.** Untracking ~276 paths changes
the repo layout and is the operator's call. Present exactly this and wait:

```
SUGGESTION: untrack the runtime-churn trees in /home/boatiq —
  .claude/{file-history,backups,paste-cache,projects}/  .npm/  .cache/  .bash_history
  .npm-global/lib/node_modules/@anthropic-ai/
  — because they are the ONLY reason `git status` is never clean, which makes the AAO §17
    snapshot check useless: a real uncommitted change is invisible among 276 noise entries.
  — what would change: add the paths to .gitignore, then `git rm -r --cached <path>` for each.
    ⚠ `--cached` ONLY. Files stay on disk; only the index entry is removed.
    ⚠ One commit per tree, so a mistake is revertible in isolation.
    ⚠ `.claude/projects/*.jsonl` are session transcripts — confirm the operator does not
      rely on git history for them before untracking.
  Apply?
```

⛔ **Never `git rm` without `--cached` here.** These are live runtime directories — Claude Code's own
state, npm's cache, and the shell history. Deleting them from disk breaks the working environment.

⛔ **The three real items in B1 must be in a commit of their own**, before this one, so the history
shows the project change separately from the noise.

---

## 4 — TESTS (all must pass before you report done)

| # | Test | Pass condition |
|---|---|---|
| T1 | `cd /home/boatiq/atmyboat-forum && git log --stat -1` | `crm-config.php` **absent** from the file list |
| T2 | `cd /home/boatiq/atmyboat-forum && git ls-files \| grep crm-config` | **empty** |
| T3 | `git -C /home/boatiq log --oneline -1 -- SESSION_LOG.md` | shows the new commit |
| T4 | `git -C /home/boatiq diff --submodule=short HEAD -- Helm-OS atmyboat-forum` | **empty** (gitlinks current) |
| T5 | `git -C /home/boatiq remote -v` | **still empty** — no remote was added |
| T6 | `git -C /home/boatiq log --oneline -3` \| `git -C /home/boatiq/atmyboat-forum log --oneline -2` | no `push` in reflog; branch unchanged |
| T7 | **Negative test — prove A1 bites.** `touch atmyboat-forum/wp-content/themes/twentytwenty-child/mobile/crm-proxy-test9.php` then `git status --short` | the new file does **not** appear. Delete it after. |

⚠ T7 is the only test that proves the ignore rule actually works. T1/T2 only prove nothing slipped
through *this* time. A guard that is present but non-functional manufactures confidence
(STANDING TRAP 6).

---

## 5 — DEFINITION OF DONE

- [ ] P1–P6 all pass, or the mismatch is reported and work stopped
- [ ] A1 done and T7 proves it bites
- [ ] A2 committed with a message describing what `footer.php` and `page-manual.php` actually change
- [ ] A3's two items reported to the operator, **untouched**
- [ ] B1 committed as its own commit
- [ ] B2 raised as one `SUGGESTION:` line, not acted on
- [ ] T1–T7 all pass
- [ ] **No `git push`. No `git remote add`. No `gh pr create`.**
- [ ] Result reported in chat with the two commit SHAs

---

## 6 — WHAT THIS SPEC DOES NOT AUTHORISE

- Deleting any file
- Adding a remote to `/home/boatiq`
- Untracking the `.claude/` / `.npm/` / `.cache/` trees
- Touching anything in `Helm-OS` (it is clean — leave it)
- Any deploy, to any target
