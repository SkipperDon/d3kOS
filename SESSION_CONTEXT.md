# Session Context — v0.9.2 Close

**Branch:** `close-v0.9.2`
**Worktree:** `/home/boatiq/worktrees/v0.9.2/`
**Purpose:** Complete all remaining v0.9.2 open tasks and formally close the version.

## READ FIRST (in order)

1. `/home/boatiq/CLAUDE.md` — governing rules
2. `PROJECT_CHECKLIST.md` (Helm-OS root) — v0.9.2 remaining tasks
3. `SESSION_LOG.md` (Helm-OS root) — last 3 entries
4. `deployment/docs/DEPLOYMENT_INDEX.md` — know what exists

## DO FIRST — Unblocks Session 2

**Move keyboard-api.service from port 8085 → 8087** (Session 2 cannot install AvNav until this is done)
- 8086 is taken by fish_detector. 8087 is free.
- Update `keyboard-api.py`: change port 8085 → 8087
- Update nginx proxy_pass for keyboard-api block: `proxy_pass http://127.0.0.1:8087`
- Update `d3kos-keyboard-api.service` EnvironmentFile if port is set there
- Reload nginx, restart service, verify `/keyboard/show` and `/window/toggle` still work
- Commit to `close-v0.9.2` and tell Don to merge — unblocks Session 2 Phase 1

**Also check: port 8080 occupancy before AvNav install**
- Existing nginx config proxies `/query` → 8080 (AI query API, old v0.9.2 service)
- AvNav needs port 8080 to itself
- Run on Pi: `ss -tlnp | grep :8080`
- If occupied: identify the service, determine if it has been superseded (likely by gemini proxy at 8097)
  and stop/disable it, OR reassign it — document in SESSION_LOG.md
- This is a pre-condition for Session 2 Phase 1

## Remaining v0.9.2 Tasks

From MEMORY.md — active tasks before v0.9.2 can close:

- **On-screen keyboard**: keyboard-fix.js v2.0 deployed — needs live test confirmation on Pi
- **Boatlog voice note**: verify full flow on Pi (record → transcribe → save → view)
- **WebSocket real-time push**: Remote Access page
- **UAT**: 5 metric + 5 imperial users
- **Data export**: test with unit metadata
- **o-charts chart activation**: Don's task — see `deployment/docs/OPENCPN_FLATPAK_OCHARTS.md`

## Branch Rules

- Work only on v0.9.2 tasks (existing Pi HTML/services/v0.9.2 files)
- Do NOT touch `deployment/d3kOS/` (that is v0.9.2.1 territory)
- Do NOT touch `deployment/v0.9.3/` (that is v0.9.3 territory)
- Commit to `close-v0.9.2` branch — do not push
- When all tasks done: run session-close, then tell Don to merge to main

## Merge When Done

```bash
# Don runs this in /home/boatiq/Helm-OS when v0.9.2 is closed:
git checkout main
git merge close-v0.9.2 --no-ff -m "merge: close v0.9.2"
```
