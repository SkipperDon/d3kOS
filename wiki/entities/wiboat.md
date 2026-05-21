# Entity: WiBoat

*Last updated: S85 2026-05-20 | Sources: WIBOAT_SAFEHELM_FRD_v1.1.md, WiBoat_BOM_v2.md, WIBOAT_SAFEHELM_INTEGRATED_ARCHITECTURE.md, MEMORY.md*

---

## Status

**DESIGN ONLY — no code written.** FRD v1.2 complete (S82). BOM v2.0 complete. Phase 1 hardware procurement pending operator action (WB-02).

---

## What It Is

WiFi CSI (Channel State Information) marine radar. Detects vessels that have no AIS and aren't on chart radar by analysing how boat hulls disturb WiFi radio signals. Feeds range/bearing contacts into SafeHelm's priority queue.

---

## Hardware (Phase 1)

| Component | Detail |
|-----------|--------|
| Host | Raspberry Pi 4B 4GB |
| OS | Raspbian Bullseye 32-bit, kernel 5.10 LOCKED (nexmon_csi requires 5.10 — do NOT apt upgrade) |
| CAN interface | None — WiBoat RPi 4B has no PiCAN-M. N2K is d3kOS RPi 5 only. |
| WiFi adapters | 2× ALFA AWUS036NH (TX injectors) |
| Antennas | 4× 12 dBi omni + SP4T GPIO-controlled RF switch (4-channel time-multiplexed CSI on BCM43455) |
| LoRa | Heltec V3 (Meshtastic) |
| Estimated cost | $565–$868 CAD |

**EIRP warning:** ALFA at full power + 12 dBi exceeds ISED 4W EIRP limit. Set TX power to 21 dBm max.

## Network

| Context | IP |
|---------|----|
| On-boat (10.42.0.x) | `10.42.0.2` (static, assign on boat router — WB-01 operator action) |
| LAN/dev | `192.168.1.x` (DHCP) |

`WIBOAT_HOST` env var switches between environments.

## Ports

| Service | Port |
|---------|------|
| WiBoat WebSocket | 8766 |
| WiBoat HTTP | 8767 |
| Meshtastic | 8768 |

## MMSI Registry

| Source | MMSI Range |
|--------|------------|
| Camera-only contacts | 999xxxxxx |
| WiBoat contacts | 998xxxxxx |
| WiBoat standalone | 970xxxxxx |
| LoRa | real node IDs |

## Key Documents

- FRD v1.2: `deployment/docs/wiboat/WIBOAT_SAFEHELM_FRD_v1.1.md`
- BOM v2.0: `deployment/docs/wiboat/WiBoat_BOM_v2.md` (**intentionally uncommitted** — Don still gathering BOM info)
- Architecture: `deployment/docs/wiboat/WIBOAT_SAFEHELM_INTEGRATED_ARCHITECTURE.md`

## Build Phases

| Phase | Key Deliverable | Hard Gate |
|-------|----------------|-----------|
| 1 | nexmon_csi range-only, 5 acceptance gates (G1.1–G1.5) | All 5 gates pass |
| 2 | 4-antenna bearing (MUSIC AoA), advisory + WiBoat CPA integration, sea trial | ±15° at 100m; zero false CRITICAL alarms |
| 3 | Full-quadrant validation, batman-adv mesh | Phase 2 sea trial complete |
| 4 | Single-box consolidation to RPi 5, autopilot | One full sailing season in Phase 2 advisory mode (G3.5 — hard calendar gate) |

## Operator Actions Required

- **WB-01**: assign `10.42.0.2` to WiBoat on boat router; confirm RPi 5 on-boat IP (placeholder `10.42.0.1`)
- **WB-02**: procure Phase 1 hardware per BOM v2.0

## Related

- [[entities/safehelm]] — SafeHelm consumes WiBoat contacts via WebSocket :8766
- [[entities/nmea2000-layer]] — N2K is on d3kOS RPi 5 only, not WiBoat RPi 4B
- [[entities/pi-system]] — d3kOS host; WiBoat is a separate box until Phase 4
