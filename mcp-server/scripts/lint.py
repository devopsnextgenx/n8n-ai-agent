"""Linting and code quality script."""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description, continue_on_error=True):
    """Run a command and display results."""
    print(f"🔄 {description}...")
    print(f"   Command: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ {description} completed successfully")
        if result.stdout.strip():
            print(f"   Output: {result.stdout.strip()}")
    else:
        print(f"❌ {description} failed")
        if result.stderr.strip():
            print(f"   Error: {result.stderr.strip()}")
        if result.stdout.strip():
            print(f"   Output: {result.stdout.strip()}")
        
        if not continue_on_error:
            sys.exit(1)
    
    print()
    return result.returncode == 0


def main():
    """Run linting and code quality checks."""
    print("🔍 N8N MCP Server Code Quality Suite")
    print("=" * 50)
    
    # Change to project directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Check if tools are available
    tools_to_check = ["black", "isort", "flake8", "mypy", "ruff"]
    missing_tools = []
    
    for tool in tools_to_check:
        try:
            subprocess.run(["python", "-m", tool, "--version"], 
                         capture_output=True, check=True)
        except subprocess.CalledProcessError:
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"❌ Missing tools: {', '.join(missing_tools)}")
        print("Please install development dependencies:")
        print("   uv sync --all-extras")
        sys.exit(1)
    
    # Determine if we're formatting or just checking
    format_mode = "--fix" in sys.argv or "--format" in sys.argv
    
    if format_mode:
        print("🔧 Running in FORMAT mode - will fix issues")
    else:
        print("🔍 Running in CHECK mode - will only report issues")
    
    print()
    
    all_passed = True
    
    # Black (code formatting)
    if format_mode:
        success = run_command(
            ["python", "-m", "black", "n8n_mcp_server/", "tests/", "scripts/"],
            "Formatting code with Black"
        )
    else:
        success = run_command(
            ["python", "-m", "black", "--check", "n8n_mcp_server/", "tests/", "scripts/"],
            "Checking code formatting with Black"
        )
    all_passed = all_passed and success
    
    # isort (import sorting)
    if format_mode:
        success = run_command(
            ["python", "-m", "isort", "n8n_mcp_server/", "tests/", "scripts/"],
            "Sorting imports with isort"
        )
    else:
        success = run_command(
            ["python", "-m", "isort", "--check-only", "n8n_mcp_server/", "tests/", "scripts/"],
            "Checking import sorting with isort"
        )
    all_passed = all_passed and success
    
    # Ruff (fast linting)
    if format_mode:
        success = run_command(
            ["python", "-m", "ruff", "check", "--fix", "n8n_mcp_server/", "tests/", "scripts/"],
            "Fixing issues with Ruff"
        )
    else:
        success = run_command(
            ["python", "-m", "ruff", "check", "n8n_mcp_server/", "tests/", "scripts/"],
            "Linting with Ruff"
        )
    all_passed = all_passed and success
    
    # Flake8 (additional linting)
    success = run_command(
        ["python", "-m", "flake8", "n8n_mcp_server/", "tests/", "scripts/"],
        "Linting with Flake8"
    )
    all_passed = all_passed and success
    
    # MyPy (type checking)
    success = run_command(
        ["python", "-m", "mypy", "n8n_mcp_server/"],
        "Type checking with MyPy"
    )
    all_passed = all_passed and success
    
    # Summary
    print("📊 Code Quality Summary")
    print("=" * 50)
    if all_passed:
        print("✅ All code quality checks passed!")
        if format_mode:
            print("🔧 Code has been formatted and fixed")
        sys.exit(0)
    else:
        print("❌ Some code quality checks failed!")
        if not format_mode:
            print("💡 Tip: Run with --fix to automatically fix some issues")
        sys.exit(1)


if __name__ == "__main__":
    main()