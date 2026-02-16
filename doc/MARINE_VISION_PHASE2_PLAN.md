# Marine Vision Phase 2 - Fish Capture Mode Implementation Plan

**Date:** February 14, 2026
**Status:** PLANNING - Ready to Begin
**Dependencies:** Phase 1 Complete ✅
**System:** d3kOS Marine Monitoring v2.7

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites Check](#prerequisites-check)
3. [Implementation Phases](#implementation-phases)
4. [Technical Architecture](#technical-architecture)
5. [Model Selection & Training](#model-selection--training)
6. [API Design](#api-design)
7. [Testing Strategy](#testing-strategy)
8. [Timeline & Resources](#timeline--resources)

---

## Overview

### Phase 2 Goals

Implement AI-powered fish capture detection system that:
1. Detects when a person is holding a fish
2. Automatically captures high-resolution photo
3. Identifies fish species (offline)
4. Checks fishing regulations (size/bag limits)
5. Sends instant notifications to user's phone
6. Logs all captures with GPS coordinates

### Key Features

**AI Detection:**
- Person detection (YOLOv8)
- Fish detection (YOLOv8 custom model)
- Combined logic: "person holding fish"

**Species Identification:**
- ResNet50 or MobileNetV2 classifier
- Pretrained on fish species dataset
- Fine-tuned for local species (Ontario waters)

**Fishing Regulations:**
- Ontario MNR database integration
- Size limit checking
- Bag limit tracking
- Season checking

**Notifications:**
- Telegram bot integration
- Signal messaging (optional)
- Email notifications
- Include photo, species, and regulation info

**Event Logging:**
- SQLite database
- Timestamp, GPS coordinates, species
- Photo file path
- Regulation compliance status

---

## Prerequisites Check

### Phase 1 Status ✅

- [x] Camera streaming operational (10.42.0.100, 8 FPS)
- [x] Frame grabber providing 30 FPS background capture
- [x] Web interface established
- [x] Storage configured (`/home/d3kos/camera-recordings/`)
- [x] API framework (Flask on port 8084)
- [x] System stable and tested

### Hardware Status

**Current:**
- Raspberry Pi 4B (8GB RAM) ✅
- 16GB SD card (456MB free) ⚠️
- Reolink RLC-810A camera ✅
- Network connectivity ✅

**Storage Concern:**
- AI models: ~250MB
- Current free space: 456MB
- **Risk:** Tight squeeze, may need cleanup or 32GB SD card

**Recommendation:** Proceed with caution, monitor space closely

### Software Requirements

**To Install:**
```bash
# PyTorch (CPU version for Pi)
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# YOLOv8 (Ultralytics)
pip3 install ultralytics

# Image processing
pip3 install Pillow

# Notifications
pip3 install python-telegram-bot  # Telegram
pip3 install requests  # General HTTP

# Database
pip3 install sqlite3  # Usually included

# GPS (if not already installed)
pip3 install gpsd-py3
```

**Estimated Installation Size:** ~400MB

---

## Implementation Phases

### Phase 2.1: AI Model Setup (Day 1)

**Tasks:**
1. Install PyTorch and dependencies
2. Download YOLOv8n (nano) pretrained model
3. Test person detection on camera feed
4. Optimize inference for Pi performance
5. Create detection service framework

**Deliverables:**
- YOLOv8 person detection working
- Detection service on port 8086
- API endpoint: `/detect/person`

**Estimated Time:** 4-6 hours

---

### Phase 2.2: Fish Detection (Day 2)

**Tasks:**
1. Obtain fish detection dataset
   - COCO dataset has "fish" class (limited)
   - Consider: Aquarium fish, fishing datasets
   - Option: Train custom YOLOv8 model

2. Integrate fish detection
   - Combined person + fish detection
   - Bounding box overlap detection
   - "Holding fish" logic

3. Test detection accuracy

**Deliverables:**
- Fish detection model integrated
- Combined detection logic working
- API endpoint: `/detect/fish`

**Estimated Time:** 6-8 hours

---

### Phase 2.3: Auto-Capture Logic (Day 3)

**Tasks:**
1. Implement state machine
   - Idle → Detecting → Holding Fish → Cooldown
   - Prevent duplicate captures

2. Auto-capture trigger
   - Confidence threshold (e.g., >80%)
   - Hold duration (e.g., 2 seconds)
   - Capture high-res from main stream

3. Photo storage and naming
   - `catch_YYYYMMDD_HHMMSS.jpg`
   - Include metadata (detection confidence)

4. Web UI updates
   - Show latest catch
   - Capture gallery

**Deliverables:**
- Auto-capture working
- State machine implemented
- Web UI showing captures

**Estimated Time:** 4-6 hours

---

### Phase 2.4: Species Identification (Day 4)

**Tasks:**
1. Select classification model
   - ResNet50 (more accurate, slower)
   - MobileNetV2 (faster, less accurate)
   - Recommendation: Start with MobileNetV2

2. Find pretrained fish species model
   - FishNet dataset
   - Kaggle fish species datasets
   - Transfer learning from ImageNet

3. Fine-tune for Ontario species
   - Lake Trout, Bass, Pike, Walleye, etc.
   - 20-30 common species

4. Integrate with capture pipeline
   - Run classification on captured photo
   - Display species name and confidence

**Deliverables:**
- Species identification working
- API endpoint: `/identify/species`
- Web UI showing species name

**Estimated Time:** 8-10 hours

---

### Phase 2.5: Fishing Regulations (Day 5)

**Tasks:**
1. Create Ontario MNR regulations database
   - SQLite database
   - Species, size limits, bag limits, seasons
   - Location-based (FMZ zones)

2. GPS integration
   - Get current GPS coordinates
   - Determine FMZ zone
   - Lookup regulations

3. Regulation checking logic
   - Size estimation (from bounding box)
   - Bag limit tracking (daily count)
   - Season checking (date-based)

4. Display compliance status
   - Legal to keep
   - Too small (must release)
   - Over bag limit

**Deliverables:**
- Regulations database populated
- GPS-based zone detection
- Compliance checking working
- API endpoint: `/regulations/check`

**Estimated Time:** 6-8 hours

---

### Phase 2.6: Notifications (Day 6)

**Tasks:**
1. Set up Telegram bot
   - Create bot via @BotFather
   - Get bot token
   - Configure chat ID

2. Notification content
   - Photo attachment
   - Species name and confidence
   - Regulation info
   - GPS coordinates

3. Notification triggers
   - On successful capture
   - On species identification
   - On regulation check complete

4. Configuration UI
   - Enable/disable notifications
   - Select notification method
   - Enter bot token / credentials

**Deliverables:**
- Telegram notifications working
- Configuration page in settings
- API endpoint: `/notify/send`

**Estimated Time:** 4-6 hours

---

### Phase 2.7: Event Logging & Gallery (Day 7)

**Tasks:**
1. Create captures database
   - SQLite schema
   - Timestamp, GPS, species, photo path
   - Regulation compliance status

2. Web UI gallery
   - Grid view of all catches
   - Click to view details
   - Filter by date, species

3. Export functionality
   - CSV export of log
   - Photo download

4. Statistics dashboard
   - Total catches
   - Species breakdown
   - Favorite fishing spots (GPS heatmap)

**Deliverables:**
- Database logging working
- Web gallery page
- Export functionality
- Statistics dashboard

**Estimated Time:** 6-8 hours

---

## Technical Architecture

### Microservices Design

```
┌─────────────────────────────────────────────────────────────┐
│                      d3kOS Marine Vision                     │
└─────────────────────────────────────────────────────────────┘

┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ Camera Stream    │  │ Fish Detector    │  │ Species ID       │
│ Manager          │  │ Service          │  │ Service          │
│ Port 8084        │  │ Port 8086        │  │ Port 8087        │
│                  │  │                  │  │                  │
│ - RTSP stream    │  │ - YOLOv8 person  │  │ - ResNet50 or    │
│ - Frame grabber  │  │ - YOLOv8 fish    │  │   MobileNetV2    │
│ - Recording      │  │ - Holding logic  │  │ - Species        │
│ - Photo capture  │  │ - Auto-capture   │  │   classification │
└────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘
         │                     │                     │
         └─────────────────────┼─────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │ Marine Vision API   │
                    │ Port 8089           │
                    │                     │
                    │ - Unified API       │
                    │ - Web UI            │
                    │ - Notifications     │
                    │ - Regulations DB    │
                    │ - Event logging     │
                    └─────────────────────┘
```

### Service Descriptions

**1. Camera Stream Manager (Existing - Port 8084)**
- Already implemented in Phase 1
- Provides frames for detection
- High-res capture on demand

**2. Fish Detector Service (New - Port 8086)**
- Subscribes to frame grabber
- Runs YOLOv8 detection (person + fish)
- Triggers auto-capture
- API endpoints:
  - `GET /detect/status` - Detection active?
  - `POST /detect/start` - Start detection
  - `POST /detect/stop` - Stop detection
  - `GET /detect/latest` - Latest detection result

**3. Species ID Service (New - Port 8087)**
- Receives captured photos
- Runs classification model
- Returns species name + confidence
- API endpoints:
  - `POST /identify` - Identify species from photo
  - `GET /identify/species` - List supported species

**4. Marine Vision API (New - Port 8089)**
- Unified API for web UI
- Coordinates all services
- Handles notifications
- Regulations database
- Event logging
- API endpoints:
  - `GET /captures` - List all captures
  - `GET /captures/{id}` - Get capture details
  - `POST /notify` - Send notification
  - `GET /regulations/check` - Check regulation
  - `GET /stats` - Statistics

---

## Model Selection & Training

### Person Detection

**Model:** YOLOv8n (nano)
**Why:** Pretrained on COCO dataset, includes "person" class
**Size:** ~6MB
**Performance:** ~10-15 FPS on Pi 4B (CPU)

**No training required** - use pretrained weights

---

### Fish Detection

**Option 1: Use COCO "fish" class**
- Pretrained YOLOv8 includes generic "fish"
- Limited accuracy (trained on aquarium fish mostly)
- **Pro:** No training required
- **Con:** Lower accuracy for wild fish

**Option 2: Train custom YOLOv8 model**
- Collect/find fishing dataset (500-1000 images)
- Annotate fish bounding boxes
- Fine-tune YOLOv8n on custom dataset
- **Pro:** Higher accuracy for target use case
- **Con:** Requires training time and dataset

**Recommendation:** Start with Option 1, upgrade to Option 2 if needed

---

### Species Classification

**Dataset Options:**
1. **Fish4Knowledge** - 23 species, 27,000 images
2. **Large Scale Fish Dataset** - 9 species, 9,000 images
3. **Kaggle Fish Species** - Various datasets

**Target Species (Ontario Waters):**
- Lake Trout
- Brook Trout
- Rainbow Trout
- Smallmouth Bass
- Largemouth Bass
- Northern Pike
- Muskellunge
- Walleye
- Yellow Perch
- White Bass
- Black Crappie
- Bluegill
- Pumpkinseed
- Rock Bass
- Channel Catfish

**Model:** MobileNetV2
**Why:** Good balance of accuracy and speed on Pi
**Size:** ~14MB
**Training:** Transfer learning from ImageNet, fine-tune on fish species

**Training Plan:**
1. Start with pretrained MobileNetV2
2. Replace final layer (15 classes for Ontario species)
3. Train on combined dataset (Fish4Knowledge + custom)
4. Aim for >85% accuracy

---

## API Design

### Fish Detector Service (Port 8086)

```python
# GET /detect/status
{
  "active": true,
  "mode": "fish_capture",
  "detections_today": 5,
  "last_detection": "2026-02-14T14:23:15Z"
}

# POST /detect/start
{
  "mode": "fish_capture",  # or "idle"
  "confidence_threshold": 0.8
}
# Response: {"status": "started"}

# GET /detect/latest
{
  "timestamp": "2026-02-14T14:23:15Z",
  "person_detected": true,
  "person_confidence": 0.95,
  "fish_detected": true,
  "fish_confidence": 0.87,
  "holding_fish": true,
  "holding_confidence": 0.91,
  "bounding_boxes": {
    "person": [120, 50, 400, 600],
    "fish": [200, 300, 350, 450]
  }
}
```

### Species ID Service (Port 8087)

```python
# POST /identify
# Request: multipart/form-data with "image" field
# Response:
{
  "species": "Largemouth Bass",
  "scientific_name": "Micropterus salmoides",
  "confidence": 0.92,
  "alternatives": [
    {"species": "Smallmouth Bass", "confidence": 0.06},
    {"species": "White Bass", "confidence": 0.02}
  ],
  "processing_time_ms": 850
}

# GET /identify/species
{
  "supported_species": [
    {"common_name": "Largemouth Bass", "scientific_name": "Micropterus salmoides"},
    {"common_name": "Lake Trout", "scientific_name": "Salvelinus namaycush"},
    ...
  ]
}
```

### Marine Vision API (Port 8089)

```python
# GET /captures
{
  "captures": [
    {
      "id": 1,
      "timestamp": "2026-02-14T14:23:15Z",
      "species": "Largemouth Bass",
      "confidence": 0.92,
      "photo_path": "/home/d3kos/camera-recordings/catch_20260214_142315.jpg",
      "gps": {"lat": 44.5, "lon": -79.3},
      "regulation_status": "legal_to_keep",
      "size_cm": 45
    },
    ...
  ]
}

# GET /captures/1
{
  "id": 1,
  "timestamp": "2026-02-14T14:23:15Z",
  "species": "Largemouth Bass",
  "scientific_name": "Micropterus salmoides",
  "confidence": 0.92,
  "photo_path": "/home/d3kos/camera-recordings/catch_20260214_142315.jpg",
  "photo_url": "/captures/1/photo",
  "gps": {
    "latitude": 44.5,
    "longitude": -79.3,
    "fmz_zone": "Zone 15"
  },
  "detection": {
    "person_confidence": 0.95,
    "fish_confidence": 0.87,
    "holding_confidence": 0.91
  },
  "regulations": {
    "status": "legal_to_keep",
    "min_size_cm": 35,
    "max_size_cm": null,
    "daily_limit": 6,
    "season_open": true,
    "caught_today": 1
  }
}

# POST /notify
{
  "capture_id": 1,
  "method": "telegram",  # or "signal", "email"
  "message": "Caught a Largemouth Bass! 45cm, legal to keep."
}
# Response: {"status": "sent", "message_id": "12345"}

# GET /regulations/check
# Query params: species=bass&size=45&lat=44.5&lon=-79.3
{
  "species": "Largemouth Bass",
  "fmz_zone": "Zone 15",
  "size_cm": 45,
  "regulations": {
    "min_size_cm": 35,
    "max_size_cm": null,
    "daily_limit": 6,
    "season": "open year-round",
    "status": "legal_to_keep"
  }
}

# GET /stats
{
  "total_catches": 23,
  "species_breakdown": {
    "Largemouth Bass": 8,
    "Lake Trout": 6,
    "Northern Pike": 5,
    "Yellow Perch": 4
  },
  "catches_this_week": 5,
  "favorite_spot": {"lat": 44.5, "lon": -79.3, "catches": 12}
}
```

---

## Testing Strategy

### Unit Tests

**Detection Service:**
- Test person detection accuracy (>90%)
- Test fish detection accuracy (>80%)
- Test holding logic (various poses)

**Species ID:**
- Test classification accuracy (>85%)
- Test inference speed (<1 second)
- Test with edge cases (multiple fish, obscured fish)

**Regulations:**
- Test zone detection
- Test size limit checking
- Test bag limit tracking

### Integration Tests

1. End-to-end capture flow
2. Notification delivery
3. Database logging
4. Web UI display

### Field Tests

1. Test with real fish catches
2. Test different lighting conditions
3. Test different fish sizes/species
4. Test GPS accuracy

---

## Timeline & Resources

### Estimated Timeline

| Phase | Tasks | Estimated Time | Dependencies |
|-------|-------|----------------|--------------|
| 2.1 | AI Model Setup | 4-6 hours | Phase 1 complete |
| 2.2 | Fish Detection | 6-8 hours | Phase 2.1 |
| 2.3 | Auto-Capture | 4-6 hours | Phase 2.2 |
| 2.4 | Species ID | 8-10 hours | Phase 2.3 |
| 2.5 | Regulations | 6-8 hours | Phase 2.4 |
| 2.6 | Notifications | 4-6 hours | Phase 2.5 |
| 2.7 | Logging/Gallery | 6-8 hours | Phase 2.6 |
| **Total** | | **38-52 hours** | **~5-7 days** |

### Resource Requirements

**Storage (SD Card):**
- AI Models: ~250MB
- Current free: 456MB
- **Status:** Tight but possible
- **Risk:** High - may need SD card cleanup or upgrade

**Compute (Pi 4B):**
- YOLOv8n inference: ~10-15 FPS (CPU)
- Classification: <1 second per image
- **Status:** Adequate for Phase 2
- **Note:** Coral USB Accelerator would improve performance

**Network:**
- Notifications require internet
- Regulation database can be offline (SQLite)
- **Status:** Adequate

### Optional Enhancements

1. **Coral USB Accelerator** ($60)
   - 5-10× faster inference
   - 50+ FPS detection possible
   - Recommended for production

2. **Larger SD Card** (32GB minimum, 128GB recommended)
   - More space for models
   - More space for recordings
   - Healthier system operation

3. **Custom Fish Dataset**
   - Improve detection accuracy
   - Train on actual fishing scenarios
   - Requires time and effort

---

## Risk Assessment

### High Priority Risks

**1. Storage Space (HIGH)**
- Current: 456MB free
- Required: ~250MB models + overhead
- **Mitigation:** Clean up unused files, or upgrade to 32GB SD card

**2. Model Performance (MEDIUM)**
- Pi 4B CPU inference may be slow
- Detection may miss some fish
- **Mitigation:** Optimize model, consider Coral accelerator

**3. Species Accuracy (MEDIUM)**
- Generic fish models may not work well
- Ontario species may differ from training data
- **Mitigation:** Start with pretrained, fine-tune as needed

### Medium Priority Risks

**4. GPS Accuracy (LOW-MEDIUM)**
- GPS may not have fix indoors/urban areas
- FMZ zone boundaries may be imprecise
- **Mitigation:** Manual zone override in settings

**5. Notification Reliability (LOW)**
- Internet connection required
- Telegram/Signal API limits
- **Mitigation:** Queue notifications, retry on failure

---

## Success Criteria

Phase 2 is complete when:

1. ✅ Person + fish detection working with >80% accuracy
2. ✅ Auto-capture triggers correctly
3. ✅ Species identification working with >75% accuracy
4. ✅ Regulation checking functional
5. ✅ Notifications delivered successfully
6. ✅ Event logging and gallery working
7. ✅ Web UI displays all Phase 2 features
8. ✅ System tested with at least 5 real fish catches

---

## Next Steps

**Before Starting Phase 2:**
1. Check SD card space: `df -h /`
2. Clean up if needed: Remove old logs, temp files
3. Consider: Order 32GB or 128GB SD card if budget allows
4. Review: Ensure Phase 1 stable and working

**To Begin Phase 2.1:**
1. Install PyTorch and dependencies
2. Download YOLOv8n model
3. Create fish detector service skeleton
4. Test person detection on live feed

**Ready to proceed when user approves!**

---

**Document Created:** February 14, 2026
**Author:** Claude (d3kOS Development Assistant)
**Version:** 1.0
