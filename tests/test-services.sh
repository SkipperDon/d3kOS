#!/bin/bash
# test-services.sh - d3kOS Service Status & Port Validation
# Part of Distribution Prep Session 3: Testing & QA
# Tests all d3kOS systemd services and verifies they're running on correct ports

set -e

# Test configuration
SCRIPT_NAME="Service Status & Port Checks"
TESTS_PASSED=0
TESTS_FAILED=0
WARNINGS=0

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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

# Service definitions (service_name:expected_port)
declare -A SERVICES=(
    ["d3kos-license-api"]="8091"
    ["d3kos-tier-api"]="8093"
    ["d3kos-tier-manager"]="none"
    ["d3kos-export-manager"]="8094"
    ["d3kos-ai-api"]="8080"
    ["d3kos-camera-stream"]="8084"
    ["d3kos-fish-detector"]="8086"
    ["d3kos-notifications"]="8088"
)

# Optional services (may not be running)
declare -A OPTIONAL_SERVICES=(
    ["d3kos-voice"]="none"
)

print_header

# Test 1: Check if systemd is available
echo "Test 1: Systemd availability"
if command -v systemctl &> /dev/null; then
    test_pass "systemctl command available"
else
    test_fail "systemctl command not found" "systemd not installed or not running"
    exit 1
fi

# Test 2: Check required services are active
echo ""
echo "Test 2: Required service status"
for service in "${!SERVICES[@]}"; do
    if systemctl is-active --quiet "$service"; then
        test_pass "Service $service is active"
    else
        status=$(systemctl is-active "$service" 2>&1 || echo "unknown")
        test_fail "Service $service not active" "Status: $status"
    fi
done

# Test 3: Check optional services (warnings only)
echo ""
echo "Test 3: Optional service status"
for service in "${!OPTIONAL_SERVICES[@]}"; do
    if systemctl is-active --quiet "$service"; then
        test_pass "Optional service $service is active"
    else
        status=$(systemctl is-active "$service" 2>&1 || echo "inactive")
        test_warn "Optional service $service not active" "This is expected if feature is disabled (Status: $status)"
    fi
done

# Test 4: Check service ports are listening
echo ""
echo "Test 4: Service port verification"
for service in "${!SERVICES[@]}"; do
    port="${SERVICES[$service]}"
    if [ "$port" = "none" ]; then
        test_pass "Service $service (no port required)"
        continue
    fi

    # Check if port is listening (try multiple methods)
    if command -v lsof &> /dev/null; then
        if sudo lsof -i ":$port" -sTCP:LISTEN &> /dev/null; then
            test_pass "Service $service listening on port $port"
        else
            test_fail "Service $service not listening on port $port" "Port may be wrong or service not started"
        fi
    elif command -v netstat &> /dev/null; then
        if netstat -tln | grep -q ":$port "; then
            test_pass "Service $service listening on port $port"
        else
            test_fail "Service $service not listening on port $port" "Port may be wrong or service not started"
        fi
    else
        test_warn "Cannot verify port $port for $service" "Neither lsof nor netstat available"
    fi
done

# Test 5: Check for service errors in logs (last 50 lines)
echo ""
echo "Test 5: Service log error check (last 50 lines)"
for service in "${!SERVICES[@]}"; do
    # Check if service has any errors in recent logs
    error_count=$(journalctl -u "$service" -n 50 --no-pager 2>/dev/null | grep -ci "error" || echo "0")

    if [ "$error_count" -eq 0 ]; then
        test_pass "Service $service has no errors in recent logs"
    else
        # Get the actual error lines
        error_sample=$(journalctl -u "$service" -n 50 --no-pager 2>/dev/null | grep -i "error" | tail -n 1)
        test_warn "Service $service has $error_count error(s) in recent logs" "Latest: $error_sample"
    fi
done

# Test 6: Check service enable status (auto-start on boot)
echo ""
echo "Test 6: Service auto-start configuration"
for service in "${!SERVICES[@]}"; do
    if systemctl is-enabled --quiet "$service" 2>/dev/null; then
        test_pass "Service $service is enabled (auto-start on boot)"
    else
        enabled_status=$(systemctl is-enabled "$service" 2>&1 || echo "unknown")
        if [ "$enabled_status" = "static" ]; then
            test_pass "Service $service is static (started by dependency)"
        else
            test_fail "Service $service not enabled for auto-start" "Status: $enabled_status"
        fi
    fi
done

# Test 7: Check nginx is running (required for web interface)
echo ""
echo "Test 7: Nginx web server status"
if systemctl is-active --quiet nginx; then
    test_pass "Nginx web server is active"
else
    test_fail "Nginx web server not active" "Web interface will not work"
fi

# Test 8: Check Signal K is running (required for boat data)
echo ""
echo "Test 8: Signal K server status"
if systemctl is-active --quiet signalk; then
    test_pass "Signal K server is active"
else
    test_fail "Signal K server not active" "Boat data will not be available"
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
    echo -e "${GREEN}✓ All required services operational${NC}"
    exit 0
else
    echo -e "${RED}✗ Some services have issues - review failures above${NC}"
    exit 1
fi
