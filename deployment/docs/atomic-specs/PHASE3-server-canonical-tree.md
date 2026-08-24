# ATOMIC SPEC — PHASE 3: Server-Side Canonical Tree + Endpoint Contract Test

**Purpose:** give the atmyboat.com half of the system the state tracking the Pi half already has, and a
contract test across the platform boundary.
**Severity:** HIGH — structural. Every Phase 3 integration task depends on knowing what is deployed.
**Tier:** Step 1 Tier 2 (inventory + judgement). Steps 2–3 Tier 3.
**Created:** 2026-08-24 (S131) · **Covers:** A3.0, A3.1, BUG-76's naming decision

---

## 1. THE ASYMMETRY THIS FIXES

| | Pi side | HostPapa side |
|---|---|---|
| Canonical tree | ✅ `deployment/v0.9.9.4/` mirroring real paths | ❌ **none** |
| Manifest | ✅ `MANIFEST.md5` | ❌ none |
| Drift check | ✅ `check-drift.sh` + the new `release-state.sh` | ❌ none |
| Proven current | ✅ **byte-identical, 216 files, 0 drift** (S131) | ❌ unknown |
| Where the code lives | one tree | **~43 PHP files scattered across 8 `features/` folders** |

**This is why "was it built?" cannot be answered from the repo.** The work was done; nothing tracks where
it went. S131's probe found the consequences directly:

- **17 of 20** documented endpoints deployed and correctly rejecting unauthenticated requests
- **`pair-device.php`** — deployed and returning 500, **with no source in the repo at all** (BUG-71)
- **`api-admin.php`, `fix-my-pi-billing.php`** — 404, **no source anywhere** (BUG-56, BUG-73)
- **5 community endpoints** — 404, sources sitting in a `v0941-plan/` folder (BUG-76)

So files run in production with no repo copy, and files are documented that exist nowhere.

---

## 2. STEP 1 (Tier 2) — build the tree, decide the names

**Target:** `deployment/v0.9.9.4-server/` mirroring the live path
`wp-content/themes/twentytwenty-child/`.

**Order matters:**

1. **Consolidate the ~43 PHP files** from the 8 `features/` folders (`auth-pages`, `autonomous-agents`,
   `diagnostic-console`, `fi4-config-backup`, `fleet-management`, `privacy`, `support-tickets`,
   `v0941-plan`) into the tree.
2. ⚠ **Pull the deployed copies down first, for the 17 that are live** — and **diff them against the
   repo copies.** The repo version may be older, newer, or divergent. **Assume nothing.** For
   `pair-device.php` the deployed copy is the *only* copy, and it is the one that is crashing.
   **This step requires main cPanel FTP access** (the `admin@atmyboat.com` account supplied in S131 is
   chrooted to an empty home and cannot read `public_html`).
3. **Generate `MANIFEST.md5`.**
4. **Resolve BUG-76's naming conflict — one decision, three documents.**

   | §8.4.4 (spec) | `ARCH_SERVICE_MAP.md` | Repo |
   |---|---|---|
   | `community-markers-post.php` | `community/markers.php` | `community-markers-write.php` |
   | `telemetry-push.php` | `telemetry/push.php` | — |

   **Recommendation: the flat `community-*.php` / `telemetry-*.php` form**, because it is closest to the
   artifacts that exist and avoids creating subdirectories on shared hosting. **Then correct the other
   two documents.** ⚠ Until this is decided, **no community endpoint should be built** — whichever name
   is chosen, two documents will be wrong, and the Node-RED flows point at a third thing.

⚠ **Do not deploy anything as part of Step 1.** It is inventory and reconciliation only. HostPapa live
changes are per-deploy operator-approved, always.

---

## 3. STEP 2 (Tier 3) — the endpoint contract test

**Target:** `tests/contract-endpoints.spec.ts`

The S131 probe is the baseline. Assert each documented endpoint returns its **expected unauthenticated
response**:

```
register-device.php     405     data-ingress.php      405     dashboard-data.php   401
command-queue.php       401     app-command.php       401     file-manifest.php    401
pdf-store.php           405     pdf-analyze.php       405     list-reports.php     401
fix-my-pi-app.php       405     turn-credentials.php  401     rtc-signal.php       400
watchdog-alert.php      405     offline-check.php     403     support-request.php  405
config-backup.php       405     pair-device.php       ← 500 today; MUST become 401/405
```

**Required behaviour — each of these encodes a lesson:**

- **404 fails.** An endpoint that vanishes is the BUG-56 / BUG-73 defect. This is the primary assertion.
- **Any 5xx fails.** `pair-device.php`'s 500 must be a hard failure, not tolerated as "non-404".
- **200 to an unauthenticated request fails.** Today *no* endpoint does this — that is a genuinely good
  result and the test's job is to keep it true. **A newly-deployed endpoint with a missing auth guard is
  precisely what this catches.**
- **Rate-limit the run.** Wordfence is active and blocking (BUG-67). Sequential requests, no
  parallelism. ⚠ A parallel sweep of 43 endpoints looks exactly like a scanner and may block the
  operator's own IP.
- **`offline-check.php` must stay 403 on GET.** That is BUG-68's fix, confirmed live. This test is its
  non-regression guard.

⚠ **This is an existence-and-guard test, not a functional test.** Confirming an endpoint rejects an
anonymous GET says nothing about whether it works when authenticated. Functional round-trips are §4 and
they need real credentials.

## 3.1 The extra 23

`ARCH_SERVICE_MAP.md` documents 20 endpoints; the repo holds ~43 PHP files. **The remaining ~23 were never
probed** — stated plainly, because 3 of the first 20 turned out absent or broken and the undocumented
remainder is likely to hold more. Probe them in one slow pass as part of Step 2, and **record what was
found rather than what was expected.**

---

## 4. STEP 3 — the functional round-trips (blocked; see the companion spec)

| Test | Blocked on |
|---|---|
| Pairing chain: `register-device` → `pair-device` → `dashboard-data` | **BUG-71** (500) and **BUG-63** (registration disabled) |
| Telemetry: `export_worker` → `data-ingress`, `failed_exports/` = 0 | **BUG-54 Part 2** (nginx 400) |
| Command round-trip: PWA → `command-queue` → `cloud_agent` → ACK | **BUG-28** (the duplicate `cloud_agent.py`) |
| Fix My Pi: `fix-my-pi-app` → Stripe → `fix-my-pi-billing` | **BUG-73** (endpoint does not exist) |
| OTA: `file-manifest` → Pi; `version.txt` survives | BUG-35 fixed in repo, **never through a real OTA** |
| WebRTC: `turn-credentials` + `rtc-signal` + `live_session` | `Uncertainty flag: I found no record of this path ever being validated end to end. Assess before scheduling effort.` |

**Do not write these tests before their blockers clear.** A test that cannot run is indistinguishable from
a test that passes — which is BUG-51's lesson applied across the platform boundary.

---

## 5. TESTS OF THE TEST

| # | Inject | Expect |
|---|---|---|
| T1 | Rename a live endpoint | FAIL naming it (the BUG-56 case) |
| T2 | Deploy a new endpoint with no auth guard, returning 200 | **FAIL** — the guard-regression test |
| T3 | `offline-check.php` reverted to accepting GET | FAIL (BUG-68 guard) |
| T4 | Endpoint returns 500 | FAIL, **not** treated as "exists" |
| T5 | Network unreachable | **FAIL loudly** — never "all endpoints fine" |
| T6 | Full run | completes without triggering a Wordfence block |

**T2 and T5 are the ones that matter.** T2 is the only forward-looking assertion — everything else
re-checks known state. T5 prevents the tool reporting success when it learned nothing, the same failure
mode called out in the drift verifier.

---

## 6. DEFINITION OF DONE

- [ ] `deployment/v0.9.9.4-server/` exists with a manifest, and **deployed-vs-repo diffs recorded** for
      all 17 live endpoints
- [ ] BUG-76 naming decided; the two non-canonical documents corrected
- [ ] The extra ~23 endpoints probed and recorded
- [ ] `contract-endpoints.spec.ts` in `run-all.sh`, T1–T6 verified by injection
- [ ] `pair-device.php` under version control (it is currently unsourced production code)
- [ ] BUG-72's `version-heartbeat.php` deployment still gated behind BUG-66, per the S131 decision

## 7. HARD DEPENDENCY

**Step 1.2 needs main cPanel FTP credentials** (home = `public_html`), or the operator reading the files
via cPanel File Manager. Without file-level access this spec can confirm *whether* an endpoint exists but
never *what it contains* — and `pair-device.php`'s 500 cannot be diagnosed from outside, especially with
`error_reporting(0)` returning an empty body.
