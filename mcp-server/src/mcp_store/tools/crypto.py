"""Crypto tools for MCP Crypto Server.

This tool provides base64 decoding functionality.
"""

from typing import Any, Dict
import sys
from pathlib import Path

# Add src to path for absolute imports
src_path = Path(__file__).parent.parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from utils import encode_to_base64, decode_from_base64, validate_base64, get_logger

logger = get_logger(__name__)


async def encrypt_tool(text: str) -> Dict[str, Any]:
    """Encrypt (encode) string to base64.
    
    Args:
        text: The string to encode to base64
        
    Returns:
        Dict containing the base64 encoded result or error
    """
    try:
        logger.debug(f"Encrypting text of length {len(text)}")
        
        if not text:
            return {
                "success": False,
                "error": "Input text cannot be empty",
                "result": None
            }
        
        encrypted_text = encode_to_base64(text)
        
        logger.debug("Text encrypted successfully")
        return {
            "success": True,
            "error": None,
            "result": encrypted_text,
        }
        
    except TypeError as e:
        error_msg = f"Type error: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "result": None
        }
    except UnicodeEncodeError as e:
        error_msg = f"Unicode encoding error: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "result": None
        }
    except Exception as e:
        error_msg = f"Unexpected error during encryption: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "result": None
        }

async def decrypt_tool(text: str) -> Dict[str, Any]:
    """Decrypt (decode) base64 string back to original text.
    
    Args:
        text: The base64 encoded string to decode
        
    Returns:
        Dict containing the decoded result or error
    """
    try:
        logger.debug(f"Decrypting base64 text of length {len(text)}")
        
        if not text:
            return {
                "success": False,
                "error": "Input encoded text cannot be empty",
                "result": None
            }
        
        # Validate base64 format first
        if not validate_base64(text):
            return {
                "success": False,
                "error": "Invalid base64 format",
                "result": None
            }
        
        decrypted_text = decode_from_base64(text)
        
        logger.debug("Base64 text decrypted successfully")
        return {
            "success": True,
            "error": None,
            "result": decrypted_text,
        }
        
    except TypeError as e:
        error_msg = f"Type error: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "result": None
        }
    except ValueError as e:
        error_msg = f"Value error: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "result": None
        }
    except UnicodeDecodeError as e:
        error_msg = f"Unicode decoding error: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "result": None
        }
    except Exception as e:
        error_msg = f"Unexpected error during decryption: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "result": None
        }