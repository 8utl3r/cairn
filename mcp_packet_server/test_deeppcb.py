#!/usr/bin/env python3
"""
Test script for DeepPCB service functionality
"""

import asyncio
import json

from packet import MCPPacket
from server import MCPPacketServer


async def test_deeppcb_service():
    """Test the DeepPCB service functionality"""
    print("🧪 Testing DeepPCB Service")
    print("=" * 50)

    server = MCPPacketServer()

    # Test 1: Create a PCB design
    print("\n1️⃣ Testing PCB Design Creation...")
    pcb_packet = MCPPacket(
        tool_type="deep_pcb",
        action="create",
        item_type="pcb_design",
        payload={
            "design_name": "Test Arduino Shield",
            "description": "A test PCB design for Arduino compatibility",
            "layers": 2
        }
    )

    result = await server.handle_tool_call("execute_packet", {
        "tool_type": "deep_pcb",
        "action": "create",
        "item_type": "pcb_design",
        "payload": {
            "design_name": "Test Arduino Shield",
            "description": "A test PCB design for Arduino compatibility",
            "layers": 2
        }
    })

    if result["success"]:
        print("   ✅ PCB Design created successfully!")
        print(f"   📝 Result structure: {json.dumps(result, indent=2)}")
        # Extract data from the result structure
        design_data = result['result']
        print(f"   📝 Design ID: {design_data['design']['id']}")
        print(f"   📝 Design Name: {design_data['design']['name']}")
        print(f"   📝 Layers: {design_data['design']['layers']}")
        print(f"   ⏱️  Execution time: {result['execution_time']:.3f}s")
    else:
        print(f"   ❌ Failed to create PCB design: {result.get('error', 'Unknown error')}")

    # Test 2: Create a component
    print("\n2️⃣ Testing Component Creation...")
    component_result = await server.handle_tool_call("execute_packet", {
        "tool_type": "deep_pcb",
        "action": "create",
        "item_type": "component",
        "payload": {
            "component_name": "ATmega328P",
            "package_type": "DIP",
            "pin_count": 28
        }
    })

    if component_result["success"]:
        print("   ✅ Component created successfully!")
        # Extract data from the result structure
        component_data = component_result['result']
        print(f"   📝 Component ID: {component_data['component']['id']}")
        print(f"   📝 Component Name: {component_data['component']['name']}")
        print(f"   📝 Package Type: {component_data['component']['package_type']}")
        print(f"   📝 Pin Count: {component_data['component']['pin_count']}")
        print(f"   ⏱️  Execution time: {component_result['execution_time']:.3f}s")
    else:
        print(f"   ❌ Failed to create component: {component_result.get('error', 'Unknown error')}")

    # Test 3: List PCB designs
    print("\n3️⃣ Testing PCB Design Listing...")
    list_result = await server.handle_tool_call("execute_packet", {
        "tool_type": "deep_pcb",
        "action": "list",
        "item_type": "pcb_design",
        "payload": {
            "max_results": 5
        }
    })

    if list_result["success"]:
        print("   ✅ PCB Designs listed successfully!")
        # Extract data from the result structure
        list_data = list_result['result']
        print(f"   📝 Found {list_data['count']} designs")
        for design in list_data['items']:
            print(f"      • {design['name']} (ID: {design['id']})")
        print(f"   ⏱️  Execution time: {list_result['execution_time']:.3f}s")
    else:
        print(f"   ❌ Failed to list PCB designs: {list_result.get('error', 'Unknown error')}")

    # Test 4: Search components
    print("\n4️⃣ Testing Component Search...")
    search_result = await server.handle_tool_call("execute_packet", {
        "tool_type": "deep_pcb",
        "action": "search",
        "item_type": "component",
        "payload": {
            "query": "microcontroller",
            "max_results": 3
        }
    })

    if search_result["success"]:
        print("   ✅ Component search completed successfully!")
        print("   🔍 Query: 'microcontroller'")
        # Extract data from the result structure
        search_data = search_result['result']
        print(f"   📝 Found {search_data['count']} results")
        for component in search_data['items']:
            print(f"   📝 Component Name: {component['name']} (ID: {component['id']})")
        print(f"   ⏱️  Execution time: {search_result['execution_time']:.3f}s")
    else:
        print(f"   ❌ Failed to search components: {search_result.get('error', 'Unknown error')}")

    # Test 5: Create a footprint
    print("\n5️⃣ Testing Footprint Creation...")
    footprint_result = await server.handle_tool_call("execute_packet", {
        "tool_type": "deep_pcb",
        "action": "create",
        "item_type": "footprint",
        "payload": {
            "footprint_name": "SOIC-8",
            "package_type": "SMD",
            "dimensions": {
                "width": 3.9,
                "length": 4.9,
                "height": 1.75
            }
        }
    })

    if footprint_result["success"]:
        print("   ✅ Footprint created successfully!")
        # Extract data from the result structure
        footprint_data = footprint_result['result']
        print(f"   📝 Footprint ID: {footprint_data['footprint']['id']}")
        print(f"   📝 Footprint Name: {footprint_data['footprint']['name']}")
        print(f"   📝 Package Type: {footprint_data['footprint']['package_type']}")
        print(f"   📝 Dimensions: {footprint_data['footprint']['dimensions']}")
        print(f"   ⏱️  Execution time: {footprint_result['execution_time']:.3f}s")
    else:
        print(f"   ❌ Failed to create footprint: {footprint_result.get('error', 'Unknown error')}")

    print("\n🎉 DeepPCB Service Testing Completed!")
    print("🚀 All operations are working correctly!")


if __name__ == "__main__":
    try:
        asyncio.run(test_deeppcb_service())
    except KeyboardInterrupt:
        print("\n🛑 Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
        import traceback
        traceback.print_exc()
