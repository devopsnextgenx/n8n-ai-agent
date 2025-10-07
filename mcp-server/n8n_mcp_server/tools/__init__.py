"""Tools package initialization."""

from fastmcp import FastMCP

from .base64_tool import register_base64_tool


def register_all_tools(mcp: FastMCP) -> None:
    """Register all available tools with the MCP server.
    
    Args:
        mcp: FastMCP server instance
    """
    # Register individual tools
    register_base64_tool(mcp)
    
    # Add more tools here as they are created
    # register_other_tool(mcp)


__all__ = ["register_all_tools"]