"""
MCP Packet Validation Tripwires
Comprehensive validation system for catching formatting and input errors
"""

import time
from typing import Dict, Any, List
from packet import MCPPacket, ValidationResults, ErrorDetails, ProcessingStep


class PacketValidationTripwires:
    """Tripwire system for catching formatting and input errors"""
    
    def __init__(self):
        self.tripwires = {
            'required_fields': self._check_required_fields,
            'field_types': self._check_field_types,
            'enum_values': self._check_enum_values,
            'payload_structure': self._check_payload_structure,
            'checksum_validation': self._check_checksum,
            'timestamp_format': self._check_timestamp_format,
            'uuid_format': self._check_uuid_format
        }
    
    def validate_packet(self, packet: MCPPacket) -> ValidationResults:
        """Run all tripwires and collect results"""
        errors = []
        warnings = []
        passed = []
        
        for tripwire_name, tripwire_func in self.tripwires.items():
            try:
                result = tripwire_func(packet)
                if result.is_valid:
                    passed.append(tripwire_name)
                else:
                    # All validation errors are treated as errors (not warnings)
                    errors.extend(result.validation_errors)
                    warnings.extend(result.validation_warnings)
            except Exception as e:
                # Tripwire itself failed - critical error
                errors.append(ErrorDetails(
                    error_type="TRIPWIRE_FAILURE",
                    error_code="TRIPWIRE_CRASH",
                    error_message=f"Tripwire {tripwire_name} crashed: {str(e)}",
                    error_location="validation_system",
                    field_path=["validation"],
                    severity="ERROR"
                ))
        
        return ValidationResults(
            is_valid=len(errors) == 0,
            validation_errors=errors,
            validation_warnings=warnings,
            validation_passed=passed
        )
    
    def _check_required_fields(self, packet: MCPPacket) -> ValidationResults:
        """Tripwire: Check all required fields are present"""
        required_fields = ['tool_type', 'action', 'item_type', 'payload']
        missing_fields = []
        
        for field in required_fields:
            if not hasattr(packet, field) or getattr(packet, field) is None:
                missing_fields.append(field)
        
        if missing_fields:
            return ValidationResults(
                is_valid=False,
                validation_errors=[ErrorDetails(
                    error_type="FORMAT_ERROR",
                    error_code="MISSING_REQUIRED_FIELDS",
                    error_message=f"Missing required fields: {', '.join(missing_fields)}",
                    error_location="packet_root",
                    field_path=missing_fields,
                    expected_format="All required fields must be present",
                    actual_value=f"Missing: {missing_fields}",
                    suggestions=[
                        f"Add missing field: {field}" for field in missing_fields
                    ]
                )]
            )
        
        return ValidationResults(is_valid=True, validation_passed=["required_fields"])
    
    def _check_field_types(self, packet: MCPPacket) -> ValidationResults:
        """Tripwire: Check field data types"""
        type_checks = [
            ('tool_type', str),
            ('action', str),
            ('item_type', str),
            ('payload', dict),
            ('priority', str)
        ]
        
        type_errors = []
        for field_name, expected_type in type_checks:
            if hasattr(packet, field_name):
                value = getattr(packet, field_name)
                if value is not None and not isinstance(value, expected_type):
                    type_errors.append(ErrorDetails(
                        error_type="FORMAT_ERROR",
                        error_code="INVALID_FIELD_TYPE",
                        error_message=f"Field '{field_name}' has wrong type",
                        error_location=field_name,
                        field_path=[field_name],
                        expected_format=f"Type: {expected_type.__name__}",
                        actual_value=f"Type: {type(value).__name__}, Value: {value}",
                        suggestions=[
                            f"Change {field_name} to {expected_type.__name__} type"
                        ]
                    ))
        
        if type_errors:
            return ValidationResults(is_valid=False, validation_errors=type_errors)
        
        return ValidationResults(is_valid=True, validation_passed=["field_types"])
    
    def _check_enum_values(self, packet: MCPPacket) -> ValidationResults:
        """Tripwire: Check enum values are valid"""
        valid_tool_types = ['todoist', 'gcal', 'gmail']
        valid_actions = ['create', 'read', 'update', 'delete', 'list', 'search']
        valid_priorities = ['low', 'normal', 'high', 'critical']
        
        enum_errors = []
        
        # Check tool_type
        if hasattr(packet, 'tool_type') and packet.tool_type:
            if packet.tool_type not in valid_tool_types:
                enum_errors.append(ErrorDetails(
                    error_type="FORMAT_ERROR",
                    error_code="INVALID_TOOL_TYPE",
                    error_message=f"Invalid tool_type: {packet.tool_type}",
                    error_location="tool_type",
                    field_path=["tool_type"],
                    expected_format=f"One of: {', '.join(valid_tool_types)}",
                    actual_value=packet.tool_type,
                    suggestions=[
                        f"Use one of the valid tool types: {', '.join(valid_tool_types)}"
                    ]
                ))
        
        # Check action
        if hasattr(packet, 'action') and packet.action:
            if packet.action not in valid_actions:
                enum_errors.append(ErrorDetails(
                    error_type="FORMAT_ERROR",
                    error_code="INVALID_ACTION",
                    error_message=f"Invalid action: {packet.action}",
                    error_location="action",
                    field_path=["action"],
                    expected_format=f"One of: {', '.join(valid_actions)}",
                    actual_value=packet.action,
                    suggestions=[
                        f"Use one of the valid actions: {', '.join(valid_actions)}"
                    ]
                ))
        
        # Check priority
        if hasattr(packet, 'priority') and packet.priority:
            if packet.priority not in valid_priorities:
                enum_errors.append(ErrorDetails(
                    error_type="FORMAT_ERROR",
                    error_code="INVALID_PRIORITY",
                    error_message=f"Invalid priority: {packet.priority}",
                    error_location="priority",
                    field_path=["priority"],
                    expected_format=f"One of: {', '.join(valid_priorities)}",
                    actual_value=packet.priority,
                    suggestions=[
                        f"Use one of the valid priorities: {', '.join(valid_priorities)}"
                    ]
                ))
        
        if enum_errors:
            return ValidationResults(is_valid=False, validation_errors=enum_errors)
        
        return ValidationResults(is_valid=True, validation_passed=["enum_values"])
    
    def _check_payload_structure(self, packet: MCPPacket) -> ValidationResults:
        """Tripwire: Check payload structure and content"""
        if not hasattr(packet, 'payload') or not packet.payload:
            return ValidationResults(
                is_valid=False,
                validation_errors=[ErrorDetails(
                    error_type="FORMAT_ERROR",
                    error_code="EMPTY_PAYLOAD",
                    error_message="Payload cannot be empty",
                    error_location="payload",
                    field_path=["payload"],
                    expected_format="Non-empty dictionary with service parameters",
                    actual_value="Empty or missing payload",
                    suggestions=[
                        "Add required parameters to payload",
                        "Ensure payload is a valid dictionary"
                    ]
                )]
            )
        
        if not isinstance(packet.payload, dict):
            return ValidationResults(
                is_valid=False,
                validation_errors=[ErrorDetails(
                    error_type="FORMAT_ERROR",
                    error_code="INVALID_PAYLOAD_TYPE",
                    error_message="Payload must be a dictionary",
                    error_location="payload",
                    field_path=["payload"],
                    expected_format="Dictionary type",
                    actual_value=f"Type: {type(packet.payload).__name__}",
                    suggestions=[
                        "Convert payload to dictionary format",
                        "Use key-value pairs for payload parameters"
                    ]
                )]
            )
        
        return ValidationResults(is_valid=True, validation_passed=["payload_structure"])
    
    def _check_checksum(self, packet: MCPPacket) -> ValidationResults:
        """Tripwire: Validate packet checksum"""
        if not hasattr(packet, 'checksum') or not packet.checksum:
            return ValidationResults(
                is_valid=False,
                validation_errors=[ErrorDetails(
                    error_type="FORMAT_ERROR",
                    error_code="MISSING_CHECKSUM",
                    error_message="Packet checksum is missing",
                    error_location="checksum",
                    field_path=["checksum"],
                    expected_format="8-character checksum string",
                    actual_value="Missing checksum",
                    suggestions=[
                        "Generate checksum for packet content",
                        "Ensure packet integrity validation"
                    ]
                )]
            )
        
        # Verify checksum format (8 characters)
        if len(packet.checksum) != 8:
            return ValidationResults(
                is_valid=False,
                validation_errors=[ErrorDetails(
                    error_type="FORMAT_ERROR",
                    error_code="INVALID_CHECKSUM_FORMAT",
                    error_message="Invalid checksum format",
                    error_location="checksum",
                    field_path=["checksum"],
                    expected_format="8-character string",
                    actual_value=f"Length: {len(packet.checksum)}",
                    suggestions=[
                        "Ensure checksum is exactly 8 characters",
                        "Regenerate checksum using proper algorithm"
                    ]
                )]
            )
        
        return ValidationResults(is_valid=True, validation_passed=["checksum_validation"])
    
    def _check_timestamp_format(self, packet: MCPPacket) -> ValidationResults:
        """Tripwire: Validate timestamp format"""
        if not hasattr(packet, 'timestamp') or not packet.timestamp:
            return ValidationResults(
                is_valid=False,
                validation_errors=[ErrorDetails(
                    error_type="FORMAT_ERROR",
                    error_code="MISSING_TIMESTAMP",
                    error_message="Packet timestamp is missing",
                    error_location="timestamp",
                    field_path=["timestamp"],
                    expected_format="ISO 8601 timestamp string",
                    actual_value="Missing timestamp",
                    suggestions=[
                        "Add timestamp to packet",
                        "Use ISO 8601 format (YYYY-MM-DDTHH:MM:SS)"
                    ]
                )]
            )
        
        # Basic ISO format validation
        try:
            from datetime import datetime
            datetime.fromisoformat(packet.timestamp.replace('Z', '+00:00'))
        except ValueError:
            return ValidationResults(
                is_valid=False,
                validation_errors=[ErrorDetails(
                    error_type="FORMAT_ERROR",
                    error_code="INVALID_TIMESTAMP_FORMAT",
                    error_message="Invalid timestamp format",
                    error_location="timestamp",
                    field_path=["timestamp"],
                    expected_format="ISO 8601 format (YYYY-MM-DDTHH:MM:SS)",
                    actual_value=packet.timestamp,
                    suggestions=[
                        "Use ISO 8601 timestamp format",
                        "Example: 2024-01-15T10:30:00Z"
                    ]
                )]
            )
        
        return ValidationResults(is_valid=True, validation_passed=["timestamp_format"])
    
    def _check_uuid_format(self, packet: MCPPacket) -> ValidationResults:
        """Tripwire: Validate UUID format"""
        if not hasattr(packet, 'packet_id') or not packet.packet_id:
            return ValidationResults(
                is_valid=False,
                validation_errors=[ErrorDetails(
                    error_type="FORMAT_ERROR",
                    error_code="MISSING_PACKET_ID",
                    error_message="Packet ID is missing",
                    error_location="packet_id",
                    field_path=["packet_id"],
                    expected_format="UUID string",
                    actual_value="Missing packet ID",
                    suggestions=[
                        "Generate unique packet ID",
                        "Use UUID4 format"
                    ]
                )]
            )
        
        # Basic UUID format validation
        import re
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        if not re.match(uuid_pattern, packet.packet_id, re.IGNORECASE):
            return ValidationResults(
                is_valid=False,
                validation_errors=[ErrorDetails(
                    error_type="FORMAT_ERROR",
                    error_code="INVALID_UUID_FORMAT",
                    error_message="Invalid UUID format",
                    error_location="packet_id",
                    field_path=["packet_id"],
                    expected_format="UUID format (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)",
                    actual_value=packet.packet_id,
                    suggestions=[
                        "Use proper UUID format",
                        "Generate new UUID using uuid.uuid4()"
                    ]
                )]
            )
        
        return ValidationResults(is_valid=True, validation_passed=["uuid_format"])


class ServiceValidationTripwires:
    """Additional tripwires for service-specific validation"""
    
    def __init__(self):
        self.service_handlers = {}
    
    def register_service_handler(self, service_name: str, handler):
        """Register a service handler for validation"""
        self.service_handlers[service_name] = handler
    
    def validate_service_availability(self, packet: MCPPacket) -> ValidationResults:
        """Tripwire: Check if target service is available"""
        if packet.tool_type not in self.service_handlers:
            return ValidationResults(
                is_valid=False,
                validation_errors=[ErrorDetails(
                    error_type="ROUTING_ERROR",
                    error_code="SERVICE_NOT_AVAILABLE",
                    error_message=f"Service '{packet.tool_type}' is not available",
                    error_location="service_routing",
                    field_path=["tool_type"],
                    expected_format=f"Available services: {', '.join(self.service_handlers.keys())}",
                    actual_value=packet.tool_type,
                    suggestions=[
                        f"Use one of the available services: {', '.join(self.service_handlers.keys())}"
                    ]
                )]
            )
        
        return ValidationResults(is_valid=True, validation_passed=["service_availability"])
    
    def validate_action_support(self, packet: MCPPacket) -> ValidationResults:
        """Tripwire: Check if action is supported by the service"""
        if packet.tool_type not in self.service_handlers:
            return ValidationResults(is_valid=True, validation_passed=["action_support"])  # Skip if service not available
        
        handler = self.service_handlers[packet.tool_type]
        if hasattr(handler, 'supported_actions') and packet.action not in handler.supported_actions:
            return ValidationResults(
                is_valid=False,
                validation_errors=[ErrorDetails(
                    error_type="EXECUTION_ERROR",
                    error_code="ACTION_NOT_SUPPORTED",
                    error_message=f"Action '{packet.action}' not supported by {packet.tool_type}",
                    error_location="action_validation",
                    field_path=["action"],
                    expected_format=f"Supported actions: {', '.join(handler.supported_actions)}",
                    actual_value=packet.action,
                    suggestions=[
                        f"Use one of the supported actions: {', '.join(handler.supported_actions)}"
                    ]
                )]
            )
        
        return ValidationResults(is_valid=True, validation_passed=["action_support"])
    
    def validate_item_type_support(self, packet: MCPPacket) -> ValidationResults:
        """Tripwire: Check if item type is supported by the service"""
        if packet.tool_type not in self.service_handlers:
            return ValidationResults(is_valid=True, validation_passed=["item_type_support"])  # Skip if service not available
        
        handler = self.service_handlers[packet.tool_type]
        if hasattr(handler, 'supported_item_types') and packet.item_type not in handler.supported_item_types:
            return ValidationResults(
                is_valid=False,
                validation_errors=[ErrorDetails(
                    error_type="EXECUTION_ERROR",
                    error_code="ITEM_TYPE_NOT_SUPPORTED",
                    error_message=f"Item type '{packet.item_type}' not supported by {packet.tool_type}",
                    error_location="item_type_validation",
                    field_path=["item_type"],
                    expected_format=f"Supported item types: {', '.join(handler.supported_item_types)}",
                    actual_value=packet.item_type,
                    suggestions=[
                        f"Use one of the supported item types: {', '.join(handler.supported_item_types)}"
                    ]
                )]
            )
        
        return ValidationResults(is_valid=True, validation_passed=["item_type_support"])


# Example usage
if __name__ == "__main__":
    # Test the tripwire system
    from packet import MCPPacket
    
    # Create a test packet
    test_packet = MCPPacket(
        tool_type="todoist",
        action="create",
        item_type="task",
        payload={"content": "Test task"}
    )
    
    # Run validation
    tripwires = PacketValidationTripwires()
    results = tripwires.validate_packet(test_packet)
    
    print(f"Validation Results:")
    print(f"Valid: {results.is_valid}")
    print(f"Errors: {len(results.validation_errors)}")
    print(f"Warnings: {len(results.validation_warnings)}")
    print(f"Passed: {len(results.validation_passed)}")
    
    if results.validation_errors:
        print("\nValidation Errors:")
        for error in results.validation_errors:
            print(f"  - {error.error_message} ({error.error_code})")
            print(f"    Location: {error.error_location}")
            print(f"    Suggestions: {', '.join(error.suggestions)}")
