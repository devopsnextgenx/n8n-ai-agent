# N8N MCP Server

A Model Context Protocol (MCP) server for n8n AI agent with multiple tools and utilities.

## Features

- **Base64 Crypter**: Encode/decode Base64 strings
- **Modular Architecture**: Well-organized codebase with separate modules
- **UV Project**: Modern Python project management with UV
- **Type Safety**: Full type hints and mypy checking
- **Testing**: Comprehensive test suite with pytest
- **Development Tools**: Pre-commit hooks, linting, and formatting

## Project Structure

```
mcp-server/
├── pyproject.toml          # Project configuration and dependencies
├── README.md               # This file
├── .gitignore             # Git ignore patterns
├── .env.example           # Environment variables example
├── uv.lock                # UV lock file (auto-generated)
├── n8n_mcp_server/        # Main package
│   ├── __init__.py        # Package initialization
│   ├── main.py            # Server entry point
│   ├── cli.py             # CLI utilities
│   ├── config.py          # Configuration management
│   ├── tools/             # MCP tools
│   │   ├── __init__.py    # Tools package init
│   │   ├── base64_tool.py # Base64 encoder/decoder
│   │   └── example_tool.py # Example tool template
│   ├── handlers/          # Request handlers
│   │   ├── __init__.py    # Handlers package init
│   │   └── base_handler.py # Base handler class
│   └── utils/             # Utility modules
│       ├── __init__.py    # Utils package init
│       ├── logging.py     # Logging configuration
│       └── helpers.py     # Helper functions
├── tests/                 # Test suite
│   ├── __init__.py        # Test package init
│   ├── conftest.py        # Pytest configuration
│   ├── test_tools/        # Tool tests
│   │   ├── __init__.py
│   │   └── test_base64_tool.py
│   └── test_handlers/     # Handler tests
│       ├── __init__.py
│       └── test_base_handler.py
└── scripts/               # Development scripts
    ├── dev.py             # Development server
    ├── lint.py            # Linting script
    └── test.py            # Testing script
```

## Quick Start with UV

### Prerequisites

Install UV (Python package manager):
```bash
# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Setup

1. **Initialize the project**:
   ```bash
   cd mcp-server
   uv sync
   ```

2. **Activate the virtual environment**:
   ```bash
   # On Windows
   .venv\Scripts\activate

   # On macOS/Linux
   source .venv/bin/activate
   ```

3. **Install development dependencies**:
   ```bash
   uv sync --all-extras
   ```

4. **Copy environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

### Development

**Run the MCP server**:
```bash
uv run mcp-server
# or
uv run python -m n8n_mcp_server.main
```

**Development mode with auto-reload**:
```bash
uv run mcp-dev
```

**Run tests**:
```bash
uv run pytest
# or with coverage
uv run pytest --cov=n8n_mcp_server
```

**Linting and formatting**:
```bash
# Format code
uv run black .
uv run isort .

# Lint code
uv run flake8 .
uv run mypy n8n_mcp_server/

# Run all checks
uv run ruff check .
```

**Install new dependencies**:
```bash
# Runtime dependency
uv add package-name

# Development dependency
uv add --dev package-name
```

### Usage

The MCP server provides the following tools:

#### Base64 Tool
- `encrypt(data: str) -> str`: Encode data to Base64
- `decrypt(encoded: str) -> str | None`: Decode Base64 to string

Example usage:
```python
# Encoding
result = encrypt("Hello, World!")
print(result)  # SGVsbG8sIFdvcmxkIQ==

# Decoding
original = decrypt("SGVsbG8sIFdvcmxkIQ==")
print(original)  # Hello, World!
```

## Adding New Tools

1. **Create a new tool file** in `n8n_mcp_server/tools/`:
   ```python
   # n8n_mcp_server/tools/my_tool.py
   from fastmcp import FastMCP
   
   def register_my_tool(mcp: FastMCP):
       @mcp.tool()
       def my_function(param: str) -> str:
           """Tool description"""
           return f"Processed: {param}"
   ```

2. **Register the tool** in `n8n_mcp_server/main.py`:
   ```python
   from .tools.my_tool import register_my_tool
   
   # In main():
   register_my_tool(mcp)
   ```

3. **Add tests** in `tests/test_tools/test_my_tool.py`

## Configuration

Create a `.env` file with your configuration:
```env
MCP_SERVER_HOST=127.0.0.1
MCP_SERVER_PORT=8000
LOG_LEVEL=INFO
DEBUG=false
```

## Contributing

1. **Set up pre-commit hooks**:
   ```bash
   uv run pre-commit install
   ```

2. **Run tests before committing**:
   ```bash
   uv run pytest
   ```

3. **Follow the coding standards**:
   - Use type hints
   - Write docstrings
   - Add tests for new features
   - Follow PEP 8 (enforced by black/isort)

## License

MIT License - see LICENSE file for details.