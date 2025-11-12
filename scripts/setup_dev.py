#!/usr/bin/env python3
"""
Development setup script for DeepBrief.

This script sets up the development environment, installs dependencies,
and verifies the installation.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"   Error: {e.stderr}")
        return False


def main() -> None:
    """Set up development environment."""
    print("🚀 Setting up DeepBrief development environment...\n")

    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print(
            "❌ Error: pyproject.toml not found. Please run this script from the project root."
        )
        sys.exit(1)

    # Check if uv is installed
    print("🔍 Checking for uv package manager...")
    try:
        subprocess.run(["uv", "--version"], check=True, capture_output=True)
        print("✅ uv found")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ uv not found. Please install uv first:")
        print("   curl -LsSf https://astral.sh/uv/install.sh | sh")
        sys.exit(1)

    # Create virtual environment
    if not Path(".venv").exists():
        if not run_command(["uv", "venv"], "Creating virtual environment"):
            sys.exit(1)
    else:
        print("✅ Virtual environment already exists")

    # Install dependencies
    if not run_command(
        ["uv", "pip", "install", "-e", ".[dev]"], "Installing dependencies"
    ):
        sys.exit(1)

    # Verify installation
    print("\n🔍 Verifying installation...")
    try:
        # Try importing the package
        result = subprocess.run(
            [
                "uv",
                "run",
                "python",
                "-c",
                "import deep_brief; print('✅ Package imports successfully')",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(result.stdout.strip())
        else:
            print(f"❌ Import failed: {result.stderr}")

        # Try CLI command
        result = subprocess.run(
            ["uv", "run", "deep-brief", "--help"], capture_output=True, text=True
        )
        if result.returncode == 0:
            print("✅ CLI command works")
        else:
            print(f"❌ CLI failed: {result.stderr}")

    except Exception as e:
        print(f"❌ Verification failed: {e}")

    # Run code quality checks
    print("\n🔍 Running code quality checks...")

    checks = [
        (["uv", "run", "ruff", "format", "--check", "."], "Code formatting check"),
        (["uv", "run", "ruff", "check", "."], "Linting check"),
        (["uv", "run", "basedpyright"], "Type checking"),
        (["uv", "run", "pytest", "--collect-only", "-q"], "Test collection"),
    ]

    for cmd, description in checks:
        if not run_command(cmd, description):
            print(f"⚠️  {description} failed - please fix before committing")

    print("\n🎉 Development environment setup complete!")
    print("\n📋 Next steps:")
    print("   1. Activate the environment: source .venv/bin/activate")
    print("   2. Run tests: pytest -v")
    print("   3. Try the CLI: deep-brief --help")
    print("   4. Check code quality: ruff format . && ruff check . && basedpyright")
    print("\n💡 Tip: Add your API keys to .env for full functionality")


if __name__ == "__main__":
    main()
