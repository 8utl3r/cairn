"""
Main MCP server for Cairn - Simplified implementation for Python 3.9
"""

import asyncio
import json
import sys
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from .database import CairnDatabase
from .models import Step, Path, PathExecution, SearchQuery, StepType, StepStatus, PathStatus


class SimpleMCPServer:
    """Simplified MCP server implementation for Python 3.9"""
    
    def __init__(self, db_path: str = "cairn.db"):
        self.db = CairnDatabase(db_path)
        self.tools = self._register_tools()
        self.resources = self._register_resources()
    
    def _register_tools(self) -> Dict[str, Dict[str, Any]]:
        """Register all MCP tools"""
        return {
            "create_path": {
                "name": "create_path",
                "description": "Create a new workflow path",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Name of the path"},
                        "description": {"type": "string", "description": "Description of the path"},
                        "steps": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "description": {"type": "string"},
                                    "step_type": {"type": "string", "enum": ["prompt", "tool_call", "context_injection", "conditional", "loop"]},
                                    "content": {"type": "string"},
                                    "context": {"type": "object"},
                                    "metadata": {"type": "object"}
                                },
                                "required": ["name", "description", "step_type", "content"]
                            }
                        },
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "branch": {"type": "string", "default": "main"}
                    },
                    "required": ["name", "description", "steps"]
                }
            },
            "get_path": {
                "name": "get_path",
                "description": "Get a workflow path by ID and branch",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path_id": {"type": "string", "description": "ID of the path to retrieve"},
                        "branch": {"type": "string", "default": "main", "description": "Branch name"}
                    },
                    "required": ["path_id"]
                }
            },
            "search_paths": {
                "name": "search_paths",
                "description": "Search for workflow paths",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query string"},
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "status": {"type": "string", "enum": ["draft", "active", "deprecated", "archived"]},
                        "limit": {"type": "integer", "default": 50}
                    },
                    "required": ["query"]
                }
            },
            "create_branch": {
                "name": "create_branch",
                "description": "Create a new branch from an existing path",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path_id": {"type": "string", "description": "ID of the base path"},
                        "base_branch": {"type": "string", "description": "Base branch name"},
                        "new_branch": {"type": "string", "description": "New branch name"}
                    },
                    "required": ["path_id", "base_branch", "new_branch"]
                }
            },
            "record_execution": {
                "name": "record_execution",
                "description": "Record the execution of a workflow path",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path_id": {"type": "string", "description": "ID of the executed path"},
                        "success": {"type": "boolean", "description": "Whether execution was successful"},
                        "execution_time": {"type": "number", "description": "Execution time in seconds"},
                        "feedback": {"type": "string", "description": "User feedback"},
                        "user_id": {"type": "string", "description": "User ID"}
                    },
                    "required": ["path_id", "success"]
                }
            }
        }
    
    def _register_resources(self) -> Dict[str, Dict[str, Any]]:
        """Register MCP resources"""
        return {
            "cairn://paths": {
                "uri": "cairn://paths",
                "name": "Available Paths",
                "description": "List of all available workflow paths",
                "mimeType": "application/json"
            }
        }
    
    async def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool calls"""
        if name == "create_path":
            return await self._create_path(**arguments)
        elif name == "get_path":
            return await self._get_path(**arguments)
        elif name == "search_paths":
            return await self._search_paths(**arguments)
        elif name == "create_branch":
            return await self._create_branch(**arguments)
        elif name == "record_execution":
            return await self._record_execution(**arguments)
        else:
            return {"success": False, "error": f"Unknown tool: {name}"}
    
    async def _create_path(self, name: str, description: str, steps: List[Dict[str, Any]], tags: Optional[List[str]] = None, branch: str = "main") -> Dict[str, Any]:
        """Create a new workflow path"""
        try:
            # Convert step dictionaries to Step objects
            step_objects = []
            for step_data in steps:
                step = Step(
                    id=str(uuid.uuid4()),
                    name=step_data["name"],
                    description=step_data["description"],
                    step_type=StepType(step_data["step_type"]),
                    content=step_data["content"],
                    context=step_data.get("context", {}),
                    metadata=step_data.get("metadata", {})
                )
                step_objects.append(step)
            
            path = Path(
                id=str(uuid.uuid4()),
                name=name,
                description=description,
                steps=step_objects,
                tags=tags or [],
                branch=branch
            )
            
            created_path = self.db.create_path(path)
            return {
                "success": True,
                "path_id": created_path.id,
                "message": f"Path '{name}' created successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_path(self, path_id: str, branch: str = "main") -> Dict[str, Any]:
        """Get a workflow path by ID and branch"""
        try:
            path = self.db.get_path(path_id, branch)
            if not path:
                return {
                    "success": False,
                    "error": f"Path not found: {path_id} on branch {branch}"
                }
            
            return {
                "success": True,
                "path": path.dict()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _search_paths(self, query: str, tags: Optional[List[str]] = None, status: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """Search for workflow paths"""
        try:
            search_query = SearchQuery(
                query=query,
                tags=tags,
                status=PathStatus(status) if status else None,
                limit=limit
            )
            
            paths = self.db.search_paths(search_query)
            return {
                "success": True,
                "paths": [path.dict() for path in paths],
                "count": len(paths)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _create_branch(self, path_id: str, base_branch: str, new_branch: str) -> Dict[str, Any]:
        """Create a new branch from an existing path"""
        try:
            new_path = self.db.create_branch(path_id, base_branch, new_branch)
            if not new_path:
                return {
                    "success": False,
                    "error": f"Base path not found: {path_id} on branch {base_branch}"
                }
            
            return {
                "success": True,
                "new_path_id": new_path.id,
                "message": f"Branch '{new_branch}' created from '{base_branch}'"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _record_execution(self, path_id: str, success: bool, execution_time: Optional[float] = None, feedback: Optional[str] = None, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Record the execution of a workflow path"""
        try:
            execution = PathExecution(
                id=str(uuid.uuid4()),
                path_id=path_id,
                user_id=user_id,
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow(),
                success=success,
                execution_time=execution_time,
                feedback=feedback
            )
            
            self.db.record_execution(execution)
            return {
                "success": True,
                "message": "Execution recorded successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools"""
        return list(self.tools.values())
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List available resources"""
        return list(self.resources.values())
    
    def get_resource(self, uri: str) -> Optional[Dict[str, Any]]:
        """Get a specific resource"""
        if uri == "cairn://paths":
            try:
                # Get all active paths
                search_query = SearchQuery(query="", status="active", limit=100)
                paths = self.db.search_paths(search_query)
                
                return {
                    "uri": uri,
                    "name": "Available Paths",
                    "description": f"Found {len(paths)} active workflow paths",
                    "mimeType": "application/json",
                    "content": json.dumps([path.dict() for path in paths], indent=2)
                }
            except Exception:
                return None
        
        # Handle individual path resources
        if uri.startswith("cairn://paths/"):
            path_id = uri.split("/")[-1]
            path = self.db.get_path(path_id)
            if path:
                return {
                    "uri": uri,
                    "name": path.name,
                    "description": path.description,
                    "mimeType": "application/json",
                    "content": json.dumps(path.dict(), indent=2)
                }
        
        return None


async def main():
    """Main entry point for testing"""
    server = SimpleMCPServer()
    
    # Test the server
    print("Cairn MCP Server initialized!")
    print(f"Available tools: {[tool['name'] for tool in server.list_tools()]}")
    print(f"Available resources: {[resource['uri'] for resource in server.list_resources()]}")
    
    # Test creating a simple path
    test_result = await server._create_path(
        name="Test Path",
        description="A test workflow path",
        steps=[
            {
                "name": "Test Step",
                "description": "A test step",
                "step_type": "prompt",
                "content": "This is a test prompt"
            }
        ],
        tags=["test", "example"]
    )
    
    print(f"Test path creation: {test_result}")


if __name__ == "__main__":
    asyncio.run(main())
