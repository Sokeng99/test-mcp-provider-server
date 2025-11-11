"""
MCP Teams Webhook Server with SSE Support
Full MCP Protocol Implementation for Langflow Integration
"""

import os
import json
import time
import requests
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

    tools = [{
        "name": "send_teams_message",
        "description": "Send a message to Microsoft Teams via webhook",
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
    }]

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
