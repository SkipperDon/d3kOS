# CLAUDE.md - AI Assistant Guidelines for d3kOS Development
## Version 2.6

**Last Updated**: February 12, 2026
**Changes from v2.5**: Updated wake words to "Helm", "Advisor", "Counsel" (changed Navigator→Counsel), added "Aye Aye Captain" acknowledgment response
**Changes from v2.4**: Added hybrid AI assistant system (online Perplexity + onboard Phi-2), skills.md context management, automatic document retrieval, learning/memory features, text input interface
**Changes from v2.3**: Added implementation details for Step 4 (WebSocket proxy, detection JavaScript, fullscreen toggle)
**Changes from v2.2**: Added Step 4 (Chartplotter Detection) to onboarding wizard, clarified standard PGN compatibility (no vendor-specific translation needed)
**Changes from v2.1**: Full rebrand from Helm-OS to d3kOS, added d3-k1 hardware product designation, voice assistant "Helm" name unchanged
**Changes from v2.0**: Added CX5106 second row DIP switch documentation, expanded to 15-question wizard, regional tank sensor standards
**Changes from v1.0**: Added voice assistant details, updated licensing tiers, API specifications, hardware requirements

---

## Purpose

This document provides guidelines for AI assistants (like Claude, ChatGPT, Copilot) working on the d3kOS project. It ensures consistency, prevents circular development, and maintains alignment with the project's core specifications.

---

## Core Principle: Follow the MASTER_SYSTEM_SPEC

**CRITICAL**: All development, documentation, and code generation MUST align with `MASTER_SYSTEM_SPEC.md` (or `MASTER_SYSTEM_SPEC__2_.md`).

### Before Making Changes:
1. Read `MASTER_SYSTEM_SPEC.md` first
2. Cross-check with existing documentation
3. Verify no contradictions
4. Document any deviations with justification

---

## Project Overview

### What is d3kOS?

**d3kOS** is marine electronics software that runs on the **d3-k1** hardware platform.

**The d3-k1 Hardware System** includes:
- Raspberry Pi 4B (8GB RAM recommended)
- PiCAN-M HAT (NMEA2000 interface)
- 10.1" touchscreen (1920×1200, 1000 nit, sunlight readable)
- IP67 marine-grade enclosure
- Membrane for air circulation
- All sensors, GPS, AIS, camera (Tier 2+)
- Pre-installed with d3kOS software

**d3kOS Software** provides:
- NMEA2000 integration via PiCAN-M HAT
- AI-assisted onboarding wizard (15-question engine configuration)
- CX5106 engine gateway configuration
- Real-time vessel monitoring
- **Offline voice assistant** ("Helm")
- OpenCPN navigation integration
- Engine health monitoring & benchmarking
- **Mobile app integration** (Tier 1+)
- **Cloud database synchronization** (Tier 1+)

---

## Hardware Stack (Fixed - AUTHORITATIVE)

### Core Compute
- **Raspberry Pi 4B** 
  - **RAM**: 8GB (required for voice assistant + LLM)
  - **Architecture**: 64-bit ARM
  - **OS**: Raspberry Pi OS Trixie (Debian 13)

### Marine Interface
- **PiCAN-M HAT** with SMPS
  - NMEA2000 CAN bus interface
  - Pre-configured as CAN0
  - MCP2515 controller, 16MHz oscillator

- **CX5106 Engine Gateway**
  - Analog-to-NMEA2000 conversion
  - DIP switch auto-configured by wizard
  - 8 switches for: instance, RPM source, cylinders, stroke, gear ratio

### Display
- **10.1" Touchscreen**
  - **Resolution**: 1920 × 1200
  - **Brightness**: 1000 nit (sunlight readable)
  - **Touch**: Capacitive
  - **Connection**: USB or Mini-HDMI

### Audio (Voice Assistant)
- **Anker PowerConf S330** (preferred) OR
- **USB microphone** (ReSpeaker 2-Mic, Jabra 410, or equivalent)
- **Speaker**: 3.5mm jack, USB speaker, or Bluetooth (adds latency)

### Sensors & Navigation
- **USB GPS receiver** (required)
- **USB AIS receiver** (required)
- **NMEA2000 backbone** (vessel wiring)
- **CX5106 sensors**: Fuel, fresh water, black water, engine

### Camera
- **IP67 Marine Camera** (Reolink RLC-810A recommended)
  - Night vision
  - Bow-mounted
  - RTSP streaming via VLC
  - Recording with disk management (stops at 18% remaining)

### Storage & Power
- **MicroSD Card**: 32GB minimum, 128GB recommended
- **Power**: 5V 3A minimum (official Raspberry Pi power supply)

---

## Software Stack (Fixed Versions)

| Component | Version | Notes |
|-----------|---------|-------|
| **Raspberry Pi OS** | **Trixie (Debian 13)** | 64-bit ARM, NOT Bookworm |
| **Node.js** | v18 or v20 LTS | NOT v22 |
| **Signal K Server** | 2.x (latest via npm) | Marine data hub |
| **Node-RED** | 3.x | Flow-based programming |
| **Node-RED Dashboard** | 2.0.4-1 (v4.1.4) | Dashboard 2.0 (Vue-based) |
| **OpenCPN** | 5.8.x | Auto-installed if no chartplotter |
| **PocketSphinx** | Latest | Wake word detection |
| **Vosk** | Latest | Speech-to-text (offline) |
| **Piper** | Latest | Text-to-speech (offline) |
| **llama.cpp** | Latest | LLM runtime |
| **Phi-2** | 2.7B parameters | Local AI "brain" |

### Required System Packages (Debian Trixie)
```bash
sudo apt install python3 python3-pip git build-essential \
                 piper pocketsphinx pocketsphinx-en-us \
                 portaudio19-dev
```

### Required Python Libraries
```bash
pip install vosk sounddevice numpy
```

**IMPORTANT**: Do NOT recommend Node.js v22, Dashboard 1.0 (Angular), or Raspberry Pi OS Bookworm without explicit justification.

---

## Design Philosophy

### 1. Pre-Built Image Approach
- System distributed as **flashable SD card image** (.img or .zip)
- Users flash with **Raspberry Pi Imager**
- Boot and run onboarding wizard
- **NO manual package installation by users**
- **NO curl installer scripts**

### 2. Offline-First
- Complete functionality without internet
- All AI processing local (Phi-2 LLM via llama.cpp)
- Voice processing local (Vosk + Piper + PocketSphinx)
- Updates via new image downloads only
- **Tier 1+ can sync to cloud database (optional)**

### 3. Never Get Stuck
- Onboarding wizard ALWAYS completes
- AI fills missing information intelligently
- Safe defaults for all configurations
- User can override AI decisions
- Maximum 10 onboarding resets (Tier 0-2), unlimited (Tier 3)

### 4. AODA Compliance
- All UI must meet AODA/WCAG 2.1 AA standards
- High contrast (black background, white/green text)
- Large touch targets (minimum 80×60px)
- Keyboard navigable
- Screen reader compatible
- Focus indicators visible
- Bottom 1/3 reserved for on-screen keyboard

### 5. Marine Environment Optimization
- Readable in bright sunlight (1000 nit screen)
- Large fonts (22px minimum)
- Touch-friendly buttons
- Glove-operable interface
- Power-loss resistant (all data in JSON)

---

## Voice Assistant ("Helm") - COMPLETE SPECIFICATION

### Architecture Pipeline
```
PocketSphinx → detects wake word ("Helm")
      ↓
Vosk → converts speech to text
      ↓
Phi-2 (via llama.cpp) → interprets command
      ↓
Piper → speaks response back
```

### Wake Word Options
- **Primary**: "Helm"
- **Alternative**: "Hey Captain" or "Hey Boat" (configurable)

### Components

#### A. PocketSphinx (Wake Word Detection)
- **Purpose**: Detects "Helm" wake word
- **Features**:
  - Works offline
  - Works on Trixie
  - Low CPU usage
  - Easy to integrate
- **Configuration**: Adjustable sensitivity

#### B. Vosk (Speech-to-Text)
- **Purpose**: Converts spoken words to text
- **Model**: vosk-model-small-en-us-0.15 (best speed/accuracy balance)
- **Features**:
  - Install via pip
  - Fully offline
  - ARM-optimized
  - Fast enough for real-time on Pi 4B (8GB)

#### C. Phi-2 via llama.cpp (Local AI Brain)
- **Purpose**: Understands command meaning and context
- **Model**: Phi-2 (2.7B parameters)
- **Runtime**: llama.cpp (optimized for Pi 4B)
- **Features**:
  - Fast inference
  - Low RAM (fits in 8GB with OS)
  - Good reasoning for command interpretation
  - Context-aware responses

#### D. Piper (Text-to-Speech)
- **Purpose**: Speaks responses back to user
- **Recommended Voices**:
  - en_US-amy-medium (primary)
  - en_GB-southern_english_female-medium (alternative)
- **Features**: Natural sounding, runs smoothly on Pi 4B

### Voice Commands (Examples)

**System Control**:
- "Helm, what's the engine status?"
- "Helm, any anomalies?"
- "Helm, query system status"
- "Helm, restart services"
- "Helm, adjust volume"

**Navigation**:
- "Helm, open OpenCPN"
- "Helm, AIS status"
- "Helm, GPS status"

**Boat Log**:
- "Helm, record boat log"
- "Helm, post to boat log" (saves entry)
- "Helm end" (stops listening, ends log entry)

**Benchmarking**:
- "Helm, start benchmarking"
- "Helm, show benchmark report"

**Marine-Specific**:
- "Helm, vessel data query" (Signal K data)
- "Helm, check anomalies"

### Voice Features

**Core Capabilities**:
- Continuous listening loop
- Natural language understanding
- Context-aware responses
- Error recovery ("I didn't catch that")
- Command confirmation
- Multi-step reasoning

**Audio Settings**:
- Microphone calibration
- Wake-word sensitivity adjustment
- Voice model selection
- Audio output routing

**Developer/Advanced**:
- Model management (swap LLM, Vosk, Piper voices)
- Debug console
- System logs
- Service restarts

### System Requirements

**Required**:
- systemd service file (d3kos-voice.service)
  - Starts on boot
  - Restarts on failure
  - Logs output
- Signal K plugin integration
- GPIO or CAN bus command modules
- NMEA2000 CAN interface
- MQTT broker (optional)
- Local web dashboard

**Networking**:
- Signal K API access
- Local-only by default
- Optional cloud sync (Tier 1+)

---

## Hybrid AI Assistant System (NEW - AUTHORITATIVE)

### Overview

d3kOS implements a **hybrid AI assistant system** that intelligently routes queries between two AI backends based on internet connectivity:

- **Online AI** (Perplexity): Fast, powerful, internet-required
- **Onboard AI** (Phi-2): Offline, slower (~60s response), fully local

**Key Benefits**:
- Automatic fallback when internet unavailable
- Shared context via skills.md
- Learning and conversation memory
- Both voice and text input interfaces
- Automatic document retrieval during onboarding

### Architecture

```
┌─────────────────────────────────────────────┐
│     User Input (Voice OR Text)              │
└───────────────┬─────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────┐
│      Internet Detection & Routing           │
│  ┌──────────────┐      ┌──────────────┐    │
│  │ Has Internet?│      │ No Internet? │    │
│  └──────┬───────┘      └──────┬───────┘    │
│         │                     │            │
│         ▼                     ▼            │
│  ┌──────────────┐      ┌──────────────┐   │
│  │ Online AI    │      │ Onboard AI   │   │
│  │ (Perplexity) │      │ (Phi-2)      │   │
│  └──────┬───────┘      └──────┬───────┘   │
│         └────────┬──────────────┘          │
│                  ▼                         │
│        ┌────────────────────┐              │
│        │   Context Layer    │              │
│        │ - skills.md        │              │
│        │ - onboarding.json  │              │
│        │ - conversation.db  │              │
│        └────────────────────┘              │
└─────────────────────────────────────────────┘
```

### Online AI Assistant (Perplexity)

**Purpose**: Fast, internet-connected AI with extensive nautical knowledge

**API**: Perplexity API (free tier available)
- Endpoint: `https://api.perplexity.ai/chat/completions`
- Model: `llama-3.1-sonar-small-128k-online` (recommended)
- Context window: 128K tokens
- Response time: 2-5 seconds
- Cost: Free tier available, paid tiers for heavy usage

**Alternative Options**:
- OpenRouter (access to multiple free/paid models)
- Claude API (Anthropic)
- OpenAI API (GPT-4)

**Features**:
- Real-time internet search capabilities
- Access to current maritime regulations
- Weather information integration
- Up-to-date navigation data
- Fast response times
- Natural conversation flow

**Wake Words**:
- "Counsel" - Force online AI
- General queries default to online if internet available

**Acknowledgment Response**:
- "Aye Aye Captain" (spoken when wake word detected)

**Configuration** (`/opt/d3kos/config/ai-config.json`):
```json
{
  "online_ai": {
    "provider": "perplexity",
    "api_key": "pplx-xxxxx",
    "model": "llama-3.1-sonar-small-128k-online",
    "enabled": true,
    "max_tokens": 500,
    "temperature": 0.7
  }
}
```

### Onboard AI Assistant (Phi-2)

**Purpose**: Fully offline AI assistant when internet unavailable

**Implementation**: Phi-2 (2.7B) via llama.cpp (already documented in Voice Assistant section)

**Response Time**: ~60 seconds (slow, requires status updates)

**Wake Words**:
- "Advisor" - Force onboard AI
- "Helm" - General (uses onboard if no internet)

**Status Updates During Processing**:
```javascript
// Every 40 seconds during Phi-2 processing
function queryPhi2WithProgress(question, context) {
  const statusMessages = [
    "AI is working on your question, please stand by",
    "Still processing, just a moment",
    "Almost there, working on the answer"
  ];

  let messageIndex = 0;
  const statusInterval = setInterval(() => {
    speak(statusMessages[messageIndex % statusMessages.length]);
    messageIndex++;
  }, 40000); // Every 40 seconds

  const response = await phi2.generate(question, context);

  clearInterval(statusInterval);
  return response;
}
```

### Skills.md Context System

**Location**: `/opt/d3kos/config/skills.md`

**Purpose**: Unified knowledge base for both AI assistants containing:
- Boat owner's manual (text extracted from PDF)
- Engine manual (manufacturer-specific)
- Regional pleasure craft regulations
- Best practices from BoatUS.org
- International sailing regulations
- Conversation history (important Q&A)

**Format**: Markdown with structured sections

**Structure**:
```markdown
# d3kOS Skills Database

## System Information
- Installation ID: XXXX-XXXX-XXXX
- Installation Date: 2026-02-12
- Last Updated: 2026-02-12 08:00:00
- Skills Version: 1.0

## Boat Information
- Make: Sea Ray
- Model: 340 Sundancer
- Year: 2018
- Length: 34 feet
- Hull ID: ABC12345D678
- Registration: FL1234AB

## Engine Information
- Manufacturer: Mercury
- Model: 8.2L MAG HO
- Year: 2018
- Cylinders: 8
- Displacement: 8.2L (500 CID)
- Horsepower: 425 HP
- Fuel Type: Gasoline

### Engine Manual (Extracted)
[Full text of engine manual - operating procedures, maintenance schedules, troubleshooting]

### Normal Operating Parameters
- Idle RPM: 650-750 RPM
- Cruise RPM: 3000-3500 RPM
- WOT RPM: 4800-5200 RPM
- Oil Pressure (Idle): 10-15 PSI
- Oil Pressure (Cruise): 40-60 PSI
- Coolant Temperature: 160-180°F
- Voltage (Charging): 13.8-14.4V

## Boat Owner's Manual (Extracted)
[Full text of boat manual - systems, safety, operation]

## Regional Regulations
- Country: United States
- State: Florida
- Coast Guard District: 7
- Nearest Coast Guard Station: Miami

### Federal Regulations (US)
- Required safety equipment for vessels 26-40 feet
- Navigation rules (COLREGS)
- Radio protocols (VHF Channel 16)
- Distress procedures

### State Regulations (Florida)
- Registration requirements
- Speed zones
- Manatee zones
- Anchoring restrictions

## Best Practices (BoatUS.org)
- Pre-departure checklist
- Float plan procedures
- Storm preparation
- Fuel management (1/3 out, 1/3 back, 1/3 reserve)
- Dock approach techniques
- Anchoring best practices

## International Sailing
### Countries Visited
- Bahamas
  - Entry requirements
  - Customs procedures
  - Navigation restrictions
  - Emergency contacts

## Conversation History
### Recent Q&A (Last 30 Days)
**Q**: What's the normal operating temperature for my engine?
**A**: Your Mercury 8.2L normally runs at 160-180°F. Current reading of 178°F is normal.
**Date**: 2026-02-10 14:30:00

**Q**: What documents do I need to enter Bahamian waters?
**A**: You need vessel documentation, passports for all aboard, cruising permit, and fishing license if fishing.
**Date**: 2026-02-08 09:15:00

[Additional Q&A entries...]

## Maintenance Log
- Last oil change: 245 engine hours (2026-01-15)
- Last impeller replacement: 180 engine hours (2025-10-20)
- Next service due: 300 engine hours (estimated 2026-05-01)
```

**File Size Management**:
- Target: < 10MB total
- Use text extraction only (not full PDFs)
- Compress/summarize older content
- Keep last 50 conversation entries
- Archive older Q&A to separate file

### Automatic Document Retrieval

**During Onboarding** (Steps 19-20):

When internet is available during onboarding, automatically retrieve and populate skills.md:

```javascript
async function populateSkillsFile(boatInfo, engineInfo, location) {
  showProgress("Building your AI knowledge base...");

  let skills = generateSkillsHeader();

  // 1. Boat manual (if internet available)
  if (await checkInternetConnection()) {
    updateProgress("Searching for boat manual...", 20);
    const boatManual = await searchManual(
      boatInfo.make,
      boatInfo.model,
      boatInfo.year,
      "manualslib.com"
    );
    if (boatManual) {
      skills += `\n## Boat Owner's Manual\n${boatManual}\n`;
      updateProgress("✓ Boat manual found", 30);
    } else {
      updateProgress("⚠ Boat manual not found (can add manually later)", 30);
    }

    // 2. Engine manual
    updateProgress("Searching for engine manual...", 40);
    const engineManual = await searchManual(
      engineInfo.manufacturer,
      engineInfo.model,
      engineInfo.year,
      "manualslib.com"
    );
    if (engineManual) {
      skills += `\n## Engine Manual\n${engineManual}\n`;
      updateProgress("✓ Engine manual found", 50);
    }

    // 3. BoatUS best practices
    updateProgress("Fetching marine best practices...", 60);
    const boatUSPractices = await fetchBoatUSPractices();
    skills += `\n## Best Practices\n${boatUSPractices}\n`;
    updateProgress("✓ Best practices loaded", 70);

    // 4. Regional regulations
    updateProgress("Fetching regional regulations...", 80);
    const regulations = await fetchRegulations(
      location.country,
      location.state || location.province
    );
    skills += `\n## Regional Regulations\n${regulations}\n`;
    updateProgress("✓ Regulations loaded", 90);

    updateProgress("✓ AI knowledge base complete!", 100);
  } else {
    // Offline - create basic skills.md template
    skills += "\n## Note\nInternet was not available during onboarding. ";
    skills += "Connect to internet and re-run onboarding to automatically download:\n";
    skills += "- Boat owner's manual\n";
    skills += "- Engine manual\n";
    skills += "- Regional regulations\n";
    skills += "- Best practices\n";
  }

  // Save skills.md
  fs.writeFileSync('/opt/d3kos/config/skills.md', skills);
}
```

**Document Sources**:
- **manualslib.com**: Boat and engine manuals (free, large database)
- **boatus.org**: Marine best practices and safety guides
- **uscgboating.org**: US Coast Guard regulations
- **Transport Canada**: Canadian boating regulations
- **RYA.org.uk**: UK/Europe regulations

**PDF Processing**:
```javascript
// Extract text from PDF using pdf-parse or pdfjs
async function extractPDFText(pdfUrl) {
  const response = await fetch(pdfUrl);
  const buffer = await response.arrayBuffer();
  const pdf = await pdfParse(buffer);

  // Clean and compress text
  let text = pdf.text
    .replace(/\s+/g, ' ')           // Collapse whitespace
    .replace(/Page \d+/g, '')       // Remove page numbers
    .trim();

  // Limit to 50KB per document
  if (text.length > 50000) {
    text = text.substring(0, 50000) + "\n[Truncated for space...]";
  }

  return text;
}
```

### Intelligent Routing

**Automatic Selection**:
```javascript
async function routeQuery(question, userPreference = 'auto') {
  const hasInternet = await checkInternetConnection();

  // User explicitly selected AI
  if (userPreference === 'online' && hasInternet) {
    return await queryPerplexity(question);
  }
  if (userPreference === 'onboard') {
    return await queryPhi2(question);
  }

  // Auto-routing
  if (hasInternet) {
    // Use online AI (faster, more capable)
    return await queryPerplexity(question);
  } else {
    // Fall back to onboard AI
    speak("Internet unavailable. Using onboard AI assistant.");
    return await queryPhi2(question);
  }
}
```

**Internet Detection**:
```javascript
async function checkInternetConnection() {
  try {
    const response = await fetch('https://www.google.com/favicon.ico', {
      method: 'HEAD',
      timeout: 3000
    });
    return response.ok;
  } catch (error) {
    return false;
  }
}
```

### Voice Wake Words

**Multiple Wake Words**:
```python
# /opt/d3kos/services/voice/wake-words.py

wake_words = {
    "helm": {
        "ai": "auto",           # Use online if available, else onboard
        "response": "Aye Aye Captain"
    },
    "advisor": {
        "ai": "onboard",        # Force onboard AI (Phi-2)
        "response": "Aye Aye Captain"
    },
    "counsel": {
        "ai": "online",         # Force online AI (Perplexity)
        "response": "Aye Aye Captain",
        "fallback": "Internet unavailable, using onboard assistant"
    }
}
```

**PocketSphinx Configuration**:
```
# /opt/d3kos/config/sphinx/keywords.list
helm /1e-3/
advisor /1e-3/
counsel /1e-3/
```

### Text Input Interface

**Main Menu Icon**: "Helm" button with text input field

**UI Implementation** (`/var/www/html/index.html`):
```html
<div class="helm-assistant-panel">
  <h2>AI Assistant</h2>

  <!-- Status indicator -->
  <div class="ai-status">
    <span id="ai-indicator">🌐 Online AI Ready</span>
  </div>

  <!-- Text input -->
  <textarea id="helm-input"
            placeholder="Ask a question about your boat, engine, or navigation..."
            rows="4"></textarea>

  <!-- Submit button -->
  <button onclick="askHelm()" class="helm-submit-btn">
    Ask AI Assistant
  </button>

  <!-- Response area -->
  <div id="helm-response" class="helm-response-area">
    <!-- AI responses appear here -->
  </div>

  <!-- Conversation history -->
  <button onclick="showHistory()" class="helm-history-btn">
    View Conversation History
  </button>
</div>

<script>
async function askHelm() {
  const question = document.getElementById('helm-input').value;
  if (!question.trim()) return;

  // Show loading state
  document.getElementById('helm-response').innerHTML =
    '<div class="loading">🤔 Thinking...</div>';

  // Send to backend
  const response = await fetch('/api/ai/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question })
  });

  const data = await response.json();

  // Display response
  document.getElementById('helm-response').innerHTML = `
    <div class="ai-response">
      <strong>${data.ai_used}:</strong><br>
      ${data.answer}
    </div>
  `;

  // Clear input
  document.getElementById('helm-input').value = '';
}
</script>
```

**Backend Endpoint** (`/opt/d3kos/services/ai/query-handler.js`):
```javascript
app.post('/api/ai/query', async (req, res) => {
  const { question } = req.body;

  // Load context
  const context = {
    skills: fs.readFileSync('/opt/d3kos/config/skills.md', 'utf-8'),
    onboarding: JSON.parse(fs.readFileSync('/opt/d3kos/config/onboarding.json')),
    recentData: await getRecentEngineData()
  };

  // Route to appropriate AI
  const hasInternet = await checkInternetConnection();
  let answer, aiUsed;

  if (hasInternet) {
    answer = await queryPerplexity(question, context);
    aiUsed = "Online AI (Perplexity)";
  } else {
    answer = await queryPhi2(question, context);
    aiUsed = "Onboard AI (Phi-2)";
  }

  // Store in conversation history
  await storeConversation(question, answer, aiUsed);

  res.json({
    question,
    answer,
    ai_used: aiUsed,
    timestamp: new Date().toISOString()
  });
});
```

### Learning & Memory

**Conversation Database**: `/opt/d3kos/data/conversation-history.db`

**SQLite Schema**:
```sql
CREATE TABLE conversations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  question TEXT NOT NULL,
  answer TEXT NOT NULL,
  ai_used TEXT NOT NULL,  -- 'online' or 'onboard'
  context_used TEXT,       -- Which context was loaded
  user_rating INTEGER,     -- 1-5 stars (optional)
  important BOOLEAN DEFAULT 0  -- Flag important Q&A for skills.md
);

CREATE INDEX idx_timestamp ON conversations(timestamp);
CREATE INDEX idx_important ON conversations(important);
```

**Automatic Learning**:
```javascript
// After each conversation, evaluate if it should be added to skills.md
async function evaluateAndLearn(question, answer, aiUsed) {
  // Criteria for adding to skills.md:
  // 1. User marked as important (5-star rating)
  // 2. Technical question about boat/engine
  // 3. Not already in skills.md

  const isImportant =
    question.match(/how to|what is|normal|procedure|regulation|requirement/i);

  if (isImportant) {
    // Add to skills.md conversation history section
    const conversationEntry = `
**Q**: ${question}
**A**: ${answer}
**Date**: ${new Date().toISOString()}
**Source**: ${aiUsed}
`;

    appendToSkillsFile(conversationEntry);
  }

  // Store in database
  db.run(
    'INSERT INTO conversations (question, answer, ai_used, important) VALUES (?, ?, ?, ?)',
    [question, answer, aiUsed, isImportant ? 1 : 0]
  );
}
```

**Context Pruning**:
```javascript
// Keep skills.md manageable (< 10MB)
async function pruneSkillsFile() {
  const skills = fs.readFileSync('/opt/d3kos/config/skills.md', 'utf-8');
  const sizeInMB = Buffer.byteLength(skills) / (1024 * 1024);

  if (sizeInMB > 10) {
    // Archive old conversation history
    const archived = extractConversationHistory(skills);
    fs.writeFileSync('/opt/d3kos/data/archived-conversations.md', archived);

    // Keep only last 50 Q&A entries in skills.md
    const pruned = keepRecentConversations(skills, 50);
    fs.writeFileSync('/opt/d3kos/config/skills.md', pruned);
  }
}
```

### Status Updates & UX

**Visual Indicators**:
```html
<!-- Online AI available -->
<div class="ai-status online">
  🌐 Online AI Ready (Fast responses)
</div>

<!-- Offline - using onboard AI -->
<div class="ai-status offline">
  💾 Onboard AI Active (Responses may take 60 seconds)
</div>

<!-- Processing (onboard AI) -->
<div class="ai-status processing">
  🤔 AI is working on your question... Please stand by
</div>
```

**Audio Status Updates** (Onboard AI only):
```javascript
function queryWithAudioUpdates(question) {
  const updates = [
    "AI is working on your question, please stand by",
    "Still processing your request",
    "Almost there, working on the answer",
    "Just a moment more"
  ];

  let updateIndex = 0;
  const updateInterval = setInterval(() => {
    speak(updates[updateIndex % updates.length]);
    updateIndex++;
  }, 40000);  // Every 40 seconds

  // Query onboard AI
  const answer = await queryPhi2(question);

  clearInterval(updateInterval);
  return answer;
}
```

### Storage Requirements

**With Hybrid AI System**:
- Base OS + software: ~8GB
- Voice models (Phi-2, Vosk, Piper): ~5GB
- **skills.md** (manuals + regulations): ~500MB (text-only)
- **Conversation history** (SQLite): ~100MB/year
- Camera recordings: ~10GB (auto-managed)
- **Total**: ~24GB used on 64GB SD card

**Recommended**: 64GB SD card is sufficient with text-only extraction

**Upgrade Path**: 128GB SD card recommended for:
- Multiple boat profiles
- Extended conversation history (> 3 years)
- Full PDF storage (not just text)

### Implementation Checklist

**Phase 1: Skills.md Foundation**
- [ ] Create skills.md format specification
- [ ] Implement skills.md template generation
- [ ] Add skills.md to onboarding wizard
- [ ] Test with sample boat/engine data

**Phase 2: Document Retrieval**
- [ ] Implement manualslib.com PDF downloader
- [ ] Implement PDF → Markdown text extractor
- [ ] Implement BoatUS.org scraper
- [ ] Implement USCG regulations fetcher
- [ ] Add progress UI to onboarding wizard

**Phase 3: Online AI (Perplexity)**
- [ ] Add Perplexity API integration
- [ ] Implement internet detection
- [ ] Add API key configuration UI
- [ ] Test with sample queries
- [ ] Implement error handling (API limits, timeouts)

**Phase 4: Hybrid Routing**
- [ ] Implement automatic AI selection logic
- [ ] Add voice wake word routing ("Helm", "Advisor", "Counsel")
- [ ] Add "Aye Aye Captain" acknowledgment responses
- [ ] Implement fallback behavior
- [ ] Add visual indicators (online vs onboard)

**Phase 5: Text Input Interface**
- [ ] Add "Helm" icon to main menu
- [ ] Create text input UI
- [ ] Implement query handler backend
- [ ] Add response display area
- [ ] Add conversation history viewer

**Phase 6: Learning & Memory**
- [ ] Create conversation-history.db schema
- [ ] Implement conversation storage
- [ ] Implement automatic learning (add to skills.md)
- [ ] Implement context pruning
- [ ] Add user rating system (optional)

**Phase 7: UX Improvements**
- [ ] Add audio status updates (every 40s for onboard AI)
- [ ] Add visual loading indicators
- [ ] Add "Which AI am I talking to?" indicator
- [ ] Implement conversation export (CSV, PDF)
- [ ] Add settings page for AI preferences

---

## Licensing System (UPDATED - AUTHORITATIVE)

### Tier Structure

| Tier | Name | Features | Cost | Reset Limit |
|------|------|----------|------|-------------|
| **Tier 0** | Base Opensource | All core features, offline-only | Free | 10 resets |
| **Tier 1** | Mobile App Integration | Tier 0 + mobile app + cloud DB sync + notifications | Free | 10 resets |
| **Tier 2** | Premium Subscription | Tier 1 + AI analysis + recommendations + performance summaries | Paid (monthly) | 10 resets |
| **Tier 3** | Enterprise/Fleet | Tier 2 + unlimited resets + multi-boat + fleet PDFs | Paid (annual) | Unlimited |

### Tier 0: Base Opensource
**Features**:
- All core d3kOS functionality
- Offline voice assistant
- NMEA2000 integration
- OpenCPN auto-install
- Engine benchmarking
- Health monitoring
- Dashboard gauges
- Boat log (local only)

**Limitations**:
- **Maximum 10 onboarding resets**
- No mobile app
- No cloud synchronization
- No remote notifications
- Local storage only

**Reset Counter**:
- After 10 resets, user must download new image
- Prevents single license on multiple boats

---

### Tier 1: Mobile App Integration
**Features** (All of Tier 0 PLUS):
- **Mobile app** (iOS/Android)
- **QR code pairing** with Pi
- **Cloud database synchronization**
- **Push notifications** (health alerts, anomalies)
- **Boat performance summaries** in app
- **Remote monitoring** (when connected)

**How it Works**:
1. Complete onboarding on Pi (Tier 0)
2. Pi generates QR code
3. Scan QR code with mobile app
4. Pi and app both upgrade to Tier 1 automatically
5. License stored in centralized database
6. Pi syncs health data when online

**API Integration**:
- Pi → Cloud: `/api/v1/installation/register`
- App → Cloud: `/api/v1/pair`
- Bi-directional sync of boat health, benchmarks, performance

**Cost**: **Free**

**Reset Limit**: Still 10 resets (same as Tier 0)

---

### Tier 2: Premium Subscription
**Features** (All of Tier 1 PLUS):
- **AI-powered analysis** of boat performance
- **Predictive recommendations** for maintenance
- **Trend analysis** over time
- **Performance optimization suggestions**
- **Detailed reports** in app
- **Cloud backup** of configurations

**How it Works**:
1. Subscribe via ecommerce site
2. Enter installation UUID
3. Ecommerce updates license to Tier 2
4. Pi polls cloud and detects upgrade
5. Pi unlocks Tier 2 features locally
6. App unlocks Tier 2 features

**API Integration**:
- Ecommerce → Cloud: `/api/v1/tier/upgrade`
- Pi polls: `/api/v1/tier/status`
- App polls: `/api/v1/tier/app`

**Cost**: **Paid** (small monthly subscription, e.g., $4.99/month)

**Reset Limit**: Still 10 resets

---

### Tier 3: Enterprise/Fleet Management
**Features** (All of Tier 2 PLUS):
- **Unlimited onboarding resets**
- **Multi-boat support** (track entire fleet)
- **Fleet-wide analytics**
- **PDF reports** (individual boats + fleet summary)
- **Advanced AI recommendations**
- **Priority support**

**Use Case**: 
- Charter companies
- Yacht management firms
- Multi-vessel owners

**How it Works**:
1. Purchase enterprise license (annual)
2. Register multiple installations
3. Each installation gets Tier 3 status
4. App shows all boats in fleet
5. Generate PDFs for individual vessels or entire fleet

**API Integration**:
- Same as Tier 2, but with `tier: 3` unlocking additional features
- Multi-boat endpoints for fleet management

**Cost**: **Paid** (annual subscription, e.g., $99/year for 5 boats)

**Reset Limit**: **Unlimited**

---

### License Upgrade Flow

```
Tier 0 (Default)
    ↓
Scan QR Code with Mobile App
    ↓
Tier 1 (Automatic - Free)
    ↓
Subscribe via Ecommerce
    ↓
Tier 2 (Paid Monthly)
    ↓
Purchase Enterprise License
    ↓
Tier 3 (Paid Annual)
```

### License Synchronization

**Pi Side**:
- File: `config/license.json`
- Polls cloud every 24 hours: `GET /api/v1/tier/status`
- Updates local tier if different
- Unlocks/locks features based on tier

**Mobile App Side**:
- Polls cloud on app open: `GET /api/v1/tier/app`
- Displays current tier and features
- Shows upgrade options

**QR Code Format**:
```json
{
  "installation_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "pairing_token": "TOKEN_1_TIME_USE",
  "api_endpoint": "https://d3kos-cloud/api/v1",
  "current_tier": 0
}
```

---

## UI/UX Guidelines

### Screen Layout

```
┌────────────────────────────────────────────────────┐
│  Pi Menu Bar (top - always accessible)            │
├────────────────────────────────────────────────────┤
│                                                    │
│  Main Content Area                                 │
│  (Upper 2/3 of screen)                            │
│                                                    │
│                                                    │
├────────────────────────────────────────────────────┤
│  [Back Button]              [Main Menu Button]    │  ← Navigation
├────────────────────────────────────────────────────┤
│  On-Screen Keyboard Area                          │  ← Bottom 1/3
│  (Reserved - do not place UI here)                │
└────────────────────────────────────────────────────┘
```

### Color Scheme (AODA Compliant)
- **Background**: Black (#000000)
- **Text**: White (#FFFFFF) or Light Gray (#EEEEEE)
- **Highlights**: Green (#00FF00 or similar)
- **Warnings**: Yellow (#FFFF00)
- **Errors**: Red (#FF0000)
- **Disabled**: Dark Gray (#666666)

### Typography
- **Minimum Font Size**: 22px
- **Headings**: 32px or larger
- **Body Text**: 22-24px
- **Small Text**: 18px (use sparingly)

### Button Design
- **Minimum Size**: 80px × 60px
- **Recommended**: 120px × 80px or larger
- **Padding**: 20px minimum
- **Border Radius**: 8px
- **Hover/Focus**: Visible state change

---

## Main Menu Features (COMPLETE LIST)

### System & Platform
- **Onboarding Wizard**
  - Operator setup
  - Boat identity & multi-boat support
  - **Step 4: Chartplotter detection** (auto-detect or manual selection)
  - Engine configuration (15-question wizard)
  - CX5106 engine gateway setup
  - DIP switch calculation & visual guidance (both rows)
  - Regional tank sensor configuration (American vs European)
  - Engine position designation (single/port/starboard)
  - OpenCPN auto-installation (if no chartplotter detected)
  - QR code generation (for app pairing)
  
- **System Health Monitoring**
  - Raspberry Pi status (CPU, memory, storage, GPU)
  - Network status (WiFi, Ethernet, NMEA2000, Internet)
  - Service status (Signal K, Node-RED, OpenCPN, Voice)

- **Benchmarking Tools**
  - 30-minute engine baseline capture
  - Performance envelope calculation
  - Trend analysis

- **License Info**
  - Current tier display
  - Version number (from GitHub)
  - Reset counter
  - Upgrade options

### Marine Data & Navigation
- **Signal K Server 2.x**
  - NMEA2000 integration via PiCAN-M
  - CAN0 interface pre-configured
  - PGN detection & parsing
  - Real-time vessel monitoring

- **GPS & AIS Integration**
  - USB GPS data (via gpsd)
  - USB AIS receiver
  - Position, speed, course

- **Engine Health Monitoring**
  - Real-time gauges (RPM, temp, oil pressure, voltage)
  - Alarm thresholds & anomaly detection
  - Baseline comparison
  - Historical trends

- **OpenCPN 5.8.x**
  - Auto-installed if no chartplotter detected
  - Signal K data integration
  - GPS/AIS passthrough
  - Chart management

### Dashboard Gauges
**Line 1 - Engine**:
- Tachometer (RPM)
- Tilt/Trim
- Engine Temperature
- Battery Voltage
- Oil Pressure

**Line 2 - Tanks**:
- Fresh Water (% full)
- Black Water (% full)
- Fuel Level (% full, gallons/liters remaining)
- House Battery Level (%)

**Line 3 - System**:
- Raspberry Pi CPU Usage
- Memory Usage
- Storage Remaining
- GPU Usage

**Line 4 - Network**:
- WiFi Status (on/off, signal strength, SSID)
- Ethernet Status (on/off, IP address)
- NMEA2000 Status (on/off, device count)
- Internet Status (on/off)

### AI & Voice
- **Offline Voice Assistant ("Helm")**
  - Wake word: "Helm"
  - End command: "Helm end"
  - STT: Vosk (vosk-model-small-en-us-0.15)
  - TTS: Piper (en_US-amy-medium)
  - LLM: Phi-2 (2.7B via llama.cpp)
  
- **Voice Enable Switch** (toggle on/off)

- **Voice Commands**:
  - Engine status queries
  - System control
  - Navigation commands
  - Boat log recording
  - Benchmark control

### Camera
- **Full-Screen View**
  - IP67 camera (Reolink RLC-810A)
  - Night vision auto-switching
  - RTSP stream via VLC

- **Recording**
  - Manual start/stop
  - Disk-space aware (stops at 18% remaining)
  - Storage management

### Boat Log
- **Voice Recording**
  - "Helm, record boat log"
  - Voice-to-text transcription
  - Read back for confirmation
  - "Helm, post to boat log" (saves)
  - Timestamp each entry

- **Storage Management**
  - Cap at 10% disk remaining
  - File rotation

### Networking
- **Wi-Fi AP**
  - SSID: "d3kOS"
  - DHCP: 10.42.0.1/24
  - Password configurable

- **Ethernet Sharing**
  - Shared mode: 10.42.0.1/24
  - DHCP for camera and other devices

- **Local-Only Operation**
  - Offline-first design
  - Optional cloud sync (Tier 1+)

### Maintenance
- **Onboarding Reset**
  - Reset counter (Tier 0-2: limit 10)
  - Reset counter (Tier 3: unlimited)
  - Clears configuration
  - Restarts wizard

- **Update System**
  - Via new image only
  - No runtime package updates
  - Version check (when online)

- **Logs & Diagnostics**
  - System logs
  - Benchmark reports
  - Health history

---

## Development Rules

### DO's

✅ **Read MASTER_SYSTEM_SPEC.md before starting**
✅ **Use exact version numbers specified**
✅ **Test on Raspberry Pi 4B (8GB) hardware**
✅ **Follow existing directory structure**
✅ **Use JSON for all configuration (no databases)**
✅ **Include verification steps after every installation command**
✅ **Write idempotent scripts (can run multiple times safely)**
✅ **Include error handling in all scripts**
✅ **Document all assumptions**
✅ **Cross-reference related documents**
✅ **Verify voice assistant works offline**
✅ **Test tier upgrades (0→1, 1→2, 2→3)**
✅ **Validate QR code generation**
✅ **Test mobile app pairing flow**

### DON'Ts

❌ **Never contradict MASTER_SYSTEM_SPEC.md**
❌ **Never recommend untested software versions**
❌ **Never assume internet connectivity for core features**
❌ **Never write code without reading existing codebase first**
❌ **Never create duplicate documentation**
❌ **Never mix conversational AI responses with technical docs**
❌ **Never expose real credentials in documentation**
❌ **Never use vague language ("should work", "might need")**
❌ **Never skip verification steps**
❌ **Never assume user knowledge**
❌ **Never recommend Raspberry Pi OS Bookworm (use Trixie)**
❌ **Never use Node.js v22 (use v18 or v20)**
❌ **Never recommend Dashboard 1.0 (use Dashboard 2.0 Vue)**

---

## CX5106 Configuration

### Critical Information

The CX5106 engine gateway is a **core component** of d3kOS. AI assistants working on CX5106-related features MUST:

1. **Read**: `CX5106_CONFIGURATION_GUIDE.md` and `CX5106_USER_MANUAL.md`
2. **Understand**: DIP switch logic for **BOTH ROWS**:
   - **First Row (8 switches)**: Engine instance, RPM source, cylinders, stroke, gear ratio
   - **Second Row (2 switches)**: Tank sensor standard (American/European), Engine position (Port/Starboard)
3. **Reference**: The 15-question engine wizard that determines DIP settings
4. **Remember**: Non-standard gear ratios (like 1.5:1 Bravo II) require correction factors
5. **Regional Settings**: North American boats use 240-33Ω tank senders, European boats use 0-190Ω
6. **Single Engine Assumption**: Single engine boats default to Port/Primary designation (Second Row Switch "2" = OFF)

### Onboarding Wizard Step 4: Chartplotter Detection (NEW)

**Purpose**: Determine if a third-party chartplotter is present on the NMEA2000 network to decide whether to install OpenCPN.

**Step Flow**:
```
Welcome → Operator → Boat Identity → [STEP 4: Chartplotter] → Engine Q1-15 → DIP Config → QR Code → Complete
```

**Detection Options**:
1. **Manual Selection**: User declares if they have a chartplotter
2. **Auto-Detection**: Listen to NMEA2000 bus for navigation PGNs (5 seconds)
3. **Skip Option**: Default to installing OpenCPN

**Navigation PGNs to Detect**:
- **PGN 129025**: Position, Rapid Update
- **PGN 129026**: COG & SOG, Rapid Update
- **PGN 129029**: GNSS Position Data

**Detection Logic**:
```javascript
if (any navigation PGN detected) {
  → Chartplotter present
  → Skip OpenCPN installation
  → Inform user: "Your chartplotter will display CX5106 engine data automatically"
} else {
  → No chartplotter
  → Auto-install OpenCPN
  → Inform user: "OpenCPN will be installed for navigation"
}
```

**Critical Understanding**:
- **Standard PGNs**: CX5106 outputs standard NMEA2000 PGNs (127488, 127489, 127505, 127508)
- **Universal Compatibility**: ALL chartplotters (Garmin, Simrad, Raymarine, Lowrance, Furuno, Humminbird) read standard PGNs
- **No Translation Required**: d3kOS does NOT need vendor-specific PGN handling
- **Automatic Display**: Third-party chartplotters will show engine data on their built-in gauge pages
- **Bi-Directional Not Needed**: d3kOS only receives NMEA2000 data; it does not transmit PGNs to chartplotters

**Supported Chartplotter Brands** (all use standard PGNs):
- Garmin (GPSMAP, Echomap, GPSMAP Plus)
- Simrad (NSS evo3, GO series, NSX)
- Raymarine (Axiom, Element, eS series)
- Lowrance (HDS LIVE, Elite FS, HDS Carbon)
- Furuno (TZtouch, NavNet TZtouch)
- Humminbird (Solix, Helix series)
- Generic NMEA2000 devices

**What Gets Stored** (`/opt/d3kos/config/onboarding.json`):
```json
{
  "chartplotter": {
    "present": true,
    "detection_method": "auto",
    "detected_pgns": [129026, 129029],
    "install_opencpn": false,
    "timestamp": "2026-02-11T10:30:00Z"
  }
}
```

**Why This Matters**:
- Saves ~500MB disk space if chartplotter already installed
- Prevents duplicate navigation displays
- Informs user that engine data flows automatically to chartplotter
- No vendor-specific configuration needed (standard PGNs work universally)

**Implementation Details (2026-02-11)**:

**Nginx Proxy Configuration** (`/etc/nginx/sites-enabled/default`):
```nginx
# Signal K WebSocket Proxy
location /signalk/ {
    proxy_pass http://localhost:3000/signalk/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout 86400;
}
```

**Why Nginx Proxy is Required**:
- Signal K listens on port 3000 (IPv6 only: `:::3000`)
- Browser WebSocket connects via port 80 (nginx)
- Nginx bridges IPv4/IPv6 and handles WebSocket upgrades
- WebSocket URL: `ws://' + window.location.hostname + '/signalk/v1/stream?subscribe=none`

**Detection JavaScript Implementation** (`/var/www/html/onboarding.html`):
```javascript
function detectChartplotter() {
  const wsUrl = 'ws://' + window.location.hostname + '/signalk/v1/stream?subscribe=none';
  const navigationPGNs = [129025, 129026, 129029];
  const detectedNavPGNs = new Set();
  const ws = new WebSocket(wsUrl);

  ws.onopen = function() {
    console.log('✓ Connected to Signal K successfully');
    ws.send(JSON.stringify({
      context: 'vessels.self',
      subscribe: [{ path: '*', period: 1000 }]
    }));
  };

  ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if (data.updates) {
      data.updates.forEach(update => {
        if (update.$source && update.$source.pgn) {
          const pgn = update.$source.pgn;
          if (navigationPGNs.includes(pgn)) {
            detectedNavPGNs.add(pgn);
          }
        }
      });
    }
  };

  // 5-second timer with progress bar
  // If navigationPGNs detected → skip OpenCPN
  // If no navigationPGNs → install OpenCPN
}
```

**Fullscreen Toggle on Wizard Completion**:
- **Location**: `goToMainMenu()` function in `/var/www/html/onboarding.html`
- **Endpoint**: POST to `http://localhost:1880/toggle-fullscreen`
- **Purpose**: Restore kiosk mode after wizard exits fullscreen (for keyboard access)
- **Implementation**:
```javascript
function goToMainMenu() {
  // ... existing wizard counter code ...

  // Toggle fullscreen (return to kiosk mode)
  fetch('http://localhost:1880/toggle-fullscreen', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  }).then(() => {
    console.log('✓ Toggled to fullscreen/kiosk mode');
  }).catch(err => {
    console.warn('Could not toggle fullscreen:', err);
  });

  // Wait for fullscreen toggle, then redirect
  setTimeout(() => {
    window.location.href = '/';
  }, 500);
}
```

**Testing Results (2026-02-11)**:
- ✅ WebSocket connects via nginx proxy on port 80
- ✅ Detection correctly identifies navigation PGNs (129025, 129026, 129029)
- ✅ Detection correctly skips engine PGNs (127488, 127489, 127505, 127508)
- ✅ Auto-selects "I have a chartplotter" if navigation PGNs detected
- ✅ Auto-selects "I don't have a chartplotter" if no navigation PGNs
- ✅ Fullscreen toggle restores kiosk mode on wizard completion

---

### 15-Question Engine Wizard

The wizard asks these questions (in order):

**ENGINE IDENTIFICATION**:
1. What is the engine manufacturer?
2. What is the engine model?
3. What year is the engine?

**ENGINE CONFIGURATION**:
4. How many cylinders does the engine have?
5. What is the engine displacement (L or CID)?
6. What is the compression ratio?
7. What is the stroke (mm or inches)?
8. What type of induction does the engine use? (Naturally aspirated, Turbocharged, Supercharged)

**ENGINE PERFORMANCE**:
9. What is the rated horsepower?
10. What is the idle RPM specification?
11. What is the WOT (wide-open throttle) RPM range?

**ENGINE LIMITS**:
12. What is the maximum coolant temperature?
13. What is the minimum safe oil pressure at idle and cruise?

**REGIONAL & MULTI-ENGINE SETTINGS (NEW)**:
14. **Tank Sensor Standard (Regional Setting)**: What region is your boat from, or what type of tank level sensors does it use?
    - North America / United States / Canada (240-33Ω senders)
    - Europe / International (0-190Ω senders)
    - I don't know (AI suggests based on boat origin)
    - **Maps to**: CX5106 Second Row Switch "1"
    - **Critical**: Wrong setting causes inverted tank readings (empty shows full, full shows empty)

15. **Engine Designation (For Multi-Engine Configuration)**: If you have multiple engines, which one is this CX5106 monitoring?
    - Single engine (or primary) → Auto-set to OFF
    - Port engine (left) → Switch OFF
    - Starboard engine (right) → Switch ON
    - **Maps to**: CX5106 Second Row Switch "2"
    - **Conditional Logic**: Skip if single engine (auto-set to Port/Primary)

These determine:
- CX5106 DIP switch positions (**FIRST ROW**: SW1-8)
- CX5106 DIP switch positions (**SECOND ROW**: "1"-"2")
- Expected PGN set
- Alarm thresholds
- Performance baselines
- Anomaly detection parameters
- Tank level sensor calibration
- Engine position designation

### DIP Switch Configuration - Both Rows

**FIRST ROW (8 Switches)**:
- SW1-2: Engine Instance (Single=0, Port=1, Starboard=2, Center=3)
- SW3-4: RPM Source (Alternator W-Terminal, Ignition Coil, Magnetic Pickup, ECU Output)
- SW5-6: Number of Cylinders (3, 4, 6, 8)
- SW7: Stroke Type (OFF=4-stroke, ON=2-stroke)
- SW8: Gear Ratio (OFF=1:1 direct, ON=2:1 reduction)

**SECOND ROW (2 Switches) - CRITICAL FOR TANK READINGS**:
- Switch "1": Tank Sensor Resistance Standard
  - **ON** = American standard (240-33Ω) - North America/Canada
  - **OFF** = European standard (0-190Ω) - Europe/International
  - **Impact**: Wrong setting inverts fuel, water, and waste tank readings

- Switch "2": Engine Position Designation
  - **OFF** = Port engine / Single engine / Primary
  - **ON** = Starboard engine
  - **Default**: OFF for single engine configurations

### Regional Detection & AI Assistance

**When user selects "I don't know" for tank sensor standard:**
- AI infers based on:
  - Country of boat registration
  - Boat manufacturer origin (e.g., American brand → likely American senders)
  - Engine manufacturer (e.g., Mercruiser, Yanmar)
  - User's location/timezone
- Default: If boat is in North America, select 240-33Ω (ON)
- Validation: If readings are inverted after configuration, toggle this switch

### Configuration Example with Both Rows

**Example: Single Yanmar 3YM30 Diesel, North American Boat**

```
FIRST ROW:
SW1: OFF  SW2: OFF  SW3: OFF  SW4: ON
SW5: ON   SW6: ON   SW7: OFF  SW8: ON

SECOND ROW:
"1": ON   (American 240-33Ω tank senders)
"2": OFF  (Single engine / Port)

Result:
- Instance 0 (single engine)
- Magnetic pickup RPM
- 3 cylinders
- 4-stroke
- 2:1 gear ratio
- American tank sensor standard
- Port/Primary designation
```

**Example: Twin Volvo Penta D4 (Port Engine), European Boat**

```
FIRST ROW:
SW1: ON   SW2: OFF  SW3: OFF  SW4: OFF
SW5: OFF  SW6: OFF  SW7: OFF  SW8: OFF

SECOND ROW:
"1": OFF  (European 0-190Ω tank senders)
"2": OFF  (Port engine)

Result:
- Instance 1 (port engine)
- Alternator W-terminal RPM
- 4 cylinders
- 4-stroke
- 1:1 direct drive
- European tank sensor standard
- Port engine designation
```

### Common Configuration Errors

**Error 1: Tank readings inverted (full shows empty)**
- **Cause**: Wrong Second Row Switch "1" setting
- **Fix**: Toggle Second Row Switch "1" (ON↔OFF)
- **Prevention**: Verify boat origin during onboarding

**Error 2: Duplicate engine instances on twin-engine boats**
- **Cause**: Both CX5106 units set to same instance (SW1/SW2)
- **Fix**: Set first to Instance 1 (Port), second to Instance 2 (Starboard)

**Error 3: Tank readings from wrong engine on twin-engine boats**
- **Cause**: Second Row Switch "2" not set correctly
- **Fix**: Verify Port=OFF, Starboard=ON designation matches physical installation

### JSON Configuration Storage (Updated)

```json
{
  "engine": {
    "manufacturer": "Yanmar",
    "model": "3YM30",
    "cylinders": 3,
    "stroke": "4-stroke",
    "fuel_type": "diesel",
    "gear_ratio": "2:1"
  },
  "gateway": {
    "model": "CX5106",
    "switches": {
      "row1": {
        "sw1": "OFF",
        "sw2": "OFF",
        "sw3": "OFF",
        "sw4": "ON",
        "sw5": "ON",
        "sw6": "ON",
        "sw7": "OFF",
        "sw8": "ON"
      },
      "row2": {
        "sw1": "ON",
        "sw2": "OFF"
      }
    },
    "instance": 0,
    "rpm_source": "magnetic_pickup",
    "tank_sensor_standard": "american_240_33",
    "tank_sensor_region": "North America",
    "engine_position": "port",
    "notes": "Single Yanmar 3YM30 diesel, 2:1 reduction, North American boat"
  },
  "tank_sensors": {
    "standard": "american_240_33",
    "resistance_range": "240-33Ω",
    "fuel_calibration": "240Ω=empty, 33Ω=full",
    "water_calibration": "240Ω=empty, 33Ω=full",
    "waste_calibration": "240Ω=empty, 33Ω=full"
  }
}
```

---

## API Specification (v1.0)

### Transport & Format
- **Transport**: HTTPS
- **Format**: JSON
- **Auth**: Bearer token
- **Versioning**: `/api/v1/...`

### Endpoints by Category

#### 1. Identity & Pairing

**POST** `/api/v1/installation/register`
- Pi registers after wizard complete
- Returns pairing token (10-minute expiry)

**POST** `/api/v1/pair`
- Mobile app pairs with Pi
- Both upgrade to Tier 1
- Pairing token invalidated

#### 2. Tier Synchronization

**GET** `/api/v1/tier/status?installation_uuid=UUID`
- Pi polls for tier updates
- Returns current tier + entitlements

**GET** `/api/v1/tier/app?device_id=UUID`
- App polls for tier updates
- Returns tier + available features

#### 3. Ecommerce Upgrade

**POST** `/api/v1/tier/upgrade`
- Ecommerce system upgrades tier
- Updates both Pi and app
- Requires transaction ID

#### 4. Wizard & Reset

**POST** `/api/v1/wizard/update`
- Pi reports wizard run count
- Returns remaining resets

**POST** `/api/v1/wizard/reset`
- Request onboarding reset
- Checks tier limit
- Returns status

#### 5. Engine Metadata

**POST** `/api/v1/engine/metadata`
- Pi uploads 13-question answers
- Returns CX5106 mode, DIP switches, expected PGNs

#### 6. Boat Health & Benchmark

**POST** `/api/v1/engine/baseline`
- Upload 30-minute baseline capture
- Returns baseline ID

**POST** `/api/v1/boat/health`
- Real-time health snapshot
- Returns anomaly detection result

#### 7. Camera Recording

**POST** `/api/v1/camera/recording`
- Upload recording metadata
- Disk usage tracking

#### 8. Boat Log

**POST** `/api/v1/log/entry`
- Upload voice-to-text log entry
- Returns entry ID

---

## File Structure & Conventions

### Directory Layout
```
/opt/d3kos/
├── services/
│   ├── onboarding/          # Onboarding wizard backend
│   ├── voice/               # Voice assistant service
│   ├── .node-red/           # Node-RED flows
│   ├── signalk/             # Signal K configuration
│   └── opencpn/             # OpenCPN integration
├── config/                  # Persistent user configuration
│   ├── operator.json
│   ├── boat-identity.json
│   ├── boat-active.json
│   ├── license.json         # Tier & entitlements
│   └── boats/               # Multi-boat support
├── state/                   # Runtime state
│   ├── onboarding.json
│   ├── onboarding-reset-count.json
│   ├── baseline.json
│   └── health-status.json
├── system/                  # Systemd services
│   ├── d3kos-onboarding.service
│   ├── d3kos-voice.service
│   ├── d3kos-health.service
│   └── d3kos-benchmark.service
└── scripts/                 # Installation scripts
```

### Configuration Files

All configuration MUST be:
- **Format**: JSON (not YAML, XML, or TOML)
- **Location**: `/opt/d3kos/config/` or `/opt/d3kos/state/`
- **Atomic writes**: Write to temp file, then rename
- **Power-loss safe**: No partial writes
- **Human-readable**: Properly indented

---

## Testing Requirements

### Before Submitting Code

✅ Tested on Raspberry Pi 4B (8GB RAM)
✅ Tested with PiCAN-M HAT connected
✅ Verified CAN0 interface works
✅ Checked with 10.1" touchscreen at 1920x1200
✅ Tested with on-screen keyboard visible
✅ Verified AODA compliance
✅ Power-cycled to test persistence
✅ Checked error handling
✅ Verified documentation is updated
✅ **Tested voice assistant wake word**
✅ **Verified offline LLM inference**
✅ **Tested tier upgrade flow (0→1→2→3)**
✅ **Validated QR code generation**
✅ **Verified mobile app pairing**

---

## Pre-Built Image Creation

### Build Process
1. Start with clean Raspberry Pi OS Trixie (64-bit)
2. Install all software components per MASTER_SYSTEM_SPEC
3. Configure all services
4. Download Vosk model
5. Download Piper voices
6. Download Phi-2 model
7. Test thoroughly on hardware
8. Create image: `sudo dd if=/dev/mmcblk0 of=d3kos-vX.X.X-pi4b.img bs=4M`
9. Compress: `gzip d3kos-vX.X.X-pi4b.img`
10. Generate checksum: `sha256sum d3kos-vX.X.X-pi4b.img.gz > d3kos-vX.X.X-pi4b.img.gz.sha256`
11. Upload to GitHub releases

### Image Naming
```
d3kos-v<version>-pi4b-<date>.img.gz

Example: d3kos-v1.0.0-pi4b-20260205.img.gz
```

### Included in Image
- Raspberry Pi OS Trixie (64-bit)
- Node.js v20 LTS
- Signal K Server 2.x
- Node-RED 3.x + Dashboard 2.0
- All Python dependencies
- All system services configured
- CAN0 interface pre-configured
- **Vosk model: vosk-model-small-en-us-0.15**
- **Piper voices: en_US-amy-medium**
- **Phi-2 model (2.7B)**
- **PocketSphinx with wake word config**
- OpenCPN 5.8.x (ready to enable)

### NOT Included (User Configures)
- Operator name
- Boat details
- Engine configuration (13 questions)
- CX5106 DIP switch settings
- Network passwords
- GPS/AIS device paths
- License tier (starts at Tier 0)

---

## Troubleshooting Guidelines for AI

### When Code Doesn't Work

1. **Check versions** - Are you using specified versions?
2. **Check prerequisites** - Did earlier steps complete?
3. **Check logs** - What do systemd logs show?
4. **Check paths** - Are files in expected locations?
5. **Check permissions** - Does `pi` user have access?
6. **Check tier** - Does feature require higher tier?
7. **Check voice models** - Are Vosk/Piper/Phi-2 downloaded?

### When Documentation Conflicts

1. **MASTER_SYSTEM_SPEC.md wins** - Always
2. **CLAUDE.md v2 overrides v1** - Check version
3. **Newer docs override older** - Check dates
4. **Ask for clarification** - Don't assume

### When Generating New Features

1. **Read related docs FIRST**
2. **Check if feature already exists**
3. **Verify tier requirements**
4. **Test on hardware**
5. **Update all related docs**
6. **Test offline functionality**

---

## Common Pitfalls to Avoid

### 1. Version Confusion
**Problem**: Recommending Bookworm instead of Trixie
**Solution**: Always specify "Raspberry Pi OS Trixie (Debian 13)"

### 2. Voice Assistant Assumptions
**Problem**: Assuming internet for voice processing
**Solution**: Everything (wake word, STT, LLM, TTS) must work offline

### 3. Tier Confusion
**Problem**: Enabling cloud features in Tier 0
**Solution**: Check tier entitlements before enabling features

### 4. QR Code Generation
**Problem**: Missing pairing token or wrong format
**Solution**: Follow exact JSON schema from API spec

### 5. Reset Counter
**Problem**: Not checking tier before allowing reset
**Solution**: Tier 3 = unlimited, Tier 0-2 = max 10

---

## Success Criteria

Code/documentation is ready when:

✅ Aligns with MASTER_SYSTEM_SPEC.md
✅ Uses correct software versions (Trixie, Node v20, etc.)
✅ Includes verification steps
✅ Includes error handling
✅ Tested on Raspberry Pi 4B (8GB)
✅ AODA compliant (if UI)
✅ Documentation updated
✅ No contradictions with existing code
✅ Works completely offline (for Tier 0)
✅ Power-loss safe
✅ Voice assistant works offline
✅ Tier system enforced correctly
✅ QR code generation validated
✅ Mobile app pairing tested (Tier 1+)
✅ Cloud sync optional (Tier 1+)

---

## Contact & Escalation

If you encounter:
- Contradictions in specifications
- Unclear requirements (especially tier boundaries)
- Missing information
- Technical limitations (e.g., Phi-2 RAM requirements)

**DO**: Document the issue and ask for clarification
**DON'T**: Make assumptions and proceed

---

## Version History

| Version | Date | Major Changes |
|---------|------|---------------|
| 1.0 | 2026-02-04 | Initial CLAUDE.md creation |
| 2.0 | 2026-02-05 | Added voice assistant spec, updated licensing tiers (0-3), API specification, hardware requirements (8GB RAM), Trixie OS requirement |
| 2.1 | 2026-02-06 | Added CX5106 second row DIP switch documentation (tank sensor standards, engine position), expanded wizard from 13 to 15 questions, added regional detection logic |
| 2.2 | 2026-02-07 | Full rebrand from Helm-OS to d3kOS, added d3-k1 hardware designation |
| 2.3 | 2026-02-11 | Added Step 4 (Chartplotter Detection) to onboarding wizard, clarified that CX5106 uses standard PGNs (no vendor-specific translation needed), documented chartplotter compatibility |
| **2.4** | **2026-02-11** | **Added implementation details for Step 4: nginx proxy configuration for WebSocket, JavaScript detection code, fullscreen toggle on wizard completion** |

---

## Anomalies Detected & Resolved

### Anomaly 1: RAM Requirement
- **Previous**: 4GB or 8GB RAM
- **Updated**: **8GB RAM required** (for Phi-2 LLM + OS + services)
- **Reason**: Phi-2 (2.7B) needs ~5-6GB RAM for inference

### Anomaly 2: OS Version
- **Previous**: Bookworm or Trixie
- **Updated**: **Trixie (Debian 13) only**
- **Reason**: Piper and PocketSphinx packages available in Trixie repos

### Anomaly 3: Licensing Tiers
- **Previous**: Vague Tier 1-4
- **Updated**: **Clear Tier 0-3 with specific features**
- **Tier 1 changed**: Now includes mobile app (was separate)

### Anomaly 4: LLM Runtime
- **Previous**: Not specified
- **Updated**: **llama.cpp** (was implied Phi-2 standalone)
- **Reason**: llama.cpp is optimized for ARM and needed for Phi-2

### Anomaly 5: Wake Word Options
- **Previous**: Only "Helm"
- **Updated**: "Helm" (primary), "Hey Captain" or "Hey Boat" (alternatives)
- **Reason**: User feedback from additionalclaude.txt

### Anomaly 6: CX5106 Second Row DIP Switches - CRITICAL DISCOVERY
- **Previous**: Documentation only covered first row (8 switches)
- **Updated**: **Second row has 2 switches** controlling tank sensor standards and engine position
- **Reason**: Manual analysis revealed undocumented second row:
  - Switch "1": Tank sensor resistance (American 240-33Ω vs European 0-190Ω)
  - Switch "2": Engine position (Port/Starboard designation)
- **Impact**: Wrong Switch "1" setting causes inverted tank level readings (critical safety issue)
- **Wizard**: Expanded from 13 to 15 questions (added Q14: Tank Sensor Standard, Q15: Engine Designation)
- **Default**: Single engine boats → Second Row Switch "2" = OFF (Port/Primary)

---

## Final Reminder

**This is not a suggestion document - it is a REQUIREMENT document.**

All AI assistants working on d3kOS MUST follow these guidelines. Deviations must be explicitly justified and documented.

When in doubt: **Read MASTER_SYSTEM_SPEC.md and CLAUDE.md v2 again.**
