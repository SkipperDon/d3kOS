# d3kOS Version Roadmap 2026
## Comprehensive Development Plan with Three-Tier AI Integration

**Date:** March 1, 2026
**Current Version:** v0.9.2 (Beta - Lake Simcoe Testing)
**Target:** v1.0.0 (Production Ready - Q4 2026)

---

## EXECUTIVE SUMMARY

This roadmap integrates:
- **8-Phase Build Plan** from Master Integration Reference
- **Three-Tier AI Architecture** (Chat, Automation, Agents)
- **Version-based milestones** for clear progress tracking
- **What's been accomplished** vs what remains

**Key Milestone:** v0.9.3 introduces Gemini API conversational AI (first of three AI tiers)

---

## CURRENT STATE - v0.9.2 (March 2026)

### ✅ What's Accomplished:

**Core d3kOS (Layer 1 - Raspberry Pi):**
- ✅ NMEA2000/CAN bus integration (CX5106 gateway)
- ✅ Signal K server (real-time marine data)
- ✅ 10.1" touchscreen dashboard (main helm interface)
- ✅ Engine monitoring + alerts (RPM, oil, temp, fuel, battery)
- ✅ Windy weather integration (radar overlay)
- ✅ GPS/AIS integration (navigation)
- ✅ Boatlog system (maintenance records)
- ✅ Onboarding wizard (20-step setup)
- ✅ 30-day data retention
- ✅ Voice assistant (wake word detection, Tier 2+)
- ✅ Camera system (Reolink 4K IP67, YOLOv8 object detection)
- ✅ Online AI assistant (OpenRouter/GPT - basic)
- ✅ Onboard AI assistant (RAG-only manual search)
- ✅ Data export component (manual trigger)
- ✅ Configuration management
- ✅ Update manager (basic curl-based)

**Existing Microservices (11 services, ports 8080-8101):**
- Port 8080: Dashboard UI
- Port 8081: Signal K server
- Port 8082: Online AI (OpenRouter)
- Port 8083: Onboard AI (RAG manual search)
- Port 8084: Navigation
- Port 8085: Camera (Marine Vision Phase 1)
- Port 8086: Voice control
- Port 8087: Boatlog
- Port 8088: Engine monitoring
- Port 8089: Data export
- Port 8090: Self-heal (verify existence)
- Port 8099: Internal API gateway
- Port 8100: Configuration
- Port 8101: Update manager

**Tier System:**
- ✅ Tier 0: Free (local dashboard, 30-day retention)
- ✅ Tier 1: Free (mobile app access planned v0.9.4)
- ✅ Tier 2: $9.99/mo (voice, camera, remote access - local only currently)
- ✅ Tier 3: $99.99/yr (fleet management - planned Phase 3)

**Status:** Beta testing on Lake Simcoe, Ontario. Core functionality operational. No cloud platform yet.

---

## VERSION ROADMAP

### v0.9.2 - Metric/Imperial Conversion System
**Target:** March 2026 (3 weeks)
**Focus:** International distribution - measurement system support
**Priority:** HIGH - "American boaters vs the world"
**Status:** ✅ NEXT - Ready to implement

**What's New:**
1. **Units Conversion System**
   - JavaScript utility library (`/var/www/html/js/units.js`)
   - Client-side conversion (temperature, pressure, speed, distance, depth, fuel, length, weight, displacement)
   - Real-time conversion (no page reload)

2. **Preferences API Extension** (Port 8107 - existing service)
   - Store measurement_system preference ("imperial" or "metric")
   - GET /preferences - Retrieve user preferences
   - POST /preferences - Update preferences
   - Persistent storage in `/opt/d3kos/config/user-preferences.json`

3. **Auto-Default Logic** (Onboarding Step 15 - Boat Origin)
   - USA/Canada → Imperial (default)
   - Europe/Asia/Oceania/Africa/South America → Metric (default)
   - User can override anytime in Settings

4. **UI Updates** (All pages support unit conversion)
   - Dashboard: Engine metrics displayed in user's preferred units
   - Onboarding: Form inputs show correct unit dropdowns
   - Navigation: Speed, altitude in preferred units
   - Weather: Temperature, wind in preferred units
   - Boatlog: Display only (stored data unchanged)
   - Voice Assistant: Responses use preferred units

5. **Settings Toggle**
   - Settings → Measurement System (toggle switch)
   - Changes take effect immediately
   - Live update across all pages

**Conversions Supported:**
- Temperature: °F ↔ °C
- Pressure: PSI ↔ bar
- Speed: Knots+MPH ↔ Knots+km/h
- Distance: Nautical miles ↔ Kilometers
- Depth: Feet ↔ Meters
- Fuel: Gallons ↔ Liters
- Length: Feet ↔ Meters
- Weight: Pounds ↔ Kilograms
- Displacement: Cubic inches ↔ Liters

**Implementation Time:** 3 weeks (120 hours)
- Week 1: Units.js library, preferences API, Settings UI
- Week 2: Dashboard, onboarding, navigation, weather updates
- Week 3: Voice assistant integration, testing

**Deliverable:** d3kOS v0.9.2 with full metric/imperial support

**Documentation:** `METRIC_IMPERIAL_IMPLEMENTATION_PLAN.md` (42KB complete plan)

---

### v0.9.3 - Multi-Camera System (4 Cameras)
**Target:** April 2026 (8-9 weeks after v0.9.2)
**Focus:** Multiple camera support with Forward Watch integration
**Priority:** HIGH - Safety and security
**Status:** ✅ APPROVED - 4 cameras confirmed

**What's New:**
1. **Camera Registry System**
   - JSON-based camera configuration (`/opt/d3kos/config/cameras.json`)
   - Auto-discovery on 10.42.0.0/24 subnet
   - DHCP reservations (10.42.0.100-103)
   - Per-camera settings (RTSP URLs, purpose, detection mode)

2. **Four Camera Layout**
   - **Bow Camera (10.42.0.100)** - Forward Watch obstacle avoidance with YOLOv8 detection
   - **Stern Camera (10.42.0.101)** - Docking assistance, wake monitoring
   - **Interior Camera (10.42.0.102)** - Security when boat unattended
   - **Port/Starboard Camera (10.42.0.103)** - Side coverage

3. **Hybrid UI Implementation**
   - **Single View Page** (`/marine-vision.html`) - Full-screen 1080p @ 25 FPS, dropdown camera selector
   - **Grid View Page** (`/marine-vision-grid.html`) - 2×2 grid, 720p @ 1 FPS all cameras, click to enlarge
   - Forward Watch detection overlay (bow camera only when active)

4. **Resource Optimization**
   - Sub-streams (720p) for grid view - reduces bandwidth/CPU
   - Main stream (1080p) for single view - full quality
   - Priority queue for AI detection (bow camera always first)
   - Motion-triggered recording (7-day retention, 28 GB storage)

5. **Camera Management API** (Port 8084 expanded)
   - `/camera/list` - Get all registered cameras
   - `/camera/status/{id}` - Connection status per camera
   - `/camera/switch/{id}` - Switch active camera in single view
   - `/camera/grid` - Get all frames for grid view

6. **Forward Watch Integration**
   - YOLOv8 marine object detection (boats, kayaks, buoys, logs, debris, docks, ice)
   - Distance estimation (monocular depth)
   - Real-time alerts (visual + audio)
   - Object tracking and logging
   - Only processes bow camera frames (resource efficient)

**Resource Requirements:**
- Memory: 970 MB total (12% of 8GB RAM)
- CPU: 25-35% average
- Bandwidth: 8-12 Mbps for grid view, 4 Mbps single view
- Storage: 28 GB for 7-day retention (motion-triggered)

**Hardware Cost:** $800-1,200 (3 additional Reolink RLC-810A cameras)

**Implementation Time:** 8-9 weeks
- Week 1: Camera registry system and auto-discovery
- Week 2-3: Multi-camera backend API
- Week 4-5: Single View + Grid View UI
- Week 6-7: Forward Watch integration (bow camera)
- Week 8: Testing and optimization
- Week 9: Documentation and deployment

**Deliverable:** d3kOS v0.9.3 with 4-camera support and Forward Watch obstacle avoidance

**Documentation:** `MULTI_CAMERA_IMPLEMENTATION_PLAN.md` (50KB complete specification)

---

### v0.9.4 - Gemini API Integration (TIER 1 AI - CHAT LAYER)
**Target:** April 2026 (5-7 weeks)
**Focus:** Conversational AI with Google Gemini API

**What's New:**
1. **Gemini API Proxy Service** (Port 8099 - new)
   - Flask API for Gemini API calls
   - Conversation history management
   - Tier-based access control (Tier 2+ only)
   - API key validation and storage

2. **Onboarding Wizard Integration**
   - **Step 17:** AI Assistant Setup (optional, skippable)
   - **Step 17.1:** Get API Key Instructions (QR code for mobile)
   - **Step 17.2:** Enter API Key
   - **Step 17.3:** Test Connection (auto-verify)
   - Tier detection (Tier 0/1 auto-skip, Tier 2+ shows setup)

3. **Settings Integration**
   - Settings → AI Assistant page updates
   - API key management UI
   - Quota display (1,000 requests/day free tier)
   - Troubleshooting guide

4. **Voice Assistant Integration**
   - Replace OpenRouter backend with Gemini
   - Maintain existing wake word system ("helm")
   - Faster response times (6-8s vs 10-15s)
   - Natural conversational responses

**Technical Details:**
- User brings own API key (100% FREE approach)
- Google Gemini API free tier: 1,000 requests/day
- No credit card required
- Typical usage: 10-20 queries/day = $0.14/month
- Response time: 6-8 seconds (vs 10-15s with OpenRouter)

**User Experience:**
- Before: "The engine temperature is 185 degrees." (robotic)
- After: "The engine temperature is currently 185 degrees Fahrenheit, which is right in the normal range of 180 to 210 degrees. Everything looks good!"

**Implementation Time:** 5-7 weeks
- Week 1-2: Backend Gemini proxy service
- Week 3-4: Onboarding wizard integration (Steps 17.x)
- Week 5: Settings UI updates
- Week 6-7: Testing and beta rollout

**Deliverable:** d3kOS v0.9.4 with conversational AI

---

### v0.9.5 - Mobile Apps (iOS/Android)
**Target:** July 2026 (8-10 weeks after v0.9.4)
**Focus:** Tier 1 activation - Mobile app access

**What's New:**
1. **React Native Mobile App** (iOS and Android)
   - Login/authentication
   - My Boats list
   - Live engine dashboard (remote)
   - Camera view (remote)
   - Push notifications (engine alarms)
   - Settings sync

2. **AtMyBoat.com Cloud Foundation** (Phase 1 - Mesh)
   - Provision DigitalOcean VPS
   - Headscale (self-hosted Tailscale coordination)
   - Mosquitto MQTT broker (TLS)
   - PostgreSQL database (device registry)
   - REST API (/devices, /devices/:id/data)
   - Auth0 authentication (user accounts, JWT)
   - Basic web dashboard (My Boats, live data)

3. **Pi-to-Cloud Integration**
   - Tailscale agent on Pi (auto-join mesh on boot)
   - MQTT publisher service (Port 8102)
   - Device registration on first boot
   - Pi hardware watchdog (/dev/watchdog)

**Tier Impact:**
- Tier 1 activated: Mobile app + web dashboard + unlimited data retention
- Tier 2: Remote camera access + voice assistant + push notifications
- Tier 3: Fleet management (planned v0.10.0)

**Implementation Time:** 8-10 weeks
- Week 1-3: AtMyBoat.com VPS setup (Headscale, MQTT, PostgreSQL)
- Week 4-6: REST API + web dashboard
- Week 7-8: React Native mobile app
- Week 9-10: Pi integration (Tailscale, MQTT publisher)
- Testing: Beta group (10-20 users)

**Deliverable:** d3kOS v0.9.5 + AtMyBoat.com cloud platform

---

### v0.9.6 - Remote Access & Camera Streaming
**Target:** September 2026 (6-8 weeks after v0.9.5)
**Focus:** Tier 2 activation - Full remote access

**What's New:**
1. **Remote Dashboard Enhancements**
   - WebSocket real-time data push (Socket.io)
   - Live engine gauges in browser
   - Camera stream relay (VLC RTSP → HLS)
   - Camera visible remotely
   - Data updates without page refresh

2. **Device Management**
   - Invite crew members
   - Set permissions (view/control)
   - Crew access control

3. **Stripe Billing Integration**
   - Tier 2 subscription ($9.99/mo)
   - Tier 3 subscription ($99.99/yr)
   - Payment processing
   - Feature gating

4. **Boat Specifications Storage**
   - Engine make/model/year
   - Hull type/length
   - Propulsion details
   - Used for benchmark matching (future)

**Implementation Time:** 6-8 weeks
- Week 1-2: WebSocket server + real-time push
- Week 3-4: Camera relay (RTSP → HLS)
- Week 5: Device management (crew invitations)
- Week 6: Stripe integration
- Week 7-8: Testing and Tier 2 rollout

**Deliverable:** d3kOS v0.9.6 with full Tier 2 remote access

---

### v0.10.0 - Predictive Maintenance (TIER 2 AI - AUTOMATION LAYER)
**Target:** October 2026 (16 weeks after v0.9.5)
**Focus:** AI-powered failure prediction and anomaly detection

**What's New:**
1. **Predictive Maintenance Service** (Port 8106 - new)
   - 30-day baseline data collection
   - Time-series data storage (InfluxDB or SQLite)
   - Normal operating range calculation
   - Anomaly detection (statistical)
   - Trend analysis (7-day, 30-day slopes)

2. **ML Models (5 models):**
   - **Overheating Predictor:** LSTM autoencoder, 90% accuracy target
   - **Oil Pressure Failure:** Time-series forecasting
   - **Battery Failure:** Voltage trend analysis
   - **SD Card Failure:** I/O error pattern detection
   - **GPS Failure:** Satellite loss prediction

3. **Alert System Integration**
   - Boatlog integration (automated entries)
   - Voice alerts (Tier 2+)
   - Mobile push notifications (Tier 2+)
   - Dashboard widget (predictive alerts)

4. **Additional Automation:**
   - Weather monitoring (storm warnings)
   - Fuel optimization (RPM efficiency analysis)
   - Maintenance scheduling (engine hours tracking)
   - Geofence alerts (Tier 3)

**Technical Approach:**
- Phase 1 (Weeks 1-4): Data collection baseline
- Phase 2 (Weeks 5-7): Statistical anomaly detection
- Phase 3 (Weeks 8-11): ML model training (LSTM, forecasting)
- Phase 4 (Weeks 12-13): Alert system integration
- Phase 5 (Weeks 14-16): Additional automation features

**User Experience:**
- **Before:** Engine overheats → alarm sounds → damage already happening
- **After:** 24 hours before failure: "Coolant temperature trending up 0.5°F/hour. Overheating predicted in 24 hours. Check coolant level."

**Implementation Time:** 16 weeks (parallel with v0.10.1 work)

**Deliverable:** d3kOS v0.10.0 with predictive maintenance

---

### v0.10.1 - Fleet Management (Tier 3)
**Target:** November 2026 (8 weeks, parallel with v0.10.0)
**Focus:** Fleet coordination and analytics

**What's New:**
1. **Fleet Management System**
   - Fleet creation (charter, fishing, marina types)
   - Fleet invitation system (installation ID based)
   - Permission levels (owner, manager, member, view)
   - Fleet data scope controls (per boat)

2. **Fleet Map**
   - Live vessel positions (Leaflet.js/Mapbox)
   - All fleet boats visible on map
   - Privacy controls (opt-in, 500m randomization)

3. **Fleet Analytics**
   - Engine hours aggregation
   - Fuel consumption tracking
   - Alert history (30 days)
   - Fleet-wide reporting

4. **Tier 3 Activation**
   - Annual subscription ($99.99/yr)
   - Fleet features gated
   - API access for third-party integrations

**Implementation Time:** 8 weeks (parallel with v0.10.0)

**Deliverable:** d3kOS v0.10.1 with fleet management

---

### v0.11.0 - Remote Diagnostic Console
**Target:** January 2027 (8-10 weeks after v0.10.x)
**Focus:** Professional support and remote diagnostics

**What's New:**
1. **Support Ticket System**
   - User submits ticket (problem description)
   - Admin receives notification (< 60 seconds)
   - Ticket tracking and status updates

2. **Diagnostic Access Flow**
   - Per-session approval (user consent)
   - Time-limited access (2 hours max)
   - Auto-expiry after session

3. **Diagnostic Agent on Pi** (Port 8103 - new)
   - Controlled log collection
   - Bundle creation (< 60 seconds)
   - Upload to AtMyBoat.com

4. **AI Diagnosis Engine**
   - Claude API integration (admin console)
   - Log analysis and diagnosis
   - Follow-up questions capability
   - Fix recommendations

5. **Fix Delivery System**
   - Admin creates fix (via AI or manual)
   - User approval notification (one-tap)
   - Fix execution via Action Layer (whitelisted commands)
   - Real-time output streaming

6. **Knowledge Base**
   - Resolved cases logged
   - Pattern detection (3+ matches)
   - Automatic recurrence tracking

7. **Admin Console UI**
   - admin.atmyboat.com
   - 3-panel layout (ticket, data, diagnosis)
   - Real-time collaboration

**Implementation Time:** 8-10 weeks
- Week 1-2: Ticket system + consent flow
- Week 3-4: Diagnostic agent (log collection)
- Week 5-6: Claude API + AI diagnosis
- Week 7: Fix delivery + user approval
- Week 8: Knowledge base
- Week 9-10: Admin console UI

**Deliverable:** d3kOS v0.11.0 with remote diagnostic console

---

### v0.12.0 - Autonomous Agents (TIER 3 AI - AGENT LAYER)
**Target:** March 2027 (15 weeks after v0.11.0)
**Focus:** Self-healing and autonomous system management

**What's New:**
1. **Agent Framework** (Weeks 1-3)
   - Base agent class
   - Agent scheduler
   - Agent communication bus
   - Agent management API

2. **Update Agent** (Weeks 4-5)
   - GitHub integration (check for d3kOS updates)
   - Backup/restore logic
   - Risk analysis
   - Auto-rollback on failure
   - Runs: Daily 3:00 AM

3. **Performance Agent** (Weeks 6-7)
   - CPU/memory/disk monitoring
   - Auto-remediation actions:
     - Clear cache when disk > 90%
     - Restart crashed services
     - Thermal throttle management
   - Alert generation
   - Runs: Every 15 minutes

4. **Storage Agent** (Weeks 8-9)
   - Cleanup automation (old logs, temp files)
   - Predictive warnings (7 days before full)
   - Storage optimization
   - Runs: Daily 4:00 AM

5. **Health Check Agent** (Weeks 10-11)
   - Daily health reports (all systems)
   - Weekly deep scans (database integrity, file system)
   - Health scoring system (0-100)
   - Trend analysis
   - Runs: Daily 5:00 AM, deep scan Sunday 2:00 AM

6. **Backup Agent** (Weeks 12-13)
   - Incremental backups (daily)
   - Full system images (weekly)
   - Cloud sync (Tier 3)
   - Restoration testing
   - Runs: Daily 6:00 AM

**Agent Dashboard:**
- Settings → Autonomous Agents page
- Agent status (enabled/disabled)
- Last run timestamp
- Success/failure history
- Manual trigger buttons

**Safety Guarantees:**
- All actions whitelisted (no arbitrary commands)
- User notification before risky actions
- Audit trail (append-only log)
- Rollback capability
- Manual override always available

**Implementation Time:** 15 weeks
- Weeks 1-3: Framework
- Weeks 4-13: Individual agents (2 weeks each)
- Weeks 14-15: Testing and integration

**Deliverable:** d3kOS v0.12.0 with autonomous agents

---

### v0.12.1 - AI Diagnostic Assistant On Pi
**Target:** April 2027 (8 weeks after v0.12.0)
**Focus:** Controlled autonomy and self-healing

**What's New:**
1. **Immutable Base Partition**
   - `/opt/d3kos/base` read-only at runtime
   - Application code protected
   - Service definitions protected
   - Signing keys protected

2. **AI Action Layer** (Port 8104 - new)
   - Named action functions only
   - Whitelist validation
   - Snapshot before execution
   - Health check after execution
   - Auto-rollback on failure

3. **Action Whitelist**
   - Defined in base partition
   - Cannot be modified at runtime
   - Example actions:
     - `restart_service(name)`
     - `clear_cache()`
     - `rotate_logs()`
     - `update_config(key, value)`
   - Non-whitelisted commands blocked

4. **Snapshot System**
   - Pre-action config backup
   - Stored in `/opt/d3kos/snapshots/`
   - Automatic restoration on failure
   - Retention: 7 days

5. **Health Check Automation**
   - Post-action verification
   - Service status checks
   - Disk space checks
   - Network connectivity checks
   - Rollback triggers when checks fail

6. **Audit Ledger**
   - Append-only action log
   - Records: what AI observed, decided, executed, outcome
   - Synced to AtMyBoat.com
   - Immutable (cannot be edited/deleted)

7. **Prompt Injection Defenses**
   - Input sanitization
   - Injection pattern detection
   - Flagged attempts logged
   - Action whitelist as primary defense

**Implementation Time:** 8 weeks
- Week 1-2: Immutable base partition setup
- Week 3-4: AI Action Layer + whitelist
- Week 5-6: Snapshot + health check system
- Week 7: Audit ledger
- Week 8: Prompt injection defenses + testing

**Deliverable:** d3kOS v0.12.1 with controlled AI autonomy

---

### v0.13.0 - Failure Intelligence & Recovery
**Target:** June 2027 (8 weeks after v0.12.1)
**Focus:** Community learning and recovery system

**What's New:**
1. **Failure Reporter Service** (Port 8106 - new)
   - Internal API for all services
   - Failure event capture (5KB max per record)
   - Local SQLite storage
   - Anonymization (hash installation ID)
   - Background sync to AtMyBoat.com

2. **Failure Record Schema (4-question format):**
   - What was the system trying to do?
   - What went wrong?
   - What was the immediate consequence?
   - What fixed it?

3. **Failure Database at AtMyBoat.com**
   - Receives all anonymized records
   - Pattern analysis (aggregation)
   - Recurrence tracking (24h, 7d)
   - Top failure patterns dashboard

4. **Personalized Config Packages**
   - Stored per installation at AtMyBoat.com
   - Engine specs, settings, boatlog data
   - Updated on every mesh sync
   - Used for recovery

5. **Recovery Mode Boot Sequence**
   - Fresh SD card detection
   - Auto-connect to mesh
   - Download personalized config
   - Restore settings + boatlog
   - Resume normal operation

6. **Export Integration**
   - User can export their failure history
   - Part of data export component (Port 8089)

**Implementation Time:** 8 weeks
- Week 1-2: Failure reporter service
- Week 3-4: AtMyBoat.com failure database
- Week 5-6: Personalized config system
- Week 7: Recovery boot sequence
- Week 8: Export integration + testing

**Deliverable:** d3kOS v0.13.0 with failure intelligence

---

### v0.14.0 - Community Features
**Target:** August 2027 (8 weeks after v0.13.0)
**Focus:** Community network and anonymous sharing

**What's New:**
1. **Anonymous Engine Benchmark Service**
   - Minimum 10-boat pool (privacy protection)
   - Aggregated performance data
   - Compare your engine to similar boats
   - Tier 2+ feature

2. **Anonymizer Service**
   - Strips all identifying data
   - Position randomization (500m radius)
   - Installation ID hashing
   - Community data isolated

3. **Community Boat Map**
   - Opt-in only (default: OFF)
   - Anonymous markers on map
   - Position randomized 500m
   - No identifying information shown

4. **Hazard and POI Marker System**
   - User submits hazards (logs, shallow water, debris)
   - Vote system (upvote/downvote)
   - Auto-expiry (30 days)
   - Moderation tools

5. **Knowledge Base to Pattern Sync**
   - Resolved diagnostic cases → onboard patterns
   - Pattern library updated on mesh sync
   - Community learning

**Privacy Rules Enforced:**
- All data private by default (opt-in required)
- Benchmark pool minimum 10 boats (no partial data)
- Position randomized 500m (never exact location)
- Hashed installation IDs (actual ID never shared)

**Implementation Time:** 8 weeks
- Week 1-2: Benchmark service
- Week 3-4: Anonymizer service
- Week 5-6: Community map
- Week 7: Hazard/POI system
- Week 8: KB-to-pattern sync

**Deliverable:** d3kOS v0.14.0 with community features

---

### v0.15.0 - Multi-Language Support (Internationalization)
**Target:** September 2027 (6-8 weeks after v0.14.0)
**Focus:** International distribution readiness
**Priority:** Required for v1.0 production release
**Status:** Low priority but must complete before v1.0

**What's New:**
1. **Language Selection System**
   - 8 languages supported: English, French, Spanish, German, Italian, Dutch, Swedish, Norwegian
   - Language selector in Settings (dropdown)
   - Auto-default based on boat origin (onboarding Step 15)
   - Real-time language switching (no page reload)
   - JSON-based translation files

2. **UI Internationalization (i18n)**
   - All pages support multi-language
   - JavaScript i18n utility library (`/var/www/html/js/i18n.js`)
   - HTML translation attributes (`data-i18n`, `data-i18n-placeholder`)
   - Fallback to English if translation missing
   - 500+ translated strings per language

3. **Voice Assistant Multi-Language**
   - 8 Piper TTS voice models installed (345 MB total)
   - Voice responses in user's selected language
   - Wake word "helm" unchanged (international maritime term)
   - Translated response templates for all queries

4. **Translation Architecture**
   - Translation files: `/opt/d3kos/config/i18n/{code}.json`
   - Preferences API extended for language preference
   - localStorage caching for performance
   - Professional translation service (7 languages)

5. **Auto-Default Logic**
   - United States → English
   - Canada → English (French available)
   - France → French
   - Spain → Spanish
   - Germany → German
   - Italy → Italian
   - Netherlands → Dutch
   - Sweden → Swedish
   - Norway → Norwegian
   - Other → English (fallback)

**Market Expansion:**
- Current: 400M English speakers
- After v0.15.0: 1.26B speakers across 8 languages (+215% addressable market)
- Enables European distribution
- Enables Latin American distribution (Spanish)
- Enables Canadian French market (Quebec)

**Implementation Time:** 6-8 weeks
- Week 1-2: i18n system foundation, preferences API extension
- Week 3-4: UI translation (all pages updated with data-i18n attributes)
- Week 5-6: Professional translation service (external, 7 languages)
- Week 7: Voice assistant integration (Piper TTS models)
- Week 8: Native speaker testing and QA

**Development Cost:** $7,750-10,500
- Internal development: $6,000 (80 hours)
- Professional translation: $1,750 (one-time)

**Storage:** 10 MB translation files + 345 MB voice models = 355 MB total

**Deliverable:** d3kOS v0.15.0 with 8-language support, ready for international v1.0 launch

**Documentation:** `LANGUAGE_SELECTION_SPECIFICATION.md` (26KB - complete specification)

---

### v0.16.0 - Security Audit & Penetration Testing
**Target:** November 2027 (4 weeks after v0.15.0)
**Focus:** Production security readiness
**Priority:** CRITICAL - Required before v1.0 launch
**Status:** Pre-v1.0 requirement

**What's New:**
1. **Comprehensive Security Audit**
   - Full codebase security review
   - Dependency vulnerability scan (npm audit, pip-audit)
   - OWASP Top 10 compliance check
   - SQL injection testing (all database queries)
   - XSS/CSRF vulnerability testing (all web endpoints)
   - Authentication/authorization review (JWT, session management)

2. **Penetration Testing**
   - External penetration test (network-level attacks)
   - Internal penetration test (privilege escalation)
   - API endpoint fuzzing (all 20+ services)
   - WireGuard VPN security review
   - MQTT broker security audit (TLS, authentication)
   - Signal K server security review

3. **Privacy Compliance**
   - GDPR compliance verification (EU users)
   - CCPA compliance verification (California users)
   - Data retention policy implementation
   - User data export functionality (GDPR Article 20)
   - Data deletion functionality (GDPR Article 17)
   - Privacy policy review and update

4. **Infrastructure Security**
   - Pi hardening review (SSH, firewall, fail2ban)
   - Certificate management audit (SSL/TLS)
   - Secrets management review (API keys, passwords)
   - Backup security (encrypted backups)
   - Update system security (signature verification)
   - Rate limiting implementation (DDoS protection)

5. **Third-Party Service Security**
   - Stripe webhook signature verification
   - Apple IAP receipt validation
   - Google Play purchase verification
   - Gemini API key protection
   - OpenRouter API security
   - Headscale mesh security

6. **Documentation**
   - Security best practices guide
   - Incident response plan
   - Vulnerability disclosure policy
   - Security update process
   - User security recommendations

7. **Security Testing Tools**
   - OWASP ZAP automated scan
   - Burp Suite professional testing
   - SQLMap injection testing
   - Nmap network scanning
   - Metasploit framework testing (authorized)

**Critical Issues to Address:**
- [ ] Ensure all API endpoints require authentication
- [ ] Verify all database queries use parameterized statements
- [ ] Check all file uploads for malicious content
- [ ] Validate all user inputs (XSS prevention)
- [ ] Implement rate limiting on all public endpoints
- [ ] Secure all MQTT topics with ACLs
- [ ] Verify all passwords hashed with bcrypt/scrypt
- [ ] Check for hardcoded secrets in code
- [ ] Ensure all external APIs use HTTPS
- [ ] Verify all sessions expire properly
- [ ] Test for session hijacking vulnerabilities
- [ ] Check for command injection vulnerabilities
- [ ] Verify file permissions on sensitive files
- [ ] Test for directory traversal attacks
- [ ] Verify all webhooks validate signatures

**Compliance Requirements:**
- OWASP Application Security Verification Standard (ASVS) Level 2
- CIS Raspberry Pi Benchmark
- NIST Cybersecurity Framework
- PCI DSS (if storing payment info - should not)
- ISO 27001 controls (relevant sections)

**Implementation Time:** 4 weeks
- Week 1: Automated security scanning, dependency audit
- Week 2: Manual code review, OWASP Top 10 testing
- Week 3: Penetration testing (external firm recommended)
- Week 4: Fix critical/high vulnerabilities, retest

**External Service (Recommended):**
- Professional penetration testing firm
- Cost: $5,000-15,000 (one-time)
- Deliverable: Security audit report with findings
- Certification: Penetration test certificate

**Internal Effort:** 40-60 hours
- Security review: 16 hours
- Vulnerability fixes: 24-32 hours
- Documentation: 8 hours
- Retesting: 8 hours

**Deliverable:** d3kOS v0.16.0 - Security certified, production ready

**Success Criteria:**
- Zero critical vulnerabilities
- Zero high vulnerabilities
- Medium/low vulnerabilities documented with mitigation plans
- Penetration test certificate obtained
- GDPR/CCPA compliant
- Security documentation complete

---

### v1.0.0 - Incremental Update System (PRODUCTION READY)
**Target:** December 2027 (4 weeks after v0.16.0)
**Focus:** Professional OTA update system

**What's New:**
1. **Enhanced d3kos-update Service** (Port 8101 - extend existing)
   - Review existing capabilities first
   - curl-based update check (every 15 minutes)
   - Package download with resume support
   - Ed25519 signature verification
   - Checksum verification

2. **Pre-Update Snapshot System**
   - Snapshot taken before every update
   - Runtime and base partition backup
   - Quick restoration on failure

3. **File Application Logic**
   - Only changed files applied (efficient)
   - Base partition remount sequence (read-only → apply → read-only)
   - Runtime partition hot-reload

4. **Post-Update Health Check**
   - All services verify running
   - Network connectivity check
   - Database integrity check
   - Auto-rollback on failure (< 3 minutes)

5. **Outcome Reporting**
   - Pi reports success/failure to AtMyBoat.com
   - Per-boat status visible in admin console
   - Results shown within 5 minutes

6. **Update Package Storage** (AtMyBoat.com)
   - Signed packages stored securely
   - Time-limited download URLs
   - API endpoints: /v1/check, /v1/download, /v1/report

7. **build-update-package.sh** (Build Server)
   - Build from git diff
   - Sign with private key (Ed25519)
   - Upload to AtMyBoat.com

8. **Admin Console - Update Manager**
   - Package upload interface
   - Target boat selection (single, group, all)
   - Push campaign creator
   - Live status dashboard (per boat)
   - Auto-pause when rollback rate > 5%

**Implementation Time:** 8 weeks
- Week 1-2: Review existing update service, add signature verification
- Week 3-4: Snapshot + health check + auto-rollback
- Week 5-6: AtMyBoat.com package storage + API
- Week 7: build-update-package.sh script
- Week 8: Admin console UI + campaign dashboard

**Deliverable:** d3kOS v1.0.0 - PRODUCTION READY

---

## TIMELINE SUMMARY

| Version | Target Date | Focus | Duration | Cumulative Time |
|---------|-------------|-------|----------|-----------------|
| **v0.9.2** | **March 2026** | **Metric/Imperial** | **3 weeks** | **3 weeks** |
| **v0.9.3** | **April 2026** | **4-Camera System** | **8-9 weeks** | **12 weeks** |
| v0.9.4 | June 2026 | Gemini API (Chat AI) | 5-7 weeks | 19 weeks |
| v0.9.5 | July 2026 | Mobile Apps + Cloud | 8-10 weeks | 29 weeks |
| v0.9.6 | September 2026 | Remote Access (Tier 2) | 6-8 weeks | 37 weeks |
| v0.10.0 | November 2026 | Predictive Maintenance | 16 weeks | 53 weeks |
| v0.10.1 | December 2026 | Fleet Management | 8 weeks (parallel) | 45 weeks |
| v0.11.0 | March 2027 | Diagnostic Console | 8-10 weeks | 63 weeks |
| v0.12.0 | May 2027 | Autonomous Agents | 15 weeks | 78 weeks |
| v0.12.1 | July 2027 | AI Action Layer | 8 weeks | 86 weeks |
| v0.13.0 | September 2027 | Failure Intelligence | 8 weeks | 94 weeks |
| v0.14.0 | November 2027 | Community Features | 8 weeks | 102 weeks |
| **v0.15.0** | **December 2027** | **Multi-Language (i18n)** | **6-8 weeks** | **110 weeks** |
| **v0.16.0** | **January 2028** | **Security Audit** | **4 weeks** | **114 weeks** |
| **v1.0.0** | **February 2028** | **Incremental Updates** | 8 weeks | **122 weeks** |

**Total Development Time:** 122 weeks (~28 months from March 2026)
**Production Launch:** Q1 2028 (February 2028)
**International Ready:** v0.15.0 (December 2027) - 8 languages supported
**Security Certified:** v0.16.0 (January 2028) - Production security audit complete

---

## THREE-TIER AI INTEGRATION SUMMARY

### TIER 1: CHAT LAYER (v0.9.3)
**What:** Conversational AI with Google Gemini API
**When:** April 2026 (5-7 weeks)
**Status:** ✅ Design complete, ready to implement
**User Experience:** Natural language responses vs robotic answers
**Cost:** FREE (user brings own API key, 1,000 req/day free tier)

### TIER 2: AUTOMATION LAYER (v0.10.0)
**What:** Predictive maintenance and failure prediction
**When:** October 2026 (16 weeks)
**Status:** 📋 Specification complete
**User Experience:** 24-hour advance warning of failures
**Features:**
- 5 ML models (overheating, oil, battery, SD card, GPS)
- Statistical anomaly detection
- Trend analysis
- Automated alerts

### TIER 3: AGENT LAYER (v0.12.0)
**What:** Autonomous system management and self-healing
**When:** March 2027 (15 weeks)
**Status:** 📋 Specification complete
**User Experience:** System maintains itself autonomously
**Features:**
- 6 autonomous agents (update, performance, storage, health, backup, fleet)
- Whitelisted actions only
- Automatic rollback
- Audit trail
- Manual override always available

---

## DEPENDENCY MAP

```
v0.9.2 (Current)
  ↓
v0.9.3 (Gemini API) ← TIER 1 AI - CHAT
  ↓
v0.9.4 (Mobile Apps + Cloud) ← Tier 1 activated
  ↓
v0.9.5 (Remote Access) ← Tier 2 activated
  ↓
v0.10.0 (Predictive Maintenance) ← TIER 2 AI - AUTOMATION
  ↓ (parallel)
v0.10.1 (Fleet Management) ← Tier 3 activated
  ↓
v0.11.0 (Diagnostic Console)
  ↓
v0.12.0 (Autonomous Agents) ← TIER 3 AI - AGENTS
  ↓
v0.12.1 (AI Action Layer) ← Controlled autonomy
  ↓
v0.13.0 (Failure Intelligence)
  ↓
v0.14.0 (Community Features)
  ↓
v1.0.0 (Incremental Updates) ← PRODUCTION READY
```

---

## COST & REVENUE PROJECTIONS

### Development Costs:
- **Gemini API (v0.9.3):** 5-7 weeks × $50-150/hr = $10,000 - $21,000
- **Mobile Apps (v0.9.4):** 8-10 weeks × $50-150/hr = $16,000 - $30,000
- **Predictive Maintenance (v0.10.0):** 16 weeks × $50-150/hr = $32,000 - $48,000
- **Autonomous Agents (v0.12.0):** 15 weeks × $50-150/hr = $30,000 - $45,000
- **Other versions:** ~40 weeks × $50-150/hr = $80,000 - $120,000
- **Total Development:** $168,000 - $264,000

### Operational Costs (Annual):
- **AtMyBoat.com VPS:** $240 - $1,200/yr
- **Tailscale mesh:** $0 (self-hosted Headscale)
- **Auth0:** $0 - $2,400/yr (free tier or paid)
- **PostgreSQL:** Included in VPS
- **Firebase push:** $0 - $600/yr
- **Stripe fees:** 2.9% + $0.30 per transaction
- **Total Operational:** $240 - $4,200/yr (before Stripe fees)

### Revenue Projections (Conservative):
**Year 1 (2027 - v1.0.0 launch):**
- 100 Tier 2 users @ $9.99/mo = $11,988/yr
- 20 Tier 3 users @ $99.99/yr = $1,999.80/yr
- **Gross Revenue:** $13,987.80/yr
- **Stripe Fees:** ~$460/yr
- **Net Revenue:** $13,527.80/yr
- **Break-even:** Need 740 users to break even on dev costs

**Year 2 (2028 - growth phase):**
- 1,000 Tier 2 users @ $9.99/mo = $119,880/yr
- 100 Tier 3 users @ $99.99/yr = $9,999/yr
- **Gross Revenue:** $129,879/yr
- **Stripe Fees:** ~$4,300/yr
- **Net Revenue:** $125,579/yr
- **Cumulative:** Break-even achieved (assuming ~$180K dev costs)

**Year 3 (2029 - mature phase):**
- 5,000 Tier 2 users @ $9.99/mo = $599,400/yr
- 500 Tier 3 users @ $99.99/yr = $49,995/yr
- **Gross Revenue:** $649,395/yr
- **Stripe Fees:** ~$21,500/yr
- **Net Revenue:** $627,895/yr

---

## SUCCESS METRICS

### Chat Layer (v0.9.3):
- ✅ Voice response time: < 8 seconds
- ✅ Voice recognition accuracy: > 90%
- ✅ User satisfaction: > 4.5/5 stars
- ✅ Free tier coverage: > 90% of users

### Automation Layer (v0.10.0):
- ✅ Failure prediction accuracy: > 80%
- ✅ False positive rate: < 10%
- ✅ Average warning time: > 24 hours
- ✅ Downtime reduction: > 30%

### Agent Layer (v0.12.0):
- ✅ Auto-update success rate: > 99%
- ✅ System uptime: > 99.5%
- ✅ Storage full events: 0
- ✅ Support tickets: -50% reduction

### Fleet Management (v0.10.1):
- ✅ Fleet adoption rate: > 20% of Tier 3 users
- ✅ Multi-boat owners: > 40% create fleets
- ✅ Average fleet size: 5-10 boats

### Community Features (v0.14.0):
- ✅ Benchmark pool: > 100 boats per engine type
- ✅ Hazard marker submissions: > 50/month
- ✅ Community map opt-in: > 30% of Tier 2+ users

---

## COMPETITIVE ADVANTAGES

| Feature | d3kOS | Garmin | Raymarine | Simrad |
|---------|-------|--------|-----------|--------|
| **Conversational AI** | ✅ v0.9.3 | ❌ | ❌ | ❌ |
| **Predictive Maintenance** | ✅ v0.10.0 | ❌ | ❌ | ❌ |
| **Autonomous Agents** | ✅ v0.12.0 | ❌ | ❌ | ❌ |
| **Fleet Management** | ✅ v0.10.1 | Limited | Limited | Limited |
| **Open Source** | ✅ GPL v3 | ❌ | ❌ | ❌ |
| **Price** | $0-$9.99/mo | $1,500-5,000 | $1,200-4,000 | $1,500-6,000 |

**d3kOS = 10-100× cheaper with MORE features!**

---

## RISK MITIGATION

### Technical Risks:
1. **Gemini API Availability:** User brings own key, no dependency on AtMyBoat.com quota
2. **ML Model Accuracy:** Extensive testing with Lake Simcoe data, fallback to statistical methods
3. **Agent Safety:** Whitelisted actions, audit trail, manual override, rollback capability
4. **Update Failures:** Signature verification, health checks, automatic rollback
5. **Network Failures:** All critical features work offline, cloud is enhancement not requirement

### Business Risks:
1. **Development Overruns:** Phased approach, can stop/pivot after any version
2. **Low Adoption:** Tier 0 remains free and functional, no sunk costs for users
3. **Competition:** First-to-market with AI-powered predictive maintenance in marine space
4. **Regulatory:** Privacy-first design, PIPEDA/GDPR compliant, data deletion rights

### Mitigation Strategies:
- Incremental rollout (version-by-version)
- Beta testing at each stage
- Rollback capability built into update system
- Community feedback loops
- Parallel development (phases can run simultaneously)

---

## NEXT STEPS

### Immediate (March 2026):
1. ✅ Read Master Integration Reference
2. ✅ Create version-based roadmap
3. ✅ **Begin v0.9.2 implementation (Metric/Imperial) - 3 weeks**
   - Create units.js conversion utility
   - Create preferences API (Port 8107)
   - Update dashboard, onboarding, navigation, weather pages
   - Update voice assistant for unit conversions
4. ⏳ After v0.9.2: Begin v0.9.3 implementation (Gemini API)
   - Set up development environment
   - Create Gemini proxy service (Port 8099)
   - Integrate into onboarding wizard (Steps 17.x)

### Short-term (April-June 2026):
1. Complete v0.9.3 (Gemini API)
2. Test with Lake Simcoe beta group
3. Begin v0.9.4 (Mobile Apps + Cloud)
4. Provision AtMyBoat.com VPS
5. Set up Headscale mesh

### Medium-term (July-December 2026):
1. Complete v0.9.4 and v0.9.5 (Tier 1 & 2 activation)
2. Begin v0.10.0 (Predictive Maintenance)
3. Collect 30-day baseline data from fleet
4. Train ML models
5. Deploy Tier 2 to paying subscribers
6. **Complete v0.10.2 (4-Camera System) - December 2026**
   - Camera registry and auto-discovery
   - Multi-camera UI (Single View + Grid View)
   - Forward Watch integration (bow camera obstacle avoidance)

### Long-term (2027):
1. Complete all phases through v1.0.0
2. Complete v0.15.0 (Multi-Language) - September 2027
3. Scale to 1,000+ users
4. Achieve break-even
5. Expand to commercial fleets
6. International distribution (8 languages: English, French, Spanish, German, Italian, Dutch, Swedish, Norwegian)
7. Launch v1.0.0 production release - December 2027

---

## APPENDICES

### A. Port Assignment Reference
See Master Integration Reference Section 4 (Microservice Inventory)

### B. Database Schema Reference
See Master Integration Reference Section 6 (Database Schema Index)

### C. API Endpoint Reference
See Master Integration Reference Section 7 (API Endpoint Index)

### D. MQTT Topic Map
See Master Integration Reference Section 8 (MQTT Topic Map)

### E. Tier Access Matrix
See Master Integration Reference Section 9 (Tier Access Quick Reference)

### F. Privacy Rules
See Master Integration Reference Section 10 (Privacy Rules - Non-Negotiable)

### G. Naming Conventions
See Master Integration Reference Section 11 (Use Consistently Everywhere)

### H. Version Tracking
See Master Integration Reference Section 12 (Release History)

---

## DOCUMENT CONTROL

**Version:** 1.3
**Date:** March 1, 2026
**Author:** Claude Code (Anthropic) + Donald Moskaluk
**Status:** Updated with 4-camera moved to v0.9.3, security audit added
**Next Review:** After v0.9.2 completion

**Related Documents:**
- Master Integration Reference (d3kos-master-integration-reference.odt)
- Three-Tier AI Architecture Proposal (THREE_TIER_AI_ARCHITECTURE_PROPOSAL.md)
- Onboarding Wizard Gemini Integration (ONBOARDING_WIZARD_GEMINI_INTEGRATION.md)
- Three-Tier AI Summary (THREE_TIER_AI_SUMMARY.md)
- Metric/Imperial Implementation Plan (METRIC_IMPERIAL_IMPLEMENTATION_PLAN.md)
- Multi-Camera Implementation Plan (MULTI_CAMERA_IMPLEMENTATION_PLAN.md)
- Language Selection Specification (LANGUAGE_SELECTION_SPECIFICATION.md)

**Change Log:**
- March 1, 2026 (v1.0): Initial version created, integrated Master Reference with three-tier AI proposal
- March 1, 2026 (v1.1): Added v0.9.2 (Metric/Imperial - 3 weeks) as immediate priority, added v0.10.2 (4-Camera System - 8-9 weeks) after Fleet Management, updated timeline to 110 weeks total
- March 1, 2026 (v1.2): Added v0.15.0 (Multi-Language Support - 6-8 weeks) before v1.0, required for international distribution, updated timeline to 118 weeks total (~27 months)
- March 1, 2026 (v1.3): **MAJOR UPDATE** - Moved 4-camera system from v0.10.2 to v0.9.3 (immediate priority after metric/imperial), renumbered all subsequent 0.9.x versions, added v0.16.0 Security Audit (4 weeks) before v1.0, updated timeline to 122 weeks total (~28 months), production launch now Q1 2028 (February 2028)

---

**© 2026 AtMyBoat.com | Donald Moskaluk | skipperdon@atmyboat.com**

*d3kOS - AI-Powered Marine Electronics Platform*
*"Smarter Boating, Simpler Systems"*
