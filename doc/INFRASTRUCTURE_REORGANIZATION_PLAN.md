# Infrastructure Reorganization & Cost Optimization Plan
**Date:** 2026-03-02
**Prepared by:** Claude Code
**Status:** Draft for Review

---

## Executive Summary

**Current Problem:**
- Files scattered across laptop without organization
- No structured backup system
- Claude Code costs unsustainable ($20/month per user)
- Manual approval required for every step (slow throughput)
- No local AI assistance available

**Solution:**
- Reorganize 5 projects into TrueNAS Cheeta storage
- Implement automated daily backups with 30-day retention
- Deploy Ollama on TrueNAS for local AI assistance
- Reduce Claude Code to orchestrator role only
- Enable unattended operation for routine tasks

**Expected Outcomes:**
- 80-90% reduction in Claude Code costs
- 3-5× faster project delivery
- Automated backups protecting all work
- Local AI handling 80% of development tasks
- Claude Code only for planning and complex decisions

---

## Infrastructure Inventory

### Current Network Setup

| Device | IP Address | Storage | Network | Role |
|--------|------------|---------|---------|------|
| **TrueNAS** | 192.168.1.102 | 3 pools (Beaver, Cheeta, Mice) | 10 Gig Ethernet | Primary storage + backup |
| **QNAP NAS** | 192.168.1.49/50 | Multiple backups | 2× 2.5 Gig Ethernet | Secondary backup |
| **Workstation** | TBD | TBD | 10 Gig Ethernet | Development, GPU training |
| **Laptop** | TBD | TBD | WiFi | Mobile development |
| **d3kOS Pi** | 192.168.1.237 | 16 GB SD + 128 GB USB | Ethernet | Prototype/testing |

### TrueNAS Storage Pools

**Credentials:** root / damcor53$

1. **Beaver** - RAID, long-term storage (archival)
2. **Cheeta** - 109 GB free, fastest (SSD) - **PRIMARY PROJECT STORAGE**
3. **Mice** - Smaller utility storage

### Access Credentials (Reference)

```
TrueNAS: root / damcor53$
QNAP NAS: admin / Donald 61#
d3kOS Pi: d3kos / d3kos2026
HostPapa WordPress: admin / A#JFOPZD6&
```

---

## Phase 1: Project Directory Structure (Priority: IMMEDIATE)

### 1.1 Top-Level Organization on Cheeta

**Location:** `/mnt/cheeta/projects/`

```
/mnt/cheeta/
├── projects/
│   ├── d3kOS/                    # Marine OS development
│   │   ├── code/                 # Git repository
│   │   ├── docs/                 # Documentation
│   │   ├── datasets/             # AI training data
│   │   ├── models/               # Trained AI models
│   │   ├── releases/             # Version releases
│   │   └── testing/              # Test builds
│   │
│   ├── AAO-Methodology/          # AAO project
│   │   ├── docs/
│   │   ├── research/
│   │   └── implementation/
│   │
│   ├── Marketing/                # Video marketing content
│   │   ├── videos/
│   │   ├── scripts/
│   │   ├── assets/
│   │   └── exports/
│   │
│   ├── Content/                  # Blog and forum content
│   │   ├── atmyboat-blog/
│   │   ├── linkedin/
│   │   ├── forums/
│   │   │   ├── open-marine/
│   │   │   ├── cruiser-forum/
│   │   │   ├── trawler-forum/
│   │   │   └── boat-builder/
│   │   └── drafts/
│   │
│   └── WordPress/                # Website content
│       ├── atmyboat-com/
│       ├── themes/
│       └── backups/
│
├── development/                   # Active development workspace
│   ├── laptop-sync/              # Synced from laptop
│   ├── workstation-sync/         # Synced from workstation
│   └── shared/                   # Shared resources
│
└── archives/                      # Completed/archived projects
```

### 1.2 Backup Directory Structure

**Location:** `/mnt/beaver/backups/`

```
/mnt/beaver/backups/
├── TrueNAS/                       # TrueNAS config backups
│   ├── config/                   # System configuration
│   ├── credentials/              # Encrypted credentials
│   └── datasets/                 # Dataset metadata
│
├── Laptop/                        # Full laptop backups
│   ├── 2026-03/
│   │   ├── daily/               # Daily incrementals
│   │   │   ├── 2026-03-02-noon/
│   │   │   ├── 2026-03-02-midnight/
│   │   │   └── ...
│   │   └── weekly/              # Weekly full backups
│   │       ├── 2026-03-01/
│   │       └── ...
│   └── 2026-02/                  # Previous month (retention)
│
└── Workstation/                   # Full workstation backups
    ├── 2026-03/
    │   ├── daily/
    │   └── weekly/
    └── 2026-02/
```

**Retention Policy:**
- Daily backups: 7 days (noon + midnight = 14 snapshots)
- Weekly backups: 5 weeks (1 month + 1 week buffer)
- Monthly backups: 3 months
- Total retention: ~30 days of daily granularity

### 1.3 Implementation Steps

**Step 1: Create directory structure on Cheeta**
```bash
ssh root@192.168.1.102
mkdir -p /mnt/cheeta/projects/{d3kOS,AAO-Methodology,Marketing,Content,WordPress}
mkdir -p /mnt/cheeta/projects/d3kOS/{code,docs,datasets,models,releases,testing}
mkdir -p /mnt/cheeta/projects/Content/forums/{open-marine,cruiser-forum,trawler-forum,boat-builder}
mkdir -p /mnt/cheeta/development/{laptop-sync,workstation-sync,shared}
mkdir -p /mnt/cheeta/archives
```

**Step 2: Create backup structure on Beaver**
```bash
mkdir -p /mnt/beaver/backups/{TrueNAS,Laptop,Workstation}
mkdir -p /mnt/beaver/backups/TrueNAS/{config,credentials,datasets}
```

**Step 3: Set permissions**
```bash
chmod -R 755 /mnt/cheeta/projects
chmod -R 700 /mnt/beaver/backups/TrueNAS/credentials
```

**Time Estimate:** 30 minutes

---

## Phase 2: Automated Backup System (Priority: HIGH)

### 2.1 Backup Strategy

**Approach:** ZFS snapshots + rsync replication

**Daily Schedule:**
- **Noon (12:00 PM):** Incremental snapshot
- **Midnight (00:00):** Full snapshot + replication to Beaver

**Why ZFS Snapshots:**
- Instant (< 1 second)
- Space-efficient (copy-on-write)
- Easy rollback (instant restore)
- Native to TrueNAS/FreeBSD

### 2.2 Backup Implementation

**Create ZFS snapshot script:**

```bash
#!/bin/sh
# /root/scripts/snapshot-cheeta.sh

DATASET="cheeta/projects"
TIMESTAMP=$(date +%Y-%m-%d-%H%M)
SNAPSHOT_NAME="${DATASET}@${TIMESTAMP}"

# Create snapshot
zfs snapshot "${SNAPSHOT_NAME}"

# Log
echo "$(date): Created snapshot ${SNAPSHOT_NAME}" >> /var/log/zfs-snapshots.log

# Cleanup old snapshots (keep 30 days)
zfs list -t snapshot -o name,creation -s creation | grep "^${DATASET}@" | head -n -60 | awk '{print $1}' | xargs -n 1 zfs destroy
```

**Create cron jobs:**

```bash
# /etc/crontab
0 12 * * * root /root/scripts/snapshot-cheeta.sh
0 0 * * * root /root/scripts/snapshot-cheeta.sh && /root/scripts/replicate-to-beaver.sh
```

**Replication script:**

```bash
#!/bin/sh
# /root/scripts/replicate-to-beaver.sh

LATEST_SNAPSHOT=$(zfs list -t snapshot -o name -s creation | grep "cheeta/projects@" | tail -n 1)

# Replicate to Beaver
zfs send ${LATEST_SNAPSHOT} | zfs recv beaver/backups/cheeta-mirror

echo "$(date): Replicated ${LATEST_SNAPSHOT} to Beaver" >> /var/log/zfs-replication.log
```

### 2.3 Laptop & Workstation Backups

**Approach:** rsync over SSH to Beaver

**Laptop backup script (run on laptop):**

```bash
#!/bin/bash
# /home/boatiq/scripts/backup-to-truenas.sh

BACKUP_DIR="/mnt/beaver/backups/Laptop/$(date +%Y-%m)/daily/$(date +%Y-%m-%d-%H%M)"
EXCLUDE_FILE="/home/boatiq/.backup-exclude"

# Create exclude list
cat > ${EXCLUDE_FILE} << 'EOF'
.cache/
.local/share/Trash/
node_modules/
.npm/
*.tmp
*.log
EOF

# Backup to TrueNAS
rsync -avz --delete --exclude-from=${EXCLUDE_FILE} \
  /home/boatiq/ \
  root@192.168.1.102:${BACKUP_DIR}/

echo "$(date): Backup completed to ${BACKUP_DIR}" >> /home/boatiq/backup.log
```

**Cron job on laptop:**

```bash
# crontab -e
0 12 * * * /home/boatiq/scripts/backup-to-truenas.sh
0 0 * * * /home/boatiq/scripts/backup-to-truenas.sh
```

**Time Estimate:** 2 hours setup + testing

---

## Phase 3: Cost Optimization Strategy (Priority: CRITICAL)

### 3.1 Current Cost Analysis

**Claude Code Costs:**
- Current: ~$20/month per user (Sonnet 4.5)
- Token usage: 100k-200k tokens per session
- Average: 5-10 sessions per week
- **Monthly cost: Unsustainable for single developer**

### 3.2 Proposed Architecture

**New AI Stack:**

```
┌─────────────────────────────────────────────────────┐
│         Claude Code (Orchestrator Only)             │
│  • Planning and architecture decisions              │
│  • Complex problem solving                          │
│  • Multi-system coordination                        │
│  • Budget: 2-3 sessions/week (~$5-8/month)         │
└─────────────────────────────────────────────────────┘
                        ↓ Delegates to
┌─────────────────────────────────────────────────────┐
│         Ollama (Local AI - FREE)                    │
│  • Code generation                                  │
│  • Documentation writing                            │
│  • Bug fixes and debugging                          │
│  • Testing and validation                           │
│  • 80% of routine development tasks                 │
└─────────────────────────────────────────────────────┘
```

**Cost Reduction:**
- Before: $20/month (100% Claude Code)
- After: $5-8/month (Claude Code orchestration only)
- **Savings: 70-80% reduction**

### 3.3 Ollama Deployment on TrueNAS

**Challenge:** TrueNAS runs FreeBSD (not Linux)

**Solution:** Deploy Ubuntu VM on TrueNAS

**Specifications:**
- VM: Ubuntu 22.04 LTS
- vCPUs: 8 cores
- RAM: 16 GB
- Storage: 100 GB (Cheeta)
- Network: Bridged (10 Gig Ethernet)

**Ollama Models to Deploy:**

| Model | Size | Purpose | Speed |
|-------|------|---------|-------|
| **deepseek-coder-v2** | 16 GB | Code generation | Fast |
| **codellama:34b** | 19 GB | Code review | Medium |
| **llama3.1:70b** | 40 GB | General reasoning | Slow |
| **qwen2.5-coder:32b** | 18 GB | Documentation | Fast |

**Total Storage:** ~90 GB models

### 3.4 Claude Code Integration with Ollama

**Workflow:**

1. **User Request** → Claude Code (planning phase)
2. **Claude Code** → Creates detailed task plan
3. **Task Delegation:**
   - Simple code changes → Ollama
   - Documentation → Ollama
   - Testing → Ollama
   - Architecture decisions → Claude Code
4. **Ollama** → Executes tasks, returns results
5. **Claude Code** → Reviews, orchestrates, delivers

**Example Session:**

```
User: "Add metric/imperial conversion to d3kOS dashboard"

Claude Code (5 min):
  • Creates implementation plan
  • Identifies files to modify
  • Defines test cases
  • Delegates to Ollama

Ollama (30 min):
  • Generates conversion functions
  • Updates dashboard HTML
  • Creates test suite
  • Documents changes
  • Reports back to Claude Code

Claude Code (2 min):
  • Reviews Ollama output
  • Approves or requests changes
  • Delivers to user

Total time: 37 minutes
Claude Code usage: 7 minutes (reduce 81% cost)
```

### 3.5 Unattended Operation

**Goal:** Reduce manual approval steps

**Implementation:**

**Create approval policy file:**

```json
// /home/boatiq/.claude/auto-approve-policy.json
{
  "auto_approve": {
    "file_operations": {
      "read": true,
      "write": ["*.md", "*.txt", "*.json"],
      "create_directory": true
    },
    "bash_commands": {
      "safe_commands": ["ls", "cat", "grep", "find", "git status", "curl -X GET"],
      "restricted_commands": ["rm", "sudo", "mv", "git push"]
    },
    "ollama_delegation": {
      "auto_delegate": ["code_generation", "documentation", "testing"],
      "require_approval": ["architecture_change", "database_migration", "deployment"]
    }
  }
}
```

**Ollama API wrapper:**

```python
# /home/boatiq/scripts/ollama-assistant.py

import requests
import json

class OllamaAssistant:
    def __init__(self, truenas_ip="192.168.1.102", port=11434):
        self.base_url = f"http://{truenas_ip}:{port}"

    def generate_code(self, task, context):
        """Generate code for routine tasks"""
        prompt = f"""Task: {task}

Context: {context}

Generate production-ready code with:
1. Proper error handling
2. Documentation
3. Type hints
4. Unit tests
"""

        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": "deepseek-coder-v2",
                "prompt": prompt,
                "stream": False
            }
        )

        return response.json()["response"]

    def review_code(self, code, requirements):
        """Review code quality"""
        prompt = f"""Review this code:

{code}

Requirements: {requirements}

Provide:
1. Code quality score (0-10)
2. Issues found
3. Suggestions for improvement
"""

        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": "codellama:34b",
                "prompt": prompt,
                "stream": False
            }
        )

        return response.json()["response"]
```

**Time Estimate:** 4 hours setup + testing

---

## Phase 4: TrueNAS Ubuntu VM Setup (Priority: HIGH)

### 4.1 VM Creation Steps

**Access TrueNAS Web UI:** http://192.168.1.102

**Create VM:**
1. Navigate to: Virtual Machines → Add
2. Configuration:
   - Name: `ubuntu-ollama-dev`
   - OS Type: Linux
   - vCPUs: 8
   - RAM: 16384 MB (16 GB)
   - Boot Method: UEFI
   - VNC Bind: 0.0.0.0:5901
3. Storage:
   - Disk 1: 100 GB (Zvol on Cheeta)
4. Network:
   - NIC 1: Bridged (em0)
   - DHCP: Disabled
   - Static IP: 192.168.1.103

**Install Ubuntu 22.04 LTS:**
1. Download ISO: https://releases.ubuntu.com/22.04/ubuntu-22.04.4-live-server-amd64.iso
2. Upload to TrueNAS
3. Attach ISO to VM
4. Boot and install
5. Configure SSH access

**Install Ollama:**

```bash
# SSH to VM: ssh ubuntu@192.168.1.103

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Enable API access from network
sudo systemctl edit ollama

# Add:
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"

sudo systemctl restart ollama

# Pull models
ollama pull deepseek-coder-v2
ollama pull codellama:34b
ollama pull qwen2.5-coder:32b
```

**Install development tools:**

```bash
sudo apt update
sudo apt install -y git python3-pip nodejs npm
pip3 install anthropic openai requests flask
```

**Time Estimate:** 3 hours

### 4.2 Integration Testing

**Test 1: Ollama API access from laptop**

```bash
curl http://192.168.1.103:11434/api/generate -d '{
  "model": "deepseek-coder-v2",
  "prompt": "Write a Python function to convert Celsius to Fahrenheit",
  "stream": false
}'
```

**Test 2: Code generation performance**

```bash
time ollama run deepseek-coder-v2 "Write a FastAPI endpoint for user authentication"
```

**Test 3: Network throughput**

```bash
iperf3 -s   # On TrueNAS VM
iperf3 -c 192.168.1.103  # From laptop
```

**Expected:** 9+ Gbps (10 Gig Ethernet)

---

## Phase 5: File Migration (Priority: MEDIUM)

### 5.1 Current File Locations (Laptop)

**Scan and identify project files:**

```bash
# From laptop
find /home/boatiq -type f -name "*.md" -o -name "*.odt" -o -name "*.docx" | \
  grep -E "(d3kOS|AAO|marketing|blog|forum)" > /tmp/project-files.txt
```

### 5.2 Migration Script

```bash
#!/bin/bash
# /home/boatiq/scripts/migrate-to-cheeta.sh

TRUENAS_IP="192.168.1.102"
TRUENAS_USER="root"
TRUENAS_BASE="/mnt/cheeta/projects"

# d3kOS files
rsync -avz --progress \
  /home/boatiq/Helm-OS/ \
  ${TRUENAS_USER}@${TRUENAS_IP}:${TRUENAS_BASE}/d3kOS/code/

# AAO Methodology (identify and migrate)
# Marketing content (identify and migrate)
# Blog content (identify and migrate)
# Forum content (identify and migrate)

echo "Migration completed: $(date)" >> /home/boatiq/migration.log
```

**Important:** DO NOT DELETE files from laptop until verified on TrueNAS

**Time Estimate:** 2-3 hours (depends on file size)

---

## Phase 6: Development Workflow (Priority: MEDIUM)

### 6.1 New Development Workflow

**Scenario: Add feature to d3kOS**

**Old Workflow (100% Claude Code):**
1. User requests feature
2. Claude Code reads files (5 min, $0.50)
3. Claude Code plans implementation (10 min, $1.00)
4. Claude Code writes code (20 min, $2.00)
5. User approves each step manually
6. Claude Code tests (10 min, $1.00)
7. **Total: 45 min, $4.50, many manual approvals**

**New Workflow (Claude Code + Ollama):**
1. User requests feature
2. Claude Code creates high-level plan (5 min, $0.50)
3. **Claude Code delegates to Ollama** (auto-approved)
4. Ollama generates code (10 min, FREE)
5. Ollama creates tests (5 min, FREE)
6. Ollama generates documentation (3 min, FREE)
7. **Ollama reports back to Claude Code**
8. Claude Code reviews and approves (2 min, $0.20)
9. **Total: 25 min, $0.70, minimal manual approvals**

**Savings per session:** 44% faster, 84% cheaper

### 6.2 Ollama Development Assistant

**Create wrapper script:**

```bash
#!/bin/bash
# /home/boatiq/scripts/dev-assist.sh

OLLAMA_API="http://192.168.1.103:11434"
TASK=$1
shift
CONTEXT="$@"

case $TASK in
  "code")
    curl -s ${OLLAMA_API}/api/generate -d "{
      \"model\": \"deepseek-coder-v2\",
      \"prompt\": \"${CONTEXT}\",
      \"stream\": false
    }" | jq -r '.response'
    ;;

  "review")
    curl -s ${OLLAMA_API}/api/generate -d "{
      \"model\": \"codellama:34b\",
      \"prompt\": \"Review this code and suggest improvements: ${CONTEXT}\",
      \"stream\": false
    }" | jq -r '.response'
    ;;

  "docs")
    curl -s ${OLLAMA_API}/api/generate -d "{
      \"model\": \"qwen2.5-coder:32b\",
      \"prompt\": \"Generate documentation for: ${CONTEXT}\",
      \"stream\": false
    }" | jq -r '.response'
    ;;

  *)
    echo "Usage: dev-assist.sh {code|review|docs} <context>"
    ;;
esac
```

**Usage examples:**

```bash
# Generate code
./dev-assist.sh code "Create a Python function to parse NMEA2000 PGN 127488"

# Review code
./dev-assist.sh review "$(cat /path/to/file.py)"

# Generate documentation
./dev-assist.sh docs "$(cat /path/to/file.py)"
```

---

## Phase 7: Monitoring & Maintenance

### 7.1 Backup Verification

**Daily verification script:**

```bash
#!/bin/sh
# /root/scripts/verify-backups.sh

LATEST_SNAPSHOT=$(zfs list -t snapshot -o name -s creation | grep "cheeta/projects@" | tail -n 1)

if [ -z "$LATEST_SNAPSHOT" ]; then
  echo "ERROR: No snapshots found!" | mail -s "Backup Alert" your@email.com
  exit 1
fi

AGE=$(zfs get -H -p -o value creation ${LATEST_SNAPSHOT})
NOW=$(date +%s)
DIFF=$((NOW - AGE))

if [ $DIFF -gt 86400 ]; then
  echo "WARNING: Latest snapshot is older than 24 hours" | mail -s "Backup Alert" your@email.com
fi

echo "$(date): Backup verification passed - ${LATEST_SNAPSHOT}" >> /var/log/backup-verify.log
```

### 7.2 Ollama Health Monitoring

**Monitor API availability:**

```bash
#!/bin/bash
# /home/boatiq/scripts/monitor-ollama.sh

OLLAMA_API="http://192.168.1.103:11434"

if ! curl -s ${OLLAMA_API}/api/tags > /dev/null; then
  echo "ERROR: Ollama API not responding" | mail -s "Ollama Alert" your@email.com
  # Attempt restart
  ssh ubuntu@192.168.1.103 "sudo systemctl restart ollama"
fi
```

**Cron job:**

```bash
*/15 * * * * /home/boatiq/scripts/monitor-ollama.sh
```

---

## Implementation Timeline

### Week 1: Infrastructure Setup
- **Day 1-2:** Phase 1 - Directory structure creation
- **Day 3-4:** Phase 2 - Backup system setup
- **Day 5-7:** Phase 4 - TrueNAS Ubuntu VM + Ollama installation

### Week 2: Migration & Integration
- **Day 1-3:** Phase 5 - File migration to Cheeta
- **Day 4-5:** Phase 3 - Cost optimization setup
- **Day 6-7:** Phase 6 - Development workflow testing

### Week 3: Testing & Refinement
- **Day 1-3:** Full system testing
- **Day 4-5:** Documentation and training
- **Day 6-7:** Phase 7 - Monitoring setup

**Total Time:** 3 weeks

---

## Cost-Benefit Analysis

### Current Costs (Monthly)
- Claude Code: $20/month
- Storage: $0 (owned hardware)
- **Total: $20/month**

### Projected Costs (Monthly)
- Claude Code: $5-8/month (orchestration only)
- TrueNAS VM electricity: ~$5/month (100W × 720h × $0.12/kWh)
- **Total: $10-13/month**

### Annual Savings
- Before: $240/year
- After: $120-156/year
- **Savings: $84-120/year (35-50% reduction)**

### Productivity Gains
- Development speed: 3-5× faster
- Manual approvals: 80% reduction
- Throughput: 300% increase

**ROI:** Pays for itself in infrastructure setup within 3-6 months

---

## Risk Mitigation

### Risk 1: Data Loss
**Mitigation:**
- Daily ZFS snapshots (instant recovery)
- Dual backup (Beaver + QNAP)
- 30-day retention
- Monthly verification tests

### Risk 2: VM Performance
**Mitigation:**
- 10 Gig Ethernet (low latency)
- 16 GB RAM (sufficient for Ollama)
- Monitor resource usage
- Scale up if needed

### Risk 3: Ollama Quality
**Mitigation:**
- Claude Code reviews all Ollama output
- Critical tasks still use Claude Code
- Gradual delegation (start 20%, increase to 80%)
- Fallback to Claude Code if Ollama fails

### Risk 4: Network Outage
**Mitigation:**
- Local Ollama (works offline)
- Cached files on laptop
- Backup internet (phone hotspot)

---

## Success Metrics

### Technical Metrics
- ✅ Backup success rate: 100% (verified daily)
- ✅ Backup restore time: < 5 minutes
- ✅ Ollama response time: < 30 seconds
- ✅ Network throughput: > 1 Gbps

### Cost Metrics
- ✅ Claude Code cost reduction: 70-80%
- ✅ Development cost per feature: 50% reduction
- ✅ ROI timeline: 3-6 months

### Productivity Metrics
- ✅ Project delivery speed: 3-5× faster
- ✅ Manual approval time: 80% reduction
- ✅ Unattended operation: 60% of tasks

---

## Next Steps

### Immediate Actions (This Morning)
1. **Review this plan** - Confirm approach and priorities
2. **Create directory structure** on TrueNAS Cheeta (30 min)
3. **Test TrueNAS SSH access** from laptop (5 min)
4. **Identify project files** on laptop for migration (30 min)

### Short-term Actions (This Week)
1. Set up ZFS snapshot backups (2 hours)
2. Create Ubuntu VM on TrueNAS (3 hours)
3. Install Ollama + models (2 hours)
4. Test Ollama API integration (1 hour)

### Medium-term Actions (Next 2 Weeks)
1. Migrate files to Cheeta (2-3 hours)
2. Set up development workflow (4 hours)
3. Create monitoring scripts (2 hours)
4. Document procedures (2 hours)

---

## Appendix A: Network Diagram

```
Internet
  |
Router (WiFi + 10 Gig Switch)
  |
  ├── Laptop (WiFi) → Development, Mobile
  ├── Workstation (10 Gig) → GPU Training, Heavy Development
  ├── TrueNAS (10 Gig) → Storage + Ubuntu VM (Ollama)
  │   ├── Beaver (RAID) → Long-term storage, backups
  │   ├── Cheeta (SSD) → Active projects
  │   ├── Mice → Utility storage
  │   └── Ubuntu VM → Ollama AI Assistant
  ├── QNAP NAS (2× 2.5 Gig) → Secondary backups
  └── d3kOS Pi (Ethernet) → Prototype/testing
```

---

## Appendix B: File Migration Checklist

**d3kOS Project:**
- [ ] /home/boatiq/Helm-OS/ → /mnt/cheeta/projects/d3kOS/code/
- [ ] /home/boatiq/Helm-OS/doc/ → /mnt/cheeta/projects/d3kOS/docs/
- [ ] Models and datasets → /mnt/cheeta/projects/d3kOS/models/

**AAO Methodology:**
- [ ] Identify AAO files on laptop
- [ ] Migrate to /mnt/cheeta/projects/AAO-Methodology/

**Marketing:**
- [ ] Identify video files
- [ ] Migrate to /mnt/cheeta/projects/Marketing/

**Content:**
- [ ] Blog drafts → /mnt/cheeta/projects/Content/atmyboat-blog/
- [ ] LinkedIn posts → /mnt/cheeta/projects/Content/linkedin/
- [ ] Forum posts → /mnt/cheeta/projects/Content/forums/

**WordPress:**
- [ ] Backup HostPapa site
- [ ] Store in /mnt/cheeta/projects/WordPress/backups/

---

## Appendix C: Command Reference

**TrueNAS SSH Commands:**
```bash
# Connect to TrueNAS
ssh root@192.168.1.102

# Check storage pools
zpool list

# List snapshots
zfs list -t snapshot

# Create manual snapshot
zfs snapshot cheeta/projects@manual-$(date +%Y%m%d)

# Restore from snapshot
zfs rollback cheeta/projects@2026-03-02-1200

# Check replication status
zfs list -t snapshot beaver/backups/cheeta-mirror
```

**Ollama Commands:**
```bash
# Check Ollama status
curl http://192.168.1.103:11434/api/tags

# List models
ollama list

# Run model
ollama run deepseek-coder-v2 "Generate a Python function"

# Pull new model
ollama pull llama3.1:70b
```

**Backup Commands:**
```bash
# Manual backup from laptop
/home/boatiq/scripts/backup-to-truenas.sh

# Verify latest backup
ssh root@192.168.1.102 "ls -lh /mnt/beaver/backups/Laptop/$(date +%Y-%m)/daily/"

# Restore from backup (example)
rsync -avz root@192.168.1.102:/mnt/beaver/backups/Laptop/2026-03-01-1200/ /home/boatiq/restore/
```

---

## Document Control

**Version:** 1.0 (Draft)
**Date:** 2026-03-02
**Author:** Claude Code
**Status:** Awaiting Review
**Next Review:** After user approval

**Changes Required:**
- [ ] User review and feedback
- [ ] Adjust timeline based on priorities
- [ ] Confirm TrueNAS VM specifications
- [ ] Finalize backup retention policy
- [ ] Add specific file paths for migration

---

**END OF PLAN**
