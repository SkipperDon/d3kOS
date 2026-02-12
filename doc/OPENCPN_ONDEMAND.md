# OpenCPN On-Demand Installation

**Feature Status:** 🚧 Infrastructure Built - Awaiting User Configuration
**Implementation Date:** 2026-02-09

## Overview

OpenCPN (Open Source Chartplotter and Marine GPS Navigation Software) is available as an on-demand installation in d3kOS. This feature allows charts/navigation software to be installed only when needed, saving 200-500MB of disk space when not in use.

The system automatically preserves configuration settings, so reinstallation requires no user setup - it's ready to use immediately.

## User Experience

### First Time Use
1. User clicks **"Charts"** button on main menu
2. System displays "Installing Chartplotter..." (30-60 seconds)
3. OpenCPN installs with default configuration
4. Application launches automatically
5. User configures OpenCPN for their boat
6. Configuration is saved for future use
7. OpenCPN uninstalled to free space

### Subsequent Uses
1. User clicks **"Charts"** button
2. System checks if installed:
   - **If yes:** Launches immediately
   - **If no:** Auto-installs with saved config (30-60 seconds), then launches
3. OpenCPN opens with user's saved settings

## Technical Architecture

### Components

**Main Menu Button:**
- Label: "Charts"
- Location: Row 2, Position 1 (main menu grid)
- Icon: Map/navigation icon
- Action: POST to `http://localhost:1880/launch-opencpn`

**Node-RED Flow:**
```
[HTTP IN: POST /launch-opencpn]
    ↓
[exec: /home/d3kos/install-opencpn.sh]
    ↓
[HTTP Response: 200 OK]
```

**Installation Script Flow:**
```
install-opencpn.sh
    ↓
Check if OpenCPN installed
    ↓
    NO → Install via apt
    ↓
Check for saved config
    ↓
    YES → Restore from backup
    NO → Use defaults
    ↓
Launch OpenCPN
```

### File Structure

```
/home/boatiq/Helm-OS/
├── scripts/
│   ├── install-opencpn.sh          # Auto-install + restore config
│   ├── backup-opencpn-config.sh    # Save current config
│   ├── restore-opencpn-config.sh   # Restore saved config
│   ├── uninstall-opencpn.sh        # Remove to free space
│   └── README.md                    # Script documentation
├── configs/
│   └── opencpn/
│       └── .opencpn/                # Saved configuration (created after first config)
│           ├── opencpn.conf         # Main config file
│           ├── navobj.xml           # Navigation objects
│           └── [chart data]         # Chart files and plugins
└── index.html                       # Main menu (Charts button)
```

**On Raspberry Pi:**
```
/home/d3kos/
├── install-opencpn.sh
├── backup-opencpn-config.sh
├── restore-opencpn-config.sh
├── uninstall-opencpn.sh
└── .opencpn/                        # Runtime configuration (when installed)
    ├── opencpn.conf
    ├── navobj.xml
    └── [charts]
```

## Configuration Workflow

### Phase 1: Initial Configuration (With User)

**Status:** 🔴 Not Yet Done - Waiting for user

When user returns from break, we will:

1. **Install OpenCPN:**
   ```bash
   ssh d3kos@192.168.1.237
   ./install-opencpn.sh
   ```

2. **Configure for User's Boat:**
   - **GPS/NMEA Connection:** Connect to Signal K server
   - **Display Settings:**
     - Dark theme to match d3kOS
     - Large fonts for 10.1" touchscreen
     - Nautical units (knots, nautical miles, feet)
   - **Chart Data:**
     - Download NOAA charts for user's area
     - Configure chart sources
   - **Plugins:**
     - Install any needed plugins (AIS, weather, etc.)
   - **Window Settings:**
     - Set default window size/position
     - Configure toolbar layout

3. **Test with Live Data:**
   - Verify GPS position displays
   - Check NMEA2000 data integration
   - Test navigation features
   - Confirm display is readable

4. **Save Configuration:**
   ```bash
   ssh d3kos@192.168.1.237
   ./backup-opencpn-config.sh
   ```

   This creates: `/home/boatiq/Helm-OS/configs/opencpn/.opencpn/`

5. **Transfer Config to Development Machine:**
   ```bash
   scp -r d3kos@192.168.1.237:.opencpn /home/boatiq/Helm-OS/configs/opencpn/
   ```

6. **Uninstall to Free Space:**
   ```bash
   ssh d3kos@192.168.1.237
   ./uninstall-opencpn.sh
   ```

   This removes OpenCPN but keeps saved config.

### Phase 2: Automatic Restoration (Every Subsequent Use)

1. User clicks "Charts" button
2. `install-opencpn.sh` runs automatically:
   - Installs OpenCPN package
   - Restores saved configuration from backup
   - Launches OpenCPN
3. User sees their configured environment immediately

## OpenCPN Configuration Details

### Signal K Integration

OpenCPN can receive GPS and NMEA data from Signal K server via TCP connection.

**Configuration:**
- Connection Type: Network (TCP)
- Address: localhost
- Port: 10110 (Signal K output port)
- Protocol: NMEA 0183
- Data: GPS position, COG, SOG, depth, wind, AIS

**Signal K Setup:**
```javascript
// Configure Signal K to output NMEA 0183 on TCP port 10110
// This allows OpenCPN to receive all marine data
```

### Display Preferences

**To Match d3kOS Design:**
- Color Scheme: Dark
- Chart Brightness: Adjusted for night use
- Font Size: Large (for 10.1" touchscreen)
- Toolbar: Simplified, touch-friendly icons
- Units: Nautical (knots, nm, feet)

### Chart Sources

**Free NOAA Charts:**
- Download from: http://www.nauticalcharts.noaa.gov/mcd/Raster/
- Format: RNC (Raster Nautical Charts)
- Coverage: US coastal and inland waters

**Chart Manager:**
- Configure chart directories
- Set priority/order
- Enable chart quilting

### Plugins

**Potentially Useful:**
- **WMM (World Magnetic Model):** Magnetic variation
- **Dashboard:** Instrument display
- **AIS Radar:** AIS target display
- **Weather Routing:** Route optimization
- **Weatherfax:** Weather fax reception

## Disk Space Management

**OpenCPN Package Size:**
- Base package: ~50MB
- Dependencies: ~150MB
- Charts (varies): 50-500MB+
- **Total:** 200-700MB depending on chart coverage

**Space Saved When Uninstalled:**
- Package + dependencies: ~200MB
- Charts remain in saved config: Can be excluded if needed
- Config files: ~1-5MB (settings only)

**Current Pi Storage:**
- Total: 32GB SD card
- Used: ~25GB (78%)
- Free: ~7GB
- **Savings from on-demand install:** 200-700MB

## Testing

### Infrastructure Testing (Completed)

✅ **Scripts Created:**
- install-opencpn.sh
- backup-opencpn-config.sh
- restore-opencpn-config.sh
- uninstall-opencpn.sh

✅ **Node-RED Flow:**
- Endpoint: POST /launch-opencpn
- Executes: install-opencpn.sh
- Returns: 200 OK

✅ **Main Menu:**
- Button: "Charts" (replaced "OpenCPN (Coming Soon)")
- Icon: Map/navigation icon
- Navigation: POSTs to Node-RED endpoint

### Configuration Testing (Pending User)

🔴 **Not Yet Done:**
- OpenCPN installation and configuration
- Signal K integration testing
- Chart data installation
- Display preferences setup
- Configuration backup/restore testing
- Uninstall and reinstall cycle testing

## Benefits

✅ **Disk Space Savings:** 200-700MB freed when not in use
✅ **Zero Configuration:** Automatic restoration of settings
✅ **Always Updated:** Fresh package install each time
✅ **Version Control:** Config can be tracked in git
✅ **Consistent Setup:** Same configuration every reinstall
✅ **On-Demand:** Only installed when actually needed

## Limitations

⚠ **Installation Time:** 30-60 seconds on first launch (per session)
⚠ **Chart Data:** Large chart collections increase install time
⚠ **Internet Required:** Initial install needs package download
⚠ **Config Drift:** Manual changes not saved unless backup is run

## Troubleshooting

### Charts Button Does Nothing

**Diagnosis:**
```bash
# Test Node-RED endpoint
curl -X POST http://localhost:1880/launch-opencpn

# Check script permissions
ssh d3kos@192.168.1.237 "ls -l /home/d3kos/install-opencpn.sh"
```

**Solutions:**
- Verify Node-RED is running
- Check script is executable
- Review Node-RED debug logs

### OpenCPN Won't Launch

**Diagnosis:**
```bash
# Try manual installation
ssh d3kos@192.168.1.237
./install-opencpn.sh

# Check for errors
journalctl -xe | grep opencpn
```

**Solutions:**
- Check display server (Wayland/X11)
- Verify graphics drivers
- Try running: `DISPLAY=:0 opencpn`

### Configuration Not Restored

**Diagnosis:**
```bash
# Check backup exists
ls -la /home/boatiq/Helm-OS/configs/opencpn/.opencpn/

# Check contents
du -sh /home/boatiq/Helm-OS/configs/opencpn/.opencpn/
```

**Solutions:**
- Verify backup was created: `./backup-opencpn-config.sh`
- Manually restore: `./restore-opencpn-config.sh`
- Reconfigure and save again

### Want to Update Configuration

**Process:**
```bash
# 1. Install if needed
./install-opencpn.sh

# 2. Make configuration changes in OpenCPN GUI

# 3. Save new configuration
./backup-opencpn-config.sh

# 4. Copy to development machine
scp -r d3kos@192.168.1.237:.opencpn /home/boatiq/Helm-OS/configs/opencpn/

# 5. Uninstall to free space
./uninstall-opencpn.sh
```

## Next Steps

### When User Returns:

1. ✅ **Infrastructure Complete:** Scripts, flows, button ready
2. 🔴 **Configure OpenCPN:** Set up for user's boat
3. 🔴 **Test Integration:** Verify Signal K data flows
4. 🔴 **Save Configuration:** Backup settings
5. 🔴 **Test Restore:** Uninstall and reinstall to verify
6. 🔴 **Document Settings:** Record configuration choices

### Future Enhancements:

- **Progress Indicator:** Show installation progress to user
- **Chart Downloads:** Auto-download charts for user's location
- **Plugin Manager:** Easy plugin install/removal
- **Config Profiles:** Multiple saved configurations
- **Cloud Sync:** Sync config across multiple devices

## References

- **OpenCPN Website:** https://opencpn.org/
- **OpenCPN Manual:** https://opencpn.org/OpenCPN/info/downloads.html
- **Signal K Integration:** https://github.com/SignalK/signalk-server
- **NOAA Charts:** http://www.nauticalcharts.noaa.gov/mcd/Raster/
- **Debian Package:** https://packages.debian.org/trixie/opencpn

---

**Document Version:** 1.0
**Status:** Infrastructure Complete - Awaiting User Configuration
**Last Updated:** 2026-02-09
**Author:** Claude (d3kOS Development)
