# d3kOS v1.0.3 Release Notes

**Release Date**: February 18, 2026
**Version**: 1.0.3
**Previous Version**: 1.0.2 (February 14, 2026)
**Download**: https://github.com/SkipperDon/d3kos/releases/tag/v1.0.3

---

## 📦 Download

**Image File**: `d3kos-v1.0.3.img.gz` (~4GB compressed, ~16GB uncompressed)
**Checksum File**: `d3kos-v1.0.3.img.gz.sha256`

**IMPORTANT**: Always verify checksum before flashing to prevent corrupted installation.

```bash
# Download
wget https://github.com/SkipperDon/d3kos/releases/download/v1.0.3/d3kos-v1.0.3.img.gz
wget https://github.com/SkipperDon/d3kos/releases/download/v1.0.3/d3kos-v1.0.3.img.gz.sha256

# Verify
sha256sum -c d3kos-v1.0.3.img.gz.sha256
# Expected: d3kos-v1.0.3.img.gz: OK
```

---

## 🎯 What's New

### Installation ID System (File-Based Persistence)

**Problem Solved**: Old installation IDs stored in browser localStorage were lost when cache cleared.

**New System**:
- **16-character hex format** (e.g., `3861513b314c5ee7`)
- **Generated from SHA-256** hash of MAC address + timestamp
- **Stored in file**: `/opt/d3kos/config/license.json`
- **Survives browser cache clears**
- **Generated on first boot** (before Initial Setup wizard)

**License API Service** (port 8091):
- `GET /license/info` - Basic license information (installation_id, tier, features)
- `GET /license/full` - Complete license.json contents

**QR Code Simplified**:
- **Old**: 170-character JSON (UUID, pairing token, API endpoint, tier)
- **New**: 16-character plain text (just installation_id)
- **Colors**: Standard black-on-white (was green-on-black)
- **Size**: 400×400px (was 300×300)
- **Easier mobile scanning**: All major phone cameras can now read QR code

---

### Tier System (Feature Licensing)

**4-Tier Licensing Model** to support sustainable development:

| Feature | Tier 0 (FREE) | Tier 1 (FREE) | Tier 2 ($9.99/mo) | Tier 3 ($99.99/yr) |
|---------|---------------|---------------|-------------------|-------------------|
| Dashboard | ✓ | ✓ | ✓ | ✓ |
| Boat log | 30 days | 60 days | 90 days | Unlimited |
| Initial Setup resets | 10 max | 10 max | Unlimited | Unlimited |
| Mobile app pairing | ❌ | ✓ | ✓ | ✓ |
| Data export | ❌ | ✓ | ✓ | ✓ |
| Voice assistant | ❌ | ❌ | ✓ | ✓ |
| Camera | ❌ | ❌ | ✓ | ✓ |
| Cloud sync | ❌ | ❌ | ❌ | ✓ |
| Multi-boat | ❌ | ❌ | ❌ | ✓ |

**Auto-Upgrade to Tier 2** (FREE):
- Installing OpenCPN automatically upgrades system to Tier 2
- No payment required
- Unlocks voice assistant and camera features
- Supports open-source marine software

**Tier Detection Service** (port 8093):
- Checks OpenCPN installation every 24 hours
- Updates tier automatically
- `GET /tier/status` - Get current tier and features

**Tier Management Service** (boot-time):
- Runs on every boot
- Detects tier and enables/disables features
- Logs: `journalctl -u d3kos-tier-manager`

---

### Data Export System (Central Database Sync)

**8 Export Categories**:
1. Engine benchmark data
2. Boatlog entries (voice, text, auto, weather)
3. **Marine vision captures** (metadata only - no image files)
4. **Marine vision snapshots** (metadata only - no video files)
5. QR code data
6. Settings configuration
7. System alerts
8. **Onboarding/Initial Setup Configuration** (all 20 wizard answers, reset counter)

**Export Format**: JSON with installation_id, timestamp, tier, format_version

**Export Manager Service** (port 8094):
- `POST /export/generate` - Create export file
- `GET /export/status` - Check export eligibility (tier check)
- `POST /export/upload` - Upload to central database
- `GET /export/history` - List previous exports

**Automatic Export**:
- **Boot-time**: Checks export queue, uploads pending exports
- **Retry logic**: 3 attempts (immediate, 5min, 15min delay)
- **Queue file**: `/opt/d3kos/data/exports/export_queue.json`

**Tier Requirement**: Tier 1+ only (Tier 0 has NO export capability)

**IMPORTANT**: Marine vision media files (photos, videos) are NOT exported to central database. Only metadata is sent. Actual media files transferred via Tier 1/2/3 mobile app.

---

### Marine Vision Telegram Notifications (Tier 2+)

**Instant Fish Capture Alerts**:
- Auto-sends Telegram notification when fish detected
- Photo uploaded to Telegram (up to 10MB)
- Message includes: species, confidence, GPS coordinates, Google Maps link, fishing regulations
- Queue and retry system (3 attempts, 5s delay)

**Notification Manager Service** (port 8088):
- `POST /notify/send` - Send notification (text or fish capture with photo)
- `POST /notify/test` - Send test notification
- `GET /notify/status` - Service status and configuration
- `POST /notify/config` - Update bot token, chat ID, enable/disable
- `GET /notify/failed` - List failed notifications

**Settings UI**: Settings → Telegram → Configure bot token and chat ID

**Setup Steps**:
1. Create Telegram bot via @BotFather
2. Get bot token (format: `110201543:AAHdqTcvCH1...`)
3. Get chat ID (via `curl https://api.telegram.org/bot<TOKEN>/getUpdates`)
4. Configure in d3kOS: Settings → Telegram
5. Test: Click "Send Test Notification"

---

### Voice/AI Performance Optimization (132× Faster!)

**Signal K Data Caching**:
- **Old**: Fetched fresh data from Signal K on every query (~18 seconds)
- **New**: 3-second cache (subsequent queries: 0.17-0.22 seconds)
- **Speedup**: 132× faster for cached queries!

**Expanded Rule-Based Patterns** (13 instant responses):
- rpm, oil, temperature, fuel, battery, speed, heading, boost, hours, location, time, help, status
- Response time: 0.17-0.22s (cached), 18s (first query)

**Phi-2 LLM Removed**:
- Phi-2 was too slow (60-180 seconds response time)
- Removed to simplify system and free 1.7GB storage
- Onboard mode now uses rule-based responses only
- Complex queries require internet connection (OpenRouter)

**Smart Data Fetching**:
- `time` and `help` queries skip boat data fetch (instant response)
- `location` queries fetch GPS only (lightweight, 2s timeout)
- All other queries fetch full boat status

**Persistent Query Handler**:
- Handler instance survives across API requests (cache persists)
- Reduced memory overhead (no repeated initialization)

---

### GPS Configuration Fix

**Problem**: GPS position not flowing to Signal K, continuous errors.

**Root Cause**: Both gpsd and Signal K tried to read `/dev/ttyACM0` simultaneously (serial device can only be read by one process).

**Solution**:
1. Configure gpsd with `DEVICES="/dev/ttyACM0"` in `/etc/default/gpsd`
2. Configure Signal K to use gpsd protocol (localhost:2947) instead of direct serial
3. Zero latitude errors (was 100+ errors/minute)

**GPS Now Working**:
- Position: 43.6866°N, 79.5196°W (example)
- Navigation page displays GPS data correctly
- Signal K receiving GPS data via gpsd

**GPS Drift Explanation**:
- Indoor GPS: 3 satellites, HDOP 3.57 → ±10-30m accuracy
- Position "wanders" within error circle (appears as 2 knots speed)
- **This is normal GPS behavior with weak signals**
- Expected outdoors: 8+ satellites, HDOP <2.0, 0 knots when stationary

---

### UI Fixes

**Export Manager**:
- Fixed nginx proxy port (8090 → 8094)
- Added `/export/status` endpoint
- Settings → Data Management page now loads correctly

**QR Code**:
- Simplified to plain text (16-char installation ID)
- Changed to standard black-on-white colors
- Increased size to 400×400px
- Mobile phones easily scan and display ID

**AI Assistant Page**:
- Restored from Feb 13 backup (fullscreen toggle removed)
- On-screen keyboard now works
- Fixed WebSocket connection error

**Weather Radar**:
- Added default GPS position (Lake Simcoe) when no GPS fix
- Fixed null handling for inland locations (marine API returns null for lakes)
- Auto-fetch on page load

**Navigation Page**:
- Fixed WebSocket URL (localhost → window.location.hostname)
- GPS data now displays correctly

**Onboarding Wizard**:
- Auto-focus added to first input field (fixes keyboard not appearing)

**Helm Assistant**:
- Auto-focus added to textarea (500ms delay)

---

### vcan0 Simulator Error Fixed

**Problem**: Repeating error after system reboot:
```
unable to open canbus vcan0: Error: Error while creating channel
Will retry connection in 5 seconds...
```

**Root Cause**: vcan0-simulator provider was re-enabled in Signal K settings after reboot, but vcan0 interface doesn't exist.

**Solution**: Disabled vcan0-simulator in Signal K settings (`~/.signalk/settings.json`).

**Result**: Zero vcan0 errors. Signal K running cleanly with can0 (real engine data) only.

---

## ⚠️ Breaking Changes

### 1. Installation ID Format Changed

**Impact**: Old installation IDs (12-char random, browser localStorage) discarded. New 16-char hex ID generated on upgrade.

**Action Required**:
- **Tier 1+ users**: Re-pair mobile app (scan new QR code in Settings)
- **Tier 0 users**: Complete Initial Setup wizard again (or restore from backup)

### 2. Tier System Enforced

**Impact**: Voice assistant and camera now restricted to Tier 2+.

**What This Means**:
- **Tier 0/1 users**: Voice assistant and camera features DISABLED
- **Tier 2 users**: All features remain enabled
- **Upgrade to Tier 2 (FREE)**: Install OpenCPN (auto-detects and upgrades)
- **Upgrade to Tier 2 (Paid)**: Purchase subscription ($9.99/month)

**Check Your Tier**:
```bash
# Via web interface
Settings → System → License Information

# Via SSH
cat /opt/d3kos/config/license.json | grep '"tier"'
```

### 3. Export Capability Tier-Locked

**Impact**: Tier 0 users can NO LONGER export data.

**Tier 1+ users**: Export functionality available
**Tier 0 users**: Must upgrade to Tier 1+ to enable export

---

## 🐛 Known Issues

### 1. **CRITICAL: Voice Assistant Wake Word Detection Not Working**

**Status**: Under investigation
**Affected**: All Tier 2+ users
**Tracking**: GitHub Issue #TBD

**Symptoms**:
- Voice service running (d3kos-voice.service active)
- Microphone captures audio (arecord works)
- Wake words not detected ("helm", "advisor", "counsel")
- No "Aye Aye Captain" response

**Root Cause** (Suspected):
- PipeWire audio server reduces microphone signal by 17× (0.18% vs 3.1% direct)
- PocketSphinx subprocess integration fragile
- Python script can't reliably read PocketSphinx stdout

**Workaround**:
- **Use text-based AI Assistant instead**
- Navigate to: http://d3kos.local/ai-assistant.html
- Type questions: "What's the RPM?", "What's the oil pressure?"
- Response time: 0.17-0.22s (cached), 6-8s (online)

**Next Steps** (Future Update):
- Investigate alternative wake word engines (Vosk, Porcupine, Snowboy)
- Rebuild voice assistant from scratch
- Consider PulseAudio instead of PipeWire

**ETA**: Unknown - requires dedicated 2-3 hour debugging session

---

### 2. **Boatlog Export Button Crash**

**Affected**: All tiers
**Workaround**: Use Settings → Data Management → Export All Data Now
**Fix**: Scheduled for v1.0.4

---

### 3. **Charts Page Missing o-charts Addon**

**Affected**: Users without third-party chartplotters
**Workaround**: Manually install o-charts plugin and charts via OpenCPN
**Fix**: Auto-install planned for v1.0.5

---

### 4. **GPS Drift Indoors**

**Status**: Expected behavior
**Explanation**: Weak satellite signals (3 satellites, HDOP 3.57) cause position "wander" within ±10-30m error circle. GPS thinks it's moving as position drifts.
**Recommendation**: Use GPS outdoors for accurate position (8+ satellites, HDOP <2.0)

---

### 5. **Small SD Card Storage Warnings**

**Affected**: Users with 16GB SD cards
**Recommendation**: Upgrade to 128GB SD card for camera recordings and system logs
**Workaround**: Automatic media cleanup after 7 days, manual cleanup in Settings → Data Management

---

## 📈 Performance Improvements

**AI Assistant Response Time**:
- **Before**: 23 seconds (every query)
- **After**: 0.17-0.22 seconds (cached queries)
- **Speedup**: 132× faster!

**Storage Freed**:
- Removed Phi-2 LLM: 1.7GB
- APT cache cleanup: 131MB
- **Total freed**: 1.8GB
- **Before**: 96-97% full (456-537MB free)
- **After**: 85% full (2.2GB free)

**Service Count**:
- **Added**: 4 new services (license-api, tier-api, tier-manager, export-manager, notifications)
- **Total**: 13 d3kOS services running

---

## 🔧 Upgrade Instructions

### Upgrade Methods

**Method 1: SD Card Swap** (All Tiers - Recommended)
- Flash new image to spare SD card
- Swap cards
- Restore configuration (Tier 1+ via mobile app)
- **Duration**: 30-45 minutes
- **Risk**: Low (old SD card kept as backup)

**Method 2: In-Place Upgrade** (Tier 2/3 Only)
- Download update package via mobile app or web interface
- Run upgrade script
- Reboot
- **Duration**: 10-15 minutes
- **Risk**: Medium (backup required)

**⚠️ IMPORTANT**: Tier 0/1 users MUST use Method 1 (in-place upgrades disabled for Tier 0/1).

**See UPGRADE_GUIDE.md for detailed step-by-step instructions.**

---

### Pre-Upgrade Checklist

✅ Read this release notes document completely
✅ Read UPGRADE_GUIDE.md
✅ Check current version: `cat /opt/d3kos/version.txt`
✅ Backup configuration: `/opt/d3kos/scripts/backup.sh`
✅ Verify tier: `cat /opt/d3kos/config/license.json | grep tier`
✅ Understand breaking changes (installation ID, tier system)
✅ Plan for re-pairing mobile app (new QR code)

---

### Post-Upgrade Verification

After upgrading, verify:

✅ Version shows 1.0.3: Settings → System → About
✅ Installation ID generated: Settings → System → License Information
✅ Tier detected correctly (should auto-detect OpenCPN if installed)
✅ Services running: `sudo systemctl status d3kos-*`
✅ Dashboard displays engine data (if CX5106 connected)
✅ GPS position displays: Navigation page
✅ AI Assistant responds: Type "What's the RPM?" in AI Assistant page
✅ Export works (Tier 1+): Settings → Data Management → Export All Data Now

**If Tier 0**: Install OpenCPN to unlock Tier 2 features (FREE upgrade):
```bash
sudo apt-get update
sudo apt-get install opencpn
```

---

## 📚 New Documentation

**Distribution Documentation** (10 files):
1. **README.md** - Project overview, quick start, feature summary
2. **INSTALLATION_GUIDE.md** - Complete installation walkthrough
3. **TROUBLESHOOTING_GUIDE.md** - Common issues and solutions (10+ scenarios)
4. **HARDWARE_SETUP_GUIDE.md** - BOM, wiring diagrams, assembly
5. **UPGRADE_GUIDE.md** - SD card swap and in-place upgrade procedures
6. **CHANGELOG.md** - Version history (1.0.0 → 1.0.3)
7. **LICENSE.txt** - d3kOS + 32 third-party licenses
8. **RELEASE_NOTES_v1.0.3.md** - This document
9. **GITHUB_RELEASE_TEMPLATE.md** - Release format for GitHub

**User Guides**:
- AI_ASSISTANT_USER_GUIDE.md (20KB, 663 lines) - Text and voice AI usage
- MARINE_VISION_API.md (32KB, 1,228 lines) - Developer API reference
- MARINE_VISION_NOTIFICATION_INTEGRATION.md (12KB) - Telegram setup
- MARINE_VISION_NOTIFICATION_TESTING.md (16KB, 25 tests)

**Total Documentation**: ~200 pages, ~50,000 words

---

## 🔐 Security

**Default Credentials** (CHANGE IMMEDIATELY):

| Component | Username | Password |
|-----------|----------|----------|
| System User | `d3kos` | `d3kos2026` |
| SSH Access | `d3kos` | `d3kos2026` |
| WiFi AP | SSID: `d3kOS` | `d3kos-2026` |
| Web Interface | http://d3kos.local | (no auth) |

**Change Password**:
```bash
ssh d3kos@d3kos.local
passwd
# Enter current: d3kos2026
# Enter new: [your secure password]
# Confirm new: [your secure password]
```

**Change WiFi Password**: Settings → Network → Change WiFi Password

---

## 🙏 Acknowledgments

- **Signal K Project** - Marine data standards
- **Node-RED Community** - Automation platform
- **OpenCPN Project** - Chart plotting software
- **Anthropic** - Claude AI development assistance
- **Raspberry Pi Foundation** - Affordable computing
- **SkipperDon** - Project creator and maintainer
- **At My Boat Community** - Beta testing and feedback

---

## 📞 Support

**Documentation**:
- README.md - Project overview
- INSTALLATION_GUIDE.md - Setup instructions
- TROUBLESHOOTING_GUIDE.md - Common issues
- UPGRADE_GUIDE.md - Version migration

**Community**:
- GitHub Issues: https://github.com/SkipperDon/d3kos/issues (bugs)
- GitHub Discussions: https://github.com/SkipperDon/d3kos/discussions (Q&A)
- At My Boat: https://atmyboat.com (blog, stories, guides)

**Commercial Support**:
- Tier 3 subscribers: Direct email support (24-hour response)
- Tier 2: Priority response on GitHub (48 hours)
- Tier 0/1: Community support via GitHub

---

## 🚀 What's Next?

**Planned for v1.0.4** (March 2026):
- Fix boatlog export button crash
- Voice assistant debugging session (wake word detection)
- Network status labels color fix
- Additional tier system features

**Planned for v1.0.5** (April 2026):
- Auto-install o-charts addon for OpenCPN
- Marine Vision custom fish detection model
- Enhanced Telegram notifications (multi-user, groups)

**Planned for v1.1.0** (Q2 2026):
- E-commerce integration (Stripe billing)
- Mobile app In-App Purchases (Apple, Google)
- Advanced AI self-healing system
- Predictive maintenance

**Planned for v2.0.0** (Q3 2026):
- Major UI redesign
- New hardware platform support (Pi 5)
- Breaking changes expected

---

## 📄 License

d3kOS v1.0.3 is released under:
- **d3kOS Core**: MIT License
- **Third-Party Components**: Various (see LICENSE.txt)

**IMPORTANT AGPL-3.0 NOTICE** (YOLOv8):
If you provide d3kOS as a network service (e.g., SaaS), you MUST release your modifications under AGPL-3.0. This is a requirement of the YOLOv8 license.

For commercial use or proprietary modifications of YOLOv8 components, contact Ultralytics for a commercial license.

---

## 🔗 Links

- **Repository**: https://github.com/SkipperDon/d3kos
- **Releases**: https://github.com/SkipperDon/d3kos/releases
- **Download v1.0.3**: https://github.com/SkipperDon/d3kos/releases/tag/v1.0.3
- **Website**: https://atmyboat.com
- **Issues**: https://github.com/SkipperDon/d3kos/issues
- **Discussions**: https://github.com/SkipperDon/d3kos/discussions

---

**Happy Boating! ⚓**

**d3kOS v1.0.3** - Marine Helm Control System
Released February 18, 2026
Maintained by SkipperDon (https://atmyboat.com)
