from langflow.custom import CustomComponent
from langflow.schema import Data
import requests
import json
import os


class SendToTeams(CustomComponent):
    display_name = "Send to Teams"
    description = "Send file or image to Microsoft Teams"
    documentation = "https://github.com/yourusername/mcp-teams-webhook"

    def build_config(self):
        return {
            "file_path": {
                "display_name": "File Path",
                "info": "Absolute path to file (e.g., C:\\Users\\Name\\file.pdf)",
            },
            "message": {
                "display_name": "Message/Caption",
                "info": "Description for files or caption for images",
                "multiline": True,
            },
            "mcp_server_url": {
                "display_name": "MCP Server URL",
                "value": "http://localhost:5000",
            },
            "api_key": {
                "display_name": "API Key",
                "password": True,
                "value": "langflow-teams-secret-123456",
            },
        }

    def build(
        self,
        file_path: str,
        message: str = "",
        mcp_server_url: str = "http://localhost:5000",
        api_key: str = "langflow-teams-secret-123456",
    ) -> Data:
        """Send file or image to Teams via MCP server"""

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
                f"{mcp_server_url.rstrip('/')}/mcp/tools/call",
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
                }
            )
