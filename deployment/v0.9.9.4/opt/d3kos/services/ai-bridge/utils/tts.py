"""
d3kOS AI Bridge — Text-to-speech wrapper

Primary engine: espeak-ng (confirmed working on Pi, piper has no voice model).
Audio device: plughw:S330,0 (Jabra S330 USB speaker confirmed on Pi).

Environment:
  TTS_ENGINE=espeak-ng    (default)
  AUDIO_DEVICE=plughw:S330,0
"""

import os
import json
import logging
import subprocess
import threading
import time

import numpy as np
import sounddevice as sd
import soundfile as sf

log = logging.getLogger(__name__)

TTS_ENGINE    = os.environ.get('TTS_ENGINE', 'espeak-ng')
AUDIO_DEVICE  = os.environ.get('AUDIO_DEVICE', 'plughw:S330,0')
SPEAKING_FILE = '/opt/d3kos/config/tts-speaking.json'
MUTE_FILE     = '/opt/d3kos/config/tts-mute.json'

# ── Speaking state flag ────────────────────────────────────────────────────────
def _write_speaking(speaking: bool):
    try:
        with open(SPEAKING_FILE, 'w') as fh:
            json.dump({'speaking': speaking}, fh)
    except Exception:
        pass


# ── TTSPlayer — chunk-based playback with pause/resume/stop ───────────────────
def _find_s330_device() -> int | None:
    """Return sounddevice index for the Anker S330 output, or None to use default."""
    try:
        for i, d in enumerate(sd.query_devices()):
            if ('S330' in d['name'] or 'Anker' in d['name']) and d['max_output_channels'] > 0:
                log.info('TTSPlayer using device %d: %s', i, d['name'])
                return i
    except Exception:
        pass
    return None


class TTSPlayer:
    def __init__(self):
        self.paused   = False
        self.stopped  = False
        self.position = 0
        self.lock     = threading.Lock()
        self.device   = _find_s330_device()

    def play(self, wav_file: str):
        """Load WAV and stream chunk-by-chunk. Supports pause/resume/stop mid-sentence."""
        try:
            data, samplerate = sf.read(wav_file, dtype='float32')
        except Exception as exc:
            log.warning('TTSPlayer: could not read %s — %s', wav_file, exc)
            return

        # Resample to device native rate if needed (S330 wants 48000Hz, Piper outputs 22050Hz)
        if self.device is not None:
            try:
                dev_rate = int(sd.query_devices(self.device, 'output')['default_samplerate'])
                if samplerate != dev_rate:
                    ratio = dev_rate / samplerate
                    new_len = int(len(data) * ratio)
                    if data.ndim == 1:
                        data = np.interp(np.linspace(0, len(data)-1, new_len),
                                         np.arange(len(data)), data).astype(np.float32)
                    else:
                        data = np.column_stack([
                            np.interp(np.linspace(0, len(data)-1, new_len),
                                      np.arange(len(data)), data[:, ch]).astype(np.float32)
                            for ch in range(data.shape[1])
                        ])
                    samplerate = dev_rate
            except Exception as exc:
                log.warning('TTSPlayer: resample failed — %s', exc)

        with self.lock:
            self.stopped = False
            self.paused  = False

        _write_speaking(True)

        def _play():
            i = self.position
            while i < len(data):
                with self.lock:
                    if self.stopped:
                        self.position = 0
                        _write_speaking(False)
                        return
                    if self.paused:
                        time.sleep(0.05)
                        continue
                sd.play(data[i:i + 1024], samplerate, device=self.device)
                sd.wait()
                i += 1024
            self.position = 0
            _write_speaking(False)

        threading.Thread(target=_play, daemon=True).start()

    def pause(self):
        with self.lock:
            self.paused = True

    def resume(self):
        with self.lock:
            self.paused = False

    def stop(self):
        with self.lock:
            self.stopped = True
            self.paused  = False
            self.position = 0
        sd.stop()
        _write_speaking(False)


player = TTSPlayer()

# ── Mute state ─────────────────────────────────────────────────────────────────
_muted = False
_active_procs: list[subprocess.Popen] = []
_procs_lock = threading.Lock()


def set_muted(muted: bool):
    """Mute or unmute TTS. Muting pauses TTSPlayer immediately; unmuting resumes."""
    global _muted
    _muted = muted
    if muted:
        player.pause()
        _kill_active()   # also kill any legacy espeak/aplay procs
    else:
        player.resume()


def is_muted() -> bool:
    return _muted


def _kill_active():
    """Kill any running espeak/aplay processes immediately."""
    with _procs_lock:
        for p in list(_active_procs):
            try:
                p.kill()
            except Exception:
                pass
        _active_procs.clear()


def speak(text: str, block: bool = False) -> bool:
    """
    Speak text aloud using the configured TTS engine.

    block=True  — wait for speech to finish before returning
    block=False — fire in background thread, return immediately

    Returns True if the command launched without error.
    Returns False immediately if muted.
    """
    if _muted:
        return False
    text = text.strip()
    if not text:
        return False

    if block:
        return _speak_sync(text)
    else:
        t = threading.Thread(target=_speak_sync, args=(text,), daemon=True)
        t.start()
        return True


def speak_urgent(text: str, repeat: int = 1):
    """
    Speak urgent alert text, optionally repeating N times (with 2-second gap).
    Always runs in background thread. Respects mute state.
    """
    def _run():
        for i in range(max(1, repeat)):
            if _muted:
                break
            _speak_sync(text)
            if i < repeat - 1:
                import time
                time.sleep(2)

    t = threading.Thread(target=_run, daemon=True)
    t.start()


def _speak_sync(text: str) -> bool:
    """Blocking speech call. Returns True on success."""
    engine = TTS_ENGINE.lower()

    try:
        if engine == 'espeak-ng':
            return _espeak(text)
        elif engine == 'piper':
            return _piper(text)
        elif engine == 'festival':
            return _festival(text)
        else:
            log.warning('Unknown TTS engine: %s — falling back to espeak-ng', engine)
            return _espeak(text)
    except Exception as exc:
        log.error('TTS speak failed: %s', exc)
        return False


def _espeak(text: str) -> bool:
    """
    espeak-ng: generate audio and pipe to aplay.
    Rate 140 wpm, amplitude 100, voice en-gb.
    """
    try:
        espeak_cmd = [
            'espeak-ng',
            '-v', 'en-gb',
            '-s', '140',    # words per minute
            '-a', '100',    # amplitude 0-200
            '--stdout',
            text,
        ]
        aplay_cmd = ['aplay', '-D', AUDIO_DEVICE, '-q']

        espeak_proc = subprocess.Popen(
            espeak_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        aplay_proc = subprocess.Popen(
            aplay_cmd,
            stdin=espeak_proc.stdout,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        espeak_proc.stdout.close()
        with _procs_lock:
            _active_procs.extend([espeak_proc, aplay_proc])
        try:
            aplay_proc.wait(timeout=30)
            espeak_proc.wait(timeout=5)
        finally:
            with _procs_lock:
                for p in [espeak_proc, aplay_proc]:
                    if p in _active_procs:
                        _active_procs.remove(p)
        return aplay_proc.returncode == 0
    except subprocess.TimeoutExpired:
        log.warning('TTS espeak-ng timed out')
        return False
    except FileNotFoundError:
        log.error('espeak-ng not found — install with: sudo apt install espeak-ng')
        return False


def _piper(text: str) -> bool:
    """
    Piper TTS: generate WAV to temp file, then stream via TTSPlayer (pause/resume/stop).
    Falls back to espeak-ng if piper binary or voice model is missing.
    """
    model_path = '/opt/d3kos/models/piper/en_US-amy-medium.onnx'
    if not os.path.isfile(model_path):
        log.warning('Piper voice model not found at %s — falling back to espeak-ng', model_path)
        return _espeak(text)

    wav_file = '/tmp/d3kos_tts.wav'
    try:
        piper_proc = subprocess.Popen(
            ['/usr/local/bin/piper', '--model', model_path, '--output_file', wav_file],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        piper_proc.communicate(input=text.encode())
        if piper_proc.returncode != 0:
            log.warning('Piper exited with code %d — falling back to espeak-ng', piper_proc.returncode)
            return _espeak(text)
    except FileNotFoundError:
        log.error('piper not found — falling back to espeak-ng')
        return _espeak(text)
    except Exception as exc:
        log.warning('Piper TTS failed: %s — falling back to espeak-ng', exc)
        return _espeak(text)

    player.play(wav_file)
    return True


def _festival(text: str) -> bool:
    """festival TTS fallback."""
    try:
        proc = subprocess.run(
            ['festival', '--tts'],
            input=text.encode(),
            timeout=30,
            capture_output=True,
        )
        return proc.returncode == 0
    except Exception as exc:
        log.warning('festival TTS failed: %s', exc)
        return False


def _shell_quote(text: str) -> str:
    """Basic shell quoting — replaces single quotes to prevent injection."""
    return "'" + text.replace("'", "'\\''") + "'"


def is_available() -> bool:
    """Returns True if the configured TTS engine binary exists."""
    engine = TTS_ENGINE.lower()
    binary = 'espeak-ng' if engine == 'espeak-ng' else engine
    try:
        subprocess.run(['which', binary], capture_output=True, check=True, timeout=3)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
