# v0.9.9.4 — EXECUTION ORDER

**This is the implementer's running order. Start here.**
**Created:** 2026-08-24 (S132-cont) · **Specs:** `deployment/docs/atomic-specs/`

Read this file, do the next unchecked item, tick it, move on. Do **not** pick items out of order —
the dependencies below are real, and several items make a later item impossible if skipped.

**Rules that apply to every item:**
- Lab Pi deploys carry standing operator approval. **Boat Pi and HostPapa live are per-deploy, and need
  explicit in-session `APPROVED` every time.**
- **Never `git push`.** Ever.
- Every spec has prerequisite checks that **abort on mismatch**. If a prerequisite fails, stop and report.
  Do not adapt the spec to what you find — the mismatch *is* the finding.
- Tier 3 = **Gemini 2.5 Flash Lite** (`gemini-2.5-flash-lite`, Google Gemini API). Key lives in
  `/opt/d3kos/config/api-keys.json` on the Pi. Dispatch scripts run FROM the Pi (SSH stdin) so the
  key never leaves the device — see `deployment/tools/tier3-dispatch/` for the pattern.
  **Exact `old`/`new` replacements only — never whole files.**

---

## PHASE 0 — Make the records true and the state measurable

No dependencies. Do this first: everything after it is untrustworthy otherwise.

- [x] **0.1 — `PHASE0-record-integrity.md`** ✓ S133 2026-08-24
      BUG-61 de-dup · BUG-25/26/27 reconciliation · BUG-70 root-cause correction · purge 5 `.pyc`
      ⚠ **Needs a Pre-Change File List and explicit `APPROVED`** — governance files.
      ⚠ Do 0.1's `.pyc` purge **before** 0.3, or the verifier reports 5 permanent false "missing" and
      the operator learns to ignore its output.
- [x] **0.2 — `BUG-28.md` Step 2** ✓ S133 2026-08-24 — bring 4 unsourced production scripts under version control,
      **byte-identical, no edits, own commit**: `create-image.sh`, `sanitize.sh`, `tier-manager.sh`,
      `detect-opencpn.sh`.
      ⚠ **Prerequisite of 2.1 and 1.4.** Both specs say so. Do it once, here.
      ⚠ **Never execute `sanitize.sh` on a Pi you are working on** — it deletes
      `~/.ssh/authorized_keys` and severs your own access.
- [x] **0.3 — `PHASE0-drift-verifier.md`** ✓ S133 2026-08-24 — build `tools/release-state.sh`.
      The S131 prototype already produced the answer (216 files, 210 identical, 0 drift). Reproduce it,
      then add `EXTRA_ON_PI` (that check is what would have caught 0.2's four orphan scripts).
      ⚠ From here on, **run this before and after every deploy.** The before-run catches drift since
      last time. A deploy record is not evidence.
- [x] **0.4 — `BUG-28.md` Steps 1 and 3** ✓ S133 2026-08-24 — de-duplicate `cloud_agent.py` and `ota_upgrade.py`;
      operator decision on the two Pi-only configs.
      ⚠ **The 719-line `cloud_agent.py` is a strict SUPERSET of the 630-line one that systemd runs.
      "De-duplicate" reads like "delete the idle one" — doing that destroys the only copy of
      `push_config_snapshot`. Promote, do not prune.** Test T4 exists for this.

---

## PHASE 2 — THE SECURITY RELEASE GATE

Operator decision: security first. This runs before Phase 1.

- [~] **2.1 — `BUG-78.md`** (CRITICAL) ✓ code+tests S134 2026-08-25 — wire `sanitize.sh` into
      `create-image.sh`; credential strip (STEP 7b); build assertion; `--unattended` flag; T1–T4+T6 PASS.
      ⚠ T5 (Pi md5 match) + deploy + §12.1 spec reconciliation pending Pi connectivity.
- [~] **2.2 — `BUG-74.md`** ✓ Steps 1+2 S134 2026-08-25 — .gitignore + template done; 5/5 PASS.
      ⚠ Step 3 (chmod 600 on Pi) pending Pi connectivity — T5 + T7 skip until then.
- [ ] **2.3 — `BUG-66.md` Phase A** — server side: 4 tables, `device-auth.php`, 3 endpoints, wp-admin
      approval queue. **Tier 1/2 only — this is new-file work; do not dispatch to Tier 3.**
      ⚠ Server before Pi. A Pi enrolling against a server with no tables fails closed, which is safe.
      The reverse is not.
- [ ] **2.4 — `BUG-66.md` Phase B** — Pi side: Ed25519 keypair generated inside
      `regenerate-identity.sh` before its sentinel; signing helper for the three services.
      ⚠ **Never bake a key into the image.** One key in the `.img` is shared by every d3kOS on earth.
- [ ] **2.5 — `BUG-77.md`** — Tier 1 = paired **and** server-approved. Depends on **2.3** (`/status`).
      ⚠ Until 2.3 exists, `device_is_paired_and_approved()` must return **False**. A stub returning True
      grants Tier 1 to every device — worse than the bug.
      ⚠ **Server unreachable must NEVER downgrade.** A tier check that fails closed at sea is a
      safety-adjacent defect, not a security win.
- [ ] **2.6 — `BUG-63.md`** — registration-code gate before `page-register.php:88`. Depends on **2.3**.
      ⚠ Claim the code atomically **then** create the user; roll back on failure. `/register/` stays
      Draft until every test passes. T16 (nonce-only POST creates nothing) proves the old path is dead.
- [ ] **2.7 — `BUG-66.md` Phase C** — migrate the 12 endpoints. **One endpoint per dispatch, not 12.**
      Accept legacy key OR signature during transition, **logging every legacy use**, then remove.
      ⚠ Do not flip 12 endpoints and the whole fleet at once — that is how a boat loses connectivity.
- [ ] **2.8 — `BUG-66.md` Phase D** — remove the blind UPSERT.
      ⚠ **SESSION_LOG records the UPDATE→UPSERT change as deliberate. Find out what needed it before
      reverting**, or this causes a regression. Delete the "is safe" comment with the statement — it is
      safe against duplicate rows, not against unauthorised registration.
- [ ] **2.9 — `BUG-65.md`** — mode **and ownership** together; tier claim-vs-detected audit; server-side
      enforcement of paid **cloud** features only.
      ⚠ `license.json` is `root:root 644` while services run as `d3kos`. **A naive `chmod 600` looks
      like a security fix and silently disables tier detection for paying customers.** T3 guards this.
      ⚠ Local tier forgery stays possible **by design** — document it so nobody "fixes" it later and
      breaks offline-first.
- [ ] **2.10 — BUG-72** — deploy `version-heartbeat.php`. **Gated behind 2.7 and 2.8** by the S131
      decision: BUG-66's fix is a prerequisite, not a parallel task.

**Phase 2 exit criterion:** BUG-66, 78, 65, 63, 77 closed. That is the release gate.

---

## PHASE 1 — Close the remaining defects

- [ ] **1.1 — `PHASE1-test-harness.md`** — do this before anything else in Phase 1. You cannot trust a
      later fix if the suite cannot tell a partial run from a complete one.
      ⚠ `bug30`/`bug36` are `.test.cjs`; the node branch records pass/fail **per file, not per
      assertion**, which is why bug30's depth-priority safety assertions **have never executed.** Add
      per-assertion visibility first, then find out what those three assertions actually say.
- [ ] **1.2 — `PHASE1-contract-test.md`** — the highest-value item in Phase 1. Kills the defect class
      that has recurred **six times** (BUG-29/30/37/38/41/47).
      ⚠ T7 (every regex matches nothing → **FAIL, not pass**) is the assertion that stops the test
      passing by failing to look.
- [ ] **1.3 — `BUG-81-WIZARD.md` Step 0** — correct `doc/CX5106_CONFIGURATION_GUIDE.md`.
      **Local-only file, no GitHub approval needed.** It is the wizard's specification: fix the spec
      before the implementation, or the next person rebuilds the bug.
- [ ] **1.4 — `BUG-81-WIZARD.md` Steps 1–2** — rewrite wizard Step 5 to the ratio model; drop the
      Actisense attribution (use **Matsutec**). Depends on **0.2**.
      ⚠ The lookup is **per engine family** — inboard petrol by cylinders, outboard by **poles**, diesel
      by an undefined "Gear Number". A single cylinder-keyed map is right for petrol inboards and
      **silently wrong for every outboard and diesel.** For those two, the empirical method is the
      *expected* path, not a failure state.
      ⚠ **Never state which direction the ratio scales RPM** — the leaflet does not document it.
- [ ] **1.5 — `BUG-24.md`** — blocked on **G6**. Recommendation: Option A, modelled on
      `alert_watcher.py`. Option B is the trap: it turns "never captures" into "captures sometimes".
- [ ] **1.6 — BUG-53** — covered inside 1.1. Invert the assertion; **keep the anchor-alarm coverage.**
      An anchor alarm that does not fire is a boat dragging onto rocks at 3 a.m.

---

## PHASE 3 — Integration

- [ ] **3.1 — `PHASE3-server-canonical-tree.md` Step 1** — build `deployment/v0.9.9.4-server/` + manifest.
      Depends on **G2**. **Pull the 17 deployed endpoints down and diff them against the repo copies —
      assume nothing.** For `pair-device.php` the deployed copy is the only copy.
      ⚠ Decide BUG-76's canonical naming here. Three documents currently use three schemes; until one is
      chosen, **no community endpoint should be built.**
- [ ] **3.2 — `PHASE3-server-canonical-tree.md` Step 2** — the endpoint contract test.
      ⚠ Sequential requests only. Wordfence is active and blocking; a parallel sweep of 43 endpoints
      looks like a scanner and may block your own IP.
      ⚠ **404 fails. Any 5xx fails. A 200 to an unauthenticated request fails.** Today no endpoint
      returns 200 anonymously — the test's job is to keep that true.
- [ ] **3.3 — `PHASE3-blocked-items.md`** — work each item as its blocker clears (G2/G3/G4).
      **Do not write an implementation spec for any of them before then.** All four are root-cause
      unknown; a spec written now is Tier 1 guessing and Tier 3 faithfully implementing the guess.
- [ ] **3.4** — the functional round-trips (pairing, telemetry, command queue, OTA, WebRTC, PDF).
      ⚠ WebRTC has **no record of ever being validated end to end.** Assess before scheduling effort.

---

## PHASE 4 — Release

- [ ] **4.1 — `PHASE4-release-engineering.md`** — version stamp, Release Package Manifest, pre-clone
      checklist, docs, boat test card.
      ⚠ **Do not start until Phase 2 is closed.** Version-stamping a build whose security gate is unmet
      produces a release that merely looks finished.
      ⚠ Two tests can only fail at release: **a real OTA** (BUG-35's fix has never executed — no OTA has
      ever run) and **booting a sanitised clone with no `cloud-config.json`**, which
      `first-boot-setup.sh` does not create.

---

## PUBLIC-FACING — needs explicit operator approval, sequence early

- [ ] **P1 — publish `docs/CX5106_DIP_SWITCH.md`** — replaces the placeholder already at that path on
      `origin/main`, so no new README links are needed.
- [ ] **P2 — correct `docs/CX5106_CONFIGURATION_GUIDE.md`** on `origin/main`. ⚠ **Highest-impact part of
      BUG-81** — it is public, README-linked, still teaches the 8-switch model, and now that its image
      path is fixed it **visibly contradicts itself**. A stranger following the README today gets wrong
      instructions for their hardware.
- [ ] **P3 — `docs/INSTALLATION.md`** default-credential decision before the repo goes public.
- [ ] **P4 — enable GitHub secret scanning** (currently disabled).
- [ ] **P5 — GitHub Issue sync** (close Step 8) for every bug touched since S130.

---

## STANDING TRAPS — read once, remember all the way through

1. **Derive every spec anchor from the target file, never from a document.** `MASTER_SYSTEM_SPEC`
   section 12.1 describes a build script that does not exist; a spec written from it would have sent
   Tier 3 to edit fiction.
2. **Never cap an audit and call it coverage.** S114's spec listed 17 call sites when there were 30,
   because the audit was piped through `head -30`.
3. **A document that cites evidence is not a document whose evidence has been looked at.** The CX5106
   guide embedded the photo that refutes it — with a broken image path, for the file's whole life.
4. **An unsourced code comment is a hypothesis, not a fact.**
5. **Offline must fail open.** Every cached-credential and cached-tier path: server unreachable means
   keep working, log the staleness, never downgrade.
6. **Guard tests must be proven to bite.** Plant the regression and watch the test fail. A guard that
   is present but non-functional manufactures confidence.
