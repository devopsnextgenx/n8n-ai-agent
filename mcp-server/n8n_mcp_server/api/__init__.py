"""HTTP endpoints for n8n integration."""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from ..tools.base64_tool import register_base64_tool
from ..utils.helpers import format_response, sanitize_input


logger = logging.getLogger(__name__)

# Create router for MCP endpoints
router = APIRouter(prefix="/mcp", tags=["MCP Tools"])


# Pydantic models for request/response validation
class ToolRequest(BaseModel):
    """Base model for tool requests."""
    tool_name: str = Field(..., description="Name of the MCP tool to execute")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")


class ToolResponse(BaseModel):
    """Base model for tool responses."""
    success: bool = Field(..., description="Whether the operation was successful")
    data: Optional[Any] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if failed")
    tool_name: str = Field(..., description="Name of the executed tool")


class Base64EncodeRequest(BaseModel):
    """Request model for Base64 encoding."""
    data: str = Field(..., description="Data to encode to Base64")


class Base64DecodeRequest(BaseModel):
    """Request model for Base64 decoding."""
    encoded: str = Field(..., description="Base64 encoded data to decode")


class Base64ValidateRequest(BaseModel):
    """Request model for Base64 validation."""
    data: str = Field(..., description="Data to validate as Base64")


class ToolInfo(BaseModel):
    """Information about an available tool."""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    parameters: Dict[str, Any] = Field(..., description="Tool parameters schema")


# Store tool functions for HTTP access
_tools_registry: Dict[str, Any] = {}


def initialize_tools_registry():
    """Initialize tools registry for HTTP access."""
    global _tools_registry
    
    # Register Base64 tools manually for HTTP access
    import base64
    
    def encrypt(data: str) -> str:
        """Encode data to Base64 format."""
        try:
            raw = data.encode("utf-8")
            return base64.b64encode(raw).decode("ascii")
        except Exception as e:
            raise ValueError(f"Encoding failed: {str(e)}")
    
    def decrypt(encoded: str) -> Optional[str]:
        """Decode Base64 data."""
        try:
            if not encoded:
                return None
            raw = base64.b64decode(encoded, validate=True)
            try:
                return raw.decode("utf-8")
            except UnicodeDecodeError:
                return raw.hex()
        except Exception:
            return None
    
    def validate_base64_string(data: str) -> bool:
        """Validate if string is valid Base64."""
        try:
            base64.b64decode(data, validate=True)
            return True
        except Exception:
            return False
    
    _tools_registry.update({
        "encrypt": encrypt,
        "decrypt": decrypt,
        "validate_base64_string": validate_base64_string
    })
    
    logger.info(f"Initialized {len(_tools_registry)} tools for HTTP access")


# Initialize tools on module import
initialize_tools_registry()


@router.get("/tools", response_model=List[ToolInfo])
async def list_tools():
    """List all available MCP tools."""
    tools = []
    
    for name, func in _tools_registry.items():
        # Extract function signature and docstring
        doc = getattr(func, '__doc__', 'No description available')
        
        # Simple parameter extraction (can be enhanced)
        import inspect
        sig = inspect.signature(func)
        parameters = {}
        
        for param_name, param in sig.parameters.items():
            parameters[param_name] = {
                "type": str(param.annotation) if param.annotation != inspect.Parameter.empty else "Any",
                "required": param.default == inspect.Parameter.empty,
                "default": param.default if param.default != inspect.Parameter.empty else None
            }
        
        tools.append(ToolInfo(
            name=name,
            description=doc.split('\n')[0] if doc else "No description",
            parameters=parameters
        ))
    
    return tools


@router.post("/execute", response_model=ToolResponse)
async def execute_tool(request: ToolRequest):
    """Execute an MCP tool by name."""
    try:
        tool_name = request.tool_name
        parameters = request.parameters
        
        logger.info(f"Executing tool: {tool_name} with parameters: {sanitize_input(str(parameters))}")
        
        if tool_name not in _tools_registry:
            raise HTTPException(
                status_code=404,
                detail=f"Tool '{tool_name}' not found. Available tools: {list(_tools_registry.keys())}"
            )
        
        tool_func = _tools_registry[tool_name]
        
        # Execute the tool
        try:
            result = tool_func(**parameters)
            
            return ToolResponse(
                success=True,
                data=result,
                tool_name=tool_name
            )
            
        except TypeError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid parameters for tool '{tool_name}': {str(e)}"
            )
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return ToolResponse(
                success=False,
                error=str(e),
                tool_name=tool_name
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in execute_tool: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Specific endpoints for Base64 tools (for easier n8n integration)
@router.post("/base64/encode")
async def encode_base64(request: Base64EncodeRequest):
    """Encode data to Base64 format."""
    try:
        if 'encrypt' not in _tools_registry:
            raise HTTPException(status_code=503, detail="Base64 encode tool not available")
        
        result = _tools_registry['encrypt'](request.data)
        
        return {
            "success": True,
            "data": {
                "original": request.data,
                "encoded": result
            },
            "tool": "base64_encode"
        }
        
    except Exception as e:
        logger.error(f"Base64 encode failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "tool": "base64_encode"
        }


@router.post("/base64/decode")
async def decode_base64(request: Base64DecodeRequest):
    """Decode Base64 data."""
    try:
        if 'decrypt' not in _tools_registry:
            raise HTTPException(status_code=503, detail="Base64 decode tool not available")
        
        result = _tools_registry['decrypt'](request.encoded)
        
        return {
            "success": True,
            "data": {
                "encoded": request.encoded,
                "decoded": result
            },
            "tool": "base64_decode"
        }
        
    except Exception as e:
        logger.error(f"Base64 decode failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "tool": "base64_decode"
        }


@router.post("/base64/validate")
async def validate_base64(request: Base64ValidateRequest):
    """Validate if data is valid Base64."""
    try:
        if 'validate_base64_string' not in _tools_registry:
            raise HTTPException(status_code=503, detail="Base64 validate tool not available")
        
        result = _tools_registry['validate_base64_string'](request.data)
        
        return {
            "success": True,
            "data": {
                "input": request.data,
                "is_valid": result
            },
            "tool": "base64_validate"
        }
        
    except Exception as e:
        logger.error(f"Base64 validate failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "tool": "base64_validate"
        }


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "tools_available": len(_tools_registry),
        "service": "n8n-mcp-server"
    }