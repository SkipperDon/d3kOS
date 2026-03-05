"""
Fish Species Classifier Training Script
Works with existing fish-species-image-data dataset
Optimized for NVIDIA RTX 3060 Ti (8GB VRAM)

Dataset structure:
C:\fish-training\fish-species-image-data\Fish_data\images\
    - cropped\
    - numbered\
    - raw_image\

Index file: final_all_index.txt (maps filenames to species)
"""

import os
import sys
import json
import time
from pathlib import Path
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models
from PIL import Image
import numpy as np
from sklearn.model_selection import train_test_split
from tqdm import tqdm

# Configuration
DATASET_ROOT = r"C:\fish-training\fish-species-image-data\Fish_data\images"
INDEX_FILE = r"C:\fish-training\final_all_index.txt"
OUTPUT_DIR = r"C:\fish-training\output"
MODEL_NAME = "fish_classifier_483species"

# Training hyperparameters (optimized for RTX 3060 Ti 8GB VRAM)
BATCH_SIZE = 32  # Safe for 8GB VRAM with EfficientNet-B0
IMG_SIZE = 512
NUM_EPOCHS = 50
LEARNING_RATE = 0.001
NUM_WORKERS = 4  # Adjust based on CPU cores

# Device configuration
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")


class FishDataset(Dataset):
    """Custom dataset for fish species images"""

    def __init__(self, image_paths, labels, transform=None):
        self.image_paths = image_paths
        self.labels = labels
        self.transform = transform

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        label = self.labels[idx]

        try:
            image = Image.open(img_path).convert('RGB')
        except Exception as e:
            print(f"Error loading {img_path}: {e}")
            # Return black image on error
            image = Image.new('RGB', (IMG_SIZE, IMG_SIZE), (0, 0, 0))

        if self.transform:
            image = self.transform(image)

        return image, label


def parse_index_file(index_path):
    """Parse the final_all_index.txt file to map filenames to species"""
    print(f"\nParsing index file: {index_path}")

    if not os.path.exists(index_path):
        print(f"ERROR: Index file not found: {index_path}")
        print("Please copy final_all_index.txt to C:\\fish-training\\")
        sys.exit(1)

    filename_to_species = {}
    species_to_id = {}
    species_count = {}

    with open(index_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Format: species_id=species_name=image_type=filename=global_id
            parts = line.split('=')
            if len(parts) >= 4:
                species_id = parts[0]
                species_name = parts[1]
                filename = parts[3]  # Filename without extension

                # Map filename to species
                filename_to_species[filename] = species_name

                # Track species IDs
                if species_name not in species_to_id:
                    species_to_id[species_name] = len(species_to_id)

                # Count images per species
                species_count[species_name] = species_count.get(species_name, 0) + 1

    print(f"✓ Parsed {len(filename_to_species)} image entries")
    print(f"✓ Found {len(species_to_id)} unique species")
    print(f"✓ Average images per species: {len(filename_to_species) / len(species_to_id):.1f}")

    return filename_to_species, species_to_id, species_count


def find_images(dataset_root, filename_to_species):
    """Find all images across the three subdirectories"""
    print(f"\nSearching for images in: {dataset_root}")

    if not os.path.exists(dataset_root):
        print(f"ERROR: Dataset directory not found: {dataset_root}")
        sys.exit(1)

    subdirs = ['cropped', 'numbered', 'raw_image']
    image_paths = []
    labels = []
    found_count = 0
    missing_count = 0

    for filename_base in tqdm(filename_to_species.keys(), desc="Finding images"):
        species = filename_to_species[filename_base]
        found = False

        # Search in all three subdirectories
        for subdir in subdirs:
            for ext in ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']:
                img_path = os.path.join(dataset_root, subdir, filename_base + ext)
                if os.path.exists(img_path):
                    image_paths.append(img_path)
                    labels.append(species)
                    found = True
                    found_count += 1
                    break
            if found:
                break

        if not found:
            missing_count += 1

    print(f"\n✓ Found {found_count} images")
    if missing_count > 0:
        print(f"⚠ Missing {missing_count} images from index")

    return image_paths, labels


def create_data_loaders(image_paths, labels, species_to_id, batch_size):
    """Create train and validation data loaders"""
    print("\nCreating data loaders...")

    # Convert species names to numeric labels
    numeric_labels = [species_to_id[label] for label in labels]

    # Split into train/validation (80/20)
    X_train, X_val, y_train, y_val = train_test_split(
        image_paths, numeric_labels, test_size=0.2, random_state=42, stratify=numeric_labels
    )

    print(f"✓ Training set: {len(X_train)} images")
    print(f"✓ Validation set: {len(X_val)} images")

    # Data augmentation for training
    train_transform = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    # No augmentation for validation
    val_transform = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    # Create datasets
    train_dataset = FishDataset(X_train, y_train, transform=train_transform)
    val_dataset = FishDataset(X_val, y_val, transform=val_transform)

    # Create data loaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=NUM_WORKERS,
        pin_memory=True
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=NUM_WORKERS,
        pin_memory=True
    )

    return train_loader, val_loader


def create_model(num_classes):
    """Create EfficientNet-B0 model (optimized for RTX 3060 Ti)"""
    print(f"\nCreating EfficientNet-B0 model for {num_classes} classes...")

    # Load pre-trained EfficientNet-B0
    model = models.efficientnet_b0(weights='IMAGENET1K_V1')

    # Replace final classifier layer
    num_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(num_features, num_classes)

    model = model.to(device)
    print(f"✓ Model loaded on {device}")

    return model


def train_one_epoch(model, train_loader, criterion, optimizer, epoch):
    """Train for one epoch"""
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{NUM_EPOCHS}")
    for images, labels in pbar:
        images, labels = images.to(device), labels.to(device)

        # Forward pass
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)

        # Backward pass
        loss.backward()
        optimizer.step()

        # Statistics
        running_loss += loss.item()
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

        # Update progress bar
        pbar.set_postfix({
            'loss': f'{running_loss/len(train_loader):.4f}',
            'acc': f'{100*correct/total:.2f}%'
        })

    epoch_loss = running_loss / len(train_loader)
    epoch_acc = 100 * correct / total

    return epoch_loss, epoch_acc


def validate(model, val_loader, criterion):
    """Validate the model"""
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in tqdm(val_loader, desc="Validation"):
            images, labels = images.to(device), labels.to(device)

            outputs = model(images)
            loss = criterion(outputs, labels)

            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    val_loss = running_loss / len(val_loader)
    val_acc = 100 * correct / total

    return val_loss, val_acc


def save_model(model, species_to_id, output_dir, model_name):
    """Save model and metadata"""
    os.makedirs(output_dir, exist_ok=True)

    # Save PyTorch model
    model_path = os.path.join(output_dir, f"{model_name}.pth")
    torch.save(model.state_dict(), model_path)
    print(f"\n✓ Model saved: {model_path}")

    # Save species mapping
    mapping_path = os.path.join(output_dir, f"{model_name}_species.json")
    with open(mapping_path, 'w') as f:
        json.dump(species_to_id, f, indent=2)
    print(f"✓ Species mapping saved: {mapping_path}")

    # Export to ONNX for Raspberry Pi
    print("\nExporting to ONNX format for Raspberry Pi...")
    model.eval()
    dummy_input = torch.randn(1, 3, IMG_SIZE, IMG_SIZE).to(device)
    onnx_path = os.path.join(output_dir, f"{model_name}.onnx")

    torch.onnx.export(
        model,
        dummy_input,
        onnx_path,
        export_params=True,
        opset_version=11,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
    )
    print(f"✓ ONNX model saved: {onnx_path}")
    print(f"  File size: {os.path.getsize(onnx_path) / 1024**2:.2f} MB")


def main():
    """Main training function"""
    print("="*60)
    print("Fish Species Classifier Training")
    print("="*60)

    start_time = time.time()

    # Step 1: Parse index file
    filename_to_species, species_to_id, species_count = parse_index_file(INDEX_FILE)
    num_classes = len(species_to_id)

    # Step 2: Find images
    image_paths, labels = find_images(DATASET_ROOT, filename_to_species)

    if len(image_paths) == 0:
        print("\nERROR: No images found!")
        print("Please check:")
        print(f"1. Dataset location: {DATASET_ROOT}")
        print(f"2. Index file: {INDEX_FILE}")
        sys.exit(1)

    # Step 3: Create data loaders
    train_loader, val_loader = create_data_loaders(
        image_paths, labels, species_to_id, BATCH_SIZE
    )

    # Step 4: Create model
    model = create_model(num_classes)

    # Step 5: Setup training
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.5, patience=3, verbose=True
    )

    # Step 6: Training loop
    print("\n" + "="*60)
    print("Starting training...")
    print("="*60)

    best_val_acc = 0.0
    history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}

    for epoch in range(NUM_EPOCHS):
        # Train
        train_loss, train_acc = train_one_epoch(model, train_loader, criterion, optimizer, epoch)

        # Validate
        val_loss, val_acc = validate(model, val_loader, criterion)

        # Learning rate scheduling
        scheduler.step(val_loss)

        # Save history
        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)

        # Print epoch summary
        print(f"\nEpoch {epoch+1}/{NUM_EPOCHS} Summary:")
        print(f"  Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")
        print(f"  Val Loss:   {val_loss:.4f} | Val Acc:   {val_acc:.2f}%")

        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            save_model(model, species_to_id, OUTPUT_DIR, f"{MODEL_NAME}_best")
            print(f"  ★ New best model saved! (Val Acc: {val_acc:.2f}%)")

    # Step 7: Save final model
    save_model(model, species_to_id, OUTPUT_DIR, f"{MODEL_NAME}_final")

    # Save training history
    history_path = os.path.join(OUTPUT_DIR, "training_history.json")
    with open(history_path, 'w') as f:
        json.dump(history, f, indent=2)
    print(f"\n✓ Training history saved: {history_path}")

    # Training complete
    elapsed_time = time.time() - start_time
    hours = int(elapsed_time // 3600)
    minutes = int((elapsed_time % 3600) // 60)

    print("\n" + "="*60)
    print("Training Complete!")
    print("="*60)
    print(f"Total time: {hours}h {minutes}m")
    print(f"Best validation accuracy: {best_val_acc:.2f}%")
    print(f"\nModel files saved to: {OUTPUT_DIR}")
    print("\nNext steps:")
    print("1. Transfer the .onnx file to Raspberry Pi:")
    print(f"   scp {OUTPUT_DIR}\\{MODEL_NAME}_best.onnx d3kos@192.168.1.237:/opt/d3kos/models/marine-vision/")
    print("2. Update fish_detector.py to use the new model")
    print("3. Test on real camera captures!")


if __name__ == "__main__":
    main()
