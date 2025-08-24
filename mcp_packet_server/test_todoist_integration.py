#!/usr/bin/env python3
"""
Test script to verify real Todoist integration
"""

import asyncio
import os
import sys

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from service_handlers import TodoistServiceHandler


async def test_todoist_integration():
    """Test the real Todoist integration"""
    print("🧪 Testing Real Todoist Integration")
    print("=" * 50)

    try:
        # Initialize the handler
        print("📱 Initializing Todoist handler...")
        handler = TodoistServiceHandler()
        print("✅ Handler initialized successfully")

        # Test creating a task
        print("\n📝 Testing task creation...")

        task_payload = {
            "content": "Test Task - Real Integration",
            "due_date": "tomorrow at 2pm",
            "priority": 1
        }

        print(f"📝 Creating task: {task_payload['content']}")
        print(f"📅 Due: {task_payload['due_date']}")
        print(f"⭐ Priority: {task_payload['priority']}")

        result = await handler.execute("create", task_payload, "task")

        print(f"📊 Full result: {result}")

        if result["success"]:
            print("✅ Task created successfully!")
            print(f"📊 Result: {result['data']}")

            # Test reading the task back
            print("\n📖 Testing task retrieval...")
            read_payload = {
                "id": result["data"]["task"]["id"],
                "item_type": "task"
            }

            read_result = await handler.execute("read", read_payload)
            if read_result["success"]:
                print("✅ Task retrieved successfully!")
                print(f"📊 Retrieved task: {read_result['data']['item']['content']}")
            else:
                print(f"❌ Task retrieval failed: {read_result['error']}")

            # Test listing tasks
            print("\n📋 Testing task listing...")
            list_payload = {
                "item_type": "task",
                "max_results": 5
            }

            list_result = await handler.execute("list", list_payload)
            if list_result["success"]:
                print(f"✅ Tasks listed successfully! Found {list_result['data']['count']} tasks")
                # Show the first few tasks
                for i, task in enumerate(list_result['data']['items'][:3]):
                    print(f"  {i+1}. {task.get('content', 'No content')} - Priority: {task.get('priority', 'No priority')}")
            else:
                print(f"❌ Task listing failed: {list_result['error']}")

            # Test searching tasks
            print("\n🔍 Testing task search...")
            search_payload = {
                "query": "Test Task",
                "max_results": 5
            }

            search_result = await handler.execute("search", search_payload)
            if search_result["success"]:
                print(f"✅ Task search successful! Found {search_result['data']['count']} matching tasks")
            else:
                print(f"❌ Task search failed: {search_result['error']}")

        else:
            print(f"❌ Task creation failed: {result['error']}")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_todoist_integration())

