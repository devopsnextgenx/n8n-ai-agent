"""CLI utilities for development and testing."""

import logging
import sys
from typing import Optional

import uvicorn
from fastapi import FastAPI

from .config import get_settings
from .main import create_mcp_server
from .utils.logging import setup_logging
from .api import router as mcp_router


def create_dev_app() -> FastAPI:
    """Create FastAPI app for development.
    
    Returns:
        FastAPI: Development FastAPI application
    """
    settings = get_settings()
    
    # Setup logging for development
    setup_logging(settings.log_level, debug=True)
    
    logger = logging.getLogger(__name__)
    logger.info("Creating development FastAPI app...")
    
    # Create FastAPI app
    app = FastAPI(
        title="N8N MCP Server (Development)",
        description="Development server for N8N MCP Server",
        version="0.1.0",
        debug=settings.debug,
    )
    
    # Create MCP server (this will register tools)
    mcp = create_mcp_server()
    
    # Include MCP API routes
    app.include_router(mcp_router)
    
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": "N8N MCP Server (Development Mode)",
            "version": "0.1.0",
            "tools_count": len(mcp._tools) if hasattr(mcp, '_tools') else 0,
            "mcp_endpoints": "/mcp/tools",
            "docs": "/docs"
        }
    
    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy"}
    
    @app.get("/tools")
    async def list_tools():
        """List available MCP tools."""
        if hasattr(mcp, '_tools'):
            return {
                "tools": [
                    {
                        "name": name,
                        "description": getattr(tool, '__doc__', 'No description'),
                    }
                    for name, tool in mcp._tools.items()
                ],
                "mcp_api": "/mcp/tools"
            }
        return {"tools": [], "mcp_api": "/mcp/tools"}
    
    logger.info("Development FastAPI app created successfully")
    return app


def dev_main() -> None:
    """Development server entry point."""
    settings = get_settings()
    
    logger = logging.getLogger(__name__)
    logger.info("Starting development server...")
    
    try:
        uvicorn.run(
            "n8n_mcp_server.cli:create_dev_app",
            factory=True,
            host=settings.host,
            port=settings.port + 1000,  # Use different port for dev
            reload=settings.auto_reload,
            log_level=settings.log_level.lower(),
        )
    except KeyboardInterrupt:
        logger.info("Development server stopped by user")
    except Exception as e:
        logger.error(f"Development server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    dev_main()