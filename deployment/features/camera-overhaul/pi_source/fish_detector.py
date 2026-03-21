#!/usr/bin/env python3
"""
Fish Detector Service - WITH Species Identification
Detects fish using YOLOv8, then identifies species using 483-species classifier
"""
from flask import Flask, jsonify, request, send_file
import cv2
import numpy as np
import onnxruntime as ort
from datetime import datetime
import sqlite3
import os
import io
import base64
import requests
import json

app = Flask(__name__)

@app.after_request
def _cors(r):
    r.headers["Access-Control-Allow-Origin"] = "*"
    return r

# Configuration
DETECTION_MODEL_PATH = "/opt/d3kos/models/marine-vision/fish_detector.onnx"
SPECIES_MODEL_PATH = "/opt/d3kos/models/fish-species/fish_classifier_483species_best.onnx"
SPECIES_LIST_PATH = "/opt/d3kos/models/fish-species/species_list.json"
CAPTURES_PATH = "/home/d3kos/camera-recordings/captures"
DB_PATH = "/opt/d3kos/data/marine-vision/captures.db"
CAMERA_STREAM_URL = "http://localhost:8084/camera/frame"
SLOTS_CONFIG      = "/opt/d3kos/config/slots.json"


# ── Gemini Vision configuration ────────────────────────────────────────────

def _load_gemini_key():
    """Read GEMINI_API_KEY from Pi env files — same paths as gemini-proxy."""
    for path in [
        '/opt/d3kos/services/gemini-nav/config/gemini.env',
        '/opt/d3kos/services/dashboard/config/api-keys.env',
    ]:
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('GEMINI_API_KEY='):
                        key = line.split('=', 1)[1].strip().strip('"\'')
                        if key and key != 'YOUR_KEY_HERE':
                            return key
    return ''


GEMINI_API_KEY = _load_gemini_key()
GEMINI_MODEL   = 'gemini-2.5-flash'
GEMINI_URL     = f'https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent'

FISH_ID_PROMPT = (
    "You are a fishing assistant for Ontario, Canada (Great Lakes, Lake Simcoe, and inland lakes). "
    "Identify the fish species in this photo. The fish was caught by an angler.\n\n"
    "Respond ONLY in this exact JSON format, with no other text:\n"
    '{"common_name":"Walleye","scientific_name":"Sander vitreus","confidence":"high",'
    '"visual_features":"Brief description of key identifying features you see",'
    '"ontario_note":"Brief Ontario regulation note if applicable, otherwise empty string"}\n\n'
    "If the image does not clearly show a fish or you cannot identify it:\n"
    '{"common_name":"Unknown","scientific_name":"","confidence":"low",'
    '"visual_features":"Reason identification was not possible","ontario_note":""}'
)

if GEMINI_API_KEY:
    print(f"✓ Gemini Vision ready — model: {GEMINI_MODEL}")
else:
    print("⚠ Gemini API key not found — species ID via Gemini will be skipped")


def load_fish_detection_slots():
    """Return slot_ids with fish_detection: true from slots.json.
    Falls back to empty list if slots.json not found (pre-migration systems).
    """
    if not os.path.exists(SLOTS_CONFIG):
        return []
    with open(SLOTS_CONFIG) as f:
        slots = json.load(f)
    return [s['slot_id'] for s in slots if s.get('roles', {}).get('fish_detection')]


# Load Fish Detection Model (YOLOv8 - generic fish detection)
print("=" * 60)
print("Loading Fish Detection Model...")
detection_session = ort.InferenceSession(DETECTION_MODEL_PATH, providers=['CPUExecutionProvider'])
detection_input_name = detection_session.get_inputs()[0].name
print(f"✓ Detection model loaded: {DETECTION_MODEL_PATH}")
print(f"✓ Detection model: YOLOv8n single-class (fish)")

# Load Species Classification Model (483 species)
print("\nLoading Species Classification Model...")
species_session = ort.InferenceSession(SPECIES_MODEL_PATH, providers=['CPUExecutionProvider'])
species_input_name = species_session.get_inputs()[0].name
species_input_shape = species_session.get_inputs()[0].shape
species_input_size = species_input_shape[2] if len(species_input_shape) > 2 else 224
print(f"✓ Species model loaded: {SPECIES_MODEL_PATH}")
print(f"✓ Species input size: {species_input_size}x{species_input_size}")

# Load Species Names
print("\nLoading species list...")
with open(SPECIES_LIST_PATH, 'r') as f:
    species_map = json.load(f)
# Reverse mapping: index -> name
idx_to_species = {v: k for k, v in species_map.items()}
print(f"✓ Loaded {len(species_map)} species")
print("=" * 60)

# Load fish detection slots from slots.json
fish_detection_slots = load_fish_detection_slots()
if fish_detection_slots:
    print(f"✓ Fish detection slots: {fish_detection_slots}")
else:
    print("⚠ No fish_detection slots found — will use active camera frame")

# Initialize database
def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    os.makedirs(CAPTURES_PATH, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Check if species_confidence column exists
    c.execute("PRAGMA table_info(captures)")
    columns = [col[1] for col in c.fetchall()]
    
    if 'species_confidence' not in columns:
        # Add new columns for species identification
        print("Upgrading database schema for species identification...")
        c.execute('ALTER TABLE captures ADD COLUMN species_confidence REAL')
        c.execute('ALTER TABLE captures ADD COLUMN species_top3 TEXT')
        print("✓ Database schema upgraded")

    if 'slot_id' not in columns:
        c.execute('ALTER TABLE captures ADD COLUMN slot_id TEXT')
        print("✓ Added slot_id column to captures table")

    if 'gemini_species' not in columns:
        c.execute('ALTER TABLE captures ADD COLUMN gemini_species TEXT')
        c.execute('ALTER TABLE captures ADD COLUMN gemini_response TEXT')
        print("✓ Added gemini_species / gemini_response columns to captures table")

    c.execute('''CREATE TABLE IF NOT EXISTS captures
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT NOT NULL,
                  image_path TEXT NOT NULL,
                  person_detected INTEGER,
                  fish_detected INTEGER,
                  person_confidence REAL,
                  fish_confidence REAL,
                  species TEXT,
                  species_confidence REAL,
                  species_top3 TEXT,
                  location TEXT,
                  slot_id TEXT,
                  gemini_species TEXT,
                  gemini_response TEXT)''')
    conn.commit()
    conn.close()

init_db()

def preprocess_detection(image):
    """Preprocess image for YOLOv8 fish detection"""
    img_resized = cv2.resize(image, (640, 640))
    img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    img_3ch = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2RGB)
    img_normalized = img_3ch.astype(np.float32) / 255.0
    img_chw = img_normalized.transpose(2, 0, 1)
    img_batch = np.expand_dims(img_chw, axis=0)
    return img_batch

def preprocess_species(image):
    """Preprocess image for species classification"""
    # Resize to model input size
    img_resized = cv2.resize(image, (species_input_size, species_input_size))
    
    # Convert BGR to RGB
    img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
    
    # Normalize to [0, 1]
    img_normalized = img_rgb.astype(np.float32) / 255.0
    
    # ImageNet normalization (EfficientNet standard)
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    img_normalized = (img_normalized - mean) / std
    
    # CHW format
    img_chw = img_normalized.transpose(2, 0, 1)
    img_batch = np.expand_dims(img_chw, axis=0)
    
    return img_batch

def identify_species_gemini(img):
    """
    Send captured JPEG to Gemini Vision for Ontario fish species identification.
    Returns dict: common_name, scientific_name, confidence, visual_features, ontario_note
    Falls back gracefully if Gemini unavailable.
    """
    if not GEMINI_API_KEY:
        return {
            'common_name': 'Unknown', 'scientific_name': '', 'confidence': 'low',
            'visual_features': 'Gemini API key not configured on this device.',
            'ontario_note': '', 'source': 'gemini_unavailable'
        }

    try:
        # Encode image as base64 JPEG
        _, buf = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 85])
        img_b64 = base64.b64encode(buf.tobytes()).decode('utf-8')

        payload = {
            'contents': [{
                'parts': [
                    {'inline_data': {'mime_type': 'image/jpeg', 'data': img_b64}},
                    {'text': FISH_ID_PROMPT}
                ]
            }],
            'generationConfig': {'maxOutputTokens': 250, 'temperature': 0.1}
        }

        resp = requests.post(
            f'{GEMINI_URL}?key={GEMINI_API_KEY}',
            json=payload, timeout=20
        )
        resp.raise_for_status()

        raw = resp.json()['candidates'][0]['content']['parts'][0]['text'].strip()

        # Strip markdown code fences if Gemini wraps response
        if '```' in raw:
            parts = raw.split('```')
            raw = parts[1] if len(parts) > 1 else raw
            if raw.startswith('json'):
                raw = raw[4:]
        raw = raw.strip()

        result = json.loads(raw)
        result['source'] = 'gemini'
        print(f"✓ Gemini ID: {result.get('common_name')} ({result.get('confidence')})")
        return result

    except requests.exceptions.Timeout:
        print("⚠ Gemini Vision timeout")
        return {
            'common_name': 'Unknown', 'scientific_name': '', 'confidence': 'low',
            'visual_features': 'Gemini request timed out — check internet connection.',
            'ontario_note': '', 'source': 'gemini_timeout'
        }
    except Exception as e:
        print(f"⚠ Gemini Vision error: {e}")
        return {
            'common_name': 'Unknown', 'scientific_name': '', 'confidence': 'low',
            'visual_features': f'Identification error: {str(e)[:100]}',
            'ontario_note': '', 'source': 'gemini_error'
        }


def classify_species(image):
    """
    Classify fish species from image.
    Returns: (species_name, confidence, top_3_predictions)
    NOTE: model outputs log-softmax — apply exp() to convert to probability.
    NOTE: This model was trained on Australian/Indo-Pacific fish. For Ontario
    freshwater species, use identify_species_gemini() instead.
    """
    input_tensor = preprocess_species(image)
    outputs = species_session.run(None, {species_input_name: input_tensor})
    log_probs = outputs[0][0]

    # Convert log-softmax → probability (values were negative raw log-softmax)
    probabilities = np.exp(log_probs)

    top_3_idx = np.argsort(probabilities)[-3:][::-1]
    top_3_predictions = [
        {
            'species': idx_to_species.get(int(idx), f"unknown_class_{idx}"),
            'confidence': float(probabilities[idx])
        }
        for idx in top_3_idx
    ]

    best_species = top_3_predictions[0]['species']
    best_confidence = top_3_predictions[0]['confidence']

    return best_species, best_confidence, top_3_predictions


def compute_iou(b1, b2):
    """Compute IoU between two bounding boxes (center format: x_center, y_center, w, h)."""
    ax1 = b1['x_center'] - b1['width'] / 2
    ay1 = b1['y_center'] - b1['height'] / 2
    ax2 = b1['x_center'] + b1['width'] / 2
    ay2 = b1['y_center'] + b1['height'] / 2

    bx1 = b2['x_center'] - b2['width'] / 2
    by1 = b2['y_center'] - b2['height'] / 2
    bx2 = b2['x_center'] + b2['width'] / 2
    by2 = b2['y_center'] + b2['height'] / 2

    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)

    if ix2 <= ix1 or iy2 <= iy1:
        return 0.0

    inter = (ix2 - ix1) * (iy2 - iy1)
    area_a = (ax2 - ax1) * (ay2 - ay1)
    area_b = (bx2 - bx1) * (by2 - by1)
    return inter / (area_a + area_b - inter)


def apply_nms(detections, iou_threshold=0.4):
    """Collapse overlapping bounding boxes — keeps highest-confidence box per cluster."""
    if len(detections) <= 1:
        return detections
    detections = sorted(detections, key=lambda x: x['confidence'], reverse=True)
    kept = []
    suppressed = set()
    for i in range(len(detections)):
        if i in suppressed:
            continue
        kept.append(detections[i])
        for j in range(i + 1, len(detections)):
            if j not in suppressed:
                if compute_iou(detections[i]['bbox'], detections[j]['bbox']) > iou_threshold:
                    suppressed.add(j)
    return kept


def postprocess_detections(outputs, confidence_threshold=0.45):
    """Post-process YOLOv8 fish detection output with NMS to suppress duplicate boxes."""
    predictions = outputs[0][0]
    predictions = predictions.T

    detections = []
    for pred in predictions:
        x_center, y_center, width, height, fish_confidence = pred

        if fish_confidence > confidence_threshold:
            detections.append({
                'class_name': 'fish',
                'confidence': float(fish_confidence),
                'bbox': {
                    'x_center': float(x_center),
                    'y_center': float(y_center),
                    'width': float(width),
                    'height': float(height)
                }
            })

    return apply_nms(detections)

@app.route('/detect/status', methods=['GET'])
def detection_status():
    """Get detection service status"""
    # Check forward-watch camera (backwards compat)
    try:
        response = requests.get(CAMERA_STREAM_URL, timeout=2)
        camera_online = response.status_code == 200
    except Exception:
        camera_online = False

    # Per-slot status for fish_detection slots
    slot_statuses = {}
    for slot_id in fish_detection_slots:
        try:
            r = requests.get(f'http://localhost:8084/camera/slots', timeout=2)
            if r.status_code == 200:
                slots = r.json()
                slot = next((s for s in slots if s['slot_id'] == slot_id), None)
                slot_statuses[slot_id] = slot['status'] if slot else 'unknown'
        except Exception:
            slot_statuses[slot_id] = 'unknown'
        break  # only one HTTP call needed — get all slots at once

    # Rebuild slot_statuses properly from one fetch
    slot_statuses = {}
    try:
        r = requests.get('http://localhost:8084/camera/slots', timeout=2)
        if r.status_code == 200:
            all_slots = {s['slot_id']: s['status'] for s in r.json()}
            for slot_id in fish_detection_slots:
                slot_statuses[slot_id] = all_slots.get(slot_id, 'unknown')
    except Exception:
        for slot_id in fish_detection_slots:
            slot_statuses[slot_id] = 'unknown'

    return jsonify({
        'status': 'active',
        'detection_model': 'YOLOv8n Fish Detector',
        'species_model': '483-species EfficientNet Classifier',
        'species_count': len(species_map),
        'detection_classes': 1,
        'camera_status': 'online' if camera_online else 'offline',
        'fish_detection_slots': fish_detection_slots,
        'slot_statuses': slot_statuses,
        'ready': True,
        'model': 'YOLOv8n + EfficientNet-483',
        'classes': str(len(species_map)) + ' species',
    })

@app.route('/detect/frame', methods=['POST'])
def detect_frame():
    """Detect fish and identify species"""
    # Resolve which slot/camera to use
    slot_id = request.args.get('slot_id') or request.form.get('slot_id')
    if not slot_id and fish_detection_slots:
        slot_id = fish_detection_slots[0]

    # Get image from request or camera stream
    img = None

    if 'image' in request.files:
        file = request.files['image']
        npimg = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    else:
        # Fetch from per-slot endpoint if slot_id known, else fall back to legacy URL
        if slot_id:
            frame_url = f'http://localhost:8084/camera/frame/{slot_id}'
        else:
            frame_url = CAMERA_STREAM_URL
        try:
            response = requests.get(frame_url, timeout=5)
            if response.status_code == 200:
                npimg = np.frombuffer(response.content, np.uint8)
                img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
            else:
                return jsonify({'status': 'offline', 'reason': 'camera unavailable', 'detections': [], 'slot_id': slot_id})
        except Exception as e:
            return jsonify({'status': 'offline', 'reason': f'camera error: {str(e)}', 'detections': [], 'slot_id': slot_id})

    if img is None:
        return jsonify({'error': 'Failed to decode image'}), 400

    # Step 1: Fish Detection
    img_preprocessed = preprocess_detection(img)
    outputs = detection_session.run(None, {detection_input_name: img_preprocessed})
    detections = postprocess_detections(outputs, confidence_threshold=0.25)

    fish_detected = len(detections) > 0
    fish_confidence = max([d['confidence'] for d in detections]) if fish_detected else 0.0

    # Step 2: ONNX species classifier (background — kept for data, not shown to user)
    species_name = None
    species_confidence = None
    species_top3 = None

    if fish_detected:
        species_name, species_confidence, species_top3 = classify_species(img)

    # Step 3: Gemini Vision species identification (primary species display)
    gemini_result = None
    if fish_detected:
        print(f"Fish detected ({fish_confidence:.2%}) — sending capture to Gemini Vision...")
        gemini_result = identify_species_gemini(img)

    # Person detection (disabled for now)
    person_detected = False
    person_confidence = 0.0

    # Auto-capture trigger
    capture_triggered = fish_detected
    capture_id = None

    if capture_triggered:
        capture_id = save_capture(
            img,
            person_confidence,
            fish_confidence,
            species_name,
            species_confidence,
            species_top3,
            slot_id=slot_id,
            gemini_result=gemini_result
        )

    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'slot_id': slot_id,
        'detections': detections,
        'person_detected': person_detected,
        'person_confidence': person_confidence,
        'fish_detected': fish_detected,
        'fish_confidence': fish_confidence,
        'gemini_id': gemini_result,
        'capture_triggered': capture_triggered,
        'capture_id': capture_id
    })

def save_capture(img, person_conf, fish_conf, species=None, species_conf=None,
                 species_top3=None, slot_id=None, gemini_result=None):
    """Save capture to database and disk"""
    timestamp = datetime.now().isoformat()
    filename = f"catch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    filepath = os.path.join(CAPTURES_PATH, filename)

    cv2.imwrite(filepath, img, [cv2.IMWRITE_JPEG_QUALITY, 95])

    gemini_species = gemini_result.get('common_name') if gemini_result else None
    gemini_json    = json.dumps(gemini_result) if gemini_result else None

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO captures
                 (timestamp, image_path, person_detected, fish_detected,
                  person_confidence, fish_confidence, species, species_confidence,
                  species_top3, slot_id, gemini_species, gemini_response)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (timestamp, filepath, 0, 1,
               float(person_conf), float(fish_conf),
               species, float(species_conf) if species_conf else None,
               json.dumps(species_top3) if species_top3 else None,
               slot_id, gemini_species, gemini_json))
    capture_id = c.lastrowid
    conn.commit()
    conn.close()

    label = gemini_species or species or 'unidentified'
    print(f"✓ Capture saved: {filename} (ID: {capture_id}, Species: {label}, Slot: {slot_id})")
    return capture_id

@app.route('/captures', methods=['GET'])
def list_captures():
    """List all captures"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM captures ORDER BY timestamp DESC LIMIT 50')
    rows = c.fetchall()
    conn.close()

    captures = []
    for row in rows:
        captures.append({
            'id': row[0],
            'timestamp': row[1],
            'image_path': row[2],
            'person_detected': bool(row[3]),
            'fish_detected': bool(row[4]),
            'person_confidence': row[5],
            'fish_confidence': row[6],
            'species': row[7],
            'location': row[8] if len(row) > 8 else None,
            'species_confidence': row[9] if len(row) > 9 else None,
            'species_top3': json.loads(row[10]) if len(row) > 10 and row[10] else None,
            'slot_id': row[11] if len(row) > 11 else None,
            'gemini_species': row[12] if len(row) > 12 else None,
            'gemini_response': json.loads(row[13]) if len(row) > 13 and row[13] else None,
        })

    return jsonify({'captures': captures, 'count': len(captures)})

@app.route('/captures/<int:capture_id>', methods=['GET'])
def get_capture(capture_id):
    """Get capture details"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM captures WHERE id = ?', (capture_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        return jsonify({'error': 'Capture not found'}), 404

    return jsonify({
        'id': row[0],
        'timestamp': row[1],
        'image_path': row[2],
        'person_detected': bool(row[3]),
        'fish_detected': bool(row[4]),
        'person_confidence': row[5],
        'fish_confidence': row[6],
        'species': row[7],
        'location': row[8] if len(row) > 8 else None,
        'species_confidence': row[9] if len(row) > 9 else None,
        'species_top3': json.loads(row[10]) if len(row) > 10 and row[10] else None,
        'slot_id': row[11] if len(row) > 11 else None,
        'gemini_species': row[12] if len(row) > 12 else None,
        'gemini_response': json.loads(row[13]) if len(row) > 13 and row[13] else None,
    })

@app.route('/captures/<int:capture_id>/image', methods=['GET'])
def get_capture_image(capture_id):
    """Get capture image"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT image_path FROM captures WHERE id = ?', (capture_id,))
    row = c.fetchone()
    conn.close()

    if not row or not os.path.exists(row[0]):
        return jsonify({'error': 'Image not found'}), 404

    return send_file(row[0], mimetype='image/jpeg')

@app.route('/detect/reload', methods=['POST'])
def reload_slots():
    """Re-read slots.json and update fish_detection_slots without restarting the service"""
    global fish_detection_slots
    fish_detection_slots = load_fish_detection_slots()
    print(f"✓ Slots reloaded: fish_detection_slots = {fish_detection_slots}")
    return jsonify({
        'status': 'reloaded',
        'fish_detection_slots': fish_detection_slots
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8086, debug=False)