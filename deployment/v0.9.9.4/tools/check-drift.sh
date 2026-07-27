#!/usr/bin/env bash
# check-drift.sh — compare the deployed Pi against the canonical v0.9.9.4 tree.
#
# WHY THIS EXISTS: between April and July 2026 the lab Pi and the repo diverged
# silently because version.txt was never bumped and two source trees were both
# treated as canonical. This script makes that class of drift impossible to miss.
#
# Usage: ./tools/check-drift.sh [pi_host]     (default d3kos@192.168.1.237)
# Exit:  0 = no drift, 1 = drift found, 2 = could not reach the Pi
set -uo pipefail

PI="${1:-d3kos@192.168.1.237}"
KEY="$HOME/.ssh/id_d3kos"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MAN="$ROOT/MANIFEST.md5"

[ -f "$MAN" ] || { echo "FATAL: MANIFEST.md5 not found at $MAN"; exit 2; }
ssh -i "$KEY" -o ConnectTimeout=10 -o BatchMode=yes "$PI" true 2>/dev/null \
  || { echo "FATAL: cannot reach $PI"; exit 2; }

# Collect md5s of every deployed counterpart in ONE ssh round-trip.
remote_list=$(sed 's/^[0-9a-f]*  /\//' "$MAN")
remote_md5=$(printf '%s\n' "$remote_list" \
  | ssh -i "$KEY" "$PI" 'sudo xargs -d "\n" -r md5sum 2>/dev/null')

drift=0; missing=0; ok=0
while read -r hash relpath; do
  [ -z "${relpath:-}" ] && continue
  pipath="/$relpath"
  actual=$(printf '%s\n' "$remote_md5" | awk -v p="$pipath" '$2==p {print $1; exit}')
  if [ -z "$actual" ]; then
    printf 'MISSING ON PI  %s\n' "$pipath"; missing=$((missing+1))
  elif [ "$actual" != "$hash" ]; then
    printf 'DRIFT          %s\n' "$pipath"; drift=$((drift+1))
  else
    ok=$((ok+1))
  fi
done < "$MAN"

echo
echo "----------------------------------------------"
printf 'match: %d   drift: %d   missing: %d\n' "$ok" "$drift" "$missing"
echo "Pi version.txt: $(ssh -i "$KEY" "$PI" 'head -1 /opt/d3kos/config/version.txt' 2>/dev/null)"
echo "----------------------------------------------"
[ $((drift+missing)) -eq 0 ] && { echo "RESULT: NO DRIFT"; exit 0; }
echo "RESULT: DRIFT DETECTED — do not clone or release until resolved"; exit 1
