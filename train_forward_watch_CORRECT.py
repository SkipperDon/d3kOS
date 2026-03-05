#!/usr/bin/env python3
"""
YOLOv8 Forward Watch Training Script
Trains marine object detection: ships, boats, debris, buoys, kayaks, logs
"""
import os
from ultralytics import YOLO

# Training configuration
EPOCHS = 100
BATCH_SIZE = 16
IMAGE_SIZE = 640

# Dataset path - Based on your file locations
DATASET_PATH = r"C:\Users\donmo\Downloads\kaggle-datasets\yolov8-ship-detection\data.yaml"

# Output directory
OUTPUT_DIR = r"C:\Users\donmo\Downloads\forward-watch-complete\output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 70)
print("🚢 YOLOv8 FORWARD WATCH TRAINING")
print("=" * 70)
print(f"Dataset: {DATASET_PATH}")

# Check if data.yaml exists
if not os.path.exists(DATASET_PATH):
    print()
    print(f"❌ ERROR: data.yaml not found!")
    print(f"   Looking at: {DATASET_PATH}")
    print()
    print("   Please verify the file exists at that location.")
    input("Press Enter to exit...")
    exit(1)

print("✓ Data file found")
print(f"Epochs: {EPOCHS}")
print(f"Batch Size: {BATCH_SIZE}")
print(f"Image Size: {IMAGE_SIZE}")
print(f"Output Directory: {OUTPUT_DIR}")
print(f"GPU: RTX 3060 Ti (device 0)")
print("=" * 70)
print()

# Load YOLOv8 nano model
print("Loading YOLOv8 nano model...")
model = YOLO('yolov8n.pt')

print()
print("Starting training...")
print("Expected duration: 12-24 hours")
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
print("=" * 70)
print("✅ TRAINING COMPLETE!")
print("=" * 70)
print(f"Best model: {OUTPUT_DIR}\\forward-watch\\weights\\best.pt")
print()
print("Next: Convert to ONNX for Raspberry Pi deployment")
print("=" * 70)
input("Press Enter to exit...")
