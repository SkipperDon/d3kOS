#!/usr/bin/env python3
"""
Export Category Collectors
Collects data for all export categories.

v0.9.4 S1 additions:
  - collect_gps()           Signal K navigation position, SOG, COG
  - collect_engine()        Signal K propulsion.port snapshot
  - collect_system_health() systemctl status for all d3kOS services + CPU/mem/disk
  - collect_system_alerts() Last 50 records from self-healing issues.db (IMPLEMENTED)
  - collect_version()       Reads /opt/d3kos/config/version.txt

Author: d3kOS Team
"""

import sqlite3
import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None


class ExportCategories:
    def __init__(self, installation_id):
        self.installation_id = installation_id

    def collect_all(self):
        """Collect all export categories."""
        categories = {
            'installation_id': self.installation_id,
            'export_timestamp': datetime.utcnow().isoformat() + 'Z',
            'format_version': '1.0',
            'data': {}
        }

        print("Collecting export categories...")

        # Original categories (unchanged)
        categories['data']['engine_benchmark']        = self.collect_engine_benchmark()
        categories['data']['boatlog']                 = self.collect_boatlog()
        categories['data']['marine_vision_captures']  = self.collect_marine_vision_captures()
        categories['data']['marine_vision_snapshots'] = self.collect_marine_vision_snapshots()
        categories['data']['qr_codes']                = self.collect_qr_codes()
        categories['data']['settings']                = self.collect_settings()
        categories['data']['system_alerts']           = self.collect_system_alerts()
        categories['data']['onboarding']              = self.collect_onboarding()
        categories['data']['telemetry']               = self.collect_telemetry()

        # v0.9.4 S1 new categories
        categories['data']['gps']                     = self.collect_gps()
        categories['data']['engine']                  = self.collect_engine()
        categories['data']['system_health']           = self.collect_system_health()
        categories['data']['version']                 = self.collect_version()

        return categories

    # ── ORIGINAL CATEGORIES (unchanged) ──────────────────────────────────────

    def collect_engine_benchmark(self):
        """Category: Engine benchmark data (placeholder)."""
        return {
            'category': 'engine_benchmark',
            'entry_count': 0,
            'entries': []
        }

    def collect_boatlog(self):
        """Category: Boatlog entries (all types — text only, no audio files)."""
        try:
            db_path = '/opt/d3kos/data/boatlog/boatlog.db'
            if not os.path.exists(db_path):
                return {
                    'category': 'boatlog',
                    'entry_count': 0,
                    'entries': [],
                    'note': 'Database not found'
                }

            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT entry_id, timestamp, entry_type, content,
                       latitude, longitude, weather_conditions
                FROM boatlog_entries
                ORDER BY timestamp DESC
            """)

            entries = []
            for row in cursor.fetchall():
                entries.append({
                    'entry_id': row['entry_id'],
                    'timestamp': row['timestamp'],
                    'type': row['entry_type'],
                    'content': row['content'],
                    'gps': {
                        'latitude': row['latitude'],
                        'longitude': row['longitude']
                    },
                    'weather': row['weather_conditions']
                })

            conn.close()

            print(f"  ✓ Boatlog: {len(entries)} entries")
            return {
                'category': 'boatlog',
                'entry_count': len(entries),
                'entries': entries
            }

        except Exception as e:
            print(f"  ✗ Boatlog error: {e}")
            return {'category': 'boatlog', 'entry_count': 0, 'entries': [], 'error': str(e)}

    def collect_marine_vision_captures(self):
        """Category: Marine vision captures (METADATA ONLY — image files stay on Pi)."""
        try:
            db_path = '/opt/d3kos/data/marine-vision/captures.db'
            if not os.path.exists(db_path):
                return {
                    'category': 'marine_vision_captures',
                    'entry_count': 0,
                    'entries': [],
                    'note': 'Metadata only - image files not exported'
                }

            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT capture_id, timestamp, species, confidence,
                       latitude, longitude, file_size
                FROM captures
                ORDER BY timestamp DESC
            """)

            entries = []
            for row in cursor.fetchall():
                entries.append({
                    'capture_id': row['capture_id'],
                    'timestamp': row['timestamp'],
                    'species': row['species'],
                    'confidence': row['confidence'],
                    'gps': {
                        'latitude': row['latitude'],
                        'longitude': row['longitude']
                    },
                    'file_size_bytes': row['file_size']
                    # file_path NOT included — images stay on Pi, stream to phone via WebRTC (S6)
                })

            conn.close()

            print(f"  ✓ Marine Vision Captures: {len(entries)} entries (metadata only)")
            return {
                'category': 'marine_vision_captures',
                'entry_count': len(entries),
                'entries': entries,
                'note': 'Metadata only - image files remain on Pi'
            }

        except Exception as e:
            print(f"  ✗ Marine Vision Captures error: {e}")
            return {'category': 'marine_vision_captures', 'entry_count': 0, 'entries': [], 'error': str(e)}

    def collect_marine_vision_snapshots(self):
        """Category: Marine vision snapshots (placeholder — video files stay on Pi)."""
        return {
            'category': 'marine_vision_snapshots',
            'entry_count': 0,
            'entries': [],
            'note': 'Metadata only - video files remain on Pi'
        }

    def collect_qr_codes(self):
        """Category: QR code data (placeholder)."""
        return {
            'category': 'qr_codes',
            'entry_count': 0,
            'entries': []
        }

    def collect_settings(self):
        """Category: Settings configuration."""
        try:
            license_path = Path('/opt/d3kos/config/license.json')
            license_data = json.loads(license_path.read_text()) if license_path.exists() else {}

            prefs_path = Path('/opt/d3kos/config/user-preferences.json')
            prefs_data = json.loads(prefs_path.read_text()) if prefs_path.exists() else {}

            print(f"  ✓ Settings collected (unit_system: {prefs_data.get('measurement_system', 'unknown')})")
            return {
                'category': 'settings',
                'data': {
                    'license': license_data,
                    'user_preferences': prefs_data,
                    'unit_metadata': {
                        'measurement_system': prefs_data.get('measurement_system', 'metric'),
                        'speed_unit':        'km/h' if prefs_data.get('measurement_system') == 'metric' else 'mph',
                        'temperature_unit':  '°C'   if prefs_data.get('measurement_system') == 'metric' else '°F',
                        'pressure_unit':     'bar'  if prefs_data.get('measurement_system') == 'metric' else 'psi',
                        'volume_unit':       'L'    if prefs_data.get('measurement_system') == 'metric' else 'gal',
                    }
                }
            }

        except Exception as e:
            print(f"  ✗ Settings error: {e}")
            return {'category': 'settings', 'data': {}, 'error': str(e)}

    def collect_system_alerts(self):
        """Category: System alerts from self-healing database.

        Source: /opt/d3kos/data/self-healing/issues.db — issues table
        Returns last 50 records ordered by timestamp DESC.
        Also returns summary counts: total, critical_unresolved, warning_unresolved.
        """
        db_path = '/opt/d3kos/data/self-healing/issues.db'
        try:
            if not os.path.exists(db_path):
                return {
                    'category': 'system_alerts',
                    'entry_count': 0,
                    'entries': [],
                    'summary': {'total': 0, 'critical_unresolved': 0, 'warning_unresolved': 0},
                    'note': 'Self-healing database not found'
                }

            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Last 50 records
            cursor.execute("""
                SELECT id, timestamp, category, severity, description,
                       status, resolved_at, remediation_action
                FROM issues
                ORDER BY timestamp DESC
                LIMIT 50
            """)

            entries = []
            for row in cursor.fetchall():
                entries.append({
                    'id': row['id'],
                    'timestamp': row['timestamp'],
                    'category': row['category'],
                    'severity': row['severity'],
                    'description': row['description'],
                    'status': row['status'],
                    'resolved_at': row['resolved_at'],
                    'remediation_action': row['remediation_action']
                })

            # Summary counts
            cursor.execute("SELECT COUNT(*) FROM issues")
            total = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*) FROM issues
                WHERE severity = 'critical' AND status != 'resolved'
            """)
            critical_unresolved = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*) FROM issues
                WHERE severity = 'warning' AND status != 'resolved'
            """)
            warning_unresolved = cursor.fetchone()[0]

            conn.close()

            print(f"  ✓ System Alerts: {len(entries)} recent, {critical_unresolved} critical unresolved")
            return {
                'category': 'system_alerts',
                'entry_count': len(entries),
                'entries': entries,
                'summary': {
                    'total': total,
                    'critical_unresolved': critical_unresolved,
                    'warning_unresolved': warning_unresolved
                }
            }

        except Exception as e:
            print(f"  ✗ System Alerts error: {e}")
            return {
                'category': 'system_alerts',
                'entry_count': 0,
                'entries': [],
                'summary': {'total': 0, 'critical_unresolved': 0, 'warning_unresolved': 0},
                'error': str(e)
            }

    def collect_onboarding(self):
        """Category: Onboarding/initial setup configuration."""
        try:
            onboarding_path = Path('/opt/d3kos/config/onboarding.json')
            onboarding_data = json.loads(onboarding_path.read_text()) if onboarding_path.exists() else {}

            reset_path = Path('/opt/d3kos/state/onboarding-reset-count.json')
            reset_data = json.loads(reset_path.read_text()) if reset_path.exists() else {'count': 0}

            print(f"  ✓ Onboarding configuration collected")
            return {
                'category': 'onboarding',
                'data': {
                    'configuration': onboarding_data,
                    'reset_count': reset_data.get('count', 0),
                    'completion_timestamp': onboarding_data.get('completed_at')
                }
            }

        except Exception as e:
            print(f"  ✗ Onboarding error: {e}")
            return {'category': 'onboarding', 'data': {}, 'error': str(e)}

    def collect_telemetry(self):
        """Category: Telemetry & analytics."""
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.read().split()[0])

            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
                mem_total     = int([l for l in meminfo.split('\n') if l.startswith('MemTotal')][0].split()[1])
                mem_available = int([l for l in meminfo.split('\n') if l.startswith('MemAvailable')][0].split()[1])

            disk_usage = shutil.disk_usage('/opt/d3kos')

            print(f"  ✓ Telemetry collected")
            return {
                'category': 'telemetry',
                'data': {
                    'system_uptime_seconds': uptime_seconds,
                    'memory_total_kb': mem_total,
                    'memory_available_kb': mem_available,
                    'memory_used_percent': round((mem_total - mem_available) / mem_total * 100, 1),
                    'disk_total_bytes': disk_usage.total,
                    'disk_used_bytes': disk_usage.used,
                    'disk_free_bytes': disk_usage.free,
                    'disk_used_percent': round(disk_usage.used / disk_usage.total * 100, 1)
                }
            }

        except Exception as e:
            print(f"  ✗ Telemetry error: {e}")
            return {'category': 'telemetry', 'data': {}, 'error': str(e)}

    # ── v0.9.4 S1 NEW CATEGORIES ─────────────────────────────────────────────

    def collect_gps(self):
        """Category: GPS / Navigation from Signal K.

        Source: http://localhost:8099/signalk/v1/api/vessels/self/navigation
        Returns null for any field Signal K does not provide.
        Never errors out — returns empty structure on SK unavailability.
        """
        if requests is None:
            return {'category': 'gps', 'data': {}, 'error': 'requests module not available'}

        try:
            r = requests.get(
                'http://localhost:8099/signalk/v1/api/vessels/self/navigation',
                timeout=5
            )
            nav = r.json()

            # Position
            pos_val = nav.get('position', {}).get('value', {})
            lat = pos_val.get('latitude')
            lng = pos_val.get('longitude')

            # Speed over ground — SK gives m/s, convert to knots
            sog_val = nav.get('speedOverGround', {}).get('value')
            sog_knots = round(sog_val * 1.944, 2) if sog_val is not None else None

            # Course over ground — SK gives radians, convert to degrees
            cog_val = nav.get('courseOverGroundTrue', {}).get('value')
            cog_deg = round(cog_val * 57.2958, 2) if cog_val is not None else None

            # Signal K source timestamp
            sk_ts = nav.get('position', {}).get('timestamp')

            # has_fix: true if we have a non-zero lat/lng
            has_fix = bool(lat is not None and lng is not None and (lat != 0 or lng != 0))

            print(f"  ✓ GPS: lat={lat}, lng={lng}, fix={has_fix}")
            return {
                'category': 'gps',
                'data': {
                    'latitude': lat,
                    'longitude': lng,
                    'speed_over_ground_knots': sog_knots,
                    'course_over_ground_deg': cog_deg,
                    'signal_k_timestamp': sk_ts,
                    'has_fix': has_fix
                }
            }

        except Exception as e:
            print(f"  ✗ GPS error: {e}")
            return {
                'category': 'gps',
                'data': {
                    'latitude': None,
                    'longitude': None,
                    'speed_over_ground_knots': None,
                    'course_over_ground_deg': None,
                    'signal_k_timestamp': None,
                    'has_fix': False
                },
                'error': str(e)
            }

    def collect_engine(self):
        """Category: Engine snapshot from Signal K.

        Source: http://localhost:8099/signalk/v1/api/vessels/self/propulsion/port
        Key is propulsion.port — NOT propulsion.0 (confirmed on this Pi).
        All fields optional. Engine off at dock — oil/coolant/fuel will be null.
        """
        if requests is None:
            return {'category': 'engine', 'data': {}, 'error': 'requests module not available'}

        try:
            r = requests.get(
                'http://localhost:8099/signalk/v1/api/vessels/self/propulsion/port',
                timeout=5
            )
            prop = r.json()

            # RPM — SK gives Hz (revolutions/s), multiply by 60 for RPM
            rev_val = prop.get('revolutions', {}).get('value')
            rpm = round(rev_val * 60) if rev_val is not None else None

            # Boost pressure — SK gives Pa, divide by 1000 for kPa
            boost_val = prop.get('boostPressure', {}).get('value')
            boost_kpa = round(boost_val / 1000, 2) if boost_val is not None else None

            # Oil pressure — SK gives Pa, divide by 1000 for kPa
            oil_val = prop.get('oilPressure', {}).get('value')
            oil_kpa = round(oil_val / 1000, 2) if oil_val is not None else None

            # Coolant temperature — SK gives Kelvin, subtract 273.15 for Celsius
            temp_val = prop.get('temperature', {}).get('value')
            coolant_c = round(temp_val - 273.15, 1) if temp_val is not None else None

            # Run time — SK gives seconds, divide by 3600 for hours
            runtime_val = prop.get('runTime', {}).get('value')
            engine_hours = round(runtime_val / 3600, 2) if runtime_val is not None else None

            # Fuel level — from tanks.fuel.0 (separate SK path)
            fuel_pct = None
            try:
                r2 = requests.get(
                    'http://localhost:8099/signalk/v1/api/vessels/self/tanks/fuel/0',
                    timeout=5
                )
                if r2.status_code == 200:
                    fuel_level_val = r2.json().get('currentLevel', {}).get('value')
                    if fuel_level_val is not None:
                        fuel_pct = round(fuel_level_val * 100, 1)
            except Exception:
                pass  # Fuel not available — leave as null

            engine_on = bool(rpm is not None and rpm > 0)

            print(f"  ✓ Engine: rpm={rpm}, on={engine_on}")
            return {
                'category': 'engine',
                'data': {
                    'rpm': rpm,
                    'boost_pressure_kpa': boost_kpa,
                    'oil_pressure_kpa': oil_kpa,
                    'coolant_temp_c': coolant_c,
                    'fuel_level_pct': fuel_pct,
                    'engine_hours': engine_hours,
                    'engine_on': engine_on
                }
            }

        except Exception as e:
            print(f"  ✗ Engine error: {e}")
            return {
                'category': 'engine',
                'data': {
                    'rpm': None,
                    'boost_pressure_kpa': None,
                    'oil_pressure_kpa': None,
                    'coolant_temp_c': None,
                    'fuel_level_pct': None,
                    'engine_hours': None,
                    'engine_on': False
                },
                'error': str(e)
            }

    def collect_system_health(self):
        """Category: System health — all d3kOS service statuses + system metrics.

        Services checked via systemctl is-active.
        Also includes uptime, memory (absolute + percent), disk (absolute + percent), CPU temp.
        Absolute values included so export_worker can map to data-ingress.php format.
        """
        services = [
            'd3kos-dashboard',
            'd3kos-gemini',
            'd3kos-ai-bridge',
            'd3kos-export-manager',
            'd3kos-camera',
            'd3kos-fish-detector',
            'd3kos-keyboard-api',
            'd3kos-ai-api',
            'd3kos-cloud-agent',
            'signalk',
            'avnav',
        ]

        service_statuses = []
        for svc in services:
            try:
                result = subprocess.run(
                    ['systemctl', 'is-active', svc],
                    capture_output=True, text=True, timeout=5
                )
                status = result.stdout.strip()
                if status not in ('active', 'inactive', 'failed'):
                    status = 'unknown'
            except Exception:
                status = 'unknown'
            service_statuses.append({'name': svc, 'status': status})

        # CPU temperature
        cpu_temp_c = None
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                cpu_temp_c = round(int(f.read().strip()) / 1000, 1)
        except Exception:
            pass

        # Uptime
        uptime_seconds = None
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.read().split()[0])
        except Exception:
            pass

        # Memory
        memory_total_kb = None
        memory_available_kb = None
        memory_used_percent = None
        try:
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
            lines = meminfo.split('\n')
            mem_total     = int([l for l in lines if l.startswith('MemTotal')][0].split()[1])
            mem_available = int([l for l in lines if l.startswith('MemAvailable')][0].split()[1])
            memory_total_kb     = mem_total
            memory_available_kb = mem_available
            memory_used_percent = round((mem_total - mem_available) / mem_total * 100, 1)
        except Exception:
            pass

        # Disk
        disk_total_bytes = None
        disk_free_bytes  = None
        disk_used_percent = None
        try:
            du = shutil.disk_usage('/opt/d3kos')
            disk_total_bytes  = du.total
            disk_free_bytes   = du.free
            disk_used_percent = round(du.used / du.total * 100, 1)
        except Exception:
            pass

        print(f"  ✓ System Health: {len(service_statuses)} services checked, cpu_temp={cpu_temp_c}°C")
        return {
            'category': 'system_health',
            'data': {
                'services': service_statuses,
                'uptime_seconds': uptime_seconds,
                'memory_total_kb': memory_total_kb,
                'memory_available_kb': memory_available_kb,
                'memory_used_percent': memory_used_percent,
                'disk_total_bytes': disk_total_bytes,
                'disk_free_bytes': disk_free_bytes,
                'disk_used_percent': disk_used_percent,
                'cpu_temp_c': cpu_temp_c
            }
        }

    def collect_version(self):
        """Category: d3kOS version from version.txt.

        Source: /opt/d3kos/config/version.txt
        Parses: version, release_date, status, raw content.
        """
        version_path = Path('/opt/d3kos/config/version.txt')
        try:
            if not version_path.exists():
                return {
                    'category': 'version',
                    'data': {},
                    'error': 'version.txt not found'
                }

            raw = version_path.read_text().strip()
            data = {'raw': raw}

            for line in raw.split('\n'):
                line = line.strip()
                if line.startswith('d3kOS Version'):
                    data['version'] = line.replace('d3kOS Version', '').strip()
                elif line.startswith('Release Date:'):
                    data['release_date'] = line.replace('Release Date:', '').strip()
                elif line.startswith('Status:'):
                    data['status'] = line.replace('Status:', '').strip()

            print(f"  ✓ Version: {data.get('version', 'unknown')}")
            return {
                'category': 'version',
                'data': data
            }

        except Exception as e:
            print(f"  ✗ Version error: {e}")
            return {'category': 'version', 'data': {}, 'error': str(e)}


if __name__ == "__main__":
    print("Testing Export Categories...")
    categories = ExportCategories("test-installation-id")
    data = categories.collect_all()

    print("\nCollected categories:")
    for name, cat in data['data'].items():
        if 'entry_count' in cat:
            print(f"  - {name}: {cat['entry_count']} entries")
        elif 'error' in cat:
            print(f"  - {name}: ERROR — {cat['error']}")
        else:
            print(f"  - {name}: data collected")

    print("\nExport Categories test complete")
