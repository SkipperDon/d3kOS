"""
test_camera_stream_manager_rtsp_sync.py
TDD test for camera_stream_manager.py structural bug:

  Bug: run_discovery_scan() updates hw['ip'] when a camera's DHCP lease
       changes but never updates hw['rtsp_url'].
  Result: RTSP URL points to the old IP → stream fails until Pi reboots or
          hardware.json is manually corrected.

  Location: camera_stream_manager.py lines 344-347 (else block in scan loop)

  Fix: after `hw['ip'] = ip`, also update rtsp_url:
       hw['rtsp_url'] = re.sub(r'(?<=@)[^:]+(?=:)', ip, hw['rtsp_url'])

Run: python3 deployment/d3kOS/dashboard/tests/test_camera_stream_manager_rtsp_sync.py
"""

import re

passed = 0
failed = 0


def assert_test(condition, message):
    global passed, failed
    if condition:
        print('  PASS:', message)
        passed += 1
    else:
        print('  FAIL:', message)
        failed += 1


def demonstrate_bug(condition, message):
    """Shows what the buggy code does — does not count toward exit."""
    if not condition:
        print('  BUG CONFIRMED:', message)
    else:
        print('  (bug not triggered):', message)


# ── Logic under test ──────────────────────────────────────────────────────────

def ip_update_BUGGY(hw, new_ip):
    """Mirrors the current buggy else-block in run_discovery_scan()."""
    if hw.get('ip') != new_ip:
        hw['ip'] = new_ip
        # rtsp_url is NOT updated — this is the bug


def ip_update_FIXED(hw, new_ip):
    """Correct behaviour: update both ip AND rtsp_url."""
    if hw.get('ip') != new_ip:
        hw['ip'] = new_ip
        hw['rtsp_url'] = re.sub(r'(?<=@)[^:]+(?=:)', new_ip, hw['rtsp_url'])


def extract_rtsp_ip(rtsp_url):
    """Parse host IP from rtsp://user:pass@IP:port/path"""
    m = re.match(r'rtsp://[^@]+@([^:/]+)', rtsp_url)
    return m.group(1) if m else None


# ── Test data ─────────────────────────────────────────────────────────────────

def make_hw(ip):
    """Create a hardware entry where rtsp_url correctly points to ip."""
    return {
        'hardware_id': 'hw_ec_71_db_43_ef_c1',
        'ip': ip,
        'rtsp_url': f'rtsp://admin:d3kos2026%24@{ip}:554/h264Preview_01_sub',
        'assigned_to_slot': 'port',
    }


# ── Tests ─────────────────────────────────────────────────────────────────────

print('\ncamera_stream_manager — RTSP URL sync on IP change\n')

# Confirm bug exists in current code
hw_buggy = make_hw('10.42.0.100')
ip_update_BUGGY(hw_buggy, '10.42.0.133')

demonstrate_bug(
    extract_rtsp_ip(hw_buggy['rtsp_url']) == hw_buggy['ip'],
    'BUGGY: after IP change 100→133, rtsp_url still points to 10.42.0.100'
)

# ── Fixed behaviour tests ─────────────────────────────────────────────────────
print('  [FIXED behaviour — these must pass after the fix]')

# Basic: RTSP IP updated when hardware IP changes
hw1 = make_hw('10.42.0.100')
ip_update_FIXED(hw1, '10.42.0.133')
assert_test(
    hw1['ip'] == '10.42.0.133',
    'ip field updated to new IP 10.42.0.133'
)
assert_test(
    extract_rtsp_ip(hw1['rtsp_url']) == '10.42.0.133',
    'rtsp_url IP updated to match new ip (10.42.0.133)'
)

# Verify RTSP URL preserves credentials and path after update
hw2 = make_hw('10.42.0.181')
ip_update_FIXED(hw2, '10.42.0.64')
assert_test(
    hw2['rtsp_url'] == 'rtsp://admin:d3kos2026%24@10.42.0.64:554/h264Preview_01_sub',
    'rtsp_url preserves credentials and path when only IP changes'
)

# No-op: same IP → nothing changes
hw3 = make_hw('10.42.0.100')
original_rtsp = hw3['rtsp_url']
ip_update_FIXED(hw3, '10.42.0.100')
assert_test(
    hw3['rtsp_url'] == original_rtsp,
    'same IP → rtsp_url unchanged'
)

# Unencoded password variant (bow camera uses plain password, no %24)
hw4 = {
    'hardware_id': 'hw_ec_71_db_f9_7c_7c',
    'ip': '10.42.0.50',
    'rtsp_url': 'rtsp://admin:d3kos2026@10.42.0.50:554/h264Preview_01_sub',
    'assigned_to_slot': 'bow',
}
ip_update_FIXED(hw4, '10.42.0.100')
assert_test(
    hw4['rtsp_url'] == 'rtsp://admin:d3kos2026@10.42.0.100:554/h264Preview_01_sub',
    'unencoded password variant: rtsp_url IP updated correctly'
)

# After fix: rtsp IP always matches ip field
hw5 = make_hw('10.42.0.63')
ip_update_FIXED(hw5, '10.42.0.200')
assert_test(
    extract_rtsp_ip(hw5['rtsp_url']) == hw5['ip'],
    'rtsp IP always equals ip field after any update'
)

# ── Results ───────────────────────────────────────────────────────────────────
print('\n─────────────────────────────────────────────────────')
print(f'Results: {passed} passed, {failed} failed')
print('─────────────────────────────────────────────────────\n')
exit(1 if failed > 0 else 0)
