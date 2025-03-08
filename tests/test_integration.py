"""Integration tests for the weather app that make actual API calls."""

import os
import sys

import pytest

# Add the parent directory to sys.path to import the weather module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import src.weather.weather as weather

# Test cities with reliable weather data
TEST_CITIES = [
    ("London", "GB"),
    ("New York", "US"),
    ("Tokyo", "JP"),
    ("Sydney", "AU"),
    ("Paris", "FR"),
]

# Test coordinates for major cities
TEST_COORDINATES = [
    (51.5074, -0.1278),  # London
    (40.7128, -74.0060),  # New York
    (35.6762, 139.6503),  # Tokyo
    (-33.8688, 151.2093),  # Sydney
    (48.8566, 2.3522),  # Paris
]

# Flag to check if we have access to the One Call API 3.0
has_onecall_access = False


@pytest.mark.integration
@pytest.mark.asyncio
async def test_api_key_valid():
    """Test that the API key is valid and check if we have access to the One Call API 3.0."""
    global has_onecall_access

    result = await weather.check_api_key_and_subscription()
    print(f"\nAPI key check result: {result}")

    # Check if the API key is valid for the regular Weather API 2.5
    assert "API key is valid" in result, "API key is not valid"

    # Check if we have access to the One Call API 3.0
    has_onecall_access = "One Call API 3.0 subscription is active" in result
    print(f"Has access to One Call API 3.0: {has_onecall_access}")

    if not has_onecall_access:
        print("WARNING: No access to One Call API 3.0. Some tests will be skipped or may use fallback to API 2.5.")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_geocoding():
    """Test the geocoding functionality with real API calls."""
    for city, country in TEST_CITIES:
        print(f"\nTesting geocoding for {city}, {country}")

        # Get coordinates for the city
        coords = await weather.get_coordinates(city, country)

        # Verify that coordinates were found
        assert coords is not None, f"Failed to get coordinates for {city}, {country}"

        lat, lon = coords
        print(f"Found coordinates: {lat}, {lon}")

        # Basic validation of coordinates
        assert -90 <= lat <= 90, f"Invalid latitude: {lat}"
        assert -180 <= lon <= 180, f"Invalid longitude: {lon}"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_current_weather():
    """Test getting current weather with real API calls."""
    for city, country in TEST_CITIES:
        print(f"\nTesting current weather for {city}, {country}")

        # Get current weather for the city
        result = await weather.get_current_weather(city, country)

        # Print the result for debugging
        print(f"Result: {result}")

        # If we don't have access to One Call API 3.0, we expect it to fall back to API 2.5
        if not has_onecall_access and "Unable to fetch current weather" in result:
            print("Skipping assertion due to lack of One Call API 3.0 access")
            continue

        # Verify that weather data was found
        assert "Unable to" not in result, f"Failed to get weather for {city}, {country}"
        assert "Temperature:" in result, "Response doesn't contain temperature data"
        assert "Conditions:" in result, "Response doesn't contain weather conditions"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_forecast():
    """Test getting weather forecast with real API calls."""
    for city, country in TEST_CITIES:
        print(f"\nTesting forecast for {city}, {country}")

        # Get forecast for the city (3 days)
        result = await weather.get_forecast(city, country, days=3)

        # Print the result for debugging
        print(f"Result: {result}")

        # If we don't have access to One Call API 3.0, we expect it to fail
        if not has_onecall_access and "Unable to fetch forecast data" in result:
            print("Skipping assertion due to lack of One Call API 3.0 access")
            continue

        # Verify that forecast data was found
        assert "Unable to" not in result, f"Failed to get forecast for {city}, {country}"
        assert "Temperature:" in result, "Response doesn't contain temperature data"
        assert "Chance of Rain:" in result, "Response doesn't contain precipitation data"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_hourly_forecast():
    """Test getting hourly forecast with real API calls."""
    for city, country in TEST_CITIES[:2]:  # Test only a couple of cities to avoid too many API calls
        print(f"\nTesting hourly forecast for {city}, {country}")

        # Get hourly forecast for the city (6 hours)
        result = await weather.get_hourly_forecast(city, country, hours=6)

        # Print the result for debugging
        print(f"Result: {result}")

        # If we don't have access to One Call API 3.0, we expect it to fail
        if not has_onecall_access and "Unable to fetch hourly forecast" in result:
            print("Skipping assertion due to lack of One Call API 3.0 access")
            continue

        # Verify that hourly forecast data was found
        assert "Unable to" not in result, f"Failed to get hourly forecast for {city}, {country}"
        assert "Hourly Weather Forecast" in result, "Response doesn't contain hourly forecast"
        assert "Chance of Rain:" in result, "Response doesn't contain precipitation data"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_weather_by_coordinates():
    """Test getting weather by coordinates with real API calls."""
    for lat, lon in TEST_COORDINATES[:2]:  # Test only a couple of coordinates to avoid too many API calls
        print(f"\nTesting weather by coordinates: {lat}, {lon}")

        # Get weather for the coordinates
        result = await weather.get_weather_by_coordinates(lat, lon)

        # Print the result for debugging
        print(f"Result: {result}")

        # Verify that weather data was found
        assert "Unable to" not in result, f"Failed to get weather for coordinates ({lat}, {lon})"
        assert "Temperature:" in result, "Response doesn't contain temperature data"
        assert "Conditions:" in result, "Response doesn't contain weather conditions"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_fallback_to_api_2_5():
    """Test the fallback to API 2.5 if One Call API 3.0 fails."""
    # This is a bit tricky to test without mocking, but we can try to force a failure
    # by using invalid parameters for the One Call API 3.0

    # Use valid coordinates but try to force a failure in the One Call API 3.0
    # by manipulating the URL (this is a bit hacky but should work for testing)
    original_base_url = weather.OPENWEATHER_API_BASE

    try:
        # Temporarily change the API base URL to an invalid one
        weather.OPENWEATHER_API_BASE = "https://api.openweathermap.org/data/3.0/invalid_endpoint"

        # Try to get weather for London coordinates
        lat, lon = 51.5074, -0.1278  # London

        print(f"\nTesting fallback to API 2.5 for coordinates: {lat}, {lon}")

        # Get weather for the coordinates
        result = await weather.get_weather_by_coordinates(lat, lon)

        # Print the result for debugging
        print(f"Result: {result}")

        # Verify that weather data was found (from the fallback API)
        assert "Unable to" not in result, f"Failed to get weather for coordinates ({lat}, {lon})"
        assert "Temperature:" in result, "Response doesn't contain temperature data"
        assert "Conditions:" in result, "Response doesn't contain weather conditions"

    finally:
        # Restore the original API base URL
        weather.OPENWEATHER_API_BASE = original_base_url
