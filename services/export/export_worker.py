#!/usr/bin/env python3
"""
Export Queue Background Worker
Handles retry logic and automatic upload

Author: d3kOS Team
Date: 2026-02-20
"""

import time
import requests
from threading import Thread, Event
from pathlib import Path
import sys

# Add service directory to path
sys.path.insert(0, '/opt/d3kos/services/export')
from export_queue import ExportQueue

class ExportWorker:
    def __init__(self, central_api_url="https://d3kos-cloud-api.example.com"):
        self.central_api_url = central_api_url
        self.queue = ExportQueue()
        self.stop_event = Event()
        self.worker_thread = None

    def start(self):
        """Start background worker thread"""
        if self.worker_thread and self.worker_thread.is_alive():
            print("Worker already running")
            return

        self.stop_event.clear()
        self.worker_thread = Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        print("Export worker started")

    def stop(self):
        """Stop background worker thread"""
        self.stop_event.set()
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        print("Export worker stopped")

    def _worker_loop(self):
        """Main worker loop - checks queue every 30 seconds"""
        while not self.stop_event.is_set():
            try:
                # Get next pending export
                entry = self.queue.get_next_pending()

                if entry:
                    print(f"Processing export: {entry['queue_id']}")
                    self._process_export(entry)

                # Check network connectivity periodically
                if not self._check_network():
                    print("No network connectivity, waiting...")

                # Wait 30 seconds before next check
                self.stop_event.wait(30)

            except Exception as e:
                print(f"Worker error: {e}")
                self.stop_event.wait(60)  # Wait longer on error

    def _check_network(self):
        """Check if network/internet is available"""
        try:
            response = requests.get(
                "https://www.google.com",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False

    def _process_export(self, entry):
        """Upload export to central database"""
        queue_id = entry['queue_id']
        export_file = entry['export_file']

        try:
            # Mark as uploading
            self.queue.mark_uploading(queue_id)

            # Read export file
            export_path = Path(export_file)
            if not export_path.exists():
                raise FileNotFoundError(f"Export file not found: {export_file}")

            with open(export_file, 'r') as f:
                export_data = f.read()

            # Get installation ID from export data
            import json
            export_json = json.loads(export_data)
            installation_id = export_json.get('installation_id', 'unknown')

            # Upload to central database
            print(f"Uploading to {self.central_api_url}/api/v1/data/import")
            response = requests.post(
                f"{self.central_api_url}/api/v1/data/import",
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {installation_id}'
                },
                data=export_data,
                timeout=30
            )

            if response.status_code == 200:
                # Success
                self.queue.mark_success(queue_id)
                print(f"✓ Export uploaded successfully: {queue_id}")
            else:
                # Failed
                error = f"HTTP {response.status_code}: {response.text}"
                self.queue.mark_failed(queue_id, error)
                print(f"✗ Export upload failed: {error}")

        except FileNotFoundError as e:
            # Permanent failure - file missing
            self.queue.mark_failed(queue_id, str(e))
            # Mark as max retries to move to failed immediately
            for _ in range(3):
                self.queue.mark_failed(queue_id, str(e))
            print(f"✗ Export file missing: {e}")

        except Exception as e:
            # Failed - will retry
            self.queue.mark_failed(queue_id, str(e))
            print(f"✗ Export upload error: {e}")


if __name__ == "__main__":
    # Test worker
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
