#!/usr/bin/env python3
"""
Main entry point for Cairn MCP Server
"""

import asyncio
import sys
from pathlib import Path

# Add the cairn package to the path
sys.path.insert(0, str(Path(__file__).parent))

from cairn.server import main


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down Cairn MCP Server...")
    except Exception as e:
        print(f"Error running Cairn MCP Server: {e}")
        sys.exit(1)
