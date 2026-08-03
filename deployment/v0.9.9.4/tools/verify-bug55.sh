#!/bin/bash
# verify-bug55.sh — BUG-55 guard test
#
# Everything must point at production (https://atmyboat.com). Nothing may point at
# https://atmyboat.com/staging.
#
# BUG-55 had two shapes:
#   Category A — 9 fallback defaults, config.get('amboat_base_url', '<staging>').
#                These resolved to production only because cloud-config.json set the
#                key. If that key ever went missing the device silently switched
#                environments with no error and no log line.
#   Category B — 5 hardcoded sites with no override at all, including the OTA version
#                check and the PWA's API_BASE.
#
# It also checks the fleet ingest path segment, which was independently wrong: the
# code default omitted /wp-content/themes/twentytwenty-child/ that fleet-push.env
# carried, so the default 404'd in either environment.
#
# Usage: ./verify-bug55.sh [host]     (default 192.168.1.237)
# Exit:  0 = all pass, 1 = one or more failed

set -u

HOST="${1:-192.168.1.237}"
SSH_KEY="$HOME/.ssh/id_d3kos"
SSH="ssh -i $SSH_KEY -o ConnectTimeout=10 -o StrictHostKeyChecking=no d3kos@$HOST"

# Resolve the canonical tree relative to this script, so it works from any cwd.
TREE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

pass=0
fail=0

check() {
  local name="$1" result="$2" detail="${3:-}"
  if [ "$result" = "0" ]; then
    printf 'PASS  %s\n' "$name"
    pass=$((pass + 1))
  else
    printf 'FAIL  %s\n' "$name"
    [ -n "$detail" ] && printf '      %s\n' "$detail"
    fail=$((fail + 1))
  fi
}

echo "BUG-55 production-endpoint guard — repo tree + $HOST"
echo "--------------------------------------------------------"

# 1 — canonical repo tree carries no staging URL (excluding backups).
#     This script is excluded from its own scan: it necessarily names the forbidden
#     string in its grep patterns and comments, and would otherwise always self-fail.
hits=$(grep -rn 'atmyboat\.com/staging' "$TREE" --exclude='verify-bug55.sh' 2>/dev/null | grep -v '\.bak' | wc -l)
[ "$hits" -eq 0 ]
check "repo tree has no atmyboat.com/staging" "$?" "$hits occurrence(s) found — run: grep -rn 'atmyboat.com/staging' $TREE"

# 2 — live Pi code and config carry no staging URL
pihits=$($SSH 'grep -rn "atmyboat\.com/staging" /opt/d3kos/services/ /opt/d3kos/config/ /var/www/html/ 2>/dev/null | grep -v "\.bak" | grep -v "\.pre-bug55" | wc -l' 2>/dev/null)
pihits="${pihits:-999}"
[ "$pihits" -eq 0 ]
check "lab Pi has no atmyboat.com/staging" "$?" "$pihits occurrence(s) still live on the Pi"

# 3 — fleet ingest URL carries the full theme path in the Pi env file.
#     Guards the path-segment defect, not just the hostname.
$SSH 'grep -q "^FLEET_INGEST_URL=https://atmyboat\.com/wp-content/themes/twentytwenty-child/mobile/fleet-ingest\.php$" /opt/d3kos/services/fleet/config/fleet-push.env'
check "fleet-push.env ingest URL is production + full path" "$?" \
      "fleet-push.env is Pi-only and NOT version-controlled — it will not survive a rebuild"

# 4 — the fleet code default agrees with the env file
grep -q "https://atmyboat\.com/wp-content/themes/twentytwenty-child/mobile/fleet-ingest\.php" \
     "$TREE/opt/d3kos/services/fleet/fleet_push_service.py"
check "fleet_push_service.py default matches fleet-push.env" "$?" \
      "code default and env file disagree — the default will 404"

echo "--------------------------------------------------------"
echo "BUG-55 production endpoints: $pass passed, $fail failed"
[ "$fail" -eq 0 ] || exit 1
exit 0
