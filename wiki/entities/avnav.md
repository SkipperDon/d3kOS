# Entity: AvNav

*Last updated: S86 2026-05-21 | Sources: MEMORY.md, safehelm entity, d3kos-platform port registry*

---

## Identity

- **Type:** Chart navigation software on Pi
- **Port:** 8080
- **Fallback:** 9876/UDP
- **Status:** Running as part of d3kOS stack

---

## What It Does

Chart display and navigation software integrated into the d3kOS dashboard. Visible as a live chart pane on the dashboard home page. Receives NMEA data from Signal K and displays vessel position, AIS traffic, and (when SafeHelm ships) virtual vessel contacts.

---

## SafeHelm Integration (pending Phase 1)

SafeHelm uses AvNav as its chart display layer for collision avoidance overlays:

**Virtual vessel injection:**
SafeHelm injects synthetic AIS contacts via NMEA TCP → they appear as native triangle targets on the AvNav chart (same visual as real AIS vessels).

**Status widget:**
A User JS plugin at `~/avnav/user/plugins/` provides the SafeHelm status overlay (current COLREGs state, active alerts, EXECUTE button for advisories).

---

## d3k-lite Integration

d3k-lite (the OpenPlotter addon concept) wraps AvNav as its chart display layer. Same integration pattern as d3kOS — AvNav runs on port 8080, d3k-lite Flask runs on 8085 to avoid conflict.

---

## Related

- [[entities/safehelm]] — uses AvNav for chart display and virtual vessel injection
- [[entities/d3k-lite]] — wraps AvNav as its chart integration
- [[entities/d3kos-platform]] — AvNav is part of the d3kOS service stack
- [[entities/pi-system]] — host platform
