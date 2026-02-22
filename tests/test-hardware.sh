#!/bin/bash
# d3kOS - Marine Intelligence Operating System
# Copyright (C) 2026 Donald Moskaluk / AtMyBoat.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# For commercial licensing contact: skipperdon@atmyboat.com

# test-hardware.sh - d3kOS Hardware Device Validation
# Part of Distribution Prep Session 3: Testing & QA
# Tests CAN interface, GPS, touchscreen, audio devices, camera, and SD card

set -e

# Test configuration
SCRIPT_NAME="Hardware Device Validation"
TESTS_PASSED=0
TESTS_FAILED=0
WARNINGS=0

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Output functions
print_header() {
    echo ""
    echo "========================================="
    echo "$SCRIPT_NAME"
    echo "========================================="
    echo ""
}

test_pass() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
    ((TESTS_PASSED++))
}

test_fail() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    echo -e "  ${RED}Reason${NC}: $2"
    ((TESTS_FAILED++))
}

test_warn() {
    echo -e "${YELLOW}⚠ WARN${NC}: $1"
    echo -e "  ${YELLOW}Info${NC}: $2"
    ((WARNINGS++))
}

print_header

# Test 1: CAN0 Interface (NMEA2000)
echo "Test 1: CAN0 interface validation"
if ip link show can0 &> /dev/null; then
    # Check if interface is up
    if ip link show can0 | grep -q "UP"; then
        test_pass "CAN0 interface is up"

        # Check bitrate (should be 250000 for NMEA2000)
        bitrate=$(ip -details link show can0 | grep -oP 'bitrate \K\d+' || echo "0")
        if [ "$bitrate" = "250000" ]; then
            test_pass "CAN0 bitrate is 250000 (NMEA2000 standard)"
        else
            test_fail "CAN0 bitrate is $bitrate" "Expected 250000 for NMEA2000"
        fi
    else
        test_fail "CAN0 interface exists but is DOWN" "May need: sudo ip link set can0 up type can bitrate 250000"
    fi
else
    test_fail "CAN0 interface not found" "Check if MCP2515 CAN hat is connected and configured"
fi

# Test 2: GPS Device
echo ""
echo "Test 2: GPS device validation"
if [ -e "/dev/ttyACM0" ]; then
    test_pass "GPS device /dev/ttyACM0 exists"

    # Check if gpsd is configured
    if grep -q "/dev/ttyACM0" /etc/default/gpsd 2>/dev/null; then
        test_pass "gpsd configured for /dev/ttyACM0"
    else
        test_warn "gpsd not configured for GPS device" "Check /etc/default/gpsd"
    fi

    # Check if gpsd is running
    if systemctl is-active --quiet gpsd; then
        test_pass "gpsd service is running"
    else
        test_warn "gpsd service not running" "GPS data may not be available"
    fi
else
    test_warn "GPS device /dev/ttyACM0 not found" "GPS may not be connected or using different port"
fi

# Test 3: Touchscreen Device
echo ""
echo "Test 3: Touchscreen device validation"
# Check for ILITEK touchscreen (USB ID 222a:0001)
if lsusb | grep -iq "222a:0001\|ILITEK"; then
    test_pass "ILITEK touchscreen detected via USB"

    # Check for input device
    if ls /dev/input/event* &> /dev/null; then
        touchscreen_count=$(ls /dev/input/event* | wc -l)
        test_pass "Input event devices found: $touchscreen_count"
    else
        test_fail "No input event devices found" "Touchscreen driver may not be loaded"
    fi

    # Check if user is in input group
    if groups | grep -q "input"; then
        test_pass "Current user is in 'input' group"
    else
        test_warn "Current user not in 'input' group" "May have permission issues with touchscreen"
    fi
else
    test_warn "ILITEK touchscreen not detected" "Touchscreen may not be connected"
fi

# Test 4: Audio Devices (Microphone & Speaker)
echo ""
echo "Test 4: Audio device validation"
# Check for Anker S330 speaker (card 3 typically)
if arecord -l 2>/dev/null | grep -iq "S330\|Anker"; then
    test_pass "Anker S330 speaker/microphone detected"

    # Get card number
    card_num=$(arecord -l | grep -i "S330\|Anker" | grep -oP 'card \K\d+' | head -1)
    test_pass "Audio device is card $card_num"

    # Test microphone recording capability
    if arecord -D plughw:$card_num,0 -d 1 -f S16_LE -r 16000 /tmp/test_audio.wav &>/dev/null; then
        test_pass "Microphone recording test successful"
        rm -f /tmp/test_audio.wav
    else
        test_warn "Microphone recording test failed" "Device may be in use or misconfigured"
    fi
else
    test_warn "Anker S330 audio device not detected" "Voice assistant may not work"
fi

# Test 5: Camera Network (Reolink RLC-810A)
echo ""
echo "Test 5: Camera network connectivity"
CAMERA_IP="10.42.0.100"

# Check if eth0 shared network is configured (10.42.0.0/24)
if ip addr show eth0 2>/dev/null | grep -q "10.42.0"; then
    test_pass "Ethernet shared network configured (10.42.0.0/24)"

    # Try to ping camera
    if ping -c 1 -W 2 "$CAMERA_IP" &> /dev/null; then
        test_pass "Camera at $CAMERA_IP is reachable"

        # Try to connect to RTSP port
        if timeout 2 bash -c "echo > /dev/tcp/$CAMERA_IP/554" 2>/dev/null; then
            test_pass "Camera RTSP port 554 is open"
        else
            test_warn "Camera RTSP port 554 not responding" "Camera may not have RTSP enabled"
        fi
    else
        test_warn "Camera at $CAMERA_IP not reachable" "Camera may be powered off or IP changed"
    fi
else
    test_warn "Ethernet shared network not configured" "Camera network may not be set up"
fi

# Test 6: SD Card Storage
echo ""
echo "Test 6: SD card storage validation"
# Get SD card mount point (usually / or /boot)
sd_mount=$(df / | tail -1 | awk '{print $1}')
sd_usage=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
sd_avail=$(df -h / | tail -1 | awk '{print $4}')

test_pass "SD card mounted at /"
test_pass "SD card usage: ${sd_usage}% (${sd_avail} available)"

if [ "$sd_usage" -gt 95 ]; then
    test_fail "SD card is ${sd_usage}% full" "Less than 5% free space remaining"
elif [ "$sd_usage" -gt 85 ]; then
    test_warn "SD card is ${sd_usage}% full" "Consider cleaning up old files"
else
    test_pass "SD card has adequate free space (${sd_usage}% used)"
fi

# Test 7: SD Card Speed Test
echo ""
echo "Test 7: SD card performance test"
# Write 10MB test file and measure speed
if command -v dd &> /dev/null; then
    write_speed=$(dd if=/dev/zero of=/tmp/test_sd_write bs=1M count=10 oflag=direct 2>&1 | grep -oP '\d+(\.\d+)? MB/s' | head -1 || echo "0 MB/s")
    rm -f /tmp/test_sd_write

    # Extract numeric value
    speed_value=$(echo "$write_speed" | grep -oP '[\d.]+' || echo "0")

    if (( $(echo "$speed_value > 5" | bc -l) )); then
        test_pass "SD card write speed: $write_speed (good)"
    elif (( $(echo "$speed_value > 2" | bc -l) )); then
        test_warn "SD card write speed: $write_speed (slow)" "Consider using a faster card"
    else
        test_fail "SD card write speed: $write_speed (very slow)" "System performance will be poor"
    fi
else
    test_warn "Cannot test SD card speed" "dd command not available"
fi

# Test 8: USB Storage (if mounted)
echo ""
echo "Test 8: USB storage validation"
if mount | grep -q "/media/d3kos\|/mnt/usb"; then
    usb_mount=$(mount | grep "/media/d3kos\|/mnt/usb" | awk '{print $3}' | head -1)
    usb_usage=$(df "$usb_mount" | tail -1 | awk '{print $5}' | tr -d '%')
    usb_avail=$(df -h "$usb_mount" | tail -1 | awk '{print $4}')

    test_pass "USB storage mounted at $usb_mount"
    test_pass "USB storage usage: ${usb_usage}% (${usb_avail} available)"

    if [ "$usb_usage" -gt 90 ]; then
        test_warn "USB storage is ${usb_usage}% full" "Consider cleaning up camera recordings"
    fi
else
    test_warn "No USB storage detected" "Camera recordings will use SD card"
fi

# Test 9: System Temperature (Raspberry Pi)
echo ""
echo "Test 9: System temperature check"
if [ -f "/sys/class/thermal/thermal_zone0/temp" ]; then
    temp_raw=$(cat /sys/class/thermal/thermal_zone0/temp)
    temp_c=$((temp_raw / 1000))

    if [ "$temp_c" -lt 70 ]; then
        test_pass "CPU temperature: ${temp_c}°C (normal)"
    elif [ "$temp_c" -lt 80 ]; then
        test_warn "CPU temperature: ${temp_c}°C (warm)" "Consider improving cooling"
    else
        test_fail "CPU temperature: ${temp_c}°C (hot)" "System may throttle performance"
    fi
else
    test_warn "Cannot read CPU temperature" "Not running on Raspberry Pi?"
fi

# Print summary
echo ""
echo "========================================="
echo "Test Summary"
echo "========================================="
echo -e "Tests Passed:  ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed:  ${RED}$TESTS_FAILED${NC}"
echo -e "Warnings:      ${YELLOW}$WARNINGS${NC}"
echo ""

# Exit with appropriate code
if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All hardware checks passed${NC}"
    exit 0
else
    echo -e "${RED}✗ Some hardware issues detected - review failures above${NC}"
    exit 1
fi
