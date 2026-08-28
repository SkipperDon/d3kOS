# ATOMIC SPEC — BUG-88

**Defect:** 32 production PHP files exist nowhere in the repo; plus a dormant parent-theme include that
would fatal every page load if ever required.
**Severity:** MEDIUM · **Tier:** Tier 1/2 — this is the evidence base for `PHASE3-server-canonical-tree.md`.
**Created:** 2026-08-28 (S135) · **Bug record:** `V09994_BUG_FIXES.md` BUG-88

---

## PART 1 — the repo does not know what production runs

| | `mobile/*.php` |
|---|---|
| `atmyboat-forum` repo | **44** |
| Production (FTP listing, 2026-08-28) | **76** |

**32 files run in production with no source anywhere.** BUG-71 was one until commit `13eebcbc`; 31 remain.

This is the measurable form of what **BUG-72**, **BUG-76** and `PHASE3-server-canonical-tree.md` state
abstractly. The Pi side has `MANIFEST.md5` and `release-state.sh`. **The server side has nothing.**

⚠ **Consequences observed in S135 alone — not hypothetical:**
- **BUG-71** — no repo copy to read; the bug survived four sessions partly because of it
- **BUG-64** — three variants of `page-my-account.php`; the theme-repo copy is **stale** while live
  matches the **Helm-OS** copy
- **BUG-56** — repo `crm-proxy.php` is 32 lines / 2 actions; production's is 411 lines / 12 actions
- **BUG-84** — two scratch files sat live for ten days because nothing compares server to manifest

### ⛔ How NOT to fix it

**Do not copy production into the repo wholesale.** `PHASE3-server-canonical-tree.md` Step 1:
**pull the deployed files down and diff them against the repo copies — assume nothing.** Some repo
copies are **newer** than production, some older, and at least one live file matches a *different* repo
than the theme repo. **A blind copy overwrites good source with stale source.**

### ⛔ Do not cap the audit

76/44 is **`mobile/` only**. The rest of the child theme, the plugins directory and `app/` were not
counted. **Count them and report the true total** before claiming coverage (STANDING TRAP 2).

### Method

1. Enumerate production per directory (FTP `LIST`).
2. For each file: present in repo? → `diff`. Absent? → capture **byte-identical, no edits.**
3. Classify each as `repo-newer` / `production-newer` / `identical` / `unsourced`.
4. Commit the unsourced ones in **one commit, unmodified**, before any reconciliation.
5. Feed the result into `PHASE3-server-canonical-tree.md` Step 1 and build the manifest.

## PART 2 — the dormant landmine

`atmyboat-forum/wp-content/themes/twentytwenty-child/inc/atmyboat-functions.php:107`:

```php
require_once get_template_directory() . '/mobile/pair-device.php';
```

`get_template_directory()` is the **PARENT** theme; the file is in the **child**. If this line ever
executes it is an unconditional fatal on **every page load** — **exactly what BUG-86 did to staging on
2026-08-25.**

**Currently dormant** — nothing requires `inc/atmyboat-functions.php` (grep of `functions.php` and
`inc/` returns nothing). The live include is `functions.php:220`, correctly using
`get_stylesheet_directory()`.

**Fix:** delete the dead file if it is dead, or correct line 107. ⛔ **Do not simply leave it** — a dead
file containing a site-killing line is one careless `require` from an outage, and this mistake has
already fired once.

⚠ **Search for other instances before closing.** `get_template_directory()` reaching a child-theme path
is now a known recurring error (BUG-86, and this). **Grep the whole theme; log what turns up.**

## TESTS

| # | Test | Pass condition |
|---|---|---|
| T1 | Production/repo file counts per directory | recorded, all directories, not just `mobile/` |
| T2 | Every unsourced file committed byte-identical | md5 matches production for each |
| T3 | Classification table produced | every file in exactly one of the four classes |
| T4 | `inc/atmyboat-functions.php` deleted or `:107` corrected | pass |
| T5 | `grep -rn "get_template_directory()" theme/` | every hit reviewed; findings logged |
| **T6** | Site still loads; `/register/`, `/my-account/`, `/blog/` all 200 | **no regression from any of it** |

## DEFINITION OF DONE

- [ ] Full production inventory, **all directories**, true total reported
- [ ] 31 unsourced files captured byte-identical in one commit
- [ ] Classification table written into the bug entry
- [ ] Part 2 resolved; repo-wide `get_template_directory()` sweep logged
- [ ] `PHASE3-server-canonical-tree.md` Step 1 updated to consume this
- [ ] ⛔ No blind copy performed
