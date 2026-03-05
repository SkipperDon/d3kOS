#!/usr/bin/env python3
"""
Forward Watch Obstacle Avoidance - YOLOv8 Training Script
Windows Workstation Training (RTX 3060 Ti, 8GB VRAM)

Dataset: 54,789 images from 6 Kaggle sources
Target: 75-85% mAP@0.5, 2+ FPS on Raspberry Pi 4B
Model: YOLOv8m (medium - balance of speed and accuracy)

Usage:
    python train_forward_watch.py --data forward-watch.yaml --epochs 150 --batch 16 --imgsz 640
"""

import os
import sys
from pathlib import Path
from ultralytics import YOLO
import torch
import yaml

# Configuration
DATASET_PATH = Path("C:/forward-watch-dataset")  # Adjust if needed
MODEL_SIZE = "yolov8m"  # yolov8n (fastest), yolov8s, yolov8m (recommended), yolov8l, yolov8x (slowest)
IMAGE_SIZE = 640  # 640x640 pixels (standard YOLO)
BATCH_SIZE = 16  # Optimal for RTX 3060 Ti (8GB VRAM)
EPOCHS = 150  # 100-150 recommended, can be adjusted
DEVICE = "0"  # GPU 0

# Classes for Forward Watch
CLASSES = {
    0: 'person',      # People in water
    1: 'boat',        # Other boats
    2: 'kayak',       # Kayaks, canoes, small craft
    3: 'buoy',        # Navigation buoys
    4: 'log',         # Floating logs, wood
    5: 'debris',      # Marine debris, garbage
    6: 'dock',        # Docks, piers
    7: 'ice'          # Ice, icebergs (Great Lakes)
}

def check_cuda():
    """Verify CUDA and GPU are available"""
    if not torch.cuda.is_available():
        print("❌ ERROR: CUDA not available. Please install PyTorch with CUDA support.")
        print("   Visit: https://pytorch.org/get-started/locally/")
        sys.exit(1)

    gpu_name = torch.cuda.get_device_name(0)
    gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
    print(f"✓ GPU Detected: {gpu_name} ({gpu_memory:.1f} GB)")
    print(f"✓ CUDA Version: {torch.version.cuda}")
    print(f"✓ PyTorch Version: {torch.__version__}")

def create_yaml_config():
    """Create YAML configuration file for YOLOv8 training"""
    config = {
        'path': str(DATASET_PATH.absolute()),
        'train': 'images/train',
        'val': 'images/val',
        'test': 'images/test',
        'nc': len(CLASSES),
        'names': list(CLASSES.values())
    }

    yaml_path = DATASET_PATH / 'forward-watch.yaml'
    with open(yaml_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)

    print(f"✓ Configuration created: {yaml_path}")
    return yaml_path

def train_model(yaml_path):
    """Train YOLOv8 model for Forward Watch obstacle detection"""
    print("\n" + "="*60)
    print("Starting Forward Watch Training")
    print("="*60)
    print(f"Model: {MODEL_SIZE}")
    print(f"Image Size: {IMAGE_SIZE}x{IMAGE_SIZE}")
    print(f"Batch Size: {BATCH_SIZE}")
    print(f"Epochs: {EPOCHS}")
    print(f"Classes: {len(CLASSES)}")
    print(f"Dataset: {DATASET_PATH}")
    print("="*60 + "\n")

    # Initialize model
    model = YOLO(f'{MODEL_SIZE}.pt')  # Download pretrained model

    # Train
    results = model.train(
        data=str(yaml_path),
        epochs=EPOCHS,
        batch=BATCH_SIZE,
        imgsz=IMAGE_SIZE,
        device=DEVICE,
        patience=20,  # Early stopping if no improvement after 20 epochs
        save=True,
        save_period=10,  # Save checkpoint every 10 epochs
        plots=True,  # Generate training plots
        name='forward-watch',
        exist_ok=True,
        pretrained=True,
        optimizer='auto',
        verbose=True,
        seed=0,
        deterministic=True,
        single_cls=False,
        rect=False,
        cos_lr=False,
        close_mosaic=10,  # Disable mosaic augmentation for last 10 epochs
        resume=False,
        amp=True,  # Automatic Mixed Precision (faster training)
        fraction=1.0,  # Use 100% of dataset
        profile=False,
        freeze=None,
        multi_scale=False,
        overlap_mask=True,
        mask_ratio=4,
        dropout=0.0,
        val=True,
        split='val',
        save_json=False,
        save_hybrid=False,
        conf=None,
        iou=0.7,
        max_det=300,
        half=False,
        dnn=False,
        plots=True,
        source=None,
        vid_stride=1,
        stream_buffer=False,
        visualize=False,
        augment=False,
        agnostic_nms=False,
        classes=None,
        retina_masks=False,
        embed=None,
        show=False,
        save_frames=False,
        save_txt=False,
        save_conf=False,
        save_crop=False,
        show_labels=True,
        show_conf=True,
        show_boxes=True,
        line_width=None
    )

    print("\n" + "="*60)
    print("Training Complete!")
    print("="*60)
    print(f"Best model saved to: runs/detect/forward-watch/weights/best.pt")
    print(f"Last model saved to: runs/detect/forward-watch/weights/last.pt")

    # Evaluate on test set
    print("\nEvaluating on test set...")
    metrics = model.val(data=str(yaml_path), split='test')

    print("\n📊 Test Set Metrics:")
    print(f"   mAP@0.5: {metrics.box.map50:.4f} (Target: >0.75)")
    print(f"   mAP@0.5:0.95: {metrics.box.map:.4f}")
    print(f"   Precision: {metrics.box.p:.4f}")
    print(f"   Recall: {metrics.box.r:.4f}")

    # Inference speed test
    print("\n⚡ Inference Speed Test (GPU):")
    print(f"   Preprocess: {metrics.speed['preprocess']:.1f} ms")
    print(f"   Inference: {metrics.speed['inference']:.1f} ms")
    print(f"   Postprocess: {metrics.speed['postprocess']:.1f} ms")
    print(f"   Total: {sum(metrics.speed.values()):.1f} ms/image")

    return metrics

def export_to_onnx():
    """Export trained model to ONNX for Raspberry Pi deployment"""
    print("\n" + "="*60)
    print("Exporting to ONNX for Raspberry Pi")
    print("="*60)

    best_model_path = Path('runs/detect/forward-watch/weights/best.pt')

    if not best_model_path.exists():
        print(f"❌ ERROR: Best model not found at {best_model_path}")
        return

    model = YOLO(str(best_model_path))

    # Export to ONNX
    onnx_path = model.export(
        format='onnx',
        imgsz=IMAGE_SIZE,
        optimize=True,  # Optimize for inference
        simplify=True,  # Simplify ONNX model
        dynamic=False,  # Static input shape for Pi
        opset=12  # ONNX opset version (compatible with ONNX Runtime on Pi)
    )

    print(f"✓ ONNX model saved to: {onnx_path}")
    print(f"✓ Ready for deployment to Raspberry Pi!")
    print(f"\nNext steps:")
    print(f"1. Transfer {onnx_path} to Pi")
    print(f"2. Place in: /opt/d3kos/models/forward-watch/forward_watch.onnx")
    print(f"3. Restart forward-watch service")

    return onnx_path

def main():
    """Main training pipeline"""
    print("\n" + "="*60)
    print("Forward Watch Obstacle Avoidance Training")
    print("d3kOS Marine Vision System")
    print("="*60 + "\n")

    # Check prerequisites
    print("Checking prerequisites...")
    check_cuda()

    if not DATASET_PATH.exists():
        print(f"\n❌ ERROR: Dataset not found at {DATASET_PATH}")
        print(f"   Please extract forward-watch-complete.tar.gz to {DATASET_PATH}")
        print(f"   Expected structure:")
        print(f"   {DATASET_PATH}/")
        print(f"   ├── images/")
        print(f"   │   ├── train/")
        print(f"   │   ├── val/")
        print(f"   │   └── test/")
        print(f"   └── labels/")
        print(f"       ├── train/")
        print(f"       ├── val/")
        print(f"       └── test/")
        sys.exit(1)

    print(f"✓ Dataset found: {DATASET_PATH}")

    # Count images
    train_images = len(list((DATASET_PATH / 'images' / 'train').glob('*.jpg')))
    val_images = len(list((DATASET_PATH / 'images' / 'val').glob('*.jpg')))
    test_images = len(list((DATASET_PATH / 'images' / 'test').glob('*.jpg')))
    total_images = train_images + val_images + test_images

    print(f"✓ Training images: {train_images}")
    print(f"✓ Validation images: {val_images}")
    print(f"✓ Test images: {test_images}")
    print(f"✓ Total images: {total_images}")

    if total_images < 1000:
        print(f"\n⚠ WARNING: Dataset seems small ({total_images} images)")
        print(f"   Expected ~54,789 images from 6 Kaggle datasets")
        response = input("   Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Training cancelled.")
            sys.exit(0)

    # Create YAML config
    yaml_path = create_yaml_config()

    # Estimate training time
    images_per_epoch = train_images
    seconds_per_image = 0.2  # Rough estimate for RTX 3060 Ti with batch_size=16
    total_seconds = EPOCHS * images_per_epoch * seconds_per_image
    total_hours = total_seconds / 3600
    print(f"\n⏱ Estimated training time: {total_hours:.1f} hours ({EPOCHS} epochs)")

    # Start training
    input("\nPress Enter to start training (or Ctrl+C to cancel)...")

    try:
        metrics = train_model(yaml_path)

        # Check if target mAP achieved
        if metrics.box.map50 >= 0.75:
            print(f"\n✅ SUCCESS: Target mAP@0.5 achieved ({metrics.box.map50:.4f} >= 0.75)")
            print(f"   Model is ready for production deployment!")
        else:
            print(f"\n⚠ Target mAP@0.5 not quite reached ({metrics.box.map50:.4f} < 0.75)")
            print(f"   Consider:")
            print(f"   - Training for more epochs (current: {EPOCHS})")
            print(f"   - Using a larger model (yolov8l or yolov8x)")
            print(f"   - Adding more training data")
            print(f"   - Adjusting hyperparameters")

        # Export to ONNX
        export_to_onnx()

        print("\n" + "="*60)
        print("Training pipeline complete!")
        print("="*60)

    except KeyboardInterrupt:
        print("\n\n⚠ Training interrupted by user")
        print("   Checkpoint saved, can resume with resume=True")
    except Exception as e:
        print(f"\n❌ ERROR during training: {e}")
        raise

if __name__ == '__main__':
    main()
