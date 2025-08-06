@echo off
echo 🚀 Setting up LangGraph MCP Groq project...

REM Check if uv is installed
where uv >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ uv is not installed. Please install uv first:
    echo powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    pause
    exit /b 1
)

REM Create project structure
echo 📁 Creating project structure...
if not exist "src\langgraph_mcp_groq\agents" mkdir src\langgraph_mcp_groq\agents
if not exist "src\langgraph_mcp_groq\server" mkdir src\langgraph_mcp_groq\server
if not exist "src\langgraph_mcp_groq\client" mkdir src\langgraph_mcp_groq\client
if not exist "src\langgraph_mcp_groq\utils" mkdir src\langgraph_mcp_groq\utils
if not exist "tests" mkdir tests
if not exist "config" mkdir config
if not exist "scripts" mkdir scripts

REM Create __init__.py files
echo. > src\langgraph_mcp_groq\__init__.py
echo. > src\langgraph_mcp_groq\agents\__init__.py
echo. > src\langgraph_mcp_groq\server\__init__.py
echo. > src\langgraph_mcp_groq\client\__init__.py
echo. > src\langgraph_mcp_groq\utils\__init__.py
echo. > tests\__init__.py

REM Install dependencies
echo 📦 Installing dependencies...
uv sync

REM Copy example config
echo ⚙️ Creating configuration...
if not exist "config\settings.env" (
    copy "config\settings.env.example" "config\settings.env"
    echo ✅ Created config\settings.env - please add your Groq API key!
) else (
    echo ⚠️ config\settings.env already exists, skipping...
)

echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Add your Groq API key to config\settings.env
echo 2. Run the server: uv run mcp-server
echo 3. Run the client: uv run groq-client
pause