# Voice Query Speed Fix — 7.6s to 0.9s

**Date:** 2026-03-09
**Status:** RESOLVED — confirmed 0.9s response time
**Problem:** Voice queries to Helm took 7.6 seconds from end of speech to spoken response.

---

## Root Cause (two issues)

### 1. Eager PDF Import
`pdf_processor.py` was imported at module load time in `query_handler.py`. Loading the PDF processor (which initialises heavy dependencies including pdfminer/pdfplumber) on every startup added ~3s to first-query latency.

**Fix:** Changed to lazy import — `pdf_processor` is only imported when a query actually needs document retrieval.

```python
# Before (at top of query_handler.py)
import pdf_processor

# After (inside the function that needs it)
def handle_rag_query(self, query):
    import pdf_processor  # lazy — only loads when needed
    ...
```

### 2. Serial Signal K Fetches
`signalk_client.py` was fetching each data point (RPM, speed, heading, temperature, etc.) as separate HTTP requests to the Signal K API. With ~8 data points, this was 8 × ~400ms = 3.2s of sequential network calls.

**Fix:** Single bulk fetch to the Signal K vessels self endpoint, then extract all values from the response JSON.

```python
# Before: 8 separate calls
rpm = fetch_signalk('/vessels/self/propulsion/engine/revolutions')
speed = fetch_signalk('/vessels/self/navigation/speedOverGround')
# ... etc

# After: one call, extract all
data = fetch_signalk('/vessels/self')
rpm = data['propulsion']['engine']['revolutions']['value']
speed = data['navigation']['speedOverGround']['value']
```

---

## Result

| Metric | Before | After |
|--------|--------|-------|
| Voice query response time | 7.6s | 0.9s |

---

## Files Modified

| File | Location on Pi |
|------|---------------|
| `query_handler.py` | `/opt/d3kos/services/ai/` |
| `signalk_client.py` | `/opt/d3kos/services/ai/` |
