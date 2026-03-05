#!/usr/bin/env python3
"""
Fish Species Dataset Downloader
Downloads images from iNaturalist for worldwide fish identification
Phase 1: 200 species × 100 images = 20,000 images total
"""

import os
import json
import requests
import time
from pathlib import Path
from pyinaturalist import get_observations
from PIL import Image
from io import BytesIO

# Configuration
SPECIES_FILE = "/home/boatiq/Helm-OS/fish_species_phase1.json"
DATASET_ROOT = "/opt/d3kos/datasets/fish-worldwide"
IMAGES_PER_SPECIES = 100
TRAIN_SPLIT = 0.8  # 80% training
VAL_SPLIT = 0.1    # 10% validation
TEST_SPLIT = 0.1   # 10% testing

class FishDatasetDownloader:
    def __init__(self):
        self.species_data = self.load_species_list()
        self.total_species = self.species_data['total_species']
        self.downloaded_count = 0
        self.failed_count = 0

    def load_species_list(self):
        """Load species list from JSON file"""
        with open(SPECIES_FILE, 'r') as f:
            return json.load(f)

    def download_image(self, url, save_path):
        """Download and save a single image"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # Open image and verify it's valid
            img = Image.open(BytesIO(response.content))

            # Convert RGBA to RGB if needed
            if img.mode == 'RGBA':
                img = img.convert('RGB')

            # Resize to 512x512 (standard size for training)
            img = img.resize((512, 512), Image.Resampling.LANCZOS)

            # Save as JPEG
            img.save(save_path, 'JPEG', quality=90)
            return True

        except Exception as e:
            print(f"  ⚠ Failed to download {url}: {e}")
            return False

    def download_species(self, taxon_id, scientific_name, common_name, class_idx):
        """Download all images for a single species"""
        print(f"\n[{class_idx + 1}/{self.total_species}] {common_name} ({scientific_name})")
        print(f"  Taxon ID: {taxon_id}")

        # Create species directories
        species_dir = scientific_name.lower().replace(' ', '_')
        train_dir = Path(DATASET_ROOT) / "train" / f"class_{class_idx:03d}_{species_dir}"
        val_dir = Path(DATASET_ROOT) / "val" / f"class_{class_idx:03d}_{species_dir}"
        test_dir = Path(DATASET_ROOT) / "test" / f"class_{class_idx:03d}_{species_dir}"

        for dir_path in [train_dir, val_dir, test_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Fetch observations from iNaturalist
        print(f"  Fetching observations from iNaturalist...")
        all_photos = []
        page = 1
        max_pages = 10  # Safety limit

        while len(all_photos) < IMAGES_PER_SPECIES and page <= max_pages:
            try:
                observations = get_observations(
                    taxon_id=taxon_id,
                    photos=True,
                    quality_grade='research',  # Only research-grade observations
                    per_page=200,
                    page=page
                )

                if not observations or 'results' not in observations:
                    break

                for obs in observations['results']:
                    if 'photos' in obs and len(obs['photos']) > 0:
                        # Get largest photo
                        photo = obs['photos'][0]
                        photo_url = photo['url'].replace('square', 'large')
                        all_photos.append(photo_url)

                        if len(all_photos) >= IMAGES_PER_SPECIES:
                            break

                page += 1
                time.sleep(1)  # Rate limiting

            except Exception as e:
                print(f"  ⚠ Error fetching page {page}: {e}")
                break

        print(f"  Found {len(all_photos)} photos")

        if len(all_photos) == 0:
            print(f"  ❌ No photos found for {common_name}")
            self.failed_count += 1
            return 0

        # Download images
        downloaded = 0
        for i, photo_url in enumerate(all_photos):
            # Determine split (80/10/10)
            if i < int(len(all_photos) * TRAIN_SPLIT):
                save_dir = train_dir
                split = "train"
            elif i < int(len(all_photos) * (TRAIN_SPLIT + VAL_SPLIT)):
                save_dir = val_dir
                split = "val"
            else:
                save_dir = test_dir
                split = "test"

            # Save path
            filename = f"{species_dir}_{i:04d}.jpg"
            save_path = save_dir / filename

            # Skip if already downloaded
            if save_path.exists():
                downloaded += 1
                continue

            # Download
            if self.download_image(photo_url, save_path):
                downloaded += 1
                if downloaded % 10 == 0:
                    print(f"    {downloaded}/{len(all_photos)} downloaded ({split})")

            # Rate limiting
            time.sleep(0.5)

        print(f"  ✅ Downloaded {downloaded} images")
        print(f"     Train: {len(list(train_dir.glob('*.jpg')))} | " +
              f"Val: {len(list(val_dir.glob('*.jpg')))} | " +
              f"Test: {len(list(test_dir.glob('*.jpg')))}")

        self.downloaded_count += downloaded
        return downloaded

    def create_class_mapping(self):
        """Create class index to species name mapping"""
        mapping = {}
        class_idx = 0

        for region, data in self.species_data['regions'].items():
            for species in data['species']:
                mapping[class_idx] = {
                    'scientific_name': species['scientific_name'],
                    'common_name': species['common_name'],
                    'taxon_id': species['taxon_id'],
                    'region': region
                }
                class_idx += 1

        # Save mapping
        mapping_file = Path(DATASET_ROOT) / "class_mapping.json"
        with open(mapping_file, 'w') as f:
            json.dump(mapping, f, indent=2)

        print(f"\n✅ Class mapping saved to {mapping_file}")
        return mapping

    def download_all(self):
        """Download all species in the dataset"""
        print("=" * 70)
        print("🐟 FISH SPECIES DATASET DOWNLOADER - PHASE 1")
        print("=" * 70)
        print(f"Total species: {self.total_species}")
        print(f"Images per species: {IMAGES_PER_SPECIES}")
        print(f"Target total images: {self.total_species * IMAGES_PER_SPECIES}")
        print(f"Dataset root: {DATASET_ROOT}")
        print("=" * 70)

        # Create class mapping
        class_mapping = self.create_class_mapping()

        # Download each species
        class_idx = 0
        for region, data in self.species_data['regions'].items():
            print(f"\n{'=' * 70}")
            print(f"REGION: {region.upper().replace('_', ' ')}")
            print(f"Species count: {data['species_count']}")
            print(f"{'=' * 70}")

            for species in data['species']:
                self.download_species(
                    taxon_id=species['taxon_id'],
                    scientific_name=species['scientific_name'],
                    common_name=species['common_name'],
                    class_idx=class_idx
                )
                class_idx += 1

        # Final summary
        print("\n" + "=" * 70)
        print("📊 DOWNLOAD COMPLETE")
        print("=" * 70)
        print(f"Total images downloaded: {self.downloaded_count}")
        print(f"Failed species: {self.failed_count}")
        print(f"Success rate: {(self.total_species - self.failed_count) / self.total_species * 100:.1f}%")

        # Count final dataset size
        train_count = len(list(Path(DATASET_ROOT).glob("train/**/*.jpg")))
        val_count = len(list(Path(DATASET_ROOT).glob("val/**/*.jpg")))
        test_count = len(list(Path(DATASET_ROOT).glob("test/**/*.jpg")))

        print(f"\nDataset Split:")
        print(f"  Training:   {train_count} images ({train_count/self.downloaded_count*100:.1f}%)")
        print(f"  Validation: {val_count} images ({val_count/self.downloaded_count*100:.1f}%)")
        print(f"  Testing:    {test_count} images ({test_count/self.downloaded_count*100:.1f}%)")
        print("=" * 70)

        # Estimate disk usage
        import subprocess
        result = subprocess.run(['du', '-sh', DATASET_ROOT], capture_output=True, text=True)
        print(f"\n💾 Disk usage: {result.stdout.split()[0]}")

if __name__ == "__main__":
    downloader = FishDatasetDownloader()
    downloader.download_all()
