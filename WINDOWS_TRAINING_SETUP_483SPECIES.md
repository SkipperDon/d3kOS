# Fish Species Training Setup - Windows Workstation
## 483 Species from Existing Dataset

**You already have the dataset!** No downloading needed - we'll use your existing fish-species-image-data.

---

## Prerequisites Check

### 1. GPU Ready?
Your RTX 3060 Ti is perfect for this:
- ✅ 8GB VRAM
- ✅ CUDA support
- ✅ Fast training (~12-16 hours for 483 species)

### 2. Dataset Check
**Location:** `C:\fish-training\fish-species-image-data-fish_data\images\`

**Structure:**
```
images\
  ├── cropped\    (fish images, cropped)
  ├── numbered\   (fish images, numbered)
  └── raw_image\  (fish images, raw/original)
```

You confirmed you have these 3 directories ✅

---

## Setup Steps

### Step 1: Copy Files to Windows Workstation

Copy these files from Ubuntu to your Windows workstation:

1. **Training script:**
   - Source: `/home/boatiq/Helm-OS/train_fish_model_483species.py`
   - Destination: `C:\fish-training\train_fish_model.py`

2. **Index file:**
   - Source: `/home/boatiq/final_all_index.txt`
   - Destination: `C:\fish-training\final_all_index.txt`

**How to copy:**
```bash
# From Ubuntu terminal:
cp /home/boatiq/Helm-OS/train_fish_model_483species.py /mnt/c/Users/donmo/Desktop/
cp /home/boatiq/final_all_index.txt /mnt/c/Users/donmo/Desktop/
```

Then from Windows:
- Move both files from Desktop to `C:\fish-training\`

---

### Step 2: Install Python Packages (If Not Already Installed)

Open **PowerShell as Administrator** on your Windows workstation:

```powershell
# Navigate to training directory
cd C:\fish-training

# Install required packages (if not already installed)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install pillow numpy scikit-learn tqdm
```

*Note: If you already have PyTorch with CUDA installed from the previous session, skip this step.*

---

### Step 3: Verify Dataset Structure

In PowerShell:

```powershell
# Check if dataset exists
Test-Path "C:\fish-training\fish-species-image-data-fish_data\images"

# Check subdirectories
Get-ChildItem "C:\fish-training\fish-species-image-data-fish_data\images"

# Count images in each subdirectory (optional)
(Get-ChildItem "C:\fish-training\fish-species-image-data-fish_data\images\cropped" -File).Count
(Get-ChildItem "C:\fish-training\fish-species-image-data-fish_data\images\numbered" -File).Count
(Get-ChildItem "C:\fish-training\fish-species-image-data-fish_data\images\raw_image" -File).Count
```

**Expected:**
- Total images: ~4,411 across all 3 subdirectories
- Species: 483

---

### Step 4: Start Training!

```powershell
cd C:\fish-training
python train_fish_model.py
```

---

## What Happens During Training

### Phase 1: Data Loading (1-2 minutes)
```
Parsing index file: C:\fish-training\final_all_index.txt
✓ Parsed 4411 image entries
✓ Found 483 unique species
✓ Average images per species: 9.1

Searching for images in: C:\fish-training\fish-species-image-data-fish_data\images
Finding images: 100%|████████████| 4411/4411 [00:45<00:00]
✓ Found 4200 images
⚠ Missing 211 images from index

Creating data loaders...
✓ Training set: 3360 images
✓ Validation set: 840 images
```

*Note: Some missing images are normal - index might reference images not in your dataset.*

### Phase 2: Model Setup (10 seconds)
```
Creating EfficientNet-B0 model for 483 classes...
Using device: cuda
GPU: NVIDIA GeForce RTX 3060 Ti
VRAM: 8.00 GB
✓ Model loaded on cuda
```

### Phase 3: Training (12-16 hours)
```
Epoch 1/50:  loss: 4.2345, acc: 12.34%
Epoch 2/50:  loss: 3.8901, acc: 18.56%
...
Epoch 50/50: loss: 0.4521, acc: 89.23%
  ★ New best model saved! (Val Acc: 92.15%)
```

### Phase 4: Saving (30 seconds)
```
✓ Model saved: C:\fish-training\output\fish_classifier_483species_best.pth
✓ Species mapping saved: C:\fish-training\output\fish_classifier_483species_best_species.json
Exporting to ONNX format for Raspberry Pi...
✓ ONNX model saved: C:\fish-training\output\fish_classifier_483species_best.onnx
  File size: 16.42 MB
```

---

## Output Files

After training completes, you'll have in `C:\fish-training\output\`:

1. **fish_classifier_483species_best.pth** (16-17 MB)
   - PyTorch model weights (best validation accuracy)

2. **fish_classifier_483species_best.onnx** (16-17 MB)
   - **THIS IS THE FILE FOR RASPBERRY PI** ⭐

3. **fish_classifier_483species_best_species.json** (15 KB)
   - Species name to ID mapping (483 species)

4. **fish_classifier_483species_final.pth** (16-17 MB)
   - Final model after 50 epochs

5. **training_history.json** (5 KB)
   - Loss and accuracy for each epoch

---

## Transfer to Raspberry Pi

### Option 1: SCP (Secure Copy)

From Windows PowerShell:

```powershell
# Navigate to output directory
cd C:\fish-training\output

# Copy ONNX model to Pi
scp -i C:\Users\donmo\.ssh\d3kos_key fish_classifier_483species_best.onnx d3kos@192.168.1.237:/opt/d3kos/models/marine-vision/

# Copy species mapping
scp -i C:\Users\donmo\.ssh\d3kos_key fish_classifier_483species_best_species.json d3kos@192.168.1.237:/opt/d3kos/models/marine-vision/
```

### Option 2: USB Drive

1. Copy `fish_classifier_483species_best.onnx` to USB drive
2. Plug USB into Raspberry Pi
3. Copy to `/opt/d3kos/models/marine-vision/`

---

## Cleanup After Training (If Needed)

Remember: Your wife wanted ML software uninstalled after training.

Run the cleanup batch file:

```powershell
cd C:\fish-training
.\uninstall_everything.bat
```

This will remove:
- PyTorch
- torchvision
- torchaudio
- NumPy, Pillow, scikit-learn
- CUDA toolkit (optional)

**Keep these files:**
- `C:\fish-training\output\` folder (your trained model!)
- Transfer the .onnx file to Pi BEFORE uninstalling

---

## Training Time Estimates

Based on RTX 3060 Ti (8GB VRAM):

| Configuration | Time per Epoch | Total (50 epochs) |
|---------------|----------------|-------------------|
| 483 species, 4200 images | 15-20 minutes | **12-16 hours** |

**Overnight training recommended!**

Start training before bed, check in the morning.

---

## Expected Results

**Good model accuracy for 483 species:**
- Training accuracy: 85-95%
- Validation accuracy: 80-90%
- Top-5 accuracy: 95%+

**Much better than COCO proxy!** Real fish detection on the boat.

---

## Troubleshooting

### Error: "Index file not found"
```
ERROR: Index file not found: C:\fish-training\final_all_index.txt
```
**Fix:** Copy `final_all_index.txt` from Desktop to `C:\fish-training\`

### Error: "Dataset directory not found"
```
ERROR: Dataset directory not found: C:\fish-training\fish-species-image-data-fish_data\images
```
**Fix:** Verify path is exactly: `C:\fish-training\fish-species-image-data-fish_data\images`

### Error: "CUDA out of memory"
```
RuntimeError: CUDA out of memory
```
**Fix:** Open `train_fish_model.py`, change line 22:
```python
BATCH_SIZE = 16  # Reduce from 32 to 16
```

### Error: "No images found"
```
✓ Found 0 images
ERROR: No images found!
```
**Fix:** Check if images have file extensions (.jpg, .png). Run this in PowerShell:
```powershell
Get-ChildItem "C:\fish-training\fish-species-image-data-fish_data\images\*" -Recurse -File | Select-Object -First 10
```

---

## Questions?

Check the training logs in PowerShell for detailed progress.

Press `Ctrl+C` to stop training early (model will save progress).

---

**Ready to train? Follow Step 1 to copy the files, then Step 4 to start training!**
