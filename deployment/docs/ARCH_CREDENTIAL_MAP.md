# AD5 — Architecture: Credential Map
**Version:** v1.0.0
**Date:** 2026-04-02
**Project:** AtMyBoat.com / d3kOS

---

## Summary

This document maps every credential used across the AtMyBoat.com / d3kOS platform. It describes what each credential is, which service owns it, which services consume it, and where it is stored. No actual credential values appear in this document — it is a map only. This document is the authoritative reference for diagnosing auth failures and planning credential rotation.

---

## Credential Definitions

---

### 1. AMBOAT_API_KEY

| Field | Value |
|---|---|
| **What it is** | Shared secret authenticating Pi-to-HostPapa API calls |
| **Owner** | HostPapa (defined in mobile/config.php) |
| **Consumers** | Pi export_worker.py, cloud_agent.py, live_session.py |
| **Auth method** | HTTP header on every Pi→HostPapa POST/GET |
| **Rotation impact** | Must update Pi cloud-config.json AND HostPapa config.php simultaneously |

**Storage locations:**

```
Pi:         /opt/d3kos/config/cloud-config.json
                key: "amboat_api_key"

HostPapa:   /wp-content/themes/twentytwenty-child/mobile/config.php
                define('AMBOAT_API_KEY', '...');
```

---

### 2. GEMINI_API_KEY (Website)

| Field | Value |
|---|---|
| **What it is** | Google Gemini API key for the website AI assistant widget |
| **Owner** | Google Cloud project gen-lang-client-0459941519 |
| **Consumers** | HostPapa ai-assistant.php |
| **Auth method** | HTTP header in PHP cURL call to Gemini REST API |
| **Quota** | Shared 1500 req/day with Pi Gemini key — same Google Cloud project |

**Storage locations:**

```
HostPapa:   /wp-content/themes/twentytwenty-child/inc/atmyboat-config.php
                define('GEMINI_API_KEY', '...');

Identifier: key suffix ...MhR0 (for quota debugging — not a secret)
```

---

### 3. GEMINI_API_KEY (Pi)

| Field | Value |
|---|---|
| **What it is** | Google Gemini API key for Pi voice assistant and Helm AI |
| **Owner** | Google Cloud project gen-lang-client-0459941519 |
| **Consumers** | Pi gemini_proxy.py, voice assistant service |
| **Auth method** | HTTP header in Python requests to Gemini REST API |
| **Quota** | Shared 1500 req/day with Website Gemini key — same Google Cloud project |

**Storage locations:**

```
Pi:         /opt/d3kos/services/gemini-nav/config/gemini.env
                GEMINI_API_KEY=...

Identifier: key suffix ...iGIA (for quota debugging — not a secret)
```

---

### 4. STRIPE_SECRET_KEY

| Field | Value |
|---|---|
| **What it is** | Stripe server-side secret key for creating charges and checkout sessions |
| **Owner** | Stripe account (Don's AtMyBoat.com account) |
| **Consumers** | HostPapa stripe-webhook.php, fix-my-pi-billing.php, checkout session creation |
| **Auth method** | Stripe PHP SDK initialisation — passed to \Stripe\Stripe::setApiKey() |
| **Rotation impact** | Update HostPapa atmyboat-config.php only. Pi does not use Stripe directly. |

**Storage locations:**

```
HostPapa:   /wp-content/themes/twentytwenty-child/inc/atmyboat-config.php
                define('STRIPE_SECRET_KEY', 'sk_live_...');

NEVER in:   Any PHP template, JS file, or committed config
```

---

### 5. STRIPE_WEBHOOK_SECRET (Subscription)

| Field | Value |
|---|---|
| **What it is** | Stripe webhook signing secret for subscription events |
| **Owner** | Stripe (generated when webhook endpoint is registered) |
| **Consumers** | HostPapa inc/stripe-webhook.php |
| **Auth method** | \Stripe\Webhook::constructEvent() signature validation |
| **Rotation impact** | Update HostPapa atmyboat-config.php, re-register webhook endpoint in Stripe dashboard |

**Storage locations:**

```
HostPapa:   /wp-content/themes/twentytwenty-child/inc/atmyboat-config.php
                define('STRIPE_WEBHOOK_SECRET', 'whsec_...');
```

---

### 6. STRIPE_WEBHOOK_SECRET (Fix My Pi)

| Field | Value |
|---|---|
| **What it is** | Stripe webhook signing secret for Fix My Pi charge events |
| **Owner** | Stripe (separate webhook endpoint for FMP) |
| **Consumers** | HostPapa fix-my-pi-billing.php |
| **Auth method** | \Stripe\Webhook::constructEvent() signature validation |
| **Rotation impact** | Update HostPapa atmyboat-config.php, re-register FMP webhook endpoint in Stripe dashboard |

**Storage locations:**

```
HostPapa:   /wp-content/themes/twentytwenty-child/inc/atmyboat-config.php
                define('STRIPE_WEBHOOK_SECRET_FMP', 'whsec_...');
```

---

### 7. STRIPE_PRICE_IDs (×3)

| ID | Product | Amount |
|---|---|---|
| FMP price_id | Fix My Pi (one-time) | $29.99 |
| T2 price_id | T2 Monthly subscription | $9.99/month |
| T3 price_id | T3 Annual subscription | $99.99/year |

**Storage locations:**

```
HostPapa:   /wp-content/themes/twentytwenty-child/inc/atmyboat-config.php
                define('STRIPE_PRICE_FMP',  'price_...');
                define('STRIPE_PRICE_T2',   'price_...');
                define('STRIPE_PRICE_T3',   'price_...');
```

Price IDs are not secret (they appear in checkout sessions) but are managed as config values, not hardcoded.

---

### 8. app_token

| Field | Value |
|---|---|
| **What it is** | Session identity token for the PWA — issued on WordPress login |
| **Owner** | WordPress (generated by AtMyBoat child theme on login) |
| **Consumers** | PWA app.js (all API calls), HostPapa: dashboard-data.php, app-command.php, pdf-store.php, pdf-analyze.php, list-reports.php, fix-my-pi-app.php, turn-credentials.php, rtc-signal.php, pair-device.php |
| **Auth method** | HTTP header on every PWA→HostPapa request |
| **Rotation** | Regenerated on each WordPress login. Old tokens expire. |

**Storage locations:**

```
WordPress:  wp_usermeta
                meta_key = 'atmyboat_app_token'
                (per-user, overwritten on each login)

PWA:        localStorage
                key: 'amboat_app_token'
                (set after login redirect, persists until logout)
```

---

### 9. device_token

| Field | Value |
|---|---|
| **What it is** | Permanent UUID identity for a specific Pi installation |
| **Owner** | Pi (generated on first setup, never changes) |
| **Consumers** | Pi: all HostPapa calls (sent with AMBOAT_API_KEY), HostPapa: data-ingress.php, command-queue.php, app-command.php, register-device.php, pair-device.php |
| **Auth method** | Sent alongside AMBOAT_API_KEY in every Pi→HostPapa request body |
| **Critical rule** | Always use device_token UUID. NEVER use installation_id hex from license.json for HostPapa calls. |

**Storage locations:**

```
Pi:         /opt/d3kos/config/device-token.json
                { "device_token": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" }

WordPress:  wp_usermeta
                meta_key = 'atmyboat_device_token'
                (written by register-device.php on first registration)
```

---

### 10. TURN Credentials

| Field | Value |
|---|---|
| **What it is** | Per-session WebRTC TURN server access credentials from Metered.ca |
| **Owner** | Metered.ca (generated via their API) |
| **Consumers** | PWA RTCPeerConnection ICE server config |
| **Auth method** | username/credential fields in RTCIceServer object |
| **Persistence** | NOT stored. Generated fresh per WebRTC session. Short TTL. |

**Storage locations:**

```
HostPapa:   turn-credentials.php holds the Metered.ca API key
                (fetches and proxies per-session credentials to PWA)

PWA:        In-memory only — RTCPeerConnection config object
                Never written to localStorage or any persistent store
```

---

### 11. WordPress Admin Credentials

| Field | Value |
|---|---|
| **What it is** | WordPress admin username + password, and cPanel login |
| **Owner** | Don (HostPapa account) |
| **Consumers** | Don only — WP Admin dashboard, cPanel |
| **Storage** | Don's personal credential document (offline) |
| **Claude rule** | Claude never handles, requests, or stores these credentials |

---

### 12. FTP Credentials (d3kos@atmyboat.com)

| Field | Value |
|---|---|
| **What it is** | HostPapa FTP account for deploying theme files via lftp |
| **Owner** | HostPapa account (Don) |
| **Consumers** | Deployment scripts in Helm-OS project |
| **Auth method** | lftp ftps:// connection |

**Storage locations:**

```
Workstation: /home/boatiq/Helm-OS/.env
                 FTP_USER=d3kos@atmyboat.com
                 FTP_PASS=...
                 FTP_HOST=...

.gitignore:  .env is gitignored — NEVER committed
```

---

### 13. SSH Key (id_d3kos)

| Field | Value |
|---|---|
| **What it is** | SSH keypair for workstation → Raspberry Pi access |
| **Owner** | Don's workstation |
| **Consumers** | SSH sessions from workstation to Pi |
| **Auth method** | SSH public key authentication |

**Storage locations:**

```
Workstation (private key): ~/.ssh/id_d3kos
Workstation (public key):  ~/.ssh/id_d3kos.pub
Pi (authorized):           ~/.ssh/authorized_keys
```

---

## Storage Location Summary Table

| Credential | Pi | HostPapa | PWA | Workstation | WordPress DB |
|---|---|---|---|---|---|
| AMBOAT_API_KEY | /opt/d3kos/config/cloud-config.json | mobile/config.php | — | — | — |
| GEMINI_API_KEY (website) | — | inc/atmyboat-config.php | — | — | — |
| GEMINI_API_KEY (Pi) | services/gemini-nav/config/gemini.env | — | — | — | — |
| STRIPE_SECRET_KEY | — | inc/atmyboat-config.php | — | — | — |
| STRIPE_WEBHOOK_SECRET ×2 | — | inc/atmyboat-config.php | — | — | — |
| STRIPE_PRICE_IDs ×3 | — | inc/atmyboat-config.php | — | — | — |
| app_token | — | — | localStorage | — | wp_usermeta |
| device_token | config/device-token.json | — | — | — | wp_usermeta |
| TURN credentials | — | turn-credentials.php (Metered.ca key) | in-memory only | — | — |
| WordPress admin | — | — | — | Don's credential doc | — |
| FTP credentials | — | — | — | Helm-OS/.env (gitignored) | — |
| SSH key (id_d3kos) | authorized_keys | — | — | ~/.ssh/id_d3kos | — |

---

## Notes

- `atmyboat-config.php` is the single most sensitive file in the project. It holds Stripe keys, Gemini key, webhook secrets, and price IDs. It is never committed to git and must not appear in any deployment script output or log. Confirm it is in `.gitignore` before every staging deploy.
- The two Gemini API keys (website + Pi) are on the same Google Cloud project and share a single 1500 req/day quota. Hitting quota on the Pi affects the website AI widget and vice versa. Do not create additional Google Cloud projects for Gemini without billing configured — new projects default to limit: 0.
- `device_token` and `installation_id` are different identifiers. `device_token` is the UUID from `device-token.json` and is the correct identity for all HostPapa calls. `installation_id` is a hex value in `license.json` used for local tier enforcement only. Mixing them up is a confirmed critical bug (see MEMORY.md).
- TURN credentials from Metered.ca are never stored persistently. Each WebRTC session fetches fresh credentials via turn-credentials.php. The Metered.ca API key itself lives only in turn-credentials.php on HostPapa.
- Claude never requests, generates, stores, or logs real credential values. Placeholders only in all documentation and examples.
