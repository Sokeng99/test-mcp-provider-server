# How to Install X-pilot Bot in Microsoft Teams

Your Teams app package has been created: **`xpilot-bot-teams-app.zip`**

## Installation Options

### Option A: Install for Yourself (Recommended to Try First)

**1. Open Microsoft Teams**

**2. Go to Apps:**
   - Click on "Apps" in the left sidebar
   - Or click the "..." menu and select "Apps"

**3. Upload the custom app:**
   - Click "Manage your apps" (bottom left)
   - Click "Upload an app" or "Upload a custom app"
   - Select "Upload for me" or "Upload for [Your Organization]"
   - Browse and select the file: `xpilot-bot-teams-app.zip`

**4. Install the app:**
   - Teams will validate the package
   - Click "Add" to install the bot for yourself
   - The bot will appear in your Apps list

**5. Start chatting:**
   - Click on the bot to open a chat
   - Send a message like "Hello" or "What can you do?"
   - The bot will respond using Langflow AI!

---

### Option B: Request Admin Approval (If Upload Fails)

If you see an error like "You don't have permission to upload custom apps", you'll need admin approval:

**1. Send the ZIP file to your Teams Admin**

**2. Ask them to upload it via Teams Admin Center:**
   - Go to: https://admin.teams.microsoft.com
   - Navigate to: **Teams apps** → **Manage apps**
   - Click **"Upload new app"**
   - Upload the file: `xpilot-bot-teams-app.zip`
   - Click **"Upload"**

**3. Admin should approve the app:**
   - Go to: **Teams apps** → **Permission policies**
   - Edit the policy that applies to your users
   - Add "X-pilot Bot" to the allowed apps list
   - Save changes

**4. Install the bot (after admin approval):**
   - Open Teams → Apps
   - Look under "Built for [Your Organization]"
   - Find "X-pilot Bot"
   - Click "Add"

---

## Adding Bot to a Team Channel

Once installed, you can add the bot to any Team channel:

**1. Open the Team where you want to add the bot**

**2. Click the "..." menu next to the channel name**

**3. Select "Manage channel"** or **"Get bots"**

**4. Search for "X-pilot Bot"**

**5. Click "Add"** to add it to the channel

**6. Team members can now @mention the bot:**
   - Example: `@X-pilot Bot what's the weather today?`

---

## Troubleshooting

### "You don't have permission to use this app"
- The app needs admin approval (see Option B above)

### "Bot not responding in Teams"
- Make sure your bot server is running: `python bot_server.py`
- Make sure ngrok is running and the URL matches in Azure Bot Configuration
- Check the messaging endpoint in Azure Bot Configuration matches ngrok URL

### "App package validation failed"
- The package has been created with correct format
- If you see this error, share the exact error message for help

---

## Important Notes

**Keep These Running:**
- ✅ Bot server: `python bot_server.py` (Port 3978)
- ✅ Ngrok: `ngrok http 3978` (Exposes bot to internet)
- ✅ Langflow: Docker container (Port 7860)

**Azure Bot Messaging Endpoint:**
- Should be set to: `https://your-ngrok-url.ngrok-free.app/api/messages`
- Update this whenever ngrok restarts (free tier gives new URL each time)

---

## File Location

The Teams app package is located at:
```
C:\Users\Hout Sokeng\Downloads\test-mcp 1\test-mcp\xpilot-bot-teams-app.zip
```

You can share this ZIP file with your admin or upload it yourself!

---

## Questions?

If you encounter any issues during installation, check:
1. Azure Bot Configuration → Messaging endpoint is correct
2. Bot server is running
3. Ngrok is active
4. Langflow container is running

Good luck! Your bot is ready to use in Teams! 🚀
