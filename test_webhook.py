"""
Test script to verify Teams webhook is working
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

TEAMS_WEBHOOK_URL = os.getenv("TEAMS_WEBHOOK_URL")
MCP_API_KEY = os.getenv("MCP_API_KEY")

def test_direct_webhook():
    """Test sending directly to Teams webhook"""
    print("Testing direct Teams webhook...")

    payload = {
        "text": "🧪 Direct webhook test",
        "message": "🧪 Direct webhook test",
        "content": "🧪 Direct webhook test"
    }

    try:
        response = requests.post(
            TEAMS_WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        if response.status_code in [200, 202]:
            print("✅ Direct webhook test PASSED")
            print(f"   Status: {response.status_code}")
            return True
        else:
            print(f"❌ Direct webhook test FAILED")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_mcp_server():
    """Test sending via MCP server"""
    print("\nTesting MCP server...")

    url = "http://localhost:5000/test"
    headers = {
        "Authorization": f"Bearer {MCP_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"message": "🧪 MCP server test"}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)

        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ MCP server test PASSED")
                print(f"   Status: {response.status_code}")
                return True
            else:
                print("❌ MCP server test FAILED")
                print(f"   Result: {result}")
                return False
        else:
            print(f"❌ MCP server test FAILED")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to MCP server")
        print("   Make sure the server is running: python mcp_server_langflow.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_mcp_endpoints():
    """Test all MCP endpoints"""
    print("\nTesting MCP endpoints...")

    tests = [
        ("GET", "http://localhost:5000/health", None, False),
        ("GET", "http://localhost:5000/mcp/info", None, False),
        ("GET", "http://localhost:5000/mcp/tools/list", None, True),
    ]

    passed = 0
    failed = 0

    for method, url, payload, needs_auth in tests:
        endpoint_name = url.split('/')[-1] or url.split('/')[-2]

        headers = {}
        if needs_auth:
            headers["Authorization"] = f"Bearer {MCP_API_KEY}"

        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=5)
            else:
                response = requests.post(url, json=payload, headers=headers, timeout=5)

            if response.status_code == 200:
                print(f"   ✅ {endpoint_name}")
                passed += 1
            else:
                print(f"   ❌ {endpoint_name} - Status {response.status_code}")
                failed += 1
        except Exception as e:
            print(f"   ❌ {endpoint_name} - {str(e)}")
            failed += 1

    print(f"\n   Passed: {passed}/{passed+failed}")
    return failed == 0


if __name__ == "__main__":
    print("=" * 60)
    print("MCP Teams Webhook Test Suite")
    print("=" * 60)

    results = []

    # Test 1: Direct webhook
    results.append(("Direct Webhook", test_direct_webhook()))

    # Test 2: MCP endpoints
    results.append(("MCP Endpoints", test_mcp_endpoints()))

    # Test 3: MCP server
    results.append(("MCP Server", test_mcp_server()))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name:20} {status}")

    all_passed = all(result[1] for result in results)

    print("=" * 60)
    if all_passed:
        print("🎉 All tests passed! Check your Teams channel for messages.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    print("=" * 60)
