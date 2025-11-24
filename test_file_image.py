"""
Test script for sending files and images to Teams via MCP server
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:5000"
API_KEY = "langflow-teams-secret-123456"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}


def test_send_image():
    """Test sending an image to Teams"""
    print("\n" + "=" * 70)
    print("Testing: Send Image to Teams")
    print("=" * 70)

    # Update this path to an actual image on your computer
    image_path = r"C:\Users\Hout Sokeng\Downloads\test-image.png"

    payload = {
        "name": "send_teams_image",
        "arguments": {
            "file_path": image_path,
            "caption": "Test Image from Local Computer"
        }
    }

    print(f"Sending image: {image_path}")

    try:
        response = requests.post(
            f"{BASE_URL}/mcp/tools/call",
            headers=headers,
            json=payload,
            timeout=30
        )

        print(f"Status Code: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")

    except Exception as e:
        print(f"Error: {str(e)}")


def test_send_file():
    """Test sending a file info to Teams"""
    print("\n" + "=" * 70)
    print("Testing: Send File to Teams")
    print("=" * 70)

    # Update this path to an actual file on your computer
    file_path = r"C:\Users\Hout Sokeng\Downloads\test-mcp 1\test-mcp\README.md"

    payload = {
        "name": "send_teams_file",
        "arguments": {
            "file_path": file_path,
            "description": "This is a test file from my local computer"
        }
    }

    print(f"Sending file: {file_path}")

    try:
        response = requests.post(
            f"{BASE_URL}/mcp/tools/call",
            headers=headers,
            json=payload,
            timeout=30
        )

        print(f"Status Code: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")

    except Exception as e:
        print(f"Error: {str(e)}")


def test_list_tools():
    """List all available tools"""
    print("\n" + "=" * 70)
    print("Testing: List Available Tools")
    print("=" * 70)

    try:
        response = requests.post(
            f"{BASE_URL}/mcp/tools/list",
            headers=headers,
            timeout=10
        )

        print(f"Status Code: {response.status_code}")
        print(f"Available Tools:")

        tools = response.json().get("tools", [])
        for i, tool in enumerate(tools, 1):
            print(f"\n{i}. {tool['name']}")
            print(f"   Description: {tool['description']}")
            print(f"   Required params: {tool['inputSchema'].get('required', [])}")

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    print("=" * 70)
    print("MCP Teams Webhook - File & Image Testing")
    print("=" * 70)
    print("\nMake sure the MCP server is running on http://localhost:5000")
    print("Update the file paths in this script to test with your own files")

    # Test listing tools
    test_list_tools()

    # Test with the README file (should work since it exists)
    test_send_file()

    # Uncomment this test when you have a valid image file
    # test_send_image()

    print("\n" + "=" * 70)
    print("Testing Complete!")
    print("=" * 70)
