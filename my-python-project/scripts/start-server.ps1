Write-Host "🚀 Starting LangGraph MCP Server..." -ForegroundColor Green

# Check if config exists
if (-not (Test-Path "config/settings.env")) {
    Write-Host "❌ config/settings.env not found!" -ForegroundColor Red
    Write-Host "Please copy config/settings.env.example to config/settings.env and add your API key" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Groq API key is set
$envContent = Get-Content "config/settings.env" | Where-Object { $_ -match "GROQ_API_KEY=" }
if (-not $envContent -or $envContent -match "your_groq_api_key_here") {
    Write-Host "❌ Please set your GROQ_API_KEY in config/settings.env" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Extract server details from config
$serverHost = (Get-Content "config/settings.env" | Where-Object { $_ -match "MCP_SERVER_HOST=" } | ForEach-Object { $_.Split("=")[1] }) -replace '"', ''
$serverPort = (Get-Content "config/settings.env" | Where-Object { $_ -match "MCP_SERVER_PORT=" } | ForEach-Object { $_.Split("=")[1] }) -replace '"', ''

if (-not $serverHost) { $serverHost = "localhost" }
if (-not $serverPort) { $serverPort = "8000" }

# Start server
Write-Host "🌐 Starting server on $serverHost`:$serverPort" -ForegroundColor Blue
uv run mcp-server
