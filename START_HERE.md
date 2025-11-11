# MCP Teams Webhook Server - START HERE

Welcome! This guide will get you up and running in 5 minutes.

## What is this?

A server that lets you send messages from **Langflow** (AI workflow tool) to **Microsoft Teams** using the **Model Context Protocol (MCP)**.

```
Langflow → MCP Server → Power Automate → Teams Channel
```

---

## Quick Start (3 Steps)

### Step 1: Configure Your Webhook

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Teams webhook URL:
   ```env
   TEAMS_WEBHOOK_URL=your_power_automate_webhook_url
   MCP_API_KEY=langflow-teams-secret-123456
   ```

**Where to get the webhook URL?**
- Create a Power Automate flow with "When a HTTP request is received" trigger
- Copy the webhook URL from Power Automate

### Step 2: Start the Server

**Windows:**
```bash
start_server.bat
```

**Linux/Mac:**
```bash
chmod +x start_server.sh
./start_server.sh
```

You should see:
```
======================================================================
MCP Teams Webhook Server v3.0 (Langflow Compatible)
======================================================================
 * Running on http://127.0.0.1:5000
```

### Step 3: Test It

```bash
python test_webhook.py
```

You should see:
```
✅ Direct Webhook - PASSED
✅ MCP Endpoints - PASSED
✅ MCP Server - PASSED
🎉 All tests passed! Check your Teams channel for messages.
```

---

## Use with Langflow

### 1. Start Langflow

```bash
docker run -d --name langflow -p 7860:7860 langflowai/langflow:latest
```

Open: http://localhost:7860

### 2. Add MCP Server

In Langflow: **Settings** → **MCP Servers** → **Add MCP Server** → **JSON**

```json
{
  "mcpServers": {
    "teams_webhook": {
      "url": "http://host.docker.internal:5000/mcp/sse",
      "headers": {
        "Authorization": "Bearer langflow-teams-secret-123456"
      },
      "transport": {
        "type": "sse"
      }
    }
  }
}
```

### 3. Create a Flow

1. Add **MCP Tools** component
2. Select **teams_webhook** as MCP Server
3. Select **send_teams_message** as Tool
4. Connect your inputs
5. Run and check Teams!

---

## Project Structure

```
test-mcp/
├── mcp_server_langflow.py    # Main server (use this!)
├── mcp_sse_server.py          # Alternative SSE server
├── .env                       # Your configuration
├── .env.example               # Example configuration
├── requirements.txt           # Python dependencies
├── test_webhook.py            # Test script
├── start_server.bat           # Windows start script
├── start_server.sh            # Linux/Mac start script
├── README.md                  # Full documentation
├── TESTING_GUIDE.md           # Detailed testing guide
└── START_HERE.md              # This file
```

---

## Key Files

### Which Server to Use?

- **`mcp_server_langflow.py`** ← **Use this!**
  - Full MCP protocol with session management
  - Works with Langflow's MCP client
  - Most robust implementation

- **`mcp_sse_server.py`**
  - Simpler SSE implementation
  - May have timeout issues with Langflow
  - Good for learning MCP concepts

### Configuration

- **`.env`** - Your actual config (not committed to git)
- **`.env.example`** - Template to share with others

### Testing

- **`test_webhook.py`** - Automated test suite
- **`TESTING_GUIDE.md`** - Manual testing instructions

---

## Common Issues

### "Connection refused" when testing

**Problem:** MCP server not running

**Solution:**
```bash
python mcp_server_langflow.py
```

### "Error on MCP Server" in Langflow

**Problem:** Langflow can't connect to server

**Solution:**
1. Check server is running: `curl http://localhost:5000/health`
2. Verify Langflow can reach it: `docker exec langflow curl http://host.docker.internal:5000/health`
3. Check API key matches in `.env` and Langflow config

### Messages not appearing in Teams

**Problem:** Webhook URL is wrong or Power Automate flow is disabled

**Solution:**
1. Test webhook directly: `python test_webhook.py`
2. Check Power Automate flow is enabled
3. Verify webhook URL in `.env` file

---

## What's Next?

1. ✅ **You have**: Push notifications from Langflow to Teams
2. 🔧 **You can add**: More tools (polls, get members, schedule messages)
3. 🚀 **You could build**: Two-way chat (requires Azure Bot Framework)

### Adding More Tools

Edit `mcp_server_langflow.py`:

1. Add function (like `send_to_teams()`)
2. Register in `list_tools()` function
3. Handle in `call_tool()` function
4. Restart server
5. Tools appear automatically in Langflow!

This is the power of MCP - extensible and scalable! 🚀

---

## Need Help?

1. **Check logs** - Server prints errors to console
2. **Run tests** - `python test_webhook.py`
3. **Read guides**:
   - `README.md` - Full documentation
   - `TESTING_GUIDE.md` - Step-by-step testing
4. **Check files** - `.env` has correct webhook URL

---

## Success Checklist

- [ ] `.env` file configured with webhook URL
- [ ] Server starts without errors
- [ ] `test_webhook.py` passes all tests
- [ ] Message appears in Teams channel
- [ ] Langflow running at http://localhost:7860
- [ ] MCP server configured in Langflow
- [ ] Can send message from Langflow to Teams

---

**You're all set!** 🎉

Start the server, configure Langflow, and start building AI workflows that notify your team in Microsoft Teams!
