# ATOMIC SPEC — BUG-28 (remaining content: duplicate + unsourced code)

**Defect as logged:** boat Pi diverged from the deploy source; two deploy sources drifted.
**Status change from S131:** the *lab* half is **answered** — repo ↔ lab Pi are byte-identical
(216 files, 0 drift). What remains is duplicate and unsourced code inside the canonical tree itself.
**Tier:** Step 1 is Tier 2 (judgement). Steps 2–3 are Tier 3 (mechanical).
**Created:** 2026-08-24 (S131)

---

## 1. WHAT S131 VERIFIED — the duplicate is resolved

Two `cloud_agent.py` files exist in the canonical tree **and on the Pi**:

| File | Lines | Runs? |
|---|---|---|
| `opt/d3kos/services/cloud_agent.py` | **719** | **No** |
| `opt/d3kos/services/cloud-agent/cloud_agent.py` | **630** | **Yes** — `d3kos-cloud-agent.service` sets `WorkingDirectory=/opt/d3kos/services/cloud-agent` |

They differ by **93 lines**, and the comparison is decisive:

```
unique to the 719-line copy:   def _read_config_files
                               def push_config_snapshot
unique to the 630-line copy:   (nothing)
```

**The larger file is a strict superset.** The running file has no capability the idle file lacks.

### The finding that matters

**`push_config_snapshot` is a working config-backup capability that has never run.** It almost certainly
pairs with `config-backup.php` — one of the 12 endpoints in BUG-66's scope, and the *only* one whose
record notes it checks device existence. The `fi4-config-backup` feature folder holds
`config-backup.php`, `config-backup-status.php` and `config-restore.php`.

**So a config backup/restore feature was built across both platforms and left disconnected on the Pi
side.** That is not a duplicate-file problem; it is an undeployed feature hiding inside one.

⚠ **Do not delete the 719-line file.** The obvious "de-duplicate" action would destroy the only copy of
`push_config_snapshot`. **Promote, don't prune.**

⚠ **Same defect class as BUG-35**, which records three copies of `ota_upgrade.py`, two with different
md5s, at `/opt/d3kos/services/cloud-agent/` (live), `/opt/d3kos/services/` (diverged) and the frozen
`pi_source` tree. **This is a pattern, not an incident:** files in `services/` shadowed by files in
`services/<name>/`, with systemd running the subdirectory copy.

---

## 2. STEP 1 (Tier 2) — decide, then act

For `cloud_agent.py`:

1. **Diff the 93 lines in full** — the def-name comparison proves the superset relationship but not that
   the shared code is identical. Confirm the 630-line file contains no *divergent* edit that the
   719-line file lacks (a bug fix applied only to the running copy would be lost by a naive promotion).
2. If clean: make the **719-line file the single copy** at
   `opt/d3kos/services/cloud-agent/cloud_agent.py` (the path systemd already uses), and delete the
   top-level shadow.
3. **`push_config_snapshot` is then live code that has never executed.** Do **not** enable it as part of
   this fix. Log it as a separate item: *"config snapshot push — built, never wired, needs an endpoint
   contract check against `config-backup.php` before first use."* Turning on an untested upload path to
   production in a de-duplication commit is exactly the kind of scope creep that caused BUG-36.

**Then repeat the same three steps for `ota_upgrade.py` (BUG-35's three copies).** Same shape, same trap.

---

## 3. STEP 2 (Tier 3) — bring unsourced production tooling under version control

Four scripts run in production and exist **only on the Pi** — no version control, no review history. A
fix applied to any of them is lost on the next reflash:

| Script | Size | Referenced by |
|---|---|---|
| `create-image.sh` | 2,640 B | BUG-78 (the image builder) |
| `sanitize.sh` | 12,237 B | BUG-78 (the sanitizer it never calls) |
| `tier-manager.sh` | 4,473 B | BUG-77 (tier detection) |
| `detect-opencpn.sh` | 670 B | BUG-77 / BUG-65 (the Tier 2 filesystem test) |

**Copy each byte-identical into `deployment/v0.9.9.4/opt/d3kos/scripts/` and commit with no edits**, so
the subsequent fix diffs are reviewable. Confirm md5 equality repo ↔ Pi. Regenerate `MANIFEST.md5`.

⚠ **This step is a prerequisite of `BUG-78.md` Step 1 and `BUG-77.md` Step 2.** Both specs already say so.
Do it once, here.

⚠ **`sanitize.sh` must never be executed on a Pi you are working on** — it deletes
`~/.ssh/authorized_keys` and would sever access. Copying it is safe; running it is not.

**Also add to the drift verifier's `EXTRA_ON_PI` check** (`PHASE0-drift-verifier.md` R1) — that check is
what would have surfaced these four automatically, and it is why R1 exists.

---

## 4. STEP 3 (Tier 3) — the two Pi-only configs

`avnav_server.xml` (`/var/lib/avnav/`) and `fleet-push.env` are **not version-controlled**. They travel
with an SD-card clone, but a repo rebuild silently reverts them — and `avnav_server.xml` carries the
BUG-19/20 fix (`fetchAis="true" aisQueryPeriod="5"`) plus the u-blox USB ignore rule that the lab card
lacks.

**This needs an operator decision, not a default:**

| Option | Consequence |
|---|---|
| (a) Mirror into the canonical tree | Version-controlled and drift-checked, but they are genuinely per-Pi (the boat has the u-blox rule; the lab does not), so the verifier will report permanent expected drift |
| (b) Leave Pi-only, document explicitly | No false drift, but a repo rebuild silently reverts the BUG-19/20 fix again — which is how it was lost the first time |
| (c) Mirror a **template** + record the per-Pi delta | Most work; the only option that is both checkable and honest |

**Recommendation: (c).** ⚠ **Do not silently pick one.** The whole reason BUG-19/20 took multiple sessions
is that a config change lived somewhere nobody was tracking.

---

## 5. TESTS

| # | Test | Expect |
|---|---|---|
| T1 | `find` for `cloud_agent.py` in the tree | exactly **1** |
| T2 | `d3kos-cloud-agent.service` `WorkingDirectory` still resolves to the surviving file | pass |
| T3 | Service restarts clean and `systemctl is-active` = active | pass |
| **T4** | **`grep -c push_config_snapshot` on the surviving file** | **1 — proves promotion, not deletion.** The negative test for the trap in section 2 |
| T5 | `ota_upgrade.py` count in the tree | exactly 1; BUG-35's `version.txt` fix still present in it |
| T6 | All four scripts md5-identical repo ↔ Pi | pass |
| T7 | `release-state.sh` reports `EXTRA_ON_PI = 0` for `/opt/d3kos/scripts/` | pass |
| T8 | `MANIFEST.md5` regenerated in the same commit | pass |

**T4 is the one that catches the plausible-but-wrong fix.** "De-duplicate" reads like "delete the one that
isn't running", and doing that quietly destroys a feature.

---

## 6. DEFINITION OF DONE

- [ ] One `cloud_agent.py`, one `ota_upgrade.py`; T4 and T5 pass
- [ ] `push_config_snapshot` preserved and logged as built-but-never-wired — **not enabled here**
- [ ] Four unsourced scripts committed byte-identical; T6 passes
- [ ] `MANIFEST.md5` regenerated; `release-state.sh` clean
- [ ] Operator decision recorded on the Pi-only configs (section 4)
- [ ] BUG-28 entry updated: **lab half CLOSED on the byte-identical evidence; boat half remains open**
- [ ] BUG-35 cross-referenced — same defect class, fixed by the same sweep

## 7. WHAT THIS DOES NOT FIX

- **The boat Pi.** Still ~20 fixes behind and unreachable from the lab. Only a trip or a clone settles it.
- **Enabling config snapshot.** Deliberately deferred; needs an endpoint contract check first.
- **`error_reporting(0)`** and the per-request `ALTER TABLE` in the PHP endpoints — noted in BUG-66 section 0.1,
  logged separately.
