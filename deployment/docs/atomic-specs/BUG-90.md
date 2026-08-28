# ATOMIC SPEC — BUG-90

**Defect:** `$wpdb->prefix` applied to a deliberately unprefixed table. The registration audit trail has
never recorded a single row.
**Severity:** HIGH — this is the detection control for a repeat of BUG-57.
**Tier:** Tier 3 (one exact replacement) — **but gated on a live DB read first.**
**Created:** 2026-08-28 (S135) · **Bug record:** `V09994_BUG_FIXES.md` BUG-90

---

## 1. PREREQUISITE — abort on mismatch

| # | Check | Expected |
|---|---|---|
| P1 | `grep -n "wpdb->prefix . 'amboat_registration_audit'" deployment/features/auth-pages/php/device-registration.php` | exactly **1** hit, at line **121** |
| P2 | `grep -c "CREATE TABLE IF NOT EXISTS amboat_registration_audit" deployment/v0.9.9.4-server/sql/device-auth-tables.sql` | **1** — unprefixed |
| P3 | `grep -n "wpdb->insert('amboat_registration_audit'" deployment/v0.9.9.4-server/plugins/d3kos-device-auth/d3kos-device-auth.php` | hit at **192**, unprefixed |

If P1 finds 0 or >1, stop and report — the file has changed since S135.

## 2. ⛔ THE GATE — read the live database FIRST

**Do not edit anything until you know which table exists.**

```sql
SHOW TABLES LIKE '%amboat_registration_audit%';
```
against the LIVE DB (`atmyb197_wp59874`, credentials in `wp-config.php` at the FTP root).

| Result | Meaning | Action |
|---|---|---|
| `amboat_registration_audit` present | dbDelta ran; only the consumer is wrong | **Step 3** — the one-line fix |
| `wpax_amboat_registration_audit` present | the convention was abandoned somewhere | **STOP.** Reconcile the convention first; do not blindly strip the prefix |
| **Neither present** | the dbDelta never ran or failed | **STOP.** Fix the creation path. A consumer-only fix writes nowhere and makes the bug *look* closed |

⚠ **This gate exists because the failure is silent.** `$wpdb->insert()` on a missing table returns
`false` and does not throw. Fixing the wrong half produces no error and no audit rows — identical to
today, but marked resolved.

## 3. THE FIX (only if the gate says "unprefixed present")

`deployment/features/auth-pages/php/device-registration.php:121`

```php
old:  $table = $wpdb->prefix . 'amboat_registration_audit';
new:  $table = 'amboat_registration_audit';
```

One line. Nothing else in the file changes.

## 4. SWEEP — do not fix one and stop

`amboat_devices`, `amboat_device_enrolments`, `amboat_registration_codes` and `amboat_device_accounts`
share the unprefixed convention (`device-auth-tables.sql:9-10` documents it).

```
grep -rn "wpdb->prefix . 'amboat_" /home/boatiq/Helm-OS /home/boatiq/atmyboat-forum
```

**Fix every hit. Report the count.** Capping this audit and calling it coverage is STANDING TRAP 2.

## 5. TESTS

| # | Test | Pass condition |
|---|---|---|
| T1 | Register a test account through `/register/` with a valid code | a row appears in `amboat_registration_audit` with `event='account_created'` |
| **T2** | **Read the row back and print it** | **the row exists.** ⛔ "No error in the log" is NOT a pass — that is exactly how this went unnoticed |
| T3 | Submit an invalid registration code | a row with `event='redeem_fail'` |
| T4 | `public_html/error_log` after T1–T3 | **no** `doesn't exist` errors for any `amboat_` table |
| **T5** | **Negative: re-add `$wpdb->prefix .`, run T1** | T1 **fails** — proves the test detects the defect (STANDING TRAP 6) |
| T6 | Grep from §4 returns 0 hits | pass |

## 6. DEFINITION OF DONE

- [ ] Gate answered from a live DB read, result recorded in the bug entry
- [ ] Fix applied only if the gate permits it
- [ ] §4 sweep run, every hit fixed, count reported
- [ ] T1–T6 pass, **T2 by reading the row back**
- [ ] Deploy to live requires explicit operator `APPROVED`
- [ ] BUG-57's entry updated — its "no audit trail" root cause is only now actually closed

## 7. WHAT THIS DOES NOT FIX

- **BUG-63's gate itself** — that works; only its audit half was broken.
- **Retroactive history.** Registrations since 2026-08-25 were never recorded and **cannot be
  recovered.** Say so in the record rather than implying the trail is complete.
