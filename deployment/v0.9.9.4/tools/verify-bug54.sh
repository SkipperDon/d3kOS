#!/bin/bash
# verify-bug54.sh — BUG-54 regression test
#
# Proves that d3kos-export-manager flushes stdout so the export worker's failure
# diagnostics actually reach the systemd journal.
#
# BUG-54 mechanism: export_worker.py reports every delivery failure with print().
# Under systemd, stdout is a socket, not a TTY, so CPython block-buffers it at 8 KB.
# The worker's "Uploading to…", "✗ Export upload failed: …" and "Archived failed
# export: …" lines were therefore trapped in the buffer and never appeared in the
# journal — while export-manager.py's logging calls (stderr, line-buffered) did.
# The result looked exactly like "the failure is not logged anywhere".
#
# Usage: ./verify-bug54.sh [host]     (default 192.168.1.237)
# Exit:  0 = all pass, 1 = one or more failed

set -u

HOST="${1:-192.168.1.237}"
SSH_KEY="$HOME/.ssh/id_d3kos"
SSH="ssh -i $SSH_KEY -o ConnectTimeout=10 -o StrictHostKeyChecking=no d3kos@$HOST"

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

echo "BUG-54 logging verification — $HOST"
echo "----------------------------------------"

# 1 — the unit file declares PYTHONUNBUFFERED
# Matches Environment=PYTHONUNBUFFERED=1 with or without surrounding quotes.
$SSH 'systemctl cat d3kos-export-manager 2>/dev/null' \
  | grep -Eq '^Environment=.*PYTHONUNBUFFERED=1'
check "unit declares PYTHONUNBUFFERED=1" "$?" \
      "add Environment=PYTHONUNBUFFERED=1 to the [Service] section"

# 2 — the RUNNING process actually has it.
# /proc/PID/environ is NUL-separated, so translate before matching. This is the
# assertion that matters: an edited unit file that was never daemon-reloaded and
# restarted would still pass test 1 and fail here.
$SSH 'PID=$(systemctl show -p MainPID --value d3kos-export-manager);
      [ -n "$PID" ] && [ "$PID" != "0" ] || exit 2;
      tr "\0" "\n" < /proc/$PID/environ | grep -q "^PYTHONUNBUFFERED=1$"'
check "running process has PYTHONUNBUFFERED=1" "$?" \
      "unit may be edited but not reloaded — run daemon-reload and restart"

# 3 — the service is actually up (a dead service trivially logs nothing)
$SSH 'systemctl is-active --quiet d3kos-export-manager'
check "d3kos-export-manager is active" "$?" "service is not running"

echo "----------------------------------------"
echo "BUG-54 logging: $pass passed, $fail failed"
[ "$fail" -eq 0 ] || exit 1
exit 0
