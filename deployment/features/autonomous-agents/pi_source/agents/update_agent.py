#!/usr/bin/env python3
"""
d3kOS Autonomous Agent AA2 — Update Check & Apply
v0.9.8

Runs every 24h (or on first boot if overdue).

Tier behaviour:
  T0 (no account): checks HostPapa public version endpoint if internet available.
                   Notifies via Pi dashboard notice bar only. Never sends to cloud.
                   Fails silently if offline.
  T1+:             Same check + auto-applies incremental updates.
                   Notifies via Pi notice bar + email (HostPapa watchdog pattern).
                   Major releases auto-applied if t1_upgrade=true in manifest.

Update package format (tar.gz at archive.org):
  d3kos-X.X.X.tar.gz
    manifest.json       — {"version","files":[pipath,...],"services_to_restart":[...]}
    opt/d3kos/...       — changed files mirrored from Pi filesystem

Backup: /opt/d3kos/backups/pre-vX.X.X/  (files before patch applied)
        Kept for MAX_BACKUPS sets — older sets cleaned by AA4.

Notice file: /opt/d3kos/data/update-notice.json  — read by /update/status → dashboard.
"""

import json
import logging
import shutil
import subprocess
import tarfile
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from agent_base import AgentBase, AgentResult

log = logging.getLogger('update_agent')

# ── Config ────────────────────────────────────────────────────────────────────

VERSION_URL   = 'https://atmyboat.com/staging/wp-content/themes/twentytwenty-child/mobile/version.php'
LICENSE_FILE  = Path('/opt/d3kos/config/license.json')
CLOUD_CONFIG  = Path('/opt/d3kos/config/cloud-config.json')
NOTICE_FILE   = Path('/opt/d3kos/data/update-notice.json')
BACKUP_BASE   = Path('/opt/d3kos/backups')
FETCH_TIMEOUT = 15   # seconds


class UpdateAgent(AgentBase):
    name             = 'update'
    label            = 'Update Check'
    interval_seconds = 86400   # 24 hours

    def run(self) -> AgentResult:
        current = self._current_version()
        tier    = self._current_tier()

        # ── Fetch version manifest ──────────────────────────────────────────
        try:
            latest = self._fetch_version()
        except urllib.error.HTTPError as e:
            log.warning('Update check: server error %s %s', e.code, e.reason)
            return AgentResult('yellow', f'Update check: server error {e.code}')
        except Exception as e:
            # Connection error, DNS failure, timeout — Pi is offline
            log.info('Update check skipped — no internet: %s', e)
            return AgentResult('green', 'Update check: offline')

        inc = latest.get('incremental', {})
        maj = latest.get('major', {})

        inc_ver = inc.get('version', '')
        maj_ver = maj.get('version', '')

        inc_available = inc_ver and self._is_newer(inc_ver, current)
        maj_available = maj_ver and self._is_newer(maj_ver, current) and maj.get('t1_upgrade', False)

        self._update_last_check()

        # ── Nothing new ──────────────────────────────────────────────────────
        if not inc_available and not maj_available:
            self._clear_notice()
            log.info('Up to date — v%s', current)
            return AgentResult('green', f'Up to date \u2014 v{current}')

        # ── Update available ─────────────────────────────────────────────────
        update_info  = maj if maj_available else inc
        update_ver   = maj_ver if maj_available else inc_ver
        update_type  = 'major' if maj_available else 'incremental'

        if tier in ('T1', 'T2', 'T3') and update_info.get('url'):
            # T1+ auto-apply
            ok, msg = self._apply_update(update_info, current, update_ver)
            if ok:
                self._clear_notice()
                self._notify_cloud(tier, f'd3kOS updated to v{update_ver}', update_type)
                return AgentResult('green', f'Updated to v{update_ver}')
            else:
                self._write_notice(update_type, current, update_ver, update_info, failed=True)
                return AgentResult('red', f'Update failed: {msg}')
        else:
            # T0 or no URL yet — notify only
            self._write_notice(update_type, current, update_ver, update_info)
            log.info('%s update available: v%s → v%s (tier=%s)', update_type, current, update_ver, tier)
            return AgentResult('yellow', f'v{update_ver} available \u2014 see Pi notice')

    # ── Version helpers ───────────────────────────────────────────────────────

    def _current_version(self) -> str:
        try:
            data = json.loads(LICENSE_FILE.read_text())
            return data.get('version', '0.0.0')
        except Exception:
            return '0.0.0'

    def _current_tier(self) -> str:
        try:
            data = json.loads(LICENSE_FILE.read_text())
            return data.get('tier', 'T0')
        except Exception:
            return 'T0'

    def _is_newer(self, candidate: str, current: str) -> bool:
        """Compare version strings (e.g. '0.9.8.1' > '0.9.8')."""
        try:
            c_parts = [int(x) for x in candidate.replace('-', '.').split('.')]
            k_parts = [int(x) for x in current.replace('-', '.').split('.')]
            # Pad shorter version with zeros
            length = max(len(c_parts), len(k_parts))
            c_parts += [0] * (length - len(c_parts))
            k_parts += [0] * (length - len(k_parts))
            return c_parts > k_parts
        except Exception:
            return False

    def _fetch_version(self) -> dict:
        req = urllib.request.Request(VERSION_URL, headers={'User-Agent': 'd3kOS-UpdateAgent/1.0'})
        with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT) as resp:
            return json.loads(resp.read().decode('utf-8'))

    def _update_last_check(self):
        try:
            data = json.loads(LICENSE_FILE.read_text())
            data['last_update_check'] = datetime.now(tz=timezone.utc).isoformat()
            LICENSE_FILE.write_text(json.dumps(data, indent=2))
        except Exception as e:
            log.warning('Could not update last_update_check: %s', e)

    # ── Apply update ──────────────────────────────────────────────────────────

    def _apply_update(self, update_info: dict, current_ver: str, new_ver: str):
        """
        Download tar.gz, verify checksum, back up, apply, restart services.
        Returns (success: bool, message: str).
        """
        url      = update_info.get('url', '')
        checksum = update_info.get('checksum', '')

        if not url:
            return False, 'No download URL in manifest'

        log.info('Downloading update v%s from %s', new_ver, url)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir) / f'd3kos-{new_ver}.tar.gz'

            # Download
            try:
                urllib.request.urlretrieve(url, str(tmp_path))
            except Exception as e:
                return False, f'Download failed: {e}'

            # Verify checksum (SHA-256) if provided
            if checksum:
                import hashlib
                sha = hashlib.sha256(tmp_path.read_bytes()).hexdigest()
                expected = checksum.replace('sha256:', '')
                if sha != expected:
                    return False, f'Checksum mismatch — expected {expected[:16]}...'

            # Extract and read manifest
            try:
                with tarfile.open(tmp_path) as tar:
                    tar.extractall(tmpdir)
            except Exception as e:
                return False, f'Extract failed: {e}'

            manifest_path = Path(tmpdir) / 'manifest.json'
            if not manifest_path.exists():
                return False, 'No manifest.json in package'

            manifest = json.loads(manifest_path.read_text())
            files_to_update   = manifest.get('files', [])
            services_to_restart = manifest.get('services_to_restart', [])

            # Back up files that will be changed
            backup_dir = BACKUP_BASE / f'pre-v{new_ver}'
            backup_dir.mkdir(parents=True, exist_ok=True)
            backed_up = []
            for rel_path in files_to_update:
                src = Path('/') / rel_path
                if src.exists():
                    dst = backup_dir / rel_path
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                    backed_up.append(str(src))

            log.info('Backed up %d files to %s', len(backed_up), backup_dir)

            # Apply files
            extract_root = Path(tmpdir)
            for rel_path in files_to_update:
                src = extract_root / rel_path
                dst = Path('/') / rel_path
                if src.exists():
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                    log.info('Updated: %s', dst)

            # Update version in license.json
            try:
                data = json.loads(LICENSE_FILE.read_text())
                data['version'] = new_ver
                LICENSE_FILE.write_text(json.dumps(data, indent=2))
            except Exception as e:
                log.warning('Could not update version in license.json: %s', e)

        # Restart affected services — check each came back up
        failed_services = []
        for svc in services_to_restart:
            try:
                subprocess.run(['sudo', 'systemctl', 'restart', svc],
                               capture_output=True, timeout=30)
                time.sleep(5)
                r = subprocess.run(['systemctl', 'is-active', svc],
                                   capture_output=True, text=True)
                if r.stdout.strip() != 'active':
                    failed_services.append(svc)
            except Exception as e:
                failed_services.append(f'{svc} ({e})')

        if failed_services:
            log.error('Services failed after update: %s — rolling back', failed_services)
            self._rollback(current_ver, files_to_update, backup_dir)
            return False, f'Rollback — services failed: {", ".join(failed_services)}'

        log.info('Update to v%s applied successfully', new_ver)
        return True, 'OK'

    def _rollback(self, current_ver: str, files: list, backup_dir: Path):
        """Restore backed-up files and restart services."""
        for rel_path in files:
            src = backup_dir / rel_path
            dst = Path('/') / rel_path
            if src.exists():
                shutil.copy2(src, dst)
                log.info('Rolled back: %s', dst)
        # Update version back
        try:
            data = json.loads(LICENSE_FILE.read_text())
            data['version'] = current_ver
            LICENSE_FILE.write_text(json.dumps(data, indent=2))
        except Exception:
            pass
        log.warning('Rollback to v%s complete', current_ver)

    # ── Notice file ───────────────────────────────────────────────────────────

    def _write_notice(self, update_type: str, current_ver: str,
                      new_ver: str, info: dict, failed: bool = False):
        NOTICE_FILE.parent.mkdir(parents=True, exist_ok=True)
        NOTICE_FILE.write_text(json.dumps({
            'available':   True,
            'type':        update_type,
            'current':     current_ver,
            'version':     new_ver,
            'released':    info.get('released', ''),
            'failed':      failed,
            'detected':    datetime.now(tz=timezone.utc).isoformat(),
        }, indent=2))

    def _clear_notice(self):
        try:
            NOTICE_FILE.unlink(missing_ok=True)
        except Exception:
            pass

    # ── Cloud notification (T1+ only) ─────────────────────────────────────────

    def _notify_cloud(self, tier: str, message: str, update_type: str):
        """POST to HostPapa watchdog-alert.php — same pattern as watchdog."""
        if tier not in ('T1', 'T2', 'T3'):
            return
        try:
            cfg = json.loads(CLOUD_CONFIG.read_text()) if CLOUD_CONFIG.exists() else {}
            api_key      = cfg.get('amboat_api_key', '')
            device_token = cfg.get('device_token', '')
            base_url     = cfg.get('amboat_base_url', '').rstrip('/')
            if not api_key or not base_url:
                return

            url     = f'{base_url}/wp-content/themes/twentytwenty-child/mobile/watchdog-alert.php'
            payload = json.dumps({
                'service':   'd3kos-agents',
                'label':     f'd3kOS Update ({update_type})',
                'reason':    message,
                'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            }).encode()
            req = urllib.request.Request(url, data=payload, method='POST',
                headers={'Authorization': f'Bearer {api_key}',
                         'X-Device-Token': device_token,
                         'Content-Type': 'application/json'})
            urllib.request.urlopen(req, timeout=10)
        except Exception as e:
            log.debug('Cloud notify failed (non-critical): %s', e)
