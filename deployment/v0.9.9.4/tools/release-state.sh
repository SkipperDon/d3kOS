#!/usr/bin/env bash
# release-state.sh — three-way drift verifier: repo ↔ MANIFEST.md5 ↔ Pi
#
# Closes the gap that check-drift.sh leaves: a Pi matching a STALE manifest
# looks clean. This tool compares all three edges and reports each separately.
#
# Usage:
#   ./tools/release-state.sh
#   PI=172.20.10.8  ./tools/release-state.sh   # boat Pi on hotspot
#   PI=192.168.1.237 ./tools/release-state.sh   # lab Pi (default)
#
# Exit: 0 = clean (repo ↔ Pi identical, manifest current)
#       1 = drift found (drifted, missing, extra, or stale manifest)
#       2 = Pi unreachable or fatal setup error
set -uo pipefail

PI_HOST="${PI:-192.168.1.237}"
KEY="$HOME/.ssh/id_d3kos"
SSH_OPTS="-i $KEY -o ConnectTimeout=10 -o BatchMode=yes -o StrictHostKeyChecking=no"
REMOTE="d3kos@${PI_HOST}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MAN="$ROOT/MANIFEST.md5"

# colour helpers — stripped when stdout is not a tty
if [ -t 1 ]; then
  GRN='\033[0;32m'; RED='\033[0;31m'; YEL='\033[1;33m'; NC='\033[0m'
else
  GRN=''; RED=''; YEL=''; NC=''
fi

sec() { echo; echo "=== $* ==="; }
fail() { echo -e "${RED}FATAL: $*${NC}" >&2; exit 2; }

[ -f "$MAN" ] || fail "MANIFEST.md5 not found at $MAN"

# ── connectivity ────────────────────────────────────────────────────────────
sec "CONNECTIVITY"
# shellcheck disable=SC2086
if ! ssh $SSH_OPTS "$REMOTE" true 2>/dev/null; then
  echo -e "${RED}UNREACHABLE${NC}: $PI_HOST"
  echo
  echo "RESULT: UNREACHABLE — Pi $PI_HOST cannot be contacted"
  exit 2
fi
echo "Connected: $PI_HOST"

# ── build repo file list (Pi-relative paths for the deployable set) ─────────
# Only the dirs that mirror Pi filesystem paths — not tools/, README.md, MANIFEST.md5.
# Exclude .pyc and __pycache__: .gitignore keeps them out of git but they can exist on disk.
REPO_FILES_REL=$(cd "$ROOT" && find etc home opt var -type f \
  ! -name "*.pyc" ! -path "*/__pycache__/*" ! -name "*.template" 2>/dev/null | sort)
# Repo md5 for every file (computed once, used in both comparisons)
declare -A REPO_HASH
while read -r rp; do
  REPO_HASH["$rp"]=$(cd "$ROOT" && md5sum "$rp" | awk '{print $1}')
done <<< "$REPO_FILES_REL"

# ── comparison 1: repo ↔ MANIFEST ──────────────────────────────────────────
sec "COMPARISON 1: repo vs MANIFEST.md5"
declare -A MAN_HASH
while read -r h p; do MAN_HASH["$p"]="$h"; done < "$MAN"

man_ok=0; man_stale=0; man_only=0; repo_only=0
for rp in "${!REPO_HASH[@]}"; do
  rh="${REPO_HASH[$rp]}"
  mh="${MAN_HASH[$rp]:-}"
  if [ -z "$mh" ]; then
    printf '  REPO_ONLY (not in manifest): %s\n' "$rp"
    repo_only=$((repo_only+1))
  elif [ "$rh" != "$mh" ]; then
    printf '  MANIFEST_STALE:              %s\n' "$rp"
    man_stale=$((man_stale+1))
  else
    man_ok=$((man_ok+1))
  fi
done
for mp in "${!MAN_HASH[@]}"; do
  if [ -z "${REPO_HASH[$mp]:-}" ]; then
    printf '  MANIFEST_ONLY (not in repo): %s\n' "$mp"
    man_only=$((man_only+1))
  fi
done
printf '  matched: %d  stale: %d  manifest-only: %d  repo-only: %d\n' \
  "$man_ok" "$man_stale" "$man_only" "$repo_only"

# ── comparison 2: repo ↔ Pi (ONE ssh invocation) ───────────────────────────
sec "COMPARISON 2: repo vs Pi ($PI_HOST)"

# Stream Pi-absolute paths over stdin; remote loop emits "hash  /path" or "MISSING  /path"
# shellcheck disable=SC2086
remote_out=$(printf '%s\n' "$REPO_FILES_REL" | sed 's|^|/|' \
  | ssh $SSH_OPTS "$REMOTE" '
while IFS= read -r p; do
  if [ -f "$p" ]; then
    md5sum "$p" 2>/dev/null || printf "MISSING  %s\n" "$p"
  else
    printf "MISSING  %s\n" "$p"
  fi
done')

identical=0; drifted=0; missing_pi=0
while read -r rp; do
  pp="/$rp"
  repo_h="${REPO_HASH[$rp]}"
  # extract the one line for this pi-path
  remote_line=$(printf '%s\n' "$remote_out" | awk -v p="$pp" '$2==p{print;exit}')
  remote_h=$(printf '%s\n' "$remote_line" | awk '{print $1}')
  if [ -z "$remote_line" ] || [ "$remote_h" = "MISSING" ]; then
    printf '  MISSING_ON_PI:  %s\n' "$pp"
    missing_pi=$((missing_pi+1))
  elif [ "$remote_h" = "$repo_h" ]; then
    identical=$((identical+1))
  else
    printf '  DRIFTED:        %s\n' "$pp"
    drifted=$((drifted+1))
  fi
done <<< "$REPO_FILES_REL"
printf '  identical: %d  drifted: %d  missing: %d\n' "$identical" "$drifted" "$missing_pi"

# ── comparison 3: EXTRA_ON_PI ───────────────────────────────────────────────
sec "COMPARISON 3: EXTRA_ON_PI"

# Walk the d3kOS-specific directories on the Pi.
# /etc/systemd/system/ is NOT walked fully (thousands of non-d3kos units) —
# only d3kos-*.service files are checked there.
# Walk the directories we track in the repo, scoped to avoid Pi-local data/cache trees.
# Per-Pi runtime state (*.env, pytest caches, avnav charts/logs, SK runtime data) is
# explicitly excluded — those are expected Pi-only files, not orphan code.
# shellcheck disable=SC2086
pi_files=$(ssh $SSH_OPTS "$REMOTE" '
# Code directories: walk fully, exclude runtime caches and env configs
find /opt/d3kos/scripts /opt/d3kos/services /var/www/html \
     -type f 2>/dev/null \
| grep -v "__pycache__" | grep -v "\.bak" | grep -v "\.pre-" | grep -v "\.pyc$" \
| grep -v "\.pytest_cache/" | grep -v "/cache/" | grep -v "/config/.*\.env$"
# avnav: maxdepth 1 only — excludes charts/, log/, ochartsng/ data trees
find /var/lib/avnav -maxdepth 1 -type f 2>/dev/null \
| grep -v "\.bak" | grep -v "\.log$" | grep -v "\.ok$"
# .signalk: maxdepth 1 only — excludes node_modules/ and SK runtime subdirs
find /home/d3kos/.signalk -maxdepth 1 -type f 2>/dev/null \
| grep -v "\.bak" | grep -v "\.log$"
# etc: only d3kos service files — avoids thousands of non-d3kos systemd units
find /etc/systemd/system -maxdepth 1 -name "d3kos-*.service" -type f 2>/dev/null
' 2>/dev/null | sort)

# Build set of Pi-absolute repo paths for lookup
declare -A REPO_ABS
for rp in "${!REPO_HASH[@]}"; do REPO_ABS["/$rp"]=1; done

extra_pi=0
while IFS= read -r pp; do
  [ -z "$pp" ] && continue
  if [ -z "${REPO_ABS[$pp]:-}" ]; then
    printf '  EXTRA_ON_PI:    %s\n' "$pp"
    extra_pi=$((extra_pi+1))
  fi
done <<< "$pi_files"
printf '  extra: %d\n' "$extra_pi"

# ── comparison 4: invariant checks (content, not byte-hash) ─────────────────
# Per-Pi config files legitimately differ between Pis (see deployment/docs/PI_CONFIG_DELTA.md).
# These checks assert required values rather than byte-comparing the files.
sec "COMPARISON 4: INVARIANTS"

invariant_fail=0

# BUG-19/20 fix: avnav_server.xml must have fetchAis="true" and aisQueryPeriod="5"
# shellcheck disable=SC2086
avnav_fetchais=$(ssh $SSH_OPTS "$REMOTE" \
  'grep -c "fetchAis=\"true\"" /var/lib/avnav/avnav_server.xml 2>/dev/null || echo 0' 2>/dev/null)
# shellcheck disable=SC2086
avnav_period=$(ssh $SSH_OPTS "$REMOTE" \
  'grep -c "aisQueryPeriod=\"5\"" /var/lib/avnav/avnav_server.xml 2>/dev/null || echo 0' 2>/dev/null)
avnav_fetchais="${avnav_fetchais//[^0-9]/}"
avnav_period="${avnav_period//[^0-9]/}"
if [ "${avnav_fetchais:-0}" -ge 1 ] && [ "${avnav_period:-0}" -ge 1 ]; then
  echo "  OK  fetchAis=\"true\" + aisQueryPeriod=\"5\" present (BUG-19/20 fix confirmed)"
else
  printf "  ${RED}FAIL${NC} BUG-19/20: avnav_server.xml missing fetchAis or aisQueryPeriod on %s\n" "$PI_HOST"
  printf '       fetchAis="true" count: %s  aisQueryPeriod="5" count: %s\n' \
    "${avnav_fetchais:-?}" "${avnav_period:-?}"
  invariant_fail=$((invariant_fail+1))
fi

# ── summary ─────────────────────────────────────────────────────────────────
pi_ver=$(ssh $SSH_OPTS "$REMOTE" 'cat /opt/d3kos/config/version.txt 2>/dev/null | head -1' 2>/dev/null || echo 'unavailable')
manifest_problems=$((man_stale+man_only+repo_only))
pi_problems=$((drifted+missing_pi+extra_pi+invariant_fail))
total=$((manifest_problems+pi_problems))

echo
echo "============================================================"
printf 'repo↔manifest : %d ok, %d stale, %d manifest-only, %d repo-only\n' \
  "$man_ok" "$man_stale" "$man_only" "$repo_only"
printf 'repo↔Pi       : %d identical, %d drifted, %d missing\n' \
  "$identical" "$drifted" "$missing_pi"
printf 'extra on Pi   : %d\n' "$extra_pi"
printf 'invariants    : %d failed\n' "$invariant_fail"
printf 'Pi %-15s: version.txt = %s\n' "$PI_HOST" "$pi_ver"
echo "============================================================"

if [ "$total" -eq 0 ]; then
  echo -e "${GRN}RESULT: CLEAN — Pi $PI_HOST is running the canonical tree${NC}"
  exit 0
elif [ "$pi_problems" -gt 0 ]; then
  echo -e "${RED}RESULT: DRIFT ($drifted drifted, $missing_pi missing, $extra_pi extra) — Pi $PI_HOST is NOT running the canonical tree${NC}"
  exit 1
else
  echo -e "${YEL}RESULT: MANIFEST STALE ($man_stale stale, $man_only manifest-only, $repo_only repo-only) — regenerate MANIFEST.md5${NC}"
  exit 1
fi
