#!/usr/bin/env python3
"""
MCP Packet Server - Model Context Protocol Implementation
Implements the MCP protocol for Cursor integration
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import Any, Dict

# Add current directory to path for imports
sys.path.insert(0, str(__file__).replace('/mcp_server.py', ''))

from bootstrap import init_env
from enhanced_server import EnhancedMCPServer

init_env()


class MCPServer:
    """MCP Protocol Server Implementation"""

    def __init__(self):
        """Initialize the MCP server"""
        self.server = EnhancedMCPServer(cache_policy="lfu", max_tools=80)
        self.request_id = 0

        print("🚀 MCP Packet Server initialized", file=sys.stderr)
        print(f"📊 Available tools: {len(self.server.tools)}", file=sys.stderr)
        print(f"🔧 Available services: {len(self.server.service_handlers)}", file=sys.stderr)

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests"""
        try:
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")

            if method == "initialize":
                return await self.initialize(request_id, params)
            elif method == "tools/list":
                return await self.list_tools(request_id)
            elif method == "tools/call":
                return await self.call_tool(request_id, params)
            elif method == "resources/list":
                return await self.list_resources(request_id)
            elif method == "resources/read":
                return await self.read_resource(request_id, params)
            else:
                return self.error_response(request_id, "MethodNotFound", f"Unknown method: {method}")

        except Exception as e:
            return self.error_response(request.get("id"), "InternalError", str(e))

    async def initialize(self, request_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialize request"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {}
                },
                "serverInfo": {
                    "name": "MCP Packet Server",
                    "version": "1.0.0"
                }
            }
        }

    async def list_tools(self, request_id: Any) -> Dict[str, Any]:
        """List available tools"""
        tools = []

        for tool_name, tool_info in self.server.tools.items():
            tools.append({
                "name": tool_name,
                "description": tool_info.get("description", ""),
                "inputSchema": tool_info.get("inputSchema", {})
            })

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": tools
            }
        }

    async def call_tool(self, request_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool"""
        try:
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            if tool_name not in self.server.tools:
                return self.error_response(request_id, "ToolNotFound", f"Tool not found: {tool_name}")

            # Execute the tool
            if tool_name == "execute_packet":
                result = await self.server._execute_packet(arguments)
            elif tool_name == "list_services":
                result = await self.server._list_services(arguments)
            elif tool_name == "get_service_schema":
                result = await self.server._get_service_schema(arguments)
            elif tool_name == "batch_execute":
                result = await self.server._batch_execute(arguments)
            elif tool_name == "get_packet_status":
                result = await self.server._get_packet_status(arguments)
            else:
                return self.error_response(request_id, "ToolNotFound", f"Tool not implemented: {tool_name}")

            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            }

        except Exception as e:
            return self.error_response(request_id, "ToolExecutionError", str(e))

    async def list_resources(self, request_id: Any) -> Dict[str, Any]:
        """List available resources"""
        resources = []

        for resource_name, resource_info in self.server.resources.items():
            resources.append({
                "uri": f"mcp://packet-server/{resource_name}",
                "name": resource_name,
                "description": resource_info.get("description", ""),
                "mimeType": resource_info.get("mimeType", "application/json")
            })

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "resources": resources
            }
        }

    async def read_resource(self, request_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read a specific resource"""
        try:
            uri = params.get("uri", "")

            if uri.startswith("mcp://packet-server/"):
                resource_name = uri.replace("mcp://packet-server/", "")

                if resource_name == "server_status":
                    content = {
                        "status": "running",
                        "timestamp": datetime.utcnow().isoformat(),
                        "tools_loaded": len(self.server.tool_manager.list_loaded_tools()),
                        "tools_registered": len(self.server.tool_manager.list_registered_tools()),
                        "services": list(self.server.service_handlers.keys())
                    }

                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "contents": [
                                {
                                    "uri": uri,
                                    "mimeType": "application/json",
                                    "text": json.dumps(content, indent=2)
                                }
                            ]
                        }
                    }
                else:
                    return self.error_response(request_id, "ResourceNotFound", f"Resource not found: {resource_name}")
            else:
                return self.error_response(request_id, "InvalidURI", f"Invalid URI: {uri}")

        except Exception as e:
            return self.error_response(request_id, "ResourceReadError", str(e))

    def error_response(self, request_id: Any, code: str, message: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }


async def main():
    """Main server loop"""
    server = MCPServer()

    print("🚀 MCP Packet Server starting...", file=sys.stderr)
    print("📡 Ready to receive MCP requests", file=sys.stderr)

    # Read from stdin, write to stdout (MCP protocol)
    while True:
        try:
            # Read request from stdin
            line = sys.stdin.readline()
            if not line:
                break

            line = line.strip()
            if not line:
                continue

            # Parse JSON request
            try:
                request = json.loads(line)
            except json.JSONDecodeError as e:
                print(json.dumps({
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": "ParseError",
                        "message": f"Invalid JSON: {e}"
                    }
                }), flush=True)
                continue

            # Handle request
            response = await server.handle_request(request)

            # Send response to stdout
            print(json.dumps(response), flush=True)

        except KeyboardInterrupt:
            print("🛑 Server interrupted", file=sys.stderr)
            break
        except Exception as e:
            print(f"❌ Server error: {e}", file=sys.stderr)
            error_response = {
                "jsonrpc": "2.0",
                "id": request.get("id") if 'request' in locals() else None,
                "error": {
                    "code": "InternalError",
                    "message": str(e)
                }
            }
            print(json.dumps(error_response), flush=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Server stopped", file=sys.stderr)
    except Exception as e:
        print(f"❌ Fatal error: {e}", file=sys.stderr)
        sys.exit(1)

