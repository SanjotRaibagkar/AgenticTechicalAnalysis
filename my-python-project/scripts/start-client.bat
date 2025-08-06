@echo off
echo 🤖 Starting Groq MCP Client...

REM Check if config exists
if not exist "config\settings.env" (
    echo ❌ config\settings.env not found!
    echo Please copy config\settings.env.example to config\settings.env and add your API key
    pause
    exit /b 1
)

REM Start client
echo 🎯 Starting client...
uv run groq-client