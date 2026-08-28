# ATOMIC SPEC — BUG-56

**Defect:** The CRM derives every endpoint URL by string-replacing a filename out of `proxy_url`. Since
S58 the replace matches nothing, so every call lands on `crm-proxy.php` and gets `400 Unknown action`.
**Severity:** MEDIUM · **Tier:** Tier 1/2 — a design change across 5 CRM modules.
**Created:** 2026-08-28 (S135) · **Bug record:** `V09994_BUG_FIXES.md` BUG-56

---

## 1. ⛔ `api-admin.php` IS NOT AN ENDPOINT — DO NOT BUILD IT

It is a **placeholder token inside a config string**. S131 probed it, got 404, and concluded *"this is a
BUILD task."* **Writing `api-admin.php` would create a file to satisfy a token, and the CRM still would
not call it.** All nine real targets already exist in production.

## 2. THE MECHANISM

```python
_issues_url = config["proxy_url"].replace("api-admin.php", "issue-api.php")   # app_patched.py:38-83
```
`DEPLOYMENT_INDEX.md:1226`: **S58 changed `proxy_url` to `.../mobile/crm-proxy.php`.** `str.replace()`
on a non-match returns the original — silently. Every call then POSTs to `crm-proxy.php`, whose 12
actions do not include the intended one, so `:404-405` fires `http_response_code(400); 'Unknown
action: …'`. **That is the S120 HTTP 400.**

## 3. ⛔ TWO SPELLINGS — no single config value can work

| Module | Token |
|---|---|
| `support-tickets/crm/app_patched.py` | `api-admin.php` |
| `autonomous-agents/crm/failure_routes.py` | `admin-api.php` |
| `autonomous-agents/crm/update_routes.py` | `admin-api.php` |
| `autonomous-agents/crm/fleet_versions_routes.py` | `admin-api.php` |
| `diagnostic-console/crm/ticket_diagnose_routes.py` | `admin-api.php` |

**Whatever `proxy_url` is set to, one group no-ops.** Restoring the old value fixes half the call sites
and leaves the rest silently wrong. This would have broken eventually regardless of S58.

## 4. PREREQUISITE — the only remaining unknown

**Read `proxy_url` from the VM's `/home/d3kos-admin/config/config.json`.**

⚠ **The CRM VM `192.168.236.5` was UNREACHABLE from the lab on 2026-08-28 — ping 100% packet loss.**
The S58 value comes from `DEPLOYMENT_INDEX.md`, which is a record, not a live read.
**Confirm before implementing.** §3 does not depend on it.

## 5. FIX — change the pattern, not the value

1. Set `proxy_url` to a **base directory** URL: `https://atmyboat.com/wp-content/themes/twentytwenty-child/mobile/`
2. Every module **appends** its filename. **Delete every `.replace()` call.**
3. Unify the two spellings **in the same change**, or the bug returns.
4. Add a startup assertion: if any derived URL still contains `admin-api` or `api-admin`, **raise and
   refuse to start.** ⚠ A guard that only logs is what allowed this to persist from S58 to now.

The nine targets, all present in production: `admin-api-tickets.php`, `diagnostic-bundle.php`,
`diagnostic-fix.php`, `diagnostic-resolve.php`, `diagnostic-past-cases.php`, `config-backup-status.php`,
`issue-api.php`, `update-publish.php`, `version-api.php`.

⚠ **The repo's `crm-proxy.php` is 32 lines / 2 actions; production's is 411 lines / 12 actions
(BUG-88). Do not audit this file from the repo copy.**

## 6. TESTS

| # | Test | Pass condition |
|---|---|---|
| T1 | Each of the nine derived URLs | resolves to its own filename, not `crm-proxy.php` |
| T2 | CRM ticket list | returns tickets, not `Unknown action` |
| T3 | CRM diagnostics | same |
| **T4** | **Negative: set `proxy_url` to a value containing neither token, start the CRM** | **startup refuses** — proves §5.4 bites. ⛔ Without this the assertion is decoration |
| T5 | `grep -rn "\.replace(\"a" crm/` across all 5 modules | 0 hits |
| T6 | `crm-proxy.php`'s own 12 actions still work | no regression |

## 7. DEFINITION OF DONE

- [ ] `proxy_url` read from the live VM and recorded
- [ ] Base-directory pattern adopted; every `.replace()` deleted across all 5 modules
- [ ] Both spellings eliminated
- [ ] Startup assertion added and **T4 demonstrated**
- [ ] T1–T6 pass
- [ ] ⛔ `api-admin.php` was NOT created
