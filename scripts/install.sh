#!/bin/bash
set -e

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Please install it first."
    echo "You can install it with: curl -sSf https://install.python-poetry.org | python3 -"
    exit 1
fi

# Create a virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv venv
fi

# Install dependencies
echo "Installing dependencies..."
uv pip install -e .

# Install development dependencies if --dev flag is provided
if [[ "$*" == *--dev* ]]; then
    echo "Installing development dependencies..."
    uv pip install -e ".[dev]"

    # Install pre-commit hooks
    echo "Setting up pre-commit hooks..."
    uv run pre-commit install
fi

echo "Installation complete!"
echo "You can activate the virtual environment with: source .venv/bin/activate"
