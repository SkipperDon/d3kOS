# Post-Deployment Fixes Implementation Plan

**Date:** February 20, 2026
**Version:** 0.9.1.2
**Issues:** 2 (Chromium Session Restore, WiFi/Hotspot Switching)
**Deferred:** 1 (Keyring password - user requested to leave as-is)

---

## Executive Summary

This document provides a comprehensive plan to address two post-deployment issues identified after Sessions A, B, C, and D were completed:

1. **Chromium Session Restore Prompt** - Browser continues asking to restore session after reboot
2. **WiFi/Hotspot Switching** - Devices cannot connect when switched to hotspot mode, needs GUI control

**Estimated Total Time:** 2-3 hours
**Priority:** Medium (system functional but user experience affected)

---

## Issue 1: Chromium Session Restore Prompt

### Current State

**File:** `/home/d3kos/.config/autostart/d3kos-browser.desktop`

**Current Flags:**
```
--start-fullscreen
--noerrdialogs
--disable-infobars
--no-first-run
--check-for-update-interval=31536000
--disable-session-crashed-bubble
--disable-translate
--disable-features=TranslateUI
```

**Problem:** Despite having `--disable-session-crashed-bubble`, Chromium still shows "Restore pages?" prompt after reboot.

### Root Cause Analysis

Based on research ([Chromium Forums](https://groups.google.com/a/chromium.org/g/chromium-discuss/c/vYNex39C-rw), [Raspberry Pi Forums](https://forums.raspberrypi.com/viewtopic.php?t=212015), [Martin Pennock Blog](http://martinpennock.com/blog/disable-restore-session-bubble-chromium-raspberry-pi/)):

**The issue has TWO components:**

1. **Command-line flags** - Partially addressed (--disable-session-crashed-bubble present)
2. **Chromium Preferences file** - NOT addressed (stores session state)

**Why the flag alone doesn't work:**
- Chromium checks `~/.config/chromium/Default/Preferences` for:
  - `"exited_cleanly": false` - Set when Chromium doesn't shut down properly
  - `"exit_type": "Crashed"` - Set when session ends unexpectedly
- These settings override the command-line flag and trigger the restore prompt

### Proposed Solution

**Two-pronged approach:**

#### Solution 1A: Additional Chromium Flags

Add missing flags to `/home/d3kos/.config/autostart/d3kos-browser.desktop`:

```bash
--disable-session-crashed-bubble  # Already present
--hide-crash-restore-bubble       # Additional flag
--no-crash-upload                 # Disable crash reporting
```

#### Solution 1B: Preferences File Modification

Create a startup script that resets Chromium preferences before launch:

**File:** `/opt/d3kos/scripts/reset-chromium-session.sh`

```bash
#!/bin/bash
# Reset Chromium session state to prevent restore prompt

PREFS="/home/d3kos/.config/chromium/Default/Preferences"

if [ -f "$PREFS" ]; then
    # Set exited_cleanly to true and exit_type to Normal
    python3 <<EOF
import json
with open('$PREFS', 'r') as f:
    prefs = json.load(f)

prefs['profile'] = prefs.get('profile', {})
prefs['profile']['exited_cleanly'] = True
prefs['profile']['exit_type'] = 'Normal'

with open('$PREFS', 'w') as f:
    json.dump(prefs, f, indent=2)
EOF
fi
```

**Modify d3kos-browser.desktop:**
```
[Desktop Entry]
Type=Application
Name=d3kOS Browser
Exec=/bin/bash -c '/opt/d3kos/scripts/reset-chromium-session.sh && /usr/bin/chromium --start-fullscreen --noerrdialogs --disable-infobars --no-first-run --check-for-update-interval=31536000 --disable-session-crashed-bubble --hide-crash-restore-bubble --disable-translate --disable-features=TranslateUI http://localhost/'
```

### Implementation Steps

**Step 1: Create reset script** (5 minutes)
```bash
sudo nano /opt/d3kos/scripts/reset-chromium-session.sh
# Paste script from Solution 1B above
sudo chmod +x /opt/d3kos/scripts/reset-chromium-session.sh
```

**Step 2: Test script** (2 minutes)
```bash
/opt/d3kos/scripts/reset-chromium-session.sh
# Check Preferences file modified correctly
cat ~/.config/chromium/Default/Preferences | jq '.profile.exited_cleanly, .profile.exit_type'
```

**Step 3: Update autostart file** (3 minutes)
```bash
sudo cp /home/d3kos/.config/autostart/d3kos-browser.desktop \
        /home/d3kos/.config/autostart/d3kos-browser.desktop.bak.session-fix

sudo nano /home/d3kos/.config/autostart/d3kos-browser.desktop
# Update Exec= line with reset script call
```

**Step 4: Test reboot** (5 minutes)
```bash
sudo reboot
# After reboot, verify no restore prompt appears
# Check Chromium opens directly to http://localhost/
```

### Testing Checklist

- [ ] Reset script creates/modifies Preferences file correctly
- [ ] Script sets `exited_cleanly` to `true`
- [ ] Script sets `exit_type` to `"Normal"`
- [ ] Chromium launches without restore prompt after normal reboot
- [ ] Chromium launches without restore prompt after power cycle (simulate power loss)
- [ ] Kiosk mode still functional (fullscreen, no browser chrome)
- [ ] All other Chromium flags still working

### Rollback Plan

If solution causes issues:

```bash
# Restore original autostart file
sudo cp /home/d3kos/.config/autostart/d3kos-browser.desktop.bak.session-fix \
        /home/d3kos/.config/autostart/d3kos-browser.desktop

# Remove reset script
sudo rm /opt/d3kos/scripts/reset-chromium-session.sh

# Reboot
sudo reboot
```

### Expected Outcome

✅ Chromium opens directly to http://localhost/ without any restore session prompts
✅ Kiosk mode fully functional
✅ System boots to fullscreen browser in <60 seconds

---

## Issue 2: WiFi/Hotspot Switching

### Current State

**NetworkManager Connections:**

**Home Network (Active):**
- SSID: `netplan-wlan0-MMN18`
- Status: Connected
- Mode: Client (infrastructure)

**Hotspot (Configured but Inactive):**
- SSID: `d3kOS`
- Password: `d3kos-2026`
- Mode: `ap` (access point)
- Method: `shared`
- Security: `wpa-psk`
- **autoconnect: false** (won't auto-start)

**Problem:** When user activates hotspot, devices cannot connect/login.

### Root Cause Analysis

Based on research ([NetworkManager WPA-PSK Issues](https://forums.gentoo.org/viewtopic-t-1091102-start-0.html), [Raspberry Pi Issue #6265](https://github.com/raspberrypi/linux/issues/6265), [Ubuntu Bug #1871710](https://bugs.launchpad.net/bugs/1871710)):

**Three potential causes:**

#### Cause 1: WPA-PSK Compatibility Issues
- NetworkManager enables WPA2/WPA3 compatibility mode by default
- Some devices (ESP32, older Windows 10, some Android) cannot connect to WPA2-only hotspots
- Issue related to WPA-PSK-SHA256 or RSN configuration
- **Solution:** Downgrade to WPA-PSK (not WPA2-PSK) or add WPA/WPA2 mixed mode

#### Cause 2: Missing dnsmasq or Incorrect DHCP Configuration
- Hotspot needs DHCP server to assign IP addresses to clients
- NetworkManager uses dnsmasq for "shared" method
- If dnsmasq not installed or misconfigured, clients connect but get no IP
- **Solution:** Verify dnsmasq installed and configured

#### Cause 3: Channel Selection
- Some regions/channels restricted or conflicting
- Raspberry Pi may auto-select channel that client devices don't support
- **Solution:** Force specific channel (1, 6, or 11 for 2.4GHz)

### Proposed Solutions

#### Solution 2A: Fix WPA-PSK Compatibility (Recommended)

**Modify hotspot connection to use WPA/WPA2 mixed mode:**

```bash
# Edit hotspot connection
sudo nmcli connection modify d3kOS \
    wifi-sec.key-mgmt wpa-psk \
    wifi-sec.proto rsn,wpa \
    wifi-sec.pairwise ccmp,tkip \
    wifi-sec.group ccmp,tkip
```

**Explanation:**
- `wifi-sec.proto rsn,wpa` - Enable both WPA2 (rsn) and WPA (wpa)
- `wifi-sec.pairwise ccmp,tkip` - Support both modern (CCMP) and legacy (TKIP) ciphers
- `wifi-sec.group ccmp,tkip` - Same for group ciphers
- Increases compatibility at slight security cost (acceptable for boat hotspot)

#### Solution 2B: Verify dnsmasq Installation

```bash
# Check if dnsmasq installed
dpkg -l | grep dnsmasq

# Install if missing
sudo apt-get install dnsmasq

# Verify NetworkManager using dnsmasq for shared connections
cat /etc/NetworkManager/NetworkManager.conf | grep dns
# Should show: dns=dnsmasq
```

#### Solution 2C: Force WiFi Channel

```bash
# Force channel 6 (most compatible)
sudo nmcli connection modify d3kOS \
    wifi.channel 6 \
    wifi.band bg
```

#### Solution 2D: GUI for WiFi/Hotspot Switching

**Option 1: nmtui (Text-based GUI - Simplest)**

Already installed with NetworkManager, accessible via:
```bash
nmtui
```

**Option 2: nm-applet (Graphical - Better UX)**

Install GNOME Network Manager applet:
```bash
sudo apt-get install network-manager-gnome
```

Add to autostart for d3kos user (optional):
```bash
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/nm-applet.desktop <<EOF
[Desktop Entry]
Type=Application
Name=Network Manager Applet
Exec=nm-applet
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF
```

**Option 3: Custom d3kOS Settings Page (Best Integration)**

Create `/var/www/html/settings-network.html`:

Features:
- Show current WiFi connection (SSID, signal strength)
- "Switch to Hotspot" button (activates d3kOS hotspot)
- "Switch to WiFi" button (deactivates hotspot, connects to available WiFi)
- List available WiFi networks
- Show hotspot status (SSID, password, connected devices)
- d3kOS theme (black/green, touch-optimized)

Backend API endpoints (new service):
- `GET /network/status` - Current connection info
- `POST /network/hotspot/enable` - Activate hotspot
- `POST /network/hotspot/disable` - Deactivate hotspot
- `GET /network/wifi/scan` - List available networks
- `POST /network/wifi/connect` - Connect to WiFi network

**Estimated Development Time:** 3-4 hours

### Implementation Steps

#### Phase 1: Fix Hotspot Compatibility (30 minutes)

**Step 1: Apply WPA/WPA2 mixed mode** (5 minutes)
```bash
sudo nmcli connection modify d3kOS \
    wifi-sec.key-mgmt wpa-psk \
    wifi-sec.proto rsn,wpa \
    wifi-sec.pairwise ccmp,tkip \
    wifi-sec.group ccmp,tkip \
    wifi.channel 6 \
    wifi.band bg

# Verify changes
nmcli connection show d3kOS | grep -E "wifi-sec|wifi.channel|wifi.band"
```

**Step 2: Verify dnsmasq** (5 minutes)
```bash
dpkg -l | grep dnsmasq
# If not installed:
# sudo apt-get install dnsmasq
```

**Step 3: Test hotspot activation** (10 minutes)
```bash
# Disconnect from home WiFi
nmcli connection down "netplan-wlan0-MMN18"

# Activate hotspot
nmcli connection up d3kOS

# Check hotspot active
nmcli connection show --active
# Should show d3kOS active

# Test with phone/laptop
# SSID: d3kOS
# Password: d3kos-2026
```

**Step 4: Test client connection** (10 minutes)
- Connect phone to d3kOS hotspot
- Verify IP address assigned (192.168.x.x)
- Test internet access (if Pi has ethernet/LTE)
- Check ping to Pi (should be 192.168.x.1)

#### Phase 2: GUI Solution (Choose ONE)

**Option A: nmtui (Immediate, No Development)**

Test nmtui interface:
```bash
nmtui
# Navigate: Activate a connection
# Test: Switch between d3kOS (hotspot) and netplan-wlan0-MMN18 (WiFi)
```

**Pros:** Already installed, no development needed
**Cons:** Text-based UI, not touch-optimized, requires keyboard

**Option B: nm-applet (Quick, 15 minutes)**

```bash
# Install
sudo apt-get install network-manager-gnome

# Test (from VNC session)
nm-applet &

# Add to autostart if works well
```

**Pros:** Graphical, familiar interface
**Cons:** Requires desktop environment, not d3kOS-themed

**Option C: Custom d3kOS Settings Page (Best, 3-4 hours)**

See **Appendix A** for full implementation guide.

**Pros:** Touch-optimized, d3kOS theme, user-friendly
**Cons:** Development time required

### Testing Checklist

**Phase 1 (Hotspot Fix):**
- [ ] WPA/WPA2 mixed mode applied to d3kOS connection
- [ ] Channel 6 forced
- [ ] dnsmasq installed and running
- [ ] Hotspot activates successfully (`nmcli connection up d3kOS`)
- [ ] Phone/laptop can connect to d3kOS hotspot
- [ ] Client receives IP address (192.168.x.x)
- [ ] Client has internet access (if Pi has backhaul)
- [ ] Multiple devices can connect simultaneously
- [ ] Hotspot deactivates cleanly (`nmcli connection down d3kOS`)
- [ ] Can reconnect to home WiFi after hotspot deactivation

**Phase 2 (GUI):**
- [ ] Chosen GUI method accessible (nmtui / nm-applet / custom page)
- [ ] Can switch from WiFi to hotspot via GUI
- [ ] Can switch from hotspot to WiFi via GUI
- [ ] GUI shows current connection status
- [ ] GUI works with touchscreen (if applicable)
- [ ] Changes persist across reboots

### Rollback Plan

If hotspot changes cause issues:

```bash
# Revert to original configuration
sudo nmcli connection modify d3kOS \
    wifi-sec.key-mgmt wpa-psk \
    wifi-sec.proto rsn \
    wifi-sec.pairwise ccmp \
    wifi-sec.group ccmp

# Remove forced channel
sudo nmcli connection modify d3kOS \
    wifi.channel 0

# Reload connection
sudo nmcli connection reload
```

### Expected Outcome

✅ Devices can connect to d3kOS hotspot (SSID: d3kOS, password: d3kos-2026)
✅ Clients receive IP addresses and have network access
✅ Hotspot can be activated/deactivated via GUI (nmtui or custom page)
✅ Can switch between home WiFi and hotspot mode easily
✅ Configuration persists across reboots

---

## Issue 3: Keyring Password (DEFERRED)

**Status:** ⏳ Deferred per user request

**User Quote:** "Lets leave the keyring for now"

**Current State:**
- Keyring password set to "pi"
- File: `~/.local/share/keyrings/Default_Keyring.keyring`

**Recommendation:** Address in future session if keyring prompts become intrusive.

---

## Implementation Order

### Recommended Sequence

**Session E (Quick Fixes):**
1. **Issue 1: Chromium Session Restore** (~30 minutes)
   - Create reset-chromium-session.sh script
   - Update d3kos-browser.desktop autostart
   - Test reboot
   - **Low risk, high impact**

2. **Issue 2A: Hotspot Compatibility Fix** (~30 minutes)
   - Apply WPA/WPA2 mixed mode
   - Force channel 6
   - Verify dnsmasq
   - Test client connection
   - **Medium risk, high impact**

3. **Issue 2B: GUI Solution** (~15 minutes OR 3-4 hours)
   - **Quick:** Install nm-applet and test
   - **Best:** Develop custom d3kOS network settings page
   - **User choice based on urgency**

**Total Time (Quick Path):** 1.5 hours
**Total Time (Best Path):** 4-5 hours

### Parallel Development Option

If user wants comprehensive solution:
- **Session E:** Chromium + Hotspot fix + nmtui setup (1.5 hours)
- **Session F:** Custom network settings page development (3-4 hours)

---

## Risk Assessment

| Issue | Risk Level | Impact if Not Fixed | Mitigation |
|-------|-----------|---------------------|------------|
| Chromium Session Restore | Low | User annoyance on every reboot | Comprehensive testing, easy rollback |
| Hotspot Connection Failure | Medium | Cannot use d3kOS as hotspot | Gradual changes (WPA mode → channel → dnsmasq), test each step |
| GUI for Network Switching | Low | Manual nmcli commands required | Multiple options (nmtui, nm-applet, custom), choose simplest first |

---

## Success Criteria

### Issue 1: Chromium
- ✅ No restore session prompt after reboot
- ✅ No restore session prompt after power cycle
- ✅ Kiosk mode fully functional
- ✅ Boot time <60 seconds maintained

### Issue 2: WiFi/Hotspot
- ✅ Multiple devices (phone, laptop, tablet) can connect to d3kOS hotspot
- ✅ Clients receive IP addresses automatically
- ✅ GUI method available for switching modes
- ✅ Easy to switch between home WiFi and hotspot
- ✅ Configuration survives reboots

---

## Appendix A: Custom Network Settings Page (Optional)

**File:** `/var/www/html/settings-network.html`

**Features:**
- Current connection status (SSID, signal strength, IP address)
- WiFi scan results with signal bars
- "Switch to Hotspot" button (large, touch-friendly)
- "Connect to WiFi" button
- Hotspot status panel (SSID, password, connected clients count)
- d3kOS theme (black background, green accents, 22px+ fonts)

**Backend Service:** `/opt/d3kos/services/network/network-api.py`

**API Endpoints:**
- `GET /network/status` - JSON with current connection info
- `POST /network/hotspot/enable` - Activates d3kOS hotspot
- `POST /network/hotspot/disable` - Deactivates hotspot
- `GET /network/wifi/scan` - Returns available WiFi networks
- `POST /network/wifi/connect` - Connects to specified network (requires SSID + password)
- `GET /network/hotspot/clients` - Lists connected devices (MAC, IP, hostname)

**Systemd Service:** `d3kos-network-api.service` (port 8101)

**Nginx Proxy:** `/network/` → `localhost:8101/network/`

**Development Time:** 3-4 hours
**Estimated Size:** ~10KB HTML + ~5KB Python

**Note:** This is OPTIONAL and can be deferred if nmtui or nm-applet are sufficient.

---

## References

**Chromium Session Restore:**
- [Chromium Forums - Disable session restore](https://groups.google.com/a/chromium.org/g/chromium-discuss/c/vYNex39C-rw)
- [Raspberry Pi Forums - Chromium restore session](https://forums.raspberrypi.com/viewtopic.php?t=212015)
- [Martin Pennock - Disable restore bubble](http://martinpennock.com/blog/disable-restore-session-bubble-chromium-raspberry-pi/)
- [Chromium Bug #445256 - Kiosk restore bubble](https://bugs.chromium.org/p/chromium/issues/detail?id=445256)

**NetworkManager Hotspot:**
- [NetworkManager WPA-PSK Issues (Gentoo Forums)](https://forums.gentoo.org/viewtopic-t-1091102-start-0.html)
- [Raspberry Pi Linux Issue #6265 - WPA-PSK key management](https://github.com/raspberrypi/linux/issues/6265)
- [Ubuntu Bug #1871710 - WiFi hotspot WPA/WPA2 security](https://bugs.launchpad.net/bugs/1871710)
- [Arch Linux - Wireless hotspot issue](https://bbs.archlinux.org/viewtopic.php?id=275540)

**NetworkManager GUI:**
- [NetworkManager ArchWiki](https://wiki.archlinux.org/title/NetworkManager)
- [Create WiFi Hotspot using nmcli (GitHub Gist)](https://gist.github.com/narate/d3f001c97e1c981a59f94cd76f041140)
- [Baeldung - Creating Wireless Access Point with nmcli](https://www.baeldung.com/linux/nmcli-wap-sharing-internet)

---

**Plan Status:** ✅ READY FOR REVIEW

**Next Step:** User approval to proceed with implementation (Session E)

**Estimated Total Time:**
- Quick path (nmtui): 1.5 hours
- Best path (custom settings page): 4-5 hours

**Recommendation:** Start with quick path (Issue 1 + Issue 2A + nmtui), then develop custom settings page in separate session if needed.
