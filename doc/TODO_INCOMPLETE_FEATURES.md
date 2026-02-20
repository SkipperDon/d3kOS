# d3kOS - Incomplete Features & TODO List

**Date Created:** 2026-02-20
**Purpose:** Comprehensive list of incomplete features for planning discussions
**Next Steps:** Discuss existing website, database structure, implementation methods

---

## OVERVIEW

**Current System Status:** 85% feature-complete (44/52 features working)
**Remaining Work:** 374-546 hours (~9-14 weeks full-time)
**Critical Gap:** Revenue features (e-commerce, mobile app, central database) 100% incomplete

---

## 🔴 HIGH PRIORITY - REVENUE-GENERATING FEATURES

### 1. E-COMMERCE & SUBSCRIPTION BILLING
**Time Estimate:** 40-60 hours
**Status:** Documentation complete, implementation NOT started
**Revenue Impact:** $669/month (100 Tier 2 subscribers @ $9.99/month)

**Documentation:**
- ✅ `STRIPE_BILLING_IMPLEMENTATION_GUIDE.md` (48KB, production-ready code)
- ✅ Database schema documented
- ✅ API endpoints designed
- ✅ Mobile IAP flows documented

**What's NOT Implemented:**

#### Backend Services (Python/Flask)
1. **Stripe Webhook Handler** (port 5000)
   - File: `/opt/d3kos/services/billing/stripe_webhook_handler.py`
   - Events: subscription.created, subscription.updated, subscription.deleted, payment.succeeded, payment.failed, trial.ending
   - Database updates on webhook events
   - Time: 12-16 hours

2. **Subscription Management API** (port 5001)
   - File: `/opt/d3kos/services/billing/subscription_api.py`
   - Endpoints (8 total):
     - `POST /api/v1/stripe/checkout/session` - Create checkout
     - `POST /api/v1/webhooks/stripe` - Receive webhooks
     - `GET /api/v1/tier/status` - Get tier and subscription
     - `POST /api/v1/subscription/cancel` - Cancel subscription
     - `POST /api/v1/subscription/reactivate` - Reactivate
     - `GET /api/v1/subscription/history` - Payment history
     - `POST /api/v1/apple/verify-receipt` - iOS receipt validation
     - `POST /api/v1/google/verify-purchase` - Android purchase validation
   - Time: 16-20 hours

3. **Database Schema** (3 new tables)
   - `subscriptions` - Active subscription tracking
   - `payments` - Transaction history
   - `tier_upgrades` - Audit log of tier changes
   - Modify: `installations` table (add subscription fields)
   - Time: 4-6 hours

4. **Systemd Services**
   - `d3kos-stripe-webhook.service`
   - `d3kos-subscription-api.service`
   - Auto-start configuration
   - Time: 2 hours

5. **Nginx Configuration**
   - Proxy `/api/v1/stripe/` → `localhost:5000`
   - Proxy `/api/v1/subscription/` → `localhost:5001`
   - SSL/TLS for webhooks
   - Time: 2 hours

#### Mobile App Integration
6. **iOS - Apple StoreKit 2**
   - Product IDs: `com.d3kos.tier2.monthly`, `com.d3kos.tier3.annual`
   - Receipt validation flow
   - Server-to-server notifications from Apple
   - Settings → Subscription management page
   - Time: 12-18 hours

7. **Android - Google Play Billing Library 5.0+**
   - Product IDs: `tier2_monthly`, `tier3_annual`
   - Purchase verification flow
   - Real-Time Developer Notifications (RTDN)
   - Settings → Subscription management page
   - Time: 12-18 hours

#### Payment Flows
8. **Failed Payment Grace Period**
   - Day 0: 1st retry (immediate), email notification
   - Day 3: 2nd retry (after 3 days), warning email
   - Day 10: 3rd retry (after 7 days), final warning
   - Day 24: 4th retry (after 14 days), expire subscription
   - Auto-downgrade tier on expiration
   - Time: 4-6 hours

9. **Subscription Cancellation**
   - Immediate cancellation (no refund)
   - End-of-period cancellation (keep until expires)
   - Tier downgrade logic
   - Time: 2-4 hours

10. **Pricing Configuration**
    - Tier 2: $9.99/month USD
    - Tier 3: $99.99/year USD (17% discount)
    - Stripe product/price setup
    - Apple/Google in-app product setup
    - Time: 2-3 hours

**Current Blocker:** Placeholder API URL in export system
- File: `/opt/d3kos/services/export/export-manager.py`
- Line: `CENTRAL_API_URL = "https://d3kos-cloud-api.example.com"`
- Must be updated to actual production URL

**Cost Breakdown:**
- Stripe: 2.9% + $0.30 per transaction
- Apple IAP: 15-30% (mandatory, auto-deducted)
- Google Play: 15-30% (mandatory, auto-deducted)
- Server: $10-50/month (VPS)
- Email: $0-10/month (SendGrid free tier)

**Revenue Example (100 Tier 2 subscribers):**
- Gross: $999/month
- Fees: ~$330/month (33%)
- **Net: ~$669/month**
- **Break-even: 3-13 months** (depending on dev cost)

---

### 2. CENTRAL DATABASE / CLOUD BACKEND
**Time Estimate:** 60-80 hours
**Status:** NOT started
**Dependency:** Required for e-commerce, mobile app, fleet management

**What's NOT Implemented:**

#### Database Server
1. **Database Schema** (13 tables + 3 billing tables)
   - `installations` - All d3kOS installations (Pi units)
   - `users` - User accounts (email, password hash)
   - `boats` - Boat information
   - `boatlog_entries` - Synced boatlog data
   - `marine_vision_captures` - Fish capture metadata (NO images)
   - `marine_vision_snapshots` - Forward watch metadata (NO videos)
   - `engine_benchmarks` - Engine telemetry data
   - `system_alerts` - Critical alerts from all installations
   - `qr_codes` - QR generation history
   - `onboarding_configs` - Wizard answers for restore
   - `export_history` - Export upload tracking
   - `subscriptions` - Active subscriptions (billing)
   - `payments` - Payment transactions (billing)
   - `tier_upgrades` - Tier change audit log (billing)
   - `fleet_assignments` - Multi-boat management (Tier 3)
   - Time: 8-12 hours

2. **Database Technology Choice** (PENDING DISCUSSION)
   - Option A: PostgreSQL (recommended for production)
   - Option B: MySQL/MariaDB
   - Option C: SQLite (NOT suitable for multi-user)
   - Needs: Geographic queries (GPS data), JSON support, transactions
   - Time: Included in setup

#### Backend API Server
3. **Data Import/Export API** (Python/Flask or Node.js/Express)
   - `POST /api/v1/data/import` - Upload export JSON from Pi
     - Authentication: Bearer token (installation_id)
     - Validates JSON format
     - Parses all 9 export categories
     - Inserts into database tables
     - Returns success/failure
   - `GET /api/v1/data/export/status` - Check sync status
   - `POST /api/v1/config/import` - Import onboarding config for restore
   - Time: 16-24 hours

4. **Installation Management API**
   - `POST /api/v1/installations/register` - Register new installation
   - `GET /api/v1/installations/{id}` - Get installation details
   - `PUT /api/v1/installations/{id}` - Update installation
   - `GET /api/v1/installations/{id}/status` - Last seen, tier, version
   - Time: 8-12 hours

5. **Fleet Management API** (Tier 3 only)
   - `GET /api/v1/fleet` - List all boats in fleet
   - `GET /api/v1/fleet/dashboard` - Aggregated fleet data
   - `POST /api/v1/fleet/assign` - Assign boat to fleet
   - Time: 12-16 hours

6. **Authentication & Authorization**
   - User registration/login (email/password)
   - JWT token generation
   - Bearer token validation
   - Installation ownership verification
   - Role-based access control (user, admin, fleet manager)
   - Time: 8-12 hours

#### Hosting & Deployment
7. **Server Setup** (PENDING DISCUSSION)
   - Option A: AWS (EC2, RDS, S3)
   - Option B: DigitalOcean (Droplet, Managed Database)
   - Option C: Heroku (easy but expensive)
   - Option D: VPS (Linode, Vultr, Hetzner)
   - Requirements: 2-4 GB RAM, 50+ GB storage, SSL/TLS
   - Cost: $10-100/month depending on provider
   - Time: 4-8 hours initial setup

8. **Domain & SSL**
   - Domain name (e.g., api.d3kos.com)
   - SSL certificate (Let's Encrypt free)
   - DNS configuration
   - Time: 2-4 hours

9. **Monitoring & Logging**
   - Error tracking (Sentry)
   - Uptime monitoring (UptimeRobot)
   - Log aggregation (Papertrail, Loggly)
   - Performance monitoring (New Relic, Datadog)
   - Time: 4-6 hours

**Current Status:**
- Export system generates JSON files ✅
- Queue system working ✅
- Background worker ready ✅
- **Cannot upload - placeholder URL** ❌
- No central storage ❌
- No remote access ❌

**Decisions Needed:**
1. Database technology (PostgreSQL recommended)
2. Backend language (Python/Flask or Node.js/Express)
3. Hosting provider (AWS, DigitalOcean, VPS)
4. Domain name for API
5. Backup/redundancy strategy
6. Data retention policy (GDPR compliance)

---

### 3. MOBILE APP (iOS & Android)
**Time Estimate:** 120-180 hours
**Status:** NOT started
**Dependency:** Requires central database API

**What's NOT Implemented:**

#### iOS App (Swift/SwiftUI)
1. **QR Code Pairing Flow**
   - Scan QR code from d3kOS onboarding (Step 19)
   - Extract installation_id and pairing_token
   - Register mobile device with central API
   - Store credentials in iOS Keychain
   - Time: 8-12 hours

2. **Data Sync**
   - Pull latest exports from central database
   - Display boatlog entries
   - Show marine vision captures (metadata, thumbnails)
   - View system status
   - Sync button + auto-sync on launch
   - Time: 16-24 hours

3. **Settings Restore**
   - Download onboarding configuration
   - Generate restore QR code
   - User scans with d3kOS after firmware update
   - Restores boat info, engine config, reset counter
   - Time: 8-12 hours

4. **Subscription Management** (Apple IAP)
   - Product catalog (Tier 2 Monthly, Tier 3 Annual)
   - Purchase flow (StoreKit 2 API)
   - Receipt validation with backend
   - Subscription status display
   - Manage subscription (cancel, reactivate)
   - Restore purchases
   - Time: 16-24 hours

5. **Push Notifications**
   - Register for APNs (Apple Push Notification service)
   - Display critical alerts from d3kOS
   - Fish capture notifications
   - Low fuel warnings
   - System alerts
   - Time: 12-16 hours

6. **UI/UX Design**
   - Navigation (tabs: Dashboard, Boatlog, Marine Vision, Settings)
   - d3kOS branding (black/green theme)
   - Charts/graphs for telemetry
   - Responsive design (iPhone, iPad)
   - Time: 20-30 hours

7. **App Store Submission**
   - App icons, screenshots, descriptions
   - Privacy policy, terms of service
   - TestFlight beta testing
   - App Store review process
   - Time: 8-12 hours

**iOS Total:** 88-130 hours

#### Android App (Kotlin/Jetpack Compose)
8. **Same features as iOS:**
   - QR code pairing (8-12h)
   - Data sync (16-24h)
   - Settings restore (8-12h)
   - Subscription management - Google Play Billing (16-24h)
   - Push notifications - Firebase Cloud Messaging (12-16h)
   - UI/UX design (20-30h)
   - Google Play submission (8-12h)

**Android Total:** 88-130 hours

#### Shared Backend Work
9. **Mobile API Endpoints** (on central database server)
   - `POST /api/v1/mobile/register` - Device registration
   - `GET /api/v1/mobile/sync` - Get latest data
   - `POST /api/v1/mobile/pair` - QR code pairing
   - `GET /api/v1/mobile/config` - Get onboarding config
   - `POST /api/v1/mobile/push-token` - Store FCM/APNs token
   - Time: 8-12 hours

10. **Push Notification Service**
    - Firebase Cloud Messaging (FCM) setup
    - Apple Push Notification service (APNs) setup
    - Notification templates
    - Trigger logic (when to send)
    - Time: 8-12 hours

**Mobile App Total:** 120-180 hours (iOS + Android + Backend)

**Technologies:**
- iOS: Swift 5.9+, SwiftUI, StoreKit 2, Combine
- Android: Kotlin 1.9+, Jetpack Compose, Billing Library 5.0+, Coroutines
- Backend: Python/Flask or Node.js/Express
- Database: PostgreSQL

**App Store Requirements:**
- Apple Developer Program: $99/year
- Google Play Console: $25 one-time
- Privacy policy URL
- Terms of service URL
- App icons (multiple sizes)
- Screenshots (iPhone, iPad, Android phones/tablets)

**Current Status:**
- QR code generates installation_id ✅
- No mobile app exists ❌
- No pairing flow ❌
- No mobile data access ❌

---

### 4. MARINE VISION - CONTINUOUS MONITORING
**Time Estimate:** 42-62 hours
**Status:** Phase 1 complete, Phases 2-5 NOT implemented
**Current Gap:** Manual frame-by-frame detection only, no continuous monitoring

**What's NOT Implemented:**

#### Phase 2.2-2.6: Fish Capture Mode
1. **Continuous Video Monitoring Service**
   - Background frame processor thread
   - Process frames at 2 FPS (balance performance/detection)
   - Run YOLOv8 detection on each frame
   - Auto-capture when person+fish detected
   - File: `/opt/d3kos/services/marine-vision/continuous_monitor.py`
   - Service: `d3kos-continuous-monitor.service`
   - Time: 6-8 hours

2. **Custom Fish Detection Model**
   - **Option A:** Download pre-trained from Roboflow (requires account)
     - Free tier available
     - Fine-tuned for freshwater/saltwater fish
     - Time: 2-4 hours
   - **Option B:** Train custom YOLOv8 model
     - Collect fish dataset (1000+ images)
     - Label images with species
     - Train on GPU (8-12 hours)
     - Export to ONNX
     - Time: 20-30 hours
   - **Option C:** Use cloud fish detection API
     - FishID, iNaturalist, or custom service
     - Internet dependency
     - API costs
     - Time: 4-6 hours
   - **Recommended:** Option A (Roboflow)

3. **Species Identification**
   - ResNet50 or EfficientNet classifier
   - Fine-tuned on Ontario fish species
   - Classes: Bass, Pike, Walleye, Trout, Muskie, Perch, etc.
   - Confidence threshold: 60%+
   - Fallback to FishBase API for unknown species
   - Time: 8-12 hours

4. **Fishing Regulations Check**
   - Ontario MNR database integration
   - Location-based (GPS) + date-based rules
   - Size limits (min/max length in cm)
   - Bag limits (daily catch limit)
   - Closed seasons
   - Special regulations (sanctuaries, slot sizes)
   - Display warnings if undersized/oversized/closed season
   - Time: 12-16 hours

5. **Auto-Capture Logic**
   - Detect: person AND fish in same frame
   - Wait for stable detection (3+ consecutive frames)
   - Trigger high-res photo capture
   - Run species identification
   - Check fishing regulations
   - Log event to database
   - Send Telegram notification
   - Time: 4-6 hours

6. **Telegram Integration** (Infrastructure exists)
   - Connect fish detector to notification service
   - Format fish capture message
   - Upload photo to Telegram
   - Include species, confidence, GPS, regulations
   - **Service already deployed** ✅
   - Time: 2 hours (just integration)

**Fish Capture Total:** 34-48 hours

#### Phase 4: Forward Watch Mode
7. **Marine Object Detection**
   - Detect: boats, kayaks, buoys, logs, floating debris
   - Use COCO classes (boat, person, bird) + custom classes
   - Train custom model for marine objects
   - Time: 12-16 hours

8. **Distance Estimation (Monocular Depth)**
   - MiDaS or ZoeDepth model
   - Estimate distance to detected objects
   - Model size: ~100MB
   - Inference time: 3-5 seconds per frame on Pi 4B
   - Depth map generation
   - Time: 8-12 hours

9. **Real-Time Collision Alerts**
   - Calculate time-to-collision (TTC)
   - Alert if object <50m and approaching
   - Visual alert (red border, flashing)
   - Audible alert (beep, voice warning)
   - Log collision risk events
   - Time: 6-8 hours

10. **Object Tracking**
    - Track detected objects across frames
    - Maintain object ID (boat_1, kayak_2, buoy_3)
    - Track movement direction and speed
    - Predict trajectory
    - Time: 8-12 hours

**Forward Watch Total:** 34-48 hours

#### Phase 5: Mode Switching
11. **Camera Orientation Detection**
    - Detect camera angle (forward vs. downward)
    - Option A: Accelerometer/gyroscope (if camera has)
    - Option B: Searchlight position sensor
    - Option C: Manual toggle button
    - Auto-switch between Fish Capture and Forward Watch
    - Time: 4-6 hours

**Mode Switching Total:** 4-6 hours

**Marine Vision Continuous Monitoring Total:** 72-102 hours

**Current Status:**
- ✅ Camera streaming (Reolink RLC-810A, RTSP, frame grabber)
- ✅ Video recording (start/stop, VLC)
- ✅ Photo capture (high-res JPEG)
- ✅ Object detection API (YOLOv8n ONNX)
- ✅ Person detection working
- ✅ Telegram notification service
- ✅ Web UI (/marine-vision.html)
- ❌ Fish detection broken (COCO has no fish class)
- ❌ Continuous monitoring NOT implemented
- ❌ Auto-capture NOT working
- ❌ Species ID NOT implemented
- ❌ Fishing regulations NOT implemented
- ❌ Forward Watch mode NOT implemented
- ❌ Distance estimation NOT implemented
- ❌ Collision alerts NOT implemented

**Performance Expectations:**
- Frame processing: 2 FPS (every 500ms)
- Detection latency: 2-3 seconds per frame
- Auto-capture delay: 1-2 seconds after detection
- Memory usage: 350-500 MB (continuous monitoring)
- CPU usage: 40-60% of one core

**User Experience:**
- Camera always monitoring (when switched on)
- Automatic fish photo capture (no button press)
- Instant Telegram notification with photo
- Species identified automatically
- Fishing regulations displayed
- Forward Watch alerts for obstacles
- Hands-free operation while boating

---

## 🟡 MEDIUM PRIORITY - SPEC'D FEATURES

### 5. CHARTS & NAVIGATION
**Time Estimate:** 2-3 hours (assuming user has charts) + user purchases
**Status:** OpenCPN installed, NOT configured

**What's Partially Working:**
- ✅ OpenCPN installed (standalone works)
- ✅ `/charts.html` page exists
- ✅ Can launch OpenCPN manually

**What's NOT Configured:**
1. **o-charts Plugin**
   - Not installed/configured
   - Required for encrypted vector charts
   - Account creation needed
   - Time: 1 hour

2. **Marine Chart Data**
   - No charts loaded
   - User must purchase:
     - NOAA charts (USA) - Free
     - CHS charts (Canada) - ~$50-150 CAD
     - Private charts (Navionics, C-Map) - $100-300
   - Download and import charts
   - Time: 1-2 hours

3. **Chart Sources**
   - Not configured in OpenCPN
   - Need to add chart directories
   - Enable chart layers
   - Time: 30 minutes

4. **Route Planning**
   - Not implemented
   - Create routes
   - Add waypoints
   - Calculate distance/bearing
   - Time: Not included (future enhancement)

5. **Auto-Routing**
   - Not configured
   - Requires depth data
   - Collision avoidance
   - Time: Not included (future enhancement)

**User Action Required:**
- Purchase chart data for region (Lake Simcoe, Ontario)
- Provide chart files
- Create o-charts account

**Time:** 2-3 hours (after user provides charts)

---

### 6. WEATHER ALERTS & NOTIFICATIONS
**Time Estimate:** 8-12 hours
**Status:** NOT implemented

**What Works:**
- ✅ Weather page shows forecast (Windy.com embed)
- ✅ Current conditions from OpenWeatherMap
- ✅ Marine forecast from NOAA/Environment Canada

**What's NOT Implemented:**
1. **Severe Weather Alerts**
   - Monitor NOAA weather alerts API
   - Environment Canada alerts API
   - Parse alert severity (watch, warning, emergency)
   - Time: 4-6 hours

2. **Push Notifications**
   - Telegram alerts for severe weather
   - Mobile app push notifications
   - Desktop browser notifications
   - Time: 2-3 hours

3. **Wind Speed Warnings**
   - Alert if wind >20 knots
   - Alert if gusts >30 knots
   - Configurable thresholds
   - Time: 1-2 hours

4. **Wave Height Alerts**
   - Alert if waves >3 feet
   - Configurable threshold
   - Time: 1-2 hours

5. **Lightning Alerts**
   - Real-time lightning detection
   - Distance to storm
   - Time to arrival
   - Time: 2-3 hours (if API available)

**APIs Needed:**
- NOAA Alerts: https://api.weather.gov/alerts
- Environment Canada: https://dd.weather.gc.ca/alerts/cap/
- Lightning API: WeatherBug, Earth Networks (paid)

**Time:** 8-12 hours

---

### 7. FUEL CONSUMPTION PREDICTIONS
**Time Estimate:** 12-16 hours
**Status:** NOT implemented

**What Works:**
- ✅ Current fuel level displayed (if sensor configured)

**What's NOT Implemented:**
1. **Fuel Burn Rate Tracking**
   - Calculate fuel consumption over time
   - Liters/hour at different RPMs
   - Fuel efficiency (L/km or MPG)
   - Store historical data
   - Time: 4-6 hours

2. **Range Prediction**
   - Estimate range based on current fuel level
   - Calculate at current speed
   - Calculate at cruising speed
   - "Distance to empty" display
   - Time: 2-3 hours

3. **Fuel Efficiency Graphs**
   - RPM vs. fuel consumption chart
   - Speed vs. fuel efficiency chart
   - Historical fuel usage over trips
   - Time: 3-4 hours

4. **Low Fuel Warnings**
   - Alert at 25% fuel remaining
   - Alert at 10% fuel remaining
   - Estimated minutes to empty
   - Nearest marina with fuel
   - Time: 2-3 hours

5. **Fuel Stop Planning**
   - Calculate if fuel stop needed on route
   - Suggest optimal refuel point
   - Display marina locations with fuel
   - Time: 3-5 hours

**Data Requirements:**
- Fuel level sensor (NMEA2000 PGN 127505)
- GPS position (for distance traveled)
- Engine RPM (for consumption calculation)
- Speed over ground (for efficiency)

**Time:** 12-16 hours

---

### 8. MAINTENANCE SCHEDULING
**Time Estimate:** 16-24 hours
**Status:** NOT implemented

**What Works:**
- ✅ Engine hours tracked (Signal K data)

**What's NOT Implemented:**
1. **Engine Hour Tracking UI**
   - Display current engine hours
   - Hours since last service
   - Remaining hours to next service
   - Time: 2-3 hours

2. **Service Interval Alerts**
   - Oil change: every 50 hours
   - Spark plugs: every 100 hours
   - Impeller: every 200 hours
   - Lower unit oil: every 100 hours
   - Configurable intervals
   - Time: 4-6 hours

3. **Oil Change Reminders**
   - Visual alert when due
   - Telegram notification
   - Reset button after service
   - Log service date and hours
   - Time: 2-3 hours

4. **Maintenance Log**
   - Record all maintenance events
   - Date, type, description, cost
   - Attach photos/receipts
   - Export to CSV/PDF
   - Time: 4-6 hours

5. **Parts Inventory**
   - Track spare parts on board
   - Oil, filters, spark plugs, impeller, fuses, etc.
   - Quantity tracking
   - Low stock alerts
   - Time: 3-4 hours

6. **Service History Export**
   - Generate maintenance report
   - Include all service events
   - For warranty claims, resale value
   - Time: 1-2 hours

**Maintenance Items:**
- Oil change (50h intervals)
- Spark plugs (100h)
- Fuel filter (100h)
- Water pump impeller (200h or annually)
- Lower unit oil (100h or annually)
- Battery inspection (monthly)
- Zinc anode replacement (annually)
- Propeller inspection (monthly)

**Time:** 16-24 hours

---

### 9. MULTI-LANGUAGE SUPPORT
**Time Estimate:** 20-30 hours
**Status:** NOT implemented

**Current:**
- English only
- All UI text hardcoded in HTML/JS

**Languages Needed:**
1. **French** (Canada requirement)
   - All UI text
   - Error messages
   - Notifications
   - Time: 12-16 hours

2. **Spanish** (optional)
   - All UI text
   - Time: 8-12 hours

**Implementation:**
1. **Translation Framework**
   - i18next or similar library
   - Translation JSON files
   - Language switcher in Settings
   - Browser locale detection
   - Time: 4-6 hours

2. **Translate All Strings**
   - 12 web pages
   - All buttons, labels, messages
   - Error messages
   - Notifications
   - ~2000-3000 strings
   - Time: 16-24 hours (for French + Spanish)

**Files to Translate:**
- index.html, dashboard.html, navigation.html, weather.html
- helm.html, boatlog.html, ai-assistant.html, settings.html
- network-settings.html, onboarding.html, marine-vision.html, self-healing.html
- All API error messages
- All notification templates

**Time:** 20-30 hours

---

### 10. REMOTE MONITORING
**Time Estimate:** 12-16 hours
**Status:** NOT implemented

**Current:**
- Local access only: http://192.168.1.237/
- Accessible on boat network only
- No internet access

**What's NOT Implemented:**
1. **VPN Configuration**
   - WireGuard or OpenVPN server on Pi
   - Mobile clients (iOS, Android, Windows, Mac)
   - Secure tunnel for remote access
   - Time: 4-6 hours

2. **Port Forwarding Setup**
   - Router configuration guide
   - Dynamic DNS (DuckDNS, No-IP)
   - Port forwarding rules
   - Security considerations
   - Time: 2-3 hours

3. **Cloud Relay Service** (optional)
   - Tunnel through cloud server (if port forwarding unavailable)
   - ngrok, Cloudflare Tunnel, or custom relay
   - Subscription cost
   - Time: 3-4 hours

4. **Mobile App Remote Access**
   - Connect via VPN or cloud relay
   - View live dashboard
   - Check system status
   - View camera feed
   - Time: 3-4 hours (if mobile app exists)

**Security Considerations:**
- HTTPS/TLS encryption required
- Strong authentication (not just password)
- IP whitelisting (optional)
- Firewall rules
- Brute force protection

**Time:** 12-16 hours

---

### 11. FLEET MANAGEMENT (Tier 3)
**Time Estimate:** 40-60 hours
**Status:** NOT started
**Dependency:** Requires central database

**Current:**
- Single boat only
- No multi-boat support

**What's NOT Implemented:**
1. **Multi-Boat Dashboard**
   - List all boats in fleet
   - Status overview (online, offline, alerts)
   - GPS map with all boat positions
   - Time: 8-12 hours

2. **Fleet Overview**
   - Aggregated statistics (total hours, fuel used, distance)
   - Fleet-wide alerts
   - Maintenance due across fleet
   - Time: 6-8 hours

3. **Boat Switching**
   - Select which boat to view
   - Switch between boats in UI
   - Permission management (who can see which boats)
   - Time: 4-6 hours

4. **Aggregated Data**
   - Combined boatlog from all boats
   - Fleet-wide marine vision captures
   - Total engine hours across fleet
   - Time: 6-8 hours

5. **Fleet-Wide Alerts**
   - Notify if ANY boat has issue
   - Critical alerts (engine overheat, low battery)
   - Daily summary email
   - Time: 4-6 hours

6. **Assignment Management**
   - Assign boats to fleet
   - Remove boats from fleet
   - Transfer ownership
   - Time: 4-6 hours

7. **Reporting**
   - Fleet utilization report
   - Maintenance schedule across fleet
   - Fuel consumption comparison
   - Export to PDF/Excel
   - Time: 8-12 hours

**Use Cases:**
- Charter boat companies
- Yacht clubs
- Fishing guides with multiple boats
- Marina management

**Time:** 40-60 hours

---

## 🟢 LOW PRIORITY - POLISH & FIXES

### 12. DASHBOARD LIVE DATA
**Time Estimate:** 1-2 hours
**Status:** Shows placeholder data, NOT reading Signal K

**Current Issue:**
- RPM: Works (shows 0 when engine off) ✅
- Oil pressure: Shows "45 PSI" (static placeholder) ❌
- Coolant temp: Shows "180°F" (static placeholder) ❌
- Fuel level: Shows "75%" (static placeholder) ❌
- Battery voltage: Shows "12.8V" (static placeholder) ❌

**Fix Required:**
- Update `/var/www/html/dashboard.html`
- Add WebSocket connection to Signal K
- Fetch real-time data for all gauges
- Same pattern as navigation.html (already working)
- Time: 1-2 hours

**File:** `/var/www/html/dashboard.html`
**Pattern:** Copy from `/var/www/html/navigation.html` (working example)

---

### 13. NETWORK STATUS LABELS (Cosmetic)
**Time Estimate:** 15 minutes
**Status:** Labels need white color

**Current Issue:**
- Network status labels hard to read
- Need white color for visibility

**Fix Required:**
- Update CSS in network settings page
- Change label color to white
- Time: 15 minutes

**File:** `/var/www/html/network-settings.html`

---

### 14. NMEA2000 SIMULATOR REMOVAL (Cleanup)
**Time Estimate:** 30 minutes
**Status:** Disabled but still in system

**Current Status:**
- vcan0 simulator disabled in Signal K ✅
- Service files still exist ❌
- Scripts still on system ❌

**Cleanup Required:**
- Remove `/opt/d3kos/simulator/` directory
- Remove `d3kos-simulator.service`
- Remove vcan0 references from Signal K config
- Time: 30 minutes

**Impact:** Low (currently disabled, not affecting anything)

---

## TOTAL SUMMARY

### Time Estimates by Priority

| Priority | Category | Time (hours) |
|----------|----------|--------------|
| 🔴 HIGH | E-commerce/Billing | 40-60 |
| 🔴 HIGH | Central Database | 60-80 |
| 🔴 HIGH | Mobile App | 120-180 |
| 🔴 HIGH | Marine Vision Continuous | 42-62 |
| **HIGH TOTAL** | | **262-382** |
| | | |
| 🟡 MEDIUM | Charts/Navigation | 2-3 |
| 🟡 MEDIUM | Weather Alerts | 8-12 |
| 🟡 MEDIUM | Fuel Predictions | 12-16 |
| 🟡 MEDIUM | Maintenance Scheduling | 16-24 |
| 🟡 MEDIUM | Multi-Language | 20-30 |
| 🟡 MEDIUM | Remote Monitoring | 12-16 |
| 🟡 MEDIUM | Fleet Management | 40-60 |
| **MEDIUM TOTAL** | | **110-161** |
| | | |
| 🟢 LOW | Dashboard Live Data | 1-2 |
| 🟢 LOW | Network Labels | 0.25 |
| 🟢 LOW | Simulator Cleanup | 0.5 |
| **LOW TOTAL** | | **2-3** |
| | | |
| **GRAND TOTAL** | | **374-546** |

---

## RECOMMENDED IMPLEMENTATION ORDER

### Phase 1: MVP for Revenue (220-320 hours / 6-8 weeks)
**Goal:** Enable subscription payments and cloud data sync

1. **Central Database API** (basic) - 30-40 hours
   - PostgreSQL database setup
   - Data import/export endpoints
   - Authentication
   - Hosting/deployment
   - Update export manager placeholder URL

2. **E-commerce Backend** - 40-60 hours
   - Stripe webhook handler
   - Subscription API
   - Database tables
   - Failed payment handling
   - Web-based checkout flow (before mobile app)

3. **Mobile App (MVP)** - 80-120 hours
   - iOS app (basic): QR pairing, data sync, subscription purchase
   - Android app (basic): Same features
   - Push notifications
   - App Store/Play Store submission

4. **Testing & Polish** - 20-30 hours
   - End-to-end testing
   - Bug fixes
   - Documentation
   - User testing

**Outcome:** Can accept subscription payments, generate revenue

---

### Phase 2: Core Features (90-130 hours / 3-4 weeks)
**Goal:** Complete critical safety and convenience features

5. **Marine Vision Continuous** - 42-62 hours
   - Continuous monitoring service
   - Custom fish model (Roboflow)
   - Auto-capture
   - Species ID
   - Fishing regulations
   - Telegram integration

6. **Dashboard Live Data** - 1-2 hours
   - Fix placeholder data
   - Read from Signal K

7. **Charts/Navigation** - 2-3 hours
   - o-charts setup (user provides charts)

8. **Weather Alerts** - 8-12 hours
   - NOAA/Environment Canada alerts
   - Push notifications

9. **Fuel Predictions** - 12-16 hours
   - Burn rate tracking
   - Range prediction
   - Low fuel warnings

10. **Maintenance Scheduling** - 16-24 hours
    - Service intervals
    - Maintenance log
    - Reminders

**Outcome:** Feature-complete for individual boat owners

---

### Phase 3: Advanced Features (60-90 hours / 2-3 weeks)
**Goal:** Expand market reach and capabilities

11. **Multi-Language Support** - 20-30 hours
    - French (Canada requirement)
    - Spanish (optional)

12. **Remote Monitoring** - 12-16 hours
    - VPN setup
    - Mobile remote access

13. **Fleet Management** - 40-60 hours
    - Multi-boat dashboard
    - Fleet-wide alerts
    - Tier 3 feature

14. **Polish & Cleanup** - 2-3 hours
    - Network label colors
    - Simulator removal

**Outcome:** Enterprise-ready, Tier 3 feature set complete

---

## DECISIONS NEEDED BEFORE IMPLEMENTATION

### Technology Stack
- [ ] Database: PostgreSQL vs. MySQL vs. other?
- [ ] Backend Language: Python/Flask vs. Node.js/Express?
- [ ] Mobile Framework: Native (Swift/Kotlin) vs. React Native vs. Flutter?
- [ ] Hosting Provider: AWS vs. DigitalOcean vs. Heroku vs. VPS?

### Infrastructure
- [ ] Domain name for API (e.g., api.d3kos.com)
- [ ] SSL certificate provider (Let's Encrypt free)
- [ ] Backup/redundancy strategy
- [ ] Monitoring and logging tools
- [ ] CI/CD pipeline (GitHub Actions, GitLab CI)

### Business Decisions
- [ ] Pricing confirmed ($9.99/month Tier 2, $99.99/year Tier 3)?
- [ ] Payment methods (Stripe, Apple IAP, Google Play only, or add PayPal)?
- [ ] Free trial period (7 days, 14 days, 30 days)?
- [ ] Data retention policy (GDPR compliance)
- [ ] Terms of Service and Privacy Policy
- [ ] Refund policy

### Development Resources
- [ ] Timeline (6 months? 12 months? rushed?)
- [ ] Budget for tools/services (Stripe, App Store, hosting)
- [ ] Testing devices (iPhone, Android, different screen sizes)
- [ ] Beta testers (boat owners willing to test)

### Marine Vision
- [ ] Roboflow account for fish detection model?
- [ ] Custom model training (dataset collection)?
- [ ] Fish species to support (Ontario freshwater?)
- [ ] Forward Watch priority (collision detection)?

---

## CURRENT SYSTEM STATUS

**Working (44/52 features - 85%):**
- ✅ Installation ID & Licensing system
- ✅ Tier detection (auto-upgrade to Tier 2)
- ✅ Export system with queue/retry (just completed)
- ✅ AI Assistant (text-based, Signal K cached)
- ✅ Voice Assistant (Vosk, wake words working)
- ✅ Marine Vision Phase 1 (camera streaming, person detection)
- ✅ Telegram notifications
- ✅ Boatlog CSV export
- ✅ Fish detector diagnostic
- ✅ Onboarding wizard (20 steps, keyboard working)
- ✅ Network Settings UI
- ✅ Self-healing system
- ✅ Backup/restore system
- ✅ All core services (11 APIs running)

**Not Working (8/52 features - 15%):**
- ❌ Marine Vision continuous monitoring
- ❌ Fish detection (COCO model limitation)
- ❌ Mobile app (doesn't exist)
- ❌ E-commerce/billing (not implemented)
- ❌ Central database (placeholder URL)
- ❌ Charts (o-charts not configured)
- ❌ Dashboard live data (shows placeholders)
- ❌ WiFi hotspot (hardware limitation - cannot fix)

**Revenue Status:**
- Current: $0/month (no payment system)
- Potential: $669/month (100 Tier 2 subscribers @ $9.99/month, after 33% fees)
- Blocker: E-commerce + central database + mobile app NOT implemented

---

## NEXT STEPS - PLANNING DISCUSSION

**Topics to Discuss:**
1. **Existing Website** - What exists? atmyboat.com? Landing page? Blog?
2. **Database Structure** - PostgreSQL schema design, relationships, indexes
3. **Implementation Methods** - Development approach, testing strategy
4. **Timeline** - When to launch MVP? Revenue projections?
5. **Priorities** - Which features are MUST-HAVE vs. nice-to-have?
6. **Resources** - Budget, tools, services, help needed?

**This document stored for reference during planning.**

---

**Document Version:** 1.0
**Date:** 2026-02-20
**Status:** Saved for future planning discussions
