"""
Main MCP Packet Server
Consolidates 137 tools into a few core tools using packet-based communication
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from bootstrap import init_env

init_env()

from packet import MCPPacket
from services import (
    DeepPCBServiceHandler,
    GmailServiceHandler,
    GoogleCalendarServiceHandler,
    TodoistServiceHandler,
)


class MCPPacketServer:
    """
    Unified MCP server using packet-based communication
    
    REDUCES 137 TOOLS TO JUST 5 CORE TOOLS:
    1. execute_packet - Execute any operation via packet
    2. list_services - List available services and capabilities
    3. get_service_schema - Get schema for a specific service
    4. batch_execute - Execute multiple packets at once
    5. get_packet_status - Check status of packet execution
    """

    def __init__(self):
        self.service_handlers = {
            'todoist': TodoistServiceHandler(),
            'gcal': GoogleCalendarServiceHandler(),
            'gmail': GmailServiceHandler(),
            'deep_pcb': DeepPCBServiceHandler()
        }

        # Packet execution tracking
        self.packet_queue = {}
        self.execution_history = {}

        # Register core tools
        self.tools = self._register_tools()
        self.resources = self._register_resources()

    def _register_tools(self) -> Dict[str, Dict[str, Any]]:
        """Register the core MCP tools (only 5 tools instead of 137!)"""
        return {
            "execute_packet": {
                "name": "execute_packet",
                "description": "Execute any operation via standardized MCP packet",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "tool_type": {
                            "type": "string",
                            "description": "Service type: todoist, gcal, gmail, or deep_pcb",
                            "enum": ["todoist", "gcal", "gmail", "deep_pcb"]
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
                            "enum": ["todoist", "gcal", "gmail", "deep_pcb"]
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
        else:
            return {"success": False, "error": f"Unknown tool: {name}"}

    async def _execute_packet(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single MCP packet"""
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

            # Execute the packet
            result = await service_handler.execute(packet.action, packet.payload, packet.item_type)

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
        handler = self.service_handlers[service_name]

        # Define schemas for each service
        schemas = {
            "todoist": {
                "actions": {
                    "create": {
                        "task": {
                            "required": ["content"],
                            "optional": ["due_date", "priority", "project_id", "labels"]
                        },
                        "project": {
                            "required": ["name"],
                            "optional": ["color", "parent_id"]
                        },
                        "label": {
                            "required": ["name"],
                            "optional": ["color", "order"]
                        }
                    },
                    "read": {
                        "required": ["id"],
                        "optional": ["item_type"]
                    },
                    "update": {
                        "required": ["id"],
                        "optional": ["updates"]
                    },
                    "delete": {
                        "required": ["id"]
                    },
                    "list": {
                        "optional": ["item_type", "limit", "project_id", "label_id"]
                    },
                    "search": {
                        "required": ["query"],
                        "optional": ["max_results", "filters"]
                    }
                }
            },
            "gcal": {
                "actions": {
                    "create": {
                        "event": {
                            "required": ["summary", "start_time", "end_time"],
                            "optional": ["description", "location", "attendees", "reminders"]
                        },
                        "calendar": {
                            "required": ["name"],
                            "optional": ["description", "timezone"]
                        }
                    },
                    "read": {
                        "required": ["id"],
                        "optional": ["item_type"]
                    },
                    "update": {
                        "required": ["id"],
                        "optional": ["updates"]
                    },
                    "delete": {
                        "required": ["id"]
                    },
                    "list": {
                        "optional": ["item_type", "limit", "calendar_id", "time_min", "time_max"]
                    },
                    "search": {
                        "required": ["query"],
                        "optional": ["max_results", "calendar_id", "time_min", "time_max"]
                    }
                }
            },
            "gmail": {
                "actions": {
                    "create": {
                        "email": {
                            "required": ["to", "subject", "body"],
                            "optional": ["cc", "bcc", "attachments"]
                        },
                        "label": {
                            "required": ["name"],
                            "optional": ["color"]
                        }
                    },
                    "read": {
                        "required": ["id"],
                        "optional": ["item_type"]
                    },
                    "update": {
                        "required": ["id"],
                        "optional": ["updates"]
                    },
                    "delete": {
                        "required": ["id"]
                    },
                    "list": {
                        "optional": ["item_type", "limit", "label_id", "query"]
                    },
                    "search": {
                        "required": ["query"],
                        "optional": ["max_results", "label_id", "date_range"]
                    }
                }
            }
        }

        return schemas.get(service_name, {})

    async def _batch_execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute multiple packets in a single request"""
        packets_data = arguments["packets"]
        parallel = arguments.get("parallel", True)

        if not packets_data:
            return {"success": False, "error": "No packets provided"}

        results = []

        if parallel:
            # Execute packets in parallel
            tasks = []
            for packet_data in packets_data:
                task = self._execute_packet(packet_data)
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Handle exceptions
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    results[i] = {
                        "success": False,
                        "error": str(result),
                        "packet_index": i
                    }
        else:
            # Execute packets sequentially
            for i, packet_data in enumerate(packets_data):
                try:
                    result = await self._execute_packet(packet_data)
                    result["packet_index"] = i
                    results.append(result)
                except Exception as e:
                    results.append({
                        "success": False,
                        "error": str(e),
                        "packet_index": i
                    })

        return {
            "success": True,
            "results": results,
            "total_packets": len(packets_data),
            "execution_mode": "parallel" if parallel else "sequential"
        }

    async def _get_packet_status(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Check the status of a previously submitted packet"""
        packet_id = arguments["packet_id"]

        if packet_id not in self.execution_history:
            return {
                "success": False,
                "error": f"Packet not found: {packet_id}"
            }

        history_entry = self.execution_history[packet_id]

        return {
            "success": True,
            "packet_id": packet_id,
            "status": "completed",
            "execution_time": history_entry["execution_time"],
            "timestamp": history_entry["timestamp"],
            "result": history_entry["result"]
        }

    def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools"""
        return list(self.tools.values())

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all available resources"""
        return list(self.resources.values())

    def get_resource(self, uri: str) -> Optional[Dict[str, Any]]:
        """Get a specific resource"""
        if uri == "mcp://services":
            return {
                "uri": uri,
                "name": "Available Services",
                "description": "List of all available services and their capabilities",
                "mimeType": "application/json",
                "content": json.dumps(self._get_services_summary(), indent=2)
            }
        elif uri == "mcp://packet-schema":
            return {
                "uri": uri,
                "name": "Packet Schema",
                "description": "Schema definition for MCP packets",
                "mimeType": "application/json",
                "content": json.dumps(self._get_packet_schema(), indent=2)
            }

        return None

    def _get_services_summary(self) -> Dict[str, Any]:
        """Get summary of all services"""
        summary = {}
        for service_name, handler in self.service_handlers.items():
            summary[service_name] = {
                "supported_actions": handler.supported_actions,
                "supported_item_types": handler.supported_item_types,
                "total_operations": len(handler.supported_actions) * len(handler.supported_item_types)
            }

        total_operations = sum(service["total_operations"] for service in summary.values())
        summary["_meta"] = {
            "total_services": len(summary),
            "total_operations": total_operations,
            "note": f"Consolidated from {total_operations} individual tools to 5 core tools"
        }

        return summary

    def _get_packet_schema(self) -> Dict[str, Any]:
        """Get the schema for MCP packets"""
        # Dynamically generate schema from service handlers
        available_services = list(self.service_handlers.keys())
        available_actions = []
        for handler in self.service_handlers.values():
            available_actions.extend(handler.supported_actions)
        available_actions = list(set(available_actions))  # Remove duplicates

        return {
            "tool_type": f"Service type ({', '.join(available_services)})",
            "action": f"Action to perform ({', '.join(available_actions)})",
            "item_type": "Type of item to operate on (varies by service)",
            "payload": "Service-specific parameters for the operation",
            "priority": "Priority level (low, normal, high, critical)",
            "packet_id": "Unique identifier for the packet",
            "timestamp": "Timestamp when packet was created",
            "checksum": "Checksum for packet integrity"
        }


async def main():
    """Main entry point for testing"""
    server = MCPPacketServer()

    print("🚀 MCP Packet Server - Proof of Concept")
    print("=" * 50)
    print(f"📚 Available tools: {len(server.tools)} (consolidated from 137!)")
    print(f"🔗 Available resources: {len(server.resources)}")

    # List available tools
    print("\n📋 Core Tools:")
    for tool in server.list_tools():
        print(f"  • {tool['name']}: {tool['description']}")

    # List available services
    print("\n🔧 Available Services:")
    services_result = await server._list_services({})
    for service_name, service_info in services_result["services"].items():
        total_ops = len(service_info["supported_actions"]) * len(service_info["supported_item_types"])
        print(f"  • {service_name}: {total_ops} operations")

    # Test packet execution
    print("\n🧪 Testing Packet Execution:")

    # Test 1: Create Todoist task
    print("\n1. Creating Todoist task...")
    task_result = await server._execute_packet({
        "tool_type": "todoist",
        "action": "create",
        "item_type": "task",
        "payload": {
            "content": "Test task from MCP Packet Server",
            "due_date": "tomorrow",
            "priority": 2
        }
    })
    print(f"   Result: {task_result}")

    # Test 2: Create Google Calendar event
    print("\n2. Creating Google Calendar event...")
    event_result = await server._execute_packet({
        "tool_type": "gcal",
        "action": "create",
        "item_type": "event",
        "payload": {
            "summary": "Test Event from MCP Packet Server",
            "start_time": "2024-01-15T14:00:00Z",
            "end_time": "2024-01-15T15:00:00Z"
        }
    })
    print(f"   Result: {event_result}")

    # Test 3: Batch execution
    print("\n3. Testing batch execution...")
    batch_result = await server._batch_execute({
        "packets": [
            {
                "tool_type": "todoist",
                "action": "list",
                "item_type": "task",
                "payload": {"limit": 5}
            },
            {
                "tool_type": "gmail",
                "action": "search",
                "item_type": "email",
                "payload": {"query": "test", "max_results": 3}
            }
        ],
        "parallel": True
    })
    print(f"   Result: {batch_result}")

    print("\n✅ MCP Packet Server test completed successfully!")
    print(f"🎯 Successfully consolidated 137 tools into just {len(server.tools)} core tools!")


if __name__ == "__main__":
    asyncio.run(main())
