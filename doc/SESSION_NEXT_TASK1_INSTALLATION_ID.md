# Session Guide: Task #1 - Installation ID System Implementation

**Date Prepared:** 2026-02-16
**Task:** Implement proper installation ID system per spec
**Estimated Time:** 4-6 hours
**Priority:** Medium (Foundation for Tier system)

---

## Current State (WRONG)

**Problems:**
1. ✗ Installation ID stored in browser localStorage (lost if cache cleared)
2. ✗ Wrong format: `XXXX-XXXX-XXXX` (12-char random)
3. ✗ Generated during onboarding wizard (Step 18)
4. ✗ Not persistent across system reinstalls
5. ✗ No license.json file exists

**Location:** `/var/www/html/onboarding.html` Line ~580
```javascript
// WRONG IMPLEMENTATION
function generateInstallationId() {
  let id = localStorage.getItem('d3kos-installation-id');
  if (!id) {
    id = Math.random().toString(36).substring(2, 6).toUpperCase() + '-' +
         Math.random().toString(36).substring(2, 6).toUpperCase() + '-' +
         Math.random().toString(36).substring(2, 6).toUpperCase();
    localStorage.setItem('d3kos-installation-id', id);
  }
  return id;
}
```

---

## Specification Requirements

**Source:** MASTER_SYSTEM_SPEC.md Section 6.3.1, CLAUDE.md Licensing System

**Installation ID:**
- Format: 16-character hex string (e.g., `550e8400e29b41d4`)
- Algorithm: SHA-256(MAC address + timestamp)
- Storage: `/opt/d3kos/config/license.json`
- Generated: First boot (BEFORE onboarding wizard runs)
- Persistence: Survives browser cache clears, SD card reflashes (Tier 1+ with mobile app restore)

**license.json Structure:**
```json
{
  "installation_id": "550e8400e29b41d4",
  "tier": 0,
  "reset_count": 0,
  "max_resets": 10,
  "version": "1.0.3",
  "last_update_check": "2026-02-16T10:00:00Z",
  "features": {
    "voice_assistant": false,
    "camera": false,
    "unlimited_resets": false,
    "cloud_sync": false
  },
  "subscription_status": "none",
  "subscription_expires_at": null
}
```

**QR Code Format (CLAUDE.md):**
```json
{
  "installation_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "pairing_token": "TOKEN_1_TIME_USE",
  "api_endpoint": "https://d3kos-cloud/api/v1",
  "current_tier": 0
}
```

---

## Implementation Plan

### Phase 1: Create Installation ID Generator Script

**File:** `/opt/d3kos/scripts/generate-installation-id.sh`

```bash
#!/bin/bash
# Generate installation ID from MAC address + timestamp

LICENSE_FILE="/opt/d3kos/config/license.json"

# Exit if license.json already exists (don't regenerate)
if [ -f "$LICENSE_FILE" ]; then
  echo "License file already exists: $LICENSE_FILE"
  exit 0
fi

# Get primary network interface MAC address
MAC_ADDRESS=$(ip link show | awk '/ether/ {print $2; exit}')

if [ -z "$MAC_ADDRESS" ]; then
  echo "ERROR: Could not detect MAC address"
  exit 1
fi

# Get current timestamp
TIMESTAMP=$(date +%s)

# Combine MAC + timestamp
SEED="${MAC_ADDRESS}-${TIMESTAMP}"

# Generate SHA-256 hash and take first 16 hex characters
INSTALLATION_ID=$(echo -n "$SEED" | sha256sum | awk '{print substr($1, 1, 16)}')

echo "Generated installation_id: $INSTALLATION_ID"

# Create /opt/d3kos/config directory if it doesn't exist
mkdir -p /opt/d3kos/config

# Create license.json with default values
cat > "$LICENSE_FILE" <<EOF
{
  "installation_id": "$INSTALLATION_ID",
  "tier": 0,
  "reset_count": 0,
  "max_resets": 10,
  "version": "1.0.3",
  "last_update_check": "$(date -Iseconds)",
  "features": {
    "voice_assistant": false,
    "camera": false,
    "unlimited_resets": false,
    "cloud_sync": false
  },
  "subscription_status": "none",
  "subscription_expires_at": null
}
EOF

# Set proper permissions
chown d3kos:d3kos "$LICENSE_FILE"
chmod 644 "$LICENSE_FILE"

echo "License file created: $LICENSE_FILE"
```

**Permissions:**
```bash
chmod +x /opt/d3kos/scripts/generate-installation-id.sh
chown root:root /opt/d3kos/scripts/generate-installation-id.sh
```

---

### Phase 2: Create First-Boot Systemd Service

**File:** `/etc/systemd/system/d3kos-first-boot.service`

```ini
[Unit]
Description=d3kOS First Boot Initialization
After=network.target
Before=nginx.service

[Service]
Type=oneshot
ExecStart=/opt/d3kos/scripts/generate-installation-id.sh
RemainAfterExit=yes
User=root

[Install]
WantedBy=multi-user.target
```

**Enable the service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable d3kos-first-boot.service
```

**Service runs once:** Creates license.json on first boot, then exits (doesn't regenerate if file exists)

---

### Phase 3: Create License API Endpoint

**File:** `/opt/d3kos/services/license/license-api.py`

```python
#!/usr/bin/env python3
"""
d3kOS License API
Port: 8090
Endpoints:
  GET /license/info - Get installation_id and tier info
  GET /license/full - Get complete license.json (admin only)
"""

from flask import Flask, jsonify
import json
import os

app = Flask(__name__)

LICENSE_FILE = "/opt/d3kos/config/license.json"

def read_license():
    """Read license.json file"""
    if not os.path.exists(LICENSE_FILE):
        return None

    try:
        with open(LICENSE_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading license file: {e}")
        return None

@app.route('/license/info', methods=['GET'])
def get_license_info():
    """Get basic license info (installation_id, tier, features)"""
    license_data = read_license()

    if not license_data:
        return jsonify({
            "error": "License file not found",
            "installation_id": None,
            "tier": 0
        }), 404

    return jsonify({
        "installation_id": license_data.get("installation_id"),
        "tier": license_data.get("tier", 0),
        "version": license_data.get("version"),
        "features": license_data.get("features", {}),
        "subscription_status": license_data.get("subscription_status", "none")
    })

@app.route('/license/full', methods=['GET'])
def get_full_license():
    """Get complete license.json (includes reset_count, etc.)"""
    license_data = read_license()

    if not license_data:
        return jsonify({"error": "License file not found"}), 404

    return jsonify(license_data)

if __name__ == '__main__':
    # Run on port 8090, accessible from localhost only
    app.run(host='127.0.0.1', port=8090, debug=False)
```

**Service File:** `/etc/systemd/system/d3kos-license-api.service`

```ini
[Unit]
Description=d3kOS License API
After=network.target d3kos-first-boot.service

[Service]
Type=simple
User=d3kos
WorkingDirectory=/opt/d3kos/services/license
ExecStart=/usr/bin/python3 /opt/d3kos/services/license/license-api.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Nginx Proxy:** Add to `/etc/nginx/sites-enabled/default`

```nginx
# License API
location /license/ {
    proxy_pass http://127.0.0.1:8090/license/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

**Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable d3kos-license-api.service
sudo systemctl start d3kos-license-api.service
sudo systemctl reload nginx
```

---

### Phase 4: Update Onboarding Wizard (Step 18 QR Code)

**File:** `/var/www/html/onboarding.html`

**REMOVE old function** (around line 580):
```javascript
// DELETE THIS ENTIRE FUNCTION
function generateInstallationId() {
  let id = localStorage.getItem('d3kos-installation-id');
  if (!id) {
    id = Math.random().toString(36).substring(2, 6).toUpperCase() + '-' +
         Math.random().toString(36).substring(2, 6).toUpperCase() + '-' +
         Math.random().toString(36).substring(2, 6).toUpperCase();
    localStorage.setItem('d3kos-installation-id', id);
  }
  return id;
}
```

**ADD new function** (fetch from license API):
```javascript
async function getInstallationId() {
  try {
    const response = await fetch('/license/info');
    const data = await response.json();

    if (data.installation_id) {
      return data.installation_id;
    } else {
      console.error('Installation ID not found in license');
      return 'ERROR-NO-ID';
    }
  } catch (error) {
    console.error('Failed to fetch installation ID:', error);
    return 'ERROR-FETCH-FAILED';
  }
}
```

**UPDATE Step 18 (QR code generation)** (around line 870):
```javascript
async function generateQRCode() {
  const qrDiv = document.getElementById('qr-code');
  qrDiv.innerHTML = ''; // Clear previous QR code

  // Fetch installation_id from license API
  const installationId = await getInstallationId();

  // Generate UUID format: 550e8400-e29b-41d4-a716-446655440000
  // First 8 chars: installation_id (hex)
  // Next 4: e29b (random)
  // Next 4: 41d4 (random with version 4 UUID)
  // Next 4: a716 (random)
  // Last 12: 446655440000 (random)

  const uuid = installationId.substring(0, 8) + '-' +
               Math.random().toString(16).substring(2, 6) + '-' +
               '41d4-' + // Version 4 UUID
               Math.random().toString(16).substring(2, 6) + '-' +
               Math.random().toString(16).substring(2, 14);

  // Generate one-time pairing token
  const pairingToken = 'PAIR-' + Math.random().toString(36).substring(2, 15).toUpperCase();

  // QR code data per CLAUDE.md spec
  const qrData = {
    installation_uuid: uuid,
    pairing_token: pairingToken,
    api_endpoint: "https://d3kos-cloud/api/v1",
    current_tier: 0
  };

  // Generate QR code with 300x300px, high error correction
  new QRCode(qrDiv, {
    text: JSON.stringify(qrData),
    width: 300,
    height: 300,
    colorDark: '#000000',
    colorLight: '#ffffff',
    correctLevel: QRCode.CorrectLevel.H
  });

  // Display installation_id below QR code
  document.getElementById('installation-id-display').textContent =
    'Installation ID: ' + installationId;
}
```

**UPDATE HTML in Step 18** (around line 980):
```html
<div id="step18" class="wizard-step" style="display: none;">
  <h2>Step 18: QR Code</h2>
  <p style="font-size: 18px;">Scan this QR code with the d3kOS mobile app to pair your device:</p>

  <div id="qr-code" style="margin: 20px auto; width: 300px;"></div>

  <p id="installation-id-display" style="font-size: 16px; color: #00CC00; margin-top: 10px;">
    Loading installation ID...
  </p>

  <p style="font-size: 16px; margin-top: 20px;">
    This QR code contains your unique installation UUID and one-time pairing token.
  </p>

  <button onclick="previousStep()" style="font-size: 22px; margin-right: 20px;">← Previous</button>
  <button onclick="nextStep()" style="font-size: 22px;">Next →</button>
</div>
```

**REMOVE localStorage cleanup:**
Find and remove any `localStorage.removeItem('d3kos-installation-id')` calls in the wizard.

---

### Phase 5: Testing Procedures

#### Test 1: First Boot Generation
```bash
# Remove license file (if exists)
sudo rm -f /opt/d3kos/config/license.json

# Run first-boot script manually
sudo /opt/d3kos/scripts/generate-installation-id.sh

# Verify license.json created
cat /opt/d3kos/config/license.json

# Expected output:
# {
#   "installation_id": "550e8400e29b41d4",  (16-char hex)
#   "tier": 0,
#   ...
# }
```

#### Test 2: License API
```bash
# Test info endpoint
curl http://localhost/license/info

# Expected output:
# {
#   "installation_id": "550e8400e29b41d4",
#   "tier": 0,
#   "version": "1.0.3",
#   "features": {...},
#   "subscription_status": "none"
# }

# Test full license endpoint
curl http://localhost/license/full

# Should return complete license.json
```

#### Test 3: Onboarding Wizard QR Code
1. Open browser: `http://192.168.1.237/onboarding.html`
2. Complete Steps 0-17
3. On Step 18:
   - QR code should appear (300x300px)
   - Installation ID should display below QR code
   - Format: "Installation ID: 550e8400e29b41d4" (16-char hex)
4. Scan QR code with phone:
   - Should decode to JSON with `installation_uuid` (UUID format)
   - Should include `pairing_token` (one-time use)
   - Should include `api_endpoint` and `current_tier`

#### Test 4: Persistence
```bash
# Clear browser cache
# Ctrl+Shift+Delete → Clear all browsing data

# Revisit onboarding Step 18
# Installation ID should be SAME as before (not regenerated)

# Verify localStorage is NOT used
# Open browser console:
localStorage.getItem('d3kos-installation-id')
# Should return: null (not used anymore)
```

#### Test 5: Script Idempotency
```bash
# Run script multiple times
sudo /opt/d3kos/scripts/generate-installation-id.sh
sudo /opt/d3kos/scripts/generate-installation-id.sh
sudo /opt/d3kos/scripts/generate-installation-id.sh

# Verify installation_id doesn't change
cat /opt/d3kos/config/license.json

# Script should exit with "License file already exists" message
```

---

## Files to Create

1. **`/opt/d3kos/scripts/generate-installation-id.sh`** (220 lines)
   - Installation ID generator
   - MAC + timestamp → SHA-256 → 16-char hex
   - Creates license.json with default values

2. **`/etc/systemd/system/d3kos-first-boot.service`** (12 lines)
   - Runs installation ID script on first boot
   - Oneshot service (runs once, then exits)

3. **`/opt/d3kos/services/license/license-api.py`** (80 lines)
   - Flask API for license info
   - Port 8090, localhost only
   - Endpoints: `/license/info`, `/license/full`

4. **`/etc/systemd/system/d3kos-license-api.service`** (15 lines)
   - License API systemd service
   - Auto-start enabled

5. **`/opt/d3kos/config/license.json`** (Generated by script)
   - Installation ID
   - Tier, reset counter, features
   - Subscription status

---

## Files to Modify

1. **`/var/www/html/onboarding.html`**
   - Remove `generateInstallationId()` function (old localStorage version)
   - Add `getInstallationId()` function (fetch from license API)
   - Update `generateQRCode()` to use UUID format + pairing token
   - Update Step 18 HTML to display installation_id
   - Remove all localStorage cleanup code

2. **`/etc/nginx/sites-enabled/default`**
   - Add proxy for `/license/` → `localhost:8090/license/`

---

## Success Criteria

✅ **Installation ID generated on first boot** (before onboarding runs)
✅ **16-character hex format** (e.g., `550e8400e29b41d4`)
✅ **Stored in `/opt/d3kos/config/license.json`**
✅ **Survives browser cache clears** (not in localStorage)
✅ **License API accessible** at `http://localhost/license/info`
✅ **QR code uses UUID format** with pairing token
✅ **Onboarding wizard displays installation_id** below QR code
✅ **Script is idempotent** (doesn't regenerate if license.json exists)

---

## Rollback Plan

If something goes wrong:

```bash
# Stop services
sudo systemctl stop d3kos-license-api.service
sudo systemctl disable d3kos-license-api.service

# Remove files
sudo rm /opt/d3kos/scripts/generate-installation-id.sh
sudo rm /etc/systemd/system/d3kos-first-boot.service
sudo rm /etc/systemd/system/d3kos-license-api.service
sudo rm -rf /opt/d3kos/services/license
sudo rm /opt/d3kos/config/license.json

# Restore onboarding.html from backup
sudo cp /var/www/html/onboarding.html.bak /var/www/html/onboarding.html

# Reload services
sudo systemctl daemon-reload
sudo systemctl reload nginx
```

---

## Estimated Time Breakdown

1. **Phase 1:** Create installation ID script - 45 minutes
2. **Phase 2:** Create first-boot service - 20 minutes
3. **Phase 3:** Create license API - 1 hour
4. **Phase 4:** Update onboarding wizard - 1 hour
5. **Phase 5:** Testing and verification - 1.5 hours

**Total:** 4-6 hours

---

## Dependencies

**Python Packages:**
```bash
sudo apt-get install python3-flask
```

**Already Installed:**
- QRCode.js library (already in onboarding.html)
- nginx (already configured)
- systemd

---

## Next Steps After Task #1

Once Installation ID system is complete:
1. ✅ Move to **Task #2** - Implement license/tier system
2. ✅ Add tier detection logic (OpenCPN = Tier 2)
3. ✅ Add feature restrictions (voice/camera disabled in Tier 0)
4. ✅ Add reset counter tracking
5. ✅ Move to **Task #3** - Data export & e-commerce

---

## Notes

- **DO NOT push to GitHub** until testing is complete
- Create `.bak` backups before modifying existing files
- Test on actual Raspberry Pi (not just development machine)
- Verify installation_id is truly unique (check with multiple systems)
- Document any deviations from this plan

---

**Ready to implement!**
