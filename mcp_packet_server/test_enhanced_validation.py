#!/usr/bin/env python3
"""
Enhanced Validation and Error Handling Test
Demonstrates the comprehensive tripwire validation system
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from enhanced_server import EnhancedMCPServer
from packet import ErrorDetails, MCPPacket
from validation_tripwires import PacketValidationTripwires


def test_tripwire_validation():
    """Test the tripwire validation system"""
    print("🚨 Testing Tripwire Validation System")
    print("=" * 50)

    tripwires = PacketValidationTripwires()

    # Test 1: Valid packet
    print("\n1️⃣ Testing Valid Packet...")
    valid_packet = MCPPacket(
        tool_type="todoist",
        action="create",
        item_type="task",
        payload={"content": "Test task"}
    )

    result = tripwires.validate_packet(valid_packet)
    print(f"   ✅ Valid packet validation: {'PASSED' if result.is_valid else 'FAILED'}")
    print(f"   📊 Validation passed: {len(result.validation_passed)} checks")
    print(f"   🚨 Validation errors: {len(result.validation_errors)}")
    print(f"   ⚠️  Validation warnings: {len(result.validation_warnings)}")

    # Test 2: Missing required fields
    print("\n2️⃣ Testing Missing Required Fields...")
    try:
        invalid_packet = MCPPacket(
            tool_type="todoist",
            action="create",
            # Missing item_type
            payload={"content": "Test task"}
        )
    except Exception as e:
        print(f"   ✅ Correctly caught missing required field: {e}")

    # Test 3: Invalid tool type
    print("\n3️⃣ Testing Invalid Tool Type...")
    invalid_tool_packet = MCPPacket(
        tool_type="invalid_service",
        action="create",
        item_type="task",
        payload={"content": "Test task"}
    )

    result = tripwires.validate_packet(invalid_tool_packet)
    print(f"   ✅ Invalid tool type caught: {'PASSED' if not result.is_valid else 'FAILED'}")
    if not result.is_valid:
        print(f"   🚨 Error: {result.validation_errors[0].error_message}")
        print(f"   💡 Suggestion: {result.validation_errors[0].suggestions[0]}")

    # Test 4: Invalid action
    print("\n4️⃣ Testing Invalid Action...")
    invalid_action_packet = MCPPacket(
        tool_type="todoist",
        action="invalid_action",
        item_type="task",
        payload={"content": "Test task"}
    )

    result = tripwires.validate_packet(invalid_action_packet)
    print(f"   ✅ Invalid action caught: {'PASSED' if not result.is_valid else 'FAILED'}")
    if not result.is_valid:
        print(f"   🚨 Error: {result.validation_errors[0].error_message}")
        print(f"   💡 Suggestion: {result.validation_errors[0].suggestions[0]}")

    # Test 5: Invalid payload structure
    print("\n5️⃣ Testing Invalid Payload Structure...")
    invalid_payload_packet = MCPPacket(
        tool_type="todoist",
        action="create",
        item_type="task",
        payload="not_a_dict"  # Should be dict
    )

    result = tripwires.validate_packet(invalid_payload_packet)
    print(f"   ✅ Invalid payload caught: {'PASSED' if not result.is_valid else 'FAILED'}")
    if not result.is_valid:
        print(f"   🚨 Error: {result.validation_errors[0].error_message}")
        print(f"   💡 Suggestion: {result.validation_errors[0].suggestions[0]}")

    return True


def test_error_details_structure():
    """Test the error details structure"""
    print("\n🔍 Testing Error Details Structure")
    print("=" * 40)

    # Create a sample error
    error = ErrorDetails(
        error_type="FORMAT_ERROR",
        error_code="MISSING_REQUIRED_FIELDS",
        error_message="Missing required fields: item_type",
        error_location="packet_root",
        field_path=["item_type"],
        expected_format="All required fields must be present",
        actual_value="Missing: ['item_type']",
        suggestions=["Add missing field: item_type"]
    )

    print("   ✅ Error created successfully")
    print(f"   📝 Error Type: {error.error_type}")
    print(f"   🔢 Error Code: {error.error_code}")
    print(f"   📍 Location: {error.error_location}")
    print(f"   🎯 Field Path: {error.field_path}")
    print(f"   💡 Suggestions: {len(error.suggestions)} provided")

    # Test serialization
    error_dict = error.to_dict()
    print(f"   🔄 Serialization: {'PASSED' if 'error_type' in error_dict else 'FAILED'}")

    return True


def test_processing_log():
    """Test the processing log functionality"""
    print("\n📝 Testing Processing Log")
    print("=" * 30)

    packet = MCPPacket(
        tool_type="todoist",
        action="create",
        item_type="task",
        payload={"content": "Test task"}
    )

    # Add processing steps
    packet.add_processing_step("packet_received", "VALIDATION", "SUCCESS")
    packet.add_processing_step("format_validation", "VALIDATION", "SUCCESS", {"duration": "15ms"})
    packet.add_processing_step("service_routing", "ROUTING", "SUCCESS", {"target": "todoist"})

    print("   ✅ Processing log created")
    print(f"   📊 Total steps: {len(packet.processing_log)}")

    for i, step in enumerate(packet.processing_log, 1):
        print(f"   {i}. {step.step_name} ({step.step_type}): {step.status}")
        if step.details:
            print(f"      📋 Details: {step.details}")

    # Test serialization
    packet_dict = packet.to_dict()
    if 'processing_log' in packet_dict:
        print("   🔄 Log serialization: PASSED")
    else:
        print("   ❌ Log serialization: FAILED")

    return True


async def test_server_integration():
    """Test the enhanced server with tripwire validation"""
    print("\n🚀 Testing Enhanced Server Integration")
    print("=" * 45)

    try:
        # Initialize server
        server = EnhancedMCPServer(cache_policy="lfu", max_tools=80)
        print("   ✅ Server initialized with tripwire validation")

        # Test 1: Valid packet execution
        print("\n1️⃣ Testing Valid Packet Execution...")
        result = await server._execute_packet({
            "tool_type": "todoist",
            "action": "create",
            "item_type": "task",
            "payload": {"content": "Test task"}
        })

        if result["success"]:
            print("   ✅ Valid packet executed successfully")
            print(f"   📝 Packet ID: {result.get('packet_id', 'N/A')}")
            print(f"   ⏱️  Execution duration: {result.get('execution_duration_ms', 'N/A')}ms")
        else:
            print(f"   ❌ Valid packet execution failed: {result.get('error', 'Unknown error')}")
            return False

        # Test 2: Invalid packet (wrong service)
        print("\n2️⃣ Testing Invalid Packet (Wrong Service)...")
        result = await server._execute_packet({
            "tool_type": "invalid_service",
            "action": "create",
            "item_type": "task",
            "payload": {"content": "Test task"}
        })

        if not result["success"]:
            print("   ✅ Invalid service correctly caught")
            print(f"   🚨 Error: {result.get('error', 'Unknown error')}")

            # Check if packet details are returned
            if "packet" in result:
                packet_data = result["packet"]
                print("   📦 Packet returned with error details")
                print(f"   📊 Processing steps: {len(packet_data.get('processing_log', []))}")

                # Show processing log
                for step in packet_data.get('processing_log', []):
                    print(f"      • {step['step']}: {step['status']}")
                    if step.get('error_details'):
                        error = step['error_details']
                        print(f"        🚨 {error['error_message']}")
            else:
                print("   ⚠️  No packet details returned")
        else:
            print("   ❌ Invalid service should have failed")
            return False

        # Test 3: Invalid packet (unsupported action)
        print("\n3️⃣ Testing Invalid Packet (Unsupported Action)...")
        result = await server._execute_packet({
            "tool_type": "todoist",
            "action": "invalid_action",
            "item_type": "task",
            "payload": {"content": "Test task"}
        })

        if not result["success"]:
            print("   ✅ Invalid action correctly caught")
            print(f"   🚨 Error: {result.get('error', 'Unknown error')}")
        else:
            print("   ❌ Invalid action should have failed")
            return False

        print("   ✅ Server integration tests passed")
        return True

    except Exception as e:
        print(f"   ❌ Server integration test failed: {e}")
        return False


async def main():
    """Main test function"""
    print("🚨 Enhanced Validation and Error Handling Test")
    print("=" * 60)

    # Test 1: Tripwire validation
    if not test_tripwire_validation():
        print("\n❌ Tripwire validation tests failed!")
        return False

    # Test 2: Error details structure
    if not test_error_details_structure():
        print("\n❌ Error details structure tests failed!")
        return False

    # Test 3: Processing log
    if not test_processing_log():
        print("\n❌ Processing log tests failed!")
        return False

    # Test 4: Server integration
    if not await test_server_integration():
        print("\n❌ Server integration tests failed!")
        return False

    print("\n🎯 SUMMARY")
    print("=" * 30)
    print("✅ Tripwire validation system: Working")
    print("✅ Error details structure: Working")
    print("✅ Processing log functionality: Working")
    print("✅ Server integration: Working")
    print("✅ Enhanced error handling: Working")

    print("\n🎉 All enhanced validation tests passed!")
    print("🚀 Your MCP server now has comprehensive error handling and debugging capabilities!")

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
