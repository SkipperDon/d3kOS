# Fish Detection & Species Identification — Architecture
**Version:** 1.0.0 | **Date:** 2026-03-21 | **Status:** Active — Ontario freshwater model pending

---

## Overview

The d3kOS fish detection system has two parallel tracks:

1. **Real-time video detection** — ONNX models running on the Pi (port :8086)
2. **Species knowledge base** — RAG/PDF data in the d3kOS document service (voice AI)

These two tracks are currently independent. The ONNX classifier detects fish and attempts species ID from video frames. The RAG knowledge base contains detailed Ontario freshwater fish information that the voice AI assistant can query.

---

## Architecture Diagram

```
Camera frame (Helm camera, starboard-facing)
         │
         ▼
┌─────────────────────────────────────┐
│  Stage 1: Fish Detection            │
│  Model: fish_detector.onnx          │
│  Type: YOLOv8n (single class)       │
│  Training: 21,719 labeled images    │
│  Output: bounding boxes + count     │
│  NMS: IoU threshold 0.4             │
│  Confidence threshold: 0.45         │
└──────────────┬──────────────────────┘
               │ (if fish detected)
               ▼
┌─────────────────────────────────────┐
│  Stage 2: Species Classifier        │
│  Model: fish_classifier_483         │
│         species_best.onnx           │
│  Type: EfficientNet (483 classes)   │
│  Training: Australian/Indo-Pacific  │
│           reef fish dataset         │
│  Output: species name + probability │
│  NOTE: Wrong model for Ontario use  │
│  ⚠ Walleye, pike, perch NOT in set │
└──────────────┬──────────────────────┘
               │
               ▼
        ┌──────────────┐
        │  Marine Vision│
        │  UI display   │
        │  + Note to use│
        │  voice AI for │
        │  Ontario fish │
        └──────────────┘

Voice AI (separate path):
  User asks: "What does a walleye look like?"
         │
         ▼
  ┌──────────────────────────────────┐
  │  RAG Knowledge Base (ChromaDB)   │
  │  Ontario fish species PDFs       │
  │  22 species × full detail:       │
  │  • Visual characteristics        │
  │  • Size range + weight           │
  │  • Habitat + distribution        │
  │  • Ontario fishing regulations   │
  └──────────────────────────────────┘
```

---

## ONNX Detection Models

### Stage 1: YOLOv8n Fish Detector
- **File:** `/opt/d3kos/models/marine-vision/fish_detector.onnx`
- **Input:** 640×640 grayscale (converted to 3-channel)
- **Output:** Bounding boxes with fish confidence
- **Use:** Detect fish in frame, count fish held up for identification
- **Status:** ✓ Working — correctly fires on fish-shaped objects

### Stage 2: EfficientNet-483 Species Classifier
- **File:** `/opt/d3kos/models/fish-species/fish_classifier_483species_best.onnx`
- **Species list:** `/opt/d3kos/models/fish-species/species_list.json`
- **Input:** Full frame (not cropped bounding box) at model input size
- **Output:** 483-class log-softmax (convert with `exp()` for probability)
- **Training dataset:** Primarily Australian and Indo-Pacific reef species
  - Examples: `acanthaluteres_brownii` (Australian filefish), `acanthopagrus_australis` (Yellowfin Bream), `achoerodus_gouldii` (Blue Groper)
- **Known limitation:** Ontario freshwater species (walleye, pike, perch, bass) are NOT in the 483-species training set
- **Status:** ⚠ Mismatched to use case — displays best-guess marine species

#### Confidence display fix (applied 2026-03-21)
The model outputs **log-softmax** values, not probabilities. Raw values are always negative.
- **Wrong:** `species_confidence * 100` → shows `-34.2%`
- **Correct:** `exp(species_confidence) * 100` → shows `71.3%`
- Fix applied in `classify_species()`: `probabilities = np.exp(log_probs)` before computing top-3

---

## RAG Knowledge Base — Ontario Fish Species

### What was built
Two scripts build and populate the Ontario fish species knowledge base:

**Script 1: `create_fish_species_pdfs.py`** (project root)
- Creates individual PDF files for 22 Great Lakes / Lake Simcoe fish species
- Uses `reportlab` to generate structured PDFs
- Output: `/opt/d3kos/datasets/fish-rag/species_pdfs/`
- Each PDF contains: description, visual characteristics, habitat, size range, distribution, Ontario fishing regulations

**Species covered (22 total):**
| Species | Scientific Name | Use Case |
|---------|----------------|----------|
| Yellow Perch | Perca flavescens | Ice fishing, summer |
| Walleye | Sander vitreus | Lake Erie trophy fishery |
| Largemouth Bass | Micropterus salmoides | Shallow weedy areas |
| Smallmouth Bass | Micropterus dolomieu | Rocky areas, Lake Simcoe |
| Northern Pike | Esox lucius | Ambush predator |
| Lake Trout | Salvelinus namaycush | Deep cold water |
| Muskellunge | Esox masquinongy | Trophy, Georgian Bay |
| Lake Whitefish | Coregonus clupeaformis | Deep, stocked annually |
| Bluegill | Lepomis macrochirus | Panfish |
| Black Crappie | Pomoxis nigromaculatus | Schools, ice fishing |
| Burbot | Lota lota | Winter fishery |
| Chinook Salmon | Oncorhynchus tshawytscha | Great Lakes stocked |
| Coho Salmon | Oncorhynchus kisutch | Great Lakes stocked |
| Rainbow Trout / Steelhead | Oncorhynchus mykiss | Lakes + tributaries |
| Brown Trout | Salmo trutta | Cool streams |
| Brook Trout | Salvelinus fontinalis | Cold headwater streams |
| Channel Catfish | Ictalurus punctatus | Erie, Huron, Ontario |
| Rock Bass | Ambloplites rupestris | Rocky areas |
| Pumpkinseed | Lepomis gibbosus | Shallow weedy areas |
| White Bass | Morone chrysops | Open water, schooling |
| Sauger | Sander canadensis | Deep, similar to walleye |

**Script 2: `add_fish_to_rag.py`** (project root)
- Reads PDFs from `/opt/d3kos/datasets/fish-rag/species_pdfs/`
- Adds each PDF to the Pi's RAG document service via `PDFProcessor`
- Pi path: `/opt/d3kos/services/documents/pdf_processor.py`
- Result: Species data ingested as chunks into ChromaDB/vector store

**Script 3: `build_fish_rag_knowledge_base.py`** (project root)
- Scrapes `ontariofishes.ca` for full Ontario species list
- Downloads Ontario Fishing Regulations PDF (`files.ontario.ca`)
- Downloads visual identification guides
- Builds complete RAG corpus at `/opt/d3kos/datasets/fish-rag/knowledge_base/`

### How to run (Pi — one-time setup)
```bash
# Step 1: Create PDFs
cd /home/d3kos
python3 /home/d3kos/Helm-OS/create_fish_species_pdfs.py

# Step 2: Add to RAG
python3 /home/d3kos/Helm-OS/add_fish_to_rag.py

# Step 3: (Optional) build full corpus from Ontario Fishes DB
python3 /home/d3kos/Helm-OS/build_fish_rag_knowledge_base.py
```

### How the RAG connects to fish detection (current)
The RAG is queried via the **voice AI assistant** (d3kos-voice-assistant.service).

When fish are detected on the Helm camera:
1. Marine Vision UI shows detection count + classifier guess
2. Classifier note reminds user to ask voice AI for Ontario species ID
3. User says: "d3kOS, what fish did I catch?" or "d3kOS, is this a walleye?"
4. Voice AI routes query to RAG → returns visual ID tips, size, regulations

Example RAG queries that work:
- "What does a walleye look like?" → visual characteristics from PDF
- "What's the size limit for walleye on Lake Erie?" → Ontario regulations
- "How do I tell the difference between a sauger and a walleye?" → comparison data

---

## Phase 2: Ontario-Trained Species Model (Planned)

### What was planned (not built yet)
`fish_species_phase1.json` defines a 200-species training dataset:
- **50 North American freshwater species** (includes walleye, pike, perch, bass, trout)
- 40 North American saltwater species
- 40 European freshwater species
- 40 Asia-Pacific species
- 30 global saltwater species

Source: iNaturalist taxon IDs, 100 images per species, research-grade observations

Training script: `train_fish_model_483species.py` (existing — needs re-run with freshwater dataset)

### To build the Ontario freshwater model
1. Run `download_fish_datasets.py` — downloads images from iNaturalist by taxon ID
2. Focus on `north_america_freshwater` region in `fish_species_phase1.json` (50 species)
3. Re-train EfficientNet using `train_fish_model_483species.py` on freshwater dataset
4. Replace `/opt/d3kos/models/fish-species/fish_classifier_483species_best.onnx`
5. Replace `/opt/d3kos/models/fish-species/species_list.json`

This is a **GPU training task** — run on the workstation (192.168.1.36), not the Pi.

---

## File Index

| File | Location | Purpose |
|------|----------|---------|
| `fish_detector.py` | `deployment/features/camera-overhaul/pi_source/` | Flask service :8086 — detect + classify |
| `fish_detector.onnx` | `/opt/d3kos/models/marine-vision/` (Pi) | YOLOv8n single-class detection |
| `fish_classifier_483species_best.onnx` | `/opt/d3kos/models/fish-species/` (Pi) | EfficientNet species classifier (marine) |
| `species_list.json` | `/opt/d3kos/models/fish-species/` (Pi) | 483-class species name map |
| `create_fish_species_pdfs.py` | `Helm-OS/` root | Build Ontario species PDFs |
| `add_fish_to_rag.py` | `Helm-OS/` root | Ingest Ontario PDFs into RAG |
| `build_fish_rag_knowledge_base.py` | `Helm-OS/` root | Scrape + build full Ontario corpus |
| `fish_species_phase1.json` | `Helm-OS/` root | 200-species training plan (Phase 2) |
| `train_fish_model_483species.py` | `Helm-OS/` root | Training script (workstation GPU) |
| `captures.db` | `/opt/d3kos/data/marine-vision/` (Pi) | Detection + capture history |
| Species PDFs | `/opt/d3kos/datasets/fish-rag/species_pdfs/` (Pi) | 22 Ontario species PDFs |

---

## Known Issues and Gaps

| # | Issue | Impact | Fix |
|---|-------|--------|-----|
| 1 | EfficientNet-483 trained on marine species | Species name is wrong for Ontario fish | Phase 2: train freshwater model |
| 2 | Stage 2 classifies full frame, not cropped fish | Less accurate even for in-set species | Crop to bounding box before classify |
| 3 | RAG and ONNX classifier not connected | UI shows wrong species; voice AI has right data | Phase 2: Gemini Vision API for species ID from captured frame |
| 4 | Ontario species PDFs may not be ingested on Pi | RAG won't answer Ontario fish questions | Run add_fish_to_rag.py on Pi |

---

*d3kOS Fish Detection Architecture — maintained in `deployment/docs/FISH_DETECTION_ARCHITECTURE.md`*
*See also: `deployment/docs/MARINE_VISION_CAMERA_OVERHAUL.md` for camera slot architecture*
