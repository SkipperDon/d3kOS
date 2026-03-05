#!/usr/bin/env python3
"""
YOLOv8 Forward Watch Training Script - FINAL VERSION
Trains marine object detection: ships, boats, debris, buoys, kayaks, logs
"""
import os
from ultralytics import YOLO

# Training configuration
EPOCHS = 100  # Number of training cycles
BATCH_SIZE = 16  # Images per batch
IMAGE_SIZE = 640  # Input image size

# Dataset path - EXACT location
DATASET_PATH = r"C:\Users\donmo\Downloads\forward-watch-complete\data.yaml"

# Output directory
OUTPUT_DIR = r"C:\Users\donmo\Downloads\forward-watch-complete\output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 60)
print("🚢 YOLOv8 FORWARD WATCH TRAINING - FINAL")
print("=" * 60)
print(f"Dataset: {DATASET_PATH}")
print(f"Epochs: {EPOCHS}")
print(f"Batch Size: {BATCH_SIZE}")
print(f"Image Size: {IMAGE_SIZE}")
print(f"Output: {OUTPUT_DIR}")
print("=" * 60)
print()

# Verify data.yaml exists
if not os.path.exists(DATASET_PATH):
    print(f"❌ ERROR: data.yaml not found at {DATASET_PATH}")
    input("Press Enter to exit...")
    exit(1)

print("✓ Found data.yaml")
print()

# Load YOLOv8 model
print("Loading YOLOv8 nano model...")
model = YOLO('yolov8n.pt')  # Nano model (fastest)

print("Starting training...")
print("This will take 12-24 hours on RTX 3060 Ti")
print()

# Train the model
results = model.train(
    data=DATASET_PATH,
    epochs=EPOCHS,
    batch=BATCH_SIZE,
    imgsz=IMAGE_SIZE,
    project=OUTPUT_DIR,
    name='forward-watch',
    device=0,  # Use GPU 0 (RTX 3060 Ti)
    patience=20,  # Early stopping if no improvement
    save=True,  # Save checkpoints
    plots=True,  # Generate training plots
    verbose=True  # Show detailed output
)

print()
print("=" * 60)
print("✅ TRAINING COMPLETE!")
print("=" * 60)
print(f"Best model saved to: {OUTPUT_DIR}\\forward-watch\\weights\\best.pt")
print()
print("Next step: Convert to ONNX for Raspberry Pi deployment")
print("=" * 60)
input("Press Enter to exit...")
