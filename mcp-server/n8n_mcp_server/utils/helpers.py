"""Helper functions and utilities."""

import base64
import logging
from typing import Any, Dict, Optional, Union


logger = logging.getLogger(__name__)


def safe_decode(data: bytes, encoding: str = "utf-8") -> str:
    """Safely decode bytes to string with fallback to hex.
    
    Args:
        data: Bytes to decode
        encoding: Character encoding to use
        
    Returns:
        str: Decoded string or hex representation if decoding fails
    """
    try:
        return data.decode(encoding)
    except UnicodeDecodeError:
        logger.warning(f"Failed to decode bytes with {encoding}, using hex representation")
        return data.hex()


def format_response(
    success: bool, 
    data: Optional[Any] = None, 
    error: Optional[str] = None,
    message: Optional[str] = None
) -> Dict[str, Any]:
    """Format a standardized response.
    
    Args:
        success: Whether the operation was successful
        data: Response data (if any)
        error: Error message (if any)
        message: Additional message
        
    Returns:
        Dict[str, Any]: Formatted response
    """
    response = {"success": success}
    
    if data is not None:
        response["data"] = data
        
    if error is not None:
        response["error"] = error
        
    if message is not None:
        response["message"] = message
        
    return response


def validate_base64(data: str) -> bool:
    """Validate if string is valid base64.
    
    Args:
        data: String to validate
        
    Returns:
        bool: True if valid base64, False otherwise
    """
    try:
        base64.b64decode(data, validate=True)
        return True
    except Exception:
        return False


def truncate_string(text: str, max_length: int = 100) -> str:
    """Truncate string to maximum length with ellipsis.
    
    Args:
        text: String to truncate
        max_length: Maximum length
        
    Returns:
        str: Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def sanitize_input(data: Union[str, bytes]) -> str:
    """Sanitize input data for logging and processing.
    
    Args:
        data: Input data to sanitize
        
    Returns:
        str: Sanitized string representation
    """
    if isinstance(data, bytes):
        try:
            return data.decode('utf-8')
        except UnicodeDecodeError:
            return f"<binary data: {len(data)} bytes>"
    elif isinstance(data, str):
        # Remove any null bytes or control characters
        return ''.join(char for char in data if ord(char) >= 32 or char in '\t\n\r')
    else:
        return str(data)