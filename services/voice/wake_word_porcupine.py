#!/usr/bin/env python3
# d3kOS - Marine Intelligence Operating System
# Copyright (C) 2026 Donald Moskaluk / AtMyBoat.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# For commercial licensing contact: skipperdon@atmyboat.com

"""
Porcupine Wake Word Detector for d3kOS
Uses Picovoice Porcupine wake word engine
Commercial product with free tier (3 wake words)
Optimized for Raspberry Pi
"""

import sys
import struct
import subprocess
import time

try:
    import pvporcupine
    PORCUPINE_AVAILABLE = True
except ImportError:
    PORCUPINE_AVAILABLE = False
    print("[Porcupine] WARNING: pvporcupine not installed", flush=True)
    print("[Porcupine] Install with: pip3 install pvporcupine", flush=True)


class PorcupineWakeWordDetector:
    """
    Wake word detector using Picovoice Porcupine

    Porcupine features:
    - Optimized for edge devices (Raspberry Pi)
    - Very low CPU usage (~2-5%)
    - High accuracy (>95%)
    - Low false positive rate (<1%)
    - Customizable sensitivity
    - Free tier: Up to 3 custom wake words

    Requires:
    - Picovoice account (free tier available)
    - Access key from https://console.picovoice.ai/
    """

    def __init__(self, access_key, keywords, sensitivities=None,
                 sample_rate=16000, mic_device="plughw:3,0"):
        """
        Initialize Porcupine wake word detector

        Args:
            access_key: Picovoice Access Key from console.picovoice.ai
            keywords: List of keyword strings or paths to .ppn files
                      Built-in keywords: "alexa", "americano", "blueberry", "bumblebee",
                                        "computer", "grapefruit", "grasshopper", "hey google",
                                        "hey siri", "jarvis", "ok google", "picovoice",
                                        "porcupine", "terminator"
                      Custom keywords: Path to .ppn file from Porcupine console
            sensitivities: List of sensitivity values (0.0-1.0) for each keyword
                          Higher = more sensitive (more false positives)
                          Lower = less sensitive (might miss wake words)
                          Default: 0.5 for all keywords
            sample_rate: Audio sample rate (must be 16000 Hz for Porcupine)
            mic_device: ALSA device string
        """
        if not PORCUPINE_AVAILABLE:
            raise ImportError("pvporcupine module not installed")

        self.access_key = access_key
        self.keywords = keywords
        self.sensitivities = sensitivities or [0.5] * len(keywords)
        self.sample_rate = sample_rate
        self.mic_device = mic_device
        self.porcupine = None

        # Validate
        if sample_rate != 16000:
            raise ValueError("Porcupine requires 16000 Hz sample rate")

        if len(self.sensitivities) != len(self.keywords):
            raise ValueError("Number of sensitivities must match number of keywords")

        print(f"[Porcupine] Initializing...", flush=True)
        print(f"  Keywords: {', '.join(keywords)}", flush=True)
        print(f"  Sensitivities: {self.sensitivities}", flush=True)
        print(f"  Mic device: {mic_device}", flush=True)

    def load_model(self):
        """Initialize Porcupine engine"""
        try:
            print(f"[Porcupine] Creating Porcupine instance...", flush=True)

            self.porcupine = pvporcupine.create(
                access_key=self.access_key,
                keywords=self.keywords,
                sensitivities=self.sensitivities
            )

            print(f"[Porcupine] Loaded successfully", flush=True)
            print(f"  Frame length: {self.porcupine.frame_length}", flush=True)
            print(f"  Sample rate: {self.porcupine.sample_rate} Hz", flush=True)
            return True

        except Exception as e:
            print(f"[Porcupine] Error loading: {e}", flush=True)
            return False

    def listen(self, callback=None):
        """
        Listen for wake words continuously

        Args:
            callback: Function to call when wake word detected
                      Signature: callback(keyword_index: int, keyword: str) -> None

        Blocks until interrupted (Ctrl+C)
        """
        if not self.porcupine:
            print(f"[Porcupine] Error: Not initialized. Call load_model() first.", flush=True)
            return

        print(f"[Porcupine] Starting audio stream from {self.mic_device}...", flush=True)

        # Porcupine processes audio in fixed-size frames
        frame_length = self.porcupine.frame_length

        # Start arecord process
        cmd = [
            'arecord',
            '-D', self.mic_device,
            '-f', 'S16_LE',
            '-r', str(self.sample_rate),
            '-c', '1',
            '-t', 'raw'
        ]

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            )

            print(f"[Porcupine] 🎤 Listening for wake words: {', '.join(self.keywords)}", flush=True)

            # Process audio in frames
            while True:
                # Read exactly one frame of audio
                pcm_data = process.stdout.read(frame_length * 2)  # 2 bytes per sample (S16_LE)

                if len(pcm_data) != frame_length * 2:
                    print(f"[Porcupine] Incomplete frame, stopping", flush=True)
                    break

                # Convert bytes to 16-bit integers
                pcm = struct.unpack_from("h" * frame_length, pcm_data)

                # Process frame
                keyword_index = self.porcupine.process(pcm)

                if keyword_index >= 0:
                    # Wake word detected!
                    keyword = self.keywords[keyword_index]
                    print(f"[Porcupine] ✓ Wake word detected: '{keyword}' (index {keyword_index})", flush=True)

                    # Call callback if provided
                    if callback:
                        callback(keyword_index, keyword)

        except KeyboardInterrupt:
            print(f"\n[Porcupine] Stopped by user", flush=True)
        except Exception as e:
            print(f"[Porcupine] Error during listening: {e}", flush=True)
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
            List of detected wake words with timestamps and indices
        """
        if not self.porcupine:
            if not self.load_model():
                return []

        detections = []
        start_time = time.time()
        end_time = start_time + duration

        def record_detection(keyword_index, keyword):
            timestamp = time.time() - start_time
            detections.append({
                'keyword': keyword,
                'index': keyword_index,
                'timestamp': timestamp
            })
            print(f"[Porcupine] Detection at {timestamp:.2f}s: {keyword} (index {keyword_index})", flush=True)

        print(f"[Porcupine] Testing for {duration} seconds...", flush=True)
        print(f"[Porcupine] Please say: {', '.join(self.keywords)}", flush=True)

        # Listen with callback, but stop after duration
        import threading

        listen_thread = threading.Thread(
            target=self.listen,
            args=(record_detection,)
        )
        listen_thread.daemon = True
        listen_thread.start()

        # Wait for duration
        time.sleep(duration)

        print(f"[Porcupine] Test complete. Detections: {len(detections)}", flush=True)
        return detections

    def cleanup(self):
        """Clean up resources"""
        if self.porcupine:
            self.porcupine.delete()
            self.porcupine = None
            print(f"[Porcupine] Cleaned up", flush=True)

    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()


def get_porcupine_access_key():
    """
    Get Porcupine access key from config file

    Create free account at: https://console.picovoice.ai/
    Save access key to: /opt/d3kos/config/porcupine-access-key.txt
    """
    key_file = "/opt/d3kos/config/porcupine-access-key.txt"

    try:
        with open(key_file, 'r') as f:
            key = f.read().strip()
            if key:
                return key
    except FileNotFoundError:
        pass

    print(f"[Porcupine] Access key not found at {key_file}", flush=True)
    print(f"[Porcupine] Steps to get access key:", flush=True)
    print(f"  1. Create free account: https://console.picovoice.ai/", flush=True)
    print(f"  2. Go to: https://console.picovoice.ai/ppn", flush=True)
    print(f"  3. Copy Access Key", flush=True)
    print(f"  4. Save to: {key_file}", flush=True)
    return None


def main():
    """Test script for Porcupine wake word detector"""
    import argparse

    parser = argparse.ArgumentParser(description='Porcupine Wake Word Detector Test')
    parser.add_argument('--key', help='Picovoice Access Key (or use config file)')
    parser.add_argument('--keywords', nargs='+', default=['porcupine', 'alexa', 'computer'],
                        help='Keywords to detect (built-in or .ppn file paths)')
    parser.add_argument('--sensitivities', nargs='+', type=float,
                        help='Sensitivity values (0.0-1.0) for each keyword')
    parser.add_argument('--device', default='plughw:3,0',
                        help='ALSA device (e.g., plughw:3,0)')
    parser.add_argument('--test', action='store_true',
                        help='Run 30-second test instead of continuous mode')

    args = parser.parse_args()

    # Get access key
    access_key = args.key or get_porcupine_access_key()
    if not access_key:
        print("[Porcupine] ERROR: No access key provided. Exiting.")
        sys.exit(1)

    # Create detector
    try:
        detector = PorcupineWakeWordDetector(
            access_key=access_key,
            keywords=args.keywords,
            sensitivities=args.sensitivities,
            mic_device=args.device
        )
    except ImportError as e:
        print(f"[Porcupine] ERROR: {e}")
        print(f"[Porcupine] Install with: pip3 install pvporcupine")
        sys.exit(1)

    # Load model
    if not detector.load_model():
        print("[Porcupine] Failed to load. Exiting.")
        sys.exit(1)

    try:
        # Run test or continuous mode
        if args.test:
            # Test mode: 30 seconds
            detections = detector.test_detection(duration=30)

            print("\n=== Test Results ===")
            print(f"Total detections: {len(detections)}")
            for i, d in enumerate(detections, 1):
                print(f"  {i}. '{d['keyword']}' (index {d['index']}) at {d['timestamp']:.2f}s")
        else:
            # Continuous mode
            def on_wake_word(index, keyword):
                print(f"\n*** WAKE WORD DETECTED: {keyword.upper()} (index {index}) ***\n", flush=True)

            detector.listen(callback=on_wake_word)

    finally:
        detector.cleanup()


if __name__ == '__main__':
    main()
