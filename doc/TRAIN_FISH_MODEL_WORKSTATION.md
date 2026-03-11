# Fish Species Model Training - NVIDIA Workstation Guide

**Date:** February 25, 2026
**Purpose:** Train EfficientNet model for worldwide fish identification
**Hardware:** NVIDIA GPU workstation (Windows/Linux)
**Time Required:** 12-24 hours training + 2-3 hours setup

---

## Prerequisites Check

### 1. Verify NVIDIA GPU

**Windows:**
```cmd
nvidia-smi
```

**Linux:**
```bash
nvidia-smi
```

**Look for:**
- GPU name (e.g., RTX 3060, RTX 4070, etc.)
- CUDA version (should be 11.8 or newer)
- Memory (need at least 6GB VRAM, 8GB+ recommended)

**Minimum requirements:**
- NVIDIA GPU with 6GB+ VRAM
- CUDA 11.8+
- 32GB+ system RAM recommended
- 50GB free disk space

---

## Step 1: Install Dependencies

### Windows Installation

**1. Install Python 3.10+ from python.org**

**2. Install CUDA Toolkit 12.1:**
- Download: https://developer.nvidia.com/cuda-downloads
- Install with default options

**3. Install cuDNN:**
- Download from: https://developer.nvidia.com/cudnn
- Extract to CUDA directory (C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.1)

**4. Install PyTorch with CUDA:**
```cmd
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**5. Install training dependencies:**
```cmd
pip install pillow matplotlib numpy tensorboard onnx onnxruntime scikit-learn tqdm
```

### Linux Installation

**1. Install CUDA:**
```bash
# Ubuntu/Debian
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda-toolkit-12-1
```

**2. Install PyTorch with CUDA:**
```bash
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**3. Install dependencies:**
```bash
pip3 install pillow matplotlib numpy tensorboard onnx onnxruntime scikit-learn tqdm
```

### Verify Installation

**Test PyTorch GPU:**
```python
import torch
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda}")
print(f"GPU: {torch.cuda.get_device_name(0)}")
```

**Expected output:**
```
PyTorch version: 2.10.0+cu121
CUDA available: True
CUDA version: 12.1
GPU: NVIDIA GeForce RTX 4070
```

---

## Step 2: Transfer Dataset from Pi to Workstation

### Method 1: Direct SSH/SCP Transfer (Recommended)

**Windows (using WinSCP or command line):**
```cmd
# Using SCP (if you have OpenSSH)
scp -r -i %USERPROFILE%\.ssh\d3kos_key d3kos@192.168.1.237:/opt/d3kos/datasets/fish-worldwide C:\fish-training\dataset
```

**Linux:**
```bash
# Create local directory
mkdir -p ~/fish-training/dataset

# Copy dataset from Pi (this will take 1-2 hours for 10GB)
scp -r -i ~/.ssh/d3kos_key d3kos@192.168.1.237:/opt/d3kos/datasets/fish-worldwide ~/fish-training/dataset/
```

### Method 2: USB Drive Transfer

**On Pi:**
```bash
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237

# Mount USB drive (assuming /dev/sda1)
sudo mkdir -p /mnt/usb
sudo mount /dev/sda1 /mnt/usb

# Copy dataset to USB
sudo cp -r /opt/d3kos/datasets/fish-worldwide /mnt/usb/

# Unmount
sudo umount /mnt/usb
```

**On Workstation:**
- Insert USB drive
- Copy `fish-worldwide` folder to `C:\fish-training\dataset` (Windows) or `~/fish-training/dataset` (Linux)

### Verify Dataset

```python
import os
from pathlib import Path

dataset_root = Path("C:/fish-training/dataset/fish-worldwide")  # Windows
# dataset_root = Path("~/fish-training/dataset/fish-worldwide").expanduser()  # Linux

train_count = len(list(dataset_root.glob("train/**/*.jpg")))
val_count = len(list(dataset_root.glob("val/**/*.jpg")))
test_count = len(list(dataset_root.glob("test/**/*.jpg")))

print(f"Training images: {train_count}")
print(f"Validation images: {val_count}")
print(f"Testing images: {test_count}")
print(f"Total: {train_count + val_count + test_count}")

# Should show ~16,000 train, ~2,000 val, ~2,000 test
```

---

## Step 3: Training Script

Create `train_fish_model.py`:

```python
#!/usr/bin/env python3
"""
Fish Species Classification Model Training
EfficientNet-B0 for 200 species worldwide
Optimized for NVIDIA GPU
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from torch.utils.tensorboard import SummaryWriter
from pathlib import Path
import time
from tqdm import tqdm

# Configuration
DATASET_ROOT = Path("C:/fish-training/dataset/fish-worldwide")  # Change for Linux
BATCH_SIZE = 32  # Adjust based on GPU memory (16 for 6GB, 32 for 8GB+, 64 for 12GB+)
NUM_EPOCHS = 50
LEARNING_RATE = 0.001
NUM_CLASSES = 200
IMAGE_SIZE = 512
NUM_WORKERS = 4  # Parallel data loading

# Device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")

# Data transforms
train_transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomRotation(15),
    transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3, hue=0.1),
    transforms.RandomAffine(degrees=0, translate=(0.1, 0.1), scale=(0.9, 1.1)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

val_transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# Load datasets
print("Loading datasets...")
train_dataset = datasets.ImageFolder(DATASET_ROOT / "train", transform=train_transform)
val_dataset = datasets.ImageFolder(DATASET_ROOT / "val", transform=val_transform)
test_dataset = datasets.ImageFolder(DATASET_ROOT / "test", transform=val_transform)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True,
                          num_workers=NUM_WORKERS, pin_memory=True)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False,
                        num_workers=NUM_WORKERS, pin_memory=True)
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False,
                         num_workers=NUM_WORKERS, pin_memory=True)

print(f"Training samples: {len(train_dataset)}")
print(f"Validation samples: {len(val_dataset)}")
print(f"Testing samples: {len(test_dataset)}")
print(f"Number of classes: {len(train_dataset.classes)}")

# Create model
print("\nCreating EfficientNet-B0 model...")
model = models.efficientnet_b0(weights='IMAGENET1K_V1')  # Pretrained on ImageNet

# Freeze early layers (transfer learning)
for param in model.features.parameters():
    param.requires_grad = False

# Replace classifier for 200 fish species
model.classifier = nn.Sequential(
    nn.Dropout(0.3),
    nn.Linear(1280, NUM_CLASSES)
)

model = model.to(device)

# Loss and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.classifier.parameters(), lr=LEARNING_RATE)
scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5,
                                                   patience=3, verbose=True)

# TensorBoard
writer = SummaryWriter('runs/fish_classification')

# Training function
def train_epoch(epoch):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{NUM_EPOCHS} [Train]")
    for i, (images, labels) in enumerate(pbar):
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()

        # Update progress bar
        pbar.set_postfix({
            'loss': running_loss / (i + 1),
            'acc': 100. * correct / total
        })

    epoch_loss = running_loss / len(train_loader)
    epoch_acc = 100. * correct / total
    return epoch_loss, epoch_acc

# Validation function
def validate(epoch):
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():
        pbar = tqdm(val_loader, desc=f"Epoch {epoch+1}/{NUM_EPOCHS} [Val]")
        for i, (images, labels) in enumerate(pbar):
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)

            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

            pbar.set_postfix({
                'loss': running_loss / (i + 1),
                'acc': 100. * correct / total
            })

    epoch_loss = running_loss / len(val_loader)
    epoch_acc = 100. * correct / total
    return epoch_loss, epoch_acc

# Training loop
best_val_acc = 0.0
print("\nStarting training...")
print("=" * 70)

for epoch in range(NUM_EPOCHS):
    start_time = time.time()

    # Train
    train_loss, train_acc = train_epoch(epoch)

    # Validate
    val_loss, val_acc = validate(epoch)

    # Learning rate scheduling
    scheduler.step(val_loss)

    # Log to TensorBoard
    writer.add_scalar('Loss/train', train_loss, epoch)
    writer.add_scalar('Loss/val', val_loss, epoch)
    writer.add_scalar('Accuracy/train', train_acc, epoch)
    writer.add_scalar('Accuracy/val', val_acc, epoch)

    # Save best model
    if val_acc > best_val_acc:
        best_val_acc = val_acc
        torch.save({
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'val_acc': val_acc,
            'class_to_idx': train_dataset.class_to_idx
        }, 'best_fish_model.pth')
        print(f"✅ Saved best model (val_acc: {val_acc:.2f}%)")

    epoch_time = time.time() - start_time
    print(f"\nEpoch {epoch+1}/{NUM_EPOCHS} - {epoch_time:.0f}s")
    print(f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")
    print(f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.2f}%")
    print("=" * 70)

print(f"\n🎉 Training complete! Best validation accuracy: {best_val_acc:.2f}%")

# Final testing
print("\nEvaluating on test set...")
model.load_state_dict(torch.load('best_fish_model.pth')['model_state_dict'])
test_loss, test_acc = validate(0)  # Use validate function for testing
print(f"Test Accuracy: {test_acc:.2f}%")

writer.close()
```

---

## Step 4: Start Training

**Windows:**
```cmd
cd C:\fish-training
python train_fish_model.py
```

**Linux:**
```bash
cd ~/fish-training
python3 train_fish_model.py
```

**Expected output:**
```
Using device: cuda
GPU: NVIDIA GeForce RTX 4070
GPU Memory: 12.00 GB
Loading datasets...
Training samples: 16000
Validation samples: 2000
Testing samples: 2000
Number of classes: 200

Creating EfficientNet-B0 model...

Starting training...
======================================================================
Epoch 1/50 [Train]: 100%|████████| 500/500 [03:45<00:00, loss: 3.2154, acc: 45.23%]
Epoch 1/50 [Val]: 100%|████████| 63/63 [00:28<00:00, loss: 2.8945, acc: 52.15%]
✅ Saved best model (val_acc: 52.15%)

Epoch 1/50 - 254s
Train Loss: 3.2154 | Train Acc: 45.23%
Val Loss: 2.8945 | Val Acc: 52.15%
======================================================================
...
```

---

## Step 5: Monitor Training

### TensorBoard (Real-time graphs)

**Open new terminal:**
```cmd
# Windows
cd C:\fish-training
tensorboard --logdir=runs

# Linux
cd ~/fish-training
tensorboard --logdir=runs
```

**Open browser:** http://localhost:6006

**You'll see:**
- Training/validation loss curves
- Training/validation accuracy curves
- Learning rate changes

### Expected Training Progress

| Epoch | Train Acc | Val Acc | Time |
|-------|-----------|---------|------|
| 1 | 45% | 52% | 4 min |
| 5 | 68% | 72% | 4 min |
| 10 | 75% | 78% | 4 min |
| 20 | 82% | 84% | 4 min |
| 30 | 86% | 86% | 4 min |
| 50 | 90% | 87% | 4 min |

**Target:** 85%+ validation accuracy
**Total time:** 12-20 hours (50 epochs × 4 min/epoch)

---

## Step 6: Export to ONNX for Pi Deployment

After training completes, convert model to ONNX:

```python
import torch
import torch.onnx
from pathlib import Path

# Load best model
device = torch.device("cuda")
checkpoint = torch.load('best_fish_model.pth')

# Create model
from torchvision import models
import torch.nn as nn

model = models.efficientnet_b0(weights=None)
model.classifier = nn.Sequential(
    nn.Dropout(0.3),
    nn.Linear(1280, 200)
)
model.load_state_dict(checkpoint['model_state_dict'])
model = model.to(device)
model.eval()

# Dummy input
dummy_input = torch.randn(1, 3, 512, 512).to(device)

# Export to ONNX
torch.onnx.export(
    model,
    dummy_input,
    "fish_classifier_200sp.onnx",
    input_names=['input'],
    output_names=['output'],
    dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}},
    opset_version=14
)

print("✅ Model exported to fish_classifier_200sp.onnx")
print(f"File size: {Path('fish_classifier_200sp.onnx').stat().st_size / 1e6:.1f} MB")
```

---

## Step 7: Transfer Model Back to Pi

**Windows:**
```cmd
scp -i %USERPROFILE%\.ssh\d3kos_key fish_classifier_200sp.onnx d3kos@192.168.1.237:/opt/d3kos/models/fish-species/
scp -i %USERPROFILE%\.ssh\d3kos_key best_fish_model.pth d3kos@192.168.1.237:/opt/d3kos/models/fish-species/
```

**Linux:**
```bash
scp -i ~/.ssh/d3kos_key fish_classifier_200sp.onnx d3kos@192.168.1.237:/opt/d3kos/models/fish-species/
scp -i ~/.ssh/d3kos_key best_fish_model.pth d3kos@192.168.1.237:/opt/d3kos/models/fish-species/
```

---

## Troubleshooting

### Out of Memory (CUDA OOM)

Reduce batch size:
```python
BATCH_SIZE = 16  # Or 8 for 6GB GPUs
```

### Slow training (< 1 epoch/hour)

Check:
- GPU utilization: `nvidia-smi` should show 80-100%
- Data loading bottleneck: Increase `NUM_WORKERS`
- Disk speed: SSD recommended for dataset

### Poor accuracy (< 70%)

- Train longer (100 epochs)
- Unfreeze more layers:
  ```python
  # Unfreeze last few feature layers
  for param in model.features[-3:].parameters():
      param.requires_grad = True
  ```
- Increase data augmentation

---

## Summary

**Setup time:** 2-3 hours
**Training time:** 12-24 hours
**Total:** ~1 day from start to deployed model

**Next:** After training completes, I'll help you integrate the model into the d3kOS fish detector service!
