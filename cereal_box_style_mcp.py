#!/usr/bin/env python3
"""Wrapper to run cereal box style MCP server with correct path."""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and expose the mcp object
from cereal_box_style_mcp.server import mcp

if __name__ == "__main__":
    mcp.run()
