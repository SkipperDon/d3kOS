# GitHub Release Template for d3kOS

**Purpose**: This template provides a standardized format for creating GitHub releases.

**Usage**: Copy this template when creating a new release on GitHub.

---

## Release Title Format

```
d3kOS v[VERSION] - [ONE-LINE SUMMARY]
```

**Examples**:
- `d3kOS v1.0.3 - Installation ID System, Tier Licensing, Data Export`
- `d3kOS v1.0.4 - Voice Assistant Fix, Boatlog Export Fix`
- `d3kOS v2.0.0 - Major UI Redesign, Raspberry Pi 5 Support`

---

## Release Description Template

```markdown
# d3kOS v[VERSION] Release

**Release Date**: [YYYY-MM-DD]
**Previous Version**: [PREVIOUS_VERSION]

---

## 📦 Downloads

**⚠️ ALWAYS VERIFY CHECKSUM BEFORE FLASHING**

| File | Size | Purpose |
|------|------|---------|
| [d3kos-v[VERSION].img.gz](https://github.com/SkipperDon/d3kos/releases/download/v[VERSION]/d3kos-v[VERSION].img.gz) | ~4GB | Main system image (compressed) |
| [d3kos-v[VERSION].img.gz.sha256](https://github.com/SkipperDon/d3kos/releases/download/v[VERSION]/d3kos-v[VERSION].img.gz.sha256) | 128 bytes | SHA-256 checksum |
| [d3kos-v[VERSION].img.gz.md5](https://github.com/SkipperDon/d3kos/releases/download/v[VERSION]/d3kos-v[VERSION].img.gz.md5) | 64 bytes | MD5 checksum (legacy) |

**Verify Checksum**:
```bash
sha256sum -c d3kos-v[VERSION].img.gz.sha256
# Expected: d3kos-v[VERSION].img.gz: OK
```

---

## 🎯 What's New

### [FEATURE_1_TITLE]

[2-3 sentence description of feature]

**Key Benefits**:
- [Benefit 1]
- [Benefit 2]
- [Benefit 3]

---

### [FEATURE_2_TITLE]

[2-3 sentence description of feature]

**Key Benefits**:
- [Benefit 1]
- [Benefit 2]

---

## ⚠️ Breaking Changes

[IF ANY - List breaking changes with impact and migration steps]

**Example**:
### 1. Installation ID Format Changed

**Impact**: Old installation IDs discarded, new 16-char hex ID generated.

**Action Required**:
- Re-pair mobile app (scan new QR code)
- OR restore configuration from backup

---

## 🐛 Bug Fixes

- Fixed [BUG_1_DESCRIPTION] (#ISSUE_NUMBER)
- Fixed [BUG_2_DESCRIPTION] (#ISSUE_NUMBER)
- Fixed [BUG_3_DESCRIPTION]

---

## 📈 Performance Improvements

- [IMPROVEMENT_1]: [X]× faster (was [OLD_TIME], now [NEW_TIME])
- [IMPROVEMENT_2]: [Y] MB storage freed
- [IMPROVEMENT_3]: [Z]% less CPU usage

---

## 🐛 Known Issues

### 1. [ISSUE_TITLE] (CRITICAL/HIGH/MEDIUM/LOW)

**Status**: [Under investigation / Fix in progress / Workaround available]
**Affected**: [All users / Tier X users / Specific hardware]
**Tracking**: #ISSUE_NUMBER (if applicable)

**Workaround**:
- [Workaround step 1]
- [Workaround step 2]

**ETA**: [Version X.X.X / Unknown / Under investigation]

---

## 🔧 Upgrade Instructions

### Tier 0/1 Users (SD Card Swap ONLY)

1. Download `d3kos-v[VERSION].img.gz`
2. Verify checksum
3. Flash to spare SD card using Raspberry Pi Imager
4. Swap SD cards
5. Complete Initial Setup wizard (or restore from backup)

**See**: [UPGRADE_GUIDE.md](https://github.com/SkipperDon/d3kos/blob/main/doc/distribution/UPGRADE_GUIDE.md)

---

### Tier 2/3 Users (In-Place Upgrade)

**Option 1: Via Mobile App**
1. Open d3kOS mobile app
2. Settings → Software Update → Check for Updates
3. Tap "Download and Install"
4. Wait 10-15 minutes for download + install + reboot

**Option 2: Via Web Interface**
1. Navigate to Settings → System → Software Update
2. Click "Check for Updates"
3. Click "Download and Install"
4. Wait for reboot

**Option 3: Via SSH** (Advanced)
```bash
cd /tmp
wget https://github.com/SkipperDon/d3kos/releases/download/v[VERSION]/d3kos-upgrade-v[VERSION].tar.gz
sha256sum -c d3kos-upgrade-v[VERSION].tar.gz.sha256
sudo /opt/d3kos/scripts/upgrade.sh /tmp/d3kos-upgrade-v[VERSION].tar.gz
```

---

## 📚 Documentation

**New/Updated Docs**:
- [DOCUMENT_1_TITLE](link)
- [DOCUMENT_2_TITLE](link)
- [DOCUMENT_3_TITLE](link)

**Quick Links**:
- [README](https://github.com/SkipperDon/d3kos/blob/main/doc/distribution/README.md)
- [Installation Guide](https://github.com/SkipperDon/d3kos/blob/main/doc/distribution/INSTALLATION_GUIDE.md)
- [Troubleshooting](https://github.com/SkipperDon/d3kos/blob/main/doc/distribution/TROUBLESHOOTING_GUIDE.md)
- [Changelog](https://github.com/SkipperDon/d3kos/blob/main/doc/distribution/CHANGELOG.md)

---

## 📊 Release Statistics

| Metric | Value |
|--------|-------|
| **Image Size** | ~4GB (compressed), ~16GB (uncompressed) |
| **Services** | [NUMBER] d3kOS services |
| **API Endpoints** | [NUMBER] total |
| **Lines of Code** | [NUMBER] (estimated) |
| **Documentation** | [NUMBER] pages, [NUMBER] words |
| **Third-Party Packages** | [NUMBER] licenses |

---

## 🙏 Acknowledgments

- Signal K Project for marine data standards
- Node-RED community for automation platform
- OpenCPN project for chart plotting software
- Anthropic for Claude AI development assistance
- Raspberry Pi Foundation for affordable computing
- **Beta Testers**: [LIST_BETA_TESTERS]
- **Contributors**: [LIST_CONTRIBUTORS]

---

## 📞 Support

**Community**:
- [GitHub Discussions](https://github.com/SkipperDon/d3kos/discussions) - Q&A and feature requests
- [GitHub Issues](https://github.com/SkipperDon/d3kos/issues) - Bug reports only
- [At My Boat](https://atmyboat.com) - Blog, stories, guides

**Commercial**:
- Tier 3: Direct email support (24-hour response)
- Tier 2: Priority GitHub response (48 hours)
- Tier 0/1: Community support

---

## 🔐 Security

**Default Credentials** (CHANGE IMMEDIATELY):
- System User: `d3kos` / `d3kos2026`
- SSH Access: `d3kos` / `d3kos2026`
- WiFi AP: SSID `d3kOS` / `d3kos-2026`

**Change password after first login**: `passwd`

---

## 📄 License

- **d3kOS Core**: MIT License
- **Third-Party Components**: Various (see [LICENSE.txt](https://github.com/SkipperDon/d3kos/blob/main/doc/distribution/LICENSE.txt))

**IMPORTANT**: YOLOv8 component licensed under AGPL-3.0. Network service provision requires releasing modifications under AGPL-3.0.

---

## 🚀 What's Next?

**Planned for v[NEXT_VERSION]** ([MONTH YEAR]):
- [PLANNED_FEATURE_1]
- [PLANNED_FEATURE_2]
- [PLANNED_FEATURE_3]

**Roadmap**: See [ROADMAP.md](https://github.com/SkipperDon/d3kos/blob/main/ROADMAP.md) (if exists)

---

**Happy Boating! ⚓**

**d3kOS v[VERSION]** - Marine Helm Control System
Released [YYYY-MM-DD]
Maintained by SkipperDon (https://atmyboat.com)
```

---

## 🔧 Creating a Release (Step-by-Step)

### 1. Prepare Release Files

```bash
# Create image
dd if=/dev/mmcblk0 of=/mnt/usb/d3kos-v1.0.X.img bs=4M status=progress

# Compress
gzip -9 /mnt/usb/d3kos-v1.0.X.img

# Generate checksums
sha256sum /mnt/usb/d3kos-v1.0.X.img.gz > /mnt/usb/d3kos-v1.0.X.img.gz.sha256
md5sum /mnt/usb/d3kos-v1.0.X.img.gz > /mnt/usb/d3kos-v1.0.X.img.gz.md5
```

### 2. Create Git Tag

```bash
# Tag release
git tag -a v1.0.X -m "d3kOS v1.0.X - [ONE-LINE SUMMARY]"

# Push tag
git push origin v1.0.X
```

### 3. Create GitHub Release

1. Go to: https://github.com/SkipperDon/d3kos/releases/new
2. Choose tag: `v1.0.X`
3. Release title: `d3kOS v1.0.X - [ONE-LINE SUMMARY]`
4. Description: Copy template above, fill in placeholders
5. Attach files:
   - `d3kos-v1.0.X.img.gz`
   - `d3kos-v1.0.X.img.gz.sha256`
   - `d3kos-v1.0.X.img.gz.md5`
6. Check "Set as the latest release" (if applicable)
7. Click "Publish release"

### 4. Announce Release

**GitHub Discussions**:
- Post announcement in "Announcements" category
- Include release notes link
- Tag active community members

**At My Boat Blog**:
- Write blog post about major features
- Include installation instructions
- Add photos/videos if available

**Social Media** (if applicable):
- Twitter/X: Short announcement with link
- Reddit: Post in relevant boating/marine subreddits
- Forums: Marine electronics forums, Raspberry Pi forums

---

## 📝 Release Checklist

**Pre-Release**:
- [ ] Version number updated in `/opt/d3kos/version.txt`
- [ ] CHANGELOG.md updated with all changes
- [ ] RELEASE_NOTES_vX.X.X.md created
- [ ] Documentation updated (README, guides)
- [ ] Breaking changes clearly documented
- [ ] Known issues listed
- [ ] All tests passing (boot, services, web interface)
- [ ] Backup configuration verified
- [ ] Upgrade path tested (SD card swap + in-place)

**Release Creation**:
- [ ] Image created and compressed
- [ ] Checksums generated (SHA-256 + MD5)
- [ ] Git tag created and pushed
- [ ] GitHub release created
- [ ] Files uploaded (image + checksums)
- [ ] Release description filled (template)
- [ ] "Latest release" checkbox set (if applicable)
- [ ] Release published

**Post-Release**:
- [ ] GitHub Discussions announcement posted
- [ ] At My Boat blog post published (optional)
- [ ] Community notified (forums, social media)
- [ ] Download links verified (working)
- [ ] Checksum verification tested
- [ ] Installation guide tested by fresh user
- [ ] Support channels monitored (first 48 hours)

---

## 🎯 Release Naming Convention

**Format**: `v[MAJOR].[MINOR].[PATCH]`

**Examples**:
- `v1.0.0` - Initial release
- `v1.0.1` - Patch release (bug fixes)
- `v1.1.0` - Minor release (new features, backwards-compatible)
- `v2.0.0` - Major release (breaking changes)

**Pre-Releases**:
- `v1.1.0-beta.1` - Beta release (feature complete, testing)
- `v1.1.0-rc.1` - Release candidate (final testing before release)
- `v1.1.0-alpha.1` - Alpha release (early testing, unstable)

---

## 📌 Template Variables Reference

| Variable | Example | Description |
|----------|---------|-------------|
| `[VERSION]` | `1.0.3` | Semantic version number |
| `[YYYY-MM-DD]` | `2026-02-18` | Release date |
| `[PREVIOUS_VERSION]` | `1.0.2` | Previous version number |
| `[ONE-LINE SUMMARY]` | `Installation ID System, Tier Licensing` | Brief feature summary |
| `[FEATURE_N_TITLE]` | `Installation ID System` | Feature section title |
| `[BUG_N_DESCRIPTION]` | `GPS position not displaying` | Bug fix description |
| `#ISSUE_NUMBER` | `#42` | GitHub issue number |
| `[NEXT_VERSION]` | `1.0.4` | Next planned version |
| `[MONTH YEAR]` | `March 2026` | Planned release month |

---

**Template Version**: 1.0.0
**Last Updated**: February 18, 2026
**Maintainer**: SkipperDon (https://atmyboat.com)
