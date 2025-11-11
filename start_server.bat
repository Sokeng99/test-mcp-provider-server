@echo off
echo ======================================================================
echo Starting MCP Teams Webhook Server
echo ======================================================================

REM Check if virtual environment exists
if not exist venv\ (
    echo Virtual environment not found! Creating one...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Installing dependencies...
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

echo.
echo Starting server...
echo Press Ctrl+C to stop the server
echo.

python mcp_server_langflow.py

pause
