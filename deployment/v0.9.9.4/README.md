# d3kOS v0.9.9.4 — CANONICAL SOURCE TREE

**Status:** IN DEVELOPMENT — not released
**Seeded:** 2026-07-27 (S108) **from the running lab Pi** `192.168.1.237`
**Master system:** the lab Pi SD card. This tree mirrors it; the Pi is the reference.

---

## Why this tree exists

Between April and July 2026 the project carried **two** dashboard source trees and treated both as
canonical:

| Tree | What it actually was |
|------|----------------------|
| `deployment/v0.9.4/pi_source/` | **the v0.9.9.2 release tree** — it stopped changing *at release*, which made its dates look stale |
| `deployment/d3kOS/dashboard/` | a separate lineage that **never contained the v0.9.9.2 features** (`_d3kEngData`, `/config/tier`, the five anchor routes, `/helm/mute`) |

The standing instruction was "add every new page to BOTH dirs." Because the trees were not peers,
that instruction caused deploys to pick files from whichever tree was reached first. The S105 deploy
took `instruments.js` from the second tree and **silently removed the M14 engine-data cache**
(BUG-36). `app.py` on the Pi is likewise from the wrong lineage and is missing seven routes
(BUG-37). Nobody noticed because `version.txt` was never bumped — two systems running materially
different code both reported `v0.9.2.2`.

**This tree replaces both.** There is now exactly one canonical source.

---

## Layout — full Pi paths, deliberately

```
deployment/v0.9.9.4/
├── opt/d3kos/services/…      → /opt/d3kos/services/…
├── var/www/html/…            → /var/www/html/…
├── etc/systemd/system/…      → /etc/systemd/system/d3kos-*.service
├── MANIFEST.md5              → md5 of every file, for drift detection
└── tools/check-drift.sh      → compares the deployed Pi against this tree
```

Paths are mirrored in full rather than flattened. The old flat layout is what made
`instruments.js` ambiguous between two trees — a filename alone did not say where it belonged.

---

## Rules

1. **The Pi is the master.** If the Pi and this tree disagree, investigate — do not blindly
   overwrite either side. Run `tools/check-drift.sh` to find out which files differ.
2. **Never deploy from `deployment/v0.9.4/pi_source/` or `deployment/d3kOS/dashboard/`.** Both are
   superseded and retained only for history and for recovering the v0.9.9.2 features still missing
   from the master (BUG-36, BUG-37, BUG-38).
3. **Every deploy must bump `/opt/d3kos/config/version.txt`** and regenerate `MANIFEST.md5`.
4. **Run `tools/check-drift.sh` before any clone or release.** A non-zero exit blocks both.
5. **No secrets in this tree.** `*.env`, `api-keys.json`, `license.json`, `device-token.json` and
   `cloud-credentials.json` are excluded by the seeding rsync and must stay excluded.

---

## Excluded from this tree (present on the Pi, deliberately not committed)

`*.env` (5 files: dashboard, ai-bridge, fleet, gemini-nav, d3kos-config) ·
`/opt/d3kos/config/` (api-keys.json, license.json, device-token.json) ·
`/opt/d3kos/data/` · `__pycache__` · `.pytest_cache` · `*.bak*` · `.ota-backup` · `*.db` · `*.log` · **runtime caches** (`*/cache/*`, `*cache*.json` — e.g. `gemini-nav/cache/response_cache.json`, which changes every time the Pi answers a query and would otherwise show as permanent drift)

Because these are excluded, a checkout of this tree is **not** a bootable system. It is source of
record, not an image. The bootable artifact is the SD card image.

---

## Drift check

```bash
cd deployment/v0.9.9.4
./tools/check-drift.sh                     # defaults to d3kos@192.168.1.237
./tools/check-drift.sh d3kos@172.20.10.8   # the boat Pi, when reachable
```

Exit codes: `0` no drift · `1` drift found · `2` Pi unreachable.
Baseline validated at seeding: 204/204. After the S108-cont deploy: **203/203 match, 0 drift**
(one runtime cache removed from tracking; BUG-39's two files intentionally excluded — see below).

**⚠ Known limitation:** this compares the **Pi** against `MANIFEST.md5`. It does **not** compare the
**repo** against the manifest. If you edit the repo without deploying, the Pi still matches the
manifest and this reports NO DRIFT — which does *not* mean the Pi is current. Regenerate
`MANIFEST.md5` as part of every deploy so the two stay meaningful together.

**Not tracked (deliberately undeployed):** `opt/d3kos/services/identity/regenerate-identity.sh` and
`etc/systemd/system/d3kos-identity-regen.service` (BUG-39) are held pending an operator ruling —
enabling that unit on the master would wipe its own identity.

---

## Release gate for v0.9.9.4

This tree is released only when the PART 17 bug list is cleared. Blocking items known at seeding:

- **BUG-36** restore `_d3kEngData` (keep the S105 `_lastSogKts` COG gate)
- **BUG-37** port the seven `app.py` routes
- **BUG-38** add `diagGrid` / `diagTitle` / `diagAiTxt` to `index.html`
- **BUG-29 / BUG-30** the `propulsion.0.*` and `belowKeel` Signal K path mismatches — these are why
  every engine gauge and the depth gauge read nothing
- **BUG-32** AIS never reaches Signal K · **BUG-33** hazard alerting disabled
- **BUG-34** hardcoded alarm string and non-boat-sourced thresholds
- **BUG-35** OTA destroys three of four `version.txt` fields
- **BUG-39** clone identity collision — must be solved before the card goes in the boat
