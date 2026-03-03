#!/usr/bin/env bash
# d3kOS v0.9.2 — Preferences API Integration Tests
# Run AFTER deployment when Pi (192.168.1.237) is online.
# Usage: ./test_api.sh [PI_IP]

PI="${1:-192.168.1.237}"
SSH_KEY="${HOME}/.ssh/id_d3kos"
BASE="http://${PI}/api/preferences"
PASSED=0
FAILED=0

green() { printf '\033[0;32m  ✓ %s\033[0m\n' "$1"; }
red()   { printf '\033[0;31m  ✗ %s\033[0m\n' "$1"; }

check() {
  local desc="$1" expected="$2" actual="$3"
  if echo "$actual" | grep -q "$expected"; then
    green "$desc"
    PASSED=$((PASSED + 1))
  else
    red "$desc — expected to contain: $expected"
    echo "    Got: $actual"
    FAILED=$((FAILED + 1))
  fi
}

echo ""
echo "d3kOS v0.9.2 — Preferences API Integration Tests"
echo "Target: $BASE"
echo "=================================================="

# Test 1: GET returns valid JSON with imperial default
echo ""
echo "[GET /api/preferences]"
R=$(curl -sf "$BASE" 2>&1)
check "Returns 200 with JSON body"           "measurement_system" "$R"
check "Default is imperial"                  '"imperial"'          "$R"

# Test 2: POST switch to metric
echo ""
echo "[POST metric]"
R=$(curl -sf -X POST "$BASE" \
  -H "Content-Type: application/json" \
  -d '{"measurement_system": "metric"}' 2>&1)
check "POST metric → success:true"          '"success":[ ]*true'    "$R"
check "POST metric → measurement_system"    '"metric"'           "$R"

# Test 3: Verify persistence
echo ""
echo "[GET — verify metric persisted]"
R=$(curl -sf "$BASE" 2>&1)
check "Metric persisted after POST"         '"metric"'           "$R"

# Test 4: Invalid value rejected
echo ""
echo "[POST invalid value]"
HTTP=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE" \
  -H "Content-Type: application/json" \
  -d '{"measurement_system": "kelvin"}')
check "Invalid value returns 400"           "400"                "$HTTP"

# Test 5: Reset to imperial
echo ""
echo "[POST imperial — reset]"
R=$(curl -sf -X POST "$BASE" \
  -H "Content-Type: application/json" \
  -d '{"measurement_system": "imperial"}' 2>&1)
check "Reset to imperial → success"         '"success":[ ]*true'    "$R"
check "Reset to imperial → value"           '"imperial"'         "$R"

# Test 6: Health endpoint
echo ""
echo "[GET /health]"
R=$(curl -sf "http://${PI}:8107/health" 2>&1)
check "Health endpoint returns ok"          '"ok"'               "$R"
check "Health reports correct service"      '"preferences-api"'  "$R"
check "Health reports correct version"      '"0.9.2"'            "$R"

# Test 7: Service status (SSH)
echo ""
echo "[systemd service status]"
STATUS=$(ssh -i ${SSH_KEY} -o ConnectTimeout=5 -o StrictHostKeyChecking=no d3kos@"$PI" \
  "sudo systemctl is-active d3kos-preferences-api" 2>&1)
check "Service is active"                   "active"             "$STATUS"

# Test 8: Config file exists
echo ""
echo "[Config file]"
FILE=$(ssh -i ${SSH_KEY} -o ConnectTimeout=5 -o StrictHostKeyChecking=no d3kos@"$PI" \
  "cat /opt/d3kos/config/user-preferences.json" 2>&1)
check "Config file exists and is readable"  "measurement_system" "$FILE"

# Test 9: units.js deployed and served
echo ""
echo "[units.js deployment]"
JS=$(curl -sf "http://${PI}/js/units.js" 2>&1 | head -5)
check "units.js served by nginx"            "d3kOS Units"        "$JS"

# Test 10: units.js tests pass on Pi
echo ""
echo "[units.js test suite on Pi]"
RESULT=$(ssh -i ${SSH_KEY} -o ConnectTimeout=5 -o StrictHostKeyChecking=no d3kos@"$PI" \
  "node /home/d3kos/test_units.js 2>&1" 2>&1)
check "All unit tests passed on Pi"         "PASSED"             "$RESULT"

# Summary
echo ""
echo "=================================================="
echo "Results: ${PASSED} passed, ${FAILED} failed"
if [ "$FAILED" -eq 0 ]; then
  echo "ALL INTEGRATION TESTS PASSED ✓ — v0.9.2 Metric/Imperial ready"
  exit 0
else
  echo "FAILED: ${FAILED} test(s) — DO NOT TAG v0.9.2"
  exit 1
fi
