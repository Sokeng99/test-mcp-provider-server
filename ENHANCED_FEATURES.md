# Enhanced Teams Message Features

Your MCP Teams Webhook server now supports **rich formatted messages** with Adaptive Cards! 🎉

## New Features

### 1. **Simple Text Messages** (Original)
Basic text messages - perfect for quick notifications.

```python
{
    "name": "send_teams_message",
    "arguments": {
        "message": "Hello from Langflow!"
    }
}
```

### 2. **Adaptive Cards** (NEW! ✨)
Rich formatted cards with priority levels, facts, images, and metadata.

**Features:**
- 🎨 Priority-based color coding (urgent, high, normal, low)
- 📊 Display facts/metadata as key-value pairs
- 🖼️ Embed images
- 👤 Include sender information
- ⏰ Automatic timestamps

**Example:**
```python
{
    "name": "send_adaptive_card",
    "arguments": {
        "title": "Deployment Status",
        "message": "Your app has been deployed to production successfully!",
        "priority": "high",
        "facts": {
            "Environment": "Production",
            "Version": "v2.5.1",
            "Status": "Running",
            "Uptime": "99.9%"
        },
        "image_url": "https://example.com/chart.png",
        "sender": "CI/CD Pipeline"
    }
}
```

### 3. **Notifications with Actions** (NEW! ✨)
Notification-style messages with optional action buttons.

**Features:**
- 🔘 Clickable action buttons
- 🔗 Link to external resources
- 📢 Perfect for alerts and notifications

**Example:**
```python
{
    "name": "send_notification",
    "arguments": {
        "title": "Pull Request Ready",
        "message": "PR #456 needs your review",
        "priority": "high",
        "action_url": "https://github.com/yourrepo/pull/456",
        "action_text": "Review Now"
    }
}
```

## Priority Levels

Each priority level has a unique visual indicator:

| Priority | Icon | Color | Use Case |
|----------|------|-------|----------|
| `urgent` | 🚨 | Red | Critical errors, immediate attention needed |
| `high` | ⚠️ | Yellow | Important updates, warnings |
| `normal` | ℹ️ | Green | Standard notifications |
| `low` | 📝 | Gray | Informational messages |

## Usage in Langflow

### Method 1: Using MCP Tools Component

1. Add **MCP Tools** component to your flow
2. Select **teams_webhook** as MCP Server
3. Choose your tool:
   - `send_teams_message` - Simple text
   - `send_adaptive_card` - Rich formatted card
   - `send_notification` - Notification with action
4. Configure the parameters
5. Connect and run!

### Method 2: Using Custom Components

Use the enhanced Langflow components in `langflow_enhanced_component.py`:

**Option A: All-in-One Component**
- `EnhancedTeamsMessageSender` - Dropdown to select message type

**Option B: Dedicated Components**
- `SimpleTeamsMessage` - Quick simple messages
- `AdaptiveCardMessage` - Dedicated adaptive card component

## Real-World Examples

### 1. Error Alert
```json
{
    "name": "send_adaptive_card",
    "arguments": {
        "title": "🔴 Critical Error",
        "message": "Database connection pool exhausted",
        "priority": "urgent",
        "facts": {
            "Error Code": "DB_CONN_POOL_EXHAUSTED",
            "Service": "API Gateway",
            "Affected Users": "~500"
        },
        "sender": "Error Monitoring"
    }
}
```

### 2. Success Notification
```json
{
    "name": "send_notification",
    "arguments": {
        "title": "✅ Backup Complete",
        "message": "All databases backed up successfully",
        "priority": "low",
        "action_url": "https://backup-dashboard.example.com",
        "action_text": "View Report"
    }
}
```

### 3. Weekly Report
```json
{
    "name": "send_adaptive_card",
    "arguments": {
        "title": "📊 Weekly Summary",
        "message": "Here's your performance summary",
        "priority": "normal",
        "facts": {
            "Total Users": "1,234",
            "New Signups": "+87",
            "Revenue": "$12,345",
            "Week": "Nov 12-19, 2025"
        },
        "sender": "Analytics Dashboard"
    }
}
```

### 4. Build Status with Image
```json
{
    "name": "send_adaptive_card",
    "arguments": {
        "title": "Build #1234 Complete",
        "message": "Your build finished successfully",
        "priority": "normal",
        "image_url": "https://example.com/build-metrics.png",
        "facts": {
            "Duration": "3m 45s",
            "Tests": "125 passed",
            "Coverage": "87%"
        },
        "sender": "CI/CD"
    }
}
```

## Testing

### Quick Test (Command Line)

```bash
# Test simple message
curl -X POST http://localhost:5000/mcp/tools/call \
  -H "Authorization: Bearer langflow-teams-secret-123456" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "send_teams_message",
    "arguments": {"message": "Hello Teams!"}
  }'

# Test adaptive card
curl -X POST http://localhost:5000/mcp/tools/call \
  -H "Authorization: Bearer langflow-teams-secret-123456" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "send_adaptive_card",
    "arguments": {
      "title": "Test Card",
      "message": "This is a test",
      "priority": "normal"
    }
  }'
```

### Comprehensive Test Suite

Run the included test script to test all features:

```bash
python test_enhanced_messages.py
```

This will send 8 different message types to your Teams channel, including:
- Simple text messages
- Cards with different priority levels
- Cards with facts and images
- Notifications with action buttons
- Real-world scenario examples

## API Reference

### send_adaptive_card

**Parameters:**
- `title` (string, required) - Card title
- `message` (string, required) - Main message content
- `priority` (string, optional) - Priority level: "urgent", "high", "normal", "low" (default: "normal")
- `facts` (object, optional) - Key-value pairs to display
- `image_url` (string, optional) - URL of image to include
- `sender` (string, optional) - Sender name/identifier

**Returns:**
```json
{
    "success": true,
    "message": "Adaptive Card sent to Teams successfully",
    "status_code": 200,
    "card_type": "adaptive",
    "priority": "normal"
}
```

### send_notification

**Parameters:**
- `title` (string, required) - Notification title
- `message` (string, required) - Notification message
- `priority` (string, optional) - Priority level (default: "normal")
- `action_url` (string, optional) - URL for action button
- `action_text` (string, optional) - Button text (default: "View Details")

**Returns:**
```json
{
    "success": true,
    "message": "Notification sent to Teams successfully",
    "status_code": 200
}
```

## Tips & Best Practices

1. **Choose the right message type:**
   - Simple text for quick updates
   - Adaptive cards for detailed information
   - Notifications for actionable items

2. **Use priority levels appropriately:**
   - Reserve "urgent" for true emergencies
   - Use "normal" for routine updates
   - "low" for background information

3. **Keep facts concise:**
   - 3-5 facts per card is optimal
   - Use short keys and values
   - Format numbers for readability

4. **Image URLs must be publicly accessible:**
   - Teams needs to fetch the image
   - Use HTTPS URLs
   - Consider image size (max ~1MB)

5. **Test action buttons:**
   - Ensure URLs are valid and accessible
   - Use descriptive button text
   - Consider mobile users

## Troubleshooting

**Cards not displaying properly:**
- Check that your webhook URL is correct
- Verify Power Automate flow is running
- Test with simple message first

**Images not showing:**
- Ensure URL is publicly accessible
- Use HTTPS (not HTTP)
- Check image format (PNG, JPG, GIF)

**Facts not appearing:**
- Verify facts is a valid JSON object
- Check key-value pairs are strings
- Test with fewer facts first

## What's Next?

Consider these enhancements:
- [ ] Add support for multiple Teams channels
- [ ] Message templates library
- [ ] Scheduled messages
- [ ] Message threading
- [ ] Interactive forms
- [ ] Two-way communication
- [ ] Message history/analytics

---

**Happy messaging! 🚀**
