# Concept: AIS Isolation

*Last updated: S85 2026-05-20 | Sources: SafeHelm design, S85 discussion with adam-gol*

---

## The Problem

SafeHelm injects synthetic vessel targets into Signal K (virtual MMSIs 998xxxxxx/999xxxxxx) for non-AIS contacts detected by camera or WiBoat. Signal K stores these as real vessel entries — identical structure to live AIS targets.

If Signal K has any N2K output configured, synthetic vessels can exit as PGN 129038/129039 onto the N2K bus, be picked up by the AIS transponder, and re-broadcast on VHF. **This is an ITU violation and operationally dangerous** (fake vessels appear on other boats' charts).

---

## Four Isolation Layers

### Layer 1 — transmitPGNs whitelist (hard gate)

In Signal K `settings.json`, the canboat-js provider must have an **explicit whitelist** of own-vessel sensor PGNs. AIS vessel PGNs must not appear.

```json
{
  "type": "@signalk/signalk-to-nmea2000",
  "options": {
    "transmitPGNs": [127250, 128267, 129025, 129026, 127245, 128259, 130306]
  }
}
```

Safe PGNs: 127250 (heading), 128267 (depth), 129025 (own position), 129026 (own COG/SOG), 127245 (rudder), 128259 (speed through water), 130306 (wind).

Never include: 129038, 129039, 129040, 129041 (AIS vessel traffic).

### Layer 2 — source tagging

Write all synthetic contacts with a source label in the Signal K delta:

```python
delta = {
    "context": f"vessels.urn:mrn:imo:mmsi:{virtual_mmsi}",
    "updates": [{
        "source": {"label": "safehelm.virtual", "type": "synthetic"},
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "values": [
            {"path": "navigation.position", "value": {"latitude": lat, "longitude": lon}},
            {"path": "navigation.courseOverGroundTrue", "value": cog_rad},
            {"path": "navigation.speedOverGround", "value": sog_ms}
        ]
    }]
}
ws.send(json.dumps(delta))
```

Any output provider can filter by `safehelm.virtual` as a defense-in-depth measure.

### Layer 3 — NMEA 0183 output filtering

If Signal K has any TCP or serial NMEA 0183 output configured, exclude `!AIVDM` and `!AIVDO` from the sentence whitelist.

### Layer 4 — virtual MMSI range

998xxxxxx and 999xxxxxx are outside ITU-allocated MMSI space. Even if a synthetic target leaks, it won't impersonate a real vessel and GMDSS stations will reject it as malformed.

---

## Current d3kOS State

Layer 1 is **implicit** (no vessel PGN output is currently configured) but **not an explicit verified whitelist**. Making it explicit is a hard gate before SafeHelm Phase 1 ships (checklist item SH-15).

---

## Related

- [[entities/safehelm]] — the system that creates synthetic AIS contacts
- [[entities/nmea2000-layer]] — the N2K output path that must be protected
- [[entities/wiboat]] — source of 998xxxxxx contacts
