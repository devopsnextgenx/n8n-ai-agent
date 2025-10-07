"""Main MCP server entry point."""

import logging
from typing import Optional

from fastmcp import FastMCP

from .config import get_settings
from .tools import register_all_tools
from .utils.logging import setup_logging


def create_mcp_server() -> FastMCP:
    """Create and configure the MCP server.
    
    Returns:
        FastMCP: Configured MCP server instance
    """
    settings = get_settings()
    
    # Setup logging
    setup_logging(settings.log_level, settings.debug)
    
    logger = logging.getLogger(__name__)
    logger.info("Creating MCP server...")
    
    # Create MCP server instance
    mcp = FastMCP("N8N-AI-Agent-MCP")
    
    # Register all tools
    register_all_tools(mcp)
    
    logger.info("MCP server created successfully")
    return mcp


def main() -> None:
    """Main entry point for the MCP server."""
    settings = get_settings()
    mcp = create_mcp_server()
    
    logger = logging.getLogger(__name__)
    logger.info(
        f"Starting MCP server on {settings.host}:{settings.port}"
    )
    
    # Run the server
    mcp.run(
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()