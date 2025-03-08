#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Installing dependencies with UV...${NC}"
uv add "mcp[cli]" httpx python-dotenv

echo -e "${YELLOW}Installing development dependencies...${NC}"
uv add --dev pytest pytest-asyncio pytest-mock pytest-cov

echo -e "${GREEN}Dependencies installed successfully!${NC}"
echo -e "${YELLOW}You can now run the weather app with:${NC}"
echo -e "  ${GREEN}./scripts/run_weather.sh${NC}"
