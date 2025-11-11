# MCP Teams Webhook Server

Send messages from Langflow to Microsoft Teams using the Model Context Protocol (MCP).

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Server

```bash
python mcp_server_langflow.py
```

You should see:
```
======================================================================
MCP Teams Webhook Server v3.0 (Langflow Compatible)
======================================================================
 * Running on http://127.0.0.1:5000
```

### 3. Configure Langflow

In Langflow: **Settings** → **MCP Servers** → **Add MCP Server** → **JSON tab**

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

### 4. Use in Langflow

1. Add **MCP Tools** component to your flow
2. Select **teams_webhook** as MCP Server
3. Select **send_teams_message** as Tool
4. Connect your inputs and run!

## Configuration

Edit `.env` file:

```env
TEAMS_WEBHOOK_URL=your_power_automate_webhook_url
MCP_API_KEY=your_secret_api_key
```

## Test the Server

```bash
# Health check
curl http://localhost:5000/health

# Send test message
curl -X POST http://localhost:5000/test \
  -H "Authorization: Bearer langflow-teams-secret-123456" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello from MCP!"}'
```

## Features

- ✅ Full MCP protocol support
- ✅ SSE (Server-Sent Events) transport
- ✅ Session management
- ✅ Bidirectional communication
- ✅ Auto-discovery of tools in Langflow
- ✅ Schema validation

## Architecture

```
Langflow Agent → MCP Protocol (SSE) → MCP Server → Power Automate → Teams
```

This is a **push-only notification system**:
- Sends messages FROM Langflow TO Teams
- Does not receive messages from Teams
- Perfect for: alerts, notifications, status updates

## Troubleshooting

**Server won't start:**
- Check if port 5000 is already in use: `netstat -ano | findstr :5000`

**Langflow shows "Error on MCP Server":**
- Verify server is running: `curl http://localhost:5000/health`
- Check API key matches in both server and Langflow config
- Restart Langflow container: `docker restart langflow`

**Messages not reaching Teams:**
- Test Power Automate webhook directly
- Check webhook URL in `.env` file
- Verify Power Automate flow is enabled

## Endpoints

- `GET /health` - Health check
- `GET /mcp/info` - Server information
- `GET /mcp/sse` - SSE stream for MCP protocol
- `POST /mcp/tools/list` - List available tools
- `POST /mcp/tools/call` - Execute a tool
- `POST /test` - Simple test endpoint

## Next Steps

Want to add more features? Simply:
1. Add new functions to the server
2. Register them in `list_tools()` function
3. They automatically appear in Langflow!

This is the power of MCP - extensible and scalable! 🚀
