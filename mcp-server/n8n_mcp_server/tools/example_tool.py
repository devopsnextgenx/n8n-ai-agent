"""Example tool template for MCP server."""

import logging
from typing import Any, Dict, List

from fastmcp import FastMCP

from ..utils.helpers import format_response


logger = logging.getLogger(__name__)


def register_example_tool(mcp: FastMCP) -> None:
    """Register example tools with the MCP server.
    
    This is a template for creating new tools. Copy this file and modify
    as needed for your specific tool requirements.
    
    Args:
        mcp: FastMCP server instance
    """
    
    @mcp.tool()
    def example_function(param: str, optional_param: int = 10) -> Dict[str, Any]:
        """
        Example tool function.
        
        This is a template function that demonstrates how to create
        a new tool for the MCP server.
        
        Args:
            param: Required string parameter
            optional_param: Optional integer parameter (default: 10)
            
        Returns:
            Dict[str, Any]: Formatted response with result
        """
        try:
            logger.debug(f"Example function called with param='{param}', optional_param={optional_param}")
            
            # Your tool logic here
            result = f"Processed '{param}' with value {optional_param}"
            
            logger.info(f"Example function completed successfully")
            
            return format_response(
                success=True,
                data={"result": result, "input_param": param, "optional_param": optional_param},
                message="Example function executed successfully"
            )
            
        except Exception as e:
            logger.error(f"Example function failed: {e}")
            return format_response(
                success=False,
                error=str(e),
                message="Example function execution failed"
            )
    
    @mcp.tool()
    def example_list_processor(items: List[str]) -> Dict[str, Any]:
        """
        Example tool for processing lists.
        
        Args:
            items: List of strings to process
            
        Returns:
            Dict[str, Any]: Formatted response with processed items
        """
        try:
            logger.debug(f"Processing list with {len(items)} items")
            
            if not items:
                return format_response(
                    success=False,
                    error="Empty list provided",
                    message="List cannot be empty"
                )
            
            # Process the items (example: convert to uppercase)
            processed_items = [item.upper() for item in items]
            
            logger.info(f"Successfully processed {len(items)} items")
            
            return format_response(
                success=True,
                data={
                    "original_items": items,
                    "processed_items": processed_items,
                    "count": len(items)
                },
                message="List processing completed successfully"
            )
            
        except Exception as e:
            logger.error(f"List processing failed: {e}")
            return format_response(
                success=False,
                error=str(e),
                message="List processing failed"
            )
    
    logger.info("Example tools registered successfully")


# Uncomment the line below in tools/__init__.py to register this tool:
# register_example_tool(mcp)