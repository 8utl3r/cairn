"""
MCP Packet - Core communication wrapper for tool interactions
Enhanced with comprehensive error handling and validation
"""

import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


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
class ErrorDetails:
    """Detailed error information for debugging and resolution"""
    error_type: str  # "FORMAT_ERROR", "VALIDATION_ERROR", "EXECUTION_ERROR"
    error_code: str  # Specific error code
    error_message: str  # Human-readable description
    error_location: str  # Where in the packet the error occurred
    field_path: List[str]  # Path to problematic field
    expected_format: Optional[str] = None  # What was expected
    actual_value: Optional[Any] = None  # What was received
    suggestions: List[str] = None  # How to fix it
    severity: str = "ERROR"  # ERROR, WARNING, INFO

    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert error details to dictionary"""
        return {
            'error_type': self.error_type,
            'error_code': self.error_code,
            'error_message': self.error_message,
            'error_location': self.error_location,
            'field_path': self.field_path,
            'expected_format': self.expected_format,
            'actual_value': str(self.actual_value) if self.actual_value is not None else None,
            'suggestions': self.suggestions,
            'severity': self.severity
        }


@dataclass
class ValidationResults:
    """Results of packet validation with detailed error information"""
    is_valid: bool
    validation_errors: List[ErrorDetails] = None
    validation_warnings: List[ErrorDetails] = None
    validation_passed: List[str] = None  # Fields that passed validation
    validation_timestamp: str = None

    def __post_init__(self):
        if self.validation_errors is None:
            self.validation_errors = []
        if self.validation_warnings is None:
            self.validation_warnings = []
        if self.validation_passed is None:
            self.validation_passed = []
        if self.validation_timestamp is None:
            self.validation_timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert validation results to dictionary"""
        return {
            'is_valid': self.is_valid,
            'validation_errors': [error.to_dict() for error in self.validation_errors],
            'validation_warnings': [warning.to_dict() for warning in self.validation_warnings],
            'validation_passed': self.validation_passed,
            'validation_timestamp': self.validation_timestamp
        }


@dataclass
class ProcessingStep:
    """Individual step in packet processing with timing and status"""
    step_name: str
    step_type: str  # "VALIDATION", "ROUTING", "EXECUTION", "ERROR_HANDLING"
    timestamp: str
    status: str  # "SUCCESS", "FAILED", "SKIPPED"
    details: Optional[Dict[str, Any]] = None
    duration_ms: Optional[float] = None
    error_details: Optional[ErrorDetails] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert processing step to dictionary"""
        return {
            'step': self.step_name,
            'type': self.step_type,
            'timestamp': self.timestamp,
            'status': self.status,
            'duration_ms': self.duration_ms,
            'details': self.details,
            'error_details': self.error_details.to_dict() if self.error_details else None
        }


@dataclass
class MCPPacket:
    """Enhanced MCP packet with comprehensive error handling and processing tracking"""

    # Core packet data
    tool_type: str                    # Service type (dynamically discovered from handlers)
    action: str                       # "create", "read", "update", "delete", "list", "search"
    item_type: str                    # "task", "event", "email", "project", "label"
    payload: Dict[str, Any]           # Tool-specific parameters

    # Enhanced metadata
    packet_id: str = None             # Unique identifier
    timestamp: str = None             # ISO timestamp
    priority: PacketPriority = PacketPriority.NORMAL
    user_id: Optional[str] = None     # User context
    session_id: Optional[str] = None  # Session context

    # Status and error tracking
    status: PacketStatus = PacketStatus.PENDING
    error_details: Optional[ErrorDetails] = None
    validation_results: Optional[ValidationResults] = None

    # Debugging and tracing
    processing_log: List[ProcessingStep] = None
    checksum: Optional[str] = None
    version: str = "1.0"

    def __post_init__(self):
        """Initialize default values after dataclass creation"""
        if self.packet_id is None:
            self.packet_id = str(uuid.uuid4())
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()
        if self.processing_log is None:
            self.processing_log = []
        if self.checksum is None:
            self.checksum = self._calculate_checksum()

    def _calculate_checksum(self) -> str:
        """Calculate a simple checksum for packet validation"""
        content = f"{self.tool_type}:{self.action}:{self.item_type}:{json.dumps(self.payload, sort_keys=True)}"
        return str(hash(content))[-8:]  # Simple hash-based checksum

    def add_processing_step(self, step_name: str, step_type: str, status: str,
                           details: Optional[Dict[str, Any]] = None,
                           duration_ms: Optional[float] = None,
                           error_details: Optional[ErrorDetails] = None):
        """Add a processing step to the packet log"""
        step = ProcessingStep(
            step_name=step_name,
            step_type=step_type,
            timestamp=datetime.utcnow().isoformat(),
            status=status,
            details=details,
            duration_ms=duration_ms,
            error_details=error_details
        )
        self.processing_log.append(step)

    def to_dict(self) -> Dict[str, Any]:
        """Convert packet to dictionary for serialization"""
        packet_dict = asdict(self)
        # Convert processing log to serializable format
        if self.processing_log:
            packet_dict['processing_log'] = [step.to_dict() for step in self.processing_log]
        # Convert error details to serializable format
        if self.error_details:
            packet_dict['error_details'] = self.error_details.to_dict()
        # Convert validation results to serializable format
        if self.validation_results:
            packet_dict['validation_results'] = self.validation_results.to_dict()
        return packet_dict

    def to_json(self) -> str:
        """Convert packet to JSON string"""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPPacket':
        """Create packet from dictionary"""
        # Handle processing log reconstruction
        if 'processing_log' in data and data['processing_log']:
            processing_log = []
            for step_data in data['processing_log']:
                step = ProcessingStep(**step_data)
                processing_log.append(step)
            data['processing_log'] = processing_log

        # Handle error details reconstruction
        if 'error_details' in data and data['error_details']:
            data['error_details'] = ErrorDetails(**data['error_details'])

        # Handle validation results reconstruction
        if 'validation_results' in data and data['validation_results']:
            data['validation_results'] = ValidationResults(**data['validation_results'])

        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> 'MCPPacket':
        """Create packet from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def validate(self) -> bool:
        """Basic packet structure validation"""
        required_fields = ['tool_type', 'action', 'item_type']

        for field in required_fields:
            if not getattr(self, field):
                return False

        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert packet to dictionary for JSON serialization"""
        return {
            'tool_type': self.tool_type,
            'action': self.action,
            'item_type': self.item_type,
            'payload': self.payload,
            'packet_id': self.packet_id,
            'timestamp': self.timestamp,
            'priority': self.priority.value if hasattr(self.priority, 'value') else str(self.priority),
            'user_id': self.user_id,
            'session_id': self.session_id,
            'status': self.status.value if hasattr(self.status, 'value') else str(self.status),
            'error_details': self.error_details.to_dict() if self.error_details else None,
            'validation_results': self.validation_results.to_dict() if self.validation_results else None,
            'processing_log': [step.to_dict() for step in self.processing_log] if self.processing_log else [],
            'checksum': self.checksum,
            'version': self.version
        }

    def get_routing_key(self) -> str:
        """Get routing key for packet processing"""
        return f"{self.tool_type}:{self.action}:{self.item_type}"

    def __str__(self) -> str:
        return f"MCPPacket({self.tool_type}:{self.action}:{self.item_type})"

    def __repr__(self) -> str:
        return self.__str__()


@dataclass
class PacketResponse:
    """Enhanced response wrapper for MCP packet execution with debugging information"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None

    # Enhanced debugging information
    packet: Optional[MCPPacket] = None  # Full packet with processing log
    validation_results: Optional[ValidationResults] = None
    execution_duration_ms: Optional[float] = None

    # Server metadata
    server_timestamp: str = None
    server_version: str = "1.0"
    server_instance_id: str = None

    def __post_init__(self):
        if self.server_timestamp is None:
            self.server_timestamp = datetime.utcnow().isoformat()
        if self.server_instance_id is None:
            self.server_instance_id = str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with all debugging information"""
        response = {
            "success": self.success,
            "server_metadata": {
                "timestamp": self.server_timestamp,
                "version": self.server_version,
                "instance_id": self.server_instance_id
            }
        }

        if self.success:
            response["data"] = self.data
            if self.execution_duration_ms:
                response["execution_duration_ms"] = self.execution_duration_ms
        else:
            response["error"] = self.error

        # Always include debugging information
        if self.packet:
            response["packet"] = {
                "packet_id": self.packet.packet_id,
                "status": self.packet.status,
                "processing_log": [
                    {
                        "step": step.step_name,
                        "type": step.step_type,
                        "timestamp": step.timestamp,
                        "status": step.status,
                        "duration_ms": step.duration_ms,
                        "details": step.details,
                        "error_details": step.error_details.to_dict() if step.error_details else None
                    }
                    for step in self.packet.processing_log
                ],
                "error_details": self.packet.error_details.to_dict() if self.packet.error_details else None,
                "validation_results": self.packet.validation_results.to_dict() if self.packet.validation_results else None
            }

        if self.validation_results:
            response["validation_results"] = {
                "is_valid": self.validation_results.is_valid,
                "errors": [error.to_dict() for error in self.validation_results.validation_errors],
                "warnings": [warning.to_dict() for warning in self.validation_results.validation_warnings],
                "passed": self.validation_results.validation_passed,
                "timestamp": self.validation_results.validation_timestamp
            }

        return response

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

        # Test processing step addition
        packet.add_processing_step("test_step", "TESTING", "SUCCESS", {"test": "data"})
        print(f"Processing Log: {len(packet.processing_log)} steps")
