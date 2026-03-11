# Plan: Remove OpenRouter, Use Ollama (Free System)

**Date:** February 27, 2026
**Goal:** Make d3kOS completely free - no paid API services
**Solution:** Use local Ollama with phi3.5 model instead of OpenRouter

---

## Current Status

### ✅ Already Installed:
- **Ollama Service:** Running (port 11434)
- **Model:** phi3.5:latest (2.2 GB)
- **Embeddings:** nomic-embed-text (274 MB) - for RAG
- **Status:** Active and working

### ❌ Current Problem:
- AI Assistant configured to use OpenRouter (paid service)
- OpenRouter out of credits ($0.18 used, needs payment)
- System NOT free as designed

---

## Implementation Plan

### Phase 1: Update AI Configuration (5 minutes)

**File:** `/opt/d3kos/config/ai-config.json`

**Current:**
```json
{
  "active_provider": "openrouter",
  "providers": {
    "openrouter": {
      "enabled": true,
      ...
    }
  }
}
```

**New:**
```json
{
  "active_provider": "ollama",
  "providers": {
    "ollama": {
      "enabled": true,
      "api_endpoint": "http://localhost:11434/api/chat",
      "default_model": "phi3.5:latest",
      "temperature": 0.7,
      "timeout": 60000
    },
    "openrouter": {
      "enabled": false,
      "api_key": "",
      "api_endpoint": "",
      "default_model": "",
      "max_tokens": 500,
      "temperature": 0.7,
      "timeout": 10000
    }
  },
  "fallback": {
    "provider": "rules",
    "model": "rule-based"
  },
  "routing": {
    "auto_select": true,
    "prefer_online": false,
    "internet_check_interval": 30000
  }
}
```

**Changes:**
- `active_provider`: "openrouter" → "ollama"
- Add `ollama` provider configuration
- Disable OpenRouter (`enabled: false`)
- Remove OpenRouter API key (security)
- Set `prefer_online: false` (use local AI)

---

### Phase 2: Modify Query Handler (30 minutes)

**File:** `/opt/d3kos/services/ai/query_handler.py`

**Add New Method:**
```python
def query_ollama(self, question, context, manual_context=None):
    """Query local Ollama API with optional manual context"""
    config = self.config["providers"]["ollama"]

    if not config.get("enabled", False):
        raise ValueError("Ollama provider not enabled")

    model = config["default_model"]

    # Get current boat status for real-time data
    boat_status = self.get_boat_status()
    status_text = f"""
Current Boat Status (Real-time Sensor Data):
- Engine RPM: {boat_status.get('rpm', 'N/A')}
- Oil Pressure: {boat_status.get('oil_pressure', 'N/A')} PSI
- Coolant Temperature: {boat_status.get('coolant_temp', 'N/A')}°F
- Fuel Level: {boat_status.get('fuel_level', 'N/A')}%
- Battery Voltage: {boat_status.get('battery_voltage', 'N/A')}V
- Speed: {boat_status.get('speed', 'N/A')} knots
- Heading: {boat_status.get('heading', 'N/A')}°
"""

    # Build system prompt with manual context if available
    system_prompt = f"""You are a marine assistant for d3kOS.

{status_text}

Context from boat knowledge base:
{context}
"""

    # Add manual context if found
    if manual_context:
        system_prompt += f"""
{manual_context}

IMPORTANT: The manual excerpts above contain specific information about this boat's systems.
When answering, prioritize information from the manuals over general knowledge.
Quote the manual when appropriate and cite the source document.
"""
    else:
        system_prompt += """
No specific manual information found for this question. Provide general marine guidance.
"""

    system_prompt += """
Provide concise, accurate answers based on this boat's specific configuration and current sensor readings."""

    # Ollama API format
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        "stream": False,
        "options": {
            "temperature": config["temperature"]
        }
    }

    req = urllib.request.Request(
        config["api_endpoint"],
        data=json.dumps(data).encode('utf-8'),
        headers={
            "Content-Type": "application/json"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=config["timeout"]/1000) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result["message"]["content"], model
    except Exception as e:
        raise Exception(f"Ollama API error: {str(e)}")
```

**Modify query() Method:**

Replace OpenRouter calls with Ollama:

```python
# OLD:
if provider == 'openrouter':
    answer, model = self.query_openrouter(question, context, manual_context)
    ai_used = 'openrouter'

# NEW:
if provider == 'ollama':
    answer, model = self.query_ollama(question, context, manual_context)
    ai_used = 'ollama'
elif provider == 'openrouter':
    # OpenRouter disabled - fallback to Ollama
    print("  ⚠ OpenRouter disabled, using Ollama instead", flush=True)
    answer, model = self.query_ollama(question, context, manual_context)
    ai_used = 'ollama'
```

**Update Provider Selection Logic:**

```python
# OLD:
if force_provider:
    provider = force_provider
else:
    # Auto-select: prefer OpenRouter if internet available
    if self.config["routing"]["prefer_online"] and self.check_internet():
        provider = "openrouter"
    else:
        provider = "onboard"

# NEW:
if force_provider:
    provider = force_provider
else:
    # Auto-select: use Ollama for complex queries
    provider = "ollama"
```

---

### Phase 3: Test Ollama Integration (15 minutes)

**Test 1: Simple Query (should use rules)**
```bash
python3 /opt/d3kos/services/ai/query_handler.py "What is the RPM?"
```
Expected: Rule-based response (0.17s)

**Test 2: Procedure Query (should use Ollama + RAG)**
```bash
python3 /opt/d3kos/services/ai/query_handler.py "What is the oil change procedure?"
```
Expected:
- Searches RAG: ✓ Found 3 relevant chunks
- Provider: ollama
- Model: phi3.5:latest
- Manual Used: True
- Response Time: 30-60 seconds
- Answer: Complete oil change procedure from manual

**Test 3: Complex Query (should use Ollama)**
```bash
python3 /opt/d3kos/services/ai/query_handler.py "Why is my engine overheating?"
```
Expected:
- Provider: ollama
- Model: phi3.5:latest
- Response Time: 20-40 seconds
- Answer: Boat-specific troubleshooting advice

---

### Phase 4: Update Configuration Files (10 minutes)

**1. Update ai-config.json:**
```bash
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237 'cat > /tmp/new-ai-config.json << EOF
{
  "active_provider": "ollama",
  "providers": {
    "ollama": {
      "enabled": true,
      "api_endpoint": "http://localhost:11434/api/chat",
      "default_model": "phi3.5:latest",
      "temperature": 0.7,
      "timeout": 60000
    },
    "openrouter": {
      "enabled": false,
      "api_key": "",
      "api_endpoint": "",
      "default_model": "",
      "max_tokens": 500,
      "temperature": 0.7,
      "timeout": 10000
    }
  },
  "fallback": {
    "provider": "rules",
    "model": "rule-based"
  },
  "routing": {
    "auto_select": true,
    "prefer_online": false,
    "internet_check_interval": 30000
  }
}
EOF
sudo cp /opt/d3kos/config/ai-config.json /opt/d3kos/config/ai-config.json.bak.openrouter
sudo cp /tmp/new-ai-config.json /opt/d3kos/config/ai-config.json
'
```

**2. Update MASTER_SYSTEM_SPEC.md:**
Remove OpenRouter references, update to show Ollama as primary AI provider.

**3. Update documentation:**
- AI_ASSISTANT_USER_GUIDE.md
- CLAUDE.md
- README.md

---

### Phase 5: Remove OpenRouter Dependency (5 minutes)

**1. Remove API key from config:**
Already done in Phase 4 (set to empty string)

**2. Update wake word responses:**
No changes needed - works with any provider

**3. Verify no hardcoded OpenRouter calls:**
```bash
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237 \
  'grep -r "openrouter" /opt/d3kos/services/ai/ | grep -v ".bak" | grep -v "config.json"'
```

If found, update to use Ollama or make provider-agnostic.

---

## Performance Expectations

### Response Times (Ollama phi3.5 on Pi 4B):

| Query Type | OpenRouter | Ollama phi3.5 | Acceptable? |
|------------|------------|---------------|-------------|
| Simple (rules) | 0.17s | 0.17s | ✅ Same |
| Complex (no RAG) | 6-8s | 20-40s | ✅ Acceptable |
| With RAG search | 10-14s | 35-65s | ✅ Acceptable |
| Very complex | 10-15s | 60-90s | ⚠️ Slow but works |

**User's Perspective:**
- Voice query: "How do I winterize my engine?"
- System: "Searching manuals..." (2-4s)
- System: "Processing..." (30-60s)
- Response: Complete winterization procedure from manual

**Acceptable for:**
- ✅ Non-critical queries
- ✅ Maintenance procedures
- ✅ Troubleshooting questions
- ✅ General marine advice

**NOT acceptable for:**
- ❌ Real-time navigation alerts (use Signal K alarms instead)
- ❌ Emergency situations (use radio/phone)

---

## Advantages of Ollama over OpenRouter

### ✅ Completely Free:
- No API costs
- No credit requirements
- No monthly fees
- No usage limits

### ✅ Privacy:
- All data stays on boat
- No internet required for complex queries
- No cloud logging
- GDPR/privacy compliant

### ✅ Offline Operation:
- Works without internet
- No dependency on external services
- Reliable in remote waters
- No service outages

### ✅ Customizable:
- Can swap models easily
- Can fine-tune for marine domain
- Can adjust temperature/parameters
- Full control over AI behavior

---

## Disadvantages (Trade-offs)

### ⚠️ Slower Responses:
- 20-90 seconds vs 6-14 seconds
- But still usable for non-emergency queries

### ⚠️ Smaller Model:
- phi3.5 (2.2GB) vs GPT-3.5-turbo (175B parameters)
- Less general knowledge
- But sufficient for boat-specific queries with RAG

### ⚠️ More RAM Usage:
- 2.2GB model loaded in RAM
- But Pi 4B has 8GB, plenty of room

---

## Rollback Plan (If Ollama Doesn't Work)

If Ollama proves too slow or unreliable:

### Option 1: Try Smaller Ollama Model
```bash
ollama pull phi3:mini    # 2.3GB → 1.2GB
ollama pull llama3.2:1b  # 1.3GB
```

### Option 2: Try Different Ollama Model
```bash
ollama pull gemma2:2b    # 1.6GB
ollama pull mistral      # 4.1GB (more capable, slower)
```

### Option 3: Restore OpenRouter (Paid)
```bash
# Restore config backup
sudo cp /opt/d3kos/config/ai-config.json.bak.openrouter \
        /opt/d3kos/config/ai-config.json

# Add $10 credits at https://openrouter.ai/settings/credits
```

### Option 4: Use Only Rule-Based (No AI)
Set all complex queries to return:
"For detailed procedures, please consult your boat manuals."

---

## Implementation Checklist

### Before Implementation:
- [ ] Verify Ollama is running: `systemctl status ollama`
- [ ] Verify phi3.5 model available: `ollama list`
- [ ] Backup current config: `cp ai-config.json ai-config.json.bak.openrouter`
- [ ] Backup query_handler.py: `cp query_handler.py query_handler.py.bak.openrouter`

### During Implementation:
- [ ] Update ai-config.json (Phase 4.1)
- [ ] Add query_ollama() method to query_handler.py (Phase 2)
- [ ] Update query() method routing logic (Phase 2)
- [ ] Test simple query (Phase 3.1)
- [ ] Test procedure query with RAG (Phase 3.2)
- [ ] Test complex query (Phase 3.3)

### After Implementation:
- [ ] Verify OpenRouter disabled: Check config shows `enabled: false`
- [ ] Remove API key from config (security)
- [ ] Update documentation (MASTER_SYSTEM_SPEC.md, CLAUDE.md)
- [ ] Test via voice assistant: "HELM" → "How do I change oil?"
- [ ] Monitor response times in real use

---

## Success Criteria

✅ **System is completely free:**
- No API keys required
- No paid services used
- No internet dependency for AI

✅ **AI still functional:**
- Complex queries answered correctly
- RAG integration works
- Manual content cited properly

✅ **Response times acceptable:**
- Simple queries: < 1 second (rules)
- Complex queries: < 60 seconds (Ollama)
- With RAG: < 90 seconds

✅ **User satisfied:**
- Answers are helpful
- Slow is acceptable (user acknowledged)
- System remains free and offline

---

## Estimated Time

- **Phase 1:** 5 minutes (update config)
- **Phase 2:** 30 minutes (modify query_handler.py)
- **Phase 3:** 15 minutes (testing)
- **Phase 4:** 10 minutes (update docs)
- **Phase 5:** 5 minutes (cleanup)

**Total:** ~65 minutes (1 hour)

---

## Questions Before Implementation

1. **Is 30-90 second response time acceptable for complex queries?**
   - User said: "it maybe slow but it works" ✅ YES

2. **Should we keep OpenRouter as fallback option?**
   - If internet available and query urgent?
   - Or completely remove? ✅ User wants free system

3. **Test Ollama first before full implementation?**
   - Quick test to verify performance
   - Then proceed with full integration

---

## Next Steps

**Recommend:**
1. **Quick Test First:** Test Ollama with one query to verify it works
2. **Full Implementation:** If test passes, proceed with all phases
3. **Monitor Performance:** Track response times for 1 week
4. **Optimize if Needed:** Try smaller models if too slow

**Ready to implement? Say "yes" to proceed with Phase 1.**

---

**Goal:** d3kOS = 100% Free, Offline, Open Source Marine System ✅
