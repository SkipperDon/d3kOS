# Implementation Questionnaire & Plan
**Date:** 2026-03-02
**Goal:** Deploy Claude Code + Ollama on 3 systems with smart routing

---

## 📋 System Information (To Be Filled)

### Question 1: Workstation Details
**Status:** ✅ ANSWERED

**Question:**
- What is your workstation's IP address?
- What is the workstation's hostname?
- What operating system? (Windows 10/11?)
- Is the workstation powered on right now?
- Can I SSH/remote into it, or do you need to work on it directly?

**Answer:**
```
IP Address: 192.168.1.39
Hostname: DAM8940DELL
OS: Windows 11 Pro
GPU: NVIDIA RTX 3060 Ti
RAM: 32 GB
Currently powered on: Yes
Currently in use: YES - CRITICAL - DO NOT INTERRUPT
Remote access available: Yes (when user finishes)
Remote method: mstsc (Remote Desktop Protocol)
```

**⚠️ IMPORTANT NOTE:**
- Workstation is currently being used by another person
- **CRITICAL: Do not interrupt their work**
- Can access via Remote Desktop (mstsc) AFTER user is finished
- Will deploy to TrueNAS first, workstation later

---

### Question 2: Workstation Current Use
**Status:** ✅ ANSWERED

**Question:**
- What is the workstation primarily used for?
- What tasks typically use the GPU? (video editing, 3D rendering, gaming, etc.)
- How often is the GPU heavily used? (hours per day)
- Is there a pattern? (e.g., mornings free, afternoons busy)

**Answer:**
```
Primary uses:
1. Income tax preparation (CRITICAL: confidential data)
2. Video surveillance (Blue Iris - 24/7)
3. Internet browsing
4. Machine learning
5. Soon: AI assistant for income tax knowledge (voice AI + RAG)
6. Future: Video editing AI (screen capture + script → marketing videos)
7. General office work

GPU-intensive tasks:
- Blue Iris: 24/7 (ALWAYS running)
- Machine learning: Heavy when active

GPU usage: CONTINUOUSLY (Blue Iris runs 24/7)

Usage pattern:
- Mornings: Active
- Evenings: Active
- Weekends: Will be active soon
- Overall: Random throughout day
```

**🚨 CRITICAL CONSTRAINTS:**
1. ⚠️ **NO FILES TO BE DELETED** - Contains confidential tax information
2. ⚠️ **Blue Iris runs 24/7** - GPU always partially loaded
3. ⚠️ **Must not interfere with user's work** at any time

**📋 FUTURE PROJECTS IDENTIFIED:**
1. Income tax AI assistant (voice AI + RAG for tax knowledge)
2. Video editing AI (screen capture + script → professional marketing videos)

**💡 DEPLOYMENT STRATEGY ADJUSTMENT:**
- **TrueNAS will be PRIMARY** Ollama instance (not workstation)
- **Workstation Ollama will be OPTIONAL/LOW PRIORITY** (GPU already heavily used)
- Smart router will **strongly prefer TrueNAS** to avoid interfering with Blue Iris
- Workstation Ollama: Only if GPU usage drops AND user not working

---

### Question 3: TrueNAS Access
**Status:** ✅ ANSWERED

**Question:**
- Can you access TrueNAS web UI right now? (http://192.168.1.102)
- Do you have the root password? (you mentioned damcor53$)
- Is there already a VM on TrueNAS or do we need to create one?
- How much storage can we use for the VM? (you mentioned 100 GB earlier)

**Answer:**
```
TrueNAS web UI accessible: YES - Logged in right now
Root password confirmed: YES - damcor53$
Existing VM: NO - Need to create new VM
Existing plugins: NO - Clean system
VM specs: Not yet set up - can allocate as needed
Priority: NAS storage function (don't overload)
Current utilization: Low - "easy life up to now"
Can be utilized: YES - Available for our purposes
```

**✅ GOOD NEWS:**
- TrueNAS accessible right now
- Clean slate - no existing VMs or plugins
- System underutilized - can add Ollama workload
- User logged in and ready

**📋 VM ALLOCATION PLAN:**
- RAM: 24 GB (enough for Ollama models)
- vCPUs: 8 cores (good CPU performance)
- Storage: 100 GB (30 GB for models + 70 GB for OS/cache)
- Network: Bridged to 192.168.1.x network
- IP: 192.168.1.103 (static)

**⚠️ CONSTRAINT:**
- Must not impact NAS storage function (primary purpose)
- Keep VM resource usage reasonable

---

### Question 4: Laptop/Current System
**Status:** ✅ ANSWERED

**Question:**
- What OS is your laptop? (Windows/Linux/WSL?)
- Is Claude Code already installed on laptop?
- Do you have an active Anthropic API subscription?
- What's your API key? (I'll need this for the router script)

**Answer:**
```
Laptop: HP Envy
Laptop OS: Windows 11 Home
Claude Code environment: WSL Ubuntu (Windows Subsystem for Linux)
Claude Code installed: YES
Anthropic API: Pay-as-you-go (on-demand, NO monthly subscription)
API key: REDACTED_ANTHROPIC_API_KEY
Location: /home/boatiq/.claude.json (line 115)
Account: networkdon89@gmail.com (Skipper Don)
```

**🔍 API KEY LOCATION:**
Need to locate API key - checking common locations:
1. `~/.claude/config.json` (WSL Ubuntu)
2. `~/.config/claude-code/config.json` (WSL Ubuntu)
3. Environment variable `ANTHROPIC_API_KEY`
4. `~/.bashrc` or `~/.zshrc`

**💡 GOOD NEWS:**
- Pay-as-you-go (not subscription) = Only pay for what you use
- Deploying Ollama will dramatically reduce API usage
- Current $800/month will drop to near $0 with Ollama

---

### Question 5: Network Setup
**Status:** ✅ ANSWERED

**Question:**
- Are all systems (laptop, workstation, TrueNAS) on the same network?
- What's the network subnet? (e.g., 192.168.1.x)
- Any firewalls between systems?
- Can laptop ping workstation right now?

**Answer:**
```
Same network: YES
Subnet: 192.168.1.x
Laptop → Workstation ping: 6ms (EXCELLENT)
Laptop → TrueNAS ping: 88ms (⚠️ HIGH - PROBLEM!)
Firewalls: 2 (Bell router, Netgear router)
LAN blocking: None (should be open)
WiFi: Same IP group as wired
```

**Network Infrastructure:**
```
Internet → Bell Router (Fiber) → Netgear Router → LAN
                                                    ↓
                                    ┌───────────────┴───────────────┐
                                    ↓                               ↓
                            1 Gig Switch                   QNAP Switch
                                                      (2.5 Gig + 10 Gig ports)
                                                            ↓
                                                ┌───────────┴────────────┐
                                                ↓                        ↓
                                          Workstation              TrueNAS
                                         (10 Gig?)                (10 Gig?)
```

**🚨 CRITICAL ISSUE FOUND:**
- **88ms ping to TrueNAS is EXTREMELY high** for local network
- Should be <2ms on 10 Gig, <5ms on 1 Gig
- **This will severely impact Ollama performance!**
- Every API call = 88ms × 2 (request + response) = 176ms overhead
- Plus model inference time = SLOW responses

**🔍 INVESTIGATION NEEDED:**
1. Is TrueNAS connected to 10 Gig switch or 1 Gig switch?
2. Is workstation connected to 10 Gig switch?
3. Is laptop on WiFi or wired? (WiFi could explain high latency)
4. Is TrueNAS network cable good? (bad cable = high latency)
5. Is TrueNAS network configured correctly?

---

### Question 6: Timeline & Availability
**Status:** ✅ ANSWERED

**Question:**
- When do you want to start? (Now/Today/Tomorrow/This week?)
- How much time can you dedicate today? (1 hour/2 hours/4 hours/all day?)
- Is there a better time when workstation will be free?
- Should we start with TrueNAS only (since workstation busy)?

**Answer:**
```
Start time: NOW (after questions complete)
Timeline: Must be setup and working TODAY
Available time today: As much as needed to complete
Workstation status: NOW FREE (available for deployment)
```

**🚀 READY TO DEPLOY:**
- ✅ TrueNAS: Logged in and ready
- ✅ Workstation: Now free and available
- ✅ User: Ready and available
- ✅ Timeline: Complete deployment today
- ✅ All systems GO!

---

### Question 7: Desired Behavior
**Status:** ✅ ANSWERED - ALL QUESTIONS COMPLETE!

**Question:**
- Do you want automatic routing (smart router decides based on GPU usage)?
- Or manual selection (you choose which system to use)?
- Should workstation Ollama auto-start on boot, or manual start?
- Priority: Speed or Cost savings? (affects which models we install)

**Answer:**
```
Routing preference: Automatic (with manual override option)
Workstation Ollama auto-start: Yes (with option to shut down if needed)
Priority: Speed & Accuracy (monitor costs, adjust later)
```

**⚡ TIME-OF-USE ELECTRICITY PRICING:**
```
7am - 7pm:  HIGH cost   → Prefer TrueNAS CPU OR smaller models
7pm - 11pm: MED cost    → Balance between speed/cost
11pm - 7am: LOW cost    → Use workstation GPU, larger models (full speed)
```

**📋 IMPLEMENTATION STRATEGY:**
1. ✅ Deploy both TrueNAS (primary) + Workstation (secondary)
2. ✅ Automatic routing with manual override
3. ✅ Auto-start on both systems (with shutdown option)
4. ✅ Time-based optimization:
   - Peak hours: Efficient models (save electricity)
   - Off-peak hours: Fast models (maximum performance)
5. ✅ Monitor costs and adjust as needed

---

## 📝 Implementation Plan (To Be Created)

**Will be filled after answers above**

### Phase 1: [To be determined based on answers]
### Phase 2: [To be determined based on answers]
### Phase 3: [To be determined based on answers]

---

## ⏰ Estimated Timeline

**Will be calculated after answers**

---

## 💰 Expected Costs

**Will be calculated after answers**

---

**Status:** Waiting for Question 1 answer to proceed
