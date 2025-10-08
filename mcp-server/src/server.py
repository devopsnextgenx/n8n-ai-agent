"""Main MCP server implementation using FastMCP.

This module sets up the FastMCP server with HTTP transport and registers
all tools and resources using proper MCP protocol.
"""

import asyncio
import sys
from pathlib import Path
from typing import Any, Dict
from fastmcp import FastMCP
from pydantic import BaseModel

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


# Pydantic models for MCP tool parameters
class EncryptParams(BaseModel):
    text: str


class DecryptParams(BaseModel):
    encoded_text: str


class CalculatorParams(BaseModel):
    a: float
    b: float


class MCPCryptoServer:
    """MCP Crypto Server using FastMCP with proper MCP protocol support."""
    
    def __init__(self):
        """Initialize the MCP server."""
        self.config = get_config()
        # Create FastMCP app with proper MCP protocol support
        self.app = FastMCP(
            name="MCP Crypto Server",
            version="0.1.0",
            # Enable debug mode for development
            debug=True
        )
        self._setup_mcp_tools()
        self._setup_mcp_resources()
        logger.info("MCP Crypto Server initialized with FastMCP")
    
    def _setup_mcp_tools(self) -> None:
        """Set up MCP tools using FastMCP decorators."""
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

        @self.app.tool(name="encrypt", description="Encrypt string to base64")
        async def encrypt(params) -> Dict[str, Any]:
            """Encrypt tool handler."""
            try:
                text = _process_encrypt_params(params)
                logger.info(f"Encrypt tool called with text length: {len(text)}")
                return await encrypt_tool(text)
            except Exception as e:
                logger.error(f"Error in encrypt tool: {e}")
                return {"success": False, "error": str(e), "encrypted_text": None}
        
        @self.app.tool(name="decrypt", description="Decrypt base64 string")
        async def decrypt(params) -> Dict[str, Any]:
            """Decrypt tool handler."""
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
        
        @self.app.tool(name="add", description="Add two numbers")
        async def add(params):
            """Add tool handler."""
            try:
                a, b = _process_calculator_params(params)
                logger.info(f"Add tool called: {a} + {b}")
                return await add_tool(a, b)
            except Exception as e:
                logger.error(f"Error in add tool: {e}")
                return {"success": False, "error": str(e), "result": None}
        
        @self.app.tool(name="subtract", description="Subtract second number from first")
        async def subtract(params):
            """Subtract tool handler."""
            try:
                a, b = _process_calculator_params(params)
                logger.info(f"Subtract tool called: {a} - {b}")
                return await subtract_tool(a, b)
            except Exception as e:
                logger.error(f"Error in subtract tool: {e}")
                return {"success": False, "error": str(e), "result": None}
        
        @self.app.tool(name="multiply", description="Multiply two numbers")
        async def multiply(params):
            """Multiply tool handler."""
            try:
                a, b = _process_calculator_params(params)
                logger.info(f"Multiply tool called: {a} * {b}")
                return await multiply_tool(a, b)
            except Exception as e:
                logger.error(f"Error in multiply tool: {e}")
                return {"success": False, "error": str(e), "result": None}
        
        @self.app.tool(name="divide", description="Divide first number by second")
        async def divide(params):
            """Divide tool handler."""
            try:
                a, b = _process_calculator_params(params)
                logger.info(f"Divide tool called: {a} / {b}")
                return await divide_tool(a, b)
            except Exception as e:
                logger.error(f"Error in divide tool: {e}")
                return {"success": False, "error": str(e), "result": None}
        
        @self.app.tool(name="modulo", description="Calculate remainder of first number divided by second")
        async def modulo(params):
            """Modulo tool handler."""
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
        """Set up MCP resources using FastMCP decorators."""
        logger.info("Setting up MCP resources")
        
        @self.app.resource(
            "resource://mcp/version",
            name="version",
            description="Current MCP server version",
            mime_type="application/json"
        )
        async def version_resource() -> str:
            """Version resource handler."""
            logger.info("Version resource requested")
            return await get_version_resource()
        
        @self.app.resource(
            "resource://mcp/status",
            name="status",
            description="Current MCP server status",
            mime_type="application/json"
        )
        async def status_resource() -> str:
            """Status resource handler."""
            logger.info("Status resource requested")
            return await get_status_resource()
        
        @self.app.resource(
            "resource://mcp/tools/list",
            name="tools_list",
            description="List MCP server tools",
            mime_type="application/json"
        )
        async def tools_list_resource() -> str:
            """Tools list resource handler."""
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
            """List all registered MCP tools."""
            try:
                tools = await self.app.get_tools() if asyncio.iscoroutinefunction(self.app.get_tools) else self.app.get_tools()
                return {
                    "tools": [
                        {
                            "name": getattr(tool, 'name', str(tool)),
                            "description": getattr(tool, 'description', ''),
                            "schema": getattr(tool, 'input_schema', None)
                        } for tool in (tools or [])
                    ],
                    "count": len(tools) if tools else 0
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