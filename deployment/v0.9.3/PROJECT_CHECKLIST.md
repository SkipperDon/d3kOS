# d3kOS v0.9.3 — atmyboat.com Website
**Status: PENDING — starts after v0.9.2 Pi fixes confirmed complete**
**Spec:** `ATMYBOAT_CLAUDE_CODE_SPEC.md` (March 2026, Donald Moskaluk Consulting)
**Target:** Next.js 15 website at atmyboat.com — T0/T1/T2/T3 tiers, dashboard, B2B portal
**Stack:** Next.js 15 · React 19 · TypeScript · Supabase · Stripe · Claude API · Vercel · Cloudflare

---

## Prerequisites (before any coding)

- [ ] Supabase project created — copy URL + anon key + service role key
- [ ] Stripe account + T2 price ($9.99/mo) + T3 price ($99.99/yr) + B2B prices created
- [ ] Resend account — `don@atmyboat.com` sending domain verified
- [ ] Anthropic API key (for First Mate widget)
- [ ] Vercel account linked to GitHub repo `github.com/SkipperDon/atmyboat-web`
- [ ] Cloudflare DNS for `atmyboat.com` pointing to Vercel
- [ ] VAPID keys generated (`npx web-push generate-vapid-keys`)
- [ ] `.env.local` populated (see spec Part 5 for all variable names)

---

## Phase 1 — Launch (~15 developer days)

### Days 1–3: Scaffold & Infrastructure
- [ ] `npx create-next-app@latest atmyboat-web --typescript --tailwind --app` — create project
- [ ] Full folder structure created (see spec Part 3 — all 45 routes scaffolded)
- [ ] Design system: CSS custom properties (navy/teal/amber/cream/charcoal + dashboard vars)
- [ ] Google Fonts: Playfair Display + Inter (marketing) + Roboto Mono (dashboard)
- [ ] Supabase: run full schema SQL (spec Part 4 — all tables, enums, RLS, pg_cron jobs)
- [ ] `.env.local` configured with all variables from spec Part 5
- [ ] `middleware.ts` — protects `/dashboard/*` (T1+), `/b2b/dashboard` etc. (b2b_session)
- [ ] Reusable UI primitives: `Button.tsx`, `Card.tsx`, `Badge.tsx`, `TierGate.tsx`, `LastSeenIndicator.tsx`

### Days 4–6: Public Marketing Pages
- [ ] `NavBar.tsx` — all main page links, Login/Register CTAs
- [ ] `Footer.tsx` — nav links, GPL v3 notice, Anthropic attribution
- [ ] `/` Landing — The Dock (hero video placeholder + 3 sections + live Supabase counters)
- [ ] `/d3kos` — product page (~$500 vs $5,000+, 6 feature blocks, CX5106 hero)
- [ ] `/hardware` — BOM table (Option A/B/C), waitlist form → Supabase `waitlist` table
- [ ] `/download` — release card (v2.0-T3), flash steps, SHA256, T0 privacy callout

### Days 7–9: Auth & Payments
- [ ] `/login` — Supabase Auth email/password + OAuth (Google optional)
- [ ] `/register` — 5-step T1 flow: email → boat details → device QR/serial → consent → welcome
  - [ ] QR scanner using `html5-qrcode` — pre-populate from `?device=[ID]` URL param
  - [ ] 4 separate consent checkboxes (CASL/GDPR: tos / privacy / telemetry / newsletter)
- [ ] `/auth/callback` — Supabase OAuth callback handler
- [ ] `/subscribe` — 4-column tier cards (T1 highlighted), full feature matrix, FAQ
  - [ ] Stripe Checkout for T2 ($9.99/mo) and T3 ($99.99/yr)
- [ ] `POST /api/stripe/webhook` — handle `checkout.session.completed`, `subscription.deleted`, `invoice.payment_failed`
- [ ] `POST /api/stripe/create-checkout` — create Stripe session server-side

### Days 10–12: Dashboard & Telemetry
- [ ] Dashboard shell — dark theme (`#0A0A0A`), 240px sidebar, header with boat name + last-seen + tier badge
- [ ] `/dashboard` — The Chart Room: BoatCard, LastPosition Leaflet map, Engine Gauges (RPM/temp/fuel/battery), Quick Stats, Recent Alerts, T1 Upgrade CTA
- [ ] `TelemetryRealtimeHook.tsx` — Supabase Realtime subscription on `telemetry_events` for live gauge updates
- [ ] `GPSMap.tsx` — Leaflet + OpenStreetMap, dark tiles `#0A0A0A`, OpenSeaMap overlay
- [ ] `GaugePanel.tsx` — green/amber/red thresholds, 22px min font, Roboto Mono values
- [ ] `POST /api/telemetry/push` — validate `device_api_key`, check T1+, insert event, update `boats.last_lat/lng`
- [ ] `GET /api/d3kos/releases/latest.json` — OTA manifest from env vars, `Cache-Control: max-age=3600`
- [ ] `POST /api/auth/register-device` — generate boat_id + device_api_key, create boats row, return credentials

### Days 13–15: AI, Docs, Legal, SEO, Deploy
- [ ] `FirstMateWidget.tsx` — fixed bottom-right, teal button, slide-up 380px chat panel
- [ ] `POST /api/first-mate` — server-side Claude API proxy (`claude-sonnet-4-20250514`, 500 max_tokens)
  - [ ] System prompt: AtMyBoat First Mate persona with routing rules (see spec Part 7)
  - [ ] Rate limiting: max 20 req/min per IP (in-memory Map)
- [ ] `/compatible` — 4-step checker (make → model/year → boat type → result), save to `compatibility_checks`
- [ ] `POST /api/compatibility` — CX5106 DIP switch preview in response
- [ ] `/docs` hub + all 7 sub-pages (quickstart, hardware, cx5106, voice, faq, changelog, api-reference)
- [ ] Legal pages: `/privacy`, `/terms`, `/warranty`, `/shipping`, `/license`
- [ ] `/contact` page with AI routing suggestions
- [ ] SEO: per-page metadata (see spec Part 10 table), OG tags, structured data
- [ ] `/public/robots.txt` — disallow `/dashboard`, `/b2b`
- [ ] `/public/sitemap.xml` via `next-sitemap`
- [ ] `/public/.well-known/security.txt` — `security@atmyboat.com`
- [ ] Vercel deployment — set all env vars in Vercel dashboard
- [ ] Cloudflare: DNS → Vercel, HTTPS enforce, HSTS header

---

## Phase 2 — Community (Month 2–3)

- [ ] Flarum forum at `community.atmyboat.com` — deploy on VPS ($5/mo) or HostPapa
  - [ ] MySQL database, required plugins (tags/mentions/likes/markdown/user-bio/sso)
  - [ ] 3 initial categories, seed 15 threads (Skipper Don manual)
  - [ ] SSO with Supabase JWT via `fof/sso` plugin
- [ ] Forum thread embed on landing page Section 3 (Flarum REST API)
- [ ] `/blog` Captain's Log — MDX or Supabase-backed, `[slug]` pages
- [ ] Dashboard pages: `/dashboard/logs` (voyage table), `/dashboard/marine-vision` (gallery), `/dashboard/helm-ai` (session history), `/dashboard/chart` (full GPS map), `/dashboard/alerts` (settings + history), `/dashboard/my-boat` (profile + registration), `/dashboard/account` (settings, Go Private toggle)
- [ ] `POST /api/notify` — webhook from n3-k1: Web Push + Resend email + (T2) Twilio SMS, insert `geofence_alerts`
- [ ] Alert settings page — geofence radius, engine thresholds, battery V, SMS config
- [ ] Directory: `/directory` hub + 4 category pages with Leaflet map + sidebar filters
- [ ] `/directory/[slug]` — listing page: hero, contact (T1+ for Verified+), reviews, quote request → `lead_referrals`
- [ ] `/directory/manage` — edit form, view stats from `listing_analytics`
- [ ] `/story` — Skipper Don origin story page
- [ ] `/hall-of-fame` — Old Boat New Brain community stories
- [ ] `/marketplace` — Coming Soon shell with email capture (Phase 2 full: listing grid, messaging)
- [ ] `/academy` — Coming Soon shell with YouTube preview (Phase 2 full: course grid, enrollment)
- [ ] `/features` — feature request portal, save to `feature_requests` table

---

## Phase 3 — Revenue (Month 3–6)

- [ ] T2 feature gates enforced: advanced analytics (`/dashboard/analytics`), Marine Vision video, Helm AI history
- [ ] B2B portal — `/b2b/subscribe`: 3 plan cards + Claude AI qualification (5 questions) + DPA e-sign + Stripe
- [ ] `/b2b/dashboard` — usage stats, data freshness
- [ ] `/b2b/datasets` — filter panel, row preview, download
- [ ] `/b2b/reports`, `/b2b/api` (Harbor+), `/b2b/account`
- [ ] Supabase B2B views: `b2b_route_patterns`, `b2b_engine_benchmarks` (spec Part 7 — min 5 boats, anonymised)
- [ ] `/api/b2b/[endpoint]` — routes/engines/fuel/alarms/seasonal queries against B2B views
- [ ] `/data-services` — B2B marketing page with Claude AI qualification chat
- [ ] `/challenges` — sponsored challenges system, Flarum integration
- [ ] `/academy` — full YouTube-based course library, enrollment, certificates
- [ ] `/marketplace` — full buy/sell listing grid, buyer messaging
- [ ] Affiliate click tracking (`affiliate_clicks` table)
- [ ] Directory lead routing: auto-email to business via Resend + `lead_referrals` fee tracking
- [ ] Directory listing analytics dashboard for business owners
- [ ] `/dashboard/fleet` (T3) — fleet GPS map, multi-boat management
- [ ] SMS alerts via Twilio (T2+ with `sms_number` configured)

---

## Phase 4 — Scale (Month 6+)

- [ ] Native mobile app (React Native — shares TypeScript types)
- [ ] PDF voyage report generation
- [ ] Fleet GPS map with clustering (T3)
- [ ] Predictive maintenance AI (fleet-wide analysis)
- [ ] Route optimisation AI
- [ ] Marina booking integration
- [ ] NOAA/Environment Canada weather overlay

---

## d3kOS Pi Side Changes Required (Part 14 of spec)

These are firmware changes needed on the Pi before website features go live:

- [ ] **QR URL update** — onboarding QR encodes `https://atmyboat.com/register?device=[INSTALLATION_ID]&tier=t0&version=[FIRMWARE]`
- [ ] **Registration handshake** — new port 8091 endpoints on Pi:
  - `POST /api/link` — receives `{boat_uuid, device_api_key, supabase_url}`, writes `cloud-credentials.json`
  - `GET /api/status` — returns `{tier, firmware_version, uptime, last_push}`
- [ ] **`/opt/d3kos/config/cloud-credentials.json`** — new file (T1+ only, gitignored)
- [ ] **Node-RED telemetry flow** — POST to `/api/telemetry/push` every 60s with Bearer auth, SQLite offline buffer at `/opt/d3kos/data/telemetry-buffer.db`
- [ ] **Node-RED alarm webhook** — POST to `/api/notify` on WARNING/CRITICAL
- [ ] **Force password change** — onboarding Step 1 forces change from default `pi` password (EU CRA, NIST requirement)

---

## Security Checklist (run before go-live)

- [ ] `ANTHROPIC_API_KEY` absent from client bundle (`next build` + `grep`)
- [ ] `SUPABASE_SERVICE_ROLE_KEY` absent from client bundle
- [ ] All `/api/*` routes validate auth before data access
- [ ] Telemetry push validates `device_api_key` before insert
- [ ] Stripe webhook validates `Stripe-Signature` header
- [ ] RLS enabled on all user-data tables (already in schema SQL)
- [ ] Rate limiting on `/api/first-mate` (20 req/min/IP)
- [ ] HTTPS enforced via Cloudflare
- [ ] HSTS: `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- [ ] CSP header (allow Supabase, Stripe, Anthropic, Leaflet CDN domains)
- [ ] `/public/.well-known/security.txt` deployed

---

## Ollama Build Strategy

When v0.9.2 is done and we start v0.9.3, the executor approach changes:
- **Target**: `atmyboat-web/` repo (new Next.js project, not Pi deployment)
- **Strategy**: Ollama generates TypeScript/React components, Claude reviews architecture
- **Executor**: New `ollama_execute_v0.9.3.py` — generate file by file, verify each, write to disk
- **Verify agent**: Same TrueNAS verify agent (`http://192.168.1.103:11436`) — update critic prompt for TypeScript/Next.js review
- **No deployment gate**: website files write to local `atmyboat-web/` dir; no SSH/SCP needed
- **Phases**: Run executor per-phase (Phase 1 first — get it live, then add phases)

---

*Spec version: 1.0 · March 2026 · Donald Moskaluk Consulting*
*Full spec: `ATMYBOAT_CLAUDE_CODE_SPEC.md`*
