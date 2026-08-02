#!/usr/bin/env bash
# d3kOS — THE test runner. BUG-51.
#
# There was no single command that ran the whole suite, so every session ran
# whatever subset happened to work and reported that number as the total.
# "33/33", "36/36", "47/47" were honest arithmetic on a dishonest denominator.
#
# This script runs EVERY test file in tests/ across all three harnesses and
# prints one total. It fails if anything fails, and — the important part — it
# also fails if a known test file could not be EXECUTED. A file that cannot run
# is not a pass.
#
#   ./tests/run-all.sh                 # against the lab Pi
#   PI=172.20.10.8 ./tests/run-all.sh  # against the boat Pi, on its hotspot
#
# Exit 0 = every file ran and every test passed. Anything else = do not claim green.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
cd "$ROOT"

PI="${PI:-192.168.1.237}"
export BASE_URL="${BASE_URL:-http://${PI}:3000}"
export SK_URL="${SK_URL:-http://${PI}:8099}"

# Playwright's chromium needs libs that cannot be apt-installed in this WSL.
# The root/ level is easy to miss and omitting it fails silently — see BUG-51.
PW_LIBS="$HOME/.local/pw-libs/root/usr/lib/x86_64-linux-gnu"
[ -d "$PW_LIBS" ] && export LD_LIBRARY_PATH="$PW_LIBS:${LD_LIBRARY_PATH:-}"

RED=$'\033[31m'; GRN=$'\033[32m'; YEL=$'\033[33m'; BLD=$'\033[1m'; RST=$'\033[0m'
FAILED=0
declare -a NOT_RUN=()
declare -a FAILURES=()

hdr() { printf '\n%s──────────────────────────────────────────────────────────%s\n%s%s%s\n' "$BLD" "$RST" "$BLD" "$1" "$RST"; }

# ───────────────────────────── PREFLIGHT ─────────────────────────────
# A broken environment must never look like a passing suite. That is the whole
# point of BUG-51. If we cannot test, we say so loudly and stop.
hdr "PREFLIGHT"

preflight_fail() {
  printf '%s  PREFLIGHT FAILED: %s%s\n' "$RED" "$1" "$RST"
  printf '%s  Refusing to run. A partial run must not be reported as a pass.%s\n' "$RED" "$RST"
  exit 2
}

printf '  target Pi ............ %s\n' "$PI"
printf '  BASE_URL ............. %s\n' "$BASE_URL"

code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "$BASE_URL/" || echo 000)
if [ "$code" = "000" ]; then
  preflight_fail "$BASE_URL is unreachable. Is the Pi up and d3kos-dashboard running?"
fi
printf '  dashboard ............ %sreachable (HTTP %s)%s\n' "$GRN" "$code" "$RST"

sk=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "$SK_URL/signalk" || echo 000)
printf '  signal k ............. %s\n' "$([ "$sk" != "000" ] && echo "reachable (HTTP $sk)" || echo "${YEL}unreachable — SK-dependent tests will report honestly${RST}")"

if ! node -e "
const { chromium } = require('playwright');
chromium.launch().then(b => b.close()).then(() => process.exit(0)).catch(e => {
  console.error('    ' + String(e).split('\n')[0]); process.exit(1);
});" 2>&1; then
  preflight_fail "Chromium cannot launch. Browser tests would fail as if the CODE were broken.
  Expected libs at: $PW_LIBS
  Rebuild with: apt-get download libnspr4 libnss3 libasound2t64 && dpkg-deb -x <deb> ~/.local/pw-libs/root"
fi
printf '  chromium ............. %slaunches%s\n' "$GRN" "$RST"

# ───────────────────────────── PLAYWRIGHT ─────────────────────────────
hdr "PLAYWRIGHT  (tests/*.spec.ts)"
# --workers=1 is REQUIRED, not a preference. Several specs inject state into
# Signal K, which is shared global state on the Pi. Run in parallel they collide
# and produce flaky failures — bug16 failed in a full run and passed 6/6 twice in
# isolation. A runner that reports flaky results is not an honest runner. (BUG-51)
PW_OUT=$(npx playwright test tests/*.spec.ts --workers=1 --reporter=line 2>&1)
echo "$PW_OUT" | tail -n 25
PW_PASS=$(echo "$PW_OUT" | grep -oE '[0-9]+ passed' | tail -1 | grep -oE '[0-9]+' || echo 0)
PW_FAIL=$(echo "$PW_OUT" | grep -oE '[0-9]+ failed' | tail -1 | grep -oE '[0-9]+' || echo 0)
PW_SKIP=$(echo "$PW_OUT" | grep -oE '[0-9]+ skipped' | tail -1 | grep -oE '[0-9]+' || echo 0)
[ "${PW_FAIL:-0}" -gt 0 ] && { FAILED=1; FAILURES+=("playwright: $PW_FAIL failed"); }
[ "${PW_SKIP:-0}" -gt 0 ] && printf '%s  NOTE: %s skipped. A skip asserts nothing — check the skip condition.%s\n' "$YEL" "$PW_SKIP" "$RST"

# ───────────────────────────── NODE ─────────────────────────────
# .cjs only. A .js file here cannot run under "type": "module" — that is BUG-51
# fault 3, and it must be reported as NOT RUN rather than quietly skipped.
hdr "NODE  (tests/*.test.cjs)"
NODE_PASS=0; NODE_FAIL=0
for f in tests/*.test.cjs; do
  [ -e "$f" ] || continue
  if out=$(timeout 120 node "$f" 2>&1); then
    printf '  %s✓%s %s\n' "$GRN" "$RST" "$(basename "$f")"; NODE_PASS=$((NODE_PASS+1))
  else
    printf '  %s✗%s %s\n' "$RED" "$RST" "$(basename "$f")"
    echo "$out" | grep -E 'AssertionError|Error' | head -2 | sed 's/^/      /'
    NODE_FAIL=$((NODE_FAIL+1)); FAILED=1; FAILURES+=("node: $(basename "$f")")
  fi
done
for f in tests/*.test.js; do
  [ -e "$f" ] || continue
  printf '  %s!%s %s — CANNOT RUN (require() under "type":"module")\n' "$RED" "$RST" "$(basename "$f")"
  NOT_RUN+=("$(basename "$f")"); FAILED=1
done

# ───────────────────────────── PYTEST ─────────────────────────────
hdr "PYTEST  (tests/test_*.py)"
PY_PASS=0; PY_FAIL=0
for f in tests/test_*.py; do
  [ -e "$f" ] || continue
  out=$(timeout 180 python3 -m pytest "$f" -q 2>&1)
  line=$(echo "$out" | tail -1)
  p=$(echo "$line" | grep -oE '[0-9]+ passed' | grep -oE '[0-9]+' || echo 0)
  bad=$(echo "$line" | grep -cE 'failed|error' || true)
  PY_PASS=$((PY_PASS + p))
  if [ "$bad" -gt 0 ]; then
    printf '  %s✗%s %-38s %s\n' "$RED" "$RST" "$(basename "$f")" "$line"
    echo "$out" | grep -E 'ModuleNotFoundError|AssertionError' | head -2 | sed 's/^/      /'
    PY_FAIL=$((PY_FAIL+1)); FAILED=1; FAILURES+=("pytest: $(basename "$f")")
  else
    printf '  %s✓%s %-38s %s\n' "$GRN" "$RST" "$(basename "$f")" "$line"
  fi
done

# ───────────────────────────── TOTAL ─────────────────────────────
hdr "TOTAL"
TOTAL_PASS=$(( ${PW_PASS:-0} + NODE_PASS*0 + PY_PASS ))
printf '  playwright ........... %s passed, %s failed, %s skipped\n' "${PW_PASS:-0}" "${PW_FAIL:-0}" "${PW_SKIP:-0}"
printf '  node ................. %s files passed, %s files failed\n' "$NODE_PASS" "$NODE_FAIL"
printf '  pytest ............... %s passed across files, %s files with failures\n' "$PY_PASS" "$PY_FAIL"

if [ ${#NOT_RUN[@]} -gt 0 ]; then
  printf '\n%s  %s FILE(S) COULD NOT BE EXECUTED — these are NOT passes:%s\n' "$RED" "${#NOT_RUN[@]}" "$RST"
  for n in "${NOT_RUN[@]}"; do printf '    %s\n' "$n"; done
fi

echo
if [ "$FAILED" -eq 0 ]; then
  printf '%s  GREEN — every known test file executed and every test passed.%s\n\n' "$GRN" "$RST"
  exit 0
fi
printf '%s  NOT GREEN. Do not report this suite as passing.%s\n' "$RED" "$RST"
for f in "${FAILURES[@]}"; do printf '    %s\n' "$f"; done
echo
exit 1
