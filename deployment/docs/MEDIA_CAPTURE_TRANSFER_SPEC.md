# d3kOS Media Capture, Storage & Transfer Specification
## Version 1.0 — 2026-03-27
## Covers: v0.9.4 S6+ — Camera Photos, Video Recording, Pi-to-App Transfer

---

## 1. PURPOSE

This document is the single authoritative reference for how photos and video
clips are captured, stored on the Pi, transferred to the mobile app, and removed
from the Pi after transfer. It consolidates behaviour established in v0.9.1 and
v0.9.2 with the v0.9.4 mobile app architecture.

**Non-negotiable constraints (confirmed by operator):**
- Photos and videos are NEVER uploaded to HostPapa — the server is not a media store
- Files are transferred P2P directly to the app via WebRTC data channel
- Once confirmed transferred to the app, files are DELETED from the Pi
- If storage reaches 90%, the app shows a notification with removal instructions
- One camera at a time — whichever slot is currently configured and selected
- App includes a full media library screen for browsing, downloading, and sharing

---

## 2. WHAT IS ALREADY BUILT (prior versions — do not rebuild)

### 2.1 Camera Stream Manager (`camera_stream_manager.py` — Port 8084)

Running on Pi at `/opt/d3kos/services/camera/camera_stream_manager.py`.

Already-built endpoints used by the media system:

| Method | Endpoint | What it does |
|--------|----------|--------------|
| POST | `/camera/capture` | Captures a JPEG frame from the forward_watch slot. Saves to `/home/d3kos/camera-recordings/capture_<slot_id>_<YYYYMMDD_HHMMSS>.jpg`. Returns `{status, filename, path, size_mb}`. |
| POST | `/camera/record/start` | Starts MP4 recording via VLC from forward_watch slot. Saves to `/home/d3kos/camera-recordings/recording_<slot_id>_<YYYYMMDD_HHMMSS>.mp4`. Returns `{status, filename, path}`. |
| POST | `/camera/record/stop` | Stops the active recording. Returns `{status: 'recording_stopped'}`. |
| GET | `/camera/recordings` | Lists all files in `/home/d3kos/camera-recordings/` — both `.mp4` and `.jpg`. Returns `{recordings: [{filename, size_mb}]}`. |
| GET | `/camera/frame/<slot_id>` | Returns raw JPEG bytes for the current frame of a slot. |

### 2.2 Storage Location on Pi

```
/home/d3kos/camera-recordings/
├── capture_<slot_id>_<YYYYMMDD_HHMMSS>.jpg     ← Manual photo (user-triggered)
├── recording_<slot_id>_<YYYYMMDD_HHMMSS>.mp4   ← Manual video (user-triggered)
└── captures/
    └── catch_<YYYYMMDD_HHMMSS>.jpg              ← Auto-capture (fish detection)
```

File format details:
- Photos: JPEG, 85% quality, frame buffer resolution
- Videos: MP4, H.264, 8000 kbps bitrate via VLC
- Fish detection captures: JPEG, 95% quality (separate subdirectory)

### 2.3 Fish Detector (`fish_detector.py` — Port 8086)

Auto-captures JPEG when YOLOv8 detects a fish with confidence > 0.25.
Stores capture metadata in SQLite: `/opt/d3kos/data/marine-vision/captures.db`.
The fish detection captures are in `captures/` subdirectory, not the main recordings folder.

### 2.4 Pi Media Manifest File (NEW — required by operator)

A human-readable index at `/home/d3kos/camera-recordings/MEDIA_README.txt` that
explains what is stored and how to remove files manually via SCP if the app is
not available. This file is maintained by the Pi service (updated on capture/delete).
See Section 6 for format.

---

## 3. WHAT NEEDS TO BE BUILT (v0.9.4 S6+)

| Component | Location | Status |
|-----------|----------|--------|
| WebRTC file transfer (Pi side) | `live_session.py` | NOT BUILT |
| WebRTC file transfer (App side) | `app.js` screens.media | NOT BUILT |
| Photo/record controls on live screen | `app.js` screens.live | NOT BUILT |
| Media library screen | `app.js` screens.media | NOT BUILT |
| Delete-from-Pi after confirmed transfer | `live_session.py` | NOT BUILT |
| 90% storage warning | `live_session.py` + `app.js` | NOT BUILT |
| Pi media manifest file (MEDIA_README.txt) | Pi `/home/d3kos/camera-recordings/` | NOT BUILT |
| Storage endpoint on Pi | `live_session.py` data channel | NOT BUILT |

---

## 4. CAPTURE TRIGGERS

### 4.1 User-Triggered (from Live Screen in App)

The user is on `screens.live` with a P2P WebRTC connection active.

**Photo capture:**
1. App sends data channel message: `{ "type": "capture_request" }`
2. Pi calls `POST http://localhost:8084/camera/capture` internally
3. Pi reads the saved JPEG file
4. Pi sends file back via WebRTC data channel (chunked — see Section 5)
5. App assembles chunks, saves to device photo library (Web Share API)
6. App sends `{ "type": "transfer_complete", "filename": "<filename>" }`
7. Pi deletes the file from disk

**Video recording:**
1. App sends: `{ "type": "record_start" }`
2. Pi calls `POST http://localhost:8084/camera/record/start` internally
3. Pi sends back: `{ "type": "record_started", "filename": "<filename>" }` (so app can show timer)
4. User taps Stop — App sends: `{ "type": "record_stop" }`
5. Pi calls `POST http://localhost:8084/camera/record/stop` internally
6. Pi reads the saved MP4 file
7. Pi sends file back via data channel (chunked — see Section 5)
8. App assembles chunks, offers save/share via Web Share API
9. App sends `{ "type": "transfer_complete", "filename": "<filename>" }`
10. Pi deletes the file from disk

### 4.2 Auto-Triggered (Fish Detection — NOT user-controlled)

Fish detection captures are stored in `captures/` subdirectory.
These are NOT auto-transferred — the user browses them in the media library
and transfers them on demand (same mechanism as manual captures).

---

## 5. FILE TRANSFER ARCHITECTURE — WebRTC DATA CHANNEL BINARY CHUNKING

The live data channel used for sensor readings is ALSO used for file transfer.
Files are sent as a sequence of data channel messages.

### 5.1 Protocol (Pi → App)

```
Step 1 — Pi sends file header:
  { "type": "file_start",
    "filename": "capture_bow_20260327_143022.jpg",
    "media_type": "photo",             // "photo" | "video" | "fish_capture"
    "mime": "image/jpeg",              // "image/jpeg" | "video/mp4"
    "size_bytes": 248192,
    "chunk_count": 25                  // ceil(size / CHUNK_SIZE)
  }

Step 2 — Pi sends binary chunks (ArrayBuffer):
  Each chunk is raw binary. No JSON wrapper. Max chunk size: 16KB.
  Chunks arrive in order. Count matches chunk_count.

Step 3 — Pi sends file footer:
  { "type": "file_end",
    "filename": "capture_bow_20260327_143022.jpg",
    "checksum": "md5:<hex>"           // MD5 of complete file for integrity check
  }

Step 4 — App verifies checksum, sends ack:
  { "type": "transfer_complete", "filename": "capture_bow_20260327_143022.jpg" }

Step 5 — Pi deletes the file from /home/d3kos/camera-recordings/
```

### 5.2 Chunk Size and Timing

- Chunk size: 16,384 bytes (16 KB) — safe for WebRTC data channel buffering
- No delay between chunks — send as fast as data channel allows
- If data channel buffer > 8 MB: pause sending, resume on `bufferedamountlow` event

### 5.3 App Assembly

App maintains a `Map` of in-progress transfers keyed by filename.
On `file_start`: initialise entry with `{mime, totalChunks, chunks: [], received: 0}`.
On binary message: append to `chunks[]`, increment `received`.
On `file_end`: verify `received === totalChunks` and checksum; if OK, assemble Blob.

### 5.4 Sensor Data During Transfer

Sensor push (every 5s) and file transfer share the same data channel.
Pi queues sensor JSON messages normally — they are small and arrive between
binary chunk messages. No conflict. App distinguishes JSON (sensor/control) from
binary (file chunks) by message type: `typeof event.data`.

---

## 6. PI MEDIA MANIFEST FILE

Path: `/home/d3kos/camera-recordings/MEDIA_README.txt`

Updated by the Pi service on every capture, transfer, and delete.
Format:

```
d3kOS Media Storage — /home/d3kos/camera-recordings/
Last updated: 2026-03-27 14:30:22
Total files: 3  |  Total size: 142.6 MB  |  Disk usage: 23%

FILES STORED:
  recording_bow_20260327_143022.mp4     38.2 MB   2026-03-27 14:30
  capture_bow_20260327_120541.jpg        0.2 MB   2026-03-27 12:05
  captures/catch_20260327_091233.jpg     0.1 MB   2026-03-27 09:12

TO REMOVE FILES VIA SCP — WINDOWS:
  Install WinSCP from https://winscp.net (free, GUI)
  Host: [Pi IP address]  Port: 22  Username: d3kos
  Navigate to: /home/d3kos/camera-recordings/
  Select files and press Delete.

  Or copy to your PC first, then delete:
    Open WinSCP → drag files to your Windows desktop → then delete on Pi side.

TO REMOVE FILES VIA SCP — MAC:
  Open Terminal (Finder → Applications → Utilities → Terminal)
  Copy a file to your Mac desktop:
    scp d3kos@[Pi IP]:/home/d3kos/camera-recordings/filename.mp4 ~/Desktop/
  Delete a file from the Pi:
    ssh d3kos@[Pi IP] "rm /home/d3kos/camera-recordings/filename.mp4"
  Delete all files at once:
    ssh d3kos@[Pi IP] "rm /home/d3kos/camera-recordings/*.mp4 /home/d3kos/camera-recordings/*.jpg"

TO REMOVE FILES VIA SCP — LINUX:
  Open a terminal.
  Copy a file to your home directory:
    scp d3kos@[Pi IP]:/home/d3kos/camera-recordings/filename.mp4 ~/
  Delete a file from the Pi:
    ssh d3kos@[Pi IP] "rm /home/d3kos/camera-recordings/filename.mp4"
  Delete all files at once:
    ssh d3kos@[Pi IP] "rm /home/d3kos/camera-recordings/*.mp4 /home/d3kos/camera-recordings/*.jpg"

NOTE: Replace [Pi IP address] with the IP shown in d3kOS Settings.
      Default SSH credentials — Username: d3kos  (no password by default on your Pi).

Files are automatically removed after successful transfer to the mobile app.
If a file remains here it was not yet transferred or transfer failed.
```

---

## 7. STORAGE WARNING — 90% DISK THRESHOLD

### 7.1 Pi Side

`live_session.py` checks disk usage at startup and every 30 minutes.
Uses `shutil.disk_usage('/')` to get total/used/free.
If used/total >= 0.90:
- Sends data channel message: `{ "type": "storage_warning", "percent_used": 92, "free_gb": 1.2 }`
- This fires on every sensor push cycle until disk drops below 90%

### 7.2 App Side — Warning Banner

When app receives `type: "storage_warning"`:
- Shows a persistent yellow banner on the live screen (and on dashboard if last seen < 24h ago)
- Banner text: "⚠ Boat storage is [X]% full. Open Media Library to transfer and remove files."
- Banner has "Open Media Library" button → `navigate('media')`
- Cannot be dismissed until disk drops below 85%

---

## 8. APP MEDIA LIBRARY — `screens.media`

### 8.1 Navigation

Accessible from:
- Dashboard quick-action row (new "Media" button alongside Go Live and My Reports)
- Live screen: "Media" button in the camera controls row
- Storage warning banner: "Open Media Library" button

### 8.2 Layout

```
← Back    [screen title: "Media Library"]

[  Transfer All  ]    [status: 3 files · 42 MB on Pi]

┌─────────────────────────────────────────────────────┐
│  🎬 recording_bow_20260327_143022.mp4                │
│     38.2 MB · 2026-03-27 14:30                       │
│     [Transfer to Phone]  [Delete from Pi]            │
├─────────────────────────────────────────────────────┤
│  📷 capture_bow_20260327_120541.jpg                  │
│     0.2 MB · 2026-03-27 12:05                        │
│     [Transfer to Phone]  [Delete from Pi]            │
├─────────────────────────────────────────────────────┤
│  🐟 Fish: catch_20260327_091233.jpg                  │
│     0.1 MB · 2026-03-27 09:12                        │
│     [Transfer to Phone]  [Delete from Pi]            │
└─────────────────────────────────────────────────────┘

[Note: Requires active live connection to Pi]
```

### 8.3 Behaviour

**Requires live session:** screens.media checks if WebRTC connection is active.
If not, shows "Connect to your boat first — tap Go Live." with a Go Live button.
If live session drops while in media library, shows disconnected state.

**Listing:** On load, sends `{ "type": "media_list_request" }` via data channel.
Pi responds with `{ "type": "media_list", "files": [...], "disk_percent": 23 }`.

**Transfer to Phone:**
- Sends `{ "type": "transfer_request", "filename": "<filename>" }`
- Pi sends file via chunked binary transfer (Section 5)
- Progress bar shows during transfer
- On complete: Web Share API or direct download (JPEG shown as image, MP4 as video)
- File removed from Pi automatically after confirmed transfer

**Delete from Pi (without transfer):**
- Sends `{ "type": "delete_request", "filename": "<filename>" }`
- Pi deletes the file, sends `{ "type": "delete_ack", "filename": "<filename>" }`
- Item removed from list in app

**Transfer All:**
- Queues all listed files for sequential transfer
- Progress: "Transferring 1 of 3…"
- Each file offered as download/share after transfer, then removed from Pi

---

## 9. DATA CHANNEL MESSAGE REFERENCE — COMPLETE

Messages sent **App → Pi** (JSON):

| type | Payload | Action |
|------|---------|--------|
| `capture_request` | *(none)* | Pi captures JPEG from active camera slot |
| `record_start` | *(none)* | Pi starts MP4 recording |
| `record_stop` | *(none)* | Pi stops MP4 recording |
| `transfer_request` | `filename` | Pi sends named file via chunked binary |
| `transfer_complete` | `filename` | Pi deletes the file (ack of successful receipt) |
| `delete_request` | `filename` | Pi deletes file without transfer |
| `media_list_request` | *(none)* | Pi returns file list + disk usage |
| `camera_request` | `slot` | Pi adds camera video track to PC |
| `camera_stop` | *(none)* | Pi removes camera track |
| `camera_slots_request` | *(none)* | Pi returns slot list for camera switcher buttons |

Messages sent **Pi → App** (JSON unless noted):

| type | Payload | Meaning |
|------|---------|---------|
| `sensors` | sensor readings object | 5s live sensor push |
| `record_started` | `filename` | Recording has begun |
| `record_stopped` | `filename` | Recording stopped, file ready |
| `capture_done` | `filename, size_bytes` | Photo captured, transfer starting |
| `file_start` | `filename, mime, size_bytes, chunk_count` | Binary transfer beginning |
| *(binary)* | raw ArrayBuffer | File chunk (16 KB max) |
| `file_end` | `filename, checksum` | Transfer complete, awaiting ack |
| `delete_ack` | `filename` | File deleted from Pi |
| `media_list` | `files[], disk_percent` | List of files + disk usage |
| `camera_slots` | `slots[]` | Available camera slots for switcher |
| `storage_warning` | `percent_used, free_gb` | Disk >= 90% alert |

---

## 10. PI-SIDE IMPLEMENTATION ADDITIONS (live_session.py)

### 10.1 New functions required

```python
def check_disk_usage() -> dict:
    """Returns {percent_used, free_gb}. Uses shutil.disk_usage('/')."""

def list_media_files() -> list:
    """Scans RECORDING_PATH and captures/ subdir. Returns list of
    {filename, media_type, size_bytes, modified_at}."""

async def send_file_chunks(dc, filepath, filename):
    """Reads file in 16KB chunks, sends header → binary chunks → footer
    over the data channel. Handles bufferedamountlow backpressure."""

def delete_media_file(filename):
    """Deletes a file from RECORDING_PATH or captures/ subdir.
    Updates MEDIA_README.txt. Returns True on success."""

def update_media_readme():
    """Regenerates /home/d3kos/camera-recordings/MEDIA_README.txt
    with current file list, sizes, total usage, and SCP instructions."""
```

### 10.2 Data channel handler additions (inside handle_offer)

Extend `dc.onmessage` handler to process new message types:
- `capture_request` → call camera API localhost:8084/camera/capture → send file
- `record_start` → call localhost:8084/camera/record/start → ack
- `record_stop` → call localhost:8084/camera/record/stop → send file
- `transfer_request` → send_file_chunks()
- `transfer_complete` → delete_media_file()
- `delete_request` → delete_media_file() → send delete_ack
- `media_list_request` → list_media_files() → send media_list JSON

### 10.3 Storage check in poll_loop

Every 30 minutes (not every 3s poll), call check_disk_usage().
If active session and percent_used >= 90: send storage_warning on data channel.

---

## 11. APP-SIDE IMPLEMENTATION ADDITIONS

### 11.1 New API/helper functions in app.js

```javascript
// State for in-progress file transfer
let _transferMap = new Map();  // filename → {mime, totalChunks, chunks, received}

function handleBinaryChunk(arrayBuffer) { ... }
function handleFileStart(msg) { ... }
function handleFileEnd(msg) { ... }  // assembles Blob, triggers download/share
function saveMediaToDevice(blob, filename, mime) { ... }  // Web Share or <a download>
```

### 11.2 Live screen additions

- Record button (🔴) + Stop button in camera controls row
- Photo button (📷) in camera controls row
- Transfer progress overlay during file receipt
- "Media Library" button in camera row

### 11.3 New screens.media function

See Section 8 for full layout.
Navigated from: dashboard quick-action, live screen camera row, storage warning banner.
Requires active `_livePC` connection — shows "Go Live first" if not connected.

---

## 12. WHAT IS NOT IN SCOPE

- Storing media on HostPapa — never
- Streaming video continuously to HostPapa — never
- Automatic upload without user action (except fish detection which stores locally)
- Video editing or thumbnail generation on the Pi
- Cloud media library across sessions (media only accessible during live session)

---

## 13. OPEN OPERATOR DECISIONS

| # | Decision | Status |
|---|----------|--------|
| 1 | Maximum video clip length | Not specified — VLC records until user taps Stop. No enforced limit. Revisit if storage concerns arise. |
| 2 | Fish detection captures in media library | Yes — included in `media_list`, labeled "Fish" with 🐟 icon |
| 3 | "Transfer All" order | Newest first (matches library sort) |
| 4 | Checksum algorithm | MD5 — fast on Pi, sufficient for transfer integrity |

---

*This document is the governing reference for all media capture/transfer work.*
*Do not build or modify any media feature without updating this document first.*
*Version bump the header when any section changes.*
