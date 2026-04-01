#!/usr/bin/env python3
"""
Pi fix script — run directly on the Pi as d3kos user (Node-RED owner).
Removes 4 dead tabs from flows.json:
  - d3kOS Cloud Telemetry Push  (non-existent API, 63% CPU)
  - Community Engine Benchmark  (never built)
  - Community Boat Map          (never built)
  - Community Knowledge Log     (Watch node error loop)

Keeps: System tab only.

Usage: python3 fix_nodered_flows.py
"""

import json
import shutil
from pathlib import Path

FLOWS = Path('/home/d3kos/.node-red/flows.json')

# Backup
shutil.copy(FLOWS, FLOWS.with_suffix('.json.bak-tab-removal'))
print("Backup created.")

data = json.loads(FLOWS.read_text())

# Tabs to remove (by label — matches what was seen in S11 session)
DEAD_TABS = {
    'd3kOS Cloud Telemetry Push',
    'Community Engine Benchmark',
    'Community Boat Map',
    'Community Knowledge Log',
}

# Find the IDs of the dead tabs
dead_tab_ids = set()
for node in data:
    if node.get('type') == 'tab' and node.get('label') in DEAD_TABS:
        dead_tab_ids.add(node['id'])
        print(f"Marking for removal: tab '{node['label']}' id={node['id']}")

if not dead_tab_ids:
    print("WARNING: No matching dead tabs found. Check tab labels in flows.json.")
    import sys; sys.exit(1)

# Remove tabs and all nodes belonging to those tabs
original_count = len(data)
cleaned = [
    node for node in data
    if node.get('id') not in dead_tab_ids        # not the tab itself
    and node.get('z') not in dead_tab_ids         # not a node in the tab
]

removed = original_count - len(cleaned)
print(f"Removed {removed} nodes/tabs (was {original_count}, now {len(cleaned)}).")

FLOWS.write_text(json.dumps(cleaned, indent=2))
print("flows.json written.")

# Verify
remaining_tabs = [n for n in cleaned if n.get('type') == 'tab']
print(f"\nRemaining tabs ({len(remaining_tabs)}):")
for t in remaining_tabs:
    print(f"  '{t.get('label')}' id={t.get('id')} disabled={t.get('disabled', False)}")

print("\nDone. Run: sudo systemctl restart nodered")
print("Then verify: sudo systemctl status nodered")
