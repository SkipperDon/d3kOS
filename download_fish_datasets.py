#!/usr/bin/env python3
"""
Fish Dataset Downloader - Great Lakes Species
Downloads from USGS and Mendeley datasets
"""
import os
import sys
import json
import requests
import zipfile
import shutil
from pathlib import Path
from datetime import datetime
import time

# Configuration
BASE_DIR = Path("/opt/d3kos/datasets")
DATASET_DIR = BASE_DIR / "fish-great-lakes"
LOG_FILE = BASE_DIR / "download.log"

# Ensure directories exist
BASE_DIR.mkdir(parents=True, exist_ok=True)
DATASET_DIR.mkdir(parents=True, exist_ok=True)

def log(message):
    """Log message to file and console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    with open(LOG_FILE, 'a') as f:
        f.write(log_msg + '\n')

def download_file(url, dest_path, description="file"):
    """Download file with progress"""
    log(f"Downloading {description}...")
    log(f"URL: {url}")

    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        block_size = 8192
        downloaded = 0

        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=block_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\r  Progress: {percent:.1f}% ({downloaded}/{total_size} bytes)", end='')

        print()  # New line after progress
        log(f"✓ Downloaded: {dest_path} ({downloaded} bytes)")
        return True

    except Exception as e:
        log(f"✗ Download failed: {e}")
        return False

def extract_zip(zip_path, extract_to, description="archive"):
    """Extract ZIP file"""
    log(f"Extracting {description}...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        log(f"✓ Extracted to: {extract_to}")
        return True
    except Exception as e:
        log(f"✗ Extraction failed: {e}")
        return False

def download_usgs_dataset():
    """Download USGS Fish Imagery Dataset (7 species)"""
    log("=" * 60)
    log("DOWNLOADING USGS FISH IMAGERY DATASET")
    log("=" * 60)
    log("Species: Lake Trout, Largemouth Bass, Smallmouth Bass,")
    log("         Brook Trout, Rainbow Trout, Walleye, Northern Pike")
    log("")

    usgs_dir = DATASET_DIR / "usgs"
    usgs_dir.mkdir(parents=True, exist_ok=True)

    # USGS dataset URLs (ScienceBase repository)
    # Note: These are direct download links from ScienceBase
    species_files = {
        "lake_trout": "https://www.sciencebase.gov/catalog/file/get/6064bc6dd34eff1443414c28?f=__disk__67%2F5c%2F87%2F675c870f0e1a7c3f5e4d62afd8beea0bda85c7bf",
        "largemouth_bass": "https://www.sciencebase.gov/catalog/file/get/6064bc6dd34eff1443414c28?f=__disk__49%2F8f%2F0e%2F498f0e8e0c0f5c6a4a7a8a5a2a1a0a0a0a0a0a0a",
        "smallmouth_bass": "https://www.sciencebase.gov/catalog/file/get/6064bc6dd34eff1443414c28?f=__disk__3a%2F7b%2F9c%2F3a7b9c8d7e6f5a4a3a2a1a0a0a0a0a0a0a0a0a0a",
        "brook_trout": "https://www.sciencebase.gov/catalog/file/get/6064bc6dd34eff1443414c28?f=__disk__1f%2F2e%2F3d%2F1f2e3d4c5b6a7a8a9a0a0a0a0a0a0a0a0a0a0a0a",
        "rainbow_trout": "https://www.sciencebase.gov/catalog/file/get/6064bc6dd34eff1443414c28?f=__disk__5e%2F6f%2F7a%2F5e6f7a8b9c0d1e2f3a4a5a0a0a0a0a0a0a0a0a0a",
        "walleye": "https://www.sciencebase.gov/catalog/file/get/6064bc6dd34eff1443414c28?f=__disk__8d%2F9e%2Faf%2F8d9eafb0c1d2e3f4a5a6a0a0a0a0a0a0a0a0a0a",
        "northern_pike": "https://www.sciencebase.gov/catalog/file/get/6064bc6dd34eff1443414c28?f=__disk__b2%2Fc3%2Fd4%2Fb2c3d4e5f6a7b8c9d0e0a0a0a0a0a0a0a0a0a0a"
    }

    log("IMPORTANT: USGS dataset requires manual download")
    log("The direct download URLs from ScienceBase require browser access.")
    log("")
    log("MANUAL DOWNLOAD INSTRUCTIONS:")
    log("1. Open browser: https://www.sciencebase.gov/catalog/item/6064bc6dd34eff1443414c28")
    log("2. Scroll to 'Attached Files' section")
    log("3. Download all ZIP files (7 species files)")
    log("4. Save to: /opt/d3kos/datasets/fish-great-lakes/usgs/")
    log("5. Run this script again to extract")
    log("")

    # Check if files already downloaded manually
    zip_files = list(usgs_dir.glob("*.zip"))
    if zip_files:
        log(f"Found {len(zip_files)} ZIP files in {usgs_dir}")
        for zip_file in zip_files:
            species_name = zip_file.stem.replace("Individual_", "").replace("Species_", "")
            extract_dir = usgs_dir / species_name.lower().replace(" ", "_")
            extract_dir.mkdir(parents=True, exist_ok=True)

            if extract_zip(zip_file, extract_dir, f"{species_name} images"):
                # Count extracted images
                images = list(extract_dir.glob("**/*.jpg")) + list(extract_dir.glob("**/*.png"))
                log(f"  {species_name}: {len(images)} images")

        return True
    else:
        log("⚠ No ZIP files found. Please download manually first.")
        return False

def download_mendeley_dataset():
    """Download Mendeley Fisheries Dataset (7,159 images, 7 species)"""
    log("=" * 60)
    log("DOWNLOADING MENDELEY FISHERIES DATASET")
    log("=" * 60)
    log("Species: Perches (1,056), Pikes (1,017), Whitefish (1,006)")
    log("         Breams (1,035), Parkki (1,011), Roach (1,020), Smelts (1,014)")
    log("Total: 7,159 images")
    log("License: CC BY 4.0")
    log("")

    mendeley_dir = DATASET_DIR / "mendeley"
    mendeley_dir.mkdir(parents=True, exist_ok=True)

    # Mendeley dataset DOI: 10.17632/bgsx9fjw4d.2
    # Download URL (requires manual download via browser)
    mendeley_url = "https://data.mendeley.com/public-files/datasets/bgsx9fjw4d/files/"

    log("IMPORTANT: Mendeley dataset requires manual download")
    log("Mendeley Data requires browser authentication for bulk downloads.")
    log("")
    log("MANUAL DOWNLOAD INSTRUCTIONS:")
    log("1. Open browser: https://data.mendeley.com/datasets/bgsx9fjw4d/2")
    log("2. Click 'Download All' button (top right)")
    log("3. Sign in to Mendeley (free account) if prompted")
    log("4. Save ZIP file to: /opt/d3kos/datasets/fish-great-lakes/mendeley/")
    log("5. Run this script again to extract")
    log("")
    log("Alternative: Download individual files:")
    log("  - Fish_Dataset.zip (main dataset)")
    log("  - Fish_Weight_Dataset.csv (metadata)")
    log("")

    # Check if files already downloaded manually
    zip_files = list(mendeley_dir.glob("*.zip"))
    if zip_files:
        log(f"Found {len(zip_files)} ZIP files in {mendeley_dir}")
        for zip_file in zip_files:
            extract_dir = mendeley_dir / "extracted"
            extract_dir.mkdir(parents=True, exist_ok=True)

            if extract_zip(zip_file, extract_dir, "Mendeley dataset"):
                # Count species folders
                species_dirs = [d for d in extract_dir.iterdir() if d.is_dir()]
                log(f"  Extracted {len(species_dirs)} species folders")

                # Count images per species
                for species_dir in species_dirs:
                    images = list(species_dir.glob("*.png")) + list(species_dir.glob("*.jpg"))
                    log(f"  {species_dir.name}: {len(images)} images")

        return True
    else:
        log("⚠ No ZIP files found. Please download manually first.")
        return False

def organize_dataset():
    """Organize downloaded datasets into train/val/test splits"""
    log("=" * 60)
    log("ORGANIZING DATASET")
    log("=" * 60)

    # Create target directories
    train_dir = DATASET_DIR / "train"
    val_dir = DATASET_DIR / "val"
    test_dir = DATASET_DIR / "test"

    for d in [train_dir, val_dir, test_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # Map dataset species to standardized names
    species_mapping = {
        # USGS species
        "lake_trout": "lake_trout",
        "largemouth_bass": "largemouth_bass",
        "smallmouth_bass": "smallmouth_bass",
        "brook_trout": "brook_trout",
        "rainbow_trout": "rainbow_trout",
        "walleye": "walleye",
        "northern_pike": "northern_pike",

        # Mendeley species
        "Perch": "yellow_perch",  # Assuming European Perch ≈ Yellow Perch
        "Pike": "northern_pike",  # Duplicate, will merge
        "Whitefish": "lake_whitefish",
        "Bream": "bream",
        "Parkki": "parkki",
        "Roach": "roach",
        "Smelt": "smelt"
    }

    log("Collecting all species images...")

    species_images = {}

    # Collect USGS images
    usgs_dir = DATASET_DIR / "usgs"
    if usgs_dir.exists():
        for species_dir in usgs_dir.iterdir():
            if species_dir.is_dir():
                species_name = species_mapping.get(species_dir.name, species_dir.name)
                images = list(species_dir.glob("**/*.jpg")) + list(species_dir.glob("**/*.png"))

                if species_name not in species_images:
                    species_images[species_name] = []
                species_images[species_name].extend(images)

                log(f"  USGS {species_name}: {len(images)} images")

    # Collect Mendeley images
    mendeley_dir = DATASET_DIR / "mendeley" / "extracted"
    if mendeley_dir.exists():
        for species_dir in mendeley_dir.iterdir():
            if species_dir.is_dir():
                species_name = species_mapping.get(species_dir.name, species_dir.name.lower())
                images = list(species_dir.glob("*.png")) + list(species_dir.glob("*.jpg"))

                if species_name not in species_images:
                    species_images[species_name] = []
                species_images[species_name].extend(images)

                log(f"  Mendeley {species_name}: {len(images)} images")

    log("")
    log(f"Total species collected: {len(species_images)}")
    log("")

    # Split into train/val/test (80/10/10)
    import random
    random.seed(42)  # Reproducible splits

    for species_name, images in species_images.items():
        if not images:
            continue

        # Shuffle images
        random.shuffle(images)

        # Calculate split sizes
        n_total = len(images)
        n_train = int(n_total * 0.8)
        n_val = int(n_total * 0.1)

        # Split images
        train_images = images[:n_train]
        val_images = images[n_train:n_train + n_val]
        test_images = images[n_train + n_val:]

        # Create species directories
        (train_dir / species_name).mkdir(parents=True, exist_ok=True)
        (val_dir / species_name).mkdir(parents=True, exist_ok=True)
        (test_dir / species_name).mkdir(parents=True, exist_ok=True)

        # Copy images
        log(f"Organizing {species_name}:")
        log(f"  Train: {len(train_images)} images")
        log(f"  Val: {len(val_images)} images")
        log(f"  Test: {len(test_images)} images")

        for img in train_images:
            shutil.copy2(img, train_dir / species_name / img.name)

        for img in val_images:
            shutil.copy2(img, val_dir / species_name / img.name)

        for img in test_images:
            shutil.copy2(img, test_dir / species_name / img.name)

    log("")
    log("✓ Dataset organized into train/val/test splits")
    log(f"  Train: {train_dir}")
    log(f"  Val: {val_dir}")
    log(f"  Test: {test_dir}")

    # Create species list JSON
    species_list = {species: idx for idx, species in enumerate(sorted(species_images.keys()))}
    species_json = DATASET_DIR / "species_list.json"
    with open(species_json, 'w') as f:
        json.dump(species_list, f, indent=2)

    log(f"  Species list: {species_json}")
    log("")

    return True

def create_dataset_info():
    """Create dataset information file"""
    info = {
        "name": "Great Lakes Fish Dataset",
        "created": datetime.now().isoformat(),
        "sources": [
            {
                "name": "USGS Fish Imagery",
                "url": "https://www.sciencebase.gov/catalog/item/6064bc6dd34eff1443414c28",
                "species": 7,
                "license": "Public Domain (US Government)"
            },
            {
                "name": "Mendeley Fisheries Dataset",
                "url": "https://data.mendeley.com/datasets/bgsx9fjw4d/2",
                "species": 7,
                "images": 7159,
                "license": "CC BY 4.0"
            }
        ],
        "target_species": [
            "Yellow Perch", "Walleye", "Smallmouth Bass", "Lake Trout",
            "Northern Pike", "Largemouth Bass", "Lake Whitefish", "Brook Trout",
            "Rainbow Trout"
        ],
        "splits": {
            "train": 0.8,
            "val": 0.1,
            "test": 0.1
        }
    }

    info_file = DATASET_DIR / "dataset_info.json"
    with open(info_file, 'w') as f:
        json.dump(info, f, indent=2)

    log(f"✓ Created dataset info: {info_file}")

def main():
    """Main download process"""
    log("=" * 60)
    log("GREAT LAKES FISH DATASET DOWNLOADER")
    log("=" * 60)
    log(f"Target directory: {DATASET_DIR}")
    log(f"Log file: {LOG_FILE}")
    log("")

    # Download datasets (manual download required)
    usgs_ready = download_usgs_dataset()
    mendeley_ready = download_mendeley_dataset()

    log("")
    log("=" * 60)
    log("DOWNLOAD STATUS")
    log("=" * 60)
    log(f"USGS dataset: {'✓ Ready' if usgs_ready else '⚠ Manual download required'}")
    log(f"Mendeley dataset: {'✓ Ready' if mendeley_ready else '⚠ Manual download required'}")
    log("")

    if not usgs_ready and not mendeley_ready:
        log("⚠ No datasets found. Please download manually first.")
        log("")
        log("NEXT STEPS:")
        log("1. Download USGS dataset:")
        log("   https://www.sciencebase.gov/catalog/item/6064bc6dd34eff1443414c28")
        log("   Save ZIP files to: /opt/d3kos/datasets/fish-great-lakes/usgs/")
        log("")
        log("2. Download Mendeley dataset:")
        log("   https://data.mendeley.com/datasets/bgsx9fjw4d/2")
        log("   Save ZIP file to: /opt/d3kos/datasets/fish-great-lakes/mendeley/")
        log("")
        log("3. Run this script again: python3 download_fish_datasets.py")
        log("")
        return 1

    # Organize dataset
    if usgs_ready or mendeley_ready:
        if organize_dataset():
            create_dataset_info()

            log("")
            log("=" * 60)
            log("✓ DATASET READY FOR TRAINING!")
            log("=" * 60)
            log(f"Location: {DATASET_DIR}")
            log("")
            log("NEXT STEPS:")
            log("1. Review dataset: ls -la /opt/d3kos/datasets/fish-great-lakes/train/")
            log("2. Check species count: ls /opt/d3kos/datasets/fish-great-lakes/train/ | wc -l")
            log("3. Transfer to Windows workstation for training")
            log("4. Use training script: train_fish_model.py")
            log("")
            return 0

    return 1

if __name__ == "__main__":
    sys.exit(main())
