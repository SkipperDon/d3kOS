# Groq Integration Implementation Plan
**Date:** February 27, 2026
**Goal:** Replace Ollama with Groq for Detailed Answer mode (3-5s vs 10-15min)
**Status:** PLANNING

---

## Architecture Overview

### Current System:
- **Quick Mode:** RAG only (1-2s, offline, 5 chunks)
- **Detailed Mode:** RAG + Ollama (10-15min, offline, times out)

### Target System:
- **Quick Mode:** RAG only (1-2s, offline, 5 chunks) - NO CHANGE
- **Detailed Mode:** RAG + Groq (3-5s, **online**, 5 chunks)

### Why RAG is Still Needed:
1. RAG searches user's specific PDFs (fishing regulations, manuals)
2. Groq only has general knowledge
3. RAG provides context from user's documents
4. Groq formats the context into conversational answers

---

## Phase 1: Get Groq API Key (15 min)

### Steps:
1. Go to https://console.groq.com
2. Sign up (free, no credit card)
3. Create API key
4. Copy key (format: `gsk_...`)

### Groq Free Tier Limits:
- 30 requests/minute
- 14,400 requests/day
- Models available:
  - `llama-3.3-70b-versatile` (recommended)
  - `llama-3.1-70b-versatile`
  - `mixtral-8x7b-32768`
  - `gemma2-9b-it`

### Success Criteria:
- [ ] Have valid Groq API key

---

## Phase 2: Add Groq Configuration (20 min)

### File: `/opt/d3kos/config/ai-config.json`

**Backup first:**
```bash
sudo cp /opt/d3kos/config/ai-config.json /opt/d3kos/config/ai-config.json.bak.before-groq
```

**Add Groq provider:**
```json
{
  "active_provider": "groq",
  "providers": {
    "groq": {
      "enabled": true,
      "api_key": "gsk_YOUR_KEY_HERE",
      "api_endpoint": "https://api.groq.com/openai/v1/chat/completions",
      "default_model": "llama-3.3-70b-versatile",
      "temperature": 0.7,
      "timeout": 10000
    },
    "ollama": {
      "enabled": false,
      "api_endpoint": "http://localhost:11434/api/chat",
      "default_model": "tinyllama",
      "temperature": 0.7,
      "timeout": 900000
    },
    "openrouter": {
      "enabled": false,
      "api_key": "",
      "api_endpoint": "",
      "default_model": ""
    }
  }
}
```

### Commands:
```bash
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237

# Edit config (add Groq section)
sudo nano /opt/d3kos/config/ai-config.json

# Verify JSON syntax
python3 -c "import json; json.load(open('/opt/d3kos/config/ai-config.json'))"
```

### Success Criteria:
- [ ] Groq section added to config
- [ ] API key configured
- [ ] JSON syntax valid
- [ ] Backup created

---

## Phase 3: Implement query_groq() Method (45 min)

### File: `/opt/d3kos/services/ai/query_handler.py`

**Backup first:**
```bash
sudo cp /opt/d3kos/services/ai/query_handler.py /opt/d3kos/services/ai/query_handler.py.bak.before-groq
```

**Add method after query_ollama():**

```python
def query_groq(self, question, context, manual_context=None):
    """Query Groq API with optional manual context"""
    config = self.config["providers"]["groq"]
    
    if not config.get("enabled", False):
        raise ValueError("Groq provider not enabled")
    
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
- Boost Pressure: {boat_status.get('boost_pressure', 'N/A')} PSI
- Engine Hours: {boat_status.get('engine_hours', 'N/A')} hours
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
    
    # Groq API format (OpenAI-compatible)
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        "temperature": config["temperature"]
    }
    
    req = urllib.request.Request(
        config["api_endpoint"],
        data=json.dumps(data).encode('utf-8'),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config['api_key']}"
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=config["timeout"]/1000) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result["choices"][0]["message"]["content"], model
    except Exception as e:
        raise Exception(f"Groq API error: {str(e)}")
```

### Update provider routing logic:

**Find this section (around line 520):**
```python
if provider == 'ollama':
    answer, model = self.query_ollama(question, context, manual_context)
    ai_used = 'onboard'
```

**Change to:**
```python
if provider == 'groq':
    answer, model = self.query_groq(question, context, manual_context)
    ai_used = 'online'
elif provider == 'ollama':
    answer, model = self.query_ollama(question, context, manual_context)
    ai_used = 'onboard'
```

### Update provider selection logic:

**Find auto-select logic (around line 510):**
```python
elif has_internet and force_provider is None:
    active = self.config["active_provider"]
    if self.config["providers"][active]["enabled"]:
        provider = active
```

**Should automatically use Groq when active_provider is "groq"**

### Test Python syntax:
```bash
python3 -m py_compile /opt/d3kos/services/ai/query_handler.py
```

### Success Criteria:
- [ ] query_groq() method added
- [ ] Provider routing updated
- [ ] Python syntax valid
- [ ] Backup created

---

## Phase 4: Update UI (15 min)

### File: `/var/www/html/ai-assistant.html`

**Backup first:**
```bash
sudo cp /var/www/html/ai-assistant.html /var/www/html/ai-assistant.html.bak.before-groq
```

**Update button text:**

Find:
```html
<button class="mode-button" id="detailedModeBtn" onclick="setMode('detailed')">📝 Detailed Answer (5-10min)</button>
```

Change to:
```html
<button class="mode-button" id="detailedModeBtn" onclick="setMode('detailed')">📝 Detailed Answer (3-5s)</button>
```

**Update fetch request:**

Find:
```javascript
body: JSON.stringify({
    question: question,
    provider: 'ollama',
    quick_mode: currentMode === 'quick'
})
```

Change to:
```javascript
body: JSON.stringify({
    question: question,
    provider: 'groq',
    quick_mode: currentMode === 'quick'
})
```

**Update status badge (optional):**

Find:
```html
<div style="font-size: 36px; font-weight: bold;">Onboard AI with Manual Search</div>
<div style="font-size: 28px; color: #888;">Using tinyllama language model • 100% Free</div>
```

Change to:
```html
<div style="font-size: 36px; font-weight: bold;">AI with Manual Search</div>
<div style="font-size: 28px; color: #888;">Quick: Offline • Detailed: Groq API • 100% Free</div>
```

### Success Criteria:
- [ ] Button text updated to "3-5s"
- [ ] Provider changed to "groq"
- [ ] Status badge updated
- [ ] Backup created

---

## Phase 5: Restart Services (5 min)

```bash
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237

# Restart AI API service
sudo systemctl restart d3kos-ai-api

# Check status
systemctl status d3kos-ai-api --no-pager | head -15

# Check logs for initialization
journalctl -u d3kos-ai-api -n 20 --no-pager
```

### Success Criteria:
- [ ] Service starts without errors
- [ ] Logs show "AI query handler ready"
- [ ] No Groq API errors in logs

---

## Phase 6: Testing (30 min)

### Test 1: Quick Mode (should be unchanged)

**Query:** "What is the walleye limit on Lake Erie?"
**Expected:** 
- Response in 1-2 seconds
- Returns 5 chunks from PDF
- Formatted text display

**Verify:**
```bash
# Monitor logs
journalctl -u d3kos-ai-api -f
```

**Success Criteria:**
- [ ] Response < 2 seconds
- [ ] Shows "Found 5 relevant chunks"
- [ ] Answer displays correctly
- [ ] Works offline (disconnect internet)

### Test 2: Detailed Mode (Groq)

**Query:** "What is the walleye limit on Lake Erie?"
**Expected:**
- Response in 3-5 seconds
- Calls Groq API
- Returns polished conversational answer

**Verify:**
```bash
# Monitor logs
journalctl -u d3kos-ai-api -f

# Should see:
# - "Found 5 relevant chunks"
# - No timeout errors
# - Response returned
```

**Success Criteria:**
- [ ] Response < 10 seconds
- [ ] Answer is conversational (not raw chunks)
- [ ] Cites source documents
- [ ] Accurate information
- [ ] Requires internet connection

### Test 3: API Direct Test

```bash
# Test Groq endpoint directly
curl -X POST http://localhost:8080/ai/query \
  -H "Content-Type: application/json" \
  -d '{"question":"What is the walleye limit?","provider":"groq","quick_mode":false}' \
  | jq .
```

**Success Criteria:**
- [ ] Returns JSON response
- [ ] Has "answer" field
- [ ] Response_time_ms < 10000
- [ ] Model shows "llama-3.3-70b-versatile"

### Test 4: Error Handling

**Test offline Detailed mode:**
- Disconnect internet
- Try Detailed mode
- Should show error message

**Test invalid API key:**
- Change API key to invalid
- Restart service
- Try Detailed mode
- Should show authentication error

**Success Criteria:**
- [ ] Graceful error messages
- [ ] Quick mode still works offline
- [ ] Clear user feedback

### Test 5: Multiple Queries (Rate Limit Test)

Ask 5 different questions in Detailed mode within 1 minute.

**Success Criteria:**
- [ ] All 5 complete successfully
- [ ] No rate limit errors
- [ ] Response times consistent (3-5s each)

---

## Phase 7: Verification (15 min)

### Checklist:

**Configuration:**
- [ ] ai-config.json has Groq section
- [ ] API key is valid
- [ ] active_provider is "groq"
- [ ] Ollama disabled

**Code:**
- [ ] query_groq() method exists
- [ ] Provider routing includes Groq
- [ ] No Python syntax errors
- [ ] Backups created

**UI:**
- [ ] Button shows "3-5s"
- [ ] Provider is "groq"
- [ ] Status badge updated
- [ ] Toggle works correctly

**Functionality:**
- [ ] Quick mode: 1-2 seconds (offline)
- [ ] Detailed mode: 3-5 seconds (online)
- [ ] RAG search working (5 chunks)
- [ ] Answers are accurate

**Error Handling:**
- [ ] Offline Detailed mode shows error
- [ ] Invalid API key shows error
- [ ] Quick mode works offline
- [ ] Service starts without errors

---

## Phase 8: Documentation (30 min)

### Create: `/home/boatiq/Helm-OS/doc/GROQ_INTEGRATION_COMPLETE_2026-02-27.md`

**Contents:**
- Architecture overview (Quick vs Detailed)
- Why RAG is still needed
- Groq API setup instructions
- Configuration details
- Code changes made
- Testing results
- Performance comparison
- User experience before/after
- Files modified
- Backup locations
- Troubleshooting guide
- Rollback instructions

### Update: `/home/boatiq/Helm-OS/doc/MEMORY.md`

**Add session entry:**
```markdown
## Session: Groq Integration (2026-02-27)

**Status:** ✅ COMPLETE
**Goal:** Replace Ollama with Groq for fast Detailed answers

**What Changed:**
- Quick mode: RAG only (1-2s, offline) - unchanged
- Detailed mode: RAG + Groq (3-5s, online) - was 10-15min with Ollama
- Added query_groq() method
- Updated UI buttons (3-5s vs 5-10min)
- Tested and verified

**Performance:**
- Quick mode: 1-2 seconds (5 chunks)
- Detailed mode: 3-5 seconds (5 chunks + Groq)
- 100% free (Groq free tier)

**Files Modified:**
- ai-config.json - Added Groq provider
- query_handler.py - Added query_groq() method
- ai-assistant.html - Updated button text and provider

**User Impact:**
- Fast detailed answers (3-5s vs 10-15min)
- No more timeouts
- Still 100% free
- Detailed mode requires internet
```

### Success Criteria:
- [ ] GROQ_INTEGRATION_COMPLETE_2026-02-27.md created
- [ ] MEMORY.md updated
- [ ] All files and changes documented

---

## Phase 9: Git Commit (10 min)

### Commit Message:
```
feat: Replace Ollama with Groq for Detailed Answer mode

- Added Groq API integration (query_groq method)
- Updated UI: Detailed Answer button shows "3-5s" instead of "5-10min"
- Quick mode: RAG only (1-2s, offline, 5 chunks) - unchanged
- Detailed mode: RAG + Groq (3-5s, online, 5 chunks) - was 10-15min timeout
- Groq free tier: 30 req/min, 14,400 req/day
- Performance: 200x faster than Ollama (3-5s vs 10-15min)
- Still 100% free for reasonable usage
- Detailed mode now requires internet connection

Files modified:
- /opt/d3kos/config/ai-config.json (added Groq provider)
- /opt/d3kos/services/ai/query_handler.py (added query_groq method)
- /var/www/html/ai-assistant.html (updated UI text and provider)

Tested:
- Quick mode: 1-2s (offline) ✓
- Detailed mode: 3-5s (online) ✓
- 5 chunks RAG search working ✓
- Error handling verified ✓

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

### Commands:
```bash
cd /home/boatiq/Helm-OS

# Check status
git status

# Stage changed files
git add doc/GROQ_INTEGRATION_COMPLETE_2026-02-27.md
git add doc/MEMORY.md

# Commit with message
git commit -m "$(cat <<'COMMIT_MSG'
feat: Replace Ollama with Groq for Detailed Answer mode

[Full message from above]
COMMIT_MSG
)"

# Push to GitHub
git push origin main
```

### Success Criteria:
- [ ] All documentation committed
- [ ] Commit message is clear
- [ ] Pushed to GitHub
- [ ] No uncommitted changes

---

## Rollback Plan (if needed)

### If Groq integration fails:

**Step 1: Restore config**
```bash
sudo cp /opt/d3kos/config/ai-config.json.bak.before-groq \
        /opt/d3kos/config/ai-config.json
```

**Step 2: Restore query handler**
```bash
sudo cp /opt/d3kos/services/ai/query_handler.py.bak.before-groq \
        /opt/d3kos/services/ai/query_handler.py
```

**Step 3: Restore UI**
```bash
sudo cp /var/www/html/ai-assistant.html.bak.before-groq \
        /var/www/html/ai-assistant.html
```

**Step 4: Restart service**
```bash
sudo systemctl restart d3kos-ai-api
```

**Step 5: Verify**
```bash
systemctl status d3kos-ai-api
journalctl -u d3kos-ai-api -n 20
```

---

## Timeline Estimate

| Phase | Time | Description |
|-------|------|-------------|
| 1 | 15 min | Get Groq API key |
| 2 | 20 min | Add configuration |
| 3 | 45 min | Implement query_groq() |
| 4 | 15 min | Update UI |
| 5 | 5 min | Restart services |
| 6 | 30 min | Testing |
| 7 | 15 min | Verification |
| 8 | 30 min | Documentation |
| 9 | 10 min | Git commit |
| **Total** | **3 hours** | **Complete implementation** |

---

## Success Metrics

**Before (Ollama):**
- Quick mode: 1-2s ✓
- Detailed mode: 10-15 min (often timeout) ✗

**After (Groq):**
- Quick mode: 1-2s ✓
- Detailed mode: 3-5s ✓

**Improvement:** 200x faster (3s vs 600s)

---

## Next Steps After Implementation

1. Monitor Groq API usage (check dashboard)
2. Collect user feedback on answer quality
3. Fine-tune prompts if needed
4. Consider adding more models (Mixtral, Gemma)
5. Implement caching for common queries

---

**Status:** READY TO IMPLEMENT
**Date:** 2026-02-27
**Estimated Completion:** 3 hours
