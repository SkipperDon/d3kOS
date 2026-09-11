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


# --------------------------------------------------------------------------
# S4-S6 -- disclaimer placement (§13.3). Added v1.4 on operator instruction.
#
# §12.3's original plan (a maritime professional's sign-off) is unobtainable:
# nobody endorses a rule boundary without reviewing the whole system, and
# anyone who does assumes liability. The system therefore ships without domain
# endorsement, and that fact must reach the captain rather than be buried.
# --------------------------------------------------------------------------

DISCLAIMER_REQUIRED_CLAIMS = [
    ('not a look-out',   ['not a look-out', 'not a lookout']),
    ('AIS-only blindness', ['without ais are completely invisible',
                            'without ais are invisible']),
    ('silence is not clearance', ['silence does not mean']),
    ('not an ARPA',      ['not an arpa']),
    ('not type-approved', ['not type-approved', 'not type approved']),
    ('captain responsible', ['remains solely responsible']),
]


def test_s4_widget_carries_the_always_visible_advisory_line():
    """S4: ADV-1 -- one line, always visible, on the widget itself."""
    src = require_file(f'{SAFEHELM}/static/safehelm-widget.js', '§13.3')
    low = src.lower()
    assert 'advisory only' in low, 'ADV-1 footer line missing from the widget'
    assert 'captain remains responsible' in low


@pytest.mark.parametrize('claim,variants', DISCLAIMER_REQUIRED_CLAIMS)
def test_s5_full_disclaimer_is_present_on_the_hardware_page(claim, variants):
    """S5: ADV-3 -- the full §13.1 text under the SafeHelm feature entry."""
    src = require_file('opt/d3kos/services/dashboard/templates/hardware.html', '§13.3')
    low = src.lower()
    assert any(v in low for v in variants), (
        f'§13.1 disclaimer is missing its "{claim}" statement')


def test_s6_first_enable_requires_an_unskippable_acknowledgement():
    """S6: §13.3 -- accepted once, recorded, and not skippable.

    A disclaimer the operator can dismiss without reading is not a disclaimer.
    """
    src = require_file(f'{SAFEHELM}/safehelm.py', '§13.3')
    low = src.lower()
    assert 'disclaimer' in low, 'no disclaimer acknowledgement gate in safehelm.py'
    assert 'accepted' in low or 'acknowledged' in low, (
        'acknowledgement is not recorded -- §13.3 requires the date accepted'
    )


# --------------------------------------------------------------------------
# S7-S11 -- D19 boot-time acceptance gate (§15). Added v1.8 on operator
# instruction: an experimental-software dialogue on boot, with Shutdown or
# Accept. Offering Shutdown is what makes it consent rather than an
# announcement.
# --------------------------------------------------------------------------

DASH = 'opt/d3kos/services/dashboard'


def test_s7_disclaimer_gate_blocks_the_dashboard_until_accepted():
    """S7: the gate must actually gate. An unacceptable disclaimer is decoration."""
    src = require_file(f'{DASH}/app.py', '§15.1')
    low = src.lower()
    assert 'disclaimer' in low, 'no disclaimer gate in the dashboard app (§15.1)'
    assert 'accept' in low, 'no acceptance path'


def test_s8_acceptance_is_recorded_with_a_text_hash():
    """S8: §15.3 -- the terms must not be changeable without re-consent.

    Recording a bare "accepted: true" would let the disclaimer text be edited
    afterwards while the record still claimed consent to it. The hash is what
    makes the record worth anything later.
    """
    src = require_file(f'{DASH}/app.py', '§15.3')
    low = src.lower()
    assert 'disclaimer-accepted.json' in low or 'disclaimer_accepted' in low, (
        'acceptance is not persisted (§15.3)')
    assert 'sha256' in low, (
        'no disclaimer text hash -- the terms could be changed after acceptance '
        'while the record still claims consent (§15.3)')
    assert 'version' in low, 'acceptance does not record the d3kOS version'


def test_s9_poweroff_endpoint_is_loopback_only():
    """S9: §15.4 -- the dashboard is reachable from the boat Wi-Fi by design.

    An unrestricted poweroff endpoint would let any guest aboard kill the helm
    display.
    """
    src = require_file(f'{DASH}/app.py', '§15.4')
    assert 'poweroff' in src.lower(), 'no shutdown endpoint (§15.4)'
    assert '127.0.0.1' in src, (
        'poweroff endpoint is not restricted to loopback -- anyone on the boat '
        'network could shut down the helm (§15.4)')


def test_s10_accept_button_requires_scrolling_to_the_end():
    """S10: §15.5 -- a button reachable without passing the text is not consent."""
    src = require_file(f'{DASH}/templates/disclaimer.html', '§15.5')
    low = src.lower()
    assert 'scroll' in low, 'ACCEPT is not gated on scrolling to the end (§15.5)'
    assert 'disabled' in low, 'ACCEPT is not initially disabled (§15.5)'


@pytest.mark.parametrize('claim,needle', [
    ('experimental',      'experimental'),
    ('not a replacement', 'not a replacement for the captain'),
    ('at your own risk',  'own risk'),
    ('vessel assumptions', 'assumes'),
])
def test_s11_disclaimer_page_carries_the_required_statements(claim, needle):
    """S11: §15.2 -- the operator asked specifically for experimental and
    not-a-replacement-for-the-captain, plus the §15.6 vessel assumptions."""
    src = require_file(f'{DASH}/templates/disclaimer.html', '§15.2')
    assert needle in src.lower(), f'disclaimer is missing its "{claim}" statement'


# --------------------------------------------------------------------------
# S12-S14 -- D19-1 every-boot gate and sensor honesty. Added v1.9.
#
# Operator decision D19-1: the dialogue appears on EVERY boot, not once per
# version. Mitigated with a tiered form -- full text with a scroll gate on
# first boot / version change / text change, abbreviated one-tap
# re-acknowledgement otherwise -- so an underway reboot costs one touch.
# --------------------------------------------------------------------------

def test_s12_gate_arms_on_every_boot():
    """S12: D19-1. Acceptance must NOT be treated as permanent.

    The guard is that the gate is not short-circuited by a stored
    "accepted: true" -- it re-arms each boot and uses the record only to
    decide full vs abbreviated form.
    """
    src = require_file(f'{DASH}/app.py', '§15.0')
    low = src.lower()
    assert 'every_boot' in low or 'require_every_boot' in low, (
        'no every-boot behaviour -- D19-1 requires the dialogue each boot (§15.0)')
    assert 'abbreviated' in low or 'full_text' in low, (
        'no tiered dialogue -- an underway reboot must clear in one tap (§15.0)')


def test_s13_full_text_is_forced_when_terms_or_version_change():
    """S13: §15.0 -- abbreviation must never hide changed terms.

    A hash or version change has to escalate back to the full scroll-gated
    read, or the abbreviation becomes a way to slip new terms past the captain.
    """
    src = require_file(f'{DASH}/app.py', '§15.0')
    low = src.lower()
    assert 'sha256' in low, 'no text hash comparison (§15.3)'
    assert 'version' in low, 'no version comparison (§15.0)'


@pytest.mark.parametrize('claim,needle', [
    ('no radar',            'no radar'),
    ('non-AIS invisible',   'invisible'),
    ('one input among',     'one input among'),
    ('never depend alone',  'never depend on it alone'),
])
def test_s14_disclaimer_states_the_sensor_limits(claim, needle):
    """S14: §13.4 -- the limited view is the most important limitation.

    Operator, S160: "you have AIS and cameras. This is a limited view for
    safety and cannot be solely dependent on d3kOS." It must be in the text
    the captain actually reads, not only in the design document.
    """
    src = require_file(f'{DASH}/templates/disclaimer.html', '§13.4')
    assert needle in src.lower(), f'disclaimer is missing its "{claim}" statement'
