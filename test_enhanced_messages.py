"""
Test script for enhanced Teams message features
Run this to test all the new message types with your Teams webhook
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5000"
API_KEY = "langflow-teams-secret-123456"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}


def test_simple_message():
    """Test 1: Simple text message (original functionality)"""
    print("\n" + "="*70)
    print("TEST 1: Simple Text Message")
    print("="*70)

    payload = {
        "name": "send_teams_message",
        "arguments": {
            "message": "Hello from the updated MCP server! 👋"
        }
    }

    response = requests.post(
        f"{BASE_URL}/mcp/tools/call",
        json=payload,
        headers=headers
    )

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code in [200, 202]


def test_adaptive_card_basic():
    """Test 2: Basic Adaptive Card with title and message"""
    print("\n" + "="*70)
    print("TEST 2: Basic Adaptive Card")
    print("="*70)

    payload = {
        "name": "send_adaptive_card",
        "arguments": {
            "title": "System Alert",
            "message": "Your application is running smoothly. All services are operational.",
            "priority": "normal"
        }
    }

    response = requests.post(
        f"{BASE_URL}/mcp/tools/call",
        json=payload,
        headers=headers
    )

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code in [200, 202]


def test_adaptive_card_with_priority():
    """Test 3: Adaptive Card with different priorities"""
    print("\n" + "="*70)
    print("TEST 3: Adaptive Cards with Different Priorities")
    print("="*70)

    priorities = ["urgent", "high", "normal", "low"]

    for priority in priorities:
        print(f"\nTesting priority: {priority}")

        payload = {
            "name": "send_adaptive_card",
            "arguments": {
                "title": f"{priority.upper()} Priority Alert",
                "message": f"This is a {priority} priority message to demonstrate color coding.",
                "priority": priority
            }
        }

        response = requests.post(
            f"{BASE_URL}/mcp/tools/call",
            json=payload,
            headers=headers
        )

        print(f"Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Error: {response.text}")

        time.sleep(2)  # Wait 2 seconds between messages

    return True


def test_adaptive_card_with_facts():
    """Test 4: Adaptive Card with facts (metadata)"""
    print("\n" + "="*70)
    print("TEST 4: Adaptive Card with Facts")
    print("="*70)

    payload = {
        "name": "send_adaptive_card",
        "arguments": {
            "title": "Deployment Status",
            "message": "Your application has been successfully deployed to production.",
            "priority": "high",
            "facts": {
                "Environment": "Production",
                "Version": "v2.5.1",
                "Status": "Running",
                "Uptime": "99.9%",
                "Last Deploy": "2025-11-19 10:30:00"
            },
            "sender": "CI/CD Pipeline"
        }
    }

    response = requests.post(
        f"{BASE_URL}/mcp/tools/call",
        json=payload,
        headers=headers
    )

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code in [200, 202]


def test_adaptive_card_with_image():
    """Test 5: Adaptive Card with image"""
    print("\n" + "="*70)
    print("TEST 5: Adaptive Card with Image")
    print("="*70)

    payload = {
        "name": "send_adaptive_card",
        "arguments": {
            "title": "Performance Report",
            "message": "Your system performance metrics for the last 24 hours.",
            "priority": "normal",
            "image_url": "https://via.placeholder.com/600x300.png?text=Performance+Chart",
            "facts": {
                "CPU Usage": "45%",
                "Memory": "2.3 GB / 8 GB",
                "Requests": "12,453"
            },
            "sender": "Monitoring System"
        }
    }

    response = requests.post(
        f"{BASE_URL}/mcp/tools/call",
        json=payload,
        headers=headers
    )

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code in [200, 202]


def test_notification_basic():
    """Test 6: Basic notification without action button"""
    print("\n" + "="*70)
    print("TEST 6: Basic Notification")
    print("="*70)

    payload = {
        "name": "send_notification",
        "arguments": {
            "title": "Build Complete",
            "message": "Your build #1234 has completed successfully.",
            "priority": "normal"
        }
    }

    response = requests.post(
        f"{BASE_URL}/mcp/tools/call",
        json=payload,
        headers=headers
    )

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code in [200, 202]


def test_notification_with_action():
    """Test 7: Notification with action button"""
    print("\n" + "="*70)
    print("TEST 7: Notification with Action Button")
    print("="*70)

    payload = {
        "name": "send_notification",
        "arguments": {
            "title": "Pull Request Ready for Review",
            "message": "PR #456: Add new authentication feature is ready for review.",
            "priority": "high",
            "action_url": "https://github.com/yourrepo/pull/456",
            "action_text": "Review Pull Request"
        }
    }

    response = requests.post(
        f"{BASE_URL}/mcp/tools/call",
        json=payload,
        headers=headers
    )

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code in [200, 202]


def test_real_world_scenarios():
    """Test 8: Real-world scenario examples"""
    print("\n" + "="*70)
    print("TEST 8: Real-World Scenarios")
    print("="*70)

    scenarios = [
        {
            "name": "Error Alert",
            "payload": {
                "name": "send_adaptive_card",
                "arguments": {
                    "title": "🔴 Critical Error Detected",
                    "message": "Database connection pool exhausted. Immediate attention required.",
                    "priority": "urgent",
                    "facts": {
                        "Error Code": "DB_CONN_POOL_EXHAUSTED",
                        "Service": "API Gateway",
                        "Affected Users": "~500",
                        "Started": "2025-11-19 14:35:22"
                    },
                    "sender": "Error Monitoring System"
                }
            }
        },
        {
            "name": "Success Notification",
            "payload": {
                "name": "send_notification",
                "arguments": {
                    "title": "✅ Daily Backup Completed",
                    "message": "All databases have been successfully backed up.",
                    "priority": "low",
                    "action_url": "https://backup-dashboard.example.com",
                    "action_text": "View Backup Report"
                }
            }
        },
        {
            "name": "Status Update",
            "payload": {
                "name": "send_adaptive_card",
                "arguments": {
                    "title": "Weekly Summary Report",
                    "message": "Here's your weekly performance summary.",
                    "priority": "normal",
                    "facts": {
                        "Total Users": "1,234",
                        "New Signups": "+87",
                        "Active Sessions": "456",
                        "Revenue": "$12,345",
                        "Week": "Nov 12-19, 2025"
                    },
                    "sender": "Analytics Dashboard"
                }
            }
        }
    ]

    for scenario in scenarios:
        print(f"\n  → {scenario['name']}")
        response = requests.post(
            f"{BASE_URL}/mcp/tools/call",
            json=scenario['payload'],
            headers=headers
        )
        print(f"     Status: {response.status_code}")
        time.sleep(2)

    return True


def main():
    """Run all tests"""
    print("="*70)
    print("TESTING ENHANCED TEAMS MESSAGES")
    print("="*70)
    print(f"Base URL: {BASE_URL}")
    print(f"API Key: {API_KEY[:20]}...")

    # Check if server is running
    try:
        health = requests.get(f"{BASE_URL}/health")
        print(f"\n✓ Server is running (v{health.json().get('version', 'unknown')})")
    except Exception as e:
        print(f"\n✗ ERROR: Cannot connect to server at {BASE_URL}")
        print(f"  Make sure the server is running: python mcp_server_langflow.py")
        return

    # Run tests
    tests = [
        ("Simple Message", test_simple_message),
        ("Basic Adaptive Card", test_adaptive_card_basic),
        ("Priority Levels", test_adaptive_card_with_priority),
        ("Card with Facts", test_adaptive_card_with_facts),
        ("Card with Image", test_adaptive_card_with_image),
        ("Basic Notification", test_notification_basic),
        ("Notification with Action", test_notification_with_action),
        ("Real-World Scenarios", test_real_world_scenarios)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, "✓ PASS" if success else "✗ FAIL"))
            time.sleep(3)  # Wait between tests
        except Exception as e:
            results.append((test_name, f"✗ ERROR: {str(e)}"))
            print(f"ERROR: {str(e)}")

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    for test_name, result in results:
        print(f"{result:12} {test_name}")

    print("\n" + "="*70)
    print("Check your Microsoft Teams channel to see all the messages!")
    print("="*70)


if __name__ == "__main__":
    main()
