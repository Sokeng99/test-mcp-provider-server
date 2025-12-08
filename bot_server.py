"""
Bot Server - Flask application to host the Teams Bot
Receives messages from Azure Bot Service and responds
"""

from flask import Flask, request, jsonify
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings
from botbuilder.schema import Activity
from teams_bot import TeamsBot
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# Bot configuration from environment
APP_ID = os.getenv("MICROSOFT_APP_ID", "")
APP_PASSWORD = os.getenv("MICROSOFT_APP_PASSWORD", "")
APP_TENANT_ID = os.getenv("MICROSOFT_APP_TENANT_ID", "")

# Create adapter with tenant ID for single-tenant apps
SETTINGS = BotFrameworkAdapterSettings(
    app_id=APP_ID,
    app_password=APP_PASSWORD,
    # For single-tenant bots, specify the tenant ID
    channel_auth_tenant=APP_TENANT_ID if APP_TENANT_ID else None
)
ADAPTER = BotFrameworkAdapter(SETTINGS)

# Create bot
BOT = TeamsBot()

# Create Flask app
app = Flask(__name__)


@app.route("/api/messages", methods=["POST", "GET"])
def messages():
    """
    Main endpoint for receiving messages from Teams
    Azure Bot Service sends all user messages here
    """
    # Handle GET requests (health check from Azure)
    if request.method == "GET":
        return jsonify({
            "status": "ready",
            "message": "Bot endpoint is active"
        })

    # Handle POST requests (actual messages)
    # Get the incoming activity (message) from Teams
    if "application/json" in request.headers.get("Content-Type", ""):
        body = request.json
    else:
        return jsonify({"error": "Invalid Content-Type"}), 415

    # Convert to Activity object
    activity = Activity().deserialize(body)

    # Get auth header
    auth_header = request.headers.get("Authorization", "")

    # Process the activity with the bot
    async def call_bot():
        await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)

    # Run the async bot logic
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(call_bot())

    return jsonify({"status": "ok"})


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "X-pilot Teams Bot",
        "version": "1.0",
        "app_id": APP_ID[:10] + "..." if APP_ID else "Not configured"
    })


if __name__ == "__main__":
    print("=" * 70)
    print("X-pilot Teams Bot Server")
    print("=" * 70)
    print(f"App ID: {APP_ID[:20]}..." if APP_ID else "App ID: Not configured")
    print("=" * 70)
    print("\nEndpoints:")
    print("  http://localhost:3978/api/messages  (Bot endpoint)")
    print("  http://localhost:3978/health        (Health check)")
    print("\nBot is ready! Configure in Azure Bot Service.")
    print("=" * 70)

    app.run(host="0.0.0.0", port=3978, debug=False)
