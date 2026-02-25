# d3kOS Hybrid AI System - Complete Testing Checklist

**System**: d3kOS v2.0
**IP Address**: http://192.168.1.237/
**Test Date**: _______________
**Tester**: _______________

---

## Pre-Test Verification

- [ ] Raspberry Pi powered on and booted
- [ ] Display connected and showing boot screen
- [ ] Network connected (check IP: 192.168.1.237)
- [ ] Can access main menu: http://192.168.1.237/
- [ ] All 11 buttons visible on main menu

---

# PHASE 1: Online AI (OpenRouter)

## Test 1.1: API Configuration
**Purpose**: Verify OpenRouter API is configured

**Steps**:
1. SSH to Pi: `ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237`
2. Check config: `cat /opt/d3kos/config/ai-config.json`
3. Verify `openrouter.api_key` is set (starts with "sk-or-")

**Expected Result**: API key present
**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test 1.2: AI API Service Running
**Purpose**: Verify AI API service is active

**Steps**:
1. SSH to Pi
2. Run: `sudo systemctl status d3kos-ai-api`
3. Check status is "active (running)"

**Expected Result**: Service running on port 8080
**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test 1.3: Simple Online Query
**Purpose**: Test basic OpenRouter query

**Steps**:
1. Open: http://192.168.1.237/ai-assistant.html
2. Click "🌐 Online (6-8s)" button
3. Type: "What is 2 + 2?"
4. Click Send
5. Wait for response

**Expected Result**:
- Response within 10 seconds
- Answer: "4" or "2 + 2 = 4"
- Model shown: "gpt-3.5-turbo" or similar
- Response time: 6-8 seconds

**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test 1.4: Complex Online Query
**Purpose**: Test AI reasoning with OpenRouter

**Steps**:
1. In AI Assistant, ensure "Online" selected
2. Type: "What should I check before starting a marine diesel engine?"
3. Click Send

**Expected Result**:
- Detailed list of pre-start checks
- Mentions: fuel, oil, coolant, battery, etc.
- Response time: 6-10 seconds

**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test 1.5: Auto-Select Mode
**Purpose**: Test automatic provider selection

**Steps**:
1. Click "🔄 Auto" button
2. Type: "Hello"
3. Click Send

**Expected Result**:
- Selects online provider (if internet available)
- Response received
- Model displayed

**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

---

# PHASE 2: Voice Assistant with Wake Words

## Test 2.1: Voice Service Status
**Purpose**: Verify voice service configuration

**Steps**:
1. SSH to Pi
2. Run: `systemctl status d3kos-voice`

**Expected Result**: Service exists (may be disabled by default due to touchscreen conflict)
**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test 2.2: Voice Toggle Button
**Purpose**: Test voice on/off from dashboard

**Steps**:
1. Open: http://192.168.1.237/
2. Look for "VOICE OFF" button (top-right if present)
3. Click button to toggle

**Expected Result**: Button changes to "VOICE ON" (green) or stays off if disabled
**Status**: [ ] Pass [ ] Fail [ ] Not Present
**Notes**: _______________

## Test 2.3: Wake Word Detection (If Enabled)
**Purpose**: Test voice activation

**Prerequisites**: Voice service must be ON, microphone connected

**Steps**:
1. Ensure voice service running
2. Speak clearly: "Helm"
3. Wait 1-2 seconds
4. Ask: "What is the RPM?"

**Expected Result**:
- System detects "helm" wake word
- Listens for 3 seconds
- Processes question
- Speaks answer via speaker

**Status**: [ ] Pass [ ] Fail [ ] Skipped (Voice Disabled)
**Notes**: _______________

## Test 2.4: Voice Model Files
**Purpose**: Verify voice models installed

**Steps**:
1. SSH to Pi
2. Run: `ls -lh /opt/d3kos/models/vosk/`
3. Run: `ls -lh /opt/d3kos/models/piper/`

**Expected Result**:
- Vosk model present (~40MB)
- Piper model present (~10-20MB)

**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

---

# PHASE 3: Onboard AI (Hybrid System)

## Test 3.1: Phi-2 Model Present
**Purpose**: Verify onboard AI model installed

**Steps**:
1. SSH to Pi
2. Run: `ls -lh /opt/d3kos/models/phi2/phi-2.Q4_K_M.gguf`

**Expected Result**: File exists, size ~1.7GB
**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test 3.2: llama.cpp Binary
**Purpose**: Verify inference engine available

**Steps**:
1. SSH to Pi
2. Run: `ls -lh /home/d3kos/llama.cpp/build/bin/llama-cli`

**Expected Result**: Binary exists and is executable
**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test 3.3: Rule-Based Response (Fast)
**Purpose**: Test simple onboard query with rules

**Steps**:
1. Open: http://192.168.1.237/ai-assistant.html
2. Click "💻 Onboard (5-60s)" button
3. Type: "What is the engine RPM?"
4. Click Send

**Expected Result**:
- Response within 10 seconds
- Answer: "Engine RPM is 0" (or current RPM value)
- Model: "phi-2-rules"
- Message: "⚡ Using fast rule-based response"

**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test 3.4: Multiple Rule Categories
**Purpose**: Test different rule patterns

**Test Each**:
- [ ] "What is the oil pressure?" → "Oil pressure is X PSI"
- [ ] "What is the temperature?" → "Coolant temperature is X degrees"
- [ ] "What is the fuel level?" → "Fuel level is X percent"
- [ ] "What is the status?" → Full status summary

**Expected Result**: All return rule-based responses < 10 seconds
**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test 3.5: Phi-2 LLM Fallback (Slow)
**Purpose**: Test full LLM for complex queries

**⚠️ WARNING**: This test takes 60-180 seconds

**Steps**:
1. Select "💻 Onboard"
2. Type: "Explain how a marine diesel engine works"
3. Click Send
4. Wait patiently (2-3 minutes)

**Expected Result**:
- Message: "⏳ Using onboard Phi-2 AI (this may take 2-3 minutes)"
- Response after 60-180 seconds
- Model: "phi-2"
- Answer attempts to explain (may be incomplete due to 50-token limit)

**Status**: [ ] Pass [ ] Fail [ ] Skipped (Too Slow)
**Notes**: _______________

---

# PHASE 4.1: Signal K Integration

## Test 4.1.1: Signal K Server Running
**Purpose**: Verify Signal K server active

**Steps**:
1. SSH to Pi
2. Run: `sudo systemctl status signalk`

**Expected Result**: Service active (running)
**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test 4.1.2: Signal K Web Interface
**Purpose**: Test Signal K dashboard access

**Steps**:
1. Open: http://192.168.1.237:3000/
2. Check for Signal K interface

**Expected Result**: Signal K dashboard loads
**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test 4.1.3: Signal K API Data
**Purpose**: Verify API returns boat data

**Steps**:
1. Open: http://192.168.1.237:3000/signalk/v1/api/vessels/self/propulsion/port/revolutions
2. Check JSON response

**Expected Result**: JSON with RPM data (value field)
**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test 4.1.4: SignalK Client Module
**Purpose**: Test Python client can read data

**Steps**:
1. SSH to Pi
2. Run: `cd /opt/d3kos/services/ai && python3 signalk_client.py`

**Expected Result**:
- Displays boat status JSON
- RPM value shown (0 if engine off)
- Other fields show null or values

**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test 4.1.5: AI Query with Real Sensor Data
**Purpose**: Verify AI uses live Signal K data

**Steps**:
1. Open AI Assistant
2. Select "Onboard"
3. Ask: "What is the RPM?"
4. Note the RPM value
5. Check Signal K: http://192.168.1.237:3000/signalk/v1/api/vessels/self/propulsion/port/revolutions
6. Compare values

**Expected Result**: AI answer matches Signal K API value
**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

---

# PHASE 4.2: Document Retrieval

## Test 4.2.1: Upload API Service
**Purpose**: Verify upload service running

**Steps**:
1. SSH to Pi
2. Run: `sudo systemctl status d3kos-upload`

**Expected Result**: Service active on port 8081
**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test 4.2.2: Upload Page Access
**Purpose**: Test upload interface loads

**Steps**:
1. Open: http://192.168.1.237/upload-manual.html
2. Check page displays correctly

**Expected Result**:
- Form with manual type dropdown
- File picker button
- Upload button
- Info box explaining process

**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test 4.2.3: Main Menu Upload Button
**Purpose**: Test navigation to upload page

**Steps**:
1. Open: http://192.168.1.237/
2. Click "Upload Manual" button
3. Verify redirects to upload-manual.html

**Expected Result**: Upload page loads
**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test 4.2.4: Manuals Directory
**Purpose**: Verify storage directory exists

**Steps**:
1. SSH to Pi
2. Run: `ls -ld /opt/d3kos/data/manuals`

**Expected Result**: Directory exists, owned by d3kos user
**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test 4.2.5: skills.md File
**Purpose**: Verify knowledge base file exists

**Steps**:
1. SSH to Pi
2. Run: `cat /opt/d3kos/config/skills.md`

**Expected Result**: File exists with template content
**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test 4.2.6: PDF Upload Test (Requires PDF)
**Purpose**: Test complete upload workflow

**⚠️ REQUIRES**: A test PDF file

**Steps**:
1. Open upload page
2. Select manual type: "Engine Manual"
3. Click "Choose PDF File"
4. Select a PDF file
5. Click "Upload and Process Manual"
6. Wait for success message

**Expected Result**:
- Success message appears
- File saved to /opt/d3kos/data/manuals/
- Content extracted to skills.md

**Status**: [ ] Pass [ ] Fail [ ] Skipped (No PDF)
**Notes**: _______________

## Test 4.2.7: Reject Non-PDF Files
**Purpose**: Verify only PDFs accepted

**Steps**:
1. Try to upload a .txt or .jpg file
2. Click Upload

**Expected Result**: Error message "Only PDF files are allowed"
**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

---

# PHASE 5: Web Text Interface

## Test 5.1: AI Assistant Page
**Purpose**: Test main chat interface

**Steps**:
1. Open: http://192.168.1.237/ai-assistant.html
2. Verify page layout

**Expected Result**:
- Top nav with "← Main Menu"
- Title: "AI Assistant"
- Three provider buttons (Auto/Online/Onboard)
- Text input area
- Send button
- Welcome message

**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test 5.2: Provider Selection
**Purpose**: Test switching AI providers

**Steps**:
1. Click each provider button
2. Verify button highlights (green background)

**Test Each**:
- [ ] "🔄 Auto" button activates
- [ ] "🌐 Online (6-8s)" button activates
- [ ] "💻 Onboard (5-60s)" button activates

**Expected Result**: Active button shows green background
**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test 5.3: Text Input Auto-Resize
**Purpose**: Test input box expands with text

**Steps**:
1. Type a short question (1 line)
2. Type a long question (multiple lines)
3. Verify input box height adjusts

**Expected Result**: Box grows to fit text, max 150px
**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test 5.4: Enter Key to Send
**Purpose**: Test keyboard shortcut

**Steps**:
1. Type a question
2. Press Enter key

**Expected Result**: Question sends (no Shift+Enter needed)
**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test 5.5: Loading Indicator
**Purpose**: Test visual feedback during processing

**Steps**:
1. Send any question
2. Watch for "Thinking..." message

**Expected Result**: Loading indicator appears while waiting
**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test 5.6: Response Display
**Purpose**: Test answer formatting

**Steps**:
1. Send a question
2. Receive answer
3. Check answer card

**Expected Result**:
- Answer appears in left-aligned card
- Shows model name (e.g., "🤖 gpt-3.5-turbo")
- Shows response time (e.g., "⏱️ 7.2s")
- "Assistant" label shown

**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test 5.7: Multiple Conversations
**Purpose**: Test chat history accumulation

**Steps**:
1. Send 3 different questions
2. Verify all appear on screen

**Expected Result**: All Q&A pairs visible, stacked vertically
**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test 5.8: Main Menu Integration
**Purpose**: Test navigation to AI Assistant

**Steps**:
1. Open main menu
2. Click "AI Assistant" button

**Expected Result**: ai-assistant.html loads
**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

---

# PHASE 6: Learning and Memory

## Test 6.1: History API Service
**Purpose**: Verify history service running

**Steps**:
1. SSH to Pi
2. Run: `sudo systemctl status d3kos-history`

**Expected Result**: Service active on port 8082
**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test 6.2: Conversation Database
**Purpose**: Verify database exists and has data

**Steps**:
1. SSH to Pi
2. Run:
```bash
python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('/opt/d3kos/data/conversation-history.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM conversations')
print(f"Total conversations: {cursor.fetchone()[0]}")
conn.close()
EOF
```

**Expected Result**: Shows conversation count (should be > 0 if any queries made)
**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test 6.3: History Page Access
**Purpose**: Test history viewer loads

**Steps**:
1. Open: http://192.168.1.237/history.html
2. Verify page displays

**Expected Result**:
- Top nav with "← Main Menu"
- Title: "Conversation History"
- Filter buttons (All/Online/Onboard)
- Search box
- Stats bar showing counts
- List of conversations (if any exist)

**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test 6.4: History Filter Buttons
**Purpose**: Test conversation filtering

**Steps**:
1. Open history page
2. Click "Online Only" button
3. Click "Onboard Only" button
4. Click "All" button

**Expected Result**: List filters based on selection, button highlights
**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test 6.5: History Search
**Purpose**: Test search functionality

**Steps**:
1. Open history page
2. Type keyword in search box (e.g., "RPM")
3. Verify list filters

**Expected Result**: Only matching conversations shown
**Status**: [ ] Pass [ ] Fail [ ] Skipped (No Conversations)
**Notes**: _______________

## Test 6.6: Copy Conversation
**Purpose**: Test copy to clipboard

**Steps**:
1. Open history page
2. Click "📋 Copy" on any conversation
3. Paste into notepad

**Expected Result**:
- Alert: "Copied to clipboard!"
- Clipboard contains: "Q: [question]\n\nA: [answer]"

**Status**: [ ] Pass [ ] Fail [ ] Skipped (No Conversations)
**Notes**: _______________

## Test 6.7: Re-ask Question
**Purpose**: Test question prefill from history

**Steps**:
1. Open history page
2. Click "🔄 Re-ask" on any conversation
3. Verify AI assistant opens
4. Check input box

**Expected Result**:
- AI assistant page loads
- Question pre-filled in input box
- Can edit or send immediately

**Status**: [ ] Pass [ ] Fail [ ] Skipped (No Conversations)
**Notes**: _______________

## Test 6.8: Delete Conversation
**Purpose**: Test conversation removal

**Steps**:
1. Note total conversation count
2. Click "🗑️ Delete" on any conversation
3. Confirm deletion
4. Verify list updates

**Expected Result**:
- Confirmation dialog appears
- After confirm, conversation removed from list
- Count decremented by 1

**Status**: [ ] Pass [ ] Fail [ ] Skipped (No Conversations)
**Notes**: _______________

## Test 6.9: Manuals Page Access
**Purpose**: Test manual manager loads

**Steps**:
1. Open: http://192.168.1.237/manuals.html
2. Verify page displays

**Expected Result**:
- Top nav with "← Main Menu"
- Title: "Manage Manuals"
- "Upload New Manual" button
- Manual count display
- List of manuals (or empty state if none)

**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test 6.10: Manual List Display
**Purpose**: Test manual information shown

**Prerequisites**: At least one PDF uploaded

**Steps**:
1. Open manuals page
2. Check manual cards

**Expected Result**: Each manual shows:
- 📄 Filename
- 📦 File size
- 📅 Upload date
- 🗑️ Delete button

**Status**: [ ] Pass [ ] Fail [ ] Skipped (No Manuals)
**Notes**: _______________

## Test 6.11: Delete Manual
**Purpose**: Test manual removal

**Prerequisites**: At least one PDF uploaded

**Steps**:
1. Click "🗑️ Delete" on any manual
2. Confirm deletion
3. Verify list updates

**Expected Result**:
- Confirmation dialog with warning
- After confirm, manual removed from list
- PDF file deleted from /opt/d3kos/data/manuals/

**Status**: [ ] Pass [ ] Fail [ ] Skipped (No Manuals)
**Notes**: _______________

## Test 6.12: Main Menu Integration
**Purpose**: Test navigation to history/manuals

**Steps**:
1. Open main menu
2. Click "History" button → verify history.html loads
3. Return to main menu
4. Click "Manage Manuals" button → verify manuals.html loads

**Expected Result**: Both navigation paths work
**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test 6.13: Skills.md Context in Queries
**Purpose**: Verify AI uses uploaded manual content

**Prerequisites**: Manual uploaded with specifications

**Steps**:
1. Upload a manual containing boat specs (e.g., "Displacement: 5.7L")
2. Wait 30 seconds
3. Open AI Assistant, select "Online"
4. Ask: "What is the engine displacement?"
5. Check if answer references the manual

**Expected Result**: AI answer includes specification from uploaded manual
**Status**: [ ] Pass [ ] Fail [ ] Skipped (No Manual with Specs)
**Notes**: _______________

---

# SYSTEM INTEGRATION TESTS

## Test INT-1: Service Startup Order
**Purpose**: Verify all services start correctly on boot

**Steps**:
1. Reboot the Pi: `sudo reboot`
2. Wait 2-3 minutes for boot
3. Check all services:
```bash
sudo systemctl status d3kos-ai-api
sudo systemctl status d3kos-upload
sudo systemctl status d3kos-history
sudo systemctl status signalk
```

**Expected Result**: All services "active (running)"
**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test INT-2: Port Availability
**Purpose**: Verify no port conflicts

**Steps**:
1. SSH to Pi
2. Run: `sudo netstat -tlnp | grep -E '(1880|3000|8080|8081|8082)'`

**Expected Result**: All ports listening:
- 1880: Node-RED
- 3000: Signal K
- 8080: AI API
- 8081: Upload API
- 8082: History API

**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test INT-3: Nginx Proxy Configuration
**Purpose**: Test all proxy routes work

**Steps**:
Test each endpoint:
1. `curl http://192.168.1.237/ai/query` (expect 405 Method Not Allowed for GET)
2. `curl http://192.168.1.237/upload/manual` (expect 405 or error)
3. `curl http://192.168.1.237/history/conversations` (expect JSON)
4. `curl http://192.168.1.237/signalk/v1/api/` (expect Signal K response)

**Expected Result**: All routes respond (not 404)
**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test INT-4: Main Menu Complete
**Purpose**: Verify all navigation buttons work

**Test Each Button**:
- [ ] Dashboard → dashboard.html
- [ ] Benchmark → benchmark.html (may not exist)
- [ ] Navigation → navigation.html
- [ ] Boat Log → boatlog.html
- [ ] Charts → OpenCPN launch attempt
- [ ] Initial Setup → onboarding.html
- [ ] QR Code → qrcode.html
- [ ] Settings → settings.html
- [ ] Helm → helm.html
- [ ] AI Assistant → ai-assistant.html
- [ ] Upload Manual → upload-manual.html
- [ ] Manage Manuals → manuals.html
- [ ] History → history.html

**Expected Result**: All buttons navigate correctly
**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test INT-5: End-to-End AI Query Flow
**Purpose**: Test complete query from web to response

**Steps**:
1. Open AI Assistant
2. Select "Online"
3. Ask: "What is the current RPM?"
4. Verify:
   - Question sent to /ai/query
   - query_handler.py loads skills.md
   - Signal K data retrieved
   - OpenRouter API called
   - Response stored in database
   - Answer displayed in browser

**Expected Result**: Complete flow succeeds, answer shown
**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test INT-6: Data Persistence After Reboot
**Purpose**: Verify data survives reboot

**Steps**:
1. Note current conversation count
2. Note current manual count
3. Reboot Pi: `sudo reboot`
4. Wait for boot
5. Check conversation count (history page)
6. Check manual count (manuals page)

**Expected Result**: Counts unchanged after reboot
**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

---

# PERFORMANCE TESTS

## Test PERF-1: Online Query Response Time
**Purpose**: Measure typical online AI response time

**Steps**:
1. Open AI Assistant, select "Online"
2. Ask 5 different simple questions
3. Record response times

**Test Results**:
1. _____ seconds
2. _____ seconds
3. _____ seconds
4. _____ seconds
5. _____ seconds
Average: _____ seconds

**Expected Result**: Average 6-10 seconds
**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test PERF-2: Onboard Rule Response Time
**Purpose**: Measure onboard rule-based response time

**Steps**:
1. Select "Onboard"
2. Ask 5 different rule-matched questions (RPM, oil, temp, fuel, status)
3. Record response times

**Test Results**:
1. _____ seconds
2. _____ seconds
3. _____ seconds
4. _____ seconds
5. _____ seconds
Average: _____ seconds

**Expected Result**: Average 5-10 seconds
**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test PERF-3: History Page Load Time
**Purpose**: Measure page load performance

**Steps**:
1. Open browser dev tools (F12)
2. Go to Network tab
3. Open: http://192.168.1.237/history.html
4. Note load time

**Measured Time**: _____ ms

**Expected Result**: < 500ms
**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test PERF-4: Database Query Performance
**Purpose**: Measure conversation retrieval speed

**Steps**:
1. Open history page
2. Open browser dev tools → Network tab
3. Find /history/conversations request
4. Note response time

**Measured Time**: _____ ms

**Expected Result**: < 100ms
**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

---

# STRESS TESTS

## Test STRESS-1: Concurrent Queries
**Purpose**: Test handling multiple simultaneous requests

**Steps**:
1. Open 3 browser tabs to AI Assistant
2. In each tab, send a question simultaneously
3. Verify all get responses

**Expected Result**: All 3 queries complete successfully
**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test STRESS-2: Large Conversation History
**Purpose**: Test history page with many conversations

**Steps**:
1. Send 20-30 AI queries
2. Open history page
3. Check performance (scrolling, filtering, searching)

**Expected Result**: Page remains responsive with large dataset
**Status**: [ ] Pass [ ] Fail [ ] Skipped
**Notes**: _______________

## Test STRESS-3: Large PDF Upload
**Purpose**: Test upload with maximum file size

**Steps**:
1. Try uploading a 40-50 MB PDF
2. Monitor upload progress
3. Verify processing completes

**Expected Result**: Upload succeeds (max 50MB)
**Status**: [ ] Pass [ ] Fail [ ] Skipped
**Notes**: _______________

---

# ERROR HANDLING TESTS

## Test ERR-1: Internet Disconnected
**Purpose**: Test fallback when no internet

**Steps**:
1. Disconnect Pi from internet
2. Try online query
3. Verify fallback to onboard

**Expected Result**: Automatic fallback, user notified
**Status**: [ ] Pass [ ] Fail [ ] Skipped
**Notes**: _______________

## Test ERR-2: Invalid Query
**Purpose**: Test handling of empty/invalid input

**Steps**:
1. Try sending empty message
2. Try sending only spaces

**Expected Result**: No error, request ignored or handled gracefully
**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test ERR-3: API Service Down
**Purpose**: Test behavior when service stopped

**Steps**:
1. Stop AI service: `sudo systemctl stop d3kos-ai-api`
2. Try sending query
3. Check error message
4. Restart: `sudo systemctl start d3kos-ai-api`

**Expected Result**: Clear error message to user
**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

## Test ERR-4: Database Corruption Protection
**Purpose**: Verify database handles errors gracefully

**Steps**:
1. Send a query that should be stored
2. Verify it appears in history
3. Try deleting non-existent conversation ID

**Expected Result**: Delete fails gracefully with error message
**Status**: [ ] Pass [ ] Fail
**Notes**: _______________

---

# SUMMARY

## Pass/Fail Totals

**Phase 1 (Online AI)**: _____ Pass / _____ Fail / _____ Total
**Phase 2 (Voice)**: _____ Pass / _____ Fail / _____ Total
**Phase 3 (Onboard AI)**: _____ Pass / _____ Fail / _____ Total
**Phase 4.1 (Signal K)**: _____ Pass / _____ Fail / _____ Total
**Phase 4.2 (Documents)**: _____ Pass / _____ Fail / _____ Total
**Phase 5 (Web Interface)**: _____ Pass / _____ Fail / _____ Total
**Phase 6 (Memory)**: _____ Pass / _____ Fail / _____ Total
**Integration Tests**: _____ Pass / _____ Fail / _____ Total
**Performance Tests**: _____ Pass / _____ Fail / _____ Total
**Stress Tests**: _____ Pass / _____ Fail / _____ Total
**Error Tests**: _____ Pass / _____ Fail / _____ Total

**OVERALL**: _____ Pass / _____ Fail / _____ Total

## Critical Issues Found

1. _____________________________________
2. _____________________________________
3. _____________________________________

## Non-Critical Issues Found

1. _____________________________________
2. _____________________________________
3. _____________________________________

## Overall System Status

[ ] PASS - System ready for production use
[ ] CONDITIONAL PASS - Minor issues, usable
[ ] FAIL - Critical issues, needs work

## Tester Signature

Tested By: _____________________
Date: _____________________
Signature: _____________________

---

## Additional Notes

_____________________________________
_____________________________________
_____________________________________
_____________________________________
_____________________________________
_____________________________________

---

**End of Testing Checklist**
