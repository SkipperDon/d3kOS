import importlib.util, pathlib, pytest

MODULES = {
    'cloud_agent_copy': 'deployment/v0.9.9.4/opt/d3kos/services/cloud-agent/ota_upgrade.py',
    'services_copy':    'deployment/v0.9.9.4/opt/d3kos/services/ota_upgrade.py',
}
FOUR_LINE = ("d3kOS Version 0.9.9.4\n"
             "Release Date: unreleased (in development)\n"
             "Status: In Development\n"
             "Build: v0.9.9.4-dev\n")

def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

@pytest.fixture(params=MODULES.items(), ids=list(MODULES))
def mod_and_file(request, tmp_path):
    name, path = request.param
    mod = load(path, name)
    vf = tmp_path / 'version.txt'
    vf.write_text(FOUR_LINE)
    mod.VERSION_FILE = vf          # redirect away from the real /opt path
    return mod, vf

def test_all_four_fields_survive(mod_and_file):
    mod, vf = mod_and_file
    mod.write_version_file('0.9.9.5')
    lines = vf.read_text().strip().split('\n')
    assert len(lines) == 4, f'expected 4 lines, got {len(lines)}: {lines}'
    assert lines[0] == 'd3kOS Version 0.9.9.5'
    assert lines[1] == 'Release Date: unreleased (in development)'   # preserved
    assert lines[2] == 'Status: In Development'                      # preserved
    assert lines[3] == 'Build: v0.9.9.5'

def test_manifest_values_win_when_present(mod_and_file):
    mod, vf = mod_and_file
    mod.write_version_file('1.0.0', {'release_date': 'May 1, 2026', 'status': 'Release'})
    txt = vf.read_text()
    assert 'Release Date: May 1, 2026' in txt
    assert 'Status: Release' in txt
    assert 'd3kOS Version 1.0.0' in txt
    assert 'Build: v1.0.0' in txt

def test_missing_file_does_not_raise(mod_and_file, tmp_path):
    mod, _ = mod_and_file
    mod.VERSION_FILE = tmp_path / 'gone.txt'
    mod.write_version_file('0.9.9.6')                 # must not raise
    txt = mod.VERSION_FILE.read_text()
    assert 'd3kOS Version 0.9.9.6' in txt
    assert 'Release Date: unknown' in txt
    assert 'Status: unknown' in txt

def test_downstream_parsers_still_work(mod_and_file):
    """The three real consumers must still parse the rewritten file."""
    mod, vf = mod_and_file
    mod.write_version_file('0.9.9.5')
    raw = vf.read_text().strip()
    # ota_upgrade.get_current_version() logic
    v1 = next(l.split()[-1] for l in raw.splitlines() if 'Version' in l)
    # cloud_agent.get_version() logic
    v2 = next(l.replace('d3kOS Version', '').strip()
              for l in raw.split('\n') if l.strip().startswith('d3kOS Version'))
    assert v1 == v2 == '0.9.9.5'
    # exactly one line may match the ota filter, or it picks up the wrong line
    assert len([l for l in raw.splitlines() if 'Version' in l]) == 1

def test_step7_calls_the_helper(mod_and_file):
    """Guards against adding the helper but never wiring it in."""
    mod, _ = mod_and_file
    src = pathlib.Path(mod.__file__).read_text()
    assert 'write_version_file(' in src.split('# 7. Update version.txt')[1][:400], \
        'step 7 must call write_version_file()'
    assert "VERSION_FILE.write_text(f'd3kOS Version" not in src, \
        'the one-line truncating write must be gone'
