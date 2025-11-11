# MCP Teams Server Testing Guide

## Quick Start (3 Steps)

### 1. Start the Server

**Windows:**
```bash
start_server.bat
```

**Linux/Mac:**
```bash
chmod +x start_server.sh
./start_server.sh
```

**Or manually:**
```bash
python mcp_server_langflow.py
```

### 2. Test the Server

```bash
# Health check
curl http://localhost:5000/health

# Send test message
curl -X POST http://localhost:5000/test \
  -H "Authorization: Bearer langflow-teams-secret-123456" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"Test from local server\"}"
```

### 3. Configure Langflow

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

---

## Complete Testing Instructions

### Prerequisites

- Python 3.9+
- Docker Desktop (for Langflow)
- Virtual environment activated
- `.env` file configured

### Step-by-Step Testing

#### 1. Test MCP Server Endpoints

```bash
# Test 1: Health check
curl http://localhost:5000/health
# Expected: {"status": "healthy", ...}

# Test 2: MCP Info
curl http://localhost:5000/mcp/info
# Expected: {"name": "teams-webhook-mcp", ...}

# Test 3: List Tools (requires auth)
curl -H "Authorization: Bearer langflow-teams-secret-123456" \
     http://localhost:5000/mcp/tools/list
# Expected: {"tools": [{"name": "send_teams_message", ...}]}

# Test 4: Send message to Teams
curl -X POST http://localhost:5000/mcp/tools/call \
  -H "Authorization: Bearer langflow-teams-secret-123456" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"send_teams_message\", \"arguments\": {\"message\": \"Hello Teams\"}}"
```

#### 2. Start Langflow

```bash
# Check if container exists
docker ps -a --filter name=langflow

# Start existing container
docker start langflow

# Or create new one
docker run -d --name langflow -p 7860:7860 langflowai/langflow:latest
```

Access Langflow: http://localhost:7860

#### 3. Configure MCP in Langflow

1. Go to **Settings** (gear icon)
2. Click **MCP Servers**
3. Click **Add MCP Server**
4. Switch to **JSON** tab
5. Paste the configuration above
6. Click **Add Server**

#### 4. Create a Test Flow

1. **Create new flow**
2. **Add components:**
   - Chat Input (for your message)
   - MCP Tools (configured with teams_webhook)
   - Chat Output (to see response)

3. **Configure MCP Tools:**
   - MCP Server: `teams_webhook`
   - Tool: `send_teams_message`
   - Connect Chat Input to message parameter

4. **Run the flow** and check Teams!

---

## Troubleshooting

### "Error on MCP Server" in Langflow

**Solution 1: Check server is running**
```bash
curl http://localhost:5000/health
```

**Solution 2: Verify Langflow can reach server**
```bash
docker exec langflow curl http://host.docker.internal:5000/health
```

**Solution 3: Check API key matches**
- Server: Check `.env` file
- Langflow: Check MCP configuration JSON

**Solution 4: Restart everything**
```bash
# Restart MCP server (Ctrl+C then restart)
python mcp_server_langflow.py

# Restart Langflow
docker restart langflow

# Refresh Langflow in browser (F5)
```

### Messages Not Appearing in Teams

1. **Test webhook directly:**
```bash
curl -X POST YOUR_TEAMS_WEBHOOK_URL \
  -H "Content-Type: application/json" \
  -d '{"text": "Direct test"}'
```

2. **Check Power Automate:**
   - Open Power Automate flow
   - Check run history
   - Verify flow is enabled

3. **Verify webhook URL in `.env`**

### Server Won't Start

**Port already in use:**
```bash
# Windows
netstat -ano | findstr :5000

# Linux/Mac
lsof -i :5000
```

**Missing dependencies:**
```bash
pip install -r requirements.txt
```

---

## Using with ngrok (Public Access)

If you need to access the server from outside localhost:

```bash
# Install ngrok: https://ngrok.com/download

# Start tunnel
ngrok http 5000

# Copy the https URL (e.g., https://abc123.ngrok.io)
```

**Update Langflow config:**
```json
{
  "mcpServers": {
    "teams_webhook": {
      "url": "https://your-ngrok-url.ngrok.io/mcp/sse",
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

---

## Testing Checklist

- [ ] MCP server starts without errors
- [ ] Health endpoint responds
- [ ] Can list tools with API key
- [ ] Can send message to Teams via `/test` endpoint
- [ ] Can send message via `/mcp/tools/call`
- [ ] Langflow container is running
- [ ] Langflow can access http://localhost:7860
- [ ] MCP server configured in Langflow
- [ ] MCP Tools component shows `send_teams_message`
- [ ] Can send message from Langflow to Teams
- [ ] Message appears in Teams channel

---

## API Reference

### Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/health` | GET | No | Health check |
| `/mcp/info` | GET | No | Server info |
| `/mcp/sse` | GET | No | SSE stream |
| `/mcp/tools/list` | GET/POST | Yes | List tools |
| `/mcp/tools/call` | POST | Yes | Execute tool |
| `/test` | POST | Yes | Simple test |

### Authentication

All authenticated endpoints require:
```
Authorization: Bearer langflow-teams-secret-123456
```

---

## Next Steps

1. **Add more tools** to the server
2. **Build complex workflows** in Langflow
3. **Set up production deployment**
4. **Add error handling and logging**
5. **Implement rate limiting**

Happy testing! 🚀
