# Voice Command Simplification - HELM vs SEER

**Date**: February 22, 2026
**Status**: DESIGN APPROVED - READY TO IMPLEMENT
**Estimated Time**: 30-45 minutes

---

## User Request

Simplify voice commands from 3 wake words to 2:
- **"HELM"** - Quick boat operations (rule-based, instant)
- **"SEER"** - AI assistant (complex queries, auto-detects online/onboard)

---

## Current System (Confusing)

**Wake Words**: helm, advisor, counsel (3 options)

**Behavior**:
- "Helm" → Auto mode (prefers online if available)
- "Advisor" → Onboard only (rule-based or error)
- "Counsel" → Online only (OpenRouter required)

**Problems**:
1. Too many wake words to remember
2. "Helm" doesn't match boat operations expectations
3. No clear distinction between simple vs complex queries
4. User must know which mode they need in advance

---

## Proposed System (Intuitive)

**Wake Words**: helm, seer (2 options)

### "HELM" - Quick Boat Commands

**Purpose**: Instant responses for boat operations

**Supported Commands** (13 categories):
- Engine: `rpm`, `oil pressure`, `temperature`, `boost`
- Gauges: `fuel`, `battery`, `speed`, `heading`
- Navigation: `location` (GPS position)
- System: `engine hours`, `time`, `help`, `status`

**Behavior**:
- Always uses rule-based responses (no AI)
- Response time: 0.2-2 seconds (instant)
- Works offline (no internet required)
- Direct sensor data from Signal K

**Example Conversations**:
```
You: "HELM"
System: "Aye Aye Captain"
You: "What's the RPM?"
System: "Engine RPM is 1,850"  [instant]

You: "HELM"
System: "Aye Aye Captain"
You: "Where am I?"
System: "Your position is 43.68 degrees north, 79.52 degrees west"  [instant]

You: "HELM"
System: "Aye Aye Captain"
You: "Give me a status report"
System: "Engine RPM is 1850, oil pressure is 45 PSI, coolant temperature is 180 degrees..."
```

**If Complex Question**:
```
You: "HELM"
System: "Aye Aye Captain"
You: "Why is my oil pressure dropping?"
System: "For complex questions, please use the wake word 'SEER' to access the AI assistant."
```

---

### "SEER" - AI Assistant (Complex Queries)

**Purpose**: Intelligent reasoning for complex questions

**Behavior**:
- Checks for internet connection automatically
- If online: Uses OpenRouter (gpt-3.5-turbo, 6-8 seconds)
- If offline: Falls back to rule-based or helpful error
- Response time: 6-30 seconds depending on complexity

**Example Conversations**:
```
You: "SEER"
System: "Aye Aye Captain"
You: "Why is my oil pressure dropping?"
System: [6s delay] "Dropping oil pressure could indicate several issues: low oil level,
worn oil pump, clogged oil filter, or worn engine bearings. Check your oil level
immediately. If the level is adequate, the oil pressure sensor may be faulty..."

You: "SEER"
System: "Aye Aye Captain"
You: "What are the fishing regulations for Lake Simcoe?"
System: [8s delay] "For Lake Simcoe, Ontario regulations include: Walleye season
opens third Saturday in May, limit 4 fish with 1 over 18 inches. Yellow perch
year-round, limit 50 fish..."

You: "SEER"
System: "Aye Aye Captain"
You: "Should I be worried about this weather?"
System: [7s delay] "Based on current conditions and forecast..."
```

**If No Internet**:
```
You: "SEER"
System: "Aye Aye Captain"
You: "Why is my engine overheating?"
System: [2s delay] "I don't have internet access for complex AI reasoning.
For quick boat data, use 'HELM'. For complex questions, please connect to internet."
```

---

## Implementation Changes

### File 1: Wake Word Configuration

**File**: `/opt/d3kos/services/voice/voice-assistant-hybrid.py`

**Change wake words**:
```python
# BEFORE:
WAKE_WORDS = {
    'helm': {'ai': 'auto', 'response': 'Aye Aye Captain', 'provider': None},
    'advisor': {'ai': 'onboard', 'response': 'Aye Aye Captain', 'provider': 'onboard'},
    'counsel': {'ai': 'online', 'response': 'Aye Aye Captain', 'provider': 'openrouter'}
}

# AFTER:
WAKE_WORDS = {
    'helm': {
        'ai': 'simple-only',
        'response': 'Aye Aye Captain',
        'provider': 'simple',
        'description': 'Quick boat commands (RPM, oil, fuel, speed, etc.)'
    },
    'seer': {
        'ai': 'auto',
        'response': 'Aye Aye Captain',
        'provider': None,
        'description': 'AI assistant for complex questions (auto-detects online/onboard)'
    }
}
```

### File 2: Query Handler Logic

**File**: `/opt/d3kos/services/voice/voice-assistant-hybrid.py`

**Add simple-only mode**:
```python
def query_ai(self, question, provider=None):
    """Query the AI handler with routing based on wake word"""

    # NEW: Handle simple-only mode (HELM wake word)
    if provider == 'simple':
        print(f"  ⚡ HELM mode: Checking for simple query...", flush=True)

        # Try to classify as simple query
        result = subprocess.run(
            ["python3", AI_QUERY_HANDLER, "--classify-only", question],
            capture_output=True,
            text=True,
            timeout=5,
            cwd="/opt/d3kos/services/ai"
        )

        if result.returncode == 0 and "SIMPLE:" in result.stdout:
            # It's a simple query, get the answer
            result = subprocess.run(
                ["python3", AI_QUERY_HANDLER, "--force-provider", "onboard", question],
                capture_output=True,
                text=True,
                timeout=10,
                cwd="/opt/d3kos/services/ai"
            )

            if result.returncode == 0 and "Answer:" in result.stdout:
                answer = result.stdout.split("Answer:")[1].strip()
                return answer

        # Not a simple query - redirect to SEER
        supported = "RPM, oil pressure, temperature, fuel, battery, speed, heading, boost, engine hours, location, time, help, and status"
        return f"I can provide quick answers for: {supported}. For complex questions, please use the wake word 'SEER' to access the AI assistant."

    # EXISTING: Handle auto mode (SEER wake word) or forced provider
    mode_name = provider if provider else 'auto'
    print(f"  🤖 Querying AI (mode: {mode_name})...", flush=True)

    # ... existing code continues ...
```

### File 3: Query Handler Updates

**File**: `/opt/d3kos/services/ai/query_handler.py`

**Add classify-only flag**:
```python
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('question', nargs='?')
    parser.add_argument('--force-provider', choices=['openrouter', 'onboard'])
    parser.add_argument('--classify-only', action='store_true',
                        help='Only classify query, do not answer')
    args = parser.parse_args()

    if not args.question:
        print("Usage: query_handler.py [--force-provider openrouter|onboard] [--classify-only] <question>")
        sys.exit(1)

    handler = AIQueryHandler()

    # NEW: Classify-only mode for HELM wake word
    if args.classify_only:
        category = handler.classify_simple_query(args.question)
        if category:
            print(f"SIMPLE: {category}")
            sys.exit(0)
        else:
            print("COMPLEX")
            sys.exit(1)

    # Regular query
    result = handler.query(args.question, force_provider=args.force_provider)

    # ... existing code continues ...
```

### File 4: Vosk Wake Word Detector

**File**: `/opt/d3kos/services/voice/wake_word_vosk.py`

**Update wake word list**:
```python
# In __init__ method:
# BEFORE:
self.wake_words = ['helm', 'advisor', 'counsel']

# AFTER:
self.wake_words = ['helm', 'seer']
```

### File 5: Sphinx Config (if using PocketSphinx fallback)

**File**: `/opt/d3kos/config/sphinx/wake-words.kws`

**Update keywords**:
```
# BEFORE:
helm /1e-3/
advisor /1e-3/
counsel /1e-3/

# AFTER:
helm /1e-3/
seer /1e-3/
```

---

## User Experience Comparison

### OLD SYSTEM (Confusing):
```
User thinks: "I want to know my RPM"
User wonders: "Should I use helm, advisor, or counsel?"
User guesses: "COUNSEL"
System: [8 seconds] "The engine RPM is 1,850"
User thinks: "That was slow... and I'm not sure I used the right wake word"
```

### NEW SYSTEM (Clear):
```
User thinks: "I want to know my RPM - that's boat operations"
User says: "HELM"
System: "Aye Aye Captain"
User says: "What's the RPM?"
System: [instant] "Engine RPM is 1,850"
User thinks: "Perfect! Quick and easy."
```

```
User thinks: "Why is my oil pressure dropping? That needs AI reasoning"
User says: "SEER"
System: "Aye Aye Captain"
User says: "Why is my oil pressure dropping?"
System: [7 seconds] "Dropping oil pressure could indicate..."
User thinks: "That makes sense. It took a moment but gave me a detailed answer."
```

---

## Testing Plan

### Phase 1: HELM Wake Word (Simple Queries)

**Test 1: Supported Commands**
```bash
Say: "HELM"
Expected: "Aye Aye Captain"

Say: "What's the RPM?"
Expected: [0.2s] "Engine RPM is [value]"

Say: "HELM"
Say: "What's the fuel level?"
Expected: [0.2s] "Fuel level is [value]"

Say: "HELM"
Say: "Give me the status"
Expected: [2s] "Engine RPM is..., oil pressure is..., etc."
```

**Test 2: Complex Query Redirect**
```bash
Say: "HELM"
Say: "Why is my engine overheating?"
Expected: "I can provide quick answers for: RPM, oil pressure...
For complex questions, please use the wake word 'SEER'."
```

### Phase 2: SEER Wake Word (AI Assistant)

**Test 3: Online AI**
```bash
# Ensure internet connected
Say: "SEER"
Expected: "Aye Aye Captain"

Say: "Why is my oil pressure dropping?"
Expected: [6-8s] "Dropping oil pressure could indicate..." (detailed answer)
```

**Test 4: Simple Query via SEER (should still work)**
```bash
Say: "SEER"
Say: "What's the RPM?"
Expected: [6-8s] "The engine RPM is [value]"
Note: Slower than HELM, but still works
```

**Test 5: Offline Fallback**
```bash
# Disconnect internet
Say: "SEER"
Say: "Why is my engine overheating?"
Expected: [2s] "I don't have internet access for complex AI reasoning.
For quick boat data, use 'HELM'. For complex questions, please connect to internet."
```

---

## Benefits

### For Users:
1. ✅ **Simpler**: Only 2 wake words to remember (was 3)
2. ✅ **Intuitive**: "Helm" for boat, "Seer" for AI wisdom
3. ✅ **Faster**: Simple queries get instant responses
4. ✅ **Automatic**: No need to know if internet is available
5. ✅ **Clear purpose**: Each wake word has distinct use case

### For System:
1. ✅ **Efficient**: Simple queries don't waste API calls
2. ✅ **Scalable**: Can add more simple patterns without affecting AI
3. ✅ **Maintainable**: Clear separation of concerns
4. ✅ **Cost-effective**: Reduces OpenRouter API usage

---

## Backwards Compatibility

**Migration**: Old wake words will stop working after update
- "advisor" → Use "HELM" instead
- "counsel" → Use "SEER" instead
- "helm" (old behavior) → Use "SEER" for same behavior

**Documentation**: Update all docs to reference new wake words

---

## Implementation Steps

### Step 1: Backup Current System
```bash
sudo cp /opt/d3kos/services/voice/voice-assistant-hybrid.py \
       /opt/d3kos/services/voice/voice-assistant-hybrid.py.before-seer
sudo cp /opt/d3kos/services/ai/query_handler.py \
       /opt/d3kos/services/ai/query_handler.py.before-seer
```

### Step 2: Update Wake Words
- Edit voice-assistant-hybrid.py
- Change WAKE_WORDS dict (2 wake words)
- Update query_ai() method (add simple-only mode)

### Step 3: Update Query Handler
- Edit query_handler.py
- Add --classify-only flag
- Test classification logic

### Step 4: Update Vosk Config
- Edit wake_word_vosk.py
- Change wake_words list to ['helm', 'seer']

### Step 5: Restart Services
```bash
sudo systemctl restart d3kos-voice
sudo systemctl restart d3kos-ai-api
```

### Step 6: Test Both Wake Words
- Test HELM with simple queries
- Test HELM with complex queries (expect redirect)
- Test SEER with complex queries (online)
- Test SEER with simple queries (should work but slower)
- Test SEER offline (expect fallback message)

### Step 7: Update Documentation
- README.md - Voice Assistant section
- AI_ASSISTANT_USER_GUIDE.md - Wake words
- VOICE_FIX_APPLIED_2026-02-22.md - Note system change

---

## Estimated Time

- **Backup**: 2 minutes
- **Code changes**: 20 minutes
- **Testing**: 15 minutes
- **Documentation**: 10 minutes
- **Total**: 45-50 minutes

---

## Rollback Plan

If issues occur:
```bash
sudo cp /opt/d3kos/services/voice/voice-assistant-hybrid.py.before-seer \
       /opt/d3kos/services/voice/voice-assistant-hybrid.py
sudo cp /opt/d3kos/services/ai/query_handler.py.before-seer \
       /opt/d3kos/services/ai/query_handler.py
sudo systemctl restart d3kos-voice
sudo systemctl restart d3kos-ai-api
```

---

## Summary

**Current**: 3 wake words (helm/advisor/counsel) - confusing, slow for simple queries
**Proposed**: 2 wake words (helm/seer) - intuitive, fast for operations, smart for AI

**HELM** = Quick boat commands (instant)
**SEER** = AI assistant (auto-detects online/onboard)

**Ready to implement**: Yes, design is sound and implementation is straightforward.

---

**Status**: AWAITING USER APPROVAL TO PROCEED
**Next Step**: Implement changes and test
