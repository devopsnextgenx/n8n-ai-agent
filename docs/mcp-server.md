# MCP Server Setup Guide

This document provides setup instructions for the N8N MCP Server project using UV (modern Python package manager).

## Overview

The MCP server has been restructured as a proper UV project with:
- ✅ **Modular Architecture**: Separate modules for tools, handlers, and utilities
- ✅ **UV Project Management**: Modern Python dependency management
- ✅ **Type Safety**: Full type hints and mypy checking
- ✅ **Testing**: Comprehensive test suite with pytest
- ✅ **Development Tools**: Linting, formatting, and code quality tools
- ✅ **Documentation**: Detailed setup and usage instructions

## Quick Setup with UV

### Prerequisites

1. **Install UV** (Python package manager):
   ```bash
   # On Windows (PowerShell)
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   
   # On macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Verify UV installation**:
   ```bash
   uv --version
   ```

### Project Setup

1. **Navigate to the MCP server directory**:
   ```bash
   cd mcp-server
   ```

2. **Initialize and sync the project**:
   ```bash
   uv sync
   ```

3. **Activate the virtual environment**:
   ```bash
   # On Windows
   .venv\Scripts\activate
   
   # On macOS/Linux
   source .venv/bin/activate
   ```

4. **Install development dependencies** (optional):
   ```bash
   uv sync --all-extras
   ```

5. **Create environment configuration**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

## Usage

### Running the MCP Server

**Production mode**:
```bash
uv run mcp-server
```

**Development mode** (with auto-reload):
```bash
uv run mcp-dev
```

**Using Python module**:
```bash
uv run python -m n8n_mcp_server.main
```

### Development Commands

**Run tests**:
```bash
# Quick tests
uv run python scripts/test.py

# With coverage
uv run python scripts/test.py coverage

# All test types
uv run python scripts/test.py all
```

**Code quality checks**:
```bash
# Check code quality
uv run python scripts/lint.py

# Fix formatting issues
uv run python scripts/lint.py --fix
```

**Development server**:
```bash
uv run python scripts/dev.py
```

### Adding Dependencies

**Runtime dependency**:
```bash
uv add package-name
```

**Development dependency**:
```bash
uv add --dev package-name
```

## Project Structure

```
mcp-server/
├── pyproject.toml          # Project configuration
├── README.md               # Detailed documentation
├── .env.example           # Environment variables template
├── n8n_mcp_server/        # Main package
│   ├── __init__.py        # Package initialization
│   ├── main.py            # Server entry point
│   ├── config.py          # Configuration management
│   ├── cli.py             # CLI utilities
│   ├── tools/             # MCP tools
│   │   ├── base64_tool.py # Base64 encoder/decoder
│   │   └── example_tool.py # Tool template
│   ├── handlers/          # Request handlers
│   └── utils/             # Utility modules
├── tests/                 # Test suite
├── scripts/               # Development scripts
└── crypter_original.py    # Original implementation (preserved)
```

## Available Tools

### Base64 Tool
- `encrypt(data: str) -> str`: Encode data to Base64
- `decrypt(encoded: str) -> str | None`: Decode Base64 to string
- `validate_base64_string(data: str) -> bool`: Validate Base64 format

## Legacy Setup (Deprecated)

The old setup method is preserved for reference but **not recommended**:

```bash
# OLD METHOD - Do not use
python -m venv .venv
source ./.venv/Scripts/activate
pip install fastmcp fastapi uvicorn modelcontextprotocol
```

**Use UV instead** for better dependency management and development experience.

## Adding New Tools

1. **Create tool file** in `n8n_mcp_server/tools/`:
   ```python
   # my_tool.py
   def register_my_tool(mcp):
       @mcp.tool()
       def my_function(param: str) -> str:
           return f"Processed: {param}"
   ```

2. **Register in** `n8n_mcp_server/tools/__init__.py`:
   ```python
   from .my_tool import register_my_tool
   
   def register_all_tools(mcp):
       register_base64_tool(mcp)
       register_my_tool(mcp)  # Add this line
   ```

3. **Add tests** in `tests/test_tools/test_my_tool.py`

## Configuration

Create `.env` file from `.env.example`:
```env
MCP_SERVER_HOST=127.0.0.1
MCP_SERVER_PORT=8000
LOG_LEVEL=INFO
DEBUG=false
```

## Documentation

- **README.md**: Comprehensive project documentation
- **pyproject.toml**: Project configuration and dependencies
- **This file**: Setup and migration guide

## Migration from Old Setup

If you were using the old setup:

1. **Backup your work**: Copy any custom tools you created
2. **Follow the UV setup** instructions above
3. **Migrate custom tools** to the new structure
4. **Update imports** to use the new package structure
5. **Run tests** to ensure everything works

The new structure provides better organization, testing, and development experience.