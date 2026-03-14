# AtMyBoat.com v0.9.3 — Project Checklist

**Last Updated:** 2026-03-13 — Session 2026-03-13

---

## Phase 0 — Repo & Staging Setup
- [✅] GitHub repo `atmyboat-forum` created
- [✅] Staging environment on HostPapa confirmed working
- [✅] FTP access established (`d3kos@atmyboat.com` — lands at `/public_html`)
- [✅] Child theme directory created on staging

## Phase 1 — bbPress Forum
- [✅] bbPress installed on staging
- [✅] Forum at `/forum/` slug confirmed

## Phase 2A — MailPoet Email
- [ ] MailPoet configured for forum notification emails

## Phase 2B — AODA CSS & Design System
- [✅] `style.css` — design system (navy/amber/teal, fonts, custom properties)
- [✅] `bbpress.css` — bbPress forum styling
- [✅] `functions.php` — stylesheet enqueue, skip-to-content, mobile bottom nav
- [✅] `.gitignore` — blocks config file and logs from git
- [✅] Child theme activated on staging WP Admin
- [🔄] Font sizes — body/buttons/tags/labels all increased; some elements may still need adjustment (screenshot pending from Don)

## Phase 2C — AI Assistant
- [✅] `inc/ai-assistant.php` — Gemini API backend (RAG + bbPress context)
- [✅] `inc/ai-widget.php` — `[atmyboat_ai]` shortcode + JS
- [✅] AJAX handler in `functions.php` — nonce, rate limiting, sanitization
- [✅] `inc/atmyboat-config.php` — fixed constant names on staging server (GEMINI_API_KEY)
- [✅] AI widget renders and submits on staging
- [⚠️] Gemini free tier: 20 requests/day limit — quota burned in testing 2026-03-13; resets midnight UTC. **Don must rotate API key** (exposed in chat session — see SESSION_LOG.md security note)

## Phase 2D — Products Hub
- [✅] `page-products.php` — listing + single product views
- [✅] `inc/products.json` — 3 products (d3kOS, CX5106, PiCAN-M)
- [✅] Products page created in WP Admin with slug `products`
- [✅] Products page renders on staging

## Phase 2E — SEO
- [ ] Yoast/RankMath configured for forum and products pages
- [ ] XML sitemap submitted to Google Search Console
- [ ] Bing Webmaster Tools verification

## Phase 3 — AODA Compliance Audit (Don's task)
- [ ] Keyboard navigation test (Tab through all interactive elements)
- [ ] WAVE accessibility scan — zero errors target
- [ ] Mobile touch target check (all buttons ≥ 48×48px)
- [ ] Contrast ratio verification (4.5:1 minimum)
- [ ] Screen reader test

## Phase 4 — Staging → Live (Don's hands only)
- [ ] UpdraftPlus full backup of live site before push
- [ ] cPanel Staging → Push to Live
- [ ] Post-push smoke test (forum, products, AI widget)
- [ ] GitHub repo set to Private

## Post-Launch
- [ ] Monitor Gemini API usage (stay within free tier or upgrade)
- [ ] UAT with real users (target: boaters 45–70)
- [ ] Consider upgrading Gemini API key to paid tier if 20 req/day insufficient

---

## Node-RED Flow Verification (do after AtMyBoat.com APIs are live)

Node-RED on the Pi has flows with placeholder URLs waiting for v0.9.3 API endpoints.
These flows fail silently today — that is intentional and expected.
Once v0.9.3 APIs are deployed, each flow must be verified end-to-end.

**Flows to verify (Pi: ~/.node-red/flows.json):**

- [ ] `POST atmyboat.com/api/telemetry/push` — telemetry payload from Signal K reaching AtMyBoat.com. Verify HTTP 200, data appears in central DB.
- [ ] `POST atmyboat.com/api/community/benchmark` (Submit Benchmark) — engine benchmark data posting correctly. Verify HTTP 200, no 4xx/5xx.
- [ ] `POST atmyboat.com/api/community/position` — GPS position posting. Verify HTTP 200. Confirm only posting when user has opted in (privacy check).
- [ ] `POST your-community-db-api.com/logs` (Post to Community DB) — **placeholder URL must be replaced** with real AtMyBoat.com endpoint before testing. Two nodes use this URL — update both.
- [✅] `GET http://localhost:3000/signalk/v1/api/vessels/self` — **FIXED 2026-03-14** — updated to `http://localhost:8099/signalk/v1/api/vessels/self`. All 4 stale :3000/signalk references in flows.json corrected. Node-RED restarted and verified active.
- [ ] `Check cloud-credentials.json` — create `/opt/d3kos/config/cloud-credentials.json` with AtMyBoat.com API key. Verify flow reads it and sets `msg.skip = false`.
- [ ] Run all flows for 24 hours — confirm no error codes in Node-RED debug panel
- [ ] Confirm no 4xx or 5xx responses in Node-RED HTTP request nodes
- [ ] Verify no credentials are hardcoded in any flow node — all must read from cloud-credentials.json

**Note:** `cloud-credentials.json` is in `.gitignore` — never commit it. Contains AtMyBoat.com API key.

---

**Security Action Required:**
- [ ] Don rotates Gemini API key in Google AI Studio
- [ ] Don updates `atmyboat-config.php` on staging server with new key
- [ ] Don changes FTP password for `d3kos@atmyboat.com`
