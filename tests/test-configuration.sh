#!/bin/bash
# test-configuration.sh - d3kOS Configuration Validation
# Part of Distribution Prep Session 3: Testing & QA
# Tests installation ID, license.json structure, tier detection, nginx proxy

set -e

# Test configuration
SCRIPT_NAME="Configuration Validation"
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

# Test 1: Installation ID file exists
echo "Test 1: Installation ID system"
if [ -f "/opt/d3kos/config/license.json" ]; then
    test_pass "license.json file exists"
else
    test_fail "license.json file not found" "Expected at /opt/d3kos/config/license.json"
fi

# Test 2: Installation ID format validation
echo ""
echo "Test 2: Installation ID format"
if command -v jq &> /dev/null && [ -f "/opt/d3kos/config/license.json" ]; then
    install_id=$(jq -r '.installation_id' /opt/d3kos/config/license.json 2>/dev/null || echo "")

    if [[ "$install_id" =~ ^[0-9a-f]{16}$ ]]; then
        test_pass "Installation ID has correct format: $install_id"
    else
        test_fail "Installation ID has wrong format: $install_id" "Expected 16-character hex string"
    fi
else
    test_warn "Cannot validate installation ID format" "jq not available or file missing"
fi

# Test 3: License.json structure validation
echo ""
echo "Test 3: license.json structure"
if command -v jq &> /dev/null && [ -f "/opt/d3kos/config/license.json" ]; then
    # Check required fields
    required_fields=("installation_id" "tier" "reset_count" "max_resets" "version" "features")

    for field in "${required_fields[@]}"; do
        if jq -e ".$field" /opt/d3kos/config/license.json &>/dev/null; then
            test_pass "license.json has required field: $field"
        else
            test_fail "license.json missing field: $field" "File structure may be corrupted"
        fi
    done

    # Check features object
    if jq -e '.features.voice_assistant' /opt/d3kos/config/license.json &>/dev/null; then
        test_pass "license.json features object is valid"
    else
        test_fail "license.json features object invalid" "Missing required feature flags"
    fi
fi

# Test 4: Tier value validation
echo ""
echo "Test 4: Tier configuration"
if command -v jq &> /dev/null && [ -f "/opt/d3kos/config/license.json" ]; then
    tier=$(jq -r '.tier' /opt/d3kos/config/license.json 2>/dev/null || echo "-1")

    if [[ "$tier" =~ ^[0-3]$ ]]; then
        test_pass "Tier value is valid: $tier"

        # Check tier matches API
        api_tier=$(curl -s "$BASE_URL/tier/status" | jq -r '.tier' 2>/dev/null || echo "-1")
        if [ "$tier" = "$api_tier" ]; then
            test_pass "license.json tier matches API tier: $tier"
        else
            test_warn "Tier mismatch" "license.json=$tier, API=$api_tier"
        fi
    else
        test_fail "Tier value is invalid: $tier" "Expected 0, 1, 2, or 3"
    fi
fi

# Test 5: Reset counter validation
echo ""
echo "Test 5: Reset counter configuration"
if command -v jq &> /dev/null && [ -f "/opt/d3kos/config/license.json" ]; then
    reset_count=$(jq -r '.reset_count' /opt/d3kos/config/license.json 2>/dev/null || echo "-1")
    max_resets=$(jq -r '.max_resets' /opt/d3kos/config/license.json 2>/dev/null || echo "-1")

    if [ "$reset_count" -ge 0 ]; then
        test_pass "Reset count is valid: $reset_count"

        if [ "$reset_count" -lt "$max_resets" ]; then
            test_pass "Reset count ($reset_count) below max ($max_resets)"
        elif [ "$max_resets" = "-1" ]; then
            test_pass "Unlimited resets enabled"
        else
            test_warn "Reset count at limit" "User cannot reset onboarding wizard"
        fi
    else
        test_fail "Reset count is invalid: $reset_count" "Expected non-negative integer"
    fi
fi

# Test 6: Nginx proxy configuration
echo ""
echo "Test 6: Nginx proxy configuration"
if [ -f "/etc/nginx/sites-enabled/default" ]; then
    test_pass "Nginx default site configuration exists"

    # Check required proxy locations
    proxy_locations=(
        "/signalk/"
        "/license/"
        "/tier/"
        "/export/"
        "/ai/"
        "/camera/"
        "/detect/"
        "/notify/"
    )

    for location in "${proxy_locations[@]}"; do
        if grep -q "location $location" /etc/nginx/sites-enabled/default; then
            test_pass "Nginx proxy configured for $location"
        else
            test_fail "Nginx proxy missing for $location" "API endpoint may not be accessible"
        fi
    done
else
    test_fail "Nginx configuration file not found" "Expected at /etc/nginx/sites-enabled/default"
fi

# Test 7: Nginx proxy port verification
echo ""
echo "Test 7: Nginx proxy port mapping"
if [ -f "/etc/nginx/sites-enabled/default" ]; then
    # Check if ports are correctly mapped
    declare -A expected_ports=(
        ["license"]="8091"
        ["tier"]="8093"
        ["export"]="8094"
        ["ai"]="8080"
        ["camera"]="8084"
        ["detect"]="8086"
        ["notify"]="8088"
    )

    for endpoint in "${!expected_ports[@]}"; do
        port="${expected_ports[$endpoint]}"
        if grep -A 2 "location /$endpoint/" /etc/nginx/sites-enabled/default | grep -q "localhost:$port"; then
            test_pass "Nginx proxy for /$endpoint/ correctly maps to port $port"
        else
            test_fail "Nginx proxy for /$endpoint/ wrong port" "Expected port $port"
        fi
    done
fi

# Test 8: Service file configuration
echo ""
echo "Test 8: Systemd service files"
service_files=(
    "d3kos-license-api.service"
    "d3kos-tier-api.service"
    "d3kos-tier-manager.service"
    "d3kos-export-manager.service"
    "d3kos-ai-api.service"
    "d3kos-camera-stream.service"
    "d3kos-fish-detector.service"
    "d3kos-notifications.service"
)

for service_file in "${service_files[@]}"; do
    if [ -f "/etc/systemd/system/$service_file" ]; then
        test_pass "Service file exists: $service_file"
    else
        test_fail "Service file missing: $service_file" "Service may not auto-start"
    fi
done

# Test 9: Configuration directory structure
echo ""
echo "Test 9: Directory structure"
required_dirs=(
    "/opt/d3kos/config"
    "/opt/d3kos/services"
    "/opt/d3kos/data"
    "/opt/d3kos/models"
    "/var/www/html"
)

for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        test_pass "Directory exists: $dir"
    else
        test_fail "Directory missing: $dir" "System may not function correctly"
    fi
done

# Test 10: File permissions
echo ""
echo "Test 10: File permissions"
# Check if config files are readable by d3kos user
if [ -f "/opt/d3kos/config/license.json" ]; then
    if [ -r "/opt/d3kos/config/license.json" ]; then
        test_pass "license.json is readable"
    else
        test_fail "license.json is not readable" "Permission issue"
    fi
fi

# Check if service scripts are executable
service_scripts=(
    "/opt/d3kos/services/license/license-api.py"
    "/opt/d3kos/services/tier/tier-api.py"
    "/opt/d3kos/services/export/export-manager.py"
)

for script in "${service_scripts[@]}"; do
    if [ -f "$script" ]; then
        if [ -x "$script" ] || head -1 "$script" | grep -q "^#!"; then
            test_pass "Service script configured: $(basename $script)"
        else
            test_warn "Service script may not be executable: $script" "Check shebang or permissions"
        fi
    fi
done

# Test 11: OpenCPN detection (Tier 2 auto-upgrade)
echo ""
echo "Test 11: OpenCPN detection logic"
if command -v opencpn &> /dev/null; then
    test_pass "OpenCPN is installed (Tier 2 eligible)"
elif [ -d "/usr/share/opencpn" ] || [ -d "/opt/opencpn" ]; then
    test_pass "OpenCPN directory found (Tier 2 eligible)"
else
    test_warn "OpenCPN not detected" "System will remain at Tier 0/1 unless paid"
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
    echo -e "${GREEN}✓ All configuration checks passed${NC}"
    exit 0
else
    echo -e "${RED}✗ Some configuration issues - review failures above${NC}"
    exit 1
fi
