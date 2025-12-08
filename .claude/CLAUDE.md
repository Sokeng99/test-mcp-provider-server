- to memorize

## X-pilot Teams Bot Project

**Project Location:** `C:\Users\Hout Sokeng\Downloads\test-mcp 1\test-mcp`

**Project Goal:** Interactive AI-powered bot for Microsoft Teams using Azure Bot Service and Langflow.

### Current Status (December 2025)

**Completed:**

- ✅ Azure Bot Service configured and working
- ✅ Interactive Teams bot with Langflow AI integration
- ✅ Bot tested successfully in Azure Bot Web Chat
- ✅ Bot connected to Langflow and responding with AI-powered answers
- ✅ Teams app package created: `xpilot-bot-teams-app.zip`
- ✅ Cleaned up MCP-related files (no longer using MCP approach)

**Ready to Use:**

- 📦 Teams app package ready for upload to Microsoft Teams
- 📝 Complete documentation and setup instructions
- 🤖 Bot server ready to run with `python bot_server.py`

**Issues Resolved:**

- ✅ Fixed 401 authentication error (added tenant ID to bot configuration)
- ✅ Fixed 405 error (updated endpoint to accept GET and POST)
- ✅ Fixed Langflow API authentication (added API key support)
- ✅ Updated to use new Langflow /run endpoint (deprecated /process endpoint)
- ✅ Removed all MCP-related code and dependencies

### Project Architecture

**Current Implementation: Azure Bot Service**

```
User in Teams → Azure Bot Service → bot_server.py → Langflow AI → Response back to user
```

- Files: `teams_bot.py`, `bot_server.py`
- Use case: Interactive AI conversations, Q&A, chat with Langflow
- Cost: FREE tier (10,000 messages/month)

### Key Files

**Core Bot Files:**

- `bot_server.py` - Flask server for Azure Bot Service
- `teams_bot.py` - Bot logic with Langflow integration
- `.env` - Configuration (Azure credentials and Langflow settings)
- `requirements.txt` - Python dependencies (Bot Framework SDK, Flask, requests)

**Teams App Package:**

- `teams-app/manifest.json` - Teams app configuration
- `teams-app/color.png` - Bot icon (color version)
- `teams-app/outline.png` - Bot icon (outline version)
- `xpilot-bot-teams-app.zip` - Ready-to-upload Teams app package

**Documentation:**

- `README.md` - Main documentation and quick start guide
- `TEAMS_BOT_SETUP.md` - Complete Azure setup guide (step-by-step)
- `TEAMS_APP_INSTALL_INSTRUCTIONS.md` - How to install bot in Teams

### Environment Configuration (`.env`)

```env
# Azure Bot Service credentials
MICROSOFT_APP_ID=2f1bd833-b2e7-48be-9075-b13623cc9165
MICROSOFT_APP_PASSWORD=<your-client-secret>
MICROSOFT_APP_TENANT_ID=2780a32d-11ce-4c57-bad5-ce0cffc115a3

# Langflow Configuration
LANGFLOW_URL=http://localhost:7860
LANGFLOW_FLOW_ID=<your-flow-id>
LANGFLOW_API_KEY=<your-api-key>
```

### Azure Resources

- **Bot Name:** `xpilot-bot`
- **Resource Group:** `xpilot-rg`
- **App ID:** `2f1bd833-b2e7-48be-9075-b13623cc9165`
- **App Tenant ID:** `2780a32d-11ce-4c57-bad5-ce0cffc115a3`
- **Messaging Endpoint:** Uses ngrok for local dev: `https://<ngrok-url>.ngrok-free.app/api/messages`

### How to Run

1. **Start Langflow** (if not already running):
   ```bash
   docker start langflow
   ```

2. **Start ngrok** (for local development):
   ```bash
   ngrok http 3978
   ```
   Copy the HTTPS URL and update Azure Bot messaging endpoint.

3. **Run bot server**:
   ```bash
   python bot_server.py
   ```
   Bot will start on port 3978 and listen for messages from Teams.

4. **Test in Teams**:
   - Upload `xpilot-bot-teams-app.zip` to Teams (if not already installed)
   - @mention the bot or send direct message
   - Bot responds with Langflow AI

### Technology Stack

- **Python 3.10+**
- **Flask** - Web framework for bot server
- **Bot Framework SDK** - Microsoft bot integration (`botbuilder-core`, `botbuilder-schema`, `botframework-connector`)
- **Langflow** - AI workflow tool (running on Docker, port 7860)
- **Azure Bot Service** - Teams bot hosting (FREE tier)
- **ngrok** - Local development tunnel (FREE tier)

### Important Context

- User has Azure account and successfully created bot resource
- Bot is fully configured and working in Azure Bot Web Chat
- Teams app package is ready for installation
- All code is production-ready
- **No longer using MCP approach** - switched to direct Azure Bot Service integration
- MCP-related files have been cleaned up and removed

### User Preferences

- Prefers simple, working solutions
- Values FREE tier options
- Wants to integrate X-pilot AI (Langflow) with Teams for team collaboration
- Interactive bot for conversations and Q&A

### Common Tasks

**Starting the bot:**
```bash
python bot_server.py
```

**Testing the bot:**
- Azure Portal → Bot Resource → Test in Web Chat
- Or @mention in Teams after installing app

**Updating Langflow flow:**
- Change `LANGFLOW_FLOW_ID` in `.env`
- Restart `bot_server.py`

**Deploying to production:**
- Deploy `bot_server.py` to Azure App Service, AWS, or other hosting
- Update Azure Bot messaging endpoint with production URL
- No longer need ngrok in production

### Troubleshooting

**Bot not responding:**
- Check `bot_server.py` is running
- Verify ngrok is running and URL is updated in Azure
- Check `.env` has all credentials set

**401 Authentication error:**
- Verify `MICROSOFT_APP_PASSWORD` is correct in `.env`
- Check `MICROSOFT_APP_TENANT_ID` is set
- Regenerate client secret in Microsoft Entra ID if needed

**Langflow connection error:**
- Verify Langflow is running: `docker ps | grep langflow`
- Check `LANGFLOW_URL` is accessible
- Verify `LANGFLOW_FLOW_ID` exists in Langflow

**Key Files to Reference:**

- `README.md` - Quick start and overview
- `TEAMS_BOT_SETUP.md` - Complete Azure setup instructions
- `TEAMS_APP_INSTALL_INSTRUCTIONS.md` - How to install in Teams
- `.env` - Configuration (credentials)
