#!/usr/bin/env bash
# configure-go2rtc.sh — resolve bow camera URL from slots/hardware and write go2rtc YAML
set -euo pipefail

SLOTS_JSON="/opt/d3kos/config/slots.json"
HARDWARE_JSON="/opt/d3kos/config/hardware.json"
YAML_OUT="/etc/go2rtc/go2rtc-d16.yaml"

if [ ! -f "$SLOTS_JSON" ]; then
    echo "ERROR: $SLOTS_JSON not found" >&2
    exit 1
fi
if [ ! -f "$HARDWARE_JSON" ]; then
    echo "ERROR: $HARDWARE_JSON not found" >&2
    exit 1
fi

# Find the slot with forward_watch role
HW_ID=$(jq -r '[.[] | select(.roles.forward_watch == true)][0].hardware_id // empty' "$SLOTS_JSON")
if [ -z "$HW_ID" ]; then
    echo "ERROR: no slot with forward_watch role found in $SLOTS_JSON" >&2
    exit 1
fi

# Resolve rtsp_url from hardware.json
RTSP_URL=$(jq -r --arg id "$HW_ID" '[.[] | select(.hardware_id == $id)][0].rtsp_url // empty' "$HARDWARE_JSON")
if [ -z "$RTSP_URL" ]; then
    echo "ERROR: hardware_id $HW_ID not found or has no rtsp_url in $HARDWARE_JSON" >&2
    exit 1
fi

# Redact password in any journal/stdout output — never log the real URL
REDACTED=$(echo "$RTSP_URL" | sed -E 's|rtsp://[^:]+:[^@]+@|rtsp://***:***@|')
echo "Configuring go2rtc with bow camera: $REDACTED"

# Write YAML under umask 077 so the file is never briefly world-readable
umask 077
mkdir -p "$(dirname "$YAML_OUT")"
cat > "$YAML_OUT" << YAML
# /etc/go2rtc/go2rtc-d16.yaml   —   written by configure-go2rtc.sh
api:
  listen: "127.0.0.1:1984"
rtsp:
  listen: "127.0.0.1:8554"
webrtc:
  candidates: ["127.0.0.1:8555"]
streams:
  d16_forward:
    - "${RTSP_URL}#video=copy"
log:
  level: warn
YAML


echo "go2rtc YAML written to $YAML_OUT (URL redacted in log)"
