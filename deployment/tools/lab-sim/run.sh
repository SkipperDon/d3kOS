#!/usr/bin/env bash
# LAB-SIM runner.
#
# Streams labsim.py into python3 on the target Pi over SSH stdin.
# NOTHING is written to the Pi's disk — so the simulator can never end up on a
# cloned boat card. That is deliberate: a simulator that can start accidentally
# on a live vessel would inject fake position and depth data underway.
#
#   ./run.sh list
#   ./run.sh cruise
#   ./run.sh oil-critical
#   PI=172.20.10.8 ./run.sh depth-sweep     # boat Pi, when on the boat hotspot
set -euo pipefail

PI="${PI:-192.168.1.237}"
KEY="${KEY:-$HOME/.ssh/id_d3kos}"
USER_="${USER_:-d3kos}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

SCENARIO="${1:-list}"

exec ssh -i "$KEY" -o ConnectTimeout=10 "${USER_}@${PI}" \
     python3 - "$SCENARIO" < "$HERE/labsim.py"
