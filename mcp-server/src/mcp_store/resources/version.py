"""Version resource for MCP Crypto Server.

This resource provides server version information.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict

# Add src to path for absolute imports
src_path = Path(__file__).parent.parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from utils import get_logger

logger = get_logger(__name__)

# Server version information
SERVER_VERSION = "0.1.0"
SERVER_NAME = "MCP Crypto Server"
MCP_VERSION = "1.0"


async def get_version_resource() -> str:
    """Get server version information.
    
    Returns:
        str: JSON string containing version information
    """
    try:
        logger.info("Retrieving server version information")
        
        version_info = {
            "server_name": SERVER_NAME,
            "server_version": SERVER_VERSION,
            "mcp_version": MCP_VERSION,
            "description": "MCP server with base64 encoding/decoding tools",
            "author": "DevOpsNextGenX",
            "capabilities": {
                "tools": ["encrypt", "decrypt"],
                "resources": ["version", "status", "tools_list"],
                "transport": "http"
            }
        }
        
        logger.info("Version information retrieved successfully")
        return json.dumps(version_info, indent=2)
        
    except Exception as e:
        error_msg = f"Error retrieving version information: {str(e)}"
        logger.error(error_msg)
        error_response = {
            "error": error_msg,
            "server_name": SERVER_NAME,
            "server_version": "unknown"
        }
        return json.dumps(error_response, indent=2)