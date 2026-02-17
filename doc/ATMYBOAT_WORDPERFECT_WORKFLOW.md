# At My Boat Landing Page - WordPerfect Implementation Workflow
## How to Use WordPerfect Instead of HTML

**Date:** February 16, 2026
**Status:** ⏳ NOT READY TO IMPLEMENT (Stored for future use)

---

## 📋 What You Have

Three files created for future use:
1. `ATMYBOAT_LANDING_PAGE.html` - Complete HTML page
2. `ATMYBOAT_LANDING_PAGE_CONTENT.md` - Copy-paste content
3. `ATMYBOAT_IMPLEMENTATION_GUIDE.md` - Implementation instructions

**Current Status:** Files are ready but NOT being implemented yet. User will review and decide when to proceed.

---

## 📝 WordPerfect Workflow (When Ready)

### Understanding the Process

**Problem:** You use WordPerfect, not HTML editors. HostPapa requires HTML/web format.

**Solution:** Two options when you're ready to implement:

---

## Option 1: WordPerfect → HTML Export (Recommended)

### Step 1: Create Document in WordPerfect

1. Open WordPerfect
2. Create new document
3. Copy content from `ATMYBOAT_LANDING_PAGE_CONTENT.md`
4. Format in WordPerfect:
   - **Headings:** Use Heading 1, Heading 2 styles
   - **Body text:** Normal paragraph style
   - **Lists:** Use bullet/numbered list formatting
   - **Bold/Italic:** Format as needed

### Step 2: Add Images in WordPerfect

1. Insert → Graphics → From File
2. Add images:
   - Logo (top)
   - d3kOS screenshots
   - Hardware photos
   - Blog thumbnails

### Step 3: Export to HTML

**WordPerfect → HTML Export:**

1. **File** → **Publish to** → **HTML**

   OR

   **File** → **Save As** → Choose file type: **"HTML Document (*.html)"**

2. **Export Settings:**
   - Layout: Choose "Single page" (not frames)
   - Graphics: Check "Include graphics in export"
   - Fonts: Use "Web-safe fonts" option
   - CSS: Check "Use CSS for formatting"

3. **Save location:**
   - Save to folder you can easily find
   - Name: `atmyboat-landing.html`

4. **Review exported files:**
   - Main HTML file: `atmyboat-landing.html`
   - Images folder: `atmyboat-landing_files/` (contains images)

### Step 4: Upload to HostPapa

1. Log into HostPapa cPanel
2. Go to File Manager
3. Navigate to `public_html`
4. Upload:
   - `atmyboat-landing.html`
   - Upload entire `atmyboat-landing_files/` folder (contains images)
5. Rename `atmyboat-landing.html` to `index.html` (for homepage)
6. Test: Visit `atmyboat.com`

### Step 5: Fix Formatting Issues (if needed)

WordPerfect HTML export sometimes needs cleanup:

**Common issues:**
- Extra spacing → Edit HTML in HostPapa file editor, remove `<br>` tags
- Fonts don't match → May need to adjust CSS
- Images broken → Check image file paths

**To fix:**
- Use HostPapa's HTML editor to make small adjustments
- OR re-export from WordPerfect with different settings
- OR use our pre-made HTML file and just replace text content

---

## Option 2: Use Our HTML + Copy Content from WordPerfect (Easier)

### Step 1: Use Pre-Made HTML Template

1. Upload our `ATMYBOAT_LANDING_PAGE.html` to HostPapa
2. Open in HostPapa HTML/Code editor

### Step 2: Replace Placeholder Content

1. Open WordPerfect document with your customized content
2. Copy section-by-section from WordPerfect
3. Paste into HTML file (replace placeholder text)

**Example:**
- HTML has: "Come Sail with Our Time"
- If you changed wording in WordPerfect: Copy new text → Paste into HTML

### Step 3: Add Images

1. Upload images to HostPapa `/images/` folder
2. Edit HTML to point to images:
   ```html
   <img src="/images/your-photo.jpg" alt="Description">
   ```

### Step 4: Test and Publish

1. Preview in browser
2. Make adjustments as needed
3. Publish when satisfied

---

## Option 3: Use HostPapa Website Builder (No WordPerfect Needed)

**Easiest option if you don't want to deal with HTML:**

### Step 1: Open Website Builder

1. Log into HostPapa
2. Find "Website Builder" or "Site Builder" tool
3. Create new page or edit existing

### Step 2: Copy Content from WordPerfect

1. Open WordPerfect document
2. Copy one section at a time
3. Paste into Website Builder text blocks

### Step 3: Format in Website Builder

- Add headings, images, buttons
- Use drag-and-drop interface
- No HTML knowledge required

### Step 4: Publish

- Preview
- Publish when ready

---

## 🎯 Recommended Approach When You're Ready

**For you (WordPerfect user), I recommend:**

### **Hybrid Approach:**

1. **Use our pre-made HTML file** (already formatted, mobile-responsive)
2. **Open WordPerfect** to draft/revise any content changes you want
3. **Copy revised text from WordPerfect** → Paste into HTML (in HostPapa editor)
4. **Add your images** via HostPapa file manager
5. **Preview and publish**

**Why this works:**
- ✅ You can write/edit in WordPerfect (your preferred tool)
- ✅ You get professional HTML/CSS (our template)
- ✅ You don't need to learn HTML
- ✅ Simple copy-paste updates
- ✅ Mobile-responsive design guaranteed

---

## 📁 File Organization for WordPerfect Users

### Create These Folders:

**On Your Computer:**
```
Documents/
  AtMyBoat/
    Content/
      landing-page.wpd (WordPerfect master document)
      blog-sections.wpd (blog content)
      product-descriptions.wpd (d3kOS/d3-k1 content)
    Images/
      logo.png
      d3kos-dashboard.jpg
      hardware-kit.jpg
      blog-thumbnails/
    Website/
      ATMYBOAT_LANDING_PAGE.html (from me)
      ATMYBOAT_LANDING_PAGE_CONTENT.md (reference)
      ATMYBOAT_IMPLEMENTATION_GUIDE.md (instructions)
```

**Workflow:**
1. **Edit content** → WordPerfect files in `Content/`
2. **Store images** → `Images/` folder
3. **When ready to publish** → Copy from WordPerfect → Paste into HTML → Upload to HostPapa

---

## 📝 WordPerfect Template Structure

When you're ready to create the WordPerfect document:

### Document Outline:

```
═══════════════════════════════════════
AT MY BOAT - LANDING PAGE MASTER
═══════════════════════════════════════

[SECTION 1: HEADER]
Logo: At My Boat
Tagline: Smarter Boating, Simpler Systems

Navigation:
• Blog
• d3kOS
• Hardware
• BoatIQ Solutions
• About

───────────────────────────────────────

[SECTION 2: HERO]

Come Sail with Our Time

At My Boat is more than a blog—it's a growing
community for boaters who want smarter systems,
safer cruising, and a few laughs along the way...

[Insert your custom text here]

───────────────────────────────────────

[SECTION 3: d3kOS PRODUCT]

Introducing d3kOS: Your Boat's Smart Brain

[Product description...]

TIER 0: Base Opensource (FREE)
• Feature 1
• Feature 2
...

TIER 1: Mobile App (FREE)
...

[Continue for all sections]

───────────────────────────────────────
```

**Save as:** `landing-page-master.wpd`

**Use for:**
- Drafting content changes
- Spell-checking
- Formatting review
- Version control (save dated copies)

---

## 🔄 Update Workflow (When Live)

Once landing page is live on HostPapa:

### To Make Content Changes:

1. **Edit in WordPerfect:**
   - Open `landing-page-master.wpd`
   - Make changes
   - Save with date: `landing-page-2026-03-15.wpd`

2. **Copy to HTML:**
   - Log into HostPapa
   - Open HTML editor
   - Find section to update
   - Copy from WordPerfect → Paste into HTML
   - Save

3. **Preview:**
   - View changes in browser
   - Check mobile view
   - Verify formatting looks good

4. **Publish:**
   - If good → Leave live
   - If issues → Revert or fix

### To Add Images:

1. **Prepare in WordPerfect:**
   - Note where image should go
   - Add placeholder text: `[INSERT: Hardware photo here]`

2. **Upload to HostPapa:**
   - File Manager → `/images/`
   - Upload image file

3. **Edit HTML:**
   - Find placeholder location
   - Add image code:
     ```html
     <img src="/images/hardware-photo.jpg" alt="d3-k1 Hardware">
     ```

4. **Save and test**

---

## ⚠️ Important Notes for WordPerfect Users

### What WordPerfect Does Well:
- ✅ Writing and editing content
- ✅ Spell-checking
- ✅ Formatting review
- ✅ Version control (save dated copies)
- ✅ Print layouts for documentation

### What WordPerfect Doesn't Do Well:
- ❌ Web-responsive design (mobile/tablet/desktop)
- ❌ Interactive elements (buttons, forms)
- ❌ Modern CSS styling
- ❌ Clean HTML export (often messy code)

### Best Practice:
- **Use WordPerfect:** Content creation and editing
- **Use HTML template:** Web formatting and responsive design
- **Copy-paste:** Bridge between the two

---

## 🆘 If You Get Stuck

### HostPapa Support Can Help With:
- Uploading files
- Editing HTML in their editor
- Configuring website builder
- Domain settings
- Email setup

### HostPapa CANNOT Help With:
- WordPerfect software issues
- Content writing/editing
- Graphic design
- Photography

### For WordPerfect Issues:
- Corel WordPerfect support
- WordPerfect user forums
- Local computer help

### For Content/Design Questions:
- Come back to Claude Code for help
- Hire freelance web designer (if needed)

---

## 📅 Timeline Suggestion (When You're Ready)

### Week 1: Content Review
- [ ] Review all three files I created
- [ ] Note any content changes you want to make
- [ ] Decide which sections to keep/modify/remove
- [ ] Draft changes in WordPerfect

### Week 2: Image Collection
- [ ] Take/find photos of d3kOS system
- [ ] Take/find photos of d3-k1 hardware
- [ ] Select blog category thumbnails
- [ ] Get logo in high-resolution format
- [ ] Organize in `/Images/` folder

### Week 3: Implementation
- [ ] Upload HTML file to HostPapa (test first on subdomain)
- [ ] Copy any content changes from WordPerfect
- [ ] Upload images
- [ ] Configure button links
- [ ] Test on desktop, tablet, mobile

### Week 4: Review & Launch
- [ ] Share test link with friends/community
- [ ] Collect feedback
- [ ] Make final adjustments
- [ ] Move to main domain (atmyboat.com)
- [ ] Announce on social media

**Or:** Take your time! No rush. Files are ready when you are.

---

## 💾 Backup Strategy

### Keep Copies Of:

**WordPerfect Documents:**
- Master content file
- Dated versions (monthly or when you make big changes)
- Backup to cloud (Google Drive, Dropbox, OneDrive)

**HTML Files:**
- Original template (from me)
- Modified versions (before each major update)
- Download from HostPapa periodically

**Images:**
- Original high-resolution versions (master copies)
- Web-optimized versions (compressed for website)
- Backup to external drive or cloud

**Why:** If something breaks on website, you can always restore from backup.

---

## ✅ Status: Stored for Future Use

**Current Status:** ⏳ NOT READY TO IMPLEMENT

**Files Created and Stored:**
1. ✅ `ATMYBOAT_LANDING_PAGE.html` - Complete website
2. ✅ `ATMYBOAT_LANDING_PAGE_CONTENT.md` - Content reference
3. ✅ `ATMYBOAT_IMPLEMENTATION_GUIDE.md` - Implementation guide
4. ✅ `ATMYBOAT_WORDPERFECT_WORKFLOW.md` - This file (WordPerfect workflow)

**Saved In Memory:** ✅ Yes (recorded in MEMORY.md as pending implementation)

**Next Steps (When Ready):**
1. Review files
2. Draft content changes in WordPerfect
3. Collect/prepare images
4. Decide on implementation method (Option 1, 2, or 3 above)
5. Test on HostPapa subdomain or staging site
6. Launch when satisfied

**No Pressure:** Take your time. Files will be here when you're ready!

---

**Last Updated:** February 16, 2026
**File Location:** `/home/boatiq/Helm-OS/doc/ATMYBOAT_WORDPERFECT_WORKFLOW.md`
