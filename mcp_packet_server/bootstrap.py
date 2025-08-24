"""Bootstrap utilities for MCP Packet Server.

This module MUST be imported at the VERY top of any runnable entry-point
(e.g. `enhanced_server.py`, `server.py`, `mcp_server.py`).  It loads
environment variables from the repository-local `.env` file so secrets are
available without manual `source` steps, and without risking accidental git
commits.
"""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    # dotenv not installed; skip automatic loading
    load_dotenv = None  # type: ignore


def init_env():  # pragma: no cover
    """Load variables from `mcp_packet_server/.env` if present.

    Safe to call multiple times; subsequent invocations are no-ops.
    """
    if load_dotenv is None:
        return

    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        # Only call once per process
        if not os.getenv("_MCP_ENV_LOADED"):
            load_dotenv(dotenv_path=env_path, override=False)
            os.environ["_MCP_ENV_LOADED"] = "1"

