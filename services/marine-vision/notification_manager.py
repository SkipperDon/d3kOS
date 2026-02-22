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
Marine Vision Notification Manager
Handles Telegram bot notifications for fish captures and marine vision events

Author: d3kOS Team
Date: February 17, 2026
Version: 1.0
"""

import os
import json
import time
import logging
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import threading
from queue import Queue, Empty
from datetime import datetime

# Configuration
CONFIG_FILE = os.getenv('TELEGRAM_CONFIG', '/opt/d3kos/config/telegram-config.json')
NOTIFICATION_QUEUE_FILE = '/opt/d3kos/data/marine-vision/notification_queue.json'
PORT = 8088

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('notification_manager')

# Global configuration
config = {
    'enabled': False,
    'bot_token': '',
    'chat_id': '',
    'retry_attempts': 3,
    'retry_delay': 5
}

# Notification queue
notification_queue = Queue()
failed_notifications = []


def load_config():
    """Load Telegram configuration from file"""
    global config

    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                loaded = json.load(f)
                config.update(loaded)
                logger.info(f"✓ Configuration loaded from {CONFIG_FILE}")

                if config.get('enabled') and config.get('bot_token') and config.get('chat_id'):
                    logger.info("✓ Telegram bot configured and enabled")
                else:
                    logger.warning("⚠ Telegram bot not fully configured")
        else:
            logger.warning(f"⚠ Configuration file not found: {CONFIG_FILE}")
            # Create default config
            save_config()
    except Exception as e:
        logger.error(f"✗ Failed to load configuration: {e}")


def save_config():
    """Save current configuration to file"""
    try:
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"✓ Configuration saved to {CONFIG_FILE}")
    except Exception as e:
        logger.error(f"✗ Failed to save configuration: {e}")


def send_telegram_message(text, photo_path=None):
    """
    Send a Telegram message with optional photo

    Args:
        text: Message text
        photo_path: Optional path to photo file

    Returns:
        bool: True if successful, False otherwise
    """
    if not config.get('enabled'):
        logger.info("⚠ Telegram notifications disabled")
        return False

    if not config.get('bot_token') or not config.get('chat_id'):
        logger.error("✗ Telegram bot token or chat ID not configured")
        return False

    bot_token = config['bot_token']
    chat_id = config['chat_id']

    try:
        if photo_path and os.path.exists(photo_path):
            # Send photo with caption
            url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"

            with open(photo_path, 'rb') as photo:
                files = {'photo': photo}
                data = {
                    'chat_id': chat_id,
                    'caption': text,
                    'parse_mode': 'Markdown'
                }

                response = requests.post(url, data=data, files=files, timeout=30)

        else:
            # Send text only
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'Markdown'
            }

            response = requests.post(url, data=data, timeout=30)

        if response.status_code == 200:
            logger.info(f"✓ Telegram notification sent successfully")
            return True
        else:
            logger.error(f"✗ Telegram API error: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        logger.error(f"✗ Failed to send Telegram message: {e}")
        return False


def format_fish_capture_message(capture_data):
    """
    Format fish capture data into Telegram message

    Args:
        capture_data: Dict with capture information

    Returns:
        str: Formatted message text
    """
    message_parts = ["🎣 *Fish Capture Detected!*\n"]

    # Capture ID and timestamp
    capture_id = capture_data.get('capture_id', 'unknown')
    timestamp = capture_data.get('timestamp', datetime.now().isoformat())
    message_parts.append(f"📸 Capture ID: `{capture_id}`")
    message_parts.append(f"⏰ Time: {timestamp}\n")

    # Species information
    species = capture_data.get('species')
    if species:
        confidence = capture_data.get('species_confidence', 0)
        message_parts.append(f"🐟 Species: *{species}*")
        message_parts.append(f"📊 Confidence: {confidence:.1%}\n")
    else:
        message_parts.append("🐟 Species: *Unknown* (identification pending)\n")

    # GPS coordinates
    gps = capture_data.get('gps')
    if gps and gps.get('latitude') and gps.get('longitude'):
        lat = gps['latitude']
        lon = gps['longitude']
        message_parts.append(f"📍 Location: {lat:.6f}, {lon:.6f}")
        # Add Google Maps link
        maps_url = f"https://maps.google.com/?q={lat},{lon}"
        message_parts.append(f"🗺️ [View on Map]({maps_url})\n")

    # Fishing regulations
    regulations = capture_data.get('regulations')
    if regulations:
        message_parts.append("📋 *Regulations:*")

        if regulations.get('legal'):
            message_parts.append("✅ Legal to keep")
        else:
            message_parts.append("⚠️ *Check regulations!*")

        if regulations.get('size_limit'):
            message_parts.append(f"📏 Size limit: {regulations['size_limit']}")

        if regulations.get('bag_limit'):
            message_parts.append(f"🎒 Bag limit: {regulations['bag_limit']}")

        if regulations.get('season'):
            message_parts.append(f"📅 Season: {regulations['season']}")

    return "\n".join(message_parts)


def notification_worker():
    """Background worker to process notification queue"""
    logger.info("✓ Notification worker started")

    while True:
        try:
            # Get notification from queue (blocking with 1 second timeout)
            notification = notification_queue.get(timeout=1)

            # Extract data
            notification_type = notification.get('type', 'text')
            message = notification.get('message', '')
            photo_path = notification.get('photo_path')
            retry_count = notification.get('retry_count', 0)

            # Send notification
            success = send_telegram_message(message, photo_path)

            if not success:
                # Retry logic
                if retry_count < config.get('retry_attempts', 3):
                    retry_count += 1
                    logger.info(f"⟳ Retrying notification (attempt {retry_count}/{config['retry_attempts']})")

                    # Add back to queue with delay
                    time.sleep(config.get('retry_delay', 5))
                    notification['retry_count'] = retry_count
                    notification_queue.put(notification)
                else:
                    # Max retries reached, save to failed queue
                    logger.error(f"✗ Notification failed after {retry_count} attempts")
                    failed_notifications.append({
                        'notification': notification,
                        'failed_at': datetime.now().isoformat()
                    })
                    save_failed_notifications()

            notification_queue.task_done()

        except Empty:
            # No notifications in queue, continue
            continue
        except Exception as e:
            logger.error(f"✗ Notification worker error: {e}")


def save_failed_notifications():
    """Save failed notifications to disk"""
    try:
        os.makedirs(os.path.dirname(NOTIFICATION_QUEUE_FILE), exist_ok=True)
        with open(NOTIFICATION_QUEUE_FILE, 'w') as f:
            json.dump(failed_notifications, f, indent=2)
    except Exception as e:
        logger.error(f"✗ Failed to save notification queue: {e}")


class NotificationAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for notification API"""

    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(f"{self.address_string()} - {format % args}")

    def _set_headers(self, status=200, content_type='application/json'):
        """Set common response headers"""
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def _send_json(self, data, status=200):
        """Send JSON response"""
        self._set_headers(status)
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        """Handle GET requests"""
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/notify/status':
            self.handle_status()
        elif path == '/notify/config':
            self.handle_get_config()
        elif path == '/notify/failed':
            self.handle_failed_notifications()
        else:
            self._send_json({'error': 'Not found'}, 404)

    def do_POST(self):
        """Handle POST requests"""
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/notify/send':
            self.handle_send_notification()
        elif path == '/notify/config':
            self.handle_update_config()
        elif path == '/notify/test':
            self.handle_test_notification()
        else:
            self._send_json({'error': 'Not found'}, 404)

    def handle_status(self):
        """Return service status"""
        self._send_json({
            'service': 'notification_manager',
            'version': '1.0',
            'enabled': config.get('enabled', False),
            'configured': bool(config.get('bot_token') and config.get('chat_id')),
            'queue_size': notification_queue.qsize(),
            'failed_count': len(failed_notifications)
        })

    def handle_get_config(self):
        """Return current configuration (without sensitive data)"""
        safe_config = {
            'enabled': config.get('enabled', False),
            'bot_token_set': bool(config.get('bot_token')),
            'chat_id_set': bool(config.get('chat_id')),
            'retry_attempts': config.get('retry_attempts', 3),
            'retry_delay': config.get('retry_delay', 5)
        }
        self._send_json(safe_config)

    def handle_update_config(self):
        """Update configuration"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())

            # Update config
            if 'enabled' in data:
                config['enabled'] = bool(data['enabled'])
            if 'bot_token' in data:
                config['bot_token'] = data['bot_token']
            if 'chat_id' in data:
                config['chat_id'] = data['chat_id']
            if 'retry_attempts' in data:
                config['retry_attempts'] = int(data['retry_attempts'])
            if 'retry_delay' in data:
                config['retry_delay'] = int(data['retry_delay'])

            # Save to file
            save_config()

            self._send_json({'success': True, 'message': 'Configuration updated'})

        except Exception as e:
            logger.error(f"✗ Failed to update configuration: {e}")
            self._send_json({'error': str(e)}, 400)

    def handle_send_notification(self):
        """Send a notification"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())

            # Validate required fields
            if 'message' not in data:
                self._send_json({'error': 'Missing required field: message'}, 400)
                return

            # Format message if it's a fish capture
            if data.get('type') == 'fish_capture':
                message = format_fish_capture_message(data.get('capture_data', {}))
            else:
                message = data['message']

            # Add to queue
            notification = {
                'type': data.get('type', 'text'),
                'message': message,
                'photo_path': data.get('photo_path'),
                'retry_count': 0
            }

            notification_queue.put(notification)

            self._send_json({
                'success': True,
                'message': 'Notification queued',
                'queue_size': notification_queue.qsize()
            })

        except Exception as e:
            logger.error(f"✗ Failed to queue notification: {e}")
            self._send_json({'error': str(e)}, 400)

    def handle_test_notification(self):
        """Send a test notification"""
        try:
            test_message = f"🧪 *Test Notification*\n\nThis is a test from d3kOS Marine Vision System.\n\n⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            success = send_telegram_message(test_message)

            if success:
                self._send_json({'success': True, 'message': 'Test notification sent'})
            else:
                self._send_json({'error': 'Failed to send test notification'}, 500)

        except Exception as e:
            logger.error(f"✗ Test notification failed: {e}")
            self._send_json({'error': str(e)}, 500)

    def handle_failed_notifications(self):
        """Return list of failed notifications"""
        self._send_json({
            'failed_notifications': failed_notifications,
            'count': len(failed_notifications)
        })


def main():
    """Main entry point"""
    logger.info("=" * 60)
    logger.info("d3kOS Marine Vision Notification Manager")
    logger.info("Version 1.0 - February 17, 2026")
    logger.info("=" * 60)

    # Load configuration
    load_config()

    # Start notification worker thread
    worker_thread = threading.Thread(target=notification_worker, daemon=True)
    worker_thread.start()
    logger.info("✓ Notification worker thread started")

    # Start HTTP server
    server = HTTPServer(('localhost', PORT), NotificationAPIHandler)
    logger.info(f"✓ Notification API server listening on http://localhost:{PORT}")
    logger.info("✓ Endpoints:")
    logger.info(f"   GET  /notify/status - Service status")
    logger.info(f"   GET  /notify/config - Get configuration")
    logger.info(f"   POST /notify/config - Update configuration")
    logger.info(f"   POST /notify/send - Send notification")
    logger.info(f"   POST /notify/test - Send test notification")
    logger.info(f"   GET  /notify/failed - List failed notifications")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("\n⚠ Shutting down...")
        server.shutdown()


if __name__ == '__main__':
    main()
