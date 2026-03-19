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

## STANDING RULES DERIVED FROM THIS RECORD

1. Pi-to-phone connectivity = WebRTC/STUN (v0.9.4). Not polling. Not message broker for live connection.
2. Message broker (HostPapa) is still used for: command queue, data export, OTA upgrades, Fix My Pi.
   It is NOT used for the live Pi ↔ phone tunnel.
3. Tailscale must be removed from Pi before v0.9.4 build begins.
4. Option C (self-hosted coordination server) is a v1.1 item — do not build in v0.9.4.
5. TURN server is deferred — not in v0.9.4 scope unless user testing reveals it is needed.

---

*d3kOS Mobile App Q&A Decision Record v1.0.0 — Donald Moskaluk / AtMyBoat.com — 2026-03-18*
