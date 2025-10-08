#!/bin/bash

# Python Virtual Environment Setup Script for n8n-ai-agent
# This script creates and sets up a Python virtual environment for the project

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "Python is not installed or not in PATH"
        exit 1
    fi
    
    # Check Python version
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | grep -oP '\d+\.\d+')
    print_status "Found Python $PYTHON_VERSION"
    
    # Check if Python version is 3.10 or higher
    if [[ $(echo "$PYTHON_VERSION >= 3.10" | bc -l) -eq 0 ]]; then
        print_error "Python 3.10 or higher is required. Found: $PYTHON_VERSION"
        exit 1
    fi
}

# Create virtual environment
create_venv() {
    print_status "Creating Python virtual environment..."
    
    if [ -d ".venv" ]; then
        print_warning "Virtual environment already exists. Removing old one..."
        rm -rf .venv
    fi
    
    $PYTHON_CMD -m venv .venv
    print_success "Virtual environment created at ./.venv"
}

# Activate virtual environment (for current session)
activate_venv() {
    print_status "Activating virtual environment..."
    
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
        # Windows
        source mcp-server/.venv/Scripts/activate
    else
        # Linux/macOS
        source mcp-server/.venv/bin/activate
    fi
    
    print_success "Virtual environment activated"
}

# Install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    
    # Upgrade pip first
    python -m pip install --upgrade pip
    
    # Install main dependencies
    if [ -f "requirements.txt" ]; then
        print_status "Installing requirements from requirements.txt..."
        pip install -r requirements.txt
    fi
    
    # Install MCP server dependencies
    if [ -f "mcp-server/pyproject.toml" ]; then
        print_status "Installing MCP server dependencies..."
        cd mcp-server
        pip install -e ".[dev]"
        cd ..
    fi
    
    print_success "All dependencies installed"
}

# Create .env file if it doesn't exist
create_env_file() {
    if [ ! -f ".env" ]; then
        print_status "Creating .env file..."
        cat > .env << EOF
# Python Environment Configuration
PYTHONPATH=./mcp-server
PYTHONDONTWRITEBYTECODE=1

# MCP Server Configuration
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=3000

# N8N Configuration
N8N_HOST=localhost
N8N_PORT=5678

# Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=n8n
MYSQL_USER=n8n
MYSQL_PASSWORD=n8n_password

# MQTT Configuration
MQTT_HOST=localhost
MQTT_PORT=1883

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
EOF
        print_success ".env file created"
    else
        print_status ".env file already exists"
    fi
}

# Main setup function
main() {
    print_status "Setting up Python environment for n8n-ai-agent..."
    
    check_python
    create_venv
    activate_venv
    install_dependencies
    create_env_file
    
    print_success "Python environment setup complete!"
    echo
    print_status "To activate the environment in your terminal, run:"
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
        echo "  source mcp-server/.venv/Scripts/activate"
    else
        echo "  source mcp-server/.venv/bin/activate"
    fi
    echo
    print_status "VS Code should automatically detect and use the .venv environment when you open this project."
}

# Run main function
main