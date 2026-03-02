# Skipperdon Environment - Complete System Context
**Created:** 2026-03-02
**Purpose:** Central reference for all AI assistants working on projects

---

## 🎯 Primary Directive

**I am the Orchestrator & Planner** - coordinating between Skipper Don and local AI assistants.

**Hierarchy:**
```
Skipper Don (Founder/Designer)
    ↓
Claude Code (Orchestrator - me)
    ↓
Local Ollama RAG (Implementation)
```

**Cost Optimization:** Reduce from $800/month to <$50/month by using local Ollama

**Autonomy Level:**
- ✅ Execute immediately: Code generation, documentation, planning, testing
- ⚠️ Ask first: System changes, deployments, network configuration
- 🛑 Never do: Delete files on laptop/workstation, change structure on those systems

---

## 🏗️ Engineering Standards (MANDATORY FOR ALL TASKS)

**Apply automatically to every task:**
1. Master AI Engineering, Coding, and Testing Standard
2. AI Engineering Specification & Solution Design Template
3. AI Engineering & Automated Testing Specification Template
4. Standard Test Case Creation Template

**Every deliverable must include:**
1. Problem definition
2. System architecture
3. Technology stack recommendation
4. Data model and schema
5. API or module design
6. Core logic with example code
7. Playwright automated tests (when applicable)
8. Windows execution instructions
9. Testing strategy
10. Documentation package

---

## 💻 Network Infrastructure

### Systems

| System | IP | User | Password | Role | OS |
|--------|-------|------|----------|------|-----|
| **TrueNAS** | 192.168.1.102 | root | damcor53$ | Storage, Ollama host | FreeBSD |
| **TrueNAS VM** | 192.168.1.103 | ollama | d3kos2026 | Ollama AI Server | Ubuntu 22.04 LTS |
| **Workstation** | 192.168.1.39 | admin | A#JFOPZD6& | GPU compute, Blue Iris | Windows 11 Pro |
| **Laptop** | Dynamic (WSL) | boatiq | N/A | Development | Windows 11 Home + WSL Ubuntu |
| **d3kOS Pi** | 192.168.1.237 | d3kos | d3kos2026 | Testing, prototype | Debian Trixie |
| **QNAP NAS** | 192.168.1.49<br>192.168.1.50 | admin | Donald 61# | Backup storage | QNAP OS |

### Network Topology
- **Laptop:** WiFi to router
- **TrueNAS + Workstation:** 10 Gig Ethernet via QNAP switch
- **QNAP:** Dual 2.5 Gig Ethernet
- **d3kOS Pi:** 1 Gig Ethernet

---

## 💾 Storage Architecture

### TrueNAS Pools

| Pool | Type | Purpose | Backup |
|------|------|---------|--------|
| **Cheeta** | Fast SSD | Primary project storage | → Beaver (noon/midnight) |
| **Beaver** | RAID | Long-term backup storage | Primary backup destination |
| **Mice** | Small | Utility work | → Beaver |
| **Windowshare** | Share | Windows file sharing | N/A |

### Project Organization on Cheeta

```
/mnt/Cheeta/
├── d3kOS/
│   ├── src/
│   ├── doc/
│   ├── tests/
│   └── deployments/
├── AAO-Methodology/
│   ├── specifications/
│   ├── templates/
│   └── examples/
├── Video-Marketing/
│   ├── scripts/
│   ├── assets/
│   └── rendered/
├── AtMyBoat/
│   ├── blog-posts/
│   ├── linkedin/
│   ├── forum-content/
│   └── marketing/
├── ollama-docs/
│   └── (deployment documentation)
└── backups/
    ├── TrueNAS/
    │   ├── configurations/
    │   └── credentials/
    ├── Laptop/
    │   └── (full system backups)
    └── Workstation/
        └── (full system backups)
```

### Backup Schedule
- **Frequency:** Noon (12:00 PM) and Midnight (12:00 AM) daily
- **Retention:** 30 days of recovery points
- **Source:** Cheeta, Mice → Beaver
- **Method:** ZFS snapshots + replication

---

## 🤖 AI Infrastructure

### Claude Code (This System)
- **Purpose:** Orchestrator, planner, architect
- **Cost:** $20-50/month (Anthropic API for critical tasks only)
- **Access:** Via laptop WSL Ubuntu

### Ollama (TrueNAS VM)
- **Purpose:** FREE local AI for code generation, RAG, testing
- **Location:** 192.168.1.103:11434
- **Model:** qwen2.5-coder:14b (CPU-optimized)
- **API:** http://192.168.1.103:11434/v1 (Anthropic-compatible)
- **Cost:** $0/month

### Routing Strategy
```bash
# Default: Use FREE TrueNAS Ollama
claude (alias)

# Premium: Use Anthropic API (costs money)
claude-premium

# Explicit: Use TrueNAS
claude-truenas
```

---

## 📦 Active Projects

### 1. d3kOS (Marine Helm Operating System)
**Status:** v0.9.1.2 → v1.0.0 (122 weeks roadmap)
**Platform:** Raspberry Pi 4B (8GB RAM)
**Purpose:** Smart marine monitoring for modern boaters
**Key Features:**
- Engine dashboard, boatlog, navigation, voice assistant
- Marine vision (fish detection, forward watch)
- Multi-camera system (4 cameras planned)
- Metric/Imperial conversion (v0.9.2 next)

**Tech Stack:**
- Backend: Python, Node.js, Signal K, Ollama
- Frontend: HTML/CSS/JS (standalone, no frameworks)
- Database: SQLite, ChromaDB (RAG)
- Hardware: Raspberry Pi, CAN bus (NMEA2000), GPS, cameras

**Documentation:**
- Spec: `/home/boatiq/Helm-OS/MASTER_SYSTEM_SPEC.md`
- Guidelines: `/home/boatiq/Helm-OS/CLAUDE.md`
- Roadmap: `/home/boatiq/Helm-OS/doc/D3KOS_VERSION_ROADMAP_2026.md`

### 2. AAO Methodology
**Status:** In development
**Purpose:** AI-assisted orchestration methodology
**Deliverables:** Templates, specifications, standards

### 3. Video Marketing
**Status:** Planned
**Purpose:** Screen capture + AI script → professional marketing videos

### 4. AtMyBoat.com
**Status:** Live website
**Platform:** WordPress on HostPapa
**Credentials:** admin / A#JFOPZD6&
**Purpose:** Blog, product marketing, community

---

## 🚨 Critical Constraints

### Workstation (192.168.1.39)
- ⚠️ **NO FILE DELETION** - Contains confidential tax data
- ⚠️ **Blue Iris runs 24/7** - GPU always partially loaded
- ⚠️ **Must not interfere** with user's work at any time
- Only access when explicitly authorized

### Laptop
- ⚠️ **DO NOT delete files or change structure**
- Safe to create new files in /home/boatiq/Helm-OS/
- Git commits allowed, GitHub push only when requested

### TrueNAS
- ⚠️ **Don't impact NAS storage function** (primary purpose)
- VM resource usage must be reasonable
- Keep backups running smoothly

### d3kOS Pi (192.168.1.237)
- ✅ Full access for testing and development
- Safe to modify, test, deploy
- Used for promotion of d3kOS versions

---

## 🔧 Development Workflow

### For New Features:
1. **Problem Definition** (AI Engineering Spec Template)
2. **System Architecture** (diagrams, component design)
3. **Technology Stack** (modern, maintainable)
4. **Data Model** (schema, relationships)
5. **API Design** (endpoints, contracts)
6. **Core Logic** (algorithms, example code)
7. **Automated Tests** (Playwright when applicable)
8. **Documentation** (overview, setup, usage, troubleshooting)
9. **Deployment Plan** (step-by-step execution)
10. **Testing Strategy** (validation criteria)

### For Bug Fixes:
1. **Root Cause Analysis**
2. **Fix Implementation** (with tests)
3. **Regression Testing**
4. **Documentation Update**

### For Documentation:
1. **Overview** (what it does)
2. **Architecture** (how it works)
3. **Setup** (how to install)
4. **Usage** (how to use)
5. **Troubleshooting** (common issues)
6. **Glossary** (technical terms)

---

## 🎯 Current Priorities (March 2026)

1. ✅ **Ollama Deployment** - TrueNAS VM deployed, cost reduction achieved
2. 🔄 **Project Organization** - Migrate files to Cheeta, setup backups
3. ⏳ **Unattended Operation** - Reduce approval friction, coordinate AI assistants
4. ⏳ **d3kOS v0.9.2** - Metric/Imperial conversion (3 weeks)
5. ⏳ **d3kOS v0.9.3** - 4-camera system (8-9 weeks)

---

## 📝 Invocation Prompts (Auto-Apply)

### For Engineering Tasks:
> Use the Master AI Engineering, Coding, and Testing Standard to produce a complete, modern, high-performance, well-documented solution. Follow all engineering, testing, language-specific, and Playwright standards. Ask for missing information if anything is unclear.

### For Solution Design:
> Use the AI Engineering Specification Template to produce a complete, modern, high-performance, well-documented solution. Follow all quality standards, constraints, and deliverables. Ask clarifying questions if any requirement is ambiguous.

### For Testing:
> Use the AI Engineering & Automated Testing Specification Template to produce a complete, modern, high-performance, well-documented solution. Include automated browser testing using Playwright/Selenium. Ask clarifying questions if any requirement is ambiguous.

---

## 🔐 Security Notes

- All credentials documented here
- This file should be backed up to Cheeta
- Never commit to public GitHub
- Store encrypted copy on Beaver

---

**Last Updated:** 2026-03-02
**Maintained By:** Claude Code (Orchestrator)
**For:** Skipper Don (Founder, d3kOS)
