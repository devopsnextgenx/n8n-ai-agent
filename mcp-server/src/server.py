"""
Main entry point for MCP Crypto Server.

This module initializes the configuration, sets up logging, and starts the MCP server
with the specified transport mode (http_streamable, http_app, or stdio).
"""

import argparse
import asyncio
import json
import os
import sys
from functools import wraps
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, Optional

import mcp
from fastmcp import FastMCP
from pydantic import BaseModel, Field

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv

    # Look for .env file in the project root (parent of src/)
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"Loaded environment variables from: {env_path}")
    else:
        # Fallback: look for .env in current working directory
        if Path(".env").exists():
            load_dotenv()
            print("Loaded environment variables from .env in current directory")
except ImportError:
    print("Warning: python-dotenv not installed. .env file will not be loaded automatically.")

# Add src to path for absolute imports
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from mcp_store.resources.status import get_status_resource
from mcp_store.resources.tools_list import get_tools_list_resource
from mcp_store.resources.version import get_version_resource
from mcp_store.tools.calculator import (
    add_tool,
    divide_tool,
    modulo_tool,
    multiply_tool,
    subtract_tool,
)
from mcp_store.tools.ScriptExecutor import run_script
from utils import get_logger, setup_logging

from config import get_config
from src.log_middleware import log_tool_calls
from src.mcp_store.tools.crypto import decrypt_tool, encrypt_tool
from src.mcp_store.tools.tools_list import list_tools


# Helper functions for response formatting
def format_response(data: Any, success: bool = True, message: str = "") -> Dict[str, Any]:
    """Format a successful response.
    
    Args:
        data: Response data
        success: Success status
        message: Optional message
        
    Returns:
        dict: Formatted response
    """
    return {
        "success": success,
        "data": data,
        "message": message
    }


def format_error_response(error: str, error_code: str = "ERROR") -> Dict[str, Any]:
    """Format an error response.
    
    Args:
        error: Error message
        error_code: Error code
        
    Returns:
        dict: Formatted error response
    """
    return {
        "success": False,
        "error": error,
        "error_code": error_code
    }


def validate_config(config) -> bool:
    """Validate configuration.
    
    Args:
        config: Configuration object to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        # Basic validation
        if not hasattr(config, 'server') or not hasattr(config, 'logging'):
            return False
        
        # Validate server config
        if not hasattr(config.server, 'host') or not hasattr(config.server, 'port'):
            return False
            
        # Validate port range
        if not (1 <= config.server.port <= 65535):
            return False
            
        return True
    except Exception:
        return False


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
    
    text: str = Field(
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
                {"text": "SGVsbG8gV29ybGQ="},
                {"text": "VGhpcyBpcyBhIHNlY3JldCBtZXNzYWdl"},
                {"text": "YW1pdGtzaGlyc2FnYXI="}
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


class ListToolsParams(BaseModel):
    """Parameters for listTools."""
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


def create_server(server_name="MCP Crypto Server"):
    """Create and configure the MCP server.
    
    Args:
        server_name (str): Name of the server
        
    Returns:
        FastMCP: Configured server instance
    """
    # Get configuration
    config = get_config()
    
    # Initialize the server
    server = FastMCP(
        name=server_name,
        version="0.1.0"
    )
    logger = get_logger(__name__)
    
    logger.info(f"MCP Server initialized: {server_name}")

    # Setup tools and resources
    _setup_mcp_tools(server, logger)
    _setup_mcp_resources(server, logger)
    _add_test_routes(server, logger)
    
    logger.info("MCP server configuration completed")
    return server


def _setup_mcp_tools(server: FastMCP, logger) -> None:
    """Set up MCP tools using FastMCP decorators with enhanced metadata."""
    logger.info("Setting up MCP tools")
    
    # Parameter processing functions
    def _process_encrypt_params(raw_params):
        """Process encrypt parameters from various formats."""
        logger.info(f"Processing encrypt params: {raw_params} (type: {type(raw_params)})")
        
        if isinstance(raw_params, str):
            return raw_params
        elif isinstance(raw_params, dict):
            if 'text' in raw_params:
                return raw_params['text']
            else:
                raise ValueError("Object format requires 'text' property")
        elif hasattr(raw_params, 'text'):
            return raw_params.text
        else:
            raise ValueError(f"Parameters must be a string or an object with 'text' property. Got: {type(raw_params)}")
    
    def _process_decrypt_params(raw_params):
        """Process decrypt parameters from various formats."""
        logger.debug(f"Processing decrypt params: {raw_params} (type: {type(raw_params)})")
        
        if isinstance(raw_params, str):
            return raw_params
        elif isinstance(raw_params, dict):
            if 'text' in raw_params:
                return raw_params['text']
            else:
                raise ValueError("Object format requires 'text' property")
        elif hasattr(raw_params, 'text'):
            return raw_params.text
        else:
            raise ValueError(f"Parameters must be a string or an object with 'text' property. Got: {type(raw_params)}")

    def _process_calculator_params(raw_params):
        """Process calculator parameters from various formats."""
        logger.debug(f"Processing calculator params: {raw_params} (type: {type(raw_params)})")
        
        if isinstance(raw_params, list):
            if len(raw_params) != 2:
                raise ValueError("Calculator requires exactly 2 parameters")
            return raw_params[0], raw_params[1]
        elif isinstance(raw_params, dict):
            if 'a' not in raw_params or 'b' not in raw_params:
                raise ValueError("Object format requires 'a' and 'b' properties")
            return raw_params['a'], raw_params['b']
        elif hasattr(raw_params, 'a') and hasattr(raw_params, 'b'):
            return raw_params.a, raw_params.b
        else:
            raise ValueError(f"Parameters must be an array of 2 numbers or an object with 'a' and 'b' properties. Got: {type(raw_params)}")

    # Script execution tool
    # @server.tool(name="executeScript", description="Execute a script in the environment. Accepts a Python script as a string and runs it safely. Returns execution result or error.")
    @log_tool_calls
    async def execute_script(script: str) -> Dict[str, Any]:
        """Execute a Python script in the environment."""
        try:
            result = run_script(script, logger)
            return {"success": True, "result": result["result"], "error": None}
        except Exception as e:
            logger.error(f"Error executing script: {e}")
            return {"success": False, "result": None, "error": str(e)}

    # Crypto tools
    @server.tool(
        name="encrypt",
        description="Encode text to base64 format. Accepts either a plain string or an object with 'text' property. Returns success status, encoded result, and length information."
    )
    @log_tool_calls
    async def encrypt(params: EncryptParams) -> Dict[str, Any]:
        """Encrypt (encode) a plain text string to base64 format."""
        try:
            text = _process_encrypt_params(params)
            logger.debug(f"Encrypt tool called with text length: {len(text)}")
            return await encrypt_tool(text)
        except Exception as e:
            logger.error(f"Error in encrypt tool: {e}")
            return {"success": False, "error": str(e), "encrypted_text": None}
    
    @server.tool(
        name="decrypt", 
        description="Decode base64 string back to original text. Accepts either a plain base64 string or an object with 'encoded_text' property. Returns success status, decoded result, and length information."
    )
    @log_tool_calls
    async def decrypt(params: DecryptParams) -> Dict[str, Any]:
        """Decrypt (decode) a base64 encoded string back to its original text."""
        try:
            encoded_text = _process_decrypt_params(params)
            logger.debug(f"Decrypt tool called with encoded text length: {len(encoded_text)}")
            return await decrypt_tool(encoded_text)
        except Exception as e:
            logger.error(f"Error in decrypt tool: {e}")
            return {"success": False, "error": str(e), "decrypted_text": None}
    
    # Calculator tools
    @server.tool(
        name="add",
        description="Add two numbers together. Accepts object {a: number, b: number}. Returns operation details and sum result."
    )
    @log_tool_calls
    async def add(params: CalculatorParams):
        """Add two numbers and return the sum."""
        try:
            a, b = _process_calculator_params(params)
            logger.debug(f"Add tool called: {a} + {b}")
            return await add_tool(a, b)
        except Exception as e:
            logger.error(f"Error in add tool: {e}")
            return {"success": False, "error": str(e), "result": None}
    
    @server.tool(
        name="subtract",
        description="Subtract second number from first number. Accepts object {a: minuend, b: subtrahend}. Returns operation details and difference result."
    )
    @log_tool_calls
    async def subtract(params: CalculatorParams):
        """Subtract the second number from the first number."""
        try:
            a, b = _process_calculator_params(params)
            logger.debug(f"Subtract tool called: {a} - {b}")
            return await subtract_tool(a, b)
        except Exception as e:
            logger.error(f"Error in subtract tool: {e}")
            return {"success": False, "error": str(e), "result": None}
    
    @server.tool(
        name="multiply",
        description="Multiply two numbers together. Accepts object {a: number, b: number}. Returns operation details and product result."
    )
    @log_tool_calls
    async def multiply(params: CalculatorParams):
        """Multiply two numbers and return the product."""
        try:
            a, b = _process_calculator_params(params)
            logger.debug(f"Multiply tool called: {a} * {b}")
            return await multiply_tool(a, b)
        except Exception as e:
            logger.error(f"Error in multiply tool: {e}")
            return {"success": False, "error": str(e), "result": None}
    
    @server.tool(
        name="divide",
        description="Divide first number by second number. Accepts object {a: dividend, b: divisor}. Includes division by zero protection. Returns operation details and quotient result."
    )
    @log_tool_calls
    async def divide(params: CalculatorParams):
        """Divide the first number by the second number."""
        try:
            a, b = _process_calculator_params(params)
            logger.debug(f"Divide tool called: {a} / {b}")
            return await divide_tool(a, b)
        except Exception as e:
            logger.error(f"Error in divide tool: {e}")
            return {"success": False, "error": str(e), "result": None}
    
    @server.tool(
        name="modulo",
        description="Calculate remainder of first number divided by second number. Accepts object {a: dividend, b: divisor}. Includes modulo by zero protection. Returns operation details and remainder result."
    )
    @log_tool_calls
    async def modulo(params: CalculatorParams):
        """Calculate the modulo (remainder) of dividing the first number by the second."""
        try:
            a, b = _process_calculator_params(params)
            logger.debug(f"Modulo tool called: {a} % {b}")
            return await modulo_tool(a, b)
        except Exception as e:
            logger.error(f"Error in modulo tool: {e}")
            return {"success": False, "error": str(e), "result": None}
    
    # List tools tool
    @server.tool(
        name="listTools",
        description="Get a list of all available tools with their input/output schemas and descriptions"
    )
    @log_tool_calls
    async def list_tools_tool(params: Optional[ListToolsParams] = None) -> Dict[str, Any]:
        """List all available tools with their schemas and descriptions."""
        try:
            logger.info(f"List tools tool called with params: {params}")
            detailed = params if params else True
            detailed = True
            return await list_tools(detailed=detailed, app=server)
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


def _setup_mcp_resources(server: FastMCP, logger) -> None:
    """Set up MCP resources using FastMCP decorators with enhanced metadata."""
    logger.info("Setting up MCP resources")
    
    @server.resource(
        "resource://mcp/version",
        name="version",
        description="Current MCP server version information including build details and compatibility",
        mime_type="application/json"
    )
    @log_tool_calls
    async def version_resource() -> str:
        """Get current MCP server version and build information."""
        logger.info("Version resource requested")
        return await get_version_resource()
    
    @server.resource(
        "resource://mcp/status",
        name="status",
        description="Current MCP server operational status and health information",
        mime_type="application/json"
    )
    @log_tool_calls
    async def status_resource() -> str:
        """Get current MCP server operational status and health metrics."""
        logger.info("Status resource requested")
        return await get_status_resource()
    
    @server.resource(
        "resource://mcp/tools/list",
        name="tools_list",
        description="Comprehensive list of all available MCP tools with detailed metadata",
        mime_type="application/json"
    )
    @log_tool_calls
    async def tools_list_resource() -> str:
        """Get comprehensive list of all available MCP tools with their metadata."""
        logger.info("Tools list resource requested")
        
        try:
            return await get_tools_list_resource(app=server)
        except Exception as e:
            logger.error(f"Error retrieving tools list: {str(e)}")
            return await get_tools_list_resource()
    
    logger.info("MCP resources setup completed")


def _add_test_routes(server: FastMCP, logger) -> None:
    """Add custom HTTP routes for testing (separate from MCP protocol)."""
    logger.info("Adding test routes for browser access")
    
    try:
        from starlette.responses import HTMLResponse, JSONResponse
        
        @server.custom_route("/", methods=["GET"])
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
        
        @server.custom_route("/test/health", methods=["GET"])
        async def health_endpoint(request):
            """Health check endpoint."""
            return JSONResponse({"status": "healthy", "server": "MCP Crypto Server (FastMCP)"})
        
        @server.custom_route("/test/tools", methods=["GET"])
        async def tools_list_endpoint(request):
            """List all registered MCP tools with enhanced metadata."""
            try:
                tools_dict = server.get_tools()
                if asyncio.iscoroutine(tools_dict):
                    tools_dict = await tools_dict
                
                enhanced_tools = []
                if isinstance(tools_dict, dict):
                    for tool_name, tool in tools_dict.items():
                        tool_info = {
                            "name": tool_name,
                            "description": getattr(tool, 'description', ''),
                            "input_schema": getattr(tool, 'input_schema', None)
                        }
                        
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
        
        @server.custom_route("/test/resources", methods=["GET"])
        async def resources_list_endpoint(request):
            """List all registered MCP resources."""
            try:
                resources_dict = server.get_resources()
                if asyncio.iscoroutine(resources_dict):
                    resources_dict = await resources_dict
                
                resources_list = []
                if isinstance(resources_dict, dict):
                    for resource_name, resource in resources_dict.items():
                        uri_value = getattr(resource, 'uri', None)
                        if uri_value is not None:
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
        
    except ImportError:
        logger.warning("Starlette not available, skipping test routes")


def parse_arguments():
    """Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description="MCP Crypto Server")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--mode", choices=["auto", "http", "streamable-http", "stdio", "sse"], 
                        help="Server transport mode (valid transports: stdio, http, sse, streamable-http)")
    parser.add_argument("--host", help="Host to bind the server to")
    parser.add_argument("--port", type=int, help="Port to bind the server to")
    parser.add_argument("--dev", action="store_true", help="Run in development mode with extra debug info")
    
    return parser.parse_args()


def main():
    """Main entry point for the application."""
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        # Load configuration
        config = get_config()
        
        # Get mode from args or default to auto
        mode = args.mode or 'auto'
            
        # Override configuration with command line arguments if provided
        if args.host:
            config.server.host = args.host
            
        if args.port:
            config.server.port = args.port
            
        # Setup logging
        logger = setup_logging(config.logging)
        
        # Validate configuration
        if not validate_config(config):
            logger.error("Invalid configuration. Please check your settings.")
            sys.exit(1)
            
        # Log startup information
        logger.info("=" * 60)
        logger.info("MCP Crypto Server Starting Up")
        logger.info("=" * 60)
        logger.info(f"Server will bind to: {config.server.host}:{config.server.port}")
        logger.info(f"Server mode: {mode}")
        logger.info(f"Log level: {config.logging.level}")
        logger.info(f"Log file: {config.logging.file}")
        
        # Create server
        server = create_server()
        
        # Start server with appropriate transport
        # Set server binding information in environment variables
        os.environ["MCP_HOST"] = config.server.host
        os.environ["MCP_PORT"] = str(config.server.port)
        
        # Apply the log level when running the server
        log_level = config.logging.level
        
        if mode == "stdio":
            logger.info("Starting server with stdio transport")
            server.run(transport="stdio", log_level=log_level)
        elif mode == "http":
            logger.info(f"Starting server with http transport on {config.server.host}:{config.server.port}")
            server.run(transport="http", host=config.server.host, port=config.server.port, log_level=log_level)
        elif mode == "streamable-http":
            logger.info(f"Starting server with streamable-http transport on {config.server.host}:{config.server.port}")
            server.run(transport="streamable-http", host=config.server.host, port=config.server.port, log_level=log_level)
        else:  # auto mode
            logger.info(f"Starting server in auto mode on {config.server.host}:{config.server.port}")
            try:
                server.run(transport="streamable-http", host=config.server.host, port=config.server.port, log_level=log_level)
            except Exception as e:
                logger.warning(f"Streamable HTTP server failed: {e}, falling back to http transport")
                server.run(transport="http", host=config.server.host, port=config.server.port, log_level=log_level)
                
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
        logger = get_logger()
        logger.info("Server shutdown requested by user")
    except FileNotFoundError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Failed to start server: {e}")
        logger = get_logger()
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)


def dev_main():
    """Development entry point with additional debug information."""
    print("MCP Crypto Server - Development Mode")
    print("=" * 50)
    
    # Print environment information
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Script location: {__file__}")
    print(f"Python path: {sys.path[:3]}...")  # Show first 3 entries
    
    # Show available modes
    print("Available server modes:")
    print("  --mode auto           : Try streamable-http first, fallback to http (default)")
    print("  --mode http           : Use standard http transport")
    print("  --mode streamable-http: Use streamable-http transport (for n8n compatibility)")
    print("  --mode stdio          : Use stdio transport for CLI or integration")
    print("  --mode sse            : Use Server-Sent Events transport")
    print("=" * 50)
    
    main()


if __name__ == "__main__":
    # Check if running in development mode
    if "--dev" in sys.argv:
        dev_main()
    else:
        main()