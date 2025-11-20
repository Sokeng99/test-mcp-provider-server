"""
Langflow Component for Testing Teams Notifications with Action Buttons
"""

import requests
from langflow.custom import Component
from langflow.io import MessageTextInput, DropdownInput, Output
from langflow.schema import Data


class QuickNotification(Component):
    display_name = "Quick Teams Notification"
    description = "Send a notification to Teams with an action button"

    inputs = [
        MessageTextInput(
            name="title",
            display_name="Title",
            info="Notification title",
            value="New Notification"
        ),
        MessageTextInput(
            name="message",
            display_name="Message",
            info="Notification message content",
        ),
        DropdownInput(
            name="priority",
            display_name="Priority",
            options=["urgent", "high", "normal", "low"],
            value="normal",
            info="Notification priority level"
        ),
        MessageTextInput(
            name="action_url",
            display_name="Action URL",
            info="URL for the action button (e.g., https://github.com)",
            value="https://github.com"
        ),
        MessageTextInput(
            name="action_text",
            display_name="Button Text",
            info="Text shown on the action button",
            value="View Details"
        ),
    ]

    outputs = [
        Output(display_name="Response", name="response", method="send_notification"),
    ]

    def send_notification(self) -> Data:
        """Send a notification with action button to Teams"""

        # Set defaults for None values
        title = self.title or "Notification"
        message = self.message or "No message provided"
        priority = self.priority or "normal"
        action_url = self.action_url or "https://github.com"
        action_text = self.action_text or "View Details"

        url = "http://host.docker.internal:5000/mcp/tools/call"
        headers = {
            "Authorization": "Bearer langflow-teams-secret-123456",
            "Content-Type": "application/json"
        }

        payload = {
            "name": "send_notification",
            "arguments": {
                "title": title,
                "message": message,
                "priority": priority,
                "action_url": action_url,
                "action_text": action_text
            }
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()

            priority_icons = {
                "urgent": "🚨",
                "high": "⚠️",
                "normal": "ℹ️",
                "low": "📝"
            }
            icon = priority_icons.get(priority, "ℹ️")

            return Data(
                data={"result": result, "success": True},
                text=f"✅ Notification sent successfully!\n\n{icon} Title: {title}\n📝 Message: {message}\n⚡ Priority: {priority.upper()}\n🔗 Action: [{action_text}]({action_url})\n\nCheck your Teams channel!"
            )

        except Exception as e:
            return Data(
                data={"error": str(e), "success": False},
                text=f"❌ Error sending notification: {str(e)}"
            )
