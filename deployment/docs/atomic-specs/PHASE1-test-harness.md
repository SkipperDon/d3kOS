# ATOMIC SPEC — PHASE 1: Test Harness Integrity (BUG-51, BUG-52, BUG-53)

**Shared root cause:** the suite does not tell the truth about its own state. A partial run has looked
like a complete one; stale expectations are carried as "accepted red"; and one test asserts a defect that
was deliberately fixed.
**Severity:** MEDIUM, but it gates confidence in every other fix in this release.
**Tier:** Tier 3 (constrained edits) except §4, which is Tier 2 judgement.
**Created:** 2026-08-24 (S131)

---

## 1. WHAT S131 VERIFIED — BUG-51's core is already fixed

`tests/run-all.sh` (7,564 B) is in better shape than the bug record implies. Verified by reading it:

| Capability | State |
|---|---|
| Chromium launch pre-check before trusting any result | ✅ **present** (line ~62) — this was the S114 blocker |
| Dispatches by file type: `*.spec.ts` → Playwright, `*.test.cjs` / `*.test.js` → node, `test_*.py` → python | ✅ present |
| `--workers=1` enforced | ✅ present (line 79) |
| Tracks and prints a `NOT_RUN` list | ✅ present (line 136) |
| `exit 1` on any failure, `exit 0` only when clean | ✅ present (lines 142–147) |

**So BUG-51 items 1–5 are genuinely done.** The pre-check is the important part: *"always confirm chromium
can launch before trusting a suite result"* is now enforced by the runner rather than by memory.

### The remaining BUG-51 defect: there are two runners

```
tests/run-all.sh          7,564 B   <- canonical
tests/run-all-tests.sh              <- stale duplicate
```

**A second runner is the same failure mode BUG-51 describes**, one level up: someone runs the wrong file
and gets a partial result that looks complete. **Delete `run-all-tests.sh`** (or reduce it to a two-line
shim that `exec`s the canonical one and prints a deprecation notice — safer if anything references it).

⚠ **Grep for references before deleting** — CI, docs, `pre-distribution-checklist.sh`, and the
`DEPLOYMENT_INDEX` may name it.

---

## 2. BUG-53 — the test that asserts a fixed defect

**Target:** `tests/bug26-anchor-watch-origin.spec.ts`

BUG-26's test asserts the hardcoded `localhost` that BUG-48 deliberately removed. So the suite now
*requires* the defect BUG-48 fixed. Left alone it either fails forever or, worse, someone "fixes" it by
reverting BUG-48.

**Fix:** rewrite the assertion to match BUG-48's contract — the anchor endpoint host must be **derived
from the page** (`window.location.hostname`), not literal. The correct assertion is the *inverse* of the
old one.

⚠ **Do not simply delete the test.** BUG-26 (Set Anchor failing, no alarm) is a real safety-relevant
defect — an anchor alarm that does not fire is a boat dragging onto rocks at 3 a.m. The test must keep
covering the anchor path; only the host assertion changes.

⚠ **BUG-26 also has a status contradiction** (bug file says deployed to Pi; PART 17 says lab only). That
is `PHASE0-record-integrity.md` A0.3 — **resolve it there first**, or this test may be written against
the wrong assumption about what is deployed.

---

## 3. BUG-52 — the "accepted red" that hides an untested safety path

**Status:** closed NOT A BUG in S118 — the diagnosis was that `bug30`/`bug36` expectations are stale
(BUG-34 added `depth_m`; BUG-43 made depth imperial), not that the code regressed. **That closure stands.**

**But one line in the record is unresolved and is the real issue:**

> *"Depth-priority safety assertions 3–5 have NEVER executed."*

**This is not a stale-expectation problem. It is untested depth-priority logic** — the code that decides
which depth source to trust. On a boat, depth is the difference between water under the keel and
grounding. Three assertions written to cover it have never run.

### Probable mechanism, and the first thing to check

`bug30-depth-fallback.test.cjs` and `bug36-engine-data-cache.test.cjs` are **`.test.cjs`** — the node
branch of the runner (line 92), not the Playwright branch. The node branch wraps each file in
`timeout 120 node "$f"` and records pass/fail **per file, not per assertion** (line 131 prints "files
passed / files failed"). So if a `.test.cjs` file exits early — an unmet precondition, an early `return`,
a thrown error caught and swallowed — **assertions 3–5 never execute and the file can still report as a
pass.**

**Verify this before writing a fix.** Add per-assertion reporting to the node branch, or convert the file
to a framework that counts assertions. **A file-level pass/fail cannot distinguish "10 assertions passed"
from "2 passed and the function returned early" — which is BUG-51's exact defect, surviving inside the
node branch after being fixed at the suite level.**

**Then fix the stale expectations** (`depth_m`, imperial units) so the suite goes honestly green.

---

## 4. STEP (Tier 2) — retire "accepted red"

The runner currently ends **NOT GREEN** by design, with known-stale reds tolerated. That is defensible
short-term and corrosive long-term: once a suite is expected to be red, nobody reads it, and a *new* red
is invisible.

**Required end state: `run-all.sh` exits 0.** Every red is either fixed, or explicitly quarantined with
a machine-readable reason:

```
# QUARANTINE: bug30 assertions 3-5 — depth-priority logic untested (BUG-52)
# Owner: <who>   Unblocks: per-assertion reporting in the node branch
# Expires: <date> — if still present after this date, escalate
```

Quarantined tests must be **printed in the summary**, not silently skipped. A test hidden from the summary
is a test that has been deleted with extra steps.

---

## 5. TESTS

| # | Test | Expect |
|---|---|---|
| T1 | `run-all.sh` on a clean lab Pi | exit **0** |
| T2 | Break one assertion in any file | exit non-zero, that file named |
| T3 | Make a `.test.cjs` file `return` early after 2 of 5 assertions | **FAIL or explicitly report 2/5** — must not report a pass (§3) |
| T4 | Rename a test file to a non-dispatched extension | appears in `NOT_RUN`, exit non-zero |
| T5 | Chromium unavailable | runner aborts with a clear message; does **not** report 0 failures |
| T6 | `bug26` test with BUG-48's fix present | PASS (BUG-53 fixed) |
| T7 | `bug26` test with `localhost` reverted | **FAIL** — proves the assertion inverted correctly |
| T8 | `grep -rn run-all-tests` across repo and docs | no live references |

**T3 is the assertion that matters.** It is the only one that proves the harness can distinguish a partial
run from a complete one at the *assertion* level, which is what BUG-51 was actually about.

---

## 6. DEFINITION OF DONE

- [ ] `run-all-tests.sh` removed or reduced to a shim; T8 clean
- [ ] BUG-53 fixed with an **inverted** assertion, anchor coverage retained; T6 and T7 pass
- [ ] Per-assertion visibility in the node branch; T3 passes
- [ ] bug30 assertions 3–5 **actually execute** — and their result recorded, whatever it is
- [ ] Stale `depth_m` / imperial expectations updated
- [ ] `run-all.sh` exits 0, or every red is quarantined with owner, reason and expiry
- [ ] Baseline recorded in `V09994_FIX_PLAN.md` progress log with the real number

## 7. WHAT THIS DOES NOT DO

- **Does not add coverage.** It makes existing coverage honest. New coverage is
  `PHASE1-contract-test.md`.
- **Does not resolve BUG-52's closure.** That stands. This addresses the untested assertions the closure
  left behind.
- **Does not fix depth-priority logic** — it makes it *testable*. If assertions 3–5 then fail, that is a
  new finding and must be logged as a bug, **not folded into this fix.**
