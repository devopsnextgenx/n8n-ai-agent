"""Main MCP server implementation using FastMCP.

This module sets up the FastMCP server with HTTP transport and registers
all tools and resources using proper MCP protocol.
"""

import asyncio
import sys
from pathlib import Path
from typing import Any, Dict
from fastmcp import FastMCP
from pydantic import BaseModel, Field

# Add src to path for absolute imports
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from config import get_config
from utils import get_logger
from src.mcp_store.tools.crypto import encrypt_tool, decrypt_tool
from mcp_store.tools.calculator import (
    add_tool, subtract_tool, multiply_tool, divide_tool, modulo_tool
)
from mcp_store.resources.version import get_version_resource
from mcp_store.resources.status import get_status_resource
from mcp_store.resources.tools_list import get_tools_list_resource

logger = get_logger(__name__)


# Pydantic models for MCP tool parameters with comprehensive schemas
class EncryptParams(BaseModel):
    """Parameters for the encrypt tool that converts text to base64 encoding."""
    
    text: str = Field(
        ...,
        description="The plain text string to encode to base64. Can contain any Unicode characters.",
        min_length=1,
        max_length=10000,
        examples=["Hello World", "This is a secret message", "amitkshirsagar"]
    )
    
    class Config:
        json_schema_extra = {
            "title": "Encrypt Tool Parameters",
            "description": "Input parameters for encoding text to base64",
            "examples": [
                {"text": "Hello World"},
                {"text": "This is a secret message"},
                {"text": "amitkshirsagar"}
            ]
        }


class DecryptParams(BaseModel):
    """Parameters for the decrypt tool that converts base64 back to original text."""
    
    encoded_text: str = Field(
        ...,
        description="The base64 encoded string to decode back to original text. Must be valid base64 format.",
        min_length=1,
        pattern=r'^[A-Za-z0-9+/]*={0,2}$',
        examples=["SGVsbG8gV29ybGQ=", "VGhpcyBpcyBhIHNlY3JldCBtZXNzYWdl", "YW1pdGtzaGlyc2FnYXI="]
    )
    
    class Config:
        json_schema_extra = {
            "title": "Decrypt Tool Parameters", 
            "description": "Input parameters for decoding base64 to original text",
            "examples": [
                {"encoded_text": "SGVsbG8gV29ybGQ="},
                {"encoded_text": "VGhpcyBpcyBhIHNlY3JldCBtZXNzYWdl"},
                {"encoded_text": "YW1pdGtzaGlyc2FnYXI="}
            ]
        }


class CalculatorParams(BaseModel):
    """Parameters for calculator tools that perform mathematical operations on two numbers."""
    
    a: float = Field(
        ...,
        description="The first number (operand) for the mathematical operation. Can be integer or decimal.",
        examples=[5.0, 10, 3.14, -2.5]
    )
    
    b: float = Field(
        ...,
        description="The second number (operand) for the mathematical operation. Can be integer or decimal.",
        examples=[3.0, 2, 1.41, -1.5]
    )
    
    class Config:
        json_schema_extra = {
            "title": "Calculator Tool Parameters",
            "description": "Input parameters for mathematical operations between two numbers",
            "examples": [
                {"a": 10, "b": 5},
                {"a": 3.14, "b": 2},
                {"a": -2.5, "b": 1.5}
            ]
        }


class MCPCryptoServer:
    """MCP Crypto Server using FastMCP with proper MCP protocol support."""
    
    def __init__(self):
        """Initialize the MCP server."""
        self.config = get_config()
        # Create FastMCP app with proper MCP protocol support
        # Remove deprecated debug parameter
        self.app = FastMCP(
            name="MCP Crypto Server",
            version="0.1.0"
        )
        self._setup_mcp_tools()
        self._setup_mcp_resources()
        logger.info("MCP Crypto Server initialized with FastMCP")
    
    def _setup_mcp_tools(self) -> None:
        """Set up MCP tools using FastMCP decorators with enhanced metadata."""
        logger.info("Setting up MCP tools")
        
        # Custom handler to process crypto parameters
        def _process_encrypt_params(raw_params):
            """Process encrypt parameters from various formats."""
            logger.info(f"Processing encrypt params: {raw_params} (type: {type(raw_params)})")
            
            if isinstance(raw_params, str):
                # Handle plain string format: "amitkshirsagar"
                return raw_params
            elif isinstance(raw_params, dict):
                # Handle object format: {"text": "amitkshirsagar"}
                if 'text' in raw_params:
                    return raw_params['text']
                else:
                    raise ValueError("Object format requires 'text' property")
            elif hasattr(raw_params, 'text'):
                # Already an EncryptParams object
                return raw_params.text
            else:
                raise ValueError(f"Parameters must be a string or an object with 'text' property. Got: {type(raw_params)}")
        
        def _process_decrypt_params(raw_params):
            """Process decrypt parameters from various formats."""
            logger.info(f"Processing decrypt params: {raw_params} (type: {type(raw_params)})")
            
            if isinstance(raw_params, str):
                # Handle plain string format: "YW1pdGtzaGlyc2FnYXI="
                return raw_params
            elif isinstance(raw_params, dict):
                # Handle object format: {"encoded_text": "YW1pdGtzaGlyc2FnYXI="}
                if 'encoded_text' in raw_params:
                    return raw_params['encoded_text']
                else:
                    raise ValueError("Object format requires 'encoded_text' property")
            elif hasattr(raw_params, 'encoded_text'):
                # Already a DecryptParams object
                return raw_params.encoded_text
            else:
                raise ValueError(f"Parameters must be a string or an object with 'encoded_text' property. Got: {type(raw_params)}")

        # Enhanced Crypto Tools with comprehensive metadata and schemas
        @self.app.tool(
            name="encrypt",
            description="Encode text to base64 format. Accepts either a plain string or an object with 'text' property. Returns success status, encoded result, and length information."
        )
        async def encrypt(params: EncryptParams) -> Dict[str, Any]:
            """
            Encrypt (encode) a plain text string to base64 format.
            
            This tool converts any text string to its base64 encoded representation,
            which is useful for encoding data that needs to be stored or transmitted
            in text-only formats.
            
            Args:
                params: Input parameters containing the text to encode.
                        Can be a string or object with 'text' property.
            
            Returns:
                Dict containing:
                - success: Boolean indicating if operation succeeded
                - encrypted_text: The base64 encoded result
                - original_length: Length of the original text
                - encoded_length: Length of the encoded text
                - error: Error message if operation failed
            
            Examples:
                Input: "Hello World"
                Output: {"success": true, "encrypted_text": "SGVsbG8gV29ybGQ=", ...}
            """
            try:
                text = _process_encrypt_params(params)
                logger.info(f"Encrypt tool called with text length: {len(text)}")
                return await encrypt_tool(text)
            except Exception as e:
                logger.error(f"Error in encrypt tool: {e}")
                return {"success": False, "error": str(e), "encrypted_text": None}
        
        @self.app.tool(
            name="decrypt", 
            description="Decode base64 string back to original text. Accepts either a plain base64 string or an object with 'encoded_text' property. Returns success status, decoded result, and length information."
        )
        async def decrypt(params: DecryptParams) -> Dict[str, Any]:
            """
            Decrypt (decode) a base64 encoded string back to its original text.
            
            This tool converts base64 encoded strings back to their original text format.
            It validates the base64 format before attempting to decode.
            
            Args:
                params: Input parameters containing the base64 text to decode.
                        Can be a string or object with 'encoded_text' property.
            
            Returns:
                Dict containing:
                - success: Boolean indicating if operation succeeded
                - decrypted_text: The decoded original text
                - encoded_length: Length of the base64 input
                - decoded_length: Length of the decoded text
                - error: Error message if operation failed
            
            Examples:
                Input: "SGVsbG8gV29ybGQ="
                Output: {"success": true, "decrypted_text": "Hello World", ...}
            """
            try:
                encoded_text = _process_decrypt_params(params)
                logger.info(f"Decrypt tool called with encoded text length: {len(encoded_text)}")
                return await decrypt_tool(encoded_text)
            except Exception as e:
                logger.error(f"Error in decrypt tool: {e}")
                return {"success": False, "error": str(e), "decrypted_text": None}
        
        # Custom handler to process calculator parameters
        def _process_calculator_params(raw_params):
            """Process calculator parameters from various formats."""
            logger.info(f"Processing calculator params: {raw_params} (type: {type(raw_params)})")
            
            if isinstance(raw_params, list):
                # Handle array format: [3, 4]
                if len(raw_params) != 2:
                    raise ValueError("Calculator requires exactly 2 parameters")
                return raw_params[0], raw_params[1]
            elif isinstance(raw_params, dict):
                # Handle object format: {"a": 3, "b": 4}
                if 'a' not in raw_params or 'b' not in raw_params:
                    raise ValueError("Object format requires 'a' and 'b' properties")
                return raw_params['a'], raw_params['b']
            elif hasattr(raw_params, 'a') and hasattr(raw_params, 'b'):
                # Already a CalculatorParams object
                return raw_params.a, raw_params.b
            else:
                raise ValueError(f"Parameters must be an array of 2 numbers or an object with 'a' and 'b' properties. Got: {type(raw_params)}")
        
        # Enhanced Calculator Tools with comprehensive metadata and schemas
        @self.app.tool(
            name="add",
            description="Add two numbers together. Accepts object {a: number, b: number}. Returns operation details and sum result."
        )
        async def add(params: CalculatorParams):
            """
            Add two numbers and return the sum.
            
            This tool performs basic addition of two numeric values.
            It supports both integers and floating-point numbers.
            
            Args:
                params: Input parameters containing two numbers to add.
                        Can be object {"a": value, "b": value}.
            
            Returns:
                Dict containing:
                - success: Boolean indicating if operation succeeded
                - operation: "add"
                - operand_a: First number
                - operand_b: Second number
                - result: Sum of the two numbers
                - error: Error message if operation failed
            
            Examples:
                Input: {"a": 5, "b": 3}
                Output: {"success": true, "operation": "add", "result": 8, ...}
            """
            try:
                a, b = _process_calculator_params(params)
                logger.info(f"Add tool called: {a} + {b}")
                return await add_tool(a, b)
            except Exception as e:
                logger.error(f"Error in add tool: {e}")
                return {"success": False, "error": str(e), "result": None}
        
        @self.app.tool(
            name="subtract",
            description="Subtract second number from first number. Accepts object {a: minuend, b: subtrahend}. Returns operation details and difference result."
        )
        async def subtract(params: CalculatorParams):
            """
            Subtract the second number from the first number.
            
            This tool performs basic subtraction (a - b) of two numeric values.
            It supports both integers and floating-point numbers.
            
            Args:
                params: Input parameters containing two numbers for subtraction.
                        Can be object {"a": minuend, "b": subtrahend}.
            
            Returns:
                Dict containing:
                - success: Boolean indicating if operation succeeded
                - operation: "subtract"
                - operand_a: First number (minuend)
                - operand_b: Second number (subtrahend)
                - result: Difference (a - b)
                - error: Error message if operation failed
            
            Examples:
                Input: {"a": 10, "b": 3}
                Output: {"success": true, "operation": "subtract", "result": 7, ...}
            """
            try:
                a, b = _process_calculator_params(params)
                logger.info(f"Subtract tool called: {a} - {b}")
                return await subtract_tool(a, b)
            except Exception as e:
                logger.error(f"Error in subtract tool: {e}")
                return {"success": False, "error": str(e), "result": None}
        
        @self.app.tool(
            name="multiply",
            description="Multiply two numbers together. Accepts object {a: number, b: number}. Returns operation details and product result."
        )
        async def multiply(params: CalculatorParams):
            """
            Multiply two numbers and return the product.
            
            This tool performs basic multiplication of two numeric values.
            It supports both integers and floating-point numbers.
            
            Args:
                params: Input parameters containing two numbers to multiply.
                        Can be object {"a": value, "b": value}.
            
            Returns:
                Dict containing:
                - success: Boolean indicating if operation succeeded
                - operation: "multiply"
                - operand_a: First number
                - operand_b: Second number
                - result: Product of the two numbers
                - error: Error message if operation failed
            
            Examples:
                Input: {"a": 4, "b": 5}
                Output: {"success": true, "operation": "multiply", "result": 20, ...}
            """
            try:
                a, b = _process_calculator_params(params)
                logger.info(f"Multiply tool called: {a} * {b}")
                return await multiply_tool(a, b)
            except Exception as e:
                logger.error(f"Error in multiply tool: {e}")
                return {"success": False, "error": str(e), "result": None}
        
        @self.app.tool(
            name="divide",
            description="Divide first number by second number. Accepts object {a: dividend, b: divisor}. Includes division by zero protection. Returns operation details and quotient result."
        )
        async def divide(params: CalculatorParams):
            """
            Divide the first number by the second number.
            
            This tool performs basic division (a / b) of two numeric values.
            It includes protection against division by zero.
            
            Args:
                params: Input parameters containing two numbers for division.
                        Can be object {"a": dividend, "b": divisor}.
            
            Returns:
                Dict containing:
                - success: Boolean indicating if operation succeeded
                - operation: "divide"
                - operand_a: First number (dividend)
                - operand_b: Second number (divisor)
                - result: Quotient (a / b)
                - error: Error message if operation failed (e.g., division by zero)
            
            Examples:
                Input: {"a": 15, "b": 3}
                Output: {"success": true, "operation": "divide", "result": 5, ...}
            """
            try:
                a, b = _process_calculator_params(params)
                logger.info(f"Divide tool called: {a} / {b}")
                return await divide_tool(a, b)
            except Exception as e:
                logger.error(f"Error in divide tool: {e}")
                return {"success": False, "error": str(e), "result": None}
        
        @self.app.tool(
            name="modulo",
            description="Calculate remainder of first number divided by second number. Accepts object {a: dividend, b: divisor}. Includes modulo by zero protection. Returns operation details and remainder result."
        )
        async def modulo(params: CalculatorParams):
            """
            Calculate the modulo (remainder) of dividing the first number by the second.
            
            This tool performs modulo operation (a % b) which returns the remainder
            after dividing the first number by the second number.
            
            Args:
                params: Input parameters containing two numbers for modulo operation.
                        Can be object {"a": dividend, "b": divisor}.
            
            Returns:
                Dict containing:
                - success: Boolean indicating if operation succeeded
                - operation: "modulo"
                - operand_a: First number (dividend)
                - operand_b: Second number (divisor)
                - result: Remainder (a % b)
                - error: Error message if operation failed (e.g., modulo by zero)
            
            Examples:
                Input: {"a": 17, "b": 5}
                Output: {"success": true, "operation": "modulo", "result": 2, ...}
            """
            try:
                a, b = _process_calculator_params(params)
                logger.info(f"Modulo tool called: {a} % {b}")
                return await modulo_tool(a, b)
            except Exception as e:
                logger.error(f"Error in modulo tool: {e}")
                return {"success": False, "error": str(e), "result": None}
        
        logger.info("MCP tools setup completed")
        
        # Add custom HTTP routes for testing (these are separate from MCP protocol)
        self._add_test_routes()
    
    def _setup_mcp_resources(self) -> None:
        """Set up MCP resources using FastMCP decorators with enhanced metadata."""
        logger.info("Setting up MCP resources")
        
        @self.app.resource(
            "resource://mcp/version",
            name="version",
            description="Current MCP server version information including build details and compatibility",
            mime_type="application/json"
        )
        async def version_resource() -> str:
            """
            Get current MCP server version and build information.
            
            This resource provides detailed version information about the MCP server,
            including version number, build timestamp, and compatibility information.
            
            Returns:
                JSON string containing:
                - version: Semantic version string (e.g., "0.1.0")
                - build_time: ISO timestamp of when the server was built
                - mcp_version: MCP protocol version supported
                - fastmcp_version: FastMCP library version used
                - python_version: Python runtime version
                
            Examples:
                {
                    "version": "0.1.0",
                    "build_time": "2025-01-07T12:00:00Z",
                    "mcp_version": "2024-11-05",
                    "fastmcp_version": "2.3.2",
                    "python_version": "3.12.0"
                }
            """
            logger.info("Version resource requested")
            return await get_version_resource()
        
        @self.app.resource(
            "resource://mcp/status",
            name="status",
            description="Current MCP server operational status and health information",
            mime_type="application/json"
        )
        async def status_resource() -> str:
            """
            Get current MCP server operational status and health metrics.
            
            This resource provides real-time information about the server's health,
            uptime, and operational metrics for monitoring and diagnostics.
            
            Returns:
                JSON string containing:
                - status: Overall health status ("healthy", "degraded", "unhealthy")
                - uptime: Server uptime in seconds since startup
                - start_time: ISO timestamp when server started
                - tools_count: Number of registered tools
                - resources_count: Number of registered resources
                - memory_usage: Current memory usage statistics
                - request_count: Total number of requests processed
                
            Examples:
                {
                    "status": "healthy",
                    "uptime": 3600,
                    "start_time": "2025-01-07T12:00:00Z",
                    "tools_count": 7,
                    "resources_count": 3,
                    "memory_usage": {"rss": 45000000, "heap_used": 12000000},
                    "request_count": 127
                }
            """
            logger.info("Status resource requested")
            return await get_status_resource()
        
        @self.app.resource(
            "resource://mcp/tools/list",
            name="tools_list",
            description="Comprehensive list of all available MCP tools with detailed metadata",
            mime_type="application/json"
        )
        async def tools_list_resource() -> str:
            """
            Get comprehensive list of all available MCP tools with their metadata.
            
            This resource provides a complete catalog of all tools registered with
            the MCP server, including their schemas, descriptions, and usage examples.
            
            Returns:
                JSON string containing:
                - tools: Array of tool objects with detailed metadata
                - count: Total number of available tools
                - categories: Tools grouped by category (crypto, calculator, etc.)
                
            Each tool object includes:
                - name: Tool identifier for calling
                - description: Human-readable description of functionality
                - schema: JSON schema for input parameters
                - examples: Example usage scenarios
                - category: Tool category (crypto, math, utility, etc.)
                - return_schema: Expected output format
                
            Examples:
                {
                    "tools": [
                        {
                            "name": "encrypt",
                            "description": "Encode text to base64 format",
                            "category": "crypto",
                            "schema": {...},
                            "examples": [{"text": "Hello"}],
                            "return_schema": {...}
                        }
                    ],
                    "count": 7,
                    "categories": ["crypto", "calculator"]
                }
            """
            logger.info("Tools list resource requested")
            return await get_tools_list_resource()
        
        logger.info("MCP resources setup completed")
    
    def _add_test_routes(self) -> None:
        """Add custom HTTP routes for testing (separate from MCP protocol)."""
        logger.info("Adding test routes for browser access")
        
        # Get the underlying HTTP app and add custom routes
        @self.app.custom_route("/", methods=["GET"])
        async def root_endpoint(request):
            """Root endpoint for testing."""
            from starlette.responses import JSONResponse
            
            # Get tools and resources from FastMCP (these might be async)
            try:
                tools = await self.app.get_tools() if asyncio.iscoroutinefunction(self.app.get_tools) else self.app.get_tools()
                resources = await self.app.get_resources() if asyncio.iscoroutinefunction(self.app.get_resources) else self.app.get_resources()
            except Exception as e:
                logger.warning(f"Could not get tools/resources: {e}")
                tools = []
                resources = []
            
            response_data = {
                "message": "MCP Crypto Server (FastMCP)",
                "status": "running",
                "version": "0.1.0",
                "protocol": "MCP (Model Context Protocol)",
                "mcp_endpoint": "/mcp",
                "test_endpoints": {
                    "root": "GET /",
                    "tools_list": "GET /test/tools",
                    "resources_list": "GET /test/resources", 
                    "health": "GET /test/health"
                },
                "tools_count": len(tools) if tools else 0,
                "resources_count": len(resources) if resources else 0,
                "tools": [{"name": getattr(tool, 'name', str(tool)), "description": getattr(tool, 'description', '')} for tool in (tools or [])],
                "resources": [{"name": getattr(resource, 'name', str(resource)), "description": getattr(resource, 'description', '')} for resource in (resources or [])]
            }
            return JSONResponse(response_data)
        
        @self.app.custom_route("/test/health", methods=["GET"])
        async def health_endpoint(request):
            """Health check endpoint."""
            from starlette.responses import JSONResponse
            return JSONResponse({"status": "healthy", "server": "MCP Crypto Server (FastMCP)"})
        
        @self.app.custom_route("/test/tools", methods=["GET"])
        async def tools_list_endpoint(request):
            """List all registered MCP tools."""
            from starlette.responses import JSONResponse
            try:
                tools = await self.app.get_tools() if asyncio.iscoroutinefunction(self.app.get_tools) else self.app.get_tools()
                response_data = {
                    "tools": [
                        {
                            "name": getattr(tool, 'name', str(tool)),
                            "description": getattr(tool, 'description', ''),
                            "schema": getattr(tool, 'input_schema', None)
                        } for tool in (tools or [])
                    ],
                    "count": len(tools) if tools else 0
                }
                return JSONResponse(response_data)
            except Exception as e:
                logger.error(f"Error getting tools: {e}")
                return JSONResponse({"error": str(e), "tools": [], "count": 0}, status_code=500)
        
        @self.app.custom_route("/test/resources", methods=["GET"])
        async def resources_list_endpoint(request):
            """List all registered MCP resources."""
            from starlette.responses import JSONResponse
            try:
                resources = await self.app.get_resources() if asyncio.iscoroutinefunction(self.app.get_resources) else self.app.get_resources()
                response_data = {
                    "resources": [
                        {
                            "name": getattr(resource, 'name', str(resource)),
                            "description": getattr(resource, 'description', ''),
                            "uri": getattr(resource, 'uri', None),
                            "mime_type": getattr(resource, 'mime_type', None)
                        } for resource in (resources or [])
                    ],
                    "count": len(resources) if resources else 0
                }
                return JSONResponse(response_data)
            except Exception as e:
                logger.error(f"Error getting resources: {e}")
                return JSONResponse({"error": str(e), "resources": [], "count": 0}, status_code=500)
        
        logger.info("Test routes added successfully")
    
    def _add_test_routes(self) -> None:
        """Add custom HTTP routes for testing (separate from MCP protocol)."""
        logger.info("Adding test routes for browser access")
        
        # Get the underlying HTTP app and add custom routes
        @self.app.custom_route("/", methods=["GET"])
        async def root_endpoint(request):
            """Root endpoint for testing."""
            import json
            
            # Get tools and resources from FastMCP (these might be async)
            try:
                tools = await self.app.get_tools() if asyncio.iscoroutinefunction(self.app.get_tools) else self.app.get_tools()
                resources = await self.app.get_resources() if asyncio.iscoroutinefunction(self.app.get_resources) else self.app.get_resources()
            except Exception as e:
                logger.warning(f"Could not get tools/resources: {e}")
                tools = []
                resources = []
            
            return {
                "message": "MCP Crypto Server (FastMCP)",
                "status": "running",
                "version": "0.1.0",
                "protocol": "MCP (Model Context Protocol)",
                "mcp_endpoint": "/mcp",
                "test_endpoints": {
                    "root": "GET /",
                    "tools_list": "GET /test/tools",
                    "resources_list": "GET /test/resources", 
                    "health": "GET /test/health"
                },
                "tools_count": len(tools) if tools else 0,
                "resources_count": len(resources) if resources else 0,
                "tools": [{"name": getattr(tool, 'name', str(tool)), "description": getattr(tool, 'description', '')} for tool in (tools or [])],
                "resources": [{"name": getattr(resource, 'name', str(resource)), "description": getattr(resource, 'description', '')} for resource in (resources or [])]
            }
        
        @self.app.custom_route("/test/health", methods=["GET"])
        async def health_endpoint(request):
            """Health check endpoint."""
            return {"status": "healthy", "server": "MCP Crypto Server (FastMCP)"}
        
        @self.app.custom_route("/test/tools", methods=["GET"])
        async def tools_list_endpoint(request):
            """List all registered MCP tools with enhanced metadata."""
            try:
                tools = await self.app.get_tools() if asyncio.iscoroutinefunction(self.app.get_tools) else self.app.get_tools()
                
                # Enhanced tool information with schemas
                enhanced_tools = []
                for tool in (tools or []):
                    tool_info = {
                        "name": getattr(tool, 'name', str(tool)),
                        "description": getattr(tool, 'description', ''),
                        "input_schema": getattr(tool, 'input_schema', None)
                    }
                    
                    # Add Pydantic schema information if available
                    tool_name = tool_info["name"]
                    if tool_name in ["encrypt"]:
                        tool_info["pydantic_schema"] = EncryptParams.model_json_schema()
                        tool_info["examples"] = [
                            {"text": "Hello World"},
                            {"text": "This is a secret message"}
                        ]
                    elif tool_name in ["decrypt"]:
                        tool_info["pydantic_schema"] = DecryptParams.model_json_schema()
                        tool_info["examples"] = [
                            {"encoded_text": "SGVsbG8gV29ybGQ="},
                            {"encoded_text": "VGhpcyBpcyBhIHNlY3JldCBtZXNzYWdl"}
                        ]
                    elif tool_name in ["add", "subtract", "multiply", "divide", "modulo"]:
                        tool_info["pydantic_schema"] = CalculatorParams.model_json_schema()
                        tool_info["examples"] = [
                            {"a": 10, "b": 5},
                            {"a": 3.14, "b": 2.0}
                        ]
                    
                    enhanced_tools.append(tool_info)
                
                return {
                    "tools": enhanced_tools,
                    "count": len(enhanced_tools),
                    "metadata": {
                        "crypto_tools": ["encrypt", "decrypt"],
                        "calculator_tools": ["add", "subtract", "multiply", "divide", "modulo"],
                        "parameter_formats": {
                            "crypto": "String or {text: string} / {encoded_text: string}",
                            "calculator": "{a: number, b: number}"
                        }
                    }
                }
            except Exception as e:
                logger.error(f"Error getting tools: {e}")
                return {"error": str(e), "tools": [], "count": 0}
        
        @self.app.custom_route("/test/resources", methods=["GET"])
        async def resources_list_endpoint(request):
            """List all registered MCP resources."""
            try:
                resources = await self.app.get_resources() if asyncio.iscoroutinefunction(self.app.get_resources) else self.app.get_resources()
                return {
                    "resources": [
                        {
                            "name": getattr(resource, 'name', str(resource)),
                            "description": getattr(resource, 'description', ''),
                            "uri": getattr(resource, 'uri', None),
                            "mime_type": getattr(resource, 'mime_type', None)
                        } for resource in (resources or [])
                    ],
                    "count": len(resources) if resources else 0
                }
            except Exception as e:
                logger.error(f"Error getting resources: {e}")
                return {"error": str(e), "resources": [], "count": 0}
        
        logger.info("Test routes added successfully")
    
    def get_fastmcp_app(self) -> FastMCP:
        """Get the FastMCP application instance.
        
        Returns:
            FastMCP: The configured FastMCP application
        """
        return self.app
    
    def get_http_app(self):
        """Get the HTTP ASGI app from FastMCP.
        
        Returns:
            The HTTP ASGI application
        """
        return self.app.http_app()
    
    def get_streamable_http_app(self):
        """Get the streamable HTTP ASGI app from FastMCP (for n8n compatibility).
        
        Note: This is deprecated in FastMCP 2.3.2+ but kept for n8n compatibility.
        
        Returns:
            The streamable HTTP ASGI application
        """
        # Suppress deprecation warning since we need this for n8n compatibility
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            return self.app.streamable_http_app()
    
    async def start_server(self, mode: str = "auto") -> None:
        """Start the MCP server with different transport modes.
        
        Args:
            mode: Server mode - "auto", "http", "streamable", "builtin"
                - auto: Try builtin first, fallback to http
                - http: Use http_app() with uvicorn  
                - streamable: Use streamable_http_app() with uvicorn (for n8n)
                - builtin: Use FastMCP's built-in run() method
        """
        host = self.config.server.host
        port = self.config.server.port
        
        logger.info(f"Starting MCP Crypto Server on {host}:{port} (mode: {mode})")
        
        if mode == "builtin" or mode == "auto":
            try:
                logger.info("Attempting to start with FastMCP built-in server...")
                # Use FastMCP's built-in server
                await self.app.run()
                return
            except Exception as e:
                if mode == "builtin":
                    logger.error(f"FastMCP built-in server failed: {str(e)}")
                    raise
                else:
                    logger.warning(f"FastMCP built-in server failed, falling back to HTTP: {str(e)}")
        
        # Fallback to uvicorn with different app modes
        try:
            import uvicorn
            
            if mode == "streamable":
                logger.info("Starting with streamable HTTP app (n8n compatible)...")
                app_to_run = self.get_streamable_http_app()
            else:  # mode == "http" or fallback from "auto"
                logger.info("Starting with standard HTTP app...")
                app_to_run = self.get_http_app()
            
            uvicorn_config = uvicorn.Config(
                app=app_to_run,
                host=host,
                port=port,
                log_level="info",
                access_log=True
            )
            
            server = uvicorn.Server(uvicorn_config)
            await server.serve()
            
        except Exception as e:
            logger.error(f"Failed to start server in {mode} mode: {str(e)}")
            
            if mode != "auto":
                raise
            
            # Final fallback: Use the working FastAPI server
            logger.info("All FastMCP modes failed, using fallback FastAPI server...")
            from fastapi_server import create_fastapi_server
            
            fallback_app = create_fastapi_server()
            
            uvicorn_config = uvicorn.Config(
                app=fallback_app,
                host=host,
                port=port,
                log_level="info",
                access_log=True
            )
            
            server = uvicorn.Server(uvicorn_config)
            await server.serve()
    
    def run_server(self, mode: str = "auto") -> None:
        """Run the MCP server (synchronous version).
        
        Args:
            mode: Server mode - "auto", "http", "streamable", "builtin"
        """
        try:
            asyncio.run(self.start_server(mode))
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Server error: {str(e)}")
            raise


def create_server() -> MCPCryptoServer:
    """Create and configure MCP server instance.
    
    Returns:
        MCPCryptoServer: Configured server instance
    """
    return MCPCryptoServer()


# Create global server instance
mcp_server = create_server()