# AtMyBoat.com — Credential Rotation Checklist
**Run this checklist before Phase 4 live push. Every item must be checked before going live.**

---

## Why This Exists
All credentials used during development (staging keys, test keys, dev passwords) must be
replaced with fresh production values before the live site goes public. Development keys
have been exposed to staging logs, cPanel sessions, and possibly browser history.

---

## Checklist

### Stripe
- [ ] Generate new **Stripe live secret key** (`sk_live_...`) in Stripe Dashboard → Developers → API keys
- [ ] Generate new **Stripe webhook secret** for Fix My Pi webhook (`whsec_...`) — Stripe Dashboard → Webhooks → fix-my-pi-billing.php endpoint → reveal signing secret
- [ ] Generate new **Stripe webhook secret** for subscription webhook (`whsec_...`) — same location, subscription endpoint
- [ ] Confirm **Stripe price IDs** are live-mode prices (not test-mode) — Products → each price → copy ID
- [ ] Update all five Stripe constants in `inc/atmyboat-config.php` on the **live** server

### Gemini API
- [ ] Confirm website is using the **new Google Cloud project** key (not the Pi's shared key)
- [ ] Rotate the website Gemini API key — Google AI Studio → API keys → delete old → create new
- [ ] Update `GEMINI_API_KEY` in `inc/atmyboat-config.php` on the **live** server

### AMBOAT_API_KEY
- [ ] Generate a new `AMBOAT_API_KEY` — use: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`
- [ ] Update `AMBOAT_API_KEY` in `mobile/config.php` on the **live** server
- [ ] Update `AMBOAT_API_KEY` in `/opt/d3kos/config/cloud-config.json` on the Pi

### FTP / HostPapa
- [ ] Change FTP password for `d3kos@atmyboat.com` in cPanel → FTP Accounts
- [ ] Update `.env` locally with new FTP password

### WordPress Admin
- [ ] Change WordPress admin password on the **live** site after Phase 4 push
- [ ] Confirm no default `admin` username exists — rename if present

### Database
- [ ] Confirm `mobile/config.php` on live server uses the **live** database credentials (not staging DB)
- [ ] Confirm `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` match cPanel → MySQL Databases

### Metered TURN (v0.9.4)
- [ ] Rotate Metered.ca API key and TURN credential before PWA goes to production users
- [ ] Update `turn-credentials.php` on live server

---

## Post-Rotation Smoke Test
After rotating all credentials, verify these flows still work on the live site:
- [ ] AI widget on /help responds to a boating question
- [ ] Stripe checkout loads on /fix-my-pi (test with a Stripe test card first, then disable test mode)
- [ ] Pi exports data successfully (check `amboat_engine_snapshots` in phpMyAdmin for new rows)
- [ ] PWA logs in and pairs a Pi

---

## Notes
- Never rotate credentials mid-session — do all rotations in one sitting so nothing is left half-updated
- Update Don's credential document with all new production values immediately after rotation
- CA4: Don's credential document must be updated before this checklist is marked complete
