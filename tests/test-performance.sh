#!/bin/bash
# test-performance.sh - d3kOS Performance Benchmarks
# Part of Distribution Prep Session 3: Testing & QA
# Tests boot time, dashboard update rate, AI response time, memory, CPU, disk usage

set -e

# Test configuration
SCRIPT_NAME="Performance Benchmarks"
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

test_metric() {
    echo -e "${GREEN}ℹ METRIC${NC}: $1"
}

print_header

# Test 1: System uptime and boot time
echo "Test 1: System boot time"
if command -v systemd-analyze &> /dev/null; then
    boot_time=$(systemd-analyze | grep "Startup finished" | grep -oP '\d+\.\d+s' | tail -1 | sed 's/s//')

    if [ -n "$boot_time" ]; then
        test_metric "System boot time: ${boot_time}s"

        # Convert to comparison-friendly format
        boot_time_int=$(echo "$boot_time" | cut -d. -f1)

        if [ "$boot_time_int" -lt 60 ]; then
            test_pass "Boot time under 60 seconds: ${boot_time}s"
        elif [ "$boot_time_int" -lt 90 ]; then
            test_warn "Boot time over 60 seconds: ${boot_time}s" "Consider optimizing startup services"
        else
            test_fail "Boot time over 90 seconds: ${boot_time}s" "System startup is too slow"
        fi
    else
        test_warn "Cannot determine boot time" "systemd-analyze output unexpected"
    fi
else
    test_warn "Cannot measure boot time" "systemd-analyze not available"
fi

# Test 2: Memory usage
echo ""
echo "Test 2: Memory usage"
if command -v free &> /dev/null; then
    mem_total=$(free -m | awk '/Mem:/ {print $2}')
    mem_used=$(free -m | awk '/Mem:/ {print $3}')
    mem_free=$(free -m | awk '/Mem:/ {print $4}')
    mem_percent=$(awk "BEGIN {printf \"%.0f\", ($mem_used / $mem_total) * 100}")

    test_metric "Memory usage: ${mem_used}MB / ${mem_total}MB (${mem_percent}%)"

    if [ "$mem_percent" -lt 70 ]; then
        test_pass "Memory usage is healthy: ${mem_percent}%"
    elif [ "$mem_percent" -lt 85 ]; then
        test_warn "Memory usage is high: ${mem_percent}%" "Consider stopping unused services"
    else
        test_fail "Memory usage is critical: ${mem_percent}%" "System may be unstable"
    fi
else
    test_warn "Cannot measure memory usage" "free command not available"
fi

# Test 3: CPU usage (5-second average)
echo ""
echo "Test 3: CPU usage"
if command -v top &> /dev/null; then
    # Get CPU idle percentage from top
    cpu_idle=$(top -bn2 -d 1 | grep "Cpu(s)" | tail -1 | awk '{print $8}' | sed 's/%id,//')
    cpu_usage=$(awk "BEGIN {printf \"%.0f\", 100 - $cpu_idle}")

    test_metric "CPU usage: ${cpu_usage}%"

    if [ "$cpu_usage" -lt 50 ]; then
        test_pass "CPU usage is normal: ${cpu_usage}%"
    elif [ "$cpu_usage" -lt 80 ]; then
        test_warn "CPU usage is elevated: ${cpu_usage}%" "May be under load"
    else
        test_fail "CPU usage is critical: ${cpu_usage}%" "System is overloaded"
    fi
else
    test_warn "Cannot measure CPU usage" "top command not available"
fi

# Test 4: Disk usage
echo ""
echo "Test 4: Disk usage"
disk_usage=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
disk_avail=$(df -h / | tail -1 | awk '{print $4}')

test_metric "Disk usage: ${disk_usage}% (${disk_avail} available)"

if [ "$disk_usage" -lt 85 ]; then
    test_pass "Disk usage is healthy: ${disk_usage}%"
elif [ "$disk_usage" -lt 95 ]; then
    test_warn "Disk usage is high: ${disk_usage}%" "Consider cleaning up old files"
else
    test_fail "Disk usage is critical: ${disk_usage}%" "System may run out of space"
fi

# Test 5: Dashboard update rate (Signal K WebSocket)
echo ""
echo "Test 5: Dashboard update rate"
# Measure time to receive 10 messages from Signal K WebSocket
if command -v websocat &> /dev/null; then
    start_time=$(date +%s.%N)
    message_count=$(timeout 10 websocat -n10 "ws://192.168.1.237/signalk/v1/stream?subscribe=all" 2>/dev/null | wc -l || echo "0")
    end_time=$(date +%s.%N)

    if [ "$message_count" -gt 0 ]; then
        elapsed=$(echo "$end_time - $start_time" | bc)
        update_rate=$(echo "scale=2; $message_count / $elapsed" | bc)

        test_metric "Dashboard update rate: ${update_rate} messages/second"

        # Check if at least 1 Hz
        if (( $(echo "$update_rate >= 1.0" | bc -l) )); then
            test_pass "Dashboard update rate meets 1 Hz requirement: ${update_rate}/s"
        else
            test_warn "Dashboard update rate below 1 Hz: ${update_rate}/s" "Data may feel laggy"
        fi
    else
        test_warn "No WebSocket messages received" "Signal K may not be streaming data"
    fi
elif command -v wscat &> /dev/null; then
    test_warn "Dashboard update rate test skipped" "Using wscat (less reliable for counting)"
else
    test_warn "Cannot test dashboard update rate" "Neither websocat nor wscat available"
fi

# Test 6: AI response time (simple query)
echo ""
echo "Test 6: AI response time (simple query)"
if command -v jq &> /dev/null; then
    # Test with a simple rule-based query (should be fast with cache)
    start_time=$(date +%s%3N)  # milliseconds
    response=$(curl -s -X POST "$BASE_URL/ai/query" \
        -H "Content-Type: application/json" \
        -d '{"question": "what time is it?", "provider": "auto"}' 2>&1)
    end_time=$(date +%s%3N)

    if echo "$response" | jq -e '.success' &>/dev/null; then
        elapsed=$((end_time - start_time))
        provider=$(echo "$response" | jq -r '.provider' 2>/dev/null || echo "unknown")

        test_metric "AI response time: ${elapsed}ms (provider: $provider)"

        if [ "$elapsed" -lt 2000 ]; then
            test_pass "AI response time under 2 seconds: ${elapsed}ms"
        elif [ "$elapsed" -lt 10000 ]; then
            test_warn "AI response time over 2 seconds: ${elapsed}ms" "May be using online AI"
        else
            test_fail "AI response time over 10 seconds: ${elapsed}ms" "Unacceptably slow"
        fi
    else
        test_warn "AI query failed" "Service may be starting up"
    fi
else
    test_warn "Cannot test AI response time" "jq not available"
fi

# Test 7: Camera frame rate
echo ""
echo "Test 7: Camera frame rate"
# Measure time to retrieve 5 frames
if curl -s "$BASE_URL/camera/status" | grep -q "true"; then
    start_time=$(date +%s%3N)
    for i in {1..5}; do
        curl -s -o /dev/null "$BASE_URL/camera/frame"
    done
    end_time=$(date +%s%3N)

    elapsed=$((end_time - start_time))
    fps=$(echo "scale=1; 5000 / $elapsed" | bc)

    test_metric "Camera frame retrieval: ${fps} FPS (average over 5 frames)"

    if (( $(echo "$fps >= 5.0" | bc -l) )); then
        test_pass "Camera frame rate acceptable: ${fps} FPS"
    else
        test_warn "Camera frame rate low: ${fps} FPS" "Network or camera may be slow"
    fi
else
    test_warn "Camera not connected" "Cannot test frame rate"
fi

# Test 8: Fish detection inference time
echo ""
echo "Test 8: Fish detection inference time"
if command -v jq &> /dev/null; then
    if curl -s "$BASE_URL/detect/status" | jq -e '.service_running' | grep -q "true"; then
        # Trigger detection on current frame
        start_time=$(date +%s%3N)
        detect_response=$(curl -s -X POST "$BASE_URL/detect/frame" 2>&1)
        end_time=$(date +%s%3N)

        if echo "$detect_response" | jq -e '.success' &>/dev/null; then
            elapsed=$((end_time - start_time))
            detection_count=$(echo "$detect_response" | jq '.detections | length' 2>/dev/null || echo "0")

            test_metric "Fish detection inference time: ${elapsed}ms (${detection_count} detections)"

            if [ "$elapsed" -lt 5000 ]; then
                test_pass "Detection inference time acceptable: ${elapsed}ms"
            else
                test_warn "Detection inference time slow: ${elapsed}ms" "Pi 4B expected 2-3 seconds"
            fi
        else
            test_warn "Detection failed" "Camera may not be connected"
        fi
    else
        test_warn "Fish detection service not running" "Cannot test inference time"
    fi
fi

# Test 9: Service startup time
echo ""
echo "Test 9: Service startup times"
if command -v systemd-analyze &> /dev/null; then
    # Get slowest starting services
    echo ""
    echo "Top 5 slowest starting services:"
    systemd-analyze blame | head -5

    test_pass "Service startup analysis available (see above)"
else
    test_warn "Cannot analyze service startup times" "systemd-analyze not available"
fi

# Test 10: Network latency
echo ""
echo "Test 10: Network latency (localhost)"
if command -v ping &> /dev/null; then
    # Ping localhost to measure network stack latency
    latency=$(ping -c 5 localhost | grep "avg" | awk -F'/' '{print $5}' || echo "0")

    if [ -n "$latency" ] && [ "$latency" != "0" ]; then
        test_metric "Network latency (localhost): ${latency}ms"

        latency_int=$(echo "$latency" | cut -d. -f1)
        if [ "$latency_int" -lt 1 ]; then
            test_pass "Network latency is excellent: ${latency}ms"
        else
            test_warn "Network latency elevated: ${latency}ms" "May indicate system load"
        fi
    else
        test_warn "Cannot measure network latency" "ping output unexpected"
    fi
fi

# Print summary
echo ""
echo "========================================="
echo "Performance Summary"
echo "========================================="
echo -e "Tests Passed:  ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed:  ${RED}$TESTS_FAILED${NC}"
echo -e "Warnings:      ${YELLOW}$WARNINGS${NC}"
echo ""

# Exit with appropriate code
if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ Performance is acceptable${NC}"
    exit 0
else
    echo -e "${RED}✗ Performance issues detected - review failures above${NC}"
    exit 1
fi
