# Entity: Tier System (T0–T3)

*Last updated: S62 2026-04-17 | Sources: MEMORY.md, S61 fix*

---

## Definitions

| Tier | Name | Key Features |
|------|------|-------------|
| T0 | Free | No Pi pairing, no cloud backup |
| T1 | Basic | Pi paired, cloud backup, Fix My Pi |
| T2 | Pro | Fix My Pi, PDF reports, T2 FMP counter reset monthly |
| T3 | Admiral | Unlimited vessels, all features |

## Storage Format (CRITICAL — BUG-04 history)

Tier is stored as string `"T0"` through `"T3"` in:
- `wpax_usermeta` (WordPress DB)
- `license.json` on Pi (`/opt/d3kos/config/license.json`)

**BUG-04 (FIXED S61 2026-04-16):** `crm-proxy.php update_tier` was storing bare integers `"0"`–`"3"` due to `int(new_tier)` cast in Flask + dropdown values `0`–`3`. Fix: dropdown values → `"T0"`–`"T3"`, Flask validates against set, `int()` cast removed, 4 staging DB rows patched. Integer values now rejected with 400.

## Enforcement Points

- `crm-proxy.php` — CRM tier update endpoint (renamed from admin-api.php)
- `tiers.html` — CRM dropdown, values must be `"T0"`–`"T3"` strings
- `app_patched.py` — validates `new_tier not in {'T0','T1','T2','T3'}`
- `license.json` — Pi reads this to determine feature access
- `cloud_agent.py` `handle_tier_change` — normalises to string tier before writing license.json

## CRM Auth Pattern

CRM-facing PHP files (crm-proxy.php, issue-api.php, admin-api-tickets.php) use `ADMIN_API_KEY` hardcoded inline — NOT `AMBOAT_API_KEY` from config.php. config.php `AMBOAT_API_KEY` is for Pi-facing endpoints only.

## Open Issues

- [[questions/bug-06-pwa-tier-display]] — PWA still shows T1 after BUG-04 fix

## Related

- [[entities/atmyboat-website]]
- [[entities/pwa]]
