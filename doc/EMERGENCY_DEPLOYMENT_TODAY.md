# EMERGENCY DEPLOYMENT PLAN - DEPLOY TODAY
**Date:** 2026-03-02
**Deadline:** End of day (8-10 hours work)
**Crisis:** Claude Code costs $800/month → Must reduce to under $20/month TODAY

---

## 🚨 CRISIS SUMMARY

**Problem:**
- Claude Code costs: $800 in February
- Unsustainable for continued development
- Need immediate cost reduction

**Solution:**
- Deploy Ollama on **BOTH Workstation (GPU) + TrueNAS (CPU)**
- Workstation PRIMARY (RTX 3060 Ti, 32GB RAM) - Fast responses (3-15s)
- TrueNAS BACKUP (24 GB RAM, CPU-only) - Slower but always available (20-120s)
- Switch 95% of tasks to local Ollama (FREE)
- Keep Claude Code for orchestration only (5% usage)

**Target:**
- Reduce costs from $800/month → under $20/month
- **97.5% cost reduction**
- Deploy in 3.5 hours (today) - DUAL SYSTEM APPROACH

---

## ⚡ STREAMLINED 3.5-HOUR PLAN (DUAL SYSTEM)

### 🎯 STRATEGY: Deploy Both Systems

**Workstation (RTX 3060 Ti GPU):**
- **PRIMARY** for interactive development
- Fast responses: 3-15 seconds
- High-quality larger models
- Use when at workstation

**TrueNAS (CPU-only):**
- **BACKUP** when workstation unavailable
- Slower responses: 20-120 seconds
- Smaller CPU-optimized models
- Always available (24/7)
- Good for batch/overnight tasks

---

### Phase 0: Workstation Ollama Setup (30 min) - DO THIS FIRST!
**Goal:** Get fast GPU-accelerated Ollama on workstation

**Time: 09:00 - 09:30 (30 min)**

#### Step 0.1: Install Ollama on Windows Workstation (10 min)
```powershell
# Download Ollama for Windows
# Visit: https://ollama.com/download/windows
# Run: OllamaSetup.exe

# After installation completes, verify
ollama --version
```

#### Step 0.2: Pull GPU-Optimized Models (15 min)
```powershell
# Open PowerShell or Command Prompt

# Model 1: DeepSeek-Coder-V2 16B - Code generation (PRIMARY)
ollama pull deepseek-coder-v2:16b
# VRAM: 6-7 GB, Speed: 40-60 tokens/sec

# Model 2: Qwen2.5-Coder 14B - Documentation
ollama pull qwen2.5-coder:14b
# VRAM: 5-6 GB, Speed: 40-50 tokens/sec

# Model 3: CodeLlama 13B - Code review
ollama pull codellama:13b
# VRAM: 5-6 GB, Speed: 35-45 tokens/sec

# Model 4: Llama 3.1 8B - General purpose
ollama pull llama3.1:8b
# VRAM: 3-4 GB, Speed: 60-80 tokens/sec

# Verify models installed
ollama list
```

#### Step 0.3: Enable Network Access (5 min)
```powershell
# Stop Ollama service
Stop-Service Ollama

# Create/edit config file
notepad C:\Users\%USERNAME%\.ollama\config.json

# Add this content:
{
  "host": "0.0.0.0:11434"
}

# Save and close

# Start Ollama service
Start-Service Ollama

# Test from laptop
# curl http://WORKSTATION_IP:11434/api/tags
```

#### Step 0.4: Test GPU Acceleration (5 min)
```powershell
# Generate code to test GPU
ollama run deepseek-coder-v2:16b "Write a Python hello world function"

# Open Task Manager (Ctrl+Shift+Esc)
# Go to Performance → GPU
# Should see GPU activity while running

# Expected: Response in 5-10 seconds (GPU-accelerated)
```

**✅ Phase 0 Complete: Workstation ready (30 min)**

---

### Phase 1: TrueNAS Ubuntu VM Setup (1.5 hours) - BACKUP SYSTEM
**Goal:** Get Ubuntu VM running with CPU-optimized Ollama

**Time: 09:30 - 11:00 (1.5 hours)**

#### Step 1.1: Create VM on TrueNAS (30 min)
```bash
# Access TrueNAS web UI
http://192.168.1.102
# Login: root / damcor53$

# Navigate to: Virtual Machines → Add

Configuration:
- Name: ubuntu-ollama-dev
- OS Type: Linux
- vCPUs: 8
- RAM: 24576 MB (24 GB) ← UPDATED from 16 GB
- Boot Method: UEFI
- VNC Port: 5901

Storage:
- Disk 1: 100 GB (Create new Zvol on Cheeta)

Network:
- NIC 1: Bridged adapter (em0 or igb0)
- DHCP: Disabled
- Static IP: 192.168.1.103
- Gateway: 192.168.1.1
- DNS: 8.8.8.8

# Save and create VM
```

#### Step 1.2: Download Ubuntu ISO (15 min)
```bash
# SSH to TrueNAS
ssh root@192.168.1.102

# Download Ubuntu 22.04 Server
cd /mnt/cheeta/isos
wget https://releases.ubuntu.com/22.04/ubuntu-22.04.4-live-server-amd64.iso

# Verify download
ls -lh ubuntu-22.04.4-live-server-amd64.iso
```

#### Step 1.3: Install Ubuntu (1.5 hours)
```bash
# Attach ISO to VM in TrueNAS UI
# Virtual Machines → ubuntu-ollama-dev → Devices → CD-ROM → Select ISO

# Start VM
# Open VNC console (port 5901)

# Ubuntu Installation:
1. Language: English
2. Keyboard: English (US)
3. Network: Configure static IP
   - IP: 192.168.1.103/24
   - Gateway: 192.168.1.1
   - DNS: 8.8.8.8
4. Proxy: (leave blank)
5. Mirror: (default)
6. Storage: Use entire disk
7. Profile:
   - Name: ollama
   - Server: ubuntu-ollama
   - Username: ollama
   - Password: ollama2026
8. SSH: Install OpenSSH server (ENABLE)
9. Featured Server Snaps: (skip)
10. Install and wait (~20 min)
11. Reboot

# After reboot, eject ISO in TrueNAS UI
```

#### Step 1.4: Configure Ubuntu (30 min)
```bash
# SSH from laptop
ssh ollama@192.168.1.103
# Password: ollama2026

# Update system
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y curl git python3-pip htop iotop net-tools

# Configure firewall
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 11434/tcp # Ollama API
sudo ufw enable

# Test network speed (10 Gig Ethernet)
sudo apt install -y iperf3
# (Run iperf3 test from laptop later)

# Reboot
sudo reboot
```

---

### Phase 2: Ollama Installation (1.5 hours)
**Goal:** Deploy Ollama with essential models

**Time: 12:00 - 13:30 (1.5 hours)**

#### Step 2.1: Install Ollama (15 min)
```bash
# SSH to Ubuntu VM
ssh ollama@192.168.1.103

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
ollama --version

# Configure Ollama to listen on all interfaces
sudo systemctl edit ollama

# Add these lines:
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"

# Save and exit (Ctrl+X, Y, Enter)

# Restart Ollama
sudo systemctl restart ollama

# Verify service running
sudo systemctl status ollama
```

#### Step 2.2: Pull CPU-Optimized Models (30 min)
```bash
# TrueNAS uses CPU-only (no GPU), so use smaller, optimized models

# Model 1: Qwen2.5 Coder 7B - Code + documentation (PRIMARY)
ollama pull qwen2.5-coder:7b
# Time: ~10 min
# RAM: 8-10 GB
# Speed: 5-10 tokens/sec (20-60 seconds per task)

# Model 2: DeepSeek Coder 6.7B - Code generation
ollama pull deepseek-coder:6.7b
# Time: ~10 min
# RAM: 8-10 GB
# Speed: 5-10 tokens/sec

# Model 3: Llama 3.1 8B - General purpose
ollama pull llama3.1:8b
# Time: ~10 min
# RAM: 10-12 GB
# Speed: 8-12 tokens/sec

# Verify models installed
ollama list

# Expected output:
# NAME                    ID              SIZE    MODIFIED
# qwen2.5-coder:7b       abc123...       7 GB    2 minutes ago
# deepseek-coder:6.7b    def456...       6.7 GB  5 minutes ago
# llama3.1:8b            ghi789...       8 GB    8 minutes ago

# NOTE: These are smaller than workstation models but optimized for CPU
# TrueNAS is BACKUP system - Workstation GPU is PRIMARY (faster)
```

#### Step 2.3: Test Ollama API (15 min)
```bash
# Test from Ubuntu VM (localhost)
curl http://localhost:11434/api/tags

# Test from laptop (network)
curl http://192.168.1.103:11434/api/tags

# Expected: JSON response with model list

# Test code generation
curl http://192.168.1.103:11434/api/generate -d '{
  "model": "deepseek-coder-v2:16b",
  "prompt": "Write a Python function to convert Celsius to Fahrenheit",
  "stream": false
}'

# Expected: JSON response with generated code (~10-30 seconds)

# Check response time
time curl -s http://192.168.1.103:11434/api/generate -d '{
  "model": "deepseek-coder-v2:16b",
  "prompt": "Write a simple hello world in Python",
  "stream": false
}' > /dev/null

# Expected: 5-15 seconds (acceptable)
```

---

### Phase 3: Ollama Integration Scripts (2 hours)
**Goal:** Create helper scripts to use Ollama from laptop

**Time: 13:30 - 15:30 (2 hours)**

#### Step 3.1: Create Ollama Helper Script (30 min)
```bash
# On laptop
mkdir -p /home/boatiq/scripts
cd /home/boatiq/scripts

# Create ollama-assist.sh
cat > ollama-assist.sh << 'EOF'
#!/bin/bash
# Ollama Development Assistant
# Usage: ./ollama-assist.sh {code|review|docs|explain} "<prompt>"

OLLAMA_API="http://192.168.1.103:11434"
COMMAND=$1
shift
PROMPT="$@"

if [ -z "$COMMAND" ] || [ -z "$PROMPT" ]; then
    echo "Usage: $0 {code|review|docs|explain} \"<prompt>\""
    exit 1
fi

case $COMMAND in
    code)
        MODEL="deepseek-coder-v2:16b"
        SYSTEM="You are an expert programmer. Generate clean, production-ready code with error handling and documentation."
        ;;
    review)
        MODEL="codellama:34b"
        SYSTEM="You are a senior code reviewer. Analyze code quality, identify issues, and suggest improvements."
        ;;
    docs)
        MODEL="qwen2.5-coder:32b"
        SYSTEM="You are a technical writer. Generate clear, comprehensive documentation."
        ;;
    explain)
        MODEL="qwen2.5-coder:32b"
        SYSTEM="You are a patient teacher. Explain technical concepts clearly with examples."
        ;;
    *)
        echo "Unknown command: $COMMAND"
        echo "Valid commands: code, review, docs, explain"
        exit 1
        ;;
esac

echo "🤖 Using $MODEL..."
echo ""

curl -s ${OLLAMA_API}/api/generate -d "{
    \"model\": \"${MODEL}\",
    \"prompt\": \"${SYSTEM}\n\n${PROMPT}\",
    \"stream\": false
}" | jq -r '.response'

echo ""
echo "✅ Done"
EOF

# Make executable
chmod +x ollama-assist.sh

# Test it
./ollama-assist.sh code "Write a Python function to calculate factorial"
```

#### Step 3.2: Create Batch Processing Script (30 min)
```bash
# Create ollama-batch.sh for processing multiple files
cat > /home/boatiq/scripts/ollama-batch.sh << 'EOF'
#!/bin/bash
# Batch process files with Ollama
# Usage: ./ollama-batch.sh {code|review|docs} <file1> <file2> ...

OLLAMA_API="http://192.168.1.103:11434"
COMMAND=$1
shift
FILES="$@"

if [ -z "$COMMAND" ] || [ -z "$FILES" ]; then
    echo "Usage: $0 {code|review|docs} <file1> <file2> ..."
    exit 1
fi

for FILE in $FILES; do
    echo "🔄 Processing: $FILE"

    CONTENT=$(cat "$FILE")

    case $COMMAND in
        review)
            PROMPT="Review this code and provide feedback:\n\n${CONTENT}"
            MODEL="codellama:34b"
            ;;
        docs)
            PROMPT="Generate documentation for this code:\n\n${CONTENT}"
            MODEL="qwen2.5-coder:32b"
            ;;
        *)
            echo "Unknown command: $COMMAND"
            continue
            ;;
    esac

    RESPONSE=$(curl -s ${OLLAMA_API}/api/generate -d "{
        \"model\": \"${MODEL}\",
        \"prompt\": \"${PROMPT}\",
        \"stream\": false
    }" | jq -r '.response')

    echo "$RESPONSE" > "${FILE}.${COMMAND}.txt"
    echo "✅ Saved to: ${FILE}.${COMMAND}.txt"
    echo ""
done

echo "🎉 Batch processing complete!"
EOF

chmod +x ollama-batch.sh
```

#### Step 3.3: Create Claude Code Integration (1 hour)
```bash
# Create Python wrapper for Claude Code to delegate to Ollama
cat > /home/boatiq/scripts/ollama_delegate.py << 'EOF'
#!/usr/bin/env python3
"""
Ollama Delegation System
Allows Claude Code to delegate tasks to local Ollama
"""

import requests
import json
import sys
import time

OLLAMA_API = "http://192.168.1.103:11434"

class OllamaDelegate:
    def __init__(self):
        self.api_url = OLLAMA_API

    def check_health(self):
        """Check if Ollama is responding"""
        try:
            response = requests.get(f"{self.api_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

    def generate_code(self, task_description, language="python", context=""):
        """Generate code for a specific task"""
        prompt = f"""Task: {task_description}
Language: {language}
Context: {context}

Generate production-ready code with:
1. Proper error handling
2. Type hints (if applicable)
3. Docstrings/comments
4. Input validation

Code:
"""
        return self._call_ollama("deepseek-coder-v2:16b", prompt)

    def review_code(self, code, requirements=""):
        """Review code quality and suggest improvements"""
        prompt = f"""Review this code:

{code}

Requirements: {requirements}

Provide:
1. Code quality score (0-10)
2. Issues found (bugs, security, performance)
3. Suggestions for improvement
4. Best practices violations

Review:
"""
        return self._call_ollama("codellama:34b", prompt)

    def generate_documentation(self, code, format="markdown"):
        """Generate documentation for code"""
        prompt = f"""Generate comprehensive documentation for this code:

{code}

Format: {format}

Include:
1. Overview/purpose
2. Parameters and return values
3. Usage examples
4. Error handling
5. Dependencies

Documentation:
"""
        return self._call_ollama("qwen2.5-coder:32b", prompt)

    def explain_code(self, code):
        """Explain what code does in plain language"""
        prompt = f"""Explain what this code does in simple terms:

{code}

Explanation:
"""
        return self._call_ollama("qwen2.5-coder:32b", prompt)

    def _call_ollama(self, model, prompt):
        """Internal method to call Ollama API"""
        start_time = time.time()

        try:
            response = requests.post(
                f"{self.api_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=300  # 5 minutes max
            )

            elapsed_time = time.time() - start_time

            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response": result["response"],
                    "model": model,
                    "elapsed_time": elapsed_time
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "elapsed_time": elapsed_time
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "elapsed_time": time.time() - start_time
            }

def main():
    if len(sys.argv) < 3:
        print("Usage: ollama_delegate.py {code|review|docs|explain} <prompt>")
        sys.exit(1)

    command = sys.argv[1]
    prompt = " ".join(sys.argv[2:])

    delegate = OllamaDelegate()

    # Check health
    if not delegate.check_health():
        print("❌ Error: Ollama is not responding at", OLLAMA_API)
        sys.exit(1)

    print(f"🤖 Delegating to Ollama ({command})...")

    if command == "code":
        result = delegate.generate_code(prompt)
    elif command == "review":
        result = delegate.review_code(prompt)
    elif command == "docs":
        result = delegate.generate_documentation(prompt)
    elif command == "explain":
        result = delegate.explain_code(prompt)
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)

    if result["success"]:
        print(f"\n✅ Response (took {result['elapsed_time']:.1f}s):\n")
        print(result["response"])
    else:
        print(f"\n❌ Error: {result['error']}")
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

chmod +x ollama_delegate.py

# Test it
python3 ollama_delegate.py code "Write a function to validate email addresses"
```

---

### Phase 4: Directory Structure (30 min)
**Goal:** Create organized project folders (fast version)

**Time: 15:30 - 16:00 (30 min)**

```bash
# SSH to TrueNAS
ssh root@192.168.1.102

# Create project structure
mkdir -p /mnt/cheeta/projects/{d3kOS,AAO-Methodology,Marketing,Content,WordPress}
mkdir -p /mnt/cheeta/projects/d3kOS/{code,docs,datasets,models,releases,testing}
mkdir -p /mnt/cheeta/projects/AAO-Methodology/{docs,research,implementation}
mkdir -p /mnt/cheeta/projects/Marketing/{videos,scripts,assets,exports}
mkdir -p /mnt/cheeta/projects/Content/{atmyboat-blog,linkedin,forums,drafts}
mkdir -p /mnt/cheeta/projects/Content/forums/{open-marine,cruiser-forum,trawler-forum,boat-builder}
mkdir -p /mnt/cheeta/projects/WordPress/{atmyboat-com,themes,backups}
mkdir -p /mnt/cheeta/development/{laptop-sync,workstation-sync,shared}
mkdir -p /mnt/cheeta/archives

# Create backup structure
mkdir -p /mnt/beaver/backups/{TrueNAS,Laptop,Workstation}
mkdir -p /mnt/beaver/backups/TrueNAS/{config,credentials,datasets}

# Set permissions
chmod -R 755 /mnt/cheeta/projects
chmod -R 755 /mnt/cheeta/development

# Verify
ls -la /mnt/cheeta/projects/
ls -la /mnt/beaver/backups/
```

---

### Phase 5: Quick Backup Setup (1 hour)
**Goal:** Basic ZFS snapshots (full automation later)

**Time: 16:00 - 17:00 (1 hour)**

#### Step 5.1: Create Snapshot Script
```bash
# SSH to TrueNAS
ssh root@192.168.1.102

# Create scripts directory
mkdir -p /root/scripts

# Create snapshot script
cat > /root/scripts/snapshot-cheeta.sh << 'EOF'
#!/bin/sh
# Snapshot Cheeta projects

TIMESTAMP=$(date +%Y-%m-%d-%H%M)
DATASET="cheeta/projects"
SNAPSHOT="${DATASET}@${TIMESTAMP}"

# Create snapshot
zfs snapshot ${SNAPSHOT}

# Log
echo "$(date): Created ${SNAPSHOT}" >> /var/log/zfs-snapshots.log

# Keep last 60 snapshots (30 days with noon+midnight)
zfs list -t snapshot -o name,creation -s creation | \
  grep "^${DATASET}@" | \
  head -n -60 | \
  awk '{print $1}' | \
  xargs -n 1 zfs destroy 2>/dev/null || true

echo "$(date): Cleanup complete" >> /var/log/zfs-snapshots.log
EOF

chmod +x /root/scripts/snapshot-cheeta.sh

# Test it
/root/scripts/snapshot-cheeta.sh

# Verify snapshot created
zfs list -t snapshot | grep cheeta
```

#### Step 5.2: Add Cron Jobs
```bash
# Edit crontab
crontab -e

# Add these lines:
0 12 * * * /root/scripts/snapshot-cheeta.sh
0 0 * * * /root/scripts/snapshot-cheeta.sh

# Save and exit

# Verify cron jobs
crontab -l
```

---

### Phase 6: New Development Workflow (1.5 hours)
**Goal:** Start using Ollama instead of Claude Code for routine tasks

**Time: 17:00 - 18:30 (1.5 hours)**

#### Step 6.1: Create Usage Guide
```bash
# On laptop
cat > /home/boatiq/OLLAMA_USAGE_GUIDE.md << 'EOF'
# Ollama Usage Guide - Cost Reduction Strategy

## 🎯 Goal
Reduce Claude Code usage from $800/month to under $20/month by delegating 95% of tasks to local Ollama.

---

## 📋 Task Delegation Rules

### ✅ USE OLLAMA (FREE) for:
1. **Code Generation**
   - Writing new functions/classes
   - Implementing features
   - Bug fixes
   - Refactoring

2. **Documentation**
   - API documentation
   - User guides
   - Code comments
   - README files

3. **Code Review**
   - Quality checks
   - Security analysis
   - Performance review
   - Best practices

4. **Explanations**
   - How code works
   - Technical concepts
   - Error messages

5. **Testing**
   - Unit test generation
   - Test case ideas
   - Integration tests

**Estimated:** 90-95% of development tasks

---

### ⚠️ USE CLAUDE CODE (PAID) for:
1. **High-Level Planning**
   - Architecture decisions
   - System design
   - Technology choices

2. **Complex Multi-Step Tasks**
   - Orchestrating multiple changes
   - Cross-system integration
   - Complex debugging

3. **Critical Decisions**
   - Security-sensitive changes
   - Database migrations
   - Production deployments

**Estimated:** 5-10% of tasks only

---

## 🛠️ How to Use Ollama Scripts

### Basic Commands

**Generate Code:**
```bash
cd /home/boatiq/scripts
./ollama-assist.sh code "Write a function to parse NMEA2000 PGN 127488"
```

**Review Code:**
```bash
./ollama-assist.sh review "$(cat /path/to/file.py)"
```

**Generate Documentation:**
```bash
./ollama-assist.sh docs "$(cat /path/to/file.py)"
```

**Explain Code:**
```bash
./ollama-assist.sh explain "$(cat /path/to/complex-function.js)"
```

### Python Delegation

```python
# Import delegation module
from ollama_delegate import OllamaDelegate

delegate = OllamaDelegate()

# Generate code
result = delegate.generate_code(
    task_description="Create a function to validate boat hull identification numbers",
    language="python",
    context="For d3kOS onboarding wizard"
)

print(result["response"])
```

### Batch Processing

**Review all Python files in a directory:**
```bash
cd /home/boatiq/Helm-OS/services
../scripts/ollama-batch.sh review *.py
```

**Generate docs for all files:**
```bash
../scripts/ollama-batch.sh docs *.py
```

---

## 💰 Cost Comparison Examples

### Example 1: Add Temperature Conversion Feature

**Old Way (100% Claude Code):**
- Time: 45 minutes
- Cost: ~$4.50
- Manual approvals: 8 steps

**New Way (95% Ollama + 5% Claude Code):**
- Claude Code: Plan architecture (5 min, $0.50)
- Ollama: Generate code (10 min, FREE)
- Ollama: Generate tests (5 min, FREE)
- Ollama: Generate docs (3 min, FREE)
- Claude Code: Review and approve (2 min, $0.20)
- **Total: 25 min, $0.70 (84% savings)**

### Example 2: Write Documentation

**Old Way:**
- Claude Code: 30 minutes
- Cost: ~$3.00

**New Way:**
- Ollama: Generate docs (5 min, FREE)
- Quick review: (1 min, FREE)
- **Total: 6 min, $0 (100% savings)**

### Example 3: Bug Fix

**Old Way:**
- Claude Code: Read files, analyze, fix (20 min, $2.00)

**New Way:**
- Ollama: Analyze and suggest fix (5 min, FREE)
- Implement fix: (2 min, FREE)
- **Total: 7 min, $0 (100% savings)**

---

## 📊 Expected Monthly Savings

**February Breakdown (All Claude Code):**
- Total cost: $800
- Average sessions: ~40 per month
- Average cost per session: $20

**New System (Ollama + Claude Code):**
- Ollama tasks: 38 sessions (95%) = $0
- Claude Code tasks: 2 sessions (5%) = $10-15
- **Total: $10-15/month**
- **Savings: $785-790/month (98% reduction!)**

---

## 🚀 Workflow Example

**Task: Implement Metric/Imperial Conversion in d3kOS**

**Step 1: Planning (Claude Code - 5 min, $0.50)**
```
User: "I need metric/imperial conversion in the dashboard"
Claude Code:
  - Analyzes requirements
  - Creates implementation plan
  - Identifies files to modify
  - Delegates code generation to Ollama
```

**Step 2: Code Generation (Ollama - 10 min, FREE)**
```bash
./ollama-assist.sh code "Create conversion functions for:
- Temperature (°F ↔ °C)
- Pressure (PSI ↔ bar)
- Speed (knots ↔ km/h)
- Distance (nm ↔ km)

Include error handling and type hints."
```

**Step 3: Testing (Ollama - 5 min, FREE)**
```bash
./ollama-assist.sh code "Generate pytest unit tests for the conversion functions"
```

**Step 4: Documentation (Ollama - 3 min, FREE)**
```bash
./ollama-assist.sh docs "$(cat conversion_utils.py)"
```

**Step 5: Review (Claude Code - 2 min, $0.20)**
```
Claude Code:
  - Reviews Ollama output
  - Verifies correctness
  - Approves or requests changes
```

**Total: 25 min, $0.70 (vs 45 min, $4.50 old way)**

---

## 🎓 Best Practices

1. **Always use Ollama first** - Try local before going to Claude Code
2. **Batch similar tasks** - Use ollama-batch.sh for multiple files
3. **Cache responses** - Save good responses for reuse
4. **Claude Code for oversight** - Final review and approval
5. **Monitor costs** - Track Claude Code usage monthly

---

## 📈 Success Metrics

**Target for March 2026:**
- Claude Code cost: Under $20/month
- Ollama usage: 95%+ of tasks
- Development speed: 2-3× faster (local = instant)
- Manual approvals: Minimal

**If you exceed $20 in Claude Code costs:**
- Review what tasks used Claude Code
- Identify if they could have used Ollama
- Adjust delegation strategy

---

## 🆘 Troubleshooting

**Ollama not responding:**
```bash
# Check if Ollama is running
curl http://192.168.1.103:11434/api/tags

# If not, SSH to VM and restart
ssh ollama@192.168.1.103
sudo systemctl restart ollama
```

**Slow responses:**
- Check network connection (should be 10 Gig Ethernet)
- Verify VM has 24 GB RAM allocated
- Monitor VM CPU usage

**Quality issues:**
- Try different model (codellama vs deepseek-coder-v2)
- Provide more context in prompt
- Use Claude Code for final review

---

EOF

# Display the guide
cat /home/boatiq/OLLAMA_USAGE_GUIDE.md
```

---

### Phase 7: Testing & Verification (1 hour)
**Goal:** Verify everything works

**Time: 18:30 - 19:30 (1 hour)**

#### Test 1: Network Performance
```bash
# On Ubuntu VM
iperf3 -s

# On laptop (new terminal)
iperf3 -c 192.168.1.103

# Expected: 8-9 Gbps (10 Gig Ethernet)
```

#### Test 2: Ollama Response Time
```bash
# Test each model
time ./ollama-assist.sh code "Write hello world in Python"
# Expected: 5-15 seconds

time ./ollama-assist.sh review "print('hello')"
# Expected: 10-20 seconds

time ./ollama-assist.sh docs "print('hello')"
# Expected: 10-20 seconds
```

#### Test 3: Full Workflow Test
```bash
# Generate a complete feature with Ollama
./ollama-assist.sh code "Create a Python class for managing boat GPS coordinates with methods to:
- Store latitude/longitude
- Calculate distance between two points
- Validate coordinate format
- Convert to/from different formats (decimal degrees, DMS)"

# Expected: Working Python code in 30-60 seconds
```

#### Test 4: Backup Verification
```bash
# SSH to TrueNAS
ssh root@192.168.1.102

# List snapshots
zfs list -t snapshot | grep cheeta

# Expected: At least one snapshot created in Phase 5
```

---

## ⏰ TIMELINE SUMMARY

| Time | Phase | Duration | Status |
|------|-------|----------|--------|
| 09:00-12:00 | Phase 1: Ubuntu VM Setup | 3 hours | ⏳ |
| 12:00-13:30 | Phase 2: Ollama Installation | 1.5 hours | ⏳ |
| 13:30-15:30 | Phase 3: Integration Scripts | 2 hours | ⏳ |
| 15:30-16:00 | Phase 4: Directory Structure | 30 min | ⏳ |
| 16:00-17:00 | Phase 5: Basic Backups | 1 hour | ⏳ |
| 17:00-18:30 | Phase 6: New Workflow | 1.5 hours | ⏳ |
| 18:30-19:30 | Phase 7: Testing | 1 hour | ⏳ |

**Total: 10.5 hours (can finish by evening)**

---

## 💰 EXPECTED RESULTS (END OF DAY)

**Before (Today Morning):**
- Claude Code costs: $800/month
- All tasks use Claude Code
- Slow, expensive development

**After (Tonight):**
- Ollama running on TrueNAS (FREE)
- 95% of tasks use Ollama
- Claude Code for orchestration only
- **Projected costs: $10-15/month**
- **Savings: $785-790/month (98%!)**

---

## 🚨 CRITICAL SUCCESS FACTORS

1. ✅ Ubuntu VM with 24 GB RAM (approved)
2. ✅ 10 Gig Ethernet (fast responses)
3. ✅ 3 Ollama models installed (code, review, docs)
4. ✅ Integration scripts working
5. ✅ Shift mindset: Ollama first, Claude Code for oversight only

---

## 📝 NEXT STEPS TOMORROW

1. **Monitor Costs:**
   - Track Claude Code usage (should be minimal)
   - Verify Ollama handling 95%+ of tasks

2. **Optimize:**
   - Fine-tune prompts for better Ollama output
   - Add more automation scripts
   - Document common patterns

3. **Backup Automation:**
   - Add laptop backup script (deferred to tomorrow)
   - Test backup restoration
   - Set up monitoring

4. **File Migration:**
   - Move d3kOS files to Cheeta (when ready)
   - Organize other projects
   - Clean up laptop (when verified)

---

## ✅ COMPLETION CHECKLIST

**By End of Today:**
- [ ] Ubuntu VM created on TrueNAS (24 GB RAM, 8 vCPUs, 100 GB disk)
- [ ] Ubuntu 22.04 installed and configured
- [ ] Ollama installed and running
- [ ] 3 models pulled (deepseek-coder-v2, qwen2.5-coder, codellama)
- [ ] ollama-assist.sh script created and tested
- [ ] ollama-batch.sh script created and tested
- [ ] ollama_delegate.py script created and tested
- [ ] Directory structure created on Cheeta
- [ ] ZFS snapshot script created and scheduled
- [ ] Usage guide written (OLLAMA_USAGE_GUIDE.md)
- [ ] All tests passed (network, response time, workflow)
- [ ] Ready to use Ollama instead of Claude Code

**Success Metric:**
- ✅ Can generate code using Ollama in under 30 seconds
- ✅ Can use Ollama for routine development tasks
- ✅ Claude Code usage reduced by 95%+
- ✅ Projected monthly costs under $20

---

**LET'S START NOW!**

**First command to run:**
```bash
# Open TrueNAS web UI
http://192.168.1.102
# Login: root / damcor53$
# Navigate to: Virtual Machines → Add
```

**I'm ready to guide you through each step. Let's deploy Ollama TODAY and stop the cost bleeding!** 🚀
