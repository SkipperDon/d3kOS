# Marine Vision Fish Identification - 4 Parallel Sessions Plan

**Goal:** Complete fish detection and species identification for Marine Vision system

**Current Status:**
- ✅ Phase 1: Camera streaming (Reolink RLC-810A working)
- ✅ Phase 2.1: YOLOv8n person detection (working)
- ⚠️ Phase 2.2: Fish detection (BLOCKED - needs custom model)
- ✅ Phase 2.6: Telegram notifications (ready)

**Target:** Fully functional fish capture with automatic species identification

---

## Session Overview

| Session ID | Domain | Focus | Est. Time | Priority |
|------------|--------|-------|-----------|----------|
| **Session-Fish-1** | Fish Detection Model | Get/train fish detection model | 4-6 hours | HIGH |
| **Session-Fish-2** | Species Identification | Implement species ID system | 6-8 hours | HIGH |
| **Session-Fish-3** | Auto-Capture & Integration | Complete capture pipeline | 4-6 hours | MEDIUM |
| **Session-Fish-4** | Testing & Optimization | Performance tuning, accuracy | 3-4 hours | MEDIUM |

**Total Estimated Time:** 17-24 hours (2-3 days with parallel sessions)

---

## Session-Fish-1: Fish Detection Model

**Agent ID:** `Session-Fish-1-Detection-Model`
**Domain:** Marine Vision - Model Acquisition
**Status:** READY
**Priority:** HIGH (blocks other sessions)

### Objective
Acquire or train a fish detection model that can replace the COCO proxy approach.

### Tasks (6 total)

#### Task 1: Evaluate Pre-trained Fish Models (2 hours)
**Goal:** Find existing fish detection models to avoid training from scratch

**Subtasks:**
1. Search Roboflow Universe for freshwater fish detection models
   - Filter: Freshwater, Object Detection, ONNX format
   - Target species: Bass, Pike, Walleye, Perch, Trout, Sunfish
2. Check Hugging Face Hub for fish detection models
   - Keywords: "fish detection", "aquatic species", "marine object detection"
3. Evaluate TensorFlow Hub and PyTorch Hub
4. Check academic datasets (Open Images, COCO-Fish extensions)
5. Document findings: model accuracy, format, license, size

**Success Criteria:**
- Find at least 2 suitable pre-trained models OR
- Confirm need for custom training

**Deliverables:**
- `FISH_MODELS_EVALUATION.md` - Comparison table of available models
- Download links and licenses documented

---

#### Task 2: Model Format Conversion (1 hour)
**Goal:** Convert selected model to ONNX format for Raspberry Pi

**Options:**
- **If PyTorch model found:** Use `torch.onnx.export()`
- **If TensorFlow model found:** Use `tf2onnx` converter
- **If Roboflow model:** Direct ONNX export available

**Commands:**
```bash
# PyTorch to ONNX
python3 convert_to_onnx.py --model fish_detector.pt --output fish_detector.onnx

# TensorFlow to ONNX
python3 -m tf2onnx.convert --saved-model fish_model/ --output fish_detector.onnx
```

**Success Criteria:**
- Fish detection model in ONNX format (<50MB preferred)
- Compatible with ONNX Runtime 1.24.1

**Deliverables:**
- `fish_detector.onnx` or `fish_yolov8.onnx`
- Conversion script if custom conversion needed

---

#### Task 3: Custom Dataset Collection (IF NEEDED - 2 hours)
**Goal:** Collect fish images for custom training (only if no suitable pre-trained model)

**Dataset Requirements:**
- 500-1000 images minimum
- Freshwater fish species (Ontario focus)
- Annotations: bounding boxes + species labels
- Diverse conditions: lighting, angles, backgrounds

**Sources:**
1. **Roboflow Public Datasets:**
   - Search "freshwater fish", "bass", "pike", etc.
   - Download and combine compatible datasets
2. **Open Images Dataset:**
   - Filter for fish-related classes
3. **iNaturalist API:**
   - Query observations with images
   - Filter: Ontario region, fish taxonomy
4. **Manual Collection:**
   - Fishing forums, YouTube screenshots
   - User-contributed photos (with permission)

**Tools:**
- Roboflow annotation tool
- LabelImg for bounding boxes
- CVAT for efficient batch annotation

**Success Criteria:**
- Dataset with 500+ annotated fish images
- 80/20 train/validation split
- Balanced species distribution

**Deliverables:**
- `fish_dataset/` directory structure
- `dataset.yaml` for YOLOv8 training
- `DATASET_README.md` with sources and licenses

---

#### Task 4: Model Training (IF NEEDED - 4-6 hours)
**Goal:** Train custom YOLOv8 fish detection model

**Approach:** Transfer learning from YOLOv8n pretrained on COCO

**Training Script:**
```python
from ultralytics import YOLO

# Load pretrained YOLOv8n
model = YOLO('yolov8n.pt')

# Train on fish dataset
results = model.train(
    data='fish_dataset/dataset.yaml',
    epochs=100,
    imgsz=640,
    batch=16,
    device='cpu',  # Or 'cuda' if GPU available
    patience=20,
    save=True,
    project='fish_training',
    name='fish_yolov8n'
)

# Export to ONNX
model.export(format='onnx')
```

**Training Environment:**
- **Option 1:** Google Colab (free GPU, 12 hours max)
- **Option 2:** Local Ubuntu machine (CPU, overnight)
- **Option 3:** AWS EC2 spot instance (cost: ~$1-2)

**Training Time:**
- GPU: 1-2 hours (100 epochs)
- CPU: 6-12 hours (100 epochs)

**Success Criteria:**
- mAP@0.5 > 0.7 (70% accuracy)
- Model size < 50MB
- Inference time < 3 seconds on Pi 4B

**Deliverables:**
- `fish_yolov8n.onnx` - Trained model
- `training_results/` - Loss curves, metrics
- `TRAINING_REPORT.md` - Hyperparameters, accuracy

---

#### Task 5: Pi Deployment & Testing (1 hour)
**Goal:** Deploy fish detection model to Raspberry Pi

**Steps:**
1. Copy model to Pi: `/opt/d3kos/models/marine-vision/fish_detector.onnx`
2. Update `fish_detector.py` to load new model
3. Test inference speed and accuracy
4. Compare with person detection baseline

**Testing:**
```bash
# Test with sample fish image
python3 /opt/d3kos/services/marine-vision/fish_detector.py \
  --image /home/d3kos/test_images/bass.jpg \
  --model /opt/d3kos/models/marine-vision/fish_detector.onnx
```

**Performance Targets:**
- Inference time: < 3 seconds
- Memory usage: < 500MB
- Detection accuracy: > 70%

**Success Criteria:**
- Model loads successfully on Pi
- Detects fish in test images
- Performance within acceptable limits

**Deliverables:**
- Model deployed to Pi
- `DEPLOYMENT_TEST_RESULTS.md`

---

#### Task 6: Documentation & Handoff (30 min)
**Goal:** Document model selection/training process for other sessions

**Documents to Create:**
1. `SESSION_FISH_1_COMPLETE.md` - Session summary
2. `FISH_MODEL_README.md` - Model details, usage, limitations
3. Update `.session-status.md`

**Model Metadata to Document:**
- Model source (pre-trained or custom)
- Training data (if custom)
- Supported species (if known)
- Accuracy metrics
- Inference performance on Pi
- License and attribution

**Success Criteria:**
- Complete documentation for Session-Fish-2 to use
- Model ready for species identification integration

**Deliverables:**
- Documentation files
- Session marked complete

---

### Session-Fish-1 Success Criteria

- [ ] Fish detection model acquired (pre-trained or custom)
- [ ] Model in ONNX format, < 50MB
- [ ] Deployed to Raspberry Pi
- [ ] Inference time < 3 seconds on Pi 4B
- [ ] Detection accuracy > 70% on test images
- [ ] Documentation complete

---

### Session-Fish-1 Dependencies

**Requires:**
- None (can start immediately)

**Blocks:**
- Session-Fish-2 (needs model for species ID)
- Session-Fish-3 (needs model for auto-capture)

---

## Session-Fish-2: Species Identification

**Agent ID:** `Session-Fish-2-Species-ID`
**Domain:** Marine Vision - Species Classification
**Status:** READY (blocked by Session-Fish-1)
**Priority:** HIGH

### Objective
Implement species identification system that classifies detected fish by species.

### Tasks (5 total)

#### Task 1: Species Classification Approach (1 hour)
**Goal:** Determine best approach for species identification

**Options:**

**Option A: Two-Stage (Detection + Classification)**
- Stage 1: Fish detection (YOLOv8) → bounding box
- Stage 2: Species classification (ResNet/EfficientNet) → species label
- Pros: More accurate, modular
- Cons: Slower (2 models), more complex

**Option B: Single-Stage (Detection with Species)**
- YOLOv8 with multiple classes (bass, pike, walleye, etc.)
- Detection and classification in one pass
- Pros: Faster, simpler
- Cons: Requires species-labeled training data

**Option C: Hybrid (Detection + API)**
- YOLOv8 detects fish, crops image
- Send crop to external API (iNaturalist, FishBase)
- Pros: No local species model needed, very accurate
- Cons: Requires internet, slower, API costs

**Recommendation:** Start with Option B (single-stage) if training data available, otherwise Option A.

**Success Criteria:**
- Approach selected and documented
- Trade-offs understood
- Implementation plan created

**Deliverables:**
- `SPECIES_ID_APPROACH.md` - Decision and rationale

---

#### Task 2: Species Dataset Preparation (2-3 hours)
**Goal:** Prepare species-labeled dataset for training/fine-tuning

**Target Species (Ontario Freshwater):**
1. **Bass** (Largemouth, Smallmouth)
2. **Pike** (Northern Pike, Muskellunge)
3. **Walleye**
4. **Perch** (Yellow Perch)
5. **Trout** (Lake Trout, Rainbow Trout)
6. **Sunfish** (Bluegill, Pumpkinseed)
7. **Catfish** (Channel Catfish)
8. **Salmon** (Chinook, Coho)
9. **Crappie** (Black Crappie, White Crappie)
10. **Whitefish** (Lake Whitefish)

**Dataset Sources:**
1. **iNaturalist API:**
   ```python
   # Query observations with photos
   import requests
   params = {
       'taxon_name': 'Micropterus salmoides',  # Largemouth Bass
       'place_id': 6883,  # Ontario
       'quality_grade': 'research',
       'per_page': 200
   }
   response = requests.get('https://api.inaturalist.org/v1/observations', params=params)
   ```

2. **FishBase API:**
   - Download reference images for each species
   - High-quality photos with metadata

3. **Roboflow Fish Datasets:**
   - Search for species-specific datasets
   - Combine compatible datasets

**Dataset Structure:**
```
species_dataset/
├── train/
│   ├── bass/
│   ├── pike/
│   ├── walleye/
│   └── ...
├── val/
│   ├── bass/
│   ├── pike/
│   └── ...
└── dataset.yaml
```

**Success Criteria:**
- 100+ images per species (1000+ total)
- 80/20 train/val split
- Consistent image quality and annotations

**Deliverables:**
- `species_dataset/` directory
- `dataset.yaml` configuration
- `SPECIES_DATASET_README.md`

---

#### Task 3: Species Classification Model (3-4 hours)
**Goal:** Train or fine-tune species classification model

**Approach A: Fine-tune ResNet50**
```python
import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D

# Load pretrained ResNet50
base_model = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

# Add classification head
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(512, activation='relu')(x)
predictions = Dense(10, activation='softmax')(x)  # 10 species

model = tf.keras.Model(inputs=base_model.input, outputs=predictions)

# Freeze base layers
for layer in base_model.layers:
    layer.trainable = False

# Compile and train
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.fit(train_data, epochs=20, validation_data=val_data)

# Export to ONNX
import tf2onnx
tf2onnx.convert.from_keras(model, output_path='species_classifier.onnx')
```

**Approach B: YOLOv8 with Species Classes**
```python
from ultralytics import YOLO

# Train YOLOv8 with species classes
model = YOLO('yolov8n.pt')
results = model.train(
    data='species_dataset/dataset.yaml',  # Includes species labels
    epochs=100,
    imgsz=640,
    batch=16
)

# Export
model.export(format='onnx')
```

**Success Criteria:**
- Classification accuracy > 80% on validation set
- Model size < 100MB (ResNet50) or < 50MB (YOLOv8)
- Inference time < 2 seconds on Pi

**Deliverables:**
- `species_classifier.onnx` or `fish_yolov8_species.onnx`
- `training_metrics.json`
- `SPECIES_MODEL_REPORT.md`

---

#### Task 4: Integration with Fish Detector (2 hours)
**Goal:** Integrate species identification into fish_detector.py

**Code Changes:**
```python
# /opt/d3kos/services/marine-vision/fish_detector.py

import onnxruntime as ort

class FishDetector:
    def __init__(self):
        # Load fish detection model
        self.detection_session = ort.InferenceSession('/opt/d3kos/models/marine-vision/fish_detector.onnx')

        # Load species classification model
        self.species_session = ort.InferenceSession('/opt/d3kos/models/marine-vision/species_classifier.onnx')

        self.species_labels = [
            'bass', 'pike', 'walleye', 'perch', 'trout',
            'sunfish', 'catfish', 'salmon', 'crappie', 'whitefish'
        ]

    def detect_and_classify(self, frame):
        # Stage 1: Detect fish
        detections = self.detect_fish(frame)

        # Stage 2: Classify each detected fish
        results = []
        for det in detections:
            x1, y1, x2, y2, conf = det
            fish_crop = frame[y1:y2, x1:x2]

            # Classify species
            species_id, species_conf = self.classify_species(fish_crop)
            species_name = self.species_labels[species_id]

            results.append({
                'bbox': [x1, y1, x2, y2],
                'detection_conf': conf,
                'species': species_name,
                'species_conf': species_conf
            })

        return results
```

**API Endpoint Update:**
```python
# POST /detect/frame
{
    "detections": [
        {
            "bbox": [100, 150, 300, 400],
            "detection_confidence": 0.92,
            "species": "bass",
            "species_confidence": 0.87
        }
    ],
    "capture_triggered": true,
    "capture_id": "CAP-20260218-001"
}
```

**Success Criteria:**
- Species classification integrated seamlessly
- API returns species name and confidence
- Performance acceptable (< 5 seconds total)

**Deliverables:**
- Updated `fish_detector.py`
- Updated API documentation
- Integration tests passing

---

#### Task 5: Species Database & Regulations (1 hour)
**Goal:** Create species database with fishing regulations

**Database Schema:**
```sql
CREATE TABLE species (
    species_id INTEGER PRIMARY KEY,
    common_name VARCHAR(50),
    scientific_name VARCHAR(100),
    family VARCHAR(50),
    description TEXT,
    typical_size_min INTEGER,  -- cm
    typical_size_max INTEGER,
    image_url VARCHAR(255)
);

CREATE TABLE regulations (
    regulation_id INTEGER PRIMARY KEY,
    species_id INTEGER,
    region VARCHAR(50),  -- 'Ontario', 'Zone 15', etc.
    season_start DATE,
    season_end DATE,
    size_limit_min INTEGER,  -- cm
    size_limit_max INTEGER,
    bag_limit INTEGER,
    possession_limit INTEGER,
    notes TEXT,
    FOREIGN KEY (species_id) REFERENCES species(species_id)
);
```

**Data Sources:**
1. **Ontario MNR Fishing Regulations:**
   - https://www.ontario.ca/document/ontario-fishing-regulations-summary
   - Parse season dates, size limits, bag limits

2. **FishBase API:**
   - Species descriptions, typical sizes
   - Scientific names and taxonomy

**Populate Database:**
```python
import sqlite3

conn = sqlite3.connect('/opt/d3kos/data/marine-vision/species.db')
cursor = conn.cursor()

# Insert species
cursor.execute('''
    INSERT INTO species VALUES
    (1, 'Largemouth Bass', 'Micropterus salmoides', 'Centrarchidae',
     'Popular sportfish with distinctive jaw extending past eye',
     25, 60, '/species/bass.jpg')
''')

# Insert regulations (Ontario, Zone 15)
cursor.execute('''
    INSERT INTO regulations VALUES
    (1, 1, 'Ontario Zone 15', '2026-06-21', '2027-03-15',
     NULL, NULL, 6, 6, 'Bass season: 4th Saturday in June to March 15')
''')

conn.commit()
```

**Success Criteria:**
- Database with 10 Ontario species
- Regulations for each species (Zone 15)
- API endpoint to query regulations

**Deliverables:**
- `species.db` SQLite database
- `populate_species_db.py` script
- `SPECIES_DATABASE_SCHEMA.md`

---

### Session-Fish-2 Success Criteria

- [ ] Species classification approach selected
- [ ] Species-labeled dataset prepared (100+ per species)
- [ ] Classification model trained (>80% accuracy)
- [ ] Integration with fish detection complete
- [ ] Species database created with regulations
- [ ] API returns species identification

---

### Session-Fish-2 Dependencies

**Requires:**
- Session-Fish-1 complete (fish detection model)

**Blocks:**
- Session-Fish-3 (needs species ID for capture metadata)

---

## Session-Fish-3: Auto-Capture & Integration

**Agent ID:** `Session-Fish-3-Auto-Capture`
**Domain:** Marine Vision - Capture Pipeline
**Status:** READY (blocked by Session-Fish-2)
**Priority:** MEDIUM

### Objective
Complete the automatic fish capture pipeline with species metadata and notification integration.

### Tasks (5 total)

#### Task 1: Auto-Capture Logic (1 hour)
**Goal:** Implement automatic photo capture when person + fish detected

**Trigger Conditions:**
```python
def should_trigger_capture(detections):
    """
    Auto-capture when:
    1. Person detected (holding fish)
    2. Fish detected (in person's hands)
    3. Both confidences > 70%
    4. No capture in last 5 seconds (cooldown)
    """
    has_person = any(d['class'] == 'person' and d['confidence'] > 0.7 for d in detections)
    has_fish = any(d['species'] and d['species_confidence'] > 0.7 for d in detections)

    cooldown_ok = (time.time() - last_capture_time) > 5

    return has_person and has_fish and cooldown_ok
```

**Capture Process:**
1. Detect person + fish
2. Get high-resolution frame from camera
3. Run fish detection/classification on full-res image
4. Save image with metadata
5. Create database entry
6. Trigger notification

**Success Criteria:**
- Auto-capture triggers correctly
- No false positives (empty hands, background objects)
- Cooldown prevents duplicate captures

**Deliverables:**
- Updated `fish_detector.py` with auto-capture logic
- `AUTO_CAPTURE_LOGIC.md` documentation

---

#### Task 2: Capture Metadata & Storage (1 hour)
**Goal:** Save captures with complete metadata

**Metadata Schema:**
```python
capture_metadata = {
    'capture_id': 'CAP-20260218-092341',
    'timestamp': '2026-02-18T09:23:41Z',
    'image_path': '/home/d3kos/camera-recordings/captures/CAP-20260218-092341.jpg',
    'detection': {
        'person_confidence': 0.95,
        'fish_bbox': [120, 200, 380, 520],
        'fish_confidence': 0.89
    },
    'species': {
        'name': 'bass',
        'common_name': 'Largemouth Bass',
        'scientific_name': 'Micropterus salmoides',
        'confidence': 0.87
    },
    'location': {
        'latitude': 44.4167,
        'longitude': -79.3333,
        'gps_accuracy': 3.5
    },
    'regulations': {
        'season_open': True,
        'size_limit_min': None,
        'size_limit_max': None,
        'bag_limit': 6,
        'notes': 'Bass season: 4th Saturday in June to March 15'
    },
    'camera': {
        'resolution': '3840x2160',
        'camera_id': 'reolink-rlc-810a'
    }
}
```

**Database Entry:**
```sql
INSERT INTO captures (
    capture_id, timestamp, image_path,
    species_id, species_confidence,
    person_confidence, fish_confidence,
    latitude, longitude, gps_accuracy,
    season_open, bag_limit, size_limit_min, size_limit_max
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
```

**Success Criteria:**
- Complete metadata saved for each capture
- GPS coordinates from Signal K
- Regulations looked up from database
- Image saved in captures directory

**Deliverables:**
- Updated database schema with regulations fields
- Metadata save function
- `CAPTURE_METADATA_FORMAT.md`

---

#### Task 3: Notification Integration (2 hours)
**Goal:** Send fish capture notifications via Telegram (Phase 2.6)

**Notification Message Format:**
```
🎣 Fish Caught!

Species: Largemouth Bass (Micropterus salmoides)
Confidence: 87%

📍 Location: 44.4167°N, 79.3333°W
📅 Time: Feb 18, 2026 9:23 AM

🎯 Fishing Regulations (Ontario Zone 15):
✅ Season: OPEN (June 21 - March 15)
📏 Size Limit: None
🎒 Bag Limit: 6 fish
📦 Possession Limit: 6 fish

[View on Google Maps]
https://www.google.com/maps?q=44.4167,-79.3333

Capture ID: CAP-20260218-092341
```

**Integration Code:**
```python
# /opt/d3kos/services/marine-vision/fish_detector.py

import requests

def send_fish_notification(capture_id, capture_data):
    """Send Telegram notification for fish capture"""

    # Prepare notification payload
    payload = {
        'type': 'fish_capture',
        'capture_data': {
            'capture_id': capture_id,
            'timestamp': capture_data['timestamp'],
            'species': capture_data['species']['common_name'],
            'scientific_name': capture_data['species']['scientific_name'],
            'species_confidence': capture_data['species']['confidence'],
            'gps': {
                'latitude': capture_data['location']['latitude'],
                'longitude': capture_data['location']['longitude']
            },
            'regulations': capture_data['regulations']
        },
        'photo_path': capture_data['image_path']
    }

    # Send to notification manager
    response = requests.post(
        'http://localhost:8088/notify/send',
        json=payload,
        timeout=5
    )

    if response.status_code == 200:
        print(f"✓ Notification sent for capture {capture_id}")
    else:
        print(f"⚠ Notification failed: {response.text}")
```

**Notification Manager Update:**
```python
# /opt/d3kos/services/marine-vision/notification_manager.py

def format_fish_capture_message(capture_data):
    """Format Telegram message for fish capture"""

    species = capture_data['species']
    scientific = capture_data['scientific_name']
    confidence = capture_data['species_confidence']

    gps = capture_data['gps']
    lat = gps['latitude']
    lon = gps['longitude']

    regs = capture_data['regulations']

    message = f"""🎣 Fish Caught!

Species: {species} ({scientific})
Confidence: {confidence:.0%}

📍 Location: {lat:.4f}°N, {lon:.4f}°W
📅 Time: {capture_data['timestamp']}

🎯 Fishing Regulations (Ontario Zone 15):
{'✅' if regs['season_open'] else '❌'} Season: {'OPEN' if regs['season_open'] else 'CLOSED'}
📏 Size Limit: {regs['size_limit_min'] or 'None'} - {regs['size_limit_max'] or 'None'} cm
🎒 Bag Limit: {regs['bag_limit']} fish
{regs['notes']}

[View on Google Maps](https://www.google.com/maps?q={lat},{lon})

Capture ID: {capture_data['capture_id']}
"""

    return message
```

**Success Criteria:**
- Notifications sent automatically on fish capture
- Photo attached to Telegram message
- Regulations displayed correctly
- Google Maps link functional

**Deliverables:**
- Updated `fish_detector.py` with notification calls
- Updated `notification_manager.py` with fish message formatting
- Test notifications sent successfully

---

#### Task 4: Web UI Integration (1 hour)
**Goal:** Update Marine Vision web UI to display species information

**UI Updates:**
```html
<!-- /var/www/html/marine-vision.html -->

<div class="capture-card">
    <img src="/captures/CAP-20260218-092341.jpg" alt="Fish Capture">

    <div class="capture-info">
        <h3>🎣 Largemouth Bass</h3>
        <p class="scientific-name">Micropterus salmoides</p>

        <div class="confidence">
            <span class="label">Species Confidence:</span>
            <span class="value">87%</span>
        </div>

        <div class="location">
            <span class="label">📍 Location:</span>
            <span class="value">44.4167°N, 79.3333°W</span>
        </div>

        <div class="timestamp">
            <span class="label">📅 Time:</span>
            <span class="value">Feb 18, 2026 9:23 AM</span>
        </div>

        <div class="regulations">
            <h4>Fishing Regulations</h4>
            <div class="reg-item">
                <span class="label">Season:</span>
                <span class="value open">✅ OPEN</span>
            </div>
            <div class="reg-item">
                <span class="label">Bag Limit:</span>
                <span class="value">6 fish</span>
            </div>
        </div>

        <div class="actions">
            <button onclick="viewOnMap(44.4167, -79.3333)">View on Map</button>
            <button onclick="deleteCapture('CAP-20260218-092341')">Delete</button>
        </div>
    </div>
</div>
```

**API Endpoint:**
```python
# GET /captures?species=bass&limit=20
{
    "captures": [
        {
            "capture_id": "CAP-20260218-092341",
            "timestamp": "2026-02-18T09:23:41Z",
            "image_url": "/captures/CAP-20260218-092341.jpg",
            "species": {
                "name": "bass",
                "common_name": "Largemouth Bass",
                "scientific_name": "Micropterus salmoides",
                "confidence": 0.87
            },
            "location": {"latitude": 44.4167, "longitude": -79.3333},
            "regulations": {...}
        }
    ]
}
```

**Success Criteria:**
- Captures display species information
- Regulations shown for each capture
- Filter by species working
- Map view integration

**Deliverables:**
- Updated `marine-vision.html`
- CSS styling for species cards
- JavaScript for map view

---

#### Task 5: Testing & Validation (1 hour)
**Goal:** End-to-end testing of capture pipeline

**Test Scenarios:**
1. **Person holding fish** → Auto-capture triggers, species identified, notification sent
2. **Person with empty hands** → No capture (fish not detected)
3. **Fish on deck (no person)** → Capture triggers, species identified, no person in metadata
4. **Multiple fish in frame** → Multiple captures created
5. **Unknown species** → Capture created with "unknown" species, notification sent
6. **GPS unavailable** → Capture created with null GPS coordinates
7. **Rapid captures** → Cooldown prevents duplicate captures

**Performance Testing:**
- Capture pipeline latency: < 5 seconds
- Database write time: < 100ms
- Notification delivery: < 3 seconds
- Storage usage: ~2-5MB per capture

**Success Criteria:**
- All test scenarios pass
- No crashes or errors
- Performance within acceptable limits
- User experience smooth

**Deliverables:**
- `CAPTURE_PIPELINE_TEST_RESULTS.md`
- Test images and expected results
- Performance metrics documented

---

### Session-Fish-3 Success Criteria

- [ ] Auto-capture logic implemented
- [ ] Complete metadata saved for captures
- [ ] Telegram notifications working
- [ ] Web UI displays species information
- [ ] End-to-end testing complete
- [ ] Pipeline latency < 5 seconds

---

### Session-Fish-3 Dependencies

**Requires:**
- Session-Fish-2 complete (species identification)
- Phase 2.6 complete (Telegram notifications) - ALREADY DONE ✅

**Blocks:**
- Session-Fish-4 (needs working pipeline for optimization)

---

## Session-Fish-4: Testing & Optimization

**Agent ID:** `Session-Fish-4-Optimization`
**Domain:** Marine Vision - Performance Tuning
**Status:** READY (blocked by Session-Fish-3)
**Priority:** MEDIUM

### Objective
Optimize fish detection and species identification for accuracy, speed, and reliability.

### Tasks (4 total)

#### Task 1: Accuracy Testing & Improvement (1.5 hours)
**Goal:** Measure and improve species identification accuracy

**Test Dataset:**
- 100 test images (unseen during training)
- 10 images per species
- Variety of lighting, angles, backgrounds

**Accuracy Metrics:**
```python
# Confusion matrix
species_accuracy = {
    'bass': {'correct': 9, 'total': 10, 'accuracy': 0.90},
    'pike': {'correct': 8, 'total': 10, 'accuracy': 0.80},
    'walleye': {'correct': 7, 'total': 10, 'accuracy': 0.70},
    # ... all species
}

# Overall metrics
overall_accuracy = 0.85  # 85/100 correct
precision = 0.87
recall = 0.83
f1_score = 0.85
```

**Improvement Strategies:**
1. **Data Augmentation:**
   - Add rotations, flips, brightness variations
   - Increases effective training data size
2. **Threshold Tuning:**
   - Adjust confidence thresholds for each species
   - Trade precision for recall or vice versa
3. **Model Ensemble:**
   - Combine predictions from multiple models
   - Improves accuracy but increases inference time
4. **Hard Negative Mining:**
   - Collect misclassified examples
   - Retrain with challenging samples

**Success Criteria:**
- Overall accuracy > 85%
- Per-species accuracy > 70%
- False positive rate < 5%

**Deliverables:**
- `ACCURACY_TEST_RESULTS.md`
- Confusion matrix visualization
- Improved model (if retrained)

---

#### Task 2: Performance Optimization (1 hour)
**Goal:** Reduce inference time and memory usage

**Current Performance (Baseline):**
- Fish detection: ~2 seconds
- Species classification: ~1 second
- Total pipeline: ~5 seconds
- Memory usage: ~500MB

**Optimization Techniques:**

**1. Model Quantization:**
```python
# Convert ONNX model to INT8 quantization
from onnxruntime.quantization import quantize_dynamic

quantize_dynamic(
    'fish_detector.onnx',
    'fish_detector_int8.onnx',
    weight_type=QuantType.QInt8
)
```
- Reduces model size by 75%
- Reduces memory usage by 50%
- Speeds up inference by 20-30%

**2. Input Resolution Reduction:**
```python
# Reduce input image size
# Before: 640x640 (YOLOv8 default)
# After: 416x416 or 320x320
model = YOLO('yolov8n.pt')
results = model.train(imgsz=416)  # Smaller input size
```
- Faster inference (50% speedup)
- Slightly lower accuracy (-5%)

**3. Frame Skipping:**
```python
# Process every Nth frame instead of every frame
frame_counter = 0
PROCESS_EVERY_N_FRAMES = 3

if frame_counter % PROCESS_EVERY_N_FRAMES == 0:
    detections = detect_and_classify(frame)
frame_counter += 1
```
- Reduces CPU usage by 66%
- Still responsive (10 FPS → 3 FPS detection)

**4. ROI (Region of Interest) Detection:**
```python
# Only process central region where person usually holds fish
roi_height = int(frame.height * 0.6)  # Middle 60%
roi_width = int(frame.width * 0.8)   # Middle 80%
roi = frame[y1:y2, x1:x2]
```
- Faster detection (smaller image)
- Reduces false positives (ignores edges)

**Performance Targets:**
- Inference time: < 3 seconds (40% improvement)
- Memory usage: < 350MB (30% reduction)
- CPU usage: < 50% (steady state)

**Success Criteria:**
- Meets performance targets
- Accuracy loss < 5%
- System responsive and stable

**Deliverables:**
- Optimized models (`_int8.onnx`, `_416.onnx`)
- Updated `fish_detector.py` with optimizations
- `PERFORMANCE_OPTIMIZATION_REPORT.md`

---

#### Task 3: Edge Case Handling (1 hour)
**Goal:** Handle unusual scenarios gracefully

**Edge Cases to Test:**

1. **Multiple People in Frame:**
   - Challenge: Which person caught the fish?
   - Solution: Detect fish-person proximity, capture all

2. **Partially Visible Fish:**
   - Challenge: Fish cropped by frame edge
   - Solution: Lower confidence threshold for edge detections

3. **Dead Fish on Deck:**
   - Challenge: Fish not being held
   - Solution: Different capture mode (deck mode vs holding mode)

4. **Night Fishing (IR Camera):**
   - Challenge: Different lighting, IR image
   - Solution: Train with IR images or adjust preprocessing

5. **Fish Out of Water (in Air):**
   - Challenge: Fish moving, blurry
   - Solution: Capture multiple frames, select sharpest

6. **Multiple Fish Species:**
   - Challenge: Multiple species in one frame
   - Solution: Detect all, create separate captures

7. **Unknown/Invasive Species:**
   - Challenge: Species not in training data
   - Solution: Classify as "unknown", flag for review

**Error Handling:**
```python
try:
    species_id, species_conf = classify_species(fish_crop)

    if species_conf < 0.5:
        # Low confidence - mark as unknown
        species_name = "unknown"
        species_conf = 0.0
        needs_review = True
    else:
        species_name = SPECIES_LABELS[species_id]
        needs_review = False

except Exception as e:
    logger.error(f"Classification error: {e}")
    species_name = "error"
    species_conf = 0.0
    needs_review = True
```

**Success Criteria:**
- All edge cases handled gracefully
- No crashes or unhandled exceptions
- User feedback for uncertain cases

**Deliverables:**
- Edge case handling code
- `EDGE_CASES_TESTING.md`
- User notification for "unknown" species

---

#### Task 4: Documentation & Deployment (30 min)
**Goal:** Complete documentation and deploy optimized system

**Documentation to Create:**

1. **USER_GUIDE.md** - End-user guide
   - How to use fish capture feature
   - Reading species identification results
   - Understanding fishing regulations
   - Troubleshooting common issues

2. **ADMIN_GUIDE.md** - System administrator guide
   - Service configuration
   - Model updates
   - Database maintenance
   - Performance monitoring

3. **API_DOCUMENTATION.md** - Developer reference
   - All API endpoints
   - Request/response formats
   - Error codes
   - Rate limiting

4. **SESSION_FISH_4_COMPLETE.md** - Session summary
   - Optimization results
   - Performance metrics
   - Known limitations
   - Future improvements

**Deployment Checklist:**
- [ ] Optimized models deployed to Pi
- [ ] Services restarted with new code
- [ ] Database migrations applied
- [ ] Web UI updated
- [ ] Notifications tested
- [ ] Documentation published
- [ ] Backup created

**Success Criteria:**
- All documentation complete
- System deployed and tested
- Performance metrics documented
- User guide accessible

**Deliverables:**
- Complete documentation set
- Deployed optimized system
- Performance benchmark results

---

### Session-Fish-4 Success Criteria

- [ ] Accuracy > 85% on test dataset
- [ ] Inference time < 3 seconds
- [ ] Memory usage < 350MB
- [ ] All edge cases handled
- [ ] Complete documentation
- [ ] System deployed and stable

---

### Session-Fish-4 Dependencies

**Requires:**
- Session-Fish-3 complete (capture pipeline working)

**Blocks:**
- None (final session)

---

## Coordination & Workflow

### Parallel Execution Strategy

**Phase 1: Model Acquisition (Session-Fish-1 only)**
- Start: Session-Fish-1
- Block: Sessions 2, 3, 4 wait for model

**Phase 2: Species & Integration (Sessions 2 & 3 in parallel)**
- Session-Fish-2: Species identification (starts when Session-1 done)
- Session-Fish-3: Auto-capture integration (can start when Session-2 50% complete)

**Phase 3: Optimization (Session-Fish-4 only)**
- Start: Session-Fish-4 (after Session-3 complete)

### Session Briefing Files

Create individual briefing files for each session:
- `SESSION_FISH_1_BRIEFING.md` - Fish detection model
- `SESSION_FISH_2_BRIEFING.md` - Species identification
- `SESSION_FISH_3_BRIEFING.md` - Auto-capture integration
- `SESSION_FISH_4_BRIEFING.md` - Testing & optimization

### Communication Protocol

**Session Status Updates:**
```markdown
# .session-status.md

## FISH IDENTIFICATION - 4 PARALLEL SESSIONS

| Session ID | Domain | Status | Progress |
|------------|--------|--------|----------|
| Session-Fish-1 | Fish Detection Model | 🟢 ACTIVE | 3/6 tasks |
| Session-Fish-2 | Species Identification | 🔵 READY | 0/5 tasks |
| Session-Fish-3 | Auto-Capture Integration | 🔵 READY | 0/5 tasks |
| Session-Fish-4 | Testing & Optimization | 🔵 READY | 0/4 tasks |
```

**Domain Ownership:**
```markdown
# .domain-ownership.md

| Domain | Owner | Files |
|--------|-------|-------|
| Fish Detection | Session-Fish-1 | fish_detector.onnx, fish_detector.py |
| Species ID | Session-Fish-2 | species_classifier.onnx, species.db |
| Auto-Capture | Session-Fish-3 | fish_detector.py (auto-capture logic) |
| Optimization | Session-Fish-4 | All models (quantized versions) |
```

---

## Success Criteria (Overall)

**System Requirements:**
- [ ] Detects fish in camera feed (>70% accuracy)
- [ ] Identifies species (>85% accuracy on 10 common species)
- [ ] Auto-captures when person holding fish
- [ ] Sends Telegram notification with photo and species
- [ ] Displays fishing regulations for identified species
- [ ] Web UI shows capture history with species info
- [ ] Pipeline latency < 5 seconds
- [ ] System stable and reliable

**Deliverables:**
- [ ] Fish detection model (ONNX, <50MB)
- [ ] Species classification model (ONNX, <100MB)
- [ ] Updated fish_detector.py service
- [ ] Species database with regulations
- [ ] Updated web UI with species display
- [ ] Complete documentation (user + admin guides)
- [ ] Test results and performance metrics

---

## Timeline

**Optimistic:** 2 days (with 2 parallel sessions)
**Realistic:** 3 days (with some troubleshooting)
**Pessimistic:** 4-5 days (if custom training needed)

**Milestone Breakdown:**
- Day 1 AM: Session-Fish-1 (model acquisition)
- Day 1 PM: Session-Fish-2 start (species ID)
- Day 2 AM: Session-Fish-2 complete, Session-Fish-3 start
- Day 2 PM: Session-Fish-3 complete
- Day 3 AM: Session-Fish-4 (optimization and testing)
- Day 3 PM: Documentation and deployment

---

## Known Risks & Mitigation

**Risk 1: No suitable pre-trained fish model found**
- Mitigation: Budget time for custom training (4-6 hours)
- Backup: Use simpler binary classifier (fish/no-fish) initially

**Risk 2: Species classification accuracy too low (<80%)**
- Mitigation: Focus on top 5 species first (bass, pike, walleye, perch, trout)
- Backup: Implement "unknown" species category with manual review

**Risk 3: Inference time too slow on Pi (>5 seconds)**
- Mitigation: Use quantization and smaller input resolution
- Backup: Process every 3rd frame instead of every frame

**Risk 4: Limited training data for some species**
- Mitigation: Use data augmentation (rotations, flips, brightness)
- Backup: Combine similar species (e.g., all trout → "trout" class)

**Risk 5: GPU training not available**
- Mitigation: Use Google Colab free tier (12 hours GPU)
- Backup: Overnight CPU training (6-12 hours)

---

## Post-Implementation: Phase 2.3+

After completing fish identification, future phases can include:

**Phase 2.3: Fishing Regulations Deep Integration**
- Real-time season/limit checking
- GPS-based zone detection
- Multi-region support (beyond Ontario)
- Regulation change alerts

**Phase 2.4: Size Measurement**
- Measure fish length from image
- Compare with size limits
- Alert if undersized/oversized

**Phase 2.5: Catch Analytics**
- Species distribution tracking
- Hot spot identification
- Best time/location analysis
- Catch rate statistics

**Phase 2.7: Social Features**
- Share catches to social media
- Leaderboards and competitions
- Community species identification
- Catch verification for tournaments

---

**Ready to start Session-Fish-1?**

Let me know when you're ready to begin, and I'll create the individual session briefing files!
