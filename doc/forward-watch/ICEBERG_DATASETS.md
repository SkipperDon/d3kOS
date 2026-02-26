# Iceberg & Sea Ice Datasets for Forward Watch

**Date:** 2026-02-26
**Purpose:** Ice/Iceberg detection (8th class) for Forward Watch marine collision avoidance
**Requirement:** 2,000+ diverse images emphasizing GENERALIZATION

---

## 🎯 Critical Requirement: Maximum Diversity

**⚠️ NO TWO ICEBERGS ARE THE SAME**

The AI model must learn **general ice characteristics** rather than specific shapes:

- **Color variations:** White, blue-white, translucent, with dirt/debris
- **Shape variations:** Irregular, angular, rounded, tabular, pinnacled
- **Size range:** Small growlers (< 5m) to large icebergs (> 75m)
- **Surface conditions:** Smooth, jagged, melted, fractured
- **Water level:** Partially submerged (only 10-20% visible above water)
- **Lighting conditions:** Bright sun, overcast, fog, low light
- **Regions:** Arctic, Antarctic, Greenland, Alaska, etc.

**Training Strategy:** Focus on training the model to recognize **"ice-like"** characteristics (color, texture, context) rather than memorizing specific iceberg shapes.

---

## 📊 Recommended Kaggle Datasets (Downloaded)

### Phase 1: Optical Camera Images (~540 MB)

| # | Dataset | Size | Images | Type | Rating |
|---|---------|------|--------|------|--------|
| 1 | **saurabhbagchi/ship-and-iceberg-images** | 424 MB | ~5,000 | Ship vs Iceberg classification | ⭐ 0.875 |
| 2 | **alexandersylvester/arctic-sea-ice-image-masking** | 93 MB | ~2,000 | Arctic ice with segmentation masks | ⭐ 0.875 |
| 3 | **pennyrowe/arctic-ice-images-data** | 21 MB | ~500 | Arctic ice photography | ⚠️ 0.375 |

**Total:** ~7,500 images, ~540 MB

**Download Command:**
```bash
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237
cd ~
./download_iceberg_datasets.sh
```

**Location on Pi:** `/home/d3kos/kaggle-datasets/ice-icebergs/`

---

## 🌐 Additional Online Resources

### 1. Roboflow Universe - Iceberg Datasets

**URL:** [universe.roboflow.com/search?q=class:iceberg](https://universe.roboflow.com/search?q=class:iceberg)

**Features:**
- Multiple YOLOv8-ready datasets with annotations
- Free download with various formats (YOLOv8, COCO, Pascal VOC)
- Community-contributed datasets from various regions
- Pre-annotated bounding boxes

**How to Download:**
1. Visit Roboflow Universe
2. Search: `class:iceberg`
3. Browse datasets, select one
4. Click "Download" → Choose "YOLOv8" format
5. Download ZIP to Windows workstation

**Advantages:**
- Already annotated for YOLO training
- Various iceberg types and conditions
- Easy integration with YOLOv8 training pipeline

---

### 2. AMRC Iceberg Images Database

**URL:** [amrc.ssec.wisc.edu/data/iceberg.html](https://amrc.ssec.wisc.edu/data/iceberg.html)

**Source:** Antarctic Meteorological Research Center
**Type:** Optical camera photography of Antarctic icebergs
**Program:** United States Antarctic Program observations

**Features:**
- Real Antarctic iceberg photography
- Various sizes and conditions
- Scientific quality imagery

**Download:** Manual download from website

---

### 3. Research Datasets with Papers

#### a) Ship-Iceberg Classification (Sentinel-2 Multispectral)

**Paper:** [Ship-Iceberg Classification in SAR and Multispectral Satellite Images](https://www.mdpi.com/2072-4292/12/15/2353)

**Dataset Details:**
- 350 ships and icebergs
- Greenland waters
- Multispectral imagery (optical + radar)
- Includes metadata (position, size, classification)

**Access:** Contact authors or check paper supplementary materials

---

#### b) YOLOv8 Arctic Iceberg Detection Dataset

**Paper:** [Feasibility of Deep Learning-Based Iceberg Detection in Land-Fast Arctic Sea Ice Using YOLOv8 and SAR Imagery](https://www.mdpi.com/2072-4292/17/24/3998)

**Dataset Details:**
- 2,344 manually labeled icebergs
- SAR (Synthetic Aperture Radar) imagery
- Franz Josef Land region (Arctic)
- YOLOv8 model already trained on this data

**Limitations:** SAR imagery (radar), not optical camera

**Access:** Contact authors (dataset may be available upon request)

---

#### c) Antarctic Iceberg Mapping Dataset

**Paper:** [Mapping the extent of giant Antarctic icebergs with deep learning](https://tc.copernicus.org/articles/17/4675/2023/)

**Dataset Details:**
- Giant Antarctic icebergs
- Sentinel-1 SAR imagery
- U-net segmentation approach
- High-resolution extent mapping

**Limitations:** SAR imagery, focused on giant icebergs only

**Access:** Check paper supplementary materials

---

## 📈 Large-Scale Options (If Needed)

### irinaartemeva/arctic-sea-ice-concentration-dataset-20152023

**Size:** 8 GB
**Period:** 2015-2023
**Rating:** 0.706
**Type:** Arctic sea ice concentration time series

**Note:** Very large dataset, download only if optical datasets insufficient

---

## 🚀 Download Strategy

### Recommended Approach (3 Phases):

**Phase 1: Kaggle Optical Datasets (Started)**
- Script: `~/download_iceberg_datasets.sh`
- Size: ~540 MB
- Images: ~7,500
- Time: 10-20 minutes

**Phase 2: Roboflow Universe Datasets (Manual)**
- Visit Roboflow Universe
- Download 2-3 pre-annotated YOLOv8 datasets
- Estimated: 1,000-2,000 additional images
- Already annotated (saves labeling time!)

**Phase 3: Research/AMRC Datasets (Manual)**
- Download AMRC Antarctic images
- Contact paper authors for datasets
- Estimated: 500-1,000 additional images
- High-quality scientific imagery

**Total Target:** 9,000-10,500 images (exceeds 2,000 minimum)

---

## 🔄 Integration with Forward Watch Training

### Directory Structure:

```
C:\forward-watch-training\
├── kaggle-datasets\
│   ├── nasa-marine-debris\
│   ├── seaclear-debris\
│   ├── uw-garbage-debris\
│   ├── yolov8-ship-detection\
│   ├── ship-detection-aerial\
│   └── ice-icebergs\           ← NEW
│       ├── ship-iceberg-images\
│       ├── arctic-ice-masking\
│       └── arctic-ice-images\
└── roboflow-icebergs\           ← NEW (Phase 2)
    ├── dataset1\
    └── dataset2\
```

### Labeling Requirements:

**If Kaggle datasets unlabeled:**
- Use [LabelImg](https://github.com/heartexlabs/labelImg) or [Roboflow](https://roboflow.com) for annotation
- Label class: `ice` or `iceberg`
- Bounding boxes around all visible ice/icebergs
- Estimated time: 2-3 seconds per image

**If Roboflow datasets:**
- Already annotated in YOLOv8 format ✓
- Just verify labels are correct
- May need to rename class to match your schema

---

## 📊 Current Status

| Phase | Status | Images | Size | Location |
|-------|--------|--------|------|----------|
| Phase 1: Kaggle Optical | ⏳ Downloading | ~7,500 | ~540 MB | Pi: `/home/d3kos/kaggle-datasets/ice-icebergs/` |
| Phase 2: Roboflow YOLOv8 | ⏳ Pending | ~2,000 | TBD | Manual download |
| Phase 3: Research/AMRC | ⏳ Pending | ~1,000 | TBD | Manual download |
| **Total Estimated** | | **~10,500** | **~1 GB** | |

**Minimum Requirement:** 2,000 images ✓ (Phase 1 alone provides 7,500)

---

## 🔗 Quick Links

- **Roboflow Universe Iceberg Search:** [universe.roboflow.com/search?q=class:iceberg](https://universe.roboflow.com/search?q=class:iceberg)
- **AMRC Iceberg Database:** [amrc.ssec.wisc.edu/data/iceberg.html](https://amrc.ssec.wisc.edu/data/iceberg.html)
- **Forward Watch Specification:** `FORWARD_WATCH_SPECIFICATION.md`
- **Dataset Transfer Instructions:** `DATASET_TRANSFER_INSTRUCTIONS.md`

---

## ⚠️ Important Notes

1. **Optical vs SAR Imagery:**
   - Forward Watch uses optical camera (Reolink RLC-810A)
   - SAR (radar) datasets are different technology
   - Prefer optical/visible light images when possible
   - SAR can be supplemental but not primary

2. **Diversity Over Quantity:**
   - 2,000 diverse images > 10,000 similar images
   - Mix regions: Arctic + Antarctic + Greenland
   - Mix conditions: sunny, overcast, fog, night
   - Mix sizes: growlers, bergy bits, large icebergs

3. **Annotation Consistency:**
   - Use single class name: `ice` or `iceberg`
   - Don't distinguish types (tabular, dome, etc.)
   - Model learns from visual features, not labels

4. **False Positives:**
   - White boats/sails may be confused with ice
   - Waves with foam may trigger false positives
   - Training with ship datasets helps reduce this

---

**Next Steps:**
1. ✅ Run `~/download_iceberg_datasets.sh` on Pi (Phase 1)
2. ⏳ Download 2-3 YOLOv8 datasets from Roboflow Universe (Phase 2)
3. ⏳ Transfer all datasets to Windows workstation
4. ⏳ Merge with existing Forward Watch training datasets
5. ⏳ Begin YOLOv8-Marine training (8 classes total)

---

**Documentation Version:** 1.0
**Last Updated:** 2026-02-26
**Estimated Images:** 7,500-10,500 (optical camera imagery)
