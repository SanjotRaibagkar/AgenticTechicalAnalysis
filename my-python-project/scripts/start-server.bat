@echo off
echo 🚀 Starting LangGraph MCP Server...

REM Check if config exists
if not exist "config\settings.env" (
    echo ❌ config\settings.env not found!
    echo Please copy config\settings.env.example to config\settings.env and add your API key
    pause
    exit /b 1
)

REM Start server (Windows doesn't have source, so we'll rely on the Python script to load the env)
echo 🌐 Starting server...
uv run mcp-server

# ================================