# ATOMIC SPEC — BUG-60

**Defect:** Blog comments are open to anonymous visitors, with an author-URL field and no anti-spam layer.
**Severity:** MEDIUM · **Tier:** almost entirely **operator clicks** — two checkboxes and one decision.
**Created:** 2026-08-28 (S135) · **Bug record:** `V09994_BUG_FIXES.md` BUG-60

---

## 1. ⛔ THE ENTRY'S ROOT CAUSE IS WRONG — no account is needed

The record says spammers *"create free accounts via `/register/`… each account immediately gains ability
to post comments."* **They do not need one.** Verified as an anonymous, logged-out visitor on
`https://atmyboat.com/say-hello-to-my-little-buddy/`, 2026-08-28:

| Check | Result |
|---|---|
| comment form rendered to anonymous visitor | **yes** (5 occurrences) |
| posts to `wp-comments-post.php` | yes |
| "You must be logged in to post a comment" | **absent** |
| Akismet / reCAPTCHA / hCaptcha / Turnstile / CleanTalk | **none — zero of five** |
| fields offered anonymously | `author`, `email`, **`url`**, `submit` |

⚠⚠ **Therefore BUG-63's device gate does NOTHING for this vector.** It would be very easy — and wrong —
to look at the closed registration path and assume this is solved.

⚠ **The "~5 per day since 2026-08-15" figure is unsupported.** `/comments/feed/` shows **no published
comment later than 17 Apr 2026**. Two of the ten *are* spam and *did* publish live (April).
`Uncertainty flag: the feed lists only APPROVED comments, so it cannot separate "moderation now on" from
"no spam arriving" from "operator deletes fast". comment_moderation is NOT visible in rendered HTML and
was NOT determined.`

## 2. ⛔ STEP ZERO — read the settings before changing them

WP Admin → Settings → Discussion. **Record the current state of both checkboxes in the bug entry
before touching anything.**

**BUG-57's S121 entry recorded a control as effective without checking it, and it was a no-op for nine
days. Do not repeat that here.** Also note the **moderation queue depth** — that is the only real
measure of the current spam rate.

## 3. THE FIX — one wp-admin visit

1. ☑ **"Comment must be approved before appearing"** — as originally planned. Still correct.
2. ☑ **"Users must be registered and logged in to comment"** — **now the strong control, and it was not
   when this bug was written.** Before BUG-63, requiring login was near-useless because bots could
   self-register. **Now a commenter must hold a server-issued code tied to an operator-approved d3kOS
   device.** The device gate does not protect comments by itself — but it turns this one checkbox into a
   hard barrier. Free, one click.
3. **Remove or filter the comment author `url` field, or enable Akismet.** ⚠ Approval-before-publishing
   stops spam reaching *readers*; it does not stop it reaching the *queue*. With no anti-spam layer you
   would trade deleting live spam for deleting queued spam — the same chore this bug was raised about.

⛔ **PHASE 2 of the original plan (reCAPTCHA on `/register/`) is SUPERSEDED — do not do it.**
Registration is not the vector, and CAPTCHA was closed as redundant by operator decision S135 (BUG-57).
It would harden a door the spam never uses.

## 4. TESTS

| # | Test | Pass condition |
|---|---|---|
| T1 | Submit a comment while **logged out** | **refused** — login required |
| T2 | Submit a comment while logged in | lands in the **moderation queue**, not live |
| **T3** | Re-fetch the post page anonymously and grep for `name="url"` | **absent**, or Akismet present |
| T4 | `/comments/feed/` after one week | no new spam authors |
| T5 | A genuine logged-in user can still comment | **no regression** — do not lock out real users |

## 5. DEFINITION OF DONE

- [ ] Both settings' **prior** state recorded before any change
- [ ] Moderation queue depth recorded — the real spam-rate measure
- [ ] Both checkboxes set; `url` field removed or Akismet enabled
- [ ] T1–T5 pass
- [ ] The entry's root-cause section corrected (done S135) so nobody re-links this to registration
