"""Calculator tool for MCP Server.

This tool provides basic mathematical operations with two inputs.
"""

from typing import Any, Dict, Union
import sys
from pathlib import Path

# Add src to path for absolute imports
src_path = Path(__file__).parent.parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from utils import get_logger

logger = get_logger(__name__)


def _validate_numbers(a: Union[int, float], b: Union[int, float]) -> tuple[bool, str]:
    """Validate that inputs are valid numbers.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Try to convert to float to ensure they're numeric
        float(a)
        float(b)
        return True, ""
    except (TypeError, ValueError) as e:
        return False, f"Invalid number format: {str(e)}"


def _create_result(operation: str, a: Union[int, float], b: Union[int, float], 
                  result: Union[int, float], success: bool = True, 
                  error: str = None) -> Dict[str, Any]:
    """Create a standardized result dictionary.
    
    Args:
        operation: Name of the operation performed
        a: First operand
        b: Second operand
        result: The calculation result
        success: Whether the operation was successful
        error: Error message if any
        
    Returns:
        Standardized result dictionary
    """
    return {
        "success": success,
        "operation": operation,
        "a": a,
        "b": b,
        "result": result,
        "error": error
    }


async def add_tool(a: Union[int, float], b: Union[int, float]) -> Dict[str, Any]:
    """Add two numbers.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Dict containing the addition result or error
    """
    try:
        logger.debug(f"Adding {a} + {b}")
        
        # Validate inputs
        is_valid, error_msg = _validate_numbers(a, b)
        if not is_valid:
            logger.error(f"Invalid inputs for addition: {error_msg}")
            return _create_result("add", a, b, None, False, error_msg)
        
        # Convert to appropriate numeric types
        num_a = float(a) if isinstance(a, str) else a
        num_b = float(b) if isinstance(b, str) else b
        
        result = num_a + num_b
        
        # Return integer if both inputs were integers and result is whole
        if isinstance(a, int) and isinstance(b, int):
            result = int(result)
        
        logger.debug(f"Addition successful: {num_a} + {num_b} = {result}")
        return _create_result("add", num_a, num_b, result)
        
    except Exception as e:
        error_msg = f"Unexpected error during addition: {str(e)}"
        logger.error(error_msg)
        return _create_result("add", a, b, None, False, error_msg)


async def subtract_tool(a: Union[int, float], b: Union[int, float]) -> Dict[str, Any]:
    """Subtract second number from first number.
    
    Args:
        a: First number (minuend)
        b: Second number (subtrahend)
        
    Returns:
        Dict containing the subtraction result or error
    """
    try:
        logger.debug(f"Subtracting {a} - {b}")
        
        # Validate inputs
        is_valid, error_msg = _validate_numbers(a, b)
        if not is_valid:
            logger.error(f"Invalid inputs for subtraction: {error_msg}")
            return _create_result("subtract", a, b, None, False, error_msg)
        
        # Convert to appropriate numeric types
        num_a = float(a) if isinstance(a, str) else a
        num_b = float(b) if isinstance(b, str) else b
        
        result = num_a - num_b
        
        # Return integer if both inputs were integers and result is whole
        if isinstance(a, int) and isinstance(b, int):
            result = int(result)
        
        logger.debug(f"Subtraction successful: {num_a} - {num_b} = {result}")
        return _create_result("subtract", num_a, num_b, result)
        
    except Exception as e:
        error_msg = f"Unexpected error during subtraction: {str(e)}"
        logger.error(error_msg)
        return _create_result("subtract", a, b, None, False, error_msg)


async def multiply_tool(a: Union[int, float], b: Union[int, float]) -> Dict[str, Any]:
    """Multiply two numbers.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Dict containing the multiplication result or error
    """
    try:
        logger.debug(f"Multiplying {a} * {b}")
        
        # Validate inputs
        is_valid, error_msg = _validate_numbers(a, b)
        if not is_valid:
            logger.error(f"Invalid inputs for multiplication: {error_msg}")
            return _create_result("multiply", a, b, None, False, error_msg)
        
        # Convert to appropriate numeric types
        num_a = float(a) if isinstance(a, str) else a
        num_b = float(b) if isinstance(b, str) else b
        
        result = num_a * num_b
        
        # Return integer if both inputs were integers and result is whole
        if isinstance(a, int) and isinstance(b, int):
            result = int(result)
        
        logger.debug(f"Multiplication successful: {num_a} * {num_b} = {result}")
        return _create_result("multiply", num_a, num_b, result)
        
    except Exception as e:
        error_msg = f"Unexpected error during multiplication: {str(e)}"
        logger.error(error_msg)
        return _create_result("multiply", a, b, None, False, error_msg)


async def divide_tool(a: Union[int, float], b: Union[int, float]) -> Dict[str, Any]:
    """Divide first number by second number.
    
    Args:
        a: First number (dividend)
        b: Second number (divisor)
        
    Returns:
        Dict containing the division result or error
    """
    try:
        logger.debug(f"Dividing {a} / {b}")
        
        # Validate inputs
        is_valid, error_msg = _validate_numbers(a, b)
        if not is_valid:
            logger.error(f"Invalid inputs for division: {error_msg}")
            return _create_result("divide", a, b, None, False, error_msg)
        
        # Convert to appropriate numeric types
        num_a = float(a) if isinstance(a, str) else a
        num_b = float(b) if isinstance(b, str) else b
        
        # Check for division by zero
        if num_b == 0:
            error_msg = "Division by zero is not allowed"
            logger.error(error_msg)
            return _create_result("divide", num_a, num_b, None, False, error_msg)
        
        result = num_a / num_b
        
        # Return integer if result is a whole number
        if result.is_integer():
            result = int(result)
        
        logger.debug(f"Division successful: {num_a} / {num_b} = {result}")
        return _create_result("divide", num_a, num_b, result)
        
    except Exception as e:
        error_msg = f"Unexpected error during division: {str(e)}"
        logger.error(error_msg)
        return _create_result("divide", a, b, None, False, error_msg)


async def modulo_tool(a: Union[int, float], b: Union[int, float]) -> Dict[str, Any]:
    """Calculate modulo (remainder) of first number divided by second number.
    
    Args:
        a: First number (dividend)
        b: Second number (divisor)
        
    Returns:
        Dict containing the modulo result or error
    """
    try:
        logger.debug(f"Calculating {a} % {b}")
        
        # Validate inputs
        is_valid, error_msg = _validate_numbers(a, b)
        if not is_valid:
            logger.error(f"Invalid inputs for modulo: {error_msg}")
            return _create_result("modulo", a, b, None, False, error_msg)
        
        # Convert to appropriate numeric types
        num_a = float(a) if isinstance(a, str) else a
        num_b = float(b) if isinstance(b, str) else b
        
        # Check for modulo by zero
        if num_b == 0:
            error_msg = "Modulo by zero is not allowed"
            logger.error(error_msg)
            return _create_result("modulo", num_a, num_b, None, False, error_msg)
        
        result = num_a % num_b
        
        # Return integer if both inputs were integers
        if isinstance(a, int) and isinstance(b, int):
            result = int(result)
        
        logger.debug(f"Modulo successful: {num_a} % {num_b} = {result}")
        return _create_result("modulo", num_a, num_b, result)
        
    except Exception as e:
        error_msg = f"Unexpected error during modulo: {str(e)}"
        logger.error(error_msg)
        return _create_result("modulo", a, b, None, False, error_msg)