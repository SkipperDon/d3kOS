# Voice Command - Single Wake Word System (HELM)

**Date**: February 22, 2026
**Status**: DESIGN FINAL - READY TO IMPLEMENT
**Estimated Time**: 30 minutes

---

## User Request

**ONE wake word for everything: "HELM"**

System automatically determines:
- Simple query → Answer immediately (instant)
- Complex query → Announce "Going to Seer to get the response" → Use AI (auto-detects online/onboard)

---

## System Behavior

### Single Wake Word: "HELM"

**User says**: "HELM"
**System responds**: "Aye Aye Captain"
**User asks any question**
**System automatically**:
1. Checks if it's a simple query (13 supported categories)
2. If YES → Answer immediately (0.2-2 seconds)
3. If NO → Say "Going to Seer to get the response" → Query AI (6-30 seconds)

---

## Example Conversations

### Example 1: Simple Query (Instant Response)
```
User: "HELM"
System: "Aye Aye Captain"
User: "What's the RPM?"
System: [instant] "Engine RPM is 1,850"
```

### Example 2: Complex Query (AI with Announcement)
```
User: "HELM"
System: "Aye Aye Captain"
User: "Why is my oil pressure dropping?"
System: "Going to Seer to get the response"
System: [7 second pause - querying online AI]
System: "Dropping oil pressure could indicate several issues: low oil level,
worn oil pump, clogged oil filter, or worn engine bearings..."
```

### Example 3: Another Simple Query
```
User: "HELM"
System: "Aye Aye Captain"
User: "Where am I?"
System: [instant] "Your position is 43.68 degrees north, 79.52 degrees west"
```

### Example 4: Complex Query with No Internet
```
User: "HELM"
System: "Aye Aye Captain"
User: "What are the fishing regulations for this lake?"
System: "Going to Seer to get the response"
System: [2 second pause - checking internet]
System: "I don't have internet access for complex questions. For quick boat data
like RPM, oil pressure, fuel, speed, etc., I can answer instantly. For complex
questions, please connect to internet."
```

### Example 5: Status Report (Simple but Multi-part)
```
User: "HELM"
System: "Aye Aye Captain"
User: "Give me a status report"
System: [2 seconds] "Engine RPM is 1850, oil pressure is 45 PSI, coolant
temperature is 180 degrees Fahrenheit, fuel level is 75 percent, battery
voltage is 13.2 volts, boat speed is 22 knots, heading is 045 degrees"
```

---

## Technical Implementation

### Flow Chart

```
User says "HELM"
    ↓
System: "Aye Aye Captain"
    ↓
Listen for 3 seconds
    ↓
Transcribe question
    ↓
Classify query
    ↓
┌─────────────────┐
│ Is it simple?   │
└─────────────────┘
    ↓         ↓
   YES       NO
    ↓         ↓
Answer      Say: "Going to Seer to get the response"
instantly       ↓
              Check internet
                ↓
           ┌─────────────┐
           │ Online?     │
           └─────────────┘
              ↓      ↓
            YES     NO
              ↓      ↓
          OpenRouter  Fallback
          (6-8s)     (2s)
              ↓      ↓
          Detailed   Error or
          answer    simple answer
```

---

## Code Changes

### File 1: voice-assistant-hybrid.py

**Change wake words to single word**:
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
        'ai': 'intelligent',  # Auto-route based on query complexity
        'response': 'Aye Aye Captain',
        'provider': 'auto',
        'description': 'Intelligent routing: instant for simple queries, AI for complex'
    }
}
```

**Update query_ai() method**:
```python
def query_ai(self, question, provider=None):
    """Query the AI handler with intelligent routing"""

    # Always check if it's a simple query first
    print(f"  🔍 Analyzing question...", flush=True)

    # Try to classify as simple query
    try:
        result = subprocess.run(
            ["python3", AI_QUERY_HANDLER, "--classify-only", question],
            capture_output=True,
            text=True,
            timeout=5,
            cwd="/opt/d3kos/services/ai"
        )

        is_simple = result.returncode == 0 and "SIMPLE:" in result.stdout

        if is_simple:
            # Simple query - answer immediately without announcement
            print(f"  ⚡ Simple query detected, using instant response", flush=True)

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

        # Complex query - announce going to Seer
        print(f"  🔮 Complex query detected, consulting AI assistant", flush=True)
        self.speak("Going to Seer to get the response")

        # Query AI with auto provider selection
        result = subprocess.run(
            ["python3", AI_QUERY_HANDLER, question],  # No force-provider = auto
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/opt/d3kos/services/ai"
        )

        if result.returncode == 0 and "Answer:" in result.stdout:
            answer = result.stdout.split("Answer:")[1].strip()
            return answer
        else:
            return "I'm having trouble answering that question."

    except Exception as e:
        print(f"  ⚠ Query error: {e}", flush=True)
        return "I encountered an error processing your question."
```

### File 2: query_handler.py

**Add --classify-only flag** (same as before):
```python
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('question', nargs='?')
    parser.add_argument('--force-provider', choices=['openrouter', 'onboard'])
    parser.add_argument('--classify-only', action='store_true',
                        help='Only classify query as simple or complex')
    args = parser.parse_args()

    if not args.question:
        print("Usage: query_handler.py [--force-provider openrouter|onboard] [--classify-only] <question>")
        sys.exit(1)

    handler = AIQueryHandler()

    # Classify-only mode
    if args.classify_only:
        category = handler.classify_simple_query(args.question)
        if category:
            print(f"SIMPLE: {category}")
            sys.exit(0)
        else:
            print("COMPLEX")
            sys.exit(1)

    # Regular query (existing code continues...)
```

**Improve auto mode to prioritize simple queries**:
```python
def query(self, question, force_provider=None):
    """Main query handler with intelligent routing"""
    start_time = time.time()

    # Check if simple query FIRST (unless explicitly forcing online)
    if force_provider != 'openrouter':
        simple_category = self.classify_simple_query(question)
        if simple_category:
            # Use rule-based response immediately
            answer = self.simple_response(simple_category)
            elapsed = time.time() - start_time
            return {
                'answer': answer,
                'provider': 'onboard',
                'model': 'rules',
                'response_time': elapsed,
                'ai_used': 'onboard'
            }

    # Complex query - determine provider based on internet
    has_internet = self.check_internet()

    if force_provider == 'onboard':
        provider = 'onboard'
    elif force_provider == 'openrouter' and has_internet:
        provider = 'openrouter'
    elif has_internet:
        # Auto-select: prefer online for complex queries
        provider = 'openrouter'
    else:
        provider = 'onboard'

    # Query the provider (existing code continues...)
```

### File 3: wake_word_vosk.py

**Update wake word list**:
```python
# In __init__ method:
# BEFORE:
self.wake_words = ['helm', 'advisor', 'counsel']

# AFTER:
self.wake_words = ['helm']  # Single wake word only
```

### File 4: wake-words.kws (Sphinx config)

**Update keywords**:
```
# BEFORE:
helm /1e-3/
advisor /1e-3/
counsel /1e-3/

# AFTER:
helm /1e-3/
```

---

## Simple Query Categories (13 total)

System answers these **instantly** without announcing "Going to Seer":

1. **rpm** - Engine RPM, revolutions, engine speed
2. **oil** - Oil pressure
3. **temperature** - Coolant temperature, engine temp
4. **fuel** - Fuel level, gas remaining
5. **battery** - Battery voltage, electrical
6. **speed** - Boat speed, knots, velocity
7. **heading** - Heading, direction, course, bearing
8. **boost** - Boost pressure, turbo pressure
9. **hours** - Engine hours, runtime, operating time
10. **location** - GPS position, coordinates, where am I
11. **time** - Current time, what time is it, date
12. **help** - What can you do, capabilities, commands
13. **status** - Full status report, all systems, overview

**Anything else** → Announces "Going to Seer" → Uses AI

---

## User Benefits

### Before (3 wake words):
```
User: "Hmm, do I use helm, advisor, or counsel?"
User: "COUNSEL" [guesses]
System: "Aye Aye Captain"
User: "What's the RPM?"
System: [8 seconds - unnecessary API call]
System: "Engine RPM is 1,850"
User: "That was slow..."
```

### After (1 wake word):
```
User: "HELM"
System: "Aye Aye Captain"
User: "What's the RPM?"
System: [instant] "Engine RPM is 1,850"
User: "Perfect!"

Later...
User: "HELM"
System: "Aye Aye Captain"
User: "Why is my oil pressure dropping?"
System: "Going to Seer to get the response"
System: [7 seconds]
System: "Dropping oil pressure could indicate..."
User: "Ah, it's using AI for complex questions. Makes sense!"
```

---

## Advantages

1. ✅ **Simplest possible**: Only ONE wake word to remember
2. ✅ **Intelligent**: System decides simple vs complex automatically
3. ✅ **Transparent**: User knows when AI is being consulted ("Going to Seer")
4. ✅ **Fast**: Simple queries instant, no wasted time
5. ✅ **Efficient**: No unnecessary API calls for simple data
6. ✅ **Automatic**: Internet detection built-in
7. ✅ **Intuitive**: Just say "HELM" for everything

---

## Testing Plan

### Test 1: Simple Queries (No Announcement)
```bash
Say: "HELM"
Expected: "Aye Aye Captain"

Say: "What's the RPM?"
Expected: [instant, NO "Going to Seer"] "Engine RPM is [value]"

Say: "HELM"
Say: "What's the fuel level?"
Expected: [instant, NO "Going to Seer"] "Fuel level is [value]"

Say: "HELM"
Say: "Where am I?"
Expected: [instant, NO "Going to Seer"] "Your position is..."
```

### Test 2: Complex Queries (With Announcement)
```bash
# With internet
Say: "HELM"
Say: "Why is my oil pressure dropping?"
Expected:
  - "Going to Seer to get the response"
  - [7 second pause]
  - "Dropping oil pressure could indicate..."

Say: "HELM"
Say: "What are the fishing regulations?"
Expected:
  - "Going to Seer to get the response"
  - [8 second pause]
  - Detailed regulations answer
```

### Test 3: Offline Complex Query
```bash
# Disconnect internet
Say: "HELM"
Say: "Explain engine overheating causes"
Expected:
  - "Going to Seer to get the response"
  - [2 second pause]
  - "I don't have internet access for complex questions..."
```

### Test 4: Status Report (Simple Multi-part)
```bash
Say: "HELM"
Say: "Give me a full status report"
Expected: [2 seconds, NO "Going to Seer"]
  "Engine RPM is..., oil pressure is..., coolant temperature is..., etc."
```

---

## Implementation Steps

### Step 1: Backup
```bash
sudo cp /opt/d3kos/services/voice/voice-assistant-hybrid.py \
       /opt/d3kos/services/voice/voice-assistant-hybrid.py.before-single-wake
sudo cp /opt/d3kos/services/ai/query_handler.py \
       /opt/d3kos/services/ai/query_handler.py.before-single-wake
```

### Step 2: Update voice-assistant-hybrid.py
- Change WAKE_WORDS to single 'helm' entry
- Update query_ai() with intelligent routing
- Add "Going to Seer" announcement for complex queries

### Step 3: Update query_handler.py
- Add --classify-only flag
- Improve auto mode to check simple queries first

### Step 4: Update wake_word_vosk.py
- Change wake_words to ['helm'] only

### Step 5: Update wake-words.kws
- Keep only 'helm /1e-3/'

### Step 6: Restart Services
```bash
sudo systemctl restart d3kos-voice
sudo systemctl restart d3kos-ai-api
```

### Step 7: Test All Scenarios
- Simple queries (instant, no announcement)
- Complex queries (announcement + AI)
- Offline complex queries (announcement + error)
- Status report (multi-part simple)

---

## Summary

**ONE wake word: "HELM"**

**Behavior**:
- Simple question → Instant answer (no announcement)
- Complex question → "Going to Seer to get the response" → AI answer (6-30s)
- Auto-detects internet for complex queries
- User always knows when AI is being consulted

**Result**: Simplest, most intuitive voice system possible!

---

**Status**: FINAL DESIGN - READY TO IMPLEMENT
**Time**: 30 minutes
**Complexity**: Low (mainly config changes)
