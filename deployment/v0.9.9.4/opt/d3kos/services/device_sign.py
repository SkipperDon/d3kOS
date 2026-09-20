"""
d3kOS device request signing helper — BUG-66 Phase B.

Provides Ed25519-signed HTTP headers for Pi→server requests.
Used by cloud_agent.py, export_worker.py, fleet_push_service.py (Phase C wiring).

The private key lives at /opt/d3kos/config/device-signing.key (32 bytes raw, mode 0600).
It is generated on first boot by regenerate-identity.sh and never baked into an image.

Importable from any service that adds /opt/d3kos/services to sys.path:
    from device_sign import sign_device_request, get_public_key_b64

All functions raise FileNotFoundError if the key files are absent (they must not be
swallowed silently — a missing key means the device has not completed first-boot
identity setup and the caller should back off and retry).
"""

import base64
import json
import os
import time
import uuid
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import (
    Encoding, PrivateFormat, PublicFormat, NoEncryption
)

_SIGNING_KEY = Path('/opt/d3kos/config/device-signing.key')
_SIGNING_PUB = Path('/opt/d3kos/config/device-signing.pub')
_TOKEN_FILE  = Path('/opt/d3kos/config/device-token.json')


def _load_private_key() -> Ed25519PrivateKey:
    """Load private key from disk. Raises FileNotFoundError if absent."""
    with open(_SIGNING_KEY, 'rb') as f:
        priv_raw = f.read()
    return Ed25519PrivateKey.from_private_bytes(priv_raw)


def _load_device_token() -> str:
    """Load device_token UUID from device-token.json. Raises FileNotFoundError if absent."""
    with open(_TOKEN_FILE) as f:
        return json.load(f)['device_token']


def sign_device_request(path: str) -> dict:
    """
    Return a dict of HTTP headers that authenticate a Pi→server request.

    The message signed is: device_token|timestamp|nonce|path
    This ties the signature to the specific endpoint and a specific moment in time.

    Headers returned:
        X-Device-Token  — the device's UUID (lookup hint only; signature decides identity)
        X-Timestamp     — Unix time as a decimal string (server rejects skew > 600 s)
        X-Nonce         — UUID4 (server caches for 600 s to prevent replay)
        X-Signature     — base64(Ed25519.sign(message))

    Raises:
        FileNotFoundError — device-signing.key or device-token.json absent (first-boot incomplete)
        ValueError        — key file is corrupt or wrong length
    """
    priv_key     = _load_private_key()
    device_token = _load_device_token()

    ts    = str(int(time.time()))
    nonce = str(uuid.uuid4())
    message = f"{device_token}|{ts}|{nonce}|{path}".encode()

    sig_raw = priv_key.sign(message)
    sig_b64 = base64.b64encode(sig_raw).decode()

    return {
        'X-Device-Token': device_token,
        'X-Timestamp':    ts,
        'X-Nonce':        nonce,
        'X-Signature':    sig_b64,
    }


def get_public_key_b64() -> str:
    """
    Return the device's Ed25519 public key as base64 (for the /enrol endpoint).

    Reads from device-signing.pub (written alongside the private key by regenerate-identity.sh).
    Falls back to deriving it from the private key if device-signing.pub is absent.

    Raises:
        FileNotFoundError — device-signing.key absent (first-boot incomplete)
    """
    if _SIGNING_PUB.exists():
        with open(_SIGNING_PUB, 'rb') as f:
            raw = f.read()
        if len(raw) != 32:
            raise ValueError(
                f'device-signing.pub is {len(raw)} bytes (expected 32 raw bytes) — '
                'run regenerate-identity.sh to rebuild the signing keypair'
            )
        return base64.b64encode(raw).decode()

    # Fallback: derive from private key
    priv_key = _load_private_key()
    pub_raw  = priv_key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    return base64.b64encode(pub_raw).decode()
