# d3kOS Manual Management System - User Guide

**Version:** 1.0
**Last Updated:** February 13, 2026
**Status:** Production Ready ✅

---

## Table of Contents

1. [Overview](#overview)
2. [How the Manual System Works](#how-the-manual-system-works)
3. [Automatic Manual Search](#automatic-manual-search)
4. [Manual Upload Methods](#manual-upload-methods)
5. [Managing Your Manual Library](#managing-your-manual-library)
6. [Troubleshooting](#troubleshooting)

---

## Overview

The d3kOS Manual Management System automatically finds, downloads, and indexes manuals for your boat, engine, and marine electronics. After completing the onboarding wizard, the system searches the internet for relevant manuals and makes them available to the AI assistant.

### Three Ways to Add Manuals:

1. **Automatic Search** - System finds manuals after onboarding wizard
2. **Upload from Computer** - Upload PDF files you already have
3. **Download from Internet** - Save PDFs from websites and upload them

---

## How the Manual System Works

### After Onboarding Wizard Completion:

```
You complete wizard (Steps 1-20)
        ↓
System saves your configuration
        ↓
Redirects to "Searching for Manuals..." page
        ↓
Automatic search runs:
  1. CX5106 manual (always included from project files)
  2. Boat owner's manual (searches based on your answers)
  3. Engine service manual (searches based on your answers)
        ↓
Results displayed:
  "✓ Found" = Downloaded successfully
  "Not Found" = Use Upload Manual button as fallback
        ↓
Click "Go to Main Menu"
```

### What Gets Searched:

| Manual Type | Search Query | Example |
|-------------|--------------|---------|
| **Boat** | `[Manufacturer] [Model] [Year] owner's manual PDF` | `Sea Ray Sundancer 320 2018 owner's manual PDF` |
| **Engine** | `[Make] [Model] [Year] service manual PDF` | `Mercury Marine 5.0L MPI 2018 service manual PDF` |
| **CX5106** | Local project file (always included) | `CX5106_manual.pdf` (251 KB, 2 pages) |

---

## Automatic Manual Search

### How It Works:

1. **DuckDuckGo Search** - Searches public internet for PDF manuals
2. **Download & Validate** - Downloads first valid PDF found (checks file header)
3. **Store & Index** - Saves to `/opt/d3kos/data/manuals/` and adds to AI knowledge base

### Success Rate:

- **CX5106 Manual:** 100% (included in project)
- **Boat Manuals:** 60-80% (varies by manufacturer)
- **Engine Service Manuals:** 20-40% (often not publicly available)

### What If Manual Not Found?

Use the **"Upload Manual"** button on the main menu to add it yourself.

---

## Manual Upload Methods

### Method 1: Upload PDF from Your Computer

**When to use:** You have a PDF manual file on your computer

**Steps:**
1. Go to http://192.168.1.237/upload-manual.html
2. Select manual type:
   - Boat Manual
   - Engine Manual
   - Electronics Manual
   - Safety Equipment Manual
   - Regulations (NEW!)
3. Click "Choose PDF File"
4. Select your PDF file
5. Click "Upload and Process Manual"
6. ✅ Done! Manual is now in your library

**File Requirements:**
- Format: PDF only
- Max size: 50 MB
- Must be valid PDF (checked by system)

---

### Method 2: Download Manual from Internet

**When to use:** You found a manual online but system didn't find it automatically

#### Step-by-Step Instructions:

**On Windows Computer:**

1. **Find the Manual Online:**
   - Open browser (Chrome, Firefox, Edge)
   - Search Google for: `[Your Boat] owner's manual PDF`
   - Example: `Bayliner Element E16 owner's manual PDF`

2. **Check If It's a PDF:**
   - Look for results ending in `.pdf`
   - Or manufacturer support/download pages
   - Click the link to open the manual

3. **Download the PDF:**
   - **Method A: Direct PDF Link**
     - Right-click anywhere on the PDF
     - Select "Save As..." or "Download"
     - Choose location (e.g., Desktop or Downloads folder)
     - Click "Save"

   - **Method B: Download Button**
     - Look for "Download" button on webpage
     - Click it
     - PDF will save to your Downloads folder

4. **Upload to d3kOS:**
   - On Raspberry Pi touchscreen or via browser:
   - Go to http://192.168.1.237/upload-manual.html
   - Click "Choose PDF File"
   - Navigate to where you saved the PDF (Desktop/Downloads)
   - Select the file
   - Choose manual type (Boat/Engine/Electronics)
   - Click "Upload and Process Manual"

5. **Verify Upload:**
   - You should see: "✓ [Filename] uploaded successfully"
   - Go to http://192.168.1.237/manuals.html to see it in your library

---

**On Raspberry Pi (Direct Download):**

If you have keyboard/mouse connected to Pi:

1. **Open Browser on Pi:**
   - Chromium should already be open in kiosk mode
   - Press F11 to exit fullscreen (enables address bar)

2. **Search for Manual:**
   - Go to Google.com or manufacturer website
   - Search: `[Boat/Engine] manual PDF`

3. **Download PDF:**
   - Click PDF link
   - Right-click → "Save As"
   - Save to: `/home/d3kos/Downloads/`

4. **Upload to System:**
   - Go to http://192.168.1.237/upload-manual.html
   - Choose the downloaded PDF
   - Select manual type
   - Click "Upload and Process Manual"

5. **Return to Kiosk Mode:**
   - Press F11 to restore fullscreen

---

**On Mobile Device (Tablet/Phone):**

1. **Find Manual:**
   - Open browser on phone/tablet
   - Search for manual
   - Open PDF link

2. **Download to Device:**
   - Tap "Download" button
   - PDF saves to device storage

3. **Transfer to d3kOS:**
   - **Option A: USB Transfer**
     - Connect phone to computer with USB
     - Copy PDF to computer
     - Then upload from computer (see Method 1 above)

   - **Option B: Cloud Transfer**
     - Upload PDF to cloud storage (Google Drive, Dropbox, etc.)
     - Access cloud on computer
     - Download PDF
     - Upload to d3kOS (see Method 1 above)

   - **Option C: Direct Browser Upload**
     - Connect phone to same WiFi as d3kOS
     - Open http://192.168.1.237/upload-manual.html in phone browser
     - Choose PDF from phone storage
     - Upload directly

---

### Common Manual Sources:

| Type | Good Sources |
|------|--------------|
| **Boat Manuals** | Manufacturer websites, BoatUS, MarineEngine.com |
| **Engine Manuals** | Mercury Marine, Yamaha, Suzuki support pages |
| **Electronics** | Garmin, Raymarine, Simrad, Maretron support sites |
| **Generic Marine** | USCG, ABYC, NMMA safety guides |

**Popular Sites:**
- Manufacturer support pages (best source)
- MarineEngine.com (large manual database)
- boats.net (parts diagrams and manuals)
- Crowley Marine manuals repository
- iBoats.com forums (user-shared manuals)

---

## Managing Your Manual Library

### View All Manuals:

**URL:** http://192.168.1.237/manuals.html

**Shows:**
- List of all uploaded manuals
- File name, size, upload date
- Total count

**Actions:**
- **Delete** - Remove manual from library (also removes from AI knowledge base)
- **Upload New Manual** - Link to upload page

---

### Delete a Manual:

1. Go to http://192.168.1.237/manuals.html
2. Find the manual you want to delete
3. Click "🗑️ Delete" button
4. Confirm deletion
5. ✅ Manual removed from filesystem AND AI knowledge base

**Warning:** Deletion is permanent - you'll need to re-upload or re-search to get it back.

---

### Check What's Indexed:

**AI Knowledge Base Location:** `/opt/d3kos/config/skills.md`

**To view:**
```bash
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237
tail -30 /opt/d3kos/config/skills.md
```

**You'll see entries like:**
```markdown
## Manual: Bayliner_Element_E16_2015_owners_manual.pdf
Type: boat
Location: /opt/d3kos/data/manuals/Bayliner_Element_E16_2015_owners_manual.pdf
Added: 2026-02-13 15:47:12
```

---

## Troubleshooting

### "Manual Not Found" During Auto-Search

**Why it happens:**
- Manual not publicly available online
- Manufacturer requires login/registration
- Manual behind paywall
- Search query didn't match available results

**Solution:**
1. Find manual yourself on manufacturer website
2. Download PDF to your computer
3. Upload via http://192.168.1.237/upload-manual.html

---

### Upload Fails: "Not a Valid PDF"

**Possible causes:**
- File is actually HTML page (saved wrong)
- File is corrupted
- File is image (JPEG/PNG) not PDF

**Solution:**
1. Open file on computer - does it open as PDF?
2. Re-download from source
3. If it's images, convert to PDF first:
   - Windows: Print to PDF
   - Mac: Preview → Export as PDF
   - Online: Use smallpdf.com or pdf2go.com

---

### Upload Fails: "File Too Large"

**Limit:** 50 MB per file

**Solution:**
1. Compress PDF:
   - Online: smallpdf.com/compress-pdf
   - Adobe Acrobat: Save As → Reduced Size PDF
2. Split large manual into sections
3. Upload most important sections only

---

### Manual Uploaded But AI Doesn't Know About It

**Reason:** Processing may not have completed

**Check:**
```bash
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237
grep "Manual:" /opt/d3kos/config/skills.md | tail -5
```

**If not listed:** Manual didn't get indexed

**Solution:**
1. Delete manual from library
2. Re-upload
3. Check logs: `journalctl -u d3kos-manuals-api -n 50`

---

### Can't Access Upload Page

**URL not loading:** http://192.168.1.237/upload-manual.html

**Check:**
1. Are you on same network as Pi?
2. Ping test: `ping 192.168.1.237`
3. Check nginx: `ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237 "systemctl status nginx"`
4. Check file exists: `ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237 "ls -l /var/www/html/upload-manual.html"`

---

### Manuals API Not Working

**Symptom:** Auto-search hangs or fails

**Check service status:**
```bash
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237
systemctl status d3kos-manuals-api
```

**If not running:**
```bash
sudo systemctl start d3kos-manuals-api
```

**Check logs:**
```bash
journalctl -u d3kos-manuals-api -n 50 --no-pager
```

---

## System Architecture Reference

### File Locations:

| Component | Path | Purpose |
|-----------|------|---------|
| **Downloaded Manuals** | `/opt/d3kos/data/manuals/` | PDF storage |
| **Reference Docs** | `/opt/d3kos/reference/` | Markdown guides |
| **AI Knowledge Base** | `/opt/d3kos/config/skills.md` | Manual index |
| **Auto-search Script** | `/opt/d3kos/services/manuals/auto-search.py` | Search logic |
| **API Server** | `/opt/d3kos/services/manuals/manuals_api.py` | Flask API |

### Network Services:

| Service | Port | Endpoint | Purpose |
|---------|------|----------|---------|
| **Manuals API** | 8083 | `/manuals/*` | Manual management |
| **Nginx Web** | 80 | `/*` | Web pages |
| **Upload API** | 8081 | `/upload/*` | File uploads |
| **AI API** | 8080 | `/ai/*` | AI assistant |

### System Services:

```bash
# Check status
systemctl status d3kos-manuals-api

# Restart service
sudo systemctl restart d3kos-manuals-api

# View logs
journalctl -u d3kos-manuals-api -f
```

---

## Tips & Best Practices

### For Best Search Results:

1. **Be specific in wizard:** Use exact manufacturer names
   - ✅ "Mercury Marine" not "Mercury"
   - ✅ "Sea Ray" not "Searay"

2. **Include model year:** Helps find correct manual version

3. **Use full model names:** "Sundancer 320" not just "320"

### For Manual Organization:

1. **Name your custom manuals clearly:**
   - Good: `Bayliner_Element_E16_2015_Owners.pdf`
   - Bad: `manual.pdf` or `download (1).pdf`

2. **Choose correct manual type:** Helps AI categorize information

3. **Delete old versions:** Keep only current year/version

### For Better AI Assistance:

1. **Upload complete manuals:** More content = better answers

2. **Include all systems:** Electrical, plumbing, engine, etc.

3. **Add troubleshooting sections:** AI can reference these

---

## Quick Reference Card

### Manual System URLs:

```
Main Menu:        http://192.168.1.237/
Upload Manual:    http://192.168.1.237/upload-manual.html
Manage Library:   http://192.168.1.237/manuals.html
Onboarding:       http://192.168.1.237/onboarding.html
```

### Upload Steps (Quick):

1. Find PDF online or on computer
2. Go to upload page
3. Choose file + select type
4. Click upload
5. ✅ Done!

### Common Commands:

```bash
# SSH to Pi
ssh -i ~/.ssh/d3kos_key d3kos@192.168.1.237

# List manuals
ls -lh /opt/d3kos/data/manuals/

# Check service
systemctl status d3kos-manuals-api

# View recent logs
journalctl -u d3kos-manuals-api -n 20
```

---

## Support & Documentation

**Primary Documentation:**
- `/home/boatiq/Helm-OS/doc/MANUAL_AUTOMATION_2026-02-13.md` - Implementation details
- `/home/boatiq/Helm-OS/doc/ONBOARDING_FIX_2026-02-13.md` - Wizard setup
- `~/.claude/projects/-home-boatiq/memory/MEMORY.md` - System memory

**GitHub Repository:**
- https://github.com/SkipperDon/d3kOS

**System Access:**
- IP: 192.168.1.237
- User: d3kos
- SSH: `~/.ssh/d3kos_key`

---

**Last Updated:** February 13, 2026
**Author:** Claude Sonnet 4.5
**Version:** 1.0
