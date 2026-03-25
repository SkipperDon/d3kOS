# AtMyBoat.com — Session 6 Content Plan
**Version 1.0 · 2026-03-24 · For Operator Review Before Any Building Starts**
**Status: DRAFT — awaiting operator approval before Session 6 begins**

> This document draws from original content documents:
> - `doc/ATMYBOAT_LANDING_PAGE_CONTENT.md` (Feb 2026 — original brand copy, tiers)
> - `doc/ATMYBOAT_ABOUT_PAGE.html` (original About page — Lake Erie origin story, mission)
> - `doc/ATMYBOAT_CONTACT_PAGE.html` (original Contact page — service@atmyboat.com, form, support hours)
> - `doc/d3kOS-MARKETING-SHEET.md` (connectivity: NMEA 2000, WiFi, Ethernet, CX5106, PiCAN-M)
> - `deployment/v0.9.3/atmyboat-mockup-v2-accessible.html` (visual design spec)
> - `deployment/v0.9.3/ATMYBOAT_BUILD_REFERENCE.md` (tier definitions, Part 9 + 16)
>
> All content below is sourced from these documents. Where gaps exist (new pages
> not previously planned), they are clearly marked [NEW — needs Don's input].
>
> **Do not start Session 6 until this document is reviewed and approved.**

---

## DESIGN SYSTEM (applies to every page below)

All pages use the dark nautical workshop aesthetic from the mockup. No exceptions.

- **Background:** `#0A2342` (navy deep)
- **Headings:** Fraunces — amber `#D4920F`
- **Body text:** Nunito — warm cream `#F0EAD8`, 20px minimum, 1.85 line-height
- **Accent:** Teal `#22A090` for AI features, secondary links
- **Blueprint grid:** subtle teal grid on body background (from mockup)
- **Voice/Tone:** Warm, plain English, "trusted friend at the helm" — never corporate, never startup

---

## PAGE 1 — `/about` — Our Story

**File to create:** `page-about.php`
**Type:** Public, informational
**Session:** S6

### What goes on this page

**HERO**
- Eyebrow label (mono): `ABOUT ATMYBOAT.COM`
- Headline: *"Open-source marine intelligence. Built by Skipper Don. For boaters who believe their boat deserves better electronics."*
- Subtext: *"At My Boat began in November 2025 on the waters of Lake Erie — a personal project born out of frustration with expensive, closed marine electronics that didn't talk to each other."*

**SECTION: Our Story**
Source: `doc/ATMYBOAT_ABOUT_PAGE.html`
> At My Boat began in November 2025 with a simple mission: to make marine electronics accessible, affordable, and open to every boater. What started as a personal project by Skipper Don on the waters of Lake Erie has rapidly grown into a trusted resource for boaters seeking to modernize their vessels without breaking the bank.
>
> We believe that marine electronics shouldn't be a mystery. For too long, boaters have been locked into expensive proprietary systems with limited flexibility. At My Boat challenges this status quo by bridging the gap between proprietary marine systems and open-source innovation.

**SECTION: What We Do**
Source: `doc/ATMYBOAT_ABOUT_PAGE.html`
Four cards:
1. **d3kOS Marine Electronics Platform** — flagship open-source helm control system. Professional-grade monitoring at a fraction of the cost.
2. **DIY Marine Electronics Guides** — step-by-step tutorials for building and installing your own marine systems using affordable, off-the-shelf components.
3. **Real-World Testing** — every product and system has been tested on the water in real Canadian boating conditions.
4. **Community Support** — a growing community of boaters sharing knowledge, tips, and troubleshooting advice.

**SECTION: Our Mission**
Source: `doc/ATMYBOAT_ABOUT_PAGE.html`
> We're here to democratize marine electronics by:
> - Making professional-grade marine monitoring accessible to every boater
> - Providing open-source alternatives to expensive proprietary systems
> - Creating compatibility bridges between old and new marine technology
> - Sharing knowledge freely through our blog, guides, and community

**SECTION: Why d3kOS Exists**
Source: `doc/ATMYBOAT_LANDING_PAGE_CONTENT.md` + `doc/ATMYBOAT_ABOUT_PAGE.html`
> The d3kOS project emerged from years of frustration with expensive, proprietary marine electronics that didn't talk to each other. We believe boaters should have access to professional-grade systems without the professional-grade price tags — and without being locked into closed ecosystems.
>
> The d3kOS (d3k Operating System) is built on proven Raspberry Pi hardware and open-source software. It provides NMEA 2000 integration, voice assistant, Marine Vision camera, cloud sync, and AI diagnostics — complete system for under $1,000 vs. $5,000+ proprietary alternatives.

**SECTION: Growing Community**
Source: `doc/ATMYBOAT_ABOUT_PAGE.html`
> Since launching in November 2025, At My Boat has experienced rapid growth within the marine electronics community. Our blog posts reach thousands of boaters monthly, and d3kOS is being adopted by recreational boaters, fishing enthusiasts, and small commercial operators across North America.
>
> What sets us apart is our commitment to real-world practicality. Every feature in d3kOS was born from actual needs encountered on the water. We don't build technology for technology's sake — we solve real problems boaters face every day.

**CLOSING CTA**
- Headline: *"Ready to Modernize Your Boat?"*
- Body: *"Join hundreds of boaters using d3kOS to monitor their vessels."*
- Buttons: `Download d3kOS — Free` · `Explore Hardware` · `Join the Community`

---

## PAGE 2 — `/contact` — Contact Us

**File to create:** `page-contact.php`
**Type:** Public
**Session:** S6

### What goes on this page

**HERO**
- Eyebrow: `GET IN TOUCH`
- Headline: *"We're real boaters. We answer real questions."*
- Subtext: *"Try the AI assistant first — it answers most questions instantly. If you need Don, his inbox is below."*

**AI CUSTOMER SERVICE PANEL** (amber bordered — uses existing Gemini widget)
- Label (mono): `AI FIRST MATE — ASK ANYTHING`
- Prompt placeholder: *"Where do I find my subscription? How do I pair my Pi? What is my tier?"*
- Answers questions about: subscriptions, accounts, hardware, d3kOS setup, billing, where to find things on the site
- Note below widget: *"AI responses are generated from our documentation. For billing disputes or account issues, use the form below."*

**CONTACT FORM**
Source: `doc/ATMYBOAT_CONTACT_PAGE.html` (fully written — needs dark theme adaptation)
Fields: Name · Email · Subject (dropdown: General Inquiry / Billing & Subscriptions / Technical Support / Partnership / Other) · Message
Submit button: `Send Message`
After submit: *"Message received. Don usually responds within 1–2 business days."*

**DIRECT CONTACT**
Source: `doc/ATMYBOAT_CONTACT_PAGE.html`
- Email: `service@atmyboat.com`
- Support hours: Monday–Friday 9:00 AM – 5:00 PM EST. Weekend support for urgent issues.
- Note: *"For urgent Pi issues — T2 and T3 subscribers use Fix My Pi for faster response."* (link to `/fix-my-pi`)

**WHERE TO FIND COMMON THINGS** (3 quick-link cards)
1. Subscription management → `/account`
2. Software download → `/download`
3. Community help → `/forum`

---

## PAGE 3 — `/pricing` — Plans & Pricing

**File to create:** `page-pricing.php`
**Type:** Public — critical revenue page
**Session:** S6

> **Note:** This is the most important new page. Every user decision — download vs. subscribe — happens here. Must be clear, honest, and reflect the lifestyle brand. Not a corporate pricing table.

### What goes on this page

**HERO**
- Eyebrow: `CHOOSE YOUR TIER`
- Headline: *"Start free. Upgrade when you're ready."*
- Subtext: *"d3kOS is free to download and use forever. Paid tiers add cloud features, AI analysis, and peace-of-mind diagnostics — for serious cruisers who want more."*

**TIER CARDS** (4 cards — source: `doc/ATMYBOAT_LANDING_PAGE_CONTENT.md` + BUILD_REFERENCE Part 9)

---

**T0 — Open Water**
Badge: `FREE FOREVER`
Tagline: *"Your boat. Your data. Nobody else's."*
Description: *"Full d3kOS on your d3-k1. 100% offline — no internet required, no account, no tracking. Everything runs on your Pi. Complete privacy is a core promise, not a setting."*

Features:
- GPS, engine monitoring, voice assistant, AI diagnostics
- OpenCPN navigation with nautical charts
- NMEA 2000 integration (engine, depth, GPS, AIS)
- Boat log and voyage history
- 100% offline — never phones home
- No account required

Fix My Pi: Not available (T0 has no cloud connection by design)
Upgrade path: Download new image from /download

CTA: `Download d3kOS — Free`

---

**T1 — First Mate** ⭐ Most Popular
Badge: `FREE ALWAYS`
Tagline: *"Everything in T0, plus your boat follows you home."*
Description: *"Connect d3kOS to the cloud and monitor your boat from any browser. Voyage logs, health alerts, and community access — all free, always."*

Features:
- Everything in T0
- Web dashboard — The Chart Room
- Voyage history in the cloud
- Community forum access
- OTA firmware updates
- Find My Boat (last known GPS)
- Fix My Pi: $29.99 per incident

CTA: `Register Free →`

---

**T2 — Skipper**
Badge: `$9.99 / MONTH`
Tagline: *"AI that actually knows your boat."*
Description: *"Advanced engine analytics, predictive maintenance recommendations, and 3 included Fix My Pi checks every month. For the cruiser who wants to stay ahead of problems, not react to them."*

Features:
- Everything in T1
- AI-powered engine performance analysis
- Predictive maintenance recommendations
- Trend analysis — spot issues before they become failures
- PDF boat health reports (email to yourself or your mechanic)
- 3 Fix My Pi checks included per month
- Multiple phones — family and crew access

CTA: `Subscribe — $9.99/mo`

---

**T3 — Admiral**
Badge: `$99.99 / YEAR`
Tagline: *"For the captain who runs more than one boat."*
Description: *"Everything in T2, plus fleet management for multiple vessels. Unlimited Fix My Pi, unlimited PDF reports. Annual billing — one payment, one year of full access."*

Features:
- Everything in T2
- Multi-boat support — manage a fleet from one account
- Fleet GPS map — see all your Pis on one map
- Unlimited Fix My Pi — no monthly limit
- Unlimited PDF boat reports
- Commercial data export (CSV)
- Priority support

CTA: `Subscribe — $99.99/yr`

---

**COMPARISON TABLE** (below tier cards)
Full feature comparison matrix — all tiers, all features, checkmarks and dashes.

**FAQ SECTION** (below comparison table)
- *Can I switch tiers?* Yes, anytime. Upgrade takes effect immediately. Downgrade takes effect at end of billing period.
- *What is Fix My Pi?* d3kOS runs a full diagnostic on your Pi and attempts to automatically restore any broken services. A detailed report is saved to your account.
- *Does T0 ever expire?* No. T0 is free forever. It runs completely offline with no account required.
- *What happens if I cancel T2 or T3?* Your account reverts to T1 at the end of your billing period. Your data and voyage history are preserved.

CTA at bottom: `Still not sure? Ask the AI →` (links to `/contact`)

---

## PAGE 4 — `/upgrade` — Subscribe

**File to create:** `page-upgrade.php` + backend wired to Stripe
**Type:** Authenticated (must be logged in)
**Session:** S6

### What goes on this page

**HERO**
- Headline: *"You're one step from full access."*
- Current tier shown: *"You're on T1 — First Mate"*

**TWO OPTIONS**

**T2 — Skipper**
Price: $9.99/month · Cancel anytime
3-line summary of what they get
Button: `Subscribe to Skipper — $9.99/mo` → Stripe Checkout

**T3 — Admiral**
Price: $99.99/year · Save $19.89 vs monthly
3-line summary of what they get
Button: `Subscribe to Admiral — $99.99/yr` → Stripe Checkout

**Trust signals below buttons:**
- Secured by Stripe · Cancel anytime · No hidden fees
- *"Questions? See [Pricing →](/pricing) or [Contact Us →](/contact)"*

---

## PAGE 5 — `/help` — Help Centre

**File to create:** `page-help.php`
**Type:** Public
**Session:** S6

### What goes on this page

**HERO**
- Eyebrow: `HELP CENTRE`
- Headline: *"Find your answer in seconds."*
- Subtext: *"The AI searches our documentation and answers most questions instantly."*

**AI HELP WIDGET** (full-width, teal bordered)
- Label: `AI FIRST MATE`
- Placeholder: *"How do I update d3kOS? How do I cancel my subscription? How do I pair my Pi?"*
- Context: support documentation, how-to guides, tier information
- Note: *"Can't find what you need? [Contact Don directly →](/contact)"*

**QUICK LINKS** (6 cards in 2 rows)

Row 1:
1. How to update d3kOS → `/help/software-update`
2. How to downgrade d3kOS → `/help/software-downgrade`
3. How to subscribe (T2/T3) → `/help/create-subscription`

Row 2:
4. How to cancel a subscription → `/help/cancel-subscription`
5. Pair your Pi with the app → `/pair-device`
6. Fix My Pi → `/fix-my-pi`

---

## PAGE 6 — `/help/software-update` — How to Update d3kOS

**File to create:** `page-help-update.php`
**Type:** Public
**Session:** S6

### What goes on this page

**HERO**
- Headline: *"Updating d3kOS"*
- Subtext: *"There are two ways to update: OTA (over-the-air, T1 and above) and manual image replacement (T0)."*

**METHOD 1: OTA UPDATE (T1, T2, T3)**
Step-by-step:
1. Open the d3kOS dashboard on your Pi
2. Tap Settings → System → Check for Updates
3. If an update is available, tap Install Update
4. The system downloads the update in the background (~5 minutes)
5. Tap Restart to apply (the Pi reboots once)
6. After restart, verify version in Settings → About

Note: *"OTA updates are automatic on T2 and T3. You will see a notification on the dashboard when an update is ready."*

**METHOD 2: MANUAL IMAGE REPLACEMENT (T0 or recovery)**
Step-by-step:
1. Download the latest d3kOS image from [/download](/download)
2. Flash to a fresh microSD using Raspberry Pi Imager or Balena Etcher
3. Swap the microSD in your d3-k1
4. Power on and run the 20-step setup wizard
5. Your configuration will need to be re-entered (T0 has no cloud backup)

Note: *"T0 users should note down their settings before flashing. T1+ users: your voyage history and settings are preserved in the cloud and will restore automatically after pairing."*

---

## PAGE 7 — `/help/software-downgrade` — How to Downgrade d3kOS

**File to create:** `page-help-downgrade.php`
**Type:** Public
**Session:** S6

### What goes on this page

**HERO**
- Headline: *"Downgrading d3kOS"*
- Subtext: *"If a recent update caused issues, you can roll back to a previous version."*

**IMPORTANT NOTE (amber bordered warning)**
*"Downgrading is a manual process — it requires reflashing your microSD. This will not affect your cloud data (voyage history, settings) on T1+."*

**STEPS**
1. Visit [/download](/download) and select the version you want under "Previous Releases"
2. Download the image (.zip file)
3. Flash to a fresh microSD using Raspberry Pi Imager or Balena Etcher
4. Swap the microSD in your d3-k1
5. Power on — d3kOS will start at the selected version
6. For T1+: re-pair the app to restore your cloud data

**IF YOUR PI IS UNRESPONSIVE**
*"If your Pi won't boot after an update, Fix My Pi can diagnose and attempt recovery remotely. [Try Fix My Pi →](/fix-my-pi)"*

CTA: `Download Previous Versions →` → links to `/download`

---

## PAGE 8 — `/help/create-subscription` — How to Subscribe

**File to create:** `page-help-subscribe.php`
**Type:** Public
**Session:** S6

### What goes on this page

**HERO**
- Headline: *"Upgrading to T2 or T3"*

**STEPS**
1. [Create a free account](/register) if you haven't already (T1 is free)
2. Log in to your account
3. Visit [Plans & Pricing](/pricing) and choose T2 (monthly) or T3 (annual)
4. Click Subscribe — you'll be taken to Stripe's secure checkout
5. Enter your payment details
6. After payment, your tier upgrades immediately
7. Your Pi will sync the new tier on its next check-in (within 30 minutes)

**WHAT CHANGES IMMEDIATELY**
- T2: PDF reports, 3 Fix My Pi checks/month, AI analytics
- T3: Everything in T2, plus fleet management and unlimited checks

**PAYMENT DETAILS**
- All payments processed by Stripe (PCI compliant)
- T2: charged monthly, cancel any time
- T3: charged annually, no monthly option

CTA: `View Plans →` → `/pricing`

---

## PAGE 9 — `/help/cancel-subscription` — How to Cancel

**File to create:** `page-help-cancel.php`
**Type:** Public
**Session:** S6

### What goes on this page

**HERO**
- Headline: *"Cancelling your subscription"*
- Subtext: *"You can cancel any time. Your access continues until the end of your billing period."*

**STEPS**
1. Log in to your account
2. Go to [Account → Subscription](/account)
3. Click Cancel Subscription
4. Confirm cancellation
5. Your account reverts to T1 (free) at the end of your billing period

**WHAT HAPPENS TO YOUR DATA**
- Voyage history: preserved on T1 (cloud access continues free)
- Fix My Pi history: preserved
- PDF reports: saved reports remain accessible; new reports require T2+
- Configuration and settings: preserved

**7-DAY GRACE PERIOD**
*"If payment fails on renewal, your account enters a 7-day grace period before reverting to T1. You'll receive an email with a link to update your payment method."*

**STILL NEED HELP?**
CTA: `Contact Don →` → `/contact`

---

## PAGE 10 — `/account` — Account & Subscription Management

**File to create:** `page-account.php`
**Type:** Authenticated (T1+)
**Session:** S7 (more complex — reads live Stripe data)

### What goes on this page

**PANEL: Current Plan**
- Shows current tier badge (T0 / T1 / T2 / T3)
- If T2: shows next billing date, amount, cancel button
- If T3: shows renewal date, amount, cancel button
- If T1: shows upgrade CTA → `/upgrade`

**PANEL: Paired Devices**
- List of paired Pis: vessel name, device ID, last sync time
- Add device button → `/pair-device`

**PANEL: Billing History**
- Table: date, product, amount, Stripe receipt link

**PANEL: Manage Subscription** (T2/T3 only)
- Update payment method (Stripe Customer Portal)
- Cancel subscription
- Downgrade confirmation: *"Your access continues until [date]. After that your account returns to T1."*

---

## CONNECTIVITY STORY — WHERE IT LIVES ON THE SITE

This was missing from the plan entirely. The WiFi, Ethernet, and NMEA 2000 connectivity story is the technical core of d3kOS. It must be told properly in two places.

### On `/hardware` (existing page — needs update in S6)

Current state: lists components. Missing: the connectivity story.

**Add section: "How d3kOS Connects to Your Boat"**

Three connection types:

**NMEA 2000 (the data backbone)**
*"NMEA 2000 is the standard that modern marine electronics use to talk to each other — chartplotters, GPS, engine sensors, depth sounders, AIS. d3kOS connects to your NMEA 2000 bus via the PiCAN-M HAT, which sits directly on the Raspberry Pi."*

*"If your boat has older analogue gauges (the kind with a needle), you need the CX5106 analogue gateway. It reads your existing RPM, temperature, fuel, oil pressure, and voltage sensors and broadcasts them on NMEA 2000. No engine modifications required."*

Compatible with: Garmin, Simrad, Raymarine, Lowrance, Furuno, Humminbird — any chartplotter on your NMEA 2000 network.

**WiFi (your phone and tablet connect here)**
*"d3kOS connects to your boat's existing WiFi network. Once connected, you access the dashboard from any phone, tablet, or laptop on the same network — no app install required. Open a browser, go to the Pi's IP address, and you're in."*

*"If your boat doesn't have WiFi, the Pi can connect directly to a phone hotspot."*

**Ethernet (for permanent helm installations)**
*"For a permanent helm mount, Ethernet is more reliable than WiFi in a marine environment. Run a short ethernet cable from your router or switch to the Pi — no configuration needed."*

---

### On `/products` (existing page — add connectivity section in S6)

Add a "How It Connects" section with a simple diagram (text-based):

```
Your Engines / Sensors
        ↓
   CX5106 Gateway          ← converts analogue signals to NMEA 2000
        ↓
   NMEA 2000 Bus           ← the backbone your chartplotter already uses
        ↓
   PiCAN-M HAT on Pi       ← d3kOS reads everything from here
        ↓
   d3kOS Dashboard         ← engine gauges, GPS, AI, voice — all in one
        ↓
  WiFi / Ethernet
        ↓
  Your Phone / Tablet      ← monitor from anywhere on the boat
```

Works alongside your existing chartplotter — d3kOS does not replace Garmin, Simrad, or Raymarine. It adds an AI intelligence layer that your chartplotter doesn't have.

---

## SUMMARY — PAGES TO BUILD IN S6

| Page | Content source | Notes |
|------|---------------|-------|
| `/about` | `doc/ATMYBOAT_ABOUT_PAGE.html` — original story exists, needs dark theme | Style update + adapt to current design |
| `/contact` | [NEW — structure above] | AI widget + form + service@atmyboat.com |
| `/pricing` | `doc/ATMYBOAT_LANDING_PAGE_CONTENT.md` tiers + BUILD_REFERENCE Part 9 | Most critical page — drives revenue |
| `/upgrade` | BUILD_REFERENCE Part 9 + Stripe | Authenticated, Stripe checkout |
| `/help` | [NEW — structure above] | AI widget + 6 quick links |
| `/help/software-update` | d3kOS onboarding wizard context + OTA architecture | OTA + manual methods |
| `/help/software-downgrade` | [NEW — structure above] | Manual reflash only |
| `/help/create-subscription` | [NEW — structure above] | Step-by-step for T2/T3 |
| `/help/cancel-subscription` | [NEW — structure above] | Steps + grace period info |
| `/hardware` update | `doc/ATMYBOAT_LANDING_PAGE_CONTENT.md` hardware section | Add connectivity section |
| `/products` update | Connectivity diagram | Add "How It Connects" section |

**Deferred to S7:**
| `/account` | Stripe Customer Portal + pairing list | Requires Stripe API integration |

---

## OPERATOR REVIEW QUESTIONS

Before S6 starts, the following need Don's answer:

1. **T3 vessel limit** — unlimited, hard cap of 10, or soft limit with admin override? (decision was needed before v0.9.4 but also affects /pricing copy)
2. **About page photo** — the original About page is text only. Do you want a photo of Don at the helm, or keep it text/illustration?
3. **Contact page** — is `service@atmyboat.com` the right email to display publicly? Or a contact form only?
4. **Pricing page** — the original had "Coming Soon" on T2 and T3. Are these live now? (yes, per BUILD_REFERENCE — Stripe is built in S5)
5. **Fix My Pi price** — confirmed $29.99 per incident for T1?
6. **Hardware connectivity section** — is the CX5106 analogue gateway still the recommended gateway for boats with old analogue gauges?

---

*Review this document. Confirm or correct any item. Session 6 does not start until approved.*
*Source documents: `doc/ATMYBOAT_LANDING_PAGE_CONTENT.md` · `doc/ATMYBOAT_ABOUT_PAGE.html` · `deployment/v0.9.3/atmyboat-mockup-v2-accessible.html` · `deployment/v0.9.3/ATMYBOAT_BUILD_REFERENCE.md`*
