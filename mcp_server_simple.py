"""
MCP Teams Webhook Server - Simple MessageCard Format
Works with basic Power Automate "Post message" action (no Adaptive Card support needed)
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
TEAMS_WEBHOOK_URL = os.getenv("TEAMS_WEBHOOK_URL")
MCP_API_KEY = os.getenv("MCP_API_KEY", "langflow-teams-secret-123456")

app = Flask(__name__)

# Add CORS headers
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
    """Send a simple text message to Teams"""
    try:
        payload = {"text": message}
        headers = {"Content-Type": "application/json"}
        response = requests.post(TEAMS_WEBHOOK_URL, json=payload, headers=headers, timeout=10)

        if response.status_code in [200, 202]:
            return {"success": True, "message": "Message sent", "status_code": response.status_code}
        else:
            return {"success": False, "message": f"Failed: {response.status_code}", "error": response.text}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}


def send_formatted_message(title: str, message: str, priority: str = "normal",
                          facts: dict = None, sender: str = None) -> dict:
    """Send a formatted message using MessageCard (works with simple Power Automate)"""
    try:
        # Priority icons
        icons = {"urgent": "🚨", "high": "⚠️", "normal": "ℹ️", "low": "📝"}
        icon = icons.get(priority.lower(), "ℹ️")

        # Build formatted text message
        formatted_text = f"**{icon} {title}**\n\n{message}"

        # Add facts if provided
        if facts:
            formatted_text += "\n\n**Details:**"
            for key, value in facts.items():
                formatted_text += f"\n- **{key}**: {value}"

        # Add metadata
        formatted_text += f"\n\n---"
        if sender:
            formatted_text += f"\n📤 From: {sender}"
        formatted_text += f"\n🕐 Sent: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        formatted_text += f"\n⚡ Priority: {priority.upper()}"

        payload = {"text": formatted_text}
        headers = {"Content-Type": "application/json"}
        response = requests.post(TEAMS_WEBHOOK_URL, json=payload, headers=headers, timeout=10)

        if response.status_code in [200, 202]:
            return {"success": True, "message": "Formatted message sent", "status_code": response.status_code}
        else:
            return {"success": False, "message": f"Failed: {response.status_code}", "error": response.text}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}


def verify_api_key():
    """Verify the MCP API key"""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return False
    return auth_header[7:] == MCP_API_KEY


def create_session():
    """Create a new SSE session"""
    session_id = str(uuid.uuid4())
    with session_lock:
        sessions[session_id] = {"queue": queue.Queue(), "created": datetime.now()}
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
        "service": "MCP Teams Webhook Server (Simple)",
        "version": "3.1-simple",
        "timestamp": datetime.now().isoformat()
    })


@app.route("/mcp/info", methods=["GET", "POST"])
def mcp_info():
    """MCP server information"""
    return jsonify({
        "protocolVersion": "2024-11-05",
        "capabilities": {"tools": {}},
        "serverInfo": {"name": "teams-webhook-mcp-simple", "version": "3.1.0"}
    })


@app.route("/mcp/initialize", methods=["POST"])
def mcp_initialize():
    """Initialize MCP connection"""
    return jsonify({
        "protocolVersion": "2024-11-05",
        "capabilities": {"tools": {}},
        "serverInfo": {"name": "teams-webhook-mcp-simple", "version": "3.1.0"}
    })


@app.route("/mcp/tools/list", methods=["GET", "POST"])
def list_tools():
    """List available MCP tools"""
    if not verify_api_key():
        return jsonify({"error": "Unauthorized"}), 401

    tools = [
        {
            "name": "send_teams_message",
            "description": "Send a simple text message to Teams",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "The message text"}
                },
                "required": ["message"]
            }
        },
        {
            "name": "send_formatted_message",
            "description": "Send a formatted message with title, priority, and facts (works with basic Power Automate)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Message title"},
                    "message": {"type": "string", "description": "Main message content"},
                    "priority": {
                        "type": "string",
                        "description": "Priority level",
                        "enum": ["urgent", "high", "normal", "low"],
                        "default": "normal"
                    },
                    "facts": {
                        "type": "object",
                        "description": "Optional key-value pairs"
                    },
                    "sender": {"type": "string", "description": "Optional sender name"}
                },
                "required": ["title", "message"]
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
                "content": [{"type": "text", "text": "Error: No message provided"}]
            }), 400

        result = send_to_teams(message)
        return jsonify({
            "content": [{"type": "text", "text": json.dumps(result, indent=2)}],
            "isError": not result.get("success", False)
        })

    elif tool_name == "send_formatted_message":
        title = arguments.get("title", "")
        message = arguments.get("message", "")
        priority = arguments.get("priority", "normal")
        facts = arguments.get("facts")
        sender = arguments.get("sender")

        if not title or not message:
            return jsonify({
                "isError": True,
                "content": [{"type": "text", "text": "Error: Title and message required"}]
            }), 400

        result = send_formatted_message(title, message, priority, facts, sender)
        return jsonify({
            "content": [{"type": "text", "text": json.dumps(result, indent=2)}],
            "isError": not result.get("success", False)
        })

    return jsonify({
        "isError": True,
        "content": [{"type": "text", "text": f"Unknown tool: {tool_name}"}]
    }), 404


@app.route("/test", methods=["POST"])
def test_endpoint():
    """Test endpoint"""
    if not verify_api_key():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}
    message = data.get("message", "Test message")
    result = send_to_teams(message)
    return jsonify(result)


if __name__ == "__main__":
    print("="*70)
    print("MCP Teams Webhook Server v3.1 (Simple MessageCard Format)")
    print("="*70)
    print("This version works with basic Power Automate 'Post message' action")
    print("No Adaptive Card support needed in Power Automate!")
    print("="*70)
    print(f"Webhook URL: {TEAMS_WEBHOOK_URL[:80]}...")
    print("="*70)
    print("\nAvailable Tools:")
    print("  1. send_teams_message - Simple text")
    print("  2. send_formatted_message - Formatted with title, priority, facts")
    print("="*70)

    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
