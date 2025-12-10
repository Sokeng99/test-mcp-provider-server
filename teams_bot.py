"""
Teams Bot - Interactive conversational bot for Microsoft Teams
Connects to Langflow for AI-powered responses
"""

from botbuilder.core import ActivityHandler, TurnContext, MessageFactory
from botbuilder.schema import ChannelAccount, Activity, ActivityTypes
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
LANGFLOW_URL = os.getenv("LANGFLOW_URL", "http://localhost:7860")
LANGFLOW_API_KEY = os.getenv("LANGFLOW_API_KEY", "")

# Multiple Flow Configuration
LANGFLOW_CHAT_FLOW_ID = os.getenv("LANGFLOW_CHAT_FLOW_ID", "")
LANGFLOW_REQUIREMENT_FLOW_ID = os.getenv("LANGFLOW_REQUIREMENT_FLOW_ID", "")

# Backwards compatibility
LANGFLOW_FLOW_ID = os.getenv("LANGFLOW_FLOW_ID", LANGFLOW_CHAT_FLOW_ID)

# Keywords that trigger requirement analysis flow
REQUIREMENT_KEYWORDS = [
    "meeting", "meetings", "meet",
    "requirement", "requirements", "require",
    "analysis", "analyze", "analyse",
    "attendee", "attendees", "attend",
    "participant", "participants", "participate",
    "who should join", "who needs to", "who need to",
    "invite", "invitation", "invites",
    "stakeholder", "stakeholders"
]


class TeamsBot(ActivityHandler):
    """
    Teams Bot that responds to messages using Langflow AI
    """

    async def on_message_activity(self, turn_context: TurnContext):
        """
        Handle incoming messages from Teams users
        """
        # Get the user's message
        user_message = turn_context.activity.text
        user_name = turn_context.activity.from_property.name

        print(f"Received from {user_name}: {user_message}")

        # Send typing indicator
        await turn_context.send_activity(
            Activity(type=ActivityTypes.typing)
        )

        # Get AI response from Langflow
        ai_response = await self.get_langflow_response(user_message)

        # Send response back to user
        await turn_context.send_activity(
            MessageFactory.text(ai_response)
        )

    def _detect_flow_type(self, message: str) -> str:
        """
        Detect which flow to use based on message content

        Args:
            message: User's message

        Returns:
            Flow ID to use (requirement or chat)
        """
        message_lower = message.lower()

        # Check if message contains requirement analysis keywords
        for keyword in REQUIREMENT_KEYWORDS:
            if keyword in message_lower:
                print(f"Detected requirement analysis keyword: '{keyword}' -> using Requirement Flow")
                return LANGFLOW_REQUIREMENT_FLOW_ID

        # Default to chat flow
        print("No requirement keywords detected -> using Chat Flow")
        return LANGFLOW_CHAT_FLOW_ID

    async def get_langflow_response(self, message: str) -> str:
        """
        Get AI response from Langflow

        Args:
            message: User's message

        Returns:
            AI-generated response
        """
        try:
            # If Langflow is configured, use it
            if LANGFLOW_CHAT_FLOW_ID or LANGFLOW_FLOW_ID:
                # Detect which flow to use based on message content
                flow_id = self._detect_flow_type(message)

                # Call Langflow with the appropriate flow
                response = await self._call_langflow(message, flow_id)
                return response

            # Otherwise, use a simple echo response
            return f"You said: {message}\n\n(Configure LANGFLOW_URL and flow IDs in .env to enable AI responses)"

        except Exception as e:
            print(f"Error getting Langflow response: {e}")
            return "Sorry, I encountered an error processing your message. Please try again."

    async def _call_langflow(self, message: str, flow_id: str = None) -> str:
        """
        Call Langflow API to get AI response

        Args:
            message: User's message
            flow_id: Langflow flow ID to use (optional, defaults to chat flow)

        Returns:
            AI response from Langflow
        """
        try:
            # Use provided flow_id or fallback to configured flow
            if not flow_id:
                flow_id = LANGFLOW_FLOW_ID

            # Parse the flow ID - format is "flow_id/folder/folder_id" or just "flow_id"
            flow_parts = flow_id.split("/")
            flow_id_clean = flow_parts[0] if flow_parts else flow_id

            # Updated Langflow API endpoint (using /run instead of deprecated /process)
            url = f"{LANGFLOW_URL}/api/v1/run/{flow_id_clean}"

            # Payload format for Langflow /run endpoint
            payload = {
                "input_value": message,
                "output_type": "chat",
                "input_type": "chat"
            }

            # Call Langflow with proper headers including API key
            headers = {
                "Content-Type": "application/json",
                "x-api-key": LANGFLOW_API_KEY
            }

            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                print(f"Langflow response received")

                # Extract message from Langflow /run endpoint response
                # Response structure: outputs[0].outputs[0].results.message.text
                try:
                    if "outputs" in data and len(data["outputs"]) > 0:
                        output = data["outputs"][0]
                        if "outputs" in output and len(output["outputs"]) > 0:
                            result = output["outputs"][0]
                            if "results" in result and "message" in result["results"]:
                                text = result["results"]["message"].get("text")
                                if text:
                                    return text
                            # Try alternative path: messages array
                            if "messages" in result and len(result["messages"]) > 0:
                                text = result["messages"][0].get("message")
                                if text:
                                    return text
                except (KeyError, IndexError, TypeError) as e:
                    print(f"Error parsing response: {e}")

                # Fallback: return raw response for debugging
                return f"Langflow responded but couldn't extract message. Check bot logs."
            else:
                error_text = response.text[:200] if response.text else "No error details"
                return f"Error calling Langflow: Status {response.status_code}, Details: {error_text}"

        except Exception as e:
            print(f"Langflow API error: {e}")
            import traceback
            traceback.print_exc()
            return f"Exception calling Langflow: {str(e)}"

    async def on_members_added_activity(
        self, members_added: list[ChannelAccount], turn_context: TurnContext
    ):
        """
        Greet new members when they're added to a conversation
        """
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    f"Hello {member.name}! 👋\n\n"
                    f"I'm your X-pilot AI assistant powered by Langflow.\n\n"
                    f"Ask me anything, and I'll do my best to help!"
                )

    async def on_conversation_update_activity(self, turn_context: TurnContext):
        """
        Handle conversation updates (bot added to channel, etc.)
        """
        await super().on_conversation_update_activity(turn_context)

        # If bot was added to a channel
        if turn_context.activity.members_added:
            await self.on_members_added_activity(
                turn_context.activity.members_added, turn_context
            )
