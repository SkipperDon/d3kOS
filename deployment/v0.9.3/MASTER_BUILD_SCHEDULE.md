# AtMyBoat.com — Master Build Schedule & Document Cross-Index
**Version 1.0 · 2026-03-24**
**Single source of truth: what is built, what is left, when each piece ships**

---

## PART 1 — DOCUMENT CROSS-INDEX

All source content documents in `Helm-OS/doc/`. Status shows whether each has been used in the current build.

| Document | What It Contains | Used In Build? | Action |
|----------|-----------------|---------------|--------|
| `doc/ATMYBOAT_ABOUT_PAGE.html` | Full About/Our Story page — Lake Erie origin, Skipper Don, mission, why d3kOS, community | **NOT USED** | S6 — source for `/about` |
| `doc/ATMYBOAT_CONTACT_PAGE.html` | Full Contact Us page — email (service@atmyboat.com), form fields, quick resources, support hours | **NOT USED** | S6 — source for `/contact` |
| `doc/ATMYBOAT_LANDING_PAGE_CONTENT.md` | Full brand copy: hero ("Come Sail with Our Time"), tier descriptions T0–T3, hardware kit (d3-k1), blog categories, BoatIQ Solutions | **PARTIALLY USED** — tier info only, brand copy not applied to pages | S6 — use for /pricing, update existing pages |
| `doc/ATMYBOAT_NEW_HOMEPAGE_CONTENT.md` | WordPress block-by-block homepage guide — hero, blog posts, MailPoet subscribe, d3kOS section | **NOT USED** | Homepage update — Don's task after live push |
| `doc/ATMYBOAT_LANDING_PAGE.html` | Complete HTML landing page with all sections | **NOT USED** | Reference only — current build uses child theme PHP |
| `doc/ATMYBOAT_HOMEPAGE_HTML.html` | Original homepage HTML | **NOT USED** | Reference only |
| `doc/ATMYBOAT_HOMEPAGE_FINAL_CORRECTED.html` | Corrected homepage HTML | **NOT USED** | Reference only |
| `doc/ATMYBOAT_HOMEPAGE_CONTENT_ONLY.html` | Homepage content without styling | **NOT USED** | Reference only |
| `doc/ATMYBOAT_HOMEPAGE_READY.html` | Ready-to-paste homepage HTML | **NOT USED** | Reference only |
| `doc/ATMYBOAT_MODERN_REDESIGN.html` | Modern redesign mockup | **NOT USED** | Reference only |
| `doc/ATMYBOAT_HARDWARE_SECTION_CORRECTED.html` | Corrected hardware section HTML | **PARTIALLY USED** — page-hardware.php built, connectivity story not included | S6 — add connectivity section |
| `doc/ATMYBOAT_CSS_FOR_WORDPRESS.css` | CSS for WordPress | **NOT USED** — current build uses mockup design system | Superseded by mockup design system |
| `doc/ATMYBOAT_ECOMMERCE_RECOMMENDATION.md` | E-commerce approach recommendation | **NOT USED** | Archived — Stripe decision already made |
| `doc/ATMYBOAT_CLAUDE_CODE_SPEC.md` | Claude Code spec for AtMyBoat | **SUPERSEDED** — replaced by BUILD_REFERENCE | Reference only |
| `doc/ATMYBOAT_IMPLEMENTATION_GUIDE.md` | Implementation guide | **SUPERSEDED** | Reference only |
| `doc/ATMYBOAT_MODERN_IMPLEMENTATION_GUIDE.md` | Modern implementation guide | **SUPERSEDED** | Reference only |
| `doc/ATMYBOAT_OPTION1_FINAL_PLAN.md` | Option 1 final plan | **SUPERSEDED** | Reference only |
| `doc/ATMYBOAT_OPTION1_FILES_SUMMARY.md` | Option 1 files summary | **SUPERSEDED** | Reference only |
| `doc/ATMYBOAT_OPTION1_IMPLEMENTATION_GUIDE.md` | Option 1 implementation guide | **SUPERSEDED** | Reference only |
| `doc/ATMYBOAT_CHANGES_SUMMARY.md` | Changes summary | **SUPERSEDED** | Reference only |
| `doc/ATMYBOAT_COMPLETE_FIX.txt` | Complete fix notes | **SUPERSEDED** | Reference only |
| `doc/ATMYBOAT_WORDPERFECT_WORKFLOW.md` | WordPerfect workflow | **SUPERSEDED** | Reference only |
| `doc/ATMYBOAT_WORDPRESS_ECOMMERCE_GUIDE.md` | WP e-commerce guide | **SUPERSEDED** | Reference only |
| `doc/ATMYBOAT_UNSUBSCRIBE_PAGE.html` | Unsubscribe page | **NOT YET NEEDED** | Add to MailPoet setup |
| `doc/ATMYBOAT_BLOG_POPUP.html` | Blog popup | **NOT USED** | Deferred — post-launch |
| `doc/ATMYBOAT_BLOG_PREVIEW_FUNCTIONAL.html` | Blog preview | **NOT USED** | Deferred — post-launch |
| `doc/d3kOS-MARKETING-SHEET.md` | Full product marketing sheet — CX5106, NMEA2000, WiFi, Ethernet, all capabilities | **NOT USED on website** | S6 — source for /products connectivity section and /hardware |
| `doc/d3kOS_PUBLIC_SUMMARY.md` | Public summary of d3kOS | **NOT USED on website** | S6 — source material |
| `doc/d3kOS_TESTING_CHECKLIST.md` | Testing checklist | **NOT USED on website** | Internal reference |
| `doc/d3kOS_TODO_2026-02-25.md` | Feb 2026 todo list | **SUPERSEDED** | Historical reference only |

**Summary:** 3 documents with live content for S6 (`ATMYBOAT_ABOUT_PAGE.html`, `ATMYBOAT_CONTACT_PAGE.html`, `d3kOS-MARKETING-SHEET.md`). 1 partially used (`ATMYBOAT_LANDING_PAGE_CONTENT.md`). Rest are superseded or deferred.

---

## PART 2 — FULL WEBPAGE INVENTORY WITH STATUS AND DEPLOY DATE

### Already Built (Sessions 1–5)

| Page | File | Built | On Staging? | Live? |
|------|------|-------|------------|-------|
| `/register` | page-register.php | S1 ✅ | After Don imports schema + runs install-pages.php | Phase 4 |
| `/pair-device` | page-pair-device.php | S1 ✅ | After Don imports schema + runs install-pages.php | Phase 4 |
| `/privacy` | page-privacy.php | S1 ✅ | After install-pages.php | Phase 4 |
| `/terms` | page-terms.php | S1 ✅ | After install-pages.php | Phase 4 |
| `/warranty` | page-warranty.php | S1 ✅ | After install-pages.php | Phase 4 |
| `/products` | page-products.php | S1/2D ✅ | Yes (S1 deploy) | Phase 4 |
| `/hardware` | page-hardware.php | S2 ✅ | After install-pages.php | Phase 4 — **with S6 connectivity update** |
| `/download` | page-download.php | S2 ✅ | After install-pages.php | Phase 4 |
| `/app` | page-app.php | S2 ✅ | After install-pages.php | Phase 4 |
| `/community` | page-community.php | S3 ✅ | After install-pages.php | Phase 4 |
| `/marketplace` | page-marketplace.php | S3 ✅ | After install-pages.php | Phase 4 |
| `/features` | page-features.php | S3 ✅ | After install-pages.php | Phase 4 |
| `/challenges` | page-challenges.php | S3 ✅ | After install-pages.php | Phase 4 |
| `/hall-of-fame` | page-hall-of-fame.php | S3 ✅ | After install-pages.php | Phase 4 |
| `/directory` | page-directory.php | S4 ✅ | After install-pages.php | Phase 4 |
| `/dashboard` | page-dashboard.php | S4 ✅ | After install-pages.php | Phase 4 |
| `/fix-my-pi` | page-fix-my-pi.php | S5 ✅ | After install-pages.php | Phase 4 |
| `/forum` | bbPress plugin | Phase 1 ✅ | S1 deploy | Phase 4 |

### To Be Built (Session 6)

| Page | File to Create | Content Source | Built | On Staging | Live |
|------|---------------|---------------|-------|-----------|------|
| `/about` | page-about.php | `doc/ATMYBOAT_ABOUT_PAGE.html` (exists — needs dark theme adapt) | S6 | S6 deploy | Phase 4 |
| `/contact` | page-contact.php | `doc/ATMYBOAT_CONTACT_PAGE.html` (exists — needs dark theme + AI widget) | S6 | S6 deploy | Phase 4 |
| `/pricing` | page-pricing.php | `doc/ATMYBOAT_LANDING_PAGE_CONTENT.md` tiers + BUILD_REFERENCE Part 9 | S6 | S6 deploy | Phase 4 |
| `/upgrade` | page-upgrade.php | Stripe T2/T3 checkout — no prior doc | S6 | S6 deploy | Phase 4 |
| `/help` | page-help.php | AI widget + quick links — no prior doc | S6 | S6 deploy | Phase 4 |
| `/help/software-update` | page-help-update.php | d3kOS OTA architecture + onboarding wizard content | S6 | S6 deploy | Phase 4 |
| `/help/software-downgrade` | page-help-downgrade.php | No prior doc — new content | S6 | S6 deploy | Phase 4 |
| `/help/create-subscription` | page-help-subscribe.php | No prior doc — new content | S6 | S6 deploy | Phase 4 |
| `/help/cancel-subscription` | page-help-cancel.php | No prior doc — new content | S6 | S6 deploy | Phase 4 |
| `/hardware` (update) | page-hardware.php — add section | `doc/d3kOS-MARKETING-SHEET.md` connectivity section | S6 | S6 deploy | Phase 4 |
| `/products` (update) | page-products.php — add section | `doc/d3kOS-MARKETING-SHEET.md` + connectivity diagram | S6 | S6 deploy | Phase 4 |

### To Be Built (Session 7)

| Page | File to Create | Content Source | Built | On Staging | Live |
|------|---------------|---------------|-------|-----------|------|
| `/account` | page-account.php | Stripe Customer Portal + pairing data | S7 | S7 deploy | Phase 4 |
| `/accessibility` | page-accessibility.php | AODA compliance statement (required by law) | S7 | S7 deploy | Phase 4 |

### Deferred / Blocked

| Page | Reason |
|------|--------|
| `/compatible` | Blocked — needs Don's engine compatibility data |
| `/academy` | No content ready — post-launch |
| `/docs` | Knowledge base — post-launch |

---

## PART 3 — API INVENTORY: BUILT, TESTED, AND DEPLOY DATES

### Website APIs (HostPapa PHP — mobile/ folder)

| Endpoint | Purpose | Built | Tested on Staging | Deployed to Live |
|----------|---------|-------|------------------|-----------------|
| `mobile/auth.php` | Device token + API key authentication | S5 ✅ | After Don imports schema | Phase 4 |
| `mobile/register-device.php` | First install — create device UUID | S5 ✅ | After Don imports schema | Phase 4 |
| `mobile/pair-device.php` | QR pairing — link Pi to account | S5 ✅ | After Don imports schema | Phase 4 |
| `mobile/command-queue.php` | Command broker Pi↔app | S5 ✅ | After Don imports schema | Phase 4 |
| `mobile/data-ingress.php` | Pi POSTs health data every 30 min | S5 ✅ — **GAP: no tier return, no pi_installation_id writes** | After S6 fix | Phase 4 |
| `mobile/tier-features.php` | Return tier feature flags | S5 ✅ | After Don imports schema | Phase 4 |
| `mobile/fix-my-pi-billing.php` | Stripe checkout + webhook | S5 ✅ — **GAP: no lifecycle webhooks (cancel/fail)** | After S6 fix | Phase 4 |
| `mobile/pdf-report.php` | mPDF + Gemini report (T2/T3) | S5 ✅ | After Don imports schema | Phase 4 |
| `mobile/version-registry.php` | OTA version tracking | S5 ✅ | After Don imports schema | Phase 4 |
| `mobile/community-markers.php` | Receive Pi community data | **S6 — NOT BUILT** | S6 | Phase 4 |
| `mobile/community-get.php` | Serve community markers to map | **S6 — NOT BUILT** | S6 | Phase 4 |
| `data-ingress.php` fix | Add tier return + pi_installation_id | **S6 — fix** | S6 | Phase 4 |
| `fix-my-pi-billing.php` fix | Add Stripe lifecycle webhooks | **S6 — fix** | S6 | Phase 4 |

### APIs Not Yet Built (Future — v0.9.4.1)

| Endpoint | Purpose | Session |
|----------|---------|---------|
| `mobile/dashboard-data.php` | App boat health dashboard + Find My Boat data | v0.9.4.1 |
| `mobile/list-vessels.php` | Multi-boat vessel list for T3 | v0.9.4.1 |

### Pi APIs (already deployed on Pi — for reference)

All Pi APIs are complete and deployed. Port map:

| Port | Service | Status |
|------|---------|--------|
| 3000 | Flask main app | Live |
| 8081 | upload_api | Live |
| 8082 | history_api | Live |
| 8083 | manuals_api | Live |
| 8084 | camera_stream_manager | Live |
| 8086 | fish_detector | Live |
| 8087 | keyboard-api | Live |
| 8089 | ai_api (Gemini proxy) | Live |
| 8094 | export-manager | Live |
| 8095 | boatlog-export-api | Live |
| 8099 | SignalK | Live |
| 8103 | community-api | Live (Node-RED flows disabled — waiting for S6 website endpoints) |
| 8111 | remote_api | Live |

**Pi side gap:** `export_worker.py` still has placeholder URL `d3kos-cloud-api.example.com` — not connected to real atmyboat.com. Fix is Part 8A (v0.9.4.1 integration work).

---

## PART 4 — GITHUB REPO STATUS AND DEPLOYMENT PIPELINE

### Current State

```
Repo: github.com/SkipperDon/atmyboat-forum
Local commits: 2 (e354c23 and 959ef65)
Pushed to GitHub: NO — code is local only (per standing git policy)
HostPapa staging: deployed via FTPS (lftp) — not connected to GitHub
```

### When GitHub Gets Used

**Recommended sequence:**

| Event | What happens | When |
|-------|-------------|------|
| **S6 session start** | Don authorizes push of existing 2 commits to GitHub | **Session 6 — first action** |
| **After S6 build** | All S6 files committed locally, then pushed to GitHub | Session 6 |
| **Staging deploy** | FTPS sync from local repo to HostPapa staging (existing pipeline) | After each session |
| **S7 session** | S7 changes committed + pushed | Session 7 |
| **Phase 4 — Live push** | Don clicks "Staging → Push to Live" in HostPapa cPanel | Session 8 |

**Why push to GitHub at Session 6 start:**
- The repo currently has 39 files and 6,291 lines of code that exist only on one laptop
- GitHub is the backup. If the laptop fails before Phase 4, the code is lost
- GitHub also enables code review before live push
- The repo should be set to **Private** (proprietary code — never public)

**Note on cPanel Git VC (future option):**
After the repo is on GitHub, HostPapa cPanel can be configured to pull from GitHub automatically on push. This replaces the FTPS sync script with a cleaner git-based pipeline. Recommended to set this up at Session 7 so Phase 4 live push is clean.

---

## PART 5 — FULL SESSION PLAN WITH DATES

### Session 6 — Tomorrow

**Gate:** Don reviews `SESSION6_CONTENT_PLAN.md` and approves content before this session starts.

**Order of operations:**

| Step | Task | Type | Est. |
|------|------|------|------|
| 1 | Push existing 2 commits to GitHub (Don authorizes) | GitHub | 5 min |
| 2 | 2B CSS font fix — 3 lines in style.css | Fix | 5 min |
| 3 | `/about` page | New page | 30 min |
| 4 | `/contact` page | New page | 30 min |
| 5 | `/pricing` page | New page — critical | 45 min |
| 6 | `/upgrade` page + Stripe subscription checkout | New page + backend | 60 min |
| 7 | `/help` + 4 help article pages | 5 new pages | 60 min |
| 8 | `/hardware` + `/products` connectivity section update | Updates to existing | 30 min |
| 9 | Multi-boat schema fix (5 ALTER TABLE statements) | DB | 15 min |
| 10 | `data-ingress.php` — add tier return + pi_installation_id | API fix | 15 min |
| 11 | `fix-my-pi-billing.php` — lifecycle webhooks + downgrade logic | API fix | 45 min |
| 12 | T2 monthly reset cron job | Config | 10 min |
| 13 | Community API endpoints (5 PHP files) | New APIs | 60 min |
| 14 | Commit + push to GitHub + FTPS sync to staging | Deploy | 15 min |
| 15 | SEO (Yoast, sitemap) | Config | 30 min |

**End of Session 6:** All pages built, all API fixes applied, on GitHub, deployed to staging for Don's review.

---

### Session 7 — AODA Audit + Account Page

| Step | Task |
|------|------|
| 1 | `/account` page — subscription management, Stripe Customer Portal, paired devices |
| 2 | `/accessibility` page — required AODA compliance statement |
| 3 | AODA audit across all pages (WAVE scan, contrast check, keyboard nav, touch targets) |
| 4 | Fix any AODA issues found |
| 5 | Set up cPanel Git VC → GitHub connection (replaces FTPS deploy going forward) |
| 6 | Commit + push + staging deploy |

**End of Session 7:** All pages exist. AODA audit passed. Ready for Don's full staging review before live push.

---

### Session 8 — Phase 4: Staging → Live (Don's hands only)

| Step | Who | Task |
|------|-----|------|
| Pre-flight | Don | UpdraftPlus full backup of live site — download off-server |
| Pre-flight | Don | Run all tests on staging — every page, every flow |
| Pre-flight | Don | Confirm Stripe is in **live mode** (not test mode) |
| Deploy | Don | cPanel → Staging → Push to Live |
| Verify | Don | All pages load on atmyboat.com |
| Verify | Don | Register, pair device, Fix My Pi flow end-to-end |
| Verify | Don | Stripe live checkout completes for T2 and T3 |
| Post-deploy | Don | Rotate Gemini API key |
| Post-deploy | Don | Change FTP password |
| Post-deploy | Don | Set GitHub repo to Private (if not already) |

**End of Session 8:** atmyboat.com fully live with all features.

---

## PART 6 — OPERATOR ACTIONS REQUIRED BEFORE SESSION 6

These cannot be done by Claude — they require Don's access to HostPapa and Stripe.

| # | Action | Why | Where |
|---|--------|-----|-------|
| 1 | **Authorize GitHub push** — say "push to GitHub" at session start | 2 commits never backed up | Claude pushes, Don confirms |
| 2 | **Create mobile/config.php** from config.php.example | All mobile APIs fail without it | phpMyAdmin or FTP |
| 3 | **Import setup/mobile-schema.sql** via phpMyAdmin | 7 tables must exist before any API test | phpMyAdmin on staging |
| 4 | **Run setup/install-pages.php** once, then delete it | Creates all 17 WP pages in DB | Browser on staging |
| 5 | **Review SESSION6_CONTENT_PLAN.md** and approve | Don must confirm all page content before building | Read + reply with approval |
| 6 | **Answer 6 questions** at bottom of SESSION6_CONTENT_PLAN.md | T3 vessel limit, contact email, About photo, etc. | Reply in chat |
| 7 | **Authorize 2B CSS font fix** | 3 lines pending since this session | Say "apply 2B CSS fix" |

---

## PART 7 — WHAT THE FORUM ON GITHUB IS AND WHEN IT GETS USED

**The repo** `github.com/SkipperDon/atmyboat-forum` contains all the WordPress child theme code for atmyboat.com — every page, every API, the database schema, the design system. It is the entire website codebase.

**Current state:** 2 commits, never pushed. Code exists only on this laptop.

**When it gets used:**
- **Session 6, first action:** Push all existing code to GitHub (2 commits, 39 files). This creates the backup and version history. **Requires Don's authorization** per git policy.
- **Every session after:** Each session's commit gets pushed to GitHub at session end.
- **Phase 4:** GitHub becomes the source of truth for the live codebase.

**Important:** The repo must be set to **Private** before the first push. The code contains business logic, page structure, and API design that is proprietary. The d3kOS repo is public (GPL v3 open source). The atmyboat-forum repo is the commercial platform — it stays private.

To set private (Don's task):
1. Go to `github.com/SkipperDon/atmyboat-forum`
2. Settings → Danger Zone → Change repository visibility → Private

---

*Master Build Schedule v1.0 · 2026-03-24*
*Cross-references: SESSION6_CONTENT_PLAN.md · PROJECT_CHECKLIST.md · ATMYBOAT_BUILD_REFERENCE.md*
