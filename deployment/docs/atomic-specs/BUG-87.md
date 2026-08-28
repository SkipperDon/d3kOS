# ATOMIC SPEC — BUG-87

**Defect:** My Account actions are unthrottled, and account deletion does not re-prompt for the password.
**Severity:** LOW — hardening. **Neither item is exploitable by an unauthenticated party.**
**Tier:** Tier 3 · **Created:** 2026-08-28 (S135) · **Bug record:** `V09994_BUG_FIXES.md` BUG-87

---

## 0. CONTEXT — the page is otherwise sound

BUG-64 was closed NOT A BUG after a full audit of the live file: no IDOR, no privilege escalation (no
role field exists), email changes de-verify and re-token, password change requires the current password,
no direct SQL, action-scoped CSRF nonces. **These two residuals are what was left.**

⚠ **Edit `deployment/features/auth-pages/php/page-my-account.php`** (live md5 `400fa44e…`).
**The `atmyboat-forum` copy (`a89e7176…`) is STALE.** Editing it changes nothing.

## 1. ⛔ CHECK WORDFENCE FIRST — the fix may already exist

R1 may already be covered by Wordfence rate limiting at the HTTP layer. **Read the Wordfence
rate-limiting configuration before writing any code.** `Uncertainty flag: this was NOT verified in S135
— confirming it means submitting repeated failed passwords against the live site, which was not done.`

If Wordfence already throttles authenticated POSTs to this page, **record that and close R1 with no code.**

## 2. R1 — no throttling

`change_password`, `change_email`, `delete_account` and the data export accept unlimited POSTs from a
valid session. No transient, counter or cooldown exists in the file.

**Concrete failure:** `:92` runs `wp_check_password( $pw_cur, … )` on every submission with no back-off.
A session-holder who does not know the password can **brute-force the current-password field**,
converting temporary session access into permanent takeover (change password → change email).

**Fix:** a per-user transient counter — N failed `wp_check_password` attempts in M minutes → refuse.

⛔ **Fail closed WITHOUT permanently locking the owner out.** A self-service account page that an
attacker can lock is a **denial-of-service on the legitimate user**. Time-boxed back-off only. Never a
permanent lock, never an admin-unlock requirement.

## 3. R2 — deletion needs no password

`:149-158` requires a valid action-scoped nonce and the literal string `DELETE MY ACCOUNT`. Sound against
CSRF and accidents; **not sound against an unattended logged-in session.**

Mitigated already: `:157` `wp_delete_user( $user_id, 1 )` **reassigns content to admin** rather than
destroying posts — blast radius is the account, not its contributions.

**Fix:** require `wp_check_password()` on `delete_account`, reusing the pattern already at `:92` **in the
same file**. Do not invent a second pattern.

## 4. TESTS

| # | Test | Pass condition |
|---|---|---|
| T1 | `change_password` with a wrong current password, N+1 times | request N+1 refused / backed off |
| **T2** | Legitimate user changes password successfully after one failed attempt | **not locked out.** ⛔ The most important test — a throttle that locks the real owner out is worse than no throttle |
| T3 | `delete_account`, correct confirmation string, **wrong** password | **rejected** |
| T4 | `delete_account`, correct confirmation and password | succeeds; content reassigned to user 1 |
| **T5** | **Negative: remove the throttle, re-run T1** | T1 **fails** — proves the guard bites |
| T6 | Password change, email change, export all still work normally | no regression |

## 5. DEFINITION OF DONE

- [ ] Wordfence coverage checked **first**; if it covers R1, close R1 with no code and say so
- [ ] T1–T6 written before the fix; T1 and T3 observed failing pre-fix
- [ ] Edited in the **Helm-OS** copy; the stale `atmyboat-forum` copy reconciled or removed
- [ ] **T2 demonstrated** — no self-DoS
- [ ] Live deploy only with explicit operator `APPROVED`
