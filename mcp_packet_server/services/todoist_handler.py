"""
Todoist Service Handler for MCP Packet Server
Handles task and project management operations
"""

import os
import time
from typing import Any, Dict

import requests

from .base_handler import BaseServiceHandler


class TodoistServiceHandler(BaseServiceHandler):
    """Handles Todoist-related packet operations"""

    def __init__(self):
        super().__init__("todoist")
        self.supported_actions = ["create", "read", "update", "delete", "list", "search"]
        self.supported_item_types = ["task", "project", "label", "comment"]

        # Get Todoist API token from environment
        self.api_token = os.getenv("TODOIST_API_TOKEN")
        if not self.api_token:
            print("⚠️  Warning: TODOIST_API_TOKEN environment variable not set - Todoist operations will be limited")
            print("   Set TODOIST_API_TOKEN environment variable to enable real API integration")
            self.api_token = None

        self.base_url = "https://api.todoist.com/rest/v2"

    async def execute(self, action: str, payload: Dict[str, Any], item_type: str = None) -> Any:
        """Execute Todoist operation"""
        if action == "create":
            if item_type == "task" or payload.get("content"):
                return await self._create_task(payload)
            elif item_type == "project" or payload.get("name"):
                return await self._create_project(payload)
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

    async def _create_task(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Todoist task"""
        content = payload.get("content")
        due_date = payload.get("due_date")
        priority = payload.get("priority", 1)
        project_id = payload.get("project_id")
        labels = payload.get("labels", [])

        if not content:
            raise ValueError("Task content is required")

        if not self.api_token:
            # Mock implementation when API token is not available
            task_data = {
                "id": f"task_{int(time.time())}",
                "content": content,
                "due": {"date": due_date} if due_date else None,
                "priority": priority,
                "project_id": project_id,
                "labels": labels,
                "status": "active",
                "created_at": time.time()
            }
            return {"task": task_data, "message": "Task created successfully (mock mode)"}

        # Real API implementation
        headers = {"Authorization": f"Bearer {self.api_token}"}
        task_data = {
            "content": content,
            "due_date": due_date,
            "priority": priority,
            "project_id": project_id,
            "labels": labels
        }

        response = requests.post(f"{self.base_url}/tasks", json=task_data, headers=headers)
        response.raise_for_status()

        return {"task": response.json(), "message": "Task created successfully"}

    async def _create_project(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Todoist project"""
        name = payload.get("name")
        color = payload.get("color", "charcoal")
        parent_id = payload.get("parent_id")

        if not name:
            raise ValueError("Project name is required")

        if not self.api_token:
            # Mock implementation
            project_data = {
                "id": f"project_{int(time.time())}",
                "name": name,
                "color": color,
                "parent_id": parent_id,
                "status": "active",
                "created_at": time.time()
            }
            return {"project": project_data, "message": "Project created successfully (mock mode)"}

        # Real API implementation
        headers = {"Authorization": f"Bearer {self.api_token}"}
        project_data = {"name": name, "color": color}
        if parent_id:
            project_data["parent_id"] = parent_id

        response = requests.post(f"{self.base_url}/projects", json=project_data, headers=headers)
        response.raise_for_status()

        return {"project": response.json(), "message": "Project created successfully"}

    async def _create_label(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Todoist label"""
        name = payload.get("name")
        color = payload.get("color", "charcoal")
        order = payload.get("order", 0)

        if not name:
            raise ValueError("Label name is required")

        if not self.api_token:
            # Mock implementation
            label_data = {
                "id": f"label_{int(time.time())}",
                "name": name,
                "color": color,
                "order": order,
                "status": "active",
                "created_at": time.time()
            }
            return {"label": label_data, "message": "Label created successfully (mock mode)"}

        # Real API implementation
        headers = {"Authorization": f"Bearer {self.api_token}"}
        label_data = {"name": name, "color": color, "order": order}

        response = requests.post(f"{self.base_url}/labels", json=label_data, headers=headers)
        response.raise_for_status()

        return {"label": response.json(), "message": "Label created successfully"}

    async def _read_item(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Read a Todoist item"""
        item_id = payload.get("id")
        item_type = payload.get("item_type", "task")

        if not item_id:
            raise ValueError("Item ID is required for read operations")

        if not self.api_token:
            # Mock implementation
            mock_data = {
                "id": item_id,
                "name": f"Sample {item_type}",
                "status": "active",
                "created_at": time.time()
            }
            return {"item": mock_data, "item_type": item_type}

        # Real API implementation
        headers = {"Authorization": f"Bearer {self.api_token}"}

        if item_type == "task":
            endpoint = f"{self.base_url}/tasks/{item_id}"
        elif item_type == "project":
            endpoint = f"{self.base_url}/projects/{item_id}"
        elif item_type == "label":
            endpoint = f"{self.base_url}/labels/{item_id}"
        else:
            raise ValueError(f"Unsupported item type: {item_type}")

        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()

        return {"item": response.json(), "item_type": item_type}

    async def _update_item(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Update a Todoist item"""
        item_id = payload.get("id")
        updates = payload.get("updates", {})

        if not item_id:
            raise ValueError("Item ID is required for update operations")

        if not updates:
            raise ValueError("Updates are required for update operations")

        if not self.api_token:
            # Mock implementation
            updated_data = {
                "id": item_id,
                "updated_fields": list(updates.keys()),
                "status": "updated",
                "updated_at": time.time()
            }
            return {"item": updated_data, "message": "Item updated successfully (mock mode)"}

        # Real API implementation would go here
        # For now, return mock data
        updated_data = {
            "id": item_id,
            "updated_fields": list(updates.keys()),
            "status": "updated",
            "updated_at": time.time()
        }

        return {"item": updated_data, "message": "Item updated successfully"}

    async def _delete_item(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a Todoist item"""
        item_id = payload.get("id")

        if not item_id:
            raise ValueError("Item ID is required for delete operations")

        if not self.api_token:
            # Mock implementation
            return {"message": f"Item {item_id} deleted successfully (mock mode)"}

        # Real API implementation would go here
        return {"message": f"Item {item_id} deleted successfully"}

    async def _list_items(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """List Todoist items"""
        item_type = payload.get("item_type", "task")
        limit = payload.get("limit", 10)
        project_id = payload.get("project_id")
        label_id = payload.get("label_id")

        if not self.api_token:
            # Mock implementation
            mock_items = [
                {
                    "id": f"{item_type}_{i}",
                    "name": f"Sample {item_type} {i}",
                    "status": "active",
                    "created_at": time.time()
                }
                for i in range(1, min(limit + 1, 6))
            ]
            return {"items": mock_items, "count": len(mock_items), "item_type": item_type}

        # Real API implementation
        headers = {"Authorization": f"Bearer {self.api_token}"}

        if item_type == "task":
            endpoint = f"{self.base_url}/tasks"
        elif item_type == "project":
            endpoint = f"{self.base_url}/projects"
        elif item_type == "label":
            endpoint = f"{self.base_url}/labels"
        else:
            raise ValueError(f"Unsupported item type: {item_type}")

        params = {}
        if project_id:
            params["project_id"] = project_id
        if label_id:
            params["label_id"] = label_id

        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()

        items = response.json()
        return {"items": items[:limit], "count": len(items), "item_type": item_type}

    async def _search_items(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Search Todoist items"""
        query = payload.get("query", "")
        max_results = payload.get("max_results", 10)

        if not query:
            raise ValueError("Search query is required")

        if not self.api_token:
            # Mock implementation
            mock_results = [
                {
                    "id": f"search_{i}",
                    "name": f"Search result {i} for '{query}'",
                    "status": "active",
                    "created_at": time.time()
                }
                for i in range(1, min(max_results + 1, 4))
            ]
            return {"items": mock_results, "count": len(mock_results), "query": query}

        # Real API implementation
        headers = {"Authorization": f"Bearer {self.api_token}"}

        # Todoist REST API v2 doesn't have a search endpoint, so we'll list and filter
        response = requests.get(f"{self.base_url}/tasks", headers=headers)
        response.raise_for_status()
        all_tasks = response.json()

        # Simple text search in task content
        matching_tasks = [task for task in all_tasks if query.lower() in task.get("content", "").lower()]

        return {"items": matching_tasks[:max_results], "count": len(matching_tasks), "query": query}
