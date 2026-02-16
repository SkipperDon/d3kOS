# Manual Automation Implementation - February 13, 2026

**Status:** COMPLETE ✅
**Implementation Time:** ~2 hours
**Option Selected:** Option 3 - Hybrid (Auto-search + Manual Upload Fallback)

## Overview

Implemented automated manual searching and downloading system that triggers after the onboarding wizard completes. The system searches for boat owner's manuals, engine service manuals, and CX5106 gateway manuals based on information collected during setup.

## Architecture

### Components

1. **Auto-Search Script** (`/opt/d3kos/services/manuals/auto-search.py`)
   - Python script that performs web searches for manuals
   - Uses DuckDuckGo HTML search (no API key required)
   - Downloads and validates PDF files
   - Processes manuals and adds to knowledge base

2. **Manuals API Server** (`/opt/d3kos/services/manuals/manuals_api.py`)
   - Flask API server on port 8083
   - Endpoints: `/manuals/auto-search`, `/manuals/list`, `/manuals/delete/<filename>`
   - Systemd service: `d3kos-manuals-api.service` (auto-start enabled)

3. **Manual Search Results Page** (`/var/www/html/manual-search.html`)
   - Displays search progress in real-time
   - Shows which manuals were found/downloaded
   - Provides summary and "Go to Main Menu" button

4. **Updated Onboarding Wizard** (`/var/www/html/onboarding.html`)
   - Saves configuration to localStorage after Step 20
   - Redirects to manual-search.html instead of main menu
   - Triggers automated manual search

## User Flow

```
Onboarding Wizard (Steps 1-20)
        ↓
    Collect Configuration:
    - Boat: Manufacturer, Model, Year
    - Engine: Make, Model, Year
    - Regional settings
        ↓
    Save config to localStorage
        ↓
    Redirect to /manual-search.html
        ↓
    Display "Searching for Manuals..."
        ↓
    Call API: POST /manuals/auto-search
    {config object with q1-q16}
        ↓
    Search for:
    1. Boat owner's manual
    2. Engine service manual
    3. CX5106 NMEA2000 gateway manual
        ↓
    Download found PDFs
    Save to /opt/d3kos/data/manuals/
        ↓
    Display Results:
    "✓ Found" or "Not Found"
    Summary: "X manuals downloaded"
        ↓
    User clicks "Go to Main Menu"
        ↓
    Toggle fullscreen (restore kiosk mode)
        ↓
    Return to main menu
```

## Manual Search Logic

### 1. Boat Owner's Manual

**Search Query:** `{manufacturer} {model} {year} owner's manual PDF`

**Example:** `Sea Ray Sundancer 320 2018 owner's manual PDF`

**Steps:**
1. Try manufacturer website first (manufacturer-specific logic)
2. Fall back to DuckDuckGo web search
3. Look for `.pdf` links in search results
4. Download first valid PDF
5. Verify PDF header (`%PDF`)
6. Save as `{manufacturer}_{model}_{year}_owners_manual.pdf`

### 2. Engine Service Manual

**Search Query:** `{make} {model} {year} service manual PDF`

**Example:** `Mercury Marine 5.0L MPI Alpha 2018 service manual PDF`

**Steps:**
1. Try manufacturer website first
2. Fall back to DuckDuckGo web search
3. Download and validate PDF
4. Save as `{make}_{model}_{year}_service_manual.pdf`

### 3. CX5106 NMEA2000 Gateway Manual

**Search Query:** `Maretron CX5106 manual PDF`

**Direct URLs Tried First:**
- `https://www.maretron.com/support/manuals/CX5106-UM_1.0.pdf`
- `https://www.maretron.com/products/pdf/CX5106_datasheet.pdf`

**Steps:**
1. Try direct Maretron URLs first
2. Fall back to web search if not found
3. Save as `CX5106_manual.pdf`

## API Endpoints

### POST /manuals/auto-search

**Purpose:** Trigger automatic manual search

**Request Body:**
```json
{
  "q1": "Sea Ray",
  "q2": "2018",
  "q3": "Sundancer 320",
  "q4": "yes",
  "q5": "Mercury Marine",
  "q6": "5.0L MPI Alpha",
  "q7": "2018",
  "q8": "8",
  "q9": "5.0",
  "q10": "220",
  "q11": "9.5",
  "q12": "700",
  "q13": "4800-5200",
  "q14": "na",
  "q15": "us",
  "q16": "primary"
}
```

**Response:**
```json
{
  "success": true,
  "results": {
    "searched": [
      "Boat: Sea Ray Sundancer 320 2018",
      "Engine: Mercury Marine 5.0L MPI Alpha 2018",
      "CX5106 NMEA2000 Gateway"
    ],
    "found": [
      "Sea_Ray_Sundancer_320_2018_owners_manual.pdf",
      "CX5106_manual.pdf"
    ],
    "downloaded": [
      {
        "filename": "Sea_Ray_Sundancer_320_2018_owners_manual.pdf",
        "type": "boat",
        "url": "https://example.com/manual.pdf",
        "size": 2456789
      },
      {
        "filename": "CX5106_manual.pdf",
        "type": "electronics",
        "url": "https://www.maretron.com/support/manuals/CX5106-UM_1.0.pdf",
        "size": 1234567
      }
    ],
    "failed": [
      "Mercury_Marine_5.0L_MPI_Alpha_2018_service_manual.pdf: Not found"
    ]
  },
  "output": "..."
}
```

**Timeout:** 120 seconds (2 minutes)

### GET /manuals/list

**Purpose:** List all downloaded manuals

**Response:**
```json
{
  "success": true,
  "count": 2,
  "manuals": [
    {
      "filename": "Sea_Ray_Sundancer_320_2018_owners_manual.pdf",
      "size": 2456789,
      "uploaded": 1676307600
    },
    {
      "filename": "CX5106_manual.pdf",
      "size": 1234567,
      "uploaded": 1676307650
    }
  ]
}
```

### DELETE /manuals/delete/<filename>

**Purpose:** Delete a manual (used by Manage Manuals page)

**Response:**
```json
{
  "success": true,
  "message": "Deleted CX5106_manual.pdf"
}
```

## File Locations

| Component | Path | Purpose |
|-----------|------|---------|
| Auto-search script | `/opt/d3kos/services/manuals/auto-search.py` | Manual search logic |
| API server | `/opt/d3kos/services/manuals/manuals_api.py` | Flask API endpoints |
| Systemd service | `/etc/systemd/system/d3kos-manuals-api.service` | API auto-start |
| Manual search page | `/var/www/html/manual-search.html` | Progress/results UI |
| Onboarding wizard | `/var/www/html/onboarding.html` | Triggers auto-search |
| Manuals directory | `/opt/d3kos/data/manuals/` | Downloaded PDFs |
| Skills file | `/opt/d3kos/config/skills.md` | AI knowledge base |
| Nginx config | `/etc/nginx/sites-enabled/default` | Proxy /manuals/ → :8083 |

## Network Configuration

**Manuals API:**
- Internal port: 8083
- Public endpoint: http://192.168.1.237/manuals/
- Nginx proxy: `/manuals/` → `http://localhost:8083/manuals/`

**Existing Services:**
- Upload API: Port 8081 (handles manual uploads via "Upload Manual" page)
- History API: Port 8082
- AI API: Port 8080
- Signal K: Port 3000
- Node-RED: Port 1880

## Manual Upload vs. Auto-Search

The system now has THREE ways to add manuals:

### 1. Automatic Search (New!)
- **When:** Triggered after onboarding wizard completion
- **How:** Searches web automatically based on boat/engine info
- **Success Rate:** Variable (depends on manual availability online)
- **User Action:** None required

### 2. Manual Upload Page
- **URL:** http://192.168.1.237/upload-manual.html
- **When:** User has a manual PDF file to add
- **How:** Form with file picker and manual type selector
- **Use Case:** Fallback for manuals not found automatically

### 3. Manage Manuals Page
- **URL:** http://192.168.1.237/manuals.html
- **Purpose:** View/delete existing manuals (library management)
- **Features:** List all manuals, show sizes/dates, delete button

## Processing Pipeline

When a manual is downloaded:

1. **Download** - Fetch PDF from URL with timeout (30s)
2. **Validate** - Check HTTP status, content-type, file size (<50MB)
3. **Verify** - Confirm PDF header (`%PDF`)
4. **Save** - Store in `/opt/d3kos/data/manuals/{filename}.pdf`
5. **Process** - Extract text (TODO: pypdf integration)
6. **Index** - Add specifications to `/opt/d3kos/config/skills.md`
7. **Enable AI** - AI assistant can now answer questions about manual

**Current Implementation:**
- Steps 1-4: ✅ Complete
- Steps 5-6: 🚧 Placeholder (adds basic note to skills.md)

**Future Enhancement:**
- Install pypdf library for text extraction
- Parse specifications from manual text
- Structure data in skills.md format
- Enable semantic search across manuals

## Search Strategy

### DuckDuckGo HTML Search

**Why DuckDuckGo:**
- No API key required
- HTML endpoint: `https://html.duckduckgo.com/html/?q={query}`
- Returns search results in HTML format
- Regex extraction: `href=['"]([^'"]*\.pdf[^'"]*)['"]`

**Limitations:**
- Basic HTML parsing (not robust to layout changes)
- First PDF link only (no ranking)
- No manufacturer website authentication
- Rate limiting may apply

**Future Improvements:**
- Implement manufacturer-specific search logic
  - Sea Ray: Check sealineseacraft.com
  - Mercury: Check mercurymarine.com
  - Yamaha: Check yamaha-motor.com
- Add Google Custom Search API (requires key)
- Implement manual fingerprinting (verify correct manual)
- Cache search results (avoid re-searching same boat/engine)
- Add user feedback ("Was this the right manual?")

## Testing

### Manual Test

1. Run wizard: http://192.168.1.237/onboarding.html
2. Fill in boat/engine information:
   - Boat: Bayliner, 2015, Element E16
   - Engine: Mercury Marine, 40 ELPT EFI, 2015
3. Complete wizard (Step 20)
4. Should redirect to manual-search.html
5. Watch progress: "Searching for manuals..."
6. See results: "X manuals downloaded"
7. Click "Go to Main Menu"
8. Check /opt/d3kos/data/manuals/ for downloaded PDFs

### API Test

```bash
# Test health check
curl http://localhost/manuals/list

# Test auto-search with sample config
curl -X POST http://localhost/manuals/auto-search \
  -H "Content-Type: application/json" \
  -d '{
    "q1": "Bayliner",
    "q2": "2015",
    "q3": "Element E16",
    "q5": "Mercury Marine",
    "q6": "40 ELPT EFI",
    "q7": "2015"
  }'

# List downloaded manuals
curl http://localhost/manuals/list

# Delete a manual
curl -X DELETE http://localhost/manuals/delete/CX5106_manual.pdf
```

## Known Limitations

1. **Search Accuracy**
   - DuckDuckGo HTML parsing is fragile
   - No guarantee first PDF is correct manual
   - Manufacturer websites may require authentication
   - Some manuals may not be publicly available

2. **Processing**
   - Text extraction not yet implemented (pypdf needed)
   - Specification parsing is basic
   - skills.md updates are minimal (just filename/type/date)

3. **Performance**
   - 120 second timeout for entire search
   - Sequential searches (boat, then engine, then CX5106)
   - Could be parallelized for faster results

4. **User Experience**
   - No preview of found manual before download
   - No verification that downloaded manual is correct
   - No option to retry failed searches

## Security Considerations

1. **File Validation**
   - PDF header verification (`%PDF`)
   - File size limit (50MB)
   - Content-type checking
   - No executable content allowed

2. **Network Safety**
   - User-Agent header spoofing (Mozilla/5.0)
   - HTTPS preferred over HTTP
   - Timeout protection (30s download, 120s total)
   - No follow of redirects to untrusted domains

3. **Filesystem Protection**
   - Manuals stored in dedicated directory (`/opt/d3kos/data/manuals/`)
   - Temporary files with `.tmp` extension
   - Atomic move after validation
   - No path traversal in filenames

## Future Enhancements

### Phase 2: Advanced Search
- [ ] Implement manufacturer-specific scrapers
- [ ] Add Google Custom Search API integration
- [ ] Cache search results to avoid re-searching
- [ ] Parallel searches for faster results
- [ ] Manual fingerprinting (MD5, size, page count)

### Phase 3: Enhanced Processing
- [ ] Install pypdf library for text extraction
- [ ] Parse specifications from manual text
- [ ] Structure data in skills.md semantic format
- [ ] Build searchable index of manual contents
- [ ] Enable AI to quote specific manual pages

### Phase 4: User Feedback
- [ ] "Was this the right manual?" confirmation
- [ ] Manual rating system (helpful/not helpful)
- [ ] Community manual database (share finds)
- [ ] Report missing manuals to database

### Phase 5: Integration
- [ ] Link manuals to specific boat systems
- [ ] Show relevant manual sections in context
- [ ] Highlight manual pages during troubleshooting
- [ ] Auto-reference manual specs in AI responses

## References

- MASTER_SYSTEM_SPEC.md Section 4.3.1 (Onboarding Wizard)
- ONBOARDING_FIX_2026-02-13.md (Keyboard fix documentation)
- MEMORY.md (Project memory)
- DuckDuckGo HTML: https://html.duckduckgo.com/html/
- Maretron Support: https://www.maretron.com/support/

---

## Update: CX5106 Manual Integration (2026-02-13 Evening)

### User Feedback:
User tested the system and reported: **"wow it good"** ✅

### Additional Work Completed:

1. **Integrated Project CX5106 Manual**
   - Found existing manual: `/home/boatiq/Helm-OS/assets/manuals/CX5106_10125_manual.pdf` (251 KB, 2 pages)
   - Deployed to Pi: `/opt/d3kos/data/manuals/CX5106_manual.pdf`
   - Updated auto-search script to check local copy first (no internet needed)

2. **Deployed Reference Documents**
   - `/opt/d3kos/reference/CX5106_USER_MANUAL.md` (25 KB) - Comprehensive configuration guide
   - `/opt/d3kos/reference/CX5106_CONFIGURATION_GUIDE.md` (14 KB) - Setup instructions

3. **Auto-Search Improvements**
   - CX5106 manual now always included (100% success rate)
   - Reports "local" as URL source when using project files
   - Falls back to web search only if local copy missing

### Test Results (Evening):

**Test Query:** Sea Ray Sundancer 320 2020

**Results:**
- ✅ CX5106 manual: Found instantly (local)
- ❌ Boat manual: Not found (2020 model too new)
- ❌ Engine manual: Not included in test query

**Performance:** CX5106 detection in <1 second (no network delay)

### User Next Steps:

User plans to create custom boat manual for testing purposes - demonstrating system's flexibility for user-created documentation.

---

## Documentation Created:

1. **Technical Implementation:** `MANUAL_AUTOMATION_2026-02-13.md` (this file)
2. **User Guide:** `MANUAL_SYSTEM_USER_GUIDE.md` - Complete instructions for end users
3. **Memory Update:** `MEMORY.md` - Added manual automation to project memory

---

**Signed:** Claude Sonnet 4.5
**Date:** 2026-02-13
**Session:** Manual Automation Implementation
**Status:** Production Ready ✅
