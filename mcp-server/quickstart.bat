@echo off
REM Quick start script for MCP Crypto Server (Windows)

echo 🚀 MCP Crypto Server Quick Start
echo =================================

REM Check if uv is installed
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ uv is not installed. Please install it first:
    echo    pip install uv
    exit /b 1
)

echo 📦 Installing dependencies...
uv sync

echo 🧪 Running basic tests...
python test_runner.py

echo 🎉 Setup complete! You can now:
echo    1. Start the server: uv run python -m src.main
echo    2. Or use dev script: python dev.py run
echo    3. Server will be available at: http://localhost:6789
echo.
echo 📋 Available endpoints:
echo    • Tools: encrypt, decrypt
echo    • Resources: version, status, tools_list
echo.
echo 💡 Configuration can be modified in config.yaml

pause