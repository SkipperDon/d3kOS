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
Export Queue Management
Handles queue operations, retry logic, and status tracking

Author: d3kOS Team
Date: 2026-02-20
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

QUEUE_FILE = "/opt/d3kos/data/exports/export_queue.json"
HISTORY_FILE = "/opt/d3kos/data/exports/export_history.json"
FAILED_DIR = "/opt/d3kos/data/exports/failed_exports"

class ExportQueue:
    def __init__(self):
        self.queue_file = Path(QUEUE_FILE)
        self.history_file = Path(HISTORY_FILE)
        self.failed_dir = Path(FAILED_DIR)
        self._ensure_files()

    def _ensure_files(self):
        """Create queue files and directories if they don't exist"""
        self.queue_file.parent.mkdir(parents=True, exist_ok=True)
        self.failed_dir.mkdir(parents=True, exist_ok=True)

        if not self.queue_file.exists():
            self._write_queue({
                "version": "1.0",
                "last_updated": datetime.utcnow().isoformat() + "Z",
                "pending": [],
                "uploading": [],
                "completed": [],
                "failed": []
            })

        if not self.history_file.exists():
            self._write_history({
                "version": "1.0",
                "exports": []
            })

    def _read_queue(self):
        """Read queue file"""
        try:
            with open(self.queue_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading queue: {e}")
            return self._get_empty_queue()

    def _write_queue(self, data):
        """Write queue file"""
        data['last_updated'] = datetime.utcnow().isoformat() + "Z"
        with open(self.queue_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _get_empty_queue(self):
        return {
            "version": "1.0",
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "pending": [],
            "uploading": [],
            "completed": [],
            "failed": []
        }

    def add_export(self, export_file, tier, category_count):
        """Add export to queue"""
        queue = self._read_queue()

        # Generate queue ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        queue_id = f"q_{timestamp}"

        # Get file size
        file_size = os.path.getsize(export_file) if os.path.exists(export_file) else 0

        # Create queue entry
        entry = {
            "queue_id": queue_id,
            "export_file": str(export_file),
            "created_at": datetime.utcnow().isoformat() + "Z",
            "tier": tier,
            "category_count": category_count,
            "file_size_bytes": file_size,
            "status": "pending",
            "retry_count": 0,
            "next_retry_at": datetime.utcnow().isoformat() + "Z",
            "last_error": None
        }

        queue['pending'].append(entry)
        self._write_queue(queue)

        print(f"Added to queue: {queue_id} ({file_size} bytes, {category_count} categories)")
        return queue_id

    def get_next_pending(self):
        """Get next pending export ready for upload"""
        queue = self._read_queue()

        for entry in queue['pending']:
            # Check if ready for retry
            next_retry = datetime.fromisoformat(entry['next_retry_at'].replace('Z', '+00:00'))
            now = datetime.now(next_retry.tzinfo) if next_retry.tzinfo else datetime.utcnow()
            if now >= next_retry:
                return entry

        return None

    def mark_uploading(self, queue_id):
        """Mark export as currently uploading"""
        queue = self._read_queue()

        # Find in pending
        for i, entry in enumerate(queue['pending']):
            if entry['queue_id'] == queue_id:
                entry['status'] = 'uploading'
                queue['uploading'].append(entry)
                del queue['pending'][i]
                self._write_queue(queue)
                return True

        return False

    def mark_success(self, queue_id):
        """Mark export as successfully uploaded"""
        queue = self._read_queue()

        # Find in uploading
        for i, entry in enumerate(queue['uploading']):
            if entry['queue_id'] == queue_id:
                entry['status'] = 'completed'
                entry['completed_at'] = datetime.utcnow().isoformat() + "Z"
                queue['completed'].append(entry)
                del queue['uploading'][i]
                self._write_queue(queue)

                # Add to history
                self._add_to_history(entry)
                return True

        return False

    def mark_failed(self, queue_id, error_message):
        """Mark export as failed (retry or permanent failure)"""
        queue = self._read_queue()

        # Find in uploading
        for i, entry in enumerate(queue['uploading']):
            if entry['queue_id'] == queue_id:
                entry['retry_count'] += 1
                entry['last_error'] = error_message

                # Retry schedule: immediate, 5min, 15min, then fail
                if entry['retry_count'] == 1:
                    # First retry: immediate (set to now)
                    entry['next_retry_at'] = datetime.utcnow().isoformat() + "Z"
                    entry['status'] = 'pending'
                    queue['pending'].append(entry)
                elif entry['retry_count'] == 2:
                    # Second retry: 5 minutes
                    entry['next_retry_at'] = (datetime.utcnow() + timedelta(minutes=5)).isoformat() + "Z"
                    entry['status'] = 'pending'
                    queue['pending'].append(entry)
                elif entry['retry_count'] == 3:
                    # Third retry: 15 minutes
                    entry['next_retry_at'] = (datetime.utcnow() + timedelta(minutes=15)).isoformat() + "Z"
                    entry['status'] = 'pending'
                    queue['pending'].append(entry)
                else:
                    # Permanent failure after 3 retries
                    entry['status'] = 'failed'
                    entry['failed_at'] = datetime.utcnow().isoformat() + "Z"
                    queue['failed'].append(entry)

                    # Archive failed export
                    self._archive_failed_export(entry)

                del queue['uploading'][i]
                self._write_queue(queue)
                return True

        return False

    def _add_to_history(self, entry):
        """Add completed export to history"""
        try:
            if self.history_file.exists():
                history = json.loads(self.history_file.read_text())
            else:
                history = {"version": "1.0", "exports": []}

            history['exports'].append(entry)
            self.history_file.write_text(json.dumps(history, indent=2))
        except Exception as e:
            print(f"Error adding to history: {e}")

    def _archive_failed_export(self, entry):
        """Archive failed export file"""
        try:
            export_file = Path(entry['export_file'])
            if export_file.exists():
                archive_name = f"{entry['queue_id']}_failed.json"
                archive_path = self.failed_dir / archive_name
                export_file.rename(archive_path)
                print(f"Archived failed export: {archive_path}")
        except Exception as e:
            print(f"Error archiving failed export: {e}")

    def get_queue_status(self):
        """Get queue status summary"""
        queue = self._read_queue()

        return {
            "pending_count": len(queue['pending']),
            "uploading_count": len(queue['uploading']),
            "completed_count": len(queue['completed']),
            "failed_count": len(queue['failed']),
            "next_pending": queue['pending'][0] if queue['pending'] else None,
            "last_updated": queue['last_updated']
        }

    def cleanup_old_completed(self, days=30):
        """Remove completed exports older than X days"""
        queue = self._read_queue()
        cutoff = datetime.utcnow() - timedelta(days=days)

        # Filter completed
        original_count = len(queue['completed'])
        queue['completed'] = [
            entry for entry in queue['completed']
            if datetime.fromisoformat(entry['completed_at'].replace('Z', '+00:00')).replace(tzinfo=None) > cutoff
        ]

        removed = original_count - len(queue['completed'])
        if removed > 0:
            self._write_queue(queue)
            print(f"Cleaned up {removed} completed exports older than {days} days")

    def cleanup_old_failed(self, days=7):
        """Remove failed exports older than X days"""
        queue = self._read_queue()
        cutoff = datetime.utcnow() - timedelta(days=days)

        # Filter failed
        original_count = len(queue['failed'])
        queue['failed'] = [
            entry for entry in queue['failed']
            if datetime.fromisoformat(entry['failed_at'].replace('Z', '+00:00')).replace(tzinfo=None) > cutoff
        ]

        removed = original_count - len(queue['failed'])
        if removed > 0:
            self._write_queue(queue)
            print(f"Cleaned up {removed} failed exports older than {days} days")

    def _write_history(self, data):
        """Write history file"""
        with open(self.history_file, 'w') as f:
            json.dump(data, f, indent=2)


if __name__ == "__main__":
    # Test queue operations
    print("Testing Export Queue...")

    queue = ExportQueue()

    # Test add
    queue_id = queue.add_export("/tmp/test_export.json", 2, 9)
    print(f"Added: {queue_id}")

    # Test status
    status = queue.get_queue_status()
    print(f"Status: {status}")

    # Test get next
    next_entry = queue.get_next_pending()
    print(f"Next pending: {next_entry}")

    print("Export Queue test complete")
