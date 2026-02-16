# Phase 2 Complete - Wake Word Updates and AI Integration

**Date**: 2026-02-12
**Status**: ✅ COMPLETE

---

## Summary

Phase 2 implementation completed:
1. Removed Perplexity provider (policy change)
2. Updated AI query handler with command-line arguments
3. Implemented three wake words: Helm, Advisor, Counsel
4. Added "Aye Aye Captain" acknowledgment
5. Integrated voice assistant with AI query handler
6. Created PocketSphinx keyword file for multi-wake-word detection

---

## Changes Made

### 1. Perplexity Removal

**Reason**: Policy change - Perplexity will not be part of this build

**Files Modified**:
- `/opt/d3kos/config/ai-config.json` - Removed Perplexity provider section
- `/opt/d3kos/services/ai/query_handler.py` - Removed `query_perplexity()` method

**Updated Configuration**:
```json
{
  "active_provider": "openrouter",
  "providers": {
    "openrouter": {
      "enabled": true,
      "api_key": "sk-or-v1-***REDACTED***",
      "api_endpoint": "https://openrouter.ai/api/v1/chat/completions",
      "default_model": "openai/gpt-3.5-turbo",
      "max_tokens": 500,
      "temperature": 0.7,
      "timeout": 10000
    }
  },
  "fallback": {
    "provider": "onboard",
    "model": "phi-2"
  },
  "routing": {
    "auto_select": true,
    "prefer_online": true,
    "internet_check_interval": 30000
  }
}
```

---

### 2. Query Handler v2 - Command-Line Arguments

**File**: `/opt/d3kos/services/ai/query_handler.py`

**New Feature**: Added argparse support for command-line queries

**Usage**:
```bash
# Auto-select provider (based on internet and config)
python3 query_handler.py "What is the oil pressure?"

# Force online AI (OpenRouter)
python3 query_handler.py --force-provider openrouter "What is the oil pressure?"

# Force onboard AI (Phi-2)
python3 query_handler.py --force-provider onboard "What is the oil pressure?"
```

**Implementation**:
```python
def main():
    """Test the query handler"""
    parser = argparse.ArgumentParser(description='d3kOS AI Query Handler')
    parser.add_argument('question', nargs='+', help='Question to ask the AI')
    parser.add_argument('--force-provider', choices=['openrouter', 'onboard'],
                       help='Force specific AI provider')
    args = parser.parse_args()

    question = " ".join(args.question)
    handler = AIQueryHandler()
    result = handler.query(question, force_provider=args.force_provider)
```

**Testing**:
```
$ python3 query_handler.py --force-provider openrouter "What is the function of the oil filter?"

Question: What is the function of the oil filter?
Processing...

Provider: openrouter
Model: openai/gpt-3.5-turbo
Response Time: 6271ms

Answer:
The oil filter is responsible for removing contaminants from the engine oil...
```

---

### 3. Wake Word Configuration

**File**: `/opt/d3kos/config/sphinx/wake-words.kws`

**Format**: PocketSphinx keyword file with threshold values

**Content**:
```
helm /1e-3/
advisor /1e-3/
counsel /1e-3/
```

**Threshold**: `1e-3` (conservative to reduce false positives)

**Wake Word Mapping**:
| Wake Word | AI Mode | Provider | Response |
|-----------|---------|----------|----------|
| **helm** | auto | Auto-select (internet-based) | "Aye Aye Captain" |
| **advisor** | onboard | Phi-2 (local) | "Aye Aye Captain" |
| **counsel** | online | OpenRouter (gpt-3.5-turbo) | "Aye Aye Captain" |

---

### 4. Voice Assistant v2

**File**: `/opt/d3kos/services/voice/voice-assistant-hybrid.py`

**Major Changes**:

#### 4.1 Wake Word Detection
**Method**: `detect_wake_word_once()`

**Before (Phase 1)**:
```python
result = subprocess.run(
    ["pocketsphinx_continuous", "-inmic", "yes", "-keyphrase", "helm", "-kws_threshold", "1e-3"],
    ...
)
```

**After (Phase 2)**:
```python
process = subprocess.Popen(
    ["pocketsphinx_continuous",
     "-inmic", "yes",
     "-kws", WAKE_WORDS_FILE,  # Use keyword file
     "-logfn", "/dev/null"],
    ...
)

# Parse output to detect which wake word
for line in process.stdout:
    for word in ['helm', 'advisor', 'counsel']:
        if word in line.lower():
            return word  # Return detected wake word
```

#### 4.2 Wake Word Configuration Dictionary
```python
WAKE_WORDS = {
    'helm': {'ai': 'auto', 'response': 'Aye Aye Captain', 'provider': None},
    'advisor': {'ai': 'onboard', 'response': 'Aye Aye Captain', 'provider': 'onboard'},
    'counsel': {'ai': 'online', 'response': 'Aye Aye Captain', 'provider': 'openrouter'}
}
```

#### 4.3 AI Query Integration
**Method**: `query_ai(question, provider=None)`

**Replaces**: Old `process_command()` with rule-based responses and Phi-2

**New Implementation**:
```python
def query_ai(self, question, provider=None):
    """Query the AI handler with routing based on wake word"""
    cmd = ["python3", AI_QUERY_HANDLER]

    # Add force-provider argument if specified
    if provider:
        cmd.extend(["--force-provider", provider])

    cmd.append(question)

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    if result.returncode == 0:
        # Parse Answer: section from output
        answer = result.stdout.split("Answer:")[1].strip()
        return answer
```

#### 4.4 Main Loop with Acknowledgment
```python
wake_word = self.detect_wake_word_once()

if wake_word:
    config = WAKE_WORDS[wake_word]
    print(f"✓ Wake word detected: {wake_word.upper()}")

    # Speak acknowledgment: "Aye Aye Captain"
    self.speak(config['response'])

    time.sleep(0.5)  # Mic release

    command = self.listen()

    if command:
        # Route to AI based on wake word
        response = self.query_ai(command, config['provider'])
        self.speak(response)
```

---

## Testing Results

### Query Handler CLI
✅ Command-line argument parsing works
✅ `--force-provider openrouter` forces online AI
✅ `--force-provider onboard` forces onboard AI (placeholder)
✅ No argument uses auto-selection
✅ Response parsing successful
✅ Response time: 6-7 seconds for OpenRouter

### Wake Word File
✅ Keyword file created at `/opt/d3kos/config/sphinx/wake-words.kws`
✅ Contains all three wake words with thresholds
✅ File permissions correct (644)
✅ PocketSphinx can read the file

### Voice Assistant v2
✅ Dependencies check passes (including keyword file)
✅ Multiple wake word detection implemented
✅ "Aye Aye Captain" acknowledgment added
✅ AI query handler integration complete
✅ Provider routing based on wake word
✅ Error handling for timeouts and failures

**Note**: Full voice testing requires the voice service to be running on the Pi with microphone/speaker. The code has been deployed and is ready for live testing.

---

## File Locations

### Configuration
- `/opt/d3kos/config/ai-config.json` - AI provider config (Perplexity removed)
- `/opt/d3kos/config/sphinx/wake-words.kws` - PocketSphinx keyword file

### Services
- `/opt/d3kos/services/ai/query_handler.py` - v2 with CLI args
- `/opt/d3kos/services/voice/voice-assistant-hybrid.py` - v2 with multi-wake-word

### Documentation
- `/home/boatiq/Helm-OS/doc/PHASE_2_COMPLETE.md` - This file
- `/home/boatiq/Helm-OS/doc/UPDATES_2026-02-12.md` - Phase 1 completion

---

## Deployment Commands

### Remove Perplexity from Config
```bash
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237
sudo nano /opt/d3kos/config/ai-config.json
# (Manually remove "perplexity" section)
```

### Deploy Query Handler v2
```bash
scp -i ~/.ssh/d3kos_key query_handler_v2.py d3kos@192.168.1.237:/tmp/
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237 \
  "sudo mv /tmp/query_handler_v2.py /opt/d3kos/services/ai/query_handler.py && \
   sudo chmod +x /opt/d3kos/services/ai/query_handler.py"
```

### Create Wake Word File
```bash
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237
mkdir -p /opt/d3kos/config/sphinx
cat > /opt/d3kos/config/sphinx/wake-words.kws << 'EOF'
helm /1e-3/
advisor /1e-3/
counsel /1e-3/
EOF
```

### Deploy Voice Assistant v2
```bash
scp -i ~/.ssh/d3kos_key voice-assistant-v2.py d3kos@192.168.1.237:/tmp/
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237 \
  "sudo cp /tmp/voice-assistant-v2.py /opt/d3kos/services/voice/voice-assistant-hybrid.py && \
   sudo chmod +x /opt/d3kos/services/voice/voice-assistant-hybrid.py"
```

---

## Usage Examples

### Command-Line Testing
```bash
# Test auto-select
python3 /opt/d3kos/services/ai/query_handler.py "What is the engine RPM?"

# Test force online
python3 /opt/d3kos/services/ai/query_handler.py --force-provider openrouter \
  "What should I check before starting the engine?"

# Test force onboard (when implemented)
python3 /opt/d3kos/services/ai/query_handler.py --force-provider onboard \
  "What is the oil pressure?"
```

### Voice Assistant
```bash
# Start voice assistant (manual test)
python3 /opt/d3kos/services/voice/voice-assistant-hybrid.py --auto-start

# Expected flow:
# 1. Assistant says: "Voice assistant started. Say helm, advisor, or counsel to activate me."
# 2. User says: "Helm"
# 3. Assistant says: "Aye Aye Captain"
# 4. User says: "What is the engine temperature?"
# 5. Assistant queries AI and responds with answer
```

---

## Wake Word Behavior

### "Helm" (Auto-Select)
- **Routing**: Checks internet, uses OpenRouter if available, falls back to onboard
- **Use Case**: General queries, user doesn't care which AI
- **Response**: "Aye Aye Captain" → [listen] → [auto AI response]

### "Advisor" (Onboard Only)
- **Routing**: Forces onboard Phi-2 (local processing)
- **Use Case**: Privacy-sensitive queries, no internet available, faster response for simple questions
- **Response**: "Aye Aye Captain" → [listen] → [onboard AI response]

### "Counsel" (Online Only)
- **Routing**: Forces OpenRouter (gpt-3.5-turbo)
- **Use Case**: Complex queries requiring up-to-date knowledge, when quality matters more than speed
- **Response**: "Aye Aye Captain" → [listen] → [online AI response]

---

## Known Issues

### 1. Onboard AI Not Implemented
- **Status**: Placeholder only (Phase 3 pending)
- **Impact**: "Advisor" wake word will return placeholder response
- **Workaround**: Falls back to placeholder: "[Onboard AI] Response to: {question}"

### 2. Touchscreen-Voice Conflict
- **Status**: Pre-existing issue from Phase 1 (2026-02-11)
- **Impact**: Touchscreen stops working if voice service is stopped
- **Workaround**: Keep voice service disabled by default, restart Pi if needed
- **See**: `touchscreen-voice-conflict.md`

### 3. Voice Service Auto-Start Disabled
- **Status**: Intentional (due to touchscreen conflict)
- **Impact**: Voice assistant must be manually started
- **Control**: Dashboard toggle button at http://192.168.1.237/

---

## Phase 2 Completion Checklist

### ✅ Completed
- [x] Remove Perplexity from configuration
- [x] Remove Perplexity code from query handler
- [x] Add command-line argument support to query handler
- [x] Test `--force-provider openrouter`
- [x] Test `--force-provider onboard`
- [x] Create PocketSphinx keyword file
- [x] Update voice assistant to detect multiple wake words
- [x] Add "Aye Aye Captain" acknowledgment
- [x] Integrate voice assistant with AI query handler
- [x] Implement wake word routing (helm/advisor/counsel)
- [x] Deploy all files to d3kOS Pi
- [x] Test query handler CLI functionality
- [x] Document all changes

### ⏳ Pending (Future Phases)
- [ ] Phase 3: Implement Phi-2 onboard AI
- [ ] Test voice assistant with live microphone/speaker
- [ ] Verify all three wake words work correctly
- [ ] Measure response times for each wake word
- [ ] Phase 4: Document retrieval and skills.md population
- [ ] Phase 5: Web interface for text input
- [ ] Phase 6: Learning and memory features

---

## Next Steps (Phase 3)

**Goal**: Implement onboard Phi-2 AI for offline operation

**Tasks**:
1. Install llama.cpp on d3kOS Pi (if not already installed)
2. Download Phi-2 Q4_K_M model to `/opt/d3kos/models/phi2/`
3. Implement `query_onboard()` method in query_handler.py
4. Test onboard AI with sample questions
5. Verify "Advisor" wake word routes correctly
6. Measure response times (target: <60 seconds)
7. Optimize context compression for 2K token limit
8. Test automatic fallback when internet unavailable

---

## Performance Expectations

### Response Times by Wake Word
| Wake Word | Provider | Expected Time | Notes |
|-----------|----------|---------------|-------|
| **helm** | Auto (OpenRouter) | 6-8 seconds | When internet available |
| **helm** | Auto (Onboard) | 40-60 seconds | When internet unavailable |
| **advisor** | Onboard (Phi-2) | 40-60 seconds | Always uses local AI |
| **counsel** | Online (OpenRouter) | 6-8 seconds | Requires internet |

### Breakdown (Online - Counsel/Helm)
- Wake word detection: <1 second
- "Aye Aye Captain" TTS: ~1 second
- User speech (3 seconds listening): 3 seconds
- Vosk transcription: 2-3 seconds
- OpenRouter API call: 3-5 seconds
- Response TTS: 1-2 seconds
- **Total**: ~11-15 seconds

### Breakdown (Onboard - Advisor/Helm fallback)
- Wake word detection: <1 second
- "Aye Aye Captain" TTS: ~1 second
- User speech (3 seconds listening): 3 seconds
- Vosk transcription: 2-3 seconds
- Phi-2 inference: 40-50 seconds
- Response TTS: 1-2 seconds
- **Total**: ~48-60 seconds

---

## API Keys and Credentials

### OpenRouter
- **API Key**: `sk-or-v1-***REDACTED***`
- **Model**: openai/gpt-3.5-turbo
- **Status**: ✅ Active and working
- **Cost**: ~$0.001 per query

### GitHub
- **Token**: ghp_***REDACTED*** (not stored in public repository for security)
- **Status**: ✅ Active

---

## Version History

| Date | Phase | Version | Changes |
|------|-------|---------|---------|
| 2026-02-12 | 1 | 1.0 | Initial AI system (OpenRouter + Perplexity) |
| 2026-02-12 | 1 | 1.1 | Fixed OpenRouter model selection bug |
| 2026-02-12 | 2 | 2.0 | Removed Perplexity, added CLI args |
| 2026-02-12 | 2 | 2.1 | Three wake words + "Aye Aye Captain" |
| TBD | 3 | 3.0 | Onboard Phi-2 implementation |

---

## Contact & Support
- **System IP**: 192.168.1.237
- **SSH Access**: `ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237`
- **Query Handler**: `/opt/d3kos/services/ai/query_handler.py`
- **Voice Assistant**: `/opt/d3kos/services/voice/voice-assistant-hybrid.py`
- **Wake Words Config**: `/opt/d3kos/config/sphinx/wake-words.kws`

---

**Phase 2 Status**: ✅ COMPLETE
**Next Phase**: Phase 3 - Onboard Phi-2 Implementation
**Overall Progress**: 30% of total hybrid AI system
