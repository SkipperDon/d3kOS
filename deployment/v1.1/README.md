# d3kOS v1.1 — Multi-Language Platform

**Status:** Planning
**Priority:** REQUIRED for v1.1 release
**Full architectural spec:** `../../doc/MULTILANGUAGE_PLATFORM_SPEC.md`
**Checklist:** `../../PROJECT_CHECKLIST.md` → v1.1 section

---

## What v1.1 Delivers

A captain operates d3kOS entirely in their own language:
- Speaks to Helm in their language → Helm responds in their language
- Records boat log by voice → transcribed in their language
- Types in helm/AI assistant in their language
- Sees all UI in their language

18 languages: English, French, German, Spanish, Italian, Dutch, Portuguese, Swedish, Norwegian, Danish, Finnish, Croatian, Turkish, Greek, Arabic, Chinese, Japanese, Ukrainian

---

## Six Layers — Build Order

| # | Layer | Key Change | Status |
|---|-------|-----------|--------|
| 0 | UI Display | Wire 14 remaining pages with data-i18n + expand JSON keys | 🔄 Partial |
| 1 | Speech Input | Replace Vosk with Whisper-small for post-wake transcription | Not Started |
| 2 | Speech Output | Per-language Piper models + espeak-ng fallback | Not Started |
| 3 | AI Response Language | Inject language into all Gemini/RAG/rule-based responses | Not Started |
| 4 | Keyboard Input | Per-language layouts + fcitx5 for Arabic (CJK deferred to v1.2) | Not Started |
| 5 | Boat Log | Automatic once Layers 1 + 4 complete | Not Started |

**Minimum viable multilingual:** Layers 1 + 2 + 3 + 5

---

## Files This Version Touches

| File | Layer | Change |
|------|-------|--------|
| `services/ai/whisper_transcribe.py` | 1 | NEW — Whisper helper, reads language from onboarding.json |
| `services/ai/voice-assistant-hybrid.py` | 1, 2 | Replace Vosk transcription block, add TTS language routing |
| `services/boatlog/boatlog-export-api.py` | 1 | Replace `transcribe_audio()` Vosk with Whisper |
| `services/ai/query_handler.py` | 3 | Read language on startup, inject into all AI calls, i18n rule responses |
| `config/i18n/*.json` (all 18) | 0, 3 | Add `responses` section for rule-based strings, expand page keys |
| `var/www/html/*.html` (14 pages) | 0 | Add data-i18n attributes + JS loader |
| `models/whisper/small.pt` | 1 | NEW — Whisper model file (244MB) |
| `models/piper/<lang>-*.onnx` | 2 | NEW — Per-language Piper model files |

---

## Pre-Conditions Before Starting

1. Keyboard investigation resolved (`memory/keyboard-scroll-investigation.md`) — Layer 4 depends on this
2. Layer 0 UI wiring can start immediately — no voice dependency
3. Layers 1 + 2 can start immediately and run in parallel
4. Layer 3 testable once Layer 1 is working

---

## Feature Specs (add as work is planned)

- `whisper-stt/` — Whisper STT integration spec
- `piper-tts-multilang/` — Per-language TTS spec
- `ai-response-language/` — query_handler language injection spec
- `keyboard-multilang/` — Per-language keyboard layouts spec
- `ui-translation-complete/` — Remaining 14-page wiring spec
