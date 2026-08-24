# ATOMIC SPEC — PHASE 4: Release Engineering for v0.9.9.4

**Purpose:** turn a set of fixes into a releasable, reproducible, rollback-able build — and a clone that
does not ship broken.
**Severity:** gating. Nothing reaches the boat without this.
**Tier:** Tier 2 throughout, except the manifest which is Tier 1 (AAO §9.3 requires judgement).
**Created:** 2026-08-24 (S131)

⚠ **Phase 4 runs LAST for a reason.** Version-stamping a build whose security gate is unmet produces a
release that looks finished. **Do not start until BUG-66, 78, 65, 63, 77 are closed** — the operator has
set security as the v0.9.9.4 release gate.

---

## 1. VERSION STAMPING

**Current live state (lab Pi, read S131) — this is already correct:**

```
d3kOS Version 0.9.9.4
Release Date: unreleased (in development)
Status: In Development
Build: v0.9.9.4-dev
```

All four fields intact, which means **BUG-35's `version.txt` fix is holding.** At release, change
`Release Date`, `Status` and `Build` — and **not** by hand.

⚠ **BUG-35's defect is latent, not dead.** `ota_upgrade.py` step 7 rewrites the whole file as a single
line and truncates three of the four fields. It has never fired, because no OTA has ever run. **The first
real OTA of v0.9.9.4 is the first time that code executes.** Verify the fix through an actual OTA before
release — see §6 T5.

⚠ **BUG-35 also records three copies of `ota_upgrade.py`, two with different md5s.** `PHASE0` /
`BUG-28.md` de-duplicates them. **If that is not done first, the OTA path used at release is unknown.**

Update in the same commit: `DEPLOYMENT_INDEX.md`, `CHANGELOG.md`, `PROJECT_CHECKLIST.md` header.

---

## 2. THE RELEASE PACKAGE MANIFEST (AAO §9.3 — mandatory)

Required in `SESSION_LOG.md` for any session that deploys to a Pi. Full format is in the AAO instructions;
the parts that are routinely got wrong:

- **Partition classification per file** — `base` (`/opt/d3kos/services/`, `/var/www/html/`),
  `runtime` (`/opt/d3kos/config/`, logs, cache), `user-data` (`/opt/d3kos/data/`, preserved through
  rollbacks). Getting this wrong is how a rollback eats user data.
- **Rollback path stated per change**, not once for the release.
- **Health check** — what to verify after deploy. Use `release-state.sh` (Phase 0), not a service list.
- **Plain-language release notes** — one paragraph, for the operator, no jargon.

⚠ **`release-state.sh` output is the evidence, not the deploy log.** The standing rule: *a deploy record
is not evidence.* Attach the before-and-after run.

---

## 3. PRE-CLONE CHECKLIST — the known regressions

The clone is how the boat Pi gets fixed. **Four documented regressions will ship broken if not handled:**

| # | Regression | Action |
|---|---|---|
| 1 | **AvNav charts wiped** — the lab card holds only `osm-online.xml` | Restore charts. ⚠ **o-charts CAac + CAgl expired 2026-04-01** — renew first, or the boat gets a blank chart plotter |
| 2 | **u-blox USB ignore rule absent** from the lab's `avnav_server.xml` | Present on the boat card, absent on the lab card. Without it the USB reader grabs the u-blox at `1-1.4:1.0` and GPS breaks |
| 3 | **BUG-39 identity sentinel clones with the card** — installed DISABLED, so it will not fire | Regenerate identity on the clone, or two Pis share six identity values |
| 4 | **`fetchAis="true" aisQueryPeriod="5"`** — the BUG-19/20 fix lives only in the Pi's `avnav_server.xml`, which is **not version-controlled** | Confirm present on the clone. `BUG-28.md` §4 decides whether these configs get mirrored |

**Plus, new from S131:**

| # | Item | Action |
|---|---|---|
| 5 | **No simulator on the master card** | sksim was uninstalled S114. Re-verify. LAB-SIM never lands on disk by design, so it is safe — **but confirm.** A simulator that can start on a live vessel, injecting fake position and depth underway, is a genuine hazard |
| 6 | **Credential strip** | BUG-78's `sanitize.sh` wiring must be **done and tested** before an image or clone is made |
| 7 | **Keep the boat's original card intact** as the rollback | Non-negotiable |

⚠ **Item 6 and §1 interact:** a sanitised card has no `cloud-config.json`, and `first-boot-setup.sh` does
**not** create one (verified S131 — it creates `license.json` only). Confirm every consumer degrades
gracefully with the file absent, or the clone boots into a broken export path. **BUG-66 §3 flags this;
do not discover it on the boat.**

---

## 4. DOCUMENTATION

- **v0.9.9.4 user manual** — current is `D3KOS_USER_MANUAL_v0992.md`. Tier 3 can draft from the delta;
  Tier 1 reviews.
- **`DEPLOYMENT_INDEX.md`** — every file built or fixed this release must appear. It is the answer to
  "where is the doc for X".
- **`MASTER_SYSTEM_SPEC`** — §12.1 still describes the **fictional** build script. `BUG-78.md` Step 6
  reconciles it with the real `create-image.sh`. **Do not release with the spec describing software that
  does not exist** — that is the defect that produced BUG-78's original mis-diagnosis.
- **§9 security architecture** (BUG-79) — folding the BUG-65/66 design back in is a **release-gate
  deliverable**, not a nice-to-have.

---

## 5. THE BOAT TEST CARD

One line per bug, pass/fail, signed by the operator. Only these genuinely need the boat:

| Item | Why the boat |
|---|---|
| BUG-14 | CX5106 src 106 — ⚠ **S119 verification FAILED**: heartbeat every 60 s, **zero data PGNs with the engine running**. Closed S118 on the tach-wire fix but never re-verified. **Use a candump of ≥130 s** — a shorter capture misses the heartbeat and reads as a dead device |
| BUG-19/20/32 | RTL-SDR dongle is absent from the lab Pi |
| BUG-13/15 | Need real motion — throttle transitions, stationary GPS noise |
| BUG-54 | The boat Pi's `failed_exports/` count — still unchecked, and it alone sets true severity |
| BUG-26/27 | Boat state marked UNKNOWN by `PHASE0-record-integrity.md` A0.3 |
| BUG-25 | Boat hotspot egress |

⚠ **Hardware first, software second.** The S112 cruise validated good fixes against dead hardware and the
conclusion looked like failure. Confirm src 106 is publishing data PGNs **before** judging any engine
gauge.

⚠ **Take `release-state.sh` with a `PI=172.20.10.8` override.** It is what finally answers "what is
actually running on this boat" — the question that consumed S101, S107 and S112.

---

## 6. TESTS

| # | Test | Expect |
|---|---|---|
| T1 | `./tests/run-all.sh --workers=1` | exit **0** — honestly green, or every red quarantined with owner and expiry |
| T2 | `release-state.sh` against the lab Pi | 0 drift, 0 `EXTRA_ON_PI` |
| T3 | `release-state.sh` against the clone | identical to the lab Pi |
| T4 | `verify-bug78.sh` | 6/6, including the negative assertion test |
| **T5** | **A real OTA on a throwaway card, then read `version.txt`** | **all four fields intact** — the only genuine test of BUG-35, which has never executed |
| T6 | Boot the clone with no network | dashboard loads; no crash from absent `cloud-config.json` (§3 item 6) |
| T7 | Boot the clone twice | identity regenerated once; no duplicate `device_token` (BUG-39) |
| T8 | AvNav on the clone | charts render; `fetchAis` active; u-blox rule present |

**T5 and T6 are the two that only fail at release time**, which is why they are here and not in Phase 1.
T7 is the one that fails silently — two Pis with one identity looks fine until the server sees them.

---

## 7. DEFINITION OF DONE

- [ ] Security gate closed: BUG-66, 78, 65, 63, 77
- [ ] `version.txt` stamped; `DEPLOYMENT_INDEX`, `CHANGELOG`, checklist header updated in one commit
- [ ] Release Package Manifest in `SESSION_LOG.md`, with `release-state.sh` before/after as evidence
- [ ] All seven pre-clone items handled and **individually verified**, not assumed
- [ ] T1–T8 pass; T5 run on a throwaway card
- [ ] §12.1 and §9 reconciled with reality
- [ ] v0.9.9.4 manual drafted and reviewed
- [ ] Boat test card written, one line per bug, before the trip
- [ ] Boat's original card retained as rollback

## 8. WHAT THIS DOES NOT COVER

- **The boat trip itself.** This produces the card; the operator works it.
- **The ecosystem features** (community telemetry, Node-RED shared flows, public dashboards,
  leaderboards). Per the S131 scope ruling, v0.9.9.4 = bug fixes plus designed-but-not-deployed work;
  the unbuilt social features are **not** in this release and v0.9.9.5 is not addressable until this
  ships.
- **v1.0.** The security audit gates v1.0 for all three platforms together.
