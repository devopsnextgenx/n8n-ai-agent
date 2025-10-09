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

# Handle imports - try different import paths based on how the module is used
try:
    # Try relative import first (when used as a package)
    from .config import LoggingConfig, get_config
except ImportError:
    try:
        # Try absolute import with src prefix (when run from project root)
        from src.config import LoggingConfig, get_config
    except ImportError:
        # Fallback to direct import (when in the same directory)
        from config import LoggingConfig, get_config

# Cache for logging configuration
_logging_configured = False
_logging_config_cache = None


def setup_logging(logging_config: LoggingConfig) -> logging.Logger:
    """Set up logging configuration for console and file output.
    
    Args:
        logging_config: Logging configuration settings
        
    Returns:
        logging.Logger: Configured logger instance
    """
    global _logging_configured, _logging_config_cache
    
    # Cache the logging configuration for reuse by get_logger
    _logging_config_cache = logging_config
    _logging_configured = True
    
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
    
    logger.debug("Logging configured successfully")
    
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
    """Get logger instance configured according to config.yml.
    
    If logging has not been set up yet, this function will attempt to
    set it up using the cached configuration or by loading the configuration
    from config.yml.
    
    Args:
        name: Logger name, defaults to module name
        
    Returns:
        logging.Logger: Configured logger instance
    """
    global _logging_configured
    
    if name is None:
        name = "mcp_crypto_server"
    
    # Create the proper logger name with namespace
    if name != "mcp_crypto_server" and not name.startswith("mcp_crypto_server."):
        logger_name = f"mcp_crypto_server.{name}"
    else:
        logger_name = name
    
    # Check if logging system is already configured
    if not _logging_configured:
        # Get the root logger for MCP to check if it's configured
        root_logger = logging.getLogger("mcp_crypto_server")
        
        # If no handlers, we need to set up logging
        if not root_logger.handlers:
            try:
                # Try to use cached config first if available
                if _logging_config_cache is not None:
                    setup_logging(_logging_config_cache)
                else:
                    # Otherwise try to load config and set up logging
                    config = get_config()
                    setup_logging(config.logging)
            except Exception as e:
                # If all else fails, set up a basic console and file logger
                console_handler = logging.StreamHandler(sys.stdout)
                formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
                console_handler.setFormatter(formatter)
                root_logger.addHandler(console_handler)
                
                # Try to add a file handler too
                try:
                    log_dir = Path("logs")
                    log_dir.mkdir(exist_ok=True)
                    file_handler = RotatingFileHandler(
                        "logs/mcp-server.log",
                        maxBytes=10 * 1024 * 1024,
                        backupCount=3,
                        encoding='utf-8'
                    )
                    file_handler.setFormatter(formatter)
                    root_logger.addHandler(file_handler)
                except Exception:
                    # Continue even if file handler setup fails
                    pass
                    
                root_logger.setLevel(logging.INFO)
                root_logger.warning(f"Could not load logging configuration: {e}. Using default settings.")
                
                # Mark as configured so we don't try again
                _logging_configured = True
    
    # Return the requested logger (which inherits from the root logger's configuration)
    return logging.getLogger(logger_name)