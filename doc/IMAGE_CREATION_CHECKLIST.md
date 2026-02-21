# d3kOS v0.9.1.2 Image Creation - Quick Checklist

**Print this page and check off items as you complete them**

---

## ☐ Phase 1: Prepare Pi (30 min)

- [ ] SSH into Pi: `ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237`
- [ ] Clear temp files: `sudo rm -rf /tmp/* /var/tmp/*`
- [ ] Clear cache: `sudo rm -rf /home/d3kos/.cache/*`
- [ ] Clean journals: `sudo journalctl --vacuum-time=7d`
- [ ] Clean APT: `sudo apt-get clean && sudo apt-get autoclean`
- [ ] Verify tier 3: `curl http://localhost:8093/tier/status | jq '.tier'`
- [ ] Check services: `systemctl --user list-units 'd3kos-*'`
- [ ] Create image info: `/boot/firmware/d3kos-image-info.txt`
- [ ] Shutdown: `sudo shutdown -h now`
- [ ] Remove SD card from Pi

---

## ☐ Phase 2: Create Image (45 min)

- [ ] Insert SD card in reader
- [ ] Identify device: `lsblk` (note device name: ______)
- [ ] Create working directory: `mkdir -p ~/d3kOS-images/v0.9.1.2 && cd ~/d3kOS-images/v0.9.1.2`
- [ ] Create raw image: `sudo dd if=/dev/[DEVICE] of=d3kos-v0.9.1.2-raw.img bs=4M status=progress conv=fsync`
- [ ] Wait ~15-20 minutes for 16GB copy
- [ ] Shrink image (follow detailed steps in main guide)
- [ ] Compress: `gzip -9 -c d3kos-v0.9.1.2-raw.img > d3kos-v0.9.1.2.img.gz`
- [ ] Wait ~5-10 minutes for compression
- [ ] Check size: `ls -lh d3kos-v0.9.1.2.img.gz` (expect ~3.2 GB)
- [ ] Generate SHA-256: `sha256sum d3kos-v0.9.1.2.img.gz > d3kos-v0.9.1.2.img.gz.sha256`
- [ ] Generate MD5: `md5sum d3kos-v0.9.1.2.img.gz > d3kos-v0.9.1.2.img.gz.md5`
- [ ] Create release notes (follow template in main guide)

**Checksum**: ______________________________________________ (write it here)

---

## ☐ Phase 3: Test Image (60 min) **DO NOT SKIP**

- [ ] Decompress test copy: `gunzip -c d3kos-v0.9.1.2.img.gz > d3kos-v0.9.1.2-test.img`
- [ ] Get different SD card for testing (16GB min)
- [ ] Flash test: `sudo dd if=d3kos-v0.9.1.2-test.img of=/dev/[TEST_DEVICE] bs=4M status=progress`
- [ ] Insert test SD in Pi and boot
- [ ] Wait 60 seconds
- [ ] Verify Chromium loads main menu
- [ ] Test buttons clickable
- [ ] Test Settings → Network Settings
- [ ] Connect to WiFi successfully
- [ ] SSH into test Pi: `ssh d3kos@[TEST_IP]`
- [ ] Check services: `systemctl --user list-units 'd3kos-*' | grep running`
- [ ] Check tier: `curl http://localhost:8093/tier/status`
- [ ] Check ID: `curl http://localhost:8091/license/info`
- [ ] Reboot test #1: `sudo reboot` → wait 2 min → check services
- [ ] Reboot test #2: `sudo reboot` → wait 2 min → check services
- [ ] Reboot test #3: `sudo reboot` → wait 2 min → check services
- [ ] Verify no "Restore pages?" prompt after any reboot

**Test Result**: ☐ PASS  ☐ FAIL (if fail, stop and fix)

---

## ☐ Phase 4: Upload to Google Drive (30 min)

- [ ] Install gdrive CLI or use browser
- [ ] Upload `d3kos-v0.9.1.2.img.gz` (3.2 GB, ~15-30 min)
- [ ] Upload `d3kos-v0.9.1.2.img.gz.sha256`
- [ ] Upload `d3kos-v0.9.1.2.img.gz.md5`
- [ ] Upload `d3kos-v0.9.1.2-RELEASE_NOTES.txt`
- [ ] Set sharing: Anyone with link → Viewer
- [ ] Copy shareable link

**Google Drive Link**: ______________________________________________ (write it here)

---

## ☐ Phase 5: GitHub Release (20 min)

- [ ] Navigate to repo: `cd ~/Helm-OS`
- [ ] Check status: `git status`
- [ ] Stage changes: `git add README.md MASTER_SYSTEM_SPEC.md doc/IMAGE_CREATION_*.md`
- [ ] Commit with message (see main guide)
- [ ] Push: `git push origin main`
- [ ] Go to GitHub: https://github.com/SkipperDon/d3kOS/releases
- [ ] Click "Draft a new release"
- [ ] Tag: `v0.9.1.2`
- [ ] Title: `d3kOS v0.9.1.2 - Testing Build`
- [ ] Description: Paste release notes
- [ ] Upload 4 files from `~/d3kOS-images/v0.9.1.2/`
- [ ] Check "This is a pre-release"
- [ ] Click "Publish release"
- [ ] Update README.md with Google Drive link (replace PLACEHOLDER)
- [ ] Commit and push README update

**GitHub Release URL**: ______________________________________________ (verify it here)

---

## ☐ Phase 6: Verify Downloads (15 min)

- [ ] Test GitHub download: `wget https://github.com/SkipperDon/d3kOS/releases/download/v0.9.1.2/d3kos-v0.9.1.2.img.gz`
- [ ] Test checksum: `sha256sum -c d3kos-v0.9.1.2.img.gz.sha256`
- [ ] Verify: Output shows "OK"
- [ ] Test Google Drive download
- [ ] Compare checksums match
- [ ] Verify README instructions work
- [ ] Test "Quick Start" section with fresh SD card

**Download Verification**: ☐ PASS  ☐ FAIL

---

## ☐ Cleanup

- [ ] Delete raw image: `rm d3kos-v0.9.1.2-raw.img`
- [ ] Delete test image: `rm d3kos-v0.9.1.2-test.img`
- [ ] Keep: .img.gz, .sha256, .md5, RELEASE_NOTES.txt
- [ ] Backup files to external drive (optional but recommended)

---

## Final File List

```
~/d3kOS-images/v0.9.1.2/
├── d3kos-v0.9.1.2.img.gz           (3.2 GB)
├── d3kos-v0.9.1.2.img.gz.sha256    (< 1 KB)
├── d3kos-v0.9.1.2.img.gz.md5       (< 1 KB)
└── d3kos-v0.9.1.2-RELEASE_NOTES.txt (5 KB)

Total: ~3.2 GB
```

---

## Time Tracking

| Phase | Estimated | Started | Completed | Actual |
|-------|-----------|---------|-----------|--------|
| 1. Prepare | 30 min | ___:___ | ___:___ | _____ |
| 2. Create | 45 min | ___:___ | ___:___ | _____ |
| 3. Test | 60 min | ___:___ | ___:___ | _____ |
| 4. Upload | 30 min | ___:___ | ___:___ | _____ |
| 5. GitHub | 20 min | ___:___ | ___:___ | _____ |
| 6. Verify | 15 min | ___:___ | ___:___ | _____ |
| **Total** | **200 min** | | | **_____** |

---

## Emergency Contacts

- GitHub Issues: https://github.com/SkipperDon/d3kOS/issues
- Documentation: https://github.com/SkipperDon/d3kOS
- Community: AtMyBoat.com forums

---

**⚠️ IMPORTANT**: Do not skip Phase 3 testing! A broken image wastes everyone's time.

**📋 Print Date**: ________________
**👤 Created By**: ________________
**✅ Completed**: ☐ YES  ☐ NO

---

**This checklist is a companion to IMAGE_CREATION_GUIDE_v0.9.1.2.md**
**Refer to the full guide for detailed commands and troubleshooting**
