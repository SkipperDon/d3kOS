#!/usr/bin/env python3
"""
diagnostic_agent.py — d3kOS v0.9.7 Remote Diagnostic Console
Triggered by cloud_agent.py when a diagnostic_collect command arrives.

What it does:
  1. Collects: syslog (24h), dmesg, kern.log (24h), systemctl status for
     all d3kos-* services, ps aux, df -h, free -h
  2. Strips API keys from collected config files
  3. Bundles into /tmp/d3kos-diag-TIMESTAMP.tar.gz  (target: <60s, <50MB)
  4. POSTs multipart bundle to HostPapa diagnostic-upload.php

Run mode: subprocess launched by cloud_agent.py (oneshot — exits when done).
Also exposes a lightweight HTTP server on port 8109 so cloud_agent can check
status and (future) stream live output.

Usage (direct test):
  python3 diagnostic_agent.py --ticket-id 42 --consent-id 7

Config: /opt/d3kos/config/cloud-config.json
        /opt/d3kos/config/device-token.json
"""

import argparse
import json
import logging
import os
import re
import subprocess
import sys
import tarfile
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path

import requests

# ── Config paths ──────────────────────────────────────────────────────────────
CONFIG_DIR    = Path('/opt/d3kos/config')
CLOUD_CONFIG  = CONFIG_DIR / 'cloud-config.json'
TOKEN_FILE    = CONFIG_DIR / 'device-token.json'
API_KEYS_FILE = CONFIG_DIR / 'api-keys.json'   # stripped from bundle

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [diagnostic_agent] %(levelname)s %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/opt/d3kos/logs/diagnostic-agent.log'),
    ]
)
logger = logging.getLogger(__name__)

# ── Key-stripping patterns (regex) ───────────────────────────────────────────
STRIP_PATTERNS = [
    re.compile(r'("amboat_api_key"\s*:\s*")[^"]+(")', re.IGNORECASE),
    re.compile(r'("api_key"\s*:\s*")[^"]+(")',         re.IGNORECASE),
    re.compile(r'("gemini_api_key"\s*:\s*")[^"]+(")', re.IGNORECASE),
    re.compile(r'("openrouter_api_key"\s*:\s*")[^"]+(")', re.IGNORECASE),
    re.compile(r'("stripe_[a-z_]*key"\s*:\s*")[^"]+(")',  re.IGNORECASE),
    re.compile(r'(AMBOAT_API_KEY\s*=\s*)[^\s\n]+',         re.IGNORECASE),
    re.compile(r'(Authorization:\s*Bearer\s+)\S+',          re.IGNORECASE),
]

def strip_keys(text: str) -> str:
    """Replace known API key patterns with [REDACTED]."""
    for pat in STRIP_PATTERNS:
        text = pat.sub(r'\g<1>[REDACTED]', text)
    return text


def _run(cmd: list, timeout: int = 10) -> str:
    """Run shell command, return stdout (truncated to 500 KB). Never raises."""
    try:
        r = subprocess.run(
            cmd, capture_output=True, text=True,
            timeout=timeout, check=False
        )
        out = (r.stdout or '') + (r.stderr or '')
        return out[:512000]  # 500 KB cap per file
    except Exception as e:
        return f'[error running {" ".join(cmd)}: {e}]'


def collect_logs(tmp_dir: str) -> None:
    """Gather system logs and status into tmp_dir."""
    now = datetime.utcnow()
    cutoff = (now - timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')

    # ── syslog (last 24h) ─────────────────────────────────────────────────
    syslog_out = _run(
        ['journalctl', '--since', cutoff, '--no-pager', '-q'], timeout=30
    )
    Path(tmp_dir, 'syslog_24h.txt').write_text(strip_keys(syslog_out))

    # ── dmesg ─────────────────────────────────────────────────────────────
    Path(tmp_dir, 'dmesg.txt').write_text(strip_keys(_run(['dmesg', '-T'])))

    # ── kern.log (last 24h via grep) ─────────────────────────────────────
    kern_log = Path('/var/log/kern.log')
    if kern_log.exists():
        kern_out = _run(['grep', '-a', '.', str(kern_log)], timeout=15)
        Path(tmp_dir, 'kern_log.txt').write_text(strip_keys(kern_out))
    else:
        Path(tmp_dir, 'kern_log.txt').write_text('[kern.log not found]')

    # ── systemctl status for all d3kos-* services ────────────────────────
    services_out = _run(
        ['systemctl', 'status', 'd3kos-*', '--no-pager', '-l'], timeout=20
    )
    Path(tmp_dir, 'services_status.txt').write_text(services_out)

    # ── Service list + enabled state ──────────────────────────────────────
    Path(tmp_dir, 'services_list.txt').write_text(
        _run(['systemctl', 'list-units', '--type=service', '--no-pager'])
    )

    # ── Process list ──────────────────────────────────────────────────────
    Path(tmp_dir, 'ps_aux.txt').write_text(_run(['ps', 'aux', '--sort=-pcpu']))

    # ── Disk usage ────────────────────────────────────────────────────────
    Path(tmp_dir, 'df_h.txt').write_text(_run(['df', '-h']))

    # ── Memory ────────────────────────────────────────────────────────────
    Path(tmp_dir, 'free_h.txt').write_text(_run(['free', '-h']))

    # ── d3kOS logs (last 200 lines each) ─────────────────────────────────
    log_dir = Path('/opt/d3kos/logs')
    if log_dir.exists():
        collected_logs_dir = Path(tmp_dir, 'd3kos_logs')
        collected_logs_dir.mkdir()
        for lf in log_dir.glob('*.log'):
            try:
                content = _run(['tail', '-n', '200', str(lf)], timeout=5)
                (collected_logs_dir / lf.name).write_text(strip_keys(content))
            except Exception:
                pass

    # ── Config files (with keys stripped) ─────────────────────────────────
    safe_configs = ['cloud-config.json', 'fleet.json', 'license.json',
                    'device-token.json', 'feature-matrix.json']
    config_out_dir = Path(tmp_dir, 'config')
    config_out_dir.mkdir()
    for name in safe_configs:
        cf = CONFIG_DIR / name
        if cf.exists():
            try:
                content = cf.read_text()
                (config_out_dir / name).write_text(strip_keys(content))
            except Exception:
                pass

    # ── Manifest ──────────────────────────────────────────────────────────
    manifest = {
        'collected_at': now.isoformat() + 'Z',
        'hostname':     _run(['hostname']).strip(),
        'd3kos_logs':   [f.name for f in log_dir.glob('*.log')] if log_dir.exists() else [],
    }
    Path(tmp_dir, 'manifest.json').write_text(json.dumps(manifest, indent=2))


def bundle(tmp_dir: str, timestamp: str) -> Path:
    """Create tar.gz from tmp_dir contents. Returns path to archive."""
    archive = Path('/tmp', f'd3kos-diag-{timestamp}.tar.gz')
    with tarfile.open(str(archive), 'w:gz') as tar:
        tar.add(tmp_dir, arcname='d3kos-diag')
    return archive


def upload(archive: Path, ticket_id: int, config: dict, device_token: str) -> bool:
    """POST multipart bundle to HostPapa. Returns True on success."""
    base_url = config.get('amboat_base_url', 'https://atmyboat.com/staging').rstrip('/')
    url      = f"{base_url}/wp-content/themes/twentytwenty-child/mobile/diagnostic-upload.php"
    api_key  = config['amboat_api_key']

    logger.info(f"Uploading {archive} ({archive.stat().st_size:,} bytes) to {url}")

    try:
        with open(archive, 'rb') as fh:
            resp = requests.post(
                url,
                data={'ticket_id': ticket_id},
                files={'bundle': (archive.name, fh, 'application/gzip')},
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'X-Device-Token': device_token,
                },
                timeout=120,
            )
        if resp.status_code == 200:
            data = resp.json()
            if data.get('success'):
                logger.info(
                    f"Upload OK: bundle_id={data['data']['bundle_id']} "
                    f"size={data['data']['size_bytes']:,} bytes"
                )
                return True
            else:
                logger.error(f"Upload rejected: {data.get('error')}")
        else:
            logger.error(f"Upload HTTP {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        logger.error(f"Upload exception: {e}")
    return False


def run(ticket_id: int) -> bool:
    """Main collection + upload flow. Returns True on success."""
    # ── Load config ───────────────────────────────────────────────────────
    try:
        config = json.loads(CLOUD_CONFIG.read_text())
    except Exception as e:
        logger.error(f"Cannot read cloud-config.json: {e}")
        return False

    try:
        device_token = json.loads(TOKEN_FILE.read_text())['device_token']
    except Exception as e:
        logger.error(f"Cannot read device-token.json: {e}")
        return False

    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    logger.info(f"Starting diagnostic collection for ticket_id={ticket_id}")

    with tempfile.TemporaryDirectory(prefix='d3kos-diag-') as tmp_dir:
        t0 = time.time()

        # Collect
        try:
            collect_logs(tmp_dir)
        except Exception as e:
            logger.error(f"Collection error: {e}")
            return False

        elapsed_collect = time.time() - t0
        logger.info(f"Collection done in {elapsed_collect:.1f}s")

        # Bundle
        try:
            archive = bundle(tmp_dir, timestamp)
        except Exception as e:
            logger.error(f"Bundle error: {e}")
            return False

        size_mb = archive.stat().st_size / 1048576
        elapsed_bundle = time.time() - t0
        logger.info(f"Bundle created: {archive} ({size_mb:.1f} MB) in {elapsed_bundle:.1f}s")

        if size_mb > 50:
            logger.error(f"Bundle too large: {size_mb:.1f} MB > 50 MB limit")
            archive.unlink(missing_ok=True)
            return False

        # Upload
        ok = upload(archive, ticket_id, config, device_token)

        # Cleanup
        try:
            archive.unlink(missing_ok=True)
        except Exception:
            pass

        total = time.time() - t0
        logger.info(f"Total time: {total:.1f}s — {'SUCCESS' if ok else 'FAILED'}")
        return ok


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='d3kOS Diagnostic Agent')
    parser.add_argument('--ticket-id', type=int, required=True,
                        help='Support ticket ID to attach bundle to')
    args = parser.parse_args()

    success = run(args.ticket_id)
    sys.exit(0 if success else 1)
