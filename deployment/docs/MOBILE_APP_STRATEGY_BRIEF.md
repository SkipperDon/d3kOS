# d3kOS Mobile App — Strategy Brief
**Version:** 2.0.0
**Date:** 2026-03-14
**Owner:** Donald Moskaluk — AtMyBoat.com
**Status:** FINAL — built from Q&A session with operator

---

## SESSION OPENER — COPY AND PASTE THIS TO START A STRATEGY SESSION

```
I am Donald Moskaluk, owner of AtMyBoat.com and creator of d3kOS — a
Raspberry Pi marine dashboard system for helm-mounted use on boats.

I want to build a mobile companion app for d3kOS. The strategy has been
fully worked out in MOBILE_APP_STRATEGY_BRIEF.md. Please read that document
first, then help me produce a complete implementation specification using the
AI Engineering Specification and Solution Design Template structure:
  - Problem definition
  - System architecture with ASCII diagram
  - Technology stack with tradeoffs
  - Data model (new vs existing)
  - API design (all endpoints needed)
  - Build sequence — day one vs Phase 2
  - Constraints that cannot be changed

Do not assume anything not stated in the brief. Confirm your understanding
of the vision before producing the spec.
```

---

## VISION — ONE SENTENCE

> Know your boat's health, get AI analysis, manage your system, and find
> your boat from anywhere — before you even leave the house.

## WHAT THIS IS NOT

This app does NOT compete with Garmin ActiveCaptain. ActiveCaptain handles
marina reviews, anchorages, and chart updates. d3kOS Companion handles boat
systems intelligence, engine health, Pi management, and AI analysis. They
complement each other. No community features. No marina reviews. No chart
management. Those are ActiveCaptain's job.

---

## ARCHITECTURE DECISIONS — FINAL

### Decision 1 — Platform: PWA on GitHub Pages

The app is a Progressive Web App (PWA) hosted on GitHub Pages.

- Zero App Store fees (no $99/year Apple, no $25 Google)
- No 30% cut on purchases
- No App Store review process
- No Apple or Google terms and conditions on payments
- Deploys like a website — push to GitHub, users get update automatically
- User installs by opening browser → atmyboat.com/app → Add to Home Screen
- Works on iPhone (Safari) and Android (Chrome)
- Looks and feels like a native app

All payments go through Stripe on atmyboat.com directly. Apple and Google
payment rules only apply to apps distributed through their stores. A PWA
is not in their store — their rules do not apply.

### Decision 2 — No third-party relay services

No Tailscale. No Supabase. No AWS. No DigitalOcean. No Cloudflare.
The only infrastructure used is what already exists:

- AtMyBoat.com on HostPapa (already paid) — message broker + identity
- GitHub (already have) — PWA hosting via GitHub Pages
- Stripe — payment processing (2.9% + 30c per transaction, no other fees)

### Decision 3 — HostPapa as the message broker (not a tunnel)

HostPapa shared hosting cannot run a true VPN tunnel. Instead it runs a
PHP + MySQL message broker that achieves the same functional result:

```
MOBILE APP (PWA — GitHub Pages)
    |  reads data / writes commands via HTTPS
    v
ATMYBOAT.COM — PHP + MySQL  (HostPapa — already paid for)
    ^
    |  Pi polls outbound every 30 seconds (punches through any firewall)
    |  Pi pushes data exports on schedule (outbound HTTPS only)
    |
PI COMMAND CONSUMER AGENT  (new Python service on Pi, ~150 lines)
    |
    v
EXISTING Pi SERVICES
(remote_api :8111, export-manager :8094, update manager, all services)
```

The Pi ALWAYS initiates connections outbound. No open inbound ports ever.
Works through marina WiFi, 4G, any firewall — exactly like IP cameras.

### Decision 4 — Unique device identity per app install

Every mobile app install generates a unique UUID device token, stored
locally on the phone. This is the device's permanent identity — equivalent
to a unique global address. No third-party address assignment needed.

### Decision 5 — QR code pairing

1. User installs PWA → creates AtMyBoat.com account → T1 unlocked
2. App shows QR scanner
3. On the Pi: Settings → "Pair Mobile App" → QR code displayed on screen
4. User scans QR → AtMyBoat.com links device token + Pi installation ID + account
5. Both screens confirm pairing — done
6. Pi installation ID already exists (implemented in v0.9.2)

### Decision 6 — No push notifications on day one

The Pi will be OFF most of the time when the boat is unattended (battery
drainage concern). A Pi that is off cannot push anything. The app shows
last known state from the last export before shutdown — exactly like the
Tesla app shows car state when the car is off. Push notifications are
Phase 2, built when there is budget for a VPS to run the relay.

### Decision 7 — Payments via Stripe on AtMyBoat.com website

Upgrades are purchased on atmyboat.com/upgrade in the browser, not inside
the app. App checks tier status from AtMyBoat.com account on each open and
unlocks features accordingly. Feature flags on AtMyBoat.com control what
each tier can see — no app code changes needed to add/remove tier features.

### Decision 8 — App updates via GitHub Actions + Service Worker

Push new code to GitHub → GitHub Actions deploys to GitHub Pages in ~2 min
→ Service Worker on user's device detects change → app updates silently
on next open. No App Store. No user action. No approval wait.

When an app update also requires a new Pi version, the app checks the Pi's
current version via AtMyBoat.com. If the Pi is behind, the app prompts the
user to upgrade the Pi before enabling the new feature.

---

## TIER SYSTEM — FINAL

| Tier | What They Get | Fix My Pi | Price |
|------|--------------|-----------|-------|
| T0 | Pi dashboard only — no mobile app | $29.99 per one-time check | Free |
| T1 | Pi + 1 paired phone — full read access | $29.99 per one-time check | Free |
| T2 | Pi + multiple phones (family/crew) | 3 free checks per month | $9.99/month |
| T3 | Multiple Pis + 1 account (fleet) | Unlimited free checks | TBD |

Fix My Pi checks for T0/T1 are purchased via Stripe on atmyboat.com — $29.99
per incident. No subscription required. T2/T3 checks are consumed from the
monthly allowance. T3 is unlimited.

---

## DAY ONE FEATURE SET (T1 — Single User)

### Home Screen — "Find My Boat"

Inspired by the Tesla app. Before the user even leaves the house they see:

```
d3kOS COMPANION
-----------------------------------------
BOAT STATUS                    ONLINE
Last synced: 8 minutes ago

LAST KNOWN LOCATION
44.3821 N  79.4105 W
Orillia Municipal Marina

SYSTEM HEALTH
Signal K    [OK]     GPS         [OK]
AvNav       [OK]     Camera      [OK]
AI Bridge   [OK]     Storage     74%
CPU Temp    52C      Uptime      14d 3h

UPDATE AVAILABLE — v0.9.3
Route Analysis + Port Arrival Briefing
[ View Release Notes ]    [ Upgrade Now ]

ENGINE  (live / last known)
RPM 0  |  Oil 42 PSI  |  Coolant 72F
Battery  12.7V  |  No active alerts

LAST BOATLOG ENTRY
Yesterday 4:32pm
"Topped up fuel, starboard tank, 42L"
-----------------------------------------
```

If Pi is offline, screen shows "OFFLINE — Last synced: [date/time]" and
displays last known values for all fields. GPS shows last known position.

### OTA Upgrade from Phone

1. App shows new version available with release notes
2. User taps "Upgrade Now"
3. Command written to AtMyBoat.com message broker
4. Pi Command Consumer Agent picks it up (within 30 seconds)
5. Pi downloads and installs update, writes progress back step by step
6. App shows live progress bar: Downloading → Installing → Restarting → Complete
7. App confirms new version running and all services healthy

No USB card. No sitting at the helm. Upgrade the entire boat navigation
system from the couch.

### Fix My Pi — Automated Repair Service

Triggered from mobile app. User taps "Fix My Pi."

**What the Pi diagnostic does:**
- Checks every d3kOS service (systemctl status — running? healthy?)
- Validates every config file (valid JSON, not corrupt, required keys present)
- Checks database integrity (SQLite PRAGMA integrity_check)
- Verifies all required files exist (checksum against known good manifest)
- Checks disk space, CPU temperature, memory
- Checks network connectivity (AvNav, Signal K, Gemini proxy reachable)

**What the repair does:**
- Restarts any crashed service
- Restores any corrupt config from the last known good backup
- Restores any missing file from the d3kOS package manifest
- Does NOT upgrade anything — only restores to last known working state
- Does NOT make improvements — diagnostic and restore only

**Report returned to mobile app:**
```
Fix My Pi Report — 2026-03-14 09:42
------------------------------------
Issues found: 2
Issues resolved: 2

1. d3kos-gemini.service — was stopped (crashed at 02:14)
   Action: restarted. Now running.

2. ai-bridge.env — file was corrupt (invalid JSON)
   Action: restored from backup dated 2026-03-12.
   All values confirmed intact.

All 9 services now running. No further issues found.
System restored to working state.
------------------------------------
```

Report stored in AtMyBoat.com central database under this installation ID.
Accessible from app at any time. T0/T1 charged $29.99 via Stripe for each
Fix My Pi run. T2 deducted from monthly allowance. T3 unlimited.

### PDF Boat Report

Generated by AtMyBoat.com on demand or on schedule. Contains:
- System health summary (all services, uptime, storage, CPU history)
- Engine performance summary (RPM, oil, temp, fuel — trends vs baseline)
- Alert history (all alerts in period, resolved/unresolved)
- Boatlog summary (entries, voice notes, auto-entries)
- Maintenance status (service intervals, hours since last service)
- AI recommendations (Gemini analysis of all data — what to watch, what to fix)

Generated as PDF on AtMyBoat.com (PHP + mPDF library — no extra server needed).
Stored in central database. Downloadable from app. Available at T1 and above.

---

## OS LOCKDOWN — Pi Protection

A Raspberry Pi OS upgrade (apt upgrade) can overwrite packages that d3kOS
depends on and break the system. The lockdown prevents this.

**Implementation:**
- d3kOS installs with a protected package list (`apt-mark hold` on all
  critical dependencies — Python version, Flask, AvNav, Signal K, etc.)
- A pre-upgrade hook warns the user: "This may break d3kOS. Run Fix My Pi
  after any OS upgrade."
- Fix My Pi detects if OS-level changes have broken d3kOS and restores
  compatibility (restores Python packages, restarts affected services)
- d3kOS code lives in /opt/d3kos/ and /var/www/html/ — these paths are
  never touched by apt upgrade

---

## WHAT DOES NOT COMPETE WITH ACTIVE CAPTAIN

The following features are explicitly OUT OF SCOPE:
- Marina reviews
- Anchorage ratings
- Waypoint sharing
- Chart updates
- Route community sharing
- Fuel price tracking
- Hazard reporting

Users who want these features use ActiveCaptain. d3kOS Companion and
ActiveCaptain are used side by side on the same phone.

---

## PHASE 2 FEATURES (deferred — need VPS budget or more users)

- Push notifications for critical alerts (requires server-side push infrastructure)
- Live screen viewing (requires persistent connection — Tailscale or VPS relay)
- T3 fleet management (multiple Pis on one account)
- Anchor watch mobile alerts (Pi must be on and anchor watch active)
- Community features if decided later (not competing with ActiveCaptain)

---

## FULL ZERO-COST INFRASTRUCTURE STACK

| Component | Platform | Monthly Cost |
|-----------|----------|-------------|
| PWA mobile app | GitHub Pages | $0 |
| App CI/CD deployment | GitHub Actions | $0 |
| Message broker + pairing + DB | AtMyBoat.com HostPapa | Already paid |
| Fix My Pi reports storage | AtMyBoat.com MySQL | Already paid |
| PDF report generation | AtMyBoat.com PHP (mPDF) | Already paid |
| Payments | Stripe (2.9% + 30c per transaction) | $0 fixed cost |
| **Total new infrastructure** | | **$0** |

---

## WHAT ALREADY EXISTS ON THE Pi (DO NOT REBUILD)

| Component | Status | Location |
|-----------|--------|----------|
| Installation ID | Built | /opt/d3kos/config/license.json |
| Tier system | Built | license.json, tier detection active |
| remote_api | Built | Pi :8111 — remote action execution |
| export-manager | Built | Pi :8094 — data push (partial, 3/8 categories) |
| Update manager | Built | Pi — curl-based, needs Command Agent wrapper |
| Self-heal stub | Exists | Port 8090 referenced — needs full implementation |
| QR code generation | Built | Displays on Pi settings page |
| Signal K data | Running | :8099 — all engine + GPS data |
| AvNav | Running | :8080 — navigation |
| All d3kOS services | Running | Ports 3000, 3001, 3002, 8084, 8086, 8087, 8089 |
| Tailscale | Running | IP 100.88.112.63 — available for Phase 2 live screen |

## WHAT NEEDS TO BE BUILT

### Pi side (new):
1. **Command Consumer Agent** — polls AtMyBoat.com every 30s for pending
   commands, executes via existing services, writes result back. ~150 lines
   Python. New systemd service: d3kos-cloud-agent.service
2. **Fix My Pi diagnostic + repair script** — full service/config/file
   verification and restore. Triggered by Command Consumer Agent.
3. **Complete export-manager** — expand from 3 to all 8 data categories
4. **OS lockdown** — apt-mark hold on critical packages, pre-upgrade hook

### AtMyBoat.com side (new PHP endpoints):
1. **Device registration** — store device UUID, link to account
2. **QR pairing** — link device UUID + Pi installation ID to account
3. **Command queue** — write/read pending commands per installation ID
4. **Data ingress** — receive Pi exports, store in central DB
5. **Tier/feature flag API** — return what features this account can access
6. **Fix My Pi billing** — Stripe $29.99 charge for T0/T1 on each run
7. **PDF report generation** — mPDF, stored and served per installation
8. **Version registry** — current d3kOS version, release notes, min app version

### Mobile PWA (new, GitHub Pages):
1. Home screen — boat status, find my boat, health dashboard
2. OTA upgrade flow — version check, release notes, progress bar
3. Fix My Pi — trigger, progress, report display
4. Engine data view — live/last known values, trend charts
5. Boatlog view — entry list, search, voice note playback
6. Alerts view — history, resolved/unresolved
7. PDF report — download and view
8. Account + pairing — login, QR scanner, tier display
9. Settings — notification prefs, units, language

---

## BUILD SEQUENCE — DAY ONE TO SHIP

**Stage 1 — Foundation (Pi + AtMyBoat.com)**
1. Complete Pi export-manager (all 8 categories)
2. Build AtMyBoat.com data ingress + command queue PHP endpoints
3. Build Pi Command Consumer Agent
4. Build device registration + QR pairing on AtMyBoat.com

**Stage 2 — Core Mobile App (GitHub Pages PWA)**
1. Account creation + QR pairing screen
2. Home screen (boat status, find my boat, health, update available)
3. OTA upgrade flow
4. Engine + alerts view

**Stage 3 — Fix My Pi**
1. Build Pi diagnostic + repair script
2. Build Fix My Pi command + report flow
3. Build Stripe $29.99 payment on AtMyBoat.com
4. Report storage + display in app

**Stage 4 — PDF Reports**
1. Install mPDF on HostPapa
2. Build report generation PHP script
3. Build AI recommendation call (Gemini 2.5 Flash, MAX_TOKENS 1000)
4. Report storage + download in app

**Stage 5 — OS Lockdown**
1. Package hold list finalised
2. Pre-upgrade hook deployed
3. Fix My Pi extended to detect and repair OS-level breakage

---

## KEY CONSTRAINTS — NON-NEGOTIABLE

- No open inbound ports on the Pi — ever
- No third-party relay services (no Tailscale, Supabase, AWS, Cloudflare)
- No App Store distribution — PWA only
- No in-app payments — all payments via Stripe on atmyboat.com
- No user question text stored anywhere — token counts only
- No GPS coordinates sent to AI — summary stats only
- AtMyBoat.com AI model: claude-haiku-4-5-20251001 — $30/month hard cap
- Gemini 2.5 Flash MAX_TOKENS: 1000 hard cap
- HostPapa is PHP + MySQL only — no Node.js, no persistent processes
- Fix My Pi restores only — never improves or upgrades without user approval
- d3kOS Companion does not compete with ActiveCaptain — no community/marina features

---

## SOURCE DOCUMENTS (for deeper context)

- `Helm-OS/doc/DATABASE_SCHEMA_SUMMARY.md` — central DB schema, all 17 tables
- `Helm-OS/doc/D3KOS_VERSION_ROADMAP_2026.md` — version plan and tier system history
- `Helm-OS/doc/THREE_TIER_AI_ARCHITECTURE_PROPOSAL.md` — cloud AI tier design
- `Helm-OS/doc/SESSION_NEXT_TASK3_DATA_EXPORT_SYNC.md` — export/sync spec
- `Helm-OS/deployment/v0.9.3/ATMYBOAT_BUILD_REFERENCE.md` — AtMyBoat.com platform detail
- `Helm-OS/deployment/v0.9.3/ATMYBOAT_STANDING_INSTRUCTION.md` — platform architecture rules
- `Helm-OS/doc/STRIPE_BILLING_IMPLEMENTATION_GUIDE.md` — subscription billing design
- `Helm-OS/deployment/d3kOS/D3KOS_PLAN.md` — current d3kOS service architecture

---

*d3kOS Mobile App Strategy Brief v2.0.0 — Donald Moskaluk / AtMyBoat.com — 2026-03-14*
*Built from direct Q&A session — 9 questions answered by operator*
