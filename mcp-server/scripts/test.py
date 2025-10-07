"""Testing script with various test configurations."""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description):
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
    
    print()
    return result.returncode == 0


def main():
    """Run comprehensive test suite."""
    print("🧪 N8N MCP Server Test Suite")
    print("=" * 50)
    
    # Change to project directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Test configurations
    test_configs = [
        {
            "name": "Quick Tests",
            "cmd": ["python", "-m", "pytest", "tests/", "-v", "--tb=short"],
            "description": "Running quick test suite"
        },
        {
            "name": "Coverage Tests",
            "cmd": ["python", "-m", "pytest", "tests/", "--cov=n8n_mcp_server", "--cov-report=term-missing"],
            "description": "Running tests with coverage"
        },
        {
            "name": "Unit Tests Only",
            "cmd": ["python", "-m", "pytest", "tests/", "-m", "unit", "-v"],
            "description": "Running unit tests only"
        },
        {
            "name": "Integration Tests Only",
            "cmd": ["python", "-m", "pytest", "tests/", "-m", "integration", "-v"],
            "description": "Running integration tests only"
        }
    ]
    
    # Check if pytest is available
    try:
        subprocess.run(["python", "-m", "pytest", "--version"], capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print("❌ pytest not found. Please install development dependencies:")
        print("   uv sync --all-extras")
        sys.exit(1)
    
    # Allow user to choose test type
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        
        if test_type == "quick":
            selected_tests = [test_configs[0]]
        elif test_type == "coverage":
            selected_tests = [test_configs[1]]
        elif test_type == "unit":
            selected_tests = [test_configs[2]]
        elif test_type == "integration":
            selected_tests = [test_configs[3]]
        elif test_type == "all":
            selected_tests = test_configs
        else:
            print(f"❌ Unknown test type: {test_type}")
            print("Available types: quick, coverage, unit, integration, all")
            sys.exit(1)
    else:
        # Default to quick tests
        selected_tests = [test_configs[0]]
    
    # Run selected tests
    all_passed = True
    for config in selected_tests:
        success = run_command(config["cmd"], config["description"])
        all_passed = all_passed and success
    
    # Summary
    print("📊 Test Summary")
    print("=" * 50)
    if all_passed:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()