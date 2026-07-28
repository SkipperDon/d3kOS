#!/usr/bin/env bash
# verify-bug39.sh — Tier-1 §25.8 verification of a Tier-3 BUG-39 submission.
# Read-only. NEVER executes regenerate-identity.sh.
set -uo pipefail
cd "$(dirname "$0")/../../.." || exit 2
S=deployment/v0.9.9.4/opt/d3kos/services/identity/regenerate-identity.sh
U=deployment/v0.9.9.4/etc/systemd/system/d3kos-identity-regen.service
fail=0
chk(){ if [ "$2" = PASS ]; then printf '  \033[32mPASS\033[0m  %s\n' "$1"; else printf '  \033[31mFAIL\033[0m  %s — %s\n' "$1" "$3"; fail=1; fi; }
echo "── BUG-39 Tier-1 verification ─────────────────────────────"
[ -f "$S" ] && [ -f "$U" ] && chk "both deliverables exist" PASS || chk "both deliverables exist" FAIL "missing"

# license.json must never be a write TARGET (2>/dev/null on a read is not a write)
if grep -qE '(>[^&]|>>|tee|mv|cp|rm|sed -i)[^|]*license\.json' "$S"; then
  chk "license.json never written" FAIL "write path found"
else chk "license.json never written" PASS; fi
grep -q "json.load(open('/opt/d3kos/config/license.json'))" "$S" && chk "license.json read-only access only" PASS || chk "license.json read-only access only" FAIL "unexpected access"

# SSH: temp-then-verify-then-replace, never rm before a confirmed keygen
awk '/^for key_path in/,/^done/' "$S" > /tmp/sshblk
kg=$(grep -n 'ssh-keygen -t' /tmp/sshblk | head -1 | cut -d: -f1)
rm_=$(grep -n 'rm -f "\$key_path"' /tmp/sshblk | head -1 | cut -d: -f1)
if [ -n "${kg:-}" ] && [ -n "${rm_:-}" ] && [ "$rm_" -gt "$kg" ]; then chk "keygen precedes rm of the old key" PASS
else chk "keygen precedes rm of the old key" FAIL "rm at ${rm_:-?} vs keygen at ${kg:-?}"; fi
grep -q 'TEMP_KEY' /tmp/sshblk && chk "generates to a temp path first" PASS || chk "generates to a temp path first" FAIL "no temp path"
grep -q '\-s "\$TEMP_KEY"' /tmp/sshblk && chk "verifies new key non-empty before replace" PASS || chk "verifies new key non-empty before replace" FAIL "no -s check"
grep -q 'keeping original' /tmp/sshblk && chk "keeps original on failure" PASS || chk "keeps original on failure" FAIL "no fallback"

# created_at must end with Z, microseconds preserved
out=$(python3 -c "from datetime import datetime,timezone;print(datetime.now(timezone.utc).isoformat().replace('+00:00','Z'))")
grep -q "replace('+00:00', 'Z')" "$S" && python3 -c "
import re,sys; sys.exit(0 if re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z','$out') else 1)" \
  && chk "created_at is ISO-8601 with trailing Z" PASS || chk "created_at is ISO-8601 with trailing Z" FAIL "$out"

# sentinel: checked first, created last, guarded by failure flag
first=$(grep -n 'identity-regenerated' "$S" | head -1 | cut -d: -f1)
last=$(grep -n 'identity-regenerated' "$S" | tail -1 | cut -d: -f1)
[ "$first" -lt 30 ] && chk "sentinel checked early (line $first)" PASS || chk "sentinel checked early" FAIL "line $first"
grep -q 'SSH_REGEN_FAILED -ne 0' "$S" && chk "sentinel guarded by failure flag" PASS || chk "sentinel guarded by failure flag" FAIL "unguarded"
[ "$last" -gt "$first" ] && chk "sentinel created last (line $last)" PASS || chk "sentinel created last" FAIL "$last"

grep -qE '^set -u' "$S" && ! grep -qE '^set -e' "$S" && chk "set -u without set -e" PASS || chk "set -u without set -e" FAIL "wrong flags"
grep -q 'EUID' "$S" && chk "root check present" PASS || chk "root check present" FAIL "missing"
bash -n "$S" 2>/dev/null && chk "bash -n clean" PASS || chk "bash -n clean" FAIL "syntax"
[ "$(stat -c%a "$S")" = 755 ] && chk "executable (755)" PASS || chk "executable" FAIL "$(stat -c%a "$S")"
[ "$(grep -c '\.signalk' "$S")" = 0 ] && chk "no Signal K access" PASS || chk "no Signal K access" FAIL "present"
[ "$(grep -cE 'tune2fs|fatlabel|mlabel' "$S")" = 0 ] && chk "no filesystem-UUID tools" PASS || chk "no filesystem-UUID tools" FAIL "present"
grep -q 'proc/sys/kernel/random/uuid' "$S" && chk "kernel UUID source" PASS || chk "kernel UUID source" FAIL "missing"
grep -q 'pre-regen' "$S" && chk "device-token backed up" PASS || chk "device-token backed up" FAIL "no backup"
for d in Type=oneshot RemainAfterExit=yes 'ConditionPathExists=!/opt/d3kos/config/.identity-regenerated' WantedBy=multi-user.target; do
  grep -qF "$d" "$U" && chk "unit: $d" PASS || chk "unit: $d" FAIL "missing"
done
echo "───────────────────────────────────────────────────────────"
[ $fail -eq 0 ] && { echo "RESULT: ACCEPT"; exit 0; } || { echo "RESULT: REJECT"; exit 1; }
