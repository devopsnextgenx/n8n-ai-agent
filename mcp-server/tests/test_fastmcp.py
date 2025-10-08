"""
Comprehensive tests for FastAPI MCP Server endpoints.

This test suite verifies that all MCP resources and tools are working correctly
through HTTP endpoints when running in streamable mode.
"""

import sys
import pytest
import asyncio
import json
from pathlib import Path
from typing import Dict, Any
from httpx import AsyncClient
from fastapi.testclient import TestClient

# Add src to path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from src.fastapi_server import create_fastapi_server


class TestFastAPIMCPServer:
    """Test class for FastAPI MCP Server endpoints."""
    
    @pytest.fixture
    def app(self):
        """Create FastAPI app for testing."""
        return create_fastapi_server()
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    async def async_client(self, app):
        """Create async test client."""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    
    # Test General Endpoints
    
    def test_root_endpoint(self, client):
        """Test the root endpoint returns server information."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "MCP Crypto Server"
        assert data["status"] == "running"
        assert data["version"] == "0.1.0"
        assert "tools" in data
        assert "resources" in data
        assert "endpoints" in data
        
        # Verify expected tools are listed
        expected_tools = ["encrypt", "decrypt", "add", "subtract", "multiply", "divide", "modulo"]
        assert all(tool in data["tools"] for tool in expected_tools)
        
        # Verify expected resources are listed
        expected_resources = ["version", "status", "tools_list"]
        assert all(resource in data["resources"] for resource in expected_resources)
    
    def test_health_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["server"] == "MCP Crypto Server"
    
    # Test Resource Endpoints
    
    def test_version_resource(self, client):
        """Test the version resource endpoint."""
        response = client.get("/resources/version")
        assert response.status_code == 200
        
        data = response.json()
        assert data["server_name"] == "MCP Crypto Server"
        assert data["server_version"] == "0.1.0"
        assert data["mcp_version"] == "1.0"
        assert "capabilities" in data
        assert "tools" in data["capabilities"]
        assert "resources" in data["capabilities"]
    
    def test_status_resource(self, client):
        """Test the status resource endpoint."""
        response = client.get("/resources/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "running"
        assert "timestamp" in data
        assert "uptime_seconds" in data
        assert "uptime_formatted" in data
        assert "process_id" in data
        assert "tools_available" in data
        assert "resources_available" in data
    
    def test_tools_list_resource(self, client):
        """Test the tools list resource endpoint."""
        response = client.get("/resources/tools")
        assert response.status_code == 200
        
        data = response.json()
        assert "tools" in data
        assert data["total_tools"] == 7
        assert "categories" in data
        
        # Verify all expected tools are documented
        tool_names = [tool["name"] for tool in data["tools"]]
        expected_tools = ["encrypt", "decrypt", "add", "subtract", "multiply", "divide", "modulo"]
        assert all(tool in tool_names for tool in expected_tools)
        
        # Verify tool structure
        for tool in data["tools"]:
            assert "name" in tool
            assert "description" in tool
            assert "parameters" in tool
            assert "returns" in tool
            assert "examples" in tool
    
    # Test Crypto Tool Endpoints
    
    def test_encrypt_tool_success(self, client):
        """Test successful encryption."""
        payload = {"text": "Hello, World!"}
        response = client.post("/tools/encrypt", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["error"] is None
        assert "encrypted_text" in data
        assert data["encrypted_text"] == "SGVsbG8sIFdvcmxkIQ=="
        assert data["original_length"] == 13
        assert data["encoded_length"] == 20
    
    def test_encrypt_tool_empty_text(self, client):
        """Test encryption with empty text."""
        payload = {"text": ""}
        response = client.post("/tools/encrypt", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is False
        assert "Input text cannot be empty" in data["error"]
        assert data["encrypted_text"] is None
    
    def test_decrypt_tool_success(self, client):
        """Test successful decryption."""
        payload = {"encoded_text": "SGVsbG8sIFdvcmxkIQ=="}
        response = client.post("/tools/decrypt", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["error"] is None
        assert data["decrypted_text"] == "Hello, World!"
        assert data["encoded_length"] == 20
        assert data["decoded_length"] == 13
    
    def test_decrypt_tool_invalid_base64(self, client):
        """Test decryption with invalid base64."""
        payload = {"encoded_text": "invalid_base64!"}
        response = client.post("/tools/decrypt", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is False
        assert "Invalid base64 format" in data["error"]
        assert data["decrypted_text"] is None
    
    def test_decrypt_tool_empty_text(self, client):
        """Test decryption with empty text."""
        payload = {"encoded_text": ""}
        response = client.post("/tools/decrypt", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is False
        assert "Input encoded text cannot be empty" in data["error"]
        assert data["decrypted_text"] is None
    
    def test_encrypt_decrypt_roundtrip(self, client):
        """Test encrypt-decrypt roundtrip."""
        original_text = "This is a test message with special chars: 🚀 ñáéíóú"
        
        # Encrypt
        encrypt_payload = {"text": original_text}
        encrypt_response = client.post("/tools/encrypt", json=encrypt_payload)
        assert encrypt_response.status_code == 200
        
        encrypt_data = encrypt_response.json()
        assert encrypt_data["success"] is True
        encrypted_text = encrypt_data["encrypted_text"]
        
        # Decrypt
        decrypt_payload = {"encoded_text": encrypted_text}
        decrypt_response = client.post("/tools/decrypt", json=decrypt_payload)
        assert decrypt_response.status_code == 200
        
        decrypt_data = decrypt_response.json()
        assert decrypt_data["success"] is True
        assert decrypt_data["decrypted_text"] == original_text
    
    # Test Calculator Tool Endpoints
    
    def test_add_tool_success(self, client):
        """Test successful addition."""
        payload = {"a": 10, "b": 5}
        response = client.post("/tools/add", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["operation"] == "add"
        assert data["operand_a"] == 10
        assert data["operand_b"] == 5
        assert data["result"] == 15
        assert data["error"] is None
    
    def test_add_tool_floats(self, client):
        """Test addition with float numbers."""
        payload = {"a": 10.5, "b": 2.3}
        response = client.post("/tools/add", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["result"] == 12.8
    
    def test_subtract_tool_success(self, client):
        """Test successful subtraction."""
        payload = {"a": 10, "b": 3}
        response = client.post("/tools/subtract", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["operation"] == "subtract"
        assert data["result"] == 7
    
    def test_multiply_tool_success(self, client):
        """Test successful multiplication."""
        payload = {"a": 6, "b": 7}
        response = client.post("/tools/multiply", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["operation"] == "multiply"
        assert data["result"] == 42
    
    def test_divide_tool_success(self, client):
        """Test successful division."""
        payload = {"a": 20, "b": 4}
        response = client.post("/tools/divide", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["operation"] == "divide"
        assert data["result"] == 5
    
    def test_divide_tool_float_result(self, client):
        """Test division with float result."""
        payload = {"a": 10, "b": 3}
        response = client.post("/tools/divide", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert abs(data["result"] - 3.3333333333333335) < 1e-10  # Float precision
    
    def test_divide_tool_zero_error(self, client):
        """Test division by zero error."""
        payload = {"a": 10, "b": 0}
        response = client.post("/tools/divide", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is False
        assert "Division by zero is not allowed" in data["error"]
        assert data["result"] is None
    
    def test_modulo_tool_success(self, client):
        """Test successful modulo."""
        payload = {"a": 17, "b": 5}
        response = client.post("/tools/modulo", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["operation"] == "modulo"
        assert data["result"] == 2
    
    def test_modulo_tool_zero_error(self, client):
        """Test modulo by zero error."""
        payload = {"a": 10, "b": 0}
        response = client.post("/tools/modulo", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is False
        assert "Modulo by zero is not allowed" in data["error"]
        assert data["result"] is None
    
    # Test Error Handling
    
    def test_invalid_tool_endpoint(self, client):
        """Test calling non-existent tool endpoint."""
        response = client.post("/tools/nonexistent", json={})
        assert response.status_code == 404
    
    def test_invalid_resource_endpoint(self, client):
        """Test calling non-existent resource endpoint."""
        response = client.get("/resources/nonexistent")
        assert response.status_code == 404
    
    def test_missing_required_fields(self, client):
        """Test requests with missing required fields."""
        # Test encrypt without text
        response = client.post("/tools/encrypt", json={})
        assert response.status_code == 422  # Validation error
        
        # Test calculator without parameters
        response = client.post("/tools/add", json={})
        assert response.status_code == 422  # Validation error
        
        # Test calculator with only one parameter
        response = client.post("/tools/add", json={"a": 5})
        assert response.status_code == 422  # Validation error


# Standalone test functions for running without pytest

def test_server_standalone():
    """Test server setup without pytest."""
    print("=" * 60)
    print("FastAPI MCP Server Standalone Test")
    print("=" * 60)
    
    try:
        # Create app
        print("Creating FastAPI app...")
        app = create_fastapi_server()
        print("✅ FastAPI app created successfully")
        
        # Create test client
        print("Creating test client...")
        client = TestClient(app)
        print("✅ Test client created successfully")
        
        # Test root endpoint
        print("Testing root endpoint...")
        response = client.get("/")
        assert response.status_code == 200
        print("✅ Root endpoint working")
        
        # Test health endpoint
        print("Testing health endpoint...")
        response = client.get("/health")
        assert response.status_code == 200
        print("✅ Health endpoint working")
        
        # Test resources
        print("Testing resource endpoints...")
        for resource in ["version", "status", "tools"]:
            response = client.get(f"/resources/{resource}")
            assert response.status_code == 200
            print(f"✅ Resource '{resource}' working")
        
        # Test crypto tools
        print("Testing crypto tools...")
        encrypt_response = client.post("/tools/encrypt", json={"text": "Test"})
        assert encrypt_response.status_code == 200
        encrypted_data = encrypt_response.json()
        assert encrypted_data["success"] is True
        
        decrypt_response = client.post("/tools/decrypt", json={"encoded_text": encrypted_data["encrypted_text"]})
        assert decrypt_response.status_code == 200
        decrypted_data = decrypt_response.json()
        assert decrypted_data["success"] is True
        assert decrypted_data["decrypted_text"] == "Test"
        print("✅ Crypto tools working")
        
        # Test calculator tools
        print("Testing calculator tools...")
        calc_tests = [
            ("add", {"a": 5, "b": 3}, 8),
            ("subtract", {"a": 10, "b": 4}, 6),
            ("multiply", {"a": 6, "b": 7}, 42),
            ("divide", {"a": 20, "b": 4}, 5),
            ("modulo", {"a": 17, "b": 5}, 2)
        ]
        
        for operation, payload, expected in calc_tests:
            response = client.post(f"/tools/{operation}", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["result"] == expected
            print(f"✅ Calculator '{operation}' working")
        
        print("\n" + "=" * 60)
        print("🎉 All tests passed! MCP server is working correctly.")
        print("\nThe server supports:")
        print("  • 7 tools: encrypt, decrypt, add, subtract, multiply, divide, modulo")
        print("  • 3 resources: version, status, tools_list")
        print("  • Health checks and server info")
        print("\nYou can start the server with:")
        print("  uv run python -m src.main --dev --mode streamable")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function for standalone testing."""
    return test_server_standalone()


if __name__ == "__main__":
    main()