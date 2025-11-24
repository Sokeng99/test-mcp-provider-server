"""
Langflow Python Code: Poll for Messages from Teams
Use this to check for new messages from Teams that need responses
"""

import requests
import json

# Configuration
MCP_SERVER_URL = "http://localhost:5000"
API_KEY = "langflow-teams-secret-123456"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Poll for new messages
response = requests.get(
    f"{MCP_SERVER_URL}/teams/poll",
    headers=headers,
    timeout=10
)

result = response.json()

if result.get('count', 0) > 0:
    messages = result.get('messages', [])

    # Output the messages for processing
    output = {
        "has_messages": True,
        "count": len(messages),
        "messages": messages,
        "latest_message": messages[-1] if messages else None
    }

    # Print for debugging
    print(f"Received {len(messages)} new messages from Teams:")
    for msg in messages:
        print(f"  - From {msg['user']}: {msg['text']}")

else:
    output = {
        "has_messages": False,
        "count": 0,
        "messages": [],
        "latest_message": None
    }
    print("No new messages from Teams")

# Return the output (this can be connected to other components)
print(json.dumps(output, indent=2))
