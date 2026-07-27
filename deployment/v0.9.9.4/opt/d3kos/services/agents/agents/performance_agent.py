#!/usr/bin/env python3
"""
d3kOS Autonomous Agent AA3 — Performance Monitor
v0.9.8

Runs every 5 minutes (same as POLL_INTERVAL — executes on every cycle).
Checks: CPU temperature, CPU usage, memory usage, disk usage.
Auto-remediates: disk critical → clears old /tmp files.
Logs only for thermal/memory critical — does not auto-kill processes
(unsafe on a running boat without operator approval).

Thresholds from MASTER_SYSTEM_SPEC.md §6.4.2:
  CPU temp:  warn 70°C  crit 80°C
  CPU %:     warn 70%   crit 90%
  Memory %:  warn 70%   crit 90%
  Disk used: warn 70%   crit 85%

Dependencies: standard library only (no psutil required).
  - CPU temp via vcgencmd (Raspberry Pi system command)
  - CPU %   via /proc/stat  (two-sample diff)
  - Memory  via /proc/meminfo
  - Disk    via shutil.disk_usage
"""

import logging
import shutil
import subprocess
import time
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from agent_base import AgentBase, AgentResult

log = logging.getLogger('performance_agent')

# ── Thresholds ────────────────────────────────────────────────────────────────

THRESHOLDS = {
    'cpu_temp': {'warn': 70.0, 'crit': 80.0},   # °C
    'cpu_pct':  {'warn': 90.0, 'crit': 95.0},   # % used — warn/crit raised (Pi SwiftShader normal load ~87%)
    'mem_pct':  {'warn': 70.0, 'crit': 90.0},   # % used
    'disk_pct': {'warn': 70.0, 'crit': 85.0},   # % used
}

TMP_MAX_AGE_DAYS = 1   # /tmp files older than this are deleted on disk critical


class PerformanceAgent(AgentBase):
    name             = 'performance'
    label            = 'Performance Monitor'
    interval_seconds = 300   # runs every cycle (5 min)

    def run(self) -> AgentResult:
        metrics = self._collect()
        issues  = self._evaluate(metrics)

        if issues:
            self._remediate(issues, metrics)

        has_crit = any(i['level'] == 'crit' for i in issues)
        has_warn = any(i['level'] == 'warn' for i in issues)
        status   = 'red' if has_crit else ('yellow' if has_warn else 'green')

        if not issues:
            msg = (
                f"CPU {metrics.get('cpu_temp', 0):.0f}\u00b0C \u00b7 "
                f"Mem {metrics.get('mem_pct', 0):.0f}% \u00b7 "
                f"Disk {metrics.get('disk_pct', 0):.0f}%"
            )
        else:
            msg = ' | '.join(i['msg'] for i in issues[:2])  # max 2 issues in message

        return AgentResult(status=status, message=msg, details=metrics)

    # ── Collection ──────────────────────────────────────────────────────────────

    def _collect(self) -> dict:
        metrics = {}

        # CPU temperature — Raspberry Pi vcgencmd
        try:
            out = subprocess.check_output(
                ['vcgencmd', 'measure_temp'], text=True, timeout=5
            )
            # e.g. "temp=45.3'C\n"
            temp_str = out.strip().replace("temp=", "").replace("'C", "")
            metrics['cpu_temp'] = float(temp_str)
        except Exception as e:
            log.debug('vcgencmd failed: %s', e)
            metrics['cpu_temp'] = 0.0

        # CPU usage — two-sample /proc/stat diff (200ms window)
        try:
            metrics['cpu_pct'] = self._cpu_percent()
        except Exception as e:
            log.debug('CPU % read failed: %s', e)
            metrics['cpu_pct'] = 0.0

        # Memory — /proc/meminfo
        try:
            mem = {}
            with open('/proc/meminfo') as f:
                for line in f:
                    if line.startswith(('MemTotal:', 'MemAvailable:')):
                        k, v = line.split(':')
                        mem[k.strip()] = int(v.split()[0])   # kB
            total = mem.get('MemTotal', 1)
            avail = mem.get('MemAvailable', total)
            metrics['mem_pct']     = round((total - avail) / total * 100, 1)
            metrics['mem_free_mb'] = round(avail / 1024, 0)
        except Exception as e:
            log.debug('Memory read failed: %s', e)
            metrics['mem_pct']     = 0.0
            metrics['mem_free_mb'] = 0.0

        # Disk — shutil
        try:
            usage = shutil.disk_usage('/')
            metrics['disk_pct']     = round(usage.used  / usage.total * 100, 1)
            metrics['disk_free_gb'] = round(usage.free  / (1024 ** 3), 1)
        except Exception as e:
            log.debug('Disk read failed: %s', e)
            metrics['disk_pct']     = 0.0
            metrics['disk_free_gb'] = 0.0

        return metrics

    def _cpu_percent(self) -> float:
        """Calculate CPU utilisation from two /proc/stat samples 200ms apart."""
        def read_stat():
            with open('/proc/stat') as f:
                line = f.readline()           # first line: cpu ...
            vals = list(map(int, line.split()[1:]))
            idle  = vals[3]
            total = sum(vals)
            return idle, total

        idle1, total1 = read_stat()
        time.sleep(0.2)
        idle2, total2 = read_stat()

        delta_idle  = idle2  - idle1
        delta_total = total2 - total1
        if delta_total == 0:
            return 0.0
        return round((1.0 - delta_idle / delta_total) * 100, 1)

    # ── Evaluation ──────────────────────────────────────────────────────────────

    def _evaluate(self, metrics: dict) -> list:
        issues = []
        checks = [
            ('cpu_temp', f"CPU {metrics.get('cpu_temp', 0):.0f}\u00b0C"),
            ('cpu_pct',  f"CPU load {metrics.get('cpu_pct', 0):.0f}%"),
            ('mem_pct',  f"Memory {metrics.get('mem_pct', 0):.0f}%"),
            ('disk_pct', f"Disk {metrics.get('disk_pct', 0):.0f}% used"),
        ]
        for key, label in checks:
            val = metrics.get(key, 0)
            t   = THRESHOLDS[key]
            if val >= t['crit']:
                issues.append({'key': key, 'val': val, 'level': 'crit',
                                'msg': f'{label} CRITICAL'})
            elif val >= t['warn']:
                issues.append({'key': key, 'val': val, 'level': 'warn',
                                'msg': f'{label} WARNING'})
        return issues

    # ── Remediation ─────────────────────────────────────────────────────────────

    def _remediate(self, issues: list, metrics: dict):
        for issue in issues:
            key   = issue['key']
            level = issue['level']

            if key == 'disk_pct' and level == 'crit':
                self._clear_tmp()

            if key == 'cpu_temp' and level == 'crit':
                log.critical(
                    'THERMAL CRITICAL: %.1f\u00b0C — check Pi cooling / reduce load',
                    metrics.get('cpu_temp', 0)
                )

            if key == 'cpu_pct' and level == 'crit':
                log.critical(
                    'CPU CRITICAL: %.1f%% — high load sustained. '
                    'No auto-kill (unsafe at sea). Manual review required.',
                    metrics.get('cpu_pct', 0)
                )

            if key == 'mem_pct' and level == 'crit':
                log.critical(
                    'MEMORY CRITICAL: %.1f%% used (%.0f MB free). '
                    'No auto-restart (unsafe at sea). Manual review required.',
                    metrics.get('mem_pct', 0), metrics.get('mem_free_mb', 0)
                )

    def _clear_tmp(self):
        """Delete /tmp files older than TMP_MAX_AGE_DAYS days (mtime)."""
        try:
            result = subprocess.run(
                ['find', '/tmp', '-type', 'f', '-mtime', f'+{TMP_MAX_AGE_DAYS}', '-delete'],
                capture_output=True, text=True, timeout=30
            )
            log.warning(
                'Disk CRITICAL — cleared old /tmp files (mtime >%dd). rc=%d',
                TMP_MAX_AGE_DAYS, result.returncode
            )
        except Exception as e:
            log.error('Failed to clear /tmp: %s', e)
