# ATOMIC SPEC — PHASE 0: Release-State Drift Verifier (A0.6)

**Purpose:** one command that prints the true, current deployment state of any Pi, comparing
**repo → manifest → Pi**. Closes BUG-28 by measurement.
**Operator decision S131:** build it. (The earlier plan dropped it in favour of cloning; the clone never
happened, so state remained unknown.)
**Tier:** Tier 1 specified; **Tier 3 implementable** — it is one self-contained shell script derived from
a working prototype.
**Created:** 2026-08-24 (S131) · **Target:** `deployment/v0.9.9.4/tools/release-state.sh`

---

## 1. THIS IS NOT A GREENFIELD BUILD — the core was proven in S131

The algorithm below **already ran successfully** against the lab Pi this session and produced the
headline result: **216 files compared, 210 md5-identical, 0 drifted, 6 "missing" of which 5 are `.pyc`
build artifacts and 1 is a README.** That is the first trustworthy statement about deployment state this
project has had.

**Implement exactly this. Do not redesign it.**

```
1. cd deployment/v0.9.9.4
2. find opt var etc home -type f   -> the mappable set (216 files; excludes tools/, README, MANIFEST)
3. local:  md5sum each, key by the Pi-absolute path ("/" + relative path)
4. remote: one ssh invocation, read paths on stdin, emit "md5  path" or "MISSING  path"
5. join on path; classify IDENTICAL / DRIFTED / MISSING_ON_PI
6. also report EXTRA_ON_PI for the tracked directories (see §3)
```

**Why one ssh invocation and not one per file:** 216 round trips at ~30 ms each is ~7 s of pure latency
and 216 auth events in the Pi's journal. Streaming the path list over stdin to a single remote loop was
what made the prototype fast. Keep it.

---

## 2. WHY `check-drift.sh` IS NOT SUFFICIENT

`tools/check-drift.sh` already exists. It compares **Pi against `MANIFEST.md5`** — so a green result means
"the Pi matches a manifest", and says nothing about whether the manifest matches the repo. The recorded
symptom of BUG-28 is precisely that: *"`check-drift.sh` compares Pi against MANIFEST, not repo against
MANIFEST — a green result does not mean the Pi is current."*

**This tool closes the third edge.** All three comparisons must be reported separately:

| Comparison | Answers |
|---|---|
| repo ↔ Pi | is the Pi running what we think? |
| repo ↔ MANIFEST | is the manifest stale? |
| MANIFEST ↔ Pi | what `check-drift.sh` already does |

**A stale manifest with a matching Pi must not print green.** That is the exact false-confidence mode
that made a deploy record look like evidence for seven sessions.

---

## 3. REQUIRED BEHAVIOUR — the parts that are easy to get wrong

**R1 — `EXTRA_ON_PI` must be reported, not ignored.** The prototype only looked for repo files on the Pi.
It would not have found an orphan file *added* on the Pi and never committed — which is exactly how
`create-image.sh`, `sanitize.sh`, `tier-manager.sh` and `detect-opencpn.sh` came to be unsourced
production tooling (BUG-78 D4). Walk the tracked directories on the Pi and flag anything not in the repo,
**excluding** `*.bak`, `__pycache__`, and `*.pre-*` (there are ~10 `.bak` files in the live templates
directory alone).

**R2 — exit non-zero on any drift.** The suite lesson from BUG-51 applies: a tool that reports problems
in prose and exits 0 gets wired into CI and silently passes forever.

**R3 — parameterise the host.** `PI=172.20.10.8 ./release-state.sh` must work for the boat Pi on the boat
hotspot. Default to the lab Pi (`192.168.1.237`). This is the tool that will finally settle the boat
column in `PHASE0-record-integrity.md` A0.3.

**R4 — never write to the Pi.** Read-only, no exceptions. This tool will be run against a live vessel.

**R5 — classify, don't just diff.** Output must distinguish:
`IDENTICAL` · `DRIFTED` (present, different md5) · `MISSING_ON_PI` · `EXTRA_ON_PI` · `UNREACHABLE`.
`UNREACHABLE` is its own state and must **never** be silently counted as identical.

**R6 — print the summary line last and make it unambiguous.** e.g.
`RESULT: DRIFT (3 drifted, 1 missing, 2 extra) — Pi 192.168.1.237 is NOT running the canonical tree`.
The prototype's value came from a single sentence a human could act on.

---

## 4. WHAT IT MUST NOT DO

- **Must not "fix" anything.** No copying, no syncing. A verifier that repairs cannot be trusted to
  report. Deployment stays a separate, deliberate act.
- **Must not exclude a file because it is "expected to differ".** If `avnav_server.xml` or
  `fleet-push.env` legitimately differ per-Pi, that is a finding about the architecture (they are
  Pi-only and not version-controlled — recorded S115), not a reason to hide them. Report them and let
  the human decide.
- **Must not regenerate `MANIFEST.md5`.** Read-only means read-only.

---

## 5. TESTS — `tools/verify-release-state.sh`

| # | Test | Expect |
|---|---|---|
| T1 | Clean lab Pi | `IDENTICAL` count 210+, exit 0 |
| **T2** | **Touch one byte in a repo file, re-run** | **`DRIFTED` = 1, exit non-zero.** The core negative test — a verifier that cannot see one changed byte is decoration |
| T3 | Point at an unreachable host | `UNREACHABLE`, exit non-zero, **not** "all identical" |
| T4 | Create an untracked file on the Pi in a tracked dir | `EXTRA_ON_PI` = 1 (R1) |
| T5 | Corrupt one line of `MANIFEST.md5` | repo↔MANIFEST mismatch reported, **not green** (§2) |
| T6 | `.bak` / `__pycache__` files present on the Pi | **excluded** from `EXTRA_ON_PI` |
| T7 | Run twice, no changes | byte-identical output (deterministic; safe for CI diffing) |

**T2 and T3 are the ones that matter.** T2 proves it detects drift; T3 proves it fails loudly rather than
reporting success when it learned nothing. T3 is the failure mode that makes tools dangerous.

---

## 6. DEFINITION OF DONE

- [ ] `release-state.sh` reproduces the S131 prototype result on the lab Pi (216/210/0/6)
- [ ] All three comparisons in §2 reported separately
- [ ] T2 and T3 pass
- [ ] `PI=` override works; documented for the boat trip
- [ ] `.pyc` noise gone (depends on `PHASE0-record-integrity.md` A0.7 — otherwise 5 permanent false
      "missing" entries train the operator to ignore the output)
- [ ] Wired into the pre/post evidence for every lab deploy under the S131 standing authorisation
- [ ] BUG-28 entry updated with a real result, not a deploy record

## 7. WHY THIS IS THE HIGHEST-LEVERAGE ITEM IN PHASE 0

Three boat trips (S101, S107, S112) were consumed because nobody could state what was running on the Pi
under test. Fixes were marked "deployed", the boat disagreed, and confidence collapsed. **This tool
converts "we deployed it" into "the Pi is byte-identical to commit X" — and the S131 run already proved
the answer can be yes.**

Run it before *and* after every deploy. The before-run is what catches a Pi that drifted since last time.
