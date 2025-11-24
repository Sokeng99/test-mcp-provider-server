"""
Simple MCP Server for Microsoft Teams
Uses Teams Incoming Webhook (100% FREE - No premium features!)
"""

import os
import json
import uuid
import queue
import threading
import base64
import mimetypes
import requests
from pathlib import Path
from flask import Flask, request, jsonify, Response
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Configuration
TEAMS_WEBHOOK_URL = os.getenv("TEAMS_WEBHOOK_URL", "")
MCP_API_KEY = os.getenv("MCP_API_KEY", "langflow-teams-secret-123456")

app = Flask(__name__)

# Session management
sessions = {}
session_lock = threading.Lock()

# Message storage for two-way communication
incoming_messages = queue.Queue()
message_history = []
MAX_HISTORY = 100


def verify_api_key():
    """Verify API key"""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return False
    return auth_header[7:] == MCP_API_KEY


def send_to_teams(message: str) -> dict:
    """Send simple text message to Teams"""
    if not TEAMS_WEBHOOK_URL:
        return {"success": False, "error": "TEAMS_WEBHOOK_URL not configured"}

    try:
        response = requests.post(
            TEAMS_WEBHOOK_URL,
            json={"text": message},
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        return {
            "success": response.status_code in [200, 202],
            "status_code": response.status_code
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def send_adaptive_card(title: str, message: str, priority: str = "normal", facts: dict = None) -> dict:
    """Send Adaptive Card to Teams"""
    if not TEAMS_WEBHOOK_URL:
        return {"success": False, "error": "TEAMS_WEBHOOK_URL not configured"}

    priority_icons = {"urgent": "🚨", "high": "⚠️", "normal": "ℹ️", "low": "📝"}
    icon = priority_icons.get(priority.lower(), "ℹ️")

    card_body = [
        {"type": "TextBlock", "text": f"{icon} {title}", "weight": "bolder", "size": "large", "wrap": True},
        {"type": "TextBlock", "text": message, "wrap": True}
    ]

    if facts:
        card_body.append({
            "type": "FactSet",
            "facts": [{"title": k, "value": str(v)} for k, v in facts.items()]
        })

    payload = {
        "type": "message",
        "attachments": [{
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": {
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "type": "AdaptiveCard",
                "version": "1.4",
                "body": card_body
            }
        }]
    }

    try:
        response = requests.post(TEAMS_WEBHOOK_URL, json=payload, timeout=10)
        return {"success": response.status_code in [200, 202], "status_code": response.status_code}
    except Exception as e:
        return {"success": False, "error": str(e)}


def send_image_to_teams(file_path: str, caption: str = "") -> dict:
    """Send image to Teams as Adaptive Card"""
    if not TEAMS_WEBHOOK_URL:
        return {"success": False, "error": "TEAMS_WEBHOOK_URL not configured"}

    try:
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            return {"success": False, "error": f"File not found: {file_path}"}

        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type or not mime_type.startswith('image/'):
            return {"success": False, "error": "File is not an image"}

        with open(file_path, 'rb') as f:
            base64_data = base64.b64encode(f.read()).decode('utf-8')

        data_uri = f"data:{mime_type};base64,{base64_data}"

        card_body = []
        if caption:
            card_body.append({"type": "TextBlock", "text": caption, "wrap": True, "weight": "Bolder"})
        card_body.append({"type": "Image", "url": data_uri, "size": "Large"})

        payload = {
            "type": "message",
            "attachments": [{
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "body": card_body
                }
            }]
        }

        response = requests.post(TEAMS_WEBHOOK_URL, json=payload, timeout=30)
        return {"success": response.status_code in [200, 202], "status_code": response.status_code}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==================== Endpoints ====================

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "service": "MCP Teams Server",
        "version": "1.0",
        "webhook_configured": bool(TEAMS_WEBHOOK_URL)
    })


@app.route("/mcp/info", methods=["GET", "POST"])
def mcp_info():
    return jsonify({
        "protocolVersion": "2024-11-05",
        "capabilities": {"tools": {}},
        "serverInfo": {"name": "teams-mcp", "version": "1.0.0"}
    })


@app.route("/mcp/tools/list", methods=["GET", "POST"])
def list_tools():
    if not verify_api_key():
        return jsonify({"error": "Unauthorized"}), 401

    return jsonify({"tools": [
        {
            "name": "send_teams_message",
            "description": "Send a text message to Microsoft Teams",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Message to send"}
                },
                "required": ["message"]
            }
        },
        {
            "name": "send_adaptive_card",
            "description": "Send a rich formatted card to Teams",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Card title"},
                    "message": {"type": "string", "description": "Card message"},
                    "priority": {"type": "string", "enum": ["urgent", "high", "normal", "low"], "default": "normal"},
                    "facts": {"type": "object", "description": "Optional key-value pairs"}
                },
                "required": ["title", "message"]
            }
        },
        {
            "name": "send_teams_image",
            "description": "Send an image from local file to Teams",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Absolute path to image file"},
                    "caption": {"type": "string", "description": "Optional caption"}
                },
                "required": ["file_path"]
            }
        },
        {
            "name": "get_teams_messages",
            "description": "Get pending messages from Teams (requires n8n setup)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 10}
                }
            }
        }
    ]})


@app.route("/mcp/tools/call", methods=["POST"])
def call_tool():
    if not verify_api_key():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}
    tool_name = data.get("name")
    arguments = data.get("arguments", {})

    if tool_name == "send_teams_message":
        result = send_to_teams(arguments.get("message", ""))
        return jsonify({"content": [{"type": "text", "text": json.dumps(result, indent=2)}], "isError": not result["success"]})

    elif tool_name == "send_adaptive_card":
        result = send_adaptive_card(
            arguments.get("title", ""),
            arguments.get("message", ""),
            arguments.get("priority", "normal"),
            arguments.get("facts")
        )
        return jsonify({"content": [{"type": "text", "text": json.dumps(result, indent=2)}], "isError": not result["success"]})

    elif tool_name == "send_teams_image":
        result = send_image_to_teams(arguments.get("file_path", ""), arguments.get("caption", ""))
        return jsonify({"content": [{"type": "text", "text": json.dumps(result, indent=2)}], "isError": not result["success"]})

    elif tool_name == "get_teams_messages":
        messages = []
        limit = arguments.get("limit", 10)
        try:
            while len(messages) < limit and not incoming_messages.empty():
                messages.append(incoming_messages.get_nowait())
        except queue.Empty:
            pass
        return jsonify({"content": [{"type": "text", "text": json.dumps({"count": len(messages), "messages": messages}, indent=2)}], "isError": False})

    return jsonify({"isError": True, "content": [{"type": "text", "text": f"Unknown tool: {tool_name}"}]}), 404


@app.route("/teams/incoming", methods=["POST"])
def receive_from_teams():
    """Receive messages from Teams (via n8n or custom webhook)"""
    try:
        data = request.get_json() or {}
        message_data = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "text": data.get("text", ""),
            "user": data.get("user", "Unknown"),
            "raw": data
        }

        incoming_messages.put(message_data)
        message_history.append(message_data)
        if len(message_history) > MAX_HISTORY:
            message_history.pop(0)

        return jsonify({"success": True, "id": message_data["id"]}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/mcp/sse", methods=["GET"])
def mcp_sse():
    """SSE endpoint for MCP"""
    session_id = str(uuid.uuid4())

    def generate():
        try:
            yield f"event: session\ndata: {json.dumps({'sessionId': session_id})}\n\n"
            yield f"event: message\ndata: {json.dumps({'jsonrpc': '2.0', 'method': 'notifications/initialized'})}\n\n"

            while True:
                yield f"event: message\ndata: {json.dumps({'jsonrpc': '2.0', 'method': 'notifications/ping'})}\n\n"
                import time
                time.sleep(30)
        except GeneratorExit:
            pass

    return Response(generate(), mimetype='text/event-stream', headers={
        'Cache-Control': 'no-cache',
        'X-Accel-Buffering': 'no',
        'Connection': 'keep-alive'
    })


@app.route("/test", methods=["POST"])
def test_endpoint():
    if not verify_api_key():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}
    result = send_to_teams(data.get("message", "Test message"))
    return jsonify(result)


if __name__ == "__main__":
    print("="*70)
    print("MCP Teams Server v1.0 - Simple & FREE!")
    print("="*70)
    print(f"Webhook: {'[OK] Configured' if TEAMS_WEBHOOK_URL else '[X] NOT SET'}")
    print(f"API Key: {MCP_API_KEY[:20]}...")
    print("="*70)
    print("\nEndpoints:")
    print("  http://localhost:5000/health")
    print("  http://localhost:5000/mcp/sse")
    print("  http://localhost:5000/test")
    print("\nSee README.md for setup instructions")
    print("="*70)

    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
