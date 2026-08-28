# ATOMIC SPEC — BUG-71

**Defect:** `pair-device.php` has no `ABSPATH` guard, so a direct HTTP fetch executes it outside
WordPress and fatals.
**Severity:** LOW · **Tier:** Tier 3 — one insertion, three lines.
**Created:** 2026-08-28 (S135) · **Bug record:** `V09994_BUG_FIXES.md` BUG-71

---

## 1. ⛔ READ THIS BEFORE TOUCHING ANYTHING ELSE IN `mobile/`

`pair-device.php` is a **WordPress AJAX handler registration file**, not an endpoint. `:20` is
`add_action('wp_ajax_atmyboat_confirm_pairing', …)`; `functions.php:220` requires it. A direct fetch
runs `add_action()` outside WordPress → undefined function → fatal → **HTTP 500, empty body**
(confirmed in the live log: `[28-Aug-2026 11:11:50] Call to undefined function add_action() … line 20`).

⛔ **42 of 44 `mobile/*.php` files also lack `ABSPATH`. DO NOT ADD GUARDS TO THEM.** They are standalone
REST endpoints meant to be fetched directly — `data-ingress.php` (405), `version-heartbeat.php` (401).
**Guarding them breaks every Pi→server call.**

**`pair-device.php` is the only file in `mobile/` that is an include AND lacks the guard.** Audited: one
file has a top-level `add_action`/`add_filter` with no `ABSPATH` reference.

## 2. PREREQUISITES — abort on mismatch

| # | Check | Expected |
|---|---|---|
| P1 | Source is under version control byte-identical | ✅ commit `13eebcbc`, md5 `b3ccd9f34d04a3c43a88eabd1aec4e1d` |
| P2 | `grep -c ABSPATH deployment/v0.9.9.4-server/mobile/pair-device.php` | **0** |
| P3 | `grep -n "add_action" …/pair-device.php` | line **20** |
| P4 | `grep -n "mobile/pair-device.php" atmyboat-forum/…/functions.php` | line **220**, `get_stylesheet_directory()` |

## 3. FIX

Insert after the closing `*/` of the header comment, before line 20:

```php
if ( ! defined( 'ABSPATH' ) ) {
    exit;
}
```

**Operator decision — one of:**
- **Silent `exit`** (above): matches `enrol.php`; a direct fetch returns empty 200.
- **Explicit 403:** `if ( ! defined('ABSPATH') ) { http_response_code(403); exit; }` — better practice.

Cosmetic either way. Default to silent `exit` for consistency unless told otherwise.

## 4. TESTS

| # | Test | Pass condition |
|---|---|---|
| T1 | `GET …/mobile/pair-device.php` | **not 500** (200 or 403 per the choice above) |
| T2 | `public_html/…/mobile/error_log` after T1 | **no new** `Call to undefined function add_action()` |
| **T3** | Pairing still works via `admin-ajax.php?action=atmyboat_confirm_pairing` | **the regression guard** — the guard must not break the real path |
| **T4** | **Negative: remove the guard, re-run T1** | T1 **fails** (500 returns) — proves the guard bites |
| T5 | `functions.php:220` require still resolves; site loads | pass |

⚠ **T3 is mandatory.** An `ABSPATH` guard is safe *because* WordPress defines `ABSPATH` before the
require — verify that rather than assuming it.

## 5. DEFINITION OF DONE

- [ ] P1–P4 pass
- [ ] Guard added; T1–T5 pass with T4 demonstrated
- [ ] ⛔ No other `mobile/*.php` file touched
- [ ] Live deploy requires explicit operator `APPROVED`
- [ ] `PHASE3-blocked-items.md`'s "critical path" claim stays corrected (done S135)
