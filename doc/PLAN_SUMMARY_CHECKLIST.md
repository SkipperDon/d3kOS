# Infrastructure Plan - Quick Review Checklist

**Date:** 2026-03-02
**Full Plan:** INFRASTRUCTURE_REORGANIZATION_PLAN.md

---

## The Big Picture

**Problem:** Claude Code costs unsustainable ($20/month), files unorganized, no backups, slow manual workflow

**Solution:** Organize files on TrueNAS, deploy Ollama for local AI, reduce Claude Code to orchestrator only

**Result:** 70-80% cost reduction, 3-5× faster development, automated backups

---

## 7 Phases - Priority Order

### ✅ Phase 1: Directory Structure (30 min - DO THIS MORNING)
**Create organized folders on TrueNAS Cheeta:**
```
/mnt/cheeta/projects/
  ├── d3kOS/
  ├── AAO-Methodology/
  ├── Marketing/
  ├── Content/ (blogs, forums)
  └── WordPress/
```

**Backup structure on Beaver:**
```
/mnt/beaver/backups/
  ├── TrueNAS/ (configs only)
  ├── Laptop/ (full backups)
  └── Workstation/ (full backups)
```

**Action:** SSH to TrueNAS, run mkdir commands
**Time:** 30 minutes
**Risk:** None (just creating folders)

---

### ✅ Phase 2: Automated Backups (2 hours)
**Daily backups at noon + midnight using ZFS snapshots**
- Instant snapshots (< 1 second)
- 30-day retention
- Auto-replicate Cheeta → Beaver

**Action:** Create cron jobs + scripts
**Time:** 2 hours
**Risk:** Low (ZFS snapshots are safe)

---

### ✅ Phase 4: Ubuntu VM + Ollama (3 hours) - BEFORE MIGRATION
**Deploy Ollama on TrueNAS for local AI:**
- Ubuntu 22.04 VM (16 GB RAM, 8 vCPUs)
- IP: 192.168.1.103
- Ollama with 4 models (~90 GB)
- 10 Gig Ethernet network

**Action:** Create VM, install Ubuntu, install Ollama
**Time:** 3 hours
**Risk:** Medium (VM setup, but reversible)

---

### ✅ Phase 3: Cost Optimization (4 hours)
**Reduce Claude Code usage by 80%:**
- Claude Code: Planning + orchestration only
- Ollama: Code generation, docs, testing (80% of work)
- Integration scripts for delegation

**Before:** $20/month, slow manual approvals
**After:** $5-8/month, mostly automated

**Action:** Create delegation scripts, test workflow
**Time:** 4 hours
**Risk:** Low (can revert if doesn't work)

---

### ✅ Phase 5: File Migration (2-3 hours)
**Move project files from laptop to Cheeta:**
- d3kOS → /mnt/cheeta/projects/d3kOS/
- AAO, Marketing, Content, WordPress → organized folders
- **DO NOT DELETE** from laptop until verified

**Action:** rsync files to TrueNAS
**Time:** 2-3 hours (depends on file size)
**Risk:** Low (keeping originals on laptop)

---

### ✅ Phase 6: New Development Workflow (4 hours)
**Set up Claude Code + Ollama integration:**
- Helper scripts for code/review/docs
- Auto-approval policies
- Unattended operation for routine tasks

**Action:** Create wrapper scripts, test delegation
**Time:** 4 hours
**Risk:** Low (gradual transition)

---

### ✅ Phase 7: Monitoring (2 hours)
**Set up health checks:**
- Daily backup verification
- Ollama API monitoring
- Email alerts on failure

**Action:** Create monitoring scripts + cron jobs
**Time:** 2 hours
**Risk:** None (just monitoring)

---

## Cost Comparison

### Current (100% Claude Code)
- Monthly: $20
- Annual: $240
- Speed: Baseline
- Manual approvals: Every step

### Proposed (Claude Code + Ollama)
- Monthly: $10-13 ($5-8 Claude + $5 electricity)
- Annual: $120-156
- **Savings: $84-120/year (35-50%)**
- Speed: 3-5× faster
- Manual approvals: 80% reduction

---

## Timeline

**Week 1 (Infrastructure)**
- Days 1-2: Phase 1 (directories) + Phase 2 (backups)
- Days 3-7: Phase 4 (Ubuntu VM + Ollama)

**Week 2 (Migration + Integration)**
- Days 1-3: Phase 5 (file migration)
- Days 4-5: Phase 3 (cost optimization)
- Days 6-7: Phase 6 (new workflow)

**Week 3 (Testing + Monitoring)**
- Days 1-5: Full system testing
- Days 6-7: Phase 7 (monitoring)

**Total:** 3 weeks to full deployment

---

## This Morning's Tasks (Priority 1)

**Goal:** Get organized foundation in place

### Task 1: Test TrueNAS Access (5 min)
```bash
ssh root@192.168.1.102
# Password: damcor53$
```

### Task 2: Create Directory Structure (30 min)
```bash
# Run commands from full plan
mkdir -p /mnt/cheeta/projects/{d3kOS,AAO-Methodology,Marketing,Content,WordPress}
# ... (see full plan for all commands)
```

### Task 3: Identify Files to Migrate (30 min)
```bash
# On laptop
find /home/boatiq -type f \( -name "*.md" -o -name "*.odt" -o -name "*.docx" \) | \
  grep -E "(d3kOS|AAO|marketing|blog|forum)" > /tmp/project-files.txt

cat /tmp/project-files.txt  # Review what needs migrating
```

### Task 4: Review Full Plan (15 min)
- Read INFRASTRUCTURE_REORGANIZATION_PLAN.md
- Confirm approach
- Ask questions

**Total Time This Morning:** ~1.5 hours

---

## Questions to Confirm

1. **TrueNAS VM Specs:** 16 GB RAM, 8 vCPUs, 100 GB storage OK?
2. **Backup Schedule:** Noon + midnight daily OK?
3. **Retention:** 30 days of daily backups sufficient?
4. **Migration Order:** d3kOS first, then AAO, Marketing, Content?
5. **Ollama Models:** deepseek-coder-v2, codellama:34b, qwen2.5-coder:32b, llama3.1:70b OK?
6. **Cost Target:** $10-13/month acceptable?

---

## Risks & Mitigations

**Risk 1: Data loss during migration**
- ✅ Mitigation: Keep originals on laptop, verify before deleting

**Risk 2: TrueNAS VM performance**
- ✅ Mitigation: 10 Gig Ethernet, monitor and adjust

**Risk 3: Ollama code quality**
- ✅ Mitigation: Claude Code reviews all output, gradual transition

**Risk 4: Backup failures**
- ✅ Mitigation: Daily verification, dual backup (Beaver + QNAP)

---

## Success Criteria

After 3 weeks:
- ✅ All 5 projects organized on Cheeta
- ✅ Daily automated backups working (100% success rate)
- ✅ Ollama handling 80% of development tasks
- ✅ Claude Code costs reduced by 70-80%
- ✅ Development speed 3-5× faster
- ✅ Manual approvals reduced by 80%

---

## Decision Points

**Option A: Full Implementation (3 weeks)**
- Complete all 7 phases
- Maximum cost savings
- Full automation

**Option B: Phased Approach (6 weeks)**
- Week 1-2: Structure + backups only
- Week 3-4: Ollama deployment
- Week 5-6: Integration + optimization
- Lower risk, slower savings

**Option C: Critical Path Only (1 week)**
- Phase 1: Directory structure
- Phase 2: Backups
- Phase 5: File migration
- Skip Ollama (defer cost optimization)

**Recommendation:** Option A (full implementation, 3 weeks)

---

## Next Steps

**Right Now:**
1. Review this summary
2. Read full plan (INFRASTRUCTURE_REORGANIZATION_PLAN.md)
3. Confirm approach
4. Ask questions

**After Approval:**
1. SSH to TrueNAS
2. Create directory structure (30 min)
3. Test file transfer (5 min)
4. Begin Phase 2 (backups)

---

## Questions?

**Ask me:**
- Clarifications on any phase
- Adjustments to timeline
- Changes to directory structure
- Alternative approaches
- Technical details

**I'm ready to start when you are!**

---

**Status:** ⏳ Awaiting your review and approval
**Next:** Confirm approach → Begin Phase 1 (directories)
