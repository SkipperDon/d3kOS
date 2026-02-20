# AtMyBoat.com - Low-Cost E-Commerce Recommendation

**Date:** 2026-02-20
**Hosting:** HostPapa Shared Hosting (no SSH access)
**File Transfer:** WinSCP (SFTP/FTP)
**Budget:** Low cost (minimize monthly fees)

---

## YOUR HOSTING CONSTRAINTS

**HostPapa Shared Hosting:**
- ✅ PHP/MySQL available (cPanel)
- ✅ FTP/SFTP access (WinSCP)
- ✅ SSL certificate (Let's Encrypt free)
- ❌ **NO SSH** - Cannot run systemd services, Node.js, Python background workers
- ❌ **NO root access** - Cannot install custom software
- ❌ **Shared resources** - Limited CPU/RAM, no dedicated server

**What This Means:**
- ❌ Cannot use the full Stripe Billing implementation from `STRIPE_BILLING_IMPLEMENTATION_GUIDE.md`
  - That guide requires: Python/Flask backend, systemd services, background workers
  - Designed for Raspberry Pi or VPS with full server control
- ✅ **CAN use Stripe Payment Links** (no-code, hosted by Stripe)
- ✅ **CAN use embedded e-commerce widgets** (JavaScript embeds)
- ✅ **CAN upload static HTML/CSS/JS** via WinSCP

---

## RECOMMENDED SOLUTION: HYBRID E-COMMERCE

### Product Categories to Sell

1. **d3kOS Software Subscriptions** (SaaS - recurring)
   - Tier 2 Premium: $9.99/month
   - Tier 3 Enterprise: $99.99/year

2. **d3-k1 Hardware Kit** (Physical product - one-time)
   - Complete kit: $299-499 (TBD pricing)
   - Pre-order now, ship later

3. **Optional Accessories** (one-time)
   - Camera mount, cables, cases, etc.

---

## SOLUTION 1: STRIPE PAYMENT LINKS (For Subscriptions) ⭐ RECOMMENDED

**Best for:** d3kOS Tier 2 and Tier 3 subscriptions

### Why Stripe Payment Links?

✅ **No backend code needed** - Everything hosted by Stripe
✅ **Free to use** - Only pay transaction fees (2.9% + $0.30)
✅ **Handles recurring billing** - Automatic monthly/yearly charges
✅ **Failed payment recovery** - Automatic retries (3 attempts)
✅ **Customer portal** - Users can cancel/update payment methods
✅ **Works on shared hosting** - Just embed a button/link on your site
✅ **Professional checkout** - Stripe-hosted payment page

### How It Works

```
User clicks "Subscribe to Tier 2" button on atmyboat.com
  ↓
Redirects to Stripe-hosted checkout page
  ↓
User enters payment info (credit card)
  ↓
Stripe processes payment
  ↓
Stripe sends webhook to your webhook handler (see below)
  ↓
User receives confirmation email
  ↓
Subscription auto-renews monthly/yearly
```

### Setup Steps (30 minutes)

1. **Create Stripe Account** (free)
   - Go to https://stripe.com
   - Sign up for account
   - Complete business verification

2. **Create Products in Stripe Dashboard**
   - Product 1: "d3kOS Tier 2 Premium" - $9.99/month recurring
   - Product 2: "d3kOS Tier 3 Enterprise" - $99.99/year recurring

3. **Create Payment Links**
   - Click "Payment Links" in Stripe Dashboard
   - Create new payment link for each product
   - Copy the payment link URL (e.g., `https://buy.stripe.com/abc123def456`)

4. **Embed Buy Buttons on Website**
   ```html
   <!-- d3kOS Tier 2 Monthly Subscription -->
   <a href="https://buy.stripe.com/your-tier2-link" class="btn btn-primary">
     Subscribe - $9.99/month
   </a>

   <!-- d3kOS Tier 3 Annual Subscription -->
   <a href="https://buy.stripe.com/your-tier3-link" class="btn btn-success">
     Subscribe - $99.99/year (Save 17%)
   </a>
   ```

5. **Collect Installation ID** (IMPORTANT!)
   - Problem: Stripe needs to know which d3kOS installation to activate
   - Solution: Add custom field to payment link
   - In Stripe Dashboard → Payment Link → Custom Fields:
     - Add text field: "Installation ID" (required)
     - User enters their 16-character ID from d3kOS onboarding

6. **Upload to HostPapa**
   - Edit `ATMYBOAT_LANDING_PAGE.html`
   - Add Stripe payment buttons
   - Upload via WinSCP

### Cost

- **Monthly fee:** $0 (Stripe is free to use)
- **Transaction fees:** 2.9% + $0.30 per payment
- **Example:** $9.99 subscription = $0.29 + $0.30 = $0.59 fee (keep $9.40)

---

## SOLUTION 2: ECWID FREE PLAN (For Hardware Sales) ⭐ RECOMMENDED

**Best for:** d3-k1 hardware kit and accessories

### Why Ecwid?

✅ **Free plan** - Up to 10 products, unlimited orders
✅ **No monthly fees** - Only pay transaction fees
✅ **Embeds on existing site** - Add via JavaScript snippet
✅ **Mobile-responsive** - Works on all devices
✅ **Inventory management** - Track stock levels
✅ **Shipping calculator** - Automatic shipping costs
✅ **PayPal + Stripe** - Accept credit cards and PayPal
✅ **Works with shared hosting** - No backend required

### How It Works

```
User browses products on atmyboat.com
  ↓
Clicks "Add to Cart" (Ecwid widget)
  ↓
Shopping cart opens (overlay or separate page)
  ↓
User enters shipping address
  ↓
Shipping cost calculated automatically
  ↓
User pays via Stripe or PayPal
  ↓
You receive order notification
  ↓
Ship product, mark as fulfilled in Ecwid dashboard
```

### Setup Steps (1 hour)

1. **Create Ecwid Account** (free)
   - Go to https://www.ecwid.com
   - Sign up for FREE plan

2. **Add Products**
   - d3-k1 Complete Kit - $299
     - Description, photos, specs
     - Weight for shipping calculation
   - Camera Mount - $29
   - Etc.

3. **Configure Shipping**
   - Set shipping zones (USA, Canada, etc.)
   - Add shipping rates (flat rate or calculated)

4. **Connect Payment Processors**
   - Add Stripe account
   - Add PayPal account (optional)

5. **Get Embed Code**
   - Ecwid Dashboard → "Get Code"
   - Copy JavaScript snippet

6. **Add to Website**
   ```html
   <!-- Add to <head> section -->
   <script src="https://app.ecwid.com/script.js?12345678"></script>

   <!-- Add where you want store to appear -->
   <div id="my-store-12345678"></div>
   <script>
     Ecwid.init();
   </script>
   ```

7. **Upload to HostPapa**
   - Edit landing page HTML
   - Add Ecwid embed code
   - Upload via WinSCP

### Cost

- **Monthly fee:** $0 (free plan)
- **Transaction fees:**
  - Stripe: 2.9% + $0.30
  - PayPal: 2.9% + $0.30
- **Example:** $299 hardware kit = $8.67 + $0.30 = $8.97 fee (keep $290.03)

### Ecwid Free Plan Limitations

- Max 10 products (enough for d3-k1 kit + accessories)
- 1 staff account
- Ecwid branding on checkout (upgrade to remove)

---

## SOLUTION 3: WEBHOOK HANDLER (For Tier Activation)

**Problem:** Stripe charges customer, but how does d3kOS Pi know to activate Tier 2/3?

**Solution:** Lightweight webhook handler (receives Stripe events, updates database)

### Option A: Vercel Serverless Function (FREE) ⭐ RECOMMENDED

**Why Vercel?**
- ✅ Free tier (100 GB bandwidth/month, 100k function invocations)
- ✅ Automatic HTTPS
- ✅ Easy deployment (Git push)
- ✅ Supports Node.js, Python, Go

**How It Works:**
```
Stripe sends webhook (subscription created)
  ↓
Vercel function receives webhook
  ↓
Validates Stripe signature
  ↓
Extracts: installation_id, tier, subscription_id
  ↓
Updates central database (PostgreSQL/MySQL)
  ↓
Returns 200 OK to Stripe
  ↓
d3kOS Pi polls database (every 24h)
  ↓
Sees tier upgrade → Activates Tier 2/3 features
```

**Setup Steps (2 hours):**

1. **Create Vercel Account** (free)
   - https://vercel.com
   - Sign up with GitHub

2. **Create Repository**
   - GitHub: `d3kos-stripe-webhook`

3. **Add Webhook Function**
   - File: `api/stripe-webhook.js`
   ```javascript
   // Vercel Serverless Function
   const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
   const { Pool } = require('pg'); // PostgreSQL client

   const pool = new Pool({
     connectionString: process.env.DATABASE_URL
   });

   module.exports = async (req, res) => {
     const sig = req.headers['stripe-signature'];
     let event;

     try {
       // Verify webhook signature
       event = stripe.webhooks.constructEvent(
         req.body,
         sig,
         process.env.STRIPE_WEBHOOK_SECRET
       );
     } catch (err) {
       return res.status(400).send(`Webhook Error: ${err.message}`);
     }

     // Handle subscription events
     if (event.type === 'customer.subscription.created' ||
         event.type === 'customer.subscription.updated') {

       const subscription = event.data.object;
       const installationId = subscription.metadata.installation_id;
       const tier = subscription.metadata.tier; // "2" or "3"

       // Update database
       await pool.query(
         'UPDATE installations SET tier = $1, subscription_status = $2 WHERE installation_id = $3',
         [tier, subscription.status, installationId]
       );
     }

     res.json({ received: true });
   };
   ```

4. **Deploy to Vercel**
   - Connect GitHub repo
   - Vercel auto-deploys on push
   - Get webhook URL: `https://your-project.vercel.app/api/stripe-webhook`

5. **Configure Stripe Webhook**
   - Stripe Dashboard → Webhooks
   - Add endpoint: `https://your-project.vercel.app/api/stripe-webhook`
   - Select events: `customer.subscription.*`

6. **Add Environment Variables in Vercel**
   - `STRIPE_SECRET_KEY` - From Stripe Dashboard
   - `STRIPE_WEBHOOK_SECRET` - From Stripe Webhook settings
   - `DATABASE_URL` - PostgreSQL connection string

**Cost:** $0 (Vercel free tier)

---

### Option B: Railway (FREE)

Alternative to Vercel, same concept:
- Free tier: $5 credit/month (enough for webhook handler)
- Supports Docker containers
- Built-in PostgreSQL database

---

### Option C: Netlify Functions (FREE)

Similar to Vercel:
- Free tier: 125k function invocations/month
- Same setup process

---

## COMPLETE E-COMMERCE ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                    ATMYBOAT.COM (HostPapa)                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Landing Page (HTML/CSS/JS)                          │  │
│  │                                                        │  │
│  │  ┌─────────────────┐    ┌──────────────────────┐    │  │
│  │  │ Stripe Payment  │    │  Ecwid Store Widget  │    │  │
│  │  │ Links (Tiers)   │    │  (Hardware Sales)    │    │  │
│  │  └─────────────────┘    └──────────────────────┘    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                 │                           │
                 │                           │
         (Subscription)              (Hardware Purchase)
                 │                           │
                 ↓                           ↓
    ┌─────────────────────┐    ┌──────────────────────┐
    │  Stripe Checkout    │    │  Ecwid Checkout      │
    │  (Hosted by Stripe) │    │  (Hosted by Ecwid)   │
    └─────────────────────┘    └──────────────────────┘
                 │                           │
                 │                           │
           (Webhook)                   (Order Email)
                 │                           │
                 ↓                           ↓
    ┌─────────────────────┐    ┌──────────────────────┐
    │ Vercel Serverless   │    │   You (Fulfill       │
    │ Function (FREE)     │    │   Order Manually)    │
    └─────────────────────┘    └──────────────────────┘
                 │
                 │
        (Update Database)
                 │
                 ↓
    ┌─────────────────────┐
    │  Central Database   │
    │  (PostgreSQL)       │
    │  - Subscriptions    │
    │  - Installations    │
    └─────────────────────┘
                 ↑
                 │
         (Poll every 24h)
                 │
    ┌─────────────────────┐
    │  d3kOS Raspberry Pi │
    │  (User's Boat)      │
    │  Checks tier status │
    │  Activates features │
    └─────────────────────┘
```

---

## STEP-BY-STEP IMPLEMENTATION PLAN

### Phase 1: Update Landing Page (2-3 hours)

1. **Edit Existing Landing Page**
   - File: `/home/boatiq/Helm-OS/doc/ATMYBOAT_LANDING_PAGE.html`
   - Add Stripe payment buttons for Tier 2 and Tier 3
   - Add Ecwid embed code for hardware store

2. **Test Locally**
   - Open HTML file in browser
   - Click buttons (won't work until Stripe/Ecwid configured)

3. **Upload to HostPapa**
   - Open WinSCP
   - Connect to HostPapa server
   - Upload HTML file to `public_html/` or `public_html/index.html`
   - Upload any images/CSS files

### Phase 2: Setup Stripe Payment Links (1 hour)

1. Create Stripe account
2. Create products (Tier 2 Monthly, Tier 3 Annual)
3. Create payment links
4. Add custom field "Installation ID"
5. Copy payment link URLs
6. Update landing page HTML with real URLs
7. Upload updated HTML to HostPapa

### Phase 3: Setup Ecwid Store (1-2 hours)

1. Create Ecwid account
2. Add products (d3-k1 kit, accessories)
3. Configure shipping rates
4. Connect Stripe/PayPal
5. Get embed code
6. Add to landing page HTML
7. Upload to HostPapa

### Phase 4: Setup Webhook Handler (2-3 hours) - OPTIONAL FOR NOW

**Note:** Can skip this initially if you manually activate tiers

1. Create Vercel account
2. Create GitHub repo
3. Add webhook function code
4. Deploy to Vercel
5. Configure Stripe webhook
6. Add environment variables
7. Test with Stripe test mode

### Phase 5: Test Everything (1 hour)

1. Test Stripe payment links (use test mode)
2. Test Ecwid checkout
3. Verify webhook receives events (if implemented)
4. Check order notifications
5. Test mobile responsiveness

---

## TOTAL COSTS

### Setup Costs (One-time)
- Stripe account: $0 (free)
- Ecwid account: $0 (free plan)
- Vercel account: $0 (free tier)
- Domain (atmyboat.com): Already owned
- SSL certificate: $0 (Let's Encrypt via HostPapa)
- **Total:** $0

### Monthly Costs
- HostPapa hosting: ~$10-20/month (existing)
- Stripe: $0 monthly fee
- Ecwid: $0 (free plan)
- Vercel: $0 (free tier)
- **Total:** $10-20/month (just hosting)

### Transaction Fees
- Stripe subscriptions: 2.9% + $0.30 per charge
- Ecwid hardware: 2.9% + $0.30 per order (via Stripe/PayPal)

### Revenue Example (100 Tier 2 Subscribers)
- Gross: $999/month
- Stripe fees: $89.70/month (9%)
- **Net: $909.30/month** (91% kept)

Much better than the 67% in the original plan because:
- No Apple/Google 30% cut (using web checkout)
- No backend server costs
- No additional software fees

---

## ALTERNATIVES CONSIDERED (NOT RECOMMENDED)

### ❌ WooCommerce (WordPress)
- Requires WordPress installation
- More complex setup
- Need WordPress hosting (HostPapa supports but more work)
- Overkill for simple subscriptions

### ❌ Shopify
- $29-299/month subscription fee
- Transaction fees on top
- Too expensive for low-cost requirement

### ❌ Square Online
- Good option, but Ecwid has better free plan
- Square charges 2.9% + $0.30 + monthly fee ($0-$72/month)

### ❌ PayPal Subscriptions
- Can work, but Stripe has better tools
- No automatic retry on failed payments
- Less professional checkout experience

---

## RECOMMENDED APPROACH

**For Your Situation:**

1. **Start Simple** (Phase 1-3 only)
   - Update landing page
   - Add Stripe Payment Links for subscriptions
   - Add Ecwid for hardware
   - **Skip webhook handler initially**
   - Manually activate tiers when customers email you their installation_id

2. **After First 10-20 Customers** (Add Phase 4)
   - Setup Vercel webhook handler
   - Automate tier activation
   - Setup central database

3. **After Revenue Grows** (Future)
   - Upgrade to paid plans if needed
   - Build full backend API
   - Create mobile apps

**Total Time to Launch:**
- Phase 1-3: 4-6 hours
- Can launch and start selling in ONE DAY!

**Total Cost:**
- Setup: $0
- Monthly: $10-20 (just hosting)
- Revenue: Keep 91% (Stripe fees only)

---

## NEXT STEPS

1. **Review landing page HTML** - `/home/boatiq/Helm-OS/doc/ATMYBOAT_LANDING_PAGE.html`
2. **Make any content updates** - Edit in WordPerfect, paste into HTML
3. **Create Stripe account** - https://stripe.com
4. **Create Ecwid account** - https://ecwid.com
5. **I'll help you integrate** - Add payment buttons and store widget to HTML
6. **Test locally** - Open in browser, verify layout
7. **Upload to HostPapa** - Use WinSCP
8. **Launch!** - Start accepting orders

**Want me to update the landing page HTML with Stripe/Ecwid integration now?**

---

**Document Version:** 1.0
**Date:** 2026-02-20
**Status:** Ready for implementation
