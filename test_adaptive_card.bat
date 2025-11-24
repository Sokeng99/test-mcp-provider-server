@echo off
echo Testing send_adaptive_card tool...
curl -X POST http://host.docker.internal:5000/mcp/tools/call ^
  -H "Authorization: Bearer langflow-teams-secret-123456" ^
  -H "Content-Type: application/json" ^
  -d "{\"name\": \"send_adaptive_card\", \"arguments\": {\"title\": \"Test from MCP Server\", \"message\": \"This is a test adaptive card\", \"priority\": \"high\", \"facts\": {\"Source\": \"Direct MCP Test\", \"Component\": \"test_adaptive_card.bat\"}, \"sender\": \"MCP Test Script\"}}"
