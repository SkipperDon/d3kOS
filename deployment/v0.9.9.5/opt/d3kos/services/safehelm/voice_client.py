# voice_client.py — sends advisory phrases to ai_bridge voice output (port 3002).
import logging
import requests

VOICE_URL = 'http://127.0.0.1:3002/webhook/alert'
_TIMEOUT_S = 2.0

logger = logging.getLogger('safehelm.voice')


def speak(message, repeat=1):
    """POST message to ai_bridge TTS endpoint. Returns True on success."""
    try:
        resp = requests.post(
            VOICE_URL,
            json={'message': message, 'repeat': repeat},
            timeout=_TIMEOUT_S)
        return resp.ok
    except Exception as exc:
        logger.warning('voice_client.speak failed: %s', exc)
        return False


def announce_startup():
    """ADV-2: announce SafeHelm is active on boot."""
    speak('SafeHelm collision advisory is active.')
