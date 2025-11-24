# MCP Teams Server

Simple MCP server to send messages from Langflow to Microsoft Teams. **100% FREE** - no premium features required!

## Features

- ✅ Send text messages to Teams
- ✅ Send rich Adaptive Cards with formatting
- ✅ Send images from local files
- ✅ Full MCP protocol support for Langflow
- ✅ Optional two-way communication with n8n

## Quick Setup (5 minutes)

### 1. Get Teams Incoming Webhook URL

1. In Microsoft Teams, go to your channel
2. Click **...** → **Connectors** → **Incoming Webhook**
3. Click **Add** → **Configure**
4. Name: `Langflow Bot`
5. Click **Create** and **copy the webhook URL**

### 2. Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit .env and paste your webhook URL
TEAMS_WEBHOOK_URL=https://your-org.webhook.office.com/webhookb2/...
MCP_API_KEY=langflow-teams-secret-123456
```

### 3. Install & Run

```bash
# Install dependencies
pip install -r requirements.txt

# Start server
python mcp_server.py
```

You should see:
```
======================================================================
MCP Teams Server v1.0 - Simple & FREE!
======================================================================
Webhook: ✓ Configured
```

### 4. Test It

```bash
curl -X POST http://localhost:5000/test \
  -H "Authorization: Bearer langflow-teams-secret-123456" \
  -H "Content-Type: application/json" \
  -d '{"message": "🎉 Hello from MCP!"}'
```

Check your Teams channel - you should see the message!

### 5. Connect to Langflow

In Langflow: **Settings** → **MCP Servers** → **Add Server**

```json
{
  "mcpServers": {
    "teams": {
      "url": "http://host.docker.internal:5000/mcp/sse",
      "headers": {
        "Authorization": "Bearer langflow-teams-secret-123456"
      },
      "transport": {"type": "sse"}
    }
  }
}
```

Now use **MCP Tools** component in your flows!

## Available Tools

### `send_teams_message`
Send simple text message to Teams.

```python
{
  "message": "Hello from Langflow!"
}
```

### `send_adaptive_card`
Send rich formatted card with icons and facts.

```python
{
  "title": "Status Update",
  "message": "Workflow completed successfully",
  "priority": "high",  # urgent, high, normal, low
  "facts": {
    "Status": "Complete",
    "Duration": "2.5s"
  }
}
```

### `send_teams_image`
Send image from your local computer.

```python
{
  "file_path": "C:\\path\\to\\image.png",
  "caption": "Generated chart"
}
```

### `get_teams_messages`
Get messages sent from Teams (requires n8n setup - see below).

## Two-Way Communication (Optional)

To receive messages FROM Teams, use **n8n** (free, open-source automation):

### Option 1: Using n8n (Recommended - FREE!)

#### Install n8n:
```bash
# Using Docker
docker run -it --rm --name n8n -p 5678:5678 -v ~/.n8n:/home/node/.n8n n8nio/n8n

# Or using npm
npm install -g n8n
n8n
```

#### Create Workflow in n8n:

1. Go to http://localhost:5678
2. Create new workflow:

**Trigger Node:**
- Type: **Webhook**
- Method: POST
- Path: `teams-incoming`

**HTTP Request Node:**
- Method: POST
- URL: `http://localhost:5000/teams/incoming`
- Body:
  ```json
  {
    "text": "{{ $json.body.text }}",
    "user": "{{ $json.body.user }}"
  }
  ```

3. Activate workflow
4. Copy the webhook URL
5. Use this URL in Teams Incoming Webhook or external trigger

### Option 2: Python Polling (Simpler but less real-time)

Create a Langflow component that polls Teams every 30 seconds using Microsoft Graph API. No external tools needed, but requires Graph API permissions.

## Architecture

### One-Way (Default):
```
Langflow → MCP Server → Teams Incoming Webhook → Teams Channel
```

### Two-Way (with n8n):
```
Teams → n8n → MCP Server → Langflow
Langflow → MCP Server → Teams Incoming Webhook → Teams
```

## Troubleshooting

**"TEAMS_WEBHOOK_URL not configured"**
- Make sure webhook URL is in `.env` file
- Restart the server after editing `.env`

**Messages not appearing in Teams:**
- Test webhook URL directly with curl
- Check Teams connector is still configured
- Webhook URLs can expire - create a new one

**Server won't start:**
- Check port 5000: `netstat -ano | findstr :5000`
- Try different port: edit `app.run()` in `mcp_server.py`

**Langflow can't connect:**
- Verify server is running: `curl http://localhost:5000/health`
- Check API key matches in both places
- Use `host.docker.internal` not `localhost` in Langflow

## Files

- `mcp_server.py` - **Main server** (use this!)
- `mcp_sse_server.py` - Alternative simpler version
- `.env` - Your configuration
- `test_webhook.py` - Test scripts

## Why This Approach?

✅ **Free** - Teams Incoming Webhook is free for everyone
✅ **Simple** - No Azure, no premium Power Automate needed
✅ **Works** - Uses standard Teams features available everywhere
✅ **Flexible** - Add n8n for two-way communication if needed

## Need Help?

- Test individual endpoints: `curl http://localhost:5000/health`
- Check server logs for errors
- Verify webhook URL in Teams connector settings
- Make sure `.env` file exists and has correct values

Happy automating! 🚀
