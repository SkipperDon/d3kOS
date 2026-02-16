# Voice/AI Optimization Test Plan - Session 3
**Created:** 2026-02-16
**Session:** Session-3-Voice-AI-Optimization
**Status:** PENDING EXECUTION

## Changes Requiring Testing

### 1. Signal K Caching (signalk_client.py)
- 3-second TTL cache added
- Expected: 132× faster responses for cached queries

### 2. Persistent Handler Instance (ai_api.py)
- Global handler persists across requests
- Expected: Cache survives between API calls

### 3. Expanded Patterns (query_handler.py)
- Added 5 new patterns: boost, hours, location, time, help
- Expected: 13 total patterns, instant responses

### 4. Phi-2 Removal (query_handler.py)
- Removed Phi-2 LLM completely
- Expected: No 60-180s hangs, helpful messages for complex queries

---

## Test Plan

### Phase 1: API Endpoint Testing ✅ DONE

**Tested via curl:**
- ✅ Simple queries (rpm, oil, fuel, battery, speed, heading, temperature)
- ✅ New patterns (boost, hours, location, time, help)
- ✅ Cache performance (18s → 0.17s)
- ✅ Phi-2 removal (helpful message for complex queries)
- ✅ Service restart (no errors)

### Phase 2: Web Interface Testing ⏳ PENDING

**Test Location:** http://192.168.1.237/ai-assistant.html

**Test Cases:**

#### 2.1 Text Interface
- [ ] **Simple Query Test**
  - Input: "What's the RPM?"
  - Expected: "Engine RPM is X" in <0.5s
  - Test: rpm, oil, fuel, battery, speed, heading, temperature
  
- [ ] **New Pattern Test**
  - Input: "What time is it?"
  - Expected: Current time in <0.5s
  - Test: time, help, boost, hours, location

- [ ] **Cache Test**
  - Query 1: "rpm" (should take ~18s first time)
  - Query 2: "oil" (should take ~0.2s - cached)
  - Query 3: "fuel" (should take ~0.2s - cached)
  - Wait 4 seconds
  - Query 4: "battery" (should take ~18s - cache expired)

- [ ] **Complex Query Test**
  - Input: "Why is my engine overheating?"
  - Expected: Online AI response OR helpful offline message
  - Test with internet ON and OFF

#### 2.2 Provider Selection
- [ ] **Auto Mode** (default)
  - Simple query → Should use rules (instant)
  - Complex query → Should use OpenRouter (if online)
  
- [ ] **Online Mode**
  - Any query → Should use OpenRouter
  - Expected: 6-8 second response time
  
- [ ] **Onboard Mode**
  - Simple query → Should use rules (instant)
  - Complex query → Should show helpful message

#### 2.3 UI Display
- [ ] Response displays correctly in chat area
- [ ] Loading indicator shows during processing
- [ ] Error messages display properly
- [ ] Response metadata shows (provider, model, time)
- [ ] On-screen keyboard works for input

### Phase 3: Voice Assistant Testing ⏳ PENDING

**Prerequisites:**
- Voice service must be started manually (disabled by default)
- Microphone (Anker S330) must be connected
- Speaker must be working

**Test Cases:**

#### 3.1 Wake Words
- [ ] **"Helm"** (auto mode)
  - Say: "Helm, what's the RPM?"
  - Expected: "Aye Aye Captain" → Fast response
  
- [ ] **"Advisor"** (onboard mode)
  - Say: "Advisor, what's the fuel level?"
  - Expected: "Aye Aye Captain" → Fast rule-based response
  
- [ ] **"Counsel"** (online mode)
  - Say: "Counsel, what should I check if oil pressure is low?"
  - Expected: "Aye Aye Captain" → Online AI response (6-8s)

#### 3.2 Voice Response Time
- [ ] Simple query via voice: Total time <10s (wake + listen + transcribe + AI + TTS)
- [ ] Complex query via voice: Total time <20s (with OpenRouter)

#### 3.3 Integration
- [ ] Voice responses use cached Signal K data
- [ ] Voice commands trigger correct provider
- [ ] TTS works for all response types

### Phase 4: OpenRouter Testing ⏳ PENDING

**Prerequisites:**
- Internet connection required
- OpenRouter API key must be valid

**Test Cases:**

#### 4.1 Complex Queries
- [ ] "Why is my engine making a knocking sound?"
  - Expected: Detailed AI response in 6-8s
  
- [ ] "How do I troubleshoot low oil pressure?"
  - Expected: Step-by-step guidance
  
- [ ] "What causes engine overheating?"
  - Expected: Comprehensive explanation

#### 4.2 Fallback Behavior
- [ ] Disconnect internet → Complex query → Should show offline message
- [ ] Reconnect internet → Complex query → Should use OpenRouter
- [ ] OpenRouter timeout → Should return error message

### Phase 5: Cache Behavior Testing ⏳ PENDING

**Test Cases:**

#### 5.1 Cache Hit
- [ ] First query: 18s (uncached)
- [ ] Second query within 3s: 0.17s (cached)
- [ ] Third query within 3s: 0.17s (cached)

#### 5.2 Cache Expiry
- [ ] Query 1: 18s
- [ ] Wait 4 seconds
- [ ] Query 2: 18s (cache expired, fresh fetch)

#### 5.3 Cache Persistence
- [ ] Query from Web UI: Creates cache
- [ ] Query from API: Uses same cache
- [ ] Verify cache survives across requests

### Phase 6: Error Handling Testing ⏳ PENDING

**Test Cases:**

#### 6.1 Signal K Down
- [ ] Stop Signal K service
- [ ] Query boat data
- [ ] Expected: Falls back to simulated values

#### 6.2 Internet Down
- [ ] Disconnect internet
- [ ] Complex query (onboard mode)
- [ ] Expected: Helpful offline message
- [ ] Simple query
- [ ] Expected: Works with cached/simulated data

#### 6.3 Invalid Input
- [ ] Empty query
- [ ] Very long query (>1000 chars)
- [ ] Special characters
- [ ] Expected: Graceful error handling

### Phase 7: Performance Testing ⏳ PENDING

**Test Cases:**

#### 7.1 Concurrent Requests
- [ ] 5 simultaneous queries
- [ ] Expected: All use same cache, fast responses
- [ ] No crashes or errors

#### 7.2 Memory Usage
- [ ] Check memory before: `free -h`
- [ ] Run 100 queries
- [ ] Check memory after
- [ ] Expected: No memory leaks

#### 7.3 Service Stability
- [ ] Run for 1 hour with queries every minute
- [ ] Expected: No crashes, consistent performance

### Phase 8: Integration Testing ⏳ PENDING

**Test Cases:**

#### 8.1 Signal K Integration
- [ ] Real boat data vs simulated
- [ ] Verify correct unit conversions
- [ ] Verify null handling for unavailable sensors

#### 8.2 Database Integration
- [ ] Queries stored in conversation-history.db
- [ ] Response times recorded correctly
- [ ] Provider/model tracked accurately

#### 8.3 Skills.md Context
- [ ] Verify context loaded on startup
- [ ] OpenRouter uses full context
- [ ] No errors with missing skills.md

---

## Test Execution Checklist

### Prerequisites
- [ ] Service running: `systemctl status d3kos-ai-api`
- [ ] No errors in logs: `journalctl -u d3kos-ai-api -n 50`
- [ ] Web interface accessible: http://192.168.1.237/ai-assistant.html
- [ ] Signal K running: `systemctl status signalk`

### Execution Order
1. ✅ Phase 1: API Endpoint Testing (COMPLETED)
2. ⏳ Phase 2: Web Interface Testing
3. ⏳ Phase 3: Voice Assistant Testing (optional - requires manual start)
4. ⏳ Phase 4: OpenRouter Testing
5. ⏳ Phase 5: Cache Behavior Testing
6. ⏳ Phase 6: Error Handling Testing
7. ⏳ Phase 7: Performance Testing
8. ⏳ Phase 8: Integration Testing

### Pass/Fail Criteria

**Pass:** All critical tests pass
- Web interface works
- Caching provides 50× speedup minimum
- No crashes or errors
- Response times within expected ranges

**Fail:** Any critical test fails
- Web interface broken
- Cache not working
- Frequent crashes
- Response times >10× slower than expected

---

## Test Results

### API Testing (Phase 1) - PASSED ✅
**Date:** 2026-02-16 10:15 AM
**Tester:** Claude Session 3
**Result:** ALL TESTS PASSED

| Test | Result | Time | Notes |
|------|--------|------|-------|
| Simple queries | ✅ PASS | 0.17-0.22s | All patterns working |
| New patterns | ✅ PASS | 0.17-0.22s | boost, hours, time, help, location |
| Cache performance | ✅ PASS | 18s → 0.17s | 100× improvement |
| Phi-2 removal | ✅ PASS | 0.17s | Helpful message for complex |
| Service restart | ✅ PASS | N/A | No errors |

### Remaining Tests - PENDING ⏳
**Status:** Awaiting execution
**Next:** Phase 2 (Web Interface Testing)
**Blocker:** None - ready to test

---

## Notes

**Quick Test Command (API):**
```bash
curl -s -X POST http://192.168.1.237:8080/ai/query \
  -H 'Content-Type: application/json' \
  -d '{"question": "rpm", "provider": "onboard"}' | jq
```

**Web Interface Test:**
1. Open http://192.168.1.237/ai-assistant.html
2. Type query in text box
3. Observe response time and content
4. Check browser console for errors (F12)

**Voice Test:**
1. Start voice: `sudo systemctl start d3kos-voice`
2. Say wake word + question
3. Listen for response
4. Stop voice when done (⚠️ don't stop - breaks touchscreen)
