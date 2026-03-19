"""
d3kOS AI Bridge — Text-to-speech wrapper

Primary engine: espeak-ng (confirmed working on Pi, piper has no voice model).
Audio device: plughw:S330,0 (Jabra S330 USB speaker confirmed on Pi).

Environment:
  TTS_ENGINE=espeak-ng    (default)
  AUDIO_DEVICE=plughw:S330,0
"""

import os
import logging
import subprocess
import threading

log = logging.getLogger(__name__)

TTS_ENGINE   = os.environ.get('TTS_ENGINE', 'espeak-ng')
AUDIO_DEVICE = os.environ.get('AUDIO_DEVICE', 'plughw:S330,0')

# ── Mute state ─────────────────────────────────────────────────────────────────
_muted = False
_active_procs: list[subprocess.Popen] = []
_procs_lock = threading.Lock()


def set_muted(muted: bool):
    """Mute or unmute TTS. Muting immediately kills any active speech subprocess."""
    global _muted
    _muted = muted
    if muted:
        _kill_active()


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
    piper TTS: requires voice model at /usr/share/piper/voices/en_US-lessac-medium.onnx
    Not currently available on Pi (no voice model installed) — fall back to espeak-ng.
    """
    model_path = '/usr/share/piper/voices/en_US-lessac-medium.onnx'
    if not os.path.isfile(model_path):
        log.warning('Piper voice model not found at %s — falling back to espeak-ng', model_path)
        return _espeak(text)

    try:
        cmd = [
            'bash', '-c',
            f'echo {_shell_quote(text)} | piper --model {model_path} --output_raw '
            f'| aplay -D {AUDIO_DEVICE} -r 22050 -f S16_LE -c 1 -q',
        ]
        result = subprocess.run(cmd, timeout=30, capture_output=True)
        return result.returncode == 0
    except Exception as exc:
        log.warning('Piper TTS failed: %s', exc)
        return False


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
