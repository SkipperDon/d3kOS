# HELM-OS AI INFERENCE ENGINE

**Version**: 2.0
**Date**: February 6, 2026
**Based on**: MASTER_SYSTEM_SPEC.md v2.0
**Audience**: Developers
**Tier**: 2+ (Voice features)

---

## TABLE OF CONTENTS

1. [AI Architecture Overview](#ai-architecture-overview)
2. [Voice Pipeline](#voice-pipeline)
3. [Wake Word Detection](#wake-word-detection)
4. [Speech-to-Text (STT)](#speech-to-text-stt)
5. [Language Model (LLM)](#language-model-llm)
6. [Text-to-Speech (TTS)](#text-to-speech-tts)
7. [Anomaly Detection](#anomaly-detection)
8. [Command Parsing](#command-parsing)
9. [Performance Optimization](#performance-optimization)
10. [Model Management](#model-management)
11. [Troubleshooting](#troubleshooting)

---

## 1. AI ARCHITECTURE OVERVIEW

### 1.1 AI Components

d3kOS uses multiple AI models for offline intelligence:

| Component | Technology | Size | RAM | Purpose | Latency |
|-----------|-----------|------|-----|---------|---------|
| **Wake Word** | PocketSphinx | 10MB | 50MB | Detect "Helm" | < 500ms |
| **STT** | Vosk | 50MB | 200MB | Speech → Text | < 1s |
| **LLM** | Phi-2 (Q4_K_M) | 5GB | 3GB | AI reasoning | < 1s |
| **TTS** | Piper | 20MB | 100MB | Text → Speech | < 500ms |
| **Anomaly Detection** | SPC Algorithm | N/A | < 10MB | Engine health | < 100ms |

**Total RAM Requirements**:
- Base: ~350MB (without LLM)
- With LLM: ~3.3GB
- Recommended: 8GB Pi 4 (4GB can work with swap)

### 1.2 AI System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERACTION                      │
│               Microphone → Speaker                       │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                  VOICE PIPELINE                          │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐│
│  │PocketSpx │→ │  Vosk    │→ │  Phi-2   │→ │ Piper   ││
│  │(Wake)    │  │  (STT)   │  │  (LLM)   │  │ (TTS)   ││
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘│
│       ↓             ↓             ↓             ↓       │
│    <500ms         <1s           <1s          <500ms    │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│               CONTEXT & DATA ACCESS                      │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ Signal K │  │ Engine   │  │  System  │             │
│  │  Data    │  │ Baseline │  │  Status  │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└─────────────────────────────────────────────────────────┘
```

### 1.3 Inference Strategies

**Hot-Path (Tier 2+ Required)**:
1. Continuous wake word detection (always listening)
2. On-demand STT (after wake word)
3. Cached LLM context (boat status pre-loaded)
4. Streaming TTS (start speaking before full generation)

**Optimization Goals**:
- Total latency: < 2 seconds (wake word to audio output)
- CPU usage: < 50% sustained
- Memory footprint: < 4GB
- 100% offline operation

---

## 2. VOICE PIPELINE

### 2.1 Complete Voice Flow

```
┌────────────────────────────────────────────────────────┐
│  Step 1: Continuous Wake Word Detection               │
│  PocketSphinx listening for "Helm"                     │
│  CPU: 5-10%, RAM: 50MB                                 │
└─────────────┬──────────────────────────────────────────┘
              │ "Helm" detected
              ▼
┌────────────────────────────────────────────────────────┐
│  Step 2: Audio Capture                                │
│  Record 5 seconds of audio (or until silence)         │
│  Format: WAV, 16kHz, 16-bit, mono                     │
└─────────────┬──────────────────────────────────────────┘
              │ recording_1234.wav
              ▼
┌────────────────────────────────────────────────────────┐
│  Step 3: Speech-to-Text (Vosk)                        │
│  Transcribe audio to text                             │
│  Latency: ~1 second for 5s audio                      │
└─────────────┬──────────────────────────────────────────┘
              │ "what's the engine status"
              ▼
┌────────────────────────────────────────────────────────┐
│  Step 4: Command Classification                       │
│  ├─ Direct command (known pattern) → Execute          │
│  └─ General query → Send to LLM                       │
└─────────────┬──────────────────────────────────────────┘
              │ Command: "engine_status"
              ▼
┌────────────────────────────────────────────────────────┐
│  Step 5: Data Retrieval                               │
│  Query Signal K for current engine metrics            │
│  {rpm: 3200, oilPressure: 45, temp: 180}              │
└─────────────┬──────────────────────────────────────────┘
              │ Current metrics
              ▼
┌────────────────────────────────────────────────────────┐
│  Step 6: Response Generation (Phi-2 or Template)      │
│  ├─ Template: "Engine running at 3200 RPM..."         │
│  └─ LLM: Generate contextual response                 │
└─────────────┬──────────────────────────────────────────┘
              │ Response text
              ▼
┌────────────────────────────────────────────────────────┐
│  Step 7: Text-to-Speech (Piper)                       │
│  Convert text to audio waveform                       │
│  Latency: ~500ms for 20 words                         │
└─────────────┬──────────────────────────────────────────┘
              │ response_audio.wav
              ▼
┌────────────────────────────────────────────────────────┐
│  Step 8: Audio Playback                               │
│  Play through Anker PowerConf S330 speaker            │
└────────────────────────────────────────────────────────┘
```

### 2.2 Service Implementation

**Systemd Service**: `/etc/systemd/system/d3kos-voice.service`

```ini
[Unit]
Description=Helm Voice Assistant
After=network.target sound.target

[Service]
Type=simple
User=pi
WorkingDirectory=/opt/d3kos/services/voice
ExecStart=/usr/bin/python3 /opt/d3kos/services/voice/assistant.py
Restart=always
RestartSec=10
Environment="PYTHONUNBUFFERED=1"
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Main Service Script**: `/opt/d3kos/services/voice/assistant.py`

```python
#!/usr/bin/env python3
import os
import sys
import time
import json
import logging
from pathlib import Path

# Import voice components
from wake_word import WakeWordDetector
from stt import SpeechToText
from llm import LanguageModel
from tts import TextToSpeech
from command_parser import CommandParser
from data_access import DataAccess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/opt/d3kos/logs/voice.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class VoiceAssistant:
    def __init__(self):
        logger.info("Initializing Helm Voice Assistant...")

        # Check license tier
        self.tier = self.check_tier()
        if self.tier < 2:
            logger.error("Voice assistant requires Tier 2+")
            sys.exit(1)

        # Initialize components
        self.wake_word = WakeWordDetector()
        self.stt = SpeechToText()
        self.llm = LanguageModel()
        self.tts = TextToSpeech()
        self.parser = CommandParser()
        self.data = DataAccess()

        logger.info("Voice assistant ready")

    def check_tier(self):
        license_file = Path('/opt/d3kos/config/license.json')
        if license_file.exists():
            with open(license_file) as f:
                return json.load(f).get('tier', 0)
        return 0

    def run(self):
        logger.info("Starting voice assistant loop")

        while True:
            try:
                # Step 1: Wait for wake word
                logger.debug("Listening for wake word...")
                if self.wake_word.detect():
                    logger.info("Wake word detected!")
                    self.handle_command()

            except KeyboardInterrupt:
                logger.info("Shutting down...")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                time.sleep(1)

    def handle_command(self):
        start_time = time.time()

        # Step 2: Capture audio
        logger.debug("Capturing audio...")
        audio_file = self.capture_audio()

        # Step 3: Speech-to-text
        logger.debug("Transcribing audio...")
        text = self.stt.transcribe(audio_file)
        logger.info(f"Transcription: {text}")

        # Clean up audio file
        os.remove(audio_file)

        # Step 4: Parse command
        command = self.parser.parse(text)
        logger.info(f"Command: {command}")

        # Step 5: Execute command or query LLM
        if command['type'] == 'direct':
            response = self.execute_command(command)
        else:
            response = self.llm_query(text, command)

        logger.info(f"Response: {response}")

        # Step 6: Text-to-speech
        logger.debug("Generating speech...")
        audio = self.tts.synthesize(response)

        # Step 7: Play audio
        self.play_audio(audio)

        elapsed = time.time() - start_time
        logger.info(f"Total response time: {elapsed:.2f}s")

    def capture_audio(self, duration=5):
        """Capture audio from microphone"""
        import wave
        import pyaudio

        audio_file = f"/opt/d3kos/data/voice/recording_{int(time.time())}.wav"

        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000

        p = pyaudio.PyAudio()
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )

        logger.debug(f"Recording for {duration} seconds...")
        frames = []

        for i in range(0, int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        # Save to file
        wf = wave.open(audio_file, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        return audio_file

    def execute_command(self, command):
        """Execute direct command"""
        if command['action'] == 'engine_status':
            return self.get_engine_status()
        elif command['action'] == 'check_anomalies':
            return self.check_anomalies()
        elif command['action'] == 'open_opencpn':
            os.system('opencpn &')
            return "Opening OpenCPN"
        else:
            return "Command not recognized"

    def llm_query(self, text, context):
        """Query LLM for general questions"""
        # Get current boat status
        status = self.data.get_current_status()

        # Build prompt
        prompt = self.build_prompt(text, status)

        # Query LLM
        response = self.llm.generate(prompt)

        return response

    def get_engine_status(self):
        """Get current engine status"""
        status = self.data.get_engine_metrics()

        rpm = status.get('rpm', 0)
        temp = status.get('temperature', 0)
        pressure = status.get('oilPressure', 0)

        return f"Engine running at {rpm} RPM. " \
               f"Temperature {temp} degrees. " \
               f"Oil pressure {pressure} PSI. " \
               f"All systems normal."

    def check_anomalies(self):
        """Check for recent anomalies"""
        anomalies = self.data.get_anomalies(limit=5)

        if not anomalies:
            return "No anomalies detected. All systems operating normally."

        count = len(anomalies)
        latest = anomalies[0]

        return f"{count} anomalies detected. " \
               f"Most recent: {latest['message']}"

    def build_prompt(self, query, status):
        """Build LLM prompt with context"""
        prompt = f"""You are Helm, a concise marine assistant. Current boat status:
- Engine RPM: {status.get('rpm', 'N/A')}
- Oil Pressure: {status.get('oilPressure', 'N/A')} PSI
- Coolant Temperature: {status.get('temperature', 'N/A')}°F
- Fuel Level: {status.get('fuelLevel', 'N/A')}%
- Battery Voltage: {status.get('voltage', 'N/A')}V

User: {query}

Helm: """
        return prompt

    def play_audio(self, audio_file):
        """Play audio file through speaker"""
        import subprocess
        subprocess.run(['aplay', audio_file],
                      stdout=subprocess.DEVNULL,
                      stderr=subprocess.DEVNULL)

if __name__ == '__main__':
    assistant = VoiceAssistant()
    assistant.run()
```

---

## 3. WAKE WORD DETECTION

### 3.1 PocketSphinx Configuration

**Wake Word**: "Helm"

**Technology**: CMU Sphinx (PocketSphinx)
- Lightweight keyword spotting
- Low CPU usage (5-10%)
- Continuous listening
- False positive rate: < 1%

### 3.2 Implementation

**Wake Word Detector**: `/opt/d3kos/services/voice/wake_word.py`

```python
import os
from pocketsphinx import LiveSpeech, get_model_path

class WakeWordDetector:
    def __init__(self):
        model_path = get_model_path()

        # Custom wake word model
        self.speech = LiveSpeech(
            verbose=False,
            sampling_rate=16000,
            buffer_size=2048,
            no_search=False,
            full_utt=False,
            hmm=os.path.join(model_path, 'en-us'),
            lm=False,
            keyphrase='helm',
            kws_threshold=1e-40  # Sensitivity threshold
        )

    def detect(self):
        """Wait for wake word detection"""
        for phrase in self.speech:
            if 'helm' in str(phrase).lower():
                return True
        return False
```

### 3.3 Sensitivity Tuning

**Threshold Parameter**: `kws_threshold`

| Value | Sensitivity | False Positives | Missed Detections |
|-------|-------------|-----------------|-------------------|
| 1e-20 | Very High | High (10%) | Very Low (1%) |
| 1e-30 | High | Medium (5%) | Low (2%) |
| 1e-40 | **Optimal** | Low (1%) | Low (3%) |
| 1e-50 | Low | Very Low (0.5%) | Medium (5%) |
| 1e-60 | Very Low | Minimal (<0.1%) | High (10%) |

**Recommended**: `1e-40` (good balance for marine environment with engine noise)

### 3.4 Custom Wake Word Training

**Create Custom Acoustic Model**:

```bash
# Install sphinxtrain
sudo apt install sphinxtrain

# Create pronunciation dictionary
echo "helm HH EH L M" > helm.dict

# Create language model
cat > helm.corpus <<EOF
helm
helm helm
helm what's the engine status
EOF

# Generate language model
sphinx_lm_convert -i helm.corpus -o helm.lm

# Move to model directory
sudo cp helm.* /opt/d3kos/models/pocketsphinx/
```

---

## 4. SPEECH-TO-TEXT (STT)

### 4.1 Vosk Configuration

**Model**: `vosk-model-small-en-us-0.15`
- Size: 50MB
- Languages: English (US)
- Vocabulary: 128k words
- Accuracy: 85-90% (general speech), 90-95% (marine commands)

### 4.2 Implementation

**STT Module**: `/opt/d3kos/services/voice/stt.py`

```python
import json
import wave
from vosk import Model, KaldiRecognizer

class SpeechToText:
    def __init__(self, model_path="/opt/d3kos/models/vosk"):
        self.model = Model(model_path)
        self.sample_rate = 16000

    def transcribe(self, audio_file):
        """Transcribe audio file to text"""
        wf = wave.open(audio_file, "rb")

        # Verify format
        if wf.getnchannels() != 1 or \
           wf.getsampwidth() != 2 or \
           wf.getframerate() != self.sample_rate:
            raise ValueError(f"Audio must be mono, 16-bit, {self.sample_rate}Hz")

        # Create recognizer
        rec = KaldiRecognizer(self.model, self.sample_rate)
        rec.SetWords(True)

        # Process audio
        results = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break

            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                results.append(result)

        # Final result
        final = json.loads(rec.FinalResult())
        results.append(final)

        # Extract text
        text = " ".join([r.get('text', '') for r in results])

        return text.strip()
```

### 4.3 Performance Optimization

**Real-Time Factor (RTF)**:
- Target: < 0.5 (2x faster than real-time)
- Pi 4 Performance: 0.3-0.5 RTF
- 5 seconds of audio → 1.5-2.5 seconds processing

**Optimization Techniques**:
1. Use small model (50MB) instead of large (1.8GB)
2. Process in chunks (4000 frames)
3. Single-threaded (avoid context switching)
4. Preload model at service startup

### 4.4 Marine Vocabulary Enhancement

**Custom Dictionary**: `/opt/d3kos/models/vosk/marine-words.txt`

```
helm
opencpn
nmea
signalk
chartplotter
tachometer
coolant
anomaly
benchmark
```

**Add to Model**:
```python
# Add custom words to recognizer
rec = KaldiRecognizer(model, sample_rate)
rec.SetWords(True)

# Load custom vocabulary
with open('/opt/d3kos/models/vosk/marine-words.txt') as f:
    words = [line.strip() for line in f]
    rec.SetGrammar(json.dumps(words))
```

---

## 5. LANGUAGE MODEL (LLM)

### 5.1 Phi-2 Overview

**Model**: Microsoft Phi-2 (2.7B parameters)
- Quantization: Q4_K_M (4-bit)
- Disk Size: 5GB
- RAM Usage: 3GB
- Inference Speed: ~10 tokens/second on Pi 4
- Context Window: 2048 tokens

**Why Phi-2?**:
- Small enough to run on Pi 4
- Excellent reasoning for size
- Fast inference with quantization
- Trained on code/reasoning tasks

### 5.2 llama.cpp Integration

**Installation**:
```bash
# Clone llama.cpp
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp

# Build for Raspberry Pi (ARM)
make

# Download Phi-2 model (Q4_K_M quantization)
wget https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf
mv phi-2.Q4_K_M.gguf /opt/d3kos/models/phi2/
```

### 5.3 LLM Module Implementation

**LLM Module**: `/opt/d3kos/services/voice/llm.py`

```python
import subprocess
import json

class LanguageModel:
    def __init__(self):
        self.model_path = "/opt/d3kos/models/phi2/phi-2.Q4_K_M.gguf"
        self.llama_bin = "/usr/local/bin/llama-cli"

        # LLM parameters
        self.params = {
            'n_ctx': 2048,        # Context window
            'n_predict': 100,     # Max tokens to generate
            'temperature': 0.7,   # Randomness (0=deterministic, 1=random)
            'top_p': 0.9,         # Nucleus sampling
            'top_k': 40,          # Top-k sampling
            'repeat_penalty': 1.1 # Penalize repetition
        }

    def generate(self, prompt, max_tokens=100):
        """Generate response from LLM"""
        cmd = [
            self.llama_bin,
            '-m', self.model_path,
            '-p', prompt,
            '-n', str(max_tokens),
            '-c', str(self.params['n_ctx']),
            '--temp', str(self.params['temperature']),
            '--top-p', str(self.params['top_p']),
            '--top-k', str(self.params['top_k']),
            '--repeat-penalty', str(self.params['repeat_penalty']),
            '--no-display-prompt'
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )

        response = result.stdout.strip()

        # Post-process
        response = self.clean_response(response)

        return response

    def clean_response(self, text):
        """Clean up LLM output"""
        # Remove trailing whitespace
        text = text.strip()

        # Remove incomplete sentences
        if text and not text[-1] in '.!?':
            # Find last complete sentence
            for punct in ['.', '!', '?']:
                idx = text.rfind(punct)
                if idx > 0:
                    text = text[:idx+1]
                    break

        # Limit length (for voice output)
        words = text.split()
        if len(words) > 50:
            text = ' '.join(words[:50]) + '...'

        return text
```

### 5.4 Prompt Engineering

**System Prompt Template**:
```python
SYSTEM_PROMPT = """You are Helm, a concise marine assistant on a boat.
Your responses should be:
- Brief (1-2 sentences max)
- Actionable
- Focused on safety
- Marine terminology appropriate

Current boat status:
- Engine RPM: {rpm}
- Oil Pressure: {oil_pressure} PSI
- Coolant Temperature: {coolant_temp}°F
- Fuel Level: {fuel_level}%
- Battery Voltage: {voltage}V

User: {user_query}

Helm:"""
```

**Example Prompts**:

1. **Engine Status Query**:
```
User: What's the engine status?
Helm: Engine running at 3200 RPM, oil pressure 45 PSI, temperature 180°F. All systems normal.
```

2. **Anomaly Inquiry**:
```
User: Any problems?
Helm: Oil pressure is 10 PSI below baseline at 35 PSI. Check oil level and consider maintenance.
```

3. **Navigation Query**:
```
User: How far to the dock?
Helm: Based on GPS, you are 2.3 nautical miles from the dock, approximately 12 minutes at current speed.
```

### 5.5 LLM Performance Tuning

**Parameter Tuning**:

| Parameter | Value | Effect | Trade-off |
|-----------|-------|--------|-----------|
| **temperature** | 0.7 | Controls randomness | 0=deterministic, 1=creative |
| **top_p** | 0.9 | Nucleus sampling | Lower=focused, higher=diverse |
| **top_k** | 40 | Limits vocabulary | Lower=safer, higher=varied |
| **repeat_penalty** | 1.1 | Penalizes repetition | Too high=incoherent |
| **n_ctx** | 2048 | Context window | Larger=slower, more memory |
| **n_predict** | 100 | Max output tokens | Longer=slower |

**Optimization Tips**:
1. **Reduce context**: Only include relevant boat status
2. **Limit output**: Set max tokens to 50-100
3. **Use quantized model**: Q4_K_M is 4x smaller than FP16
4. **Cache prompt**: Reuse system prompt across requests
5. **Batch infrequent**: Don't query LLM for every command

---

## 6. TEXT-TO-SPEECH (TTS)

### 6.1 Piper Configuration

**Voice**: `en_US-amy-medium`
- Quality: Medium (balance speed vs quality)
- Sample Rate: 22050Hz
- Format: WAV, 16-bit
- Size: ~20MB

### 6.2 Implementation

**TTS Module**: `/opt/d3kos/services/voice/tts.py`

```python
import subprocess
import tempfile

class TextToSpeech:
    def __init__(self):
        self.piper_bin = "/usr/local/bin/piper"
        self.voice_model = "/opt/d3kos/models/piper/en_US-amy-medium.onnx"
        self.voice_config = "/opt/d3kos/models/piper/en_US-amy-medium.onnx.json"
        self.sample_rate = 22050

    def synthesize(self, text, output_file=None):
        """Convert text to speech"""
        if output_file is None:
            output_file = tempfile.mktemp(suffix='.wav')

        # Piper command
        cmd = [
            self.piper_bin,
            '--model', self.voice_model,
            '--config', self.voice_config,
            '--output_file', output_file
        ]

        # Run Piper with text input
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout, stderr = process.communicate(input=text)

        if process.returncode != 0:
            raise Exception(f"Piper TTS failed: {stderr}")

        return output_file

    def synthesize_with_speed(self, text, speed=1.0, output_file=None):
        """Synthesize with custom speed"""
        if output_file is None:
            output_file = tempfile.mktemp(suffix='.wav')

        temp_file = tempfile.mktemp(suffix='.wav')

        # First synthesize
        self.synthesize(text, temp_file)

        # Then adjust speed with sox
        subprocess.run([
            'sox', temp_file, output_file,
            'tempo', str(speed)
        ])

        return output_file
```

### 6.3 Voice Customization

**Adjust Speed**:
```python
# Slower (0.8x) - more clear
audio = tts.synthesize_with_speed("Engine running normally", speed=0.8)

# Normal (1.0x)
audio = tts.synthesize("Engine running normally")

# Faster (1.2x) - more urgent
audio = tts.synthesize_with_speed("Critical oil pressure low!", speed=1.2)
```

**Prosody Control** (limited in Piper):
- Emphasis: Use ALL CAPS for important words
- Pauses: Use commas and periods
- Numbers: Spell out for clarity ("three thousand" vs "3000")

**Example**:
```python
# Poor prosody
text = "Engine at 3200 rpm oil pressure 45 psi temperature 180 degrees"

# Better prosody
text = "Engine at thirty-two hundred RPM. Oil pressure, forty-five PSI. Temperature, one hundred eighty degrees."
```

### 6.4 Audio Post-Processing

**Normalize Volume**:
```bash
# Use sox to normalize audio levels
sox input.wav output.wav gain -n
```

**Add Marine Radio Effect** (optional):
```bash
# Simulate VHF radio effect
sox input.wav output.wav \
    lowpass 3000 \
    highpass 300 \
    gain -3
```

---

## 7. ANOMALY DETECTION

### 7.1 Statistical Process Control (SPC)

**Algorithm**: 3-Sigma Rule
- Normal: Within 1σ (68% of data)
- Warning: Between 2σ and 3σ (4.6% of data)
- Critical: Beyond 3σ (0.3% of data)

### 7.2 Implementation

**Anomaly Detector**: `/opt/d3kos/services/health/anomaly_detector.py`

```python
import json
import math
import sqlite3
from datetime import datetime

class AnomalyDetector:
    def __init__(self):
        self.baseline = self.load_baseline()
        self.db = sqlite3.connect('/opt/d3kos/data/historical.db')

    def load_baseline(self):
        """Load engine baseline data"""
        with open('/opt/d3kos/config/benchmark-results.json') as f:
            return json.load(f)['baseline']

    def detect(self, metric_name, current_value, operating_mode='cruise'):
        """Detect if current value is anomalous"""
        # Get baseline stats
        if metric_name not in self.baseline:
            return {'level': 'UNKNOWN', 'message': None}

        baseline_data = self.baseline[metric_name].get(operating_mode, {})
        if not baseline_data:
            return {'level': 'UNKNOWN', 'message': None}

        mean = baseline_data.get('mean')
        stddev = baseline_data.get('stddev')

        if mean is None or stddev is None:
            return {'level': 'UNKNOWN', 'message': None}

        # Calculate deviation
        deviation = abs(current_value - mean)
        sigma = deviation / stddev if stddev > 0 else 0

        # Classify
        if sigma > 3:
            level = 'CRITICAL'
            message = f"{metric_name} is {deviation:.1f} units from baseline (>{sigma:.1f}σ)"
        elif sigma > 2:
            level = 'WARNING'
            message = f"{metric_name} is {deviation:.1f} units from baseline (>{sigma:.1f}σ)"
        elif sigma > 1:
            level = 'INFO'
            message = f"{metric_name} is slightly elevated"
        else:
            level = 'NORMAL'
            message = None

        # Log anomaly
        if level in ['WARNING', 'CRITICAL']:
            self.log_anomaly(
                level=level,
                metric=metric_name,
                value=current_value,
                baseline_value=mean,
                deviation=deviation,
                sigma=sigma,
                message=message
            )

        return {
            'level': level,
            'message': message,
            'deviation': deviation,
            'sigma': sigma,
            'baseline': mean,
            'stddev': stddev
        }

    def log_anomaly(self, level, metric, value, baseline_value, deviation, sigma, message):
        """Log anomaly to database"""
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT INTO anomalies (
                timestamp, level, metric, value,
                baseline_value, deviation, sigma, message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            level, metric, value,
            baseline_value, deviation, sigma, message
        ))
        self.db.commit()
```

### 7.3 Real-Time Monitoring

**Node-RED Flow**:
```javascript
// Anomaly detection flow
[signalk:in] → [function: check threshold] → [anomaly detector]
    ↓                                              ↓
[dashboard gauge]                        [voice alert (if critical)]
                                                  ↓
                                         [log to database]
```

**Function Node** (Node-RED):
```javascript
// Check if metric exceeds thresholds
const rpm = msg.payload.propulsion.main.revolutions;
const oilPressure = msg.payload.propulsion.main.oilPressure / 6894.76; // Pa to PSI
const temp = (msg.payload.propulsion.main.temperature - 273.15) * 9/5 + 32; // K to F

// Call anomaly detector
const http = require('http');
const postData = JSON.stringify({
    metrics: {
        rpm: rpm,
        oilPressure: oilPressure,
        coolantTemp: temp
    },
    operatingMode: rpm > 3000 ? 'cruise' : 'idle'
});

const options = {
    hostname: 'localhost',
    port: 8000,
    path: '/api/anomaly/detect',
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Content-Length': postData.length
    }
};

const req = http.request(options, (res) => {
    let data = '';
    res.on('data', (chunk) => { data += chunk; });
    res.on('end', () => {
        const anomalies = JSON.parse(data);

        // Check for critical anomalies
        for (const anomaly of anomalies) {
            if (anomaly.level === 'CRITICAL') {
                // Trigger voice alert
                node.send({payload: {
                    type: 'voice_alert',
                    message: anomaly.message
                }});
            }
        }
    });
});

req.write(postData);
req.end();
```

### 7.4 Trend Detection

**Sliding Window Analysis**:
```python
def detect_trend(metric_name, window_days=7):
    """Detect if metric is trending away from baseline"""
    cursor = self.db.cursor()
    cursor.execute("""
        SELECT
            DATE(timestamp) as date,
            AVG(?) as avg_value
        FROM engine_metrics
        WHERE timestamp >= datetime('now', '-? days')
        GROUP BY DATE(timestamp)
        ORDER BY date ASC
    """, (metric_name, window_days))

    data = cursor.fetchall()

    if len(data) < 3:
        return None

    # Calculate linear regression slope
    values = [row[1] for row in data]
    n = len(values)
    x = list(range(n))

    x_mean = sum(x) / n
    y_mean = sum(values) / n

    numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
    denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

    slope = numerator / denominator if denominator != 0 else 0

    # Check if slope is significant
    baseline_mean = self.baseline[metric_name]['cruise']['mean']
    daily_change = slope
    weekly_change = slope * 7

    # Threshold: 10% change per week is significant
    if abs(weekly_change / baseline_mean) > 0.10:
        direction = "increasing" if slope > 0 else "decreasing"
        return {
            'metric': metric_name,
            'trend': direction,
            'daily_change': daily_change,
            'weekly_change': weekly_change,
            'percentage': (weekly_change / baseline_mean) * 100,
            'message': f"{metric_name} is {direction} by {abs(weekly_change):.1f} units per week"
        }

    return None
```

---

## 8. COMMAND PARSING

### 8.1 Intent Classification

**Command Parser**: `/opt/d3kos/services/voice/command_parser.py`

```python
import re
from difflib import SequenceMatcher

class CommandParser:
    def __init__(self):
        # Define command patterns
        self.commands = {
            'engine_status': [
                'engine status',
                'how is the engine',
                'engine condition',
                'engine running'
            ],
            'check_anomalies': [
                'any anomalies',
                'any problems',
                'any issues',
                'any alerts',
                'anything wrong'
            ],
            'open_opencpn': [
                'open opencpn',
                'launch opencpn',
                'start opencpn',
                'open charts'
            ],
            'start_benchmark': [
                'start benchmarking',
                'start benchmark',
                'begin benchmark',
                'run benchmark'
            ],
            'record_log': [
                'record boat log',
                'start recording',
                'log entry',
                'record entry'
            ],
            'system_status': [
                'system status',
                'raspberry pi status',
                'pi status',
                'system health'
            ]
        }

    def parse(self, text):
        """Parse user input and classify intent"""
        text = text.lower().strip()

        # Try exact match first
        for action, patterns in self.commands.items():
            for pattern in patterns:
                if pattern in text:
                    return {
                        'type': 'direct',
                        'action': action,
                        'confidence': 1.0,
                        'original': text
                    }

        # Try fuzzy match
        best_match = None
        best_score = 0

        for action, patterns in self.commands.items():
            for pattern in patterns:
                similarity = self.similarity(text, pattern)
                if similarity > best_score:
                    best_score = similarity
                    best_match = action

        # Threshold for fuzzy match
        if best_score > 0.8:
            return {
                'type': 'direct',
                'action': best_match,
                'confidence': best_score,
                'original': text
            }

        # No direct command matched, use LLM
        return {
            'type': 'llm_query',
            'action': None,
            'confidence': 0,
            'original': text
        }

    def similarity(self, a, b):
        """Calculate similarity between two strings (0-1)"""
        return SequenceMatcher(None, a, b).ratio()
```

### 8.2 Entity Extraction

**Extract Numeric Values**:
```python
def extract_numbers(text):
    """Extract numbers from text"""
    # Match integers and floats
    pattern = r'\b\d+(?:\.\d+)?\b'
    return [float(match) for match in re.findall(pattern, text)]

# Example
text = "set rpm to 3200"
numbers = extract_numbers(text)  # [3200.0]
```

**Extract Time References**:
```python
def extract_time(text):
    """Extract time references"""
    if 'hour' in text:
        return 'hours'
    elif 'minute' in text:
        return 'minutes'
    elif 'second' in text:
        return 'seconds'
    return None
```

---

## 9. PERFORMANCE OPTIMIZATION

### 9.1 Latency Breakdown

**Target**: < 2 seconds total

| Stage | Target | Typical | Optimization |
|-------|--------|---------|--------------|
| Wake word | < 500ms | 300ms | Always listening, low CPU |
| Audio capture | N/A | 5000ms | Fixed (user speaking time) |
| STT | < 1000ms | 800ms | Use small model, process chunks |
| Command parse | < 50ms | 10ms | Regex matching, precompiled |
| Data query | < 100ms | 50ms | SQLite indexed queries |
| LLM inference | < 1000ms | 800ms | Quantized model, limit tokens |
| TTS | < 500ms | 400ms | Medium quality, streaming |
| **Total** | **< 2000ms** | **~1500ms** | Achievable on Pi 4 |

### 9.2 Memory Management

**Model Loading Strategy**:
```python
# Load models at startup (not per-request)
class VoiceAssistant:
    def __init__(self):
        # Load all models into RAM
        self.stt = SpeechToText()      # 200MB
        self.llm = LanguageModel()     # 3GB
        self.tts = TextToSpeech()      # 100MB

        # Total: ~3.3GB
```

**Swap Configuration** (if using 4GB Pi):
```bash
# Increase swap to 4GB
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Set CONF_SWAPSIZE=4096
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### 9.3 CPU Optimization

**Thread Affinity** (pin to specific cores):
```python
import os

# Pin to cores 2-3 (leave 0-1 for OS)
os.sched_setaffinity(0, {2, 3})
```

**Process Priority**:
```bash
# Set high priority for voice service
sudo renice -n -10 -p $(pgrep -f helm-voice)
```

### 9.4 Caching Strategies

**Cache LLM Prompt**:
```python
class LanguageModel:
    def __init__(self):
        self.cached_prompt = None
        self.cached_context = None

    def generate(self, prompt):
        # Check if base prompt changed
        if self.should_cache(prompt):
            # Reuse cached KV cache
            pass
```

**Cache TTS Phrases**:
```python
TTS_CACHE = {
    "all systems normal": "/opt/d3kos/cache/tts_normal.wav",
    "oil pressure low": "/opt/d3kos/cache/tts_oil_low.wav"
}

def synthesize_cached(text):
    if text in TTS_CACHE:
        return TTS_CACHE[text]
    return tts.synthesize(text)
```

---

## 10. MODEL MANAGEMENT

### 10.1 Model Storage

```
/opt/d3kos/models/
├── pocketsphinx/
│   ├── en-us/              # Acoustic model
│   ├── helm.dict           # Pronunciation dictionary
│   └── helm.lm             # Language model
│
├── vosk/
│   ├── am/                 # Acoustic model
│   ├── conf/               # Configuration
│   ├── graph/              # HCLG graph
│   └── ivector/            # Feature extractor
│
├── phi2/
│   └── phi-2.Q4_K_M.gguf  # Quantized LLM (5GB)
│
└── piper/
    ├── en_US-amy-medium.onnx       # Voice model
    └── en_US-amy-medium.onnx.json  # Config
```

### 10.2 Model Updates

**Update Script**: `/opt/d3kos/scripts/update-models.sh`

```bash
#!/bin/bash
# Update AI models

MODELS_DIR="/opt/d3kos/models"
BACKUP_DIR="/opt/d3kos/backups/models_$(date +%Y%m%d)"

# Backup existing models
mkdir -p $BACKUP_DIR
cp -r $MODELS_DIR/* $BACKUP_DIR/

echo "Models backed up to: $BACKUP_DIR"

# Update Vosk model
echo "Updating Vosk model..."
wget -O /tmp/vosk-model.zip \
    https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip /tmp/vosk-model.zip -d /tmp/
rm -rf $MODELS_DIR/vosk
mv /tmp/vosk-model-small-en-us-0.15 $MODELS_DIR/vosk

# Update Piper voice
echo "Updating Piper voice..."
wget -O $MODELS_DIR/piper/en_US-amy-medium.onnx \
    https://github.com/rhasspy/piper/releases/download/v1.2.0/en_US-amy-medium.onnx
wget -O $MODELS_DIR/piper/en_US-amy-medium.onnx.json \
    https://github.com/rhasspy/piper/releases/download/v1.2.0/en_US-amy-medium.onnx.json

# Update Phi-2 (manual, large file)
echo "Phi-2 model update requires manual download"

# Restart voice service
sudo systemctl restart helm-voice

echo "Models updated successfully"
```

### 10.3 Model Verification

**Checksum Verification**:
```bash
#!/bin/bash
# Verify model integrity

# Vosk model
echo "Verifying Vosk model..."
VOSK_CHECKSUM="abc123..."  # Expected checksum
VOSK_ACTUAL=$(find /opt/d3kos/models/vosk -type f -exec sha256sum {} \; | sha256sum | cut -d' ' -f1)

if [ "$VOSK_CHECKSUM" != "$VOSK_ACTUAL" ]; then
    echo "ERROR: Vosk model checksum mismatch"
    exit 1
fi

# Phi-2 model
echo "Verifying Phi-2 model..."
PHI2_CHECKSUM="def456..."
PHI2_ACTUAL=$(sha256sum /opt/d3kos/models/phi2/phi-2.Q4_K_M.gguf | cut -d' ' -f1)

if [ "$PHI2_CHECKSUM" != "$PHI2_ACTUAL" ]; then
    echo "ERROR: Phi-2 model checksum mismatch"
    exit 1
fi

echo "All models verified successfully"
```

---

## 11. TROUBLESHOOTING

### 11.1 Wake Word Not Detecting

**Symptoms**:
- Wake word never triggers
- High false positive rate

**Diagnostic**:
```bash
# Test microphone
arecord -l

# Record test audio
arecord -d 5 -f S16_LE -r 16000 test.wav

# Play back
aplay test.wav

# Check sensitivity
# Edit threshold in wake_word.py: kws_threshold=1e-40
```

**Solutions**:
1. Adjust `kws_threshold` (lower = more sensitive)
2. Check microphone levels: `alsamixer`
3. Verify correct audio device selected
4. Test in quieter environment (reduce engine noise)

### 11.2 STT Transcription Errors

**Symptoms**:
- Incorrect transcriptions
- Missing words
- Low accuracy

**Diagnostic**:
```python
# Test STT directly
from stt import SpeechToText

stt = SpeechToText()
text = stt.transcribe('/path/to/test.wav')
print(f"Transcription: {text}")
```

**Solutions**:
1. Use clearer speech (enunciate)
2. Add marine vocabulary to model
3. Reduce background noise
4. Verify audio format (16kHz, mono, 16-bit)
5. Try larger Vosk model (if RAM available)

### 11.3 LLM Slow Inference

**Symptoms**:
- Responses take > 2 seconds
- High CPU usage

**Diagnostic**:
```bash
# Check CPU usage
top

# Monitor inference time
journalctl -u helm-voice -f | grep "LLM inference"

# Check for thermal throttling
vcgencmd get_throttled
```

**Solutions**:
1. Reduce `n_predict` (max tokens)
2. Lower `temperature` (faster sampling)
3. Improve cooling (add heatsink)
4. Use smaller model (1.3B Phi instead of 2.7B)
5. Enable swap if RAM limited

### 11.4 TTS Audio Quality Issues

**Symptoms**:
- Robotic voice
- Choppy audio
- Distorted sound

**Diagnostic**:
```bash
# Test TTS directly
echo "test" | /usr/local/bin/piper \
    --model /opt/d3kos/models/piper/en_US-amy-medium.onnx \
    --output_file test.wav

aplay test.wav
```

**Solutions**:
1. Try different voice model (amy, lessac, etc.)
2. Adjust speaking rate (use sox tempo)
3. Normalize audio levels
4. Check speaker connections
5. Verify sample rate compatibility

### 11.5 Memory Issues

**Symptoms**:
- Service crashes
- OOM (Out of Memory) errors
- Slow performance

**Diagnostic**:
```bash
# Check memory usage
free -h

# Check service status
systemctl status helm-voice

# View OOM errors
dmesg | grep -i "out of memory"
```

**Solutions**:
1. Use 8GB Pi 4 (recommended)
2. Increase swap space
3. Reduce model sizes (use smaller quantization)
4. Unload models between uses (not recommended)
5. Disable camera service temporarily

---

## APPENDIX A: Performance Benchmarks

### A.1 Raspberry Pi 4 Performance

**Model Loading Times**:
| Model | Size | Load Time (4GB Pi) | Load Time (8GB Pi) |
|-------|------|--------------------|--------------------|
| Vosk STT | 50MB | 2-3 seconds | 2-3 seconds |
| Phi-2 LLM | 5GB | 8-12 seconds | 6-8 seconds |
| Piper TTS | 20MB | 1-2 seconds | 1-2 seconds |

**Inference Times**:
| Operation | Duration | CPU Usage | RAM Usage |
|-----------|----------|-----------|-----------|
| Wake word (continuous) | N/A | 5-10% | 50MB |
| STT (5s audio) | 0.8-1.2s | 100% | 200MB |
| LLM (50 tokens) | 0.8-1.5s | 100% | 3GB |
| TTS (20 words) | 0.4-0.6s | 80% | 100MB |

---

## APPENDIX B: Alternative Models

### B.1 Lightweight Alternatives

**For 4GB Pi** (if struggling with Phi-2):

| Model | Size | RAM | Speed | Quality |
|-------|------|-----|-------|---------|
| **Phi-1.5** | 3GB | 2GB | 15 tok/s | Lower than Phi-2 |
| **TinyLlama** | 2GB | 1.5GB | 20 tok/s | Basic responses |
| **GPT-2 Small** | 500MB | 500MB | 30 tok/s | Simple commands only |

### B.2 High-Quality Alternatives

**For 8GB Pi** (if want better quality):

| Model | Size | RAM | Speed | Quality |
|-------|------|-----|-------|---------|
| **Phi-2 (Q8)** | 8GB | 5GB | 5 tok/s | Better than Q4 |
| **Mistral 7B (Q4)** | 4GB | 3GB | 8 tok/s | Excellent reasoning |
| **Llama-2 7B (Q4)** | 4GB | 3GB | 8 tok/s | Good general knowledge |

---

## APPENDIX C: Command Reference

### C.1 Supported Voice Commands

**Engine & Health**:
- "Helm, what's the engine status?"
- "Helm, any anomalies?"
- "Helm, show benchmark report"
- "Helm, start benchmarking"
- "Helm, check oil pressure"
- "Helm, engine temperature"

**Navigation**:
- "Helm, open OpenCPN"
- "Helm, GPS status"
- "Helm, AIS status"
- "Helm, where are we?"
- "Helm, distance to dock"

**System**:
- "Helm, system status"
- "Helm, Raspberry Pi status"
- "Helm, CPU temperature"
- "Helm, memory usage"
- "Helm, restart services"

**Boat Log**:
- "Helm, record boat log"
- "Helm, post to boat log"
- "Helm end" (stop listening)

---

**END OF AI INFERENCE ENGINE SPECIFICATION**
