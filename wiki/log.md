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
