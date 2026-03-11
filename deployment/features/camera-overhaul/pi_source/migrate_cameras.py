#!/usr/bin/env python3
"""
migrate_cameras.py — One-time migration: cameras.json -> slots.json + hardware.json

Reads:   /opt/d3kos/config/cameras.json
Writes:  /opt/d3kos/config/slots.json
         /opt/d3kos/config/hardware.json
Renames: cameras.json -> cameras.json.bak

Safe to run multiple times — will skip if slots.json already exists,
unless --force is passed.

Deploy to Pi: /opt/d3kos/services/marine-vision/migrate_cameras.py
Run:          python3 /opt/d3kos/services/marine-vision/migrate_cameras.py
"""

import json
import os
import sys
import subprocess
from datetime import datetime, timezone
from typing import Optional

CAMERAS_JSON  = '/opt/d3kos/config/cameras.json'
SLOTS_JSON    = '/opt/d3kos/config/slots.json'
HARDWARE_JSON = '/opt/d3kos/config/hardware.json'
CAMERAS_BAK   = '/opt/d3kos/config/cameras.json.bak'


def get_mac_from_arp(ip: str) -> Optional[str]:
    """Try to read MAC address for an IP from the ARP table.

    Tries /proc/net/arp first (Linux kernel table), then falls back
    to the arp command. Returns uppercase MAC string or None if not found.
    Camera must be reachable on the network for ARP to have an entry.
    """
    # Method 1: kernel ARP table
    try:
        with open('/proc/net/arp') as f:
            for line in f:
                parts = line.split()
                # Format: IP  HW_type  Flags  HW_addr  Mask  Device
                if len(parts) >= 4 and parts[0] == ip:
                    mac = parts[3]
                    if mac != '00:00:00:00:00:00':
                        return mac.upper()
    except Exception:
        pass

    # Method 2: arp command fallback
    try:
        result = subprocess.run(
            ['arp', '-n', ip],
            capture_output=True, text=True, timeout=3
        )
        for line in result.stdout.splitlines():
            parts = line.split()
            for part in parts:
                # MAC addresses are 17 chars: AA:BB:CC:DD:EE:FF
                if ':' in part and len(part) == 17:
                    return part.upper()
    except Exception:
        pass

    return None


def mac_to_hardware_id(mac: str) -> str:
    """Convert MAC address to stable hardware_id.

    AA:BB:CC:DD:EE:FF -> hw_aa_bb_cc_dd_ee_ff
    hardware_id is stable even if the camera's IP changes (DHCP).
    """
    return 'hw_' + mac.replace(':', '_').lower()


def ip_to_fallback_id(ip: str) -> str:
    """Fallback hardware_id when MAC is unavailable (camera offline).

    10.42.0.100 -> hw_ip_10_42_0_100

    After Step 2 deploy, run Scan in Settings -> Camera Setup. The scan
    reads the real MAC and updates hardware.json. Then reassign the slot
    from the unassigned panel if needed.
    """
    return 'hw_ip_' + ip.replace('.', '_')


def main() -> None:
    force = '--force' in sys.argv

    # Guard: don't re-run unless forced
    if os.path.exists(SLOTS_JSON) and not force:
        print('slots.json already exists — migration already ran.')
        print('Pass --force to re-run and overwrite.')
        sys.exit(0)

    if not os.path.exists(CAMERAS_JSON):
        print(f'ERROR: cameras.json not found at {CAMERAS_JSON}')
        print('Nothing to migrate.')
        sys.exit(1)

    with open(CAMERAS_JSON) as f:
        cfg = json.load(f)

    cameras = cfg.get('cameras', [])
    print(f'Found {len(cameras)} camera(s) in cameras.json')
    print()

    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')
    slots = []
    hardware = []
    mac_warnings = []

    for i, cam in enumerate(cameras):
        cam_id = cam.get('id', f'camera_{i}')
        # Prefer explicit name, fall back to location, then slugged id
        label  = cam.get('name') or cam.get('location') or cam_id.replace('_', ' ').title()
        ip     = cam.get('ip', '')
        rtsp   = cam.get('rtsp_url', '')
        model  = cam.get('model', 'Unknown')
        detect = bool(cam.get('detection_enabled', False))

        # Spec rule: the bow slot gets forward_watch + active_default.
        # This is the camera pointed forward for collision avoidance —
        # it becomes the primary navigation view regardless of which camera
        # was previously set as active_camera in cameras.json.
        position         = cam.get('position', cam_id)
        is_bow           = (position == 'bow' or cam_id == 'bow')
        is_forward_watch = is_bow
        is_active_default = is_bow

        print(f'  [{cam_id}] IP={ip}  label="{label}"')
        print(f'           Looking up MAC...')
        mac = get_mac_from_arp(ip)

        if mac:
            hardware_id = mac_to_hardware_id(mac)
            print(f'           MAC={mac}  hardware_id={hardware_id}')
        else:
            hardware_id = ip_to_fallback_id(ip)
            mac = 'UNKNOWN'
            mac_warnings.append(cam_id)
            print(f'           MAC not found (camera may be offline)')
            print(f'           Using fallback hardware_id={hardware_id}')
        print()

        slots.append({
            'slot_id':       cam_id,
            'label':         label,
            'display_order': i + 1,
            'roles': {
                'forward_watch':  is_forward_watch,
                'fish_detection': detect,
                'active_default': is_active_default,
                'display_in_grid': True,
            },
            'hardware_id': hardware_id,
            'assigned':    True,
            'created':     now,
        })

        hardware.append({
            'hardware_id':      hardware_id,
            'mac':              mac,
            'ip':               ip,
            'model':            model,
            'rtsp_url':         rtsp,
            'last_seen':        now,
            'status':           'online',
            'assigned_to_slot': cam_id,
        })

    # Write slots.json
    with open(SLOTS_JSON, 'w') as f:
        json.dump(slots, f, indent=2)
    print(f'Written: {SLOTS_JSON}')

    # Write hardware.json
    with open(HARDWARE_JSON, 'w') as f:
        json.dump(hardware, f, indent=2)
    print(f'Written: {HARDWARE_JSON}')

    # Rename cameras.json -> cameras.json.bak (keep as rollback)
    if os.path.exists(CAMERAS_BAK):
        os.remove(CAMERAS_BAK)
    os.rename(CAMERAS_JSON, CAMERAS_BAK)
    print(f'Renamed: cameras.json -> cameras.json.bak')
    print()

    # Summary
    print('=== Migration Summary ===')
    for s in slots:
        hw_entry = next(h for h in hardware if h['hardware_id'] == s['hardware_id'])
        active_roles = [k for k, v in s['roles'].items() if v]
        print(f"  Slot '{s['slot_id']}' ({s['label']})")
        print(f"    hardware_id  : {s['hardware_id']}")
        print(f"    MAC          : {hw_entry['mac']}")
        print(f"    IP           : {hw_entry['ip']}")
        print(f"    roles        : {', '.join(active_roles)}")
        print()

    if mac_warnings:
        print('WARNING: MAC address not resolved for the following slot(s):')
        for cid in mac_warnings:
            print(f'  - {cid}')
        print()
        print('The hardware_id for these slots uses the IP as a fallback identifier.')
        print('After Step 2 (camera_stream_manager.py) is deployed:')
        print('  1. Open Settings -> Camera Setup')
        print('  2. Tap [Scan for Cameras]')
        print('  3. The scan reads the real MAC and updates hardware.json')
        print('  4. If the slot shows unassigned, tap [Assign to Position] to relink it')
        print()

    print('Migration complete.')
    print('Next step: deploy camera_stream_manager.py (Step 2)')
    print('Verify the existing camera feed is still working before proceeding.')


if __name__ == '__main__':
    main()
