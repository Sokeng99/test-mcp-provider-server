"""
Complete Example: Teams Question → Langflow Agent → Teams Response

This shows a complete flow for two-way communication:
1. Poll for messages from Teams
2. Process with your agent/LLM
3. Send response back to Teams

Use this as a template in Langflow!
"""

import requests
import json
import time

# Configuration
MCP_SERVER_URL = "http://localhost:5000"
API_KEY = "langflow-teams-secret-123456"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def poll_for_messages():
    """Poll for new messages from Teams"""
    response = requests.get(
        f"{MCP_SERVER_URL}/teams/poll",
        headers=headers,
        timeout=10
    )
    return response.json()


def process_with_agent(message_text):
    """
    Process the message with your agent/LLM
    In Langflow, this would be your actual agent component
    """
    # For demo purposes, just echo back with "processed"
    # In real flow, connect to your LLM/Agent
    return f"I received your message: '{message_text}'. Processing complete!"


def send_response(response_text):
    """Send response back to Teams"""
    payload = {
        "message": response_text,
        "type": "text"
    }

    response = requests.post(
        f"{MCP_SERVER_URL}/teams/respond",
        headers=headers,
        json=payload,
        timeout=10
    )
    return response.json()


# Main Flow
print("Starting Teams message listener...")
print("Polling for messages every 5 seconds...")
print("Press Ctrl+C to stop")
print("-" * 50)

try:
    while True:
        # Step 1: Poll for messages
        result = poll_for_messages()

        if result.get('count', 0) > 0:
            messages = result.get('messages', [])

            for msg in messages:
                user = msg.get('user', 'Unknown')
                text = msg.get('text', '')

                print(f"\n[RECEIVED] Message from {user}: {text}")

                # Step 2: Process with agent
                agent_response = process_with_agent(text)
                print(f"[AGENT] Generated response: {agent_response}")

                # Step 3: Send response back to Teams
                send_result = send_response(agent_response)

                if send_result.get('success'):
                    print(f"[SENT] Response delivered to Teams!")
                else:
                    print(f"[ERROR] Failed to send: {send_result.get('message')}")

        # Wait before polling again
        time.sleep(5)

except KeyboardInterrupt:
    print("\n\nStopped listening for messages.")
