# Session B: License/Tier System Implementation Guide

**Task ID:** Task #2 - Implement license/tier system and feature restrictions
**Date Prepared:** 2026-02-17
**Estimated Time:** 8-12 hours
**Status:** ✅ Fully planned and ready to implement
**Dependencies:** Task #1 (Installation ID System) MUST be completed first

---

## CRITICAL: Prerequisites

**BEFORE STARTING THIS TASK:**

1. ✅ Task #1 (Installation ID) MUST be complete
2. ✅ File `/opt/d3kos/config/license.json` MUST exist
3. ✅ License API at `http://localhost/license/info` MUST be working
4. ✅ Installation ID MUST be 16-character hex format

**Verify Prerequisites:**
```bash
# Check license.json exists
ls -lh /opt/d3kos/config/license.json

# Check license API is running
curl http://localhost/license/info

# Verify installation_id format (should be 16 hex chars)
cat /opt/d3kos/config/license.json | jq -r '.installation_id'
```

**Expected Output:**
```json
{
  "installation_id": "550e8400e29b41d4",
  "tier": 0,
  "reset_count": 0,
  "max_resets": 10,
  "version": "1.0.3",
  "features": {
    "voice_assistant": false,
    "camera": false,
    "unlimited_resets": false,
    "cloud_sync": false
  }
}
```

If any of these checks fail, **STOP** and complete Task #1 first.

---

## CURRENT PROBLEM

**What's Wrong:**
- No tier detection logic exists
- Voice assistant enabled for Tier 0 (should be Tier 2+ only)
- Camera enabled for Tier 0 (should be Tier 2+ only)
- No reset counter tracking (Tier 0 limited to 10 resets)
- System violating spec requirements

**Spec Requirements (MASTER_SYSTEM_SPEC.md Section 6.3):**

**Tier 0 (Default - FREE):**
- ✓ Dashboard, health monitoring, boat log (30 days)
- ✓ Onboarding wizard (10 resets max)
- ✗ Voice assistant DISABLED
- ✗ Camera DISABLED

**Tier 2 (OpenCPN installed or Paid):**
- ✓ All Tier 0 features
- ✓ Voice assistant ENABLED
- ✓ Camera ENABLED
- ✓ Unlimited resets
- ✓ Historical graphs (90 days)

**Tier 3 (Enterprise - Paid Annual):**
- ✓ All Tier 2 features
- ✓ Cloud sync
- ✓ Multi-boat support
- ✓ Unlimited resets

---

## IMPLEMENTATION OVERVIEW

### Phase Breakdown

**Phase 1: Tier Detection Logic** (3-4 hours)
- OpenCPN detection script
- Tier upgrade logic
- License.json updates

**Phase 2: Feature Restrictions** (2-3 hours)
- Service control (voice, camera)
- Reset counter enforcement
- Onboarding restrictions

**Phase 3: UI Updates** (2-3 hours)
- Settings page tier display
- Onboarding wizard footer
- Feature locked messages

**Phase 4: Testing** (1-2 hours)
- Tier 0 restrictions test
- Tier 2 auto-detection test
- Reset counter test
- Service control test

---

## PHASE 1: TIER DETECTION LOGIC (3-4 HOURS)

### Step 1.1: Create OpenCPN Detection Script

**File:** `/opt/d3kos/scripts/detect-opencpn.sh`

```bash
#!/bin/bash
# detect-opencpn.sh - Detect OpenCPN installation for Tier 2 auto-upgrade
# Part of d3kOS Tier Management System

set -e

OPENCPN_PATHS=(
    "/usr/bin/opencpn"
    "/usr/local/bin/opencpn"
    "/opt/opencpn/bin/opencpn"
)

# Check if OpenCPN is installed
for path in "${OPENCPN_PATHS[@]}"; do
    if [ -f "$path" ]; then
        echo "true"
        exit 0
    fi
done

# Check via dpkg (Debian package manager)
if dpkg -l | grep -q "^ii.*opencpn"; then
    echo "true"
    exit 0
fi

# Check via flatpak
if command -v flatpak &> /dev/null; then
    if flatpak list | grep -q "opencpn"; then
        echo "true"
        exit 0
    fi
fi

echo "false"
exit 0
```

**Set Permissions:**
```bash
sudo chmod +x /opt/d3kos/scripts/detect-opencpn.sh
sudo chown d3kos:d3kos /opt/d3kos/scripts/detect-opencpn.sh
```

**Test:**
```bash
# Should return "false" (OpenCPN not installed by default)
/opt/d3kos/scripts/detect-opencpn.sh
```

---

### Step 1.2: Create Tier Manager Script

**File:** `/opt/d3kos/scripts/tier-manager.sh`

```bash
#!/bin/bash
# tier-manager.sh - Manage license tiers and feature restrictions
# Part of d3kOS Tier Management System

set -e

LICENSE_FILE="/opt/d3kos/config/license.json"
SCRIPT_DIR="$(dirname "$0")"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a /var/log/d3kos-tier-manager.log
}

# Check if license.json exists
if [ ! -f "$LICENSE_FILE" ]; then
    log "ERROR: license.json not found at $LICENSE_FILE"
    log "ERROR: Run generate-installation-id.sh first (Task #1)"
    exit 1
fi

# Read current tier
current_tier=$(jq -r '.tier' "$LICENSE_FILE")
log "Current tier: $current_tier"

# Detect OpenCPN installation
opencpn_installed=$("$SCRIPT_DIR/detect-opencpn.sh")
log "OpenCPN installed: $opencpn_installed"

# Auto-upgrade to Tier 2 if OpenCPN is installed
if [ "$opencpn_installed" = "true" ] && [ "$current_tier" -lt 2 ]; then
    log "OpenCPN detected! Upgrading to Tier 2..."

    # Update license.json
    jq '.tier = 2 |
        .features.voice_assistant = true |
        .features.camera = true |
        .features.unlimited_resets = true |
        .max_resets = 9999 |
        .upgrade_method = "opencpn_detect" |
        .upgraded_at = (now | strftime("%Y-%m-%dT%H:%M:%SZ"))' \
        "$LICENSE_FILE" > "$LICENSE_FILE.tmp"

    mv "$LICENSE_FILE.tmp" "$LICENSE_FILE"
    chmod 644 "$LICENSE_FILE"
    chown d3kos:d3kos "$LICENSE_FILE"

    log "Upgraded to Tier 2 successfully!"
    current_tier=2
fi

# Check if paid tier (subscription)
is_paid=$(jq -r '.is_paid_tier // false' "$LICENSE_FILE")
subscription_status=$(jq -r '.subscription_status // "none"' "$LICENSE_FILE")

if [ "$is_paid" = "true" ] && [ "$subscription_status" = "active" ]; then
    paid_tier=$(jq -r '.paid_tier_level // 0' "$LICENSE_FILE")

    if [ "$paid_tier" -eq 2 ] && [ "$current_tier" -lt 2 ]; then
        log "Active Tier 2 subscription detected! Upgrading..."
        jq '.tier = 2 |
            .features.voice_assistant = true |
            .features.camera = true |
            .features.unlimited_resets = true |
            .max_resets = 9999' \
            "$LICENSE_FILE" > "$LICENSE_FILE.tmp"
        mv "$LICENSE_FILE.tmp" "$LICENSE_FILE"
        current_tier=2
    fi

    if [ "$paid_tier" -eq 3 ] && [ "$current_tier" -lt 3 ]; then
        log "Active Tier 3 subscription detected! Upgrading..."
        jq '.tier = 3 |
            .features.voice_assistant = true |
            .features.camera = true |
            .features.unlimited_resets = true |
            .features.cloud_sync = true |
            .max_resets = 9999' \
            "$LICENSE_FILE" > "$LICENSE_FILE.tmp"
        mv "$LICENSE_FILE.tmp" "$LICENSE_FILE"
        current_tier=3
    fi
fi

# Update feature flags based on tier
case $current_tier in
    0)
        log "Tier 0: Disabling voice assistant and camera"
        jq '.features.voice_assistant = false |
            .features.camera = false |
            .features.unlimited_resets = false |
            .features.cloud_sync = false |
            .max_resets = 10' \
            "$LICENSE_FILE" > "$LICENSE_FILE.tmp"
        mv "$LICENSE_FILE.tmp" "$LICENSE_FILE"
        ;;
    1)
        log "Tier 1: Disabling voice assistant and camera (mobile app integration only)"
        jq '.features.voice_assistant = false |
            .features.camera = false |
            .features.unlimited_resets = false |
            .features.cloud_sync = false |
            .max_resets = 10' \
            "$LICENSE_FILE" > "$LICENSE_FILE.tmp"
        mv "$LICENSE_FILE.tmp" "$LICENSE_FILE"
        ;;
    2)
        log "Tier 2: Enabling voice assistant and camera"
        jq '.features.voice_assistant = true |
            .features.camera = true |
            .features.unlimited_resets = true |
            .features.cloud_sync = false |
            .max_resets = 9999' \
            "$LICENSE_FILE" > "$LICENSE_FILE.tmp"
        mv "$LICENSE_FILE.tmp" "$LICENSE_FILE"
        ;;
    3)
        log "Tier 3: Enabling all features (voice, camera, cloud sync)"
        jq '.features.voice_assistant = true |
            .features.camera = true |
            .features.unlimited_resets = true |
            .features.cloud_sync = true |
            .max_resets = 9999' \
            "$LICENSE_FILE" > "$LICENSE_FILE.tmp"
        mv "$LICENSE_FILE.tmp" "$LICENSE_FILE"
        ;;
esac

log "Tier management complete. Current tier: $current_tier"

# Output tier for systemd services to use
echo "$current_tier"
```

**Set Permissions:**
```bash
sudo chmod +x /opt/d3kos/scripts/tier-manager.sh
sudo chown d3kos:d3kos /opt/d3kos/scripts/tier-manager.sh
```

**Test:**
```bash
# Should detect Tier 0, disable voice/camera
sudo /opt/d3kos/scripts/tier-manager.sh

# Check updated license.json
cat /opt/d3kos/config/license.json | jq '.features'
```

**Expected Output:**
```json
{
  "voice_assistant": false,
  "camera": false,
  "unlimited_resets": false,
  "cloud_sync": false
}
```

---

### Step 1.3: Create Tier Manager Systemd Service

**File:** `/etc/systemd/system/d3kos-tier-manager.service`

```ini
[Unit]
Description=d3kOS Tier Management Service
Documentation=https://github.com/boatiq/d3kos
After=network-online.target d3kos-first-boot.service
Wants=network-online.target

[Service]
Type=oneshot
User=root
ExecStart=/opt/d3kos/scripts/tier-manager.sh
StandardOutput=journal
StandardError=journal
RemainAfterExit=yes

# Run on every boot to check for tier changes
Restart=no

[Install]
WantedBy=multi-user.target
```

**Enable and Test Service:**
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (runs on every boot)
sudo systemctl enable d3kos-tier-manager.service

# Test service
sudo systemctl start d3kos-tier-manager.service

# Check status
systemctl status d3kos-tier-manager.service

# View logs
journalctl -u d3kos-tier-manager.service -n 20
```

---

### Step 1.4: Create Tier API Service

**File:** `/opt/d3kos/services/tier/tier-api.py`

```python
#!/usr/bin/env python3
"""
d3kOS Tier API Service
Provides HTTP API for checking tier status and features
Port: 8091
"""

from flask import Flask, jsonify, request
import json
import os
import sys
import logging
from datetime import datetime

app = Flask(__name__)

# Configuration
LICENSE_FILE = '/opt/d3kos/config/license.json'
PORT = 8091

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('tier-api')

def load_license():
    """Load license.json file"""
    try:
        if not os.path.exists(LICENSE_FILE):
            logger.error(f"License file not found: {LICENSE_FILE}")
            return None

        with open(LICENSE_FILE, 'r') as f:
            license_data = json.load(f)

        return license_data
    except Exception as e:
        logger.error(f"Error loading license file: {e}")
        return None

def is_feature_enabled(feature_name):
    """Check if a specific feature is enabled for current tier"""
    license_data = load_license()
    if not license_data:
        return False

    features = license_data.get('features', {})
    return features.get(feature_name, False)

@app.route('/tier/status', methods=['GET'])
def get_tier_status():
    """Get current tier and all feature flags"""
    license_data = load_license()

    if not license_data:
        return jsonify({
            'success': False,
            'error': 'License file not found'
        }), 500

    return jsonify({
        'success': True,
        'tier': license_data.get('tier', 0),
        'installation_id': license_data.get('installation_id', 'unknown'),
        'features': license_data.get('features', {}),
        'reset_count': license_data.get('reset_count', 0),
        'max_resets': license_data.get('max_resets', 10),
        'subscription_status': license_data.get('subscription_status', 'none'),
        'is_paid_tier': license_data.get('is_paid_tier', False)
    })

@app.route('/tier/feature/<feature_name>', methods=['GET'])
def check_feature(feature_name):
    """Check if a specific feature is enabled"""
    enabled = is_feature_enabled(feature_name)

    return jsonify({
        'success': True,
        'feature': feature_name,
        'enabled': enabled
    })

@app.route('/tier/increment-reset', methods=['POST'])
def increment_reset_counter():
    """Increment reset counter (called by onboarding wizard)"""
    license_data = load_license()

    if not license_data:
        return jsonify({
            'success': False,
            'error': 'License file not found'
        }), 500

    current_count = license_data.get('reset_count', 0)
    max_resets = license_data.get('max_resets', 10)

    # Check if max resets exceeded
    if current_count >= max_resets:
        return jsonify({
            'success': False,
            'error': f'Maximum resets ({max_resets}) exceeded',
            'reset_count': current_count,
            'max_resets': max_resets,
            'upgrade_required': True
        }), 403

    # Increment counter
    license_data['reset_count'] = current_count + 1
    license_data['last_reset'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    # Save updated license.json
    try:
        with open(LICENSE_FILE, 'w') as f:
            json.dump(license_data, f, indent=2)

        logger.info(f"Reset counter incremented: {current_count} -> {current_count + 1}")

        return jsonify({
            'success': True,
            'reset_count': license_data['reset_count'],
            'max_resets': max_resets,
            'resets_remaining': max_resets - license_data['reset_count']
        })

    except Exception as e:
        logger.error(f"Error saving license file: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to update license file'
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'tier-api'})

if __name__ == '__main__':
    logger.info(f"Starting d3kOS Tier API on port {PORT}")
    app.run(host='127.0.0.1', port=PORT, debug=False)
```

**Set Permissions:**
```bash
sudo mkdir -p /opt/d3kos/services/tier
sudo chmod +x /opt/d3kos/services/tier/tier-api.py
sudo chown -R d3kos:d3kos /opt/d3kos/services/tier
```

**Install Dependencies:**
```bash
# Flask should already be installed from AI API service
sudo apt-get update
sudo apt-get install -y python3-flask
```

---

### Step 1.5: Create Tier API Systemd Service

**File:** `/etc/systemd/system/d3kos-tier-api.service`

```ini
[Unit]
Description=d3kOS Tier API Service
Documentation=https://github.com/boatiq/d3kos
After=network.target d3kos-tier-manager.service

[Service]
Type=simple
User=d3kos
WorkingDirectory=/opt/d3kos/services/tier
ExecStart=/usr/bin/python3 /opt/d3kos/services/tier/tier-api.py
Restart=always
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Enable and Test Service:**
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable d3kos-tier-api.service

# Start service
sudo systemctl start d3kos-tier-api.service

# Check status
systemctl status d3kos-tier-api.service

# Test API
curl http://localhost:8091/tier/status | jq

# Test feature check
curl http://localhost:8091/tier/feature/voice_assistant | jq
```

**Expected Output:**
```json
{
  "success": true,
  "tier": 0,
  "installation_id": "550e8400e29b41d4",
  "features": {
    "voice_assistant": false,
    "camera": false,
    "unlimited_resets": false,
    "cloud_sync": false
  },
  "reset_count": 0,
  "max_resets": 10
}
```

---

### Step 1.6: Add Nginx Proxy for Tier API

**File:** `/etc/nginx/sites-enabled/default`

**Add this location block** (after the license API block):

```nginx
    # Tier API (port 8091)
    location /tier/ {
        proxy_pass http://127.0.0.1:8091/tier/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
```

**Test and Reload Nginx:**
```bash
# Test nginx configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx

# Test external access
curl http://localhost/tier/status | jq
```

---

## PHASE 2: FEATURE RESTRICTIONS (2-3 HOURS)

### Step 2.1: Update Voice Assistant Service (Conditional Start)

**File:** `/etc/systemd/system/d3kos-voice.service`

**Modify the `[Service]` section** to add a pre-start check:

```ini
[Unit]
Description=d3kOS Voice Assistant Service
Documentation=https://github.com/boatiq/d3kos
After=network.target d3kos-tier-manager.service d3kos-tier-api.service

[Service]
Type=simple
User=d3kos
WorkingDirectory=/opt/d3kos/services/voice

# Check if voice assistant is enabled for current tier
ExecStartPre=/bin/bash -c 'curl -s http://localhost:8091/tier/feature/voice_assistant | jq -e ".enabled == true" || exit 1'

ExecStart=/usr/bin/python3 /opt/d3kos/services/voice/voice-assistant-hybrid.py --auto-start
Restart=on-failure
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Important:** The `ExecStartPre` line checks the tier API. If voice is disabled (Tier 0/1), the service won't start.

**Reload and Test:**
```bash
# Reload systemd
sudo systemctl daemon-reload

# Try to start voice service (should FAIL on Tier 0)
sudo systemctl start d3kos-voice.service

# Check status (should show "failed" with tier message)
systemctl status d3kos-voice.service

# View logs
journalctl -u d3kos-voice.service -n 20
```

**Expected:** Service should fail to start with a message about voice_assistant being disabled.

---

### Step 2.2: Update Camera Service (Conditional Start)

**File:** `/etc/systemd/system/d3kos-camera-stream.service`

**Modify the `[Service]` section:**

```ini
[Unit]
Description=d3kOS Camera Stream Manager
Documentation=https://github.com/boatiq/d3kos
After=network.target d3kos-tier-manager.service d3kos-tier-api.service

[Service]
Type=simple
User=d3kos
WorkingDirectory=/opt/d3kos/services/marine-vision

# Check if camera is enabled for current tier
ExecStartPre=/bin/bash -c 'curl -s http://localhost:8091/tier/feature/camera | jq -e ".enabled == true" || exit 1'

ExecStart=/usr/bin/python3 /opt/d3kos/services/marine-vision/camera_stream_manager.py
Restart=on-failure
RestartSec=10

StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Reload and Test:**
```bash
# Reload systemd
sudo systemctl daemon-reload

# Try to start camera service (should FAIL on Tier 0)
sudo systemctl start d3kos-camera-stream.service

# Check status
systemctl status d3kos-camera-stream.service
```

---

### Step 2.3: Update Fish Detector Service (Conditional Start)

**File:** `/etc/systemd/system/d3kos-fish-detector.service`

**Add the tier check:**

```ini
[Unit]
Description=d3kOS Fish Detection Service
Documentation=https://github.com/boatiq/d3kos
After=network.target d3kos-camera-stream.service d3kos-tier-manager.service d3kos-tier-api.service
Requires=d3kos-camera-stream.service

[Service]
Type=simple
User=d3kos
WorkingDirectory=/opt/d3kos/services/marine-vision

# Check if camera is enabled for current tier
ExecStartPre=/bin/bash -c 'curl -s http://localhost:8091/tier/feature/camera | jq -e ".enabled == true" || exit 1'

ExecStart=/usr/bin/python3 /opt/d3kos/services/marine-vision/fish_detector.py
Restart=on-failure
RestartSec=10

StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Reload:**
```bash
sudo systemctl daemon-reload
```

---

## PHASE 3: UI UPDATES (2-3 HOURS)

### Step 3.1: Update Onboarding Wizard (Reset Counter)

**File:** `/var/www/html/onboarding.html`

**Backup first:**
```bash
sudo cp /var/www/html/onboarding.html /var/www/html/onboarding.html.bak.tier-system
```

**Find the footer section** (around line 550-600) and add reset counter display:

```html
<!-- Progress footer with reset counter -->
<div style="position: fixed; bottom: 0; left: 0; right: 0; background: rgba(0,0,0,0.9);
            padding: 15px; text-align: center; font-size: 18px; border-top: 2px solid #00CC00;">
    <span id="progress-text">Step <span id="current-step">1</span> of 20</span>
    <span id="reset-counter-display" style="margin-left: 30px; color: #FFD700;"></span>
</div>
```

**Add JavaScript function** to fetch and display reset counter (in `<script>` section):

```javascript
// Fetch reset counter from Tier API
async function updateResetCounter() {
    try {
        const response = await fetch('/tier/status');
        const data = await response.json();

        if (data.success) {
            const resetCount = data.reset_count || 0;
            const maxResets = data.max_resets || 10;
            const tier = data.tier || 0;

            const counterDisplay = document.getElementById('reset-counter-display');

            if (tier === 0 || tier === 1) {
                // Show reset counter for Tier 0/1
                const remaining = maxResets - resetCount;
                counterDisplay.innerHTML = `<strong>Resets:</strong> ${resetCount} of ${maxResets} (${remaining} remaining)`;

                if (remaining <= 2) {
                    counterDisplay.style.color = '#FF3333'; // Red warning
                } else if (remaining <= 5) {
                    counterDisplay.style.color = '#FFA500'; // Orange warning
                } else {
                    counterDisplay.style.color = '#FFD700'; // Gold
                }
            } else {
                // Tier 2/3 - Unlimited resets
                counterDisplay.innerHTML = `<strong>Resets:</strong> Unlimited (Tier ${tier})`;
                counterDisplay.style.color = '#00CC00'; // Green
            }
        }
    } catch (error) {
        console.error('Error fetching reset counter:', error);
    }
}

// Call on page load
window.addEventListener('load', updateResetCounter);
```

**Add reset increment** when wizard completes (in the "Finish" button handler):

```javascript
// In the finish button click handler (Step 20)
async function completeWizard() {
    // Increment reset counter
    try {
        const response = await fetch('/tier/increment-reset', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (!data.success) {
            if (data.upgrade_required) {
                // Max resets exceeded
                alert('❌ Maximum resets exceeded!\n\n' +
                      `You have reached the limit of ${data.max_resets} resets for Tier 0.\n\n` +
                      'To reset again, upgrade to Tier 2 by:\n' +
                      '1. Installing OpenCPN (auto-detects)\n' +
                      '2. Purchasing Tier 2 subscription ($9.99/month)\n\n' +
                      'Visit Settings → Subscription for details.');
                return; // Don't complete wizard
            }
        }
    } catch (error) {
        console.error('Error incrementing reset counter:', error);
    }

    // Continue with wizard completion...
    // (existing code for saving config, generating QR, etc.)
}
```

---

### Step 3.2: Update Settings Page (Tier Display)

**File:** `/var/www/html/settings.html`

**Backup first:**
```bash
sudo cp /var/www/html/settings.html /var/www/html/settings.html.bak.tier-system
```

**Add new section** after the "System Information" section:

```html
<!-- License & Tier Information -->
<div style="background: #1a1a1a; padding: 20px; margin-bottom: 20px; border-left: 4px solid #00CC00;">
    <h2 style="margin: 0 0 15px 0; font-size: 24px;">License & Tier</h2>

    <div id="tier-info" style="font-size: 20px; line-height: 1.8;">
        <div style="margin-bottom: 10px;">
            <strong>Current Tier:</strong>
            <span id="tier-level" style="color: #FFD700; font-size: 28px; font-weight: bold;">Loading...</span>
        </div>

        <div style="margin-bottom: 10px;">
            <strong>Installation ID:</strong>
            <span id="installation-id" style="color: #00CC00; font-family: monospace;">Loading...</span>
        </div>

        <div style="margin-bottom: 10px;">
            <strong>Reset Counter:</strong>
            <span id="reset-info">Loading...</span>
        </div>

        <div style="margin-top: 20px; padding: 15px; background: #000; border: 1px solid #333;">
            <h3 style="margin: 0 0 10px 0; font-size: 20px; color: #00CC00;">Available Features</h3>
            <div id="features-list" style="font-size: 18px;">
                Loading...
            </div>
        </div>

        <div id="upgrade-message" style="display: none; margin-top: 20px; padding: 15px;
                                          background: #1a3300; border: 2px solid #00CC00;">
            <strong>🚀 Upgrade to Tier 2</strong><br>
            <p style="margin: 10px 0;">Get unlimited resets, voice assistant, and camera features!</p>
            <p style="margin: 10px 0; font-size: 18px;">
                <strong>Option 1:</strong> Install OpenCPN (free, auto-detects)<br>
                <strong>Option 2:</strong> Purchase subscription ($9.99/month)
            </p>
            <button onclick="window.location.href='subscription.html'"
                    style="background: #00CC00; color: #000; border: none; padding: 15px 30px;
                           font-size: 20px; cursor: pointer; margin-top: 10px;">
                View Subscription Options
            </button>
        </div>
    </div>
</div>
```

**Add JavaScript** to fetch and display tier info:

```javascript
// Fetch tier information
async function loadTierInfo() {
    try {
        const response = await fetch('/tier/status');
        const data = await response.json();

        if (data.success) {
            // Tier level
            const tierLevel = document.getElementById('tier-level');
            tierLevel.textContent = `Tier ${data.tier}`;

            if (data.tier === 0) {
                tierLevel.style.color = '#888888'; // Gray
                document.getElementById('upgrade-message').style.display = 'block';
            } else if (data.tier === 1) {
                tierLevel.style.color = '#4169E1'; // Blue
            } else if (data.tier === 2) {
                tierLevel.style.color = '#FFD700'; // Gold
            } else if (data.tier === 3) {
                tierLevel.style.color = '#00FF00'; // Bright green
            }

            // Installation ID
            document.getElementById('installation-id').textContent = data.installation_id;

            // Reset counter
            const resetInfo = document.getElementById('reset-info');
            if (data.features.unlimited_resets) {
                resetInfo.innerHTML = '<span style="color: #00CC00;">Unlimited</span>';
            } else {
                const remaining = data.max_resets - data.reset_count;
                resetInfo.innerHTML = `${data.reset_count} of ${data.max_resets}
                    (<span style="color: ${remaining <= 2 ? '#FF3333' : '#FFD700'};">${remaining} remaining</span>)`;
            }

            // Features list
            const features = data.features;
            const featuresList = document.getElementById('features-list');
            featuresList.innerHTML = `
                <div style="margin: 5px 0;">
                    ${features.voice_assistant ? '✅' : '❌'} Voice Assistant
                    ${!features.voice_assistant ? '<span style="color: #FF3333; font-size: 16px;"> (Tier 2+ required)</span>' : ''}
                </div>
                <div style="margin: 5px 0;">
                    ${features.camera ? '✅' : '❌'} Camera & Marine Vision
                    ${!features.camera ? '<span style="color: #FF3333; font-size: 16px;"> (Tier 2+ required)</span>' : ''}
                </div>
                <div style="margin: 5px 0;">
                    ${features.unlimited_resets ? '✅' : '❌'} Unlimited Resets
                    ${!features.unlimited_resets ? '<span style="color: #FF3333; font-size: 16px;"> (Tier 2+ required)</span>' : ''}
                </div>
                <div style="margin: 5px 0;">
                    ${features.cloud_sync ? '✅' : '❌'} Cloud Sync
                    ${!features.cloud_sync ? '<span style="color: #888; font-size: 16px;"> (Tier 3 only)</span>' : ''}
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading tier info:', error);
        document.getElementById('tier-level').textContent = 'Error';
    }
}

// Auto-refresh every 30 seconds
window.addEventListener('load', () => {
    loadTierInfo();
    setInterval(loadTierInfo, 30000);
});
```

---

### Step 3.3: Update Main Menu (Disable Buttons for Tier 0/1)

**File:** `/var/www/html/index.html`

**Backup first:**
```bash
sudo cp /var/www/html/index.html /var/www/html/index.html.bak.tier-system
```

**Add JavaScript** to disable voice and camera buttons based on tier:

```javascript
// Check tier and disable features if not available
async function checkTierRestrictions() {
    try {
        const response = await fetch('/tier/status');
        const data = await response.json();

        if (data.success) {
            const features = data.features;

            // Disable voice button if not available
            if (!features.voice_assistant) {
                const voiceButtons = document.querySelectorAll('[onclick*="voice"], [onclick*="Voice"]');
                voiceButtons.forEach(btn => {
                    btn.style.opacity = '0.3';
                    btn.style.cursor = 'not-allowed';
                    btn.onclick = function(e) {
                        e.preventDefault();
                        alert('Voice Assistant requires Tier 2+\n\n' +
                              'Upgrade by:\n' +
                              '1. Installing OpenCPN (free)\n' +
                              '2. Purchasing Tier 2 ($9.99/month)\n\n' +
                              'Visit Settings → License & Tier for details.');
                        return false;
                    };
                });
            }

            // Disable camera button if not available
            if (!features.camera) {
                const cameraButtons = document.querySelectorAll('[onclick*="marine-vision"]');
                cameraButtons.forEach(btn => {
                    btn.style.opacity = '0.3';
                    btn.style.cursor = 'not-allowed';
                    btn.onclick = function(e) {
                        e.preventDefault();
                        alert('Marine Vision Camera requires Tier 2+\n\n' +
                              'Upgrade by:\n' +
                              '1. Installing OpenCPN (free)\n' +
                              '2. Purchasing Tier 2 ($9.99/month)\n\n' +
                              'Visit Settings → License & Tier for details.');
                        return false;
                    };
                });
            }
        }
    } catch (error) {
        console.error('Error checking tier restrictions:', error);
    }
}

// Run on page load
window.addEventListener('load', checkTierRestrictions);
```

---

### Step 3.4: Update Marine Vision Page (Tier Check)

**File:** `/var/www/html/marine-vision.html`

**Add tier check** at the top of the page:

```javascript
// Check if camera is enabled for current tier
async function checkCameraAccess() {
    try {
        const response = await fetch('/tier/status');
        const data = await response.json();

        if (data.success && !data.features.camera) {
            // Camera not available - show upgrade message
            document.body.innerHTML = `
                <div style="text-align: center; padding: 50px; background: #000; color: #FFF;
                            font-family: Arial; min-height: 100vh;">
                    <h1 style="color: #FF3333; font-size: 48px; margin-bottom: 30px;">❌ Camera Not Available</h1>
                    <p style="font-size: 28px; margin-bottom: 20px;">Marine Vision Camera requires <strong>Tier 2</strong> or higher.</p>

                    <div style="background: #1a1a1a; padding: 30px; margin: 30px auto; max-width: 800px;
                                border: 2px solid #00CC00;">
                        <h2 style="color: #00CC00; margin-bottom: 20px;">How to Upgrade to Tier 2:</h2>
                        <p style="font-size: 24px; text-align: left; line-height: 1.8;">
                            <strong>Option 1 (FREE):</strong> Install OpenCPN navigation software<br>
                            <span style="margin-left: 40px; font-size: 20px; color: #888;">
                                System will auto-detect and upgrade to Tier 2
                            </span>
                        </p>
                        <p style="font-size: 24px; text-align: left; line-height: 1.8; margin-top: 20px;">
                            <strong>Option 2:</strong> Purchase Tier 2 subscription ($9.99/month)<br>
                            <span style="margin-left: 40px; font-size: 20px; color: #888;">
                                Includes voice assistant, camera, unlimited resets
                            </span>
                        </p>
                    </div>

                    <button onclick="window.location.href='/settings.html'"
                            style="background: #00CC00; color: #000; border: none; padding: 20px 40px;
                                   font-size: 24px; cursor: pointer; margin: 20px;">
                        Go to Settings
                    </button>

                    <button onclick="window.location.href='/'"
                            style="background: #333; color: #FFF; border: 2px solid #00CC00; padding: 20px 40px;
                                   font-size: 24px; cursor: pointer; margin: 20px;">
                        ← Main Menu
                    </button>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error checking camera access:', error);
    }
}

// Run on page load (before any other initialization)
checkCameraAccess().then(() => {
    // Continue with normal page initialization if access granted
    // ... (existing code)
});
```

---

## PHASE 4: TESTING (1-2 HOURS)

### Test 1: Tier 0 Restrictions

**Verify Tier 0 behavior:**

```bash
# Check license.json shows Tier 0
cat /opt/d3kos/config/license.json | jq '.tier, .features'

# Expected output:
# 0
# {
#   "voice_assistant": false,
#   "camera": false,
#   "unlimited_resets": false,
#   "cloud_sync": false
# }

# Check voice service is NOT running
systemctl status d3kos-voice.service
# Expected: inactive (dead) or failed

# Check camera service is NOT running
systemctl status d3kos-camera-stream.service
# Expected: inactive (dead) or failed

# Check tier API
curl http://localhost/tier/status | jq

# Test reset counter increment
curl -X POST http://localhost/tier/increment-reset | jq
# Expected: {"success": true, "reset_count": 1, "max_resets": 10, "resets_remaining": 9}

# Increment 9 more times to reach limit
for i in {2..10}; do
    curl -X POST http://localhost/tier/increment-reset | jq '.reset_count'
done

# Try one more time (should FAIL - max resets exceeded)
curl -X POST http://localhost/tier/increment-reset | jq
# Expected: {"success": false, "error": "Maximum resets (10) exceeded", "upgrade_required": true}
```

**Test in browser:**
1. Navigate to `http://192.168.1.237/`
2. Voice and Camera buttons should be grayed out
3. Click Voice button → Should show upgrade message
4. Click Camera button → Should show upgrade message
5. Go to Settings → Should show "Tier 0" with upgrade options
6. Go to Onboarding → Footer should show "Resets: X of 10"

---

### Test 2: OpenCPN Detection (Tier 2 Auto-Upgrade)

**Install OpenCPN:**

```bash
# Install OpenCPN
sudo apt-get update
sudo apt-get install -y opencpn

# Run tier manager to detect OpenCPN
sudo /opt/d3kos/scripts/tier-manager.sh

# Check logs
journalctl -u d3kos-tier-manager.service -n 30

# Expected log output:
# "OpenCPN detected! Upgrading to Tier 2..."
# "Upgraded to Tier 2 successfully!"

# Verify license.json updated
cat /opt/d3kos/config/license.json | jq '.tier, .features, .upgrade_method'

# Expected output:
# 2
# {
#   "voice_assistant": true,
#   "camera": true,
#   "unlimited_resets": true,
#   "cloud_sync": false
# }
# "opencpn_detect"
```

**Test Tier 2 features:**

```bash
# Voice service should now START successfully
sudo systemctl start d3kos-voice.service
systemctl status d3kos-voice.service
# Expected: active (running)

# Camera service should now START successfully
sudo systemctl start d3kos-camera-stream.service
systemctl status d3kos-camera-stream.service
# Expected: active (running)

# Reset counter should show unlimited
curl http://localhost/tier/status | jq '.max_resets, .features.unlimited_resets'
# Expected: 9999, true
```

**Test in browser:**
1. Refresh main menu → Voice and Camera buttons should be enabled (full opacity)
2. Click Marine Vision → Should load normally (no upgrade message)
3. Go to Settings → Should show "Tier 2" in gold
4. Go to Onboarding → Footer should show "Resets: Unlimited (Tier 2)"

---

### Test 3: Reboot Persistence

**Reboot and verify tier persists:**

```bash
# Reboot system
sudo reboot

# After reboot, SSH back in
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237

# Check tier manager ran on boot
journalctl -u d3kos-tier-manager.service -b

# Check tier status
curl http://localhost/tier/status | jq '.tier'
# Expected: 2 (if OpenCPN was installed)

# Check services auto-started (Tier 2)
systemctl status d3kos-voice.service
systemctl status d3kos-camera-stream.service
# Both should be running
```

---

### Test 4: Downgrade Scenario (Remove OpenCPN)

**Test tier downgrade:**

```bash
# Remove OpenCPN
sudo apt-get remove -y opencpn

# Run tier manager
sudo /opt/d3kos/scripts/tier-manager.sh

# Check logs
journalctl -u d3kos-tier-manager.service -n 20

# Tier should remain 2 (upgrade_method: opencpn_detect means "was upgraded")
# This is INTENTIONAL - we don't downgrade if OpenCPN is removed

# To manually downgrade (for testing):
sudo jq '.tier = 0 | .features.voice_assistant = false | .features.camera = false | .max_resets = 10' \
    /opt/d3kos/config/license.json > /tmp/license.json
sudo mv /tmp/license.json /opt/d3kos/config/license.json

# Reboot to apply changes
sudo reboot
```

---

## SUCCESS CRITERIA

After completing all phases, verify:

✅ **Tier Detection:**
- [ ] Tier 0 by default (fresh install)
- [ ] Tier 2 auto-upgrade when OpenCPN installed
- [ ] Tier API returns correct tier status

✅ **Feature Restrictions:**
- [ ] Voice service disabled on Tier 0/1
- [ ] Camera service disabled on Tier 0/1
- [ ] Services start successfully on Tier 2+

✅ **Reset Counter:**
- [ ] Counter increments on each onboarding completion
- [ ] Maximum 10 resets enforced for Tier 0
- [ ] Upgrade required message shown at limit
- [ ] Unlimited resets for Tier 2+

✅ **UI Updates:**
- [ ] Settings page shows tier level and features
- [ ] Onboarding footer shows reset counter
- [ ] Main menu disables locked features (grayed out)
- [ ] Marine Vision shows upgrade message for Tier 0/1
- [ ] Tier 2+ users see all features enabled

✅ **Persistence:**
- [ ] Tier persists across reboots
- [ ] Reset counter persists
- [ ] Services auto-start based on tier

✅ **API Endpoints:**
- [ ] `GET /tier/status` works
- [ ] `GET /tier/feature/<name>` works
- [ ] `POST /tier/increment-reset` works
- [ ] All endpoints accessible via nginx proxy

---

## ROLLBACK PLAN

If something goes wrong:

### Rollback Step 1: Restore Backups

```bash
# Restore onboarding.html
sudo cp /var/www/html/onboarding.html.bak.tier-system /var/www/html/onboarding.html

# Restore settings.html
sudo cp /var/www/html/settings.html.bak.tier-system /var/www/html/settings.html

# Restore index.html
sudo cp /var/www/html/index.html.bak.tier-system /var/www/html/index.html
```

### Rollback Step 2: Stop and Disable Services

```bash
# Stop tier services
sudo systemctl stop d3kos-tier-api.service
sudo systemctl stop d3kos-tier-manager.service

# Disable services
sudo systemctl disable d3kos-tier-api.service
sudo systemctl disable d3kos-tier-manager.service

# Restore original voice service
sudo systemctl daemon-reload
sudo systemctl enable d3kos-voice.service
sudo systemctl start d3kos-voice.service

# Restore original camera service
sudo systemctl enable d3kos-camera-stream.service
sudo systemctl start d3kos-camera-stream.service
```

### Rollback Step 3: Remove Tier API from Nginx

```bash
# Edit nginx config and remove /tier/ location block
sudo nano /etc/nginx/sites-enabled/default

# Test and reload
sudo nginx -t
sudo systemctl reload nginx
```

### Rollback Step 4: Reboot

```bash
sudo reboot
```

---

## FILES CREATED (SUMMARY)

**Scripts:**
- `/opt/d3kos/scripts/detect-opencpn.sh` (OpenCPN detection)
- `/opt/d3kos/scripts/tier-manager.sh` (Tier management logic)

**Services:**
- `/opt/d3kos/services/tier/tier-api.py` (Tier API server, port 8091)

**Systemd Units:**
- `/etc/systemd/system/d3kos-tier-manager.service` (Boot-time tier detection)
- `/etc/systemd/system/d3kos-tier-api.service` (Tier API service)

**Modified:**
- `/etc/systemd/system/d3kos-voice.service` (Conditional start)
- `/etc/systemd/system/d3kos-camera-stream.service` (Conditional start)
- `/etc/systemd/system/d3kos-fish-detector.service` (Conditional start)
- `/var/www/html/onboarding.html` (Reset counter display + increment)
- `/var/www/html/settings.html` (Tier display section)
- `/var/www/html/index.html` (Feature restriction logic)
- `/var/www/html/marine-vision.html` (Tier check)
- `/etc/nginx/sites-enabled/default` (Tier API proxy)

---

## TIME ESTIMATE BREAKDOWN

| Phase | Task | Time |
|-------|------|------|
| **Phase 1** | OpenCPN detection script | 30 min |
| | Tier manager script | 1 hour |
| | Tier manager service | 20 min |
| | Tier API service | 1 hour |
| | Nginx proxy | 15 min |
| | Testing Phase 1 | 30 min |
| **Phase 2** | Voice service conditional start | 30 min |
| | Camera service conditional start | 30 min |
| | Fish detector service | 15 min |
| | Testing Phase 2 | 30 min |
| **Phase 3** | Onboarding wizard updates | 1 hour |
| | Settings page updates | 1 hour |
| | Main menu updates | 30 min |
| | Marine vision page | 30 min |
| **Phase 4** | Comprehensive testing | 1.5 hours |
| **Total** | | **8-12 hours** |

---

## DEPENDENCIES

**Required Before Starting:**
- ✅ Task #1 (Installation ID) complete
- ✅ Python 3 with Flask installed
- ✅ jq installed (`sudo apt-get install jq`)
- ✅ curl installed
- ✅ systemd available

**Services That Must Be Working:**
- ✅ d3kos-license-api.service (from Task #1)
- ✅ nginx web server
- ✅ d3kos-voice.service (to modify)
- ✅ d3kos-camera-stream.service (to modify)

---

## NEXT STEPS AFTER COMPLETION

Once Task #2 is complete:

1. **Update MEMORY.md** with implementation details
2. **Test all tier transitions** (0→2, 2→3)
3. **Begin Task #3** (Data Export & Central Database Sync)
4. **Document tier system** in user guide
5. **Update MASTER_SYSTEM_SPEC.md** with implementation notes

---

## NOTES FOR NEXT SESSION

**Session Coordination:**
- Register in `.session-status.md` before starting
- Check `.domain-ownership.md` for file conflicts
- Domain: Core System Configuration (Domain 6)
- Cannot run parallel with Task #1

**Testing Checklist:**
- [ ] Tier 0 restrictions working
- [ ] OpenCPN auto-upgrade working
- [ ] Reset counter working
- [ ] Services conditional start working
- [ ] UI updates working
- [ ] Reboot persistence working
- [ ] All API endpoints working

**Known Limitations:**
- Downgrade from Tier 2→0 requires manual intervention (intentional design)
- Paid tier detection requires Task #3 (E-commerce) to be implemented
- Cloud sync (Tier 3) requires backend infrastructure

---

**END OF IMPLEMENTATION GUIDE - TASK #2**

**All preparation complete - ready to start implementation!**
