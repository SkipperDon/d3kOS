# Forward Watch Dataset Transfer Instructions

**Date:** 2026-02-26
**Source:** Raspberry Pi (`/home/d3kos/kaggle-datasets/`)
**Destination:** Windows Workstation (for Forward Watch YOLOv8-Marine training)

---

## Downloaded Datasets (5 of 6 successful)

| # | Dataset | Size | Status |
|---|---------|------|--------|
| 1 | NASA Marine Debris | 386 KB | ✅ Downloaded |
| 2 | Seaclear Marine Debris Detection | 1.61 GB | ✅ Downloaded |
| 3 | Underwater Garbage/Debris | 231 MB | ✅ Downloaded |
| 4 | YOLOv8 Ship Detection | 1.21 GB | ✅ Downloaded |
| 5 | MARVEL Maritime Vessels | N/A | ❌ Failed (404 error) |
| 6 | Ship Detection (Aerial) | 122 MB | ✅ Downloaded |

**Total Size:** 3.6 GB (uncompressed)

---

## Transfer Method 1: HTTP Download (Recommended)

**On Raspberry Pi (via SSH):**
```bash
# 1. Start simple HTTP server on Pi
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237
cd ~
python3 -m http.server 8888
```

**On Windows Workstation:**
1. Open browser
2. Navigate to: `http://192.168.1.237:8888/`
3. Click: `forward-watch-datasets.tar.gz`
4. Save to: `C:\forward-watch-training\`
5. Extract archive (use 7-Zip or Windows built-in)

**After download, stop HTTP server:**
- Press `Ctrl+C` in SSH terminal

---

## Transfer Method 2: SCP Direct Transfer

**On Windows (PowerShell or WSL):**
```bash
# From WSL Ubuntu:
scp -i ~/.ssh/d3kos_key d3kos@192.168.1.237:~/forward-watch-datasets.tar.gz /mnt/c/forward-watch-training/

# Or from Windows Downloads folder (via WSL):
scp -i ~/.ssh/d3kos_key d3kos@192.168.1.237:~/forward-watch-datasets.tar.gz /mnt/c/Users/donmo/Downloads/
```

---

## Transfer Method 3: USB Drive

1. **On Raspberry Pi:**
   ```bash
   # Copy to USB drive (if connected)
   sudo cp ~/forward-watch-datasets.tar.gz /media/d3kos/YOUR_USB_DRIVE/
   sudo sync
   ```

2. **Eject USB:**
   ```bash
   sudo umount /media/d3kos/YOUR_USB_DRIVE
   ```

3. **On Windows:**
   - Move file from USB to `C:\forward-watch-training\`

---

## Extract on Windows Workstation

**Using 7-Zip (Recommended):**
1. Right-click `forward-watch-datasets.tar.gz`
2. Choose: 7-Zip → Extract Here
3. Extract again (will create `kaggle-datasets` folder)

**Using Windows Built-in (Windows 11):**
1. Right-click `forward-watch-datasets.tar.gz`
2. Choose: Extract All
3. May need to extract twice (.tar.gz → .tar → folders)

---

## Verify Extraction

**Expected Directory Structure:**
```
C:\forward-watch-training\
└── kaggle-datasets\
    ├── nasa-marine-debris\
    ├── seaclear-debris\
    ├── uw-garbage-debris\
    ├── yolov8-ship-detection\
    └── ship-detection-aerial\
```

**Check image counts:**
- Total images: 5,000-10,000+ images across all datasets
- Each dataset should have images in subdirectories
- Verify at least 3 datasets extracted successfully

---

## Next Steps After Transfer

1. **Still Missing: Ice/Iceberg Dataset**
   - Need 2,000+ diverse iceberg images
   - Search Roboflow Universe: `https://universe.roboflow.com/search?q=class:iceberg`
   - Or Kaggle: Statoil Iceberg Classifier Challenge
   - Add to `C:\forward-watch-training\kaggle-datasets\ice-icebergs\`

2. **Combine with Existing Datasets:**
   - Move fish training datasets (if completed): `C:\fish-training\dataset\`
   - Merge into unified training structure

3. **Start YOLOv8-Marine Training:**
   - Follow: `/home/boatiq/Helm-OS/doc/forward-watch/FORWARD_WATCH_SPECIFICATION.md` Section 3.1
   - Training time: 20-30 hours on RTX 3060 Ti (8 classes, 20,000+ images)

---

## Troubleshooting

**"Archive is corrupted":**
- Re-download from Pi
- Verify file size matches (check with `ls -lh` on Pi)
- Use 7-Zip instead of Windows built-in extractor

**"Permission denied" on Pi:**
```bash
chmod 644 ~/forward-watch-datasets.tar.gz
```

**HTTP server port 8888 already in use:**
```bash
# Use different port
python3 -m http.server 9999
# Then access: http://192.168.1.237:9999/
```

**Transfer interrupted:**
- Resume with `wget` or `curl` (supports resume)
- Or restart transfer completely

---

## Archive Cleanup (After Successful Transfer)

**On Raspberry Pi (to save space):**
```bash
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237
rm ~/forward-watch-datasets.tar.gz
# Keep source datasets at ~/kaggle-datasets/ for reference
```

**On Windows (after extraction):**
- Delete `forward-watch-datasets.tar.gz` to save 1.5-2 GB disk space
- Keep extracted `kaggle-datasets` folder

---

**Questions? See:**
- Forward Watch Specification: `FORWARD_WATCH_SPECIFICATION.md`
- Training Guide: (To be created after datasets ready)
