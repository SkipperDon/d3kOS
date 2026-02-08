# d3kOS INSTALLATION GUIDE

**Version**: 2.0
**Last Updated**: February 7, 2026

---

## DEFAULT CREDENTIALS

**⚠️ IMPORTANT - Change After First Login**

| Access Method | Username | Password |
|---------------|----------|----------|
| **SSH Login** | `d3kos` | `d3kos2026` |
| **Desktop Login** | `d3kos` | `d3kos2026` |
| **WiFi AP** | SSID: `d3kOS` | `d3kos-2026` |

**Security Note**: Run `passwd` immediately after first login to change the default password.

---

## TABLE OF CONTENTS

1. [Overview](#overview)
2. [Pre-Installation Requirements](#pre-installation-requirements)
3. [Hardware Assembly](#hardware-assembly)
4. [Software Installation](#software-installation)
5. [First Boot Configuration](#first-boot-configuration)
6. [Network Setup](#network-setup)
7. [Hardware Configuration](#hardware-configuration)
8. [Service Verification](#service-verification)
9. [Post-Installation Tasks](#post-installation-tasks)
10. [Troubleshooting Installation Issues](#troubleshooting-installation-issues)

---

## OVERVIEW

d3kOS is a comprehensive marine electronics system built on Raspberry Pi 4. This guide will walk you through the complete installation process, from hardware assembly to final system configuration.

### Installation Time

- Hardware assembly: 2-4 hours
- Software installation: 30-45 minutes (using pre-built image)
- Initial configuration: 10-15 minutes
- **Total**: 3-5 hours

### What You'll Need

- All hardware components (see Bill of Materials)
- Computer with SD card reader
- Internet connection (for downloading image)
- Basic hand tools (screwdriver, wire strippers)
- Multimeter (recommended for power verification)

---

## PRE-INSTALLATION REQUIREMENTS

### Hardware Requirements

| Component | Specification | Required/Optional |
|-----------|---------------|-------------------|
| **Raspberry Pi 4** | Model B, 4GB RAM minimum | Required |
| **SD Card** | 64GB Class 10 A2 or better | Required |
| **Power Supply** | Official Raspberry Pi 5V 3A USB-C | Required |
| **PiCAN-M HAT** | With micro-fit connector | Required |
| **Display** | 10.1" 1920×1200 touchscreen | Required |
| **USB GPS** | VK-162 or equivalent | Required |
| **USB AIS** | dAISy or equivalent | Recommended |
| **Speakerphone** | Anker PowerConf S330 | Optional (Tier 2+) |
| **IP Camera** | Reolink RLC-810A | Optional (Tier 2+) |
| **DC Converter** | 12V to 5V, 3A minimum | Required (for boat power) |

### Software Requirements

- **Raspberry Pi Imager** (free download from raspberrypi.com)
- **d3kOS Image** (download from GitHub releases)
- **Web Browser** (for accessing d3kOS interface)

### Bill of Materials

| Item | Part Number | Quantity | Estimated Cost (USD) |
|------|-------------|----------|----------------------|
| Raspberry Pi 4 Model B (4GB) | RPI4-MODBP-4GB | 1 | $55 |
| PiCAN-M HAT | PICAN-M | 1 | $60 |
| 10.1" Touchscreen (1920×1200) | Generic | 1 | $120 |
| USB GPS Receiver | VK-162 | 1 | $15 |
| USB AIS Receiver | dAISy | 1 | $80 |
| Anker PowerConf S330 | A3302 | 1 | $130 |
| SD Card (64GB Class 10 A2) | SanDisk Extreme | 1 | $12 |
| 12V to 5V DC Converter | Victron Orion-Tr | 1 | $35 |
| Micro-Fit Connector | Molex 43025-0400 | 1 | $5 |
| Enclosure | Custom 3D-printed | 1 | $20 |
| **Total (Core)** | | | **$402** |
| **Total (with Voice & Camera)** | | | **$532** |

---

## HARDWARE ASSEMBLY

### Step 1: Prepare Raspberry Pi

1. **Inspect the Raspberry Pi**
   - Check for any physical damage
   - Ensure all ports are clean and free from debris

2. **Install Heat Sinks** (if included)
   - Attach heat sinks to CPU, RAM, and USB controller chips
   - Ensure good thermal contact

### Step 2: Install PiCAN-M HAT

1. **Align GPIO Pins**
   - Carefully align the PiCAN-M HAT with the 40-pin GPIO header
   - Ensure pin 1 alignment (square pad on HAT, square pad on Pi)

2. **Seat the HAT**
   - Press down firmly but gently until fully seated
   - All pins should be engaged

3. **Secure with Standoffs** (if provided)
   - Install standoffs at mounting holes
   - Tighten screws gently (do not overtighten)

### Step 3: Connect NMEA2000

1. **Prepare Micro-Fit Connector**
   - Strip wires to 6mm length
   - Crimp pins according to Molex specifications

2. **Pin Configuration**
   ```
   Pin 1: NET-S (Shield) - Drain wire from NMEA2000 cable
   Pin 2: NET-C (CAN_H) - White wire from NMEA2000
   Pin 3: NET-C (CAN_L) - Blue wire from NMEA2000
   Pin 4: NET-S (Ground) - Black wire or shield ground
   ```

3. **Insert into PiCAN-M**
   - Connector should click into place
   - Verify secure connection

### Step 4: Connect Display

1. **DSI Connection** (if using DSI touchscreen)
   - Connect ribbon cable to DSI port on Raspberry Pi
   - Ensure cable is fully inserted and clip is secure

2. **HDMI Connection** (if using HDMI touchscreen)
   - Connect HDMI cable to micro-HDMI port 0 (closest to USB-C)
   - Connect USB cable for touch input

3. **Power the Display**
   - Connect display power according to manufacturer instructions
   - Ensure proper voltage (typically 5V or 12V)

### Step 5: Connect USB Devices

1. **USB GPS Receiver**
   - Connect to any USB port
   - Will auto-detect as `/dev/ttyACM0` or `/dev/ttyUSB0`

2. **USB AIS Receiver**
   - Connect to separate USB port
   - Will auto-detect as `/dev/ttyUSB1` or `/dev/ttyUSB2`

3. **Anker Speakerphone** (Optional, Tier 2+)
   - Connect to USB 3.0 port (blue port) for best performance
   - Will auto-detect as audio input/output device

### Step 6: Install in Enclosure

1. **Mount Raspberry Pi**
   - Secure to mounting plate using standoffs
   - Ensure adequate ventilation space (minimum 10mm clearance)

2. **Route Cables**
   - Use strain relief for all connections
   - Avoid sharp bends in cables
   - Keep power cables separate from signal cables

3. **Seal Enclosure**
   - If using waterproof enclosure, ensure gaskets are properly seated
   - Cable glands should be tightened to manufacturer specifications

### Step 7: Power Connection

1. **Install DC Converter**
   - Mount converter in accessible location
   - Ensure adequate cooling

2. **Connect Boat Power**
   ```
   Boat 12V (+) → DC Converter (+IN)
   Boat GND (-) → DC Converter (-IN)
   DC Converter (+OUT) → USB-C Power Supply (+)
   DC Converter (-OUT) → USB-C Power Supply (-)
   ```

3. **Verify Voltage**
   - Use multimeter to verify 5V output
   - Check for proper polarity before connecting to Pi

4. **Add Protection**
   - Install inline fuse (5A recommended)
   - Add noise filter if electrical noise is present

---

## SOFTWARE INSTALLATION

### Method 1: Pre-Built Image (Recommended)

#### Step 1: Download d3kOS Image

1. Visit GitHub releases: `https://github.com/SkipperDon/d3kOS/releases/latest`
2. Download `d3kos-v2.0.0.img.gz` (~4GB compressed)
3. Download `d3kos-v2.0.0.img.gz.sha256` (checksum file)

#### Step 2: Verify Download

**On Linux/Mac:**
```bash
sha256sum -c d3kos-v2.0.0.img.gz.sha256
```

**On Windows:**
```powershell
certutil -hashfile d3kos-v2.0.0.img.gz SHA256
# Compare output with contents of .sha256 file
```

#### Step 3: Flash SD Card

**Using Raspberry Pi Imager (Recommended):**

1. Download and install Raspberry Pi Imager from `https://www.raspberrypi.com/software/`
2. Insert SD card into computer
3. Launch Raspberry Pi Imager
4. Click "Choose OS" → "Use custom" → Select downloaded `.img.gz` file
5. Click "Choose Storage" → Select your SD card
6. Click "Write"
7. Wait for writing and verification to complete (15-30 minutes)
8. Click "Continue" when finished

**Using balenaEtcher (Alternative):**

1. Download balenaEtcher from `https://www.balena.io/etcher/`
2. Launch balenaEtcher
3. Click "Flash from file" → Select `.img.gz` file
4. Click "Select target" → Choose SD card
5. Click "Flash"
6. Wait for completion

**Using dd (Advanced, Linux only):**

```bash
# Decompress image
gunzip d3kos-v2.0.0.img.gz

# Flash to SD card (replace /dev/sdX with your SD card device)
sudo dd if=d3kos-v2.0.0.img of=/dev/sdX bs=4M status=progress conv=fsync

# Sync to ensure all data is written
sync
```

⚠️ **WARNING**: Double-check device name! Using wrong device will destroy data.

#### Step 4: First Boot

1. Safely eject SD card from computer
2. Insert SD card into Raspberry Pi
3. Connect all USB devices (GPS, AIS, speakerphone)
4. Connect display
5. Apply power
6. Wait for first boot (2-3 minutes)
   - First boot expands filesystem automatically
   - Services start and configure themselves
   - Chromium browser launches in maximized mode

---

## FIRST BOOT CONFIGURATION

### Step 1: Connect to WiFi Network

1. Raspberry Pi creates WiFi access point: **d3kOS**
2. From your laptop/tablet/phone:
   - Connect to WiFi network: **d3kOS**
   - Password: **d3kos-2026**
   - Wait for connection (10-15 seconds)

### Step 2: Access Web Interface

1. Open web browser
2. Navigate to one of:
   - `http://d3kos.local` (preferred, uses mDNS)
   - `http://10.42.0.1` (fallback, direct IP)

3. Main menu should load within 5 seconds

### Step 3: Complete Onboarding Wizard

The onboarding wizard will launch automatically on first boot. See [ONBOARDING.md](ONBOARDING.md) for detailed instructions.

**Quick Summary:**
1. Answer 13 questions about your engine
2. Record CX5106 DIP switch configuration
3. Generate installation QR code
4. Arrive at main menu

---

## NETWORK SETUP

### WiFi Access Point Configuration

d3kOS creates a WiFi access point by default:

| Setting | Value |
|---------|-------|
| SSID | d3kOS |
| Password | d3kos-2026 |
| IP Address | 10.42.0.1 |
| DHCP Range | 10.42.0.2 - 10.42.0.254 |
| Subnet Mask | 255.255.255.0 |

### Internet Sharing (Optional)

If you connect an ethernet cable to the Raspberry Pi:
- WiFi clients can access internet through Raspberry Pi
- Useful for downloading OpenCPN charts
- Useful for checking for system updates

**To connect ethernet:**
1. Plug ethernet cable into Raspberry Pi
2. Wait 10 seconds for connection
3. WiFi clients will automatically get internet access

### Changing WiFi Credentials (Advanced)

```bash
# SSH into Raspberry Pi (must enable SSH first in settings)
ssh pi@10.42.0.1

# Edit WiFi configuration
sudo nmcli connection modify d3kOS-AP wifi.ssid "YourBoatName"
sudo nmcli connection modify d3kOS-AP wifi-sec.psk "YourPassword"

# Restart network
sudo nmcli connection down d3kOS-AP
sudo nmcli connection up d3kOS-AP
```

### Firewall Configuration

d3kOS uses UFW (Uncomplicated Firewall) with the following rules:

| Port | Service | Access |
|------|---------|--------|
| 80 | HTTP (Main menu) | WiFi clients only |
| 3000 | Signal K | WiFi clients only |
| 1880 | Node-RED Dashboard | WiFi clients only |
| 554 | RTSP (Camera) | WiFi clients only (Tier 2+) |
| 22 | SSH | Disabled by default |

---

## HARDWARE CONFIGURATION

### CAN Bus Configuration

The CAN0 interface should be automatically configured. To verify:

```bash
# Check if CAN interface exists
ifconfig can0

# Should show:
# can0: flags=193<UP,RUNNING,NOARP>  mtu 16
#       unspec 00-00-00-00-00-00-00-00-00-00-00-00-00-00-00-00  txqueuelen 10  (UNSPEC)
```

If CAN0 is not configured:

```bash
# Manually configure CAN interface
sudo ip link set can0 type can bitrate 250000
sudo ifconfig can0 up

# Make permanent by adding to /etc/network/interfaces.d/can0:
sudo nano /etc/network/interfaces.d/can0

# Add these lines:
auto can0
iface can0 inet manual
    pre-up /sbin/ip link set can0 type can bitrate 250000
    up /sbin/ifconfig can0 up
    down /sbin/ifconfig can0 down
```

### GPS Configuration

Verify GPS is detected:

```bash
# List USB devices
lsusb | grep GPS

# Check if gpsd is receiving data
cgps -s

# Should show latitude, longitude, satellites
```

### Display Configuration

Verify touchscreen is working:

```bash
# List input devices
xinput list

# Should show touchscreen device
```

If touch is not working, calibrate:

```bash
# Install calibration tool
sudo apt-get install xinput-calibrator

# Run calibration
xinput_calibrator
```

---

## SERVICE VERIFICATION

### Check System Services

Verify all required services are running:

```bash
# Signal K Server
sudo systemctl status signalk.service

# Node-RED
sudo systemctl status nodered.service

# GPS Daemon
sudo systemctl status gpsd.service

# d3kOS Health Monitor
sudo systemctl status d3kos-health.service
```

All services should show **active (running)** in green.

### Test Signal K Data

1. Open browser to `http://10.42.0.1:3000`
2. Signal K admin interface should load
3. Click "Dashboard" → "Data Browser"
4. Verify NMEA2000 data is flowing
5. Look for paths like:
   - `vessels.self.propulsion.main.revolutions`
   - `vessels.self.navigation.position`
   - `vessels.self.electrical.batteries.0.voltage`

### Test Node-RED Dashboard

1. Open browser to `http://10.42.0.1:1880/dashboard`
2. Dashboard should load with gauges
3. Verify gauges are updating (may show "0" or "null" if engine is off)

### Test Voice Assistant (Tier 2+ only)

1. Ensure Anker speakerphone is connected
2. From main menu, enable voice assistant toggle
3. Wait 10 seconds for wake word detection to start
4. Say "Helm" clearly
5. Listen for acknowledgment beep
6. Say "What's the engine status?"
7. Should hear spoken response within 2 seconds

---

## POST-INSTALLATION TASKS

### 1. Complete Engine Baseline

After installation, you should run an engine baseline:

1. Start your engine and let it warm up (5 minutes)
2. From main menu, tap "Engine Benchmark"
3. Run engine for 30 minutes at various RPMs
4. System will record baseline metrics
5. Save baseline for future anomaly detection

See section 6.1 in MASTER_SYSTEM_SPEC.md for details.

### 2. Install OpenCPN (Optional)

If you want chart plotting capabilities:

1. From main menu, tap "OpenCPN Management"
2. Tap "Install OpenCPN"
3. Wait for installation (5-10 minutes)
4. Installation unlocks Tier 2 features (voice assistant, camera)
5. Tap "Launch OpenCPN" to test

### 3. Configure Camera (Optional, Tier 2+)

If you have a Reolink IP camera:

1. Connect camera to same network as Raspberry Pi
2. Note camera IP address from camera's display/app
3. From main menu, tap "Camera"
4. Enter RTSP URL: `rtsp://admin:password@CAMERA_IP:554/h264Preview_01_main`
5. Live view should appear within 5 seconds

### 4. Set Up Boat Log

The boat log allows voice-recorded log entries:

1. From main menu, tap "Boat Log"
2. Tap microphone icon to record entry
3. Speak your log entry
4. Tap "Helm post" when finished to save
5. Entries are transcribed and timestamped

### 5. Configure Backup Schedule

Automated daily backups are enabled by default at 2 AM. To verify:

```bash
# Check backup cron job
sudo crontab -l | grep backup

# Should show:
# 0 2 * * * /opt/d3kos/scripts/backup.sh
```

Backups are stored in `/opt/d3kos/backups/` and retained for 30 days.

### 6. Update System (Optional)

Check for system updates:

1. Connect ethernet cable for internet access
2. From main menu, view version information
3. If update available, download new image from GitHub
4. Follow update procedure in TROUBLESHOOTING.md

---

## TROUBLESHOOTING INSTALLATION ISSUES

### Issue: SD Card Not Recognized

**Symptoms**: Raspberry Pi does not boot, red LED only (no green LED activity)

**Solutions**:
1. Verify SD card is fully inserted
2. Try different SD card (must be Class 10 or better)
3. Reflash image to SD card
4. Verify power supply is adequate (5V 3A)

### Issue: Display Shows "No Signal"

**Symptoms**: Display powers on but shows no signal

**Solutions**:
1. Check HDMI/DSI cable connections
2. Verify correct HDMI port (use port 0, closest to USB-C)
3. Try different display or cable
4. Check `config.txt` on SD card boot partition

### Issue: Cannot Connect to WiFi Network

**Symptoms**: "d3kOS" WiFi network not visible

**Solutions**:
1. Wait 2-3 minutes after boot for WiFi to start
2. Check WiFi is enabled on Raspberry Pi (no WiFi disable jumper)
3. Verify client device supports 2.4GHz WiFi
4. Try moving closer to Raspberry Pi
5. Connect via ethernet and check logs: `sudo systemctl status NetworkManager`

### Issue: No NMEA2000 Data

**Symptoms**: Signal K shows no data, gauges show "null"

**Solutions**:
1. Verify CAN0 interface is up: `ifconfig can0`
2. Check NMEA2000 cable connections
3. Verify NMEA2000 bus has power (9-16V DC)
4. Check termination resistors on NMEA2000 backbone
5. Monitor CAN bus: `candump can0`

### Issue: GPS Not Working

**Symptoms**: No position data, OpenCPN shows no GPS fix

**Solutions**:
1. Verify GPS has clear view of sky (won't work indoors)
2. Wait 5-10 minutes for initial GPS fix (cold start)
3. Check GPS is detected: `lsusb | grep GPS`
4. Verify gpsd is running: `sudo systemctl status gpsd`
5. Test with `cgps -s`

### Issue: Touchscreen Not Responding

**Symptoms**: Display works but touch input doesn't register

**Solutions**:
1. Check USB cable for touch (if HDMI display)
2. Verify touch device is detected: `xinput list`
3. Calibrate touchscreen: `xinput_calibrator`
4. Reboot system

### Issue: Voice Assistant Not Working

**Symptoms**: No response when saying "Helm" (Tier 2+ only)

**Solutions**:
1. Verify Anker speakerphone is connected: `arecord -l`
2. Check voice service is running: `sudo systemctl status helm-voice`
3. Test microphone: `arecord -d 5 test.wav && aplay test.wav`
4. Adjust microphone sensitivity in speakerphone settings
5. Ensure you have Tier 2+ license (OpenCPN installed)

### Issue: Services Not Starting

**Symptoms**: Error messages on boot, dashboard not loading

**Solutions**:
1. Check service status: `sudo systemctl status signalk nodered gpsd`
2. View logs: `sudo journalctl -u signalk -n 50`
3. Restart services: `sudo systemctl restart signalk nodered`
4. Check disk space: `df -h` (need >2GB free)
5. Verify SD card integrity: `sudo fsck /dev/mmcblk0p2`

### Issue: System Running Slow

**Symptoms**: UI is laggy, voice responses delayed

**Solutions**:
1. Check CPU temperature: `vcgencmd measure_temp` (should be <80°C)
2. Check CPU usage: `top`
3. Ensure adequate cooling (add heat sinks or fan)
4. Reduce camera recording quality if enabled
5. Use 8GB Raspberry Pi for better performance with voice features

---

## GETTING HELP

If you encounter issues not covered here:

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed solutions
2. Search GitHub Issues: `https://github.com/SkipperDon/d3kOS/issues`
3. Post new issue with:
   - Hardware configuration
   - Software version (from main menu)
   - Detailed error description
   - Relevant log files

---

## NEXT STEPS

After successful installation:

1. Complete onboarding wizard → [ONBOARDING.md](ONBOARDING.md)
2. Run engine baseline for health monitoring
3. Explore main menu features
4. Read API documentation → [API_REFERENCE.md](API_REFERENCE.md)
5. Join community discussions on GitHub

---

**Installation Complete!** Welcome to d3kOS.
