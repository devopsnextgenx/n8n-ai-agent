"""Test configuration and fixtures."""

import pytest
from fastmcp import FastMCP

from n8n_mcp_server.main import create_mcp_server
from n8n_mcp_server.config import get_settings


@pytest.fixture
def mcp_server():
    """Create MCP server instance for testing."""
    return create_mcp_server()


@pytest.fixture
def settings():
    """Get application settings for testing."""
    return get_settings()


@pytest.fixture
def sample_text_data():
    """Sample text data for testing."""
    return "Hello, World! This is test data."


@pytest.fixture
def sample_base64_data():
    """Sample base64 encoded data for testing."""
    return "SGVsbG8sIFdvcmxkISBUaGlzIGlzIHRlc3QgZGF0YS4="


@pytest.fixture
def sample_binary_data():
    """Sample binary data for testing."""
    return b"\\x00\\x01\\x02\\x03\\xFF\\xFE\\xFD"