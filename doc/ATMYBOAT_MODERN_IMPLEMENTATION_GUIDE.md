# At My Boat Modern Redesign - Implementation Guide

**Date:** 2026-02-20
**Design:** Dark theme with neon green accents (#BFFF00)
**File:** `ATMYBOAT_MODERN_REDESIGN.html`

---

## STEP 1: ADD YOUR LOGO

### 1.1 Upload Logo to HostPapa

1. **Open WinSCP**, connect to HostPapa
2. Navigate to `public_html/images/` (create folder if it doesn't exist)
3. Upload `logo with better lines.png` from `C:\Users\donmo\Desktop\Atmyboat.com\d3kOS\`
4. Rename to `atmyboat-logo.png` (easier to reference)

### 1.2 Update HTML Logo Section

Find this section in the HTML (around line 234):

```html
<div class="logo-container">
    <!-- Logo will go here - you'll upload logo with better lines.png -->
    <div class="logo-text">
        <span class="at">@</span>MyBoat
    </div>
</div>
```

Replace with:

```html
<div class="logo-container">
    <img src="images/atmyboat-logo.png" alt="At My Boat Logo" style="height: 50px;">
</div>
```

**OR** if you want logo + text:

```html
<div class="logo-container">
    <img src="images/atmyboat-logo.png" alt="At My Boat Logo" style="height: 40px;">
    <div class="logo-text">
        <span class="at">@</span>MyBoat
    </div>
</div>
```

---

## STEP 2: INTEGRATE YOUR 50+ BLOG ENTRIES

### Option A: Manual HTML (Simple)

**If your blog is currently HTML files:**

1. **List your blog posts** in a spreadsheet/document:
   - Title
   - Date
   - Category (DIY, Stories, Tech, Food)
   - Excerpt (2-3 sentences)
   - Link to full post

2. **Find the blog grid** section (around line 669):

```html
<div class="blog-grid">
    <!-- Sample Blog Card 1 -->
    <div class="blog-card">
        ...
    </div>
```

3. **Add each blog post** using this template:

```html
<div class="blog-card">
    <div class="blog-image">
        <i class="fas fa-ICON-NAME"></i>
        <!-- OR use actual image: <img src="images/blog/post-1.jpg" style="width: 100%; height: 100%; object-fit: cover;"> -->
    </div>
    <div class="blog-content">
        <div class="blog-meta">
            <span><i class="fas fa-calendar"></i> FEB 15, 2026</span>
            <span><i class="fas fa-tag"></i> CATEGORY</span>
        </div>
        <h3><a href="blog/your-post.html">YOUR BLOG POST TITLE</a></h3>
        <p class="blog-excerpt">
            Your blog post excerpt goes here. Keep it to 2-3 sentences...
        </p>
        <a href="blog/your-post.html" class="read-more">
            Read More <i class="fas fa-arrow-right"></i>
        </a>
    </div>
</div>
```

**Icon options for blog-image:**
- DIY/Tech: `fas fa-tools`, `fas fa-microchip`, `fas fa-wrench`
- Stories: `fas fa-ship`, `fas fa-anchor`, `fas fa-water`
- Food: `fas fa-utensils`, `fas fa-fish`, `fas fa-cookie`
- Digital Strategy: `fas fa-chart-line`, `fas fa-network-wired`

4. **Repeat for all 50+ posts**

### Option B: Dynamic with JavaScript (Recommended for 50+ posts)

**Create a blog data file** (`blog-posts.js`):

```javascript
// blog-posts.js
const blogPosts = [
    {
        title: "Building Your Own Marine Helm Display",
        date: "Feb 15, 2026",
        category: "DIY",
        icon: "fas fa-tools",
        excerpt: "Step-by-step guide to creating a modern touchscreen helm using d3kOS and open-source hardware...",
        link: "blog/marine-helm-display.html"
    },
    {
        title: "First Ice-Out Trip on Lake Simcoe",
        date: "Feb 12, 2026",
        category: "Stories",
        icon: "fas fa-ship",
        excerpt: "The ice finally cleared and we ventured out for the first boating trip of the season...",
        link: "blog/ice-out-lake-simcoe.html"
    },
    // ... add all 50+ posts here
];
```

**Add to HTML** (before `</body>`):

```html
<script src="blog-posts.js"></script>
<script>
// Dynamically generate blog cards
const blogGrid = document.querySelector('.blog-grid');

blogPosts.forEach(post => {
    const card = `
        <div class="blog-card">
            <div class="blog-image">
                <i class="${post.icon}"></i>
            </div>
            <div class="blog-content">
                <div class="blog-meta">
                    <span><i class="fas fa-calendar"></i> ${post.date}</span>
                    <span><i class="fas fa-tag"></i> ${post.category}</span>
                </div>
                <h3><a href="${post.link}">${post.title}</a></h3>
                <p class="blog-excerpt">${post.excerpt}</p>
                <a href="${post.link}" class="read-more">
                    Read More <i class="fas fa-arrow-right"></i>
                </a>
            </div>
        </div>
    `;
    blogGrid.innerHTML += card;
});
</script>
```

**Benefits:**
- ✅ Easier to manage 50+ posts in one file
- ✅ Can add filtering by category
- ✅ Can add search functionality
- ✅ Can add pagination

---

## STEP 3: ADD STRIPE PAYMENT LINKS

### 3.1 Create Stripe Account

1. Go to https://stripe.com
2. Sign up for account
3. Complete business verification

### 3.2 Create Products

**In Stripe Dashboard:**

1. Click **"Products"** → **"Add Product"**

2. **Create Tier 2 Product:**
   - Name: "d3kOS Tier 2 Premium"
   - Description: "Full AI assistant and marine vision features"
   - Price: $9.99 USD
   - Billing: Recurring monthly
   - Click "Save Product"

3. **Create Tier 3 Product:**
   - Name: "d3kOS Tier 3 Enterprise"
   - Description: "Fleet management and advanced analytics"
   - Price: $99.99 USD
   - Billing: Recurring yearly
   - Click "Save Product"

### 3.3 Create Payment Links

1. Click **"Payment Links"** in Stripe Dashboard
2. Click **"New"**

**For Tier 2:**
- Select product: "d3kOS Tier 2 Premium"
- **Add Custom Field:**
  - Field name: "Installation ID"
  - Field type: Text
  - Required: Yes
  - Description: "Enter your 16-character d3kOS installation ID"
- Click "Create Link"
- **Copy the URL** (looks like: `https://buy.stripe.com/abc123def456`)

**For Tier 3:**
- Same process, select "d3kOS Tier 3 Enterprise" product
- **Copy the URL**

### 3.4 Add Payment Links to HTML

Find the subscription buttons (around line 439 and 461):

**Tier 2 button:**
```html
<!-- BEFORE: -->
<a href="#" class="btn btn-primary" style="width: 100%; text-align: center;">Subscribe Now</a>

<!-- AFTER: -->
<a href="https://buy.stripe.com/YOUR_TIER2_LINK" class="btn btn-primary" style="width: 100%; text-align: center;">Subscribe Now</a>
```

**Tier 3 button:**
```html
<!-- BEFORE: -->
<a href="#" class="btn btn-primary" style="width: 100%; text-align: center;">Subscribe Annually</a>

<!-- AFTER: -->
<a href="https://buy.stripe.com/YOUR_TIER3_LINK" class="btn btn-primary" style="width: 100%; text-align: center;">Subscribe Annually</a>
```

---

## STEP 4: ADD ECWID STORE FOR HARDWARE

### 4.1 Create Ecwid Account

1. Go to https://www.ecwid.com
2. Sign up for **FREE plan**
3. Complete store setup wizard

### 4.2 Add d3-k1 Hardware Product

**In Ecwid Dashboard:**

1. Click **"Catalog"** → **"Add Product"**
2. **Product Details:**
   - Name: "d3-k1 Complete Marine Electronics Kit"
   - Price: $299.00 (or your pricing)
   - Description: (copy from HTML or write detailed description)
   - Upload product images (if you have photos of the kit)
   - Weight: (for shipping calculation)
3. Click "Save"

### 4.3 Configure Shipping

1. **Settings** → **Shipping**
2. Add shipping zones (USA, Canada, etc.)
3. Set rates (flat rate or calculated)

### 4.4 Connect Payment Processors

1. **Settings** → **Payment**
2. Connect Stripe account (use same account from Step 3)
3. Optional: Connect PayPal

### 4.5 Get Embed Code

1. **Settings** → **Store Embed**
2. Click **"Get Code"**
3. Copy the JavaScript snippet (looks like):

```html
<script src="https://app.ecwid.com/script.js?12345678" type="text/javascript" charset="utf-8"></script>
<script type="text/javascript">
  xProductBrowser("categoriesPerRow=3","views=grid(20,3) list(60) table(60)","categoryView=grid","searchView=list","id=my-store-12345678");
</script>
```

### 4.6 Add Ecwid to HTML

**Option A: Replace "Pre-Order Now" button** (around line 554):

```html
<!-- BEFORE: -->
<a href="#" class="btn btn-primary" style="margin-top: 2rem;">Pre-Order Now</a>

<!-- AFTER: -->
<div id="my-store-12345678" style="margin-top: 2rem;"></div>
<script src="https://app.ecwid.com/script.js?12345678" type="text/javascript" charset="utf-8"></script>
<script type="text/javascript">
  Ecwid.init();
</script>
```

**Option B: Add dedicated store section** (after hardware section):

```html
<!-- Add after hardware section, before blog section -->
<section class="store-section" style="background: var(--color-dark); padding: 5rem 2rem;">
    <div class="section-container">
        <div class="section-header">
            <div class="section-label">Online Store</div>
            <h2 class="section-title">Shop Hardware & Accessories</h2>
        </div>
        <div id="my-store-12345678"></div>
        <script src="https://app.ecwid.com/script.js?12345678" type="text/javascript" charset="utf-8"></script>
        <script type="text/javascript">
          Ecwid.init();
        </script>
    </div>
</section>
```

---

## STEP 5: CUSTOMIZE COLORS (Optional)

The design uses your exact color scheme from the reference image:

```css
:root {
    --color-dark: #1a1a1a;      /* Main background */
    --color-darker: #0d0d0d;    /* Sections, header */
    --color-neon: #BFFF00;      /* Bright green accent */
    --color-white: #ffffff;     /* Text */
    --color-gray: #888888;      /* Secondary text */
}
```

**To adjust colors**, edit the `:root` section at the top of `<style>` (around line 17).

---

## STEP 6: UPLOAD TO HOSTPAPA VIA WINSCP

### 6.1 Prepare Files

**On your computer, organize:**
```
Desktop/AtMyBoat-Upload/
├── index.html (renamed from ATMYBOAT_MODERN_REDESIGN.html)
├── images/
│   ├── atmyboat-logo.png (your logo)
│   └── blog/ (optional blog images)
├── blog/ (your existing 50+ blog posts)
└── blog-posts.js (if using Option B for blog)
```

### 6.2 WinSCP Upload

1. **Open WinSCP**
2. **Connect to HostPapa:**
   - Protocol: SFTP or FTP
   - Host: (your HostPapa server)
   - Username: (your cPanel username)
   - Password: (your cPanel password)

3. **Navigate to `public_html/`**

4. **Backup current site** (if you have one):
   - Right-click `index.html` → Rename to `index.html.backup`

5. **Upload new files:**
   - Upload `index.html` (your new modern design)
   - Upload `images/` folder
   - Upload `blog/` folder (if applicable)
   - Upload `blog-posts.js` (if using dynamic blog)

6. **Set permissions:**
   - Right-click `index.html` → Properties → Permissions: 644
   - All folders: 755

### 6.3 Test

1. **Open browser**, go to https://atmyboat.com
2. **Clear cache:** Ctrl+Shift+R (hard refresh)
3. **Test:**
   - Logo appears
   - Blog posts display (50+)
   - Stripe payment links work (test mode)
   - Ecwid store loads
   - Mobile responsiveness (test on phone)

---

## STEP 7: INTEGRATE EXISTING BLOG CONTENT

### If your blog is WordPress:

**You have two options:**

**Option A: Keep WordPress, add landing page**
- Rename new design to `landing.html`
- Keep WordPress blog at `/blog/`
- Update navigation links to point to `/blog/`

**Option B: Export WordPress to static HTML**
1. Use plugin: "Simply Static" or "WP2Static"
2. Export all 50+ posts as HTML files
3. Upload to HostPapa `/blog/` folder
4. Update `blog-posts.js` with all titles/links

### If your blog is HTML files already:

1. **Organize blog files:**
   ```
   public_html/
   ├── index.html (new modern landing page)
   └── blog/
       ├── post-1.html
       ├── post-2.html
       ├── post-3.html
       └── ... (all 50+ posts)
   ```

2. **Update blog links** in `blog-posts.js` or HTML

3. **Consistent styling:** Add same dark theme CSS to each blog post template

---

## STEP 8: MOBILE MENU (For Small Screens)

Current design hides navigation on mobile. Add hamburger menu:

**Add before `</header>`:**

```html
<!-- Mobile Menu Button -->
<button class="mobile-menu-btn" onclick="toggleMobileMenu()">
    <i class="fas fa-bars"></i>
</button>
```

**Add CSS:**

```css
.mobile-menu-btn {
    display: none;
    background: none;
    border: none;
    color: var(--color-white);
    font-size: 1.5rem;
    cursor: pointer;
}

@media (max-width: 768px) {
    nav {
        display: none;
    }

    nav.mobile-active {
        display: flex;
        flex-direction: column;
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: var(--color-darker);
        padding: 1rem 2rem;
        gap: 1rem;
        box-shadow: 0 5px 20px rgba(0,0,0,0.5);
    }

    .mobile-menu-btn {
        display: block;
    }
}
```

**Add JavaScript before `</body>`:**

```html
<script>
function toggleMobileMenu() {
    const nav = document.querySelector('nav');
    nav.classList.toggle('mobile-active');
}
</script>
```

---

## STEP 9: SEO OPTIMIZATION

**Update `<head>` section:**

```html
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <!-- SEO Meta Tags -->
    <meta name="description" content="At My Boat - Smart marine electronics, DIY boating guides, and d3kOS open-source software. Featuring d3-k1 hardware kit for modern helm systems.">
    <meta name="keywords" content="marine electronics, boat helm, d3kOS, NMEA2000, fish detector, AI assistant, open source boating">
    <meta name="author" content="At My Boat">

    <!-- Open Graph (Social Media) -->
    <meta property="og:title" content="At My Boat | Smart Marine Electronics & Boating Blog">
    <meta property="og:description" content="Open-source marine electronics and DIY boating guides">
    <meta property="og:image" content="https://atmyboat.com/images/atmyboat-logo.png">
    <meta property="og:url" content="https://atmyboat.com">
    <meta property="og:type" content="website">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="At My Boat | Smart Marine Electronics">
    <meta name="twitter:description" content="Open-source marine electronics and DIY boating guides">
    <meta name="twitter:image" content="https://atmyboat.com/images/atmyboat-logo.png">

    <title>At My Boat | Smart Marine Electronics & Boating Blog</title>
    ...
</head>
```

---

## STEP 10: ANALYTICS (Optional)

**Add Google Analytics** before `</head>`:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

Replace `G-XXXXXXXXXX` with your Google Analytics ID.

---

## CHECKLIST BEFORE GOING LIVE

- [ ] Logo uploaded and displays correctly
- [ ] All 50+ blog posts linked and accessible
- [ ] Stripe payment links working (test in test mode first)
- [ ] Ecwid store displays and checkout works
- [ ] Mobile menu works on phone/tablet
- [ ] All links work (no broken links)
- [ ] Images load correctly
- [ ] Contact email updated (change `contact@atmyboat.com` to your real email)
- [ ] Social media links updated (footer)
- [ ] Google Analytics added (optional)
- [ ] Test on multiple browsers (Chrome, Firefox, Safari)
- [ ] Test on mobile devices
- [ ] Clear cache and test as visitor
- [ ] Backup old site before replacing

---

## MAINTENANCE

**To update blog:**
1. Add new post HTML file to `/blog/` folder
2. Update `blog-posts.js` with new entry
3. Upload via WinSCP

**To update pricing:**
1. Update Stripe product pricing
2. Update HTML text (but price pulls from Stripe)

**To add products:**
1. Add to Ecwid dashboard
2. Store auto-updates

---

## SUPPORT

**Questions about:**
- Design/HTML: Ask me (Claude)
- Stripe: https://stripe.com/docs
- Ecwid: https://support.ecwid.com
- HostPapa: Contact HostPapa support

---

**Ready to launch your modern atmyboat.com!** 🚤

Let me know when you want to proceed with any of these steps, and I'll help you implement them.
