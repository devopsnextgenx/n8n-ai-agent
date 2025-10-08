#!/usr/bin/env python3
"""
Live test of MCP server endpoints using HTTP requests.
This tests the actual running server to verify tools are working.
"""

import requests
import json
import sys
from typing import Dict, Any


def test_mcp_server_http():
    """Test MCP server using direct HTTP calls."""
    base_url = "http://localhost:6789"
    
    print("🧪 Testing Live MCP Server")
    print("=" * 50)
    
    # Test if server is responding
    try:
        print("1. Testing server connectivity...")
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Response: {response.text}")
        else:
            print("   ✅ Server responding")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Server connection failed: {e}")
        return False
    
    # Test MCP endpoint with proper session handling
    print("\n2. Testing MCP protocol...")
    
    # Try to initialize MCP session
    try:
        mcp_url = f"{base_url}/mcp"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        
        # Initialize request
        init_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "python-test",
                    "version": "1.0"
                }
            }
        }
        
        print("   Initializing MCP session...")
        response = requests.post(mcp_url, json=init_payload, headers=headers, timeout=10)
        print(f"   Init Status: {response.status_code}")
        print(f"   Init Response: {response.text[:200]}...")
        
        if "server-error" in response.text:
            print("   ❌ MCP initialization failed")
            return False
        
        print("   ✅ MCP session initialized")
        
    except requests.exceptions.RequestException as e:
        print(f"   ❌ MCP initialization failed: {e}")
        return False
    
    # Test if there are alternative endpoints
    print("\n3. Testing alternative endpoints...")
    
    # Check for API documentation
    endpoints_to_try = [
        "/docs",
        "/redoc", 
        "/openapi.json",
        "/health",
        "/tools",
        "/resources"
    ]
    
    working_endpoints = []
    
    for endpoint in endpoints_to_try:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                working_endpoints.append(endpoint)
                print(f"   ✅ {endpoint} - Available")
            else:
                print(f"   ❌ {endpoint} - Status {response.status_code}")
        except:
            print(f"   ❌ {endpoint} - Failed")
    
    if working_endpoints:
        print(f"\n   Found {len(working_endpoints)} working endpoints!")
        
        # Test the /tools endpoint if available
        if "/tools" in working_endpoints:
            print("\n4. Testing /tools endpoint...")
            try:
                response = requests.get(f"{base_url}/tools", timeout=5)
                print(f"   Tools response: {response.text[:500]}")
            except Exception as e:
                print(f"   Tools test failed: {e}")
    
    return len(working_endpoints) > 0


def test_direct_tool_calls():
    """Test direct tool calls if standard endpoints are available."""
    base_url = "http://localhost:6789"
    
    print("\n🔧 Testing Direct Tool Calls")
    print("=" * 50)
    
    # Test calculator add tool directly
    try:
        print("1. Testing ADD tool...")
        
        # Try different possible endpoints
        endpoints_to_try = [
            "/tools/add",
            "/api/tools/add",
            "/mcp/tools/add"
        ]
        
        payload = {"a": 15, "b": 25}
        
        for endpoint in endpoints_to_try:
            try:
                response = requests.post(
                    f"{base_url}{endpoint}", 
                    json=payload, 
                    timeout=10,
                    headers={"Content-Type": "application/json"}
                )
                
                print(f"   Endpoint: {endpoint}")
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   Response: {json.dumps(data, indent=2)}")
                    
                    if data.get("success") and data.get("result") == 40:
                        print("   ✅ ADD tool working correctly!")
                        print(f"   ✅ 15 + 25 = {data.get('result')}")
                        return True
                    else:
                        print("   ⚠️  ADD tool responded but result unexpected")
                        
                elif response.status_code == 404:
                    print("   ❌ Endpoint not found")
                else:
                    print(f"   ❌ Error: {response.text[:200]}")
                    
            except requests.exceptions.RequestException as e:
                print(f"   ❌ Request failed: {e}")
        
        return False
        
    except Exception as e:
        print(f"❌ Tool testing failed: {e}")
        return False


def main():
    """Main test function."""
    print("🚀 MCP Server Live Testing")
    print("=" * 60)
    print("Testing server running on http://localhost:6789")
    print("=" * 60)
    
    # Test 1: Basic HTTP connectivity
    http_ok = test_mcp_server_http()
    
    # Test 2: Direct tool calls
    tools_ok = test_direct_tool_calls()
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"HTTP Connectivity: {'✅ PASS' if http_ok else '❌ FAIL'}")
    print(f"Tool Functionality: {'✅ PASS' if tools_ok else '❌ FAIL'}")
    
    if http_ok and tools_ok:
        print("\n🎉 MCP Server is working correctly!")
        print("✅ All tests passed")
    elif http_ok:
        print("\n⚠️  Server is running but tools may need different endpoints")
        print("💡 Check server logs for more details")
    else:
        print("\n❌ Server connectivity issues detected")
        print("💡 Make sure the server is running on port 6789")
    
    print("=" * 60)
    
    return http_ok and tools_ok


if __name__ == "__main__":
    main()