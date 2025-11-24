"""
MCP Teams Webhook Server with SSE Support
Full MCP Protocol Implementation for Langflow Integration
"""

import os
import json
import time
import base64
import mimetypes
import requests
from pathlib import Path
from flask import Flask, request, jsonify, Response
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Configuration
TEAMS_WEBHOOK_URL = os.getenv(
    "TEAMS_WEBHOOK_URL",
    "https://default2780a32d11ce4c57bad5ce0cffc115.a3.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/26e512fb89fa43aea71085fd99bada49/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=pQxmWrPAumQYq4SKLmX5zbew9YgQrwRYsIDyCHR_nVQ"
)
MCP_API_KEY = os.getenv("MCP_API_KEY", "langflow-teams-secret-123456")

app = Flask(__name__)


def read_file_as_base64(file_path: str) -> tuple:
    """
    Read a file and encode it as base64
    Returns: (base64_data, mime_type, error)
    """
    try:
        path = Path(file_path)

        # Check if file exists
        if not path.exists():
            return None, None, f"File not found: {file_path}"

        # Check if it's a file (not directory)
        if not path.is_file():
            return None, None, f"Path is not a file: {file_path}"

        # Get MIME type
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            # Default MIME types for common extensions
            ext = path.suffix.lower()
            mime_map = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.bmp': 'image/bmp',
                '.svg': 'image/svg+xml',
                '.webp': 'image/webp',
                '.pdf': 'application/pdf',
                '.txt': 'text/plain',
                '.json': 'application/json',
                '.xml': 'application/xml',
            }
            mime_type = mime_map.get(ext, 'application/octet-stream')

        # Read file and encode as base64
        with open(file_path, 'rb') as f:
            file_data = f.read()
            base64_data = base64.b64encode(file_data).decode('utf-8')

        return base64_data, mime_type, None

    except Exception as e:
        return None, None, f"Error reading file: {str(e)}"


def send_to_teams(message: str) -> dict:
    """Send a message to Microsoft Teams via webhook"""
    try:
        payload = {
            "text": message,
            "message": message,
            "content": message
        }
        headers = {"Content-Type": "application/json"}

        response = requests.post(
            TEAMS_WEBHOOK_URL,
            json=payload,
            headers=headers,
            timeout=10
        )

        if response.status_code in [200, 202]:
            return {
                "success": True,
                "message": "Message sent to Teams successfully",
                "status_code": response.status_code
            }
        else:
            return {
                "success": False,
                "message": f"Failed to send. Status: {response.status_code}",
                "error": response.text
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }


def send_image_to_teams(file_path: str, caption: str = "") -> dict:
    """Send an image from local file system to Microsoft Teams via webhook"""
    try:
        # Read and encode the image
        base64_data, mime_type, error = read_file_as_base64(file_path)

        if error:
            return {
                "success": False,
                "message": error
            }

        # Check if it's an image
        if not mime_type.startswith('image/'):
            return {
                "success": False,
                "message": f"File is not an image. MIME type: {mime_type}"
            }

        # Create data URI
        data_uri = f"data:{mime_type};base64,{base64_data}"

        # Build Adaptive Card with image
        card_body = [
            {
                "type": "Image",
                "url": data_uri,
                "size": "Large"
            }
        ]

        # Add caption if provided
        if caption:
            card_body.insert(0, {
                "type": "TextBlock",
                "text": caption,
                "wrap": True,
                "weight": "Bolder",
                "size": "Medium"
            })

        # Create the complete payload with Adaptive Card
        payload = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "contentUrl": None,
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.4",
                        "body": card_body
                    }
                }
            ]
        }

        headers = {"Content-Type": "application/json"}

        response = requests.post(
            TEAMS_WEBHOOK_URL,
            json=payload,
            headers=headers,
            timeout=30  # Longer timeout for large images
        )

        if response.status_code in [200, 202]:
            return {
                "success": True,
                "message": "Image sent to Teams successfully",
                "status_code": response.status_code,
                "file_path": file_path,
                "mime_type": mime_type
            }
        else:
            return {
                "success": False,
                "message": f"Failed to send. Status: {response.status_code}",
                "error": response.text
            }

    except Exception as e:
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }


def send_file_to_teams(file_path: str, description: str = "") -> dict:
    """Send a file from local file system to Microsoft Teams via webhook (as text preview or download link)"""
    try:
        # Read and encode the file
        base64_data, mime_type, error = read_file_as_base64(file_path)

        if error:
            return {
                "success": False,
                "message": error
            }

        path = Path(file_path)
        file_name = path.name
        file_size = path.stat().st_size

        # Format file size
        if file_size < 1024:
            size_str = f"{file_size} B"
        elif file_size < 1024 * 1024:
            size_str = f"{file_size / 1024:.2f} KB"
        else:
            size_str = f"{file_size / (1024 * 1024):.2f} MB"

        # Build Adaptive Card
        card_body = [
            {
                "type": "TextBlock",
                "text": f"File: {file_name}",
                "weight": "Bolder",
                "size": "Large"
            },
            {
                "type": "FactSet",
                "facts": [
                    {
                        "title": "Type:",
                        "value": mime_type
                    },
                    {
                        "title": "Size:",
                        "value": size_str
                    }
                ]
            }
        ]

        # Add description if provided
        if description:
            card_body.insert(1, {
                "type": "TextBlock",
                "text": description,
                "wrap": True,
                "separator": True
            })

        # For text files, include preview
        if mime_type.startswith('text/') and file_size < 50000:  # < 50KB
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(2000)  # First 2000 chars
                    if len(content) >= 2000:
                        content = content[:1997] + "..."

                    card_body.append({
                        "type": "TextBlock",
                        "text": f"```\n{content}\n```",
                        "wrap": True,
                        "separator": True
                    })
            except:
                pass  # Skip preview if can't read as text

        # Add note about file being encoded
        card_body.append({
            "type": "TextBlock",
            "text": f"File is encoded as base64. Total size: {len(base64_data)} characters",
            "wrap": True,
            "size": "Small",
            "isSubtle": True,
            "separator": True
        })

        # Create the complete payload with Adaptive Card
        payload = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "contentUrl": None,
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.4",
                        "body": card_body
                    }
                }
            ]
        }

        headers = {"Content-Type": "application/json"}

        response = requests.post(
            TEAMS_WEBHOOK_URL,
            json=payload,
            headers=headers,
            timeout=30
        )

        if response.status_code in [200, 202]:
            return {
                "success": True,
                "message": "File info sent to Teams successfully",
                "status_code": response.status_code,
                "file_path": file_path,
                "mime_type": mime_type,
                "file_size": size_str
            }
        else:
            return {
                "success": False,
                "message": f"Failed to send. Status: {response.status_code}",
                "error": response.text
            }

    except Exception as e:
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }


def verify_api_key():
    """Verify the MCP API key"""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return False
    token = auth_header[7:]
    return token == MCP_API_KEY


def format_sse_message(data: dict, event: str = "message") -> str:
    """Format a message for Server-Sent Events"""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


# ==================== MCP Protocol Endpoints ====================

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "MCP Teams Webhook Server (SSE)",
        "version": "2.0",
        "timestamp": datetime.now().isoformat()
    })


@app.route("/mcp/info", methods=["GET"])
def mcp_info():
    """MCP server information"""
    return jsonify({
        "name": "teams-webhook-mcp",
        "version": "2.0.0",
        "protocol_version": "2024-11-05",
        "capabilities": {
            "tools": True,
            "resources": False,
            "prompts": False
        },
        "server_info": {
            "name": "Microsoft Teams Webhook MCP Server",
            "description": "Send messages to Microsoft Teams via Power Automate webhook"
        }
    })


@app.route("/mcp/tools/list", methods=["GET", "POST"])
def list_tools():
    """List available MCP tools"""
    if not verify_api_key():
        return jsonify({"error": "Unauthorized"}), 401

    tools = [
        {
            "name": "send_teams_message",
            "description": "Send a text message to Microsoft Teams via webhook",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The message text to send to Microsoft Teams"
                    }
                },
                "required": ["message"]
            }
        },
        {
            "name": "send_teams_image",
            "description": "Send an image from local file system to Microsoft Teams via webhook. The image is read from your computer and sent as a base64-encoded Adaptive Card.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to the image file on your local computer (e.g., C:\\Users\\Name\\Pictures\\image.png)"
                    },
                    "caption": {
                        "type": "string",
                        "description": "Optional caption/title for the image"
                    }
                },
                "required": ["file_path"]
            }
        },
        {
            "name": "send_teams_file",
            "description": "Send file information from local file system to Microsoft Teams via webhook. Displays file metadata and preview for text files.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to the file on your local computer"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional description or context about the file"
                    }
                },
                "required": ["file_path"]
            }
        }
    ]

    return jsonify({"tools": tools})


@app.route("/mcp/tools/call", methods=["POST"])
def call_tool():
    """Call an MCP tool"""
    if not verify_api_key():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}
    tool_name = data.get("name")
    arguments = data.get("arguments", {})

    if tool_name == "send_teams_message":
        message = arguments.get("message", "")

        if not message:
            return jsonify({
                "isError": True,
                "content": [{
                    "type": "text",
                    "text": "Error: No message provided"
                }]
            }), 400

        result = send_to_teams(message)

        return jsonify({
            "content": [{
                "type": "text",
                "text": json.dumps(result, indent=2)
            }],
            "isError": not result.get("success", False)
        })

    elif tool_name == "send_teams_image":
        file_path = arguments.get("file_path", "")
        caption = arguments.get("caption", "")

        if not file_path:
            return jsonify({
                "isError": True,
                "content": [{
                    "type": "text",
                    "text": "Error: No file_path provided"
                }]
            }), 400

        result = send_image_to_teams(file_path, caption)

        return jsonify({
            "content": [{
                "type": "text",
                "text": json.dumps(result, indent=2)
            }],
            "isError": not result.get("success", False)
        })

    elif tool_name == "send_teams_file":
        file_path = arguments.get("file_path", "")
        description = arguments.get("description", "")

        if not file_path:
            return jsonify({
                "isError": True,
                "content": [{
                    "type": "text",
                    "text": "Error: No file_path provided"
                }]
            }), 400

        result = send_file_to_teams(file_path, description)

        return jsonify({
            "content": [{
                "type": "text",
                "text": json.dumps(result, indent=2)
            }],
            "isError": not result.get("success", False)
        })

    return jsonify({
        "isError": True,
        "content": [{
            "type": "text",
            "text": f"Unknown tool: {tool_name}"
        }]
    }), 404


# ==================== SSE Endpoint for MCP ====================

@app.route("/mcp/sse", methods=["GET"])
def mcp_sse():
    """Server-Sent Events endpoint for MCP protocol"""

    def generate():
        # Send endpoint notification (MCP protocol initialization)
        yield format_sse_message({
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        })

        # Keep connection alive with heartbeat
        try:
            while True:
                yield format_sse_message({
                    "jsonrpc": "2.0",
                    "method": "notifications/ping"
                })
                time.sleep(30)
        except GeneratorExit:
            pass

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive'
        }
    )


# ==================== Test Endpoint ====================

@app.route("/test", methods=["POST"])
def test_endpoint():
    """Test endpoint"""
    if not verify_api_key():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}
    message = data.get("message", "Test message from MCP SSE server")

    result = send_to_teams(message)
    return jsonify(result)


if __name__ == "__main__":
    print("=" * 70)
    print("MCP Teams Webhook Server v2.0 (with SSE Support)")
    print("=" * 70)
    print(f"Webhook URL: {TEAMS_WEBHOOK_URL[:80]}...")
    print(f"API Key: {MCP_API_KEY[:20]}...")
    print("=" * 70)
    print("\nMCP Endpoints:")
    print("  - Health:        http://localhost:5000/health")
    print("  - MCP Info:      http://localhost:5000/mcp/info")
    print("  - SSE Stream:    http://localhost:5000/mcp/sse")
    print("  - List Tools:    http://localhost:5000/mcp/tools/list")
    print("  - Call Tool:     http://localhost:5000/mcp/tools/call")
    print("  - Test:          http://localhost:5000/test")
    print("\nFor Langflow MCP Configuration:")
    print("  - SSE URL: http://host.docker.internal:5000/mcp/sse")
    print("  - Headers: Authorization: Bearer " + MCP_API_KEY)
    print("=" * 70)

    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
