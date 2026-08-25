#!/bin/bash
# verify-bug74.sh — BUG-74: cloud-config.json not in .gitignore; template incomplete; mode 644
# Tests must FAIL before the fix and PASS after.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
GITIGNORE="$REPO_ROOT/.gitignore"
TEMPLATE="$REPO_ROOT/deployment/v0.9.4/pi_source/cloud-config.json"
PI_HOST="192.168.1.237"
PI_USER="d3kos"
PI_KEY="$HOME/.ssh/id_d3kos"
PI_FILE="/opt/d3kos/config/cloud-config.json"

PASS=0
FAIL=0

check() {
    local num="$1" desc="$2" result="$3"
    if [ "$result" = "pass" ]; then
        echo "T${num} PASS: ${desc}"
        PASS=$((PASS + 1))
    else
        echo "T${num} FAIL: ${desc}"
        FAIL=$((FAIL + 1))
    fi
}

# T1 — .gitignore contains cloud-config.json in both forms
if grep -q '^cloud-config\.json$' "$GITIGNORE" 2>/dev/null && \
   grep -q '^\*\*/config/cloud-config\.json$' "$GITIGNORE" 2>/dev/null; then
    check 1 ".gitignore contains cloud-config.json (bare and **/config/ forms)" pass
else
    check 1 ".gitignore contains cloud-config.json (bare and **/config/ forms)" fail
fi

# T2 — template contains all six required keys
ALL_KEYS=true
for key in amboat_api_key amboat_base_url poll_interval_seconds turn_username turn_credential device_token; do
    if ! grep -q "\"$key\"" "$TEMPLATE" 2>/dev/null; then
        ALL_KEYS=false
        break
    fi
done
if [ "$ALL_KEYS" = "true" ]; then
    check 2 "template contains all six required keys" pass
else
    check 2 "template contains all six required keys" fail
fi

# T3 — template's amboat_api_key is a placeholder (must not regress)
API_KEY_VAL=$(python3 -c "import json,sys; d=json.load(open('$TEMPLATE')); print(d.get('amboat_api_key',''))" 2>/dev/null || echo "")
if echo "$API_KEY_VAL" | grep -qiE 'placeholder|YOUR|CHANGE|example|REDACTED|^$'; then
    check 3 "template amboat_api_key is a placeholder (not a live key)" pass
else
    check 3 "template amboat_api_key is a placeholder (not a live key)" fail
fi

# T4 — template's device_token is "" (empty string, not a placeholder word)
DEVICE_TOKEN_VAL=$(python3 -c "import json,sys; d=json.load(open('$TEMPLATE')); print(repr(d.get('device_token','MISSING')))" 2>/dev/null || echo "MISSING")
if [ "$DEVICE_TOKEN_VAL" = "''" ]; then
    check 4 "template device_token is empty string (not a placeholder word)" pass
else
    check 4 "template device_token is empty string (not a placeholder word) — got: $DEVICE_TOKEN_VAL" fail
fi

# T5 — Pi file mode is 600
if ssh -i "$PI_KEY" -o ConnectTimeout=5 -o BatchMode=yes "${PI_USER}@${PI_HOST}" true 2>/dev/null; then
    MODE=$(ssh -i "$PI_KEY" "${PI_USER}@${PI_HOST}" "stat -c %a '$PI_FILE' 2>/dev/null" 2>/dev/null || echo "")
    if [ "$MODE" = "600" ]; then
        check 5 "Pi cloud-config.json mode is 600" pass
    else
        check 5 "Pi cloud-config.json mode is 600 (got: $MODE)" fail
    fi
else
    echo "T5 SKIP: Pi unreachable — cannot check file mode"
fi

# T6 — NEGATIVE: git check-ignore confirms the rule actually matches
# (a rule in the wrong section or with wrong glob does nothing)
TMPFILE=$(mktemp --suffix=cloud-config.json)
trap 'rm -f "$TMPFILE"' EXIT
if git -C "$REPO_ROOT" check-ignore -q "$TMPFILE" 2>/dev/null || \
   git -C "$REPO_ROOT" check-ignore -q "some/config/cloud-config.json" 2>/dev/null; then
    check 6 "NEGATIVE: git check-ignore matches cloud-config.json" pass
else
    check 6 "NEGATIVE: git check-ignore matches cloud-config.json" fail
fi

# T7 — services reading the file are active (post-deploy only, skip if Pi unreachable)
if ssh -i "$PI_KEY" -o ConnectTimeout=5 -o BatchMode=yes "${PI_USER}@${PI_HOST}" true 2>/dev/null; then
    SVCS="d3kos-cloud-agent d3kos-export-manager d3kos-live"
    ALL_ACTIVE=true
    for svc in $SVCS; do
        STATUS=$(ssh -i "$PI_KEY" "${PI_USER}@${PI_HOST}" "systemctl is-active $svc 2>/dev/null" 2>/dev/null || echo "unknown")
        if [ "$STATUS" != "active" ]; then
            echo "  NOTE: $svc is $STATUS"
            ALL_ACTIVE=false
        fi
    done
    if [ "$ALL_ACTIVE" = "true" ]; then
        check 7 "all services reading cloud-config.json are active" pass
    else
        check 7 "all services reading cloud-config.json are active" fail
    fi
else
    echo "T7 SKIP: Pi unreachable — run after deploy to verify services"
fi

echo ""
echo "Results: $PASS passed, $FAIL failed"
if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
exit 0
