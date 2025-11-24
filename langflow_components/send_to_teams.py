"""
Langflow Custom Component: Send to Teams (Auto-detect File/Image)
"""

from langflow.custom import Component
from langflow.io import MessageTextInput, Output, StrInput
from langflow.schema import Data
import requests
import json
import os


class SendToTeamsComponent(Component):
    display_name = "Send to Teams"
    description = "Send file or image to Microsoft Teams (auto-detects type)"
    icon = "send"

    inputs = [
        StrInput(
            name="file_path",
            display_name="File Path",
            info="Absolute path to file/image (e.g., C:\\Users\\Name\\file.png)",
            required=True
        ),
        MessageTextInput(
            name="message",
            display_name="Message/Caption",
            info="Description for files or caption for images",
            required=False
        ),
        StrInput(
            name="mcp_server_url",
            display_name="MCP Server URL",
            info="URL of the MCP server",
            value="http://localhost:5000",
            required=True
        ),
        StrInput(
            name="api_key",
            display_name="API Key",
            info="MCP server API key",
            value="langflow-teams-secret-123456",
            password=True,
            required=True
        )
    ]

    outputs = [
        Output(display_name="Result", name="result", method="send_to_teams")
    ]

    def send_to_teams(self) -> Data:
        """Send file or image to Teams via MCP server (auto-detect)"""

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
                "arguments": {
                    "file_path": file_path,
                    "caption": message
                }
            }
        else:
            tool_name = "send_teams_file"
            payload = {
                "name": tool_name,
                "arguments": {
                    "file_path": file_path,
                    "description": message
                }
            }

        try:
            # Call MCP server
            response = requests.post(
                f"{mcp_url}/mcp/tools/call",
                headers=headers,
                json=payload,
                timeout=30
            )

            result = response.json()

            # Parse the result
            if response.status_code == 200 and not result.get('isError', True):
                content = result.get('content', [{}])[0]
                result_text = content.get('text', '{}')
                result_data = json.loads(result_text)

                return Data(
                    data={
                        "success": True,
                        "type": "image" if is_image else "file",
                        "message": result_data.get('message', 'Sent successfully'),
                        "file_path": result_data.get('file_path', file_path),
                        "file_size": result_data.get('file_size', 'N/A'),
                        "mime_type": result_data.get('mime_type', 'Unknown'),
                        "status_code": result_data.get('status_code', response.status_code),
                        "tool_used": tool_name
                    }
                )
            else:
                error_msg = result.get('content', [{}])[0].get('text', 'Failed to send')
                return Data(
                    data={
                        "success": False,
                        "error": error_msg,
                        "status_code": response.status_code,
                        "tool_used": tool_name
                    }
                )

        except Exception as e:
            return Data(
                data={
                    "success": False,
                    "error": str(e),
                    "tool_used": tool_name if 'tool_name' in locals() else 'unknown'
                }
            )
