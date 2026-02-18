#!/bin/bash
# pre-distribution-checklist.sh - d3kOS Pre-Distribution Checklist
# Part of Distribution Prep Session 3: Testing & QA
# Verifies user data removed, no SSH keys, default credentials, version correct

set -e

# Test configuration
SCRIPT_NAME="Pre-Distribution Checklist"
TESTS_PASSED=0
TESTS_FAILED=0
WARNINGS=0
CRITICAL_FAILURES=0

# Expected version (update before each release)
EXPECTED_VERSION="1.0.3"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Output functions
print_header() {
    echo ""
    echo "========================================="
    echo "$SCRIPT_NAME"
    echo "========================================="
    echo ""
    echo -e "${MAGENTA}⚠  CRITICAL: This test MUST pass before distribution!${NC}"
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

test_critical() {
    echo -e "${MAGENTA}✗ CRITICAL FAIL${NC}: $1"
    echo -e "  ${MAGENTA}Reason${NC}: $2"
    echo -e "  ${MAGENTA}Action${NC}: $3"
    ((CRITICAL_FAILURES++))
}

test_warn() {
    echo -e "${YELLOW}⚠ WARN${NC}: $1"
    echo -e "  ${YELLOW}Info${NC}: $2"
    ((WARNINGS++))
}

print_header

# CRITICAL TEST 1: No user SSH keys in home directory
echo "Critical Test 1: SSH Keys Sanitization"
echo "---------------------------------------"

if [ -d "/home/d3kos/.ssh" ]; then
    # Check for private keys
    if ls /home/d3kos/.ssh/id_* &>/dev/null; then
        test_critical \
            "User SSH private keys found in /home/d3kos/.ssh/" \
            "Private keys must be removed before distribution" \
            "Run: rm -f /home/d3kos/.ssh/id_*"
    else
        test_pass "No user SSH private keys found"
    fi

    # Check for authorized_keys
    if [ -f "/home/d3kos/.ssh/authorized_keys" ]; then
        key_count=$(wc -l < /home/d3kos/.ssh/authorized_keys)
        if [ "$key_count" -gt 0 ]; then
            test_critical \
                "authorized_keys file contains $key_count key(s)" \
                "User-specific SSH keys must be removed" \
                "Run: rm /home/d3kos/.ssh/authorized_keys"
        else
            test_pass "authorized_keys file is empty"
        fi
    else
        test_pass "No authorized_keys file present"
    fi

    # Check for known_hosts
    if [ -f "/home/d3kos/.ssh/known_hosts" ]; then
        test_warn "known_hosts file present" "Consider removing user-specific SSH fingerprints"
    fi
else
    test_pass ".ssh directory does not exist"
fi

# CRITICAL TEST 2: No browser history or user data
echo ""
echo "Critical Test 2: Browser Data Sanitization"
echo "-------------------------------------------"

# Check Chromium user data
if [ -d "/home/d3kos/.config/chromium" ]; then
    # Check for history database
    if [ -f "/home/d3kos/.config/chromium/Default/History" ]; then
        test_critical \
            "Chromium browser history found" \
            "User browsing history must be removed" \
            "Run: rm -rf /home/d3kos/.config/chromium/Default/History*"
    else
        test_pass "No Chromium browser history"
    fi

    # Check for cookies
    if [ -f "/home/d3kos/.config/chromium/Default/Cookies" ]; then
        test_warn "Chromium cookies found" "Consider removing: rm /home/d3kos/.config/chromium/Default/Cookies"
    fi

    # Check for cache
    if [ -d "/home/d3kos/.config/chromium/Default/Cache" ]; then
        cache_size=$(du -sh /home/d3kos/.config/chromium/Default/Cache | awk '{print $1}')
        test_warn "Chromium cache present ($cache_size)" "Consider cleaning: rm -rf /home/d3kos/.config/chromium/Default/Cache"
    fi
else
    test_pass "No Chromium user data directory"
fi

# CRITICAL TEST 3: No personal data in boatlog
echo ""
echo "Critical Test 3: Boatlog Data Sanitization"
echo "-------------------------------------------"

if [ -f "/opt/d3kos/data/boatlog.db" ]; then
    # Check if database has entries
    if command -v sqlite3 &>/dev/null; then
        entry_count=$(sqlite3 /opt/d3kos/data/boatlog.db "SELECT COUNT(*) FROM boatlog_entries;" 2>/dev/null || echo "0")

        if [ "$entry_count" -gt 0 ]; then
            test_critical \
                "Boatlog database contains $entry_count user entries" \
                "Personal logs must be removed before distribution" \
                "Run: sqlite3 /opt/d3kos/data/boatlog.db 'DELETE FROM boatlog_entries;'"
        else
            test_pass "Boatlog database is empty (no user entries)"
        fi
    else
        test_warn "Cannot verify boatlog contents" "sqlite3 not available"
    fi
else
    test_pass "No boatlog database file (clean state)"
fi

# CRITICAL TEST 4: No personal data in AI conversation history
echo ""
echo "Critical Test 4: AI Conversation History Sanitization"
echo "------------------------------------------------------"

if [ -f "/opt/d3kos/data/conversation-history.db" ]; then
    if command -v sqlite3 &>/dev/null; then
        message_count=$(sqlite3 /opt/d3kos/data/conversation-history.db "SELECT COUNT(*) FROM messages;" 2>/dev/null || echo "0")

        if [ "$message_count" -gt 0 ]; then
            test_critical \
                "AI conversation history contains $message_count messages" \
                "User conversations must be removed before distribution" \
                "Run: sqlite3 /opt/d3kos/data/conversation-history.db 'DELETE FROM messages;'"
        else
            test_pass "AI conversation history is empty"
        fi
    fi
else
    test_pass "No AI conversation history database (clean state)"
fi

# CRITICAL TEST 5: No camera recordings or captures
echo ""
echo "Critical Test 5: Camera Data Sanitization"
echo "------------------------------------------"

if [ -d "/home/d3kos/camera-recordings" ]; then
    recording_count=$(find /home/d3kos/camera-recordings -name "*.mp4" 2>/dev/null | wc -l)
    capture_count=$(find /home/d3kos/camera-recordings/captures -name "*.jpg" 2>/dev/null | wc -l)

    if [ "$recording_count" -gt 0 ]; then
        test_critical \
            "Camera recordings directory contains $recording_count video files" \
            "User recordings must be removed" \
            "Run: rm -f /home/d3kos/camera-recordings/*.mp4"
    else
        test_pass "No camera recording files"
    fi

    if [ "$capture_count" -gt 0 ]; then
        test_critical \
            "Camera captures directory contains $capture_count image files" \
            "User captures must be removed" \
            "Run: rm -rf /home/d3kos/camera-recordings/captures/*"
    else
        test_pass "No camera capture files"
    fi
else
    test_pass "No camera recordings directory (clean state)"
fi

# CRITICAL TEST 6: Default credentials verification
echo ""
echo "Critical Test 6: Default Credentials"
echo "-------------------------------------"

# Check if default d3kos user exists
if id "d3kos" &>/dev/null; then
    test_pass "Default user 'd3kos' exists"
else
    test_critical \
        "Default user 'd3kos' does not exist" \
        "System must have default user for distribution" \
        "Create user with: sudo adduser d3kos"
fi

# Check if root login is disabled
if grep -q "^PermitRootLogin no" /etc/ssh/sshd_config 2>/dev/null; then
    test_pass "Root SSH login is disabled (security best practice)"
elif grep -q "^PermitRootLogin" /etc/ssh/sshd_config 2>/dev/null; then
    test_warn "Root SSH login may be enabled" "Consider setting: PermitRootLogin no"
else
    test_warn "Cannot verify root SSH login setting" "sshd_config not found or no explicit setting"
fi

# CRITICAL TEST 7: System version verification
echo ""
echo "Critical Test 7: System Version"
echo "--------------------------------"

if [ -f "/opt/d3kos/config/license.json" ]; then
    if command -v jq &>/dev/null; then
        current_version=$(jq -r '.version' /opt/d3kos/config/license.json 2>/dev/null || echo "unknown")

        if [ "$current_version" = "$EXPECTED_VERSION" ]; then
            test_pass "System version is correct: $current_version"
        else
            test_critical \
                "System version mismatch: $current_version (expected: $EXPECTED_VERSION)" \
                "Version must be updated before distribution" \
                "Update license.json with: jq '.version = \"$EXPECTED_VERSION\"' license.json > tmp && mv tmp license.json"
        fi
    else
        test_warn "Cannot verify system version" "jq not available"
    fi
else
    test_critical \
        "license.json file not found" \
        "Installation ID system not initialized" \
        "Run installation ID generation script first"
fi

# CRITICAL TEST 8: No personal Telegram credentials
echo ""
echo "Critical Test 8: Telegram Configuration Sanitization"
echo "-----------------------------------------------------"

if [ -f "/opt/d3kos/config/telegram-config.json" ]; then
    if command -v jq &>/dev/null; then
        bot_token=$(jq -r '.bot_token' /opt/d3kos/config/telegram-config.json 2>/dev/null || echo "")
        chat_id=$(jq -r '.chat_id' /opt/d3kos/config/telegram-config.json 2>/dev/null || echo "")

        if [ -n "$bot_token" ] && [ "$bot_token" != "YOUR_BOT_TOKEN_HERE" ]; then
            test_critical \
                "Telegram bot token is configured (user-specific)" \
                "Personal bot token must be removed" \
                "Reset to default: jq '.bot_token = \"YOUR_BOT_TOKEN_HERE\"' telegram-config.json > tmp && mv tmp telegram-config.json"
        else
            test_pass "Telegram bot token is at default (not configured)"
        fi

        if [ -n "$chat_id" ] && [ "$chat_id" != "YOUR_CHAT_ID_HERE" ]; then
            test_critical \
                "Telegram chat ID is configured (user-specific)" \
                "Personal chat ID must be removed" \
                "Reset to default: jq '.chat_id = \"YOUR_CHAT_ID_HERE\"' telegram-config.json > tmp && mv tmp telegram-config.json"
        else
            test_pass "Telegram chat ID is at default (not configured)"
        fi
    fi
else
    test_pass "No Telegram configuration file (clean state)"
fi

# CRITICAL TEST 9: No personal WiFi credentials
echo ""
echo "Critical Test 9: WiFi Credentials Sanitization"
echo "-----------------------------------------------"

if [ -d "/etc/NetworkManager/system-connections" ]; then
    wifi_count=$(ls /etc/NetworkManager/system-connections/*.nmconnection 2>/dev/null | wc -l || echo "0")

    if [ "$wifi_count" -gt 0 ]; then
        test_warn "Found $wifi_count saved WiFi connection(s)" "Consider removing user-specific networks before distribution"

        # List connections
        echo "  Saved connections:"
        ls /etc/NetworkManager/system-connections/*.nmconnection 2>/dev/null | while read conn; do
            echo "    - $(basename "$conn" .nmconnection)"
        done
    else
        test_pass "No saved WiFi connections (clean state)"
    fi
else
    test_pass "NetworkManager connections directory not found"
fi

# CRITICAL TEST 10: Installation ID is generic (not tied to this hardware)
echo ""
echo "Critical Test 10: Installation ID Reset"
echo "----------------------------------------"

if [ -f "/opt/d3kos/config/license.json" ]; then
    if command -v jq &>/dev/null; then
        install_id=$(jq -r '.installation_id' /opt/d3kos/config/license.json 2>/dev/null || echo "")

        # Installation ID should be regenerated on first boot
        # For distribution, we want a PLACEHOLDER or the ID should be regenerated
        test_warn "Installation ID present: $install_id" \
            "This will be regenerated on first boot of distributed image"

        # Check if first-boot service is enabled
        if systemctl list-unit-files | grep -q "d3kos-first-boot.service"; then
            if systemctl is-enabled --quiet d3kos-first-boot.service 2>/dev/null; then
                test_pass "First-boot service enabled (will regenerate installation ID)"
            else
                test_critical \
                    "First-boot service is NOT enabled" \
                    "Installation ID will not be regenerated on user's system" \
                    "Enable: sudo systemctl enable d3kos-first-boot.service"
            fi
        else
            test_critical \
                "First-boot service not found" \
                "Installation ID will not be regenerated" \
                "Install first-boot service before distribution"
        fi
    fi
fi

# CRITICAL TEST 11: No temporary files or logs with personal data
echo ""
echo "Critical Test 11: Temporary Files & Logs"
echo "-----------------------------------------"

# Check for large log files
if [ -d "/var/log" ]; then
    large_logs=$(find /var/log -type f -size +50M 2>/dev/null || true)

    if [ -n "$large_logs" ]; then
        test_warn "Large log files found (>50MB)" "Consider cleaning before distribution"
        echo "$large_logs" | while read log; do
            log_size=$(du -h "$log" | awk '{print $1}')
            echo "    - $log ($log_size)"
        done
    else
        test_pass "No excessively large log files"
    fi
fi

# Check /tmp for leftover data
if [ -d "/tmp" ]; then
    tmp_count=$(ls /tmp 2>/dev/null | wc -l)
    if [ "$tmp_count" -gt 10 ]; then
        test_warn "/tmp directory has $tmp_count items" "Consider cleaning before distribution"
    else
        test_pass "/tmp directory is relatively clean"
    fi
fi

# CRITICAL TEST 12: Default tier configuration
echo ""
echo "Critical Test 12: Default Tier Configuration"
echo "---------------------------------------------"

if [ -f "/opt/d3kos/config/license.json" ]; then
    if command -v jq &>/dev/null; then
        tier=$(jq -r '.tier' /opt/d3kos/config/license.json 2>/dev/null || echo "-1")

        if [ "$tier" = "0" ]; then
            test_pass "System configured for Tier 0 (default/free)"
        else
            test_warn "System is at Tier $tier" "Distribution should default to Tier 0, will upgrade based on OpenCPN detection"
        fi
    fi
fi

# Print summary
echo ""
echo "========================================="
echo "Distribution Checklist Summary"
echo "========================================="
echo -e "Tests Passed:        ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed:        ${RED}$TESTS_FAILED${NC}"
echo -e "Warnings:            ${YELLOW}$WARNINGS${NC}"
echo -e "CRITICAL Failures:   ${MAGENTA}$CRITICAL_FAILURES${NC}"
echo ""

# Exit code based on critical failures
if [ $CRITICAL_FAILURES -gt 0 ]; then
    echo -e "${MAGENTA}=========================================${NC}"
    echo -e "${MAGENTA}✗ DISTRIBUTION BLOCKED${NC}"
    echo -e "${MAGENTA}=========================================${NC}"
    echo -e "${MAGENTA}$CRITICAL_FAILURES critical issue(s) must be fixed before distribution!${NC}"
    echo ""
    echo "Review failures above and follow action items."
    echo ""
    exit 1
elif [ $TESTS_FAILED -gt 0 ]; then
    echo -e "${RED}✗ Some issues detected - review before distribution${NC}"
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠ $WARNINGS warning(s) - review recommended${NC}"
    echo -e "${GREEN}✓ No critical issues - safe to distribute${NC}"
    exit 0
else
    echo -e "${GREEN}=========================================${NC}"
    echo -e "${GREEN}✓ READY FOR DISTRIBUTION${NC}"
    echo -e "${GREEN}=========================================${NC}"
    echo -e "${GREEN}All checks passed! Image is clean and ready.${NC}"
    echo ""
    exit 0
fi
