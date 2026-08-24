# ATOMIC SPEC — BUG-77

**Defect:** `detectTier()` can never return Tier 1, yet Tier 1 is a defined tier and the device-tied
registration design gates on it.
**Severity:** HIGH — was blocking the registration design. **Resolution chosen: operator decision S131,
Option (a).**
**Tier:** Step 1 is Tier 1/2 (new function). Steps 2–3 are Tier 3 (exact replacements).
**Created:** 2026-08-24 (S131)
**Bug record:** `V09994_BUG_FIXES.md` BUG-77 · **Spec updated:** `MASTER_SYSTEM_SPEC` §6.3.1 v4.0

---

## 1. THE DECISION

**Option (a):** `detectTier()` returns **1 when the device's `device_token` is paired and
server-approved.** Tier 1 becomes the first **server-verified** tier; Tier 0 stays purely local.

Rationale, recorded so it is not re-litigated: Tier 1 previously meant nothing checkable. Anchoring it
to the approval queue makes one human decision govern both tier and forum registration — closing the
open question at `D3KOS_DEVICE_REGISTRATION_SPEC.md` §12.2 — and removes any dependence on a
world-readable local file that BUG-65 shows is forgeable.

⚠ **This does not close BUG-65.** Tier 2 (`/opt/opencpn` exists) and Tier 3 (`subscription.key` exists)
remain trivially forgeable filesystem tests.

---

## 2. WHAT S131 VERIFIED — three parse sites, not one

The bug record cited `tier_service.py:21,29,128-160` and `app.py:412-417,479-480`. **Live read gives
different line numbers**, so anchors below are derived from the files, not the record:

| Site | File | Lines | Current behaviour |
|---|---|---|---|
| S1 | `services/tier/tier_service.py` | 21, 28, 123, 145 | `LICENSE_FILE` const; `_parse_tier(raw)` **already handles both `0` and `'T0'`**; `/tier/status` returns `license_data.get('tier', 0)` verbatim |
| S2 | `services/dashboard/app.py` | 471–473 | `t = lic.get('tier','T0')`; `tier_num = int(str(t).replace('T',''))` |
| S3 | `services/dashboard/app.py` | 750–758 | `/config/tier` route — the **same** parse repeated |

**Findings that shape the fix:**

1. **Three independent parse sites, two of them duplicated logic.** S2 and S3 are the same four lines
   twice. Any change must hit all three or tiers will disagree between the dashboard, the `/config/tier`
   route, and the tier service. This is the BUG-29 defect class — the same logic in several places,
   drifting.
2. **`_parse_tier()` in `tier_service.py` is the good implementation** and already tolerates the
   `"T3"`-vs-`3` divergence BUG-77 reports. **Do not write a fourth parser — reuse this one.**
   *Diff against the nearest working thing.*
3. **`tier_service.py:42` comments that `FEATURE_MATRIX` "mirrors data-ingress.php feature_matrix".**
   So a server-side tier matrix already exists. That is a fourth copy, on the other platform. **Verify
   the two matrices agree before touching either** — a mismatch means the Pi and the server disagree
   about what a paid tier includes, which is a revenue defect. **Not in this spec's scope; log it if
   they differ.**

---

## 3. STEP 1 (Tier 1/2) — the approval check

New function in `tier_service.py`, near `load_license()`:

```
def device_is_paired_and_approved() -> bool
```

**Required behaviour — each line here is a decision, not a detail:**

| Rule | Why |
|---|---|
| Query `GET /wp-json/amboat-device/v1/status` over the **signed** channel (BUG-66 Phase A/B) | The whole point is that this is server-verified. Do not read `license.json` |
| Cache the result **with its timestamp** in `/opt/d3kos/state/tier1-approval.json` (mode 600) | Needed for the offline rule below |
| **Server unreachable → the cached result stands.** Never downgrade on a network failure | d3kOS is offline-first. A boat at sea must not lose paid function because the marina WiFi dropped. **A tier check that fails closed on a vessel is a safety-adjacent defect, not a security win** |
| Log cache staleness; never act on it silently | Silent degradation is what made BUG-54 invisible for five months |
| `status = "pending"` → **not** Tier 1 | Enrolled ≠ approved. This is the trust anchor |
| No `device_token` at all → Tier 0 | Unpaired device |
| Poll no more than once per 15 min | Shared hosting; 12 endpoints already poll |

⚠ **Dependency: this step cannot be implemented until BUG-66 Phase A3 (`/status`) exists.** Until then,
`device_is_paired_and_approved()` must return `False` — never a stub that returns `True`. A stub
returning `True` grants Tier 1 to every device, which is worse than the bug being fixed.

## 4. STEP 2 (Tier 3) — wire it into `detectTier()`, ordering corrected

Per `MASTER_SYSTEM_SPEC` §6.3.1 v4.0: **Tier 3 is now tested first**, so a subscribed device is never
mis-reported as Tier 2 by the OpenCPN test. Then Tier 2, then the new Tier 1, then Tier 0.

`detect-tier.sh` / `tier-manager.sh` on the Pi hold the shell implementation.
⚠ **`tier-manager.sh` (4,473 bytes) and `detect-opencpn.sh` (670 bytes) exist at
`/opt/d3kos/scripts/` and are NOT in the canonical tree** — same unsourced-tooling class as BUG-78 D4.
**Bring them under version control before editing**, or the fix is lost on the next reflash.

## 5. STEP 3 (Tier 3) — deduplicate the parse sites

Replace S2 and S3's inline `int(str(t).replace('T',''))` with a call to the single parser. Exact `old`
blocks are the four lines at `app.py:471-473` and the equivalent at `750-758` — **derive them from the
file at implementation time**, since earlier line numbers in the bug record were already stale.

---

## 6. TDD TESTS

| # | Test | Expect |
|---|---|---|
| T1 | Approved device, server reachable | tier 1 |
| T2 | **Enrolled but `pending`** | tier 0 — **the trust-anchor test** |
| T3 | No `device_token` | tier 0 |
| T4 | **Approved, then server unreachable** | **tier 1 from cache** — the offline-first test |
| T5 | Never approved, server unreachable, no cache | tier 0 (fail closed when there is nothing to trust) |
| T6 | `subscription.key` present **and** approved | tier 3 — ordering test |
| T7 | `/opt/opencpn` present **and** approved | tier 2, not 1 |
| T8 | `license.json` hand-edited to `"T3"`, device unapproved | **tier 1 is not granted from the file** — proves S1 no longer trusts local state for Tier 1 |
| T9 | All three sites report the same tier for the same state | pass — the duplication guard |

**T2, T4 and T8 are the ones that matter.** T2 proves approval is the anchor; T4 proves we did not trade
a licensing bug for a boat losing features offshore; T8 proves the local file is no longer authoritative.

## 7. DEFINITION OF DONE

- [ ] BUG-66 Phase A3 `/status` exists — this spec cannot complete before it
- [ ] Tier 1 is never granted from `license.json` (T8)
- [ ] Offline behaviour verified with the network actually down, not mocked (T4)
- [ ] All three parse sites agree (T9); `app.py`'s duplication removed
- [ ] `tier-manager.sh` + `detect-opencpn.sh` under version control before edit
- [ ] Pi-vs-server `FEATURE_MATRIX` comparison performed; mismatch logged as a new bug if found
- [ ] `MASTER_SYSTEM_SPEC` §6.3.1 already amended (S131) — confirm code matches spec, not the reverse
