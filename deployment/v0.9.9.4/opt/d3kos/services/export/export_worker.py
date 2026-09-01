#!/usr/bin/env python3
"""
Export Queue Background Worker
Handles retry logic and automatic upload to AtMyBoat.com.

v0.9.4 S1 changes:
  - Reads amboat_api_key and base_url from /opt/d3kos/config/cloud-config.json
  - Reads device_token from /opt/d3kos/config/device-token.json
  - POSTs to data-ingress.php (not /api/v1/data/import)
  - Maps export categories JSON to data-ingress.php expected format
  - Sends boatlog text entries to AtMyBoat.com

Author: d3kOS Team
"""

import json
import time
from pathlib import Path
from threading import Thread, Event

import requests

import sys
sys.path.insert(0, '/opt/d3kos/services/export')
from export_queue import ExportQueue

CLOUD_CONFIG_FILE  = Path('/opt/d3kos/config/cloud-config.json')
DEVICE_TOKEN_FILE  = Path('/opt/d3kos/config/device-token.json')
LICENSE_FILE       = Path('/opt/d3kos/config/license.json')


class ExportWorker:
    def __init__(self, central_api_url='https://atmyboat.com'):
        self.central_api_url = central_api_url
        self.queue = ExportQueue()
        self.stop_event = Event()
        self.worker_thread = None
        self._cloud_config = None
        self._device_token = None

    def start(self):
        if self.worker_thread and self.worker_thread.is_alive():
            print("Worker already running")
            return
        self.stop_event.clear()
        self.worker_thread = Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        print("Export worker started")

    def stop(self):
        self.stop_event.set()
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        print("Export worker stopped")

    def _worker_loop(self):
        while not self.stop_event.is_set():
            try:
                entry = self.queue.get_next_pending()
                if entry:
                    print(f"Processing export: {entry['queue_id']}")
                    self._process_export(entry)

                if not self._check_network():
                    print("No network connectivity, waiting...")

                self.stop_event.wait(30)

            except Exception as e:
                print(f"Worker error: {e}")
                self.stop_event.wait(60)

    def _check_network(self):
        try:
            response = requests.get('https://www.google.com', timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def _load_cloud_config(self):
        """Load cloud-config.json. Cached after first read."""
        if self._cloud_config:
            return self._cloud_config
        try:
            with open(CLOUD_CONFIG_FILE) as f:
                self._cloud_config = json.load(f)
            return self._cloud_config
        except FileNotFoundError:
            print(f"cloud-config.json not found at {CLOUD_CONFIG_FILE} — export upload skipped")
            return {}
        except Exception as e:
            print(f"Failed to load cloud-config.json: {e}")
            return {}

    def _load_device_token(self):
        """Load device token from device-token.json. Cached after first read."""
        if self._device_token:
            return self._device_token
        try:
            with open(DEVICE_TOKEN_FILE) as f:
                data = json.load(f)
                self._device_token = data.get('device_token')
            return self._device_token
        except FileNotFoundError:
            print(f"device-token.json not found — run cloud-agent first to generate it")
            return None
        except Exception as e:
            print(f"Failed to load device-token.json: {e}")
            return None

    def _build_ingress_payload(self, export_json):
        """Map export categories JSON to data-ingress.php expected format.

        data-ingress.php expects:
          installation_id, d3kos_version, vessel_name, timestamp,
          position {lat, lng}, engine {rpm, coolant_temp, oil_pressure, fuel_level, hours},
          system {uptime_s, disk_free_mb, cpu_temp, mem_free_mb},
          alerts [{type, message}], boatlog [{entry_id, timestamp, type, content}]
        """
        data = export_json.get('data', {})

        payload = {
            'installation_id': export_json.get('installation_id'),
            'timestamp': export_json.get('export_timestamp'),
        }

        # d3kOS version
        version_data = data.get('version', {}).get('data', {})
        if version_data.get('version'):
            payload['d3kos_version'] = version_data['version']

        # Vessel name from settings → user_preferences
        settings = data.get('settings', {}).get('data', {})
        prefs = settings.get('user_preferences', {}) if isinstance(settings, dict) else {}
        payload['vessel_name'] = prefs.get('vessel_name', '')

        # GPS position
        gps = data.get('gps', {}).get('data', {})
        if gps.get('latitude') is not None and gps.get('longitude') is not None:
            payload['position'] = {
                'lat': gps['latitude'],
                'lng': gps['longitude']
            }

        # Engine snapshot
        engine_cat = data.get('engine', {}).get('data', {})
        if engine_cat:
            engine = {}
            if engine_cat.get('rpm') is not None:
                engine['rpm'] = engine_cat['rpm']
            if engine_cat.get('coolant_temp_c') is not None:
                engine['coolant_temp'] = engine_cat['coolant_temp_c']
            if engine_cat.get('oil_pressure_kpa') is not None:
                engine['oil_pressure'] = engine_cat['oil_pressure_kpa']
            if engine_cat.get('fuel_level_pct') is not None:
                engine['fuel_level'] = engine_cat['fuel_level_pct']
            if engine_cat.get('engine_hours') is not None:
                engine['hours'] = engine_cat['engine_hours']
            if engine_cat.get('battery_voltage_v') is not None:
                engine['battery_voltage'] = engine_cat['battery_voltage_v']
            if engine:
                payload['engine'] = engine

        # System metrics
        health = data.get('system_health', {}).get('data', {})
        if health:
            system = {}
            if health.get('uptime_seconds') is not None:
                system['uptime_s'] = int(health['uptime_seconds'])
            if health.get('cpu_temp_c') is not None:
                system['cpu_temp'] = health['cpu_temp_c']
            if health.get('memory_available_kb') is not None:
                system['mem_free_mb'] = int(health['memory_available_kb'] / 1024)
            if health.get('disk_free_bytes') is not None:
                system['disk_free_mb'] = int(health['disk_free_bytes'] / (1024 * 1024))
            if system:
                payload['system'] = system

        # Alerts — unresolved only, cap at 20 per push
        alerts_cat = data.get('system_alerts', {})
        alerts = []
        # Exclude internal service_down alerts — Pi self-healing issue, not a marine event
        INTERNAL_ALERT_TYPES = {'service_down', 'service_restart', 'high_memory', 'high_cpu'}
        for entry in alerts_cat.get('entries', []):
            if entry.get('status') == 'resolved':
                continue
            if entry.get('category') in INTERNAL_ALERT_TYPES:
                continue
            alerts.append({
                'type': entry.get('category', 'unknown'),
                'message': str(entry.get('description', ''))[:500]
            })
        if alerts:
            payload['alerts'] = alerts[:20]

        # Boatlog — text entries only, cap at 50 per push
        boatlog_cat = data.get('boatlog', {})
        boatlog_entries = []
        for entry in boatlog_cat.get('entries', [])[:50]:
            boatlog_entries.append({
                'entry_id': entry.get('entry_id'),
                'timestamp': entry.get('timestamp'),
                'type': entry.get('type'),
                'content': entry.get('content')
            })
        if boatlog_entries:
            payload['boatlog'] = boatlog_entries

        # BUG-65 Step 2: tier claim-vs-detected audit — makes local forgery visible to the server.
        # Server should compare tier_claimed vs entitlement record and flag mismatches for review.
        # Do NOT auto-downgrade — a false positive at sea strips paid features mid-passage.
        try:
            with open(LICENSE_FILE) as f:
                _lic = json.load(f)
            _claimed_raw = _lic.get('tier', 0)
            if isinstance(_claimed_raw, str) and _claimed_raw.upper().startswith('T'):
                try:
                    tier_claimed = int(_claimed_raw[1:])
                except ValueError:
                    tier_claimed = 0
            else:
                try:
                    tier_claimed = int(_claimed_raw)
                except (ValueError, TypeError):
                    tier_claimed = 0
        except Exception:
            tier_claimed = 0

        opencpn_present          = Path('/opt/opencpn').is_dir()
        subscription_key_present = Path('/opt/d3kos/config/subscription.key').is_file()

        if opencpn_present and subscription_key_present:
            tier_detected = 3
        elif opencpn_present:
            tier_detected = 2
        else:
            tier_detected = 1

        payload['tier_claimed']            = tier_claimed
        payload['tier_detected']           = tier_detected
        payload['opencpn_present']         = opencpn_present
        payload['subscription_key_present'] = subscription_key_present

        return payload

    def _sync_tier_from_response(self, tier_str):
        """P6: Sync tier from data-ingress.php response to license.json."""
        tier_map = {'T1': 1, 'T2': 2, 'T3': 3}
        tier_int = tier_map.get(str(tier_str).upper())
        if tier_int is None:
            return
        try:
            with open(LICENSE_FILE) as f:
                license_data = json.load(f)
            current = license_data.get('tier', 0)
            if current != tier_int:
                license_data['tier'] = tier_int
                with open(LICENSE_FILE, 'w') as f:
                    json.dump(license_data, f, indent=2)
                print(f"Tier synced from server: {current} → {tier_int}")
        except Exception as e:
            print(f"Tier sync failed: {e}")

    def _process_export(self, entry):
        """Upload export to AtMyBoat.com data-ingress.php."""
        queue_id    = entry['queue_id']
        export_file = entry['export_file']

        try:
            self.queue.mark_uploading(queue_id)

            export_path = Path(export_file)
            if not export_path.exists():
                raise FileNotFoundError(f"Export file not found: {export_file}")

            with open(export_file) as f:
                export_json = json.load(f)

            # Load credentials
            cloud_config = self._load_cloud_config()
            api_key      = cloud_config.get('amboat_api_key', '')
            base_url     = cloud_config.get('amboat_base_url', self.central_api_url).rstrip('/')
            device_token = self._load_device_token()

            if not api_key or api_key == 'YOUR_32_CHAR_HEX_KEY_HERE':
                raise ValueError(
                    "amboat_api_key not configured in cloud-config.json. "
                    "Set the key to match AMBOAT_API_KEY in mobile/config.php on AtMyBoat.com."
                )
            if not device_token:
                raise ValueError(
                    "device-token.json not found. "
                    "Start d3kos-cloud-agent once to generate the device token, "
                    "then register it in AtMyBoat.com staging phpMyAdmin."
                )

            # Build and POST payload
            payload  = self._build_ingress_payload(export_json)
            endpoint = f"{base_url}/wp-content/themes/twentytwenty-child/mobile/data-ingress.php"
            headers  = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}',
                'X-Device-Token': device_token,
                'User-Agent': 'Mozilla/5.0',  # nginx blocks python-requests UA on HostPapa (BUG-54)
            }

            print(f"Uploading to {endpoint}")
            response = requests.post(endpoint, json=payload, headers=headers, timeout=30)

            if response.status_code == 200:
                self.queue.mark_success(queue_id)
                print(f"✓ Export uploaded: {queue_id}")
                # P6: Read tier from response and sync to license.json
                try:
                    resp_data = response.json()
                    resp_tier = resp_data.get('data', {}).get('tier')
                    if resp_tier:
                        self._sync_tier_from_response(resp_tier)
                except Exception:
                    pass
            else:
                error = f"HTTP {response.status_code}: {response.text[:200]}"
                self.queue.mark_failed(queue_id, error)
                print(f"✗ Export upload failed: {error}")

        except FileNotFoundError as e:
            self.queue.mark_failed(queue_id, str(e))
            print(f"✗ Export file missing: {e}")

        except Exception as e:
            self.queue.mark_failed(queue_id, str(e))
            print(f"✗ Export upload error: {e}")


if __name__ == "__main__":
    print("Testing Export Worker...")
    worker = ExportWorker()
    worker.start()
    print("Worker running... Press Ctrl+C to stop")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping worker...")
        worker.stop()
        print("Worker stopped")
