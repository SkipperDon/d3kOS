# ATOMIC SPEC — BUG-65

**Defect:** `license.json` is unsigned and world-readable. Editing one line — `"tier": 0` → `"tier": 3` —
grants every paid feature. Tier is pushed **down** from the server and never verified **up**.
**Severity:** HIGH — licensing/revenue bypass. Part of the v0.9.9.4 security release gate.
**Tier:** Steps 1–2 are Tier 3 (exact replacements). Step 3 is Tier 1/2 (design + server work).
**Created:** 2026-08-24 (S131)
**Bug record:** `V09994_BUG_FIXES.md` BUG-65

---

## 0. THE CONSTRAINT THAT DECIDES THE DESIGN

**Do not attempt to make the local tier tamper-proof. It cannot be done, and attempting it wastes the
release gate.**

`MASTER_SYSTEM_SPEC` section 12.1: the image is a **free, anonymous, public GitHub Releases download**. It
therefore contains **no per-copy secret**. Any signing key capable of validating `license.json` offline
must be *in* the image, so the attacker has it too. Signature verification against a key the attacker
holds is theatre.

section 6.3.1 makes it worse, and this is **architecturally intended, not an oversight**: tier is a filesystem
test. `mkdir /opt/opencpn` grants Tier 2. `touch subscription.key` grants Tier 3. No file to sign is even
involved.

**Therefore the only defensible fix is: enforce paid features server-side, where the secret lives.**
This is option 2 of the 3 in the bug record, and it is the one that does not contradict offline-first.

⚠ **section 9.2's "No license key validation servers" is stale and was corrected in `MASTER_SYSTEM_SPEC` v4.0
(BUG-79).** Without that correction this spec would appear to violate the specification. It does not —
it matches what the system already does (Stripe webhooks, central sync, fleet management).

---

## 1. WHAT S131 VERIFIED LIVE

```
license.json        mode 644   owner root:root   "tier": "T3"
/opt/opencpn        EXISTS          -> detectTier() would return 2
subscription.key    ABSENT          -> the only documented path to Tier 3
```

**The Pi claims Tier 3 while the documented logic would return 2, and nothing notices.** That is the bug,
demonstrated — not theorised.

Two further findings:

1. **The deployed value is the string `"T3"`, not the integer the spec shows**, plus six undocumented
   fields (`subscription_status`, `subscription_expires_at`, `testing_mode`, `upgrade_method`,
   `upgraded_at`, `version_installed_at`). `tier_service.py:28`'s `_parse_tier()` already tolerates both
   forms — **reuse it, do not write another parser** (see BUG-77 section 2).
2. **Mode 644 is written in two places, and both must be fixed** or the next reset re-creates it:
   - `first-boot-setup.sh:147` — `chmod 644 /opt/d3kos/config/license.json`
   - `sanitize.sh` STEP 8 — `chmod 644 "$LICENSE_FILE"` (also covered by BUG-78 D3)

   Fixing one and not the other is the likeliest way this bug silently returns.

---

## 2. STEP 1 (Tier 3) — close the world-readable hole

Two identical replacements, different files.

**A — `first-boot-setup.sh`** `old`: `    chmod 644 /opt/d3kos/config/license.json`
→ `new`: `    chmod 600 /opt/d3kos/config/license.json`

**B — `sanitize.sh`** — same change; **already specified in `atomic-specs/BUG-78.md` section 3.1.** Do it once,
there. Do not apply it twice.

⚠ **Verify which user each consumer runs as before changing the mode.** `tier_service.py` (port 8093) and
`app.py` (dashboard) both read the file; `license.json` is owned **root:root** while the services run as
`d3kos`. **At 644 they can read it; at 600 they cannot.** So this replacement, applied alone, **breaks
the tier service.** The correct change is mode **and** ownership together: `chown d3kos:d3kos` +
`chmod 600`, matching what `sanitize.sh` STEP 8 already does for ownership.

**This is the trap in this spec.** A naive `chmod 600` looks like a security fix and silently disables
tier detection — which fails to Tier 0 and disables paid features for a paying customer. Test T3 exists
for exactly this.

⚠ Mode 600 raises the bar only. The owner can still edit it. **This step alone does not fix BUG-65** —
it is hygiene, and it is listed first only because it is cheap.

---

## 3. STEP 2 (Tier 3) — make forgery visible

Local tier cannot be prevented; it **can** be detected. The server already receives a tier claim on every
sync — it simply never checks it (`export_worker.py:204-218`, `cloud_agent.py:292-300,405-425` push tier
down and never verify up).

Add to the export/heartbeat payload, alongside the claimed tier:
- `tier_claimed` — from `license.json`
- `tier_detected` — the result of `detectTier()` right now
- `opencpn_present`, `subscription_key_present` — booleans

**Server-side:** if `tier_claimed > tier_entitled` (from the Stripe subscription record), write an audit
row and flag the device. **Do not auto-downgrade.** A false positive at sea would strip a paying
customer's features mid-passage. Flag for human review; that matches the approval-queue anchor used
everywhere else in this design.

**Cheap, high value:** this is a handful of extra JSON fields and one server-side comparison, and it turns
an invisible bypass into a reviewable list. Do it even if Step 3 is deferred.

---

## 4. STEP 3 (Tier 1/2) — server-side enforcement of paid *cloud* features

The actual fix. Scope it precisely:

| Feature class | Enforced where | Why |
|---|---|---|
| **Cloud** — sync, export ingestion, PDF/Gemini analysis, fleet management, remote monitoring | **Server** — reject on the entitlement record, ignore the Pi's claim | The server holds the secret. This is where revenue is |
| **Local** — voice assistant, camera, gauges, boat log, charts | **Pi, on the local claim** | Must work with no internet. Offline-first is a hard requirement, and a forged local tier costs nothing recurring |

So: a forged `"tier": 3` still turns on voice and camera locally. **That is an accepted outcome**, not a
gap — it costs nothing per use, and enforcing it would require the impossible offline validation ruled out
in section 0. It must be written down, because otherwise a future session will "fix" it and break offline-first.

**Source of truth:** the Stripe subscription record, which is where money actually is. `tier_service.py:42`
notes `FEATURE_MATRIX` "mirrors data-ingress.php feature_matrix" — **there are already two matrices, one
per platform. Reconcile them before adding enforcement**; if they disagree, the two sides differ on what a
paid tier includes. Verify, and log a new bug if they differ.

---

## 5. TDD TESTS

| # | Test | Expect |
|---|---|---|
| T1 | Hand-edit `license.json` to `"tier": 3`, call a **cloud** endpoint | **rejected on the server's entitlement record** — the core fix |
| T2 | Same edit, use a **local** feature | **works** — documents the accepted limitation deliberately |
| **T3** | After the mode change, `tier_service.py` and `app.py` still read the file | **passes** — the regression guard for section 2's trap |
| T4 | `license.json` mode is 600 and owner is `d3kos` after first boot **and** after sanitize | pass |
| T5 | `mkdir /opt/opencpn` on a Tier 0 device, then sync | server records a `tier_claimed > tier_entitled` audit row; **device is not auto-downgraded** |
| T6 | Server unreachable, valid subscription cached | cloud features continue per the cache; **no downgrade on a network failure** |
| T7 | `"tier"` as `3` and as `"T3"` both parse identically at all sites | pass (BUG-77 T9 overlaps) |

**T1 and T3 are the pair that matters.** T1 proves the bypass is closed where it costs money; T3 proves we
did not disable tier detection for paying customers while doing it.

---

## 6. DEFINITION OF DONE

- [ ] Mode **and ownership** fixed in both `first-boot-setup.sh` and `sanitize.sh`
- [ ] T3 passes — services still read the file after the change
- [ ] Tier claim vs detection reported and audited server-side (Step 2)
- [ ] Cloud features enforced on the entitlement record, not the Pi's claim (Step 3)
- [ ] The accepted local-forgery limitation written into `MASTER_SYSTEM_SPEC` section 9 so it is not "fixed" later
- [ ] Pi/server `FEATURE_MATRIX` reconciled; mismatch logged as a new bug
- [ ] No auto-downgrade path exists anywhere (T5, T6)

## 7. WHAT THIS DOES NOT FIX

- **Local tier forgery.** By design — see section 0 and section 4. Accepted, documented, tested (T2).
- **BUG-77.** Tier 1's definition is separate; this spec covers 2 and 3.
- **BUG-66.** Different credential, different defect. BUG-66 must land first, since Step 2's audit
  reporting travels over the channel BUG-66 authenticates.
