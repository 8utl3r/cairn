#!/usr/bin/env python3
"""
Test script to verify real Google Calendar integration
"""

import asyncio
import os
import sys

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta

from service_handlers import GoogleCalendarServiceHandler


async def test_google_calendar_integration():
    """Test the real Google Calendar integration"""
    print("🧪 Testing Real Google Calendar Integration")
    print("=" * 50)

    try:
        # Initialize the handler
        print("📱 Initializing Google Calendar handler...")
        handler = GoogleCalendarServiceHandler()
        print("✅ Handler initialized successfully")

        # Test creating an event
        print("\n📅 Testing event creation...")

        # Create a test event for tomorrow at 2:00 PM
        tomorrow = datetime.now() + timedelta(days=1)
        start_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=1)

        event_payload = {
            "summary": "Test Event - Real Integration",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "description": "This is a test event to verify real Google Calendar integration",
            "location": "Test Location"
        }

        print(f"📝 Creating event: {event_payload['summary']}")
        print(f"🕐 Start: {start_time}")
        print(f"🕐 End: {end_time}")

        result = await handler.execute("create", event_payload, "event")

        print(f"📊 Full result: {result}")

        if result["success"]:
            print("✅ Event created successfully!")
            print(f"📊 Result: {result['data']}")

            # Test reading the event back
            print("\n📖 Testing event retrieval...")
            read_payload = {
                "id": result["data"]["event_id"],
                "item_type": "event"
            }

            read_result = await handler.execute("read", read_payload)
            if read_result["success"]:
                print("✅ Event retrieved successfully!")
                print(f"📊 Retrieved event: {read_result['data']['item']['summary']}")
            else:
                print(f"❌ Event retrieval failed: {read_result['error']}")

            # Test listing events
            print("\n📋 Testing event listing...")
            list_payload = {
                "item_type": "event",
                "max_results": 5
            }

            list_result = await handler.execute("list", list_payload)
            if list_result["success"]:
                print(f"✅ Events listed successfully! Found {list_result['data']['count']} events")
                # Show the first few events
                for i, event in enumerate(list_result['data']['items'][:3]):
                    print(f"  {i+1}. {event.get('summary', 'No summary')} - {event.get('start', {}).get('dateTime', 'No time')}")
            else:
                print(f"❌ Event listing failed: {list_result['error']}")

        else:
            print(f"❌ Event creation failed: {result['error']}")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_google_calendar_integration())
