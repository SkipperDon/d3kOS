"""
D17 Hardware Capability Detection — guard tests.
Validates: hardware-probe.sh invariants, d3kos_feature_gate.py logic,
capabilities-manifest.json schema, systemd/udev units, app.py routes.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

# Paths under the v0.9.9.5 tree
PROBE     = ROOT / 'deployment/v0.9.9.5/opt/d3kos/scripts/hardware-probe.sh'
GATE      = ROOT / 'deployment/v0.9.9.5/opt/d3kos/services/d3kos_feature_gate.py'
MANIFEST  = ROOT / 'deployment/v0.9.9.5/opt/d3kos/config/capabilities-manifest.json'
SERVICE   = ROOT / 'deployment/v0.9.9.5/etc/systemd/system/d3kos-hardware-probe.service'
TIMER     = ROOT / 'deployment/v0.9.9.5/etc/systemd/system/d3kos-hardware-probe.timer'
UDEV      = ROOT / 'deployment/v0.9.9.5/etc/udev/rules.d/99-d3kos-accelerator.rules'
APP       = ROOT / 'deployment/v0.9.9.5/opt/d3kos/services/dashboard/app.py'
HARDWARE_HTML = ROOT / 'deployment/v0.9.9.5/opt/d3kos/services/dashboard/templates/hardware.html'


# ─── hardware-probe.sh invariants ────────────────────────────────────────────

def test_probe_uses_ram_mb_not_ram_gb():
    """A1: probe calculates ram_mb = ram_kb / 1024 (not /1048576 which truncates)."""
    content = PROBE.read_text()
    assert 'ram_mb=$(( ram_kb / 1024 ))' in content, \
        'hardware-probe.sh must use ram_kb/1024 (MB) not /1048576 (GB)'


def test_probe_atomic_rename():
    """A4: profile is written via atomic mv from a tmp file."""
    content = PROBE.read_text()
    assert 'mv "$TMP" "$PROFILE"' in content, \
        'hardware-probe.sh must use atomic mv for profile write'


def test_probe_tmp_cleanup_trap():
    """probe uses trap to clean up tmp on exit."""
    content = PROBE.read_text()
    assert "trap 'rm -f \"$TMP\"' EXIT" in content or \
           "trap" in content and "rm -f" in content and "TMP" in content, \
        'hardware-probe.sh must trap EXIT to clean up tmp file'


def test_probe_chmod_after_move():
    """A8: chmod 644 applied after atomic rename."""
    content = PROBE.read_text()
    assert 'chmod 644 "$PROFILE"' in content, \
        'hardware-probe.sh must chmod 644 profile after mv'


def test_probe_content_hash_excludes_volatile_fields():
    """A6: content_hash is computed excluding probe_version and probed_at."""
    content = PROBE.read_text()
    assert 'probe_version' in content and 'probed_at' in content, \
        'hardware-probe.sh must exclude probe_version and probed_at from hash'
    # The del() call on jq to strip those fields before hashing
    assert 'del(' in content, \
        'hardware-probe.sh must use jq del() to strip volatile fields for hash'


# ─── d3kos_feature_gate.py invariants ────────────────────────────────────────

def test_gate_fails_closed_import():
    """Gate module is importable and defines FeatureGateUnavailable."""
    gate_path = str(GATE.parent)
    if gate_path not in sys.path:
        sys.path.insert(0, gate_path)
    import d3kos_feature_gate as fg
    assert hasattr(fg, 'FeatureGateUnavailable')
    assert hasattr(fg, 'feature_available')
    assert hasattr(fg, 'feature_reason')
    assert hasattr(fg, 'feature_upgrade_path')


def test_gate_fails_closed_on_missing_profile(tmp_path):
    """feature_available returns False when profile is absent (fail CLOSED)."""
    gate_path = str(GATE.parent)
    if gate_path not in sys.path:
        sys.path.insert(0, gate_path)
    import importlib
    import d3kos_feature_gate as fg
    # Temporarily override _PROFILE_PATH to a nonexistent file
    orig = fg._PROFILE_PATH
    fg._PROFILE_PATH = str(tmp_path / 'nonexistent.json')
    fg._profile = None
    fg._profile_mtime = None
    try:
        result = fg.feature_available('surround_view')
    finally:
        fg._PROFILE_PATH = orig
        fg._profile = None
        fg._profile_mtime = None
    assert result is False, 'Gate must fail CLOSED when profile is missing'


def test_gate_accel_check_fails_closed_when_needed_but_absent():
    """_accel_ok returns False when accelerator_any=True but accelerator absent."""
    gate_path = str(GATE.parent)
    if gate_path not in sys.path:
        sys.path.insert(0, gate_path)
    import d3kos_feature_gate as fg
    req  = {'accelerator_any': True, 'accelerator_class_any': ['hailo-8l']}
    accel_absent = {'present': False, 'accelerator_class': []}
    assert fg._accel_ok(req, accel_absent) is False, \
        '_accel_ok must return False when accelerator needed but absent'


def test_gate_accel_check_passes_when_present_and_matched():
    """_accel_ok returns True when fitted accelerator is in the allowed list."""
    gate_path = str(GATE.parent)
    if gate_path not in sys.path:
        sys.path.insert(0, gate_path)
    import d3kos_feature_gate as fg
    req  = {'accelerator_any': True, 'accelerator_class_any': ['hailo-8l', 'coral-usb']}
    accel = {'present': True, 'accelerator_class': ['hailo-8l']}
    assert fg._accel_ok(req, accel) is True


def test_gate_no_accel_requirement_passes():
    """_accel_ok returns True when feature needs no accelerator."""
    gate_path = str(GATE.parent)
    if gate_path not in sys.path:
        sys.path.insert(0, gate_path)
    import d3kos_feature_gate as fg
    req   = {'pi_gen_min': 4, 'ram_mb_min': 2048}
    accel = {'present': False, 'accelerator_class': []}
    assert fg._accel_ok(req, accel) is True


# ─── capabilities-manifest.json schema ───────────────────────────────────────

def test_manifest_valid_json():
    """Manifest file is valid JSON."""
    data = json.loads(MANIFEST.read_text())
    assert 'features' in data


def test_manifest_uses_ram_mb_not_ram_gb():
    """All RAM requirements in manifest use ram_mb_min (not ram_gb_min)."""
    data = json.loads(MANIFEST.read_text())
    for key, feat in data['features'].items():
        req = feat.get('requires', {})
        assert 'ram_gb_min' not in req, \
            f'Feature {key!r} uses ram_gb_min — must use ram_mb_min (avoids truncation)'
        if 'ram_mb_min' in req:
            assert req['ram_mb_min'] >= 1024, \
                f'Feature {key!r} ram_mb_min={req["ram_mb_min"]} seems too low'


def test_manifest_features_have_required_fields():
    """Every feature entry has display_name and requires block."""
    data = json.loads(MANIFEST.read_text())
    for key, feat in data['features'].items():
        assert 'display_name' in feat, f'{key} missing display_name'
        assert 'requires' in feat, f'{key} missing requires'


# ─── systemd service/timer unit invariants ───────────────────────────────────

def test_service_type_oneshot():
    """B1: service is Type=oneshot (not simple — avoids BUG-105 restart loop)."""
    content = SERVICE.read_text()
    assert 'Type=oneshot' in content, \
        'd3kos-hardware-probe.service must be Type=oneshot'


def test_service_remain_after_exit_no():
    """B1: RemainAfterExit=no (avoids BUG-105 watchdog loop)."""
    content = SERVICE.read_text()
    assert 'RemainAfterExit=no' in content, \
        'd3kos-hardware-probe.service must have RemainAfterExit=no'


def test_timer_on_boot_sec():
    """Timer fires on boot after short delay."""
    content = TIMER.read_text()
    assert 'OnBootSec=' in content


def test_timer_periodic_reprobe():
    """Timer has periodic OnUnitActiveSec for belt-and-suspenders (REQ-HCD-027)."""
    content = TIMER.read_text()
    assert 'OnUnitActiveSec=' in content


# ─── udev rule invariants ─────────────────────────────────────────────────────

def test_udev_uses_systemd_run_no_block():
    """udev rule uses systemd-run --no-block (never runs probe synchronously in udev worker)."""
    content = UDEV.read_text()
    assert 'systemd-run' in content and '--no-block' in content, \
        'udev rule must use systemd-run --no-block to avoid blocking udev'


def test_udev_targets_google_coral_vendor():
    """udev rule targets vendor 18d1 (Google Coral)."""
    content = UDEV.read_text()
    assert '18d1' in content


# ─── app.py routes ───────────────────────────────────────────────────────────

def test_app_has_hardware_route():
    """/hardware route exists in app.py."""
    content = APP.read_text()
    assert "@app.route('/hardware')" in content


def test_app_has_hardware_summary_route():
    """/hardware-summary JSON endpoint exists (HCD-5 wizard step 9)."""
    content = APP.read_text()
    assert "@app.route('/hardware-summary')" in content


def test_app_has_reprobe_route():
    """/api/hardware/reprobe POST route exists."""
    content = APP.read_text()
    assert "@app.route('/api/hardware/reprobe'" in content


def test_app_has_health_route():
    """/health endpoint exists (required by D23 OTA agent)."""
    content = APP.read_text()
    assert "@app.route('/health')" in content
    assert "d3kos-dashboard" in content


def test_app_reprobe_calls_systemctl():
    """Reprobe route calls systemctl start d3kos-hardware-probe.service."""
    content = APP.read_text()
    assert 'd3kos-hardware-probe.service' in content
    assert 'systemctl' in content


# ─── hardware.html template ──────────────────────────────────────────────────

def test_hardware_html_no_font_awesome():
    """hardware.html must not use Font Awesome (not loaded in d3kOS)."""
    content = HARDWARE_HTML.read_text()
    assert 'fa-' not in content and 'font-awesome' not in content.lower(), \
        'hardware.html must not use Font Awesome — use Unicode symbols instead'


def test_hardware_html_reprobe_checks_data_ok():
    """Re-probe JS must check data.ok (not data.success) to match endpoint."""
    content = HARDWARE_HTML.read_text()
    assert 'd.ok' in content or 'data.ok' in content, \
        'hardware.html reprobe JS must check d.ok (endpoint returns {ok: true})'
    assert 'data.success' not in content and 'd.success' not in content, \
        'hardware.html must not check data.success (endpoint returns ok, not success)'


def test_hardware_html_min_font_size_18():
    """hardware.html body base font-size is 18px (AODA)."""
    content = HARDWARE_HTML.read_text()
    assert 'font-size:18px' in content or 'font-size: 18px' in content, \
        'hardware.html must set base font-size to 18px minimum (AODA)'
