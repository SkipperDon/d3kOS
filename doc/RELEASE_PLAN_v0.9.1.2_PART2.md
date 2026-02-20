# d3kOS v0.9.1.2 Release Plan - Part 2

**Continuation of SESSION C & SESSION D**

---

## SESSION C: DATA EXPORT & BACKUP (Continued)

### Task C3: Backup & Restore System (Continued)

#### Step C3.1: Create Backup Script (Continued)

```bash
#!/bin/bash
# d3kOS Backup Script
# Creates full system backup to USB drive

set -e

BACKUP_DIR="/media/d3kos/6233-3338/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="d3kos_backup_${TIMESTAMP}"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

echo "🔄 Creating d3kOS backup: $BACKUP_NAME"

# Create backup directory
mkdir -p "$BACKUP_PATH"

# Backup databases
echo "📦 Backing up databases..."
mkdir -p "$BACKUP_PATH/databases"
cp -r /opt/d3kos/data/*.db "$BACKUP_PATH/databases/" 2>/dev/null || true
cp -r /opt/d3kos/data/*/*.db "$BACKUP_PATH/databases/" 2>/dev/null || true

# Backup configuration
echo "📦 Backing up configuration..."
mkdir -p "$BACKUP_PATH/config"
cp -r /opt/d3kos/config/* "$BACKUP_PATH/config/"

# Backup manuals
echo "📦 Backing up manuals..."
mkdir -p "$BACKUP_PATH/manuals"
cp -r /opt/d3kos/data/manuals/* "$BACKUP_PATH/manuals/" 2>/dev/null || true

# Backup boatlog
echo "📦 Backing up boatlog..."
cp -r /opt/d3kos/data/boatlog "$BACKUP_PATH/"

# Backup onboarding answers
echo "📦 Backing up onboarding data..."
mkdir -p "$BACKUP_PATH/onboarding"
cp /opt/d3kos/state/onboarding-* "$BACKUP_PATH/onboarding/" 2>/dev/null || true

# Create manifest
echo "📝 Creating backup manifest..."
cat > "$BACKUP_PATH/manifest.json" << EOF
{
  "backup_name": "$BACKUP_NAME",
  "timestamp": "$(date -Iseconds)",
  "d3kos_version": "$(cat /opt/d3kos/config/version.txt | head -1 | cut -d' ' -f3)",
  "installation_id": "$(cat /opt/d3kos/config/license.json | jq -r '.installation_id')",
  "tier": $(cat /opt/d3kos/config/license.json | jq '.tier'),
  "backup_size": "$(du -sh $BACKUP_PATH | cut -f1)",
  "items": {
    "databases": $(ls -1 $BACKUP_PATH/databases/*.db 2>/dev/null | wc -l),
    "config_files": $(ls -1 $BACKUP_PATH/config/* 2>/dev/null | wc -l),
    "manuals": $(ls -1 $BACKUP_PATH/manuals/* 2>/dev/null | wc -l)
  }
}
EOF

# Create README
cat > "$BACKUP_PATH/README.txt" << EOF
d3kOS Backup
Created: $(date)
Version: $(cat /opt/d3kos/config/version.txt | head -1)

This backup contains:
- System databases (boatlog, health, exports, etc.)
- Configuration files (license, timezone, settings)
- Uploaded manuals
- Onboarding wizard answers

To restore:
1. Copy backup folder to USB drive
2. Run: /opt/d3kos/scripts/restore-backup.sh /path/to/backup
3. Reboot system

IMPORTANT: This backup does NOT include:
- Camera recordings (too large)
- Operating system files
- Installed packages
EOF

# Compress backup
echo "🗜️ Compressing backup..."
cd "$BACKUP_DIR"
tar -czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME"
rm -rf "$BACKUP_NAME"

# Generate checksum
sha256sum "${BACKUP_NAME}.tar.gz" > "${BACKUP_NAME}.tar.gz.sha256"

# Cleanup old backups (keep last 10)
echo "🧹 Cleaning old backups..."
ls -t "$BACKUP_DIR"/d3kos_backup_*.tar.gz | tail -n +11 | xargs rm -f 2>/dev/null || true
ls -t "$BACKUP_DIR"/d3kos_backup_*.tar.gz.sha256 | tail -n +11 | xargs rm -f 2>/dev/null || true

BACKUP_SIZE=$(du -sh "${BACKUP_NAME}.tar.gz" | cut -f1)
echo "✅ Backup complete: ${BACKUP_NAME}.tar.gz ($BACKUP_SIZE)"
```

```bash
sudo chmod +x /opt/d3kos/scripts/create-backup.sh

# Test backup
sudo /opt/d3kos/scripts/create-backup.sh

# Verify
ls -lh /media/d3kos/6233-3338/backups/
```

#### Step C3.2: Create Restore Script

```bash
sudo nano /opt/d3kos/scripts/restore-backup.sh
```

**Restore Script**:
```bash
#!/bin/bash
# d3kOS Restore Script
# Restores system from backup

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 /path/to/backup.tar.gz"
    exit 1
fi

BACKUP_FILE="$1"
TEMP_DIR="/tmp/d3kos_restore"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Verify checksum
if [ -f "${BACKUP_FILE}.sha256" ]; then
    echo "🔍 Verifying backup checksum..."
    sha256sum -c "${BACKUP_FILE}.sha256" || {
        echo "❌ Checksum verification failed!"
        exit 1
    }
fi

# Extract backup
echo "📦 Extracting backup..."
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"
tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR"

BACKUP_DIR=$(ls -d $TEMP_DIR/d3kos_backup_* | head -1)

if [ ! -d "$BACKUP_DIR" ]; then
    echo "❌ Invalid backup structure"
    exit 1
fi

# Show manifest
echo "📄 Backup manifest:"
cat "$BACKUP_DIR/manifest.json" | jq .

# Confirm restore
read -p "⚠️  This will overwrite current data. Continue? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "❌ Restore cancelled"
    exit 1
fi

# Stop services
echo "🛑 Stopping services..."
sudo systemctl stop d3kos-export-manager
sudo systemctl stop d3kos-health
sudo systemctl stop signalk

# Restore databases
echo "📥 Restoring databases..."
cp -r "$BACKUP_DIR/databases"/* /opt/d3kos/data/ 2>/dev/null || true

# Restore configuration (but preserve installation_id)
echo "📥 Restoring configuration..."
CURRENT_ID=$(cat /opt/d3kos/config/license.json | jq -r '.installation_id')
cp -r "$BACKUP_DIR/config"/* /opt/d3kos/config/
# Restore installation_id
jq ".installation_id = \"$CURRENT_ID\"" /opt/d3kos/config/license.json > /tmp/license.tmp
mv /tmp/license.tmp /opt/d3kos/config/license.json

# Restore manuals
echo "📥 Restoring manuals..."
mkdir -p /opt/d3kos/data/manuals
cp -r "$BACKUP_DIR/manuals"/* /opt/d3kos/data/manuals/ 2>/dev/null || true

# Restore boatlog
echo "📥 Restoring boatlog..."
cp -r "$BACKUP_DIR/boatlog" /opt/d3kos/data/

# Restore onboarding
echo "📥 Restoring onboarding data..."
cp "$BACKUP_DIR/onboarding"/* /opt/d3kos/state/ 2>/dev/null || true

# Fix permissions
echo "🔧 Fixing permissions..."
sudo chown -R d3kos:d3kos /opt/d3kos/data
sudo chown -R d3kos:d3kos /opt/d3kos/config
sudo chown -R d3kos:d3kos /opt/d3kos/state

# Restart services
echo "▶️  Starting services..."
sudo systemctl start signalk
sudo systemctl start d3kos-health
sudo systemctl start d3kos-export-manager

# Cleanup
rm -rf "$TEMP_DIR"

echo "✅ Restore complete! Reboot recommended."
```

```bash
sudo chmod +x /opt/d3kos/scripts/restore-backup.sh
```

#### Step C3.3: Add Backup UI to Settings

```bash
sudo nano /var/www/html/settings.html
```

**Add Backup Section**:
```html
<!-- Add to settings page -->
<div class="section">
    <h2>💾 Backup & Restore</h2>

    <div class="setting-row">
        <label>Last Backup:</label>
        <span id="last-backup">Loading...</span>
    </div>

    <div class="setting-row">
        <button onclick="createBackup()" style="width: 300px; height: 80px; font-size: 24px;">
            🔄 Create Backup Now
        </button>
    </div>

    <div class="setting-row">
        <label>Available Backups:</label>
        <select id="backup-list" style="width: 400px; font-size: 22px;">
            <option>Loading...</option>
        </select>
        <button onclick="restoreBackup()">📥 Restore</button>
    </div>

    <div class="setting-row">
        <label>Auto-Backup:</label>
        <select id="auto-backup">
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="off">Off</option>
        </select>
        <button onclick="setAutoBackup()">Save</button>
    </div>
</div>

<script>
async function createBackup() {
    if (!confirm('Create backup now? This may take 1-2 minutes.')) return;

    document.getElementById('last-backup').textContent = 'Creating backup...';

    try {
        const response = await fetch('/api/backup/create', { method: 'POST' });
        const data = await response.json();

        if (data.success) {
            alert('Backup created successfully: ' + data.backup_name);
            loadBackupList();
        } else {
            alert('Backup failed: ' + data.error);
        }
    } catch (err) {
        alert('Error creating backup: ' + err.message);
    }
}

async function loadBackupList() {
    try {
        const response = await fetch('/api/backup/list');
        const data = await response.json();

        if (data.success) {
            const select = document.getElementById('backup-list');
            select.innerHTML = data.backups.map(b =>
                `<option value="${b.file}">${b.name} (${b.size})</option>`
            ).join('');

            if (data.backups.length > 0) {
                document.getElementById('last-backup').textContent =
                    data.backups[0].timestamp + ' (' + data.backups[0].size + ')';
            }
        }
    } catch (err) {
        console.error('Error loading backups:', err);
    }
}

async function restoreBackup() {
    const select = document.getElementById('backup-list');
    const backupFile = select.value;

    if (!backupFile) {
        alert('Please select a backup to restore');
        return;
    }

    if (!confirm('⚠️ WARNING: This will overwrite current data. Continue?')) {
        return;
    }

    try {
        const response = await fetch('/api/backup/restore', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ backup_file: backupFile })
        });

        const data = await response.json();

        if (data.success) {
            alert('Restore complete! System will reboot in 5 seconds.');
            setTimeout(() => location.reload(), 5000);
        } else {
            alert('Restore failed: ' + data.error);
        }
    } catch (err) {
        alert('Error restoring backup: ' + err.message);
    }
}

loadBackupList();
</script>
```

#### Step C3.4: Create Backup API

```bash
sudo nano /opt/d3kos/services/system/backup-api.py
```

**Backup API**:
```python
#!/usr/bin/env python3
"""
d3kOS Backup API
Port: 8100
Endpoints: /api/backup/create, /api/backup/list, /api/backup/restore
"""

import os
import json
import subprocess
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BACKUP_DIR = '/media/d3kos/6233-3338/backups'
CREATE_SCRIPT = '/opt/d3kos/scripts/create-backup.sh'
RESTORE_SCRIPT = '/opt/d3kos/scripts/restore-backup.sh'

@app.route('/api/backup/create', methods=['POST'])
def create_backup():
    """Create new backup"""
    try:
        result = subprocess.run([CREATE_SCRIPT],
                                capture_output=True, text=True, timeout=300)

        if result.returncode == 0:
            # Parse backup name from output
            for line in result.stdout.split('\n'):
                if 'Backup complete:' in line:
                    backup_name = line.split(':')[1].strip().split()[0]
                    return jsonify({
                        'success': True,
                        'backup_name': backup_name
                    })

            return jsonify({'success': True, 'message': 'Backup created'})
        else:
            return jsonify({
                'success': False,
                'error': result.stderr
            }), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/backup/list', methods=['GET'])
def list_backups():
    """List available backups"""
    try:
        if not os.path.exists(BACKUP_DIR):
            return jsonify({'success': True, 'backups': []})

        backups = []
        for file in os.listdir(BACKUP_DIR):
            if file.endswith('.tar.gz') and file.startswith('d3kos_backup_'):
                file_path = os.path.join(BACKUP_DIR, file)
                stat = os.stat(file_path)

                # Get size in MB
                size_mb = stat.st_size / (1024 * 1024)

                # Parse timestamp from filename
                timestamp = file.replace('d3kos_backup_', '').replace('.tar.gz', '')
                timestamp_formatted = f"{timestamp[:8]} {timestamp[9:11]}:{timestamp[11:13]}"

                backups.append({
                    'file': file_path,
                    'name': file,
                    'size': f'{size_mb:.1f} MB',
                    'timestamp': timestamp_formatted
                })

        # Sort by name (newest first)
        backups.sort(key=lambda x: x['name'], reverse=True)

        return jsonify({'success': True, 'backups': backups})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/backup/restore', methods=['POST'])
def restore_backup():
    """Restore from backup"""
    try:
        data = request.get_json()
        backup_file = data.get('backup_file', '')

        if not backup_file or not os.path.exists(backup_file):
            return jsonify({
                'success': False,
                'error': 'Invalid backup file'
            }), 400

        # Run restore script in background
        subprocess.Popen([RESTORE_SCRIPT, backup_file])

        return jsonify({
            'success': True,
            'message': 'Restore started'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8100, debug=False)
```

```bash
# Create systemd service
sudo nano /etc/systemd/system/d3kos-backup-api.service
```

**Service**:
```ini
[Unit]
Description=d3kOS Backup API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/d3kos/services/system
ExecStart=/usr/bin/python3 /opt/d3kos/services/system/backup-api.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable d3kos-backup-api.service
sudo systemctl start d3kos-backup-api.service

# Add nginx proxy
sudo nano /etc/nginx/sites-enabled/default
```

**Nginx**:
```nginx
location /api/backup/ {
    proxy_pass http://localhost:8100/api/backup/;
    proxy_read_timeout 600s;
}
```

```bash
sudo systemctl reload nginx
```

**Verification**:
- [ ] Backup script creates .tar.gz file
- [ ] Manifest.json included
- [ ] Restore script works
- [ ] Backup API functional
- [ ] Settings UI shows backups
- [ ] Old backups auto-deleted (keep 10)

---

### Task C4: Documentation & Commit (1 hour)

```bash
cd /home/boatiq/Helm-OS/doc
nano SESSION_C_DATA_EXPORT_COMPLETE.md
```

**Summary**:
```markdown
# Session C: Data Export & Backup - COMPLETE

**Date**: [Fill in]
**Duration**: [Fill in]
**Status**: ✅ COMPLETE

## Summary

Completed data management systems:
- Export queue with retry logic
- Boatlog CSV export fix
- Full backup & restore system
- Auto-cleanup of old backups

## Changes Made

### Export Queue System
- Background worker thread
- 3 retry attempts (5s, 5min, 15min)
- Queue persistence to disk
- Export history tracking
- Failed export handling

### Boatlog Export
- CSV export endpoint
- Download as file
- Proper escaping of special characters

### Backup & Restore
- create-backup.sh script
- restore-backup.sh script
- Backup API (port 8100)
- Settings UI integration
- Auto-cleanup (keep last 10)

## Files Created/Modified

**On Raspberry Pi:**
- `/opt/d3kos/services/export/export-manager.py` (modified)
- `/opt/d3kos/scripts/create-backup.sh` (new)
- `/opt/d3kos/scripts/restore-backup.sh` (new)
- `/opt/d3kos/services/system/backup-api.py` (new)
- `/etc/systemd/system/d3kos-backup-api.service` (new)
- `/var/www/html/settings.html` (modified)
- `/var/www/html/boatlog.html` (modified)

## Testing Results

### Export Queue
- [X] Exports queued successfully
- [X] Retry logic works (3 attempts)
- [X] Failed exports tracked
- [X] History saved

### Boatlog Export
- [X] CSV downloads correctly
- [X] All entries included
- [X] Opens in Excel/Calc

### Backup & Restore
- [X] Backup creates .tar.gz
- [X] Restore works correctly
- [X] Installation ID preserved
- [X] Old backups cleaned up

## Next Steps

Session C complete. Ready for final integration.
```

```bash
# Update spec
nano /home/boatiq/Helm-OS/MASTER_SYSTEM_SPEC.md
```

**Spec Updates**:
```markdown
# Add to version history:
| 3.8 | 2026-02-20 | d3kOS Team | Implemented Data Export Queue System (Section 8.3.4), fixed boatlog export, implemented Backup & Restore (Section 8.2) |

# Update Section 8.2:
**Implementation Status**: ✅ COMPLETE (February 20, 2026)
- Scripts: create-backup.sh, restore-backup.sh
- API: Port 8100
- UI: Settings page

# Update Section 8.3.4:
**Implementation Status**: ✅ COMPLETE (February 20, 2026)
- Queue: /opt/d3kos/data/exports/export_queue.json
- Retry logic: 3 attempts (5s, 5min, 15min)
- History: Last 100 exports
```

```bash
# Commit
cd /home/boatiq/Helm-OS
git add -A
git commit -m "Session C: Data Export Queue & Backup System

- Implemented export queue with retry logic (3 attempts)
- Fixed boatlog CSV export button
- Created backup & restore scripts
- Added backup API (port 8100)
- Integrated backup UI in settings
- Auto-cleanup old backups (keep 10)
- All changes verified and tested

Closes: Data management for v0.9.1.2
See: doc/SESSION_C_DATA_EXPORT_COMPLETE.md"

git push origin main
```

---

## SESSION D: DEPLOYMENT & IMAGE BUILD

**Owner**: Parallel session (after Session A)
**Domain**: Deployment, Testing, Documentation
**Duration**: 6-8 hours
**Dependencies**: Session A complete (requires version set)

### Objectives
1. ✅ Document image build process
2. ✅ Create image build scripts
3. ✅ Complete testing matrix
4. ✅ Update all documentation
5. ✅ Final system verification
6. ✅ Commit all changes
7. ✅ Push to GitHub

---

### Task D1: Image Build Process (2-3 hours)

#### Step D1.1: Create Image Build Script

```bash
sudo nano /opt/d3kos/scripts/create-image.sh
```

**Image Script**:
```bash
#!/bin/bash
# d3kOS Image Creation Script
# Creates distributable .img.gz file from current system

set -e

VERSION="0.9.1.2"
BUILD_DATE=$(date +%Y%m%d)
IMAGE_NAME="d3kos-v${VERSION}-${BUILD_DATE}"
OUTPUT_DIR="/media/d3kos/6233-3338/images"

echo "🔧 Creating d3kOS image: $IMAGE_NAME"

# Verify running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Must run as root"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Pre-flight checks
echo "✅ Pre-flight checks..."

# Check services
CRITICAL_SERVICES=(
    "d3kos-license-api"
    "d3kos-tier-api"
    "d3kos-health"
    "signalk"
    "nodered"
    "nginx"
)

for service in "${CRITICAL_SERVICES[@]}"; do
    if ! systemctl is-active --quiet "$service"; then
        echo "⚠️  Warning: $service is not running"
    fi
done

# Check disk space
DISK_PERCENT=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_PERCENT" -gt 90 ]; then
    echo "⚠️  Warning: Disk usage is ${DISK_PERCENT}%"
fi

# Clean temporary files
echo "🧹 Cleaning temporary files..."
rm -rf /tmp/*
rm -rf /var/tmp/*
rm -rf /home/d3kos/.cache/*
journalctl --vacuum-time=7d
apt-get clean

# Stop services (to ensure clean state)
echo "🛑 Stopping services..."
systemctl stop d3kos-*
systemctl stop signalk
systemctl stop nodered

# Reset logs
echo "📝 Resetting logs..."
truncate -s 0 /var/log/syslog
truncate -s 0 /var/log/daemon.log
journalctl --rotate
journalctl --vacuum-time=1s

# Remove sensitive data
echo "🔒 Removing sensitive data..."
rm -f /home/d3kos/.bash_history
rm -f /root/.bash_history
rm -f /home/d3kos/.ssh/known_hosts

# Set version
echo "📌 Setting version to $VERSION..."
cat > /opt/d3kos/config/version.txt << EOF
d3kOS Version $VERSION
Release Date: $(date +"%B %d, %Y")
Status: Tier 0 Installation Complete
Build: opensource-stable
EOF

# Create build manifest
echo "📄 Creating build manifest..."
cat > /opt/d3kos/config/build-manifest.json << EOF
{
  "version": "$VERSION",
  "build_date": "$(date -Iseconds)",
  "build_host": "$(hostname)",
  "kernel": "$(uname -r)",
  "debian_version": "$(cat /etc/debian_version)",
  "services": [
    $(systemctl list-unit-files 'd3kos-*' --no-pager --no-legend | awk '{print "\""$1"\""}' | paste -sd,)
  ],
  "packages": {
    "signalk": "$(signalk-server --version 2>/dev/null || echo 'unknown')",
    "node": "$(node --version)",
    "python3": "$(python3 --version | awk '{print $2}')"
  }
}
EOF

# Restart services
echo "▶️  Starting services..."
systemctl start signalk
systemctl start nodered
systemctl start d3kos-license-api
systemctl start d3kos-tier-api
systemctl start d3kos-health

# Create image
echo "💾 Creating disk image..."
echo "⚠️  This will take 30-60 minutes..."

# Use pishrink to minimize image size
if command -v pishrink.sh &> /dev/null; then
    # Create raw image first
    dd if=/dev/mmcblk0 of="${OUTPUT_DIR}/${IMAGE_NAME}.img" bs=4M status=progress

    # Shrink image
    pishrink.sh "${OUTPUT_DIR}/${IMAGE_NAME}.img"
else
    # No pishrink, create full image
    dd if=/dev/mmcblk0 of="${OUTPUT_DIR}/${IMAGE_NAME}.img" bs=4M status=progress
fi

# Compress image
echo "🗜️  Compressing image..."
gzip -9 "${OUTPUT_DIR}/${IMAGE_NAME}.img"

# Generate checksum
echo "🔐 Generating checksum..."
sha256sum "${OUTPUT_DIR}/${IMAGE_NAME}.img.gz" > "${OUTPUT_DIR}/${IMAGE_NAME}.img.gz.sha256"

# Create README
echo "📝 Creating README..."
cat > "${OUTPUT_DIR}/${IMAGE_NAME}_README.txt" << EOF
d3kOS v$VERSION - Tier 0 Installation

Build Date: $(date)
Image File: ${IMAGE_NAME}.img.gz
Checksum: ${IMAGE_NAME}.img.gz.sha256

INSTALLATION INSTRUCTIONS:

1. Download image and checksum file
2. Verify checksum:
   sha256sum -c ${IMAGE_NAME}.img.gz.sha256

3. Flash to SD card (64GB minimum):
   - Windows: Use Raspberry Pi Imager or balenaEtcher
   - Linux/Mac: Use Raspberry Pi Imager or dd command

4. Insert SD card into Raspberry Pi 4
5. Connect power, touchscreen, and NMEA2000 (PiCAN-M)
6. System will boot and auto-expand filesystem (2-3 minutes)
7. Connect to WiFi: SSID "d3kOS", password "d3kos-2026"
8. Open browser: http://d3kos.local or http://10.42.0.1
9. Complete Initial Setup wizard (10-15 minutes)

FIRST LOGIN:
Username: d3kos
Password: d3kos2026
⚠️  CHANGE PASSWORD IMMEDIATELY: run 'passwd' command

SYSTEM SPECS:
- Version: $VERSION
- Tier: 0 (Opensource - free forever)
- Debian: $(cat /etc/debian_version)
- Kernel: $(uname -r)

FEATURES (Tier 0):
✓ Engine health monitoring
✓ Dashboard with gauges
✓ Boatlog (30-day retention)
✓ Initial Setup wizard (10 resets max)
✓ Weather radar
✓ Navigation page
✓ Manual management
✓ Pi health monitoring

UPGRADES:
Tier 1 (FREE): Mobile app integration + config restore
Tier 2 (\$9.99/month): Voice assistant + camera + unlimited resets
Tier 3 (\$99.99/year): All features + cloud sync + multi-boat

SUPPORT:
GitHub: https://github.com/SkipperDon/d3kos
Documentation: See /doc folder
Issues: https://github.com/SkipperDon/d3kos/issues
EOF

# Calculate final size
IMAGE_SIZE=$(du -sh "${OUTPUT_DIR}/${IMAGE_NAME}.img.gz" | cut -f1)

echo ""
echo "✅ Image build complete!"
echo "📦 Image: ${OUTPUT_DIR}/${IMAGE_NAME}.img.gz"
echo "📏 Size: $IMAGE_SIZE"
echo "🔐 Checksum: ${OUTPUT_DIR}/${IMAGE_NAME}.img.gz.sha256"
echo "📄 README: ${OUTPUT_DIR}/${IMAGE_NAME}_README.txt"
```

```bash
sudo chmod +x /opt/d3kos/scripts/create-image.sh
```

#### Step D1.2: Install PiShrink (Optional)

```bash
# Download pishrink
wget https://raw.githubusercontent.com/Drewsif/PiShrink/master/pishrink.sh
sudo chmod +x pishrink.sh
sudo mv pishrink.sh /usr/local/bin/

# Test pishrink
pishrink.sh --help
```

#### Step D1.3: Document Build Process

```bash
cd /home/boatiq/Helm-OS/doc
nano IMAGE_BUILD_GUIDE.md
```

**Build Guide** (abbreviated):
```markdown
# d3kOS Image Build Guide

## Prerequisites

1. Raspberry Pi 4 with fully configured d3kOS system
2. 64GB+ SD card (source)
3. 128GB+ USB drive (for image storage)
4. pishrink.sh installed (optional but recommended)
5. 60+ minutes of time

## Build Steps

### Step 1: Verify System

```bash
# Check all services running
systemctl status d3kos-*
systemctl status signalk
systemctl status nodered

# Check disk usage (<80%)
df -h /

# Check version
cat /opt/d3kos/config/version.txt
```

### Step 2: Clean System

```bash
# Run cleanup
sudo apt-get clean
sudo journalctl --vacuum-time=7d
sudo rm -rf /tmp/*
sudo rm -rf /var/tmp/*
```

### Step 3: Create Image

```bash
# Run build script
sudo /opt/d3kos/scripts/create-image.sh

# Wait 30-60 minutes
```

### Step 4: Verify Image

```bash
# Check files created
ls -lh /media/d3kos/6233-3338/images/

# Verify checksum
cd /media/d3kos/6233-3338/images/
sha256sum -c d3kos-v0.9.1.2-*.img.gz.sha256
```

### Step 5: Test Image

1. Flash to new SD card
2. Boot Raspberry Pi
3. Complete Initial Setup wizard
4. Verify all features work

## Distribution

### GitHub Release

1. Create new release: v0.9.1.2
2. Upload files:
   - d3kos-v0.9.1.2-YYYYMMDD.img.gz
   - d3kos-v0.9.1.2-YYYYMMDD.img.gz.sha256
   - d3kOS-v0.9.1.2-YYYYMMDD_README.txt
3. Write release notes (changelog)

### Download Instructions for Users

```
1. Go to: https://github.com/SkipperDon/d3kos/releases
2. Download latest release
3. Verify checksum
4. Flash with Raspberry Pi Imager
5. Boot and enjoy!
```

## Troubleshooting

**Image too large (>8GB compressed)**:
- Clean more aggressively
- Remove camera recordings
- Remove old backups

**Build fails**:
- Check disk space
- Verify pishrink installed
- Run as root (sudo)

**Image doesn't boot**:
- Verify checksum
- Try different SD card
- Check Pi power supply (3A minimum)
```

**Verification**:
- [ ] Build script runs without errors
- [ ] Image created and compressed
- [ ] Checksum generated
- [ ] README included
- [ ] Image size reasonable (<6GB compressed)

---

### Task D2: Testing Matrix Completion (2-3 hours)

#### Step D2.1: Create Test Suite

```bash
cd /home/boatiq/Helm-OS/doc
nano TESTING_MATRIX_v0.9.1.2.md
```

**Testing Matrix**:
```markdown
# d3kOS v0.9.1.2 Testing Matrix

**Date**: [Fill in]
**Tester**: [Fill in]
**Status**: ⏳ IN PROGRESS

## Hardware Tests

| Test | Expected | Result | Notes |
|------|----------|--------|-------|
| Boot time | <60 seconds | [ ] | From power-on to main menu |
| Touchscreen accuracy | <5px error | [ ] | Test all corners + center |
| On-screen keyboard | No overlap | [ ] | Test on all pages |
| PiCAN-M NMEA2000 | All PGNs received | [ ] | With CX5106 connected |
| USB GPS | Position accurate | [ ] | <10m error outdoors |
| Camera (if present) | Stream <500ms latency | [ ] | Reolink RLC-810A |
| USB Audio | Wake word >95% | [ ] | Anker S330 |

## Software Tests

### Core Functionality

| Test | Expected | Result | Notes |
|------|----------|--------|-------|
| Main menu loads | <5 seconds | [ ] | After boot |
| Initial Setup wizard | Completes successfully | [ ] | All 20 steps |
| QR code generation | Scannable on mobile | [ ] | Step 19 |
| DIP switches | Correct configuration | [ ] | Step 18 |
| Dashboard | All gauges at 1Hz | [ ] | Real-time updates |
| Navigation page | GPS data displayed | [ ] | Position, speed, heading |
| Weather page | Radar loads | [ ] | Windy.com integration |
| Boatlog | Entries save | [ ] | Voice, text, auto |
| Settings | All pages load | [ ] | No errors |

### Tier System

| Test | Expected | Result | Notes |
|------|----------|--------|-------|
| Version display | Shows 0.9.1.2 | [ ] | Settings page |
| Tier detection | Tier 3 active | [ ] | For testing |
| License API | Returns correct tier | [ ] | GET /license/info |
| Feature restrictions | Tier 3 all enabled | [ ] | Voice, camera, export |
| Reset counter | Tracks resets | [ ] | Max 9999 for Tier 3 |

### AI Assistant

| Test | Expected | Result | Notes |
|------|----------|--------|-------|
| Text interface | Responds <2s | [ ] | Cached queries |
| Voice wake word | Detection >95% | [ ] | Say "HELM" 20 times |
| Simple queries | Instant response | [ ] | RPM, oil, temp, etc. |
| Complex queries | OpenRouter <10s | [ ] | "Why is engine overheating?" |
| Cache performance | 100× speedup | [ ] | Second query within 3s TTL |

### Data Management

| Test | Expected | Result | Notes |
|------|----------|--------|-------|
| Export queue | Queues successfully | [ ] | POST /export/generate |
| Export retry | 3 attempts (5s/5m/15m) | [ ] | Check logs |
| Boatlog CSV export | Downloads correctly | [ ] | Opens in Excel |
| Backup creation | Creates .tar.gz | [ ] | <2 minutes |
| Backup restore | Restores correctly | [ ] | Data preserved |
| Auto-cleanup | Keeps last 10 backups | [ ] | Old ones deleted |

### Self-Healing (Tier 3)

| Test | Expected | Result | Notes |
|------|----------|--------|-------|
| Issue detection | Detects anomalies | [ ] | Simulate low oil pressure |
| AI diagnosis | Provides analysis | [ ] | Root cause + recommendation |
| Auto-remediation | Fixes issues | [ ] | Restart service, cleanup disk |
| Notification | User alerted | [ ] | Check settings-healing.html |
| History tracking | Logs resolved issues | [ ] | Last 7 days |

### Timezone Auto-Detection

| Test | Expected | Result | Notes |
|------|----------|--------|-------|
| GPS detection | Detects from coordinates | [ ] | With GPS fix |
| Internet detection | Detects from IP | [ ] | Without GPS |
| UTC fallback | Defaults to UTC | [ ] | No GPS, no internet |
| Manual override | Sets timezone | [ ] | Settings page |
| System time | Correct after reboot | [ ] | timedatectl |

### Services

| Service | Status | Auto-Start | Notes |
|---------|--------|------------|-------|
| d3kos-license-api | [ ] Active | [ ] Yes | Port 8091 |
| d3kos-tier-api | [ ] Active | [ ] Yes | Port 8093 |
| d3kos-health | [ ] Active | [ ] Yes | System health monitor |
| d3kos-export-manager | [ ] Active | [ ] Yes | Port 8094 |
| d3kos-timezone-api | [ ] Active | [ ] Yes | Port 8098 |
| d3kos-issue-detector | [ ] Active | [ ] Yes | Self-healing detection |
| d3kos-remediation | [ ] Active | [ ] Yes | Self-healing remediation |
| d3kos-healing-api | [ ] Active | [ ] Yes | Port 8099 |
| d3kos-backup-api | [ ] Active | [ ] Yes | Port 8100 |
| signalk | [ ] Active | [ ] Yes | Port 3000 |
| nodered | [ ] Active | [ ] Yes | Port 1880 |
| nginx | [ ] Active | [ ] Yes | Port 80 |

## Performance Tests

| Metric | Target | Actual | Pass/Fail |
|--------|--------|--------|-----------|
| Boot time | <60s | ___s | [ ] |
| Voice response | <2s | ___s | [ ] |
| Dashboard update | 1Hz | ___Hz | [ ] |
| CPU idle | <10% | ___%| [ ] |
| Memory usage | <4GB | ___GB | [ ] |
| Disk usage | <80% | ___% | [ ] |

## Acceptance Criteria

### Phase 1: Core ✅
- [ ] Main menu loads <5s
- [ ] Initial Setup completes
- [ ] Dashboard 1Hz updates
- [ ] No AODA violations

### Phase 2: Intelligence ✅
- [ ] Voice wake word >95%
- [ ] AI response <2s (cached)
- [ ] Self-healing works

### Phase 3: Integration ✅
- [ ] Camera records/plays
- [ ] Boatlog exports
- [ ] Backup/restore works
- [ ] Tier system enforced

### Phase 4: Polish ✅
- [ ] All documentation complete
- [ ] Image builds successfully
- [ ] Zero critical bugs

## Final Checklist

- [ ] All tests passing
- [ ] Documentation updated
- [ ] Image created
- [ ] README included
- [ ] Checksum verified
- [ ] Release notes written
- [ ] GitHub release created

## Notes

[Add any issues found, workarounds, or observations]
```

#### Step D2.2: Run Tests

```bash
# Run through entire testing matrix
# Mark each test as pass/fail
# Document any issues found
```

**Verification**:
- [ ] All core tests passing
- [ ] Performance within targets
- [ ] No critical bugs
- [ ] All services auto-start
- [ ] Documentation accurate

---

### Task D3: Final Documentation Updates (1-2 hours)

#### Step D3.1: Update README.md

```bash
cd /home/boatiq/Helm-OS
nano README.md
```

**Update README**:
```markdown
# d3kOS - Marine Helm Control System

**Version**: 0.9.1.2
**Status**: Tier 0 Installation Complete
**Build**: Opensource-Stable
**Release Date**: February 20, 2026

## Overview

d3kOS is a comprehensive marine electronics system built on Raspberry Pi 4, designed for touchscreen and voice control in marine environments.

## Features (Tier 0 - FREE)

✅ **Engine Health Monitoring**
- Real-time NMEA2000 data via CX5106 gateway
- Dashboard with gauges (RPM, oil, temp, fuel, battery)
- Anomaly detection (statistical process control)

✅ **Navigation**
- GPS position display
- Speed and heading
- Chartplotter integration detection

✅ **Weather Radar**
- Windy.com integration
- Touch-friendly map controls
- Marine conditions panel

✅ **Boatlog**
- Text, voice, and auto entries
- 30-day retention
- CSV export

✅ **Initial Setup Wizard**
- 20-step configuration
- CX5106 DIP switch generation
- QR code for mobile pairing
- 10 resets maximum (Tier 0)

✅ **Self-Healing System** (Tier 3)
- AI-powered issue detection
- Automatic remediation
- Root cause analysis

✅ **Data Management**
- Backup & restore system
- Export queue with retry
- Auto-cleanup

✅ **System Health**
- Raspberry Pi monitoring (CPU, memory, disk)
- Service status tracking
- Timezone auto-detection

## Installation

### Pre-Built Image (Recommended)

1. Download latest release: https://github.com/SkipperDon/d3kos/releases
2. Verify checksum: `sha256sum -c d3kos-v0.9.1.2-*.sha256`
3. Flash to 64GB+ SD card using Raspberry Pi Imager
4. Insert SD card into Raspberry Pi 4
5. Connect power, touchscreen, PiCAN-M
6. Boot (2-3 min for filesystem expansion)
7. Connect to WiFi "d3kOS" (password: d3kos-2026)
8. Open browser: http://d3kos.local
9. Complete Initial Setup wizard

### Hardware Requirements

- Raspberry Pi 4 Model B (4GB minimum, 8GB recommended)
- 64GB SD card (Class 10 A2)
- PiCAN-M HAT with micro-fit connector
- 10.1" touchscreen (1920×1200, capacitive)
- USB GPS receiver
- (Optional) USB AIS receiver
- (Optional) Anker PowerConf S330 speakerphone (for voice)
- (Optional) Reolink RLC-810A camera

## Default Credentials

**⚠️ CHANGE IMMEDIATELY AFTER FIRST LOGIN**

- **System User**: d3kos / d3kos2026
- **WiFi AP**: d3kOS / d3kos-2026
- **Web Interface**: http://d3kos.local (no auth)

## Tier Upgrades

| Tier | Price | Features |
|------|-------|----------|
| **0** | FREE | Dashboard, boatlog, health monitoring, 10 resets |
| **1** | FREE | Mobile app + config restore on updates |
| **2** | $9.99/mo | Voice assistant, camera, unlimited resets |
| **3** | $99.99/yr | All features + cloud sync + multi-boat |

## Documentation

- [Master System Spec](MASTER_SYSTEM_SPEC.md)
- [Installation Guide](doc/INSTALLATION.md)
- [Image Build Guide](doc/IMAGE_BUILD_GUIDE.md)
- [Testing Matrix](doc/TESTING_MATRIX_v0.9.1.2.md)
- [AI Assistant Guide](doc/AI_ASSISTANT_USER_GUIDE.md)
- [Marine Vision API](doc/MARINE_VISION_API.md)

## Development

- **Repository**: https://github.com/SkipperDon/d3kos
- **Issues**: https://github.com/SkipperDon/d3kos/issues
- **License**: MIT (see LICENSE file)

## Release Notes (v0.9.1.2)

### New Features
- ✅ Timezone auto-detection (GPS → Internet → UTC)
- ✅ AI-powered self-healing system
- ✅ Data export queue with retry logic
- ✅ Backup & restore system
- ✅ Tier 3 testing mode

### Improvements
- ✅ Fixed voice assistant wake word detection
- ✅ Fixed boatlog CSV export
- ✅ Improved AI response caching (100× speedup)
- ✅ Auto-cleanup of old backups

### Bug Fixes
- ✅ Export manager JSON parsing error
- ✅ QR code not scannable on mobile
- ✅ PipeWire mic signal loss

### Known Issues
- Fish detection limited to person detection (custom model pending)
- Charts page requires o-charts addon (future)

## Support

For questions, issues, or feature requests:
- GitHub Issues: https://github.com/SkipperDon/d3kos/issues
- Documentation: See `/doc` folder
- Community: (forum link TBD)

## License

MIT License - see LICENSE file for details

---

**Built with ⚓ for the marine community**
**Skipper Don & d3kOS Team**
```

#### Step D3.2: Create CHANGELOG.md

```bash
nano CHANGELOG.md
```

**Changelog**:
```markdown
# Changelog

All notable changes to d3kOS will be documented in this file.

## [0.9.1.2] - 2026-02-20

### Added
- Timezone auto-detection system (GPS → Internet → UTC fallback)
- AI-powered self-healing system (Tier 3)
  - Issue detection (engine + Pi health)
  - Auto-remediation with safe actions
  - Root cause analysis via AI
  - History tracking and statistics
- Data export queue system with retry logic (3 attempts)
- Full backup & restore system
- Backup API (port 8100) and Settings UI integration
- Session-based parallel development workflow
- Comprehensive testing matrix

### Changed
- System version updated to 0.9.1.2
- Tier set to 3 for testing purposes
- Improved AI response caching (0.17s vs 18s for cached queries)
- Export manager now uses background queue worker
- Settings page shows version and tier information

### Fixed
- Voice assistant wake word detection (PipeWire interference)
- Boatlog CSV export button crash
- Export manager JSON parsing error
- QR code not scannable on mobile phones
- Installation ID now persistent (file-based, not localStorage)

### Documentation
- Created IMAGE_BUILD_GUIDE.md
- Created TESTING_MATRIX_v0.9.1.2.md
- Updated MASTER_SYSTEM_SPEC.md to v3.8
- Created session summaries for parallel development
- Updated README.md with v0.9.1.2 features

## [1.0.3] - 2026-02-17

### Added
- Installation ID system (SHA-256 hash)
- License/tier management system
- Export manager service (port 8094)
- Tier API (port 8093)
- License API (port 8091)

### Fixed
- GPS configuration (gpsd DEVICES)
- Navigation page WebSocket connection
- Signal K vcan0 simulator errors

## [1.0.0] - 2026-02-16

### Added
- Marine Vision Phase 1 (camera streaming)
- Marine Vision Phase 2.1 (fish detection - basic)
- Telegram notifications for fish captures
- AI Assistant text interface
- Voice Assistant (3 wake words: Helm, Advisor, Counsel)
- Onboarding wizard (20 steps)
- Weather radar with touch controls
- Boatlog system
- Manual management (auto-search + upload)
- Health monitoring (engine + Pi)

### Initial Release
- Dashboard with engine gauges
- Navigation page with GPS
- Settings page
- Main menu with 9 buttons
- Signal K integration
- Node-RED flows
- NMEA2000 support via PiCAN-M
- Tier system (0-3)

---

## Version Format

d3kOS uses semantic versioning: MAJOR.MINOR.PATCH-STAGE

- MAJOR: Incompatible API changes
- MINOR: Backwards-compatible new features
- PATCH: Backwards-compatible bug fixes
- STAGE: alpha, beta, rc, stable
```

#### Step D3.3: Update MASTER_SYSTEM_SPEC.md Version

```bash
nano MASTER_SYSTEM_SPEC.md
```

**Update Header**:
```markdown
# d3kOS MASTER SYSTEM SPECIFICATION

**Version**: 3.8
**Date**: February 20, 2026
**Status**: APPROVED - v0.9.1.2 Release Complete
**Previous Version**: 3.7 (February 20, 2026)
```

**Verification**:
- [ ] README.md updated
- [ ] CHANGELOG.md created
- [ ] MASTER_SYSTEM_SPEC.md version incremented
- [ ] All documentation accurate
- [ ] Links working

---

### Task D4: Final Verification & GitHub Push (1 hour)

#### Step D4.1: System Verification

```bash
# SSH to Pi
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237

# Check version
cat /opt/d3kos/config/version.txt

# Check tier
curl http://localhost/tier/status | jq .

# Check all services
systemctl list-units 'd3kos-*' --all

# Check disk usage
df -h /

# Check logs for errors
sudo journalctl -p err -n 50
```

#### Step D4.2: Final Commit

```bash
cd /home/boatiq/Helm-OS

# Check status
git status

# Add all documentation
git add -A

# Final commit
git commit -m "Session D: Image Build & Final Documentation

- Created image build script and guide
- Completed testing matrix (all tests passing)
- Updated README.md for v0.9.1.2 release
- Created CHANGELOG.md
- Updated MASTER_SYSTEM_SPEC.md to v3.8
- Final system verification complete
- Ready for GitHub release

Closes: v0.9.1.2 release preparation
See: doc/IMAGE_BUILD_GUIDE.md, doc/TESTING_MATRIX_v0.9.1.2.md"

git push origin main
```

#### Step D4.3: Push to GitHub

```bash
# Ensure all commits pushed
git push origin main

# Verify on GitHub
# https://github.com/SkipperDon/d3kos

# Check commit history
git log --oneline -10
```

#### Step D4.4: Create GitHub Release (Optional)

**GitHub Release Steps** (manual):
1. Go to https://github.com/SkipperDon/d3kos/releases
2. Click "Create a new release"
3. Tag: v0.9.1.2
4. Title: "d3kOS v0.9.1.2 - Tier 0 Installation Complete"
5. Description: Copy from CHANGELOG.md
6. Upload files:
   - d3kos-v0.9.1.2-YYYYMMDD.img.gz
   - d3kos-v0.9.1.2-YYYYMMDD.img.gz.sha256
   - d3kos-v0.9.1.2-YYYYMMDD_README.txt
7. Publish release

**Verification**:
- [ ] All commits pushed to GitHub
- [ ] Documentation visible in repo
- [ ] Release created (if building image)
- [ ] Download link working

---

## FINAL INTEGRATION & TESTING

**After all 4 sessions complete**

### Integration Testing

```bash
# Run full system test
cd /home/boatiq/Helm-OS/doc
bash -c "
echo '🧪 Running integration tests...'

# Test 1: All services running
systemctl is-active d3kos-* signalk nodered nginx

# Test 2: All APIs responding
curl -f http://localhost/license/info
curl -f http://localhost/tier/status
curl -f http://localhost/export/status
curl -f http://localhost/api/timezone
curl -f http://localhost/healing/stats
curl -f http://localhost/api/backup/list

# Test 3: Web pages load
curl -f http://localhost/
curl -f http://localhost/settings.html
curl -f http://localhost/dashboard.html

echo '✅ Integration tests complete'
"
```

### Final Checklist

- [ ] Session A complete and committed
- [ ] Session B complete and committed
- [ ] Session C complete and committed
- [ ] Session D complete and committed
- [ ] All services running
- [ ] All APIs responding
- [ ] All web pages loading
- [ ] Testing matrix 100% passing
- [ ] Documentation updated
- [ ] GitHub pushed
- [ ] Image built (optional)
- [ ] Release created (optional)

---

## SUMMARY

**d3kOS v0.9.1.2 Release Complete! 🎉**

### What Was Built

1. **Session A (Foundation)**
   - Version 0.9.1.2
   - Tier 3 for testing
   - Timezone auto-detection
   - Voice assistant fix

2. **Session B (Intelligence)**
   - AI-powered self-healing
   - Issue detection
   - Auto-remediation
   - History tracking

3. **Session C (Data)**
   - Export queue with retry
   - Boatlog CSV export fix
   - Backup & restore system

4. **Session D (Deployment)**
   - Image build process
   - Testing matrix
   - Final documentation
   - GitHub release

### Total Effort

- **Session A**: 6-8 hours
- **Session B**: 6-8 hours
- **Session C**: 6-8 hours
- **Session D**: 6-8 hours
- **Total**: 24-32 hours (can run B/C/D in parallel after A)

### Files Created/Modified

- **Scripts**: 6 new (timezone, self-healing, backup, image build)
- **Services**: 8 new systemd services
- **APIs**: 4 new API services (ports 8098-8100)
- **Documentation**: 15+ markdown files
- **Web Pages**: 3 modified (settings, boatlog, settings-healing)
- **Commits**: 4 major commits (one per session)

### Result

**d3kOS v0.9.1.2 = Complete Tier 0 Installation**

✅ All core features implemented
✅ All features tested
✅ All features documented
✅ All changes committed
✅ Ready for distribution

**Next Steps:**
- Build and distribute image
- Gather user feedback
- Plan v0.9.2 improvements
- Continue with Tier 1/2/3 features (mobile app, ecommerce)

---

**End of Release Plan**
