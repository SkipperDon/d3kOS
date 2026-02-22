# CLAUDE.md - AI Assistant Guidelines for d3kOS Development
## Version 3.8

**Last Updated**: February 22, 2026
**Changes from v3.7**: **CRITICAL UPDATE - Phi-2 LLM REMOVED** (Feb 16, 2026): Removed due to 60-180s response time (unusable on boat helm), freed 1.7GB storage. Replaced with OpenRouter (gpt-3.5-turbo, 6-8s) + rule-based system (13 patterns, 0.17s). Updated all documentation references from Perplexity→OpenRouter. Updated software versions: Node.js v18→v20.20.0, Node-RED 3.x→v4.1.4. Confirmed Trixie (Debian 13) as current OS (NOT Bookworm). Added Signal K caching (3s TTL, 100× speedup for rapid-fire queries). Documented actual system state: d3kOS v0.9.1.2, Tier 3, 22+ services.
**Changes from v3.6**: Added Timezone Auto-Detection System - 3-tier automatic detection (GPS coordinates → internet geolocation → UTC fallback), runs on first boot before onboarding wizard, no user prompts during setup, manual override available in Settings page. Prevents hardcoded Toronto timezone issue for worldwide deployment.
**Changes from v3.5**: Added comprehensive AI-Powered Self-Healing System - 5-tier architecture (detection, correlation, AI diagnosis, auto-remediation, user notification), engine and Pi health monitoring, anomaly detection with statistical process control, pattern matching for common failures, AI integration for root cause analysis, safe auto-remediation (restart services, kill stuck processes), user-friendly error translation, and remediation history tracking. Renamed "factory reset" to "Initial Setup Reset" throughout documentation.
**Changes from v3.4**: Added comprehensive Version Management & Upgrade System - d3kOS version tracking (current: 0.9.1-beta), GitHub-based version checking, tier-based upgrade capabilities (Tier 0: no upgrades, Tier 1/2/3: curl-based OTA upgrades via mobile app approval), System Management API (port 8095), automated backup/rollback, checksum verification, and upgrade monitoring. Clarified that Tier 0/1 cannot incrementally update (image-only), while Tier 2/3 support OTA updates.
**Changes from v3.3**: Added comprehensive Stripe Billing implementation documentation - 48KB implementation guide with 40-60 hour development breakdown, production-ready code examples (Python Flask webhook handler + subscription API, iOS StoreKit 2, Android Billing Library 5.0+, SQL database schema), complete testing procedures, deployment checklist, and cost analysis. Confirmed traditional e-commerce platforms (OpenCart, PrestaShop, osCommerce, Zen Cart) are NOT suitable for mobile app subscription billing.
**Changes from v3.2**: Added comprehensive E-commerce Integration & Mobile App In-App Purchases section - Stripe (primary), Apple App Store IAP (iOS mandatory), Google Play Billing (Android mandatory), PayPal (alternative) - subscription management, payment webhooks, failed payment grace period, platform-specific purchase flows, updated Tier 2 pricing to $9.99/month and Tier 3 to $99.99/year
**Changes from v3.1**: Added comprehensive telemetry & analytics export (#9 category) - system performance metrics, user interaction data, AI assistance metrics, device/environment data, business intelligence - collected in background via d3kos-telemetry.service (Tier 1+ only, user consent required)
**Changes from v3.0**: Updated tier-based update restrictions (Tier 0/1: image-only, Tier 2/3: OTA updates), added Tier 1 configuration preservation via mobile app, added onboarding export (#8 category) with reset counter, renamed "Onboarding Wizard" to "Initial Setup" in all UI references
**Changes from v2.9**: Added comprehensive Data Export & Central Database Sync specification (Tier 1+) - includes export formats, triggers, queue system, API endpoints, and automatic boot-time sync
**Changes from v2.8**: Added Marine Vision System specification (fish capture mode, forward watch mode, species ID, fishing regulations)
**Changes from v2.7**: Added large touch-friendly map controls to Weather Radar (80px buttons: Zoom In/Out, Recenter, overlay toggle)
**Changes from v2.6**: Added Weather Radar feature (GPS-based, animated radar, marine conditions, auto-logging to boatlog every 30 minutes)
**Changes from v2.5**: Updated wake words to "Helm", "Advisor", "Counsel" (changed Navigator→Counsel), added "Aye Aye Captain" acknowledgment response
**Changes from v2.4**: Added hybrid AI assistant system (online Perplexity + onboard Phi-2), skills.md context management, automatic document retrieval, learning/memory features, text input interface
**Changes from v2.3**: Added implementation details for Step 4 (WebSocket proxy, detection JavaScript, fullscreen toggle)
**Changes from v2.2**: Added Step 4 (Chartplotter Detection) to Initial Setup wizard, clarified standard PGN compatibility (no vendor-specific translation needed)
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
- AI-assisted Initial Setup wizard (15-question engine configuration)
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
- **MicroSD Card**: 32GB minimum, 128GB recommended (currently 16GB OS card)
- **USB Storage**: 128GB USB drive installed at `/media/d3kos/6233-3338` (119.2GB usable)
- **Power**: 5V 3A minimum (official Raspberry Pi power supply)

---

## Software Stack (Fixed Versions)

| Component | Version | Notes |
|-----------|---------|-------|
| **Raspberry Pi OS** | **Trixie (Debian 13)** | 64-bit ARM, NOT Bookworm |
| **Node.js** | v20.20.0 | Current (NOT v18, NOT v22) |
| **Signal K Server** | 2.x (latest via npm) | Marine data hub |
| **Node-RED** | v4.1.4 | Flow-based programming |
| **Node-RED Dashboard** | 2.0.4-1 (v4.1.4) | Dashboard 2.0 (Vue-based) |
| **OpenCPN** | 5.8.x | Auto-installed if no chartplotter |
| **PocketSphinx** | Latest | Wake word detection |
| **Vosk** | Latest | Speech-to-text (offline) |
| **Piper** | Latest | Text-to-speech (offline) |
| **OpenRouter** | API (gpt-3.5-turbo) | Online AI (6-8s) |
| **Rule-based AI** | 13 patterns | Offline AI (0.17s) |

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
- Boot and run Initial Setup wizard
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

#### C. AI Query Handler (Hybrid Brain)
- **Purpose**: Routes queries to appropriate AI backend
- **Backends**:
  - **OpenRouter** (gpt-3.5-turbo): Online, 6-8s, complex queries
  - **Rule-based**: Offline, 0.17s, 13 simple patterns
- **Wake Word Routing**:
  - "helm" → Auto (rule-based if simple, OpenRouter if complex)
  - "advisor" → Force offline (rule-based only)
  - "counsel" → Force online (OpenRouter)
- **Features**:
  - Signal K caching (3s TTL, 100× speedup)
  - Pattern matching for common queries
  - Context-aware responses with boat status
  - Conversation history in SQLite

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

## Hybrid AI Assistant System (UPDATED FEB 16, 2026)

### Overview

**⚠️ CRITICAL UPDATE**: Phi-2 LLM removed (Feb 16, 2026) due to 60-180s response time (unusable on boat helm).

d3kOS implements a **hybrid AI assistant system** that intelligently routes queries between two backends:

- **Online AI** (OpenRouter gpt-3.5-turbo): Fast (6-8s), powerful, internet-required
- **Offline AI** (Rule-based patterns): Ultra-fast (0.17s), 13 query types, no internet

**Key Benefits**:
- Automatic pattern matching for simple queries (instant response)
- OpenRouter for complex queries (6-8s vs Phi-2's 60-180s)
- Signal K caching (3s TTL, 100× speedup for rapid-fire questions)
- Shared context via skills.md
- Conversation memory in SQLite
- Both voice and text input interfaces

### Architecture

```
┌─────────────────────────────────────────────┐
│     User Input (Voice OR Text)              │
└───────────────┬─────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────┐
│         Pattern Matching & Routing          │
│  ┌──────────────┐      ┌──────────────┐    │
│  │Pattern match?│      │ No match?    │    │
│  └──────┬───────┘      └──────┬───────┘    │
│         │                     │            │
│         ▼                     ▼            │
│  ┌──────────────┐      ┌──────────────┐   │
│  │ Rule-Based   │      │   Internet?  │   │
│  │   0.17-0.22s │      │   Check      │   │
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
  "openrouter": {
    "api_key": "sk-or-v1-...",
    "base_url": "https://openrouter.ai/api/v1/chat/completions",
    "model": "openai/gpt-3.5-turbo",
    "enabled": true,
    "max_tokens": 500,
    "temperature": 0.7
  },
  "cache_ttl": 3.0
}
```

### Offline AI Assistant (Rule-Based)

**Purpose**: Fast offline responses for simple queries

**Implementation**: Pattern matching (13 predefined query types)

**Response Time**: 0.17-0.22 seconds (with Signal K cache)

**Wake Words**:
- "Advisor" - Force offline (rule-based only)
- "Helm" - Auto (rule-based if simple, OpenRouter if complex)

**Supported Patterns**:
```javascript
// 13 instant-response patterns
const patterns = {
  rpm: /\b(rpm|engine speed|revolutions)\b/,
  oil: /\b(oil|oil pressure)\b/,
  temperature: /\b(temp|temperature|coolant)\b/,
  fuel: /\b(fuel|fuel level|diesel)\b/,
  battery: /\b(battery|voltage|power)\b/,
  speed: /\b(speed|knots|velocity)\b/,
  heading: /\b(heading|direction|course)\b/,
  boost: /\b(boost|turbo|manifold pressure)\b/,
  hours: /\b(engine hours|runtime|operating time)\b/,
  location: /\b(location|position|where|gps|coordinates)\b/,
  time: /\b(what time|current time|date)\b/,
  help: /\b(help|capabilities|commands)\b/,
  status: /\b(status|all|everything|full)\b/
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

**Current System**: 128GB USB drive installed for additional storage (119.2GB usable)

**Recommended**: 64GB SD card is sufficient for OS, 128GB USB drive provides expansion storage

**Storage Configuration**:
- Multiple boat profiles
- Extended conversation history (> 3 years)
- Full PDF storage (not just text)

### Implementation Checklist

**Phase 1: Skills.md Foundation**
- [ ] Create skills.md format specification
- [ ] Implement skills.md template generation
- [ ] Add skills.md to Initial Setup wizard
- [ ] Test with sample boat/engine data

**Phase 2: Document Retrieval**
- [ ] Implement manualslib.com PDF downloader
- [ ] Implement PDF → Markdown text extractor
- [ ] Implement BoatUS.org scraper
- [ ] Implement USCG regulations fetcher
- [ ] Add progress UI to Initial Setup wizard

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
- **No incremental updates** - must download new d3kOS image for updates

**Reset Counter**:
- After 10 resets, user must download new image
- Prevents single license on multiple boats

**Updates**:
- **Cannot incrementally update** - new versions require fresh image download
- Configuration and onboarding data NOT preserved across updates
- User must re-run Initial Setup wizard after update

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

**Updates**:
- **Cannot incrementally update** - new versions require fresh image download (same as Tier 0)
- **Configuration preservation:** Mobile app stores onboarding data and configuration with installation_id
- After downloading new d3kOS image, user can import saved configuration from mobile app
- Eliminates need to re-run Initial Setup wizard after updates
- Mobile app syncs: onboarding answers, settings, benchmarks, reset counter

**Configuration Restore Process** (Tier 1 only):
1. User downloads new d3kOS image
2. Flash SD card with new image
3. Boot Pi and connect to mobile app
4. Mobile app detects new installation with matching installation_id
5. App prompts: "Restore previous configuration?"
6. User taps "Restore"
7. App sends configuration to Pi via `/api/v1/config/import`
8. System applies saved settings, skips Initial Setup wizard
9. User ready to use updated d3kOS with preserved settings

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

**Cost**: **$9.99/month** (USD)

**Reset Limit**: Still 10 resets

**Updates**:
- **CAN incrementally update** - OTA (over-the-air) updates via apt/dpkg
- No need to download new image for minor/patch updates
- Major version updates may still require image download
- Configuration automatically preserved during updates
- Update via Settings → System → Check for Updates

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

**Cost**: **$99.99/year** (USD) - 17% discount vs monthly, supports up to 5 boats

**Reset Limit**: **Unlimited**

**Updates**:
- **CAN incrementally update** - OTA (over-the-air) updates via apt/dpkg (same as Tier 2)
- No need to download new image for minor/patch updates
- Major version updates may still require image download
- Configuration automatically preserved during updates
- Update via Settings → System → Check for Updates
- Fleet-wide update management via enterprise dashboard

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

### E-commerce Integration & Mobile App In-App Purchases

**Purpose**: Enable users to purchase Tier 2 and Tier 3 subscriptions directly within the mobile app, with seamless integration to central database for automatic tier upgrades.

---

#### E-commerce Platform Options

The d3kOS ecosystem supports multiple payment platforms to accommodate different app distribution channels and user preferences:

| Platform | Use Case | Commission | Required For |
|----------|----------|------------|--------------|
| **Stripe** | Web checkout, cross-platform | 2.9% + $0.30 | Primary payment processor |
| **Apple App Store IAP** | iOS app subscriptions | 15-30% | iOS apps (mandatory) |
| **Google Play Billing** | Android app subscriptions | 15-30% | Android apps (mandatory) |
| **PayPal** | Alternative payment method | 2.9% + $0.30 | Optional (user preference) |

**Recommended Architecture**:
- **Primary**: Stripe (lowest fees, works across web + mobile)
- **iOS Requirement**: Apple In-App Purchase (IAP) - mandatory per App Store guidelines
- **Android Requirement**: Google Play Billing - mandatory per Play Store guidelines
- **Alternative**: PayPal for users without credit cards

---

#### Platform-Specific Requirements

##### **Stripe** (Cross-Platform - Recommended)
- **Stripe Checkout**: Web-based payment flow opened in mobile app browser
- **Stripe SDK**: Native iOS/Android integration for better UX
- **Products**:
  - `price_tier2_monthly`: $9.99/month recurring
  - `price_tier3_annual`: $99.99/year recurring
- **Webhooks**:
  - `customer.subscription.created` - New subscription
  - `invoice.payment_succeeded` - Recurring payment
  - `invoice.payment_failed` - Payment failure
  - `customer.subscription.deleted` - Cancellation
- **Metadata**: Store `installation_id` in subscription metadata
- **Customer Portal**: Allow users to manage subscriptions, update payment methods, view invoices

##### **Apple App Store In-App Purchase (iOS)**
- **Product IDs**:
  - `com.d3kos.tier2.monthly` - $9.99/month auto-renewable subscription
  - `com.d3kos.tier3.annual` - $99.99/year auto-renewable subscription
- **StoreKit 2**: Use StoreKit 2 API for iOS 15+ (SwiftUI integration)
- **Server-to-Server Notifications**: Apple sends notifications to webhook endpoint
- **Receipt Validation**: Validate receipts with Apple server before granting access
- **Family Sharing**: Consider enabling for Tier 3 (enterprise/family boats)
- **Subscription Groups**: Create "d3kOS Premium" group with Tier 2 and Tier 3 as options

##### **Google Play Billing (Android)**
- **Product IDs**:
  - `tier2_monthly` - $9.99/month auto-renewable subscription
  - `tier3_annual` - $99.99/year auto-renewable subscription
- **Billing Library**: Use Google Play Billing Library 5.0+
- **Real-Time Developer Notifications (RTDN)**: Google sends notifications via Cloud Pub/Sub
- **Subscription Management**: Link to Google Play subscription settings
- **Offer Codes**: Support promo codes for trials/discounts

##### **PayPal** (Alternative Payment)
- **PayPal Subscriptions API**: Create recurring billing agreements
- **Products**:
  - Tier 2 Monthly Subscription: $9.99/month
  - Tier 3 Annual Subscription: $99.99/year
- **Webhooks**: `BILLING.SUBSCRIPTION.CREATED`, `BILLING.SUBSCRIPTION.CANCELLED`
- **PayPal Button**: Embed in mobile app or redirect to PayPal checkout

---

#### Subscription Information Structure

All subscription records in the central database must include:

```json
{
  "subscription_id": "sub_abc123def456",
  "installation_id": "550e8400e29b41d4",
  "tier": 2,
  "status": "active",

  "payment_provider": "stripe",
  "provider_subscription_id": "sub_1234567890",
  "provider_customer_id": "cus_9876543210",

  "started_at": "2026-02-16T10:00:00Z",
  "current_period_start": "2026-02-16T10:00:00Z",
  "current_period_end": "2026-03-16T10:00:00Z",
  "canceled_at": null,
  "expires_at": null,

  "amount_cents": 999,
  "currency": "USD",
  "billing_interval": "month",

  "trial_start": null,
  "trial_end": null,

  "last_payment_at": "2026-02-16T10:00:00Z",
  "next_payment_at": "2026-03-16T10:00:00Z",
  "payment_failed_count": 0,

  "user_email": "captain@example.com",
  "user_name": "Captain John Smith"
}
```

**Required Fields**:
- `installation_id` - Link subscription to specific d3kOS system
- `tier` - 2 or 3
- `status` - `active`, `past_due`, `canceled`, `expired`
- `payment_provider` - `stripe`, `apple_iap`, `google_play`, `paypal`
- `provider_subscription_id` - External subscription ID for webhook matching
- `amount_cents` - 999 for $9.99, 9999 for $99.99
- `billing_interval` - `month` or `year`
- `current_period_end` - When subscription renews or expires

---

#### Mobile App In-App Purchase Flow

##### **Tier 1 → Tier 2 Upgrade (Monthly)**

**Step 1: User Initiates Upgrade**
- User opens mobile app Settings → Subscription
- Taps "Upgrade to Premium (Tier 2)"
- App displays feature comparison and pricing ($9.99/month)
- User taps "Subscribe Now"

**Step 2: Platform Detection**
```javascript
if (platform === 'ios') {
  // Use Apple In-App Purchase
  initiateAppleIAP('com.d3kos.tier2.monthly');
} else if (platform === 'android') {
  // Use Google Play Billing
  initiateGooglePlayBilling('tier2_monthly');
} else {
  // Use Stripe Checkout (web or cross-platform)
  initiateStripeCheckout(installationId, 'tier2_monthly');
}
```

**Step 3a: Stripe Flow** (iOS/Android using Stripe)
1. App calls backend: `POST /api/v1/stripe/checkout/session`
   ```json
   {
     "installation_id": "550e8400e29b41d4",
     "tier": 2,
     "billing_interval": "month"
   }
   ```
2. Backend creates Stripe Checkout Session with metadata
3. Backend returns checkout URL: `https://checkout.stripe.com/...`
4. App opens checkout URL in in-app browser or external browser
5. User enters payment details on Stripe-hosted page
6. Stripe processes payment
7. Stripe webhook fires: `customer.subscription.created`
8. Backend receives webhook, creates subscription record
9. Backend updates `installations.tier = 2` and `is_paid_tier = TRUE`
10. Backend sends push notification to mobile app: "Upgrade successful!"
11. App polls: `GET /api/v1/tier/status?installation_id=550e...`
12. App receives `{"tier": 2, "status": "active"}` and unlocks Tier 2 features
13. On next Pi boot, Pi polls cloud and detects tier upgrade
14. Pi updates local `license.json` and enables Tier 2 features

**Step 3b: Apple IAP Flow** (iOS Only)
1. App requests product info: `SKProductsRequest` for `com.d3kos.tier2.monthly`
2. App displays localized price from App Store
3. User taps "Subscribe", triggers: `SKPaymentQueue.add(payment)`
4. iOS shows native payment sheet (Face ID/Touch ID)
5. User confirms purchase
6. App receives transaction: `SKPaymentTransactionObserver`
7. App validates receipt with Apple server
8. App calls backend: `POST /api/v1/apple/verify-receipt`
   ```json
   {
     "installation_id": "550e8400e29b41d4",
     "receipt_data": "base64_encoded_receipt",
     "transaction_id": "1000000123456789"
   }
   ```
9. Backend validates receipt with Apple
10. Backend creates subscription record with `payment_provider = 'apple_iap'`
11. Backend updates tier in database
12. Backend returns success to app
13. App unlocks Tier 2 features immediately
14. Apple sends server-to-server notification for renewals/cancellations

**Step 3c: Google Play Billing Flow** (Android Only)
1. App queries product details: `BillingClient.queryProductDetailsAsync()`
2. App displays localized price from Play Store
3. User taps "Subscribe", triggers: `billingClient.launchBillingFlow()`
4. Android shows native payment sheet (Google Pay)
5. User confirms purchase
6. App receives purchase token: `onPurchasesUpdated()`
7. App acknowledges purchase: `billingClient.acknowledgePurchase()`
8. App calls backend: `POST /api/v1/google/verify-purchase`
   ```json
   {
     "installation_id": "550e8400e29b41d4",
     "purchase_token": "abc123...",
     "product_id": "tier2_monthly"
   }
   ```
9. Backend verifies purchase with Google Play Developer API
10. Backend creates subscription record with `payment_provider = 'google_play'`
11. Backend updates tier in database
12. Backend returns success to app
13. App unlocks Tier 2 features immediately
14. Google sends Real-Time Developer Notifications (RTDN) for renewals/cancellations

**Step 4: d3kOS System Upgrade**
- Pi polls cloud every 24 hours: `GET /api/v1/tier/status`
- Cloud returns: `{"tier": 2, "status": "active", "expires_at": "2026-03-16T10:00:00Z"}`
- Pi updates `/opt/d3kos/config/license.json`:
  ```json
  {
    "installation_id": "550e8400e29b41d4",
    "tier": 2,
    "subscription_status": "active",
    "subscription_expires_at": "2026-03-16T10:00:00Z"
  }
  ```
- Pi enables Tier 2 features (OTA updates, cloud backup, AI analysis)
- User sees "Premium Features Unlocked" notification on d3kOS UI

---

##### **Tier 2 → Tier 3 Upgrade (Annual)**

Same flow as Tier 1 → Tier 2, but:
- Product ID: `com.d3kos.tier3.annual` (iOS) or `tier3_annual` (Android)
- Price: $99.99/year
- Billing interval: `year`
- Additional features: Unlimited resets, multi-boat support, fleet management

---

#### Subscription Management in Mobile App

**Settings → Subscription Page**:

```
┌─────────────────────────────────────┐
│  Premium Subscription               │
│                                     │
│  ✓ Tier 2 - Premium Monthly        │
│  Status: Active                     │
│                                     │
│  Next billing: March 16, 2026       │
│  Amount: $9.99/month                │
│                                     │
│  Payment method: •••• 4242          │
│                                     │
│  [ Upgrade to Annual ]              │
│  [ Manage Subscription ]            │
│  [ Cancel Subscription ]            │
│                                     │
│  Payment History                    │
│  ─────────────────────────────────  │
│  Feb 16, 2026 - $9.99 ✓ Paid      │
│  Jan 16, 2026 - $9.99 ✓ Paid      │
│  Dec 16, 2025 - $9.99 ✓ Paid      │
└─────────────────────────────────────┘
```

**"Manage Subscription" Button Actions**:
- **Stripe**: Opens Stripe Customer Portal URL in browser
  - Update payment method
  - View invoices
  - Change billing interval (monthly ↔ annual)
  - Cancel subscription
- **Apple IAP**: Opens iOS Settings → Subscriptions
- **Google Play**: Opens Google Play → Subscriptions

**"Cancel Subscription" Flow**:
1. User taps "Cancel Subscription"
2. App shows confirmation dialog:
   ```
   Cancel Premium Subscription?

   Your subscription will remain active until
   March 16, 2026. After that, you'll be
   downgraded to Tier 1 (Free).

   [ Keep Subscription ]  [ Confirm Cancel ]
   ```
3. If confirmed, app calls: `POST /api/v1/subscription/cancel`
4. Backend marks subscription: `status = 'canceled'`, `canceled_at = NOW()`
5. Subscription remains active until `current_period_end`
6. On expiration, backend downgrades: `tier = 1`, `is_paid_tier = FALSE`
7. Pi detects downgrade on next poll, disables Tier 2 features

---

#### Failed Payment Handling & Grace Period

**Payment Failure Flow**:
1. Stripe/Apple/Google attempts to charge subscription renewal
2. Payment fails (expired card, insufficient funds, etc.)
3. Webhook fired: `invoice.payment_failed` (Stripe) or equivalent
4. Backend increments `payment_failed_count`
5. Backend sets `status = 'past_due'`
6. Backend sends email to user: "Payment failed - please update payment method"
7. Mobile app shows banner: "⚠️ Payment Issue - Update Payment Method"

**Grace Period Logic**:
- **1st failure** (Day 0): Retry in 3 days, send email notification
- **2nd failure** (Day 3): Retry in 7 days (total: 10 days), send warning email
- **3rd failure** (Day 10): Retry in 14 days (total: 24 days), send final warning
- **4th failure** (Day 24): Subscription expires, downgrade tier

**During Grace Period** (status = `past_due`):
- Tier 2/3 features **remain active** (user can continue using)
- Mobile app shows persistent warning banner
- Email notifications sent before each retry
- User can update payment method via Stripe Portal / Apple / Google

**After Grace Period Expiration**:
- Backend sets: `status = 'expired'`, `expires_at = NOW()`
- Backend downgrades: `tier = 1` (or `tier = 0` if no mobile app paired)
- Backend sets: `is_paid_tier = FALSE`
- Pi polls cloud, detects downgrade
- Pi updates `license.json`, disables Tier 2/3 features
- Mobile app shows: "Subscription expired - features locked"
- User can reactivate by tapping "Reactivate Subscription"

---

#### API Endpoints for E-commerce Integration

**Stripe**:
- `POST /api/v1/stripe/checkout/session` - Create checkout session
- `POST /api/v1/webhooks/stripe` - Receive Stripe webhooks
- `GET /api/v1/stripe/customer-portal` - Get Stripe portal URL

**Apple IAP**:
- `POST /api/v1/apple/verify-receipt` - Validate App Store receipt
- `POST /api/v1/webhooks/apple` - Receive Apple server-to-server notifications

**Google Play**:
- `POST /api/v1/google/verify-purchase` - Validate Google Play purchase
- `POST /api/v1/webhooks/google` - Receive Google RTDN (via Pub/Sub)

**PayPal**:
- `POST /api/v1/paypal/create-subscription` - Create PayPal subscription
- `POST /api/v1/webhooks/paypal` - Receive PayPal webhooks

**Tier Management** (used by all platforms):
- `GET /api/v1/tier/status` - Get current tier and subscription status
- `POST /api/v1/tier/upgrade` - Manual tier upgrade (admin only)
- `POST /api/v1/subscription/cancel` - Cancel active subscription
- `POST /api/v1/subscription/reactivate` - Reactivate canceled subscription
- `GET /api/v1/subscription/history` - Get payment history

---

#### Testing Requirements

**Stripe Testing**:
- Use Stripe test mode API keys
- Test card: `4242 4242 4242 4242` (success)
- Test card: `4000 0000 0000 9995` (payment failure)
- Webhook testing: Use Stripe CLI for local webhook forwarding

**Apple IAP Testing**:
- Use Sandbox environment (separate Apple ID required)
- StoreKit Configuration file for local testing (Xcode 12+)
- Test scenarios: purchase, renewal, cancellation, restore

**Google Play Testing**:
- Use test tracks (Internal, Closed, Open)
- License testing accounts (can make purchases without charges)
- Test scenarios: purchase, renewal, cancellation, restore

**End-to-End Testing**:
1. ✅ Purchase Tier 2 via Stripe → tier upgrades on Pi
2. ✅ Purchase Tier 2 via Apple IAP → tier upgrades on Pi
3. ✅ Purchase Tier 2 via Google Play → tier upgrades on Pi
4. ✅ Subscription renewal succeeds → tier remains active
5. ✅ Subscription renewal fails → grace period activated
6. ✅ 3 failed payments → tier downgraded after 24 days
7. ✅ User cancels subscription → tier remains active until expiration
8. ✅ Subscription expires → tier downgraded immediately
9. ✅ User reactivates subscription → tier re-upgraded
10. ✅ Upgrade from Tier 2 → Tier 3 → price difference handled correctly

---

### Version Management & Upgrade System

**Current d3kOS Version**: 0.9.1-beta (GitHub: `SkipperDon/d3kos`)

**Purpose**: Track d3kOS software version, check GitHub for updates, and enable tier-based over-the-air (OTA) upgrades via mobile app approval.

---

#### Version Tracking

**Version Storage Locations**:

1. **`/opt/d3kos/VERSION`** - Plain text file
   ```
   0.9.1-beta
   ```

2. **`/opt/d3kos/config/license.json`** - Full version metadata
   ```json
   {
     "installation_id": "3861513b314c5ee7",
     "version": "0.9.1-beta",
     "version_installed_at": "2026-02-17T10:00:00Z",
     "tier": 2,
     ...
   }
   ```

**Version Format**: `MAJOR.MINOR.PATCH-STAGE`
- Example: `0.9.1-beta`, `1.0.0-stable`, `1.2.3-rc1`
- Follows semantic versioning

---

#### Tier-Based Upgrade Capabilities

| Tier | Can Upgrade? | Method | User Action Required |
|------|--------------|--------|---------------------|
| **Tier 0** | ❌ NO | Must download new image | Re-flash SD card, re-run Initial Setup |
| **Tier 1** | ❌ NO | Must download new image | Re-flash SD card, restore config via mobile app |
| **Tier 2** | ✅ YES | OTA via mobile app | Approve upgrade in app → automatic curl-based install |
| **Tier 3** | ✅ YES | OTA via mobile app | Approve upgrade in app → automatic curl-based install |

**Rationale**:
- **Tier 0**: No mobile app = no upgrade trigger mechanism, prevents incremental updates
- **Tier 1**: Free tier limitation (encourages Tier 2 upgrade for convenience)
- **Tier 2/3**: Paid tiers get OTA upgrade convenience as premium feature

---

#### GitHub Release Structure

**Repository**: `https://github.com/SkipperDon/d3kos`

**Release Tag Format**: `vMAJOR.MINOR.PATCH-STAGE`
- Example: `v0.9.1-beta`

**Release Assets Required**:
1. `d3kos-upgrade.tar.gz` - Upgrade package
2. `d3kos-upgrade.tar.gz.sha256` - Checksum file

**Upgrade Package Contents**:
```
d3kos-upgrade/
├── install.sh              # Installation script
├── pre-upgrade.sh          # Pre-upgrade checks (optional)
├── post-upgrade.sh         # Post-upgrade tasks (optional)
├── services/               # Updated service files
├── scripts/                # Updated scripts
├── html/                   # Updated web UI files
└── etc/                    # Updated system configs
```

---

#### System Management API (Port 8095)

**Service**: `d3kos-system-api.service`
**File**: `/opt/d3kos/services/system/system-api.py`
**Nginx Proxy**: `/system/` → `localhost:8095/system/`

**Endpoints**:

##### GET /system/version
Returns current d3kOS version and tier
```json
{
  "success": true,
  "version": "0.9.1-beta",
  "version_installed_at": "2026-02-17T10:00:00Z",
  "tier": 2,
  "installation_id": "3861513b314c5ee7"
}
```

##### GET /system/check-update
Checks GitHub for latest release
```json
{
  "success": true,
  "current_version": "0.9.1-beta",
  "latest_version": "0.9.2-beta",
  "update_available": true,
  "release_url": "https://github.com/USER/d3kos/releases/tag/v0.9.2-beta",
  "release_notes": "## What's New\n- Bug fixes\n- Performance improvements",
  "published_at": "2026-02-20T15:30:00Z",
  "tier": 2
}
```

**Tier 0 Response** (403 Forbidden):
```json
{
  "success": false,
  "error": "Updates require Tier 1 or higher",
  "tier": 0
}
```

##### POST /system/upgrade
Triggers upgrade process (Tier 1+ only, requires authentication)

**Request**:
```json
{
  "installation_id": "3861513b314c5ee7"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Upgrade started",
  "log_file": "/opt/d3kos/logs/upgrade.log",
  "note": "System will restart after upgrade completes"
}
```

**Tier 0 Response** (403 Forbidden):
```json
{
  "success": false,
  "error": "Upgrades require Tier 1 or higher",
  "tier": 0
}
```

##### GET /system/upgrade-status
Monitor upgrade progress
```json
{
  "success": true,
  "log_tail": "[2026-02-20 10:15:32] Downloading upgrade package...\n[2026-02-20 10:15:45] Verifying checksum...\n[2026-02-20 10:15:46] ✓ Checksum verified",
  "log_file": "/opt/d3kos/logs/upgrade.log"
}
```

---

#### Mobile App Upgrade Flow (Tier 2/3 Only)

**Step-by-Step Process**:

1. **App Checks Tier**
   - GET `/tier/status`
   - If Tier 0 or 1: Show "Upgrade to Tier 2 for automatic updates"
   - If Tier 2 or 3: Continue

2. **App Checks for Updates**
   - GET `/system/check-update`
   - Compare `current_version` vs `latest_version`

3. **Update Available → Prompt User**
   ```
   ┌─────────────────────────────────────┐
   │  Update Available                   │
   │  Current: 0.9.1-beta                │
   │  Latest:  0.9.2-beta                │
   │                                     │
   │  Release Notes:                     │
   │  • Bug fixes                        │
   │  • Performance improvements         │
   │                                     │
   │  [ View Details ]  [ Install Now ]  │
   └─────────────────────────────────────┘
   ```

4. **User Approves → App Triggers Upgrade**
   - POST `/system/upgrade` with `installation_id`
   - Pi executes `/opt/d3kos/scripts/upgrade.sh` in background

5. **App Polls Status**
   - GET `/system/upgrade-status` every 5 seconds
   - Display log tail to user
   - Show progress spinner

6. **Upgrade Completes**
   - Pi services restart
   - App detects version change
   - Show success message

---

#### Upgrade Script (`/opt/d3kos/scripts/upgrade.sh`)

**Automated Process**:

1. ✅ Check internet connection
2. ✅ Fetch latest release from GitHub API
3. ✅ Download upgrade package (`d3kos-upgrade.tar.gz`)
4. ✅ Download checksum (`d3kos-upgrade.tar.gz.sha256`)
5. ✅ Verify checksum (SHA-256)
6. ✅ Create backup (`/opt/d3kos/backups/upgrade-YYYYMMDD-HHMMSS/`)
   - Config files (`/opt/d3kos/config/`)
   - Data files (`/opt/d3kos/data/`)
   - License file (`license.json`)
7. ✅ Extract upgrade package
8. ✅ Run pre-upgrade checks (if `pre-upgrade.sh` exists)
9. ✅ Stop d3kOS services
10. ✅ Install upgrade (`install.sh`)
11. ✅ Update version in `license.json`
12. ✅ Run post-upgrade tasks (if `post-upgrade.sh` exists)
13. ✅ Restart services
14. ✅ Verify critical services started
15. ✅ Cleanup temp files
16. ✅ Log completion

**Backup Location**: `/opt/d3kos/backups/upgrade-YYYYMMDD-HHMMSS/`

**Log File**: `/opt/d3kos/logs/upgrade.log`

---

#### Security & Safety

**Authentication**:
- Upgrade API requires `installation_id` in request body
- Prevents unauthorized upgrades

**Checksum Verification**:
- SHA-256 hash verification before installation
- Prevents corrupted/tampered packages

**Automatic Backup**:
- All config and data files backed up before upgrade
- Rollback possible if upgrade fails

**Service Verification**:
- Critical services checked after upgrade
- Failed services logged for troubleshooting

**Tier Enforcement**:
- API returns 403 Forbidden for Tier 0/1 upgrade attempts
- Only Tier 2/3 can trigger upgrades

---

#### Rollback Process (Manual)

If upgrade fails, restore from backup:

```bash
# 1. Stop services
sudo systemctl stop d3kos-*.service

# 2. Restore config
sudo cp -r /opt/d3kos/backups/upgrade-YYYYMMDD-HHMMSS/config/* /opt/d3kos/config/

# 3. Restore data
sudo cp -r /opt/d3kos/backups/upgrade-YYYYMMDD-HHMMSS/data/* /opt/d3kos/data/

# 4. Restore license
sudo cp /opt/d3kos/backups/upgrade-YYYYMMDD-HHMMSS/license.json /opt/d3kos/config/

# 5. Restart services
sudo systemctl restart d3kos-*.service
```

---

#### Version Update Scenarios

**Scenario 1: Tier 0 User Wants to Update**
- Download new d3kOS image from GitHub releases
- Flash SD card with new image
- Boot Pi
- Re-run Initial Setup wizard (all 20 steps)
- Configuration NOT preserved

**Scenario 2: Tier 1 User Wants to Update**
- Download new d3kOS image from GitHub releases
- Flash SD card with new image
- Boot Pi and open mobile app
- App detects matching `installation_id`
- App prompts "Restore previous configuration?"
- User taps "Restore" → app sends config to Pi
- Configuration preserved, skip Initial Setup wizard

**Scenario 3: Tier 2/3 User Wants to Update**
- Open mobile app
- App shows "Update Available: 0.9.2-beta"
- User taps "Install Now"
- App sends upgrade request to Pi
- Pi downloads, verifies, installs upgrade automatically
- Services restart, app shows "Upgrade Complete"
- Configuration automatically preserved

---

#### First-Time Installation (All Tiers)

**Initial Image Flash**:
- Version set during first boot by `/opt/d3kos/scripts/generate-installation-id.sh`
- Reads version from `/opt/d3kos/VERSION`
- Writes to `license.json` with `version_installed_at` timestamp

**Example**:
```json
{
  "installation_id": "3861513b314c5ee7",
  "version": "0.9.1-beta",
  "version_installed_at": "2026-02-17T10:00:00Z",
  "tier": 0
}
```

---

### AI-Powered Self-Healing System

**Purpose**: Automatically detect, diagnose, and remediate system issues with minimal user intervention. Critical for marine environments where technical support is limited and non-technical boat operators need reliable, self-maintaining systems.

---

#### Architecture Overview

**5-Tier Self-Healing Architecture**:

```
┌─────────────────────────────────────────────────────┐
│           AI-Powered Self-Healing System             │
└─────────────────────────────────────────────────────┘
                         ↓
    ┌──────────────────────────────────────────┐
    │  Tier 1: Detection Layer                 │
    │  - Engine anomaly detector               │
    │  - Pi health monitor (CPU, mem, disk)    │
    │  - Service status checker                │
    │  - Network monitor                       │
    └──────────────────────────────────────────┘
                         ↓
    ┌──────────────────────────────────────────┐
    │  Tier 2: Correlation Engine              │
    │  - Pattern matching (known failure modes)│
    │  - Time-window correlation               │
    │  - Root cause analysis                   │
    └──────────────────────────────────────────┘
                         ↓
    ┌──────────────────────────────────────────┐
    │  Tier 3: AI Diagnosis (AI Assistant)     │
    │  - Send anomalies + context to AI        │
    │  - Get diagnosis and suggestions         │
    │  - Confidence scoring                    │
    └──────────────────────────────────────────┘
                         ↓
    ┌──────────────────────────────────────────┐
    │  Tier 4: Auto-Remediation Engine         │
    │  - Safe actions (auto-execute)           │
    │  - Risky actions (require approval)      │
    │  - Action logging                        │
    │  - Rollback capability                   │
    └──────────────────────────────────────────┘
                         ↓
    ┌──────────────────────────────────────────┐
    │  Tier 5: User Notification               │
    │  - Translate technical errors            │
    │  - Voice alerts ("Helm alert: ...")      │
    │  - Dashboard banners                     │
    │  - Remediation history page              │
    └──────────────────────────────────────────┘
```

---

#### Tier 1: Detection (What's Wrong?)

**Engine Anomaly Detection** (from NMEA2000):

**Baseline Establishment**:
- File: `/opt/d3kos/config/benchmark-results.json`
- Collected during first engine run after onboarding (30 minutes)
- Metrics: RPM (idle/cruise), oil pressure, coolant temp, fuel rate, voltage

**Statistical Process Control (SPC)**:
```javascript
function detectAnomaly(current, baseline) {
  const deviation = Math.abs(current.value - baseline.mean);
  const sigma = baseline.stddev;

  if (deviation > 3 * sigma) {
    return {
      level: 'CRITICAL',
      message: `${current.name} is ${deviation.toFixed(1)} units from baseline (>3σ)`,
      type: 'ENGINE_ANOMALY'
    };
  } else if (deviation > 2 * sigma) {
    return {
      level: 'WARNING',
      message: `${current.name} is ${deviation.toFixed(1)} units from baseline (>2σ)`,
      type: 'ENGINE_ANOMALY'
    };
  }

  return { level: 'NORMAL', message: null };
}
```

**Example Anomalies**:
- RPM Instability: `stddev > 2 × baseline_stddev` → "Engine running rough"
- High Temperature: `temp > baseline + 15°F` → "Coolant temperature high"
- Low Oil Pressure: `pressure < baseline - 5 PSI` → "Oil pressure low"

**Pi System Monitoring** (every 10 seconds):

**Metrics Collected**:
- CPU temperature (`vcgencmd measure_temp`)
- CPU usage (top -bn1)
- Memory usage (free)
- Disk free space (df -h)
- GPU temperature
- Throttling status (vcgencmd get_throttled)

**Thresholds**:
```javascript
const thresholds = {
  cpu_temp: { warning: 70, critical: 80 },    // °C
  cpu_usage: { warning: 70, critical: 90 },   // %
  memory_usage: { warning: 70, critical: 90 }, // %
  disk_free: { warning: 30, critical: 15 }     // % remaining
};
```

**Service Status Monitoring**:
- CAN interface (can0 up/down)
- Signal K (systemctl is-active)
- Node-RED (systemctl is-active)
- All d3kos-*.service processes
- Network connectivity (ping 8.8.8.8)

---

#### Tier 2: Correlation (Why Did It Happen?)

**Pattern Matching** (known failure modes):

```javascript
const failure_patterns = {
  FAILING_SD_CARD: {
    symptoms: ["DISK_IO_SPIKE", "NETWORK_DROPPED", "SERVICE_CRASHED"],
    time_window: 10,  // seconds
    confidence: 0.85,
    explanation: "Network dropped at same time disk I/O spiked - likely failing SD card"
  },

  OVERHEATING: {
    symptoms: ["CPU_TEMP_HIGH", "THROTTLED", "SLOW_RESPONSE"],
    time_window: 60,
    confidence: 0.90,
    explanation: "CPU overheating causing throttling and slow response"
  },

  LOW_POWER: {
    symptoms: ["UNDERVOLTAGE", "USB_DEVICE_DISCONNECT", "RANDOM_REBOOT"],
    time_window: 5,
    confidence: 0.95,
    explanation: "Power supply issue - use official 5V 3A adapter"
  },

  STUCK_PROCESS: {
    symptoms: ["CPU_100_PERCENT", "PROCESS_AGE_5MIN", "NO_USER_ACTIVITY"],
    time_window: 300,  // 5 minutes
    confidence: 0.85,
    explanation: "Process stuck in infinite loop or deadlock"
  }
};
```

**Correlation Engine**:
```javascript
function correlateEvents(events, time_window_seconds) {
  const grouped = [];

  for (const pattern_name in failure_patterns) {
    const pattern = failure_patterns[pattern_name];
    const matches = events.filter(e =>
      pattern.symptoms.includes(e.type) &&
      e.timestamp > (Date.now() - pattern.time_window * 1000)
    );

    if (matches.length >= 2) {  // At least 2 symptoms match
      grouped.push({
        root_cause: pattern_name,
        confidence: pattern.confidence,
        evidence: matches,
        explanation: pattern.explanation
      });
    }
  }

  // Return highest confidence match
  return grouped.sort((a, b) => b.confidence - a.confidence)[0];
}
```

---

#### Tier 3: AI Diagnosis

**AI Integration** (uses existing AI Assistant):

```javascript
async function diagnoseWithAI(system_state, anomalies, recent_events) {
  const diagnosis_request = {
    system_state: {
      cpu_temp: system_state.cpu_temp,
      cpu_usage: system_state.cpu_usage,
      memory_free: system_state.memory_free,
      disk_free: system_state.disk_free,
      services: system_state.services,  // { signalk: "running", nodered: "crashed", ... }
      engine_metrics: system_state.engine_metrics
    },
    anomalies: anomalies,  // [{ type: "CPU_OVERHEATING", severity: "WARNING" }, ...]
    recent_events: recent_events,  // ["User started camera recording 2 min ago", ...]
    patterns_detected: correlateEvents(anomalies, 60)
  };

  // Send to AI Assistant with special diagnostic prompt
  const ai_response = await fetch('/ai/diagnose', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query: `System health diagnostic needed. Analyze the following system state and anomalies, then provide root cause analysis and suggested fixes.`,
      context: diagnosis_request
    })
  });

  const result = await ai_response.json();

  return {
    root_cause: result.root_cause,
    explanation: result.explanation,
    suggested_fixes: result.suggested_fixes,  // [{ action, confidence, user_message }, ...]
    confidence: result.confidence
  };
}
```

**AI Diagnostic Prompt** (added to AI Assistant):
```
You are a marine system diagnostician. Analyze system health data and provide:
1. Root cause of the issue (single most likely cause)
2. Plain English explanation (non-technical, boat operator friendly)
3. Suggested fixes (prioritized by confidence)
4. User action needed (if any)

Be concise. Focus on marine safety and reliability.
```

---

#### Tier 4: Auto-Remediation (Fix It Automatically)

**Remediation Actions** (safe, reversible):

```javascript
const remediation_actions = {
  RESTART_SERVICE: {
    severity_threshold: "CRITICAL",
    requires_approval: false,  // Auto-execute
    command: "systemctl restart {service_name}",
    rollback: "systemctl stop {service_name}",
    timeout: 30  // seconds
  },

  KILL_STUCK_PROCESS: {
    severity_threshold: "CRITICAL",
    requires_approval: false,  // Auto-execute
    command: "kill -9 {pid}",
    conditions: ["cpu_usage > 90%", "process_age > 5min"],
    timeout: 5
  },

  STOP_CAMERA_RECORDING: {
    severity_threshold: "WARNING",
    requires_approval: true,  // Ask user first
    command: "curl -X POST http://localhost:8084/camera/record/stop",
    timeout: 10
  },

  CLEAR_TEMP_FILES: {
    severity_threshold: "WARNING",
    requires_approval: false,  // Auto-execute
    command: "find /tmp -type f -atime +7 -delete",
    timeout: 60
  },

  INITIAL_SETUP_RESET: {
    severity_threshold: "CRITICAL",
    requires_approval: true,  // ALWAYS ask user
    command: "/opt/d3kos/scripts/factory-reset.sh",
    timeout: 30
  }
};
```

**Auto-Remediation Flow**:
```javascript
async function executeRemediation(action_name, params) {
  const action = remediation_actions[action_name];

  // Check if approval required
  if (action.requires_approval) {
    const approved = await askUserApproval(action_name, params);
    if (!approved) {
      log(`Remediation ${action_name} cancelled by user`);
      return { success: false, reason: "User declined" };
    }
  }

  // Log action
  logRemediation({
    action: action_name,
    params: params,
    timestamp: Date.now(),
    auto_executed: !action.requires_approval
  });

  // Execute command
  try {
    const result = await executeCommand(action.command, params, action.timeout);

    // Verify fix worked
    const verified = await verifyRemediationSuccess(action_name, params);

    if (verified) {
      notifyUser(`✅ Issue resolved: ${action_name}`, "success");
      return { success: true, result: result };
    } else {
      // Rollback if verification failed
      if (action.rollback) {
        await executeCommand(action.rollback, params, action.timeout);
      }
      notifyUser(`⚠️ Remediation failed: ${action_name}`, "warning");
      return { success: false, reason: "Verification failed" };
    }

  } catch (error) {
    notifyUser(`❌ Remediation error: ${action_name}`, "error");
    return { success: false, reason: error.message };
  }
}
```

**Example Auto-Remediation**:
```
1. Detect: Node-RED process using 100% CPU for 5 minutes
2. Correlate: Stuck process pattern detected (confidence: 85%)
3. AI Diagnose: "Node-RED flow likely in infinite loop"
4. Auto-Remediate (no approval needed):
   ✓ Kill process (PID 1234)
   ✓ Restart service: systemctl restart nodered
   ✓ Verify: Node-RED running, CPU usage normal
   ✓ Log action: /var/log/d3kos-remediation.log
   ✓ Notify user: "Node-RED was stuck and has been restarted"
```

---

#### Tier 5: User-Friendly Notifications

**Error Translation** (technical → plain English):

```javascript
const error_translations = {
  "systemd[1]: your-app.service: Main process exited, code=killed, status=9/KILL":
    "The main program crashed and had to be stopped. Restarting now.",

  "vcgencmd: throttled=0x50000":
    "Power supply issue detected. Use official 5V 3A power adapter.",

  "can0: No such device":
    "NMEA2000 connection lost. Check CAN bus wiring.",

  "Out of memory: Killed process 1234 (node)":
    "System ran out of memory and stopped Node-RED. Try closing other programs.",

  "SD card I/O error":
    "SD card may be failing. Back up data and replace card soon.",

  "CPU temperature 85°C (expected 45°C)":
    "System is overheating. Improve ventilation or reduce workload."
};

function translateForUser(technical_error) {
  const plain_english = error_translations[technical_error] ||
                        "Something went wrong with the system.";

  return {
    display: plain_english,
    voice: plain_english,
    action_taken: "System automatically fixed the issue.",
    user_action_needed: "None - monitoring for repeat issues."
  };
}
```

**Voice Alerts** (Tier 2+ only):
```javascript
async function voiceAlert(message, severity) {
  if (tier < 2) return;  // Voice requires Tier 2+

  const voice_message = `Helm alert: ${message}`;

  // Text-to-speech via Piper
  await textToSpeech(voice_message);

  // Log alert
  logAlert({
    message: message,
    severity: severity,
    voice_alert_sent: true,
    timestamp: Date.now()
  });
}
```

**Dashboard Notifications**:
```html
<!-- Self-Healing Banner (top of dashboard) -->
<div id="healing-banner" class="banner banner-success" style="display: none;">
  <span id="healing-message">✅ Issue resolved: Node-RED restarted</span>
  <button onclick="viewRemediationHistory()">View Details</button>
  <button onclick="closeBanner()">×</button>
</div>
```

**Remediation History Page** (`/remediation-history.html`):
```
┌─────────────────────────────────────────┐
│  Self-Healing History                   │
├─────────────────────────────────────────┤
│  Feb 17, 2026 2:15 PM                   │
│  ✅ Node-RED Restarted                  │
│  Issue: Process stuck (100% CPU)        │
│  Action: Automatic restart              │
│  Result: Successful                     │
│  [ View Details ]                       │
├─────────────────────────────────────────┤
│  Feb 17, 2026 11:30 AM                  │
│  ✅ Disk Space Cleared                  │
│  Issue: Disk 92% full                   │
│  Action: Deleted temp files             │
│  Result: 78% full (14% freed)           │
│  [ View Details ]                       │
├─────────────────────────────────────────┤
│  Feb 16, 2026 6:45 PM                   │
│  ⚠️ User Declined Action                │
│  Issue: Camera using excessive CPU      │
│  Suggested: Stop camera recording       │
│  Result: User declined, issue persists  │
│  [ View Details ]                       │
└─────────────────────────────────────────┘
```

---

#### Tier-Based Features

| Feature | Tier 0 | Tier 1 | Tier 2 | Tier 3 |
|---------|--------|--------|--------|--------|
| **Detection** | ✅ Basic | ✅ Full | ✅ Full | ✅ Full |
| **Correlation** | ✅ Local | ✅ Local | ✅ Local + Cloud | ✅ Local + Cloud |
| **AI Diagnosis** | ❌ No | ⚠️ Limited | ✅ Full | ✅ Full + Priority |
| **Auto-Remediation** | ⚠️ Manual only | ⚠️ Manual only | ✅ Safe actions auto | ✅ All actions auto |
| **Voice Alerts** | ❌ No | ❌ No | ✅ Yes | ✅ Yes |
| **History Tracking** | ✅ 30 days | ✅ 90 days | ✅ 1 year | ✅ Unlimited |
| **Predictive Maintenance** | ❌ No | ❌ No | ✅ Basic | ✅ Advanced |

---

#### Implementation Status

**Current Status**: ⏳ NOT IMPLEMENTED (Specification Only)

**Estimated Development**: 30-40 hours
- Phase 1: Enhanced Health Monitoring (8-10 hours)
- Phase 2: Anomaly Detection (6-8 hours)
- Phase 3: AI Integration (8-10 hours)
- Phase 4: Auto-Remediation (6-8 hours)
- Phase 5: User Interface (6-8 hours)

**Files to Create**:
- `/opt/d3kos/services/health/health-monitor.py` - Detection layer
- `/opt/d3kos/services/health/correlation-engine.py` - Pattern matching
- `/opt/d3kos/services/health/remediation-engine.py` - Auto-fix actions
- `/opt/d3kos/services/ai/ai_diagnostic.py` - AI diagnosis integration
- `/var/www/html/remediation-history.html` - User interface
- `/var/log/d3kos-remediation.log` - Action log

**Why This is Critical for d3kOS**:
1. ✅ Marine environments have limited technical support
2. ✅ Boat operators are often non-technical users
3. ✅ Safety-critical - engine/system failures at sea are dangerous
4. ✅ Offline-capable (rule-based + cached AI responses)
5. ✅ Unique differentiator - no other marine system has AI self-healing

---

### Timezone Auto-Detection System

**Purpose**: Automatically configure correct timezone on first boot to prevent hardcoded Toronto time issue. Critical for worldwide deployment to ensure accurate timestamps in boatlogs, health monitoring, data exports, and GPS synchronization.

**Current Problem**: Timezone hardcoded to America/Toronto (EST/EDT) in base image, causing wrong timestamps for users in other locations.

---

#### Auto-Detection Flow (First Boot)

**3-Tier Detection** (no user interaction):

```
First Boot
    ↓
┌─────────────────────────────────────────┐
│  Tier 1: GPS Coordinate Detection      │
│  Wait up to 30 seconds for GPS fix     │
└─────────────────────────────────────────┘
    ↓
GPS fix acquired?
    ↓
YES ─┐                    NO
     ↓                     ↓
┌──────────────┐    ┌─────────────────────┐
│  Use GPS     │    │  Tier 2: Internet   │
│  lat/lon →   │    │  Geolocation API    │
│  timezone    │    │  (IP-based)         │
└──────────────┘    └─────────────────────┘
     ↓                     ↓
     │              Internet available?
     │                     ↓
     │              YES ─┐         NO
     │                   ↓          ↓
     │         ┌──────────────┐  ┌────────────┐
     │         │  Use IP geo  │  │  Tier 3:   │
     │         │  timezone    │  │  Default   │
     │         └──────────────┘  │  to UTC    │
     ↓                   ↓        └────────────┘
┌─────────────────────────────────────────┐
│  Set System Timezone                    │
│  timedatectl set-timezone <timezone>    │
│  Save to /opt/d3kos/config/timezone.txt │
└─────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────┐
│  Continue to Onboarding Wizard          │
│  (No timezone question - automatic)     │
└─────────────────────────────────────────┘
```

---

#### Detection Methods

##### Method 1: GPS Coordinates (BEST)

**How it works**:
```javascript
// GPS provides UTC time + coordinates
const gps_data = {
  utc_time: "2026-02-17T23:30:00Z",
  latitude: 28.5383,   // Miami, Florida
  longitude: -81.3792
};

// Lookup timezone from coordinates
// Uses GeoNames API: http://api.geonames.org/timezoneJSON
const response = await fetch(
  `http://api.geonames.org/timezoneJSON?lat=${gps_data.latitude}&lng=${gps_data.longitude}&username=d3kos`
);
const data = await response.json();
const timezone = data.timezoneId;  // "America/New_York"

// Set system timezone
await setSystemTimezone(timezone);
```

**Advantages**:
- ✅ Most accurate (GPS = ground truth)
- ✅ Works offline (no internet needed after initial lookup)
- ✅ Automatic (no user input)
- ✅ Updates as boat crosses timezone boundaries

**Timeout**: 30 seconds maximum wait for GPS fix

---

##### Method 2: Internet Geolocation (FALLBACK)

**How it works**:
```javascript
// Use IP address to determine timezone
const response = await fetch('http://worldtimeapi.org/api/ip');
const data = await response.json();

// Response includes timezone
{
  "timezone": "America/New_York",
  "utc_offset": "-05:00",
  "dst": true,
  "datetime": "2026-02-17T18:30:00-05:00"
}

// Set system timezone
await setSystemTimezone(data.timezone);
```

**Free APIs** (no API key required):
- `http://worldtimeapi.org/api/ip` (rate limit: 100 req/min)
- `http://ip-api.com/json/` (rate limit: 45 req/min)

**Advantages**:
- ✅ Fast (< 1 second)
- ✅ Works before GPS fix acquired
- ✅ Automatic (no user input)

**Disadvantages**:
- ⚠️ Less accurate than GPS (IP location ≠ actual location)
- ❌ Requires internet

---

##### Method 3: Default to UTC (LAST RESORT)

If both GPS and internet fail:
```javascript
// Set to UTC as safe default
await setSystemTimezone("UTC");

// Log warning
console.warn("⚠️ Timezone auto-detection failed. Defaulting to UTC.");

// User can manually change later in Settings
```

**UTC Benefits**:
- ✅ Universal time (no DST complications)
- ✅ Safe default for marine use
- ✅ Matches GPS time format

---

#### Manual Override (Settings Page)

**Location**: Settings → System → Timezone

**UI**:
```
┌─────────────────────────────────────────┐
│  Timezone Configuration                 │
├─────────────────────────────────────────┤
│  Current Timezone:                      │
│  America/New_York (Eastern Time)        │
│                                         │
│  Current Time: 6:30 PM                  │
│  UTC Time: 11:30 PM                     │
│                                         │
│  Detection Method: GPS                  │
│  Last Updated: Feb 17, 2026 11:30 PM    │
│                                         │
│  [ Change Timezone ]                    │
└─────────────────────────────────────────┘
```

**Change Timezone Dialog**:
```
┌─────────────────────────────────────────┐
│  Select Timezone                        │
├─────────────────────────────────────────┤
│  Common North American Timezones:       │
│                                         │
│  [ ◉ Eastern Time (US/Canada)     ]     │
│  [ ○ Central Time (US/Canada)     ]     │
│  [ ○ Mountain Time (US/Canada)    ]     │
│  [ ○ Pacific Time (US/Canada)     ]     │
│  [ ○ Atlantic Time (Canada)       ]     │
│  [ ○ Alaska Time                  ]     │
│  [ ○ Hawaii Time                  ]     │
│                                         │
│  Other Regions:                         │
│  [ ○ UK Time (GMT/BST)            ]     │
│  [ ○ Central Europe Time          ]     │
│  [ ○ Australian Eastern Time      ]     │
│  [ ○ UTC (Universal Time)         ]     │
│                                         │
│  [ Show All Timezones (400+) ▼ ]        │
│                                         │
│  [ Cancel ]          [ Save Changes ]   │
└─────────────────────────────────────────┘
```

**Common Timezones List**:
```javascript
const common_timezones = [
  // North America
  { label: "Eastern Time (US/Canada)", value: "America/New_York" },
  { label: "Central Time (US/Canada)", value: "America/Chicago" },
  { label: "Mountain Time (US/Canada)", value: "America/Denver" },
  { label: "Pacific Time (US/Canada)", value: "America/Los_Angeles" },
  { label: "Atlantic Time (Canada)", value: "America/Halifax" },
  { label: "Alaska Time", value: "America/Anchorage" },
  { label: "Hawaii Time", value: "Pacific/Honolulu" },

  // Europe
  { label: "UK Time (GMT/BST)", value: "Europe/London" },
  { label: "Central Europe Time", value: "Europe/Paris" },
  { label: "Eastern Europe Time", value: "Europe/Helsinki" },

  // Australia/NZ
  { label: "Australian Eastern Time", value: "Australia/Sydney" },
  { label: "Australian Central Time", value: "Australia/Adelaide" },
  { label: "Australian Western Time", value: "Australia/Perth" },
  { label: "New Zealand Time", value: "Pacific/Auckland" },

  // Other
  { label: "UTC (Universal Time)", value: "UTC" }
];
```

---

#### Implementation Files

**Detection Script**: `/opt/d3kos/scripts/detect-timezone.sh`
- Tries GPS (30s timeout)
- Falls back to internet geolocation
- Defaults to UTC if all fail
- Logs to `/var/log/d3kos-timezone.log`
- Saves result to `/opt/d3kos/config/timezone.txt`

**First-Boot Service**: `/etc/systemd/system/d3kos-timezone-setup.service`
- Runs before onboarding wizard
- Executes detection script
- Sets system timezone via `timedatectl`

**Config File**: `/opt/d3kos/config/timezone.txt`
```json
{
  "timezone": "America/New_York",
  "detection_method": "GPS",
  "detected_at": "2026-02-17T23:30:00Z",
  "latitude": 28.5383,
  "longitude": -81.3792
}
```

**API Endpoint**: `POST /system/timezone` (port 8095)
- Allows manual timezone change from Settings page
- Updates system timezone and config file
- Validates timezone name against system database

---

#### Status & Priority

**Current Status**: ⏳ NOT IMPLEMENTED (Specification Only)

**Implementation Time**: 4-6 hours
- Detection script: 2 hours
- First-boot service: 1 hour
- Settings UI: 1 hour
- API endpoint: 1 hour
- Testing: 1 hour

**Priority**: High
- Affects all timestamps system-wide
- Critical for accurate boatlog entries
- Legal implications (fishing regulations are time-based)
- User experience issue (wrong time is confusing)

**Workaround Until Implemented**:
- Users must manually run `sudo timedatectl set-timezone <timezone>` via SSH
- Or accept Toronto time and mentally adjust

---

### Data Export & Central Database Sync

**Tier Requirement**: Tier 1, 2, and 3 only (Tier 0 does NOT have export capability)

**Purpose**: Export all boat data in format suitable for central database import, enabling cloud sync, mobile app features, and fleet management.

---

#### Export Data Categories

All exports must include:
- **installation_id** (16-char hex from license.json)
- **export_timestamp** (ISO-8601 format)
- **tier** (1, 2, or 3)
- **format_version** (e.g., "1.0")

**Data Types for Export**:

1. **Engine Benchmark Data**
   - Baseline RPM values (idle, cruise, max)
   - Oil pressure ranges
   - Coolant temperature ranges
   - Performance metrics
   - Anomaly thresholds

2. **Boatlog Entries**
   - Timestamp
   - Entry type (voice, text, auto)
   - Content/transcription
   - GPS coordinates
   - Weather conditions (if logged)

3. **Marine Vision Captures** (Metadata Only - NO Files)
   - Installation ID (system_id)
   - Capture ID (unique per photo)
   - Timestamp (when photo was taken)
   - File size (bytes)
   - Image metadata (resolution, format)
   - Detection results (species, confidence score)
   - Size/legal compliance (if applicable)
   - GPS coordinates
   - **NOTE:** Actual image files are NOT exported to central database. Files are transferred via Tier 1/2/3 mobile app only.

4. **Marine Vision Snapshots** (Metadata Only - NO Files)
   - Installation ID (system_id)
   - Snapshot ID (unique per snapshot)
   - Timestamp (when snapshot was taken)
   - File size (bytes)
   - Camera orientation (degrees)
   - Detection events (object type, count, distance)
   - GPS coordinates
   - **NOTE:** Actual video/snapshot files are NOT exported to central database. Files are transferred via Tier 1/2/3 mobile app only.

5. **QR Code Data**
   - Installation UUID
   - Pairing token
   - Generation timestamp
   - Tier level

6. **Settings Configuration**
   - User preferences
   - Feature toggles
   - Network configuration
   - Alert thresholds

7. **System Alerts**
   - Alert ID
   - Timestamp
   - Alert type (health, anomaly, system)
   - Severity level
   - Message/description
   - Resolved status

8. **Onboarding/Initial Setup Configuration**
   - Installation ID (system_id)
   - All Initial Setup wizard answers (20 steps)
   - Boat information (manufacturer, year, model, chartplotter)
   - Engine information (make, model, year, specs)
   - Regional settings (tank sensors, engine position)
   - Reset counter (resets used, resets remaining)
   - Max resets allowed (10 for Tier 0/1, unlimited for Tier 3)
   - Last reset timestamp
   - **Purpose:** Enables Tier 1 mobile app to restore configuration after d3kOS update

9. **Telemetry & Analytics** (Background Collection)
   - **Tier Requirement:** Tier 1+ only (user consent required)
   - **Collection:** Automatic background service
   - **Privacy:** Anonymized, no personally identifiable information
   - **Retention:** 30 days local, unlimited in central database

   **System Performance Metrics:**
   - Boot time (power-on to fully operational)
   - Memory usage (RAM consumption over time, average/peak)
   - CPU usage patterns (average, peak, idle percentage)
   - Network connectivity status (WiFi/ethernet uptime, latency)
   - Error/crash logs (count, frequency, error types)
   - System uptime between reboots
   - Battery level (if applicable - future UPS integration)
   - Storage usage (SD card %, growth rate)
   - Service restart counts (d3kos-voice, d3kos-ai-api, etc.)

   **User Interaction Data:**
   - Menu navigation patterns (button clicks per menu)
   - Feature usage frequency (which features used most/least)
   - User flow paths (which menus lead to which actions)
   - Abandoned actions (started but not completed)
   - Settings changes frequency and types
   - Voice command success/failure rates
   - Time spent per page/screen (average session duration)
   - Onboarding completion time (first boot to wizard done)

   **AI Assistance Metrics:**
   - Number of AI queries per session (total, average)
   - AI response time/latency (average, p95, p99)
   - Query types/categories (simple vs complex, onboard vs online)
   - Provider usage (OpenRouter vs onboard rules)
   - Cache hit rate (Signal K data caching effectiveness)
   - Follow-up question patterns (chains of related queries)
   - Query abandonment (user closes page before response)

   **Device & Environment:**
   - Connected device count (other devices on 10.42.0.0/24 network)
   - Camera connection status and uptime
   - Time of day usage patterns (hourly heatmap)
   - d3kOS software version
   - Raspberry Pi model and RAM size
   - SD card size and type
   - Network mode (AP mode vs client mode, WiFi vs ethernet)

   **Business Intelligence:**
   - First-time vs returning user patterns
   - Feature adoption rate over time
   - Session duration and frequency (daily, weekly, monthly)
   - Days since installation (installation age)
   - Days since last use (user retention)
   - Tier upgrade events (0→1, 1→2, 2→3)
   - Reset counter trends (approaching limit?)

   **Collection Method:**
   - Background service: `d3kos-telemetry.service` (runs every 5 minutes)
   - Local storage: `/opt/d3kos/data/telemetry/` (SQLite database)
   - Export frequency: Included in daily export (Tier 2+) or manual export (Tier 1)
   - User control: Can disable via Settings → Privacy → Telemetry (still exports if disabled, but anonymized)

---

#### Export File Format

**JSON Structure** (for central database import):

```json
{
  "export_metadata": {
    "installation_id": "abc123def456",
    "export_timestamp": "2026-02-16T14:30:00.000Z",
    "tier": 2,
    "format_version": "1.0",
    "export_type": "full"
  },
  "boat_info": {
    "manufacturer": "Sea Ray",
    "year": 2018,
    "model": "Sundancer 320",
    "engine_make": "Mercury",
    "engine_model": "8.2L Mag HO"
  },
  "benchmark_data": {
    "baseline_rpm": {
      "idle": 700,
      "cruise": 3200,
      "max": 4800
    },
    "oil_pressure": {
      "min": 10,
      "normal": 45,
      "max": 65
    },
    "last_benchmark": "2026-02-10T10:00:00.000Z"
  },
  "boatlog_entries": [
    {
      "entry_id": "log_20260216_143000_001",
      "timestamp": "2026-02-16T14:30:00.000Z",
      "type": "voice",
      "content": "Engine running smooth, heading to marina",
      "gps": {
        "latitude": 43.6817,
        "longitude": -79.5214
      }
    }
  ],
  "marine_vision_captures": [
    {
      "installation_id": "abc123def456",
      "capture_id": "capture_20260216_120000_001",
      "timestamp": "2026-02-16T12:00:00.000Z",
      "file_size_bytes": 524288,
      "file_path_local": "/home/d3kos/camera-recordings/captures/capture_20260216_120000_001.jpg",
      "resolution": "1920x1080",
      "format": "JPEG",
      "species": "Largemouth Bass",
      "confidence": 0.92,
      "size_cm": 38,
      "legal_size": true,
      "bag_limit_check": "within_limit",
      "gps": {
        "latitude": 43.6817,
        "longitude": -79.5214
      }
    }
  ],
  "marine_vision_snapshots": [
    {
      "installation_id": "abc123def456",
      "snapshot_id": "snapshot_20260216_130000_001",
      "timestamp": "2026-02-16T13:00:00.000Z",
      "file_size_bytes": 102400,
      "file_path_local": "/home/d3kos/camera-recordings/snapshots/snapshot_20260216_130000_001.jpg",
      "camera_orientation": 45,
      "detection_events": [
        {
          "object_type": "boat",
          "count": 1,
          "distance_estimate": 150
        }
      ],
      "gps": {
        "latitude": 43.6830,
        "longitude": -79.5250
      }
    }
  ],
  "alerts": [
    {
      "alert_id": "alert_20260216_100000_001",
      "timestamp": "2026-02-16T10:00:00.000Z",
      "type": "anomaly",
      "severity": "warning",
      "message": "Oil pressure below normal range (8 PSI)",
      "resolved": true,
      "resolved_timestamp": "2026-02-16T10:15:00.000Z"
    }
  ],
  "settings": {
    "voice_enabled": true,
    "camera_enabled": true,
    "auto_logging": true,
    "alert_thresholds": {
      "oil_pressure_min": 10,
      "coolant_temp_max": 195
    }
  },
  "onboarding_config": {
    "installation_id": "abc123def456",
    "completed": true,
    "completion_timestamp": "2026-02-10T10:00:00.000Z",
    "reset_count": 2,
    "max_resets": 10,
    "resets_remaining": 8,
    "last_reset_timestamp": "2026-02-10T10:00:00.000Z",
    "wizard_answers": {
      "step_0": "Welcome",
      "step_1": "Sea Ray",
      "step_2": 2018,
      "step_3": "Sundancer 320",
      "step_4": "Garmin GPSMAP 7412xsv",
      "step_5": "Mercury",
      "step_6": "8.2L Mag HO",
      "step_7": 2018,
      "step_8": 8,
      "step_9": "8.2",
      "step_10": "425",
      "step_11": "9.0:1",
      "step_12": 700,
      "step_13": 4800,
      "step_14": "gasoline",
      "step_15": "North America",
      "step_16": "single"
    }
  },
  "telemetry_data": {
    "collection_period": {
      "start": "2026-02-15T00:00:00.000Z",
      "end": "2026-02-16T14:30:00.000Z",
      "duration_hours": 38.5
    },
    "system_performance": {
      "boot_time_seconds": 45.2,
      "average_ram_usage_mb": 1250,
      "peak_ram_usage_mb": 1850,
      "average_cpu_percent": 15.3,
      "peak_cpu_percent": 78.5,
      "network_uptime_percent": 98.2,
      "average_latency_ms": 12,
      "error_count": 3,
      "crash_count": 0,
      "system_uptime_hours": 168.5,
      "reboot_count": 2,
      "storage_used_percent": 85,
      "service_restarts": {
        "d3kos-voice": 0,
        "d3kos-ai-api": 1,
        "d3kos-camera-stream": 2
      }
    },
    "user_interaction": {
      "total_sessions": 15,
      "average_session_duration_minutes": 8.5,
      "menu_clicks": {
        "dashboard": 45,
        "boatlog": 12,
        "navigation": 8,
        "helm": 22,
        "weather": 10,
        "settings": 5,
        "ai_assistant": 18
      },
      "feature_usage": {
        "voice_commands": 5,
        "ai_queries": 23,
        "camera_access": 8,
        "manual_upload": 2
      },
      "abandoned_actions": 3,
      "settings_changes": 4,
      "voice_command_success_rate": 0.80
    },
    "ai_assistance": {
      "total_queries": 23,
      "average_response_time_ms": 850,
      "p95_response_time_ms": 18500,
      "query_types": {
        "simple_patterns": 18,
        "complex_online": 5
      },
      "provider_usage": {
        "rules": 18,
        "openrouter": 5
      },
      "cache_hit_rate": 0.78,
      "follow_up_chains": 4,
      "query_abandonment_rate": 0.04
    },
    "device_environment": {
      "connected_devices_count": 3,
      "camera_uptime_percent": 95.5,
      "usage_by_hour": {
        "00-06": 0,
        "06-12": 5,
        "12-18": 8,
        "18-24": 2
      },
      "software_version": "2.9",
      "hardware": {
        "model": "Raspberry Pi 4B",
        "ram_gb": 8,
        "sd_card_gb": 32
      },
      "network_mode": "ap"
    },
    "business_intelligence": {
      "days_since_installation": 6,
      "days_since_last_use": 0,
      "current_tier": 1,
      "tier_upgrade_history": [
        {
          "from": 0,
          "to": 1,
          "timestamp": "2026-02-11T10:00:00.000Z"
        }
      ],
      "retention_score": 0.92
    }
  }
}
```

**Export File Naming**: `d3kos_export_{installation_id}_{timestamp}.json`

**Example**: `d3kos_export_abc123def456_20260216143000.json`

---

#### Media File Management & Deletion Policy

**IMPORTANT:** Marine vision media files (photos, videos, snapshots) are NOT exported to the central database. Only metadata is exported. Actual media files are transferred via the Tier 1/2/3 mobile app.

**Media Storage Locations:**
- Captures (photos): `/home/d3kos/camera-recordings/captures/`
- Snapshots: `/home/d3kos/camera-recordings/snapshots/`
- Recordings (videos): `/home/d3kos/camera-recordings/`

**Automatic Deletion Policy:**
- **Default:** Media files are deleted after 7 days
- **Low Storage:** Files may be deleted sooner if storage exceeds 90% full
- **Priority:** Oldest files deleted first
- **Notification:** User is notified when automatic deletion occurs

**Storage Management Service:**
- Service: `d3kos-media-cleanup.service`
- Schedule: Daily at 4:00 AM
- Cleanup order:
  1. Files older than 7 days → Delete
  2. If still > 90% full → Delete files older than 5 days
  3. If still > 90% full → Delete files older than 3 days
  4. If still > 95% full → Alert user (critical storage)

**User Notifications:**
- **Daily cleanup:** No notification (silent)
- **Low storage cleanup:** "Media files older than X days deleted due to limited storage."
- **Critical storage:** "Storage critically low. Please transfer media to mobile app or expand SD card."

**Mobile App Transfer:**
- Tier 1/2/3 mobile app can browse and download media files
- App connects to Pi via local network (WiFi)
- HTTPS file transfer with installation_id authentication
- After successful transfer to mobile app, user can manually delete from Pi

**Storage Expansion:**
- Recommend 128GB SD card minimum
- Larger SD cards = longer retention period
- User can adjust retention period in Settings (3, 7, 14, 30 days)

---

#### Export Triggers

**1. Manual Export** (Settings → Data Management → Export All)
- User initiates export
- Creates JSON file in `/opt/d3kos/data/exports/`
- Queues for upload to central database
- Displays success/failure notification

**2. Automatic Export on Boot**
- On system startup, check if pending exports exist
- If `export_queue.json` exists → automatic upload
- Retry failed uploads (max 3 attempts)
- Mark successful uploads in `export_history.json`

**3. Scheduled Export** (Tier 2+ only)
- Daily automatic export at 3:00 AM (if online)
- Incremental export (only new data since last export)
- Background process, no user notification

---

#### Export Queue System

**Queue File**: `/opt/d3kos/data/exports/export_queue.json`

```json
{
  "pending_exports": [
    {
      "export_id": "export_20260216_143000",
      "file_path": "/opt/d3kos/data/exports/d3kos_export_abc123def456_20260216143000.json",
      "created": "2026-02-16T14:30:00.000Z",
      "upload_attempts": 0,
      "status": "pending"
    }
  ]
}
```

**Upload Process**:
1. Check internet connectivity
2. POST export JSON to `https://d3kos-cloud/api/v1/data/import`
3. Wait for 200 OK response with confirmation ID
4. Update queue status to "completed"
5. Move file to `/opt/d3kos/data/exports/archive/`

**Retry Logic**:
- Attempt 1: Immediate (on boot or manual trigger)
- Attempt 2: 5 minutes later
- Attempt 3: 15 minutes later
- After 3 failures: Mark as "failed", require manual retry

---

#### API Endpoints

**Central Database Import**:
- **POST** `/api/v1/data/import`
- **Headers**: `Authorization: Bearer {installation_id}`
- **Body**: Full JSON export (multipart/form-data for images)
- **Response**:
  ```json
  {
    "status": "success",
    "import_id": "import_550e8400e29b41d4",
    "records_imported": 47,
    "timestamp": "2026-02-16T14:30:15.000Z"
  }
  ```

**Export Status Check**:
- **GET** `/api/v1/data/export/status?installation_id={id}`
- **Response**:
  ```json
  {
    "last_export": "2026-02-16T14:30:00.000Z",
    "records_synced": 1247,
    "pending_records": 3
  }
  ```

---

#### UI Implementation

**Settings → Data Management Page**:

```
┌────────────────────────────────────────┐
│ Data Management                         │
├────────────────────────────────────────┤
│                                         │
│ Last Export: Feb 16, 2026 2:30 PM     │
│ Status: ✓ Synced to cloud              │
│                                         │
│ ┌────────────────────────────────────┐ │
│ │   [Export All Data Now]            │ │
│ └────────────────────────────────────┘ │
│                                         │
│ Export History:                         │
│ • Feb 16, 2026 2:30 PM - 47 records    │
│ • Feb 15, 2026 3:00 AM - 23 records    │
│ • Feb 14, 2026 3:00 AM - 15 records    │
│                                         │
│ Pending Uploads: 0                      │
│                                         │
│ ┌────────────────────────────────────┐ │
│ │   [View Export Files]              │ │
│ │   [Clear Export Archive]           │ │
│ └────────────────────────────────────┘ │
└────────────────────────────────────────┘
```

**Boot-time Export Notification**:
- Small notification: "Syncing data to cloud..." (if export pending)
- Success: No notification (silent background sync)
- Failure: "Unable to sync data. Will retry later."

---

#### Storage Management

**Export Directory Structure**:
```
/opt/d3kos/data/exports/
├── export_queue.json          # Pending uploads
├── export_history.json        # Successful uploads log
├── d3kos_export_*.json        # Current pending exports
└── archive/                   # Completed exports (kept 30 days)
    └── d3kos_export_*.json
```

**Cleanup Policy**:
- Archive exports older than 30 days: Delete
- Failed exports after 7 days: Delete
- Successful exports: Move to archive immediately after upload

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

- **Weather Radar** (NEW - 2026-02-13)
  - GPS-based weather display
  - Animated weather radar (Windy.com embed)
  - Real-time marine conditions
  - Open-Meteo Marine API & Weather API
  - **Large Touch-Friendly Map Controls** (80px × 80px):
    - Zoom In (+) / Zoom Out (−) buttons
    - Recenter on Position (⊙) button
    - Wind/Clouds/Radar overlay toggle
    - Positioned right side of map, vertically centered
    - Full touchscreen support with visual feedback
  - **Essential Marine Data**:
    - Wind speed, direction, gusts (knots)
    - Wave height, direction, period (meters/seconds)
    - Sea state description (Calm/Smooth/Slight/Moderate/Rough/etc.)
    - Visibility (kilometers)
    - Precipitation (mm/hr)
    - Barometric pressure (hPa)
    - Temperature & humidity
    - Weather alerts (High Wind, High Seas, Heavy Precipitation)
  - **Auto-Logging to Boatlog** (every 30 minutes)
  - Split-screen layout: Radar (2/3) + Conditions Panel (1/3)
  - See: `/home/boatiq/Helm-OS/doc/WEATHER_2026-02-13.md`

- **Marine Vision System** (PLANNED - 2026-02-14)
  - IP67 camera integration (Reolink RLC-810A)
  - Two operating modes: Fish Capture + Forward Watch
  - **Fish Capture Mode**:
    - Person + fish detection (YOLOv8)
    - Auto-capture photo when holding fish
    - Species identification (pretrained + fine-tuned model)
    - Fishing regulations check (size/bag limits by location/date)
    - Notification to phone (Telegram/Signal/email)
    - Event logging with timestamp, species, GPS location
  - **Forward Watch Mode**:
    - Marine object detection (boats, kayaks, buoys, logs, debris)
    - Distance estimation (monocular depth - MiDaS/ZoeDepth)
    - Real-time alerts (visual + audible)
    - Detection logging
  - **Camera**:
    - Model: Reolink RLC-810A (IP67, night vision)
    - Stream: RTSP (rtsp://d3kos:d3kos2026@CAMERA_IP:554/h264Preview_01_main)
    - Recording: VLC integration, stored on 128GB USB drive
    - Mounted on 360° motorized searchlight
  - **Orientation Detection**: Camera angle determines mode (Fish: 135-225°, Forward: 315-45°)
  - **APIs**: FishBase, GBIF, iNaturalist, Ontario MNR regulations
  - **Models**: YOLOv8 (detection), ResNet50 (species ID), MiDaS (depth)
  - **Services**: camera-stream, vision-core, fish-detector, forward-watch, marine-vision-api
  - **Storage**: ~250MB models, ~1GB/hour video recordings
  - **Performance**: 10+ FPS detection, 5+ FPS depth estimation
  - See: `/home/boatiq/Helm-OS/doc/MARINE_VISION.md`

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
| 2.3 | 2026-02-11 | Added Step 4 (Chartplotter Detection) to Initial Setup wizard, clarified that CX5106 uses standard PGNs (no vendor-specific translation needed), documented chartplotter compatibility |
| 2.4 | 2026-02-11 | Added implementation details for Step 4: nginx proxy configuration for WebSocket, JavaScript detection code, fullscreen toggle on wizard completion |
| **3.3** | **2026-02-16** | **Added comprehensive Stripe Billing implementation documentation (40-60 hour development guide with production-ready code examples). See /doc/STRIPE_BILLING_IMPLEMENTATION_GUIDE.md for complete backend API, iOS StoreKit 2, and Android Billing Library integration. MASTER_SYSTEM_SPEC.md v3.2 Section 6.3.4 expanded with database schema (3 tables), 8 API endpoints, and cost breakdown. Confirmed traditional e-commerce platforms (OpenCart, PrestaShop, etc.) are NOT suitable for mobile app subscriptions due to Apple/Google IAP requirements.** |
| **3.8** | **2026-02-22** | **CRITICAL UPDATE: Phi-2 LLM REMOVED (Feb 16, 2026).** Reason: 60-180s response unusable on boat helm. Freed 1.7GB storage + 3GB RAM. **Replaced with OpenRouter (gpt-3.5-turbo, 6-8s) + Rule-based system (13 patterns, 0.17s).** Updated all Perplexity→OpenRouter references. Updated software versions: Node.js v18→v20.20.0, Node-RED 3.x→v4.1.4. Confirmed Trixie (Debian 13) as current OS. Added Signal K caching (3s TTL, 100× speedup). Documented actual system: d3kOS v0.9.1.2, Tier 3, 22+ services. |

---

## Anomalies Detected & Resolved

### Anomaly 1: RAM Requirement
- **Previous**: 4GB or 8GB RAM
- **Updated**: **8GB RAM recommended** (for Marine Vision + all services)
- **Reason**: YOLOv8n ONNX + Camera + Voice + Services = ~1.6GB, 8GB provides headroom. **NOTE**: Phi-2 removed Feb 16, 2026 (freed 1.7GB storage + 3GB RAM)

### Anomaly 2: OS Version
- **Previous**: Bookworm or Trixie
- **Updated**: **Trixie (Debian 13) only**
- **Reason**: Piper and PocketSphinx packages available in Trixie repos

### Anomaly 3: Licensing Tiers
- **Previous**: Vague Tier 1-4
- **Updated**: **Clear Tier 0-3 with specific features**
- **Tier 1 changed**: Now includes mobile app (was separate)

### Anomaly 4: AI Backend System
- **Previous**: Phi-2 LLM via llama.cpp (60-180s response)
- **Updated (Feb 16, 2026)**: **OpenRouter (gpt-3.5-turbo) + Rule-based patterns**
- **Reason**: Phi-2 unusable on boat helm (too slow). OpenRouter: 6-8s complex queries. Rule-based: 0.17s simple queries. Freed 1.7GB storage.

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
