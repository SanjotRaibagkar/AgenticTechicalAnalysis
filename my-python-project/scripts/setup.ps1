Write-Host "🚀 Setting up LangGraph MCP Groq project..." -ForegroundColor Green

# Check if uv is installed
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "❌ uv is not installed. Please install uv first:" -ForegroundColor Red
    Write-Host "irm https://astral.sh/uv/install.ps1 | iex" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Create project structure
Write-Host "📁 Creating project structure..." -ForegroundColor Blue
$directories = @(
    "src/langgraph_mcp_groq/agents",
    "src/langgraph_mcp_groq/server", 
    "src/langgraph_mcp_groq/client",
    "src/langgraph_mcp_groq/utils",
    "tests",
    "config",
    "scripts"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

# Create __init__.py files
$initFiles = @(
    "src/langgraph_mcp_groq/__init__.py",
    "src/langgraph_mcp_groq/agents/__init__.py",
    "src/langgraph_mcp_groq/server/__init__.py",
    "src/langgraph_mcp_groq/client/__init__.py",
    "src/langgraph_mcp_groq/utils/__init__.py",
    "tests/__init__.py"
)

foreach ($file in $initFiles) {
    if (-not (Test-Path $file)) {
        New-Item -ItemType File -Path $file -Force | Out-Null
    }
}

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Blue
uv sync

# Copy example config
Write-Host "⚙️ Creating configuration..." -ForegroundColor Blue
if (-not (Test-Path "config/settings.env")) {
    Copy-Item "config/settings.env.example" "config/settings.env"
    Write-Host "✅ Created config/settings.env - please add your Groq API key!" -ForegroundColor Green
} else {
    Write-Host "⚠️ config/settings.env already exists, skipping..." -ForegroundColor Yellow
}

Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Add your Groq API key to config/settings.env" -ForegroundColor White
Write-Host "2. Run the server: uv run mcp-server" -ForegroundColor White  
Write-Host "3. Run the client: uv run groq-client" -ForegroundColor White
Read-Host "Press Enter to continue"
