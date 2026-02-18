#!/bin/bash
# test-known-issues.sh - d3kOS Known Issues Testing
# Part of Distribution Prep Session 3: Testing & QA
# Tests for known issues and documents their status (expected failures)

set -e

# Test configuration
SCRIPT_NAME="Known Issues Testing"
TESTS_PASSED=0
TESTS_FAILED=0
WARNINGS=0
KNOWN_ISSUES=0

# Base URL
BASE_URL="${BASE_URL:-http://192.168.1.237}"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Output functions
print_header() {
    echo ""
    echo "========================================="
    echo "$SCRIPT_NAME"
    echo "========================================="
    echo ""
    echo -e "${BLUE}NOTE: This test suite documents KNOWN issues.${NC}"
    echo -e "${BLUE}Some failures here are EXPECTED and documented.${NC}"
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

test_known_issue() {
    echo -e "${BLUE}✗ KNOWN ISSUE${NC}: $1"
    echo -e "  ${BLUE}Status${NC}: $2"
    echo -e "  ${BLUE}Workaround${NC}: $3"
    ((KNOWN_ISSUES++))
}

print_header

# KNOWN ISSUE #1: Voice Assistant Wake Word Detection
echo "Known Issue #1: Voice Assistant Wake Word Detection"
echo "---------------------------------------------------"

# Check if voice service is running
if systemctl is-active --quiet d3kos-voice; then
    test_pass "Voice assistant service is running"

    # Check if PocketSphinx process is running
    if pgrep -f pocketsphinx_continuous &>/dev/null; then
        test_pass "PocketSphinx wake word detection process is running"

        # Try to detect wake word (this is expected to FAIL)
        echo ""
        echo "Testing wake word detection (20-second test)..."
        echo "(Please say 'HELM' clearly into microphone)"
        echo ""

        # Monitor logs for wake word detection
        timeout 20 journalctl -u d3kos-voice -f --since "1 minute ago" | grep -m 1 "Wake word detected" &
        log_pid=$!

        sleep 20
        kill $log_pid 2>/dev/null || true

        # Check if wake word was detected
        if journalctl -u d3kos-voice --since "1 minute ago" | grep -q "Wake word detected"; then
            test_pass "Voice assistant detected wake word"
            echo -e "${GREEN}✓ ISSUE RESOLVED!${NC} Voice assistant is now working."
        else
            test_known_issue \
                "Voice assistant does not detect wake words ('helm', 'advisor', 'counsel')" \
                "CONFIRMED - Issue present since 2026-02-17" \
                "Use text-based AI Assistant at http://192.168.1.237/ai-assistant.html"
        fi
    else
        test_fail "PocketSphinx process not running" "Voice service may have crashed"
    fi
else
    test_warn "Voice assistant service not running" "Service may be disabled (expected for Tier 0/1)"
fi

# KNOWN ISSUE #2: NMEA2000 Simulator (should be disabled)
echo ""
echo "Known Issue #2: NMEA2000 Simulator Status"
echo "------------------------------------------"

# Check if simulator service exists
if systemctl list-unit-files | grep -q "d3kos-simulator.service"; then
    # Check if simulator is running
    if systemctl is-active --quiet d3kos-simulator; then
        test_known_issue \
            "NMEA2000 simulator is running on production system" \
            "Should be disabled for distribution" \
            "Run: sudo systemctl stop d3kos-simulator && sudo systemctl disable d3kos-simulator"
    else
        test_pass "NMEA2000 simulator is disabled (correct for production)"
    fi
else
    test_pass "NMEA2000 simulator service not installed (correct for distribution)"
fi

# Check if vcan0-simulator is enabled in Signal K
if [ -f "/home/d3kos/.signalk/settings.json" ]; then
    if grep -q '"id": "vcan0-simulator"' /home/d3kos/.signalk/settings.json; then
        if grep -A 2 '"id": "vcan0-simulator"' /home/d3kos/.signalk/settings.json | grep -q '"enabled": true'; then
            test_known_issue \
                "vcan0-simulator provider enabled in Signal K" \
                "Should be disabled for distribution" \
                "Disable in Signal K admin UI or edit ~/.signalk/settings.json"
        else
            test_pass "vcan0-simulator provider is disabled in Signal K"
        fi
    else
        test_pass "vcan0-simulator provider not configured (correct)"
    fi
fi

# KNOWN ISSUE #3: Boatlog Export Button
echo ""
echo "Known Issue #3: Boatlog Export Button"
echo "--------------------------------------"

# This is a UI test that requires browser interaction
test_warn "Boatlog export button functionality not testable via script" \
    "Manual test required: Visit http://192.168.1.237/boatlog.html and click Export button"

# Check if export manager service is running (prerequisite)
if systemctl is-active --quiet d3kos-export-manager; then
    test_pass "Export manager service is running (prerequisite OK)"
else
    test_fail "Export manager service not running" "Export functionality will not work"
fi

# KNOWN ISSUE #4: GPS Drift When Stationary
echo ""
echo "Known Issue #4: GPS Drift When Stationary"
echo "------------------------------------------"

if command -v jq &> /dev/null; then
    # Get current speed from Signal K
    speed_data=$(curl -s "$BASE_URL/signalk/v1/api/vessels/self/navigation/speedOverGround" 2>&1)

    if echo "$speed_data" | jq -e '.value' &>/dev/null; then
        speed_mps=$(echo "$speed_data" | jq -r '.value')
        speed_knots=$(echo "scale=2; $speed_mps * 1.94384" | bc)

        # If stationary (engine off) but showing movement
        rpm_data=$(curl -s "$BASE_URL/signalk/v1/api/vessels/self/propulsion/port/revolutions" 2>&1)
        if echo "$rpm_data" | jq -e '.value' &>/dev/null; then
            rpm_value=$(echo "$rpm_data" | jq -r '.value')

            if [ "$rpm_value" = "0" ] || [ "$rpm_value" = "null" ]; then
                # Engine is off, check if GPS shows movement
                if (( $(echo "$speed_knots > 0.5" | bc -l) )); then
                    test_known_issue \
                        "GPS shows movement ($speed_knots knots) when stationary (engine off)" \
                        "EXPECTED - GPS drift with weak satellite signals indoors" \
                        "Normal behavior. GPS accuracy improves outdoors with 8+ satellites"
                else
                    test_pass "GPS drift is minimal ($speed_knots knots)"
                fi
            else
                test_pass "Engine is running, GPS movement expected"
            fi
        fi
    else
        test_warn "GPS speed data not available" "Cannot test for drift"
    fi
fi

# KNOWN ISSUE #5: Onboarding Reset Limit
echo ""
echo "Known Issue #5: Onboarding Reset Limit"
echo "---------------------------------------"

if command -v jq &> /dev/null && [ -f "/opt/d3kos/config/license.json" ]; then
    reset_count=$(jq -r '.reset_count' /opt/d3kos/config/license.json 2>/dev/null || echo "0")
    max_resets=$(jq -r '.max_resets' /opt/d3kos/config/license.json 2>/dev/null || echo "10")

    if [ "$max_resets" != "-1" ]; then
        remaining=$((max_resets - reset_count))

        if [ "$remaining" -le 3 ]; then
            test_known_issue \
                "Onboarding wizard resets nearly exhausted ($reset_count/$max_resets)" \
                "Tier 0 has 10 reset limit" \
                "Upgrade to Tier 2+ for unlimited resets"
        elif [ "$remaining" -le 5 ]; then
            test_warn "Onboarding resets at $reset_count/$max_resets" \
                "Consider upgrade to Tier 2+ for unlimited resets"
        else
            test_pass "Onboarding resets available: $reset_count/$max_resets"
        fi
    else
        test_pass "Unlimited onboarding resets enabled (Tier 2+)"
    fi
fi

# KNOWN ISSUE #6: PipeWire Audio Signal Loss
echo ""
echo "Known Issue #6: PipeWire Audio Signal Loss"
echo "-------------------------------------------"

# Check if PipeWire is running
if pgrep -x pipewire &>/dev/null; then
    test_pass "PipeWire audio server is running"

    # Check microphone signal strength
    if command -v arecord &> /dev/null; then
        # Record 1 second sample
        if arecord -D plughw:3,0 -d 1 -f S16_LE -r 16000 /tmp/test_mic.wav &>/dev/null 2>&1; then
            # Analyze signal strength with sox if available
            if command -v sox &> /dev/null; then
                max_amplitude=$(sox /tmp/test_mic.wav -n stat 2>&1 | grep "Maximum amplitude" | awk '{print $3}')
                rm -f /tmp/test_mic.wav

                if [ -n "$max_amplitude" ]; then
                    # Convert to percentage
                    amplitude_percent=$(echo "scale=2; $max_amplitude * 100" | bc)

                    test_known_issue \
                        "PipeWire reduces microphone signal by ~17x (detected: ${amplitude_percent}%)" \
                        "Voice assistant uses direct hardware access to bypass" \
                        "Voice service configured with '-adcdev plughw:3,0' to avoid PipeWire"
                fi
            else
                test_pass "Microphone recording works (signal strength not measurable)"
            fi
        else
            test_warn "Cannot record from microphone" "Device may be in use or misconfigured"
        fi
    fi
else
    test_warn "PipeWire not running" "Audio may be using ALSA directly"
fi

# KNOWN ISSUE #7: Telegram Not Configured
echo ""
echo "Known Issue #7: Telegram Notifications"
echo "---------------------------------------"

if command -v jq &> /dev/null; then
    notify_status=$(curl -s "$BASE_URL/notify/status" 2>&1)

    if echo "$notify_status" | jq -e '.telegram_configured' &>/dev/null; then
        telegram_configured=$(echo "$notify_status" | jq -r '.telegram_configured')

        if [ "$telegram_configured" = "false" ]; then
            test_known_issue \
                "Telegram notifications not configured" \
                "Expected for fresh installation" \
                "User must set up bot via @BotFather and configure token/chat_id"
        else
            test_pass "Telegram notifications are configured"
        fi
    fi
fi

# Print summary
echo ""
echo "========================================="
echo "Known Issues Summary"
echo "========================================="
echo -e "Tests Passed:     ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed:     ${RED}$TESTS_FAILED${NC}"
echo -e "Warnings:         ${YELLOW}$WARNINGS${NC}"
echo -e "Known Issues:     ${BLUE}$KNOWN_ISSUES${NC}"
echo ""

if [ $KNOWN_ISSUES -gt 0 ]; then
    echo -e "${BLUE}ℹ  $KNOWN_ISSUES known issue(s) documented above${NC}"
    echo -e "${BLUE}   These are expected and have workarounds.${NC}"
    echo ""
fi

# Exit with success if only known issues (not new failures)
if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ No NEW issues detected${NC}"
    exit 0
else
    echo -e "${RED}✗ New issues detected (not documented as known) - review failures above${NC}"
    exit 1
fi
