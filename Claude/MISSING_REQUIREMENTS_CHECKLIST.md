# d3kOS Missing Requirements & Implementation Checklist

**Generated**: February 4, 2026  
**Based on**: MASTER_SYSTEM_SPEC.md, lookandfeeld3kos.txt, and existing documentation

---

## CRITICAL MISSING COMPONENTS

### ⚠️ HIGH PRIORITY - Core Functionality

#### 1. Main Menu HTML/UI
- [ ] **File**: `services/main-menu/index.html`
- [ ] **Requirements**:
  - [ ] AODA compliant
  - [ ] Black background (#000000)
  - [ ] White/green icons
  - [ ] 22px minimum font size
  - [ ] Large touch-friendly buttons (120px × 80px min)
  - [ ] Back button (left side, bottom)
  - [ ] Main Menu button (right side, bottom)
  - [ ] Reserved bottom 1/3 for on-screen keyboard
  - [ ] Browser runs in maximized mode (NOT kiosk to keep Pi menu accessible)
- [ ] **Buttons Required**:
  - [ ] Voice Enable (toggle switch)
  - [ ] Camera (full screen view + record)
  - [ ] OpenCPN (launch/manage)
  - [ ] License Info
  - [ ] Version Display (from GitHub)
  - [ ] QR Code Generator (for mobile app pairing)
  - [ ] Onboarding Wizard (launch/reset)
  - [ ] OpenCPN Install/Uninstall
  - [ ] Engine Benchmark
  - [ ] Boat Health
  - [ ] Boat Performance
  - [ ] Raspberry Pi Status
  - [ ] Boat Log (voice recording)
  - [ ] Dashboard (gauges)

---

#### 2. Onboarding Wizard - Complete Implementation
- [ ] **13-Question Engine Wizard**:
  - [ ] Engine manufacturer (dropdown with AI assist)
  - [ ] Engine model (dropdown with AI assist)
  - [ ] Engine year (number input with validation)
  - [ ] Number of cylinders (dropdown: 3, 4, 6, 8)
  - [ ] Engine displacement (L or CID with conversion)
  - [ ] Compression ratio (number input)
  - [ ] Stroke length (mm or inches with conversion)
  - [ ] Induction type (naturally aspirated, turbocharged, supercharged)
  - [ ] Rated horsepower (number input)
  - [ ] Idle RPM specification (number input)
  - [ ] WOT RPM range (min/max inputs)
  - [ ] Maximum coolant temperature (number input with unit)
  - [ ] Minimum safe oil pressure at idle and cruise (two number inputs)

- [ ] **Wizard Flow Control**:
  - [ ] Step-by-step navigation
  - [ ] Progress indicator
  - [ ] Back/Next buttons
  - [ ] Data persistence between steps
  - [ ] Auto-save on each step
  - [ ] Resume capability after reboot
  - [ ] AI-assisted field completion
  - [ ] Input validation
  - [ ] Error messaging

- [ ] **CX5106 Configuration Output**:
  - [ ] Visual DIP switch diagram
  - [ ] Switch-by-switch instructions
  - [ ] Explanation of why each setting
  - [ ] Photo/diagram overlay
  - [ ] Verification checklist

- [ ] **Onboarding Reset Tracking**:
  - [ ] Reset counter (Tier 0 limit: 10 resets)
  - [ ] Counter display in UI
  - [ ] Warning at reset 8 and 9
  - [ ] Hard stop at reset 10 with instructions to download new image
  - [ ] File: `state/onboarding-reset-count.json`

---

#### 3. Voice Assistant ("Helm")
- [ ] **Wake Word Detection**:
  - [ ] PocketSphinx integration
  - [ ] Wake word: "Helm"
  - [ ] Visual indicator when listening
  - [ ] Audio feedback (beep/chime)

- [ ] **Speech-to-Text (STT)**:
  - [ ] Vosk integration
  - [ ] Model: vosk-model-small-en-us-0.15
  - [ ] Offline processing
  - [ ] Real-time transcription display

- [ ] **Text-to-Speech (TTS)**:
  - [ ] Piper integration
  - [ ] Voice: en_US-amy-medium
  - [ ] Adjustable speed
  - [ ] Volume control

- [ ] **Local LLM**:
  - [ ] Phi-2 (2.7B) integration
  - [ ] Offline inference
  - [ ] Context awareness (boat status, engine data)
  - [ ] Command interpretation
  - [ ] Response generation

- [ ] **Voice Commands**:
  - [ ] "What's the engine status?"
  - [ ] "Any anomalies?"
  - [ ] "Open OpenCPN"
  - [ ] "Start benchmarking"
  - [ ] "Start onboarding"
  - [ ] "Record boat log"
  - [ ] "Helm post" (save log entry)
  - [ ] "Helm end" (end listening)

- [ ] **Boat Log Voice Recording**:
  - [ ] Voice-to-text transcription
  - [ ] Append to log file
  - [ ] Timestamp each entry
  - [ ] Read back for confirmation
  - [ ] Accept/discard options
  - [ ] Storage limit management (cap at 10% disk remaining)

---

#### 4. Camera Integration
- [ ] **Reolink RLC-810A Integration**:
  - [ ] IP camera discovery
  - [ ] RTSP stream display (VLC)
  - [ ] Full-screen view mode
  - [ ] Recording capability
  - [ ] Night vision auto-switching
  - [ ] Storage management (warn at 18% disk remaining)
  - [ ] File rotation/deletion when full

- [ ] **Camera Controls**:
  - [ ] Start/stop recording
  - [ ] Snapshot capture
  - [ ] Recording indicator
  - [ ] Storage status display
  - [ ] Playback interface

---

#### 5. Dashboard Gauges
- [ ] **Engine Gauges** (Line 1):
  - [ ] Tachometer (RPM)
  - [ ] Tilt/Trim indicator
  - [ ] Engine temperature
  - [ ] Battery voltage
  - [ ] Oil pressure

- [ ] **Tank Levels** (Line 2):
  - [ ] Fresh water (% full)
  - [ ] Black water (% full)
  - [ ] Fuel level (% full, gallons/liters remaining)
  - [ ] House battery level (%)

- [ ] **System Status** (Line 3):
  - [ ] Raspberry Pi CPU usage
  - [ ] Memory usage
  - [ ] Storage remaining
  - [ ] GPU usage

- [ ] **Network Status** (Line 4):
  - [ ] WiFi status (on/off, signal strength)
  - [ ] Ethernet status (on/off, IP address)
  - [ ] NMEA2000 status (on/off, device count)
  - [ ] Internet status (on/off)

- [ ] **Gauge Requirements**:
  - [ ] Real-time updates (1-second intervals)
  - [ ] Color-coded warnings (green/yellow/red)
  - [ ] Min/max values displayed
  - [ ] Historical graphs available
  - [ ] Touch to expand for details

---

#### 6. Engine Health Monitoring
- [ ] **Baseline Establishment**:
  - [ ] 30-minute data capture during first use
  - [ ] RPM stability analysis
  - [ ] Temperature curves
  - [ ] Oil pressure trends
  - [ ] Fuel rate measurement
  - [ ] Voltage monitoring
  - [ ] Storage: `config/benchmark-results.json`

- [ ] **Anomaly Detection**:
  - [ ] Real-time comparison to baseline
  - [ ] Threshold alerts
  - [ ] Trend analysis
  - [ ] Predictive warnings
  - [ ] Manufacturer spec compliance

- [ ] **Health Reports**:
  - [ ] Current status summary
  - [ ] Anomaly history
  - [ ] Trend graphs
  - [ ] Maintenance recommendations
  - [ ] Voice alerts for critical issues

---

#### 7. Raspberry Pi Health Monitoring
- [ ] **System Metrics**:
  - [ ] CPU temperature (warn > 80°C)
  - [ ] CPU usage (warn > 90%)
  - [ ] Memory usage (warn > 90%)
  - [ ] Disk space (warn < 20%)
  - [ ] GPU temperature
  - [ ] Throttling detection

- [ ] **Notifications**:
  - [ ] Visual warnings on dashboard
  - [ ] Voice alerts for critical conditions
  - [ ] Automatic logging
  - [ ] File: `state/pi-health-status.json`

---

#### 8. Licensing System
- [ ] **Tier Detection**:
  - [ ] Default: Tier 0 (opensource)
  - [ ] Tier 2: Detect installed apps
  - [ ] Tier 3: Validate subscription (future)
  - [ ] File: `config/license.json`

- [ ] **Version Management**:
  - [ ] GitHub release version tracking
  - [ ] Display current version in UI
  - [ ] Update notification (when online)
  - [ ] Changelog display

- [ ] **QR Code Generation**:
  - [ ] Generate unique installation ID
  - [ ] QR code for mobile app pairing
  - [ ] Display on completion screen
  - [ ] Regenerate capability

---

#### 9. OpenCPN Integration
- [ ] **Auto-Install**:
  - [ ] Detect no chartplotter
  - [ ] Install OpenCPN 5.8.x
  - [ ] Configure Signal K plugin
  - [ ] Configure GPS/AIS data sources
  - [ ] Script: `scripts/install-opencpn.sh`

- [ ] **Management**:
  - [ ] Launch button in main menu
  - [ ] Uninstall capability
  - [ ] Status indicator
  - [ ] Script: `scripts/uninstall-opencpn.sh`

- [ ] **Integration**:
  - [ ] Signal K data passthrough
  - [ ] GPS data from gpsd
  - [ ] AIS data forwarding
  - [ ] Chart management

---

### 📊 MEDIUM PRIORITY - Enhanced Features

#### 10. Network Configuration
- [ ] **WiFi Access Point**:
  - [ ] SSID: "d3kOS"
  - [ ] DHCP server
  - [ ] IP range: 10.42.0.1/24
  - [ ] Password configuration

- [ ] **Ethernet Sharing**:
  - [ ] Shared mode (10.42.0.1/24)
  - [ ] DHCP for camera
  - [ ] Static IP option

- [ ] **Status Display**:
  - [ ] Connected devices list
  - [ ] IP addresses
  - [ ] Signal strength (WiFi)
  - [ ] Bandwidth usage

---

#### 11. Boat Performance Tracking
- [ ] **Data Collection**:
  - [ ] Speed over ground
  - [ ] Fuel consumption
  - [ ] RPM vs speed curves
  - [ ] Trip distance
  - [ ] Trip time

- [ ] **Historical Analysis**:
  - [ ] Trip history
  - [ ] Fuel efficiency trends
  - [ ] Performance degradation detection
  - [ ] Seasonal comparisons

- [ ] **Reports**:
  - [ ] Daily summary
  - [ ] Weekly summary
  - [ ] Monthly summary
  - [ ] Export capability

---

#### 12. Touchscreen Optimizations
- [ ] **Gesture Support**:
  - [ ] Touchégg integration
  - [ ] Pinch-to-zoom (Ctrl + +/-)
  - [ ] Two-finger scroll
  - [ ] Swipe navigation

- [ ] **On-Screen Keyboard**:
  - [ ] Always-on-top behavior
  - [ ] Fixed position (bottom 1/3)
  - [ ] Auto-show on input focus
  - [ ] Auto-hide when not needed

- [ ] **Window Management**:
  - [ ] wmctrl integration
  - [ ] Enforce window positions
  - [ ] Prevent keyboard overlap
  - [ ] Restore window positions after reboot

---

### 🔧 LOW PRIORITY - Polish & Future

#### 13. Additional Features
- [ ] **Multi-Boat Support**:
  - [ ] Store multiple boat configurations
  - [ ] Switch between boats
  - [ ] Boat selection at boot

- [ ] **Data Export**:
  - [ ] CSV export for logs
  - [ ] JSON export for configs
  - [ ] Backup/restore capability

- [ ] **Theme Customization**:
  - [ ] Color scheme selection
  - [ ] Font size adjustment
  - [ ] Contrast settings

- [ ] **Advanced Settings**:
  - [ ] Update frequency adjustments
  - [ ] Logging verbosity
  - [ ] Debug mode

---

## DOCUMENTATION UPDATES NEEDED

### Update README.md
- [ ] Add pre-built image download link
- [ ] Add flashing instructions
- [ ] Add first-boot instructions
- [ ] Update hardware list to match lookandfeeld3kos.txt
- [ ] Add voice assistant info
- [ ] Add licensing tiers

### Update INSTALLATION_GUIDE.md
- [ ] Change from manual install to image flashing
- [ ] Add image verification (SHA256)
- [ ] Add first-boot configuration
- [ ] Add troubleshooting for image issues

### Update ARCHITECTURE.md
- [ ] Add voice assistant architecture
- [ ] Add camera integration architecture
- [ ] Add licensing system architecture
- [ ] Add boat log system architecture
- [ ] Update UI/UX section with AODA requirements

### Update ONBOARDING_FLOW.md
- [ ] Add all 13 engine questions
- [ ] Add AI assistance logic for each question
- [ ] Add reset counter logic
- [ ] Add QR code generation step
- [ ] Add license tier selection

### Create New Documents
- [ ] `VOICE_ASSISTANT.md` - Complete voice system documentation
- [ ] `DASHBOARD_GAUGES.md` - Gauge specifications and layouts
- [ ] `LICENSING.md` - Tier system and reset limits
- [ ] `CAMERA_INTEGRATION.md` - Camera setup and management
- [ ] `BOAT_LOG.md` - Voice logging system
- [ ] `FLASHING_GUIDE.md` - How to flash the pre-built image
- [ ] `FIRST_BOOT.md` - What happens on first boot

---

## CODE/SCRIPTS NEEDED

### Core Services
- [ ] `/opt/d3kos/services/onboarding/index.js` - Onboarding backend
- [ ] `/opt/d3kos/services/onboarding/reasoningEngine.js` - AI logic
- [ ] `/opt/d3kos/services/onboarding/dipSwitchCalculator.js` - CX5106 logic
- [ ] `/opt/d3kos/services/onboarding/pgnDetector.js` - NMEA2000 detection
- [ ] `/opt/d3kos/services/voice/index.js` - Voice assistant backend
- [ ] `/opt/d3kos/services/voice/wakeword.js` - PocketSphinx integration
- [ ] `/opt/d3kos/services/voice/stt.js` - Vosk integration
- [ ] `/opt/d3kos/services/voice/tts.js` - Piper integration
- [ ] `/opt/d3kos/services/voice/llm.js` - Phi-2 integration
- [ ] `/opt/d3kos/services/camera/index.js` - Camera management
- [ ] `/opt/d3kos/services/health/index.js` - System health monitoring
- [ ] `/opt/d3kos/services/health/engine-monitor.js` - Engine health
- [ ] `/opt/d3kos/services/health/pi-monitor.js` - Pi health

### Installation Scripts
- [ ] `scripts/install-voice.sh` - Voice assistant setup
- [ ] `scripts/install-phi2.sh` - Phi-2 LLM download
- [ ] `scripts/install-camera.sh` - Camera integration
- [ ] `scripts/configure-touchscreen.sh` - Touchégg setup
- [ ] `scripts/configure-keyboard.sh` - On-screen keyboard setup
- [ ] `scripts/create-image.sh` - Build flashable image
- [ ] `scripts/verify-image.sh` - Generate checksums

### Systemd Services
- [ ] `system/d3kos-voice.service` - Voice assistant service
- [ ] `system/helm-camera.service` - Camera service
- [ ] `system/d3kos-health.service` - Health monitoring
- [ ] `system/helm-boatlog.service` - Boat log service

---

## TESTING CHECKLIST

### Hardware Testing
- [ ] Test on Raspberry Pi 4B (4GB)
- [ ] Test on Raspberry Pi 4B (8GB)
- [ ] Test with PiCAN-M HAT
- [ ] Test with 10.1" touchscreen at 1920x1200
- [ ] Test on-screen keyboard positioning
- [ ] Test with USB GPS connected
- [ ] Test with USB AIS connected
- [ ] Test with Anker PowerConf S330
- [ ] Test with Reolink camera

### Software Testing
- [ ] Complete onboarding wizard (all paths)
- [ ] CX5106 DIP switch generation
- [ ] Voice assistant wake word
- [ ] Voice commands (all supported)
- [ ] Camera recording/playback
- [ ] Dashboard gauge updates
- [ ] Engine health monitoring
- [ ] Anomaly detection
- [ ] Onboarding reset counter
- [ ] OpenCPN auto-install
- [ ] Network configuration

### UI/UX Testing
- [ ] AODA compliance validation
- [ ] Color contrast testing (1000 nit screen)
- [ ] Font size readability
- [ ] Button size and spacing
- [ ] Touch target accuracy
- [ ] Keyboard overlap prevention
- [ ] Navigation flow
- [ ] Error message clarity

### Integration Testing
- [ ] Signal K → Node-RED data flow
- [ ] Node-RED → Dashboard display
- [ ] CAN0 → Signal K data reception
- [ ] GPS → Signal K → OpenCPN
- [ ] AIS → Signal K → OpenCPN
- [ ] Voice → Actions → Feedback loop
- [ ] Camera → Storage management

### Performance Testing
- [ ] Boot time (target: < 60 seconds to ready)
- [ ] Voice response time (target: < 2 seconds)
- [ ] Dashboard update frequency (target: 1 second)
- [ ] CPU usage under load
- [ ] Memory usage over time
- [ ] Storage usage growth rate

---

## PRIORITY MATRIX

### Phase 1 - Core (Do First)
1. ✅ CLAUDE.md (complete)
2. ✅ CX5106_USER_MANUAL.md (complete)
3. Main Menu HTML/UI
4. 13-Question Onboarding Wizard
5. Onboarding Reset Counter
6. Dashboard Gauges

### Phase 2 - Intelligence (Do Second)
7. Voice Assistant (Helm)
8. Engine Health Monitoring
9. Anomaly Detection
10. Raspberry Pi Health Monitoring

### Phase 3 - Integration (Do Third)
11. Camera Integration
12. Boat Log System
13. OpenCPN Auto-Install
14. QR Code Generation

### Phase 4 - Polish (Do Last)
15. Performance Tracking
16. Touchscreen Gestures
17. Multi-Boat Support
18. Theme Customization

---

## BLOCKERS & DEPENDENCIES

### Current Blockers
- [ ] Need Node-RED Dashboard 2.0 flow examples
- [ ] Need Phi-2 model hosting location
- [ ] Need Vosk model download instructions
- [ ] Need Piper voice file paths
- [ ] Need Reolink camera RTSP URL format

### External Dependencies
- [ ] GitHub release hosting for images
- [ ] SHA256 checksum generation
- [ ] Image compression (gzip)
- [ ] Mobile app development (QR code pairing)

---

## ESTIMATED EFFORT

| Component | Complexity | Estimated Hours |
|-----------|------------|-----------------|
| Main Menu UI | Medium | 16 |
| 13-Question Wizard | High | 40 |
| Voice Assistant | High | 60 |
| Dashboard Gauges | Medium | 24 |
| Camera Integration | Low | 8 |
| Health Monitoring | Medium | 32 |
| Documentation Updates | Medium | 24 |
| Testing | High | 40 |
| **Total** | | **244 hours** |

---

## SIGN-OFF CHECKLIST

Before declaring d3kOS v1.0 complete:

- [ ] All Phase 1 items complete
- [ ] All Phase 2 items complete
- [ ] All Phase 3 items complete
- [ ] All documentation updated
- [ ] All tests passing
- [ ] Image created and tested
- [ ] Image hosted on GitHub releases
- [ ] Flashing guide published
- [ ] Video demonstration recorded
- [ ] Community feedback addressed

---

**Document Version**: 1.0  
**Last Updated**: February 4, 2026  
**Next Review**: After Phase 1 completion
