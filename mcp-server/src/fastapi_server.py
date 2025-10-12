"""
Simple FastAPI-based MCP server implementation.

This provides a working HTTP server with the same functionality as the FastMCP version.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

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
from utils import get_logger

from config import get_config
from src.mcp_store.tools.crypto import decrypt_tool, encrypt_tool

logger = get_logger(__name__)


# Pydantic models for API requests
class EncryptRequest(BaseModel):
    text: str


class DecryptRequest(BaseModel):
    encoded_text: str


class CalculatorRequest(BaseModel):
    a: float
    b: float


def create_fastapi_server() -> FastAPI:
    """Create a FastAPI server with MCP functionality."""
    app = FastAPI(
        title="MCP Crypto Server",
        description="HTTP server providing MCP-style crypto tools and resources",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    @app.get("/")
    async def root():
        """Root endpoint with server information."""
        return {
            "message": "MCP Crypto Server",
            "status": "running",
            "version": "0.1.0",
            "tools": ["encrypt", "decrypt", "add", "subtract", "multiply", "divide", "modulo"],
            "resources": ["version", "status", "tools_list"],
            "endpoints": {
                "tools": {
                    "encrypt": "POST /tools/encrypt",
                    "decrypt": "POST /tools/decrypt",
                    "add": "POST /tools/add",
                    "subtract": "POST /tools/subtract",
                    "multiply": "POST /tools/multiply",
                    "divide": "POST /tools/divide",
                    "modulo": "POST /tools/modulo"
                },
                "resources": {
                    "version": "GET /resources/version",
                    "status": "GET /resources/status",
                    "tools_list": "GET /resources/tools"
                }
            }
        }
    
    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy", "server": "MCP Crypto Server"}
    
    # Tool endpoints
    @app.post("/tools/encrypt")
    async def encrypt_endpoint(request: EncryptRequest) -> Dict[str, Any]:
        """Encrypt text to base64."""
        try:
            result = await encrypt_tool(request.text)
            return result
        except Exception as e:
            logger.error(f"Encrypt endpoint error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/tools/decrypt")
    async def decrypt_endpoint(request: DecryptRequest) -> Dict[str, Any]:
        """Decrypt base64 text."""
        try:
            result = await decrypt_tool(request.encoded_text)
            return result
        except Exception as e:
            logger.error(f"Decrypt endpoint error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/tools/add")
    async def add_endpoint(request: CalculatorRequest) -> Dict[str, Any]:
        """Add two numbers."""
        try:
            result = await add_tool(request.a, request.b)
            return result
        except Exception as e:
            logger.error(f"Add endpoint error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/tools/subtract")
    async def subtract_endpoint(request: CalculatorRequest) -> Dict[str, Any]:
        """Subtract second number from first."""
        try:
            result = await subtract_tool(request.a, request.b)
            return result
        except Exception as e:
            logger.error(f"Subtract endpoint error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/tools/multiply")
    async def multiply_endpoint(request: CalculatorRequest) -> Dict[str, Any]:
        """Multiply two numbers."""
        try:
            result = await multiply_tool(request.a, request.b)
            return result
        except Exception as e:
            logger.error(f"Multiply endpoint error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/tools/divide")
    async def divide_endpoint(request: CalculatorRequest) -> Dict[str, Any]:
        """Divide first number by second."""
        try:
            result = await divide_tool(request.a, request.b)
            return result
        except Exception as e:
            logger.error(f"Divide endpoint error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/tools/modulo")
    async def modulo_endpoint(request: CalculatorRequest) -> Dict[str, Any]:
        """Calculate remainder of first number divided by second."""
        try:
            result = await modulo_tool(request.a, request.b)
            return result
        except Exception as e:
            logger.error(f"Modulo endpoint error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Resource endpoints
    @app.get("/resources/version")
    async def version_endpoint():
        """Get server version information."""
        try:
            import json
            version_data = await get_version_resource()
            return json.loads(version_data)
        except Exception as e:
            logger.error(f"Version endpoint error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/resources/status")
    async def status_endpoint():
        """Get server status information."""
        try:
            import json
            status_data = await get_status_resource()
            return json.loads(status_data)
        except Exception as e:
            logger.error(f"Status endpoint error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/resources/tools")
    async def tools_list_endpoint():
        """Get available tools information."""
        try:
            import json
            tools_data = await get_tools_list_resource()
            return json.loads(tools_data)
        except Exception as e:
            logger.error(f"Tools list endpoint error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return app


async def run_server():
    """Run the FastAPI server."""
    try:
        config = get_config()
        
        # Override with environment variables if set
        if os.getenv("MCP_HOST"):
            config.server.host = os.getenv("MCP_HOST")

        if os.getenv("MCP_PORT"):
            config.server.port = int(os.getenv("MCP_PORT"))
            
        logger.info("Creating FastAPI-based MCP server...")
        app = create_fastapi_server()
        
        logger.info(f"Starting server on {config.server.host}:{config.server.port}")
        
        import uvicorn
        
        uvicorn_config = uvicorn.Config(
            app=app,
            host=config.server.host,
            port=config.server.port,
            log_level="info",
            access_log=True
        )
        
        server = uvicorn.Server(uvicorn_config)
        await server.serve()
        
    except Exception as e:
        logger.error(f"Failed to start FastAPI server: {e}")
        raise


def main():
    """Main entry point."""
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    main()