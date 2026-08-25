# Entity: AtMyBoat.com Website

*Last updated: S134-cont 2026-08-25 | Sources: MEMORY.md, atmyboat_v093.md*

---

## Identity

- **URL:** https://atmyboat.com
- **Status:** LIVE — Phase 4 complete 2026-04-12
- **Platform:** WordPress + Twenty Twenty child theme
- **Hosting:** HostPapa shared hosting
- **GitHub:** github.com/SkipperDon/atmyboat-forum
- **AI model (server-side):** `claude-haiku-4-5-20251001` ONLY — hard cap $30/month

## Architecture Rules (non-negotiable)

- All custom code in child theme: `/wp-content/themes/twentytwenty-child/`
- AI is PHP + cURL only — no Node.js, no npm, no Composer
- All API keys via `define()` in `atmyboat-config.php` — NEVER hardcode, NEVER commit
- No subdomains — all content at `atmyboat.com/subfolder`
- Never modify files outside `/forum`, `/products`, `/blog`, or child theme

## Deploy Rules

- FTP landing IS the web root — no `public_html` subdirectory exists as a separate FTP target. Paths start directly from login: `wp-content/themes/twentytwenty-child/...`, NOT `public_html/wp-content/...` (S134-cont: `public_html/` prefix caused 553 errors)
- FTP deploy via Python ftplib only — bash breaks `!` in password
- Don clicks "Push to Live" in cPanel — never Claude
- UpdraftPlus backup required before any live push
- NEVER push to live without verified UpdraftPlus backup

## Database

- DB prefix: `wpax_`
- DB user: `atmyb197_wp59874` (production). `atmyb197_wp302` is BROKEN as of S134 — do not use.
- MySQL: `localhost` (socket) — works. S17c rule "always use 127.0.0.1" is STALE and confirmed wrong for production (S134-cont).
- PHP on HostPapa has mysqli strict exceptions — always call `mysqli_report(MYSQLI_REPORT_OFF)` after connect

## Auth System (S56/S57)

- `page-register.php` / `page-login.php` / `page-my-account.php` + `inc/auth.php`
- `atmyboat_email_verified` usermeta gates login (`0`=blocked, `1`=allowed, empty=allowed for legacy)
- `authenticate` filter priority 30 — runs after WP credential check (priority 20)
- `wp_set_password()` clears auth cookies — must call `wp_set_auth_cookie($user_id, true)` after
- Always use PRG (redirect after POST) on forms that call wp_set_password()

## ImunifyAV Pattern (S58)

Credentials + SQL + php://input in one file triggers 403. Fix: split to `*-config.php` + `require`. `admin-api.php` renamed to `crm-proxy.php`.

## Mobile Endpoints

- Located at `mobile/` in child theme
- Use `config.php` + direct mysqli (NOT wp-load.php) except `support-request.php`
- `app_token` stored in usermeta key `atmyboat_app_token` (NOT `app_token`)
- Pi identity = `device_token` UUID from device-token.json — NEVER `installation_id`

## AODA Requirements

- Minimum 18px body text, 1.8 line-height
- Minimum 48×48px touch targets
- Skip-to-content link on every page
- WCAG 2.0 AA 4.5:1 contrast minimum
- Fonts: Fraunces (headings) + Nunito (body) + JetBrains Mono (code)

## Stripe Webhooks (S74 2026-05-04 — FIXED)

Both Stripe webhook endpoints were pointing to `/staging/` since Phase 4 launch (2026-04-12). Production webhook calls were going to staging handlers.

**Fix S74:** Updated both endpoints in Stripe Dashboard to production URLs. New signing secrets written to live `inc/atmyboat-config.php` via FTPS.

| Constant | Purpose |
|----------|---------|
| `STRIPE_WEBHOOK_SECRET` | Fix My Pi webhook |
| `STRIPE_WEBHOOK_SECRET_SUB` | Subscription webhook |

Credentials in CREDENTIAL_VAULT.md Live Mode section.

## Registration (device-gated — S134-cont 2026-08-25)

- `/register/` now requires a 10-char Crockford Base32 code from an operator-approved d3kOS device
- Code is SHA-256 hashed, atomically claimed (SELECT FOR UPDATE), consumed once — prevents replay
- `wp_create_user()` only runs after code is claimed — closes the BUG-63 wp_create_user direct-call vulnerability
- Form fields: alias (display name, public), legal name (private user_meta), email, password, code_input
- Page: WordPress ID=339, slug='register', `wpax_posts` table
- PHP files: `page-register.php` + `device-registration.php` in child theme
- `device-registration.php` has `if (!defined('ABSPATH')) { exit; }` — WordPress context only
- Bot detection note: `unticking "Anyone can register"` has ZERO effect — the template calls `wp_create_user()` directly

## Related

- [[entities/tier-system]] — subscription tiers
- [[entities/pwa]] — mobile PWA hosted here
- [[entities/admin-console-vm]] — CRM admin interface manages site data
- [[concepts/php-proxy-pattern]]
