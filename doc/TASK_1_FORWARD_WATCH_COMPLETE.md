# Task 1: Forward Watch AI Model - COMPLETE Implementation

**Executor:** Ollama (supervised by Claude Code)
**Timeline:** 20-30 hours training + 2 hours deployment
**Status:** Ready to execute

## Objective
Train YOLOv8 marine obstacle detection model on Windows workstation, deploy to Pi, verify working.

## Steps

### 1. Workstation Setup (30 min)
- Location: `C:\fish-training\`
- Check PyTorch installed: `pip list | findstr torch`
- Install Ultralytics: `pip install ultralytics`
- Transfer dataset from Pi: `forward-watch-complete.tar.gz` (3.7 GB, 54,789 images)

### 2. Training (20-30 hours)
```python
# C:\fish-training\train_forward_watch.py
from ultralytics import YOLO

model = YOLO('yolov8m.pt')
results = model.train(
    data='forward-watch-dataset/data.yaml',
    epochs=100,
    batch=16,
    imgsz=640,
    device=0,
    project='forward-watch-runs',
    name='v1'
)

# Export to ONNX for Pi
model.export(format='onnx')
```

### 3. Verify Results
- Target: mAP@0.5 > 75%
- Classes: boats, kayaks, buoys, logs, debris, docks, ice
- If < 75%: Increase epochs to 150, retry

### 4. Deploy to Pi
```bash
scp best.onnx d3kos@192.168.1.237:/opt/d3kos/models/forward-watch/
ssh d3kos@192.168.1.237 'sudo systemctl restart d3kos-fish-detector'
```

### 5. Test & Verify
- Open: http://192.168.1.237/marine-vision.html
- Click "Run Detection"
- Verify detections appear (boats, buoys, etc.)
- Test 10 different images
- All pass: COMPLETE

### 6. Git Commit
```bash
cd /home/boatiq/Helm-OS
git add doc/forward-watch/
git commit -m "feat: Forward Watch AI model trained and deployed

- Trained YOLOv8m on 54,789 marine images
- Achieved XX.X% mAP@0.5 accuracy
- Deployed to Pi at /opt/d3kos/models/forward-watch/
- Verified obstacle detection working
- Classes: boats, kayaks, buoys, logs, debris, docks, ice"
```

## Acceptance Criteria
- ✅ Model trained (mAP > 75%)
- ✅ ONNX model on Pi
- ✅ Detections working in UI
- ✅ Git committed
- ✅ Nothing hanging

## Cleanup
```bash
# On workstation after verification
C:\fish-training\uninstall_everything.bat
```
