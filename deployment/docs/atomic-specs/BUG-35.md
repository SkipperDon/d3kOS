# Atomic Spec — BUG-35 (OTA upgrade destroys three of the four `version.txt` fields)

**Format:** AAO §23.5 Atomic Spec · §25 escalation-enabled · §24 Question Queue
**Created:** 2026-07-27 (S108) by Tier 1 (Opus 5)
**Tracker:** `deployment/docs/V09994_BUG_FIXES.md` BUG-35 · `PROJECT_CHECKLIST.md` PART 17
**Questions:** `wiki/questions/2026-07-27-v0994-tier3-spec-questions.md` — **read Q0.1–Q0.5 and Q35.1–Q35.3 first**
**Depends on:** nothing. **Latent** — has never fired on this Pi.

---

## Tier-1 finding

`ota_upgrade.py` step 7 rewrites the whole file with a single line:

```python
# 7. Update version.txt
try:
    VERSION_FILE.write_text(f'd3kOS Version {latest_ver}\n')
except Exception as e:
    errors.append(f'Could not update version.txt: {e}')
```

`Path.write_text()` truncates. `Release Date`, `Status` and `Build` are destroyed.

**Silent by construction:** `ota_upgrade.get_current_version()` and `cloud_agent.get_version()` both
read only line 1, so nothing errors. Only `export_categories.collect_version()` — which parses
`Release Date:` and `Status:` by prefix — quietly loses those keys from its export payload.

It has never fired here: `version.txt` still had all four fields at mtime 2026-03-23, so no OTA has
ever run on this Pi. But it **will** wipe the S108 relabel (`0.9.9.4` / `unreleased (in development)`
/ `In Development` / `v0.9.9.4-dev`) the first time it does.

The release manifest is a dict; only `version` and `download_url` are read anywhere in the file.
Whether it carries a date or status is **unconfirmed** — hence the read-modify-write contract below,
which is correct either way.

---

## SPEC (paste this block to the Tier 3 model)

```
🔧 ATOMIC SPEC — BUG-35   (AAO §23.5 · §25 escalation-enabled)
═══════════════════════════════════════════════════════════════════════
TASK TYPE : [IMPLEMENT] — Tier 3
BUG       : BUG-35 — OTA must preserve all four version.txt fields

FILES TO EDIT (exactly two — apply the SAME change to each, in place)
  deployment/v0.9.9.4/opt/d3kos/services/cloud-agent/ota_upgrade.py   ← the LIVE one
  deployment/v0.9.9.4/opt/d3kos/services/ota_upgrade.py               ← second copy

  These two files are NOT identical (md5 7043f1d7… vs 6105de65…). Edit each
  in place. Do NOT copy one over the other. Do NOT reconcile their other
  differences — that is a separate task. See Q35.2.

THE FILE FORMAT BEING PROTECTED (four lines, exact prefixes)
  d3kOS Version 0.9.9.4
  Release Date: unreleased (in development)
  Status: In Development
  Build: v0.9.9.4-dev

  Parsers depend on these prefixes:
    ota_upgrade.get_current_version()  -> first line containing "Version", .split()[-1]
    cloud_agent.get_version()          -> line startswith "d3kOS Version"
    export_categories.collect_version()-> prefixes "d3kOS Version" / "Release Date:" / "Status:"

CHANGE — add one helper, then call it from step 7.

  (1) ADD this module-level function (place it directly after the existing
      get_current_version() definition, ~line 58):

        def write_version_file(new_version, release=None):
            """Rewrite version.txt preserving every field.

            Updates 'd3kOS Version' and 'Build' from new_version. Takes
            'Release Date' and 'Status' from the release manifest when it
            supplies them, otherwise PRESERVES the existing values. Never
            invents a date. BUG-35.
            """
            release = release or {}
            fields = {
                'd3kOS Version': None,
                'Release Date':  None,
                'Status':        None,
                'Build':         None,
            }
            # read whatever is currently there
            try:
                for line in VERSION_FILE.read_text().splitlines():
                    line = line.strip()
                    if line.startswith('d3kOS Version'):
                        fields['d3kOS Version'] = line.replace('d3kOS Version', '').strip()
                    elif line.startswith('Release Date:'):
                        fields['Release Date'] = line.replace('Release Date:', '').strip()
                    elif line.startswith('Status:'):
                        fields['Status'] = line.replace('Status:', '').strip()
                    elif line.startswith('Build:'):
                        fields['Build'] = line.replace('Build:', '').strip()
            except Exception:
                pass                      # missing/unreadable file -> fall through to defaults

            fields['d3kOS Version'] = str(new_version)
            fields['Build'] = 'v' + str(new_version)
            if release.get('release_date'):
                fields['Release Date'] = str(release['release_date'])
            if release.get('status'):
                fields['Status'] = str(release['status'])
            if not fields['Release Date']:
                fields['Release Date'] = 'unknown'
            if not fields['Status']:
                fields['Status'] = 'unknown'

            VERSION_FILE.write_text(
                "d3kOS Version {}\nRelease Date: {}\nStatus: {}\nBuild: {}\n".format(
                    fields['d3kOS Version'], fields['Release Date'],
                    fields['Status'], fields['Build']))

  (2) REPLACE the body of step 7. Keep the surrounding try/except exactly as is:

        # 7. Update version.txt
        try:
            write_version_file(latest_ver, release)     # BUG-35: preserve all four fields
        except Exception as e:
            errors.append(f'Could not update version.txt: {e}')

      Confirm that the name `release` is in scope at that point (it is the dict
      `latest_ver` came from). If it is NOT in scope under that name, ESCALATE —
      do not substitute a different variable.

CONSTRAINT BOUNDARIES (do NOT)
  • Do NOT invent a date. datetime IS imported in this module, but writing the
    install date into "Release Date" would record a value that is not the
    release's date — the exact class of wrong-metadata defect this bug is about.
    Preserve, or take it from the manifest, or write "unknown".
  • Do NOT change get_current_version(), cloud_agent.py, export_categories.py,
    or the version.txt file itself.
  • Do NOT change the field order, the prefixes, or the trailing newline.
  • Do NOT remove the outer try/except in step 7 — an OTA must never crash here.
  • Do NOT add imports. Everything needed is already imported.
  • Do NOT edit any other file. Do NOT regenerate MANIFEST.md5 (Q0.4).
  • Do NOT deploy to the Pi, and do NOT run an OTA (Q0.2).

INTERFACE CONTRACT
  write_version_file('0.9.9.5') applied to a file containing the four-line format
  yields exactly:
      d3kOS Version 0.9.9.5
      Release Date: <the previous value, unchanged>
      Status: <the previous value, unchanged>
      Build: v0.9.9.5
  write_version_file('0.9.9.5', {'release_date': 'May 1, 2026', 'status': 'Release'})
  yields those two values instead. A missing/empty file yields the new version with
  'unknown' for date and status. The function never raises.

FAILING TEST FIRST (TDD — write it, RUN IT, watch it fail, then fix)
  File: tests/test_bug35_version_file.py         (pytest, tmp_path — no Pi needed)
  Run : python3 -m pytest tests/test_bug35_version_file.py -v
  ota_upgrade.py is safe to import: its only top-level statement is
  `if __name__ == '__main__'`.

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

  EXPECTED BEFORE THE FIX: every test fails with
  AttributeError: module has no attribute 'write_version_file'
  (and test_step7_calls_the_helper fails on the old one-line write).
  If they do not fail first, STOP and escalate.

DONE WHEN
  • All tests FAILED before your edit and PASS after, for BOTH module copies
    (pytest runs each test twice — once per file — via the fixture params).
  • git diff touches only the two ota_upgrade.py files plus the new test.
  • The old one-line write_text call exists nowhere in either file.

ESCALATE-IF  (emit the 🔺 block — do not guess)
  • `release` is not in scope at step 7 under that name
                                   → CLARIFICATION (do not guess a variable)
  • The two copies differ so much that the same patch will not apply to both
                                   → ADVICE (describe the difference; do not force it)
  • You find a real OTA manifest schema showing date/status key names
                                   → ADVICE (Tier 1 will confirm the key names)
  • Importing either module raises  → SOLUTION-REQUEST (contradicts Tier-1's check)

PRE-FLIGHT SELF-CHECK
  1. How many files do I edit?      → exactly 2, in place, same change
  2. May I write today's date?      → no, never invent a date
  3. May step 7 raise?              → no, the outer try/except stays
  4. What proves done?              → 5 tests × 2 modules flip fail→pass

RETURN TO TIER 1
  • The diff for both files
  • pytest output showing fail-before / pass-after (10 test instances)
  • Decision Log: any deviation, or "none"
═══════════════════════════════════════════════════════════════════════
```

---

## Tier-1 verification pass (§25.8)

1. Both copies patched; the one-line `write_text(f'd3kOS Version …')` gone from both.
2. No invented date anywhere — grep for `datetime.now`, `strftime`, `today` in the diff. Any hit is a fail.
3. The outer `try/except` in step 7 intact.
4. `test_downstream_parsers_still_work` proves exactly one line matches the OTA filter — this is the
   subtle failure mode (a second line containing "Version" would silently break `get_current_version`).
5. Tests genuinely failed first — require the pre-fix output.
6. **Cannot verify remotely:** actual OTA behaviour. It has never run on this Pi and must not be
   triggered to test.

## Out of scope
Pi deployment · running an OTA · reconciling the two copies' other differences · the OTA manifest
schema itself · `cloud_agent.py` and `export_categories.py`.
