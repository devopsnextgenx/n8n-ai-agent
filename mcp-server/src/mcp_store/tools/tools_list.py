"""Tools list tool for MCP Crypto Server.

This tool provides information about available tools with their schemas and descriptions.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add src to path for absolute imports
src_path = Path(__file__).parent.parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from src.utils import get_logger

logger = get_logger(__name__)


async def list_tools(detailed: bool = False, app=None) -> Dict[str, Any]:
    """List available tools with their schemas and descriptions.
    
    This function is used both by:
    1. The `listTools` MCP tool for direct client invocation
    2. The `tools_list` MCP resource for protocol-compliant tool discovery
    
    Args:
        detailed: Whether to include full schema and examples in the response
        app: Optional FastMCP app instance to get registered tools dynamically
             If not provided, falls back to static information
        
    Returns:
        Dict containing:
        - success: Boolean indicating if operation succeeded
        - tools: List of tool information with schemas and descriptions
        - count: Total number of available tools
        - categories: Categories of available tools
        - error: Error message if operation failed
    """
    try:
        logger.info(f"Listing tools (detailed: {detailed})")
        
        # If app is provided, get tools from it directly
        if app:
            # Get tools directly from FastMCP app
            logger.info("Getting tools from FastMCP app instance")
            import asyncio
            
            # Get tools from FastMCP (might be async)
            tools_list_from_app = await app.get_tools() if asyncio.iscoroutinefunction(app.get_tools) else app.get_tools()
            
            # Process tools based on detail level
            tools_list = []
            categories = set()
            
            for tool in tools_list_from_app:
                tool_info = {
                    "name": getattr(tool, 'name', str(tool)),
                    "description": getattr(tool, 'description', ''),
                }
                
                # Add detailed information if requested
                if detailed:
                    # Get schema information if available
                    input_schema = getattr(tool, 'input_schema', None)
                    if input_schema:
                        tool_info["parameters"] = input_schema.get('properties', {})
                        
                    # Get examples if available
                    examples = getattr(tool, 'examples', None)
                    if examples:
                        tool_info["examples"] = examples
                        
                    # Get return schema if available
                    return_schema = getattr(tool, 'output_schema', None)
                    if return_schema:
                        tool_info["returns"] = return_schema
                else:
                    # For non-detailed view, add simplified parameter and return info
                    input_schema = getattr(tool, 'input_schema', None)
                    if input_schema:
                        tool_info["parameters_summary"] = _summarize_params(input_schema.get('properties', {}))
                    
                    return_schema = getattr(tool, 'output_schema', None)
                    if return_schema:
                        tool_info["returns_summary"] = _summarize_returns(return_schema)
                
                # Try to determine category from tool name or properties
                tool_name = tool_info["name"]
                category = None
                if "encrypt" in tool_name.lower() or "decrypt" in tool_name.lower() or "crypto" in tool_name.lower():
                    category = "crypto"
                    categories.add("crypto")
                elif any(op in tool_name.lower() for op in ["add", "subtract", "multiply", "divide", "modulo"]):
                    category = "calculator"
                    categories.add("calculator")
                elif "script" in tool_name.lower() or "exec" in tool_name.lower():
                    category = "execution"
                    categories.add("execution")
                elif "list" in tool_name.lower():
                    category = "discovery"
                    categories.add("discovery")
                
                if category:
                    tool_info["category"] = category
                
                tools_list.append(tool_info)
        else:
            # Fallback to static resource if app not provided
            from src.mcp_store.resources.tools_list import get_tools_list_resource
            
            # Get the full tools list from the resource
            tools_json = await get_tools_list_resource()
            tools_data = json.loads(tools_json)
            
            # Process tools based on detail level
            if not detailed:
                # For non-detailed view, simplify the output
                simplified_tools = []
                for tool in tools_data.get("tools", []):
                    simplified_tools.append({
                        "name": tool.get("name", ""),
                        "description": tool.get("description", ""),
                        "parameters_summary": _summarize_params(tool.get("parameters", {})),
                        "returns_summary": _summarize_returns(tool.get("returns", {}))
                    })
                
                tools_list = simplified_tools
            else:
                # For detailed view, use full data
                tools_list = tools_data.get("tools", [])
            
            categories = tools_data.get("categories", [])
        
        result = {
            "success": True,
            "tools": tools_list,
            "count": len(tools_list),
            "categories": list(categories) if isinstance(categories, set) else categories,
            "error": None
        }
        
        logger.info(f"Successfully listed {len(tools_list)} tools")
        return result
        
    except Exception as e:
        error_msg = f"Error listing tools: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "tools": [],
            "count": 0,
            "categories": [],
            "error": error_msg
        }


def _summarize_params(params: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Summarize parameter information to a simplified format.
    
    Args:
        params: Full parameter schema information
    
    Returns:
        List of simplified parameter information
    """
    summary = []
    for name, info in params.items():
        summary.append({
            "name": name,
            "type": info.get("type", "unknown"),
            "description": info.get("description", ""),
            "required": info.get("required", False)
        })
    return summary


def _summarize_returns(returns: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Summarize return value information to a simplified format.
    
    Args:
        returns: Full return value schema information
    
    Returns:
        List of simplified return value information
    """
    summary = []
    for name, info in returns.items():
        summary.append({
            "name": name,
            "type": info.get("type", "unknown"),
            "description": info.get("description", "")
        })
    return summary