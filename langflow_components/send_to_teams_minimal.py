from langflow.custom import Component
from langflow.io import MessageTextInput, Output, StrInput
from langflow.schema import Data
import requests
import json
import os


class SendToTeams(Component):
    display_name = "Send to Teams"
    description = "Send file to Teams"

    inputs = [
        StrInput(name="file_path", display_name="File Path", required=True),
        MessageTextInput(name="message", display_name="Message"),
        StrInput(name="server_url", display_name="Server URL", value="http://localhost:5000"),
        StrInput(name="api_key", display_name="API Key", value="langflow-teams-secret-123456"),
    ]

    outputs = [
        Output(display_name="Result", name="output", method="send_to_teams"),
    ]

    def send_to_teams(self) -> Data:
        ext = os.path.splitext(self.file_path)[1].lower()
        is_image = ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "name": "send_teams_image" if is_image else "send_teams_file",
            "arguments": {
                "file_path": self.file_path,
                "caption" if is_image else "description": self.message or ""
            }
        }

        try:
            response = requests.post(
                f"{self.server_url}/mcp/tools/call",
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                return Data(data={"success": True, "message": "Sent to Teams!"})
            else:
                return Data(data={"success": False, "error": response.text})
        except Exception as e:
            return Data(data={"success": False, "error": str(e)})
