# Fish Species Model Training - Windows Workstation

**Your Task:** Train fish species classifier for Great Lakes
**Hardware:** RTX 3060 Ti (8GB VRAM)
**Time:** 12-16 hours
**Dataset:** Need to download (Great Lakes species)

---

## Step 1: Setup Environment (10 min)

### Open Command Prompt (Administrator):
```cmd
cd C:\fish-training

REM Check PyTorch installed
python --version
pip list | findstr torch

REM If missing, install:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

REM Install requirements
pip install ultralytics pillow
```

---

## Step 2: Download Great Lakes Dataset (2 hours)

### Option A: Use existing dataset on Pi
```bash
# On Pi (via PuTTY):
cd /opt/d3kos/datasets
tar -czf great-lakes-fish.tar.gz fish-worldwide/

# Start HTTP server:
python3 -m http.server 8888
```

Then download from workstation browser:
`http://192.168.1.237:8888/great-lakes-fish.tar.gz`

### Option B: Manual download
1. Visit: https://www.inaturalist.org
2. Search each species (Bass, Pike, Walleye, Perch, etc.)
3. Download 50-100 images per species
4. Organize: `C:\fish-training\fish-dataset\[species-name]\*.jpg`

---

## Step 3: Create Training Script (5 min)

Create: `C:\fish-training\train_fish_species.py`

```python
from ultralytics import YOLO
import torch

# Verify GPU
print(f"CUDA Available: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0)}")

# Load YOLOv8 for classification
model = YOLO('yolov8m-cls.pt')  # Classification model

# Train on Great Lakes fish species
results = model.train(
    data='fish-dataset',  # Folder with subfolders per species
    epochs=50,
    batch=32,
    imgsz=224,
    device=0,
    project='fish-species-runs',
    name='great-lakes-v1',
    patience=10
)

print("\nTraining Complete!")
print(f"Best model: fish-species-runs/great-lakes-v1/weights/best.pt")

# Export to ONNX for Raspberry Pi
print("\nExporting to ONNX...")
best_model = YOLO('fish-species-runs/great-lakes-v1/weights/best.pt')
best_model.export(format='onnx')
print("ONNX export complete: fish-species-runs/great-lakes-v1/weights/best.onnx")
```

---

## Step 4: Start Training (12-16 hours)

```cmd
cd C:\fish-training
python train_fish_species.py
```

### Monitor Progress:
- Watch console output
- GPU usage: Task Manager → Performance → GPU
- Should see: ~90-100% GPU utilization

### Target Species (Great Lakes):
- Largemouth Bass
- Smallmouth Bass
- Northern Pike
- Walleye
- Yellow Perch
- Lake Trout
- Muskellunge
- Bluegill
- Black Crappie
- White Bass

---

## Step 5: Check Results (After training completes)

### Look for accuracy in console:
- **Target:** > 85% (Excellent)
- **Acceptable:** > 75%
- **Retry if:** < 75% (increase epochs to 75)

---

## Step 6: Transfer to Pi (15 min)

### Using WinSCP/FileZilla:
1. Copy: `C:\fish-training\fish-species-runs\great-lakes-v1\weights\best.onnx`
2. Connect: `192.168.1.237` (user: `d3kos`, password: `d3kos2026`)
3. Upload to: `/opt/d3kos/models/fish-species/fish_classifier_greatlakes.onnx`

### On Pi (via PuTTY):
```bash
# Update fish detector to use new model
sudo systemctl restart d3kos-fish-detector
```

---

## Step 7: Test on Pi (10 min)

1. Open: `http://192.168.1.237/marine-vision.html`
2. Point camera at fish (or fish photo on phone)
3. Click "Run Detection"
4. Should identify species: "Largemouth Bass (92% confidence)"
5. Test with 5 different species
6. **Success:** Correct species identified
7. **Fail:** Check logs: `journalctl -u d3kos-fish-detector -n 50`

---

## Step 8: Cleanup Workstation (5 min)

```cmd
cd C:\fish-training
uninstall_everything.bat
```

Frees: ~8 GB disk space

---

## Troubleshooting

**Low accuracy:**
- Need more images (100+ per species minimum)
- Check image quality (clear, well-lit fish photos)
- Increase epochs to 75-100

**GPU memory error:**
- Reduce batch size: `batch=16` instead of 32
- Reduce image size: `imgsz=128` instead of 224

**Wrong species detected:**
- Dataset imbalance (some species have more images)
- Add more images for underrepresented species
- Check for mislabeled images

---

**Total Time:** ~14-18 hours
**Hands-on Time:** ~45 minutes
**Automated Time:** 12-16 hours (leave running overnight)

---

## After Both Models Trained

You'll have:
1. Forward Watch: Detects obstacles (boats, buoys, logs, debris)
2. Fish Species: Identifies fish species when caught

Both models work together:
- Forward Watch: Monitors water ahead while cruising
- Fish Species: Identifies catch when person+fish detected
