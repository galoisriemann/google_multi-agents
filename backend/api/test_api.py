#!/usr/bin/env python3
"""Simple test script for the Flexible Agent Workflow API.

This script tests the basic functionality of the API endpoints
to ensure everything is working correctly.
"""

import asyncio
import json
import time
from typing import Dict, Any
import httpx

API_BASE_URL = "http://localhost:8000"


async def test_health_check() -> bool:
    """Test the health check endpoint."""
    print("🔍 Testing health check endpoint...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/api/v1/health")
            
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False


async def test_workflow_config() -> bool:
    """Test the workflow configuration endpoint."""
    print("\n🔍 Testing workflow configuration endpoint...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/api/v1/workflow/config")
            
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Configuration loaded:")
            print(f"   - Name: {data.get('name')}")
            print(f"   - Version: {data.get('version')}")
            print(f"   - Agents: {len(data.get('agents', []))}")
            print(f"   - Tools: {len(data.get('available_tools', []))}")
            return True
        else:
            print(f"❌ Configuration test failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Configuration test error: {e}")
        return False


async def test_tools_endpoint() -> bool:
    """Test the tools endpoint."""
    print("\n🔍 Testing tools endpoint...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/api/v1/tools")
            
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Tools loaded: {len(data)} tools available")
            for tool in data[:3]:  # Show first 3 tools
                print(f"   - {tool.get('name')}: {tool.get('description')}")
            if len(data) > 3:
                print(f"   ... and {len(data) - 3} more tools")
            return True
        else:
            print(f"❌ Tools test failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Tools test error: {e}")
        return False


async def test_workflow_execution() -> bool:
    """Test workflow execution (basic test without waiting for completion)."""
    print("\n🔍 Testing workflow execution endpoint...")
    
    try:
        workflow_request = {
            "user_request": "Create a simple test report for API testing"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{API_BASE_URL}/api/v1/workflow/execute",
                json=workflow_request
            )
            
        if response.status_code == 200:
            data = response.json()
            workflow_id = data.get('id')
            print(f"✅ Workflow started successfully:")
            print(f"   - ID: {workflow_id}")
            print(f"   - Status: {data.get('status')}")
            
            # Test status endpoint
            await asyncio.sleep(1)  # Wait a moment
            
            async with httpx.AsyncClient() as client:
                status_response = await client.get(f"{API_BASE_URL}/api/v1/workflow/status/{workflow_id}")
                
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"✅ Status check successful:")
                print(f"   - Status: {status_data.get('status')}")
                print(f"   - Progress: {status_data.get('progress')}%")
                print(f"   - Current Agent: {status_data.get('current_agent')}")
            else:
                print(f"⚠️ Status check failed: {status_response.status_code}")
            
            return True
        else:
            print(f"❌ Workflow execution failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Workflow execution error: {e}")
        return False


async def test_list_workflows() -> bool:
    """Test the list workflows endpoint."""
    print("\n🔍 Testing list workflows endpoint...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/api/v1/workflows")
            
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Workflows listed: {data.get('total')} total workflows")
            
            workflows = data.get('workflows', [])
            for i, workflow in enumerate(workflows[:3], 1):  # Show first 3
                print(f"   {i}. ID: {workflow.get('id', 'N/A')[:8]}... Status: {workflow.get('status')}")
            
            if len(workflows) > 3:
                print(f"   ... and {len(workflows) - 3} more workflows")
            
            return True
        else:
            print(f"❌ List workflows failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ List workflows error: {e}")
        return False


async def main():
    """Run all API tests."""
    print("🚀 Starting Flexible Agent Workflow API Tests")
    print("="*60)
    
    # Check if server is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/")
        print(f"✅ API server is running at {API_BASE_URL}")
    except Exception as e:
        print(f"❌ Cannot connect to API server at {API_BASE_URL}")
        print(f"   Please make sure the server is running: python backend/api/start_server.py")
        return
    
    # Run tests
    tests = [
        ("Health Check", test_health_check),
        ("Workflow Configuration", test_workflow_config),
        ("Tools Endpoint", test_tools_endpoint),
        ("List Workflows", test_list_workflows),
        ("Workflow Execution", test_workflow_execution),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
    
    print("\n" + "="*60)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! API is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main()) 