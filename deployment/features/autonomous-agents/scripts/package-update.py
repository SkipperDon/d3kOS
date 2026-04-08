#!/usr/bin/env python3
"""
d3kOS Update Packager
v0.9.8 — S32

Creates a d3kOS incremental update package (tar.gz) from a list of changed files.
Generates SHA-256 checksum. Outputs upload instructions.

Usage:
    python3 package-update.py --version 0.9.8.1 --files file1.py file2.py

    # Or with a file list:
    python3 package-update.py --version 0.9.8.1 --filelist changed_files.txt

    # With service restart list:
    python3 package-update.py --version 0.9.8.1 \\
        --files agents/update_agent.py agent_base.py \\
        --services d3kos-agents d3kos-dashboard

How files are mapped to Pi paths:
    Files are taken from the repo working directory and placed in the package
    using their Pi filesystem path. You provide the REPO-relative path and the
    REPO-to-PI mapping is applied automatically.

    If a file isn't in the repo, provide its absolute Pi path with --pipath:
        --pipath /opt/d3kos/services/agents/agents/update_agent.py

Output:
    d3kos-<version>.tar.gz         — upload to HostPapa updates/ or archive.org
    d3kos-<version>.tar.gz.sha256  — checksum file (paste into CRM)

Package structure:
    manifest.json
    opt/d3kos/services/agents/agents/update_agent.py
    ...

After running:
    1. Upload tar.gz to HostPapa staging/wp-content/themes/.../updates/
       or archive.org
    2. Open CRM → Publish Update
    3. Fill in version, URL, checksum (from .sha256 file), services
    4. Click Publish — all T1+ Pis receive it within 24h

Run from: /home/boatiq/Helm-OS/
"""

import argparse
import hashlib
import json
import os
import sys
import tarfile
from datetime import date
from pathlib import Path

# ── Repo-to-Pi path mapping ───────────────────────────────────────────────────
# Key: prefix in repo (relative to Helm-OS/)
# Value: corresponding prefix on Pi filesystem (from /)
#
# Add new mappings here as the project grows.

REPO_TO_PI: dict[str, str] = {
    'deployment/features/autonomous-agents/pi_source/':
        'opt/d3kos/services/agents/',
    'deployment/features/autonomous-agents/pi_source/agents/':
        'opt/d3kos/services/agents/agents/',
    'deployment/v0.9.4/pi_source/':
        'opt/d3kos/services/',
    'deployment/d3kOS/dashboard/':
        'opt/d3kos/services/dashboard/',
    'deployment/d3kOS/dashboard/static/':
        'opt/d3kos/services/dashboard/static/',
    'deployment/d3kOS/dashboard/templates/':
        'opt/d3kos/services/dashboard/templates/',
}

REPO_ROOT = Path(__file__).parent.parent.parent.parent  # Helm-OS/


def repo_to_pi_path(repo_rel: str) -> str:
    """Convert a repo-relative path to its Pi absolute path (without leading /)."""
    for prefix, pi_prefix in sorted(REPO_TO_PI.items(), key=lambda x: -len(x[0])):
        if repo_rel.startswith(prefix):
            return pi_prefix + repo_rel[len(prefix):]
    # No mapping found — assume it's already a Pi path
    return repo_rel.lstrip('/')


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description='d3kOS update packager')
    parser.add_argument('--version',   required=True, help='Version string e.g. 0.9.8.1')
    parser.add_argument('--files',     nargs='*', default=[], help='Repo-relative file paths')
    parser.add_argument('--filelist',  help='Text file with one repo-relative path per line')
    parser.add_argument('--pipath',    nargs='*', default=[],
                        help='Absolute Pi path overrides (e.g. /opt/d3kos/services/foo.py)')
    parser.add_argument('--services',  nargs='*', default=[],
                        help='systemd services to restart after applying update')
    parser.add_argument('--type',      default='incremental',
                        choices=['incremental', 'major'], help='Update type')
    parser.add_argument('--notes',     default='', help='Release notes (one line)')
    parser.add_argument('--out',       default='.', help='Output directory')
    args = parser.parse_args()

    files_repo = list(args.files)
    if args.filelist:
        with open(args.filelist) as f:
            files_repo += [l.strip() for l in f if l.strip() and not l.startswith('#')]

    if not files_repo and not args.pipath:
        print('ERROR: provide at least one file via --files, --filelist, or --pipath')
        sys.exit(1)

    out_dir  = Path(args.out)
    pkg_name = f'd3kos-{args.version}.tar.gz'
    pkg_path = out_dir / pkg_name

    # Build file map: pi_path (no leading /) → local file Path
    file_map: dict[str, Path] = {}

    for repo_rel in files_repo:
        local = REPO_ROOT / repo_rel
        if not local.exists():
            print(f'WARNING: {repo_rel} not found at {local} — skipping')
            continue
        pi_path = repo_to_pi_path(repo_rel)
        file_map[pi_path] = local
        print(f'  {repo_rel}\n    → /{pi_path}')

    for pi_abs in (args.pipath or []):
        pi_rel = pi_abs.lstrip('/')
        # For direct Pi paths, try to find the file in the repo
        # by reverse-mapping — if not found, file must exist locally
        local = Path(pi_abs)  # must already exist or be provided
        if not local.exists():
            print(f'WARNING: {pi_abs} does not exist locally — skipping')
            continue
        file_map[pi_rel] = local
        print(f'  {pi_abs}')

    if not file_map:
        print('ERROR: no valid files found')
        sys.exit(1)

    # Build manifest
    manifest = {
        'version':             args.version,
        'type':                args.type,
        'released':            str(date.today()),
        'files':               list(file_map.keys()),
        'services_to_restart': args.services,
        'release_notes':       args.notes,
    }

    print(f'\nBuilding {pkg_name}...')
    with tarfile.open(pkg_path, 'w:gz') as tar:
        # manifest.json
        import io
        manifest_bytes = json.dumps(manifest, indent=2).encode()
        ti = tarfile.TarInfo(name='manifest.json')
        ti.size = len(manifest_bytes)
        tar.addfile(ti, io.BytesIO(manifest_bytes))

        # Files
        for pi_path, local in file_map.items():
            tar.add(local, arcname=pi_path)

    checksum = sha256_file(pkg_path)
    sha_path = pkg_path.with_suffix('.tar.gz.sha256')
    sha_path.write_text(f'sha256:{checksum}  {pkg_name}\n')

    pkg_size = pkg_path.stat().st_size / 1024

    print(f'\n✓ Package created: {pkg_path}  ({pkg_size:.1f} KB)')
    print(f'  SHA-256: sha256:{checksum}')
    print(f'  Checksum file: {sha_path}')
    print(f'\n── Next steps ──────────────────────────────────────────────────')
    print(f'1. Upload {pkg_name} to HostPapa:')
    print(f'   FTP → staging/wp-content/themes/twentytwenty-child/updates/')
    print(f'   URL: https://atmyboat.com/staging/wp-content/themes/twentytwenty-child/updates/{pkg_name}')
    print(f'2. Open Admin CRM → Publish Update')
    print(f'   Version:  {args.version}')
    print(f'   URL:      (paste from step 1)')
    print(f'   Checksum: sha256:{checksum}')
    if args.services:
        print(f'   Services: {", ".join(args.services)}')
    print(f'3. Click Publish → T1+ Pis receive update within 24h')
    print('────────────────────────────────────────────────────────────────')


if __name__ == '__main__':
    main()
