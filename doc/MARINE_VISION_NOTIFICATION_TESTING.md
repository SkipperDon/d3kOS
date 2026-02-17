# Marine Vision Notification System - Testing Guide

**Date:** February 17, 2026
**Session:** Session-B-Marine-Vision-Notifications
**Phase:** 2.6
**Status:** Ready for Testing ✅

---

## Testing Overview

This document provides comprehensive testing procedures for the Marine Vision Telegram notification system.

## Prerequisites

Before testing, ensure:

- ✅ Raspberry Pi 4B running d3kOS
- ✅ Internet connectivity (WiFi or Ethernet)
- ✅ Telegram app installed on phone
- ✅ notification_manager.py deployed to `/opt/d3kos/services/marine-vision/`
- ✅ d3kos-notifications.service installed and enabled
- ✅ Telegram bot created via @BotFather

---

## Test Suite

### Phase 1: Service Deployment

#### Test 1.1: File Deployment
**Objective:** Verify all files are in correct locations

```bash
# Check service file
ls -l /opt/d3kos/services/marine-vision/notification_manager.py

# Check config file
ls -l /opt/d3kos/config/telegram-config.json

# Check systemd service
ls -l /etc/systemd/system/d3kos-notifications.service

# Check permissions
ls -la /opt/d3kos/services/marine-vision/
ls -la /opt/d3kos/config/
```

**Expected:** All files exist with correct permissions (d3kos:d3kos)

**Status:** ⬜ Pass | ⬜ Fail

---

#### Test 1.2: Python Dependencies
**Objective:** Verify required Python packages installed

```bash
python3 -c "import requests; print('✓ requests')"
python3 -c "import json; print('✓ json')"
python3 -c "import threading; print('✓ threading')"
```

**Expected:** All imports succeed

**Status:** ⬜ Pass | ⬜ Fail

---

#### Test 1.3: Service Start
**Objective:** Verify service starts without errors

```bash
sudo systemctl daemon-reload
sudo systemctl start d3kos-notifications.service
sudo systemctl status d3kos-notifications.service
```

**Expected:**
- Status: `active (running)`
- No error messages in logs

```bash
journalctl -u d3kos-notifications.service -n 20
```

**Expected log output:**
```
✓ Configuration loaded from /opt/d3kos/config/telegram-config.json
✓ Notification worker thread started
✓ Notification API server listening on http://localhost:8088
```

**Status:** ⬜ Pass | ⬜ Fail

---

### Phase 2: API Endpoints

#### Test 2.1: Status Endpoint
**Objective:** Verify status endpoint returns correct data

```bash
curl -s http://localhost:8088/notify/status | jq .
```

**Expected response:**
```json
{
  "service": "notification_manager",
  "version": "1.0",
  "enabled": false,
  "configured": false,
  "queue_size": 0,
  "failed_count": 0
}
```

**Status:** ⬜ Pass | ⬜ Fail

---

#### Test 2.2: Config Endpoint (GET)
**Objective:** Verify configuration retrieval

```bash
curl -s http://localhost:8088/notify/config | jq .
```

**Expected response:**
```json
{
  "enabled": false,
  "bot_token_set": false,
  "chat_id_set": false,
  "retry_attempts": 3,
  "retry_delay": 5
}
```

**Status:** ⬜ Pass | ⬜ Fail

---

### Phase 3: Telegram Bot Setup

#### Test 3.1: Bot Creation
**Objective:** Create Telegram bot via @BotFather

**Steps:**
1. Open Telegram app
2. Search for `@BotFather`
3. Send: `/newbot`
4. Bot name: `d3kOS Fish Notifier`
5. Bot username: `d3kos_fish_<your_initials>_bot`
6. Copy bot token

**Bot Token Format:** `<numbers>:AA<alphanumeric_string>`

**Example:** `110201543:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw`

**Your Bot Token:** ___________________________________

**Status:** ⬜ Pass | ⬜ Fail

---

#### Test 3.2: Get Chat ID
**Objective:** Retrieve your Telegram chat ID

**Steps:**
1. Search for your bot in Telegram
2. Start a chat
3. Send: `/start`

4. Get chat ID:
```bash
# Replace <BOT_TOKEN> with your actual token
curl -s "https://api.telegram.org/bot<BOT_TOKEN>/getUpdates" | jq .
```

5. Look for: `"chat": {"id": 123456789}`

**Your Chat ID:** ___________________________________

**Status:** ⬜ Pass | ⬜ Fail

---

#### Test 3.3: Manual Bot Test
**Objective:** Verify bot responds via Telegram API

```bash
# Replace <BOT_TOKEN> and <CHAT_ID> with your values
curl -X POST "https://api.telegram.org/bot<BOT_TOKEN>/sendMessage" \
  -d "chat_id=<CHAT_ID>" \
  -d "text=Manual test from terminal"
```

**Expected:** Message appears in your Telegram chat

**Status:** ⬜ Pass | ⬜ Fail

---

### Phase 4: Configuration

#### Test 4.1: Update Configuration via API
**Objective:** Configure bot via HTTP API

```bash
# Replace <BOT_TOKEN> and <CHAT_ID> with your values
curl -X POST http://localhost:8088/notify/config \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "bot_token": "<BOT_TOKEN>",
    "chat_id": "<CHAT_ID>"
  }'
```

**Expected response:**
```json
{
  "success": true,
  "message": "Configuration updated"
}
```

**Status:** ⬜ Pass | ⬜ Fail

---

#### Test 4.2: Verify Configuration Saved
**Objective:** Confirm configuration persisted to file

```bash
cat /opt/d3kos/config/telegram-config.json
```

**Expected:**
- `"enabled": true`
- `"bot_token"` contains your token
- `"chat_id"` contains your chat ID

**Status:** ⬜ Pass | ⬜ Fail

---

#### Test 4.3: Service Restart
**Objective:** Verify configuration loads after restart

```bash
sudo systemctl restart d3kos-notifications.service
sleep 3
curl -s http://localhost:8088/notify/status | jq .
```

**Expected:**
```json
{
  "enabled": true,
  "configured": true,
  ...
}
```

**Expected log message:**
```bash
journalctl -u d3kos-notifications.service -n 10 | grep "Telegram bot configured"
```

**Status:** ⬜ Pass | ⬜ Fail

---

### Phase 5: Notification Sending

#### Test 5.1: Test Notification
**Objective:** Send test notification via API

```bash
curl -X POST http://localhost:8088/notify/test
```

**Expected:**
- API response: `{"success": true, "message": "Test notification sent"}`
- Telegram message received within 5 seconds
- Message format:
  ```
  🧪 Test Notification

  This is a test from d3kOS Marine Vision System.

  ⏰ Time: 2026-02-17 10:30:00
  ```

**Delivery Time:** _______ seconds

**Status:** ⬜ Pass | ⬜ Fail

---

#### Test 5.2: Text Notification
**Objective:** Send custom text notification

```bash
curl -X POST http://localhost:8088/notify/send \
  -H "Content-Type: application/json" \
  -d '{
    "type": "text",
    "message": "Custom test message from API"
  }'
```

**Expected:**
- API response: `{"success": true, "message": "Notification queued"}`
- Telegram message received
- Message text: "Custom test message from API"

**Status:** ⬜ Pass | ⬜ Fail

---

#### Test 5.3: Fish Capture Notification (No Photo)
**Objective:** Send fish capture notification without photo

```bash
curl -X POST http://localhost:8088/notify/send \
  -H "Content-Type: application/json" \
  -d '{
    "type": "fish_capture",
    "capture_data": {
      "capture_id": "test_12345",
      "timestamp": "2026-02-17T10:30:00Z",
      "species": "Largemouth Bass",
      "species_confidence": 0.89,
      "gps": {
        "latitude": 44.4167,
        "longitude": -79.3333
      },
      "regulations": {
        "legal": true,
        "size_limit": "12 inches minimum",
        "bag_limit": "6 per day",
        "season": "Open year-round"
      }
    }
  }'
```

**Expected Telegram message:**
```
🎣 Fish Capture Detected!

📸 Capture ID: test_12345
⏰ Time: 2026-02-17T10:30:00Z

🐟 Species: Largemouth Bass
📊 Confidence: 89.0%

📍 Location: 44.416700, -79.333300
🗺️ View on Map (link)

📋 Regulations:
✅ Legal to keep
📏 Size limit: 12 inches minimum
🎒 Bag limit: 6 per day
📅 Season: Open year-round
```

**Status:** ⬜ Pass | ⬜ Fail

---

#### Test 5.4: Fish Capture with Photo
**Objective:** Send notification with photo attachment

**Prerequisites:**
- Test photo at `/home/d3kos/camera-recordings/captures/test.jpg`
- Or use any existing photo

```bash
# Create test photo if needed
curl http://localhost:8084/camera/frame -o /tmp/test_fish.jpg

# Send notification
curl -X POST http://localhost:8088/notify/send \
  -H "Content-Type: application/json" \
  -d '{
    "type": "fish_capture",
    "photo_path": "/tmp/test_fish.jpg",
    "capture_data": {
      "capture_id": "test_photo_001",
      "timestamp": "2026-02-17T10:45:00Z",
      "species": "Northern Pike",
      "species_confidence": 0.92,
      "gps": {
        "latitude": 44.4200,
        "longitude": -79.3400
      }
    }
  }'
```

**Expected:**
- Telegram message with photo
- Photo displays correctly
- Caption includes all fish data
- Delivery time < 10 seconds

**Delivery Time:** _______ seconds

**Status:** ⬜ Pass | ⬜ Fail

---

### Phase 6: Error Handling

#### Test 6.1: Invalid Bot Token
**Objective:** Verify graceful handling of invalid token

```bash
# Save current config
cp /opt/d3kos/config/telegram-config.json /tmp/telegram-config.backup

# Set invalid token
curl -X POST http://localhost:8088/notify/config \
  -H "Content-Type: application/json" \
  -d '{
    "bot_token": "invalid_token_12345"
  }'

# Try test notification
curl -X POST http://localhost:8088/notify/test
```

**Expected:**
- API returns error or success: false
- Log shows: "Telegram API error"
- Service continues running (doesn't crash)

```bash
journalctl -u d3kos-notifications.service -n 5
```

**Restore config:**
```bash
cp /tmp/telegram-config.backup /opt/d3kos/config/telegram-config.json
sudo systemctl restart d3kos-notifications.service
```

**Status:** ⬜ Pass | ⬜ Fail

---

#### Test 6.2: Network Failure
**Objective:** Verify retry logic on network failure

```bash
# Block Telegram API temporarily
sudo iptables -A OUTPUT -d api.telegram.org -j DROP

# Send notification
curl -X POST http://localhost:8088/notify/test

# Watch logs for retries
journalctl -u d3kos-notifications.service -f
```

**Expected:**
- Log shows: "⟳ Retrying notification (attempt 1/3)"
- After 3 attempts: "✗ Notification failed after 3 attempts"
- Failed notification saved to queue

**Verify failed queue:**
```bash
curl -s http://localhost:8088/notify/failed | jq .
```

**Restore network:**
```bash
sudo iptables -D OUTPUT -d api.telegram.org -j DROP
```

**Status:** ⬜ Pass | ⬜ Fail

---

#### Test 6.3: Missing Photo File
**Objective:** Verify handling of non-existent photo

```bash
curl -X POST http://localhost:8088/notify/send \
  -H "Content-Type: application/json" \
  -d '{
    "type": "fish_capture",
    "photo_path": "/nonexistent/path/photo.jpg",
    "capture_data": {
      "capture_id": "test_no_photo",
      "timestamp": "2026-02-17T11:00:00Z"
    }
  }'
```

**Expected:**
- Notification sent WITHOUT photo
- Text message delivered successfully
- Log shows: "Photo file not found" or similar

**Status:** ⬜ Pass | ⬜ Fail

---

### Phase 7: Performance Testing

#### Test 7.1: Notification Latency
**Objective:** Measure end-to-end notification delivery time

```bash
# Send 5 test notifications and measure time
for i in {1..5}; do
  START=$(date +%s.%N)
  curl -X POST http://localhost:8088/notify/test
  # Check Telegram for message receipt time
  echo "Notification $i sent at $(date)"
  sleep 2
done
```

**Record times:**
1. _______ seconds
2. _______ seconds
3. _______ seconds
4. _______ seconds
5. _______ seconds

**Average:** _______ seconds

**Target:** < 5 seconds

**Status:** ⬜ Pass | ⬜ Fail

---

#### Test 7.2: Photo Upload Performance
**Objective:** Measure photo notification delivery time

```bash
# Test with different photo sizes
curl http://localhost:8084/camera/frame -o /tmp/test_photo.jpg

# Check file size
ls -lh /tmp/test_photo.jpg

# Time the notification
time curl -X POST http://localhost:8088/notify/send \
  -H "Content-Type: application/json" \
  -d "{
    \"type\": \"fish_capture\",
    \"photo_path\": \"/tmp/test_photo.jpg\",
    \"capture_data\": {
      \"capture_id\": \"perf_test_$(date +%s)\"
    }
  }"
```

**Photo size:** _______ KB
**Upload time:** _______ seconds

**Target:** < 10 seconds

**Status:** ⬜ Pass | ⬜ Fail

---

#### Test 7.3: Queue Processing
**Objective:** Verify multiple notifications processed correctly

```bash
# Send 10 notifications rapidly
for i in {1..10}; do
  curl -X POST http://localhost:8088/notify/send \
    -H "Content-Type: application/json" \
    -d "{\"type\": \"text\", \"message\": \"Bulk test $i\"}" &
done
wait

# Check queue status
curl -s http://localhost:8088/notify/status | jq .queue_size
```

**Expected:**
- All 10 notifications received on Telegram
- Queue processed to 0
- No failed notifications

**Status:** ⬜ Pass | ⬜ Fail

---

### Phase 8: Integration Testing

#### Test 8.1: End-to-End with Fish Detector
**Objective:** Verify integration with fish detector service

**Prerequisites:**
- d3kos-fish-detector.service running
- Camera operational

**Steps:**
1. Update fish_detector.py with notification integration (see integration guide)
2. Restart fish detector: `sudo systemctl restart d3kos-fish-detector.service`
3. Trigger fish capture (hold object in front of camera)
4. Wait for detection

**Expected:**
- Fish capture triggered
- Notification sent automatically
- Telegram message received with photo

**Status:** ⬜ Pass | ⬜ Fail

---

#### Test 8.2: GPS Integration
**Objective:** Verify GPS coordinates included in notifications

```bash
# Check Signal K GPS data
curl -s http://localhost:3000/signalk/v1/api/vessels/self/navigation/position | jq .

# Send notification with GPS
# (See integration guide for fish_detector.py GPS integration)
```

**Expected:**
- GPS coordinates in notification message
- Google Maps link functional
- Coordinates accurate

**Status:** ⬜ Pass | ⬜ Fail

---

### Phase 9: Nginx Proxy (Optional)

#### Test 9.1: Add Nginx Configuration
**Objective:** Make API accessible from network

```bash
# Add to /etc/nginx/sites-enabled/default
sudo nano /etc/nginx/sites-enabled/default

# Add location block (see integration guide)
# Test nginx config
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

**Status:** ⬜ Pass | ⬜ Fail

---

#### Test 9.2: Network Access
**Objective:** Access notification API from another device

```bash
# From another computer on network
curl http://192.168.1.237/notify/status
```

**Expected:** Status response received

**Status:** ⬜ Pass | ⬜ Fail

---

## Test Results Summary

| Phase | Tests | Passed | Failed | Notes |
|-------|-------|--------|--------|-------|
| 1. Deployment | 3 | | | |
| 2. API Endpoints | 2 | | | |
| 3. Bot Setup | 3 | | | |
| 4. Configuration | 3 | | | |
| 5. Notifications | 4 | | | |
| 6. Error Handling | 3 | | | |
| 7. Performance | 3 | | | |
| 8. Integration | 2 | | | |
| 9. Nginx Proxy | 2 | | | |
| **TOTAL** | **25** | | | |

## Acceptance Criteria

✅ **Must Pass:**
- [ ] Service starts without errors
- [ ] Status API returns correct data
- [ ] Bot configuration successful
- [ ] Test notification delivered < 5 seconds
- [ ] Photo notification delivered < 10 seconds
- [ ] Retry logic handles network failures
- [ ] Queue processes all notifications

⭐ **Nice to Have:**
- [ ] GPS coordinates in notifications
- [ ] Integration with fish detector
- [ ] Nginx proxy configured
- [ ] Multiple rapid notifications handled

## Sign-Off

**Tester Name:** _______________________________

**Date:** _______________________________

**Overall Status:** ⬜ PASS | ⬜ FAIL | ⬜ PARTIAL

**Notes:**
_______________________________________________________________
_______________________________________________________________
_______________________________________________________________

---

**Testing Complete!** 🎉

If all tests pass, the notification system is ready for production use.
