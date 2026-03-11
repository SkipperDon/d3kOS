# SKILLS.MD SPECIFICATION
## d3kOS AI Context Management System

**Version**: 1.0
**Date**: February 12, 2026
**Status**: APPROVED
**Related Documents**: CLAUDE.md v2.5, MASTER_SYSTEM_SPEC.md v2.3

---

## TABLE OF CONTENTS

1. [Overview](#overview)
2. [Purpose & Objectives](#purpose--objectives)
3. [File Format & Structure](#file-format--structure)
4. [Content Sections](#content-sections)
5. [Automatic Population](#automatic-population)
6. [Context Usage by AI Assistants](#context-usage-by-ai-assistants)
7. [Size Management & Optimization](#size-management--optimization)
8. [Learning & Memory Integration](#learning--memory-integration)
9. [Implementation Guide](#implementation-guide)
10. [API Reference](#api-reference)
11. [Best Practices](#best-practices)

---

## 1. OVERVIEW

### 1.1 What is skills.md?

`skills.md` is a unified, Markdown-formatted knowledge base file that provides context to both online and onboard AI assistants in d3kOS. It contains:

- Boat and engine specifications
- Owner's manuals (text extracted from PDFs)
- Regional boating regulations
- Marine best practices
- Conversation history (important Q&A)
- Maintenance logs

### 1.2 Key Features

- **Unified Context**: Single source of truth for both AI assistants
- **Markdown Format**: Human-readable, easy to edit, version-controllable
- **Auto-Generated**: Populated automatically during onboarding
- **Learning-Enabled**: Grows over time with important conversations
- **Size-Managed**: Automatic pruning to maintain < 10MB target
- **Offline-First**: Works completely offline after initial download

### 1.3 Location

**Primary File**: `/opt/d3kos/config/skills.md`
**Backup Directory**: `/opt/d3kos/backups/skills/`
**Archive Directory**: `/opt/d3kos/data/archived-conversations/`

---

## 2. PURPOSE & OBJECTIVES

### 2.1 Problem Statement

Without a structured knowledge base:
- AI assistants lack boat-specific context
- Users must manually provide specs in every query
- No memory of previous conversations
- Manuals and regulations not easily accessible
- Each AI query starts from zero knowledge

### 2.2 Solution

skills.md provides:
- **Persistent Context**: AI knows boat specs, engine details, regulations
- **Conversation Memory**: Important Q&A stored for future reference
- **Intelligent Responses**: AI can reference manuals and best practices
- **Learning Over Time**: System becomes smarter with each interaction

### 2.3 Design Goals

1. **Simplicity**: Markdown format, human-editable
2. **Portability**: Single file, easy to backup/restore
3. **Scalability**: Size management prevents bloat
4. **Flexibility**: Sections can be added/removed as needed
5. **Performance**: Fast to parse, efficient for AI context loading

---

## 3. FILE FORMAT & STRUCTURE

### 3.1 Markdown Format

skills.md uses GitHub-Flavored Markdown (GFM) with:
- Headers (##, ###, ####)
- Bold/italic text
- Lists (bulleted, numbered)
- Code blocks (optional, for technical specs)
- Links (for external references)

### 3.2 Standard Structure

```markdown
# d3kOS Skills Database

## System Information
[Installation metadata]

## Boat Information
[Make, model, year, specifications]

## Engine Information
[Manufacturer, model, specs, normal parameters]

## Engine Manual (Text Extracted)
[Full engine manual text]

## Boat Owner's Manual (Text Extracted)
[Full boat manual text]

## Regional Regulations
[Country, state/province, local regulations]

## Best Practices (BoatUS.org)
[Marine safety and operational best practices]

## International Sailing
[Regulations for countries you plan to visit]

## Conversation History (Recent)
[Last 50 important Q&A pairs]

## Maintenance Log
[Service history, upcoming maintenance]

## Notes & Customizations
[User-added notes and information]
```

### 3.3 Section Hierarchy

- **Level 1 Header (#)**: File title only
- **Level 2 Headers (##)**: Major sections
- **Level 3 Headers (###)**: Subsections
- **Level 4 Headers (####)**: Detail sections

### 3.4 Encoding & Character Set

- **Encoding**: UTF-8
- **Line Endings**: Unix (LF)
- **Maximum Line Length**: None (wrap as needed)
- **Special Characters**: Allowed (nautical symbols, degrees, etc.)

---

## 4. CONTENT SECTIONS

### 4.1 System Information

**Purpose**: Installation metadata for identification and troubleshooting

**Fields**:
```markdown
## System Information
- Installation ID: XXXX-XXXX-XXXX
- Installation Date: YYYY-MM-DD
- Last Updated: YYYY-MM-DD HH:MM:SS
- Skills Version: X.X
- d3kOS Version: X.X.X
- Tier: 0 | 1 | 2 | 3
```

**Auto-Generated**: Yes (during onboarding)
**User Editable**: No (managed by system)

### 4.2 Boat Information

**Purpose**: Basic boat identity and specifications

**Fields**:
```markdown
## Boat Information
- Make: [Manufacturer name]
- Model: [Model name/number]
- Year: [Build year]
- Length: [Feet/meters]
- Beam: [Feet/meters]
- Draft: [Feet/meters]
- Displacement: [Pounds/kilograms]
- Hull Type: [Planing, Displacement, Semi-displacement]
- Hull Material: [Fiberglass, Aluminum, Wood, etc.]
- Hull ID: [HIN - Hull Identification Number]
- Registration: [State/country registration number]
- Home Port: [Marina, city, state]
- Owner: [Name from onboarding]
```

**Auto-Generated**: Partially (from onboarding)
**User Editable**: Yes (can be manually updated)

### 4.3 Engine Information

**Purpose**: Engine specifications and normal operating parameters

**Fields**:
```markdown
## Engine Information

### Basic Specifications
- Manufacturer: [Mercury, Volvo Penta, Yanmar, etc.]
- Model: [Model number]
- Year: [Manufacturing year]
- Serial Number: [If available]
- Type: [Inboard, Outboard, Sterndrive]
- Fuel Type: [Gasoline, Diesel]
- Cylinders: [3, 4, 6, 8]
- Displacement: [Liters or Cubic Inches]
- Compression Ratio: [X.X:1]
- Stroke: [4-stroke, 2-stroke]
- Horsepower: [Rated HP]
- Max RPM: [WOT RPM]
- Gear Ratio: [X.XX:1]
- Cooling: [Raw water, Fresh water, Keel cooled]
- Induction: [Naturally Aspirated, Turbocharged, Supercharged]

### Normal Operating Parameters
- Idle RPM: [XXX-XXX RPM]
- Cruise RPM: [XXXX-XXXX RPM]
- WOT RPM: [XXXX-XXXX RPM]
- Oil Pressure (Idle): [XX PSI / X.X bar]
- Oil Pressure (Cruise): [XX PSI / X.X bar]
- Coolant Temperature (Normal): [XXX-XXX°F / XX-XX°C]
- Voltage (Charging): [XX.X-XX.X V]
- Fuel Consumption (Cruise): [X.X GPH / X.X LPH]

### Sensor Configuration (CX5106)
- DIP Switch Configuration: [Row 1: XXXXXXXX, Row 2: XX]
- Tank Sensor Standard: [American 240-33Ω / European 0-190Ω]
- Engine Position: [Single/Port/Starboard]
```

**Auto-Generated**: Yes (from onboarding)
**User Editable**: Yes (can add notes, adjust parameters)

### 4.4 Engine Manual (Text Extracted)

**Purpose**: Full engine manual for reference by AI

**Format**:
```markdown
## Engine Manual (Text Extracted)

**Source**: [Manual name, version, year]
**Downloaded**: [YYYY-MM-DD]
**Pages**: [Total page count]
**File Size**: [XX KB]

### Table of Contents
[Extracted TOC if available]

### Introduction
[Manual introduction text]

### Specifications
[Technical specifications from manual]

### Operation
[Operating procedures]

### Maintenance
[Maintenance schedules and procedures]

### Troubleshooting
[Troubleshooting guides and charts]

### Parts & Service
[Parts diagrams, service information]

[Additional sections as needed...]
```

**Auto-Generated**: Yes (downloaded and extracted during onboarding if internet available)
**User Editable**: No (but can be replaced with updated manual)
**Size Limit**: ~50KB per manual (compressed text only, not full PDF)

### 4.5 Boat Owner's Manual (Text Extracted)

**Purpose**: Full boat owner's manual for reference

**Format**: Same as Engine Manual structure
**Auto-Generated**: Yes (if available online)
**User Editable**: No (but can be replaced)
**Size Limit**: ~50KB

### 4.6 Regional Regulations

**Purpose**: Local and federal boating regulations

**Format**:
```markdown
## Regional Regulations

### Country: [United States, Canada, UK, etc.]
- Coast Guard District: [X]
- Nearest CG Station: [Location]

### State/Province: [Florida, Ontario, etc.]
- State Boating Authority: [Agency name]
- State Boating Hotline: [Phone number]

### Federal Regulations (US Example)
#### Required Safety Equipment
- Life jackets: [Requirements]
- Fire extinguishers: [Requirements]
- Visual distress signals: [Requirements]
- Sound signaling devices: [Requirements]
- Navigation lights: [Requirements]

#### Navigation Rules (COLREGS)
- Right of way rules
- Sound signals
- Light configurations
- Speed restrictions

#### Radio Protocols
- VHF Channel usage
- Distress procedures (Mayday, Pan-Pan, Securité)
- DSC registration

### State/Provincial Regulations
[State-specific requirements]

### Local Ordinances
- No-wake zones
- Speed limits
- Anchoring restrictions
- Marine protected areas
- Manatee zones (Florida example)
```

**Auto-Generated**: Yes (fetched from USCG, Transport Canada, RYA, etc.)
**User Editable**: Yes (can add local knowledge)
**Update Frequency**: Check for updates annually

### 4.7 Best Practices (BoatUS.org)

**Purpose**: Marine safety and operational best practices

**Format**:
```markdown
## Best Practices (BoatUS.org)

### Pre-Departure Checklist
- [ ] Check weather forecast
- [ ] Inspect engine and bilge
- [ ] Test navigation lights
- [ ] Check fuel level (1/3 out, 1/3 back, 1/3 reserve)
- [ ] Verify safety equipment
- [ ] File float plan
[Full checklist...]

### Float Plan Procedures
[How to create and file a float plan]

### Fuel Management
[1/3 rule, fuel range calculations]

### Storm Preparation
[Securing boat, emergency procedures]

### Docking & Anchoring
[Best practices for docking and anchoring]

### Navigation Safety
[Safe navigation practices]

### Emergency Procedures
[Man overboard, fire, flooding, etc.]
```

**Auto-Generated**: Yes (scraped from BoatUS.org)
**User Editable**: Yes (can add personal practices)

### 4.8 International Sailing

**Purpose**: Regulations for international cruising

**Format**:
```markdown
## International Sailing

### Countries You Plan to Visit

#### Bahamas
- Entry requirements: [Documents needed]
- Customs procedures: [Step-by-step]
- Immigration: [Process]
- Permits required: [Cruising permit, fishing license]
- Navigation restrictions: [Areas to avoid, speed limits]
- Emergency contacts: [Coast Guard, police, hospitals]
- VHF channels: [Working channels]

#### [Additional countries as needed]
```

**Auto-Generated**: No (user must specify destination countries)
**User Editable**: Yes (add/remove countries as travel plans change)

### 4.9 Conversation History (Recent)

**Purpose**: Store important Q&A for future reference

**Format**:
```markdown
## Conversation History (Recent)

### Last Updated: [YYYY-MM-DD HH:MM:SS]

**Q**: What's the normal operating temperature for my engine?
**A**: Your Mercury 8.2L normally runs at 160-180°F when fully warmed up. Your current reading of 178°F is within normal range.
**Date**: 2026-02-10 14:30:00
**Source**: Online AI (Perplexity)
**Important**: Yes

---

**Q**: What documents do I need to enter Bahamian waters?
**A**: You need: (1) Vessel documentation or state registration, (2) Passports for all aboard, (3) Bahamas cruising permit ($150), (4) Bahamas fishing license if fishing ($20). You can clear customs at any official port of entry.
**Date**: 2026-02-08 09:15:00
**Source**: Onboard AI (Phi-2)
**Important**: Yes

---

[Additional Q&A entries up to 50 most recent]
```

**Auto-Generated**: Yes (automatically added when AI marks answer as important)
**User Editable**: Yes (can manually add/remove entries)
**Size Management**: Keep last 50 entries, archive older ones

### 4.10 Maintenance Log

**Purpose**: Track service history and upcoming maintenance

**Format**:
```markdown
## Maintenance Log

### Service History

#### 2026-01-15 - Oil Change
- Engine Hours: 245
- Oil Type: Mercury 25W-40 Synthetic
- Oil Filter: Mercury 35-879885K01
- Performed By: Marina Service Center
- Cost: $180
- Notes: No issues, engine running well

#### 2025-10-20 - Impeller Replacement
- Engine Hours: 180
- Impeller: CEF 500108
- Performed By: Self
- Cost: $45 (parts only)
- Notes: Old impeller showed wear, replaced preventatively

[Additional service records...]

### Upcoming Maintenance

#### Next Oil Change
- Due At: 300 engine hours (currently at 278)
- Estimated Date: 2026-05-01
- Parts Needed: Oil (5 qts), filter
- Estimated Cost: $180

#### Next Impeller Inspection
- Due At: 400 engine hours
- Estimated Date: 2026-08-15

[Additional upcoming items...]

### Manufacturer Recommendations
[Service intervals from engine manual]
```

**Auto-Generated**: Partially (intervals from manual)
**User Editable**: Yes (user logs service)
**Integration**: Can link to external maintenance tracking apps

### 4.11 Notes & Customizations

**Purpose**: User-added information and boat-specific knowledge

**Format**:
```markdown
## Notes & Customizations

### Custom Modifications
[User describes any modifications made to boat]

### Local Knowledge
[Favorite anchorages, marinas, restaurants]

### Quirks & Tips
[Boat-specific quirks and workarounds]

### Contact Information
- Home Marina: [Name, phone, address]
- Mechanic: [Name, phone]
- Electronics Technician: [Name, phone]
- Insurance: [Company, policy #, phone]
- Towing Service: [BoatUS, SeaTow, etc.]

### Additional Information
[Anything else user wants AI to know]
```

**Auto-Generated**: No (user-created)
**User Editable**: Yes (completely user-controlled)

---

## 5. AUTOMATIC POPULATION

### 5.1 When Skills.md is Generated

skills.md is automatically generated during:

1. **Initial Onboarding** (Steps 19-20):
   - If internet available: Download manuals and regulations
   - If offline: Create template with placeholders

2. **Re-Running Onboarding** (with internet):
   - Offer to update/replace existing content
   - Prompt: "Download new manuals? This will replace existing content."

3. **Manual Trigger** (from Settings menu):
   - User can manually trigger document retrieval
   - Useful if initial onboarding was offline

### 5.2 Document Retrieval Process

**Step-by-Step Process During Onboarding:**

```javascript
async function populateSkillsFile(boatInfo, engineInfo, location) {
  showProgressModal("Building Your AI Knowledge Base");

  // Initialize skills.md
  let skills = generateSkillsHeader(boatInfo, engineInfo);

  // Step 1: Boat Manual (20-30%)
  updateProgress("Searching for boat manual...", 20);
  try {
    const boatManual = await searchManual(
      boatInfo.make,
      boatInfo.model,
      boatInfo.year,
      'boat'
    );
    if (boatManual) {
      skills += formatManualSection('Boat Owner\'s Manual', boatManual);
      updateProgress("✓ Boat manual found and extracted", 30);
    } else {
      updateProgress("⚠ Boat manual not found (can be added manually later)", 30);
      skills += manualPlaceholder('Boat Owner\'s Manual');
    }
  } catch (error) {
    updateProgress("⚠ Error retrieving boat manual", 30);
    skills += manualPlaceholder('Boat Owner\'s Manual');
  }

  // Step 2: Engine Manual (30-50%)
  updateProgress("Searching for engine manual...", 40);
  try {
    const engineManual = await searchManual(
      engineInfo.manufacturer,
      engineInfo.model,
      engineInfo.year,
      'engine'
    );
    if (engineManual) {
      skills += formatManualSection('Engine Manual', engineManual);
      updateProgress("✓ Engine manual found and extracted", 50);
    } else {
      updateProgress("⚠ Engine manual not found", 50);
      skills += manualPlaceholder('Engine Manual');
    }
  } catch (error) {
    updateProgress("⚠ Error retrieving engine manual", 50);
    skills += manualPlaceholder('Engine Manual');
  }

  // Step 3: Regulations (50-70%)
  updateProgress("Fetching regional regulations...", 60);
  try {
    const regulations = await fetchRegulations(
      location.country,
      location.state
    );
    skills += formatRegulationsSection(regulations);
    updateProgress("✓ Regulations loaded", 70);
  } catch (error) {
    updateProgress("⚠ Error fetching regulations", 70);
    skills += regulationsPlaceholder();
  }

  // Step 4: Best Practices (70-90%)
  updateProgress("Fetching marine best practices...", 80);
  try {
    const bestPractices = await fetchBoatUSPractices();
    skills += formatBestPracticesSection(bestPractices);
    updateProgress("✓ Best practices loaded", 90);
  } catch (error) {
    updateProgress("⚠ Error fetching best practices", 90);
    skills += bestPracticesPlaceholder();
  }

  // Step 5: Save skills.md (90-100%)
  updateProgress("Saving AI knowledge base...", 95);
  fs.writeFileSync('/opt/d3kos/config/skills.md', skills);
  updateProgress("✓ AI knowledge base created successfully!", 100);

  // Log statistics
  logSkillsStats(skills);
}
```

### 5.3 Document Sources

#### 5.3.1 manualslib.com

**Search Strategy**:
```javascript
async function searchManualsLib(make, model, year, type) {
  const query = `${make} ${model} ${year} ${type}`;
  const searchUrl = `https://www.manualslib.com/search.html?q=${encodeURIComponent(query)}`;

  const response = await fetch(searchUrl);
  const html = await response.text();

  // Parse HTML for PDF links
  const $ = cheerio.load(html);
  const results = [];

  $('a[href*="/manual/"]').each((i, elem) => {
    const href = $(elem).attr('href');
    const text = $(elem).text();
    results.push({ url: `https://www.manualslib.com${href}`, title: text });
  });

  if (results.length === 0) return null;

  // Download first result
  const manualPage = await fetch(results[0].url);
  const manualHtml = await manualPage.text();

  // Extract PDF download link
  const $manual = cheerio.load(manualHtml);
  const pdfLink = $manual('a[href*=".pdf"]').first().attr('href');

  if (!pdfLink) return null;

  // Download and extract PDF
  const pdfBuffer = await downloadFile(pdfLink);
  const text = await extractPDFText(pdfBuffer);

  return text;
}
```

**Fallback**: If manualslib.com fails, try manufacturer website

#### 5.3.2 BoatUS.org

**Fetch Best Practices**:
```javascript
async function fetchBoatUSPractices() {
  const topics = [
    { slug: 'pre-departure', title: 'Pre-Departure Checklist' },
    { slug: 'float-plan', title: 'Float Plan' },
    { slug: 'fuel-management', title: 'Fuel Management' },
    { slug: 'anchoring', title: 'Anchoring' },
    { slug: 'storm-prep', title: 'Storm Preparation' },
    { slug: 'docking', title: 'Docking Techniques' }
  ];

  let practices = '';

  for (const topic of topics) {
    try {
      const url = `https://www.boatus.org/study-guide/${topic.slug}`;
      const response = await fetch(url);
      const html = await response.text();

      // Extract main content
      const $ = cheerio.load(html);
      const content = $('.main-content').text()
        .replace(/\s+/g, ' ')
        .trim();

      practices += `### ${topic.title}\n${content}\n\n`;
    } catch (error) {
      console.log(`Failed to fetch ${topic.slug}`);
    }
  }

  return practices;
}
```

#### 5.3.3 USCG Regulations (US)

**Fetch Federal Regulations**:
```javascript
async function fetchUSCGRegulations(state) {
  const baseUrl = 'https://www.uscgboating.org';

  // Fetch federal requirements
  const federalUrl = `${baseUrl}/regulations/summary.php`;
  const response = await fetch(federalUrl);
  const html = await response.text();

  const $ = cheerio.load(html);
  const regulations = {
    federal: $('.regulations-content').text(),
    state: ''
  };

  // Fetch state-specific (if available)
  if (state) {
    const stateUrl = `${baseUrl}/regulations/state.php?state=${state}`;
    const stateResponse = await fetch(stateUrl);
    const stateHtml = await stateResponse.text();
    regulations.state = cheerio.load(stateHtml)('.state-regs').text();
  }

  return regulations;
}
```

#### 5.3.4 Transport Canada (Canada)

**Fetch Canadian Regulations**:
```javascript
async function fetchTransportCanadaRegulations(province) {
  const url = 'https://tc.canada.ca/en/marine-transportation/marine-safety/boating-safety';
  const response = await fetch(url);
  const html = await response.text();

  const $ = cheerio.load(html);
  const regulations = $('.regulations-section').text();

  return regulations;
}
```

### 5.4 PDF Processing

**Extract Text from PDF**:
```javascript
const pdfParse = require('pdf-parse');

async function extractPDFText(pdfBuffer) {
  try {
    const data = await pdfParse(pdfBuffer, {
      max: 0  // Parse all pages
    });

    let text = data.text
      .replace(/\s+/g, ' ')                 // Collapse whitespace
      .replace(/Page \d+ of \d+/gi, '')     // Remove page numbers
      .replace(/\f/g, '\n\n')               // Form feed to paragraph break
      .replace(/\u0000/g, '')               // Remove null characters
      .trim();

    // Compress if too large
    if (text.length > 50000) {
      text = compressManualText(text);
    }

    return text;
  } catch (error) {
    console.error('PDF extraction failed:', error);
    return null;
  }
}

function compressManualText(text) {
  // Keep: TOC, specs, operation, maintenance, troubleshooting
  // Remove: Warranty, disclaimers, part lists (unless important)

  const sections = [
    'table of contents',
    'specifications',
    'operation',
    'maintenance',
    'troubleshooting'
  ];

  let compressed = '';
  sections.forEach(section => {
    const regex = new RegExp(
      `(${section}[\\s\\S]*?)(?=(${sections.join('|')})|$)`,
      'i'
    );
    const match = text.match(regex);
    if (match) {
      compressed += match[0] + '\n\n';
    }
  });

  // Still too large? Truncate
  if (compressed.length > 50000) {
    compressed = compressed.substring(0, 50000) +
      '\n\n[Manual truncated for space. Full manual available online.]';
  }

  return compressed;
}
```

---

## 6. CONTEXT USAGE BY AI ASSISTANTS

### 6.1 How AI Uses skills.md

**Loading Context**:
```javascript
async function loadContextForAI(question) {
  // Load skills.md
  const skills = fs.readFileSync('/opt/d3kos/config/skills.md', 'utf-8');

  // Load current boat data
  const currentData = await getRecentEngineData();

  // Load onboarding info
  const onboarding = JSON.parse(
    fs.readFileSync('/opt/d3kos/config/onboarding.json')
  );

  return {
    skills,
    currentData: {
      rpm: currentData.rpm,
      oilPressure: currentData.oilPressure,
      temperature: currentData.temperature,
      fuelLevel: currentData.fuelLevel,
      voltage: currentData.voltage,
      timestamp: currentData.timestamp
    },
    onboarding
  };
}
```

### 6.2 Online AI (Perplexity)

**Full Context** (128K token window):
```javascript
async function queryPerplexity(question, context) {
  const systemPrompt = `You are a marine assistant for d3kOS.

Current boat data (real-time):
- RPM: ${context.currentData.rpm}
- Oil Pressure: ${context.currentData.oilPressure} PSI
- Temperature: ${context.currentData.temperature}°F
- Fuel Level: ${context.currentData.fuelLevel}%
- Voltage: ${context.currentData.voltage}V
- Time: ${context.currentData.timestamp}

Boat knowledge base:
${context.skills}

Please provide concise, accurate answers based on this boat's specific configuration and current status.`;

  const response = await fetch('https://api.perplexity.ai/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${config.api_key}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model: 'llama-3.1-sonar-small-128k-online',
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: question }
      ]
    })
  });

  const data = await response.json();
  return data.choices[0].message.content;
}
```

**Benefits**:
- Can use entire skills.md (no compression needed)
- Fast response times (2-5 seconds)
- Can search online for additional information
- Natural conversation flow

### 6.3 Onboard AI (Phi-2)

**Compressed Context** (2K token window):
```javascript
async function queryPhi2(question, context) {
  // Phi-2 has limited context window - must compress
  const compressedSkills = compressContextForPhi2(context.skills);

  const prompt = `You are a marine assistant. Boat info:
${compressedSkills}

Current data:
RPM: ${context.currentData.rpm}
Oil: ${context.currentData.oilPressure} PSI
Temp: ${context.currentData.temperature}°F
Fuel: ${context.currentData.fuelLevel}%

Question: ${question}

Answer concisely:`;

  const answer = await llama.generate(prompt, {
    max_tokens: 100,
    temperature: 0.7
  });

  return answer;
}

function compressContextForPhi2(skills) {
  // Extract only essential sections
  const essential = [
    'System Information',
    'Boat Information',
    'Engine Information',
    'Normal Operating Parameters'
  ];

  let compressed = '';
  essential.forEach(section => {
    const match = skills.match(
      new RegExp(`## ${section}[\\s\\S]*?(?=##|$)`)
    );
    if (match) {
      // Further compress: remove markdown formatting
      const text = match[0]
        .replace(/^#+\s*/gm, '')    // Remove headers
        .replace(/\*\*/g, '')       // Remove bold
        .replace(/\n\n+/g, '\n')    // Single line breaks
        .trim();

      compressed += text + '\n';
    }
  });

  // Add last 3 Q&A only
  const conversations = extractRecentConversations(skills, 3);
  if (conversations) {
    compressed += '\nRecent Q&A:\n' + conversations;
  }

  return compressed;
}
```

**Limitations**:
- Cannot use full skills.md (only essential info)
- Slower response (~60 seconds)
- Less context-aware
- No online search capability

**Workaround**: Status updates every 40 seconds during processing

---

## 7. SIZE MANAGEMENT & OPTIMIZATION

### 7.1 Target Size

- **Target**: < 10MB total
- **Warning**: 8-9MB (prompt user to archive)
- **Critical**: > 10MB (automatic archival)

### 7.2 Size Breakdown

Typical sizes:
- System Information: ~1KB
- Boat Information: ~2KB
- Engine Information: ~5KB
- Engine Manual: ~50KB (compressed)
- Boat Manual: ~50KB (compressed)
- Regulations: ~30KB
- Best Practices: ~20KB
- Conversation History (50 entries): ~50KB
- Maintenance Log: ~10KB
- Notes: ~10KB

**Total**: ~230KB (plenty of room to grow)

### 7.3 Automatic Compression

**When Size Exceeds 8MB**:
```javascript
async function checkAndCompressSkills() {
  const skills = fs.readFileSync('/opt/d3kos/config/skills.md', 'utf-8');
  const sizeInMB = Buffer.byteLength(skills, 'utf-8') / (1024 * 1024);

  if (sizeInMB > 8) {
    console.log(`skills.md is ${sizeInMB.toFixed(2)}MB - archiving old conversations`);

    // Archive conversation history
    const conversations = extractConversationHistory(skills);
    const archiveFile = `/opt/d3kos/data/archived-conversations/conversations-${Date.now()}.md`;
    fs.writeFileSync(archiveFile, conversations);

    // Keep only last 50 entries
    const pruned = keepRecentConversations(skills, 50);
    fs.writeFileSync('/opt/d3kos/config/skills.md', pruned);

    console.log(`Archived old conversations to ${archiveFile}`);
  }
}

// Run daily
setInterval(checkAndCompressSkills, 24 * 60 * 60 * 1000);
```

### 7.4 Manual Pruning

**User can manually archive**:
- Main Menu → Settings → AI Knowledge Base → Archive Old Conversations
- Moves all but last 50 Q&A to archive file
- Archive files remain searchable if needed

---

## 8. LEARNING & MEMORY INTEGRATION

### 8.1 What Gets Saved

AI automatically saves conversations that:
1. User marks as important (5-star rating)
2. Technical questions about boat/engine
3. Contain keywords: "how to", "what is", "normal", "procedure", "regulation"
4. User explicitly says "remember this"

### 8.2 Conversation Database

**SQLite Schema** (separate from skills.md):
```sql
CREATE TABLE conversations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  question TEXT NOT NULL,
  answer TEXT NOT NULL,
  ai_used TEXT NOT NULL,
  important BOOLEAN DEFAULT 0,
  added_to_skills BOOLEAN DEFAULT 0,
  user_rating INTEGER
);
```

**Important conversations** are copied to skills.md:
```javascript
async function saveImportantConversation(question, answer, aiUsed) {
  // Save to database
  await db.run(
    'INSERT INTO conversations (question, answer, ai_used, important, added_to_skills) VALUES (?, ?, ?, 1, 1)',
    [question, answer, aiUsed]
  );

  // Append to skills.md
  const entry = `
**Q**: ${question}
**A**: ${answer}
**Date**: ${new Date().toISOString()}
**Source**: ${aiUsed === 'online' ? 'Online AI' : 'Onboard AI'}

---

`;

  appendToSkillsFile('## Conversation History (Recent)', entry);
}
```

### 8.3 Learning Over Time

**Example**: After 6 months of use, skills.md contains:
- 50 important Q&A about this specific boat
- User-discovered quirks and workarounds
- Seasonal maintenance notes
- Preferred marinas and anchorages
- Troubleshooting history

Result: AI becomes an expert on **this specific boat**

---

## 9. IMPLEMENTATION GUIDE

### 9.1 Creating skills.md Template

**Initial Template**:
```javascript
function generateSkillsTemplate() {
  return `# d3kOS Skills Database

## System Information
- Installation ID: ${generateInstallationID()}
- Installation Date: ${new Date().toISOString().split('T')[0]}
- Last Updated: ${new Date().toISOString()}
- Skills Version: 1.0
- d3kOS Version: ${getD3kOSVersion()}
- Tier: ${getCurrentTier()}

## Boat Information
[To be populated during onboarding]

## Engine Information
[To be populated during onboarding]

## Engine Manual (Text Extracted)
[Will be downloaded during onboarding if internet available]

## Boat Owner's Manual (Text Extracted)
[Will be downloaded during onboarding if internet available]

## Regional Regulations
[Will be downloaded during onboarding if internet available]

## Best Practices (BoatUS.org)
[Will be downloaded during onboarding if internet available]

## International Sailing
[Add destination countries as needed]

## Conversation History (Recent)
[Important conversations will be added here automatically]

## Maintenance Log
[Log your maintenance here or let AI track it]

## Notes & Customizations
[Add your own notes here]
`;
}
```

### 9.2 Populating from Onboarding

**Integration Point**: Onboarding wizard Steps 19-20

```javascript
// In onboarding wizard (after engine configuration complete)
async function completeOnboarding() {
  // ... existing onboarding code ...

  // Step 19: Generate skills.md
  showStep(19, "Building AI Knowledge Base");

  const boatInfo = getBoatInfo();
  const engineInfo = getEngineInfo();
  const location = getLocation();

  const hasInternet = await checkInternetConnection();

  if (hasInternet) {
    // Download manuals and regulations
    await populateSkillsFile(boatInfo, engineInfo, location);
  } else {
    // Create template only
    const template = generateSkillsTemplate();
    const populated = fillTemplateWithOnboardingData(template, boatInfo, engineInfo);
    fs.writeFileSync('/opt/d3kos/config/skills.md', populated);

    showMessage("Internet not available. skills.md created with basic info. Connect to internet and re-run onboarding to download manuals and regulations.");
  }

  // Step 20: QR Code generation
  showStep(20, "Generating QR Code");
  // ... existing QR code logic ...
}
```

### 9.3 Updating skills.md

**User-Initiated Update**:
- Main Menu → Settings → AI Knowledge Base → Update Manuals

**Automatic Updates**:
- Check for regulation updates quarterly (if internet available)
- Prompt user: "New regional regulations available. Update?"

---

## 10. API REFERENCE

### 10.1 File Operations

#### loadSkills()
```javascript
function loadSkills() {
  return fs.readFileSync('/opt/d3kos/config/skills.md', 'utf-8');
}
```

#### saveSkills(content)
```javascript
function saveSkills(content) {
  fs.writeFileSync('/opt/d3kos/config/skills.md', content);
}
```

#### appendToSkills(section, content)
```javascript
function appendToSkills(section, content) {
  let skills = loadSkills();
  const sectionRegex = new RegExp(`(## ${section}[\\s\\S]*?)(?=##|$)`);
  const match = skills.match(sectionRegex);

  if (match) {
    const insertPosition = match.index + match[0].length;
    skills = skills.slice(0, insertPosition) + '\n' + content + skills.slice(insertPosition);
  }

  saveSkills(skills);
}
```

### 10.2 Section Extraction

#### extractSection(section)
```javascript
function extractSection(section) {
  const skills = loadSkills();
  const regex = new RegExp(`## ${section}[\\s\\S]*?(?=##|$)`);
  const match = skills.match(regex);
  return match ? match[0] : null;
}
```

#### updateSection(section, newContent)
```javascript
function updateSection(section, newContent) {
  let skills = loadSkills();
  const regex = new RegExp(`## ${section}[\\s\\S]*?(?=##|$)`);
  skills = skills.replace(regex, `## ${section}\n${newContent}\n\n`);
  saveSkills(skills);
}
```

### 10.3 Size Management

#### getSkillsSize()
```javascript
function getSkillsSize() {
  const skills = loadSkills();
  return Buffer.byteLength(skills, 'utf-8');
}
```

#### archiveConversations()
```javascript
function archiveConversations() {
  const skills = loadSkills();
  const conversations = extractSection('Conversation History \\(Recent\\)');

  if (conversations) {
    const archiveFile = `/opt/d3kos/data/archived-conversations/archive-${Date.now()}.md`;
    fs.writeFileSync(archiveFile, conversations);

    // Keep only last 50
    const recent = keepRecentConversations(skills, 50);
    saveSkills(recent);

    return archiveFile;
  }

  return null;
}
```

---

## 11. BEST PRACTICES

### 11.1 For Users

1. **Complete Onboarding with Internet**: Download manuals during initial setup
2. **Add Local Knowledge**: Use Notes section for marina contacts, favorite spots
3. **Review Conversation History**: Periodically review and delete irrelevant Q&A
4. **Backup Regularly**: skills.md is your boat's "brain" - back it up!
5. **Update Annually**: Re-run document retrieval yearly for regulation updates

### 11.2 For Developers

1. **Validate Content**: Always validate content before adding to skills.md
2. **Compress Aggressively**: Keep text-only extracts, remove unnecessary content
3. **Handle Errors Gracefully**: Failed downloads should not break onboarding
4. **Test AI Context Loading**: Ensure both AIs can parse skills.md correctly
5. **Monitor Size**: Implement size warnings before hitting 10MB limit
6. **Version Control**: Track changes to skills.md format in git

### 11.3 For AI Integration

1. **Always Load Fresh**: Don't cache skills.md - always read from disk
2. **Compress for Phi-2**: Use compressed context for onboard AI
3. **Full Context for Perplexity**: Send complete skills.md to online AI
4. **Include Current Data**: Always merge real-time data with static context
5. **Log Context Usage**: Track which sections AI references in responses

---

## 12. TROUBLESHOOTING

### Common Issues

**Issue**: skills.md not found
**Solution**: Check `/opt/d3kos/config/skills.md` exists. If not, re-run onboarding.

**Issue**: PDF extraction fails
**Solution**: Check `pdf-parse` package is installed. Try alternative PDF libraries.

**Issue**: skills.md growing too large
**Solution**: Run `archiveConversations()` to move old Q&A to archive.

**Issue**: AI not using context
**Solution**: Verify skills.md loads correctly. Check AI prompt includes skills content.

**Issue**: Manuals not downloading during onboarding
**Solution**: Verify internet connection. Check manualslib.com accessibility. Use fallback sources.

---

## APPENDICES

### Appendix A: Example skills.md File

See: `/opt/d3kos/examples/skills-example.md`

### Appendix B: Supported Manual Sources

- manualslib.com
- boats.net/manuals
- Manufacturer websites (Mercury, Volvo Penta, Yanmar, etc.)
- User uploads (manual PDF upload feature - future)

### Appendix C: Regulation Sources by Country

**United States**: uscgboating.org
**Canada**: tc.canada.ca
**United Kingdom**: rya.org.uk
**Australia**: marinesafety.gov.au
**New Zealand**: maritimenz.govt.nz

---

**END OF SPECIFICATION**

Last Updated: February 12, 2026
Version: 1.0
