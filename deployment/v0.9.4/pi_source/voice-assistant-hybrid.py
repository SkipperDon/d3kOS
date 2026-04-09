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
import threading
from vosk import Model, KaldiRecognizer
import argparse
import time
import re
import signal

# Import Vosk wake word detector
sys.path.insert(0, '/opt/d3kos/services/voice')
from wake_word_vosk import VoskWakeWordDetector

# Paths
VOSK_MODEL = "/opt/d3kos/models/vosk/vosk-model-small-en-us-0.15"
PIPER_BIN = "/usr/local/bin/piper"
PIPER_VOICE = "/opt/d3kos/models/piper/en_US-amy-medium.onnx"
AI_QUERY_HANDLER = "/opt/d3kos/services/ai/query_handler.py"
MUTE_STATE_FILE = "/opt/d3kos/config/tts-mute.json"

SAMPLE_RATE = 16000
LISTEN_DURATION = 7

# Wake word configuration
WAKE_WORDS = {
    'helm': {'ai': 'auto', 'response': 'Aye Aye Captain'}
}

class HybridVoiceAssistant:
    def __init__(self):
        self.vosk_model = None
        self.mic_device = None
        self.wake_word_detector = None
        self.detected_wake_word = None  # Store detected wake word
        self.ack_wav = None
        self._mic_locked = False
        self._prewarmed_rec = None  # Pre-warmed KaldiRecognizer for instant listen()
        signal.signal(signal.SIGUSR1, self._handle_mic_lock)
        signal.signal(signal.SIGUSR2, self._handle_mic_unlock)

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

    def _is_muted(self) -> bool:
        """Read mute state from tts-mute.json (written by ai_bridge on HELM mute toggle)."""
        try:
            with open(MUTE_STATE_FILE) as fh:
                return json.load(fh).get('muted', False)
        except Exception:
            return False  # file missing or unreadable = not muted

    def speak(self, text):
        if self._is_muted():
            print(f"🔇 Muted — suppressed: {text[:50]}", flush=True)
            return
        print(f"🔊 Assistant: {text}", flush=True)
        try:
            p = subprocess.Popen(
                [PIPER_BIN, "--model", PIPER_VOICE, "--output_file", "/tmp/response.wav"],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            p.communicate(input=text.encode())
            if p.returncode == 0:
                if self._is_muted():  # re-check — mute may have been pressed while piper ran
                    print("🔇 Muted — suppressed playback", flush=True)
                    try:
                        os.remove("/tmp/response.wav")
                    except OSError:
                        pass
                    return
                subprocess.run(["aplay", "-q", "-D", "plughw:S330,0", "/tmp/response.wav"])
                os.remove("/tmp/response.wav")
        except Exception as e:
            print(f"⚠ TTS error: {e}", flush=True)

    def pregenerate_ack(self):
        """Pre-generate acknowledgment WAV at startup for instant playback."""
        try:
            p = subprocess.Popen(
                [PIPER_BIN, "--model", PIPER_VOICE, "--output_file", "/tmp/d3kos_ack.wav"],
                stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            p.communicate(input=b"Aye Aye Captain")
            if p.returncode == 0 and os.path.exists("/tmp/d3kos_ack.wav"):
                self.ack_wav = "/tmp/d3kos_ack.wav"
                print("  ✓ Acknowledgment audio pre-generated", flush=True)
            else:
                self.ack_wav = None
        except Exception as e:
            print(f"  ⚠ Pre-generate ack error: {e}", flush=True)
            self.ack_wav = None

    def _prewarm_recognizer(self):
        """Pre-create a KaldiRecognizer so listen() can start arecord without 2s init delay."""
        try:
            if not self.vosk_model:
                self.vosk_model = Model(VOSK_MODEL)
            self._prewarmed_rec = KaldiRecognizer(self.vosk_model, SAMPLE_RATE)
        except Exception as e:
            print(f"  ⚠ Pre-warm recognizer error: {e}", flush=True)
            self._prewarmed_rec = None

    def listen(self, max_duration=LISTEN_DURATION):
        """Stream audio with VAD — stops after speech + 1.5s silence instead of fixed duration."""
        print(f"🎤 Listening (VAD, max {max_duration}s)...", flush=True)

        # Use pre-warmed recognizer if available (no 2s init delay)
        if self._prewarmed_rec is not None:
            rec = self._prewarmed_rec
            self._prewarmed_rec = None
        else:
            if not self.vosk_model:
                self.vosk_model = Model(VOSK_MODEL)
            rec = KaldiRecognizer(self.vosk_model, SAMPLE_RATE)

        # Pre-warm next recognizer in background while we listen
        threading.Thread(target=self._prewarm_recognizer, daemon=True).start()

        # Stream raw audio from arecord (no fixed duration)
        proc = subprocess.Popen(
            ["arecord", "-D", self.mic_device, "-f", "S16_LE", "-r", str(SAMPLE_RATE),
             "-c", "1", "-t", "raw", "-q"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
        )

        CHUNK_BYTES = 8000   # 4000 frames * 2 bytes = ~0.25s at 16kHz
        SILENCE_TIMEOUT = 1.5  # seconds of silence after speech to stop

        speech_started = False
        silence_start = None
        result_text = ""
        start_time = time.time()

        try:
            while time.time() - start_time < max_duration:
                data = proc.stdout.read(CHUNK_BYTES)
                if not data:
                    break

                if rec.AcceptWaveform(data):
                    text = json.loads(rec.Result()).get('text', '').strip()
                    if text:
                        result_text = text
                        print(f"📝 Heard: {result_text}", flush=True)
                        break
                else:
                    partial = json.loads(rec.PartialResult()).get('partial', '').strip()
                    if partial:
                        speech_started = True
                        silence_start = None
                    elif speech_started:
                        if silence_start is None:
                            silence_start = time.time()
                        elif time.time() - silence_start >= SILENCE_TIMEOUT:
                            break  # Silence after speech — done

            # Drain any remaining final result
            final = json.loads(rec.FinalResult()).get('text', '').strip()
            if final and not result_text:
                result_text = final
                print(f"📝 Heard: {result_text}", flush=True)

        except Exception as e:
            print(f"⚠ Listen error: {e}", flush=True)
        finally:
            proc.kill()
            proc.wait()

        if not result_text:
            print("📝 Nothing heard", flush=True)
        return result_text

    def query_ai(self, question, provider=None):
        """Query the AI handler with routing based on wake word"""
        mode_name = provider if provider else 'auto'
        print(f"  🤖 Querying AI (mode: {mode_name})...", flush=True)

        try:
            # Build command for AI query handler — --no-rag skips PDF init for fast voice response
            cmd = ["python3", AI_QUERY_HANDLER, "--no-rag"]

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
                # Answer: prefix is always the last meaningful line
                for line in reversed(result.stdout.strip().splitlines()):
                    if line.startswith("Answer:"):
                        return line[len("Answer:"):].strip()
                return "I couldn't get an answer to that."
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

    def _handle_mic_lock(self, signum, frame):
        """External mic lock — release ALSA device for browser recording."""
        self._mic_locked = True
        try:
            self.wake_word_detector.stop()
            print("🔒 Mic locked for external recording", flush=True)
        except Exception as e:
            print(f"⚠  Mic lock error: {e}", flush=True)

    def _handle_mic_unlock(self, signum, frame):
        """External mic unlock — resume wake word detection."""
        self._mic_locked = False
        print("🔓 Mic unlocked — will resume wake word detection", flush=True)

    def run_service(self):
        print("="*60, flush=True)
        print("d3kOS Hybrid Voice Assistant v3 - Vosk Integration", flush=True)
        print("Wake word: HELM", flush=True)
        print("="*60, flush=True)

        if not self.check_dependencies():
            return False

        # Initialize Vosk wake word detector
        if not self.init_wake_word_detector():
            return False

        self.pregenerate_ack()
        self._prewarm_recognizer()
        print("  ✓ KaldiRecognizer pre-warmed — first listen() will be instant", flush=True)
        self.speak("Voice assistant ready. Say helm to activate.")
        print("🎤 Listening for wake words...", flush=True)

        try:
            # Start wake word detection in background thread
            def wake_word_listener():
                """Background thread for wake word detection"""
                self.wake_word_detector.listen(callback=self.on_wake_word_detected)

            listener_thread = threading.Thread(target=wake_word_listener, daemon=True)
            listener_thread.start()

            # Main loop - check for detected wake words
            while True:
                # If mic is externally locked (boatlog recording), idle until released
                if self._mic_locked:
                    time.sleep(0.5)
                    continue

                # Restart listener if it exited (after command or after external unlock)
                if not listener_thread.is_alive():
                    print("▶  Resuming wake word detection...", flush=True)
                    listener_thread = threading.Thread(target=wake_word_listener, daemon=True)
                    listener_thread.start()
                    print("🎤 Listening for wake words...", flush=True)

                if self.detected_wake_word:
                    wake_word = self.detected_wake_word
                    self.detected_wake_word = None  # Reset for next detection

                    config = WAKE_WORDS[wake_word]
                    print(f"AI mode: {config['ai']}", flush=True)

                    # Play pre-generated ack WAV for instant response, fallback to TTS
                    if self.ack_wav and os.path.exists(self.ack_wav) and not self._is_muted():
                        subprocess.run(["aplay", "-q", "-D", "plughw:S330,0", self.ack_wav])
                    elif not self._is_muted():
                        self.speak(config['response'])

                    # STOP wake word detection to free microphone
                    print("⏸  Pausing wake word detection...", flush=True)
                    self.wake_word_detector.stop()
                    time.sleep(0.5)  # Wait for device to fully release

                    command = self.listen()

                    if command:
                        print(f"💭 You asked: {command}", flush=True)
                        response = self.query_ai(command)
                        self.speak(response)
                    else:
                        self.speak("I didn't catch that.")

                    # Wait for audio playback to fully complete
                    time.sleep(2)
                    # Listener restart handled at top of loop

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
