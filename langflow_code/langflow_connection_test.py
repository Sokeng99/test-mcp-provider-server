"""
Test if Langflow can connect to MCP server
Use this to verify the connection before sending messages
"""

import requests
from langflow.custom import Component
from langflow.io import Output
from langflow.schema import Data


class TestMCPConnection(Component):
    display_name = "Test MCP Connection"
    description = "Verify connection to MCP server"

    inputs = []

    outputs = [
        Output(display_name="Result", name="result", method="test_connection"),
    ]

    def test_connection(self) -> Data:
        """Test connection to MCP server"""

        urls_to_test = [
            ("host.docker.internal", "http://host.docker.internal:5000/health"),
            ("localhost", "http://localhost:5000/health"),
            ("127.0.0.1", "http://127.0.0.1:5000/health"),
        ]

        results = []
        successful_url = None

        for name, url in urls_to_test:
            try:
                response = requests.get(url, timeout=3)
                if response.status_code == 200:
                    results.append(f"✅ {name}: Connected successfully!")
                    successful_url = url.replace("/health", "/mcp/tools/call")
                else:
                    results.append(f"❌ {name}: HTTP {response.status_code}")
            except Exception as e:
                results.append(f"❌ {name}: {str(e)[:50]}")

        result_text = "\n".join(results)

        if successful_url:
            result_text += f"\n\n🎉 Use this URL in your components:\n{successful_url}"
            return Data(
                data={"success": True, "url": successful_url},
                text=result_text
            )
        else:
            result_text += "\n\n⚠️ MCP server not reachable. Make sure it's running on the host machine."
            return Data(
                data={"success": False},
                text=result_text
            )
