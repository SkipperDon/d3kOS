# Forward Watch Training - Windows Workstation Setup

**Date:** February 27, 2026
**GPU:** NVIDIA RTX 3060 Ti (8GB VRAM)
**Status:** Ready for training

---

## Prerequisites Checklist

Before running training, verify:

### 1. ✅ GPU Setup
- [ ] NVIDIA RTX 3060 Ti installed
- [ ] CUDA 12.1 or later installed
- [ ] nvidia-smi command works
- [ ] GPU shows in Task Manager → Performance

### 2. ✅ Python Environment
- [ ] Python 3.10 or 3.11 installed
- [ ] PyTorch with CUDA support installed
- [ ] Ultralytics package installed

### 3. ✅ Dataset Downloaded
- [ ] Dataset at: `C:\Users\donmo\Downloads\forward-watch-complete\`
- [ ] data.yaml exists in dataset folder
- [ ] Training images exist

---

## Installation Steps (Windows)

### Step 1: Verify Python
```cmd
python --version
```
Should show: Python 3.10.x or 3.11.x

### Step 2: Install PyTorch with CUDA
```cmd
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Step 3: Install Ultralytics
```cmd
pip install ultralytics
```

### Step 4: Verify GPU Detection
```cmd
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')"
```

Should show:
```
CUDA available: True
GPU: NVIDIA GeForce RTX 3060 Ti
```

---

## Dataset Verification

### Check Data YAML Exists:
```cmd
dir "C:\Users\donmo\Downloads\forward-watch-complete\data.yaml"
```

### Expected data.yaml Content:
```yaml
path: C:\Users\donmo\Downloads\forward-watch-complete
train: images/train
val: images/val

names:
  0: ship
  1: boat
  2: debris
  3: buoy
  4: kayak
  5: log
```

If data.yaml is missing or incorrect, training will fail immediately.

---

## Running Training

### Method 1: Use START_CORRECT.bat
```cmd
cd C:\Users\donmo\Downloads\forward-watch-complete
START_CORRECT.bat
```

### Method 2: Run Python Script Directly
```cmd
cd C:\Users\donmo\Downloads\forward-watch-complete
python train_forward_watch_CORRECT.py
```

---

## Expected Training Output

### Initial Messages:
```
================================================
🚢 YOLOV8 FORWARD WATCH TRAINING
================================================
Dataset: C:\Users\donmo\Downloads\forward-watch-complete\data.yaml
✓ Data file found
Epochs: 100
Batch Size: 16
Image Size: 640
Output Directory: C:\Users\donmo\Downloads\forward-watch-complete\output
GPU: RTX 3060 Ti (device 0)
================================================

Loading YOLOv8 nano model...
Starting training...
Expected duration: 12-24 hours
```

### During Training:
```
Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
  1/100      1.2G      1.234      2.456      0.789         42        640: 100%|████████| 123/123
```

---

## Common Errors and Solutions

### Error: "ModuleNotFoundError: No module named 'ultralytics'"
**Cause:** Ultralytics not installed
**Fix:**
```cmd
pip install ultralytics
```

### Error: "CUDA not available" or "GPU not detected"
**Cause:** PyTorch installed without CUDA support
**Fix:** Reinstall PyTorch with CUDA:
```cmd
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Error: "data.yaml not found!"
**Cause:** Dataset path is incorrect or data.yaml missing
**Fix:** Verify file exists:
```cmd
dir "C:\Users\donmo\Downloads\forward-watch-complete\data.yaml"
```

If missing, check if dataset was downloaded to different location.

### Error: "RuntimeError: CUDA out of memory"
**Cause:** Batch size too large for 8GB GPU
**Fix:** Edit train_forward_watch_CORRECT.py:
```python
BATCH_SIZE = 8  # Reduce from 16 to 8
```

### Training Hangs or Freezes
**Cause:** GPU driver issue or insufficient RAM
**Fix:**
1. Update NVIDIA drivers
2. Close other GPU applications
3. Restart computer and try again

---

## Training Progress Monitoring

### Check Output Files:
```cmd
dir "C:\Users\donmo\Downloads\forward-watch-complete\output\forward-watch\weights"
```

Should contain:
- `best.pt` - Best model weights
- `last.pt` - Latest epoch weights

### View Training Plots:
Open in browser:
```
C:\Users\donmo\Downloads\forward-watch-complete\output\forward-watch\results.png
C:\Users\donmo\Downloads\forward-watch-complete\output\forward-watch\confusion_matrix.png
```

### Check GPU Usage:
Open Task Manager → Performance → GPU
Should show: ~95-100% GPU utilization during training

---

## After Training Completes

### Expected Output:
```
================================================
✅ TRAINING COMPLETE!
================================================
Best model: C:\Users\donmo\Downloads\forward-watch-complete\output\forward-watch\weights\best.pt

Next: Convert to ONNX for Raspberry Pi deployment
================================================
Press Enter to exit...
```

### Next Steps:
1. Convert model to ONNX format (for Pi deployment)
2. Transfer to Raspberry Pi
3. Integrate with d3kOS Forward Watch system

---

## Troubleshooting

### Issue: Training runs but accuracy is low (< 50%)
**Possible Causes:**
- Insufficient training data
- Dataset mislabeled
- Model too small (yolov8n)

**Solutions:**
- Use yolov8s or yolov8m instead of nano
- Increase training epochs
- Check data.yaml labels match image annotations

### Issue: Training takes longer than 24 hours
**Causes:**
- GPU not being used (running on CPU)
- Batch size too small

**Verify GPU Usage:**
```cmd
nvidia-smi
```
Should show Python process using GPU memory

---

## Training Time Estimates

| Model | GPU | Dataset Size | Epochs | Expected Time |
|-------|-----|--------------|--------|---------------|
| YOLOv8n | RTX 3060 Ti | 54,789 images | 100 | 12-16 hours |
| YOLOv8s | RTX 3060 Ti | 54,789 images | 100 | 18-24 hours |
| YOLOv8m | RTX 3060 Ti | 54,789 images | 100 | 30-36 hours |

**Note:** Times assume 16 batch size. Reducing to 8 will double training time.

---

## Summary

✅ Training script is ready
✅ GPU setup documented
✅ Common errors documented
✅ START_CORRECT.bat ready to use

**To Begin Training:**
1. Verify all prerequisites checked
2. Double-click `START_CORRECT.bat`
3. Wait 12-24 hours
4. Model will be saved to output/forward-watch/weights/best.pt

---

**Questions? Check:**
- FORWARD_WATCH_SPECIFICATION.md - System design
- Dataset documentation in dataset folder
- Ultralytics documentation: https://docs.ultralytics.com/
