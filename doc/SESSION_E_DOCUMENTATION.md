# Session E: Documentation & User Guides

**Estimated Time:** 4-6 hours
**Domain:** Documentation (Domain 5)
**Priority:** Medium
**Status:** Ready to start

---

## Overview

Create comprehensive user documentation for d3kOS system:
1. System Administrator Guide
2. Hardware Installation Guide
3. Onboarding Wizard User Guide
4. Troubleshooting Guide
5. Quick Start Guide

**Completed Guides:**
- ✅ AI Assistant User Guide (20KB)
- ✅ Marine Vision API Documentation (32KB)

---

## Guide 1: System Administrator Guide (2 hours)

**Audience:** System administrators, developers
**File:** `/home/boatiq/Helm-OS/doc/SYSTEM_ADMIN_GUIDE.md`
**Length:** ~10-15KB

### Contents:

#### 1. System Architecture
- Service overview (all d3kOS services)
- Port assignments (8080-8094)
- Data directories
- Configuration files

#### 2. Service Management
```bash
# Start/stop services
sudo systemctl start d3kos-voice
sudo systemctl stop d3kos-export-manager
sudo systemctl restart d3kos-tier-manager

# Enable/disable auto-start
sudo systemctl enable d3kos-camera-stream
sudo systemctl disable d3kos-voice

# Check status
systemctl status d3kos-ai-api
journalctl -u d3kos-fish-detector -n 50
```

#### 3. Configuration Management
- License.json structure and location
- Tier detection configuration
- Wake word threshold adjustment
- API endpoint configuration

#### 4. Backup & Restore
- Critical files to backup
- Database backup commands
- Configuration export/import
- System image creation

#### 5. Network Configuration
- Port forwarding for remote access
- VPN setup for security
- Nginx proxy configuration
- Firewall rules

#### 6. Performance Tuning
- Signal K cache settings
- AI response optimization
- Camera stream quality
- Database optimization

#### 7. Security Best Practices
- SSH key management
- Service isolation
- API authentication
- File permissions

---

## Guide 2: Hardware Installation Guide (1.5 hours)

**Audience:** Boat owners installing d3kOS
**File:** `/home/boatiq/Helm-OS/doc/HARDWARE_INSTALLATION_GUIDE.md`
**Length:** ~8-10KB

### Contents:

#### 1. Bill of Materials
- Raspberry Pi 4B (8GB recommended)
- SD card (32GB minimum, 128GB recommended)
- Touchscreen display
- Anker S330 conference speaker/mic
- Reolink RLC-810A camera
- CX5106 NMEA2000 gateway
- Power supply, cables, mounting hardware

#### 2. Physical Installation
- Mounting Pi in helm station
- Touchscreen positioning (eye level, arm's reach)
- Anker S330 placement (clear voice path)
- Camera mounting (360° searchlight or fixed)
- Cable routing and strain relief

#### 3. Network Wiring
- Ethernet connection to CX5106
- WiFi configuration for internet
- Network topology diagram
- IP address assignments

#### 4. Power Supply
- 12V DC to 5V USB-C converter
- Wire gauge recommendations
- Fuse/breaker sizing
- Clean power considerations

#### 5. NMEA2000 Integration
- CX5106 connection to N2K backbone
- Terminator resistors
- Bus power considerations
- Troubleshooting connection issues

#### 6. Initial System Setup
- Flash SD card with d3kOS image
- First boot process
- WiFi configuration
- Onboarding wizard

---

## Guide 3: Onboarding Wizard User Guide (1 hour)

**Audience:** End users during first setup
**File:** `/home/boatiq/Helm-OS/doc/ONBOARDING_USER_GUIDE.md`
**Length:** ~6-8KB

### Contents:

#### 1. Welcome (Step 1)
- What is d3kOS
- What to expect during setup
- Time required (~10 minutes)

#### 2. Boat Information (Steps 2-5)
- Why we need boat details
- Examples of manufacturer/model
- Chartplotter selection
- "I don't know" options

#### 3. Engine Specifications (Steps 6-15)
- Why engine details matter
- How to find engine specs
- Reasonable defaults if unknown
- Impact on dashboard accuracy

#### 4. Regional Settings (Steps 16-17)
- Boat origin (for regulations)
- Engine position (affects CX5106 mapping)

#### 5. Configuration Review (Step 18)
- Verify all entered information
- Edit if needed
- Importance of accuracy

#### 6. DIP Switch Configuration (Step 19)
- What are DIP switches
- Reading the diagram
- Setting switches on CX5106
- Why this step is critical

#### 7. QR Code & Mobile Pairing (Step 20)
- Scan QR code with mobile app
- Installation ID explained
- What happens next
- Troubleshooting scan issues

#### 8. Completion
- System is ready
- Main menu tour
- Where to find help

---

## Guide 4: Troubleshooting Guide (1 hour)

**Audience:** Users experiencing issues
**File:** `/home/boatiq/Helm-OS/doc/TROUBLESHOOTING_GUIDE.md`
**Length:** ~8-10KB

### Contents:

#### 1. Common Issues

**Touchscreen Not Working**
- Check for active voice service
- Reboot system
- Check Wayland/Squeekboard logs
- Verify input group membership

**Voice Not Responding**
- Check microphone connection
- Test audio levels: `arecord -D plughw:3,0 -d 2 /tmp/test.wav`
- Check PipeWire interference
- Verify wake word threshold
- Review voice service logs

**No Engine Data**
- Verify CX5106 connection
- Check NMEA2000 bus power
- Test Signal K connection
- Review can0 interface status
- Check DIP switch settings

**Export Failed**
- Check tier level (Tier 1+ required)
- Verify internet connection
- Check export service logs
- Test API endpoint manually

**Camera Not Streaming**
- Ping camera: `ping 10.42.0.100`
- Check RTSP URL
- Verify camera power
- Test with VLC directly
- Review camera service logs

#### 2. Diagnostic Commands
```bash
# System status
systemctl status d3kos-*
df -h  # Storage
free -h  # Memory
top  # CPU usage

# Network
ip addr show
ping -c 3 8.8.8.8
curl http://localhost:8091/license/info

# Audio
arecord -l
amixer -c 3 contents
pactl list sources

# Logs
journalctl -u d3kos-voice -n 50
tail -100 /var/log/nginx/error.log
```

#### 3. Getting Help
- GitHub issues
- Community forum
- Email support
- Include logs and system info

---

## Guide 5: Quick Start Guide (30 minutes)

**Audience:** New users, quick reference
**File:** `/home/boatiq/Helm-OS/doc/QUICK_START_GUIDE.md`
**Length:** ~4-5KB

### Contents:

#### 1. First Boot
- Power on
- Wait for boot (~30 seconds)
- Onboarding wizard starts automatically

#### 2. Main Menu Overview
- Dashboard - Engine metrics
- Helm - AI assistant chat
- Boatlog - Logging and notes
- Weather - Radar and forecast
- Navigation - GPS and charts
- Settings - System configuration
- Marine Vision - Camera and fish detection
- AI Assistant - Voice commands

#### 3. Voice Commands
- Say "Helm" to activate
- Example queries:
  - "What's the RPM?"
  - "Show me fuel level"
  - "What's the engine temperature?"
- Wait for "Aye Aye Captain" response

#### 4. Touchscreen Tips
- Tap input fields to show on-screen keyboard
- Use "Main Menu" button to navigate back
- Fullscreen toggle for keyboard access
- Swipe gestures not supported

#### 5. Daily Use
- Check dashboard before starting engine
- Monitor alerts
- Log interesting events in boatlog
- Review marine vision captures

#### 6. Maintenance
- Weekly: Review logs
- Monthly: Export data backup
- Seasonal: Clean camera lens
- Annual: Update system

---

## Documentation Standards

### Formatting:
- Markdown format (.md files)
- Clear headings (H1, H2, H3)
- Code blocks with syntax highlighting
- Tables for comparisons
- Bullet points for lists

### Style:
- Active voice ("Click the button" not "The button should be clicked")
- Simple language (avoid jargon)
- Step-by-step instructions
- Include screenshots/diagrams (describe if not available)
- Examples for clarity

### Structure:
- Table of contents for long documents
- Sections with clear headings
- Quick reference at top
- Detailed explanations below
- Related links at bottom

---

## Testing Documentation

**Checklist:**
- [ ] All commands tested and verified
- [ ] No broken links
- [ ] Code examples copy-paste ready
- [ ] Clear and easy to follow
- [ ] Reviewed for technical accuracy
- [ ] Spell check completed

---

## Files to Create

1. `/home/boatiq/Helm-OS/doc/SYSTEM_ADMIN_GUIDE.md` (~15KB)
2. `/home/boatiq/Helm-OS/doc/HARDWARE_INSTALLATION_GUIDE.md` (~10KB)
3. `/home/boatiq/Helm-OS/doc/ONBOARDING_USER_GUIDE.md` (~8KB)
4. `/home/boatiq/Helm-OS/doc/TROUBLESHOOTING_GUIDE.md` (~10KB)
5. `/home/boatiq/Helm-OS/doc/QUICK_START_GUIDE.md` (~5KB)

**Total:** ~48KB of documentation

---

## Time Breakdown

- System Admin Guide: 2 hours
- Hardware Installation Guide: 1.5 hours
- Onboarding User Guide: 1 hour
- Troubleshooting Guide: 1 hour
- Quick Start Guide: 30 minutes

**Total: 4-6 hours**

---

## Success Criteria

✅ 5 comprehensive guides created
✅ All commands tested
✅ Clear, easy to understand
✅ Covers common user scenarios
✅ Professional quality

---

**Ready to start Session E!**
