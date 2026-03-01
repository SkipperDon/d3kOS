# Multi-Language Support - d3kOS Internationalization

**Version:** 1.0
**Date:** March 1, 2026
**Status:** Specification - Pre-v1.0 Requirement
**Priority:** Low (but must complete before v1.0 production release)
**Target Version:** v0.15.0 (September 2027)
**Estimated Effort:** 6-8 weeks

---

## EXECUTIVE SUMMARY

Add multi-language support to d3kOS to enable international distribution. Users can select their preferred language from Settings, with auto-default based on boat origin. All UI text, voice responses, and system messages will be localized.

**Key Features:**
- Language selector in Settings (dropdown)
- Auto-default based on boat origin from onboarding wizard
- 8 languages initially: English, French, Spanish, German, Italian, Dutch, Swedish, Norwegian
- JSON-based translation files
- Real-time language switching (no page reload required)
- Voice assistant responses in selected language
- Fallback to English if translation missing

---

## BUSINESS JUSTIFICATION

### Market Expansion Opportunity

**Current Limitation:**
- d3kOS is English-only
- Blocks distribution in non-English speaking countries
- Limits market to ~400M English speakers

**With Multi-Language:**
- Opens European market (740M people)
- Opens Latin American market (650M Spanish/Portuguese speakers)
- Opens Canadian French market (7.5M Quebec boaters)
- Enables global distribution

### Competitive Advantage

| Feature | d3kOS (with i18n) | Garmin | Raymarine | Simrad |
|---------|-------------------|--------|-----------|--------|
| Multi-Language UI | ✅ 8 languages | ✅ 25+ | ✅ 20+ | ✅ 15+ |
| Voice in Local Language | ✅ Yes | ❌ No | ❌ No | ❌ No |
| Free Language Packs | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| Community Translations | ✅ Planned | ❌ No | ❌ No | ❌ No |

**ROI:**
- Development Cost: $15,000-24,000 (6-8 weeks)
- Market Expansion: +60% potential users
- Required for v1.0 production release

---

## LANGUAGES SUPPORTED (PHASE 1)

### Initial 8 Languages

| Language | Code | Market | Speakers | Priority |
|----------|------|--------|----------|----------|
| **English** | `en` | USA, Canada, UK, Australia | 400M | Default |
| **French** | `fr` | France, Canada (Quebec) | 80M | High |
| **Spanish** | `es` | Spain, Latin America | 580M | High |
| **German** | `de` | Germany, Austria, Switzerland | 95M | Medium |
| **Italian** | `it` | Italy | 65M | Medium |
| **Dutch** | `nl` | Netherlands, Belgium | 25M | Medium |
| **Swedish** | `sv` | Sweden | 10M | Low |
| **Norwegian** | `no` | Norway | 5M | Low |

**Total Coverage:** ~1.26 billion speakers

### Future Languages (Phase 2 - Post-v1.0)

- Portuguese (`pt`) - Brazil, Portugal (260M speakers)
- Russian (`ru`) - Russia (150M speakers)
- Japanese (`ja`) - Japan (125M speakers)
- Chinese Simplified (`zh-CN`) - China (1.1B speakers)
- Turkish (`tr`) - Turkey (80M speakers)
- Greek (`el`) - Greece (13M speakers)
- Polish (`pl`) - Poland (45M speakers)
- Danish (`da`) - Denmark (6M speakers)
- Finnish (`fi`) - Finland (5M speakers)

---

## AUTO-DEFAULT LOGIC

### Based on Boat Origin (Onboarding Step 15)

Similar to metric/imperial auto-detection:

| Boat Origin | Default Language | Rationale |
|-------------|------------------|-----------|
| **United States** | English (`en`) | Primary market |
| **Canada** | English (`en`) | Majority English, French available |
| **United Kingdom** | English (`en`) | Native language |
| **Australia** | English (`en`) | Native language |
| **France** | French (`fr`) | Native language |
| **Spain** | Spanish (`es`) | Native language |
| **Germany** | German (`de`) | Native language |
| **Italy** | Italian (`it`) | Native language |
| **Netherlands** | Dutch (`nl`) | Native language |
| **Sweden** | Swedish (`sv`) | Native language |
| **Norway** | Norwegian (`no`) | Native language |
| **Mexico** | Spanish (`es`) | Spanish-speaking |
| **Other** | English (`en`) | Fallback |

**User Can Override:** Always changeable in Settings

---

## IMPLEMENTATION ARCHITECTURE

### Translation File Structure

**Location:** `/opt/d3kos/config/i18n/`

**Format:** JSON per language

```json
// /opt/d3kos/config/i18n/en.json (English - master)
{
  "meta": {
    "language": "English",
    "code": "en",
    "version": "1.0",
    "last_updated": "2027-09-01"
  },
  "common": {
    "main_menu": "Main Menu",
    "settings": "Settings",
    "back": "Back",
    "save": "Save",
    "cancel": "Cancel",
    "ok": "OK",
    "yes": "Yes",
    "no": "No",
    "loading": "Loading..."
  },
  "dashboard": {
    "title": "Engine Dashboard",
    "rpm": "RPM",
    "oil_pressure": "Oil Pressure",
    "engine_temp": "Engine Temperature",
    "fuel_level": "Fuel Level",
    "battery_voltage": "Battery Voltage",
    "boost_pressure": "Boost Pressure",
    "coolant_temp": "Coolant Temperature",
    "speed": "Speed",
    "heading": "Heading"
  },
  "onboarding": {
    "welcome": "Welcome to d3kOS",
    "step": "Step",
    "of": "of",
    "next": "Next",
    "previous": "Previous",
    "finish": "Finish",
    "boat_info": "Boat Information",
    "engine_info": "Engine Information",
    "boat_manufacturer": "Boat Manufacturer",
    "boat_year": "Boat Year",
    "boat_model": "Boat Model",
    "boat_origin": "Where was your boat manufactured?"
  },
  "voice": {
    "wake_word_detected": "Aye Aye Captain",
    "listening": "Listening...",
    "processing": "Processing...",
    "rpm_response": "The current RPM is {rpm}.",
    "oil_response": "Oil pressure is {psi} PSI.",
    "temp_response": "Engine temperature is {temp} degrees.",
    "fuel_response": "Fuel level is {level} percent.",
    "status_response": "All systems operational."
  },
  "errors": {
    "network_error": "Network connection error",
    "service_unavailable": "Service temporarily unavailable",
    "invalid_input": "Invalid input",
    "file_not_found": "File not found",
    "permission_denied": "Permission denied"
  },
  "settings": {
    "language": "Language",
    "language_description": "Select your preferred language. Changes take effect immediately.",
    "measurement_system": "Measurement System",
    "measurement_description": "Choose between Imperial or Metric units."
  }
}
```

```json
// /opt/d3kos/config/i18n/fr.json (French)
{
  "meta": {
    "language": "Français",
    "code": "fr",
    "version": "1.0",
    "last_updated": "2027-09-01"
  },
  "common": {
    "main_menu": "Menu Principal",
    "settings": "Paramètres",
    "back": "Retour",
    "save": "Enregistrer",
    "cancel": "Annuler",
    "ok": "OK",
    "yes": "Oui",
    "no": "Non",
    "loading": "Chargement..."
  },
  "dashboard": {
    "title": "Tableau de Bord Moteur",
    "rpm": "RPM",
    "oil_pressure": "Pression d'Huile",
    "engine_temp": "Température Moteur",
    "fuel_level": "Niveau de Carburant",
    "battery_voltage": "Tension Batterie",
    "boost_pressure": "Pression Turbo",
    "coolant_temp": "Température Liquide de Refroidissement",
    "speed": "Vitesse",
    "heading": "Cap"
  }
  // ... (full translations)
}
```

### JavaScript i18n Utility

**File:** `/var/www/html/js/i18n.js`

```javascript
const i18n = {
  currentLanguage: 'en',
  translations: {},

  // Initialize i18n system
  init: async function() {
    // Get user preference from API
    const response = await fetch('/api/preferences');
    const prefs = await response.json();
    this.currentLanguage = prefs.language || 'en';

    // Load translation file
    await this.loadLanguage(this.currentLanguage);

    // Update all page text
    this.updatePageText();
  },

  // Load language file
  loadLanguage: async function(code) {
    const response = await fetch(`/i18n/${code}.json`);
    this.translations = await response.json();
    this.currentLanguage = code;
    localStorage.setItem('d3kos-language', code);
  },

  // Get translated string
  t: function(key, params = {}) {
    // Split key by dots (e.g., "dashboard.rpm")
    const keys = key.split('.');
    let value = this.translations;

    // Traverse object
    for (const k of keys) {
      value = value?.[k];
      if (!value) {
        console.warn(`Missing translation: ${key}`);
        return key; // Fallback to key itself
      }
    }

    // Replace parameters {rpm}, {psi}, etc.
    if (typeof value === 'string') {
      return value.replace(/\{(\w+)\}/g, (match, param) => {
        return params[param] !== undefined ? params[param] : match;
      });
    }

    return value;
  },

  // Update all text on page
  updatePageText: function() {
    // Find all elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      el.textContent = this.t(key);
    });

    // Update placeholders
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      const key = el.getAttribute('data-i18n-placeholder');
      el.placeholder = this.t(key);
    });

    // Update titles
    document.querySelectorAll('[data-i18n-title]').forEach(el => {
      const key = el.getAttribute('data-i18n-title');
      el.title = this.t(key);
    });
  },

  // Change language
  setLanguage: async function(code) {
    await this.loadLanguage(code);
    this.updatePageText();

    // Save to server
    await fetch('/api/preferences', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({language: code})
    });
  }
};

// Auto-init on page load
document.addEventListener('DOMContentLoaded', () => {
  i18n.init();
});
```

### HTML Usage Example

```html
<!-- Simple text translation -->
<h1 data-i18n="dashboard.title">Engine Dashboard</h1>
<button data-i18n="common.save">Save</button>

<!-- With placeholder -->
<input type="text" data-i18n-placeholder="onboarding.boat_manufacturer">

<!-- With title/tooltip -->
<button data-i18n-title="common.help" class="help-btn">?</button>

<!-- Dynamic content via JavaScript -->
<script>
  const rpmValue = 1500;
  document.getElementById('rpm-label').textContent = i18n.t('voice.rpm_response', {rpm: rpmValue});
  // Output: "The current RPM is 1500." (English)
  // Output: "Le RPM actuel est 1500." (French)
</script>
```

### Backend API (Preferences API Extended)

**Service:** `/opt/d3kos/services/config/preferences-api.py` (Port 8107)

**Endpoints:**

1. **GET /preferences** - Get all user preferences
```json
{
  "measurement_system": "metric",
  "language": "fr",
  "timezone": "America/Toronto"
}
```

2. **POST /preferences** - Update preferences
```json
{
  "language": "es"
}
```

3. **GET /i18n/languages** - List available languages
```json
{
  "languages": [
    {"code": "en", "name": "English", "native": "English"},
    {"code": "fr", "name": "French", "native": "Français"},
    {"code": "es", "name": "Spanish", "native": "Español"},
    {"code": "de", "name": "German", "native": "Deutsch"},
    {"code": "it", "name": "Italian", "native": "Italiano"},
    {"code": "nl", "name": "Dutch", "native": "Nederlands"},
    {"code": "sv", "name": "Swedish", "native": "Svenska"},
    {"code": "no", "name": "Norwegian", "native": "Norsk"}
  ]
}
```

4. **GET /i18n/{code}.json** - Fetch translation file

**Storage:** `/opt/d3kos/config/user-preferences.json`

```json
{
  "measurement_system": "metric",
  "language": "fr",
  "timezone": "America/Toronto",
  "voice_enabled": true,
  "camera_enabled": true
}
```

---

## VOICE ASSISTANT INTEGRATION

### Text-to-Speech Language Support

**Current:** Piper TTS with `en_US-amy-medium` voice

**Multi-Language:** Piper supports multiple voices per language

**Voices to Install:**

| Language | Piper Voice Model | Size |
|----------|-------------------|------|
| English | `en_US-amy-medium` | 50 MB (installed) |
| French | `fr_FR-siwis-medium` | 45 MB |
| Spanish | `es_ES-sharvard-medium` | 48 MB |
| German | `de_DE-thorsten-medium` | 52 MB |
| Italian | `it_IT-riccardo-x_low` | 30 MB |
| Dutch | `nl_NL-mls-medium` | 42 MB |
| Swedish | `sv_SE-nst-medium` | 40 MB |
| Norwegian | `no_NO-talesyntese-medium` | 38 MB |

**Total Storage:** ~345 MB (all 8 languages)

### Voice Response Translation

**File:** `/opt/d3kos/services/ai/query_handler.py`

**Updated Response Logic:**

```python
def simple_response(self, category, boat_status):
    """Generate rule-based response in user's language"""
    # Get user language preference
    prefs = self.load_user_preferences()
    lang = prefs.get('language', 'en')

    # Load translation file
    with open(f'/opt/d3kos/config/i18n/{lang}.json', 'r') as f:
        translations = json.load(f)

    # Get translated template
    if category == 'rpm':
        template = translations['voice']['rpm_response']
        rpm = boat_status.get('rpm', 'N/A')
        return template.format(rpm=rpm)

    elif category == 'oil':
        template = translations['voice']['oil_response']
        psi = boat_status.get('oil_pressure', 'N/A')
        return template.format(psi=psi)

    # ... (all other categories)
```

### Wake Word (Unchanged)

**Wake word remains:** "helm" (language-neutral, maritime term used internationally)

**No translation needed** - "helm" recognized in all languages

---

## SETTINGS UI

### Language Selector

**Location:** Settings → General → Language

**HTML:**

```html
<div class="settings-section">
  <h2 data-i18n="settings.language">Language</h2>
  <div class="setting-row">
    <label for="language-select">
      <span data-i18n="settings.language_description">
        Select your preferred language. Changes take effect immediately.
      </span>
    </label>
    <select id="language-select" onchange="changeLanguage(this.value)">
      <option value="en">English</option>
      <option value="fr">Français (French)</option>
      <option value="es">Español (Spanish)</option>
      <option value="de">Deutsch (German)</option>
      <option value="it">Italiano (Italian)</option>
      <option value="nl">Nederlands (Dutch)</option>
      <option value="sv">Svenska (Swedish)</option>
      <option value="no">Norsk (Norwegian)</option>
    </select>
  </div>
</div>

<script>
async function changeLanguage(code) {
  await i18n.setLanguage(code);

  // Update language selector (in case page reloads)
  document.getElementById('language-select').value = code;

  // Optional: Show confirmation
  alert(i18n.t('settings.language_changed'));
}

// Set current language on load
document.addEventListener('DOMContentLoaded', async () => {
  const response = await fetch('/api/preferences');
  const prefs = await response.json();
  document.getElementById('language-select').value = prefs.language || 'en';
});
</script>
```

---

## IMPLEMENTATION PHASES

### Phase 1: Foundation (Week 1-2)

**Tasks:**
1. Create i18n directory structure (`/opt/d3kos/config/i18n/`)
2. Create master `en.json` translation file (extract all English strings from UI)
3. Create `i18n.js` utility library
4. Extend preferences API to handle language setting
5. Update `user-preferences.json` schema

**Deliverables:**
- Complete English translation file (500+ strings)
- Working i18n.js library
- Language preference storage

**Estimated Time:** 16 hours

---

### Phase 2: UI Translation (Week 3-4)

**Tasks:**
1. Update all HTML pages with `data-i18n` attributes
   - index.html (main menu)
   - dashboard.html
   - onboarding.html (20 steps)
   - settings.html
   - navigation.html
   - weather.html
   - boatlog.html
   - helm.html
   - ai-assistant.html
   - marine-vision.html
   - upload-manual.html
   - manuals.html
2. Test real-time language switching
3. Create Settings UI language selector

**Deliverables:**
- All pages support i18n
- Language selector in Settings
- No English hardcoded in HTML

**Estimated Time:** 24 hours

---

### Phase 3: Professional Translation (Week 5-6)

**Tasks:**
1. **Option A: Professional Translation Service**
   - Send `en.json` to translation service
   - Cost: ~$0.10/word × 2,500 words × 7 languages = ~$1,750
   - Quality: High (native speakers)
   - Turnaround: 5-7 days

2. **Option B: Community Translation**
   - Create translation portal (Weblate/Crowdin)
   - Recruit volunteer translators from boating community
   - Quality: Variable (requires review)
   - Cost: Free
   - Turnaround: 2-4 weeks

**Recommended:** Option A (professional) for v1.0, Option B for future languages

**Deliverables:**
- 7 complete translation files (fr, es, de, it, nl, sv, no)
- Native speaker review/testing

**Estimated Time:** External service (1 week wait) or 24 hours coordination

---

### Phase 4: Voice Assistant Integration (Week 7)

**Tasks:**
1. Download Piper TTS voice models (7 languages)
2. Update `voice-assistant-hybrid.py` to use language preference
3. Update `query_handler.py` for translated responses
4. Test all voice responses in each language

**Deliverables:**
- Voice responses in 8 languages
- Piper voice models installed

**Estimated Time:** 16 hours

---

### Phase 5: Testing & QA (Week 8)

**Tasks:**
1. Test language switching on all pages
2. Test voice responses in all languages
3. Test auto-default logic (8 boat origins)
4. Check for untranslated strings (fallback to English)
5. Performance testing (translation file loading time)
6. Beta testing with native speakers (1 per language)

**Deliverables:**
- QA test results
- Bug fixes
- Native speaker feedback incorporated

**Estimated Time:** 24 hours

---

## WHAT GETS TRANSLATED

### UI Text (All Pages)

✅ **Translated:**
- Page titles
- Button labels ("Save", "Cancel", "Next", "Back")
- Form labels ("Boat Manufacturer", "Engine Model")
- Menu items ("Dashboard", "Settings", "Boatlog")
- Status messages ("Loading...", "Success", "Error")
- Help text
- Tooltips
- Error messages

❌ **NOT Translated:**
- Boat manufacturer names ("Bayliner", "Sea Ray")
- Engine manufacturer names ("Mercruiser", "Volvo Penta")
- Technical abbreviations ("RPM", "PSI", "GPS")
- User-entered data (boat name, registration number)
- Code/API responses (JSON, technical logs)
- URLs

### Voice Assistant Responses

✅ **Translated:**
- "Aye Aye Captain" (wake word acknowledgment)
- "The current RPM is {value}"
- "Oil pressure is {value} PSI"
- "All systems operational"
- Error messages ("Sensor not available")

❌ **NOT Translated:**
- Wake word "helm" (international maritime term)
- Unit abbreviations (RPM, PSI, °F, °C)
- Technical terms (NMEA2000, Signal K)

### Documentation

**Scope:** Separate from v0.15.0 (post-v1.0 task)

- User manuals
- Help pages
- Troubleshooting guides
- README files
- API documentation

---

## TESTING STRATEGY

### Unit Tests

**Test Cases:**
1. `i18n.t('dashboard.rpm')` returns correct translation
2. Missing translation falls back to English
3. Parameter substitution works (`{rpm}` → actual value)
4. Language switching updates all page elements
5. Preference API stores language correctly
6. Translation file loads without errors

### Integration Tests

**Test Cases:**
1. Change language in Settings → all pages update
2. Onboarding auto-default based on boat origin
3. Voice responses use correct language
4. All 8 languages load successfully
5. Browser refresh persists language choice

### Native Speaker Testing

**Requirement:** 1 native speaker tester per language (8 total)

**Test Script:**
1. Set language to native language
2. Complete onboarding wizard
3. Navigate through all pages
4. Test voice assistant (5 queries)
5. Report untranslated strings
6. Report awkward/incorrect translations
7. Report cultural issues (date formats, number formats)

---

## FALLBACK STRATEGY

### Missing Translations

**Behavior:** Fall back to English if translation key missing

**Example:**
```javascript
i18n.t('new_feature.title')
// If "new_feature.title" doesn't exist in fr.json
// → Returns "new_feature.title" (key itself)
// → Console warning: "Missing translation: new_feature.title"
```

**Best Practice:**
- Always add new strings to `en.json` first
- Log missing translations for future translation work
- Never crash if translation missing

### Unsupported Languages

**User selects unsupported language:**
- Default to English
- Show message: "Language not yet supported. Using English."

---

## FUTURE ENHANCEMENTS

### Phase 2 (Post-v1.0)

1. **Additional Languages**
   - Portuguese, Russian, Japanese, Chinese
   - Community-contributed translations

2. **Right-to-Left (RTL) Support**
   - Arabic, Hebrew
   - CSS mirroring for RTL layouts

3. **Regional Variants**
   - English (US vs UK vs AU)
   - Spanish (Spain vs Mexico vs Argentina)
   - French (France vs Quebec)

4. **Date/Time Localization**
   - Date formats (MM/DD/YYYY vs DD/MM/YYYY)
   - Time formats (12-hour vs 24-hour)
   - First day of week (Sunday vs Monday)

5. **Number Localization**
   - Decimal separator (1,000.50 vs 1.000,50)
   - Currency formats

6. **Translation Management Portal**
   - Web-based translation interface
   - Community contributions
   - Version control for translations
   - Translation progress tracking

---

## COST BREAKDOWN

### Development

**Internal Development:**
- Phase 1: 16 hours × $75/hour = $1,200
- Phase 2: 24 hours × $75/hour = $1,800
- Phase 4: 16 hours × $75/hour = $1,200
- Phase 5: 24 hours × $75/hour = $1,800
- **Subtotal:** $6,000

**External Translation Service:**
- Professional translation: $1,750 (one-time)

**Total Development:** $7,750 - $10,500

### Ongoing Costs

- Translation updates: $200-500/year (new features, UI changes)
- Storage: 10 MB (translation files + voice models)
- Performance impact: Negligible (< 1ms to load translation file)

### ROI

**Market Expansion:**
- Current addressable market: 400M English speakers
- With 8 languages: 1.26B speakers (+215% increase)
- Estimated revenue increase: 30-60% (conservative)

**Break-even:** 12-18 months after v1.0 launch

---

## DEPENDENCIES

### Required Before v0.15.0

- ✅ Preferences API (Port 8107) - Already exists (v0.9.2)
- ✅ Settings page structure - Already exists
- ✅ User preference storage - Already exists
- ✅ Piper TTS system - Already exists
- ✅ Voice assistant - Already exists

### No New Infrastructure Required

All existing systems can be extended for i18n support.

---

## RISKS & MITIGATION

### Translation Quality

**Risk:** Poor translations confuse users
**Mitigation:** Use professional service for v1.0, native speaker testing

### Incomplete Translations

**Risk:** New features missing translations
**Mitigation:** English fallback, log missing keys, translation portal

### Storage Overhead

**Risk:** 8 translation files + 8 voice models = ~350 MB
**Mitigation:** Acceptable on 128GB SD card (0.3% usage)

### Performance Impact

**Risk:** Loading translation files slows page load
**Mitigation:** Cache in localStorage, async loading, < 50 KB per file

---

## SUCCESS METRICS

### Technical

- ✅ All UI strings translatable (0 hardcoded English)
- ✅ Translation file loads < 100ms
- ✅ Language switching < 200ms
- ✅ Voice responses in correct language 100% of time
- ✅ Zero crashes due to missing translations

### User Experience

- ✅ User satisfaction > 4.5/5 (native language users)
- ✅ 90%+ strings professionally translated
- ✅ Auto-default accuracy > 95%
- ✅ Community translation contributions (post-v1.0)

### Business

- ✅ Enables European distribution (v1.0 requirement)
- ✅ Enables Latin American distribution
- ✅ Revenue increase > 30% within 12 months of v1.0

---

## DELIVERABLES

1. **Translation Files** - 8 JSON files (en, fr, es, de, it, nl, sv, no)
2. **i18n JavaScript Library** - `/var/www/html/js/i18n.js`
3. **Preferences API Extension** - Language preference support
4. **Settings UI** - Language selector dropdown
5. **Voice Models** - 8 Piper TTS voice models installed
6. **Documentation** - Translation guide, developer guide
7. **QA Report** - Native speaker test results

---

## TIMELINE

**Target:** v0.15.0 - September 2027 (before v1.0)
**Duration:** 6-8 weeks
**Effort:** 80-104 hours development + 1 week external translation

**Milestones:**
- Week 1-2: Foundation (i18n system, preferences)
- Week 3-4: UI translation (all pages updated)
- Week 5: Professional translation service (external)
- Week 6: Translation delivery and integration
- Week 7: Voice assistant integration
- Week 8: Testing and QA

---

## CONCLUSION

Multi-language support is **required for v1.0 production release** to enable international distribution. The feature is low complexity (extends existing systems) but high impact (market expansion).

**Recommendation:** Implement in v0.15.0 (September 2027), 2 months before v1.0 launch, to allow time for native speaker testing and translation refinement.

**Next Step:** Approve specification and allocate budget ($7,750-10,500) for Q3 2027 implementation.

---

**Document Version:** 1.0
**Author:** Claude Code (Anthropic) + Donald Moskaluk
**Date:** March 1, 2026

**© 2026 AtMyBoat.com | d3kOS - AI-Powered Marine Electronics**
*"Smarter Boating, Simpler Systems - Now in Your Language!"*
