#!/usr/bin/env bash
# /opt/d3kos/scripts/hardware-probe.sh
# Single source of truth writer for /opt/d3kos/config/hardware-profile.json
set -uo pipefail

PROFILE=/opt/d3kos/config/hardware-profile.json
TMP="${PROFILE}.tmp.$$"
trap 'rm -f "$TMP"' EXIT

command -v jq >/dev/null || { echo "hardware-probe: jq missing" >&2; exit 1; }

dt() { tr -d '\0' < "$1" 2>/dev/null || true; }   # device-tree strings are NUL-terminated

# --- Platform ---
pi_model=$(dt /proc/device-tree/model); : "${pi_model:=unknown}"
if [[ "$pi_model" =~ Raspberry\ Pi\ ([0-9]+) ]]; then pi_gen="${BASH_REMATCH[1]}"; else pi_gen=0; fi
ram_kb=$(awk '/^MemTotal:/{print $2}' /proc/meminfo)
ram_mb=$(( ram_kb / 1024 ))
ram_gb_nominal=$(( (ram_mb + 512) / 1024 ))       # rounded, DISPLAY ONLY — gates use ram_mb

# --- HAT (REQ-HCD-009: probed at boot and on every scheduled re-probe; not hot-plugged) ---
hat_present=false; hat_product=""; hat_vendor=""; hat_pid=""; hat_ver=""; hat_class=""
if [ -d /proc/device-tree/hat ]; then
    hat_present=true
    hat_product=$(dt /proc/device-tree/hat/product)
    hat_vendor=$(dt  /proc/device-tree/hat/vendor)
    hat_pid=$(dt     /proc/device-tree/hat/product_id)
    hat_ver=$(dt     /proc/device-tree/hat/product_ver)
    case "$hat_product" in
        *"AI HAT+"*)   hat_class="hailo-ai-hat" ;;
        *"PiCAN-M"*)   hat_class="pican-m"      ;;
        *"PiCAN2"*)    hat_class="pican2"       ;;
        *"Waveshare"*) hat_class="waveshare-can";;
        *)             hat_class="unknown-hat"  ;;
    esac
fi

# --- Accelerators ---
classes=(); devices=()
add_accel() { classes+=("$1"); devices+=("$(jq -nc --arg t "$1" --arg n "$2" --arg b "$3" \
              '{type:$t,node:$n,bus:$b}')"); }

[ -c /dev/hailo0 ] && add_accel hailo-8l      /dev/hailo0 pcie
lsusb 2>/dev/null | grep -q '18d1:9302' && add_accel coral-usb      usb usb
lsusb 2>/dev/null | grep -q '18d1:9303' && add_accel coral-usb-mini usb usb
grep -qls '0x1e60' /sys/bus/pci/devices/*/vendor 2>/dev/null && add_accel hailo-8 pcie pcie

accel_present=false; [ ${#classes[@]} -gt 0 ] && accel_present=true
classes_json=$(printf '%s\n' "${classes[@]:-}" | jq -Rsc 'split("\n")|map(select(length>0))')
devices_json=$(printf '%s\n' "${devices[@]:-}" | jq -sc 'map(select(.!=null))' 2>/dev/null || echo '[]')

# --- probe_version: increments on EVERY write, per HCD-REQ-001 ---
current=$(jq -r '.probe_version // 0' "$PROFILE" 2>/dev/null || echo 0)
[[ "$current" =~ ^[0-9]+$ ]] || current=0

jq -n \
  --argjson probe_version "$(( current + 1 ))" \
  --arg     probed_at      "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --arg     pi_model       "$pi_model" \
  --argjson pi_gen         "$pi_gen" \
  --argjson ram_mb         "$ram_mb" \
  --argjson ram_gb_nominal "$ram_gb_nominal" \
  --argjson hat_present    "$hat_present" \
  --arg     hat_product    "$hat_product" \
  --arg     hat_vendor     "$hat_vendor" \
  --arg     hat_pid        "$hat_pid" \
  --arg     hat_ver        "$hat_ver" \
  --arg     hat_class      "$hat_class" \
  --argjson accel_present  "$accel_present" \
  --argjson accel_classes  "$classes_json" \
  --argjson accel_devices  "$devices_json" \
  '{
     probe_version: $probe_version,
     probed_at:     $probed_at,
     platform:  { pi_model:$pi_model, pi_gen:$pi_gen,
                  ram_mb:$ram_mb, ram_gb_nominal:$ram_gb_nominal },
     hat:       { present:$hat_present, product:$hat_product, vendor:$hat_vendor,
                  product_id:$hat_pid, product_ver:$hat_ver, hat_class:$hat_class },
     accelerator:{ present:$accel_present, accelerator_class:$accel_classes,
                   devices:$accel_devices }
   }
   | .content_hash = (del(.probe_version,.probed_at) | tojson | @base64)' > "$TMP"

mv "$TMP" "$PROFILE"          # atomic replace
chmod 644 "$PROFILE"
