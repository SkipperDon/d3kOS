"""
Tests for boatlog voice note endpoint.
TDD — written before fixes. Tests define required behaviour.

Run on Pi: cd /opt/d3kos/services/boatlog && python3 -m pytest /tmp/test_voice_note_api.py -v
"""
import io
import sys
import os
import importlib.util
import pytest

# Load module from hyphenated filename
_spec = importlib.util.spec_from_file_location(
    'boatlog_export_api',
    '/opt/d3kos/services/boatlog/boatlog-export-api.py'
)
boatlog_export_api = importlib.util.module_from_spec(_spec)
sys.modules['boatlog_export_api'] = boatlog_export_api  # register so monkeypatch resolves it
_spec.loader.exec_module(boatlog_export_api)

app = boatlog_export_api.app


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Flask test client with isolated temp dirs."""
    monkeypatch.setattr(boatlog_export_api, 'VOICE_NOTE_DIR', str(tmp_path))
    monkeypatch.setattr(boatlog_export_api, 'BOATLOG_DB', '/tmp/nonexistent_test_db.db')
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c, tmp_path


# ── Failing test 1: 0-byte upload must be rejected ──────────────────────────
def test_empty_audio_rejected(client):
    """A 0-byte audio upload must return 400 success=False.
    Before fix: API accepted empty files, ran ffmpeg, returned 200 success=True
    with empty transcript. FAILS before fix."""
    c, _ = client
    data = {'audio': (io.BytesIO(b''), 'voice-note.webm', 'audio/webm')}
    resp = c.post('/api/boatlog/voice-note',
                  content_type='multipart/form-data', data=data)
    assert resp.status_code == 400
    body = resp.get_json()
    assert body['success'] is False


# ── Failing test 2: MIME type determines file extension ─────────────────────
def test_ogg_upload_saved_with_ogg_extension(client):
    """audio/ogg upload must be saved as .ogg, not .webm.
    Before fix: all uploads hardcoded to .webm regardless of content type.
    FAILS before fix."""
    c, tmp_path = client
    ogg_magic = b'OggS' + b'\x00' * 28  # minimal OGG magic bytes
    data = {'audio': (io.BytesIO(ogg_magic), 'voice-note.ogg', 'audio/ogg')}
    c.post('/api/boatlog/voice-note',
           content_type='multipart/form-data', data=data)
    saved_ogg = list(tmp_path.glob('*.ogg'))
    saved_webm = list(tmp_path.glob('*.webm'))
    assert len(saved_ogg) == 1, (
        f"Expected 1 .ogg file, got ogg={saved_ogg} webm={saved_webm}"
    )


# ── Passing test: missing audio field returns 400 ───────────────────────────
def test_missing_audio_field_returns_400(client):
    """No audio field must return 400. Passes before and after fix."""
    c, _ = client
    resp = c.post('/api/boatlog/voice-note',
                  content_type='multipart/form-data', data={})
    assert resp.status_code == 400
    assert resp.get_json()['success'] is False
