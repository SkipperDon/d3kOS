# d3kOS Admin CRM Tool — Specification
**Version target:** v0.9.9.1 (post security audit, pre public launch)
**Document version:** 1.0 — 2026-04-01
**Owner:** Donald Moskaluk — AtMyBoat.com

---

## 1. Purpose

A private, locally-hosted admin tool giving Don a complete picture of every
customer — their account, their Pi health, their billing, and their support
emails — in one place, without touching the WordPress site.

If WordPress is ever compromised, this tool is completely unaffected.
It connects directly to the HostPapa MySQL database and to the email mailbox.
It never runs on the internet.

---

## 2. What It Is Not

- Not a public-facing page
- Not part of WordPress
- Not a replacement for the existing staging admin-tools.php page
  (that page handles quick staging-time testing — this tool handles production support)
- Not a full helpdesk ticketing system (day one — may evolve)

---

## 3. Runtime Environment

| Item | Decision |
|------|----------|
| Host machine | Workstation (primary) or laptop (secondary) |
| VM software | VirtualBox (free) |
| OS | Ubuntu 22.04 LTS Desktop |
| VM resources | 4GB RAM, 2 CPU cores, 40GB storage |
| App framework | Python 3.11 + Flask |
| Access | Windows browser → `http://[VM IP]:5000` |
| AI | Gemini Flash free tier (already configured in d3kOS) |
| Remote access | WireGuard VPN — Phase 2 addition |
| Migration path | Same Ubuntu + same app folder → cloud VM when needed |

---

## 4. Connections

| System | Protocol | Notes |
|--------|----------|-------|
| HostPapa MySQL | TCP/SSL port 3306 | cPanel → Remote MySQL → whitelist VM IP |
| skipperdon@atmyboat.com | IMAP (read) + SMTP (send) | HostPapa email credentials |
| Pi (192.168.1.237) | SSH | Existing `~/.ssh/id_d3kos` key (copied to VM) |
| Gemini API | HTTPS | Existing API key from d3kOS config |
| WordPress | None — direct DB only | No WP API calls |

---

## 5. Authentication

Single-user tool. One local password stored in `config.json` as a bcrypt hash.
Flask session with 8-hour timeout. HTTPS enforced when accessed remotely (Phase 2).
No WordPress credentials used — completely independent auth.

---

## 6. Configuration File

`/home/d3kos-admin/config/config.json` on the VM.
Never committed to any repo. Contains:

```json
{
  "admin_password_hash": "bcrypt hash",
  "db": {
    "host": "mysql.hostpapa.com",
    "port": 3306,
    "user": "db_user",
    "password": "db_password",
    "database": "db_name",
    "ssl": true
  },
  "email": {
    "imap_host": "mail.hostpapa.com",
    "imap_port": 993,
    "smtp_host": "mail.hostpapa.com",
    "smtp_port": 587,
    "address": "skipperdon@atmyboat.com",
    "password": "email_password"
  },
  "gemini_api_key": "key",
  "pi_ssh": {
    "host": "192.168.1.237",
    "user": "d3kos",
    "key_path": "/home/d3kos-admin/.ssh/id_d3kos"
  },
  "wp_db_prefix": "wpax_"
}
```

---

## 7. Features — Phased

### Phase 1 — Foundation (build first)
Core app skeleton. No features — just the frame that everything else plugs into.
- VirtualBox + Ubuntu setup instructions (written, not automated)
- Flask app with login page + session management
- Config file loader
- Database connection pool (pymysql)
- Navigation sidebar (links to all sections — most show "coming soon" until built)
- Base HTML template with AtMyBoat branding

### Phase 2 — Customer View
The most-used feature. Find a customer, see everything about them.
- **Customer list** — paginated table: email, name, tier, joined date, last Pi seen
- **Search** — by email address, display name, or vessel name
- **Customer profile page:**
  - Account: tier, FMP used/remaining, join date, WP user ID
  - Paired Pis: vessel name, device token, last seen, d3kOS version, online status
  - Billing history: last 5 transactions from amboat_billing
  - Fix My Pi history: last 5 FMP commands + results

### Phase 3 — Pi Diagnostics
Read-only view of a customer's Pi state.
- **Service health** — SSH to Pi, run `systemctl is-active` for 10 critical services
  (same list as watchdog: cloud-agent, tier, export-manager, etc.)
- **Recent alerts** — last 20 rows from amboat_alerts for this user + pi_id
- **Recent commands** — last 10 rows from amboat_command_queue (command, status, result)
- **Engine snapshots** — last 24h from amboat_engine_snapshots (RPM, temp, voltage)
- **Boatlog** — last 10 entries
- Refresh button — re-runs SSH + DB queries on demand

### Phase 4 — Email Inbox
Support emails linked to customer accounts.
- **Inbox view** — all emails in `skipperdon@atmyboat.com` INBOX via IMAP
- **Account linking** — match sender email to wpax_users.user_email automatically
  Unmatched emails shown as "Unknown sender" with manual link option
- **Thread view** — full email thread, oldest first
- **Reply form** — compose reply, send via SMTP, thread stays in view
- **Customer context panel** — when viewing an email from a known customer,
  shows their tier + Pi status alongside the email (the "complete picture")
- **Mark handled** — local flag (stored in SQLite on VM) — not synced to mailbox

### Phase 5 — AI Draft Assist
One-click AI reply draft using Gemini Flash.
- Draft button appears in email thread view
- Sends to Gemini:
  - The customer's email text
  - Their tier + FMP remaining
  - Their active alerts (if any)
  - Their Pi last-seen time + d3kOS version
  - Last command result (if relevant)
- Gemini drafts a specific, accurate reply
- Draft appears in reply box — Don edits and sends, or discards
- System prompt: helpful, professional, one-person operation tone

### Phase 6 — Tier Management + Audit Log
Safe tier changes with full accountability.
- **Tier change form:** dropdown (T0/T1/T2/T3) + mandatory reason field (min 10 chars)
- **Confirmation step:** shows old tier → new tier + reason, requires checkbox confirm
- **amboat_admin_log table** (HostPapa MySQL):
  ```sql
  CREATE TABLE amboat_admin_log (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    admin_user    VARCHAR(100) NOT NULL,
    target_user_id INT NOT NULL,
    action        VARCHAR(50) NOT NULL,
    old_value     VARCHAR(255),
    new_value     VARCHAR(255),
    reason        TEXT NOT NULL,
    ip_address    VARCHAR(45),
    created_at    DATETIME NOT NULL
  );
  ```
- Every tier change, FMP reset, and alert clear writes one row
- **Audit log view** — filterable by date, action type, target user

### Phase 7 — Database Explorer
Direct DB access for investigation and support.
- Table selector — dropdown of all amboat_* and wpax_users tables
- Row browser — paginated, filterable by any column
- Export to CSV
- SELECT only — no UPDATE/DELETE/INSERT exposed in UI
- Raw query box (SELECT only — blocked at query parser level)

### Phase 8 — In-App Support Button (PWA)
Customer-side feature that feeds Phase 4.
- "Contact Support" button in PWA Settings screen
- Opens a simple form: message text (max 500 chars)
- On submit: sends email to `skipperdon@atmyboat.com` with structured subject line:
  ```
  [d3kOS Support] {vessel_name} — T{tier} — {short message}
  ```
  Body auto-includes: vessel name, tier, Pi last seen, active alert count,
  d3kOS version, FMP remaining. Customer only types their message.
- When this email arrives in Phase 4 inbox, it links automatically to their account

---

## 8. Database Tables Used (read)

| Table | Used for |
|-------|----------|
| wpax_users | Customer email, display name, registered date |
| wpax_usermeta | Tier (atmyboat_tier), FMP used (atmyboat_fmp_used_month) |
| d3kos_pairings | Paired Pis, vessel name, last_seen_at |
| amboat_alerts | Customer alerts |
| amboat_command_queue | Command history |
| amboat_engine_snapshots | Engine data |
| amboat_boatlog | Boatlog entries |
| amboat_billing | Billing transactions |
| amboat_pdf_reports | PDF report history |

## Database Tables Used (write)

| Table | Used for |
|-------|----------|
| wpax_usermeta | Tier change, FMP reset |
| amboat_alerts | Clear alerts |
| amboat_admin_log | Audit trail (NEW — must create before Phase 6) |

---

## 9. Security Model

| Concern | Mitigation |
|---------|-----------|
| Internet exposure | None — localhost only until VPN added |
| WordPress compromise | Zero impact — completely separate app + credentials |
| DB credentials | Separate MySQL user with only required permissions |
| Login brute force | 5 attempts → 15-minute lockout |
| Session hijack | 8-hour timeout, secure cookie flags |
| SQL injection | Parameterised queries only — no string concatenation |
| Destructive DB | UI exposes SELECT only in explorer; writes are specific endpoints |
| Audit trail | Every write action logged to amboat_admin_log |

---

## 10. Build Order

Build phases in order. Each phase is independently usable before the next begins.

| Phase | Name | Depends on |
|-------|------|-----------|
| 1 | Foundation | Nothing |
| 2 | Customer View | Phase 1 |
| 3 | Pi Diagnostics | Phase 2 |
| 4 | Email Inbox | Phase 2 |
| 5 | AI Draft Assist | Phase 4 |
| 6 | Tier Management + Audit Log | Phase 2 |
| 7 | Database Explorer | Phase 1 |
| 8 | In-App Support Button (PWA) | Phase 4 |

Phase 1 → Phase 2 → Phase 6 is the minimum viable tool.
Phase 4 + Phase 5 is the email + AI piece.
Phase 3 + Phase 8 complete the "complete picture."

---

## 11. Not In Scope (v0.9.9.1)

- Ticket numbering system
- SLA tracking
- Multiple admin users
- Remote access / VPN (add in v0.9.9.2)
- Automated email triage
- Customer-facing portal
- Stripe dashboard integration (investigate for v1.1)

---

## 12. Migration to Cloud

When workstation can no longer handle the VM:
1. Export VM from VirtualBox as `.ova` file
2. Spin up Ubuntu 22.04 on cloud provider (Hetzner CAX11 ~$4/month recommended)
3. Import or re-setup: `git clone` + `pip install -r requirements.txt`
4. Update `config.json` with cloud server's IP
5. Add cloud IP to HostPapa Remote MySQL whitelist
6. Add WireGuard VPN for remote access
7. Zero code changes required

---

*Spec version 1.0 — ready for BUILD_CHECKLIST.md task breakdown*
