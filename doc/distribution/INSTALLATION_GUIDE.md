# d3kOS Installation Guide

**Version**: 1.0.3
**Platform**: Raspberry Pi 4B (4GB/8GB RAM)
**Estimated Time**: 30-45 minutes (first-time installation)

---

## 📋 Table of Contents

1. [Before You Begin](#before-you-begin)
2. [Download Image](#download-image)
3. [Verify Checksum](#verify-checksum)
4. [Flash SD Card](#flash-sd-card)
5. [Hardware Assembly](#hardware-assembly)
6. [First Boot](#first-boot)
7. [Initial Setup Wizard](#initial-setup-wizard)
8. [Post-Installation](#post-installation)
9. [Verification Tests](#verification-tests)

---

## 1. Before You Begin

### Required Hardware

✅ **Raspberry Pi 4 Model B** (4GB or 8GB RAM)
✅ **PiCAN-M HAT** (NMEA2000 interface)
✅ **10.1" Touchscreen** (1920×1200 IPS recommended, HDMI + USB)
✅ **MicroSD Card** (32GB minimum, 128GB recommended, Class 10 A2)
✅ **USB GPS Receiver** (VK-162 or compatible)
✅ **USB Speaker** (Anker PowerConf S330 or compatible, for voice)
✅ **12V to 5V DC Converter** (Victron Orion-Tr 12/12-9 or similar, 3A minimum)
✅ **NMEA2000 Backbone** (existing boat network)
✅ **CX5106 Engine Gateway** (analog sensor to NMEA2000 converter)

**Optional**:
- USB AIS Receiver (dAISy or compatible)
- Reolink RLC-810A IP Camera (4K/1080p, IP67, night vision)
- Enclosure (custom 3D-printed or waterproof case)

### Required Software

✅ **Raspberry Pi Imager** (v1.8+) - Download: https://www.raspberrypi.com/software/
✅ **SD Card Reader** (built-in or USB)
✅ **Computer** (Windows, macOS, or Linux)
✅ **Web Browser** (Chrome, Firefox, Safari, Edge)
✅ **WiFi-enabled device** (laptop, phone, or tablet for first setup)

**Optional**:
- SSH client (for advanced configuration)
- VNC viewer (for remote desktop access)

### Recommended Tools

- Small Phillips screwdriver (for GPIO header assembly)
- Multimeter (for voltage verification)
- Wire strippers (for power wiring)
- Heat-shrink tubing or electrical tape (for insulation)
- 3D printer or marine adhesive (for enclosure mounting)

---

## 2. Download Image

### Step 2.1: Download from GitHub Releases

Visit the d3kOS releases page:
```
https://github.com/SkipperDon/d3kos/releases/tag/v1.0.3
```

Download two files:
1. **d3kos-v1.0.3.img.gz** (~4GB compressed, ~16GB uncompressed)
2. **d3kos-v1.0.3.img.gz.sha256** (checksum file)

**Command-Line Download** (Linux/macOS):
```bash
# Download image
wget https://github.com/SkipperDon/d3kos/releases/download/v1.0.3/d3kos-v1.0.3.img.gz

# Download checksum
wget https://github.com/SkipperDon/d3kos/releases/download/v1.0.3/d3kos-v1.0.3.img.gz.sha256
```

**Browser Download** (Windows):
- Right-click each file → Save Link As...
- Save to a known location (e.g., `Downloads` folder)

### Step 2.2: Download Time

| Connection Speed | Download Time (4GB) |
|------------------|---------------------|
| 10 Mbps | ~60 minutes |
| 25 Mbps | ~25 minutes |
| 50 Mbps | ~12 minutes |
| 100 Mbps | ~6 minutes |
| 500 Mbps | ~1 minute |

**Tip**: Download overnight if on slow connection. Browser download can be resumed if interrupted.

---

## 3. Verify Checksum

**⚠️ CRITICAL**: Always verify the image checksum before flashing. Corrupted images cause boot failures and data corruption.

### Step 3.1: Verify on Linux/macOS

```bash
cd ~/Downloads  # Navigate to download folder

# Verify checksum
sha256sum -c d3kos-v1.0.3.img.gz.sha256

# Expected output:
# d3kos-v1.0.3.img.gz: OK
```

**If checksum fails**:
```
d3kos-v1.0.3.img.gz: FAILED
```
- Delete the .img.gz file
- Re-download from GitHub
- Verify again

### Step 3.2: Verify on Windows (PowerShell)

```powershell
cd $HOME\Downloads  # Navigate to download folder

# Calculate checksum
Get-FileHash d3kos-v1.0.3.img.gz -Algorithm SHA256

# Compare with checksum file (open in Notepad)
notepad d3kos-v1.0.3.img.gz.sha256
```

**Expected checksum** (example - actual checksum in .sha256 file):
```
a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456  d3kos-v1.0.3.img.gz
```

**If checksums don't match**: Re-download the image.

### Step 3.3: Why Checksum Verification Matters

- **Detects corrupted downloads** - Partial downloads, network errors
- **Prevents boot failures** - Corrupted images won't boot or cause crashes
- **Security** - Ensures image hasn't been tampered with
- **Saves time** - Catches issues before spending 30+ minutes on assembly

---

## 4. Flash SD Card

### Step 4.1: Insert SD Card

1. Insert microSD card into SD card reader
2. Connect reader to computer
3. Wait for computer to recognize the card
4. **⚠️ IMPORTANT**: Back up any existing data on the card - flashing will erase everything

### Step 4.2: Launch Raspberry Pi Imager

**Download**: https://www.raspberrypi.com/software/

**Launch**:
- **Windows**: Start Menu → Raspberry Pi Imager
- **macOS**: Applications → Raspberry Pi Imager
- **Linux**: `rpi-imager` (or run from Applications menu)

### Step 4.3: Configure Imager

**Choose Operating System**:
1. Click "Choose OS"
2. Scroll down → "Use custom"
3. Navigate to `d3kos-v1.0.3.img.gz`
4. Select the .img.gz file (no need to decompress)

**Choose Storage**:
1. Click "Choose Storage"
2. Select your SD card (e.g., "Generic - 128GB")
3. **⚠️ WARNING**: Double-check you selected the correct device - flashing erases all data

**Advanced Options** (⚙️ Gear Icon):
- **Do NOT modify settings** - d3kOS image is pre-configured
- Skip hostname, SSH, WiFi, locale settings

### Step 4.4: Flash Image

1. Click "Write"
2. Confirm warning: "All existing data on the SD card will be erased"
3. Enter computer password if prompted (admin privileges required)
4. Wait for flashing to complete (10-20 minutes for 128GB card)

**Progress**:
```
Writing... 23% (3.7 GB / 16 GB)
[==============                                ]
```

**Completion**:
```
Write Successful
Verifying... 100%
```

### Step 4.5: Eject SD Card

1. Click "Continue" in Raspberry Pi Imager
2. Wait for "You can now eject the SD card" message
3. Safely eject SD card:
   - **Windows**: Right-click drive → Eject
   - **macOS**: Drag drive to Trash
   - **Linux**: Unmount via file manager
4. Remove SD card from reader

---

## 5. Hardware Assembly

### Step 5.1: PiCAN-M HAT Installation

**⚠️ IMPORTANT**: Power off Raspberry Pi before installing HAT.

1. **Align PiCAN-M HAT**:
   - GPIO header on HAT aligns with 40-pin GPIO on Raspberry Pi
   - Ensure all 40 pins are aligned (double-check)

2. **Press HAT onto GPIO**:
   - Apply even pressure on both sides
   - Press firmly until HAT seats completely
   - HAT should be parallel to Raspberry Pi board

3. **Verify Installation**:
   - No GPIO pins visible above HAT
   - HAT sits flush on standoffs (if installed)
   - DB9 connector (NMEA2000) accessible on side

**See**: HARDWARE_SETUP_GUIDE.md for photos and detailed wiring

### Step 5.2: Touchscreen Connection

**HDMI**:
1. Connect micro-HDMI to HDMI cable (or adapter)
2. Plug into **HDMI0** port on Raspberry Pi (port closest to USB-C)
3. Connect other end to touchscreen HDMI input

**USB Touch**:
1. Connect USB-A to USB-B cable (included with touchscreen)
2. Plug USB-A end into Raspberry Pi USB 3.0 port (blue)
3. Plug USB-B end into touchscreen USB port

**Power** (touchscreen):
1. Connect touchscreen power adapter to wall outlet
2. Turn on touchscreen power switch
3. Adjust brightness and contrast if needed

### Step 5.3: GPS Receiver

1. Plug USB GPS receiver (VK-162) into Raspberry Pi USB port
2. Position GPS antenna near window or outside for best signal
3. Allow 2-5 minutes for GPS fix on first boot

**LED Indicator**:
- **Blinking red** - Searching for satellites
- **Solid red** - GPS fix acquired

### Step 5.4: Speaker (Anker S330)

**For Tier 2+ Voice Assistant**:
1. Plug Anker PowerConf S330 USB cable into Raspberry Pi
2. Turn on speaker power button
3. Set speaker volume to ~70% (adjust after first boot)
4. Speaker LED should show white (ready)

**Audio Configuration**:
- d3kOS auto-detects "Anker" or "S330" audio devices
- No manual configuration required
- Microphone auto-enabled for wake word detection

### Step 5.5: SD Card Installation

1. Orient SD card with contacts facing Raspberry Pi board
2. Gently insert into SD card slot until it clicks
3. Push card in until flush with board edge
4. **Do not force** - card should slide in smoothly

### Step 5.6: Power Connection

**⚠️ WARNING**: Verify voltage before connecting to Raspberry Pi.

**12V Boat Power → DC Converter → Raspberry Pi**:

1. **Input** (Boat 12V):
   - Connect boat 12V+ to DC converter input (+)
   - Connect boat ground to DC converter input (-)
   - Add inline fuse (5A) on 12V+ line
   - Use marine-grade wire (14 AWG minimum)

2. **Verify Output Voltage**:
   - Use multimeter to check DC converter output
   - Should be **5.0-5.2V DC**
   - If voltage is wrong, adjust converter or check wiring

3. **USB-C Power** (Raspberry Pi):
   - Connect DC converter output to USB-C power cable
   - **Option A**: Use Victron Orion-Tr with built-in USB output
   - **Option B**: Wire DC converter to USB-C breakout board

4. **Power On**:
   - Flip boat circuit breaker or switch
   - Raspberry Pi red LED should illuminate
   - Wait 10 seconds, then green LED should flash (booting)

**Power Specifications**:
- **Voltage**: 5.0-5.2V DC (USB-C PD not required)
- **Current**: 3A minimum (5V @ 3A = 15W)
- **Peak**: 5A during boot and camera recording
- **Idle**: 1-2A typical

---

## 6. First Boot

### Step 6.1: Boot Sequence

**Timeline**:
- **0s**: Power applied, red LED on
- **5s**: Green LED flashing (kernel boot)
- **15s**: Custom d3kOS splash screen appears (AtMyBoat.com logo)
- **30s**: Filesystem expansion (first boot only)
- **60s**: Chromium browser launches
- **75s**: Initial Setup wizard loads
- **90s**: System ready (total first boot time)

**What Happens Automatically**:
1. ✅ Filesystem expands to full SD card size
2. ✅ Unique installation ID generated (16-char hex)
3. ✅ License.json created (Tier 0 default)
4. ✅ Signal K server starts
5. ✅ Node-RED starts
6. ✅ gpsd starts (GPS processing)
7. ✅ Network services initialized
8. ✅ Ethernet enabled (if connected)
9. ✅ Chromium launches in kiosk mode
10. ✅ Initial Setup wizard auto-loads

### Step 6.2: Connect to WiFi Network

**⚠️ Note**: d3kOS connects TO WiFi networks (client mode), not AS a WiFi hotspot. BCM4345/6 hardware limitation prevents AP mode.

**Using Touchscreen** (Primary Method):
1. Touchscreen shows d3kOS main menu in Chromium
2. Navigate to: **Settings → Network Settings**
3. Tap **"Scan for Networks"**
4. Select your WiFi network from the list:
   - Home WiFi
   - Phone hotspot (iPhone/Android)
   - Starlink
   - Marina WiFi
   - Mobile hotspot
5. Tap network name to connect
6. Enter password using **on-screen keyboard**
7. Tap **"Connect"**
8. Wait for "Connected" confirmation
9. Note the IP address displayed (e.g., 192.168.1.237)

**Using SSH** (Alternative Method):
```bash
# From laptop on same network as your WiFi router
ssh d3kos@d3kos.local

# Scan for networks
nmcli device wifi list

# Connect to network
nmcli device wifi connect "Your-Network-Name" password "your-password"
```

**Network Information** (after connection):
- **IP Address**: Assigned by your WiFi router (DHCP)
- **Gateway**: Your router's IP
- **DNS**: Provided by your network
- **Access**: d3kOS is now accessible from any device on the same WiFi network

### Step 6.3: Access Web Interface

**Option 1: Hostname (Recommended)**:
```
http://d3kos.local
```

**Option 2: IP Address** (shown in Network Settings):
```
http://[IP-ADDRESS]
```
Example: `http://192.168.1.237`

**Option 3: Touchscreen** (Direct):
- Interface loads automatically on touchscreen
- No keyboard/mouse needed
- Fully touch-optimized

**Browser Compatibility**:
- ✅ Chrome/Chromium (recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ❌ Internet Explorer (not supported)

---

## 7. Initial Setup Wizard

**Duration**: 5-10 minutes
**Steps**: 20 total
**Required**: Yes (one-time setup)

### Step 7.1: Welcome Screen (Step 0)

```
┌────────────────────────────────────────┐
│  Welcome to d3kOS                      │
│  Marine Helm Control System            │
│                                        │
│  This wizard will collect information  │
│  about your boat and engine.           │
│                                        │
│  Estimated time: 5 minutes             │
│                                        │
│  [← Main Menu]      [Start Wizard →]  │
└────────────────────────────────────────┘
```

**Options**:
- **[Start Wizard →]** - Begin setup (recommended for first boot)
- **[← Main Menu]** - Skip wizard (not recommended - engine data won't display)

**Recommendation**: Click "Start Wizard →" on first boot.

### Step 7.2: Boat Information (Steps 1-4)

**Step 1: Boat Manufacturer**:
- Example: "Bayliner", "SeaRay", "Boston Whaler", "Custom Build"
- Free text input (touchscreen keyboard)

**Step 2: Boat Year**:
- Example: "2015", "2020"
- 4-digit year (1950-2026)

**Step 3: Boat Model**:
- Example: "242 Classic", "Sundancer 320", "18 Dauntless"
- Free text input

**Step 4: Chartplotter Detection**:
- Auto-detects if NMEA2000 chartplotter is connected
- Shows detected PGNs (129025, 129026, 129029)
- Options:
  - ✅ **I have a chartplotter** (auto-selected if navigation PGNs detected)
  - ❌ **I don't have a chartplotter** (auto-installs OpenCPN)

**Tip**: If you have a Garmin/Simrad/Raymarine chartplotter, wizard will auto-detect it. If not, d3kOS will install OpenCPN for you.

### Step 7.3: Engine Information (Steps 5-14)

**Step 5: Engine Manufacturer**:
- Dropdown list (Volvo Penta, MerCruiser, Yamaha, Honda, Suzuki, Mercury, OMC, Crusader, PCM, Indmar, etc.)
- Or type custom manufacturer

**Step 6: Engine Model**:
- Example: "5.7L V8", "F90", "4.3L MPI"
- Free text input

**Step 7: Engine Year**:
- 4-digit year (1970-2026)

**Step 8: Number of Cylinders**:
- Dropdown: 2, 3, 4, 6, 8, 12
- Used for baseline RPM calculations

**Step 9: Engine Displacement**:
- Example: "5.7L", "350 CID", "4300 cc"
- Free text (units optional)

**Step 10: Engine Horsepower**:
- Example: "350 HP", "260 HP"
- Used for fuel consumption estimates

**Step 11: Compression Ratio**:
- Example: "9.4:1", "10.0:1"
- Used for performance calculations

**Step 12: Idle RPM**:
- Example: "650", "800"
- Normal idle speed (engine warmed up)

**Step 13: Max RPM**:
- Example: "4800", "5500"
- Wide Open Throttle (WOT) RPM
- Used for anomaly detection (alerts if exceeded)

**Step 14: Engine Type**:
- Dropdown: Gasoline (carburetor), Gasoline (fuel injection), Diesel, Electric, Hybrid
- Used for fuel calculations

### Step 7.4: Regional Information (Steps 15-16)

**Step 15: Boat Origin**:
- Dropdown: Ontario, Quebec, British Columbia, Nova Scotia, Alberta, USA, Europe, Asia, Other
- Used for fishing regulations database

**Step 16: Engine Position**:
- Dropdown: Inboard, Outboard, Stern Drive, Jet Drive
- Used for display labels and calculations

### Step 7.5: Review & Completion (Steps 17-20)

**Step 17: Configuration Review**:
- Displays all 16 answers in table format
- Verify information before proceeding
- Click [← Back] to edit any answer

**Step 18: DIP Switch Configuration**:
```
CX5106 DIP Switch Settings
(Based on your engine configuration)

Switch 1 [ON ] - Engine Type: Gasoline (Fuel Injection)
Switch 2 [OFF] - Number of Cylinders: 8
Switch 3 [OFF] -
Switch 4 [ON ] - Idle RPM: 650
Switch 5 [ON ] - Max RPM: 4800
Switch 6 [OFF] - Compression Ratio: 9.4:1
Switch 7 [OFF] -
Switch 8 [OFF] - Reserved

Visual Diagram:
[█][░][░][█][█][░][░][░]
 1  2  3  4  5  6  7  8
```

**⚠️ IMPORTANT**: Write down this configuration! Required for CX5106 engine gateway setup.

**Step 19: Installation ID & QR Code**:
```
Installation ID: 3861513b314c5ee7

[QR CODE IMAGE]

Scan this QR code with the d3kOS mobile app
to pair your boat.
```

- Installation ID displayed (16-character hex)
- QR code generated (plain text: installation_id)
- Mobile app uses QR code for pairing

**Step 20: Completion**:
```
Setup Complete!

Your d3kOS system is ready to use.

[Return to Main Menu]
```

- Click [Return to Main Menu] to exit wizard
- Fullscreen mode restores automatically
- Main menu loads

**Data Saved**:
- `/opt/d3kos/config/onboarding.json` - All wizard answers
- `/opt/d3kos/config/license.json` - Installation ID, tier, reset count
- `/opt/d3kos/state/onboarding-reset-count.json` - Reset counter (0 after first completion)

---

## 8. Post-Installation

### Step 8.1: Change Default Password

**⚠️ SECURITY**: Change the default system password immediately.

```bash
# SSH into d3kOS
ssh d3kos@d3kos.local
# Password: d3kos2026

# Change password
passwd
# Enter current password: d3kos2026
# Enter new password: [your secure password]
# Confirm new password: [your secure password]
```

**Password Requirements**:
- Minimum 8 characters
- Mix of letters, numbers, symbols recommended
- Write down password - no password recovery!

### Step 8.2: Manage WiFi Networks

**Add Additional Networks**:
1. Navigate to Settings → Network Settings
2. Tap **"Scan for Networks"**
3. Select new network
4. Enter password using on-screen keyboard
5. Tap **"Connect"**
6. d3kOS will remember this network

**Switch Between Networks**:
1. Navigate to Settings → Network Settings
2. View current connection status
3. Tap **"Disconnect"** to disconnect from current network
4. Tap **"Scan for Networks"**
5. Select different saved or new network
6. Tap **"Connect"**

**Saved Networks**:
- d3kOS remembers all networks you've connected to
- Auto-reconnects to known networks when in range
- No need to re-enter passwords for saved networks

**Common Use Cases**:
- **Home**: Connect to home WiFi
- **Boat Launch**: Connect to phone hotspot for updates
- **On Water**: Connect to Starlink or cellular hotspot
- **Marina**: Connect to marina WiFi

**Network Settings Features** (Session F):
- Real-time signal strength display
- Connection status monitoring
- Saved network management
- Touch-optimized interface
- On-screen keyboard for passwords

### Step 8.3: Configure CX5106 Engine Gateway

**DIP Switch Configuration**:
1. Locate CX5106 unit on NMEA2000 backbone
2. Open CX5106 enclosure
3. Set DIP switches per wizard (Step 18)
4. Close enclosure
5. Restart CX5106 (power cycle)

**Sensor Wiring** (analog sensors to CX5106):
- **Oil Pressure**: Blue wire → oil pressure sender
- **Coolant Temp**: Green wire → temperature sender
- **Tachometer**: Yellow wire → tach signal (negative coil or alternator W terminal)
- **Ground**: Black wire → engine ground

**See**: CX5106_CONFIGURATION_GUIDE.md for detailed wiring diagrams

### Step 8.4: Verify NMEA2000 Connection

**From Web Interface**:
1. Navigate to Dashboard
2. Verify engine data appears:
   - RPM (should show 0 if engine off)
   - Oil Pressure (may show 0 or null)
   - Coolant Temperature (ambient temp)

**From SSH** (advanced):
```bash
# Check CAN interface
ifconfig can0

# Should show:
can0: flags=193<UP,RUNNING,NOARP>  mtu 16
      RX packets: 1234  errors: 0  dropped: 0
      TX packets: 0  errors: 0  dropped: 0

# Monitor CAN traffic
candump can0

# Should show PGN messages:
can0  18FEF200  [8] 00 FF FF FF FF FF FF FF
can0  18FEEE00  [8] FF FF FF FF FF FF FF FF
```

**If no CAN traffic**:
- Check NMEA2000 backbone power (12V)
- Verify PiCAN-M termination resistors (120Ω)
- Check DB9 cable wiring (CAN-H, CAN-L, Shield, Ground)

### Step 8.5: Mount and Secure Hardware

**Enclosure Mounting**:
1. Choose location at helm (within view of operator)
2. Ensure touchscreen is reachable from helm seat
3. Mount enclosure with marine-grade fasteners or adhesive
4. Route power and data cables cleanly

**Cable Management**:
- Use cable ties or conduit for organization
- Protect cables from chafing and moisture
- Label cables for future maintenance
- Allow service loops for removal

**Environmental Protection**:
- Keep Raspberry Pi and PiCAN-M in waterproof enclosure
- Vent enclosure to prevent condensation
- Add desiccant pack if needed
- Seal cable entry points

---

## 9. Verification Tests

### Test 1: System Boot
- ✅ Power on Raspberry Pi
- ✅ Red LED on immediately
- ✅ Green LED flashing after 5 seconds
- ✅ d3kOS splash screen appears after 15 seconds
- ✅ Web interface loads after 60-90 seconds

### Test 2: Network Connectivity
- ✅ WiFi AP visible (SSID: d3kOS)
- ✅ Connect to WiFi with password: d3kos-2026
- ✅ Access http://d3kos.local from browser
- ✅ Main menu loads

### Test 3: GPS Signal
- ✅ Navigate to Navigation page
- ✅ GPS status shows "GNSS Fix" or "2D Fix" or "3D Fix"
- ✅ Latitude/longitude displayed (e.g., 43.68°N, 79.52°W)
- ✅ Satellite count > 3

### Test 4: Engine Data (CX5106 connected)
- ✅ Navigate to Dashboard
- ✅ RPM displays (0 if engine off, >0 if running)
- ✅ Oil pressure displays (may be 0 if engine off)
- ✅ Temperature displays (ambient if engine off)

### Test 5: Touchscreen
- ✅ Tap navigation buttons on main menu
- ✅ Pages load correctly
- ✅ Tap input fields → on-screen keyboard appears
- ✅ Type text using on-screen keyboard

### Test 6: Voice Assistant (Tier 2+)
- ⚠️ **Known Issue**: Wake word detection currently not working
- **Workaround**: Use text-based AI Assistant instead
- Navigate to AI Assistant page
- Type "What's the RPM?" and press Send
- Verify response appears

### Test 7: Camera (Tier 2+)
- ✅ Navigate to Marine Vision page
- ✅ Camera status shows "Connected" (if camera configured)
- ✅ Live feed displays (8 FPS refresh)
- ✅ Click [Capture Photo] → photo saved

### Test 8: Data Export (Tier 1+)
- ✅ Navigate to Settings → Data Management
- ✅ Export status shows tier and count
- ✅ Click [Export All Data Now]
- ✅ Success message appears

---

## 🎉 Installation Complete!

Your d3kOS system is now operational. Next steps:

1. **Start Engine** - Run engine and verify dashboard displays real-time data
2. **Test Features** - Explore AI Assistant, weather radar, boatlog, navigation
3. **Configure Camera** (Tier 2+) - Add Reolink camera IP in Settings
4. **Set Up Mobile App** (Tier 1+) - Scan QR code to pair boat
5. **Read User Guides** - AI_ASSISTANT_USER_GUIDE.md, MARINE_VISION_API.md

**Need Help?** See TROUBLESHOOTING_GUIDE.md for common issues and solutions.

**Happy Boating! ⚓**

---

**Document Version**: 1.0.3
**Last Updated**: February 18, 2026
**Maintainer**: SkipperDon (https://atmyboat.com)
