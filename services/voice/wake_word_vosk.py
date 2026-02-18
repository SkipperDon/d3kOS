#!/usr/bin/env python3
"""
Vosk Wake Word Detector for d3kOS
Uses keyphrase spotting with Vosk speech recognition
Alternative to PocketSphinx (which is not detecting wake words)
"""

import wave
import json
import subprocess
import sys
import time
from vosk import Model, KaldiRecognizer

class VoskWakeWordDetector:
    """
    Wake word detector using Vosk keyphrase spotting

    Vosk supports both full speech recognition and keyphrase spotting.
    For wake word detection, we use keyphrase spotting mode which is:
    - Faster than full recognition
    - More accurate for specific phrases
    - Lower CPU usage
    """

    def __init__(self, model_path, wake_words, sample_rate=16000, mic_device="plughw:3,0"):
        """
        Initialize Vosk wake word detector

        Args:
            model_path: Path to Vosk model directory
            wake_words: List of wake word strings (e.g., ["helm", "advisor", "counsel"])
            sample_rate: Audio sample rate (default 16000 Hz)
            mic_device: ALSA device string (e.g., "plughw:3,0")
        """
        self.model_path = model_path
        self.wake_words = [w.lower() for w in wake_words]
        self.sample_rate = sample_rate
        self.mic_device = mic_device
        self.model = None
        self.recognizer = None

        print(f"[Vosk Wake Word] Initializing...", flush=True)
        print(f"  Model: {model_path}", flush=True)
        print(f"  Wake words: {', '.join(self.wake_words)}", flush=True)
        print(f"  Sample rate: {sample_rate} Hz", flush=True)
        print(f"  Mic device: {mic_device}", flush=True)

    def load_model(self):
        """Load Vosk model and create recognizer"""
        try:
            print(f"[Vosk Wake Word] Loading model from {self.model_path}...", flush=True)
            self.model = Model(self.model_path)

            # Create recognizer with keyphrase grammar
            # Vosk will look for these specific phrases in the audio stream
            self.recognizer = KaldiRecognizer(self.model, self.sample_rate)

            # Set keyphrase mode with our wake words
            # Format: '["phrase1", "phrase2", "phrase3"]'
            grammar = json.dumps(self.wake_words)
            self.recognizer.SetGrammar(grammar)

            print(f"[Vosk Wake Word] Model loaded successfully", flush=True)
            return True

        except Exception as e:
            print(f"[Vosk Wake Word] Error loading model: {e}", flush=True)
            return False

    def listen(self, callback=None, chunk_size=4000):
        """
        Listen for wake words continuously

        Args:
            callback: Function to call when wake word detected
                      Signature: callback(wake_word: str) -> None
            chunk_size: Audio chunk size in bytes (default 4000)

        Blocks until interrupted (Ctrl+C)
        """
        if not self.model or not self.recognizer:
            print(f"[Vosk Wake Word] Error: Model not loaded. Call load_model() first.", flush=True)
            return

        print(f"[Vosk Wake Word] Starting audio stream from {self.mic_device}...", flush=True)

        # Start arecord process to capture audio
        # -D: ALSA device
        # -f S16_LE: 16-bit signed little-endian
        # -r: Sample rate
        # -c 1: Mono (1 channel)
        cmd = [
            'arecord',
            '-D', self.mic_device,
            '-f', 'S16_LE',
            '-r', str(self.sample_rate),
            '-c', '1',
            '-t', 'raw'
        ]

        try:
            # Start recording process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            )

            print(f"[Vosk Wake Word] 🎤 Listening for wake words: {', '.join(self.wake_words)}", flush=True)

            # Process audio in chunks
            while True:
                # Read audio chunk
                data = process.stdout.read(chunk_size)

                if len(data) == 0:
                    break

                # Feed audio to recognizer
                if self.recognizer.AcceptWaveform(data):
                    # Full phrase recognized
                    result = json.loads(self.recognizer.Result())

                    if 'text' in result and result['text']:
                        detected_text = result['text'].lower().strip()

                        # Check if detected text matches any wake word
                        for wake_word in self.wake_words:
                            if wake_word in detected_text:
                                print(f"[Vosk Wake Word] ✓ Wake word detected: '{wake_word}'", flush=True)

                                # Call callback if provided
                                if callback:
                                    callback(wake_word)

                                # Reset recognizer for next detection
                                self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
                                grammar = json.dumps(self.wake_words)
                                self.recognizer.SetGrammar(grammar)

                                break
                else:
                    # Partial result (still processing)
                    partial = json.loads(self.recognizer.PartialResult())
                    if 'partial' in partial and partial['partial']:
                        # Optional: print partial results for debugging
                        # print(f"[Vosk Wake Word] Partial: {partial['partial']}", flush=True)
                        pass

        except KeyboardInterrupt:
            print(f"\n[Vosk Wake Word] Stopped by user", flush=True)
        except Exception as e:
            print(f"[Vosk Wake Word] Error during listening: {e}", flush=True)
        finally:
            if process:
                process.terminate()
                process.wait()

    def test_detection(self, duration=10):
        """
        Test wake word detection for a limited time

        Args:
            duration: How long to listen (seconds)

        Returns:
            List of detected wake words with timestamps
        """
        if not self.model or not self.recognizer:
            if not self.load_model():
                return []

        detections = []
        start_time = time.time()

        def record_detection(wake_word):
            timestamp = time.time() - start_time
            detections.append({
                'wake_word': wake_word,
                'timestamp': timestamp
            })
            print(f"[Vosk Wake Word] Detection at {timestamp:.2f}s: {wake_word}", flush=True)

        print(f"[Vosk Wake Word] Testing for {duration} seconds...", flush=True)
        print(f"[Vosk Wake Word] Please say: {', '.join(self.wake_words)}", flush=True)

        # Start listening in separate thread with timeout
        import threading

        listen_thread = threading.Thread(
            target=self.listen,
            args=(record_detection,)
        )
        listen_thread.daemon = True
        listen_thread.start()

        # Wait for duration
        time.sleep(duration)

        print(f"[Vosk Wake Word] Test complete. Detections: {len(detections)}", flush=True)
        return detections


def main():
    """Test script for Vosk wake word detector"""
    import argparse

    parser = argparse.ArgumentParser(description='Vosk Wake Word Detector Test')
    parser.add_argument('--model', default='/opt/d3kos/models/vosk/vosk-model-small-en-us-0.15',
                        help='Path to Vosk model directory')
    parser.add_argument('--words', nargs='+', default=['helm', 'advisor', 'counsel'],
                        help='Wake words to detect')
    parser.add_argument('--device', default='plughw:3,0',
                        help='ALSA device (e.g., plughw:3,0)')
    parser.add_argument('--test', action='store_true',
                        help='Run 30-second test instead of continuous mode')

    args = parser.parse_args()

    # Create detector
    detector = VoskWakeWordDetector(
        model_path=args.model,
        wake_words=args.words,
        mic_device=args.device
    )

    # Load model
    if not detector.load_model():
        print("Failed to load model. Exiting.")
        sys.exit(1)

    # Run test or continuous mode
    if args.test:
        # Test mode: 30 seconds
        detections = detector.test_detection(duration=30)

        print("\n=== Test Results ===")
        print(f"Total detections: {len(detections)}")
        for i, d in enumerate(detections, 1):
            print(f"  {i}. '{d['wake_word']}' at {d['timestamp']:.2f}s")
    else:
        # Continuous mode
        def on_wake_word(word):
            print(f"\n*** WAKE WORD DETECTED: {word.upper()} ***\n", flush=True)

        detector.listen(callback=on_wake_word)


if __name__ == '__main__':
    main()
