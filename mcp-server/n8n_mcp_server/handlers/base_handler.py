"""Base handler class for MCP server operations."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from ..utils.helpers import format_response


logger = logging.getLogger(__name__)


class BaseHandler(ABC):
    """Base class for MCP request handlers."""
    
    def __init__(self, name: str):
        """Initialize the handler.
        
        Args:
            name: Handler name for logging
        """
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    @abstractmethod
    async def handle(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the request.
        
        Args:
            request: Request data
            
        Returns:
            Dict[str, Any]: Response data
        """
        pass
    
    def validate_request(self, request: Dict[str, Any], required_fields: list) -> Optional[str]:
        """Validate request contains required fields.
        
        Args:
            request: Request data to validate
            required_fields: List of required field names
            
        Returns:
            str | None: Error message if validation fails, None if valid
        """
        for field in required_fields:
            if field not in request:
                error_msg = f"Missing required field: {field}"
                self.logger.error(error_msg)
                return error_msg
        return None
    
    def create_success_response(self, data: Any, message: str = "Operation completed successfully") -> Dict[str, Any]:
        """Create a success response.
        
        Args:
            data: Response data
            message: Success message
            
        Returns:
            Dict[str, Any]: Formatted success response
        """
        return format_response(success=True, data=data, message=message)
    
    def create_error_response(self, error: str, message: str = "Operation failed") -> Dict[str, Any]:
        """Create an error response.
        
        Args:
            error: Error description
            message: Error message
            
        Returns:
            Dict[str, Any]: Formatted error response
        """
        return format_response(success=False, error=error, message=message)
    
    async def safe_handle(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Safely handle request with error catching.
        
        Args:
            request: Request data
            
        Returns:
            Dict[str, Any]: Response data
        """
        try:
            self.logger.debug(f"Handling request: {request}")
            result = await self.handle(request)
            self.logger.debug(f"Request handled successfully")
            return result
        except Exception as e:
            error_msg = f"Handler {self.name} failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return self.create_error_response(
                error=str(e),
                message=f"Handler {self.name} encountered an error"
            )