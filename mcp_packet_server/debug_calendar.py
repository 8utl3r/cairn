#!/usr/bin/env python3
"""
Debug script for Google Calendar API integration
"""

import os
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def debug_calendar_api():
    """Debug Google Calendar API directly"""
    print("🔍 Debugging Google Calendar API")
    print("=" * 40)

    # Set up credentials
    SCOPES = ['https://www.googleapis.com/auth/calendar']

    creds = None
    token_path = "../google_calendar/token.json"
    credentials_path = "../google_calendar/client_secret_845546139155-uo8gpt5ftlgqroefmtqhd5t30lqhqjjg.apps.googleusercontent.com.json"

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(f"Google Calendar credentials file not found: {credentials_path}")

            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    calendar_id = "primary"

    try:
        # Test 1: List calendars
        print("📅 Testing calendar listing...")
        calendar_list = service.calendarList().list().execute()
        calendars = calendar_list.get('items', [])
        print(f"Found {len(calendars)} calendars:")
        for calendar in calendars[:3]:
            print(f"  - {calendar.get('summary', 'No name')} ({calendar.get('id', 'No ID')})")

        # Test 2: Create a test event
        print("\n📝 Creating test event...")
        tomorrow = datetime.now() + timedelta(days=1)
        start_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=1)

        event_body = {
            'summary': 'Debug Test Event',
            'description': 'This is a debug test event',
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'America/Chicago',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'America/Chicago',
            },
        }

        print(f"Event details: {start_time} to {end_time}")

        event = service.events().insert(
            calendarId=calendar_id,
            body=event_body
        ).execute()

        print(f"✅ Event created with ID: {event['id']}")
        print(f"Event summary: {event.get('summary', 'No summary')}")
        print(f"Event start: {event.get('start', {}).get('dateTime', 'No start time')}")

        # Test 3: Verify event exists by fetching it
        print("\n🔍 Verifying event exists...")
        verification_event = service.events().get(
            calendarId=calendar_id,
            eventId=event['id']
        ).execute()

        if verification_event:
            print("✅ Event verification successful")
        else:
            print("❌ Event verification failed")

        # Test 4: List events in the time range
        print("\n📋 Listing events in time range...")
        time_min = start_time.isoformat() + 'Z'
        time_max = end_time.isoformat() + 'Z'

        print(f"Searching from {time_min} to {time_max}")

        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])
        print(f"Found {len(events)} events in time range:")

        for i, evt in enumerate(events):
            print(f"  {i+1}. {evt.get('summary', 'No summary')} - {evt.get('start', {}).get('dateTime', 'No time')} (ID: {evt.get('id', 'No ID')})")

        # Test 5: Check if our created event is in the list
        created_event_found = any(e['id'] == event['id'] for e in events)
        print(f"\n🔍 Our created event found in listing: {created_event_found}")

        if not created_event_found:
            print("❌ Event not found in listing - this explains the verification failure!")
            print("Possible causes:")
            print("  1. Time zone conversion issues")
            print("  2. API timing delays")
            print("  3. Calendar ID mismatch")

            # Try listing all events without time filter
            print("\n🔍 Trying to list all events...")
            all_events_result = service.events().list(
                calendarId=calendar_id,
                maxResults=10,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            all_events = all_events_result.get('items', [])
            print(f"Found {len(all_events)} total events:")

            for i, evt in enumerate(all_events):
                print(f"  {i+1}. {evt.get('summary', 'No summary')} - {evt.get('start', {}).get('dateTime', 'No time')} (ID: {evt.get('id', 'No ID')})")

            # Check if our event is in the total list
            event_in_total = any(e['id'] == event['id'] for e in all_events)
            print(f"\n🔍 Our created event found in total listing: {event_in_total}")

        # Clean up: delete the test event
        print("\n🧹 Cleaning up test event...")
        service.events().delete(
            calendarId=calendar_id,
            eventId=event['id']
        ).execute()
        print("✅ Test event deleted")

    except HttpError as error:
        print(f"❌ Google Calendar API error: {error}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_calendar_api()

