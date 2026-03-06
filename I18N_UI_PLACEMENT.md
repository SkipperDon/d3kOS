# d3kOS Language Selector — UI Placement Instructions
## Instructions for Claude Code

> **Read I18N_IMPLEMENTATION.md first** before working on this file.
> This document covers WHERE to place the language selector.
> That document covers HOW the backend works.
> Both are required.

---

## Overview

The language selector must appear in **three places** in d3kOS, each serving
a different purpose. Implement them in this order — onboarding first, as it
is the most critical.

| Location | Priority | Purpose |
|----------|----------|---------|
| Onboarding Wizard — Question 0 | 🔴 Critical | First-boot language selection before anything else |
| Main Menu — globe icon | 🟡 Important | Always visible for crew/charter handover |
| Settings Page | 🟢 Standard | Change language after initial setup |

---

## Placement 1 — Onboarding Wizard (Question 0)

### Why
The onboarding wizard asks 13 questions about the engine. A French or Greek
sailor should answer those questions in their own language. Language must
therefore be **the first screen shown**, before Question 1 (engine manufacturer).

If the user has already completed onboarding and a language is saved in
`onboarding.json`, skip this screen and go straight to Question 1 as normal.
Only show it when `onboarding.json` has no `"language"` field, or when the
onboarding wizard is being run fresh.

### Where to Find the Onboarding Wizard
Look in `/opt/d3kos/services/onboarding/` — find the main HTML file that
renders the wizard steps. It will have a step controller (likely an array of
steps or a step index variable).

### What to Add

**Insert a new step at index 0** — before all existing questions.

The step should:
- Show the d3kOS logo and "Welcome to d3kOS / Bienvenue / Willkommen / Bienvenido"
  (show 4–5 languages simultaneously so the user recognises their own)
- Show the full 18-language grid (reuse `language-menu.html` layout/style)
- Have a single "Continue →" button that saves the selection and advances
  to Question 1
- NOT show a "Back" button (it is the first screen)
- NOT count toward the reset counter

**JavaScript — insert at top of step controller:**

```javascript
// ── QUESTION 0: LANGUAGE SELECTION ───────────────────────────────────────
// Shown only on fresh onboarding (no language saved yet).
// Skipped if language already set in onboarding.json.

async function shouldShowLanguageStep() {
  try {
    const res  = await fetch('http://localhost:8101/api/language');
    const data = await res.json();
    // Show language step if language is still default 'en' AND
    // this is a fresh onboarding (reset count === 0)
    return !data.language || data.language === 'en';
  } catch {
    return true; // If API offline, always show it
  }
}

// Call this before rendering the first wizard step:
// if (await shouldShowLanguageStep()) { showStep(0); } else { showStep(1); }
```

**HTML — the language step panel:**

```html
<!-- STEP 0: Language Selection — insert before existing step 1 HTML -->
<div class="wizard-step" id="step-language" data-step="0">

  <!-- Multi-language welcome — user recognises their language visually -->
  <div class="welcome-multilang">
    <div class="welcome-line">🇬🇧 Welcome to d3kOS</div>
    <div class="welcome-line">🇫🇷 Bienvenue sur d3kOS</div>
    <div class="welcome-line">🇩🇪 Willkommen bei d3kOS</div>
    <div class="welcome-line">🇪🇸 Bienvenido a d3kOS</div>
    <div class="welcome-line">🇮🇹 Benvenuto su d3kOS</div>
  </div>

  <h2 class="step-title">Select Your Language</h2>
  <p class="step-subtitle">Choose once — you can change this later in Settings</p>

  <!-- Reuse the same lang-grid pattern from language-menu.html -->
  <div class="lang-grid" id="onboarding-lang-grid" role="listbox">
    <!-- Populated by JavaScript — same buildGrid() function as language-menu.html -->
  </div>

  <!-- No back button on step 0 -->
  <div class="wizard-nav">
    <div class="selected-lang-label">
      Selected: <span id="ob-selected-name">English</span>
    </div>
    <button class="wizard-next-btn" id="ob-lang-confirm"
            onclick="confirmOnboardingLanguage()">
      Continue →
    </button>
  </div>

</div>
```

**CSS additions (add to onboarding stylesheet):**

```css
/* Multi-language welcome lines */
.welcome-multilang {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 24px;
  margin-bottom: 32px;
  justify-content: center;
}
.welcome-line {
  font-size: 22px;
  color: #888888;
  font-weight: 400;
}
.welcome-line:first-child {
  color: #00CC00;  /* Highlight English so it stands out as default */
  font-weight: 700;
}

/* Step subtitle */
.step-subtitle {
  font-size: 20px;
  color: #666666;
  margin-bottom: 24px;
  text-align: center;
}
```

**JavaScript — confirm function:**

```javascript
async function confirmOnboardingLanguage() {
  const btn = document.getElementById('ob-lang-confirm');
  btn.disabled = true;
  btn.textContent = 'Saving...';

  try {
    const lang = languages.find(l => l.code === currentLang);
    await fetch('http://localhost:8101/api/language', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ language: lang.code, dir: lang.dir })
    });
    // Advance to Question 1 (engine manufacturer)
    showStep(1);
  } catch (err) {
    btn.disabled = false;
    btn.textContent = 'Continue →';
    console.error('Language save failed:', err);
    // Still advance — don't block onboarding if API hiccups
    showStep(1);
  }
}
```

---

## Placement 2 — Main Menu Globe Icon

### Why
Charter guests, delivery crews, or anyone handed the helm needs to find the
language selector instantly — without reading any text at all. A globe icon
is universally understood regardless of language.

### Where to Find the Main Menu
Look in `/opt/d3kos/ui/` or the Node-RED Dashboard flows for the main menu
HTML. It will be the page that shows navigation tiles to Dashboard, Settings,
Boat Log, Camera etc.

### What to Add

Add a **globe button** to the main menu. It must be:
- Visible without scrolling
- Positioned consistently — **top-right corner** of the menu (standard
  location for language switchers globally)
- Not a full tile — a compact button so it doesn't dominate the menu
- Opens `http://localhost:8101/language` directly

**HTML — add inside the main menu header bar:**

```html
<!-- Add to the header/top bar of the main menu page -->
<!-- Position: top-right corner, alongside any existing header buttons -->

<button
  class="lang-globe-btn"
  onclick="window.location.href='http://localhost:8101/language'"
  aria-label="Change interface language"
  title="Change Language"
>
  🌐
  <span class="lang-globe-label" id="current-lang-display">EN</span>
</button>
```

**CSS — add to main menu stylesheet:**

```css
/* Globe language button — top-right of main menu header */
.lang-globe-btn {
  position: fixed;         /* Fixed so it stays visible when scrolling */
  top: 16px;
  right: 16px;
  z-index: 500;

  display: flex;
  align-items: center;
  gap: 8px;

  background: #111111;
  border: 2px solid #333333;
  border-radius: 6px;
  padding: 10px 16px;
  min-height: 60px;        /* Slightly smaller than main buttons — not dominant */
  min-width: 80px;

  font-size: 24px;         /* Globe emoji */
  color: #FFFFFF;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}

.lang-globe-btn:hover,
.lang-globe-btn:focus {
  background: #001a00;
  border-color: #00CC00;
  outline: none;
}

.lang-globe-btn:focus {
  outline: 3px solid #00CC00;
  outline-offset: 2px;
}

.lang-globe-label {
  font-size: 16px;
  font-weight: 700;
  color: #00CC00;
  letter-spacing: 0.08em;
}
```

**JavaScript — load and display the current language code on the button:**

```javascript
// Run on main menu page load — shows current language on the globe button
async function initLangGlobe() {
  try {
    const res  = await fetch('http://localhost:8101/api/language');
    const data = await res.json();
    const el   = document.getElementById('current-lang-display');
    if (el) el.textContent = (data.language || 'en').toUpperCase();
  } catch {
    // Silent fail — globe still works even if label stays as default
  }
}

// Call on page load:
document.addEventListener('DOMContentLoaded', initLangGlobe);
```

### If the Main Menu is a Node-RED Dashboard Flow

If the main menu is built in Node-RED Dashboard 2.0 (Vue-based), add a
**UI Template node** with the globe button HTML above. Wire it to the existing
layout so it appears in the top-right of the dashboard header.

In Node-RED, the template node should contain:
```html
<template>
  <div style="position:fixed;top:16px;right:16px;z-index:500;">
    <button @click="goToLanguage()" style="...same CSS as above...">
      🌐 <span>{{ currentLang }}</span>
    </button>
  </div>
</template>
<script>
export default {
  data() { return { currentLang: 'EN' } },
  mounted() {
    fetch('http://localhost:8101/api/language')
      .then(r => r.json())
      .then(d => { this.currentLang = (d.language || 'en').toUpperCase(); })
      .catch(() => {});
  },
  methods: {
    goToLanguage() { window.location.href = 'http://localhost:8101/language'; }
  }
}
</script>
```

---

## Placement 3 — Settings Page

### Why
Standard location for changing preferences. Sits alongside Network Settings
(port 8101, Session F) which uses the same Flask service — so the plumbing
is already there.

### Where to Find the Settings Page
Look for the Settings HTML page in `/opt/d3kos/ui/` or in Node-RED. It will
already contain links to Network Settings and possibly other configuration
screens.

### What to Add

Add a **Language Settings tile** to the Settings page, styled identically to
the existing Network Settings tile.

**HTML — add alongside existing settings tiles:**

```html
<!-- Add to Settings page — same style as existing Network Settings tile -->

<div class="settings-tile" id="tile-language">
  <div class="settings-tile-icon">🌐</div>
  <div class="settings-tile-content">
    <div class="settings-tile-title">Language</div>
    <div class="settings-tile-subtitle" id="settings-current-lang">
      Loading...
    </div>
  </div>
  <button
    class="settings-tile-btn"
    onclick="window.location.href='http://localhost:8101/language'"
    aria-label="Change interface language"
  >
    Change →
  </button>
</div>
```

**CSS — only needed if settings tiles don't already have this style.
Match exactly to the existing Network Settings tile style in the page:**

```css
/* Only add if not already defined for other settings tiles */
.settings-tile {
  display: flex;
  align-items: center;
  gap: 20px;
  background: #111111;
  border: 1px solid #333333;
  border-radius: 6px;
  padding: 20px 24px;
  min-height: 80px;
}
.settings-tile-icon    { font-size: 32px; }
.settings-tile-content { flex: 1; }
.settings-tile-title   { font-size: 24px; font-weight: 700; color: #FFFFFF; }
.settings-tile-subtitle { font-size: 20px; color: #888888; margin-top: 4px; }
.settings-tile-btn {
  background: transparent;
  border: 2px solid #333333;
  border-radius: 6px;
  padding: 12px 24px;
  min-height: 60px;
  font-size: 22px;
  color: #FFFFFF;
  cursor: pointer;
  transition: border-color 0.15s;
  white-space: nowrap;
}
.settings-tile-btn:hover { border-color: #00CC00; color: #00CC00; }
```

**JavaScript — show current language name in the tile subtitle:**

```javascript
// Run on Settings page load — shows current language in the tile
async function initSettingsLangTile() {
  const el = document.getElementById('settings-current-lang');
  if (!el) return;

  // Language names for display — matches the 18 in language-menu.html
  const langNames = {
    en:'English', fr:'Français', it:'Italiano', es:'Español',
    el:'Ελληνικά', hr:'Hrvatski', tr:'Türkçe', de:'Deutsch',
    nl:'Nederlands', sv:'Svenska', no:'Norsk', da:'Dansk',
    fi:'Suomi', pt:'Português', ar:'العربية', zh:'中文',
    ja:'日本語', uk:'Українська'
  };

  try {
    const res  = await fetch('http://localhost:8101/api/language');
    const data = await res.json();
    const name = langNames[data.language] || data.language || 'English';
    el.textContent = `Currently: ${name}`;
  } catch {
    el.textContent = 'Currently: English (default)';
  }
}

document.addEventListener('DOMContentLoaded', initSettingsLangTile);
```

---

## After Implementing All Three — Verification Checklist

### Onboarding
- [ ] Fresh onboarding (cleared `onboarding.json`) shows language step first
- [ ] Language step shows all 18 flags and names correctly
- [ ] Selecting a language and clicking Continue saves to API
- [ ] Question 1 (engine manufacturer) appears after language step
- [ ] If language already set, language step is skipped on next onboarding run
- [ ] Reset counter does NOT increment for the language step

### Main Menu Globe
- [ ] Globe icon visible in top-right on main menu without scrolling
- [ ] Globe button shows current language code (e.g. "FR", "EL")
- [ ] Tapping globe opens `http://localhost:8101/language`
- [ ] Globe button meets 60px min-height touch target
- [ ] Globe updates correctly after returning from language page

### Settings Page
- [ ] Language tile appears in Settings alongside Network Settings
- [ ] Subtitle shows current language name (e.g. "Currently: Français")
- [ ] Tapping "Change →" opens `http://localhost:8101/language`
- [ ] After changing language and returning, subtitle reflects new language

### Cross-Cutting
- [ ] Changing language on any path (onboarding / menu / settings) saves
      correctly to `onboarding.json` via `http://localhost:8101/api/language`
- [ ] All three entry points open the same `language-menu.html` page
- [ ] Language persists after Pi reboot

---

## Notes for Claude Code

- The language selection page (`language-menu.html`) is already built and
  tested. Do not rewrite it — just link to it from these three locations.
- All three entry points use the same URL: `http://localhost:8101/language`
- All API calls use `http://localhost:8101` — never filesystem paths.
- Match existing d3kOS design system exactly:
  `#000000` background · `#00CC00` accent · `#FFFFFF` text · Roboto font ·
  22px minimum · 80px minimum touch targets
- If you are unsure whether the main menu is plain HTML or Node-RED Dashboard,
  check `/opt/d3kos/ui/` for HTML files and `http://localhost:1880` for
  Node-RED flows. It may be both — implement for whichever is actually used.

---

*Designed by Claude (claude.ai) — March 2026*
*Companion to: I18N_IMPLEMENTATION.md*
*Architecture based on MASTER_SYSTEM_SPEC.md — SkipperDon/d3kOS*
