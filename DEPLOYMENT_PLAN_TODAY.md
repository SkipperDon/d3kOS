# Custom Deployment Plan - Claude Code + Ollama
**Date:** 2026-03-02
**Timeline:** Deploy TODAY
**Systems:** TrueNAS (Primary) + Workstation (Secondary)

---

## 📋 Your Specific Configuration

Based on your answers:

**Systems:**
- **Laptop:** HP Envy, Windows 11 Home, WSL Ubuntu
- **Workstation:** DAM8940DELL, 192.168.1.39, Windows 11 Pro, RTX 3060 Ti, 32GB RAM
- **TrueNAS:** 192.168.1.102, Logged in NOW, Ready for VM

**Requirements:**
- ✅ Automatic routing (with manual override)
- ✅ Auto-start on boot (with shutdown option)
- ✅ Speed & accuracy priority
- ✅ Time-based cost optimization (peak 7am-7pm, off-peak 11pm-7am)
- ✅ Must complete TODAY

**Critical Constraints:**
- ⚠️ Workstation: NO file deletion (confidential tax data)
- ⚠️ Workstation: Blue Iris runs 24/7 (GPU partially loaded)
- ⚠️ TrueNAS: Don't impact NAS storage function
- ⚠️ Network: TrueNAS has 88ms latency (investigate)

---

## 🎯 Deployment Strategy

**Phase 1:** TrueNAS VM Setup (PRIMARY system)
- Create Ubuntu VM (24 GB RAM, 8 vCPUs, 100 GB storage)
- Install Ollama
- Deploy CPU-optimized models
- **Time:** 1.5 hours

**Phase 2:** Workstation Ollama Setup (SECONDARY system)
- Install Ollama on Windows
- Deploy GPU-accelerated models
- Configure auto-start
- **Time:** 45 minutes

**Phase 3:** Laptop Configuration
- Configure smart router with time-based optimization
- Create manual override commands
- Test all routing scenarios
- **Time:** 30 minutes

**Phase 4:** Testing & Verification
- Test automatic routing
- Test manual overrides
- Test time-based switching
- Verify Blue Iris not impacted
- **Time:** 30 minutes

**Total Time:** ~3.5 hours

---

## 📊 Model Selection Strategy

### TrueNAS Models (CPU - Always Available)

**Primary Model:**
- `qwen2.5-coder:14b` (14 GB) - Best CPU performance, good accuracy

**Backup Model:**
- `deepseek-coder:6.7b` (6.7 GB) - Faster when under load

**Use During:**
- Peak hours (7am-7pm) - Save electricity
- When workstation GPU busy with Blue Iris/ML
- 24/7 availability

---

### Workstation Models (GPU - Fast but Power-Hungry)

**Peak Hours (7am-7pm) - Efficient:**
- `qwen2.5-coder:14b` (14 GB) - Same as TrueNAS, can use CPU

**Off-Peak Hours (11pm-7am) - Maximum Performance:**
- `qwen2.5-coder:32b` (32 GB) - BEST accuracy, GPU-accelerated

**Use During:**
- Off-peak hours (11pm-7am) - Cheap electricity, full speed
- When GPU <50% usage (Blue Iris idle)
- When TrueNAS overloaded

---

## 🚀 PHASE 1: TrueNAS VM Setup (START NOW!)

### Step 1.1: Quick Network Check (2 minutes)

**You're in TrueNAS Web UI now:**

1. Click **Network** → **Interfaces**
2. Note the settings:
   - Link Speed: _____ Mbps
   - Interface: _____
   - Status: _____

**Tell me what you see, then we proceed.**

---

### Step 1.2: Create Ubuntu VM (15 minutes)

**In TrueNAS Web UI:**

1. Navigate to **Virtual Machines** (left menu)
2. Click **Add** (top right)
3. Configure VM:

```
Operating System: Linux
Name: ubuntu-ollama
Description: Ollama AI Server for Claude Code

vCPUs: 8
Cores: 8
Threads: 1
CPU Mode: Host Model

Memory: 24576 MB (24 GB)

Boot Method: UEFI
VNC Bind: 0.0.0.0:5901
```

4. Click **Next**

---

### Step 1.3: Configure Storage (5 minutes)

**Disk Configuration:**

```
Create new disk image: YES
Disk Type: AHCI
Zvol Location: [Select pool - likely "cheeta"]
Size: 100 GiB
```

**CD-ROM (for Ubuntu ISO):**
```
We'll add this in next step after VM creation
```

5. Click **Next**

---

### Step 1.4: Configure Network (5 minutes)

**Network Interface:**

```
Attach NIC: YES
Type: VirtIO
NIC to Attach: [Select your network bridge]
MAC Address: [Auto-generated]
```

6. Click **Next**
7. Review settings
8. Click **Submit**

**VM Created!** ✅

---

### Step 1.5: Download Ubuntu ISO (10 minutes)

**In TrueNAS Shell (top right corner → Shell):**

```bash
# Create ISO directory if doesn't exist
mkdir -p /mnt/cheeta/isos

# Download Ubuntu 22.04 LTS Server
cd /mnt/cheeta/isos
wget https://releases.ubuntu.com/22.04/ubuntu-22.04.5-live-server-amd64.iso

# Verify download
ls -lh ubuntu-22.04.5-live-server-amd64.iso
# Should be ~2.5 GB
```

**Wait for download to complete (~10 minutes depending on internet speed).**

---

### Step 1.6: Attach ISO to VM (2 minutes)

**Back in TrueNAS Web UI:**

1. Go to **Virtual Machines**
2. Click on **ubuntu-ollama** VM
3. Click **Devices**
4. Click **Add** → **CD-ROM**
5. Configure:
   ```
   CD-ROM Path: /mnt/cheeta/isos/ubuntu-22.04.5-live-server-amd64.iso
   ```
6. Click **Save**

---

### Step 1.7: Start VM & Install Ubuntu (20 minutes)

**Start VM:**
1. Click **Start** button on ubuntu-ollama VM
2. Click **VNC** button to open console

**Ubuntu Installation:**

**I'll guide you through EVERY screen. Are you ready to start?**

---

## ⏸️ PAUSE HERE

**Before we continue, please:**

1. **Check TrueNAS Network** (Step 1.1)
   - Go to Network → Interfaces
   - Tell me: Link Speed and Interface name

2. **Confirm you're ready** to create the VM

3. **I'll guide you** step-by-step through:
   - VM creation (click-by-click)
   - Ubuntu installation (screen-by-screen)
   - Ollama setup (command-by-command)
   - Then workstation
   - Then laptop configuration
   - Then testing

**Are you ready to start Step 1.1 (Network Check)?** 🎯

---

## 📝 What Comes After This

Once TrueNAS is done (Phase 1 complete):

**Phase 2: Workstation**
- Remote Desktop to DAM8940DELL
- Download Ollama for Windows
- Install and configure
- Pull GPU models
- Auto-start setup

**Phase 3: Laptop**
- Configure smart router
- Add time-based optimization
- Create manual override commands
- Test routing

**Phase 4: Testing**
- End-to-end workflow test
- Verify Blue Iris unaffected
- Verify time-based switching
- Performance benchmarks

**By end of today: Fully operational Claude Code + Ollama system!**

---

**Ready to start? Let me know and I'll guide you step-by-step!** 🚀
