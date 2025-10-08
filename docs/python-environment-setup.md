# Python Environment Setup

This document explains how to set up and use the Python virtual environment for the n8n-ai-agent project.

## Prerequisites

- Python 3.10 or higher
- pip (Python package installer)
- VS Code (recommended)

## Quick Setup

### Windows

1. Open a terminal in the project root directory
2. Run the setup script:
   ```cmd
   setup-python-env.bat
   ```

### Linux/macOS

1. Open a terminal in the project root directory
2. Make the script executable and run it:
   ```bash
   chmod +x setup-python-env.sh
   ./setup-python-env.sh
   ```

## Manual Setup

If you prefer to set up the environment manually:

### 1. Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install main dependencies
pip install -r requirements.txt

# Install MCP server dependencies (development mode)
cd mcp-server
pip install -e .[dev]
cd ..
```

### 3. Create Environment File

Create a `.env` file in the project root with the following content:

```env
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
```

## VS Code Integration

The project is pre-configured to work seamlessly with VS Code:

### Automatic Environment Detection

- VS Code will automatically detect the `.venv` environment
- The Python interpreter will be set to `.venv/Scripts/python.exe` (Windows) or `.venv/bin/python` (Linux/macOS)
- Terminal integration will automatically activate the virtual environment

### Recommended Extensions

The following extensions will be recommended when you open the project:

- **Python** - Core Python support
- **Black Formatter** - Code formatting
- **isort** - Import sorting
- **Flake8** - Linting
- **Mypy Type Checker** - Type checking
- **Pylint** - Additional linting
- **Ruff** - Fast Python linter
- **Code Spell Checker** - Spell checking

### Available Tasks

Access these tasks via `Ctrl+Shift+P` → "Tasks: Run Task":

- **Setup Python Environment** - Run the automated setup script
- **Install Python Dependencies** - Install/update dependencies
- **Run MCP Server** - Start the MCP server
- **Run Tests** - Execute all tests
- **Format Code (Black)** - Format code with Black
- **Lint Code (Ruff)** - Lint code with Ruff

### Debug Configurations

The following debug configurations are available:

- **Python: Current File** - Debug the currently open Python file
- **Python: MCP Server** - Debug the MCP server
- **Python: Run Tests** - Debug tests
- **Python: FastAPI Server** - Debug the FastAPI server

## Project Structure

```
n8n-ai-agent/
├── .venv/                  # Virtual environment (created by setup)
├── .vscode/                # VS Code configuration
│   ├── settings.json       # Workspace settings
│   ├── extensions.json     # Recommended extensions
│   ├── launch.json         # Debug configurations
│   └── tasks.json          # Build/run tasks
├── mcp-server/             # MCP server Python package
│   ├── n8n_mcp_server/     # Main package
│   ├── tests/              # Package tests
│   └── pyproject.toml      # Package configuration
├── requirements.txt        # Main dependencies
├── .env                    # Environment variables (created by setup)
├── setup-python-env.sh     # Linux/macOS setup script
└── setup-python-env.bat    # Windows setup script
```

## Usage

### Activating the Environment

#### In Terminal

```bash
# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate
```

#### In VS Code

The environment is automatically activated when you:
- Open a terminal in VS Code
- Run Python files
- Use debug configurations
- Execute tasks

### Running the MCP Server

```bash
# Method 1: Using the task (recommended)
# Ctrl+Shift+P → "Tasks: Run Task" → "Run MCP Server"

# Method 2: Command line
cd mcp-server
python -m n8n_mcp_server.main

# Method 3: Using uvicorn directly
uvicorn n8n_mcp_server.main:app --reload --host 0.0.0.0 --port 3000
```

### Running Tests

```bash
# Method 1: Using the task (recommended)
# Ctrl+Shift+P → "Tasks: Run Task" → "Run Tests"

# Method 2: Command line
pytest tests/ mcp-server/tests/ -v

# Method 3: Specific test files
pytest mcp-server/tests/test_handlers/ -v
```

### Code Formatting and Linting

```bash
# Format code with Black
python -m black mcp-server/ --line-length 88

# Sort imports with isort
python -m isort mcp-server/

# Lint with Ruff
python -m ruff check mcp-server/

# Type checking with mypy
python -m mypy mcp-server/
```

## Troubleshooting

### Python Not Found

Ensure Python 3.10+ is installed and in your PATH:

```bash
python --version
```

### Virtual Environment Issues

If the virtual environment is corrupted, remove and recreate it:

```bash
# Remove existing environment
rm -rf .venv  # Linux/macOS
rmdir /s .venv  # Windows

# Run setup script again
./setup-python-env.sh  # Linux/macOS
setup-python-env.bat   # Windows
```

### VS Code Not Detecting Environment

1. Open Command Palette (`Ctrl+Shift+P`)
2. Run "Python: Select Interpreter"
3. Choose the interpreter from `.venv/Scripts/python.exe` or `.venv/bin/python`

### Import Errors

Ensure the PYTHONPATH is set correctly:

```bash
export PYTHONPATH="${PYTHONPATH}:./mcp-server"  # Linux/macOS
set PYTHONPATH=%PYTHONPATH%;.\mcp-server        # Windows
```

Or check that your `.env` file contains:

```env
PYTHONPATH=./mcp-server
```

## Development Workflow

1. **Setup**: Run the setup script once
2. **Code**: Write your Python code in the `mcp-server/` directory
3. **Format**: Use Black formatter (automatic on save in VS Code)
4. **Lint**: Check with Ruff linter
5. **Test**: Run tests frequently
6. **Debug**: Use VS Code debug configurations
7. **Commit**: Ensure code is formatted and tests pass

## Additional Resources

- [Python Virtual Environments Guide](https://docs.python.org/3/tutorial/venv.html)
- [VS Code Python Extension Documentation](https://code.visualstudio.com/docs/python/python-tutorial)
- [Black Code Formatter](https://black.readthedocs.io/)
- [Ruff Linter](https://docs.astral.sh/ruff/)
- [pytest Testing Framework](https://docs.pytest.org/)