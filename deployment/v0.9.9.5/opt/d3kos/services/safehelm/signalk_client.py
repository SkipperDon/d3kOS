# signalk_client.py — WebSocket consumer for Signal K AIS stream.
# BUG-46: Signal K WebSocket is ws://host:8099, NOT :3000 (dashboard port).
import json
import logging
import threading
import time

import websocket

SK_PORT = 8099
SK_PATH = '/signalk/v1/stream?subscribe=none'

logger = logging.getLogger('safehelm.signalk')


class SignalKClient:
    """Thread-safe AIS target cache. Targets are keyed by MMSI."""

    def __init__(self, host='localhost'):
        self._host = host
        self._targets = {}
        self._own = None
        self._lock = threading.Lock()
        self._ws = None
        self._thread = None
        self._running = False

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._ws:
            self._ws.close()

    def get_own(self):
        with self._lock:
            return self._own

    def get_targets(self):
        with self._lock:
            return list(self._targets.values())

    def _run(self):
        url = f'ws://{self._host}:{SK_PORT}{SK_PATH}'
        while self._running:
            try:
                self._ws = websocket.WebSocketApp(
                    url,
                    on_message=self._on_message,
                    on_error=self._on_error,
                    on_close=self._on_close)
                self._ws.run_forever()
            except Exception as exc:
                logger.warning('SignalK WS error: %s', exc)
            if self._running:
                time.sleep(5)

    def _on_message(self, ws, raw):
        try:
            msg = json.loads(raw)
            self._handle(msg)
        except Exception:
            pass

    def _on_error(self, ws, err):
        logger.debug('SignalK WS error: %s', err)

    def _on_close(self, ws, code, msg):
        logger.debug('SignalK WS closed')

    def _handle(self, msg):
        updates = msg.get('updates', [])
        for upd in updates:
            src = upd.get('$source', '')
            for v in upd.get('values', []):
                path = v.get('path', '')
                value = v.get('value')
                context = msg.get('context', '')
                if context.startswith('vessels.urn:mrn:imo:mmsi:'):
                    mmsi = context.split(':')[-1]
                    self._apply_vessel(mmsi, path, value)

    def _apply_vessel(self, mmsi, path, value):
        with self._lock:
            if mmsi not in self._targets:
                self._targets[mmsi] = _AISTarget(mmsi)
            self._targets[mmsi].apply(path, value)


class _AISTarget:
    def __init__(self, mmsi):
        self.mmsi = mmsi
        self.lat = None
        self.lon = None
        self.sog = 0.0
        self.cog = 0.0
        self.relative_bearing = 0.0
        self.vessel_class = None

    def apply(self, path, value):
        if path == 'navigation.position':
            if isinstance(value, dict):
                self.lat = value.get('latitude')
                self.lon = value.get('longitude')
        elif path == 'navigation.speedOverGround':
            self.sog = (value or 0.0) * 1.94384   # m/s to knots
        elif path == 'navigation.courseOverGroundTrue':
            import math
            self.cog = math.degrees(value or 0.0) % 360.0
