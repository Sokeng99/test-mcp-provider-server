# Teams Bot Setup Guide - X-pilot

Complete guide to set up an interactive Teams bot powered by Langflow AI.

## Architecture

```
User in Teams → Azure Bot Service → Your Bot Server (bot_server.py) → Langflow AI → Response
```

---

## Prerequisites

- Microsoft Azure account (FREE tier available!)
- Ngrok or similar tunneling tool (for local development)
- Your Langflow instance running (http://localhost:7860)

---

## Part 1: Azure Bot Service Setup (One-time, 15 minutes)

### Step 1: Create Azure Bot Resource

1. **Go to Azure Portal:** https://portal.azure.com
2. **Click "Create a resource"**
3. **Search for:** "Azure Bot"
4. **Click "Create"**

### Step 2: Configure Bot

**Basics:**
- **Bot handle:** `xpilot-bot` (or your choice, must be unique)
- **Subscription:** Your Azure subscription
- **Resource group:** Create new `xpilot-rg`
- **Pricing tier:** **F0 (FREE)** - 10,000 messages/month
- **Microsoft App ID:** Create new → Create new Microsoft App ID

**Click "Create"**

### Step 3: Get App Credentials

1. After deployment, **go to your bot resource**
2. **Click "Configuration"** in left menu
3. **Click "Manage"** next to Microsoft App ID
4. **Click "Certificates & secrets"**
5. **Click "New client secret"**
   - Description: `xpilot-secret`
   - Expires: 24 months
6. **COPY THE SECRET VALUE** immediately (you can't see it again!)
7. **Go back** and **copy the Application (client) ID**

**Save these:**
```
MICROSOFT_APP_ID=2f1bd833-b2e7-48be-9075-b13623cc9165
MICROSOFT_APP_PASSWORD=EjJ8Q~JAYn-b063yVYYKTbl34t2FZko9saB.hagx
MICROSOFT_APP_PASSWORD=<your-secret-value>
```

---

## Part 2: Local Bot Setup (5 minutes)

### Step 1: Update `.env` File

Add to your `.env` file:

```env
# Teams Bot Configuration
MICROSOFT_APP_ID=your-app-id-here
MICROSOFT_APP_PASSWORD=your-app-password-here

# Langflow Configuration (optional)
LANGFLOW_URL=http://localhost:7860
LANGFLOW_FLOW_ID=your-flow-id-here
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Install Ngrok

**Download:** https://ngrok.com/download

**Or with winget:**
```bash
winget install --id=Ngrok.Ngrok -e
```

---

## Part 3: Run the Bot (2 minutes)

### Step 1: Start Ngrok

```bash
ngrok http 3978
```

**Copy the HTTPS URL** (looks like: `https://abc123.ngrok-free.app`)

### Step 2: Configure Azure Bot Messaging Endpoint

1. **Go to Azure Portal** → Your bot resource
2. **Click "Configuration"**
3. **Set Messaging endpoint:** `https://your-ngrok-url.ngrok-free.app/api/messages`

https://mythoclastic-consecrative-regena.ngrok-free.dev/api/messages

4. **Click "Apply"**

### Step 3: Start Bot Server

```bash
python bot_server.py
```

You should see:
```
======================================================================
X-pilot Teams Bot Server
======================================================================
App ID: <your-app-id>...
======================================================================

Endpoints:
  http://localhost:3978/api/messages  (Bot endpoint)
  http://localhost:3978/health        (Health check)

Bot is ready! Configure in Azure Bot Service.
======================================================================
```

---

## Part 4: Add Bot to Teams (2 minutes)

### Step 1: Test in Web Chat

1. **In Azure Portal** → Your bot
2. **Click "Test in Web Chat"** in left menu
3. **Type a message**
4. **Bot should respond!**

### Step 2: Add to Teams

1. **In Azure Portal** → Your bot
2. **Click "Channels"**
3. **Click "Microsoft Teams"** icon
4. **Click "Apply"**
5. **Click "Open in Teams"**

### Step 3: Chat with Bot

1. **Bot opens in Teams**
2. **Type:** `Hello!`
3. **Bot responds!**

---

## Part 5: Connect to Langflow (Optional, 5 minutes)

### Step 1: Get Langflow Flow ID

1. **Open Langflow:** http://localhost:7860
2. **Open your AI flow**
3. **Copy the Flow ID** from the URL (after `/flow/`)

### Step 2: Update `.env`

```env
LANGFLOW_FLOW_ID=your-flow-id-here
```

### Step 3: Restart Bot

```bash
# Stop bot_server.py (Ctrl+C)
python bot_server.py
```

**Now the bot uses Langflow AI for responses!**

---

## Testing

**In Teams, type:**
- `Hello` → Bot greets you
- `What can you do?` → Bot responds with AI answer (if Langflow connected)
- Any question → Bot processes via Langflow and responds

---

## Troubleshooting

### "401 Unauthorized"
- Check MICROSOFT_APP_ID and MICROSOFT_APP_PASSWORD in `.env`
- Verify they match Azure Bot configuration

### "Bot not responding"
- Check ngrok is running
- Verify messaging endpoint in Azure matches ngrok URL
- Check bot_server.py logs

### "Langflow not working"
- Verify LANGFLOW_URL and LANGFLOW_FLOW_ID
- Make sure Langflow is running on port 7860
- Check Langflow flow is deployed

---

## Production Deployment

For production (not using ngrok):

1. **Deploy bot_server.py** to:
   - Azure App Service
   - Heroku
   - Your own server

2. **Update Azure Bot messaging endpoint** to your production URL

3. **Remove ngrok** dependency

---

## Cost Breakdown

| Service | Free Tier | Paid |
|---------|-----------|------|
| Azure Bot Service | ✅ 10,000 msg/month | After 10k messages |
| Langflow (self-hosted) | ✅ FREE | - |
| Ngrok (dev only) | ✅ FREE | - |

**Total for development: FREE!**

---

## What You Get

✅ **Interactive Teams bot** - users can @mention and chat
✅ **AI-powered responses** - via Langflow
✅ **Two-way conversations** - not just notifications
✅ **Free tier** - 10,000 messages/month
✅ **Easy to extend** - add more Langflow flows

---

## Files Created

- `teams_bot.py` - Bot logic and Langflow integration
- `bot_server.py` - Flask server for Azure Bot Service
- `requirements.txt` - Updated with bot dependencies
- `TEAMS_BOT_SETUP.md` - This guide

## Next Steps

1. Complete Azure setup (Parts 1-4)
2. Test bot in Teams
3. Connect Langflow (Part 5)
4. Customize bot responses in `teams_bot.py`
5. Deploy to production!

---

**Need help?** Check Azure Bot Service docs: https://docs.microsoft.com/en-us/azure/bot-service/
