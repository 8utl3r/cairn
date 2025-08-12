"""
HTTP server wrapper for Cairn MCP Server
"""

import json
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any
import threading

from .server import SimpleMCPServer


class CairnHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Cairn MCP Server"""
    
    def __init__(self, *args, mcp_server: SimpleMCPServer, **kwargs):
        self.mcp_server = mcp_server
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            
            if path == "/":
                self._send_response(200, {"message": "Cairn MCP Server", "status": "running"})
            elif path == "/tools":
                tools = self.mcp_server.list_tools()
                self._send_response(200, {"tools": tools})
            elif path == "/resources":
                resources = self.mcp_server.list_resources()
                self._send_response(200, {"resources": resources})
            elif path.startswith("/resource/"):
                # Extract resource URI from path
                resource_uri = path.replace("/resource/", "")
                if resource_uri.startswith("cairn://"):
                    resource = self.mcp_server.get_resource(resource_uri)
                    if resource:
                        self._send_response(200, resource)
                    else:
                        self._send_response(404, {"error": "Resource not found"})
                else:
                    self._send_response(400, {"error": "Invalid resource URI"})
            else:
                self._send_response(404, {"error": "Endpoint not found"})
                
        except Exception as e:
            self._send_response(500, {"error": str(e)})
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            
            if path == "/tool":
                # Handle tool calls
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    body = self.rfile.read(content_length)
                    data = json.loads(body.decode('utf-8'))
                    
                    tool_name = data.get('name')
                    arguments = data.get('arguments', {})
                    
                    if not tool_name:
                        self._send_response(400, {"error": "Tool name is required"})
                        return
                    
                    # Run the tool call in an async context
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        result = loop.run_until_complete(
                            self.mcp_server.handle_tool_call(tool_name, arguments)
                        )
                        self._send_response(200, result)
                    finally:
                        loop.close()
                else:
                    self._send_response(400, {"error": "Request body is required"})
            else:
                self._send_response(404, {"error": "Endpoint not found"})
                
        except Exception as e:
            self._send_response(500, {"error": str(e)})
    
    def _send_response(self, status_code: int, data: Dict[str, Any]):
        """Send HTTP response with JSON data"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response = json.dumps(data, indent=2, default=str)
        self.wfile.write(response.encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Custom logging to avoid cluttering output"""
        pass


class CairnHTTPServer:
    """HTTP server wrapper for Cairn MCP Server"""
    
    def __init__(self, host: str = "localhost", port: int = 8000, db_path: str = "cairn.db"):
        self.host = host
        self.port = port
        self.mcp_server = SimpleMCPServer(db_path)
        self.http_server = None
    
    def start(self):
        """Start the HTTP server"""
        def handler_factory(*args, **kwargs):
            return CairnHTTPHandler(*args, mcp_server=self.mcp_server, **kwargs)
        
        self.http_server = HTTPServer((self.host, self.port), handler_factory)
        print(f"🚀 Cairn MCP Server running on http://{self.host}:{self.port}")
        print(f"📚 Available tools: {[tool['name'] for tool in self.mcp_server.list_tools()]}")
        print(f"🔗 Available resources: {[resource['uri'] for resource in self.mcp_server.list_resources()]}")
        print("\n📖 API Endpoints:")
        print(f"  GET  /                    - Server status")
        print(f"  GET  /tools               - List available tools")
        print(f"  GET  /resources           - List available resources")
        print(f"  GET  /resource/{{uri}}      - Get specific resource")
        print(f"  POST /tool                - Execute a tool")
        print("\n💡 Example tool call:")
        print(f"  curl -X POST http://{self.host}:{self.port}/tool \\")
        print(f"    -H 'Content-Type: application/json' \\")
        print(f"    -d '{{'name': 'create_path', 'arguments': {{'name': 'Test', 'description': 'Test path', 'steps': []}}}}'")
        
        try:
            self.http_server.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down Cairn MCP Server...")
            self.stop()
    
    def stop(self):
        """Stop the HTTP server"""
        if self.http_server:
            self.http_server.shutdown()
            self.http_server.server_close()


def main():
    """Main entry point for HTTP server"""
    server = CairnHTTPServer()
    server.start()


if __name__ == "__main__":
    main()
