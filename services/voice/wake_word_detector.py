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
Unified Wake Word Detector for d3kOS
Abstraction layer supporting multiple wake word engines:
- Vosk (keyphrase spotting)
- Porcupine (commercial, free tier)

Provides drop-in replacement for PocketSphinx wake word detection
"""

import os
import sys

# Import wake word engines
try:
    from wake_word_vosk import VoskWakeWordDetector
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False

try:
    from wake_word_porcupine import PorcupineWakeWordDetector, get_porcupine_access_key
    import pvporcupine
    PORCUPINE_AVAILABLE = True
except ImportError:
    PORCUPINE_AVAILABLE = False


class WakeWordDetector:
    """
    Unified wake word detection interface

    Automatically selects best available engine:
    1. Porcupine (if access key available) - BEST PERFORMANCE
    2. Vosk (if model available) - GOOD FALLBACK
    3. Error if neither available

    Usage:
        # Auto-select engine
        detector = WakeWordDetector(wake_words=['helm', 'advisor', 'counsel'])
        detector.load_model()
        detector.listen(callback=on_wake_word)

        # Force specific engine
        detector = WakeWordDetector(wake_words=['helm'], engine='vosk')
        detector.listen()
    """

    def __init__(self, wake_words, engine='auto', **kwargs):
        """
        Initialize unified wake word detector

        Args:
            wake_words: List of wake word strings
            engine: Which engine to use ('auto', 'vosk', 'porcupine')
            **kwargs: Engine-specific parameters:
                - vosk_model: Path to Vosk model
                - porcupine_key: Porcupine access key
                - sensitivities: Porcupine sensitivity values
                - mic_device: ALSA device (default: plughw:3,0)
                - sample_rate: Audio sample rate (default: 16000)
        """
        self.wake_words = wake_words
        self.engine_name = engine
        self.kwargs = kwargs
        self.detector = None
        self.engine_type = None

        # Extract common parameters
        self.mic_device = kwargs.get('mic_device', 'plughw:3,0')
        self.sample_rate = kwargs.get('sample_rate', 16000)

        print(f"[Wake Word Detector] Initializing...", flush=True)
        print(f"  Wake words: {', '.join(wake_words)}", flush=True)
        print(f"  Engine: {engine}", flush=True)

        # Select engine
        self._select_engine()

    def _select_engine(self):
        """Select best available wake word engine"""

        if self.engine_name == 'auto':
            # Auto-select best engine
            print(f"[Wake Word Detector] Auto-selecting engine...", flush=True)

            # Try Porcupine first (best performance)
            if PORCUPINE_AVAILABLE:
                porcupine_key = self.kwargs.get('porcupine_key') or get_porcupine_access_key()
                if porcupine_key:
                    print(f"[Wake Word Detector] ✓ Porcupine available with access key", flush=True)
                    self.engine_name = 'porcupine'
                    self._init_porcupine(porcupine_key)
                    return
                else:
                    print(f"[Wake Word Detector] ⚠ Porcupine available but no access key", flush=True)

            # Try Vosk (good fallback)
            if VOSK_AVAILABLE:
                vosk_model = self.kwargs.get('vosk_model', '/opt/d3kos/models/vosk/vosk-model-small-en-us-0.15')
                if os.path.exists(vosk_model):
                    print(f"[Wake Word Detector] ✓ Vosk available with model", flush=True)
                    self.engine_name = 'vosk'
                    self._init_vosk(vosk_model)
                    return
                else:
                    print(f"[Wake Word Detector] ⚠ Vosk available but model not found: {vosk_model}", flush=True)

            # No engine available
            raise RuntimeError("No wake word engine available. Install Vosk or Porcupine.")

        elif self.engine_name == 'vosk':
            # Force Vosk
            if not VOSK_AVAILABLE:
                raise ImportError("Vosk not available. Install with: pip3 install vosk")

            vosk_model = self.kwargs.get('vosk_model', '/opt/d3kos/models/vosk/vosk-model-small-en-us-0.15')
            self._init_vosk(vosk_model)

        elif self.engine_name == 'porcupine':
            # Force Porcupine
            if not PORCUPINE_AVAILABLE:
                raise ImportError("Porcupine not available. Install with: pip3 install pvporcupine")

            porcupine_key = self.kwargs.get('porcupine_key') or get_porcupine_access_key()
            if not porcupine_key:
                raise ValueError("Porcupine access key required. Get from: https://console.picovoice.ai/")

            self._init_porcupine(porcupine_key)

        else:
            raise ValueError(f"Unknown engine: {self.engine_name}")

    def _init_vosk(self, vosk_model):
        """Initialize Vosk wake word detector"""
        print(f"[Wake Word Detector] Using Vosk engine", flush=True)

        self.detector = VoskWakeWordDetector(
            model_path=vosk_model,
            wake_words=self.wake_words,
            sample_rate=self.sample_rate,
            mic_device=self.mic_device
        )
        self.engine_type = 'vosk'

    def _init_porcupine(self, access_key):
        """Initialize Porcupine wake word detector"""
        print(f"[Wake Word Detector] Using Porcupine engine", flush=True)

        # Porcupine requires built-in keywords or .ppn files
        # For now, use built-in keywords as test
        # TODO: Train custom wake words for "helm", "advisor", "counsel"
        keywords = self.kwargs.get('porcupine_keywords', ['porcupine', 'alexa', 'computer'])
        sensitivities = self.kwargs.get('sensitivities', [0.5] * len(keywords))

        self.detector = PorcupineWakeWordDetector(
            access_key=access_key,
            keywords=keywords,
            sensitivities=sensitivities,
            sample_rate=self.sample_rate,
            mic_device=self.mic_device
        )
        self.engine_type = 'porcupine'

    def load_model(self):
        """Load wake word detection model"""
        if not self.detector:
            raise RuntimeError("No detector initialized")

        return self.detector.load_model()

    def listen(self, callback=None):
        """
        Listen for wake words continuously

        Args:
            callback: Function to call when wake word detected
                      For Vosk: callback(wake_word: str)
                      For Porcupine: callback(keyword_index: int, keyword: str)

        To make callbacks compatible, we normalize Porcupine callback:
        """
        if not self.detector:
            raise RuntimeError("No detector initialized")

        # Normalize callback for Porcupine
        if self.engine_type == 'porcupine' and callback:
            original_callback = callback

            def porcupine_callback(keyword_index, keyword):
                # Call with just keyword (ignore index)
                original_callback(keyword)

            self.detector.listen(callback=porcupine_callback)
        else:
            # Vosk callback is already correct format
            self.detector.listen(callback=callback)

    def test_detection(self, duration=10):
        """Test wake word detection for limited time"""
        if not self.detector:
            raise RuntimeError("No detector initialized")

        return self.detector.test_detection(duration=duration)

    def cleanup(self):
        """Clean up resources"""
        if self.detector and hasattr(self.detector, 'cleanup'):
            self.detector.cleanup()

    def get_info(self):
        """Get information about current engine"""
        return {
            'engine': self.engine_name,
            'engine_type': self.engine_type,
            'wake_words': self.wake_words,
            'mic_device': self.mic_device,
            'sample_rate': self.sample_rate,
            'vosk_available': VOSK_AVAILABLE,
            'porcupine_available': PORCUPINE_AVAILABLE
        }

    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()


def main():
    """Test script for unified wake word detector"""
    import argparse

    parser = argparse.ArgumentParser(description='Unified Wake Word Detector Test')
    parser.add_argument('--engine', choices=['auto', 'vosk', 'porcupine'], default='auto',
                        help='Wake word engine to use')
    parser.add_argument('--words', nargs='+', default=['helm', 'advisor', 'counsel'],
                        help='Wake words to detect')
    parser.add_argument('--device', default='plughw:3,0',
                        help='ALSA device (e.g., plughw:3,0)')
    parser.add_argument('--test', action='store_true',
                        help='Run 30-second test instead of continuous mode')
    parser.add_argument('--vosk-model', default='/opt/d3kos/models/vosk/vosk-model-small-en-us-0.15',
                        help='Path to Vosk model directory')
    parser.add_argument('--porcupine-key', help='Porcupine access key')

    args = parser.parse_args()

    # Create detector
    try:
        detector = WakeWordDetector(
            wake_words=args.words,
            engine=args.engine,
            mic_device=args.device,
            vosk_model=args.vosk_model,
            porcupine_key=args.porcupine_key
        )
    except Exception as e:
        print(f"[Wake Word Detector] ERROR: {e}")
        sys.exit(1)

    # Show engine info
    info = detector.get_info()
    print("\n=== Engine Info ===")
    print(f"Engine: {info['engine']} ({info['engine_type']})")
    print(f"Wake words: {', '.join(info['wake_words'])}")
    print(f"Mic device: {info['mic_device']}")
    print(f"Vosk available: {info['vosk_available']}")
    print(f"Porcupine available: {info['porcupine_available']}")
    print("")

    # Load model
    if not detector.load_model():
        print("[Wake Word Detector] Failed to load model. Exiting.")
        sys.exit(1)

    try:
        # Run test or continuous mode
        if args.test:
            # Test mode: 30 seconds
            detections = detector.test_detection(duration=30)

            print("\n=== Test Results ===")
            print(f"Total detections: {len(detections)}")
            for i, d in enumerate(detections, 1):
                if 'wake_word' in d:  # Vosk
                    print(f"  {i}. '{d['wake_word']}' at {d['timestamp']:.2f}s")
                elif 'keyword' in d:  # Porcupine
                    print(f"  {i}. '{d['keyword']}' at {d['timestamp']:.2f}s")
        else:
            # Continuous mode
            def on_wake_word(word):
                print(f"\n*** WAKE WORD DETECTED: {word.upper()} ***\n", flush=True)

            detector.listen(callback=on_wake_word)

    finally:
        detector.cleanup()


if __name__ == '__main__':
    main()
