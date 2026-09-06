#!/usr/bin/env python3
"""
auto_enrol.py — Silent background auto-enrolment for d3kOS Pi.

Runs on first internet connection and periodically thereafter (via systemd timer).
Sends the device's Ed25519 public key to atmyboat.com for operator approval.
No user-facing output — all status written to journald and enrol-state.json.

Exit codes:
  0 — already enrolled (pending or approved) — timer can stop firing
  1 — enrolment attempted and succeeded (status: pending)
  2 — enrolment skipped (identity not ready, no internet)
  3 — enrolment failed (server error)
"""

import json
import logging
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_SERVICES_DIR    = Path('/opt/d3kos/services')
_TOKEN_FILE      = Path('/opt/d3kos/config/device-token.json')
_ENROL_STATE     = Path('/opt/d3kos/config/enrol-state.json')
_AMBOAT_BASE_URL = 'https://atmyboat.com'
_ENROL_PATH      = '/amboat-device/v1/enrol'

logging.basicConfig(
    level=logging.INFO,
    format='auto_enrol: %(levelname)s %(message)s',
    stream=sys.stdout,
)
log = logging.getLogger('auto_enrol')


def _read_state() -> dict:
    try:
        return json.loads(_ENROL_STATE.read_text()) if _ENROL_STATE.exists() else {}
    except Exception:
        return {}


def _write_state(state: dict) -> None:
    _ENROL_STATE.parent.mkdir(parents=True, exist_ok=True)
    _ENROL_STATE.write_text(json.dumps(state))
    _ENROL_STATE.chmod(0o600)


def main() -> int:
    # ── Identity check ────────────────────────────────────────────────────────
    if not _TOKEN_FILE.exists():
        log.info('identity not provisioned (device-token.json absent) — skipping')
        return 2

    try:
        token_data   = json.loads(_TOKEN_FILE.read_text())
        device_token = token_data['device_token']
    except Exception as e:
        log.warning(f'could not read device-token.json: {e}')
        return 2

    # ── Already enrolled? ─────────────────────────────────────────────────────
    state = _read_state()
    if state.get('status') in ('pending', 'approved'):
        log.info(f'already enrolled (status={state["status"]}) — nothing to do')
        return 0

    # ── Sign the request ──────────────────────────────────────────────────────
    sys.path.insert(0, str(_SERVICES_DIR))
    try:
        from device_sign import sign_device_request, get_public_key_b64
        auth_headers = sign_device_request(_ENROL_PATH)
        public_key   = get_public_key_b64()
    except FileNotFoundError:
        log.info('Ed25519 key absent (first-boot incomplete) — skipping')
        return 2
    except Exception as e:
        log.warning(f'could not sign request: {e}')
        return 2

    # ── POST to /enrol ────────────────────────────────────────────────────────
    try:
        import requests
        resp = requests.post(
            f'{_AMBOAT_BASE_URL}/wp-json{_ENROL_PATH}',
            json={
                'device_token': device_token,
                'public_key':   public_key,
                'note':         'auto-enrolment on first internet connection',
            },
            headers={
                **auth_headers,
                'Content-Type': 'application/json',
                'User-Agent':   'd3kOS/0.9.9.4 (auto-enrolment)',
            },
            timeout=15,
        )
    except Exception as e:
        log.warning(f'enrolment request failed (network): {e}')
        return 2

    if resp.status_code == 409:
        # Server already has this device — treat as enrolled
        log.info('server returned 409 (already enrolled) — marking pending')
        _write_state({'status': 'pending', 'enrolled_at': time.time()})
        return 0

    if resp.status_code == 200:
        data = resp.json()
        if data.get('status') == 'pending':
            log.info('enrolment succeeded — status: pending (awaiting operator approval)')
            _write_state({'status': 'pending', 'enrolled_at': time.time()})
            return 1

    # ── Unexpected response ───────────────────────────────────────────────────
    try:
        body = resp.json()
        msg  = body.get('message') or body.get('error') or str(body)
    except Exception:
        msg = resp.text[:200]
    log.warning(f'enrolment failed: HTTP {resp.status_code} — {msg}')
    return 3


if __name__ == '__main__':
    sys.exit(main())
