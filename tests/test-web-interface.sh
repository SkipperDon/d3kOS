#!/bin/bash
# test-web-interface.sh - d3kOS Web Interface & API Validation
# Part of Distribution Prep Session 3: Testing & QA
# Tests all web pages return 200 OK and API endpoints return valid JSON

set -e

# Test configuration
SCRIPT_NAME="Web Interface & API Validation"
TESTS_PASSED=0
TESTS_FAILED=0
WARNINGS=0

# Base URL (change if testing remotely)
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
    echo "Base URL: $BASE_URL"
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

# Web pages to test
WEB_PAGES=(
    "/"
    "/index.html"
    "/dashboard.html"
    "/onboarding.html"
    "/boatlog.html"
    "/navigation.html"
    "/helm.html"
    "/weather.html"
    "/marine-vision.html"
    "/ai-assistant.html"
    "/settings.html"
)

# API endpoints to test (endpoint:expected_key_in_json)
declare -A API_ENDPOINTS=(
    ["/license/info"]="installation_id"
    ["/tier/status"]="tier"
    ["/export/status"]="success"
    ["/ai/status"]="success"
    ["/camera/status"]="connected"
    ["/detect/status"]="service_running"
    ["/notify/status"]="service_running"
)

print_header

# Test 1: Check curl is available
echo "Test 1: Curl availability"
if command -v curl &> /dev/null; then
    test_pass "curl command available"
else
    test_fail "curl command not found" "Cannot test web interface without curl"
    exit 1
fi

# Test 2: Check jq is available (for JSON parsing)
echo ""
echo "Test 2: JSON parser availability"
if command -v jq &> /dev/null; then
    test_pass "jq command available"
    JQ_AVAILABLE=true
else
    test_warn "jq command not found" "JSON validation will be limited"
    JQ_AVAILABLE=false
fi

# Test 3: Test nginx is responding
echo ""
echo "Test 3: Nginx web server connectivity"
if curl -s -o /dev/null -w "%{http_code}" "$BASE_URL" | grep -q "200\|301\|302"; then
    test_pass "Nginx web server is responding"
else
    test_fail "Nginx web server not responding" "Cannot reach $BASE_URL"
    exit 1
fi

# Test 4: Test all web pages return 200 OK
echo ""
echo "Test 4: Web page status codes"
for page in "${WEB_PAGES[@]}"; do
    url="$BASE_URL$page"
    http_code=$(curl -s -o /dev/null -w "%{http_code}" "$url")

    if [ "$http_code" = "200" ]; then
        test_pass "Page $page returns 200 OK"
    else
        test_fail "Page $page returns $http_code" "Expected 200 OK"
    fi
done

# Test 5: Test all web pages contain basic HTML structure
echo ""
echo "Test 5: Web page HTML validation"
for page in "${WEB_PAGES[@]}"; do
    url="$BASE_URL$page"
    content=$(curl -s "$url")

    if echo "$content" | grep -qi "<html"; then
        test_pass "Page $page contains valid HTML"
    else
        test_fail "Page $page missing HTML structure" "May be misconfigured"
    fi
done

# Test 6: Test all API endpoints return valid JSON
echo ""
echo "Test 6: API endpoint JSON validation"
for endpoint in "${!API_ENDPOINTS[@]}"; do
    url="$BASE_URL$endpoint"
    expected_key="${API_ENDPOINTS[$endpoint]}"

    # Get response
    response=$(curl -s "$url" 2>&1)
    http_code=$(curl -s -o /dev/null -w "%{http_code}" "$url")

    # Check HTTP code
    if [ "$http_code" != "200" ]; then
        test_fail "API $endpoint returns $http_code" "Expected 200 OK"
        continue
    fi

    # Check if response is valid JSON
    if [ "$JQ_AVAILABLE" = true ]; then
        if echo "$response" | jq empty 2>/dev/null; then
            # Check if expected key exists
            if echo "$response" | jq -e ".$expected_key" &>/dev/null; then
                test_pass "API $endpoint returns valid JSON with '$expected_key'"
            else
                test_fail "API $endpoint missing expected key '$expected_key'" "JSON structure may have changed"
            fi
        else
            test_fail "API $endpoint returns invalid JSON" "Response: ${response:0:100}"
        fi
    else
        # Basic JSON check without jq
        if echo "$response" | grep -q "{"; then
            test_pass "API $endpoint returns JSON (basic check)"
        else
            test_fail "API $endpoint doesn't return JSON" "Response: ${response:0:100}"
        fi
    fi
done

# Test 7: Test specific API functionality
echo ""
echo "Test 7: API functionality tests"

# Test license API installation ID format (16-char hex)
if [ "$JQ_AVAILABLE" = true ]; then
    install_id=$(curl -s "$BASE_URL/license/info" | jq -r '.installation_id')
    if [[ "$install_id" =~ ^[0-9a-f]{16}$ ]]; then
        test_pass "Installation ID has correct format (16-char hex): $install_id"
    else
        test_fail "Installation ID has wrong format: $install_id" "Expected 16-char hex string"
    fi

    # Test tier is valid (0, 1, 2, or 3)
    tier=$(curl -s "$BASE_URL/tier/status" | jq -r '.tier')
    if [[ "$tier" =~ ^[0-3]$ ]]; then
        test_pass "Tier value is valid: $tier"
    else
        test_fail "Tier value is invalid: $tier" "Expected 0, 1, 2, or 3"
    fi
fi

# Test 8: Test main menu navigation links
echo ""
echo "Test 8: Main menu navigation validation"
main_page=$(curl -s "$BASE_URL/")

# Check for navigation buttons
nav_buttons=("Dashboard" "Boatlog" "Navigation" "Charts" "Helm" "Weather" "Marine Vision" "AI" "Settings")
for button in "${nav_buttons[@]}"; do
    if echo "$main_page" | grep -qi "$button"; then
        test_pass "Main menu contains '$button' navigation"
    else
        test_warn "Main menu missing '$button' button" "May have been renamed or removed"
    fi
done

# Test 9: Test AtMyBoat.com logo presence
echo ""
echo "Test 9: Branding validation"
if echo "$main_page" | grep -qi "atmyboat"; then
    test_pass "AtMyBoat.com branding present"
else
    test_warn "AtMyBoat.com branding not found" "Logo may be missing"
fi

# Test 10: Test onboarding wizard QR code generation
echo ""
echo "Test 10: Onboarding wizard features"
onboarding_page=$(curl -s "$BASE_URL/onboarding.html")

if echo "$onboarding_page" | grep -qi "qrcode"; then
    test_pass "Onboarding wizard includes QR code generation"
else
    test_warn "QR code generation not found in onboarding" "Feature may have been removed"
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
    echo -e "${GREEN}✓ All web interfaces operational${NC}"
    exit 0
else
    echo -e "${RED}✗ Some web interface issues - review failures above${NC}"
    exit 1
fi
