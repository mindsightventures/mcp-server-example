#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if dependencies are installed
if ! pytest --version > /dev/null 2>&1; then
    echo -e "${YELLOW}Installing dependencies with UV...${NC}"
    uv pip install -e ".[dev]"
fi

echo -e "${YELLOW}Testing Madrid coordinates issue...${NC}"
cd "$(dirname "$0")/.." && pytest -v tests/test_madrid_coordinates.py

# Check if tests passed
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Madrid coordinates test passed!${NC}"
else
    echo -e "${RED}Madrid coordinates test failed.${NC}"
    exit 1
fi
