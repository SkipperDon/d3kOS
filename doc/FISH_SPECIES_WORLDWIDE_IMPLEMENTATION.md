# Worldwide Fish Species Identification - Implementation Plan

**Date:** February 25, 2026
**Prerequisites:** 128GB SD card installed ✅
**Status:** Ready to implement
**Target:** 1000+ species, 75-85% accuracy, <10s identification time

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Dataset Acquisition](#dataset-acquisition)
3. [Model Training Strategy](#model-training-strategy)
4. [Regional Models](#regional-models)
5. [Regulations Database](#regulations-database)
6. [Implementation Timeline](#implementation-timeline)
7. [Limitations & Disclaimers](#limitations--disclaimers)

---

## System Architecture

### Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      Marine Vision Fish ID                       │
└─────────────────────────────────────────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
   ┌────▼────┐          ┌──────▼──────┐      ┌───────▼────────┐
   │Detection│          │Classification│      │  Regulations   │
   │ YOLOv8n │          │ EfficientNet │      │    Database    │
   │ (13MB)  │          │  (200-500MB) │      │   (500MB-1GB)  │
   └────┬────┘          └──────┬───────┘      └───────┬────────┘
        │                      │                      │
        │ Person + Fish        │ Species ID           │ Size/Bag
        │ Detected             │ + Confidence         │ Limits
        │                      │                      │
        └──────────────────────┴──────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Telegram Notify    │
                    │  Photo + Species    │
                    │  + Regulations      │
                    └─────────────────────┘
```

### Processing Flow

1. **Detection** (2-3s)
   - YOLOv8n detects person + fish
   - Crops fish bounding box
   - Quality check (blur, lighting, size)

2. **GPS Lookup** (<1s)
   - Get current GPS coordinates
   - Determine region (North America, Europe, Asia, etc.)
   - Load appropriate regional model (if not cached)

3. **Classification** (3-5s)
   - EfficientNet-B0/B1 species identification
   - Returns top 3 predictions with confidence scores
   - Hierarchical fallback: Species → Genus → Family

4. **Confidence Evaluation**
   - >80%: Display species name
   - 60-80%: Display genus + "likely [species]"
   - <60%: "Unknown fish - upload for cloud ID?"

5. **Regulations Lookup** (1-2s)
   - Query local database by species + GPS + date
   - Return size limits, bag limits, season status
   - Display warnings if undersize/over limit/out of season

6. **Notification** (2-3s)
   - Send photo to Telegram
   - Include species, confidence, regulations
   - Google Maps link to catch location

**Total Time:** 8-14 seconds (acceptable for catch photo)

---

## Dataset Acquisition

### Primary Sources

#### 1. iNaturalist Research-Grade Observations

**URL:** https://www.inaturalist.org/
**Coverage:** 3M+ fish observations worldwide
**Quality:** Research-grade (expert verified)
**License:** CC BY / CC0 (varies)

**Download Method:**
```bash
# Install iNaturalist API client
pip3 install pyinaturalist

# Download by taxon (e.g., all bass species)
python3 << 'EOF'
from pyinaturalist import get_observations

# Get 500 observations of Largemouth Bass
obs = get_observations(
    taxon_id=66867,  # Micropterus salmoides
    photos=True,
    quality_grade='research',
    per_page=200,
    pages=3
)

# Download photos
for o in obs['results']:
    species = o['taxon']['name']
    photo_url = o['photos'][0]['url'].replace('square', 'large')
    # Download photo_url, save to /dataset/bass/micropterus_salmoides_001.jpg
EOF
```

**Target Species:** 1000 most common recreational catches

#### 2. FishBase Image Database

**URL:** https://www.fishbase.se/
**Coverage:** 58,000+ species profiles
**Photos:** 64,000+ images (swimming fish)
**License:** Varies (check each image)

**Limitation:** Most photos are live/swimming fish, not caught fish
**Use Case:** Supplement dataset for rare species

#### 3. GBIF (Global Biodiversity Information Facility)

**URL:** https://www.gbif.org/
**Coverage:** 50M+ occurrence records
**Photos:** Specimen photos (dead fish, museum samples)
**License:** CC0 / CC BY

**Download Method:**
```bash
# Use GBIF API
# Filter: Actinopterygii (ray-finned fishes)
# Filter: hasCoordinate=true, hasImage=true
# Quality: research grade

wget "https://api.gbif.org/v1/occurrence/search?taxonKey=204&hasCoordinate=true&hasImage=true&limit=1000"
```

#### 4. Custom "Caught Fish" Dataset

**Source:** User contributions + scraping fishing forums
**Target:** 50,000+ images of fish being held
**Critical:** This is KEY - caught fish look VERY different from swimming fish

**Scraping Sources:**
- r/fishing (Reddit)
- Fishbrain app uploads
- Fishing tournament photos
- YouTube fishing video screenshots

**Labeling:** Use Amazon Mechanical Turk or Roboflow for annotation

---

### Dataset Organization

```
/opt/d3kos/datasets/fish-worldwide/
├── metadata.json                    # Dataset manifest
├── species_list.json                # 1000 species with IDs
├── train/                          # 80% for training
│   ├── class_0_micropterus_salmoides/
│   │   ├── image_001.jpg           # 100-500 images per species
│   │   ├── image_002.jpg
│   │   └── ...
│   ├── class_1_esox_lucius/
│   └── ...
├── val/                            # 10% for validation
│   ├── class_0_micropterus_salmoides/
│   └── ...
└── test/                           # 10% for final testing
    ├── class_0_micropterus_salmoides/
    └── ...

Total Size: ~10GB (100 images × 1000 species × 10KB average)
```

---

## Model Training Strategy

### Phase 1: Base Model (Week 1)

**Target:** 200 most common species
**Model:** EfficientNet-B0 (20MB)
**Training:** Transfer learning from ImageNet

**Species List:**
- **North America (70 species):**
  - Bass: Largemouth, Smallmouth, Spotted, White, Striped
  - Trout: Rainbow, Brown, Brook, Lake, Cutthroat
  - Panfish: Bluegill, Crappie, Perch, Sunfish
  - Pike: Northern, Muskie, Chain Pickerel
  - Walleye, Sauger
  - Catfish: Channel, Flathead, Blue
  - Salmon: Chinook, Coho, Sockeye, Atlantic
  - Carp: Common, Grass, Silver
  - Gar: Longnose, Alligator
  - Drum: Freshwater
  - Sturgeon: Lake, White
  - etc.

- **Europe (50 species):**
  - Pike, Zander, Perch
  - Carp: Common, Mirror, Leather
  - Trout: Brown, Rainbow, Sea
  - Salmon: Atlantic, Sea
  - Bream, Tench, Roach, Rudd
  - Catfish: Wels
  - etc.

- **Asia-Pacific (40 species):**
  - Snakehead: Giant, Channa
  - Barramundi, Mangrove Jack
  - Grouper species
  - Trevally species
  - Barracuda
  - Tilapia species
  - etc.

- **Saltwater Global (40 species):**
  - Tuna: Bluefin, Yellowfin, Albacore
  - Marlin: Blue, Black, Striped
  - Snapper: Red, Yellowtail, Mangrove
  - Cod: Atlantic, Pacific
  - Halibut: Atlantic, Pacific
  - Mahi-mahi, Wahoo
  - Redfish, Seatrout
  - etc.

**Training Code:**
```python
import torch
import torchvision.models as models
from torch import nn, optim
from torchvision import datasets, transforms

# Load pretrained EfficientNet-B0
model = models.efficientnet_b0(pretrained=True)

# Freeze early layers (transfer learning)
for param in model.parameters():
    param.requires_grad = False

# Replace classifier for 200 species
model.classifier = nn.Sequential(
    nn.Dropout(0.2),
    nn.Linear(1280, 200)  # 200 species
)

# Data augmentation (critical for caught fish)
train_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
    transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),  # Simulate hand shake
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# Load dataset
train_data = datasets.ImageFolder('/opt/d3kos/datasets/fish-worldwide/train', transform=train_transform)
train_loader = torch.utils.data.DataLoader(train_data, batch_size=32, shuffle=True)

# Train
optimizer = optim.Adam(model.classifier.parameters(), lr=0.001)
criterion = nn.CrossEntropyLoss()

for epoch in range(20):
    for images, labels in train_loader:
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

# Export to ONNX for Pi deployment
torch.onnx.export(model, dummy_input, "fish_classifier_200sp.onnx")
```

**Training Time:** 12-24 hours on GPU (laptop with NVIDIA RTX)
**Expected Accuracy:** 80-85% on test set

---

### Phase 2: Expanded Model (Week 2-3)

**Target:** 500 species
**Model:** EfficientNet-B1 (30MB)
**Incremental training:** Add 300 species to Phase 1 model

**Additional Regions:**
- South America: Peacock Bass, Arapaima, Piranha, Dorado, etc.
- Africa: Nile Perch, Tigerfish, Tilapia, etc.
- Australia: Barramundi, Murray Cod, Golden Perch, etc.

**Training Time:** 20-36 hours
**Expected Accuracy:** 75-80% (more species = harder)

---

### Phase 3: Full Model (Week 4)

**Target:** 1000 species
**Model:** EfficientNet-B2 (36MB) or EfficientNet-B1 with larger classifier
**Final training:** Complete worldwide coverage

**Training Time:** 48-72 hours
**Expected Accuracy:** 70-75% (realistic for 1000 species)

---

## Regional Models

### GPS-Based Model Loading

**Regions:**
1. **North America Freshwater** (150 species, 25MB)
2. **North America Saltwater** (100 species, 20MB)
3. **Europe** (120 species, 22MB)
4. **Asia-Pacific** (150 species, 25MB)
5. **South America** (80 species, 18MB)
6. **Africa** (60 species, 15MB)
7. **Australia/Oceania** (80 species, 18MB)
8. **Global Saltwater** (260 species, 40MB)

**Implementation:**
```python
import requests

def get_region_from_gps(lat, lon):
    """Determine fishing region from GPS coordinates"""
    # North America
    if -170 < lon < -50 and 25 < lat < 70:
        # Further split by freshwater vs saltwater
        # Check if near coast (within 50km)
        if is_coastal(lat, lon):
            return "north_america_saltwater"
        else:
            return "north_america_freshwater"

    # Europe
    elif -10 < lon < 40 and 35 < lat < 70:
        return "europe"

    # Asia-Pacific
    elif 60 < lon < 180 and -10 < lat < 60:
        return "asia_pacific"

    # South America
    elif -80 < lon < -35 and -55 < lat < 12:
        return "south_america"

    # Africa
    elif -20 < lon < 50 and -35 < lat < 35:
        return "africa"

    # Australia/Oceania
    elif 110 < lon < 180 and -50 < lat < 0:
        return "australia_oceania"

    # Global saltwater (fallback for open ocean)
    else:
        return "global_saltwater"

def load_regional_model(region):
    """Load appropriate model for region"""
    model_path = f"/opt/d3kos/models/fish-species/{region}.onnx"

    # Check if model cached
    if os.path.exists(model_path):
        return load_onnx_model(model_path)

    # Otherwise load global model (slower but covers all species)
    return load_onnx_model("/opt/d3kos/models/fish-species/global_1000sp.onnx")
```

**Benefits:**
- Faster inference (fewer classes to consider)
- Higher accuracy (regional fish easier to distinguish)
- Lower memory usage (smaller models)

**Fallback:** If GPS unavailable or region unknown → use global 1000-species model

---

## Regulations Database

### Structure

```json
{
  "species": {
    "micropterus_salmoides": {
      "common_names": {
        "en_US": "Largemouth Bass",
        "fr_CA": "Achigan à grande bouche",
        "es_MX": "Lobina negra"
      },
      "scientific_name": "Micropterus salmoides",
      "family": "Centrarchidae",
      "regulations": [
        {
          "jurisdiction": "Ontario",
          "waterbody": "All provincial waters",
          "season": {
            "open": "3rd Saturday in June",
            "close": "November 30"
          },
          "size_limit": {
            "min_cm": 30,
            "min_inches": 12,
            "slot_protected": null
          },
          "bag_limit": {
            "daily": 6,
            "possession": 6
          },
          "notes": "Catch-and-release only during closed season",
          "last_updated": "2026-01-15",
          "source": "https://www.ontario.ca/fishing-regulations"
        },
        {
          "jurisdiction": "Wisconsin",
          "waterbody": "Inland waters",
          "season": {
            "open": "First Saturday in May",
            "close": "Open year-round"
          },
          "size_limit": {
            "min_inches": 14
          },
          "bag_limit": {
            "daily": 5
          },
          "last_updated": "2026-02-01"
        }
      ]
    }
  },
  "jurisdictions": {
    "Ontario": {
      "country": "Canada",
      "province": "ON",
      "coordinates": {
        "lat_min": 41.7,
        "lat_max": 56.9,
        "lon_min": -95.2,
        "lon_max": -74.3
      }
    }
  }
}
```

### Data Sources

**North America:**
- Ontario: https://www.ontario.ca/page/fishing
- US states: Each state's DNR/Fish & Wildlife website
- API available: Some states offer JSON APIs

**Europe:**
- UK: https://www.gov.uk/freshwater-rod-fishing-rules
- EU countries: Varies by country

**Initial Focus:** US + Canada (easier to maintain)

**Update Frequency:**
- Manual review: Quarterly
- API sync (if available): Weekly
- User reports: Real-time (flagged for review)

**Disclaimer (CRITICAL):**
```
⚠️ FISHING REGULATIONS ADVISORY
This information is provided for guidance only and may not be current.
Always verify regulations with local authorities before fishing.
Regulations updated: [DATE]
Source: [JURISDICTION WEBSITE]
d3kOS is not responsible for regulatory violations.
```

### Database Size

- 1000 species × 20 jurisdictions average × 500 bytes = 10MB
- Full worldwide: ~500MB (including translations)

---

## Implementation Timeline

### Week 1: Dataset Preparation
- Download iNaturalist data for 200 species
- Organize into train/val/test splits
- Data augmentation pipeline
- Quality control (remove bad images)

### Week 2: Phase 1 Model Training
- Train EfficientNet-B0 on 200 species
- Export to ONNX format
- Deploy to Pi, test inference speed
- Achieve 80%+ accuracy on test set

### Week 3: Integration & Testing
- Integrate with existing fish detector
- GPS-based region detection
- Confidence thresholds tuning
- End-to-end testing with camera

### Week 4: Expand to 500 Species
- Download additional datasets
- Train EfficientNet-B1
- Regional model creation
- Performance testing

### Week 5: Regulations Database
- Scrape US + Canada regulations
- Build JSON database
- GPS → jurisdiction lookup
- API integration

### Week 6: Full Deployment
- Train final 1000-species model
- Deploy all regional models
- Complete testing
- User documentation

**Total Time:** 6 weeks (part-time work)
**GPU Time:** ~150 hours training
**Storage Used:** ~15GB (10GB dataset + 5GB models)

---

## Limitations & Disclaimers

### Technical Limitations

1. **Accuracy:** 70-75% for 1000 species (not 95%+)
2. **Coverage:** 1000 species covers ~80-90% of recreational catches
3. **Rare species:** Will be identified as "unknown"
4. **Look-alikes:** May misidentify similar species
5. **Photo quality:** Requires good lighting, clear view of fish
6. **Inference time:** 8-14 seconds total (not instant)

### Legal Disclaimers

**MUST display on every identification:**

```
═══════════════════════════════════════════════════
  ⚠️  SPECIES IDENTIFICATION DISCLAIMER  ⚠️
═══════════════════════════════════════════════════

This identification is provided by AI and may be
INCORRECT. Do NOT rely solely on this identification
for regulatory compliance.

Confidence: 78%
Alternative: Northern Pike (12% probability)

When in doubt, release the fish or consult a local
fishing expert before keeping.

═══════════════════════════════════════════════════
  ⚠️  FISHING REGULATIONS DISCLAIMER  ⚠️
═══════════════════════════════════════════════════

Regulations shown are for GUIDANCE ONLY and may be
outdated or incorrect. ALWAYS verify with local
authorities before keeping fish.

Last updated: February 15, 2026
Source: Ontario Ministry of Natural Resources

d3kOS is NOT responsible for regulatory violations
resulting from use of this information.

═══════════════════════════════════════════════════
```

### User Agreement

Before enabling fish ID features, user must agree:

```
I understand that:
- AI species identification may be incorrect
- Fishing regulations shown may be outdated
- I am responsible for verifying all information
- I will not hold d3kOS liable for misidentification
- I will release fish if uncertain about species/legality
- This tool is for ASSISTANCE, not legal compliance
```

---

## Success Metrics

**Phase 1 (200 species):**
- ✅ 80%+ accuracy on test set
- ✅ <10s total identification time
- ✅ Works offline
- ✅ User satisfaction: "It correctly ID'd my bass!"

**Phase 2 (500 species):**
- ✅ 75%+ accuracy
- ✅ Regional models deployed
- ✅ GPS-based model switching works

**Phase 3 (1000 species):**
- ✅ 70%+ accuracy
- ✅ Worldwide coverage
- ✅ Regulations database (US + Canada)
- ✅ Full production deployment

**User Feedback:**
- "Close enough to be useful"
- "Caught a fish I'd never seen, app said Walleye, local confirmed it!"
- "Helped me avoid keeping undersize fish"

---

## Next Steps After SD Card Upgrade

1. **Verify 128GB card installed:** `df -h` shows ~119GB total
2. **Install training dependencies:**
   ```bash
   pip3 install torch torchvision pillow pyinaturalist onnx onnxruntime
   ```
3. **Download Phase 1 dataset:** 200 species (2-4 hours)
4. **Train Phase 1 model:** EfficientNet-B0 (12-24 hours GPU time)
5. **Deploy to Pi:** Test inference speed and accuracy
6. **Iterate:** Expand to 500, then 1000 species

---

**Ready to start?** Confirm 128GB SD card installed and verified, then I'll begin dataset download.
