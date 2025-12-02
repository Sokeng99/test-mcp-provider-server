# Quick Start - Send Messages to Teams

## Simple Python Script (No Langflow, No MCP)

### Setup (One Time)

1. **Get Teams Incoming Webhook URL:**
   - Go to your Teams channel
   - Click ... → Connectors → Incoming Webhook → Configure
   - Name it "Bot" and create
   - Copy the webhook URL

2. **Update `.env` file:**
   ```env
   TEAMS_WEBHOOK_URL=https://your-webhook-url-here
   ```

### Usage

**Send a message:**
```python
from send_to_teams import send_to_teams

# Simple message
send_to_teams("Hello Teams!")

# Message with title
send_to_teams(
    message="This is the message body",
    title="Notification Title"
)
```

**Run the test:**
```bash
python send_to_teams.py
```

That's it! Check your Teams channel for the message.

## Files

- `send_to_teams.py` - Simple script to send messages to Teams
- `.env` - Your configuration (webhook URL)
- `QUICKSTART.md` - This file

## Complete Example

```python
from send_to_teams import send_to_teams

result = send_to_teams(
    message="Task completed successfully!",
    title="Build Status"
)

if result["success"]:
    print("Message sent!")
else:
    print(f"Error: {result['error']}")
```

Done!
