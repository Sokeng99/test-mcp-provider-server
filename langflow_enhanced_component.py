"""
Enhanced Langflow Component for Teams Messages
Supports simple messages, adaptive cards, and notifications
"""

import requests
import json
from langflow.custom import Component
from langflow.io import MessageTextInput, DropdownInput, DictInput, Output
from langflow.schema import Data


class EnhancedTeamsMessageSender(Component):
    display_name = "Send Enhanced Teams Message"
    description = "Send messages to Microsoft Teams with rich formatting, priorities, and action buttons"

    inputs = [
        DropdownInput(
            name="message_type",
            display_name="Message Type",
            options=["simple", "adaptive_card", "notification"],
            value="simple",
            info="Type of message to send"
        ),
        MessageTextInput(
            name="title",
            display_name="Title",
            info="Message title (required for adaptive cards and notifications)",
        ),
        MessageTextInput(
            name="message",
            display_name="Message",
            info="The main message content",
        ),
        DropdownInput(
            name="priority",
            display_name="Priority",
            options=["urgent", "high", "normal", "low"],
            value="normal",
            info="Message priority level"
        ),
        DictInput(
            name="facts",
            display_name="Facts (Optional)",
            info="Key-value pairs to display as facts (e.g., {'Status': 'Running', 'Uptime': '99.9%'})",
            is_list=False,
            advanced=True
        ),
        MessageTextInput(
            name="image_url",
            display_name="Image URL (Optional)",
            info="URL of an image to include in the card",
            advanced=True
        ),
        MessageTextInput(
            name="sender",
            display_name="Sender (Optional)",
            info="Sender name or identifier",
            advanced=True
        ),
        MessageTextInput(
            name="action_url",
            display_name="Action URL (Optional)",
            info="URL for action button (notifications only)",
            advanced=True
        ),
        MessageTextInput(
            name="action_text",
            display_name="Action Button Text",
            value="View Details",
            info="Text for action button",
            advanced=True
        ),
    ]

    outputs = [
        Output(display_name="Response", name="response", method="send_message"),
    ]

    def send_message(self) -> Data:
        # MCP server configuration
        url = "http://localhost:5000/mcp/tools/call"
        headers = {
            "Authorization": "Bearer langflow-teams-secret-123456",
            "Content-Type": "application/json"
        }

        try:
            # Build payload based on message type
            if self.message_type == "simple":
                payload = {
                    "name": "send_teams_message",
                    "arguments": {
                        "message": self.message
                    }
                }

            elif self.message_type == "adaptive_card":
                arguments = {
                    "title": self.title or "Notification",
                    "message": self.message,
                    "priority": self.priority
                }

                # Add optional fields if provided
                if self.facts:
                    arguments["facts"] = self.facts
                if self.image_url:
                    arguments["image_url"] = self.image_url
                if self.sender:
                    arguments["sender"] = self.sender

                payload = {
                    "name": "send_adaptive_card",
                    "arguments": arguments
                }

            elif self.message_type == "notification":
                arguments = {
                    "title": self.title or "Notification",
                    "message": self.message,
                    "priority": self.priority
                }

                # Add optional fields if provided
                if self.action_url:
                    arguments["action_url"] = self.action_url
                    arguments["action_text"] = self.action_text or "View Details"

                payload = {
                    "name": "send_notification",
                    "arguments": arguments
                }

            else:
                return Data(
                    data={"error": f"Unknown message type: {self.message_type}"},
                    text=f"Error: Unknown message type"
                )

            # Send request
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()

            return Data(
                data={"result": result, "type": self.message_type, "priority": self.priority},
                text=f"✓ {self.message_type.replace('_', ' ').title()} sent successfully ({self.priority} priority)"
            )

        except requests.exceptions.RequestException as e:
            return Data(
                data={"error": str(e), "type": self.message_type},
                text=f"✗ Error sending message: {str(e)}"
            )
        except Exception as e:
            return Data(
                data={"error": str(e), "type": self.message_type},
                text=f"✗ Unexpected error: {str(e)}"
            )


class SimpleTeamsMessage(Component):
    """Simplified component for quick simple messages"""
    display_name = "Simple Teams Message"
    description = "Send a quick simple text message to Teams"

    inputs = [
        MessageTextInput(
            name="message",
            display_name="Message",
            info="The message text to send",
        ),
    ]

    outputs = [
        Output(display_name="Response", name="response", method="send_message"),
    ]

    def send_message(self) -> Data:
        url = "http://localhost:5000/mcp/tools/call"
        headers = {
            "Authorization": "Bearer langflow-teams-secret-123456",
            "Content-Type": "application/json"
        }

        payload = {
            "name": "send_teams_message",
            "arguments": {"message": self.message}
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()

            return Data(
                data={"result": result},
                text="✓ Message sent successfully"
            )
        except Exception as e:
            return Data(
                data={"error": str(e)},
                text=f"✗ Error: {str(e)}"
            )


class AdaptiveCardMessage(Component):
    """Component specifically for adaptive cards"""
    display_name = "Teams Adaptive Card"
    description = "Send a rich formatted adaptive card to Teams"

    inputs = [
        MessageTextInput(
            name="title",
            display_name="Title",
            info="Card title",
        ),
        MessageTextInput(
            name="message",
            display_name="Message",
            info="Main message content",
        ),
        DropdownInput(
            name="priority",
            display_name="Priority",
            options=["urgent", "high", "normal", "low"],
            value="normal",
        ),
        DictInput(
            name="facts",
            display_name="Facts",
            info="Key-value pairs (e.g., {'Status': 'Running'})",
            is_list=False,
        ),
    ]

    outputs = [
        Output(display_name="Response", name="response", method="send_message"),
    ]

    def send_message(self) -> Data:
        url = "http://localhost:5000/mcp/tools/call"
        headers = {
            "Authorization": "Bearer langflow-teams-secret-123456",
            "Content-Type": "application/json"
        }

        arguments = {
            "title": self.title,
            "message": self.message,
            "priority": self.priority
        }

        if self.facts:
            arguments["facts"] = self.facts

        payload = {
            "name": "send_adaptive_card",
            "arguments": arguments
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()

            return Data(
                data={"result": result},
                text=f"✓ Adaptive card sent ({self.priority} priority)"
            )
        except Exception as e:
            return Data(
                data={"error": str(e)},
                text=f"✗ Error: {str(e)}"
            )
