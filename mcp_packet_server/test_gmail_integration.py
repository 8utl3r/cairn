#!/usr/bin/env python3
"""
Test script to verify real Gmail integration
"""

import asyncio
import os
import sys

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from service_handlers import GmailServiceHandler


async def test_gmail_integration():
    """Test the real Gmail integration"""
    print("🧪 Testing Real Gmail Integration")
    print("=" * 50)

    try:
        # Initialize the handler
        print("📱 Initializing Gmail handler...")
        handler = GmailServiceHandler()
        print("✅ Handler initialized successfully")

        # Test creating an email draft
        print("\n📧 Testing email draft creation...")

        email_payload = {
            "to": ["test@example.com"],
            "subject": "Test Email - Real Integration",
            "body": "This is a test email to verify real Gmail integration is working."
        }

        print("📧 Creating email draft:")
        print(f"  To: {email_payload['to']}")
        print(f"  Subject: {email_payload['subject']}")
        print(f"  Body: {email_payload['body'][:50]}...")

        result = await handler.execute("create", email_payload, "email")

        print(f"📊 Full result: {result}")

        if result["success"]:
            print("✅ Email draft created successfully!")
            print(f"📊 Result: {result['data']}")

            # Test reading the draft back
            print("\n📖 Testing draft retrieval...")
            read_payload = {
                "id": result["data"]["draft_id"],
                "item_type": "email"
            }

            read_result = await handler.execute("read", read_payload)
            if read_result["success"]:
                print("✅ Draft retrieved successfully!")
                print(f"📊 Retrieved draft ID: {read_result['data']['item']['id']}")
            else:
                print(f"❌ Draft retrieval failed: {read_result['error']}")

            # Test listing drafts
            print("\n📋 Testing draft listing...")
            list_payload = {
                "item_type": "email",
                "max_results": 5
            }

            list_result = await handler.execute("list", list_payload)
            if list_result["success"]:
                print(f"✅ Drafts listed successfully! Found {list_result['data']['count']} drafts")
                # Show the first few drafts
                for i, draft in enumerate(list_result['data']['items'][:3]):
                    print(f"  {i+1}. Draft ID: {draft.get('id', 'No ID')}")
            else:
                print(f"❌ Draft listing failed: {list_result['error']}")

            # Test creating a label
            print("\n🏷️  Testing label creation...")
            label_payload = {
                "name": "Test Label - Real Integration",
                "label_list_visibility": "labelShow",
                "message_list_visibility": "show"
            }

            print(f"🏷️  Creating label: {label_payload['name']}")

            label_result = await handler.execute("create", label_payload, "label")
            if label_result["success"]:
                print("✅ Label created successfully!")
                print(f"📊 Label result: {label_result['data']}")

                # Test listing labels
                print("\n📋 Testing label listing...")
                labels_list_result = await handler.execute("list", {"item_type": "label"})
                if labels_list_result["success"]:
                    print(f"✅ Labels listed successfully! Found {labels_list_result['data']['count']} labels")
                else:
                    print(f"❌ Label listing failed: {labels_list_result['error']}")
            else:
                print(f"❌ Label creation failed: {label_result['error']}")

        else:
            print(f"❌ Email draft creation failed: {result['error']}")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_gmail_integration())

