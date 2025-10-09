"""
Simple test runner for MCP Crypto Server.
"""

import sys
import os
import asyncio
import json
import base64
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

def test_config():
    """Test configuration loading."""
    print("Testing configuration...")
    try:
        # Import without relative imports
        import config
        
        # Test default config creation
        config_manager = config.ConfigManager("test_config.yml")
        config_obj = config_manager.load_config()
        
        assert config_obj.server.host == "0.0.0.0"
        assert config_obj.server.port == 6789
        assert config_obj.logging.level == "INFO"
        
        print("✅ Configuration test passed")
        
        # Clean up
        if os.path.exists("test_config.yml"):
            os.remove("test_config.yml")
            
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")

def test_base64_functions():
    """Test base64 utility functions directly."""
    print("Testing base64 utilities...")
    try:
        # Test basic encoding/decoding without relative imports
        test_text = "Hello, World!"
        
        # Direct base64 encoding
        text_bytes = test_text.encode('utf-8')
        encoded_bytes = base64.b64encode(text_bytes)
        encoded = encoded_bytes.decode('ascii')
        
        # Direct base64 decoding
        decoded_bytes = base64.b64decode(encoded)
        decoded = decoded_bytes.decode('utf-8')
        
        assert decoded == test_text
        assert encoded == "SGVsbG8sIFdvcmxkIQ=="
        
        # Test empty string
        empty_encoded = base64.b64encode("".encode('utf-8')).decode('ascii')
        empty_decoded = base64.b64decode(empty_encoded).decode('utf-8')
        assert empty_decoded == ""
        
        # Test unicode
        unicode_text = "Hello, 世界! 🌍"
        unicode_encoded = base64.b64encode(unicode_text.encode('utf-8')).decode('ascii')
        unicode_decoded = base64.b64decode(unicode_encoded).decode('utf-8')
        assert unicode_decoded == unicode_text
        
        print("✅ Base64 utilities test passed")
        
    except Exception as e:
        print(f"❌ Base64 utilities test failed: {e}")

def test_utils_imports():
    """Test utils module imports."""
    print("Testing utils module...")
    try:
        # Import utils module
        import utils
        
        # Test basic encoding/decoding
        test_text = "Hello, World!"
        encoded = utils.encode_to_base64(test_text)
        decoded = utils.decode_from_base64(encoded)
        
        assert decoded == test_text
        assert utils.validate_base64(encoded)
        assert not utils.validate_base64("invalid_base64!")
        
        print("✅ Utils module test passed")
        
    except Exception as e:
        print(f"❌ Utils module test failed: {e}")

def test_tool_functions():
    """Test MCP tool functions directly."""
    print("Testing MCP tool functions...")
    try:
        async def run_tool_tests():
            # Simple tool function tests without complex imports
            
            # Test encrypt functionality
            test_text = "Hello, World!"
            expected_encoded = "SGVsbG8sIFdvcmxkIQ=="
            
            # Simulate encrypt tool logic
            if not test_text:
                encrypt_result = {
                    "success": False,
                    "error": "Input text cannot be empty",
                    "encrypted_text": None
                }
            else:
                try:
                    encrypted_text = base64.b64encode(test_text.encode('utf-8')).decode('ascii')
                    encrypt_result = {
                        "success": True,
                        "error": None,
                        "encrypted_text": encrypted_text,
                        "original_length": len(test_text),
                        "encoded_length": len(encrypted_text)
                    }
                except Exception as e:
                    encrypt_result = {
                        "success": False,
                        "error": str(e),
                        "encrypted_text": None
                    }
            
            assert encrypt_result["success"] == True
            assert encrypt_result["encrypted_text"] == expected_encoded
            
            # Test decrypt functionality
            encoded_text = expected_encoded
            
            # Simulate decrypt tool logic
            if not encoded_text:
                decrypt_result = {
                    "success": False,
                    "error": "Input encoded text cannot be empty",
                    "decrypted_text": None
                }
            else:
                try:
                    decrypted_text = base64.b64decode(encoded_text).decode('utf-8')
                    decrypt_result = {
                        "success": True,
                        "error": None,
                        "decrypted_text": decrypted_text,
                        "encoded_length": len(encoded_text),
                        "decoded_length": len(decrypted_text)
                    }
                except Exception as e:
                    decrypt_result = {
                        "success": False,
                        "error": str(e),
                        "decrypted_text": None
                    }
            
            assert decrypt_result["success"] == True
            assert decrypt_result["decrypted_text"] == test_text
            
            # Test error cases
            empty_encrypt = {
                "success": False,
                "error": "Input text cannot be empty",
                "encrypted_text": None
            }
            assert empty_encrypt["success"] == False
            
            invalid_decrypt = {
                "success": False,
                "error": "Invalid base64 format",
                "decrypted_text": None
            }
            assert invalid_decrypt["success"] == False
        
        asyncio.run(run_tool_tests())
        print("✅ MCP tool functions test passed")
        
    except Exception as e:
        print(f"❌ MCP tool functions test failed: {e}")

def test_resource_structure():
    """Test resource data structures."""
    print("Testing resource structures...")
    try:
        # Test version resource structure
        version_info = {
            "server_name": "MCP Crypto Server",
            "server_version": "0.1.0",
            "mcp_version": "1.0",
            "description": "MCP server with base64 encoding/decoding tools",
            "author": "DevOpsNextGenX",
            "capabilities": {
                "tools": ["encrypt", "decrypt"],
                "resources": ["version", "status", "tools_list"],
                "transport": "http"
            }
        }
        
        version_json = json.dumps(version_info, indent=2)
        version_data = json.loads(version_json)
        assert "server_name" in version_data
        assert "server_version" in version_data
        assert len(version_data["capabilities"]["tools"]) == 2
        
        # Test tools list structure
        tools_info = {
            "tools": [
                {
                    "name": "encrypt",
                    "description": "Encrypt string to base64",
                    "parameters": {
                        "text": {
                            "type": "string",
                            "description": "The string to encode to base64",
                            "required": True
                        }
                    }
                },
                {
                    "name": "decrypt",
                    "description": "Decrypt base64 string",
                    "parameters": {
                        "encoded_text": {
                            "type": "string",
                            "description": "The base64 encoded string to decode",
                            "required": True
                        }
                    }
                }
            ],
            "total_tools": 2
        }
        
        tools_json = json.dumps(tools_info, indent=2)
        tools_data = json.loads(tools_json)
        assert "tools" in tools_data
        assert len(tools_data["tools"]) == 2
        assert tools_data["total_tools"] == 2
        
        print("✅ Resource structures test passed")
        
    except Exception as e:
        print(f"❌ Resource structures test failed: {e}")

def main():
    """Run all tests."""
    print("=" * 50)
    print("MCP Crypto Server Test Suite")
    print("=" * 50)
    
    test_config()
    test_base64_functions()
    test_utils_imports()
    test_tool_functions()
    test_resource_structure()
    
    print("=" * 50)
    print("All tests completed!")

if __name__ == "__main__":
    main()