Write-Host "🧪 Running tests..." -ForegroundColor Green

# Run tests
Write-Host "Running pytest..." -ForegroundColor Blue
uv run pytest tests/ -v

# Run linting
Write-Host "🔍 Running code quality checks..." -ForegroundColor Blue
Write-Host "Checking code formatting..." -ForegroundColor Cyan
uv run black --check src/ tests/

Write-Host "Running flake8..." -ForegroundColor Cyan
uv run flake8 src/ tests/

Write-Host "Running mypy..." -ForegroundColor Cyan
uv run mypy src/

Write-Host "✅ All tests and checks completed!" -ForegroundColor Green
Read-Host "Press Enter to continue"
