# ATOMIC SPEC — BUG-91

**Defect:** The server-side entitlement authority fails **open** to Tier 1, and discards the tier-audit
fields the Pi sends it.
**Severity:** HIGH — revenue. **Blocks BUG-65 Step 3.**
**Tier:** Tier 1/2 — design + server work. **Not Tier 3.**
**Created:** 2026-08-28 (S135) · **Bug record:** `V09994_BUG_FIXES.md` BUG-91

---

## 0. WHY THIS BLOCKS BUG-65 STEP 3

Step 3's premise is *"enforce paid features server-side, where the secret lives."* **The server-side
authority currently hands Tier 1 features to anyone it cannot classify.** Building enforcement on top of
that inherits the bypass it was created to close. **Fix this first, then write Step 3.**

## 1. THE THREE DEFECTS — live `data-ingress.php`, verified 2026-08-28

```php
148: $tier = amboat_get_user_meta( $user_id, 'atmyboat_tier' ) ?: 'T1';
227: $tier = amboat_get_user_meta( $user_id, 'atmyboat_tier' ) ?: 'T1';
272: $features = $feature_matrix[ $tier ] ?? $feature_matrix['T1'];
```

1. **Fail-open ×2.** `?:` is a *falsy* test — `'0'`, `''`, `0`, `null`, absent-meta all become `'T1'`.
   `:272` repeats it for any key the matrix lacks. **There is no `T0` key**, so Tier 0 cannot be
   expressed, only defaulted away.
2. **Audit fields discarded.** `export_worker.py:239-242` sends `tier_claimed`, `tier_detected`,
   `opencpn_present`, `subscription_key_present`. Grep of the live file for all four → **0 matches.**
3. **7 Pi features have no server key** — `camera`, **`cloud_sync`**, `engine_monitoring`,
   `maintenance_schedule`, `mobile_app`, `predictive_alerts`, `voice_assistant`.

✅ **What is NOT wrong:** the 10 shared features have **0 value mismatches** across T1/T2/T3. The
matrices agree. Do not go looking for a divergence bug — BUG-77's concern is answered.

## 2. ⛔ COUNT BEFORE YOU CLOSE THE DEFAULT

```sql
SELECT COUNT(*) FROM wpax_users u
LEFT JOIN wpax_usermeta m ON m.user_id = u.ID AND m.meta_key = 'atmyboat_tier'
WHERE m.meta_value IS NULL OR m.meta_value = '' OR m.meta_value = '0';
```

⚠ **Changing `'T1'` to `'T0'` without this number is an outage.** Every paying customer whose meta is
missing or malformed loses their features the moment the default closes. If the count is non-zero,
**backfill `atmyboat_tier` from the Stripe subscription record first**, then close the default.

⚠ This runs against **live** data. Read-only `SELECT`. Explicit operator `APPROVED` before any write.

## 3. FIX ORDER — do not reorder

1. **Count** (§2). Backfill if needed.
2. **Add a `T0` row** to `$feature_matrix` — every feature `false` except what a free device genuinely gets.
3. **Close both defaults** — `?: 'T0'` at `:148`/`:227`, `?? $feature_matrix['T0']` at `:272`.
4. **Add the missing feature keys**, `cloud_sync` first — BUG-65 §4 classifies it as server-enforced and
   **the server cannot enforce an entitlement it cannot name.**
   ⚠ Decide whether `mobile_app`/`engine_monitoring` and `live_monitoring` are the same concept.
   **Verify against what each actually gates. Do not assume.**
5. **Build the Step 2 consumer** — persist `tier_claimed` vs the entitlement record; write an audit row on
   mismatch. ⛔ **No auto-downgrade** (BUG-65 T5/T6): a false positive at sea strips paid features.
6. **Correct BUG-65's record** — its Step 2 claim *"mismatch is visible for human review"* is false today.
7. **Then** write BUG-65 Step 3.

## 4. TESTS

| # | Test | Pass condition |
|---|---|---|
| T1 | User with **no** `atmyboat_tier` meta calls a cloud feature | **denied** — served T0, not T1 |
| T2 | `atmyboat_tier = '0'` | **denied** — the falsy-collapse case specifically |
| **T3** | Existing paying **T2** user, unchanged meta | **still has every T2 feature.** ⛔ The outage guard — most important test here |
| T4 | Unknown tier string (`'T9'`) | falls back to **T0**, not T1 |
| T5 | Pi sends `tier_claimed=3` while entitlement says T1 | audit row written; **device NOT downgraded** |
| T6 | Server unreachable, valid cached subscription | cloud features continue — no downgrade on network failure |
| **T7** | **Negative: restore `?: 'T1'`, re-run T1** | T1 **fails** — proves the guard bites |

**T3 is the one that protects customers. T7 is the one that proves the fix is real.**

## 5. DEFINITION OF DONE

- [ ] §2 count obtained and recorded; backfill done if non-zero
- [ ] `T0` row added; both defaults closed
- [ ] `cloud_sync` and the other missing keys present
- [ ] Step 2 consumer built; audit row on mismatch; **no auto-downgrade path anywhere**
- [ ] BUG-65's Step 2 record corrected
- [ ] T1–T7 pass, T3 and T7 explicitly demonstrated
- [ ] Live deploy only with explicit operator `APPROVED`
- [ ] **BUG-65 Step 3 unblocked and written afterwards — not before**

## 6. WHAT THIS DOES NOT FIX

- **Local tier forgery.** Accepted by design — `BUG-65.md` §0 and §4. **Do not "fix" it; it breaks
  offline-first.**
- **BUG-77** — Tier 1's definition, separate entry.
