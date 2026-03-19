# ATMYBOAT.COM — MASTER BUILD REFERENCE
**Version 2.0 · March 2026 · Donald Moskaluk Consulting**
**Classification: Authoritative build document — all decisions made, no ambiguity**

> **HOW TO USE THIS DOCUMENT**
> This is the single source of truth for atmyboat.com. All architectural decisions are final.
> Paste `ATMYBOAT_STANDING_INSTRUCTION.md` at the top of every Claude Code session before describing any task.
> Complete phases in strict order. Never open Claude Code until Phase 0 is done.
> Never push to live until Phase 4 checklist is complete.

---

## PART 1 — PLATFORM OVERVIEW

### What AtMyBoat.com Is

**atmyboat.com** is a live WordPress website on HostPapa. It serves four audiences:

1. **Boaters (45–70 years old)** — upgrading their boat electronics with d3kOS
2. **The open source / maker community** — interested in marine + embedded software
3. **Marine industry** — dealers, marinas, installers reaching verified boat owners
4. **Commercial fleet operators** — telemetry and analytics (future Phase 5)

### What Already Exists — DO NOT TOUCH

| What Exists | Status | Rule |
|---|---|---|
| atmyboat.com WordPress site | Live | No changes to homepage, existing pages, nav, or WP settings until staging push |
| Twenty Twenty theme | Active on live | Never modify directly — use child theme |
| d3kOS platform (separate system) | Documented in spec | Forum links to d3kOS page. Does not integrate technically. |
| MailPoet | Installed + active | Configure for forum emails in Phase 2A. Do not change existing email lists. |
| Yoast SEO | Installed + active | Configure for forum/products in Phase 2E. Do not change existing SEO settings. |
| Site Kit | Connected to Google Search Console | Already showing data. Submit new sitemap in Phase 2E only. |
| UpdraftPlus | Installed | Run full backup before every phase transition. Never skip. |
| WPReset | Installed | Use on staging only to reset and retry. NEVER run on live site. |

### What Is Being Added (This Build)

| Layer | URL | Technology | What It Does |
|---|---|---|---|
| 1 | atmyboat.com/forum | bbPress WordPress plugin | Community forum — threads, categories, member profiles |
| 2 | atmyboat.com/products | WordPress pages + template | Product hub — d3kOS is product #1; future products get new pages from template |
| 3 | Forum AI widget | PHP + cURL in child theme | AI assistant — searches forum threads for context, calls Claude Haiku, returns cited answer |
| 4 | atmyboat.com/blog | WordPress posts (existing) | SEO-optimised in Phase 2E — no rebuild needed |

### Future Phases (Do Not Build Now — Scaffold Only Where Noted)

The full d3kOS dashboard (T1–T3 tiers, Stripe, Supabase telemetry, Next.js app) is **future Phase 5+** and is documented separately. The current build is the WordPress foundation. Links from the forum and products hub point to the d3kOS platform pages as they exist today.

---

## PART 2 — STACK DECISIONS (ALL FINAL — DO NOT SUBSTITUTE)

| Decision | Choice | Why |
|---|---|---|
| **Forum engine** | bbPress (not Flarum) | bbPress is a WordPress plugin. Uses existing users, theme, database, and admin panel. Flarum requires a separate PHP app, its own database, and user system — two systems to maintain instead of one. |
| **Forum location** | Subfolder /forum (not subdomain) | Subdomains are treated as separate sites by Google and don't inherit atmyboat.com's domain authority. Subfolder keeps all SEO value on one domain. |
| **Hosting** | HostPapa Growth shared hosting | Already paid. cPanel, PHP/MySQL, staging, CDN, SSL all included. |
| **AI assistant** | PHP + cURL (not Node.js) | HostPapa shared hosting does not support Node.js persistent processes. PHP cURL calls the Anthropic API directly — simpler, works perfectly on shared hosting. |
| **AI model** | Claude Haiku only | Haiku costs roughly 15× less than Sonnet. At early forum volumes the entire AI assistant costs under $20/month. Quality is sufficient for forum Q&A. Upgrade path exists if needed. |
| **Email** | MailPoet + HostPapa email | Already installed. Uses existing skipperdon@atmyboat.com infrastructure. No third-party service needed. |
| **SEO** | Yoast SEO + Site Kit | Both already installed and configured. Zero additional setup. |
| **Analytics** | HostPapa built-in stats | No cookies, no third-party JavaScript, PIPEDA compliant. Google Analytics requires a consent banner — unnecessary complexity for a community forum. |
| **Backups** | UpdraftPlus | Already installed. Run before every staging-to-live push. |
| **Build environment** | HostPapa Staging | Identical PHP version, MySQL version, and server config as live. What works on staging works on live. |

---

## PART 3 — DESIGN SYSTEM

### Philosophy: Nostalgic Workshop × Modern AI

The visual identity is a dark-mode workshop aesthetic: warmly lit workbench darkness shot through with amber workshop-lamp warmth and teal circuit-board precision. It conveys expertise, craft, and the trust of someone who has been doing this for 40 years — not a Silicon Valley startup. It is fully AODA / WCAG 2.0 AA compliant.

### Colour Palette (CSS Custom Properties)

```css
:root {
  /* Backgrounds */
  --bg-deep:       #0A2342;   /* Navy deep — page backgrounds, headers */
  --bg-surface:    #0F2D50;   /* Workbench — card sections, sidebars */
  --bg-card:       #162B47;   /* Card surfaces */
  --bg-raised:     #1C3558;   /* Elevated elements, hover states */

  /* Brand Accents */
  --amber:         #B87800;   /* Primary CTA, headings, links — 7.0:1 on white ✓ AODA */
  --amber-bright:  #D4920F;   /* Hover state, amber on dark bg — 8.1:1 on #0A2342 ✓ */
  --amber-glow:    rgba(184,120,0,0.14);

  --teal:          #1A7A6E;   /* AI features, tags, secondary links — 4.6:1 on white ✓ */
  --teal-bright:   #22A090;   /* Teal on dark backgrounds — 6.2:1 on #0A2342 ✓ */
  --teal-glow:     rgba(26,122,110,0.12);

  /* Text */
  --text-primary:  #F0EAD8;   /* Warm cream — 14.8:1 on bg-deep ✓ AODA AAA */
  --text-secondary:#C8BEA8;   /* 8.4:1 on bg-deep ✓ */
  --text-muted:    #8A8070;   /* 4.5:1 on bg-deep ✓ AA large text */

  /* Borders */
  --border:        rgba(240,234,216,0.12);
  --border-amber:  rgba(184,120,0,0.25);
  --border-teal:   rgba(26,122,110,0.25);

  /* Status (for d3kOS integration, future) */
  --signal-green:  #00CC00;   /* Online / normal */
  --warning-amber: #FFA500;   /* Warning */
  --critical-red:  #FF0000;   /* Critical / alert */
  --offline-gray:  #666666;   /* Offline */
}
```

### Typography

```css
/* Google Fonts — load in child theme functions.php */
/* Playfair Display: 400, 700, 900 */
/* Source Serif 4: 300, 400, 600 (italic 400) */
/* JetBrains Mono: 400, 600 (monospace for labels, code, meta) */

--font-display: 'Playfair Display', Georgia, serif;   /* Display headings — editorial, nostalgic */
--font-body:    'Source Serif 4', Georgia, serif;      /* Body text, forum posts — readable, warm */
--font-mono:    'JetBrains Mono', 'Courier New', monospace; /* Labels, tags, code, thread meta */
```

### Typography Scale

| Element | Size | Font | Weight | Colour |
|---|---|---|---|---|
| Page H1 | clamp(2.2rem, 5vw, 3.8rem) | Playfair Display | 900 | --text-primary |
| Page H2 | clamp(1.6rem, 3vw, 2.4rem) | Playfair Display | 700 | --text-primary |
| Page H3 | 1.3rem | Playfair Display | 700 | --text-primary |
| Section label | 0.65rem / 0.2em tracking | JetBrains Mono | 600 | --amber-bright |
| Forum post body | **18px minimum** | Source Serif 4 | 400 | --text-primary |
| Forum post body line-height | **1.8** | — | — | — |
| Thread title | 1rem | Source Serif 4 | 600 | --text-primary |
| Thread meta | 0.65rem | JetBrains Mono | 400 | --text-muted |
| Navigation | 0.9rem | Source Serif 4 | 400 | --text-secondary |
| Code | 0.9rem | JetBrains Mono | 400 | --teal-bright |

**AODA Rule: 18px minimum for all body and forum post text. Never reduce below this.**

### Background Texture

```css
/* Subtle blueprint grid — applied to body::before */
background-image:
  linear-gradient(rgba(26,122,110,0.03) 1px, transparent 1px),
  linear-gradient(90deg, rgba(26,122,110,0.03) 1px, transparent 1px);
background-size: 40px 40px;
```

### UI Component Patterns (from design concept)

**Cards:**
```css
.card {
  background: var(--bg-card);
  border: 1px solid var(--border-amber);
  border-radius: 8px;
  padding: 1.5rem;
  transition: border-color 0.25s, transform 0.25s;
}
.card::before { /* top gradient bar — hidden until hover */
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, var(--amber-bright), var(--teal-bright));
  opacity: 0; transition: opacity 0.25s;
}
.card:hover { border-color: var(--border-amber); transform: translateY(-2px); }
.card:hover::before { opacity: 1; }
```

**Thread list item (bbPress styling):**
```css
.thread-item {
  display: grid;
  grid-template-columns: 44px 1fr auto;
  gap: 1.5rem;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid rgba(255,255,255,0.04);
  transition: background 0.2s;
  min-height: 72px; /* AODA touch target */
}
.thread-item:hover { background: var(--bg-raised); }
.thread-title { font-family: var(--font-body); font-size: 1rem; font-weight: 600; }
.thread-meta { font-family: var(--font-mono); font-size: 0.6rem; color: var(--text-muted); }
```

**Tags / labels:**
```css
.tag {
  display: inline-block;
  font-family: var(--font-mono); font-size: 0.6rem;
  letter-spacing: 0.1em; text-transform: uppercase;
  padding: 3px 8px; border-radius: 2px;
}
.tag-amber { background: var(--amber-glow); color: var(--amber-bright); border: 1px solid var(--border-amber); }
.tag-teal  { background: var(--teal-glow);  color: var(--teal-bright);  border: 1px solid var(--border-teal); }
```

**Primary button:**
```css
.btn-primary {
  background: var(--amber-bright); color: #0A2342;
  font-family: var(--font-body); font-weight: 700; font-size: 1rem;
  padding: 0.85rem 2rem; border-radius: 4px;
  min-height: 48px; min-width: 48px; /* AODA */
  transition: background 0.2s, transform 0.2s;
}
.btn-primary:hover { background: #E5A820; transform: translateY(-1px); }
```

**AI assistant widget — teal treatment:**
```css
.ai-widget {
  background: var(--bg-card);
  border: 1px solid var(--border-teal);
  border-radius: 8px;
  padding: 1.5rem;
  position: relative;
}
.ai-widget::before {
  content: 'AI ASSISTANT';
  position: absolute; top: -10px; left: 1.5rem;
  font-family: var(--font-mono); font-size: 0.55rem;
  letter-spacing: 0.15em; background: var(--teal-bright);
  color: #0A2342; padding: 2px 10px; border-radius: 2px; font-weight: 600;
}
```

### Navigation Pattern

**Desktop:** Sticky header, `backdrop-filter: blur(12px)`, logo left, nav links centre, CTA right. Active link gets amber bottom-border underline.

**Mobile (≤768px):** 4-item bottom navigation bar: Home / Forum / Search / Profile. Each item minimum 48×56px. This replaces the hamburger menu — research confirms 45–70 year old users prefer always-visible bottom tabs over hamburger menus.

**Skip-to-content link:** First focusable element on every page (AODA requirement). Visually hidden until focused.

### AODA / WCAG 2.0 AA Compliance Table

| Colour Pair | Use | Ratio | AA (4.5:1) | AAA (7:1) |
|---|---|---|---|---|
| #F0EAD8 on #0A2342 | Body text on page bg | 14.8:1 | ✓ PASS | ✓ PASS |
| #D4920F on #0A2342 | Amber headings on dark | 8.1:1 | ✓ PASS | ✓ PASS |
| #22A090 on #0A2342 | Teal links on dark | 6.2:1 | ✓ PASS | — |
| #C8BEA8 on #0A2342 | Secondary text on dark | 8.4:1 | ✓ PASS | ✓ PASS |
| #0A2342 on #B87800 | Dark text on amber button | 7.0:1 | ✓ PASS | ✓ PASS |
| #B87800 on #FFFFFF | Amber on white (light bg use) | 4.6:1 | ✓ PASS | — large text only |

**Additional AODA requirements:**
- Skip-to-content link at page top
- All images have descriptive alt text
- Form labels always visible (never placeholder-only)
- Focus indicators visible at 3:1+ contrast
- No flashing content >3Hz
- Keyboard-navigable throughout
- Minimum 18px body text, 1.8 line-height
- Minimum 48×48px touch targets on all interactive elements

---

## PART 4 — FILE & FOLDER STRUCTURE

All custom code lives in the Twenty Twenty child theme. Never edit the parent theme.

```
/wp-content/themes/twentytwenty-child/
├── style.css                  ← Child theme header + AtMyBoat CSS variables + Google Fonts
├── functions.php              ← Enqueues parent styles, loads child CSS, registers AJAX, loads inc/ files
├── inc/
│   ├── atmyboat-config.php    ← API keys via define() constants — NEVER commit to GitHub
│   ├── ai-assistant.php       ← PHP AI assistant — bbPress search + Anthropic API call
│   └── ai-widget.php          ← [atmyboat_ai] shortcode — renders the AI widget UI
├── bbpress.css                ← All bbPress forum styling — dark theme, AODA compliance
├── page-products.php          ← WordPress page template — renders product hub grid from products.json
├── page-product.php           ← WordPress page template — individual product page
├── data/
│   └── products.json          ← Product registry — drives product hub index grid
├── logs/
│   └── ai-YYYY-MM-DD.log      ← Daily AI usage logs — token counts + timestamps only (no query text)
└── header.php                 ← (optional) Override to add skip-to-content link and font preload

/wp-content/themes/twentytwenty-child/.gitignore
  inc/atmyboat-config.php      ← API key file must NEVER be committed
  logs/
```

**GitHub repo:** `github.com/SkipperDon/atmyboat-forum`
Review this repo before building anything. Check if a file already exists before creating it.

---

## PART 5 — API CONFIGURATION

Only one external service credential is required. Everything else uses existing WordPress plugins.

### atmyboat-config.php

```php
<?php
// AtMyBoat.com private config — NEVER commit to GitHub
// Path: /wp-content/themes/twentytwenty-child/inc/atmyboat-config.php

define( 'ANTHROPIC_API_KEY',    'sk-ant-[YOUR_KEY]' );
define( 'ANTHROPIC_MODEL',      'claude-haiku-4-5-20251001' );
define( 'ANTHROPIC_MAX_TOKENS', 1000 );
```

**Hard billing cap:** Set $30/month limit in Anthropic Console billing settings immediately after creating the account. The API returns an error when the cap is hit — the forum keeps working and the AI widget shows "temporarily unavailable." You will never receive a surprise bill.

---

## PART 6 — FORUM STRUCTURE (bbPress)

### Seven Categories (create in this order)

| # | Category Name | Purpose |
|---|---|---|
| 1 | d3kOS Support | Installation help, firmware questions, troubleshooting |
| 2 | Marine Electronics | General electronics, NMEA, AIS, chartplotters |
| 3 | Engine & Mechanical | Engine diagnostics, CX5106, mechanical issues |
| 4 | Electrical & Wiring | Marine wiring, batteries, inverters, solar |
| 5 | Navigation & Charts | GPS, charts, routing, weather |
| 6 | General Seamanship | General boating, maintenance, stories |
| 7 | AI-Assisted Fixes | Members sharing successful AI-assisted repair solutions |

### Registration
Open self-registration: WP Admin → Settings → General → Membership → tick "Anyone can register."

### Seed Threads (Claude Code drafts — Donald posts manually before launch)
10 starter threads across d3kOS Support, Engine & Mechanical, and AI-Assisted Fixes. Titles should be specific, SEO-friendly questions (e.g., "How do I configure CX5106 DIP switches for a Mercruiser 4.3?"). Real d3kOS knowledge, proper forum post format.

---

## PART 7 — AI ASSISTANT ARCHITECTURE

### How It Works

```
Member types question → jQuery AJAX POST to WordPress endpoint
→ WordPress action handler (functions.php) calls ai-assistant.php
→ ai-assistant.php: PHP WP_Query searches bbPress posts for keyword matches (top 5)
→ Builds context: 5 excerpts + source thread URLs
→ PHP cURL POST to api.anthropic.com/v1/messages (Haiku model)
→ System prompt + forum context + user question → Claude Haiku
→ Response returned as JSON with answer + cited thread URLs
→ AI widget renders answer with clickable source links
```

### ai-assistant.php — Core Logic

```php
<?php
require_once get_template_directory() . '/inc/atmyboat-config.php';

function atmyboat_get_forum_context( $question ) {
    // Search bbPress posts for relevant content
    $search_args = [
        'post_type'      => [ 'topic', 'reply' ],
        'posts_per_page' => 5,
        's'              => sanitize_text_field( $question ),
        'post_status'    => 'publish',
    ];
    $results = new WP_Query( $search_args );
    $context = [];

    if ( $results->have_posts() ) {
        while ( $results->have_posts() ) {
            $results->the_post();
            $context[] = [
                'title'   => get_the_title(),
                'excerpt' => wp_trim_words( get_the_content(), 60 ),
                'url'     => get_permalink(),
            ];
        }
        wp_reset_postdata();
    }
    return $context;
}

function atmyboat_ai_answer( $question ) {
    // Input validation
    if ( strlen( $question ) > 500 ) {
        return [ 'answer' => 'Please keep your question under 500 characters so I can give you a focused answer.', 'sources' => [] ];
    }

    $context = atmyboat_get_forum_context( $question );
    $context_text = '';
    $sources = [];

    foreach ( $context as $item ) {
        $context_text .= "Thread: {$item['title']}\nExcerpt: {$item['excerpt']}\nURL: {$item['url']}\n\n";
        $sources[] = [ 'title' => $item['title'], 'url' => $item['url'] ];
    }

    $system_prompt = "You are the AtMyBoat AI Assistant — a knowledgeable marine mechanic and d3kOS expert helping community members at atmyboat.com.

You have access to relevant forum threads from the AtMyBoat Community Forum. Always cite specific thread URLs in your answer.

RULES:
- Answer like an experienced marine mechanic — practical, plain English, no jargon without explanation
- Always cite 1–3 relevant forum thread URLs from the context provided
- End every answer with: 'Verify this with the community — post a follow-up in the forum if something doesn't match your setup.'
- If the forum context doesn't contain a relevant answer, say so and suggest posting a new thread
- Never give advice that could endanger life or vessel safety without strong caveats
- Keep answers concise — 3–5 sentences plus source links
- NEVER store, log, or reference the user's question text";

    $payload = json_encode([
        'model'      => ANTHROPIC_MODEL,
        'max_tokens' => ANTHROPIC_MAX_TOKENS,
        'system'     => $system_prompt,
        'messages'   => [
            [ 'role' => 'user', 'content' => "Forum context:\n{$context_text}\n\nMember question: {$question}" ]
        ],
    ]);

    $ch = curl_init( 'https://api.anthropic.com/v1/messages' );
    curl_setopt_array( $ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST           => true,
        CURLOPT_POSTFIELDS     => $payload,
        CURLOPT_HTTPHEADER     => [
            'Content-Type: application/json',
            'x-api-key: ' . ANTHROPIC_API_KEY,
            'anthropic-version: 2023-06-01',
        ],
        CURLOPT_TIMEOUT => 20,
    ]);

    $response = curl_exec( $ch );
    $http_code = curl_getinfo( $ch, CURLINFO_HTTP_CODE );
    curl_close( $ch );

    // Log token counts only — NEVER log query text
    $data = json_decode( $response, true );
    if ( $http_code === 200 && isset( $data['content'][0]['text'] ) ) {
        $tokens_in  = $data['usage']['input_tokens']  ?? 0;
        $tokens_out = $data['usage']['output_tokens'] ?? 0;
        $log_file = get_template_directory() . '/logs/ai-' . date('Y-m-d') . '.log';
        file_put_contents( $log_file, date('H:i:s') . " in={$tokens_in} out={$tokens_out}\n", FILE_APPEND );
        return [ 'answer' => $data['content'][0]['text'], 'sources' => $sources ];
    }

    return [ 'answer' => 'The AI assistant is temporarily unavailable. Please post your question in the forum and a community member will help.', 'sources' => [] ];
}
```

### AJAX Handler in functions.php

```php
// Register AJAX handler for AI assistant
add_action( 'wp_ajax_atmyboat_ai_query',        'atmyboat_handle_ai_query' );
add_action( 'wp_ajax_nopriv_atmyboat_ai_query', 'atmyboat_handle_ai_query' );

function atmyboat_handle_ai_query() {
    check_ajax_referer( 'atmyboat_ai_nonce', 'nonce' );
    $question = isset( $_POST['question'] ) ? sanitize_text_field( wp_unslash( $_POST['question'] ) ) : '';
    if ( empty( $question ) ) {
        wp_send_json_error( [ 'message' => 'Please enter a question.' ] );
    }
    require_once get_template_directory() . '/inc/ai-assistant.php';
    $result = atmyboat_ai_answer( $question );
    wp_send_json_success( $result );
}
```

### ai-widget.php Shortcode

The `[atmyboat_ai]` shortcode renders the AI widget. It can be placed on the forum index page, in a sidebar widget, or on any page via the block editor.

**Widget UI requirements:**
- Navy/teal styling with "AI ASSISTANT" label (teal pill, top-left of widget border)
- Question input: placeholder "Ask a marine question…", max 500 characters
- Submit button: amber, minimum 48px height
- Answer area: hidden until response arrives, shows answer text + source links
- Disclaimer below answer: "AI responses are based on community forum threads. Always verify advice before working on your vessel."
- Loading state: spinner while waiting for API response
- Error state: graceful "temporarily unavailable" message

---

## PART 8 — PRODUCT HUB

### products.json Structure

```json
{
  "products": [
    {
      "name": "d3kOS",
      "slug": "d3kos",
      "tagline": "The open-source marine operating system for the d3-k1 hardware",
      "category": "Marine Operating System",
      "status": "available",
      "price_from": "Free to download",
      "github_url": "https://github.com/SkipperDon/d3kOS",
      "forum_category": "d3kos-support",
      "forum_url": "/forum/forum/d3kos-support/",
      "description": "d3kOS is a full marine intelligence platform built on Raspberry Pi 4B. Runs offline completely (T0) or connects to the cloud for dashboard access, telemetry, and AI features (T1+).",
      "features": [
        "NMEA 2000 engine monitoring",
        "GPS tracking and route logging",
        "Voice commands",
        "Marine Vision camera system",
        "AI-assisted engine diagnostics",
        "Offline-first — no internet required"
      ],
      "specs": {
        "Hardware": "Raspberry Pi 4B 8GB",
        "Display": "10.1\" 1000-nit sunlight-readable touchscreen",
        "Connectivity": "NMEA 2000 via PiCAN-M HAT",
        "Engine interface": "CX5106 NMEA2000 gateway",
        "Build approach": "DIY · parts list in documentation",
        "Current version": "v0.9.2 (March 2026)"
      },
      "cta_primary": { "text": "Download d3kOS", "url": "/download" },
      "cta_secondary": { "text": "Get Community Support", "url": "/forum/forum/d3kos-support/" }
    }
  ]
}
```

### page-products.php

Reads `products.json`, renders a grid of product cards. Each card: product name, tagline, category tag, status badge, "Learn More" CTA. Uses the design system card pattern.

### page-product.php

Individual product page template. Sections: hero (product name + tagline + primary CTA), features (icon list), specs (table), GitHub link (teal), forum support link (amber CTA: "Get support in the d3kOS Forum →").

---

## PART 9 — URL STRUCTURE

All new URLs are subfolders of atmyboat.com. **No subdomains.** This keeps all SEO authority on one domain.

| URL | Status | What Loads |
|---|---|---|
| atmyboat.com | Existing | Main homepage — do not modify |
| atmyboat.com/forum | **New — Phase 2A** | bbPress forum home — all categories, recent threads |
| atmyboat.com/forum/forum/d3kos-support/ | bbPress auto | d3kOS Support category |
| atmyboat.com/forum/topic/[thread-slug]/ | bbPress auto | Individual thread |
| atmyboat.com/forum/register/ | bbPress auto | New member registration |
| atmyboat.com/products | **New — Phase 2D** | Product hub index — grid of all products |
| atmyboat.com/products/d3kos | **New — Phase 2D** | d3kOS product page |
| atmyboat.com/products/[product-slug] | **New — Phase 2D** | Future product pages |
| atmyboat.com/blog | Existing WP | WordPress blog — SEO optimised Phase 2E |
| atmyboat.com/privacy | Existing or new | Privacy policy — required for AODA and PIPEDA |
| atmyboat.com/accessibility | **New — Phase 3** | Accessibility statement — required for AODA |
| atmyboat.com/sitemap_index.xml | Yoast auto | XML sitemap — all pages, forum, products, posts |

---

## PART 10 — PHASE BUILD PLAN

### Phase 0 — Activate Staging & Verify Safety Net
*Do this before anything else. Takes 30 minutes. Protects the live site.*

- [ ] Run UpdraftPlus full backup right now — before anything else
- [ ] Confirm backup completed and files are downloadable (test download one file)
- [ ] Store a copy of the backup off-server (Google Drive, Dropbox, or USB)
- [ ] Activate HostPapa Staging from cPanel → Staging → Create Staging Site
- [ ] Confirm staging URL loads and looks identical to live
- [ ] Confirm staging has its own separate database (cPanel → MySQL Databases)
- [ ] Bookmark staging URL labelled "AtMyBoat STAGING"
- [ ] Register Anthropic Console account at console.anthropic.com
- [ ] Set $30/month billing hard cap in Anthropic Console billing settings immediately
- [ ] Generate API key and have it ready for Phase 1

**✓ PHASE 0 COMPLETE — Backup verified. Staging live. Anthropic key in hand. Safe to proceed.**

---

### Phase 1 — Staging Preparation (Manual — before Claude Code)
*You do this manually on staging before Claude Code opens.*

- [ ] On staging: create Twenty Twenty Child Theme folder at `/wp-content/themes/twentytwenty-child/`
- [ ] Create `style.css` with child theme header (Template: twentytwenty)
- [ ] Create `functions.php` that enqueues parent theme styles
- [ ] Create `inc/` folder inside child theme
- [ ] Create `atmyboat-config.php` in `inc/` with Anthropic API key
- [ ] Add `inc/atmyboat-config.php` to `.gitignore` before first commit
- [ ] Create `logs/` folder inside child theme (gitignored)
- [ ] Activate child theme on staging (WP Admin → Appearance → Themes)
- [ ] Verify staging site still looks correct with child theme active
- [ ] Create GitHub repo `atmyboat-forum` and push child theme files (excluding config)

**✓ PHASE 1 COMPLETE — Child theme active on staging. Config file in place. GitHub repo created.**

---

### Phase 2A — bbPress Forum & MailPoet Configuration
*All work on staging only. Never touch the live site.*

- [ ] Install bbPress plugin on staging (WP Admin → Plugins → Add New → bbPress)
- [ ] Create 7 forum categories in the order listed in Part 6
- [ ] Set forum registration: open self-registration (WP Admin → Settings → General → Anyone can register)
- [ ] Configure MailPoet to send bbPress notification emails through MailPoet SMTP
- [ ] Create forum index page at `/forum` — assign bbPress forum index template
- [ ] Draft 10 seed threads (Claude Code task), post manually in WP Admin before launch
- [ ] Verify 7 forums visible at `/forum` on staging, 10 threads present across categories

**✓ 2A COMPLETE — Forum live on staging with 10 seed threads. Email notifications working.**

---

### Phase 2B — AODA Design (Twenty Twenty Child Theme)
*Design system: Navy/Amber/Teal. Fonts: Playfair Display + Source Serif 4. All WCAG 2.0 AA.*

- [ ] Add CSS variables and Google Fonts (Playfair Display, Source Serif 4, JetBrains Mono) to `style.css`
- [ ] Add blueprint grid background texture to `body::before`
- [ ] Create `bbpress.css` — style forum thread list, post layout, member avatars, category cards
- [ ] Thread list: dark card style, amber/teal tags, 18px Source Serif 4 body text
- [ ] Minimum 48×48px touch targets for all buttons, links, and nav items
- [ ] Skip-to-content link as first focusable element on every page (`header.php` override)
- [ ] Sticky header: backdrop blur, logo left, nav links, amber CTA right
- [ ] Mobile: 4-item bottom navigation (Home / Forum / Search / Profile), min 48×56px per item
- [ ] Forum readable at 320px width — no horizontal scroll
- [ ] Forum header shows AtMyBoat logo and nav link back to main site
- [ ] Verify all colour pairs pass WCAG 2.0 AA 4.5:1 minimum (see Part 3 contrast table)
- [ ] Forum matches design system in Part 3 (dark navy backgrounds, amber headings, teal AI elements)

**✓ 2B COMPLETE — Forum styled. AODA colour pairs verified. Mobile confirmed.**

---

### Phase 2C — PHP AI Assistant

- [ ] Create `/inc/ai-assistant.php` — loads config constants, implements bbPress context search, implements cURL API call (see Part 7 for full code)
- [ ] System prompt: experienced marine mechanic, cites forum threads by URL, plain English, "verify with the community" note (see Part 7)
- [ ] Cost guard: reject questions over 500 characters, enforce 1000 token output cap, log daily token totals to `/logs/ai-YYYY-MM-DD.log` (no query text logged)
- [ ] Create AJAX endpoint in `functions.php` — `wp_ajax` action calls `ai-assistant.php`, returns JSON
- [ ] Create `ai-widget.php` shortcode `[atmyboat_ai]` — navy/teal styling, question input, answer display with source links, disclaimer (see Part 7)
- [ ] Add `[atmyboat_ai]` to forum index page and sidebar via WP Admin
- [ ] Test: ask a d3kOS question — confirm response arrives with cited thread URLs
- [ ] Test: ask a >500 character question — confirm it is rejected gracefully
- [ ] Verify log file is created and updated (token counts only)

**✓ 2C COMPLETE — AI assistant answering questions on staging with forum citations.**

---

### Phase 2D — Product Hub

- [ ] Create `data/products.json` in child theme — d3kOS entry with all fields (see Part 8)
- [ ] Create `page-products.php` template — reads `products.json`, renders product grid
- [ ] Create `page-product.php` template — hero, features, specs, GitHub link, forum support CTA
- [ ] Create d3kOS product page in WP Admin using `page-product.php` template — slug: `/products/d3kos`
- [ ] Verify d3kOS product page includes "Get support in the Forum →" link to d3kOS Support category
- [ ] Add Products link to main WordPress navigation menu on staging
- [ ] Yoast SEO: set meta title and description on `/products` and `/products/d3kos`

**✓ 2D COMPLETE — Product hub live on staging. d3kOS page complete. Nav updated.**

---

### Phase 2E — SEO Configuration

- [ ] Yoast: enable XML sitemap — confirm it includes `/forum`, `/products`, and all blog posts
- [ ] Yoast: set forum pages to be indexed — bbPress archives and threads in sitemap XML
- [ ] Yoast: set meta title format for forum threads: "Thread Title | AtMyBoat Community"
- [ ] Yoast: configure Open Graph for product pages (image, description, site name)
- [ ] Register Bing Webmaster Tools at bing.com/webmasters — verify atmyboat.com
- [ ] Add Bing verification meta tag via Yoast → General → Webmaster Tools
- [ ] Submit sitemap to Bing Webmaster Tools: `atmyboat.com/sitemap_index.xml`
- [ ] Submit updated sitemap to Google Search Console via Site Kit
- [ ] Create privacy policy page at `/privacy` if not already present
- [ ] Create accessibility statement at `/accessibility` (required for AODA)
- [ ] Add internal cross-links: homepage → products → forum → blog

**✓ 2E COMPLETE — SEO configured. Bing verified. Sitemap submitted to Google and Bing.**

---

### Phase 2F — Mobile App Backend (HostPapa PHP + MySQL)

*Builds the server-side infrastructure required by the d3kOS mobile PWA. All code is PHP + MySQL on existing HostPapa Growth hosting — no new servers, no new cost.*

**New MySQL tables (create via phpMyAdmin SQL import):**

```sql
-- Device registry
CREATE TABLE d3kos_devices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_uuid VARCHAR(64) NOT NULL UNIQUE,
    account_id INT NOT NULL,
    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- QR pairings
CREATE TABLE d3kos_pairings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_uuid VARCHAR(64) NOT NULL,
    pi_installation_id VARCHAR(64) NOT NULL,
    account_id INT NOT NULL,
    paired_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Command queue
CREATE TABLE d3kos_command_queue (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pi_installation_id VARCHAR(64) NOT NULL,
    command VARCHAR(64) NOT NULL,
    payload JSON,
    status ENUM('pending','picked_up','completed','failed') DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    picked_up_at DATETIME NULL,
    completed_at DATETIME NULL,
    result JSON NULL
);

-- Pi exports (all 8 data categories)
CREATE TABLE d3kos_pi_exports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pi_installation_id VARCHAR(64) NOT NULL,
    export_type VARCHAR(32) NOT NULL,
    data_json JSON NOT NULL,
    exported_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Fix My Pi reports
CREATE TABLE d3kos_fix_my_pi_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pi_installation_id VARCHAR(64) NOT NULL,
    triggered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    issues_found INT DEFAULT 0,
    issues_resolved INT DEFAULT 0,
    report_json JSON,
    tier VARCHAR(4) NOT NULL
);

-- PDF reports
CREATE TABLE d3kos_pdf_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pi_installation_id VARCHAR(64) NOT NULL,
    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    report_path VARCHAR(255),
    tier VARCHAR(4) NOT NULL
);

-- Version registry
CREATE TABLE d3kos_version_registry (
    id INT AUTO_INCREMENT PRIMARY KEY,
    version VARCHAR(20) NOT NULL,
    release_notes TEXT,
    min_app_version VARCHAR(20),
    released_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**New PHP endpoints (all under `/mobile/` subfolder, require API key header):**

| Endpoint | Method | What It Does |
|----------|--------|--------------|
| `register-device.php` | POST | Stores device UUID + links to account |
| `pair-device.php` | POST | Links device UUID + Pi installation ID to account |
| `command-queue.php` | POST/GET | App writes command; Pi polls for pending; Pi writes result |
| `data-ingress.php` | POST | Receives Pi exports (all 8 data categories), stores in DB |
| `tier-features.php` | GET | Returns feature flags for this account/tier |
| `fix-my-pi-billing.php` | POST | Stripe $29.99 charge for T0/T1 per incident |
| `pdf-report.php` | POST/GET | T2/T3 only: triggers mPDF generation + AI recommendations |
| `version-registry.php` | GET | Returns current d3kOS version, release notes, min app version |

**Phase 2F build checklist:**

- [ ] Create 7 MySQL tables via phpMyAdmin SQL import
- [ ] Build `mobile/register-device.php` — store device UUID, link to account
- [ ] Build `mobile/pair-device.php` — link device UUID + Pi installation ID + account, return confirmation
- [ ] Build `mobile/command-queue.php` — write (app), poll (Pi every 30s), result write (Pi), read (app)
- [ ] Build `mobile/data-ingress.php` — receive all 8 export categories from Pi, store in DB
- [ ] Build `mobile/tier-features.php` — return JSON feature flags per tier (T0/T1/T2/T3)
- [ ] Build Stripe $29.99 Fix My Pi payment page — T0/T1 only; Stripe webhook updates DB on success
- [ ] Upload mPDF library to HostPapa via FTPS (no Composer — upload pre-packaged ZIP)
- [ ] Build `mobile/pdf-report.php` — generate PDF via mPDF, call Gemini 2.5 Flash (MAX_TOKENS 1000), store file, return download URL — T2/T3 only
- [ ] Build `mobile/version-registry.php` — seed with current d3kOS version on launch
- [ ] Add API key authentication to all `/mobile/` endpoints (Pi uses installation ID + shared secret)
- [ ] Add all `/mobile/` endpoints to security checklist (Part 12)
- [ ] Test: command queue end-to-end — app writes → Pi polls → Pi responds → app reads result
- [ ] Test: Stripe Fix My Pi — app opens payment page → payment completes → tier status updated
- [ ] Test: PDF report generation — trigger from app → mPDF generates → Gemini recommendations included → download URL returned
- [ ] Verify PDF reports blocked for T0/T1 — return 403 with clear message

**✓ 2F COMPLETE — Mobile app backend live on staging. Command queue, pairing, exports, Stripe Fix My Pi, PDF reports all verified.**

---

### Phase 3 — AODA Compliance Audit (Run on Staging Before Migration)
*Non-negotiable for Ontario. Run every test before Phase 4.*

- [ ] All body text minimum 4.5:1 contrast ratio — test every text/background combination
- [ ] Navy #0A2342 on white — must pass 4.5:1
- [ ] Amber #B87800 on white — must pass 4.5:1 for large text
- [ ] Minimum 18px font for all forum body text — verify in Chrome DevTools
- [ ] All buttons and links minimum 48×48px touch target — DevTools mobile emulation
- [ ] All images have descriptive alt text — WAVE scan at wave.webaim.org
- [ ] All form inputs have visible labels (not placeholder-only) — WAVE scan + manual
- [ ] Tab key navigates every interactive element in logical order — unplug mouse and test
- [ ] Focus ring visible on every focused element at 3:1+ contrast — manual + DevTools
- [ ] Skip-to-content link is first Tab stop on every page
- [ ] Screen reader can navigate forum thread list (VoiceOver / NVDA test)
- [ ] AI assistant responses include clickable source thread URLs
- [ ] No content flashes more than 3 times per second
- [ ] `lang="en"` attribute on all HTML pages
- [ ] Privacy policy at `/privacy` is live and linked in footer
- [ ] Accessibility statement at `/accessibility` is live

**✓ PHASE 3 COMPLETE — All AODA checks passed on staging. Cleared for migration.**

---

### Phase 4 — Migration: Staging to Live
*Backup first. Push second. Verify third. Rollback plan ready.*

> **STOP. This is where things went wrong before.** The steps below are sequenced specifically to protect the live site.

- [ ] Run UpdraftPlus full backup on the **live site** right now — all options, verify completed
- [ ] Download backup off-server to Google Drive or local hard drive — confirm files are not 0KB
- [ ] Write down the backup timestamp — "Live backup taken: [date and time]"
- [ ] In HostPapa cPanel: Staging → Push to Live
- [ ] Wait for HostPapa confirmation — do not close browser
- [ ] Immediately visit atmyboat.com — confirm homepage loads correctly
- [ ] Visit atmyboat.com/forum — confirm forum loads with all categories and threads
- [ ] Visit atmyboat.com/products — confirm product hub loads, d3kOS page renders
- [ ] Submit a test forum post — confirm it saves and notification email arrives
- [ ] Test AI assistant on live site — ask a question, confirm response with thread citations
- [ ] Visit atmyboat.com/sitemap_index.xml — confirm sitemap includes forum and products
- [ ] Google Search Console → Sitemaps → Resubmit
- [ ] Bing Webmaster → Sitemaps → Resubmit

**✓ PHASE 4 COMPLETE — Forum and Product Hub live. SEO resubmitted. Site verified.**

---

### Phase 5 — Future: Platform Expansion (post-v0.9.4 launch)
*Do not start until Phase 4 is live and v0.9.4 mobile app is shipping.*

**Note: Next.js, Supabase, and any separate server infrastructure are NOT in scope.**
All expansion uses HostPapa PHP + MySQL — the existing platform. $0 new infrastructure.
Device registration, QR pairing, command queue, and Stripe payments are Phase 2F (already built).

This future phase adds:
- T3 fleet management (multiple Pis on one account)
- B2B intelligence portal (marine dealers, marinas, installers)
- Marine Vision gallery (shared camera clips and highlights)
- Advanced AI session history (Helm AI conversation logs, if decided)
- Annual billing option via Stripe (T2/T3 — currently monthly only)
- Community features TBD (only if they do not duplicate ActiveCaptain)

---

## PART 11 — COST SUMMARY

| Item | Monthly | Notes |
|---|---|---|
| HostPapa Growth hosting | Existing plan | Forum, products, blog, email, CDN, SSL — entire platform |
| Domain (atmyboat.com) | Already owned | Annual renewal |
| Anthropic Claude API (Haiku) | Usage-based | Hard cap set in Console — forum always stays live |
| MailPoet | $0 | Free plan — 1,000 subscribers, unlimited emails |
| Yoast SEO | $0 | Free version covers all requirements |
| bbPress | $0 | Free WordPress plugin |
| Google Search Console | $0 | Free — Site Kit already connected |
| UpdraftPlus | $0 | Free plan — manual and scheduled backups |
| SSL | $0 | Included in HostPapa Growth |
| CDN | $0 | Included in HostPapa Growth |
| **TOTAL** | **Low fixed overhead** | **Entire platform including AI assistant** |

### AI Cost Guards
- **Haiku model only.** `ANTHROPIC_MODEL = claude-haiku-4-5-20251001`. Never change to Sonnet in production.
- **1000 token output cap.** `ANTHROPIC_MAX_TOKENS = 1000` in every API call.
- **500 character input limit.** `ai-assistant.php` rejects longer questions with a helpful message.
- **Stateless queries.** No conversation history. Each question is independent. Cost stays flat per query.
- **Daily log.** `/logs/ai-YYYY-MM-DD.log` — review weekly. Token counts and timestamps only. No query text stored.
- **Hard cap in Console.** $30/month cap set in Anthropic billing. If hit, forum keeps working. AI widget shows "temporarily unavailable."

---

## PART 12 — SECURITY CHECKLIST (before Phase 4 migration)

- [ ] `inc/atmyboat-config.php` in `.gitignore` — confirm API key is never in GitHub
- [ ] Confirm no API keys hardcoded in any PHP file other than `atmyboat-config.php`
- [ ] AJAX endpoints use `check_ajax_referer()` nonce validation
- [ ] All user input sanitized with `sanitize_text_field()` before use
- [ ] AI query text never stored in database, logs, or transients
- [ ] `logs/` folder not accessible via browser (add `Options -Indexes` to `.htaccess`)
- [ ] UpdraftPlus backup verified working (Phase 0)
- [ ] SSL certificate active on live site (HostPapa Growth includes this)
- [ ] HTTPS enforced — check cPanel → Force HTTPS redirect is enabled

---

## PART 13 — NAMING CONVENTIONS

| Term | Use This | Never Use |
|---|---|---|
| Main platform | AtMyBoat.com | atmyboat, Atmyboat, AtMyBoat |
| Operating system | d3kOS | D3KOS, d3kos (except code/filenames) |
| Hardware kit | d3-k1 | Jellyfish, d3k1 (except code) |
| Forum | the AtMyBoat Community Forum | message board, bulletin board, community |
| Forum members | members | users, customers, clients |
| AI feature | AI Assistant | chatbot, bot, GPT, robot, the AI |
| Product section | Products | store, shop (unless selling direct) |
| Creator — public | Skipper Don | Donald Moskaluk (public-facing) |
| Creator — legal | Donald Moskaluk | Skipper Don (legal and financial documents) |
| Contact email | skipperdon@atmyboat.com | any other address for platform matters |
| GitHub — existing | github.com/SkipperDon/d3kOS | any other capitalisation |
| GitHub — forum | github.com/SkipperDon/atmyboat-forum | any other capitalisation |

---

## PART 14 — VERSION TRACKING

*Update this table after every Claude Code session. If you skip updating it, the next session starts with stale context.*

| Version | Type | Date | Phase | What Changed |
|---|---|---|---|---|
| 2.0 | Planning | March 2026 | Pre-build | Master reference v2.0 created. Stack confirmed: WordPress + bbPress + PHP AI + Twenty Twenty child theme + HostPapa staging. Design system: dark navy + amber + teal from TinkerHub concept adapted to AtMyBoat brand. |
| [NEXT] | — | — | — | Add row here after every session. What was built. What was tested. What comes next. |

---

*AtMyBoat.com Master Build Reference v2.0 · Donald Moskaluk · skipperdon@atmyboat.com*
*Source documents: Forum Master Reference v1.0, ATMYBOAT_CLAUDE_CODE_SPEC.md v1.0, TinkerHub Design Concept*

---

## PART 15 — DEPLOYMENT STRATEGY: NO-SSH HOSTPAPA BUILD PIPELINE

### The Reality

HostPapa shared hosting has **no SSH access** — this is a firm policy, not a plan limitation. This means:

- No `wp-cli` from command line
- No `git pull` from terminal
- No `rsync` over SSH
- No remote `composer` or `npm`

Claude Code runs **entirely on your local machine**. The server is treated as a dumb file target. All logic, all code generation, all testing happens locally. Files are delivered to HostPapa by one of three mechanisms described below.

---

### Three Delivery Mechanisms

#### Mechanism 1 — FTPS (Primary for Claude Code)

HostPapa supports FTP and FTPS. Claude Code uses `lftp` (a command-line FTP client) to sync the child theme folder and plugin folder from the local repo to the server.

**Why this is the right tool:**
- `lftp mirror --reverse` is a one-command differential sync — it only uploads changed files
- Supports FTPS (encrypted) unlike plain FTP
- Runs headlessly inside Claude Code without any browser interaction
- Claude Code can generate the `lftp` commands itself and run them

**Credentials needed (collect in Phase 0):**
- FTP hostname (usually `ftp.atmyboat.com` or the server IP)
- FTP username (your cPanel username)
- FTP password
- Remote base path: `/public_html/wp-content/`

**Example lftp sync command Claude Code will use:**
```bash
lftp -e "
  set ftp:ssl-force true;
  set ssl:verify-certificate false;
  open -u YOUR_FTP_USER,YOUR_FTP_PASS ftp.atmyboat.com;
  mirror --reverse --delete --verbose \
    ./wp-content/themes/twentytwenty-child \
    /public_html/wp-content/themes/twentytwenty-child;
  bye
"
```

Claude Code stores credentials in a local `.env` file that is **never committed to GitHub** (`.gitignore` enforced).

---

#### Mechanism 2 — cPanel Git Version Control (For Full Deploys)

HostPapa's cPanel includes **Git Version Control** — documented by HostPapa to work without SSH. This connects cPanel directly to a GitHub repository and pulls on demand.

**Setup (one-time, done by you in cPanel — not by Claude Code):**

1. In cPanel → Files → Git Version Control → Create
2. Enable "Clone a Repository"
3. Clone URL: `https://github.com/SkipperDon/atmyboat-forum.git`
4. Repository Path: `/public_html/wp-content` (or a subfolder)
5. Click Create — cPanel clones the repo immediately

**To deploy after that:**
- In cPanel → Git Version Control → your repo → Pull or Deploy button
- Or: Claude Code commits and pushes to GitHub, you click Pull in cPanel

**Best used for:** Major phase deployments (end of Phase 2B, Phase 2C, etc.) where you want a clean, version-controlled deployment rather than file-by-file FTP.

---

#### Mechanism 3 — cPanel File Manager (Last Resort / Single Files)

For quick one-off edits or emergencies, cPanel File Manager (browser-based) lets you upload individual files or edit them in-browser.

**Use only for:** Fixing a typo, uploading a single new file, emergency hotfix.
**Never use for:** Deploying whole phases or making multi-file changes (error-prone, no version control).

---

### The Full Claude Code Workflow

This is the session-by-session process for every build phase:

```
┌─────────────────────────────────────────────────────────────┐
│  LOCAL MACHINE (where Claude Code runs)                     │
│                                                             │
│  1. Claude Code reads ATMYBOAT_STANDING_INSTRUCTION.md      │
│  2. Claude Code writes / modifies files in:                 │
│     ./wp-content/themes/twentytwenty-child/                 │
│     ./wp-content/plugins/atmyboat-ai-assistant/             │
│  3. You review the changes in your editor                   │
│  4. Claude Code runs: lftp sync → HostPapa staging          │
│  5. You test in browser at staging URL                      │
│  6. Claude Code commits: git add . && git commit && push    │
│  7. When phase complete: cPanel → Pull → live site          │
└─────────────────────────────────────────────────────────────┘
```

**Rule:** Claude Code never deploys to live directly. It always deploys to staging first via FTPS. You promote staging to live via the HostPapa Staging → Push to Live button (one click in cPanel).

---

### Local Repo Structure

Claude Code maintains this folder structure on your local machine. It mirrors exactly what lives on the server.

```
atmyboat-forum/                         ← GitHub repo root
│
├── .env                                ← FTP credentials (NEVER commit)
├── .gitignore                          ← Includes .env, node_modules, etc.
├── .claudeignore                       ← Tells Claude Code to skip binary/log files
├── README.md
│
├── wp-content/
│   ├── themes/
│   │   └── twentytwenty-child/         ← The child theme (all CSS + PHP)
│   │       ├── style.css               ← Theme header + CSS variables
│   │       ├── functions.php           ← Enqueue scripts, register widgets
│   │       ├── bbpress.css             ← Forum-specific overrides
│   │       ├── footer.php              ← Custom footer template
│   │       └── inc/
│   │           └── atmyboat-config.php ← define() constants (git-ignored)
│   │
│   └── plugins/
│       └── atmyboat-ai-assistant/      ← Custom AI plugin
│           ├── atmyboat-ai-assistant.php
│           ├── ai-handler.php          ← PHP cURL → Anthropic API
│           └── assets/
│               ├── ai-widget.css
│               └── ai-widget.js
│
├── deploy/
│   ├── sync-staging.sh                 ← lftp command to push to staging
│   ├── sync-live.sh                    ← lftp command to push to live
│   └── db-seeds/
│       ├── bbpress-categories.sql      ← 7 forum categories
│       └── seed-threads.sql            ← 10 starter threads
│
└── docs/
    ├── ATMYBOAT_BUILD_REFERENCE.md     ← This document (copy)
    └── ATMYBOAT_STANDING_INSTRUCTION.md
```

---

### Database Changes Without SSH

WP-CLI (the standard WordPress command-line tool) requires SSH. Without it, all database operations use one of:

**phpMyAdmin (in cPanel):**
- Import `.sql` files directly — used for bbPress category seeding, test data
- Run queries manually — used for one-off fixes
- Export full DB before every phase transition — part of the backup checklist

**WordPress Admin UI:**
- Install plugins via Plugins → Add New → Upload (ZIP file)
- Activate/deactivate plugins
- bbPress forum creation via WP Admin → Forums → Add New
- MailPoet list configuration via MailPoet admin panel

**PHP installer scripts (for repeatable setup):**
For anything that needs to run once and be reproducible (e.g. creating all 7 bbPress categories with correct slugs), Claude Code writes a self-deleting PHP installer script:

```php
<?php
// atmyboat-setup-forums.php
// Upload via FTP, visit URL once, delete immediately.
// NEVER leave this file on the server.

if (!defined('ABSPATH')) {
    require_once('../../../wp-load.php');
}

// Create forum categories via bbPress functions
$forums = [
    ['d3kOS Support', 'd3kos-support', 'Installation, configuration, troubleshooting'],
    ['AI-Assisted Fixes', 'ai-assisted-fixes', 'Share your AI-assisted repair wins'],
    // ... etc
];

foreach ($forums as [$title, $slug, $desc]) {
    bb_new_forum(['forum_name' => $title, 'forum_slug' => $slug, 'forum_desc' => $desc]);
}

echo 'Done. Delete this file now.';
// Optionally: unlink(__FILE__);
?>
```

Upload via FTPS, visit `staging.atmyboat.com/wp-content/themes/twentytwenty-child/atmyboat-setup-forums.php`, delete immediately. Claude Code writes these for each phase that needs DB setup.

---

### Phase 0 Checklist Additions for This Strategy

Add these to the Phase 0 checklist before any Claude Code session:

- [ ] Collect FTP hostname, username, password from HostPapa cPanel → FTP Accounts
- [ ] Confirm staging subdomain URL from cPanel → Softaculous → Staging
- [ ] Create GitHub repo: `github.com/SkipperDon/atmyboat-forum`
- [ ] In cPanel → Git Version Control → clone from GitHub repo into a staging path
- [ ] Install `lftp` on local machine (`brew install lftp` on Mac, `apt install lftp` on Linux)
- [ ] Create `.env` file locally with FTP credentials, confirm `.gitignore` excludes it
- [ ] Test `deploy/sync-staging.sh` with a single test file before beginning Phase 1
- [ ] Confirm cPanel File Manager can browse `/public_html/wp-content/themes/`

---

### What Claude Code Asks You to Do vs. Does Itself

| Task | Who Does It | How |
|---|---|---|
| Write PHP, CSS, JS files | Claude Code | Generates locally |
| Upload files to staging | Claude Code | `lftp` FTPS sync via `sync-staging.sh` |
| Install plugins (ZIP) | You | WP Admin → Upload Plugin |
| Create forum categories | Claude Code | Writes PHP installer script → you run it once |
| Seed test threads | Claude Code | Writes SQL → you import via phpMyAdmin |
| Backup before phase | You | UpdraftPlus → Backup Now |
| Review changes in browser | You | Browse staging URL |
| Approve and promote to live | You | HostPapa cPanel → Staging → Push to Live |
| Commit to GitHub | Claude Code | `git add . && git commit -m "..." && git push` |
| Configure MailPoet | You | MailPoet admin panel (Claude Code gives instructions) |
| Anthropic API key | You | Set in `atmyboat-config.php` (never committed) |

---

### What Claude Code CANNOT Do on HostPapa

Record these constraints — do not ask Claude Code to attempt them:

| Cannot Do | Reason | Workaround |
|---|---|---|
| Run `wp-cli` commands | No SSH | PHP installer scripts + WP Admin |
| Run `composer install` | No SSH | Not needed — pure PHP, no dependencies |
| Run `npm` or build JS | No SSH | Vanilla JS only, no build step needed |
| Restart PHP/Apache | No SSH / no root | Not needed for this stack |
| Set cron jobs via crontab | No SSH | WordPress cron (`wp_schedule_event`) or cPanel Cron Jobs UI |
| Access server logs directly | No SSH | cPanel → Logs → Error Log viewer |
| Run database migrations | No SSH | phpMyAdmin SQL import |
| Set file permissions recursively | No SSH | cPanel File Manager → select all → permissions |

---

*Part 15 added March 2026. Deployment strategy confirmed for HostPapa Growth shared hosting (no SSH). Primary deploy path: FTPS via lftp. Version control: GitHub → cPanel Git Version Control.*
