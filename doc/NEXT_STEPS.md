# What to Do Next - Quick Guide

**Date:** 2026-02-26
**Current Status:** Bug fixes committed, datasets ready, v0.9.2 planned

---

## 🎯 Immediate Actions (Next 30 Minutes)

### 1. Push Git Commits to GitHub

**You have 4 commits ready to push:**

```bash
# Check what's ready to push
git log --oneline -4

# Push to GitHub
git push origin main

# Verify push succeeded
git status
```

**What You're Pushing:**
- Voice assistant watchdog system
- WordPress landing page (AtMyBoat.com)
- Bug fix (sysstat dependency + Forward Watch datasets)
- Problems & Resolutions log

---

### 2. Transfer Forward Watch Datasets to Windows Workstation

**Datasets are ready on Raspberry Pi:** `~/forward-watch-complete.tar.gz` (112 MB)

#### Option A: HTTP Download (Easiest)

**On Raspberry Pi (via SSH):**
```bash
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237
cd ~
python3 -m http.server 8888
```

**On Windows:**
1. Open browser
2. Go to: `http://192.168.1.237:8888/`
3. Click: `forward-watch-complete.tar.gz`
4. Save to: `C:\forward-watch-training\`

**After download:**
- Press `Ctrl+C` in SSH terminal to stop HTTP server

#### Option B: Direct SCP (From WSL)

```bash
# From WSL Ubuntu
scp -i ~/.ssh/d3kos_key d3kos@192.168.1.237:~/forward-watch-complete.tar.gz /mnt/c/forward-watch-training/
```

---

### 3. Extract Datasets on Windows

**Using 7-Zip (Recommended):**
1. Right-click `forward-watch-complete.tar.gz`
2. Choose: 7-Zip → Extract Here
3. Extract again (will extract .tar file)
4. Creates: `kaggle-datasets\` folder

**What You'll Have:**
```
C:\forward-watch-training\
└── kaggle-datasets\
    ├── ice-icebergs\           ← 6,790 images
    ├── nasa-marine-debris\     ← 300 images
    ├── seaclear-debris\        ← 20,000 images
    ├── uw-garbage-debris\      ← 1,200 images
    ├── yolov8-ship-detection\  ← 25,000 images
    └── ship-detection-aerial\  ← 1,500 images
```

**Total:** 54,789 images for 8 detection classes

---

## 📅 Short-Term Tasks (Next Week)

### 4. Start Forward Watch YOLOv8-Marine Training (Optional)

**⚠️ Note:** This is a 20-30 hour project. Start only if you have time.

**Requirements:**
- ✅ Windows workstation with GPU (RTX 3060 Ti)
- ✅ Datasets downloaded and extracted
- ✅ Training script ready

**Quick Start:**
```bash
# On Windows (after extracting datasets)
cd C:\forward-watch-training
python train_yolov8_marine.py
```

**Estimated Time:** 20-30 hours on RTX 3060 Ti

**What You'll Get:**
- YOLOv8-Marine model (8 classes)
- ONNX format for Raspberry Pi
- Ready for Signal K plugin integration

**Can Be Deferred:** Forward Watch is planned for v0.9.2, not urgent for v0.9.1.2

---

### 5. Test Holger's Bug Fix (If You Have Time)

**Quick Test:**
```bash
# SSH to Raspberry Pi
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237

# Verify sysstat installed
which mpstat
mpstat 1 3

# Check Signal K logs (should be no "mpstat: not found" errors)
journalctl -u signalk -n 50 --no-pager | grep mpstat
```

**Expected Result:** No errors, CPU monitoring working

---

### 6. Review v0.9.2 Release Plan

**File:** `/home/boatiq/Helm-OS/VERSION_0.9.2_PLAN.md`

**Key Items for v0.9.2:**
1. ⚠️ **CRITICAL:** Fix voice assistant wake word detection (6-8 hours)
2. Data export system (complete implementation, 10-12 hours)
3. Boatlog export button (2-3 hours)
4. Forward Watch implementation (20-30 hours)
5. Other UI/feature improvements

**Estimated Timeline:** 7 weeks (end of March 2026)

---

## 🔧 Medium-Term Tasks (Next Month)

### 7. Priority 1: Fix Voice Assistant (CRITICAL)

**Status:** Wake word detection not working
**Time Estimate:** 6-8 hours dedicated debugging session

**Recommended Approach:**
1. Timeline analysis (system updates since last working)
2. Manual PocketSphinx testing
3. Try alternative wake word engines (Vosk, Porcupine)
4. Fix PipeWire audio signal loss
5. Document solution

**Blocker:** Yes - Tier 2+ feature broken

---

### 8. Priority 2: Complete Data Export System

**Status:** API exists, queue system not implemented
**Time Estimate:** 10-12 hours

**Tasks:**
- Export queue system (queue.json)
- Boot-time export service
- Daily cron job (Tier 2+)
- All 8 export categories
- Central database API endpoints

**Blocker:** No - but important for Tier 1+ features

---

### 9. Priority 3: Boatlog Export Button

**Status:** Button crashes
**Time Estimate:** 2-3 hours

**Simple fix - should be quick!**

---

## 📊 What's Already Done (No Action Needed)

✅ **Bug Fixes:**
- sysstat package documented
- Signal K GPS errors fixed
- QR code simplified
- Export manager port fixed
- On-screen keyboard auto-focus added

✅ **Documentation:**
- Bug fix guide (BUGFIX_SYSSTAT_HARDWARE_CONFIG.md)
- Problems log (15 issues documented)
- Forward Watch specification (complete)
- Iceberg datasets (6,790 images)

✅ **Datasets:**
- 54,789 images downloaded (4.1 GB → 112 MB compressed)
- 8 detection classes covered
- Ready for training

✅ **System Status:**
- d3kOS v0.9.1.2 running
- Tier 3 active (all features)
- 22+ services running
- Signal K stable

---

## 🚫 What NOT to Do

❌ **Don't start training fish model** - Still downloading (5,929 of 20,000 images, ~30% complete)
❌ **Don't try to fix WiFi hotspot** - Hardware limitation, can't be fixed
❌ **Don't spend time on e-commerce** - 40-60 hour project, defer to later
❌ **Don't rebuild voice assistant yet** - Need systematic debugging first

---

## ❓ If You're Unsure What to Do

**Quick Wins (< 1 hour each):**
1. Push git commits to GitHub
2. Transfer datasets to Windows
3. Extract datasets
4. Review v0.9.2 plan

**Medium Tasks (2-8 hours):**
5. Fix boatlog export button
6. Test Holger's bug fix
7. Update documentation

**Big Projects (20+ hours):**
8. Fix voice assistant (CRITICAL)
9. Complete data export system
10. Train Forward Watch model

**Start with the Quick Wins!** 🎯

---

## 📞 Need Help?

**Documentation:**
- `VERSION_0.9.2_PLAN.md` - Next version roadmap
- `PROBLEMS_AND_RESOLUTIONS.md` - Known issues
- `doc/forward-watch/` - Forward Watch specs
- `MASTER_SYSTEM_SPEC.md` - Complete system spec

**Status Check:**
```bash
# On Raspberry Pi
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237
cd /opt/d3kos
./check-system-status.sh  # (if script exists)

# Or manually
systemctl status signalk
systemctl status d3kos-*
```

---

## ✅ Success Criteria - You'll Know You're Done When:

**Today (Immediate):**
- ✅ Git commits pushed to GitHub
- ✅ Datasets transferred to Windows
- ✅ Datasets extracted (54,789 images ready)

**This Week:**
- ✅ v0.9.2 plan reviewed
- ✅ Priority tasks identified
- ✅ Quick wins completed (boatlog export, etc.)

**This Month:**
- ✅ Voice assistant fixed
- ✅ Data export system complete
- ✅ Forward Watch model trained

**Next Release (v0.9.2):**
- ✅ All critical bugs fixed
- ✅ Core features complete
- ✅ Field tested and stable

---

**You're doing great! Start with the Quick Wins and build momentum.** 🚀

**Next Command:**
```bash
git push origin main
```
