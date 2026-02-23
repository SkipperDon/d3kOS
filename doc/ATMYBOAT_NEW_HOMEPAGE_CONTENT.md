# AtMyBoat.com - New Homepage Content
## WordPress Block-by-Block Guide (Mobile-Responsive)

**Theme:** Twenty Twenty (already responsive)
**Page Title:** Home
**Template:** Full Width (no sidebar)

---

## SECTION 1: HERO - Welcome Message

**Block Type:** Cover Block (full-width background)
**Background:** Image or solid color (Twenty Twenty default blue)
**Height:** 400px (desktop), auto-adjust mobile

**Content:**
```
[Heading - H1, Centered, White text]
Welcome Aboard, Come Sail with Our Time

[Paragraph - Centered, White text, 18px]
At My Boat is more than a blog—it's a growing community for boaters who want smarter
systems, safer cruising, and a few laughs along the way. Dive into approachable guides,
family stories, and the tools that make boating simpler and more enjoyable.

[Button - Centered, Primary color]
Text: "Explore the Blog"
Link: /blog (or your blog page URL)
```

**Mobile:** Text auto-scales, button stacks below text, full-width

---

## SECTION 2: LATEST BLOG POSTS ⭐

**Block Type:** Latest Posts Block (WordPress core)
**Settings:**
- Display: 3 posts
- Show featured image: YES
- Show excerpt: YES (100 words)
- Show date: YES
- Show author: Optional
- Layout: Grid (3 columns desktop, 1 column mobile)

**Heading above block:**
```
[Heading - H2, Centered]
Latest from the Blog
```

**Mobile:** Automatically stacks into single column

---

## SECTION 3: SUBSCRIBE TO BLOG

**Block Type:** MailPoet Form Block
**Heading:**
```
[Heading - H3, Centered]
Never Miss a Post
```

**Form Fields:**
- Email address (required)
- First Name (optional)
- Subscribe button: "Subscribe to Blog Updates"

**Note:** If MailPoet block not available, use HTML block with this code:
```html
<div style="max-width: 500px; margin: 2rem auto; text-align: center; padding: 2rem; background: #f5f5f5; border-radius: 8px;">
  <h3>Never Miss a Post</h3>
  <p>Get new posts delivered to your inbox</p>
  [mailpoet_form id="1"]
</div>
```

**Mobile:** Form scales to 100% width, fields stack vertically

---

## SECTION 4: WHAT IS d3kOS?

**Block Type:** Columns Block (2 columns desktop, stack on mobile)

**Left Column:**
```
[Heading - H2]
What is d3kOS?

[Paragraph]
d3kOS (Deck OS) is an open-source marine helm control system that brings modern
technology to your boat. Think of it as a "smart home" for your vessel—centralized
monitoring, voice commands, automated logging, and intelligent alerts—all through
a sunlight-readable touchscreen.

Built on Raspberry Pi 4, d3kOS gives boat owners professional-grade engine monitoring,
navigation assistance, and AI-powered voice control—without the enterprise price tag.

Perfect for recreational boaters, liveaboards, and marine electronics enthusiasts who
want more control, better data, and smarter automation.
```

**Right Column:**
```
[Image]
Add: Photo of d3kOS dashboard or boat helm setup
Alt text: "d3kOS marine helm control system"

[Paragraph - Small, Italics]
Open-source, customizable, and designed for real-world boating conditions.
```

**Mobile:** Columns stack (image below text)

---

## SECTION 5: SUBSCRIPTION TIERS

**Block Type:** Table Block (4 columns × 6 rows) OR Custom HTML for better mobile

**Heading:**
```
[Heading - H2, Centered]
Choose Your Tier
```

**Subheading:**
```
[Paragraph - Centered]
d3kOS is free and open-source. Upgrade for premium features and support.
```

**Table Content:**

| Feature | Tier 0 (Free) | Tier 1 (Free) | Tier 2 ($9.99/mo) | Tier 3 ($99.99/yr) |
|---------|---------------|---------------|-------------------|-------------------|
| **Core System** | ✓ Dashboard, engine monitoring, boat log | ✓ All Tier 0 features | ✓ All Tier 1 features | ✓ All Tier 2 features |
| **Mobile App** | ❌ | ✓ iOS/Android app, remote monitoring | ✓ Mobile app included | ✓ Mobile app included |
| **AI Voice Assistant** | ❌ | ❌ | ✓ Hands-free voice control ("Helm", "Advisor", "Counsel") | ✓ Voice assistant included |
| **Marine Vision Camera** | ❌ | ❌ | ✓ 4K camera, fish detection, alerts | ✓ Camera system included |
| **Cloud Sync** | ❌ | ❌ | ❌ | ✓ Multi-boat sync, cloud backup |
| **Support** | Community (GitHub) | Community + Email | Priority email support | Priority + Phone support |
| **Download** | [Free Download →] | [Free Download →] | [Subscribe →] | [Subscribe →] |

**Mobile Optimization:** Use Cards instead of table:

**Alternative Mobile-Friendly Layout (Recommended):**

Use **Group Blocks** (one per tier) instead of table:

```
[Group Block - Tier 0]
Background: Light gray
Padding: 2rem
Border radius: 8px

Tier 0 - Free & Open Source
✓ Dashboard & engine monitoring
✓ Real-time NMEA2000 data
✓ Automated boat log
✓ GPS navigation
✓ Community support

[Button]
Download from GitHub

---

[Group Block - Tier 1]
Background: Light blue

Tier 1 - Mobile Integration
FREE (requires mobile app)
✓ All Tier 0 features
✓ iOS/Android mobile app
✓ Remote monitoring
✓ Cloud data export
✓ Email support

[Button]
Download from GitHub

---

[Group Block - Tier 2]
Background: Light green

Tier 2 - Premium
$9.99/month
✓ All Tier 1 features
✓ AI Voice Assistant
✓ Marine Vision Camera (4K)
✓ Priority email support
✓ Advanced analytics

[Button]
Subscribe Now

---

[Group Block - Tier 3]
Background: Light gold

Tier 3 - Enterprise
$99.99/year (Save 17%)
✓ All Tier 2 features
✓ Multi-boat management
✓ Cloud sync & backup
✓ Priority phone support
✓ Early access to features

[Button]
Subscribe Now
```

**Mobile:** Each tier card stacks vertically, full-width

---

## SECTION 6: DOWNLOAD d3kOS

**Block Type:** Buttons Block (centered)

**Content:**
```
[Heading - H2, Centered]
Download d3kOS

[Paragraph - Centered]
Free and open-source. Install on your own Raspberry Pi 4 hardware.

[Button - Large, Primary color]
Text: "Download from GitHub"
Link: https://github.com/[yourusername]/d3kos
Style: Filled, rounded corners

[Button - Large, Secondary color]
Text: "Read Installation Guide"
Link: /blog/d3kos-installation-guide (your blog post)
Style: Outline

[Paragraph - Small, Centered]
Current Version: v0.9.1.2 (Beta) | Release Date: Feb 2026
```

**Mobile:** Buttons stack vertically, full-width

---

## SECTION 7: HARDWARE PARTNERS WANTED

**Block Type:** Cover Block (with background color or image)
**Background:** Light blue or boat/water image
**Padding:** 3rem

**Content:**
```
[Heading - H2, Centered]
Hardware Partners Wanted 🤝

[Paragraph - Centered, 18px]
We're looking for manufacturing partners to assemble and distribute d3-k1 hardware kits.
The d3-k1 is a complete marine electronics package: Raspberry Pi 4, CX5106 NMEA2000 gateway,
Reolink 4K camera, 10.1" touchscreen, GPS, and all cables.

If you're a marine electronics manufacturer, distributor, or fabrication shop interested
in bringing smart marine technology to boaters worldwide, let's talk.

[Button - Centered]
Text: "Contact Us About Partnership"
Link: /contact or mailto:your@email.com
```

**Mobile:** Text and button auto-adjust, full-width

---

## SECTION 8: FOOTER

**Block Type:** Group Block (dark background)
**Background:** #1a1a1a (dark)
**Text color:** White
**Padding:** 2rem

**Content:**
```
[Columns - 3 columns desktop, stack on mobile]

Column 1:
[Heading - H4, White]
At My Boat

[Paragraph - Small, White]
Smarter boating through approachable
technology and plain-English guides.

Column 2:
[Heading - H4, White]
Quick Links

[List - White]
• Blog
• About
• Contact
• Privacy Policy

Column 3:
[Heading - H4, White]
Connect

[Social Media Icons]
• Email newsletter
• GitHub
• YouTube (if applicable)

---

[Separator]

[Paragraph - Centered, Small, White]
Copyright © 2026 AtMyBoat.com | All Rights Reserved
```

**Mobile:** All columns stack vertically

---

## MOBILE OPTIMIZATION CHECKLIST

✅ **Typography:**
- H1: Auto-scales 36px → 28px on mobile
- H2: Auto-scales 32px → 24px on mobile
- Body: 18px → 16px on mobile
- Line height: 1.6 (readable on small screens)

✅ **Images:**
- Set max-width: 100%
- Height: auto
- Lazy loading enabled

✅ **Buttons:**
- Min height: 48px (thumb-friendly)
- Full-width on mobile (< 600px)
- Adequate spacing between buttons

✅ **Spacing:**
- Section padding: 4rem desktop → 2rem mobile
- Margin between sections: 3rem desktop → 1.5rem mobile

✅ **Columns:**
- 2-3 columns desktop → 1 column mobile (automatic in Twenty Twenty)

✅ **Navigation:**
- Hamburger menu on mobile (Twenty Twenty default)
- Sticky header optional

✅ **Forms:**
- Input fields: 100% width on mobile
- Label above input (not side-by-side)
- Large submit button (full-width)

---

## WORDPRESS SETUP STEPS

### Step 1: Create Page
1. Go to **Pages → Add New**
2. Title: "Home"
3. Use **Full Width** template (no sidebar)

### Step 2: Add Blocks
Follow the sections above, adding blocks in order:
1. Cover block (Hero)
2. Latest Posts block
3. MailPoet form or HTML block
4. Columns block (d3kOS explanation)
5. Group blocks (Tier cards)
6. Buttons block (Download)
7. Cover block (Hardware partners)
8. Group block (Footer)

### Step 3: Set as Homepage
1. **Publish** the page
2. Go to **Settings → Reading**
3. Set "Your homepage displays" to **A static page**
4. Choose "Home" as homepage
5. Save changes

### Step 4: Test Mobile
1. Open http://atmyboat.local/ on desktop
2. Resize browser window to mobile size (< 600px)
3. Check: Text readable, buttons full-width, columns stack, images scale
4. Or use browser DevTools → Toggle device toolbar

---

## PHOTOS TO ADD

Recommended images to enhance the page:

1. **Hero background:** Boat on water at sunset/sunrise
2. **d3kOS dashboard:** Screenshot of actual interface
3. **d3-k1 hardware:** Photo of Raspberry Pi + components
4. **Blog post featured images:** Automatically pulled from posts
5. **Hardware partnership section:** Manufacturing/workshop photo

Upload via **Media → Add New** in WordPress admin.

---

## CUSTOMIZATION NOTES

**Twenty Twenty Theme Colors (Keep these):**
- Primary: #CD2653 (red/pink)
- Secondary: #6D6D6D (gray)
- Background: #FFFFFF (white)
- Text: #000000 (black)
- Accent: Links automatically use theme colors

**No custom CSS needed** - Twenty Twenty handles all responsive behavior automatically.

---

## NEXT STEPS AFTER CREATING PAGE

1. ✅ Create page with blocks
2. ✅ Set as homepage
3. ✅ Test on mobile
4. ⏳ Add photos
5. ⏳ Configure MailPoet subscription list
6. ⏳ Update GitHub link (when repo is public)
7. ⏳ Create contact form for hardware partnerships
8. ⏳ Test all buttons and links
9. ⏳ Export page (WordPress XML) when ready
10. ⏳ Deploy to live site (atmyboat.com)

---

**This page will be fully responsive on mobile without any additional work!**
