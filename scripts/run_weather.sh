#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if dependencies are installed
if ! python -c "import mcp" &> /dev/null; then
    echo -e "${YELLOW}MCP not found. Installing dependencies...${NC}"
    ./scripts/setup_env.sh
fi

echo -e "${YELLOW}Starting weather app server...${NC}"
echo -e "${GREEN}Available tools:${NC}"
echo -e "  - get_current_weather: Get current weather conditions"
echo -e "  - get_forecast: Get daily weather forecast"
echo -e "  - get_hourly_forecast: Get hourly weather forecast"
echo -e "  - get_alerts: Get weather alerts"
echo -e "  - get_weather_by_coordinates: Get weather by coordinates"
echo -e "  - get_user_location: Get your current location"
echo -e "  - test_api_connection: Test the API connection"
echo -e "  - check_api_key_and_subscription: Check your API key and subscription"
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"

# Run the weather app
uv run -m weather.weather 