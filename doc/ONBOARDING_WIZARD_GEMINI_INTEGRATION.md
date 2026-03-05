# Onboarding Wizard: Gemini API Integration Design

**Version:** 1.0
**Date:** March 1, 2026
**Target:** d3kOS v0.10.0+
**Purpose:** Integrate Gemini API setup into initial onboarding wizard

---

## CURRENT ONBOARDING WIZARD FLOW

**Existing 20 Steps:**
- Steps 0-4: Welcome + Boat info (Manufacturer, Year, Model, Chartplotter)
- Steps 5-14: Engine info (Make, Model, Year, Cylinders, Size, Power, Compression, Idle/Max RPM, Type)
- Steps 15-16: Regional/Position (Boat Origin, Engine Position)
- Steps 17: Configuration Review
- Steps 18: DIP Switch Diagram
- Steps 19: QR Code (Installation ID)
- Steps 20: Finish

**File:** `/var/www/html/onboarding.html` (605 lines)

---

## PROPOSED NEW FLOW (22 Steps)

### **NEW Step 17: AI Assistant Setup (Optional)**

**Position:** After engine/boat setup, before configuration review
**Skippable:** Yes (user can skip and set up later in Settings)
**Tier:** Tier 2+ only (Tier 0/1 users skip automatically)

---

## STEP 17: AI ASSISTANT SETUP

### **UI Design**

```
┌─────────────────────────────────────────────────────────────┐
│ d3kOS Initial Setup                              Step 17/22 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│                    🤖 AI Assistant Setup                     │
│                                                              │
│  Enable conversational voice AI with Gemini? (Optional)     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  What you get:                                      │    │
│  │  ✅ Natural language conversations                  │    │
│  │  ✅ Ask complex questions                           │    │
│  │  ✅ Understand context                              │    │
│  │                                                      │    │
│  │  Example:                                            │    │
│  │  You: "Helm, should I be worried about the weather?"│    │
│  │  AI: "There's a storm coming in 2 hours with 25    │    │
│  │      knot winds. I recommend heading back to the   │    │
│  │      marina within the next hour."                  │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  What you need:                                     │    │
│  │  • Google account (Gmail)                           │    │
│  │  • 5 minutes to get free API key                    │    │
│  │  • Internet connection                              │    │
│  │                                                      │    │
│  │  Cost: $0 FREE (1,000 requests/day)                │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌──────────────────────┐  ┌───────────────────────────┐  │
│  │ [Skip for Now]       │  │ [⭐ Set Up Gemini API]   │  │
│  └──────────────────────┘  └───────────────────────────┘  │
│                                                              │
│  ℹ️ You can set this up later in Settings → AI Assistant   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### **User Actions**

**Option 1: User clicks "Skip for Now"**
- Proceed to Step 18 (Configuration Review)
- AI Assistant stays in offline mode (Vosk + Piper + RAG)
- Can set up later in Settings

**Option 2: User clicks "Set Up Gemini API"**
- Proceed to Step 17.1 (Gemini Setup Instructions)

---

## STEP 17.1: GEMINI API - GET YOUR KEY

### **UI Design**

```
┌─────────────────────────────────────────────────────────────┐
│ d3kOS Initial Setup                            Step 17.1/22 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│                  📱 Get Your Gemini API Key                  │
│                                                              │
│  Follow these steps on your phone or computer:              │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Step 1: Go to this website                        │    │
│  │  ┌──────────────────────────────────────────────┐  │    │
│  │  │ https://aistudio.google.com/apikey           │  │    │
│  │  └──────────────────────────────────────────────┘  │    │
│  │  [📋 Copy Link]    [📱 Show QR Code]              │    │
│  │                                                      │    │
│  │  Step 2: Sign in with your Google account          │    │
│  │                                                      │    │
│  │  Step 3: Click "Get API key"                        │    │
│  │                                                      │    │
│  │  Step 4: Click "Create API key in new project"     │    │
│  │                                                      │    │
│  │  Step 5: Copy the API key (looks like this):       │    │
│  │     AIzaSyDH8xK9YpL2mNqR3tUvW4xYz...               │    │
│  │                                                      │    │
│  │  ⚠️ Keep it secret! Don't share publicly.          │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ [Screenshot Guide] - Opens detailed visual guide    │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────┐  ┌───────────────────────────┐  │
│  │ [← Back]             │  │ [I Have My Key →]         │  │
│  └──────────────────────┘  └───────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### **Features**

1. **Copy Link Button** - Copies URL to clipboard for easy sharing to phone
2. **Show QR Code** - Generates QR code of URL for phone scanning
3. **Screenshot Guide** - Opens overlay with visual step-by-step screenshots
4. **Back Button** - Return to Step 17 (skip Gemini setup)
5. **I Have My Key** - Proceed to Step 17.2 (paste API key)

---

## STEP 17.2: GEMINI API - ENTER YOUR KEY

### **UI Design**

```
┌─────────────────────────────────────────────────────────────┐
│ d3kOS Initial Setup                            Step 17.2/22 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│                  🔑 Enter Your Gemini API Key                │
│                                                              │
│  Paste your API key below:                                  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ [Tap here to paste your API key]                     │  │
│  │                                                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ℹ️ Your API key should start with: AIzaSy...              │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Tips:                                              │    │
│  │  • Long-press in the box to paste                   │    │
│  │  • Make sure you copied the entire key              │    │
│  │  • No spaces before or after                        │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  Status: ⚪ Not configured                                  │
│                                                              │
│  ┌──────────────────────┐  ┌───────────────────────────┐  │
│  │ [← Back]             │  │ [Test Connection →]       │  │
│  └──────────────────────┘  └───────────────────────────┘  │
│                                                              │
│  [Skip this step]                                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### **Features**

1. **Auto-focus on text box** - On-screen keyboard appears immediately
2. **Paste detection** - Detects when API key is pasted
3. **Format validation** - Checks if key starts with "AIzaSy" (39-40 chars)
4. **Test Connection** - Proceeds to Step 17.3 (test API key)
5. **Skip** - Skip Gemini setup, continue to Step 18

---

## STEP 17.3: GEMINI API - TEST CONNECTION

### **UI Design (Testing State)**

```
┌─────────────────────────────────────────────────────────────┐
│ d3kOS Initial Setup                            Step 17.3/22 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│                  ⏳ Testing Your API Key...                  │
│                                                              │
│  Please wait while we verify your Gemini API key.           │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │                                                      │    │
│  │          [━━━━━━━━━━━━━━━━━━        ]               │    │
│  │                                                      │    │
│  │          Testing connection to Google...            │    │
│  │                                                      │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  This usually takes 5-10 seconds.                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### **Backend Test**

```javascript
async function testGeminiAPIKey(apiKey) {
    try {
        // Send test query to Gemini API
        const response = await fetch('https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-goog-api-key': apiKey
            },
            body: JSON.stringify({
                contents: [{
                    parts: [{
                        text: "Say 'test successful' if you can read this."
                    }]
                }]
            })
        });

        if (response.ok) {
            return { success: true, message: "API key valid!" };
        } else {
            const error = await response.json();
            return { success: false, message: error.error.message };
        }
    } catch (err) {
        return { success: false, message: "Network error. Check internet connection." };
    }
}
```

---

## STEP 17.3: GEMINI API - TEST SUCCESS

### **UI Design (Success State)**

```
┌─────────────────────────────────────────────────────────────┐
│ d3kOS Initial Setup                            Step 17.3/22 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│                  ✅ API Key Verified!                        │
│                                                              │
│  Your Gemini API is connected and ready to use.             │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │                                                      │    │
│  │                      🎉                              │    │
│  │                                                      │    │
│  │       Conversational AI Enabled!                    │    │
│  │                                                      │    │
│  │  You can now ask complex questions like:            │    │
│  │  • "Helm, what's wrong with the engine?"            │    │
│  │  • "Helm, should I be worried about this weather?"  │    │
│  │  • "Helm, what fish is this?"                       │    │
│  │                                                      │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Free Tier Status:                                  │    │
│  │  • Daily Quota: 1,000 requests                      │    │
│  │  • Resets: Midnight PT                              │    │
│  │  • Cost: $0 FREE                                    │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌───────────────────────────────────────────────────┐     │
│  │ [Continue to Next Step →]                         │     │
│  └───────────────────────────────────────────────────┘     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**After 3 seconds:** Auto-advance to Step 18 (Configuration Review)

---

## STEP 17.3: GEMINI API - TEST FAILED

### **UI Design (Error State)**

```
┌─────────────────────────────────────────────────────────────┐
│ d3kOS Initial Setup                            Step 17.3/22 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│                  ❌ API Key Test Failed                      │
│                                                              │
│  We couldn't verify your Gemini API key.                    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Error:                                             │    │
│  │  Invalid API key. Please check and try again.      │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Common issues:                                     │    │
│  │  • Didn't copy entire key (should be 39-40 chars)  │    │
│  │  • Extra spaces before or after key                │    │
│  │  • API not enabled (see troubleshooting below)     │    │
│  │  • No internet connection                          │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ [📖 Troubleshooting Guide]                         │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌──────────────────────┐  ┌───────────────────────────┐  │
│  │ [← Try Again]        │  │ [Skip for Now →]          │  │
│  └──────────────────────┘  └───────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### **Error Messages**

```javascript
const errorMessages = {
    'API_KEY_INVALID': 'Invalid API key. Please check and try again.',
    'PERMISSION_DENIED': 'API not enabled. Click Troubleshooting Guide below.',
    'QUOTA_EXCEEDED': 'Daily quota exceeded. Try again tomorrow.',
    'NETWORK_ERROR': 'No internet connection. Check WiFi and try again.',
    'TIMEOUT': 'Connection timeout. Check internet and try again.'
};
```

---

## UPDATED ONBOARDING FLOW

**New 22-Step Flow:**

1-16: (Unchanged) Boat and engine info
17: **AI Assistant Setup (Optional)** ← NEW
  - 17.1: Get API Key Instructions ← NEW
  - 17.2: Enter API Key ← NEW
  - 17.3: Test Connection ← NEW
18: Configuration Review (was Step 17)
19: DIP Switch Diagram (was Step 18)
20: QR Code (was Step 19)
21: Finish (was Step 20)

**Total Steps:** 21 (main) + 3 (optional Gemini substeps) = 22 maximum

---

## IMPLEMENTATION DETAILS

### **Files to Modify**

**1. `/var/www/html/onboarding.html`**

Add new step HTML:
```html
<!-- Step 17: AI Assistant Setup -->
<div id="step17" class="step">
    <h2>🤖 AI Assistant Setup</h2>
    <p>Enable conversational voice AI with Gemini? (Optional)</p>

    <div class="info-box">
        <h3>What you get:</h3>
        <ul>
            <li>✅ Natural language conversations</li>
            <li>✅ Ask complex questions</li>
            <li>✅ Understand context</li>
        </ul>
        <p class="example">
            <strong>Example:</strong><br>
            You: "Helm, should I be worried about the weather?"<br>
            AI: "There's a storm coming in 2 hours with 25 knot winds..."
        </p>
    </div>

    <div class="info-box">
        <h3>What you need:</h3>
        <ul>
            <li>Google account (Gmail)</li>
            <li>5 minutes to get free API key</li>
            <li>Internet connection</li>
        </ul>
        <p><strong>Cost: $0 FREE</strong> (1,000 requests/day)</p>
    </div>

    <button onclick="skipGeminiSetup()" class="btn-secondary">Skip for Now</button>
    <button onclick="startGeminiSetup()" class="btn-primary">⭐ Set Up Gemini API</button>

    <p class="hint">ℹ️ You can set this up later in Settings → AI Assistant</p>
</div>

<!-- Step 17.1: Get API Key -->
<div id="step17-1" class="step" style="display: none;">
    <h2>📱 Get Your Gemini API Key</h2>
    <p>Follow these steps on your phone or computer:</p>

    <div class="instruction-box">
        <h3>Step 1: Go to this website</h3>
        <div class="url-box">
            <input type="text" value="https://aistudio.google.com/apikey" readonly id="gemini-url">
            <button onclick="copyGeminiURL()">📋 Copy Link</button>
            <button onclick="showGeminiQR()">📱 Show QR Code</button>
        </div>

        <h3>Step 2-5:</h3>
        <ol>
            <li>Sign in with your Google account</li>
            <li>Click "Get API key"</li>
            <li>Click "Create API key in new project"</li>
            <li>Copy the API key (looks like: AIzaSyDH8xK9YpL2...)</li>
        </ol>

        <p class="warning">⚠️ Keep it secret! Don't share publicly.</p>
    </div>

    <button onclick="showScreenshotGuide()" class="btn-secondary">📸 Screenshot Guide</button>

    <button onclick="backToStep17()" class="btn-secondary">← Back</button>
    <button onclick="gotoStep17_2()" class="btn-primary">I Have My Key →</button>
</div>

<!-- Step 17.2: Enter API Key -->
<div id="step17-2" class="step" style="display: none;">
    <h2>🔑 Enter Your Gemini API Key</h2>
    <p>Paste your API key below:</p>

    <textarea id="gemini-api-key" placeholder="Tap here to paste your API key" rows="3"></textarea>

    <p class="hint">ℹ️ Your API key should start with: AIzaSy...</p>

    <div class="tips-box">
        <h3>Tips:</h3>
        <ul>
            <li>Long-press in the box to paste</li>
            <li>Make sure you copied the entire key</li>
            <li>No spaces before or after</li>
        </ul>
    </div>

    <p id="gemini-status" class="status">Status: ⚪ Not configured</p>

    <button onclick="backToStep17_1()" class="btn-secondary">← Back</button>
    <button onclick="testGeminiAPI()" class="btn-primary">Test Connection →</button>

    <button onclick="skipGeminiSetup()" class="btn-link">Skip this step</button>
</div>

<!-- Step 17.3: Test Connection -->
<div id="step17-3" class="step" style="display: none;">
    <h2 id="test-title">⏳ Testing Your API Key...</h2>

    <div id="test-progress" class="progress-box">
        <div class="progress-bar">
            <div id="progress-fill"></div>
        </div>
        <p id="test-message">Testing connection to Google...</p>
    </div>

    <div id="test-result" style="display: none;">
        <!-- Success or error message will be inserted here -->
    </div>
</div>
```

Add JavaScript functions:
```javascript
function skipGeminiSetup() {
    // Save "skipped" state
    localStorage.setItem('gemini-setup-skipped', 'true');
    // Go to step 18 (Configuration Review)
    show(18);
}

function startGeminiSetup() {
    show(17.1); // Show Step 17.1
}

function copyGeminiURL() {
    const url = document.getElementById('gemini-url');
    url.select();
    document.execCommand('copy');
    alert('Link copied! Paste it in your phone/computer browser.');
}

function showGeminiQR() {
    // Generate QR code of Gemini API URL
    const qrDiv = document.getElementById('gemini-qr');
    qrDiv.innerHTML = '';
    new QRCode(qrDiv, {
        text: 'https://aistudio.google.com/apikey',
        width: 300,
        height: 300
    });
    // Show modal with QR code
    document.getElementById('qr-modal').style.display = 'block';
}

function showScreenshotGuide() {
    // Open overlay with step-by-step screenshots
    document.getElementById('screenshot-guide-modal').style.display = 'block';
}

function gotoStep17_2() {
    show(17.2);
    // Auto-focus on API key textarea
    setTimeout(() => {
        document.getElementById('gemini-api-key').focus();
    }, 500);
}

async function testGeminiAPI() {
    const apiKey = document.getElementById('gemini-api-key').value.trim();

    // Validate format
    if (!apiKey.startsWith('AIzaSy') || apiKey.length < 39) {
        alert('Invalid API key format. Make sure you copied the entire key.');
        return;
    }

    // Show testing step
    show(17.3);

    // Animate progress bar
    let progress = 0;
    const progressBar = document.getElementById('progress-fill');
    const interval = setInterval(() => {
        progress += 10;
        progressBar.style.width = progress + '%';
        if (progress >= 90) clearInterval(interval);
    }, 500);

    try {
        // Test API key with actual Gemini API call
        const response = await fetch('https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-goog-api-key': apiKey
            },
            body: JSON.stringify({
                contents: [{
                    parts: [{
                        text: "Say 'test successful' if you can read this."
                    }]
                }]
            })
        });

        clearInterval(interval);
        progressBar.style.width = '100%';

        if (response.ok) {
            // SUCCESS!
            showTestSuccess(apiKey);
        } else {
            // FAILED
            const error = await response.json();
            showTestError(error.error.message);
        }

    } catch (err) {
        clearInterval(interval);
        showTestError('Network error. Check internet connection.');
    }
}

function showTestSuccess(apiKey) {
    // Save API key to config
    fetch('/gemini/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: apiKey, enabled: true })
    });

    // Update UI
    document.getElementById('test-title').innerHTML = '✅ API Key Verified!';
    document.getElementById('test-progress').style.display = 'none';
    document.getElementById('test-result').style.display = 'block';
    document.getElementById('test-result').innerHTML = `
        <div class="success-box">
            <h2>🎉</h2>
            <h3>Conversational AI Enabled!</h3>
            <p>You can now ask complex questions like:</p>
            <ul>
                <li>"Helm, what's wrong with the engine?"</li>
                <li>"Helm, should I be worried about this weather?"</li>
                <li>"Helm, what fish is this?"</li>
            </ul>
            <div class="quota-info">
                <h4>Free Tier Status:</h4>
                <ul>
                    <li>Daily Quota: 1,000 requests</li>
                    <li>Resets: Midnight PT</li>
                    <li>Cost: $0 FREE</li>
                </ul>
            </div>
        </div>
        <button onclick="show(18)" class="btn-primary">Continue to Next Step →</button>
    `;

    // Auto-advance after 3 seconds
    setTimeout(() => {
        show(18);
    }, 3000);
}

function showTestError(errorMessage) {
    // Update UI
    document.getElementById('test-title').innerHTML = '❌ API Key Test Failed';
    document.getElementById('test-progress').style.display = 'none';
    document.getElementById('test-result').style.display = 'block';
    document.getElementById('test-result').innerHTML = `
        <div class="error-box">
            <h3>Error:</h3>
            <p>${errorMessage}</p>
        </div>
        <div class="tips-box">
            <h3>Common issues:</h3>
            <ul>
                <li>Didn't copy entire key (should be 39-40 chars)</li>
                <li>Extra spaces before or after key</li>
                <li>API not enabled (see troubleshooting below)</li>
                <li>No internet connection</li>
            </ul>
        </div>
        <button onclick="openTroubleshooting()" class="btn-secondary">📖 Troubleshooting Guide</button>
        <button onclick="show(17.2)" class="btn-secondary">← Try Again</button>
        <button onclick="skipGeminiSetup()" class="btn-primary">Skip for Now →</button>
    `;
}
```

**2. Update Step Numbers**

All existing steps 17-20 → renumber to 18-21

---

## SETTINGS PAGE INTEGRATION

**After onboarding, users can manage Gemini API:**

**Settings → AI Assistant:**
```
┌─────────────────────────────────────────────────────────────┐
│ AI Assistant Settings                                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Gemini API Configuration                                   │
│  ────────────────────────                                   │
│                                                              │
│  Status: ✅ Connected                                       │
│  Quota Today: 47 / 1,000 requests                          │
│                                                              │
│  API Key: AIzaSyDH8xK9YpL2... [Show] [Change]              │
│                                                              │
│  [📖 Setup Guide]   [🔧 Test Connection]                   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Don't have an API key?                              │  │
│  │  [Get Free Gemini API Key]                           │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  [ ] Fallback to offline mode when quota exceeded          │
│  [✓] Show quota warnings at 80% and 95%                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## TIER DETECTION

**Automatic Tier Detection:**
```javascript
// Check user's tier
const tier = parseInt(localStorage.getItem('d3kos-tier') || '0');

// Show/hide Gemini setup based on tier
if (tier >= 2) {
    // Show Step 17 (Gemini setup)
    document.getElementById('step17').style.display = 'block';
} else {
    // Skip Step 17 for Tier 0/1
    // Go directly from Step 16 → Step 18
    skipGeminiSetup();
}
```

---

## USER FLOW DIAGRAM

```
Step 16: Boat Origin
    ↓
Check Tier
    ├─ Tier 0/1: Skip to Step 18 (Configuration Review)
    └─ Tier 2/3: Show Step 17 (AI Assistant Setup)
        ↓
    Step 17: AI Assistant Setup (Optional)
        ├─ Skip for Now → Step 18
        └─ Set Up Gemini API → Step 17.1
            ↓
        Step 17.1: Get API Key Instructions
            ├─ Back → Step 17
            └─ I Have My Key → Step 17.2
                ↓
            Step 17.2: Enter API Key
                ├─ Back → Step 17.1
                ├─ Skip → Step 18
                └─ Test Connection → Step 17.3
                    ↓
                Step 17.3: Test Connection
                    ├─ Success → Auto-advance to Step 18 (3s)
                    └─ Failed → Try Again or Skip
                        ↓
Step 18: Configuration Review
Step 19: DIP Switch Diagram
Step 20: QR Code
Step 21: Finish
```

---

## SUMMARY

**Changes Required:**
1. Add Step 17, 17.1, 17.2, 17.3 to onboarding.html
2. Renumber existing steps 17-20 → 18-21
3. Add tier detection logic (Tier 2+ only)
4. Add Gemini API test function
5. Update Settings → AI Assistant page
6. Create troubleshooting guide modal

**Files to Modify:**
- `/var/www/html/onboarding.html` - Add new steps
- `/var/www/html/settings-ai.html` - Add Gemini config
- `/opt/d3kos/services/ai/gemini_proxy.py` - NEW service (port 8099)
- `/etc/nginx/sites-enabled/default` - Add `/gemini/` proxy

**Testing Checklist:**
- ✅ Tier 0/1 users skip Gemini setup automatically
- ✅ Tier 2/3 users see Gemini setup option
- ✅ "Skip for Now" works correctly
- ✅ API key paste detection works
- ✅ API key validation works
- ✅ Test connection works (success/failure)
- ✅ Auto-advance after success works
- ✅ Error messages are clear
- ✅ Can access setup later in Settings
- ✅ QR code generation works
- ✅ Screenshot guide displays correctly

**User Experience:**
- **Best case:** 5 minutes (already have Gmail, quick setup)
- **Worst case:** Skip entirely, set up later (0 minutes)
- **Average case:** 8 minutes (create Gmail + get API key)

---

**END OF DOCUMENT**
