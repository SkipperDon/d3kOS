# Tomorrow's Quick Start - Forward Watch Training

**Date:** March 2, 2026
**Time Required:** 30 minutes setup + 20-30 hours training
**Workstation:** RTX 3060 Ti, 32GB RAM

---

## 🎯 GOAL
Train YOLOv8 obstacle detection model for Forward Watch collision avoidance

---

## ✅ 30-Minute Setup Checklist

### 1. Install Python (5 min)
```powershell
python --version  # Should be 3.10 or 3.11
```
If not: https://www.python.org/downloads/

### 2. Install PyTorch with CUDA (10 min)
```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```

### 3. Install YOLOv8 (2 min)
```powershell
pip install ultralytics
```

### 4. Transfer Dataset (15 min)
**On Pi (when online):**
```bash
cd /home/d3kos
python3 -m http.server 8888
```

**On Workstation:**
- Browser: `http://192.168.1.237:8888/`
- Download: `forward-watch-complete.tar.gz` (3.7 GB)
- Save to: `C:\forward-watch-complete.tar.gz`

### 5. Extract Dataset (10 min)
```powershell
mkdir C:\forward-watch-dataset
cd C:\forward-watch-dataset
python -c "import tarfile; tarfile.open('C:/forward-watch-complete.tar.gz').extractall('.')"
```

**Verify:**
```powershell
dir images\train  # Should have ~38,000 images
dir images\val    # Should have ~11,000 images
dir images\test   # Should have ~5,700 images
```

### 6. Copy Training Script
```powershell
copy Helm-OS\doc\forward-watch\train_forward_watch.py C:\forward-watch-dataset\
```

### 7. Start Training
```powershell
cd C:\forward-watch-dataset
python train_forward_watch.py
```

**Expected:** Script runs for 20-30 hours

---

## 📊 What to Watch During Training

**Good signs:**
- GPU usage: 90-100% (`nvidia-smi`)
- Losses decreasing each epoch
- mAP increasing
- No "out of memory" errors

**Red flags:**
- GPU usage < 50% (something wrong)
- Losses not decreasing after 20 epochs
- Out of memory errors

---

## 🎯 Success Criteria

**At end of training, should see:**
```
mAP@0.5: 0.78 (Target: >0.75) ✅
Precision: 0.75
Recall: 0.72
```

**ONNX model auto-exported to:**
```
runs\detect\forward-watch\weights\best.onnx
```

---

## 🚢 After Training (15 min)

**Transfer to Pi:**
```bash
# On Pi
cd /opt/d3kos/models/forward-watch
wget http://YOUR_WORKSTATION_IP:8888/best.onnx -O forward_watch.onnx
sudo systemctl restart d3kos-forward-watch
```

---

## 🆘 If Problems

**CUDA not available:**
```powershell
# Install NVIDIA drivers + CUDA Toolkit 12.1
# Then reinstall PyTorch
```

**Out of memory:**
Edit `train_forward_watch.py` line 24:
```python
BATCH_SIZE = 8  # Was 16
```

**Need help:**
- Enable SSH on Windows (see full guide)
- Claude can assist remotely

---

## 📝 Command Summary

```powershell
# Full setup and training in one go:
python --version
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install ultralytics
mkdir C:\forward-watch-dataset
cd C:\forward-watch-dataset
# Download and extract dataset here
copy ..\Helm-OS\doc\forward-watch\train_forward_watch.py .
python train_forward_watch.py
```

**That's it! Let it run for 20-30 hours.**

---

**Full Documentation:**
- Setup Guide: `Helm-OS/doc/forward-watch/TRAINING_WORKSTATION_SETUP.md`
- Training Script: `Helm-OS/doc/forward-watch/train_forward_watch.py`
- Specifications: `Helm-OS/doc/forward-watch/FORWARD_WATCH_SPECIFICATION.md`
