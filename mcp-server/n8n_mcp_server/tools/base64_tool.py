"""Base64 encoding/decoding tool for MCP server."""

import base64
import logging
from typing import Optional

from fastmcp import FastMCP

from ..utils.helpers import safe_decode, validate_base64, sanitize_input


logger = logging.getLogger(__name__)


def register_base64_tool(mcp: FastMCP) -> None:
    """Register Base64 tools with the MCP server.
    
    Args:
        mcp: FastMCP server instance
    """
    
    @mcp.tool()
    def encrypt(data: str) -> str:
        """
        Encode data to Base64 format.
        
        Accepts a base64 or raw string data, returns base64-encoded string.
        If input is not valid base64, treat as raw bytes (utf-8) then encode.
        
        Args:
            data: String data to encode
            
        Returns:
            str: Base64 encoded string
        """
        try:
            logger.debug(f"Encoding data: {sanitize_input(data)[:50]}...")
            
            # If it's already valid base64, decode first then re-encode
            if validate_base64(data):
                try:
                    raw = base64.b64decode(data, validate=True)
                    logger.debug("Input was valid base64, decoded first")
                except Exception:
                    # If decoding fails, treat as raw text
                    raw = data.encode("utf-8")
            else:
                # Treat input as utf-8 text
                raw = data.encode("utf-8")
            
            result = base64.b64encode(raw).decode("ascii")
            logger.info(f"Successfully encoded {len(data)} characters to base64")
            return result
            
        except Exception as e:
            logger.error(f"Failed to encode data: {e}")
            raise ValueError(f"Encoding failed: {str(e)}")
    
    @mcp.tool()
    def decrypt(encoded: str) -> Optional[str]:
        """
        Decode Base64 encoded string.
        
        Accepts a base64-encoded string, returns decoded string (utf-8) if possible,
        or returns None / error if decoding fails.
        
        Args:
            encoded: Base64 encoded string to decode
            
        Returns:
            str | None: Decoded string or None if decoding fails
        """
        try:
            logger.debug(f"Decoding base64 data: {sanitize_input(encoded)[:50]}...")
            
            if not encoded:
                logger.warning("Empty input provided for decoding")
                return None
                
            # Validate and decode base64
            try:
                raw = base64.b64decode(encoded, validate=True)
            except Exception as e:
                logger.error(f"Invalid base64 input: {e}")
                return None
            
            # Try to decode to utf-8 string
            try:
                result = raw.decode("utf-8")
                logger.info(f"Successfully decoded base64 to {len(result)} characters")
                return result
            except UnicodeDecodeError:
                # Return binary data as hex if not valid UTF-8
                hex_result = raw.hex()
                logger.info(f"Decoded to binary data, returning as hex: {len(hex_result)} chars")
                return hex_result
                
        except Exception as e:
            logger.error(f"Failed to decode data: {e}")
            return None
    
    @mcp.tool()
    def validate_base64_string(data: str) -> bool:
        """
        Validate if a string is valid Base64.
        
        Args:
            data: String to validate
            
        Returns:
            bool: True if valid Base64, False otherwise
        """
        try:
            logger.debug(f"Validating base64: {sanitize_input(data)[:50]}...")
            result = validate_base64(data)
            logger.info(f"Base64 validation result: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to validate base64: {e}")
            return False
    
    logger.info("Base64 tools registered successfully")