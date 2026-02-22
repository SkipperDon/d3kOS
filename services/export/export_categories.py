#!/usr/bin/env python3
# d3kOS - Marine Intelligence Operating System
# Copyright (C) 2026 Donald Moskaluk / AtMyBoat.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# For commercial licensing contact: skipperdon@atmyboat.com

"""
Export Category Collectors
Collects data for all 9 export categories per MASTER_SYSTEM_SPEC.md Section 8.3

Author: d3kOS Team
Date: 2026-02-20
"""

import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path

class ExportCategories:
    def __init__(self, installation_id):
        self.installation_id = installation_id

    def collect_all(self):
        """Collect all 9 categories"""
        categories = {
            'installation_id': self.installation_id,
            'export_timestamp': datetime.utcnow().isoformat() + 'Z',
            'format_version': '1.0',
            'data': {}
        }

        # Collect each category
        print("Collecting export categories...")
        categories['data']['engine_benchmark'] = self.collect_engine_benchmark()
        categories['data']['boatlog'] = self.collect_boatlog()
        categories['data']['marine_vision_captures'] = self.collect_marine_vision_captures()
        categories['data']['marine_vision_snapshots'] = self.collect_marine_vision_snapshots()
        categories['data']['qr_codes'] = self.collect_qr_codes()
        categories['data']['settings'] = self.collect_settings()
        categories['data']['system_alerts'] = self.collect_system_alerts()
        categories['data']['onboarding'] = self.collect_onboarding()
        categories['data']['telemetry'] = self.collect_telemetry()

        return categories

    def collect_engine_benchmark(self):
        """Category 1: Engine benchmark data"""
        # Placeholder - implement when engine benchmark feature is added
        return {
            'category': 'engine_benchmark',
            'entry_count': 0,
            'entries': []
        }

    def collect_boatlog(self):
        """Category 2: Boatlog entries (all types)"""
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
        """Category 3: Marine vision captures (METADATA ONLY)"""
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
                    # NOTE: file_path NOT included in export (privacy)
                })

            conn.close()

            print(f"  ✓ Marine Vision Captures: {len(entries)} entries")
            return {
                'category': 'marine_vision_captures',
                'entry_count': len(entries),
                'entries': entries,
                'note': 'Metadata only - image files not exported'
            }

        except Exception as e:
            print(f"  ✗ Marine Vision Captures error: {e}")
            return {'category': 'marine_vision_captures', 'entry_count': 0, 'entries': [], 'error': str(e)}

    def collect_marine_vision_snapshots(self):
        """Category 4: Marine vision snapshots (METADATA ONLY)"""
        # Placeholder - snapshots feature not yet implemented
        return {
            'category': 'marine_vision_snapshots',
            'entry_count': 0,
            'entries': [],
            'note': 'Metadata only - video files not exported'
        }

    def collect_qr_codes(self):
        """Category 5: QR code data"""
        # Placeholder - QR code data tracking not yet implemented
        return {
            'category': 'qr_codes',
            'entry_count': 0,
            'entries': []
        }

    def collect_settings(self):
        """Category 6: Settings configuration"""
        try:
            # Read license.json
            license_path = Path('/opt/d3kos/config/license.json')
            if license_path.exists():
                license_data = json.loads(license_path.read_text())
            else:
                license_data = {}

            print(f"  ✓ Settings collected")
            return {
                'category': 'settings',
                'data': {
                    'license': license_data
                }
            }

        except Exception as e:
            print(f"  ✗ Settings error: {e}")
            return {'category': 'settings', 'data': {}, 'error': str(e)}

    def collect_system_alerts(self):
        """Category 7: System alerts"""
        # Placeholder - system alerts feature not yet implemented
        return {
            'category': 'system_alerts',
            'entry_count': 0,
            'entries': []
        }

    def collect_onboarding(self):
        """Category 8: Onboarding/initial setup configuration"""
        try:
            # Read onboarding.json
            onboarding_path = Path('/opt/d3kos/config/onboarding.json')
            if onboarding_path.exists():
                onboarding_data = json.loads(onboarding_path.read_text())
            else:
                onboarding_data = {}

            # Read reset counter
            reset_path = Path('/opt/d3kos/state/onboarding-reset-count.json')
            if reset_path.exists():
                reset_data = json.loads(reset_path.read_text())
            else:
                reset_data = {'count': 0}

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
        """Category 9: Telemetry & analytics (NEW)"""
        try:
            # System uptime
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.read().split()[0])

            # Memory usage
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
                mem_total = int([line for line in meminfo.split('\n') if 'MemTotal' in line][0].split()[1])
                mem_available = int([line for line in meminfo.split('\n') if 'MemAvailable' in line][0].split()[1])

            # Disk usage
            import shutil
            disk_usage = shutil.disk_usage('/opt/d3kos')

            print(f"  ✓ Telemetry collected")
            return {
                'category': 'telemetry',
                'data': {
                    'system_uptime_seconds': uptime_seconds,
                    'memory_total_kb': mem_total,
                    'memory_available_kb': mem_available,
                    'memory_used_percent': ((mem_total - mem_available) / mem_total) * 100,
                    'disk_total_bytes': disk_usage.total,
                    'disk_used_bytes': disk_usage.used,
                    'disk_free_bytes': disk_usage.free,
                    'disk_used_percent': (disk_usage.used / disk_usage.total) * 100
                }
            }

        except Exception as e:
            print(f"  ✗ Telemetry error: {e}")
            return {'category': 'telemetry', 'data': {}, 'error': str(e)}


if __name__ == "__main__":
    # Test category collection
    print("Testing Export Categories...")

    categories = ExportCategories("test-installation-id")
    data = categories.collect_all()

    print("\nCollected categories:")
    for category_name, category_data in data['data'].items():
        if 'entry_count' in category_data:
            print(f"  - {category_name}: {category_data['entry_count']} entries")
        else:
            print(f"  - {category_name}: data collected")

    print("\nExport Categories test complete")
