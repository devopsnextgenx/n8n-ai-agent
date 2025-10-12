#!/bin/bash

# Docker entrypoint script for MCP server
set -e

echo "🚀 Starting MCP Server Container"
echo "================================="

# Wait for dependencies if needed
if [ "$WAIT_FOR_DEPS" = "true" ]; then
    echo "⏳ Waiting for dependencies..."
    sleep 5
fi

# Set default values if not provided
export MCP_HOST=${MCP_HOST:-0.0.0.0}
export MCP_PORT=${MCP_PORT:-6789}
export LOG_LEVEL=${LOG_LEVEL:-INFO}

echo "📋 Configuration:"
echo "   Host: $MCP_HOST"
echo "   Port: $MCP_PORT"
echo "   Log Level: $LOG_LEVEL"

# Determine which server to run based on command or environment
if [ "$1" = "fastapi" ] || [ "$SERVER_TYPE" = "fastapi" ]; then
    echo "🎯 Starting FastAPI server..."
    exec uv run python src/fastapi_server.py
elif [ "$1" = "mcp" ] || [ "$SERVER_TYPE" = "mcp" ] || [ -z "$1" ]; then
    echo "🎯 Starting MCP server..."
    exec uv run python src/server.py
else
    echo "🎯 Starting with custom command: $@"
    exec "$@"
fi