# Feature Spec: Cloud Integration Pre-Requisites (Pi Side)
# v0.9.2 — Required before atmyboat.com website build (v0.9.3)
# Spec source: ATMYBOAT_CLAUDE_CODE_SPEC.md PART 14

## Overview
Six changes to the Pi to make it cloud-ready for T1+ users.
T0 devices (offline) are completely unaffected — all cloud features are no-op when cloud-credentials.json is absent.

---

## PHASE 1: QR Code URL Update (onboarding.html)

File: /var/www/html/onboarding.html

The generateQR() function currently sets qrData to just the installation ID string.
It must be changed to encode a full atmyboat.com registration URL:

  https://atmyboat.com/register?device=[INSTALLATION_ID]&tier=t0&version=[FIRMWARE_VERSION]

The firmware version should be fetched from /api/version or fallback to 'unknown'.
The QR code text must be the full URL, not just the ID.
The displayed "Installation ID" text below the QR stays the same (still shows just the ID).

---

## PHASE 2: New Flask Service — cloud-link-api.py (Port 8091)

New file: /opt/d3kos/services/cloud/cloud-link-api.py

This service handles the registration handshake between the Pi and atmyboat.com.

Endpoints:

POST /api/link
  - Receives JSON: {boat_uuid, device_api_key, supabase_url, supabase_anon_key, webhook_url, tier}
  - Validates all required fields are present
  - Writes to /opt/d3kos/config/cloud-credentials.json with mode 0o600
  - Returns {"success": true, "tier": tier}
  - Returns {"success": false, "error": "..."} on failure

GET /api/status
  - Reads cloud-credentials.json if it exists
  - Returns {linked: true/false, tier: "t0"/"t1"/"t2"/"t3", firmware_version, uptime_seconds, last_push}
  - last_push: read from /opt/d3kos/data/telemetry-last-push.txt if it exists, else null
  - If not linked (no cloud-credentials.json): returns {linked: false, tier: "t0"}

Service details:
  - Flask app on host 0.0.0.0 port 8091
  - CORS enabled
  - Systemd service name: d3kos-cloud-link
  - Nginx proxy: /cloud/ -> localhost:8091 (strip prefix)
  - Use python3-flask (already installed on Pi)
  - Import: flask, json, os, time, subprocess

---

## PHASE 3: Force Password Change in Onboarding Wizard (onboarding.html)

File: /var/www/html/onboarding.html

Add a password change check as the FIRST step (step0) before the current step1.
This step only appears if the Pi password is still the default 'pi'.

Detection: fetch GET /network/check-default-password
  - This endpoint does not exist yet — the phase creates it in network-api.py

If password is default:
  - Show a warning step: "Security Required: Change your default password"
  - Input field: new password (min 8 chars)
  - Input field: confirm password
  - Submit button calls POST /network/change-password with {new_password}
  - On success: mark password_changed=true in onboarding.json via POST /api/language (reuse existing endpoint pattern) — actually POST to /network/save-onboarding with {password_changed: true}
  - Advance to step1

If password is NOT default:
  - Skip step0 entirely, go straight to step1

Network API additions (network-api.py, port 8101):

GET /network/check-default-password
  - Run: subprocess check if current d3kos user password matches 'pi' using PAM or shadow check
  - Simpler approach: check if /opt/d3kos/config/onboarding.json has password_changed=true
  - If password_changed is true in onboarding.json: return {default: false}
  - If missing or false: return {default: true}

POST /network/change-password
  - Receives {new_password}
  - Validates: min 8 chars, not 'pi', not empty
  - Runs: echo "d3kos:NEW_PASSWORD" | sudo chpasswd
  - Updates onboarding.json: set password_changed=true
  - Returns {success: true} or {success: false, error: "..."}
  - Requires sudoers entry: d3kos ALL=(ALL) NOPASSWD: /usr/sbin/chpasswd

---

## PHASE 4: Node-RED Telemetry Push Flow (JSON export)

New file: /opt/d3kos/nodered-flows/cloud-telemetry-push.json

This is a Node-RED flow exported as JSON. It will be imported into Node-RED manually.

Flow logic:
  1. Inject node: triggers every 60 seconds
  2. Function node "check-credentials": reads /opt/d3kos/config/cloud-credentials.json
     - If file missing: set msg.skip = true
     - If file exists: parse and set msg.credentials
  3. Switch node: if msg.skip == true, stop
  4. Function node "build-telemetry": fetch current engine/nav data from Signal K
     - GET http://localhost:3000/signalk/v1/api/vessels/self
     - Build payload: {device_api_key, boat_uuid, timestamp, readings: {rpm, coolant_temp, fuel_level, battery_volts, gps_lat, gps_lon, speed_knots, firmware_version}}
     - firmware_version: read from /opt/d3kos/config/version.txt
  5. HTTP request node: POST https://atmyboat.com/api/telemetry/push
     - Header: Authorization: Bearer [device_api_key from credentials]
     - Content-Type: application/json
  6. Function node "log-push": write timestamp to /opt/d3kos/data/telemetry-last-push.txt
  7. Catch node: on error, write to /opt/d3kos/data/telemetry-buffer.db (SQLite append)

Note: Generate valid Node-RED flow JSON with proper UUIDs for all node ids.

---

## PHASE 5: Force Password — sudoers Entry

New file content to append to /etc/sudoers.d/d3kos-chpasswd:

  d3kos ALL=(ALL) NOPASSWD: /usr/sbin/chpasswd

This allows the network-api.py service (running as d3kos) to change the system password
without requiring a sudo password prompt.

This is a CREATE phase — generate the file content only.
Claude will deploy this manually via SSH since it requires root.
