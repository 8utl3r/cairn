"""
Base Service Handler for MCP Packet Server
Abstract base class that all service handlers inherit from
"""

import time
from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseServiceHandler(ABC):
    """Base class for all service handlers"""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.supported_actions = []
        self.supported_item_types = []

    @abstractmethod
    async def execute(self, action: str, payload: Dict[str, Any], item_type: str = None) -> Any:
        """Execute the specified action with the given payload and item type"""
        pass

    def supports_action(self, action: str) -> bool:
        """Check if this handler supports the given action"""
        return action in self.supported_actions

    def supports_item_type(self, item_type: str) -> bool:
        """Check if this handler supports the given item type"""
        return item_type in self.supported_item_types

    def _create_response(self, success: bool, data: Any = None, error: str = None, execution_time: float = 0.0) -> Dict[str, Any]:
        """Create a standardized response format"""
        response = {
            "success": success,
            "execution_time": execution_time,
            "service": self.service_name
        }

        if success and data is not None:
            response["result"] = data
        elif not success and error is not None:
            response["error"] = error

        return response

    async def _execute_with_timing(self, action: str, payload: Dict[str, Any], item_type: str = None) -> Dict[str, Any]:
        """Execute operation with timing and error handling"""
        start_time = time.time()

        try:
            result = await self.execute(action, payload, item_type)
            execution_time = time.time() - start_time

            return self._create_response(
                success=True,
                data=result,
                execution_time=execution_time
            )

        except Exception as e:
            execution_time = time.time() - start_time

            return self._create_response(
                success=False,
                error=str(e),
                execution_time=execution_time
            )
