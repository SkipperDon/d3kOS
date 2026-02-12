# d3kOS Scripts

Utility scripts for managing d3kOS components.

## OpenCPN On-Demand Installation

OpenCPN can be installed on-demand to save disk space when not in use. The configuration is saved and automatically restored on reinstall.

### User Experience

**From Main Menu:**
1. User clicks **"Charts"** button
2. If OpenCPN not installed:
   - System shows "Installing..."
   - Auto-installs OpenCPN (~200-500MB)
   - Restores saved configuration
   - Launches OpenCPN
3. If OpenCPN already installed:
   - Launches immediately

### Scripts

#### `install-opencpn.sh`
Installs OpenCPN and restores saved configuration.

```bash
./install-opencpn.sh
```

**What it does:**
- Checks if OpenCPN is already installed
- If not, installs via apt
- Restores configuration from `../configs/opencpn/.opencpn/`
- Launches OpenCPN

**Used by:**
- Main menu "Charts" button → Node-RED endpoint → this script

#### `backup-opencpn-config.sh`
Saves current OpenCPN configuration for future reinstalls.

```bash
./backup-opencpn-config.sh
```

**What it does:**
- Backs up `~/.opencpn/` to `../configs/opencpn/.opencpn/`
- Preserves all settings, charts, plugins

**When to use:**
- After configuring OpenCPN for the first time
- After making any configuration changes you want to keep
- Before uninstalling

#### `restore-opencpn-config.sh`
Restores saved configuration to current system.

```bash
./restore-opencpn-config.sh
```

**What it does:**
- Restores `../configs/opencpn/.opencpn/` to `~/.opencpn/`
- Backs up existing config if present
- Useful for manual restore or troubleshooting

#### `uninstall-opencpn.sh`
Removes OpenCPN to free disk space.

```bash
./uninstall-opencpn.sh
```

**What it does:**
- Prompts to backup configuration if not already saved
- Removes OpenCPN package
- Optionally removes local configuration
- Preserves saved configuration in `../configs/opencpn/`

**When to use:**
- After testing and saving configuration
- To free up disk space (~200-500MB)
- Configuration will be restored automatically on next install

### Configuration Workflow

**Initial Setup (Do with user):**
1. Install OpenCPN: `./install-opencpn.sh`
2. Configure OpenCPN:
   - Connect to Signal K for GPS/NMEA data
   - Set display preferences (fonts, colors, units)
   - Add chart data
   - Configure plugins
   - Test with live boat data
3. Save configuration: `./backup-opencpn-config.sh`
4. Uninstall to free space: `./uninstall-opencpn.sh`

**Subsequent Use (Automatic):**
1. User clicks "Charts" button
2. System auto-installs with saved config
3. OpenCPN launches ready to use

### File Locations

**Installed Scripts (on Pi):**
- `/home/d3kos/install-opencpn.sh`
- `/home/d3kos/backup-opencpn-config.sh`
- `/home/d3kos/restore-opencpn-config.sh`
- `/home/d3kos/uninstall-opencpn.sh`

**Configuration Backup (on development machine):**
- `/home/boatiq/Helm-OS/configs/opencpn/.opencpn/`
- Contains: `opencpn.conf`, chart data, plugins, settings

**OpenCPN Runtime Config (on Pi):**
- `/home/d3kos/.opencpn/`
- Created on first run
- Saved/restored by scripts

### Node-RED Integration

**Endpoint:** `POST http://localhost:1880/launch-opencpn`

**Flow:**
```
[HTTP IN] → [exec: install-opencpn.sh] → [HTTP Response 200]
```

**Called by:**
- Main menu index.html "Charts" button

### Notes

- OpenCPN package size: ~200-500MB (varies with dependencies)
- First install takes 30-60 seconds
- Subsequent launches: immediate (if already installed)
- Configuration includes: settings, charts, plugins, window position
- Saved configs should be version controlled in Helm-OS repo

### Troubleshooting

**Charts button does nothing:**
```bash
# Check Node-RED endpoint
curl -X POST http://localhost:1880/launch-opencpn

# Check script is executable
ls -l /home/d3kos/install-opencpn.sh
```

**OpenCPN won't launch:**
```bash
# Try manual installation
ssh d3kos@192.168.1.237
./install-opencpn.sh
```

**Configuration not restored:**
```bash
# Check backup exists
ls -la /home/boatiq/Helm-OS/configs/opencpn/.opencpn/

# Manually restore
ssh d3kos@192.168.1.237
./restore-opencpn-config.sh
```

**Want to reset OpenCPN:**
```bash
# Remove config and start fresh
rm -rf ~/.opencpn
opencpn  # Will create new default config
```

---

**Last Updated:** 2026-02-09
**Author:** Claude (d3kOS Development)
