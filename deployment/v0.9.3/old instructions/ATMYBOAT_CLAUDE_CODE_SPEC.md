# ATMYBOAT.COM — COMPLETE BUILD SPECIFICATION FOR CLAUDE CODE
**Version 1.0 · March 2026 · Donald Moskaluk Consulting**
**Classification: Authoritative build document — all decisions made, no ambiguity**

---

## READ THIS FIRST — HOW TO USE THIS DOCUMENT

This is a single, self-contained specification. Every architectural decision has been made. Every route is defined. Every database table is specified as executable SQL. Every environment variable is named.

**Your job as Claude Code is to build exactly what is described here — do not invent alternatives, do not ask for clarification on what is specified, do not substitute technologies.**

When you encounter a section marked `[BUILD THIS]`, implement it completely. When you see `[DEFER — Phase 2+]`, scaffold the route/component but leave it as a placeholder with a "Coming Soon" state.

---

## PART 1 — PROJECT OVERVIEW

### What This Is

**atmyboat.com** is the web platform for **d3kOS** — an open-source marine operating system that runs on the **n3-k1** (Raspberry Pi 4B-based custom hardware). The website serves four audiences simultaneously:

1. **Boaters (45–70 years old)** who want to upgrade their boat's electronics cheaply (~$500 vs $5,000+)
2. **The open source community** who want to hack on marine software
3. **Commercial operators** who want fleet telemetry and analytics
4. **The marine industry** (dealers, marinas, installers) who want to reach verified boat owners

### The Four Tiers — Memorise These, They Gate Everything

| Tier | Name | Price | What It Is |
|------|------|-------|------------|
| **T0** | Open Water | Free | Standalone d3kOS on n3-k1. Zero internet. 100% private. No account. |
| **T1** | First Mate | Free | T0 + website dashboard + mobile app + data sharing (opt-in). No credit card ever. |
| **T2** | Skipper | $9.99/month | All T1 + advanced analytics, AI insights, Marine Vision video, SMS alerts, one-click OTA updates. |
| **T3** | Admiral | $99.99/year | All T2 + unlimited fleet management, fleet GPS map, commercial data export. |

**T0 is architecturally offline.** The n3-k1 in T0 mode cannot phone home. No credentials file exists on the device. This is a core legal and brand promise — never gate anything in a way that implies T0 can connect.

---

## PART 2 — TECHNOLOGY STACK (ALL FREE OR LOW-COST)

Every technology choice here maximises free tiers. Monthly cost at launch: **$0–$20/month**.

### Core Framework
```
Next.js 15 (App Router, TypeScript)
Tailwind CSS v3
React 19
```

### Backend & Database
```
Supabase (FREE tier: 500MB database, 50,000 monthly active users, 1GB file storage)
  - PostgreSQL database
  - Supabase Auth (replaces NextAuth — free, no setup)
  - Supabase Realtime (live telemetry updates — free)
  - Supabase Storage (Marine Vision media — free up to 1GB)
  - Supabase Edge Functions (serverless — free 500K invocations/month)
```

### Hosting & CDN
```
Vercel (FREE hobby tier — perfect for Next.js, 100GB bandwidth/month)
  OR HostPapa (already paid — deploy as Node.js app)
Cloudflare (FREE — DNS, CDN, DDoS protection, SSL, HSTS)
```

### Payments
```
Stripe (FREE to set up — pay 2.9% + $0.30 per transaction only)
```

### Email
```
Resend (FREE tier: 3,000 emails/month, 100/day — sufficient for launch)
```

### Forum
```
Flarum (FREE open source — self-hosted on HostPapa shared hosting or separate $5/mo VPS)
  Subdomain: community.atmyboat.com
```

### Maps
```
Leaflet.js + OpenStreetMap (FREE — no API key, no billing, no limits)
  OpenSeaMap overlay for nautical charts (FREE)
```

### Analytics
```
Umami (FREE self-hosted on Vercel — privacy-first, GDPR compliant, replaces Plausible $9/mo)
  Deploy to: analytics.atmyboat.com
```

### AI — First Mate Widget
```
Anthropic Claude API (claude-sonnet-4-20250514)
  Cost: ~$0.003 per conversation — budget $10–30/month at launch
  Server-side only — API key never exposed to client
```

### Video Courses (Phase 3)
```
Cloudflare Stream ($5/month per 1,000 minutes stored — cheapest video hosting)
  OR: YouTube unlisted embeds (FREE — free forever, zero infrastructure)
  Recommendation: YouTube embeds at launch, migrate to Cloudflare Stream when revenue justifies
```

### Push Notifications
```
Web Push API — native browser, FREE, no third party
  vapid keys generated once, stored in env vars
```

### SMS (T2+ alerts only)
```
Twilio — $0.0075 USD per SMS
  Only charged when T2 user receives an SMS alert
  Defer setup until first T2 subscriber
```

### Version Control & CI/CD
```
GitHub (FREE) — repo: github.com/SkipperDon/atmyboat-web (separate from d3kOS repo)
Vercel auto-deploys on push to main (FREE)
```

### Total Monthly Cost at Launch
```
Vercel:     $0 (free tier)
Supabase:   $0 (free tier)
Cloudflare: $0 (free)
Resend:     $0 (free tier)
Claude API: ~$10–30 (actual usage)
Umami:      $0 (self-hosted on Vercel free tier)
Flarum VPS: $5 (cheapest VPS) OR $0 (on existing HostPapa)
─────────────────────────────────────────
TOTAL:      $15–35/month
```

---

## PART 3 — PROJECT STRUCTURE

```
atmyboat-web/
├── app/                          # Next.js App Router
│   ├── (public)/                 # Public routes — no auth required
│   │   ├── page.tsx              # / Landing — The Dock
│   │   ├── story/page.tsx        # /story — Skipper Don
│   │   ├── d3kos/page.tsx        # /d3kos — Product page
│   │   ├── hardware/page.tsx     # /hardware — BOM + shop
│   │   ├── download/page.tsx     # /download — Image download
│   │   ├── compatible/page.tsx   # /compatible — Compatibility checker
│   │   ├── subscribe/page.tsx    # /subscribe — Tier plans
│   │   ├── app/page.tsx          # /app — Mobile app pre-launch
│   │   ├── blog/                 # /blog — Captain's Log
│   │   │   ├── page.tsx
│   │   │   └── [slug]/page.tsx
│   │   ├── features/page.tsx     # /features — Feature request portal
│   │   ├── data-services/page.tsx# /data-services — B2B marketing
│   │   ├── directory/            # /directory — Business directory
│   │   │   ├── page.tsx
│   │   │   ├── installers/page.tsx
│   │   │   ├── dealers/page.tsx
│   │   │   ├── marinas/page.tsx
│   │   │   ├── service/page.tsx
│   │   │   └── [slug]/page.tsx
│   │   ├── marketplace/page.tsx  # /marketplace — Buy/Sell
│   │   ├── academy/              # /academy — Skipper's Academy
│   │   │   ├── page.tsx
│   │   │   └── [slug]/page.tsx
│   │   ├── challenges/page.tsx   # /challenges — Sponsored contests
│   │   ├── hall-of-fame/page.tsx # /hall-of-fame
│   │   ├── contact/page.tsx      # /contact
│   │   ├── privacy/page.tsx      # /privacy
│   │   ├── terms/page.tsx        # /terms
│   │   ├── warranty/page.tsx     # /warranty
│   │   ├── shipping/page.tsx     # /shipping
│   │   └── license/page.tsx      # /license — GPL v3
│   │
│   ├── (auth)/                   # Auth routes
│   │   ├── login/page.tsx
│   │   ├── register/page.tsx     # /register?device=[ID] — QR deep link
│   │   └── callback/page.tsx     # Supabase OAuth callback
│   │
│   ├── dashboard/                # T1+ authenticated dashboard
│   │   ├── layout.tsx            # Dashboard shell — sidebar + header
│   │   ├── page.tsx              # /dashboard — The Chart Room home
│   │   ├── my-boat/page.tsx
│   │   ├── logs/page.tsx
│   │   ├── marine-vision/page.tsx
│   │   ├── helm-ai/page.tsx
│   │   ├── chart/page.tsx
│   │   ├── alerts/page.tsx
│   │   ├── analytics/page.tsx    # T2+ gated
│   │   ├── fleet/page.tsx        # T3 gated
│   │   └── account/page.tsx
│   │
│   ├── b2b/                      # B2B Intelligence Portal
│   │   ├── page.tsx              # /b2b — Login gate
│   │   ├── layout.tsx            # B2B portal shell
│   │   ├── dashboard/page.tsx
│   │   ├── datasets/page.tsx
│   │   ├── reports/page.tsx
│   │   ├── api/page.tsx          # Harbor+ only
│   │   ├── account/page.tsx
│   │   └── subscribe/page.tsx
│   │
│   ├── docs/                     # Documentation hub
│   │   ├── page.tsx
│   │   ├── quickstart/page.tsx
│   │   ├── hardware/page.tsx
│   │   ├── cx5106/page.tsx
│   │   ├── voice/page.tsx
│   │   ├── faq/page.tsx
│   │   ├── changelog/page.tsx
│   │   └── api-reference/page.tsx
│   │
│   └── api/                      # API routes (server-side only)
│       ├── auth/
│       │   └── register-device/route.ts    # Link n3-k1 to account
│       ├── telemetry/
│       │   └── push/route.ts               # Receive telemetry from n3-k1
│       ├── notify/route.ts                 # Receive alarm webhooks from n3-k1
│       ├── first-mate/route.ts             # Claude API proxy — server-side only
│       ├── compatibility/route.ts          # CX5106 engine checker
│       ├── stripe/
│       │   ├── webhook/route.ts
│       │   └── create-checkout/route.ts
│       ├── d3kos/
│       │   └── releases/latest.json/route.ts  # OTA manifest
│       ├── b2b/
│       │   └── [...endpoint]/route.ts      # B2B data API
│       └── push/
│           └── subscribe/route.ts          # Web Push subscription
│
├── components/
│   ├── layout/
│   │   ├── NavBar.tsx
│   │   ├── Footer.tsx
│   │   └── DashboardSidebar.tsx
│   ├── ui/                       # Reusable UI primitives
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Badge.tsx
│   │   ├── TierGate.tsx          # Wraps content, shows upgrade prompt if wrong tier
│   │   └── LastSeenIndicator.tsx # 🟢🟡🟠⚫ status dot
│   ├── first-mate/
│   │   ├── FirstMateWidget.tsx   # Floating chat button — present on all pages
│   │   └── FirstMateChat.tsx     # Chat panel
│   ├── dashboard/
│   │   ├── BoatCard.tsx
│   │   ├── GaugePanel.tsx        # Engine gauges (dark theme)
│   │   ├── GPSMap.tsx            # Leaflet map component
│   │   ├── VoyageLogTable.tsx
│   │   ├── AlertSettings.tsx
│   │   └── TelemetryRealtimeHook.tsx  # Supabase realtime subscription
│   ├── directory/
│   │   ├── ListingCard.tsx
│   │   ├── DirectoryMap.tsx
│   │   └── ReviewWidget.tsx
│   └── marketing/
│       ├── HeroSection.tsx
│       ├── TierComparisonTable.tsx
│       ├── BOMTable.tsx
│       └── CompatibilityChecker.tsx
│
├── lib/
│   ├── supabase/
│   │   ├── client.ts             # Browser client
│   │   ├── server.ts             # Server client (RSC + API routes)
│   │   └── middleware.ts         # Session refresh middleware
│   ├── stripe.ts
│   ├── resend.ts
│   ├── anthropic.ts              # Claude API client — SERVER ONLY
│   ├── webpush.ts
│   ├── tier.ts                   # Tier comparison helpers
│   └── telemetry.ts              # Telemetry payload types
│
├── types/
│   ├── database.ts               # Generated Supabase types
│   ├── telemetry.ts
│   └── d3kos.ts
│
├── middleware.ts                  # Auth middleware — protects /dashboard, /b2b
├── .env.local                     # Environment variables (see Part 5)
├── next.config.ts
├── tailwind.config.ts
└── package.json
```

---

## PART 4 — COMPLETE DATABASE SCHEMA

Run this SQL in Supabase SQL Editor to initialise the entire database. Execute in order.

```sql
-- ================================================================
-- ATMYBOAT.COM — COMPLETE DATABASE SCHEMA v2.2
-- Execute in Supabase SQL Editor
-- ================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_cron";        -- for automated retention jobs
CREATE EXTENSION IF NOT EXISTS "postgis";         -- for geospatial queries

-- ----------------------------------------------------------------
-- ENUMS
-- ----------------------------------------------------------------
CREATE TYPE subscription_tier AS ENUM ('t0', 't1', 't2', 't3');
CREATE TYPE listing_type AS ENUM ('installer', 'dealer', 'marina', 'service');
CREATE TYPE listing_tier AS ENUM ('basic', 'verified', 'premium', 'featured');
CREATE TYPE listing_status AS ENUM ('pending', 'active', 'suspended');
CREATE TYPE lead_type AS ENUM ('quote_request', 'insurance_referral', 'booking_referral');
CREATE TYPE lead_status AS ENUM ('sent', 'opened', 'converted', 'expired');
CREATE TYPE marketplace_condition AS ENUM ('new', 'like_new', 'good', 'fair', 'parts');
CREATE TYPE marketplace_status AS ENUM ('active', 'sold', 'expired', 'removed');
CREATE TYPE challenge_status AS ENUM ('draft', 'active', 'judging', 'complete');
CREATE TYPE b2b_plan AS ENUM ('buoy', 'harbor', 'admiral');
CREATE TYPE b2b_status AS ENUM ('active', 'suspended', 'cancelled', 'pending_dpa');
CREATE TYPE alert_type_enum AS ENUM (
  'geofence', 'geofence_clear', 'engine_critical', 'engine_warning',
  'low_battery', 'motion_detected', 'system_offline', 'firmware_update'
);

-- ----------------------------------------------------------------
-- USERS (extends Supabase auth.users)
-- ----------------------------------------------------------------
CREATE TABLE public.users (
  id                    UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email                 VARCHAR(255) UNIQUE NOT NULL,
  display_name          VARCHAR(100),
  subscription_tier     subscription_tier DEFAULT 't1',
  stripe_customer_id    VARCHAR(100),
  stripe_subscription_id VARCHAR(100),
  subscription_expires_at TIMESTAMPTZ,
  is_private_mode       BOOLEAN DEFAULT false,
  home_port             VARCHAR(200),
  data_consent          BOOLEAN DEFAULT false,
  newsletter_opt_in     BOOLEAN DEFAULT true,
  created_at            TIMESTAMPTZ DEFAULT NOW(),
  last_login_at         TIMESTAMPTZ
);

-- Auto-create user record on auth signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.users (id, email)
  VALUES (NEW.id, NEW.email);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ----------------------------------------------------------------
-- BOATS
-- ----------------------------------------------------------------
CREATE TABLE public.boats (
  id                    UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  owner_id              UUID REFERENCES public.users(id) ON DELETE CASCADE,
  installation_id       CHAR(16) UNIQUE,
  serial_number         VARCHAR(100),
  device_api_key        VARCHAR(100) UNIQUE,
  boat_name             VARCHAR(150),
  boat_make             VARCHAR(150),
  boat_model            VARCHAR(150),
  boat_year             SMALLINT,
  boat_type             VARCHAR(100),         -- power/sail/pontoon/commercial
  engine_make           VARCHAR(150),
  engine_model          VARCHAR(150),
  engine_year           SMALLINT,
  engine_hp             SMALLINT,
  benchmark_json        JSONB,
  cx5106_config_json    JSONB,
  last_lat              DECIMAL(9,6),
  last_lng              DECIMAL(9,6),
  last_seen_at          TIMESTAMPTZ,
  firmware_version      VARCHAR(50),
  is_active             BOOLEAN DEFAULT true,
  fleet_id              UUID,               -- FK added after fleets table
  registered_at         TIMESTAMPTZ DEFAULT NOW()
);

-- ----------------------------------------------------------------
-- FLEETS (T3 only)
-- ----------------------------------------------------------------
CREATE TABLE public.fleets (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  owner_id      UUID REFERENCES public.users(id) ON DELETE CASCADE,
  fleet_name    VARCHAR(200) NOT NULL,
  company_name  VARCHAR(200),
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.boats
  ADD CONSTRAINT fk_fleet FOREIGN KEY (fleet_id) REFERENCES public.fleets(id);

-- ----------------------------------------------------------------
-- TELEMETRY EVENTS (T1+ only — T0 never transmits)
-- ----------------------------------------------------------------
CREATE TABLE public.telemetry_events (
  id                      BIGSERIAL PRIMARY KEY,
  boat_id                 UUID REFERENCES public.boats(id) ON DELETE CASCADE,
  event_type              VARCHAR(100) NOT NULL,   -- gps_ping/engine_metric/alarm/vision_event/benchmark/system_health
  recorded_at             TIMESTAMPTZ NOT NULL,
  lat                     DECIMAL(9,6),
  lng                     DECIMAL(9,6),
  speed_knots             DECIMAL(6,2),
  heading_deg             DECIMAL(6,2),
  depth_ft                DECIMAL(8,2),
  engine_rpm              INTEGER,
  engine_temp_f           DECIMAL(6,2),
  fuel_level_pct          DECIMAL(5,2),
  battery_volts           DECIMAL(5,2),
  fresh_water_pct         DECIMAL(5,2),
  black_water_pct         DECIMAL(5,2),
  tilt_trim_deg           DECIMAL(6,2),
  pi_cpu_temp_c           DECIMAL(5,2),
  pi_cpu_pct              DECIMAL(5,2),
  pi_memory_pct           DECIMAL(5,2),
  nmea2000_device_count   SMALLINT,
  alarm_code              VARCHAR(100),
  alarm_severity          VARCHAR(20),             -- info/warning/critical
  payload_json            JSONB
);

-- Partition by month for performance (Supabase supports this)
CREATE INDEX idx_telemetry_boat_time ON public.telemetry_events (boat_id, recorded_at DESC);
CREATE INDEX idx_telemetry_event_type ON public.telemetry_events (event_type);

-- ----------------------------------------------------------------
-- VOYAGE LOGS
-- ----------------------------------------------------------------
CREATE TABLE public.voyage_logs (
  id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  boat_id             UUID REFERENCES public.boats(id) ON DELETE CASCADE,
  started_at          TIMESTAMPTZ NOT NULL,
  ended_at            TIMESTAMPTZ,
  duration_minutes    INTEGER,
  distance_nm         DECIMAL(8,2),
  avg_speed_kts       DECIMAL(6,2),
  max_speed_kts       DECIMAL(6,2),
  start_lat           DECIMAL(9,6),
  start_lng           DECIMAL(9,6),
  end_lat             DECIMAL(9,6),
  end_lng             DECIMAL(9,6),
  route_polyline      TEXT,                 -- Google encoded polyline
  fuel_used_gal       DECIMAL(8,2),
  engine_hours_added  DECIMAL(8,2),
  created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ----------------------------------------------------------------
-- HELM AI SESSIONS
-- ----------------------------------------------------------------
CREATE TABLE public.helm_ai_sessions (
  id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  boat_id     UUID REFERENCES public.boats(id) ON DELETE CASCADE,
  started_at  TIMESTAMPTZ NOT NULL,
  ended_at    TIMESTAMPTZ,
  messages    JSONB,                        -- [{role, content, ts}]
  topic_tags  TEXT[],
  lat         DECIMAL(9,6),
  lng         DECIMAL(9,6),
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- ----------------------------------------------------------------
-- MARINE VISION MEDIA
-- ----------------------------------------------------------------
CREATE TABLE public.marine_vision_media (
  id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  boat_id             UUID REFERENCES public.boats(id) ON DELETE CASCADE,
  media_type          VARCHAR(20),           -- photo/video
  storage_url         TEXT NOT NULL,         -- Supabase Storage URL
  captured_at         TIMESTAMPTZ,
  lat                 DECIMAL(9,6),
  lng                 DECIMAL(9,6),
  file_size_bytes     BIGINT,
  yolo_detections     TEXT[],
  ai_tags             TEXT[],
  created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ----------------------------------------------------------------
-- GEOFENCE ALERTS
-- ----------------------------------------------------------------
CREATE TABLE public.geofence_alerts (
  id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  boat_id           UUID REFERENCES public.boats(id) ON DELETE CASCADE,
  alert_type        alert_type_enum NOT NULL,
  triggered_at      TIMESTAMPTZ NOT NULL,
  lat               DECIMAL(9,6),
  lng               DECIMAL(9,6),
  geofence_radius_nm DECIMAL(6,2),
  message           TEXT,
  severity          VARCHAR(20),
  push_sent         BOOLEAN DEFAULT false,
  email_sent        BOOLEAN DEFAULT false,
  sms_sent          BOOLEAN DEFAULT false,
  acknowledged_at   TIMESTAMPTZ
);

-- ----------------------------------------------------------------
-- ALERT SETTINGS (per boat)
-- ----------------------------------------------------------------
CREATE TABLE public.alert_settings (
  boat_id                 UUID PRIMARY KEY REFERENCES public.boats(id) ON DELETE CASCADE,
  geofence_enabled        BOOLEAN DEFAULT false,
  geofence_radius_nm      DECIMAL(6,2) DEFAULT 0.25,
  geofence_home_lat       DECIMAL(9,6),
  geofence_home_lng       DECIMAL(9,6),
  engine_critical_push    BOOLEAN DEFAULT true,
  engine_critical_email   BOOLEAN DEFAULT true,
  battery_threshold_v     DECIMAL(4,2) DEFAULT 11.8,
  motion_alert_enabled    BOOLEAN DEFAULT false,
  offline_alert_hours     SMALLINT DEFAULT 2,
  sms_number              VARCHAR(20),
  push_subscription_json  JSONB               -- Web Push API subscription object
);

-- ----------------------------------------------------------------
-- COMPATIBILITY CHECKS
-- ----------------------------------------------------------------
CREATE TABLE public.compatibility_checks (
  id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  engine_make       VARCHAR(150),
  engine_model      VARCHAR(150),
  engine_year       SMALLINT,
  boat_type         VARCHAR(100),
  has_nmea2000      BOOLEAN,
  result            VARCHAR(20),              -- compatible/likely/unlikely/unknown
  result_notes      TEXT,
  cx5106_preview    JSONB,
  checked_at        TIMESTAMPTZ DEFAULT NOW(),
  converted_to_lead BOOLEAN DEFAULT false
);

-- ----------------------------------------------------------------
-- FEATURE REQUESTS
-- ----------------------------------------------------------------
CREATE TABLE public.feature_requests (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  feature_number  SERIAL UNIQUE,
  submitted_by    UUID REFERENCES public.users(id),
  title           VARCHAR(300) NOT NULL,
  description     TEXT,
  boat_type       VARCHAR(100),
  engine_make     VARCHAR(150),
  tier_at_time    subscription_tier,
  status          VARCHAR(50) DEFAULT 'submitted',  -- submitted/under_review/planned/in_progress/shipped/closed
  target_version  VARCHAR(50),
  vote_count      INTEGER DEFAULT 1,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ----------------------------------------------------------------
-- CONSENT LOG (CASL/GDPR — append-only, never update/delete)
-- ----------------------------------------------------------------
CREATE TABLE public.consent_log (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id         UUID REFERENCES public.users(id),
  consent_type    VARCHAR(100) NOT NULL,   -- tos/privacy/telemetry/voice_sync/vision_upload/newsletter/commercial_data
  granted         BOOLEAN NOT NULL,
  ip_address      INET,
  user_agent      TEXT,
  consent_version VARCHAR(50),            -- links to Privacy Policy version
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Make append-only
CREATE RULE consent_log_no_update AS ON UPDATE TO public.consent_log DO INSTEAD NOTHING;
CREATE RULE consent_log_no_delete AS ON DELETE TO public.consent_log DO INSTEAD NOTHING;

-- ----------------------------------------------------------------
-- FORUM / MARKETPLACE TABLES
-- ----------------------------------------------------------------
CREATE TABLE public.marketplace_listings (
  id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  seller_id           UUID REFERENCES public.users(id) ON DELETE CASCADE,
  title               VARCHAR(200) NOT NULL,
  category            VARCHAR(100),
  condition           marketplace_condition,
  price_cad           DECIMAL(10,2),
  description         TEXT,
  photos              TEXT[],
  location_city       VARCHAR(100),
  location_province_state VARCHAR(100),
  d3kos_compatible    BOOLEAN DEFAULT false,
  is_featured         BOOLEAN DEFAULT false,
  featured_until      TIMESTAMPTZ,
  status              marketplace_status DEFAULT 'active',
  views               INTEGER DEFAULT 0,
  created_at          TIMESTAMPTZ DEFAULT NOW(),
  expires_at          TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '60 days')
);

CREATE TABLE public.marketplace_messages (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  listing_id    UUID REFERENCES public.marketplace_listings(id) ON DELETE CASCADE,
  sender_id     UUID REFERENCES public.users(id),
  recipient_id  UUID REFERENCES public.users(id),
  body          TEXT NOT NULL,
  sent_at       TIMESTAMPTZ DEFAULT NOW(),
  read_at       TIMESTAMPTZ
);

CREATE TABLE public.course_catalog (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  slug            VARCHAR(200) UNIQUE NOT NULL,
  title           VARCHAR(200) NOT NULL,
  tagline         VARCHAR(300),
  instructor_name VARCHAR(150),
  price_cad       DECIMAL(8,2),
  duration_minutes INTEGER,
  lesson_count    SMALLINT,
  category        VARCHAR(100),
  video_ids       JSONB,                    -- [{lesson_title, duration_sec, youtube_id, is_free}]
  downloads       JSONB,                    -- [{title, storage_url}]
  is_published    BOOLEAN DEFAULT false,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE public.course_enrollments (
  id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id                 UUID REFERENCES public.users(id) ON DELETE CASCADE,
  course_id               UUID REFERENCES public.course_catalog(id),
  stripe_payment_intent_id VARCHAR(200),
  enrolled_at             TIMESTAMPTZ DEFAULT NOW(),
  completed_at            TIMESTAMPTZ,
  lessons_completed       INTEGER DEFAULT 0,
  certificate_issued      BOOLEAN DEFAULT false,
  certificate_url         TEXT,
  UNIQUE(user_id, course_id)
);

CREATE TABLE public.sponsored_challenges (
  id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  title               VARCHAR(200) NOT NULL,
  sponsor_brand       VARCHAR(200),
  sponsor_logo_url    TEXT,
  description         TEXT,
  prize_description   TEXT,
  entry_forum_thread_id VARCHAR(100),
  starts_at           TIMESTAMPTZ,
  ends_at             TIMESTAMPTZ,
  winner_user_id      UUID REFERENCES public.users(id),
  status              challenge_status DEFAULT 'draft',
  created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE public.affiliate_clicks (
  id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id           UUID REFERENCES public.users(id),   -- nullable (anonymous)
  affiliate_partner VARCHAR(100),
  destination_url   TEXT,
  source_context    VARCHAR(200),
  session_id        VARCHAR(100),
  clicked_at        TIMESTAMPTZ DEFAULT NOW(),
  converted         BOOLEAN DEFAULT false,
  commission_earned_cad DECIMAL(8,2)
);

-- ----------------------------------------------------------------
-- DIRECTORY TABLES
-- ----------------------------------------------------------------
CREATE TABLE public.directory_listings (
  id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  slug                VARCHAR(200) UNIQUE NOT NULL,
  listing_type        listing_type NOT NULL,
  business_name       VARCHAR(200) NOT NULL,
  contact_name        VARCHAR(150),
  email               VARCHAR(255),
  phone               VARCHAR(30),
  website_url         TEXT,
  address             TEXT,
  city                VARCHAR(100),
  province_state      VARCHAR(100),
  country             CHAR(2) DEFAULT 'CA',
  lat                 DECIMAL(9,6),
  lng                 DECIMAL(9,6),
  listing_tier        listing_tier DEFAULT 'basic',
  stripe_subscription_id VARCHAR(200),
  services            TEXT[],
  photos              TEXT[],
  description         TEXT,
  hours_json          JSONB,
  amenities           TEXT[],
  rating_average      DECIMAL(3,2) DEFAULT 0,
  review_count        INTEGER DEFAULT 0,
  verified_at         TIMESTAMPTZ,
  status              listing_status DEFAULT 'pending',
  created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_directory_type_location ON public.directory_listings (listing_type, lat, lng);
CREATE INDEX idx_directory_status ON public.directory_listings (status);

CREATE TABLE public.directory_reviews (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  listing_id    UUID REFERENCES public.directory_listings(id) ON DELETE CASCADE,
  reviewer_id   UUID REFERENCES public.users(id),
  rating        SMALLINT CHECK (rating BETWEEN 1 AND 5),
  body          TEXT,
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  is_published  BOOLEAN DEFAULT false,
  UNIQUE(listing_id, reviewer_id)
);

CREATE TABLE public.lead_referrals (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id       UUID REFERENCES public.users(id),
  listing_id    UUID REFERENCES public.directory_listings(id),
  lead_type     lead_type NOT NULL,
  message       TEXT,
  submitted_at  TIMESTAMPTZ DEFAULT NOW(),
  status        lead_status DEFAULT 'sent',
  fee_cad       DECIMAL(8,2),
  fee_invoiced  BOOLEAN DEFAULT false
);

CREATE TABLE public.listing_analytics (
  id          BIGSERIAL PRIMARY KEY,
  listing_id  UUID REFERENCES public.directory_listings(id) ON DELETE CASCADE,
  event_type  VARCHAR(50),                  -- view/quote_request/phone_click/website_click
  recorded_at TIMESTAMPTZ DEFAULT NOW(),
  session_id  VARCHAR(100)
);

-- ----------------------------------------------------------------
-- B2B PORTAL TABLES
-- ----------------------------------------------------------------
CREATE TABLE public.b2b_accounts (
  id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_name            VARCHAR(200) NOT NULL,
  industry                VARCHAR(100),
  contact_name            VARCHAR(150) NOT NULL,
  contact_email           VARCHAR(255) UNIQUE NOT NULL,
  plan                    b2b_plan NOT NULL,
  stripe_customer_id      VARCHAR(200),
  stripe_subscription_id  VARCHAR(200),
  billing_cycle_start     TIMESTAMPTZ,
  api_calls_this_month    INTEGER DEFAULT 0,
  dpa_signed_at           TIMESTAMPTZ,
  dpa_signer_name         VARCHAR(200),
  dpa_version             VARCHAR(50),
  status                  b2b_status DEFAULT 'pending_dpa',
  created_at              TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE public.b2b_api_keys (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  account_id    UUID REFERENCES public.b2b_accounts(id) ON DELETE CASCADE,
  key_name      VARCHAR(100),
  key_hash      VARCHAR(200) NOT NULL,      -- SHA-256 of actual key — never store plaintext
  key_prefix    CHAR(8),                    -- First 8 chars shown in UI (e.g. 'amb_k7f2')
  permissions   TEXT[],
  last_used_at  TIMESTAMPTZ,
  calls_total   BIGINT DEFAULT 0,
  expires_at    TIMESTAMPTZ,
  revoked_at    TIMESTAMPTZ,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE public.b2b_download_log (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  account_id      UUID REFERENCES public.b2b_accounts(id),
  user_email      VARCHAR(255),
  dataset_type    VARCHAR(100),
  filters_json    JSONB,
  row_count       INTEGER,
  format          VARCHAR(20),
  file_size_bytes BIGINT,
  downloaded_at   TIMESTAMPTZ DEFAULT NOW()
);

-- ----------------------------------------------------------------
-- ROW LEVEL SECURITY (RLS)
-- ----------------------------------------------------------------
-- Enable RLS on all user-data tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.boats ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.telemetry_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.voyage_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.helm_ai_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.marine_vision_media ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.geofence_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.alert_settings ENABLE ROW LEVEL SECURITY;

-- Users can only see their own data
CREATE POLICY "Users see own profile" ON public.users
  FOR ALL USING (auth.uid() = id);

CREATE POLICY "Users see own boats" ON public.boats
  FOR ALL USING (auth.uid() = owner_id);

CREATE POLICY "Users see own telemetry" ON public.telemetry_events
  FOR SELECT USING (
    boat_id IN (SELECT id FROM public.boats WHERE owner_id = auth.uid())
  );

-- Devices can INSERT telemetry using device_api_key (checked in API route)
-- Directory listings are public read
CREATE POLICY "Directory listings public read" ON public.directory_listings
  FOR SELECT USING (status = 'active');

-- Marketplace listings are public read
CREATE POLICY "Marketplace public read" ON public.marketplace_listings
  FOR SELECT USING (status = 'active');

-- ----------------------------------------------------------------
-- AUTOMATED DATA RETENTION (pg_cron)
-- ----------------------------------------------------------------
-- Delete T1 telemetry older than 12 months
SELECT cron.schedule('delete-t1-telemetry', '0 3 1 * *', $$
  DELETE FROM public.telemetry_events
  WHERE recorded_at < NOW() - INTERVAL '12 months'
  AND boat_id IN (
    SELECT b.id FROM public.boats b
    JOIN public.users u ON b.owner_id = u.id
    WHERE u.subscription_tier = 't1'
  );
$$);

-- Expire marketplace listings
SELECT cron.schedule('expire-marketplace', '0 4 * * *', $$
  UPDATE public.marketplace_listings
  SET status = 'expired'
  WHERE expires_at < NOW() AND status = 'active';
$$);
```

---

## PART 5 — ENVIRONMENT VARIABLES

Create `.env.local` with these exact variable names:

```bash
# ── Supabase ──────────────────────────────────────────
NEXT_PUBLIC_SUPABASE_URL=https://[your-project-ref].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=[your-anon-key]
SUPABASE_SERVICE_ROLE_KEY=[your-service-role-key]   # SERVER ONLY — never expose to client

# ── Stripe ────────────────────────────────────────────
STRIPE_SECRET_KEY=sk_live_[key]                      # SERVER ONLY
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_[key]
STRIPE_WEBHOOK_SECRET=whsec_[key]
STRIPE_T2_PRICE_ID=price_[id]                        # $9.99/mo
STRIPE_T3_PRICE_ID=price_[id]                        # $99.99/yr
STRIPE_B2B_BUOY_PRICE_ID=price_[id]                  # $199/mo
STRIPE_B2B_HARBOR_PRICE_ID=price_[id]                # $799/mo
STRIPE_B2B_ADMIRAL_PRICE_ID=price_[id]               # $2,499/mo

# ── Anthropic (Claude API) ────────────────────────────
ANTHROPIC_API_KEY=sk-ant-[key]                       # SERVER ONLY — never expose

# ── Resend (email) ────────────────────────────────────
RESEND_API_KEY=re_[key]
RESEND_FROM_EMAIL=don@atmyboat.com
RESEND_FROM_NAME=Skipper Don | AtMyBoat

# ── Web Push ──────────────────────────────────────────
VAPID_PUBLIC_KEY=[generated-vapid-public-key]
VAPID_PRIVATE_KEY=[generated-vapid-private-key]     # SERVER ONLY
VAPID_SUBJECT=mailto:don@atmyboat.com

# ── Twilio (SMS — T2+ only, configure when first T2 subscriber) ──
TWILIO_ACCOUNT_SID=AC[sid]
TWILIO_AUTH_TOKEN=[token]
TWILIO_FROM_NUMBER=+1[number]

# ── App Config ────────────────────────────────────────
NEXT_PUBLIC_APP_URL=https://atmyboat.com
NEXT_PUBLIC_APP_NAME=AtMyBoat
NODE_ENV=production

# ── OTA Update Config ─────────────────────────────────
D3KOS_LATEST_VERSION=2.0.0
D3KOS_LATEST_RELEASE_DATE=2026-02-22
D3KOS_DOWNLOAD_URL=https://drive.google.com/[share-link]
D3KOS_SHA256=51f5a3115c24f77b0998d06d7e4b31ca8b54418cb3791531d8e18538e53ec368
```

---

## PART 6 — DESIGN SYSTEM

### Colours (CSS custom properties in globals.css)
```css
:root {
  --navy:           #1B3A5C;   /* Primary headings, nav */
  --teal:           #0D7377;   /* Links, CTAs, sub-headings */
  --amber:          #D4820A;   /* Accents, callouts, section 3 headings */
  --cream:          #F5EDD8;   /* Warm section backgrounds */
  --charcoal:       #1A1A1A;   /* Body text */
  --dashboard-bg:   #0A0A0A;   /* Dashboard — mirrors d3kOS */
  --signal-green:   #00CC00;   /* Online / normal status */
  --warning-amber:  #FFA500;   /* Warning status */
  --critical-red:   #FF0000;   /* Critical / alert status */
  --offline-gray:   #666666;   /* Offline status */
}
```

### Typography
```css
/* Marketing pages */
font-family: 'Playfair Display', Georgia, serif;   /* Display headings — nostalgic editorial */
font-family: 'Inter', system-ui, sans-serif;        /* Body, sub-headings, UI */

/* Dashboard (mirrors d3kOS on-device) */
font-family: 'Roboto Mono', monospace;              /* Gauge values */
font-family: 'Roboto', sans-serif;                  /* Dashboard labels — 22px minimum */

/* Code blocks */
font-family: 'JetBrains Mono', 'Courier New', monospace;
```

### Nautical Copy — Use These Exact Strings
```
Page loading:     "Checking the charts..."
Saving data:      "Dropping anchor..."
404 error:        "Ran aground — couldn't find that page"
500 error:        "Engine's down. Our crew has been alerted."
Empty state:      "No voyages logged yet. Time to cast off."
Success toast:    "All fast."
Delete confirm:   "Are you sure, Captain?"
```

### Component Conventions
- **TierGate component**: Wraps any T2/T3-only content. Shows blurred content with upgrade CTA overlay if wrong tier. Never hides — always teases.
- **LastSeenIndicator**: `🟢 Live` (<2min), `🟡 Recent` (2-60min), `🟠 Offline` (1-24hr), `⚫ No Data` (>24hr)
- **Dashboard theme**: Black background `#0A0A0A`, all widgets use `border: 1px solid #333`, no white backgrounds in the dashboard shell.

---

## PART 7 — PAGE-BY-PAGE SPECIFICATIONS

### `[BUILD THIS]` / Landing Page — The Dock

**Route:** `/`

**Purpose:** Convert three simultaneous audiences: the nostalgic boater (feel section), the tech searcher (product section), the community member (social section).

**Sections (in order):**

1. **Hero** — Full-screen video background (use a placeholder `<video>` tag with poster image at build time, Skipper Don will provide the actual video file). Headline: `"She's got 40 years of stories. Now she's got a brain."` Sub-headline: `"d3kOS — the AI-first marine electronics system for boats that deserve better."` Two CTAs: `Tell Me More` (scroll to section 2) and `I Want This` (→ /d3kos).

2. **Section 1 — The Feeling** — Three quote cards on cream background. Quotes: `"That smell of salt, diesel, and possibility on a Saturday morning."` / `"The engine that always starts... eventually."` / `"An anchorage so quiet you could hear the stars."` No tech, no specs.

3. **Section 2 — The Tech** — Navy background. Headline: `"But what if your old girl could think?"` Three feature cards: (a) ~$500 vs $5,000+ stat with dramatic typography, (b) Voice assistant demo (static image of d3kOS UI), (c) "100% offline — your data, your boat, your call". CTA: `See the Hardware →`

4. **Section 3 — The Community** — Teal background. Live counter (pulled from Supabase): `X skippers aboard · X voyages logged · X nautical miles tracked`. Two CTAs: `Join Free (T1)` and `Get the Hardware`.

5. **Footer** — Navy background. Links: all main pages. GPL v3 notice: `"d3kOS is open source under GPL v3. Source: github.com/SkipperDon/d3kOS"`. Anthropic attribution: `"AI features powered by Claude"`.

---

### `[BUILD THIS]` / Product Page — d3kOS & n3-k1

**Route:** `/d3kos`

Lead with the price comparison: `~$500` in massive typography vs `$5,000+` crossed out. Then: what d3kOS does (6 feature blocks), hardware overview with BOM summary, CX5106 wizard as hero feature, 100% offline positioning. CTA: `/hardware` and `/download`.

---

### `[BUILD THIS]` / Hardware Page

**Route:** `/hardware`

**Three options presented:**

**Option A — Build It Yourself** — Full BOM table:
| Component | Spec | Est. Cost |
|-----------|------|-----------|
| Raspberry Pi 4B | 8GB RAM | $55–$75 |
| PiCAN-M HAT | NMEA2000 | $60 |
| MicroSD | 64GB A2 | $12–$20 |
| Touchscreen | 10.1" 1000-nit | $120 |
| DC-DC Converter | Victron Orion-Tr 12V→5V | $35 |
| USB GPS | VK-162 | $15 |
| USB AIS | dAISy | $80 |
| CX5106 Gateway | NMEA2000 engine interface | ~$80 |
| Enclosure | Marine mount | $20–$50 |
| **TOTAL** | | **~$477–$535** |

**Option B — Buy Assembled** — Waitlist form (email + boat type + region). Saves to Supabase `waitlist` table.

**Option C — Find an Installer** — Links to `/directory/installers`.

---

### `[BUILD THIS]` / Download Page

**Route:** `/download`

Current release card:
```
Version:   v2.0-T3 (Testing Build)
Released:  February 22, 2026
Size:      9.2 GB compressed
SHA256:    51f5a3115c24f77b0998d06d7e4b31ca8b54418cb3791531d8e18538e53ec368
Download:  [Google Drive Button]
```

Flash instructions as numbered steps (1–8, see Section 7.2 of Foundation). T0 privacy callout box. Version history table.

---

### `[BUILD THIS]` / Compatibility Checker

**Route:** `/compatible`

**4-step interactive flow** (client-side state, no page reload):
1. Select engine manufacturer (dropdown — populated from JSON, matches d3kOS onboarding wizard data)
2. Enter model and year (text input + number)
3. Select boat type (radio: power / sail / pontoon / commercial)
4. Click "Check Compatibility" → POST to `/api/compatibility` → returns result + CX5106 DIP switch preview

**Result states:** ✅ Compatible / ⚠️ Likely Compatible / ❌ Unlikely / ❓ Unknown

Save every check to `compatibility_checks` table (anonymised — no user ID required).

---

### `[BUILD THIS]` / Subscribe Page

**Route:** `/subscribe`

Four-column card layout:

| T0 Open Water | T1 First Mate ⭐ | T2 Skipper | T3 Admiral |
|---|---|---|---|
| Free | Free | $9.99/mo | $99.99/yr |
| [5 bullets] | [5 bullets] | [5 bullets] | [5 bullets] |
| Download d3kOS | Join Free | Subscribe | Contact Us |

T1 card gets `border-2 border-teal` "Most Popular" treatment.

Below cards: full feature matrix table (from Part 1). FAQ section: 5 questions.

**T1 Registration Flow** (multi-step, client-side):
1. Email + password
2. Boat details (name, type, home port)
3. Device registration — QR scanner (using `html5-qrcode` library, free) OR serial number text input
4. Granular consent checkboxes (each purpose separate — CASL/GDPR required)
5. Welcome — links to dashboard

If URL has `?device=[ID]` param (from n3-k1 QR scan): pre-populate device field on step 3.

---

### `[BUILD THIS]` / Dashboard — The Chart Room

**Route:** `/dashboard` (requires T1+ auth)

**Layout:** Dark theme. Left sidebar (240px) with nav links. Top header with boat name, last-seen indicator, and tier badge. Main content area.

**Home page widgets** (responsive grid, 2-col on desktop):
- **Boat Card** — vessel photo placeholder, name, home port, firmware version, tier badge, system health badge
- **Last Position Map** — Leaflet map, `#0A0A0A` background tiles from OpenStreetMap, marker at `boats.last_lat/lng`, last-seen timestamp
- **Engine Gauges** (T1+) — RPM gauge, Engine temp, Fuel level, Battery volts — latest from `telemetry_events`. Green/amber/red colour coding. 22px minimum font. Real-time via Supabase subscription.
- **Quick Stats** — Total voyages, Total nm, Engine hours
- **Recent Alerts** — Last 5 from `geofence_alerts`
- **Upgrade CTA** (T1 only) — soft card: "Unlock advanced analytics, AI insights, and one-click updates — $9.99/month"

**Supabase Realtime** — Subscribe to `telemetry_events` for the user's boat. When a new row arrives, update gauges without page reload.

```typescript
// In TelemetryRealtimeHook.tsx
const channel = supabase.channel('telemetry-live')
  .on('postgres_changes', {
    event: 'INSERT',
    schema: 'public',
    table: 'telemetry_events',
    filter: `boat_id=eq.${boatId}`
  }, (payload) => {
    updateGauges(payload.new)
  })
  .subscribe()
```

---

### `[BUILD THIS]` / AI First Mate Widget

**Present on every page** — floating button bottom-right, `position: fixed`.

**Implementation:**
- Button: `👋 Ask the First Mate` — teal background, opens slide-up chat panel
- Chat panel: 380px wide, full height on mobile, fixed on desktop
- Conversation history stored in React state (session only — no localStorage)
- Each message sent via POST to `/api/first-mate` (server-side Claude API proxy)

**`/api/first-mate/route.ts`:**
```typescript
import Anthropic from '@anthropic-ai/sdk'

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY })

const SYSTEM_PROMPT = `You are the AtMyBoat First Mate — a friendly, knowledgeable marine assistant for atmyboat.com.

You help boaters understand:
- d3kOS: the marine operating system for the n3-k1 hardware
- The four tiers: T0 (free, offline, private), T1 (free, with connectivity), T2 ($9.99/mo, premium), T3 ($99.99/yr, commercial fleet)
- The n3-k1 hardware (~$500 to build vs $5,000+ traditional systems)
- How to install, configure, and use d3kOS

ROUTING RULES:
- Hardware questions → suggest /hardware
- Download questions → suggest /download  
- Compatibility questions → suggest /compatible
- Pricing/tier questions → suggest /subscribe
- Support questions → suggest /contact
- Commercial/fleet → suggest /data-services or T3

TONE: Warm, nautical, knowledgeable. Use occasional nautical language naturally.
Do not use "ahoy" or "arr" — too cliché. Do use: "at the helm", "cast off", "chart a course", "drop anchor".

Keep responses concise — 2-4 sentences max unless explaining something complex.
Always suggest a relevant page link at the end of your response.`

export async function POST(req: Request) {
  const { messages } = await req.json()
  
  const response = await client.messages.create({
    model: 'claude-sonnet-4-20250514',
    max_tokens: 500,
    system: SYSTEM_PROMPT,
    messages
  })
  
  return Response.json({ 
    content: response.content[0].type === 'text' ? response.content[0].text : ''
  })
}
```

---

### `[BUILD THIS]` / Telemetry Ingest API

**Route:** `POST /api/telemetry/push`

Receives telemetry events from n3-k1 devices.

```typescript
// /api/telemetry/push/route.ts
export async function POST(req: Request) {
  const apiKey = req.headers.get('Authorization')?.replace('Bearer ', '')
  if (!apiKey) return Response.json({ error: 'Unauthorized' }, { status: 401 })
  
  const supabase = createSupabaseServerClient()
  
  // Validate device API key
  const { data: boat } = await supabase
    .from('boats')
    .select('id, owner_id')
    .eq('device_api_key', apiKey)
    .eq('is_active', true)
    .single()
  
  if (!boat) return Response.json({ error: 'Invalid device key' }, { status: 401 })
  
  // Validate user is T1+
  const { data: user } = await supabase
    .from('users')
    .select('subscription_tier')
    .eq('id', boat.owner_id)
    .single()
  
  if (!user || user.subscription_tier === 't0') {
    return Response.json({ error: 'T0 devices do not transmit' }, { status: 403 })
  }
  
  const payload = await req.json()
  
  // Insert telemetry event
  await supabase.from('telemetry_events').insert({
    boat_id: boat.id,
    ...payload
  })
  
  // Update boat's last position
  if (payload.lat && payload.lng) {
    await supabase.from('boats').update({
      last_lat: payload.lat,
      last_lng: payload.lng,
      last_seen_at: new Date().toISOString()
    }).eq('id', boat.id)
  }
  
  return Response.json({ ok: true }, { status: 201 })
}
```

---

### `[BUILD THIS]` / Alarm Notification API

**Route:** `POST /api/notify`

Receives alarm webhooks from n3-k1. Sends push notifications and email.

```typescript
// Validate device_api_key, look up boat, look up alert_settings
// If geofence or critical alarm: send Web Push to push_subscription_json
// If email enabled: send via Resend
// If T2+ and SMS configured: send via Twilio
// Insert into geofence_alerts table
// Return 200
```

---

### `[BUILD THIS]` / Device Registration API

**Route:** `POST /api/auth/register-device`

Called by website after T1 user registers. Links n3-k1 to account.

```typescript
// Generates a UUID v4 boat_id and a secure random device_api_key
// Creates boats row with installation_id, boat details
// Returns { boat_id, device_api_key, supabase_url, supabase_anon_key }
// n3-k1 saves this as /opt/d3kos/config/cloud-credentials.json
```

---

### `[BUILD THIS]` / OTA Manifest

**Route:** `GET /api/d3kos/releases/latest.json`

```typescript
export async function GET() {
  return Response.json({
    version: process.env.D3KOS_LATEST_VERSION,
    release_date: process.env.D3KOS_LATEST_RELEASE_DATE,
    download_url: process.env.D3KOS_DOWNLOAD_URL,
    sha256: process.env.D3KOS_SHA256,
    is_critical: false,
    release_notes_url: 'https://atmyboat.com/docs/changelog'
  }, {
    headers: { 'Cache-Control': 'public, max-age=3600' }
  })
}
```

---

### `[BUILD THIS]` / Stripe Webhook

**Route:** `POST /api/stripe/webhook`

Handle these events:
- `checkout.session.completed` → update `users.subscription_tier`, set `stripe_subscription_id`
- `customer.subscription.deleted` → downgrade user to `t1`
- `invoice.payment_failed` → send email via Resend, keep on current tier for 3-day grace

---

### `[BUILD THIS]` / B2B Intelligence Portal

**Route tree:** `/b2b/*`

The `/b2b` route checks for a separate `b2b_accounts` session (not Supabase auth — use a separate JWT stored in HttpOnly cookie).

**`/b2b/subscribe`** — Three plan cards (Buoy/Harbor/Admiral), AI qualification chat (5 questions using Claude API), generates sample brief, Stripe checkout, DPA e-signature (render DPA text in-page, require checkbox + typed name before Stripe checkout unlocks).

**`/b2b/dashboard`** — Usage stats (API calls, downloads this month), data freshness indicator, quick links to datasets/reports/API.

**`/b2b/datasets`** — Filter panel (dataset type, region, date range, vessel type, format). Preview shows row count and sample. Download button calls `/api/b2b/[endpoint]` which queries the anonymised aggregate views (see below).

**B2B Data Views (create in Supabase):**
```sql
-- These views produce the anonymised aggregate data sold to B2B customers
-- Never expose individual boat_id, user_id, or lat/lng in B2B outputs

CREATE VIEW b2b_route_patterns AS
SELECT
  DATE_TRUNC('week', recorded_at) AS week,
  ROUND(lat::numeric, 1) AS lat_bucket,     -- 0.1 degree = ~10km grid
  ROUND(lng::numeric, 1) AS lng_bucket,
  COUNT(DISTINCT boat_id) AS vessel_count,
  AVG(speed_knots) AS avg_speed,
  COUNT(*) AS data_points
FROM public.telemetry_events
WHERE event_type = 'gps_ping'
AND boat_id IN (
  SELECT b.id FROM boats b
  JOIN users u ON b.owner_id = u.id
  WHERE u.data_consent = true
)
GROUP BY 1, 2, 3
HAVING COUNT(DISTINCT boat_id) >= 5;        -- Minimum 5 boats per cell (anonymisation threshold)

CREATE VIEW b2b_engine_benchmarks AS
SELECT
  engine_make,
  engine_model,
  engine_year,
  DATE_TRUNC('month', recorded_at) AS month,
  AVG(engine_rpm) AS avg_rpm,
  AVG(engine_temp_f) AS avg_temp,
  AVG(fuel_level_pct) AS avg_fuel,
  COUNT(DISTINCT boat_id) AS sample_size
FROM public.telemetry_events te
JOIN public.boats b ON te.boat_id = b.id
JOIN public.users u ON b.owner_id = u.id
WHERE u.data_consent = true
AND engine_make IS NOT NULL
GROUP BY 1, 2, 3, 4
HAVING COUNT(DISTINCT boat_id) >= 5;
```

---

### `[BUILD THIS]` / Directory Pages

**`/directory`** — Hub with 4 category cards and global search. Each card shows live count from Supabase.

**`/directory/[category]`** — List view with:
- Sidebar filters: region, services, listing tier
- Map panel (Leaflet, right side) — markers for all visible listings
- List panel (left side) — ListingCard components
- "List your business" CTA at bottom

**`/directory/[slug]`** — Full listing page:
- Hero photo, business name, tier badge
- Contact info (T1+ only for Verified+)
- Services tags, map, description
- Reviews widget (T1+ can submit)
- "Request a Quote" button → saves to `lead_referrals`, sends email to business via Resend
- Analytics: fire `listing_analytics` INSERT on every view

**`/directory/manage`** (authenticated business owners):
- Preview of their listing
- Edit form
- Stats: views, quote requests, clicks (last 30 days from `listing_analytics`)
- Upgrade CTA with Stripe checkout links

---

### `[BUILD THIS]` / Forum Integration

The forum is **Flarum** deployed at `community.atmyboat.com` — separate from the Next.js app. The main site:

1. **Embeds recent forum threads** on the landing page Section 3 using Flarum's REST API (`GET /api/discussions?sort=-createdAt&page[limit]=3`)
2. **Links to** `community.atmyboat.com` from nav and dashboard
3. **SSO**: Use Flarum's built-in SSO plugin to sign in users automatically using their Supabase JWT

**Flarum Setup Instructions for Claude Code (in FLARUM_SETUP.md):**
```
1. Deploy Flarum on VPS ($5/mo DigitalOcean) or existing HostPapa
2. Database: MySQL (Flarum requirement — separate from Supabase PostgreSQL)
3. Domain: community.atmyboat.com → point to Flarum server
4. Required plugins (all free):
   - flarum/tags (category organisation)
   - flarum/mentions (@mentions)
   - flarum/likes (post likes)
   - flarum/markdown (markdown formatting)
   - fof/user-bio (user profiles)
   - fof/sso (Single Sign-On with atmyboat.com)
5. Initial categories (do not create more at launch):
   - d3kOS Help & Installation
   - Boats & Voyages
   - Buy/Sell (The Chandlery)
6. Seed with 15 threads before public launch (Skipper Don posts these manually)
```

---

### `[DEFER — Phase 2]` / Marketplace

**Route:** `/marketplace`

Build the page structure and empty state. Show "Coming Soon — The Chandlery launches [Month Year]" with email capture form (saves to Supabase `waitlist` table with `type = 'marketplace'`). Full implementation in Phase 2.

---

### `[DEFER — Phase 2]` / Skipper's Academy

**Route:** `/academy`

Build the page shell with empty course grid and "First courses launching [Month Year]". YouTube embed for course preview (use Skipper Don's d3kOS build video if available). Full implementation in Phase 2.

---

### `[DEFER — Phase 2]` / Sponsored Challenges

**Route:** `/challenges`

Build shell with empty state. Full implementation in Phase 2.

---

## PART 8 — MIDDLEWARE & AUTH

```typescript
// middleware.ts
import { createServerClient } from '@supabase/ssr'
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
  const response = NextResponse.next()
  
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    { cookies: { /* cookie handlers */ } }
  )
  
  const { data: { user } } = await supabase.auth.getUser()
  
  // Protect dashboard routes
  if (request.nextUrl.pathname.startsWith('/dashboard')) {
    if (!user) {
      return NextResponse.redirect(new URL('/login?redirect=/dashboard', request.url))
    }
    
    // Check T2+ for analytics
    if (request.nextUrl.pathname === '/dashboard/analytics') {
      const { data: profile } = await supabase
        .from('users').select('subscription_tier').eq('id', user.id).single()
      if (!profile || ['t0','t1'].includes(profile.subscription_tier)) {
        return NextResponse.redirect(new URL('/dashboard?upgrade=analytics', request.url))
      }
    }
    
    // Check T3 for fleet
    if (request.nextUrl.pathname === '/dashboard/fleet') {
      const { data: profile } = await supabase
        .from('users').select('subscription_tier').eq('id', user.id).single()
      if (!profile || profile.subscription_tier !== 't3') {
        return NextResponse.redirect(new URL('/dashboard?upgrade=fleet', request.url))
      }
    }
  }
  
  // Protect B2B portal (separate session check)
  if (request.nextUrl.pathname.startsWith('/b2b/dashboard') ||
      request.nextUrl.pathname.startsWith('/b2b/datasets') ||
      request.nextUrl.pathname.startsWith('/b2b/reports') ||
      request.nextUrl.pathname.startsWith('/b2b/api') ||
      request.nextUrl.pathname.startsWith('/b2b/account')) {
    const b2bSession = request.cookies.get('b2b_session')
    if (!b2bSession) {
      return NextResponse.redirect(new URL('/b2b', request.url))
    }
  }
  
  return response
}

export const config = {
  matcher: ['/dashboard/:path*', '/b2b/:path*']
}
```

---

## PART 9 — EMAIL TEMPLATES (Resend)

Create these email templates using React Email (free library):

1. **Welcome email** — sent on T1 registration. "Welcome aboard, [Name]" — links to dashboard, quick start, community.
2. **Device linked** — sent when n3-k1 is registered. Confirms device serial and tier.
3. **Alert notification** — sent when alarm fires. Shows alarm type, vessel name, timestamp, GPS link.
4. **T2 upgrade confirmation** — receipt with features unlocked.
5. **Feature request confirmation** — "Feature #[N] received — we'll update you when it moves forward."
6. **B2B welcome** — portal login credentials and onboarding steps.

---

## PART 10 — SEO CONFIGURATION

```typescript
// app/layout.tsx — base metadata
export const metadata: Metadata = {
  metadataBase: new URL('https://atmyboat.com'),
  title: { default: 'AtMyBoat — d3kOS Marine Intelligence', template: '%s | AtMyBoat' },
  description: 'The AI-first marine electronics system. ~$500 hardware. 100% offline or full cloud sync. For boats that deserve better.',
  openGraph: {
    type: 'website',
    siteName: 'AtMyBoat',
    images: [{ url: '/og-default.jpg', width: 1200, height: 630 }]
  },
  robots: { index: true, follow: true },
}
```

**Per-page SEO targets:**
| Route | Title | Primary Keyword |
|-------|-------|-----------------|
| `/` | `Marine AI Computer for Your Boat` | marine AI computer |
| `/d3kos` | `d3kOS Marine Operating System — Review & Features` | d3kOS |
| `/hardware` | `DIY Raspberry Pi Boat Computer — ~$500 Build Guide` | raspberry pi boat computer |
| `/download` | `Download d3kOS — Free Marine Linux Image` | d3kOS download |
| `/compatible` | `Is d3kOS Compatible With My Engine?` | engine compatibility checker |
| `/blog` | `Captain's Log — Marine Electronics & Boating` | marine electronics blog |

**Required files:**
- `/public/sitemap.xml` — auto-generated by `next-sitemap` package
- `/public/robots.txt` — allow all, disallow `/dashboard`, `/b2b`
- `/public/.well-known/security.txt` — security disclosure contact
- `/public/manifest.json` — PWA manifest for `/app` pre-launch

---

## PART 11 — PACKAGE.JSON DEPENDENCIES

```json
{
  "dependencies": {
    "next": "^15.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "typescript": "^5.0.0",
    "@supabase/supabase-js": "^2.0.0",
    "@supabase/ssr": "^0.5.0",
    "@anthropic-ai/sdk": "^0.30.0",
    "stripe": "^16.0.0",
    "@stripe/stripe-js": "^4.0.0",
    "resend": "^4.0.0",
    "react-email": "^3.0.0",
    "@react-email/components": "^0.0.22",
    "leaflet": "^1.9.0",
    "react-leaflet": "^4.0.0",
    "@types/leaflet": "^1.9.0",
    "html5-qrcode": "^2.3.0",
    "web-push": "^3.6.0",
    "twilio": "^5.0.0",
    "tailwindcss": "^3.4.0",
    "lucide-react": "^0.400.0",
    "clsx": "^2.0.0",
    "date-fns": "^3.0.0",
    "zod": "^3.22.0",
    "next-sitemap": "^4.0.0"
  }
}
```

---

## PART 12 — IMPLEMENTATION PHASES

### Phase 1 — Launch (Build This First) — ~15 developer days

**Days 1–3:**
- [ ] Next.js project scaffold with all folder structure
- [ ] Tailwind + design system (colours, fonts, components)
- [ ] Supabase project setup + run full schema SQL
- [ ] Environment variables configured
- [ ] Middleware auth protection

**Days 4–6:**
- [ ] Landing page (all 3 sections + hero)
- [ ] Nav + Footer components
- [ ] /d3kos product page
- [ ] /hardware BOM page
- [ ] /download page

**Days 7–9:**
- [ ] Supabase Auth + T1 registration flow (multi-step)
- [ ] Device registration API + QR scanner
- [ ] /subscribe tier comparison page
- [ ] Stripe checkout for T2 + T3
- [ ] Stripe webhook handler

**Days 10–12:**
- [ ] Dashboard shell (dark theme, sidebar, header)
- [ ] Boat card + GPS map (Leaflet)
- [ ] Engine gauges (Supabase realtime)
- [ ] Telemetry push API (`/api/telemetry/push`)
- [ ] OTA manifest API

**Days 13–15:**
- [ ] AI First Mate widget + `/api/first-mate` proxy
- [ ] /compatible checker + API
- [ ] /docs hub (quickstart, FAQ, hardware, CX5106, voice)
- [ ] Legal pages (privacy, terms, license, warranty, shipping)
- [ ] /contact page
- [ ] SEO metadata + sitemap
- [ ] Vercel + Cloudflare deployment

---

### Phase 2 — Community (Month 2–3)

- [ ] Flarum forum deployment at `community.atmyboat.com`
- [ ] Forum SSO integration
- [ ] /blog Captain's Log (MDX or Supabase-backed)
- [ ] Dashboard: voyage logs, alerts, marine vision gallery
- [ ] Alert system: webhook handler + Web Push + Resend
- [ ] Alert settings page
- [ ] Directory hub + 4 category pages
- [ ] Individual listing pages
- [ ] Business claim/manage flow
- [ ] /compatible checker enhancements
- [ ] Marketplace (Phase 2 full build)
- [ ] /story Skipper Don page
- [ ] /hall-of-fame

---

### Phase 3 — Revenue (Month 3–6)

- [ ] T2 feature gates: advanced analytics, Marine Vision video, Helm AI history
- [ ] B2B portal complete build (`/b2b/*`)
- [ ] B2B data API endpoints + anonymised views
- [ ] Skipper's Academy (YouTube-based, Phase 3 full build)
- [ ] Sponsored challenges system
- [ ] Affiliate link tracking
- [ ] /data-services AI qualification flow
- [ ] Directory: lead routing system, listing analytics dashboard
- [ ] T3 fleet management dashboard (`/dashboard/fleet`)
- [ ] SMS alerts via Twilio (T2+)

---

### Phase 4 — Scale (Month 6+)

- [ ] Native mobile app (React Native — shares types with web)
- [ ] PDF voyage report generation
- [ ] Fleet GPS map (T3)
- [ ] Predictive maintenance (AI fleet-wide analysis)
- [ ] Route optimisation AI
- [ ] Marina booking integration
- [ ] NOAA/Environment Canada weather overlay

---

## PART 13 — SECURITY CHECKLIST

Before going live, verify:

- [ ] `ANTHROPIC_API_KEY` never appears in client bundle (check with `next build` + `grep`)
- [ ] `SUPABASE_SERVICE_ROLE_KEY` never appears in client bundle
- [ ] All `/api/*` routes validate auth before accessing data
- [ ] Telemetry push validates `device_api_key` before inserting
- [ ] Stripe webhook validates `Stripe-Signature` header
- [ ] RLS enabled on all user-data tables
- [ ] Rate limiting on `/api/first-mate` (max 20 requests/minute per IP using Upstash Redis free tier OR simple in-memory Map)
- [ ] HTTPS enforced via Cloudflare (redirect all HTTP → HTTPS)
- [ ] HSTS header: `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- [ ] CSP header configured (allow Supabase, Stripe, Anthropic domains)
- [ ] `/public/.well-known/security.txt` deployed with `security@atmyboat.com`

---

## PART 14 — d3kOS SIDE CHANGES REQUIRED

These changes must be made to the d3kOS firmware (separate GitHub repo: `github.com/SkipperDon/d3kOS`). Document these as issues on that repo.

### Changes Needed Before Website Launch:

1. **QR Code URL update** — Change onboarding QR to encode:
   `https://atmyboat.com/register?device=[INSTALLATION_ID]&tier=t0&version=[FIRMWARE]`

2. **Registration handshake endpoint** — New on d3kOS (Port 8091):
   - `POST /api/link` — receives `{boat_uuid, device_api_key, supabase_url}` from website, writes to `/opt/d3kos/config/cloud-credentials.json`
   - `GET /api/status` — returns `{tier, firmware_version, uptime, last_push}`

3. **cloud-credentials.json** — New file (T1+ only, gitignored):
   ```json
   {
     "boat_uuid": "[UUID]",
     "device_api_key": "[key]",
     "supabase_url": "https://[project].supabase.co",
     "supabase_anon_key": "[anon-key]",
     "webhook_url": "https://atmyboat.com/api/notify",
     "tier": "t1"
   }
   ```

4. **Telemetry push Node-RED flow** — New flow `d3kOS-cloud-telemetry-push`:
   - POST to `https://atmyboat.com/api/telemetry/push` every 60s
   - Auth header: `Authorization: Bearer [device_api_key]`
   - SQLite offline buffer at `/opt/d3kos/data/telemetry-buffer.db`

5. **Alarm webhook** — New Node-RED flow:
   - POST to `https://atmyboat.com/api/notify` on WARNING/CRITICAL

6. **Force password change** — During onboarding wizard Step 1, force change from default `pi` password. This is a security requirement (EU CRA, NIST).

---

## PART 15 — COMPLETE ROUTE SUMMARY

All 45 routes at a glance:

```
PUBLIC (no auth)
/                   Landing — The Dock
/story              Skipper Don origin story
/d3kos              Product page
/hardware           BOM + shop
/download           Image download + flash instructions
/compatible         Engine compatibility checker
/subscribe          Tier plans + T1 registration
/app                Mobile app pre-launch + PWA
/blog               Captain's Log blog index
/blog/[slug]        Individual blog post
/features           Feature request portal
/data-services      B2B Intelligence marketing page
/directory          Directory hub
/directory/installers  Certified installer map
/directory/dealers  Marine dealer listings
/directory/marinas  Marina & boatyard map
/directory/service  Service & repair directory
/directory/[slug]   Individual business listing
/marketplace        Buy/Sell — The Chandlery [Phase 2]
/academy            Skipper's Academy course library [Phase 2]
/academy/[slug]     Individual course [Phase 2]
/challenges         Sponsored challenges [Phase 2]
/contact            Contact + AI routing
/privacy            Privacy Policy
/terms              Terms of Service
/warranty           Warranty & Returns
/shipping           Shipping Policy
/license            GPL v3 Open Source License
/hall-of-fame       Old Boat New Brain community stories
/docs               Documentation hub
/docs/quickstart    Quick start guide
/docs/hardware      Hardware assembly guide
/docs/cx5106        CX5106 DIP switch guide
/docs/voice         Voice command reference
/docs/faq           FAQ
/docs/changelog     Version history
/docs/api-reference Local API reference

AUTH
/login              Login
/register           T1 registration (+ ?device= QR deep-link)
/auth/callback      Supabase OAuth callback

DASHBOARD (T1+ auth required)
/dashboard          The Chart Room home
/dashboard/my-boat  Boat profile + registration
/dashboard/logs     Voyage logs + boat log
/dashboard/marine-vision  Photo/video gallery
/dashboard/helm-ai  Helm AI session history
/dashboard/chart    GPS world map
/dashboard/alerts   Alert settings + history
/dashboard/analytics  Journey analytics [T2+]
/dashboard/fleet    Fleet management [T3]
/dashboard/account  Account settings + Go Private toggle

B2B PORTAL (b2b_session auth)
/b2b                Login gate
/b2b/subscribe      Plan selection + DPA
/b2b/dashboard      Portal home
/b2b/datasets       Dataset browser + download
/b2b/reports        Pre-built reports
/b2b/api            API docs + key management [Harbor+]
/b2b/account        Subscription + team members + billing

API ROUTES (server-side)
POST /api/auth/register-device
POST /api/telemetry/push
POST /api/notify
POST /api/first-mate
POST /api/compatibility
POST /api/stripe/webhook
POST /api/stripe/create-checkout
GET  /api/d3kos/releases/latest.json
GET  /api/b2b/routes
GET  /api/b2b/engines
GET  /api/b2b/fuel
GET  /api/b2b/alarms
GET  /api/b2b/seasonal
POST /api/push/subscribe
```

---

## PART 16 — WHAT SUCCESS LOOKS LIKE

**Day 1 after launch:**
- atmyboat.com loads in <2 seconds on mobile
- Skipper Don can flash a d3kOS image, boot, and see his telemetry in the dashboard
- A new visitor can understand what d3kOS is, find the hardware BOM, download the image, and register a T1 account — all without talking to anyone
- The First Mate answers questions correctly and routes to the right pages

**Month 1:**
- 50+ T1 accounts registered
- 10+ n3-k1 devices sending live telemetry
- Forum seeded with 15 threads, 5+ community members posting

**Month 3:**
- First T2 subscriber ($9.99/month)
- First directory listing (certified installer)
- Forum has 100+ threads, people answering each other's questions

**Month 6:**
- 500+ registered boats
- First B2B inquiry via /data-services AI qualification flow
- 5+ directory listings generating lead referrals

---

*This document was prepared by Donald Moskaluk Consulting, March 2026.*
*Source documents: Foundation v2.1, Foundation v2.2 Amendment, d3kOS Integration Spec v2.1, Forum & Directory Monetization Strategy.*
*d3kOS GitHub: https://github.com/SkipperDon/d3kOS*
