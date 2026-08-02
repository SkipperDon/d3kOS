import sys, os, importlib.util, pytest

APP_PATH = 'deployment/v0.9.9.4/opt/d3kos/services/dashboard/app.py'

def load_app():
    spec = importlib.util.spec_from_file_location('dashboard_app', APP_PATH)
    mod = importlib.util.module_from_spec(spec)
    # Register BEFORE exec_module. app.py calls Flask(__name__), and Flask resolves
    # its root_path (and therefore templates/) by looking the module up in
    # sys.modules to read its __file__. Without this the lookup fails, Flask falls
    # back to the CWD, and every render raises TemplateNotFound -> 500 — which
    # looks exactly like the BUG-41 defect this test exists to detect. (BUG-51)
    sys.modules['dashboard_app'] = mod
    spec.loader.exec_module(mod)
    return mod.app

@pytest.fixture(scope='module')
def client():
    flask_app = load_app()
    flask_app.config['TESTING'] = False   # exceptions become 500, not raised
    with flask_app.test_client() as c:
        yield c

def test_settings_returns_200_not_500(client):
    """Before fix: Jinja UndefinedError -> 500. After fix: 200."""
    response = client.get('/settings')
    assert response.status_code == 200, (
        f'Expected 200 but got {response.status_code}. '
        'tier_num or device_token is still not passed to render_template.'
    )

def test_settings_response_contains_html(client):
    """Confirms the template rendered, not a Flask error page."""
    response = client.get('/settings')
    body = response.data.decode('utf-8', errors='replace')
    assert '<html' in body.lower(), 'Response should be an HTML page'
    assert 'UndefinedError' not in body, 'Jinja error must not appear in output'
    assert 'tier_num' not in body, (
        'tier_num must be resolved; it must not appear as literal text'
    )

def test_app_py_passes_tier_num_and_device_token():
    """Static check: render_template call in settings() must include both vars."""
    import pathlib
    src = pathlib.Path(APP_PATH).read_text()
    settings_block = src.split('@app.route(\'/settings\')')[1].split('@app.route')[0]
    assert 'tier_num' in settings_block, \
        'tier_num must be in the settings() render_template call'
    assert 'device_token' in settings_block, \
        'device_token must be in the settings() render_template call'
