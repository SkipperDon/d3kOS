# Fix 4: Export Queue/Retry System Implementation

**Date:** February 20, 2026
**Issue:** Export queue and retry logic not implemented
**Status:** ⏳ IN PROGRESS
**Time:** 10-12 hours (5 phases)

---

## Problem Statement

The export manager service (d3kos-export-manager.service, port 8094) can generate manual exports but is missing critical functionality:

**Currently Working:**
- ✅ Manual export generation (`POST /export/generate`)
- ✅ Export status checking (`GET /export/status`)
- ✅ Tier-based export restrictions

**Missing (Critical):**
- ❌ Export queue file system
- ❌ Retry logic (3 attempts: immediate, 5min, 15min)
- ❌ Boot-time upload of pending exports
- ❌ Scheduled daily export (3:00 AM, Tier 2+ only)
- ❌ All 9 export categories (currently only basic implementation)
- ❌ Export history tracking
- ❌ Network connectivity checks
- ❌ Failed export archiving

---

## Implementation Phases

### Phase 1: Queue System (3-4 hours)
- Export queue JSON file structure
- Queue management class
- Add exports to queue
- Queue status API endpoint
- Queue cleanup (old/completed exports)

### Phase 2: Retry Logic (2-3 hours)
- Background worker thread
- Network connectivity detection
- 3-attempt retry mechanism (immediate, 5min, 15min)
- Failed export tracking
- Success/failure callbacks

### Phase 3: Boot-time Upload (1-2 hours)
- Check queue on system boot
- Upload pending exports
- Boot service integration
- Logging and status reporting

### Phase 4: Scheduled Export (2-3 hours)
- Systemd timer (daily 3:00 AM)
- Tier 2+ restriction check
- Incremental export (only new data since last export)
- Auto-add to queue

### Phase 5: All 9 Categories (2-3 hours)
- Engine benchmark data
- Boatlog entries (voice, text, auto, weather)
- Marine vision captures (metadata only)
- Marine vision snapshots (metadata only)
- QR code data
- Settings configuration
- System alerts
- Onboarding/initial setup configuration
- Telemetry & analytics (NEW)

---

## File Structure

```
/opt/d3kos/
├── data/
│   └── exports/
│       ├── export_queue.json          # Pending exports queue
│       ├── export_history.json        # Completed exports log
│       ├── failed_exports/            # Failed export archive
│       └── exports/                   # Generated export JSON files
│           ├── export_20260220_100530.json
│           └── ...
├── services/
│   └── export/
│       ├── export-manager.py          # Main export service (UPDATE)
│       ├── export_queue.py            # Queue management class (NEW)
│       ├── export_worker.py           # Background retry worker (NEW)
│       └── export_categories.py       # All 9 category collectors (NEW)
└── scripts/
    └── export-on-boot.sh              # Boot-time export script (NEW)
```

---

## Phase 1: Queue System

### Queue File Format

**File:** `/opt/d3kos/data/exports/export_queue.json`

```json
{
  "version": "1.0",
  "last_updated": "2026-02-20T10:05:30Z",
  "pending": [
    {
      "queue_id": "q_20260220_100530",
      "export_file": "/opt/d3kos/data/exports/exports/export_20260220_100530.json",
      "created_at": "2026-02-20T10:05:30Z",
      "tier": 2,
      "category_count": 9,
      "file_size_bytes": 45632,
      "status": "pending",
      "retry_count": 0,
      "next_retry_at": "2026-02-20T10:05:30Z",
      "last_error": null
    }
  ],
  "uploading": [],
  "completed": [],
  "failed": []
}
```

### Queue Management Class

**File:** `/opt/d3kos/services/export/export_queue.py`

```python
#!/usr/bin/env python3
"""
Export Queue Management
Handles queue operations, retry logic, and status tracking
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

QUEUE_FILE = "/opt/d3kos/data/exports/export_queue.json"
HISTORY_FILE = "/opt/d3kos/data/exports/export_history.json"
FAILED_DIR = "/opt/d3kos/data/exports/failed_exports"

class ExportQueue:
    def __init__(self):
        self.queue_file = Path(QUEUE_FILE)
        self.history_file = Path(HISTORY_FILE)
        self.failed_dir = Path(FAILED_DIR)
        self._ensure_files()

    def _ensure_files(self):
        """Create queue files and directories if they don't exist"""
        self.queue_file.parent.mkdir(parents=True, exist_ok=True)
        self.failed_dir.mkdir(parents=True, exist_ok=True)

        if not self.queue_file.exists():
            self._write_queue({
                "version": "1.0",
                "last_updated": datetime.utcnow().isoformat() + "Z",
                "pending": [],
                "uploading": [],
                "completed": [],
                "failed": []
            })

        if not self.history_file.exists():
            self._write_history({
                "version": "1.0",
                "exports": []
            })

    def _read_queue(self):
        """Read queue file"""
        try:
            with open(self.queue_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading queue: {e}")
            return self._get_empty_queue()

    def _write_queue(self, data):
        """Write queue file"""
        data['last_updated'] = datetime.utcnow().isoformat() + "Z"
        with open(self.queue_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _get_empty_queue(self):
        return {
            "version": "1.0",
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "pending": [],
            "uploading": [],
            "completed": [],
            "failed": []
        }

    def add_export(self, export_file, tier, category_count):
        """Add export to queue"""
        queue = self._read_queue()

        # Generate queue ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        queue_id = f"q_{timestamp}"

        # Get file size
        file_size = os.path.getsize(export_file) if os.path.exists(export_file) else 0

        # Create queue entry
        entry = {
            "queue_id": queue_id,
            "export_file": str(export_file),
            "created_at": datetime.utcnow().isoformat() + "Z",
            "tier": tier,
            "category_count": category_count,
            "file_size_bytes": file_size,
            "status": "pending",
            "retry_count": 0,
            "next_retry_at": datetime.utcnow().isoformat() + "Z",
            "last_error": None
        }

        queue['pending'].append(entry)
        self._write_queue(queue)

        print(f"Added to queue: {queue_id} ({file_size} bytes, {category_count} categories)")
        return queue_id

    def get_next_pending(self):
        """Get next pending export ready for upload"""
        queue = self._read_queue()

        for entry in queue['pending']:
            # Check if ready for retry
            next_retry = datetime.fromisoformat(entry['next_retry_at'].replace('Z', '+00:00'))
            if datetime.now(next_retry.tzinfo) >= next_retry:
                return entry

        return None

    def mark_uploading(self, queue_id):
        """Mark export as currently uploading"""
        queue = self._read_queue()

        # Find in pending
        for i, entry in enumerate(queue['pending']):
            if entry['queue_id'] == queue_id:
                entry['status'] = 'uploading'
                queue['uploading'].append(entry)
                del queue['pending'][i]
                self._write_queue(queue)
                return True

        return False

    def mark_success(self, queue_id):
        """Mark export as successfully uploaded"""
        queue = self._read_queue()

        # Find in uploading
        for i, entry in enumerate(queue['uploading']):
            if entry['queue_id'] == queue_id:
                entry['status'] = 'completed'
                entry['completed_at'] = datetime.utcnow().isoformat() + "Z"
                queue['completed'].append(entry)
                del queue['uploading'][i]
                self._write_queue(queue)

                # Add to history
                self._add_to_history(entry)
                return True

        return False

    def mark_failed(self, queue_id, error_message):
        """Mark export as failed (retry or permanent failure)"""
        queue = self._read_queue()

        # Find in uploading
        for i, entry in enumerate(queue['uploading']):
            if entry['queue_id'] == queue_id:
                entry['retry_count'] += 1
                entry['last_error'] = error_message

                # Retry schedule: immediate, 5min, 15min, then fail
                if entry['retry_count'] == 1:
                    # First retry: immediate (set to now)
                    entry['next_retry_at'] = datetime.utcnow().isoformat() + "Z"
                    entry['status'] = 'pending'
                    queue['pending'].append(entry)
                elif entry['retry_count'] == 2:
                    # Second retry: 5 minutes
                    entry['next_retry_at'] = (datetime.utcnow() + timedelta(minutes=5)).isoformat() + "Z"
                    entry['status'] = 'pending'
                    queue['pending'].append(entry)
                elif entry['retry_count'] == 3:
                    # Third retry: 15 minutes
                    entry['next_retry_at'] = (datetime.utcnow() + timedelta(minutes=15)).isoformat() + "Z"
                    entry['status'] = 'pending'
                    queue['pending'].append(entry)
                else:
                    # Permanent failure after 3 retries
                    entry['status'] = 'failed'
                    entry['failed_at'] = datetime.utcnow().isoformat() + "Z"
                    queue['failed'].append(entry)

                    # Archive failed export
                    self._archive_failed_export(entry)

                del queue['uploading'][i]
                self._write_queue(queue)
                return True

        return False

    def _add_to_history(self, entry):
        """Add completed export to history"""
        try:
            history = json.loads(self.history_file.read_text())
        except:
            history = {"version": "1.0", "exports": []}

        history['exports'].append(entry)
        self.history_file.write_text(json.dumps(history, indent=2))

    def _archive_failed_export(self, entry):
        """Archive failed export file"""
        try:
            export_file = Path(entry['export_file'])
            if export_file.exists():
                archive_name = f"{entry['queue_id']}_failed.json"
                archive_path = self.failed_dir / archive_name
                export_file.rename(archive_path)
                print(f"Archived failed export: {archive_path}")
        except Exception as e:
            print(f"Error archiving failed export: {e}")

    def get_queue_status(self):
        """Get queue status summary"""
        queue = self._read_queue()

        return {
            "pending_count": len(queue['pending']),
            "uploading_count": len(queue['uploading']),
            "completed_count": len(queue['completed']),
            "failed_count": len(queue['failed']),
            "next_pending": queue['pending'][0] if queue['pending'] else None,
            "last_updated": queue['last_updated']
        }

    def cleanup_old_completed(self, days=30):
        """Remove completed exports older than X days"""
        queue = self._read_queue()
        cutoff = datetime.utcnow() - timedelta(days=days)

        # Filter completed
        queue['completed'] = [
            entry for entry in queue['completed']
            if datetime.fromisoformat(entry['completed_at'].replace('Z', '+00:00')) > cutoff
        ]

        self._write_queue(queue)
        print(f"Cleaned up completed exports older than {days} days")

    def cleanup_old_failed(self, days=7):
        """Remove failed exports older than X days"""
        queue = self._read_queue()
        cutoff = datetime.utcnow() - timedelta(days=days)

        # Filter failed
        queue['failed'] = [
            entry for entry in queue['failed']
            if datetime.fromisoformat(entry['failed_at'].replace('Z', '+00:00')) > cutoff
        ]

        self._write_queue(queue)
        print(f"Cleaned up failed exports older than {days} days")
```

### Update Export Manager Service

**File:** `/opt/d3kos/services/export/export-manager.py` (UPDATE)

Add queue integration to existing export manager:

```python
# Add import
from export_queue import ExportQueue

# In __init__
self.queue = ExportQueue()

# Update generate_export() method to add to queue
@app.route('/export/generate', methods=['POST'])
def api_generate_export():
    """Generate export and add to queue"""
    try:
        # ... existing export generation code ...

        # Add to queue
        queue_id = self.queue.add_export(
            export_file=export_path,
            tier=tier,
            category_count=len(export_data['data'])
        )

        return jsonify({
            'success': True,
            'export_file': export_filename,
            'queue_id': queue_id,
            'message': 'Export generated and added to queue'
        })

    except Exception as e:
        # ... error handling ...

# Add queue status endpoint
@app.route('/export/queue/status', methods=['GET'])
def api_queue_status():
    """Get export queue status"""
    try:
        status = self.queue.get_queue_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

---

## Phase 2: Retry Logic & Background Worker

### Background Worker Thread

**File:** `/opt/d3kos/services/export/export_worker.py`

```python
#!/usr/bin/env python3
"""
Export Queue Background Worker
Handles retry logic and automatic upload
"""

import time
import requests
from threading import Thread, Event
from export_queue import ExportQueue

class ExportWorker:
    def __init__(self, central_api_url):
        self.central_api_url = central_api_url
        self.queue = ExportQueue()
        self.stop_event = Event()
        self.worker_thread = None

    def start(self):
        """Start background worker thread"""
        if self.worker_thread and self.worker_thread.is_alive():
            print("Worker already running")
            return

        self.stop_event.clear()
        self.worker_thread = Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        print("Export worker started")

    def stop(self):
        """Stop background worker thread"""
        self.stop_event.set()
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        print("Export worker stopped")

    def _worker_loop(self):
        """Main worker loop - checks queue every 30 seconds"""
        while not self.stop_event.is_set():
            try:
                # Get next pending export
                entry = self.queue.get_next_pending()

                if entry:
                    print(f"Processing export: {entry['queue_id']}")
                    self._process_export(entry)

                # Check network connectivity
                if not self._check_network():
                    print("No network connectivity, waiting...")

                # Wait 30 seconds before next check
                self.stop_event.wait(30)

            except Exception as e:
                print(f"Worker error: {e}")
                self.stop_event.wait(60)  # Wait longer on error

    def _check_network(self):
        """Check if network/internet is available"""
        try:
            response = requests.get(
                "https://www.google.com",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False

    def _process_export(self, entry):
        """Upload export to central database"""
        queue_id = entry['queue_id']
        export_file = entry['export_file']

        try:
            # Mark as uploading
            self.queue.mark_uploading(queue_id)

            # Read export file
            with open(export_file, 'r') as f:
                export_data = f.read()

            # Upload to central database
            response = requests.post(
                f"{self.central_api_url}/api/v1/data/import",
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {entry["tier"]}'  # Placeholder
                },
                data=export_data,
                timeout=30
            )

            if response.status_code == 200:
                # Success
                self.queue.mark_success(queue_id)
                print(f"✓ Export uploaded successfully: {queue_id}")
            else:
                # Failed
                error = f"HTTP {response.status_code}: {response.text}"
                self.queue.mark_failed(queue_id, error)
                print(f"✗ Export upload failed: {error}")

        except Exception as e:
            # Failed
            self.queue.mark_failed(queue_id, str(e))
            print(f"✗ Export upload error: {e}")
```

### Integrate Worker with Export Manager

**File:** `/opt/d3kos/services/export/export-manager.py` (UPDATE)

```python
# Add import
from export_worker import ExportWorker

# In main Flask app
CENTRAL_API_URL = "https://d3kos-cloud-api.example.com"  # Update with actual URL

# Initialize worker
worker = ExportWorker(CENTRAL_API_URL)
worker.start()

# Shutdown handler
import atexit
@atexit.register
def shutdown():
    worker.stop()
```

---

## Phase 3: Boot-time Upload

### Boot-time Export Script

**File:** `/opt/d3kos/scripts/export-on-boot.sh`

```bash
#!/bin/bash
# Export Queue Boot-time Upload
# Checks queue and uploads pending exports on system boot

set -e

LOG_FILE="/var/log/d3kos-export-boot.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=== d3kOS Export Boot-time Upload ==="

# Wait for network (max 60 seconds)
log "Waiting for network..."
for i in {1..12}; do
    if ping -c 1 -W 2 8.8.8.8 >/dev/null 2>&1; then
        log "✓ Network available"
        break
    fi
    sleep 5
done

# Check if export manager is running
if ! systemctl is-active --quiet d3kos-export-manager.service; then
    log "⚠ Export manager not running, starting..."
    systemctl start d3kos-export-manager.service
    sleep 3
fi

# Check queue status
QUEUE_STATUS=$(curl -s http://localhost:8094/export/queue/status)
PENDING_COUNT=$(echo "$QUEUE_STATUS" | jq -r '.pending_count // 0')

log "Queue status: $PENDING_COUNT pending exports"

if [ "$PENDING_COUNT" -gt 0 ]; then
    log "Processing pending exports..."

    # Worker will automatically process queue
    # Just wait and monitor

    # Monitor for 5 minutes max
    for i in {1..10}; do
        sleep 30
        QUEUE_STATUS=$(curl -s http://localhost:8094/export/queue/status)
        PENDING_COUNT=$(echo "$QUEUE_STATUS" | jq -r '.pending_count // 0')
        log "Queue status: $PENDING_COUNT pending"

        if [ "$PENDING_COUNT" -eq 0 ]; then
            log "✓ All exports uploaded"
            break
        fi
    done
else
    log "No pending exports"
fi

log "=== Boot-time upload complete ==="
```

### Systemd Service for Boot Upload

**File:** `/etc/systemd/system/d3kos-export-boot.service`

```ini
[Unit]
Description=d3kOS Export Boot-time Upload
After=network-online.target d3kos-export-manager.service
Wants=network-online.target

[Service]
Type=oneshot
User=d3kos
ExecStart=/opt/d3kos/scripts/export-on-boot.sh
RemainAfterExit=yes
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

---

## Phase 4: Scheduled Export

### Systemd Timer

**File:** `/etc/systemd/system/d3kos-export-daily.timer`

```ini
[Unit]
Description=d3kOS Daily Export Timer
Requires=d3kos-export-daily.service

[Timer]
# Run daily at 3:00 AM
OnCalendar=*-*-* 03:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

**File:** `/etc/systemd/system/d3kos-export-daily.service`

```ini
[Unit]
Description=d3kOS Daily Scheduled Export
After=network-online.target d3kos-export-manager.service
Wants=network-online.target

[Service]
Type=oneshot
User=d3kos
ExecStart=/opt/d3kos/scripts/export-daily.sh
StandardOutput=journal
StandardError=journal

[Install]
# No [Install] section - triggered by timer only
```

### Daily Export Script

**File:** `/opt/d3kos/scripts/export-daily.sh`

```bash
#!/bin/bash
# Daily Scheduled Export (Tier 2+ only)

set -e

LOG_FILE="/var/log/d3kos-export-daily.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=== d3kOS Daily Scheduled Export ==="

# Check tier
TIER_STATUS=$(curl -s http://localhost:8093/tier/status)
TIER=$(echo "$TIER_STATUS" | jq -r '.tier // 0')

log "Current tier: $TIER"

if [ "$TIER" -lt 2 ]; then
    log "⚠ Scheduled export requires Tier 2+ (current: Tier $TIER)"
    log "Skipping export"
    exit 0
fi

log "Triggering export..."

# Trigger export
RESULT=$(curl -s -X POST http://localhost:8094/export/generate)
SUCCESS=$(echo "$RESULT" | jq -r '.success // false')

if [ "$SUCCESS" = "true" ]; then
    QUEUE_ID=$(echo "$RESULT" | jq -r '.queue_id')
    log "✓ Export generated and queued: $QUEUE_ID"
else
    ERROR=$(echo "$RESULT" | jq -r '.error // "Unknown error"')
    log "✗ Export failed: $ERROR"
    exit 1
fi

log "=== Daily export complete ==="
```

---

## Phase 5: All 9 Export Categories

### Export Categories Implementation

**File:** `/opt/d3kos/services/export/export_categories.py`

```python
#!/usr/bin/env python3
"""
Export Category Collectors
Collects data for all 9 export categories per MASTER_SYSTEM_SPEC.md Section 8.3
"""

import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path

class ExportCategories:
    def __init__(self, installation_id):
        self.installation_id = installation_id

    def collect_all(self):
        """Collect all 9 categories"""
        categories = {
            'installation_id': self.installation_id,
            'export_timestamp': datetime.utcnow().isoformat() + 'Z',
            'format_version': '1.0',
            'data': {}
        }

        # Collect each category
        categories['data']['engine_benchmark'] = self.collect_engine_benchmark()
        categories['data']['boatlog'] = self.collect_boatlog()
        categories['data']['marine_vision_captures'] = self.collect_marine_vision_captures()
        categories['data']['marine_vision_snapshots'] = self.collect_marine_vision_snapshots()
        categories['data']['qr_codes'] = self.collect_qr_codes()
        categories['data']['settings'] = self.collect_settings()
        categories['data']['system_alerts'] = self.collect_system_alerts()
        categories['data']['onboarding'] = self.collect_onboarding()
        categories['data']['telemetry'] = self.collect_telemetry()

        return categories

    def collect_engine_benchmark(self):
        """Category 1: Engine benchmark data"""
        # Placeholder - implement when engine benchmark feature is added
        return {
            'category': 'engine_benchmark',
            'entry_count': 0,
            'entries': []
        }

    def collect_boatlog(self):
        """Category 2: Boatlog entries (all types)"""
        try:
            conn = sqlite3.connect('/opt/d3kos/data/boatlog/boatlog.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT entry_id, timestamp, entry_type, content,
                       latitude, longitude, weather_conditions
                FROM boatlog_entries
                ORDER BY timestamp DESC
            """)

            entries = []
            for row in cursor.fetchall():
                entries.append({
                    'entry_id': row['entry_id'],
                    'timestamp': row['timestamp'],
                    'type': row['entry_type'],
                    'content': row['content'],
                    'gps': {
                        'latitude': row['latitude'],
                        'longitude': row['longitude']
                    },
                    'weather': row['weather_conditions']
                })

            conn.close()

            return {
                'category': 'boatlog',
                'entry_count': len(entries),
                'entries': entries
            }

        except Exception as e:
            print(f"Error collecting boatlog: {e}")
            return {'category': 'boatlog', 'entry_count': 0, 'entries': [], 'error': str(e)}

    def collect_marine_vision_captures(self):
        """Category 3: Marine vision captures (METADATA ONLY)"""
        try:
            conn = sqlite3.connect('/opt/d3kos/data/marine-vision/captures.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT capture_id, timestamp, species, confidence,
                       latitude, longitude, file_path, file_size
                FROM captures
                ORDER BY timestamp DESC
            """)

            entries = []
            for row in cursor.fetchall():
                entries.append({
                    'capture_id': row['capture_id'],
                    'timestamp': row['timestamp'],
                    'species': row['species'],
                    'confidence': row['confidence'],
                    'gps': {
                        'latitude': row['latitude'],
                        'longitude': row['longitude']
                    },
                    'file_size_bytes': row['file_size'],
                    # NOTE: file_path NOT included in export (privacy)
                })

            conn.close()

            return {
                'category': 'marine_vision_captures',
                'entry_count': len(entries),
                'entries': entries,
                'note': 'Metadata only - image files not exported'
            }

        except Exception as e:
            print(f"Error collecting marine vision captures: {e}")
            return {'category': 'marine_vision_captures', 'entry_count': 0, 'entries': [], 'error': str(e)}

    def collect_marine_vision_snapshots(self):
        """Category 4: Marine vision snapshots (METADATA ONLY)"""
        # Placeholder - snapshots feature not yet implemented
        return {
            'category': 'marine_vision_snapshots',
            'entry_count': 0,
            'entries': [],
            'note': 'Metadata only - video files not exported'
        }

    def collect_qr_codes(self):
        """Category 5: QR code data"""
        # Placeholder - QR code data tracking not yet implemented
        return {
            'category': 'qr_codes',
            'entry_count': 0,
            'entries': []
        }

    def collect_settings(self):
        """Category 6: Settings configuration"""
        try:
            # Read license.json
            license_path = Path('/opt/d3kos/config/license.json')
            if license_path.exists():
                license_data = json.loads(license_path.read_text())
            else:
                license_data = {}

            # Collect other settings
            settings = {
                'license': license_data,
                'network': {},  # Add network settings if available
                'display': {},  # Add display settings if available
            }

            return {
                'category': 'settings',
                'data': settings
            }

        except Exception as e:
            print(f"Error collecting settings: {e}")
            return {'category': 'settings', 'data': {}, 'error': str(e)}

    def collect_system_alerts(self):
        """Category 7: System alerts"""
        # Placeholder - system alerts feature not yet implemented
        return {
            'category': 'system_alerts',
            'entry_count': 0,
            'entries': []
        }

    def collect_onboarding(self):
        """Category 8: Onboarding/initial setup configuration"""
        try:
            # Read onboarding.json
            onboarding_path = Path('/opt/d3kos/config/onboarding.json')
            if onboarding_path.exists():
                onboarding_data = json.loads(onboarding_path.read_text())
            else:
                onboarding_data = {}

            # Read reset counter
            reset_path = Path('/opt/d3kos/state/onboarding-reset-count.json')
            if reset_path.exists():
                reset_data = json.loads(reset_path.read_text())
            else:
                reset_data = {'count': 0}

            return {
                'category': 'onboarding',
                'data': {
                    'configuration': onboarding_data,
                    'reset_count': reset_data.get('count', 0),
                    'completion_timestamp': onboarding_data.get('completed_at')
                }
            }

        except Exception as e:
            print(f"Error collecting onboarding: {e}")
            return {'category': 'onboarding', 'data': {}, 'error': str(e)}

    def collect_telemetry(self):
        """Category 9: Telemetry & analytics (NEW)"""
        try:
            # System uptime
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.read().split()[0])

            # Memory usage
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
                mem_total = int([line for line in meminfo.split('\n') if 'MemTotal' in line][0].split()[1])
                mem_available = int([line for line in meminfo.split('\n') if 'MemAvailable' in line][0].split()[1])

            # Disk usage
            import shutil
            disk_usage = shutil.disk_usage('/opt/d3kos')

            return {
                'category': 'telemetry',
                'data': {
                    'system_uptime_seconds': uptime_seconds,
                    'memory_total_kb': mem_total,
                    'memory_available_kb': mem_available,
                    'memory_used_percent': ((mem_total - mem_available) / mem_total) * 100,
                    'disk_total_bytes': disk_usage.total,
                    'disk_used_bytes': disk_usage.used,
                    'disk_free_bytes': disk_usage.free,
                    'disk_used_percent': (disk_usage.used / disk_usage.total) * 100
                }
            }

        except Exception as e:
            print(f"Error collecting telemetry: {e}")
            return {'category': 'telemetry', 'data': {}, 'error': str(e)}
```

---

## Deployment Steps

### Step 1: Create Files

```bash
# SSH to Pi
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237

# Create export queue module
sudo mkdir -p /opt/d3kos/services/export
sudo cp export_queue.py /opt/d3kos/services/export/
sudo cp export_worker.py /opt/d3kos/services/export/
sudo cp export_categories.py /opt/d3kos/services/export/
sudo chown -R d3kos:d3kos /opt/d3kos/services/export

# Create scripts
sudo cp export-on-boot.sh /opt/d3kos/scripts/
sudo cp export-daily.sh /opt/d3kos/scripts/
sudo chmod +x /opt/d3kos/scripts/export-*.sh

# Create systemd services
sudo cp d3kos-export-boot.service /etc/systemd/system/
sudo cp d3kos-export-daily.service /etc/systemd/system/
sudo cp d3kos-export-daily.timer /etc/systemd/system/

# Create queue directories
sudo mkdir -p /opt/d3kos/data/exports/exports
sudo mkdir -p /opt/d3kos/data/exports/failed_exports
sudo chown -R d3kos:d3kos /opt/d3kos/data/exports
```

### Step 2: Update Export Manager

```bash
# Backup current version
sudo cp /opt/d3kos/services/export/export-manager.py \
       /opt/d3kos/services/export/export-manager.py.bak.queue

# Update with queue integration
sudo cp export-manager.py /opt/d3kos/services/export/

# Restart service
sudo systemctl restart d3kos-export-manager.service
```

### Step 3: Enable Services

```bash
# Enable boot upload
sudo systemctl daemon-reload
sudo systemctl enable d3kos-export-boot.service

# Enable daily timer
sudo systemctl enable d3kos-export-daily.timer
sudo systemctl start d3kos-export-daily.timer

# Verify timer
systemctl list-timers | grep d3kos-export
```

---

## Testing

### Test 1: Queue System

```bash
# Generate export
curl -X POST http://localhost:8094/export/generate

# Check queue
curl http://localhost:8094/export/queue/status | jq .

# Expected:
# {
#   "pending_count": 1,
#   "uploading_count": 0,
#   "completed_count": 0,
#   "failed_count": 0,
#   "next_pending": { ... }
# }

# Verify queue file
cat /opt/d3kos/data/exports/export_queue.json | jq .
```

### Test 2: Background Worker

```bash
# Monitor export manager logs
journalctl -u d3kos-export-manager.service -f

# Should see:
# "Processing export: q_YYYYMMDD_HHMMSS"
# "✓ Export uploaded successfully"

# Check queue after upload
curl http://localhost:8094/export/queue/status | jq .

# Expected:
# {
#   "pending_count": 0,
#   "completed_count": 1,
#   ...
# }
```

### Test 3: Retry Logic

```bash
# Disconnect network
sudo nmcli networking off

# Generate export
curl -X POST http://localhost:8094/export/generate

# Wait 30 seconds, check logs
journalctl -u d3kos-export-manager.service -n 20

# Should see:
# "Export upload failed: ..."
# "Retry 1/3 in 5 minutes"

# Reconnect network
sudo nmcli networking on

# Wait for retry, check logs
# Should see:
# "Processing export: q_..."
# "✓ Export uploaded successfully"
```

### Test 4: Boot Upload

```bash
# Generate export manually
curl -X POST http://localhost:8094/export/generate

# Reboot system
sudo reboot

# After reboot, check logs
journalctl -u d3kos-export-boot.service

# Should see:
# "Queue status: 1 pending exports"
# "Processing pending exports..."
# "✓ All exports uploaded"
```

### Test 5: Scheduled Export

```bash
# Trigger timer manually (don't wait for 3:00 AM)
sudo systemctl start d3kos-export-daily.service

# Check logs
journalctl -u d3kos-export-daily.service -n 50

# Should see:
# "Current tier: 2"
# "Triggering export..."
# "✓ Export generated and queued: q_..."

# Verify timer schedule
systemctl list-timers | grep d3kos-export

# Should show:
# NEXT                          LEFT     LAST ...
# Thu 2026-02-21 03:00:00 EST   ...      n/a  d3kos-export-daily.timer
```

### Test 6: All 9 Categories

```bash
# Generate export
curl -X POST http://localhost:8094/export/generate

# Get export file
EXPORT_FILE=$(ls -t /opt/d3kos/data/exports/exports/ | head -1)

# Check categories
cat "/opt/d3kos/data/exports/exports/$EXPORT_FILE" | jq -r '.data | keys[]'

# Expected output:
# boatlog
# engine_benchmark
# marine_vision_captures
# marine_vision_snapshots
# onboarding
# qr_codes
# settings
# system_alerts
# telemetry
```

---

## Rollback

```bash
# Stop services
sudo systemctl stop d3kos-export-boot.service
sudo systemctl stop d3kos-export-daily.timer
sudo systemctl stop d3kos-export-daily.service

# Restore original export manager
sudo cp /opt/d3kos/services/export/export-manager.py.bak.queue \
       /opt/d3kos/services/export/export-manager.py

# Restart export manager
sudo systemctl restart d3kos-export-manager.service

# Disable new services
sudo systemctl disable d3kos-export-boot.service
sudo systemctl disable d3kos-export-daily.timer
```

---

**Status:** ⏳ READY FOR DEPLOYMENT
**Next Step:** Deploy to Raspberry Pi and test each phase
**Estimated Time:** 10-12 hours (can be done in phases)
