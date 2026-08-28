# ATOMIC SPEC — BUG-85

**Defect:** `/staging/.htaccess` is a verbatim copy of the live site's. Every staging page-route is
served or 301'd by **production**.
**Severity:** HIGH — staging has not been a test environment for any page-based route.
**Tier:** Tier 2/3 — one file, but on a live host. **Deploy needs explicit operator `APPROVED`.**
**Created:** 2026-08-28 (S135) · **Bug record:** `V09994_BUG_FIXES.md` BUG-85

---

## 1. PROVEN BEHAVIOUR — 2026-08-28

```
GET /staging/about/        -> 301 -> https://atmyboat.com/about/      (LIVE)
GET /staging/blog/         -> 301                                      (LIVE)
GET /staging/<random>.php  -> 404 page whose assets are ALL at the live root
                              (18x atmyboat.com/wp-content/, 0x /staging/wp-content/)
GET /staging/              -> 200, correct /staging/ assets   (index.php is a REAL file)
```

## 2. ROOT CAUSE

`/staging/.htaccess`:
```
39: RewriteBase /                  <- must be /staging/
43: RewriteRule . /index.php [L]   <- must be /staging/index.php
57: php_value auto_prepend_file '/home/atmyb197/public_html/wordfence-waf.php'   <- LIVE's WAF
```
Non-file, non-directory requests under `/staging/` are rewritten to the **live** `index.php`.

## 3. ⛔ WHAT IS NOT THE CAUSE — do not touch these

⚠ **`siteurl` and `home` are CORRECT.** The staging homepage renders **0** occurrences of
`staging/staging`; every asset, the canonical and `wp-json` resolve to `/staging/`. `wp-config.php`
defines **neither** `WP_SITEURL` nor `WP_HOME` (read 2026-08-28).

**Previous sessions edited `wpax_options` chasing this symptom. Do not repeat it.** The DB is right;
the rewrite is wrong.

⚠ **Staging's DB is `atmyb197_wp5888`, not `atmyb197_wp302`.** That misrecorded name is why those
credentials read as "broken".

## 4. PREREQUISITES — abort on mismatch

| # | Check | Expected |
|---|---|---|
| P1 | `/staging/.htaccess` contains `RewriteBase /` on its own line | present |
| P2 | Same file contains `RewriteRule . /index.php [L]` | present |
| P3 | `GET /staging/about/` | 301 to `atmyboat.com/about/` |
| P4 | `GET /staging/` | 200, and `staging/staging` count is **0** |

If P3 already returns staging content, someone has fixed it — stop and re-verify.

## 5. FIX

⛔ **Back up `/staging/.htaccess` to `.aao-backups/` and md5-verify BEFORE editing.** A bad rewrite rule
takes the entire path down, and you will be editing the file that serves the recovery route.

```
RewriteBase /staging/
RewriteRule . /staging/index.php [L]
```

Then repoint or remove line 57's `auto_prepend_file` so staging uses **staging's** `wordfence-waf.php`,
not live's.

**Preferred method:** log into **staging's** wp-admin → Settings → Permalinks → Save. WordPress
regenerates the block correctly for a subdirectory install. ⚠ **Blocked today** — `/staging/wp-admin/`
is unreachable (see §7). If it stays blocked, hand-edit.

## 6. TESTS

| # | Test | Pass condition |
|---|---|---|
| **T1** | `GET /staging/about/` | returns **staging** content. ⛔ **A 200 alone is NOT a pass — production returns 200 too.** Assert an asset URL contains `/staging/wp-content/` |
| T2 | `GET /staging/` | still 200, assets still `/staging/` — no regression |
| T3 | `GET /staging/<random>.php` | 404 from **staging**, not a live-asset 404 page |
| T4 | `GET /` and `/about/` | live site unaffected |
| **T5** | **Negative: restore `RewriteBase /`, re-run T1** | T1 **fails** — proves the assertion bites |
| T6 | Rollback drill: restore the backup, confirm `/staging/` still 200 | pass |

**T1's asset assertion is the whole test.** Checking the status code is what let this hide.

## 7. KNOWN UNRESOLVED — do not claim this spec covers it

`/staging/wp-admin/` → 301 → `/staging/staging/wp-login.php`. **`wp-admin` is a real directory, so the
rewrite should not fire on it.** Cause unidentified.

`Uncertainty flag: this spec may or may not fix wp-admin. Re-test it after the change. If it still
doubles, that is a SEPARATE defect — log it rather than folding it in here.`

## 8. DEFINITION OF DONE

- [ ] Backup taken, md5-verified, path recorded in chat
- [ ] P1–P4 pass before editing
- [ ] T1–T6 pass, T1 asserting on **assets** not status
- [ ] `/staging/wp-admin/` re-tested; if still doubled, logged as a new bug
- [ ] Explicit operator `APPROVED` before the upload
- [ ] Every past "verified on staging" claim for a page route flagged for re-verification
