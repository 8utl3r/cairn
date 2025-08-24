#!/usr/bin/env python3
"""
Demo script for MCP Packet Server
Showcases the consolidation from 137 tools to 5 core tools
"""

import asyncio
import json
from datetime import datetime, timedelta

from packet import MCPPacket
from server import MCPPacketServer


class MCPPacketDemo:
    """Demonstration of MCP Packet Server capabilities"""

    def __init__(self):
        self.server = MCPPacketServer()

    async def run_demo(self):
        """Run the complete demonstration"""
        print("🎭 MCP Packet Server - Live Demonstration")
        print("=" * 60)

        # Phase 1: Show the consolidation
        await self._demonstrate_consolidation()

        # Phase 2: Show packet creation and validation
        await self._demonstrate_packet_system()

        # Phase 3: Show real operations
        await self._demonstrate_real_operations()

        # Phase 4: Show batch operations
        await self._demonstrate_batch_operations()

        # Phase 5: Show service schemas
        await self._demonstrate_service_schemas()

        print("\n🎉 Demo completed successfully!")
        print("🚀 Your MCP server is now ready with packet-based communication!")

    async def _demonstrate_consolidation(self):
        """Demonstrate the tool consolidation"""
        print("\n📊 PHASE 1: Tool Consolidation")
        print("-" * 40)

        # Show before/after
        print("BEFORE: 137 individual tools")
        print("  • create_todoist_task")
        print("  • update_todoist_task")
        print("  • delete_todoist_task")
        print("  • create_gcal_event")
        print("  • update_gcal_event")
        print("  • delete_gcal_event")
        print("  • create_gmail_email")
        print("  • ... and 130 more!")

        print("\nAFTER: 5 core tools")
        for tool in self.server.list_tools():
            print(f"  • {tool['name']}: {tool['description']}")

        # Calculate consolidation ratio
        services_result = await self.server._list_services({})
        total_operations = 0
        for service_info in services_result["services"].values():
            total_ops = len(service_info["supported_actions"]) * len(service_info["supported_item_types"])
            total_operations += total_ops

        consolidation_ratio = total_operations / len(self.server.tools)
        print(f"\n📈 Consolidation Ratio: {total_operations} operations → {len(self.server.tools)} tools")
        print(f"📈 Efficiency Gain: {consolidation_ratio:.1f}x improvement")

    async def _demonstrate_packet_system(self):
        """Demonstrate the packet system"""
        print("\n📦 PHASE 2: Packet System")
        print("-" * 40)

        # Create example packets
        packets = [
            MCPPacket(
                tool_type="todoist",
                action="create",
                item_type="task",
                payload={"content": "Buy groceries", "due_date": "tomorrow"}
            ),
            MCPPacket(
                tool_type="gcal",
                action="create",
                item_type="event",
                payload={"summary": "Team Meeting", "start_time": "2024-01-15T10:00:00Z"}
            ),
            MCPPacket(
                tool_type="gmail",
                action="search",
                item_type="email",
                payload={"query": "from:boss@company.com"}
            )
        ]

        print("📦 Example Packets:")
        for i, packet in enumerate(packets, 1):
            print(f"\n  Packet {i}:")
            print(f"    Tool Type: {packet.tool_type}")
            print(f"    Action: {packet.action}")
            print(f"    Item Type: {packet.item_type}")
            print(f"    Payload: {packet.payload}")
            print(f"    Valid: {packet.validate()}")
            print(f"    Routing Key: {packet.get_routing_key()}")

    async def _demonstrate_real_operations(self):
        """Demonstrate real operations using packets"""
        print("\n🔧 PHASE 3: Real Operations")
        print("-" * 40)

        # Test 1: Create Todoist task
        print("\n1️⃣ Creating Todoist Task...")
        task_result = await self.server._execute_packet({
            "tool_type": "todoist",
            "action": "create",
            "item_type": "task",
            "payload": {
                "content": "Demo task from MCP Packet Server",
                "due_date": "tomorrow",
                "priority": 1
            }
        })

        if task_result["success"]:
            print("   ✅ Task created successfully!")
            print(f"   📝 Task ID: {task_result['packet_id']}")
            print(f"   ⏱️  Execution time: {task_result['execution_time']:.3f}s")
        else:
            print(f"   ❌ Task creation failed: {task_result['error']}")

        # Test 2: Create Google Calendar event
        print("\n2️⃣ Creating Google Calendar Event...")
        tomorrow = datetime.now() + timedelta(days=1)
        event_result = await self.server._execute_packet({
            "tool_type": "gcal",
            "action": "create",
            "item_type": "event",
            "payload": {
                "summary": "Demo Event from MCP Packet Server",
                "start_time": tomorrow.replace(hour=10, minute=0, second=0).isoformat(),
                "end_time": tomorrow.replace(hour=11, minute=0, second=0).isoformat(),
                "description": "This event was created using the MCP Packet Server"
            }
        })

        if event_result["success"]:
            print("   ✅ Event created successfully!")
            print(f"   📅 Event ID: {event_result['packet_id']}")
            print(f"   ⏱️  Execution time: {event_result['execution_time']:.3f}s")
        else:
            print(f"   ❌ Event creation failed: {event_result['error']}")

        # Test 3: Search Gmail
        print("\n3️⃣ Searching Gmail...")
        search_result = await self.server._execute_packet({
            "tool_type": "gmail",
            "action": "search",
            "item_type": "email",
            "payload": {
                "query": "demo",
                "max_results": 5
            }
        })

        if search_result["success"]:
            print("   ✅ Search completed successfully!")
            print(f"   🔍 Found {search_result['result']['data']['count']} results")
            print(f"   ⏱️  Execution time: {search_result['execution_time']:.3f}s")
        else:
            print(f"   ❌ Search failed: {search_result['error']}")

    async def _demonstrate_batch_operations(self):
        """Demonstrate batch operations"""
        print("\n📦 PHASE 4: Batch Operations")
        print("-" * 40)

        # Create multiple packets for batch execution
        batch_packets = [
            {
                "tool_type": "todoist",
                "action": "list",
                "item_type": "task",
                "payload": {"limit": 3}
            },
            {
                "tool_type": "gcal",
                "action": "list",
                "item_type": "event",
                "payload": {"limit": 3}
            },
            {
                "tool_type": "gmail",
                "action": "list",
                "item_type": "email",
                "payload": {"limit": 3}
            }
        ]

        print("📦 Executing batch operation with 3 packets...")
        batch_result = await self.server._batch_execute({
            "packets": batch_packets,
            "parallel": True
        })

        if batch_result["success"]:
            print("   ✅ Batch execution completed!")
            print(f"   📊 Total packets: {batch_result['total_packets']}")
            print(f"   🚀 Execution mode: {batch_result['execution_mode']}")

            print("\n   📋 Individual Results:")
            for i, result in enumerate(batch_result["results"]):
                status = "✅" if result["success"] else "❌"
                print(f"     {i+1}. {status} {result.get('packet_id', 'Unknown')}")
                if result["success"]:
                    print(f"        ⏱️  {result['execution_time']:.3f}s")
                else:
                    print(f"        ❌ {result['error']}")
        else:
            print(f"   ❌ Batch execution failed: {batch_result['error']}")

    async def _demonstrate_service_schemas(self):
        """Demonstrate service schema capabilities"""
        print("\n📋 PHASE 5: Service Schemas")
        print("-" * 40)

        # Get service list
        services_result = await self.server._list_services({"include_schemas": True})

        if services_result["success"]:
            print(f"🔧 Available Services: {services_result['total_services']}")

            for service_name, service_info in services_result["services"].items():
                print(f"\n  📋 {service_name.upper()} Service:")
                print(f"     Actions: {', '.join(service_info['supported_actions'])}")
                print(f"     Item Types: {', '.join(service_info['supported_item_types'])}")

                if "schema" in service_info:
                    schema = service_info["schema"]
                    if "actions" in schema:
                        print(f"     📖 Schema: {len(schema['actions'])} action types defined")

        # Get specific service schema
        print("\n🔍 Detailed Todoist Schema:")
        todoist_schema = await self.server._get_service_schema({"service_name": "todoist"})

        if todoist_schema["success"]:
            schema = todoist_schema["schema"]
            if "actions" in schema:
                for action, action_schemas in schema["actions"].items():
                    print(f"     {action}:")
                    if isinstance(action_schemas, dict):
                        for item_type, requirements in action_schemas.items():
                            if isinstance(requirements, dict):
                                req_fields = requirements.get("required", [])
                                opt_fields = requirements.get("optional", [])
                                print(f"       {item_type}:")
                                if req_fields:
                                    print(f"         Required: {', '.join(req_fields)}")
                                if opt_fields:
                                    print(f"         Optional: {', '.join(opt_fields)}")
                            else:
                                print(f"       {item_type}: {requirements}")
                    else:
                        print(f"       {action_schemas}")
            else:
                print(f"     Schema: {schema}")

    def show_usage_examples(self):
        """Show usage examples for developers"""
        print("\n💡 USAGE EXAMPLES FOR DEVELOPERS")
        print("=" * 60)

        examples = [
            {
                "title": "Create Todoist Task",
                "description": "Create a new task in Todoist",
                "code": {
                    "tool": "execute_packet",
                    "arguments": {
                        "tool_type": "todoist",
                        "action": "create",
                        "item_type": "task",
                        "payload": {
                            "content": "Buy groceries",
                            "due_date": "tomorrow",
                            "priority": 1
                        }
                    }
                }
            },
            {
                "title": "Create Google Calendar Event",
                "description": "Schedule a new calendar event",
                "code": {
                    "tool": "execute_packet",
                    "arguments": {
                        "tool_type": "gcal",
                        "action": "create",
                        "item_type": "event",
                        "payload": {
                            "summary": "Team Meeting",
                            "start_time": "2024-01-15T10:00:00Z",
                            "end_time": "2024-01-15T11:00:00Z",
                            "attendees": ["team@company.com"]
                        }
                    }
                }
            },
            {
                "title": "Search Gmail Messages",
                "description": "Search for emails with specific criteria",
                "code": {
                    "tool": "execute_packet",
                    "arguments": {
                        "tool_type": "gmail",
                        "action": "search",
                        "item_type": "email",
                        "payload": {
                            "query": "from:boss@company.com subject:meeting",
                            "max_results": 10
                        }
                    }
                }
            },
            {
                "title": "Batch Operations",
                "description": "Execute multiple operations at once",
                "code": {
                    "tool": "batch_execute",
                    "arguments": {
                        "packets": [
                            {
                                "tool_type": "todoist",
                                "action": "list",
                                "item_type": "task",
                                "payload": {"limit": 5}
                            },
                            {
                                "tool_type": "gcal",
                                "action": "list",
                                "item_type": "event",
                                "payload": {"limit": 5}
                            }
                        ],
                        "parallel": True
                    }
                }
            }
        ]

        for i, example in enumerate(examples, 1):
            print(f"\n{i}. {example['title']}")
            print(f"   {example['description']}")
            print("   Code:")
            print("   ```json")
            print(f"   {json.dumps(example['code'], indent=2)}")
            print("   ```")


async def main():
    """Main demo entry point"""
    demo = MCPPacketDemo()
    await demo.run_demo()

    # Show usage examples
    demo.show_usage_examples()


if __name__ == "__main__":
    asyncio.run(main())
