# Claude Code ↔ Ollama Integration Guide
**Date:** 2026-03-02
**Architecture:** 3-System Network with Claude Code Orchestration

---

## 🎯 Goal

Enable Claude Code on **laptop** and **workstation** to seamlessly delegate tasks to local Ollama instances, reducing costs from $800/month to under $20/month.

---

## 🏗️ Network Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLAUDE CODE (Orchestrator)                    │
│                 Runs on: Laptop OR Workstation                   │
│                   Cost: $5-10/month (5% usage)                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                    Delegates 95% of tasks to ↓
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌────────────────┐    ┌────────────────┐
│    LAPTOP     │    │  WORKSTATION   │    │   TRUENAS VM   │
│   Ollama      │    │  Ollama (GPU)  │    │  Ollama (CPU)  │
├───────────────┤    ├────────────────┤    ├────────────────┤
│ CPU-only      │    │ RTX 3060 Ti    │    │ CPU-only       │
│ 8-16 GB RAM   │    │ 8GB VRAM       │    │ 24 GB RAM      │
│               │    │ 32 GB RAM      │    │                │
├───────────────┤    ├────────────────┤    ├────────────────┤
│ Response:     │    │ Response:      │    │ Response:      │
│ 30-90 sec     │    │ 3-15 sec ⚡    │    │ 20-120 sec     │
├───────────────┤    ├────────────────┤    ├────────────────┤
│ Models:       │    │ Models:        │    │ Models:        │
│ 7B-8B only    │    │ 13B-16B (GPU)  │    │ 7B-8B only     │
├───────────────┤    ├────────────────┤    ├────────────────┤
│ Use:          │    │ Use:           │    │ Use:           │
│ Mobile work   │    │ PRIMARY DESK   │    │ BACKUP 24/7    │
└───────────────┘    └────────────────┘    └────────────────┘
localhost:11434      192.168.1.XXX:11434   192.168.1.103:11434
```

---

## 📊 Smart Routing Logic

**Priority Order (Fastest → Slowest):**

1. **Try Local Ollama First** (0ms network latency)
   - If on laptop → use laptop Ollama
   - If on workstation → use workstation Ollama (GPU)

2. **Try Workstation GPU Second** (LAN latency ~1ms)
   - If workstation is on and available
   - Best performance (3-15 seconds)

3. **Fallback to TrueNAS Third** (Always available)
   - If local and workstation unavailable
   - Slower but reliable (20-120 seconds)

4. **Escalate to Claude Code** (Complex tasks only)
   - If all Ollama instances fail
   - Or task too complex for Ollama
   - Uses paid API ($5-10/month total)

---

## 🔧 Installation Plan - 3 Systems

### System 1: Laptop Ollama (Mobile Development)

**Hardware:** CPU-only, 8-16 GB RAM
**Models:** Small, CPU-optimized (7B-8B)
**Use Case:** Working on the go, when away from desk

```bash
# Install Ollama on Ubuntu/WSL
curl -fsSL https://ollama.com/install.sh | sh

# Pull small CPU-optimized models
ollama pull qwen2.5-coder:7b         # Code + docs (7 GB)
ollama pull llama3.1:8b              # General (8 GB)

# Configure for local + network access
sudo systemctl edit ollama
# Add:
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"

sudo systemctl restart ollama

# Test
ollama run qwen2.5-coder:7b "Write hello world in Python"
# Expected: 30-60 seconds
```

**Total Storage:** ~15 GB
**Response Time:** 30-90 seconds (acceptable for mobile)

---

### System 2: Workstation Ollama (Primary Desk Work)

**Hardware:** RTX 3060 Ti (8GB VRAM), 32 GB RAM
**Models:** Large, GPU-accelerated (13B-16B)
**Use Case:** PRIMARY for interactive development at desk

```powershell
# Download Ollama for Windows
# Visit: https://ollama.com/download/windows
# Run: OllamaSetup.exe

# Pull GPU-accelerated models
ollama pull deepseek-coder-v2:16b    # Code (16 GB) - PRIMARY
ollama pull qwen2.5-coder:14b        # Docs (14 GB)
ollama pull codellama:13b            # Review (13 GB)
ollama pull llama3.1:8b              # General (8 GB)

# Configure for network access
# Edit: C:\Users\<username>\.ollama\config.json
{
  "host": "0.0.0.0:11434"
}

# Restart Ollama service
Restart-Service Ollama

# Test GPU acceleration
ollama run deepseek-coder-v2:16b "Write hello world in Python"
# Expected: 5-10 seconds (GPU-accelerated)

# Verify GPU usage in Task Manager → Performance → GPU
```

**Total Storage:** ~60 GB
**Response Time:** 3-15 seconds (FAST!)

---

### System 3: TrueNAS Ollama (24/7 Backup)

**Hardware:** CPU-only, 24 GB RAM
**Models:** Medium, CPU-optimized (7B-8B)
**Use Case:** Always-on backup, batch processing

```bash
# SSH to TrueNAS VM
ssh ollama@192.168.1.103

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull CPU-optimized models
ollama pull qwen2.5-coder:7b         # Code + docs
ollama pull deepseek-coder:6.7b      # Code generation
ollama pull llama3.1:8b              # General

# Configure for network access
sudo systemctl edit ollama
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"

sudo systemctl restart ollama

# Test
ollama run qwen2.5-coder:7b "Write hello world in Python"
# Expected: 20-40 seconds
```

**Total Storage:** ~30 GB
**Response Time:** 20-120 seconds (reliable backup)

---

## 🐍 Python Integration Library

### Create: `/home/boatiq/scripts/claude_ollama_bridge.py`

```python
#!/usr/bin/env python3
"""
Claude Code ↔ Ollama Integration Bridge

Allows Claude Code to automatically delegate tasks to the best available
Ollama instance (local → workstation → TrueNAS → Claude API)

Usage:
    from claude_ollama_bridge import OllamaBridge

    bridge = OllamaBridge()
    result = bridge.generate_code("Write a function to parse GPS coordinates")
    print(result)
"""

import requests
import socket
import time
import json
import sys
from typing import Dict, List, Optional, Tuple

class OllamaBridge:
    """Smart routing bridge between Claude Code and Ollama instances"""

    def __init__(self):
        """Initialize with known Ollama endpoints"""

        # Get laptop hostname/IP
        self.laptop_ip = self._get_local_ip()

        # Define all Ollama endpoints (priority order)
        self.endpoints = [
            {
                "name": "Local (This Machine)",
                "url": "http://localhost:11434",
                "priority": 1,
                "speed": "fast",
                "models": {
                    "code": "qwen2.5-coder:7b",      # Laptop: smaller models
                    "docs": "qwen2.5-coder:7b",
                    "review": "qwen2.5-coder:7b",
                    "general": "llama3.1:8b"
                }
            },
            {
                "name": "Workstation GPU",
                "url": "http://192.168.1.XXX:11434",  # UPDATE with actual workstation IP
                "priority": 2,
                "speed": "fastest",
                "models": {
                    "code": "deepseek-coder-v2:16b",  # Workstation: larger GPU models
                    "docs": "qwen2.5-coder:14b",
                    "review": "codellama:13b",
                    "general": "llama3.1:8b"
                }
            },
            {
                "name": "TrueNAS Backup",
                "url": "http://192.168.1.103:11434",
                "priority": 3,
                "speed": "medium",
                "models": {
                    "code": "qwen2.5-coder:7b",       # TrueNAS: CPU-optimized
                    "docs": "qwen2.5-coder:7b",
                    "review": "deepseek-coder:6.7b",
                    "general": "llama3.1:8b"
                }
            }
        ]

        # Cache available endpoints (checked at startup)
        self.available_endpoints = []
        self._check_availability()

    def _get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def _check_availability(self):
        """Check which Ollama endpoints are available"""
        print("🔍 Checking Ollama availability...")

        for endpoint in self.endpoints:
            try:
                response = requests.get(
                    f"{endpoint['url']}/api/tags",
                    timeout=2
                )
                if response.status_code == 200:
                    models = response.json().get('models', [])
                    endpoint['available_models'] = [m['name'] for m in models]
                    self.available_endpoints.append(endpoint)
                    print(f"  ✅ {endpoint['name']}: {len(models)} models available")
            except:
                print(f"  ❌ {endpoint['name']}: Not available")

        if not self.available_endpoints:
            print("  ⚠️  WARNING: No Ollama instances available!")
            print("  📌 Will use Claude Code API for all tasks (expensive!)")

        print()

    def _select_endpoint(self, task_type: str = "code") -> Optional[Dict]:
        """Select best available endpoint for task type"""

        # If on workstation, prefer local GPU
        if self.laptop_ip.startswith("192.168.1."):
            # Check if we ARE the workstation (running locally on GPU machine)
            for endpoint in self.available_endpoints:
                if endpoint['name'] == "Local (This Machine)":
                    # Check if local has GPU models (larger models = workstation)
                    if "deepseek-coder-v2:16b" in endpoint.get('available_models', []):
                        print(f"🚀 Using Local GPU (workstation)")
                        return endpoint

        # Otherwise, use priority order
        for endpoint in self.available_endpoints:
            required_model = endpoint['models'].get(task_type)
            if required_model in endpoint.get('available_models', []):
                print(f"🤖 Using {endpoint['name']} ({endpoint['speed']})")
                return endpoint

        # No suitable endpoint found
        return None

    def _call_ollama(
        self,
        endpoint: Dict,
        model: str,
        prompt: str,
        system: str = ""
    ) -> Dict:
        """Call Ollama API with timing"""

        start_time = time.time()

        try:
            full_prompt = f"{system}\n\n{prompt}" if system else prompt

            response = requests.post(
                f"{endpoint['url']}/api/generate",
                json={
                    "model": model,
                    "prompt": full_prompt,
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
                    "endpoint": endpoint['name'],
                    "elapsed_time": elapsed_time,
                    "speed": endpoint['speed']
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "endpoint": endpoint['name'],
                    "elapsed_time": elapsed_time
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "endpoint": endpoint['name'],
                "elapsed_time": time.time() - start_time
            }

    def generate_code(self, task: str, language: str = "python", context: str = "") -> Dict:
        """Generate code using best available Ollama"""

        system_prompt = f"""You are an expert {language} programmer.
Generate clean, production-ready code with:
- Proper error handling
- Type hints (if applicable)
- Docstrings/comments
- Input validation

Task: {task}
Context: {context}
"""

        endpoint = self._select_endpoint("code")

        if not endpoint:
            return {
                "success": False,
                "error": "No Ollama instances available. Use Claude Code API instead.",
                "suggestion": "Start Ollama on laptop, workstation, or TrueNAS"
            }

        model = endpoint['models']['code']
        return self._call_ollama(endpoint, model, task, system_prompt)

    def review_code(self, code: str, requirements: str = "") -> Dict:
        """Review code using best available Ollama"""

        system_prompt = f"""You are a senior code reviewer.
Analyze the code for:
- Bugs and logic errors
- Security vulnerabilities
- Performance issues
- Best practices violations

Requirements: {requirements}

Provide:
1. Code quality score (0-10)
2. Issues found
3. Specific suggestions for improvement
"""

        endpoint = self._select_endpoint("review")

        if not endpoint:
            return {"success": False, "error": "No Ollama available"}

        model = endpoint['models']['review']
        prompt = f"Review this code:\n\n{code}"

        return self._call_ollama(endpoint, model, prompt, system_prompt)

    def generate_docs(self, code: str, format: str = "markdown") -> Dict:
        """Generate documentation using best available Ollama"""

        system_prompt = f"""You are a technical writer.
Generate comprehensive {format} documentation including:
- Overview/purpose
- Parameters and return values
- Usage examples
- Error handling
- Dependencies
"""

        endpoint = self._select_endpoint("docs")

        if not endpoint:
            return {"success": False, "error": "No Ollama available"}

        model = endpoint['models']['docs']
        prompt = f"Generate documentation for:\n\n{code}"

        return self._call_ollama(endpoint, model, prompt, system_prompt)

    def explain_code(self, code: str) -> Dict:
        """Explain code in plain language"""

        system_prompt = "You are a patient teacher. Explain technical concepts clearly with examples."

        endpoint = self._select_endpoint("general")

        if not endpoint:
            return {"success": False, "error": "No Ollama available"}

        model = endpoint['models']['general']
        prompt = f"Explain what this code does:\n\n{code}"

        return self._call_ollama(endpoint, model, prompt, system_prompt)

    def get_status(self) -> Dict:
        """Get status of all Ollama endpoints"""

        return {
            "total_endpoints": len(self.endpoints),
            "available_endpoints": len(self.available_endpoints),
            "endpoints": [
                {
                    "name": e['name'],
                    "url": e['url'],
                    "speed": e['speed'],
                    "available": e in self.available_endpoints,
                    "models": e.get('available_models', [])
                }
                for e in self.endpoints
            ]
        }

# CLI interface for testing
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: claude_ollama_bridge.py {code|review|docs|explain|status} \"<prompt>\"")
        sys.exit(1)

    command = sys.argv[1]
    bridge = OllamaBridge()

    if command == "status":
        status = bridge.get_status()
        print(json.dumps(status, indent=2))
        sys.exit(0)

    prompt = " ".join(sys.argv[2:])

    if command == "code":
        result = bridge.generate_code(prompt)
    elif command == "review":
        result = bridge.review_code(prompt)
    elif command == "docs":
        result = bridge.generate_docs(prompt)
    elif command == "explain":
        result = bridge.explain_code(prompt)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

    if result["success"]:
        print(f"\n✅ Response from {result['endpoint']} using {result['model']}")
        print(f"⏱️  Time: {result['elapsed_time']:.1f}s ({result['speed']})")
        print(f"\n{result['response']}")
    else:
        print(f"\n❌ Error: {result['error']}")
        sys.exit(1)
```

---

## 🚀 Usage from Claude Code

### Example 1: Simple Code Generation

```python
from claude_ollama_bridge import OllamaBridge

# Initialize bridge (auto-detects best Ollama)
bridge = OllamaBridge()

# Generate code
result = bridge.generate_code(
    task="Create a function to validate email addresses",
    language="python"
)

if result["success"]:
    print(result["response"])  # Generated code
    print(f"Time: {result['elapsed_time']:.1f}s")  # 3-15s if workstation, 20-60s if TrueNAS
```

### Example 2: Code Review

```python
code = """
def calculate_total(items):
    total = 0
    for item in items:
        total += item
    return total
"""

result = bridge.review_code(code)
print(result["response"])  # Review feedback
```

### Example 3: Check Status

```python
status = bridge.get_status()
print(f"Available: {status['available_endpoints']}/{status['total_endpoints']}")
for endpoint in status['endpoints']:
    if endpoint['available']:
        print(f"✅ {endpoint['name']}: {len(endpoint['models'])} models")
```

---

## 🔄 Automatic Fallback Chain

**Scenario: Laptop user needs code generated**

```
1. Try local Ollama (laptop CPU)
   ↓ Available? → Use it (30-60s)
   ↓ Not available ↓

2. Try workstation Ollama (GPU)
   ↓ Available? → Use it (5-10s) ⚡ BEST!
   ↓ Not available ↓

3. Try TrueNAS Ollama (CPU)
   ↓ Available? → Use it (20-40s)
   ↓ Not available ↓

4. Escalate to Claude Code API
   → Use paid API ($$$)
   → Notify user: "All Ollama instances down"
```

---

## 📋 Deployment Checklist

### Step 1: Install Ollama Everywhere (2 hours)

- [ ] **Laptop:** Install Ollama, pull 2 small models (qwen2.5-coder:7b, llama3.1:8b)
- [ ] **Workstation:** Install Ollama, pull 4 GPU models (deepseek-coder-v2:16b, qwen2.5-coder:14b, codellama:13b, llama3.1:8b)
- [ ] **TrueNAS:** Install Ollama, pull 3 CPU models (qwen2.5-coder:7b, deepseek-coder:6.7b, llama3.1:8b)

### Step 2: Configure Network Access (15 min)

- [ ] **Laptop:** Edit Ollama config, set `OLLAMA_HOST=0.0.0.0:11434`
- [ ] **Workstation:** Edit Ollama config, set host to `0.0.0.0:11434`
- [ ] **TrueNAS:** Already configured in deployment script

### Step 3: Create Integration Scripts (30 min)

- [ ] Create `/home/boatiq/scripts/claude_ollama_bridge.py`
- [ ] Update workstation IP in bridge script (line 38)
- [ ] Make executable: `chmod +x claude_ollama_bridge.py`
- [ ] Test from laptop: `python3 claude_ollama_bridge.py status`

### Step 4: Test Integration (30 min)

- [ ] Test local Ollama: `python3 claude_ollama_bridge.py code "Write hello world"`
- [ ] Test workstation routing (if available)
- [ ] Test TrueNAS fallback (disconnect workstation)
- [ ] Verify automatic routing works

### Step 5: Update Claude Code Workflow (30 min)

- [ ] Import bridge in Claude Code sessions
- [ ] Use bridge for routine tasks (code, docs, review)
- [ ] Reserve Claude Code API for orchestration only
- [ ] Monitor costs (should drop to $5-10/month)

---

## 💰 Cost Savings Breakdown

### Current (February - All Claude Code)

| Task Type | Frequency | Cost per Task | Monthly Cost |
|-----------|-----------|---------------|--------------|
| Code generation | 200 tasks | $2.00 | $400 |
| Documentation | 100 tasks | $1.50 | $150 |
| Code review | 100 tasks | $2.00 | $200 |
| Bug fixes | 50 tasks | $1.00 | $50 |
| **Total** | **450 tasks** | - | **$800** |

### After Integration (March - 95% Ollama)

| Task Type | Frequency | Ollama (FREE) | Claude Code | Monthly Cost |
|-----------|-----------|---------------|-------------|--------------|
| Code generation | 200 tasks | 195 (98%) | 5 (2%) | $10 |
| Documentation | 100 tasks | 100 (100%) | 0 (0%) | $0 |
| Code review | 100 tasks | 100 (100%) | 0 (0%) | $0 |
| Bug fixes | 50 tasks | 50 (100%) | 0 (0%) | $0 |
| Planning/orchestration | - | - | - | $5-10 |
| **Total** | **450 tasks** | **445 (99%)** | **5 (1%)** | **$15-20** |

**Savings: $780-785/month (98% reduction!)**

---

## 🎯 Updated Timeline (3 Systems)

**Total Time: 4 hours**

| Time | Task | System |
|------|------|--------|
| **30 min** | Install Ollama + 2 models | Laptop |
| **30 min** | Install Ollama + 4 models | Workstation |
| **1.5 hours** | Create VM + install Ollama + 3 models | TrueNAS |
| **30 min** | Create integration scripts | Laptop |
| **30 min** | Test all systems | All |
| **30 min** | Update Claude Code workflow | Laptop |

**By 1-2 PM: All systems deployed, ready to save $780/month!**

---

## ✅ Success Criteria

**After deployment, you should be able to:**

1. ✅ Run code generation from laptop (uses best available Ollama)
2. ✅ Run code generation from workstation (uses local GPU, fastest)
3. ✅ Have backup when workstation off (TrueNAS 24/7)
4. ✅ Automatic routing (no manual selection needed)
5. ✅ Claude Code costs under $20/month (98% reduction)
6. ✅ Response times: 3-120 seconds (vs 10-20 seconds Claude Code)
7. ✅ No manual approvals for routine tasks (auto-delegated to Ollama)

---

## 🆘 Troubleshooting

**Issue: "No Ollama instances available"**
```bash
# Check each system
curl http://localhost:11434/api/tags           # Laptop
curl http://192.168.1.XXX:11434/api/tags       # Workstation
curl http://192.168.1.103:11434/api/tags       # TrueNAS

# Restart Ollama if needed
sudo systemctl restart ollama  # Linux/TrueNAS
Restart-Service Ollama         # Windows workstation
```

**Issue: "Slow responses from laptop Ollama"**
- Expected: Laptop CPU is slower (30-90s)
- Solution: Use workstation when at desk (3-15s)
- Or: Wait for TrueNAS routing (20-120s)

**Issue: "Workstation not routing"**
- Check firewall allows port 11434
- Verify workstation IP in bridge script
- Test: `curl http://WORKSTATION_IP:11434/api/tags`

---

## 🚀 READY TO DEPLOY

**Next Steps:**

1. **Confirm workstation IP address** - Need for integration script
2. **Choose deployment approach:**
   - **Full (Recommended):** All 3 systems (4 hours)
   - **Workstation + TrueNAS:** Skip laptop (3.5 hours)
   - **Essential:** TrueNAS only (1.5 hours)

3. **I'll guide you step-by-step** through:
   - Installing Ollama on each system
   - Pulling optimal models
   - Creating integration scripts
   - Testing the full workflow

**Ready to start? What's the workstation IP address?**
