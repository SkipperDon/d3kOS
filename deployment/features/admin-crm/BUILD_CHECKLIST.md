# Admin CRM Tool — Build Checklist
**Version target:** v0.9.9.1
**Spec:** `SPEC.md` (read before each phase)
**Status:** PLANNED — not started

---

## Phase 1 — Foundation

- [ ] **1.1 VM setup doc** — Write step-by-step VirtualBox + Ubuntu 22.04 install
      instructions for Don (Windows GUI steps, no terminal). Save as `VM_SETUP.md`.
- [ ] **1.2 Flask skeleton** — `app.py` + `templates/base.html` + `static/`
      Navigation sidebar with 7 section links. AtMyBoat branding. Placeholder pages.
- [ ] **1.3 Login page** — `templates/login.html`. Single user, bcrypt password hash.
      Flask session, 8-hour timeout. 5-attempt lockout → 15-min freeze.
- [ ] **1.4 Config loader** — `config.py` reads `config/config.json`.
      Validates all required keys on startup. Fails loudly if missing.
- [ ] **1.5 DB connection** — `db.py`. pymysql connection pool, SSL enabled.
      Test query on startup: `SELECT 1` — confirm HostPapa DB reachable.
- [ ] **1.6 Requirements + run script** — `requirements.txt`. `start.sh` that
      activates venv and starts Flask. Don double-clicks it from Ubuntu Desktop.
- [ ] **1.7 Config template** — `config/config.template.json` with all keys
      and placeholder values. Instructions for Don to fill in real values.

---

## Phase 2 — Customer View

- [ ] **2.1 Customer list page** — `/customers`. Paginated table (25/page).
      Columns: email, display name, tier badge, join date, last Pi seen.
      Pulls from `wpax_users` JOIN `wpax_usermeta` JOIN `d3kos_pairings`.
- [ ] **2.2 Search** — Live filter on email, name, vessel name. No page reload.
      Search runs parameterised query — no LIKE on unindexed columns without limit.
- [ ] **2.3 Customer profile page** — `/customer/<user_id>`.
      Sections: Account summary, Paired Pis, Billing history (last 5), FMP history.
- [ ] **2.4 Paired Pi cards** — Each paired Pi shows: vessel name, device token
      (truncated), last seen relative time, d3kOS version, online/offline badge.
- [ ] **2.5 FMP history** — Last 5 `fix_my_pi` commands from `amboat_command_queue`.
      Show: date, status (pending/completed/failed), result summary.
- [ ] **2.6 Billing rows** — Last 5 rows from `amboat_billing` for this user.
      Show: date, amount, product, status (paid/refunded).

---

## Phase 3 — Pi Diagnostics

- [ ] **3.1 Diagnostics tab on customer profile** — "Pi Health" tab alongside
      Account / Email tabs. Lazy-loaded — only fires SSH when tab is opened.
- [ ] **3.2 Service health via SSH** — Paramiko SSH to Pi. Run
      `systemctl is-active` for the 10 watchdog services. Show green/red badges.
      Timeout: 8 seconds. Graceful error if Pi offline.
- [ ] **3.3 Recent alerts table** — Last 20 rows from `amboat_alerts`
      for this user + pi_id. Columns: time, category, severity, message, status.
- [ ] **3.4 Recent commands table** — Last 10 rows from `amboat_command_queue`.
      Columns: time, command, status, result (truncated, expandable).
- [ ] **3.5 Engine snapshot sparklines** — Last 24h from `amboat_engine_snapshots`.
      Mini inline charts: RPM, coolant temp, battery voltage. Use Chart.js.
- [ ] **3.6 Refresh button** — Re-runs SSH + DB queries on demand.
      Shows "Last refreshed: X seconds ago."

---

## Phase 4 — Email Inbox

- [ ] **4.1 IMAP connection** — `email_client.py`. imaplib connection to
      `skipperdon@atmyboat.com`. Fetch INBOX, last 50 messages, cache for 2 min.
- [ ] **4.2 Inbox page** — `/inbox`. Table: from, subject, date, linked account
      (name if matched, "Unknown" if not). Unread bold. Handled dimmed.
- [ ] **4.3 Account auto-link** — On fetch, match sender email to `wpax_users.user_email`.
      Store match in local SQLite (`admin_local.db`) so repeated emails stay linked.
- [ ] **4.4 Thread view** — `/inbox/<message_id>`. Full thread oldest-first.
      Right panel: linked customer summary (tier, Pi status, active alerts).
      "Unknown sender" shows manual link dropdown.
- [ ] **4.5 Reply form** — Compose reply in thread view. Send via SMTP.
      Pre-fills To: and Subject: (Re: ...). Plain text only (day one).
- [ ] **4.6 Mark handled** — Toggle button. Stored in local SQLite.
      Inbox shows handled rows dimmed. Filter: All / Unhandled / Handled.
- [ ] **4.7 Local SQLite** — `data/admin_local.db`. Tables:
      `email_links (message_id, user_id, linked_at)`,
      `email_status (message_id, handled, handled_at)`.
      Never synced to HostPapa — stays on VM only.

---

## Phase 5 — AI Draft Assist

- [ ] **5.1 Gemini client** — `ai_client.py`. Calls Gemini Flash free tier.
      Single function: `draft_reply(customer_context, email_thread) → str`.
- [ ] **5.2 Context builder** — Assembles context dict before Gemini call:
      customer tier, FMP remaining, active alert count + categories,
      Pi last seen, d3kOS version, last command result if recent.
- [ ] **5.3 System prompt** — Professional, helpful, one-person operation tone.
      Instructs Gemini: draft a support reply, use the context, be specific,
      do not invent technical details not in the context.
- [ ] **5.4 Draft button** — Appears in thread view reply area.
      Shows spinner while Gemini responds. Populates reply textarea on return.
      Don edits freely before sending. Discard button clears to blank.
- [ ] **5.5 Fallback** — If Gemini call fails (quota, network), show
      "AI draft unavailable — compose manually" — reply form still works.

---

## Phase 6 — Tier Management + Audit Log

- [ ] **6.1 Create amboat_admin_log table** — SQL migration. Run in phpMyAdmin
      before Phase 6 code is deployed. Schema in SPEC.md Section 8.
- [ ] **6.2 Tier change form** — On customer profile: current tier shown,
      dropdown (T0/T1/T2/T3), reason textarea (min 10 chars, required).
- [ ] **6.3 Confirmation step** — After submit: "Change tier from T1 → T2.
      Reason: [reason]. Confirm?" Checkbox required. Cancel returns to form.
- [ ] **6.4 Tier write** — Updates `wpax_usermeta.atmyboat_tier`. Also queues
      `tier_change` command in `amboat_command_queue` so Pi syncs on next poll.
- [ ] **6.5 Audit log write** — Every tier change, FMP reset, alert clear
      writes to `amboat_admin_log`. Captures: admin user, target user,
      action, old value, new value, reason, IP, timestamp.
- [ ] **6.6 Audit log view** — `/audit`. Table: date, action, target user,
      old → new, reason. Filter by date range and action type.
- [ ] **6.7 FMP reset** — Button on customer profile. Reason required.
      Sets `atmyboat_fmp_used_month = 0`. Logged to audit log.

---

## Phase 7 — Database Explorer

- [ ] **7.1 Table list** — `/db`. Dropdown of allowed tables (whitelist —
      not all tables, only amboat_* + wpax_users + wpax_usermeta + d3kos_pairings).
- [ ] **7.2 Row browser** — Paginated 50 rows. Column filter inputs above each
      column. Sort by any column. SELECT only — parameterised.
- [ ] **7.3 CSV export** — "Export page" and "Export all" buttons.
      Streams CSV download. Max 10,000 rows per export.
- [ ] **7.4 Raw query box** — Optional advanced feature. Text area → Run.
      Query parser: must start with SELECT. Any other keyword → blocked, error shown.

---

## Phase 8 — In-App Support Button (PWA)

- [ ] **8.1 Support screen in app.js** — New `screens.support` screen.
      Accessible from Settings screen "Contact Support" button.
      Form: textarea (max 500 chars) + Send button. Screen header with back chevron.
- [ ] **8.2 support-request.php (HostPapa)** — New endpoint, Bearer app_token auth.
      Receives: message text. Reads user context: tier, vessel, Pi last seen,
      active alert count, d3kOS version. Sends email to skipperdon@atmyboat.com
      via wp_mail() with structured subject + full context body.
- [ ] **8.3 Rate limit** — Max 3 support requests per user per 24 hours.
      Stored in `wpax_usermeta`. Returns 429 with message if exceeded.
- [ ] **8.4 Confirmation in app** — After send: "Your message has been sent.
      We'll respond to [email] within 1 business day." Back button returns to Settings.

---

## Pre-Build Operator Actions (Do before Phase 1 coding starts)

- [x] **OP1** — Remote MySQL blocked by HostPapa. PHP proxy (Option B) adopted instead. 2026-04-03
- [x] **OP2** — IMAP/SMTP confirmed: mail.atmyboat.com, 993 SSL, 465 SSL. 2026-04-03
- [x] **OP3** — Gemini API key confirmed available in atmyboat-config.php. 2026-04-03
- [x] **OP4** — Staging: atmyb197_wp302 / atmyboat2026. Production: atmyb197_wp59874 / [redacted] 2026-04-03

---

## Build Status

| Phase | Status | Session | Notes |
|-------|--------|---------|-------|
| Pre-build (OP1–OP4) | `[x]` Complete | S16 2026-04-03 | OP1 remote MySQL attempted — blocked. Adopted PHP proxy (Option B) instead. OP2–OP4 confirmed. |
| Phase 1 — Foundation | `[x]` Complete | S16 2026-04-03 | Flask, login, bcrypt, session, lockout, config, db (PHP proxy), dashboard |
| Phase 2 — Customer View | `[x]` Complete | S16 2026-04-03 | Customer list + profile. Schema fixes applied. Branding logo deployed. |
| Phase 3 — Pi Diagnostics | `[x]` Complete | S16 2026-04-03 | Alerts + commands via PHP proxy. Live SSH deferred — VM→Pi network not confirmed. |
| Phase 4 — Email Inbox | `[x]` Complete | S16 2026-04-03 | IMAP fetch, thread view, reply, mark handled, auto-link to customer, 2min cache |
| Phase 5 — AI Draft Assist | `[x]` Complete | S16 2026-04-03 | Gemini Flash — draft button in thread view when customer is linked |
| Phase 6 — Tier + Audit Log | `[x]` Complete | S16 2026-04-03 | amboat_admin_log table created by Don in phpMyAdmin. Tier change + FMP reset logged. |
| Phase 7 — DB Explorer | `[x]` Complete | S16 2026-04-03 | 8 whitelisted tables, filter/search, CSV export |
| Phase 8 — PWA Support Button | `[x]` Complete | S16 2026-04-03 | Settings → Contact Support → support-request.php. Rate limit 3/24h. Email to skipperdon@. |

**Minimum viable tool:** Phase 1 + Phase 2 + Phase 6 (foundation + customers + tier management)
**Complete picture:** All 8 phases

---

*Build checklist version 1.0 — 2026-04-01*
*Part of v0.9.9.1 milestone — do not start until v0.9.9 security audit is complete*
