"""Deprecated shim — import from linear_client instead.

Kept for one release so existing callers (phase scripts, third-party
vendored copies) keep working. Remove once every importer has been
updated to `from linear_client import ...`.
"""

from linear_client import *  # noqa: F401,F403
