#!/usr/bin/env python3
"""
YOLOv8 Forward Watch Training Script
Trains marine object detection: ships, debris, icebergs
"""
import os
from ultralytics import YOLO

# Get script directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Training configuration
EPOCHS = 100
BATCH_SIZE = 16
IMAGE_SIZE = 640

# Look for data.yaml in same folder as this script
DATASET_PATH = os.path.join(script_dir, "data.yaml")

# Output directory
OUTPUT_DIR = os.path.join(script_dir, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 60)
print("🚢 YOLOv8 FORWARD WATCH TRAINING")
print("=" * 60)
print(f"Script location: {script_dir}")
print(f"Looking for data.yaml at: {DATASET_PATH}")

if not os.path.exists(DATASET_PATH):
    print()
    print("❌ ERROR: data.yaml not found!")
    print(f"   Expected location: {DATASET_PATH}")
    print()
    print("   Put data.yaml in the same folder as this script.")
    input("Press Enter to exit...")
    exit(1)

print(f"✓ Found data.yaml")
print(f"Epochs: {EPOCHS}")
print(f"Batch Size: {BATCH_SIZE}")
print(f"Image Size: {IMAGE_SIZE}")
print(f"Output: {OUTPUT_DIR}")
print("=" * 60)
print()

# Load YOLOv8 model
print("Loading YOLOv8 nano model...")
model = YOLO('yolov8n.pt')

print("Starting training...")
print()

# Train the model
results = model.train(
    data=DATASET_PATH,
    epochs=EPOCHS,
    batch=BATCH_SIZE,
    imgsz=IMAGE_SIZE,
    project=OUTPUT_DIR,
    name='forward-watch',
    device=0,
    patience=20,
    save=True,
    plots=True,
    verbose=True
)

print()
print("=" * 60)
print("✅ TRAINING COMPLETE!")
print("=" * 60)
print(f"Best model: {OUTPUT_DIR}\\forward-watch\\weights\\best.pt")
print("=" * 60)
input("Press Enter to exit...")
