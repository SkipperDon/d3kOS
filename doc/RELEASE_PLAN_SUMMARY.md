# d3kOS v0.9.1.2 Release Plan - Executive Summary

**Version**: 0.9.1.2 (Tier 0 Installation Complete)
**Date**: February 20, 2026
**Total Effort**: 24-32 hours (parallelizable)
**Status**: ✅ READY TO EXECUTE

---

## Quick Overview

This release completes all Tier 0 features, sets tier to 3 for testing, and prepares the system for image distribution.

### What's Being Built

| Session | Focus | Duration | Can Run After |
|---------|-------|----------|---------------|
| **A** | Foundation (version, tier, timezone, voice) | 6-8h | START HERE |
| **B** | Self-Healing System | 6-8h | Session A |
| **C** | Data Export & Backup | 6-8h | Session A |
| **D** | Image Build & Testing | 6-8h | Session A |

### Parallelization

```
Session A (MUST RUN FIRST)
    ↓
┌───┴───┬───────┬───────┐
│   B   │   C   │   D   │  (Can run in parallel)
│ Self- │ Data  │ Image │
│ Heal  │ Mgmt  │ Build │
└───┬───┴───┬───┴───┬───┘
    └───────┴───────┘
           ↓
   Final Integration
           ↓
      GitHub Push
```

---

## Session A: Foundation (START HERE)

**MUST complete before B/C/D**

### Tasks
1. ✅ Update version to 0.9.1.2 (1h)
2. ✅ Set tier to 3 for testing (30min)
3. ✅ Implement timezone auto-detection (3-4h)
4. ✅ Fix voice assistant wake word detection (2-3h)
5. ✅ Document and commit (1h)

### Key Files
- `/opt/d3kos/config/license.json` (version, tier)
- `/opt/d3kos/scripts/detect-timezone.sh` (NEW)
- `/opt/d3kos/services/system/timezone-api.py` (NEW, port 8098)
- `/opt/d3kos/services/voice/voice-assistant-hybrid.py` (MODIFIED)

### Verification
```bash
# Check version
curl http://localhost/license/info | jq '.version'
# Should show: "0.9.1.2"

# Check tier
curl http://localhost/tier/status | jq '.tier'
# Should show: 3

# Check timezone
curl http://localhost/api/timezone | jq '.timezone'
# Should show detected timezone

# Test voice
# Say "HELM" 20 times, should detect 19+ times
```

---

## Session B: Self-Healing System

**Runs in parallel after Session A**

### Tasks
1. ✅ Create issue detection service (2-3h)
2. ✅ Create remediation engine (2-3h)
3. ✅ Create self-healing API & UI (1-2h)
4. ✅ Document and commit (1h)

### Key Files
- `/opt/d3kos/services/self-healing/issue_detector.py` (NEW)
- `/opt/d3kos/services/self-healing/remediation_engine.py` (NEW)
- `/opt/d3kos/services/self-healing/self_healing_api.py` (NEW, port 8099)
- `/var/www/html/settings-healing.html` (NEW)

### Services Created
- `d3kos-issue-detector.service` (detection)
- `d3kos-remediation.service` (auto-fix)
- `d3kos-healing-api.service` (port 8099)

### Verification
```bash
# Check services running
systemctl status d3kos-issue-detector
systemctl status d3kos-remediation
systemctl status d3kos-healing-api

# Test API
curl http://localhost/healing/stats | jq .

# View UI
curl http://localhost/settings-healing.html
```

---

## Session C: Data Export & Backup

**Runs in parallel after Session A**

### Tasks
1. ✅ Complete export queue system (3-4h)
2. ✅ Fix boatlog export button (1-2h)
3. ✅ Implement backup & restore (2-3h)
4. ✅ Document and commit (1h)

### Key Files
- `/opt/d3kos/services/export/export-manager.py` (MODIFIED - add queue)
- `/opt/d3kos/scripts/create-backup.sh` (NEW)
- `/opt/d3kos/scripts/restore-backup.sh` (NEW)
- `/opt/d3kos/services/system/backup-api.py` (NEW, port 8100)
- `/var/www/html/boatlog.html` (MODIFIED - fix export)

### Services Created
- `d3kos-backup-api.service` (port 8100)

### Verification
```bash
# Test export queue
curl -X POST http://localhost/export/generate
curl http://localhost/export/queue | jq .

# Test boatlog export
curl http://localhost/export/boatlog/csv > test.csv
wc -l test.csv  # Should have entries

# Test backup
curl -X POST http://localhost/api/backup/create
curl http://localhost/api/backup/list | jq .
```

---

## Session D: Image Build & Testing

**Runs in parallel after Session A**

### Tasks
1. ✅ Create image build script (2-3h)
2. ✅ Complete testing matrix (2-3h)
3. ✅ Update all documentation (1-2h)
4. ✅ Final verification & GitHub push (1h)

### Key Files
- `/opt/d3kos/scripts/create-image.sh` (NEW)
- `doc/IMAGE_BUILD_GUIDE.md` (NEW)
- `doc/TESTING_MATRIX_v0.9.1.2.md` (NEW)
- `README.md` (MODIFIED - v0.9.1.2)
- `CHANGELOG.md` (NEW)

### Deliverables
- ✅ Image build script
- ✅ Testing matrix (100% pass rate)
- ✅ Updated documentation
- ✅ Compressed image (d3kos-v0.9.1.2-YYYYMMDD.img.gz)

### Verification
```bash
# Run all tests
# See: doc/TESTING_MATRIX_v0.9.1.2.md

# Build image (optional - takes 30-60 min)
sudo /opt/d3kos/scripts/create-image.sh

# Verify documentation
cat README.md | grep "0.9.1.2"
cat CHANGELOG.md | grep "0.9.1.2"
```

---

## Execution Instructions

### Step 1: Start Session A

```bash
# Open full plan
cat /home/boatiq/Helm-OS/doc/RELEASE_PLAN_v0.9.1.2.md

# Follow Session A tasks in order:
# - Task A1: Version & Tier Update
# - Task A2: Timezone Auto-Detection
# - Task A3: Voice Assistant Fix
# - Task A4: Documentation & Commit

# When Session A complete:
# - Verify all changes
# - Commit to git
# - Push to origin/main
```

### Step 2: Start Sessions B, C, D (Parallel)

**Option 1: Run sequentially**
```bash
# Do Session B, then C, then D
# Safer, easier to debug, but slower
```

**Option 2: Run in parallel (Advanced)**
```bash
# Terminal 1: Session B (Self-Healing)
# Terminal 2: Session C (Data Export)
# Terminal 3: Session D (Image Build)

# IMPORTANT: Watch for file conflicts!
# - Session B: /opt/d3kos/services/self-healing/*
# - Session C: /opt/d3kos/services/export/*, /var/www/html/boatlog.html
# - Session D: Documentation files

# No conflicts = safe to run parallel
```

### Step 3: Final Integration

```bash
# After all sessions complete:

# 1. Run integration tests
systemctl status d3kos-*
curl http://localhost/license/info
curl http://localhost/tier/status
curl http://localhost/export/status
curl http://localhost/api/timezone
curl http://localhost/healing/stats
curl http://localhost/api/backup/list

# 2. Run testing matrix
# See: doc/TESTING_MATRIX_v0.9.1.2.md
# Mark all tests as pass/fail

# 3. Verify all commits pushed
git log --oneline -10
git status

# 4. Push to GitHub
git push origin main
```

### Step 4: Build Image (Optional)

```bash
# Only if distributing to others
sudo /opt/d3kos/scripts/create-image.sh

# Wait 30-60 minutes

# Upload to GitHub Releases:
# https://github.com/SkipperDon/d3kos/releases
```

---

## Dependency Matrix

### File Dependencies

| File | Session A | Session B | Session C | Session D |
|------|-----------|-----------|-----------|-----------|
| license.json | WRITE | READ | READ | READ |
| version.txt | WRITE | READ | READ | READ |
| timezone.txt | WRITE | READ | - | READ |
| settings.html | WRITE | WRITE | WRITE | - |
| boatlog.html | - | - | WRITE | - |
| README.md | - | - | - | WRITE |
| MASTER_SYSTEM_SPEC.md | WRITE | WRITE | WRITE | WRITE |

**Conflict Resolution**:
- Session A must complete first (writes version/tier)
- Sessions B/C both modify settings.html → merge carefully
- Session D only reads system state → no conflicts

### Service Dependencies

| Service | Created By | Depends On |
|---------|------------|------------|
| d3kos-timezone-api | Session A | - |
| d3kos-issue-detector | Session B | Session A (tier 3) |
| d3kos-remediation | Session B | issue-detector |
| d3kos-healing-api | Session B | issue-detector |
| d3kos-backup-api | Session C | - |

**Start Order**:
1. Session A services first
2. Sessions B/C services can start in any order

---

## Port Allocation

| Port | Service | Session | Status |
|------|---------|---------|--------|
| 8080 | AI API | (Existing) | ✅ Active |
| 8084 | Camera Stream | (Existing) | ✅ Active |
| 8086 | Fish Detector | (Existing) | ⏸️ Inactive |
| 8088 | Notifications | (Existing) | ✅ Active |
| 8089 | Marine Vision API | (Existing) | - |
| 8091 | License API | (Existing) | ✅ Active |
| 8092 | History API | (Existing) | ✅ Active |
| 8093 | Tier API | (Existing) | ✅ Active |
| 8094 | Export Manager | (Existing) | ✅ Active |
| 8097 | Upload API | (Existing) | ✅ Active |
| **8098** | **Timezone API** | **Session A** | **NEW** |
| **8099** | **Self-Healing API** | **Session B** | **NEW** |
| **8100** | **Backup API** | **Session C** | **NEW** |

---

## Git Workflow

### Commit Strategy

Each session creates ONE commit:

```bash
# Session A
git commit -m "Session A: Version 0.9.1.2, Tier 3, Timezone, Voice Fix"

# Session B
git commit -m "Session B: Self-Healing System Implementation"

# Session C
git commit -m "Session C: Data Export Queue & Backup System"

# Session D
git commit -m "Session D: Image Build & Final Documentation"
```

### Branch Strategy (Optional)

```bash
# Main branch (recommended for simple workflow)
git checkout main
# Work directly on main, push after each session

# OR feature branches (advanced)
git checkout -b session-a-foundation
# ... work ...
git commit -m "Session A complete"
git checkout main
git merge session-a-foundation
git push origin main
```

---

## Success Criteria

### Session A
- [X] Version shows 0.9.1.2
- [X] Tier shows 3
- [X] Timezone auto-detected
- [X] Voice wake word >95% detection

### Session B
- [X] Issue detection working
- [X] Auto-remediation functional
- [X] AI diagnosis integrated
- [X] Self-healing UI accessible

### Session C
- [X] Export queue with retry logic
- [X] Boatlog CSV downloads
- [X] Backup creates .tar.gz
- [X] Restore preserves data

### Session D
- [X] Image build script works
- [X] Testing matrix 100% pass
- [X] All documentation updated
- [X] GitHub pushed

### Final
- [X] All 4 sessions committed
- [X] Integration tests passing
- [X] Zero critical bugs
- [X] Image ready for distribution

---

## Time Estimates

### Best Case (Experienced, No Issues)
- Session A: 6 hours
- Session B: 6 hours (parallel)
- Session C: 6 hours (parallel)
- Session D: 6 hours (parallel)
- **Total: 12 hours** (A sequential, then B/C/D parallel)

### Realistic Case (Some Debugging)
- Session A: 8 hours
- Session B: 8 hours (parallel)
- Session C: 7 hours (parallel)
- Session D: 7 hours (parallel)
- **Total: 16 hours** (A sequential, then B/C/D parallel)

### Worst Case (Many Issues, Sequential)
- Session A: 8 hours
- Session B: 8 hours
- Session C: 8 hours
- Session D: 8 hours
- **Total: 32 hours** (all sequential)

---

## Emergency Rollback

### If Something Goes Wrong

**Session A Rollback**:
```bash
# Restore license.json backup
sudo cp /opt/d3kos/config/license.json.bak /opt/d3kos/config/license.json

# Restore voice service backup
sudo cp /opt/d3kos/services/voice/voice-assistant-hybrid.py.bak \
        /opt/d3kos/services/voice/voice-assistant-hybrid.py
sudo systemctl restart d3kos-voice

# Revert git commits
git revert HEAD
git push origin main
```

**Session B/C Rollback**:
```bash
# Stop new services
sudo systemctl stop d3kos-issue-detector
sudo systemctl stop d3kos-remediation
sudo systemctl stop d3kos-healing-api
sudo systemctl stop d3kos-backup-api

# Disable auto-start
sudo systemctl disable d3kos-issue-detector
sudo systemctl disable d3kos-remediation
sudo systemctl disable d3kos-healing-api
sudo systemctl disable d3kos-backup-api

# Revert git
git revert HEAD
```

---

## Contact & Support

**Questions during implementation?**
- Check full plan: `doc/RELEASE_PLAN_v0.9.1.2.md` (Part 1)
- Check continuation: `doc/RELEASE_PLAN_v0.9.1.2_PART2.md`
- Check MASTER_SYSTEM_SPEC.md for detailed specs
- Create GitHub issue if stuck

---

## Ready to Start?

1. ✅ Read this summary
2. ✅ Open full plan (Part 1 + Part 2)
3. ✅ Start Session A
4. ✅ After A completes, start B/C/D
5. ✅ Run integration tests
6. ✅ Push to GitHub
7. ✅ Build image (optional)
8. ✅ Celebrate! 🎉

**Let's build d3kOS v0.9.1.2!**
