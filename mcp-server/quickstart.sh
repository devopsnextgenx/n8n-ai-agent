#!/bin/bash

# Quick start script for MCP Crypto Server

echo "🚀 MCP Crypto Server Quick Start"
echo "================================="

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install it first:"
    echo "   pip install uv"
    exit 1
fi

echo "📦 Installing dependencies..."
uv sync

echo "🧪 Running basic tests..."
python test_runner.py

echo "🎉 Setup complete! You can now:"
echo "   1. Start the server: uv run python -m src.main"
echo "   2. Or use dev script: python dev.py run"
echo "   3. Server will be available at: http://localhost:6789"
echo ""
echo "📋 Available endpoints:"
echo "   • Tools: encrypt, decrypt"
echo "   • Resources: version, status, tools_list"
echo ""
echo "💡 Configuration can be modified in config.yaml"