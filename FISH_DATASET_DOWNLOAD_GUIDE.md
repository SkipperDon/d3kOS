# Great Lakes Fish Dataset Download Guide

**Date:** 2026-02-27
**Goal:** Download 7,000+ images for 10+ Great Lakes fish species
**Status:** Manual download required (browser authentication needed)

---

## Quick Summary

**Two Datasets Found:**
1. **USGS Fish Imagery** - 7 species (free, public domain)
2. **Mendeley Fisheries** - 7,159 images, 7 species (free, CC BY 4.0)

**Species Coverage:** 10+ species including Yellow Perch, Walleye, Bass, Pike, Trout, Whitefish

---

## Option 1: USGS Dataset (7 Great Lakes Species)

### Species Included:
- Lake Trout
- Largemouth Bass
- Smallmouth Bass
- Brook Trout
- Rainbow Trout
- Walleye
- Northern Pike

### Download Instructions:

**Step 1: Visit USGS ScienceBase**
```
URL: https://www.sciencebase.gov/catalog/item/6064bc6dd34eff1443414c28
```

**Step 2: Download Files**
- Scroll down to "Attached Files" section
- You'll see 7 ZIP files (one per species)
- Click each file name to download:
  - Individual_BrookTrout.zip
  - Individual_LakeTrout.zip
  - Individual_LargemouthBass.zip
  - Individual_SmallmouthBass.zip
  - Individual_RainbowTrout.zip
  - Individual_Walleye.zip
  - Individual_NorthernPike.zip

**Step 3: Save to Pi**
```bash
# On your Windows machine, transfer files to Pi:
scp -i ~/.ssh/d3kos_key ~/Downloads/Individual_*.zip d3kos@192.168.1.237:/opt/d3kos/datasets/fish-great-lakes/usgs/
```

**Step 4: Extract on Pi**
```bash
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237
cd /opt/d3kos/datasets/fish-great-lakes/usgs/
for zip in *.zip; do unzip -q "$zip" -d "${zip%.zip}"; done
```

**Expected Result:**
- 7 species folders with images
- Each species has multiple annotated fish photos

---

## Option 2: Mendeley Dataset (7,159 Images!)

### Species Included:
- **Perches: 1,056 images** (Yellow Perch equivalent)
- **Pikes: 1,017 images** (Northern Pike)
- **Whitefish: 1,006 images** (Lake Whitefish)
- Breams: 1,035 images
- Parkki: 1,011 images
- Roach: 1,020 images
- Smelts: 1,014 images

### Download Instructions:

**Step 1: Visit Mendeley Data**
```
URL: https://data.mendeley.com/datasets/bgsx9fjw4d/2
```

**Step 2: Create Free Account (if needed)**
- Click "Download All" button (top right)
- Sign in with Google/Microsoft or create Mendeley account (free)
- No payment required - dataset is free under CC BY 4.0 license

**Step 3: Download ZIP**
- After sign-in, download starts automatically
- File: ~50-100 MB ZIP archive
- Contains all 7,159 images organized by species

**Step 4: Transfer to Pi**
```bash
# On your Windows machine:
scp -i ~/.ssh/d3kos_key ~/Downloads/bgsx9fjw4d.zip d3kos@192.168.1.237:/opt/d3kos/datasets/fish-great-lakes/mendeley/

# Extract on Pi:
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237
cd /opt/d3kos/datasets/fish-great-lakes/mendeley/
unzip -q bgsx9fjw4d.zip
```

**Expected Result:**
- 7 species folders
- 1,000+ images per major species
- CSV file with fish measurements (weight, length)

---

## Step-by-Step Process (Complete Workflow)

### 1. Prepare Directories on Pi

```bash
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237
sudo mkdir -p /opt/d3kos/datasets/fish-great-lakes/{usgs,mendeley}
sudo chown -R d3kos:d3kos /opt/d3kos/datasets/
```

### 2. Download USGS Dataset (Browser)

1. Open: https://www.sciencebase.gov/catalog/item/6064bc6dd34eff1443414c28
2. Download all 7 ZIP files (Individual_*.zip)
3. Save to: `C:\Users\donmo\Downloads\`

### 3. Download Mendeley Dataset (Browser)

1. Open: https://data.mendeley.com/datasets/bgsx9fjw4d/2
2. Click "Download All"
3. Sign in (free account)
4. Save ZIP to: `C:\Users\donmo\Downloads\`

### 4. Transfer to Pi (Windows/Ubuntu)

```bash
# Open Ubuntu terminal on Windows
cd /mnt/c/Users/donmo/Downloads

# Transfer USGS files
scp -i ~/.ssh/d3kos_key Individual_*.zip d3kos@192.168.1.237:/opt/d3kos/datasets/fish-great-lakes/usgs/

# Transfer Mendeley file
scp -i ~/.ssh/d3kos_key bgsx9fjw4d.zip d3kos@192.168.1.237:/opt/d3kos/datasets/fish-great-lakes/mendeley/
```

### 5. Run Organization Script

```bash
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237
cd ~/Helm-OS
python3 download_fish_datasets.py
```

**This will:**
- Extract all ZIP files
- Organize images by species
- Create train/val/test splits (80/10/10)
- Generate species_list.json
- Create dataset_info.json

### 6. Verify Dataset

```bash
# Check organized dataset
ls -la /opt/d3kos/datasets/fish-great-lakes/train/

# Count species
ls /opt/d3kos/datasets/fish-great-lakes/train/ | wc -l

# Count total images
find /opt/d3kos/datasets/fish-great-lakes/train/ -name "*.jpg" -o -name "*.png" | wc -l
```

**Expected Output:**
- 10+ species folders
- 5,000-8,000+ total images
- train/ (80%), val/ (10%), test/ (10%) directories

### 7. Create Archive for Windows Workstation

```bash
# On Pi, create tar.gz archive
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237
cd /opt/d3kos/datasets
tar -czf /tmp/fish-great-lakes-dataset.tar.gz fish-great-lakes/

# Check archive size
ls -lh /tmp/fish-great-lakes-dataset.tar.gz
```

### 8. Transfer to Windows Workstation

```bash
# On Windows/Ubuntu terminal:
scp -i ~/.ssh/d3kos_key d3kos@192.168.1.237:/tmp/fish-great-lakes-dataset.tar.gz ~/Helm-OS/output/

# Extract on Windows
cd /mnt/c/fish-training/
tar -xzf ~/Helm-OS/output/fish-great-lakes-dataset.tar.gz
```

### 9. Train Model on Windows

```bash
# On Windows workstation:
cd C:\fish-training
python train_fish_model.py

# Wait 12-16 hours for training to complete
```

### 10. Deploy to Pi

```bash
# Copy trained model back to Pi
scp -i ~/.ssh/d3kos_key ~/Helm-OS/output/fish_classifier_10species_best.onnx d3kos@192.168.1.237:/opt/d3kos/models/fish-species/

scp -i ~/.ssh/d3kos_key ~/Helm-OS/output/species_list.json d3kos@192.168.1.237:/opt/d3kos/models/fish-species/

# Restart fish detector service
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237
sudo systemctl restart d3kos-fish-detector
```

---

## Alternative: Direct wget Downloads (if URLs work)

**USGS Dataset (may require session):**
```bash
# Try direct download (might fail due to authentication)
cd /opt/d3kos/datasets/fish-great-lakes/usgs/

# Example for Brook Trout (repeat for each species)
wget "https://www.sciencebase.gov/catalog/file/get/6064bc6dd34eff1443414c28?name=Individual_BrookTrout.zip" -O Individual_BrookTrout.zip

# If this fails, use browser download method above
```

**Mendeley Dataset (requires authentication):**
```bash
# wget will NOT work for Mendeley (requires login session)
# MUST use browser download method
```

---

## Troubleshooting

### Problem: "Permission denied" when creating directories
```bash
sudo chown -R d3kos:d3kos /opt/d3kos/datasets/
```

### Problem: "No space left on device"
```bash
# Check disk space
df -h

# Clean up if needed
sudo apt-get clean
sudo rm -rf /var/log/*.gz
```

### Problem: ZIP extraction fails
```bash
# Install unzip if missing
sudo apt-get install unzip

# Extract with verbose output to see errors
unzip -v Individual_BrookTrout.zip
```

### Problem: SCP transfer fails
```bash
# Test SSH connection first
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237 'echo "Connection OK"'

# Use rsync for large files (resumes if interrupted)
rsync -avz -e "ssh -i ~/.ssh/d3kos_key" ~/Downloads/*.zip d3kos@192.168.1.237:/opt/d3kos/datasets/fish-great-lakes/usgs/
```

---

## Dataset Information

### USGS Dataset Details
- **Source:** U.S. Geological Survey
- **DOI:** 10.5066/P9NMVL2Q
- **Published:** 2021
- **License:** Public Domain (US Government)
- **Format:** JPG images with annotations
- **Quality:** High-resolution photos from field research
- **Citation:** Provided on ScienceBase page

### Mendeley Dataset Details
- **Source:** Mendeley Data
- **DOI:** 10.17632/bgsx9fjw4d.2
- **Published:** 2024
- **License:** CC BY 4.0 (attribution required)
- **Format:** PNG images + CSV metadata
- **Quality:** Controlled conditions, consistent lighting
- **Citation:**
  ```
  Fisheries Dataset: Fish Species Classification and Attribute Analysis
  Mendeley Data, V2
  https://data.mendeley.com/datasets/bgsx9fjw4d/2
  ```

---

## Species Mapping

**After download, these species will be available:**

| Dataset Species | Mapped To | Great Lakes? |
|----------------|-----------|--------------|
| USGS: Lake Trout | lake_trout | ✅ Yes |
| USGS: Largemouth Bass | largemouth_bass | ✅ Yes |
| USGS: Smallmouth Bass | smallmouth_bass | ✅ Yes |
| USGS: Brook Trout | brook_trout | ✅ Yes |
| USGS: Rainbow Trout | rainbow_trout | ✅ Yes |
| USGS: Walleye | walleye | ✅ Yes |
| USGS: Northern Pike | northern_pike | ✅ Yes |
| Mendeley: Perch | yellow_perch | ✅ Yes (close match) |
| Mendeley: Pike | northern_pike | ✅ Yes (duplicate) |
| Mendeley: Whitefish | lake_whitefish | ✅ Yes |
| Mendeley: Bream | bream | ❌ European |
| Mendeley: Parkki | parkki | ❌ European |
| Mendeley: Roach | roach | ❌ European |
| Mendeley: Smelt | smelt | ⚠️ Partial (Rainbow Smelt) |

**Great Lakes Species Count:** 10 unique species
**Total Images:** 7,000-8,000+ images
**Coverage of Top 10:** 8/10 species (80%)

---

## Next Steps After Download

1. ✅ **Verify dataset** - Check species folders and image counts
2. ✅ **Review images** - Ensure quality is good for training
3. ✅ **Transfer to workstation** - Prepare for GPU training
4. ⏳ **Train model** - 12-16 hours on RTX 3060 Ti
5. ⏳ **Deploy to Pi** - Replace tropical model with freshwater
6. ⏳ **Test** - Verify species identification works on Lake Simcoe fish

---

**Estimated Timeline:**
- Download: 30-60 minutes (manual browser downloads)
- Transfer to Pi: 10-15 minutes
- Organization: 5-10 minutes (script runs automatically)
- Archive creation: 5-10 minutes
- Transfer to workstation: 15-30 minutes
- **Total: 1-2 hours to dataset ready for training**

---

**Ready to start?** Follow Step 1-10 above in order!
