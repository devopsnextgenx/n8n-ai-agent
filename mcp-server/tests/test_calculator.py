#!/usr/bin/env python3
"""Test script for calculator tools."""

import asyncio
import sys
from pathlib import Path

# Add src directory to path for absolute imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from mcp_store.tools.calculator import (
    add_tool, subtract_tool, multiply_tool, divide_tool, modulo_tool
)


async def test_calculator_functions():
    """Test all calculator functions."""
    print("Testing Calculator Functions")
    print("=" * 40)
    
    # Test addition
    print("\n1. Testing Addition:")
    result = await add_tool(10, 5)
    print(f"add_tool(10, 5) = {result}")
    
    result = await add_tool(3.5, 2.7)
    print(f"add_tool(3.5, 2.7) = {result}")
    
    # Test subtraction
    print("\n2. Testing Subtraction:")
    result = await subtract_tool(10, 5)
    print(f"subtract_tool(10, 5) = {result}")
    
    result = await subtract_tool(3.5, 2.7)
    print(f"subtract_tool(3.5, 2.7) = {result}")
    
    # Test multiplication
    print("\n3. Testing Multiplication:")
    result = await multiply_tool(10, 5)
    print(f"multiply_tool(10, 5) = {result}")
    
    result = await multiply_tool(3.5, 2.0)
    print(f"multiply_tool(3.5, 2.0) = {result}")
    
    # Test division
    print("\n4. Testing Division:")
    result = await divide_tool(10, 5)
    print(f"divide_tool(10, 5) = {result}")
    
    result = await divide_tool(7, 2)
    print(f"divide_tool(7, 2) = {result}")
    
    # Test division by zero
    print("\n5. Testing Division by Zero (Error Case):")
    result = await divide_tool(10, 0)
    print(f"divide_tool(10, 0) = {result}")
    
    # Test modulo
    print("\n6. Testing Modulo:")
    result = await modulo_tool(10, 3)
    print(f"modulo_tool(10, 3) = {result}")
    
    result = await modulo_tool(15, 4)
    print(f"modulo_tool(15, 4) = {result}")
    
    # Test modulo by zero
    print("\n7. Testing Modulo by Zero (Error Case):")
    result = await modulo_tool(10, 0)
    print(f"modulo_tool(10, 0) = {result}")
    
    # Test invalid inputs
    print("\n8. Testing Invalid Inputs (Error Cases):")
    result = await add_tool("invalid", 5)
    print(f"add_tool('invalid', 5) = {result}")
    
    result = await multiply_tool(None, 5)
    print(f"multiply_tool(None, 5) = {result}")
    
    print("\n" + "=" * 40)
    print("All tests completed!")


if __name__ == "__main__":
    asyncio.run(test_calculator_functions())