#!/usr/bin/env python3
"""
d3kOS Autonomous Agent AA6 — Backup Agent
v0.9.8

Runs every 24h.
  - Daily   : incremental backup using rsync --link-dest (hard-link unchanged files)
  - Weekly  : full backup (rsync without --link-dest, new complete copy)
  - T3 cloud: compressed config+data upload to HostPapa (critical files only, small)

Backup destination: /mnt/usb-backup/d3kos/
  incremental/YYYY-MM-DD/   ← daily incremental
  full/YYYY-MM-DD/          ← weekly full
  latest -> incremental/YYYY-MM-DD/  (symlink)

What is backed up:
  /opt/d3kos/config/    — tokens, settings, vessel config (CRITICAL)
  /opt/d3kos/data/      — all SQLite DBs, boatlog, engine history (CRITICAL)
                          excludes: /data/exports/  (can be regenerated)
                                    /data/agents/   (runtime state)

What is NOT backed up:
  /opt/d3kos/services/  — application code (redeployable from repo)
  /opt/d3kos/logs/      — logs (trimmed by AA4, not critical)

USB check:
  AA6 checks if /mnt/usb-backup is on a DIFFERENT filesystem than /.
  If same filesystem (USB not plugged in): logs warning, skips backup, returns yellow.
  If separate device: proceeds normally.

T3 cloud sync:
  Compresses /opt/d3kos/config/ + all *.db files into a tar.gz.
  POSTs to HostPapa config-package.php (built in S32 FI3).
  Skipped if endpoint not yet deployed or upload fails (non-critical).
"""

import json
import logging
import os
import shutil
import sqlite3
import subprocess
import tarfile
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from agent_base import AgentBase, AgentResult, STATE_DB

log = logging.getLogger('backup_agent')

# ── Config ────────────────────────────────────────────────────────────────────

BACKUP_MOUNT   = Path('/mnt/usb-backup')
BACKUP_DIR     = BACKUP_MOUNT / 'd3kos'
FULL_INTERVAL  = 7 * 86400          # full backup every 7 days

BACKUP_SOURCES = [
    Path('/opt/d3kos/config'),
    Path('/opt/d3kos/data'),
]

RSYNC_EXCLUDES = [
    '--exclude=data/exports/',
    '--exclude=data/agents/',
    '--exclude=*.tmp',
    '--exclude=*.pyc',
]

CLOUD_CONFIG   = Path('/opt/d3kos/config/cloud-config.json')
LICENSE_FILE   = Path('/opt/d3kos/config/license.json')


class BackupAgent(AgentBase):
    name             = 'backup'
    label            = 'Backup Agent'
    interval_seconds = 86400   # 24 hours

    def run(self) -> AgentResult:
        # ── Check USB is mounted ──────────────────────────────────────────
        if not self._usb_mounted():
            log.warning('USB backup drive not mounted at %s — skipping backup', BACKUP_MOUNT)
            return AgentResult('yellow',
                               f'USB not mounted at {BACKUP_MOUNT} \u2014 plug in drive')

        BACKUP_DIR.mkdir(parents=True, exist_ok=True)

        today     = datetime.now().strftime('%Y-%m-%d')
        do_full   = self._full_backup_due()
        backup_type = 'full' if do_full else 'incremental'

        dest = BACKUP_DIR / backup_type / today
        dest.mkdir(parents=True, exist_ok=True)

        log.info('Starting %s backup → %s', backup_type, dest)

        # ── rsync backup ──────────────────────────────────────────────────
        errors = []
        for src in BACKUP_SOURCES:
            if not src.exists():
                continue
            ok, msg = self._rsync(src, dest, do_full)
            if not ok:
                errors.append(msg)
                log.error('rsync failed for %s: %s', src, msg)

        if errors:
            return AgentResult('red', f'Backup failed: {errors[0]}')

        # ── Update latest symlink ─────────────────────────────────────────
        latest = BACKUP_DIR / 'latest'
        try:
            if latest.is_symlink():
                latest.unlink()
            latest.symlink_to(dest)
        except Exception as e:
            log.warning('Could not update latest symlink: %s', e)

        # ── Record full backup timestamp ──────────────────────────────────
        if do_full:
            self._record_full_backup()

        # ── Clean old backups (keep last 7 incremental, last 4 full) ─────
        self._clean_old(BACKUP_DIR / 'incremental', keep=7)
        self._clean_old(BACKUP_DIR / 'full', keep=4)

        # ── T3 cloud sync ─────────────────────────────────────────────────
        tier = self._current_tier()
        synced = False
        if tier == 'T3':
            synced = self._cloud_sync()

        # ── Result ────────────────────────────────────────────────────────
        size_mb = self._dir_size_mb(dest)
        msg = (f'{backup_type.capitalize()} backup OK \u2014 {size_mb:.0f}MB'
               + (' \u00b7 cloud synced' if synced else ''))
        log.info(msg)
        return AgentResult('green', msg, details={'type': backup_type, 'dest': str(dest),
                                                   'size_mb': size_mb, 'cloud_synced': synced})

    # ── USB check ─────────────────────────────────────────────────────────────

    def _usb_mounted(self) -> bool:
        """Returns True only if /mnt/usb-backup is on a different device than /."""
        try:
            root_dev  = os.stat('/').st_dev
            mount_dev = os.stat(BACKUP_MOUNT).st_dev
            if root_dev == mount_dev:
                return False
            # Also verify it's writable
            test = BACKUP_MOUNT / '.aa6_check'
            test.touch()
            test.unlink()
            return True
        except Exception:
            return False

    # ── rsync ─────────────────────────────────────────────────────────────────

    def _rsync(self, src: Path, dest: Path, full: bool):
        """rsync src/ → dest/src_name/. Returns (success, message)."""
        dst_dir = dest / src.name
        dst_dir.mkdir(parents=True, exist_ok=True)

        cmd = ['rsync', '-a', '--delete'] + RSYNC_EXCLUDES

        if not full:
            # Incremental: hard-link unchanged files from latest backup
            latest = BACKUP_DIR / 'latest' / src.name
            if latest.exists():
                cmd += [f'--link-dest={latest}']

        cmd += [f'{src}/', str(dst_dir)]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode not in (0, 24):   # 24 = partial transfer (ok for live files)
                return False, f'rsync rc={result.returncode}: {result.stderr[:100]}'
            return True, 'OK'
        except subprocess.TimeoutExpired:
            return False, 'rsync timed out after 5 min'
        except Exception as e:
            return False, str(e)

    # ── Full backup scheduling ────────────────────────────────────────────────

    def _full_backup_due(self) -> bool:
        try:
            conn = sqlite3.connect(STATE_DB)
            row  = conn.execute(
                "SELECT last_run_ts FROM agent_runs WHERE name='backup_full'"
            ).fetchone()
            conn.close()
            if not row:
                return True
            return (time.time() - row[0]) >= FULL_INTERVAL
        except Exception:
            return True

    def _record_full_backup(self):
        try:
            conn = sqlite3.connect(STATE_DB)
            conn.execute('''
                INSERT INTO agent_runs (name, last_run_ts, last_status, last_message, run_count)
                VALUES ('backup_full', ?, 'ok', 'full backup complete', 1)
                ON CONFLICT(name) DO UPDATE SET
                    last_run_ts=excluded.last_run_ts,
                    last_message=excluded.last_message,
                    run_count=run_count+1
            ''', (time.time(),))
            conn.commit()
            conn.close()
        except Exception:
            pass

    # ── Cleanup ───────────────────────────────────────────────────────────────

    def _clean_old(self, parent: Path, keep: int):
        if not parent.exists():
            return
        dirs = sorted([d for d in parent.iterdir() if d.is_dir()],
                      key=lambda d: d.name)
        for old in dirs[:-keep]:
            try:
                shutil.rmtree(old)
                log.info('Removed old backup: %s', old)
            except Exception as e:
                log.warning('Could not remove %s: %s', old, e)

    # ── Cloud sync (T3) ───────────────────────────────────────────────────────

    def _cloud_sync(self) -> bool:
        """
        Upload compressed config + data to HostPapa config-package.php (FI3).
        Returns True if successful. Non-fatal on failure.
        """
        try:
            cfg = json.loads(CLOUD_CONFIG.read_text()) if CLOUD_CONFIG.exists() else {}
            api_key      = cfg.get('amboat_api_key', '')
            device_token = cfg.get('device_token', '')
            base_url     = cfg.get('amboat_base_url', '').rstrip('/')
            if not api_key or not base_url:
                return False

            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tmp:
                tmp_path = Path(tmp.name)

            # Create compressed archive of config + all DBs
            with tarfile.open(tmp_path, 'w:gz') as tar:
                config_dir = Path('/opt/d3kos/config')
                if config_dir.exists():
                    tar.add(config_dir, arcname='config')
                for db_file in Path('/opt/d3kos/data').rglob('*.db'):
                    tar.add(db_file, arcname=f'data/{db_file.name}')

            url  = f'{base_url}/wp-content/themes/twentytwenty-child/mobile/config-package.php'
            data = tmp_path.read_bytes()
            req  = urllib.request.Request(url, data=data, method='POST',
                headers={'Authorization': f'Bearer {api_key}',
                         'X-Device-Token': device_token,
                         'Content-Type': 'application/octet-stream'})
            urllib.request.urlopen(req, timeout=60)
            tmp_path.unlink(missing_ok=True)
            log.info('T3 cloud sync complete — %d bytes', len(data))
            return True

        except Exception as e:
            log.debug('T3 cloud sync failed (non-critical): %s', e)
            return False

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _current_tier(self) -> str:
        try:
            return json.loads(LICENSE_FILE.read_text()).get('tier', 'T0')
        except Exception:
            return 'T0'

    def _dir_size_mb(self, path: Path) -> float:
        try:
            total = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
            return total / (1024 * 1024)
        except Exception:
            return 0.0
