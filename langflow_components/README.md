# Langflow Custom Components for Teams File/Image Sending

These custom components allow you to send files and images from your local computer to Microsoft Teams directly from Langflow.

## Components Available

### 1. **Send to Teams** (Recommended - Auto-detect)
- **File**: `send_to_teams.py`
- **Description**: Automatically detects if file is an image or document and uses the appropriate method
- **Icon**: Send icon
- **Use when**: You want a simple all-in-one component

### 2. **Send Teams Image**
- **File**: `send_teams_image.py`
- **Description**: Specifically for sending images (JPG, PNG, GIF, etc.)
- **Icon**: Image icon
- **Use when**: You only work with images

### 3. **Send Teams File**
- **File**: `send_teams_file.py`
- **Description**: For sending any file with metadata and preview
- **Icon**: File icon
- **Use when**: You only work with documents/files

## How to Import Components into Langflow

### Method 1: Via Langflow UI (Recommended)

1. **Open Langflow** in your browser (usually http://localhost:7860)

2. **Create or open a flow**

3. **Add Custom Component**:
   - Click the "**+**" button or search for "**Custom Component**"
   - Drag the "**Custom Component**" onto your canvas

4. **Load the component code**:
   - Click on the Custom Component
   - In the right panel, find the "**Code**" field
   - Click "**Edit Code**" or paste the code directly
   - Copy the ENTIRE content from one of these files:
     - `send_to_teams.py` (recommended)
     - `send_teams_image.py`
     - `send_teams_file.py`
   - Click "**Check & Save**"

5. **Component will appear** with the proper name and inputs!

### Method 2: Via File System

1. **Find your Langflow custom components folder**:
   - Windows: `%USERPROFILE%\.langflow\custom_components\`
   - Linux/Mac: `~/.langflow/custom_components/`

2. **Copy the component files**:
   ```bash
   # Create the directory if it doesn't exist
   mkdir -p ~/.langflow/custom_components/

   # Copy components
   cp send_to_teams.py ~/.langflow/custom_components/
   cp send_teams_image.py ~/.langflow/custom_components/
   cp send_teams_file.py ~/.langflow/custom_components/
   ```

3. **Restart Langflow**:
   ```bash
   langflow run
   ```

4. **Components will appear** in the component sidebar under "Custom"

## Using the Components

### Example Flow 1: Send File from Input

```
[Text Input] → [Send to Teams]
    ↓
File Path: C:\Users\Name\file.pdf
Message: "Here's the report"
```

**Steps**:
1. Add **Text Input** component - set value to your file path
2. Add **Send to Teams** component
3. Connect Text Input output to "file_path" input
4. Set the "Message/Caption" field
5. Run the flow!

### Example Flow 2: Agent Sends Screenshot

```
[Agent] → [Code] → [Send to Teams] → [Teams Channel]
          (saves screenshot)
```

**Use case**: Your agent takes a screenshot and sends it to Teams automatically.

### Example Flow 3: Process File and Send

```
[File Input] → [Process Document] → [Send to Teams]
```

## Component Inputs

### Send to Teams Component

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `file_path` | String | Yes | - | Absolute path to file (e.g., `C:\Users\Name\file.pdf`) |
| `message` | Text | No | "" | Description/caption for the file |
| `mcp_server_url` | String | Yes | `http://localhost:5000` | URL of your MCP server |
| `api_key` | Password | Yes | `langflow-teams-secret-123456` | API key for MCP server |

### Send Teams Image Component

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `file_path` | String | Yes | - | Path to image file |
| `caption` | Text | No | "" | Caption for the image |
| `mcp_server_url` | String | Yes | `http://localhost:5000` | MCP server URL |
| `api_key` | Password | Yes | `langflow-teams-secret-123456` | API key |

### Send Teams File Component

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `file_path` | String | Yes | - | Path to file |
| `description` | Text | No | "" | Description of the file |
| `mcp_server_url` | String | Yes | `http://localhost:5000` | MCP server URL |
| `api_key` | Password | Yes | `langflow-teams-secret-123456` | API key |

## Component Output

All components return a `Data` object with:

```json
{
  "success": true,
  "type": "image" or "file",
  "message": "Image sent successfully",
  "file_path": "C:\\Users\\Name\\image.png",
  "file_size": "245.67 KB",
  "mime_type": "image/png",
  "status_code": 202,
  "tool_used": "send_teams_image"
}
```

Or on error:
```json
{
  "success": false,
  "error": "Error message here",
  "status_code": 400
}
```

## Complete Example Flow

### Send Agent's Response as File

```python
# Flow: Chat → Agent → Save Response → Send to Teams

1. [Chat Input] - User asks question
2. [Agent] - Processes and generates response
3. [Python Code] - Saves response to file
4. [Send to Teams] - Sends the file to Teams channel
```

**Python Code Component**:
```python
import os
from datetime import datetime

# Get the response from agent
response = inputs['agent_response']

# Create filename with timestamp
filename = f"agent_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
filepath = os.path.join(os.getcwd(), filename)

# Write to file
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(response)

# Return filepath to send to Teams
return {"filepath": filepath}
```

## Testing the Component

1. **Make sure MCP server is running**:
   ```bash
   python mcp_server_langflow.py
   ```

2. **In Langflow**:
   - Add the "Send to Teams" component
   - Set file_path to a test file (e.g., `C:\Users\Name\test.txt`)
   - Set message to "Testing from Langflow!"
   - Click "Run"

3. **Check Teams** - You should see your file!

## Troubleshooting

### Component doesn't appear in Langflow
- Make sure you saved the code properly
- Restart Langflow
- Check for syntax errors in the code

### "Server not running" error
- Start the MCP server: `python mcp_server_langflow.py`
- Verify server URL is correct (default: `http://localhost:5000`)

### "File not found" error
- Use absolute paths (e.g., `C:\Users\Name\file.pdf`)
- Check that the file exists
- On Windows, use double backslashes or forward slashes

### "Unauthorized" error
- Check that API key matches the one in `.env` file
- Default: `langflow-teams-secret-123456`

## Advanced Usage

### Dynamic File Paths

Use a Python component before Send to Teams to generate dynamic paths:

```python
from datetime import datetime
import os

# Generate filename
filename = f"report_{datetime.now().strftime('%Y%m%d')}.pdf"
filepath = os.path.join("C:\\Reports", filename)

return {"file_path": filepath}
```

### Conditional Sending

Use a Conditional Router to send only certain files:

```
[File Check] → [Router] → [Send to Teams] (if valid)
                       → [Log Error] (if invalid)
```

### Batch Sending

Use a loop to send multiple files:

```python
files = ["file1.pdf", "file2.png", "file3.txt"]
results = []

for file in files:
    # Call Send to Teams component for each file
    result = send_to_teams(file_path=file)
    results.append(result)

return {"results": results}
```

## Notes

- **File Size**: Large files (>10MB) may take longer to send due to base64 encoding
- **Security**: Files are read directly from your computer and sent via webhook
- **Privacy**: No files are stored on the MCP server
- **Supported Images**: JPG, PNG, GIF, BMP, WebP, SVG
- **Text Preview**: Text files <50KB show a preview in Teams

## Support

If you encounter issues:
1. Check MCP server logs
2. Verify file paths are absolute
3. Ensure Teams webhook is working (test with `send_teams_message`)
4. Check Langflow logs for errors

Happy building! 🚀
