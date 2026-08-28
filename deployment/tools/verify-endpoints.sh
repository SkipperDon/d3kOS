#!/usr/bin/env bash
# verify-endpoints.sh — asserts every atmyboat.com URL in the canonical Pi tree resolves (not 404).
#
# BUG-89 §5: verify-bug55.sh and release-state.sh both PASS while endpoints 404 — they check
# text identity, never whether a destination URL resolves. This script fills that gap.
#
# Usage: bash deployment/tools/verify-endpoints.sh
# Returns: exit 0 if all URLs return non-404; exit 1 if any URL is 404 or unreachable.
#
# Rules:
#   - Sequential requests with 1s delay (Wordfence rate-limit protection)
#   - Script excluded from its own grep scan (avoid self-match false positive)
#   - 401/405/200 are all acceptable — the URL resolves, just auth-gated or method-restricted
#   - 404 and connection failures are failures

set -euo pipefail

CANONICAL_TREE="deployment/v0.9.9.4/opt/d3kos/services"
FAILURES=0
CHECKED=0

# Extract unique atmyboat.com URLs from Python source files, excluding this script itself
URLS=$(grep -roh "https://atmyboat\.com[^'\"]*" \
    "$CANONICAL_TREE" \
    --include="*.py" \
    2>/dev/null | sort -u)

if [ -z "$URLS" ]; then
    echo "No atmyboat.com URLs found in $CANONICAL_TREE"
    exit 0
fi

echo "Checking atmyboat.com endpoints found in canonical Pi tree..."
echo "Sequential scan with 1s delay (Wordfence protection)"
echo ""

while IFS= read -r url; do
    # Skip incomplete URLs (e.g. string fragments with {variables})
    if echo "$url" | grep -qE '\{|\}'; then
        echo "  SKIP (template): $url"
        continue
    fi

    CHECKED=$((CHECKED + 1))
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
        --max-time 10 \
        -A "d3kOS-EndpointVerifier/1.0" \
        "$url" 2>/dev/null || echo "CONN_FAIL")

    if [ "$HTTP_CODE" = "404" ] || [ "$HTTP_CODE" = "CONN_FAIL" ]; then
        echo "  FAIL ($HTTP_CODE): $url"
        FAILURES=$((FAILURES + 1))
    else
        echo "  OK   ($HTTP_CODE): $url"
    fi

    sleep 1
done <<< "$URLS"

echo ""
echo "Checked: $CHECKED URLs — Failures: $FAILURES"

if [ "$FAILURES" -gt 0 ]; then
    echo "FAIL: $FAILURES endpoint(s) returned 404 or connection failure"
    exit 1
else
    echo "PASS: all endpoints resolve"
    exit 0
fi
