from langflow.custom import Component
from langflow.inputs import StrInput, SecretStrInput, MessageTextInput
from langflow.template import Output
from langflow.schema.message import Message
import requests
import json
import os


class SendToTeamsComponent(Component):
    display_name = "Send to Teams"
    description = "Send file or image from local computer to Microsoft Teams"
    icon = "send"

    inputs = [
        StrInput(
            name="file_path",
            display_name="File Path",
            info="Absolute path to file (e.g., C:\\Users\\Name\\file.pdf)",
            required=True,
        ),
        MessageTextInput(
            name="message",
            display_name="Message/Caption",
            info="Description for files or caption for images",
        ),
        StrInput(
            name="mcp_server_url",
            display_name="MCP Server URL",
            value="http://localhost:5000",
        ),
        SecretStrInput(
            name="api_key",
            display_name="API Key",
            value="langflow-teams-secret-123456",
        ),
    ]

    outputs = [
        Output(display_name="Result", name="result", method="send_file"),
    ]

    def send_file(self) -> Message:
        file_path = self.file_path
        message = self.message or ""
        mcp_url = self.mcp_server_url.rstrip('/')
        api_key = self.api_key

        # Auto-detect if it's an image
        ext = os.path.splitext(file_path)[1].lower()
        is_image = ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']

        # Prepare the request
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        if is_image:
            tool_name = "send_teams_image"
            payload = {
                "name": tool_name,
                "arguments": {"file_path": file_path, "caption": message}
            }
        else:
            tool_name = "send_teams_file"
            payload = {
                "name": tool_name,
                "arguments": {"file_path": file_path, "description": message}
            }

        try:
            response = requests.post(
                f"{mcp_url}/mcp/tools/call",
                headers=headers,
                json=payload,
                timeout=30
            )

            result = response.json()

            if response.status_code == 200 and not result.get('isError', True):
                content = result.get('content', [{}])[0]
                result_text = content.get('text', '{}')
                result_data = json.loads(result_text)

                success_msg = f"✓ Sent to Teams successfully!\nFile: {file_path}\nType: {'Image' if is_image else 'File'}"
                return Message(text=success_msg)
            else:
                error_msg = result.get('content', [{}])[0].get('text', 'Failed')
                return Message(text=f"✗ Error: {error_msg}")

        except Exception as e:
            return Message(text=f"✗ Error: {str(e)}")
