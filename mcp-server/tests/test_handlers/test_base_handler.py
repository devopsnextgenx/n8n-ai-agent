"""Tests for base handler functionality."""

import pytest

from n8n_mcp_server.handlers.base_handler import BaseHandler


class TestHandler(BaseHandler):
    """Test implementation of BaseHandler."""
    
    async def handle(self, request):
        """Test handle implementation."""
        return self.create_success_response(
            data={"processed": request.get("data", "")},
            message="Test handler completed"
        )


class TestBaseHandler:
    """Test cases for BaseHandler class."""
    
    def test_handler_initialization(self):
        """Test handler initialization."""
        handler = TestHandler("test_handler")
        assert handler.name == "test_handler"
        assert handler.logger is not None
    
    @pytest.mark.asyncio
    async def test_successful_handle(self):
        """Test successful request handling."""
        handler = TestHandler("test_handler")
        request = {"data": "test_data"}
        
        result = await handler.handle(request)
        
        assert result["success"] is True
        assert result["data"]["processed"] == "test_data"
        assert "message" in result
    
    def test_validate_request_success(self):
        """Test successful request validation."""
        handler = TestHandler("test_handler")
        request = {"field1": "value1", "field2": "value2"}
        required_fields = ["field1", "field2"]
        
        error = handler.validate_request(request, required_fields)
        
        assert error is None
    
    def test_validate_request_missing_field(self):
        """Test request validation with missing field."""
        handler = TestHandler("test_handler")
        request = {"field1": "value1"}
        required_fields = ["field1", "field2"]
        
        error = handler.validate_request(request, required_fields)
        
        assert error is not None
        assert "field2" in error
    
    def test_create_success_response(self):
        """Test success response creation."""
        handler = TestHandler("test_handler")
        data = {"result": "success"}
        message = "Operation completed"
        
        response = handler.create_success_response(data, message)
        
        assert response["success"] is True
        assert response["data"] == data
        assert response["message"] == message
    
    def test_create_error_response(self):
        """Test error response creation."""
        handler = TestHandler("test_handler")
        error = "Something went wrong"
        message = "Operation failed"
        
        response = handler.create_error_response(error, message)
        
        assert response["success"] is False
        assert response["error"] == error
        assert response["message"] == message
    
    @pytest.mark.asyncio
    async def test_safe_handle_success(self):
        """Test safe handle with successful operation."""
        handler = TestHandler("test_handler")
        request = {"data": "test_data"}
        
        result = await handler.safe_handle(request)
        
        assert result["success"] is True
        assert result["data"]["processed"] == "test_data"
    
    @pytest.mark.asyncio
    async def test_safe_handle_exception(self):
        """Test safe handle with exception."""
        class FailingHandler(BaseHandler):
            async def handle(self, request):
                raise ValueError("Test error")
        
        handler = FailingHandler("failing_handler")
        request = {"data": "test_data"}
        
        result = await handler.safe_handle(request)
        
        assert result["success"] is False
        assert "Test error" in result["error"]
        assert "failing_handler" in result["message"]