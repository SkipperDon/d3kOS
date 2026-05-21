# Entity: d3k-lite

*Last updated: S85 2026-05-20 | Sources: feasibility.md, MEMORY.md S78*

---

## Status

**CONCEPT ONLY — no code written.** Feasibility study complete (1,261 lines). Interest gauge article drafted but not yet posted (DL-1 pending). Build conditional on community validation.

---

## What It Is

Free `.deb` addon for OpenPlotter users. Wraps the existing OpenPlotter stack (Signal K, AvNav) with the d3kOS dashboard, Gemini AI assistant, Windy weather, and Fix My Pi diagnostics — without requiring a full d3kOS installation.

---

## Key Design Decisions

- **Not a replacement** for OpenPlotter's core services — wraps them
- **70% code reuse** from d3kOS (path/port/env-var changes only)
- **Flask on port 8085** (not 8080 to avoid AvNav conflict, not 3000 to avoid Signal K conflict)
- **Python 3.11 venv** on Bookworm
- **Systemd services** — same pattern as d3kOS
- **No changes to OpenPlotter's core** — Signal K, AvNav, Node-RED untouched

## Features

- Turnkey kiosk dashboard
- Live instruments (Signal K data)
- AvNav chart integration
- Gemini AI assistant
- Windy weather embed
- Fix My Pi diagnostics + automated repairs
- Mobile companion (QR pairing — same as d3kOS v0.9.4)

## Target Audience

OpenPlotter users who want the d3kOS dashboard + AI + mobile features without building the full d3kOS system from scratch.

## Upgrade Path

d3k-lite users can migrate to full d3kOS later with the same AtMyBoat.com account.

## Estimated Build

~25 hours across 4–5 sessions. Pending community validation before Phase 1 approval.

## Key Documents

- Feasibility study: `/home/boatiq/feasibility.md` (1,261 lines)
- Interest gauge article: drafted, at `DL-1` in PROJECT_CHECKLIST.md

## Open Items (PROJECT_CHECKLIST.md)

| # | Item | Status |
|---|------|--------|
| DL-1 | Interest gauge article — post to forum | `[~]` Awaiting user post |
| DL-3 | Community feedback | `[ ]` Blocked on DL-1 |
| DL-4 | Phase 1 build approval | `[ ]` Blocked on DL-3 |

## Related

- [[entities/d3kos-platform]] — d3k-lite is a subset of d3kOS functionality
- [[entities/pi-system]] — same RPi target hardware
