#!/bin/bash
# test-bug-wait-for-signalk-url.sh
#
# Regression test for: wait-for-signalk.sh stale URL bug
#
# Bug:   wait-for-signalk.sh polled http://localhost:3000/signalk
#        Signal K migrated from :3000 -> :8099 on 2026-03-13
#        Node-RED stuck in start-pre (activating) indefinitely on every boot
#        Flask :3000 had no /signalk route -> 404 flood every 2s
#
# Fix:   URL updated to http://localhost:8099/signalk
#        /usr/local/bin/wait-for-signalk.sh on Pi
#
# This test would FAIL against the old script (localhost:3000)
# and PASS against the fixed script (localhost:8099)
#
# Run locally (checks repo copy):
#   bash tests/test-bug-wait-for-signalk-url.sh
#
# Run on Pi (checks live file):
#   ssh d3kos@192.168.1.237 'bash /tmp/test-bug-wait-for-signalk-url.sh'

PASS=0
FAIL=0

ok()   { echo "  PASS: $1"; ((PASS++)); }
fail() { echo "  FAIL: $1"; ((FAIL++)); }

echo "=== Regression: wait-for-signalk.sh URL ==="
echo ""

# ── Test 1: Pi live file uses correct port ──────────────────────────────────
if command -v ssh &>/dev/null; then
  SCRIPT_URL=$(ssh -i ~/.ssh/id_d3kos -o StrictHostKeyChecking=no \
    -o ConnectTimeout=5 d3kos@192.168.1.237 \
    "grep 'curl' /usr/local/bin/wait-for-signalk.sh 2>/dev/null" 2>/dev/null)

  if echo "$SCRIPT_URL" | grep -q 'localhost:8099/signalk'; then
    ok "Pi wait-for-signalk.sh uses localhost:8099/signalk"
  elif echo "$SCRIPT_URL" | grep -q 'localhost:3000/signalk'; then
    fail "Pi wait-for-signalk.sh still has stale localhost:3000/signalk — BUG NOT FIXED"
  else
    echo "  WARN: could not reach Pi or script not found (skipping Pi check)"
  fi
else
  echo "  WARN: ssh not available, skipping Pi live file check"
fi

# ── Test 2: Pi file must NOT reference port 3000 for signalk ────────────────
if command -v ssh &>/dev/null; then
  BAD=$(ssh -i ~/.ssh/id_d3kos -o StrictHostKeyChecking=no \
    -o ConnectTimeout=5 d3kos@192.168.1.237 \
    "grep -c 'localhost:3000/signalk' /usr/local/bin/wait-for-signalk.sh 2>/dev/null || echo 0" 2>/dev/null)

  if [[ "$BAD" == "0" ]]; then
    ok "Pi wait-for-signalk.sh contains no localhost:3000/signalk references"
  else
    fail "Pi wait-for-signalk.sh still contains $BAD stale localhost:3000/signalk reference(s)"
  fi
fi

# ── Test 3: Node-RED service is active on Pi ────────────────────────────────
if command -v ssh &>/dev/null; then
  NR_STATE=$(ssh -i ~/.ssh/id_d3kos -o StrictHostKeyChecking=no \
    -o ConnectTimeout=5 d3kos@192.168.1.237 \
    "systemctl is-active nodered 2>/dev/null" 2>/dev/null)

  if [[ "$NR_STATE" == "active" ]]; then
    ok "Node-RED service is active (was stuck in start-pre before fix)"
  else
    fail "Node-RED service state is '$NR_STATE' — expected 'active'"
  fi
fi

# ── Test 4: No /signalk 404s in Flask dashboard logs (last 10 lines) ─────────
if command -v ssh &>/dev/null; then
  FLOOD=$(ssh -i ~/.ssh/id_d3kos -o StrictHostKeyChecking=no \
    -o ConnectTimeout=5 d3kos@192.168.1.237 \
    "sudo journalctl -u d3kos-dashboard -n 10 --no-pager 2>/dev/null | grep -c 'GET /signalk' || echo 0" 2>/dev/null)

  if [[ "$FLOOD" -lt 3 ]]; then
    ok "Flask dashboard logs: /signalk 404 flood stopped (count in last 10 lines: $FLOOD)"
  else
    fail "Flask dashboard logs: still seeing $FLOOD /signalk 404s in last 10 lines"
  fi
fi

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
