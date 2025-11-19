import requests
import json
from langflow.custom import Component
from langflow.io import MessageTextInput, Output
from langflow.schema import Data

class TeamsMessageSender(Component):
    display_name = "Send Teams Message"
    description = "Send a message to Microsoft Teams via MCP server"

    inputs = [
        MessageTextInput(
            name="message",
            display_name="Message",
            info="The message to send to Teams",
        ),
    ]

    outputs = [
        Output(display_name="Response", name="response", method="send_message"),
    ]

    def send_message(self) -> Data:
        url = "https://mythoclastic-consecrative-regena.ngrok-free.dev/mcp/tools/call"
        headers = {
            "Authorization": "Bearer langflow-teams-secret-123456",
            "Content-Type": "application/json"
        }
        payload = {
            "name": "send_teams_message",
            "arguments": {
                "message": self.message
            }
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()

            return Data(
                data={"result": result},
                text=f"Message sent successfully: {json.dumps(result, indent=2)}"
            )
        except Exception as e:
            return Data(
                data={"error": str(e)},
                text=f"Error sending message: {str(e)}"
            )
