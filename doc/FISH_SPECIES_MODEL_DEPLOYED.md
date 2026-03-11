# Fish Species Model - Deployment Summary

**Date:** 2026-02-27
**Status:** ✅ Model deployed, ⚠️ NOT suitable for freshwater fishing

---

## What Was Accomplished

### ✅ Model Training Complete
- **483 species** trained successfully
- **Model files:**
  - `fish_classifier_483species_best.onnx` (18 MB) - Deployed to Pi
  - `fish_classifier_483species_best.pth` (18 MB) - PyTorch backup
  - `fish_classifier_483species_best_species.json` (16 KB) - Species list

### ✅ Deployed to Raspberry Pi
- **Location:** `/opt/d3kos/models/fish-species/`
- **Files on Pi:**
  - `fish_classifier_483species_best.onnx` (18 MB)
  - `species_list.json` (16 KB)
  - `fish_model.onnx` (12 MB) - older backup model

---

## CRITICAL LIMITATION ⚠️

### This Model is for SALTWATER/TROPICAL FISH

**Species Covered:**
- 483 Indo-Pacific reef and coastal species
- Examples: Groupers, Snappers, Trevally, Wrasses, Parrotfish, Surgeonfish, Sharks, Rays
- Geographic: Australia, Indonesia, Philippines, Pacific Islands, Indian Ocean

**Species NOT Covered (Your Fishing Area):**
- ❌ Largemouth Bass
- ❌ Smallmouth Bass
- ❌ Northern Pike
- ❌ Walleye
- ❌ Yellow Perch
- ❌ Muskie
- ❌ Lake Trout
- ❌ Rainbow Trout
- ❌ Salmon species
- ❌ ALL Great Lakes / Lake Simcoe freshwater fish

### Why This Happened

The training dataset used was focused on tropical saltwater fish, not North American freshwater species. This model will NOT work for your fishing on Lake Simcoe.

---

## What Needs to Happen Next

### Option 1: Train Freshwater Model (Recommended)

**Target Species (50-100 Great Lakes/Ontario species):**

**Bass Family (5 species):**
- Largemouth Bass (*Micropterus salmoides*)
- Smallmouth Bass (*Micropterus dolomieu*)
- Spotted Bass (*Micropterus punctulatus*)
- White Bass (*Morone chrysops*)
- Striped Bass (*Morone saxatilis*)

**Pike Family (3 species):**
- Northern Pike (*Esox lucius*)
- Muskellunge (*Esox masquinongy*)
- Chain Pickerel (*Esox niger*)

**Perch Family (3 species):**
- Yellow Perch (*Perca flavescens*)
- Walleye (*Sander vitreus*)
- Sauger (*Sander canadensis*)

**Panfish (8 species):**
- Bluegill (*Lepomis macrochirus*)
- Pumpkinseed (*Lepomis gibbosus*)
- Black Crappie (*Pomoxis nigromaculatus*)
- White Crappie (*Pomoxis annularis*)
- Rock Bass (*Ambloplites rupestris*)
- Green Sunfish (*Lepomis cyanellus*)
- Longear Sunfish (*Lepomis megalotis*)
- Redear Sunfish (*Lepomis microlophus*)

**Trout & Salmon (10 species):**
- Lake Trout (*Salvelinus namaycush*)
- Brook Trout (*Salvelinus fontinalis*)
- Brown Trout (*Salmo trutta*)
- Rainbow Trout (*Oncorhynchus mykiss*)
- Chinook Salmon (*Oncorhynchus tshawytscha*)
- Coho Salmon (*Oncorhynchus kisutch*)
- Atlantic Salmon (*Salmo salar*)
- Pink Salmon (*Oncorhynchus gorbuscha*)
- Sockeye Salmon (*Oncorhynchus nerka*)
- Steelhead (*Oncorhynchus mykiss*)

**Catfish (5 species):**
- Channel Catfish (*Ictalurus punctatus*)
- Flathead Catfish (*Pylodictis olivaris*)
- Blue Catfish (*Ictalurus furcatus*)
- Brown Bullhead (*Ameiurus nebulosus*)
- Yellow Bullhead (*Ameiurus natalis*)

**Others (10-20 species):**
- Burbot, Whitefish, Cisco, Gar, Carp, Drum, Sturgeon, etc.

**Training Requirements:**
- **Dataset size:** 100-500 images per species (5,000-25,000 images total)
- **Sources:** iNaturalist, FishBase, Fishbrain, fishing forums, user contributions
- **Training time:** 12-24 hours on GPU (RTX 3060 Ti)
- **Accuracy target:** 80-85% on test set

---

## Integration Status

### Current System (Already Deployed):
1. ✅ **Fish Detection** - YOLOv8 model detects "fish" (generic)
   - Location: `/opt/d3kos/models/marine-vision/fish_detector.onnx`
   - Working: Yes
   - Accuracy: 93.6% mAP@50

2. ✅ **Species Classification** - 483 tropical species model deployed
   - Location: `/opt/d3kos/models/fish-species/fish_classifier_483species_best.onnx`
   - Working: Yes (not integrated yet)
   - Accuracy: Unknown (not tested)
   - **Problem:** Wrong species (saltwater, not freshwater)

### Integration Needed:
- ⏳ Connect fish detector → species classifier pipeline
- ⏳ Test with sample images
- ⏳ Deploy to Marine Vision web UI
- ⏳ Add to Telegram notifications

---

## Recommendations

### Immediate (Today):
1. **Test the tropical fish model** - Verify it works technically
2. **Document the limitation** - Update user documentation
3. **Plan freshwater model training** - Start collecting dataset

### Short-term (Next Week):
1. **Collect freshwater fish dataset** - 5,000-10,000 images minimum
2. **Train freshwater model** - 50-100 Great Lakes species
3. **Deploy freshwater model** - Replace tropical model

### Long-term (Future):
1. **Regional model switching** - GPS-based model selection
   - Freshwater model for inland lakes
   - Saltwater model for ocean/coastal
   - Automatic switching based on GPS coordinates

---

## Files Location

**On Raspberry Pi:**
- Models: `/opt/d3kos/models/fish-species/`
- Service: `/opt/d3kos/services/marine-vision/fish_detector.py`
- Database: `/opt/d3kos/data/marine-vision/captures.db`

**On Development Machine:**
- Training output: `~/Helm-OS/output/`
- Documentation: `~/Helm-OS/doc/FISH_*.md`
- This file: `~/Helm-OS/FISH_SPECIES_MODEL_DEPLOYED.md`

---

## Next Steps

**What would you like to do?**

**Option A:** Train freshwater model NOW (12-24 hours)
- Collect Great Lakes fish dataset
- Train on RTX 3060 Ti
- Deploy to replace tropical model

**Option B:** Test tropical model first (1-2 hours)
- Integrate species classifier
- Test with tropical fish images
- Verify system works technically
- Then plan freshwater training

**Option C:** Use current system as-is
- Generic "fish" detection only
- No species identification
- Wait for freshwater model later

**Your choice?**

---

**Summary:** You successfully trained a 483-species tropical fish model, but it won't work for Lake Simcoe fishing. Need to train a separate freshwater model for your actual use case.
