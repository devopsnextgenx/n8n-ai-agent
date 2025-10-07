# N8N MCP Server Makefile
.PHONY: help install dev test lint format clean run

# Default target
help:
	@echo "N8N MCP Server Development Commands"
	@echo "=================================="
	@echo "install     - Install dependencies with UV"
	@echo "dev         - Install development dependencies"
	@echo "run         - Run the MCP server"
	@echo "dev-run     - Run development server with auto-reload"
	@echo "test        - Run test suite"
	@echo "test-cov    - Run tests with coverage"
	@echo "lint        - Run linting and code quality checks"
	@echo "format      - Format code (black, isort, ruff --fix)"
	@echo "clean       - Clean build artifacts and cache"
	@echo "check       - Run all checks (lint + test)"

# Installation
install:
	uv sync

dev:
	uv sync --all-extras

# Running
run:
	uv run mcp-server

dev-run:
	uv run mcp-dev

# Testing
test:
	uv run python scripts/test.py

test-cov:
	uv run python scripts/test.py coverage

test-all:
	uv run python scripts/test.py all

# Code quality
lint:
	uv run python scripts/lint.py

format:
	uv run python scripts/lint.py --fix

# Utilities
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ .pytest_cache/

check: lint test

# Pre-commit
pre-commit-install:
	uv run pre-commit install

pre-commit-run:
	uv run pre-commit run --all-files

# Package building
build:
	uv build

# Help with UV commands
uv-help:
	@echo "Common UV Commands:"
	@echo "=================="
	@echo "uv add package-name      - Add runtime dependency"
	@echo "uv add --dev package     - Add development dependency"
	@echo "uv remove package-name   - Remove dependency"
	@echo "uv sync                  - Install dependencies"
	@echo "uv sync --all-extras     - Install with dev dependencies"
	@echo "uv run command           - Run command in virtual environment"
	@echo "uv pip list              - List installed packages"