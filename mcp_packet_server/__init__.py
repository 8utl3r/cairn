"""
MCP Packet Server - Proof of Concept
A unified MCP server using IP packet-like communication to consolidate 137 tools into a few core tools.
"""

__version__ = "0.1.0"
__author__ = "Pete"

# Automatically load environment variables from .env if present
from pathlib import Path

try:
    from dotenv import load_dotenv  # type: ignore

    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
except ModuleNotFoundError:
    # dotenv not installed; continue without auto-loading
    pass
