# Question: BUG-06 — PWA Tier Display Still Shows T1

*Last updated: S62 2026-04-17 | Status: OPEN — blocked pending operator confirmation*

---

## Symptom

PWA still shows T1 after BUG-04 fix (S61 2026-04-16). User's account was upgraded but PWA tier display did not update.

## Background

BUG-04 (FIXED S61): `crm-proxy.php update_tier` was storing bare integers `"0"`–`"3"` due to `int(new_tier)` cast. Fix applied — dropdown values changed to `"T0"`–`"T3"`, Flask validates against set, integer values now rejected with 400. Four staging DB rows patched.

## Hypothesis

PWA may be reading a cached tier value from:
1. Service worker cache (PWA cache v7)
2. `license.json` on Pi not yet updated
3. PWA local storage not invalidated after tier change

## Blocked On

Operator needs to:
1. Confirm the account tier in `wpax_usermeta` is now `"T2"` or `"T3"` (string format)
2. Confirm `license.json` on Pi shows updated string tier
3. Hard-refresh PWA (clear service worker cache) on phone and retest

## Resolution Criteria

Closed when operator confirms PWA displays correct tier after hard refresh.

## Related

- [[entities/tier-system]] — BUG-04 fix details
- [[entities/pwa]] — PWA cache pattern
