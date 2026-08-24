# ATOMIC SPEC — PHASE 0: Record Integrity

**Purpose:** make the governance records internally consistent, so every later spec rests on facts.
**Severity:** blocking. Phase 1 and 3 statuses are not trustworthy until this is done.
**Tier:** Tier 2 throughout. These are judgement edits to governance files, not code.
**Created:** 2026-08-24 (S131) · **Covers:** A0.2, A0.3, A0.4, A0.7

⚠ **Every item below writes to a governance file. Per the standing rule, present a Pre-Change File List
and get explicit `APPROVED` before executing — do not batch these into another task's approval.**

---

## A0.2 — De-duplicate BUG-61

**State:** the S131 merge imported BUG-61 **twice**, and the two entries contradict each other:

| Occurrence | Status |
|---|---|
| first | `[x]` FIXED S125 — "fully operational, all assets loading, menu navigation working" |
| second | `[!]` REOPENED S126 — "fix was INCOMPLETE; `/staging/staging/` double-path still broken" |

**Fix:** keep the REOPENED entry as the live status. Demote the S125 text to a `### History — S125 (superseded)`
sub-heading **beneath** it. **Do not delete it** — append-only is the standing rule for the audit ledger,
and the S125 text is evidence of what was believed at the time.

**Also reconcile PART 17:** it carries one BUG-61 row, which must match the surviving entry.

⚠ **New fact for the entry, from the S131 probe:** `/staging/wp-admin/` returned **`000`** — no response
at all, not a 404. Staging may be entirely down, which is a *different* condition from the double-path
defect BUG-61 describes. Record it; do not assume it is the same problem.

---

## A0.3 — Reconcile the three contradicted bugs

Three bugs disagree between `V09994_BUG_FIXES.md` and `PROJECT_CHECKLIST.md` PART 17:

| Bug | Bug file | PART 17 |
|---|---|---|
| BUG-25 | `[~]` "likely not a d3kOS bug" | `[x]` **NOT A BUG** — verified live on the boat |
| BUG-26 | `[x]` FIXED + deployed **to Pi** | `[~]` FIXED **in lab ONLY — NOT on the boat Pi** |
| BUG-27 | `[x]` COMPLETE — operator-confirmed | `[~]` DEPLOYED **to lab Pi ONLY** |

**Method — and this is the whole point of the item: a live read outranks every document.** In S114 the
two records disagreed on BUG-15 and the deployed code proved the checklist right; acting on the wrong
record produced a GitHub edit that had to be reverted.

**Lab Pi — already answered.** S131 established repo ↔ lab Pi are **byte-identical** (216 files, 0 drift).
So for the lab, the canonical tree *is* the lab state. Check the markers there and settle the lab column
with no further reads.

**Boat Pi — cannot be answered from here.** It is reachable only on the boat hotspot (`172.20.10.8`).
**Do not resolve the boat column by inference.** Mark each as `BOAT STATE UNKNOWN — verify on next trip`
and add the marker greps to the boat test card. That is an honest answer; picking a document is not.

⚠ **BUG-25 is different from the other two** — the disagreement is about *whether it is a bug at all*, not
about where a fix landed. PART 17 cites a live on-boat verification (Gemini answered a real query,
`tokens:290`, `online:true`, egress OK). **That is evidence and it wins.** Close BUG-25 in the bug file to
match.

---

## A0.4 — Correct BUG-70's disproved root cause

**State:** the entry says `OPEN` and prescribes restoring **6** doc files into a `docs/` folder on
`public-release`.

**What S130 established:** no `docs/` folder ever existed on that branch. There were **2** broken links,
not 6, both caused by deliberate 2026-08-20 key-containment deletions that **predate** the S129 cleanup
the entry blames. Commit `e630bfeb` fixed them; all 11 links were verified resolving.

**So the prescribed fix would create a folder that never existed**, to match links that no longer exist.

**Fix:** rewrite the root cause to match S130's finding and close the entry against `e630bfeb`. Preserve
the original text as `### Original diagnosis — S129 (DISPROVED by S130)`.

⚠ **Keep the "Protocol Failures That Caused This" section verbatim.** Those four failures (didn't read
README first, no Pre-Change File List, no `git status` before `filter-repo`, didn't re-read CLAUDE.md
after compaction) are **accurate and remain the most valuable content in the entry**, regardless of the
technical mis-diagnosis. Do not soften them because the root cause was wrong.

---

## A0.7 — Purge build artifacts from the canonical tree

**State:** 5 `.pyc` files are committed and appear in `MANIFEST.md5`, so the drift verifier reports them
as "missing on Pi" forever:

```
opt/d3kos/services/__pycache__/ota_upgrade.cpython-312.pyc
opt/d3kos/services/cloud-agent/__pycache__/ota_upgrade.cpython-312.pyc
opt/d3kos/services/dashboard/__pycache__/app.cpython-312.pyc
opt/d3kos/services/voice/__pycache__/voice-assistant-hybrid.cpython-312.pyc
opt/d3kos/services/voice/__pycache__/wake_word_vosk.cpython-312.pyc
```

**Fix:** `git rm --cached` the five, add `__pycache__/` and `*.pyc` to `.gitignore`, regenerate
`MANIFEST.md5`.

⚠ **`MANIFEST.md5` must be regenerated in the same commit.** A stale manifest is exactly the BUG-28 class
of defect this phase exists to eliminate — and `check-drift.sh` compares against it.

⚠ Also present and out of scope, but **note it in the BUG-28 entry**: `/var/lib/avnav/README.md` is in the
repo and absent on the Pi. Six "missing" files, and only this one is a real (if harmless) divergence.

---

## DEFINITION OF DONE

- [ ] Pre-Change File List presented and `APPROVED` before any edit
- [ ] BUG-61 appears exactly once; PART 17 row matches; `/staging/wp-admin/` `000` recorded
- [ ] BUG-25 closed to match the live on-boat evidence
- [ ] BUG-26 / BUG-27 lab column settled from the byte-identical read; **boat column explicitly marked
      UNKNOWN and added to the boat test card** — not guessed
- [ ] BUG-70 root cause corrected, closed against `e630bfeb`, protocol-failure section untouched
- [ ] 5 `.pyc` untracked, `.gitignore` updated, `MANIFEST.md5` regenerated in the same commit
- [ ] A grep for `BUG-\d+` across both records finds no bug present in one and absent from the other

## WHAT THIS DOES NOT DO

- **Does not resolve boat-Pi state.** That needs the trip. Any spec claiming otherwise is guessing.
- **Does not touch BUG-58/59/70's S129 statuses** — they were settled in the S131 merge.
