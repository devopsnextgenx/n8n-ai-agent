"""Tests for Base64 tool functionality."""

import base64
import pytest

from n8n_mcp_server.tools.base64_tool import register_base64_tool
from n8n_mcp_server.utils.helpers import validate_base64


class TestBase64Tool:
    """Test cases for Base64 encoding/decoding tool."""
    
    def test_encrypt_simple_text(self, mcp_server, sample_text_data):
        """Test encoding simple text to base64."""
        # Register the tool
        register_base64_tool(mcp_server)
        
        # Get the encrypt function
        encrypt_func = None
        if hasattr(mcp_server, '_tools'):
            encrypt_func = mcp_server._tools.get('encrypt')
        
        assert encrypt_func is not None, "Encrypt function not registered"
        
        # Test encoding
        result = encrypt_func(sample_text_data)
        
        # Verify the result
        assert isinstance(result, str)
        assert validate_base64(result)
        
        # Verify we can decode it back
        decoded = base64.b64decode(result).decode('utf-8')
        assert decoded == sample_text_data
    
    def test_decrypt_valid_base64(self, mcp_server, sample_base64_data, sample_text_data):
        """Test decoding valid base64 data."""
        # Register the tool
        register_base64_tool(mcp_server)
        
        # Get the decrypt function
        decrypt_func = None
        if hasattr(mcp_server, '_tools'):
            decrypt_func = mcp_server._tools.get('decrypt')
        
        assert decrypt_func is not None, "Decrypt function not registered"
        
        # Test decoding
        result = decrypt_func(sample_base64_data)
        
        # Verify the result
        assert result == sample_text_data
    
    def test_decrypt_invalid_base64(self, mcp_server):
        """Test decoding invalid base64 data."""
        # Register the tool
        register_base64_tool(mcp_server)
        
        # Get the decrypt function
        decrypt_func = None
        if hasattr(mcp_server, '_tools'):
            decrypt_func = mcp_server._tools.get('decrypt')
        
        assert decrypt_func is not None, "Decrypt function not registered"
        
        # Test with invalid base64
        result = decrypt_func("invalid_base64!")
        
        # Should return None for invalid input
        assert result is None
    
    def test_decrypt_empty_input(self, mcp_server):
        """Test decoding empty input."""
        # Register the tool
        register_base64_tool(mcp_server)
        
        # Get the decrypt function
        decrypt_func = None
        if hasattr(mcp_server, '_tools'):
            decrypt_func = mcp_server._tools.get('decrypt')
        
        assert decrypt_func is not None, "Decrypt function not registered"
        
        # Test with empty input
        result = decrypt_func("")
        
        # Should return None for empty input
        assert result is None
    
    def test_validate_base64_string_valid(self, mcp_server, sample_base64_data):
        """Test validation of valid base64 string."""
        # Register the tool
        register_base64_tool(mcp_server)
        
        # Get the validation function
        validate_func = None
        if hasattr(mcp_server, '_tools'):
            validate_func = mcp_server._tools.get('validate_base64_string')
        
        assert validate_func is not None, "Validate function not registered"
        
        # Test validation
        result = validate_func(sample_base64_data)
        
        # Should return True for valid base64
        assert result is True
    
    def test_validate_base64_string_invalid(self, mcp_server):
        """Test validation of invalid base64 string."""
        # Register the tool
        register_base64_tool(mcp_server)
        
        # Get the validation function
        validate_func = None
        if hasattr(mcp_server, '_tools'):
            validate_func = mcp_server._tools.get('validate_base64_string')
        
        assert validate_func is not None, "Validate function not registered"
        
        # Test validation with invalid data
        result = validate_func("invalid_base64!")
        
        # Should return False for invalid base64
        assert result is False
    
    def test_encrypt_binary_data(self, mcp_server, sample_binary_data):
        """Test encoding binary data."""
        # Register the tool
        register_base64_tool(mcp_server)
        
        # Get the encrypt function
        encrypt_func = None
        if hasattr(mcp_server, '_tools'):
            encrypt_func = mcp_server._tools.get('encrypt')
        
        assert encrypt_func is not None, "Encrypt function not registered"
        
        # Convert binary to hex string for input
        hex_input = sample_binary_data.hex()
        
        # Test encoding
        result = encrypt_func(hex_input)
        
        # Verify the result
        assert isinstance(result, str)
        assert validate_base64(result)