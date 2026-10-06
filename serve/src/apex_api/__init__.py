"""Apex API — one HTTP surface in front of the Apex store.

The console, the MCP server and any external consumer read through this layer
so that none of them needs a ClickHouse user. See app.create_app.
"""

from .app import create_app
from .config import ConfigError, Settings, load_settings

__all__ = ["create_app", "ConfigError", "Settings", "load_settings"]
