# Simple Power Automate Flow Setup

## Create a new flow with these steps:

### Step 1: Trigger
- **When a HTTP request is received**
- Request Body JSON Schema: (leave empty or use this)
```json
{
    "type": "object",
    "properties": {
        "text": {
            "type": "string"
        }
    }
}
```

### Step 2: Post message in Teams
- **Post message in a chat or channel**
- Post as: Flow bot
- Post in: Channel
- Team: (Select your team)
- Channel: (Select your channel)
- Message: `@{triggerBody()?['text']}`

That's it! Just 2 steps.

## After creating the flow:
1. Copy the HTTP POST URL from Step 1
2. Save it to your `.env` file as `TEAMS_WEBHOOK_URL=<your-url>`
3. Restart the MCP server
4. Test with: `curl -X POST http://localhost:5000/mcp/tools/call -H "Authorization: Bearer langflow-teams-secret-123456" -H "Content-Type: application/json" -d "{\"name\": \"send_teams_message\", \"arguments\": {\"message\": \"Hello from MCP!\"}}"
