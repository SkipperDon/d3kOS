#!/bin/bash
# Update skills.md on d3kOS Raspberry Pi with project management section
# Run this from a machine that can reach the Pi (192.168.1.237)

echo "Updating /opt/d3kos/config/skills.md on Pi..."

ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237 'cat >> /opt/d3kos/config/skills.md' << 'EOF'

## Project Management & Roadmap

### Version Roadmap
- Current Version: v0.9.1.2
- Target Version: v1.0.0 (February 2028)
- Total Timeline: 122 weeks (~28 months)
- Current Priority: v0.9.2 (Metric/Imperial - 3 weeks)
- Next Priority: v0.9.3 (4-Camera System - 8-9 weeks)

### Immediate Implementations
1. v0.9.2 - Metric/Imperial Conversion (March 2026, 3 weeks)
   - Auto-default based on boat origin
   - Imperial: USA, Canada
   - Metric: Europe, Asia, Oceania, Africa, South America
   - Conversions: Temperature, Pressure, Speed, Distance, Depth, Fuel, Length, Weight, Displacement

2. v0.9.3 - Multi-Camera System (April 2026, 8-9 weeks)
   - 4 cameras: Bow (Forward Watch), Stern, Interior, Port/Starboard
   - Hybrid UI: Single View + Grid View
   - Forward Watch obstacle avoidance (YOLOv8)
   - Resource: 970 MB RAM, 25-35% CPU, 8-12 Mbps bandwidth

### Pre-v1.0 Requirements
- v0.15.0 - Multi-Language Support (8 languages: English, French, Spanish, German, Italian, Dutch, Swedish, Norwegian)
- v0.16.0 - Security Audit (Zero critical/high vulnerabilities, penetration testing, GDPR/CCPA compliance)

### Development Tracking
- Project Checklist: /home/boatiq/Helm-OS/PROJECT_CHECKLIST.md
- Roadmap Document: /home/boatiq/Helm-OS/doc/D3KOS_VERSION_ROADMAP_2026.md (v1.3)
- All tasks tracked with verification status
- Update checklist on every commit

### Critical Path to v1.0
1. v0.9.2 (Metric/Imperial) → NEXT
2. v0.9.3 (4-Camera) → HIGH PRIORITY
3. v0.9.4-0.14.0 (Features) → 94 weeks
4. v0.15.0 (Multi-Language) → REQUIRED
5. v0.16.0 (Security Audit) → REQUIRED
6. v1.0.0 (Production) → February 2028

### Checklist Update Protocol
**IMPORTANT:** Update PROJECT_CHECKLIST.md on every commit

Status codes:
- [ ] Not Started
- [🔄] In Progress
- [✅] Complete (verified working)
- [⚠️] Blocked (add comment)
- [🔍] Verification Needed (add <!-- VERIFY: issue -->)
- [❌] Not Working (add <!-- NOT WORKING: description -->)

When starting task: [ ] → [🔄]
When completing task: [🔄] → [✅] (after testing)
When issue found: → [🔍] or [❌] + add comment

Example commit:
```
feat(v0.9.2): Add temperature conversion + update checklist

- Implemented °F ↔ °C in units.js
- Updated dashboard display
- PROJECT_CHECKLIST.md: [✅] Temperature conversion complete
```

### Version Status Summary
- v0.9.1.2: Current (Beta - Lake Simcoe testing)
- v0.9.2: Next (3 weeks) - Metric/Imperial
- v0.9.3: Immediate (8-9 weeks) - 4-Camera System
- v0.9.4: Planned (5-7 weeks) - Gemini API
- v0.9.5: Planned (8-10 weeks) - Mobile Apps
- v0.9.6: Planned (6-8 weeks) - Remote Access
- v0.10.0-v0.14.0: Feature development (94 weeks)
- v0.15.0: Required (6-8 weeks) - Multi-Language
- v0.16.0: Required (4 weeks) - Security Audit
- v1.0.0: Production (February 2028)

### Resources
- Full Roadmap: /home/boatiq/Helm-OS/doc/D3KOS_VERSION_ROADMAP_2026.md (v1.3, 122 weeks)
- Task Checklist: /home/boatiq/Helm-OS/PROJECT_CHECKLIST.md (645 lines, 500+ tasks)
- Metric/Imperial Plan: /home/boatiq/Helm-OS/doc/METRIC_IMPERIAL_IMPLEMENTATION_PLAN.md (42KB)
- Multi-Camera Plan: /home/boatiq/Helm-OS/doc/MULTI_CAMERA_IMPLEMENTATION_PLAN.md (50KB)
- Language Plan: /home/boatiq/Helm-OS/doc/LANGUAGE_SELECTION_SPECIFICATION.md (26KB)

EOF

echo "✅ skills.md updated successfully!"
echo "Verify by running: ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237 'tail -50 /opt/d3kos/config/skills.md'"
