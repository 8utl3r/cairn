"""
Enhanced MCP Packet Server with Dynamic Tool Management
Integrates packet-based communication with intelligent tool loading/unloading
"""

import asyncio
import json
import time
from typing import Any, Dict, List, Optional
from datetime import datetime

from packet import MCPPacket, PacketResponse, PacketStatus
from service_handlers import (
    TodoistServiceHandler, 
    GoogleCalendarServiceHandler, 
    GmailServiceHandler
)
from dynamic_tool_manager import DynamicToolManager


class EnhancedMCPServer:
    """
    Enhanced MCP server with dynamic tool management
    
    Features:
    - Packet-based communication (5 core tools)
    - Dynamic tool loading/unloading
    - Intelligent eviction policies (LRU/LFU)
    - Configurable tool limits
    - Memory optimization
    - Performance monitoring
    """
    
    def __init__(self, cache_policy: str = "lfu", max_tools: int = 80):
        """
        Initialize enhanced MCP server
        
        Args:
            cache_policy: "lru" (Least Recently Used) or "lfu" (Least Frequently Used)
            max_tools: Maximum number of tools to keep in memory
        """
        # Initialize dynamic tool manager
        self.tool_manager = DynamicToolManager(cache_policy=cache_policy, max_tools=max_tools)
        
        # Service handlers (always loaded)
        self.service_handlers = {
            'todoist': TodoistServiceHandler(),
            'gcal': GoogleCalendarServiceHandler(),
            'gmail': GmailServiceHandler()
        }
        
        # Register all 137 individual tools for dynamic loading
        self._register_all_tools()
        
        # Packet execution tracking
        self.packet_queue = {}
        self.execution_history = {}
        
        # Register core tools (always loaded)
        self.tools = self._register_core_tools()
        self.resources = self._register_resources()
        
        print(f"🚀 Enhanced MCP Server initialized with {cache_policy.upper()} policy")
        print(f"📊 Tool limit: {max_tools}")
        print(f"🔧 Available services: {len(self.service_handlers)}")
    
    def _register_all_tools(self):
        """Register all 137 individual tools for dynamic loading"""
        
        # Todoist tools (24 total)
        todoist_tools = [
            # Task operations
            ("create_todoist_task", "todoist"),
            ("read_todoist_task", "todoist"),
            ("update_todoist_task", "todoist"),
            ("delete_todoist_task", "todoist"),
            ("list_todoist_tasks", "todoist"),
            ("search_todoist_tasks", "todoist"),
            
            # Project operations
            ("create_todoist_project", "todoist"),
            ("read_todoist_project", "todoist"),
            ("update_todoist_project", "todoist"),
            ("delete_todoist_project", "todoist"),
            ("list_todoist_projects", "todoist"),
            ("search_todoist_projects", "todoist"),
            
            # Label operations
            ("create_todoist_label", "todoist"),
            ("read_todoist_label", "todoist"),
            ("update_todoist_label", "todoist"),
            ("delete_todoist_label", "todoist"),
            ("list_todoist_labels", "todoist"),
            ("search_todoist_labels", "todoist"),
            
            # Comment operations
            ("create_todoist_comment", "todoist"),
            ("read_todoist_comment", "todoist"),
            ("update_todoist_comment", "todoist"),
            ("delete_todoist_comment", "todoist"),
            ("list_todoist_comments", "todoist"),
            ("search_todoist_comments", "todoist"),
        ]
        
        # Google Calendar tools (24 total)
        gcal_tools = [
            # Event operations
            ("create_gcal_event", "gcal"),
            ("read_gcal_event", "gcal"),
            ("update_gcal_event", "gcal"),
            ("delete_gcal_event", "gcal"),
            ("list_gcal_events", "gcal"),
            ("search_gcal_events", "gcal"),
            
            # Calendar operations
            ("create_gcal_calendar", "gcal"),
            ("read_gcal_calendar", "gcal"),
            ("update_gcal_calendar", "gcal"),
            ("delete_gcal_calendar", "gcal"),
            ("list_gcal_calendars", "gcal"),
            ("search_gcal_calendars", "gcal"),
            
            # Reminder operations
            ("create_gcal_reminder", "gcal"),
            ("read_gcal_reminder", "gcal"),
            ("update_gcal_reminder", "gcal"),
            ("delete_gcal_reminder", "gcal"),
            ("list_gcal_reminders", "gcal"),
            ("search_gcal_reminders", "gcal"),
            
            # Additional operations
            ("get_gcal_free_busy", "gcal"),
            ("get_gcal_events_today", "gcal"),
            ("get_gcal_upcoming_events", "gcal"),
            ("get_gcal_calendar_acl", "gcal"),
            ("share_gcal_calendar", "gcal"),
            ("move_gcal_event", "gcal"),
        ]
        
        # Gmail tools (24 total)
        gmail_tools = [
            # Email operations
            ("create_gmail_email", "gmail"),
            ("read_gmail_email", "gmail"),
            ("update_gmail_email", "gmail"),
            ("delete_gmail_email", "gmail"),
            ("list_gmail_emails", "gmail"),
            ("search_gmail_emails", "gmail"),
            
            # Label operations
            ("create_gmail_label", "gmail"),
            ("read_gmail_label", "gmail"),
            ("update_gmail_label", "gmail"),
            ("delete_gmail_label", "gmail"),
            ("list_gmail_labels", "gmail"),
            ("search_gmail_labels", "gmail"),
            
            # Attachment operations
            ("create_gmail_attachment", "gmail"),
            ("read_gmail_attachment", "gmail"),
            ("update_gmail_attachment", "gmail"),
            ("delete_gmail_attachment", "gmail"),
            ("list_gmail_attachments", "gmail"),
            ("search_gmail_attachments", "gmail"),
            
            # Additional operations
            ("mark_gmail_read", "gmail"),
            ("mark_gmail_unread", "gmail"),
            ("get_gmail_unread", "gmail"),
            ("get_gmail_today", "gmail"),
            ("get_gmail_by_date_range", "gmail"),
            ("get_gmail_by_label", "gmail"),
        ]
        
        # Register all tools
        all_tools = todoist_tools + gcal_tools + gmail_tools
        
        for tool_name, service in all_tools:
            # Create a loader function for each tool
            def create_loader(service_name, tool_name):
                def loader():
                    return {
                        "name": tool_name,
                        "service": service_name,
                        "type": "individual_tool",
                        "loaded_at": time.time()
                    }
                return loader
            
            self.tool_manager.register_tool(tool_name, create_loader(service, tool_name), service)
        
        print(f"📝 Registered {len(all_tools)} individual tools for dynamic loading")
    
    def _register_core_tools(self) -> Dict[str, Dict[str, Any]]:
        """Register the core MCP tools (always loaded)"""
        return {
            "execute_packet": {
                "name": "execute_packet",
                "description": "Execute any operation via standardized MCP packet",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "tool_type": {
                            "type": "string",
                            "description": "Service type: todoist, gcal, or gmail",
                            "enum": ["todoist", "gcal", "gmail"]
                        },
                        "action": {
                            "type": "string", 
                            "description": "Action to perform: create, read, update, delete, list, search",
                            "enum": ["create", "read", "update", "delete", "list", "search"]
                        },
                        "item_type": {
                            "type": "string",
                            "description": "Type of item to operate on (varies by service)"
                        },
                        "payload": {
                            "type": "object",
                            "description": "Service-specific parameters for the operation"
                        },
                        "priority": {
                            "type": "string",
                            "description": "Priority level: low, normal, high, critical",
                            "enum": ["low", "normal", "high", "critical"],
                            "default": "normal"
                        }
                    },
                    "required": ["tool_type", "action", "item_type", "payload"]
                }
            },
            
            "list_services": {
                "name": "list_services",
                "description": "List all available services and their capabilities",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "include_schemas": {
                            "type": "boolean",
                            "description": "Include detailed schemas for each service",
                            "default": False
                        }
                    }
                }
            },
            
            "get_service_schema": {
                "name": "get_service_schema",
                "description": "Get detailed schema for a specific service",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "service_name": {
                            "type": "string",
                            "description": "Name of the service to get schema for",
                            "enum": ["todoist", "gcal", "gmail"]
                        }
                    },
                    "required": ["service_name"]
                }
            },
            
            "batch_execute": {
                "name": "batch_execute",
                "description": "Execute multiple packets in a single request",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "packets": {
                            "type": "array",
                            "description": "Array of packet definitions to execute",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "tool_type": {"type": "string"},
                                    "action": {"type": "string"},
                                    "item_type": {"type": "string"},
                                    "payload": {"type": "object"}
                                },
                                "required": ["tool_type", "action", "item_type", "payload"]
                            }
                        },
                        "parallel": {
                            "type": "boolean",
                            "description": "Execute packets in parallel if possible",
                            "default": True
                        }
                    },
                    "required": ["packets"]
                }
            },
            
            "get_packet_status": {
                "name": "get_packet_status",
                "description": "Check the status of a previously submitted packet",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "packet_id": {
                            "type": "string",
                            "description": "ID of the packet to check"
                        }
                    },
                    "required": ["packet_id"]
                }
            },
            
            # New dynamic tool management tools
            "load_tool": {
                "name": "load_tool",
                "description": "Dynamically load a specific tool into memory",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "tool_name": {
                            "type": "string",
                            "description": "Name of the tool to load"
                        }
                    },
                    "required": ["tool_name"]
                }
            },
            
            "unload_tool": {
                "name": "unload_tool",
                "description": "Unload a specific tool from memory",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "tool_name": {
                            "type": "string",
                            "description": "Name of the tool to unload"
                        }
                    },
                    "required": ["tool_name"]
                }
            },
            
            "get_tool_status": {
                "name": "get_tool_status",
                "description": "Get status of a specific tool",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "tool_name": {
                            "type": "string",
                            "description": "Name of the tool to check"
                        }
                    },
                    "required": ["tool_name"]
                }
            },
            
            "get_performance_metrics": {
                "name": "get_performance_metrics",
                "description": "Get performance metrics and cache statistics",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            
            "optimize_cache": {
                "name": "optimize_cache",
                "description": "Optimize the tool cache by evicting low-usage tools",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            
            "set_cache_policy": {
                "name": "set_cache_policy",
                "description": "Change the cache eviction policy (LRU/LFU)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "policy": {
                            "type": "string",
                            "description": "Cache policy: lru or lfu",
                            "enum": ["lru", "lfu"]
                        }
                    },
                    "required": ["policy"]
                }
            },
            
            "set_max_tools": {
                "name": "set_max_tools",
                "description": "Change the maximum number of tools in memory",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "max_tools": {
                            "type": "integer",
                            "description": "New maximum number of tools",
                            "minimum": 5
                        }
                    },
                    "required": ["max_tools"]
                }
            }
        }
    
    def _register_resources(self) -> Dict[str, Dict[str, Any]]:
        """Register MCP resources"""
        return {
            "mcp://services": {
                "uri": "mcp://services",
                "name": "Available Services",
                "description": "List of all available services and their capabilities",
                "mimeType": "application/json"
            },
            "mcp://packet-schema": {
                "uri": "mcp://packet-schema", 
                "name": "Packet Schema",
                "description": "Schema definition for MCP packets",
                "mimeType": "application/json"
            },
            "mcp://tool-cache": {
                "uri": "mcp://tool-cache",
                "name": "Tool Cache Status",
                "description": "Current status of the dynamic tool cache",
                "mimeType": "application/json"
            }
        }
    
    async def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Route tool calls to appropriate handlers"""
        if name == "execute_packet":
            return await self._execute_packet(arguments)
        elif name == "list_services":
            return await self._list_services(arguments)
        elif name == "get_service_schema":
            return await self._get_service_schema(arguments)
        elif name == "batch_execute":
            return await self._batch_execute(arguments)
        elif name == "get_packet_status":
            return await self._get_packet_status(arguments)
        # Dynamic tool management tools
        elif name == "load_tool":
            return await self._load_tool(arguments)
        elif name == "unload_tool":
            return await self._unload_tool(arguments)
        elif name == "get_tool_status":
            return await self._get_tool_status(arguments)
        elif name == "get_performance_metrics":
            return await self._get_performance_metrics(arguments)
        elif name == "optimize_cache":
            return await self._optimize_cache(arguments)
        elif name == "set_cache_policy":
            return await self._set_cache_policy(arguments)
        elif name == "set_max_tools":
            return await self._set_max_tools(arguments)
        else:
            return {"success": False, "error": f"Unknown tool: {name}"}
    
    async def _execute_packet(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single MCP packet with dynamic tool loading"""
        start_time = time.time()
        
        try:
            # Create packet from arguments
            packet = MCPPacket(
                tool_type=arguments["tool_type"],
                action=arguments["action"],
                item_type=arguments["item_type"],
                payload=arguments["payload"],
                priority=arguments.get("priority", "normal")
            )
            
            # Validate packet
            if not packet.validate():
                return {
                    "success": False,
                    "error": "Invalid packet structure",
                    "packet_id": packet.packet_id
                }
            
            # Get appropriate service handler
            service_handler = self.service_handlers.get(packet.tool_type)
            if not service_handler:
                return {
                    "success": False,
                    "error": f"Unknown service: {packet.tool_type}",
                    "packet_id": packet.packet_id
                }
            
            # Load relevant tools for this operation
            await self._load_service_tools_if_needed(packet.tool_type)
            
            # Execute the packet
            result = await service_handler.execute(packet.action, packet.payload)
            
            # Track execution
            execution_time = time.time() - start_time
            self.execution_history[packet.packet_id] = {
                "packet": packet.to_dict(),
                "result": result,
                "execution_time": execution_time,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return {
                "success": True,
                "packet_id": packet.packet_id,
                "result": result,
                "execution_time": execution_time
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "execution_time": execution_time
            }
    
    async def _load_service_tools_if_needed(self, service_name: str):
        """Load tools for a service if they're not already loaded"""
        # This is where you'd implement intelligent tool loading
        # For now, we'll just ensure the service handler is available
        if service_name in self.service_handlers:
            # Load some commonly used tools for this service
            common_tools = [
                f"{service_name}_list",
                f"{service_name}_search",
                f"{service_name}_read"
            ]
            
            for tool_name in common_tools:
                if tool_name in self.tool_manager.tool_registry:
                    self.tool_manager.load_tool(tool_name)
    
    async def _load_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Dynamically load a specific tool"""
        tool_name = arguments["tool_name"]
        
        try:
            tool = self.tool_manager.load_tool(tool_name)
            if tool:
                return {
                    "success": True,
                    "tool_name": tool_name,
                    "message": f"Tool {tool_name} loaded successfully",
                    "tool_info": tool
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to load tool: {tool_name}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error loading tool {tool_name}: {str(e)}"
            }
    
    async def _unload_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Unload a specific tool"""
        tool_name = arguments["tool_name"]
        
        try:
            success = self.tool_manager.unload_tool(tool_name)
            if success:
                return {
                    "success": True,
                    "tool_name": tool_name,
                    "message": f"Tool {tool_name} unloaded successfully"
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to unload tool: {tool_name}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error unloading tool {tool_name}: {str(e)}"
            }
    
    async def _get_tool_status(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get status of a specific tool"""
        tool_name = arguments["tool_name"]
        
        try:
            status = self.tool_manager.get_tool_status(tool_name)
            return {
                "success": True,
                "tool_status": status
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting tool status: {str(e)}"
            }
    
    async def _get_performance_metrics(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get performance metrics and cache statistics"""
        try:
            metrics = self.tool_manager.get_performance_metrics()
            return {
                "success": True,
                "metrics": metrics
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting performance metrics: {str(e)}"
            }
    
    async def _optimize_cache(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize the tool cache"""
        try:
            result = self.tool_manager.optimize_cache()
            return {
                "success": True,
                "optimization_result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error optimizing cache: {str(e)}"
            }
    
    async def _set_cache_policy(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Change the cache eviction policy"""
        policy = arguments["policy"]
        
        try:
            self.tool_manager.set_cache_policy(policy)
            return {
                "success": True,
                "message": f"Cache policy changed to {policy.upper()}",
                "new_policy": policy
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error changing cache policy: {str(e)}"
            }
    
    async def _set_max_tools(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Change the maximum number of tools"""
        max_tools = arguments["max_tools"]
        
        try:
            self.tool_manager.set_max_tools(max_tools)
            return {
                "success": True,
                "message": f"Maximum tools changed to {max_tools}",
                "new_max": max_tools
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error changing max tools: {str(e)}"
            }
    
    # ... existing methods from the original server ...
    async def _list_services(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """List all available services and their capabilities"""
        include_schemas = arguments.get("include_schemas", False)
        
        services = {}
        for service_name, handler in self.service_handlers.items():
            service_info = {
                "name": service_name,
                "supported_actions": handler.supported_actions,
                "supported_item_types": handler.supported_item_types
            }
            
            if include_schemas:
                service_info["schema"] = await self._get_service_schema_internal(service_name)
            
            services[service_name] = service_info
        
        return {
            "success": True,
            "services": services,
            "total_services": len(services)
        }
    
    async def _get_service_schema(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed schema for a specific service"""
        service_name = arguments["service_name"]
        
        if service_name not in self.service_handlers:
            return {
                "success": False,
                "error": f"Unknown service: {service_name}"
            }
        
        schema = await self._get_service_schema_internal(service_name)
        
        return {
            "success": True,
            "service": service_name,
            "schema": schema
        }
    
    async def _get_service_schema_internal(self, service_name: str) -> Dict[str, Any]:
        """Internal method to get service schema"""
        # ... existing schema logic ...
        return {}
    
    async def _batch_execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute multiple packets in a single request"""
        # ... existing batch execution logic ...
        return {"success": True, "message": "Batch execution placeholder"}
    
    async def _get_packet_status(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Check the status of a previously submitted packet"""
        # ... existing status logic ...
        return {"success": True, "message": "Status check placeholder"}
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools"""
        return list(self.tools.values())
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all available resources"""
        return list(self.resources.values())
    
    def get_resource(self, uri: str) -> Optional[Dict[str, Any]]:
        """Get a specific resource"""
        if uri == "mcp://tool-cache":
            return {
                "uri": uri,
                "name": "Tool Cache Status",
                "description": "Current status of the dynamic tool cache",
                "mimeType": "application/json",
                "content": json.dumps(self.tool_manager.get_performance_metrics(), indent=2)
            }
        # ... handle other resources ...
        return None


async def main():
    """Main entry point for testing"""
    server = EnhancedMCPServer(cache_policy="lfu", max_tools=20)
    
    print("🚀 Enhanced MCP Server with Dynamic Tool Management")
    print("=" * 60)
    print(f"📚 Available tools: {len(server.tools)}")
    print(f"🔗 Available resources: {len(server.resources)}")
    print(f"⚙️  Cache policy: {server.tool_manager.cache_policy.upper()}")
    print(f"📊 Tool limit: {server.tool_manager.max_tools}")
    
    # Test dynamic tool loading
    print("\n🧪 Testing Dynamic Tool Management:")
    
    # Test 1: Load a tool
    print("\n1️⃣ Loading Todoist task creator...")
    result = await server._load_tool({"tool_name": "create_todoist_task"})
    print(f"   Result: {result}")
    
    # Test 2: Get tool status
    print("\n2️⃣ Getting tool status...")
    status = await server._get_tool_status({"tool_name": "create_todoist_task"})
    print(f"   Status: {status}")
    
    # Test 3: Get performance metrics
    print("\n3️⃣ Getting performance metrics...")
    metrics = await server._get_performance_metrics({})
    print(f"   Cache size: {metrics['metrics']['cache_stats']['current_size']}/{metrics['metrics']['cache_stats']['capacity']}")
    
    # Test 4: Change cache policy
    print("\n4️⃣ Changing cache policy to LRU...")
    policy_result = await server._set_cache_policy({"policy": "lru"})
    print(f"   Result: {policy_result}")
    
    print("\n✅ Enhanced MCP Server test completed!")


if __name__ == "__main__":
    asyncio.run(main())
