# SIMPLEST Teams Setup - NO Power Automate Needed!

## Use Teams Incoming Webhook (100% FREE!)

### Step 1: Create Incoming Webhook in Teams

1. **Go to your Teams channel** (Sok Eng Team → SE Team)
2. **Click the "..." next to the channel name**
3. **Select "Connectors" or "Workflows"**
4. **Find "Incoming Webhook"**
5. **Click "Add" or "Configure"**
6. **Give it a name:** "Langflow Bot"
7. **Click "Create"**
8. **COPY THE WEBHOOK URL** (looks like: `https://...webhook.office.com/webhookb2/...`)

### Step 2: Update `.env` file

Replace your current `TEAMS_WEBHOOK_URL` with the new Incoming Webhook URL:

```env
TEAMS_WEBHOOK_URL=https://your-org.webhook.office.com/webhookb2/...
```

### Step 3: Use the Simple MCP Server

Run `mcp_server.py` (the original one):

```bash
python mcp_server.py
```

This sends messages in the format:
```json
{"text": "your message"}
```

Which is EXACTLY what Teams Incoming Webhook expects!

### Step 4: Test

```bash
curl -X POST http://localhost:5000/test \
  -H "Authorization: Bearer langflow-teams-secret-123456" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello from Langflow!"}'
```

### Step 5: Update Langflow Component

Use `langflow_component_final.py` - it's already configured correctly!

---

## Why This Works

- **Teams Incoming Webhook** is FREE and accepts simple JSON `{"text": "..."}`
- **No Power Automate Premium** required
- **No complex Bot Framework format** needed
- **Works with your existing MCP server** (`mcp_server.py`)

---

## Comparison

| Method | Cost | Complexity | Works? |
|--------|------|------------|--------|
| Incoming Webhook | FREE | Easy | ✅ YES |
| Power Automate HTTP Request | PAID | Easy | ❌ Premium required |
| Power Automate Teams Webhook | FREE | Hard | ❌ Bot Framework format |

**Use Incoming Webhook!** It's the simplest and FREE!
