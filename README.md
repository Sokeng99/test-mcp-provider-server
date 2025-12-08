# X-Pilot Teams Bot

AI-powered interactive bot for Microsoft Teams using Azure Bot Service and Langflow. **100% FREE** (Azure Bot Service free tier: 10,000 messages/month).

## Features

- Interactive conversations with Langflow AI in Teams
- Natural language processing and responses
- Direct mentions (@xpilot-bot) in channels
- Private 1-on-1 conversations
- Easy deployment to Teams

## Quick Setup

### Prerequisites

- Microsoft Azure account (free tier works)
- Langflow running locally or accessible endpoint
- ngrok for local development (free)

### 1. Azure Bot Setup

See `TEAMS_BOT_SETUP.md` for complete step-by-step instructions.

Quick summary:
1. Create Azure Bot Service resource
2. Get App ID and create client secret in Microsoft Entra ID
3. Configure messaging endpoint with ngrok URL

### 2. Environment Configuration

Create/edit `.env` file:

```env
# Azure Bot Service credentials
MICROSOFT_APP_ID=your-app-id-here
MICROSOFT_APP_PASSWORD=your-client-secret-here
MICROSOFT_APP_TENANT_ID=your-tenant-id-here

# Langflow Configuration
LANGFLOW_URL=http://localhost:7860
LANGFLOW_FLOW_ID=your-flow-id-here
LANGFLOW_API_KEY=your-api-key-here
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Bot Server

```bash
python bot_server.py
```

You should see:
```
Flask app running on http://0.0.0.0:3978
Bot is ready to receive messages at /api/messages
```

### 5. Setup ngrok (for local development)

```bash
ngrok http 3978
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok-free.app`) and configure it in Azure:
- Azure Portal → Your Bot → Configuration → Messaging endpoint
- Set to: `https://your-ngrok-url.ngrok-free.app/api/messages`

### 6. Deploy to Teams

Use the Teams app package `xpilot-bot-teams-app.zip`:

1. Open Microsoft Teams
2. Go to Apps → Manage your apps → Upload an app
3. Upload `xpilot-bot-teams-app.zip`
4. Add to team or chat

See `TEAMS_APP_INSTALL_INSTRUCTIONS.md` for detailed instructions.

## Usage

### In Teams Channels

Mention the bot:
```
@xpilot-bot What is the weather today?
```

### In Direct Messages

Just send a message:
```
Help me analyze this data
```

## Architecture

```
User in Teams → Azure Bot Service → bot_server.py → Langflow AI → Response back to user
```

## Files

- `bot_server.py` - Flask server that handles bot messages
- `teams_bot.py` - Bot logic with Langflow integration
- `.env` - Configuration (credentials and endpoints)
- `requirements.txt` - Python dependencies
- `teams-app/` - Teams app package files (manifest, icons)
- `xpilot-bot-teams-app.zip` - Ready-to-upload Teams app
- `TEAMS_BOT_SETUP.md` - Complete setup guide
- `TEAMS_APP_INSTALL_INSTRUCTIONS.md` - How to install in Teams

## Troubleshooting

**Bot doesn't respond:**
- Check bot server is running: `python bot_server.py`
- Verify ngrok is running and URL is configured in Azure
- Check logs for authentication errors

**401 Authentication error:**
- Verify `MICROSOFT_APP_PASSWORD` is set correctly in `.env`
- Ensure tenant ID is configured
- Check app registration in Microsoft Entra ID

**Langflow connection failed:**
- Verify `LANGFLOW_URL` is accessible from bot server
- Check `LANGFLOW_FLOW_ID` is correct
- Ensure `LANGFLOW_API_KEY` is set if required

**Can't install Teams app:**
- Check app package has all required files (manifest.json, icons)
- Verify manifest.json bot ID matches your Azure bot's App ID
- Try uploading to "Apps for [Your Team]" if org-wide upload is restricted

## Development

### Testing Locally

1. Start bot server: `python bot_server.py`
2. Start ngrok: `ngrok http 3978`
3. Update Azure messaging endpoint with ngrok URL
4. Test in Teams or Azure Bot "Test in Web Chat"

### Production Deployment

For production, deploy `bot_server.py` to:
- Azure App Service
- AWS EC2/Lambda
- Google Cloud Run
- Any hosting service that supports Python/Flask

Replace ngrok URL with your production URL in Azure bot configuration.

## Cost

- Azure Bot Service: **FREE** (up to 10,000 messages/month)
- Langflow: **FREE** (self-hosted)
- ngrok: **FREE** (for development)
- Teams: **FREE** (part of Microsoft 365)

Total cost: **$0/month** for typical usage!

## Why This Approach?

- **Interactive** - Two-way conversations, not just notifications
- **AI-Powered** - Integrates with your Langflow workflows
- **Scalable** - Azure Bot Service handles the infrastructure
- **Free** - No costs for typical usage
- **Professional** - Uses official Microsoft Bot Framework

## Need Help?

1. Check `TEAMS_BOT_SETUP.md` for setup instructions
2. Verify all credentials in `.env` are correct
3. Test bot in Azure "Test in Web Chat" first before Teams
4. Check bot server logs for error messages

Happy chatting with your AI bot! 🤖
