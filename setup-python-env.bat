@echo off
REM Python Virtual Environment Setup Script for n8n-ai-agent (Windows)
REM This script creates and sets up a Python virtual environment for the project

setlocal enabledelayedexpansion

echo [INFO] Setting up Python environment for n8n-ai-agent...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    exit /b 1
)

REM Get Python version
for /f "tokens=2 delims= " %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [INFO] Found Python %PYTHON_VERSION%

REM Create virtual environment
echo [INFO] Creating Python virtual environment...
if exist ".venv" (
    echo [WARNING] Virtual environment already exists. Removing old one...
    rmdir /s /q .venv
)

python -m venv .venv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment
    exit /b 1
)
echo [SUCCESS] Virtual environment created at .\.venv

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call .venv\Scripts\activate.bat

REM Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo [INFO] Installing dependencies...
if exist "requirements.txt" (
    echo [INFO] Installing requirements from requirements.txt...
    pip install -r requirements.txt
)

REM Install MCP server dependencies
if exist "mcp-server\pyproject.toml" (
    echo [INFO] Installing MCP server dependencies...
    cd mcp-server
    pip install -e .[dev]
    cd ..
)

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo [INFO] Creating .env file...
    (
        echo # Python Environment Configuration
        echo PYTHONPATH=./mcp-server
        echo PYTHONDONTWRITEBYTECODE=1
        echo.
        echo # MCP Server Configuration
        echo MCP_SERVER_HOST=localhost
        echo MCP_SERVER_PORT=3000
        echo.
        echo # N8N Configuration
        echo N8N_HOST=localhost
        echo N8N_PORT=5678
        echo.
        echo # Database Configuration
        echo MYSQL_HOST=localhost
        echo MYSQL_PORT=3306
        echo MYSQL_DATABASE=n8n
        echo MYSQL_USER=n8n
        echo MYSQL_PASSWORD=n8n_password
        echo.
        echo # MQTT Configuration
        echo MQTT_HOST=localhost
        echo MQTT_PORT=1883
        echo.
        echo # Redis Configuration
        echo REDIS_HOST=localhost
        echo REDIS_PORT=6379
    ) > .env
    echo [SUCCESS] .env file created
) else (
    echo [INFO] .env file already exists
)

echo [SUCCESS] Python environment setup complete!
echo.
echo [INFO] To activate the environment in your terminal, run:
echo   .venv\Scripts\activate.bat
echo.
echo [INFO] VS Code should automatically detect and use the .venv environment when you open this project.

pause