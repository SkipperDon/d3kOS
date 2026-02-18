# d3kOS Troubleshooting Guide

**Version**: 1.0.3
**Last Updated**: February 18, 2026

---

## 📋 Table of Contents

1. [Boot Issues](#boot-issues)
2. [Network & WiFi](#network--wifi)
3. [NMEA2000 & Engine Data](#nmea2000--engine-data)
4. [GPS & Navigation](#gps--navigation)
5. [Camera Issues](#camera-issues)
6. [Voice Assistant](#voice-assistant)
7. [Web Interface](#web-interface)
8. [Touchscreen](#touchscreen)
9. [Performance & Storage](#performance--storage)
10. [System Recovery](#system-recovery)

---

## 1. Boot Issues

### Problem: Raspberry Pi Won't Power On (No Red LED)

**Symptoms**:
- No LED lights on Raspberry Pi
- Touchscreen shows no signal
- No boot splash screen

**Causes & Solutions**:

**1. Insufficient Power Supply**
- **Check**: Measure DC converter output voltage with multimeter
- **Expected**: 5.0-5.2V DC
- **Solution**: If voltage is low (<4.8V), replace DC converter or check boat battery
- **Common Issue**: Victron Orion-Tr output voltage drops under load

**2. Loose USB-C Cable**
- **Check**: Wiggle USB-C power cable at Raspberry Pi
- **Solution**: Unplug and re-plug firmly, ensure cable clicks into place
- **Tip**: Use high-quality USB-C cable rated for 3A minimum

**3. Blown Fuse**
- **Check**: Inline fuse on 12V power line
- **Solution**: Replace 5A fuse if blown
- **Prevention**: Add surge protector if boat has electrical noise

**4. Faulty SD Card**
- **Check**: Remove SD card, inspect for damage
- **Solution**: Re-flash image to new SD card (see INSTALLATION_GUIDE.md)
- **Prevention**: Use high-quality Class 10 A2 SD cards (SanDisk Extreme)

---

### Problem: Raspberry Pi Powers On But Won't Boot (Green LED Not Flashing)

**Symptoms**:
- Red LED on (power)
- Green LED off or stays solid (not flashing)
- No boot splash screen after 30 seconds

**Causes & Solutions**:

**1. Corrupted SD Card Image**
- **Check**: Re-flash SD card with verified image
- **Solution**:
  ```bash
  # Re-download image and verify checksum
  sha256sum -c d3kos-v1.0.3.img.gz.sha256

  # Re-flash using Raspberry Pi Imager
  ```
- **Prevention**: Always verify checksum before flashing

**2. SD Card Not Seated Properly**
- **Check**: Remove and re-insert SD card
- **Solution**: Push SD card until it clicks, should be flush with board
- **Tip**: Do not force - card should slide in smoothly

**3. PiCAN-M HAT Installation Error**
- **Check**: Remove PiCAN-M HAT, boot Raspberry Pi without it
- **Solution**: If Pi boots without HAT, re-seat HAT carefully (all 40 GPIO pins aligned)
- **Common Issue**: Bent GPIO pins prevent proper contact

**4. Incompatible SD Card**
- **Check**: Try different SD card (known working)
- **Solution**: Use Class 10 A2 SD cards (not all cards are compatible)
- **Avoid**: Generic no-name SD cards, old/slow cards

---

### Problem: Boot Hangs at d3kOS Splash Screen

**Symptoms**:
- d3kOS splash screen appears
- System hangs for 5+ minutes
- No web interface loads

**Causes & Solutions**:

**1. First Boot Filesystem Expansion (Normal)**
- **Check**: Wait 2-3 minutes on first boot only
- **Explanation**: System expands filesystem to full SD card size
- **Solution**: Be patient - only happens once

**2. Corrupted Filesystem**
- **Check**: If hang persists after 5 minutes, power cycle
- **Solution**: If still hangs, re-flash SD card
- **Recovery**:
  ```bash
  # From another computer, check SD card filesystem
  sudo fsck.ext4 -f /dev/sdX2  # Replace sdX with your SD card device
  ```

**3. Network Service Timeout**
- **Check**: SSH into Pi (if accessible) and check logs
  ```bash
  journalctl -u NetworkManager -n 50
  ```
- **Solution**: Disable NetworkManager timeout (advanced)

---

## 2. Network & WiFi

### Problem: Can't See d3kOS WiFi Network

**Symptoms**:
- WiFi list doesn't show "d3kOS" SSID
- Laptop/phone can't connect

**Causes & Solutions**:

**1. WiFi Not Started Yet**
- **Check**: Wait 90 seconds after boot for WiFi AP to start
- **Solution**: Be patient - NetworkManager needs time to configure AP

**2. Wrong WiFi Band**
- **Check**: Ensure device supports 2.4 GHz WiFi (Raspberry Pi doesn't support 5 GHz AP)
- **Solution**: Check device WiFi settings, enable 2.4 GHz band

**3. NetworkManager Service Not Running**
- **Check** (via SSH or VNC):
  ```bash
  sudo systemctl status NetworkManager
  ```
- **Solution**:
  ```bash
  sudo systemctl restart NetworkManager
  sudo systemctl restart dnsmasq
  ```

**4. Conflicting Network Configuration**
- **Check**: Disable other network managers (dhcpcd, systemd-networkd)
  ```bash
  sudo systemctl stop dhcpcd
  sudo systemctl disable dhcpcd
  ```

---

### Problem: Connected to d3kOS WiFi But No Internet

**Symptoms**:
- WiFi connected
- Can access http://d3kos.local
- No internet access (can't browse web)

**Explanation**: **This is normal!** d3kOS WiFi AP is for local access only.

**Solution Options**:

**Option 1: Connect Pi to Internet via Ethernet**
- Plug Ethernet cable into Raspberry Pi eth0 port
- Ethernet internet shared to WiFi AP automatically
- Devices connected to d3kOS WiFi now have internet

**Option 2: Use Separate WiFi for Internet**
- Connect laptop/phone to marina/home WiFi for internet
- Keep second WiFi connection to d3kOS for boat data
- Most devices support 2 WiFi connections simultaneously

**Option 3: USB Cellular Modem** (advanced)
- Plug USB LTE modem into Raspberry Pi
- Configure modem for internet connection
- Internet shared to WiFi AP

---

### Problem: Can't Access http://d3kos.local (Hostname Not Resolving)

**Symptoms**:
- "Server not found" or "ERR_NAME_NOT_RESOLVED"
- WiFi connected to d3kOS

**Causes & Solutions**:

**1. mDNS Not Supported** (Windows without Bonjour)
- **Check**: Try IP address instead: http://10.42.0.1
- **Solution Windows**: Install Bonjour Print Services (includes mDNS)
- **Download**: https://support.apple.com/kb/DL999

**2. DNS Cache**
- **Solution**: Flush DNS cache
  ```bash
  # Windows
  ipconfig /flushdns

  # macOS
  sudo dscacheutil -flushcache

  # Linux
  sudo systemd-resolve --flush-caches
  ```

**3. Browser Cache**
- **Solution**: Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)

**Workaround**: Use IP address instead of hostname: http://10.42.0.1

---

## 3. NMEA2000 & Engine Data

### Problem: Dashboard Shows No Engine Data (All 0 or Null)

**Symptoms**:
- RPM: 0
- Oil Pressure: N/A
- Temperature: N/A
- Fuel: N/A

**Causes & Solutions**:

**1. Engine Not Running** (Normal)
- **Explanation**: Most sensors read 0 when engine is off
- **Solution**: Start engine and verify data appears
- **Expected**: RPM should increase to idle speed (600-900 RPM)

**2. NMEA2000 Backbone Not Powered**
- **Check**: Measure voltage on NMEA2000 backbone (should be 9-16V DC)
- **Solution**: Check NMEA2000 power connection, fuses, and wiring
- **Tip**: NMEA2000 red wire = 12V+, black wire = ground

**3. CAN Interface Not Running**
- **Check**:
  ```bash
  ifconfig can0
  ```
- **Expected Output**:
  ```
  can0: flags=193<UP,RUNNING,NOARP>  mtu 16
  ```
- **Solution**:
  ```bash
  sudo ip link set can0 up type can bitrate 250000
  ```

**4. No CAN Traffic**
- **Check**:
  ```bash
  candump can0
  ```
- **Expected**: Should show continuous PGN messages
- **If Silent**: Check physical NMEA2000 wiring, termination resistors, CX5106 power

**5. CX5106 Not Configured**
- **Check**: DIP switches on CX5106 match wizard configuration (Step 18)
- **Solution**: Reconfigure DIP switches per INSTALLATION_GUIDE.md Step 8.3

**6. Signal K Not Processing Data**
- **Check**:
  ```bash
  sudo systemctl status signalk
  ```
- **Solution**:
  ```bash
  sudo systemctl restart signalk
  ```

---

### Problem: RPM Reads Correctly But Oil Pressure Always 0

**Symptoms**:
- RPM shows correct value (e.g., 750 when idling)
- Oil Pressure: 0 PSI or N/A

**Causes & Solutions**:

**1. Oil Pressure Sender Not Wired**
- **Check**: CX5106 blue wire connected to oil pressure sender
- **Solution**: Wire CX5106 blue wire to oil pressure sender terminal

**2. Wrong Sender Type**
- **Check**: Sender resistance when engine off (should be 10-180Ω)
- **Solution**: Replace with compatible sender (0-80 PSI range)
- **See**: CX5106_CONFIGURATION_GUIDE.md for sender compatibility

**3. CX5106 DIP Switch Configuration**
- **Check**: Verify DIP switch 3 matches sender type
- **Solution**: Adjust switch per sender specifications

---

### Problem: Signal K Shows "cannot read properties of null (reading 'latitude')"

**Symptoms**:
- journalctl shows continuous errors:
  ```
  Cannot read properties of null (reading 'latitude')
  [signalk-to-nmea0183] GGA: no position, not converting
  ```

**Cause**: GPS not providing position data, but sk-to-nmea0183 plugin tries to convert it

**Solutions**:

**1. Wait for GPS Fix**
- **Check**: Allow 2-5 minutes for GPS to acquire satellites
- **Expected**: Errors stop once GPS has fix

**2. Disable sk-to-nmea0183 Plugin** (if not needed)
- **Via VNC or SSH**:
  ```bash
  # Edit Signal K settings
  nano ~/.signalk/settings.json

  # Find sk-to-nmea0183 plugin, set enabled: false
  ```

**3. Lower Signal K Log Level**
- **Solution**:
  ```bash
  # Edit settings
  nano ~/.signalk/settings.json

  # Change "loglevel": "info" to "loglevel": "warn"
  ```
- **Restart Signal K**:
  ```bash
  sudo systemctl restart signalk
  ```

**Note**: journalctl automatically rate-limits these errors (40,000-50,000 messages suppressed per 30 seconds)

---

## 4. GPS & Navigation

### Problem: GPS Shows No Fix (0 Satellites)

**Symptoms**:
- Navigation page shows "No Fix"
- Satellite count: 0
- Position: N/A

**Causes & Solutions**:

**1. GPS Receiver Indoors** (Normal)
- **Explanation**: GPS requires clear sky view
- **Solution**: Move GPS antenna outdoors or near window
- **Expected**: 3-5 minutes to acquire fix outdoors

**2. GPS Not Detected by gpsd**
- **Check**:
  ```bash
  gpsd -V  # Verify gpsd installed
  cat /etc/default/gpsd  # Check configuration
  ```
- **Expected**:
  ```
  DEVICES="/dev/ttyACM0"
  ```
- **Solution**: If DEVICES empty, edit /etc/default/gpsd and restart:
  ```bash
  sudo nano /etc/default/gpsd
  # Set: DEVICES="/dev/ttyACM0"

  sudo systemctl restart gpsd
  ```

**3. USB GPS Not Detected**
- **Check**:
  ```bash
  lsusb  # Should show GPS device
  ls /dev/ttyACM*  # Should show /dev/ttyACM0
  ```
- **Solution**: Unplug GPS, wait 5 seconds, plug back in

**4. gpsd and Signal K Conflict** (Both reading /dev/ttyACM0)
- **Check**: Signal K GPS provider configuration
- **Solution**: Configure Signal K to use gpsd protocol (not serial):
  ```bash
  # Edit ~/.signalk/settings.json
  # GPS provider should use:
  {
    "type": "gpsd",
    "hostname": "localhost",
    "port": 2947
  }
  ```

---

### Problem: GPS Position Shows Movement When Stationary (Drift)

**Symptoms**:
- Boat not moving but GPS shows 2 knots speed
- Course changes randomly (e.g., 100°, 150°, 200°)
- Position "wanders" within 10-30m radius

**Explanation**: **This is normal GPS behavior with weak signals!**

**Cause**: Weak satellite signals (3 satellites, HDOP 3.57) cause position error circle. GPS position "drifts" within this circle, making it look like boat is moving.

**Indoors Accuracy**: ±10-30m (position wanders within error circle)
**Outdoors Accuracy**: ±3-5m with 8+ satellites, HDOP <2.0

**Solution**: Move GPS antenna outdoors for better satellite visibility

**Expected Outdoors**:
- 8+ satellites
- HDOP < 2.0
- 0 knots when stationary
- Stable position (±3-5m)

---

## 5. Camera Issues

### Problem: Marine Vision Page Shows "Camera Not Connected"

**Symptoms**:
- Camera status: ✗ Disconnected
- No live feed displayed

**Causes & Solutions**:

**1. Camera Not Configured**
- **Check**: Camera IP address not set in d3kOS
- **Solution**: Navigate to Settings → Camera → Add Camera
  - IP: 10.42.0.100 (or your camera's IP)
  - Username: admin
  - Password: [your camera password]

**2. Camera Not on Network**
- **Check**: Ping camera from Pi:
  ```bash
  ping 10.42.0.100
  ```
- **Solution**: Verify camera connected to same network (10.42.0.0/24)

**3. Camera Firewall Blocking Pi**
- **Check**: Access camera web interface (http://10.42.0.100)
- **Solution**: Disable camera firewall or whitelist Pi IP (10.42.0.1)

**4. RTSP Not Enabled**
- **Check**: Camera RTSP setting enabled
- **Solution**: Login to camera → Settings → Network → RTSP → Enable

**5. Wrong Credentials**
- **Check**: Verify username/password correct
- **Default**: admin/admin (change after first login!)
- **Solution**: Update credentials in d3kOS Settings → Camera

---

### Problem: Camera Feed Shows Black Screen or "Stream Error"

**Symptoms**:
- Camera status: ✓ Connected
- Feed shows black or "Loading..." never completes

**Causes & Solutions**:

**1. Wrong RTSP Stream** (Main vs Sub)
- **Issue**: Main stream (4K) too high bitrate for Pi 4
- **Solution**: Use sub-stream (720p/1080p) instead
- **RTSP URL**: rtsp://admin:password@10.42.0.100:554/h264Preview_01_sub

**2. Camera Offline**
- **Check**: Power cycle camera
- **Solution**: Unplug camera power, wait 10 seconds, plug back in

**3. Network Congestion**
- **Check**: Other devices using bandwidth
- **Solution**: Reduce camera bitrate in camera settings (2-4 Mbps recommended)

---

## 6. Voice Assistant

### ⚠️ CRITICAL KNOWN ISSUE: Wake Word Detection Not Working

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

**Debugging Steps Attempted**:
1. ✅ Tested microphone hardware (works)
2. ✅ Tested PocketSphinx binary (runs)
3. ✅ Direct hardware access (`-adcdev plughw:3,0`) attempted
4. ❌ PipeWire interference confirmed but bypassing failed
5. ❌ Python subprocess handling broken

**Next Steps** (Future Update):
- Investigate alternative wake word engines (Vosk, Porcupine, Snowboy)
- Rebuild voice assistant from scratch
- Consider PulseAudio instead of PipeWire

**ETA**: Unknown - requires dedicated 2-3 hour debugging session

---

### Problem: Text-Based AI Assistant Not Responding

**Symptoms**:
- Type question in AI Assistant page
- Click Send
- No response appears

**Causes & Solutions**:

**1. AI API Service Not Running**
- **Check**:
  ```bash
  sudo systemctl status d3kos-ai-api
  ```
- **Solution**:
  ```bash
  sudo systemctl restart d3kos-ai-api
  ```

**2. No Internet Connection** (Online AI Queries)
- **Check**: Verify Pi has internet access
  ```bash
  ping 8.8.8.8
  ```
- **Solution**: Connect Pi to internet via Ethernet or cellular modem

**3. OpenRouter API Error**
- **Check**: Logs for API errors
  ```bash
  journalctl -u d3kos-ai-api -n 50
  ```
- **Solution**: May be temporary API issue, retry in 1 minute

---

## 7. Web Interface

### Problem: Web Pages Not Loading or Show 404 Error

**Symptoms**:
- http://d3kos.local loads but pages return 404
- Click navigation buttons → "Page Not Found"

**Causes & Solutions**:

**1. Nginx Not Running**
- **Check**:
  ```bash
  sudo systemctl status nginx
  ```
- **Solution**:
  ```bash
  sudo systemctl restart nginx
  ```

**2. Files Missing**
- **Check**:
  ```bash
  ls /var/www/html/*.html
  ```
- **Solution**: Re-flash SD card (files may be corrupted)

**3. Browser Cache**
- **Solution**: Hard refresh (Ctrl+Shift+R) or clear browser cache

---

### Problem: Pages Load But No Data Displayed

**Symptoms**:
- Dashboard loads but all gauges show 0 or N/A
- Navigation page loads but no GPS position

**Causes & Solutions**:

**1. Signal K Not Running**
- **Check**:
  ```bash
  sudo systemctl status signalk
  ```
- **Solution**:
  ```bash
  sudo systemctl restart signalk
  ```

**2. WebSocket Connection Failed**
- **Check**: Browser console (F12) for WebSocket errors
- **Solution**: Verify nginx proxy configured for WebSocket passthrough

**3. JavaScript Errors**
- **Check**: Browser console (F12) for script errors
- **Solution**: Hard refresh browser or clear cache

---

## 8. Touchscreen

### Problem: Touchscreen Not Responding

**Symptoms**:
- Display shows image but touch input doesn't work
- Can't tap buttons or input fields

**Causes & Solutions**:

**1. USB Touch Cable Not Connected**
- **Check**: USB cable from touchscreen to Raspberry Pi
- **Solution**: Reconnect USB touch cable to blue USB 3.0 port

**2. Touch Device Not Detected**
- **Check**:
  ```bash
  lsusb | grep -i ilitek
  ```
- **Expected**: Should show ILITEK touch device
- **Solution**: Unplug USB, wait 5 seconds, plug back in

**3. Wayland Not Running**
- **Check**:
  ```bash
  ps aux | grep labwc
  ```
- **Solution**:
  ```bash
  sudo systemctl restart display-manager
  ```

**4. Touchscreen Disabled After Voice Service Stop** (Known Issue)
- **Cause**: Stopping d3kos-voice service breaks touchscreen
- **Workaround**: Reboot system to restore touch
  ```bash
  sudo reboot
  ```
- **Prevention**: Don't stop voice service if it's running

---

### Problem: On-Screen Keyboard Doesn't Appear

**Symptoms**:
- Tap input field
- No keyboard appears
- Can't type text

**Causes & Solutions**:

**1. Squeekboard Not Running**
- **Check**:
  ```bash
  ps aux | grep squeekboard
  ```
- **Solution**:
  ```bash
  squeekboard &
  ```

**2. Wayland Text-Input Protocol Not Triggered**
- **Cause**: Input field doesn't have focus
- **Solution**: Tap input field again, or click inside field

**3. Page-Specific Issue** (AI Assistant page)
- **Known Issue**: AI Assistant page keyboard doesn't input text (under investigation)
- **Workaround**: Use other pages (onboarding, settings, helm) where keyboard works

---

## 9. Performance & Storage

### Problem: SD Card Full (Storage Warning)

**Symptoms**:
- Dashboard shows "Storage 97% full"
- System slow or unresponsive
- Media cleanup notification appears

**Causes & Solutions**:

**1. Camera Recordings Filling SD Card**
- **Check**:
  ```bash
  du -sh /home/d3kos/camera-recordings/
  ```
- **Solution**: Transfer recordings to mobile app, then delete from Pi
  ```bash
  # Manual cleanup (deletes recordings older than 3 days)
  find /home/d3kos/camera-recordings/ -type f -mtime +3 -delete
  ```

**2. System Logs Growing**
- **Check**:
  ```bash
  journalctl --disk-usage
  ```
- **Solution**:
  ```bash
  sudo journalctl --vacuum-size=100M
  ```

**3. Small SD Card** (16GB)
- **Recommendation**: Upgrade to 128GB SD card
- **Procedure**: See UPGRADE_GUIDE.md for SD card migration

---

### Problem: System Slow or Laggy

**Symptoms**:
- Pages take >5 seconds to load
- Dashboard update rate <1 Hz
- Voice response time >30 seconds

**Causes & Solutions**:

**1. High CPU Temperature** (Thermal Throttling)
- **Check**:
  ```bash
  vcgencmd measure_temp
  ```
- **Expected**: <80°C
- **Solution**: Add heatsinks or fan to Raspberry Pi, improve enclosure ventilation

**2. Low Memory** (Swapping)
- **Check**:
  ```bash
  free -h
  ```
- **Solution**: Restart services or reboot
  ```bash
  sudo systemctl restart signalk nodered nginx
  ```

**3. Too Many Services Running**
- **Check**:
  ```bash
  systemctl list-units --state=running
  ```
- **Solution**: Disable unused services (advanced)

---

## 10. System Recovery

### Problem: System Completely Broken (Last Resort)

**Solution 1: Re-Flash SD Card**
1. Power off Raspberry Pi
2. Remove SD card
3. Re-flash with d3kOS image (see INSTALLATION_GUIDE.md)
4. Boot and complete Initial Setup wizard again

**Solution 2: Factory Reset** (Initial Setup Reset)
- Navigate to Settings → System → Initial Setup Reset
- Confirms and resets to Step 0 of wizard
- All configuration lost (backup first!)

**Solution 3: Fresh Start**
- Download latest d3kOS image from GitHub Releases
- Flash to new SD card
- Start from scratch

---

## 📞 Getting Additional Help

**Troubleshooting Priority**:
1. Check this guide first
2. Search GitHub Discussions for similar issues
3. Check GitHub Issues for known bugs
4. Post new question in GitHub Discussions

**Reporting Bugs**:
- GitHub Issues: https://github.com/SkipperDon/d3kos/issues
- Include: d3kOS version, hardware model, error messages, steps to reproduce

**Community Support**:
- GitHub Discussions: https://github.com/SkipperDon/d3kos/discussions
- At My Boat: https://atmyboat.com

**Log Collection** (for bug reports):
```bash
# Collect system logs
journalctl -b > /tmp/d3kos-logs.txt

# Collect service logs
sudo systemctl status signalk nodered nginx d3kos-* >> /tmp/d3kos-logs.txt

# Upload to GitHub issue
```

---

**Document Version**: 1.0.3
**Last Updated**: February 18, 2026
**Maintainer**: SkipperDon (https://atmyboat.com)
