# CLAUDE.md - AI Assistant Guidelines for Helm-OS Development

## Purpose

This document provides guidelines for AI assistants (like Claude, ChatGPT, Copilot) working on the Helm-OS project. It ensures consistency, prevents circular development, and maintains alignment with the project's core specifications.

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

### What is Helm-OS?

Helm-OS is a **pre-built Raspberry Pi 4B marine intelligence platform** that provides:
- NMEA2000 integration via PiCAN-M HAT
- AI-assisted onboarding wizard
- CX5106 engine gateway configuration
- Real-time vessel monitoring
- Offline voice assistant
- OpenCPN navigation integration
- Engine health monitoring

### Hardware Stack (Fixed)
- **Raspberry Pi 4B** (4GB or 8GB RAM)
- **PiCAN-M HAT** with SMPS
- **CX5106 Engine Gateway**
- **10.1" Touchscreen** (1920x1200, 1000 nit)
- **USB GPS & AIS receivers**
- **Anker PowerConf S330** (mic + speaker)
- **IP67 Camera** (Reolink RLC-810A)

### Software Stack (Fixed Versions)

| Component | Version | Notes |
|-----------|---------|-------|
| Raspberry Pi OS | Trixie (Debian 13) | 64-bit |
| Node.js | v18 or v20 LTS | NOT v22 |
| Signal K Server | 2.x (latest) | Install via npm |
| Node-RED | 3.x | Install via npm |
| Node-RED Dashboard | 2.0.4-1 (v4.1.4) | Dashboard 2.0 (Vue-based) |
| OpenCPN | 5.8.x | Auto-installed if no chartplotter |
| Vosk | Latest | Speech-to-text (offline) |
| Piper | Latest | Text-to-speech (offline) |
| Phi-2 | 2.7B | Local LLM for AI reasoning |

**IMPORTANT**: Do NOT recommend Node.js v22, Dashboard 1.0 (Angular), or different versions without explicit justification.

---

## Design Philosophy

### 1. Pre-Built Image Approach
- System is distributed as a **flashable SD card image**
- Users flash, boot, and run onboarding wizard
- NO curl installer scripts
- NO manual package installation by users

### 2. Offline-First
- Complete functionality without internet
- All AI processing local (Phi-2 LLM)
- Voice processing local (Vosk + Piper)
- Updates via new image downloads only

### 3. Never Get Stuck
- Onboarding wizard ALWAYS completes
- AI fills missing information intelligently
- Safe defaults for all configurations
- User can override AI decisions

### 4. AODA Compliance
- All UI must meet AODA/WCAG 2.1 AA standards
- High contrast (black background, white/green text)
- Large touch targets (minimum 44x44px)
- Keyboard navigable
- Screen reader compatible
- Focus indicators visible

### 5. Marine Environment Optimization
- Readable in bright sunlight (1000 nit screen)
- Large fonts (22px minimum)
- Touch-friendly buttons
- Glove-operable interface
- Power-loss resistant (all data in JSON)

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

### Color Scheme
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

## Development Rules

### DO's

✅ **Read MASTER_SYSTEM_SPEC.md before starting**
✅ **Use exact version numbers specified**
✅ **Test on Raspberry Pi 4B hardware**
✅ **Follow existing directory structure**
✅ **Use JSON for all configuration (no databases)**
✅ **Include verification steps after every installation command**
✅ **Write idempotent scripts (can run multiple times safely)**
✅ **Include error handling in all scripts**
✅ **Document all assumptions**
✅ **Cross-reference related documents**

### DON'Ts

❌ **Never contradict MASTER_SYSTEM_SPEC.md**
❌ **Never recommend untested software versions**
❌ **Never assume internet connectivity**
❌ **Never write code without reading existing codebase first**
❌ **Never create duplicate documentation**
❌ **Never mix conversational AI responses with technical docs**
❌ **Never expose real credentials in documentation**
❌ **Never use vague language ("should work", "might need")**
❌ **Never skip verification steps**
❌ **Never assume user knowledge**

---

## CX5106 Configuration

### Critical Information

The CX5106 engine gateway is a **core component** of Helm-OS. AI assistants working on CX5106-related features MUST:

1. **Read**: `CX5106_CONFIGURATION_GUIDE.md` and `CX5106_USER_MANUAL.md`
2. **Understand**: DIP switch logic (8 switches control instance, RPM source, cylinders, stroke, gear ratio)
3. **Reference**: The 13-question engine wizard that determines DIP settings
4. **Remember**: Non-standard gear ratios (like 1.5:1 Bravo II) require correction factors

### Onboarding Wizard Integration

The wizard asks **13 engine-specific questions**:
1. Engine manufacturer
2. Engine model
3. Engine year
4. Number of cylinders
5. Engine displacement
6. Compression ratio
7. Stroke length
8. Induction type
9. Rated horsepower
10. Idle RPM
11. WOT RPM range
12. Max coolant temperature
13. Min safe oil pressure

These determine:
- CX5106 DIP switch positions
- Expected PGN set
- Alarm thresholds
- Performance baselines
- Anomaly detection parameters

---

## Voice Assistant ("Helm")

### Architecture
- **Wake Word**: "Helm" (using PocketSphinx)
- **STT**: Vosk (offline)
- **TTS**: Piper (offline)
- **LLM**: Phi-2 (2.7B parameters, offline)
- **End Command**: "Helm end" (stops listening)

### Voice Commands (Examples)
```
"Helm, what's the engine status?"
"Helm, any anomalies?"
"Helm, open OpenCPN"
"Helm, start benchmarking"
"Helm, record boat log"
"Helm, post to boat log"
```

### Design Constraints
- Must work **completely offline**
- Response time < 2 seconds
- No cloud API calls
- All processing on Pi 4B

---

## Licensing System

### Tier Structure

| Tier | Description | Features | Cost |
|------|-------------|----------|------|
| **Tier 0** | Base opensource | All core features, limited to 10 onboarding resets | Free |
| **Tier 1** | Mobile App | Future | centralize backend data and reporting |
| **Tier 2** | App integration | Additional apps installed | TBD |
| **Tier 3** | Premium subscription | Unlimited resets, cloud sync | Paid |
| **Tier 4** | Enterprise | Fleet management | Paid |

### Onboarding Reset Limit
- **Tier 0**: Maximum 10 onboarding resets
- After 10 resets: User must download new image
- **Reason**: Prevents single license from being used on multiple boats
- Counter stored in: `state/onboarding-reset-count.json`

---

## File Structure & Conventions

### Directory Layout
```
/opt/helm-os/
├── services/
│   ├── onboarding/          # Onboarding wizard backend
│   ├── .node-red/           # Node-RED flows
│   ├── signalk/             # Signal K configuration
│   └── opencpn/             # OpenCPN integration
├── config/                  # Persistent user configuration
│   ├── operator.json
│   ├── boat-identity.json
│   ├── boat-active.json
│   └── boats/               # Multi-boat support
├── state/                   # Runtime state
│   ├── onboarding.json
│   ├── baseline.json
│   └── health-status.json
├── system/                  # Systemd services
│   ├── helm-onboarding.service
│   ├── helm-health.service
│   └── helm-benchmark.service
└── scripts/                 # Installation scripts
```

### Configuration Files

All configuration MUST be:
- **Format**: JSON (not YAML, XML, or TOML)
- **Location**: `/opt/helm-os/config/` or `/opt/helm-os/state/`
- **Atomic writes**: Write to temp file, then rename
- **Power-loss safe**: No partial writes
- **Human-readable**: Properly indented

---

## API Endpoints

### Onboarding Service (Port 8080)

```
GET  /onboarding/status
POST /onboarding/operator-alias
POST /onboarding/boat
POST /onboarding/engine
POST /onboarding/chartplotter
POST /onboarding/install-opencpn
POST /onboarding/pgn-detection
POST /onboarding/dip-switch
POST /onboarding/finalize
POST /onboarding/reset
```

### Health Monitoring

```
GET  /health/summary
GET  /health/anomalies
POST /health/baseline
```

### Benchmarking

```
POST /benchmark/start
POST /benchmark/stop
GET  /benchmark/status
GET  /benchmark/report
POST /benchmark/accept
```

---

## Testing Requirements

### Before Submitting Code

✅ Tested on actual Raspberry Pi 4B
✅ Tested with PiCAN-M HAT connected
✅ Verified CAN0 interface works
✅ Checked with 10.1" touchscreen at 1920x1200
✅ Tested with on-screen keyboard visible
✅ Verified AODA compliance
✅ Power-cycled to test persistence
✅ Checked error handling
✅ Verified documentation is updated

---

## Common Pitfalls to Avoid

### 1. Version Confusion
**Problem**: Recommending Node-RED Dashboard 1.0 (Angular) instead of 2.0 (Vue)
**Solution**: Always specify "Dashboard 2.0.4-1" or "Dashboard 2.0 (Vue-based)"

### 2. Network Assumptions
**Problem**: Assuming internet connectivity for package installs
**Solution**: Pre-built image includes everything; no runtime installs

### 3. Circular Development
**Problem**: AI generating code that contradicts earlier code
**Solution**: Read existing codebase FIRST, then generate new code

### 4. Incomplete Error Handling
**Problem**: Scripts that fail silently
**Solution**: Every script must include error checking and rollback

### 5. Credential Exposure
**Problem**: Real passwords in documentation
**Solution**: Always use placeholders like `<YOUR_PASSWORD>`

### 6. Inconsistent Terminology
**Problem**: "NMEA2000" vs "NMEA 2000" vs "N2K"
**Solution**: Use "NMEA2000" (one word, no spaces)

---

## When You Don't Know

If you're unsure about any aspect:

1. **Check MASTER_SYSTEM_SPEC.md**
2. **Check existing documentation** in `docs/`
3. **Check related `.md` files**
4. **Ask for clarification** (don't guess)
5. **Document your assumptions** if you must proceed

**NEVER**:
- Make up version numbers
- Assume compatibility
- Guess at configurations
- Skip verification steps

---

## Documentation Standards

### Markdown Style
- Use ATX-style headers (`#`, `##`, `###`)
- Code blocks with language specified: ` ```bash `
- Tables for structured data
- ASCII diagrams for flows
- Consistent terminology throughout

### Code Examples
- Must be **copy-paste ready**
- Include expected output
- Show verification steps
- Include error handling

### Verification Steps
Every installation command MUST include:
```markdown
**Verification:**
```bash
# Command to verify
<expected output>
```
```

---

## Pre-Built Image Creation

### Build Process
1. Start with clean Raspberry Pi OS Trixie
2. Install all software components
3. Configure all services
4. Test thoroughly
5. Create image with `dd`
6. Compress with `gzip`
7. Generate checksums (SHA256)
8. Upload to GitHub releases

### Image Naming
```
helm-os-v<version>-pi4b-<date>.img.gz

Example: helm-os-v0.1.0-pi4b-20260204.img.gz
```

### Included in Image
- Raspberry Pi OS Trixie (64-bit)
- Node.js v20 LTS
- Signal K Server 2.x
- Node-RED 3.x + Dashboard 2.0
- All Python dependencies
- All system services configured
- CAN0 interface pre-configured
- Vosk models downloaded
- Piper voices downloaded
- Phi-2 model downloaded

### NOT Included (User Configures)
- Operator name
- Boat details
- Engine configuration
- CX5106 DIP switch settings
- Network passwords
- GPS/AIS device paths

---

## Troubleshooting Guidelines for AI

### When Code Doesn't Work

1. **Check versions** - Are you using the specified versions?
2. **Check prerequisites** - Did earlier steps complete?
3. **Check logs** - What do systemd logs show?
4. **Check paths** - Are files in expected locations?
5. **Check permissions** - Does `pi` user have access?

### When Documentation Conflicts

1. **MASTER_SYSTEM_SPEC.md wins** - Always
2. **Newer docs override older** - Check dates
3. **Ask for clarification** - Don't assume

### When Generating New Features

1. **Read related docs FIRST**
2. **Check if feature already exists**
3. **Verify compatibility**
4. **Test on hardware**
5. **Update all related docs**

---

## Success Criteria

Code/documentation is ready when:

✅ Aligns with MASTER_SYSTEM_SPEC.md
✅ Uses correct software versions
✅ Includes verification steps
✅ Includes error handling
✅ Tested on Raspberry Pi 4B
✅ AODA compliant (if UI)
✅ Documentation updated
✅ No contradictions with existing code
✅ No assumptions about internet
✅ Power-loss safe

---

## Contact & Escalation

If you encounter:
- Contradictions in specifications
- Unclear requirements
- Missing information
- Technical limitations

**DO**: Document the issue and ask for clarification
**DON'T**: Make assumptions and proceed

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-04 | Initial CLAUDE.md creation |

---

## Final Reminder

**This is not a suggestion document - it is a REQUIREMENT document.**

All AI assistants working on Helm-OS MUST follow these guidelines. Deviations must be explicitly justified and documented.

When in doubt: **Read MASTER_SYSTEM_SPEC.md again.**
