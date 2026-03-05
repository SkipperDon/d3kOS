#!/usr/bin/env python3
"""
Fish Species Classification Model Training
EfficientNet-B0 for 200 species worldwide
Optimized for NVIDIA GPU workstation
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from torch.utils.tensorboard import SummaryWriter
from pathlib import Path
import time
import json
from tqdm import tqdm

# Configuration
DATASET_ROOT = Path("C:/fish-training/dataset/fish-worldwide")  # CHANGE THIS for your system
BATCH_SIZE = 32  # Adjust: 16 for 6GB GPU, 32 for 8GB+, 64 for 12GB+
NUM_EPOCHS = 50
LEARNING_RATE = 0.001
NUM_CLASSES = None  # Auto-detect from dataset
IMAGE_SIZE = 512
NUM_WORKERS = 4

# Device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("=" * 70)
print("🐟 FISH SPECIES MODEL TRAINING")
print("=" * 70)
print(f"Device: {device}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    print(f"CUDA Version: {torch.version.cuda}")
else:
    print("⚠️ WARNING: CUDA not available! Training will be VERY slow on CPU.")
    print("   Please install CUDA and PyTorch with GPU support.")
print("=" * 70)

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
print("\n📂 Loading datasets...")
print(f"Dataset root: {DATASET_ROOT}")

if not DATASET_ROOT.exists():
    print(f"\n❌ ERROR: Dataset not found at {DATASET_ROOT}")
    print("Please update DATASET_ROOT in the script to point to your dataset location.")
    exit(1)

train_dataset = datasets.ImageFolder(DATASET_ROOT / "train", transform=train_transform)
val_dataset = datasets.ImageFolder(DATASET_ROOT / "val", transform=val_transform)
test_dataset = datasets.ImageFolder(DATASET_ROOT / "test", transform=val_transform)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True,
                          num_workers=NUM_WORKERS, pin_memory=True)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False,
                        num_workers=NUM_WORKERS, pin_memory=True)
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False,
                         num_workers=NUM_WORKERS, pin_memory=True)

print(f"✅ Training samples: {len(train_dataset)}")
print(f"✅ Validation samples: {len(val_dataset)}")
print(f"✅ Testing samples: {len(test_dataset)}")
print(f"✅ Number of classes: {len(train_dataset.classes)}")
print(f"✅ Batch size: {BATCH_SIZE}")

# Auto-detect number of classes from dataset
NUM_CLASSES = len(train_dataset.classes)
print(f"✅ Auto-detected {NUM_CLASSES} species classes from dataset")

# Save class mapping
class_mapping = {str(idx): class_name for class_name, idx in train_dataset.class_to_idx.items()}
with open('class_mapping.json', 'w') as f:
    json.dump(class_mapping, f, indent=2)
print("✅ Class mapping saved to class_mapping.json")

# Create model
print("\n🤖 Creating EfficientNet-B0 model...")
model = models.efficientnet_b0(weights='IMAGENET1K_V1')  # Pretrained on ImageNet

# Freeze early layers (transfer learning)
for param in model.features.parameters():
    param.requires_grad = False

# Replace classifier for detected number of fish species
model.classifier = nn.Sequential(
    nn.Dropout(0.3),
    nn.Linear(1280, NUM_CLASSES)
)

model = model.to(device)
print(f"✅ Model created with {NUM_CLASSES} output classes")

# Count parameters
total_params = sum(p.numel() for p in model.parameters())
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"✅ Total parameters: {total_params:,}")
print(f"✅ Trainable parameters: {trainable_params:,}")

# Loss and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.classifier.parameters(), lr=LEARNING_RATE)
scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5,
                                                   patience=3, verbose=True)

# TensorBoard
writer = SummaryWriter('runs/fish_classification')
print("✅ TensorBoard logging to: runs/fish_classification")
print("   View with: tensorboard --logdir=runs")

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

        pbar.set_postfix({
            'loss': f"{running_loss / (i + 1):.4f}",
            'acc': f"{100. * correct / total:.2f}%"
        })

    epoch_loss = running_loss / len(train_loader)
    epoch_acc = 100. * correct / total
    return epoch_loss, epoch_acc

# Validation function
def validate(epoch, phase="Val"):
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0

    loader = val_loader if phase == "Val" else test_loader

    with torch.no_grad():
        pbar = tqdm(loader, desc=f"Epoch {epoch+1}/{NUM_EPOCHS} [{phase}]")
        for i, (images, labels) in enumerate(pbar):
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)

            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

            pbar.set_postfix({
                'loss': f"{running_loss / (i + 1):.4f}",
                'acc': f"{100. * correct / total:.2f}%"
            })

    epoch_loss = running_loss / len(loader)
    epoch_acc = 100. * correct / total
    return epoch_loss, epoch_acc

# Training loop
best_val_acc = 0.0
training_history = {
    'train_loss': [],
    'train_acc': [],
    'val_loss': [],
    'val_acc': []
}

print("\n" + "=" * 70)
print("🚀 STARTING TRAINING")
print("=" * 70)
print(f"Epochs: {NUM_EPOCHS}")
print(f"Learning rate: {LEARNING_RATE}")
print(f"Estimated time: {NUM_EPOCHS * 4 / 60:.1f} hours (4 min/epoch)")
print("=" * 70 + "\n")

for epoch in range(NUM_EPOCHS):
    start_time = time.time()

    # Train
    train_loss, train_acc = train_epoch(epoch)
    training_history['train_loss'].append(train_loss)
    training_history['train_acc'].append(train_acc)

    # Validate
    val_loss, val_acc = validate(epoch, "Val")
    training_history['val_loss'].append(val_loss)
    training_history['val_acc'].append(val_acc)

    # Learning rate scheduling
    scheduler.step(val_loss)

    # Log to TensorBoard
    writer.add_scalar('Loss/train', train_loss, epoch)
    writer.add_scalar('Loss/val', val_loss, epoch)
    writer.add_scalar('Accuracy/train', train_acc, epoch)
    writer.add_scalar('Accuracy/val', val_acc, epoch)
    writer.add_scalar('Learning_rate', optimizer.param_groups[0]['lr'], epoch)

    # Save best model
    if val_acc > best_val_acc:
        best_val_acc = val_acc
        torch.save({
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'val_acc': val_acc,
            'val_loss': val_loss,
            'class_to_idx': train_dataset.class_to_idx
        }, 'best_fish_model.pth')
        print(f"\n✅ Saved best model (val_acc: {val_acc:.2f}%)")

    # Save checkpoint every 10 epochs
    if (epoch + 1) % 10 == 0:
        torch.save({
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'val_acc': val_acc,
            'val_loss': val_loss,
        }, f'checkpoint_epoch_{epoch+1}.pth')

    epoch_time = time.time() - start_time
    print(f"\n📊 Epoch {epoch+1}/{NUM_EPOCHS} - {epoch_time:.0f}s ({epoch_time/60:.1f} min)")
    print(f"   Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")
    print(f"   Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.2f}%")
    print(f"   Best Val Acc: {best_val_acc:.2f}%")
    print("=" * 70)

# Save training history
with open('training_history.json', 'w') as f:
    json.dump(training_history, f, indent=2)

print(f"\n🎉 TRAINING COMPLETE!")
print(f"Best validation accuracy: {best_val_acc:.2f}%")
print("=" * 70)

# Final testing
print("\n📊 Evaluating on test set...")
model.load_state_dict(torch.load('best_fish_model.pth')['model_state_dict'])
test_loss, test_acc = validate(0, "Test")
print(f"\n✅ Test Accuracy: {test_acc:.2f}%")
print("=" * 70)

# Export to ONNX
print("\n📦 Exporting model to ONNX format...")
model.eval()
dummy_input = torch.randn(1, 3, IMAGE_SIZE, IMAGE_SIZE).to(device)

try:
    torch.onnx.export(
        model,
        dummy_input,
        "fish_classifier_200sp.onnx",
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}},
        opset_version=14,
        verbose=False
    )
    onnx_size = Path('fish_classifier_200sp.onnx').stat().st_size / 1e6
    print(f"✅ ONNX model exported: fish_classifier_200sp.onnx ({onnx_size:.1f} MB)")
except Exception as e:
    print(f"⚠️ ONNX export failed: {e}")
    print("   Model saved as PyTorch (.pth) only")

writer.close()

print("\n" + "=" * 70)
print("📁 FILES CREATED:")
print("=" * 70)
print("  best_fish_model.pth          - Best model (PyTorch format)")
print("  fish_classifier_200sp.onnx   - ONNX model for Pi deployment")
print("  class_mapping.json           - Class index to species mapping")
print("  training_history.json        - Loss/accuracy per epoch")
print("  checkpoint_epoch_*.pth       - Training checkpoints")
print("=" * 70)
print("\n🎯 NEXT STEP: Transfer ONNX model to Raspberry Pi:")
print(f"   scp fish_classifier_200sp.onnx d3kos@192.168.1.237:/opt/d3kos/models/fish-species/")
print("=" * 70)
