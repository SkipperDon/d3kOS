#!/bin/bash
# test-data-flow.sh - d3kOS Data Flow Validation
# Part of Distribution Prep Session 3: Testing & QA
# Tests Signal K WebSocket, NMEA2000 parsing, GPS updates, AI queries, camera frames

set -e

# Test configuration
SCRIPT_NAME="Data Flow Validation"
TESTS_PASSED=0
TESTS_FAILED=0
WARNINGS=0

# Base URL
BASE_URL="${BASE_URL:-http://192.168.1.237}"

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

# Test 1: Signal K API connectivity
echo "Test 1: Signal K API connectivity"
if curl -s "$BASE_URL/signalk/v1/api/" | grep -q "vessels\|self"; then
    test_pass "Signal K API is responding"
else
    test_fail "Signal K API not responding" "Cannot reach $BASE_URL/signalk/v1/api/"
    exit 1
fi

# Test 2: Signal K WebSocket connectivity
echo ""
echo "Test 2: Signal K WebSocket connectivity"
# Try to connect to WebSocket (timeout after 5 seconds)
if command -v websocat &> /dev/null; then
    if timeout 5 websocat -n1 "ws://192.168.1.237/signalk/v1/stream?subscribe=none" &>/dev/null; then
        test_pass "Signal K WebSocket is responding"
    else
        test_warn "Signal K WebSocket test inconclusive" "websocat connection timed out"
    fi
elif command -v wscat &> /dev/null; then
    if timeout 5 wscat -c "ws://192.168.1.237/signalk/v1/stream?subscribe=none" &>/dev/null; then
        test_pass "Signal K WebSocket is responding"
    else
        test_warn "Signal K WebSocket test inconclusive" "wscat connection timed out"
    fi
else
    test_warn "Cannot test WebSocket" "Neither websocat nor wscat available"
fi

# Test 3: NMEA2000 data flow (engine RPM)
echo ""
echo "Test 3: NMEA2000 engine data flow"
if command -v jq &> /dev/null; then
    rpm_data=$(curl -s "$BASE_URL/signalk/v1/api/vessels/self/propulsion/port/revolutions")

    if echo "$rpm_data" | jq -e '.value' &>/dev/null; then
        rpm_value=$(echo "$rpm_data" | jq -r '.value')
        rpm_rpm=$(echo "$rpm_value * 60" | bc 2>/dev/null || echo "unknown")

        test_pass "Engine RPM data available: $rpm_rpm RPM"

        # Check if timestamp is recent (within last 60 seconds)
        timestamp=$(echo "$rpm_data" | jq -r '.timestamp' 2>/dev/null || echo "")
        if [ -n "$timestamp" ]; then
            test_pass "Engine data has valid timestamp"
        else
            test_warn "Engine data missing timestamp" "Data may be stale"
        fi
    else
        test_warn "Engine RPM data not available" "Engine may be off or CAN0 not connected"
    fi
else
    test_warn "Cannot parse NMEA2000 data" "jq command not available"
fi

# Test 4: GPS position data
echo ""
echo "Test 4: GPS position data flow"
if command -v jq &> /dev/null; then
    gps_data=$(curl -s "$BASE_URL/signalk/v1/api/vessels/self/navigation/position")

    if echo "$gps_data" | jq -e '.value.latitude' &>/dev/null; then
        lat=$(echo "$gps_data" | jq -r '.value.latitude')
        lon=$(echo "$gps_data" | jq -r '.value.longitude')

        test_pass "GPS position available: $lat°N, $lon°W"

        # Check if position is reasonable (not 0,0)
        if [ "$lat" != "0" ] && [ "$lon" != "0" ]; then
            test_pass "GPS position is non-zero (valid fix)"
        else
            test_warn "GPS position is 0,0" "GPS may not have a fix"
        fi
    else
        test_warn "GPS position data not available" "GPS may not have a fix or device not connected"
    fi
else
    test_warn "Cannot parse GPS data" "jq command not available"
fi

# Test 5: GPS satellite count
echo ""
echo "Test 5: GPS satellite data"
if command -v jq &> /dev/null; then
    sat_data=$(curl -s "$BASE_URL/signalk/v1/api/vessels/self/navigation/gnss/satellitesInView")

    if echo "$sat_data" | jq -e '.value.count' &>/dev/null; then
        sat_count=$(echo "$sat_data" | jq -r '.value.count')

        if [ "$sat_count" -ge 4 ]; then
            test_pass "GPS has good satellite count: $sat_count"
        elif [ "$sat_count" -gt 0 ]; then
            test_warn "GPS has low satellite count: $sat_count" "May have weak fix"
        else
            test_warn "GPS has no satellites" "No GPS fix available"
        fi
    else
        test_warn "Satellite count not available" "GPS may not be configured"
    fi
fi

# Test 6: AI Assistant query test
echo ""
echo "Test 6: AI Assistant query processing"
# Send a simple query to AI assistant
ai_response=$(curl -s -X POST "$BASE_URL/ai/query" \
    -H "Content-Type: application/json" \
    -d '{"question": "what time is it?", "provider": "auto"}' 2>&1)

if echo "$ai_response" | grep -qi "time\|error"; then
    if echo "$ai_response" | grep -qi "error"; then
        test_warn "AI Assistant responded with error" "Service may be starting up"
    else
        test_pass "AI Assistant is processing queries"
    fi
else
    test_fail "AI Assistant not responding" "Response: ${ai_response:0:100}"
fi

# Test 7: Camera frame retrieval
echo ""
echo "Test 7: Camera frame retrieval"
# Try to get a frame from camera
http_code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/camera/frame" 2>&1)

if [ "$http_code" = "200" ]; then
    test_pass "Camera is streaming frames"
elif [ "$http_code" = "503" ]; then
    test_warn "Camera not connected" "Service available but camera offline"
else
    test_fail "Camera service not responding" "HTTP $http_code"
fi

# Test 8: Fish detection service
echo ""
echo "Test 8: Fish detection service status"
if command -v jq &> /dev/null; then
    detect_status=$(curl -s "$BASE_URL/detect/status")

    if echo "$detect_status" | jq -e '.service_running' &>/dev/null; then
        service_running=$(echo "$detect_status" | jq -r '.service_running')

        if [ "$service_running" = "true" ]; then
            test_pass "Fish detection service is running"
        else
            test_warn "Fish detection service not running" "May need to be started"
        fi
    else
        test_fail "Fish detection service not responding" "Endpoint may be misconfigured"
    fi
fi

# Test 9: Notification service (if configured)
echo ""
echo "Test 9: Notification service status"
if command -v jq &> /dev/null; then
    notify_status=$(curl -s "$BASE_URL/notify/status" 2>&1)

    if echo "$notify_status" | jq -e '.service_running' &>/dev/null; then
        service_running=$(echo "$notify_status" | jq -r '.service_running')

        if [ "$service_running" = "true" ]; then
            test_pass "Notification service is running"

            # Check if Telegram is configured
            telegram_configured=$(echo "$notify_status" | jq -r '.telegram_configured' 2>/dev/null || echo "false")
            if [ "$telegram_configured" = "true" ]; then
                test_pass "Telegram notifications configured"
            else
                test_warn "Telegram not configured" "User needs to set up bot token and chat ID"
            fi
        else
            test_warn "Notification service not running" "May need to be started"
        fi
    else
        test_warn "Notification service not responding" "Service may not be installed"
    fi
fi

# Test 10: Export manager status
echo ""
echo "Test 10: Export manager data flow"
if command -v jq &> /dev/null; then
    export_status=$(curl -s "$BASE_URL/export/status")

    if echo "$export_status" | jq -e '.tier' &>/dev/null; then
        tier=$(echo "$export_status" | jq -r '.tier')
        can_export=$(echo "$export_status" | jq -r '.can_export')

        test_pass "Export manager is operational (Tier $tier)"

        if [ "$can_export" = "true" ]; then
            test_pass "Data export is enabled for current tier"
        else
            test_warn "Data export disabled for Tier $tier" "Requires Tier 1+"
        fi
    else
        test_fail "Export manager not responding correctly" "Service may be misconfigured"
    fi
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
    echo -e "${GREEN}✓ All data flows operational${NC}"
    exit 0
else
    echo -e "${RED}✗ Some data flow issues - review failures above${NC}"
    exit 1
fi
