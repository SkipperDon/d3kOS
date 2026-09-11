"""S1-S3, U1-U4 -- config and systemd unit guard tests (V09995-SOL-001 §12).

File-content guards for defects that live in configuration rather than logic.
Each asserts against files under deployment/v0.9.9.5/, so each fails with an
actionable "not yet implemented" message until that file is written.

  S1  Signal K WebSocket port. Solution design v1.0 wrote :3000, which is the
      DASHBOARD. app.py says in capitals "CRITICAL: Signal K WebSocket is
      ws://localhost:8099 -- NOT ws://localhost:3000", tagged BUG-46.
  S2  No hardcoded localhost in browser-delivered JS (BUG-48): it resolves in
      the BROWSER, which killed every remote gauge once already.
  U1  No Restart=always without a start limit. BUG-105 was a self-healing
      runaway: ~40 restarts/sec for eight days, 2.6 GB of log. v1.0 shipped
      this pattern on both new units, one paired with a hard exit.
  U2  No 0.0.0.0 binds. The boat runs a Wi-Fi network with guests aboard;
      v1.0's `listen: ":8554"` would have published unauthenticated camera
      streams and v1.0's SafeHelm would have let anyone silence a collision
      alarm.
  U3  Camera credentials. Reolink RTSP URLs embed user:password@.
"""
import re

import pytest

from conftest import require_file

SAFEHELM = 'opt/d3kos/services/safehelm'
UNITS = 'etc/systemd/system'


# --------------------------------------------------------------------------
# S -- Signal K wiring.
# --------------------------------------------------------------------------

def test_s1_signalk_client_uses_port_8099_not_3000():
    """S1: BUG-46 guard. 3000 is the dashboard; Signal K is 8099."""
    src = require_file(f'{SAFEHELM}/signalk_client.py', '§8 header')
    assert '8099' in src, 'Signal K WebSocket port 8099 not referenced (BUG-46)'
    bad = [m.group(0) for m in re.finditer(r'(?:ws|http)s?://[^\s\'"]*:3000[^\s\'"]*', src)]
    assert not bad, f'Signal K URL points at the dashboard port 3000 (BUG-46): {bad}'


def test_s2_widget_js_has_no_hardcoded_localhost():
    """S2: BUG-48 guard -- localhost in front-end code resolves in the browser."""
    src = require_file(f'{SAFEHELM}/static/safehelm-widget.js', '§8.7')
    hits = [ln.strip() for ln in src.splitlines()
            if 'localhost' in ln and not ln.strip().startswith(('//', '*'))]
    assert not hits, f'hardcoded localhost in browser-delivered JS (BUG-48): {hits}'


def test_s3_voice_client_posts_to_the_ai_bridge_alert_endpoint():
    """S3: the voice path is ai_bridge :3002 /webhook/alert, and it must not be fatal."""
    src = require_file(f'{SAFEHELM}/voice_client.py', '§8 header')
    assert '3002' in src, 'ai_bridge port 3002 not referenced'
    assert '/webhook/alert' in src, 'ai_bridge alert endpoint not referenced'
    assert 'timeout' in src, 'HTTP call without a timeout would stall the advisory loop'


# --------------------------------------------------------------------------
# U -- systemd units and service exposure.
# --------------------------------------------------------------------------

@pytest.mark.parametrize('unit', ['d3kos-safehelm.service', 'd3kos-go2rtc.service'])
def test_u1_no_unbounded_restart_always(unit):
    """U1: BUG-105 guard -- no Restart=always, and a start limit must be set."""
    src = require_file(f'{UNITS}/{unit}', '§7.3, §8.6')
    assert not re.search(r'^\s*Restart\s*=\s*always', src, re.M), (
        f'{unit} uses Restart=always -- the BUG-105 restart-storm pattern')
    assert re.search(r'^\s*Restart\s*=\s*on-failure', src, re.M), (
        f'{unit} must use Restart=on-failure')
    assert 'StartLimitBurst' in src, (
        f'{unit} has no StartLimitBurst -- a bad config would retry forever')


def test_u1b_safehelm_sets_pythonunbuffered():
    """U1b: BUG-54 guard -- Python services using print() need unbuffered output."""
    src = require_file(f'{UNITS}/d3kos-safehelm.service', '§8.6')
    assert 'PYTHONUNBUFFERED=1' in src, 'journal output will be buffered and lost (BUG-54)'


def test_u1c_safehelm_does_not_exit_on_sh15_violation():
    """U1c: an SH-15 misconfiguration must degrade to Advisory, not exit.

    v1.0 raised SystemExit here. With Restart=always that was a permanent
    restart loop, and it also took the collision advisory off the boat
    because of a Phase 2 config error.
    """
    src = require_file(f'{SAFEHELM}/safehelm.py', '§8.6')
    marker = src[src.find('verify_signalk_transmit_whitelist'):] if \
        'verify_signalk_transmit_whitelist' in src else ''
    assert marker, 'SH-15 verification call not found (§8.6)'
    assert 'SystemExit' not in marker, (
        'SH-15 failure path raises SystemExit -- degrade to Advisory instead')


def test_u2_go2rtc_binds_loopback_only():
    """U2: no 0.0.0.0 listeners. Guests are on the boat Wi-Fi."""
    cfg = require_file('etc/go2rtc/go2rtc-d16.yaml', '§7.3')
    wildcard = re.findall(r'listen:\s*["\']?:\d+', cfg)
    assert not wildcard, f'go2rtc binds all interfaces: {wildcard}'
    assert '0.0.0.0' not in cfg, 'go2rtc binds 0.0.0.0'
    assert '127.0.0.1' in cfg, 'go2rtc must bind loopback and be proxied by the dashboard'


def test_u2b_go2rtc_does_not_put_its_api_on_the_rtsp_port():
    """U2b: 8554 is go2rtc's RTSP listener; its HTTP API belongs on 1984.

    v1.0 set `api.listen: ":8554"`, colliding with go2rtc's own internal RTSP
    server -- and paired it with Restart=always, so a bind failure became a
    restart loop.
    """
    cfg = require_file('etc/go2rtc/go2rtc-d16.yaml', '§7.3')
    api_block = re.search(r'api:\s*\n(?:\s+.*\n)*', cfg)
    assert api_block, 'no api: block in go2rtc config'
    assert ':8554' not in api_block.group(0), (
        'api.listen is on 8554, which collides with go2rtc RTSP')


def test_u2c_go2rtc_stream_is_passthrough():
    """U2c: transcoding four camera feeds on a Pi 4B is not in the CPU budget."""
    cfg = require_file('etc/go2rtc/go2rtc-d16.yaml', '§7.3')
    assert 'video=copy' in cfg, 'forward panel must be passthrough, not transcoded (§7.2)'


def test_u3_camera_credentials_are_not_left_world_readable():
    """U3: Reolink RTSP URLs embed user:password@ -- the file needs tight perms."""
    src = require_file('opt/d3kos/scripts/configure-go2rtc.sh', '§7.3')
    assert re.search(r'umask\s+0?77|chmod\s+600', src), (
        'configure-go2rtc.sh must umask 077 or chmod 600 -- the YAML holds '
        'camera credentials')


def test_u4_udev_rule_does_not_block_the_worker():
    """U4: no lsusb, PCI walks, curl or flock inline in a udev RUN+=.

    udev kills slow RUN processes and a blocked worker stalls all device
    events. v1.0 ran the whole probe plus an HTTP POST inline.
    """
    src = require_file('etc/udev/rules.d/99-d3kos-accelerator.rules', '§5 HCD-2')
    assert 'systemd-run' in src and '--no-block' in src, (
        'udev rule must hand off with systemd-run --no-block (§5 HCD-2)')
    for blocking in ('curl', 'flock', 'lsusb'):
        assert blocking not in src, f'{blocking} runs inline in the udev worker'


def test_u5_probe_timer_exists_and_is_fifteen_minutes():
    """U5: REQ-HCD-027. Absent from v1.0 entirely."""
    src = require_file(f'{UNITS}/d3kos-hardware-probe.timer', '§5 HCD-1')
    assert re.search(r'OnUnitActiveSec\s*=\s*15min', src), (
        'REQ-HCD-027 requires a 15-minute re-probe')


def test_u5b_probe_service_can_be_retriggered():
    """U5b: RemainAfterExit=yes would stop the timer re-running the unit."""
    src = require_file(f'{UNITS}/d3kos-hardware-probe.service', '§5 HCD-1')
    assert not re.search(r'^\s*RemainAfterExit\s*=\s*yes', src, re.M), (
        'RemainAfterExit=yes blocks the 15-minute timer from re-triggering')
