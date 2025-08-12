#!/usr/bin/env python3
"""
Simple test client for Cairn MCP HTTP Server
"""

import requests
import json
import time


def test_server():
    """Test the cairn HTTP server"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Cairn MCP HTTP Server...")
    
    try:
        # Test server status
        print("\n1. Testing server status...")
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Server is running")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Server status failed: {response.status_code}")
            return
        
        # Test listing tools
        print("\n2. Testing tools listing...")
        response = requests.get(f"{base_url}/tools")
        if response.status_code == 200:
            tools = response.json()["tools"]
            print(f"✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"   - {tool['name']}: {tool['description']}")
        else:
            print(f"❌ Tools listing failed: {response.status_code}")
            return
        
        # Test listing resources
        print("\n3. Testing resources listing...")
        response = requests.get(f"{base_url}/resources")
        if response.status_code == 200:
            resources = response.json()["resources"]
            print(f"✅ Found {len(resources)} resources:")
            for resource in resources:
                print(f"   - {resource['uri']}: {resource['description']}")
        else:
            print(f"❌ Resources listing failed: {response.status_code}")
            return
        
        # Test creating a path
        print("\n4. Testing path creation...")
        path_data = {
            "name": "Test Workflow Path",
            "description": "A test workflow for demonstration",
            "steps": [
                {
                    "name": "Initialize",
                    "description": "Initialize the workflow",
                    "step_type": "prompt",
                    "content": "Let's start by understanding your requirements.",
                    "context": {"step": 1},
                    "metadata": {"version": "1.0"}
                },
                {
                    "name": "Process",
                    "description": "Process the input",
                    "step_type": "tool_call",
                    "content": "Processing your request...",
                    "context": {"step": 2},
                    "metadata": {"version": "1.0"}
                }
            ],
            "tags": ["test", "workflow", "demo"],
            "branch": "main"
        }
        
        response = requests.post(
            f"{base_url}/tool",
            json={
                "name": "create_path",
                "arguments": path_data
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                path_id = result["path_id"]
                print(f"✅ Path created successfully with ID: {path_id}")
                
                # Test getting the created path
                print("\n5. Testing path retrieval...")
                response = requests.get(f"{base_url}/resource/cairn://paths/{path_id}")
                if response.status_code == 200:
                    path_info = response.json()
                    print(f"✅ Path retrieved: {path_info['name']}")
                    print(f"   Description: {path_info['description']}")
                    print(f"   Steps: {len(json.loads(path_info['content'])['steps'])}")
                else:
                    print(f"❌ Path retrieval failed: {response.status_code}")
            else:
                print(f"❌ Path creation failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ Path creation request failed: {response.status_code}")
        
        # Test searching paths
        print("\n6. Testing path search...")
        response = requests.post(
            f"{base_url}/tool",
            json={
                "name": "search_paths",
                "arguments": {
                    "query": "test",
                    "limit": 10
                }
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                paths = result["paths"]
                print(f"✅ Search successful, found {len(paths)} paths")
                for path in paths:
                    print(f"   - {path['name']} ({path['status']})")
            else:
                print(f"❌ Search failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ Search request failed: {response.status_code}")
        
        print("\n🎉 All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")


if __name__ == "__main__":
    test_server()
