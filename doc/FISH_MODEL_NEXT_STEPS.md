# Fish Detection Model - Next Steps & User Actions Required

**Date:** 2026-02-18
**Session:** Session-Fish-1, Task 2
**Status:** ⏸️ PAUSED - Awaiting user decision

---

## Current Status

✅ **Task 1 Complete:** Model evaluation finished
- Found 9 fish detection models
- Primary recommendation: Roboflow Freshwater Fish Detection
- Alternative: Hugging Face grayscale fish detector (93.6% accuracy)
- Documentation: `FISH_MODELS_EVALUATION.md`

⏸️ **Task 2 Blocked:** Model download requires user action

---

## Why We're Blocked

**Problem 1: Roboflow Model (RECOMMENDED)**
- Requires free Roboflow account creation
- Cannot proceed without user API key
- **5 minutes** to set up account

**Problem 2: Hugging Face Model (ALTERNATIVE)**
- Downloaded successfully (6MB PyTorch model)
- Conversion to ONNX requires PyTorch installation
- PyTorch is ~1GB+ download, not currently installed
- **1-2 hours** to install dependencies and convert

**Problem 3: Custom Training (FALLBACK)**
- Build dataset from public sources
- Train custom YOLOv8n model
- **6-8 hours** total time

---

## Recommended Path: Roboflow Account (5 minutes setup)

This is the **fastest and easiest** option:

### Step 1: Create Free Roboflow Account
1. Go to: https://roboflow.com
2. Click "Sign Up" (top right)
3. Use Google/GitHub OAuth or email
4. Confirm email address

### Step 2: Get API Key
1. Log in to Roboflow
2. Go to: https://app.roboflow.com/settings/api
3. Copy your Private API Key
4. Looks like: `abc123xyz456...` (long alphanumeric string)

### Step 3: Provide API Key to Claude
Just paste the API key in chat, and I'll:
- Download the freshwater fish detection model
- Export to ONNX format automatically
- Deploy to Raspberry Pi
- Test inference speed and accuracy
- Complete Task 2 in ~1 hour

### Step 4: Done!
You'll have a working fish detection model ready to test.

---

## Alternative Path A: Manual Hugging Face Conversion (2 hours)

If you don't want to create a Roboflow account, you can do the model conversion locally on a machine with Python and pip:

### Requirements:
- Python 3.8+ with pip installed
- ~2GB free disk space
- Internet connection

### Instructions:
```bash
# 1. Install ultralytics (includes PyTorch, ONNX dependencies)
pip install ultralytics

# 2. Download model from Hugging Face
wget https://huggingface.co/akridge/yolo8-fish-detector-grayscale/resolve/main/yolov8n_fish_trained.pt

# 3. Convert to ONNX (Python script)
python3 << 'EOF'
from ultralytics import YOLO

# Load PyTorch model
model = YOLO("yolov8n_fish_trained.pt")

# Export to ONNX
print("Converting to ONNX...")
model.export(format="onnx", imgsz=640)
print("✓ Conversion complete! File: yolov8n_fish_trained.onnx")
EOF

# 4. Copy ONNX file to Pi
scp yolov8n_fish_trained.onnx d3kos@192.168.1.237:/opt/d3kos/models/marine-vision/fish_detector.onnx
```

**Pros:**
- No account creation needed
- Model has proven accuracy (93.6% mAP50)
- Free and open-source

**Cons:**
- Model trained on grayscale imagery (may not work well with color camera)
- Underwater focus (different lighting than above-water fishing)
- Requires Python setup on local machine

---

## Alternative Path B: Custom Training (6-8 hours)

If both options above fail, we can train a custom model specifically for Ontario freshwater fish:

### Approach:
1. **Dataset Collection** (2 hours)
   - iNaturalist API: Ontario fish observations
   - Open Images: Fish class images
   - Roboflow Public: Freshwater fish datasets
   - Target: 500-1000 annotated images

2. **Model Training** (4-6 hours)
   - Platform: Google Colab (free GPU)
   - Base model: YOLOv8n pretrained on COCO
   - Fine-tune for Ontario species (bass, pike, walleye, perch, sunfish)
   - Export to ONNX

3. **Deployment** (30 minutes)
   - Copy to Pi, test, integrate

**Pros:**
- Optimized specifically for Ontario fish species
- Color imagery (matches d3kOS camera)
- Highest potential accuracy for our use case

**Cons:**
- Longest time investment
- Requires manual dataset curation
- Training expertise needed

---

## Comparison Table

| Option | User Action | Time | Accuracy | Color Support | Ontario Species |
|--------|-------------|------|----------|---------------|-----------------|
| **Roboflow** | Create account (5 min) | 1 hour total | ~75%* | Yes | Unknown |
| **Hugging Face** | Install Python packages | 2 hours total | 93.6% | No (grayscale) | No (generic fish) |
| **Custom Training** | None (Claude does it) | 6-8 hours | >85%** | Yes | Yes (optimized) |

\* Estimated based on similar models
\** Expected with fine-tuning

---

## What Happens Next (After User Chooses)

### If Roboflow (Recommended):
1. User provides API key → 5 seconds
2. Claude downloads model → 2 minutes
3. Claude exports to ONNX → 1 minute
4. Claude deploys to Pi → 2 minutes
5. Claude tests inference → 15 minutes
6. **Task 2 complete → Move to Task 5** (skip Tasks 3-4)

### If Hugging Face:
1. User runs conversion commands → 20 minutes
2. User copies ONNX file to Pi → 1 minute
3. Claude tests model → 15 minutes
4. If grayscale issue, fall back to custom training
5. **Task 2 complete → Move to Task 5**

### If Custom Training:
1. Claude collects dataset → 2 hours
2. Claude trains model on Colab → 4-6 hours
3. Claude deploys and tests → 1 hour
4. **Tasks 2-4 complete → Move to Task 5**

---

## My Recommendation

**Choose Roboflow** - Here's why:
- ✅ Fastest path (5 min setup + 1 hour implementation)
- ✅ Free account, no credit card needed
- ✅ Color imagery support
- ✅ Proven YOLO models
- ✅ Easy ONNX export
- ✅ Can always fine-tune later if accuracy insufficient

**Second choice: Custom Training**
- If you don't want to create any accounts
- Best long-term accuracy for Ontario species
- Takes longer but highest quality result

**Avoid: Hugging Face grayscale model**
- Trained on underwater grayscale imagery
- d3kOS has color camera, above-water use case
- Likely poor accuracy in production

---

## Files Downloaded So Far

On Raspberry Pi:
- `/tmp/yolov8n_fish_grayscale.pt` (6.0MB) - PyTorch model from Hugging Face

On Ubuntu/WSL:
- `/tmp/yolov8n_fish_grayscale.pt` (6.0MB) - Copy for conversion

**Note:** These can be deleted if choosing Roboflow option.

---

## Session Status

**Session-Fish-1 Progress:** 1/6 tasks complete
- ✅ Task 1: Model evaluation
- ⏸️ Task 2: Model download (BLOCKED - awaiting user)
- ⏸️ Tasks 3-6: Pending

**Estimated Completion:**
- Roboflow path: +1 hour from user providing API key
- Hugging Face path: +2 hours from user running conversion
- Custom training path: +6-8 hours from user approval

---

## Ready to Proceed

Just tell me which option you want:
1. **"Use Roboflow"** - I'll walk you through 5-minute account setup
2. **"Use Hugging Face"** - I'll provide conversion commands to run
3. **"Train custom model"** - I'll start dataset collection immediately

**Or if you want to defer this:**
- I can pause Session-Fish-1 and work on something else
- Come back to fish detection later when ready
- Other priorities: Charts page, boatlog export fix, distribution prep

---

**Waiting for your decision!** 🎣
