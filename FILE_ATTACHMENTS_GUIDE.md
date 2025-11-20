# Adding File Attachments to Teams Messages

## The Challenge

Webhooks (both simple and Adaptive Cards) can only send JSON data, not binary files like PDFs or images.

## Solutions

### **Solution 1: Upload Files to Cloud Storage + Send Link** (Recommended)

This is the most common approach:

#### Step 1: Upload File to SharePoint/OneDrive

Add this to your Power Automate flow:

```
1. When a HTTP request is received
   ↓
2. Create file (SharePoint/OneDrive)
   - File Content: @{triggerBody()?['file_content']} (base64)
   - File Name: @{triggerBody()?['file_name']}
   ↓
3. Create sharing link (SharePoint/OneDrive)
   - File: (output from step 2)
   - Link type: View
   ↓
4. Post message in chat or channel
   - Message: "New file uploaded: @{triggerBody()?['message']}\n\nView file: @{outputs('Create_sharing_link')?['body/webUrl']}"
```

#### Step 2: Send file data from MCP server

Your server would need to:
1. Read the file
2. Convert to base64
3. Send in webhook payload

**Example Server Code:**
```python
import base64

def send_message_with_file(message: str, file_path: str) -> dict:
    """Send message with file attachment"""
    try:
        # Read file and convert to base64
        with open(file_path, 'rb') as f:
            file_content = base64.b64encode(f.read()).decode('utf-8')

        file_name = os.path.basename(file_path)

        payload = {
            "message": message,
            "file_name": file_name,
            "file_content": file_content,
            "file_type": file_path.split('.')[-1]
        }

        response = requests.post(TEAMS_WEBHOOK_URL, json=payload, headers=headers)
        return {"success": True, "message": "File sent"}
    except Exception as e:
        return {"success": False, "message": str(e)}
```

---

### **Solution 2: Use Image URLs** (For Images Only - Simple!)

If your images are already hosted somewhere (web server, cloud storage, etc.):

#### For Simple Server (Option 1):

```python
def send_message_with_image(message: str, image_url: str) -> dict:
    """Send message with image URL - Teams will render it"""
    formatted_message = f"{message}\n\n![Image]({image_url})"

    payload = {"text": formatted_message}
    response = requests.post(TEAMS_WEBHOOK_URL, json=payload)
    return {"success": True}
```

#### For Adaptive Cards (Option 2):

Already implemented! Use the `image_url` parameter:

```python
# This already works in mcp_server_langflow.py
send_adaptive_card(
    title="Status Update",
    message="Here's the chart",
    image_url="https://example.com/chart.png"
)
```

---

### **Solution 3: Upload to SharePoint First, Then Notify** (Most Reliable)

Create a two-step process:

**Step 1: Upload endpoint in your MCP server**
```python
@app.route("/upload_file", methods=["POST"])
def upload_file():
    """Upload file to SharePoint via Power Automate"""
    # This triggers a different Power Automate flow
    # that handles file uploads
    file_data = request.files.get('file')

    # Send to SharePoint upload webhook
    sharepoint_webhook = os.getenv("SHAREPOINT_UPLOAD_WEBHOOK")
    # ... upload logic ...

    return jsonify({"file_url": sharepoint_file_url})
```

**Step 2: Send Teams notification with file link**
```python
# After upload completes, send Teams message
send_message_with_file_link(
    message="New report available",
    file_url=sharepoint_file_url,
    file_name="report.pdf"
)
```

**Power Automate Flow for File Upload:**
```
Flow 1: Upload to SharePoint
├─ When HTTP request received (with file data)
├─ Create file in SharePoint
├─ Create sharing link
└─ Respond with file URL

Flow 2: Notify Teams (your current flow)
├─ When HTTP request received (with message + file URL)
└─ Post message with file link
```

---

### **Solution 4: Microsoft Graph API** (Advanced - Full Control)

For complete control over file attachments, use Microsoft Graph API:

**Features:**
- Direct file attachments to Teams messages
- Upload files to Teams channel files tab
- Full Teams integration

**Complexity:** High - requires Azure AD app registration, authentication, etc.

**Example:**
```python
import requests

def post_with_attachment_graph(channel_id: str, message: str, file_path: str):
    """Post Teams message with file attachment using Graph API"""

    # 1. Get access token (OAuth)
    token = get_oauth_token()

    # 2. Upload file to Teams channel
    headers = {"Authorization": f"Bearer {token}"}

    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(
            f"https://graph.microsoft.com/v1.0/teams/{team_id}/channels/{channel_id}/messages",
            headers=headers,
            json={
                "body": {
                    "content": message
                },
                "attachments": [{
                    "name": os.path.basename(file_path),
                    "contentType": "reference",
                    "contentUrl": file_url
                }]
            }
        )

    return response.json()
```

---

## Quick Comparison

| Method | Images | PDFs | Complexity | Works with Your Setup |
|--------|--------|------|------------|----------------------|
| **Image URLs** | ✅ | ❌ | Low | ✅ Yes (both options) |
| **SharePoint + Link** | ✅ | ✅ | Medium | ✅ Yes (need to update PA) |
| **Base64 in webhook** | ✅ | ✅ | Medium | ⚠️ Need to update PA flow |
| **Graph API** | ✅ | ✅ | High | ❌ Need complete rebuild |

---

## Recommended Approach for You

### **For Images:**
Use **Option 2 (Adaptive Cards) + Image URLs**

1. Host your images somewhere accessible (imgur, your web server, cloud storage)
2. Use the existing `send_adaptive_card` with `image_url` parameter
3. Already implemented! Just provide the URL

### **For PDFs/Files:**
Use **SharePoint + Link approach**

1. Update Power Automate to handle file uploads
2. Add MCP server endpoint to upload files first
3. Send Teams notification with file link

---

## Example: Complete File Upload Flow

```python
# In your MCP server

def send_notification_with_file(title: str, message: str,
                                file_path: str = None) -> dict:
    """Send notification with optional file"""

    if file_path:
        # Step 1: Upload file to SharePoint (separate webhook)
        file_url = upload_to_sharepoint(file_path)

        # Step 2: Send Teams message with file link
        formatted_message = f"{message}\n\n📎 Attached: [{os.path.basename(file_path)}]({file_url})"
    else:
        formatted_message = message

    return send_formatted_message(title, formatted_message, "normal")


def upload_to_sharepoint(file_path: str) -> str:
    """Upload file to SharePoint via separate Power Automate flow"""

    sharepoint_webhook = os.getenv("SHAREPOINT_UPLOAD_WEBHOOK")

    with open(file_path, 'rb') as f:
        file_content = base64.b64encode(f.read()).decode('utf-8')

    payload = {
        "file_name": os.path.basename(file_path),
        "file_content": file_content,
        "folder_path": "/Shared Documents/Uploads"
    }

    response = requests.post(sharepoint_webhook, json=payload)
    result = response.json()

    return result.get('file_url')  # SharePoint link returned by PA
```

---

## What to Do Next?

**For your use case, I recommend:**

1. **Images only?** → Use Option 2 (Adaptive Cards) with `image_url`
   - Already implemented!
   - Just provide public image URLs

2. **Need PDF attachments?** → Set up SharePoint upload flow
   - Create second Power Automate flow for file uploads
   - Add upload endpoint to MCP server
   - Send Teams notification with file link

**Which scenario applies to you?**
- Just images? (Easy - already works!)
- Need PDFs/files too? (Medium - need SharePoint setup)
