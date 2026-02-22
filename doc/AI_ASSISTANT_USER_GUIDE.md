# d3kOS AI Assistant - User Guide

**Version:** 2.0
**Last Updated:** February 16, 2026
**System:** d3kOS Marine Helm Control System

---

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Using the AI Assistant](#using-the-ai-assistant)
4. [Voice Commands](#voice-commands)
5. [Understanding AI Modes](#understanding-ai-modes)
6. [Quick Reference](#quick-reference)
7. [Tips & Best Practices](#tips--best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Overview

### What is the AI Assistant?

The d3kOS AI Assistant is your intelligent marine copilot that helps you:
- **Monitor boat systems** - Ask about engine RPM, oil pressure, fuel levels, battery status
- **Get instant answers** - Simple queries answered in under 1 second
- **Navigate safely** - Check GPS position, speed, heading
- **Learn about your boat** - Access manuals, technical specs, regulations
- **Operate hands-free** - Use voice commands while at the helm

### Two Ways to Interact

**1. Text Interface** (Touchscreen)
- Open AI Assistant from main menu
- Type questions using on-screen keyboard
- See chat history and responses
- Access: http://192.168.1.237/ai-assistant.html

**2. Voice Commands** (Hands-Free)
- Say wake word: "Helm", "Advisor", or "Counsel"
- Ask your question (3 seconds to speak)
- Hear spoken response through boat speakers
- Perfect for operating boat in rough conditions

---

## Getting Started

### Opening the AI Assistant

#### From Main Menu (Touchscreen):
1. Tap **Main Menu** button (top-left on any page)
2. Tap **AI Assistant** button (robot icon)
3. Chat interface opens - ready to use

#### Using Voice (Hands-Free):
- Voice assistant must be enabled (check dashboard)
- Simply say a wake word to activate
- No button pressing required

### First-Time Setup

**No setup required!** The AI Assistant is:
- ✅ Pre-configured with your boat data
- ✅ Connected to all sensors (NMEA2000)
- ✅ Ready to answer questions immediately
- ✅ Works offline for simple queries

---

## Using the AI Assistant

### Text Interface

#### Asking Questions

1. **Tap the text box** at bottom of screen
   - On-screen keyboard appears automatically

2. **Type your question**
   - Examples: "What's the RPM?", "Show fuel level", "Where am I?"

3. **Send your message**
   - Tap **Send** button (green arrow)
   - OR press **Enter** key

4. **Wait for response**
   - "Thinking..." indicator appears
   - Response appears in 0.2-18 seconds (depending on query type)

#### Example Conversation

```
You: What's the engine RPM?
AI: Engine RPM is 1,850. (0.18s | rules)

You: What's the oil pressure?
AI: Oil pressure is 45 PSI. (0.17s | rules)

You: What time is it?
AI: Current time is 2:45 PM on Saturday, February 16, 2026. (0.22s | rules)

You: Where am I?
AI: Current position: 44.4167° N, 79.3333° W (Lake Simcoe, Ontario) (0.19s | rules)
```

### Choosing AI Mode

The AI Assistant has three modes:

#### 🔄 Auto (Default - Recommended)
- **What it does:** Automatically picks fastest available AI
- **When to use:** All the time (let the system decide)
- **Response time:** 0.2-8 seconds depending on query

#### 🌐 Online
- **What it does:** Uses cloud AI (OpenRouter GPT-3.5)
- **When to use:** Complex questions requiring internet knowledge
- **Response time:** 6-8 seconds
- **Requires:** Internet connection (cellular, Starlink, marina WiFi)

#### 💻 Onboard
- **What it does:** Uses local AI (rules-based, no internet needed)
- **When to use:** When offshore with no internet
- **Response time:** 0.2 seconds for simple queries
- **Limitation:** Only handles 13 simple query types (see Quick Reference)

**To change mode:** Tap the mode buttons at top of chat interface

---

## Voice Commands

### Wake Words

Say one of these words to activate voice assistant:

| Wake Word | Mode | Response | When to Use |
|-----------|------|----------|-------------|
| **"Helm"** | Auto | "Aye Aye Captain" | General use (recommended) |
| **"Advisor"** | Onboard | "Aye Aye Captain" | Force offline mode |
| **"Counsel"** | Online | "Aye Aye Captain" | Force online mode |

### How to Use Voice Commands

1. **Say wake word clearly**
   - Example: "Helm"

2. **Wait for acknowledgment**
   - You'll hear: "Aye Aye Captain"

3. **Ask your question (3 seconds)**
   - Example: "What's the engine RPM?"

4. **Listen to response**
   - Spoken answer through boat speakers
   - Example: "Engine RPM is 1,850"

### Voice Command Examples

**Engine Monitoring:**
```
You: "Helm, what's the RPM?"
AI: "Engine RPM is 1,850."

You: "Helm, check oil pressure"
AI: "Oil pressure is 45 PSI."

You: "Helm, how much fuel do I have?"
AI: "Fuel level is 75 percent, approximately 30 gallons remaining."
```

**Navigation:**
```
You: "Helm, where am I?"
AI: "Current position: 44.4167° N, 79.3333° W, Lake Simcoe, Ontario."

You: "Helm, what's my speed?"
AI: "Current speed is 15 knots."

You: "Helm, what's my heading?"
AI: "Current heading is 270 degrees, heading west."
```

**System Status:**
```
You: "Helm, give me status"
AI: "Engine running at 1,850 RPM. Oil pressure 45 PSI. Coolant temperature 185°F.
     Battery at 13.2 volts. All systems normal."
```

### Voice Tips

**✅ DO:**
- Speak clearly and at normal volume
- Wait for "Aye Aye Captain" before asking question
- Use simple, direct questions
- Say wake word each time (no continuous conversation)

**❌ DON'T:**
- Shout or whisper
- Ask multiple questions in one breath
- Expect conversation memory (each query is independent)
- Use voice in extremely loud environments (engine room)

---

## Understanding AI Modes

### What's the Difference?

| Feature | Auto Mode | Online Mode | Onboard Mode |
|---------|-----------|-------------|--------------|
| **Speed** | 0.2-8s | 6-8s | 0.2s |
| **Internet Required** | No (falls back) | Yes | No |
| **Query Types** | All | All | Simple only (13 types) |
| **Complex Questions** | ✅ Yes | ✅ Yes | ❌ No |
| **Privacy** | Hybrid | Cloud AI | 100% Local |
| **Recommended For** | Everyday use | Research questions | Offshore/no internet |

### Simple vs Complex Queries

**Simple Queries (Instant - Onboard):**
- Engine metrics: RPM, oil pressure, temperature, boost
- Tank levels: Fuel, water, battery voltage
- Navigation: Speed, heading, location
- System info: Time, date, help, status
- Engine hours

**Complex Queries (Require Online):**
- "Why is my engine overheating and what should I do?"
- "What are the fishing regulations for bass in Ontario?"
- "How do I troubleshoot a fuel pump issue?"
- "Calculate range to destination at current fuel consumption"

### When Internet is Available

**Auto Mode logic:**
1. Check if query is simple (13 patterns)
2. ✅ Simple → Use onboard (0.2s response)
3. ❌ Complex → Use online AI (6-8s response)

**Result:** You get fast answers for simple queries, smart answers for complex ones

### When Internet is NOT Available

**Auto Mode logic:**
1. Check if query is simple (13 patterns)
2. ✅ Simple → Use onboard (0.2s response)
3. ❌ Complex → Return helpful message:
   ```
   "I can answer simple questions offline: rpm, oil pressure, temperature,
   fuel, battery, speed, heading, boost, hours, location, time, help, status.
   For complex questions, please connect to internet."
   ```

---

## Quick Reference

### 13 Instant-Answer Query Types

| Category | Example Questions | Response Time |
|----------|-------------------|---------------|
| **RPM** | "What's the RPM?", "Engine speed?" | 0.18s |
| **Oil Pressure** | "Oil pressure?", "Check oil" | 0.17s |
| **Temperature** | "Coolant temp?", "Engine temperature?" | 0.18s |
| **Fuel** | "Fuel level?", "How much fuel?" | 0.18s |
| **Battery** | "Battery voltage?", "Check battery" | 0.19s |
| **Speed** | "How fast am I going?", "Speed?" | 0.18s |
| **Heading** | "What's my heading?", "Which direction?" | 0.18s |
| **Boost** | "Boost pressure?", "Turbo pressure?" | 0.18s |
| **Hours** | "Engine hours?", "Runtime?" | 0.19s |
| **Location** | "Where am I?", "GPS position?" | 0.19s |
| **Time** | "What time is it?", "Current time?" | 0.22s |
| **Help** | "What can you do?", "Help" | 0.19s |
| **Status** | "System status", "Check all systems" | 0.18s |

**All cached queries respond in under 0.3 seconds!**

### Common Voice Patterns

**Quick Status Checks:**
- "Helm, RPM" → "Engine RPM is 1,850"
- "Helm, oil" → "Oil pressure is 45 PSI"
- "Helm, fuel" → "Fuel level is 75 percent"
- "Helm, status" → [Full system status]

**Navigation Queries:**
- "Helm, location" → [GPS coordinates]
- "Helm, speed" → "Current speed is 15 knots"
- "Helm, heading" → "Heading 270 degrees, west"

**System Information:**
- "Helm, time" → "2:45 PM on Saturday, February 16, 2026"
- "Helm, help" → [List of available commands]
- "Helm, engine hours" → "Engine has 127.5 hours of runtime"

---

## Tips & Best Practices

### Getting Fastest Responses

**✅ Use simple, direct questions:**
- Good: "RPM?"
- Good: "What's the fuel level?"
- Slow: "Can you please tell me what the current engine RPM is at this moment?"

**✅ Use Auto mode (default):**
- Automatically picks fastest option
- No manual switching needed

**✅ Learn the 13 instant patterns:**
- See Quick Reference above
- These always respond in under 0.3 seconds

### When to Use Each Mode

**Use Auto (🔄):**
- 95% of the time
- Let the system optimize for you

**Use Online (🌐):**
- Researching fishing regulations
- Troubleshooting complex problems
- Planning routes with weather data
- Learning about marine systems

**Use Onboard (💻):**
- Testing system while offline
- Verifying sensor readings
- When privacy is critical
- When internet is slow/unreliable

### Voice Assistant Tips

**For best recognition:**
- Speak at normal conversation volume
- Face toward boat speakers/microphone
- Reduce background noise when possible
- Use wake word each time (no continuous chat)

**In noisy conditions:**
- Move to quieter area of boat
- Increase microphone sensitivity (Settings)
- Use text interface instead
- Close engine room door

### Battery Saving

Voice assistant uses minimal power, but for extended offline use:
- Disable voice assistant in Settings
- Use text interface only
- Voice can be re-enabled anytime from dashboard

---

## Emergency Voice Reboot

### When to Use

**Emergency reboot is for recovering from touchscreen failures** caused by voice service issues.

**Symptoms that require emergency reboot:**
- Touchscreen stopped responding to touch
- Cannot tap buttons on screen
- Onboard keyboard doesn't appear
- Voice service broke touch input (known issue)

**When NOT needed:**
- Normal system operations (use Settings → System → Reboot)
- Voice assistant not responding (check microphone, wait 8 seconds)
- Screen is black (power issue, not software)

### How to Perform Emergency Reboot

**Step-by-Step:**

1. **Say the wake word:** "HELM" (loud and clear)
2. **Listen for response:** "Aye Aye Captain" (~3 seconds)
3. **Wait 8 seconds** for listening mode to fully activate
4. **Say one command:**
   - "reboot" (recommended - simple)
   - "restart"
   - "shutdown"
   - "reboot system"
   - "power cycle"
5. **Listen for confirmation:** "Rebooting system now. Please wait 60 seconds."
6. **System reboots immediately** (wait ~60 seconds for full restart)

### Example Session

```
You: "HELM"
Assistant: "Aye Aye Captain" ✓
[Wait 8 seconds - system is now listening]
You: "reboot"
Assistant: "Rebooting system now. Please wait 60 seconds." ✓
[System reboots immediately]
```

### Important Notes

**Timing is Critical:**
- Wait full 8 seconds after "Aye Aye Captain" before speaking
- If you speak too soon, command won't be heard
- If no response after 10 seconds, try again

**Voice Must Be Clear:**
- Speak at normal volume (not whisper, not shout)
- Say one word: "reboot" (simplest)
- Background noise can interfere - reduce if possible

**What Happens:**
- System saves all data automatically before reboot
- All services restart cleanly
- Touchscreen functionality restored after reboot
- No data loss or corruption

### If Emergency Reboot Doesn't Work

1. **Physical Power Cycle:**
   - Disconnect 12V power from NMEA2000 bus
   - Wait 10 seconds
   - Reconnect power
   - System will boot normally (~60 seconds)

2. **Check Voice Service:**
   - Use SSH from laptop: `ssh d3kos@192.168.1.237`
   - Check status: `systemctl status d3kos-voice.service`
   - If stopped: `sudo systemctl start d3kos-voice.service`

3. **Contact Support:**
   - Document issue (photos, description)
   - Email support@atmyboat.com
   - Include installation ID from Settings page

### Technical Details

**Implementation:** Industry-standard D-Bus + Polkit
- No password required for d3kos user
- Direct communication with systemd-logind
- Secure, auditable, reliable

**Voice Pipeline:**
```
Microphone → "HELM" → Vosk STT → Pattern Match → D-Bus → Systemd → Reboot
```

**Total Time:** ~12 seconds from wake word to reboot initiation

---

## Troubleshooting

### Text Interface Issues

**Problem: On-screen keyboard doesn't appear**
- **Solution:** Tap text input field directly
- **Fallback:** Use physical keyboard if available
- **Note:** Fullscreen mode automatically disables when entering AI Assistant page

**Problem: "Thinking..." indicator stays forever**
- **Solution:** Check internet connection (for online queries)
- **Check:** AI service status in Settings → System Services
- **Restart:** Refresh page (F5) or restart browser

**Problem: Responses are slow (>10 seconds)**
- **Cause:** First query after system start fetches live sensor data (18s)
- **Solution:** Subsequent queries use cache (0.2s responses)
- **Workaround:** Send "RPM?" query on startup to warm up cache

### Voice Assistant Issues

**Problem: Wake word not recognized**
- **Check:** Voice service enabled (Dashboard toggle)
- **Adjust:** Microphone sensitivity in Settings
- **Test:** Try in quieter environment
- **Alternative:** Use different wake word ("Helm" vs "Advisor")

**Problem: No spoken response**
- **Check:** Boat speakers connected and volume up
- **Check:** Audio output settings (Settings → Audio)
- **Test:** Play test sound from Settings page

**Problem: Wrong answers to questions**
- **Check:** Sensors connected (NMEA2000 bus active)
- **Verify:** Dashboard shows live data
- **Report:** Note exact question and answer for debugging

**Problem: Touchscreen becomes unresponsive while voice is speaking**
- **Behavior:** Touch input pauses during voice assistant audio playback
- **Duration:** 2-5 seconds (while TTS is speaking)
- **This is normal!** Audio subsystem temporarily locks input during playback
- **What happens:**
  - Touchscreen pauses when voice starts speaking
  - Resumes immediately after voice finishes
  - Visual display remains responsive
  - Touch input is queued (not lost)
- **Workaround:** Wait for voice response to finish before tapping screen
- **Note:** This prevents audio/input conflicts, not a bug

### Connection Issues

**Problem: "Internet connection required" for simple queries**
- **This shouldn't happen!** Simple queries work offline
- **Check:** AI mode set to "Onboard" or "Auto"
- **Restart:** d3kos-ai-api service

**Problem: "Service unavailable" error**
- **Check:** System Services status page
- **Restart:** AI Assistant service from Settings
- **Contact:** System administrator if persists

### Performance Issues

**Problem: Responses slower than expected**
- **Check:** Response time shown with each answer
- **Expected:** 0.2s for simple, 6-8s for complex (online)
- **Cache warming:** First query is slower (18s), then fast (0.2s)

**Problem: Text interface laggy or slow**
- **Check:** Browser cache (clear with Ctrl+Shift+R)
- **Check:** System load (Settings → System Status)
- **Restart:** Chromium browser (reboot system)

---

## Advanced Features

### Response Metadata

Every text response shows:
- **Response time** - How long it took (e.g., "0.18s")
- **Model used** - Which AI answered (e.g., "rules", "gpt-3.5-turbo")

**Example:**
```
AI: Engine RPM is 1,850.
⏱️ 0.18s | 🤖 rules
```

This helps you understand:
- **rules** = Instant onboard response (cached sensor data)
- **gpt-3.5-turbo** = Online AI response (internet used)
- **Response time** = System performance indicator

### Conversation History

**Web interface:**
- Chat history preserved while page is open
- Refreshing page clears history
- No persistent storage (for privacy)

**Voice interface:**
- Each query is independent
- No conversation memory
- Say wake word for each question

### Skills Knowledge Base

The AI has access to:
- Your boat specifications (from onboarding wizard)
- Engine technical data
- NMEA2000 sensor readings
- System configuration
- Web URLs for documentation
- Basic marine knowledge

**Location:** `/opt/d3kos/config/skills.md` (advanced users only)

---

## Privacy & Security

### Data Storage

**What's stored locally:**
- Conversation history database (on Pi SD card)
- Sensor data logs
- Skills knowledge base

**What's NOT stored:**
- Voice recordings (deleted after transcription)
- Personal information
- GPS tracks (unless you enable logging)

### Internet Usage

**Onboard mode:**
- ✅ 100% local processing
- ✅ No internet required
- ✅ Zero data sent to cloud

**Online mode:**
- ⚠️ Question sent to OpenRouter API (cloud)
- ⚠️ Sensor data may be included in context
- ⚠️ Requires internet connection
- ℹ️ Responses are NOT logged by OpenRouter

**Auto mode:**
- Simple queries: Local only (no internet)
- Complex queries: Sent to cloud (if internet available)

### Best Practices

**For maximum privacy:**
- Use Onboard mode exclusively
- Disable internet when not needed
- Review conversation history regularly
- Clear history from Settings

**For best functionality:**
- Use Auto mode (balances privacy and capability)
- Connect to internet for complex queries
- Trust that simple queries never leave the boat

---

## System Requirements

**Hardware:**
- ✅ Raspberry Pi 4B (8GB RAM) - Included in d3kOS
- ✅ 7" Touchscreen Display
- ✅ Anker S330 Speaker (for voice responses)
- ✅ USB Microphone (for voice commands)
- ✅ NMEA2000 Connection (for sensor data)

**Software:**
- ✅ d3kOS v2.0+
- ✅ AI API Service (d3kos-ai-api)
- ✅ Voice Assistant Service (d3kos-voice) - Optional
- ✅ Signal K Server (for sensor data)

**Network:**
- Touchscreen interface: No internet required
- Voice interface: No internet required for simple queries
- Online AI: Internet required (cellular, Starlink, marina WiFi)

---

## Getting Help

### Built-in Help

**Ask the AI:**
- "Helm, help" → List of capabilities
- "What can you do?" → Available query types
- "How do I use this?" → Basic instructions

### Documentation

**User Guides:**
- This document: `/home/boatiq/Helm-OS/doc/AI_ASSISTANT_USER_GUIDE.md`
- Master System Spec: `/home/boatiq/Helm-OS/doc/MASTER_SYSTEM_SPEC.md`
- Settings page: http://192.168.1.237/settings.html

### Support

**System Administrator:**
- Settings → System Services → View Logs
- Settings → About → System Information

**Community:**
- d3kOS GitHub: https://github.com/boatiq/Helm-OS
- AtMyBoat.com: https://atmyboat.com

---

## Appendix: Technical Details

### System Architecture

**Components:**
1. **AI API Server** (Port 8080)
   - HTTP REST API
   - Handles text queries from web interface
   - Routes to appropriate AI provider

2. **Query Handler** (Python Module)
   - Rule-based pattern matching
   - Signal K data fetching
   - Response caching (3-second TTL)
   - Provider selection logic

3. **Voice Assistant** (Optional Service)
   - Wake word detection (Vosk)
   - Speech-to-text (Vosk)
   - Text-to-speech (Piper)
   - Audio I/O management

4. **Signal K Client** (Data Source)
   - Fetches live sensor data
   - WebSocket or HTTP API
   - Cached responses (3s TTL)

### API Endpoints

**Web Access:**
- Chat Interface: `http://192.168.1.237/ai-assistant.html`
- API Endpoint: `POST http://192.168.1.237/ai/query`

**Request Format:**
```json
{
  "question": "What is the RPM?",
  "provider": "auto"  // or "onboard" or "openrouter"
}
```

**Response Format:**
```json
{
  "question": "What is the RPM?",
  "answer": "Engine RPM is 1,850.",
  "provider": "onboard",
  "model": "rules",
  "ai_used": "onboard",
  "response_time_ms": 180,
  "timestamp": "2026-02-16T14:45:00.123456"
}
```

### Service Management

**Start/Stop Services:**
```bash
# AI API Server
sudo systemctl start d3kos-ai-api
sudo systemctl stop d3kos-ai-api
sudo systemctl status d3kos-ai-api

# Voice Assistant (Optional)
sudo systemctl start d3kos-voice
sudo systemctl stop d3kos-voice
sudo systemctl status d3kos-voice
```

**View Logs:**
```bash
# AI API logs
sudo journalctl -u d3kos-ai-api -f

# Voice assistant logs
sudo journalctl -u d3kos-voice -f
```

### Configuration Files

**AI Configuration:**
- `/opt/d3kos/config/ai-config.json` - API keys, providers
- `/opt/d3kos/config/skills.md` - Knowledge base

**Voice Configuration:**
- `/opt/d3kos/config/sphinx/wake-words.kws` - Wake word list

**Service Files:**
- `/opt/d3kos/services/ai/ai_api.py` - Web API server
- `/opt/d3kos/services/ai/query_handler.py` - Query processing
- `/opt/d3kos/services/ai/signalk_client.py` - Sensor data
- `/opt/d3kos/services/voice/voice-assistant-hybrid.py` - Voice interface

---

**Document Version:** 1.0
**Created:** February 16, 2026
**For:** d3kOS Marine Helm Control System v2.0
**Author:** d3kOS Documentation Team
