# Fish Detection & Species Identification — Architecture
**Version:** 1.1.0 | **Date:** 2026-03-21 | **Status:** Fish detection complete. Species ID via Gemini Vision — pending connection.

---

## What Is Done vs. What Is Not Done

| Component | Status | Notes |
|-----------|--------|-------|
| Fish detection (YOLOv8n) | ✓ Working | Detects fish-shaped objects in frame |
| NMS (duplicate box collapse) | ✓ Fixed 2026-03-21 | Was showing 11 boxes for 2 fish |
| Detection confidence display | ✓ Fixed 2026-03-21 | exp(log-softmax) fix — was showing -34.2% |
| Auto-capture on detection | ✓ Working | Saves JPEG to `/home/d3kos/camera-recordings/captures/` |
| Ontario species RAG (PDFs) | ✓ Scripts built | Voice AI text queries only — NOT visual ID |
| Gemini API key on Pi | ✓ Installed | At `/opt/d3kos/services/gemini-nav/config/gemini.env` |
| ONNX species classifier (EfficientNet-483) | ⚠ Wrong model | Trained on Australian/Indo-Pacific fish. Not Ontario. |
| Gemini Vision species ID from capture | ✗ Not built | **This is the completion step** — send JPEG to Gemini Vision |
| Ontario RAG scripts run on Pi | ✗ Not confirmed | `create_fish_species_pdfs.py` + `add_fish_to_rag.py` — not logged as run |

---

## Architecture: What Was Built

```
Camera frame (Helm camera — faces starboard for fish brought aboard)
         │
         ▼
┌─────────────────────────────────────────────┐
│  Stage 1: Fish Detection (WORKING)          │
│  Model: fish_detector.onnx (YOLOv8n)        │
│  Confidence threshold: 0.45                 │
│  NMS: IoU 0.4 — collapses duplicate boxes   │
│  Output: fish count + bounding boxes        │
└──────────────┬──────────────────────────────┘
               │ fish detected
               ▼
┌─────────────────────────────────────────────┐
│  Auto-capture                               │
│  Saves JPEG: /home/d3kos/camera-recordings/ │
│  captures/catch_YYYYMMDD_HHMMSS.jpg         │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  Stage 2: Species ID via EfficientNet-483   │
│  STATUS: WRONG MODEL                        │
│  Trained on: Australian / Indo-Pacific fish │
│  Will NOT correctly identify Ontario fish   │
│  (walleye, pike, perch, bass NOT in set)    │
└──────────────┬──────────────────────────────┘
               │
               ▼
     ┌─────────────────────┐
     │  Marine Vision UI   │
     │  Shows: fish count  │
     │  Shows: classifier  │
     │  result (wrong for  │
     │  Ontario species)   │
     └─────────────────────┘

Ontario Fish RAG (SEPARATE PATH — voice AI only):
  User asks: "What does a walleye look like?"
         │
         ▼
  d3kOS Voice Assistant → query_handler.py → RAG → answer
  (text responses only — does NOT look at camera images)
```

---

## The Completion Path: Gemini Vision (No Model Training Required)

The Gemini API is **already configured on the Pi** at:
`/opt/d3kos/services/gemini-nav/config/gemini.env` (holds `GEMINI_API_KEY`)

Gemini 2.5 Flash supports multimodal input (text + image). It can correctly identify walleye, pike, perch, bass, and other Ontario freshwater species from a photograph with no training required.

### Proposed completion (awaiting authorization):

**Step 1:** Add `/detect/identify` endpoint to `fish_detector.py`
- Accepts a capture JPEG (by capture ID or direct upload)
- Reads Gemini API key from env
- Sends JPEG + Ontario-specific prompt to `gemini-2.5-flash` vision API
- Returns: species common name, scientific name, key visual features, confidence statement

**Step 2:** Call `/detect/identify` automatically when a capture is saved
- fish_detector.py calls Gemini Vision after each auto-capture
- Stores Gemini species result in `captures.db` (new `gemini_species` column)

**Step 3:** Display in Marine Vision UI
- Detection result panel shows Gemini species name (not ONNX classifier)
- Shows confidence statement from Gemini

### Gemini prompt for Ontario fishing:
```
You are an AI fishing assistant for Ontario, Canada. Identify the fish species
in this photo. Provide:
1. Common name (as used in Ontario)
2. Scientific name
3. Your confidence: high / medium / low
4. Key visual features you see that support your identification
5. Whether this fish has Ontario size or bag limit rules you can note

If you cannot identify the species with confidence, say so honestly.
```

This approach:
- Uses existing Gemini API key (no new accounts, no cost setup)
- Works for Ontario freshwater fish (walleye, pike, perch, bass, trout, etc.)
- More accurate than any specialized ONNX model for uncommon species
- Provides regulation context in the same response

---

## Ontario Species RAG — What It Does and Does Not Do

### What the RAG IS for (voice AI text queries)
The RAG knowledge base allows the voice assistant to answer:
- "What does a walleye look like?"
- "What's the size limit for walleye on Lake Erie?"
- "How do I tell a sauger from a walleye?"
- "What habitat does northern pike prefer?"

The RAG is a **text knowledge base** queried by the voice assistant. It does NOT look at camera images.

### Ontario species PDF scripts (built — run status unconfirmed on Pi)

**`create_fish_species_pdfs.py`** (repo root)
Creates 22 Ontario / Great Lakes species PDFs using reportlab:

| Species | Scientific Name |
|---------|----------------|
| Yellow Perch | Perca flavescens |
| Walleye | Sander vitreus |
| Largemouth Bass | Micropterus salmoides |
| Smallmouth Bass | Micropterus dolomieu |
| Northern Pike | Esox lucius |
| Lake Trout | Salvelinus namaycush |
| Muskellunge | Esox masquinongy |
| Lake Whitefish | Coregonus clupeaformis |
| Bluegill | Lepomis macrochirus |
| Black Crappie | Pomoxis nigromaculatus |
| Burbot | Lota lota |
| Chinook Salmon | Oncorhynchus tshawytscha |
| Coho Salmon | Oncorhynchus kisutch |
| Rainbow Trout / Steelhead | Oncorhynchus mykiss |
| Brown Trout | Salmo trutta |
| Brook Trout | Salvelinus fontinalis |
| Channel Catfish | Ictalurus punctatus |
| Rock Bass | Ambloplites rupestris |
| Pumpkinseed | Lepomis gibbosus |
| White Bass | Morone chrysops |
| Sauger | Sander canadensis |

Each PDF contains: description, visual characteristics, habitat, size range, distribution, Ontario fishing regulations.

**`add_fish_to_rag.py`** (repo root)
Adds those PDFs to the Pi's document RAG service via `PDFProcessor`.

**To run on Pi (one-time setup — if not already done):**
```bash
cd /home/d3kos
python3 /path/to/create_fish_species_pdfs.py
python3 /path/to/add_fish_to_rag.py
```

**`build_fish_rag_knowledge_base.py`** (repo root)
Scrapes `ontariofishes.ca` + downloads Ontario Fishing Regulations PDF.
Builds full corpus at `/opt/d3kos/datasets/fish-rag/knowledge_base/`.

---

## EfficientNet-483 — Why It Is Wrong

The ONNX classifier `fish_classifier_483species_best.onnx` was trained on an **Australian and Indo-Pacific reef fish dataset**. The first entries in the species list confirm this:
- `acanthaluteres_brownii` — Australian toadstool filefish
- `acanthopagrus_australis` — Yellowfin Bream (Australia)
- `achoerodus_gouldii` — Blue Groper (Australia)

Ontario freshwater species (walleye, pike, perch, bass, Lake Trout) are not in this training set. The model will always return a wrong species name for Ontario fish.

The model is NOT discarded — it is useful as a "fish-vs-not-fish" signal (Stage 1 result is reliable). The species classification output from Stage 2 should be suppressed until Gemini Vision is connected.

**If a future Ontario freshwater classifier is desired (optional):**
- Training plan: `fish_species_phase1.json` (50 North American freshwater species, iNaturalist taxon IDs)
- Training script: `train_fish_model_483species.py`
- Data download: `download_fish_datasets.py`
- Runs on workstation GPU (192.168.1.36) — NOT the Pi
- This is a Phase 2 improvement, not required for working species ID

---

## File Index

| File | Location | Purpose | Status |
|------|----------|---------|--------|
| `fish_detector.py` | `deployment/features/camera-overhaul/pi_source/` → Pi `/opt/d3kos/services/marine-vision/` | Flask :8086 — detect + classify | ✓ Deployed |
| `fish_detector.onnx` | Pi `/opt/d3kos/models/marine-vision/` | YOLOv8n detection | ✓ Working |
| `fish_classifier_483species_best.onnx` | Pi `/opt/d3kos/models/fish-species/` | EfficientNet species (wrong dataset) | ⚠ Wrong species |
| `species_list.json` | Pi `/opt/d3kos/models/fish-species/` | 483-class name map | ⚠ Australian fish |
| `create_fish_species_pdfs.py` | `Helm-OS/` root | Build Ontario species PDFs | ✓ Script ready — run on Pi |
| `add_fish_to_rag.py` | `Helm-OS/` root | Ingest Ontario PDFs into RAG | ✓ Script ready — run on Pi |
| `build_fish_rag_knowledge_base.py` | `Helm-OS/` root | Scrape + build full Ontario corpus | ✓ Script ready — optional |
| `fish_species_phase1.json` | `Helm-OS/` root | 200-species iNaturalist training plan | 📋 Phase 2 optional |
| `train_fish_model_483species.py` | `Helm-OS/` root | EfficientNet training script | 📋 Phase 2 optional |
| `captures.db` | Pi `/opt/d3kos/data/marine-vision/` | Detection + capture history | ✓ Active |
| Species PDFs | Pi `/opt/d3kos/datasets/fish-rag/species_pdfs/` | 22 Ontario species PDFs | ✗ Run create script |
| `gemini.env` | Pi `/opt/d3kos/services/gemini-nav/config/` | Gemini API key | ✓ Installed |

---

## Open Items

| # | Item | Priority | Path |
|---|------|----------|------|
| 1 | Connect Gemini Vision to fish captures for species ID | **High** | Add `/detect/identify` to fish_detector.py — awaiting authorization |
| 2 | Run Ontario species RAG scripts on Pi | **Medium** | Run `create_fish_species_pdfs.py` then `add_fish_to_rag.py` on Pi |
| 3 | Suppress ONNX species name in Marine Vision UI (show Gemini result instead) | Completes with item 1 |
| 4 | Phase 2 (optional): Train freshwater ONNX model | **Low** | Workstation GPU — not blocking anything |

---

*d3kOS Fish Detection Architecture — `deployment/docs/FISH_DETECTION_ARCHITECTURE.md`*
*See also: `deployment/docs/MARINE_VISION_CAMERA_OVERHAUL.md`*
