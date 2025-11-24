# Quick Start: Add Component to Langflow (5 Minutes)

## Step-by-Step Guide

### Step 1: Open Langflow
1. Make sure Langflow is running
2. Open browser to `http://localhost:7860` (or your Langflow URL)
3. Create a new flow or open an existing one

### Step 2: Add Custom Component
1. In the Langflow interface, look for the **component sidebar** (left side)
2. Search for "**Custom Component**" or scroll to find it
3. **Drag and drop** the Custom Component onto the canvas

### Step 3: Load the Code

**Option A: Copy-Paste (Easiest)**
1. Click on the Custom Component you just added
2. In the right panel, find the **"Code"** section
3. Click the **"Edit"** or **"<>"** button to open code editor
4. **Delete all existing code**
5. Open `send_to_teams.py` in a text editor
6. **Copy ALL the code** (Ctrl+A, Ctrl+C)
7. **Paste it** into the Langflow code editor (Ctrl+V)
8. Click **"Check & Save"** or **"Save"**
9. The component should now show as **"Send to Teams"** with a send icon!

**Option B: Load from File**
1. Click on the Custom Component
2. Look for **"Load from file"** or **"Import"** button
3. Navigate to `langflow_components/send_to_teams.py`
4. Select and load it

### Step 4: Configure the Component
1. Click on your **"Send to Teams"** component
2. You'll see these inputs in the right panel:
   - **File Path**: Enter path to a file (e.g., `C:\Users\YourName\Documents\test.pdf`)
   - **Message/Caption**: Enter a description
   - **MCP Server URL**: Should be `http://localhost:5000` (default)
   - **API Key**: Should be `langflow-teams-secret-123456` (default)

### Step 5: Test It!

**Simple Test:**
1. Set **File Path** to: `C:\Users\Hout Sokeng\Downloads\test-mcp 1\test-mcp\README.md`
2. Set **Message/Caption** to: `Testing from Langflow!`
3. Click the **"Play"** or **"Run"** button on the component
4. Check your Teams channel - you should see the file!

## Example Flows

### Example 1: Simple File Sender

```
Just the component alone:

┌─────────────────────┐
│  Send to Teams      │
│                     │
│  File Path: [____]  │
│  Message: [_____]   │
│  [RUN]              │
└─────────────────────┘
```

**To create:**
1. Add "Send to Teams" component
2. Fill in the file path
3. Click Run
4. Done!

### Example 2: With Text Input

```
┌──────────────┐       ┌─────────────────┐
│  Text Input  │──────>│  Send to Teams  │
│              │       │                 │
│ File path    │       │  Message: "..."  │
└──────────────┘       └─────────────────┘
```

**To create:**
1. Add "Text Input" component
2. Add "Send to Teams" component
3. Connect Text Input **output** to Send to Teams **file_path** input
4. Set the message
5. Run the flow

### Example 3: Agent Screenshot to Teams

```
┌──────────┐    ┌──────────┐    ┌─────────────────┐
│  Agent   │───>│  Python  │───>│  Send to Teams  │
│          │    │  Code    │    │                 │
│ "Take a  │    │ (saves   │    │  Caption: "..." │
│ screenshot"    │  file)   │    │                 │
└──────────┘    └──────────┘    └─────────────────┘
```

**Python Code example:**
```python
import pyautogui
from datetime import datetime

# Take screenshot
filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
filepath = f"C:\\Temp\\{filename}"
pyautogui.screenshot(filepath)

return filepath
```

## Testing Checklist

Before running in Langflow, make sure:

- [ ] MCP server is running (`python mcp_server_langflow.py`)
- [ ] Server shows "Running on http://0.0.0.0:5000"
- [ ] You can access http://localhost:5000/health
- [ ] File path you're testing with actually exists
- [ ] File path is absolute (starts with C:\ on Windows)

## Common Issues & Solutions

### ❌ Component shows error after pasting code
**Solution**: Make sure you copied ALL the code including imports at the top

### ❌ "Module 'langflow.custom' not found"
**Solution**: You're using an older version of Langflow. Update Langflow:
```bash
pip install langflow --upgrade
```

### ❌ Component doesn't show proper name/icon
**Solution**:
- Check the `display_name` field in the code
- Try clicking "Check & Save" again
- Refresh Langflow page

### ❌ "Connection refused" error
**Solution**: MCP server is not running
```bash
cd "C:\Users\Hout Sokeng\Downloads\test-mcp 1\test-mcp"
python mcp_server_langflow.py
```

### ❌ File not found error
**Solution**:
- Use absolute path: `C:\Users\Name\file.pdf` ✓
- Not relative path: `file.pdf` ✗
- On Windows, use `\\` or `/` in paths

### ❌ Nothing appears in Teams
**Solution**:
- Check Teams webhook URL in `.env` file
- Test with simple message first: `python send_file.py README.md`
- Check server logs for errors

## Quick Copy-Paste Test

Copy this into your Send to Teams component:

**File Path:**
```
C:\Users\Hout Sokeng\Downloads\test-mcp 1\test-mcp\README.md
```

**Message:**
```
Hello from Langflow! This is a test message.
```

Then click **Run** and check Teams!

## Next Steps

Once you have it working:

1. **Create more flows** with different file types
2. **Connect to agents** - let agents send files automatically
3. **Add conditionals** - only send files that meet criteria
4. **Batch process** - send multiple files in sequence
5. **Integrate with APIs** - download and send files from APIs

## Video Tutorial (If you need it)

If you're stuck, here's what the process looks like:

1. **Drag** Custom Component to canvas
2. **Click** on the component
3. **Click** "Edit Code" button
4. **Paste** the code from `send_to_teams.py`
5. **Click** "Check & Save"
6. **Fill** in File Path and Message
7. **Click** Run
8. **Check** Teams channel

That's it! 🎉

## Need Help?

If you're still having trouble:

1. Check that all 3 files were created:
   - `send_to_teams.py` ✓
   - `send_teams_image.py` ✓
   - `send_teams_file.py` ✓

2. Verify MCP server is running:
   ```bash
   curl http://localhost:5000/health
   ```

3. Test outside Langflow first:
   ```bash
   python send_file.py README.md "Test"
   ```

4. Check Langflow version:
   ```bash
   langflow --version
   # Should be 1.0.0 or higher
   ```

Good luck! 🚀
