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

# Configuration - Load from .env file only
TEAMS_WEBHOOK_URL = os.getenv("TEAMS_WEBHOOK_URL")
MCP_API_KEY = os.getenv("MCP_API_KEY", "langflow-teams-secret-123456")

if not TEAMS_WEBHOOK_URL:
    raise ValueError("TEAMS_WEBHOOK_URL must be set in .env file!")

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
    """Send a simple text message to Microsoft Teams via webhook"""
    try:
        # Simple payload - just the message
        payload = {"message": message}

        print(f"\n[DEBUG] Sending to webhook: {TEAMS_WEBHOOK_URL[:80]}...")
        print(f"[DEBUG] Payload: {json.dumps(payload, indent=2)}")

        response = requests.post(
            TEAMS_WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        print(f"[DEBUG] Response status: {response.status_code}")
        print(f"[DEBUG] Response body: {response.text}\n")

        if response.status_code in [200, 202]:
            return {
                "success": True,
                "message": "Message sent to Teams",
                "status_code": response.status_code
            }
        else:
            return {
                "success": False,
                "message": f"Failed: Status {response.status_code}",
                "error": response.text
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }


def send_adaptive_card(title: str, message: str, priority: str = "normal",
                      facts: dict = None, image_url: str = None,
                      sender: str = None) -> dict:
    """Send a rich formatted Adaptive Card message to Teams

    Args:
        title: Card title
        message: Main message content
        priority: Priority level (urgent, high, normal, low)
        facts: Dictionary of key-value pairs to display as facts
        image_url: Optional image URL to include
        sender: Optional sender name/identifier
    """
    try:
        # Color coding based on priority
        priority_colors = {
            "urgent": "attention",  # Red
            "high": "warning",      # Yellow
            "normal": "good",       # Green
            "low": "default"        # Gray
        }

        priority_icons = {
            "urgent": "🚨",
            "high": "⚠️",
            "normal": "ℹ️",
            "low": "📝"
        }

        theme_color = priority_colors.get(priority.lower(), "default")
        icon = priority_icons.get(priority.lower(), "ℹ️")

        # Build the card body
        card_body = [
            {
                "type": "TextBlock",
                "text": f"{icon} {title}",
                "weight": "bolder",
                "size": "large",
                "wrap": True
            },
            {
                "type": "TextBlock",
                "text": message,
                "wrap": True,
                "spacing": "medium"
            }
        ]

        # Add image if provided
        if image_url:
            card_body.append({
                "type": "Image",
                "url": image_url,
                "size": "large",
                "spacing": "medium"
            })

        # Add facts if provided
        if facts:
            fact_set = {
                "type": "FactSet",
                "facts": [{"title": k, "value": str(v)} for k, v in facts.items()],
                "spacing": "medium"
            }
            card_body.append(fact_set)

        # Add metadata footer
        footer_facts = []
        if sender:
            footer_facts.append({"title": "From", "value": sender})
        footer_facts.append({
            "title": "Sent",
            "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        footer_facts.append({
            "title": "Priority",
            "value": priority.upper()
        })

        card_body.append({
            "type": "FactSet",
            "facts": footer_facts,
            "spacing": "medium",
            "separator": True
        })

        # Construct the Adaptive Card payload
        adaptive_card = {
            "type": "message",
            "attachments": [{
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "body": card_body,
                    "msteams": {
                        "width": "full"
                    }
                }
            }]
        }

        headers = {"Content-Type": "application/json"}

        response = requests.post(
            TEAMS_WEBHOOK_URL,
            json=adaptive_card,
            headers=headers,
            timeout=10
        )

        if response.status_code in [200, 202]:
            return {
                "success": True,
                "message": "Adaptive Card sent to Teams successfully",
                "status_code": response.status_code,
                "card_type": "adaptive",
                "priority": priority
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


def send_notification(title: str, message: str, priority: str = "normal",
                      action_url: str = None, action_text: str = "View Details") -> dict:
    """Send a notification-style message with optional action button

    Args:
        title: Notification title
        message: Notification message
        priority: Priority level (urgent, high, normal, low)
        action_url: Optional URL for action button
        action_text: Text for the action button
    """
    try:
        facts = {
            "Priority": priority.upper(),
            "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # If action URL provided, send adaptive card with button
        if action_url:
            card_body = [
                {
                    "type": "TextBlock",
                    "text": title,
                    "weight": "bolder",
                    "size": "large",
                    "wrap": True
                },
                {
                    "type": "TextBlock",
                    "text": message,
                    "wrap": True,
                    "spacing": "medium"
                },
                {
                    "type": "FactSet",
                    "facts": [{"title": k, "value": v} for k, v in facts.items()],
                    "spacing": "medium"
                }
            ]

            adaptive_card = {
                "type": "message",
                "attachments": [{
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.4",
                        "body": card_body,
                        "actions": [{
                            "type": "Action.OpenUrl",
                            "title": action_text,
                            "url": action_url
                        }]
                    }
                }]
            }

            headers = {"Content-Type": "application/json"}
            response = requests.post(
                TEAMS_WEBHOOK_URL,
                json=adaptive_card,
                headers=headers,
                timeout=10
            )
        else:
            # Simple notification without action button
            return send_adaptive_card(title, message, priority, facts)

        if response.status_code in [200, 202]:
            return {
                "success": True,
                "message": "Notification sent to Teams successfully",
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

    tools = [
        {
            "name": "send_teams_message",
            "description": "Send a simple text message to Microsoft Teams via webhook",
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
            "name": "send_adaptive_card",
            "description": "Send a rich formatted Adaptive Card message with priority, facts, images, and metadata",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The card title"
                    },
                    "message": {
                        "type": "string",
                        "description": "The main message content"
                    },
                    "priority": {
                        "type": "string",
                        "description": "Priority level: urgent, high, normal, or low",
                        "enum": ["urgent", "high", "normal", "low"],
                        "default": "normal"
                    },
                    "facts": {
                        "type": "object",
                        "description": "Optional key-value pairs to display as facts (e.g., {'Status': 'Running', 'Progress': '75%'})",
                        "additionalProperties": {"type": "string"}
                    },
                    "image_url": {
                        "type": "string",
                        "description": "Optional image URL to include in the card"
                    },
                    "sender": {
                        "type": "string",
                        "description": "Optional sender name or identifier"
                    }
                },
                "required": ["title", "message"]
            }
        },
        {
            "name": "send_notification",
            "description": "Send a notification with optional action button",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The notification title"
                    },
                    "message": {
                        "type": "string",
                        "description": "The notification message"
                    },
                    "priority": {
                        "type": "string",
                        "description": "Priority level: urgent, high, normal, or low",
                        "enum": ["urgent", "high", "normal", "low"],
                        "default": "normal"
                    },
                    "action_url": {
                        "type": "string",
                        "description": "Optional URL for the action button"
                    },
                    "action_text": {
                        "type": "string",
                        "description": "Text for the action button (default: 'View Details')",
                        "default": "View Details"
                    }
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

    # DEBUG: Log incoming request
    print("=" * 70)
    print("INCOMING REQUEST TO /mcp/tools/call")
    print(f"Headers: {dict(request.headers)}")
    print(f"Raw data: {request.get_data(as_text=True)}")
    print(f"Parsed JSON: {json.dumps(data, indent=2)}")
    print("=" * 70)

    tool_name = data.get("name")
    arguments = data.get("arguments", {})

    # Handle case where arguments might be a string instead of dict
    if isinstance(arguments, str):
        print(f"WARNING: arguments is a string, not a dict: {arguments}")
        return jsonify({
            "isError": True,
            "content": [{
                "type": "text",
                "text": f"Error: arguments must be a JSON object, received string: {arguments}"
            }]
        }), 400

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

    elif tool_name == "send_adaptive_card":
        title = arguments.get("title", "")
        message = arguments.get("message", "")
        priority = arguments.get("priority", "normal")
        facts = arguments.get("facts")
        image_url = arguments.get("image_url")
        sender = arguments.get("sender")

        if not title or not message:
            return jsonify({
                "isError": True,
                "content": [{
                    "type": "text",
                    "text": "Error: Both title and message are required"
                }]
            }), 400

        result = send_adaptive_card(title, message, priority, facts, image_url, sender)

        return jsonify({
            "content": [{
                "type": "text",
                "text": json.dumps(result, indent=2)
            }],
            "isError": not result.get("success", False)
        })

    elif tool_name == "send_notification":
        title = arguments.get("title", "")
        message = arguments.get("message", "")
        priority = arguments.get("priority", "normal")
        action_url = arguments.get("action_url")
        action_text = arguments.get("action_text", "View Details")

        if not title or not message:
            return jsonify({
                "isError": True,
                "content": [{
                    "type": "text",
                    "text": "Error: Both title and message are required"
                }]
            }), 400

        result = send_notification(title, message, priority, action_url, action_text)

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
                "tools": [
                    {
                        "name": "send_teams_message",
                        "description": "Send a simple text message to Microsoft Teams via webhook",
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
                        "name": "send_adaptive_card",
                        "description": "Send a rich formatted Adaptive Card message with priority, facts, images, and metadata",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "message": {"type": "string"},
                                "priority": {"type": "string", "enum": ["urgent", "high", "normal", "low"]},
                                "facts": {"type": "object"},
                                "image_url": {"type": "string"},
                                "sender": {"type": "string"}
                            },
                            "required": ["title", "message"]
                        }
                    },
                    {
                        "name": "send_notification",
                        "description": "Send a notification with optional action button",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "message": {"type": "string"},
                                "priority": {"type": "string", "enum": ["urgent", "high", "normal", "low"]},
                                "action_url": {"type": "string"},
                                "action_text": {"type": "string"}
                            },
                            "required": ["title", "message"]
                        }
                    }
                ]
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
        elif tool_name == "send_adaptive_card":
            result = send_adaptive_card(
                arguments.get("title", ""),
                arguments.get("message", ""),
                arguments.get("priority", "normal"),
                arguments.get("facts"),
                arguments.get("image_url"),
                arguments.get("sender")
            )
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
        elif tool_name == "send_notification":
            result = send_notification(
                arguments.get("title", ""),
                arguments.get("message", ""),
                arguments.get("priority", "normal"),
                arguments.get("action_url"),
                arguments.get("action_text", "View Details")
            )
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
