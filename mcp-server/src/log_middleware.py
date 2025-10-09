"""Logging middleware for MCP tools.

This module provides logging middleware functionality to log inputs and outputs 
for all MCP tools.
"""

import functools
import json
import inspect
import sys
import logging
from pathlib import Path
from typing import Any, Callable, Dict, Awaitable

# Add src to path for absolute imports
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Try different import paths based on how the module is used
try:
    from utils import get_logger
except ImportError:
    try:
        from src.utils import get_logger
    except ImportError:
        try:
            from .utils import get_logger
        except ImportError:
            # Fallback to basic logger if all imports fail
            def get_logger(name):
                logger = logging.getLogger(name)
                if not logger.handlers:
                    handler = logging.StreamHandler(sys.stdout)
                    handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
                    logger.addHandler(handler)
                    logger.setLevel(logging.INFO)
                return logger

logger = get_logger(__name__)

def log_tool_calls(func):
    """
    Decorator to log tool inputs and outputs.
    
    This decorator logs the input parameters and result of each tool execution.
    It handles both asynchronous and synchronous functions.
    
    Args:
        func: The tool function to decorate
        
    Returns:
        Wrapped function that logs inputs and outputs
    """
    func_name = func.__name__
    
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        # Get tool name from function or name attribute if available
        tool_name = getattr(func, "__name__", "unknown_tool")
        if hasattr(func, "name") and func.name:
            tool_name = func.name
            
        # Log the input parameters (safely)
        try:
            # Extract and format parameters for logging
            params_dict = {}
            
            # Process positional arguments except self
            if len(args) > 0 and not isinstance(args[0], str) and not hasattr(args[0], '__dict__'):
                # Skip first arg if it's self (instance)
                start_idx = 1
            else:
                start_idx = 0
                
            # Get function signature to identify parameter names
            sig = inspect.signature(func)
            param_names = list(sig.parameters.keys())[start_idx:]
            
            # Match positional args with their parameter names
            for i, arg in enumerate(args[start_idx:]):
                if i < len(param_names):
                    param_name = param_names[i]
                else:
                    param_name = f"arg{i}"
                    
                # Try to get a string representation that's safe to log
                if hasattr(arg, '__dict__'):
                    # For objects, log a summary
                    params_dict[param_name] = f"{arg.__class__.__name__}(...)"
                    # Try to log object attributes if Pydantic model or similar
                    if hasattr(arg, "model_dump"):
                        params_dict[f"{param_name}_data"] = arg.model_dump()
                    elif hasattr(arg, "dict"):
                        params_dict[f"{param_name}_data"] = arg.dict()
                    elif hasattr(arg, "__dict__"):
                        params_dict[f"{param_name}_data"] = arg.__dict__
                else:
                    # For primitive types
                    params_dict[param_name] = arg
                    
            # Add kwargs
            params_dict.update(kwargs)
            
            # Format for logging
            params_str = json.dumps(params_dict, default=str)
            logger.info(f"TOOL INPUT: {tool_name} - Parameters: {params_str}")
        except Exception as e:
            logger.warning(f"Failed to log input for tool {tool_name}: {str(e)}")
        
        # Execute the actual function
        try:
            result = await func(*args, **kwargs)
            
            # Log the result (safely)
            try:
                result_str = json.dumps(result, default=str)
                logger.info(f"TOOL OUTPUT: {tool_name} - Result: {result_str}")
            except Exception as e:
                logger.warning(f"Failed to log output for tool {tool_name}: {str(e)}")
                
            return result
            
        except Exception as e:
            # Log the exception
            logger.error(f"TOOL ERROR: {tool_name} - Exception: {str(e)}")
            raise
            
    # Return the async wrapper
    return async_wrapper