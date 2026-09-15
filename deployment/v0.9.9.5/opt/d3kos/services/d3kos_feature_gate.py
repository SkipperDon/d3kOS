# /opt/d3kos/services/d3kos_feature_gate.py
"""Hardware feature gate. Fails CLOSED: if the profile is unreadable, nothing is enabled."""
import json, os

_PROFILE_PATH  = '/opt/d3kos/config/hardware-profile.json'
_MANIFEST_PATH = '/opt/d3kos/config/capabilities-manifest.json'

_profile = None
_manifest = None
_profile_mtime = None


class FeatureGateUnavailable(RuntimeError):
    """Hardware profile missing or malformed."""


def _load():
    """Reload only when the profile file has actually been replaced.

    The probe writes via atomic rename, so st_mtime_ns changing is the signal.
    A bare stat() is cheap enough to call per lookup and is correct across
    processes — which an in-process version counter is not.
    """
    global _profile, _manifest, _profile_mtime
    try:
        mtime = os.stat(_PROFILE_PATH).st_mtime_ns
    except OSError as exc:
        raise FeatureGateUnavailable(f'cannot stat {_PROFILE_PATH}: {exc}') from exc
    if mtime == _profile_mtime and _profile is not None:
        return
    try:
        with open(_PROFILE_PATH) as fh:
            profile = json.load(fh)
        with open(_MANIFEST_PATH) as fh:
            manifest = json.load(fh)
    except (OSError, ValueError) as exc:
        raise FeatureGateUnavailable(f'cannot load hardware profile: {exc}') from exc
    _profile, _manifest, _profile_mtime = profile, manifest, mtime


def _accel_ok(req, accel) -> bool:
    if not req.get('accelerator_any'):
        return True                                    # feature needs no accelerator
    if not accel.get('present'):
        return False                                   # needs one, none fitted
    allowed = req.get('accelerator_class_any')
    if not allowed:
        return True                                    # any accelerator will do
    fitted = accel.get('accelerator_class') or []
    return any(c in fitted for c in allowed)           # whitelist enforced when fitted


def _unmet(key):
    """Yields (reason, upgrade_action) for each unmet requirement."""
    _load()
    feat = _manifest['features'].get(key)
    if feat is None:
        return None, [('Feature not defined.', None)]
    if feat.get('operator_override'):
        return feat, []
    req, plat = feat['requires'], _profile['platform']
    accel = _profile['accelerator']
    out = []
    if plat['pi_gen'] < req.get('pi_gen_min', 0):
        out.append((f"Requires Raspberry Pi {req['pi_gen_min']} "
                    f"(detected: Pi {plat['pi_gen']})",
                    f"Upgrade to Raspberry Pi {req['pi_gen_min']}"))
    if plat['ram_mb'] < req.get('ram_mb_min', 0):
        out.append((f"Requires {req['ram_mb_min']} MB RAM "
                    f"(detected: {plat['ram_mb']} MB)",
                    f"Install at least {req['ram_mb_min']} MB RAM"))
    if not _accel_ok(req, accel):
        allowed = req.get('accelerator_class_any') or ['any supported accelerator']
        out.append((f"Requires {' or '.join(allowed)}",
                    'Add a Hailo-8L AI HAT+ or Google Coral USB Accelerator'))
    return feat, out


def feature_available(key: str) -> bool:
    try:
        feat, unmet = _unmet(key)
    except FeatureGateUnavailable:
        return False                                   # fail closed
    return feat is not None and not unmet


def feature_reason(key: str) -> str:
    try:
        _, unmet = _unmet(key)
    except FeatureGateUnavailable as exc:
        return f'Hardware profile unavailable ({exc}). Run d3kos-probe.'
    return '. '.join(r for r, _ in unmet) or 'Hardware requirements met.'


def feature_upgrade_path(key: str) -> list:
    try:
        _, unmet = _unmet(key)
    except FeatureGateUnavailable:
        return []
    return [a for _, a in unmet if a]
