"""Tools list tool for MCP Crypto Server.

This tool provides information about available tools with their schemas and descriptions.
"""

import json
import sys
import inspect
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
            # Get tools directly from FastMCP app's tool registry
            logger.info("Getting tools from FastMCP app instance")
            
            # Access the actual tool registry - FastMCP stores tools in different attributes
            tools_registry = None
            
            # Try different possible attributes where FastMCP might store tools
            for attr in ['_tools', 'tools', '_tool_registry', 'tool_registry', '_resources']:
                if hasattr(app, attr):
                    potential_registry = getattr(app, attr)
                    logger.info(f"Found attribute '{attr}': {type(potential_registry)}")
                    
                    # Check if it's a dict-like structure
                    if hasattr(potential_registry, 'items') or hasattr(potential_registry, '__getitem__'):
                        tools_registry = potential_registry
                        logger.info(f"Using '{attr}' as tools registry")
                        break
            
            if not tools_registry:
                logger.warning("Could not find tools registry in app, falling back to static resource")
                # Fall through to static resource
                app = None
            else:
                # Process tools from registry
                tools_list = []
                categories = set()
                
                # Handle dict-like registry
                if hasattr(tools_registry, 'items'):
                    items = tools_registry.items()
                else:
                    # Handle list-like registry
                    items = [(str(i), tool) for i, tool in enumerate(tools_registry)]
                
                for tool_name, tool_obj in items:
                    logger.info(f"Processing tool: {tool_name}, type: {type(tool_obj)}")
                    
                    # Extract tool information
                    tool_info = _extract_tool_info(tool_name, tool_obj, detailed)
                    
                    # Determine category
                    category = _determine_category(tool_info["name"])
                    if category:
                        tool_info["category"] = category
                        categories.add(category)
                    
                    tools_list.append(tool_info)
                    logger.info(f"Extracted tool info: {json.dumps(tool_info, indent=2)}")
        
        # Fallback to static resource if app not provided or registry not found
        if not app:
            logger.info("Using static resource for tools list")
            from src.mcp_store.resources.tools_list import get_tools_list_resource
            
            # Get the full tools list from the resource
            tools_json = await get_tools_list_resource()
            tools_data = json.loads(tools_json)
            
            # Process tools based on detail level
            if not detailed:
                # For non-detailed view, simplify the output
                simplified_tools = []
                for tool in tools_data.get("tools", []):
                    tool_dict = {
                        "name": tool.get("name", ""),
                        "description": tool.get("description", ""),
                    }
                    
                    params = tool.get("parameters", {})
                    if params:
                        tool_dict["parameters_summary"] = _summarize_params(params)
                    
                    returns = tool.get("returns", {})
                    if returns:
                        tool_dict["returns_summary"] = _summarize_returns(returns)
                    
                    category = tool.get("category")
                    if category:
                        tool_dict["category"] = category
                    
                    simplified_tools.append(tool_dict)
                
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
        logger.error(error_msg, exc_info=True)
        return {
            "success": False,
            "tools": [],
            "count": 0,
            "categories": [],
            "error": error_msg
        }


def _extract_tool_info(tool_name: str, tool_obj: Any, detailed: bool = False) -> Dict[str, Any]:
    """Extract all available information from a tool object.
    
    Args:
        tool_name: Name of the tool
        tool_obj: Tool object to extract information from
        detailed: Whether to include detailed information
        
    Returns:
        Dictionary with tool information
    """
    tool_info = {"name": tool_name}
    
    # If tool_obj is a string, it's just a name reference
    if isinstance(tool_obj, str):
        tool_info["description"] = ""
        return tool_info
    
    logger.info(f"Tool '{tool_name}' type: {type(tool_obj)}, attributes: {dir(tool_obj)[:20]}...")
    
    # Extract description
    description = None
    
    # Try direct attributes
    for attr in ['description', 'desc', '__doc__']:
        if hasattr(tool_obj, attr):
            val = getattr(tool_obj, attr)
            if val and isinstance(val, str) and "str(object=" not in val:
                description = val.strip()
                logger.info(f"Found description in {attr}: {description[:100]}")
                break
    
    # Try nested function/handler
    if not description:
        for fn_attr in ['fn', 'func', 'handler', 'callback', '_fn']:
            if hasattr(tool_obj, fn_attr):
                fn = getattr(tool_obj, fn_attr)
                if fn and callable(fn):
                    fn_doc = inspect.getdoc(fn)
                    if fn_doc and "str(object=" not in fn_doc:
                        description = fn_doc
                        logger.info(f"Found description in {fn_attr}.__doc__: {description[:100]}")
                        break
    
    tool_info["description"] = description or ""
    
    # Extract parameters/input schema
    params = _extract_input_schema(tool_obj)
    
    if params:
        if detailed:
            tool_info["parameters"] = params
        else:
            tool_info["parameters_summary"] = _summarize_params(params)
    
    # Extract returns/output schema
    returns = _extract_output_schema(tool_obj)
    
    if returns:
        if detailed:
            tool_info["returns"] = returns
        else:
            tool_info["returns_summary"] = _summarize_returns(returns)
    
    # Extract examples if available
    if detailed and hasattr(tool_obj, 'examples'):
        examples = getattr(tool_obj, 'examples')
        if examples:
            tool_info["examples"] = examples
    
    return tool_info


def _extract_input_schema(tool_obj: Any) -> Optional[Dict[str, Any]]:
    """Extract input schema from a tool object.
    
    Args:
        tool_obj: Tool object to extract schema from
        
    Returns:
        Input schema dictionary or None
    """
    # Try to get input schema from various attributes
    for schema_attr in ['input_schema', 'inputSchema', 'parameters_schema', 'params_schema', 'schema']:
        if hasattr(tool_obj, schema_attr):
            schema = getattr(tool_obj, schema_attr)
            
            if schema:
                # Handle dict-based schema
                if isinstance(schema, dict):
                    return schema.get('properties', schema)
                # Handle object with properties
                elif hasattr(schema, 'properties'):
                    props = schema.properties
                    if isinstance(props, dict):
                        return props
                # Handle Pydantic model
                elif hasattr(schema, 'model_fields'):
                    return {
                        name: {
                            "type": _get_field_type(field),
                            "description": field.description or ""
                        }
                        for name, field in schema.model_fields.items()
                    }
    
    # Try to extract from function signature
    for fn_attr in ['fn', 'func', 'handler', 'callback', '_fn']:
        if hasattr(tool_obj, fn_attr):
            fn = getattr(tool_obj, fn_attr)
            if fn and callable(fn):
                try:
                    sig = inspect.signature(fn)
                    params = {}
                    for param_name, param in sig.parameters.items():
                        if param_name not in ['self', 'cls']:
                            param_info = {
                                "type": str(param.annotation) if param.annotation != inspect.Parameter.empty else "any",
                                "required": param.default == inspect.Parameter.empty
                            }
                            params[param_name] = param_info
                    if params:
                        logger.info(f"Extracted params from function signature: {params}")
                        return params
                except Exception as e:
                    logger.warning(f"Could not extract signature: {e}")
    
    return None


def _extract_output_schema(tool_obj: Any) -> Optional[Dict[str, Any]]:
    """Extract output schema from a tool object.
    
    Args:
        tool_obj: Tool object to extract schema from
        
    Returns:
        Output schema dictionary or None
    """
    for schema_attr in ['output_schema', 'outputSchema', 'return_schema', 'returns_schema', 'response_schema']:
        if hasattr(tool_obj, schema_attr):
            schema = getattr(tool_obj, schema_attr)
            
            if schema:
                if isinstance(schema, dict):
                    return schema.get('properties', schema)
                elif hasattr(schema, 'properties'):
                    props = schema.properties
                    if isinstance(props, dict):
                        return props
    
    return None


def _get_field_type(field) -> str:
    """Get type string from a Pydantic field.
    
    Args:
        field: Pydantic field object
        
    Returns:
        Type string
    """
    if hasattr(field, 'annotation'):
        annotation = field.annotation
        if hasattr(annotation, '__name__'):
            return annotation.__name__
        return str(annotation).replace('typing.', '')
    return "any"


def _determine_category(tool_name: str) -> Optional[str]:
    """Determine category from tool name.
    
    Args:
        tool_name: Name of the tool
        
    Returns:
        Category string or None
    """
    name_lower = tool_name.lower()
    
    if "encrypt" in name_lower or "decrypt" in name_lower or "crypto" in name_lower or "hash" in name_lower:
        return "crypto"
    elif any(op in name_lower for op in ["add", "subtract", "multiply", "divide", "modulo", "calculate"]):
        return "calculator"
    elif "script" in name_lower or "exec" in name_lower or "run" in name_lower:
        return "execution"
    elif "list" in name_lower or "get_tools" in name_lower or "discover" in name_lower:
        return "discovery"
    
    return None


def _summarize_params(params: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Summarize parameter information to a simplified format.
    
    Args:
        params: Full parameter schema information
    
    Returns:
        List of simplified parameter information
    """
    summary = []
    for name, info in params.items():
        param_summary = {
            "name": name,
            "type": info.get("type", "any") if isinstance(info, dict) else "any",
        }
        
        if isinstance(info, dict):
            if "description" in info:
                param_summary["description"] = info["description"]
            if "required" in info:
                param_summary["required"] = info["required"]
        
        summary.append(param_summary)
    
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
        return_summary = {
            "name": name,
            "type": info.get("type", "any") if isinstance(info, dict) else "any",
        }
        
        if isinstance(info, dict) and "description" in info:
            return_summary["description"] = info["description"]
        
        summary.append(return_summary)
    
    return summary