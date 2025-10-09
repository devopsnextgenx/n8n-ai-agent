"""Tools list resource for MCP Crypto Server.

This resource provides static information about available tools.
It serves as a fallback when dynamic tool discovery fails.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add src to path for absolute imports
src_path = Path(__file__).parent.parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from src.utils import get_logger

logger = get_logger(__name__)


async def get_tools_list_resource(app=None) -> str:
    """Get list of available tools, preferably from runtime if app is provided.
    
    This function returns a list of tools with their schemas and examples.
    If a FastMCP app instance is provided, it will dynamically retrieve the tools.
    Otherwise, it will return static hardcoded information as a fallback.
    
    Args:
        app: Optional FastMCP app instance to get registered tools
    
    Returns:
        str: JSON string containing tools information
    """
    try:
        # If app is provided, get tools dynamically
        if app:
            logger.info("Retrieving dynamic tools list information from FastMCP app")
            import asyncio
            from src.mcp_store.tools.tools_list import list_tools
            
            # Get tools dynamically using the same function as the listTools tool
            tools_result = await list_tools(detailed=True, app=app)
            
            if tools_result["success"]:
                tools_info = {
                    "tools": tools_result["tools"],
                    "total_tools": tools_result["count"],
                    "categories": tools_result["categories"],
                    "transport": "http",
                    "api_version": "1.0"
                }
                return json.dumps(tools_info, indent=2)
            else:
                logger.warning(f"Dynamic tools retrieval failed: {tools_result['error']}, using fallback")
        else:
            logger.info("No FastMCP app provided, using static tools list information (fallback)")
        
        # Fallback to static hardcoded tool information
        tools_info = {
            "tools": [
                {
                    "name": "listTools",
                    "description": "Get a list of all available tools with their input/output schemas and descriptions",
                    "parameters": {
                        "detailed": {
                            "type": "boolean",
                            "description": "Whether to include full schema details and examples in the response",
                            "required": False
                        }
                    },
                    "returns": {
                        "success": {"type": "boolean", "description": "Whether operation succeeded"},
                        "tools": {"type": "array", "description": "List of tools with their schemas and descriptions"},
                        "count": {"type": "integer", "description": "Total number of available tools"},
                        "categories": {"type": "array", "description": "Categories of available tools"},
                        "error": {"type": "string", "description": "Error message if operation failed"}
                    },
                    "examples": [
                        {
                            "input": {"detailed": False},
                            "output": {
                                "success": True,
                                "tools": [{"name": "encrypt", "description": "Encrypt string to base64"}],
                                "count": 8,
                                "categories": ["encryption", "calculator"],
                                "error": None
                            }
                        }
                    ]
                },
                {
                    "name": "encrypt",
                    "description": "Encrypt string to base64",
                    "parameters": {
                        "text": {
                            "type": "string",
                            "description": "The string to encode to base64",
                            "required": True
                        }
                    },
                    "returns": {
                        "success": {"type": "boolean", "description": "Whether operation succeeded"},
                        "encrypted_text": {"type": "string", "description": "Base64 encoded result"},
                        "error": {"type": "string", "description": "Error message if failed"},
                        "original_length": {"type": "integer", "description": "Length of original text"},
                        "encoded_length": {"type": "integer", "description": "Length of encoded text"}
                    },
                    "examples": [
                        {
                            "input": {"text": "Hello, World!"},
                            "output": {
                                "success": True,
                                "encrypted_text": "SGVsbG8sIFdvcmxkIQ==",
                                "error": None,
                                "original_length": 13,
                                "encoded_length": 20
                            }
                        }
                    ]
                },
                {
                    "name": "decrypt",
                    "description": "Decrypt base64 string",
                    "parameters": {
                        "encoded_text": {
                            "type": "string",
                            "description": "The base64 encoded string to decode",
                            "required": True
                        }
                    },
                    "returns": {
                        "success": {"type": "boolean", "description": "Whether operation succeeded"},
                        "decrypted_text": {"type": "string", "description": "Decoded original text"},
                        "error": {"type": "string", "description": "Error message if failed"},
                        "encoded_length": {"type": "integer", "description": "Length of encoded text"},
                        "decoded_length": {"type": "integer", "description": "Length of decoded text"}
                    },
                    "examples": [
                        {
                            "input": {"encoded_text": "SGVsbG8sIFdvcmxkIQ=="},
                            "output": {
                                "success": True,
                                "decrypted_text": "Hello, World!",
                                "error": None,
                                "encoded_length": 20,
                                "decoded_length": 13
                            }
                        }
                    ]
                },
                {
                    "name": "add",
                    "description": "Add two numbers",
                    "parameters": {
                        "a": {"type": "number", "description": "First number", "required": True},
                        "b": {"type": "number", "description": "Second number", "required": True}
                    },
                    "returns": {
                        "success": {"type": "boolean", "description": "Whether operation succeeded"},
                        "operation": {"type": "string", "description": "Operation performed"},
                        "a": {"type": "number", "description": "First operand"},
                        "b": {"type": "number", "description": "Second operand"},
                        "result": {"type": "number", "description": "Addition result"},
                        "error": {"type": "string", "description": "Error message if failed"}
                    },
                    "examples": [
                        {
                            "input": {"a": 10, "b": 5},
                            "output": {
                                "success": True,
                                "operation": "add",
                                "a": 10,
                                "b": 5,
                                "result": 15,
                                "error": None
                            }
                        }
                    ]
                },
                {
                    "name": "subtract",
                    "description": "Subtract second number from first",
                    "parameters": {
                        "a": {"type": "number", "description": "First number (minuend)", "required": True},
                        "b": {"type": "number", "description": "Second number (subtrahend)", "required": True}
                    },
                    "returns": {
                        "success": {"type": "boolean", "description": "Whether operation succeeded"},
                        "operation": {"type": "string", "description": "Operation performed"},
                        "a": {"type": "number", "description": "First operand"},
                        "b": {"type": "number", "description": "Second operand"},
                        "result": {"type": "number", "description": "Subtraction result"},
                        "error": {"type": "string", "description": "Error message if failed"}
                    },
                    "examples": [
                        {
                            "input": {"a": 10, "b": 5},
                            "output": {
                                "success": True,
                                "operation": "subtract",
                                "a": 10,
                                "b": 5,
                                "result": 5,
                                "error": None
                            }
                        }
                    ]
                },
                {
                    "name": "multiply",
                    "description": "Multiply two numbers",
                    "parameters": {
                        "a": {"type": "number", "description": "First number", "required": True},
                        "b": {"type": "number", "description": "Second number", "required": True}
                    },
                    "returns": {
                        "success": {"type": "boolean", "description": "Whether operation succeeded"},
                        "operation": {"type": "string", "description": "Operation performed"},
                        "a": {"type": "number", "description": "First operand"},
                        "b": {"type": "number", "description": "Second operand"},
                        "result": {"type": "number", "description": "Multiplication result"},
                        "error": {"type": "string", "description": "Error message if failed"}
                    },
                    "examples": [
                        {
                            "input": {"a": 10, "b": 5},
                            "output": {
                                "success": True,
                                "operation": "multiply",
                                "a": 10,
                                "b": 5,
                                "result": 50,
                                "error": None
                            }
                        }
                    ]
                },
                {
                    "name": "divide",
                    "description": "Divide first number by second",
                    "parameters": {
                        "a": {"type": "number", "description": "First number (dividend)", "required": True},
                        "b": {"type": "number", "description": "Second number (divisor)", "required": True}
                    },
                    "returns": {
                        "success": {"type": "boolean", "description": "Whether operation succeeded"},
                        "operation": {"type": "string", "description": "Operation performed"},
                        "a": {"type": "number", "description": "First operand"},
                        "b": {"type": "number", "description": "Second operand"},
                        "result": {"type": "number", "description": "Division result"},
                        "error": {"type": "string", "description": "Error message if failed"}
                    },
                    "examples": [
                        {
                            "input": {"a": 10, "b": 5},
                            "output": {
                                "success": True,
                                "operation": "divide",
                                "a": 10,
                                "b": 5,
                                "result": 2,
                                "error": None
                            }
                        }
                    ]
                },
                {
                    "name": "modulo",
                    "description": "Calculate remainder of first number divided by second",
                    "parameters": {
                        "a": {"type": "number", "description": "First number (dividend)", "required": True},
                        "b": {"type": "number", "description": "Second number (divisor)", "required": True}
                    },
                    "returns": {
                        "success": {"type": "boolean", "description": "Whether operation succeeded"},
                        "operation": {"type": "string", "description": "Operation performed"},
                        "a": {"type": "number", "description": "First operand"},
                        "b": {"type": "number", "description": "Second operand"},
                        "result": {"type": "number", "description": "Modulo result"},
                        "error": {"type": "string", "description": "Error message if failed"}
                    },
                    "examples": [
                        {
                            "input": {"a": 10, "b": 3},
                            "output": {
                                "success": True,
                                "operation": "modulo",
                                "a": 10,
                                "b": 3,
                                "result": 1,
                                "error": None
                            }
                        }
                    ]
                }
            ],
            "total_tools": 8,
            "categories": ["encryption", "encoding", "base64", "calculator", "mathematics", "discovery"],
            "transport": "http",
            "api_version": "1.0"
        }
        
        logger.info("Tools list information retrieved successfully")
        return json.dumps(tools_info, indent=2)
        
    except Exception as e:
        error_msg = f"Error retrieving tools list: {str(e)}"
        logger.error(error_msg)
        error_response = {
            "error": error_msg,
            "tools": [],
            "total_tools": 0
        }
        return json.dumps(error_response, indent=2)