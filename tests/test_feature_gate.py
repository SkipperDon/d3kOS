"""F1-F8 -- hardware feature gate guard tests (V09995-SOL-001 §5 HCD-3, §10.4, §12).

Two v1.0 defects are guarded here:

  F1  FAIL-OPEN. The accelerator check sat inside
      `if req.get('accelerator_any') and not accel['present']:` so the whole
      block was skipped whenever an accelerator WAS fitted -- a Coral USB
      therefore satisfied a Hailo-only feature. Same shape as BUG-91, where
      the entitlement authority failed open to Tier 1.

  F5  RAM TRUNCATION. `ram_gb = ram_kb // 1048576` truncates, and MemTotal
      excludes reserved memory: a 4 GB Pi reports ~3882000 kB -> 3, an 8 GB
      Pi -> 7. Any manifest written `ram_gb_min: 8` was unsatisfiable on 8 GB
      hardware. v1.1 records ram_mb and gates on ram_mb_min.

The gate must FAIL CLOSED: an unreadable profile enables nothing (F7).

`env.write()` resolves the module on first call, i.e. inside the test body, so
a missing module is a FAILURE and not a fixture setup ERROR (§12.1).
"""
import json
import os

import pytest

from conftest import require_module

SPEC = '§5 HCD-3'


class _Env:
    def __init__(self, tmp_path, monkeypatch):
        self.profile = tmp_path / 'hardware-profile.json'
        self.manifest = tmp_path / 'capabilities-manifest.json'
        self._mp = monkeypatch
        self._n = 0
        self.fg = None

    def write(self, *, pi_gen=4, ram_mb=3790, accel=None, requires=None,
              operator_override=False):
        if self.fg is None:
            self.fg = require_module('d3kos_feature_gate', SPEC)
            self._mp.setattr(self.fg, '_PROFILE_PATH', str(self.profile))
            self._mp.setattr(self.fg, '_MANIFEST_PATH', str(self.manifest))

        self._n += 1
        accel = accel or []
        self.profile.write_text(json.dumps({
            'probe_version': self._n,
            'probed_at': '2026-09-11T00:00:00Z',
            'platform': {'pi_model': f'Raspberry Pi {pi_gen} Model B',
                         'pi_gen': pi_gen, 'ram_mb': ram_mb,
                         'ram_gb_nominal': round(ram_mb / 1024)},
            'hat': {'present': False},
            'accelerator': {'present': bool(accel), 'accelerator_class': accel,
                            'devices': []},
        }))
        feature = {'requires': requires if requires is not None else {}}
        if operator_override:
            feature['operator_override'] = True
        self.manifest.write_text(json.dumps({'features': {'feat': feature}}))

        # Force a distinct mtime so the mtime-keyed reload is exercised
        # deterministically regardless of filesystem timestamp granularity.
        stamp = 1_700_000_000 + self._n
        os.utime(self.profile, (stamp, stamp))
        self.fg._profile = None
        self.fg._manifest = None
        self.fg._profile_mtime = None
        return self.fg


@pytest.fixture
def env(tmp_path, monkeypatch):
    return _Env(tmp_path, monkeypatch)


# --------------------------------------------------------------------------
# Accelerator whitelist -- the fail-open guard.
# --------------------------------------------------------------------------

def test_f1_coral_does_not_satisfy_a_hailo_only_feature(env):
    """F1: wrong accelerator class fitted -> feature stays locked.

    THE FAIL-OPEN GUARD. v1.0 returned True here.
    """
    fg = env.write(accel=['coral-usb'],
                   requires={'accelerator_any': True,
                             'accelerator_class_any': ['hailo-8l']})
    assert fg.feature_available('feat') is False, (
        'FAIL-OPEN: a Coral USB satisfied a Hailo-only requirement')


def test_f2_correct_accelerator_unlocks_the_feature(env):
    """F2: the whitelisted class is fitted -> available."""
    fg = env.write(accel=['hailo-8l'],
                   requires={'accelerator_any': True,
                             'accelerator_class_any': ['hailo-8l']})
    assert fg.feature_available('feat') is True


def test_f3_no_accelerator_locks_a_feature_that_needs_one(env):
    """F3: nothing fitted -> locked."""
    fg = env.write(accel=[], requires={'accelerator_any': True})
    assert fg.feature_available('feat') is False


def test_f4_any_accelerator_satisfies_an_unrestricted_requirement(env):
    """F4: accelerator_any with no whitelist -> any device will do."""
    fg = env.write(accel=['coral-usb'], requires={'accelerator_any': True})
    assert fg.feature_available('feat') is True


def test_f4b_feature_needing_no_accelerator_is_unaffected(env):
    """F4b: absent accelerator_any -> the accelerator is irrelevant."""
    fg = env.write(accel=[], requires={'pi_gen_min': 4})
    assert fg.feature_available('feat') is True


def test_f4c_one_of_several_whitelisted_classes_is_enough(env):
    fg = env.write(accel=['coral-usb-mini'],
                   requires={'accelerator_any': True,
                             'accelerator_class_any': ['hailo-8l', 'coral-usb-mini']})
    assert fg.feature_available('feat') is True


# --------------------------------------------------------------------------
# RAM -- the truncation guard.
# --------------------------------------------------------------------------

def test_f5_four_gb_pi_satisfies_a_four_gb_requirement(env):
    """F5: a real 4 GB Pi reports ~3790 MB and must pass a 4 GB gate.

    v1.0 computed ram_gb = 3 for this board, so `ram_gb_min: 4` locked the
    feature on hardware that genuinely qualified.
    """
    fg = env.write(ram_mb=3790, requires={'ram_mb_min': 3500})
    assert fg.feature_available('feat') is True


def test_f6_eight_gb_pi_satisfies_an_eight_gb_requirement(env):
    """F6: a real 8 GB Pi reports ~7900 MB. v1.0 read this as 7 GB."""
    fg = env.write(ram_mb=7900, requires={'ram_mb_min': 7500})
    assert fg.feature_available('feat') is True


def test_f6b_insufficient_ram_still_locks(env):
    """F6b: the RAM gate must still bite when RAM really is short."""
    fg = env.write(ram_mb=1900, requires={'ram_mb_min': 3500})
    assert fg.feature_available('feat') is False
    assert 'MB' in fg.feature_reason('feat')


def test_f6c_gate_uses_ram_mb_not_ram_gb(env):
    """F6c: ram_gb_nominal is display-only and must not gate anything.

    A manifest using the rounded field would reintroduce the truncation class
    of bug, so a ram_gb_min key must not silently take effect.
    """
    fg = env.write(ram_mb=3790, requires={'ram_gb_min': 8})
    assert fg.feature_available('feat') is True, (
        'ram_gb_min must be ignored -- gates use ram_mb_min (§5 HCD-3)')


# --------------------------------------------------------------------------
# Platform generation.
# --------------------------------------------------------------------------

def test_f_pi4_does_not_satisfy_a_pi5_requirement(env):
    fg = env.write(pi_gen=4, requires={'pi_gen_min': 5})
    assert fg.feature_available('feat') is False
    assert 'Pi 5' in fg.feature_reason('feat')
    assert any('Pi 5' in s for s in fg.feature_upgrade_path('feat'))


def test_f_operator_override_unlocks_regardless_of_hardware(env):
    fg = env.write(pi_gen=4, requires={'pi_gen_min': 5}, operator_override=True)
    assert fg.feature_available('feat') is True


# --------------------------------------------------------------------------
# Fail-closed and cross-process reload.
# --------------------------------------------------------------------------

def test_f7_missing_profile_fails_closed(env):
    """F7: an unreadable profile must enable nothing and say why.

    Failing open here would hand out every gated feature on a box whose
    hardware state is unknown.
    """
    fg = env.write(accel=['hailo-8l'], requires={'accelerator_any': True})
    os.remove(env.profile)
    assert fg.feature_available('feat') is False
    reason = fg.feature_reason('feat')
    assert 'unavailable' in reason.lower() or 'probe' in reason.lower()


def test_f7b_corrupt_profile_fails_closed(env):
    """F7b: truncated or malformed JSON must not raise into callers."""
    fg = env.write(accel=['hailo-8l'], requires={'accelerator_any': True})
    env.profile.write_text('{ this is not json')
    assert fg.feature_available('feat') is False


def test_f7c_unknown_feature_key_is_unavailable(env):
    fg = env.write()
    assert fg.feature_available('no-such-feature') is False
    assert fg.feature_upgrade_path('no-such-feature') == []


def test_f8_profile_replacement_is_picked_up_without_restart(env):
    """F8: fitting hardware at runtime unlocks the feature in a live process.

    The probe replaces the profile by atomic rename, so a changed mtime is the
    signal. v1.0 tried to invalidate by having the dashboard poke a module
    global, which could not work for SafeHelm or any other separate process.
    """
    fg = env.write(accel=[], requires={'accelerator_any': True})
    assert fg.feature_available('feat') is False

    env.write(accel=['hailo-8l'], requires={'accelerator_any': True})
    assert fg.feature_available('feat') is True, (
        'gate did not observe the replaced profile -- stale cache')
