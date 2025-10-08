#!/usr/bin/env python3
"""Test script for crypto tools."""

import asyncio
import sys
import unittest
import pytest
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


class TestCryptoTools(unittest.TestCase):
    """Test class for crypto tools."""

    def test_imports(self):
        """Test that all required modules can be imported."""
        from mcp_store.tools.crypto import encrypt_tool, decrypt_tool
        self.assertIsNotNone(encrypt_tool)
        self.assertIsNotNone(decrypt_tool)

    @pytest.mark.asyncio
    async def test_encrypt_success(self):
        """Test encryption with valid input."""
        from mcp_store.tools.crypto import encrypt_tool
        
        # Test with simple string
        result = await encrypt_tool("Hello, World!")
        self.assertTrue(result["success"])
        self.assertIsNone(result["error"])
        self.assertIsNotNone(result["encrypted_text"])
        self.assertEqual(result["original_length"], 13)
        
        # Test with empty string
        result = await encrypt_tool("")
        self.assertFalse(result["success"])
        self.assertIsNotNone(result["error"])
        self.assertIn("cannot be empty", result["error"])
        
        # Test with special characters
        result = await encrypt_tool("Special Ch@r$ &%!")
        self.assertTrue(result["success"])
        self.assertIsNone(result["error"])
        self.assertIsNotNone(result["encrypted_text"])

    @pytest.mark.asyncio
    async def test_decrypt_success(self):
        """Test decryption with valid input."""
        from mcp_store.tools.crypto import encrypt_tool, decrypt_tool
        
        # First encrypt some text to get valid base64
        encrypted = await encrypt_tool("Test decryption")
        encrypted_text = encrypted["encrypted_text"]
        
        # Test decryption
        result = await decrypt_tool(encrypted_text)
        self.assertTrue(result["success"])
        self.assertIsNone(result["error"])
        self.assertEqual(result["decrypted_text"], "Test decryption")
        self.assertEqual(result["encoded_length"], len(encrypted_text))
        self.assertEqual(result["decoded_length"], 14)  # "Test decryption" length
    
    @pytest.mark.asyncio
    async def test_decrypt_failure(self):
        """Test decryption with invalid input."""
        from mcp_store.tools.crypto import decrypt_tool
        
        # Test with empty string
        result = await decrypt_tool("")
        self.assertFalse(result["success"])
        self.assertIsNotNone(result["error"])
        self.assertIn("cannot be empty", result["error"])
        
        # Test with invalid base64
        result = await decrypt_tool("Not!Valid@Base64")
        self.assertFalse(result["success"])
        self.assertIsNotNone(result["error"])
        self.assertIn("Invalid base64", result["error"])
    
    @pytest.mark.asyncio
    async def test_round_trip(self):
        """Test encryption followed by decryption returns the original text."""
        from mcp_store.tools.crypto import encrypt_tool, decrypt_tool
        
        original_texts = [
            "Simple text",
            "Text with numbers 123456",
            "Text with special characters !@#$%^&*()",
            "Unicode text: こんにちは, 你好, 안녕하세요",
            "A" * 1000  # Test with longer text
        ]
        
        for text in original_texts:
            # Encrypt
            encrypt_result = await encrypt_tool(text)
            self.assertTrue(encrypt_result["success"])
            
            # Decrypt
            encrypted_text = encrypt_result["encrypted_text"]
            decrypt_result = await decrypt_tool(encrypted_text)
            self.assertTrue(decrypt_result["success"])
            
            # Compare
            self.assertEqual(decrypt_result["decrypted_text"], text)
    
    @pytest.mark.asyncio
    async def test_encrypt_with_invalid_input(self):
        """Test encryption with invalid input types."""
        from mcp_store.tools.crypto import encrypt_tool
        
        # Test with None input - Note: in actual use, a type error would happen before
        # reaching the function, but we're testing the function's error handling
        with self.assertRaises(TypeError):
            await encrypt_tool(None)  # type: ignore
    
    @pytest.mark.asyncio
    async def test_decrypt_with_invalid_input(self):
        """Test decryption with invalid input types."""
        from mcp_store.tools.crypto import decrypt_tool
        
        # Test with None input - Note: in actual use, a type error would happen before
        # reaching the function, but we're testing the function's error handling
        with self.assertRaises(TypeError):
            await decrypt_tool(None)  # type: ignore


async def test_crypto_functions():
    """Run tests for crypto tools directly."""
    print("Testing Crypto Functions")
    print("=" * 40)
    
    try:
        from mcp_store.tools.crypto import encrypt_tool, decrypt_tool
        
        # Test encryption
        print("\n1. Testing Encryption:")
        result = await encrypt_tool("Hello, World!")
        print(f"encrypt_tool('Hello, World!') = {result}")
        
        # Test decryption
        print("\n2. Testing Decryption:")
        encrypted_text = result["encrypted_text"]
        result = await decrypt_tool(encrypted_text)
        print(f"decrypt_tool('{encrypted_text}') = {result}")
        
        # Test error cases
        print("\n3. Testing Error Cases:")
        result = await encrypt_tool("")
        print(f"encrypt_tool('') = {result}")
        
        result = await decrypt_tool("")
        print(f"decrypt_tool('') = {result}")
        
        result = await decrypt_tool("InvalidBase64!@#")
        print(f"decrypt_tool('InvalidBase64!@#') = {result}")
        
        print("\n" + "=" * 40)
        print("All tests completed!")
        return True
        
    except Exception as e:
        print(f"Error during tests: {e}")
        import traceback
        traceback.print_exc()
        return False


# To run this test file directly
if __name__ == "__main__":
    asyncio.run(test_crypto_functions())