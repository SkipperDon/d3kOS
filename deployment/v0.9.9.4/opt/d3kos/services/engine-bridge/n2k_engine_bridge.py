#!/usr/bin/env python3
"""
d3kOS N2K Engine Bridge — CX5106 to Signal K
Reads raw CAN frames from SocketCAN can0, decodes CX5106 engine data
(PGN 193024 = DP=1 variant of NMEA 2000 PGN 127488), and injects
decoded values into Signal K via WebSocket delta.

Root cause of BUG-130: Matsutec CX5106 transmits with DataPage=1,
giving PGN 193024 (CAN ID 0x09F2xxxx) instead of the standard
PGN 127488 (CAN ID 0x08F2xxxx). canboat-js only decodes DP=0 PGNs.
This bridge handles the gap.

Filter strategy: match any frame with PF=0xF2, GE=0x00 (any SA, any DP).
This catches both PGN 127488 (DP=0) and PGN 193024 (DP=1) — the
standard and the CX5106 variant.
"""

import json
import logging
import socket
import struct
import sys
import threading
import time
from datetime import datetime, timezone

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [n2k-engine-bridge] %(levelname)s: %(message)s',
    stream=sys.stdout
)
log = logging.getLogger(__name__)

CAN_INTERFACE = 'can0'
SK_WS_URL     = 'ws://localhost:8099/signalk/v1/stream?subscribe=none'

# CAN frame struct: can_id(uint32 LE), dlc(uint8), 3-byte pad, 8-byte data
CAN_FRAME_FMT  = '<IB3x8s'
CAN_FRAME_SIZE = struct.calcsize(CAN_FRAME_FMT)
CAN_EFF_FLAG   = 0x80000000

# PGN 127488 / 193024 field layout (8-byte single frame)
#   Byte 0:   Engine Instance (0=port, 1=starboard, 0xFF=N/A)
#   Bytes 1-2 LE uint16: Speed raw (0.25 rev/min per unit; 0xFFFF=N/A)
#   Bytes 3-4 LE uint16: Boost Pressure raw (hPa; 0xFFFF=N/A)
#   Byte 5:   Tilt/Trim (int8 percent; 0x7F=N/A)
#   Bytes 6-7: Spare (0xFF)
INSTANCE_TO_NAME = {0: 'port', 1: 'starboard'}

# Thread-safe SK WebSocket handle
_sk_ws   = None
_sk_lock = threading.Lock()


def _is_engine_pgn(can_id):
    """True if frame has PF=0xF2 and GE=0x00 (PGN 127488 / 193024, any SA/DP)."""
    pf = (can_id >> 16) & 0xFF
    ge = (can_id >> 8) & 0xFF
    return pf == 0xF2 and ge == 0x00


def _decode_payload(data):
    """
    Decode 8-byte PGN 127488 payload.
    Returns dict with instance, revolutions (rev/s), boostPressure (Pa).
    """
    if len(data) < 6:
        return None
    instance   = data[0]
    speed_raw  = struct.unpack_from('<H', data, 1)[0]
    boost_raw  = struct.unpack_from('<H', data, 3)[0]

    result = {'instance': instance}
    if speed_raw != 0xFFFF:
        result['revolutions'] = (speed_raw * 0.25) / 60.0   # rev/s for Signal K
        result['rpm']         = speed_raw * 0.25
    if boost_raw != 0xFFFF:
        result['boostPressure'] = boost_raw * 100             # hPa → Pa

    return result


def _build_delta(decoded):
    """Build Signal K delta dict from decoded engine data."""
    instance = decoded.get('instance', 0)
    name     = INSTANCE_TO_NAME.get(instance, str(instance))
    values   = []

    if 'revolutions' in decoded:
        rev = decoded['revolutions']
        values.append({'path': f'propulsion.{name}.revolutions', 'value': rev})
        values.append({'path': f'propulsion.{instance}.revolutions', 'value': rev})

    if 'boostPressure' in decoded:
        bp = decoded['boostPressure']
        values.append({'path': f'propulsion.{name}.boostPressure', 'value': bp})

    if not values:
        return None

    return {
        'context': 'vessels.self',
        'updates': [{
            'source':    {'label': 'd3kos-n2k-bridge', 'type': 'NMEA2000'},
            'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
            'values':    values,
        }]
    }


def _sk_connect():
    """Connect to Signal K WebSocket; sets _sk_ws on success."""
    global _sk_ws
    try:
        import websocket as ws_lib
        ws = ws_lib.WebSocket()
        ws.connect(SK_WS_URL, timeout=5)
        log.info('Connected to Signal K WebSocket')
        with _sk_lock:
            _sk_ws = ws
        return True
    except ImportError:
        log.warning('websocket-client not installed — SK injection disabled. '
                    'Install: pip3 install websocket-client')
        return False
    except Exception as e:
        log.warning(f'SK WebSocket connect failed: {e}')
        return False


def _sk_reconnect_loop():
    """Background thread: reconnect SK WebSocket when disconnected."""
    while True:
        time.sleep(10)
        with _sk_lock:
            connected = _sk_ws is not None
        if not connected:
            _sk_connect()


def _send_to_sk(delta):
    """Send delta to Signal K, mark disconnected on failure."""
    global _sk_ws
    with _sk_lock:
        ws = _sk_ws
    if ws is None:
        return
    try:
        ws.send(json.dumps(delta))
    except Exception as e:
        log.warning(f'SK send failed: {e}')
        with _sk_lock:
            _sk_ws = None


def main():
    log.info('d3kOS N2K Engine Bridge starting (BUG-130 fix — PGN 193024)')

    # Start SK connection
    _sk_connect()
    reconnect_thread = threading.Thread(target=_sk_reconnect_loop, daemon=True)
    reconnect_thread.start()

    # Open SocketCAN socket
    try:
        sock = socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
        sock.bind((CAN_INTERFACE,))
        log.info(f'Listening on {CAN_INTERFACE}')
    except OSError as e:
        log.warning(f'Cannot open {CAN_INTERFACE}: {e}')
        time.sleep(30)
        sys.exit(1)

    frame_count  = 0
    engine_count = 0

    while True:
        try:
            raw = sock.recv(CAN_FRAME_SIZE)
            if len(raw) < CAN_FRAME_SIZE:
                continue

            can_id_raw, dlc, data = struct.unpack(CAN_FRAME_FMT, raw)
            can_id = can_id_raw & ~CAN_EFF_FLAG

            frame_count += 1
            if frame_count % 1000 == 0:
                log.info(f'Frames: {frame_count} total, {engine_count} engine')

            if not _is_engine_pgn(can_id):
                continue

            engine_count += 1
            dp      = (can_id >> 24) & 0x01
            sa      = can_id & 0xFF
            pgn_num = (dp << 17) | (0xF2 << 8) | 0x00

            decoded = _decode_payload(bytes(data[:min(dlc, 8)]))
            if decoded is None:
                continue

            rpm = decoded.get('rpm')
            log.debug(f'PGN {pgn_num} (DP={dp} SA={sa}): RPM={rpm:.0f if rpm is not None else "N/A"}')

            delta = _build_delta(decoded)
            if delta:
                _send_to_sk(delta)

        except KeyboardInterrupt:
            log.info('Stopped by operator')
            break
        except Exception as e:
            log.error(f'Frame error: {e}')
            time.sleep(1)

    sock.close()


if __name__ == '__main__':
    main()
