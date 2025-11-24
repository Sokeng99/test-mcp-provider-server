# Langflow Setup: Two-Way Communication with Teams

This guide shows how to set up Langflow flows to receive messages from Teams, process them with your agent, and send responses back.

## Architecture

```
┌──────────┐    ┌────────────────┐    ┌─────────────┐    ┌──────────────┐
│  Teams   │───>│ Power Automate │───>│ MCP Server  │<───│   Langflow   │
│  User    │    │     Flow       │    │  (Queue)    │    │    Agent     │
│          │<───│                │<───│             │───>│              │
└──────────┘    └────────────────┘    └─────────────┘    └──────────────┘

Flow:
1. User sends message in Teams
2. Power Automate forwards to MCP server /teams/incoming
3. MCP server queues the message
4. Langflow polls /teams/poll and gets new messages
5. Langflow agent processes the message
6. Langflow sends response to /teams/respond
7. MCP server sends response to Teams
8. User sees response in Teams
```

## Three Langflow Flow Options

### Option 1: Simple Polling Flow (Recommended for Testing)

**Components:**
1. **Python Code** - Poll for messages
2. **Python Code** - Send response

**Steps:**
1. Add **Python Code** component
2. Paste code from `poll_teams_messages.py`
3. Connect to another **Python Code** component
4. Paste code from `send_response_to_teams.py`
5. Set to run every 5 seconds (using Timer or manual trigger)

### Option 2: Agent Response Flow (Recommended for Production)

**Components:**
```
[Timer/Trigger] → [Python: Poll] → [Conditional] → [Agent] → [Python: Respond]
                                       ↓
                                [Log: No messages]
```

**Setup:**

1. **Timer/Trigger Component**:
   - Runs every 5-10 seconds
   - Triggers the polling

2. **Python Code - Poll**:
```python
import requests

MCP_SERVER = "http://localhost:5000"
API_KEY = "langflow-teams-secret-123456"

response = requests.get(
    f"{MCP_SERVER}/teams/poll",
    headers={"Authorization": f"Bearer {API_KEY}"}
)

result = response.json()

if result.get('count', 0) > 0:
    latest = result['messages'][-1]
    output = {
        "has_message": True,
        "user": latest['user'],
        "text": latest['text'],
        "question": latest['text']  # For agent input
    }
else:
    output = {"has_message": False}

print(output)
```

3. **Conditional Component**:
   - Check if `has_message == True`
   - If yes → continue to Agent
   - If no → end

4. **Agent/LLM Component**:
   - Input: `{question}` from polling component
   - System prompt: "You are a helpful Teams assistant. Answer questions concisely."
   - Output: Agent's response

5. **Python Code - Respond**:
```python
import requests

MCP_SERVER = "http://localhost:5000"
API_KEY = "langflow-teams-secret-123456"

# Get agent response from previous component
agent_response = inputs.get('agent_output', 'No response')

response = requests.post(
    f"{MCP_SERVER}/teams/respond",
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "message": agent_response,
        "type": "text"
    }
)

print(f"Sent to Teams: {response.status_code}")
```

### Option 3: Continuous Listener (Advanced)

Use `complete_flow_example.py` as a standalone script:

```bash
python langflow_two_way/complete_flow_example.py
```

This runs continuously and processes messages in real-time.

## Detailed Step-by-Step: Agent Response Flow

### Step 1: Create New Flow

1. Open Langflow
2. Create new flow: "Teams Q&A Bot"

### Step 2: Add Poll Component

1. Add **Python Code** component
2. Name it: "Poll Teams Messages"
3. Paste this code:

```python
import requests
import json

MCP_SERVER_URL = "http://localhost:5000"
API_KEY = "langflow-teams-secret-123456"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

response = requests.get(
    f"{MCP_SERVER_URL}/teams/poll",
    headers=headers,
    timeout=10
)

result = response.json()

if result.get('count', 0) > 0:
    messages = result.get('messages', [])
    latest = messages[-1]

    output = {
        "has_message": True,
        "user": latest['user'],
        "question": latest['text'],
        "all_messages": messages
    }

    print(f"New message from {latest['user']}: {latest['text']}")
else:
    output = {
        "has_message": False,
        "question": "",
        "user": ""
    }

# Make output available to next component
question = output.get('question', '')
```

4. Set **output variable** to `question`

### Step 3: Add Your Agent

1. Add **Agent** or **LLM** component
2. Connect Poll component's `question` output to Agent's input
3. Configure agent:
   - Model: Your preferred LLM
   - System message: "You are a helpful assistant in Microsoft Teams. Answer questions clearly and concisely."
   - Input: `{question}`

### Step 4: Add Response Component

1. Add **Python Code** component
2. Name it: "Send to Teams"
3. Paste this code:

```python
import requests
import json

MCP_SERVER_URL = "http://localhost:5000"
API_KEY = "langflow-teams-secret-123456"

# Get agent response
agent_response = inputs.get('text', 'No response generated')

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "message": agent_response,
    "type": "text"
}

response = requests.post(
    f"{MCP_SERVER_URL}/teams/respond",
    headers=headers,
    json=payload,
    timeout=10
)

result = response.json()

if result.get('success'):
    print(f"✓ Sent response to Teams: {agent_response[:100]}...")
    output = "Success"
else:
    print(f"✗ Failed to send: {result}")
    output = "Failed"
```

4. Connect Agent output to this component's input

### Step 5: Add Conditional (Optional but Recommended)

To avoid processing empty polls:

1. Add **Conditional** component after Poll
2. Condition: `has_message == True`
3. True branch → Agent
4. False branch → End (or Log)

### Step 6: Add Timer/Scheduler

1. Add **Timer** component (if available)
   OR
2. Use **API Trigger** and call it every 5 seconds
   OR
3. Use external scheduler (cron job):

```bash
# Run every 5 seconds
while true; do
  curl http://localhost:7860/api/v1/run/YOUR_FLOW_ID
  sleep 5
done
```

### Step 7: Test the Flow

1. **Start MCP Server**:
   ```bash
   python mcp_server_langflow.py
   ```

2. **Send test message** to Teams channel

3. **Trigger Langflow flow** (manually or via timer)

4. **Check Teams** for response!

## Example Flows

### Example 1: Simple Echo Bot

```
[Timer: 5s] → [Poll] → [Python: Echo] → [Respond]
```

Echo code:
```python
message = inputs.get('question', '')
response = f"You said: {message}"
```

### Example 2: Summarization Bot

```
[Poll] → [Check if message] → [LLM: Summarize] → [Respond]
```

LLM prompt: "Summarize this in one sentence: {question}"

### Example 3: RAG Q&A Bot

```
[Poll] → [Vector Store: Search] → [LLM: Answer] → [Respond]
                                        ↑
                                   [Context]
```

## Testing Checklist

- [ ] MCP server running
- [ ] Power Automate flow active
- [ ] Langflow flow created
- [ ] Test message sent in Teams
- [ ] Message appears in `/teams/poll`
- [ ] Agent processes message
- [ ] Response sent back to Teams
- [ ] Response appears in Teams channel

## Debugging

### Check if messages are reaching MCP server:

```bash
curl -H "Authorization: Bearer langflow-teams-secret-123456" \
  http://localhost:5000/teams/history
```

### Check message queue:

```bash
curl -H "Authorization: Bearer langflow-teams-secret-123456" \
  http://localhost:5000/teams/poll
```

### Manually send response:

```bash
curl -X POST http://localhost:5000/teams/respond \
  -H "Authorization: Bearer langflow-teams-secret-123456" \
  -H "Content-Type: application/json" \
  -d '{"message": "Test response", "type": "text"}'
```

### Check Langflow logs:

- Look for Python Code component outputs
- Check for connection errors
- Verify API key matches

## Performance Tips

1. **Polling Interval**:
   - Start with 10 seconds
   - Decrease to 5 seconds if responses need to be faster
   - Don't go below 2 seconds (rate limiting)

2. **Message Queue**:
   - MCP server stores last 100 messages
   - Polling clears the queue
   - Old messages are dropped

3. **Agent Timeout**:
   - Set reasonable timeout for agent (30s)
   - Add error handling for slow responses

## Advanced: Webhook Instead of Polling

For instant responses, use webhook instead:

1. Expose Langflow endpoint
2. Configure Power Automate to call Langflow directly
3. Langflow processes and responds immediately

This requires:
- Langflow API endpoint
- Public URL (ngrok, cloudflare tunnel)
- Webhook trigger in Langflow

## Next Steps

1. ✅ Set up basic polling flow
2. ✅ Test with simple responses
3. ✅ Connect your actual agent
4. ⬜ Add error handling
5. ⬜ Add conversation history
6. ⬜ Deploy to production

You now have two-way communication working! 🎉
