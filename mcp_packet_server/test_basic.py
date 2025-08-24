#!/usr/bin/env python3
"""
Basic test script for MCP Packet Server
Tests core functionality without running the full demo
"""

import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from packet import MCPPacket, create_example_packets
from server import MCPPacketServer


async def test_basic_functionality():
    """Test basic functionality of the MCP Packet Server"""
    print("🧪 Testing MCP Packet Server Basic Functionality")
    print("=" * 50)

    # Test 1: Packet creation and validation
    print("\n1️⃣ Testing Packet System...")
    try:
        packets = create_example_packets()
        print(f"   ✅ Created {len(packets)} example packets")

        for i, packet in enumerate(packets, 1):
            print(f"   📦 Packet {i}: {packet.tool_type}:{packet.action}:{packet.item_type}")
            print(f"      Valid: {packet.validate()}")
            print(f"      Routing Key: {packet.get_routing_key()}")

        print("   ✅ Packet system working correctly")
    except Exception as e:
        print(f"   ❌ Packet system failed: {e}")
        return False

    # Test 2: Server initialization
    print("\n2️⃣ Testing Server Initialization...")
    try:
        server = MCPPacketServer()
        print("   ✅ Server initialized successfully")
        print(f"   📚 Available tools: {len(server.tools)}")
        print(f"   🔗 Available resources: {len(server.resources)}")

        # List tools
        print("   📋 Core Tools:")
        for tool in server.list_tools():
            print(f"      • {tool['name']}: {tool['description']}")

        print("   ✅ Server initialization working correctly")
    except Exception as e:
        print(f"   ❌ Server initialization failed: {e}")
        return False

    # Test 3: Service listing
    print("\n3️⃣ Testing Service Listing...")
    try:
        services_result = await server._list_services({})
        if services_result["success"]:
            print("   ✅ Services listed successfully")
            print(f"   🔧 Total services: {services_result['total_services']}")

            for service_name, service_info in services_result["services"].items():
                total_ops = len(service_info["supported_actions"]) * len(service_info["supported_item_types"])
                print(f"      • {service_name}: {total_ops} operations")

            print("   ✅ Service listing working correctly")
        else:
            print(f"   ❌ Service listing failed: {services_result.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"   ❌ Service listing failed: {e}")
        return False

    # Test 4: Basic packet execution
    print("\n4️⃣ Testing Basic Packet Execution...")
    try:
        # Test a simple operation
        result = await server._execute_packet({
            "tool_type": "todoist",
            "action": "list",
            "item_type": "task",
            "payload": {"limit": 3}
        })

        if result["success"]:
            print("   ✅ Packet execution successful")
            print(f"   📝 Packet ID: {result['packet_id']}")
            print(f"   ⏱️  Execution time: {result['execution_time']:.3f}s")
            print("   ✅ Basic packet execution working correctly")
        else:
            print(f"   ❌ Packet execution failed: {result.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"   ❌ Packet execution failed: {e}")
        return False

    # Test 5: Service schema retrieval
    print("\n5️⃣ Testing Service Schema Retrieval...")
    try:
        schema_result = await server._get_service_schema({"service_name": "todoist"})
        if schema_result["success"]:
            print("   ✅ Schema retrieved successfully")
            schema = schema_result["schema"]
            if "actions" in schema:
                print(f"   📖 Actions defined: {len(schema['actions'])}")
                for action in schema["actions"]:
                    print(f"      • {action}")
            print("   ✅ Service schema retrieval working correctly")
        else:
            print(f"   ❌ Schema retrieval failed: {schema_result.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"   ❌ Schema retrieval failed: {e}")
        return False

    print("\n🎉 All basic functionality tests passed!")
    return True


def test_packet_validation():
    """Test packet validation logic with tripwire system"""
    print("\n🔍 Testing Packet Validation...")

    # Test valid packet
    valid_packet = MCPPacket(
        tool_type="todoist",
        action="create",
        item_type="task",
        payload={"content": "Test task"}
    )

    if valid_packet.validate():
        print("   ✅ Valid packet validation working")
    else:
        print("   ❌ Valid packet validation failed")
        return False

    # Test invalid packet (missing required field)
    try:
        invalid_packet = MCPPacket(
            tool_type="todoist",
            action="create",
            # Missing item_type
            payload={"content": "Test task"}
        )

        if not invalid_packet.validate():
            print("   ✅ Invalid packet validation working")
        else:
            print("   ❌ Invalid packet validation failed")
            return False
    except Exception as e:
        print(f"   ✅ Invalid packet handling working (caught: {e})")

    # Test tripwire validation system
    try:
        from validation_tripwires import PacketValidationTripwires

        tripwires = PacketValidationTripwires()

        # Test with valid packet
        validation_result = tripwires.validate_packet(valid_packet)
        if validation_result.is_valid:
            print("   ✅ Tripwire validation working for valid packets")
        else:
            print("   ❌ Tripwire validation failed for valid packets")
            return False

        # Test with invalid packet (wrong tool type)
        invalid_tool_packet = MCPPacket(
            tool_type="invalid_service",
            action="create",
            item_type="task",
            payload={"content": "Test task"}
        )

        validation_result = tripwires.validate_packet(invalid_tool_packet)
        if not validation_result.is_valid:
            print("   ✅ Tripwire validation correctly caught invalid tool type")
            print(f"   📝 Validation errors: {len(validation_result.validation_errors)}")
        else:
            print("   ❌ Tripwire validation missed invalid tool type")
            return False

    except Exception as e:
        print(f"   ❌ Tripwire validation test failed: {e}")
        return False

    print("   ✅ Packet validation tests passed")
    return True


async def main():
    """Main test entry point"""
    print("🚀 MCP Packet Server - Basic Functionality Test")
    print("=" * 60)

    # Test packet validation
    if not test_packet_validation():
        print("\n❌ Packet validation tests failed!")
        return False

    # Test basic functionality
    if not await test_basic_functionality():
        print("\n❌ Basic functionality tests failed!")
        return False

    print("\n🎯 SUMMARY")
    print("=" * 30)
    print("✅ Packet system: Working")
    print("✅ Server initialization: Working")
    print("✅ Service listing: Working")
    print("✅ Basic execution: Working")
    print("✅ Schema retrieval: Working")
    print("✅ Validation logic: Working")

    print("\n🎉 All tests passed! Your MCP Packet Server is working correctly.")
    print("🚀 Ready to run the full demo with: python run_demo.py")

    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Tests failed with error: {e}")
        sys.exit(1)
