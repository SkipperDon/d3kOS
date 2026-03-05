# Forward Watch Training - Windows Workstation Setup Guide

**Date:** March 1, 2026
**Session:** Tomorrow's Priority (March 2, 2026)
**Workstation:** RTX 3060 Ti (8GB VRAM), 32GB RAM
**Task:** Train YOLOv8 obstacle detection model for Forward Watch

---

## 📋 Quick Start Checklist

Tomorrow's session (30-minute setup):

- [ ] **Step 1:** Install Python 3.10 or 3.11 (if not installed)
- [ ] **Step 2:** Install PyTorch with CUDA support
- [ ] **Step 3:** Install Ultralytics YOLOv8
- [ ] **Step 4:** Transfer dataset from Pi to workstation
- [ ] **Step 5:** Extract dataset and verify structure
- [ ] **Step 6:** Run training script
- [ ] **Step 7:** Monitor training progress (20-30 hours)
- [ ] **Step 8:** Export to ONNX and deploy to Pi

---

## 🖥️ Step 1: Install Python (5 minutes)

**Check if Python is installed:**
```powershell
python --version
```

**If not installed or < 3.10:**
1. Download Python 3.11: https://www.python.org/downloads/
2. Run installer with these options:
   - ✅ Add Python to PATH
   - ✅ Install pip
   - ✅ Install for all users

**Verify:**
```powershell
python --version  # Should show Python 3.11.x
pip --version     # Should show pip 23.x or higher
```

---

## 🔥 Step 2: Install PyTorch with CUDA (10 minutes)

**For RTX 3060 Ti with CUDA 12.1:**
```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**Verify GPU is detected:**
```powershell
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0)}'); print(f'CUDA Version: {torch.version.cuda}')"
```

**Expected output:**
```
CUDA Available: True
GPU: NVIDIA GeForce RTX 3060 Ti
CUDA Version: 12.1
```

**If CUDA not available:**
- Install NVIDIA drivers: https://www.nvidia.com/Download/index.aspx
- Install CUDA Toolkit 12.1: https://developer.nvidia.com/cuda-downloads
- Reboot and try again

---

## 🤖 Step 3: Install Ultralytics YOLOv8 (2 minutes)

```powershell
pip install ultralytics
```

**Verify:**
```powershell
yolo version
```

**Expected output:**
```
Ultralytics YOLOv8.x.x
```

---

## 📦 Step 4: Transfer Dataset from Pi (15 minutes)

**On Raspberry Pi (via SSH or when Pi is online):**
```bash
# Start HTTP server
cd /home/d3kos
python3 -m http.server 8888
```

**On Windows Workstation:**
1. Open browser: `http://192.168.1.237:8888/`
2. Download: `forward-watch-complete.tar.gz` (3.7 GB)
3. Save to: `C:\forward-watch-complete.tar.gz`

**Or use SCP (if SSH enabled on Pi):**
```powershell
scp -i C:\Users\YourUser\.ssh\d3kos_key d3kos@192.168.1.237:/home/d3kos/forward-watch-complete.tar.gz C:\
```

---

## 📂 Step 5: Extract Dataset (10 minutes)

**Extract twice (tar.gz → tar → files):**
```powershell
# Create working directory
mkdir C:\forward-watch-dataset
cd C:\forward-watch-dataset

# Extract (using 7-Zip or Windows built-in)
# If using 7-Zip:
"C:\Program Files\7-Zip\7z.exe" x C:\forward-watch-complete.tar.gz
"C:\Program Files\7-Zip\7z.exe" x forward-watch-complete.tar

# Or use Python
python -c "import tarfile; tarfile.open('C:/forward-watch-complete.tar.gz').extractall('C:/forward-watch-dataset')"
```

**Verify structure:**
```powershell
dir C:\forward-watch-dataset\images
dir C:\forward-watch-dataset\labels
```

**Expected structure:**
```
C:\forward-watch-dataset\
├── images\
│   ├── train\      (~38,000 images)
│   ├── val\        (~11,000 images)
│   └── test\       (~5,700 images)
└── labels\
    ├── train\      (~38,000 .txt files)
    ├── val\        (~11,000 .txt files)
    └── test\       (~5,700 .txt files)
```

**Count files:**
```powershell
(Get-ChildItem -Path "C:\forward-watch-dataset\images\train" -File).Count
(Get-ChildItem -Path "C:\forward-watch-dataset\images\val" -File).Count
(Get-ChildItem -Path "C:\forward-watch-dataset\images\test" -File).Count
```

**Expected:** ~54,789 total images

---

## 🚀 Step 6: Run Training Script (1 minute to start)

**Copy training script:**
```powershell
# From this repository
copy Helm-OS\doc\forward-watch\train_forward_watch.py C:\forward-watch-dataset\
```

**Or download directly from GitHub when pushed**

**Edit script if dataset path is different:**
```python
# Line 19 in train_forward_watch.py
DATASET_PATH = Path("C:/forward-watch-dataset")  # Adjust if needed
```

**Start training:**
```powershell
cd C:\forward-watch-dataset
python train_forward_watch.py
```

**Script will:**
1. ✅ Verify CUDA and GPU
2. ✅ Count images in dataset
3. ✅ Create YAML configuration
4. ✅ Estimate training time (~20-30 hours)
5. ✅ Ask for confirmation
6. ✅ Start training

---

## 📊 Step 7: Monitor Training Progress (20-30 hours)

**Training will output:**
```
Epoch    GPU_mem    box_loss    cls_loss    dfl_loss    Instances    Size
  1/150      2.45G     1.2345      1.5678      1.0123         150      640
  2/150      2.47G     1.1234      1.4567      0.9876         152      640
...
```

**Key metrics to watch:**
- **box_loss:** Should decrease (object localization accuracy)
- **cls_loss:** Should decrease (classification accuracy)
- **mAP@0.5:** Target >= 0.75 (75% accuracy)
- **GPU_mem:** Should stay < 8 GB

**Checkpoints saved every 10 epochs:**
- `runs/detect/forward-watch/weights/epoch10.pt`
- `runs/detect/forward-watch/weights/epoch20.pt`
- etc.

**Best model saved automatically:**
- `runs/detect/forward-watch/weights/best.pt` (highest mAP)
- `runs/detect/forward-watch/weights/last.pt` (last epoch)

**Training plots:**
- `runs/detect/forward-watch/results.png` (loss curves, mAP curves)
- `runs/detect/forward-watch/confusion_matrix.png` (classification accuracy)

**If training crashes:**
```powershell
# Resume from last checkpoint
python train_forward_watch.py --resume runs/detect/forward-watch/weights/last.pt
```

---

## 📈 Step 8: Export to ONNX (Automatic)

**After training completes, script automatically:**
1. ✅ Evaluates model on test set
2. ✅ Prints final metrics (mAP, precision, recall)
3. ✅ Exports to ONNX format for Raspberry Pi
4. ✅ Optimizes and simplifies ONNX model

**ONNX model location:**
```
runs/detect/forward-watch/weights/best.onnx
```

---

## 🚢 Step 9: Deploy to Raspberry Pi (Manual)

**When training is complete, transfer ONNX model to Pi:**

**Option A: HTTP Server (Simple)**
```powershell
# On Windows workstation
cd runs\detect\forward-watch\weights
python -m http.server 8888
```

**On Pi:**
```bash
cd /opt/d3kos/models/forward-watch
wget http://YOUR_WORKSTATION_IP:8888/best.onnx -O forward_watch.onnx
```

**Option B: SCP (If SSH enabled)**
```powershell
scp -i C:\Users\YourUser\.ssh\d3kos_key runs\detect\forward-watch\weights\best.onnx d3kos@192.168.1.237:/opt/d3kos/models/forward-watch/forward_watch.onnx
```

**Verify on Pi:**
```bash
ls -lh /opt/d3kos/models/forward-watch/forward_watch.onnx
# Should show ~40-60 MB file
```

**Restart Forward Watch service:**
```bash
sudo systemctl restart d3kos-forward-watch
journalctl -u d3kos-forward-watch -f  # Check logs
```

---

## 🎯 Success Criteria

**Training successful if:**
- ✅ mAP@0.5 >= 0.75 (75% accuracy)
- ✅ mAP@0.5:0.95 >= 0.50 (50% accuracy across all IoU thresholds)
- ✅ Precision >= 0.70 (70% of detections are correct)
- ✅ Recall >= 0.70 (70% of objects are detected)

**Deployment successful if:**
- ✅ ONNX model loads without errors
- ✅ Inference time < 500ms per frame on Pi
- ✅ Detections display on chartplotter via Signal K
- ✅ Forward Watch alerts trigger correctly

---

## 🐛 Troubleshooting

**CUDA not available:**
- Install/update NVIDIA drivers
- Install CUDA Toolkit 12.1
- Reinstall PyTorch with correct CUDA version
- Reboot

**Out of memory during training:**
- Reduce batch size: `BATCH_SIZE = 8` in script
- Use smaller model: `MODEL_SIZE = "yolov8s"` in script
- Close other GPU applications

**Training too slow:**
- Check GPU utilization: `nvidia-smi`
- Should show ~90-100% GPU usage
- If low, check batch size and multi-processing

**mAP < 0.75 after training:**
- Train for more epochs (150 → 200)
- Use larger model (yolov8m → yolov8l)
- Check dataset quality (correct labels?)
- Adjust hyperparameters

**ONNX export fails:**
- Update Ultralytics: `pip install --upgrade ultralytics`
- Try different opset: `opset=11` or `opset=13`
- Check PyTorch version compatibility

---

## 📞 SSH Remote Assistance (Optional)

**If you want Claude to assist remotely:**

**Enable SSH on Windows:**
```powershell
# Run as Administrator
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Start-Service sshd
Set-Service -Name sshd -StartupType 'Automatic'

# Allow through firewall
New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
```

**Get your IP address:**
```powershell
ipconfig | findstr IPv4
```

**Provide to Claude:**
- IP address: `192.168.1.XXX`
- Username: `YourWindowsUsername`
- Password or SSH key

**Benefits:**
- Real-time monitoring and assistance
- Quick fixes if issues arise
- Automated deployment to Pi when complete

---

## 📝 Training Log Example

**Expected output:**
```
================================================================
Forward Watch Obstacle Avoidance Training
d3kOS Marine Vision System
================================================================

Checking prerequisites...
✓ GPU Detected: NVIDIA GeForce RTX 3060 Ti (8.0 GB)
✓ CUDA Version: 12.1
✓ PyTorch Version: 2.2.0
✓ Dataset found: C:\forward-watch-dataset
✓ Training images: 38252
✓ Validation images: 10967
✓ Test images: 5570
✓ Total images: 54789
✓ Configuration created: C:\forward-watch-dataset\forward-watch.yaml

⏱ Estimated training time: 22.3 hours (150 epochs)

Press Enter to start training (or Ctrl+C to cancel)...

================================================================
Starting Forward Watch Training
================================================================
Model: yolov8m
Image Size: 640x640
Batch Size: 16
Epochs: 150
Classes: 8
Dataset: C:\forward-watch-dataset
================================================================

Downloading yolov8m.pt... Done
Starting training...

Epoch    GPU_mem    box_loss    cls_loss    dfl_loss    Instances    Size
  1/150      2.45G     1.2345      1.5678      1.0123         150      640
  2/150      2.47G     1.1234      1.4567      0.9876         152      640
  3/150      2.48G     1.0987      1.3456      0.9543         148      640
...
148/150      2.51G     0.3456      0.4123      0.4567         155      640
149/150      2.51G     0.3412      0.4089      0.4534         153      640
150/150      2.51G     0.3398      0.4056      0.4512         154      640

================================================================
Training Complete!
================================================================
Best model saved to: runs/detect/forward-watch/weights/best.pt
Last model saved to: runs/detect/forward-watch/weights/last.pt

Evaluating on test set...

📊 Test Set Metrics:
   mAP@0.5: 0.7823 (Target: >0.75) ✅
   mAP@0.5:0.95: 0.5234
   Precision: 0.7456
   Recall: 0.7198

⚡ Inference Speed Test (GPU):
   Preprocess: 2.3 ms
   Inference: 8.7 ms
   Postprocess: 3.1 ms
   Total: 14.1 ms/image (70.9 FPS)

✅ SUCCESS: Target mAP@0.5 achieved (0.7823 >= 0.75)
   Model is ready for production deployment!

================================================================
Exporting to ONNX for Raspberry Pi
================================================================
Optimizing model for inference...
Simplifying ONNX graph...
✓ ONNX model saved to: runs/detect/forward-watch/weights/best.onnx
✓ Ready for deployment to Raspberry Pi!

Next steps:
1. Transfer runs/detect/forward-watch/weights/best.onnx to Pi
2. Place in: /opt/d3kos/models/forward-watch/forward_watch.onnx
3. Restart forward-watch service

================================================================
Training pipeline complete!
================================================================
```

---

## 🚀 Ready for Tomorrow!

Everything is prepared. When you start tomorrow's session:

1. Run through Steps 1-5 (setup and dataset transfer)
2. Start training script
3. Monitor for first 10-15 minutes to ensure no errors
4. Let it run for 20-30 hours
5. Deploy ONNX model to Pi when complete

**Estimated total time:**
- Setup: 30-45 minutes
- Training: 20-30 hours (unattended)
- Deployment: 15 minutes

**Questions or issues tomorrow?**
- Claude can assist via SSH remote access
- Or guide step-by-step via text

---

**Document Created:** March 1, 2026
**Training Start:** March 2, 2026
**Expected Completion:** March 3-4, 2026
