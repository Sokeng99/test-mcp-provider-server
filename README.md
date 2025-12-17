# X-Pilot Teams Bot

AI-powered interactive bot for Microsoft Teams using Azure Bot Service and Langflow. **100% FREE** (Azure Bot Service free tier: 10,000 messages/month).

## Features

- Interactive conversations with Langflow AI in Teams
- **Multi-flow routing** - Automatically routes to different AI flows based on question type
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

# Langflow Configuration - Production
LANGFLOW_URL=https://your-langflow-domain.com
LANGFLOW_API_KEY=your-api-key-here

# Multiple Flow Configuration
# Chat Flow - General conversation
LANGFLOW_CHAT_FLOW_ID=your-chat-flow-id

# Requirement Analysis Flow - Meeting requirements, attendees, etc.
LANGFLOW_REQUIREMENT_FLOW_ID=your-requirement-flow-id
```

**Multi-Flow Routing**: The bot automatically detects the question type and routes to the appropriate Langflow flow:

- **Requirement Analysis Flow** - Triggered by keywords like: `meeting`, `requirement`, `analysis`, `attendees`, `who should join`, `participants`, `stakeholders`, etc.
- **Chat Flow** - Default for general conversation and questions

You can customize the keywords in `teams_bot.py` (see `REQUIREMENT_KEYWORDS` constant).

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

### Multi-Flow Routing Examples

The bot intelligently routes your questions to the appropriate AI flow:

**General Chat Flow** (default):

```
Hello, how are you?
What's the latest on the project?
Can you explain this concept?
```

**Requirement Analysis Flow** (automatically triggered):

```
Who should attend the kickoff meeting?
Analyze the requirements for this feature
What are the meeting requirements?
List the stakeholders for this project
Who needs to be invited to the planning session?
```

The routing is based on keywords like: `meeting`, `requirement`, `analysis`, `attendees`, `participants`, `stakeholders`, etc.

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

**Three deployment options:**

#### Option 1: Docker + Kubernetes (Recommended for Organizations)

Full enterprise deployment with high availability:

- **Kubernetes/Rancher**: See [RANCHER_DEPLOYMENT.md](RANCHER_DEPLOYMENT.md) - Complete walkthrough
- **Kubernetes Guide**: See [KUBERNETES_DEPLOYMENT.md](KUBERNETES_DEPLOYMENT.md) - Detailed K8s concepts
- **CI/CD Pipeline**: See [CI_CD_PIPELINE.md](CI_CD_PIPELINE.md) - Automate deployments
- **Includes**: Docker containerization, staging/production environments, auto-scaling, SSL, monitoring

**Why this approach?**

- ✅ Zero-downtime deployments
- ✅ Auto-scaling based on load
- ✅ Easy rollbacks
- ✅ Professional grade infrastructure
- ✅ Works in any cloud (Azure, AWS, GCP)

#### Option 2: Platform-as-a-Service

Simple deployment to managed services:

- **Azure App Service**: Deploy Flask app directly
- **Google Cloud Run**: Serverless container deployment
- **AWS Lambda**: With Mangum adapter for Flask
- **Heroku**: Easy deployment with Procfile

#### Option 3: Simple VM/Server

Traditional server deployment:

- Deploy `bot_server.py` to any server with Python
- Use systemd or supervisor to keep it running
- Configure reverse proxy (nginx) for SSL

**For Kubernetes deployment, your project includes:**

- `Dockerfile` - Multi-stage optimized build
- `.dockerignore` - Exclude unnecessary files
- `deployment/staging/` - Staging environment configs
- `deployment/production/` - Production environment configs with HPA

Replace ngrok URL with your production URL in Azure bot configuration.

## Docker Build and Push Command
docker build -t registry.smart.com.kh/spa/xpilot-bot:v1.0.2 .
docker push registry.smart.com.kh/spa/xpilot-bot:v1.0.2