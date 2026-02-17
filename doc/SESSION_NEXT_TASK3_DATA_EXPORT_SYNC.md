# Session C: Data Export & Central Database Sync Implementation Guide

**Task ID:** Task #3 - Implement data export & central database sync system
**Date Prepared:** 2026-02-17
**Estimated Time:** 12-16 hours
**Status:** ✅ Fully planned and ready to implement
**Dependencies:** Tasks #1 (Installation ID) AND #2 (Tier System) MUST be completed first

---

## CRITICAL: Prerequisites

**BEFORE STARTING THIS TASK:**

1. ✅ Task #1 (Installation ID) MUST be complete
2. ✅ Task #2 (Tier System) MUST be complete
3. ✅ File `/opt/d3kos/config/license.json` MUST exist with `installation_id`
4. ✅ Tier API at `http://localhost/tier/status` MUST be working
5. ✅ Tier detection working (Tier 0 vs Tier 1+ distinction)

**Verify Prerequisites:**
```bash
# Check license.json exists with installation_id
cat /opt/d3kos/config/license.json | jq '.installation_id, .tier'

# Check tier API is working
curl http://localhost/tier/status | jq

# Verify installation_id format (16 hex chars)
cat /opt/d3kos/config/license.json | jq -r '.installation_id' | wc -c
# Expected: 17 (16 chars + newline)
```

**Expected Output:**
```json
{
  "installation_id": "550e8400e29b41d4",
  "tier": 0  // or 1, 2, 3
}
```

If any of these checks fail, **STOP** and complete Tasks #1 and #2 first.

---

## CURRENT PROBLEM

**What's Wrong:**
- No export functionality exists
- Boatlog export button crashes (known issue)
- No data sync to central database
- No export queue system
- No automatic boot-time upload
- Marine vision media files never transferred

**Spec Requirements (MASTER_SYSTEM_SPEC.md Section 8.3, CLAUDE.md v3.0):**

**Tier Requirement:** Tier 1, 2, and 3 ONLY (Tier 0 has NO export capability)

**Export Categories (9 types):**
1. Engine benchmark data
2. Boatlog entries (voice, text, auto, weather)
3. Marine vision captures (METADATA ONLY - no image files)
4. Marine vision snapshots (METADATA ONLY - no video files)
5. QR code data
6. Settings configuration
7. System alerts
8. Onboarding/Initial Setup Configuration (wizard answers, reset counter)
9. Telemetry & Analytics (system performance, user interaction, AI metrics)

**CRITICAL:** Marine vision media files (photos/videos) are NOT exported to central database. Only metadata sent.

**Export Format:** JSON with installation_id, timestamp, tier, format_version

**Export Triggers:**
1. Manual: Settings → Data Management → Export All Data Now
2. Automatic: On boot, check queue and upload pending exports
3. Scheduled: Daily 3:00 AM (Tier 2+ only, incremental)

---

## IMPLEMENTATION OVERVIEW

### Phase Breakdown

**Phase 1: Export Manager Service** (4-6 hours)
- Export collector functions (9 categories)
- JSON formatting with installation_id
- Queue management

**Phase 2: Export Queue System** (2-3 hours)
- Retry logic (3 attempts)
- Archive successful exports
- Auto-cleanup failed exports

**Phase 3: Boot-Time Upload Service** (1-2 hours)
- Systemd service for boot upload
- Queue processor
- Internet connectivity check

**Phase 4: Data Management UI** (2-3 hours)
- Settings → Data Management page
- Manual export button
- Queue status display
- Tier 0 restrictions

**Phase 5: Media Cleanup System** (2-3 hours)
- 7-day automatic deletion
- Storage threshold cleanup (>90%)
- User notifications
- Critical alerts (>95%)

**Phase 6: Testing & Integration** (1-2 hours)
- Test all 9 export categories
- Test queue retry logic
- Test boot-time upload
- Test media cleanup

---

## PHASE 1: EXPORT MANAGER SERVICE (4-6 HOURS)

### Step 1.1: Create Export Manager Service

**File:** `/opt/d3kos/services/export/export-manager.js`

```javascript
#!/usr/bin/env node
/**
 * d3kOS Export Manager Service
 * Collects and exports boat data to central database
 * Port: 8092
 */

const express = require('express');
const fs = require('fs').promises;
const path = require('path');
const { exec } = require('child_process');
const { promisify } = require('util');
const sqlite3 = require('sqlite3').verbose();

const execAsync = promisify(exec);
const app = express();
const PORT = 8092;

// Configuration
const LICENSE_FILE = '/opt/d3kos/config/license.json';
const EXPORT_DIR = '/opt/d3kos/data/exports';
const QUEUE_FILE = path.join(EXPORT_DIR, 'export_queue.json');
const HISTORY_FILE = path.join(EXPORT_DIR, 'export_history.json');
const CENTRAL_API = process.env.CENTRAL_API_URL || 'https://d3kos-cloud/api/v1';

// Database paths
const BOATLOG_DB = '/opt/d3kos/data/boatlog.db';
const CAPTURES_DB = '/opt/d3kos/data/marine-vision/captures.db';
const TELEMETRY_DB = '/opt/d3kos/data/telemetry.db';
const CONVERSATION_DB = '/opt/d3kos/data/conversation-history.db';

app.use(express.json());

// Logging
function log(message) {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] ${message}`);
}

// Load license info (installation_id, tier)
async function loadLicense() {
    try {
        const data = await fs.readFile(LICENSE_FILE, 'utf8');
        return JSON.parse(data);
    } catch (error) {
        log(`Error loading license: ${error.message}`);
        return null;
    }
}

// Check if tier allows export (Tier 1+)
async function checkExportPermission() {
    const license = await loadLicense();
    if (!license) return false;

    const tier = license.tier || 0;
    if (tier === 0) {
        log('Export blocked: Tier 0 does not have export capability');
        return false;
    }

    return true;
}

// ============================================
// EXPORT COLLECTORS (9 CATEGORIES)
// ============================================

// Category 1: Engine Benchmark Data
async function collectEngineBenchmark() {
    try {
        const benchmarkFile = '/opt/d3kos/data/engine-benchmark.json';
        const data = await fs.readFile(benchmarkFile, 'utf8');
        return JSON.parse(data);
    } catch (error) {
        log(`No benchmark data: ${error.message}`);
        return null;
    }
}

// Category 2: Boatlog Entries
async function collectBoatlogEntries() {
    return new Promise((resolve, reject) => {
        const db = new sqlite3.Database(BOATLOG_DB, sqlite3.OPEN_READONLY, (err) => {
            if (err) {
                log(`Cannot open boatlog database: ${err.message}`);
                resolve(null);
                return;
            }
        });

        db.all(`
            SELECT * FROM boatlog_entries
            WHERE exported = 0
            ORDER BY timestamp DESC
        `, [], (err, rows) => {
            db.close();

            if (err) {
                log(`Error reading boatlog: ${err.message}`);
                resolve(null);
            } else {
                resolve(rows);
            }
        });
    });
}

// Category 3: Marine Vision Captures (METADATA ONLY)
async function collectMarineVisionMetadata() {
    return new Promise((resolve, reject) => {
        const db = new sqlite3.Database(CAPTURES_DB, sqlite3.OPEN_READONLY, (err) => {
            if (err) {
                log(`Cannot open captures database: ${err.message}`);
                resolve(null);
                return;
            }
        });

        db.all(`
            SELECT
                id,
                timestamp,
                species,
                confidence,
                latitude,
                longitude,
                file_size,
                exported
            FROM captures
            WHERE exported = 0
            ORDER BY timestamp DESC
        `, [], (err, rows) => {
            db.close();

            if (err) {
                log(`Error reading captures: ${err.message}`);
                resolve(null);
            } else {
                // Remove file paths - only metadata
                const metadata = rows.map(row => ({
                    ...row,
                    note: 'Media file transferred via mobile app, not central database'
                }));
                resolve(metadata);
            }
        });
    });
}

// Category 4: Marine Vision Snapshots (METADATA ONLY)
async function collectMarineVisionSnapshots() {
    try {
        const snapshotsDir = '/home/d3kos/camera-recordings';
        const files = await fs.readdir(snapshotsDir);

        const snapshots = [];
        for (const file of files) {
            if (file.endsWith('.jpg') || file.endsWith('.mp4')) {
                const stats = await fs.stat(path.join(snapshotsDir, file));
                snapshots.push({
                    filename: file,
                    file_size: stats.size,
                    created_at: stats.birthtime.toISOString(),
                    type: file.endsWith('.mp4') ? 'video' : 'photo',
                    note: 'Media file stored locally, transferred via mobile app'
                });
            }
        }

        return snapshots;
    } catch (error) {
        log(`Error collecting snapshots metadata: ${error.message}`);
        return null;
    }
}

// Category 5: QR Code Data
async function collectQRCodeData() {
    try {
        const qrFile = '/opt/d3kos/data/qr-codes.json';
        const data = await fs.readFile(qrFile, 'utf8');
        return JSON.parse(data);
    } catch (error) {
        log(`No QR code data: ${error.message}`);
        return null;
    }
}

// Category 6: Settings Configuration
async function collectSettingsConfig() {
    try {
        const settingsFile = '/opt/d3kos/config/settings.json';
        const data = await fs.readFile(settingsFile, 'utf8');
        return JSON.parse(data);
    } catch (error) {
        log(`No settings config: ${error.message}`);
        return null;
    }
}

// Category 7: System Alerts
async function collectSystemAlerts() {
    try {
        const alertsFile = '/opt/d3kos/data/alerts.json';
        const data = await fs.readFile(alertsFile, 'utf8');
        return JSON.parse(data);
    } catch (error) {
        log(`No system alerts: ${error.message}`);
        return null;
    }
}

// Category 8: Onboarding/Initial Setup Configuration
async function collectOnboardingConfig() {
    try {
        const onboardingFile = '/opt/d3kos/config/onboarding.json';
        const resetCountFile = '/opt/d3kos/state/onboarding-reset-count.json';

        const onboardingData = await fs.readFile(onboardingFile, 'utf8');
        const resetData = await fs.readFile(resetCountFile, 'utf8');

        return {
            wizard_answers: JSON.parse(onboardingData),
            reset_info: JSON.parse(resetData),
            completed_at: new Date().toISOString()
        };
    } catch (error) {
        log(`No onboarding config: ${error.message}`);
        return null;
    }
}

// Category 9: Telemetry & Analytics
async function collectTelemetryData() {
    return new Promise((resolve, reject) => {
        const db = new sqlite3.Database(TELEMETRY_DB, sqlite3.OPEN_READONLY, (err) => {
            if (err) {
                log(`Cannot open telemetry database: ${err.message}`);
                resolve(null);
                return;
            }
        });

        db.all(`
            SELECT * FROM telemetry_events
            WHERE exported = 0
            ORDER BY timestamp DESC
            LIMIT 1000
        `, [], (err, rows) => {
            db.close();

            if (err) {
                log(`Error reading telemetry: ${err.message}`);
                resolve(null);
            } else {
                resolve(rows);
            }
        });
    });
}

// ============================================
// EXPORT GENERATION
// ============================================

async function generateExport() {
    log('Starting export generation...');

    // Check tier permission
    if (!await checkExportPermission()) {
        return {
            success: false,
            error: 'Export requires Tier 1 or higher'
        };
    }

    const license = await loadLicense();
    const exportId = `export_${Date.now()}`;

    // Collect all categories
    const exportData = {
        export_id: exportId,
        installation_id: license.installation_id,
        tier: license.tier,
        format_version: '1.0',
        timestamp: new Date().toISOString(),
        categories: {}
    };

    // Collect each category
    log('Collecting Category 1: Engine Benchmark...');
    exportData.categories.engine_benchmark = await collectEngineBenchmark();

    log('Collecting Category 2: Boatlog Entries...');
    exportData.categories.boatlog_entries = await collectBoatlogEntries();

    log('Collecting Category 3: Marine Vision Captures (Metadata)...');
    exportData.categories.marine_vision_captures = await collectMarineVisionMetadata();

    log('Collecting Category 4: Marine Vision Snapshots (Metadata)...');
    exportData.categories.marine_vision_snapshots = await collectMarineVisionSnapshots();

    log('Collecting Category 5: QR Code Data...');
    exportData.categories.qr_codes = await collectQRCodeData();

    log('Collecting Category 6: Settings Configuration...');
    exportData.categories.settings_config = await collectSettingsConfig();

    log('Collecting Category 7: System Alerts...');
    exportData.categories.system_alerts = await collectSystemAlerts();

    log('Collecting Category 8: Onboarding Configuration...');
    exportData.categories.onboarding_config = await collectOnboardingConfig();

    log('Collecting Category 9: Telemetry & Analytics...');
    exportData.categories.telemetry_data = await collectTelemetryData();

    // Calculate statistics
    const stats = {
        total_categories: 9,
        categories_with_data: 0,
        total_size_bytes: 0
    };

    for (const [category, data] of Object.entries(exportData.categories)) {
        if (data !== null) {
            stats.categories_with_data++;
        }
    }

    const exportJSON = JSON.stringify(exportData, null, 2);
    stats.total_size_bytes = Buffer.byteLength(exportJSON, 'utf8');

    exportData.statistics = stats;

    log(`Export generated: ${exportId}, ${stats.categories_with_data}/9 categories, ${Math.round(stats.total_size_bytes / 1024)} KB`);

    // Save export to file
    const exportFilePath = path.join(EXPORT_DIR, `${exportId}.json`);
    await fs.writeFile(exportFilePath, exportJSON);

    // Add to queue
    await addToQueue(exportId, exportFilePath);

    return {
        success: true,
        export_id: exportId,
        file_path: exportFilePath,
        statistics: stats
    };
}

// ============================================
// QUEUE MANAGEMENT
// ============================================

async function loadQueue() {
    try {
        const data = await fs.readFile(QUEUE_FILE, 'utf8');
        return JSON.parse(data);
    } catch (error) {
        // Queue file doesn't exist yet
        return { pending: [], failed: [] };
    }
}

async function saveQueue(queue) {
    await fs.writeFile(QUEUE_FILE, JSON.stringify(queue, null, 2));
}

async function addToQueue(exportId, filePath) {
    const queue = await loadQueue();

    queue.pending.push({
        export_id: exportId,
        file_path: filePath,
        created_at: new Date().toISOString(),
        attempts: 0,
        last_attempt: null,
        next_retry: new Date().toISOString() // Immediate
    });

    await saveQueue(queue);
    log(`Added ${exportId} to export queue`);
}

async function processQueue() {
    log('Processing export queue...');

    const queue = await loadQueue();
    const now = new Date();

    for (const item of queue.pending) {
        const nextRetry = new Date(item.next_retry);

        if (now >= nextRetry) {
            log(`Processing ${item.export_id} (attempt ${item.attempts + 1}/3)...`);

            const success = await uploadExport(item.file_path);

            if (success) {
                log(`✅ ${item.export_id} uploaded successfully`);

                // Move to history
                await archiveExport(item);

                // Remove from pending
                queue.pending = queue.pending.filter(i => i.export_id !== item.export_id);

                // Mark as exported in databases
                await markAsExported(item.export_id);
            } else {
                // Increment attempts
                item.attempts++;
                item.last_attempt = now.toISOString();

                if (item.attempts >= 3) {
                    log(`❌ ${item.export_id} failed after 3 attempts, moving to failed queue`);

                    queue.failed.push({
                        ...item,
                        failed_at: now.toISOString()
                    });

                    queue.pending = queue.pending.filter(i => i.export_id !== item.export_id);
                } else {
                    // Schedule next retry
                    const delays = [5 * 60 * 1000, 15 * 60 * 1000]; // 5 min, 15 min
                    const delay = delays[item.attempts - 1];
                    const nextRetryTime = new Date(now.getTime() + delay);
                    item.next_retry = nextRetryTime.toISOString();

                    log(`⏳ ${item.export_id} retry scheduled for ${nextRetryTime.toLocaleString()}`);
                }
            }
        }
    }

    await saveQueue(queue);
    log('Queue processing complete');
}

async function uploadExport(filePath) {
    try {
        // Read export file
        const exportData = await fs.readFile(filePath, 'utf8');
        const exportJSON = JSON.parse(exportData);

        // Check internet connectivity
        try {
            await execAsync('ping -c 1 -W 2 8.8.8.8');
        } catch (error) {
            log('No internet connection, skipping upload');
            return false;
        }

        // POST to central database API
        const fetch = require('node-fetch');
        const response = await fetch(`${CENTRAL_API}/data/import`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${exportJSON.installation_id}`
            },
            body: exportData,
            timeout: 30000 // 30 seconds
        });

        if (response.ok) {
            log(`Upload successful: ${response.status}`);
            return true;
        } else {
            log(`Upload failed: ${response.status} ${response.statusText}`);
            return false;
        }
    } catch (error) {
        log(`Upload error: ${error.message}`);
        return false;
    }
}

async function archiveExport(item) {
    // Load history
    let history = [];
    try {
        const data = await fs.readFile(HISTORY_FILE, 'utf8');
        history = JSON.parse(data);
    } catch (error) {
        // History file doesn't exist
    }

    history.push({
        ...item,
        archived_at: new Date().toISOString(),
        status: 'success'
    });

    // Keep only last 30 days
    const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
    history = history.filter(h => new Date(h.archived_at) > thirtyDaysAgo);

    await fs.writeFile(HISTORY_FILE, JSON.stringify(history, null, 2));
}

async function markAsExported(exportId) {
    // Mark boatlog entries as exported
    const boatlogDb = new sqlite3.Database(BOATLOG_DB);
    boatlogDb.run('UPDATE boatlog_entries SET exported = 1 WHERE exported = 0');
    boatlogDb.close();

    // Mark captures as exported
    const capturesDb = new sqlite3.Database(CAPTURES_DB);
    capturesDb.run('UPDATE captures SET exported = 1 WHERE exported = 0');
    capturesDb.close();

    // Mark telemetry as exported
    const telemetryDb = new sqlite3.Database(TELEMETRY_DB);
    telemetryDb.run('UPDATE telemetry_events SET exported = 1 WHERE exported = 0');
    telemetryDb.close();

    log('Marked records as exported in databases');
}

// Cleanup failed exports older than 7 days
async function cleanupFailedExports() {
    log('Cleaning up old failed exports...');

    const queue = await loadQueue();
    const sevenDaysAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);

    const before = queue.failed.length;
    queue.failed = queue.failed.filter(item => {
        const failedDate = new Date(item.failed_at);
        if (failedDate < sevenDaysAgo) {
            // Delete export file
            fs.unlink(item.file_path).catch(err => {
                log(`Error deleting ${item.file_path}: ${err.message}`);
            });
            return false;
        }
        return true;
    });

    const after = queue.failed.length;
    log(`Cleaned up ${before - after} old failed exports`);

    await saveQueue(queue);
}

// ============================================
// API ENDPOINTS
// ============================================

app.post('/export/generate', async (req, res) => {
    try {
        const result = await generateExport();
        res.json(result);
    } catch (error) {
        log(`Error generating export: ${error.message}`);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

app.post('/export/process-queue', async (req, res) => {
    try {
        await processQueue();
        res.json({ success: true, message: 'Queue processed' });
    } catch (error) {
        log(`Error processing queue: ${error.message}`);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

app.get('/export/queue/status', async (req, res) => {
    try {
        const queue = await loadQueue();
        res.json({
            success: true,
            pending: queue.pending.length,
            failed: queue.failed.length,
            items: queue
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

app.get('/export/history', async (req, res) => {
    try {
        const data = await fs.readFile(HISTORY_FILE, 'utf8');
        const history = JSON.parse(data);
        res.json({
            success: true,
            count: history.length,
            history: history
        });
    } catch (error) {
        res.json({
            success: true,
            count: 0,
            history: []
        });
    }
});

app.get('/health', (req, res) => {
    res.json({ status: 'ok', service: 'export-manager' });
});

// ============================================
// STARTUP
// ============================================

async function ensureDirectories() {
    await fs.mkdir(EXPORT_DIR, { recursive: true });
    log(`Export directory ready: ${EXPORT_DIR}`);
}

async function startup() {
    await ensureDirectories();

    // Run initial cleanup
    await cleanupFailedExports();

    // Start periodic queue processing (every 5 minutes)
    setInterval(async () => {
        await processQueue();
        await cleanupFailedExports();
    }, 5 * 60 * 1000);

    log(`d3kOS Export Manager started on port ${PORT}`);
    app.listen(PORT, '127.0.0.1');
}

startup();
```

**Install Dependencies:**
```bash
sudo apt-get update
sudo apt-get install -y nodejs npm sqlite3

cd /opt/d3kos/services/export
sudo npm install express sqlite3 node-fetch@2

sudo chown -R d3kos:d3kos /opt/d3kos/services/export
sudo chmod +x /opt/d3kos/services/export/export-manager.js
```

---

### Step 1.2: Create Export Manager Systemd Service

**File:** `/etc/systemd/system/d3kos-export-manager.service`

```ini
[Unit]
Description=d3kOS Export Manager Service
Documentation=https://github.com/boatiq/d3kos
After=network-online.target d3kos-tier-manager.service
Wants=network-online.target

[Service]
Type=simple
User=d3kos
WorkingDirectory=/opt/d3kos/services/export
ExecStart=/usr/bin/node /opt/d3kos/services/export/export-manager.js
Restart=always
RestartSec=10

# Environment
Environment="NODE_ENV=production"
Environment="CENTRAL_API_URL=https://d3kos-cloud/api/v1"

# Logging
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Enable and Test:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable d3kos-export-manager.service
sudo systemctl start d3kos-export-manager.service
systemctl status d3kos-export-manager.service

# Test API
curl http://localhost:8092/health | jq
```

---

### Step 1.3: Add Nginx Proxy for Export API

**File:** `/etc/nginx/sites-enabled/default`

**Add this location block:**

```nginx
    # Export Manager API (port 8092)
    location /export/ {
        proxy_pass http://127.0.0.1:8092/export/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Longer timeout for export generation
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
    }
```

**Reload Nginx:**
```bash
sudo nginx -t
sudo systemctl reload nginx

curl http://localhost/export/queue/status | jq
```

---

## PHASE 2: BOOT-TIME UPLOAD SERVICE (1-2 HOURS)

### Step 2.1: Create Boot Upload Script

**File:** `/opt/d3kos/scripts/boot-time-export.sh`

```bash
#!/bin/bash
# boot-time-export.sh - Process export queue on system boot
# Part of d3kOS Data Export System

set -e

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a /var/log/d3kos-boot-export.log
}

log "Boot-time export starting..."

# Wait for network (max 60 seconds)
for i in {1..60}; do
    if ping -c 1 -W 1 8.8.8.8 &> /dev/null; then
        log "Network ready"
        break
    fi
    sleep 1
done

# Wait for export manager service to be ready
for i in {1..30}; do
    if curl -s http://localhost:8092/health | grep -q "ok"; then
        log "Export manager service ready"
        break
    fi
    sleep 1
done

# Process queue
log "Processing export queue..."
response=$(curl -s -X POST http://localhost:8092/export/process-queue)
log "Queue processing response: $response"

log "Boot-time export complete"
```

**Set Permissions:**
```bash
sudo chmod +x /opt/d3kos/scripts/boot-time-export.sh
sudo chown d3kos:d3kos /opt/d3kos/scripts/boot-time-export.sh
```

---

### Step 2.2: Create Boot Upload Systemd Service

**File:** `/etc/systemd/system/d3kos-boot-export.service`

```ini
[Unit]
Description=d3kOS Boot-Time Export Service
Documentation=https://github.com/boatiq/d3kos
After=network-online.target d3kos-export-manager.service
Wants=network-online.target

[Service]
Type=oneshot
User=d3kos
ExecStart=/opt/d3kos/scripts/boot-time-export.sh
RemainAfterExit=no

# Logging
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Enable Service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable d3kos-boot-export.service

# Test (run manually)
sudo systemctl start d3kos-boot-export.service
journalctl -u d3kos-boot-export.service -n 30
```

---

## PHASE 3: DATA MANAGEMENT UI (2-3 HOURS)

### Step 3.1: Create Data Management Page

**File:** `/var/www/html/settings-data.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Management - d3kOS</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: Arial, sans-serif;
            background: #000;
            color: #FFF;
            font-size: 22px;
            padding: 20px;
        }

        .header {
            background: #1a1a1a;
            padding: 20px;
            margin-bottom: 20px;
            border-left: 4px solid #00CC00;
        }

        h1 {
            font-size: 36px;
            margin-bottom: 10px;
        }

        .section {
            background: #1a1a1a;
            padding: 20px;
            margin-bottom: 20px;
            border-left: 4px solid #00CC00;
        }

        .button {
            background: #00CC00;
            color: #000;
            border: none;
            padding: 20px 40px;
            font-size: 24px;
            cursor: pointer;
            margin: 10px 10px 10px 0;
            font-weight: bold;
        }

        .button:disabled {
            background: #333;
            color: #888;
            cursor: not-allowed;
        }

        .button.secondary {
            background: #333;
            color: #FFF;
            border: 2px solid #00CC00;
        }

        .status-text {
            font-size: 20px;
            padding: 15px;
            background: #000;
            margin: 10px 0;
            border: 1px solid #333;
        }

        .tier-warning {
            background: #331100;
            border: 2px solid #FF3333;
            padding: 20px;
            margin: 20px 0;
            color: #FF3333;
            font-size: 24px;
        }

        .success {
            color: #00CC00;
        }

        .error {
            color: #FF3333;
        }

        .warning {
            color: #FFA500;
        }

        .queue-item {
            background: #000;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #FFD700;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📦 Data Management</h1>
        <p>Export boat data to central database</p>
    </div>

    <!-- Tier Check -->
    <div id="tier-check" style="display: none;" class="tier-warning">
        <h2>⚠️ Export Not Available</h2>
        <p>Data export requires <strong>Tier 1</strong> or higher.</p>
        <p style="margin-top: 15px;">You are currently on <strong>Tier 0</strong>.</p>
        <button class="button" onclick="window.location.href='/settings.html'" style="margin-top: 20px;">
            View Upgrade Options
        </button>
    </div>

    <!-- Export Actions -->
    <div id="export-section">
        <div class="section">
            <h2>Manual Export</h2>
            <p style="margin: 15px 0;">Export all data categories now:</p>
            <button id="export-btn" class="button" onclick="generateExport()">
                📤 Export All Data Now
            </button>
            <div id="export-status" class="status-text" style="display: none;"></div>
        </div>

        <!-- Export Queue Status -->
        <div class="section">
            <h2>Export Queue</h2>
            <p style="margin: 15px 0;">Pending uploads to central database:</p>
            <div id="queue-status" class="status-text">
                Loading queue status...
            </div>
            <div id="queue-items"></div>
            <button class="button secondary" onclick="processQueue()">
                🔄 Process Queue Now
            </button>
        </div>

        <!-- Export History -->
        <div class="section">
            <h2>Export History</h2>
            <p style="margin: 15px 0;">Last 10 successful exports:</p>
            <div id="history-list" class="status-text">
                Loading history...
            </div>
        </div>

        <!-- Export Categories -->
        <div class="section">
            <h2>Export Categories</h2>
            <p style="margin: 15px 0;">Data included in exports:</p>
            <div style="font-size: 20px; line-height: 1.8;">
                <div>✅ Engine benchmark data</div>
                <div>✅ Boatlog entries (voice, text, auto, weather)</div>
                <div>✅ Marine vision captures (metadata only)</div>
                <div>✅ Marine vision snapshots (metadata only)</div>
                <div>✅ QR code data</div>
                <div>✅ Settings configuration</div>
                <div>✅ System alerts</div>
                <div>✅ Onboarding/Initial setup configuration</div>
                <div>✅ Telemetry & analytics</div>
            </div>
            <p style="margin-top: 20px; color: #FFD700;">
                <strong>Note:</strong> Media files (photos/videos) are NOT uploaded to central database.
                Transfer via Tier 1+ mobile app instead.
            </p>
        </div>
    </div>

    <!-- Navigation -->
    <div style="margin-top: 30px;">
        <button class="button secondary" onclick="window.location.href='/settings.html'">
            ← Back to Settings
        </button>
        <button class="button secondary" onclick="window.location.href='/'">
            ← Main Menu
        </button>
    </div>

    <script>
        // Check tier on page load
        async function checkTierAccess() {
            try {
                const response = await fetch('/tier/status');
                const data = await response.json();

                if (data.success && data.tier === 0) {
                    // Tier 0 - no export access
                    document.getElementById('tier-check').style.display = 'block';
                    document.getElementById('export-section').style.display = 'none';
                } else {
                    // Tier 1+ - export enabled
                    document.getElementById('tier-check').style.display = 'none';
                    document.getElementById('export-section').style.display = 'block';

                    // Load queue and history
                    loadQueueStatus();
                    loadHistory();
                }
            } catch (error) {
                console.error('Error checking tier:', error);
            }
        }

        // Generate export
        async function generateExport() {
            const btn = document.getElementById('export-btn');
            const status = document.getElementById('export-status');

            btn.disabled = true;
            btn.textContent = '⏳ Exporting...';
            status.style.display = 'block';
            status.innerHTML = '<span class="warning">Collecting data...</span>';

            try {
                const response = await fetch('/export/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });

                const data = await response.json();

                if (data.success) {
                    status.innerHTML = `
                        <span class="success">✅ Export created successfully!</span><br>
                        Export ID: ${data.export_id}<br>
                        Categories: ${data.statistics.categories_with_data}/9<br>
                        Size: ${Math.round(data.statistics.total_size_bytes / 1024)} KB<br>
                        <span class="warning">Added to upload queue...</span>
                    `;

                    // Refresh queue status
                    setTimeout(loadQueueStatus, 1000);
                } else {
                    status.innerHTML = `<span class="error">❌ Export failed: ${data.error}</span>`;
                }
            } catch (error) {
                status.innerHTML = `<span class="error">❌ Error: ${error.message}</span>`;
            } finally {
                btn.disabled = false;
                btn.textContent = '📤 Export All Data Now';
            }
        }

        // Load queue status
        async function loadQueueStatus() {
            try {
                const response = await fetch('/export/queue/status');
                const data = await response.json();

                if (data.success) {
                    const queueStatus = document.getElementById('queue-status');
                    queueStatus.innerHTML = `
                        <strong>Pending:</strong> ${data.pending} exports<br>
                        <strong>Failed:</strong> ${data.failed} exports
                    `;

                    // Display queue items
                    const queueItems = document.getElementById('queue-items');
                    queueItems.innerHTML = '';

                    if (data.items.pending.length > 0) {
                        data.items.pending.forEach(item => {
                            const div = document.createElement('div');
                            div.className = 'queue-item';
                            div.innerHTML = `
                                <strong>${item.export_id}</strong><br>
                                Attempts: ${item.attempts}/3<br>
                                Next retry: ${new Date(item.next_retry).toLocaleString()}
                            `;
                            queueItems.appendChild(div);
                        });
                    }
                }
            } catch (error) {
                console.error('Error loading queue:', error);
            }
        }

        // Process queue manually
        async function processQueue() {
            try {
                const response = await fetch('/export/process-queue', {
                    method: 'POST'
                });

                const data = await response.json();

                if (data.success) {
                    alert('✅ Queue processing started!\n\nCheck queue status in a few moments.');
                    setTimeout(loadQueueStatus, 5000);
                } else {
                    alert('❌ Failed to process queue');
                }
            } catch (error) {
                alert('❌ Error: ' + error.message);
            }
        }

        // Load export history
        async function loadHistory() {
            try {
                const response = await fetch('/export/history');
                const data = await response.json();

                const historyList = document.getElementById('history-list');

                if (data.success && data.count > 0) {
                    const recent = data.history.slice(-10).reverse();
                    historyList.innerHTML = recent.map(item => `
                        <div style="margin: 10px 0; padding: 10px; background: #000; border-left: 3px solid #00CC00;">
                            <strong>${item.export_id}</strong><br>
                            Archived: ${new Date(item.archived_at).toLocaleString()}<br>
                            Status: <span class="success">✅ Success</span>
                        </div>
                    `).join('');
                } else {
                    historyList.innerHTML = 'No export history yet';
                }
            } catch (error) {
                console.error('Error loading history:', error);
            }
        }

        // Auto-refresh queue status every 30 seconds
        setInterval(loadQueueStatus, 30000);

        // Check tier on load
        window.addEventListener('load', checkTierAccess);
    </script>
</body>
</html>
```

---

### Step 3.2: Add Data Management Button to Settings

**File:** `/var/www/html/settings.html`

**Add button** after the "License & Tier" section:

```html
<!-- Data Management -->
<div style="margin: 20px 0;">
    <button onclick="window.location.href='/settings-data.html'"
            style="background: #00CC00; color: #000; border: none; padding: 20px 40px;
                   font-size: 24px; cursor: pointer; width: 100%;">
        📦 Data Management & Export
    </button>
</div>
```

---

## PHASE 4: MEDIA CLEANUP SYSTEM (2-3 HOURS)

### Step 4.1: Create Media Cleanup Script

**File:** `/opt/d3kos/scripts/media-cleanup.sh`

```bash
#!/bin/bash
# media-cleanup.sh - Automatic cleanup of marine vision media files
# Deletes files older than 7 days OR when storage > 90% full

set -e

MEDIA_DIR="/home/d3kos/camera-recordings"
MAX_AGE_DAYS=7
STORAGE_THRESHOLD=90
CRITICAL_THRESHOLD=95

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a /var/log/d3kos-media-cleanup.log
}

log "Media cleanup starting..."

# Check if media directory exists
if [ ! -d "$MEDIA_DIR" ]; then
    log "Media directory not found: $MEDIA_DIR"
    exit 0
fi

# Get current storage usage
storage_usage=$(df -h "$MEDIA_DIR" | awk 'NR==2 {print $5}' | sed 's/%//')
log "Current storage usage: ${storage_usage}%"

# Function to delete old files
delete_old_files() {
    local age_days=$1
    log "Deleting files older than $age_days days..."

    find "$MEDIA_DIR" -type f \( -name "*.jpg" -o -name "*.mp4" \) -mtime +$age_days -exec rm -f {} \; 2>/dev/null

    local count=$(find "$MEDIA_DIR" -type f \( -name "*.jpg" -o -name "*.mp4" \) -mtime +$age_days 2>/dev/null | wc -l)
    log "Deleted $count files older than $age_days days"
}

# Function to delete oldest files until storage is below threshold
delete_oldest_files() {
    local target_threshold=$1
    log "Storage critical (${storage_usage}%), deleting oldest files..."

    local files_deleted=0
    while [ "$storage_usage" -ge "$target_threshold" ]; do
        # Find oldest file
        local oldest=$(find "$MEDIA_DIR" -type f \( -name "*.jpg" -o -name "*.mp4" \) -printf '%T+ %p\n' | sort | head -n 1 | cut -d' ' -f2-)

        if [ -z "$oldest" ]; then
            log "No more media files to delete"
            break
        fi

        log "Deleting oldest file: $oldest"
        rm -f "$oldest"
        files_deleted=$((files_deleted + 1))

        # Recheck storage
        storage_usage=$(df -h "$MEDIA_DIR" | awk 'NR==2 {print $5}' | sed 's/%//')
    done

    log "Deleted $files_deleted oldest files, storage now at ${storage_usage}%"
}

# Critical threshold - delete oldest files immediately
if [ "$storage_usage" -ge "$CRITICAL_THRESHOLD" ]; then
    log "CRITICAL: Storage at ${storage_usage}% (>= ${CRITICAL_THRESHOLD}%)"

    # Send alert to user
    curl -s -X POST http://localhost:8092/alert/storage-critical \
        -H "Content-Type: application/json" \
        -d "{\"storage_usage\": $storage_usage, \"threshold\": $CRITICAL_THRESHOLD}" || true

    delete_oldest_files 85  # Delete until 85%
fi

# High threshold - delete oldest files
if [ "$storage_usage" -ge "$STORAGE_THRESHOLD" ]; then
    log "WARNING: Storage at ${storage_usage}% (>= ${STORAGE_THRESHOLD}%)"

    delete_oldest_files 80  # Delete until 80%
fi

# Normal cleanup - delete files older than 7 days
delete_old_files $MAX_AGE_DAYS

# Final storage check
storage_usage=$(df -h "$MEDIA_DIR" | awk 'NR==2 {print $5}' | sed 's/%//')
log "Media cleanup complete, storage at ${storage_usage}%"
```

**Set Permissions:**
```bash
sudo chmod +x /opt/d3kos/scripts/media-cleanup.sh
sudo chown d3kos:d3kos /opt/d3kos/scripts/media-cleanup.sh
```

**Test:**
```bash
sudo /opt/d3kos/scripts/media-cleanup.sh
```

---

### Step 4.2: Create Media Cleanup Timer

**File:** `/etc/systemd/system/d3kos-media-cleanup.timer`

```ini
[Unit]
Description=d3kOS Media Cleanup Timer
Documentation=https://github.com/boatiq/d3kos

[Timer]
OnCalendar=daily
OnCalendar=04:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

**File:** `/etc/systemd/system/d3kos-media-cleanup.service`

```ini
[Unit]
Description=d3kOS Media Cleanup Service
Documentation=https://github.com/boatiq/d3kos

[Service]
Type=oneshot
User=root
ExecStart=/opt/d3kos/scripts/media-cleanup.sh

StandardOutput=journal
StandardError=journal
```

**Enable Timer:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable d3kos-media-cleanup.timer
sudo systemctl start d3kos-media-cleanup.timer

# Check timer status
systemctl list-timers --all | grep media-cleanup

# Test service
sudo systemctl start d3kos-media-cleanup.service
journalctl -u d3kos-media-cleanup.service -n 30
```

---

## PHASE 5: TESTING & INTEGRATION (1-2 HOURS)

### Test 1: Manual Export Generation

```bash
# Generate export via API
curl -X POST http://localhost/export/generate | jq

# Expected output:
# {
#   "success": true,
#   "export_id": "export_1234567890",
#   "file_path": "/opt/d3kos/data/exports/export_1234567890.json",
#   "statistics": {
#     "total_categories": 9,
#     "categories_with_data": X,
#     "total_size_bytes": XXXX
#   }
# }

# Check export file was created
ls -lh /opt/d3kos/data/exports/export_*.json

# View export contents
cat /opt/d3kos/data/exports/export_*.json | jq '.installation_id, .tier, .categories | keys'
```

---

### Test 2: Queue Management

```bash
# Check queue status
curl http://localhost/export/queue/status | jq

# Process queue manually
curl -X POST http://localhost/export/process-queue | jq

# Check queue after processing
curl http://localhost/export/queue/status | jq

# View export history
curl http://localhost/export/history | jq
```

---

### Test 3: Boot-Time Upload

```bash
# Reboot system
sudo reboot

# After reboot, check boot export service
journalctl -u d3kos-boot-export.service -b

# Expected: "Queue processing complete" message

# Check queue was processed
curl http://localhost/export/queue/status | jq
```

---

### Test 4: Web UI

1. Navigate to `http://192.168.1.237/settings.html`
2. Click "Data Management & Export"
3. **Tier 0:** Should show upgrade message (no export access)
4. **Tier 1+:** Should show export controls
5. Click "Export All Data Now" → Should generate export and add to queue
6. Check queue status → Should show pending export
7. Click "Process Queue Now" → Should attempt upload
8. Check history → Should show successful export (if internet available)

---

### Test 5: Media Cleanup

```bash
# Create test media files
cd /home/d3kos/camera-recordings
touch test_old.jpg
touch test_old.mp4

# Set files to 8 days old
sudo touch -d "8 days ago" test_old.jpg test_old.mp4

# Run cleanup
sudo /opt/d3kos/scripts/media-cleanup.sh

# Check logs
tail -n 50 /var/log/d3kos-media-cleanup.log

# Verify old files deleted
ls -lh /home/d3kos/camera-recordings/test_old.*
# Expected: No such file or directory
```

---

### Test 6: Tier 0 Restrictions

```bash
# Set tier to 0 (if not already)
sudo jq '.tier = 0' /opt/d3kos/config/license.json > /tmp/license.json
sudo mv /tmp/license.json /opt/d3kos/config/license.json

# Try to generate export via API (should FAIL)
curl -X POST http://localhost/export/generate | jq

# Expected output:
# {
#   "success": false,
#   "error": "Export requires Tier 1 or higher"
# }

# Test web UI
# Navigate to http://192.168.1.237/settings-data.html
# Expected: Tier 0 warning message, no export controls
```

---

## SUCCESS CRITERIA

After completing all phases, verify:

✅ **Export Generation:**
- [ ] All 9 categories collected correctly
- [ ] Installation ID included in export
- [ ] Tier information included
- [ ] Marine vision exports metadata only (no media files)
- [ ] Export file created in `/opt/d3kos/data/exports/`

✅ **Queue Management:**
- [ ] Exports added to queue automatically
- [ ] Retry logic works (5min, 15min)
- [ ] Failed exports move to failed queue after 3 attempts
- [ ] Successful exports archived in history
- [ ] 7-day cleanup removes old failed exports

✅ **Boot-Time Upload:**
- [ ] Service runs on system boot
- [ ] Queue processed automatically
- [ ] Logs show successful processing

✅ **Web UI:**
- [ ] Data Management page loads correctly
- [ ] Tier 0 shows upgrade message (no export access)
- [ ] Tier 1+ shows export controls
- [ ] Manual export button works
- [ ] Queue status displays correctly
- [ ] History shows successful exports

✅ **Media Cleanup:**
- [ ] Timer runs daily at 4:00 AM
- [ ] Files older than 7 days deleted
- [ ] Storage threshold cleanup works (>90%)
- [ ] Critical threshold cleanup works (>95%)
- [ ] Logs show cleanup activity

✅ **API Endpoints:**
- [ ] `POST /export/generate` works
- [ ] `POST /export/process-queue` works
- [ ] `GET /export/queue/status` works
- [ ] `GET /export/history` works
- [ ] All endpoints accessible via nginx proxy

---

## ROLLBACK PLAN

If something goes wrong:

### Rollback Step 1: Stop Services

```bash
sudo systemctl stop d3kos-export-manager.service
sudo systemctl stop d3kos-boot-export.service
sudo systemctl stop d3kos-media-cleanup.timer

sudo systemctl disable d3kos-export-manager.service
sudo systemctl disable d3kos-boot-export.service
sudo systemctl disable d3kos-media-cleanup.timer
```

### Rollback Step 2: Remove Web UI

```bash
sudo rm /var/www/html/settings-data.html

# Restore settings.html backup (if modified)
sudo cp /var/www/html/settings.html.bak /var/www/html/settings.html
```

### Rollback Step 3: Remove Nginx Proxy

```bash
# Edit nginx config and remove /export/ location block
sudo nano /etc/nginx/sites-enabled/default

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
- `/opt/d3kos/scripts/boot-time-export.sh` (Boot upload script)
- `/opt/d3kos/scripts/media-cleanup.sh` (Media cleanup)

**Services:**
- `/opt/d3kos/services/export/export-manager.js` (Export manager, port 8092)

**Systemd Units:**
- `/etc/systemd/system/d3kos-export-manager.service` (Export manager service)
- `/etc/systemd/system/d3kos-boot-export.service` (Boot-time upload)
- `/etc/systemd/system/d3kos-media-cleanup.service` (Cleanup service)
- `/etc/systemd/system/d3kos-media-cleanup.timer` (Daily 4am timer)

**Web UI:**
- `/var/www/html/settings-data.html` (Data Management page)

**Modified:**
- `/var/www/html/settings.html` (Add Data Management button)
- `/etc/nginx/sites-enabled/default` (Export API proxy)

**Data Directories:**
- `/opt/d3kos/data/exports/` (Export files)
- `/opt/d3kos/data/exports/export_queue.json` (Queue)
- `/opt/d3kos/data/exports/export_history.json` (History)

---

## TIME ESTIMATE BREAKDOWN

| Phase | Task | Time |
|-------|------|------|
| **Phase 1** | Export collector functions (9 categories) | 2 hours |
| | Export generation logic | 1 hour |
| | Queue management functions | 1 hour |
| | Export manager service | 1 hour |
| | Nginx proxy | 15 min |
| **Phase 2** | Boot upload script | 30 min |
| | Boot upload service | 30 min |
| **Phase 3** | Data Management page HTML | 1.5 hours |
| | Settings page button | 15 min |
| **Phase 4** | Media cleanup script | 1 hour |
| | Cleanup timer/service | 30 min |
| **Phase 5** | Comprehensive testing | 2 hours |
| **Total** | | **12-16 hours** |

---

## DEPENDENCIES

**Required Before Starting:**
- ✅ Task #1 (Installation ID) complete
- ✅ Task #2 (Tier System) complete
- ✅ Node.js and npm installed
- ✅ SQLite databases exist (boatlog, captures, telemetry)

**Services That Must Be Working:**
- ✅ d3kos-tier-api.service (tier detection)
- ✅ d3kos-license-api.service (installation_id)
- ✅ nginx web server

---

## NEXT STEPS AFTER COMPLETION

Once Task #3 is complete:

1. **Update MEMORY.md** with implementation details
2. **Test with real data** (boat logs, captures, etc.)
3. **Set up central database API** (backend infrastructure)
4. **Document export system** in user guide
5. **Implement E-commerce/Stripe** (Task #4 - paid tiers)

---

## NOTES FOR NEXT SESSION

**Session Coordination:**
- Register in `.session-status.md` before starting
- Check `.domain-ownership.md` for file conflicts
- Domain: Data Management (Domain 7)
- Can run parallel with other sessions (different domain)

**Testing Checklist:**
- [ ] All 9 export categories working
- [ ] Queue retry logic working
- [ ] Boot-time upload working
- [ ] Media cleanup working
- [ ] Web UI working
- [ ] Tier 0 restrictions working
- [ ] All API endpoints working

**Known Limitations:**
- Central database API not implemented yet (exports will fail upload)
- Mock API server needed for testing
- Marine vision media files NOT uploaded (design limitation)
- Telemetry database may not exist yet (Phase 5 depends on separate telemetry system)

---

**END OF IMPLEMENTATION GUIDE - TASK #3**

**All preparation complete - ready to start implementation!**
