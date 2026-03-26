# v0.9.4 — d3kOS Mobile Companion App — Build Plan
**Version:** 1.0.0
**Date:** 2026-03-26
**Owner:** Donald Moskaluk — AtMyBoat.com
**Status:** DRAFT — awaiting operator approval before any code is written

---

## GOVERNING DOCUMENTS (read before every session)

- Strategy: `deployment/docs/MOBILE_APP_STRATEGY_BRIEF.md` v2.0.0
- Decisions: `deployment/docs/MOBILE_APP_QA_RECORD.md` v1.0.0 — authoritative
- v0.9.3 AtMyBoat.com rules: `deployment/v0.9.3/ATMYBOAT_STANDING_INSTRUCTION.md`
- Pi architecture: `deployment/docs/DEPLOYMENT_INDEX.md`

---

## WHAT IS ALREADY BUILT (do not rebuild)

### AtMyBoat.com PHP side — COMPLETE (built v0.9.3 S5)
| Endpoint | File | Status |
|----------|------|--------|
| Device registration | `mobile/register-device.php` | ✅ Built |
| QR pairing | `mobile/pair-device.php` | ✅ Built |
| Command queue read/write | `mobile/command-queue.php` | ✅ Built |
| Pi heartbeat + data ingress | `mobile/data-ingress.php` | ✅ Built |
| Tier + feature flags | `mobile/tier-features.php` | ✅ Built |
| Fix My Pi billing + lifecycle | `mobile/fix-my-pi-billing.php` | ✅ Built |
| PDF report generation | `mobile/pdf-report.php` | ✅ Built |
| Version registry | `mobile/version-registry.php` | ✅ Built |
| Community positions + markers | `mobile/community-*.php` | ✅ Built |

### Pi side — PARTIAL
| Component | Status |
|-----------|--------|
| Installation ID (`license.json`) | ✅ Built |
| Tier detection | ✅ Built |
| remote_api `:8111` | ✅ Built |
| export-manager `:8094` | ✅ Partial — 3 of 8 categories built |
| QR code display (Settings) | ✅ Built |
| Signal K `:8099` | ✅ Running |
| Self-heal stub | ⚠️ Port 8090 referenced — needs full implementation |
| Command Consumer Agent | ❌ Not built |
| Fix My Pi diagnostic + repair | ❌ Not built |
| OS lockdown (apt-mark hold) | ❌ Not built |
| Tailscale | ⚠️ Must be removed before v0.9.4 build begins |

---

## KEY CONSTRAINTS (non-negotiable — from Q&A record)

- Pi ↔ phone LIVE connection = WebRTC/STUN P2P — not polling
- Message broker (HostPapa) = command queue, OTA, Fix My Pi, data export only
- No open inbound ports on Pi — ever
- No TURN server unless user testing proves necessary
- Option C (self-hosted coordination) = v1.1, not v0.9.4
- Tailscale removed before build starts
- PWA on GitHub Pages — no App Store
- All payments via Stripe on atmyboat.com — never in-app
- Never store user question text — token counts only
- Never send GPS to AI — summary stats only
- PDF reports: T2 and T3 only (T1 does NOT get PDF reports)
- Fix My Pi: T0 = NO access. T1 = $29.99/incident. T2 = 3 free/month. T3 = unlimited.

---

## INSIGHT — MOST DAY-1 FEATURES DON'T NEED WEBRTC

The live WebRTC tunnel is needed only for truly real-time Pi data. Most day-1
features read from AtMyBoat.com's stored data (export-manager pushes):

| Feature | Needs WebRTC? |
|---------|--------------|
| Find My Boat (last known GPS) | No — reads from data export |
| System health dashboard | No — reads from data export |
| OTA upgrade | No — uses command queue |
| Fix My Pi | No — uses command queue |
| Alerts history | No — reads from data export |
| Engine data (last known) | No — reads from data export |
| Boatlog view | No — reads from data export |
| PDF report | No — generated on AtMyBoat.com |
| **Engine data (LIVE)** | **Yes — WebRTC only** |
| **Live camera feed** | **Yes — WebRTC only (Phase 2)** |

**Strategy: Build everything without WebRTC first. Ship a working app. Add WebRTC live data in S6.**

---

## BUILD SEQUENCE — 8 SESSIONS

### S1 — Pi Foundation (Pi must be online)
**Goal:** Pi can push all 8 export categories + receive and execute commands

Tasks:
1. Remove Tailscale from Pi (prerequisite — Don confirms Pi is online first)
2. Audit export-manager — identify which 3 categories are built, which 5 are missing
3. Complete export-manager — all 8 categories:
   - System health (services status, CPU, memory, storage, uptime)
   - GPS position (last known lat/lng, speed, course)
   - Engine snapshot (RPM, oil, coolant, fuel, hours)
   - Alerts (recent history)
   - Boatlog entries (recent, with voice note filenames)
   - Signal K summary (key values)
   - d3kOS version + config summary
   - Maintenance intervals (hours since last service — if tracked)
4. Build **Command Consumer Agent** (`d3kos-cloud-agent.service`):
   - Python service, polls `command-queue.php` every 30s
   - Executes: `ota_upgrade`, `fix_my_pi`, `pair_confirmed`, `tier_change`
   - Writes result back to command queue
   - Systemd service, auto-restart
5. Test: write a test command to AtMyBoat.com staging command queue → confirm Pi picks it up in 30s

**Deliverables:** export-manager complete, cloud agent running, end-to-end command test passing

---

### S2 — PWA Shell + Auth + Pairing
**Goal:** Installable PWA on GitHub Pages, users can log in and pair their Pi

Tasks:
1. Create GitHub Pages repo: `SkipperDon/d3kos-app` (or agreed name)
2. PWA shell:
   - `manifest.json` (name, icons, display: standalone, theme colour)
   - Service worker (offline shell, update detection)
   - App frame (bottom nav: Home / Engine / Alerts / Log / Account)
   - Dark marine theme matching d3kOS design system
3. Login / Register screen:
   - Login: POST to atmyboat.com/staging/wp-json or mobile auth endpoint
   - Register: opens atmyboat.com/register in in-app browser
   - JWT or session token stored in localStorage
4. QR pairing screen:
   - Camera access → scan QR from Pi Settings page
   - POST to pair-device.php → confirm pairing
   - Show success state with paired Pi name
5. Deploy to GitHub Pages, test on iPhone (Safari) and Android (Chrome)

**Deliverables:** Installable PWA, login working, QR pairing working

---

### S3 — Home Screen + Find My Boat + OTA
**Goal:** User opens app and sees their boat's status. Can trigger an OTA upgrade.

Tasks:
1. Home screen — reads last export from AtMyBoat.com:
   - Boat status (ONLINE / OFFLINE — based on last_seen_at age)
   - Last synced timestamp
   - Last known GPS position + reverse geocode (city/marina name)
   - System health grid (Signal K, AvNav, GPS, Camera, AI Bridge, Storage, CPU Temp, Uptime)
   - Update available banner (if version-registry shows newer version)
   - Engine summary (RPM, oil, coolant — last known)
   - Last boatlog entry
2. OTA upgrade flow:
   - Version check against version-registry.php
   - Release notes display
   - "Upgrade Now" → writes `ota_upgrade` command to queue
   - Progress polling (command status: pending → in progress → completed)
   - Progress bar: Downloading → Installing → Restarting → Complete
   - Confirm new version running

**Deliverables:** Home screen rendering real Pi data, OTA upgrade flow working end-to-end

---

### S4 — Fix My Pi
**Goal:** User can trigger a Fix My Pi repair from the app, pay via Stripe, see the report.

Tasks:
1. **Pi — Fix My Pi diagnostic + repair script** (`fix-my-pi-watchdog.sh`):
   - Full bash script (survives broken Python)
   - Checks: all d3kOS services (systemctl status), config file validity (JSON parse),
     database integrity (SQLite PRAGMA), required files (checksum), disk, CPU temp, network
   - Repairs: restart crashed services, restore corrupt configs from backup,
     restore missing files from package manifest
   - Writes structured report (JSON) back to command queue result
   - Does NOT upgrade anything — restore only
2. Fix My Pi app flow:
   - Disclaimer screen (what it does, what it costs, no guarantee)
   - T1: "Pay $29.99" → opens Stripe on atmyboat.com → payment completes → fix begins
   - T2: "Use 1 of 3 monthly checks" → confirm → fix begins
   - T3: "Start Fix" → fix begins immediately
   - Progress display: polling command queue status every 10s
   - Report display: issues found, issues resolved, all services status
3. T1 auto-refund on failure (already built in fix-my-pi-billing.php — just wire to app display)

**Deliverables:** Fix My Pi works end-to-end — trigger, payment, repair on Pi, report in app

---

### S5 — Engine, Alerts, Boatlog Views
**Goal:** User can see engine history, alert history, and boatlog entries in the app.

Tasks:
1. Engine view:
   - Current / last known: RPM, oil pressure, coolant temp, fuel level, engine hours
   - Battery voltage
   - Trend charts (last 24h from export history)
   - Alert state indicators (normal / warning / critical colour coding)
2. Alerts view:
   - List of recent alerts (type, message, timestamp, resolved/unresolved)
   - Filter by type (engine, GPS, anchor, system)
   - Mark resolved (writes command to queue)
3. Boatlog view:
   - Entry list (date, type, summary text)
   - Entry detail (full text, voice note playback if present)
   - Voice note: fetch audio file from Pi via AtMyBoat.com proxy
   - Search by date range or keyword

**Deliverables:** All three views rendering real data from Pi exports

---

### S6 — WebRTC/STUN Live Tunnel
**Goal:** App connects directly to Pi in real time when Pi is online. Live engine data.

Tasks:
1. **Signaling server** (minimal — HostPapa PHP):
   - Pi registers its WebRTC offer to AtMyBoat.com
   - App picks up offer, sends answer back
   - ICE candidates exchanged via AtMyBoat.com (polling or long-poll)
   - After handshake: P2P direct. AtMyBoat.com exits the flow.
2. **Pi side** (Python — aiortc library):
   - WebRTC peer connection
   - Streams live Signal K data (engine, GPS) over data channel
   - Initiates outbound to signaling server — no inbound ports
3. **PWA side** (browser native WebRTC):
   - Picks up Pi offer from signaling server
   - Establishes P2P data channel
   - Live engine data updates home screen + engine view in real time
4. Fallback: if WebRTC fails, app falls back gracefully to last known data (already working)

**Deliverables:** Live engine + GPS data in app when Pi is online on same or different network

**Note:** This session may need to be split into S6a (signaling) and S6b (live data) depending on WebRTC complexity.

---

### S7 — PDF Reports + OS Lockdown + Account Screen
**Goal:** T2/T3 users can download PDF reports. Pi is protected from OS upgrades.

Tasks:
1. PDF report flow in app (T2/T3 only):
   - "Generate Report" → POST to pdf-report.php → progress → download
   - Report viewer (in-app PDF display or browser open)
   - Report history list (past reports, downloadable)
2. OS lockdown on Pi:
   - `apt-mark hold` on all critical packages (Python version, Flask, AvNav, Signal K)
   - Pre-upgrade hook: warns user "This may break d3kOS. Run Fix My Pi after upgrade."
   - Deployed via Command Consumer Agent (one-time setup command)
3. Account screen in app:
   - Current tier display (T1 / T2 / T3)
   - Upgrade link (opens atmyboat.com/upgrade in in-app browser)
   - Fix My Pi usage (T2: X of 3 used this month)
   - Paired Pi info (name, version, last seen)
   - Settings: units (metric/imperial), language (v1.1), quiet hours

**Deliverables:** PDF reports working for T2/T3, OS lockdown deployed, account screen complete

---

### S8 — Testing, Hardening, Release Candidate
**Goal:** v0.9.4 is stable, tested, and ready.

Tasks:
1. Offline state testing:
   - Pi offline → app shows last known state cleanly, no errors
   - App offline → cached shell loads, shows last data, queues actions
2. Error state handling:
   - Command queue timeout (Pi doesn't pick up in 10 min — alert user)
   - WebRTC failure → graceful fallback to polled data
   - Payment failure → clear message, no command written
3. AODA compliance pass on PWA (18px min, 48px touch targets, contrast 4.5:1)
4. Service worker update flow test (push new version → users get it on next open)
5. iPhone + Android install-to-home-screen test
6. version.txt bump to v0.9.4
7. SESSION_LOG + CHANGELOG + PROJECT_CHECKLIST updated

**Deliverables:** v0.9.4 release candidate — stable, tested, AODA compliant

---

## WHAT v0.9.4.1 MIGHT COVER

Don mentioned v0.9.4.1 as a separate milestone before live push. Scope TBD by operator. Likely candidates:
- Bug fixes from S8 testing
- Push notifications (if budget allows relay infrastructure)
- T3 fleet management (multiple Pis)
- Any WebRTC edge cases from real-world testing

---

## HARD RULES FOR v0.9.4 SESSIONS

1. **Content-first**: Produce session content plan → Don approves → build. No exceptions.
2. **Pi is online**: S1 requires Pi. Flag immediately if Pi is off.
3. **No live atmyboat.com touches**: All AtMyBoat.com work goes to staging only.
4. **No git push**: All repos local only. Don authorizes any push explicitly.
5. **WebRTC is S6**: Do not attempt WebRTC earlier. Build and ship the polling-based app first.
6. **Tailscale removed before S1 starts**: Do not begin S1 until Tailscale is confirmed off the Pi.
7. **HIGH RISK = STOP**: Any action touching live Pi services, live site, or Stripe live keys requires explicit authorization. No scripting live deploys without operator instruction.

---

## OPEN QUESTIONS (answer before S1 starts)

1. **GitHub repo name for PWA?** Suggest: `d3kos-app` under `SkipperDon`
2. **Is Pi currently online?** S1 requires SSH access.
3. **Tailscale — confirm removed?** Memory says it was removed 2026-03-19. Verify.
4. **What are the 3 completed export categories?** Need to audit export-manager before S1.
5. **mPDF on HostPapa** — is it installed? pdf-report.php assumes it is. Verify before S7.

---

*v0.9.4 Build Plan v1.0.0 — Donald Moskaluk / AtMyBoat.com — 2026-03-26*
*Awaiting operator approval. No code written until approved.*
