# HELM-OS TROUBLESHOOTING GUIDE

**Version**: 2.0
**Last Updated**: February 6, 2026

---

## TABLE OF CONTENTS

1. [Quick Diagnostic Steps](#quick-diagnostic-steps)
2. [Boot and Startup Issues](#boot-and-startup-issues)
3. [Network and Connectivity](#network-and-connectivity)
4. [NMEA2000 and Signal K](#nmea2000-and-signal-k)
5. [Display and Touchscreen](#display-and-touchscreen)
6. [Voice Assistant](#voice-assistant)
7. [Camera Issues](#camera-issues)
8. [Performance Problems](#performance-problems)
9. [Data and Storage](#data-and-storage)
10. [Service Failures](#service-failures)
11. [Update and Recovery](#update-and-recovery)
12. [Advanced Troubleshooting](#advanced-troubleshooting)

---

## QUICK DIAGNOSTIC STEPS

Before diving into specific issues, try these quick checks:

### 1. Check System Status

```bash
# SSH into Raspberry Pi
ssh pi@10.42.0.1
# Default password: raspberry (change this!)

# Check all Helm-OS services
sudo systemctl status signalk nodered gpsd helm-health

# Check system health
curl http://10.42.0.1/api/health | jq
```

### 2. Check Logs

```bash
# View recent system log
sudo journalctl -n 100

# View Signal K logs
sudo journalctl -u signalk -n 50

# View Node-RED logs
sudo journalctl -u nodered -n 50

# View Helm-OS specific logs
tail -f /opt/helm-os/logs/*.log
```

### 3. Check Hardware

```bash
# Check CPU temperature
vcgencmd measure_temp

# Check for throttling
vcgencmd get_throttled
# Output: throttled=0x0 (good) or throttled=0x50000 (bad)

# Check disk space
df -h

# Check memory usage
free -h

# List USB devices
lsusb

# Check network interfaces
ifconfig
```

### 4. Restart Services

```bash
# Restart all core services
sudo systemctl restart signalk nodered gpsd

# Restart specific service
sudo systemctl restart helm-voice

# Reboot entire system
sudo reboot
```

---

## BOOT AND STARTUP ISSUES

### Issue: Raspberry Pi Won't Boot

**Symptoms:**
- No green LED activity
- Only red LED stays on
- No display output

**Possible Causes:**
1. Corrupted SD card
2. Insufficient power supply
3. Hardware failure

**Solutions:**

**Step 1: Check Power Supply**
```bash
# With multimeter, verify:
# - 5.0V to 5.2V at USB-C connector
# - 3A current capability
```

**Step 2: Check SD Card**
```bash
# On computer, check SD card integrity:
# Windows:
chkdsk E: /f

# Linux/Mac:
sudo fsck /dev/sdX
```

**Step 3: Reflash SD Card**
1. Download fresh Helm-OS image from GitHub
2. Flash to SD card using Raspberry Pi Imager
3. Insert and reboot

**Step 4: Test with Different SD Card**
- Use known-good SD card
- If boots successfully, original SD card is faulty

---

### Issue: Boots But Stops at Rainbow Screen

**Symptoms:**
- Rainbow screen appears
- No progress to desktop

**Cause:** Boot configuration issue

**Solution:**
```bash
# Mount SD card on computer
# Edit /boot/config.txt

# Add or uncomment:
hdmi_force_hotplug=1
hdmi_drive=2
config_hdmi_boost=4

# For touchscreen issues, add:
dtoverlay=vc4-kms-v3d
max_framebuffers=2
```

---

### Issue: Boots But No GUI Appears

**Symptoms:**
- Terminal login prompt instead of GUI
- Or blank screen after boot

**Solution:**

**Step 1: Check X Server**
```bash
# Login via terminal (keyboard required)
# Username: pi
# Password: raspberry

# Check if X is running
ps aux | grep X

# Manually start X
startx

# If errors, check logs
cat ~/.xsession-errors
```

**Step 2: Reinstall Display Manager**
```bash
sudo apt-get update
sudo apt-get install --reinstall xserver-xorg
sudo reboot
```

---

### Issue: Services Don't Start on Boot

**Symptoms:**
- Dashboard not accessible
- Signal K not running
- Empty gauges

**Solution:**

**Check Service Status:**
```bash
sudo systemctl status signalk
sudo systemctl status nodered
sudo systemctl status gpsd
```

**Enable Services:**
```bash
sudo systemctl enable signalk
sudo systemctl enable nodered
sudo systemctl enable gpsd
sudo systemctl enable helm-health

sudo reboot
```

**Check Dependencies:**
```bash
# View service dependencies
systemctl list-dependencies signalk

# Check for failed dependencies
systemctl --failed
```

---

## NETWORK AND CONNECTIVITY

### Issue: Cannot Connect to "Helm-OS" WiFi

**Symptoms:**
- WiFi network not visible
- Connection fails
- Wrong password error

**Solutions:**

**Step 1: Verify WiFi is Active**
```bash
# Via terminal (connect keyboard/mouse)
nmcli device status

# Should show wlan0 as "connected"
```

**Step 2: Check WiFi Configuration**
```bash
nmcli connection show Helm-OS-AP

# Verify settings:
# - SSID: Helm-OS
# - Mode: ap
# - Password: helm-os-2026
```

**Step 3: Restart WiFi**
```bash
sudo nmcli connection down Helm-OS-AP
sudo nmcli connection up Helm-OS-AP

# Or restart NetworkManager
sudo systemctl restart NetworkManager
```

**Step 4: Recreate WiFi AP**
```bash
# Delete existing connection
sudo nmcli connection delete Helm-OS-AP

# Create new AP
sudo nmcli device wifi hotspot \
  ifname wlan0 \
  ssid Helm-OS \
  password helm-os-2026

# Make persistent
sudo nmcli connection modify Helm-OS-AP \
  connection.autoconnect yes \
  ipv4.method shared
```

---

### Issue: Connected to WiFi But Can't Access Dashboard

**Symptoms:**
- Connected to Helm-OS WiFi
- http://helm-os.local doesn't work
- http://10.42.0.1 doesn't work

**Solutions:**

**Step 1: Verify IP Assignment**
```bash
# On client device:
# Windows:
ipconfig

# Mac/Linux:
ifconfig

# Should show IP: 10.42.0.x
# Gateway: 10.42.0.1
```

**Step 2: Test Connectivity**
```bash
# Ping Raspberry Pi
ping 10.42.0.1

# If no response, check firewall
```

**Step 3: Check Firewall**
```bash
sudo ufw status

# Should show:
# 80/tcp ALLOW IN
# 1880/tcp ALLOW IN
# 3000/tcp ALLOW IN

# If not, add rules:
sudo ufw allow 80/tcp
sudo ufw allow 1880/tcp
sudo ufw allow 3000/tcp
sudo ufw reload
```

**Step 4: Check Web Server**
```bash
# Verify Chromium/web server is running
ps aux | grep chromium

# Check Node-RED dashboard
curl http://localhost:1880/dashboard

# Should return HTML
```

---

### Issue: mDNS (helm-os.local) Not Working

**Symptoms:**
- http://helm-os.local doesn't resolve
- IP address (10.42.0.1) works fine

**Solution:**

**Step 1: Install/Check Avahi**
```bash
sudo systemctl status avahi-daemon

# If not running:
sudo apt-get install avahi-daemon
sudo systemctl enable avahi-daemon
sudo systemctl start avahi-daemon
```

**Step 2: Configure Hostname**
```bash
# Check hostname
hostname

# Should be: helm-os

# If not, set it:
sudo hostnamectl set-hostname helm-os

# Edit hosts file
sudo nano /etc/hosts
# Add: 127.0.1.1  helm-os
```

**Step 3: Client Device Requirements**
- **Windows**: Install Bonjour Print Services
- **Mac/iOS**: Built-in (should work)
- **Linux**: Install avahi-utils
- **Android**: Install Bonjour Browser app

---

## NMEA2000 AND SIGNAL K

### Issue: No NMEA2000 Data

**Symptoms:**
- Dashboard gauges show "null" or "---"
- Signal K shows no data
- Engine metrics missing

**Solutions:**

**Step 1: Check CAN Interface**
```bash
# Verify can0 exists
ifconfig can0

# Should show:
# can0: flags=193<UP,RUNNING,NOARP>

# If not present:
sudo ip link set can0 type can bitrate 250000
sudo ifconfig can0 up
```

**Step 2: Monitor CAN Bus**
```bash
# Install can-utils if needed
sudo apt-get install can-utils

# Monitor raw CAN messages
candump can0

# Should see messages like:
# can0  09F10D05   [8]  FF 00 DC 05 00 FF FF FF
# can0  09F21111   [8]  00 FC 00 00 FF FF FF FF

# If no messages:
# - Check NMEA2000 bus has power (9-16V)
# - Check termination resistors (120Ω at each end)
# - Verify PiCAN-M connections
```

**Step 3: Check Signal K Configuration**
```bash
# View Signal K config
cat ~/.signalk/settings.json | jq '.pipedProviders'

# Should show can0 provider
# If missing, add via Signal K web interface:
# http://10.42.0.1:3000/admin
# → Data Connections → Add Connection → NMEA2000 (canbus)
```

**Step 4: Restart Signal K**
```bash
sudo systemctl restart signalk

# Watch logs for errors
sudo journalctl -u signalk -f
```

---

### Issue: Some PGNs Missing

**Symptoms:**
- Some data appears (e.g., RPM)
- Other data missing (e.g., temperature, pressure)

**Possible Causes:**
1. CX5106 DIP switches incorrect
2. Sensors not connected
3. PGN not transmitted by ECU

**Solutions:**

**Step 1: Verify Data is on Bus**
```bash
# Use candump to see raw messages
candump can0 | grep "09F113"  # Look for PGN 127489 (engine parameters)

# If not present, data isn't being transmitted
```

**Step 2: Check CX5106 Configuration**
- Review DIP switch settings from onboarding
- Verify switches match your engine configuration
- Ensure switch 8 is ON (enables all outputs)

**Step 3: Check Sensor Connections**
```bash
# For CX5106, check physical sensor wiring:
# - RPM: Connected to ignition coil
# - Temp: Thermistor in coolant
# - Pressure: Sensor in oil gallery
```

**Step 4: Check Signal K Parsing**
```bash
# View Signal K debug log
sudo journalctl -u signalk -n 1000 | grep "PGN 127489"

# Should show parsed messages
# If errors, update Signal K:
cd ~/.signalk
npm update
```

---

### Issue: Incorrect Data Values

**Symptoms:**
- RPM shows wrong value (e.g., 16000 instead of 4000)
- Temperature in wrong units
- Pressure readings nonsensical

**Solutions:**

**For RPM Issues:**
```bash
# RPM too high: Wrong cylinder count in CX5106
# - 8-cyl engine with 4-cyl setting = 2× actual RPM
# - Fix: Correct DIP switch 2

# RPM too low: Wrong ignition pickup
# - Check CX5106 manual for RPM configuration
```

**For Temperature Issues:**
```bash
# Signal K uses Kelvin
# Display should convert: °F = (K - 273.15) × 9/5 + 32

# Verify conversion in Node-RED:
# Function node: msg.payload = (msg.payload - 273.15) * 9/5 + 32
```

**For Pressure Issues:**
```bash
# Signal K uses Pascals
# Display should convert: PSI = Pa / 6895

# Verify pressure sensor range matches CX5106 DIP switch 5
# - ON: 0-100 PSI
# - OFF: 0-150 PSI
```

---

## DISPLAY AND TOUCHSCREEN

### Issue: Touchscreen Not Responding

**Symptoms:**
- Display works, but touch doesn't register
- Wrong touch locations
- Erratic touch behavior

**Solutions:**

**Step 1: Verify Touch Device**
```bash
# List input devices
xinput list

# Should show touchscreen device
# Example: "eGalax Inc. USB TouchController"

# If not listed, check USB connection
lsusb | grep -i touch
```

**Step 2: Calibrate Touchscreen**
```bash
# Install calibration tool
sudo apt-get install xinput-calibrator

# Run calibration
DISPLAY=:0 xinput_calibrator

# Follow on-screen instructions (tap corners)

# Save calibration data to:
sudo nano /etc/X11/xorg.conf.d/99-calibration.conf

# Paste output from calibration tool
```

**Step 3: Check Touch Driver**
```bash
# For HDMI + USB touch:
# Verify USB cable is connected

# For DSI + I2C touch:
# Check /boot/config.txt for:
dtoverlay=vc4-kms-v3d
dtoverlay=edt-ft5406

# Reboot after changes
sudo reboot
```

---

### Issue: Display Resolution Wrong

**Symptoms:**
- Image doesn't fill screen
- Text too small or too large
- Black borders around display

**Solution:**

**Edit Boot Config:**
```bash
sudo nano /boot/config.txt

# For 1920×1200 display:
hdmi_group=2
hdmi_mode=87
hdmi_cvt=1920 1200 60 6 0 0 0

# For 1280×800 display:
hdmi_group=2
hdmi_mode=28

# Save and reboot
sudo reboot
```

---

### Issue: On-Screen Keyboard Not Appearing

**Symptoms:**
- Keyboard doesn't pop up when tapping text field
- Or keyboard is present but not functional

**Solution:**

**Step 1: Check Onboard is Installed**
```bash
# Check if running
ps aux | grep onboard

# Install if missing
sudo apt-get install onboard

# Start manually
DISPLAY=:0 onboard &
```

**Step 2: Auto-Start Onboard**
```bash
# Add to autostart
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/onboard.desktop << EOF
[Desktop Entry]
Type=Application
Name=Onboard
Exec=onboard
X-GNOME-Autostart-enabled=true
EOF
```

---

## VOICE ASSISTANT

### Issue: Voice Assistant Not Responding

**Symptoms:**
- Say "Helm" but no response
- No beep or acknowledgment
- Voice service shows "running" but doesn't work

**Solutions:**

**Step 1: Check Tier**
```bash
# Voice requires Tier 2+
curl http://10.42.0.1/api/license | jq '.data.tier'

# Should show: 2 or 3
# If 0, install OpenCPN to upgrade
```

**Step 2: Verify Microphone**
```bash
# List audio devices
arecord -l

# Should show Anker PowerConf S330

# Test microphone
arecord -d 5 test.wav
# Speak for 5 seconds

# Play back
aplay test.wav
# Should hear your voice clearly
```

**Step 3: Check Voice Service**
```bash
sudo systemctl status helm-voice

# If not running:
sudo systemctl start helm-voice

# Watch logs
sudo journalctl -u helm-voice -f

# Look for errors like:
# - "Microphone not found"
# - "Model not loaded"
# - "Vosk initialization failed"
```

**Step 4: Test Wake Word Detection**
```bash
# Run wake word detector manually
cd /opt/helm-os/services/voice
python3 wake_word.py

# Should show:
# "Listening for wake word 'Helm'..."

# Say "Helm" clearly
# Should show: "Wake word detected!"

# If not detecting:
# - Check microphone volume (adjust on speakerphone)
# - Reduce background noise
# - Speak louder/closer to microphone
```

---

### Issue: Wake Word Detected But No Response

**Symptoms:**
- "Helm" triggers detection
- But no spoken response to command
- Or garbled/robotic speech

**Solutions:**

**Step 1: Check Speaker**
```bash
# List audio output devices
aplay -l

# Test speaker
speaker-test -t wav -c 2

# Should hear "Front Left, Front Right"
```

**Step 2: Check TTS Service**
```bash
# Test Piper TTS manually
echo "Engine is running normally" | \
  /opt/helm-os/models/piper/piper \
  --model /opt/helm-os/models/piper/en_US-amy-medium.onnx \
  --output_file test.wav

aplay test.wav

# Should hear clear speech
```

**Step 3: Check LLM Service**
```bash
# Test Phi-2 manually
cd /opt/helm-os/services/voice
python3 test_llm.py "What's the engine status?"

# Should output response text
# If fails:
# - Check model file exists: /opt/helm-os/models/phi2/
# - Check sufficient memory (need 4GB free)
# - Check CPU not throttling
```

---

### Issue: Voice Response Too Slow

**Symptoms:**
- Takes >5 seconds from "Helm" to response
- Target is <2 seconds total

**Solutions:**

**Step 1: Check CPU/Memory**
```bash
# Check CPU usage during voice query
top

# Phi-2 should use ~80% CPU briefly
# If 100% sustained, system overloaded

# Check memory
free -h

# Need at least 3GB free for LLM
```

**Step 2: Use Smaller LLM**
```bash
# Edit voice service config
sudo nano /opt/helm-os/config/voice.json

# Change model:
{
  "llm": {
    "model": "phi-2-q4",  # Smaller, faster quantization
    "context_size": 1024  # Reduce from 2048
  }
}

sudo systemctl restart helm-voice
```

**Step 3: Reduce Wake Word Sensitivity**
```bash
# Edit wake word config
sudo nano /opt/helm-os/config/wake_word.json

# Increase threshold (less sensitive, faster)
{
  "threshold": 1e-35  # Default: 1e-40
}
```

---

## CAMERA ISSUES

### Issue: Camera Not Connecting

**Symptoms:**
- Live view shows "No Signal"
- Connection timeout error
- Camera not detected

**Solutions:**

**Step 1: Verify Camera Network**
```bash
# Ping camera
ping 192.168.1.100  # Replace with your camera IP

# If no response:
# - Check camera is powered on
# - Check camera is on same network
# - Check camera IP address (use Reolink app)
```

**Step 2: Test RTSP Stream**
```bash
# Test stream with VLC command line
vlc rtsp://admin:password@192.168.1.100:554/h264Preview_01_main

# Replace:
# - admin:password with your camera credentials
# - 192.168.1.100 with your camera IP

# If stream works, issue is in Helm-OS camera service
```

**Step 3: Check Camera Credentials**
```bash
# Edit camera config
sudo nano /opt/helm-os/config/camera.json

# Verify:
{
  "url": "rtsp://admin:password@192.168.1.100:554/h264Preview_01_main",
  "username": "admin",
  "password": "yourpassword"
}

# Save and restart service
sudo systemctl restart helm-camera
```

---

### Issue: Recording Won't Start

**Symptoms:**
- Click record button but nothing happens
- Error: "Insufficient disk space"
- Or "Recording already in progress"

**Solutions:**

**Step 1: Check Disk Space**
```bash
df -h

# Need at least 18% free to start recording
# If below 18%, delete old recordings:
rm /opt/helm-os/data/camera/202601*.mp4
```

**Step 2: Check Existing Recording**
```bash
# Check if recording is already running
curl http://10.42.0.1/api/camera/status | jq '.data.recording'

# If true, stop it first:
curl -X POST http://10.42.0.1/api/camera/recording/stop
```

**Step 3: Check Service**
```bash
sudo systemctl status helm-camera

# Check logs for errors
sudo journalctl -u helm-camera -n 50
```

---

### Issue: Recordings Automatically Deleted

**Symptoms:**
- Old recordings disappear
- Storage never fills up

**Explanation:**
This is normal behavior! Helm-OS automatically deletes oldest recordings when disk space drops below 18% to prevent system failure.

**To Preserve Recordings:**
1. Copy to external USB drive regularly
2. Export important clips via interface
3. Increase SD card size (128GB or larger)

```bash
# Disable auto-delete (not recommended)
sudo nano /opt/helm-os/config/camera.json

# Set:
{
  "auto_delete": false
}

# WARNING: Disk may fill up and crash system!
```

---

## PERFORMANCE PROBLEMS

### Issue: System Running Slow

**Symptoms:**
- Dashboard laggy
- Voice responses slow
- UI freezes

**Solutions:**

**Step 1: Check CPU Temperature**
```bash
vcgencmd measure_temp

# Safe: <75°C
# Warning: 75-80°C
# Critical: >80°C (throttling)

# If hot:
# - Improve cooling (add heatsinks/fan)
# - Reduce ambient temperature
# - Check case ventilation
```

**Step 2: Check CPU Throttling**
```bash
vcgencmd get_throttled

# Output decoder:
# 0x0 = No issues
# 0x50000 = Throttled due to undervoltage
# 0x50005 = Throttled due to undervoltage & temp

# If throttled:
# - Check power supply (need 5V 3A)
# - Reduce CPU load
# - Improve cooling
```

**Step 3: Reduce Services**
```bash
# Disable voice assistant (Tier 2+)
curl -X POST http://10.42.0.1/api/voice/enable \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'

# Stop camera service
sudo systemctl stop helm-camera
sudo systemctl disable helm-camera

# Reduce Node-RED flows
# - Open http://10.42.0.1:1880
# - Delete unused flows
# - Deploy changes
```

---

### Issue: High Memory Usage

**Symptoms:**
- System slow
- Services crash
- Out of memory errors

**Solutions:**

**Check Memory:**
```bash
free -h

# If <500MB available:
# System is memory constrained
```

**Reduce Memory Usage:**
```bash
# 1. Use 4GB Raspberry Pi without voice
# 2. Or upgrade to 8GB Pi for voice features

# Restart services to free memory:
sudo systemctl restart signalk nodered

# Clear system cache:
sudo sync
echo 3 | sudo tee /proc/sys/vm/drop_caches
```

---

### Issue: SD Card Corruption

**Symptoms:**
- Read-only file system errors
- Boot failures
- Data loss

**Prevention:**
```bash
# Enable overlay filesystem (prevents writes)
sudo raspi-config
# → Performance Options → Overlay File System → Enable

# WARNING: Changes won't persist across reboots!
```

**Recovery:**
```bash
# Boot from recovery media
# Check and repair filesystem
sudo fsck -y /dev/mmcblk0p2

# Backup data
sudo mount /dev/mmcblk0p2 /mnt
sudo tar czf backup.tar.gz /mnt/opt/helm-os

# Reflash SD card with fresh image
```

---

## DATA AND STORAGE

### Issue: Disk Space Running Low

**Symptoms:**
- Warning: "Disk space <20%"
- Services failing
- Cannot record camera

**Solutions:**

**Check Disk Usage:**
```bash
df -h
du -sh /opt/helm-os/data/*

# Common space hogs:
# - Camera recordings: /opt/helm-os/data/camera/
# - Historical logs: /opt/helm-os/data/historical.db
# - System logs: /var/log/
```

**Free Up Space:**
```bash
# Delete old camera recordings
rm /opt/helm-os/data/camera/202601*.mp4

# Compact historical database
sqlite3 /opt/helm-os/data/historical.db "VACUUM;"

# Clear system logs
sudo journalctl --vacuum-time=7d

# Clear apt cache
sudo apt-get clean
```

---

### Issue: Historical Data Missing

**Symptoms:**
- Graphs show no data
- API returns empty results
- Recent data not recorded

**Solutions:**

**Check Database:**
```bash
# Check database exists
ls -lh /opt/helm-os/data/historical.db

# Check database size
du -h /opt/helm-os/data/historical.db

# Query database
sqlite3 /opt/helm-os/data/historical.db \
  "SELECT COUNT(*) FROM engine_metrics;"

# Should show number of records
```

**Check Logging Service:**
```bash
sudo systemctl status helm-health

# Check logs
sudo journalctl -u helm-health -n 50

# Restart service
sudo systemctl restart helm-health
```

---

## SERVICE FAILURES

### Issue: Signal K Not Starting

**Error Messages:**
- "Failed to start Signal K server"
- "Port 3000 already in use"
- "Cannot read configuration"

**Solutions:**

**Check Port Conflict:**
```bash
# Check what's using port 3000
sudo lsof -i :3000

# Kill conflicting process
sudo kill <PID>

# Restart Signal K
sudo systemctl restart signalk
```

**Check Configuration:**
```bash
# Validate Signal K config
cd ~/.signalk
cat settings.json | jq

# If JSON errors, restore backup
cp settings.json.backup settings.json

# Restart
sudo systemctl restart signalk
```

**Reinstall Signal K:**
```bash
# Remove and reinstall
sudo systemctl stop signalk
sudo apt-get remove --purge signalk-server
sudo apt-get install signalk-server
sudo systemctl enable signalk
sudo systemctl start signalk
```

---

### Issue: Node-RED Not Starting

**Error Messages:**
- "Failed to start Node-RED"
- "Port 1880 already in use"
- "Module not found"

**Solutions:**

**Check Service:**
```bash
sudo systemctl status nodered

# Check logs
sudo journalctl -u nodered -n 100

# Common errors:
# - Missing node modules
# - Corrupted flow file
# - Port conflict
```

**Reset Node-RED:**
```bash
# Stop Node-RED
sudo systemctl stop nodered

# Backup flows
cp ~/.node-red/flows.json ~/.node-red/flows.json.backup

# Clear cache
rm -rf ~/.node-red/node_modules
cd ~/.node-red
npm install

# Restart
sudo systemctl start nodered
```

---

## UPDATE AND RECOVERY

### Issue: Update Failed

**Symptoms:**
- Downloaded new image but system won't boot
- Or system boots but features missing

**Solution:**

**Restore Previous Version:**
1. Keep old SD card as backup
2. Flash new image to different SD card
3. Test before replacing original

**If Already Replaced:**
1. Download previous version from GitHub releases
2. Flash to new SD card
3. Restore configuration backup

**Restore Configuration:**
```bash
# From backup tarball
sudo tar xzf backup.tar.gz -C /

# Or manually copy files
sudo cp backup/onboarding.json /opt/helm-os/config/
sudo cp backup/benchmark-results.json /opt/helm-os/config/
sudo cp backup/license.json /opt/helm-os/config/

sudo reboot
```

---

### Issue: System Unresponsive

**Symptoms:**
- Cannot SSH
- Cannot access web interface
- System frozen

**Recovery:**

**Step 1: Hard Reboot**
1. Disconnect power
2. Wait 10 seconds
3. Reconnect power
4. Wait for boot (2-3 minutes)

**Step 2: Boot to Recovery**
1. Power off
2. Remove SD card
3. Mount on computer
4. Edit /boot/cmdline.txt, add to end: `init=/bin/bash`
5. Insert SD card, boot
6. System will boot to bash prompt
7. Run fsck: `fsck -y /dev/mmcblk0p2`
8. Remove init=/bin/bash from cmdline.txt
9. Reboot

**Step 3: Fresh Install**
If recovery fails:
1. Backup data if possible
2. Download fresh image
3. Flash to SD card
4. Restore configuration

---

## ADVANCED TROUBLESHOOTING

### Accessing Logs Remotely

**Via Web Interface:**
```bash
# View logs in browser
http://10.42.0.1:1880/ui  # Node-RED dashboard
http://10.42.0.1:3000/admin  # Signal K admin
```

**Via SSH:**
```bash
# Enable SSH
# From terminal: sudo systemctl enable ssh
# Or from main menu: Settings → Enable SSH

# Connect from computer
ssh pi@10.42.0.1
# Password: raspberry (change this!)
```

**Via Serial Console:**
```bash
# Connect USB-to-TTL adapter to GPIO pins:
# GND → Pin 6
# TX → Pin 8 (RX)
# RX → Pin 10 (TX)

# Use PuTTY/screen:
screen /dev/ttyUSB0 115200

# Login as pi
```

---

### Database Maintenance

**Check Database Integrity:**
```bash
sqlite3 /opt/helm-os/data/historical.db "PRAGMA integrity_check;"

# Should output: ok
```

**Repair Corrupted Database:**
```bash
# Dump to SQL
sqlite3 /opt/helm-os/data/historical.db .dump > backup.sql

# Recreate database
rm /opt/helm-os/data/historical.db
sqlite3 /opt/helm-os/data/historical.db < backup.sql

# Verify
sqlite3 /opt/helm-os/data/historical.db "SELECT COUNT(*) FROM engine_metrics;"
```

**Optimize Database:**
```bash
# Compact and optimize
sqlite3 /opt/helm-os/data/historical.db << EOF
VACUUM;
ANALYZE;
EOF
```

---

### Factory Reset

**Warning:** This deletes all configuration and data!

```bash
# Backup important data first!
sudo /opt/helm-os/scripts/backup.sh

# Reset onboarding
rm /opt/helm-os/config/onboarding.json
rm /opt/helm-os/config/benchmark-results.json
rm /opt/helm-os/state/onboarding-reset-count.json

# Keep license (preserves tier)
# Or delete to reset to Tier 0:
# rm /opt/helm-os/config/license.json

# Clear data
rm -rf /opt/helm-os/data/camera/*
rm -rf /opt/helm-os/data/historical.db
rm /opt/helm-os/data/boat-log.txt

# Reboot
sudo reboot

# Onboarding wizard will launch automatically
```

---

## GETTING HELP

### Before Asking for Help

Collect this information:

1. **System Info:**
   ```bash
   cat /opt/helm-os/config/license.json
   uname -a
   vcgencmd version
   ```

2. **Error Logs:**
   ```bash
   sudo journalctl -u signalk -n 100 > signalk.log
   sudo journalctl -u nodered -n 100 > nodered.log
   sudo journalctl -n 200 > system.log
   ```

3. **Hardware Info:**
   ```bash
   lsusb > usb-devices.txt
   ifconfig > network.txt
   vcgencmd measure_temp
   vcgencmd get_throttled
   ```

4. **Describe the Issue:**
   - What were you trying to do?
   - What happened instead?
   - When did it start?
   - What have you tried?

### Where to Get Help

1. **GitHub Issues:**
   - https://github.com/SkipperDon/Helm-OS/issues
   - Search existing issues first
   - Include all diagnostic info

2. **GitHub Discussions:**
   - https://github.com/SkipperDon/Helm-OS/discussions
   - General questions and community help

3. **Documentation:**
   - [INSTALLATION.md](INSTALLATION.md)
   - [ONBOARDING.md](ONBOARDING.md)
   - [API_REFERENCE.md](API_REFERENCE.md)
   - MASTER_SYSTEM_SPEC.md

---

**Document Version**: 2.0
**Last Updated**: February 6, 2026

**Remember:** Most issues can be resolved by:
1. Checking logs
2. Restarting services
3. Rebooting the system
4. Reflashing with fresh image

When in doubt, reboot!
