"""
Google Calendar Service Handler for MCP Packet Server
Handles calendar event and calendar management operations
"""

import os
import time
from datetime import datetime
from typing import Any, Dict

from .base_handler import BaseServiceHandler

# Google Calendar imports (with error handling)
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("⚠️  Warning: Google API libraries not available - Google Calendar operations will be limited")


class GoogleCalendarServiceHandler(BaseServiceHandler):
    """Handles Google Calendar-related packet operations"""

    def __init__(self):
        super().__init__("gcal")
        self.supported_actions = ["create", "read", "update", "delete", "list", "search"]
        self.supported_item_types = ["event", "calendar", "reminder"]

        # Initialize Google Calendar API client
        self.service = self._get_calendar_service()
        self.default_calendar_id = "primary"

    def _get_calendar_service(self):
        """Get authenticated Google Calendar service"""
        if not GOOGLE_AVAILABLE:
            print("⚠️  Warning: Google API libraries not available - using mock service")
            return None

        try:
            SCOPES = ['https://www.googleapis.com/auth/calendar']

            creds = None
            # Get credential paths from environment variables
            token_path = os.getenv("GOOGLE_CALENDAR_TOKEN_PATH", "../google_calendar/token.json")
            credentials_path = os.getenv("GOOGLE_CALENDAR_CREDENTIALS_PATH", "../google_calendar/client_secret_845546139155-uo8gpt5ftlgqroefmtqhd5t30lqhqjjg.apps.googleusercontent.com.json")

            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)

            # If there are no (valid) credentials available, let the user log in
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(credentials_path):
                        print(f"⚠️  Warning: Google Calendar credentials file not found: {credentials_path}")
                        print("   Set GOOGLE_CALENDAR_CREDENTIALS_PATH environment variable to fix this")
                        return None

                    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                    creds = flow.run_local_server(port=0)

                # Save the credentials for the next run
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())

            return build('calendar', 'v3', credentials=creds)
        except Exception as e:
            print(f"⚠️  Warning: Failed to initialize Google Calendar service: {e}")
            return None

    async def execute(self, action: str, payload: Dict[str, Any], item_type: str = None) -> Any:
        """Execute Google Calendar operation"""
        if action == "create":
            if item_type == "event" or "summary" in payload:
                return await self._create_event(payload)
            elif item_type == "calendar":
                return await self._create_calendar(payload)
            else:
                raise ValueError(f"Unsupported item type for creation: {item_type}")

        elif action == "read":
            return await self._read_item(payload)

        elif action == "update":
            return await self._update_item(payload)

        elif action == "delete":
            return await self._delete_item(payload)

        elif action == "list":
            return await self._list_items(payload)

        elif action == "search":
            return await self._search_items(payload)

        else:
            raise ValueError(f"Unsupported action: {action}")

    async def _create_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Google Calendar event"""
        summary = payload.get("summary", "")
        start_time_str = payload.get("start_time")
        end_time_str = payload.get("end_time")
        attendees = payload.get("attendees", [])
        description = payload.get("description", "")
        location = payload.get("location", "")

        if not summary:
            raise ValueError("Event summary is required")

        if not self.service:
            # Mock implementation when service is not available
            event_data = {
                "id": f"event_{int(time.time())}",
                "summary": summary,
                "start": {"dateTime": start_time_str} if start_time_str else None,
                "end": {"dateTime": end_time_str} if end_time_str else None,
                "attendees": attendees,
                "description": description,
                "location": location,
                "status": "confirmed",
                "created": datetime.now().isoformat()
            }
            return {"event": event_data, "message": "Event created successfully (mock mode)"}

        # Real API implementation
        try:
            # Parse and validate time strings
            start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
        except ValueError as e:
            raise ValueError(f"Invalid time format: {e}. Expected ISO format (e.g., 2024-12-19T16:20:00-06:00)")

        # Convert to RFC3339 format for Google Calendar API
        start_time_rfc3339 = start_time.isoformat()
        end_time_rfc3339 = end_time.isoformat()

        event_body = {
            "summary": summary,
            "start": {"dateTime": start_time_rfc3339},
            "end": {"dateTime": end_time_rfc3339},
            "description": description,
            "location": location
        }

        if attendees:
            event_body["attendees"] = [{"email": email} for email in attendees]

        event = self.service.events().insert(
            calendarId=self.default_calendar_id,
            body=event_body
        ).execute()

        return {"event": event, "message": "Event created successfully"}

    async def _create_calendar(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Google Calendar"""
        summary = payload.get("summary", "")
        description = payload.get("description", "")
        timezone_str = payload.get("timezone", "UTC")

        if not summary:
            raise ValueError("Calendar summary is required")

        if not self.service:
            # Mock implementation
            calendar_data = {
                "id": f"calendar_{int(time.time())}",
                "summary": summary,
                "description": description,
                "timeZone": timezone_str,
                "status": "active",
                "created": datetime.now().isoformat()
            }
            return {"calendar": calendar_data, "message": "Calendar created successfully (mock mode)"}

        # Real API implementation
        calendar_body = {
            "summary": summary,
            "description": description,
            "timeZone": timezone_str
        }

        calendar = self.service.calendars().insert(body=calendar_body).execute()

        return {"calendar": calendar, "message": "Calendar created successfully"}

    async def _read_item(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Read a Google Calendar item"""
        item_id = payload.get("id")
        item_type = payload.get("item_type", "event")
        calendar_id = payload.get("calendar_id", self.default_calendar_id)

        if not item_id:
            raise ValueError("Item ID is required for read operations")

        if not self.service:
            # Mock implementation
            mock_data = {
                "id": item_id,
                "name": f"Sample {item_type}",
                "status": "active",
                "created": datetime.now().isoformat()
            }
            return {"item": mock_data, "item_type": item_type}

        # Real API implementation
        try:
            if item_type == "event":
                event = self.service.events().get(
                    calendarId=calendar_id,
                    eventId=item_id
                ).execute()
                return {"item": event, "item_type": item_type}
            elif item_type == "calendar":
                calendar = self.service.calendars().get(calendarId=item_id).execute()
                return {"item": calendar, "item_type": item_type}
            else:
                raise ValueError(f"Unsupported item type: {item_type}")
        except HttpError as error:
            raise Exception(f"Google Calendar API error: {error}")

    async def _update_item(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Update a Google Calendar item"""
        item_id = payload.get("id")
        updates = payload.get("updates", {})
        calendar_id = payload.get("calendar_id", self.default_calendar_id)

        if not item_id:
            raise ValueError("Item ID is required for update operations")

        if not updates:
            raise ValueError("Updates are required for update operations")

        if not self.service:
            # Mock implementation
            updated_data = {
                "id": item_id,
                "updated_fields": list(updates.keys()),
                "status": "updated",
                "updated": datetime.now().isoformat()
            }
            return {"item": updated_data, "message": "Item updated successfully (mock mode)"}

        # Real API implementation
        try:
            # For events, we need to get the current event first
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=item_id
            ).execute()

            # Update the event with new data
            event.update(updates)

            updated_event = self.service.events().update(
                calendarId=calendar_id,
                eventId=item_id,
                body=event
            ).execute()

            return {"item": updated_event, "message": "Event updated successfully"}
        except HttpError as error:
            raise Exception(f"Google Calendar API error: {error}")

    async def _delete_item(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a Google Calendar item"""
        item_id = payload.get("id")
        calendar_id = payload.get("calendar_id", self.default_calendar_id)

        if not item_id:
            raise ValueError("Item ID is required for delete operations")

        if not self.service:
            # Mock implementation
            return {"message": f"Item {item_id} deleted successfully (mock mode)"}

        # Real API implementation
        try:
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=item_id
            ).execute()

            return {"message": f"Event {item_id} deleted successfully"}
        except HttpError as error:
            raise Exception(f"Google Calendar API error: {error}")

    async def _list_items(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """List Google Calendar items"""
        item_type = payload.get("item_type", "event")
        limit = payload.get("limit", 10)
        calendar_id = payload.get("calendar_id", self.default_calendar_id)

        if not self.service:
            # Mock implementation
            mock_items = [
                {
                    "id": f"{item_type}_{i}",
                    "name": f"Sample {item_type} {i}",
                    "status": "active",
                    "created": datetime.now().isoformat()
                }
                for i in range(1, min(limit + 1, 6))
            ]
            return {"items": mock_items, "count": len(mock_items), "item_type": item_type}

        # Real API implementation
        try:
            if item_type == "event":
                now = datetime.utcnow().isoformat() + 'Z'
                events_result = self.service.events().list(
                    calendarId=calendar_id,
                    timeMin=now,
                    maxResults=limit,
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()

                events = events_result.get('items', [])
                return {"items": events, "count": len(events), "item_type": item_type}
            elif item_type == "calendar":
                calendars_result = self.service.calendarList().list().execute()
                calendars = calendars_result.get('items', [])
                return {"items": calendars[:limit], "count": len(calendars), "item_type": item_type}
            else:
                raise ValueError(f"Unsupported item type: {item_type}")
        except HttpError as error:
            raise Exception(f"Google Calendar API error: {error}")

    async def _search_items(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Search Google Calendar items"""
        query = payload.get("query", "")
        max_results = payload.get("max_results", 10)
        calendar_id = payload.get("calendar_id", self.default_calendar_id)

        if not query:
            raise ValueError("Search query is required")

        if not self.service:
            # Mock implementation
            mock_results = [
                {
                    "id": f"search_{i}",
                    "name": f"Search result {i} for '{query}'",
                    "status": "active",
                    "created": datetime.now().isoformat()
                }
                for i in range(1, min(max_results + 1, 4))
            ]
            return {"items": mock_results, "count": len(mock_results), "query": query}

        # Real API implementation
        try:
            now = datetime.utcnow().isoformat() + 'Z'
            events_result = self.service.events().list(
                calendarId=calendar_id,
                q=query,
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])
            return {"items": events, "count": len(events), "query": query}
        except HttpError as error:
            raise Exception(f"Google Calendar API error: {error}")
