#!/usr/bin/env python3
"""
YOLOv8 Forward Watch Training Script
Trains marine object detection: ships, debris, icebergs
Runs from current directory
"""
import os
from ultralytics import YOLO

# Get current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Training configuration
EPOCHS = 100  # Number of training cycles
BATCH_SIZE = 16  # Images per batch (adjust based on GPU memory)
IMAGE_SIZE = 640  # Input image size

# Dataset path (look for data.yaml in current directory)
DATASET_PATH = os.path.join(current_dir, "data.yaml")

# Output directory (current directory)
OUTPUT_DIR = os.path.join(current_dir, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 60)
print("🚢 YOLOv8 FORWARD WATCH TRAINING")
print("=" * 60)
print(f"Current directory: {current_dir}")
print(f"Dataset: {DATASET_PATH}")
print(f"Epochs: {EPOCHS}")
print(f"Batch Size: {BATCH_SIZE}")
print(f"Image Size: {IMAGE_SIZE}")
print(f"Output: {OUTPUT_DIR}")
print("=" * 60)
print()

# Check if data.yaml exists
if not os.path.exists(DATASET_PATH):
    print("❌ ERROR: data.yaml not found in current directory!")
    print(f"   Looking for: {DATASET_PATH}")
    print()
    print("Make sure data.yaml is in the same folder as this script.")
    input("Press Enter to exit...")
    exit(1)

# Load YOLOv8 model
print("Loading YOLOv8 nano model...")
model = YOLO('yolov8n.pt')  # Nano model (fastest)

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
