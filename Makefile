# DeepBrief Development Makefile

.PHONY: help install setup test lint format type-check clean run dev

# Default target
help:
	@echo "DeepBrief Development Commands"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  setup      - Set up development environment"
	@echo "  install    - Install dependencies"
	@echo ""
	@echo "Development:"
	@echo "  dev        - Run in development mode"
	@echo "  run        - Run the CLI"
	@echo "  web        - Launch web interface"
	@echo ""
	@echo "Code Quality:"
	@echo "  format     - Format code with ruff"
	@echo "  lint       - Lint code with ruff"
	@echo "  type-check - Type check with basedpyright"
	@echo "  check      - Run all code quality checks"
	@echo ""
	@echo "Testing:"
	@echo "  test       - Run all tests"
	@echo "  test-fast  - Run tests excluding slow ones"
	@echo "  test-cov   - Run tests with coverage"
	@echo ""
	@echo "Utilities:"
	@echo "  clean      - Clean temporary files"
	@echo "  videos     - Generate test videos"
	@echo "  config     - Show configuration"

# Setup & Installation
setup:
	@echo "🚀 Setting up development environment..."
	python scripts/setup_dev.py

install:
	@echo "📦 Installing dependencies..."
	uv pip install -e ".[dev]"

# Development
dev:
	@echo "🔧 Running in development mode..."
	uv run deep-brief --help

run:
	@echo "🎬 Running DeepBrief CLI..."
	uv run deep-brief

web:
	@echo "🌐 Launching web interface..."
	uv run python -m deep_brief.interface.gradio_app

# Code Quality
format:
	@echo "🎨 Formatting code..."
	ruff format .

lint:
	@echo "🔍 Linting code..."
	ruff check .

type-check:
	@echo "📋 Type checking..."
	basedpyright

check: format lint type-check
	@echo "✅ All code quality checks completed"

# Testing
test:
	@echo "🧪 Running all tests..."
	uv run pytest -v

test-fast:
	@echo "⚡ Running fast tests only..."
	uv run pytest -v -m "not slow"

test-cov:
	@echo "📊 Running tests with coverage..."
	uv run pytest -v --cov-report=html --cov-report=term-missing

# Utilities
clean:
	@echo "🧹 Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf dist
	rm -rf build

videos:
	@echo "🎥 Generating test videos..."
	python3 scripts/generate_test_videos.py

config:
	@echo "⚙️ Showing configuration..."
	uv run deep-brief config --all

# Quick development workflow
dev-check: format lint type-check test-fast
	@echo "🚀 Development checks completed"

# Full CI workflow
ci: check test
	@echo "🎯 CI workflow completed"