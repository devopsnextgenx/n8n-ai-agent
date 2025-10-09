"""Main MCP server implementation using FastMCP.

This module sets up the FastMCP server with HTTP transport and registers
all tools and resources using proper MCP protocol.
"""

import asyncio
import sys
import json
from pathlib import Path
from typing import Any, Dict, Callable, Awaitable, Optional
from functools import wraps
from fastmcp import FastMCP
from pydantic import BaseModel, Field

# Add src to path for absolute imports
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from config import get_config
from utils import get_logger
from src.mcp_store.tools.crypto import encrypt_tool, decrypt_tool
from src.log_middleware import log_tool_calls
from mcp_store.tools.calculator import (
    add_tool, subtract_tool, multiply_tool, divide_tool, modulo_tool
)
from mcp_store.resources.version import get_version_resource
from mcp_store.resources.status import get_status_resource
from mcp_store.resources.tools_list import get_tools_list_resource
from mcp_store.tools.ScriptExecutor import run_script
from src.mcp_store.tools.tools_list import list_tools

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
            logger.debug(f"Processing decrypt params: {raw_params} (type: {type(raw_params)})")
            
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

        @self.app.tool(name="executeScript", description="Execute a script in the environment. Accepts a Python script as a string and runs it safely. Returns execution result or error.")
        @log_tool_calls
        async def execute_script(script: str) -> Dict[str, Any]:
            """
            Execute a Python script in the environment.
            
            This tool takes a Python script as input and executes it within the
            environment. It is designed to run scripts that interact
            for automating tasks.
            
            Args:
                script: The Python script to execute as a string.
            
            Returns:
                Dict containing:
                - success: Boolean indicating if execution succeeded
                - output: Any output or result from the script execution
                - error: Error message if execution failed
            
            Examples:
                Input: "print('Hello from AI')"
                Output: {"success": true, "result": null, "error": null}
            """
            try:
                result = run_script(script, logger)
                return {"success": True, "result": result["result"], "error": None}
            except Exception as e:
                logger.error(f"Error executing script: {e}")
                return {"success": False, "result": None, "error": str(e)}

        # Enhanced Crypto Tools with comprehensive metadata and schemas
        @self.app.tool(
            name="encrypt",
            description="Encode text to base64 format. Accepts either a plain string or an object with 'text' property. Returns success status, encoded result, and length information."
        )
        @log_tool_calls
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
                logger.debug(f"Encrypt tool called with text length: {len(text)}")
                return await encrypt_tool(text)
            except Exception as e:
                logger.error(f"Error in encrypt tool: {e}")
                return {"success": False, "error": str(e), "encrypted_text": None}
        
        @self.app.tool(
            name="decrypt", 
            description="Decode base64 string back to original text. Accepts either a plain base64 string or an object with 'encoded_text' property. Returns success status, decoded result, and length information."
        )
        @log_tool_calls
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
                logger.debug(f"Decrypt tool called with encoded text length: {len(encoded_text)}")
                return await decrypt_tool(encoded_text)
            except Exception as e:
                logger.error(f"Error in decrypt tool: {e}")
                return {"success": False, "error": str(e), "decrypted_text": None}
        
        # Custom handler to process calculator parameters
        def _process_calculator_params(raw_params):
            """Process calculator parameters from various formats."""
            logger.debug(f"Processing calculator params: {raw_params} (type: {type(raw_params)})")
            
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
        @log_tool_calls
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
                logger.debug(f"Add tool called: {a} + {b}")
                return await add_tool(a, b)
            except Exception as e:
                logger.error(f"Error in add tool: {e}")
                return {"success": False, "error": str(e), "result": None}
        
        @self.app.tool(
            name="subtract",
            description="Subtract second number from first number. Accepts object {a: minuend, b: subtrahend}. Returns operation details and difference result."
        )
        @log_tool_calls
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
                logger.debug(f"Subtract tool called: {a} - {b}")
                return await subtract_tool(a, b)
            except Exception as e:
                logger.error(f"Error in subtract tool: {e}")
                return {"success": False, "error": str(e), "result": None}
        
        @self.app.tool(
            name="multiply",
            description="Multiply two numbers together. Accepts object {a: number, b: number}. Returns operation details and product result."
        )
        @log_tool_calls
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
                logger.debug(f"Multiply tool called: {a} * {b}")
                return await multiply_tool(a, b)
            except Exception as e:
                logger.error(f"Error in multiply tool: {e}")
                return {"success": False, "error": str(e), "result": None}
        
        @self.app.tool(
            name="divide",
            description="Divide first number by second number. Accepts object {a: dividend, b: divisor}. Includes division by zero protection. Returns operation details and quotient result."
        )
        @log_tool_calls
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
                logger.debug(f"Divide tool called: {a} / {b}")
                return await divide_tool(a, b)
            except Exception as e:
                logger.error(f"Error in divide tool: {e}")
                return {"success": False, "error": str(e), "result": None}
        
        @self.app.tool(
            name="modulo",
            description="Calculate remainder of first number divided by second number. Accepts object {a: dividend, b: divisor}. Includes modulo by zero protection. Returns operation details and remainder result."
        )
        @log_tool_calls
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
                logger.debug(f"Modulo tool called: {a} % {b}")
                return await modulo_tool(a, b)
            except Exception as e:
                logger.error(f"Error in modulo tool: {e}")
                return {"success": False, "error": str(e), "result": None}
        
        # Define Pydantic model for listTools parameters
        class ListToolsParams(BaseModel):
            detailed: bool = Field(
                False,
                description="Whether to include full schema details and examples in the response",
                examples=[True, False]
            )
            
            class Config:
                json_schema_extra = {
                    "title": "List Tools Parameters",
                    "description": "Parameters for listing available tools with their schemas",
                    "examples": [
                        {"detailed": False},
                        {"detailed": True}
                    ]
                }
        
        @self.app.tool(
            name="listTools",
            description="Get a list of all available tools with their input/output schemas and descriptions"
        )
        @log_tool_calls
        async def list_tools_tool(params: Optional[ListToolsParams] = None) -> Dict[str, Any]:
            """
            List all available tools with their schemas and descriptions.
            
            This tool returns detailed information about all tools registered with
            the MCP server, including their input parameters, output schemas,
            and descriptions. Useful for tool discovery and documentation.
            
            Args:
                params: Optional parameters containing:
                       - detailed: Whether to include full schema details in the response
            
            Returns:
                Dict containing:
                - success: Boolean indicating if operation succeeded
                - tools: List of tool information with schemas and descriptions
                - count: Total number of available tools
                - categories: Categories of available tools
                - error: Error message if operation failed
            
            Examples:
                Input: {"detailed": false}
                Output: {"success": true, "tools": [{name: "encrypt", ...}], ...}
            """
            try:
                detailed = params.detailed if params else False
                logger.debug(f"List tools tool called with detailed={detailed}")
                # Pass the FastMCP app instance to dynamically get registered tools
                return await list_tools(detailed=detailed, app=self.app)
            except Exception as e:
                logger.error(f"Error in listTools tool: {e}")
                return {
                    "success": False,
                    "tools": [],
                    "count": 0,
                    "categories": [],
                    "error": str(e)
                }
                
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
        @log_tool_calls
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
        @log_tool_calls
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
        @log_tool_calls
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
                    "count": 8,
                    "categories": ["crypto", "calculator", "discovery"]
                }
            """
            logger.info("Tools list resource requested")
            
            # Use the updated get_tools_list_resource function that supports dynamic retrieval
            try:
                # Pass the FastMCP app instance directly to get_tools_list_resource
                return await get_tools_list_resource(app=self.app)
            except Exception as e:
                logger.error(f"Error retrieving tools list: {str(e)}")
                # Fall back to completely static resource
                return await get_tools_list_resource()
        
        logger.info("MCP resources setup completed")
    
    def _add_test_routes(self) -> None:
        """Add custom HTTP routes for testing (separate from MCP protocol)."""
        logger.info("Adding test routes for browser access")
        
        from starlette.responses import JSONResponse, HTMLResponse
        
        # Get the underlying HTTP app and add custom routes
        @self.app.custom_route("/", methods=["GET"])
        async def root_endpoint(request):
            """Root endpoint for testing."""
            html_content = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>MCP Server</title>
                <style>
                    * { margin: 0; padding: 0; box-sizing: border-box; }
                    body {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        padding: 20px;
                    }
                    .container {
                        background: white;
                        border-radius: 16px;
                        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                        max-width: 600px;
                        width: 100%;
                        padding: 48px;
                        text-align: center;
                    }
                    .status {
                        display: inline-block;
                        padding: 8px 16px;
                        background: #10b981;
                        color: white;
                        border-radius: 20px;
                        font-size: 14px;
                        font-weight: 600;
                        margin-bottom: 24px;
                    }
                    h1 { font-size: 32px; color: #1f2937; margin-bottom: 16px; }
                    .description { color: #6b7280; font-size: 16px; line-height: 1.6; margin-bottom: 32px; }
                    .endpoint {
                        background: #f3f4f6;
                        border: 2px solid #e5e7eb;
                        border-radius: 8px;
                        padding: 16px;
                        margin-bottom: 24px;
                    }
                    .endpoint-label {
                        font-size: 12px;
                        color: #6b7280;
                        text-transform: uppercase;
                        font-weight: 600;
                        margin-bottom: 8px;
                    }
                    .endpoint-url {
                        font-family: 'Monaco', 'Courier New', monospace;
                        font-size: 18px;
                        color: #667eea;
                        font-weight: 600;
                    }
                    .link { color: #667eea; text-decoration: none; font-weight: 600; }
                    .link:hover { text-decoration: underline; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="status">✓ Server Running</div>
                    <h1>🚀 MCP Server</h1>
                    <p class="description">
                        Model Context Protocol server is up and running. 
                        Connect your MCP client to the endpoint below.
                    </p>
                    <div class="endpoint">
                        <div class="endpoint-label">Host: MCP Endpoint</div>
                        <div class="endpoint-url">http://localhost:6789/mcp</div>
                    </div>
                    <div class="endpoint">
                        <div class="endpoint-label">Docker: MCP Endpoint</div>
                        <div class="endpoint-url">http://host.docker.internal:6789/mcp</div>
                    </div>
                    <div>
                        <a href="/test/tools" class="link">View Tools</a> | 
                        <a href="/test/resources" class="link">View Resources</a> | 
                        <a href="/test/health" class="link">Health Check</a>
                    </div>
                </div>
            </body>
            </html>
            """
            return HTMLResponse(content=html_content)
        
        @self.app.custom_route("/test/health", methods=["GET"])
        async def health_endpoint(request):
            """Health check endpoint."""
            return JSONResponse({"status": "healthy", "server": "MCP Crypto Server (FastMCP)"})
        
        @self.app.custom_route("/test/tools", methods=["GET"])
        async def tools_list_endpoint(request):
            """List all registered MCP tools with enhanced metadata."""
            try:
                # Get tools from FastMCP - it returns a dict, not a list
                tools_dict = self.app.get_tools()
                if asyncio.iscoroutine(tools_dict):
                    tools_dict = await tools_dict
                
                # Convert tools dict to list format
                enhanced_tools = []
                if isinstance(tools_dict, dict):
                    for tool_name, tool in tools_dict.items():
                        tool_info = {
                            "name": tool_name,
                            "description": getattr(tool, 'description', ''),
                            "input_schema": getattr(tool, 'input_schema', None)
                        }
                        
                        # Add Pydantic schema information if available
                        if tool_name == "encrypt":
                            tool_info["pydantic_schema"] = EncryptParams.model_json_schema()
                            tool_info["examples"] = [{"text": "Hello World"}]
                        elif tool_name == "decrypt":
                            tool_info["pydantic_schema"] = DecryptParams.model_json_schema()
                            tool_info["examples"] = [{"encoded_text": "SGVsbG8gV29ybGQ="}]
                        elif tool_name in ["add", "subtract", "multiply", "divide", "modulo"]:
                            tool_info["pydantic_schema"] = CalculatorParams.model_json_schema()
                            tool_info["examples"] = [{"a": 10, "b": 5}]
                        
                        enhanced_tools.append(tool_info)
                
                response_data = {
                    "tools": enhanced_tools,
                    "count": len(enhanced_tools),
                    "metadata": {
                        "crypto_tools": ["encrypt", "decrypt"],
                        "calculator_tools": ["add", "subtract", "multiply", "divide", "modulo"]
                    }
                }
                return JSONResponse(response_data)
            except Exception as e:
                logger.error(f"Error getting tools: {e}")
                return JSONResponse({"error": str(e), "tools": [], "count": 0}, status_code=500)
        
        @self.app.custom_route("/test/resources", methods=["GET"])
        async def resources_list_endpoint(request):
            """List all registered MCP resources."""
            try:
                # Get resources from FastMCP - it returns a dict, not a list
                resources_dict = self.app.get_resources()
                if asyncio.iscoroutine(resources_dict):
                    resources_dict = await resources_dict
                
                # Convert resources dict to list format
                resources_list = []
                if isinstance(resources_dict, dict):
                    for resource_name, resource in resources_dict.items():
                        # Convert uri to string if it's an AnyUrl object
                        uri_value = getattr(resource, 'uri', None)
                        if uri_value is not None:
                            # Convert AnyUrl or similar objects to string
                            uri_value = str(uri_value)
                        
                        resource_info = {
                            "name": resource_name,
                            "description": getattr(resource, 'description', ''),
                            "uri": uri_value,
                            "mime_type": getattr(resource, 'mime_type', None)
                        }
                        resources_list.append(resource_info)
                
                response_data = {
                    "resources": resources_list,
                    "count": len(resources_list)
                }
                return JSONResponse(response_data)
            except Exception as e:
                logger.error(f"Error getting resources: {e}")
                return JSONResponse({"error": str(e), "resources": [], "count": 0}, status_code=500)
        
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
                # Use FastMCP's built-in server - it's not async in newer versions
                self.app.run()
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
            
            # Final fallback: Log error and exit gracefully
            logger.error("All server startup modes failed. Please check your FastMCP installation.")
            raise Exception("Failed to start server in any mode")
    
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