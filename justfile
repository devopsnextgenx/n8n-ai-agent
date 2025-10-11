# MCP Server Just Commands
# This file contains useful commands for working with the n8n-ai-agent project
# Run commands using: just <command-name>

# Display help information
default:
    @just --list

# Set up the Python environment
setup-env:
    @echo "Setting up Python environment..."
    @bash setup-python-env.sh

# Install Python dependencies
install-deps:
    @echo "Installing Python dependencies..."
    cd mcp-server && ./.venv/Scripts/python.exe -m pip install -r requirements.txt

# Run the MCP server in standard mode
run-server:
    @echo "Starting MCP server..."
    cd mcp-server && ./.venv/Scripts/python.exe -m n8n_mcp_server.cli

# Run the MCP server in development mode using the main module
run-dev-auto:
    @echo "Starting MCP server in development mode..."
    cd mcp-server && python -m src.server --dev --mode auto

# Run the MCP server in development mode with streamable option (for n8n integration)
dev:
    #!/bin/bash
    echo "Starting MCP server in streamable mode (for n8n)..."
    cd mcp-server
    source .venv/bin/activate
    python -m src.server --dev --mode streamable-http

# Run the MCP server in development mode with streamable option (for n8n integration)
run-dev:
    #!/bin/bash
    echo "Starting MCP server in streamable mode (for n8n)..."
    cd mcp-server
    source .venv/Scripts/activate
    python -m src.server --dev --mode streamable-http

run-dev-streamable:
    #!/bin/bash
    echo "Starting MCP server in streamable mode (for n8n)..."
    cd mcp-server
    source .venv/Scripts/activate
    python -m src.server --dev --mode streamable-http

# Run tests
run-tests:
    @echo "Running tests..."
    cd mcp-server && ./.venv/Scripts/python.exe -m pytest tests/ -v

# Format code using black
format-code:
    @echo "Formatting code with black..."
    cd mcp-server && ./.venv/Scripts/python.exe -m black mcp-server/ --line-length 88

# Lint code using ruff
lint-code:
    @echo "Linting code with ruff..."
    cd mcp-server && ./.venv/Scripts/python.exe -m ruff check mcp-server/

# Full development workflow - setup, install, format, lint, test
dev-workflow: setup-env install-deps format-code lint-code run-tests
    @echo "Development workflow completed successfully!"
