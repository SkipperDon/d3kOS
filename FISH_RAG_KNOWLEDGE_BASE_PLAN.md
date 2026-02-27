# Fish Species RAG Knowledge Base - Implementation Plan

**Date:** 2026-02-27
**Approach:** RAG (Retrieval Augmented Generation) with Ollama + Phi-3.5
**Status:** Prepared - Awaiting Session 2 completion

---

## Executive Summary

**NEW APPROACH:** Using RAG instead of traditional model training for fish species identification.

**Why RAG?**
- Requires 97% less data (1,600 images vs 50,000)
- No GPU training needed (hours vs days)
- Explainable AI (tells you WHY)
- Easier to update (add text, not retrain)
- Works offline (Phi-3.5 on Pi)

---

## RAG Architecture

### Traditional Approach (What we were doing):
```
Camera → YOLOv8 detection → EfficientNet species classification → Species name
```
**Problem:** Needs 10,000-50,000 training images, rigid, no explanation

### RAG Approach (What we're building):
```
Camera → YOLOv8 detection → Feature extraction → RAG query → Phi-3.5 reasoning → Species + explanation
```
**Benefit:** Needs 1,600 images, flexible, explains reasoning

---

## System Components

### Session 2 (Parallel - In Progress):
- ✅ Ollama installed and running
- ✅ Phi-3.5 model loaded (2.2 GB)
- ⏳ PDF learning system (RAG pipeline)
- ⏳ Vector database setup
- ⏳ Embedding generation

### Session 1 (This Session - Ready):
- ✅ RAG Knowledge Base Builder created
- ✅ Script transferred to Pi
- ✅ Dependencies verified
- ⏳ Waiting for signal to start download

---

## Data Collection Plan

### What Will Be Downloaded:

**1. Ontario Freshwater Fishes Database (161 species)**
- Source: https://www.ontariofishes.ca/
- Text: Life history, visual characteristics, habitat, distribution
- Photos: 1-2 per species page
- Format: JSON + JPEG

**2. PDF Visual Guides (3 documents)**
- Salmon/Trout ID guide (SUNY Sea Grant)
- Ontario Fishing Regulations (Ontario MNR)
- Learn to Fish guide (Ontario MNR)
- Purpose: Extract visual identification keys

**3. Reference Images (5-10 per species)**
- Total: ~1,600 images
- Source: Ontario Fishes database photos
- Size: 200-400 MB total

### Output Structure:
```
/opt/d3kos/datasets/fish-rag/
├── species_descriptions/           161 JSON files
├── reference_images/               1,600+ photos
├── visual_guides/                  3 PDFs
└── knowledge_base/
    ├── fish_rag_corpus.json        Complete database
    ├── species_embeddings_prep.json Ready for vector DB
    └── quick_reference.json        Top 30 species
```

---

## RAG Corpus Format

### Species Entry Example:
```json
{
  "species_id": "001",
  "common_name": "Yellow Perch",
  "scientific_name": "Perca flavescens",
  "family": "Percidae",
  "description": "Native fish, dominant species in Lake Simcoe...",
  "visual_characteristics": "Yellow to brassy green body with 6-9 dark vertical bars, orange pelvic fins...",
  "habitat": "Shallow weedy areas, prefers cool water...",
  "distribution": "Great Lakes, Lake Simcoe, all Ontario waters",
  "size_range": "15-30 cm, 14+ inch jumbos in Lake Simcoe",
  "reference_images": [
    "/opt/d3kos/datasets/fish-rag/reference_images/001_yellow_perch_1.jpg",
    "/opt/d3kos/datasets/fish-rag/reference_images/001_yellow_perch_2.jpg"
  ]
}
```

### For RAG Embedding:
```
Species: Yellow Perch (Perca flavescens)
Family: Percidae

Description: Native fish, dominant species in Lake Simcoe...

Visual Characteristics: Yellow to brassy green body with 6-9 dark vertical bars, orange pelvic fins...

Habitat: Shallow weedy areas, prefers cool water...
```

---

## Integration Workflow

### Step 1: Data Collection (Session 1)
```bash
python3 ~/build_fish_rag_knowledge_base.py
# Downloads: 2-4 hours
# Output: 161 species + 1,600 images + 3 PDFs
```

### Step 2: Vector Database (Session 2)
```python
# Load corpus
corpus = json.load('fish_rag_corpus.json')

# Generate embeddings
for species in corpus['species']:
    embedding = ollama.embeddings(species['text_for_embedding'])
    vector_db.add(embedding, metadata=species)
```

### Step 3: RAG Query (Both Sessions)
```python
# Fish detected
features = extract_features(image)  # "yellow body, vertical bars, orange fins"

# Query RAG
query = f"What fish has {features}?"
candidates = vector_db.query(query, top_k=5)

# Phi-3.5 reasoning
prompt = f"""
Given these fish descriptions:
{candidates}

And these visual features: {features}

Which species is most likely and why?
"""

response = ollama.generate(model='phi3.5', prompt=prompt)
# Output: "Yellow Perch - vertical bars and yellow coloring are distinctive..."
```

---

## Priority Species (Top 30)

### Lake Simcoe:
1. Yellow Perch (dominant - 94% winter catch)
2. Lake Trout (20+ lbs)
3. Smallmouth Bass (5+ lbs avg)
4. Largemouth Bass
5. Northern Pike (40+ inches)
6. Lake Whitefish (stocked annually)
7. Burbot (winter fishery)
8. Bluegill
9. Black Crappie

### Lake Erie:
10. Walleye (trophy fishery)
11. Steelhead (tributaries)
12. Channel Catfish

### Lake Huron:
13. Chinook Salmon (20+ lbs)
14. Coho Salmon
15. Brown Trout

### Other Important:
16-30. Brook Trout, Rainbow Trout, Rock Bass, White Bass, Pumpkinseed, Green Sunfish, Muskellunge, Flathead Catfish, Freshwater Drum, Lake Sturgeon, Longnose Gar

---

## Advantages Over Traditional Training

| Aspect | Traditional Training | RAG Approach |
|--------|---------------------|--------------|
| **Data needed** | 10,000-50,000 images | 1,600 images + text |
| **Training time** | 12-50 hours GPU | None (no training) |
| **Model size** | 18-100 MB | 2.2 GB (Phi-3.5) |
| **Accuracy** | 80-90% | 70-85% (similar) |
| **Explainable** | ❌ No | ✅ Yes |
| **Update** | ❌ Retrain | ✅ Add text |
| **Edge cases** | ❌ Fails silently | ✅ Reasons through |
| **Offline** | ✅ Yes | ✅ Yes |

---

## Storage Requirements

### On Raspberry Pi:
- Current: 2.2 GB free (85% used)
- Phi-3.5 model: 2.2 GB (already installed)
- RAG corpus: ~500 MB (images + text + PDFs)
- Vector database: ~100 MB (embeddings)
- Total new: ~600 MB
- **Status:** ✅ Sufficient space

---

## Timeline

| Phase | Time | Status |
|-------|------|--------|
| Session 2: RAG pipeline | 2-3 hours | ⏳ In progress |
| Session 1: Data collection | 2-4 hours | ⏳ Ready to start |
| Integration testing | 1-2 hours | ⏳ Pending |
| Deployment | 30 min | ⏳ Pending |
| **Total** | **6-10 hours** | **In progress** |

---

## Success Criteria

### Knowledge Base Complete:
- [ ] 161 species descriptions scraped
- [ ] 1,600+ reference images downloaded
- [ ] 3 PDF guides downloaded
- [ ] RAG corpus JSON created
- [ ] Embeddings prep file ready

### RAG System Working:
- [ ] Vector database loaded
- [ ] Embeddings generated
- [ ] Query retrieval accurate
- [ ] Phi-3.5 reasoning quality good

### Fish Identification Working:
- [ ] Fish detection triggers RAG query
- [ ] Species returned with confidence
- [ ] Explanation provided
- [ ] Works offline
- [ ] Accurate for Lake Simcoe species

---

## Next Steps

### When Session 2 Signals Ready:

**1. Start Data Collection:**
```bash
ssh d3kos@192.168.1.237
python3 ~/build_fish_rag_knowledge_base.py
```

**2. Monitor Progress:**
```bash
tail -f /opt/d3kos/datasets/fish-rag/rag_builder.log
```

**3. Verify Output:**
```bash
ls /opt/d3kos/datasets/fish-rag/knowledge_base/
cat /opt/d3kos/datasets/fish-rag/knowledge_base/fish_rag_corpus.json | jq '.metadata'
```

**4. Coordinate with Session 2:**
- Session 2 loads corpus
- Session 2 generates embeddings
- Both sessions integrate and test

---

## Files

### Created:
- `/home/boatiq/Helm-OS/build_fish_rag_knowledge_base.py` (675 lines)
- `/home/boatiq/.claude/projects/-home-boatiq/memory/fish-rag-knowledge-base-session.md`
- `/home/boatiq/Helm-OS/FISH_RAG_KNOWLEDGE_BASE_PLAN.md` (this file)

### On Pi:
- `~/build_fish_rag_knowledge_base.py` (ready to execute)

---

## Coordination

**Session 1 (This):** Data collection (fish species text + photos)
**Session 2 (Parallel):** RAG implementation (Ollama + Phi-3.5 + vector DB)

**Communication:** User will signal when Session 2 ready for data

**Status:** ✅ PREPARED AND READY

---

**Last Updated:** 2026-02-27 09:40 AM
**Next Action:** Wait for user signal to proceed
