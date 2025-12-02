"""
Simple test script to send messages to Teams via Power Automate
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

TEAMS_WEBHOOK_URL = os.getenv("TEAMS_WEBHOOK_URL")

def test_simple_text():
    """Test sending simple text message"""
    print("=" * 70)
    print("TEST 1: Simple Text Message")
    print("=" * 70)

    payload = {
        "text": "Hello from simple test script!"
    }

    print(f"Sending to: {TEAMS_WEBHOOK_URL[:80]}...")
    print(f"Payload: {payload}")

    try:
        response = requests.post(
            TEAMS_WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body: {response.text}")

        if response.status_code in [200, 202]:
            print("\nSUCCESS! Check your Teams channel.")
        else:
            print("\nFAILED!")

    except Exception as e:
        print(f"\nERROR: {e}")


def test_with_message_field():
    """Test sending with 'message' field"""
    print("\n" + "=" * 70)
    print("TEST 2: Using 'message' field")
    print("=" * 70)

    payload = {
        "message": "Hello using message field!"
    }

    print(f"Sending to: {TEAMS_WEBHOOK_URL[:80]}...")
    print(f"Payload: {payload}")

    try:
        response = requests.post(
            TEAMS_WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body: {response.text}")

        if response.status_code in [200, 202]:
            print("\nSUCCESS! Check your Teams channel.")
        else:
            print("\nFAILED!")

    except Exception as e:
        print(f"\nERROR: {e}")


def test_both_fields():
    """Test sending with both 'text' and 'message' fields"""
    print("\n" + "=" * 70)
    print("TEST 3: Using both 'text' and 'message' fields")
    print("=" * 70)

    payload = {
        "text": "This is the text field",
        "message": "This is the message field"
    }

    print(f"Sending to: {TEAMS_WEBHOOK_URL[:80]}...")
    print(f"Payload: {payload}")

    try:
        response = requests.post(
            TEAMS_WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body: {response.text}")

        if response.status_code in [200, 202]:
            print("\nSUCCESS! Check your Teams channel.")
        else:
            print("\nFAILED!")

    except Exception as e:
        print(f"\nERROR: {e}")


if __name__ == "__main__":
    if not TEAMS_WEBHOOK_URL:
        print("ERROR: TEAMS_WEBHOOK_URL not found in .env file!")
        exit(1)

    print("\nTesting Teams Webhook Integration\n")

    # Run all tests
    test_simple_text()
    test_with_message_field()
    test_both_fields()

    print("\n" + "=" * 70)
    print("All tests completed! Check your Teams channel for messages.")
    print("=" * 70)
