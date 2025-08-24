#!/bin/bash

# MCP Packet Server Launch Script
# This script starts the MCP server for Cursor integration

echo "🚀 Starting MCP Packet Server..."
echo "📁 Working directory: $(pwd)"
echo "🐍 Python version: $(python3 --version)"
echo ""

# Set the Python path
export PYTHONPATH="$(pwd):$PYTHONPATH"

# Start the MCP server
echo "📡 Starting MCP server..."
echo "🔗 Ready to accept connections from Cursor"
echo ""

# Run the MCP server
python3 mcp_server.py

