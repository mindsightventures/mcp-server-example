import asyncio
import os
import sys

import pytest

# Add the parent directory to sys.path to import the weather module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import src.weather.weather as weather


# This test directly tests the Madrid coordinates that were failing
@pytest.mark.asyncio
async def test_madrid_coordinates_direct():
    """Test the exact Madrid coordinates that were failing."""
    # These are the exact coordinates from the error
    madrid_lat = 40.4165
    madrid_lon = -3.7026

    # Print debug info
    print(f"\nTesting Madrid coordinates: {madrid_lat}, {madrid_lon}")
    print(f"API URL: {weather.OPENWEATHER_API_BASE}")
    print(
        f"API Key: {weather.OPENWEATHER_API_KEY[:5]}...{weather.OPENWEATHER_API_KEY[-3:]} (length: {len(weather.OPENWEATHER_API_KEY)})"
    )

    # First check if the API key is valid
    api_check_result = await weather.check_api_key_and_subscription()
    print(f"API Key check result: {api_check_result}")

    # Now try to get weather for Madrid coordinates
    result = await weather.get_weather_by_coordinates(madrid_lat, madrid_lon, "celsius")

    # Print the result for debugging
    print(f"Result: {result}")

    # Check if the result contains an error message
    assert "Unable to fetch current weather" not in result, "Failed to get weather for Madrid coordinates"

    # Verify we got some weather data
    assert "Temperature:" in result
    assert "Conditions:" in result


# This test checks if the fallback to API 2.5 works
@pytest.mark.asyncio
async def test_madrid_coordinates_fallback():
    """Test that the fallback to API 2.5 works for Madrid coordinates."""
    madrid_lat = 40.4165
    madrid_lon = -3.7026

    # Print debug info
    print(f"\nTesting Madrid coordinates with fallback: {madrid_lat}, {madrid_lon}")

    # Try the regular Weather API 2.5 directly
    fallback_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"lat": madrid_lat, "lon": madrid_lon}

    # Make the API request
    data = await weather.make_weather_request(fallback_url, params)

    # Print the result for debugging
    print(f"API 2.5 response: {data is not None}")
    if data:
        print(f"API 2.5 response keys: {list(data.keys())}")

    # Check if we got data
    assert data is not None, "Failed to get weather data from API 2.5"
    assert "main" in data, "Response doesn't contain weather data"
    assert "temp" in data["main"], "Response doesn't contain temperature data"
