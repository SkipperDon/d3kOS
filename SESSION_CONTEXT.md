# Session Context — v0.9.2.1 d3kOS Build

**Branch:** `build-v0.9.2.1`
**Worktree:** `/home/boatiq/worktrees/v0.9.2.1/`
**Purpose:** Build d3kOS Flask-based marine dashboard (Phases 1–5).

## READ FIRST (in order)

1. `/home/boatiq/CLAUDE.md` — governing rules
2. `deployment/d3kOS/D3KOS_PLAN.md` — current phase + all implementation details
3. `deployment/d3kOS/PROJECT_CHECKLIST.md` — exact task state per phase
4. `deployment/d3kOS/SESSION_LOG.md` — last 3 entries for continuity

## Current Phase State

- **Phase 0:** COMPLETE 2026-03-12
- **Phase 1:** TODO — Pi menu restructure (requires Pi at 192.168.1.237)
- **Phase 2:** TODO — Flask dashboard at :3000
- **Phase 3:** TODO — Gemini AI proxy at :3001
- **Phase 4:** TODO — Settings page + docs
- **Phase 5:** TODO — AI + AvNav integration (spec at `deployment/d3kOS/docs/D3KOS_PHASE5_AI_AVNAV_INTEGRATION.md`)

**Start with Phase 2** (Flask local dev — no Pi needed, no blockers).
**Phase 1 is blocked** until Session 1 (close-v0.9.2) moves keyboard-api from port 8085 → 8086
and that change is merged to main. AvNav cannot be installed until port 8085 is free.
**Voice/query proxy migration** (switching :8097 → :3001) is blocked until Phase 3 is live on Pi.

## Key References

- UI mockup: `deployment/d3kOS/docs/d3kos-mockup-v4.html`
- Phase 5 spec: `deployment/d3kOS/docs/D3KOS_PHASE5_AI_AVNAV_INTEGRATION.md` (v1.1.0)
- AvNav install: `deployment/d3kOS/docs/AVNAV_INSTALL_AND_API.md`

## Branch Rules

- Work only in `deployment/d3kOS/` and governance files
- Do NOT touch v0.9.2 Pi HTML pages or existing services
- Do NOT touch `deployment/v0.9.3/`
- Commit to `build-v0.9.2.1` branch — do not push
- When a phase is done: run session-close, then tell Don to merge to main

## Merge When Done

```bash
# Don runs this in /home/boatiq/Helm-OS after each phase milestone:
git checkout main
git merge build-v0.9.2.1 --no-ff -m "merge: d3kOS Phase N complete"
# Then: git branch -d build-v0.9.2.1 && git branch build-v0.9.2.1 main
# (reset branch for next phase)
```
