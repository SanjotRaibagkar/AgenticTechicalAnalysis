@echo off
echo 🧪 Running tests...

REM Run tests
uv run pytest tests/ -v

REM Run linting
echo 🔍 Running code quality checks...
uv run black --check src/ tests/
uv run flake8 src/ tests/
uv run mypy src/

echo ✅ All tests and checks completed!
pause
