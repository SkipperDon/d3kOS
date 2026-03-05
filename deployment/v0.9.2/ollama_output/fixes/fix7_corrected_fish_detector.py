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
import requests
import json

app = Flask(__name__)

# Configuration
DETECTION_MODEL_PATH = "/opt/d3kos/models/marine-vision/fish_detector.onnx"
SPECIES_MODEL_PATH = "/opt/d3kos/models/fish-species/fish_classifier_483species_best.onnx"
SPECIES_LIST_PATH = "/opt/d3kos/models/fish-species/species_list.json"
CAPTURES_PATH = "/home/d3kos/camera-recordings/captures"
DB_PATH = "/opt/d3kos/data/marine-vision/captures.db"
CAMERA_STREAM_URL = "http://localhost:8084/camera/frame"

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
                  location TEXT)''')
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

def classify_species(image):
    """
    Classify fish species from image
    Returns: (species_name, confidence, top_3_predictions)
    """
    # Preprocess
    input_tensor = preprocess_species(image)
    
    # Run inference
    outputs = species_session.run(None, {species_input_name: input_tensor})
    probabilities = outputs[0][0]
    
    # Get top 3 predictions
    top_3_idx = np.argsort(probabilities)[-3:][::-1]
    top_3_predictions = [
        {
            'species': idx_to_species.get(int(idx), f"unknown_class_{idx}"),
            'confidence': float(probabilities[idx])
        }
        for idx in top_3_idx
    ]
    
    # Return best prediction
    best_species = top_3_predictions[0]['species']
    best_confidence = top_3_predictions[0]['confidence']
    
    return best_species, best_confidence, top_3_predictions

def postprocess_detections(outputs, confidence_threshold=0.25):
    """Post-process YOLOv8 fish detection output"""
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

    return detections

@app.route('/detect/status', methods=['GET'])
def detection_status():
    """Get detection service status"""
    # Check camera status
    try:
        response = requests.get(CAMERA_STREAM_URL, timeout=2)
        camera_online = response.status_code == 200
    except Exception:
        camera_online = False
    
    return jsonify({
        'status': 'active',
        'detection_model': 'YOLOv8n Fish Detector',
        'species_model': '483-species EfficientNet Classifier',
        'species_count': len(species_map),
        'detection_classes': 1,
        'camera_status': 'online' if camera_online else 'offline',
        'ready': True
    })

@app.route('/detect/frame', methods=['POST'])
def detect_frame():
    """Detect fish and identify species"""
    # Get image from request or camera stream
    img = None
    
    if 'image' in request.files:
        file = request.files['image']
        npimg = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    else:
        try:
            response = requests.get(CAMERA_STREAM_URL, timeout=5)
            if response.status_code == 200:
                npimg = np.frombuffer(response.content, np.uint8)
                img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
            else:
                return jsonify({'status': 'offline', 'reason': 'camera unavailable', 'detections': []})
        except Exception as e:
            return jsonify({'status': 'offline', 'reason': f'camera error: {str(e)}', 'detections': []})

    if img is None:
        return jsonify({'error': 'Failed to decode image'}), 400

    # Step 1: Fish Detection
    img_preprocessed = preprocess_detection(img)
    outputs = detection_session.run(None, {detection_input_name: img_preprocessed})
    detections = postprocess_detections(outputs, confidence_threshold=0.25)

    fish_detected = len(detections) > 0
    fish_confidence = max([d['confidence'] for d in detections]) if fish_detected else 0.0

    # Step 2: Species Identification (if fish detected)
    species_name = None
    species_confidence = None
    species_top3 = None
    
    if fish_detected:
        print(f"Fish detected with {fish_confidence:.2%} confidence, running species ID...")
        species_name, species_confidence, species_top3 = classify_species(img)
        print(f"✓ Species: {species_name} ({species_confidence:.2%} confidence)")

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
            species_top3
        )

    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'detections': detections,
        'person_detected': person_detected,
        'person_confidence': person_confidence,
        'fish_detected': fish_detected,
        'fish_confidence': fish_confidence,
        'species': species_name,
        'species_confidence': species_confidence,
        'species_top3': species_top3,
        'capture_triggered': capture_triggered,
        'capture_id': capture_id
    })

def save_capture(img, person_conf, fish_conf, species=None, species_conf=None, species_top3=None):
    """Save capture to database and disk"""
    timestamp = datetime.now().isoformat()
    filename = f"catch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    filepath = os.path.join(CAPTURES_PATH, filename)

    # Save image
    cv2.imwrite(filepath, img, [cv2.IMWRITE_JPEG_QUALITY, 95])

    # Save to database
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO captures
                 (timestamp, image_path, person_detected, fish_detected,
                  person_confidence, fish_confidence, species, species_confidence, species_top3)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (timestamp, filepath, 0, 1, 
               float(person_conf), float(fish_conf),
               species, float(species_conf) if species_conf else None,
               json.dumps(species_top3) if species_top3 else None))
    capture_id = c.lastrowid
    conn.commit()
    conn.close()

    print(f"✓ Capture saved: {filename} (ID: {capture_id}, Species: {species})")
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
            'species_confidence': row[8] if len(row) > 8 else None,
            'species_top3': json.loads(row[9]) if len(row) > 9 and row[9] else None
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
        'species_confidence': row[8] if len(row) > 8 else None,
        'species_top3': json.loads(row[9]) if len(row) > 9 and row[9] else None
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8086, debug=False)