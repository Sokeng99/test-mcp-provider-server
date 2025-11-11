"""
MCP Teams Webhook Server - Proper Langflow Integration
Implements full MCP protocol with bidirectional SSE communication
"""

import os
import json
import uuid
import queue
import threading
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

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

# Session management for SSE
sessions = {}
session_lock = threading.Lock()


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


def create_session():
    """Create a new SSE session"""
    session_id = str(uuid.uuid4())
    with session_lock:
        sessions[session_id] = {
            "queue": queue.Queue(),
            "created": datetime.now()
        }
    return session_id


def get_session(session_id):
    """Get an existing session"""
    with session_lock:
        return sessions.get(session_id)


def delete_session(session_id):
    """Delete a session"""
    with session_lock:
        if session_id in sessions:
            del sessions[session_id]


# ==================== MCP Protocol Endpoints ====================

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "MCP Teams Webhook Server (Langflow)",
        "version": "3.0",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": len(sessions)
    })


@app.route("/mcp/info", methods=["GET", "POST"])
def mcp_info():
    """MCP server information (supports both GET and POST)"""
    return jsonify({
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {}
        },
        "serverInfo": {
            "name": "teams-webhook-mcp",
            "version": "3.0.0"
        }
    })


@app.route("/mcp/initialize", methods=["POST"])
def mcp_initialize():
    """Initialize MCP connection"""
    data = request.get_json() or {}

    return jsonify({
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {}
        },
        "serverInfo": {
            "name": "teams-webhook-mcp",
            "version": "3.0.0"
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


# ==================== SSE Endpoint with Session Management ====================

@app.route("/mcp/sse", methods=["GET"])
def mcp_sse():
    """Server-Sent Events endpoint for MCP protocol with bidirectional support"""

    # Create session
    session_id = create_session()
    session = get_session(session_id)

    if not session:
        return jsonify({"error": "Failed to create session"}), 500

    def generate():
        try:
            # Send session ID
            yield format_sse_message({
                "type": "session",
                "sessionId": session_id
            }, event="session")

            # Send initialization notification
            yield format_sse_message({
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "teams-webhook-mcp",
                        "version": "3.0.0"
                    }
                }
            })

            # Stream messages from queue
            while True:
                try:
                    message = session["queue"].get(timeout=30)
                    if message is None:  # Shutdown signal
                        break
                    yield format_sse_message(message)
                except queue.Empty:
                    # Send heartbeat
                    yield format_sse_message({
                        "jsonrpc": "2.0",
                        "method": "notifications/ping"
                    })

        except GeneratorExit:
            pass
        finally:
            delete_session(session_id)

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*'
        }
    )


@app.route("/mcp/message", methods=["POST"])
def mcp_message():
    """Receive JSON-RPC messages and respond via SSE"""
    if not verify_api_key():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}
    session_id = data.get("sessionId") or request.headers.get("X-Session-ID")

    # Handle different JSON-RPC methods
    method = data.get("method")
    params = data.get("params", {})
    msg_id = data.get("id")

    if method == "tools/list":
        response = {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "tools": [{
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
            }
        }
    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name == "send_teams_message":
            result = send_to_teams(arguments.get("message", ""))
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{
                        "type": "text",
                        "text": json.dumps(result, indent=2)
                    }]
                }
            }
        else:
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32601,
                    "message": f"Unknown tool: {tool_name}"
                }
            }
    else:
        response = {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}"
            }
        }

    # If session exists, queue the response
    if session_id:
        session = get_session(session_id)
        if session:
            session["queue"].put(response)
            return jsonify({"status": "queued"}), 202

    # Otherwise return directly
    return jsonify(response)


# ==================== Test Endpoint ====================

@app.route("/test", methods=["POST"])
def test_endpoint():
    """Test endpoint"""
    if not verify_api_key():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}
    message = data.get("message", "Test message from MCP server")

    result = send_to_teams(message)
    return jsonify(result)


if __name__ == "__main__":
    print("=" * 70)
    print("MCP Teams Webhook Server v3.0 (Langflow Compatible)")
    print("=" * 70)
    print(f"Webhook URL: {TEAMS_WEBHOOK_URL[:80]}...")
    print(f"API Key: {MCP_API_KEY[:20]}...")
    print("=" * 70)
    print("\nMCP Endpoints:")
    print("  - Health:        http://localhost:5000/health")
    print("  - Initialize:    http://localhost:5000/mcp/initialize")
    print("  - Info:          http://localhost:5000/mcp/info")
    print("  - SSE Stream:    http://localhost:5000/mcp/sse")
    print("  - Message:       http://localhost:5000/mcp/message")
    print("  - List Tools:    http://localhost:5000/mcp/tools/list")
    print("  - Call Tool:     http://localhost:5000/mcp/tools/call")
    print("\nFor Langflow MCP Configuration:")
    print("  - SSE URL: http://host.docker.internal:5000/mcp/sse")
    print("  - Headers: Authorization: Bearer " + MCP_API_KEY)
    print("  - Transport: sse")
    print("=" * 70)

    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
