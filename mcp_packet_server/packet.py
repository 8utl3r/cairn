"""
MCP Packet - Core communication wrapper for tool interactions
"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum


class PacketStatus(str, Enum):
    """Status of MCP packet processing"""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"


class PacketPriority(str, Enum):
    """Priority levels for MCP packets"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class MCPPacket:
    """Standardized MCP packet for tool communication"""
    
    # Header - routing and metadata
    tool_type: str                    # "todoist", "gcal", "gmail"
    action: str                       # "create", "read", "update", "delete", "list", "search"
    item_type: str                    # "task", "event", "email", "project", "label"
    
    # Payload - actual data
    payload: Dict[str, Any]           # Tool-specific parameters
    
    # Metadata
    packet_id: str = None             # Unique identifier
    timestamp: str = None             # ISO timestamp
    priority: PacketPriority = PacketPriority.NORMAL
    user_id: Optional[str] = None     # User context
    session_id: Optional[str] = None  # Session context
    
    # Footer - processing status
    status: PacketStatus = PacketStatus.PENDING
    error_message: Optional[str] = None
    checksum: Optional[str] = None
    
    def __post_init__(self):
        """Initialize default values after dataclass creation"""
        if self.packet_id is None:
            self.packet_id = str(uuid.uuid4())
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()
        if self.checksum is None:
            self.checksum = self._calculate_checksum()
    
    def _calculate_checksum(self) -> str:
        """Calculate a simple checksum for packet validation"""
        content = f"{self.tool_type}:{self.action}:{self.item_type}:{json.dumps(self.payload, sort_keys=True)}"
        return str(hash(content))[-8:]  # Simple hash-based checksum
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert packet to dictionary for serialization"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert packet to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPPacket':
        """Create packet from dictionary"""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'MCPPacket':
        """Create packet from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def validate(self) -> bool:
        """Validate packet structure and content"""
        required_fields = ['tool_type', 'action', 'item_type']
        
        for field in required_fields:
            if not getattr(self, field):
                return False
        
        # Validate tool_type
        valid_tool_types = ['todoist', 'gcal', 'gmail']
        if self.tool_type not in valid_tool_types:
            return False
        
        # Validate action
        valid_actions = ['create', 'read', 'update', 'delete', 'list', 'search']
        if self.action not in valid_actions:
            return False
        
        # Validate item_type based on tool_type
        valid_item_types = {
            'todoist': ['task', 'project', 'label', 'comment'],
            'gcal': ['event', 'calendar', 'reminder'],
            'gmail': ['email', 'label', 'attachment']
        }
        
        if self.item_type not in valid_item_types.get(self.tool_type, []):
            return False
        
        return True
    
    def get_routing_key(self) -> str:
        """Get routing key for packet processing"""
        return f"{self.tool_type}:{self.action}:{self.item_type}"
    
    def __str__(self) -> str:
        return f"MCPPacket({self.tool_type}:{self.action}:{self.item_type})"
    
    def __repr__(self) -> str:
        return self.__str__()


class PacketResponse:
    """Response wrapper for MCP packet execution"""
    
    def __init__(self, packet: MCPPacket, success: bool, data: Any = None, error: str = None):
        self.packet_id = packet.packet_id
        self.success = success
        self.data = data
        self.error = error
        self.timestamp = datetime.utcnow().isoformat()
        self.execution_time = None  # Will be set by executor
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary"""
        return {
            'packet_id': self.packet_id,
            'success': self.success,
            'data': self.data,
            'error': self.error,
            'timestamp': self.timestamp,
            'execution_time': self.execution_time
        }
    
    def to_json(self) -> str:
        """Convert response to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


# Example packet creation
def create_example_packets():
    """Create example packets for testing"""
    
    # Todoist task creation
    todoist_packet = MCPPacket(
        tool_type="todoist",
        action="create",
        item_type="task",
        payload={
            "content": "Buy groceries",
            "due_date": "tomorrow",
            "priority": 1
        }
    )
    
    # Google Calendar event creation
    gcal_packet = MCPPacket(
        tool_type="gcal",
        action="create",
        item_type="event",
        payload={
            "summary": "Team Meeting",
            "start_time": "2024-01-15T10:00:00Z",
            "end_time": "2024-01-15T11:00:00Z",
            "attendees": ["team@company.com"]
        }
    )
    
    # Gmail email search
    gmail_packet = MCPPacket(
        tool_type="gmail",
        action="search",
        item_type="email",
        payload={
            "query": "from:boss@company.com",
            "max_results": 10
        }
    )
    
    return [todoist_packet, gcal_packet, gmail_packet]


if __name__ == "__main__":
    # Test packet creation and validation
    packets = create_example_packets()
    
    for packet in packets:
        print(f"\nPacket: {packet}")
        print(f"Valid: {packet.validate()}")
        print(f"Routing Key: {packet.get_routing_key()}")
        print(f"JSON: {packet.to_json()[:200]}...")
