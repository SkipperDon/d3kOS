# Entity: PWA (Progressive Web App)

*Last updated: S62 2026-04-17 | Sources: MEMORY.md, project_v094_php.md*

---

## Identity

- **URL:** `atmyboat.com/staging/app/`
- **Hosted:** HostPapa (NOT on the Pi)
- **Type:** PWA — no App Store, no Apple/Google terms
- **Cache version:** v7 (update when deploying breaking PWA changes)

## Pi Identity Rule (CRITICAL)

Pi identity for ALL HostPapa services = **`device_token`** UUID from `device-token.json`  
NEVER use `installation_id` hex from `license.json` — wrong identifier entirely.

`app_token` stored in `wpax_usermeta` with key **`atmyboat_app_token`** (NOT `app_token`) — confirmed by user-login.php.

## Connectivity Architecture

- **Live Pi ↔ phone connection:** WebRTC/STUN P2P — not polling, not message broker
- **STUN servers:** Google/Cloudflare public (free, no account required)
- **TURN server:** deferred — add only if real user testing proves necessary
- **Pi never accepts inbound connections** — Pi always initiates outbound
- **No open inbound ports on Pi — ever**
- Option C (self-hosted UDP hole punching) is v1.1 — NOT in v0.9.4

## PDF Systems (TWO — never confuse them)

| System | PHP endpoint | Storage | Key | Read by |
|--------|-------------|---------|-----|---------|
| Server-side Gemini report | `mobile/pdf-report.php` | `wpax_usermeta` key `atmyboat_pdf_reports` as `[{date,type,url}]` | user_id | Chart Room |
| Client-side jsPDF | `mobile/pdf-store.php` | `amboat_pdf_reports` DB table keyed by device_token | device_token | PWA library |

S36 wrongly "fixed" Chart Room to read DB table — reverted.

## Mobile PHP Endpoints

- Located at `mobile/` in child theme
- Use `config.php` + direct mysqli (NOT wp-load.php) — except `support-request.php`
- `wp-load.php` path from `mobile/` = `__DIR__ . '/../../../../wp-load.php'` (4 levels up)

## HostPapa PHP Probe Pattern

`amboat_get_db()` is NOT in config.php — it's in the auth.php stack.  
Temp DB probes must use raw `new mysqli('127.0.0.1', 'atmyb197_wp302', ...)` directly.  
Delete probe immediately after use.

## Tier Display

- BUG-06 (OPEN): PWA still shows T1 after BUG-04 fix — blocked pending operator confirmation
- See [[questions/bug-06-pwa-tier-display]]

## Payments

- Stripe on `atmyboat.com` only — never in-app
- Stripe keys ARE configured on HostPapa staging — do not ask Don to set up again

## Security (v0.9.9 audit complete)

- SA1: all DB creds + ADMIN_API_KEY centralised in config.php
- SA2: zero `real_escape_string()` — all SQL uses `prepare()+bind_param()`
- SA3: all API key comparisons use `hash_equals()` (timing-safe)
- SA6: data-export.php (GDPR Art.15) + data-delete.php (GDPR Art.17) deployed

## Related

- [[entities/atmyboat-website]] — hosting platform
- [[entities/tier-system]] — tier enforcement in PWA
- [[entities/d3kos-platform]] — Pi that PWA connects to
