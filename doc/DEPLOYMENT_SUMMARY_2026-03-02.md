# Claude Code + Ollama Deployment Summary
**Date:** March 2, 2026
**Goal:** Reduce Claude Code costs from $800/month to under $20/month
**Approach:** Deploy Ollama on TrueNAS (primary) + Workstation (secondary)

---

## 🎯 What We Accomplished Today

### ✅ Phase 1: TrueNAS VM Setup - COMPLETE

**VM Created:**
- Name: `ubuntuollama`
- RAM: 16 GB (reduced from 24 GB due to available memory)
- CPU: 8 vCPUs × 2 cores × 1 thread = 16 cores total
- Disk: 60 GB (on Cheeta/windowshare storage)
- OS: Ubuntu 22.04.5 LTS Server
- Network: Bridge (br0) with static IP 192.168.1.103

**Ollama Installed:**
- Version: 0.17.5
- Service: Auto-start enabled
- API Endpoint: `http://192.168.1.103:11434`
- Mode: CPU-only (no GPU in VM)

**Model Deployed:**
- Model: `qwen2.5-coder:14b`
- Size: ~14 GB
- Purpose: CPU-optimized code generation
- Performance: 20-30 seconds per response

**Network Configuration:**
- Created bridge interface `br0` in TrueNAS
- Bridge member: `em0` (physical interface)
- Bridge IP: 192.168.1.102 (TrueNAS host)
- VM IP: 192.168.1.103 (static, manual configuration)
- Gateway: 192.168.1.1
- DNS: 8.8.8.8, 8.8.4.4

**Configuration Files:**
- `/etc/systemd/system/ollama.service.d/override.conf`
  ```ini
  [Service]
  Environment="OLLAMA_HOST=0.0.0.0:11434"
  ```

**Testing:**
```bash
# Test model
ollama run qwen2.5-coder:14b "Write hello world in Python"

# Check status
systemctl status ollama

# List models
ollama list
```

---

### 🔄 Phase 2: Workstation Ollama Setup - IN PROGRESS

**Workstation Details:**
- Name: DAM8940DELL
- IP: 192.168.1.39
- OS: Windows 11 Pro
- GPU: NVIDIA RTX 3060 Ti (8GB VRAM)
- RAM: 32 GB
- Current Use: Blue Iris (24/7), income tax work, machine learning

**Ollama Installation:**
- Download: https://ollama.com/download/windows
- File: OllamaSetup.exe
- Status: Installing (in progress)

**Model to Deploy:**
- Model: `qwen3-coder:30b` ← UPDATED (Qwen 3, not 2.5!)
- Size: 19 GB
- Architecture: 30B total params, 3.3B activated (efficient)
- Context: 256K tokens
- Purpose: GPU-accelerated code generation
- Performance: 3-8 seconds per response (estimated)

**Commands After Install:**
```powershell
# Pull GPU-optimized model
ollama pull qwen3-coder:30b

# Verify installation
ollama list

# Test model
ollama run qwen3-coder:30b "Write hello world in Python"
```

**Configuration (After Install):**
- Enable network access: Edit `C:\Users\<username>\.ollama\config.json`
  ```json
  {
    "host": "0.0.0.0:11434"
  }
  ```
- Restart Ollama service: `Restart-Service Ollama`

---

### ⏳ Phase 3: Laptop Smart Router Configuration - PENDING

**Laptop Details:**
- Name: HP Envy
- OS: Windows 11 Home + WSL Ubuntu
- Claude Code: Installed in WSL
- API Key: `REDACTED_ANTHROPIC_API_KEY`
- Location: `/home/boatiq/.claude.json` (line 115)

**Smart Router Script:**
- File: `/home/boatiq/scripts/smart-claude-router.sh`
- Purpose: Automatically route Claude Code requests to best available backend
- Logic:
  1. Check workstation GPU usage (via nvidia-smi over SSH)
  2. If GPU <70% usage → Use workstation Ollama (fast, GPU)
  3. If GPU >70% busy → Use TrueNAS Ollama (slower, CPU, doesn't interfere)
  4. If both unavailable → Use Anthropic API (costs money)

**Router Configuration (NEEDS UPDATE):**
```bash
# Update workstation IP in router script
nano /home/boatiq/scripts/smart-claude-router.sh

# Line 8: Change this
WORKSTATION_IP="192.168.1.XXX"  # UPDATE with actual IP

# To this:
WORKSTATION_IP="192.168.1.39"
```

**Bash Aliases (Add to ~/.bashrc or ~/.bash_aliases):**
```bash
# Profile 1: Use Anthropic API (Premium - costs money)
alias claude-premium='
    export ANTHROPIC_API_KEY="REDACTED_ANTHROPIC_API_KEY"
    unset ANTHROPIC_BASE_URL
    echo "💰 Using Anthropic API (Premium - costs money)"
    claude-code
'

# Profile 2: Use Workstation Ollama (FREE, GPU-accelerated)
alias claude-workstation='
    export ANTHROPIC_API_KEY="ollama"
    export ANTHROPIC_BASE_URL="http://192.168.1.39:11434/v1"
    echo "🚀 Using Workstation Ollama (FREE, GPU-accelerated)"
    claude-code
'

# Profile 3: Use TrueNAS Ollama (FREE, CPU-only)
alias claude-truenas='
    export ANTHROPIC_API_KEY="ollama"
    export ANTHROPIC_BASE_URL="http://192.168.1.103:11434/v1"
    echo "🖥️  Using TrueNAS Ollama (FREE, CPU-only)"
    claude-code
'

# Profile 4: Smart Auto-Routing (RECOMMENDED)
alias claude='bash /home/boatiq/scripts/smart-claude-router.sh'
```

**Usage:**
```bash
# Automatic routing (recommended)
claude

# Manual selection
claude-premium        # Use Anthropic API
claude-workstation    # Force workstation
claude-truenas        # Force TrueNAS
```

**Time-Based Optimization (In Router Script):**
- Peak hours (7am-7pm): Prefer TrueNAS CPU OR efficient models (save electricity)
- Medium hours (7pm-11pm): Balance speed/cost
- Off-peak hours (11pm-7am): Use workstation GPU, maximum performance (cheap electricity)

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Your Network                             │
│                      (192.168.1.0/24)                            │
└─────────────────────────────────────────────────────────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
        ▼                        ▼                        ▼
┌───────────────┐      ┌─────────────────┐      ┌──────────────────┐
│   Laptop      │      │  Workstation    │      │   TrueNAS        │
│   HP Envy     │      │  DAM8940DELL    │      │   Teyko2         │
│               │      │                 │      │                  │
│ WSL Ubuntu    │      │ Windows 11 Pro  │      │ 192.168.1.102    │
│ Claude Code   │◄────►│ 192.168.1.39    │      │                  │
│               │      │                 │      │ ┌──────────────┐ │
│ Smart Router  │      │ Ollama (GPU)    │      │ │ Ubuntu VM    │ │
│               │      │ qwen3-coder:30b │      │ │ 192.168.1.103│ │
│               │      │ RTX 3060 Ti     │      │ │              │ │
│               │      │ 3-8s responses  │      │ │ Ollama (CPU) │ │
│               │      │                 │      │ │ qwen2.5:14b  │ │
│               │      │ Blue Iris 24/7  │      │ │ 20-30s resp  │ │
└───────────────┘      └─────────────────┘      │ └──────────────┘ │
                                                 └──────────────────┘

Routing Logic:
1. Check workstation GPU usage
   ├─ <70% → Use Workstation (fast, GPU) ✅
   └─ >70% → Use TrueNAS (CPU, doesn't interfere) ✅
2. If both unavailable → Use Anthropic API (costs $$$) ⚠️
```

---

## 💰 Cost Analysis

### Before Deployment:
- **Anthropic API:** $800/month (all requests)

### After Deployment (Estimated):
- **Laptop Anthropic:** $20-50/month (critical tasks only)
- **Workstation Ollama:** $0/month (FREE)
- **TrueNAS Ollama:** $0/month (FREE)
- **Electricity:** ~$13/month (both systems running)
- **Total:** $33-63/month

**Savings:** $737-767/month (92-96% reduction!)

---

## 🔧 Commands Reference

### TrueNAS VM Commands (via SSH to 192.168.1.103)

```bash
# Check Ollama status
systemctl status ollama

# Restart Ollama
sudo systemctl restart ollama

# List models
ollama list

# Pull new model
ollama pull <model-name>

# Test model
ollama run <model-name> "Your prompt here"

# Check logs
journalctl -u ollama -f

# Check system resources
htop
free -h
df -h
```

### Workstation Commands (PowerShell)

```powershell
# Check Ollama status
Get-Service Ollama

# Restart Ollama
Restart-Service Ollama

# List models
ollama list

# Pull new model
ollama pull <model-name>

# Test model
ollama run <model-name> "Your prompt here"

# Check GPU usage
nvidia-smi

# Check Ollama service config
Get-Content C:\Users\$env:USERNAME\.ollama\config.json
```

### Laptop Commands (WSL Ubuntu)

```bash
# Test TrueNAS connection
curl http://192.168.1.103:11434/api/tags

# Test Workstation connection
curl http://192.168.1.39:11434/api/tags

# Test Anthropic API
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-sonnet-4.5","max_tokens":1024,"messages":[{"role":"user","content":"Hello"}]}'

# Use router
claude "Your question here"

# Use specific backend
claude-workstation "Your question here"
claude-truenas "Your question here"
claude-premium "Your question here"
```

---

## 📝 Next Steps (Remaining)

### 1. Complete Workstation Setup (20 min)
- [ ] Wait for Ollama installation to finish
- [ ] Pull qwen3-coder:30b model (~15 min download)
- [ ] Test model with simple query
- [ ] Verify GPU acceleration working (nvidia-smi shows activity)
- [ ] Enable network access (edit config.json)

### 2. Configure Laptop Router (30 min)
- [ ] Update smart-claude-router.sh with workstation IP (192.168.1.39)
- [ ] Add bash aliases to ~/.bashrc
- [ ] Source ~/.bashrc (or restart terminal)
- [ ] Test all routing scenarios:
  - [ ] claude-premium (Anthropic API)
  - [ ] claude-workstation (GPU Ollama)
  - [ ] claude-truenas (CPU Ollama)
  - [ ] claude (auto-routing)

### 3. Testing & Verification (30 min)
- [ ] Test automatic GPU detection (workstation <70% → use GPU)
- [ ] Test failover (workstation busy → TrueNAS)
- [ ] Test fallback (both unavailable → Anthropic API)
- [ ] Verify Blue Iris not impacted by Ollama GPU usage
- [ ] Compare response times:
  - [ ] Workstation GPU: Should be 3-8 seconds
  - [ ] TrueNAS CPU: Should be 20-30 seconds
  - [ ] Anthropic API: Should be 5-10 seconds

### 4. Documentation & Training (15 min)
- [ ] Save this document for future reference
- [ ] Note any issues or improvements needed
- [ ] Document actual costs after 1 week of use

---

## ⚠️ Important Notes

### TrueNAS VM Limitations:
- **RAM:** Only 16 GB available (not 24 GB as planned)
  - TrueNAS has 31.9 GB total, 17.4 GB available
  - VM uses 16 GB, leaves room for ZFS cache (9.8 GB)
- **Network:** Required bridge configuration (br0)
  - Direct attachment to physical interface (re0) didn't work
  - Bridge required for VM network access
- **Performance:** CPU-only inference is slow (20-30s)
  - Good for non-urgent tasks, overnight processing
  - Workstation GPU is 4-6× faster

### Workstation Constraints:
- **Blue Iris:** Runs 24/7, uses GPU continuously
  - Smart router checks GPU usage before routing
  - If >70% busy, routes to TrueNAS instead
- **User Priority:** Income tax work, surveillance, other tasks take precedence
  - Ollama will run with lower priority (won't interfere)
- **Confidential Data:** NO FILE DELETION allowed
  - All workstation files must remain untouched
- **Time-Based Usage:** Electricity costs vary by time
  - Peak (7am-7pm): High cost → prefer TrueNAS or efficient models
  - Off-peak (11pm-7am): Low cost → use workstation GPU freely

### Network Setup:
- **Subnet:** 192.168.1.0/24
- **Gateway:** 192.168.1.1
- **TrueNAS Host:** 192.168.1.102 (bridge br0)
- **TrueNAS VM:** 192.168.1.103 (static IP)
- **Workstation:** 192.168.1.39
- **Latency Issue:** TrueNAS had 88ms ping initially
  - Fixed by creating proper network bridge
  - Should now be <10ms

---

## 🔍 Troubleshooting

### If TrueNAS Ollama Not Responding:
```bash
# SSH to VM
ssh ollama@192.168.1.103

# Check service
systemctl status ollama

# Check logs
journalctl -u ollama -n 50

# Restart if needed
sudo systemctl restart ollama

# Test locally
curl http://localhost:11434/api/tags
```

### If Workstation Ollama Not Responding:
```powershell
# Check service
Get-Service Ollama

# Check if listening on network
netstat -an | findstr 11434

# Restart service
Restart-Service Ollama

# Check logs (Event Viewer)
Get-EventLog -LogName Application -Source Ollama -Newest 10
```

### If Smart Router Not Working:
```bash
# Check router script
cat /home/boatiq/scripts/smart-claude-router.sh

# Make executable
chmod +x /home/boatiq/scripts/smart-claude-router.sh

# Test GPU check manually
ssh user@192.168.1.39 "nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits"

# Check environment variables
echo $ANTHROPIC_API_KEY
echo $ANTHROPIC_BASE_URL
```

---

## 📚 Resources

**Ollama Documentation:**
- https://ollama.com/
- https://ollama.com/library/qwen3-coder
- https://github.com/ollama/ollama

**Claude Code Documentation:**
- https://docs.anthropic.com/claude/docs/claude-code

**Model Information:**
- Qwen3-Coder: https://huggingface.co/Qwen/Qwen3-Coder-Next
- Qwen 2.5 Coder: https://huggingface.co/Qwen/Qwen2.5-Coder

**TrueNAS Documentation:**
- VM Setup: https://www.truenas.com/docs/scale/scaletutorials/virtualization/
- Network Bridge: https://www.truenas.com/docs/scale/scaletutorials/network/interfaces/settingupbridge/

---

## ✅ Summary

**What Works:**
- ✅ TrueNAS VM running Ubuntu 22.04
- ✅ Ollama installed on TrueNAS VM
- ✅ qwen2.5-coder:14b model deployed (CPU)
- ✅ Network bridge configured (VM has internet)
- ✅ SSH access working (PuTTY → 192.168.1.103)
- ✅ Ollama API accessible on network (0.0.0.0:11434)
- ✅ Workstation Ollama installing (in progress)

**What's Pending:**
- ⏳ Workstation model download (qwen3-coder:30b)
- ⏳ Laptop router configuration
- ⏳ End-to-end testing
- ⏳ Cost monitoring (verify savings)

**Estimated Time to Complete:**
- Workstation setup: 20 minutes
- Router config: 30 minutes
- Testing: 30 minutes
- **Total remaining:** ~80 minutes

**Expected Outcome:**
- Monthly cost: $33-63 (was $800) ✅
- Workstation responses: 3-8 seconds ⚡
- TrueNAS responses: 20-30 seconds 🐌
- Automatic routing: Smart, no manual intervention required ✅

---

**Document Created:** March 2, 2026
**Last Updated:** March 2, 2026 - 5:40 PM UTC
**Status:** Phase 1 Complete, Phase 2 In Progress
