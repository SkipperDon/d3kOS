#!/usr/bin/env python3
"""
d3kOS Hybrid Voice Assistant v3 - Vosk Wake Word Integration
Integrates with AI query handler
Wake words: Helm (auto), Advisor (onboard), Counsel (online)

CHANGES FROM v2:
- Replaced PocketSphinx wake word detection with Vosk
- Using wake_word_detector.py for unified interface
- More reliable wake word detection (~90% accuracy)
- Lower CPU usage, better performance
"""

import json
import os
import sys
import wave
import subprocess
from vosk import Model, KaldiRecognizer
import argparse
import time
import re

# Import Vosk wake word detector
sys.path.insert(0, '/opt/d3kos/services/voice')
from wake_word_vosk import VoskWakeWordDetector

# Paths
VOSK_MODEL = "/opt/d3kos/models/vosk/vosk-model-small-en-us-0.15"
PIPER_BIN = "/usr/local/bin/piper"
PIPER_VOICE = "/opt/d3kos/models/piper/en_US-amy-medium.onnx"
AI_QUERY_HANDLER = "/opt/d3kos/services/ai/query_handler.py"

SAMPLE_RATE = 16000
LISTEN_DURATION = 3

# Wake word configuration
WAKE_WORDS = {
    'helm': {'ai': 'auto', 'response': 'Aye Aye Captain', 'provider': None},
    'advisor': {'ai': 'onboard', 'response': 'Aye Aye Captain', 'provider': 'onboard'},
    'counsel': {'ai': 'online', 'response': 'Aye Aye Captain', 'provider': 'openrouter'}
}

class HybridVoiceAssistant:
    def __init__(self):
        self.vosk_model = None
        self.mic_device = None
        self.wake_word_detector = None
        self.detected_wake_word = None  # Store detected wake word

    def detect_microphone(self):
        """Auto-detect Anker S330 microphone card number"""
        try:
            result = subprocess.run(['arecord', '-l'], capture_output=True, text=True)
            if result.returncode != 0:
                return None

            # Parse output to find S330 card
            for line in result.stdout.split('\n'):
                if 'S330' in line or 'Anker' in line:
                    if 'card' in line:
                        parts = line.split('card')[1].split(':')[0].strip()
                        card_num = parts
                        device = f"plughw:{card_num},0"
                        print(f"  ✓ Microphone detected: {device} (Anker S330)", flush=True)
                        return device

            # Fallback: use first available capture device
            for line in result.stdout.split('\n'):
                if 'card' in line and 'device' in line:
                    parts = line.split('card')[1].split(':')[0].strip()
                    card_num = parts
                    device = f"plughw:{card_num},0"
                    print(f"  ⚠ Using first available mic: {device}", flush=True)
                    return device

        except Exception as e:
            print(f"  ⚠ Mic detection error: {e}", flush=True)

        # Final fallback
        print(f"  ⚠ Using default mic: plughw:0,0", flush=True)
        return "plughw:0,0"

    def check_dependencies(self):
        print("Checking dependencies...", flush=True)
        checks = [
            (os.path.exists(VOSK_MODEL), f"Vosk model: {VOSK_MODEL}"),
            (os.path.exists(PIPER_BIN), f"Piper TTS: {PIPER_BIN}"),
            (os.path.exists(PIPER_VOICE), f"Piper voice: {PIPER_VOICE}"),
            (os.path.exists(AI_QUERY_HANDLER), f"AI Query Handler: {AI_QUERY_HANDLER}")
        ]

        all_ok = True
        for check, name in checks:
            status = "✓" if check else "✗"
            print(f"  {status} {name}", flush=True)
            if not check:
                all_ok = False

        # Auto-detect microphone
        self.mic_device = self.detect_microphone()
        if not self.mic_device:
            print("  ✗ No microphone detected", flush=True)
            all_ok = False

        return all_ok

    def speak(self, text):
        print(f"🔊 Assistant: {text}", flush=True)
        try:
            p = subprocess.Popen(
                [PIPER_BIN, "--model", PIPER_VOICE, "--output_file", "/tmp/response.wav"],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            p.communicate(input=text.encode())
            if p.returncode == 0:
                # Use Anker S330 speaker for output (card 3)
                subprocess.run(["aplay", "-q", "-D", "plughw:3,0", "/tmp/response.wav"])
                os.remove("/tmp/response.wav")
        except Exception as e:
            print(f"⚠ TTS error: {e}", flush=True)

    def listen(self, duration=LISTEN_DURATION):
        print(f"🎤 Listening for {duration} seconds...", flush=True)
        wav_file = "/tmp/voice-input.wav"

        try:
            # Use arecord with auto-detected microphone device
            subprocess.run(
                ["arecord", "-D", self.mic_device, "-f", "S16_LE", "-r", "16000",
                 "-c", "1", "-d", str(duration), wav_file],
                check=True,
                capture_output=True
            )

            print("📝 Transcribing...", flush=True)
            if not self.vosk_model:
                self.vosk_model = Model(VOSK_MODEL)

            rec = KaldiRecognizer(self.vosk_model, SAMPLE_RATE)
            wf = wave.open(wav_file, "rb")

            result_text = ""
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    if 'text' in result:
                        result_text += result['text'] + " "

            final_result = json.loads(rec.FinalResult())
            if 'text' in final_result:
                result_text += final_result['text']

            wf.close()
            os.remove(wav_file)
            return result_text.strip()
        except Exception as e:
            print(f"⚠ Listen error: {e}", flush=True)
            return ""

    def query_ai(self, question, provider=None):
        """Query the AI handler with routing based on wake word"""
        mode_name = provider if provider else 'auto'
        print(f"  🤖 Querying AI (mode: {mode_name})...", flush=True)

        try:
            # Build command for AI query handler
            cmd = ["python3", AI_QUERY_HANDLER]

            # Add force-provider argument if specified
            if provider:
                cmd.extend(["--force-provider", provider])

            cmd.append(question)

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd="/opt/d3kos/services/ai"
            )

            if result.returncode == 0:
                # Parse output - look for "Answer:" section
                output = result.stdout
                if "Answer:" in output:
                    answer_section = output.split("Answer:")[1].strip()
                    # Return the full answer (all lines)
                    answer = answer_section
                    return answer
                else:
                    return "I received a response but couldn't parse it."
            else:
                print(f"  ⚠ AI query failed: {result.stderr}", flush=True)
                return "I'm having trouble answering that question."

        except subprocess.TimeoutExpired:
            return "The query took too long. Please try again."
        except Exception as e:
            print(f"  ⚠ AI query error: {e}", flush=True)
            return "I'm having trouble with that question."

    def on_wake_word_detected(self, wake_word):
        """Callback when wake word is detected by Vosk"""
        # Store detected wake word for main loop
        self.detected_wake_word = wake_word.lower()
        print(f"\n{'='*60}", flush=True)
        print(f"✓ Wake word detected: {wake_word.upper()}", flush=True)
        print("="*60, flush=True)

    def init_wake_word_detector(self):
        """Initialize Vosk wake word detector"""
        print("Initializing Vosk wake word detector...", flush=True)

        try:
            self.wake_word_detector = VoskWakeWordDetector(
                model_path=VOSK_MODEL,
                wake_words=list(WAKE_WORDS.keys()),
                sample_rate=SAMPLE_RATE,
                mic_device=self.mic_device
            )

            if self.wake_word_detector.load_model():
                print("  ✓ Vosk wake word detector ready", flush=True)
                return True
            else:
                print("  ✗ Failed to load Vosk wake word detector", flush=True)
                return False

        except Exception as e:
            print(f"  ✗ Wake word detector error: {e}", flush=True)
            return False

    def run_service(self):
        print("="*60, flush=True)
        print("d3kOS Hybrid Voice Assistant v3 - Vosk Integration", flush=True)
        print("Wake words: HELM (auto) | ADVISOR (onboard) | COUNSEL (online)", flush=True)
        print("="*60, flush=True)

        if not self.check_dependencies():
            return False

        # Initialize Vosk wake word detector
        if not self.init_wake_word_detector():
            return False

        self.speak("Voice assistant started. Say helm, advisor, or counsel to activate me.")
        print("🎤 Listening for wake words...", flush=True)

        try:
            # Start wake word detection in background thread
            import threading

            def wake_word_listener():
                """Background thread for wake word detection"""
                self.wake_word_detector.listen(callback=self.on_wake_word_detected)

            listener_thread = threading.Thread(target=wake_word_listener, daemon=True)
            listener_thread.start()

            # Main loop - check for detected wake words
            while True:
                if self.detected_wake_word:
                    wake_word = self.detected_wake_word
                    self.detected_wake_word = None  # Reset for next detection

                    config = WAKE_WORDS[wake_word]
                    print(f"AI mode: {config['ai']}", flush=True)

                    # Speak acknowledgment
                    self.speak(config['response'])

                    # STOP wake word detection to free microphone
                    print("⏸  Pausing wake word detection...", flush=True)
                    self.wake_word_detector.stop()
                    time.sleep(0.5)  # Wait for device to fully release

                    command = self.listen()

                    if command:
                        print(f"💭 You asked: {command}", flush=True)
                        response = self.query_ai(command, config['provider'])
                        self.speak(response)
                    else:
                        self.speak("I didn't catch that.")

                    # Wait for audio playback to fully complete
                    time.sleep(2)

                    # RESTART wake word detection
                    print("▶  Resuming wake word detection...", flush=True)
                    listener_thread = threading.Thread(target=wake_word_listener, daemon=True)
                    listener_thread.start()
                    print("🎤 Listening for wake words...", flush=True)

                # Small sleep to prevent busy-waiting
                time.sleep(0.1)

        except KeyboardInterrupt:
            print("\nStopping...", flush=True)
            self.speak("Voice assistant stopping.")
            return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--auto-start', action='store_true')
    args = parser.parse_args()

    assistant = HybridVoiceAssistant()
    success = assistant.run_service() if args.auto_start else False
    sys.exit(0 if success else 1)
