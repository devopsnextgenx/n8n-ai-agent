"""Utility functions for MCP Crypto Server.

This module provides utility functions including base64 encoding/decoding,
logging setup, and other helper functions.
"""

import base64
import logging
import os
import sys
import binascii
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional, Union

# Handle imports - try relative first, fall back to absolute
try:
    from .config import LoggingConfig
except ImportError:
    # If relative import fails, try absolute import
    from config import LoggingConfig


def setup_logging(logging_config: LoggingConfig) -> logging.Logger:
    """Set up logging configuration for console and file output.
    
    Args:
        logging_config: Logging configuration settings
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_file_path = Path(logging_config.file)
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    logger = logging.getLogger("mcp_crypto_server")
    logger.setLevel(getattr(logging, logging_config.level.upper(), logging.INFO))
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(logging_config.format)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    max_bytes = _parse_file_size(logging_config.max_file_size)
    file_handler = RotatingFileHandler(
        logging_config.file,
        maxBytes=max_bytes,
        backupCount=logging_config.backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


def _parse_file_size(size_str: str) -> int:
    """Parse file size string to bytes.
    
    Args:
        size_str: Size string like "10MB", "1GB", etc.
        
    Returns:
        int: Size in bytes
    """
    size_str = size_str.upper().strip()
    
    # Extract number and unit
    unit_multipliers = {
        'B': 1,
        'KB': 1024,
        'MB': 1024 * 1024,
        'GB': 1024 * 1024 * 1024,
    }
    
    for unit, multiplier in unit_multipliers.items():
        if size_str.endswith(unit):
            number_part = size_str[:-len(unit)].strip()
            try:
                return int(float(number_part) * multiplier)
            except ValueError:
                break
    
    # Default to 10MB if parsing fails
    return 10 * 1024 * 1024


def encode_to_base64(text: str) -> str:
    """Encode string to base64.
    
    Args:
        text: Input string to encode
        
    Returns:
        str: Base64 encoded string
        
    Raises:
        TypeError: If input is not a string
        UnicodeEncodeError: If string contains invalid characters
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    
    try:
        # Convert string to bytes using UTF-8 encoding
        text_bytes = text.encode('utf-8')
        # Encode to base64 and decode back to string
        encoded_bytes = base64.b64encode(text_bytes)
        return encoded_bytes.decode('ascii')
    except UnicodeEncodeError as e:
        raise UnicodeEncodeError(
            e.encoding, e.object, e.start, e.end,
            f"Unable to encode string to UTF-8: {e.reason}"
        )


def decode_from_base64(encoded_text: str) -> str:
    """Decode base64 string back to original text.
    
    Args:
        encoded_text: Base64 encoded string
        
    Returns:
        str: Decoded original string
        
    Raises:
        TypeError: If input is not a string
        ValueError: If input is not valid base64
        UnicodeDecodeError: If decoded bytes are not valid UTF-8
    """
    if not isinstance(encoded_text, str):
        raise TypeError("Input must be a string")
    
    try:
        # Decode from base64
        decoded_bytes = base64.b64decode(encoded_text)
        # Convert bytes back to string using UTF-8
        return decoded_bytes.decode('utf-8')
    except Exception as e:
        if isinstance(e, binascii.Error):
            raise ValueError(f"Invalid base64 input: {str(e)}")
        elif isinstance(e, UnicodeDecodeError):
            raise UnicodeDecodeError(
                e.encoding, e.object, e.start, e.end,
                f"Unable to decode bytes to UTF-8: {e.reason}"
            )
        else:
            raise ValueError(f"Decoding failed: {str(e)}")


def validate_base64(encoded_text: str) -> bool:
    """Validate if string is valid base64.
    
    Args:
        encoded_text: String to validate
        
    Returns:
        bool: True if valid base64, False otherwise
    """
    try:
        decode_from_base64(encoded_text)
        return True
    except (TypeError, ValueError, UnicodeDecodeError):
        return False


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get logger instance.
    
    Args:
        name: Logger name, defaults to module name
        
    Returns:
        logging.Logger: Logger instance
    """
    if name is None:
        name = "mcp_crypto_server"
    return logging.getLogger(name)