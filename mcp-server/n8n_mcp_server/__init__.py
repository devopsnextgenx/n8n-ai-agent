"""N8N MCP Server Package.

A Model Context Protocol server for n8n AI agent with multiple tools and utilities.
"""

__version__ = "0.1.0"
__author__ = "DevOpsNextGenX"
__email__ = "your-email@example.com"

from .main import main, create_mcp_server

__all__ = ["main", "create_mcp_server", "__version__"]