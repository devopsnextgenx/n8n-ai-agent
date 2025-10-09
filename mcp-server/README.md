# MCP Crypto Server

A Model Context Protocol (MCP) server implementation using FastMCP with HTTP transport, providing cryptographic tools for base64 encoding/decoding.

## Features

- **Tools**: 
  - `encrypt`: Encrypt strings to base64
  - `decrypt`: Decrypt base64 strings
- **Resources**:
  - Server version information
  - Server status
  - Tools list
- **Configuration**: YAML-based configuration for server settings and logging
- **Logging**: Console and file logging with rotation

## Requirements

- Python 3.10 or higher
- uv package manager

## Installation

This project uses `uv` for dependency management. Install dependencies:

```bash
python -m venv .venv
source .venv/Scripts/activate
uv sync
python.exe -m pip install -e .
```

## Configuration

Copy `config.yml.example` to `config.yml` and adjust settings:

```yaml
server:
  host: "0.0.0.0"
  port: 6789

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "logs/mcp-server.log"
```

## Usage

Start the server (multiple options):

**Option 1: FastAPI server (recommended - most reliable)**
```bash
uv run python src/fastapi_server.py
```

**Option 2: Main server with FastMCP**
```bash
uv run python -m src.main
python -m src.main
```

**Option 3: Simple server (alternative)**
```bash
uv run python src/simple_server.py
python src/simple_server.py
```

**Option 4: Development mode (tries FastAPI first)**
```bash
uv run python dev.py run
python dev.py run
```

The server will be available at `http://localhost:6789` (configurable in `config.yml`)

### API Endpoints

Once running, you can access:

- **Root**: `GET /` - Server information
- **Health**: `GET /health` - Health check
- **Documentation**: `GET /docs` - Interactive API docs
- **Tools**:
  - `POST /tools/encrypt` - Encrypt text to base64
  - `POST /tools/decrypt` - Decrypt base64 text
- **Resources**:
  - `GET /resources/version` - Server version info
  - `GET /resources/status` - Server status and metrics
  - `GET /resources/tools` - Available tools list

## Project Structure

```
├── src/
│   ├── mcp_store/
│   │   ├── tools/
│   │   ├── resources/
│   │   └── prompts/
│   ├── main.py
│   ├── config.py
│   ├── server.py
│   └── utils.py
├── logs/
├── scripts/
├── config.yml
└── pyproject.toml
```

## Development

Run tests:

```bash
uv run pytest
```

Format code:

```bash
uv run black src/
uv run isort src/
```

Lint code:

```bash
uv run flake8 src/
```