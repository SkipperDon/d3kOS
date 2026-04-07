# v0.9.7 Support Ticket System — Build Checklist
**Version:** 1.0 | **Created:** 2026-04-07 S25 | **Status:** PHASE 1 WRITTEN — PENDING DEPLOY

---

## Architecture

```
PWA (phone)
  └── Support screen (app.js)
        ├── POST support-request.php  → email + amboat_support_tickets INSERT
        │     Returns ticket_id
        └── GET  ticket-status.php    → ticket status + admin_note (resolved only)

Admin CRM (Flask VM)
  └── /tickets          → list all tickets (paginated, status filter)
  └── /ticket/<id>      → ticket detail + update form
  └── /ticket/<id>/update → POST, updates status + admin_note
        └── proxy → admin-api-tickets.php (PDO, AMBOAT_ADMIN_API_KEY)

HostPapa MySQL
  └── amboat_support_tickets (ticket_id, user_id, device_token, subject, body,
                               status ENUM, admin_note, created_at, updated_at)
```

---

## Phase 1 — Infrastructure + Basic Ticket Tracking

### HostPapa PHP files
- [x] `support-migrate.php` — one-shot table creation (FLEET_SETUP_KEY protected) — written S25
- [x] `support-request.php` — upgraded: DB insert + email, returns ticket_id — written S25
- [x] `ticket-status.php` — GET by ticket_id, user-auth, returns status+admin_note — written S25
- [x] `admin-api-tickets.php` — PDO, actions: get_tickets/get_ticket/update_ticket — written S25

### PWA (app.js)
- [x] Support screen: capture ticket_id on success, show "Ticket #N created" — written S25
- [x] Support screen: "Check Ticket Status" button + live refresh via ticket-status.php — written S25
- [x] Store ticket_id in localStorage — written S25

### Admin CRM (VM)
- [x] `tickets.html` template — list + detail views, update form — written S25
- [x] `ticket_routes_snippet.py` — Flask routes (insert before __main__) — written S25
- [ ] `proxy_call_tickets()` helper added to app.py on VM — PENDING
- [ ] 3 ticket routes added to app.py on VM — PENDING
- [ ] Tickets nav link added to base.html on VM — PENDING

### Deployment
- [x] PHP files deployed to HostPapa staging (FTP) — S25
- [x] PWA app.js deployed to HostPapa staging (FTP) — S25
- [x] tickets.html deployed to VM (/home/d3kos-admin/templates/) — S25
- [x] app.py updated on VM (routes + helper) — S25 full replacement
- [x] base.html updated on VM (Tickets nav link) — S25
- [x] support-migrate.php run in browser → table created — S25
- [x] support-migrate.php deleted from HostPapa — S25

### Phase 1 test criteria
- [x] POST support-request.php returns `{"success":true,"data":{"sent":true,"ticket_id":N}}` — S25 ✓
- [ ] GET ticket-status.php?ticket_id=N returns status for correct user — pending phone SW cache clear
- [ ] GET ticket-status.php?ticket_id=N returns 404 for wrong user (security check)
- [x] Admin CRM /tickets loads with pagination and status filter — S25 ✓
- [x] Admin CRM /ticket/N shows full ticket detail — S25 ✓ (after CSS fix)
- [ ] Admin CRM update changes status → visible on status check — pending full end-to-end
- [ ] PWA shows ticket_id on success, Check Status button works — pending SW cache clear on phone
- [x] Rate limit enforced (3 per 24h) — confirmed S25 (triggered during testing, cleared)

---

## Phase 2 — Deferred (v0.9.7 future sessions)

- [ ] Email notification to customer on ticket update (wp_mail)
- [ ] Ticket list in PWA settings screen ("My Tickets" entry point)
- [ ] Admin CRM: open ticket count badge in nav

---

## Files This Feature Touches

### New (HostPapa staging)
- `mobile/support-request.php` — replaces existing one-way email version
- `mobile/ticket-status.php`
- `mobile/admin-api-tickets.php`
- `mobile/support-migrate.php` — run once, then DELETE

### Modified (PWA)
- `app/app.js` — Support screen: ticket_id capture + status check

### New (Admin CRM VM)
- `/home/d3kos-admin/templates/tickets.html`

### Modified (Admin CRM VM)
- `/home/d3kos-admin/app.py` — proxy_call_tickets() + 3 routes
- `/home/d3kos-admin/templates/base.html` — Tickets nav link

### New (repo — deploy artifacts)
- `deployment/features/support-tickets/php/support-request.php`
- `deployment/features/support-tickets/php/support-migrate.php`
- `deployment/features/support-tickets/php/ticket-status.php`
- `deployment/features/support-tickets/php/admin-api-tickets.php`
- `deployment/features/support-tickets/crm/tickets.html`
- `deployment/features/support-tickets/crm/ticket_routes_snippet.py`
- `deployment/features/support-tickets/scripts/deploy-support-tickets.py`
