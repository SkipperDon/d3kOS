"""
D23 OTA Agent — guard tests (pytest).

All tests run without network, without Pi hardware.
Imports the agent module directly; mocks only network and filesystem calls.
"""

import hashlib
import importlib
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest


# ── Module import helper ──────────────────────────────────────────────────────
# The agent imports device_sign which is not present in the test environment.
# Stub it before importing the module under test.

@pytest.fixture(autouse=True)
def stub_device_sign(monkeypatch):
    """Stub device_sign so the module can be imported without Pi files."""
    fake_ds = MagicMock()
    fake_ds.sign_device_request.return_value = {
        'X-Device-Token': 'test-token',
        'X-Timestamp': '1000000000',
        'X-Nonce': 'test-nonce',
        'X-Signature': 'fakesig==',
    }
    fake_ds._load_device_token.return_value = 'test-token'
    monkeypatch.setitem(sys.modules, 'device_sign', fake_ds)


def _import_agent():
    """Import (or re-import) the agent module after stubs are in place."""
    agent_path = (
        Path(__file__).parent.parent
        / 'deployment/v0.9.9.5/opt/d3kos/services/ota/d3kos-ota-agent.py'
    )
    spec = importlib.util.spec_from_file_location('d3kos_ota_agent', agent_path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ── Tier gate tests ───────────────────────────────────────────────────────────

def test_tier_gate_t0_blocks(tmp_path):
    """_check_tier() returns False when license.json has tier: 0."""
    lic = tmp_path / 'license.json'
    lic.write_text(json.dumps({'tier': 0}))

    agent = _import_agent()
    with patch.object(agent, 'LICENSE_PATH', lic):
        assert agent._check_tier() is False


def test_tier_gate_t1_passes(tmp_path):
    """_check_tier() returns True when license.json has tier: 1."""
    lic = tmp_path / 'license.json'
    lic.write_text(json.dumps({'tier': 1}))

    agent = _import_agent()
    with patch.object(agent, 'LICENSE_PATH', lic):
        assert agent._check_tier() is True


def test_tier_gate_missing_file(tmp_path):
    """_check_tier() returns False when license.json does not exist (fail closed)."""
    agent = _import_agent()
    with patch.object(agent, 'LICENSE_PATH', tmp_path / 'nonexistent.json'):
        assert agent._check_tier() is False


# ── SHA-256 tests ─────────────────────────────────────────────────────────────

def test_checksum_pass(tmp_path):
    """_verify_sha256() returns True for a file whose hash matches."""
    f = tmp_path / 'archive.tar.gz'
    f.write_bytes(b'hello world')
    expected = hashlib.sha256(b'hello world').hexdigest()

    agent = _import_agent()
    assert agent._verify_sha256(f, expected) is True


def test_checksum_fail(tmp_path):
    """_verify_sha256() returns False for a tampered file."""
    f = tmp_path / 'archive.tar.gz'
    f.write_bytes(b'tampered content')
    correct_hash = hashlib.sha256(b'original content').hexdigest()

    agent = _import_agent()
    assert agent._verify_sha256(f, correct_hash) is False


# ── Command schema tests ──────────────────────────────────────────────────────

def test_command_schema_valid():
    """_parse_command() accepts a correctly-shaped command dict without raising."""
    agent = _import_agent()
    cmd = {
        'command_type': 'ota_install',
        'command_id': 42,
        'pi_id': 'test-token',
        'payload': {
            'version': '0.9.9.5',
            'download_url': 'https://example.com/d3kos.tar.gz',
            'sha256': 'abc123',
        },
    }
    result = agent._parse_command(cmd)
    assert result['command_id'] == 42


def test_command_schema_wrong_type():
    """_parse_command() raises ValueError when command_type != 'ota_install'."""
    agent = _import_agent()
    cmd = {
        'command_type': 'reboot',
        'command_id': 99,
        'pi_id': 'test-token',
        'payload': {},
    }
    with pytest.raises(ValueError, match='Unexpected command_type'):
        agent._parse_command(cmd)


# ── Result payload shape test ─────────────────────────────────────────────────

def test_result_payload_shape(tmp_path):
    """_build_result_payload() returns a dict with all required keys."""
    agent = _import_agent()
    with patch.object(agent, 'HARDWARE_PROFILE', tmp_path / 'hw.json'):
        payload = agent._build_result_payload(
            command_id=42,
            pi_id='test-token',
            status='success',
            version_installed='0.9.9.5',
        )

    required_keys = {'command_id', 'pi_id', 'status', 'version_installed',
                     'hardware_profile_version'}
    assert required_keys.issubset(payload.keys())
    assert payload['command_id'] == 42
    assert payload['pi_id'] == 'test-token'
    assert payload['status'] == 'success'
    assert payload['version_installed'] == '0.9.9.5'


# ── Rollback on health fail ───────────────────────────────────────────────────

def test_rollback_triggered_on_health_fail(tmp_path, monkeypatch):
    """When health check always fails, rollback path is called."""
    agent = _import_agent()

    # Patch out all filesystem / subprocess / network operations
    monkeypatch.setattr(agent, '_check_tier', lambda: True)
    monkeypatch.setattr(agent, '_ack', lambda *a, **kw: None)
    monkeypatch.setattr(agent, '_verify_sha256', lambda *a, **kw: True)
    monkeypatch.setattr(agent, '_d3kos_services', lambda: ['d3kos-dashboard.service'])
    monkeypatch.setattr(agent, '_stop_services', lambda *a: None)
    monkeypatch.setattr(agent, '_start_services', lambda *a: None)
    monkeypatch.setattr(agent, '_health_check', lambda **kw: False)
    monkeypatch.setattr(agent, '_post_result', lambda *a, **kw: None)
    monkeypatch.setattr(agent, 'DEPLOY_ROOT', tmp_path / 'deploy')
    monkeypatch.setattr(agent, 'ROLLBACK_DIR', tmp_path / 'rollback')
    (tmp_path / 'deploy').mkdir()
    (tmp_path / 'rollback').mkdir()

    # Fake a download that writes a valid (empty) .tar.gz
    import tarfile, io
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode='w:gz'):
        pass
    tar_bytes = buf.getvalue()

    fake_resp = MagicMock()
    fake_resp.raise_for_status = MagicMock()
    fake_resp.iter_content.return_value = [tar_bytes]
    fake_resp.__enter__ = lambda s: s
    fake_resp.__exit__ = MagicMock(return_value=False)

    rollback_called = []

    original_rollback = agent._rollback
    def mock_rollback(units, detail):
        rollback_called.append(detail)
    monkeypatch.setattr(agent, '_rollback', mock_rollback)

    with patch('requests.get', return_value=fake_resp):
        agent._install(
            base_url='https://example.com',
            php_path='/wp-content/themes/twentytwenty-child/mobile/ota-queue.php',
            pi_id='test-token',
            cmd={
                'command_id': 1,
                'command_type': 'ota_install',
                'pi_id': 'test-token',
                'payload': {
                    'version': '0.9.9.5',
                    'download_url': 'https://example.com/d3kos.tar.gz',
                    'sha256': hashlib.sha256(tar_bytes).hexdigest(),
                },
            },
        )

    assert len(rollback_called) == 1, 'Rollback should have been called exactly once'
