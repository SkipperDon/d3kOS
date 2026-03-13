"""
pytest configuration for d3kOS AI Bridge tests.

Adds the ai-bridge/ root to sys.path so that 'utils' and 'features'
are importable without installing the package.

Run from deployment/d3kOS/ai-bridge/:
    pip install pytest flask requests python-dotenv
    pytest tests/ -v
"""

import sys
import os

# ai-bridge/ directory (one level above this file)
_AI_BRIDGE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _AI_BRIDGE_ROOT not in sys.path:
    sys.path.insert(0, _AI_BRIDGE_ROOT)
