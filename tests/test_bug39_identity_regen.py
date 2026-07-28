import pathlib, re, subprocess, pytest

SH   = pathlib.Path('deployment/v0.9.9.4/opt/d3kos/services/identity/regenerate-identity.sh')
UNIT = pathlib.Path('deployment/v0.9.9.4/etc/systemd/system/d3kos-identity-regen.service')

def test_files_exist():
    assert SH.exists() and UNIT.exists()

def test_shebang_and_executable():
    assert SH.read_text().startswith('#!')
    assert SH.stat().st_mode & 0o111, 'must be chmod +x'

def test_bash_syntax_ok():
    r = subprocess.run(['bash', '-n', str(SH)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr

def test_sentinel_guard_is_first_logic():
    body = [l for l in SH.read_text().splitlines()
            if l.strip() and not l.strip().startswith('#')]
    head = '\n'.join(body[:15])
    assert '.identity-regenerated' in head, 'sentinel check must come first'

def test_regenerates_the_three():
    s = SH.read_text()
    assert 'machine-id' in s
    assert 'ssh-keygen' in s
    assert 'device-token.json' in s
    assert '/proc/sys/kernel/random/uuid' in s, 'use the kernel UUID source'

def test_license_json_is_never_written():
    """installation_id is per-owner — license.json must be read-only here."""
    for line in SH.read_text().splitlines():
        if 'license.json' in line and not line.strip().startswith('#'):
            assert not re.search(r'(>\s*\S*license\.json|>>|sed -i|tee\s+\S*license\.json'
                                 r'|rm\s+\S*license\.json|mv\s+\S*license\.json)', line), \
                f'license.json must never be written: {line.strip()}'

def test_signalk_untouched():
    s = SH.read_text()
    assert '.signalk' not in s, 'SK vessel UUID is out of scope (Q39.3)'

@pytest.mark.parametrize('tool', ['tune2fs', 'fatlabel', 'mlabel'])
def test_no_filesystem_uuid_tools(tool):
    assert tool not in SH.read_text()

def test_backs_up_before_rewriting_token():
    assert 'pre-regen' in SH.read_text(), 'must back up device-token.json first'

def test_writes_json_with_python_not_echo():
    s = SH.read_text()
    assert 'python3' in s, 'device-token.json must be written via python3, not echo/sed'

def test_requires_root():
    assert re.search(r'EUID|id -u', SH.read_text()), 'must refuse to run as non-root'

def test_unit_contract():
    u = UNIT.read_text()
    for needed in ('Type=oneshot', 'RemainAfterExit=yes',
                   'ConditionPathExists=!/opt/d3kos/config/.identity-regenerated',
                   'ExecStart=/opt/d3kos/services/identity/regenerate-identity.sh',
                   'WantedBy=multi-user.target'):
        assert needed in u, f'unit missing: {needed}'

def test_ssh_keys_not_deleted_before_generation():
    """SSH keys must not be deleted until the new ones are confirmed written."""
    src = SH.read_text()
    lines = src.splitlines()

    # Find the SSH key generation loop
    in_ssh_loop = False
    rm_before_keygen = False

    for i, line in enumerate(lines):
        if 'ssh-keygen' in line and 'for key_path' in '\n'.join(lines[max(0, i-20):i]):
            in_ssh_loop = True

        if in_ssh_loop and 'for key_path' in line:
            # Look ahead in the loop for rm and ssh-keygen ordering
            loop_section = '\n'.join(lines[i:min(len(lines), i+40)])

            # Find positions of rm and ssh-keygen
            rm_pos = loop_section.find('rm -f')
            ssh_keygen_pos = loop_section.find('ssh-keygen')

            if rm_pos != -1 and ssh_keygen_pos != -1:
                # rm must NOT come before ssh-keygen
                if rm_pos < ssh_keygen_pos:
                    rm_before_keygen = True

    assert not rm_before_keygen, 'rm -f must not precede ssh-keygen in the loop'

def test_created_at_format_is_iso8601_with_z():
    """created_at must be ISO-8601 with Z suffix, not +00:00."""
    src = SH.read_text()
    assert 'replace' in src and '+00:00' in src and "'Z'" in src, \
        'created_at generation must convert +00:00 to Z for ISO-8601 compliance'
