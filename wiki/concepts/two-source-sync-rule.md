# Concept: Two-Source Sync Rule

*Last updated: S62 2026-04-17 | Sources: MEMORY.md, S52*

---

## The Rule

`deployment/d3kOS/dashboard/` and `deployment/v0.9.4/pi_source/` are BOTH authoritative sources for the Pi.

Any new file added to one MUST be added to the other AND deployed to the Pi.

## Why This Exists

Discovered S52 (2026-04-08): Anchor Watch + Manual pages were missing from `d3kOS/dashboard/` since they were added in S39b/S41. They existed in `v0.9.4/pi_source/` but not the other directory. The violation was undetected for multiple sessions.

## Enforcement

Before closing any session that adds a Pi file:

1. List the file path in both directories
2. Confirm both were updated
3. Confirm Pi deploy occurred

If either directory is missing the file: stop and sync before the session closes.

## Directories

| Directory | Role |
|-----------|------|
| `deployment/d3kOS/dashboard/` | Dashboard source — primary working copy |
| `deployment/v0.9.4/pi_source/` | Pi deployment source — must stay identical |

## Related

- [[entities/d3kos-platform]] — Two Source Directories section
