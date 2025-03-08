#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running integration tests...${NC}"
echo -e "${YELLOW}These tests make actual API calls to OpenWeatherMap.${NC}"
echo -e "${YELLOW}They may take longer to run and could fail if the API is down or rate-limited.${NC}"
echo -e "${YELLOW}Press Ctrl+C to cancel or wait 3 seconds to continue...${NC}"
sleep 3

cd "$(dirname "$0")/.." && python -m pytest -v tests/test_integration.py -m integration

# Check if tests passed
if [ $? -eq 0 ]; then
    echo -e "${GREEN}All integration tests passed!${NC}"
else
    echo -e "${RED}Some integration tests failed.${NC}"
    exit 1
fi 