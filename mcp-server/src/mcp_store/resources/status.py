"""Status resource for MCP Crypto Server.

This resource provides server status information.
"""

import json
import time
import psutil
import os
import sys
from pathlib import Path
from typing import Any, Dict
from datetime import datetime

# Add src to path for absolute imports
src_path = Path(__file__).parent.parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from utils import get_logger

logger = get_logger(__name__)

# Server start time
_server_start_time = time.time()


async def get_status_resource() -> str:
    """Get server status information.
    
    Returns:
        str: JSON string containing status information
    """
    try:
        logger.info("Retrieving server status information")
        
        current_time = time.time()
        uptime_seconds = current_time - _server_start_time
        
        # Get system information
        try:
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            cpu_percent = process.cpu_percent()
        except Exception:
            # Fallback if psutil is not available
            memory_info = None
            cpu_percent = None
        
        status_info = {
            "status": "running",
            "timestamp": datetime.fromtimestamp(current_time).isoformat(),
            "uptime_seconds": round(uptime_seconds, 2),
            "uptime_formatted": _format_uptime(uptime_seconds),
            "server_start_time": datetime.fromtimestamp(_server_start_time).isoformat(),
            "process_id": os.getpid(),
            "memory_usage": {
                "rss_bytes": memory_info.rss if memory_info else None,
                "vms_bytes": memory_info.vms if memory_info else None,
                "rss_mb": round(memory_info.rss / (1024 * 1024), 2) if memory_info else None
            } if memory_info else None,
            "cpu_percent": cpu_percent,
            "tools_available": ["encrypt", "decrypt"],
            "resources_available": ["version", "status", "tools_list"]
        }
        
        logger.info("Status information retrieved successfully")
        return json.dumps(status_info, indent=2)
        
    except Exception as e:
        error_msg = f"Error retrieving status information: {str(e)}"
        logger.error(error_msg)
        error_response = {
            "status": "error",
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }
        return json.dumps(error_response, indent=2)


def _format_uptime(uptime_seconds: float) -> str:
    """Format uptime in human-readable format.
    
    Args:
        uptime_seconds: Uptime in seconds
        
    Returns:
        str: Formatted uptime string
    """
    days = int(uptime_seconds // 86400)
    hours = int((uptime_seconds % 86400) // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    seconds = int(uptime_seconds % 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")
    
    return " ".join(parts)