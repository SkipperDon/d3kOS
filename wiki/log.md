# Wiki Log — Helm-OS / d3kOS

*Append-only. One entry per operation. Format: `## [YYYY-MM-DD] <type> | <title>`*

---

## [2026-05-21] update | S86b — 4 new entities, 1 new concept, index updated (15 entities, 4 concepts)

- Files changed: entities/avnav.md (new), entities/fix-my-pi.md (new), entities/truenas-verify-agent.md (new), entities/sail-o-vision.md (new), concepts/orphan-branch-rule.md (new), index.md (15 entities, 4 concepts now)
- Wiki pages updated: all above
- Contradictions flagged: none
- Open questions: none new

## [2026-05-21] update | S86 — 2 new entities, 3 entity updates, index updated

- Files changed: entities/signalk-forward-watch.md (new), entities/admin-console-vm.md (new), entities/atmyboat-website.md (Stripe webhook fix S74 added), entities/d3kos-platform.md (Gemini model + BUG-08 added), entities/pwa.md (Stripe webhook note added), index.md (11 entities now)
- Wiki pages updated: all above
- Contradictions flagged: none
- Open questions: none new — d3kos-platform/atmyboat-website/pwa were last updated S62 (5 weeks stale); now current

## [2026-05-20] update | S85 — 4 new entities, 1 new concept, pi-system updated, index updated

- Files changed: entities/safehelm.md (new), entities/wiboat.md (new), entities/nmea2000-layer.md (new), entities/d3k-lite.md (new), concepts/ais-isolation.md (new), entities/pi-system.md (PiCAN-M added), index.md (9 entities, 3 concepts now)
- Wiki pages updated: all above
- Contradictions flagged: none
- Open questions: PiCAN-M was missing from wiki and pi-system.md since S62 — gap caused hardware claim error in S85. Root cause: fact discussed in session but never written to memory files. Session-start skill updated to grep DEPLOYMENT_INDEX.md as standing rule.

## [2026-04-17] ingest | Wiki initialization complete — 11 files, seeded from MEMORY.md

- Files created: index.md, log.md, entities/d3kos-platform.md, entities/atmyboat-website.md, entities/tier-system.md, entities/pi-system.md, entities/pwa.md, concepts/php-proxy-pattern.md, concepts/two-source-sync-rule.md, questions/bug-06-pwa-tier-display.md, questions/session-log-gap-s56-s61.md + sources/.gitkeep + syntheses/.gitkeep
- Wiki pages updated: ALL — initial creation
- Contradictions flagged: none
- Open questions: BUG-06 tier display (blocked), SESSION_LOG S56–S61 gap
- Status: ACTIVE

## [2026-05-21] research | S87 — sail-o-vision reply drafted; AIS700 N2K behaviour confirmed; simulator concept filed
- Files changed: SESSION_LOG.md, wiki/log.md
- Wiki pages updated: none (facts noted in log only — sail-o-vision entity update deferred to next session with confirmed new facts)
- Contradictions flagged: AIS isolation 4-layer design assumes general AIS transponder relay risk; Adam's AIS700 does not relay received N2K AIS PGNs — no contradiction, just different hardware context
- Open questions: Adam's Axiom MMSI suppression behaviour for 99xxx range (untested)

## [2026-05-29] update | S89 — AAO v2.0 Section 24 authored and pushed to GitHub
- Files changed: aao-methodology-repo/SPECIFICATION.md, aao-methodology-repo/CLAUDE.md, /home/boatiq/CLAUDE.md
- Wiki pages updated: none (methodology doc, not wiki entity)
- Contradictions flagged: none
- Open questions: none

## [2026-05-30] comms | S90 — LinkedIn comment drafted: quantified Adaptive Governance Spec example (S83 SGCR violation → spec sharpening → 6 consecutive 100/100 sessions)

## [2026-06-23] planning | S92 — v0.9.9.5 Discussion Plan created; 11 research items captured
- Files changed: deployment/docs/V09995_DISCUSSION_PLAN.md (new), PROJECT_CHECKLIST.md (PART 20 added), deployment/docs/DEPLOYMENT_INDEX.md (V09995 indexed)
- Wiki pages updated: wiki/log.md only
- Contradictions flagged: none
- Open questions: D11 hardware selection (NCS2 vs Hailo/Coral), D11 marine class model source, D11 chart engine (AvNav vs MapLibre)
## [2026-07-11] fix | S96 — BUG-12 AIS provider re-enabled; AvNav serial conflict fixed; o-charts expiry diagnosed
- Files changed: PROJECT_CHECKLIST.md (BUG-12 row, OB-O05-08), V09994_BUG_FIXES.md (BUG-12 entry), DEPLOYMENT_INDEX.md (S96 entry)
- Pi config changed: ~/.signalk/settings.json (ais enabled:true), /var/lib/avnav/avnav_server.xml (ignore usbid 1-1.4:1.0)
- Wiki pages updated: log.md (this entry)
- Contradictions flagged: none
- Open questions: o-charts license renewal required (OB-O05)

## [2026-07-11] bug-log | S97 — BUG-13 logged: speed gauge flicker + long-press UX issue
- Files changed: PROJECT_CHECKLIST.md (PART 17 BUG-13 row), V09994_BUG_FIXES.md (v1.5.0→v1.6.0 full entry), DEPLOYMENT_INDEX.md (S97 section)
- Wiki pages updated: none (no entity/concept changes — bug tracking only)
- Contradictions flagged: none
- Open questions: R1–R4 investigation steps defined in BUG-13 entry; root cause unknown pending investigation
## [2026-07-15] research | S99 — D13 VHF Communication Suite added to V09995 discussion plan
- Files changed: deployment/docs/V09995_DISCUSSION_PLAN.md (v1.0→v1.1, D13 added), PROJECT_CHECKLIST.md (PART 20 D13 row), deployment/docs/DEPLOYMENT_INDEX.md (V09995 entry updated)
- Wiki pages updated: none (no new entities — base project external, no Pi architecture changes)
- Contradictions flagged: none
- Open questions: VHF radio audio tap accessibility (blocking Phase 1); Pi memory headroom for Faster-Whisper base model; ALSA card index collision check

## [2026-07-27] fix+governance | S108 — lab Pi = master; canonical tree seeded from the Pi; BUG-35…BUG-40 logged; 5 bugs specced, implemented and verified
- Files changed: `deployment/v0.9.9.4/` (NEW — 204 files + README + MANIFEST.md5 + 6 tools); `deployment/docs/atomic-specs/BUG-35|36|37|38|39.md` (NEW); `tests/` (5 NEW); `PROJECT_CHECKLIST.md`; `deployment/docs/V09994_BUG_FIXES.md`; `deployment/docs/DEPLOYMENT_INDEX.md`; Pi `/opt/d3kos/config/version.txt`
- Wiki pages updated: `index.md` (question-queue pointer); `questions/2026-07-27-v0994-tier3-spec-questions.md` (NEW — 17 Q&A)
- Contradictions flagged: **`concepts/two-source-sync-rule` is invalidated.** The two trees were never peers — `deployment/v0.9.4/pi_source/` IS the v0.9.9.2 release tree, and `deployment/d3kOS/dashboard/` is a separate lineage that never held the v0.9.9.2 features (md5-proven). The "add every new page to BOTH dirs" instruction is what produced BUG-36 and BUG-37. Superseded by a single canonical tree plus `check-drift.sh`. S107's inverted reading also invalidated BUG-28/29/30 and DEP20 as written.
- Open questions: BUG-30 approach (keel offset vs `belowTransducer` + relabel) — operator ruling needed, grounding-risk dimension; BUG-29 whether Signal K's engine instance→name mapping is configurable; BUG-40 whether the SK vessel UUID is runtime-random or machine-id-derived; whether the boat Pi is also v0.9.9.2-era.

## [2026-07-27] fix | S108-cont — BUG-29/30 specced from converter source; seven Tier-3 fixes implemented and verified; Tier 3 closed out
- Files changed: `deployment/v0.9.9.4/` (7 source files fixed, 7 verifier tools added); `deployment/docs/atomic-specs/BUG-29.md` + `BUG-30.md` (NEW), BUG-36/BUG-30 revised; `tests/` (7 files); `PROJECT_CHECKLIST.md` v3.12; `DEPLOYMENT_INDEX.md`
- Wiki pages updated: `questions/2026-07-27-v0994-tier3-spec-questions.md` (Q29.1-3, Q30.1-2 added and answered)
- Contradictions flagged: **Signal K's engine instance mapping is NOT configurable** — `skEngineId()` is a hardcoded ternary in `@signalk/n2k-signalk/dist/utils.js`, closing the open S107 question. It returns the numeric instance OR `'port'` depending on how canboat decodes the field, so the path is unstable and the fix must accept both. **Two of four engine paths have a wrong LEAF as well as a wrong instance** (`.temperature`, `.drive.trimState`). **`electrical.batteries.0.voltage` and `tanks.fuel.0.currentLevel` are CORRECT** — earlier suspicion closed. **BUG-30's framing was wrong:** SK already derives `belowKeel` from a negative PGN 128267 offset, so the primary fix is sounder configuration, not code.
- Open questions: oil-pressure Pa vs kPa scaling (`pgns/127489.js` returns an unconverted value from a variable named `kpa`) — post-deploy check against the analogue gauge; `check-drift.sh` compares Pi-vs-manifest, not repo-vs-manifest, and reports NO DRIFT while the repo is 8 files ahead.
## [2026-07-29] spec | S110 — BUG-41 atomic spec authored
- Files changed: `deployment/docs/atomic-specs/BUG-41.md` (NEW)
- Wiki pages updated: none
- Contradictions flagged: none
- Open questions: none — all information derived directly from the target file (`app.py` + `settings.html`). The spec is a one-file, three-test, straightforward pass.
## [2026-07-29] spec | S110 — BUG-34 atomic spec authored
- Files changed: `deployment/docs/atomic-specs/BUG-34.md` (NEW)
- Wiki pages updated: none
- Contradictions flagged: none
- Open questions: none. Source authority: MerCruiser 454 SM AI doc (S106) for all threshold values.
## [2026-07-29] fix+governance | S110 — BUG-41 + BUG-34 fixed and deployed to lab Pi; session close
- Files changed: `deployment/v0.9.9.4/opt/d3kos/services/dashboard/app.py`; `static/js/instruments.js`; `static/js/overlays.js`; `deployment/docs/atomic-specs/BUG-41.md` (NEW); `deployment/docs/atomic-specs/BUG-34.md` (NEW); `tests/test_bug41_settings_route.py` (NEW); `tests/bug34-diag-panel.test.cjs` (NEW); `PROJECT_CHECKLIST.md` v3.15→v3.16; `deployment/docs/V09994_BUG_FIXES.md` (BUG-34 updated, BUG-41 added); `deployment/docs/DEPLOYMENT_INDEX.md` (S110 section); `SESSION_LOG.md` (S110 entry); MEMORY.md (trimmed 24.5KB→13.3KB)
- Wiki pages updated: `wiki/log.md` (this entry)
- Contradictions flagged: none
- Open questions: BUG-41 Flask client tests (tests 1+2) need Flask on Pi to run fully; BUG-34 pre-fix failing run not recorded by Haiku; jest.config.cjs has `export default` in a .cjs file (pre-existing, unresolved); oil-pressure kPa/Pa scaling still open.
