#!/usr/bin/env python3
"""Test script for server implementations with calculator tools."""

import asyncio
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


async def test_fastapi_server():
    """Test FastAPI server import and initialization."""
    print("Testing FastAPI Server Implementation")
    print("=" * 50)
    
    try:
        from fastapi_server import create_fastapi_server
        
        # Create the FastAPI server
        app = create_fastapi_server()
        
        print("✅ FastAPI server created successfully")
        print(f"   - Server type: {type(app)}")
        print(f"   - Routes count: {len(app.routes)}")
        
        # Check for calculator routes
        route_paths = [route.path for route in app.routes]
        calculator_routes = [path for path in route_paths if any(op in path for op in ['add', 'subtract', 'multiply', 'divide', 'modulo'])]
        
        print(f"   - Calculator routes found: {len(calculator_routes)}")
        for route in calculator_routes:
            print(f"     * {route}")
        
        return True
        
    except Exception as e:
        print(f"❌ FastAPI server test failed: {e}")
        return False


async def test_simple_server():
    """Test simple server import and initialization."""
    print("\nTesting Simple Server Implementation")
    print("=" * 50)
    
    try:
        from server import create_server
        
        # Create the MCP server
        mcp_server = create_server()
        
        print("✅ Simple server created successfully")
        print(f"   - Server type: {type(mcp_server)}")
        print(f"   - App type: {type(mcp_server.get_app())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Simple server test failed: {e}")
        return False


async def test_calculator_integration():
    """Test that calculator tools are properly integrated."""
    print("\nTesting Calculator Tool Integration")
    print("=" * 50)
    
    try:
        # Test direct calculator tool imports
        from mcp_store.tools.calculator import (
            add_tool, subtract_tool, multiply_tool, divide_tool, modulo_tool
        )
        
        print("✅ Calculator tools imported successfully")
        
        # Test a simple calculation
        result = await add_tool(10, 5)
        if result['success'] and result['result'] == 15:
            print("✅ Calculator tools working correctly")
            print(f"   - Sample calculation: 10 + 5 = {result['result']}")
        else:
            print(f"❌ Calculator test failed: {result}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Calculator integration test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("MCP Server Calculator Integration Tests")
    print("=" * 60)
    
    tests = [
        test_fastapi_server(),
        test_simple_server(),
        test_calculator_integration()
    ]
    
    results = await asyncio.gather(*tests, return_exceptions=True)
    
    passed = sum(1 for result in results if result is True)
    total = len(results)
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Calculator tools are properly integrated.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"   Test {i+1} exception: {result}")


if __name__ == "__main__":
    asyncio.run(main())