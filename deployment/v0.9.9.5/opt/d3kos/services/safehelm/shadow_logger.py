# shadow_logger.py — rotating diagnostic log. Cap prevents BUG-105-style runaway.
import logging
import logging.handlers
import os

_logger = None
_LOG_PATH = os.path.join(os.path.dirname(__file__), 'logs', 'shadow.log')
_MAX_BYTES = 5 * 1024 * 1024   # 5 MB per file
_BACKUP_COUNT = 3


def initialize(log_path=None):
    global _logger
    path = log_path or _LOG_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    _logger = logging.getLogger('safehelm.shadow')
    _logger.setLevel(logging.DEBUG)
    if not _logger.handlers:
        handler = logging.handlers.RotatingFileHandler(
            path, maxBytes=_MAX_BYTES, backupCount=_BACKUP_COUNT)
        handler.setFormatter(logging.Formatter('%(message)s'))
        _logger.addHandler(handler)


def record(now_iso, mmsi, cpa_m, tcpa_s, range_m, rule, tier):
    """Write one diagnostic line per target per tick. Best-effort; never raises."""
    try:
        if _logger is None:
            return
        tier_str = tier['tier'] if tier else 'none'
        _logger.debug('%s mmsi=%s cpa=%.1f tcpa=%.1f rng=%.1f rule=%s tier=%s',
                      now_iso, mmsi, cpa_m, tcpa_s, range_m, rule, tier_str)
    except Exception:
        pass
