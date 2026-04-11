"""Add repo-root tools/ to sys.path so linear_client can be imported.

Each script in this directory imports this module first (as
`import bootstrap  # noqa: F401`) before importing from linear_client.
"""

import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[4] / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))
