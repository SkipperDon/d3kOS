# ATOMIC SPEC — BUG-63

**Defect:** `page-register.php` calls `wp_create_user()` directly, so WordPress's `users_can_register`
setting was never in the path. No CAPTCHA, no honeypot, no rate limit; the nonce is harvestable.
**Severity:** CRITICAL as logged; **contained** since S127 (`/register/` set to Draft). The permanent fix
is a v0.9.9.4 release gate.
**Tier:** Step 2 is Tier 3 (one exact insertion). Steps 1 and 3 are Tier 1/2.
**Created:** 2026-08-24 (S131)
**Bug record:** `V09994_BUG_FIXES.md` BUG-63 · **Design of record:** `D3KOS_DEVICE_REGISTRATION_SPEC.md` v2.0.0 §7.3

---

## 1. GROUND TRUTH — verified in the file, S131

Target: `deployment/features/auth-pages/php/page-register.php`
⚠ **This file is in a `features/` folder, not the canonical tree, and there is no server-side canonical
tree at all (BUG-72).** Establish the deployment path before editing, or the fix goes nowhere.

| Line | Code | Assessment |
|---|---|---|
| 55 | `wp_verify_nonce( wp_unslash($_POST['atmyboat_register_nonce']), 'atmyboat_register_action' )` | Present — and **worthless as a bot control**: a bot GETs the page, scrapes the nonce, posts it back. It prevents CSRF, not automation |
| 84–86 | username built from the email local-part, falling back to `'user_' . wp_generate_password(6)` | **This is the mechanism behind BUG-57's `user12345`-style names.** The 62k bot accounts are this line |
| **88** | `$user_id = wp_create_user( $username, $pw, $email );` | **The defect. `users_can_register` is never consulted** |
| 102 | `update_user_meta( $user_id, 'atmyboat_tier', 'T0' )` | Note: `'T0'` string form — the same divergence as BUG-77 |
| 104 | `update_user_meta( $user_id, 'atmyboat_email_verified', '0' )` | **Gates login, not creation.** The `wp_users` row already exists — which is why 62k rows accumulated despite email verification, and why MailPoet could read them (BUG-57 → BUG-60) |
| 106–107 | 40-char `wp_generate_password` verify token | Adequate |

**Confirmed: unticking "Anyone can register" would have done nothing**, and anyone who did it would have
believed the hole closed while it stayed fully open. That is the most important fact in this entry.

---

## 2. STEP 1 (Tier 1/2) — prerequisite

**BUG-66 Phase A must be complete.** This spec consumes `amboat_registration_codes` and the atomic claim
in registration spec §6.2. Without it there is no code to redeem.

**Do not implement a weaker interim gate.** A CAPTCHA-only stopgap would let `/register/` be republished
while device binding is still absent — and republishing is the thing that must not happen early
(registration spec §8.3). Draft status is the correct control until the real gate ships.

---

## 3. STEP 2 (Tier 3) — the registration-code gate

**One insertion, immediately before line 88.** Everything below line 88 is unchanged.

`old` (exact, single occurrence):
```php
            $user_id = wp_create_user( $username, $pw, $email );
```

`new`:
```php
            // ── BUG-63: device-tied registration gate ─────────────────────────
            // Claim the registration code ATOMICALLY before creating anything.
            // Order matters: claim, then create. Never check-then-act — v1.0.0 of
            // the registration spec had that race (defect V5).
            require_once __DIR__ . '/device-registration.php';
            $claim = amboat_claim_registration_code( $code_input );

            if ( is_wp_error( $claim ) ) {
                $reg_error = esc_html( $claim->get_error_message() );
                amboat_registration_audit( 'redeem_fail', null, $claim->get_error_code() );
            } else {
                $user_id = wp_create_user( $username, $pw, $email );
```

…and close the added `else` after the existing success block, rolling the claim back if
`wp_create_user()` fails so the code returns to `valid`.

**Constraints for the dispatch — each of these is a real failure mode:**

1. **Claim before create, in a transaction.** Registration spec §6.2: `UPDATE … WHERE code_hash = ? AND
   status='valid' AND expires_at > NOW()`, proceed **only if `affected_rows === 1`**. Two simultaneous
   submissions must not both succeed.
2. **On `wp_create_user()` failure, roll the code back to `valid`.** Otherwise a WordPress error burns
   the user's one-time code and they cannot retry.
3. **Bind the account to the device** — insert into `amboat_device_accounts` (D4: exactly one account per
   device) inside the same transaction.
4. **Do not remove the nonce check.** It is not a bot control but it is a valid CSRF control.
5. **Do not touch lines 90–110.** Names, tier meta, CASL consent and the verify token all stay.

## 3.1 Also required — the §7.3 form fields

Registration spec §7.3 requires **legal name** (private, `user_meta.atmyboat_legal_name`, admin-visible
only) and **display alias** (public `display_name`). Line 84's email-derived username must be replaced by
the alias.

⚠ **Enforce with a test that the legal name never appears in any public HTML** (spec test T15). This is
the one requirement most likely to be quietly missed, and it is a privacy commitment.

⚠ **Honest limitation, from the spec and worth repeating:** "real name required" is an accountability
control, **not a bot filter**. No software can tell that "Robert Smith" is genuine. The prevention is the
approval queue; the name is what lets you ban a person and know who they were. **Do not let anyone
describe this field as anti-bot.**

---

## 4. STEP 3 (Tier 1/2) — migration and republish

Per registration spec §8, in order:

1. Export the ~62k unverified Subscriber rows (`atmyboat_email_verified = '0'`) for the record, **then**
   bulk-delete. Export first — they are BUG-57 evidence.
2. Flag genuine existing users `atmyboat_legacy = 1`; keep access; prompt for alias + legal name at next
   login. **Do not force device binding retroactively** — existing users have no device.
3. **`/register/` stays in Draft until every test below passes.** It is the live hole.

⚠ **The vulnerable template remains on disk while in Draft — one status change from live.** Draft is a
stopgap, not a fix. Anyone with wp-admin can re-expose it by accident.

---

## 5. TDD TESTS — registration spec §9 T8–T15, plus two

| # | Test | Expect |
|---|---|---|
| T8 | Redeem a valid code | account created; alias public; **legal name absent from page source** |
| T9 | Redeem the same code twice | second fails; **exactly one** user exists |
| T10 | Two concurrent redemptions of one code | exactly one succeeds |
| T11 | Redeem at 15 min + 1 s | expired |
| T12 | Second code request for a device that already has an account | 403 `already_registered` (D4) |
| T13 | 11 submissions from one IP in an hour | 11th → 429 |
| T15 | Legal name never appears in any public HTML | pass |
| **T16** | **POST directly to the template with a valid nonce and no code** | **rejected — no user created.** This is the BUG-63 regression test: it is exactly what the 62k bots did |
| **T17** | **`wp_create_user()` forced to fail after a successful claim** | code returns to `valid`; no orphan row |

**T16 is the test that proves BUG-63 is fixed.** T8–T15 prove the new flow works; only T16 proves the old
one is dead.

---

## 6. DEFINITION OF DONE

- [ ] BUG-66 Phase A complete (hard dependency)
- [ ] T16 passes — a nonce-only POST creates nothing
- [ ] T17 passes — no code is burned by a WordPress failure
- [ ] Legal name proven absent from public HTML by test, not by inspection
- [ ] 62k rows exported **before** deletion
- [ ] Deployment path established (BUG-72) — this file is not in any canonical tree
- [ ] `/register/` republished **only** after all of the above, with explicit operator approval
- [ ] BUG-57 and BUG-60 re-assessed — this fix removes their root supply of accounts

## 7. WHAT THIS DOES NOT FIX

- **BUG-64** — `/my-account/` security. Registration spec §7.4 explicitly holds it out of scope and warns
  it "must not be assumed done." S131 verified only that `/my-account/` redirects to `/login/`; role
  escalation, email-change verification and rate limiting are **untested**.
- **BUG-57's MailPoet vector.** This stops new bot accounts. How MailPoet was accessed is unresolved.
- **BUG-60.** Comment moderation is a WordPress setting, separate.
