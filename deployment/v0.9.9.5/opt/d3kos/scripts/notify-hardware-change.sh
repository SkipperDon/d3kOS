#!/usr/bin/env bash
# /opt/d3kos/scripts/notify-hardware-change.sh
exec 9>/run/d3kos-hw-notify.lock
flock 9
curl -fsS --max-time 3 -X POST http://127.0.0.1:3000/api/hardware/profile-updated || true
