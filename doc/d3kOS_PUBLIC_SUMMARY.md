# d3kOS - Smart Marine Helm Control System

**Version 2.7 | February 2026**

---

## What is d3kOS?

d3kOS is a comprehensive marine electronics system that transforms your boat into a smart vessel with AI-powered monitoring, voice control, and advanced navigation. Built on the reliable Raspberry Pi platform, d3kOS provides professional-grade features at a fraction of traditional marine electronics costs.

---

## Core Capabilities

### 🎯 Smart Engine Monitoring
- **Real-time engine health tracking** with RPM, temperature, oil pressure, and voltage monitoring
- **Intelligent anomaly detection** - alerts you before problems become failures
- **Baseline benchmarking** - learns your engine's normal behavior for accurate diagnostics
- **Visual dashboard** with easy-to-read gauges optimized for marine environments
- **Historical trend analysis** to track engine performance over time
- **Maintenance reminders** based on actual usage

### 🗣️ Voice-Controlled AI Assistant ("Helm")
- **Fully offline voice control** - works without internet connectivity
- **Hands-free operation** - perfect for when you're at the helm
- **Natural language commands** - just say "Helm, what's the engine status?"
- **Two AI modes:**
  - **Online AI** (fast, internet-connected, extensive knowledge)
  - **Onboard AI** (offline, fully private, local processing)
- **Wake words:** "Helm" (auto), "Advisor" (offline), "Counsel" (online)
- **Voice boat logging** - record notes hands-free while operating

### 🗺️ Navigation & Positioning
- **Automatic chartplotter detection** - works with existing systems or auto-installs OpenCPN
- **GPS/AIS integration** - track your position and nearby vessels
- **Compatible with major brands:**
  - Garmin (GPSMAP, Echomap series)
  - Simrad (NSS, GO, NSX series)
  - Raymarine (Axiom, Element, eS series)
  - Lowrance (HDS LIVE, Elite FS, HDS Carbon)
  - Furuno (TZtouch, NavNet series)
  - Humminbird (Solix, Helix series)
- **Standard NMEA2000 integration** - universal compatibility

### 🌦️ Weather Radar & Marine Conditions
- **GPS-based animated weather radar** with live precipitation overlay
- **Real-time marine conditions:**
  - Wind speed, direction, and gusts (knots)
  - Wave height, direction, and period
  - Sea state descriptions (Calm to Very Rough)
  - Visibility, precipitation, barometric pressure
  - Weather alerts (High Wind, High Seas warnings)
- **Large touch-friendly controls** (80×80px buttons)
- **Auto-logging to boat log** every 30 minutes
- **Windy.com integration** for professional weather visualization

### 📹 Marine Vision System (Planned Feature)
- **Fish Capture Mode:**
  - Automatic photo capture when holding a fish
  - AI species identification
  - Fishing regulations check (size/bag limits by location)
  - GPS-tagged catch logging
  - Phone notifications (Telegram/Signal/email)
- **Forward Watch Mode:**
  - Marine object detection (boats, kayaks, buoys, debris)
  - Distance estimation with visual alerts
  - Real-time hazard warnings
  - Night vision capability
- **IP67 waterproof camera** (Reolink RLC-810A)
- **360° motorized mount** - automatic mode switching

### 📊 Data Integration
- **NMEA2000 network integration** via PiCAN-M HAT
- **Tank level monitoring** (fuel, fresh water, black water)
- **Battery monitoring** with voltage and charge state
- **Compass and speed data**
- **Engine parameters** (12+ data points)
- **Environmental sensors** (temperature, humidity, pressure)

### 📝 Digital Boat Log
- **Voice-to-text logging** - speak your entries
- **Automatic weather logging** every 30 minutes
- **GPS position tagging** for each entry
- **Timestamp tracking** for all events
- **Export options** for record keeping
- **Searchable history**

### 📱 Mobile App Integration (Tier 1+)
- **QR code pairing** - instant setup with your phone
- **Remote monitoring** when connected to internet
- **Push notifications** for health alerts
- **Cloud synchronization** of logs and performance data
- **iOS and Android support**

---

## Hardware Platform

### Included in d3-k1 Complete System:
- **Raspberry Pi 4B** (8GB RAM recommended)
- **PiCAN-M HAT** with NMEA2000 interface
- **10.1" Sunlight-Readable Touchscreen** (1920×1200, 1000 nit)
- **IP67 Marine-Grade Enclosure**
- **GPS Receiver** (USB)
- **AIS Receiver** (USB)
- **Camera** (IP67 waterproof, night vision) - Tier 2+
- **All cables and mounting hardware**

### Storage:
- **32GB SD Card** (minimum) - OS and core software
- **128GB USB Drive** (recommended) - recordings and data storage

---

## Key Technical Features

### 🔒 Offline-First Design
- **Complete functionality without internet** - perfect for remote cruising
- **All AI processing runs locally** - no cloud dependency
- **Optional cloud sync** for backups and mobile access (Tier 1+)
- **Privacy-focused** - your data stays on your boat

### ♿ Accessibility & Usability
- **AODA/WCAG 2.1 AA compliant** interface
- **Large touch targets** (minimum 60×80px)
- **High contrast display** (black background, green/white text)
- **Sunlight-readable** 1000 nit screen
- **Glove-operable** controls
- **On-screen keyboard** for text input
- **Voice control** for hands-free operation

### 🔧 Easy Setup
- **AI-guided onboarding wizard** - 20 steps, ~10 minutes
- **Automatic engine configuration** - answers 15 questions about your engine
- **DIP switch calculator** for CX5106 gateway
- **Regional tank sensor support** (North American 240-33Ω or European 0-190Ω)
- **Multi-engine support** (port/starboard designation)
- **Automatic chartplotter detection**

### 🌐 Networking
- **WiFi Access Point** - connect phones/tablets directly
- **Ethernet sharing** - share internet with connected devices
- **DHCP server** - automatic IP assignment
- **mDNS/Bonjour** - access via http://d3kos.local

---

## Software Architecture

### Core Services:
- **Signal K Server** - Marine data aggregation hub
- **Node-RED** - Automation and data flows
- **OpenCPN 5.8.x** - Chart plotting (auto-installed if needed)
- **Voice Assistant Service** - Wake word detection and AI processing
- **Health Monitoring Service** - Continuous system diagnostics
- **Camera Service** - RTSP streaming and recording management

### AI Technology:
- **PocketSphinx** - Wake word detection ("Helm", "Advisor", "Counsel")
- **Vosk** - Speech-to-text (offline, 50MB model)
- **Piper** - Text-to-speech (natural voices)
- **Phi-2** - 2.7B parameter AI model (offline reasoning)
- **Perplexity API** - Online AI with internet search capability
- **SQLite** - Conversation history and learning

### Browser-Based Interface:
- **Chromium browser** - familiar web interface
- **Responsive design** - works on all screen sizes
- **Touchscreen optimized** - large buttons and controls
- **No app installation** - everything runs in the browser

---

## Licensing Tiers

### Tier 0: Base Opensource (FREE)
- All core features
- Offline voice assistant
- Engine monitoring and benchmarking
- OpenCPN navigation
- Boat log (local only)
- Weather radar
- **Limit:** 10 onboarding resets

### Tier 1: Mobile App Integration (FREE)
- Everything in Tier 0, PLUS:
- Mobile app (iOS/Android)
- Cloud database synchronization
- Push notifications
- Remote monitoring
- QR code pairing

### Tier 2: Premium Subscription (PAID)
- Everything in Tier 1, PLUS:
- AI-powered performance analysis
- Predictive maintenance recommendations
- Trend analysis and reports
- Camera recording and marine vision
- Cloud backup of configurations
- **~$4.99/month**

### Tier 3: Enterprise/Fleet (PAID)
- Everything in Tier 2, PLUS:
- **Unlimited onboarding resets**
- Multi-boat/fleet management
- Fleet-wide analytics
- PDF reports (individual + fleet)
- Priority support
- **~$99/year for 5 boats**

---

## Performance Specifications

### System Performance:
- **Boot time:** < 60 seconds to operational
- **Voice response time:** 2-8 seconds (online AI), 5-60 seconds (offline AI)
- **Dashboard update rate:** 1 Hz (every second)
- **Anomaly detection accuracy:** > 95%
- **False positive rate:** < 5%

### Data Update Rates:
- **Engine RPM:** 10 Hz (100ms)
- **Oil pressure/temperature:** 2 Hz (500ms)
- **Tank levels:** 0.4 Hz (2500ms)
- **Battery status:** 0.67 Hz (1500ms)
- **GPS position:** 1-10 Hz

---

## Use Cases

### Recreational Boaters:
- Monitor engine health without expensive marine electronics
- Voice-controlled boat logging for cruising notes
- Weather-aware trip planning
- Peace of mind with anomaly detection
- Document catches with species identification

### Liveaboards:
- Complete offline operation for remote cruising
- Track fuel and tank levels
- Weather monitoring without satellite
- Voice assistant for hands-free operation
- Digital logbook with GPS tracking

### Charter Operators (Tier 3):
- Fleet-wide health monitoring
- Predictive maintenance scheduling
- Automated reporting for compliance
- Remote monitoring of entire fleet
- Reduce downtime with early fault detection

### DIY/Tech Enthusiasts:
- Open-source platform (Tier 0)
- Fully customizable
- Standard NMEA2000 integration
- Raspberry Pi ecosystem compatibility
- Active development community

---

## Compatibility

### Works With:
- **Any NMEA2000 engine gateway** (CX5106 recommended)
- **Standard NMEA2000 sensors** (tank, temperature, pressure)
- **USB GPS receivers** (VK-162, BU-353, GlobalSat)
- **USB AIS receivers** (dAISy, NASA, em-trak)
- **IP cameras with RTSP** (Reolink, Hikvision, Dahua)
- **All major chartplotters** (Garmin, Simrad, Raymarine, etc.)

### Supported Engines:
- Gasoline (2-stroke and 4-stroke)
- Diesel (naturally aspirated and turbocharged)
- Outboard, inboard, and stern drive
- 3, 4, 6, or 8 cylinders
- Single or twin engine configurations

---

## Why Choose d3kOS?

### ✅ Cost-Effective
- **1/10th the cost** of equivalent marine electronics systems
- **No subscription required** for core features (Tier 0 is free)
- **Open-source** - full transparency and community support
- **Standard hardware** - Raspberry Pi is widely available and affordable

### ✅ Privacy-Focused
- **Offline-first design** - works without internet
- **Local AI processing** - no data sent to cloud (Tier 0)
- **Optional cloud sync** - you control what gets shared (Tier 1+)
- **No tracking** - your data stays on your boat

### ✅ Easy to Use
- **Voice control** - hands-free operation
- **Large touchscreen** - easy to read in sunlight
- **Intuitive interface** - no marine electronics experience required
- **AI-guided setup** - wizard walks you through configuration

### ✅ Powerful & Reliable
- **Professional-grade monitoring** - used by commercial operators
- **Proven platform** - based on reliable Raspberry Pi hardware
- **Active development** - regular updates and new features
- **Community support** - helpful user community

### ✅ Future-Proof
- **Modular design** - add features as needed
- **Open standards** - NMEA2000, Signal K, OpenCPN
- **Regular updates** - new features added quarterly
- **Expandable** - supports custom integrations

---

## Coming Soon

### Planned Features:
- **Marine Vision Phase 2** - Fish species identification and regulations
- **Marine Vision Phase 3** - Forward collision avoidance
- **Anchor watch** - GPS-based anchor drag alerts
- **Route planning** - Integration with popular chartplotters
- **Fuel consumption tracking** - Range prediction and efficiency analysis
- **Social features** - Share catches and routes with friends (opt-in)
- **Weather routing** - Optimal route suggestions based on forecasts
- **Integration with marine marketplaces** - Order parts directly from system

---

## Technical Specifications Summary

| Specification | Details |
|--------------|---------|
| **Processor** | Raspberry Pi 4B (4GB or 8GB RAM) |
| **Display** | 10.1" 1920×1200 IPS, 1000 nit, capacitive touch |
| **Storage** | 32GB SD + 128GB USB (recommended) |
| **Network** | WiFi 802.11ac, Gigabit Ethernet, NMEA2000 |
| **Voice** | Offline AI, wake word detection, natural language |
| **Camera** | IP67 waterproof, 4K/1080p, night vision (optional) |
| **Power** | 12V DC input, 10W typical, 15W peak |
| **Operating Temp** | 0°C to 50°C (32°F to 122°F) |
| **Software** | Raspberry Pi OS (Debian), Signal K, Node-RED, OpenCPN |
| **Interface** | Browser-based (Chromium) |

---

## Get Started

### Option 1: DIY Build (Tier 0 - FREE)
1. Download d3kOS image from GitHub
2. Flash to 32GB+ SD card using Raspberry Pi Imager
3. Assemble hardware (Pi 4B + PiCAN-M + touchscreen)
4. Boot and complete onboarding wizard
5. Start monitoring your engine!

### Option 2: Complete Kit (d3-k1)
1. Purchase pre-assembled d3-k1 system
2. Install on boat and connect to NMEA2000
3. Power on and complete onboarding wizard
4. Everything ready to go!

### Option 3: Professional Installation
1. Contact certified installer
2. Full system integration with existing marine electronics
3. Custom configuration and training
4. Ongoing support options

---

## Support & Community

- **Documentation:** Full user manual and technical specs at GitHub
- **Community Forum:** Active user community for questions and tips
- **Video Tutorials:** Step-by-step installation and setup guides
- **Email Support:** Priority email support for Tier 2+ subscribers
- **Commercial Support:** Custom integration for Tier 3 fleet operators

---

## About d3kOS

d3kOS is developed by boating enthusiasts for boating enthusiasts. Our mission is to make professional-grade marine electronics accessible to everyone, whether you're a weekend sailor or a commercial operator.

**Built on open standards. Powered by open source. Designed for the open water.**

---

*Version 2.7 - February 2026*
*For the latest updates, visit our GitHub repository*
*Patent Pending - d3kOS Marine Helm Control System*
