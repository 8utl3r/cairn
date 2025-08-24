"""
Gmail Service Handler for MCP Packet Server
Handles email and label management operations
"""

import os
import time
from datetime import datetime
from typing import Any, Dict

from .base_handler import BaseServiceHandler

# Gmail imports (with error handling)
try:
    from google.auth.transport.requests import Request as GmailRequest
    from google.oauth2.credentials import Credentials as GmailCredentials
    from google_auth_oauthlib.flow import InstalledAppFlow as GmailInstalledAppFlow
    from googleapiclient.discovery import build as gmail_build
    from googleapiclient.errors import HttpError as GmailHttpError
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False
    print("⚠️  Warning: Gmail API libraries not available - Gmail operations will be limited")


class GmailServiceHandler(BaseServiceHandler):
    """Handles Gmail-related packet operations"""

    def __init__(self):
        super().__init__("gmail")
        self.supported_actions = ["create", "read", "update", "delete", "list", "search"]
        self.supported_item_types = ["email", "label", "attachment"]

        # Initialize Gmail API client
        self.service = self._get_gmail_service()

    def _get_gmail_service(self):
        """Get authenticated Gmail service"""
        if not GMAIL_AVAILABLE:
            print("⚠️  Warning: Gmail API libraries not available - using mock service")
            return None

        try:
            SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

            creds = None
            # Get credential paths from environment variables
            token_path = os.getenv("GMAIL_TOKEN_PATH", "../gmail/token.json")
            credentials_path = os.getenv("GMAIL_CREDENTIALS_PATH", "../gmail/client_secret.json")

            if os.path.exists(token_path):
                creds = GmailCredentials.from_authorized_user_file(token_path, SCOPES)

            # If there are no (valid) credentials available, let the user log in
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(GmailRequest())
                else:
                    if not os.path.exists(credentials_path):
                        print(f"⚠️  Warning: Gmail credentials file not found: {credentials_path}")
                        print("   Set GMAIL_CREDENTIALS_PATH environment variable to fix this")
                        return None

                    flow = GmailInstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                    creds = flow.run_local_server(port=0)

                # Save the credentials for the next run
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())

            return gmail_build('gmail', 'v1', credentials=creds)
        except Exception as e:
            print(f"⚠️  Warning: Failed to initialize Gmail service: {e}")
            return None

    async def execute(self, action: str, payload: Dict[str, Any], item_type: str = None) -> Any:
        """Execute Gmail operation"""
        if action == "create":
            if item_type == "email" or "to" in payload:
                return await self._create_email(payload)
            elif item_type == "label":
                return await self._create_label(payload)
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

    async def _create_email(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Gmail email (send)"""
        to = payload.get("to", [])
        subject = payload.get("subject", "")
        body = payload.get("body", "")
        cc = payload.get("cc", [])
        bcc = payload.get("bcc", [])

        if not to:
            raise ValueError("Recipient email is required")

        if not subject:
            raise ValueError("Email subject is required")

        if not self.service:
            # Mock implementation when service is not available
            email_data = {
                "id": f"email_{int(time.time())}",
                "to": to,
                "subject": subject,
                "body": body,
                "cc": cc,
                "bcc": bcc,
                "status": "sent",
                "created": datetime.now().isoformat()
            }
            return {"email": email_data, "message": "Email sent successfully (mock mode)"}

        # Real API implementation
        try:
            # Create the email message
            message = self._create_message(to, subject, body, cc, bcc)

            # Send the email
            sent_message = self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()

            return {"email": sent_message, "message": "Email sent successfully"}
        except GmailHttpError as error:
            raise Exception(f"Gmail API error: {error}")

    def _create_message(self, to, subject, body, cc=None, bcc=None):
        """Create a Gmail message"""
        import base64
        from email.mime.text import MIMEText

        message = MIMEText(body)
        message['to'] = ', '.join(to) if isinstance(to, list) else to
        message['subject'] = subject

        if cc:
            message['cc'] = ', '.join(cc) if isinstance(cc, list) else cc
        if bcc:
            message['bcc'] = ', '.join(bcc) if isinstance(bcc, list) else bcc

        return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

    async def _create_label(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Gmail label"""
        name = payload.get("name")
        label_list_visibility = payload.get("label_list_visibility", "labelShow")
        message_list_visibility = payload.get("message_list_visibility", "show")

        if not name:
            raise ValueError("Label name is required")

        if not self.service:
            # Mock implementation
            label_data = {
                "id": f"label_{int(time.time())}",
                "name": name,
                "labelListVisibility": label_list_visibility,
                "messageListVisibility": message_list_visibility,
                "status": "active",
                "created": datetime.now().isoformat()
            }
            return {"label": label_data, "message": "Label created successfully (mock mode)"}

        # Real API implementation
        try:
            label_body = {
                'name': name,
                'labelListVisibility': label_list_visibility,
                'messageListVisibility': message_list_visibility
            }

            label = self.service.users().labels().create(
                userId='me',
                body=label_body
            ).execute()

            return {"label": label, "message": "Label created successfully"}
        except GmailHttpError as error:
            raise Exception(f"Gmail API error: {error}")

    async def _read_item(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Read a Gmail item"""
        item_id = payload.get("id")
        item_type = payload.get("item_type", "email")

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
            if item_type == "email":
                message = self.service.users().messages().get(
                    userId='me',
                    id=item_id
                ).execute()
                return {"item": message, "item_type": item_type}
            elif item_type == "label":
                label = self.service.users().labels().get(
                    userId='me',
                    id=item_id
                ).execute()
                return {"item": label, "item_type": item_type}
            else:
                raise ValueError(f"Unsupported item type: {item_type}")
        except GmailHttpError as error:
            raise Exception(f"Gmail API error: {error}")

    async def _update_item(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Update a Gmail item"""
        item_id = payload.get("id")
        updates = payload.get("updates", {})

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
            # For Gmail, updates typically involve modifying labels
            if 'add_label_ids' in updates or 'remove_label_ids' in updates:
                modify_body = {}
                if 'add_label_ids' in updates:
                    modify_body['addLabelIds'] = updates['add_label_ids']
                if 'remove_label_ids' in updates:
                    modify_body['removeLabelIds'] = updates['remove_label_ids']

                message = self.service.users().messages().modify(
                    userId='me',
                    id=item_id,
                    body=modify_body
                ).execute()

                return {"item": message, "message": "Message updated successfully"}
            else:
                raise ValueError("Gmail updates only support label modifications")
        except GmailHttpError as error:
            raise Exception(f"Gmail API error: {error}")

    async def _delete_item(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a Gmail item"""
        item_id = payload.get("id")

        if not item_id:
            raise ValueError("Item ID is required for delete operations")

        if not self.service:
            # Mock implementation
            return {"message": f"Item {item_id} deleted successfully (mock mode)"}

        # Real API implementation
        try:
            self.service.users().messages().delete(
                userId='me',
                id=item_id
            ).execute()

            # Verify deletion by attempting to fetch the message
            try:
                self.service.users().messages().get(
                    userId='me',
                    id=item_id
                ).execute()
                raise Exception("Message deletion verification failed - message still exists")
            except GmailHttpError as error:
                if error.resp.status == 404:
                    return {"message": f"Message {item_id} deleted and verified successfully"}
                else:
                    raise Exception(f"Unexpected error during deletion verification: {error}")
        except GmailHttpError as error:
            raise Exception(f"Gmail API error: {error}")

    async def _list_items(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """List Gmail items"""
        item_type = payload.get("item_type", "email")
        max_results = payload.get("max_results", 10)

        if not self.service:
            # Mock implementation
            mock_items = [
                {
                    "id": f"{item_type}_{i}",
                    "name": f"Sample {item_type} {i}",
                    "status": "active",
                    "created": datetime.now().isoformat()
                }
                for i in range(1, min(max_results + 1, 6))
            ]
            return {"items": mock_items, "count": len(mock_items), "item_type": item_type}

        # Real API implementation
        try:
            if item_type == "email":
                messages_result = self.service.users().messages().list(
                    userId='me',
                    maxResults=max_results
                ).execute()

                messages = messages_result.get('messages', [])
                return {"items": messages, "count": len(messages)}

            elif item_type == "label":
                labels_result = self.service.users().labels().list(
                    userId='me'
                ).execute()

                labels = labels_result.get('labels', [])
                return {"items": labels, "count": len(labels)}

            else:
                raise ValueError(f"Unsupported item type: {item_type}")
        except GmailHttpError as error:
            raise Exception(f"Gmail API error: {error}")

    async def _search_items(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Search Gmail items"""
        query = payload.get("query", "")
        max_results = payload.get("max_results", 10)

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
            messages_result = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()

            messages = messages_result.get('messages', [])
            return {"items": messages, "count": len(messages), "query": query}
        except GmailHttpError as error:
            raise Exception(f"Gmail API error: {error}")
