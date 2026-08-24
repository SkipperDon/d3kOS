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
## [2026-07-29] fix | S110 — BUG-32 + BUG-40 (Group B) fixed and deployed to lab Pi
- Files changed: `etc/systemd/system/rtl-ais.service` (NEW in canonical tree; `-T -P 10108`); `home/d3kos/.signalk/settings.json` (NEW; ais provider port 10108, enabled:true, host points to rtl_ais server); `home/d3kos/.signalk/defaults.json` (NEW; vessel uuid af7d4be0); `deployment/docs/atomic-specs/BUG-32.md` (NEW); `PROJECT_CHECKLIST.md` v3.18; `V09994_BUG_FIXES.md` (BUG-32 + BUG-40 status). Commits `13716ac`, `89e8ea0`.
- Wiki pages updated: `wiki/log.md` (this entry)
- Contradictions flagged: **SK TcpProvider has no server mode** — `"server": true` and removing `host` both confirmed ineffective (ECONNREFUSED loop, not a listener). The correct fix is `rtl_ais -T` (rtl_ais becomes TCP server). BUG-32 spec was written before this was discovered; spec updated to reflect actual fix. **SK v2.23 ignores vessel.uuid in settings.json** — confirmed by restart test (UUID changed); fix is defaults.json, not settings.json vessel block.
- Open questions: BUG-32 on-boat validation required (dongle absent on lab Pi; can only confirm data flows on the boat). Boat Pi settings.json vessel.uuid may differ from lab — verify before deploying defaults.json to boat Pi.

## [2026-07-29] spec+fix | S110 — BUG-13 atomic spec authored; Haiku implemented; §25.8 verified
- Files changed: `deployment/docs/atomic-specs/BUG-13.md` (NEW); `static/js/instruments.js` (Changes A+B+C); `tests/bug13-speed-gauge.test.cjs` (NEW); `PROJECT_CHECKLIST.md` v3.17; `V09994_BUG_FIXES.md` (BUG-13 status updated)
- Wiki pages updated: `wiki/log.md` (this entry)
- Contradictions flagged: none
- Open questions: Issue 1 (flicker) root cause assumed to be multi-source SK interleaving — requires on-boat throttle change to confirm; if debounce insufficient, SK subscription-level source filtering is the next step (BUG-13v2)

## [2026-07-29] fix+governance | S110 — BUG-33 + BUG-21 (Group C) config fix; governance updated
- Files changed: `deployment/docs/V09994_BUG_FIXES.md` (BUG-33 status + fix summary; BUG-21 resolution note); `PROJECT_CHECKLIST.md` (BUG-33 `[~]`, BUG-21 `[~]`)
- Pi config changed directly (NOT in canonical tree — contains credentials): `/home/d3kos/.signalk/plugin-config-data/signalk-forward-watch.json` (`detection_interval` 300→10, `audio_alarm` false→true)
- Wiki pages updated: `wiki/log.md` (this entry)
- Contradictions flagged: **BUG-21 "pipeline not built" claim was WRONG** — S110 source read confirmed pipeline IS built end-to-end in `signalk-forward-watch` (`index.js` + `signalk-output.js`). The detection loop, ONNX inference, SK publish path, and audio alarm are all implemented. The root cause was purely config (5-min interval + audio disabled). No code changes needed.
- Open questions: On-boat validation required — camera at `10.42.0.100` is on boat-subnet only; lab Pi can't reach it; detection loop exits early via `if (!framePath) return` when RTSP fails. Full end-to-end (detections → `notifications.*` → audio) can only be confirmed on the boat.
- Security note: `signalk-forward-watch.json` contains `camera_pass: d3kos2026` — never pull into canonical tree.

## [2026-07-29] fix+governance | S110 — BUG-41 + BUG-34 fixed and deployed to lab Pi; session close
- Files changed: `deployment/v0.9.9.4/opt/d3kos/services/dashboard/app.py`; `static/js/instruments.js`; `static/js/overlays.js`; `deployment/docs/atomic-specs/BUG-41.md` (NEW); `deployment/docs/atomic-specs/BUG-34.md` (NEW); `tests/test_bug41_settings_route.py` (NEW); `tests/bug34-diag-panel.test.cjs` (NEW); `PROJECT_CHECKLIST.md` v3.15→v3.16; `deployment/docs/V09994_BUG_FIXES.md` (BUG-34 updated, BUG-41 added); `deployment/docs/DEPLOYMENT_INDEX.md` (S110 section); `SESSION_LOG.md` (S110 entry); MEMORY.md (trimmed 24.5KB→13.3KB)
- Wiki pages updated: `wiki/log.md` (this entry)
- Contradictions flagged: none
- Open questions: BUG-41 Flask client tests (tests 1+2) need Flask on Pi to run fully; BUG-34 pre-fix failing run not recorded by Haiku; jest.config.cjs has `export default` in a .cjs file (pre-existing, unresolved); oil-pressure kPa/Pa scaling still open.

## [2026-08-24] research+governance | S132 — CX5106 DIP switch truth established from primary source; BUG-81 logged
- Files changed: `docs/CX5106_DIP_SWITCH.md` (NEW, public guide — not published); `deployment/docs/CX5106_CONFIGURATION_FROM_MANUAL.md` (NEW, internal record + audit); `deployment/docs/V09994_BUG_FIXES.md` (BUG-81, 170 lines); `PROJECT_CHECKLIST.md` v3.33→v3.34; `doc/CX5106_CONFIGURATION_GUIDE.md` + `doc/CX5106_USER_MANUAL.md` (image paths only, text still wrong); `deployment/docs/DEPLOYMENT_INDEX.md` (S132); `SESSION_LOG.md` (S132); MEMORY.md + `project_cx5106_status.md`
- Wiki pages updated: `wiki/log.md` (this entry)
- Contradictions flagged: **THREE.** (1) **The CX5106 has a 7-position DIP + a separate 2-position switch, NOT 8 switches in one row.** The 7 positions are ONE binary field — the RPM speed ratio, sw1 = LSB, `ratio = 1 + sum of ON values`. `setup.html` lines 1237-1305, `doc/CX5106_CONFIGURATION_GUIDE.md` and `doc/CX5106_USER_MANUAL.md:53` all assert the 8-switch model with invented per-feature fields (engine instance / RPM sensor type / cylinder count / stroke type / gear ratio). Of the wizard's 10 mappings only 2 are correct, both on the 2-switch block. → BUG-81. (2) **`assets/images/cx5106_10125.png` refutes the guide that embeds it** — the photo shows a block numbered 1-7 and a separate block numbered 1-2; `CX5106_CONFIGURATION_GUIDE.md` references it at lines 23/332 directly under its own 8-switch claim. The image paths were broken (`../../assets`, outside the repo) so it never rendered and the contradiction was invisible. (3) **The wizard calls the device "Actisense CX5106"** (`setup.html:796`, `:1328`) — the label plate carries no brand, and the same wizard correctly lists the Actisense EMU-1 separately. Manufacturer unconfirmed.
- Verification method (recorded because it is reusable): encoding decoded from the leaflet, then **predict-and-check** against printed rows at BOTH ends of the table (ratio 13 → switches 3,4; ratio 125 → switches 3,4,5,6,7) rather than only the easy end; plus an independent structural cross-check — the terminal label's 4 left + 9 right = 13 inputs exactly matches §2.2's separate "up to 13 sensors" statement.
- Open questions: whether a wrong ratio bears on BUG-14 at all (a ratio error gives a WRONG RPM, not ABSENT data PGNs, and cannot explain missing oil/temp/fuel PGNs — do NOT record it as BUG-14's root cause); the direction in which the ratio scales displayed RPM (undocumented, untested); how to interpret the S101 switch record now that two blocks are known; the actual manufacturer; whether a leaflet §5 exists anywhere (the sheet jumps §4 → §6).
- Process note: this is the third instance of the **premise-over-source** failure mode after BUG-08 and BUG-78 — a plausible written premise trusted instead of the primary source. Here the primary source was already in the repository at `assets/manuals/CX5106_10125_manual.pdf` the entire time.

## [2026-08-24] spec-authoring | S131 + S132-cont — v0.9.9.4 atomic spec set, governance recovery
- Files changed: `V09994_BUG_FIXES.md` (BUG-60–69 restored, BUG-71–80 logged, BUG-56/62/66/78
  re-diagnosed, 10 credentials redacted) · `PROJECT_CHECKLIST.md` (+17 rows, 3.30→3.33) ·
  `doc/MASTER_SYSTEM_SPEC.md` (3.9→4.0, 11 edits) · `D3KOS_DEVICE_REGISTRATION_SPEC.md` (restored,
  475 lines) · `deployment/docs/atomic-specs/` (18 new files incl. `EXECUTION-ORDER.md`) ·
  `SESSION_LOG.md` (S131 + S132-cont entries, written late)
- Wiki pages updated: none — no entity page exists for the v0.9.9.4 spec set or the CX5106 gateway.
  **Open gap: `wiki/log.md` was not appended to during either session, only at the end. Standing scope
  allows it; the discipline was not followed.**
- Contradictions flagged: `MASTER_SYSTEM_SPEC` section 12.1's build script is fictional (no
  `sanitize.sh` call exists) · section 9.2's three "No Phone-Home" clauses contradicted by sections
  8.3/8.4/6.3.4 of the same document · `.gitignore` protects a credential file that has never existed
  while leaving the real one unprotected · two different READMEs (local 2 links, `origin/main` 1 link)
  with no record stating which is meant · `detectTier()` structurally unable to return a tier the
  registration design gates on
- Open questions: leaflet section 6.1 read only via a derived guide, not the primary source
  (`poppler-utils` absent) · whether a released `.img` already ships a live fleet key (UNVERIFIED,
  highest priority) · why `version-heartbeat.php`'s UPDATE became an UPSERT · whether WebRTC has ever
  been validated end to end

## [2026-08-24] governance+tooling | S133-cont — Phase 0.2–0.4 complete; fetchAis invariant asserted
- Files changed: `deployment/v0.9.9.4/opt/d3kos/scripts/` (4 new: create-image.sh, sanitize.sh, tier-manager.sh, detect-opencpn.sh) · `tools/release-state.sh` (new: three-way drift verifier + comparison 4 INVARIANTS) · `opt/d3kos/services/cloud-agent/cloud_agent.py` (promoted 719-line superset) · `opt/d3kos/services/cloud-agent/ota_upgrade.py` (promoted 410-line version with BUG-35 fix) · `var/lib/avnav/avnav_server.xml` → `avnav_server.xml.template` (renamed + annotated) · `opt/d3kos/services/fleet/config/fleet-push.env.template` (new) · `deployment/docs/PI_CONFIG_DELTA.md` (new) · `MANIFEST.md5` (212 entries) · `EXECUTION-ORDER.md` (0.2/0.3/0.4 ticked) · `PROJECT_CHECKLIST.md` (3.37→3.40)
- Wiki pages updated: none — no entity page covers drift tooling or per-Pi config templates. `[[entities/avnav]]` is the closest relevant entity; adding a note below.
- Contradictions flagged: none new
- Open questions: cloud_agent.py promoted but not yet deployed to lab Pi — DRIFTED in verifier; deploy is pending

### Addendum — entities/avnav note
Per-Pi delta for avnav_server.xml is now formally documented in `deployment/docs/PI_CONFIG_DELTA.md`. The BUG-19/20 fix (`fetchAis="true" aisQueryPeriod="5"`) is machine-asserted by `tools/release-state.sh` comparison 4 on every verifier run. The boat Pi additionally requires a u-blox USB ignore rule (usbid `1-1.4:1.0`) absent from the lab Pi — this is expected and documented.
