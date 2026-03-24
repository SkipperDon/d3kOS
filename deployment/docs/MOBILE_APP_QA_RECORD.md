# d3kOS Mobile App — Q&A Decision Record
**Version:** 1.0.0
**Date:** 2026-03-18
**Owner:** Donald Moskaluk — AtMyBoat.com
**Purpose:** Verbatim record of operator decisions on mobile app connectivity strategy.
This file is the authoritative source. MOBILE_APP_STRATEGY_BRIEF.md is derived from it.

---

## SESSION 1 — 2026-03-14 (reconstructed 2026-03-18)

The 2026-03-14 Q&A session produced MOBILE_APP_STRATEGY_BRIEF.md v2.0.0.
The raw Q&A was not saved at the time — only the synthesized brief was written.
The brief misinterpreted one answer (see Correction below).

**Decisions confirmed from brief:**
- Platform: PWA on GitHub Pages — no App Store, no 30% cut
- No third-party relay services for core connectivity
- QR code pairing: phone UUID → AtMyBoat.com → Pi installation ID
- No push notifications on day one (Pi is off when boat unattended)
- Payments via Stripe on atmyboat.com only — not in-app
- Do NOT compete with ActiveCaptain
- Fix My Pi: $29.99/incident T0/T1, 3 free/month T2, unlimited T3
- PDF Boat Reports via mPDF on HostPapa
- OS Lockdown via apt-mark hold + pre-upgrade hook
- Find My Boat: last known GPS + Pi state from last export (Tesla app model)

**Correction to PDF Boat Reports (2026-03-18):**
Original brief stated "Available at T1 and above."
Operator confirmed: T2 and T3 only. T1 does not include PDF reports.

**Decision 11 confirmed (2026-03-18) — OS Lockdown:**
apt-mark hold on all critical packages. Pre-upgrade hook warns user.
d3kOS paths (/opt/d3kos/, /var/www/html/) never touched by apt upgrade.
Fix My Pi detects and repairs any OS-level breakage post-upgrade.

**Decision 12 confirmed (2026-03-18) — Push Notifications:**
Deferred. No money, no push unless Pi is actively communicating.
Pi is off when boat is unattended — it cannot push.
Push notifications only work while Pi is online.
Phase 2 item: revisit if/when budget allows persistent relay infrastructure.
App shows last known state when Pi is offline (Tesla app model).

---

## SESSION 2 — 2026-03-18 (verbatim)

### Correction to 2026-03-14 Brief — Decision 3

**What the brief said:**
HostPapa PHP + MySQL message broker. Pi polls outbound every 30 seconds.
"Works through marina WiFi, 4G, any firewall — exactly like IP cameras."

**What the operator actually said:**
Use the same P2P technology that IP cameras (e.g. Reolink) use to punch
through firewalls and connect directly to a phone app.
The brief captured the IP camera reference but drew the wrong conclusion —
it used "like IP cameras" as a metaphor for polling, not as a technology directive.

**Decision 9 confirmed (2026-03-18) — OTA Upgrade tiers:**
T0 = no OTA (no mobile app, no remote connection — direct Pi access only).
T1, T2, T3 = OTA from PWA. Command queue → Pi picks up in 30s → progress bar in app.

**Decision 6 confirmed (2026-03-18) — Product Identity:**
d3kOS = AI First Mate. A companion system to chartplotters and ActiveCaptain.
Does not duplicate navigation or community features. Adds the AI intelligence
layer: boat health, engine monitoring, system management, AI analysis.
Chartplotter = navigation. ActiveCaptain = marina/community. d3kOS = boat
systems intelligence. All three sit side by side on helm and phone.

**Operator confirmation (2026-03-18):**
"I believe it is" — confirmed when presented with the interpretation:
"the Pi should connect to the mobile app using the same P2P technology that
Reolink and similar IP camera systems use to punch through firewalls and
connect directly to a phone app."

### Technology Decision — v0.9.4

**Question:** Which P2P option?
- Option A: WebRTC with STUN (public free servers — Google, Cloudflare)
- Option B: Throughtek TUTK SDK (proprietary, Reolink's actual SDK — not self-hostable)
- Option C: Self-hosted UDP hole punching coordination server

**Decision 5 confirmed (2026-03-18):**
Payments via Stripe on atmyboat.com. User initiates from inside the PWA (tap Upgrade
or Fix My Pi) → PWA opens atmyboat.com payment page in an embedded browser view →
Stripe payment completes → PWA detects tier change and unlocks features.
User never leaves the PWA experience. No App Store cut. 2.9% + 30c Stripe only.

**Operator answer:** Option A — WebRTC/STUN.

**Rationale stated by operator:** $0 continuous cost.

**Confirmed understanding:**
- STUN servers (Google, Cloudflare) are permanently free
- Works for standard NAT (marina WiFi, 4G) — covers the boat use case
- Browser/PWA native — no plugin or SDK required
- ~10-15% of symmetric NAT networks may fail — acceptable risk for boat users
- TURN relay (cost) can be added later if real users report failures

### Technology Decision — v1.1

**Operator answer:** Option C — self-hosted UDP hole punching coordination server.

**Rationale:** Full independence, no third-party dependency. Deferred to v1.1.

### Tailscale

**Operator statement:** "Tailscale was never my choice."

**Status:** Tailscale is currently running on Pi at 100.88.112.63.
It was installed without explicit operator authorization.
It must be removed. No features depend on it.
Removal is a tracked task — see PROJECT_CHECKLIST.md.

---

## SESSION 3 — 2026-03-24 (product decisions Q&A with operator)

**Cross-reference:** All decisions in this session are fully recorded in
`deployment/v0.9.3/ATMYBOAT_BUILD_REFERENCE.md` Part 16 (authoritative source).
This entry records the v0.9.4-relevant subset only.

### Decision Corrections — v0.9.4 Impact

**T0 Fix My Pi — CORRECTION (supersedes all prior references):**
T0 cannot use Fix My Pi under any circumstances.
T0 has no mobile app and no account.
The ONLY path for T0 is: download new image from atmyboat.com/download, reinstall on Pi.
T0 must upgrade to T1 (register free account, pair app) before Fix My Pi is accessible.

**T3 pricing — CORRECTION:**
T3 = $99.99/YEAR (annual billing only). Not monthly.
Previous brief did not specify billing frequency. Annual is now confirmed and final.

**T1 Fix My Pi flow — CLARIFICATION:**
$29.99 per incident. Stripe payment must authorize first.
Only after payment is authorized does the mobile app launch the fix deployment to the Pi.
Sequence: user taps Fix My Pi → Stripe payment page → payment completes → fix command
written to command queue → Pi picks up in 30s → fix executes → report returned to app.

### New Decisions — v0.9.4 Relevant

**Decision 13 — Boat Notifications:**
- T1: in-app push (PWA) + email (MailPoet)
- T2/T3: in-app push + email + SMS (Twilio)
- Alert triggers: engine critical (oil, coolant, RPM), low battery, motion detected,
  geofence breach/anchor drag, Pi offline (30-min default), Fix My Pi complete,
  OTA available, T2 check allowance low (1 remaining)
- Critical alerts sent immediately. Non-critical batched (max 1/day).
- User controls: per-alert toggle, geofence radius, Pi offline threshold,
  SMS number (T2+), quiet hours.

**Decision 14 — Geofence / Anchor Drag:**
Centre point = automatic GPS position when user taps "Set Anchor" in app.
No manual coordinate entry. User sets radius only (slider, default 50m).
"Weigh Anchor" deactivates. Pi monitors, fires Critical alert if boat exits radius.

**Decision 15 — Registration required for T1+:**
T1 and higher require account registration on atmyboat.com.
Registration captures: first name, last name, email, password.
CASL opt-in checkbox required (Canadian anti-spam law).
All boat details captured in Pi onboarding wizard — not at registration.
QR pairing happens post-login, not on login page.

**Decision 16 — Community Map access:**
T1+ only. Must be registered and app paired.
Your boat = red dot. Other d3kOS boats = green dots.
Leaflet + OpenStreetMap. Position blurred to ~500m. Clicking dot shows nothing.
Privacy zone available in Settings. 30-day inactivity → drops off map.
Auto-on after T1 pairing. Opt-out in Settings.

---

## STANDING RULES DERIVED FROM THIS RECORD

1. Pi-to-phone connectivity = WebRTC/STUN (v0.9.4). Not polling. Not message broker for live connection.
2. Message broker (HostPapa) is still used for: command queue, data export, OTA upgrades, Fix My Pi.
   It is NOT used for the live Pi ↔ phone tunnel.
3. Tailscale must be removed from Pi before v0.9.4 build begins.
4. Option C (self-hosted coordination server) is a v1.1 item — do not build in v0.9.4.
5. TURN server is deferred — not in v0.9.4 scope unless user testing reveals it is needed.

---

*d3kOS Mobile App Q&A Decision Record v1.0.0 — Donald Moskaluk / AtMyBoat.com — 2026-03-18*
