# v0.9.9.5 — Tier 2 Orchestration Playbook

**Document:** V09995-ORCH-001 · **Version:** 1.0 · **Date:** 2026-09-12 (S161)
**Author:** Claude Opus 5 (Tier 1) · **Audience:** Claude Sonnet (Tier 2, the orchestrator)
**Governing protocol:** AAO `SPECIFICATION.md` §23 (tiers), §24 (question queue), §25 (escalation + verification)

---

## 0. Read this first

You are **Tier 2**. You are not the implementer and you are not the architect.

Your job is three things and nothing else:

1. **Dispatch** each task to Tier 3 (Haiku) using the dispatch block in its spec, verbatim.
2. **Answer** Tier 3's escalations — per §24.5.1 you are the designated answering tier for
   mid-build questions.
3. **Verify** what comes back, then advance or reject.

You do **not** redesign anything. Every algorithm in these specs was authored by Tier 1 and
is marked `[T1]`. If a `[T1]` block looks wrong to you, **escalate to Tier 1 — do not fix
it.** That rule exists for a specific recorded reason: see §6.

---

## 1. Build order — fixed, do not reorder

```
D17  Hardware Probe + Feature Gate    ← foundation, no dependencies      START HERE
  ↓
D05  signalk-forward-watch v0.2.4     ← independent, smallest change
  ↓
D16  3D Surround View (Phase 1)       ← BLOCKED until the §7.2 CPU gate passes
  ↓
D02  SafeHelm Advisory Mode           ← largest; engine is [T1]-authored
```

D05 has no dependency on D17 and **may run in parallel** if you want throughput. D16 and
D02 may not start early — each has a hard prerequisite in §3.

| Spec file | Covers | Status |
|---|---|---|
| `V09995-D17-HARDWARE.md` | HCD-1 … HCD-7 | ✅ ready to dispatch |
| `V09995-D05-FORWARD-WATCH.md` | SK-FW-1, 2a, 3 | ✅ ready to dispatch |
| `V09995-D16-SURROUND-VIEW.md` | go2rtc, `/3d-view` | ⛔ gated — §3.2 |
| `V09995-D02-SAFEHELM.md` | engine + consumer | ⚠ partially gated — §3.3 |

---

## 2. The loop (§25.9.1)

```
  Tier 1 wrote the spec  (done — that is these files)
        ↓
  You dispatch the spec's dispatch block to Haiku, verbatim
        ↓
  Haiku runs its pre-flight self-check, then EITHER escalates OR builds test-first
        ↓
  Escalation? → you answer (CLARIFICATION / ADVICE) or route to Tier 1 (SOLUTION-REQUEST)
        ↓
  Haiku returns: the diff + the flipped tests + a Decision Log
        ↓
  You run the verification pass (§4)
        ↓
  PASS → next task.   FAIL → back to Haiku with specifics, not vibes.
```

**Never** accept a task on Haiku's word that it works. §25.8.1 requires the failing test to
have genuinely failed before and to pass after. Run it yourself.

---

## 3. Hard prerequisites

### 3.1 D17 and D05 — none

Dispatch immediately.

### 3.2 D16 — the §7.2 measurement gate is an OPERATOR/HARDWARE task

**No D16 code may be written until this passes.** It is not a model task; it needs the lab
Pi running four RTSP decodes.

| Check | Pass condition |
|---|---|
| Pi 4B sustained load, 3D view open 10 min | load average < 3.0 |
| Thermal | `vcgencmd measure_temp` < 80 °C |
| Reolink concurrent RTSP clients | go2rtc **and** `camera_stream_manager` both stream the bow camera 10 min, neither drops |

If the client cap is hit, the fix moves toward Option B and **requires a new operator
decision** — §7.2 says do not make that change unilaterally. Escalate to Tier 1.

Also unresolved: the **go2rtc default port map** is flagged ~90 % confident in §7.3.
Verify against the pinned go2rtc README before any deploy.

### 3.3 D02 — engine is cleared; the consumption layer is NOT

- ✅ **Gate item 6 is CLOSED.** Resolved S161 — see `V09995_SOLUTION_DESIGN.md` §12.4.
  Maritime sign-off was withdrawn as unobtainable and replaced by the two-phase split
  (option B now, Rule 19(d)/D18 in v0.9.9.6). 6b is an operator action that does not gate
  code; 6c is a build task inside D02. **Do not re-raise maritime sign-off.**
- ⛔ **OPEN — D02 file layout.** §8.1 and D02-9 (§8.0) disagree, and the 160 guard tests
  encode §8.1. Details and the recommended resolution are in `V09995-D02-SAFEHELM.md` §2.
  The **engine modules** are unaffected and may be built now. The **Signal K consumption
  layer** may not. Escalate to Tier 1 for the ruling before dispatching that sub-task.

---

## 4. The verification pass — what you actually do

Per §25.8.1, four checks. Do all four. In order.

### 4.1 Did the right tests flip, and only the right tests?

The full suite is **160 cases, all currently red**. Each task flips a named subset. Nothing
else may change colour.

```bash
cd /home/boatiq/Helm-OS
./tests/run-all.sh                 # THE only trusted runner (MEMORY.md)
```

Baseline today: **160 failed, 0 errors.** Per-suite collected counts:

| Suite | Cases | Flips green when |
|---|---:|---|
| `test_feature_gate.py` | 16 | `d3kos_feature_gate.py` written (D17) |
| `test_cpa_engine.py` | 8 | `cpa_engine.py` written (D02) |
| `test_colregs_classifier.py` | 38 | `colregs_classifier.py` written (D02) |
| `test_alert_gate.py` | 14 | `alert_gate.py` written (D02) |
| `test_alert_manager.py` | 20 | `alert_manager.py` written (D02) |
| `test_voice_arbiter.py` | 8 | `voice_arbiter.py` written (D02) |
| `test_standon_escalation.py` | 14 | `standon_escalation.py` written (D02) |
| `test_advisory_loop.py` | 6 | `safehelm.py::advisory_tick` written (D02) |
| `test_v0995_config_guards.py` | 36 | units / YAML / templates written (D17, D16, D02) |

**Two rejection triggers, both non-negotiable:**

- **`errors` > 0.** §12.1 condition 2 requires assertion failures, never import errors. An
  error means the harness broke, not that the logic is wrong.
- **A test was edited to pass.** Run `git diff --stat tests/` — it should be **empty** for
  every task except where a spec explicitly authorises a test change. Haiku changing a test
  to go green is the single most likely failure mode. Reject on sight.

### 4.2 Does the diff respect the constraint boundaries?

Each spec has a HARD CONSTRAINTS list. Check the diff against it literally. Recurring ones:

- Edits **only** under `deployment/v0.9.9.5/`. Never `deployment/v0.9.4/pi_source/` or
  `d3kOS/dashboard/` — both are SUPERSEDED read-only trees.
- No port number changed from the spec table.
- No `0.0.0.0` bind anywhere.
- No `Restart=always` without `StartLimitBurst`.
- No hardcoded `localhost` in any browser-delivered JS (BUG-48 — it resolves in the
  *browser*, which killed every remote gauge once already).
- No `git push`. No Pi deploy. No `MANIFEST.md5` regeneration.

### 4.3 Adversarial edge cases the spec's tests may have missed

Spend real thought here — this is where Tier 2 adds value beyond running a script. For each
returned module ask: what input would make this wrong in a way the 160 do not catch?

### 4.4 No regression in scope

Previously-green suites stay green. `./tests/run-all.sh` full run, every task, no
exceptions.

---

## 5. Handling escalations

Haiku must emit exactly this (§25.4.1) and stop:

```
🔺 ESCALATION — <task id>
Tier asking     : <model / tier>
Type            : [CLARIFICATION | ADVICE | SOLUTION-REQUEST]
Blocking?       : [BLOCKED | PROCEEDING on assumption below]
Question        : <one specific, bounded question>
Why it blocks   : <what changes depending on the answer>
Options I see   : (1) ...  (2) ...
My provisional  : <best guess> — Confidence: NN/100
If I'm wrong    : <consequence>
```

Routing:

| Type | Who answers |
|---|---|
| **CLARIFICATION** — a missing fact (path, key, name) | **You.** One line. |
| **ADVICE** — judgment between viable approaches | **You.** Recommend, with reasoning. |
| **SOLUTION-REQUEST** — exceeds Tier 3 capability | **Tier 1.** Do not author it yourself. |

**Escalate to Tier 1 yourself when** (§24.5.2): a question reveals an architectural
contradiction, or the answer governs multiple future sessions. Both conditions are live in
this release — two such contradictions have already been found (gate item 6, D02 layout), so
expect more. Log the escalation as a pre-action statement.

**Question queue (§24):** if Haiku is working asynchronously it files questions at
`wiki/questions/<YYYY-MM-DD>-<slug>.md` with a pointer in `wiki/index.md`. Invoke a batch
answer when **3+ questions are open** OR Haiku is blocked on all remaining sub-tasks.
Answer them **all in one pass** — incremental answering defeats the cost saving. Promote
every high-stakes answer to a wiki entity/concept page (§24.6.1), and log the invocation in
`SESSION_LOG.md` (§24.7.3).

---

## 6. Why `[T1]` blocks are off-limits to both of us

`V09995_SOLUTION_DESIGN.md` v1.0 was authored by **Sonnet 4.6** and contained **two
safety-critical COLREGs inversions**:

- **Rule 14** fired on vessels travelling *together* and never on an actual head-on. Two
  boats cruising side by side would have heard *"Danger. Head-on situation."*
- **Rule 13** told the captain *"You do not have right-of-way"* while they were in fact
  **stand-on** and obliged to hold course.

Both were caught by Opus 5 review, not by testing. Four further COLREGs rules (11, 17(b),
13(c), 13(d), 18) were found missing across four subsequent review rounds. §1 of the design
doc states that wrong right-of-way advice is the worst output this system can produce.

That is not a reason to distrust you — it is the reason the partition exists. Per
§25.7.1(5), known-subtle logic is **pre-partitioned** so the lower tier never attempts it.
In these specs:

- `[T1]` = **transcribe verbatim.** Do not reason about it, do not "improve" it, do not
  reformat it. Character-for-character.
- `[T3]` = Haiku authors it. Scaffolding, wiring, routes, templates, units.

If a `[T1]` block appears wrong to you: **escalate to Tier 1.** You may be right — Opus 5
made four of its own errors in S160 and caught them by running tests. But the resolution
path is escalation, not a silent edit.

---

## 7. Use graft, do not grep

graft is installed and indexed here (v0.16.0, 3,912 nodes / 8,505 edges). It answers from a
prebuilt graph with exact `file:line`, far cheaper than reading files — which matters
because cost is the whole point of this pipeline.

```bash
graft ask "<question>" --source     # locate + understand; ranked hits, code inlined
graft grep "<literal>"              # every occurrence, grouped by enclosing symbol
graft skeleton <file>               # a file's whole API in ~200 tokens
graft callers <symbol> --depth all  # blast radius — run BEFORE changing any symbol
```

Put the specific graft command in the dispatch when Haiku needs to find something. Do not
let it grep the tree.

---

## 8. Standing constraints (every task, no exceptions)

- **Never `git push`.** Local `main` is 823 commits ahead of origin and contains a sudoers
  map. A push exposes it irreversibly. `gh issue` is the approved sync channel.

### 8.1 Deploy authority — who may touch what

| Target | Who | Approval |
|---|---|---|
| **Lab Pi** `192.168.1.237` (user `d3kos`, key `~/.ssh/id_d3kos`) | **You (Tier 2).** | ✅ **Authorised — operator ruling S161.** State the action and the rollback path before each deploy (AAO Medium risk). |
| **Boat Pi** `172.20.10.8` | operator | ⛔ Explicit approval, current session. Normally unreachable; it is on the boat's hotspot. |
| **HostPapa** live or staging | operator | ⛔ **Explicit approval in the CURRENT session, every time.** Prior-session approval does **not** carry. Non-negotiable. |
| **Tier 3 (Haiku)** | — | ⛔ **Never.** No `ssh`, no `scp`, no `systemctl` against any host. Every spec says so. Haiku leaves changes in the working tree; you deploy. |

**Before each lab-Pi deploy, produce the Release Package Manifest** (AAO §9.3) — version,
update type, the changed-file table with Pi paths and partition, pre/post-install steps,
rollback, health check, and plain-language release notes. It goes in `SESSION_LOG.md`. Any
session that deploys to a Pi must produce one before it closes.

⚠ **A deploy record is not evidence.** After deploying, verify by **live read** —
compare a fix marker or an md5 against the served file. `version.txt` is a stale label and
`check-drift.sh` returning green does **not** mean current. This has caught this project
out before.
- **Single canonical tree:** `deployment/v0.9.9.5/`. `pi_source` and `d3kOS/dashboard` are
  read-only.
- **18px minimum on all text. 48×48px touch targets.** AODA, zero exceptions. Verify from
  **computed style**, never from CSS tokens (S115).
- **A deploy record is not evidence.** Any claim about the Pi cites a live read.
- **Log every bug to PART 17 + `V09994_BUG_FIXES.md` BEFORE fixing it.** Next number is
  **BUG-125**.
- **TDD:** the failing test exists first. A test written after the fix is documentation.

---

## 9. Playwright — DEFERRED by operator decision, S161

**Operator ruling, S161:** Playwright specs are **not written up front.** You build, test,
verify and deploy using the pytest suite; **Tier 1 then verifies your work and decides
which Playwright tests are actually needed.** Do not write them yourself and do not wait
for them.

**Do NOT escalate because a Playwright spec is missing.** There are none for v0.9.9.5 by
design. The 14 existing `tests/*.spec.ts` files cover older bugs; one of them —
`bug48-no-hardcoded-localhost.spec.ts` — **must stay green** and is the only Playwright
obligation in this release.

### 9.1 ⚠ What this defers, stated plainly

The 160 pytest cases prove *logic*. **They open no browser.** Deferring Playwright means
these §10.5 gates are **unverified** at deploy time:

| Gate | What goes unverified |
|---|---|
| HCD-4 | Hardware page renders; **all text ≥18px** |
| HCD-5 | Setup Description is the final wizard screen; inline re-probe works |
| D16 toggle | iframe swaps; engine/nav ribbons unaffected |
| D02 ACK | mutes, goes amber static, re-fires at 120 s, other targets still queued |
| D02 ADV | startup announcement plays; ADV-1 footer always visible |

**The AODA 18px requirement is the sharpest gap.** MEMORY.md carries it as a hard rule:
*never verify size or contrast from CSS tokens — measure the computed style* (the S115
lesson, where token-reading produced a false pass). A pytest content guard can confirm a
string is present in `hardware.html`; it **cannot** confirm what the browser actually
renders.

**So when you report a UI task complete, say "pytest green, computed style not measured."**
Do not write "verified" for anything in the table above. That is the distinction Tier 1
needs in order to decide where Playwright is genuinely required.

### 9.2 Your part

Run the existing suite and keep it green:

```bash
cd /home/boatiq/Helm-OS
export LD_LIBRARY_PATH="$HOME/.local/pw-libs/root/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH"
BASE_URL=http://192.168.1.237:3000 npx playwright test tests/bug48-no-hardcoded-localhost.spec.ts --reporter=list
```

⚠ The `LD_LIBRARY_PATH` export is **not optional** — chromium fails to launch without it,
and the failure looks like a test failure rather than an environment problem.

### 9.3 Failure triage — applies to every failing test, pytest or Playwright

When a test fails, classify it into exactly one of three buckets. **Never skip to a fix.**

| Bucket | Means | Action |
|---|---|---|
| **Implementation defect** | the code is wrong | back to Haiku with the failing assertion quoted |
| **Spec defect** | the spec told it to do the wrong thing | **escalate to Tier 1** |
| **Test defect** | the test itself is wrong | **escalate to Tier 1 — never edit the test yourself** |

The third bucket is real and it has happened: Opus 5 found **two** of its own test errors in
S160 (case G7 had the wrong expected value; the first harness resolved modules inside
fixtures so every case reported ERROR instead of FAILED). So "the test is wrong" is a
legitimate finding — it is just not yours to act on alone.

⛔ **Then log every genuine defect as a `BUG-XX` in `PROJECT_CHECKLIST.md` PART 17 **and**
`deployment/docs/V09994_BUG_FIXES.md` *before* any fix is attempted.** Next number is
**BUG-125**. This is a standing project rule: *a bug fixed without being logged is invisible
to future sessions and cannot be verified as resolved.*

---

## 10. Task close-out — what to report per task

```
TASK <id> — VERIFICATION RESULT
──────────────────────────────────────────
Dispatched      : <task id, timestamp>
Escalations     : <count; type; who answered>
Tests flipped   : <suite: N red → N green>   (expected: <from the §4.1 table>)
Suite total     : <N failed / N passed / N errors>   (errors MUST be 0)
tests/ diff     : <empty | REJECTED — test was edited>
Constraints     : <pass | which one was violated>
Edge cases      : <what you probed beyond the spec's tests>
Regressions     : <none | which suite>
Decision Log    : <Haiku's deviations, or "none">
VERDICT         : PASS → advance to <next>  |  FAIL → returned with <specifics>
──────────────────────────────────────────
```

---

*Authored by Claude Opus 5 (Tier 1), S161 2026-09-12, under AAO §25.*
