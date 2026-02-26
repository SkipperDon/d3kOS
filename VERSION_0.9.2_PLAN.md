# d3kOS Version 0.9.2 Release Plan

**Current Version:** 0.9.1.2 (February 20, 2026)
**Target Version:** 0.9.2
**Target Date:** March 2026 (estimated)
**Focus:** Bug Fixes + Remaining Core Features

---

## 🎯 Release Goals

**Primary:** Stability and bug fixes from field testing
**Secondary:** Complete remaining Tier 1/2/3 features
**Theme:** "Field-Tested & Feature-Complete"

---

## ✅ Completed in v0.9.1.2

### Core System:
- ✅ Installation ID system (file-based, persistent)
- ✅ Tier detection system (Tier 0/1/2/3)
- ✅ License API (port 8091)
- ✅ Tier API (port 8093)
- ✅ Timezone auto-detection (GPS → Internet → UTC)
- ✅ Voice assistant (Vosk wake words: helm/advisor/counsel)
- ✅ AI assistant (OpenRouter + rule-based, 13 patterns)
- ✅ Signal K integration
- ✅ Marine Vision Phase 1 (camera streaming)
- ✅ Marine Vision Phase 2.1 (fish detection - YOLOv8n ONNX)
- ✅ Marine Vision Phase 2.6 (Telegram notifications)
- ✅ Export manager (port 8094)
- ✅ Network settings UI (WiFi management)

### Bug Fixes (Field Testing):
- ✅ sysstat package added (Holger's bug report)
- ✅ Signal K GPS errors fixed (gpsd configuration)
- ✅ vcan0 simulator errors fixed
- ✅ QR code simplified (16-char plain text)
- ✅ Export manager port mismatch fixed
- ✅ On-screen keyboard auto-focus added
- ✅ Navigation WebSocket connection fixed
- ✅ Weather radar default GPS added

### Documentation:
- ✅ Bug fix guide (BUGFIX_SYSSTAT_HARDWARE_CONFIG.md)
- ✅ Problems & Resolutions log (15 issues documented)
- ✅ Forward Watch specification (complete)
- ✅ Iceberg datasets documented (6,790 images)
- ✅ Alternative hardware configurations (Moitessier HAT, 12MHz CAN)

---

## 🔨 To-Do for v0.9.2

### Critical Bug Fixes:

#### 1. Voice Assistant Wake Word Detection ⚠️ CRITICAL
**Status:** OPEN - Not detecting wake words
**Priority:** HIGH
**Estimated Time:** 6-8 hours
**Blocker:** Yes (Tier 2+ feature broken)

**Tasks:**
- [ ] Timeline analysis (system updates since "last working")
- [ ] Manual PocketSphinx testing (not via Python)
- [ ] Test alternative wake word engines (Vosk, Porcupine)
- [ ] Fix PipeWire audio signal loss (17× reduction)
- [ ] Verify microphone signal strength
- [ ] Test on fresh Pi installation
- [ ] Document final solution

**Acceptance Criteria:**
- Wake word detection working with 95%+ accuracy
- Voice assistant responds within 2 seconds
- Works with Anker S330 microphone at plughw:3,0

---

### High Priority Features:

#### 2. Data Export System (Complete Implementation)
**Status:** API exists, queue system not implemented
**Priority:** HIGH
**Estimated Time:** 10-12 hours
**Blocker:** No (Tier 1+ feature)

**Tasks:**
- [ ] Export queue system (queue.json, retry logic)
- [ ] Boot-time export service (d3kos-export.service)
- [ ] Daily cron job (Tier 2+)
- [ ] Export all 8 categories:
  - [ ] Engine benchmark data
  - [ ] Boatlog entries
  - [ ] Marine vision metadata (no image files)
  - [ ] QR code data
  - [ ] Settings configuration
  - [ ] System alerts
  - [ ] Marine vision snapshots metadata
  - [ ] Onboarding configuration (Tier 1 restore)
- [ ] Central database API endpoints
- [ ] Test export/import flow
- [ ] Documentation update

**Acceptance Criteria:**
- Tier 1+ can export all data to central database
- Boot-time export runs automatically
- Export queue with 3-attempt retry logic
- Tier 0 has NO export capability

---

#### 3. Boatlog Export Button
**Status:** Button exists but crashes
**Priority:** MEDIUM
**Estimated Time:** 2-3 hours
**Blocker:** No (UI issue)

**Tasks:**
- [ ] Debug boatlog export crash
- [ ] Implement CSV export functionality
- [ ] Test export with sample data
- [ ] Add download link after export
- [ ] Update UI to show export status

**Acceptance Criteria:**
- Export button downloads CSV file
- Includes all boatlog entries with timestamps
- No crashes or errors

---

#### 4. Charts Page (o-charts Plugin)
**Status:** OpenCPN installed, o-charts unavailable
**Priority:** LOW
**Estimated Time:** 4-6 hours (if plugin available)
**Blocker:** Yes (plugin not available for Debian Trixie ARM64)

**Tasks:**
- [ ] Research o-charts availability for Debian Trixie
- [ ] Alternative: OpenSeaMap free charts
- [ ] Alternative: NOAA free charts
- [ ] Document chart installation process
- [ ] Update Charts page with instructions

**Acceptance Criteria:**
- Charts page displays chart sources
- Instructions for installing free charts
- Links to OpenCPN chart catalog

---

#### 5. Forward Watch Implementation
**Status:** Datasets ready (54,789 images), not implemented
**Priority:** MEDIUM
**Estimated Time:** 20-30 hours
**Blocker:** No (new feature)

**Tasks:**
- [ ] Train YOLOv8-Marine model (8 classes)
  - [ ] People detection
  - [ ] Boats detection
  - [ ] Kayaks detection
  - [ ] Buoys detection
  - [ ] Logs detection
  - [ ] Debris detection
  - [ ] Docks detection
  - [ ] Ice/Icebergs detection
- [ ] Convert to ONNX format
- [ ] Create Signal K plugin (signalk-forward-watch)
- [ ] Integrate with Marine Vision camera stream
- [ ] Test detection accuracy
- [ ] Output NMEA2000 PGN 129038 (AIS-like hazard markers)
- [ ] Display on chartplotter
- [ ] Documentation

**Acceptance Criteria:**
- Real-time object detection at 5-10 FPS
- Hazards displayed on chartplotter
- Distance estimation working
- Signal K plugin published

---

### Medium Priority Features:

#### 6. Marine Vision Phase 2.2-2.5
**Status:** Phase 1 and 2.1 complete
**Priority:** MEDIUM
**Estimated Time:** 30-40 hours
**Blocker:** No (nice-to-have)

**Tasks:**
- [ ] Phase 2.2: Custom fish detection model
- [ ] Phase 2.3: Fish species identification
- [ ] Phase 2.4: Fishing regulations integration
- [ ] Phase 2.5: Advanced features (catch log, statistics)

**Acceptance Criteria:**
- Custom fish model trained and deployed
- Species ID with 80%+ accuracy
- Fishing regulations database integrated
- Catch log saved to database

---

#### 7. Engine Dashboard Live Data
**Status:** Dashboard exists, reads from static file
**Priority:** LOW
**Estimated Time:** 2-3 hours
**Blocker:** No (UI improvement)

**Tasks:**
- [ ] Update dashboard.html to read from Signal K WebSocket
- [ ] Remove static baseline.json dependency
- [ ] Add real-time updates (1 Hz)
- [ ] Test with real engine data

**Acceptance Criteria:**
- Dashboard shows live engine data
- Updates every 1 second
- No more static baseline.json file

---

#### 8. Network Status Labels Color Fix
**Status:** Labels not visible (black text on black background)
**Priority:** LOW
**Estimated Time:** 30 minutes
**Blocker:** No (cosmetic)

**Tasks:**
- [ ] Update settings-network.html CSS
- [ ] Change label color to white (#FFFFFF)
- [ ] Test visibility

**Acceptance Criteria:**
- Network status labels visible
- White text on dark background

---

### Low Priority / Future:

#### 9. E-Commerce Integration (Stripe Billing)
**Status:** Fully documented, not implemented
**Priority:** LOW (revenue-generating but requires 40-60 hours)
**Estimated Time:** 40-60 hours
**Blocker:** No (business feature)

**Tasks:**
- [ ] Backend development (Phase 2: 16-24 hours)
- [ ] Mobile app integration (Phase 3: 12-18 hours)
- [ ] Testing (Phase 4: 8-12 hours)
- [ ] Production deployment

**Acceptance Criteria:**
- Users can purchase Tier 2/3 subscriptions
- Stripe, Apple IAP, Google Play working
- Failed payment grace period (24 days)
- Automatic tier upgrades

---

## 📊 Version 0.9.2 Priorities

### Must-Have (Blocker for v0.9.2 Release):
1. ⚠️ **Voice Assistant Wake Word Detection** - CRITICAL FIX

### Should-Have (Important but not blocking):
2. Data Export System (complete implementation)
3. Boatlog Export Button
4. Forward Watch Implementation

### Nice-to-Have (Can be deferred to v0.9.3):
5. Charts Page (o-charts or free charts)
6. Marine Vision Phase 2.2-2.5
7. Engine Dashboard Live Data
8. Network Status Labels Color Fix
9. E-Commerce Integration

---

## 🎯 Release Criteria for v0.9.2

**Must Pass:**
- ✅ All Tier 0 features working (basic functionality)
- ✅ All Tier 1 features working (mobile app pairing, config restore)
- ✅ All Tier 2 features working (voice assistant, camera, data export)
- ✅ All Tier 3 features working (cloud sync, multi-boat)
- ✅ Voice assistant wake word detection fixed
- ✅ No critical bugs from field testing
- ✅ Documentation complete
- ✅ Installation guide updated

**Nice to Pass:**
- Forward Watch implemented and tested
- Data export system fully functional
- Boatlog export working
- Charts page with free chart sources

---

## 📅 Estimated Timeline

| Phase | Duration | Tasks |
|-------|----------|-------|
| **Phase 1: Critical Fixes** | 1 week | Voice assistant wake word detection |
| **Phase 2: Core Features** | 2 weeks | Data export system, boatlog export |
| **Phase 3: Forward Watch** | 3 weeks | Training, implementation, testing |
| **Phase 4: Polish** | 1 week | UI fixes, documentation |
| **Total** | **7 weeks** | **v0.9.2 Release** |

**Target Release:** End of March 2026

---

## 🐛 Known Issues Carried Forward

From PROBLEMS_AND_RESOLUTIONS.md:

1. ⚠️ **Voice Assistant** - Wake word detection not working (CRITICAL)
2. ❌ **WiFi Hotspot** - Not supported (hardware limitation, documented)
3. ℹ️ **Alternative Hardware** - Moitessier HAT, 12MHz CAN (documented)

---

## 📝 Version Numbers Explained

- **0.9.x** = Beta phase (feature development + testing)
- **0.9.1.x** = Patch releases (bug fixes only)
- **0.9.2** = Next feature release (bug fixes + new features)
- **1.0.0** = First stable release (all core features complete + tested)

**Current:** 0.9.1.2 (last patch release)
**Next:** 0.9.2 (feature release with bug fixes)
**Future:** 1.0.0 (stable release, estimated Q2 2026)

---

## 🔗 Related Documentation

- **Current Version:** `MASTER_SYSTEM_SPEC.md` v3.8
- **Bug Fixes:** `doc/BUGFIX_SYSSTAT_HARDWARE_CONFIG.md`
- **Problems Log:** `doc/PROBLEMS_AND_RESOLUTIONS.md`
- **Forward Watch:** `doc/forward-watch/FORWARD_WATCH_SPECIFICATION.md`
- **Architecture:** `doc/architecture.md`

---

**Version:** 1.0
**Created:** 2026-02-26
**Status:** DRAFT - Ready for Development
**Next Review:** After v0.9.2 Release
