#!/bin/bash
# TDD verifier for BUG-65: license.json mode+ownership + tier audit fields
# Static analysis only — no live Pi required.
# All tests must pass before BUG-65 is considered fixed.
set -euo pipefail

PASS=0; FAIL=0
check() {
    local id="$1" desc="$2" result="$3"
    if [ "$result" = "0" ]; then
        echo "  PASS T${id}: ${desc}"
        PASS=$((PASS+1))
    else
        echo "  FAIL T${id}: ${desc}"
        FAIL=$((FAIL+1))
    fi
}

CANONICAL="deployment/v0.9.9.4"
FIRST_BOOT="${CANONICAL}/opt/d3kos/scripts/first-boot-setup.sh"
SANITIZE="${CANONICAL}/opt/d3kos/scripts/sanitize.sh"
EXPORT_WORKER="${CANONICAL}/opt/d3kos/services/export/export_worker.py"

echo "=== BUG-65 TDD Verifier ==="
echo ""
echo "--- File presence ---"

# T1: first-boot-setup.sh exists in canonical tree
check 1 "first-boot-setup.sh exists in canonical tree" \
    "$([ -f "$FIRST_BOOT" ] && echo 0 || echo 1)"

# T2: sanitize.sh exists in canonical tree
check 2 "sanitize.sh exists in canonical tree" \
    "$([ -f "$SANITIZE" ] && echo 0 || echo 1)"

# T3: export_worker.py exists in canonical tree
check 3 "export_worker.py exists in canonical tree" \
    "$([ -f "$EXPORT_WORKER" ] && echo 0 || echo 1)"

echo ""
echo "--- first-boot-setup.sh: chmod 600 (not 644) on license.json ---"

# T4: first-boot-setup.sh contains chmod 600 on license.json
check 4 "first-boot-setup.sh has chmod 600 on license.json" \
    "$(grep -qE 'chmod 600.*/opt/d3kos/config/license\.json' "$FIRST_BOOT" && echo 0 || echo 1)"

# T5: first-boot-setup.sh does NOT have chmod 644 on license.json (the bug is gone)
# Using ! grep for negative test — avoids pipefail issues
check 5 "first-boot-setup.sh does NOT have chmod 644 on license.json" \
    "$(! grep -qE 'chmod 644.*/opt/d3kos/config/license\.json' "$FIRST_BOOT" && echo 0 || echo 1)"

# T6: BUG-65 trap guard — chown d3kos:d3kos appears before chmod 600 on license.json
# A naive chmod 600 without chown d3kos:d3kos makes root:root 600 → d3kos cannot read it
check 6 "first-boot-setup.sh has chown d3kos:d3kos on license.json" \
    "$(grep -qE 'chown d3kos:d3kos.*/opt/d3kos/config/license\.json' "$FIRST_BOOT" && echo 0 || echo 1)"

# T7: STEP 6 in first-boot-setup.sh re-asserts chmod 600 (defense against future regressions)
# The chown -R in STEP 6 changes ownership but not mode; the re-assert is the guard.
check 7 "first-boot-setup.sh re-asserts chmod 600 after chown -R in STEP 6" \
    "$(awk '/STEP 6/,/STEP 7/' "$FIRST_BOOT" | grep -qE 'chmod 600.*license\.json' && echo 0 || echo 1)"

echo ""
echo "--- sanitize.sh: chmod 600 (BUG-78 / BUG-65 D3 confirmation) ---"

# T8: sanitize.sh has chmod 600 on license.json (BUG-78 already fixed this)
check 8 "sanitize.sh has chmod 600 on license.json (BUG-78 guard)" \
    "$(grep -qE 'chmod 600.*LICENSE_FILE|chmod 600.*license\.json' "$SANITIZE" && echo 0 || echo 1)"

# T9: sanitize.sh does NOT have chmod 644 on license.json
check 9 "sanitize.sh does NOT have chmod 644 on license.json" \
    "$(! grep -qE 'chmod 644.*LICENSE_FILE|chmod 644.*license\.json' "$SANITIZE" && echo 0 || echo 1)"

echo ""
echo "--- export_worker.py: tier audit fields in _build_ingress_payload() ---"

# T10: tier_claimed field in export_worker.py
check 10 "export_worker.py sets tier_claimed in payload" \
    "$(grep -q "tier_claimed" "$EXPORT_WORKER" && echo 0 || echo 1)"

# T11: tier_detected field in export_worker.py
check 11 "export_worker.py sets tier_detected in payload" \
    "$(grep -q "tier_detected" "$EXPORT_WORKER" && echo 0 || echo 1)"

# T12: opencpn_present field in export_worker.py
check 12 "export_worker.py sets opencpn_present in payload" \
    "$(grep -q "opencpn_present" "$EXPORT_WORKER" && echo 0 || echo 1)"

# T13: subscription_key_present field in export_worker.py
check 13 "export_worker.py sets subscription_key_present in payload" \
    "$(grep -q "subscription_key_present" "$EXPORT_WORKER" && echo 0 || echo 1)"

# T14: Tier parsing handles both int 3 and string "T3" (BUG-77 overlap — confirm)
check 14 "export_worker.py handles both int and string tier forms" \
    "$(grep -qE "startswith\(['\"]T['\"]|T3|tier\[1:\]" "$EXPORT_WORKER" && echo 0 || echo 1)"

echo ""
echo "--- Summary ---"
echo "  PASS: ${PASS}"
echo "  FAIL: ${FAIL}"
echo "  TOTAL: $((PASS+FAIL))"
echo ""

if [ "$FAIL" -gt 0 ]; then
    echo "RESULT: FAIL — ${FAIL} test(s) failed"
    exit 1
else
    echo "RESULT: PASS — all ${PASS} tests passed"
    exit 0
fi
