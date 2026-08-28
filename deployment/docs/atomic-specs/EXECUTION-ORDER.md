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

## OPERATOR GATES — restored and re-scored 2026-08-28 (S135)

⚠ **S134 deleted the GATE 0 table as "all cleared" while items 1.5, 3.1 and 3.3 still referenced
G2/G3/G4/G6.** Those references were dangling for four sessions. Restored here with current status.

| # | Gate | Status 2026-08-28 | Blocks |
|---|---|---|---|
| G1 | Inspect the released `.img` for a live `AMBOAT_API_KEY` | ✅ CLEAR (S133) | — |
| **G2** | **Main FTP access to `public_html`** | ✅ **CLEARED S135** — the `d3kos@` account reaches the web root; used throughout S135 | was 4 of 5 Phase 3 items |
| **G3** | **HostPapa nginx error log** | ⛔ **STILL BLOCKED** — outside the web root, FTP cannot reach it | BUG-54 Part 2's final answer |
| **G4** | **Stripe dashboard check** | ⚠ **DOWNGRADED urgent → routine (BUG-73 closed NOT A BUG)** — the webhook exists, is wired and verifies signatures | BUG-73 verification only |
| G5 | Install `poppler-utils` | open | CX5106 manual readability |
| **G6** | **BUG-24 design decision** | ✅ **CLEARED S135 — operator chose Option A** | item 1.5, now unblocked |
| G7 | BUG-57 partial close — REST user enumeration returns 403 | ✅ confirmed | record accuracy |
| **G8** | **MailPoet Q3: is "auto-create WordPress user on subscribe" enabled?** | ⛔ **OPEN — one screenshot.** If YES, BUG-57 goes back to CRITICAL and the device gate does not close it | BUG-57 closure |
| **G9** | **Count users with missing/falsy `atmyboat_tier`** | ⛔ **OPEN** — decides whether closing BUG-91's fail-open is safe or an outage | BUG-91, then BUG-65 Step 3 |
| **G10** | **Which `amboat_registration_audit` table exists in the live DB** | ⛔ **OPEN** — one `SHOW TABLES` | BUG-90 |
| **G11** | **Rotate the two FTP passwords** | ⛔ **OPEN** — they are in the S135 transcript twice | commit handoff item 0.5 B1a |

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
- [ ] **0.5 — `S135-COMMIT-HANDOFF.md`** — commit the uncommitted `/home/boatiq` and `atmyboat-forum`
      working trees. **Do this first in the next session.** `Helm-OS` is clean; the other two are not,
      so AAO §17 currently has no valid rollback baseline for them.
      ⚠ `atmyboat-forum/…/mobile/crm-config.php` is **untracked, credential-bearing, and NOT matched by
      the existing `.gitignore`.** A blanket `git add -A` commits it. Do A1 before staging anything.
      ⛔ `/home/boatiq` has **no remote and must never get one.**

---

## PHASE 2 — THE SECURITY RELEASE GATE

Operator decision: security first. This runs before Phase 1.

- [x] **2.1 — `BUG-78.md`** (CRITICAL) ✓ DONE S134 2026-08-25 — 6/6 PASS incl. T5 (Pi md5) + deploy.
      ⚠ §12.1 spec reconciliation still pending (Step 6).
- [x] **2.2 — `BUG-74.md`** ✓ DONE S134 2026-08-25 — 7/7 PASS incl. T5 (mode 600) + T7 (services active).
- [x] **2.3 — `BUG-66.md` Phase A** ✓ DONE S134 2026-08-25 — 12/12 PASS. 4 tables (A1), shared verifier
      device-auth.php (A2), 3 REST endpoints enrol/status/request-code (A3), wp-admin approval queue (A4).
      Plugin: d3kos-device-auth.php — REST registration + dbDelta table creation. Commit 2f3dd7ea.
      ⚠ Awaiting HostPapa staging deploy and operator APPROVED before server goes live.
      ⚠ Server before Pi. A Pi enrolling against a server with no tables fails closed, which is safe.
- [x] **2.4 — `BUG-66.md` Phase B** ✓ DONE S134 2026-08-25 — 10/10 PASS. `regenerate-identity.sh`
      step 4 generates `device-signing.key` (0600, 32 bytes raw Ed25519) + `device-signing.pub` (0644);
      SIGNING_KEY_FAILED gates sentinel. `device_sign.py` provides `sign_device_request()` and
      `get_public_key_b64()`. Commit e14fb26d.
- [x] **2.5 — `BUG-77.md`** ✓ DONE S134-cont 2026-08-25 — 9/9 PASS. `device_is_paired_and_approved()` +
      `detect_tier()` in tier_service.py; offline-first cache (tier1-approval.json mode 600);
      fail-closed on no-cache+unreachable; license.json cannot grant Tier 1 (T8). tier-manager.sh
      ordering fixed (subscription.key first). app.py parse sites deduped via _parse_tier(). Commit 1facb1b2.
      ⚠ NOTED: data-ingress.php FEATURE_MATRIX not in canonical tree — comparison cannot be done
      without a live HostPapa read. Log as new bug if values disagree.
- [x] **2.6 — `BUG-63.md`** ✓ DONE S134-cont 2026-08-25 — 11/11 PASS. device-registration.php: atomic
      SELECT FOR UPDATE + UPDATE WHERE status='valid'; rollback + audit helpers. page-register.php: alias
      replaces email-derived username; legal name → private user_meta; code_input required; claim-then-create
      enforces T16; rollback on wp_create_user failure enforces T17. Commit d9915753.
      ⚠ Step 3 (bulk-delete 62k rows + republish /register/) is HIGH-RISK — NOT executed. Requires explicit
      operator APPROVED before proceeding.
- [x] **2.7 — `BUG-66.md` Phase C** ✓ DONE S134-cont 2026-08-25 — 9/9 PASS. verify_device_request_server()
      added to device-auth.php (plain PHP, reads $_SERVER); verify_device_request() now nullable-arg for
      backward-compat; legacy key path retained + every use logged to amboat_registration_audit
      event='legacy_key_used'. 6 Pi→Server endpoints migrated: version-heartbeat, failure-report,
      fix-confirmed, community-markers-write (Pi path), community-position, config-backup. Commit 5fae9a91.
      ⚠ OBSERVATION: fleet-create/join/status/map/analytics/leave use PWA JWT — AMBOAT_API_KEY absent;
      these are out of scope for this replacement (confirmed grep).
- [x] **2.8 — `BUG-66.md` Phase D** ✓ DONE S134-cont 2026-08-25 — 5/5 PASS. version-heartbeat.php:
      UPSERT replaced with UPDATE WHERE device_token=?; 404 unknown_device on affected_rows=0; misleading
      'safe' comment removed. SESSION_LOG S33/S37 origin found: UPSERT added for pre-pairing devices;
      safe to remove now because Phase C auth rejects unknown devices at 401. Commit b94ce203.
      ⚠ Phase A gap: approval handler must INSERT into amboat_devices on approval — without this, approved
      devices get 404 on first heartbeat. BUG-72 deploy gated on this.
- [x] **2.9 — `BUG-65.md`** — Steps 1+2 DONE S134-cont 2026-08-25 — 14/14 PASS.
      Step 1: `first-boot-setup.sh` promoted to canonical tree with `chown d3kos:d3kos` +
      `chmod 600` on license.json (fallback branch line 148-149) + STEP 6 re-assert after chown -R.
      sanitize.sh confirmed already fixed (BUG-78 T8). Step 2: `export_worker.py`
      `_build_ingress_payload()` now appends `tier_claimed`, `tier_detected`, `opencpn_present`,
      `subscription_key_present`. Verifier: `verify-bug65.sh`. Commit pending.
      ⚠ Step 3 (server-side enforcement of paid cloud features) is Tier 1/2 gate — deferred.
      ⚠ Local tier forgery stays possible **by design** — accepted outcome, documented in BUG-65 spec
      section 0 and 4. Do not "fix" it — breaks offline-first.
- [ ] **2.10 — BUG-72** — deploy `version-heartbeat.php`. **Gated behind 2.7 and 2.8** by the S131
      decision: BUG-66's fix is a prerequisite, not a parallel task.
      Phase A gap FIXED S134-cont 2026-08-25: `d3kos-device-auth.php` plugin now (a) creates
      `amboat_devices` in dbDelta, (b) INSERT IGNORE into amboat_devices on approve.
      `amboat_registration_audit` event enum extended with `legacy_key_used` (Phase C).
      verify-bug66-phase-a.sh extended to T14 — 14/14 PASS. Commit pending.
      ⚠ **Deploy still requires explicit operator APPROVED** (HostPapa staging first, then live).
      ⚠ version-heartbeat.php is in `deployment/features/autonomous-agents/php/` — confirm
      HostPapa staging path before deploy.

**Phase 2 exit criterion:** BUG-66, 78, 65, 63, 77 closed. That is the release gate.

---

## PHASE 1 — Close the remaining defects

- [x] **1.1 — `PHASE1-test-harness.md`** — DONE S134-cont 2026-08-25 — commit b6812e37.
      (a) run-all-tests.sh → deprecated shim; T8 clean.
      (b) run-all.sh node branch: per-assertion guard — requires 'ALL ASSERTIONS PASSED' sentinel
      in addition to exit 0; early-exit now reported as EARLY EXIT, not silent pass (T3 PASS).
      (c) bug26: BUG-53 fixed — inverted assertion; BASE_HOST:3002 not localhost:3002; anchor
      coverage retained; regression guard: not.toContain('localhost').
      (d) bug30: stale expectations fixed (BUG-43 imperial) → 13.8 ft / 11.5 ft; safety
      assertions 3-5 executed and passed for the FIRST TIME.
      bug36 already passing — no changes needed.
- [x] **1.2 — `PHASE1-contract-test.md`** ✓ DONE S134-cont 2026-08-25 — `tests/contract-dashboard.spec.ts`.
      C1: extracts SK paths from served instruments.js → validates each against live SK REST tree (EXPECTED_ABSENT
      list with mandatory justification per entry). T7 guard: `expect(paths.length).toBeGreaterThan(5)` — zero
      extractions fail, not pass. Bidirectional: REQUIRED_HANDLED_PATHS guards propulsion.port.* twins (BUG-47).
      C2: extracts DOM IDs from served instruments.js → asserts each exists in rendered DOM. T7 guard:
      `expect(ids.length).toBeGreaterThan(3)`.
      C3: 5 dashboard routes → assert HTTP ≠404 and ≠5xx (BUG-37/41).
      Reads from `BASE_URL/static/js/instruments.js` (served, not repo). Never localhost. Count guards on all
      regex extraction. Fails with specific path name on violation.
- [x] **1.3 — `BUG-81-WIZARD.md` Step 0** ✓ DONE S134-cont 2026-08-25 — corrected `doc/CX5106_CONFIGURATION_GUIDE.md`.
      Correction notice at top with BUG-81 date. Part 1 rewritten: 7+2 block model (Block A = 7-pos binary ratio,
      Block B = 2 independent fields). Engine-to-ratio tables: inboard-gas (cylinders), outboard (POLES, not cylinders),
      diesel (gear number, undefined — empirical if unknown). Q3/Q5/Q6 removed (no such fields on hardware);
      new Q4 asks engine family first. Q7/Q8 unchanged (correct). "located on side, labeled 1-8" sentence corrected.
      Superseded original preserved at end of file (reviewers need it for Step 2 `buildDIPRow1` replacements).
      Cross-links `docs/CX5106_DIP_SWITCH.md` as authority. Manufacturer corrected to Matsutec.
- [x] **1.4 — `BUG-81-WIZARD.md` Steps 1–2** ✓ DONE S134-cont 2026-08-25 — `setup.html` rewritten.
      Replacement A: `cylinderMap`+`buildDIPRow1` → `RATIO_INBOARD_GAS`+`RATIO_OUTBOARD`+`ratioForEngine()`+
      `encodeRatio()`+`buildDIPBlockA()`; `buildDIPRow1` retained as backward-compat alias (twin call sites).
      Replacement B: `buildRow1Key` → states ratio + derivation, not fabricated fields; null-ratio path emits
      empirical-method instruction.
      Replacement C: `buildWhyText` → ratio paragraph + constant-factor diagnostic + tank-sender (correct, retained).
      Replacement D: JS portTitle + 2 static HTML labels: "(8 switches)"→"(7 switches)"; "Row 1"→"Block A".
      Replacement E: `Actisense CX5106`→`Matsutec CX5106` (dropdown option) + ctxTitle (Actisense removed).
      Verification: cylinderMap=0 ✓, Actisense CX5106=0 ✓, (8 switches)=0 ✓, Matsutec CX5106=1 ✓, Block A=13 ✓.
      ⚠ Prerequisite mismatches noted and resolved: P1 expected 1 cylinderMap, found 3 (comment+def+use); P4
      expected 2 (8 switches), found 3 (extra static HTML). Both resolved in the same commit.
      ⚠ Tests T1-T16 (SPEC §4) cannot run until lab Pi is available — test file written S134-cont as TDD remediation: `tests/bug81-cx5106-dip.spec.ts`. Must verify GREEN before deploy.
- [ ] **1.5 — `BUG-24.md`** — **UNBLOCKED. G6 cleared 2026-08-28 (S135): operator chose Option A.**
      Spec rewritten S135 against the live code and lab Pi; ready for Tier 3.
      ⚠ **Model on `predictive_maintenance.py`, NOT `alert_watcher.py`** — S131's recommendation is
      superseded. The predictive service already writes `boatlog_entries` on this exact DB in production
      (72 rows); it is the nearest working thing. *Diff against what works.*
      ⚠ S135 found three further faults in the same path (spec §0): `/api/boatlog/engine-entry` **does not
      exist** so every POST has 404'd since v0.9.2.3; the JS `.catch` hides it; and
      `boatlog-export-api.py` **binds `127.0.0.1`**, so all :8095 calls fail from any remote browser.
      The spec routes around the bind fault on purpose — **BUG-24 is not gated on it.**
      ⚠ The UI read path is part of the fix. `boat-log.html` renders from `localStorage` only, so a
      server-side writer alone leaves the operator seeing nothing. Serve `GET /api/boatlog/entries`
      from **`app.py` (:3000, same origin)**, not :8095.
- [x] **1.6 — BUG-53** ✓ DONE inside 1.1 S134-cont 2026-08-25 — assertion inverted in bug26 spec;
      BASE_HOST:3002 asserted; not.toContain('localhost') regression guard added. Anchor alarm coverage retained.

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


---

## PHASE 5 — S135 FINDINGS (2026-08-28)

**Twelve bugs were investigated one-by-one with live evidence. Six had wrong premises.** Ten new bugs
were logged (BUG-82…BUG-91). Every item below has an atomic spec. **Do them in this order — the
dependencies are real.**

⚠⚠ **THE LESSON THAT GOVERNS THIS PHASE.** BUG-72 (recorded "never deployed" — it is live and returns
401), BUG-73 (recorded "absent from production and repo" — present in both, byte-identical, working),
BUG-71 (recorded "broken endpoint" — not an endpoint), BUG-64 (recorded HIGH privilege-escalation — no
role field exists), BUG-56 (recorded "BUILD task" — the target is a placeholder token). **Every one was
recorded from an inference rather than a read.**
**Probe to find a candidate. Read the file or list the directory to conclude.**
**A status code is a response, not a fact.**

### 5.1 — SECURITY FIRST (operator's standing ordering)

- [x] **5.1 — `BUG-90.md`** (HIGH) — the registration audit trail has **never recorded a row**.
      `device-registration.php:121` applies `$wpdb->prefix` to a deliberately unprefixed table.
      ⛔ **Gated on G10** — read the live DB first. If neither table exists, a consumer-only fix writes
      nowhere and makes the bug *look* closed.
      ⚠ BUG-57's root cause included "no audit trail when accounts were created". This is that control.
- [x] **5.2 — `BUG-91.md`** (HIGH, revenue) — the entitlement authority **fails open to Tier 1** and
      discards all four BUG-65 Step 2 audit fields.
      ⛔ **Gated on G9 — count affected users first. Closing the default blind is an outage for paying
      customers.**
      ✅ The BUG-65 §4 FEATURE_MATRIX reconciliation is **done**: 0 value mismatches. No divergence bug.
- [x] **5.3 — `BUG-65.md` Step 3** — server-side enforcement. **Blocked until 5.2 lands.** Building
      enforcement on a fail-open authority inherits the bypass it exists to close.
- [x] **5.4 — `BUG-85.md`** (HIGH) — `/staging/.htaccess` is a copy of live's; every staging page-route
      is served or 301'd by **production**. **Sequence early: staging is not a test environment until
      this is fixed**, and later items want to test there.
      ⚠ `siteurl`/`home` are CORRECT — **do not edit `wpax_options` again.**
- [ ] **5.5 — `BUG-60.md`** — comments are open to **anonymous** visitors with an author-`url` field and
      **zero** anti-spam layers. **BUG-63's device gate does nothing for this vector.**
      ⚠ Requiring login is now a *strong* control **because of** BUG-63 — one checkbox.
      ⛔ Record both settings' prior state before changing them.
- [ ] **5.6 — `BUG-57-MAILPOET.md`** — **gated on G8.** Answer Q3 first; it can re-escalate BUG-57.

### 5.2 — CORRECTNESS

- [x] **5.7 — `BUG-76.md`** ✓ DONE S136 2026-08-28 — canonical names = deployed reality: `data-ingress.php`,
      `community-markers.php`, `community-get.php`. Five retired naming schemes documented. §8.4.4 in
      `doc/MASTER_SYSTEM_SPEC.md` rewritten to v4.1. `deployment/docs/ARCH_SERVICE_MAP.md` lines 204-207
      corrected. `community-api.py` URLs fixed on both Pi and HostPapa. `verify-endpoints.sh` T5+T6 PASS.
- [x] **5.8 — `BUG-89.md`** (HIGH) ✓ DONE S136 2026-08-28 — Part A: new `version.php` created at
      canonical path; format matches `update_agent.py` expected parse `{incremental,major}`; curl PASS.
      Part B: `community-api.py` URL fixes (done in 5.7). Part C: `cloud-link-api.py` `webhook_url` added
      to required list. `deployment/tools/verify-endpoints.sh` created; T5 PASS (4 URLs, 0 failures),
      T6 PASS (planted 404 caught). OTA endpoint now resolves for first time.
- [ ] **5.9 — `BUG-56.md`** — `api-admin.php` is a **placeholder token, not an endpoint**.
      ⛔ **Do not build it.** Two spellings exist, so **no single `proxy_url` value can work.**
      Blocked on reading one config value from the CRM VM (unreachable from the lab 2026-08-28).
- [x] **5.10 — `BUG-71.md`** — three-line `ABSPATH` guard.
      ⛔ **Do NOT add guards to the other 42 `mobile/*.php` files** — they are standalone endpoints and
      guarding them breaks every Pi→server call.
- [x] **5.11 — `BUG-82.md`** ✓ DONE S136 2026-08-28 — §3 answered: kiosk loads `http://localhost/`
      (touchscreen works; remote browsers broken). Option B chosen: 3 proxy routes in app.py
      (`/api/boatlog/status`, `/voice-note`, `/export`). `BOATLOG_API = ''` in boat-log.html.
      `refreshStatus()` checks `r.ok` → visible 'unavailable (HTTP 503)' when service down.
      T1 PASS (78 entries from remote). T5 PASS (visible error shown). Lab Pi deployed.
- [x] **5.12 — `BUG-83.md`** — de-duplicate `alert_watcher.py`. ⛔ **Promote, do not prune** — the root
      copy is the superset and the one systemd runs. **Third instance of the pattern Phase 0.4 missed;
      sweep for more.**
- [x] **5.13 — `BUG-24.md`** ✓ DONE S136 2026-08-28 — Option A. `boatlog_capture.py`: SK REST poll
      5s, 3-sample debounce, direct SQLite write (pattern: predictive_maintenance.py). Systemd unit
      deployed lab Pi (PYTHONUNBUFFERED=1, MemoryMax=128M). `app.py` GET `/api/boatlog/entries`
      (read-only, same origin, sidesteps F3). `boat-log.html` fetches+merges on load; legacy
      localStorage preserved. boatlog-engine.js <script> removed; file kept with RETIRED header.
      T4 PASS: engine row written without page open. T8 PASS: journald within 7s. T13 spec written.
- [x] **5.14 — `BUG-87.md`** (LOW) ✓ DONE S136 2026-08-28 — Wordfence confirmed: only covers
      `/wp-login.php` (maxFailures=20, lockoutMins=240); custom page-my-account.php POST handler unprotected.
      R1: 5-failure transient throttle (`atmyboat_pw_fail_{user_id}`, 15 min) on change_password handler.
      R2: `wp_check_password($pw_del,...)` + `pw_delete` input field on delete_account handler.
      Deployed to `wp-content/themes/twentytwenty-child/page-my-account.php` (24559 bytes). 4/4 PASS.
- [ ] **5.15 — `BUG-88.md`** — **32 production files exist nowhere in the repo.** ⛔ **Do not copy
      production in wholesale** — some repo copies are newer. **Feeds `PHASE3-server-canonical-tree.md`
      Step 1; do this before 3.1.**

### 5.3 — BLOCKED / DECISIONS

- [ ] **5.16 — `BUG-75.md` Step 3** — operator decision: should a `/mobile/` alias exist?
      Recommend **no**. If yes, sequence **after 5.4**.
- [ ] **5.17 — `BUG-54-PART2.md`** — ⛔ **G3 blocked** for the final answer, but **one approved POST**
      splits size-vs-path first. ⚠ **The regression has a date: 2026-04-22.** Export worked for four
      weeks; six hypotheses are eliminated. **Do not re-test them.**

### Phase 5 exit criterion

BUG-90, 91, 85 closed and BUG-65 Step 3 written. Those are the release-gate items; the rest are
correctness and can trail.
