# ATOMIC SPEC — BUG-75

**Defect:** `MASTER_SYSTEM_SPEC` §8.4.2 P1 names a data-ingress URL that 404s.
**Severity:** MEDIUM · **Tier:** operator decision + a one-line doc edit.
**Created:** 2026-08-28 (S135) · **Bug record:** `V09994_BUG_FIXES.md` BUG-75

---

## 1. STATUS — Steps 1 and 2 are DONE. Only Step 3 remains.

- **Step 1** (correct §8.4.2 P1 to the full theme path) — done S131.
- **Step 2** (audit every Pi/Node-RED destination URL against probe results) — **done S135.**
  **No Pi code uses the broken short `/mobile/` form** — the spec error never reached code.
  The audit did find three destinations that 404 for other reasons → **BUG-89**.

⚠ **This entry was logged CORRECTLY.** It recorded both probes and stated that only the full
child-theme path resolves. It was briefly and wrongly listed as an "overturned premise" in S135;
that claim has been retracted. Re-verified 2026-08-28:

```
/mobile/data-ingress.php                                       -> 404
/wp-content/themes/twentytwenty-child/mobile/data-ingress.php  -> 405
```

⚠ `/staging` appears 3× in the Pi tree but is **NOT a BUG-55 regression** — all three hits are inside
`tools/verify-bug55.sh`, the guard script, which necessarily contains the string it searches for.

## 2. STEP 3 — the only open item, and it is an operator decision

**Should a `/mobile/` rewrite alias exist?**

| Option | Consequence |
|---|---|
| **No — recommended** | Delete the short form from the spec. Nothing uses it, the full path works, and an alias is one more thing to keep in sync |
| **Yes** | A deliberate `.htaccess` change on HostPapa — **not** a documentation edit. ⚠ **Sequence AFTER BUG-85**: `/staging/.htaccess` is currently a copy of live's, so rewrite work cannot be tested through a staging path that production serves |

## 3. TESTS

| # | Test | Pass condition |
|---|---|---|
| T1 (if "No") | Grep the spec for `atmyboat.com/mobile/` | 0 hits |
| T2 (if "Yes") | `GET /mobile/data-ingress.php` | 405, matching the full path |
| T3 (either) | `GET /wp-content/.../mobile/data-ingress.php` | still 405 — **no regression** |
| T4 (if "Yes") | Live site unaffected by the new rewrite | `/`, `/about/`, `/register/` all 200 |

## 4. DEFINITION OF DONE

- [ ] Operator decision recorded
- [ ] Spec edited or `.htaccess` changed accordingly — **not both**
- [ ] T1–T4 pass for the chosen branch
- [ ] ⚠ **No evidence links BUG-54's 400 to this. Do not merge the two diagnoses.**
