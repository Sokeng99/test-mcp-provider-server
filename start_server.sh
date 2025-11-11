#!/bin/bash

echo "======================================================================"
echo "Starting MCP Teams Webhook Server"
echo "======================================================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found! Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

echo ""
echo "Starting server..."
echo "Press Ctrl+C to stop the server"
echo ""

python mcp_server_langflow.py
