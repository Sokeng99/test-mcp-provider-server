"""
Langflow Python Code: Send Response to Teams
Use this to send agent responses back to Teams
"""

import requests
import json

# Configuration
MCP_SERVER_URL = "http://localhost:5000"
API_KEY = "langflow-teams-secret-123456"

# Get the response message from your agent (or hardcode for testing)
# In a flow, this would come from your agent's output
response_message = "This is a response from Langflow! I received your message and processed it."

# Optional: get from connected component
# response_message = inputs.get('agent_response', 'Default response')

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Send response to Teams
payload = {
    "message": response_message,
    "type": "text"  # Can be "text" or "card"
}

response = requests.post(
    f"{MCP_SERVER_URL}/teams/respond",
    headers=headers,
    json=payload,
    timeout=10
)

result = response.json()

if result.get('success'):
    output = {
        "success": True,
        "message": "Response sent to Teams successfully",
        "response_text": response_message
    }
    print("Successfully sent response to Teams!")
else:
    output = {
        "success": False,
        "error": result.get('message', 'Unknown error'),
        "response_text": response_message
    }
    print(f"Failed to send response: {result.get('message')}")

print(json.dumps(output, indent=2))
