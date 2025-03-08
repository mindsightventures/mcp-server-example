#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}UV not found. Installing UV...${NC}"
    pip install uv
    echo -e "${GREEN}UV installed successfully!${NC}"
else
    echo -e "${GREEN}UV is already installed.${NC}"
fi

# Check if mcp is installed
if ! python -c "import mcp" &> /dev/null; then
    echo -e "${YELLOW}MCP not found. Installing MCP...${NC}"
    uv pip install "mcp[cli]"
    echo -e "${GREEN}MCP installed successfully!${NC}"
else
    echo -e "${GREEN}MCP is already installed.${NC}"
fi

# Install project dependencies
echo -e "${YELLOW}Installing project dependencies...${NC}"
uv pip install -e ".[dev]" || {
    echo -e "${RED}Failed to install dependencies with UV. Trying with pip...${NC}"
    pip install -e ".[dev]"
}
echo -e "${GREEN}Dependencies installed successfully!${NC}"

echo -e "${YELLOW}Environment setup complete. You can now run tests with:${NC}"
echo -e "  ${GREEN}./scripts/run_tests.sh${NC} - Run all tests"
echo -e "  ${GREEN}./scripts/test_madrid.sh${NC} - Test the Madrid coordinates issue specifically"
echo -e "  ${GREEN}pytest -v${NC} - Run all tests with verbose output"
