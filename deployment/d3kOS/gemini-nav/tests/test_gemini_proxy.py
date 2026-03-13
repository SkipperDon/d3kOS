"""
Test suite for d3kOS Gemini Marine AI Proxy
Run: cd gemini-nav && pytest tests/test_gemini_proxy.py -v
All tests must pass before Phase 3 is marked complete.
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import gemini_proxy as gp


@pytest.fixture
def client():
    gp.app.config['TESTING'] = True
    with gp.app.test_client() as c:
        yield c


def test_status_endpoint(client):
    """Status endpoint returns 200 with all expected keys."""
    res = client.get('/status')
    assert res.status_code == 200
    data = res.get_json()
    assert 'online'       in data
    assert 'ollama'       in data
    assert 'gemini_key'   in data
    assert 'model'        in data
    assert 'ollama_model' in data


def test_ask_empty_message(client):
    """Empty message string returns 400."""
    res = client.post('/ask', json={'message': ''})
    assert res.status_code == 400


def test_ask_missing_message(client):
    """Missing message key returns 400."""
    res = client.post('/ask', json={})
    assert res.status_code == 400


def test_ask_no_body(client):
    """Non-JSON content type returns 400 or 415 (Flask 3.x returns 415 for wrong content-type)."""
    res = client.post('/ask', data='not json', content_type='text/plain')
    assert res.status_code in (400, 415)


def test_cache_load_empty():
    """Cache load on non-existent file returns empty list."""
    import tempfile
    gp.CACHE_FILE = Path(tempfile.mktemp(suffix='.json'))
    result = gp.load_cache()
    assert result == []


def test_cache_save_and_load(tmp_path):
    """Cache round-trip: save then load returns identical data."""
    gp.CACHE_FILE = tmp_path / 'test_cache.json'
    entries = [{'timestamp': 1, 'source': 'test', 'tokens': 10, 'response': 'ok'}]
    gp.save_cache(entries)
    loaded = gp.load_cache()
    assert loaded == entries


def test_cache_max_enforced(tmp_path):
    """Cache never exceeds CACHE_MAX (10) entries."""
    gp.CACHE_FILE = tmp_path / 'cache.json'
    entries = [
        {'timestamp': i, 'source': 'test', 'tokens': i, 'response': f'r{i}'}
        for i in range(20)
    ]
    gp.save_cache(entries)
    loaded = gp.load_cache()
    assert len(loaded) <= gp.CACHE_MAX


def test_cache_contains_no_query_text(tmp_path):
    """Cache entries must not contain a 'query' or 'message' field (privacy rule)."""
    gp.CACHE_FILE = tmp_path / 'cache.json'
    entry = {'timestamp': 1, 'source': 'gemini', 'tokens': 50, 'response': 'Port info here.'}
    gp.save_cache([entry])
    loaded = gp.load_cache()
    for item in loaded:
        assert 'query'   not in item, "Query text must never be stored in cache"
        assert 'message' not in item, "User message must never be stored in cache"


def test_cache_creates_parent_dir(tmp_path):
    """Cache save creates parent directory if it does not exist."""
    gp.CACHE_FILE = tmp_path / 'new_subdir' / 'cache.json'
    gp.save_cache([{'timestamp': 1, 'source': 'ollama', 'tokens': 5, 'response': 'ok'}])
    assert gp.CACHE_FILE.exists()


def test_chat_ui_loads(client):
    """GET / returns 200 and HTML."""
    res = client.get('/')
    assert res.status_code == 200
    assert b'<!DOCTYPE html' in res.data or b'html' in res.data.lower()
