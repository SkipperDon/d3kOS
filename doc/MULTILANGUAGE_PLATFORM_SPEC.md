# d3kOS Multi-Language Platform Specification
**Version:** 1.0 | **Created:** 2026-03-09 | **Target:** v1.1
**Author:** Skipper Don — AtMyBoat.com

---

## What This Is

Multi-language in d3kOS is not UI translation. It is a 6-layer platform stack. A French captain must be able to:
- Say "Helm, quel est mon régime moteur?" and receive a spoken French answer
- Record a voice boat log entry in French and read it back in French
- Type a message to the AI assistant in French using a French keyboard
- See all UI labels, alerts, and status messages in French

All six layers must work together. Translating button labels while leaving the voice pipeline in English is not multilingual — it is a cosmetic patch.

---

## Architecture: Six Layers

```
Layer 0 — UI Display         (translation JSON + data-i18n on all pages)
Layer 1 — Speech Input       (Whisper STT replaces Vosk for post-wake transcription)
Layer 2 — Speech Output      (Piper per-language models + espeak-ng fallback)
Layer 3 — AI Response        (query_handler reads language, injects into all AI calls)
Layer 4 — Keyboard Input     (per-language virtual keyboard + fcitx5 for RTL/CJK)
Layer 5 — Boat Log           (automatic once Layers 1 + 4 complete)
```

---

## Layer 0 — UI Display

### What's Done
- 18 JSON translation files at `/opt/d3kos/config/i18n/`
- Language API at port 8101
- `language-menu.html` selector page
- `data-i18n` wired on 6 pages: `index.html`, `dashboard.html`, `navigation.html`, `boatlog.html`, `settings.html`, `onboarding.html`

### What Remains
Wire 14 remaining pages (add `data-i18n` attributes + JS loader on each):
- `weather.html`, `marine-vision.html`, `helm.html`, `ai-assistant.html`
- `charts.html`, `manuals.html`, `manual-search.html`, `history.html`
- `settings-network.html`, `settings-data.html`, `settings-healing.html`
- `settings-simulator.html`, `remote-access.html`, `upload-manual.html`

Expand translation keys in all 18 JSON files to cover every label on those 14 pages.

### Arabic RTL
When `lang=ar`, every page must execute:
```javascript
document.documentElement.setAttribute('dir', 'rtl');
document.documentElement.setAttribute('lang', 'ar');
```
CSS must not break on layout flip — test all pages in RTL mode.

### Font Requirements
```bash
sudo apt install fonts-noto fonts-noto-cjk fonts-noto-extra
```
Required for: Arabic, Chinese, Japanese, Greek, Cyrillic (Ukrainian). Without these, characters render as boxes.

---

## Layer 1 — Speech-to-Text

### Problem
Vosk uses an English-only grammar model. Every spoken command is forced through English transcription regardless of language setting. A French captain's voice commands cannot be understood.

### Solution: Whisper
- Model: `whisper-small` (244MB) — handles 99 languages
- Wake word: stays in Vosk (English "Helm" — no change)
- Post-wake transcription: switches to Whisper with `language=` from `onboarding.json`
- Pi 4B performance: ~3–6 seconds per transcription (acceptable for post-wake)

### Files to Modify

**New file: `/opt/d3kos/services/ai/whisper_transcribe.py`**
```python
# Load model once at import time
# Read language from /opt/d3kos/config/onboarding.json
# Expose: transcribe(wav_path: str) -> str
```

**`voice-assistant-hybrid.py` — `listen()` function:**
- Keep Vosk for wake-word detection
- Replace the post-wake transcription block with `whisper_transcribe.transcribe(wav_path)`

**`boatlog-export-api.py` — `transcribe_audio()` function:**
- Replace `vosk-transcribe` subprocess call with `whisper_transcribe.transcribe(audio_path)`

### Model Deployment
```bash
# Install whisper Python package
pip install openai-whisper

# On first run, model auto-downloads to ~/.cache/whisper/
# Pre-download on Pi during deployment:
python3 -c "import whisper; whisper.load_model('small')"
# Move to permanent location:
# /opt/d3kos/models/whisper/small.pt
```

---

## Layer 2 — Text-to-Speech

### Problem
Only one Piper model deployed: `en_US-amy-medium.onnx`. All responses are spoken in English regardless of language setting.

### Solution: Per-Language Piper Models + espeak-ng Fallback

**Languages with Piper official models:**

| Language | Piper Model | Size |
|----------|------------|------|
| French | `fr_FR-upmc-medium` | ~63MB |
| German | `de_DE-thorsten-medium` | ~63MB |
| Spanish | `es_ES-sharvard-medium` | ~63MB |
| Italian | `it_IT-riccardo-x_low` | ~32MB |
| Dutch | `nl_NL-mls-medium` | ~63MB |
| Portuguese | `pt_PT-tugao-medium` | ~63MB |
| Ukrainian | `uk_UA-lada-x_low` | ~32MB |
| Arabic | `ar_JO-kareem-medium` | ~63MB |

**Languages using espeak-ng fallback** (no Piper model available):
Swedish, Norwegian, Danish, Finnish, Croatian, Turkish, Greek, Chinese, Japanese

espeak-ng voice codes:
```
sv → sv  | no → no  | da → da  | fi → fi
hr → hr  | tr → tr  | el → el  | zh → zh
ja → ja
```

### Files to Modify

**`voice-assistant-hybrid.py`:**
```python
# On startup: read language from onboarding.json
# tts_speak(text: str, language: str) abstraction:
#   - if language in PIPER_MODELS: use piper with model path
#   - else: use espeak-ng with language code
```

### Model Deployment
```bash
# Piper model files go to:
/opt/d3kos/models/piper/<lang_code>-<model_name>.onnx
/opt/d3kos/models/piper/<lang_code>-<model_name>.onnx.json

# espeak-ng install (if not present):
sudo apt install espeak-ng
```

---

## Layer 3 — AI Response Language

### Problem
`query_handler.py` has zero language awareness. Gemini responses, RAG answers, and all hardcoded rule-based strings (RPM, temperature, pressure) always return English.

### Files to Modify

**`query_handler.py`:**

1. On startup, read language from `onboarding.json`:
```python
with open('/opt/d3kos/config/onboarding.json') as f:
    prefs = json.load(f)
    self.language = prefs.get('language', 'en')
    self.language_name = LANGUAGE_NAMES.get(self.language, 'English')
```

2. Inject into Gemini system prompt:
```python
system_prompt = f"""You are Helm, a marine AI assistant on a boat running d3kOS.
The user speaks {self.language_name}. Always respond in {self.language_name}.
Use correct marine terminology for {self.language_name}. Keep responses concise.
"""
```

3. Replace hardcoded English strings in rule-based responses with i18n lookups:
```python
# Instead of: return f"Your RPM is {rpm}"
# Use: return self.i18n['responses']['rpm'].format(value=rpm)
```
Add a `responses` section to all 18 i18n JSON files with templated strings for engine data, navigation, alerts.

4. RAG results: add to Gemini prompt — "The following technical information was retrieved from the boat's manuals. Translate any relevant details into {language_name} in your response."

### Language Name Map
```python
LANGUAGE_NAMES = {
    'en': 'English', 'fr': 'French', 'de': 'German', 'es': 'Spanish',
    'it': 'Italian', 'nl': 'Dutch', 'pt': 'Portuguese', 'sv': 'Swedish',
    'no': 'Norwegian', 'da': 'Danish', 'fi': 'Finnish', 'hr': 'Croatian',
    'tr': 'Turkish', 'el': 'Greek', 'ar': 'Arabic', 'zh': 'Chinese',
    'ja': 'Japanese', 'uk': 'Ukrainian'
}
```

---

## Layer 4 — Keyboard and Text Input

### Pre-Condition
Fix the existing on-screen keyboard bug (documented in `memory/keyboard-scroll-investigation.md`) before implementing multilingual layouts. The keyboard must work in English first.

### Latin-script Languages
Languages: fr, de, es, it, nl, sv, no, da, fi, pt, hr, tr, uk

Implement per-language virtual keyboard layouts in the on-screen keyboard component. Key differences:
- AZERTY layout: fr
- QWERTZ layout: de, hr
- Additional keys: é, à, ü, ö, ñ, ø, å, ç, ğ, і, and others
- Load layout based on `onboarding.json` language on page startup

### Arabic (RTL)
```bash
sudo apt install fcitx5 fcitx5-arabic
```

Configure labwc to use fcitx5:
```bash
# /home/d3kos/.config/environment.d/input.conf
GTK_IM_MODULE=fcitx
QT_IM_MODULE=fcitx
XMODIFIERS=@im=fcitx
```

All text input fields when `lang=ar`:
```html
<input type="text" dir="rtl" lang="ar">
<textarea dir="rtl" lang="ar"></textarea>
```

### CJK — Chinese and Japanese (v1.2+ milestone)
Not v1.1 scope. Voice input (Layer 1 Whisper) is the practical path for CJK on a boat touchscreen. Typed CJK input requires:
```bash
sudo apt install fcitx5 fcitx5-chinese-addons  # Chinese Pinyin
sudo apt install fcitx5 fcitx5-mozc            # Japanese
```

---

## Layer 5 — Boat Log in the User's Language

### Automatic Dependencies
- Voice notes in the user's language: Layer 1 (Whisper) handles this automatically
- Typed entries in the user's language: Layer 4 (keyboard) handles this
- Display rendering: Layer 0 (Noto fonts) handles this
- Export (CSV/JSON): UTF-8 already — no changes needed

### Manual Test Required
Once Layers 1 and 4 are complete:
- French captain records voice note → Whisper transcribes in French → stored and displayed in French
- German captain types a log entry in German → stored and displayed correctly
- Arabic entry stored and displayed right-to-left with correct script

---

## Testing Checklist (per language)

For each language, verify the full end-to-end chain:
- [ ] UI labels display in language on all 20 pages
- [ ] Voice command spoken in language → correctly transcribed by Whisper
- [ ] Helm responds in correct language (spoken)
- [ ] AI assistant text response in correct language
- [ ] Rule-based engine data response in correct language
- [ ] Boat log voice note transcribed in correct language
- [ ] Keyboard supports language characters
- [ ] Arabic: all pages display RTL, input fields RTL
- [ ] CJK: Noto fonts render correctly (typed input deferred to v1.2)

---

## Delivery Order

1. **Layer 1 + 2** (Whisper + Piper) — voice pipeline, no UI dependencies
2. **Layer 3** (query_handler language) — testable once Layer 1 works
3. **Layer 0** (14 remaining pages) — parallel, no voice dependency
4. **Layer 4** (keyboard) — after existing keyboard bug is resolved
5. **Layer 5** (boat log) — automatic once 1 + 4 done

**Minimum viable multilingual release:** Layers 1 + 2 + 3 + 5
A captain can speak their language, hear responses in their language, and record their log in their language. UI translation is the polish layer that completes the experience.

---

*Spec authored 2026-03-09 — AtMyBoat.com / d3kOS v1.1*
