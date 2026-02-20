# d3kOS v0.9.1.2 - 4-Session Execution Guide

**CRITICAL**: This guide shows exactly when and how to execute each session, and ensures all work is pushed to GitHub at the end.

---

## 📋 Quick Reference

| Session | When to Run | Duration | Must Complete Before | Git Action |
|---------|-------------|----------|---------------------|------------|
| **A** | **NOW** (Day 1) | 6-8 hours | Sessions B, C, D | Commit + Push |
| **B** | After A completes | 6-8 hours | Final push | Commit (local) |
| **C** | After A completes | 6-8 hours | Final push | Commit (local) |
| **D** | After A completes | 6-8 hours | Final push | Commit (local) |
| **Final** | After B, C, D done | 30 min | - | **PUSH ALL** |

---

## 🚀 EXECUTION TIMELINE

### Day 1: Session A (REQUIRED FIRST)

**Start Time**: Choose a 6-8 hour block
**Location**: `/home/boatiq/Helm-OS/doc/RELEASE_PLAN_v0.9.1.2.md`
**SSH**: `ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237`

#### Tasks (in order)
1. ✅ **Task A1**: Version & Tier Update (1 hour)
2. ✅ **Task A2**: Timezone Auto-Detection (3-4 hours)
3. ✅ **Task A3**: Voice Assistant Fix (2-3 hours)
4. ✅ **Task A4**: Documentation & Commit (1 hour)

#### Git Actions at End of Session A
```bash
cd /home/boatiq/Helm-OS

# Verify changes
git status
git diff

# Commit Session A
git add -A
git commit -m "Session A: Version 0.9.1.2, Tier 3, Timezone, Voice Fix

- Updated system version to 0.9.1.2
- Set tier to 3 for testing mode
- Implemented timezone auto-detection (GPS → Internet → UTC)
- Created timezone API service (port 8098)
- Added manual timezone override to settings
- Fixed voice assistant wake word detection
- All changes verified and tested

Closes: Foundation updates for v0.9.1.2 release
See: doc/SESSION_A_FOUNDATION_COMPLETE.md"

# Push immediately (unblocks B/C/D)
git push origin main
```

#### Verification Checklist
```bash
# Check version
curl http://localhost/license/info | jq '.version'
# Expected: "0.9.1.2"

# Check tier
curl http://localhost/tier/status | jq '.tier'
# Expected: 3

# Check timezone
curl http://localhost/api/timezone | jq '.timezone'
# Expected: Your detected timezone

# Test voice
# Say "HELM" 20 times
# Expected: Detects 19+ times (>95%)
```

**✅ Session A Complete** → Sessions B, C, D can now run

---

### Day 2-4: Sessions B, C, D (PARALLEL or SEQUENTIAL)

**Choose Your Approach:**

#### Option 1: Sequential (Recommended for Solo Work)
```
Day 2: Session B (Self-Healing)    → 6-8 hours
Day 3: Session C (Data Export)     → 6-8 hours
Day 4: Session D (Image Build)     → 6-8 hours
```

#### Option 2: Parallel (Advanced - 3 Claude Code Sessions)
```
Day 2: Run B, C, D simultaneously → 6-8 hours
       (Requires 3 terminal windows / Claude sessions)
```

---

### SESSION B: Self-Healing System

**When**: After Session A pushed to GitHub
**Duration**: 6-8 hours
**Location**: `/home/boatiq/Helm-OS/doc/RELEASE_PLAN_v0.9.1.2.md` (Session B section)

#### Tasks (in order)
1. ✅ **Task B1**: Issue Detection Service (2-3 hours)
2. ✅ **Task B2**: Remediation Engine (2-3 hours)
3. ✅ **Task B3**: Self-Healing API & UI (1-2 hours)
4. ✅ **Task B4**: Documentation & Commit (1 hour)

#### Git Actions at End of Session B
```bash
cd /home/boatiq/Helm-OS

# Commit Session B (DO NOT PUSH YET)
git add -A
git commit -m "Session B: Self-Healing System Implementation

- Implemented AI-powered self-healing per spec Section 6.4
- Created issue detection service (engine + Pi health)
- Created remediation engine with safe actions
- Integrated AI diagnosis for root cause analysis
- Added self-healing API (port 8099)
- Created settings UI for monitoring
- All changes verified and tested

Closes: Self-healing system for v0.9.1.2
See: doc/SESSION_B_SELF_HEALING_COMPLETE.md"

# DO NOT PUSH - wait for all sessions to complete
```

#### Verification Checklist
```bash
# Services running
systemctl status d3kos-issue-detector
systemctl status d3kos-remediation
systemctl status d3kos-healing-api

# API responding
curl http://localhost/healing/stats | jq .

# Simulate issue (test detection)
# Fill disk to 92% or stop a service
# Verify: Issue detected and remediated
```

**✅ Session B Complete** → Committed locally, waiting for final push

---

### SESSION C: Data Export & Backup

**When**: After Session A pushed to GitHub
**Duration**: 6-8 hours
**Location**: `/home/boatiq/Helm-OS/doc/RELEASE_PLAN_v0.9.1.2_PART2.md` (Session C section)

#### Tasks (in order)
1. ✅ **Task C1**: Export Queue System (3-4 hours)
2. ✅ **Task C2**: Boatlog Export Fix (1-2 hours)
3. ✅ **Task C3**: Backup & Restore (2-3 hours)
4. ✅ **Task C4**: Documentation & Commit (1 hour)

#### Git Actions at End of Session C
```bash
cd /home/boatiq/Helm-OS

# Commit Session C (DO NOT PUSH YET)
git add -A
git commit -m "Session C: Data Export Queue & Backup System

- Implemented export queue with retry logic (3 attempts)
- Fixed boatlog CSV export button
- Created backup & restore scripts
- Added backup API (port 8100)
- Integrated backup UI in settings
- Auto-cleanup old backups (keep 10)
- All changes verified and tested

Closes: Data management for v0.9.1.2
See: doc/SESSION_C_DATA_EXPORT_COMPLETE.md"

# DO NOT PUSH - wait for all sessions to complete
```

#### Verification Checklist
```bash
# Export queue working
curl -X POST http://localhost/export/generate
curl http://localhost/export/queue | jq .

# Boatlog export working
curl http://localhost/export/boatlog/csv > test.csv
wc -l test.csv  # Should have entries

# Backup working
curl -X POST http://localhost/api/backup/create
curl http://localhost/api/backup/list | jq .
```

**✅ Session C Complete** → Committed locally, waiting for final push

---

### SESSION D: Image Build & Testing

**When**: After Session A pushed to GitHub
**Duration**: 6-8 hours
**Location**: `/home/boatiq/Helm-OS/doc/RELEASE_PLAN_v0.9.1.2_PART2.md` (Session D section)

#### Tasks (in order)
1. ✅ **Task D1**: Image Build Script (2-3 hours)
2. ✅ **Task D2**: Testing Matrix (2-3 hours)
3. ✅ **Task D3**: Documentation Updates (1-2 hours)
4. ✅ **Task D4**: Final Verification (1 hour)

#### Git Actions at End of Session D
```bash
cd /home/boatiq/Helm-OS

# Commit Session D (DO NOT PUSH YET)
git add -A
git commit -m "Session D: Image Build & Final Documentation

- Created image build script and guide
- Completed testing matrix (all tests passing)
- Updated README.md for v0.9.1.2 release
- Created CHANGELOG.md
- Updated MASTER_SYSTEM_SPEC.md to v3.8
- Final system verification complete
- Ready for GitHub release

Closes: v0.9.1.2 release preparation
See: doc/IMAGE_BUILD_GUIDE.md, doc/TESTING_MATRIX_v0.9.1.2.md"

# DO NOT PUSH - wait for final integration
```

#### Verification Checklist
```bash
# Testing matrix complete
cat doc/TESTING_MATRIX_v0.9.1.2.md
# All tests marked as PASS

# Documentation updated
grep "0.9.1.2" README.md
grep "0.9.1.2" CHANGELOG.md

# Image script ready (don't run yet - takes 30-60 min)
ls -lh /opt/d3kos/scripts/create-image.sh
```

**✅ Session D Complete** → Committed locally, waiting for final push

---

## 🎯 FINAL INTEGRATION & GITHUB PUSH

**When**: After ALL 4 sessions are complete
**Duration**: 30 minutes
**Critical**: This is when EVERYTHING gets pushed to GitHub

### Step 1: Verify All Commits

```bash
cd /home/boatiq/Helm-OS

# Check commit history
git log --oneline -5

# Expected output:
# xxxxxxx Session D: Image Build & Final Documentation
# xxxxxxx Session C: Data Export Queue & Backup System
# xxxxxxx Session B: Self-Healing System Implementation
# xxxxxxx Session A: Version 0.9.1.2, Tier 3, Timezone, Voice Fix
# xxxxxxx Add d3kOS v0.9.1.2 Release Plan

# Verify nothing uncommitted
git status
# Expected: "nothing to commit, working tree clean"
```

### Step 2: Integration Testing

```bash
# Test all services running
systemctl status d3kos-* --no-pager

# Test all APIs responding
curl -f http://localhost/license/info       # Session A
curl -f http://localhost/tier/status        # Session A
curl -f http://localhost/api/timezone       # Session A
curl -f http://localhost/healing/stats      # Session B
curl -f http://localhost/export/status      # Session C
curl -f http://localhost/api/backup/list    # Session C

# Test web pages load
curl -f http://localhost/
curl -f http://localhost/settings.html
curl -f http://localhost/dashboard.html
curl -f http://localhost/settings-healing.html  # Session B

# If any fail, DO NOT PUSH - debug and fix first
```

### Step 3: Run Full Testing Matrix

```bash
# Open testing matrix
cat doc/TESTING_MATRIX_v0.9.1.2.md

# Go through each test section:
# - Hardware Tests
# - Software Tests (Core, Tier, AI, Data, Self-Healing, Timezone)
# - Services (all 14+ services)
# - Performance Tests

# Mark each test as PASS or FAIL
# If ANY critical test fails, DO NOT PUSH - fix first

# Commit testing results
git add doc/TESTING_MATRIX_v0.9.1.2.md
git commit -m "Testing: v0.9.1.2 validation complete - all tests passing"
```

### Step 4: Final Verification Checklist

**System State**:
- [ ] Version = 0.9.1.2 (check: `curl http://localhost/license/info | jq .version`)
- [ ] Tier = 3 (check: `curl http://localhost/tier/status | jq .tier`)
- [ ] All 14+ services active (check: `systemctl list-units 'd3kos-*'`)
- [ ] Disk usage < 90% (check: `df -h /`)
- [ ] No critical errors in logs (check: `sudo journalctl -p err -n 20`)

**Git State**:
- [ ] 5+ commits ready (release plan + 4 sessions + testing)
- [ ] All changes committed
- [ ] No uncommitted files
- [ ] No merge conflicts

**Documentation**:
- [ ] README.md shows v0.9.1.2
- [ ] CHANGELOG.md created with v0.9.1.2 entry
- [ ] MASTER_SYSTEM_SPEC.md updated to v3.8
- [ ] All 4 session summaries created

### Step 5: PUSH TO GITHUB (THE BIG MOMENT!)

```bash
cd /home/boatiq/Helm-OS

# Final check
git log --oneline -10
git status

# Push everything
git push origin main

# Verify push succeeded
git log origin/main --oneline -5

# Expected: All 5+ commits now on GitHub
```

### Step 6: Verify on GitHub

1. Open browser: https://github.com/SkipperDon/d3kos
2. Check commits tab: Should see all 5+ commits
3. Check files:
   - README.md shows v0.9.1.2
   - CHANGELOG.md exists
   - doc/RELEASE_PLAN_*.md files present
   - doc/SESSION_*_COMPLETE.md files present

**✅ ALL WORK PUSHED TO GITHUB!**

---

## 📊 EXECUTION SUMMARY

### Timeline Example (Sequential)

```
Day 1 (6-8h):  Session A → Commit → PUSH ✅
               ↓
Day 2 (6-8h):  Session B → Commit (local only)
               ↓
Day 3 (6-8h):  Session C → Commit (local only)
               ↓
Day 4 (6-8h):  Session D → Commit (local only)
               ↓
Day 5 (30m):   Final Integration → Testing → PUSH ALL ✅
```

### Timeline Example (Parallel - Advanced)

```
Day 1 (6-8h):  Session A → Commit → PUSH ✅
               ↓
Day 2 (6-8h):  Session B + C + D (parallel) → Commit all (local)
               ↓
Day 3 (30m):   Final Integration → Testing → PUSH ALL ✅
```

---

## ⚠️ CRITICAL RULES

### MUST DO:
1. ✅ Complete Session A FIRST (blocks others)
2. ✅ PUSH Session A immediately (unblocks B/C/D)
3. ✅ Commit B/C/D but DON'T push yet
4. ✅ Run integration tests BEFORE final push
5. ✅ Push everything together at the end

### MUST NOT DO:
1. ❌ Don't skip Session A
2. ❌ Don't run B/C/D before A is pushed
3. ❌ Don't push B/C/D individually (push together)
4. ❌ Don't push if tests fail
5. ❌ Don't skip documentation commits

---

## 🔧 TROUBLESHOOTING

### If Session A Push Fails
```bash
# Check connection
git remote -v

# Try push again
git push origin main

# If still fails, check GitHub credentials
```

### If Integration Tests Fail
```bash
# Don't push to GitHub
# Debug the failing component
# Fix the issue
# Commit the fix
# Re-run tests
# Only push when all tests pass
```

### If You Need to Pause

**Safe Pause Points**:
- ✅ After Session A (pushed to GitHub)
- ✅ After Session B (committed locally)
- ✅ After Session C (committed locally)
- ✅ After Session D (committed locally)

**Resume**:
```bash
cd /home/boatiq/Helm-OS
git status  # Check where you left off
git log --oneline -5  # See what's committed
# Continue from next session
```

---

## 📁 FILE TRACKING

### Files Modified by Session

**Session A**:
- `/opt/d3kos/config/license.json`
- `/opt/d3kos/config/version.txt` (new)
- `/opt/d3kos/scripts/detect-timezone.sh` (new)
- `/opt/d3kos/services/system/timezone-api.py` (new)
- `/var/www/html/settings.html`
- `MASTER_SYSTEM_SPEC.md`
- `doc/SESSION_A_FOUNDATION_COMPLETE.md` (new)

**Session B**:
- `/opt/d3kos/services/self-healing/` (new directory)
- `/var/www/html/settings-healing.html` (new)
- `/var/www/html/settings.html` (add link)
- `MASTER_SYSTEM_SPEC.md`
- `doc/SESSION_B_SELF_HEALING_COMPLETE.md` (new)

**Session C**:
- `/opt/d3kos/services/export/export-manager.py`
- `/opt/d3kos/scripts/create-backup.sh` (new)
- `/opt/d3kos/scripts/restore-backup.sh` (new)
- `/opt/d3kos/services/system/backup-api.py` (new)
- `/var/www/html/boatlog.html`
- `/var/www/html/settings.html` (add backup section)
- `MASTER_SYSTEM_SPEC.md`
- `doc/SESSION_C_DATA_EXPORT_COMPLETE.md` (new)

**Session D**:
- `/opt/d3kos/scripts/create-image.sh` (new)
- `README.md`
- `CHANGELOG.md` (new)
- `MASTER_SYSTEM_SPEC.md`
- `doc/IMAGE_BUILD_GUIDE.md` (new)
- `doc/TESTING_MATRIX_v0.9.1.2.md` (new)
- `doc/SESSION_D_IMAGE_BUILD_COMPLETE.md` (new)

---

## ✅ SUCCESS CONFIRMATION

After final push, you should have:

**On Raspberry Pi**:
- 8 new systemd services running
- 3 new API endpoints (8098, 8099, 8100)
- Version 0.9.1.2, Tier 3
- All features working

**On GitHub**:
- 5+ new commits on main branch
- Updated README.md (v0.9.1.2)
- New CHANGELOG.md
- 3 release plan documents
- 4 session completion documents
- Updated MASTER_SYSTEM_SPEC.md (v3.8)

**System Ready For**:
- Image distribution
- Testing by users
- GitHub release creation (optional)
- Continued development

---

## 🎉 YOU'RE DONE!

**Congratulations! d3kOS v0.9.1.2 is complete and published to GitHub!**

Next steps:
1. Build image (optional): `sudo /opt/d3kos/scripts/create-image.sh`
2. Create GitHub release (optional)
3. Announce to users
4. Plan v0.9.2 features

---

**Need help during execution?**
- Check the full plan documents for detailed steps
- Each session has verification checklists
- Emergency rollback procedures included
- Create GitHub issue if stuck

**LET'S BUILD d3kOS v0.9.1.2!**
