# Forward Watch Model Training - Windows Workstation

**Your Task:** Train YOLOv8 marine obstacle detection model
**Hardware:** RTX 3060 Ti (8GB VRAM)
**Time:** 20-30 hours
**Dataset:** Ready on Pi (54,789 images, 3.7 GB)

---

## Step 1: Transfer Dataset (15 min)

### On Pi (via PuTTY - ssh d3kos@192.168.1.237):
```bash
cd ~
python3 -m http.server 8888
```

### On Workstation (Windows browser):
1. Download: `http://192.168.1.237:8888/forward-watch-complete.tar.gz`
2. Save to: `C:\fish-training\`
3. Extract twice (tar.gz → tar → folders)
4. Result: `C:\fish-training\forward-watch-dataset\`

---

## Step 2: Setup Environment (10 min)

### Open Command Prompt (Administrator):
```cmd
cd C:\fish-training

REM Check PyTorch installed
python --version
pip list | findstr torch

REM If PyTorch missing, install:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

REM Install YOLOv8
pip install ultralytics
```

---

## Step 3: Create Training Script (5 min)

Create: `C:\fish-training\train_forward_watch.py`

```python
from ultralytics import YOLO
import torch

# Verify GPU
print(f"CUDA Available: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0)}")

# Load YOLOv8m (medium - best for 8GB VRAM)
model = YOLO('yolov8m.pt')

# Train
results = model.train(
    data='forward-watch-dataset/data.yaml',
    epochs=100,
    batch=16,
    imgsz=640,
    device=0,
    project='forward-watch-runs',
    name='v1',
    patience=10
)

print("\nTraining Complete!")
print(f"Best model: forward-watch-runs/v1/weights/best.pt")

# Export to ONNX for Raspberry Pi
print("\nExporting to ONNX...")
best_model = YOLO('forward-watch-runs/v1/weights/best.pt')
best_model.export(format='onnx')
print("ONNX export complete: forward-watch-runs/v1/weights/best.onnx")
```

---

## Step 4: Start Training (20-30 hours)

```cmd
cd C:\fish-training
python train_forward_watch.py
```

### Monitor Progress:
- Watch console output
- GPU usage: Open Task Manager → Performance → GPU
- Should see: ~90-100% GPU utilization
- Training saves checkpoints every epoch

### If Training Stops:
- Check GPU temperature (should be < 85°C)
- Check power settings (disable sleep mode)
- Resume: Script will auto-resume from last checkpoint

---

## Step 5: Check Results (After training completes)

### Training completes when you see:
```
Training Complete!
Best model: forward-watch-runs/v1/weights/best.pt
Exporting to ONNX...
ONNX export complete: forward-watch-runs/v1/weights/best.onnx
```

### Check Accuracy:
Look for `mAP50` in console output:
- **Target:** > 75% (Good)
- **Acceptable:** > 65%
- **Retry if:** < 65% (increase epochs to 150)

---

## Step 6: Transfer to Pi (15 min)

### On Workstation:
1. Copy file: `C:\fish-training\forward-watch-runs\v1\weights\best.onnx`
2. Open WinSCP or FileZilla
3. Connect to Pi: `192.168.1.237` (user: `d3kos`, password: `d3kos2026`)
4. Upload to: `/opt/d3kos/models/forward-watch/best.onnx`

### On Pi (via PuTTY):
```bash
sudo systemctl restart d3kos-fish-detector
```

---

## Step 7: Test on Pi (10 min)

1. Open browser: `http://192.168.1.237/marine-vision.html`
2. Camera should show live feed
3. Click "Run Detection" button
4. Should see bounding boxes around boats/buoys/obstacles
5. Test with 10 different camera angles
6. **Success:** Detections appear correctly
7. **Fail:** Check logs: `journalctl -u d3kos-fish-detector -n 50`

---

## Step 8: Cleanup Workstation (5 min)

```cmd
cd C:\fish-training
uninstall_everything.bat
```

This removes:
- PyTorch
- Ultralytics
- Dataset files
- Training outputs

Frees: ~10 GB disk space

---

## Troubleshooting

**GPU not detected:**
- Reinstall CUDA toolkit
- Check NVIDIA drivers updated

**Out of memory:**
- Reduce batch size: `batch=8` instead of 16
- Use smaller model: `yolov8s.pt` instead of yolov8m.pt

**Low accuracy (<65%):**
- Increase epochs: `epochs=150`
- Check dataset quality (images not corrupt)

**Training too slow:**
- Verify GPU usage (Task Manager)
- Close other GPU applications
- Check background processes

---

**Total Time:** ~21-31 hours
**Hands-on Time:** ~1 hour
**Automated Time:** 20-30 hours (leave running overnight)
