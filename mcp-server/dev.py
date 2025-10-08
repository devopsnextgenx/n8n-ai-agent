#!/usr/bin/env python3
"""
Development and testing script for MCP Crypto Server.
"""

import sys
import subprocess
import os
from pathlib import Path

def install_dependencies():
    """Install project dependencies using uv."""
    print("Installing dependencies with uv...")
    try:
        subprocess.run(["uv", "sync"], check=True, cwd=Path(__file__).parent)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False
    except FileNotFoundError:
        print("❌ uv not found. Please install uv first: pip install uv")
        return False
    return True

def run_server():
    """Run the MCP server."""
    print("Starting MCP Crypto Server...")
    try:
        # Try FastAPI server first (more reliable)
        subprocess.run([
            "uv", "run", "python", "src/fastapi_server.py"
        ], check=True, cwd=Path(__file__).parent)
    except subprocess.CalledProcessError:
        print("❌ FastAPI server failed, trying main server...")
        try:
            subprocess.run([
                "uv", "run", "python", "-m", "src.main"
            ], check=True, cwd=Path(__file__).parent)
        except subprocess.CalledProcessError:
            print("❌ Failed to start any server")
    except KeyboardInterrupt:
        print("\n⏹️ Server stopped by user")

def run_tests():
    """Run tests (placeholder for future implementation)."""
    print("Running tests...")
    # For now, just check if the modules can be imported
    try:
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        import config
        import utils
        import server
        print("✅ All modules import successfully")
        
        # Test basic functionality
        from utils import encode_to_base64, decode_from_base64
        test_text = "Hello, World!"
        encoded = encode_to_base64(test_text)
        decoded = decode_from_base64(encoded)
        assert decoded == test_text
        print("✅ Base64 encoding/decoding test passed")
        
    except Exception as e:
        print(f"❌ Tests failed: {e}")

def format_code():
    """Format code using black and isort."""
    print("Formatting code...")
    try:
        subprocess.run(["uv", "run", "black", "src/"], check=True)
        subprocess.run(["uv", "run", "isort", "src/"], check=True)
        print("✅ Code formatted successfully")
    except subprocess.CalledProcessError:
        print("❌ Code formatting failed")
    except FileNotFoundError:
        print("❌ Formatting tools not found")

def lint_code():
    """Lint code using flake8."""
    print("Linting code...")
    try:
        subprocess.run(["uv", "run", "flake8", "src/"], check=True)
        print("✅ Code linting passed")
    except subprocess.CalledProcessError:
        print("⚠️ Linting issues found")
    except FileNotFoundError:
        print("❌ flake8 not found")

def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python dev.py [command]")
        print("Commands:")
        print("  install    - Install dependencies")
        print("  run        - Run the server")
        print("  test       - Run tests")
        print("  format     - Format code")
        print("  lint       - Lint code")
        print("  setup      - Install deps and run tests")
        return
    
    command = sys.argv[1]
    
    if command == "install":
        install_dependencies()
    elif command == "run":
        run_server()
    elif command == "test":
        run_tests()
    elif command == "format":
        format_code()
    elif command == "lint":
        lint_code()
    elif command == "setup":
        if install_dependencies():
            run_tests()
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()